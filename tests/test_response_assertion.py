"""Testes do avaliador determinístico de `ASSERTIVA` sobre valor já resolvido.

Todo o corpus é **sintético**: nenhum preço, capacidade, horário, prazo,
percentual ou quantidade real aparece, nenhuma frase de
`knowledge/respostas-aprovadas.md` é reproduzida e **nada em `knowledge/**` é
lido**. Os valores existem apenas para exercitar o domínio e a fronteira.

As garantias estruturais do módulo de produção — pureza de imports, ausência de
I/O, de *locale*, de coerção e de dependência interna — são provadas sobre a
**AST**, seguindo o precedente de `test_response_index.py`,
`test_response_index_load.py`, `test_response_equivalence.py` e
`test_response_format.py`.

O escopo julgado aqui é **apenas o domínio booleano estrito**. Nenhum outro
domínio de `ASSERTIVA` é exercitado, inferido ou arbitrado por estes testes.
"""

from __future__ import annotations

import ast
import inspect
from decimal import Decimal
from pathlib import Path

import pytest

from casa77_sdr.response_assertion import AssertivaNaoAvaliavel, avaliar_assertiva

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "response_assertion.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

# Sentinela sintética: nunca deve vazar para a mensagem da exceção.
SENTINELA = "SENTINELA_NAO_DEVE_VAZAR"

PREDICADOS_VALIDOS = ["EH_VERDADEIRO", "EH_FALSO"]

# Valores que **não** pertencem ao domínio booleano estrito. `0` e `1`
# encabeçam a lista porque são exatamente os que a igualdade permissiva de
# Python confundiria com `False` e `True`.
NAO_BOOLEANOS = [
    0,
    1,
    -1,
    7,
    0.0,
    1.0,
    -1.5,
    Decimal("0"),
    Decimal("1"),
    "EH_VERDADEIRO",
    "True",
    "true",
    "False",
    "false",
    "",
    None,
    b"\x01",
    b"",
    [],
    [True],
    (),
    (True,),
    {},
    {"valor": True},
    {True},
    object(),
]

PREDICADOS_NAO_STR = [None, 0, 1, True, False, 1.0, Decimal("1"), b"EH_VERDADEIRO", ["EH_VERDADEIRO"], {"EH_VERDADEIRO": True}, object()]

PREDICADOS_DESCONHECIDOS = [
    "eh_verdadeiro",
    "eh_falso",
    "Eh_Verdadeiro",
    "EH_verdadeiro",
    "eh_VERDADEIRO",
    " EH_VERDADEIRO",
    "EH_VERDADEIRO ",
    " EH_VERDADEIRO ",
    "\tEH_VERDADEIRO",
    "EH_VERDADEIRO\n",
    "EH VERDADEIRO",
    "",
    " ",
    "EH_NULO",
    "VERDADEIRO",
    "EH_VERDADEIROO",
    "H_VERDADEIRO",
    "TRUE",
]


def categoria_de(erro: pytest.ExceptionInfo[AssertivaNaoAvaliavel]) -> str:
    return str(erro.value).split(":", 1)[0]


def localizador_de(erro: pytest.ExceptionInfo[AssertivaNaoAvaliavel]) -> str:
    return str(erro.value).split(":", 1)[1].strip()


# A. Matriz válida — os quatro únicos casos avaliáveis


def test_verdadeiro_com_true() -> None:
    assert avaliar_assertiva("EH_VERDADEIRO", True) is True


def test_verdadeiro_com_false() -> None:
    assert avaliar_assertiva("EH_VERDADEIRO", False) is False


def test_falso_com_false() -> None:
    assert avaliar_assertiva("EH_FALSO", False) is True


def test_falso_com_true() -> None:
    assert avaliar_assertiva("EH_FALSO", True) is False


@pytest.mark.parametrize(
    ("predicado", "valor", "esperado"),
    [
        ("EH_VERDADEIRO", True, True),
        ("EH_VERDADEIRO", False, False),
        ("EH_FALSO", True, False),
        ("EH_FALSO", False, True),
    ],
)
def test_matriz_completa(predicado: str, valor: bool, esperado: bool) -> None:
    assert avaliar_assertiva(predicado, valor) is esperado


