"""Testes do resolver factual de `caminho_yaml` — `CY13`, linha 3.

A fronteira materializa **exclusivamente** a terceira responsabilidade de
`CY13`: percorrer a **estrutura factual já carregada em memória** com uma
**decomposição já produzida** pelo parser, resolver chaves, executar seletores,
decidir **zero / um / múltiplos *matches*** e devolver o **terminal como está**.
Ela **não** abre arquivo, **não** importa `yaml`, **não** conhece caminho de
corpus, **não** rejulga gramática e **não** aplica `C-7`.

Estes testes provam o percurso, os terminais, o `@` isolado, a distinção entre
**ausência** e **`None` factual**, a recusa de `(False, ())`, a **doutrina de
conformidade do seletor** — a coleção inteira antes da cardinalidade —, a
comparação literal por `str`, o contrato de `itera_sobre`, a taxonomia fechada
de nove categorias e seis localizadores, a ausência de vazamento, a não-mutação,
o determinismo, a identidade do objeto devolvido e a pureza do módulo de
produção. **Nenhum teste toca o corpus versionado**: todas as fixtures são
**sintéticas**.
"""

from __future__ import annotations

import ast
import copy
import inspect
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr import response_yaml_resolve
from casa77_sdr.response_yaml_path import CaminhoYamlInvalido
from casa77_sdr.response_yaml_path_context import CaminhoYamlContextoInvalido
from casa77_sdr.response_yaml_resolve import (
    CaminhoYamlNaoResolvido,
    resolver_caminho,
    resolver_itera_sobre,
)

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_yaml_resolve.py"
)
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)


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


def _nomes_executaveis():
    """Nomes que o módulo REALMENTE usa em código — não vocabulário de docstring.

    Só `ast.Name` e `ast.Attribute` entram. Comentário e docstring ficam de
    fora de propósito: a prova é sobre estrutura executável.
    """
    nomes = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


NOMES_PRODUCAO = _nomes_executaveis()


def _constantes_de_codigo():
    """Constantes `str` do módulo que **não** são docstring."""
    return [
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, str)
        and id(no) not in IDS_DOCSTRING
    ]


def _importados():
    """Pares `(modulo, nome, apelido)` de todo `from ... import ...`."""
    return [
        (no.module, alias.name, alias.asname)
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.ImportFrom)
        for alias in no.names
    ]


def erro_caminho(raiz, decomposicao, **contexto):
    """Mensagem da recusa de `resolver_caminho`."""
    with pytest.raises(CaminhoYamlNaoResolvido) as erro:
        resolver_caminho(raiz, decomposicao, **contexto)
    return str(erro.value)


def erro_itera(raiz, decomposicao):
    """Mensagem da recusa de `resolver_itera_sobre`."""
    with pytest.raises(CaminhoYamlNaoResolvido) as erro:
        resolver_itera_sobre(raiz, decomposicao)
    return str(erro.value)


def seg(chave, seletor=None):
    """Monta um segmento da decomposição, no formato do parser."""
    return (chave, seletor)


def absoluto(*segmentos):
    return (False, tuple(segmentos))


def relativo(*segmentos):
    return (True, tuple(segmentos))


class MapaDerivado(dict):
    """Subclasse de `dict`: recusada como estrutura canônica."""


class ListaDerivada(list):
    """Subclasse de `list`: recusada como coleção canônica."""


CATEGORIAS = {
    "tipo_invalido",
    "item_corrente_ausente",
    "relativo_em_itera_sobre",
    "segmento_inexistente",
    "tipo_incompativel",
    "travessia_em_nulo",
    "zero_matches",
    "multiplos_matches",
    "itera_sobre_nao_colecao",
}

LOCALIZADORES = {
    "raiz",
    "decomposicao",
    "item_corrente",
    "segmento",
    "seletor",
    "itera_sobre",
}


# ---------------------------------------------------------------------------
# A. Percurso
# ---------------------------------------------------------------------------


def test_absoluto_de_um_segmento():
    raiz = {"bloco_exemplo": "valor_exemplo"}
    assert resolver_caminho(raiz, absoluto(seg("bloco_exemplo"))) == "valor_exemplo"


def test_absoluto_multi_segmento():
    raiz = {"bloco_exemplo": {"submapa": {"campo_exemplo": "valor_exemplo"}}}
    resultado = resolver_caminho(
        raiz, absoluto(seg("bloco_exemplo"), seg("submapa"), seg("campo_exemplo"))
    )
    assert resultado == "valor_exemplo"


def test_relativo_de_um_segmento():
    item = {"campo_exemplo": "valor_exemplo"}
    resultado = resolver_caminho(
        {}, relativo(seg("campo_exemplo")), item_corrente=item
    )
    assert resultado == "valor_exemplo"


def test_relativo_multi_segmento():
    item = {"submapa": {"campo_exemplo": "valor_exemplo"}}
    resultado = resolver_caminho(
        {}, relativo(seg("submapa"), seg("campo_exemplo")), item_corrente=item
    )
    assert resultado == "valor_exemplo"


def test_relativo_nao_consulta_a_raiz():
    """A raiz existe e tem a chave, mas o relativo parte do item corrente."""
    raiz = {"campo_exemplo": "da_raiz"}
    item = {"campo_exemplo": "do_item"}
    resultado = resolver_caminho(
        raiz, relativo(seg("campo_exemplo")), item_corrente=item
    )
    assert resultado == "do_item"


def test_absoluto_nao_consulta_o_item_corrente():
    raiz = {"campo_exemplo": "da_raiz"}
    item = {"campo_exemplo": "do_item"}
    resultado = resolver_caminho(
        raiz, absoluto(seg("campo_exemplo")), item_corrente=item
    )
    assert resultado == "da_raiz"


def test_arroba_isolado_devolve_o_item_corrente_por_identidade():
    item = {"campo_exemplo": "valor_exemplo"}
    assert resolver_caminho({}, relativo(), item_corrente=item) is item


def test_arroba_isolado_com_item_corrente_nulo_e_sucesso():
    """`None` é valor factual legítimo, e não ausência."""
    assert resolver_caminho({}, relativo(), item_corrente=None) is None


