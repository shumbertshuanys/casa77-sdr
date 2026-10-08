"""Testes das etapas 6–7 do ciclo (`orchestrator_decision`).

Cobre a ordem conceitual determinística anterior à etapa 7 (`docs/07` §5):
atualização de dados → regras → qualificação provisória → S2-D8 → qualificação
final → eventos → primeira chamada da `MaquinaEstados`; a propagação da
Classe I **antes** da máquina; e o caminho `HUMANO_UNICO` (T33).

Base real (`carregar_base_motor`) e `ArtefatosInterpretacao` real produzido por
`executar_interpretacao_do_ciclo` com produtor fake. As asserções são por enum
de estado/ação e por identificador estrutural de fragmento — nunca por valor
comercial. Zero PII, zero conversa real.
"""

from __future__ import annotations

import dataclasses
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import orchestrator_decision
from casa77_sdr.coverage_map import MapaCoberturaInvalido
from casa77_sdr.hydration import AtendimentoHidratado, hidratar
from casa77_sdr.identity import (
    CriterioIdentidade,
    DecisaoIdentidade,
    SituacaoTakeover,
    Vinculo,
)
from casa77_sdr.interpretation_stage import executar_interpretacao_do_ciclo
from casa77_sdr.motor_deps import BaseMotor, carregar_base_motor
from casa77_sdr.orchestrator_decision import PrimeiraDecisao, decidir_primeira_chamada
from casa77_sdr.orchestrator_identity import AlvoDoCiclo
from casa77_sdr.persistence import RegistroAtendimento
from casa77_sdr.state_machine import (
    AcaoMaquina,
    CondicoesCiclo,
    Estado,
    Evento,
    Transicao,
)

RAIZ = Path(__file__).resolve().parents[1]
MARCO = datetime(2026, 1, 10, 9, 0, tzinfo=UTC)


# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------


def _slot(valor: str | None) -> dict[str, Any]:
    if valor is None:
        return {"presente": False, "valor": "alta"}
    return {"presente": True, "valor": valor}


def _payload(
    *,
    dados: dict[str, Any] | None = None,
    perguntas: tuple[str, ...] = (),
    pedido_de_humano: bool = False,
) -> str:
    extraidos: dict[str, Any] = {}
    for campo in ("tipo_evento", "data_nomeada", "convidados", "formato", "nome", "contato"):
        valor = (dados or {}).get(campo)
        extraidos[campo] = valor
        extraidos[f"confianca_{campo}"] = _slot(None if valor is None else "alta")
    return json.dumps(
        {
            "dados_extraidos": extraidos,
            "correcoes": [],
            "perguntas_comerciais": [
                {"texto": "pergunta ficticia", "confianca": _slot("alta"), "assunto": a}
                for a in perguntas
            ],
            "pedido_de_humano": pedido_de_humano,
            "confianca_pedido_de_humano": _slot("alta" if pedido_de_humano else None),
            "referencias_evento_anterior": [],
            "trechos_ambiguos": [],
            "confianca_global": _slot("alta"),
            "intencoes_autonomas": [],
        }
    )


class ProdutorFixo:
    def __init__(self, bruto: str) -> None:
        self.bruto = bruto

    def produzir(self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]) -> str:
        return self.bruto


def _decisao(situacao: SituacaoTakeover, alvo: str | None) -> DecisaoIdentidade:
    return DecisaoIdentidade(
        identidade=None,
        id_atendimento_alvo=alvo,
        criterio=(
            CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO
            if situacao is SituacaoTakeover.SEM_TAKEOVER
            else None
        ),
        candidatos_avaliados=(),
        classificacao_por_candidato=(),
        vinculo_declarado=Vinculo.SEM_DECLARACAO,
        situacao_takeover=situacao,
        escopo_restrito_por_identificador=False,
    )


def _alvo(
    bruto: str,
    *,
    atendimento: AtendimentoHidratado | None = None,
    situacao: SituacaoTakeover = SituacaoTakeover.SEM_TAKEOVER,
) -> AlvoDoCiclo:
    artefatos = executar_interpretacao_do_ciclo(
        "mensagem ficticia", produtor=ProdutorFixo(bruto), prompt_sistema="prompt ficticio"
    )
    if atendimento is None:
        atendimento = hidratar(None)
    return AlvoDoCiclo(artefatos, _decisao(situacao, atendimento.id_atendimento), atendimento)


@pytest.fixture(scope="module")
def base_motor() -> BaseMotor:
    return carregar_base_motor(RAIZ)


def _decidir(alvo: AlvoDoCiclo, base_motor: BaseMotor) -> PrimeiraDecisao:
    return decidir_primeira_chamada(
        alvo, base_motor=base_motor, calendario_integrado=False, e01_confirmado=True
    )


# --------------------------------------------------------------------------
# Primeira mensagem em atendimento novo
# --------------------------------------------------------------------------


