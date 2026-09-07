"""Testes do parser puro da gramática de `caminho_yaml`.

A fronteira materializa **exclusivamente** a primeira responsabilidade de
`CY13`: o **parser da gramática**. Ela julga **somente** a `str` — sintaxe,
alfabeto, absoluto × relativo, seletor, canonicalidade e chave numérica não
endereçável — e devolve a **decomposição imutável já validada**.

Estes testes provam a forma da saída, a distinção explícita entre absoluto e
relativo, o `@` isolado, o seletor único por segmento, o literal numérico
válido, a chave numérica inválida, as três categorias fechadas, os seis
localizadores semânticos, a precedência fixa, o determinismo e a pureza do
módulo de produção. Eles **não** transformam em norma coisa alguma sobre
`itera_sobre`, resolução, `C-7` ou índice — tudo isso está **fora** desta
fronteira. **Nenhum teste toca o corpus versionado**: todos os casos são
**sintéticos**.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr import response_yaml_path
from casa77_sdr.response_yaml_path import CaminhoYamlInvalido, analisar_caminho_yaml

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_yaml_path.py"
)
CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)

MAIUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
DIGITOS = "0123456789"
ALFABETO_DE_NOME = MAIUSCULAS + MINUSCULAS + DIGITOS + "_"


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


def erro_de(caminho):
    """Mensagem da recusa de `caminho`, para asserção direta."""
    with pytest.raises(CaminhoYamlInvalido) as erro:
        analisar_caminho_yaml(caminho)
    return str(erro.value)


# ---------------------------------------------------------------------------
# A. Casos-guia de sucesso
# ---------------------------------------------------------------------------


def test_segmento_unico_absoluto():
    assert analisar_caminho_yaml("bloco_exemplo") == (False, (("bloco_exemplo", None),))


def test_dois_segmentos_absolutos():
    assert analisar_caminho_yaml("bloco_exemplo.campo_exemplo") == (
        False,
        (("bloco_exemplo", None), ("campo_exemplo", None)),
    )


def test_absoluto_com_seletor_no_meio():
    assert analisar_caminho_yaml(
        "bloco_exemplo.colecao_exemplo[id=item_exemplo].campo_exemplo"
    ) == (
        False,
        (
            ("bloco_exemplo", None),
            ("colecao_exemplo", ("id", "item_exemplo")),
            ("campo_exemplo", None),
        ),
    )


def test_seletor_com_literal_numerico():
    assert analisar_caminho_yaml("colecao[id=2026]") == (
        False,
        (("colecao", ("id", "2026")),),
    )


def test_relativo_com_um_segmento():
    assert analisar_caminho_yaml("@.campo_exemplo") == (
        True,
        (("campo_exemplo", None),),
    )


def test_relativo_com_dois_segmentos():
    assert analisar_caminho_yaml("@.submapa.campo_exemplo") == (
        True,
        (("submapa", None), ("campo_exemplo", None)),
    )


def test_relativo_com_seletor():
    assert analisar_caminho_yaml(
        "@.colecao_exemplo[id=item_exemplo].campo_exemplo"
    ) == (
        True,
        (("colecao_exemplo", ("id", "item_exemplo")), ("campo_exemplo", None)),
    )


def test_arroba_isolado():
    """`CY11`: `@` sozinho é o próprio item corrente, sem segmento algum."""
    assert analisar_caminho_yaml("@") == (True, ())


def test_seletor_no_ultimo_segmento():
    assert analisar_caminho_yaml("bloco_exemplo.colecao_exemplo[id=item_exemplo]") == (
        False,
        (("bloco_exemplo", None), ("colecao_exemplo", ("id", "item_exemplo"))),
    )


def test_seletor_no_primeiro_segmento():
    assert analisar_caminho_yaml("colecao_exemplo[id=item_exemplo].campo_exemplo") == (
        False,
        (("colecao_exemplo", ("id", "item_exemplo")), ("campo_exemplo", None)),
    )


def test_dois_seletores_em_segmentos_distintos_sao_validos():
    """A restrição é **um por segmento**, não um por caminho."""
    assert analisar_caminho_yaml("a[x=y].b[z=w]") == (
        False,
        (("a", ("x", "y")), ("b", ("z", "w"))),
    )


def test_sublinhado_isolado_e_chave_valida():
    assert analisar_caminho_yaml("_") == (False, (("_", None),))


def test_chave_alfanumerica_iniciada_por_digito_e_valida():
    """Só a chave **exclusivamente** numérica é recusada."""
    assert analisar_caminho_yaml("2026_exemplo") == (False, (("2026_exemplo", None),))


def test_caixa_e_significativa():
    assert analisar_caminho_yaml("Bloco") != analisar_caminho_yaml("bloco")
    assert analisar_caminho_yaml("Bloco") == (False, (("Bloco", None),))


def test_todo_o_alfabeto_de_nome_e_aceito_em_chave():
    assert analisar_caminho_yaml(ALFABETO_DE_NOME) == (
        False,
        ((ALFABETO_DE_NOME, None),),
    )


def test_todo_o_alfabeto_de_nome_e_aceito_em_literal():
    assert analisar_caminho_yaml(f"a[x={ALFABETO_DE_NOME}]") == (
        False,
        (("a", ("x", ALFABETO_DE_NOME)),),
    )


# ---------------------------------------------------------------------------
# B. Forma e imutabilidade da saida
# ---------------------------------------------------------------------------


def test_forma_da_saida_e_par_bool_tupla():
    resultado = analisar_caminho_yaml("a.b[c=d]")
    assert type(resultado) is tuple
    assert len(resultado) == 2
    relativo, segmentos = resultado
    assert type(relativo) is bool
    assert type(segmentos) is tuple


def test_cada_segmento_e_par_de_str_e_seletor():
    _, segmentos = analisar_caminho_yaml("a.b[c=d]")
    for entrada in segmentos:
        assert type(entrada) is tuple
        assert len(entrada) == 2
        chave, seletor = entrada
        assert type(chave) is str
        assert seletor is None or type(seletor) is tuple
    assert segmentos[0][1] is None
    assert segmentos[1][1] == ("c", "d")
    assert type(segmentos[1][1][0]) is str
    assert type(segmentos[1][1][1]) is str


def test_saida_e_imutavel():
    _, segmentos = analisar_caminho_yaml("a.b")
    with pytest.raises(TypeError):
        segmentos[0] = ("z", None)


def test_saida_nao_contem_estrutura_mutavel():
    resultado = analisar_caminho_yaml("a.b[c=d]")
    pilha = [resultado]
    while pilha:
        no = pilha.pop()
        assert not isinstance(no, (list, dict, set, bytearray))
        if isinstance(no, tuple):
            pilha.extend(no)


# ---------------------------------------------------------------------------
# C. Absoluto x relativo
# ---------------------------------------------------------------------------


def test_absoluto_devolve_falso():
    relativo, _ = analisar_caminho_yaml("a.b")
    assert relativo is False


def test_relativo_devolve_verdadeiro():
    relativo, _ = analisar_caminho_yaml("@.a")
    assert relativo is True


def test_marcador_nao_aparece_nos_segmentos():
    _, segmentos = analisar_caminho_yaml("@.a.b")
    assert segmentos == (("a", None), ("b", None))


def test_absoluto_e_relativo_com_mesmos_segmentos_diferem_so_na_forma():
    absoluto = analisar_caminho_yaml("a.b")
    relativo = analisar_caminho_yaml("@.a.b")
    assert absoluto[1] == relativo[1]
    assert absoluto[0] is False
    assert relativo[0] is True


# ---------------------------------------------------------------------------
# D. Seletor
# ---------------------------------------------------------------------------


def test_seletor_ausente_e_none():
    _, segmentos = analisar_caminho_yaml("a")
    assert segmentos[0][1] is None


def test_seletor_presente_e_par_chave_literal():
    _, segmentos = analisar_caminho_yaml("a[chave_exemplo=valor_exemplo]")
    assert segmentos[0][1] == ("chave_exemplo", "valor_exemplo")


def test_dois_seletores_no_mesmo_segmento_sao_invalidos():
    assert erro_de("a[x=y][z=w]") == "forma_invalida: seletor"


def test_caracteres_apos_o_fechamento_sao_invalidos():
    assert erro_de("a[x=y]resto") == "forma_invalida: seletor"


def test_seletor_sem_fechamento_e_invalido():
    assert erro_de("a[x=y") == "forma_invalida: seletor"


def test_fechamento_extra_e_invalido():
    assert erro_de("a[x=y]]") == "forma_invalida: seletor"


def test_seletor_vazio_e_invalido():
    assert erro_de("a[]") == "forma_invalida: seletor"


def test_seletor_sem_igual_e_invalido():
    assert erro_de("a[x]") == "forma_invalida: seletor"


def test_chave_seletora_vazia_e_invalida():
    assert erro_de("a[=x]") == "forma_invalida: chave_seletora"


def test_literal_vazio_e_invalido():
    assert erro_de("a[x=]") == "forma_invalida: literal"


def test_literal_com_igual_extra_e_invalido():
    assert erro_de("a[x=y=z]") == "forma_invalida: literal"


def test_fechamento_sem_abertura_e_invalido():
    assert erro_de("a]") == "forma_invalida: chave"


def test_selecao_posicional_e_invalida():
    """`C-A1-S1`: `[0]` não tem forma de seletor e a chave `0` não é endereçável."""
    assert erro_de("colecao[0]") == "forma_invalida: seletor"
    assert erro_de("colecao[0=x]") == "chave_nao_enderecavel: chave_seletora"


# ---------------------------------------------------------------------------
# E. Chave nao enderecavel x literal numerico
# ---------------------------------------------------------------------------


def test_chave_unica_exclusivamente_numerica_e_invalida():
    assert erro_de("123") == "chave_nao_enderecavel: chave"


def test_chave_de_segmento_exclusivamente_numerica_e_invalida():
    assert erro_de("a.123") == "chave_nao_enderecavel: chave"


def test_chave_seletora_exclusivamente_numerica_e_invalida():
    assert erro_de("a[123=x]") == "chave_nao_enderecavel: chave_seletora"


def test_literal_exclusivamente_numerico_e_valido():
    """Contraste obrigatório: o literal é **sempre** semanticamente uma `str`."""
    assert analisar_caminho_yaml("a[x=123]") == (False, (("a", ("x", "123")),))


def test_chave_numerica_com_zero_a_esquerda_e_invalida():
    assert erro_de("a.007") == "chave_nao_enderecavel: chave"


def test_chave_numerica_relativa_tambem_e_invalida():
    assert erro_de("@.123") == "chave_nao_enderecavel: chave"


def test_digito_nao_ascii_nao_e_digito_nem_nome():
    """Um dígito decimal de outro sistema de escrita não pertence ao alfabeto."""
    assert erro_de("١٢٣") == "forma_invalida: chave"


# ---------------------------------------------------------------------------
# F. Tipo da entrada
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entrada", [None, 0, 1, True, False, 2.0, [], (), {}, b"a"])
def test_entrada_nao_str_e_tipo_invalido(entrada):
    assert erro_de(entrada) == "tipo_invalido: caminho"


def test_subclasse_de_str_e_recusada():
    class Caminho(str):
        pass

    assert erro_de(Caminho("bloco_exemplo")) == "tipo_invalido: caminho"


def test_subclasse_de_str_e_recusada_antes_de_qualquer_leitura():
    class Caminho(str):
        def __getitem__(self, indice):  # pragma: no cover - nunca invocado
            raise AssertionError("a entrada nao pode ser lida")

        def find(self, *args):  # pragma: no cover - nunca invocado
            raise AssertionError("a entrada nao pode ser lida")

    assert erro_de(Caminho("bloco_exemplo")) == "tipo_invalido: caminho"


def test_tipo_e_julgado_antes_da_forma():
    class Caminho(str):
        pass

    assert erro_de(Caminho("")) == "tipo_invalido: caminho"


# ---------------------------------------------------------------------------
# G. Falhas de forma e canonicalidade
# ---------------------------------------------------------------------------


def test_str_vazia_e_invalida():
    assert erro_de("") == "forma_invalida: caminho"


def test_ponto_inicial_e_invalido():
    assert erro_de(".a") == "forma_invalida: segmento"


def test_ponto_final_e_invalido():
    assert erro_de("a.") == "forma_invalida: segmento"


def test_ponto_duplo_e_invalido():
    assert erro_de("a..b") == "forma_invalida: segmento"


def test_ponto_isolado_e_invalido():
    assert erro_de(".") == "forma_invalida: segmento"


def test_arroba_no_meio_e_invalido():
    assert erro_de("a.@b") == "forma_invalida: chave"


def test_arroba_dentro_da_chave_e_invalido():
    assert erro_de("a@b") == "forma_invalida: chave"


def test_arroba_duplo_e_invalido():
    assert erro_de("@@") == "forma_invalida: caminho"


def test_arroba_seguido_de_chave_sem_ponto_e_invalido():
    assert erro_de("@a") == "forma_invalida: caminho"


def test_arroba_seguido_de_ponto_sem_segmento_e_invalido():
    assert erro_de("@.") == "forma_invalida: segmento"


def test_arroba_seguido_de_seletor_e_invalido():
    assert erro_de("@[x=y]") == "forma_invalida: caminho"


@pytest.mark.parametrize(
    "caminho",
    [
        "a b",
        "a\tb",
        "a\nb",
        "a\rb",
        "a\x0bb",
        "a\x0cb",
        "a\xa0b",
        " a",
        "a ",
    ],
)
def test_whitespace_e_invalido(caminho):
    assert erro_de(caminho) == "forma_invalida: chave"


@pytest.mark.parametrize(
    "caminho",
    ['a"b', "a'b", "a\\b", "a/b", "a-b", "a:b", "a*b", "a+b", "a#b", "a$b", "a%b"],
)
def test_caracteres_fora_do_alfabeto_sao_invalidos(caminho):
    assert erro_de(caminho) == "forma_invalida: chave"


@pytest.mark.parametrize(
    "caminho", ["café", "seção", "á", "não", "中"]
)
def test_unicode_nao_ascii_e_invalido(caminho):
    assert erro_de(caminho) == "forma_invalida: chave"


@pytest.mark.parametrize("caminho", ["a[x=y z]", "a[x y=z]", 'a[x="y"]', "a[x=y-z]"])
def test_seletor_com_caracteres_fora_do_alfabeto_e_invalido(caminho):
    assert erro_de(caminho) in {
        "forma_invalida: chave_seletora",
        "forma_invalida: literal",
    }


def test_abertura_sem_chave_e_invalida():
    assert erro_de("[x=y]") == "forma_invalida: chave"


def test_nenhuma_tolerancia_a_espaco_de_borda_no_seletor():
    assert erro_de("a[ x=y]") == "forma_invalida: chave_seletora"
    assert erro_de("a[x=y ]") == "forma_invalida: literal"


# ---------------------------------------------------------------------------
# H. Precedencia
# ---------------------------------------------------------------------------


def test_chave_nao_enderecavel_vence_borda_final_invalida():
    """`123.`: a primeira chave completa e não endereçável vence a borda final."""
    assert erro_de("123.") == "chave_nao_enderecavel: chave"


def test_forma_da_chave_e_julgada_antes_da_enderecabilidade():
    assert erro_de("12 3") == "forma_invalida: chave"


def test_chave_do_segmento_e_julgada_antes_do_seletor():
    assert erro_de("123[456=x]") == "chave_nao_enderecavel: chave"


def test_chave_seletora_e_julgada_antes_do_literal():
    assert erro_de("a[123=]") == "chave_nao_enderecavel: chave_seletora"


def test_primeira_violacao_fisica_encerra():
    assert erro_de("a..b[c") == "forma_invalida: segmento"
    assert erro_de("a.123.b[c") == "chave_nao_enderecavel: chave"


def test_violacao_anterior_vence_violacao_posterior():
    assert erro_de(".a.123") == "forma_invalida: segmento"


def test_nada_e_devolvido_parcialmente():
    resultado = None
    with pytest.raises(CaminhoYamlInvalido):
        resultado = analisar_caminho_yaml("a.b.123")
    assert resultado is None


def test_a_mensagem_nao_ecoa_a_entrada():
    entrada = "segredo_sintetico_nao_deve_aparecer.123"
    with pytest.raises(CaminhoYamlInvalido) as erro:
        analisar_caminho_yaml(entrada)
    mensagem = str(erro.value)
    assert "segredo_sintetico_nao_deve_aparecer" not in mensagem
    assert "123" not in mensagem
    assert mensagem == "chave_nao_enderecavel: chave"


def test_a_mensagem_nao_carrega_indice_nem_tipo():
    for caminho in ("a b", "a.", "a[x]", None, 7):
        mensagem = erro_de(caminho)
        categoria, _, localizador = mensagem.partition(": ")
        assert categoria in {
            "tipo_invalido",
            "forma_invalida",
            "chave_nao_enderecavel",
        }
        assert localizador in {
            "caminho",
            "segmento",
            "seletor",
            "chave",
            "chave_seletora",
            "literal",
        }


# ---------------------------------------------------------------------------
# I. Categorias e localizadores fechados
# ---------------------------------------------------------------------------


def test_constantes_de_modulo_sao_exatamente_as_esperadas():
    """Exatamente **três** categorias e **seis** localizadores existem no módulo."""
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
        "_FORMA_INVALIDA",
        "_CHAVE_NAO_ENDERECAVEL",
        "_CAMINHO",
        "_SEGMENTO",
        "_SELETOR",
        "_CHAVE",
        "_CHAVE_SELETORA",
        "_LITERAL",
        "_CARACTERES_DE_NOME",
        "_DIGITOS_ASCII",
        "_MARCADOR_RELATIVO",
        "_PONTO",
        "_ABRE",
        "_FECHA",
        "_IGUAL",
    ]


def test_as_tres_categorias_e_os_seis_localizadores_sao_literais():
    constantes = set(_constantes_de_codigo())
    assert {"tipo_invalido", "forma_invalida", "chave_nao_enderecavel"} <= constantes
    assert {
        "caminho",
        "segmento",
        "seletor",
        "chave",
        "chave_seletora",
        "literal",
    } <= constantes


def test_categorias_observadas_sao_exatamente_tres():
    observadas = set()
    for caminho in (None, "", "123"):
        observadas.add(erro_de(caminho).split(":")[0])
    assert observadas == {"tipo_invalido", "forma_invalida", "chave_nao_enderecavel"}


def test_localizadores_observados_pertencem_ao_conjunto_fechado():
    observados = set()
    for caminho in (
        None,
        "",
        "a.",
        "a[x]",
        "a b",
        "a[=x]",
        "a[x=]",
    ):
        observados.add(erro_de(caminho).split(": ")[1])
    assert observados <= {
        "caminho",
        "segmento",
        "seletor",
        "chave",
        "chave_seletora",
        "literal",
    }


def test_excecao_e_a_unica_publica():
    assert issubclass(CaminhoYamlInvalido, Exception)
    assert CaminhoYamlInvalido.__mro__[1] is Exception


def test_mensagem_tem_forma_categoria_localizador():
    mensagem = erro_de("a.")
    assert mensagem.count(": ") == 1
    assert mensagem == "forma_invalida: segmento"


# ---------------------------------------------------------------------------
# J. Determinismo e entrada inalterada
# ---------------------------------------------------------------------------


def test_resultado_e_deterministico():
    caminho = "bloco_exemplo.colecao_exemplo[id=item_exemplo].campo_exemplo"
    assert analisar_caminho_yaml(caminho) == analisar_caminho_yaml(caminho)


def test_repeticoes_produzem_o_mesmo_resultado():
    caminho = "@.colecao_exemplo[id=item_exemplo]"
    esperado = analisar_caminho_yaml(caminho)
    for _ in range(5):
        assert analisar_caminho_yaml(caminho) == esperado


def test_falha_e_deterministica():
    assert erro_de("a[x=y][z=w]") == erro_de("a[x=y][z=w]")


def test_entrada_nao_e_alterada():
    caminho = "bloco_exemplo.colecao_exemplo[id=item_exemplo]"
    copia = str(caminho)
    analisar_caminho_yaml(caminho)
    assert caminho == copia


def test_resultado_nao_depende_de_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    monkeypatch.setenv("LC_ALL", "tr_TR.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert analisar_caminho_yaml("Bloco_I") == (False, (("Bloco_I", None),))


# ---------------------------------------------------------------------------
# K. Contrato publico
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_os_dois_nomes():
    assert response_yaml_path.__all__ == [
        "CaminhoYamlInvalido",
        "analisar_caminho_yaml",
    ]


def test_nao_ha_nome_publico_fora_de_all():
    publicos = {
        nome
        for nome in vars(response_yaml_path)
        if not nome.startswith("_") and nome not in {"annotations"}
    }
    assert publicos == set(response_yaml_path.__all__)


def test_assinatura_tem_um_unico_parametro_sem_default():
    assinatura = inspect.signature(analisar_caminho_yaml)
    assert list(assinatura.parameters) == ["caminho"]
    parametro = assinatura.parameters["caminho"]
    assert parametro.default is inspect.Parameter.empty
    assert parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_anotacao_de_retorno_e_a_arbitrada():
    assinatura = inspect.signature(analisar_caminho_yaml)
    assert assinatura.return_annotation == (
        "tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]"
    )


def test_nao_e_exportado_pelo_pacote():
    assert not hasattr(casa77_sdr, "analisar_caminho_yaml")
    assert not hasattr(casa77_sdr, "CaminhoYamlInvalido")
    assert "analisar_caminho_yaml" not in getattr(casa77_sdr, "__all__", [])
    assert "CaminhoYamlInvalido" not in getattr(casa77_sdr, "__all__", [])


def test_producao_declara_uma_unica_classe_e_uma_unica_funcao_publica():
    classes = [
        no.name for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)
    ]
    assert classes == ["CaminhoYamlInvalido"]
    funcoes = [
        no.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert funcoes[0] == "analisar_caminho_yaml"
    assert all(nome.startswith("_") for nome in funcoes[1:])


def test_producao_nao_declara_dto_nem_dataclass():
    proibidos = {"dataclass", "NamedTuple", "TypedDict", "Enum", "StrEnum"}
    assert not proibidos & NOMES_PRODUCAO


# ---------------------------------------------------------------------------
# L. Pureza do modulo de producao
# ---------------------------------------------------------------------------


def test_import_e_exatamente_um():
    assert not [no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.Import)]
    de_onde = [
        no for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ImportFrom)
    ]
    assert [no.module for no in de_onde] == ["__future__"]
    assert [alias.name for no in de_onde for alias in no.names] == ["annotations"]


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
        assert chamada.func.id == "_invalido"


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


def test_nao_ha_relogio_aleatoriedade_locale_ambiente_nem_logging():
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
        "md5",
        "sha256",
        "logging",
        "getLogger",
        "cache",
        "lru_cache",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_regex_nem_unicodedata():
    proibidos = {
        "re",
        "regex",
        "match",
        "fullmatch",
        "search",
        "sub",
        "unicodedata",
        "normalize",
    }
    assert not proibidos & NOMES_PRODUCAO


def test_nao_ha_normalizacao_de_caixa_nem_strip():
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
        "expandtabs",
        "translate",
        "replace",
        "isdigit",
        "isalnum",
        "isascii",
        "isidentifier",
    }
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
    for nome, valor in vars(response_yaml_path).items():
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


# ---------------------------------------------------------------------------
# M. Limites
# ---------------------------------------------------------------------------


def test_a_fronteira_nao_distingue_caminho_yaml_de_itera_sobre():
    """A mesma `str` é analisada igualmente, venha de onde vier."""
    assert analisar_caminho_yaml("colecao_exemplo") == (
        False,
        (("colecao_exemplo", None),),
    )


def test_relativo_e_aceito_sem_contexto_de_itera_sobre():
    """A validação contextual de `CY13` **não** pertence a esta fronteira."""
    assert analisar_caminho_yaml("@.campo_exemplo")[0] is True


def test_sucesso_nao_prova_existencia_no_yaml():
    """Uma chave sintética inexistente é gramaticalmente válida."""
    assert analisar_caminho_yaml("bloco_inexistente_exemplo.campo_inexistente") == (
        False,
        (("bloco_inexistente_exemplo", None), ("campo_inexistente", None)),
    )


def test_a_fronteira_nao_resolve_seletor():
    """Zero, um ou muitos *matches* são assunto do resolver, não daqui."""
    assert analisar_caminho_yaml("colecao_exemplo[id=inexistente_exemplo]") == (
        False,
        (("colecao_exemplo", ("id", "inexistente_exemplo")),),
    )


def test_nenhum_teste_desta_suite_toca_o_corpus():
    """A suíte é sintética: nada aqui lê o corpus versionado.

    Os alvos da busca são montados por concatenação para que a própria asserção
    não os introduza no arquivo e invalide o teste.
    """
    fonte = Path(__file__).read_text(encoding="utf-8")
    assert ("respostas" + "-aprovadas") not in fonte
    assert ("casa77" + ".yaml") not in fonte
    assert ("open" + "(") not in fonte