@pytest.mark.parametrize(
    "item",
    ["escalar_exemplo", 7, 2.5, True, False, None, [], [1, 2], {}, {"a": 1}],
)
def test_arroba_isolado_devolve_qualquer_item_corrente(item):
    assert resolver_caminho({}, relativo(), item_corrente=item) is item


def test_arroba_isolado_sobre_lista_e_sucesso():
    item = ["a", "b"]
    assert resolver_caminho({}, relativo(), item_corrente=item) is item


# ---------------------------------------------------------------------------
# B. Terminais
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "terminal",
    ["texto_exemplo", 0, 42, -1, 2.5, True, False, None, [], [1], {}, {"a": 1}],
)
def test_terminal_e_devolvido_como_esta(terminal):
    raiz = {"campo_exemplo": terminal}
    assert resolver_caminho(raiz, absoluto(seg("campo_exemplo"))) is terminal


def test_terminal_nulo_e_sucesso():
    raiz = {"campo_exemplo": None}
    assert resolver_caminho(raiz, absoluto(seg("campo_exemplo"))) is None


def test_terminal_mapa_e_devolvido_por_identidade():
    interno = {"a": 1}
    raiz = {"campo_exemplo": interno}
    assert resolver_caminho(raiz, absoluto(seg("campo_exemplo"))) is interno


def test_terminal_lista_e_devolvido_por_identidade():
    interno = [1, 2, 3]
    raiz = {"campo_exemplo": interno}
    assert resolver_caminho(raiz, absoluto(seg("campo_exemplo"))) is interno


def test_terminal_bool_nao_e_confundido_com_inteiro():
    raiz = {"campo_exemplo": True}
    resultado = resolver_caminho(raiz, absoluto(seg("campo_exemplo")))
    assert resultado is True
    assert type(resultado) is bool


# ---------------------------------------------------------------------------
# C. Percurso invalido
# ---------------------------------------------------------------------------


def test_chave_ausente():
    raiz = {"bloco_exemplo": {}}
    assert (
        erro_caminho(raiz, absoluto(seg("bloco_exemplo"), seg("inexistente")))
        == "segmento_inexistente: segmento"
    )


def test_chave_ausente_no_primeiro_segmento():
    assert erro_caminho({}, absoluto(seg("inexistente"))) == (
        "segmento_inexistente: segmento"
    )


def test_travessia_em_nulo_intermediario():
    raiz = {"bloco_exemplo": None}
    assert (
        erro_caminho(raiz, absoluto(seg("bloco_exemplo"), seg("campo_exemplo")))
        == "travessia_em_nulo: segmento"
    )


def test_travessia_em_nulo_no_item_corrente():
    assert (
        erro_caminho({}, relativo(seg("campo_exemplo")), item_corrente=None)
        == "travessia_em_nulo: segmento"
    )


@pytest.mark.parametrize("intermediario", ["texto", 7, 2.5, True, [1, 2], ()])
def test_tipo_intermediario_incompativel(intermediario):
    raiz = {"bloco_exemplo": intermediario}
    assert (
        erro_caminho(raiz, absoluto(seg("bloco_exemplo"), seg("campo_exemplo")))
        == "tipo_incompativel: segmento"
    )


@pytest.mark.parametrize("raiz", [None, "texto", 7, 2.5, True, [], (), set(), object()])
def test_raiz_nao_dict(raiz):
    assert erro_caminho(raiz, absoluto(seg("campo_exemplo"))) == "tipo_invalido: raiz"


def test_subclasse_de_dict_como_raiz_e_recusada():
    raiz = MapaDerivado({"campo_exemplo": "valor_exemplo"})
    assert erro_caminho(raiz, absoluto(seg("campo_exemplo"))) == "tipo_invalido: raiz"


def test_subclasse_de_dict_como_no_intermediario_e_recusada():
    raiz = {"bloco_exemplo": MapaDerivado({"campo_exemplo": "valor_exemplo"})}
    assert (
        erro_caminho(raiz, absoluto(seg("bloco_exemplo"), seg("campo_exemplo")))
        == "tipo_incompativel: segmento"
    )


def test_subclasse_de_dict_como_item_corrente_e_recusada():
    item = MapaDerivado({"campo_exemplo": "valor_exemplo"})
    assert (
        erro_caminho({}, relativo(seg("campo_exemplo")), item_corrente=item)
        == "tipo_incompativel: segmento"
    )


def test_raiz_e_julgada_antes_da_decomposicao():
    assert erro_caminho(None, "decomposicao_absurda") == "tipo_invalido: raiz"


def test_nulo_vence_tipo_incompativel_por_ser_o_no_corrente():
    raiz = {"a": {"b": None}}
    assert (
        erro_caminho(raiz, absoluto(seg("a"), seg("b"), seg("c")))
        == "travessia_em_nulo: segmento"
    )


def test_primeira_violacao_do_percurso_encerra():
    raiz = {"a": None}
    assert (
        erro_caminho(raiz, absoluto(seg("a"), seg("b"), seg("inexistente")))
        == "travessia_em_nulo: segmento"
    )


# ---------------------------------------------------------------------------
# D. Seletor
# ---------------------------------------------------------------------------


def test_seletor_com_um_match():
    alvo = {"id": "item_exemplo", "campo_exemplo": "valor_exemplo"}
    raiz = {"colecao_exemplo": [{"id": "outro_exemplo"}, alvo]}
    resultado = resolver_caminho(
        raiz, absoluto(seg("colecao_exemplo", ("id", "item_exemplo")))
    )
    assert resultado is alvo


def test_seletor_seguido_de_segmento():
    raiz = {
        "colecao_exemplo": [
            {"id": "item_exemplo", "campo_exemplo": "valor_exemplo"},
        ]
    }
    resultado = resolver_caminho(
        raiz,
        absoluto(
            seg("colecao_exemplo", ("id", "item_exemplo")), seg("campo_exemplo")
        ),
    )
    assert resultado == "valor_exemplo"


def test_seletor_com_zero_matches():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": "b"}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "z"))))
        == "zero_matches: seletor"
    )


