"""Testes do resumo determinístico de *handoff* (`handoff_summary`).

Formato de `docs/04-handoff-humano.md` "Conteúdo do resumo entregue". O pacote
aparece **somente** pelo código lido da base, ou "não determinado"; nenhum valor
de preço entra. Valores comerciais são lidos da base real, nunca escritos aqui.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from casa77_sdr.handoff_summary import (
    NAO_DETERMINADO,
    NAO_INFORMADO,
    codigo_pacote_aplicavel,
    montar_resumo_handoff,
)
from casa77_sdr.knowledge import load_knowledge
from casa77_sdr.pricing_applicability import AplicabilidadePacote
from casa77_sdr.qualification import (
    DadosQualificacao,
    FormatoEvento,
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.rules import DadosAtendimento

RAIZ = Path(__file__).resolve().parents[1]

ROTULOS = (
    "Lead:",
    "Contato:",
    "Tipo de evento:",
    "Data pretendida:",
    "Convidados:",
    "Formato:",
    "Pacote aplicável:",
    "Classificação:",
    "Motivo do handoff:",
    "Perguntas em aberto:",
    "Histórico:",
)


@pytest.fixture(scope="module")
def base() -> dict:
    return load_knowledge(RAIZ / "knowledge" / "casa77.yaml")


def _qualificacao(resultado: ResultadoQualificacao) -> Qualificacao:
    return Qualificacao(resultado=resultado, motivo=MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES)


def test_faixas_mapeiam_para_o_codigo_do_pacote_da_base(base):
    pacotes = sorted(base["precos"]["pacotes"], key=lambda p: p["limite_convidados"])
    assert codigo_pacote_aplicavel(AplicabilidadePacote.FAIXA_INFERIOR, base) == pacotes[0]["codigo"]
    assert codigo_pacote_aplicavel(AplicabilidadePacote.FAIXA_SUPERIOR, base) == pacotes[-1]["codigo"]
    assert codigo_pacote_aplicavel(AplicabilidadePacote.INDETERMINADO, base) is None
    assert codigo_pacote_aplicavel(AplicabilidadePacote.NENHUM_APLICAVEL, base) is None


def test_resumo_segue_o_formato_de_docs_04_na_ordem(base):
    dados = DadosQualificacao(
        atendimento=DadosAtendimento(tipo_evento="tipo ficticio", data_nomeada="data ficticia", convidados=7),
        nome="Nome Ficticio",
        contato="contato-ficticio",
        formato=FormatoEvento.SENTADO,
    )
    resumo = montar_resumo_handoff(
        dados=dados,
        qualificacao=_qualificacao(ResultadoQualificacao.QUALIFICADO),
        codigo_pacote="CODIGO_FICTICIO",
        motivos=("pedido_humano",),
        perguntas_em_aberto=("pergunta 1", "pergunta 2"),
        historico="mensagem ficticia",
    )
    linhas = resumo.split("\n")
    assert len(linhas) == len(ROTULOS)
    for linha, rotulo in zip(linhas, ROTULOS, strict=True):
        assert linha.startswith(rotulo)
    assert linhas[0] == "Lead: Nome Ficticio"
    assert linhas[4] == "Convidados: 7"
    assert linhas[5] == f"Formato: {FormatoEvento.SENTADO.value}"
    assert linhas[6] == "Pacote aplicável: CODIGO_FICTICIO"
    assert linhas[7] == f"Classificação: {ResultadoQualificacao.QUALIFICADO.value}"
    assert linhas[8] == "Motivo do handoff: pedido_humano"
    assert linhas[9] == "Perguntas em aberto: pergunta 1; pergunta 2"
    assert linhas[10] == "Histórico: mensagem ficticia"


def test_campos_ausentes_viram_nao_informado_e_pacote_nao_determinado():
    resumo = montar_resumo_handoff(
        dados=DadosQualificacao(atendimento=DadosAtendimento()),
        qualificacao=_qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
        codigo_pacote=None,
        motivos=(),
        perguntas_em_aberto=(),
        historico="mensagem ficticia",
    )
    linhas = resumo.split("\n")
    for indice in (0, 1, 2, 3, 4, 5, 8, 9):
        assert linhas[indice].endswith(NAO_INFORMADO)
    assert linhas[6] == f"Pacote aplicável: {NAO_DETERMINADO}"
