"""Consulta de status na autoridade estruturada — `consultar_status` (`C-11`).

Zero valor comercial: as asserções são **estruturais** — identidade, domínio de
tokens, propagação de exceção e ausência de vocabulário paralelo. Nenhum preço,
capacidade, horário ou frase aprovada é reproduzido.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr.response_index import IndiceInvalido
from casa77_sdr.response_index_load import carregar_indice
from casa77_sdr.response_index_status import (
    StatusNaoLocalizado,
    consultar_status,
)
from casa77_sdr.response_index_tokens import (
    ProjecaoDeIdentidadeInvalida,
    derivar_tokens_do_indice,
)

RAIZ = Path(__file__).resolve().parents[1]
INDICE = RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml"
MODULO = RAIZ / "src" / "casa77_sdr" / "response_index_status.py"

TOTAL_FRAGMENTOS = 37

# Vocabulário canônico de `C-3`. Ele vive **aqui**, no teste, exatamente para
# provar que **não** vive no módulo sob teste.
VOCABULARIO_CANONICO = frozenset({"APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO"})


@pytest.fixture(scope="module")
def indice() -> dict[str, Any]:
    return carregar_indice(INDICE)


def _indice_sintetico(**fragmento: Any) -> dict[str, Any]:
    """Índice mínimo válido para `validar_indice`, sem valor comercial."""
    base = {"id": "F1", "status": "APROVADO", "bindings": []}
    base.update(fragmento)
    return {"respostas": [{"id": "R01", "fragmentos": [base]}]}


# ---------------------------------------------------------------------------
# A. Status real, na autoridade do índice


def test_status_de_token_real(indice: dict[str, Any]) -> None:
    """O rótulo devolvido é exatamente o que o índice físico declara."""
    for resposta in indice["respostas"]:
        for fragmento in resposta["fragmentos"]:
            token = f"{resposta['id']}/{fragmento['id']}"

            assert consultar_status(indice, token) == fragmento["status"]


def test_r28_f1_e_aprovado_na_autoridade(indice: dict[str, Any]) -> None:
    """`R28/F1` é `APROVADO` **no índice**, sem passar pelo Markdown.

    O `PARCIAL` do cabeçalho de `R28` é rótulo humano agregado e **não** é
    consultado aqui: o valor esperado vem da autoridade de status.
    """
    assert consultar_status(indice, "R28/F1") == "APROVADO"


def test_os_37_tokens_reais_resolvem(indice: dict[str, Any]) -> None:
    """Todo token do domínio projetado tem status na autoridade."""
    tokens = derivar_tokens_do_indice(indice)

    assert len(tokens) == TOTAL_FRAGMENTOS

    resolvidos = [consultar_status(indice, token) for token in tokens]

    assert len(resolvidos) == TOTAL_FRAGMENTOS
    assert set(resolvidos) <= VOCABULARIO_CANONICO


# ---------------------------------------------------------------------------
# B. Recusa — zero valor padrão


def test_token_inexistente_e_recusado(indice: dict[str, Any]) -> None:
    """Fora do domínio projetado não há status: nada é presumido."""
    with pytest.raises(StatusNaoLocalizado) as erro:
        consultar_status(indice, "R99/F1")

    assert str(erro.value) == "token_inexistente: token"


@pytest.mark.parametrize(
    "token",
    [None, 1, b"R01/F1", ("R01", "F1"), ["R01/F1"], object()],
)
def test_token_de_tipo_invalido_e_recusado(
    indice: dict[str, Any], token: object
) -> None:
    with pytest.raises(StatusNaoLocalizado) as erro:
        consultar_status(indice, token)  # type: ignore[arg-type]

    assert str(erro.value) == "tipo_invalido: token"


def test_subclasse_de_str_nao_e_token(indice: dict[str, Any]) -> None:
    """`str` **exata**: uma subclasse decidiria por conta própria a identidade."""

    class Token(str):
        pass

    with pytest.raises(StatusNaoLocalizado) as erro:
        consultar_status(indice, Token("R01/F1"))

    assert str(erro.value) == "tipo_invalido: token"


def test_nao_existe_valor_padrao(indice: dict[str, Any]) -> None:
    """Token ausente **nunca** vira `APROVADO` nem qualquer outro rótulo."""
    for ausente in ("", "R01", "F1", "R01/", "/F1", "R01/F9999"):
        with pytest.raises(StatusNaoLocalizado):
            consultar_status(indice, ausente)


def test_markdown_nao_e_fallback() -> None:
    """O módulo não importa fronteira alguma de status do Markdown.

    A prova é estrutural sobre o próprio arquivo: nenhum `import` alcança as
    fronteiras que leem rótulo de cabeçalho, `status-fragmento` ou propagação.
    """
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    importados = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module is not None
    } | {
        alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.Import)
        for alias in no.names
    }

    proibidos = {
        "casa77_sdr.response_status",
        "casa77_sdr.response_status_composition",
        "casa77_sdr.response_status_propagation",
        "casa77_sdr.response_fragment_status",
        "casa77_sdr.response_header_labels",
        "casa77_sdr.response_markdown_units",
        "casa77_sdr.response_section_membership",
        "casa77_sdr.response_emittable_text",
        "casa77_sdr.response_index_load",
        "pathlib",
        "yaml",
    }

    assert importados & proibidos == set()
    assert "respostas-aprovadas.md" not in MODULO.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# C. As autoridades existentes correm primeiro e atravessam intactas


def test_indice_invalido_propaga_indice_invalido() -> None:
    """Rótulo fora do vocabulário é `IndiceInvalido`, nunca categoria local."""
    invalido = _indice_sintetico(status="PARCIAL")

    with pytest.raises(IndiceInvalido):
        consultar_status(invalido, "R01/F1")


def test_estrutura_invalida_propaga_indice_invalido() -> None:
    for invalido in ({}, {"respostas": {}}, {"respostas": [{}]}, "R01/F1", None):
        with pytest.raises(IndiceInvalido):
            consultar_status(invalido, "R01/F1")


def test_projecao_invalida_propaga_projecao_de_identidade_invalida() -> None:
    """`validar_indice` aceita `id` não vazio; a projeção exige `C-A5-I3`.

    Um `id` fora da gramática fechada do token, portanto, passa pela validação
    estrutural e falha na projeção — e essa exceção atravessa **intacta**.
    """
    projecao_invalida = _indice_sintetico(id="X1")

    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        consultar_status(projecao_invalida, "R01/X1")


def test_indice_invalido_vence_token_invalido() -> None:
    """A estrutura entra pelos portões **antes** do token."""
    invalido = _indice_sintetico(status="PARCIAL")

    with pytest.raises(IndiceInvalido):
        consultar_status(invalido, None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# D. Ausência de vocabulário paralelo e de mutação


def test_modulo_nao_declara_segunda_tabela_de_status() -> None:
    """Nenhum rótulo canônico é literal no módulo — nem em `docstring`.

    Se o módulo carregasse a sua própria tabela, ele passaria a ser uma segunda
    autoridade sobre `C-3`. A autoridade é `validar_indice`, e este teste prova
    estruturalmente que ela não foi duplicada.
    """
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    literais = {
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    }

    assert literais & VOCABULARIO_CANONICO == set()


def test_consultar_status_nao_muta_o_indice(indice: dict[str, Any]) -> None:
    antes = copy.deepcopy(indice)

    for token in derivar_tokens_do_indice(indice):
        consultar_status(indice, token)

    assert indice == antes


def test_chamadas_repetidas_dao_o_mesmo_resultado(indice: dict[str, Any]) -> None:
    for _ in range(3):
        assert consultar_status(indice, "R28/F1") == "APROVADO"
