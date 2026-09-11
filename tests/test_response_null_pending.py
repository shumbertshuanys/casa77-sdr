"""Testes da recusa determinística de `null` e `status: pendente` — `C-7`.

A fronteira materializa **somente** o reconhecimento e a recusa do **valor
terminal já resolvido**: `None` e o `dict` **exato** cuja chave literal `status`
tem por valor a `str` **exata** `pendente`. Qualquer outro valor volta **pelo
próprio objeto**.

Estes testes provam os dois casos de recusa, a devolução por identidade, a
ausência de travessia para chaves irmãs e descendentes, a comparação literal sem
normalização, a recusa da forma canônica a subclasses de `dict` e de `str`, a
não-mutação, o determinismo, o vocabulário fechado de duas mensagens, a ausência
de vazamento, a composição sintética com o resolver factual e a pureza
estrutural do módulo de produção.

**Todo o corpus é sintético.** Nenhum preço, capacidade, horário, prazo,
percentual ou quantidade real aparece, e **nada em `knowledge/**` é lido**. Os
valores existem apenas para exercitar a forma do terminal.
"""

from __future__ import annotations

import ast
import copy
import inspect
from pathlib import Path

import pytest

from casa77_sdr import response_null_pending
from casa77_sdr.response_null_pending import (
    ValorNuloOuPendente,
    recusar_nulo_ou_pendente,
)
from casa77_sdr.response_yaml_resolve import (
    CaminhoYamlNaoResolvido,
    resolver_caminho,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "response_null_pending.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

# Sentinela sintética: jamais deve aparecer na mensagem da exceção.
SENTINELA = "SENTINELA_NAO_DEVE_VAZAR"


# ---------------------------------------------------------------------------
# A. Caso A — `null`


def test_none_e_recusado() -> None:
    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(None)

    assert str(erro.value) == "nulo: valor"


@pytest.mark.parametrize("valor", [0, 0.0, False, "", [], {}, ()])
def test_falso_nao_e_nulo(valor: object) -> None:
    """*Falsy* não é `null`: só `None` é `None`."""
    assert recusar_nulo_ou_pendente(valor) is valor


@pytest.mark.parametrize("valor", ["null", "None", "NULL", "none", "nulo"])
def test_texto_de_nulo_nao_e_nulo(valor: str) -> None:
    assert recusar_nulo_ou_pendente(valor) is valor


# ---------------------------------------------------------------------------
# B. Caso B — estrutura `pendente`


def test_estrutura_pendente_e_recusada() -> None:
    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente({"status": "pendente"})

    assert str(erro.value) == "pendente: status"


def test_estrutura_pendente_com_chaves_irmas_e_recusada() -> None:
    terminal = {
        "status": "pendente",
        "observacao_sintetica": SENTINELA,
        "outro_campo": [SENTINELA, 123],
    }

    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(terminal)

    assert str(erro.value) == "pendente: status"


def test_chave_irma_nao_vaza_na_mensagem() -> None:
    terminal = {"status": "pendente", "irma": SENTINELA}

    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(terminal)

    assert SENTINELA not in str(erro.value)
    assert "irma" not in str(erro.value)


@pytest.mark.parametrize(
    "terminal",
    [
        {},
        {"status": "aprovado"},
        {"status": "APROVADO"},
        {"outro": "pendente"},
        {"estado": "pendente"},
    ],
)
def test_mapa_fora_da_forma_canonica_e_devolvido(terminal: dict) -> None:
    assert recusar_nulo_ou_pendente(terminal) is terminal


# ---------------------------------------------------------------------------
# C. Strings isoladas não são `C-7`


@pytest.mark.parametrize("valor", ["pendente", "PENDENTE", "Pendente", "status"])
def test_string_isolada_nao_e_estrutura_pendente(valor: str) -> None:
    assert recusar_nulo_ou_pendente(valor) is valor


# ---------------------------------------------------------------------------
# D. Terminal somente — nenhuma travessia


@pytest.mark.parametrize(
    "terminal",
    [
        {"x": None},
        {"x": {"status": "pendente"}},
        {"x": {"y": {"status": "pendente"}}},
        {"x": [None]},
        [None],
        [{"status": "pendente"}],
        [[{"status": "pendente"}]],
        (None,),
        ({"status": "pendente"},),
    ],
)
def test_conteudo_interno_nao_e_percorrido(terminal: object) -> None:
    """A fronteira examina o terminal recebido, nunca os seus descendentes."""
    assert recusar_nulo_ou_pendente(terminal) is terminal


# ---------------------------------------------------------------------------
# E. Variantes de `status` não são normalizadas


@pytest.mark.parametrize(
    "status",
    [
        "Pendente",
        "PENDENTE",
        "pendentE",
        " pendente",
        "pendente ",
        " pendente ",
        "pendente\n",
        "\tpendente",
        "pen dente",
        "pendentes",
        "",
    ],
)
def test_variante_de_status_nao_e_canonica(status: str) -> None:
    terminal = {"status": status}
    assert recusar_nulo_ou_pendente(terminal) is terminal


# ---------------------------------------------------------------------------
# F. `status` que não é `str` exata


@pytest.mark.parametrize(
    "status",
    [
        None,
        False,
        True,
        0,
        1,
        0.0,
        b"pendente",
        ["pendente"],
        ("pendente",),
        {"pendente"},
        {"x": "pendente"},
        {"status": "pendente"},
    ],
)
def test_status_nao_str_nao_e_canonico(status: object) -> None:
    """Fora da forma canônica, o valor volta — sem ganhar significado algum."""
    terminal = {"status": status}
    assert recusar_nulo_ou_pendente(terminal) is terminal


# ---------------------------------------------------------------------------
# G. Subclasses não satisfazem a forma canônica


class _DictDerivado(dict):
    pass


class _StrDerivada(str):
    pass


def test_subclasse_de_dict_nao_e_forma_canonica() -> None:
    terminal = _DictDerivado({"status": "pendente"})
    assert recusar_nulo_ou_pendente(terminal) is terminal


def test_subclasse_de_str_em_status_nao_e_forma_canonica() -> None:
    terminal = {"status": _StrDerivada("pendente")}
    assert recusar_nulo_ou_pendente(terminal) is terminal


def test_contains_de_subclasse_nao_e_executado() -> None:
    """Tipo exato precede a consulta à chave: nenhum `__contains__` alheio roda."""

    class _DictEspiao(dict):
        def __init__(self) -> None:
            super().__init__()
            self.consultado = False

        def __contains__(self, chave: object) -> bool:
            self.consultado = True
            return True

        def __getitem__(self, chave: object) -> str:
            return "pendente"

    terminal = _DictEspiao()

    assert recusar_nulo_ou_pendente(terminal) is terminal
    assert terminal.consultado is False


# ---------------------------------------------------------------------------
# H. Identidade, não-mutação e determinismo


@pytest.mark.parametrize(
    "valor",
    [
        0,
        0.0,
        False,
        True,
        "",
        "texto_sintetico",
        [],
        {},
        (),
        [1, 2, 3],
        {"a": 1},
        {"status": "aprovado"},
    ],
)
def test_sucesso_devolve_por_identidade(valor: object) -> None:
    assert recusar_nulo_ou_pendente(valor) is valor


@pytest.mark.parametrize(
    "valor",
    [
        {"status": "aprovado", "lista": [1, 2]},
        {"x": {"status": "pendente"}},
        [None, {"status": "pendente"}],
        {"status": None},
    ],
)
def test_entrada_nao_e_mutada(valor: object) -> None:
    antes = copy.deepcopy(valor)
    recusar_nulo_ou_pendente(valor)
    assert valor == antes


def test_entrada_recusada_nao_e_mutada() -> None:
    terminal = {"status": "pendente", "irma": [1, 2]}
    antes = copy.deepcopy(terminal)

    with pytest.raises(ValorNuloOuPendente):
        recusar_nulo_ou_pendente(terminal)

    assert terminal == antes


@pytest.mark.parametrize("valor", [None, {"status": "pendente"}])
def test_recusa_e_deterministica(valor: object) -> None:
    mensagens = set()
    for _ in range(4):
        with pytest.raises(ValorNuloOuPendente) as erro:
            recusar_nulo_ou_pendente(valor)
        mensagens.add(str(erro.value))

    assert len(mensagens) == 1


@pytest.mark.parametrize("valor", [0, "", {"status": "aprovado"}, [None]])
def test_sucesso_e_deterministico(valor: object) -> None:
    assert all(recusar_nulo_ou_pendente(valor) is valor for _ in range(4))


# ---------------------------------------------------------------------------
# I. Vocabulário fechado e ausência de vazamento


def test_vocabulario_tem_exatamente_duas_mensagens() -> None:
    mensagens = set()
    for entrada in (None, {"status": "pendente"}):
        with pytest.raises(ValorNuloOuPendente) as erro:
            recusar_nulo_ou_pendente(entrada)
        mensagens.add(str(erro.value))

    assert mensagens == {"nulo: valor", "pendente: status"}


@pytest.mark.parametrize("entrada", [None, {"status": "pendente", "irma": SENTINELA}])
def test_mensagem_tem_categoria_e_localizador(entrada: object) -> None:
    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(entrada)

    partes = str(erro.value).split(": ")
    assert len(partes) == 2
    assert partes[0] in {"nulo", "pendente"}
    assert partes[1] in {"valor", "status"}


@pytest.mark.parametrize("entrada", [None, {"status": "pendente", "irma": SENTINELA}])
def test_mensagem_nao_tem_repr_nem_indice(entrada: object) -> None:
    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(entrada)

    mensagem = str(erro.value)
    assert not any(caractere.isdigit() for caractere in mensagem)
    assert "[" not in mensagem
    assert "{" not in mensagem
    assert "'" not in mensagem
    assert "<" not in mensagem


@pytest.mark.parametrize("entrada", [None, {"status": "pendente"}])
def test_excecao_sem_cause_nem_contexto(entrada: object) -> None:
    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(entrada)

    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


def test_excecao_deriva_diretamente_de_exception() -> None:
    assert ValorNuloOuPendente.__bases__ == (Exception,)


def test_excecao_nao_se_confunde_com_a_fronteira_do_resolver() -> None:
    assert not issubclass(ValorNuloOuPendente, CaminhoYamlNaoResolvido)
    assert not issubclass(CaminhoYamlNaoResolvido, ValorNuloOuPendente)


# ---------------------------------------------------------------------------
# J. Composição sintética com o resolver factual
#
# A raiz é 100% sintética e existe apenas para demonstrar a fronteira: o
# resolver entrega o terminal, e só então a guarda decide.

RAIZ_SINTETICA = {
    "bloco_exemplo": {
        "campo_nulo": None,
        "campo_pendente": {"status": "pendente"},
        "campo_comum": "valor_sintetico",
    },
    "bloco_nulo": None,
}


def _absoluto(*chaves: str) -> tuple[bool, tuple]:
    return False, tuple((chave, None) for chave in chaves)


def test_composicao_terminal_nulo() -> None:
    terminal = resolver_caminho(RAIZ_SINTETICA, _absoluto("bloco_exemplo", "campo_nulo"))
    assert terminal is None

    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(terminal)

    assert str(erro.value) == "nulo: valor"


def test_composicao_terminal_pendente() -> None:
    terminal = resolver_caminho(
        RAIZ_SINTETICA, _absoluto("bloco_exemplo", "campo_pendente")
    )

    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(terminal)

    assert str(erro.value) == "pendente: status"


def test_composicao_terminal_comum_atravessa_a_guarda() -> None:
    terminal = resolver_caminho(
        RAIZ_SINTETICA, _absoluto("bloco_exemplo", "campo_comum")
    )
    assert recusar_nulo_ou_pendente(terminal) is terminal


def test_composicao_chave_inexistente_falha_antes_da_guarda() -> None:
    """Chave inexistente ≠ `null` (`CY14`): falha no resolver, não em `C-7`."""
    with pytest.raises(CaminhoYamlNaoResolvido) as erro:
        resolver_caminho(RAIZ_SINTETICA, _absoluto("bloco_exemplo", "nao_existe"))

    assert str(erro.value) == "segmento_inexistente: segmento"


def test_composicao_travessia_em_nulo_falha_antes_da_guarda() -> None:
    with pytest.raises(CaminhoYamlNaoResolvido) as erro:
        resolver_caminho(RAIZ_SINTETICA, _absoluto("bloco_nulo", "campo_qualquer"))

    assert str(erro.value) == "travessia_em_nulo: segmento"


def test_composicao_arroba_isolado_sobre_item_nulo() -> None:
    terminal = resolver_caminho(RAIZ_SINTETICA, (True, ()), item_corrente=None)
    assert terminal is None

    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(terminal)

    assert str(erro.value) == "nulo: valor"


def test_composicao_arroba_isolado_sobre_item_pendente() -> None:
    item = {"status": "pendente"}
    terminal = resolver_caminho(RAIZ_SINTETICA, (True, ()), item_corrente=item)
    assert terminal is item

    with pytest.raises(ValorNuloOuPendente) as erro:
        recusar_nulo_ou_pendente(terminal)

    assert str(erro.value) == "pendente: status"


# ---------------------------------------------------------------------------
# K. API pública


def test_all_exato() -> None:
    assert response_null_pending.__all__ == [
        "ValorNuloOuPendente",
        "recusar_nulo_ou_pendente",
    ]


def test_assinatura_tem_um_parametro_obrigatorio() -> None:
    parametros = list(inspect.signature(recusar_nulo_ou_pendente).parameters.values())

    assert [p.name for p in parametros] == ["valor"]
    assert parametros[0].default is inspect.Parameter.empty
    assert parametros[0].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_assinatura_nao_tem_politica_configuravel() -> None:
    parametros = inspect.signature(recusar_nulo_ou_pendente).parameters

    assert len(parametros) == 1
    for parametro in parametros.values():
        assert parametro.kind is not inspect.Parameter.VAR_POSITIONAL
        assert parametro.kind is not inspect.Parameter.VAR_KEYWORD


def test_init_nao_exporta_a_fronteira() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "response_null_pending" not in codigo
    assert "ValorNuloOuPendente" not in codigo
    assert "recusar_nulo_ou_pendente" not in codigo


# ---------------------------------------------------------------------------
# L. Pureza estrutural, por AST


def arvore_do_modulo() -> ast.Module:
    return ast.parse(MODULO.read_text(encoding="utf-8"))


def modulos_importados() -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(arvore_do_modulo()):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)
    return importados


