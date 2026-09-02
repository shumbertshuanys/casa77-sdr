"""Testes do verificador de correspondência bijetiva de `C-A1-B3`/`C-A1-B4`.

A fronteira julga **apenas** a relação entre os domínios recebidos. Estes testes
provam o julgamento, a ordem fixa de validação, a opacidade dos tokens, a
ausência de normalização, o silêncio da mensagem de erro, a pureza do módulo de
produção e a imutabilidade das entradas — e **não** provam completude de índice
real, extração de Markdown, bijeção física do corpus ou satisfação de
`C-A1-ST7`, que estão fora desta fronteira.
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Sequence
from pathlib import Path

import pytest

import casa77_sdr
from casa77_sdr.response_bijection import BijecaoInvalida, validar_bijecao

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

# Tokens sinteticos e opacos. Nenhum deles carrega formato, gramatica ou
# significado: sao apenas cadeias distintas.
FRAG_A = "fragmento-alfa"
FRAG_B = "fragmento-beta"
FRAG_C = "fragmento-gama"
UNID_A = "unidade-alfa"
UNID_B = "unidade-beta"
UNID_C = "unidade-gama"

FLUTUANTE = len("alfa") / len("beta gama")


class TokenPermissivo(str):
    """Subclasse sintetica de `str` que sequestra a identidade do token.

    Ela existe SOMENTE neste teste. Redefine `__eq__` e `__hash__` para que
    conteudos diferentes se comportem como iguais, demonstrando por que a
    fronteira nao pode aceitar subclasses de `str`: a decisao sobre quando dois
    tokens sao o mesmo token passaria a ser do chamador.
    """

    def __eq__(self, outro: object) -> bool:
        return isinstance(outro, str)

    def __hash__(self) -> int:
        return len("")


TOKEN_FANTASMA = "token-fantasma"


class ParInstavel(tuple):
    """Subclasse sintetica de `tuple` que mente sobre a propria forma.

    Ela existe SOMENTE neste teste. Redefine `__len__` e `__getitem__` para
    demonstrar por que a fronteira nao pode aceitar subclasses de `tuple`: o
    conteudo real do objeto e um, a forma anunciada e outra, e o valor lido em
    cada indice nao vem do conteudo. A representacao verificada numa etapa nao
    seria a mesma usada na etapa seguinte, e o julgamento deixaria de ser
    deterministico.
    """

    def __len__(self) -> int:
        return len(("origem", "destino"))

    def __getitem__(self, indice: object) -> object:
        return TOKEN_FANTASMA


CATEGORIAS = (
    "tipo_invalido",
    "estrutura_invalida",
    "duplicidade",
    "referencia_desconhecida",
    "cobertura_incompleta",
)

LOCALIZADORES = (
    "fragmentos_indice",
    "unidades_markdown",
    "correspondencias",
    "correspondencias.item",
    "correspondencias.origem",
    "correspondencias.destino",
)

CAMINHO_PRODUCAO = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "casa77_sdr"
    / "response_bijection.py"
)

CODIGO_PRODUCAO = CAMINHO_PRODUCAO.read_text(encoding="utf-8")
ARVORE_PRODUCAO = ast.parse(CODIGO_PRODUCAO)


def mensagem(excecao: pytest.ExceptionInfo[BijecaoInvalida]) -> str:
    return str(excecao.value)


def partes(texto: str) -> tuple[str, str]:
    categoria, _, localizador = texto.partition(": ")
    return categoria, localizador


def identificadores_do_codigo() -> set[str]:
    """Nomes e atributos que aparecem no codigo de producao, sem docstrings."""
    encontrados: set[str] = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Name):
            encontrados.add(no.id)
        elif isinstance(no, ast.Attribute):
            encontrados.add(no.attr)
        elif isinstance(no, ast.FunctionDef):
            encontrados.add(no.name)
    return encontrados


def literais_numericos() -> set[object]:
    return {
        no.value
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.Constant) and isinstance(no.value, int)
    }


def modulos_importados() -> set[str]:
    encontrados: set[str] = set()
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Import):
            for alias in no.names:
                encontrados.add(alias.name)
        elif isinstance(no, ast.ImportFrom):
            encontrados.add(no.module or "")
    return encontrados


# ---------------------------------------------------------------------------
# Casos validos
# ---------------------------------------------------------------------------


def test_dominios_vazios_sao_bijecao_trivial():
    assert validar_bijecao([], [], []) is None


def test_dominios_vazios_em_tuplas_sao_bijecao_trivial():
    assert validar_bijecao((), (), ()) is None


def test_cardinalidade_unitaria_e_valida():
    assert validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A, UNID_A)]) is None


def test_cardinalidade_plural_e_valida():
    assert (
        validar_bijecao(
            [FRAG_A, FRAG_B, FRAG_C],
            [UNID_A, UNID_B, UNID_C],
            [(FRAG_A, UNID_A), (FRAG_B, UNID_B), (FRAG_C, UNID_C)],
        )
        is None
    )


def test_tokens_dos_dois_dominios_podem_ser_totalmente_diferentes():
    assert (
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(FRAG_A, UNID_B), (FRAG_B, UNID_A)],
        )
        is None
    )


def test_tokens_dos_dois_dominios_podem_coincidir():
    """O modulo nao exige que os dominios sejam disjuntos nem que coincidam."""
    assert (
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [FRAG_A, FRAG_B],
            [(FRAG_A, FRAG_B), (FRAG_B, FRAG_A)],
        )
        is None
    )


def test_ordem_dos_pares_nao_altera_o_resultado():
    fragmentos = [FRAG_A, FRAG_B, FRAG_C]
    unidades = [UNID_A, UNID_B, UNID_C]
    direta = [(FRAG_A, UNID_A), (FRAG_B, UNID_B), (FRAG_C, UNID_C)]
    invertida = list(reversed(direta))
    assert validar_bijecao(fragmentos, unidades, direta) is None
    assert validar_bijecao(fragmentos, unidades, invertida) is None


def test_ordem_dos_dominios_nao_altera_o_resultado():
    pares = [(FRAG_A, UNID_A), (FRAG_B, UNID_B)]
    assert validar_bijecao([FRAG_A, FRAG_B], [UNID_A, UNID_B], pares) is None
    assert validar_bijecao([FRAG_B, FRAG_A], [UNID_B, UNID_A], pares) is None


def test_resultado_e_deterministico_sob_repeticao():
    fragmentos = [FRAG_A, FRAG_B]
    unidades = [UNID_A, UNID_B]
    pares = [(FRAG_A, UNID_B), (FRAG_B, UNID_A)]
    resultados = [
        validar_bijecao(fragmentos, unidades, pares) for _ in CATEGORIAS
    ]
    assert all(resultado is None for resultado in resultados)


def test_falha_e_deterministica_sob_repeticao():
    mensagens = set()
    for _ in CATEGORIAS:
        with pytest.raises(BijecaoInvalida) as erro:
            validar_bijecao([FRAG_A], [UNID_A], [])
        mensagens.add(mensagem(erro))
    assert len(mensagens) == 1


def test_a_subclasse_de_tuple_realmente_mente_sobre_a_forma():
    """Sem a validacao estrita, este objeto passaria pela conferencia de forma
    e entregaria depois valores que nao estao no seu conteudo."""
    instavel = ParInstavel(())
    assert isinstance(instavel, tuple)
    assert type(instavel) is not tuple
    assert len(instavel) == len(("origem", "destino"))
    assert tuple.__len__(instavel) != len(instavel)
    assert instavel[0] == TOKEN_FANTASMA
    assert instavel[1] == TOKEN_FANTASMA


def test_subclasse_de_tuple_e_recusada_como_item():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A], [UNID_A], [ParInstavel((FRAG_A, UNID_A))]
        )
    assert mensagem(erro) == "tipo_invalido: correspondencias.item"


def test_subclasse_de_tuple_vazia_tambem_e_recusada_antes_da_forma():
    """A recusa acontece na etapa do tipo, antes de qualquer leitura de forma."""
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [ParInstavel(())])
    assert mensagem(erro) == "tipo_invalido: correspondencias.item"


def test_par_precisa_ser_tuple_e_lista_e_recusada():
    """O contrato publico do item e tuple[str, str]: uma lista de dois
    elementos nao e um par valido, mesmo com a forma correta."""
    assert validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A, UNID_A)]) is None
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [[FRAG_A, UNID_A]])
    assert mensagem(erro) == "tipo_invalido: correspondencias.item"


def test_dominios_podem_chegar_como_tuplas():
    assert validar_bijecao((FRAG_A,), (UNID_A,), ((FRAG_A, UNID_A),)) is None


def test_token_vazio_e_apenas_um_token():
    """O conteudo do token nao e interpretado: a cadeia vazia e valida."""
    assert validar_bijecao([""], [""], [("", "")]) is None


def test_tokens_com_conteudo_arbitrario_sao_aceitos():
    exoticos = [" ", "\n", "\t", "R\u00e9sultat", "\U0001f600", "a b c"]
    pares = [(token, token) for token in exoticos]
    assert validar_bijecao(exoticos, exoticos, pares) is None


def test_token_nao_precisa_de_formato_rxx():
    aleatorios = ["7", "-", "::", "{}", "x" * len(CATEGORIAS)]
    pares = [(token, token) for token in aleatorios]
    assert validar_bijecao(aleatorios, aleatorios, pares) is None


# ---------------------------------------------------------------------------
# str exata / recusa de subclasse
# ---------------------------------------------------------------------------


def test_a_subclasse_sintetica_realmente_sequestra_a_igualdade():
    """Sem a validacao estrita, esta subclasse faria conteudos diferentes
    parecerem o mesmo token."""
    permissivo = TokenPermissivo(FRAG_A)
    assert permissivo == FRAG_B
    assert permissivo == UNID_A
    assert hash(permissivo) == hash(TokenPermissivo(FRAG_C))
    assert isinstance(permissivo, str)
    assert type(permissivo) is not str


def test_subclasse_de_str_e_recusada_em_fragmentos_indice():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([TokenPermissivo(FRAG_A)], [UNID_A], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


def test_subclasse_de_str_e_recusada_em_unidades_markdown():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [TokenPermissivo(UNID_A)], [])
    assert mensagem(erro) == "tipo_invalido: unidades_markdown"


def test_subclasse_de_str_e_recusada_na_origem():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A], [UNID_A], [(TokenPermissivo(FRAG_A), UNID_A)]
        )
    assert mensagem(erro) == "tipo_invalido: correspondencias.origem"


def test_subclasse_de_str_e_recusada_no_destino():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A], [UNID_A], [(FRAG_A, TokenPermissivo(UNID_A))]
        )
    assert mensagem(erro) == "tipo_invalido: correspondencias.destino"


def test_str_normal_continua_aceita_nos_quatro_lugares():
    assert validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A, UNID_A)]) is None


# ---------------------------------------------------------------------------
# Igualdade exata de str / ausencia de normalizacao
# ---------------------------------------------------------------------------


def test_tokens_equivalentes_por_nfc_e_nfd_sao_tokens_distintos():
    composto = "\u00e9"
    decomposto = "e\u0301"
    assert composto != decomposto
    assert (
        validar_bijecao(
            [composto, decomposto],
            [composto, decomposto],
            [(composto, composto), (decomposto, decomposto)],
        )
        is None
    )


def test_diferenca_de_caixa_nao_e_tolerada():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A.upper(), UNID_A)])
    assert mensagem(erro) == "referencia_desconhecida: correspondencias.origem"


def test_espaco_nas_bordas_nao_e_removido():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(f" {FRAG_A} ", UNID_A)])
    assert mensagem(erro) == "referencia_desconhecida: correspondencias.origem"


def test_igualdade_de_conteudo_basta_mesmo_sem_identidade_de_objeto():
    copia = "".join(list(FRAG_A))
    assert copia is not FRAG_A
    assert validar_bijecao([FRAG_A], [UNID_A], [(copia, UNID_A)]) is None


# ---------------------------------------------------------------------------
# Tipos de topo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalido",
    [None, True, len(CATEGORIAS), FLUTUANTE, {FRAG_A}, {FRAG_A: UNID_A}, object()],
)
def test_fragmentos_indice_precisa_ser_sequencia(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(invalido, [], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


@pytest.mark.parametrize(
    "invalido",
    [None, True, len(CATEGORIAS), FLUTUANTE, {UNID_A}, {UNID_A: FRAG_A}, object()],
)
def test_unidades_markdown_precisa_ser_sequencia(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], invalido, [])
    assert mensagem(erro) == "tipo_invalido: unidades_markdown"


@pytest.mark.parametrize(
    "invalido",
    [None, True, len(CATEGORIAS), FLUTUANTE, {FRAG_A}, {FRAG_A: UNID_A}, object()],
)
def test_correspondencias_precisa_ser_sequencia(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], [], invalido)
    assert mensagem(erro) == "tipo_invalido: correspondencias"


def test_mapping_nao_e_aceito_como_relacao():
    """A relacao chega como pares explicitos, nunca como mapa."""
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], {FRAG_A: UNID_A})
    assert mensagem(erro) == "tipo_invalido: correspondencias"


def test_gerador_nao_e_sequencia():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao((token for token in [FRAG_A]), [], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


@pytest.mark.parametrize("localizador", ["fragmentos_indice"])
def test_str_nao_e_contentor_de_fragmentos(localizador):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(FRAG_A, [], [])
    assert mensagem(erro) == f"tipo_invalido: {localizador}"


def test_str_nao_e_contentor_de_unidades():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], UNID_A, [])
    assert mensagem(erro) == "tipo_invalido: unidades_markdown"


def test_str_nao_e_contentor_de_correspondencias():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], [], FRAG_A)
    assert mensagem(erro) == "tipo_invalido: correspondencias"


def test_str_vazia_tambem_e_recusada_como_contentor():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao("", [], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


@pytest.mark.parametrize("invalido", [b"alfa", bytearray(b"alfa")])
def test_bytes_nao_sao_contentor_de_fragmentos(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(invalido, [], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


@pytest.mark.parametrize("invalido", [b"alfa", bytearray(b"alfa")])
def test_bytes_nao_sao_contentor_de_unidades(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], invalido, [])
    assert mensagem(erro) == "tipo_invalido: unidades_markdown"


@pytest.mark.parametrize("invalido", [b"alfa", bytearray(b"alfa")])
def test_bytes_nao_sao_contentor_de_correspondencias(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], [], invalido)
    assert mensagem(erro) == "tipo_invalido: correspondencias"


# ---------------------------------------------------------------------------
# Tipos dos tokens
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalido", [None, True, len(CATEGORIAS), FLUTUANTE, b"alfa", (), object()]
)
def test_token_de_fragmento_precisa_ser_str(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([invalido], [], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


@pytest.mark.parametrize(
    "invalido", [None, True, len(CATEGORIAS), FLUTUANTE, b"alfa", (), object()]
)
def test_token_de_unidade_precisa_ser_str(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], [invalido], [])
    assert mensagem(erro) == "tipo_invalido: unidades_markdown"


def test_token_invalido_no_fim_do_dominio_tambem_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A, None], [], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


# ---------------------------------------------------------------------------
# Estrutura dos pares
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalido", [None, True, len(CATEGORIAS), FLUTUANTE, {FRAG_A}, object()]
)
def test_par_precisa_ser_sequencia(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [invalido])
    assert mensagem(erro) == "tipo_invalido: correspondencias.item"


@pytest.mark.parametrize("invalido", ["ab", b"ab", bytearray(b"ab")])
def test_par_nao_pode_ser_str_nem_bytes(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [invalido])
    assert mensagem(erro) == "tipo_invalido: correspondencias.item"


def test_par_com_um_unico_lado_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A,)])
    assert mensagem(erro) == "estrutura_invalida: correspondencias.item"


def test_par_vazio_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [()])
    assert mensagem(erro) == "estrutura_invalida: correspondencias.item"


def test_par_com_lado_extra_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A, UNID_A, FRAG_A)])
    assert mensagem(erro) == "estrutura_invalida: correspondencias.item"


@pytest.mark.parametrize(
    "invalido", [None, True, len(CATEGORIAS), FLUTUANTE, b"alfa", (), object()]
)
def test_origem_precisa_ser_str(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(invalido, UNID_A)])
    assert mensagem(erro) == "tipo_invalido: correspondencias.origem"


@pytest.mark.parametrize(
    "invalido", [None, True, len(CATEGORIAS), FLUTUANTE, b"alfa", (), object()]
)
def test_destino_precisa_ser_str(invalido):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A, invalido)])
    assert mensagem(erro) == "tipo_invalido: correspondencias.destino"


def test_origem_precede_destino_no_mesmo_par():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(None, None)])
    assert mensagem(erro) == "tipo_invalido: correspondencias.origem"


def test_lados_sao_conferidos_par_a_par_na_ordem_recebida():
    """A conferencia dos lados e por par: o destino do primeiro par vem antes
    da origem do segundo."""
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(FRAG_A, None), (None, UNID_B)],
        )
    assert mensagem(erro) == "tipo_invalido: correspondencias.destino"


# ---------------------------------------------------------------------------
# Duplicidades
# ---------------------------------------------------------------------------


def test_fragmento_duplicado_no_dominio_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_A], [UNID_A, UNID_B], [(FRAG_A, UNID_A)]
        )
    assert mensagem(erro) == "duplicidade: fragmentos_indice"


def test_unidade_duplicada_no_dominio_e_recusada():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B], [UNID_A, UNID_A], [(FRAG_A, UNID_A)]
        )
    assert mensagem(erro) == "duplicidade: unidades_markdown"


def test_origem_repetida_na_relacao_e_recusada():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(FRAG_A, UNID_A), (FRAG_A, UNID_B)],
        )
    assert mensagem(erro) == "duplicidade: correspondencias.origem"


def test_destino_repetido_na_relacao_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(FRAG_A, UNID_A), (FRAG_B, UNID_A)],
        )
    assert mensagem(erro) == "duplicidade: correspondencias.destino"


def test_par_identico_repetido_e_recusado_pela_origem():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A], [UNID_A], [(FRAG_A, UNID_A), (FRAG_A, UNID_A)]
        )
    assert mensagem(erro) == "duplicidade: correspondencias.origem"


def test_duplicidade_de_dominio_precede_duplicidade_de_relacao():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_A],
            [UNID_A],
            [(FRAG_A, UNID_A), (FRAG_A, UNID_A)],
        )
    assert mensagem(erro) == "duplicidade: fragmentos_indice"


def test_duplicidade_de_fragmento_precede_duplicidade_de_unidade():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A, FRAG_A], [UNID_A, UNID_A], [])
    assert mensagem(erro) == "duplicidade: fragmentos_indice"


def test_duplicidade_de_origem_precede_duplicidade_de_destino():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(FRAG_A, UNID_A), (FRAG_A, UNID_A)],
        )
    assert mensagem(erro) == "duplicidade: correspondencias.origem"


# ---------------------------------------------------------------------------
# Referencias
# ---------------------------------------------------------------------------


def test_origem_desconhecida_e_recusada():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(FRAG_B, UNID_A)])
    assert mensagem(erro) == "referencia_desconhecida: correspondencias.origem"


def test_destino_desconhecido_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(FRAG_A, UNID_B)])
    assert mensagem(erro) == "referencia_desconhecida: correspondencias.destino"


def test_relacao_sobre_dominios_vazios_e_recusada():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], [], [(FRAG_A, UNID_A)])
    assert mensagem(erro) == "referencia_desconhecida: correspondencias.origem"


def test_origem_desconhecida_precede_destino_desconhecido():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [(FRAG_B, UNID_B)])
    assert mensagem(erro) == "referencia_desconhecida: correspondencias.origem"


def test_duplicidade_precede_referencia_desconhecida():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A],
            [UNID_A, UNID_B],
            [(FRAG_B, UNID_A), (FRAG_B, UNID_B)],
        )
    assert mensagem(erro) == "duplicidade: correspondencias.origem"


# ---------------------------------------------------------------------------
# Cobertura
# ---------------------------------------------------------------------------


def test_fragmento_sem_par_e_recusado():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B], [UNID_A, UNID_B], [(FRAG_A, UNID_A)]
        )
    assert mensagem(erro) == "cobertura_incompleta: fragmentos_indice"


def test_unidade_sem_par_e_recusada():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A, UNID_B], [(FRAG_A, UNID_A)])
    assert mensagem(erro) == "cobertura_incompleta: unidades_markdown"


def test_relacao_vazia_sobre_dominios_nao_vazios_e_recusada():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A], [UNID_A], [])
    assert mensagem(erro) == "cobertura_incompleta: fragmentos_indice"


def test_cobertura_de_fragmentos_precede_cobertura_de_unidades():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A, FRAG_B], [UNID_A, UNID_B], [])
    assert mensagem(erro) == "cobertura_incompleta: fragmentos_indice"


def test_referencia_desconhecida_precede_cobertura_incompleta():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A, FRAG_B], [UNID_A], [(FRAG_C, UNID_A)])
    assert mensagem(erro) == "referencia_desconhecida: correspondencias.origem"


# ---------------------------------------------------------------------------
# Precedencia global
# ---------------------------------------------------------------------------


def test_tipo_de_fragmentos_precede_tipo_de_unidades():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(None, None, None)
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


def test_tipo_de_unidades_precede_tipo_de_correspondencias():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([], None, None)
    assert mensagem(erro) == "tipo_invalido: unidades_markdown"


def test_tipo_de_topo_precede_tipo_de_token():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(None, [None], [None])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


def test_tipo_de_token_de_fragmento_precede_tipo_de_token_de_unidade():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([None], [None], [])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


def test_tipo_de_token_precede_estrutura_do_par():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([None], [UNID_A], [(FRAG_A,)])
    assert mensagem(erro) == "tipo_invalido: fragmentos_indice"


def test_estrutura_do_par_precede_tipo_dos_lados():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(None, UNID_A), (FRAG_B,)],
        )
    assert mensagem(erro) == "estrutura_invalida: correspondencias.item"


def test_tipo_do_item_precede_estrutura_do_item():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(FRAG_A,), None],
        )
    assert mensagem(erro) == "tipo_invalido: correspondencias.item"


def test_tipo_dos_lados_precede_duplicidade_de_dominio():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A, FRAG_A], [UNID_A], [(None, UNID_A)])
    assert mensagem(erro) == "tipo_invalido: correspondencias.origem"


def test_duplicidade_de_dominio_precede_referencia_desconhecida():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao([FRAG_A, FRAG_A], [UNID_A], [(FRAG_C, UNID_A)])
    assert mensagem(erro) == "duplicidade: fragmentos_indice"


def test_duplicidade_de_relacao_precede_cobertura_incompleta():
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(
            [FRAG_A, FRAG_B],
            [UNID_A, UNID_B],
            [(FRAG_A, UNID_A), (FRAG_A, UNID_B)],
        )
    assert mensagem(erro) == "duplicidade: correspondencias.origem"


# ---------------------------------------------------------------------------
# Superficie publica
# ---------------------------------------------------------------------------


def test_all_tem_exatamente_dois_nomes():
    from casa77_sdr import response_bijection

    assert response_bijection.__all__ == ["BijecaoInvalida", "validar_bijecao"]


def test_modulo_nao_expoe_outra_funcao_publica():
    from casa77_sdr import response_bijection

    publicos = {
        nome
        for nome in vars(response_bijection)
        if not nome.startswith("_") and nome not in {"annotations", "Sequence"}
    }
    assert publicos == set(response_bijection.__all__)


def test_assinatura_tem_tres_parametros_sem_default():
    parametros = inspect.signature(validar_bijecao).parameters
    assert list(parametros) == [
        "fragmentos_indice",
        "unidades_markdown",
        "correspondencias",
    ]
    assert all(
        parametro.default is inspect.Parameter.empty
        for parametro in parametros.values()
    )
    assert all(
        parametro.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parametro in parametros.values()
    )


def test_assinatura_nao_tem_parametro_de_modo_ou_tolerancia():
    proibidos = {
        "modo",
        "origem",
        "caminho",
        "config",
        "configuracao",
        "estrategia",
        "tolerancia",
        "strict",
        "mode",
    }
    assert not proibidos & set(inspect.signature(validar_bijecao).parameters)


def test_bijecao_invalida_deriva_diretamente_de_exception():
    assert BijecaoInvalida.__bases__ == (Exception,)


def test_bijecao_invalida_nao_e_subclasse_de_outro_erro_do_projeto():
    assert not issubclass(BijecaoInvalida, (TypeError, ValueError, LookupError))


def test_nao_e_exportado_pelo_pacote():
    assert not hasattr(casa77_sdr, "validar_bijecao")
    assert not hasattr(casa77_sdr, "BijecaoInvalida")
    assert "validar_bijecao" not in getattr(casa77_sdr, "__all__", ())
    assert "BijecaoInvalida" not in getattr(casa77_sdr, "__all__", ())


def test_funcao_declara_retorno_none():
    assert inspect.signature(validar_bijecao).return_annotation == "None"


# ---------------------------------------------------------------------------
# Seguranca da mensagem
# ---------------------------------------------------------------------------

CASOS_DE_ERRO = (
    (None, [], []),
    ([], None, []),
    ([], [], None),
    ([None], [], []),
    ([], [None], []),
    ([FRAG_A], [UNID_A], [None]),
    ([FRAG_A], [UNID_A], [(FRAG_A,)]),
    ([FRAG_A], [UNID_A], [(None, UNID_A)]),
    ([FRAG_A], [UNID_A], [(FRAG_A, None)]),
    ([FRAG_A, FRAG_A], [UNID_A], []),
    ([FRAG_A], [UNID_A, UNID_A], []),
    ([FRAG_A], [UNID_A], [(FRAG_A, UNID_A), (FRAG_A, UNID_A)]),
    ([FRAG_A, FRAG_B], [UNID_A], [(FRAG_A, UNID_A), (FRAG_B, UNID_A)]),
    ([FRAG_A], [UNID_A], [(FRAG_B, UNID_A)]),
    ([FRAG_A], [UNID_A], [(FRAG_A, UNID_B)]),
    ([FRAG_A], [UNID_A], []),
    ([FRAG_A], [UNID_A, UNID_B], [(FRAG_A, UNID_A)]),
)


@pytest.mark.parametrize("caso", CASOS_DE_ERRO)
def test_mensagem_tem_categoria_e_localizador_fechados(caso):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(*caso)
    categoria, localizador = partes(mensagem(erro))
    assert categoria in CATEGORIAS
    assert localizador in LOCALIZADORES


@pytest.mark.parametrize("caso", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_token_recebido(caso):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(*caso)
    texto = mensagem(erro)
    for token in (FRAG_A, FRAG_B, FRAG_C, UNID_A, UNID_B, UNID_C):
        assert token not in texto


@pytest.mark.parametrize("caso", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_tipo_concreto(caso):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(*caso)
    texto = mensagem(erro)
    for concreto in ("NoneType", "int", "float", "bytes", "list", "dict", "set"):
        assert concreto not in texto


@pytest.mark.parametrize("caso", CASOS_DE_ERRO)
def test_mensagem_nao_ecoa_numero(caso):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(*caso)
    assert not any(caractere.isdigit() for caractere in mensagem(erro))


@pytest.mark.parametrize("caso", CASOS_DE_ERRO)
def test_mensagem_nao_tem_colchete_de_indice(caso):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(*caso)
    texto = mensagem(erro)
    assert "[" not in texto
    assert "]" not in texto


@pytest.mark.parametrize("caso", CASOS_DE_ERRO)
def test_excecao_nao_tem_cause_nem_context(caso):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(*caso)
    assert erro.value.__cause__ is None
    assert erro.value.__context__ is None
    assert erro.value.__suppress_context__ is False


@pytest.mark.parametrize("caso", CASOS_DE_ERRO)
def test_excecao_carrega_um_unico_argumento(caso):
    with pytest.raises(BijecaoInvalida) as erro:
        validar_bijecao(*caso)
    assert len(erro.value.args) == 1
    assert isinstance(erro.value.args[0], str)


def test_todas_as_categorias_declaradas_sao_alcancaveis():
    alcancadas = set()
    for caso in CASOS_DE_ERRO:
        with pytest.raises(BijecaoInvalida) as erro:
            validar_bijecao(*caso)
        alcancadas.add(partes(mensagem(erro))[0])
    assert alcancadas == set(CATEGORIAS)


# ---------------------------------------------------------------------------
# Pureza (AST)
# ---------------------------------------------------------------------------


def test_imports_sao_fechados():
    assert modulos_importados() == {"__future__", "collections.abc"}


def test_nao_importa_nada_do_proprio_pacote():
    assert not any(
        modulo.startswith("casa77_sdr") for modulo in modulos_importados()
    )


def test_nao_ha_import_dentro_de_funcao():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.FunctionDef):
            for interno in ast.walk(no):
                assert not isinstance(interno, (ast.Import, ast.ImportFrom))


def test_nao_ha_io_nem_filesystem():
    proibidos = {
        "open",
        "read",
        "write",
        "input",
        "print",
        "Path",
        "os",
        "sys",
        "io",
        "pathlib",
        "shutil",
        "tempfile",
        "glob",
    }
    assert not proibidos & identificadores_do_codigo()


def test_nao_ha_rede_nem_processo():
    proibidos = {
        "socket",
        "requests",
        "urllib",
        "urlopen",
        "http",
        "subprocess",
        "asyncio",
        "yaml",
        "json",
    }
    assert not proibidos & identificadores_do_codigo()


def test_nao_ha_locale_ambiente_relogio_nem_calendario():
    proibidos = {
        "locale",
        "setlocale",
        "environ",
        "getenv",
        "time",
        "datetime",
        "date",
        "now",
        "today",
        "clock",
        "random",
        "calendar",
    }
    assert not proibidos & identificadores_do_codigo()


def test_nao_ha_execucao_dinamica():
    proibidos = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "getattr",
        "setattr",
        "globals",
        "locals",
        "vars",
    }
    assert not proibidos & identificadores_do_codigo()


def test_nao_ha_normalizacao_de_token():
    proibidos = {
        "strip",
        "lstrip",
        "rstrip",
        "lower",
        "upper",
        "casefold",
        "title",
        "swapcase",
        "normalize",
        "unicodedata",
        "translate",
        "encode",
        "decode",
        "format",
        "replace",
        "split",
        "sort",
        "sorted",
    }
    assert not proibidos & identificadores_do_codigo()


def test_nao_ha_captura_de_excecao():
    for no in ast.walk(ARVORE_PRODUCAO):
        assert not isinstance(no, (ast.Try, ast.ExceptHandler))


def test_nao_ha_raise_from():
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.Raise):
            assert no.cause is None


def test_nao_ha_cardinalidade_fixa_do_corpus():
    numericos = {str(valor) for valor in literais_numericos()}
    assert "37" not in numericos
    assert "30" not in numericos


def test_producao_nao_menciona_caminho_de_knowledge():
    for proibido in ("knowledge", ".yaml", ".md", "indice-respostas"):
        assert proibido not in CODIGO_PRODUCAO


def test_producao_nao_declara_enum_nem_dataclass():
    identificadores = identificadores_do_codigo()
    assert "Enum" not in identificadores
    assert "dataclass" not in identificadores
    for no in ast.walk(ARVORE_PRODUCAO):
        if isinstance(no, ast.ClassDef):
            assert not no.bases or all(
                isinstance(base, ast.Name) and base.id == "Exception"
                for base in no.bases
            )
            assert not no.decorator_list


def test_producao_declara_uma_unica_classe():
    classes = [
        no.name for no in ast.walk(ARVORE_PRODUCAO) if isinstance(no, ast.ClassDef)
    ]
    assert classes == ["BijecaoInvalida"]


def test_producao_nao_tem_estado_mutavel_de_modulo():
    for no in ARVORE_PRODUCAO.body:
        if isinstance(no, ast.Assign):
            assert isinstance(no.value, (ast.Constant, ast.List))


def test_sequence_e_a_unica_abstracao_importada():
    importados = [
        alias.name
        for no in ast.walk(ARVORE_PRODUCAO)
        if isinstance(no, ast.ImportFrom) and no.module == "collections.abc"
        for alias in no.names
    ]
    assert importados == ["Sequence"]


def test_producao_usa_sequence_para_decidir_contentor():
    assert "Sequence" in identificadores_do_codigo()
    assert issubclass(list, Sequence)


def test_producao_valida_token_por_tipo_exato_e_nao_por_isinstance():
    """`isinstance` sobrevive apenas para decidir contentor; o token e o lado
    da correspondencia sao validados por tipo exato."""
    exatos = [
        "if type(par) is not tuple:",
        "if type(token) is not str:",
        "if type(par[_POSICAO_DA_ORIGEM]) is not str:",
        "if type(par[_POSICAO_DO_DESTINO]) is not str:",
    ]
    for trecho in exatos:
        assert trecho in CODIGO_PRODUCAO
    assert "isinstance(par, tuple)" not in CODIGO_PRODUCAO
    assert "isinstance(token, str)" not in CODIGO_PRODUCAO
    assert "isinstance(par[_POSICAO_DA_ORIGEM], str)" not in CODIGO_PRODUCAO
    assert "isinstance(par[_POSICAO_DO_DESTINO], str)" not in CODIGO_PRODUCAO


def test_producao_nao_converte_o_item_da_relacao():
    """`tuple(correspondencias)` congela a Sequence de topo; converter cada par
    mascararia o tipo concreto do item."""
    assert "tuple(correspondencias)" in CODIGO_PRODUCAO
    assert "tuple(par)" not in CODIGO_PRODUCAO


def test_producao_nao_converte_o_token():
    for proibido in ("str(token", "str(par", "repr(", "!r"):
        assert proibido not in CODIGO_PRODUCAO


# ---------------------------------------------------------------------------
# Imutabilidade das entradas
# ---------------------------------------------------------------------------


def test_entradas_nao_sao_alteradas_no_caminho_valido():
    fragmentos = [FRAG_A, FRAG_B]
    unidades = [UNID_A, UNID_B]
    pares = [(FRAG_A, UNID_A), (FRAG_B, UNID_B)]
    copia_fragmentos = list(fragmentos)
    copia_unidades = list(unidades)
    copia_pares = list(pares)

    validar_bijecao(fragmentos, unidades, pares)

    assert fragmentos == copia_fragmentos
    assert unidades == copia_unidades
    assert pares == copia_pares


def test_entradas_nao_sao_alteradas_no_caminho_de_falha():
    fragmentos = [FRAG_A, FRAG_B]
    unidades = [UNID_A]
    pares = [(FRAG_A, UNID_A)]
    copia_fragmentos = list(fragmentos)
    copia_unidades = list(unidades)
    copia_pares = list(pares)

    with pytest.raises(BijecaoInvalida):
        validar_bijecao(fragmentos, unidades, pares)

    assert fragmentos == copia_fragmentos
    assert unidades == copia_unidades
    assert pares == copia_pares


def test_entradas_nao_sao_alteradas_quando_o_token_e_invalido():
    fragmentos = [FRAG_A, None]
    unidades = [UNID_A]
    pares = [(FRAG_A, UNID_A)]
    copia_fragmentos = list(fragmentos)

    with pytest.raises(BijecaoInvalida):
        validar_bijecao(fragmentos, unidades, pares)

    assert fragmentos == copia_fragmentos
    assert unidades == [UNID_A]
    assert pares == [(FRAG_A, UNID_A)]


def test_chamadas_sucessivas_nao_acumulam_estado():
    fragmentos = [FRAG_A]
    unidades = [UNID_A]
    pares = [(FRAG_A, UNID_A)]
    assert validar_bijecao(fragmentos, unidades, pares) is None
    with pytest.raises(BijecaoInvalida):
        validar_bijecao(fragmentos, unidades, [])
    assert validar_bijecao(fragmentos, unidades, pares) is None
