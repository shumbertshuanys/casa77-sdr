"""Testes da extração determinística do texto emitível canônico.

A fronteira converte cada bloco **já declarado** da representação marcada em uma
`str` do domínio canônico `D1`–`D7`, ou recusa *fail-closed*. Estes testes provam
a precedência integral do portão `C8`, a proveniência física do terminador de
`MT8` — inclusive a distinção entre `CRLF` e `CR` isolado no fim do texto —, o
prefixo exato de `MT3`/`MT4`, a regra de linha vazia de `MT5`–`MT7`, a quebra
suave de `MT9`, o branco terminal de `MT10`, os dois desfechos de `MT11`, o
silêncio das mensagens, o invariante entre as duas caminhadas, a pureza do módulo
de produção e o determinismo — e **não** transformam em norma a equivalência
`C-15`, a normalização `NFC`, a conversão de quebra suave em espaço, a unicidade
global dos tokens, o índice real ou a bijeção física, que estão **fora** desta
fronteira.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from casa77_sdr.response_emittable_text import (
    TextoEmitivelInvalido,
    extrair_textos_emitiveis,
)
from casa77_sdr.response_markdown_units import (
    RepresentacaoMarcadaInvalida,
    ler_unidades_marcadas,
)

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent

CAMINHO_PRODUCAO = RAIZ / "src" / "casa77_sdr" / "response_emittable_text.py"
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)

CATEGORIAS = (
    "prefixo_invalido",
    "linha_vazia_invalida",
    "terminador_proibido",
    "branco_antes_do_terminador",
)
LOCALIZADORES = ("linha", "unidade")

LF = "\n"
CR = "\r"
TAB = "\t"

# Terminadores exoticos recusados por `MT8`, nomeados por ponto de codigo para
# que o arquivo de teste nao carregue caractere de controle solto.
LS = chr(0x2028)
PS = chr(0x2029)
NEL = chr(0x0085)
VT = chr(0x000B)
FF = chr(0x000C)

EXOTICOS = (LS, PS, NEL, VT, FF)

# `e` acentuado nas duas representacoes: composta e decomposta. Elas sao
# distintas como `str` e devem permanecer distintas na saida - a `NFC`
# pertence ao comparador de `C-15b`, nunca a esta fronteira.
COMPOSTO = chr(0x00E9)
DECOMPOSTO = chr(0x0065) + chr(0x0301)


def marcador(identificador: str) -> str:
    """Linha de marcador com o envelope exato de `C-A5-I1`."""
    return f"<!-- fragmento: {identificador} -->"


def doc(*linhas: str) -> str:
    """Documento sintético terminado em `LF`."""
    return LF.join(linhas) + LF


def sem_newline(*linhas: str) -> str:
    """Mesmo documento sintético terminando direto no `EOF`."""
    return LF.join(linhas)


def crlf(texto: str) -> str:
    """Mesmo documento com terminação `CRLF`, sem tocar em mais nada."""
    return texto.replace(LF, CR + LF)


def categoria_de(excecao: pytest.ExceptionInfo) -> str:
    return str(excecao.value).split(":")[0]


def localizador_de(excecao: pytest.ExceptionInfo) -> str:
    return str(excecao.value).split(": ")[1]


class TextoPermissivo(str):
    """Subclasse de `str` que sequestra a igualdade e o hash."""

    def __eq__(self, outro: object) -> bool:
        return True

    def __hash__(self) -> int:
        return 0


class TextoSimples(str):
    """Subclasse de `str` que não redefine coisa alguma."""


def _docstrings(arvore: ast.AST) -> set[int]:
    """Ids dos nós de constante que são docstring de módulo, classe ou função."""
    ids: set[int] = set()
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


def _nomes_usados() -> set[str]:
    nomes: set[str] = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


NOMES_PRODUCAO = _nomes_usados()


# ---------------------------------------------------------------------------
# Documentos sinteticos amplos, reutilizados pelo invariante `C8`/`C11`
# ---------------------------------------------------------------------------

DOCUMENTOS_VALIDOS: tuple[str, ...] = (
    "",
    LF,
    doc("texto solto sem cabecalho"),
    doc("## Assunto", "texto de secao nao Rxx"),
    doc("## R01", marcador("F1"), "> alfa"),
    sem_newline("## R01", marcador("F1"), "> alfa"),
    doc("## R01", marcador("F1"), "> alfa", "> beta"),
    doc("## R01", marcador("F1"), "> alfa", ">", "> beta"),
    doc("## R01", marcador("F1"), "> alfa", marcador("F2"), "> beta"),
    doc("## R01", marcador("F1"), "> alfa", "## R02", marcador("F1"), "> beta"),
    doc("## R01", marcador("F1"), "> alfa", "## R01", marcador("F1"), "> beta"),
    doc("## R01", marcador("F1"), "> alfa", "# Documento", "texto fora"),
    doc("## R01", marcador("F1"), "> alfa", "## Outro assunto", "texto fora"),
    doc("## R01", "### Sub", marcador("F1"), "> alfa"),
    doc("## R01", "#### Sub", "##### Sub", "###### Sub", marcador("F1"), "> alfa"),
    doc("  ## R01 indentado", "## R01", marcador("F1"), "> alfa"),
    doc("> bloco fora de secao", "## R01", marcador("F1"), "> alfa"),
    doc("## R01", marcador("F1"), "> alfa", "# Fim", "> bloco fora de secao"),
    doc("## R01", "<!-- fragmento:F1 -->", marcador("F1"), "> alfa"),
    doc("## R01", "<!-- fragmento: F1 --> extra", marcador("F1"), "> alfa"),
    doc("## R01", marcador("F10"), "> alfa"),
    doc(
        "# Corpus",
        "## R01",
        marcador("F1"),
        "> alfa",
        "> beta",
        marcador("F2"),
        "> gama",
        "### Nota",
        "## R02",
        marcador("F1"),
        "> delta",
        ">",
        "> epsilon",
        "# Fim",
        "> bloco fora de secao",
    ),
)

DOCUMENTOS_VALIDOS_CRLF: tuple[str, ...] = tuple(
    crlf(texto) for texto in DOCUMENTOS_VALIDOS
)

# Mistura deliberada: a primeira metade em `CRLF`, a segunda em `LF`.
DOCUMENTO_MISTO = (
    "## R01" + CR + LF + marcador("F1") + CR + LF + "> alfa" + LF + "> beta" + LF
)


# ---------------------------------------------------------------------------
# Sucesso — dominio, forma e ordem
# ---------------------------------------------------------------------------


def test_documento_vazio_devolve_tupla_vazia():
    assert extrair_textos_emitiveis("") == ()


def test_documento_sem_rxx_devolve_tupla_vazia():
    texto = doc("# Documento", "## Assunto", "texto qualquer")
    assert extrair_textos_emitiveis(texto) == ()


def test_uma_unidade_uma_linha_sem_newline_final():
    texto = sem_newline("## R01", marcador("F1"), "> alfa")
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa"),)


def test_uma_unidade_uma_linha_com_lf_final():
    texto = doc("## R01", marcador("F1"), "> alfa")
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa"),)


def test_uma_unidade_uma_linha_com_crlf_final():
    texto = crlf(doc("## R01", marcador("F1"), "> alfa"))
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa"),)


def test_bloco_final_com_crlf_nao_deixa_cr_na_saida():
    texto = crlf(doc("## R01", marcador("F1"), "> alfa"))
    (_, emitido), = extrair_textos_emitiveis(texto)
    assert CR not in emitido


def test_multiplas_linhas_do_mesmo_paragrafo():
    texto = doc("## R01", marcador("F1"), "> alfa", "> beta", "> gama")
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa\nbeta\ngama"),)


def test_quebra_suave_produz_exatamente_um_lf():
    texto = doc("## R01", marcador("F1"), "> alfa", "> beta")
    (_, emitido), = extrair_textos_emitiveis(texto)
    assert emitido == "alfa" + LF + "beta"
    assert emitido.count(LF) == 1


def test_quebra_suave_nao_vira_espaco():
    texto = doc("## R01", marcador("F1"), "> alfa", "> beta")
    (_, emitido), = extrair_textos_emitiveis(texto)
    assert " " not in emitido


def test_linha_vazia_interna_e_aceita():
    texto = doc("## R01", marcador("F1"), "> alfa", ">", "> beta")
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa\n\nbeta"),)


def test_linha_vazia_interna_produz_exatamente_dois_lf():
    texto = doc("## R01", marcador("F1"), "> alfa", ">", "> beta")
    (_, emitido), = extrair_textos_emitiveis(texto)
    assert emitido == "alfa" + LF + LF + "beta"
    assert LF + LF + LF not in emitido


def test_duas_linhas_vazias_separadas_produzem_dois_paragrafos():
    texto = doc(
        "## R01", marcador("F1"), "> alfa", ">", "> beta", ">", "> gama"
    )
    assert extrair_textos_emitiveis(texto) == (
        ("R01/F1", "alfa\n\nbeta\n\ngama"),
    )


def test_multiplos_fragmentos_no_mesmo_rxx():
    texto = doc(
        "## R01", marcador("F1"), "> alfa", marcador("F2"), "> beta"
    )
    assert extrair_textos_emitiveis(texto) == (
        ("R01/F1", "alfa"),
        ("R01/F2", "beta"),
    )


def test_multiplos_rxx():
    texto = doc(
        "## R01", marcador("F1"), "> alfa", "## R02", marcador("F1"), "> beta"
    )
    assert extrair_textos_emitiveis(texto) == (
        ("R01/F1", "alfa"),
        ("R02/F1", "beta"),
    )


def test_ordem_e_a_fisica_do_documento():
    texto = doc(
        "## R02",
        marcador("F2"),
        "> segundo",
        "## R01",
        marcador("F1"),
        "> primeiro",
    )
    assert [token for token, _ in extrair_textos_emitiveis(texto)] == [
        "R02/F2",
        "R01/F1",
    ]


def test_token_fica_com_o_texto_declarado_correspondente():
    texto = doc(
        "## R07",
        marcador("F3"),
        "> conteudo de F3",
        marcador("F1"),
        "> conteudo de F1",
        "## R09",
        marcador("F2"),
        "> conteudo de F2",
    )
    assert dict(extrair_textos_emitiveis(texto)) == {
        "R07/F3": "conteudo de F3",
        "R07/F1": "conteudo de F1",
        "R09/F2": "conteudo de F2",
    }


def test_documento_integralmente_em_lf():
    texto = doc(
        "## R01", marcador("F1"), "> alfa", ">", "> beta", marcador("F2"), "> gama"
    )
    assert extrair_textos_emitiveis(texto) == (
        ("R01/F1", "alfa\n\nbeta"),
        ("R01/F2", "gama"),
    )


def test_documento_integralmente_em_crlf_produz_o_mesmo():
    texto = doc(
        "## R01", marcador("F1"), "> alfa", ">", "> beta", marcador("F2"), "> gama"
    )
    assert extrair_textos_emitiveis(crlf(texto)) == extrair_textos_emitiveis(texto)


def test_mistura_de_lf_e_crlf_entre_linhas_e_aceita():
    assert extrair_textos_emitiveis(DOCUMENTO_MISTO) == (("R01/F1", "alfa\nbeta"),)


def test_mistura_dentro_da_mesma_unidade_e_aceita():
    texto = (
        "## R01"
        + LF
        + marcador("F1")
        + LF
        + "> alfa"
        + CR
        + LF
        + "> beta"
        + LF
        + "> gama"
        + CR
        + LF
    )
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa\nbeta\ngama"),)


def test_unicode_composto_e_preservado():
    composto = "caf" + COMPOSTO
    texto = doc("## R01", marcador("F1"), "> " + composto)
    assert extrair_textos_emitiveis(texto) == (("R01/F1", composto),)


def test_unicode_decomposto_e_preservado():
    decomposto = "caf" + DECOMPOSTO
    texto = doc("## R01", marcador("F1"), "> " + decomposto)
    assert extrair_textos_emitiveis(texto) == (("R01/F1", decomposto),)


def test_zero_nfc_composto_e_decomposto_permanecem_distintos():
    composto = "caf" + COMPOSTO
    decomposto = "caf" + DECOMPOSTO
    texto = doc(
        "## R01",
        marcador("F1"),
        "> " + composto,
        marcador("F2"),
        "> " + decomposto,
    )
    (_, primeiro), (_, segundo) = extrair_textos_emitiveis(texto)
    assert primeiro == composto
    assert segundo == decomposto
    assert primeiro != segundo


def test_token_global_repetido_quando_c8_permite():
    texto = doc(
        "## R01", marcador("F1"), "> alfa", "## R01", marcador("F1"), "> beta"
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F1")
    assert extrair_textos_emitiveis(texto) == (
        ("R01/F1", "alfa"),
        ("R01/F1", "beta"),
    )


def test_bloco_fora_de_rxx_e_ignorado_integralmente():
    texto = doc(
        "> bloco antes de qualquer secao",
        "## R01",
        marcador("F1"),
        "> alfa",
        "# Fim",
        "> bloco depois do fim da secao",
    )
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa"),)


def test_bloco_fora_de_rxx_nao_e_validado_textualmente():
    # O bloco de fora viola `MT3`, `MT7` e `MT10` ao mesmo tempo e ainda assim
    # nao produz falha: ele esta fora do dominio de `C-A5-U2`.
    texto = doc(
        "# Fora",
        ">colado",
        ">",
        "> com branco terminal ",
        "## R01",
        marcador("F1"),
        "> alfa",
    )
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa"),)


def test_tokens_localizados_iguais_aos_de_c8():
    texto = DOCUMENTOS_VALIDOS[-1]
    assert tuple(
        token for token, _ in extrair_textos_emitiveis(texto)
    ) == ler_unidades_marcadas(texto)


def test_saida_e_deterministica():
    texto = DOCUMENTOS_VALIDOS[-1]
    assert extrair_textos_emitiveis(texto) == extrair_textos_emitiveis(texto)


def test_entrada_nao_e_alterada():
    texto = doc("## R01", marcador("F1"), "> alfa", ">", "> beta")
    copia = str(texto)
    extrair_textos_emitiveis(texto)
    assert texto == copia


def test_retorno_e_tupla_de_pares_de_str():
    texto = doc("## R01", marcador("F1"), "> alfa")
    resultado = extrair_textos_emitiveis(texto)
    assert isinstance(resultado, tuple)
    for par in resultado:
        assert isinstance(par, tuple)
        assert len(par) == 2
        assert type(par[0]) is str
        assert type(par[1]) is str


def test_texto_emitido_pertence_ao_dominio_canonico():
    texto = DOCUMENTOS_VALIDOS[-1]
    for _, emitido in extrair_textos_emitiveis(texto):
        assert emitido
        assert CR not in emitido
        assert not any(exotico in emitido for exotico in EXOTICOS)
        assert not emitido.startswith(LF)
        assert not emitido.endswith(LF)
        assert LF + LF + LF not in emitido
        assert " " + LF not in emitido
        assert TAB + LF not in emitido
        assert LF + " " not in emitido
        assert LF + TAB not in emitido


# ---------------------------------------------------------------------------
# Fail-closed — prefixo (`MT3`, `MT4`)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "linha",
    [
        ">colado",
        ">  dois espacos",
        ">" + TAB + "tab colado",
        "> " + TAB + "tab apos o espaco",
        "> ",
    ],
)
def test_prefixo_invalido_e_recusado(linha):
    texto = doc("## R01", marcador("F1"), linha)
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "prefixo_invalido: linha"


def test_prefixo_invalido_em_linha_posterior_da_unidade():
    texto = doc("## R01", marcador("F1"), "> alfa", ">colado")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "prefixo_invalido: linha"


def test_prefixo_invalido_com_crlf_tambem_e_recusado():
    texto = crlf(doc("## R01", marcador("F1"), ">colado"))
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "prefixo_invalido: linha"


def test_prefixo_invalido_sem_newline_final():
    texto = sem_newline("## R01", marcador("F1"), ">colado")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "prefixo_invalido: linha"


# ---------------------------------------------------------------------------
# Fail-closed — linha vazia (`MT5`, `MT6`, `MT7`)
# ---------------------------------------------------------------------------


def test_linha_vazia_na_borda_inicial_e_recusada():
    texto = doc("## R01", marcador("F1"), ">", "> alfa")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "linha_vazia_invalida: unidade"


def test_linha_vazia_na_borda_final_e_recusada():
    texto = doc("## R01", marcador("F1"), "> alfa", ">")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "linha_vazia_invalida: unidade"


def test_unidade_inteiramente_vazia_e_recusada():
    texto = doc("## R01", marcador("F1"), ">")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "linha_vazia_invalida: unidade"


def test_duas_linhas_vazias_consecutivas_sao_recusadas():
    texto = doc("## R01", marcador("F1"), "> alfa", ">", ">", "> beta")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "linha_vazia_invalida: unidade"


def test_tres_linhas_vazias_consecutivas_sao_recusadas():
    texto = doc("## R01", marcador("F1"), "> alfa", ">", ">", ">", "> beta")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "linha_vazia_invalida: unidade"


def test_linha_vazia_invalida_nao_e_colapsada_nem_corrigida():
    texto = doc("## R01", marcador("F1"), "> alfa", ">", ">", "> beta")
    with pytest.raises(TextoEmitivelInvalido):
        extrair_textos_emitiveis(texto)


# ---------------------------------------------------------------------------
# Fail-closed — branco antes do terminador (`MT10`)
# ---------------------------------------------------------------------------


def test_espaco_terminal_e_recusado():
    texto = doc("## R01", marcador("F1"), "> alfa ")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "branco_antes_do_terminador: linha"


def test_tab_terminal_e_recusado():
    texto = doc("## R01", marcador("F1"), "> alfa" + TAB)
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "branco_antes_do_terminador: linha"


def test_espaco_terminal_antes_de_crlf_e_recusado():
    texto = crlf(doc("## R01", marcador("F1"), "> alfa "))
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "branco_antes_do_terminador: linha"


def test_espaco_terminal_no_eof_sem_newline_e_recusado():
    texto = sem_newline("## R01", marcador("F1"), "> alfa ")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "branco_antes_do_terminador: linha"


# ---------------------------------------------------------------------------
# Fail-closed — terminadores (`MT8`)
# ---------------------------------------------------------------------------


def test_cr_isolado_interno_e_recusado():
    texto = "## R01" + LF + marcador("F1") + LF + "> alfa" + CR + "beta" + LF
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


def test_cr_isolado_no_eof_e_recusado():
    texto = "## R01" + LF + marcador("F1") + LF + "> alfa" + CR
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


def test_cr_isolado_no_eof_e_estruturalmente_aceito_por_c8():
    # `MT2` em acao: `C8` reconhece o bloco pela sua politica local de linha, e
    # `C11` ainda assim o recusa **textualmente**.
    texto = "## R01" + LF + marcador("F1") + LF + "> alfa" + CR
    assert ler_unidades_marcadas(texto) == ("R01/F1",)
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


def test_mesmo_bloco_com_crlf_no_eof_e_aceito():
    # Prova que a recusa anterior vem da **ausencia** do `LF`, e nao do `CR`.
    texto = "## R01" + LF + marcador("F1") + LF + "> alfa" + CR + LF
    assert extrair_textos_emitiveis(texto) == (("R01/F1", "alfa"),)


def test_dois_cr_antes_de_lf_sao_recusados():
    texto = "## R01" + LF + marcador("F1") + LF + "> alfa" + CR + CR + LF
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


@pytest.mark.parametrize("exotico", EXOTICOS)
def test_terminador_exotico_e_recusado(exotico):
    texto = doc("## R01", marcador("F1"), "> alfa" + exotico + "beta")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


@pytest.mark.parametrize("exotico", EXOTICOS)
def test_terminador_exotico_no_fim_da_linha_e_recusado(exotico):
    texto = doc("## R01", marcador("F1"), "> alfa" + exotico)
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


def test_mistura_de_terminador_permitido_e_proibido_e_recusada():
    texto = (
        "## R01"
        + LF
        + marcador("F1")
        + LF
        + "> alfa"
        + CR
        + LF
        + "> beta"
        + VT
        + LF
        + "> gama"
        + LF
    )
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


def test_terminador_proibido_vence_o_prefixo_na_mesma_linha():
    # A ordem local de falha coloca o terminador **antes** do prefixo.
    texto = "## R01" + LF + marcador("F1") + LF + ">colado" + CR + CR + LF
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "terminador_proibido: linha"


def test_prefixo_vence_o_branco_terminal_na_mesma_linha():
    texto = doc("## R01", marcador("F1"), ">  dois espacos e um final ")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "prefixo_invalido: linha"


def test_violacao_de_linha_vence_a_regra_de_unidade():
    # A regra de linha vazia e da **unidade** e so e avaliada depois que todas
    # as linhas passam pelas suas proprias verificacoes.
    texto = doc("## R01", marcador("F1"), ">", ">colado")
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "prefixo_invalido: linha"


def test_primeira_unidade_invalida_encerra_sem_devolver_nada():
    texto = doc(
        "## R01",
        marcador("F1"),
        ">colado",
        marcador("F2"),
        "> valido",
    )
    with pytest.raises(TextoEmitivelInvalido):
        extrair_textos_emitiveis(texto)


def test_unidade_posterior_invalida_encerra_sem_devolver_a_anterior():
    texto = doc(
        "## R01",
        marcador("F1"),
        "> valido",
        marcador("F2"),
        ">colado",
    )
    with pytest.raises(TextoEmitivelInvalido):
        extrair_textos_emitiveis(texto)


# ---------------------------------------------------------------------------
# Silencio da mensagem
# ---------------------------------------------------------------------------


MENSAGENS_DE_FALHA = (
    doc("## R01", marcador("F1"), ">colado-com-conteudo-comercial"),
    doc("## R01", marcador("F1"), ">", "> alfa"),
    doc("## R01", marcador("F1"), "> alfa "),
    "## R09" + LF + marcador("F7") + LF + "> alfa" + CR,
)


@pytest.mark.parametrize("texto", MENSAGENS_DE_FALHA)
def test_mensagem_tem_apenas_categoria_e_localizador(texto):
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    mensagem = str(excecao.value)
    assert mensagem.count(": ") == 1
    assert categoria_de(excecao) in CATEGORIAS
    assert localizador_de(excecao) in LOCALIZADORES


@pytest.mark.parametrize("texto", MENSAGENS_DE_FALHA)
def test_mensagem_nao_carrega_conteudo_token_nem_posicao(texto):
    with pytest.raises(TextoEmitivelInvalido) as excecao:
        extrair_textos_emitiveis(texto)
    mensagem = str(excecao.value)
    for proibido in (
        "R01",
        "R09",
        "F1",
        "F7",
        "/",
        "alfa",
        "colado",
        "conteudo",
        "comercial",
        ">",
        CR,
        TAB,
        "'",
        '"',
        "str",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
    ):
        assert proibido not in mensagem


def test_mapeamento_de_categoria_para_localizador_e_fechado():
    esperado = {
        "prefixo_invalido": "linha",
        "terminador_proibido": "linha",
        "branco_antes_do_terminador": "linha",
        "linha_vazia_invalida": "unidade",
    }
    observado = {}
    for texto in (
        doc("## R01", marcador("F1"), ">colado"),
        doc("## R01", marcador("F1"), "> alfa "),
        doc("## R01", marcador("F1"), ">", "> alfa"),
        "## R01" + LF + marcador("F1") + LF + "> alfa" + CR,
    ):
        with pytest.raises(TextoEmitivelInvalido) as excecao:
            extrair_textos_emitiveis(texto)
        observado[categoria_de(excecao)] = localizador_de(excecao)
    assert observado == esperado


def test_excecao_publica_e_subclasse_direta_de_exception():
    assert TextoEmitivelInvalido.__bases__ == (Exception,)
    assert not issubclass(TextoEmitivelInvalido, RepresentacaoMarcadaInvalida)
    assert not issubclass(RepresentacaoMarcadaInvalida, TextoEmitivelInvalido)


# ---------------------------------------------------------------------------
# Delegacao integral a `C8`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entrada",
    [None, 0, 1, b"", b"## R01", [], (), {}, object(), 1.0, True],
)
def test_nao_str_e_recusado_por_c8(entrada):
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_textos_emitiveis(entrada)
    assert str(excecao.value) == "tipo_invalido: texto"


@pytest.mark.parametrize("subclasse", [TextoSimples, TextoPermissivo])
def test_subclasse_de_str_e_recusada_por_c8(subclasse):
    texto = subclasse(doc("## R01", marcador("F1"), "> alfa"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "tipo_invalido: texto"


ESTRUTURAIS = (
    ("bloco_sem_marcador: bloco", doc("## R01", "> sem marcador antes")),
    ("marcador_sem_bloco: marcador", doc("## R01", marcador("F1"), "sem bloco")),
    ("marcador_sem_bloco: marcador", sem_newline("## R01", marcador("F1"))),
    ("marcador_fora_de_secao: marcador", doc("# Doc", marcador("F1"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc("## R01", marcador("F0"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc("## R01", marcador("F01"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc("## R01", marcador("f1"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc("## R01", marcador(""), "> alfa")),
    (
        "id_duplicado: marcador",
        doc("## R01", marcador("F1"), "> alfa", marcador("F1"), "> beta"),
    ),
    ("secao_sem_unidade: secao", doc("## R01", "texto sem unidade", "# Fim")),
)


@pytest.mark.parametrize("mensagem, texto", ESTRUTURAIS)
def test_falha_estrutural_continua_de_c8(mensagem, texto):
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == mensagem


@pytest.mark.parametrize("mensagem, texto", ESTRUTURAIS)
def test_excecao_estrutural_e_identica_a_de_c8(mensagem, texto):
    with pytest.raises(RepresentacaoMarcadaInvalida) as pelo_c8:
        ler_unidades_marcadas(texto)
    with pytest.raises(RepresentacaoMarcadaInvalida) as pelo_c11:
        extrair_textos_emitiveis(texto)
    assert type(pelo_c11.value) is type(pelo_c8.value)
    assert str(pelo_c11.value) == str(pelo_c8.value)


@pytest.mark.parametrize("mensagem, texto", ESTRUTURAIS)
def test_excecao_estrutural_sobe_sem_cause_nem_context(mensagem, texto):
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_textos_emitiveis(texto)
    assert excecao.value.__cause__ is None
    assert excecao.value.__context__ is None
    assert excecao.value.__suppress_context__ is False


def test_nao_str_sobe_sem_cause_nem_context():
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_textos_emitiveis(None)
    assert excecao.value.__cause__ is None
    assert excecao.value.__context__ is None


def test_falha_estrutural_posterior_vence_violacao_textual_anterior():
    # Decisao tecnica de **composicao**, nao norma nova de `C`: o portao `C8` e
    # integral e anterior, entao ele julga o documento inteiro antes de `C11`
    # olhar uma unica linha.
    texto = doc(
        "## R01",
        marcador("F1"),
        ">colado",
        "## R02",
        marcador("F1"),
        "sem bloco",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_textos_emitiveis(texto)
    assert str(excecao.value) == "marcador_sem_bloco: marcador"


def test_producao_nao_captura_a_excecao_de_c8():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_producao_nao_menciona_a_excecao_estrutural():
    assert "RepresentacaoMarcadaInvalida" not in NOMES_PRODUCAO


def test_producao_chama_o_leitor_antes_de_qualquer_outra_coisa():
    funcao = next(
        no
        for no in ARVORE_PRODUCAO.body
        if isinstance(no, ast.FunctionDef) and no.name == "extrair_textos_emitiveis"
    )
    corpo = [no for no in funcao.body if not isinstance(no, ast.Expr)]
    primeira = corpo[0]
    assert isinstance(primeira, ast.Assign)
    assert isinstance(primeira.value, ast.Call)
    assert isinstance(primeira.value.func, ast.Name)
    assert primeira.value.func.id == "ler_unidades_marcadas"


# ---------------------------------------------------------------------------
# Invariante `C8` <-> `C11`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("texto", DOCUMENTOS_VALIDOS)
def test_invariante_com_documentos_validos_em_lf(texto):
    assert tuple(
        token for token, _ in extrair_textos_emitiveis(texto)
    ) == ler_unidades_marcadas(texto)


@pytest.mark.parametrize("texto", DOCUMENTOS_VALIDOS_CRLF)
def test_invariante_com_documentos_validos_em_crlf(texto):
    assert tuple(
        token for token, _ in extrair_textos_emitiveis(texto)
    ) == ler_unidades_marcadas(texto)


DOCUMENTOS_VALIDOS_SEM_NEWLINE: tuple[str, ...] = tuple(
    texto[:-1] if texto.endswith(LF) else texto for texto in DOCUMENTOS_VALIDOS
)


@pytest.mark.parametrize("texto", DOCUMENTOS_VALIDOS_SEM_NEWLINE)
def test_invariante_com_documentos_validos_sem_newline_final(texto):
    assert tuple(
        token for token, _ in extrair_textos_emitiveis(texto)
    ) == ler_unidades_marcadas(texto)


def test_invariante_com_documento_misto():
    assert tuple(
        token for token, _ in extrair_textos_emitiveis(DOCUMENTO_MISTO)
    ) == ler_unidades_marcadas(DOCUMENTO_MISTO)


def test_invariante_cobre_secoes_homonimas():
    texto = doc(
        "## R01", marcador("F1"), "> alfa", "## R01", marcador("F1"), "> beta"
    )
    localizados = tuple(token for token, _ in extrair_textos_emitiveis(texto))
    assert localizados == ler_unidades_marcadas(texto)
    assert len(localizados) == 2


def test_token_nao_e_derivado_por_zip_nem_por_posicao():
    # O token vem de uma `f-string` sobre o `Rxx` e o `id` **declarados**
    # (`C-A5-I5`); nenhuma relacao e montada por `zip` ou por indice.
    assert "zip" not in NOMES_PRODUCAO
    assert "index" not in NOMES_PRODUCAO
    assert [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.JoinedStr)]


def test_producao_acumula_os_tokens_separadamente():
    anotados = {
        no.target.id
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.AnnAssign) and isinstance(no.target, ast.Name)
    }
    assert "tokens_localizados" in anotados
    assert "pares" in anotados


def test_guard_do_invariante_levanta_runtime_error(monkeypatch):
    texto = doc("## R01", marcador("F1"), "> alfa")

    def divergente(_texto):
        return ("R99/F9",)

    monkeypatch.setattr(
        "casa77_sdr.response_emittable_text.ler_unidades_marcadas", divergente
    )
    with pytest.raises(RuntimeError) as excecao:
        extrair_textos_emitiveis(texto)
    assert type(excecao.value) is RuntimeError
    assert str(excecao.value) == "invariante_estrutural"


def test_guard_do_invariante_e_mudo(monkeypatch):
    texto = doc("## R01", marcador("F1"), "> conteudo sensivel")

    def divergente(_texto):
        return ()

    monkeypatch.setattr(
        "casa77_sdr.response_emittable_text.ler_unidades_marcadas", divergente
    )
    with pytest.raises(RuntimeError) as excecao:
        extrair_textos_emitiveis(texto)
    mensagem = str(excecao.value)
    assert mensagem == "invariante_estrutural"
    for proibido in ("R01", "F1", "/", "conteudo", "sensivel", "0", "1", ">"):
        assert proibido not in mensagem


def test_guard_do_invariante_nao_e_textoemitivelinvalido(monkeypatch):
    texto = doc("## R01", marcador("F1"), "> alfa")

    def divergente(_texto):
        return ("R01/F1", "R01/F2")

    monkeypatch.setattr(
        "casa77_sdr.response_emittable_text.ler_unidades_marcadas", divergente
    )
    with pytest.raises(RuntimeError) as excecao:
        extrair_textos_emitiveis(texto)
    assert not isinstance(excecao.value, TextoEmitivelInvalido)


def test_producao_nao_usa_assert():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, ast.Assert)


# ---------------------------------------------------------------------------
# Contrato negativo — assinatura, `__all__` e pureza
# ---------------------------------------------------------------------------


def test_all_do_modulo_e_fechado():
    from casa77_sdr import response_emittable_text

    assert response_emittable_text.__all__ == [
        "TextoEmitivelInvalido",
        "extrair_textos_emitiveis",
    ]


def test_assinatura_publica_e_exata():
    import inspect

    assinatura = inspect.signature(extrair_textos_emitiveis)
    assert list(assinatura.parameters) == ["texto"]
    parametro = assinatura.parameters["texto"]
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parametro.default is inspect.Parameter.empty


def test_nao_e_exportado_pelo_package_root():
    import casa77_sdr

    assert not hasattr(casa77_sdr, "extrair_textos_emitiveis")
    assert not hasattr(casa77_sdr, "TextoEmitivelInvalido")


def test_modulo_nao_cria_dto_nem_dataclass():
    classes = [
        no.name for no in ARVORE_PRODUCAO.body if isinstance(no, ast.ClassDef)
    ]
    assert classes == ["TextoEmitivelInvalido"]
    assert "dataclass" not in NOMES_PRODUCAO
    assert "NamedTuple" not in NOMES_PRODUCAO
    assert "TypedDict" not in NOMES_PRODUCAO


def test_imports_sao_apenas_future_e_o_leitor():
    importados = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_modulo = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert importados == []
    assert [no.module for no in de_modulo] == [
        "__future__",
        "casa77_sdr.response_markdown_units",
    ]
    nomes = [alias.name for no in de_modulo for alias in no.names]
    assert nomes == ["annotations", "ler_unidades_marcadas"]


def test_nao_importa_equivalencia_nem_correspondencia():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.ImportFrom):
            modulo = no.module or ""
            assert "response_equivalence" not in modulo
            assert "response_correspondence" not in modulo
            assert "response_bijection" not in modulo
            assert "response_index_tokens" not in modulo
    assert "response_equivalence" not in CODIGO_PRODUCAO
    assert "response_correspondence" not in CODIGO_PRODUCAO


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_nao_ha_io_nem_filesystem():
    proibidos = {
        "open",
        "read",
        "read_text",
        "read_bytes",
        "write",
        "write_text",
        "write_bytes",
        "Path",
        "pathlib",
        "os",
        "io",
        "sys",
        "stdin",
        "stdout",
        "stderr",
        "input",
        "print",
        "glob",
        "listdir",
        "shutil",
        "tempfile",
        "StringIO",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_nem_parser():
    proibidos = {
        "splitlines",
        "strip",
        "lstrip",
        "rstrip",
        "casefold",
        "lower",
        "upper",
        "normalize",
        "unicodedata",
        "re",
        "compile",
        "match",
        "search",
        "sub",
        "fullmatch",
        "markdown",
        "commonmark",
        "expandtabs",
        "translate",
        "encode",
        "decode",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_rede_relogio_ambiente_nem_estado():
    proibidos = {
        "requests",
        "urllib",
        "httpx",
        "socket",
        "yaml",
        "safe_load",
        "json",
        "sqlite3",
        "datetime",
        "now",
        "today",
        "time",
        "locale",
        "getenv",
        "environ",
        "random",
        "uuid",
        "hashlib",
        "lru_cache",
        "cache",
        "global",
        "nonlocal",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_estado_mutavel_de_modulo():
    for no in ARVORE_PRODUCAO.body:
        if isinstance(no, ast.Assign):
            for alvo in no.targets:
                assert isinstance(alvo, ast.Name)
                if alvo.id == "__all__":
                    continue
                assert alvo.id.isupper() or alvo.id.startswith("_")
                assert isinstance(no.value, (ast.Constant, ast.Tuple))


def test_nao_ha_global_nem_nonlocal():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal))


def test_nao_ha_prints_nem_logging():
    assert "logging" not in NOMES_PRODUCAO
    assert "logger" not in NOMES_PRODUCAO


def test_modulo_nao_carrega_conteudo_comercial():
    # A citacao normativa do caminho do corpus e permitida — o leitor de `C8`
    # tambem a faz. O que nao pode existir aqui e **valor**, segredo ou dado
    # real: preco, capacidade, horario, contato, credencial ou fragmento
    # aprovado.
    minusculo = CODIGO_PRODUCAO.lower()
    for proibido in (
        "casa 77",
        "casa77.yaml",
        "r$",
        "whatsapp",
        "douglas",
        "@",
        "http://",
        "https://",
        "senha",
        "token=",
        ".env",
    ):
        assert proibido not in minusculo


def test_vizinhos_permanecem_com_a_api_conhecida():
    from casa77_sdr import response_correspondence, response_markdown_units

    assert response_markdown_units.__all__ == [
        "RepresentacaoMarcadaInvalida",
        "ler_unidades_marcadas",
    ]
    assert response_correspondence.__all__ == ["validar_correspondencia_canonica"]


def test_equivalencia_permanece_intacta_e_nao_e_tocada():
    from casa77_sdr import response_equivalence

    assert "extrair_textos_emitiveis" not in dir(response_equivalence)
    assert "TextoEmitivelInvalido" not in dir(response_equivalence)
