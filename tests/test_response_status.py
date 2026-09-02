"""Testes da canonicalização determinística de rótulo de status já extraído.

A fronteira materializa **apenas** as três traduções automáticas de
`C-A1-ST1`–`C-A1-ST3`. Estes testes provam essas três traduções, o **fechamento**
da tabela, a recusa de tipo, a precedência fixa, a **ausência total de
normalização**, o silêncio da mensagem de erro, a pureza do módulo de produção e
o determinismo — e **não** transformam em norma um mapeamento de `BLOQUEADO`, um
mapeamento automático de `PARCIAL`, qualquer tolerância, uma quarta tradução, a
migração de autoridade de status, o status agregado de um `Rxx` ou a
emissibilidade de fragmento, que estão **fora** desta fronteira.
"""

from __future__ import annotations

import ast
import inspect
from enum import Enum
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_status import StatusNaoCanonicalizavel, canonicalizar_status

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

# Os rotulos acentuados sao escritos por escape para que o teste nao dependa da
# forma de normalizacao com que este arquivo foi gravado. `C7` e `C3` sao a
# cedilha e o til **compostos** (NFC); `F3` e o `o` agudo composto.
APROVADO_MD = "APROVADO"
AGUARDA_MD = "AGUARDA APROVA\u00c7\u00c3O"
HANDOFF_MD = "APROVADO com handoff obrigat\u00f3rio"

# Imagens canonicas de `C-3` alcancaveis por traducao automatica.
APROVADO_CANONICO = "APROVADO"
AGUARDA_CANONICO = "AGUARDA_APROVACAO"

# As tres traducoes arbitradas, e nenhuma quarta.
TRADUCOES = (
    (APROVADO_MD, APROVADO_CANONICO),
    (AGUARDA_MD, AGUARDA_CANONICO),
    (HANDOFF_MD, APROVADO_CANONICO),
)

# Mesmas cadeias em forma **decomposta** (NFD): cedilha e til combinantes, e `o`
# seguido de acento agudo combinante. Visualmente iguais, textualmente outras.
AGUARDA_MD_NFD = "AGUARDA APROVAC\u0327A\u0303O"
HANDOFF_MD_NFD = "APROVADO com handoff obrigato\u0301rio"

# Espaco inquebravel no lugar do espaco comum.
AGUARDA_MD_NBSP = "AGUARDA\u00a0APROVA\u00c7\u00c3O"
HANDOFF_MD_NBSP = "APROVADO com handoff\u00a0obrigat\u00f3rio"

CATEGORIAS = ("tipo_invalido", "rotulo_nao_mapeado")
LOCALIZADOR = "rotulo"

MENSAGEM_TIPO = "tipo_invalido: rotulo"
MENSAGEM_NAO_MAPEADO = "rotulo_nao_mapeado: rotulo"

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_status.py"
)
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)


class RotuloPermissivo(str):
    """Subclasse de `str` que sequestra a igualdade e o hash.

    Ela se declara igual a qualquer coisa. Se a fronteira consultasse a tabela
    antes de conferir o tipo, esta subclasse decidiria sozinha a que linha
    pertence — exatamente o que a recusa por tipo exato impede.
    """

    def __eq__(self, outro: object) -> bool:
        return True

    def __ne__(self, outro: object) -> bool:
        return False

    def __hash__(self) -> int:
        return hash(APROVADO_CANONICO)


class RotuloSimples(str):
    """Subclasse de `str` que nada redefine. Ainda assim, não é `str` exata."""


class ObjetoComStr:
    """Objeto que **parece** um rótulo quando convertido — e nunca é convertido."""

    def __str__(self) -> str:
        return APROVADO_MD

    def __repr__(self) -> str:
        return APROVADO_MD


class RotuloEnum(str, Enum):
    """Enum de `str`: o tipo concreto é o enum, nunca `str` exata."""

    APROVADO = "APROVADO"


class RotuloEnumPuro(Enum):
    """Enum que não é `str` de forma alguma."""

    APROVADO = "APROVADO"


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
# A. Traducoes automaticas — as tres, e a imagem exata
# ---------------------------------------------------------------------------


def test_st1_aprovado_traduz_para_aprovado():
    assert canonicalizar_status(APROVADO_MD) == APROVADO_CANONICO