def identificadores_do_codigo() -> set[str]:
    """Nomes e atributos usados — docstring e comentário ficam de fora."""
    usados: set[str] = set()
    for no in ast.walk(arvore_do_modulo()):
        if isinstance(no, ast.Name):
            usados.add(no.id)
        elif isinstance(no, ast.Attribute):
            usados.add(no.attr)
    return usados


def chamadas_do_codigo() -> set[str]:
    return {
        ast.unparse(no.func)
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.Call)
    }


def test_imports_de_producao_sao_fechados() -> None:
    assert modulos_importados() == {"__future__"}


@pytest.mark.parametrize(
    "proibido",
    [
        "yaml",
        "json",
        "collections",
        "collections.abc",
        "typing",
        "re",
        "unicodedata",
        "locale",
        "pathlib",
        "os",
        "sys",
        "io",
        "socket",
        "urllib",
        "datetime",
        "time",
        "calendar",
        "random",
        "logging",
        "sqlite3",
        "functools",
        "enum",
        "dataclasses",
    ],
)
def test_modulo_nao_importa_proibido(proibido: str) -> None:
    assert proibido not in modulos_importados()


def test_modulo_nao_depende_do_pacote() -> None:
    internos = {
        modulo for modulo in modulos_importados() if modulo.startswith("casa77_sdr")
    }
    assert internos == set()