@pytest.mark.parametrize("valor", [True, False])
def test_os_dois_predicados_sao_opostos_sobre_o_mesmo_valor(valor: bool) -> None:
    """`EH_FALSO` é a negação exata de `EH_VERDADEIRO` — sem terceiro desfecho."""
    assert avaliar_assertiva("EH_VERDADEIRO", valor) is not avaliar_assertiva(
        "EH_FALSO", valor
    )


@pytest.mark.parametrize("predicado", PREDICADOS_VALIDOS)
@pytest.mark.parametrize("valor", [True, False])
def test_retorno_e_bool_estrito(predicado: str, valor: bool) -> None:
    assert type(avaliar_assertiva(predicado, valor)) is bool


@pytest.mark.parametrize("predicado", PREDICADOS_VALIDOS)
@pytest.mark.parametrize("valor", [True, False])
def test_avaliacao_e_deterministica(predicado: str, valor: bool) -> None:
    primeira = avaliar_assertiva(predicado, valor)
    repeticoes = [
        avaliar_assertiva(predicado, valor) for _ in PREDICADOS_VALIDOS * 2
    ]

    assert all(resultado is primeira for resultado in repeticoes)


# B. Domínio booleano estrito — nada mais é avaliável


@pytest.mark.parametrize("valor", NAO_BOOLEANOS)
@pytest.mark.parametrize("predicado", PREDICADOS_VALIDOS)
def test_valor_nao_booleano_e_nao_avaliavel(predicado: str, valor: object) -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(predicado, valor)

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "valor"


def test_zero_nao_e_false() -> None:
    """Em Python `0 == False`; aqui `0` é NÃO AVALIÁVEL."""
    assert 0 == False  # noqa: E712 - a igualdade permissiva é o ponto do teste

    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_FALSO", 0)


def test_um_nao_e_true() -> None:
    """Em Python `1 == True`; aqui `1` é NÃO AVALIÁVEL."""
    assert 1 == True  # noqa: E712 - a igualdade permissiva é o ponto do teste

    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", 1)


def test_menos_um_e_nao_avaliavel() -> None:
    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", -1)


@pytest.mark.parametrize("valor", [0.0, 1.0, -1.5, 3.14])
def test_float_e_nao_avaliavel(valor: float) -> None:
    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", valor)


@pytest.mark.parametrize("valor", [Decimal("0"), Decimal("1"), Decimal("-1")])
def test_decimal_e_nao_avaliavel(valor: Decimal) -> None:
    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", valor)


@pytest.mark.parametrize("valor", ["True", "true", "False", "false", "1", "0", ""])
def test_texto_de_booleano_e_nao_avaliavel(valor: str) -> None:
    """Nenhuma leitura de texto como booleano: sem análise, sem normalização."""
    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", valor)


def test_none_e_nao_avaliavel() -> None:
    """C-7: `null` não ganha significado positivo — é ausência de veredito."""
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_FALSO", None)

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "valor"


@pytest.mark.parametrize("valor", [b"", b"\x00", b"\x01"])
def test_bytes_e_nao_avaliavel(valor: bytes) -> None:
    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", valor)


@pytest.mark.parametrize("valor", [[], [True], (), (True,), {}, {"a": True}, {True}])
def test_conteiner_e_nao_avaliavel(valor: object) -> None:
    """Contêiner vazio ou cheio: nenhum dos dois é lido como booleano."""
    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", valor)


def test_objeto_arbitrario_e_nao_avaliavel() -> None:
    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", object())


def test_objeto_com_bool_customizado_e_nao_avaliavel() -> None:
    """`__bool__` não é consultado: não há *truthiness*."""

    class SempreVerdadeiro:
        def __bool__(self) -> bool:
            return True

    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_VERDADEIRO", SempreVerdadeiro())

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "valor"


def test_objeto_com_eq_permissivo_e_nao_avaliavel() -> None:
    """`__eq__` não é consultado: a decisão é por tipo, não por igualdade."""

    class IgualATudo:
        def __eq__(self, outro: object) -> bool:
            return True

        __hash__ = None  # type: ignore[assignment]

    with pytest.raises(AssertivaNaoAvaliavel):
        avaliar_assertiva("EH_VERDADEIRO", IgualATudo())


