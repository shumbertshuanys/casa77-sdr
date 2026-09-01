"""Testes dos formatadores determinísticos de apresentação pura de `C-6`.

Todo o corpus é **sintético**: nenhum preço, capacidade, horário, prazo,
percentual ou quantidade real aparece, nenhuma frase de
`knowledge/respostas-aprovadas.md` é reproduzida e **nada em `knowledge/**` é
lido**. Os números foram escolhidos para exercitar a forma do agrupamento, e
**não** para representar fato comercial algum.

As garantias estruturais do módulo de produção — pureza de imports, ausência de
I/O, de *locale* e de dependência interna — são provadas sobre a **AST**,
seguindo o precedente de `test_response_index.py`, `test_response_index_load.py`
e `test_response_equivalence.py`.

O formato `hora` **não é exercitado**: ele não existe nesta fronteira, e há
teste explícito de que continua inexistente.
"""

from __future__ import annotations

import ast
import inspect
from decimal import Decimal
from pathlib import Path

import pytest

from casa77_sdr.response_format import (
    FormatoInaplicavel,
    formatar_inteiro,
    formatar_inteiro_agrupado,
    formatar_lista,
    formatar_simbolo_moeda,
    formatar_texto,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "response_format.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

# Sentinela sintética: nunca deve vazar para a mensagem da exceção.
SENTINELA = "SENTINELA_NAO_DEVE_VAZAR"

# Valores que **não** são `int` estrito. `bool` encabeça a lista porque é o
# único que passaria por `isinstance(..., int)`.
NAO_INTEIROS = [
    True,
    False,
    1.0,
    -1.0,
    0.0,
    Decimal("7"),
    Decimal("0"),
    "7",
    "-7",
    "",
    None,
    b"7",
    ["7"],
    ("7",),
    {"valor": 7},
    object(),
]

NAO_TEXTOS = [None, 7, -7, True, False, 1.0, Decimal("7"), b"x", ["x"], {"x": 1}, object()]


def categoria_de(erro: pytest.ExceptionInfo[FormatoInaplicavel]) -> str:
    return str(erro.value).split(":", 1)[0]


def localizador_de(erro: pytest.ExceptionInfo[FormatoInaplicavel]) -> str:
    return str(erro.value).split(":", 1)[1].strip()


# 1. Tipos — `inteiro` e `inteiro_agrupado` aceitam somente `int` estrito


@pytest.mark.parametrize("valor", NAO_INTEIROS)
def test_inteiro_recusa_nao_inteiro(valor: object) -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_inteiro(valor)  # type: ignore[arg-type]

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "valor"


@pytest.mark.parametrize("valor", NAO_INTEIROS)
def test_inteiro_agrupado_recusa_nao_inteiro(valor: object) -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_inteiro_agrupado(valor)  # type: ignore[arg-type]

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "valor"


@pytest.mark.parametrize("valor", [True, False])
def test_bool_nao_e_inteiro_de_apresentacao(valor: bool) -> None:
    """`bool` é subclasse de `int` e ainda assim é recusado pelos dois."""
    with pytest.raises(FormatoInaplicavel):
        formatar_inteiro(valor)
    with pytest.raises(FormatoInaplicavel):
        formatar_inteiro_agrupado(valor)


def test_float_inteiro_nao_e_coagido() -> None:
    """`7.0` não vira `7`: não há coerção."""
    with pytest.raises(FormatoInaplicavel):
        formatar_inteiro(7.0)  # type: ignore[arg-type]


def test_decimal_nao_e_coagido() -> None:
    with pytest.raises(FormatoInaplicavel):
        formatar_inteiro(Decimal("7"))  # type: ignore[arg-type]


def test_string_numerica_nao_e_coagida() -> None:
    with pytest.raises(FormatoInaplicavel):
        formatar_inteiro("428")  # type: ignore[arg-type]


def test_none_nao_e_inteiro() -> None:
    with pytest.raises(FormatoInaplicavel):
        formatar_inteiro(None)  # type: ignore[arg-type]


# 2. `inteiro`


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (0, "0"),
        (7, "7"),
        (-7, "-7"),
        (9, "9"),
        (67, "67"),
        (428, "428"),
        (-428, "-428"),
        (4567, "4567"),
        (-4567, "-4567"),
        (987654, "987654"),
        (7654321, "7654321"),
        (98765432109876, "98765432109876"),
    ],
)
def test_inteiro_e_decimal_do_mesmo_valor(valor: int, esperado: str) -> None:
    assert formatar_inteiro(valor) == esperado