def test_st2_aguarda_aprovacao_traduz_para_aguarda_aprovacao():
    assert canonicalizar_status(AGUARDA_MD) == AGUARDA_CANONICO


def test_st3_handoff_traduz_para_aprovado():
    assert canonicalizar_status(HANDOFF_MD) == APROVADO_CANONICO


def test_st3_nao_transporta_o_sufixo_de_handoff():
    devolvido = canonicalizar_status(HANDOFF_MD)
    assert "handoff" not in devolvido
    assert "obrigat" not in devolvido
    assert devolvido == APROVADO_CANONICO


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_traducoes_devolvem_a_imagem_exata(rotulo, esperado):
    devolvido = canonicalizar_status(rotulo)
    assert devolvido == esperado
    assert type(devolvido) is str


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_imagem_esta_no_vocabulario_fechado_de_c3(rotulo, esperado):
    assert esperado in ("APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO")


def test_st1_e_st3_compartilham_a_mesma_imagem():
    assert canonicalizar_status(APROVADO_MD) == canonicalizar_status(HANDOFF_MD)


def test_a_imagem_de_st2_nao_tem_espaco():
    assert " " not in canonicalizar_status(AGUARDA_MD)


def test_a_imagem_de_st2_nao_tem_acento():
    devolvido = canonicalizar_status(AGUARDA_MD)
    assert devolvido.isascii()


# ---------------------------------------------------------------------------
# B. Fechamento da tabela automatica
# ---------------------------------------------------------------------------


def test_parcial_nao_tem_traducao_automatica():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status("PARCIAL")
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


def test_bloqueado_nao_ganha_mapeamento_inventado():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status("BLOQUEADO")
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


def test_status_ja_canonico_nao_e_reaceito():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status("AGUARDA_APROVACAO")
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


def test_string_vazia_e_recusada():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status("")
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


@pytest.mark.parametrize(
    "rotulo",
    [
        "PARCIAL",
        "BLOQUEADO",
        "AGUARDA_APROVACAO",
        "",
        " ",
        "APROVADO_COM_HANDOFF",
        "APROVADO com handoff",
        "handoff obrigatório",
        "REPROVADO",
        "PENDENTE",
        "RASCUNHO",
        "APROVADA",
        "APROVADOS",
        "AGUARDA",
        "APROVAÇÃO",
        "NULL",
        "None",
        "0",
    ],
)
def test_rotulo_fora_da_tabela_e_recusado(rotulo):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(rotulo)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


def test_exatamente_tres_rotulos_sao_aceitos_entre_os_candidatos_plausiveis():
    candidatos = [
        APROVADO_MD,
        AGUARDA_MD,
        HANDOFF_MD,
        "PARCIAL",
        "BLOQUEADO",
        "AGUARDA_APROVACAO",
        "APROVADO com handoff",
        AGUARDA_MD_NFD,
        HANDOFF_MD_NFD,
        AGUARDA_MD_NBSP,
        "aprovado",
        "",
    ]
    aceitos = []
    for candidato in candidatos:
        try:
            canonicalizar_status(candidato)
        except StatusNaoCanonicalizavel:
            continue
        aceitos.append(candidato)
    assert aceitos == [APROVADO_MD, AGUARDA_MD, HANDOFF_MD]


def test_nenhuma_imagem_bloqueado_e_produzida():
    for rotulo, esperado in TRADUCOES:
        assert canonicalizar_status(rotulo) != "BLOQUEADO"


# ---------------------------------------------------------------------------
# C. Tipos invalidos — nenhuma coercao
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalido",
    [
        None,
        0,
        1,
        -1,
        True,
        False,
        1.0,
        1j,
        b"APROVADO",
        bytearray(b"APROVADO"),
        memoryview(b"APROVADO"),
        ["APROVADO"],
        ("APROVADO",),
        {"APROVADO"},
        {"rotulo": "APROVADO"},
        frozenset({"APROVADO"}),
        range(1),
        object(),
        ObjetoComStr(),
        RotuloEnum.APROVADO,
        RotuloEnumPuro.APROVADO,
        canonicalizar_status,
        str,
        Ellipsis,
        NotImplemented,
    ],
)
def test_tipo_invalido_e_recusado(invalido):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(invalido)
    assert str(erro.value) == MENSAGEM_TIPO


