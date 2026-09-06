"""Testes da propagação pura e determinística de status `ST1`–`ST3`.

A fronteira materializa **apenas** `SP1`–`SP3`: recebido um rótulo já
identificado e uma sequência de fragmentos **já associados pelo chamador** ao
mesmo `Rxx`, ela aplica **uniformemente** o status canônico das três traduções
automáticas de `C-A1-ST1`–`C-A1-ST3` a **todos** os fragmentos.

Estes testes provam as três traduções, a **uniformidade** de `SP3`, a
**preservação de ordem e de duplicidades**, a **opacidade** dos tokens, a
precedência fixa do canonicalizador, a categoria única `tipo_invalido`, o
silêncio da mensagem de erro e a pureza do módulo de produção — e **não**
transformam em norma a resolução de `PARCIAL`, uma quarta tradução, a leitura de
Markdown, a composição com `C8`/`C11`/`C12`, a deduplicação de identidade, a
existência do `Rxx`, a satisfação de `C-A1-ST6`–`C-A1-ST10` ou a migração da
autoridade de status, que estão **fora** desta fronteira.
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Sequence
from enum import Enum
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_status import StatusNaoCanonicalizavel
from casa77_sdr.response_status_propagation import (
    PropagacaoInvalida,
    propagar_status,
)

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

# Os rotulos acentuados sao escritos por escape para que o teste nao dependa da
# forma de normalizacao com que este arquivo foi gravado. `C7` e `C3` sao a
# cedilha e o til **compostos** (NFC); `F3` e o `o` agudo composto.
APROVADO_MD = "APROVADO"
AGUARDA_MD = "AGUARDA APROVAÇÃO"
HANDOFF_MD = "APROVADO com handoff obrigatório"

# Imagens canonicas de `C-3` alcancaveis por traducao automatica.
APROVADO_CANONICO = "APROVADO"
AGUARDA_CANONICO = "AGUARDA_APROVACAO"

# As tres traducoes arbitradas, e nenhuma quarta.
TRADUCOES = (
    (APROVADO_MD, APROVADO_CANONICO),
    (AGUARDA_MD, AGUARDA_CANONICO),
    (HANDOFF_MD, APROVADO_CANONICO),
)

# Mesmas cadeias em forma decomposta (NFD) e com espaco inquebravel.
AGUARDA_MD_NFD = "AGUARDA APROVAÇÃO"
HANDOFF_MD_NFD = "APROVADO com handoff obrigatório"
AGUARDA_MD_NBSP = "AGUARDA APROVAÇÃO"
HANDOFF_MD_NBSP = "APROVADO com handoff obrigatório"

CATEGORIA = "tipo_invalido"
LOCALIZADORES = ("fragmentos", "fragmentos.item")

MENSAGEM_CONTENTOR = "tipo_invalido: fragmentos"
MENSAGEM_ITEM = "tipo_invalido: fragmentos.item"

# Mensagens que pertencem ao canonicalizador, e que sobem intactas por aqui.
MENSAGEM_ROTULO_TIPO = "tipo_invalido: rotulo"
MENSAGEM_ROTULO_NAO_MAPEADO = "rotulo_nao_mapeado: rotulo"

# Tokens opacos: nenhum deles tem a sua forma interpretada pela fronteira.
TOKENS_OPACOS = (
    "",
    "abc",
    "R01/F1",
    "a/b/c",
    "/",
    "//",
    "R01",
    "R01/",
    "/F1",
    "R99/fábio",
    "ção",
    "\U0001f600",
    " ",
    "\t",
    "\n",
    " R01/F1 ",
    "APROVADO",
    "AGUARDA_APROVACAO",
    "PARCIAL",
    "R01/F1/F2",
    "R01\\F1",
)

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_status_propagation.py"
)
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)


class TokenPermissivo(str):
    """Subclasse de `str` que sequestra a igualdade e o hash.

    Ela se declara igual a qualquer coisa. Aceitá-la entregaria ao chamador a
    semântica de identidade que esta fronteira precisa manter nativa — mesmo que
    aqui a identidade nem sequer seja julgada.
    """

    def __eq__(self, outro: object) -> bool:
        return True

    def __ne__(self, outro: object) -> bool:
        return False

    def __hash__(self) -> int:
        return hash(APROVADO_CANONICO)


class TokenSimples(str):
    """Subclasse de `str` que nada redefine. Ainda assim, não é `str` exata."""


class ObjetoComStr:
    """Objeto que **parece** um token quando convertido — e nunca é convertido."""

    def __str__(self) -> str:
        return "R01/F1"

    def __repr__(self) -> str:
        return "R01/F1"


class TokenEnum(str, Enum):
    """Enum de `str`: o tipo concreto é o enum, nunca `str` exata."""

    UM = "R01/F1"


class SequenciaDeTokens(Sequence):
    """`Sequence` própria: prova que o contêiner é decidido pela ABC, não pelo tipo."""

    def __init__(self, itens):
        self._itens = tuple(itens)

    def __getitem__(self, indice):
        return self._itens[indice]

    def __len__(self) -> int:
        return len(self._itens)


class QuaseSequencia:
    """Tem `__getitem__` e `__len__`, mas **não** é uma `Sequence` registrada."""

    def __init__(self, itens):
        self._itens = tuple(itens)

    def __getitem__(self, indice):
        return self._itens[indice]

    def __len__(self) -> int:
        return len(self._itens)


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
# A. `ST1`-`ST3` — as tres traducoes, e a imagem exata
# ---------------------------------------------------------------------------


def test_st1_propaga_aprovado():
    assert propagar_status(APROVADO_MD, ["R01/F1"]) == (("R01/F1", "APROVADO"),)


def test_st2_propaga_aguarda_aprovacao():
    assert propagar_status(AGUARDA_MD, ["R01/F1"]) == (
        ("R01/F1", "AGUARDA_APROVACAO"),
    )


def test_st3_propaga_aprovado():
    assert propagar_status(HANDOFF_MD, ["R01/F1"]) == (("R01/F1", "APROVADO"),)


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_as_tres_traducoes_produzem_a_imagem_exata(rotulo, esperado):
    pares = propagar_status(rotulo, ["a", "b"])
    assert pares == (("a", esperado), ("b", esperado))


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_imagem_esta_no_vocabulario_fechado_de_c3(rotulo, esperado):
    assert esperado in {"APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO"}
    assert propagar_status(rotulo, ["x"])[0][1] == esperado


def test_st1_e_st3_compartilham_a_mesma_imagem():
    assert propagar_status(APROVADO_MD, ["x"]) == propagar_status(HANDOFF_MD, ["x"])


def test_nenhuma_imagem_bloqueado_e_produzida():
    for rotulo, _ in TRADUCOES:
        for _, status in propagar_status(rotulo, list(TOKENS_OPACOS)):
            assert status != "BLOQUEADO"


def test_nenhuma_quarta_traducao_existe():
    """Entre candidatos plausíveis, exatamente três rótulos propagam."""
    candidatos = (
        APROVADO_MD,
        AGUARDA_MD,
        HANDOFF_MD,
        "PARCIAL",
        "BLOQUEADO",
        "AGUARDA_APROVACAO",
        "APROVADA",
        "aprovado",
        "",
        "APROVADO com handoff",
        "APROVADO COM HANDOFF OBRIGATÓRIO",
    )
    aceitos = []
    for candidato in candidatos:
        try:
            propagar_status(candidato, ["x"])
        except StatusNaoCanonicalizavel:
            continue
        aceitos.append(candidato)
    assert aceitos == [APROVADO_MD, AGUARDA_MD, HANDOFF_MD]


def test_a_traducao_e_delegada_e_nao_reimplementada():
    """A imagem devolvida é exatamente a de `canonicalizar_status`."""
    from casa77_sdr.response_status import canonicalizar_status

    for rotulo, _ in TRADUCOES:
        esperado = canonicalizar_status(rotulo)
        assert propagar_status(rotulo, ["x"]) == (("x", esperado),)


def test_producao_nao_tem_tabela_local_de_traducao():
    for constante in _constantes_de_codigo():
        assert constante != APROVADO_MD
        assert constante != AGUARDA_MD
        assert constante != HANDOFF_MD
        assert constante != AGUARDA_CANONICO
        assert "APROVA" not in constante
        assert "BLOQUEADO" not in constante
        assert "PARCIAL" not in constante


# ---------------------------------------------------------------------------
# B. Handoff — `ST3` nao transporta instrucao operacional
# ---------------------------------------------------------------------------


def test_st3_nao_transporta_o_sufixo_de_handoff():
    pares = propagar_status(HANDOFF_MD, ["R01/F1", "R01/F2"])
    for token, status in pares:
        assert status == APROVADO_CANONICO
        assert "handoff" not in status
        assert "obrigat" not in status
        assert token in {"R01/F1", "R01/F2"}


def test_st3_e_st1_sao_indistinguiveis_na_saida():
    tokens = ["a", "b", "c"]
    assert propagar_status(HANDOFF_MD, tokens) == propagar_status(APROVADO_MD, tokens)


def test_o_handoff_nao_cria_par_extra():
    assert len(propagar_status(HANDOFF_MD, ["a", "b"])) == 2


# ---------------------------------------------------------------------------
# C. Quantidade — zero, um, dois, varios
# ---------------------------------------------------------------------------


def test_sequencia_vazia_devolve_tupla_vazia():
    assert propagar_status(APROVADO_MD, []) == ()


def test_tupla_vazia_tambem_devolve_tupla_vazia():
    assert propagar_status(AGUARDA_MD, ()) == ()


def test_sequencia_propria_vazia_devolve_tupla_vazia():
    assert propagar_status(HANDOFF_MD, SequenciaDeTokens(())) == ()


def test_um_fragmento():
    assert propagar_status(APROVADO_MD, ["u"]) == (("u", APROVADO_CANONICO),)


def test_dois_fragmentos():
    assert propagar_status(AGUARDA_MD, ["u", "v"]) == (
        ("u", AGUARDA_CANONICO),
        ("v", AGUARDA_CANONICO),
    )


@pytest.mark.parametrize("quantidade", [3, 4, 7, 37, 200])
def test_varios_fragmentos(quantidade):
    tokens = [f"R01/F{numero}" for numero in range(quantidade)]
    pares = propagar_status(APROVADO_MD, tokens)
    assert len(pares) == quantidade
    assert [token for token, _ in pares] == tokens


def test_cardinalidade_da_saida_e_a_da_entrada():
    for quantidade in range(0, 12):
        tokens = ["t"] * quantidade
        assert len(propagar_status(APROVADO_MD, tokens)) == quantidade


def test_sequencia_vazia_nao_prova_que_um_rxx_possa_nao_ter_fragmentos():
    """A tupla vazia afirma somente que nada foi recebido."""
    assert propagar_status(APROVADO_MD, []) == ()
    assert propagar_status(APROVADO_MD, ["R01/F1"]) != ()


# ---------------------------------------------------------------------------
# D. Ordem preservada
# ---------------------------------------------------------------------------


def test_ordem_da_entrada_e_preservada():
    tokens = ["c", "a", "b"]
    assert [token for token, _ in propagar_status(APROVADO_MD, tokens)] == tokens


def test_ordem_nao_e_alfabetica():
    pares = propagar_status(APROVADO_MD, ["z", "a"])
    assert pares[0][0] == "z"
    assert pares[1][0] == "a"


def test_ordem_inversa_produz_saida_inversa():
    tokens = ["a", "b", "c", "d"]
    direta = propagar_status(AGUARDA_MD, tokens)
    inversa = propagar_status(AGUARDA_MD, list(reversed(tokens)))
    assert direta == tuple(reversed(inversa))


def test_ordem_e_preservada_com_sequencia_propria():
    tokens = ("m", "n", "o")
    pares = propagar_status(APROVADO_MD, SequenciaDeTokens(tokens))
    assert tuple(token for token, _ in pares) == tokens


def test_ordem_e_preservada_com_tokens_opacos():
    tokens = list(TOKENS_OPACOS)
    pares = propagar_status(HANDOFF_MD, tokens)
    assert [token for token, _ in pares] == tokens


# ---------------------------------------------------------------------------
# E. Uniformidade — `SP3`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_todos_os_fragmentos_recebem_o_mesmo_status(rotulo, esperado):
    pares = propagar_status(rotulo, list(TOKENS_OPACOS))
    assert {status for _, status in pares} == {esperado}


def test_o_status_nao_depende_da_posicao():
    pares = propagar_status(AGUARDA_MD, ["a", "b", "c", "d", "e"])
    assert all(status == AGUARDA_CANONICO for _, status in pares)


def test_o_status_nao_depende_do_conteudo_do_token():
    tokens = ["APROVADO", "BLOQUEADO", "PARCIAL", "AGUARDA APROVAÇÃO"]
    pares = propagar_status(AGUARDA_MD, tokens)
    assert {status for _, status in pares} == {AGUARDA_CANONICO}


def test_o_status_nao_depende_da_quantidade():
    for quantidade in (1, 2, 5, 50):
        pares = propagar_status(AGUARDA_MD, ["t"] * quantidade)
        assert {status for _, status in pares} == {AGUARDA_CANONICO}


def test_o_status_nao_depende_da_ordem():
    tokens = ["x", "y", "z"]
    direta = {status for _, status in propagar_status(APROVADO_MD, tokens)}
    inversa = {
        status for _, status in propagar_status(APROVADO_MD, list(reversed(tokens)))
    }
    assert direta == inversa == {APROVADO_CANONICO}


def test_o_status_e_o_mesmo_objeto_para_todos_os_pares():
    """Nenhum par recebe uma imagem construída à parte."""
    pares = propagar_status(AGUARDA_MD, ["a", "b", "c"])
    primeiro = pares[0][1]
    for _, status in pares:
        assert status is primeiro


def test_a_sequencia_so_determina_quais_tokens_e_em_que_ordem():
    tokens = ["a", "b"]
    pares = propagar_status(APROVADO_MD, tokens)
    assert [token for token, _ in pares] == tokens
    assert {status for _, status in pares} == {APROVADO_CANONICO}


# ---------------------------------------------------------------------------
# F. Fail-closed do rotulo — `StatusNaoCanonicalizavel` intacta
# ---------------------------------------------------------------------------


ROTULOS_NAO_MAPEADOS = (
    "PARCIAL",
    "BLOQUEADO",
    "AGUARDA_APROVACAO",
    "",
    "aprovado",
    "Aprovado",
    "APROVADo",
    "AGUARDA APROVACAO",
    "AGUARDA APROVAÇAO",
    "APROVADO com handoff obrigatorio",
    " APROVADO",
    "APROVADO ",
    "APROVADO\n",
    "AGUARDA  APROVAÇÃO",
    AGUARDA_MD_NBSP,
    HANDOFF_MD_NBSP,
    AGUARDA_MD_NFD,
    HANDOFF_MD_NFD,
    "APROVADO com handoff",
    "handoff obrigatório",
)

ROTULOS_DE_TIPO_INVALIDO = (
    None,
    1,
    0,
    True,
    b"APROVADO",
    bytearray(b"APROVADO"),
    ["APROVADO"],
    ("APROVADO",),
    {"APROVADO"},
    3.5,
    ObjetoComStr(),
    TokenEnum.UM,
)


@pytest.mark.parametrize("rotulo", ROTULOS_NAO_MAPEADOS)
def test_rotulo_sem_traducao_automatica_falha_no_canonicalizador(rotulo):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status(rotulo, ["R01/F1"])
    assert str(erro.value) == MENSAGEM_ROTULO_NAO_MAPEADO


@pytest.mark.parametrize("rotulo", ROTULOS_DE_TIPO_INVALIDO)
def test_rotulo_de_tipo_invalido_falha_no_canonicalizador(rotulo):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status(rotulo, ["R01/F1"])
    assert str(erro.value) == MENSAGEM_ROTULO_TIPO


def test_subclasse_de_str_como_rotulo_e_recusada_por_tipo():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status(TokenSimples(APROVADO_MD), ["R01/F1"])
    assert str(erro.value) == MENSAGEM_ROTULO_TIPO


def test_subclasse_permissiva_como_rotulo_nao_sequestra_a_tabela():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status(TokenPermissivo("qualquer"), ["R01/F1"])
    assert str(erro.value) == MENSAGEM_ROTULO_TIPO


@pytest.mark.parametrize("rotulo", ROTULOS_NAO_MAPEADOS + ROTULOS_DE_TIPO_INVALIDO)
def test_a_excecao_do_canonicalizador_sobe_com_a_classe_exata(rotulo):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status(rotulo, ["R01/F1"])
    assert type(erro.value) is StatusNaoCanonicalizavel


@pytest.mark.parametrize("rotulo", ["PARCIAL", "BLOQUEADO", "", None, 1])
def test_a_excecao_do_canonicalizador_sobe_sem_cause_nem_context(rotulo):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status(rotulo, ["R01/F1"])
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None
    assert erro.value.__suppress_context__ is False


@pytest.mark.parametrize("rotulo", ["PARCIAL", "BLOQUEADO", None])
def test_a_excecao_do_canonicalizador_carrega_um_unico_argumento(rotulo):
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status(rotulo, ["R01/F1"])
    assert len(erro.value.args) == 1


def test_a_mensagem_do_canonicalizador_nao_e_enriquecida():
    """A fronteira não acrescenta localizador, token, contagem ou contexto."""
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status("PARCIAL", ["R01/F1", "R01/F2"])
    mensagem = str(erro.value)
    assert mensagem == MENSAGEM_ROTULO_NAO_MAPEADO
    assert "fragmentos" not in mensagem
    assert "R01" not in mensagem
    assert "2" not in mensagem


def test_a_excecao_do_canonicalizador_nao_e_reclassificada():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status("PARCIAL", ["R01/F1"])
    assert not isinstance(erro.value, PropagacaoInvalida)


def test_a_mensagem_do_canonicalizador_e_identica_a_dele():
    from casa77_sdr.response_status import canonicalizar_status

    for rotulo in ("PARCIAL", "BLOQUEADO", "", None, 1):
        with pytest.raises(StatusNaoCanonicalizavel) as direto:
            canonicalizar_status(rotulo)
        with pytest.raises(StatusNaoCanonicalizavel) as pela_propagacao:
            propagar_status(rotulo, ["x"])
        assert str(pela_propagacao.value) == str(direto.value)


# ---------------------------------------------------------------------------
# G. `PARCIAL` — nao resolvido, e falha daquela invocacao
# ---------------------------------------------------------------------------


def test_parcial_nao_recebe_traducao_automatica():
    with pytest.raises(StatusNaoCanonicalizavel):
        propagar_status("PARCIAL", ["R01/F1"])


def test_parcial_nao_vira_quarto_status():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status("PARCIAL", ["R01/F1"])
    assert "PARCIAL" not in str(erro.value)


def test_parcial_nao_e_capturado_nem_convertido():
    with pytest.raises(StatusNaoCanonicalizavel):
        propagar_status("PARCIAL", [])
    with pytest.raises(StatusNaoCanonicalizavel):
        propagar_status("PARCIAL", ["a", "b", "c"])


def test_parcial_falha_da_invocacao_e_nao_veredito_de_documento():
    """A recusa de uma chamada não contamina outra: não há estado global."""
    with pytest.raises(StatusNaoCanonicalizavel):
        propagar_status("PARCIAL", ["R01/F1"])
    assert propagar_status(APROVADO_MD, ["R01/F1"]) == (("R01/F1", APROVADO_CANONICO),)


def test_producao_nao_menciona_parcial_em_codigo():
    assert "PARCIAL" not in NOMES_PRODUCAO
    for constante in _constantes_de_codigo():
        assert "PARCIAL" not in constante


# ---------------------------------------------------------------------------
# H. Tipo do contentor
# ---------------------------------------------------------------------------


CONTENTORES_INVALIDOS = (
    "abc",
    "",
    "R01/F1",
    b"abc",
    b"",
    bytearray(b"abc"),
    1,
    0,
    None,
    True,
    3.5,
    {"a"},
    frozenset({"a"}),
    {"a": "b"},
    object(),
    QuaseSequencia(("a",)),
)


@pytest.mark.parametrize("invalido", CONTENTORES_INVALIDOS)
def test_contentor_invalido_e_recusado(invalido):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, invalido)
    assert str(erro.value) == MENSAGEM_CONTENTOR


def test_gerador_nao_e_sequencia():
    gerador = (token for token in ("a", "b"))
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, gerador)
    assert str(erro.value) == MENSAGEM_CONTENTOR


def test_iterador_nao_e_sequencia():
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, iter(["a"]))
    assert str(erro.value) == MENSAGEM_CONTENTOR


def test_str_vazia_tambem_e_recusada_como_contentor():
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, "")
    assert str(erro.value) == MENSAGEM_CONTENTOR


def test_str_nao_e_decomposta_em_caracteres():
    """`"ab"` não vira dois fragmentos: os elementos de uma `str` não são tokens."""
    with pytest.raises(PropagacaoInvalida):
        propagar_status(APROVADO_MD, "ab")


@pytest.mark.parametrize("valido", [[], (), ["a"], ("a", "b")])
def test_list_e_tuple_sao_contentores_validos(valido):
    assert len(propagar_status(APROVADO_MD, valido)) == len(valido)


def test_sequencia_propria_e_contentor_valido():
    pares = propagar_status(APROVADO_MD, SequenciaDeTokens(("a", "b")))
    assert pares == (("a", APROVADO_CANONICO), ("b", APROVADO_CANONICO))


# ---------------------------------------------------------------------------
# I. Tipo dos elementos
# ---------------------------------------------------------------------------


ELEMENTOS_INVALIDOS = (
    1,
    0,
    None,
    True,
    3.5,
    b"a",
    bytearray(b"a"),
    ["a"],
    ("a",),
    {"a"},
    {"a": "b"},
    object(),
    ObjetoComStr(),
    TokenEnum.UM,
    TokenSimples("a"),
    TokenPermissivo("a"),
)


@pytest.mark.parametrize("invalido", ELEMENTOS_INVALIDOS)
def test_elemento_invalido_e_recusado(invalido):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, [invalido])
    assert str(erro.value) == MENSAGEM_ITEM


@pytest.mark.parametrize("invalido", ELEMENTOS_INVALIDOS)
def test_elemento_invalido_e_recusado_mesmo_acompanhado(invalido):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, ["a", invalido, "b"])
    assert str(erro.value) == MENSAGEM_ITEM


def test_subclasse_de_str_como_elemento_e_recusada():
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, [TokenSimples("R01/F1")])
    assert str(erro.value) == MENSAGEM_ITEM


def test_subclasse_permissiva_nao_se_faz_passar_por_str():
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, [TokenPermissivo("R01/F1")])
    assert str(erro.value) == MENSAGEM_ITEM


def test_str_normal_com_o_mesmo_conteudo_da_subclasse_e_aceita():
    assert propagar_status(APROVADO_MD, ["R01/F1"]) == (
        ("R01/F1", APROVADO_CANONICO),
    )


def test_elemento_invalido_no_fim_tambem_e_alcancado():
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, ["a", "b", "c", 1])
    assert str(erro.value) == MENSAGEM_ITEM


def test_nada_e_devolvido_parcialmente():
    """A validação percorre tudo antes da montagem; não há saída parcial."""
    with pytest.raises(PropagacaoInvalida):
        propagar_status(APROVADO_MD, ["a", "b", None])


def test_contentor_invalido_prevalece_sobre_elementos():
    """`str` falha como contêiner, e não como elemento."""
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, "abc")
    assert str(erro.value) == MENSAGEM_CONTENTOR


# ---------------------------------------------------------------------------
# J. Taxonomia — categoria unica e mensagem muda
# ---------------------------------------------------------------------------


CASOS_DE_ERRO = (
    ("abc", MENSAGEM_CONTENTOR),
    (b"abc", MENSAGEM_CONTENTOR),
    (bytearray(b"abc"), MENSAGEM_CONTENTOR),
    (1, MENSAGEM_CONTENTOR),
    (None, MENSAGEM_CONTENTOR),
    ({"a"}, MENSAGEM_CONTENTOR),
    ([1], MENSAGEM_ITEM),
    ([None], MENSAGEM_ITEM),
    ([b"a"], MENSAGEM_ITEM),
    ([TokenSimples("a")], MENSAGEM_ITEM),
)


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_tem_categoria_e_localizador_fechados(entrada, mensagem):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, entrada)
    assert str(erro.value) == mensagem
    categoria, _, localizador = mensagem.partition(": ")
    assert categoria == CATEGORIA
    assert localizador in LOCALIZADORES


def test_existe_uma_unica_categoria():
    assert {mensagem.split(": ")[0] for _, mensagem in CASOS_DE_ERRO} == {CATEGORIA}


def test_existem_exatamente_dois_localizadores():
    assert {mensagem.split(": ")[1] for _, mensagem in CASOS_DE_ERRO} == set(
        LOCALIZADORES
    )


def test_as_duas_mensagens_declaradas_sao_alcancaveis():
    alcancadas = set()
    for entrada, _ in CASOS_DE_ERRO:
        with pytest.raises(PropagacaoInvalida) as erro:
            propagar_status(APROVADO_MD, entrada)
        alcancadas.add(str(erro.value))
    assert alcancadas == {MENSAGEM_CONTENTOR, MENSAGEM_ITEM}


def test_nenhuma_terceira_mensagem_e_produzida():
    entradas = list(CONTENTORES_INVALIDOS) + [[item] for item in ELEMENTOS_INVALIDOS]
    for entrada in entradas:
        with pytest.raises(PropagacaoInvalida) as erro:
            propagar_status(APROVADO_MD, entrada)
        assert str(erro.value) in {MENSAGEM_CONTENTOR, MENSAGEM_ITEM}


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_token_rotulo_nem_conteudo(entrada, mensagem):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(HANDOFF_MD, entrada)
    texto = str(erro.value)
    assert "APROVADO" not in texto
    assert "handoff" not in texto
    assert "abc" not in texto
    assert "R01" not in texto


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_o_tipo_concreto(entrada, mensagem):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, entrada)
    texto = str(erro.value)
    for proibido in ("int", "NoneType", "bytes", "bytearray", "set", "list", "str"):
        assert proibido not in texto


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_tem_numero_indice_nem_cardinalidade(entrada, mensagem):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, entrada)
    assert not any(caractere.isdigit() for caractere in str(erro.value))


def test_mensagem_nao_muda_com_a_posicao_do_defeito():
    mensagens = []
    for entrada in ([1, "a", "a"], ["a", 1, "a"], ["a", "a", 1]):
        with pytest.raises(PropagacaoInvalida) as erro:
            propagar_status(APROVADO_MD, entrada)
        mensagens.append(str(erro.value))
    assert mensagens == [MENSAGEM_ITEM] * 3


def test_mensagem_nao_muda_com_a_quantidade_de_defeitos():
    mensagens = []
    for entrada in ([1], [1, 2], [1, 2, 3, 4]):
        with pytest.raises(PropagacaoInvalida) as erro:
            propagar_status(APROVADO_MD, entrada)
        mensagens.append(str(erro.value))
    assert mensagens == [MENSAGEM_ITEM] * 3


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_mensagem_nao_tem_repr(entrada, mensagem):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, entrada)
    texto = str(erro.value)
    for proibido in ("<", ">", "'", '"', "[", "]", "(", ")", "{", "}"):
        assert proibido not in texto


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_propagacao_invalida_nao_tem_cause_nem_context(entrada, mensagem):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, entrada)
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None
    assert erro.value.__suppress_context__ is False


@pytest.mark.parametrize("entrada, mensagem", CASOS_DE_ERRO)
def test_propagacao_invalida_carrega_um_unico_argumento(entrada, mensagem):
    with pytest.raises(PropagacaoInvalida) as erro:
        propagar_status(APROVADO_MD, entrada)
    assert erro.value.args == (mensagem,)


# ---------------------------------------------------------------------------
# K. Precedencia — o canonicalizador vence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rotulo", ["PARCIAL", "BLOQUEADO", "", "aprovado"])
@pytest.mark.parametrize("fragmentos", ["abc", 1, None, {"a"}, [1], [None]])
def test_rotulo_invalido_vence_fragmentos_invalidos(rotulo, fragmentos):
    with pytest.raises(StatusNaoCanonicalizavel):
        propagar_status(rotulo, fragmentos)


@pytest.mark.parametrize("rotulo", [None, 1, b"APROVADO", TokenSimples("APROVADO")])
@pytest.mark.parametrize("fragmentos", ["abc", 1, None, [1]])
def test_rotulo_de_tipo_invalido_vence_fragmentos_invalidos(rotulo, fragmentos):
    with pytest.raises(StatusNaoCanonicalizavel):
        propagar_status(rotulo, fragmentos)


def test_com_ambos_invalidos_nunca_se_ve_propagacao_invalida():
    with pytest.raises(StatusNaoCanonicalizavel) as erro:
        propagar_status("PARCIAL", 1)
    assert not isinstance(erro.value, PropagacaoInvalida)


def test_com_rotulo_valido_o_fragmento_invalido_e_alcancado():
    with pytest.raises(PropagacaoInvalida):
        propagar_status(APROVADO_MD, 1)


def test_a_primeira_operacao_funcional_e_a_canonicalizacao():
    """No corpo público, a primeira instrução chama `canonicalizar_status`."""
    funcao = next(
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.FunctionDef) and no.name == "propagar_status"
    )
    corpo = [no for no in funcao.body if not isinstance(no, ast.Expr)]
    primeira = corpo[0]
    assert isinstance(primeira, ast.Assign)
    assert isinstance(primeira.value, ast.Call)
    assert isinstance(primeira.value.func, ast.Name)
    assert primeira.value.func.id == "canonicalizar_status"


def test_nenhuma_validacao_de_fragmentos_precede_a_canonicalizacao():
    funcao = next(
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.FunctionDef) and no.name == "propagar_status"
    )
    corpo = [no for no in funcao.body if not isinstance(no, ast.Expr)]
    assert not isinstance(corpo[0], (ast.If, ast.For, ast.While, ast.Raise))


# ---------------------------------------------------------------------------
# L. Duplicidade — preservada, nunca deduplicada
# ---------------------------------------------------------------------------


def test_token_repetido_produz_dois_pares():
    assert propagar_status(APROVADO_MD, ("x", "x")) == (
        ("x", APROVADO_CANONICO),
        ("x", APROVADO_CANONICO),
    )


def test_duplicidade_nao_e_erro():
    assert len(propagar_status(AGUARDA_MD, ["x"] * 5)) == 5


def test_duplicidade_preserva_a_ordem_das_repeticoes():
    tokens = ["a", "b", "a", "b", "a"]
    assert [token for token, _ in propagar_status(APROVADO_MD, tokens)] == tokens


def test_saida_nao_e_um_conjunto_nem_um_mapa():
    pares = propagar_status(APROVADO_MD, ["x", "x"])
    assert isinstance(pares, tuple)
    assert not isinstance(pares, (set, frozenset, dict))
    assert len(pares) == 2


def test_todos_repetidos_produzem_a_mesma_cardinalidade():
    for quantidade in (1, 2, 3, 10):
        assert len(propagar_status(APROVADO_MD, ["igual"] * quantidade)) == quantidade


def test_a_unicidade_de_identidade_nao_e_julgada():
    """Tokens iguais convivem; a fronteira não decide unicidade global."""
    pares = propagar_status(HANDOFF_MD, ["R01/F1", "R01/F1", "R01/F1"])
    assert pares == (("R01/F1", APROVADO_CANONICO),) * 3


# ---------------------------------------------------------------------------
# M. Opacidade dos tokens
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("token", TOKENS_OPACOS)
def test_qualquer_str_e_aceita_como_token(token):
    assert propagar_status(APROVADO_MD, [token]) == ((token, APROVADO_CANONICO),)


def test_token_vazio_e_aceito():
    assert propagar_status(APROVADO_MD, [""]) == (("", APROVADO_CANONICO),)


def test_token_sem_separador_e_aceito():
    assert propagar_status(APROVADO_MD, ["abc"]) == (("abc", APROVADO_CANONICO),)


def test_token_com_varios_separadores_e_aceito():
    assert propagar_status(APROVADO_MD, ["a/b/c"]) == (("a/b/c", APROVADO_CANONICO),)


def test_token_nao_e_decomposto():
    pares = propagar_status(APROVADO_MD, ["R01/F1"])
    assert pares[0][0] == "R01/F1"
    assert len(pares) == 1


def test_token_nao_e_normalizado():
    variantes = [
        " R01/F1 ",
        "r01/f1",
        "R01 /F1",
        "R01/F1",
        "AGUARDA APROVAÇÃO",
    ]
    pares = propagar_status(APROVADO_MD, variantes)
    assert [token for token, _ in pares] == variantes


def test_token_que_parece_rotulo_nao_e_reinterpretado():
    pares = propagar_status(AGUARDA_MD, ["APROVADO", HANDOFF_MD, "PARCIAL"])
    assert {status for _, status in pares} == {AGUARDA_CANONICO}


def test_token_unicode_e_preservado_caractere_a_caractere():
    token = "R01/fábio\U0001f600"
    devolvido = propagar_status(APROVADO_MD, [token])[0][0]
    assert devolvido == token
    assert list(devolvido) == list(token)


def test_o_token_devolvido_e_o_mesmo_objeto_recebido():
    token = "R01/F1"
    assert propagar_status(APROVADO_MD, [token])[0][0] is token


# ---------------------------------------------------------------------------
# N. Forma da saida
# ---------------------------------------------------------------------------


def test_saida_e_tupla_de_tuplas():
    pares = propagar_status(APROVADO_MD, ["a", "b"])
    assert isinstance(pares, tuple)
    for par in pares:
        assert type(par) is tuple
        assert len(par) == 2
        assert all(type(campo) is str for campo in par)


def test_saida_nao_e_tupla_paralela_de_status():
    pares = propagar_status(APROVADO_MD, ["a", "b"])
    assert pares == (("a", APROVADO_CANONICO), ("b", APROVADO_CANONICO))
    assert pares != (("a", "b"), (APROVADO_CANONICO, APROVADO_CANONICO))


def test_o_fragmento_vem_antes_do_status():
    par = propagar_status(AGUARDA_MD, ["R01/F1"])[0]
    assert par[0] == "R01/F1"
    assert par[1] == AGUARDA_CANONICO


def test_a_anotacao_de_retorno_e_tupla_de_pares():
    assinatura = inspect.signature(propagar_status)
    assert assinatura.return_annotation == "tuple[tuple[str, str], ...]"


# ---------------------------------------------------------------------------
# O. Contrato publico
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_dois_nomes():
    from casa77_sdr import response_status_propagation

    assert response_status_propagation.__all__ == [
        "PropagacaoInvalida",
        "propagar_status",
    ]


def test_nao_ha_nome_publico_fora_de_all():
    from casa77_sdr import response_status_propagation

    publicos = {
        nome
        for nome in vars(response_status_propagation)
        if not nome.startswith("_")
        and nome not in {"annotations", "Sequence", "canonicalizar_status"}
    }
    assert publicos == set(response_status_propagation.__all__)


def test_assinatura_tem_dois_parametros_sem_default():
    assinatura = inspect.signature(propagar_status)
    assert list(assinatura.parameters) == ["rotulo", "fragmentos"]
    for parametro in assinatura.parameters.values():
        assert parametro.default is inspect.Parameter.empty
        assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_assinatura_nao_tem_parametro_de_contexto_ou_tolerancia():
    assinatura = inspect.signature(propagar_status)
    proibidos = {
        "caminho",
        "arquivo",
        "modo",
        "tolerancia",
        "config",
        "indice",
        "texto",
        "markdown",
        "rxx",
        "documento",
        "estrito",
    }
    assert not proibidos & set(assinatura.parameters)


def test_excecao_deriva_diretamente_de_exception():
    assert PropagacaoInvalida.__bases__ == (Exception,)


def test_excecao_nao_tem_relacao_com_a_do_canonicalizador():
    assert not issubclass(PropagacaoInvalida, StatusNaoCanonicalizavel)
    assert not issubclass(StatusNaoCanonicalizavel, PropagacaoInvalida)


def test_excecao_nao_e_subclasse_de_outro_erro_do_projeto():
    from casa77_sdr.response_bijection import BijecaoInvalida
    from casa77_sdr.response_index import IndiceInvalido

    for outra in (BijecaoInvalida, IndiceInvalido, StatusNaoCanonicalizavel):
        assert not issubclass(PropagacaoInvalida, outra)
        assert not issubclass(outra, PropagacaoInvalida)


def test_nao_e_exportado_pelo_pacote():
    assert not hasattr(casa77_sdr, "propagar_status")
    assert not hasattr(casa77_sdr, "PropagacaoInvalida")
    assert "propagar_status" not in getattr(casa77_sdr, "__all__", [])
    assert "PropagacaoInvalida" not in getattr(casa77_sdr, "__all__", [])


def test_modulo_nao_expoe_outra_funcao_publica():
    from casa77_sdr import response_status_propagation

    for nome, valor in vars(response_status_propagation).items():
        if nome.startswith("_") or isinstance(valor, type):
            continue
        if not callable(valor):
            continue
        assert nome in {"propagar_status", "canonicalizar_status"}


# ---------------------------------------------------------------------------
# P. Pureza do modulo de producao
# ---------------------------------------------------------------------------


def test_imports_sao_exatamente_os_tres_permitidos():
    assert not [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert [no.module for no in de_onde] == [
        "__future__",
        "collections.abc",
        "casa77_sdr.response_status",
    ]
    importados = [alias.name for no in de_onde for alias in no.names]
    assert importados == ["annotations", "Sequence", "canonicalizar_status"]


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_nao_importa_markdown_nem_c8_c11_c12():
    proibidos = {
        "response_markdown_units",
        "response_emittable_text",
        "response_header_labels",
        "response_index",
        "response_index_tokens",
        "response_bijection",
        "response_correspondence",
        "response_equivalence",
        "ler_unidades_marcadas",
        "extrair_textos_emitiveis",
        "extrair_rotulos_de_cabecalho",
        "derivar_tokens_do_indice",
        "validar_bijecao",
        "validar_indice",
    }
    assert not proibidos & NOMES_PRODUCAO
    for proibido in proibidos:
        assert proibido not in CODIGO_PRODUCAO


def test_nao_ha_io_nem_filesystem():
    proibidos = {
        "open",
        "read",
        "write",
        "read_text",
        "write_text",
        "read_bytes",
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


def test_nao_ha_yaml_indice_nem_corpus():
    for constante in _constantes_de_codigo():
        assert "knowledge" not in constante
        assert ".yaml" not in constante
        assert ".yml" not in constante
        assert ".md" not in constante
        assert ".json" not in constante
    proibidos = {"yaml", "json", "pickle", "safe_load", "load", "dump", "dumps"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_rede_llm_nem_processo():
    proibidos = {
        "requests",
        "urllib",
        "socket",
        "http",
        "httpx",
        "anthropic",
        "openai",
        "subprocess",
        "threading",
        "asyncio",
        "multiprocessing",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_relogio_calendario_locale_nem_ambiente():
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
        "logging",
        "getLogger",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_nem_coercao_de_texto():
    proibidos = {
        "strip",
        "lstrip",
        "rstrip",
        "lower",
        "upper",
        "casefold",
        "title",
        "capitalize",
        "normalize",
        "unicodedata",
        "encode",
        "decode",
        "expandtabs",
        "translate",
        "repr",
        "format",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_composicao_nem_decomposicao_de_token():
    proibidos = {
        "split",
        "rsplit",
        "splitlines",
        "partition",
        "rpartition",
        "join",
        "startswith",
        "endswith",
        "removeprefix",
        "removesuffix",
        "find",
        "rfind",
        "index",
        "count",
        "replace",
        "zip",
        "enumerate",
        "slice",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_dict_nem_conjunto_no_codigo():
    assert not [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.Dict, ast.DictComp, ast.Set, ast.SetComp))
    ]
    proibidos = {"dict", "set", "frozenset", "defaultdict", "Counter", "OrderedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_execucao_dinamica():
    proibidos = {"eval", "exec", "compile", "__import__", "globals", "locals", "vars"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_captura_de_excecao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_nao_ha_raise_from():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise):
            assert no.cause is None


def test_nao_ha_global_nem_nonlocal():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal))


def test_nao_ha_assert_em_producao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, ast.Assert)


def test_nao_ha_regex():
    proibidos = {"re", "regex", "match", "fullmatch", "search", "sub", "compile"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_enum_nem_dataclass():
    proibidos = {"Enum", "StrEnum", "dataclass", "NamedTuple", "TypedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_o_tipo_do_elemento_e_conferido_por_identidade_com_str():
    comparacoes = [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Compare)
        and any(isinstance(operador, ast.IsNot) for operador in no.ops)
    ]
    assert len(comparacoes) == 1
    comparacao = comparacoes[0]
    assert isinstance(comparacao.left, ast.Call)
    assert isinstance(comparacao.left.func, ast.Name)
    assert comparacao.left.func.id == "type"
    comparado = comparacao.comparators[0]
    assert isinstance(comparado, ast.Name)
    assert comparado.id == "str"


def test_isinstance_sobrevive_apenas_para_decidir_contentor():
    funcoes_com_isinstance = {
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.FunctionDef)
        and any(
            isinstance(interno, ast.Call)
            and isinstance(interno.func, ast.Name)
            and interno.func.id == "isinstance"
            for interno in ast.walk(no)
        )
    }
    assert funcoes_com_isinstance == {"_e_contentor"}


def test_producao_usa_sequence_para_decidir_contentor():
    assert "Sequence" in NOMES_PRODUCAO
    assert issubclass(list, Sequence)
    assert issubclass(tuple, Sequence)


def test_a_sequencia_e_materializada_uma_unica_vez():
    chamadas_tuple = [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Call)
        and isinstance(no.func, ast.Name)
        and no.func.id == "tuple"
    ]
    assert len(chamadas_tuple) == 2


def test_producao_declara_uma_unica_classe():
    classes = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)]
    assert [classe.name for classe in classes] == ["PropagacaoInvalida"]


def test_producao_declara_tres_funcoes_uma_publica():
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert funcoes == ["propagar_status", "_e_contentor", "_invalida"]


def test_constantes_de_codigo_sao_fechadas():
    assert set(_constantes_de_codigo()) == {
        "PropagacaoInvalida",
        "propagar_status",
        "tipo_invalido",
        "fragmentos",
        "fragmentos.item",
        ": ",
    }


def test_nao_ha_estado_mutavel_no_modulo():
    from casa77_sdr import response_status_propagation

    for nome, valor in vars(response_status_propagation).items():
        if nome.startswith("__") and nome.endswith("__"):
            continue
        if nome == "annotations":
            continue
        assert not isinstance(valor, (list, dict, set, bytearray))


def test_nao_ha_atribuicao_de_modulo_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.FunctionDef):
            for interno in ast.walk(no):
                if isinstance(interno, ast.Assign):
                    for alvo in interno.targets:
                        assert isinstance(alvo, ast.Name)
                        assert not alvo.id.startswith("_")


# ---------------------------------------------------------------------------
# Q. Determinismo e imutabilidade da entrada
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rotulo, esperado", TRADUCOES)
def test_chamadas_repetidas_devolvem_o_mesmo_resultado(rotulo, esperado):
    tokens = ["a", "b", "a"]
    resultados = [propagar_status(rotulo, tokens) for _ in range(20)]
    assert resultados == [
        (("a", esperado), ("b", esperado), ("a", esperado))
    ] * 20


def test_falha_e_deterministica_sob_repeticao():
    mensagens = []
    for _ in range(20):
        with pytest.raises(PropagacaoInvalida) as erro:
            propagar_status(APROVADO_MD, [1])
        mensagens.append(str(erro.value))
    assert mensagens == [MENSAGEM_ITEM] * 20


def test_sucesso_e_falha_intercalados_nao_acumulam_estado():
    for _ in range(10):
        assert propagar_status(APROVADO_MD, ["x"]) == (("x", APROVADO_CANONICO),)
        with pytest.raises(StatusNaoCanonicalizavel):
            propagar_status("PARCIAL", ["x"])
        with pytest.raises(PropagacaoInvalida):
            propagar_status(APROVADO_MD, [1])
    assert propagar_status(AGUARDA_MD, ["x"]) == (("x", AGUARDA_CANONICO),)


def test_a_lista_de_entrada_nao_e_alterada():
    tokens = ["a", "b", "a"]
    copia = list(tokens)
    propagar_status(APROVADO_MD, tokens)
    assert tokens == copia


def test_a_lista_de_entrada_nao_e_alterada_no_caminho_de_falha():
    tokens = ["a", 1, "b"]
    copia = list(tokens)
    with pytest.raises(PropagacaoInvalida):
        propagar_status(APROVADO_MD, tokens)
    assert tokens == copia


def test_o_rotulo_nao_e_alterado():
    rotulo = HANDOFF_MD
    copia = rotulo[:]
    propagar_status(rotulo, ["x"])
    assert rotulo == copia


def test_a_saida_nao_compartilha_mutabilidade_com_a_entrada():
    tokens = ["a", "b"]
    pares = propagar_status(APROVADO_MD, tokens)
    tokens.append("c")
    assert len(pares) == 2


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert propagar_status(APROVADO_MD, ["x"]) == (("x", APROVADO_CANONICO),)
    with pytest.raises(StatusNaoCanonicalizavel):
        propagar_status("aprovado", ["x"])


# ---------------------------------------------------------------------------
# R. Limites — o que um retorno bem-sucedido NAO afirma
# ---------------------------------------------------------------------------


def test_sucesso_nao_prova_existencia_do_rxx():
    """Um `Rxx` inexistente produz o mesmo sucesso: a associação é do chamador."""
    assert propagar_status(APROVADO_MD, ["R99/INEXISTENTE"]) == (
        ("R99/INEXISTENTE", APROVADO_CANONICO),
    )


def test_sucesso_nao_prova_pertencimento_nem_completude():
    de_um = propagar_status(APROVADO_MD, ["R01/F1"])
    de_outros = propagar_status(APROVADO_MD, ["R01/F1", "R77/F9"])
    assert de_um[0] == de_outros[0]
    assert len(de_outros) == 2


def test_a_fronteira_nao_agrupa_por_rxx():
    pares = propagar_status(APROVADO_MD, ["R01/F1", "R02/F1", "R01/F2"])
    assert [token for token, _ in pares] == ["R01/F1", "R02/F1", "R01/F2"]
    assert len(pares) == 3


def test_a_fronteira_nao_recusa_rxx_homonimo():
    pares = propagar_status(AGUARDA_MD, ["R01/F1", "R01/F1"])
    assert len(pares) == 2


def test_a_fronteira_nao_valida_cobertura_nem_cardinalidade():
    assert len(propagar_status(APROVADO_MD, [])) == 0
    assert len(propagar_status(APROVADO_MD, ["um"])) == 1