def test_inteiro_nao_agrupa() -> None:
    assert "." not in formatar_inteiro(7654321)
    assert "," not in formatar_inteiro(7654321)
    assert " " not in formatar_inteiro(7654321)


def test_inteiro_nao_acrescenta_zero() -> None:
    assert formatar_inteiro(7) == "7"
    assert formatar_inteiro(67) == "67"


def test_inteiro_zero_nao_tem_sinal() -> None:
    assert formatar_inteiro(0) == "0"


def test_inteiro_preserva_o_sinal_negativo() -> None:
    assert formatar_inteiro(-4567).startswith("-")


def test_inteiro_nao_acrescenta_sinal_positivo() -> None:
    assert not formatar_inteiro(4567).startswith("+")


def test_inteiro_devolve_str() -> None:
    assert type(formatar_inteiro(7)) is str


@pytest.mark.parametrize("valor", [0, 7, -7, 4567, -987654, 98765432109876])
def test_inteiro_faz_round_trip(valor: int) -> None:
    """A apresentação não altera o valor: ela volta a ser o mesmo inteiro."""
    assert int(formatar_inteiro(valor)) == valor


# 3. `inteiro_agrupado`


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (0, "0"),
        (7, "7"),
        (67, "67"),
        (428, "428"),
        (4567, "4.567"),
        (98765, "98.765"),
        (987654, "987.654"),
        (7654321, "7.654.321"),
        (98765432, "98.765.432"),
        (987654321, "987.654.321"),
        (7654321987, "7.654.321.987"),
        (98765432109876, "98.765.432.109.876"),
    ],
)
def test_inteiro_agrupado_positivo(valor: int, esperado: str) -> None:
    assert formatar_inteiro_agrupado(valor) == esperado


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (-7, "-7"),
        (-428, "-428"),
        (-4567, "-4.567"),
        (-987654, "-987.654"),
        (-7654321, "-7.654.321"),
    ],
)
def test_inteiro_agrupado_negativo(valor: int, esperado: str) -> None:
    assert formatar_inteiro_agrupado(valor) == esperado


def test_inteiro_agrupado_de_tres_digitos_nao_recebe_separador() -> None:
    assert formatar_inteiro_agrupado(428) == "428"


def test_inteiro_agrupado_de_quatro_digitos_tem_um_separador() -> None:
    assert formatar_inteiro_agrupado(4567).count(".") == 1


def test_inteiro_agrupado_de_seis_digitos_tem_um_separador() -> None:
    assert formatar_inteiro_agrupado(987654).count(".") == 1


def test_inteiro_agrupado_de_sete_digitos_tem_dois_separadores() -> None:
    assert formatar_inteiro_agrupado(7654321).count(".") == 2


def test_inteiro_agrupado_zero() -> None:
    assert formatar_inteiro_agrupado(0) == "0"


def test_inteiro_agrupado_nao_completa_grupo_com_zero() -> None:
    """O grupo mais à esquerda fica com o que sobrar, e não é preenchido."""
    assert formatar_inteiro_agrupado(4567) == "4.567"
    assert formatar_inteiro_agrupado(98765) == "98.765"


def test_inteiro_agrupado_agrupa_da_direita_para_a_esquerda() -> None:
    assert formatar_inteiro_agrupado(7654321).split(".") == ["7", "654", "321"]


def test_inteiro_agrupado_usa_ponto_e_nao_virgula() -> None:
    formatado = formatar_inteiro_agrupado(7654321)

    assert "," not in formatado
    assert " " not in formatado
    assert "\u00a0" not in formatado
    assert "_" not in formatado


def test_inteiro_agrupado_nao_tem_casa_decimal() -> None:
    formatado = formatar_inteiro_agrupado(98765432)
    ultimo_grupo = formatado.split(".")[-1]

    assert len(ultimo_grupo) == 3


def test_inteiro_agrupado_preserva_o_sinal() -> None:
    assert formatar_inteiro_agrupado(-7654321) == "-" + formatar_inteiro_agrupado(
        7654321
    )