def test_seletor_em_colecao_vazia_e_zero_matches():
    raiz = {"colecao_exemplo": []}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "zero_matches: seletor"
    )


def test_seletor_com_multiplos_matches():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": "a"}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "multiplos_matches: seletor"
    )


@pytest.mark.parametrize("colecao", ["texto", 7, 2.5, True, {}, {"a": 1}, (), set()])
def test_seletor_sobre_nao_lista(colecao):
    raiz = {"colecao_exemplo": colecao}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_seletor_sobre_nulo():
    raiz = {"colecao_exemplo": None}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "travessia_em_nulo: seletor"
    )


def test_seletor_sobre_subclasse_de_lista_e_recusado():
    raiz = {"colecao_exemplo": ListaDerivada([{"id": "a"}])}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


@pytest.mark.parametrize("item", ["texto", 7, None, [], (), True])
def test_item_da_colecao_nao_e_mapa(item):
    raiz = {"colecao_exemplo": [item]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_item_da_colecao_e_subclasse_de_dict():
    raiz = {"colecao_exemplo": [MapaDerivado({"id": "a"})]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_chave_seletora_ausente_no_item():
    raiz = {"colecao_exemplo": [{"outra": "a"}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "segmento_inexistente: seletor"
    )


@pytest.mark.parametrize("valor", [7, 2.5, True, None, [], {}, ()])
def test_valor_da_chave_seletora_nao_e_str(valor):
    raiz = {"colecao_exemplo": [{"id": valor}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


# ---------------------------------------------------------------------------
# E. Conformidade da colecao PRECEDE a cardinalidade
# ---------------------------------------------------------------------------


def test_item_invalido_antes_do_match_vence():
    raiz = {"colecao_exemplo": ["nao_e_mapa", {"id": "a"}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_item_invalido_depois_do_match_vence():
    """O *match* já ocorreu, mas a coleção inteira precisa estar conforme."""
    raiz = {"colecao_exemplo": [{"id": "a"}, "nao_e_mapa"]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_item_invalido_depois_de_multiplos_matches_vence():
    """Nem mesmo `multiplos_matches` antecipa a verificação estrutural."""
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": "a"}, "nao_e_mapa"]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_chave_ausente_depois_do_match_vence():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"outra": "b"}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "segmento_inexistente: seletor"
    )


def test_valor_nao_str_depois_do_match_vence():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": 7}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_item_invalido_vence_zero_matches():
    raiz = {"colecao_exemplo": [{"id": "x"}, 7]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "tipo_incompativel: seletor"
    )


def test_colecao_inteiramente_conforme_decide_cardinalidade():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}
    alvo = raiz["colecao_exemplo"][1]
    assert (
        resolver_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "b")))) is alvo
    )


# ---------------------------------------------------------------------------
# F. Comparacao literal por `str`
# ---------------------------------------------------------------------------


def test_literal_numerico_casa_com_str():
    alvo = {"id": "2026"}
    raiz = {"colecao_exemplo": [alvo]}
    assert (
        resolver_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "2026"))))
        is alvo
    )


def test_literal_numerico_nao_casa_com_inteiro():
    """Zero coerção: o valor precisa ser `str` exata, e aí falha por tipo."""
    raiz = {"colecao_exemplo": [{"id": 2026}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "2026"))))
        == "tipo_incompativel: seletor"
    )


def test_comparacao_do_seletor_e_sensivel_a_caixa():
    raiz = {"colecao_exemplo": [{"id": "Item"}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "item"))))
        == "zero_matches: seletor"
    )


def test_comparacao_do_seletor_nao_tolera_espaco_de_borda():
    raiz = {"colecao_exemplo": [{"id": " a"}]}
    assert (
        erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "zero_matches: seletor"
    )


def test_dois_seletores_em_segmentos_distintos():
    alvo = {"id": "b", "campo_exemplo": "valor_exemplo"}
    raiz = {
        "primeira": [
            {"id": "a", "segunda": [{"id": "z"}]},
            {"id": "x", "segunda": [alvo]},
        ]
    }
    resultado = resolver_caminho(
        raiz,
        absoluto(seg("primeira", ("id", "x")), seg("segunda", ("id", "b"))),
    )
    assert resultado is alvo


# ---------------------------------------------------------------------------
# G. `itera_sobre`
# ---------------------------------------------------------------------------


def test_itera_sobre_lista_nao_vazia():
    colecao = [{"id": "a"}, {"id": "b"}]
    raiz = {"colecao_exemplo": colecao}
    assert resolver_itera_sobre(raiz, absoluto(seg("colecao_exemplo"))) is colecao


def test_itera_sobre_lista_vazia_e_sucesso():
    colecao = []
    raiz = {"colecao_exemplo": colecao}
    assert resolver_itera_sobre(raiz, absoluto(seg("colecao_exemplo"))) is colecao


def test_itera_sobre_lista_de_escalares():
    colecao = ["a", "b", "c"]
    raiz = {"colecao_exemplo": colecao}
    assert resolver_itera_sobre(raiz, absoluto(seg("colecao_exemplo"))) is colecao


def test_itera_sobre_com_seletor_no_meio():
    colecao = [{"id": "z"}]
    raiz = {"primeira": [{"id": "x", "segunda": colecao}]}
    resultado = resolver_itera_sobre(
        raiz, absoluto(seg("primeira", ("id", "x")), seg("segunda"))
    )
    assert resultado is colecao


@pytest.mark.parametrize(
    "terminal", [{"a": 1}, {}, "texto", 7, 2.5, True, False, None]
)
def test_itera_sobre_terminal_nao_colecao(terminal):
    raiz = {"colecao_exemplo": terminal}
    assert (
        erro_itera(raiz, absoluto(seg("colecao_exemplo")))
        == "itera_sobre_nao_colecao: itera_sobre"
    )


def test_itera_sobre_terminal_tuple_e_recusado():
    raiz = {"colecao_exemplo": ("a", "b")}
    assert (
        erro_itera(raiz, absoluto(seg("colecao_exemplo")))
        == "itera_sobre_nao_colecao: itera_sobre"
    )