def test_modulo_nao_faz_io_nem_filesystem() -> None:
    proibidos = {
        "open",
        "read",
        "write",
        "read_text",
        "write_text",
        "Path",
        "listdir",
        "walk",
        "input",
        "print",
    }
    assert identificadores_do_codigo() & proibidos == set()


def test_modulo_nao_acessa_rede_relogio_nem_ambiente() -> None:
    proibidos = {
        "urlopen",
        "socket",
        "request",
        "now",
        "today",
        "utcnow",
        "monotonic",
        "environ",
        "getenv",
        "putenv",
    }
    assert identificadores_do_codigo() & proibidos == set()


def test_modulo_nao_normaliza_nem_coage() -> None:
    proibidos = {
        "strip",
        "lstrip",
        "rstrip",
        "upper",
        "lower",
        "casefold",
        "normalize",
        "encode",
        "decode",
        "format",
    }
    assert identificadores_do_codigo() & proibidos == set()


def test_modulo_usa_tipo_exato_e_nao_isinstance() -> None:
    chamadas = chamadas_do_codigo()

    assert "type" in chamadas
    assert "isinstance" not in chamadas


def test_modulo_nao_tem_try_nem_raise_from() -> None:
    arvore = arvore_do_modulo()

    assert not [no for no in ast.walk(arvore) if isinstance(no, ast.Try)]
    assert not [
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.Raise) and no.cause is not None
    ]


def test_modulo_nao_tem_estado_mutavel_global() -> None:
    arvore = arvore_do_modulo()

    assert not [
        no for no in ast.walk(arvore) if isinstance(no, (ast.Global, ast.Nonlocal))
    ]


def test_modulo_nao_usa_enum_nem_dataclass() -> None:
    assert identificadores_do_codigo() & {"Enum", "dataclass", "StrEnum"} == set()


def test_modulo_tem_uma_excecao_e_uma_funcao_publicas() -> None:
    corpo = arvore_do_modulo().body

    classes = [
        no
        for no in corpo
        if isinstance(no, ast.ClassDef) and not no.name.startswith("_")
    ]
    funcoes = [
        no
        for no in corpo
        if isinstance(no, ast.FunctionDef) and not no.name.startswith("_")
    ]

    assert [no.name for no in classes] == ["ValorNuloOuPendente"]
    assert [no.name for no in funcoes] == ["recusar_nulo_ou_pendente"]