def test_inteiro_agrupado_nao_agrupa_o_sinal() -> None:
    """O `-` fica colado ao primeiro dígito, e não vira grupo próprio."""
    assert formatar_inteiro_agrupado(-4567).startswith("-4")


def test_inteiro_agrupado_nao_acrescenta_sinal_positivo() -> None:
    assert not formatar_inteiro_agrupado(4567).startswith("+")


def test_inteiro_agrupado_preserva_zero_interno() -> None:
    assert formatar_inteiro_agrupado(1007) == "1.007"
    assert formatar_inteiro_agrupado(90007654) == "90.007.654"


def test_inteiro_agrupado_devolve_str() -> None:
    assert type(formatar_inteiro_agrupado(7654321)) is str


@pytest.mark.parametrize(
    "valor",
    [0, 7, 428, 4567, 98765, 987654, 7654321, -4567, -987654, 98765432109876],
)
def test_inteiro_agrupado_faz_round_trip(valor: int) -> None:
    """Round-trip estrutural: removidos os separadores, é o mesmo inteiro."""
    assert int(formatar_inteiro_agrupado(valor).replace(".", "")) == valor


@pytest.mark.parametrize("valor", [0, 7, 4567, 987654, 7654321, -4567, -7654321])
def test_inteiro_agrupado_tem_os_mesmos_digitos_do_inteiro(valor: int) -> None:
    """Nenhum dígito é criado, removido ou reordenado pelo agrupamento."""
    assert formatar_inteiro_agrupado(valor).replace(".", "") == formatar_inteiro(
        valor
    )


def test_inteiro_agrupado_nao_arredonda_nem_calcula() -> None:
    """Vizinhos próximos continuam distintos: nada é aproximado."""
    assert formatar_inteiro_agrupado(4567) != formatar_inteiro_agrupado(4568)
    assert formatar_inteiro_agrupado(98765) != formatar_inteiro_agrupado(98764)