def test_objeto_com_str_nao_e_convertido():
    candidato = ObjetoComStr()
    assert str(candidato) == APROVADO_MD
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(candidato)
    assert str(erro.value) == MENSAGEM_TIPO


def test_bytes_com_o_mesmo_conteudo_nao_e_aceito():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(APROVADO_MD.encode("utf-8"))
    assert str(erro.value) == MENSAGEM_TIPO


def test_enum_de_str_e_recusado_por_tipo():
    assert RotuloEnum.APROVADO == APROVADO_MD
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(RotuloEnum.APROVADO)
    assert str(erro.value) == MENSAGEM_TIPO


def test_bool_nao_e_tratado_como_rotulo():
    for valor in (True, False):
        with pytest.raises(StatusNaoCanonicalizavel) as erro:
            canonicalizar_status(valor)
        assert str(erro.value) == MENSAGEM_TIPO


# ---------------------------------------------------------------------------
# D. Subclasse adversarial de str
# ---------------------------------------------------------------------------


def test_a_subclasse_realmente_sequestra_a_igualdade():
    permissivo = RotuloPermissivo("QUALQUER COISA")
    assert permissivo == APROVADO_MD
    assert permissivo == "PARCIAL"
    assert permissivo == ""
    assert hash(permissivo) == hash(APROVADO_CANONICO)


def test_subclasse_permissiva_com_conteudo_valido_e_recusada_por_tipo():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(RotuloPermissivo(APROVADO_MD))
    assert str(erro.value) == MENSAGEM_TIPO


def test_subclasse_permissiva_com_conteudo_invalido_tambem_falha_por_tipo():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(RotuloPermissivo("QUALQUER COISA"))
    assert str(erro.value) == MENSAGEM_TIPO


@pytest.mark.parametrize("rotulo", [APROVADO_MD, AGUARDA_MD, HANDOFF_MD])
def test_subclasse_simples_e_recusada_nas_tres_linhas(rotulo):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(RotuloSimples(rotulo))
    assert str(erro.value) == MENSAGEM_TIPO


def test_str_normal_com_o_mesmo_conteudo_da_subclasse_continua_aceita():
    assert canonicalizar_status(str(RotuloSimples(APROVADO_MD))) == APROVADO_CANONICO


# ---------------------------------------------------------------------------
# E. Precedencia — tipo antes de pertenca
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalido",
    [
        RotuloPermissivo(APROVADO_MD),
        RotuloSimples(APROVADO_MD),
        RotuloEnum.APROVADO,
        b"APROVADO",
        bytearray(b"APROVADO"),
        ObjetoComStr(),
    ],
)
def test_tipo_invalido_prevalece_sobre_conteudo_aparentemente_valido(invalido):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(invalido)
    assert str(erro.value) == MENSAGEM_TIPO
    assert str(erro.value) != MENSAGEM_NAO_MAPEADO


@pytest.mark.parametrize(
    "invalido",
    [None, 0, b"PARCIAL", RotuloSimples("PARCIAL"), RotuloPermissivo("PARCIAL")],
)
def test_tipo_invalido_prevalece_tambem_sobre_conteudo_invalido(invalido):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(invalido)
    assert str(erro.value) == MENSAGEM_TIPO


def test_str_exata_invalida_cai_em_nao_mapeado_e_nao_em_tipo():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status("PARCIAL")
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO
    assert str(erro.value) != MENSAGEM_TIPO


# ---------------------------------------------------------------------------
# F. Ausencia de normalizacao
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "variante",
    [
        "aprovado",
        "Aprovado",
        "aPROVADO",
        "APROVADo",
        "aguarda aprovação",
        "Aguarda Aprovação",
        "APROVADO COM HANDOFF OBRIGATÓRIO",
        "APROVADO Com Handoff Obrigatório",
    ],
)
def test_variacao_de_caixa_nao_e_tolerada(variante):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(variante)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