def test_itera_sobre_terminal_set_e_recusado():
    raiz = {"colecao_exemplo": {"a", "b"}}
    assert (
        erro_itera(raiz, absoluto(seg("colecao_exemplo")))
        == "itera_sobre_nao_colecao: itera_sobre"
    )


def test_itera_sobre_terminal_subclasse_de_lista_e_recusado():
    raiz = {"colecao_exemplo": ListaDerivada([1, 2])}
    assert (
        erro_itera(raiz, absoluto(seg("colecao_exemplo")))
        == "itera_sobre_nao_colecao: itera_sobre"
    )


def test_itera_sobre_recusa_decomposicao_relativa():
    raiz = {"colecao_exemplo": []}
    assert (
        erro_itera(raiz, relativo(seg("colecao_exemplo")))
        == "relativo_em_itera_sobre: decomposicao"
    )


def test_itera_sobre_recusa_arroba_isolado():
    assert erro_itera({}, relativo()) == "relativo_em_itera_sobre: decomposicao"


def test_itera_sobre_raiz_nao_dict():
    assert erro_itera(None, absoluto(seg("a"))) == "tipo_invalido: raiz"


def test_itera_sobre_recusa_falso_vazio():
    assert erro_itera({}, absoluto()) == "tipo_invalido: decomposicao"


def test_itera_sobre_recusa_relativo_antes_de_olhar_os_segmentos():
    """`CASO B`: a recusa do relativo precede a forma de segmento não alcançado.

    O envelope externo já está bem formado; o segundo elemento do par é uma
    `tuple` com um segmento malformado. Como `itera_sobre` recusa a forma
    relativa **antes** do percurso, aquele segmento **jamais é inspecionado**.
    """
    assert erro_itera({}, (True, ("nao_e_segmento",))) == (
        "relativo_em_itera_sobre: decomposicao"
    )


def test_itera_sobre_envelope_malformado_ainda_vence_o_relativo():
    """O envelope, esse sim, é julgado antes da regra do relativo."""
    assert erro_itera({}, (True, "nao_e_tuple")) == "tipo_invalido: decomposicao"


def test_itera_sobre_propaga_falhas_de_percurso():
    raiz = {"a": None}
    assert (
        erro_itera(raiz, absoluto(seg("a"), seg("b")))
        == "travessia_em_nulo: segmento"
    )


def test_itera_sobre_propaga_falhas_de_seletor():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": "a"}]}
    assert (
        erro_itera(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
        == "multiplos_matches: seletor"
    )


def test_itera_sobre_nao_recebe_item_corrente():
    assinatura = inspect.signature(resolver_itera_sobre)
    assert list(assinatura.parameters) == ["raiz", "decomposicao"]


# ---------------------------------------------------------------------------
# H. Item corrente
# ---------------------------------------------------------------------------


def test_relativo_sem_item_corrente_e_recusado():
    assert (
        erro_caminho({}, relativo(seg("campo_exemplo")))
        == "item_corrente_ausente: item_corrente"
    )


def test_arroba_isolado_sem_item_corrente_e_recusado():
    assert erro_caminho({}, relativo()) == "item_corrente_ausente: item_corrente"


def test_absoluto_sem_item_corrente_e_valido():
    raiz = {"campo_exemplo": "valor_exemplo"}
    assert resolver_caminho(raiz, absoluto(seg("campo_exemplo"))) == "valor_exemplo"


def test_item_corrente_e_keyword_only():
    assinatura = inspect.signature(resolver_caminho)
    parametro = assinatura.parameters["item_corrente"]
    assert parametro.kind is inspect.Parameter.KEYWORD_ONLY
    with pytest.raises(TypeError):
        resolver_caminho({}, relativo(), {"a": 1})


def test_o_default_do_item_corrente_e_a_sentinela_privada():
    assinatura = inspect.signature(resolver_caminho)
    parametro = assinatura.parameters["item_corrente"]
    assert parametro.default is response_yaml_resolve._AUSENTE


def test_none_nao_e_ausencia():
    """`item_corrente=None` é presença de um valor nulo, não ausência."""
    assert resolver_caminho({}, relativo(), item_corrente=None) is None
    assert erro_caminho({}, relativo()) == "item_corrente_ausente: item_corrente"


def test_envelope_da_decomposicao_e_julgado_antes_do_item_corrente():
    assert erro_caminho({}, "lixo") == "tipo_invalido: decomposicao"
    assert erro_caminho({}, absoluto()) == "tipo_invalido: decomposicao"


# ---------------------------------------------------------------------------
# I. Forma tecnica da decomposicao
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "decomposicao",
    [None, "texto", 7, 2.5, True, [], [False, ()], {}, set(), object()],
)
def test_decomposicao_nao_tuple(decomposicao):
    assert erro_caminho({}, decomposicao) == "tipo_invalido: decomposicao"


@pytest.mark.parametrize("decomposicao", [(), (False,), (False, (), "extra")])
def test_decomposicao_com_tamanho_errado(decomposicao):
    assert erro_caminho({}, decomposicao) == "tipo_invalido: decomposicao"


@pytest.mark.parametrize("relativo_bruto", [0, 1, "sim", None, [], ()])
def test_relativo_precisa_ser_bool_exato(relativo_bruto):
    decomposicao = (relativo_bruto, (seg("a"),))
    assert erro_caminho({"a": 1}, decomposicao) == "tipo_invalido: decomposicao"


@pytest.mark.parametrize("segmentos", [None, "texto", 7, [], [("a", None)], {}])
def test_segmentos_precisam_ser_tuple(segmentos):
    assert erro_caminho({}, (False, segmentos)) == "tipo_invalido: decomposicao"


@pytest.mark.parametrize(
    "segmento", ["a", 7, None, ["a", None], ("a",), ("a", None, "extra"), ()]
)
def test_segmento_com_forma_errada(segmento):
    assert erro_caminho({}, (False, (segmento,))) == "tipo_invalido: decomposicao"