def test_inteiro_agrupado_nao_depende_de_locale(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ambiente de *locale* alterado não muda a saída (C-A4-F1m, C-A4-F1n)."""
    esperado = formatar_inteiro_agrupado(7654321)
    for variavel in ("LC_ALL", "LC_NUMERIC", "LANG"):
        monkeypatch.setenv(variavel, "de_DE.UTF-8")

    assert formatar_inteiro_agrupado(7654321) == esperado


# 4. `simbolo_moeda`


def test_codigo_suportado_devolve_o_simbolo() -> None:
    assert formatar_simbolo_moeda("BRL") == "R$"


def test_simbolo_nao_tem_espaco_antes_nem_depois() -> None:
    """C-A4-F2c: o espaço pertence ao fragmento estático, não ao formatador."""
    simbolo = formatar_simbolo_moeda("BRL")

    assert simbolo == simbolo.strip()
    assert not simbolo.startswith(" ")
    assert not simbolo.endswith(" ")


def test_simbolo_nao_tem_whitespace_algum() -> None:
    simbolo = formatar_simbolo_moeda("BRL")

    assert not any(caractere.isspace() for caractere in simbolo)


def test_simbolo_nao_traz_valor_junto() -> None:
    """Sem dependência oculta: o formatador não conhece valor algum."""
    simbolo = formatar_simbolo_moeda("BRL")

    assert not any(caractere.isdigit() for caractere in simbolo)


@pytest.mark.parametrize(
    "codigo",
    ["brl", "Brl", "bRL", "BrL", "BRl"],
)
def test_variacao_de_caixa_e_recusada(codigo: str) -> None:
    """Sem `upper`: o código é consultado exatamente como chegou."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda(codigo)

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "codigo"


@pytest.mark.parametrize(
    "codigo",
    [" BRL", "BRL ", " BRL ", "\tBRL", "BRL\n", "B RL"],
)
def test_codigo_com_espaco_e_recusado(codigo: str) -> None:
    """Sem `strip`: espaço em volta faz o código deixar de ser suportado."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda(codigo)

    assert categoria_de(erro) == "valor_invalido"


def test_codigo_vazio_e_recusado() -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda("")

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "codigo"


@pytest.mark.parametrize(
    "codigo",
    ["USD", "EUR", "GBP", "JPY", "ARS", "BR", "BRLL", "R$", "REAL"],
)
def test_codigo_nao_suportado_falha(codigo: str) -> None:
    """C-A4-F2d / C-A4-F2e: a tabela não é ampliada, e o resto falha."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda(codigo)

    assert categoria_de(erro) == "valor_invalido"


@pytest.mark.parametrize("codigo", [None, 7, True, 1.0, b"BRL", ["BRL"], {"BRL": 1}])
def test_codigo_nao_texto_e_recusado(codigo: object) -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda(codigo)  # type: ignore[arg-type]

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "codigo"


def test_moeda_nunca_e_inferida() -> None:
    """Sem código explícito não há símbolo: a assinatura o exige."""
    with pytest.raises(TypeError):
        formatar_simbolo_moeda()  # type: ignore[call-arg]


def test_simbolo_devolve_str() -> None:
    assert type(formatar_simbolo_moeda("BRL")) is str


# 5. `texto`


@pytest.mark.parametrize(
    "valor",
    [
        "",
        "alfa",
        "Alfa Beta",
        "alfa beta gama",
        "  alfa  ",
        "\talfa\t",
        "alfa\nbeta",
        "alfa\n\nbeta",
        "alfa\r\nbeta",
        "alfa, beta; gama.",
        "ALFA",
        "caf\u00e9",
        "cafe\u0301",
        "\u00e1\u00e9\u00ed",
        "a\u0301e\u0301i\u0301",
        "\ufb01m",
        "alfa\u00a0beta",
        "  ",
    ],
)
def test_texto_e_identidade_exata(valor: str) -> None:
    assert formatar_texto(valor) == valor


@pytest.mark.parametrize("valor", ["", "alfa", "  alfa  ", "cafe\u0301"])
def test_texto_devolve_a_mesma_str(valor: str) -> None:
    assert formatar_texto(valor) is valor


def test_texto_nao_aplica_nfc() -> None:
    """Decomposto continua decomposto: o formatador não normaliza."""
    decomposto = "cafe\u0301"

    assert formatar_texto(decomposto) == decomposto
    assert formatar_texto(decomposto) != "caf\u00e9"


def test_texto_nao_faz_strip() -> None:
    assert formatar_texto("  alfa  ") == "  alfa  "


def test_texto_preserva_tab() -> None:
    assert formatar_texto("alfa\tbeta") == "alfa\tbeta"


def test_texto_preserva_quebra() -> None:
    assert formatar_texto("alfa\nbeta") == "alfa\nbeta"


def test_texto_preserva_paragrafo() -> None:
    assert formatar_texto("alfa\n\nbeta") == "alfa\n\nbeta"


def test_texto_nao_normaliza_espacos() -> None:
    assert formatar_texto("alfa    beta") == "alfa    beta"


def test_texto_nao_faz_casefold() -> None:
    assert formatar_texto("ALFA Beta") == "ALFA Beta"


def test_texto_nao_altera_pontuacao() -> None:
    assert formatar_texto("alfa, beta; gama.") == "alfa, beta; gama."


def test_texto_vazio_continua_vazio() -> None:
    assert formatar_texto("") == ""


@pytest.mark.parametrize("valor", NAO_TEXTOS)
def test_texto_recusa_nao_str(valor: object) -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_texto(valor)  # type: ignore[arg-type]

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "valor"


def test_texto_devolve_str() -> None:
    assert type(formatar_texto("alfa")) is str


# 6. `lista`


def test_lista_de_zero_itens_falha() -> None:
    """C-A1-L1: cardinalidade zero é fail-closed."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista([])

    assert categoria_de(erro) == "valor_invalido"
    assert localizador_de(erro) == "itens"


def test_tupla_de_zero_itens_falha() -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista(())

    assert categoria_de(erro) == "valor_invalido"


def test_lista_de_um_item() -> None:
    assert formatar_lista(["alfa"]) == "alfa"


def test_lista_de_um_item_nao_ganha_conjuncao() -> None:
    formatado = formatar_lista(["alfa"])

    assert " e " not in formatado
    assert "," not in formatado


def test_lista_de_dois_itens() -> None:
    assert formatar_lista(["alfa", "beta"]) == "alfa e beta"


def test_lista_de_dois_itens_nao_tem_virgula() -> None:
    assert "," not in formatar_lista(["alfa", "beta"])


def test_lista_de_tres_itens() -> None:
    assert formatar_lista(["alfa", "beta", "gama"]) == "alfa, beta e gama"


def test_lista_de_quatro_itens() -> None:
    assert (
        formatar_lista(["alfa", "beta", "gama", "delta"])
        == "alfa, beta, gama e delta"
    )


def test_lista_de_cinco_itens() -> None:
    assert (
        formatar_lista(["alfa", "beta", "gama", "delta", "epsilon"])
        == "alfa, beta, gama, delta e epsilon"
    )


def test_lista_tem_uma_unica_conjuncao() -> None:
    formatado = formatar_lista(["alfa", "beta", "gama", "delta"])

    assert formatado.count(" e ") == 1


def test_lista_separa_os_anteriores_por_virgula() -> None:
    formatado = formatar_lista(["alfa", "beta", "gama", "delta"])

    assert formatado.count(", ") == 2


def test_lista_nao_termina_com_pontuacao_propria() -> None:
    formatado = formatar_lista(["alfa", "beta", "gama"])

    assert not formatado.endswith(".")
    assert not formatado.endswith(",")


def test_lista_aceita_tuple() -> None:
    assert formatar_lista(("alfa", "beta", "gama")) == "alfa, beta e gama"


def test_lista_e_tuple_produzem_o_mesmo() -> None:
    itens = ["alfa", "beta", "gama"]

    assert formatar_lista(itens) == formatar_lista(tuple(itens))


def test_lista_preserva_a_ordem() -> None:
    assert formatar_lista(["gama", "alfa", "beta"]) == "gama, alfa e beta"


def test_lista_nao_ordena() -> None:
    direta = formatar_lista(["gama", "beta", "alfa"])
    inversa = formatar_lista(["alfa", "beta", "gama"])

    assert direta != inversa


def test_lista_nao_filtra_repetidos() -> None:
    assert formatar_lista(["alfa", "alfa", "alfa"]) == "alfa, alfa e alfa"


def test_lista_preserva_o_conteudo_literal_de_cada_item() -> None:
    itens = ["  alfa  ", "beta\tbeta", "GAMA"]

    assert formatar_lista(itens) == "  alfa  , beta\tbeta e GAMA"


def test_lista_preserva_pontuacao_interna_do_item() -> None:
    itens = ["alfa, alfa", "beta; beta", "gama."]

    assert formatar_lista(itens) == "alfa, alfa, beta; beta e gama."


def test_lista_preserva_unicode_do_item() -> None:
    itens = ["cafe\u0301", "caf\u00e9"]

    assert formatar_lista(itens) == "cafe\u0301 e caf\u00e9"


def test_lista_nao_flexiona_nem_parafraseia_item() -> None:
    itens = ["alfa", "beta"]

    for item in itens:
        assert item in formatar_lista(itens)


def test_lista_nao_acrescenta_prefixo_por_item() -> None:
    formatado = formatar_lista(["alfa", "beta", "gama"])

    assert not formatado.startswith("-")
    assert "- " not in formatado
    assert "* " not in formatado


def test_lista_de_um_item_preserva_o_item_intacto() -> None:
    item = "  alfa, beta  "

    assert formatar_lista([item]) == item


def test_item_vazio_e_preservado_em_lista_de_um() -> None:
    """O contrato não proíbe item vazio, e manda preservar literalmente."""
    assert formatar_lista([""]) == ""


def test_item_vazio_e_preservado_em_lista_de_dois() -> None:
    assert formatar_lista(["", "beta"]) == " e beta"
    assert formatar_lista(["alfa", ""]) == "alfa e "


def test_item_vazio_e_preservado_em_lista_de_tres() -> None:
    assert formatar_lista(["alfa", "", "gama"]) == "alfa,  e gama"


def test_item_vazio_nao_e_filtrado() -> None:
    """Lista só de vazios continua com a cardinalidade que recebeu."""
    assert formatar_lista(["", "", ""]) == ",  e "


def test_lista_de_itens_vazios_nao_vira_cardinalidade_zero() -> None:
    formatar_lista(["", ""])  # não levanta: são dois itens, não zero


@pytest.mark.parametrize(
    "itens",
    [["alfa", 7], [7, "alfa"], ["alfa", None], ["alfa", True], ["alfa", ["beta"]]],
)
def test_item_nao_str_e_recusado(itens: list[object]) -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista(itens)  # type: ignore[arg-type]

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "itens.item"


@pytest.mark.parametrize("texto", ["alfa", "", "a", "alfa beta"])
def test_str_nao_e_conteiner_de_lista(texto: str) -> None:
    """Os caracteres de uma `str` não são itens."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista(texto)

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "itens"


@pytest.mark.parametrize(
    "itens",
    [None, 7, True, 1.0, {"alfa": "beta"}, {"alfa"}, iter(["alfa"])],
)
def test_conteiner_invalido_e_recusado(itens: object) -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista(itens)  # type: ignore[arg-type]

    assert categoria_de(erro) == "tipo_invalido"
    assert localizador_de(erro) == "itens"


def test_lista_nao_muta_a_entrada() -> None:
    itens = ["alfa", "beta", "gama"]
    copia = list(itens)

    formatar_lista(itens)

    assert itens == copia


def test_lista_nao_muta_a_entrada_quando_falha() -> None:
    itens: list[object] = ["alfa", 7]
    copia = list(itens)

    with pytest.raises(FormatoInaplicavel):
        formatar_lista(itens)  # type: ignore[arg-type]

    assert itens == copia


def test_lista_devolve_str() -> None:
    assert type(formatar_lista(["alfa", "beta"])) is str


# 7. Fail-closed e segurança da exceção


def test_excecao_deriva_diretamente_de_exception() -> None:
    assert FormatoInaplicavel.__bases__ == (Exception,)


def test_excecao_nao_deriva_de_valueerror() -> None:
    assert not issubclass(FormatoInaplicavel, ValueError)


def test_excecao_nao_se_confunde_com_as_outras_fronteiras() -> None:
    from casa77_sdr.response_equivalence import EquivalenciaNaoDeterminavel
    from casa77_sdr.response_index import IndiceInvalido
    from casa77_sdr.response_index_load import IndiceIlegivel

    for outra in (EquivalenciaNaoDeterminavel, IndiceInvalido, IndiceIlegivel):
        assert not issubclass(FormatoInaplicavel, outra)
        assert not issubclass(outra, FormatoInaplicavel)


def test_mensagem_tem_categoria_e_localizador() -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda("USD")

    assert str(erro.value) == "valor_invalido: codigo"


def test_vocabulario_de_categorias_e_fechado() -> None:
    observadas = set()

    for chamada in (
        lambda: formatar_inteiro("7"),  # type: ignore[arg-type]
        lambda: formatar_simbolo_moeda("USD"),
        lambda: formatar_lista([]),
        lambda: formatar_lista(["alfa", 7]),  # type: ignore[list-item]
    ):
        with pytest.raises(FormatoInaplicavel) as erro:
            chamada()
        observadas.add(categoria_de(erro))

    assert observadas == {"tipo_invalido", "valor_invalido"}


def test_vocabulario_de_localizadores_e_fechado() -> None:
    observados = set()

    for chamada in (
        lambda: formatar_inteiro(None),  # type: ignore[arg-type]
        lambda: formatar_texto(None),  # type: ignore[arg-type]
        lambda: formatar_simbolo_moeda("USD"),
        lambda: formatar_lista([]),
        lambda: formatar_lista(["alfa", 7]),  # type: ignore[list-item]
    ):
        with pytest.raises(FormatoInaplicavel) as erro:
            chamada()
        observados.add(localizador_de(erro))

    assert observados == {"valor", "codigo", "itens", "itens.item"}


@pytest.mark.parametrize(
    "chamada",
    [
        lambda: formatar_inteiro(SENTINELA),
        lambda: formatar_inteiro_agrupado(SENTINELA),
        lambda: formatar_simbolo_moeda(SENTINELA),
        lambda: formatar_texto(object()),
        lambda: formatar_lista(SENTINELA),
        lambda: formatar_lista([SENTINELA, 7]),
        lambda: formatar_lista({SENTINELA: 1}),
    ],
)
def test_mensagem_nao_ecoa_o_recebido(chamada: object) -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        chamada()  # type: ignore[operator]

    assert SENTINELA not in str(erro.value)


def test_mensagem_nao_ecoa_codigo_nao_suportado() -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda("XPTO_NAO_SUPORTADO")

    assert "XPTO" not in str(erro.value)
    assert "NAO_SUPORTADO" not in str(erro.value)


def test_mensagem_nao_ecoa_inteiro_recusado() -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_inteiro(98765.4321)  # type: ignore[arg-type]

    mensagem = str(erro.value)

    assert not any(caractere.isdigit() for caractere in mensagem)


def test_mensagem_nao_tem_indice_de_item() -> None:
    """O localizador diz que um item falhou, não qual nem onde."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista(["alfa", "beta", "gama", 7])  # type: ignore[list-item]

    mensagem = str(erro.value)

    assert not any(caractere.isdigit() for caractere in mensagem)
    assert "[" not in mensagem


def test_primeira_violacao_encerra() -> None:
    """Duas violações na mesma chamada: a primeira decide, nada é acumulado."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista([7, None])  # type: ignore[list-item]

    assert str(erro.value) == "tipo_invalido: itens.item"


def test_conteiner_invalido_vence_cardinalidade() -> None:
    """A `str` vazia é recusada como contêiner, não como lista de zero itens."""
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_lista("")

    assert localizador_de(erro) == "itens"
    assert categoria_de(erro) == "tipo_invalido"


def test_excecao_sem_cause() -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda("USD")

    assert erro.value.__cause__ is None


def test_excecao_sem_contexto_encadeado() -> None:
    with pytest.raises(FormatoInaplicavel) as erro:
        formatar_simbolo_moeda("USD")

    assert erro.value.__context__ is None


# 8. Contrato de API


def test_all_exato() -> None:
    from casa77_sdr import response_format

    assert response_format.__all__ == [
        "FormatoInaplicavel",
        "formatar_inteiro",
        "formatar_inteiro_agrupado",
        "formatar_simbolo_moeda",
        "formatar_texto",
        "formatar_lista",
    ]


def test_all_tem_seis_nomes() -> None:
    from casa77_sdr import response_format

    assert len(response_format.__all__) == 6


@pytest.mark.parametrize(
    ("funcao", "parametro"),
    [
        (formatar_inteiro, "valor"),
        (formatar_inteiro_agrupado, "valor"),
        (formatar_simbolo_moeda, "codigo"),
        (formatar_texto, "valor"),
        (formatar_lista, "itens"),
    ],
)
def test_assinatura_tem_um_parametro_sem_default(funcao: object, parametro: str) -> None:
    parametros = list(inspect.signature(funcao).parameters.values())  # type: ignore[arg-type]

    assert [p.name for p in parametros] == [parametro]
    assert parametros[0].default is inspect.Parameter.empty


@pytest.mark.parametrize(
    "funcao",
    [
        formatar_inteiro,
        formatar_inteiro_agrupado,
        formatar_simbolo_moeda,
        formatar_texto,
        formatar_lista,
    ],
)
def test_nenhum_formatador_tem_parametro_de_estilo(funcao: object) -> None:
    """Sem `estilo`, `padrao`, `locale` ou variante: a saída é única."""
    parametros = inspect.signature(funcao).parameters  # type: ignore[arg-type]

    assert len(parametros) == 1
    for proibido in ("estilo", "padrao", "locale", "formato", "variante"):
        assert proibido not in parametros


def test_init_nao_exporta_os_formatadores() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "response_format" not in codigo
    assert "FormatoInaplicavel" not in codigo
    for nome in (
        "formatar_inteiro",
        "formatar_inteiro_agrupado",
        "formatar_simbolo_moeda",
        "formatar_texto",
        "formatar_lista",
    ):
        assert nome not in codigo


# 9. `hora` não existe nesta fronteira


def test_formato_hora_nao_foi_implementado() -> None:
    """C-6d fica fora: a escolha entre `HH:MM` e `Hh` não está arbitrada."""
    from casa77_sdr import response_format

    assert not hasattr(response_format, "formatar_hora")
    assert "formatar_hora" not in response_format.__all__


def test_modulo_nao_tem_helper_de_hora() -> None:
    nomes = {
        no.name
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, (ast.FunctionDef, ast.ClassDef))
    }

    for proibido in ("formatar_hora", "_formatar_hora", "_hora", "_minutos"):
        assert proibido not in nomes