@pytest.mark.parametrize(
    "variante",
    [
        " APROVADO",
        "APROVADO ",
        " APROVADO ",
        "\tAPROVADO",
        "APROVADO\t",
        "APROVADO\n",
        "\nAPROVADO",
        "APROVADO\r\n",
        " " + AGUARDA_MD,
        AGUARDA_MD + " ",
        " " + HANDOFF_MD,
        HANDOFF_MD + " ",
    ],
)
def test_espaco_nas_bordas_nao_e_removido(variante):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(variante)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


@pytest.mark.parametrize(
    "variante",
    [
        "AGUARDA  APROVAÇÃO",
        "APROVADO  com handoff obrigatório",
        "APROVADO com  handoff obrigatório",
        "APROVADO com handoff  obrigatório",
    ],
)
def test_espaco_duplicado_nao_e_colapsado(variante):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(variante)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


@pytest.mark.parametrize("variante", [AGUARDA_MD_NBSP, HANDOFF_MD_NBSP])
def test_espaco_inquebravel_nao_e_substituido(variante):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(variante)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


@pytest.mark.parametrize("variante", [AGUARDA_MD_NFD, HANDOFF_MD_NFD])
def test_forma_decomposta_nfd_e_um_rotulo_distinto(variante):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(variante)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


def test_nfd_e_nfc_sao_visualmente_iguais_e_textualmente_distintos():
    import unicodedata

    assert AGUARDA_MD != AGUARDA_MD_NFD
    assert unicodedata.normalize("NFC", AGUARDA_MD_NFD) == AGUARDA_MD
    assert HANDOFF_MD != HANDOFF_MD_NFD
    assert unicodedata.normalize("NFC", HANDOFF_MD_NFD) == HANDOFF_MD


def test_a_tabela_de_producao_esta_em_forma_composta():
    import unicodedata

    assert unicodedata.is_normalized("NFC", AGUARDA_MD)
    assert unicodedata.is_normalized("NFC", HANDOFF_MD)
    assert canonicalizar_status(unicodedata.normalize("NFC", AGUARDA_MD_NFD)) == (
        AGUARDA_CANONICO
    )


@pytest.mark.parametrize(
    "variante",
    [
        "AGUARDA APROVACAO",
        "AGUARDA APROVACÃO",
        "APROVADO com handoff obrigatorio",
        "APROVADO COM HANDOFF OBRIGATORIO",
    ],
)
def test_ausencia_de_acento_nao_e_tolerada(variante):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(variante)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


@pytest.mark.parametrize(
    "variante",
    [
        "APROVADO\u0000",
        "\u0000APROVADO",
        "APROVADO\u0007",
        "APROVADO\u200b",
        "\ufeffAPROVADO",
        "APROVADO\u00ad",
        "APROVAD\u041e",
        "APROVADO\u2000",
    ],
)
def test_caractere_extra_ou_confundivel_e_recusado(variante):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(variante)
    assert str(erro.value) == MENSAGEM_NAO_MAPEADO


def test_prefixo_e_sufixo_nao_sao_aceitos():
    for variante in (
        "APROVADO.",
        ".APROVADO",
        "APROVADO:",
        "status: APROVADO",
        "APROVADO com handoff obrigatório.",
        "**APROVADO**",
    ):
        with pytest.raises(StatusNaoCanonicalizavel) as erro:
            canonicalizar_status(variante)
        assert str(erro.value) == MENSAGEM_NAO_MAPEADO


# ---------------------------------------------------------------------------
# G. Seguranca da mensagem
# ---------------------------------------------------------------------------