@pytest.mark.parametrize("chave", [7, None, True, b"a", ["a"], ()])
def test_chave_do_segmento_precisa_ser_str(chave):
    assert erro_caminho({}, (False, ((chave, None),))) == (
        "tipo_invalido: decomposicao"
    )


@pytest.mark.parametrize(
    "seletor", ["a", 7, ["id", "a"], ("id",), ("id", "a", "extra"), (), True]
)
def test_seletor_com_forma_errada(seletor):
    assert erro_caminho({}, (False, (("a", seletor),))) == (
        "tipo_invalido: decomposicao"
    )


@pytest.mark.parametrize("chave_seletora", [7, None, True, b"id", ()])
def test_chave_seletora_precisa_ser_str(chave_seletora):
    decomposicao = (False, (("a", (chave_seletora, "valor")),))
    assert erro_caminho({}, decomposicao) == "tipo_invalido: decomposicao"


@pytest.mark.parametrize("literal", [7, None, True, b"a", ()])
def test_literal_do_seletor_precisa_ser_str(literal):
    decomposicao = (False, (("a", ("id", literal)),))
    assert erro_caminho({}, decomposicao) == "tipo_invalido: decomposicao"


def test_falso_vazio_e_tecnicamente_invalido():
    """`(False, ())` — absoluto sem segmento — não tem referente."""
    assert erro_caminho({}, (False, ())) == "tipo_invalido: decomposicao"


def test_verdadeiro_vazio_e_valido():
    """`(True, ())` é o `@` isolado de `CY11`."""
    item = {"a": 1}
    assert resolver_caminho({}, (True, ()), item_corrente=item) is item


def test_forma_do_primeiro_segmento_e_exigida_ao_alcanca_lo():
    assert erro_caminho({}, (False, ("nao_e_segmento",))) == (
        "tipo_invalido: decomposicao"
    )


# ---------------------------------------------------------------------------
# I.1 Precedencia: envelope externo x segmento ALCANCADO
# ---------------------------------------------------------------------------


def test_item_corrente_ausente_vence_segmento_futuro_malformado():
    """`CASO A`: a ausência do item corrente precede o percurso.

    O segmento malformado está na decomposição, mas o percurso nem começa —
    logo, ele **não é inspecionado**.
    """
    assert erro_caminho({}, (True, ("nao_e_segmento",))) == (
        "item_corrente_ausente: item_corrente"
    )


def test_chave_inexistente_vence_segmento_futuro_malformado():
    """`CASO C`: a falha do primeiro segmento encerra antes do segundo."""
    decomposicao = (False, (("a", None), "nao_e_segmento"))
    assert erro_caminho({}, decomposicao) == "segmento_inexistente: segmento"


def test_travessia_em_nulo_vence_segmento_futuro_malformado():
    """`CASO D`: o terceiro elemento jamais é alcançado."""
    decomposicao = (False, (("a", None), ("b", None), "nao_e_segmento"))
    assert erro_caminho({"a": None}, decomposicao) == "travessia_em_nulo: segmento"


def test_forma_do_segmento_corrente_vence_o_estado_estrutural_do_mesmo_passo():
    """Prova complementar: segmento ATUAL malformado × segmento FUTURO.

    Aqui o segundo segmento **é alcançado** — o percurso chegou nele — e a sua
    forma é julgada **antes** do `None` deixado pelo passo anterior. Isso
    distingue as duas doutrinas: forma do corrente vence o estado do mesmo
    passo; forma de um futuro não alcançado não interfere em nada.
    """
    decomposicao = (False, (("a", None), "nao_e_segmento"))
    assert erro_caminho({"a": None}, decomposicao) == "tipo_invalido: decomposicao"


def test_tipo_incompativel_anterior_vence_segmento_futuro_malformado():
    decomposicao = (False, (("a", None), ("b", None), "nao_e_segmento"))
    assert erro_caminho({"a": 7}, decomposicao) == "tipo_incompativel: segmento"


def test_falha_de_seletor_anterior_vence_segmento_futuro_malformado():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": "a"}]}
    decomposicao = (
        False,
        (("colecao_exemplo", ("id", "a")), "nao_e_segmento"),
    )
    assert erro_caminho(raiz, decomposicao) == "multiplos_matches: seletor"


def test_envelope_malformado_vence_o_item_corrente_ausente():
    """O envelope externo continua sendo julgado antes de tudo o mais."""
    assert erro_caminho({}, (True, "nao_e_tuple")) == "tipo_invalido: decomposicao"
    assert erro_caminho({}, (1, ())) == "tipo_invalido: decomposicao"


def test_arroba_isolado_nao_inspeciona_segmento_algum():
    """Sem segmentos não há forma de segmento a exigir."""
    item = {"a": 1}
    assert resolver_caminho({}, (True, ()), item_corrente=item) is item


def test_seletor_none_e_forma_valida():
    raiz = {"a": "valor_exemplo"}
    assert resolver_caminho(raiz, (False, (("a", None),))) == "valor_exemplo"


# ---------------------------------------------------------------------------
# J. A gramatica NAO e rejulgada
# ---------------------------------------------------------------------------


def test_chave_gramaticalmente_absurda_nao_e_rejulgada():
    """Uma chave impossível para o parser resolve normalmente se existir."""
    raiz = {"chave com espaco e @!": "valor_exemplo"}
    resultado = resolver_caminho(raiz, absoluto(seg("chave com espaco e @!")))
    assert resultado == "valor_exemplo"


def test_chave_vazia_nao_e_rejulgada():
    raiz = {"": "valor_exemplo"}
    assert resolver_caminho(raiz, absoluto(seg(""))) == "valor_exemplo"


def test_chave_exclusivamente_numerica_nao_e_rejulgada():
    """`CY9` é da gramática, não daqui: aqui `"123"` é só uma chave."""
    raiz = {"123": "valor_exemplo"}
    assert resolver_caminho(raiz, absoluto(seg("123"))) == "valor_exemplo"


def test_chave_com_arroba_nao_e_rejulgada():
    raiz = {"@": {"campo_exemplo": "valor_exemplo"}}
    resultado = resolver_caminho(raiz, absoluto(seg("@"), seg("campo_exemplo")))
    assert resultado == "valor_exemplo"