def test_modulo_nao_declara_padrao_de_hora() -> None:
    codigo = MODULO.read_text(encoding="utf-8")

    for proibido in ('"HH:MM"', "'HH:MM'", '"Hh"', "'Hh'", '"%H'):
        assert proibido not in codigo


# 10. Pureza estrutural, por AST


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


def test_imports_de_producao_sao_minimos() -> None:
    assert modulos_importados() == {"__future__", "collections.abc"}


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
        "decimal",
        "datetime",
        "babel",
        "casa77_sdr",
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_equivalence",
        "casa77_sdr.knowledge",
        "casa77_sdr.rules",
        "casa77_sdr.qualification",
    ],
)
def test_modulo_nao_importa_proibido(proibido: str) -> None:
    assert proibido not in modulos_importados()


def test_modulo_nao_depende_do_pacote() -> None:
    """Pureza: o formatador não conhece índice, carregador nem comparador."""
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
        "environ",
        "getenv",
        "system",
        "run",
        "urlopen",
        "request",
        "connect",
        "socket",
        "load",
        "safe_load",
        "dump",
        "safe_dump",
    }

    assert usados & proibidos == set()


def test_modulo_nao_consulta_locale() -> None:
    usados = identificadores_do_codigo()
    proibidos = {"setlocale", "localeconv", "getlocale", "nl_langinfo", "format_string"}

    assert usados & proibidos == set()
    assert "locale" not in modulos_importados()