CASOS_DE_ERRO = (
    ("PARCIAL", MENSAGEM_NAO_MAPEADO),
    ("BLOQUEADO", MENSAGEM_NAO_MAPEADO),
    ("", MENSAGEM_NAO_MAPEADO),
    ("aprovado", MENSAGEM_NAO_MAPEADO),
    (" APROVADO ", MENSAGEM_NAO_MAPEADO),
    (AGUARDA_MD_NFD, MENSAGEM_NAO_MAPEADO),
    ("SENTINELA-OPACA-9137", MENSAGEM_NAO_MAPEADO),
    (None, MENSAGEM_TIPO),
    (12345678, MENSAGEM_TIPO),
    (b"SENTINELA-EM-BYTES", MENSAGEM_TIPO),
    (RotuloPermissivo("SENTINELA-EM-SUBCLASSE"), MENSAGEM_TIPO),
    (ObjetoComStr(), MENSAGEM_TIPO),
)


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_tem_categoria_e_localizador_fechados(entrada, mensagem):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(entrada)
    texto = str(erro.value)
    assert texto == mensagem
    categoria, _, localizador = texto.partition(": ")
    assert categoria in CATEGORIAS
    assert localizador == LOCALIZADOR


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_a_entrada(entrada, mensagem):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(entrada)
    texto = str(erro.value)
    assert "SENTINELA" not in texto
    assert "PARCIAL" not in texto
    assert "BLOQUEADO" not in texto
    assert "APROVADO" not in texto
    assert "aprovado" not in texto


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_o_tipo_concreto(entrada, mensagem):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(entrada)
    texto = str(erro.value)
    for proibido in (
        type(entrada).__name__,
        "NoneType",
        "bytes",
        "int",
        "RotuloPermissivo",
        "ObjetoComStr",
    ):
        if proibido == "int" and "tipo_invalido" in texto:
            continue
        assert proibido not in texto


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_tem_numero_nem_indice(entrada, mensagem):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(entrada)
    texto = str(erro.value)
    assert not any(caractere.isdigit() for caractere in texto)
    assert "[" not in texto
    assert "]" not in texto


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_tem_repr(entrada, mensagem):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(entrada)
    texto = str(erro.value)
    assert "'" not in texto
    assert '"' not in texto
    assert "<" not in texto
    assert ">" not in texto


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_excecao_nao_tem_cause_nem_context(entrada, mensagem):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(entrada)
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None
    assert erro.value.__suppress_context__ is False


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_excecao_carrega_um_unico_argumento(entrada, mensagem):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        canonicalizar_status(entrada)
    assert erro.value.args == (mensagem,)


def test_as_duas_categorias_declaradas_sao_alcancaveis():
    alcancadas = set()
    for entrada, _ in CASOS_DE_ERRO:
        with pytest.raises(StatusNaoCanonicalizavel) as erro:
            canonicalizar_status(entrada)
        alcancadas.add(str(erro.value).partition(": ")[0])
    assert alcancadas == set(CATEGORIAS)


def test_nenhuma_terceira_categoria_e_produzida():
    for entrada, _ in CASOS_DE_ERRO:
        with pytest.raises(StatusNaoCanonicalizavel) as erro:
            canonicalizar_status(entrada)
        assert str(erro.value).partition(": ")[0] in CATEGORIAS


# ---------------------------------------------------------------------------
# H. Superficie publica
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_dois_nomes():
    from casa77_sdr import response_status

    assert response_status.__all__ == [
        "StatusNaoCanonicalizavel",
        "canonicalizar_status",
    ]


def test_modulo_nao_expoe_outra_funcao_publica():
    from casa77_sdr import response_status

    publicos = {
        nome
        for nome, valor in vars(response_status).items()
        if not nome.startswith("_") and callable(valor)
    }
    assert publicos == {"StatusNaoCanonicalizavel", "canonicalizar_status"}


def test_assinatura_tem_um_unico_parametro_sem_default():
    assinatura = inspect.signature(canonicalizar_status)
    parametros = list(assinatura.parameters.values())
    assert len(parametros) == 1
    (parametro,) = parametros
    assert parametro.name == "rotulo"
    assert parametro.default is inspect.Parameter.empty
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_assinatura_nao_tem_parametro_de_contexto_ou_tolerancia():
    assinatura = inspect.signature(canonicalizar_status)
    proibidos = {
        "contexto",
        "origem",
        "modo",
        "tolerancia",
        "fragmento",
        "rxx",
        "config",
        "configuracao",
        "normalizar",
        "estrito",
        "default",
        "padrao",
    }
    assert not proibidos & set(assinatura.parameters)


def test_funcao_declara_retorno_str():
    assinatura = inspect.signature(canonicalizar_status)
    assert assinatura.return_annotation in (str, "str")


def test_excecao_deriva_diretamente_de_exception():
    assert StatusNaoCanonicalizavel.__bases__ == (Exception,)