def test_primeira_mensagem_sai_de_novo_e_apresenta_atendimento(base_motor):
    alvo = _alvo(_payload(dados={"tipo_evento": "aniversario"}))
    pd = _decidir(alvo, base_motor)
    assert pd.decisao.estado_final is not Estado.NOVO
    assert AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL in pd.decisao.acoes
    assert pd.atualizacao.insumo_qualificacao_atualizado is True
    assert pd.eventos[0] is Evento.E01
    assert isinstance(pd.condicoes, CondicoesCiclo)
    assert pd.condicoes.calendario_integrado is False


def test_primeira_decisao_expoe_insumos_passados_a_maquina(base_motor, monkeypatch):
    capturado: dict[str, Any] = {}
    original = orchestrator_decision.decidir

    def espiao(estado, eventos, qualificacao, condicoes):
        capturado.update(
            estado=estado, eventos=eventos, qualificacao=qualificacao, condicoes=condicoes
        )
        return original(estado, eventos, qualificacao, condicoes)

    monkeypatch.setattr(orchestrator_decision, "decidir", espiao)
    pd = _decidir(_alvo(_payload(dados={"tipo_evento": "aniversario"})), base_motor)
    assert capturado["estado"] is Estado.NOVO
    assert capturado["eventos"] == pd.eventos
    assert capturado["qualificacao"] is pd.qualificacao
    assert capturado["condicoes"] is pd.condicoes


# --------------------------------------------------------------------------
# Handoff
# --------------------------------------------------------------------------


def test_pedido_explicito_de_humano_produz_motivos_de_handoff(base_motor):
    pd = _decidir(_alvo(_payload(pedido_de_humano=True)), base_motor)
    assert pd.decisao.motivos_handoff
    assert Evento.E18 in pd.eventos


# --------------------------------------------------------------------------
# Classe I — bloqueia antes da etapa 7
# --------------------------------------------------------------------------


def test_classe_i_mapa_invalido_propaga_sem_chamar_a_maquina(base_motor, monkeypatch):
    chamadas = {"n": 0}

    def contador(*_a: Any, **_k: Any) -> None:
        chamadas["n"] += 1

    monkeypatch.setattr(orchestrator_decision, "decidir", contador)
    base_invalida = dataclasses.replace(base_motor, mapa={"invalido": True})
    alvo = _alvo(_payload(dados={"tipo_evento": "aniversario"}))
    with pytest.raises(MapaCoberturaInvalido):
        decidir_primeira_chamada(
            alvo, base_motor=base_invalida, calendario_integrado=False, e01_confirmado=True
        )
    assert chamadas["n"] == 0


# --------------------------------------------------------------------------
# HUMANO_UNICO — a cadeia roda e a máquina mantém o estado (T33)
# --------------------------------------------------------------------------


def test_humano_unico_mantem_atendimento_humano_via_t33(base_motor):
    registro = RegistroAtendimento(
        id_atendimento="at-h1",
        canal="teste",
        contato="contato-ficticio",
        estado_conversa=Estado.ATENDIMENTO_HUMANO.value,
        dados_coletados={"tipo_evento": "evento ficticio"},
        instante_ultima_transicao=MARCO,
    )
    alvo = _alvo(
        _payload(dados={"tipo_evento": "evento ficticio"}),
        atendimento=hidratar(registro),
        situacao=SituacaoTakeover.HUMANO_UNICO,
    )
    pd = _decidir(alvo, base_motor)
    assert pd.decisao.estado_final is Estado.ATENDIMENTO_HUMANO
    assert Transicao.T33 in pd.decisao.caminho
    assert pd.condicoes.identidade is None


# --------------------------------------------------------------------------
# fatos_runtime sem calendário — R05 cai no caminho sem consulta
# --------------------------------------------------------------------------


def test_pergunta_de_disponibilidade_sem_calendario_nao_bloqueia(base_motor):
    pd = _decidir(_alvo(_payload(perguntas=("disponibilidade_de_data",))), base_motor)
    assert pd.s2d8.fragmentos_autorizados == ("R05/F1",)


# --------------------------------------------------------------------------
# Aplicabilidade de pacote sobre os dados acumulados
# --------------------------------------------------------------------------


def test_aplicabilidade_usa_convidados_ja_registrados(base_motor):
    sentados = base_motor.base["capacidade"]["convidados_sentados"]
    registro = RegistroAtendimento(
        id_atendimento="at-1",
        canal="teste",
        contato="contato-ficticio",
        estado_conversa=Estado.COLETANDO_DADOS.value,
        dados_coletados={"convidados": sentados},
        instante_ultima_transicao=MARCO,
    )
    alvo = _alvo(
        _payload(perguntas=("preco_locacao",)), atendimento=hidratar(registro)
    )
    pd = _decidir(alvo, base_motor)
    assert pd.s2d8.fragmentos_autorizados == ("R09/F1",)