def test_valor_nao_booleano_nunca_vira_false() -> None:
    """NÃO AVALIÁVEL não é assertiva falsa: nada é devolvido."""
    for valor in (0, None, "", [], Decimal("0")):
        with pytest.raises(AssertivaNaoAvaliavel):
            avaliar_assertiva("EH_VERDADEIRO", valor)
        with pytest.raises(AssertivaNaoAvaliavel):
            avaliar_assertiva("EH_FALSO", valor)


# C. Predicado


@pytest.mark.parametrize("predicado", PREDICADOS_VALIDOS)
def test_predicado_do_vocabulario_fechado_e_aceito(predicado: str) -> None:
    assert isinstance(avaliar_assertiva(predicado, True), bool)


@pytest.mark.parametrize("predicado", PREDICADOS_NAO_STR)
def test_predicado_nao_str(predicado: object) -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(predicado, True)  # type: ignore[arg-type]

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "predicado"


@pytest.mark.parametrize("predicado", PREDICADOS_DESCONHECIDOS)
def test_predicado_fora_do_vocabulario(predicado: str) -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(predicado, True)

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "predicado"


@pytest.mark.parametrize("predicado", ["eh_verdadeiro", "Eh_Falso", "eh_FALSO"])
def test_variacao_de_caixa_e_recusada(predicado: str) -> None:
    """Sem `upper` e sem `casefold`: o predicado é consultado como chegou."""
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(predicado, True)

    assert categoria_de(erro) == "valor_invalido"


@pytest.mark.parametrize(
    "predicado", [" EH_FALSO", "EH_FALSO ", "\tEH_FALSO", "EH_FALSO\n", " EH_FALSO "]
)
def test_espacos_no_predicado_sao_recusados(predicado: str) -> None:
    """Sem `strip`: espaço em volta faz o predicado deixar de ser suportado."""
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(predicado, True)

    assert categoria_de(erro) == "valor_invalido"


def test_predicado_vazio_e_recusado() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("", True)

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "predicado"


@pytest.mark.parametrize("predicado", ["EH_NULO", "EH_AUSENTE", "EH_PENDENTE", "IGUAL_A"])
def test_nenhum_predicado_novo_e_aceito(predicado: str) -> None:
    """C-A1-R: nenhum predicado além dos dois de C-5g/C-5h."""
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(predicado, True)

    assert categoria_de(erro) == "valor_invalido"


def test_vocabulario_de_predicados_tem_exatamente_dois() -> None:
    aceitos = []
    for candidato in PREDICADOS_VALIDOS + PREDICADOS_DESCONHECIDOS:
        try:
            avaliar_assertiva(candidato, True)
        except AssertivaNaoAvaliavel:
            continue
        aceitos.append(candidato)

    assert aceitos == ["EH_VERDADEIRO", "EH_FALSO"]


# D. Precedência — tipo do predicado, valor do predicado, domínio do valor


def test_tipo_do_predicado_vence_valor_nao_booleano() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(None, 0)  # type: ignore[arg-type]

    assert str(erro.value) == "tipo_invalido: predicado"


def test_tipo_do_predicado_vence_predicado_desconhecido_e_valor_invalido() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(object(), object())  # type: ignore[arg-type]

    assert str(erro.value) == "tipo_invalido: predicado"


def test_valor_do_predicado_vence_dominio_do_valor() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("DESCONHECIDO", 0)

    assert str(erro.value) == "valor_invalido: predicado"


@pytest.mark.parametrize("valor", [0, 1, None, "", [], object()])
def test_predicado_desconhecido_decide_antes_do_valor(valor: object) -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("eh_verdadeiro", valor)

    assert localizador_de(erro) == "predicado"


def test_dominio_do_valor_so_decide_com_predicado_valido() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_VERDADEIRO", 0)

    assert str(erro.value) == "tipo_invalido: valor"