def test_chave_absurda_ausente_falha_como_estrutura_e_nao_como_gramatica():
    assert erro_caminho({}, absoluto(seg("chave com espaco"))) == (
        "segmento_inexistente: segmento"
    )


def test_literal_seletor_absurdo_nao_e_rejulgado():
    alvo = {"id": "com espaco"}
    raiz = {"colecao_exemplo": [alvo]}
    resultado = resolver_caminho(
        raiz, absoluto(seg("colecao_exemplo", ("id", "com espaco")))
    )
    assert resultado is alvo


def test_producao_nao_importa_o_parser():
    assert "analisar_caminho_yaml" not in NOMES_PRODUCAO
    modulos = [modulo for modulo, _, _ in _importados()]
    assert "casa77_sdr.response_yaml_path" not in modulos
    assert "casa77_sdr.response_yaml_path_context" not in modulos


# ---------------------------------------------------------------------------
# K. Taxonomia fechada e ausencia de vazamento
# ---------------------------------------------------------------------------


def test_as_nove_categorias_sao_observaveis():
    observadas = {
        erro_caminho(None, absoluto(seg("a"))).split(":")[0],
        erro_caminho({}, relativo()).split(":")[0],
        erro_itera({}, relativo()).split(":")[0],
        erro_caminho({}, absoluto(seg("x"))).split(":")[0],
        erro_caminho({"a": 7}, absoluto(seg("a"), seg("b"))).split(":")[0],
        erro_caminho({"a": None}, absoluto(seg("a"), seg("b"))).split(":")[0],
        erro_caminho({"c": []}, absoluto(seg("c", ("id", "a")))).split(":")[0],
        erro_caminho(
            {"c": [{"id": "a"}, {"id": "a"}]}, absoluto(seg("c", ("id", "a")))
        ).split(":")[0],
        erro_itera({"a": 7}, absoluto(seg("a"))).split(":")[0],
    }
    assert observadas == CATEGORIAS


def test_todo_erro_pertence_ao_vocabulario_fechado():
    mensagens = [
        erro_caminho(None, absoluto(seg("a"))),
        erro_caminho({}, "lixo"),
        erro_caminho({}, relativo()),
        erro_caminho({}, absoluto(seg("x"))),
        erro_caminho({"a": 7}, absoluto(seg("a"), seg("b"))),
        erro_caminho({"a": None}, absoluto(seg("a"), seg("b"))),
        erro_caminho({"c": []}, absoluto(seg("c", ("id", "a")))),
        erro_caminho({"c": [{"id": "a"}, {"id": "a"}]}, absoluto(seg("c", ("id", "a")))),
        erro_caminho({"c": None}, absoluto(seg("c", ("id", "a")))),
        erro_caminho({"c": 7}, absoluto(seg("c", ("id", "a")))),
        erro_caminho({"c": [{"outra": "a"}]}, absoluto(seg("c", ("id", "a")))),
        erro_itera({}, relativo()),
        erro_itera({"a": 7}, absoluto(seg("a"))),
    ]
    for mensagem in mensagens:
        assert mensagem.count(": ") == 1
        categoria, _, localizador = mensagem.partition(": ")
        assert categoria in CATEGORIAS
        assert localizador in LOCALIZADORES


def test_a_mensagem_nao_ecoa_valor_factual():
    marcador = "marcador_sintetico_nao_deve_aparecer"
    raiz = {marcador: {marcador: None}}
    mensagem = erro_caminho(raiz, absoluto(seg(marcador), seg(marcador), seg("x")))
    assert marcador not in mensagem
    assert mensagem == "travessia_em_nulo: segmento"


def test_a_mensagem_nao_ecoa_chave_nem_literal():
    marcador = "literal_sintetico_nao_deve_aparecer"
    raiz = {"colecao_exemplo": [{"id": "outro"}]}
    mensagem = erro_caminho(
        raiz, absoluto(seg("colecao_exemplo", ("id", marcador)))
    )
    assert marcador not in mensagem
    assert "colecao_exemplo" not in mensagem
    assert mensagem == "zero_matches: seletor"


def test_a_mensagem_nao_ecoa_tipo_concreto_nem_cardinalidade():
    raiz = {"colecao_exemplo": [{"id": "a"}, {"id": "a"}, {"id": "a"}]}
    mensagem = erro_caminho(raiz, absoluto(seg("colecao_exemplo", ("id", "a"))))
    assert mensagem == "multiplos_matches: seletor"
    assert not any(caractere in "0123456789" for caractere in mensagem)


def test_a_mensagem_nao_ecoa_o_valor_recebido_na_raiz():
    class Estranho:
        def __repr__(self):  # pragma: no cover - nao deve ser chamado
            raise AssertionError("o repr nao pode ser consultado")

    mensagem = erro_caminho(Estranho(), absoluto(seg("a")))
    assert mensagem == "tipo_invalido: raiz"


def test_nenhuma_mensagem_carrega_digito():
    for mensagem in (
        erro_caminho(None, absoluto(seg("a"))),
        erro_caminho({}, "lixo"),
        erro_caminho({}, relativo()),
        erro_itera({"a": 7}, absoluto(seg("a"))),
    ):
        assert not any(caractere in "0123456789" for caractere in mensagem)


# ---------------------------------------------------------------------------
# L. Nao mutacao, determinismo e identidade
# ---------------------------------------------------------------------------


def _corpus_sintetico():
    return {
        "bloco_exemplo": {
            "campo_exemplo": "valor_exemplo",
            "nulo_exemplo": None,
            "colecao_exemplo": [
                {"id": "a", "campo_exemplo": "primeiro"},
                {"id": "b", "campo_exemplo": "segundo"},
            ],
        },
        "lista_exemplo": ["x", "y"],
    }


def test_a_raiz_nao_e_mutada_no_sucesso():
    raiz = _corpus_sintetico()
    antes = copy.deepcopy(raiz)
    resolver_caminho(
        raiz,
        absoluto(
            seg("bloco_exemplo"),
            seg("colecao_exemplo", ("id", "a")),
            seg("campo_exemplo"),
        ),
    )
    assert raiz == antes


