"""Testes da sintaxe física de *placeholder* — `PH1`–`PH12`.

A fronteira fecha **somente** a forma física do *placeholder* no *template* de um
fragmento emitível: a derivação canônica `{{nome}}`, a gramática do nome de
*binding* `RENDERIZADO`, a reserva das chaves, o *parsing* literal, a
cardinalidade de uma ou mais ocorrências e a decomposição alternada.

Estes testes provam a derivação, a gramática, as formas inválidas de envelope, a
correspondência entre *template* e *bindings*, a repetição do mesmo
*placeholder*, a ordem física da decomposição, a literalidade — sem NFC, sem
`strip`, sem alteração de caixa —, o *round-trip* que reconstrói o *template*
original, a ausência de vazamento nas mensagens e a pureza de importação do
módulo de produção.

**Todo o corpus é sintético.** Nenhum preço, capacidade, horário, prazo,
percentual ou quantidade real aparece, nenhuma frase aprovada é reproduzida e
**nada em `knowledge/**` é lido**.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from casa77_sdr import response_placeholder
from casa77_sdr.response_placeholder import (
    PlaceholderInvalido,
    decompor_template,
    derivar_placeholder,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "response_placeholder.py"

# Sentinela sintética: jamais deve aparecer na mensagem da exceção.
SENTINELA = "SENTINELA_NAO_DEVE_VAZAR"


def reconstruir(partes: tuple[str, ...]) -> str:
    """Recompõe o *template* recolocando `{{nome}}` nas posições ímpares."""
    return "".join(
        parte if indice % 2 == 0 else "{{" + parte + "}}"
        for indice, parte in enumerate(partes)
    )


# ---------------------------------------------------------------------------
# A. `derivar_placeholder` — nomes válidos


@pytest.mark.parametrize(
    "nome",
    ["a", "a1", "valor_exemplo", "x9_y8", "z", "campo_exemplo_dois", "a1_b2_c3"],
)
def test_derivacao_valida(nome: str) -> None:
    assert derivar_placeholder(nome) == "{{" + nome + "}}"


def test_derivacao_e_a_unica_representacao() -> None:
    assert derivar_placeholder("valor_exemplo") == "{{valor_exemplo}}"


def test_derivacao_e_deterministica() -> None:
    assert len({derivar_placeholder("x9_y8") for _ in range(4)}) == 1


# ---------------------------------------------------------------------------
# B. `derivar_placeholder` — nomes inválidos (PH4)


@pytest.mark.parametrize(
    "nome",
    [
        "",
        "A",
        "Valor",
        "VALOR",
        "_a",
        "a_",
        "a__b",
        "1a",
        "9",
        "a-b",
        "a.b",
        "a b",
        "a\n",
        "a\t",
        "á",
        "ç",
        "a{",
        "a}",
        "a٣",
        "{{a}}",
        "a@b",
        "a[b]",
        "a/b",
        "a=b",
        "a'b",
        "_",
        "__",
    ],
)
def test_nome_invalido_e_recusado(nome: str) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        derivar_placeholder(nome)

    assert str(erro.value) == "valor_invalido: nome"


@pytest.mark.parametrize("nome", [None, 0, b"a", ["a"], ("a",), {"a": 1}, True])
def test_nome_nao_str_e_recusado(nome: object) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        derivar_placeholder(nome)

    assert str(erro.value) == "tipo_invalido: nome"


def test_subclasse_de_str_nao_e_nome_canonico() -> None:
    class _StrDerivada(str):
        pass

    with pytest.raises(PlaceholderInvalido) as erro:
        derivar_placeholder(_StrDerivada("a"))

    assert str(erro.value) == "tipo_invalido: nome"


# ---------------------------------------------------------------------------
# C. `decompor_template` — templates válidos


def test_template_sem_placeholder() -> None:
    assert decompor_template("texto sintetico apenas.", ()) == (
        "texto sintetico apenas.",
    )


def test_template_vazio_sem_nomes() -> None:
    assert decompor_template("", ()) == ("",)


def test_um_placeholder() -> None:
    assert decompor_template("A {{x}} B", ("x",)) == ("A ", "x", " B")


def test_varios_placeholders_distintos() -> None:
    resultado = decompor_template("A {{x}} B {{y}} C", ("x", "y"))
    assert resultado == ("A ", "x", " B ", "y", " C")


def test_placeholder_na_primeira_posicao() -> None:
    assert decompor_template("{{x}} resto", ("x",)) == ("", "x", " resto")


def test_placeholder_na_ultima_posicao() -> None:
    assert decompor_template("inicio {{x}}", ("x",)) == ("inicio ", "x", "")


def test_template_e_somente_um_placeholder() -> None:
    assert decompor_template("{{x}}", ("x",)) == ("", "x", "")


def test_placeholders_adjacentes_produzem_literal_vazio() -> None:
    assert decompor_template("{{x}}{{y}}", ("x", "y")) == ("", "x", "", "y", "")


def test_mesmo_placeholder_repetido_duas_vezes() -> None:
    resultado = decompor_template("A {{x}} B {{x}} C", ("x",))
    assert resultado == ("A ", "x", " B ", "x", " C")


def test_mesmo_placeholder_repetido_tres_vezes() -> None:
    resultado = decompor_template("{{x}}-{{x}}-{{x}}", ("x",))
    assert resultado == ("", "x", "-", "x", "-", "x", "")


def test_exemplo_sintetico_do_contrato() -> None:
    """`PH7c` e `PH10b`: o nome repetido permanece repetido na decomposição."""
    resultado = decompor_template("A {{x}} B {{x}} C {{y}}.", ("x", "y"))
    assert resultado == ("A ", "x", " B ", "x", " C ", "y", ".")


@pytest.mark.parametrize(
    ("template", "nomes"),
    [
        ("", ()),
        ("sem nada", ()),
        ("{{x}}", ("x",)),
        ("A {{x}} B {{x}} C {{y}}.", ("x", "y")),
        ("{{x}}{{y}}{{x}}", ("x", "y")),
    ],
)
def test_comprimento_e_sempre_impar(template: str, nomes: tuple[str, ...]) -> None:
    assert len(decompor_template(template, nomes)) % 2 == 1


def test_ordem_segue_o_template_e_nao_a_tupla() -> None:
    """`PH10a`: a ordem é a física de ocorrência, não a de `nomes`."""
    resultado = decompor_template("{{y}} e {{x}}", ("x", "y"))
    assert resultado == ("", "y", " e ", "x", "")


# ---------------------------------------------------------------------------
# D. Correspondência template × bindings (PH7, PH8)


def test_placeholder_sem_binding() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("A {{x}} B", ())

    assert str(erro.value) == "placeholder_sem_binding: placeholder"


def test_placeholder_desconhecido_entre_conhecidos() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{x}} {{z}}", ("x", "y"))

    assert str(erro.value) == "placeholder_sem_binding: placeholder"


def test_binding_sem_placeholder() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("A {{x}} B", ("x", "y"))

    assert str(erro.value) == "binding_sem_placeholder: placeholder"


def test_binding_sem_placeholder_com_template_sem_nenhum() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("texto sem placeholder", ("x",))

    assert str(erro.value) == "binding_sem_placeholder: placeholder"


def test_nome_duplicado_em_nomes() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{x}}", ("x", "x"))

    assert str(erro.value) == "duplicidade: nomes.item"


def test_repeticao_no_template_nao_exige_binding_duplicado() -> None:
    """`PH7c`: um único *binding* abastece todas as ocorrências."""
    assert decompor_template("{{x}} {{x}}", ("x",)) == ("", "x", " ", "x", "")


# ---------------------------------------------------------------------------
# E. Formas inválidas de envelope (PH5, PH6)


@pytest.mark.parametrize(
    "template",
    [
        "{",
        "}",
        "{x}",
        "{{x",
        "x}}",
        "{{}}",
        "{{ x }}",
        "{{X}}",
        "{{x-y}}",
        "{{{x}}}",
        "{{x}}}",
        "a { b",
        "a } b",
        "{{x}",
        "{{a.b}}",
        "{{_x}}",
        "{{x_}}",
        "{{1x}}",
        "{{a}b}}",
        "{{x}}{{",
    ],
)
def test_forma_invalida_de_template(template: str) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template(template, ("x",))

    assert str(erro.value) == "forma_invalida: template"


def test_chave_literal_nao_tem_escaping() -> None:
    """`PH5`: não existe *escaping*; nenhuma intenção é inferida."""
    with pytest.raises(PlaceholderInvalido):
        decompor_template("preco entre {chaves}", ())


# ---------------------------------------------------------------------------
# F. Tipos de entrada


@pytest.mark.parametrize("template", [None, 0, b"a", ["a"], ("a",), {"a": 1}])
def test_template_nao_str(template: object) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template(template, ())

    assert str(erro.value) == "tipo_invalido: template"


@pytest.mark.parametrize("nomes", [None, "x", ["x"], {"x"}, {"x": 1}, 0])
def test_nomes_nao_tuple(nomes: object) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{x}}", nomes)

    assert str(erro.value) == "tipo_invalido: nomes"


@pytest.mark.parametrize("item", [None, 0, b"x", ["x"], ("x",)])
def test_item_de_nomes_nao_str(item: object) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{x}}", (item,))

    assert str(erro.value) == "tipo_invalido: nomes.item"


@pytest.mark.parametrize("item", ["", "A", "_a", "a_", "a__b", "1a", "a-b", "á"])
def test_item_de_nomes_com_gramatica_invalida(item: str) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{x}}", (item,))

    assert str(erro.value) == "valor_invalido: nomes.item"


def test_subclasse_de_str_em_nomes_e_recusada() -> None:
    class _StrDerivada(str):
        pass

    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{x}}", (_StrDerivada("x"),))

    assert str(erro.value) == "tipo_invalido: nomes.item"


# ---------------------------------------------------------------------------
# G. Precedência determinística (§9)


def test_tipo_de_template_vence_tipo_de_nomes() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template(None, None)

    assert str(erro.value) == "tipo_invalido: template"


def test_tipo_de_nomes_vence_forma_do_template() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{", None)

    assert str(erro.value) == "tipo_invalido: nomes"


def test_nomes_vencem_forma_do_template() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{", ("A",))

    assert str(erro.value) == "valor_invalido: nomes.item"


def test_gramatica_vence_duplicidade() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{x}}", ("A", "A"))

    assert str(erro.value) == "valor_invalido: nomes.item"


def test_forma_do_template_vence_nome_faltante() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{", ("x",))

    assert str(erro.value) == "forma_invalida: template"


def test_correspondencia_vence_nome_faltante() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{z}}", ("x",))

    assert str(erro.value) == "placeholder_sem_binding: placeholder"


def test_primeira_violacao_do_template_encerra() -> None:
    """A varredura é da esquerda para a direita: o `}` isolado vem antes."""
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("} {{z}}", ("x",))

    assert str(erro.value) == "forma_invalida: template"


# ---------------------------------------------------------------------------
# H. Literalidade (PH9)


@pytest.mark.parametrize(
    "template",
    [
        "  espaco preservado  ",
        "linha um\nlinha dois",
        "tab\there",
        "Caixa MISTA Preservada",
        "acentuacao: café e café",
        "\r\n misto \r\n",
    ],
)
def test_literal_e_preservado_sem_normalizacao(template: str) -> None:
    assert decompor_template(template, ()) == (template,)


def test_nfc_nao_e_aplicado() -> None:
    """`PH9`: NFC pertence exclusivamente a `C-15b` e não é reaberta aqui."""
    decomposto = "café"
    precomposto = "café"

    assert decompor_template(decomposto, ()) == (decomposto,)
    assert decompor_template(precomposto, ()) == (precomposto,)
    assert decompor_template(decomposto, ()) != decompor_template(precomposto, ())


def test_lf_permanece_literal_dentro_do_literal() -> None:
    resultado = decompor_template("antes\n{{x}}\ndepois", ("x",))
    assert resultado == ("antes\n", "x", "\ndepois")


def test_espacos_ao_redor_do_placeholder_sao_preservados() -> None:
    assert decompor_template("  {{x}}  ", ("x",)) == ("  ", "x", "  ")


@pytest.mark.parametrize(
    ("template", "nomes"),
    [
        ("", ()),
        ("so texto", ()),
        ("{{x}}", ("x",)),
        ("A {{x}} B", ("x",)),
        ("{{x}}{{y}}", ("x", "y")),
        ("A {{x}} B {{x}} C {{y}}.", ("x", "y")),
        ("  {{x}}\n{{y}}\t", ("x", "y")),
        ("{{a1_b2}} e {{z}}", ("a1_b2", "z")),
    ],
)
def test_round_trip_reconstroi_o_template(
    template: str, nomes: tuple[str, ...]
) -> None:
    assert reconstruir(decompor_template(template, nomes)) == template


def test_round_trip_usa_a_mesma_derivacao() -> None:
    """A reconstrução coincide com `derivar_placeholder` (`PH2`, `PH3b`)."""
    partes = decompor_template("A {{x}} B", ("x",))
    assert partes[0] + derivar_placeholder(partes[1]) + partes[2] == "A {{x}} B"


# ---------------------------------------------------------------------------
# I. Correspondência com `binding.placeholder` (PH3)


@pytest.mark.parametrize("nome", ["a", "valor_exemplo", "x9_y8"])
def test_placeholder_derivado_ocorre_no_template(nome: str) -> None:
    """`PH3b`: o campo explícito é exatamente a derivação do nome."""
    placeholder = derivar_placeholder(nome)
    template = "antes " + placeholder + " depois"

    assert decompor_template(template, (nome,)) == ("antes ", nome, " depois")


# ---------------------------------------------------------------------------
# J. Segurança das mensagens


@pytest.mark.parametrize(
    ("template", "nomes"),
    [
        (SENTINELA + " {{", ("x",)),
        (SENTINELA + " {{z}}", ("x",)),
        (SENTINELA, ("x",)),
        ("{{x}}", (SENTINELA,)),
    ],
)
def test_mensagem_nao_vaza_sentinela(template: str, nomes: tuple) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template(template, nomes)

    assert SENTINELA not in str(erro.value)


def test_mensagem_nao_vaza_nome_recebido() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        derivar_placeholder(SENTINELA)

    assert SENTINELA not in str(erro.value)


@pytest.mark.parametrize(
    ("template", "nomes"),
    [("{{", ("x",)), ("{{z}}", ("x",)), ("texto", ("x",)), ("{{x}}", ("x", "x"))],
)
def test_mensagem_tem_categoria_e_localizador(
    template: str, nomes: tuple[str, ...]
) -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template(template, nomes)

    partes = str(erro.value).split(": ")
    assert len(partes) == 2
    assert partes[0] in {
        "tipo_invalido",
        "valor_invalido",
        "duplicidade",
        "forma_invalida",
        "placeholder_sem_binding",
        "binding_sem_placeholder",
    }
    assert partes[1] in {"nome", "template", "nomes", "nomes.item", "placeholder"}


def test_mensagem_nao_tem_repr_nem_posicao() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("abc {{ x }} def", ("x",))

    mensagem = str(erro.value)
    assert not any(caractere.isdigit() for caractere in mensagem)
    assert "'" not in mensagem
    assert "<" not in mensagem
    assert "{" not in mensagem


def test_excecao_deriva_diretamente_de_exception() -> None:
    assert PlaceholderInvalido.__bases__ == (Exception,)


def test_excecao_sem_cause_nem_contexto() -> None:
    with pytest.raises(PlaceholderInvalido) as erro:
        decompor_template("{{", ("x",))

    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None


# ---------------------------------------------------------------------------
# K. API pública e pureza


def test_all_exato() -> None:
    assert response_placeholder.__all__ == [
        "PlaceholderInvalido",
        "derivar_placeholder",
        "decompor_template",
    ]


def test_producao_importa_somente_future() -> None:
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))

    importados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)

    assert importados == {"__future__"}
