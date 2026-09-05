"""Testes da extração determinística do rótulo literal de status de `Rxx`.

A fronteira localiza cada cabeçalho `## Rxx` **já aceito** pelo portão
estrutural `C8` e aplica a gramática física `G2` — `## Rxx — <titulo> —
<rotulo>` — devolvendo o par `(Rxx, rotulo_literal)` ou recusando
*fail-closed*. Estes testes provam o portão `C8` integral e anterior, a
**ausência** de invariante local × `C8`, as quatro categorias e os três
localizadores, a precedência local, a política estrutural de linha, a
preservação de seções homônimas, a extração literal de `PARCIAL`, a pureza do
módulo de produção e o determinismo — e **não** transformam em norma a
canonicalização, a propagação `SP1`–`SP7`, o mapeamento de `PARCIAL`, o índice
ou a bijeção física, que estão **fora** desta fronteira.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_header_labels import (
    CabecalhoRxxInvalido,
    extrair_rotulos_de_cabecalho,
)
from casa77_sdr.response_markdown_units import (
    RepresentacaoMarcadaInvalida,
    ler_unidades_marcadas,
)
from casa77_sdr.response_status import StatusNaoCanonicalizavel, canonicalizar_status

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent

CAMINHO_PRODUCAO = RAIZ / "src" / "casa77_sdr" / "response_header_labels.py"
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)

CATEGORIAS = (
    "separador_ausente",
    "cardinalidade_de_separador",
    "segmento_vazio",
    "branco_de_borda",
)
LOCALIZADORES = ("cabecalho", "titulo", "rotulo")

MENSAGENS = (
    "separador_ausente: cabecalho",
    "cardinalidade_de_separador: cabecalho",
    "segmento_vazio: titulo",
    "branco_de_borda: titulo",
    "segmento_vazio: rotulo",
    "branco_de_borda: rotulo",
)

LF = "\n"
CR = "\r"
TAB = "\t"
ESPACO = " "

# Separador literal de `G2`, nomeado por ponto de codigo.
EM_DASH = chr(0x2014)
SEP = ESPACO + EM_DASH + ESPACO

# Caracteres que **nao** sao o separador nem o espaco ASCII.
HIFEN = chr(0x002D)
EN_DASH = chr(0x2013)
FIGURE_DASH = chr(0x2012)
HORIZONTAL_BAR = chr(0x2015)
TWO_EM_DASH = chr(0x2E3A)
SMALL_EM_DASH = chr(0xFE58)
NBSP = chr(0x00A0)
LS = chr(0x2028)
PS = chr(0x2029)
NEL = chr(0x0085)
VT = chr(0x000B)
FF = chr(0x000C)

# Os quatro rotulos fisicos que `docs/07` registra como evidencia — apenas
# rotulos, sem conteudo comercial.
APROVADO = "APROVADO"
AGUARDA = "AGUARDA APROVA" + chr(0x00C7) + chr(0x00C3) + "O"
HANDOFF = "APROVADO com handoff obrigat" + chr(0x00F3) + "rio"
PARCIAL = "PARCIAL"


def marcador(identificador: str) -> str:
    """Linha de marcador com o envelope exato de `C-A5-I1`."""
    return f"<!-- fragmento: {identificador} -->"


def cab(rxx: str, titulo: str, rotulo: str) -> str:
    """Cabeçalho na forma `G2`, montado por concatenação literal."""
    return "## " + rxx + SEP + titulo + SEP + rotulo


def secao(cabecalho: str, *ids: str) -> tuple[str, ...]:
    """Cabeçalho seguido de uma unidade marcada por `id`, aceitável por `C8`."""
    linhas = [cabecalho]
    for identificador in ids or ("F1",):
        linhas.extend((marcador(identificador), "> alfa"))
    return tuple(linhas)


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


def _nomes_usados() -> set[str]:
    nomes: set[str] = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


NOMES_PRODUCAO = _nomes_usados()


def _funcao_publica() -> ast.FunctionDef:
    return next(
        no
        for no in ARVORE_PRODUCAO.body
        if isinstance(no, ast.FunctionDef) and no.name == "extrair_rotulos_de_cabecalho"
    )


# ---------------------------------------------------------------------------
# Documentos sinteticos validos, reutilizados pela politica de linha
# ---------------------------------------------------------------------------

UM_RXX = doc(*secao(cab("R01", "Titulo", APROVADO)))

VARIOS_RXX = doc(
    "# Corpus",
    *secao(cab("R01", "Primeiro", APROVADO)),
    *secao(cab("R02", "Segundo", AGUARDA), "F1", "F2"),
    "### Nota",
    *secao(cab("R03", "Terceiro", HANDOFF)),
    *secao(cab("R04", "Quarto", PARCIAL)),
    "# Fim",
    "> bloco fora de secao",
)

ESPERADO_VARIOS = (
    ("R01", APROVADO),
    ("R02", AGUARDA),
    ("R03", HANDOFF),
    ("R04", PARCIAL),
)

DOCUMENTOS_VALIDOS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("", ()),
    (LF, ()),
    (doc("texto solto sem cabecalho"), ()),
    (doc("## Assunto", "texto de secao nao Rxx"), ()),
    (doc("> bloco fora de secao"), ()),
    (UM_RXX, (("R01", APROVADO),)),
    (sem_newline(*secao(cab("R01", "Titulo", APROVADO))), (("R01", APROVADO),)),
    (VARIOS_RXX, ESPERADO_VARIOS),
    (
        doc(*secao(cab("R05", "A", APROVADO)), *secao(cab("R02", "B", PARCIAL))),
        (("R05", APROVADO), ("R02", PARCIAL)),
    ),
    (
        doc(*secao(cab("R01", "A", APROVADO)), *secao(cab("R01", "B", AGUARDA))),
        (("R01", APROVADO), ("R01", AGUARDA)),
    ),
    (
        doc("  ## R01 indentado", *secao(cab("R01", "A", APROVADO))),
        (("R01", APROVADO),),
    ),
)


# ---------------------------------------------------------------------------
# Sucesso — dominio, forma e ordem
# ---------------------------------------------------------------------------


def test_documento_vazio_devolve_tupla_vazia():
    assert extrair_rotulos_de_cabecalho("") == ()


def test_apenas_quebras_devolve_tupla_vazia():
    assert extrair_rotulos_de_cabecalho(LF) == ()
    assert extrair_rotulos_de_cabecalho(CR + LF) == ()


def test_documento_sem_rxx_devolve_tupla_vazia():
    texto = doc("# Documento", "## Assunto", "texto", "> bloco fora de secao")
    assert extrair_rotulos_de_cabecalho(texto) == ()


def test_um_rxx():
    assert extrair_rotulos_de_cabecalho(UM_RXX) == (("R01", APROVADO),)


def test_um_rxx_sem_newline_final():
    texto = sem_newline(*secao(cab("R01", "Titulo", APROVADO)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_multiplos_rxx_em_ordem_fisica():
    assert extrair_rotulos_de_cabecalho(VARIOS_RXX) == ESPERADO_VARIOS


def test_ordem_fisica_nao_crescente_e_preservada():
    texto = doc(
        *secao(cab("R09", "A", APROVADO)),
        *secao(cab("R03", "B", PARCIAL)),
        *secao(cab("R27", "C", AGUARDA)),
        *secao(cab("R01", "D", HANDOFF)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (
        ("R09", APROVADO),
        ("R03", PARCIAL),
        ("R27", AGUARDA),
        ("R01", HANDOFF),
    )


def test_titulo_nao_aparece_na_saida():
    texto = doc(*secao(cab("R01", "TituloSentinela", APROVADO)))
    resultado = extrair_rotulos_de_cabecalho(texto)
    assert resultado == (("R01", APROVADO),)
    assert "TituloSentinela" not in repr(resultado)


def test_um_par_por_cabecalho_e_nao_por_unidade():
    texto = doc(*secao(cab("R01", "Multi", APROVADO), "F1", "F2", "F3"))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


@pytest.mark.parametrize("rotulo", [APROVADO, AGUARDA, HANDOFF, PARCIAL])
def test_os_quatro_rotulos_fisicos_sao_devolvidos_literalmente(rotulo):
    texto = doc(*secao(cab("R01", "Titulo", rotulo)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", rotulo),)


def test_rotulo_devolvido_e_o_mesmo_objeto_de_conteudo_sem_conversao():
    texto = doc(*secao(cab("R01", "Titulo", HANDOFF)))
    ((_, rotulo),) = extrair_rotulos_de_cabecalho(texto)
    assert rotulo == HANDOFF
    assert type(rotulo) is str


@pytest.mark.parametrize(
    "rotulo",
    [
        "A B",
        "A  B",
        "A" + EM_DASH + "B",
        "A " + EM_DASH + "B",
        "A" + EM_DASH + " B",
        "A " + HIFEN + " B",
        "A " + EN_DASH + " B",
        "A" + NBSP + "B",
        NBSP + "A",
        "A" + NBSP,
        "A" + TAB + "B",
        "B" + EM_DASH,
        EM_DASH + "B",
        "x",
        "0",
        "#",
        ">",
        "<!-- fragmento: F1 -->",
    ],
)
def test_rotulo_literal_com_conteudo_interno_permitido(rotulo):
    texto = doc(*secao(cab("R01", "Titulo", rotulo)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", rotulo),)


@pytest.mark.parametrize(
    "titulo",
    [
        "Prazo" + EM_DASH + "limite",
        "A " + EM_DASH + "B",
        "A" + EM_DASH + " B",
        "A " + HIFEN + " B",
        "A " + EN_DASH + " B",
        "A " + FIGURE_DASH + " B",
        "A " + HORIZONTAL_BAR + " B",
        "A" + NBSP + EM_DASH + NBSP + "B",
        "A" + TAB + "B",
        "Titulo com varias palavras",
        "R01",
        "##",
        "0",
    ],
)
def test_titulo_com_caracteres_que_nao_formam_o_separador(titulo):
    texto = doc(*secao(cab("R01", titulo, APROVADO)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_rotulo_terminando_em_em_dash_sem_espaco_e_literal():
    # `B` + EM DASH nao forma o separador literal: falta o espaco final.
    texto = doc(*secao(cab("R01", "A", "B" + EM_DASH)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", "B" + EM_DASH),)


def test_cabecalho_nao_rxx_de_nivel_2_e_ignorado():
    texto = doc(
        "## Assunto" + SEP + "titulo" + SEP + "rotulo",
        *secao(cab("R01", "A", APROVADO)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_cabecalho_rxx_de_outro_nivel_nao_e_rxx():
    texto = doc(
        "# R01" + SEP + "titulo" + SEP + "rotulo",
        *secao(cab("R02", "A", APROVADO)),
        "### R03" + SEP + "titulo" + SEP + "rotulo",
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R02", APROVADO),)


def test_cabecalho_rxx_indentado_nao_e_rxx():
    texto = doc(
        "  ## R09" + SEP + "titulo" + SEP + "rotulo",
        *secao(cab("R01", "A", APROVADO)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_cabecalho_com_espaco_extra_antes_do_rxx_nao_e_rxx():
    texto = doc(
        "##  R09" + SEP + "titulo" + SEP + "rotulo",
        *secao(cab("R01", "A", APROVADO)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_rxx_seguido_de_nbsp_nao_e_rxx():
    texto = doc(
        "## R09" + NBSP + EM_DASH + " titulo" + SEP + "rotulo",
        *secao(cab("R01", "A", APROVADO)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_rxx_com_digito_nao_ascii_nao_e_rxx():
    # Digito arabe-indico: nao e digito ASCII para esta fronteira nem para `C8`.
    texto = doc(
        "## R" + chr(0x0660) + "1" + SEP + "titulo" + SEP + "rotulo",
        *secao(cab("R01", "A", APROVADO)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_linha_parecida_com_cabecalho_dentro_de_bloco_nao_e_cabecalho():
    texto = doc(
        cab("R01", "A", APROVADO),
        marcador("F1"),
        "> ## R02" + SEP + "titulo" + SEP + "rotulo",
    )
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


# ---------------------------------------------------------------------------
# Politica de linha — a estrutural de `C8`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("texto, esperado", DOCUMENTOS_VALIDOS)
def test_documento_em_lf(texto, esperado):
    assert extrair_rotulos_de_cabecalho(texto) == esperado


@pytest.mark.parametrize("texto, esperado", DOCUMENTOS_VALIDOS)
def test_documento_em_crlf_produz_o_mesmo(texto, esperado):
    assert extrair_rotulos_de_cabecalho(crlf(texto)) == esperado


def test_documento_misto_lf_e_crlf():
    texto = (
        cab("R01", "A", APROVADO)
        + CR
        + LF
        + marcador("F1")
        + LF
        + "> alfa"
        + CR
        + LF
        + cab("R02", "B", PARCIAL)
        + LF
        + marcador("F1")
        + CR
        + LF
        + "> beta"
        + LF
    )
    assert extrair_rotulos_de_cabecalho(texto) == (
        ("R01", APROVADO),
        ("R02", PARCIAL),
    )


def test_crlf_nao_deixa_cr_no_rotulo():
    ((_, rotulo),) = extrair_rotulos_de_cabecalho(crlf(UM_RXX))
    assert CR not in rotulo
    assert rotulo == APROVADO


def test_cr_residual_permanece_conteudo_literal_do_rotulo():
    # Dois `CR` antes do `LF`: a politica estrutural tira **um**; o outro e
    # conteudo da linha e, portanto, do rotulo. Nao ha normalizacao aqui.
    texto = cab("R01", "A", APROVADO) + CR + CR + LF + marcador("F1") + LF + "> alfa" + LF
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO + CR),)


@pytest.mark.parametrize("exotico", [LS, PS, NEL, VT, FF])
def test_terminador_exotico_e_conteudo_do_rotulo(exotico):
    texto = doc(*secao(cab("R01", "A", "B" + exotico + "C")))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", "B" + exotico + "C"),)


@pytest.mark.parametrize("exotico", [LS, PS, NEL, VT, FF])
def test_terminador_exotico_nao_divide_a_linha(exotico):
    # Se o exotico dividisse a linha, o cabecalho terminaria em `A` e o resto
    # viraria outra linha; nada disso acontece.
    texto = doc(*secao(cab("R01", "A" + exotico + "B", APROVADO)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


def test_nbsp_de_borda_no_rotulo_nao_e_branco_ascii():
    texto = doc(*secao(cab("R01", "A", NBSP + APROVADO + NBSP)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", NBSP + APROVADO + NBSP),)


def test_nbsp_de_borda_no_titulo_nao_e_branco_ascii():
    texto = doc(*secao(cab("R01", NBSP + "A" + NBSP, APROVADO)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", APROVADO),)


# ---------------------------------------------------------------------------
# Homonimos — dois cabecalhos fisicos, dois pares
# ---------------------------------------------------------------------------


def test_secoes_homonimas_devolvem_dois_pares():
    texto = doc(
        *secao(cab("R01", "Titulo A", APROVADO)),
        *secao(cab("R01", "Titulo B", APROVADO)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (
        ("R01", APROVADO),
        ("R01", APROVADO),
    )


def test_secoes_homonimas_com_rotulos_distintos_preservam_ambos_em_ordem():
    texto = doc(
        *secao(cab("R01", "A", PARCIAL)),
        *secao(cab("R02", "B", APROVADO)),
        *secao(cab("R01", "C", AGUARDA)),
    )
    assert extrair_rotulos_de_cabecalho(texto) == (
        ("R01", PARCIAL),
        ("R02", APROVADO),
        ("R01", AGUARDA),
    )


def test_homonimos_sao_aceitos_por_c8_e_por_esta_fronteira():
    texto = doc(*secao(cab("R01", "A", APROVADO)), *secao(cab("R01", "B", APROVADO)))
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F1")
    assert len(extrair_rotulos_de_cabecalho(texto)) == 2


def test_homonimos_nao_sao_deduplicados_nem_sobrescritos():
    texto = doc(*secao(cab("R01", "A", APROVADO)), *secao(cab("R01", "B", PARCIAL)))
    resultado = extrair_rotulos_de_cabecalho(texto)
    assert resultado == (("R01", APROVADO), ("R01", PARCIAL))
    assert len({rxx for rxx, _ in resultado}) == 1


# ---------------------------------------------------------------------------
# `PARCIAL` — extraido literalmente, nao resolvido
# ---------------------------------------------------------------------------


def test_parcial_e_devolvido_literalmente():
    texto = doc(*secao(cab("R01", "Titulo", PARCIAL)))
    assert extrair_rotulos_de_cabecalho(texto) == (("R01", PARCIAL),)


def test_parcial_nao_e_traduzido_nem_convertido():
    texto = doc(*secao(cab("R01", "Titulo", PARCIAL)))
    ((_, rotulo),) = extrair_rotulos_de_cabecalho(texto)
    assert rotulo == "PARCIAL"
    assert rotulo not in ("APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO")


def test_canonicalizar_status_continua_recusando_parcial():
    # Prova externa: a fronteira de canonicalizacao permanece como esta. O
    # modulo de producao desta entrega **nao** importa `response_status`.
    with pytest.raises(StatusNaoCanonicalizavel) as excecao:
        canonicalizar_status(PARCIAL)
    assert str(excecao.value) == "rotulo_nao_mapeado: rotulo"


def test_rotulo_fora_de_st1_st3_tambem_e_extraido_literalmente():
    # A gramatica nao decide pertenca a `ST1`-`ST3` (`GR2.10`).
    for rotulo in ("BLOQUEADO", "aprovado", "AGUARDA_APROVACAO", "qualquer coisa"):
        texto = doc(*secao(cab("R01", "Titulo", rotulo)))
        assert extrair_rotulos_de_cabecalho(texto) == (("R01", rotulo),)


# ---------------------------------------------------------------------------
# G2 fail-closed — separador ausente
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "linha",
    [
        "## R01",
        "## R01 ",
        "## R01 Titulo",
        "## R01 Titulo APROVADO",
        "## R01 " + HIFEN + " Titulo " + HIFEN + " APROVADO",
        "## R01 " + EN_DASH + " Titulo " + EN_DASH + " APROVADO",
        "## R01 " + FIGURE_DASH + " Titulo " + FIGURE_DASH + " APROVADO",
        "## R01 " + HORIZONTAL_BAR + " Titulo " + HORIZONTAL_BAR + " APROVADO",
        "## R01 " + TWO_EM_DASH + " Titulo " + TWO_EM_DASH + " APROVADO",
        "## R01 " + SMALL_EM_DASH + " Titulo " + SMALL_EM_DASH + " APROVADO",
        "## R01 " + HIFEN + HIFEN + " Titulo " + HIFEN + HIFEN + " APROVADO",
        "## R01 " + HIFEN + HIFEN + HIFEN + " Titulo " + HIFEN + HIFEN + HIFEN + " APROVADO",
        "## R01 " + NBSP + EM_DASH + NBSP + "Titulo" + NBSP + EM_DASH + NBSP + "APROVADO",
        "## R01 " + EM_DASH + "Titulo" + SEP + "APROVADO",
        "## R01 " + EM_DASH + TAB + "Titulo" + SEP + "APROVADO",
        "## R01  " + EM_DASH + " Titulo" + SEP + "APROVADO",
        "## R01 " + TAB + EM_DASH + " Titulo" + SEP + "APROVADO",
        "## R01 extra" + SEP + "Titulo" + SEP + "APROVADO",
        "## R01 Titulo" + SEP + "APROVADO",
        "## R01 Titulo" + SEP + "APROVADO" + SEP + "extra",
        "## R01 " + EM_DASH + "Titulo" + SEP + "APROVADO" + SEP + "extra",
    ],
)
def test_separador_ausente_na_posicao_imediata(linha):
    texto = doc(linha, marcador("F1"), "> alfa")
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "separador_ausente: cabecalho"


def test_separador_ausente_e_recusado_mesmo_com_cabecalho_valido_antes():
    texto = doc(
        *secao(cab("R01", "A", APROVADO)),
        "## R02 Titulo APROVADO",
        marcador("F1"),
        "> beta",
    )
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "separador_ausente: cabecalho"


def test_separador_ausente_sem_newline_final():
    texto = sem_newline("## R01", marcador("F1"), "> alfa")
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "separador_ausente: cabecalho"


def test_separador_ausente_com_crlf():
    texto = crlf(doc("## R01 Titulo APROVADO", marcador("F1"), "> alfa"))
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "separador_ausente: cabecalho"


# ---------------------------------------------------------------------------
# G2 fail-closed — cardinalidade de separador
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "linha",
    [
        "## R01" + SEP,
        "## R01" + SEP + "Titulo",
        "## R01" + SEP + "APROVADO",
        "## R01" + SEP + "Titulo " + EM_DASH,
        "## R01" + SEP + "Titulo " + HIFEN + " APROVADO",
        "## R01" + SEP + "Titulo " + EN_DASH + " APROVADO",
        "## R01" + SEP + "Titulo" + SEP + "APROVADO" + SEP,
        "## R01" + SEP + "Titulo" + SEP + "APROVADO" + SEP + "extra",
        "## R01" + SEP + "A" + SEP + "B" + SEP + "C" + SEP + "D",
        "## R01" + SEP + "A " + EM_DASH + SEP + "B",
        "## R01" + SEP + "A" + SEP + EM_DASH + " B",
        "## R01" + SEP + "A" + SEP + "B" + SEP,
        "## R01" + SEP + "Titulo " + EM_DASH + "APROVADO",
    ],
)
def test_cardinalidade_de_separador_diferente_de_dois(linha):
    texto = doc(linha, marcador("F1"), "> alfa")
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "cardinalidade_de_separador: cabecalho"


def test_ocorrencias_sobrepostas_contam_e_nao_sao_resolvidas_por_inferencia():
    # `A — — B` admite duas decomposicoes; nenhuma e escolhida.
    linha = "## R01" + SEP + "A" + SEP + EM_DASH + " B"
    texto = doc(linha, marcador("F1"), "> alfa")
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "cardinalidade_de_separador: cabecalho"


# ---------------------------------------------------------------------------
# G2 fail-closed — segmento vazio e branco de borda
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "linha",
    [
        "## R01" + SEP + SEP + "APROVADO",
        "## R01" + SEP + "" + SEP + "APROVADO",
        # Segunda ocorrencia sobreposta a primeira: nao ha texto entre elas.
        "## R01 " + EM_DASH + SEP + "APROVADO",
    ],
)
def test_titulo_vazio(linha):
    texto = doc(linha, marcador("F1"), "> alfa")
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "segmento_vazio: titulo"


@pytest.mark.parametrize(
    "titulo",
    [
        ESPACO + "Titulo",
        "Titulo" + ESPACO,
        ESPACO + "Titulo" + ESPACO,
        TAB + "Titulo",
        "Titulo" + TAB,
        TAB + "Titulo" + TAB,
        ESPACO,
        TAB,
        ESPACO + ESPACO,
        ESPACO + TAB,
    ],
)
def test_branco_de_borda_no_titulo(titulo):
    texto = doc(*secao(cab("R01", titulo, APROVADO)))
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "branco_de_borda: titulo"


def test_rotulo_vazio():
    texto = doc("## R01" + SEP + "Titulo" + SEP, marcador("F1"), "> alfa")
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "segmento_vazio: rotulo"


def test_rotulo_vazio_com_crlf():
    texto = crlf(doc("## R01" + SEP + "Titulo" + SEP, marcador("F1"), "> alfa"))
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "segmento_vazio: rotulo"


def test_rotulo_vazio_sem_newline_final():
    texto = sem_newline("## R01" + SEP + "Titulo" + SEP, marcador("F1"), "> alfa")
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "segmento_vazio: rotulo"


@pytest.mark.parametrize(
    "rotulo",
    [
        ESPACO + APROVADO,
        APROVADO + ESPACO,
        ESPACO + APROVADO + ESPACO,
        TAB + APROVADO,
        APROVADO + TAB,
        TAB + APROVADO + TAB,
        ESPACO,
        TAB,
        ESPACO + ESPACO,
        TAB + ESPACO,
        PARCIAL + ESPACO,
        HANDOFF + ESPACO,
    ],
)
def test_branco_de_borda_no_rotulo(rotulo):
    texto = doc(*secao(cab("R01", "Titulo", rotulo)))
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "branco_de_borda: rotulo"


def test_espaco_terminal_antes_de_crlf_e_branco_de_borda():
    texto = crlf(doc(*secao(cab("R01", "Titulo", APROVADO + ESPACO))))
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "branco_de_borda: rotulo"


def test_espacamento_divergente_nao_e_corrigido():
    # `GR2.8`/`GR2.9`: nenhuma das variantes e aceita; todas sao recusadas.
    variantes = (
        "## R01" + SEP + "Titulo " + SEP + "APROVADO",
        "## R01" + SEP + " Titulo" + SEP + "APROVADO",
        "## R01" + SEP + "Titulo" + SEP + " APROVADO",
        "## R01" + SEP + "Titulo" + SEP + "APROVADO ",
        "## R01" + SEP + "Titulo" + SEP + "APROVADO" + TAB,
    )
    for linha in variantes:
        with pytest.raises(CabecalhoRxxInvalido):
            extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))


# ---------------------------------------------------------------------------
# Precedencia local — primeira violacao, em ordem fixa
# ---------------------------------------------------------------------------


def test_separador_ausente_vence_cardinalidade():
    linha = "## R01 Titulo" + SEP + "A" + SEP + "B" + SEP + "C"
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert str(excecao.value) == "separador_ausente: cabecalho"


def test_cardinalidade_vence_segmento_vazio():
    linha = "## R01" + SEP + SEP + SEP
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert str(excecao.value) == "cardinalidade_de_separador: cabecalho"


def test_titulo_vazio_vence_rotulo_vazio():
    linha = "## R01" + SEP + SEP
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert str(excecao.value) == "segmento_vazio: titulo"


def test_titulo_vazio_vence_branco_no_rotulo():
    linha = "## R01" + SEP + SEP + " " + APROVADO
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert str(excecao.value) == "segmento_vazio: titulo"


def test_branco_no_titulo_vence_rotulo_vazio():
    linha = "## R01" + SEP + " Titulo" + SEP
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert str(excecao.value) == "branco_de_borda: titulo"


def test_branco_no_titulo_vence_branco_no_rotulo():
    texto = doc(*secao(cab("R01", "Titulo ", " " + APROVADO)))
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "branco_de_borda: titulo"


def test_rotulo_vazio_vence_nada_alem_de_si():
    linha = "## R01" + SEP + "Titulo" + SEP
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert str(excecao.value) == "segmento_vazio: rotulo"


def test_primeiro_cabecalho_invalido_encerra_sem_devolver_nada():
    texto = doc(
        "## R01 Titulo APROVADO",
        marcador("F1"),
        "> alfa",
        *secao(cab("R02", "B", APROVADO)),
    )
    with pytest.raises(CabecalhoRxxInvalido):
        extrair_rotulos_de_cabecalho(texto)


def test_cabecalho_posterior_invalido_encerra_sem_devolver_o_anterior():
    texto = doc(
        *secao(cab("R01", "A", APROVADO)),
        *secao(cab("R02", "B", APROVADO)),
        "## R03" + SEP + "C" + SEP,
        marcador("F1"),
        "> gama",
    )
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "segmento_vazio: rotulo"


def test_a_primeira_violacao_em_ordem_fisica_vence_a_segunda():
    texto = doc(
        "## R01" + SEP + "Titulo" + SEP,
        marcador("F1"),
        "> alfa",
        "## R02 Titulo APROVADO",
        marcador("F1"),
        "> beta",
    )
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "segmento_vazio: rotulo"


# ---------------------------------------------------------------------------
# Mensagem — forma fechada e sem vazamento
# ---------------------------------------------------------------------------

LINHAS_INVALIDAS = (
    ("separador_ausente: cabecalho", "## R47 TituloSentinela RotuloSentinela"),
    (
        "cardinalidade_de_separador: cabecalho",
        "## R47" + SEP + "TituloSentinela" + SEP + "RotuloSentinela" + SEP + "X",
    ),
    ("segmento_vazio: titulo", "## R47" + SEP + SEP + "RotuloSentinela"),
    (
        "branco_de_borda: titulo",
        "## R47" + SEP + " TituloSentinela" + SEP + "RotuloSentinela",
    ),
    ("segmento_vazio: rotulo", "## R47" + SEP + "TituloSentinela" + SEP),
    (
        "branco_de_borda: rotulo",
        "## R47" + SEP + "TituloSentinela" + SEP + "RotuloSentinela" + TAB,
    ),
)


@pytest.mark.parametrize("mensagem, linha", LINHAS_INVALIDAS)
def test_mensagem_tem_apenas_categoria_e_localizador(mensagem, linha):
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert str(excecao.value) == mensagem
    assert categoria_de(excecao) in CATEGORIAS
    assert localizador_de(excecao) in LOCALIZADORES
    assert excecao.value.args == (mensagem,)


@pytest.mark.parametrize("mensagem, linha", LINHAS_INVALIDAS)
def test_mensagem_nao_carrega_rxx_titulo_rotulo_nem_posicao(mensagem, linha):
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    texto = str(excecao.value)
    assert "R47" not in texto
    assert "TituloSentinela" not in texto
    assert "RotuloSentinela" not in texto
    assert EM_DASH not in texto
    assert "#" not in texto
    assert TAB not in texto
    assert "'" not in texto
    assert '"' not in texto
    assert "<" not in texto
    assert "str" not in texto
    assert not any(caractere.isdigit() for caractere in texto)


def test_as_seis_mensagens_sao_alcancaveis_e_fechadas():
    observadas = set()
    for _, linha in LINHAS_INVALIDAS:
        with pytest.raises(CabecalhoRxxInvalido) as excecao:
            extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
        observadas.add(str(excecao.value))
    assert observadas == set(MENSAGENS)


def test_mapeamento_de_categoria_para_localizador_e_fechado():
    esperado = {
        "separador_ausente": {"cabecalho"},
        "cardinalidade_de_separador": {"cabecalho"},
        "segmento_vazio": {"titulo", "rotulo"},
        "branco_de_borda": {"titulo", "rotulo"},
    }
    observado: dict[str, set[str]] = {}
    for _, linha in LINHAS_INVALIDAS:
        with pytest.raises(CabecalhoRxxInvalido) as excecao:
            extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
        observado.setdefault(categoria_de(excecao), set()).add(localizador_de(excecao))
    assert observado == esperado


@pytest.mark.parametrize("mensagem, linha", LINHAS_INVALIDAS)
def test_excecao_g2_nao_tem_cause_nem_context(mensagem, linha):
    with pytest.raises(CabecalhoRxxInvalido) as excecao:
        extrair_rotulos_de_cabecalho(doc(linha, marcador("F1"), "> alfa"))
    assert excecao.value.__cause__ is None
    assert excecao.value.__context__ is None


def test_excecao_publica_e_subclasse_direta_de_exception():
    assert CabecalhoRxxInvalido.__bases__ == (Exception,)
    assert not issubclass(CabecalhoRxxInvalido, RepresentacaoMarcadaInvalida)
    assert not issubclass(RepresentacaoMarcadaInvalida, CabecalhoRxxInvalido)
    assert not issubclass(CabecalhoRxxInvalido, StatusNaoCanonicalizavel)


# ---------------------------------------------------------------------------
# Gate `C8` — delegacao integral, sem invariante
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entrada",
    [None, 0, 1, b"", b"## R01", [], (), {}, object(), 1.0, True, ["## R01"]],
)
def test_nao_str_e_recusado_por_c8(entrada):
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(entrada)
    assert str(excecao.value) == "tipo_invalido: texto"


@pytest.mark.parametrize("subclasse", [TextoSimples, TextoPermissivo])
def test_subclasse_de_str_e_recusada_por_c8(subclasse):
    texto = subclasse(UM_RXX)
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "tipo_invalido: texto"


def test_subclasse_de_str_e_recusada_mesmo_com_conteudo_g2_invalido():
    # O tipo pertence a `C8` e vence qualquer coisa que `G2` diria.
    texto = TextoSimples(doc("## R01 Titulo APROVADO", marcador("F1"), "> alfa"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "tipo_invalido: texto"


ESTRUTURAIS = (
    ("bloco_sem_marcador: bloco", doc(cab("R01", "A", APROVADO), "> sem marcador")),
    (
        "marcador_sem_bloco: marcador",
        doc(cab("R01", "A", APROVADO), marcador("F1"), "sem bloco"),
    ),
    ("marcador_sem_bloco: marcador", sem_newline(cab("R01", "A", APROVADO), marcador("F1"))),
    ("marcador_fora_de_secao: marcador", doc("# Doc", marcador("F1"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc(cab("R01", "A", APROVADO), marcador("F0"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc(cab("R01", "A", APROVADO), marcador("F01"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc(cab("R01", "A", APROVADO), marcador("f1"), "> alfa")),
    ("id_fora_da_gramatica: marcador", doc(cab("R01", "A", APROVADO), marcador(""), "> alfa")),
    (
        "id_duplicado: marcador",
        doc(cab("R01", "A", APROVADO), marcador("F1"), "> alfa", marcador("F1"), "> beta"),
    ),
    ("secao_sem_unidade: secao", doc(cab("R01", "A", APROVADO), "texto sem unidade", "# Fim")),
    ("secao_sem_unidade: secao", doc(cab("R01", "A", APROVADO))),
    ("secao_sem_unidade: secao", doc("## R01")),
    ("secao_sem_unidade: secao", doc("## R01 Titulo APROVADO")),
)


@pytest.mark.parametrize("mensagem, texto", ESTRUTURAIS)
def test_falha_estrutural_continua_de_c8(mensagem, texto):
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == mensagem


@pytest.mark.parametrize("mensagem, texto", ESTRUTURAIS)
def test_excecao_estrutural_e_identica_a_de_c8(mensagem, texto):
    with pytest.raises(RepresentacaoMarcadaInvalida) as pelo_c8:
        ler_unidades_marcadas(texto)
    with pytest.raises(RepresentacaoMarcadaInvalida) as pelo_c12:
        extrair_rotulos_de_cabecalho(texto)
    assert type(pelo_c12.value) is type(pelo_c8.value)
    assert str(pelo_c12.value) == str(pelo_c8.value)
    assert pelo_c12.value.args == pelo_c8.value.args


@pytest.mark.parametrize("mensagem, texto", ESTRUTURAIS)
def test_excecao_estrutural_sobe_sem_cause_nem_context(mensagem, texto):
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert excecao.value.__cause__ is None
    assert excecao.value.__context__ is None
    assert excecao.value.__suppress_context__ is False


def test_nao_str_sobe_sem_cause_nem_context():
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(None)
    assert excecao.value.__cause__ is None
    assert excecao.value.__context__ is None


def test_falha_estrutural_posterior_vence_violacao_g2_anterior():
    # Decisao tecnica de composicao: o portao `C8` e integral e anterior, entao
    # ele julga o documento inteiro antes de `G2` olhar um unico cabecalho.
    texto = doc(
        "## R01 Titulo APROVADO",
        marcador("F1"),
        "> alfa",
        cab("R02", "B", APROVADO),
        marcador("F1"),
        "sem bloco",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "marcador_sem_bloco: marcador"


def test_secao_sem_unidade_posterior_vence_g2_anterior():
    texto = doc(
        "## R01" + SEP + "Titulo" + SEP,
        marcador("F1"),
        "> alfa",
        cab("R02", "B", APROVADO),
        "texto sem unidade",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as excecao:
        extrair_rotulos_de_cabecalho(texto)
    assert str(excecao.value) == "secao_sem_unidade: secao"


def test_g2_so_e_avaliada_em_documento_estruturalmente_aceito():
    # Um cabecalho `G2`-invalido em documento que `C8` recusa nunca chega a
    # `CabecalhoRxxInvalido`.
    texto = doc("## R01 Titulo APROVADO")
    with pytest.raises(RepresentacaoMarcadaInvalida):
        extrair_rotulos_de_cabecalho(texto)


def test_producao_nao_captura_a_excecao_de_c8():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.TryStar, ast.ExceptHandler))


def test_producao_nao_menciona_a_excecao_estrutural():
    assert "RepresentacaoMarcadaInvalida" not in NOMES_PRODUCAO


def test_producao_nao_usa_raise_from():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise):
            assert no.cause is None


def test_producao_chama_o_leitor_antes_de_qualquer_outra_coisa():
    corpo = [
        no
        for no in _funcao_publica().body
        if not (
            isinstance(no, ast.Expr)
            and isinstance(no.value, ast.Constant)
            and isinstance(no.value.value, str)
        )
    ]
    primeira = corpo[0]
    assert isinstance(primeira, ast.Expr)
    assert isinstance(primeira.value, ast.Call)
    assert isinstance(primeira.value.func, ast.Name)
    assert primeira.value.func.id == "ler_unidades_marcadas"
    assert [ast.unparse(argumento) for argumento in primeira.value.args] == ["texto"]


def test_producao_nao_guarda_o_resultado_de_c8():
    # Zero invariante local x `C8`: a chamada e uma expressao solta, nunca o
    # valor de um `Assign`, `AnnAssign`, `NamedExpr`, `Return` ou argumento.
    chamadas = [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Call)
        and isinstance(no.func, ast.Name)
        and no.func.id == "ler_unidades_marcadas"
    ]
    assert len(chamadas) == 1
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.Assign, ast.AnnAssign, ast.NamedExpr, ast.Return)):
            valor = no.value
            assert not (
                isinstance(valor, ast.Call)
                and isinstance(valor.func, ast.Name)
                and valor.func.id == "ler_unidades_marcadas"
            )


def test_producao_nao_compara_conjuntos_contagens_nem_tokens():
    assert "set" not in NOMES_PRODUCAO
    assert "frozenset" not in NOMES_PRODUCAO
    assert "Counter" not in NOMES_PRODUCAO
    assert "collections" not in NOMES_PRODUCAO
    assert "sorted" not in NOMES_PRODUCAO
    assert "zip" not in NOMES_PRODUCAO
    assert "tokens" not in NOMES_PRODUCAO
    assert "tokens_c8" not in NOMES_PRODUCAO
    assert "RuntimeError" not in NOMES_PRODUCAO
    assert "invariante_estrutural" not in CODIGO_PRODUCAO
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Compare):
            # Nenhuma comparacao envolve o que `C8` devolve: nao ha nome para
            # isso no modulo, e nenhuma tupla de tokens e comparada.
            assert "ler_unidades_marcadas" not in ast.unparse(no)


def test_producao_nao_levanta_runtime_error():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise) and no.exc is not None:
            assert "RuntimeError" not in ast.unparse(no.exc)


def test_producao_nao_deriva_o_token_canonico():
    # `<Rxx>/<id>` e assunto de `C8`; aqui nao ha barra, `id` nem envelope.
    assert "/" not in [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    ]
    assert "fragmento" not in NOMES_PRODUCAO
    assert "_envelope" not in NOMES_PRODUCAO
    assert "_id_conforme" not in NOMES_PRODUCAO


# ---------------------------------------------------------------------------
# Determinismo e ausencia de efeito
# ---------------------------------------------------------------------------


def test_saida_e_deterministica():
    assert extrair_rotulos_de_cabecalho(VARIOS_RXX) == extrair_rotulos_de_cabecalho(
        VARIOS_RXX
    )


def test_ordem_das_chamadas_nao_altera_o_resultado():
    primeiro = extrair_rotulos_de_cabecalho(UM_RXX)
    with pytest.raises(CabecalhoRxxInvalido):
        extrair_rotulos_de_cabecalho(doc("## R01 x", marcador("F1"), "> alfa"))
    with pytest.raises(RepresentacaoMarcadaInvalida):
        extrair_rotulos_de_cabecalho(None)
    assert extrair_rotulos_de_cabecalho(UM_RXX) == primeiro


def test_entrada_nao_e_alterada():
    copia = str(VARIOS_RXX)
    extrair_rotulos_de_cabecalho(VARIOS_RXX)
    assert VARIOS_RXX == copia


def test_retorno_e_tupla_de_pares_de_str_exata():
    resultado = extrair_rotulos_de_cabecalho(VARIOS_RXX)
    assert type(resultado) is tuple
    for par in resultado:
        assert type(par) is tuple
        assert len(par) == 2
        rxx, rotulo = par
        assert type(rxx) is str
        assert type(rotulo) is str
        assert len(rxx) == 3
        assert rxx[0] == "R"
        assert rxx[1:].isdigit()


def test_retorno_vazio_e_tupla_e_nao_dict():
    resultado = extrair_rotulos_de_cabecalho("")
    assert resultado == ()
    assert type(resultado) is tuple


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("CASA77_HEADER_LABELS", "1")
    monkeypatch.setenv("LANG", "C")
    assert extrair_rotulos_de_cabecalho(VARIOS_RXX) == ESPERADO_VARIOS


# ---------------------------------------------------------------------------
# Contrato negativo — assinatura, `__all__` e pureza
# ---------------------------------------------------------------------------


def test_all_do_modulo_e_exato():
    from casa77_sdr import response_header_labels

    assert response_header_labels.__all__ == [
        "CabecalhoRxxInvalido",
        "extrair_rotulos_de_cabecalho",
    ]


def test_nao_ha_nome_publico_fora_de_all():
    from casa77_sdr import response_header_labels

    publicos = {
        nome
        for nome in dir(response_header_labels)
        if not nome.startswith("_") and nome not in ("annotations", "ler_unidades_marcadas")
    }
    assert publicos == set(response_header_labels.__all__)


def test_assinatura_publica_e_exata():
    assinatura = inspect.signature(extrair_rotulos_de_cabecalho)
    assert list(assinatura.parameters) == ["texto"]
    parametro = assinatura.parameters["texto"]
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parametro.default is inspect.Parameter.empty
    assert parametro.annotation == "str"
    assert assinatura.return_annotation == "tuple[tuple[str, str], ...]"


def test_nao_e_exportado_pelo_package_root():
    assert not hasattr(casa77_sdr, "extrair_rotulos_de_cabecalho")
    assert not hasattr(casa77_sdr, "CabecalhoRxxInvalido")
    assert "extrair_rotulos_de_cabecalho" not in casa77_sdr.__all__
    assert "CabecalhoRxxInvalido" not in casa77_sdr.__all__


def test_modulo_declara_uma_unica_classe_publica():
    classes = [no.name for no in ARVORE_PRODUCAO.body if isinstance(no, ast.ClassDef)]
    assert classes == ["CabecalhoRxxInvalido"]
    assert "dataclass" not in NOMES_PRODUCAO
    assert "NamedTuple" not in NOMES_PRODUCAO
    assert "TypedDict" not in NOMES_PRODUCAO
    assert "Enum" not in NOMES_PRODUCAO


def test_excecao_publica_tem_base_direta_exception_no_codigo():
    classe = next(no for no in ARVORE_PRODUCAO.body if isinstance(no, ast.ClassDef))
    assert [ast.unparse(base) for base in classe.bases] == ["Exception"]


def test_modulo_declara_uma_unica_funcao_publica():
    funcoes = [no.name for no in ARVORE_PRODUCAO.body if isinstance(no, ast.FunctionDef)]
    assert [nome for nome in funcoes if not nome.startswith("_")] == [
        "extrair_rotulos_de_cabecalho"
    ]


def test_imports_sao_apenas_future_e_o_leitor():
    importados = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_modulo = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)]
    assert importados == []
    assert [no.module for no in de_modulo] == [
        "__future__",
        "casa77_sdr.response_markdown_units",
    ]
    nomes = [alias.name for no in de_modulo for alias in no.names]
    assert nomes == ["annotations", "ler_unidades_marcadas"]


@pytest.mark.parametrize(
    "proibido",
    [
        "response_status",
        "response_emittable_text",
        "response_index",
        "response_index_tokens",
        "response_correspondence",
        "response_bijection",
        "response_equivalence",
        "canonicalizar_status",
        "extrair_textos_emitiveis",
    ],
)
def test_nao_importa_nem_menciona_fronteira_proibida(proibido):
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.ImportFrom):
            assert proibido not in (no.module or "")
            assert proibido not in [alias.name for alias in no.names]
    assert proibido not in NOMES_PRODUCAO
    assert proibido not in CODIGO_PRODUCAO


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
        "title",
        "capitalize",
        "swapcase",
        "normalize",
        "unicodedata",
        "re",
        "compile",
        "match",
        "search",
        "sub",
        "fullmatch",
        "findall",
        "finditer",
        "markdown",
        "commonmark",
        "expandtabs",
        "translate",
        "encode",
        "decode",
        "replace",
        "partition",
        "rpartition",
        "rsplit",
        "count",
        "find",
        "rfind",
        "index",
        "rindex",
        "isspace",
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
        "functools",
        "logging",
        "logger",
        "warnings",
        "eval",
        "exec",
        "__import__",
        "importlib",
        "getattr",
        "setattr",
        "globals",
        "locals",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_estado_mutavel_de_modulo():
    for no in ARVORE_PRODUCAO.body:
        if isinstance(no, ast.Assign):
            for alvo in no.targets:
                assert isinstance(alvo, ast.Name)
                if alvo.id == "__all__":
                    continue
                assert alvo.id.startswith("_")
                assert isinstance(no.value, (ast.Constant, ast.Tuple))
        assert not isinstance(no, (ast.AugAssign, ast.AnnAssign))


def test_nao_ha_global_nonlocal_assert_nem_dict():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal, ast.Assert))
        assert not isinstance(no, (ast.Dict, ast.DictComp, ast.SetComp, ast.Set))
    assert "dict" not in NOMES_PRODUCAO
    assert "defaultdict" not in NOMES_PRODUCAO
    assert "OrderedDict" not in NOMES_PRODUCAO


def test_retorno_em_codigo_e_tupla():
    retornos = [no for no in ast.walk(_funcao_publica()) if isinstance(no, ast.Return)]
    assert len(retornos) == 1
    assert ast.unparse(retornos[0].value) == "tuple(pares)"


def test_separador_de_producao_e_o_literal_de_tres_caracteres():
    from casa77_sdr import response_header_labels

    separador = response_header_labels._SEPARADOR
    assert separador == SEP
    assert len(separador) == 3
    assert [ord(caractere) for caractere in separador] == [0x20, 0x2014, 0x20]


def test_producao_nao_conhece_equivalentes_do_separador():
    constantes = [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    ]
    for equivalente in (HIFEN, EN_DASH, FIGURE_DASH, HORIZONTAL_BAR, TWO_EM_DASH, NBSP):
        assert all(equivalente not in constante for constante in constantes if len(constante) < 8)


def test_producao_nao_conhece_nenhum_rotulo_de_status():
    constantes = [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    ]
    curtas = [constante for constante in constantes if len(constante) < 60]
    for rotulo in (APROVADO, AGUARDA, HANDOFF, PARCIAL, "BLOQUEADO", "AGUARDA_APROVACAO"):
        assert rotulo not in curtas


def test_modulo_nao_carrega_conteudo_comercial_nem_caminho_de_knowledge():
    minusculo = CODIGO_PRODUCAO.lower()
    for proibido in (
        "knowledge",
        "casa 77",
        "casa77.yaml",
        "respostas-aprovadas",
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
    from casa77_sdr import (
        response_emittable_text,
        response_markdown_units,
        response_status,
    )

    assert response_markdown_units.__all__ == [
        "RepresentacaoMarcadaInvalida",
        "ler_unidades_marcadas",
    ]
    assert response_emittable_text.__all__ == [
        "TextoEmitivelInvalido",
        "extrair_textos_emitiveis",
    ]
    assert response_status.__all__ == ["StatusNaoCanonicalizavel", "canonicalizar_status"]


def test_vizinhos_nao_receberam_esta_api():
    from casa77_sdr import (
        response_emittable_text,
        response_markdown_units,
        response_status,
    )

    for modulo in (response_markdown_units, response_emittable_text, response_status):
        assert "extrair_rotulos_de_cabecalho" not in dir(modulo)
        assert "CabecalhoRxxInvalido" not in dir(modulo)