@pytest.mark.parametrize(
    "termo",
    [
        "knowledge",
        "casa77.yaml",
        "indice-respostas-aprovadas.yaml",
        "respostas-aprovadas",
    ],
)
def test_modulo_nao_menciona_fonte_comercial(termo: str) -> None:
    assert termo not in MODULO.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "termo",
    [
        "placeholder",
        "template",
        "renderer",
        "renderizar",
        "markdown",
        "fragmento",
        "binding",
        "assertiva",
        "indice",
        "handoff",
        "E09",
        "lead",
        "orquestrador",
    ],
)
def test_modulo_nao_conhece_consumidor_nem_vizinhanca(termo: str) -> None:
    """A fronteira formata um valor recebido, e não sabe quem a chama."""
    identificadores = {nome.lower() for nome in identificadores_do_codigo()}

    assert termo.lower() not in identificadores


def test_modulo_nao_declara_despachante_por_token_de_formato() -> None:
    """Nenhuma tabela `formato -> função`: cada formatador é chamado direto."""
    codigo = MODULO.read_text(encoding="utf-8")
    identificadores = identificadores_do_codigo()

    for token in ("inteiro_agrupado", "simbolo_moeda"):
        assert f'"{token}"' not in codigo
    for proibido in ("formatar", "aplicar_formato", "despachar", "FORMATOS"):
        assert proibido not in identificadores