def test_excecao_nao_e_subclasse_de_outro_erro_do_projeto():
    from casa77_sdr.response_bijection import BijecaoInvalida
    from casa77_sdr.response_index import IndiceInvalido

    assert not issubclass(StatusNaoCanonicalizavel, BijecaoInvalida)
    assert not issubclass(StatusNaoCanonicalizavel, IndiceInvalido)
    assert not issubclass(BijecaoInvalida, StatusNaoCanonicalizavel)


def test_nao_e_exportado_pelo_pacote():
    assert "StatusNaoCanonicalizavel" not in casa77_sdr.__all__
    assert "canonicalizar_status" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "canonicalizar_status")
    assert not hasattr(casa77_sdr, "StatusNaoCanonicalizavel")


def test_tabela_nao_esta_em_all():
    from casa77_sdr import response_status

    for nome in response_status.__all__:
        valor = getattr(response_status, nome)
        assert not isinstance(valor, (tuple, list, dict, set))


# ---------------------------------------------------------------------------
# I. Pureza (AST) e ausencia de estado mutavel publico
# ---------------------------------------------------------------------------


def test_imports_sao_fechados_em_future():
    importados = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, (ast.Import,))
    ]
    de_modulo = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert importados == []
    assert [no.module for no in de_modulo] == ["__future__"]