def test_ordem_completa_das_tres_violacoes() -> None:
    """As três violações, isoladas e combinadas, respeitam a mesma ordem."""
    casos = [
        ((None, 0), "tipo_invalido: predicado"),
        (("DESCONHECIDO", 0), "valor_invalido: predicado"),
        (("EH_VERDADEIRO", 0), "tipo_invalido: valor"),
    ]
    for argumentos, esperado in casos:
        with pytest.raises(AssertivaNaoAvaliavel) as erro:
            avaliar_assertiva(*argumentos)  # type: ignore[arg-type]
        assert str(erro.value) == esperado


def test_primeira_violacao_encerra_sem_acumular() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(b"EH_VERDADEIRO", Decimal("1"))  # type: ignore[arg-type]

    assert str(erro.value) == "tipo_invalido: predicado"
    assert str(erro.value).count(":") == 1


# E. Contrato de erro


def test_excecao_deriva_diretamente_de_exception() -> None:
    assert AssertivaNaoAvaliavel.__bases__ == (Exception,)


def test_excecao_nao_deriva_de_valueerror_nem_typeerror() -> None:
    assert not issubclass(AssertivaNaoAvaliavel, ValueError)
    assert not issubclass(AssertivaNaoAvaliavel, TypeError)


def test_excecao_nao_se_confunde_com_as_outras_fronteiras() -> None:
    from casa77_sdr.response_equivalence import EquivalenciaNaoDeterminavel
    from casa77_sdr.response_format import FormatoInaplicavel
    from casa77_sdr.response_index import IndiceInvalido
    from casa77_sdr.response_index_load import IndiceIlegivel

    for outra in (
        EquivalenciaNaoDeterminavel,
        FormatoInaplicavel,
        IndiceInvalido,
        IndiceIlegivel,
    ):
        assert not issubclass(AssertivaNaoAvaliavel, outra)
        assert not issubclass(outra, AssertivaNaoAvaliavel)


def test_vocabulario_de_categorias_e_fechado() -> None:
    observadas = set()

    for argumentos in ((None, True), ("DESCONHECIDO", True), ("EH_FALSO", 0)):
        with pytest.raises(AssertivaNaoAvaliavel) as erro:
            avaliar_assertiva(*argumentos)  # type: ignore[arg-type]
        observadas.add(categoria_de(erro))

    assert observadas == {"tipo_invalido", "valor_invalido"}


def test_vocabulario_de_localizadores_e_fechado() -> None:
    observados = set()

    for argumentos in ((None, True), ("DESCONHECIDO", True), ("EH_FALSO", 0)):
        with pytest.raises(AssertivaNaoAvaliavel) as erro:
            avaliar_assertiva(*argumentos)  # type: ignore[arg-type]
        observados.add(localizador_de(erro))

    assert observados == {"predicado", "valor"}


def test_mensagem_tem_categoria_e_localizador() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_NULO", True)

    assert str(erro.value) == "valor_invalido: predicado"


def test_mensagem_nao_ecoa_predicado_recebido() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(SENTINELA, True)

    assert SENTINELA not in str(erro.value)


def test_mensagem_nao_ecoa_valor_recebido() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_VERDADEIRO", SENTINELA)

    assert SENTINELA not in str(erro.value)


def test_mensagem_nao_ecoa_predicado_nem_valor_juntos() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva([SENTINELA], {SENTINELA: SENTINELA})  # type: ignore[arg-type]

    assert SENTINELA not in str(erro.value)


@pytest.mark.parametrize(
    ("argumentos", "tipo_concreto"),
    [
        (("EH_VERDADEIRO", None), "NoneType"),
        (("EH_VERDADEIRO", 0), "int"),
        (("EH_VERDADEIRO", 0.0), "float"),
        (("EH_VERDADEIRO", "x"), "str"),
        (("EH_VERDADEIRO", b"x"), "bytes"),
        (("EH_VERDADEIRO", []), "list"),
        (("EH_VERDADEIRO", {}), "dict"),
        (("EH_VERDADEIRO", Decimal("1")), "Decimal"),
        ((None, True), "NoneType"),
        ((0, True), "int"),
    ],
)
def test_mensagem_nao_ecoa_tipo_concreto(
    argumentos: tuple[object, object], tipo_concreto: str
) -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(*argumentos)  # type: ignore[arg-type]

    assert tipo_concreto not in str(erro.value)


