"""Etapa 13 — persistência do ciclo (doc 07 §5 linha 13 e §7.2). Valores sintéticos."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr.hydration import AtendimentoHidratado, hidratar
from casa77_sdr.identity import (
    CriterioIdentidade,
    DecisaoIdentidade,
    SituacaoTakeover,
    Vinculo,
)
from casa77_sdr.interpretation_stage import executar_interpretacao_do_ciclo
from casa77_sdr.motor_deps import BaseMotor, DependenciasMotor, carregar_base_motor
from casa77_sdr.normalization import EntradaMensagem, normalizar_entrada
from casa77_sdr.orchestrator_decision import PrimeiraDecisao, decidir_primeira_chamada
from casa77_sdr.orchestrator_emission import TextoFinal
from casa77_sdr.orchestrator_identity import AlvoDoCiclo
from casa77_sdr.orchestrator_persist import persistir_ciclo
from casa77_sdr.persistence import (
    FalhaDePersistencia,
    PersistenciaEmMemoria,
    RegistroAtendimento,
)
from casa77_sdr.state_machine import Estado

RAIZ = Path(__file__).resolve().parents[1]
MARCO_ANTIGO = datetime(2026, 1, 10, 9, 0, tzinfo=UTC)
RECEBIDA = MARCO_ANTIGO + timedelta(hours=3)
CANAL = "teste"
CONTATO = "contato-ficticio"


def _slot(valor: str | None) -> dict[str, Any]:
    if valor is None:
        return {"presente": False, "valor": "alta"}
    return {"presente": True, "valor": valor}


def _payload(*, pedido_de_humano: bool = False) -> str:
    extraidos: dict[str, Any] = {}
    for campo in ("tipo_evento", "data_nomeada", "convidados", "formato", "nome", "contato"):
        extraidos[campo] = None
        extraidos[f"confianca_{campo}"] = _slot(None)
    return json.dumps(
        {
            "dados_extraidos": extraidos,
            "correcoes": [],
            "perguntas_comerciais": [],
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


class AlertaEspiao:
    def __init__(self) -> None:
        self.chamadas: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> None:
        self.chamadas.append(kwargs)


class PersistenciaQueFalha(PersistenciaEmMemoria):
    def criar(self, registro: RegistroAtendimento) -> None:
        raise FalhaDePersistencia("falha sintetica")

    def gravar(self, registro: RegistroAtendimento) -> None:
        raise FalhaDePersistencia("falha sintetica")


@pytest.fixture(scope="module")
def base_motor() -> BaseMotor:
    return carregar_base_motor(RAIZ)


def _entrada() -> EntradaMensagem:
    return EntradaMensagem(
        canal=CANAL, contato=CONTATO, mensagem="mensagem ficticia", recebida_em=RECEBIDA
    )


def _deps(base_motor: BaseMotor, persistencia: PersistenciaEmMemoria, alerta: AlertaEspiao):
    return DependenciasMotor(
        base_motor=base_motor,
        persistencia=persistencia,
        produtor=ProdutorFixo(_payload()),
        prompt_sistema="prompt ficticio",
        janela_idempotencia=timedelta(minutes=5),
        limiar_recencia=timedelta(days=1),
        calendario_integrado=False,
        tentar_alerta=alerta,
        enviar_mensagem=lambda canal, contato, texto: None,
        entregar_resumo=lambda resumo: None,
    )


def _ciclo(
    base_motor: BaseMotor,
    *,
    atendimento: AtendimentoHidratado,
    pedido_de_humano: bool = False,
) -> tuple[AlvoDoCiclo, PrimeiraDecisao, TextoFinal]:
    artefatos = executar_interpretacao_do_ciclo(
        "mensagem ficticia",
        produtor=ProdutorFixo(_payload(pedido_de_humano=pedido_de_humano)),
        prompt_sistema="prompt ficticio",
    )
    identidade = DecisaoIdentidade(
        identidade=None,
        id_atendimento_alvo=atendimento.id_atendimento,
        criterio=CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO,
        candidatos_avaliados=(),
        classificacao_por_candidato=(),
        vinculo_declarado=Vinculo.SEM_DECLARACAO,
        situacao_takeover=SituacaoTakeover.SEM_TAKEOVER,
        escopo_restrito_por_identificador=False,
    )
    alvo = AlvoDoCiclo(artefatos, identidade, atendimento)
    pd = decidir_primeira_chamada(
        alvo, base_motor=base_motor, calendario_integrado=False, e01_confirmado=True
    )
    final = TextoFinal(texto=None, decisoes_do_ciclo=(pd.decisao,), resumo_handoff=None)
    return alvo, pd, final


def _persistir(deps, alvo, pd, final) -> bool:
    entrada = _entrada()
    ids = iter(["id-gerado-1"])
    return persistir_ciclo(
        deps=deps,
        alvo=alvo,
        primeira=pd,
        texto_final=final,
        entrada=entrada,
        entrada_normalizada=normalizar_entrada(entrada, deps.janela_idempotencia),
        gerar_id=lambda: next(ids),
    )


def test_atendimento_novo_e_criado_com_id_gerado_e_estado_final(base_motor):
    persistencia = PersistenciaEmMemoria()
    deps = _deps(base_motor, persistencia, AlertaEspiao())
    alvo, pd, final = _ciclo(base_motor, atendimento=hidratar(None))

    assert _persistir(deps, alvo, pd, final) is True

    rec = persistencia.recuperar_por_id("id-gerado-1", CANAL, CONTATO)
    assert rec.registro is not None
    assert rec.registro.estado_conversa == final.decisoes_do_ciclo[-1].estado_final.value
    chave = normalizar_entrada(_entrada(), deps.janela_idempotencia).chave_idempotencia
    assert persistencia.chave_processada(chave)


def test_marco_atualiza_com_mudanca_de_estado(base_motor):
    persistencia = PersistenciaEmMemoria()
    deps = _deps(base_motor, persistencia, AlertaEspiao())
    alvo, pd, final = _ciclo(base_motor, atendimento=hidratar(None))
    assert any(d.transicoes_que_mudaram_estado for d in final.decisoes_do_ciclo)

    _persistir(deps, alvo, pd, final)

    rec = persistencia.recuperar_por_id("id-gerado-1", CANAL, CONTATO).registro
    assert rec.instante_ultima_transicao == RECEBIDA


def test_marco_inalterado_sem_mudanca_de_estado_em_atendimento_existente(base_motor):
    persistencia = PersistenciaEmMemoria()
    existente = RegistroAtendimento(
        id_atendimento="at-1",
        canal=CANAL,
        contato=CONTATO,
        estado_conversa=Estado.ENCAMINHADO_HUMANO.value,
        instante_ultima_transicao=MARCO_ANTIGO,
    )
    persistencia.criar(existente)
    deps = _deps(base_motor, persistencia, AlertaEspiao())
    alvo, pd, final = _ciclo(base_motor, atendimento=hidratar(existente))
    assert not any(d.transicoes_que_mudaram_estado for d in final.decisoes_do_ciclo)

    assert _persistir(deps, alvo, pd, final) is True

    rec = persistencia.recuperar_por_id("at-1", CANAL, CONTATO).registro
    assert rec.instante_ultima_transicao == MARCO_ANTIGO


def test_falha_de_persistencia_preserva_alerta_e_nao_marca_chave(base_motor):
    persistencia = PersistenciaQueFalha()
    alerta = AlertaEspiao()
    deps = _deps(base_motor, persistencia, alerta)
    alvo, pd, final = _ciclo(base_motor, atendimento=hidratar(None))

    assert _persistir(deps, alvo, pd, final) is False

    chave = normalizar_entrada(_entrada(), deps.janela_idempotencia).chave_idempotencia
    assert not persistencia.chave_processada(chave)
    pendentes = persistencia.recuperar_pendentes()
    assert len(pendentes) == 1
    assert pendentes[0].conteudo == "mensagem ficticia"
    assert len(alerta.chamadas) == 1
    assert alerta.chamadas[0]["categoria"] == "FalhaDePersistencia"
    assert alerta.chamadas[0]["pendente_preservado"] is True
    assert alerta.chamadas[0]["correlacao"] == chave