def test_nao_importa_nada_do_proprio_pacote():
    assert "casa77_sdr" not in CODIGO_PRODUCAO.split('"""')[-1]
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.ImportFrom):
            assert not (no.module or "").startswith("casa77_sdr")


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
        "Path",
        "os",
        "io",
        "pathlib",
        "shutil",
        "tempfile",
        "glob",
        "listdir",
        "stat",
        "print",
        "input",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_yaml_nem_serializacao_externa():
    proibidos = {"yaml", "safe_load", "json", "loads", "dumps", "pickle", "toml"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_rede_nem_processo():
    proibidos = {
        "socket",
        "urllib",
        "urlopen",
        "requests",
        "http",
        "httpx",
        "subprocess",
        "Popen",
        "system",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_locale_ambiente_relogio_nem_calendario():
    proibidos = {
        "locale",
        "setlocale",
        "getenv",
        "environ",
        "time",
        "datetime",
        "date",
        "now",
        "today",
        "timezone",
        "calendar",
        "random",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_unicode_nem_de_texto():
    proibidos = {
        "unicodedata",
        "normalize",
        "is_normalized",
        "casefold",
        "lower",
        "upper",
        "title",
        "capitalize",
        "strip",
        "lstrip",
        "rstrip",
        "replace",
        "translate",
        "split",
        "encode",
        "decode",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_execucao_dinamica():
    proibidos = {"eval", "exec", "compile", "__import__", "globals", "locals", "getattr"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_usa_isinstance_para_decidir_o_tipo():
    assert "isinstance" not in NOMES_PRODUCAO


def test_o_tipo_e_conferido_por_identidade_com_str():
    comparacoes = [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Compare)
        and any(isinstance(operador, ast.IsNot) for operador in no.ops)
    ]
    assert len(comparacoes) == 1
    (comparacao,) = comparacoes
    assert isinstance(comparacao.left, ast.Call)
    assert isinstance(comparacao.left.func, ast.Name)
    assert comparacao.left.func.id == "type"
    (comparado,) = comparacao.comparators
    assert isinstance(comparado, ast.Name)
    assert comparado.id == "str"


def test_o_rotulo_nao_e_convertido():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
            assert no.func.id not in {"str", "repr", "format", "bytes", "int"}


def test_nao_ha_captura_de_excecao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_nao_ha_raise_from():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise):
            assert no.cause is None


def test_producao_nao_menciona_caminho_de_knowledge_em_codigo():
    for constante in _constantes_de_codigo():
        assert "knowledge" not in constante
        assert ".yaml" not in constante
        assert ".md" not in constante


def test_producao_nao_declara_enum_nem_dataclass():
    proibidos = {"Enum", "StrEnum", "dataclass", "NamedTuple", "TypedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_producao_declara_uma_unica_classe():
    classes = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)
    ]
    assert [classe.name for classe in classes] == ["StatusNaoCanonicalizavel"]


def test_producao_declara_duas_funcoes_uma_publica():
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert funcoes == ["canonicalizar_status", "_nao_canonicalizavel"]


def test_nao_ha_estado_mutavel_no_modulo():
    from casa77_sdr import response_status

    for nome, valor in vars(response_status).items():
        if nome.startswith("__") and nome.endswith("__"):
            continue
        if nome == "annotations":
            continue
        assert not isinstance(valor, (list, dict, set, bytearray))


def test_nao_ha_nome_publico_fora_de_all():
    from casa77_sdr import response_status

    publicos = {
        nome
        for nome in vars(response_status)
        if not nome.startswith("_") and nome != "annotations"
    }
    assert publicos == set(response_status.__all__)


def test_a_tabela_privada_e_imutavel_e_tem_tres_linhas():
    from casa77_sdr import response_status

    tabela = response_status._TRADUCOES_AUTOMATICAS
    assert isinstance(tabela, tuple)
    assert len(tabela) == 3
    for linha in tabela:
        assert isinstance(linha, tuple)
        assert len(linha) == 2
        assert all(type(campo) is str for campo in linha)


def test_a_tabela_privada_corresponde_as_tres_linhas_arbitradas():
    from casa77_sdr import response_status

    assert response_status._TRADUCOES_AUTOMATICAS == TRADUCOES


def test_nao_ha_api_publica_de_mutacao():
    from casa77_sdr import response_status

    for nome, valor in vars(response_status).items():
        if nome.startswith("_"):
            continue
        if not callable(valor):
            continue
        if isinstance(valor, type):
            continue
        assert nome == "canonicalizar_status"


# ---------------------------------------------------------------------------
# J. Determinismo e imutabilidade da entrada
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_chamadas_repetidas_devolvem_o_mesmo_resultado(rotulo, esperado):
    assert [canonicalizar_status(rotulo) for _ in range(20)] == [esperado] * 20


def test_ordem_das_chamadas_nao_altera_o_resultado():
    direta = [canonicalizar_status(rotulo) for rotulo, _ in TRADUCOES]
    inversa = [canonicalizar_status(rotulo) for rotulo, _ in reversed(TRADUCOES)]
    assert direta == list(reversed(inversa))


def test_falha_e_deterministica_sob_repeticao():
    mensagens = []
    for _ in range(20):
        with pytest.raises(StatusNaoCanonicalizavel) as erro:
            canonicalizar_status("PARCIAL")
        mensagens.append(str(erro.value))
    assert mensagens == [MENSAGEM_NAO_MAPEADO] * 20


def test_sucesso_e_falha_intercalados_nao_acumulam_estado():
    for _ in range(10):
        assert canonicalizar_status(APROVADO_MD) == APROVADO_CANONICO
        with pytest.raises(StatusNaoCanonicalizavel):
            canonicalizar_status("PARCIAL")
        assert canonicalizar_status(AGUARDA_MD) == AGUARDA_CANONICO
        with pytest.raises(StatusNaoCanonicalizavel):
            canonicalizar_status(None)
    assert canonicalizar_status(HANDOFF_MD) == APROVADO_CANONICO


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert canonicalizar_status(APROVADO_MD) == APROVADO_CANONICO
    assert canonicalizar_status(AGUARDA_MD) == AGUARDA_CANONICO
    with pytest.raises(StatusNaoCanonicalizavel):
        canonicalizar_status("aprovado")


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_entrada_nao_e_alterada_no_caminho_valido(rotulo, esperado):
    copia = rotulo[:]
    canonicalizar_status(rotulo)
    assert rotulo == copia


@pytest.mark.parametrize("invalido", ["PARCIAL", "BLOQUEADO", "", " APROVADO "])
def test_entrada_nao_e_alterada_no_caminho_de_falha(invalido):
    copia = invalido[:]
    with pytest.raises(StatusNaoCanonicalizavel):
        canonicalizar_status(invalido)
    assert invalido == copia


def test_a_tabela_nao_e_alterada_pelas_chamadas():
    from casa77_sdr import response_status

    antes = response_status._TRADUCOES_AUTOMATICAS
    canonicalizar_status(APROVADO_MD)
    with pytest.raises(StatusNaoCanonicalizavel):
        canonicalizar_status("PARCIAL")
    assert response_status._TRADUCOES_AUTOMATICAS == antes
    assert response_status._TRADUCOES_AUTOMATICAS is antes
