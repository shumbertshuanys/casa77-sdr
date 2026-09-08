"""Testes da validação estrutural **contextual** de `caminho_yaml` — `CY13`, linha 2.

A fronteira materializa **exclusivamente** a segunda responsabilidade de `CY13`:
**relativo somente em fragmento com `itera_sobre`** e **`@` proibido no próprio
`itera_sobre`**. Ela julga **a posição**, nunca a gramática — esta pertence a
`analisar_caminho_yaml` — e nunca o YAML factual — este pertence ao resolver,
que continua **NÃO IMPLEMENTADO**.

Estes testes provam a precedência do parser, a propagação **intacta** de
`CaminhoYamlInvalido`, as duas regras contextuais, a exigência de `bool` exato
para o contexto, o repasse do **mesmo** resultado do parser, a chamada **única**
ao parser, o vocabulário contextual fechado, a independência entre as duas
exceções, o contrato público e a pureza do módulo de produção. Eles **não**
transformam em norma coisa alguma sobre resolução, existência de chave, *match*
de seletor, `C-7` ou índice físico. **Nenhum teste toca o corpus versionado**:
todos os casos são **sintéticos**.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr import response_yaml_path_context
from casa77_sdr.response_yaml_path import CaminhoYamlInvalido, analisar_caminho_yaml
from casa77_sdr.response_yaml_path_context import (
    CaminhoYamlContextoInvalido,
    validar_caminho_de_binding,
    validar_itera_sobre,
)

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_yaml_path_context.py"
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


def _importados():
    """Pares `(modulo, nome_importado, apelido)` de todo `from ... import ...`."""
    return [
        (no.module, alias.name, alias.asname)
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.ImportFrom)
        for alias in no.names
    ]


def erro_de_binding(caminho, contexto):
    """Mensagem da recusa **contextual** de um `caminho_yaml` de *binding*."""
    with pytest.raises(CaminhoYamlContextoInvalido) as erro:
        validar_caminho_de_binding(caminho, fragmento_itera=contexto)
    return str(erro.value)


def erro_de_itera(caminho):
    """Mensagem da recusa **contextual** de um `itera_sobre`."""
    with pytest.raises(CaminhoYamlContextoInvalido) as erro:
        validar_itera_sobre(caminho)
    return str(erro.value)


class ContextoVerdadeiro:
    """Objeto **truthy** que não é `bool`: prova que não há coerção."""

    def __bool__(self):
        return True


class ContextoFalso:
    """Objeto **falsy** que não é `bool`: prova que não há coerção."""

    def __bool__(self):
        return False


class InteiroFalso(int):
    """Subclasse de `int` valendo `0`: `bool` é exato, não estrutural."""


CAMINHOS_INVALIDOS = [
    "",
    ".",
    "a.",
    ".a",
    "a..b",
    "@@",
    "@a",
    "@.",
    "@[x=y]",
    "a b",
    "a-b",
    "a@b",
    "a.@b",
    "a[x=y",
    "a[x=y]]",
    "a[x=y][z=w]",
    "a[x=y]resto",
    "a[]",
    "a[x]",
    "a[=x]",
    "a[x=]",
    "a]",
    "[x=y]",
    "123",
    "123.",
    "a.123",
    "a[123=x]",
    "@.123",
    "colecao[0]",
    "colecao[0=x]",
    "café",
]

ENTRADAS_NAO_STR = [None, 0, 1, True, False, 2.0, [], (), {}, b"a"]

CONTEXTOS_INVALIDOS = [
    None,
    0,
    1,
    -1,
    "sim",
    "",
    "True",
    [],
    [True],
    (),
    {},
    2.0,
    0.0,
    b"",
    ContextoVerdadeiro(),
    ContextoFalso(),
    InteiroFalso(0),
]


# ---------------------------------------------------------------------------
# A. Aceitacao — `caminho_yaml` de binding
# ---------------------------------------------------------------------------


def test_absoluto_sem_itera_sobre_e_aceito():
    assert validar_caminho_de_binding("bloco_exemplo", fragmento_itera=False) == (
        False,
        (("bloco_exemplo", None),),
    )


def test_absoluto_com_itera_sobre_e_aceito():
    """Iterar não proíbe endereçar a raiz do YAML."""
    assert validar_caminho_de_binding("bloco_exemplo", fragmento_itera=True) == (
        False,
        (("bloco_exemplo", None),),
    )


def test_absoluto_de_varios_segmentos_e_aceito_nas_duas_situacoes():
    esperado = (False, (("bloco_exemplo", None), ("campo_exemplo", None)))
    caminho = "bloco_exemplo.campo_exemplo"
    assert validar_caminho_de_binding(caminho, fragmento_itera=False) == esperado
    assert validar_caminho_de_binding(caminho, fragmento_itera=True) == esperado


def test_relativo_com_itera_sobre_e_aceito():
    assert validar_caminho_de_binding("@.campo_exemplo", fragmento_itera=True) == (
        True,
        (("campo_exemplo", None),),
    )


def test_relativo_de_varios_segmentos_com_itera_sobre_e_aceito():
    assert validar_caminho_de_binding(
        "@.submapa_exemplo.campo_exemplo", fragmento_itera=True
    ) == (True, (("submapa_exemplo", None), ("campo_exemplo", None)))


def test_arroba_isolado_com_itera_sobre_e_aceito():
    """`CY11`: `@` sozinho é o próprio item corrente, e ele existe ao iterar."""
    assert validar_caminho_de_binding("@", fragmento_itera=True) == (True, ())


def test_absoluto_com_seletor_e_aceito():
    assert validar_caminho_de_binding(
        "bloco_exemplo.colecao_exemplo[id=item_exemplo].campo_exemplo",
        fragmento_itera=False,
    ) == (
        False,
        (
            ("bloco_exemplo", None),
            ("colecao_exemplo", ("id", "item_exemplo")),
            ("campo_exemplo", None),
        ),
    )


def test_relativo_com_seletor_e_aceito_quando_ha_itera_sobre():
    assert validar_caminho_de_binding(
        "@.colecao_exemplo[id=item_exemplo].campo_exemplo", fragmento_itera=True
    ) == (
        True,
        (("colecao_exemplo", ("id", "item_exemplo")), ("campo_exemplo", None)),
    )


def test_seletor_com_literal_numerico_e_aceito():
    """`CY7`: o literal seletor é sempre semanticamente uma `str`."""
    assert validar_caminho_de_binding(
        "colecao_exemplo[id=2026]", fragmento_itera=False
    ) == (False, (("colecao_exemplo", ("id", "2026")),))


# ---------------------------------------------------------------------------
# B. Aceitacao — `itera_sobre`
# ---------------------------------------------------------------------------


def test_itera_sobre_absoluto_e_aceito():
    assert validar_itera_sobre("colecao_exemplo") == (
        False,
        (("colecao_exemplo", None),),
    )


def test_itera_sobre_absoluto_de_varios_segmentos_e_aceito():
    assert validar_itera_sobre("bloco_exemplo.colecao_exemplo") == (
        False,
        (("bloco_exemplo", None), ("colecao_exemplo", None)),
    )


def test_itera_sobre_com_seletor_e_aceito():
    """`CY12`: seletores estruturais são permitidos em `itera_sobre`."""
    assert validar_itera_sobre(
        "bloco_exemplo.colecao_exemplo[id=item_exemplo].sub_colecao"
    ) == (
        False,
        (
            ("bloco_exemplo", None),
            ("colecao_exemplo", ("id", "item_exemplo")),
            ("sub_colecao", None),
        ),
    )


def test_itera_sobre_nao_recebe_contexto():
    """A proibição de `@` é incondicional: não há parâmetro de contexto."""
    assinatura = inspect.signature(validar_itera_sobre)
    assert list(assinatura.parameters) == ["caminho"]


# ---------------------------------------------------------------------------
# C. Recusa — relativo sem `itera_sobre`
# ---------------------------------------------------------------------------


def test_relativo_sem_itera_sobre_e_recusado():
    assert (
        erro_de_binding("@.campo_exemplo", False)
        == "relativo_sem_itera_sobre: caminho_yaml"
    )


def test_arroba_isolado_sem_itera_sobre_e_recusado():
    assert erro_de_binding("@", False) == "relativo_sem_itera_sobre: caminho_yaml"


def test_relativo_com_seletor_sem_itera_sobre_e_recusado():
    assert (
        erro_de_binding("@.colecao_exemplo[id=item_exemplo]", False)
        == "relativo_sem_itera_sobre: caminho_yaml"
    )


def test_relativo_profundo_sem_itera_sobre_e_recusado():
    assert (
        erro_de_binding("@.a.b.c", False) == "relativo_sem_itera_sobre: caminho_yaml"
    )


def test_a_recusa_de_relativo_e_do_tipo_contextual():
    with pytest.raises(CaminhoYamlContextoInvalido) as erro:
        validar_caminho_de_binding("@.campo_exemplo", fragmento_itera=False)
    assert type(erro.value) is CaminhoYamlContextoInvalido
    assert not isinstance(erro.value, CaminhoYamlInvalido)


# ---------------------------------------------------------------------------
# D. Recusa — `@` no proprio `itera_sobre`
# ---------------------------------------------------------------------------


def test_itera_sobre_relativo_e_recusado():
    assert erro_de_itera("@.colecao_exemplo") == "arroba_em_itera_sobre: itera_sobre"


def test_itera_sobre_arroba_isolado_e_recusado():
    assert erro_de_itera("@") == "arroba_em_itera_sobre: itera_sobre"


def test_itera_sobre_relativo_com_seletor_e_recusado():
    assert (
        erro_de_itera("@.colecao_exemplo[id=item_exemplo]")
        == "arroba_em_itera_sobre: itera_sobre"
    )


def test_a_recusa_de_itera_sobre_e_do_tipo_contextual():
    with pytest.raises(CaminhoYamlContextoInvalido) as erro:
        validar_itera_sobre("@")
    assert type(erro.value) is CaminhoYamlContextoInvalido
    assert not isinstance(erro.value, CaminhoYamlInvalido)


def test_o_mesmo_relativo_e_aceito_em_binding_e_recusado_em_itera_sobre():
    """A `str` é a mesma; muda **somente** a posição no índice."""
    caminho = "@.campo_exemplo"
    assert validar_caminho_de_binding(caminho, fragmento_itera=True)[0] is True
    assert erro_de_itera(caminho) == "arroba_em_itera_sobre: itera_sobre"


# ---------------------------------------------------------------------------
# E. Tipo do contexto
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("contexto", CONTEXTOS_INVALIDOS)
def test_contexto_que_nao_e_bool_exato_e_recusado(contexto):
    assert erro_de_binding("bloco_exemplo", contexto) == "tipo_invalido: contexto"


@pytest.mark.parametrize("contexto", [True, False])
def test_somente_bool_exato_e_aceito(contexto):
    assert validar_caminho_de_binding("bloco_exemplo", fragmento_itera=contexto) == (
        False,
        (("bloco_exemplo", None),),
    )
    assert type(contexto) is bool


def test_contexto_truthy_nao_substitui_itera_sobre():
    """Um objeto verdadeiro **não** libera o caminho relativo: não há coerção."""
    assert erro_de_binding("@.a", ContextoVerdadeiro()) == "tipo_invalido: contexto"
    assert erro_de_binding("@.a", 1) == "tipo_invalido: contexto"
    assert erro_de_binding("@.a", "sim") == "tipo_invalido: contexto"


def test_contexto_falsy_nao_substitui_a_ausencia_de_itera_sobre():
    assert erro_de_binding("@.a", ContextoFalso()) == "tipo_invalido: contexto"
    assert erro_de_binding("@.a", 0) == "tipo_invalido: contexto"


def test_tipo_do_contexto_vence_a_regra_contextual():
    """Com caminho relativo e contexto inválido, a categoria é `tipo_invalido`."""
    assert erro_de_binding("@", None) == "tipo_invalido: contexto"
    assert erro_de_binding("@.a.b", []) == "tipo_invalido: contexto"


def test_contexto_e_keyword_only():
    assinatura = inspect.signature(validar_caminho_de_binding)
    parametro = assinatura.parameters["fragmento_itera"]
    assert parametro.kind is inspect.Parameter.KEYWORD_ONLY
    assert parametro.default is inspect.Parameter.empty
    with pytest.raises(TypeError):
        validar_caminho_de_binding("bloco_exemplo", True)


def test_contexto_e_obrigatorio():
    with pytest.raises(TypeError):
        validar_caminho_de_binding("bloco_exemplo")


# ---------------------------------------------------------------------------
# F. Precedencia — o parser vem primeiro
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("contexto", [None, 0, 1, "sim", []])
def test_caminho_invalido_vence_contexto_invalido(contexto):
    """Gramática antes de contexto: a exceção continua sendo a do parser."""
    with pytest.raises(CaminhoYamlInvalido) as erro:
        validar_caminho_de_binding("a..b", fragmento_itera=contexto)
    assert str(erro.value) == "forma_invalida: segmento"
    assert not isinstance(erro.value, CaminhoYamlContextoInvalido)


def test_relativo_malformado_vence_contexto_invalido():
    with pytest.raises(CaminhoYamlInvalido) as erro:
        validar_caminho_de_binding("@@", fragmento_itera=None)
    assert str(erro.value) == "forma_invalida: caminho"


def test_chave_nao_enderecavel_vence_contexto_invalido():
    with pytest.raises(CaminhoYamlInvalido) as erro:
        validar_caminho_de_binding("@.123", fragmento_itera=0)
    assert str(erro.value) == "chave_nao_enderecavel: chave"


def test_entrada_nao_str_vence_contexto_invalido():
    with pytest.raises(CaminhoYamlInvalido) as erro:
        validar_caminho_de_binding(None, fragmento_itera=None)
    assert str(erro.value) == "tipo_invalido: caminho"


def test_tipo_do_caminho_e_do_contexto_tem_localizadores_distintos():
    """`caminho` é do parser; `contexto` é desta fronteira. Nunca se confundem."""
    with pytest.raises(CaminhoYamlInvalido) as do_parser:
        validar_caminho_de_binding(None, fragmento_itera=True)
    assert str(do_parser.value) == "tipo_invalido: caminho"
    assert erro_de_binding("a", None) == "tipo_invalido: contexto"


# ---------------------------------------------------------------------------
# G. Propagacao intacta de `CaminhoYamlInvalido`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("caminho", CAMINHOS_INVALIDOS)
def test_binding_propaga_a_excecao_do_parser_sem_transformacao(caminho):
    with pytest.raises(CaminhoYamlInvalido) as esperado:
        analisar_caminho_yaml(caminho)
    with pytest.raises(CaminhoYamlInvalido) as obtido:
        validar_caminho_de_binding(caminho, fragmento_itera=True)
    assert type(obtido.value) is type(esperado.value)
    assert str(obtido.value) == str(esperado.value)


@pytest.mark.parametrize("caminho", CAMINHOS_INVALIDOS)
def test_itera_sobre_propaga_a_excecao_do_parser_sem_transformacao(caminho):
    with pytest.raises(CaminhoYamlInvalido) as esperado:
        analisar_caminho_yaml(caminho)
    with pytest.raises(CaminhoYamlInvalido) as obtido:
        validar_itera_sobre(caminho)
    assert type(obtido.value) is type(esperado.value)
    assert str(obtido.value) == str(esperado.value)


@pytest.mark.parametrize("entrada", ENTRADAS_NAO_STR)
def test_entrada_nao_str_falha_como_no_parser(entrada):
    with pytest.raises(CaminhoYamlInvalido) as no_binding:
        validar_caminho_de_binding(entrada, fragmento_itera=True)
    with pytest.raises(CaminhoYamlInvalido) as no_itera:
        validar_itera_sobre(entrada)
    assert str(no_binding.value) == "tipo_invalido: caminho"
    assert str(no_itera.value) == "tipo_invalido: caminho"


def test_a_propagacao_nao_encadeia_causa_nem_contexto():
    """Zero `raise from` e zero `raise` dentro de `except`."""
    for chamada in (
        lambda: validar_caminho_de_binding("a..b", fragmento_itera=True),
        lambda: validar_itera_sobre("a..b"),
    ):
        with pytest.raises(CaminhoYamlInvalido) as erro:
            chamada()
        assert erro.value.__cause__ is None
        assert erro.value.__context__ is None


def test_a_recusa_contextual_tambem_nao_encadeia():
    with pytest.raises(CaminhoYamlContextoInvalido) as erro:
        validar_itera_sobre("@")
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_subclasse_de_str_e_recusada_pelo_parser():
    class Caminho(str):
        pass

    with pytest.raises(CaminhoYamlInvalido) as erro:
        validar_caminho_de_binding(Caminho("bloco_exemplo"), fragmento_itera=True)
    assert str(erro.value) == "tipo_invalido: caminho"


# ---------------------------------------------------------------------------
# H. Retorno — o mesmo resultado do parser
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "caminho",
    [
        "bloco_exemplo",
        "bloco_exemplo.campo_exemplo",
        "colecao_exemplo[id=item_exemplo]",
        "@",
        "@.campo_exemplo",
        "@.colecao_exemplo[id=item_exemplo].campo_exemplo",
    ],
)
def test_binding_devolve_o_que_o_parser_devolve(caminho):
    assert validar_caminho_de_binding(
        caminho, fragmento_itera=True
    ) == analisar_caminho_yaml(caminho)


@pytest.mark.parametrize(
    "caminho",
    [
        "colecao_exemplo",
        "bloco_exemplo.colecao_exemplo",
        "bloco_exemplo.colecao_exemplo[id=item_exemplo]",
    ],
)
def test_itera_sobre_devolve_o_que_o_parser_devolve(caminho):
    assert validar_itera_sobre(caminho) == analisar_caminho_yaml(caminho)


def test_forma_da_saida_e_a_do_parser():
    resultado = validar_caminho_de_binding("a.b[c=d]", fragmento_itera=False)
    assert type(resultado) is tuple
    assert len(resultado) == 2
    relativo, segmentos = resultado
    assert type(relativo) is bool
    assert type(segmentos) is tuple
    assert segmentos == (("a", None), ("b", ("c", "d")))


def test_saida_nao_contem_estrutura_mutavel():
    for resultado in (
        validar_caminho_de_binding("@.a[b=c]", fragmento_itera=True),
        validar_itera_sobre("a.b[c=d]"),
    ):
        pilha = [resultado]
        while pilha:
            no = pilha.pop()
            assert not isinstance(no, (list, dict, set, bytearray))
            if isinstance(no, tuple):
                pilha.extend(no)


def test_binding_repassa_o_objeto_identico_do_parser(monkeypatch):
    """Identidade, não igualdade: nada é reconstruído."""
    sentinela = (False, (("marcador_sintetico", None),))
    monkeypatch.setattr(
        response_yaml_path_context,
        "_analisar_caminho_yaml",
        lambda caminho: sentinela,
    )
    assert (
        validar_caminho_de_binding("qualquer", fragmento_itera=False) is sentinela
    )
    assert validar_caminho_de_binding("qualquer", fragmento_itera=True) is sentinela


def test_itera_sobre_repassa_o_objeto_identico_do_parser(monkeypatch):
    sentinela = (False, (("marcador_sintetico", None),))
    monkeypatch.setattr(
        response_yaml_path_context,
        "_analisar_caminho_yaml",
        lambda caminho: sentinela,
    )
    assert validar_itera_sobre("qualquer") is sentinela


# ---------------------------------------------------------------------------
# I. O parser e chamado uma unica vez
# ---------------------------------------------------------------------------


def _espiao(monkeypatch, resultado):
    chamadas = []

    def espiao(caminho):
        chamadas.append(caminho)
        return resultado

    monkeypatch.setattr(
        response_yaml_path_context, "_analisar_caminho_yaml", espiao
    )
    return chamadas


def test_binding_chama_o_parser_uma_unica_vez_no_sucesso(monkeypatch):
    chamadas = _espiao(monkeypatch, (True, ()))
    validar_caminho_de_binding("entrada_sintetica", fragmento_itera=True)
    assert chamadas == ["entrada_sintetica"]


def test_binding_chama_o_parser_uma_unica_vez_na_recusa_contextual(monkeypatch):
    chamadas = _espiao(monkeypatch, (True, ()))
    with pytest.raises(CaminhoYamlContextoInvalido):
        validar_caminho_de_binding("entrada_sintetica", fragmento_itera=False)
    assert chamadas == ["entrada_sintetica"]


def test_binding_chama_o_parser_uma_unica_vez_na_recusa_de_tipo(monkeypatch):
    chamadas = _espiao(monkeypatch, (False, ()))
    with pytest.raises(CaminhoYamlContextoInvalido):
        validar_caminho_de_binding("entrada_sintetica", fragmento_itera=None)
    assert chamadas == ["entrada_sintetica"]


def test_itera_sobre_chama_o_parser_uma_unica_vez_no_sucesso(monkeypatch):
    chamadas = _espiao(monkeypatch, (False, ()))
    validar_itera_sobre("entrada_sintetica")
    assert chamadas == ["entrada_sintetica"]


def test_itera_sobre_chama_o_parser_uma_unica_vez_na_recusa(monkeypatch):
    chamadas = _espiao(monkeypatch, (True, ()))
    with pytest.raises(CaminhoYamlContextoInvalido):
        validar_itera_sobre("entrada_sintetica")
    assert chamadas == ["entrada_sintetica"]


def test_a_forma_vem_do_parser_e_nao_da_str(monkeypatch):
    """Se o parser disser `relativo`, a regra vale mesmo sem `@` na `str`."""
    monkeypatch.setattr(
        response_yaml_path_context,
        "_analisar_caminho_yaml",
        lambda caminho: (True, (("a", None),)),
    )
    assert (
        erro_de_binding("sem_arroba_algum", False)
        == "relativo_sem_itera_sobre: caminho_yaml"
    )
    assert erro_de_itera("sem_arroba_algum") == "arroba_em_itera_sobre: itera_sobre"


def test_a_forma_vem_do_parser_e_nao_do_texto_com_arroba(monkeypatch):
    """E se o parser disser `absoluto`, nada é recusado por causa do texto."""
    esperado = (False, (("a", None),))
    monkeypatch.setattr(
        response_yaml_path_context,
        "_analisar_caminho_yaml",
        lambda caminho: esperado,
    )
    assert validar_caminho_de_binding("@.a", fragmento_itera=False) is esperado
    assert validar_itera_sobre("@.a") is esperado


# ---------------------------------------------------------------------------
# J. Vocabulario contextual fechado
# ---------------------------------------------------------------------------


def test_as_tres_falhas_contextuais_sao_exatamente_estas():
    observadas = {
        erro_de_binding("a", None),
        erro_de_binding("@", False),
        erro_de_itera("@"),
    }
    assert observadas == {
        "tipo_invalido: contexto",
        "relativo_sem_itera_sobre: caminho_yaml",
        "arroba_em_itera_sobre: itera_sobre",
    }


@pytest.mark.parametrize(
    "mensagem",
    [
        "tipo_invalido: contexto",
        "relativo_sem_itera_sobre: caminho_yaml",
        "arroba_em_itera_sobre: itera_sobre",
    ],
)
def test_mensagem_tem_forma_categoria_localizador(mensagem):
    assert mensagem.count(": ") == 1
    categoria, _, localizador = mensagem.partition(": ")
    assert categoria in {
        "tipo_invalido",
        "relativo_sem_itera_sobre",
        "arroba_em_itera_sobre",
    }
    assert localizador in {"contexto", "caminho_yaml", "itera_sobre"}


def test_a_mensagem_contextual_nao_ecoa_a_entrada():
    entrada = "@.segredo_sintetico_nao_deve_aparecer[id=valor_sintetico]"
    mensagem = erro_de_binding(entrada, False)
    assert "segredo_sintetico_nao_deve_aparecer" not in mensagem
    assert "valor_sintetico" not in mensagem
    assert mensagem == "relativo_sem_itera_sobre: caminho_yaml"


def test_a_mensagem_de_tipo_nao_ecoa_o_tipo_concreto():
    for contexto in (None, 1, "sim", [], ContextoVerdadeiro()):
        mensagem = erro_de_binding("bloco_exemplo", contexto)
        assert mensagem == "tipo_invalido: contexto"
        assert "None" not in mensagem
        assert "int" not in mensagem
        assert "str" not in mensagem
        assert "list" not in mensagem
        assert "Contexto" not in mensagem


def test_a_mensagem_nao_carrega_posicao_indice_nem_cardinalidade():
    for mensagem in (
        erro_de_binding("@.a.b.c", False),
        erro_de_itera("@.a.b.c"),
        erro_de_binding("a.b.c", None),
    ):
        assert not any(caractere in "0123456789" for caractere in mensagem)


def test_o_vocabulario_contextual_nao_colide_com_o_do_parser():
    """`tipo_invalido` é a única categoria comum, e o localizador difere."""
    assert erro_de_binding("a", None) == "tipo_invalido: contexto"
    with pytest.raises(CaminhoYamlInvalido) as erro:
        analisar_caminho_yaml(None)
    assert str(erro.value) == "tipo_invalido: caminho"


# ---------------------------------------------------------------------------
# K. Zero resolucao factual
# ---------------------------------------------------------------------------


def test_objeto_inexistente_e_aceito():
    """Gramatical e bem posicionado basta: existência é do resolver."""
    assert validar_caminho_de_binding(
        "objeto_inexistente.campo", fragmento_itera=False
    ) == (False, (("objeto_inexistente", None), ("campo", None)))


def test_seletor_sem_match_em_corpus_algum_e_aceito():
    assert validar_caminho_de_binding(
        "colecao_inexistente[id=item_que_nao_existe]", fragmento_itera=False
    ) == (False, (("colecao_inexistente", ("id", "item_que_nao_existe")),))


def test_relativo_inexistente_e_aceito_quando_ha_itera_sobre():
    assert validar_caminho_de_binding(
        "@.campo_que_nao_existe", fragmento_itera=True
    ) == (True, (("campo_que_nao_existe", None),))


def test_itera_sobre_de_colecao_inexistente_e_aceito():
    """Terminar em coleção é juízo do resolver, não desta fronteira."""
    assert validar_itera_sobre("bloco_inexistente.colecao_inexistente") == (
        False,
        (("bloco_inexistente", None), ("colecao_inexistente", None)),
    )


def test_itera_sobre_apontando_para_escalar_sintetico_e_aceito():
    assert validar_itera_sobre("bloco_exemplo.campo_escalar_sintetico") == (
        False,
        (("bloco_exemplo", None), ("campo_escalar_sintetico", None)),
    )


def test_o_resultado_e_deterministico():
    caminho = "@.colecao_exemplo[id=item_exemplo].campo_exemplo"
    primeiro = validar_caminho_de_binding(caminho, fragmento_itera=True)
    for _ in range(5):
        assert validar_caminho_de_binding(caminho, fragmento_itera=True) == primeiro
    assert erro_de_itera(caminho) == erro_de_itera(caminho)


def test_a_entrada_nao_e_alterada():
    caminho = "@.colecao_exemplo[id=item_exemplo]"
    copia = str(caminho)
    validar_caminho_de_binding(caminho, fragmento_itera=True)
    assert caminho == copia


# ---------------------------------------------------------------------------
# L. Contrato publico
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_os_tres_nomes():
    assert response_yaml_path_context.__all__ == [
        "CaminhoYamlContextoInvalido",
        "validar_caminho_de_binding",
        "validar_itera_sobre",
    ]


def test_nao_ha_nome_publico_fora_de_all():
    publicos = {
        nome
        for nome in vars(response_yaml_path_context)
        if not nome.startswith("_") and nome not in {"annotations"}
    }
    assert publicos == set(response_yaml_path_context.__all__)


def test_producao_declara_uma_unica_classe_e_duas_funcoes_publicas():
    classes = [
        no.name for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)
    ]
    assert classes == ["CaminhoYamlContextoInvalido"]
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    publicas = [nome for nome in funcoes if not nome.startswith("_")]
    assert publicas == ["validar_caminho_de_binding", "validar_itera_sobre"]


def test_assinatura_do_binding_e_a_arbitrada():
    assinatura = inspect.signature(validar_caminho_de_binding)
    assert list(assinatura.parameters) == ["caminho", "fragmento_itera"]
    caminho = assinatura.parameters["caminho"]
    assert caminho.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert caminho.default is inspect.Parameter.empty
    assert assinatura.return_annotation == (
        "tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]"
    )


def test_assinatura_do_itera_sobre_e_a_arbitrada():
    assinatura = inspect.signature(validar_itera_sobre)
    parametro = assinatura.parameters["caminho"]
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parametro.default is inspect.Parameter.empty
    assert assinatura.return_annotation == (
        "tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]"
    )


def test_nao_e_exportado_pelo_pacote():
    for nome in (
        "CaminhoYamlContextoInvalido",
        "validar_caminho_de_binding",
        "validar_itera_sobre",
    ):
        assert not hasattr(casa77_sdr, nome)
        assert nome not in getattr(casa77_sdr, "__all__", [])


def test_as_duas_excecoes_sao_independentes():
    assert issubclass(CaminhoYamlContextoInvalido, Exception)
    assert CaminhoYamlContextoInvalido.__mro__[1] is Exception
    assert not issubclass(CaminhoYamlContextoInvalido, CaminhoYamlInvalido)
    assert not issubclass(CaminhoYamlInvalido, CaminhoYamlContextoInvalido)


def test_capturar_uma_excecao_nao_captura_a_outra():
    with pytest.raises(CaminhoYamlContextoInvalido):
        validar_itera_sobre("@")
    with pytest.raises(CaminhoYamlInvalido):
        validar_itera_sobre("@@")


def test_producao_nao_importa_a_excecao_do_parser():
    assert not hasattr(response_yaml_path_context, "CaminhoYamlInvalido")
    assert "CaminhoYamlInvalido" not in NOMES_PRODUCAO
    assert "CaminhoYamlInvalido" not in [nome for _, nome, _ in _importados()]


def test_o_parser_e_importado_sob_nome_privado():
    assert (
        response_yaml_path_context._analisar_caminho_yaml is analisar_caminho_yaml
    )
    assert not hasattr(response_yaml_path_context, "analisar_caminho_yaml")


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
        "_TIPO_INVALIDO",
        "_RELATIVO_SEM_ITERA_SOBRE",
        "_ARROBA_EM_ITERA_SOBRE",
        "_CONTEXTO",
        "_CAMINHO_YAML",
        "_ITERA_SOBRE",
    ]


def test_constantes_de_codigo_sao_exatamente_o_vocabulario_fechado():
    assert set(_constantes_de_codigo()) == {
        "CaminhoYamlContextoInvalido",
        "validar_caminho_de_binding",
        "validar_itera_sobre",
        "tipo_invalido",
        "relativo_sem_itera_sobre",
        "arroba_em_itera_sobre",
        "contexto",
        "caminho_yaml",
        "itera_sobre",
        ": ",
    }


# ---------------------------------------------------------------------------
# M. Pureza do modulo de producao
# ---------------------------------------------------------------------------


def test_os_imports_sao_exatamente_dois_e_fechados():
    assert not [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    assert _importados() == [
        ("__future__", "annotations", None),
        (
            "casa77_sdr.response_yaml_path",
            "analisar_caminho_yaml",
            "_analisar_caminho_yaml",
        ),
    ]


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


def test_todo_raise_e_da_excecao_contextual():
    lancamentos = [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Raise)]
    assert len(lancamentos) == 3
    for lancamento in lancamentos:
        chamada = lancamento.exc
        assert isinstance(chamada, ast.Call)
        assert isinstance(chamada.func, ast.Name)
        assert chamada.func.id == "_invalido"


def test_a_producao_nao_reinterpreta_a_str():
    """Zero busca de `@`, zero `startswith`, zero segunda leitura da entrada."""
    proibidos = {
        "startswith",
        "endswith",
        "find",
        "rfind",
        "index",
        "split",
        "rsplit",
        "partition",
        "count",
        "join",
        "format",
    }
    assert not proibidos & NOMES_PRODUCAO
    for constante in _constantes_de_codigo():
        assert "@" not in constante


def test_nao_ha_normalizacao_nem_coercao():
    proibidos = {
        "strip",
        "lstrip",
        "rstrip",
        "lower",
        "upper",
        "casefold",
        "title",
        "capitalize",
        "encode",
        "decode",
        "translate",
        "replace",
        "normalize",
        "unicodedata",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_regex():
    proibidos = {"re", "regex", "match", "fullmatch", "search", "sub", "compile"}
    assert not proibidos & NOMES_PRODUCAO


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


def test_nao_ha_dto_dataclass_nem_enum():
    proibidos = {"dataclass", "NamedTuple", "TypedDict", "Enum", "StrEnum"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_dict_nem_conjunto_no_codigo():
    assert not [
        no
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.Dict, ast.DictComp, ast.Set, ast.SetComp))
    ]
    proibidos = {"dict", "set", "frozenset", "Counter", "defaultdict", "OrderedDict"}
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_global_nem_nonlocal():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Global, ast.Nonlocal))


def test_nao_ha_assert_em_producao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, ast.Assert)


def test_nao_ha_estado_mutavel_no_modulo():
    for nome, valor in vars(response_yaml_path_context).items():
        if nome.startswith("__") and nome.endswith("__"):
            continue
        if nome == "annotations":
            continue
        assert not isinstance(valor, (list, dict, set, bytearray))


def test_producao_nao_menciona_corpus_caminho_nem_url():
    for constante in _constantes_de_codigo():
        assert "knowledge" not in constante
        assert ".yaml" not in constante
        assert ".md" not in constante
        assert ".env" not in constante
        assert "http" not in constante
        assert "C:" not in constante
        assert "/home/" not in constante


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert validar_itera_sobre("Bloco_I") == (False, (("Bloco_I", None),))


# ---------------------------------------------------------------------------
# N. Limites da fronteira
# ---------------------------------------------------------------------------


def test_a_fronteira_nao_e_consumida_pelo_indice():
    """`E1` ainda **não** integra esta validação: `response_index` não a importa."""
    from casa77_sdr import response_index

    assert not hasattr(response_index, "validar_caminho_de_binding")
    assert not hasattr(response_index, "validar_itera_sobre")
    assert not hasattr(response_index, "CaminhoYamlContextoInvalido")
    assert response_index.__all__ == ["IndiceInvalido", "validar_indice"]


def test_a_fronteira_nao_substitui_o_parser():
    """A gramática continua acessível e inalterada na sua própria fronteira."""
    assert analisar_caminho_yaml("@.a") == (True, (("a", None),))


def test_nenhum_teste_desta_suite_toca_o_corpus():
    """A suíte é sintética: nada aqui lê o corpus versionado.

    Os alvos da busca são montados por concatenação para que a própria asserção
    não os introduza no arquivo e invalide o teste.
    """
    fonte = Path(__file__).read_text(encoding="utf-8")
    assert ("respostas" + "-aprovadas") not in fonte
    assert ("casa77" + ".yaml") not in fonte
    assert ("informacoes" + "-pendentes") not in fonte