def test_modulo_tem_uma_unica_classe_publica() -> None:
    classes = [
        no.name
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.ClassDef)
    ]

    assert classes == ["FormatoInaplicavel"]


def test_modulo_expoe_exatamente_as_cinco_funcoes_publicas() -> None:
    publicas = [
        no.name
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.FunctionDef) and not no.name.startswith("_")
    ]

    assert publicas == [
        "formatar_inteiro",
        "formatar_inteiro_agrupado",
        "formatar_simbolo_moeda",
        "formatar_texto",
        "formatar_lista",
    ]


def test_modulo_nao_declara_enum_nem_dataclass() -> None:
    """A prova é sobre o código: a prosa pode dizer "enumeração" à vontade."""
    usados = identificadores_do_codigo()

    assert not {"Enum", "StrEnum", "IntEnum", "dataclass"} & usados
    for no in ast.walk(arvore_do_modulo()):
        if isinstance(no, ast.ClassDef):
            assert not no.bases or [
                base.id for base in no.bases if isinstance(base, ast.Name)
            ] == ["Exception"]
            assert not no.decorator_list


def test_modulo_nao_usa_formatacao_de_milhar_da_linguagem() -> None:
    """O agrupamento é montado dígito a dígito, e não delegado ao `format`."""
    codigo = MODULO.read_text(encoding="utf-8")

    for delegacao in (":,", ":_", "{:,}", "format(", ".format("):
        assert delegacao not in codigo


def test_tabela_de_moedas_tem_um_unico_codigo() -> None:
    """C-A4-F2d: a tabela não é ampliada por esta entrega."""
    from casa77_sdr import response_format

    assert response_format._SIMBOLO_POR_CODIGO == {"BRL": "R$"}
