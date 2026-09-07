"""Testes da composição total de status dos fragmentos emitíveis.

A fronteira resolve o status de **todas** as ocorrências físicas de fragmento
emitível de um documento: `ST1`–`ST3` por `propagar_status`, `PARCIAL` pelas
declarações lidas pela `C14`, e **falha fechada** diante de rótulo `G2` válido
sem tradução automática.

Estes testes provam a ordem física, a preservação de homônimos e de tokens
textualmente repetidos, o consumo do fluxo da `C14` **na ordem que ela mesma
produziu**, a propagação intacta das exceções de `C8`, `C12`, `C14` e `SP5`, a
precedência entre elas, os três invariantes internos e a pureza do módulo de
produção. Eles **não** transformam em norma coisa alguma sobre índice, bijeção
física ou `C-A1-ST8`. **Nenhum teste toca o corpus versionado**: todos os
documentos são **sintéticos**.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr import response_status_composition
from casa77_sdr.response_fragment_status import DeclaracaoDeStatusInvalida
from casa77_sdr.response_header_labels import (
    CabecalhoRxxInvalido,
    extrair_rotulos_de_cabecalho,
)
from casa77_sdr.response_markdown_units import RepresentacaoMarcadaInvalida
from casa77_sdr.response_status import StatusNaoCanonicalizavel
from casa77_sdr.response_status_composition import compor_status_dos_fragmentos

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

# Separador literal de `G2`: SPACE + EM DASH + SPACE, montado por ponto de
# codigo para que o teste nao dependa da forma como este arquivo foi gravado.
SEPARADOR = " " + chr(0x2014) + " "

ROTULO_ST1 = "APROVADO"
ROTULO_ST2 = "AGUARDA APROVA" + chr(0x00C7) + chr(0x00C3) + "O"
ROTULO_ST3 = "APROVADO com handoff obrigat" + chr(0x00F3) + "rio"
ROTULO_PARCIAL = "PARCIAL"
ROTULO_DESCONHECIDO = "REVISAO INTERNA"

STATUS_APROVADO = "APROVADO"
STATUS_AGUARDA = "AGUARDA_APROVACAO"
STATUS_BLOQUEADO = "BLOQUEADO"

BLOCO = "> conteudo"

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_status_composition.py"
)
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)


def cabecalho(rxx="R01", titulo="Titulo", rotulo=ROTULO_ST1):
    """Linha de cabeçalho `G2` sintética."""
    return f"## {rxx}{SEPARADOR}{titulo}{SEPARADOR}{rotulo}"


def marcador(identificador="F1"):
    """Linha de marcador `C-A5` sintética."""
    return f"<!-- fragmento: {identificador} -->"


def declaracao(valor=STATUS_APROVADO):
    """Linha de declaração `status-fragmento` sintética, no envelope de `PM1`."""
    return f"<!-- status-fragmento: {valor} -->"


def unidade(identificador="F1"):
    """Marcador e bloco de um fragmento emitível, sem declaração."""
    return (marcador(identificador), BLOCO)


def unidade_parcial(identificador="F1", valor=STATUS_APROVADO):
    """Declaração, marcador e bloco de um fragmento sob `PARCIAL`."""
    return (declaracao(valor), marcador(identificador), BLOCO)


def documento(*linhas, terminador="\n"):
    """Documento sintético terminado por `LF`, salvo indicação contrária."""
    return "\n".join(linhas) + terminador


def com_crlf(texto):
    """Mesmo documento com todas as quebras em `CRLF`."""
    return texto.replace("\n", "\r\n")


def _docstrings(arvore):
    """Ids dos nós de constante que são docstring de módulo, classe ou função."""
    ids = set()
    for no in ast.walk(arvore):
        if isinstance(
            no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            corpo = getattr(no, "body", [])
            if (
                corpo
                and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)
            ):
                ids.add(id(corpo[0].value))
    return ids


IDS_DOCSTRING = _docstrings(ARVORE_PRODUCAO)


def _nomes_usados():
    nomes = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


NOMES_PRODUCAO = _nomes_usados()


def _constantes_de_codigo():
    """Constantes `str` do módulo que **não** são docstring."""
    return [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, str)
        and id(no) not in IDS_DOCSTRING
    ]


def _funcao_publica():
    return next(
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.FunctionDef)
        and no.name == "compor_status_dos_fragmentos"
    )


class InstanciasInstaveis:
    """Dependência que devolve conteúdo diferente entre iterações.

    Simula uma associação física que **não é autoconsistente** — exatamente a
    espécie de defeito interno que `I2` existe para recusar.
    """

    def __init__(self, primeiras, ultima):
        self._primeiras = primeiras
        self._ultima = ultima
        self._vezes = 0

    def __iter__(self):
        self._vezes += 1
        alvo = self._primeiras if self._vezes <= 2 else self._ultima
        return iter(alvo)


# ---------------------------------------------------------------------------
# A. Sucesso e forma da saida
# ---------------------------------------------------------------------------


def test_documento_vazio_devolve_tupla_vazia():
    assert compor_status_dos_fragmentos("") == ()


def test_documento_so_com_quebra_devolve_tupla_vazia():
    assert compor_status_dos_fragmentos("\n") == ()


def test_documento_sem_rxx_devolve_tupla_vazia():
    texto = documento("# Documento", "", "texto comum", "")
    assert compor_status_dos_fragmentos(texto) == ()


def test_forma_da_saida_e_tupla_de_pares_de_str():
    resultado = compor_status_dos_fragmentos(
        documento(cabecalho(), *unidade("F1"), *unidade("F2"))
    )
    assert isinstance(resultado, tuple)
    for entrada in resultado:
        assert type(entrada) is tuple
        assert len(entrada) == 2
        token, status = entrada
        assert type(token) is str
        assert type(status) is str


def test_saida_e_imutavel():
    resultado = compor_status_dos_fragmentos(documento(cabecalho(), *unidade("F1")))
    with pytest.raises(TypeError):
        resultado[0] = ("R01/F1", STATUS_BLOQUEADO)


# ---------------------------------------------------------------------------
# B. ST1-ST3 — propagacao uniforme
# ---------------------------------------------------------------------------


def test_st1_um_fragmento():
    texto = documento(cabecalho("R01", rotulo=ROTULO_ST1), *unidade("F1"))
    assert compor_status_dos_fragmentos(texto) == (("R01/F1", STATUS_APROVADO),)


def test_st2_um_fragmento():
    texto = documento(cabecalho("R02", rotulo=ROTULO_ST2), *unidade("F1"))
    assert compor_status_dos_fragmentos(texto) == (("R02/F1", STATUS_AGUARDA),)


def test_st3_um_fragmento_sem_sufixo_de_handoff():
    """`C-A1-ST3` devolve `APROVADO`: o sufixo é instrução operacional."""
    texto = documento(cabecalho("R03", rotulo=ROTULO_ST3), *unidade("F1"))
    assert compor_status_dos_fragmentos(texto) == (("R03/F1", STATUS_APROVADO),)


def test_st1_com_varios_fragmentos_recebe_o_mesmo_status():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        *unidade("F2"),
        *unidade("F3"),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R01/F1", STATUS_APROVADO),
        ("R01/F2", STATUS_APROVADO),
        ("R01/F3", STATUS_APROVADO),
    )


def test_varias_secoes_em_ordem_fisica():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_ST2),
        *unidade("F1"),
        *unidade("F2"),
        cabecalho("R03", rotulo=ROTULO_ST3),
        *unidade("F1"),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R01/F1", STATUS_APROVADO),
        ("R02/F1", STATUS_AGUARDA),
        ("R02/F2", STATUS_AGUARDA),
        ("R03/F1", STATUS_APROVADO),
    )


def test_status_nao_depende_de_posicao_nem_de_id():
    texto = documento(
        cabecalho("R09", rotulo=ROTULO_ST2), *unidade("F2"), *unidade("F10")
    )
    resultado = compor_status_dos_fragmentos(texto)
    assert [status for _, status in resultado] == [STATUS_AGUARDA, STATUS_AGUARDA]


def test_ids_em_ordem_nao_lexicografica_sao_preservados():
    texto = documento(
        cabecalho("R09"), *unidade("F2"), *unidade("F10"), *unidade("F1")
    )
    tokens = [token for token, _ in compor_status_dos_fragmentos(texto)]
    assert tokens == ["R09/F2", "R09/F10", "R09/F1"]
    assert tokens != sorted(tokens)


# ---------------------------------------------------------------------------
# C. PARCIAL — resolvido exclusivamente pela C14
# ---------------------------------------------------------------------------


def test_parcial_com_um_fragmento():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL), *unidade_parcial("F1", STATUS_APROVADO)
    )
    assert compor_status_dos_fragmentos(texto) == (("R28/F1", STATUS_APROVADO),)


def test_parcial_com_varios_fragmentos():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_APROVADO),
        *unidade_parcial("F2", STATUS_AGUARDA),
        *unidade_parcial("F3", STATUS_BLOQUEADO),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R28/F1", STATUS_APROVADO),
        ("R28/F2", STATUS_AGUARDA),
        ("R28/F3", STATUS_BLOQUEADO),
    )


def test_parcial_com_status_iguais():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_AGUARDA),
        *unidade_parcial("F2", STATUS_AGUARDA),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R28/F1", STATUS_AGUARDA),
        ("R28/F2", STATUS_AGUARDA),
    )


def test_parcial_contendo_bloqueado():
    """`BLOQUEADO` é alcançável **somente** por declaração explícita."""
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
    )
    assert compor_status_dos_fragmentos(texto) == (("R28/F1", STATUS_BLOQUEADO),)


def test_mistura_de_st1_st3_e_parcial():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
        *unidade_parcial("F2", STATUS_APROVADO),
        cabecalho("R03", rotulo=ROTULO_ST3),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_ST2),
        *unidade("F1"),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R01/F1", STATUS_APROVADO),
        ("R28/F1", STATUS_BLOQUEADO),
        ("R28/F2", STATUS_APROVADO),
        ("R03/F1", STATUS_APROVADO),
        ("R02/F1", STATUS_AGUARDA),
    )


def test_parcial_no_meio_nao_desalinha_o_fluxo():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        *unidade("F2"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
        cabecalho("R05", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R29", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_AGUARDA),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R01/F1", STATUS_APROVADO),
        ("R01/F2", STATUS_APROVADO),
        ("R28/F1", STATUS_BLOQUEADO),
        ("R05/F1", STATUS_APROVADO),
        ("R29/F1", STATUS_AGUARDA),
    )


# ---------------------------------------------------------------------------
# D. Homonimos e tokens textualmente repetidos
# ---------------------------------------------------------------------------


def test_homonimas_com_rotulos_diferentes():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST2),
        *unidade("F1"),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R28/F1", STATUS_APROVADO),
        ("R28/F1", STATUS_AGUARDA),
    )


def test_homonimas_com_token_textual_repetido_e_mesmo_status():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    resultado = compor_status_dos_fragmentos(texto)
    assert resultado == (
        ("R28/F1", STATUS_APROVADO),
        ("R28/F1", STATUS_APROVADO),
    )
    assert len(resultado) == 2


def test_duas_instancias_parcial_homonimas_mesmo_token_status_diferentes():
    """A ordem física da `C14` é preservada, e nada é agrupado por `Rxx`."""
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_APROVADO),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R28/F1", STATUS_APROVADO),
        ("R28/F1", STATUS_BLOQUEADO),
    )


def test_tres_instancias_parcial_homonimas_com_status_distintos():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_AGUARDA),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_APROVADO),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R28/F1", STATUS_BLOQUEADO),
        ("R28/F1", STATUS_AGUARDA),
        ("R28/F1", STATUS_APROVADO),
    )


def test_homonimas_uma_parcial_e_uma_st1_com_o_mesmo_token():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R28/F1", STATUS_BLOQUEADO),
        ("R28/F1", STATUS_APROVADO),
    )


def test_nada_e_deduplicado_nem_agrupado():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    assert len(compor_status_dos_fragmentos(texto)) == 3


# ---------------------------------------------------------------------------
# E. Politica de linha e escopo de secao
# ---------------------------------------------------------------------------


def test_lf_e_crlf_sao_estruturalmente_equivalentes():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
    )
    assert compor_status_dos_fragmentos(com_crlf(texto)) == (
        compor_status_dos_fragmentos(texto)
    )


def test_documento_sem_quebra_final():
    texto = documento(cabecalho("R01"), *unidade("F1"), terminador="")
    assert compor_status_dos_fragmentos(texto) == (("R01/F1", STATUS_APROVADO),)


def test_parcial_sem_quebra_final():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_AGUARDA),
        terminador="",
    )
    assert compor_status_dos_fragmentos(texto) == (("R28/F1", STATUS_AGUARDA),)


def test_h3_a_h6_nao_encerram_a_secao():
    texto = documento(
        cabecalho("R01"),
        "### Subtitulo",
        *unidade("F1"),
        "###### Outro",
        *unidade("F2"),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R01/F1", STATUS_APROVADO),
        ("R01/F2", STATUS_APROVADO),
    )


def test_h1_encerra_a_secao():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "# Documento",
        "texto comum",
        cabecalho("R02", rotulo=ROTULO_ST2),
        *unidade("F1"),
    )
    assert compor_status_dos_fragmentos(texto) == (
        ("R01/F1", STATUS_APROVADO),
        ("R02/F1", STATUS_AGUARDA),
    )


def test_h2_nao_rxx_encerra_a_secao():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        "## Respostas bloqueadas",
        "texto comum",
    )
    assert compor_status_dos_fragmentos(texto) == (("R01/F1", STATUS_APROVADO),)


def test_quase_declaracao_sob_st1_permanece_conteudo():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        "  <!-- status-fragmento: APROVADO -->",
        *unidade("F1"),
    )
    assert compor_status_dos_fragmentos(texto) == (("R01/F1", STATUS_APROVADO),)


# ---------------------------------------------------------------------------
# F. Determinismo e entrada inalterada
# ---------------------------------------------------------------------------


def test_resultado_e_deterministico():
    texto = documento(
        cabecalho("R01"),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
    )
    assert compor_status_dos_fragmentos(texto) == compor_status_dos_fragmentos(texto)


def test_entrada_nao_e_alterada():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL), *unidade_parcial("F1", STATUS_AGUARDA)
    )
    copia = str(texto)
    compor_status_dos_fragmentos(texto)
    assert texto == copia


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    texto = documento(cabecalho("R01"), *unidade("F1"))
    assert compor_status_dos_fragmentos(texto) == (("R01/F1", STATUS_APROVADO),)


# ---------------------------------------------------------------------------
# G. Falhas de C8 e C12 — propagacao intacta
# ---------------------------------------------------------------------------


def test_violacao_c_a5_propaga_intacta():
    texto = documento(cabecalho("R01"), marcador("F1"), "texto")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is RepresentacaoMarcadaInvalida
    assert str(erro.value) == "marcador_sem_bloco: marcador"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_tipo_invalido_pertence_a_c8():
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        compor_status_dos_fragmentos(None)
    assert str(erro.value) == "tipo_invalido: texto"


def test_subclasse_de_str_e_recusada_por_c8():
    class Documento(str):
        pass

    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        compor_status_dos_fragmentos(Documento(""))
    assert str(erro.value) == "tipo_invalido: texto"


def test_secao_sem_unidade_pertence_a_c8():
    texto = documento(cabecalho("R01"), "texto", cabecalho("R02"), *unidade("F1"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert str(erro.value) == "secao_sem_unidade: secao"


def test_violacao_g2_propaga_intacta():
    texto = documento("## R01 - Titulo - APROVADO", *unidade("F1"))
    with pytest.raises(CabecalhoRxxInvalido) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is CabecalhoRxxInvalido
    assert str(erro.value) == "separador_ausente: cabecalho"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


# ---------------------------------------------------------------------------
# H. Falhas da C14 — cinco categorias, propagacao intacta
# ---------------------------------------------------------------------------


def test_c14_valor_invalido():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL), *unidade_parcial("F1", "aprovado")
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is DeclaracaoDeStatusInvalida
    assert str(erro.value) == "valor_invalido: declaracao"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_c14_valor_invalido_com_parcial_como_valor():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", ROTULO_PARCIAL),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert str(erro.value) == "valor_invalido: declaracao"


def test_c14_declaracao_orfa():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        declaracao(STATUS_APROVADO),
        "",
        *unidade("F1"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is DeclaracaoDeStatusInvalida
    assert str(erro.value) == "declaracao_orfa: declaracao"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_c14_declaracao_ausente():
    texto = documento(cabecalho("R28", rotulo=ROTULO_PARCIAL), *unidade("F1"))
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is DeclaracaoDeStatusInvalida
    assert str(erro.value) == "declaracao_ausente: marcador"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_c14_declaracao_proibida_sob_st1():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1), *unidade_parcial("F1", STATUS_APROVADO)
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is DeclaracaoDeStatusInvalida
    assert str(erro.value) == "declaracao_proibida: declaracao"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_c14_declaracao_proibida_sob_rotulo_desconhecido():
    """O regime exclusivo alcança **qualquer** rótulo `G2` que não seja `PARCIAL`."""
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO),
        *unidade_parcial("F1", STATUS_APROVADO),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert str(erro.value) == "declaracao_proibida: declaracao"


def test_c14_declaracao_fora_de_secao():
    texto = documento(
        declaracao(STATUS_APROVADO),
        "texto comum",
        cabecalho("R01"),
        *unidade("F1"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is DeclaracaoDeStatusInvalida
    assert str(erro.value) == "declaracao_fora_de_secao: declaracao"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_nada_e_devolvido_parcialmente_com_falha_pm():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida):
        compor_status_dos_fragmentos(texto)


# ---------------------------------------------------------------------------
# I. Precedencia entre as fronteiras compostas
# ---------------------------------------------------------------------------


def test_falha_c8_posterior_vence_violacao_pm_anterior():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_ST1),
        marcador("F1"),
        "texto",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert str(erro.value) == "marcador_sem_bloco: marcador"


def test_falha_g2_posterior_vence_violacao_pm_anterior():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
        "## R02 - Titulo - APROVADO",
        *unidade("F1"),
    )
    with pytest.raises(CabecalhoRxxInvalido):
        compor_status_dos_fragmentos(texto)


def test_falha_pm_posterior_vence_rotulo_desconhecido_anterior():
    """A `C14` percorre o documento inteiro antes da caminhada local."""
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade("F1"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert str(erro.value) == "declaracao_ausente: marcador"


def test_falha_c8_vence_rotulo_desconhecido_anterior():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_ST1),
        marcador("F1"),
        "texto",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida):
        compor_status_dos_fragmentos(texto)


# ---------------------------------------------------------------------------
# J. SP5 — rotulo G2 valido sem traducao automatica
# ---------------------------------------------------------------------------


def test_rotulo_desconhecido_e_aceito_por_c12_e_permanece_literal():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO), *unidade("F1")
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", ROTULO_DESCONHECIDO),)


def test_rotulo_desconhecido_falha_fechado_na_composicao():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO), *unidade("F1")
    )
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        compor_status_dos_fragmentos(texto)
    assert type(erro.value) is StatusNaoCanonicalizavel
    assert str(erro.value) == "rotulo_nao_mapeado: rotulo"
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_rotulo_desconhecido_nao_produz_cabecalho_invalido():
    """O rótulo desconhecido não torna o cabeçalho `G2` inválido."""
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO), *unidade("F1")
    )
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        compor_status_dos_fragmentos(texto)
    assert not isinstance(erro.value, CabecalhoRxxInvalido)
    assert not isinstance(erro.value, RepresentacaoMarcadaInvalida)
    assert not isinstance(erro.value, DeclaracaoDeStatusInvalida)
    assert not isinstance(erro.value, RuntimeError)


def test_rotulo_desconhecido_com_secoes_validas_antes_e_depois():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_DESCONHECIDO),
        *unidade("F1"),
        cabecalho("R03", rotulo=ROTULO_ST2),
        *unidade("F1"),
    )
    with pytest.raises(StatusNaoCanonicalizavel):
        compor_status_dos_fragmentos(texto)


def test_duas_secoes_desconhecidas():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO),
        *unidade("F1"),
        cabecalho("R02", rotulo="outro rotulo"),
        *unidade("F1"),
    )
    with pytest.raises(StatusNaoCanonicalizavel):
        compor_status_dos_fragmentos(texto)


def test_parcial_valido_nao_cai_no_ramo_desconhecido():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL), *unidade_parcial("F1", STATUS_APROVADO)
    )
    assert compor_status_dos_fragmentos(texto) == (("R28/F1", STATUS_APROVADO),)


def test_c14_invalida_vence_sp5():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", "quarto status"),
        cabecalho("R01", rotulo=ROTULO_DESCONHECIDO),
        *unidade("F1"),
    )
    with pytest.raises(DeclaracaoDeStatusInvalida) as erro:
        compor_status_dos_fragmentos(texto)
    assert str(erro.value) == "valor_invalido: declaracao"


def test_rotulo_desconhecido_nao_devolve_resultado_parcial():
    """Sucesso e fragmento não resolvido são mutuamente exclusivos."""
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R02", rotulo=ROTULO_DESCONHECIDO),
        *unidade("F1"),
    )
    resultado = None
    with pytest.raises(StatusNaoCanonicalizavel):
        resultado = compor_status_dos_fragmentos(texto)
    assert resultado is None


def test_nenhum_status_produzido_e_none_ou_sentinela():
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
    )
    for _, status in compor_status_dos_fragmentos(texto):
        assert status is not None
        assert status in (STATUS_APROVADO, STATUS_AGUARDA, STATUS_BLOQUEADO)


# ---------------------------------------------------------------------------
# K. Invariante I1 — alinhamento do fluxo PARCIAL
# ---------------------------------------------------------------------------


def _texto_parcial_simples():
    return documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_APROVADO),
        *unidade_parcial("F2", STATUS_AGUARDA),
    )


def test_i1_dispara_com_par_a_mais(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda texto: (
            ("R28/F1", STATUS_APROVADO),
            ("R28/F2", STATUS_AGUARDA),
            ("R28/F3", STATUS_APROVADO),
        ),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_parcial_simples())
    assert str(erro.value) == "invariante_estrutural"


def test_i1_dispara_com_par_a_menos(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda texto: (("R28/F1", STATUS_APROVADO),),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_parcial_simples())
    assert str(erro.value) == "invariante_estrutural"


def test_i1_dispara_com_token_divergente(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda texto: (
            ("R28/F1", STATUS_APROVADO),
            ("R99/F2", STATUS_AGUARDA),
        ),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_parcial_simples())
    assert str(erro.value) == "invariante_estrutural"


def test_i1_dispara_com_ordem_divergente(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda texto: (
            ("R28/F2", STATUS_AGUARDA),
            ("R28/F1", STATUS_APROVADO),
        ),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_parcial_simples())
    assert str(erro.value) == "invariante_estrutural"


def test_i1_dispara_com_par_de_instancia_nao_parcial(monkeypatch):
    texto = documento(cabecalho("R01", rotulo=ROTULO_ST1), *unidade("F1"))
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda entrada: (("R01/F1", STATUS_APROVADO),),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(texto)
    assert str(erro.value) == "invariante_estrutural"


def test_i1_nao_dispara_quando_o_fluxo_coincide(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda texto: (
            ("R28/F1", STATUS_BLOQUEADO),
            ("R28/F2", STATUS_BLOQUEADO),
        ),
    )
    assert compor_status_dos_fragmentos(_texto_parcial_simples()) == (
        ("R28/F1", STATUS_BLOQUEADO),
        ("R28/F2", STATUS_BLOQUEADO),
    )


def test_i1_nunca_e_excecao_publica(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda texto: (),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_parcial_simples())
    assert type(erro.value) is RuntimeError
    assert not isinstance(erro.value, DeclaracaoDeStatusInvalida)
    assert not isinstance(erro.value, StatusNaoCanonicalizavel)
    assert not isinstance(erro.value, CabecalhoRxxInvalido)
    assert not isinstance(erro.value, RepresentacaoMarcadaInvalida)


# ---------------------------------------------------------------------------
# L. Invariante I2 — cobertura da composicao
# ---------------------------------------------------------------------------


def _texto_st1_dois_fragmentos():
    return documento(
        cabecalho("R01", rotulo=ROTULO_ST1), *unidade("F1"), *unidade("F2")
    )


def test_i2_dispara_quando_a_propagacao_omite(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "propagar_status",
        lambda rotulo, tokens: ((tokens[0], STATUS_APROVADO),),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert str(erro.value) == "invariante_estrutural"


def test_i2_dispara_quando_a_propagacao_inventa(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "propagar_status",
        lambda rotulo, tokens: tuple(
            (token, STATUS_APROVADO) for token in tokens
        )
        + (("R01/F9", STATUS_APROVADO),),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert str(erro.value) == "invariante_estrutural"


def test_i2_dispara_quando_a_propagacao_reordena(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "propagar_status",
        lambda rotulo, tokens: (
            (tokens[1], STATUS_APROVADO),
            (tokens[0], STATUS_APROVADO),
        ),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert str(erro.value) == "invariante_estrutural"


def test_i2_dispara_com_membership_estruturalmente_incompativel(monkeypatch):
    instaveis = InstanciasInstaveis(
        (("R01", ROTULO_ST1, ("R01/F1",)),),
        (("R01", ROTULO_ST1, ("R01/F1", "R01/F2")),),
    )
    monkeypatch.setattr(
        response_status_composition,
        "associar_fragmentos_a_secao",
        lambda texto: instaveis,
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert str(erro.value) == "invariante_estrutural"


def test_i2_nunca_e_excecao_publica(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "propagar_status",
        lambda rotulo, tokens: (),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert type(erro.value) is RuntimeError


# ---------------------------------------------------------------------------
# M. Invariante I3 — vocabulario fechado de C-3
# ---------------------------------------------------------------------------


def test_i3_dispara_com_quarto_status_vindo_da_propagacao(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "propagar_status",
        lambda rotulo, tokens: tuple((token, "PARCIAL") for token in tokens),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert str(erro.value) == "invariante_estrutural"


def test_i3_dispara_com_quarto_status_vindo_da_c14(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "extrair_status_por_fragmento",
        lambda texto: (
            ("R28/F1", STATUS_APROVADO),
            ("R28/F2", "QUASE_APROVADO"),
        ),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_parcial_simples())
    assert str(erro.value) == "invariante_estrutural"


def test_i3_dispara_com_status_none(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "propagar_status",
        lambda rotulo, tokens: tuple((token, None) for token in tokens),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert str(erro.value) == "invariante_estrutural"


def test_i3_nunca_e_excecao_publica(monkeypatch):
    monkeypatch.setattr(
        response_status_composition,
        "propagar_status",
        lambda rotulo, tokens: tuple((token, "OUTRO") for token in tokens),
    )
    with pytest.raises(RuntimeError) as erro:
        compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert type(erro.value) is RuntimeError


# ---------------------------------------------------------------------------
# N. Ordem e cardinalidade das chamadas
# ---------------------------------------------------------------------------


def test_membership_e_c14_sao_chamadas_uma_vez_cada_e_nessa_ordem(monkeypatch):
    registro = []
    membership = response_status_composition.associar_fragmentos_a_secao
    c14 = response_status_composition.extrair_status_por_fragmento

    def membership_espia(texto):
        registro.append("membership")
        return membership(texto)

    def c14_espia(texto):
        registro.append("c14")
        return c14(texto)

    monkeypatch.setattr(
        response_status_composition, "associar_fragmentos_a_secao", membership_espia
    )
    monkeypatch.setattr(
        response_status_composition, "extrair_status_por_fragmento", c14_espia
    )
    compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert registro == ["membership", "c14"]


def test_c14_e_chamada_mesmo_sem_secao_parcial(monkeypatch):
    registro = []
    c14 = response_status_composition.extrair_status_por_fragmento

    def c14_espia(texto):
        registro.append("c14")
        return c14(texto)

    monkeypatch.setattr(
        response_status_composition, "extrair_status_por_fragmento", c14_espia
    )
    compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert registro == ["c14"]


def test_c14_e_chamada_antes_da_propagacao(monkeypatch):
    registro = []
    c14 = response_status_composition.extrair_status_por_fragmento
    propagacao = response_status_composition.propagar_status

    def c14_espia(texto):
        registro.append("c14")
        return c14(texto)

    def propagacao_espia(rotulo, tokens):
        registro.append("propagacao")
        return propagacao(rotulo, tokens)

    monkeypatch.setattr(
        response_status_composition, "extrair_status_por_fragmento", c14_espia
    )
    monkeypatch.setattr(
        response_status_composition, "propagar_status", propagacao_espia
    )
    compor_status_dos_fragmentos(_texto_st1_dois_fragmentos())
    assert registro == ["c14", "propagacao"]


def test_propagacao_e_chamada_uma_vez_por_instancia_nao_parcial(monkeypatch):
    registro = []
    propagacao = response_status_composition.propagar_status

    def propagacao_espia(rotulo, tokens):
        registro.append(rotulo)
        return propagacao(rotulo, tokens)

    monkeypatch.setattr(
        response_status_composition, "propagar_status", propagacao_espia
    )
    texto = documento(
        cabecalho("R01", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_PARCIAL),
        *unidade_parcial("F1", STATUS_BLOQUEADO),
        cabecalho("R02", rotulo=ROTULO_ST2),
        *unidade("F1"),
    )
    compor_status_dos_fragmentos(texto)
    assert registro == [ROTULO_ST1, ROTULO_ST2]


def test_propagacao_nao_e_chamada_para_instancia_parcial(monkeypatch):
    registro = []
    propagacao = response_status_composition.propagar_status

    def propagacao_espia(rotulo, tokens):
        registro.append(rotulo)
        return propagacao(rotulo, tokens)

    monkeypatch.setattr(
        response_status_composition, "propagar_status", propagacao_espia
    )
    compor_status_dos_fragmentos(_texto_parcial_simples())
    assert registro == []


# ---------------------------------------------------------------------------
# O. Contrato publico
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_um_nome():
    assert response_status_composition.__all__ == ["compor_status_dos_fragmentos"]


def test_nao_ha_nome_publico_fora_de_all():
    publicos = {
        nome
        for nome in vars(response_status_composition)
        if not nome.startswith("_")
        and nome
        not in {
            "annotations",
            "associar_fragmentos_a_secao",
            "extrair_status_por_fragmento",
            "propagar_status",
        }
    }
    assert publicos == set(response_status_composition.__all__)


def test_assinatura_tem_um_unico_parametro_sem_default():
    assinatura = inspect.signature(compor_status_dos_fragmentos)
    assert list(assinatura.parameters) == ["texto"]
    parametro = assinatura.parameters["texto"]
    assert parametro.default is inspect.Parameter.empty
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_anotacao_de_retorno_e_a_arbitrada():
    assinatura = inspect.signature(compor_status_dos_fragmentos)
    assert assinatura.return_annotation == "tuple[tuple[str, str], ...]"


def test_nao_e_exportado_pelo_pacote():
    assert not hasattr(casa77_sdr, "compor_status_dos_fragmentos")
    assert "compor_status_dos_fragmentos" not in getattr(casa77_sdr, "__all__", [])


def test_nenhuma_excecao_publica_nova_foi_definida():
    classes = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)
    ]
    assert classes == []
    for nome, valor in vars(response_status_composition).items():
        if isinstance(valor, type):
            assert not issubclass(valor, BaseException)


def test_producao_nao_declara_dto_nem_dataclass():
    proibidos = {"dataclass", "NamedTuple", "TypedDict", "Enum", "StrEnum"}
    assert not proibidos & NOMES_PRODUCAO


def test_producao_declara_uma_unica_funcao():
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert funcoes == ["compor_status_dos_fragmentos"]


# ---------------------------------------------------------------------------
# P. Pureza do modulo de producao
# ---------------------------------------------------------------------------


def test_imports_sao_exatamente_os_quatro_permitidos():
    assert not [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert [no.module for no in de_onde] == [
        "__future__",
        "casa77_sdr.response_section_membership",
        "casa77_sdr.response_fragment_status",
        "casa77_sdr.response_status_propagation",
    ]
    importados = [alias.name for no in de_onde for alias in no.names]
    assert importados == [
        "annotations",
        "associar_fragmentos_a_secao",
        "extrair_status_por_fragmento",
        "propagar_status",
    ]


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_producao_nao_importa_c8_c12_nem_canonicalizacao():
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    modulos = [no.module for no in de_onde]
    nomes = [alias.name for no in de_onde for alias in no.names]
    for proibido in (
        "casa77_sdr.response_markdown_units",
        "casa77_sdr.response_header_labels",
        "casa77_sdr.response_status",
    ):
        assert proibido not in modulos
    for proibido in (
        "ler_unidades_marcadas",
        "extrair_rotulos_de_cabecalho",
        "canonicalizar_status",
        "StatusNaoCanonicalizavel",
    ):
        assert proibido not in nomes
        assert proibido not in NOMES_PRODUCAO


def test_producao_nao_carrega_os_rotulos_fisicos_de_st1_a_st3():
    """A tradução é inteiramente de `SP2`; não há tabela local aqui."""
    for constante in _constantes_de_codigo():
        assert constante != ROTULO_ST2
        assert constante != ROTULO_ST3
        assert "handoff" not in constante
        assert "AGUARDA " not in constante


def test_producao_nao_interpreta_declaracao_de_status():
    for constante in _constantes_de_codigo():
        assert "status-fragmento" not in constante
        assert "<!--" not in constante
        assert "fragmento:" not in constante


def test_primeira_operacao_funcional_e_a_membership():
    corpo = [no for no in _funcao_publica().body if not isinstance(no, ast.Expr)]
    primeira = corpo[0]
    assert isinstance(primeira, ast.Assign)
    assert isinstance(primeira.value, ast.Call)
    assert isinstance(primeira.value.func, ast.Name)
    assert primeira.value.func.id == "associar_fragmentos_a_secao"


def test_segunda_operacao_funcional_e_a_c14():
    corpo = [no for no in _funcao_publica().body if not isinstance(no, ast.Expr)]
    segunda = corpo[1]
    assert isinstance(segunda, ast.Assign)
    assert isinstance(segunda.value, ast.Call)
    assert isinstance(segunda.value.func, ast.Name)
    assert segunda.value.func.id == "extrair_status_por_fragmento"


def test_a_c14_nao_e_preguicosa():
    """A chamada da `C14` está no corpo da função, fora de `if` e de laço."""
    corpo = [no for no in _funcao_publica().body if not isinstance(no, ast.Expr)]
    segunda = corpo[1]
    for no in ast.walk(_funcao_publica()):
        if isinstance(no, (ast.If, ast.For, ast.While, ast.IfExp)):
            assert segunda not in list(ast.walk(no))


def test_cada_dependencia_e_chamada_uma_unica_vez_no_codigo():
    for nome in (
        "associar_fragmentos_a_secao",
        "extrair_status_por_fragmento",
        "propagar_status",
    ):
        chamadas = [
            no
            for no in ast.walk(ARVORE_PRODUCAO)
            if isinstance(no, ast.Call)
            and isinstance(no.func, ast.Name)
            and no.func.id == nome
        ]
        assert len(chamadas) == 1


def test_nao_ha_captura_de_excecao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_nao_ha_raise_from():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise):
            assert no.cause is None


def test_a_unica_excecao_originada_e_o_invariante():
    lancamentos = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Raise)]
    assert lancamentos
    for lancamento in lancamentos:
        chamada = lancamento.exc
        assert isinstance(chamada, ast.Call)
        assert isinstance(chamada.func, ast.Name)
        assert chamada.func.id == "RuntimeError"
        assert len(chamada.args) == 1
        assert isinstance(chamada.args[0], ast.Name)
        assert chamada.args[0].id == "_INVARIANTE_ESTRUTURAL"


def test_nao_ha_global_nem_nonlocal():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal))


def test_nao_ha_assert_em_producao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, ast.Assert)


def test_nao_ha_dict_nem_conjunto_no_codigo():
    assert not [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.Dict, ast.DictComp, ast.Set, ast.SetComp))
    ]
    proibidos = {"dict", "set", "frozenset", "Counter", "defaultdict", "OrderedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_zip_sorted_map_filter_nem_reversed():
    assert not {"zip", "sorted", "reversed", "map", "filter"} & NOMES_PRODUCAO


def test_nao_ha_io_nem_filesystem():
    proibidos = {
        "open",
        "read",
        "write",
        "read_text",
        "write_text",
        "Path",
        "pathlib",
        "os",
        "io",
        "StringIO",
        "shutil",
        "tempfile",
        "print",
        "input",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_yaml_json_rede_llm_nem_banco():
    proibidos = {
        "yaml",
        "json",
        "safe_load",
        "dumps",
        "pickle",
        "requests",
        "urllib",
        "socket",
        "httpx",
        "anthropic",
        "openai",
        "sqlite3",
        "subprocess",
        "threading",
        "asyncio",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_relogio_calendario_locale_ambiente_nem_logging():
    proibidos = {
        "time",
        "datetime",
        "date",
        "now",
        "utcnow",
        "monotonic",
        "calendar",
        "locale",
        "setlocale",
        "getenv",
        "environ",
        "random",
        "uuid",
        "uuid4",
        "hashlib",
        "md5",
        "sha256",
        "logging",
        "getLogger",
        "cache",
        "lru_cache",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_regex_nem_unicodedata():
    proibidos = {"re", "regex", "match", "fullmatch", "search", "sub", "unicodedata"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_nem_caminhada_markdown():
    proibidos = {
        "strip",
        "lstrip",
        "rstrip",
        "split",
        "splitlines",
        "startswith",
        "endswith",
        "lower",
        "upper",
        "casefold",
        "normalize",
        "encode",
        "decode",
        "expandtabs",
        "translate",
        "replace",
        "format",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_execucao_dinamica():
    proibidos = {"eval", "exec", "compile", "__import__", "globals", "locals", "vars"}
    assert not proibidos & NOMES_PRODUCAO


def test_producao_nao_menciona_corpus_caminho_nem_url():
    for constante in _constantes_de_codigo():
        assert "knowledge" not in constante
        assert ".yaml" not in constante
        assert ".md" not in constante
        assert ".env" not in constante
        assert "http" not in constante
        assert "C:" not in constante
        assert "/home/" not in constante


def test_nao_ha_estado_mutavel_no_modulo():
    for nome, valor in vars(response_status_composition).items():
        if nome.startswith("__") and nome.endswith("__"):
            continue
        if nome == "annotations":
            continue
        assert not isinstance(valor, (list, dict, set, bytearray))


# ---------------------------------------------------------------------------
# Q. Limites
# ---------------------------------------------------------------------------


def test_sucesso_nao_prova_unicidade_global():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
        cabecalho("R28", rotulo=ROTULO_ST1),
        *unidade("F1"),
    )
    resultado = compor_status_dos_fragmentos(texto)
    assert resultado[0] == resultado[1]
    assert len(resultado) == 2


def test_sucesso_nao_prova_completude_do_corpus():
    """Documento sintético mínimo compõe com sucesso e nada afirma sobre `ST8`."""
    texto = documento(cabecalho("R01"), *unidade("F1"))
    assert compor_status_dos_fragmentos(texto) == (("R01/F1", STATUS_APROVADO),)


def test_o_status_nao_e_gravado_no_texto():
    texto = documento(
        cabecalho("R28", rotulo=ROTULO_PARCIAL), *unidade_parcial("F1", STATUS_AGUARDA)
    )
    compor_status_dos_fragmentos(texto)
    assert texto.count(declaracao(STATUS_AGUARDA)) == 1


def test_nenhum_teste_desta_suite_toca_o_corpus():
    """A suíte é sintética: nada aqui lê o corpus versionado.

    Os alvos da busca são montados por concatenação para que a própria asserção
    não os introduza no arquivo e invalide o teste.
    """
    fonte = Path(__file__).read_text(encoding="utf-8")
    assert ("respostas" + "-aprovadas") not in fonte
    assert ("casa77" + ".yaml") not in fonte
    assert ("open" + "(") not in fonte