def test_a_raiz_nao_e_mutada_na_falha():
    raiz = _corpus_sintetico()
    antes = copy.deepcopy(raiz)
    with pytest.raises(CaminhoYamlNaoResolvido):
        resolver_caminho(raiz, absoluto(seg("bloco_exemplo"), seg("inexistente")))
    assert raiz == antes


def test_o_item_corrente_nao_e_mutado():
    item = {"campo_exemplo": "valor_exemplo", "interno": {"a": [1, 2]}}
    antes = copy.deepcopy(item)
    resolver_caminho({}, relativo(seg("campo_exemplo")), item_corrente=item)
    assert item == antes


def test_itera_sobre_nao_muta_a_raiz():
    raiz = _corpus_sintetico()
    antes = copy.deepcopy(raiz)
    resolver_itera_sobre(raiz, absoluto(seg("bloco_exemplo"), seg("colecao_exemplo")))
    assert raiz == antes


def test_itera_sobre_devolve_a_mesma_lista_sem_copiar():
    raiz = _corpus_sintetico()
    colecao = raiz["bloco_exemplo"]["colecao_exemplo"]
    resultado = resolver_itera_sobre(
        raiz, absoluto(seg("bloco_exemplo"), seg("colecao_exemplo"))
    )
    assert resultado is colecao


def test_o_terminal_e_o_proprio_objeto_da_estrutura():
    raiz = _corpus_sintetico()
    alvo = raiz["bloco_exemplo"]["colecao_exemplo"][1]
    resultado = resolver_caminho(
        raiz, absoluto(seg("bloco_exemplo"), seg("colecao_exemplo", ("id", "b")))
    )
    assert resultado is alvo


def test_resultado_e_deterministico():
    raiz = _corpus_sintetico()
    decomposicao = absoluto(
        seg("bloco_exemplo"), seg("colecao_exemplo", ("id", "a")), seg("campo_exemplo")
    )
    primeiro = resolver_caminho(raiz, decomposicao)
    for _ in range(5):
        assert resolver_caminho(raiz, decomposicao) is primeiro


def test_falha_e_deterministica():
    raiz = _corpus_sintetico()
    decomposicao = absoluto(seg("bloco_exemplo"), seg("inexistente"))
    assert erro_caminho(raiz, decomposicao) == erro_caminho(raiz, decomposicao)


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    raiz = {"Bloco_I": "valor_exemplo"}
    assert resolver_caminho(raiz, absoluto(seg("Bloco_I"))) == "valor_exemplo"


def test_a_decomposicao_nao_e_mutada():
    decomposicao = absoluto(seg("a"), seg("c", ("id", "x")))
    copia = copy.deepcopy(decomposicao)
    with pytest.raises(CaminhoYamlNaoResolvido):
        resolver_caminho({}, decomposicao)
    assert decomposicao == copia


# ---------------------------------------------------------------------------
# M. Contrato publico
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_os_tres_nomes():
    assert response_yaml_resolve.__all__ == [
        "CaminhoYamlNaoResolvido",
        "resolver_caminho",
        "resolver_itera_sobre",
    ]


def test_a_sentinela_e_privada():
    assert "_AUSENTE" not in response_yaml_resolve.__all__
    assert response_yaml_resolve._AUSENTE is not None
    assert type(response_yaml_resolve._AUSENTE) is object


def test_nao_ha_nome_publico_fora_de_all():
    publicos = {
        nome
        for nome in vars(response_yaml_resolve)
        if not nome.startswith("_") and nome not in {"annotations"}
    }
    assert publicos == set(response_yaml_resolve.__all__)


def test_producao_declara_uma_classe_e_duas_funcoes_publicas():
    classes = [
        no.name for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)
    ]
    assert classes == ["CaminhoYamlNaoResolvido"]
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    publicas = [nome for nome in funcoes if not nome.startswith("_")]
    assert publicas == ["resolver_caminho", "resolver_itera_sobre"]


def test_assinatura_de_resolver_caminho():
    assinatura = inspect.signature(resolver_caminho)
    assert list(assinatura.parameters) == ["raiz", "decomposicao", "item_corrente"]
    for nome in ("raiz", "decomposicao"):
        parametro = assinatura.parameters[nome]
        assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parametro.default is inspect.Parameter.empty
    assert assinatura.return_annotation == "object"


def test_assinatura_de_resolver_itera_sobre():
    assinatura = inspect.signature(resolver_itera_sobre)
    assert list(assinatura.parameters) == ["raiz", "decomposicao"]
    for parametro in assinatura.parameters.values():
        assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parametro.default is inspect.Parameter.empty
    assert assinatura.return_annotation == "list"


def test_nao_e_exportado_pelo_pacote():
    for nome in (
        "CaminhoYamlNaoResolvido",
        "resolver_caminho",
        "resolver_itera_sobre",
    ):
        assert not hasattr(casa77_sdr, nome)
        assert nome not in getattr(casa77_sdr, "__all__", [])


def test_as_tres_excecoes_de_cy13_sao_independentes():
    excecoes = (
        CaminhoYamlInvalido,
        CaminhoYamlContextoInvalido,
        CaminhoYamlNaoResolvido,
    )
    for excecao in excecoes:
        assert issubclass(excecao, Exception)
        assert excecao.__mro__[1] is Exception
    for primeira in excecoes:
        for segunda in excecoes:
            if primeira is not segunda:
                assert not issubclass(primeira, segunda)


def test_capturar_a_excecao_do_resolver_nao_captura_as_outras():
    with pytest.raises(CaminhoYamlNaoResolvido) as erro:
        resolver_caminho({}, absoluto(seg("x")))
    assert not isinstance(erro.value, CaminhoYamlInvalido)
    assert not isinstance(erro.value, CaminhoYamlContextoInvalido)