def test_mensagem_nao_tem_digito_indice_nem_repr() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_VERDADEIRO", [SENTINELA, SENTINELA, SENTINELA])

    mensagem = str(erro.value)

    assert not any(caractere.isdigit() for caractere in mensagem)
    assert "[" not in mensagem
    assert "'" not in mensagem
    assert "<" not in mensagem


def test_excecao_sem_cause() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_VERDADEIRO", 0)

    assert erro.value.__cause__ is None


def test_excecao_sem_contexto_encadeado() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva("EH_VERDADEIRO", 0)

    assert erro.value.__context__ is None


@pytest.mark.parametrize(
    "argumentos", [(None, True), ("DESCONHECIDO", True), ("EH_FALSO", 0)]
)
def test_mensagem_tem_exatamente_duas_partes(argumentos: tuple[object, object]) -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_assertiva(*argumentos)  # type: ignore[arg-type]

    partes = str(erro.value).split(": ")

    assert len(partes) == 2
    assert partes[0] in {"tipo_invalido", "valor_invalido"}
    assert partes[1] in {"predicado", "valor"}


# F. Contrato de API


def test_all_exato() -> None:
    from casa77_sdr import response_assertion

    assert response_assertion.__all__ == [
        "AssertivaNaoAvaliavel",
        "avaliar_assertiva",
    ]


def test_all_tem_dois_nomes() -> None:
    from casa77_sdr import response_assertion

    assert len(response_assertion.__all__) == 2


def test_assinatura_tem_dois_parametros_sem_default() -> None:
    parametros = list(inspect.signature(avaliar_assertiva).parameters.values())

    assert [p.name for p in parametros] == ["predicado", "valor"]
    for parametro in parametros:
        assert parametro.default is inspect.Parameter.empty
        assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_assinatura_nao_tem_parametro_de_configuracao() -> None:
    """Sem modo, estilo, origem, caminho ou configuração: a decisão é única."""
    parametros = inspect.signature(avaliar_assertiva).parameters

    assert len(parametros) == 2
    for proibido in ("modo", "estilo", "origem", "caminho", "config", "contexto"):
        assert proibido not in parametros


def test_assinatura_nao_tem_vararg_nem_kwarg() -> None:
    parametros = inspect.signature(avaliar_assertiva).parameters.values()

    for parametro in parametros:
        assert parametro.kind is not inspect.Parameter.VAR_POSITIONAL
        assert parametro.kind is not inspect.Parameter.VAR_KEYWORD


def test_init_nao_exporta_o_avaliador() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "response_assertion" not in codigo
    assert "AssertivaNaoAvaliavel" not in codigo
    assert "avaliar_assertiva" not in codigo


# G. Pureza estrutural, por AST


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
        "locale",
        "pathlib",
        "os",
        "io",
        "sys",
        "re",
        "json",
        "socket",
        "urllib",
        "http",
        "decimal",
        "datetime",
        "calendar",
        "time",
        "subprocess",
        "importlib",
        "casa77_sdr",
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_equivalence",
        "casa77_sdr.response_format",
        "casa77_sdr.knowledge",
    ],
)
def test_modulo_nao_importa_proibido(proibido: str) -> None:
    assert proibido not in modulos_importados()


def test_modulo_nao_depende_do_pacote() -> None:
    """Pureza: o avaliador não conhece índice, carregador, comparador ou formatador."""
    internos = {n for n in modulos_importados() if n.startswith("casa77_sdr")}

    assert internos == set()


def test_modulo_nao_faz_io_nem_filesystem() -> None:
    usados = identificadores_do_codigo()
    proibidos = {
        "open",
        "read_text",
        "read_bytes",
        "write_text",
        "write_bytes",
        "Path",
        "glob",
        "rglob",
        "iterdir",
        "walk",
        "load",
        "safe_load",
        "dump",
        "safe_dump",
    }

    assert usados & proibidos == set()


