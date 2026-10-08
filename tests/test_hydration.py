"""Testes da hidratação do atendimento (M2, Task 2). Valores sintéticos."""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest

from casa77_sdr.hydration import AtendimentoHidratado, desidratar, hidratar
from casa77_sdr.persistence import RegistroAtendimento
from casa77_sdr.qualification import (
    FormatoEvento,
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.state_machine import DecisaoMaquina, Estado

MARCO = datetime(2000, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def registro_coletando() -> RegistroAtendimento:
    return RegistroAtendimento(
        id_atendimento="at-ficticio",
        canal="canal-ficticio",
        contato="contato-ficticio",
        estado_conversa="coletando_dados",
        dados_coletados={
            "tipo_evento": "evento-ficticio",
            "data_nomeada": "data-ficticia",
            "convidados": 80,
            "nome": "Fulano Ficticio",
            "contato": "contato-ficticio",
            "formato": "sentado",
        },
        instante_ultima_transicao=MARCO,
    )


@pytest.fixture
def decisao_coletando() -> DecisaoMaquina:
    return DecisaoMaquina(
        estado_final=Estado.COLETANDO_DADOS, motivos_handoff=("motivo-x",)
    )


@pytest.fixture
def qualificacao() -> Qualificacao:
    return Qualificacao(
        resultado=ResultadoQualificacao.DADOS_INCOMPLETOS,
        motivo=MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES,
        campos_ausentes=("nome",),
    )


@pytest.fixture
def s2d8_vazio():
    from casa77_sdr.coverage_decision import ResultadoS2D8

    return ResultadoS2D8(
        pendencia_impeditiva=False,
        pendencias_impeditivas=(),
        resposta_aprovada_disponivel=True,
        fragmentos_autorizados=(),
        pendencias_resposta=(),
        causas_e09=(),
    )


def test_sem_registro_e_atendimento_novo():
    at = hidratar(None)
    assert isinstance(at, AtendimentoHidratado)
    assert at.id_atendimento is None
    assert at.estado is Estado.NOVO
    assert at.dados.atendimento.convidados is None
    assert at.marco_atual is None


def test_registro_existente_preserva_estado_e_dados(registro_coletando):
    at = hidratar(registro_coletando)
    assert at.estado is Estado.COLETANDO_DADOS
    assert at.dados.atendimento.convidados == 80
    assert at.dados.atendimento.tipo_evento == "evento-ficticio"
    assert at.dados.atendimento.data_nomeada == "data-ficticia"
    assert at.dados.nome == "Fulano Ficticio"
    assert at.dados.formato is FormatoEvento.SENTADO
    assert at.id_atendimento == registro_coletando.id_atendimento
    assert at.marco_atual == MARCO


def test_chaves_ausentes_viram_none(registro_coletando):
    vazio = dataclasses.replace(registro_coletando, dados_coletados={})
    at = hidratar(vazio)
    assert at.dados.atendimento.tipo_evento is None
    assert at.dados.nome is None
    assert at.dados.formato is None


def test_estado_desconhecido_falha_fechado(registro_coletando):
    ruim = dataclasses.replace(registro_coletando, estado_conversa="inventado")
    with pytest.raises(ValueError):
        hidratar(ruim)


def test_estado_none_em_registro_existente_falha_fechado(registro_coletando):
    ruim = dataclasses.replace(registro_coletando, estado_conversa=None)
    with pytest.raises(ValueError):
        hidratar(ruim)


def test_formato_invalido_falha_fechado(registro_coletando):
    ruim = dataclasses.replace(
        registro_coletando,
        dados_coletados={**registro_coletando.dados_coletados, "formato": "xyz"},
    )
    with pytest.raises(ValueError):
        hidratar(ruim)


def test_ida_e_volta_preserva_dados(
    registro_coletando, decisao_coletando, qualificacao, s2d8_vazio
):
    at = hidratar(registro_coletando)
    reg = desidratar(
        at,
        id_atendimento=at.id_atendimento,
        canal="canal-ficticio",
        contato="contato-ficticio",
        decisao=decisao_coletando,
        qualificacao=qualificacao,
        s2d8=s2d8_vazio,
    )
    assert hidratar(reg).dados == at.dados
    assert reg.estado_conversa == "coletando_dados"
    assert reg.resultado_qualificacao == "dados_incompletos"
    assert reg.motivos_handoff == ("motivo-x",)
    assert reg.pendencias_resposta == ()
    assert reg.instante_ultima_transicao == MARCO


def test_desidratar_atendimento_novo_omite_chaves_none(
    decisao_coletando, qualificacao, s2d8_vazio
):
    reg = desidratar(
        hidratar(None),
        id_atendimento="at-novo",
        canal="c",
        contato="k",
        decisao=decisao_coletando,
        qualificacao=qualificacao,
        s2d8=s2d8_vazio,
    )
    assert reg.dados_coletados == {}
    assert reg.instante_ultima_transicao is None
