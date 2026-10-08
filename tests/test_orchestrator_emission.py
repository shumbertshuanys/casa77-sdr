"""Testes das etapas 8–12 do ciclo (`orchestrator_emission`).

Cobre: projeção → fatos → composição → montagem → validação (texto candidato =
literal aprovado, sem LLM no M2); substituição por `R03` quando a validação
reprova; silêncio em `atendimento_humano`; reentrada de fechamento `E15` → `E12`
com no máximo três chamadas da `MaquinaEstados`; e o resumo de *handoff*.

Base real (`carregar_base_motor`) e `PrimeiraDecisao` real produzida pelo
caminho da Task 4 com produtor fake. As asserções são por enum de estado/ação e
por identificador estrutural de fragmento — o texto esperado é obtido pela
mesma cadeia aprovada, nunca escrito à mão. Zero valor comercial literal.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import orchestrator_emission
from casa77_sdr.emission_projection import projetar_fragmentos_para_emissao
from casa77_sdr.fact_selection import materializar_fatos_autorizados
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
from casa77_sdr.orchestrator_emission import TextoFinal, produzir_texto_final
from casa77_sdr.orchestrator_identity import AlvoDoCiclo
from casa77_sdr.persistence import RegistroAtendimento
from casa77_sdr.response_assembly import montar_resposta_final
from casa77_sdr.response_composition import compor_textos_emitiveis
from casa77_sdr.response_validation import (
    MotivoValidacaoResposta,
    ResultadoValidacaoResposta,
)
from casa77_sdr.state_machine import AcaoMaquina, Estado, Evento, Transicao

RAIZ = Path(__file__).resolve().parents[1]
MARCO = datetime(2026, 1, 10, 9, 0, tzinfo=UTC)
MENSAGEM = "mensagem ficticia normalizada"
CORRELACAO = "corr-ficticia"


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
    intencoes: tuple[str, ...] = (),
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
                {"texto": f"pergunta ficticia {a}", "confianca": _slot("alta"), "assunto": a}
                for a in perguntas
            ],
            "pedido_de_humano": pedido_de_humano,
            "confianca_pedido_de_humano": _slot("alta" if pedido_de_humano else None),
            "referencias_evento_anterior": [],
            "trechos_ambiguos": [],
            "confianca_global": _slot("alta"),
            "intencoes_autonomas": [
                {"codigo": codigo, "confianca": _slot("alta")} for codigo in intencoes
            ],
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


def _decisao_identidade(situacao: SituacaoTakeover, alvo: str | None) -> DecisaoIdentidade:
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


def _registro(estado: Estado, dados: dict[str, Any]) -> AtendimentoHidratado:
    return hidratar(
        RegistroAtendimento(
            id_atendimento="at-1",
            canal="teste",
            contato="contato-ficticio",
            estado_conversa=estado.value,
            dados_coletados=dados,
            instante_ultima_transicao=MARCO,
        )
    )


@pytest.fixture(scope="module")
def base_motor() -> BaseMotor:
    return carregar_base_motor(RAIZ)


def _dados_completos(base_motor: BaseMotor) -> dict[str, Any]:
    return {
        "tipo_evento": "evento ficticio",
        "data_nomeada": "data ficticia",
        "convidados": base_motor.base["capacidade"]["convidados_sentados"],
        "formato": "sentado",
        "nome": "Nome Ficticio",
        "contato": "contato-ficticio",
    }


def _primeira(
    bruto: str,
    base_motor: BaseMotor,
    *,
    atendimento: AtendimentoHidratado | None = None,
    situacao: SituacaoTakeover = SituacaoTakeover.SEM_TAKEOVER,
) -> tuple[PrimeiraDecisao, Estado]:
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorFixo(bruto), prompt_sistema="prompt ficticio"
    )
    if atendimento is None:
        atendimento = hidratar(None)
    alvo = AlvoDoCiclo(
        artefatos, _decisao_identidade(situacao, atendimento.id_atendimento), atendimento
    )
    pd = decidir_primeira_chamada(
        alvo, base_motor=base_motor, calendario_integrado=False, e01_confirmado=True
    )
    return pd, atendimento.estado


def _produzir(
    pd: PrimeiraDecisao,
    estado_inicial: Estado,
    base_motor: BaseMotor,
    alerta: AlertaEspiao | None = None,
) -> TextoFinal:
    return produzir_texto_final(
        pd,
        base_motor=base_motor,
        estado_inicial=estado_inicial,
        mensagem=MENSAGEM,
        tentar_alerta=alerta if alerta is not None else AlertaEspiao(),
        correlacao=CORRELACAO,
    )


def _texto_aprovado(base_motor: BaseMotor, tokens: tuple[str, ...]) -> str:
    selecao = materializar_fatos_autorizados(
        base_motor.indice, base_motor.base, base_motor.textos, tokens
    )
    return montar_resposta_final(compor_textos_emitiveis(selecao)).texto


def _contar_decidir(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    contador = {"n": 0}
    original = orchestrator_emission.decidir

    def espiao(*args: Any) -> Any:
        contador["n"] += 1
        return original(*args)

    monkeypatch.setattr(orchestrator_emission, "decidir", espiao)
    return contador


# --------------------------------------------------------------------------
# Etapas 8–11 — texto literal aprovado
# --------------------------------------------------------------------------


def test_pergunta_comercial_emite_composicao_aprovada_byte_a_byte(base_motor):
    pd, estado = _primeira(_payload(perguntas=("preco_locacao",)), base_motor)
    assert AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL in pd.decisao.acoes
    projetados = projetar_fragmentos_para_emissao(
        pd.s2d8.fragmentos_autorizados, pd.decisao.acoes
    )
    # `E15` → T20 na primeira mensagem (`NOVO`): não há coleta a retomar, então
    # só a pergunta do tipo de evento (primeiro campo da prioridade natural)
    # fecha a mensagem — sem `R32/F1` (achado final M2.1 #3).
    assert estado is Estado.NOVO
    esperado = _texto_aprovado(base_motor, (*projetados, "R31/F2"))

    final = _produzir(pd, estado, base_motor)

    assert final.texto
    assert final.texto == esperado
    assert final.decisoes_do_ciclo[0] is pd.decisao


def test_apresentar_atendimento_inicial_emite_a_saudacao_aprovada(base_motor):
    # M2.1: `APRESENTAR_ATENDIMENTO_INICIAL` → `R01/F1` (PE-24, PE-25).
    pd, estado = _primeira(_payload(), base_motor)
    assert pd.decisao.acoes == (AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL,)
    final = _produzir(pd, estado, base_motor)
    assert final.texto == _texto_aprovado(base_motor, ("R01/F1",))
    assert final.decisoes_do_ciclo == (pd.decisao,)
    assert final.resumo_handoff is None


def test_primeiro_contato_com_visita_saudacao_e_visita_numa_mensagem(base_motor):
    # 1º contato com dado + interesse em visita: a máquina emite T01, T04, T16
    # (saudação, pergunta, visita). A saudação já pergunta o tipo de evento, então
    # a pergunta de coleta não entra: saudação → visita.
    pd, estado = _primeira(
        _payload(dados={"tipo_evento": "evento ficticio"}, intencoes=("interesse_em_visita",)),
        base_motor,
    )
    assert pd.decisao.acoes == (
        AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL,
        AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,
        AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,
    )
    assert pd.qualificacao.campos_ausentes[0] == "nome"

    final = _produzir(pd, estado, base_motor)

    partes = [
        _texto_aprovado(base_motor, (token,)) for token in ("R01/F1", "R06/F1")
    ]
    assert final.texto == "\n\n".join(partes)
    assert final.texto.split("\n\n") == partes
    assert all("\n" not in parte for parte in partes)


def test_retomada_seguida_da_pergunta_do_proximo_campo(base_motor):
    pd, estado = _primeira(
        _payload(dados={"nome": "Nome Ficticio"}),
        base_motor,
        atendimento=_registro(Estado.RESPONDENDO_DUVIDAS, {"tipo_evento": "evento ficticio"}),
    )
    assert pd.decisao.acoes == (AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR,)
    assert pd.qualificacao.campos_ausentes[0] == "contato"

    final = _produzir(pd, estado, base_motor)

    # Prioridade natural: data antes de convidados, nome e contato.
    assert final.texto == _texto_aprovado(base_motor, ("R32/F1", "R31/F3"))


def test_resposta_comercial_em_coleta_retoma_e_pergunta_numa_mensagem(
    base_motor, monkeypatch
):
    validados: list[str] = []
    original = orchestrator_emission.validar_resposta_final

    def espiao(texto: str, montada: Any) -> Any:
        validados.append(texto)
        return original(texto, montada)

    monkeypatch.setattr(orchestrator_emission, "validar_resposta_final", espiao)
    contador = _contar_decidir(monkeypatch)
    pd, estado = _primeira(
        _payload(perguntas=("preco_locacao",)),
        base_motor,
        atendimento=_registro(Estado.COLETANDO_DADOS, {"tipo_evento": "evento ficticio"}),
    )
    assert pd.decisao.caminho == (Transicao.T10,)
    resposta = pd.s2d8.fragmentos_autorizados
    assert resposta

    final = _produzir(pd, estado, base_motor)

    assert final.decisoes_do_ciclo[1].caminho == (Transicao.T20,)
    esperado = "\n\n".join(
        (
            _texto_aprovado(base_motor, resposta),
            _texto_aprovado(base_motor, ("R32/F1",)),
            _texto_aprovado(base_motor, ("R31/F3",)),
        )
    )
    assert final.texto == esperado
    # O texto final é validado uma vez; a primeira validação é a da resposta,
    # que sustenta o critério de `E15`.
    assert validados[-1] == esperado
    assert validados.count(esperado) == 1
    assert contador["n"] == 1
    assert final.texto_encaminhamento is None


def test_retomada_do_e15_reprovada_mantem_a_resposta_validada(base_motor, monkeypatch):
    original = orchestrator_emission.validar_resposta_final
    pd, estado = _primeira(
        _payload(perguntas=("preco_locacao",)),
        base_motor,
        atendimento=_registro(Estado.COLETANDO_DADOS, {"tipo_evento": "evento ficticio"}),
    )
    resposta = _texto_aprovado(base_motor, pd.s2d8.fragmentos_autorizados)
    retomada = _texto_aprovado(base_motor, ("R32/F1",))

    def reprova(texto: str, montada: Any) -> Any:
        if retomada in texto:
            return ResultadoValidacaoResposta(False, MotivoValidacaoResposta.TEXTO_DIVERGENTE)
        return original(texto, montada)

    monkeypatch.setattr(orchestrator_emission, "validar_resposta_final", reprova)
    alerta = AlertaEspiao()

    final = _produzir(pd, estado, base_motor, alerta)

    assert final.texto == resposta
    assert len(alerta.chamadas) == 1


def test_regra_incompativel_por_capacidade_informa_o_limite(base_motor):
    acima = base_motor.base["capacidade"]["formato_coquetel"] + 1
    pd, estado = _primeira(
        _payload(dados={"convidados": acima}),
        base_motor,
        atendimento=_registro(Estado.COLETANDO_DADOS, {"tipo_evento": "evento ficticio"}),
    )
    assert AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL in pd.decisao.acoes

    final = _produzir(pd, estado, base_motor)

    assert final.texto == _texto_aprovado(base_motor, ("R33/F1",))


def test_condicoes_de_visita_pela_rota_da_acao_usam_fotografia(base_motor):
    pd, estado = _primeira(
        _payload(intencoes=("interesse_em_visita",)),
        base_motor,
        atendimento=_registro(Estado.COLETANDO_DADOS, {"tipo_evento": "evento ficticio"}),
    )
    assert AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA in pd.decisao.acoes
    assert "R06/F1" not in pd.s2d8.fragmentos_autorizados
    final = _produzir(pd, estado, base_motor)
    assert final.texto == _texto_aprovado(base_motor, ("R06/F1",))


# --------------------------------------------------------------------------
# Review Focus 5 — assunto com `grupos: []` → R03 + resumo
# --------------------------------------------------------------------------


def test_assunto_sem_cobertura_emite_r03_e_gera_resumo(base_motor, monkeypatch):
    contador = _contar_decidir(monkeypatch)
    pd, estado = _primeira(_payload(perguntas=("mobiliario",)), base_motor)
    assert pd.s2d8.fragmentos_autorizados == ()
    assert AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO in pd.decisao.acoes

    final = _produzir(pd, estado, base_motor)

    assert final.texto == _texto_aprovado(base_motor, ("R03/F1",))
    assert final.resumo_handoff is not None
    assert final.texto_encaminhamento == _texto_aprovado(base_motor, ("R08/F1",))
    # R03 não responde a pergunta: sem `E15`; o resumo confirma `E12` → T27.
    assert len(final.decisoes_do_ciclo) == 2
    assert final.decisoes_do_ciclo[1].caminho == (Transicao.T27,)
    assert final.decisoes_do_ciclo[-1].estado_final is Estado.ENCAMINHADO_HUMANO
    assert contador["n"] == 1


# --------------------------------------------------------------------------
# Silêncio
# --------------------------------------------------------------------------


def test_atendimento_humano_nao_produz_texto(base_motor, monkeypatch):
    contador = _contar_decidir(monkeypatch)
    pd, estado = _primeira(
        _payload(perguntas=("preco_locacao",)),
        base_motor,
        atendimento=_registro(Estado.ATENDIMENTO_HUMANO, {"tipo_evento": "evento ficticio"}),
        situacao=SituacaoTakeover.HUMANO_UNICO,
    )
    assert pd.decisao.estado_final is Estado.ATENDIMENTO_HUMANO
    assert AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA in pd.decisao.acoes

    final = _produzir(pd, estado, base_motor)

    assert final.texto is None
    assert final.resumo_handoff is None
    assert final.decisoes_do_ciclo == (pd.decisao,)
    assert contador["n"] == 0


# --------------------------------------------------------------------------
# Etapa 12 — validação reprovada
# --------------------------------------------------------------------------


def test_validacao_reprovada_substitui_por_r03_e_tenta_alerta(base_motor, monkeypatch):
    chamadas = {"n": 0}

    def reprova(texto_candidato: object, montada: object) -> ResultadoValidacaoResposta:
        chamadas["n"] += 1
        return ResultadoValidacaoResposta(False, MotivoValidacaoResposta.TEXTO_DIVERGENTE)

    monkeypatch.setattr(orchestrator_emission, "validar_resposta_final", reprova)
    contador = _contar_decidir(monkeypatch)
    alerta = AlertaEspiao()
    pd, estado = _primeira(_payload(perguntas=("preco_locacao",)), base_motor)

    final = _produzir(pd, estado, base_motor, alerta)

    assert final.texto == _texto_aprovado(base_motor, ("R03/F1",))
    assert chamadas["n"] == 1  # uma única validação; nenhuma nova redação
    assert len(alerta.chamadas) == 1
    assert alerta.chamadas[0]["correlacao"] == CORRELACAO
    assert alerta.chamadas[0]["pendente_preservado"] is True
    # Sem resposta comercial concluída: nada de `E15`, nada de transição extra.
    assert final.decisoes_do_ciclo == (pd.decisao,)
    assert contador["n"] == 0


def test_falha_do_alerta_nao_impede_a_substituicao(base_motor, monkeypatch):
    monkeypatch.setattr(
        orchestrator_emission,
        "validar_resposta_final",
        lambda t, m: ResultadoValidacaoResposta(False, MotivoValidacaoResposta.TEXTO_DIVERGENTE),
    )

    def alerta_quebrado(**_: Any) -> None:
        raise RuntimeError("canal de alerta fora")

    pd, estado = _primeira(_payload(perguntas=("preco_locacao",)), base_motor)
    final = produzir_texto_final(
        pd,
        base_motor=base_motor,
        estado_inicial=estado,
        mensagem=MENSAGEM,
        tentar_alerta=alerta_quebrado,
        correlacao=CORRELACAO,
    )
    assert final.texto == _texto_aprovado(base_motor, ("R03/F1",))


# --------------------------------------------------------------------------
# Fechamento do ciclo — `E15` e `E12`
# --------------------------------------------------------------------------


def test_e15_reentra_apos_resposta_comercial_e_retoma_coleta(base_motor, monkeypatch):
    contador = _contar_decidir(monkeypatch)
    pd, estado = _primeira(_payload(perguntas=("preco_locacao",)), base_motor)
    assert pd.decisao.estado_final is Estado.RESPONDENDO_DUVIDAS

    final = _produzir(pd, estado, base_motor)

    assert len(final.decisoes_do_ciclo) == 2
    assert Evento.E15 in final.decisoes_do_ciclo[1].eventos_consumidos
    assert final.decisoes_do_ciclo[1].caminho == (Transicao.T20,)
    assert final.decisoes_do_ciclo[-1].estado_final is Estado.COLETANDO_DADOS
    assert final.resumo_handoff is None
    assert final.texto_encaminhamento is None
    assert contador["n"] == 1


def test_cadeia_completa_e15_e12_usa_exatamente_tres_chamadas(base_motor, monkeypatch):
    contador = _contar_decidir(monkeypatch)
    pd, estado = _primeira(
        _payload(perguntas=("preco_locacao",)),
        base_motor,
        atendimento=_registro(Estado.RESPONDENDO_DUVIDAS, _dados_completos(base_motor)),
    )
    assert pd.decisao.caminho == (Transicao.T17,)

    final = _produzir(pd, estado, base_motor)

    caminhos = [d.caminho for d in final.decisoes_do_ciclo]
    assert caminhos == [(Transicao.T17,), (Transicao.T21,), (Transicao.T27,)]
    assert final.decisoes_do_ciclo[-1].estado_final is Estado.ENCAMINHADO_HUMANO
    assert final.resumo_handoff is not None
    assert final.texto
    assert contador["n"] == 2  # + a primeira chamada (Task 4) = 3 no ciclo


def test_e15_inerte_em_pronto_para_handoff_prossegue_para_e12(base_motor):
    pd, estado = _primeira(_payload(perguntas=("preco_locacao", "mobiliario")), base_motor)
    assert pd.decisao.estado_final is Estado.PRONTO_PARA_HANDOFF
    assert pd.s2d8.fragmentos_autorizados

    final = _produzir(pd, estado, base_motor)

    assert len(final.decisoes_do_ciclo) == 3
    assert final.decisoes_do_ciclo[1].caminho == ()
    assert final.decisoes_do_ciclo[2].caminho == (Transicao.T27,)
    # Cobertura mista: os fragmentos de cobertura ficam e R03 vem ao final (PC-4).
    assert final.texto.endswith(_texto_aprovado(base_motor, ("R03/F1",)))


def test_pedido_de_humano_gera_resumo_e12_sem_texto_aprovado(base_motor):
    pd, estado = _primeira(_payload(pedido_de_humano=True), base_motor)
    assert AcaoMaquina.PREPARAR_RESUMO in pd.decisao.acoes

    final = _produzir(pd, estado, base_motor)

    assert final.resumo_handoff is not None
    assert [d.caminho for d in final.decisoes_do_ciclo][-1] == (Transicao.T27,)
    assert final.decisoes_do_ciclo[-1].estado_final is Estado.ENCAMINHADO_HUMANO
    # A mensagem de encaminhamento é a R08 aprovada (docs/04), separada do texto
    # principal: só é enviada depois da entrega do resumo.
    assert final.texto is None
    assert final.texto_encaminhamento == _texto_aprovado(base_motor, ("R08/F1",))


@pytest.mark.parametrize(
    "bruto_kwargs",
    [
        {},
        {"perguntas": ("preco_locacao",)},
        {"perguntas": ("mobiliario",)},
        {"perguntas": ("preco_locacao", "mobiliario")},
        {"pedido_de_humano": True},
        {"perguntas": ("disponibilidade_de_data",)},
    ],
)
def test_nunca_mais_de_tres_chamadas(base_motor, bruto_kwargs):
    pd, estado = _primeira(_payload(**bruto_kwargs), base_motor)
    final = _produzir(pd, estado, base_motor)
    assert 1 <= len(final.decisoes_do_ciclo) <= 3
    assert final.decisoes_do_ciclo[0] is pd.decisao


# --------------------------------------------------------------------------
# Resumo — sem preço
# --------------------------------------------------------------------------


def test_resumo_nao_contem_preco(base_motor):
    pd, estado = _primeira(
        _payload(perguntas=("preco_locacao",)),
        base_motor,
        atendimento=_registro(Estado.RESPONDENDO_DUVIDAS, _dados_completos(base_motor)),
    )
    final = _produzir(pd, estado, base_motor)
    resumo = final.resumo_handoff
    assert resumo is not None
    assert "R$" not in resumo
    for pacote in base_motor.base["precos"]["pacotes"]:
        for campo in ("valor", "hora_adicional"):
            valor = pacote.get(campo)
            if isinstance(valor, int) and not isinstance(valor, bool):
                assert str(valor) not in resumo
                assert f"{valor:,}".replace(",", ".") not in resumo
    assert MENSAGEM in resumo


def test_encaminhamento_reprovado_nao_e_enviado_e_tenta_alerta(base_motor, monkeypatch):
    original = orchestrator_emission.validar_resposta_final

    def reprova_r08(texto_candidato: object, montada: Any) -> ResultadoValidacaoResposta:
        if montada.tokens == ("R08/F1",):
            return ResultadoValidacaoResposta(False, MotivoValidacaoResposta.TEXTO_DIVERGENTE)
        return original(texto_candidato, montada)

    monkeypatch.setattr(orchestrator_emission, "validar_resposta_final", reprova_r08)
    alerta = AlertaEspiao()
    pd, estado = _primeira(_payload(pedido_de_humano=True), base_motor)
    final = _produzir(pd, estado, base_motor, alerta)
    assert final.texto_encaminhamento is None
    assert final.resumo_handoff is not None
    assert len(alerta.chamadas) == 1