def test_constantes_de_modulo_sao_exatamente_as_esperadas():
    nomes = [
        alvo.id
        for no in ARVORE_PRODUCAO.body
        if isinstance(no, ast.Assign)
        for alvo in no.targets
        if isinstance(alvo, ast.Name)
    ]
    assert nomes == [
        "__all__",
        "_AUSENTE",
        "_TIPO_INVALIDO",
        "_ITEM_CORRENTE_AUSENTE",
        "_RELATIVO_EM_ITERA_SOBRE",
        "_SEGMENTO_INEXISTENTE",
        "_TIPO_INCOMPATIVEL",
        "_TRAVESSIA_EM_NULO",
        "_ZERO_MATCHES",
        "_MULTIPLOS_MATCHES",
        "_ITERA_SOBRE_NAO_COLECAO",
        "_RAIZ",
        "_DECOMPOSICAO",
        "_ITEM_CORRENTE",
        "_SEGMENTO",
        "_SELETOR",
        "_ITERA_SOBRE",
        "_Decomposicao",
    ]


def test_constantes_de_codigo_sao_exatamente_o_vocabulario_fechado():
    assert set(_constantes_de_codigo()) == {
        "CaminhoYamlNaoResolvido",
        "resolver_caminho",
        "resolver_itera_sobre",
        "tipo_invalido",
        "item_corrente_ausente",
        "relativo_em_itera_sobre",
        "segmento_inexistente",
        "tipo_incompativel",
        "travessia_em_nulo",
        "zero_matches",
        "multiplos_matches",
        "itera_sobre_nao_colecao",
        "raiz",
        "decomposicao",
        "item_corrente",
        "segmento",
        "seletor",
        "itera_sobre",
        ": ",
    }


# ---------------------------------------------------------------------------
# N. Pureza estrutural do modulo de producao
# ---------------------------------------------------------------------------


def test_o_import_e_exatamente_um():
    assert not [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    assert _importados() == [("__future__", "annotations", None)]


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_nao_ha_captura_de_excecao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_nao_ha_raise_from():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise):
            assert no.cause is None


def test_todo_raise_e_da_excecao_publica():
    lancamentos = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Raise)]
    assert lancamentos
    for lancamento in lancamentos:
        chamada = lancamento.exc
        assert isinstance(chamada, ast.Call)
        assert isinstance(chamada.func, ast.Name)
        assert chamada.func.id == "_nao_resolvido"


def test_nao_ha_assert_em_producao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, ast.Assert)


def test_nao_ha_global_nem_nonlocal():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal))


def test_nao_ha_execucao_dinamica():
    proibidos = {"eval", "exec", "compile", "__import__", "globals", "locals", "vars"}
    assert not proibidos & NOMES_PRODUCAO


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
        "load",
        "dumps",
        "loads",
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


def test_nao_ha_relogio_aleatoriedade_ambiente_nem_logging():
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
        "choice",
        "shuffle",
        "uuid",
        "uuid4",
        "hashlib",
        "logging",
        "getLogger",
        "cache",
        "lru_cache",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_regex_nem_normalizacao():
    proibidos = {
        "re",
        "regex",
        "match",
        "fullmatch",
        "search",
        "sub",
        "unicodedata",
        "normalize",
        "strip",
        "lower",
        "upper",
        "casefold",
        "encode",
        "decode",
        "replace",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_copia_profunda_nem_conversao_de_estrutura():
    proibidos = {
        "deepcopy",
        "copy",
        "sorted",
        "reversed",
        "sort",
        "append",
        "extend",
        "update",
        "setdefault",
        "pop",
        "insert",
        "remove",
        "clear",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_dto_dataclass_nem_enum():
    proibidos = {"dataclass", "NamedTuple", "TypedDict", "Enum", "StrEnum"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_estado_mutavel_no_modulo():
    for nome, valor in vars(response_yaml_resolve).items():
        if nome.startswith("__") and nome.endswith("__"):
            continue
        if nome == "annotations":
            continue
        assert not isinstance(valor, (list, dict, set, bytearray))


def test_producao_nao_menciona_corpus_em_constante_de_codigo():
    """Só constantes executáveis são julgadas — docstring não é vocabulário."""
    for constante in _constantes_de_codigo():
        assert "knowledge" not in constante
        assert ".yaml" not in constante
        assert ".env" not in constante
        assert "http" not in constante
        assert "C:" not in constante


# ---------------------------------------------------------------------------
# O. Limites da fronteira
# ---------------------------------------------------------------------------


def test_a_fronteira_nao_e_consumida_pelo_indice():
    """`E1` continua sem consumir o resolver."""
    from casa77_sdr import response_index

    assert not hasattr(response_index, "resolver_caminho")
    assert not hasattr(response_index, "resolver_itera_sobre")
    assert not hasattr(response_index, "CaminhoYamlNaoResolvido")
    assert response_index.__all__ == ["IndiceInvalido", "validar_indice"]


def test_o_sucesso_nao_afirma_oficialidade_do_corpus():
    """Qualquer `dict` sintético serve de raiz: o resolver não conhece corpus."""
    raiz = {"objeto_totalmente_inventado": {"campo_inventado": "valor_inventado"}}
    resultado = resolver_caminho(
        raiz, absoluto(seg("objeto_totalmente_inventado"), seg("campo_inventado"))
    )
    assert resultado == "valor_inventado"


def test_a_fronteira_nao_aplica_c7():
    """Terminal `null` é resolução bem-sucedida, e não pendência."""
    raiz = {"campo_exemplo": None}
    assert resolver_caminho(raiz, absoluto(seg("campo_exemplo"))) is None


def test_a_fronteira_nao_formata_valor():
    raiz = {"campo_exemplo": 1234}
    resultado = resolver_caminho(raiz, absoluto(seg("campo_exemplo")))
    assert resultado == 1234
    assert type(resultado) is int


def test_nenhum_teste_desta_suite_toca_o_corpus():
    """A suíte é sintética: nada aqui lê o corpus versionado.

    Os alvos da busca são montados por concatenação para que a própria asserção
    não os introduza no arquivo e invalide o teste.
    """
    fonte = Path(__file__).read_text(encoding="utf-8")
    assert ("respostas" + "-aprovadas") not in fonte
    assert ("casa77" + ".yaml") not in fonte
    assert ("informacoes" + "-pendentes") not in fonte
