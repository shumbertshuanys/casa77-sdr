"""Testes do leitor determinístico da representação marcada `C-A5`.

A fronteira lê **identidade** e nada mais: ela devolve os tokens `<Rxx>/<id>` de
`C-A5-T1` na ordem física do documento. Estes testes provam a política local de
linha (`LF`/`CRLF`), a delimitação parcial de seção, o envelope do marcador em
dois estágios, a gramática fechada do `id`, as **sete redações** de `C-A5-X1`
cobertas por **seis** categorias estruturais, a precedência fixa, o silêncio da
mensagem de erro, a pureza do módulo de produção, o determinismo e a
correspondência do corpus real com as **37** unidades humanamente aprovadas em
`C-A5-M5` — e **não** transformam em norma a extração de texto emitível, a
leitura de status, a unicidade global dos tokens, a prova histórica de
`C-A5-I6`, uma oitava falha, o índice real ou a bijeção física, que estão
**fora** desta fronteira.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_markdown_units import (
    RepresentacaoMarcadaInvalida,
    ler_unidades_marcadas,
)

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent

CAMINHO_PRODUCAO = RAIZ / "src" / "casa77_sdr" / "response_markdown_units.py"
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)

CAMINHO_CORPUS = RAIZ / "knowledge" / "respostas-aprovadas.md"

CATEGORIAS = (
    "tipo_invalido",
    "bloco_sem_marcador",
    "marcador_sem_bloco",
    "marcador_fora_de_secao",
    "id_fora_da_gramatica",
    "id_duplicado",
    "secao_sem_unidade",
)
LOCALIZADORES = ("texto", "bloco", "marcador", "secao")


def marcador(identificador: str) -> str:
    """Linha de marcador com o envelope exato de `C-A5-I1`."""
    return f"<!-- fragmento: {identificador} -->"


def doc(*linhas: str) -> str:
    """Documento sintético terminado em `LF`, como o corpus real."""
    return "\n".join(linhas) + "\n"


def crlf(texto: str) -> str:
    """Mesmo documento com terminação `CRLF`, sem tocar em mais nada."""
    return texto.replace("\n", "\r\n")


def categoria_de(excecao: pytest.ExceptionInfo) -> str:
    return str(excecao.value).split(":")[0]


class TextoPermissivo(str):
    """Subclasse de `str` que sequestra a igualdade e o hash.

    Ela se declara igual a qualquer coisa. Se a fronteira lesse o documento
    antes de conferir o tipo, esta subclasse decidiria sozinha o que o texto
    diz — exatamente o que a recusa por tipo exato impede.
    """

    def __eq__(self, outro: object) -> bool:
        return True

    def __ne__(self, outro: object) -> bool:
        return False

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


def _constantes_de_codigo() -> list[str]:
    """Constantes `str` do módulo que **não** são docstring."""
    return [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, str)
        and id(no) not in IDS_DOCSTRING
    ]


# ---------------------------------------------------------------------------
# Conjunto aprovado — transcricao do mapeamento humano `C-A5-M5`
#
# Esta constante e **transcricao** da tabela aprovada em
# `docs/07-arquitetura-motor-respostas.md`. Ela **nao** e construida lendo nem
# parseando o corpus: se o corpus divergir do mapeamento humano, o teste falha.
# ---------------------------------------------------------------------------

UNIDADES_APROVADAS = frozenset(
    {
        "R01/F1",
        "R02/F1",
        "R03/F1",
        "R04/F1",
        "R05/F1",
        "R05/F2",
        "R05/F3",
        "R06/F1",
        "R07/F1",
        "R08/F1",
        "R09/F1",
        "R09/F2",
        "R10/F1",
        "R11/F1",
        "R11/F2",
        "R12/F1",
        "R12/F2",
        "R13/F1",
        "R14/F1",
        "R15/F1",
        "R16/F1",
        "R17/F1",
        "R18/F1",
        "R19/F1",
        "R20/F1",
        "R21/F1",
        "R22/F1",
        "R23/F1",
        "R23/F2",
        "R24/F1",
        "R25/F1",
        "R25/F2",
        "R26/F1",
        "R27/F1",
        "R28/F1",
        "R29/F1",
        "R30/F1",
    }
)

TOTAL_APROVADO = 37


# ---------------------------------------------------------------------------
# A. Caminho feliz e ordem fisica
# ---------------------------------------------------------------------------


def test_secao_unica_com_uma_unidade():
    texto = doc("## R01 — titulo", "", marcador("F1"), "> corpo")
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_secao_com_varias_unidades():
    texto = doc(
        "## R05 — titulo",
        "prosa",
        marcador("F1"),
        "> corpo um",
        "> continuacao",
        "",
        "prosa",
        marcador("F2"),
        "> corpo dois",
        "",
        marcador("F3"),
        "> corpo tres",
    )
    assert ler_unidades_marcadas(texto) == ("R05/F1", "R05/F2", "R05/F3")


def test_varias_secoes_em_ordem_fisica():
    texto = doc(
        "## R02 — titulo",
        marcador("F1"),
        "> corpo",
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "## R03 — titulo",
        marcador("F2"),
        "> corpo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == (
        "R02/F1",
        "R01/F1",
        "R03/F2",
        "R03/F1",
    )


def test_a_ordem_e_a_do_documento_e_nao_a_alfabetica():
    texto = doc(
        "## R09 — titulo",
        marcador("F2"),
        "> corpo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R09/F2", "R09/F1")


def test_bloco_maximal_e_consumido_inteiro():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> linha um",
        "> linha dois",
        "> linha tres",
        "prosa",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_o_par_nao_e_processado_duas_vezes():
    texto = doc("## R01 — titulo", marcador("F1"), "> corpo", "> corpo")
    assert ler_unidades_marcadas(texto).count("R01/F1") == 1


def test_token_usa_a_barra_como_separador():
    texto = doc("## R07 — titulo", marcador("F10"), "> corpo")
    assert ler_unidades_marcadas(texto) == ("R07/F10",)


def test_saida_e_tupla_de_str_exata():
    texto = doc("## R01 — titulo", marcador("F1"), "> corpo")
    tokens = ler_unidades_marcadas(texto)
    assert type(tokens) is tuple
    for token in tokens:
        assert type(token) is str


# ---------------------------------------------------------------------------
# B. Documento vazio e sem `Rxx`
# ---------------------------------------------------------------------------


def test_texto_vazio_devolve_tupla_vazia():
    assert ler_unidades_marcadas("") == ()


def test_apenas_quebras_devolve_tupla_vazia():
    assert ler_unidades_marcadas("\n\n\n") == ()


def test_texto_sem_secao_rxx_devolve_tupla_vazia():
    texto = doc("# Titulo", "prosa", "## Apendice", "mais prosa")
    assert ler_unidades_marcadas(texto) == ()


def test_texto_sem_marcador_e_sem_bloco_devolve_tupla_vazia():
    assert ler_unidades_marcadas("prosa solta sem estrutura") == ()


# ---------------------------------------------------------------------------
# C. Contrato de entrada — `str` exata
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalido",
    [
        None,
        0,
        1,
        True,
        False,
        3.5,
        b"## R01 x",
        bytearray(b"## R01 x"),
        [],
        ["## R01 x"],
        (),
        {},
        set(),
        object(),
    ],
)
def test_tipo_invalido_e_recusado(invalido):
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(invalido)
    assert str(erro.value) == "tipo_invalido: texto"


def test_subclasse_permissiva_e_recusada_por_tipo():
    texto = TextoPermissivo(doc("## R01 — titulo", marcador("F1"), "> corpo"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "tipo_invalido: texto"


def test_subclasse_simples_tambem_e_recusada_por_tipo():
    texto = TextoSimples(doc("## R01 — titulo", marcador("F1"), "> corpo"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "tipo_invalido: texto"


def test_str_normal_com_o_mesmo_conteudo_continua_aceita():
    texto = doc("## R01 — titulo", marcador("F1"), "> corpo")
    assert ler_unidades_marcadas(str(texto)) == ("R01/F1",)


def test_a_subclasse_realmente_sequestra_a_igualdade():
    assert TextoPermissivo("qualquer") == "outra coisa"


def test_tipo_prevalece_sobre_conteudo_valido():
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(
            TextoPermissivo(doc("## R01 — t", marcador("F1"), "> corpo"))
        )
    assert categoria_de(erro) == "tipo_invalido"


def test_entrada_nao_e_convertida():
    class SemStrUtil:
        def __str__(self) -> str:  # pragma: no cover - nunca chamado
            raise AssertionError("a entrada foi convertida")

        def __repr__(self) -> str:  # pragma: no cover - nunca chamado
            raise AssertionError("a entrada foi inspecionada")

    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(SemStrUtil())
    assert str(erro.value) == "tipo_invalido: texto"


# ---------------------------------------------------------------------------
# D. Politica de linha — `LF`, `CRLF` e nada mais
# ---------------------------------------------------------------------------


DOCUMENTO_MULTI = doc(
    "# Documento",
    "",
    "## R01 — titulo",
    marcador("F1"),
    "> corpo um",
    "",
    "## R05 — titulo",
    marcador("F1"),
    "> corpo dois",
    marcador("F2"),
    "> corpo tres",
)


def test_lf_e_crlf_produzem_o_mesmo_resultado():
    assert ler_unidades_marcadas(DOCUMENTO_MULTI) == ler_unidades_marcadas(
        crlf(DOCUMENTO_MULTI)
    )


def test_crlf_produz_o_resultado_esperado():
    assert ler_unidades_marcadas(crlf(DOCUMENTO_MULTI)) == (
        "R01/F1",
        "R05/F1",
        "R05/F2",
    )


def test_documento_sem_quebra_final_e_lido_igual():
    texto = "## R01 — titulo\n" + marcador("F1") + "\n> corpo"
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_apenas_um_retorno_terminal_e_removido():
    # `\r\r\n` deixa um `\r` residual dentro da linha do marcador, que por isso
    # deixa de ser marcador — e o bloco seguinte fica sem marcador valido.
    texto = "## R01 — titulo\n" + marcador("F1") + "\r\r\n> corpo\n"
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "bloco_sem_marcador"


def test_retorno_duplo_no_cabecalho_deixa_zero_rxx_em_escopo():
    # O `\r` residual fica **dentro** da linha, logo apos o `Rxx`, e por isso o
    # token deixa de terminar em espaco ou fim de linha.
    texto = "## R01\r\r\n" + marcador("F1") + "\n> corpo\n"
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_fora_de_secao"


@pytest.mark.parametrize("separador", [" ", " ", "", "\v", "\f"])
def test_separador_exotico_nao_e_quebra_de_linha(separador):
    # Tudo colapsa numa unica linha, que nao e cabecalho, nao e marcador e nao
    # e bloco — logo nada e reconhecido.
    texto = separador.join(["prosa", marcador("F1"), "> corpo"]) + separador
    assert ler_unidades_marcadas(texto) == ()


@pytest.mark.parametrize("separador", [" ", " ", "", "\v", "\f"])
def test_separador_exotico_dentro_da_linha_desfaz_o_marcador(separador):
    texto = doc(
        "## R01 — titulo",
        marcador("F1") + separador,
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "bloco_sem_marcador"


def test_retorno_isolado_sem_quebra_nao_separa_linhas():
    texto = "prosa\r" + marcador("F1") + "\r> corpo\r"
    assert ler_unidades_marcadas(texto) == ()


# ---------------------------------------------------------------------------
# E. Delimitacao de secao
# ---------------------------------------------------------------------------


def test_cabecalho_nivel_1_encerra_a_secao_e_zera_o_escopo():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "# Outro documento",
        marcador("F1"),
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_fora_de_secao"


def test_cabecalho_nivel_2_nao_rxx_zera_o_escopo():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "## Apendice",
        marcador("F1"),
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_fora_de_secao"


@pytest.mark.parametrize("nivel", [3, 4, 5, 6])
def test_niveis_3_a_6_nao_encerram_a_secao(nivel):
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "#" * nivel + " Subtitulo",
        marcador("F2"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F2")


def test_sete_cerquilhas_nao_sao_cabecalho():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "####### nao e cabecalho",
        marcador("F2"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F2")


def test_cabecalho_indentado_nao_e_reconhecido():
    texto = doc(
        "  ## R01 — titulo",
        marcador("F1"),
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_fora_de_secao"


def test_cerquilha_sem_espaco_nao_e_cabecalho():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "##R02",
        marcador("F2"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F2")


def test_cabecalho_nivel_2_sem_texto_zera_o_escopo():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "##",
        marcador("F1"),
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_fora_de_secao"


def test_rxx_sozinho_na_linha_e_valido():
    texto = doc("## R01", marcador("F1"), "> corpo")
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


@pytest.mark.parametrize(
    "cabecalho",
    [
        "## R1 — um digito",
        "## R001 — tres digitos",
        "## r01 — minusculo",
        "## RXX — sem digito",
        "## R0a — digito e letra",
        "## R01x — sem separador",
        "##  R01 — espaco extra",
        "## R١٢ — digitos nao ascii",
    ],
)
def test_cabecalho_que_nao_abre_rxx_deixa_zero_escopo(cabecalho):
    texto = doc(cabecalho, marcador("F1"), "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_fora_de_secao"


def test_conteudo_antes_do_primeiro_rxx_e_ignorado():
    texto = doc(
        "# Titulo",
        "prosa livre",
        "## Sumario",
        "mais prosa",
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_conteudo_depois_do_ultimo_rxx_e_ignorado():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "",
        "prosa final",
        "### nota",
        "mais prosa",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_linha_de_citacao_nunca_e_cabecalho():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> ## R02 — nao e cabecalho",
        "> corpo",
        marcador("F2"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F2")


# ---------------------------------------------------------------------------
# E2. Bloco de citacao fora de `Rxx` — fora do dominio de `C-A5-U2`
#
# Por `C-A5-U2` a unidade vive **dentro** de uma secao `Rxx`. Um bloco nao
# marcado fora de qualquer secao **nao e** automaticamente unidade emitivel, e
# por isso e ignorado inteiro. Dentro de `Rxx` o bloco sem marcador continua
# fail-closed, e o marcador valido fora de `Rxx` tambem.
# ---------------------------------------------------------------------------


def test_bloco_fora_de_rxx_e_ignorado():
    texto = doc("# Titulo", "> nota", "> continuacao")
    assert ler_unidades_marcadas(texto) == ()


def test_bloco_fora_de_rxx_antes_de_secao_valida():
    texto = doc(
        "# Titulo",
        "> nota externa",
        "",
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_bloco_dentro_de_cabecalho_nivel_2_nao_rxx_e_ignorado():
    texto = doc(
        "## Apendice",
        "> nota externa",
        "",
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_bloco_fora_de_rxx_antes_do_primeiro_cabecalho_e_ignorado():
    texto = doc(
        "> nota de abertura",
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_bloco_fora_de_rxx_depois_da_ultima_secao_e_ignorado():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "# Encerramento",
        "> nota final",
        "> continuacao",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_bloco_maximal_fora_de_rxx_e_saltado_inteiro():
    # Nenhuma linha do bloco e interpretada: nem o que parece cabecalho, nem o
    # que parece marcador dentro dele.
    texto = doc(
        "# Titulo",
        "> ## R01 — nao abre secao",
        ">" + marcador("F1"),
        "> corpo",
        "## R02 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R02/F1",)


def test_varios_blocos_fora_de_rxx_sao_ignorados():
    texto = doc(
        "# Titulo",
        "> primeiro",
        "prosa",
        "> segundo",
        "## Apendice",
        "> terceiro",
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_bloco_sem_marcador_dentro_de_rxx_continua_fail_closed():
    texto = doc("## R01 — titulo", "> corpo sem marcador")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "bloco_sem_marcador: bloco"


def test_marcador_valido_fora_de_rxx_continua_fail_closed():
    texto = doc("# Titulo", marcador("F1"), "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "marcador_fora_de_secao: marcador"


def test_bloco_ignorado_nao_conta_como_unidade_da_secao_seguinte():
    texto = doc(
        "# Titulo",
        "> nota externa",
        "## R01 — titulo",
        "somente prosa",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "secao_sem_unidade: secao"


# ---------------------------------------------------------------------------
# F. Envelope do marcador — estagio A
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "quase",
    [
        "<!-- fragmento:F1 -->",
        "<!-- fragmento: F1 --> extra",
        "<!-- fragmento: F1 -->extra",
        "extra <!-- fragmento: F1 -->",
        " <!-- fragmento: F1 -->",
        "<!-- fragmento: F1 --> ",
        "<!--fragmento: F1 -->",
        "<!-- fragmento : F1 -->",
        "<!-- Fragmento: F1 -->",
        "<!-- fragmento: F1-->",
        "<!-- fragmento: F1 --",
        "<!-- fragmento: F1 --->",
        "<!-- fragmento: -->",
        "<!-- fragment: F1 -->",
    ],
)
def test_quase_marcador_nao_e_marcador(quase):
    texto = doc("## R01 — titulo", quase, "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "bloco_sem_marcador"


def test_quase_marcador_sem_bloco_e_conteudo_comum():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "<!-- fragmento:F2 -->",
        "prosa",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_marcador_textual_dentro_do_bloco_nao_e_marcador():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        ">" + marcador("F2"),
        "> mais corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_marcador_precedido_de_citacao_pertence_ao_bloco():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> " + marcador("F2"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


def test_envelope_com_id_vazio_e_candidato_e_falha_na_gramatica():
    texto = doc("## R01 — titulo", "<!-- fragmento:  -->", "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "id_fora_da_gramatica"


# ---------------------------------------------------------------------------
# G. Gramatica do `id` — estagio B (`C-A5-I3`)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("identificador", ["F1", "F2", "F10"])
def test_id_valido_e_aceito(identificador):
    texto = doc("## R01 — titulo", marcador(identificador), "> corpo")
    assert ler_unidades_marcadas(texto) == (f"R01/{identificador}",)


@pytest.mark.parametrize("identificador", ["F3", "F9", "F11", "F99", "F100"])
def test_outros_ids_conformes_tambem_sao_aceitos(identificador):
    texto = doc("## R01 — titulo", marcador(identificador), "> corpo")
    assert ler_unidades_marcadas(texto) == (f"R01/{identificador}",)


@pytest.mark.parametrize(
    "identificador",
    [
        "",
        "F",
        "F0",
        "F01",
        "f1",
        "F-1",
        "F1x",
        "F 1",
        "F+1",
        "F1.0",
        "1",
        "1F",
        "FF1",
        "F١",
        "F１",
        "F1​",
        "G1",
    ],
)
def test_id_fora_da_gramatica_e_recusado(identificador):
    texto = doc("## R01 — titulo", marcador(identificador), "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "id_fora_da_gramatica"


def test_zero_a_esquerda_e_recusado_mesmo_com_valor_positivo():
    texto = doc("## R01 — titulo", marcador("F010"), "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "id_fora_da_gramatica"


# ---------------------------------------------------------------------------
# H. As sete redacoes de `C-A5-X1`
# ---------------------------------------------------------------------------


def test_x1_1_bloco_destinado_a_emissao_sem_marcador_valido():
    texto = doc("## R01 — titulo", "> corpo sem marcador")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "bloco_sem_marcador: bloco"


def test_x1_2_marcador_orfao():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        marcador("F2"),
        "",
        "## R02 — titulo",
        marcador("F1"),
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "marcador_sem_bloco: marcador"


def test_x1_3_marcador_sem_bloco_imediatamente_seguinte():
    texto = doc("## R01 — titulo", marcador("F1"), "", "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "marcador_sem_bloco: marcador"


def test_x1_4_marcador_fora_de_rxx():
    texto = doc("# Titulo", marcador("F1"), "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "marcador_fora_de_secao: marcador"


def test_x1_5_id_fora_da_gramatica():
    texto = doc("## R01 — titulo", marcador("F0"), "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "id_fora_da_gramatica: marcador"


def test_x1_6_id_repetido_no_mesmo_rxx():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo um",
        marcador("F1"),
        "> corpo dois",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "id_duplicado: marcador"


def test_x1_7_rxx_sem_unidade_emitivel():
    texto = doc(
        "## R01 — titulo",
        "somente prosa",
        "## R02 — titulo",
        marcador("F1"),
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "secao_sem_unidade: secao"


def test_x1_7_tambem_vale_para_a_ultima_secao():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "## R02 — titulo",
        "somente prosa",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert str(erro.value) == "secao_sem_unidade: secao"


def test_secao_vazia_encerrada_por_cabecalho_nivel_1():
    texto = doc("## R01 — titulo", "prosa", "# Fim")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "secao_sem_unidade"


def test_as_seis_categorias_estruturais_sao_alcancaveis():
    alcancadas = set()
    casos = (
        doc("## R01 — titulo", "> corpo"),
        doc("## R01 — titulo", marcador("F1"), "prosa"),
        doc("# Titulo", marcador("F1"), "> corpo"),
        doc("## R01 — titulo", marcador("F0"), "> corpo"),
        doc(
            "## R01 — titulo",
            marcador("F1"),
            "> a",
            marcador("F1"),
            "> b",
        ),
        doc("## R01 — titulo", "prosa", "## R02 — t", marcador("F1"), "> a"),
    )
    for caso in casos:
        with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
            ler_unidades_marcadas(caso)
        alcancadas.add(categoria_de(erro))
    assert alcancadas == {
        "bloco_sem_marcador",
        "marcador_sem_bloco",
        "marcador_fora_de_secao",
        "id_fora_da_gramatica",
        "id_duplicado",
        "secao_sem_unidade",
    }
    assert len(alcancadas) == 6


def test_nao_existe_oitava_categoria():
    from casa77_sdr import response_markdown_units

    publicos = set(response_markdown_units.__all__)
    constantes = set(_constantes_de_codigo()) - publicos
    candidatas = {
        constante
        for constante in constantes
        if constante.islower() and "_" in constante and " " not in constante
    }
    assert candidatas == set(CATEGORIAS)
    assert len(CATEGORIAS) == 7


# ---------------------------------------------------------------------------
# I. Marcador sem bloco — as cinco continuacoes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "continuacao",
    [
        "",
        "prosa comum",
        "<!-- fragmento: F2 -->",
        "## R02 — titulo",
        "# Titulo",
        "### Subtitulo",
    ],
)
def test_marcador_seguido_de_nao_bloco(continuacao):
    texto = doc("## R01 — titulo", marcador("F1"), continuacao, "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_sem_bloco"


def test_marcador_no_fim_do_arquivo():
    texto = "## R01 — titulo\n" + marcador("F1")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_sem_bloco"


def test_marcador_no_fim_do_arquivo_com_quebra():
    texto = doc("## R01 — titulo", marcador("F1"))
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_sem_bloco"


def test_linha_em_branco_entre_marcador_e_bloco_e_recusada():
    texto = doc("## R01 — titulo", marcador("F1"), "", "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_sem_bloco"


# ---------------------------------------------------------------------------
# J. Unicidade local, `Rxx` duplicado (`D4`) e limite de `C-A5-I6`
# ---------------------------------------------------------------------------


def test_mesmo_id_em_rxx_distintos_e_valido():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "## R02 — titulo",
        marcador("F1"),
        "> corpo",
        "## R03 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R02/F1", "R03/F1")


def test_id_duplicado_e_local_a_secao_e_nao_ao_documento():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        marcador("F2"),
        "> corpo",
        "## R02 — titulo",
        marcador("F2"),
        "> corpo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == (
        "R01/F1",
        "R01/F2",
        "R02/F2",
        "R02/F1",
    )


def test_rxx_duplicado_nao_e_recusado():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "## R01 — outra vez",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F1")


def test_rxx_duplicado_pode_repetir_token_global():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "## R01 — outra vez",
        marcador("F1"),
        "> corpo",
    )
    tokens = ler_unidades_marcadas(texto)
    assert len(tokens) == 2
    assert len(set(tokens)) == 1


def test_secao_homonima_reabre_o_espaco_de_id():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        "## Intervalo",
        "prosa",
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
    )
    assert ler_unidades_marcadas(texto) == ("R01/F1", "R01/F1")


def test_i6_nao_e_provada_e_o_snapshot_isolado_e_aceito():
    # `C-A5-I6` proibe reutilizar `F1` apos a remocao historica daquele
    # fragmento. Um snapshot unico nao carrega esse historico, e a fronteira
    # **nao** o inventa: o documento abaixo e aceito.
    texto = doc("## R01 — titulo", marcador("F1"), "> outro corpo")
    assert ler_unidades_marcadas(texto) == ("R01/F1",)


# ---------------------------------------------------------------------------
# K. Precedencia — primeira violacao em ordem de documento
# ---------------------------------------------------------------------------


def test_violacao_anterior_no_documento_prevalece():
    texto = doc(
        "## R01 — titulo",
        "> bloco sem marcador",
        marcador("F0"),
        "> corpo",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "bloco_sem_marcador"


def test_violacao_posterior_nao_encobre_a_primeira():
    texto = doc(
        "## R01 — titulo",
        marcador("F0"),
        "> corpo",
        "> bloco sem marcador",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "id_fora_da_gramatica"


def test_gramatica_precede_o_escopo():
    texto = doc("prosa solta", marcador("F0"), "> corpo")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "id_fora_da_gramatica"


def test_escopo_precede_a_existencia_do_bloco():
    texto = doc("prosa solta", marcador("F1"), "prosa")
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_fora_de_secao"


def test_existencia_do_bloco_precede_a_duplicidade():
    texto = doc(
        "## R01 — titulo",
        marcador("F1"),
        "> corpo",
        marcador("F1"),
        "prosa",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "marcador_sem_bloco"


def test_secao_sem_unidade_e_detectada_ao_encerrar_e_nao_no_fim():
    texto = doc(
        "## R01 — titulo",
        "prosa",
        "## R02 — titulo",
        "> bloco sem marcador",
    )
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(texto)
    assert categoria_de(erro) == "secao_sem_unidade"


def test_tipo_precede_toda_a_estrutura():
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(TextoSimples(doc("## R01 — t", "> sem marcador")))
    assert categoria_de(erro) == "tipo_invalido"


# ---------------------------------------------------------------------------
# L. Mensagem de erro — forma fechada e sem vazamento
# ---------------------------------------------------------------------------

CASOS_DE_FALHA = (
    doc("## R01 — titulo", "> segredo comercial"),
    doc("## R01 — titulo", marcador("F1"), "prosa"),
    doc("# Titulo", marcador("F1"), "> segredo comercial"),
    doc("## R01 — titulo", marcador("F0"), "> segredo comercial"),
    doc(
        "## R01 — titulo",
        marcador("F1"),
        "> a",
        marcador("F1"),
        "> b",
    ),
    doc("## R01 — titulo", "prosa", "## R02 — t", marcador("F1"), "> a"),
)


@pytest.mark.parametrize("caso", CASOS_DE_FALHA)
def test_mensagem_tem_categoria_e_localizador(caso):
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(caso)
    mensagem = str(erro.value)
    categoria, _, localizador = mensagem.partition(": ")
    assert categoria in CATEGORIAS
    assert localizador in LOCALIZADORES
    assert mensagem == f"{categoria}: {localizador}"


@pytest.mark.parametrize("caso", CASOS_DE_FALHA)
def test_mensagem_nao_vaza_id_rxx_nem_conteudo(caso):
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(caso)
    mensagem = str(erro.value)
    for vazamento in (
        "R01",
        "R02",
        "F0",
        "F1",
        "segredo",
        "comercial",
        "titulo",
        "prosa",
        "fragmento",
        "<!--",
        ">",
        "/",
    ):
        assert vazamento not in mensagem


@pytest.mark.parametrize("caso", CASOS_DE_FALHA)
def test_mensagem_nao_vaza_numero(caso):
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(caso)
    assert not any(caractere.isdigit() for caractere in str(erro.value))


def test_mensagem_de_tipo_nao_vaza_o_tipo_concreto():
    with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
        ler_unidades_marcadas(12345)
    mensagem = str(erro.value)
    assert "int" not in mensagem
    assert "12345" not in mensagem
    assert mensagem == "tipo_invalido: texto"


def test_excecao_deriva_apenas_de_exception():
    assert RepresentacaoMarcadaInvalida.__bases__ == (Exception,)


def test_excecao_nao_e_parente_de_outro_erro_do_projeto():
    from casa77_sdr.response_bijection import BijecaoInvalida
    from casa77_sdr.response_index import IndiceInvalido
    from casa77_sdr.response_status import StatusNaoCanonicalizavel

    for outra in (BijecaoInvalida, IndiceInvalido, StatusNaoCanonicalizavel):
        assert not issubclass(RepresentacaoMarcadaInvalida, outra)
        assert not issubclass(outra, RepresentacaoMarcadaInvalida)


# ---------------------------------------------------------------------------
# M. Pureza do modulo de producao
# ---------------------------------------------------------------------------


def test_nao_e_exportado_pelo_pacote():
    assert "ler_unidades_marcadas" not in casa77_sdr.__all__
    assert "RepresentacaoMarcadaInvalida" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "ler_unidades_marcadas")
    assert not hasattr(casa77_sdr, "RepresentacaoMarcadaInvalida")


def test_all_do_modulo_e_fechado():
    from casa77_sdr import response_markdown_units

    assert response_markdown_units.__all__ == [
        "RepresentacaoMarcadaInvalida",
        "ler_unidades_marcadas",
    ]


def test_imports_sao_fechados_em_future():
    importados = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_modulo = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert importados == []
    assert [no.module for no in de_modulo] == ["__future__"]


def test_nao_importa_nada_do_proprio_pacote():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.ImportFrom):
            assert not (no.module or "").startswith("casa77_sdr")
        if isinstance(no, ast.Import):  # pragma: no cover - lista ja e vazia
            for alias in no.names:
                assert not alias.name.startswith("casa77_sdr")


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
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_yaml_nem_serializacao_externa():
    proibidos = {"yaml", "safe_load", "load", "json", "loads", "dumps", "pickle"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_rede_processo_nem_llm():
    proibidos = {
        "socket",
        "requests",
        "urllib",
        "urlopen",
        "http",
        "httpx",
        "subprocess",
        "run",
        "Popen",
        "git",
        "prompt",
        "completions",
        "sqlite3",
        "connect",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_relogio_calendario_locale_nem_ambiente():
    proibidos = {
        "time",
        "monotonic",
        "datetime",
        "date",
        "now",
        "utcnow",
        "today",
        "calendar",
        "locale",
        "setlocale",
        "getenv",
        "environ",
        "zoneinfo",
        "random",
        "uuid",
        "hashlib",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_de_texto():
    proibidos = {
        "unicodedata",
        "normalize",
        "casefold",
        "lower",
        "upper",
        "strip",
        "lstrip",
        "rstrip",
        "expandtabs",
        "splitlines",
        "translate",
        "encode",
        "decode",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_execucao_dinamica():
    proibidos = {"eval", "exec", "compile", "__import__", "importlib", "globals"}
    assert not proibidos & NOMES_PRODUCAO


def test_a_divisao_e_feita_somente_por_quebra_de_linha():
    # `splitlines` so pode aparecer na docstring, que **declara** que ele nao e
    # usado; no codigo executavel ele nao existe.
    assert "splitlines" not in NOMES_PRODUCAO
    divisoes = [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Call)
        and isinstance(no.func, ast.Attribute)
        and no.func.attr == "split"
    ]
    assert len(divisoes) == 1


def test_a_docstring_declara_as_nao_garantias():
    docstring = ast.get_docstring(ARVORE_PRODUCAO) or ""
    for exigido in (
        "LER A REPRESENTAÇÃO MARCADA NÃO É MATERIALIZAR",
        "C-A5-I6",
        "unicidade física das seções",
        "C-A1-ST6",
        "C-15",
        "Setext",
        "splitlines",
    ):
        assert exigido in docstring


# ---------------------------------------------------------------------------
# N. Determinismo, idempotencia e ausencia de efeito
# ---------------------------------------------------------------------------


def test_chamadas_repetidas_devolvem_o_mesmo_resultado():
    assert ler_unidades_marcadas(DOCUMENTO_MULTI) == ler_unidades_marcadas(
        DOCUMENTO_MULTI
    )


def test_a_entrada_nao_e_alterada():
    antes = DOCUMENTO_MULTI
    copia = str(DOCUMENTO_MULTI)
    ler_unidades_marcadas(antes)
    assert antes == copia


def test_nao_ha_estado_entre_chamadas():
    primeiro = doc("## R01 — titulo", marcador("F1"), "> corpo")
    segundo = doc("## R01 — titulo", marcador("F1"), "> outro corpo")
    assert ler_unidades_marcadas(primeiro) == ("R01/F1",)
    assert ler_unidades_marcadas(segundo) == ("R01/F1",)
    assert ler_unidades_marcadas(primeiro) == ("R01/F1",)


def test_falha_repetida_devolve_a_mesma_mensagem():
    caso = doc("## R01 — titulo", "> corpo")
    mensagens = set()
    for _ in range(3):
        with pytest.raises(RepresentacaoMarcadaInvalida) as erro:
            ler_unidades_marcadas(caso)
        mensagens.add(str(erro.value))
    assert len(mensagens) == 1


# ---------------------------------------------------------------------------
# O. Guarda do corpus real — `C-A5-M5`, 37/37
# ---------------------------------------------------------------------------


def _corpus() -> str:
    """Texto do corpus lido em bytes e decodificado, sem *universal newline*.

    `read_bytes` e `decode` preservam a terminação física do arquivo; usar
    `read_text` converteria `CRLF` em `LF` **antes** do módulo e o teste
    deixaria de exercitar a política local de linha.
    """
    return CAMINHO_CORPUS.read_bytes().decode("utf-8")


def test_o_corpus_real_produz_trinta_e_sete_tokens():
    assert len(ler_unidades_marcadas(_corpus())) == TOTAL_APROVADO


def test_os_tokens_do_corpus_real_sao_distintos():
    tokens = ler_unidades_marcadas(_corpus())
    assert len(set(tokens)) == TOTAL_APROVADO


def test_o_corpus_real_coincide_com_o_mapeamento_aprovado():
    assert set(ler_unidades_marcadas(_corpus())) == UNIDADES_APROVADAS


def test_o_conjunto_aprovado_tem_trinta_e_sete_entradas():
    assert len(UNIDADES_APROVADAS) == TOTAL_APROVADO


def test_o_corpus_real_nao_dispara_falha():
    ler_unidades_marcadas(_corpus())


def test_a_leitura_do_corpus_real_e_idempotente():
    texto = _corpus()
    assert ler_unidades_marcadas(texto) == ler_unidades_marcadas(texto)