def test_modulo_nao_acessa_rede() -> None:
    usados = identificadores_do_codigo()
    proibidos = {"socket", "connect", "urlopen", "request", "get", "post", "session"}

    assert usados & proibidos == set()


def test_modulo_nao_consulta_locale() -> None:
    usados = identificadores_do_codigo()

    assert usados & {"setlocale", "localeconv", "getlocale", "nl_langinfo"} == set()
    assert "locale" not in modulos_importados()


def test_modulo_nao_consulta_relogio_nem_calendario() -> None:
    usados = identificadores_do_codigo()
    proibidos = {"now", "today", "utcnow", "date", "datetime", "time", "monotonic"}

    assert usados & proibidos == set()


def test_modulo_nao_le_variavel_de_ambiente() -> None:
    usados = identificadores_do_codigo()

    assert usados & {"environ", "getenv", "putenv", "expandvars"} == set()


def test_modulo_nao_chama_bool() -> None:
    """Sem coerção: `bool` aparece só como tipo em `isinstance`, nunca chamado."""
    assert "bool" not in chamadas_do_codigo()


def test_modulo_nao_normaliza_o_predicado() -> None:
    usados = identificadores_do_codigo()

    assert usados & {"strip", "lstrip", "rstrip", "upper", "lower", "casefold"} == set()


def test_modulo_usa_isinstance_e_nao_igualdade_de_tipo() -> None:
    """A decisão de domínio é por `isinstance`, não por `type(...) ==`."""
    chamadas = chamadas_do_codigo()

    assert "isinstance" in chamadas
    assert "type" not in chamadas


@pytest.mark.parametrize(
    "termo",
    [
        "knowledge",
        "casa77.yaml",
        "indice-respostas-aprovadas.yaml",
        "respostas-aprovadas",
        "caminho_yaml",
        "fato_runtime",
        "RUNTIME_AUTORITATIVO",
        "response_index",
        "response_index_load",
        "response_equivalence",
        "response_format",
    ],
)
def test_modulo_nao_menciona_fronteira_alheia(termo: str) -> None:
    assert termo not in MODULO.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "termo",
    [
        "placeholder",
        "template",
        "renderer",
        "renderizar",
        "markdown",
        "binding",
        "indice",
        "handoff",
        "E09",
        "E18",
        "lead",
        "orquestrador",
        "calendario",
        "disponibilidade",
        "candidatura",
    ],
)
def test_modulo_nao_conhece_consumidor_nem_vizinhanca(termo: str) -> None:
    """A fronteira julga um valor recebido, e não sabe quem a chama."""
    identificadores = {nome.lower() for nome in identificadores_do_codigo()}

    assert termo.lower() not in identificadores


def test_modulo_nao_declara_despachante() -> None:
    """Nenhuma tabela `predicado → função`: a decisão é direta."""
    identificadores = identificadores_do_codigo()

    for proibido in ("despachar", "aplicar", "resolver", "carregar", "avaliar_todos"):
        assert proibido not in identificadores


def test_modulo_tem_uma_unica_classe_publica() -> None:
    classes = [
        no.name
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.ClassDef)
    ]

    assert classes == ["AssertivaNaoAvaliavel"]


def test_modulo_expoe_exatamente_uma_funcao_publica() -> None:
    publicas = [
        no.name
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.FunctionDef) and not no.name.startswith("_")
    ]

    assert publicas == ["avaliar_assertiva"]


def test_modulo_nao_declara_enum_nem_dataclass() -> None:
    usados = identificadores_do_codigo()

    assert not {"Enum", "StrEnum", "IntEnum", "dataclass"} & usados
    for no in ast.walk(arvore_do_modulo()):
        if isinstance(no, ast.ClassDef):
            assert not no.bases or [
                base.id for base in no.bases if isinstance(base, ast.Name)
            ] == ["Exception"]
            assert not no.decorator_list


def test_vocabulario_de_predicados_do_modulo_tem_dois_membros() -> None:
    from casa77_sdr import response_assertion

    assert response_assertion._PREDICADOS == frozenset(
        {"EH_VERDADEIRO", "EH_FALSO"}
    )
