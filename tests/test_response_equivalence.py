"""Testes do comparador determinístico de equivalência textual de `C-15b`.

Todo o corpus é **sintético**: nenhuma frase de `knowledge/respostas-aprovadas.md`
é reproduzida, nenhum valor comercial aparece e **nada em `knowledge/**` é lido**.
Os caracteres de controle das fixtures são escritos por **escape** — `\\n`, `\\r`,
`\\t`, `\\u2028` — e nunca como quebra real dentro do literal, para que a prova de
terminação de linha não dependa de como o arquivo foi materializado no disco.

As garantias estruturais do módulo de produção — pureza de imports, ausência de
I/O e não menção a `knowledge/**` — são provadas sobre a **AST**, seguindo o
precedente de `test_response_index.py` e `test_response_index_load.py`.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from casa77_sdr.response_equivalence import (
    EquivalenciaNaoDeterminavel,
    sao_textualmente_equivalentes,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "response_equivalence.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

# Sentinela sintética: nunca deve vazar para a mensagem da exceção.
SENTINELA = "SENTINELA_NAO_DEVE_VAZAR"

# Todos os terminadores proibidos por D5, por escape.
TERMINADORES_PROIBIDOS = [
    "\r",
    "\r\n",
    "\u2028",   # LINE SEPARATOR
    "\u2029",   # PARAGRAPH SEPARATOR
    "\u0085",   # NEXT LINE
    "\u000b",   # LINE TABULATION
    "\u000c",   # FORM FEED
]


def categoria_de(erro: pytest.ExceptionInfo[EquivalenciaNaoDeterminavel]) -> str:
    return str(erro.value).split(":", 1)[0]


def onde_de(erro: pytest.ExceptionInfo[EquivalenciaNaoDeterminavel]) -> str:
    return str(erro.value).split(":", 1)[1].strip()


# 1. Tipo — erro de contrato de chamada, nunca NÃO DETERMINÁVEL


@pytest.mark.parametrize("valor", [None, 1, 1.0, True, b"x", ["x"], {"x": 1}, object()])
def test_aprovado_nao_str(valor: object) -> None:
    with pytest.raises(TypeError) as erro:
        sao_textualmente_equivalentes(valor, "x")  # type: ignore[arg-type]

    assert str(erro.value) == "aprovado: esperado str"


@pytest.mark.parametrize("valor", [None, 1, 1.0, True, b"x", ["x"], {"x": 1}, object()])
def test_renderizado_nao_str(valor: object) -> None:
    with pytest.raises(TypeError) as erro:
        sao_textualmente_equivalentes("x", valor)  # type: ignore[arg-type]

    assert str(erro.value) == "renderizado: esperado str"


def test_ambos_nao_str_aprovado_tem_precedencia() -> None:
    with pytest.raises(TypeError) as erro:
        sao_textualmente_equivalentes(None, None)  # type: ignore[arg-type]

    assert str(erro.value) == "aprovado: esperado str"


def test_tipo_invalido_nao_e_nao_determinavel() -> None:
    """Tipo errado é erro de chamada — não ausência de veredito."""
    with pytest.raises(TypeError) as erro:
        sao_textualmente_equivalentes(None, "x")  # type: ignore[arg-type]

    assert not isinstance(erro.value, EquivalenciaNaoDeterminavel)


def test_tipo_vence_erro_de_canonicidade() -> None:
    """`aprovado` não-str decide antes de o outro lado ser sequer olhado."""
    with pytest.raises(TypeError):
        sao_textualmente_equivalentes(None, "a\rb")  # type: ignore[arg-type]


def test_tipo_do_renderizado_vence_canonicidade_do_renderizado() -> None:
    with pytest.raises(TypeError) as erro:
        sao_textualmente_equivalentes("ok", 42)  # type: ignore[arg-type]

    assert str(erro.value) == "renderizado: esperado str"


@pytest.mark.parametrize("valor", [None, 12345, [SENTINELA]])
def test_mensagem_de_tipo_nao_ecoa_valor(valor: object) -> None:
    with pytest.raises(TypeError) as erro:
        sao_textualmente_equivalentes(valor, "x")  # type: ignore[arg-type]

    mensagem = str(erro.value)

    assert SENTINELA not in mensagem
    assert "12345" not in mensagem
    assert "None" not in mensagem


# 2. String vazia — permanece no domínio canônico


def test_vazio_com_vazio_e_equivalente() -> None:
    assert sao_textualmente_equivalentes("", "") is True


def test_vazio_com_nao_vazio_nao_e_equivalente() -> None:
    assert sao_textualmente_equivalentes("", "texto_exemplo") is False


def test_nao_vazio_com_vazio_nao_e_equivalente() -> None:
    assert sao_textualmente_equivalentes("texto_exemplo", "") is False


def test_vazio_nao_levanta_nao_determinavel() -> None:
    """A `str` vazia não viola D5 nem D7 — não há categoria para ela."""
    assert sao_textualmente_equivalentes("", "") is True


# 3. NFC


def test_composto_e_decomposto_sao_equivalentes() -> None:
    decomposto = "cafe\u0301"  # e + acento combinante
    composto = "café"

    assert sao_textualmente_equivalentes(decomposto, composto) is True


def test_normalizacao_aplicada_ao_lado_aprovado() -> None:
    assert sao_textualmente_equivalentes("a\u0301", "\u00e1") is True


def test_normalizacao_aplicada_ao_lado_renderizado() -> None:
    assert sao_textualmente_equivalentes("\u00e1", "a\u0301") is True


def test_diferenca_real_de_conteudo_nao_e_equivalente() -> None:
    assert sao_textualmente_equivalentes("café", "chá_exemplo") is False


def test_nfc_nao_e_compatibilidade() -> None:
    """`NFKC` uniria estes dois; `NFC` não — e o contrato é `NFC`."""
    assert sao_textualmente_equivalentes("\ufb01m", "fim") is False


# 4. Quebra suave


def test_quebra_suave_vira_um_espaco() -> None:
    assert sao_textualmente_equivalentes("a\nb", "a b") is True


def test_multiplos_lf_isolados() -> None:
    assert sao_textualmente_equivalentes("a\nb\nc\nd", "a b c d") is True


def test_quebra_suave_produz_exatamente_um_espaco() -> None:
    assert sao_textualmente_equivalentes("a\nb", "a  b") is False


def test_quebra_suave_nao_colapsa_espacos_vizinhos() -> None:
    """Só o `LF` vira espaço; espaços já existentes permanecem."""
    assert sao_textualmente_equivalentes("a\nb  c", "a b  c") is True


def test_espacos_comuns_nao_sao_colapsados() -> None:
    assert sao_textualmente_equivalentes("a  b", "a b") is False


def test_quebra_suave_dos_dois_lados() -> None:
    assert sao_textualmente_equivalentes("a\nb", "a\nb") is True


# 5. Parágrafo real


def test_paragrafo_preservado() -> None:
    assert sao_textualmente_equivalentes("a\n\nb", "a\n\nb") is True


def test_paragrafo_nao_vira_espaco() -> None:
    assert sao_textualmente_equivalentes("a\n\nb", "a b") is False


def test_paragrafo_nao_e_quebra_suave() -> None:
    assert sao_textualmente_equivalentes("a\n\nb", "a\nb") is False


def test_paragrafo_com_quebra_suave_interna() -> None:
    assert sao_textualmente_equivalentes("a\nb\n\nc\nd", "a b\n\nc d") is True


def test_paragrafo_nao_equivale_a_dois_espacos() -> None:
    """A fronteira de parágrafo sobrevive à normalização como `\\n\\n`.

    Ela não vira espaço algum — nem um, nem dois —, então nenhum texto feito de
    espaços pode casar com ela.
    """
    assert sao_textualmente_equivalentes("a\n\nb", "a  b") is False


@pytest.mark.parametrize("quantidade", [3, 4, 5])
def test_sequencia_excessiva_de_quebras_e_nao_determinavel(
    quantidade: int,
) -> None:
    texto = "a" + "\n" * quantidade + "b"

    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes(texto, "a b")

    assert categoria_de(erro) == "sequencia_de_quebras_excessiva"
    assert onde_de(erro) == "aprovado"


@pytest.mark.parametrize("quantidade", [3, 4, 5])
def test_sequencia_excessiva_no_renderizado(quantidade: int) -> None:
    texto = "a" + "\n" * quantidade + "b"

    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a b", texto)

    assert categoria_de(erro) == "sequencia_de_quebras_excessiva"
    assert onde_de(erro) == "renderizado"


# 6. Terminadores proibidos


@pytest.mark.parametrize("terminador", TERMINADORES_PROIBIDOS)
def test_terminador_proibido_no_aprovado(terminador: str) -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes(f"a{terminador}b", "a b")

    assert categoria_de(erro) == "terminador_proibido"
    assert onde_de(erro) == "aprovado"


@pytest.mark.parametrize("terminador", TERMINADORES_PROIBIDOS)
def test_terminador_proibido_no_renderizado(terminador: str) -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a b", f"a{terminador}b")

    assert categoria_de(erro) == "terminador_proibido"
    assert onde_de(erro) == "renderizado"


def test_crlf_e_recusado_e_nunca_convertido() -> None:
    """`CRLF` não vira `LF`: ele é recusado, como manda D5."""
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\r\nb", "a b")

    assert categoria_de(erro) == "terminador_proibido"


def test_cr_isolado_e_recusado() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\rb", "a b")

    assert categoria_de(erro) == "terminador_proibido"


def test_terminador_proibido_vence_outras_violacoes() -> None:
    """Ordem de D7: terminador antes de borda, sequência e branco."""
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("\na \n\n\n\rb\n", "ok")

    assert categoria_de(erro) == "terminador_proibido"


# 7. Quebra na borda


def test_quebra_na_borda_inicial() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("\na", "a")

    assert categoria_de(erro) == "quebra_na_borda"
    assert onde_de(erro) == "aprovado.inicio"


def test_quebra_na_borda_final() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\n", "a")

    assert categoria_de(erro) == "quebra_na_borda"
    assert onde_de(erro) == "aprovado.fim"


def test_quebra_nas_duas_bordas_inicio_vence() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("\na\n", "a")

    assert onde_de(erro) == "aprovado.inicio"


def test_quebra_na_borda_no_renderizado() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a", "\na")

    assert categoria_de(erro) == "quebra_na_borda"
    assert onde_de(erro) == "renderizado.inicio"


def test_texto_de_uma_unica_quebra() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("\n", "")

    assert onde_de(erro) == "aprovado.inicio"


def test_borda_vence_sequencia_e_branco() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("\na \n\n\nb", "ok")

    assert categoria_de(erro) == "quebra_na_borda"


# 8. Branco adjacente à quebra


def test_espaco_antes_da_quebra() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a \nb", "a b")

    assert categoria_de(erro) == "branco_adjacente_a_quebra"
    assert onde_de(erro) == "aprovado.antes"


def test_tab_antes_da_quebra() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\t\nb", "a b")

    assert categoria_de(erro) == "branco_adjacente_a_quebra"
    assert onde_de(erro) == "aprovado.antes"


def test_espaco_depois_da_quebra() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\n b", "a b")

    assert categoria_de(erro) == "branco_adjacente_a_quebra"
    assert onde_de(erro) == "aprovado.depois"


def test_tab_depois_da_quebra() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\n\tb", "a b")

    assert categoria_de(erro) == "branco_adjacente_a_quebra"
    assert onde_de(erro) == "aprovado.depois"


def test_branco_antes_vence_branco_depois() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a \n b", "a b")

    assert onde_de(erro) == "aprovado.antes"


def test_branco_adjacente_no_renderizado() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a b", "a\n b")

    assert categoria_de(erro) == "branco_adjacente_a_quebra"
    assert onde_de(erro) == "renderizado.depois"


def test_sequencia_vence_branco_adjacente() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a \n\n\nb", "ok")

    assert categoria_de(erro) == "sequencia_de_quebras_excessiva"


# 9. Precedência entre lados


def test_aprovado_vence_quando_ambos_sao_nao_canonicos() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\rb", "c\rd")

    assert onde_de(erro) == "aprovado"


def test_aprovado_vence_mesmo_com_categoria_diferente_no_outro_lado() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("\na", "b\rc")

    assert categoria_de(erro) == "quebra_na_borda"
    assert onde_de(erro) == "aprovado.inicio"


def test_renderizado_so_e_avaliado_com_aprovado_canonico() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a b", "c\rd")

    assert onde_de(erro) == "renderizado"


# 10. Preservações — nada de tolerância aproximada


def test_caixa_e_preservada() -> None:
    assert sao_textualmente_equivalentes("Texto_Exemplo", "texto_exemplo") is False


def test_ausencia_de_casefold() -> None:
    assert sao_textualmente_equivalentes("STRASSE_EXEMPLO", "strasse_exemplo") is False


def test_pontuacao_e_preservada() -> None:
    assert sao_textualmente_equivalentes("a, b.", "a b") is False


def test_ordem_e_preservada() -> None:
    assert sao_textualmente_equivalentes("alfa beta", "beta alfa") is False


def test_conteudo_e_preservado() -> None:
    assert sao_textualmente_equivalentes("alfa", "alfa_extra") is False


def test_ausencia_de_strip_nas_bordas() -> None:
    """Branco de borda **sem** `LF` é canônico e continua contando."""
    assert sao_textualmente_equivalentes(" alfa ", "alfa") is False


def test_ausencia_de_strip_com_tab_na_borda() -> None:
    assert sao_textualmente_equivalentes("\talfa", "alfa") is False


def test_ausencia_de_tolerancia_aproximada() -> None:
    assert sao_textualmente_equivalentes("alfa beta", "alfa  beta") is False


def test_ausencia_de_remocao_de_pontuacao() -> None:
    assert sao_textualmente_equivalentes("alfa.", "alfa") is False


def test_identidade_exata_e_equivalente() -> None:
    assert sao_textualmente_equivalentes("alfa beta", "alfa beta") is True


# 11. Segurança da mensagem


@pytest.mark.parametrize(
    "aprovado",
    [
        SENTINELA + "\r" + SENTINELA,
        "\n" + SENTINELA,
        SENTINELA + "\n",
        SENTINELA + "\n\n\n" + SENTINELA,
        SENTINELA + " \n" + SENTINELA,
        SENTINELA + "\n " + SENTINELA,
    ],
)
def test_mensagem_nao_ecoa_conteudo(aprovado: str) -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes(aprovado, "ok")

    assert SENTINELA not in str(erro.value)


@pytest.mark.parametrize("terminador", TERMINADORES_PROIBIDOS)
def test_mensagem_nao_ecoa_caractere_ofensor(terminador: str) -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes(f"a{terminador}b", "a b")

    mensagem = str(erro.value)

    for caractere in terminador:
        assert caractere not in mensagem
    assert "\\u" not in mensagem
    assert "\\r" not in mensagem


def test_mensagem_nao_tem_offset_indice_nem_comprimento() -> None:
    aprovado = SENTINELA * 3 + "\r" + SENTINELA * 3

    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes(aprovado, "ok")

    mensagem = str(erro.value)

    assert not any(caractere.isdigit() for caractere in mensagem)
    assert str(len(aprovado)) not in mensagem


def test_mensagem_tem_apenas_categoria_e_lado() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\rb", "ok")

    assert str(erro.value) == "terminador_proibido: aprovado"


def test_mensagem_com_localizador_tem_forma_fechada() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("\na", "ok")

    assert str(erro.value) == "quebra_na_borda: aprovado.inicio"


def test_excecao_sem_cause() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\rb", "ok")

    assert erro.value.__cause__ is None


def test_excecao_sem_contexto_encadeado() -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\rb", "ok")

    assert erro.value.__context__ is None


# 12. Categorias e lados — cobertura cruzada


@pytest.mark.parametrize(
    ("texto", "categoria", "onde_sufixo"),
    [
        ("a\rb", "terminador_proibido", ""),
        ("\nab", "quebra_na_borda", ".inicio"),
        ("ab\n", "quebra_na_borda", ".fim"),
        ("a\n\n\nb", "sequencia_de_quebras_excessiva", ""),
        ("a \nb", "branco_adjacente_a_quebra", ".antes"),
        ("a\n b", "branco_adjacente_a_quebra", ".depois"),
    ],
)
def test_cada_categoria_no_lado_aprovado(
    texto: str, categoria: str, onde_sufixo: str
) -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes(texto, "ok")

    assert categoria_de(erro) == categoria
    assert onde_de(erro) == "aprovado" + onde_sufixo


@pytest.mark.parametrize(
    ("texto", "categoria", "onde_sufixo"),
    [
        ("a\rb", "terminador_proibido", ""),
        ("\nab", "quebra_na_borda", ".inicio"),
        ("ab\n", "quebra_na_borda", ".fim"),
        ("a\n\n\nb", "sequencia_de_quebras_excessiva", ""),
        ("a \nb", "branco_adjacente_a_quebra", ".antes"),
        ("a\n b", "branco_adjacente_a_quebra", ".depois"),
    ],
)
def test_cada_categoria_no_lado_renderizado(
    texto: str, categoria: str, onde_sufixo: str
) -> None:
    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("ok", texto)

    assert categoria_de(erro) == categoria
    assert onde_de(erro) == "renderizado" + onde_sufixo


def test_vocabulario_de_categorias_e_fechado() -> None:
    categorias = {
        "terminador_proibido",
        "quebra_na_borda",
        "sequencia_de_quebras_excessiva",
        "branco_adjacente_a_quebra",
    }
    observadas = set()

    for texto in ("a\rb", "\nab", "a\n\n\nb", "a \nb"):
        with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
            sao_textualmente_equivalentes(texto, "ok")
        observadas.add(categoria_de(erro))

    assert observadas == categorias


def test_vocabulario_de_lados_e_fechado() -> None:
    lados = set()

    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("a\rb", "ok")
    lados.add(onde_de(erro))

    with pytest.raises(EquivalenciaNaoDeterminavel) as erro:
        sao_textualmente_equivalentes("ok", "a\rb")
    lados.add(onde_de(erro))

    assert lados == {"aprovado", "renderizado"}


# 13. Contrato de API


def test_api_publica_e_fechada() -> None:
    from casa77_sdr import response_equivalence

    assert response_equivalence.__all__ == [
        "EquivalenciaNaoDeterminavel",
        "sao_textualmente_equivalentes",
    ]


def test_assinatura_tem_dois_parametros_sem_default() -> None:
    parametros = list(inspect.signature(sao_textualmente_equivalentes).parameters.values())

    assert [p.name for p in parametros] == ["aprovado", "renderizado"]
    for parametro in parametros:
        assert parametro.default is inspect.Parameter.empty


def test_retorno_e_bool_estrito() -> None:
    assert type(sao_textualmente_equivalentes("a", "a")) is bool
    assert type(sao_textualmente_equivalentes("a", "b")) is bool


def test_excecao_deriva_diretamente_de_exception() -> None:
    assert EquivalenciaNaoDeterminavel.__bases__ == (Exception,)


def test_excecao_nao_deriva_de_valueerror() -> None:
    assert not issubclass(EquivalenciaNaoDeterminavel, ValueError)


def test_excecao_nao_se_confunde_com_as_de_indice() -> None:
    from casa77_sdr.response_index import IndiceInvalido
    from casa77_sdr.response_index_load import IndiceIlegivel

    assert not issubclass(EquivalenciaNaoDeterminavel, IndiceInvalido)
    assert not issubclass(EquivalenciaNaoDeterminavel, IndiceIlegivel)
    assert not issubclass(IndiceInvalido, EquivalenciaNaoDeterminavel)


# 14. Pureza estrutural, por AST


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


def test_imports_de_producao_sao_apenas_future_e_unicodedata() -> None:
    assert modulos_importados() == {"__future__", "unicodedata"}


@pytest.mark.parametrize(
    "proibido",
    [
        "yaml",
        "pathlib",
        "os",
        "re",
        "json",
        "sys",
        "io",
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_load",
        "casa77_sdr.knowledge",
    ],
)
def test_modulo_nao_importa_proibido(proibido: str) -> None:
    assert proibido not in modulos_importados()


def test_modulo_nao_depende_do_pacote() -> None:
    """Pureza: o comparador não conhece índice, carregador nem base."""
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
        "iterdir",
        "environ",
        "getenv",
        "system",
        "run",
        "urlopen",
        "request",
        "connect",
        "socket",
    }

    assert usados & proibidos == set()


@pytest.mark.parametrize(
    "termo",
    [
        "knowledge",
        "casa77.yaml",
        "respostas-aprovadas.md",
        "indice-respostas-aprovadas.yaml",
    ],
)
def test_modulo_nao_menciona_fonte_comercial(termo: str) -> None:
    assert termo not in MODULO.read_text(encoding="utf-8")


def test_modulo_nao_declara_enum_nem_dataclass() -> None:
    codigo = MODULO.read_text(encoding="utf-8")

    assert "Enum" not in codigo
    assert "dataclass" not in codigo


def test_modulo_tem_uma_unica_classe_publica() -> None:
    classes = [
        no.name
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.ClassDef)
    ]

    assert classes == ["EquivalenciaNaoDeterminavel"]


def test_modulo_nao_tem_funcao_publica_alem_da_fronteira() -> None:
    publicas = [
        no.name
        for no in ast.walk(arvore_do_modulo())
        if isinstance(no, ast.FunctionDef) and not no.name.startswith("_")
    ]

    assert publicas == ["sao_textualmente_equivalentes"]


def test_modulo_usa_nfc_e_nao_compatibilidade() -> None:
    codigo = MODULO.read_text(encoding="utf-8")

    assert '"NFC"' in codigo
    for forma in ("NFKC", "NFKD", "NFD"):
        assert f'"{forma}"' not in codigo


def test_modulo_nao_substitui_quebra_globalmente() -> None:
    """A dobra é por parágrafo; `replace` global destruiria D4."""
    codigo = MODULO.read_text(encoding="utf-8")

    assert 'texto.replace("\\n", " ")' not in codigo
    assert 'composto.replace("\\n", " ")' not in codigo


def test_init_nao_referencia_o_comparador() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "response_equivalence" not in codigo
    assert "sao_textualmente_equivalentes" not in codigo
    assert "EquivalenciaNaoDeterminavel" not in codigo
