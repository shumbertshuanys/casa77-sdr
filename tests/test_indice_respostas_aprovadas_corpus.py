"""Integração estrutural do corpus real — índice físico × Markdown × YAML.

Esta suíte prova, **sobre os artefatos versionados reais**, que o índice
`knowledge/indice-respostas-aprovadas.yaml` é estruturalmente válido e coerente
com `knowledge/respostas-aprovadas.md` e com `knowledge/casa77.yaml`. Ela é a
prova permanente dos gates **`C-A1-ST6`**–**`C-A1-ST9`** e de **`PH7`**/**`PH8`**.

**Ela usa exclusivamente as fronteiras de produção já materializadas.** Não
existe aqui *parser*, *renderer*, resolver, formatador ou expressão regular de
*placeholder* paralelos: cada juízo é delegado ao módulo que tem autoridade
sobre ele. O que esta suíte acrescenta é **a composição** dessas fronteiras
sobre o corpus real.

**Zero valor comercial.** Nenhum preço, capacidade, horário, prazo, percentual,
quantidade ou frase aprovada é reproduzido. As asserções são **estruturais** —
contagens, coincidência de domínios, aplicabilidade de formato, veracidade de
predicado — e nunca comparam conteúdo factual contra literal esperado.

**Autoridade de status.** Sob `C-11`, a autoridade de status por fragmento é
`knowledge/indice-respostas-aprovadas.yaml`. `knowledge/respostas-aprovadas.md`
permanece como **representação física de reconciliação**, nunca como autoridade:
a conferência aqui corre na direção **índice → Markdown**.

**O que ela NÃO afirma.** Não constrói *renderer* de produção; não cria *lookup*
de status nem consumidor operacional; não decide candidatura, cobertura, `E09`,
`pendencia_impeditiva`, handoff nem condição de ciclo (`C-12`); e, para os
*bindings* `RUNTIME_AUTORITATIVO`, **não afirma verdade operacional** — ver
`test_st9_runtime_nao_afirma_verdade_operacional`.
"""

from __future__ import annotations

import collections
from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.response_assertion import avaliar_assertiva
from casa77_sdr.response_bijection import validar_bijecao
from casa77_sdr.response_correspondence import validar_correspondencia_canonica
from casa77_sdr.response_emittable_text import extrair_textos_emitiveis
from casa77_sdr.response_format import (
    formatar_hora,
    formatar_inteiro,
    formatar_inteiro_agrupado,
    formatar_lista,
    formatar_simbolo_moeda,
    formatar_texto,
)
from casa77_sdr.response_index import validar_indice
from casa77_sdr.response_index_load import carregar_indice
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice
from casa77_sdr.response_markdown_units import ler_unidades_marcadas
from casa77_sdr.response_null_pending import recusar_nulo_ou_pendente
from casa77_sdr.response_placeholder import decompor_template
from casa77_sdr.response_status_composition import compor_status_dos_fragmentos
from casa77_sdr.response_yaml_path_context import validar_caminho_de_binding
from casa77_sdr.response_yaml_resolve import resolver_caminho

RAIZ = Path(__file__).resolve().parents[1]
INDICE = RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml"
MARKDOWN = RAIZ / "knowledge" / "respostas-aprovadas.md"
BASE_FACTUAL = RAIZ / "knowledge" / "casa77.yaml"

# Cardinalidades físicas do corpus corrente. São **contagens estruturais**, não
# dado comercial: nenhuma delas é preço, capacidade, horário ou condição.
TOTAL_FRAGMENTOS = 37
TOTAL_RESPOSTAS = 30
TOTAL_BINDINGS = 118
TOTAL_RENDERIZADO_YAML = 62
TOTAL_ASSERTIVA_YAML = 52
TOTAL_ASSERTIVA_RUNTIME = 4
TOTAL_OCORRENCIAS_PLACEHOLDER = 65
TOTAL_FRAGMENTOS_COM_RENDERIZADO = 19

# Despacho fechado de `C-6`. Cada formato é aplicado pela sua própria fronteira.
_FORMATADORES = {
    "inteiro": formatar_inteiro,
    "inteiro_agrupado": formatar_inteiro_agrupado,
    "simbolo_moeda": formatar_simbolo_moeda,
    "hora": formatar_hora,
    "texto": formatar_texto,
    "lista": formatar_lista,
}


@pytest.fixture(scope="module")
def indice() -> dict[str, Any]:
    """O índice físico real, lido pela fronteira de carga (`ST6`)."""
    return carregar_indice(INDICE)


@pytest.fixture(scope="module")
def markdown() -> str:
    return MARKDOWN.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def base() -> dict[str, Any]:
    """A base factual aprovada, já carregada em memória."""
    return yaml.safe_load(BASE_FACTUAL.read_text(encoding="utf-8"))


def _fragmentos(indice: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Pares `(token, fragmento)` na ordem física do índice."""
    return [
        (f"{resposta['id']}/{fragmento['id']}", fragmento)
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
    ]


def _bindings(indice: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    return [
        (token, binding)
        for token, fragmento in _fragmentos(indice)
        for binding in fragmento["bindings"]
    ]


def _resolver(base: dict[str, Any], caminho: str) -> object:
    """Valida contexto e resolve o caminho, pelas fronteiras de `CY13`."""
    decomposicao = validar_caminho_de_binding(caminho, fragmento_itera=False)
    return resolver_caminho(base, decomposicao)


# ---------------------------------------------------------------------------
# ST6 — o índice físico existe, carrega e é estruturalmente válido


def test_st6_indice_fisico_existe() -> None:
    assert INDICE.exists()


def test_st6_indice_carrega_pela_fronteira(indice: dict[str, Any]) -> None:
    """`carregar_indice` aceita o artefato real, sem chave duplicada."""
    assert isinstance(indice, dict)
    assert "respostas" in indice


def test_st6_e1_considera_o_indice_estruturalmente_valido(
    indice: dict[str, Any],
) -> None:
    """E1 valida o índice real — incluindo a gramática de *placeholder*."""
    assert validar_indice(indice) is None


def test_st6_cardinalidade_estrutural(indice: dict[str, Any]) -> None:
    assert len(indice["respostas"]) == TOTAL_RESPOSTAS
    assert len(_fragmentos(indice)) == TOTAL_FRAGMENTOS
    assert len(_bindings(indice)) == TOTAL_BINDINGS


def test_st6_vocabulario_de_status_do_indice(indice: dict[str, Any]) -> None:
    contagem = collections.Counter(f["status"] for _, f in _fragmentos(indice))

    assert contagem["APROVADO"] == 35
    assert contagem["AGUARDA_APROVACAO"] == 2
    assert contagem["BLOQUEADO"] == 0
    assert set(contagem) <= {"APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO"}


def test_st6_mecanismo_e_origem(indice: dict[str, Any]) -> None:
    contagem = collections.Counter(
        (b["mecanismo"], b["origem"]) for _, b in _bindings(indice)
    )

    assert contagem[("RENDERIZADO", "YAML")] == TOTAL_RENDERIZADO_YAML
    assert contagem[("ASSERTIVA", "YAML")] == TOTAL_ASSERTIVA_YAML
    assert contagem[("ASSERTIVA", "RUNTIME_AUTORITATIVO")] == TOTAL_ASSERTIVA_RUNTIME
    assert sum(contagem.values()) == TOTAL_BINDINGS


def test_st6_nenhum_fragmento_itera(indice: dict[str, Any]) -> None:
    assert not [t for t, f in _fragmentos(indice) if "itera_sobre" in f]


def test_st6_indice_nao_armazena_valor_resolvido(indice: dict[str, Any]) -> None:
    """C-1h–C-1m e C-15e: o índice guarda referentes, nunca o valor.

    O esquema fechado de E1 já proíbe chave desconhecida; aqui confirma-se que
    nenhum *binding* carrega campo de valor, *snapshot*, *hash* ou versão.
    """
    permitidas = {
        "nome",
        "mecanismo",
        "origem",
        "caminho_yaml",
        "fato_runtime",
        "placeholder",
        "formato",
        "predicado",
    }

    for _, binding in _bindings(indice):
        assert set(binding) <= permitidas


# ---------------------------------------------------------------------------
# ST7 — bijeção entre o domínio do índice e o do Markdown


def test_st7_bijecao_integral(indice: dict[str, Any], markdown: str) -> None:
    do_indice = derivar_tokens_do_indice(indice)
    do_markdown = ler_unidades_marcadas(markdown)

    assert len(do_indice) == TOTAL_FRAGMENTOS
    assert len(do_markdown) == TOTAL_FRAGMENTOS

    correspondencias = [(token, token) for token in do_indice]

    assert validar_bijecao(do_indice, do_markdown, correspondencias) is None


def test_st7_correspondencia_canonica(
    indice: dict[str, Any], markdown: str
) -> None:
    """A mesma bijeção, pela fronteira que a encapsula."""
    assert validar_correspondencia_canonica(indice, markdown) is None


# ---------------------------------------------------------------------------
# ST8 — status do índice × status composto do Markdown


def test_st8_markdown_reconcilia_com_status_autoritativo_do_indice(
    indice: dict[str, Any], markdown: str
) -> None:
    """37/37, por ocorrência física e na ordem do documento.

    A direção é **índice → Markdown** (`C-11`): o índice é o **esperado
    autoritativo** e o Markdown é o **conferido**. Esta comparação **NÃO** torna
    o Markdown autoridade — ela prova apenas que a representação humana de
    reconciliação não divergiu da autoridade.
    """
    autoritativo = {token: f["status"] for token, f in _fragmentos(indice)}
    fisico_no_markdown = compor_status_dos_fragmentos(markdown)

    assert len(autoritativo) == TOTAL_FRAGMENTOS
    assert len(fisico_no_markdown) == TOTAL_FRAGMENTOS

    # A bijeção dos domínios já é de `ST7`; aqui ela é apenas a pré-condição
    # que torna a conferência por token total dos dois lados.
    assert {token for token, _ in fisico_no_markdown} == set(autoritativo)

    divergentes = [
        token
        for token, status_fisico in fisico_no_markdown
        if status_fisico != autoritativo[token]
    ]

    assert divergentes == []


def test_r28_f1_tem_status_autoritativo_aprovado_no_indice(
    indice: dict[str, Any],
) -> None:
    """`R28/F1` é `APROVADO` **no índice**, sem passar pelo Markdown.

    O status esperado é lido **diretamente da autoridade** (`C-11`): nada aqui
    consulta o rótulo `PARCIAL` do cabeçalho de `R28`, a declaração
    `status-fragmento` ou a propagação `SP1`–`SP7`. Isso demonstra que `PARCIAL`
    permanece rótulo humano agregado do Markdown e **não** é um quarto status
    autoritativo.
    """
    autoritativo = {token: f["status"] for token, f in _fragmentos(indice)}

    assert autoritativo["R28/F1"] == "APROVADO"
    assert "PARCIAL" not in set(autoritativo.values())


# ---------------------------------------------------------------------------
# ST9 — referentes YAML resolvem, não são C-7 e sustentam o mecanismo


def test_st9_todo_caminho_yaml_resolve(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    """Contexto validado e caminho resolvido na base real, por `CY13`."""
    for token, binding in _bindings(indice):
        if binding["origem"] != "YAML":
            continue
        _resolver(base, binding["caminho_yaml"])


def test_st9_nenhum_referente_yaml_e_nulo_ou_pendente(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    """`C-7`: nenhum *binding* necessário resolve para `null` ou `pendente`."""
    for token, binding in _bindings(indice):
        if binding["origem"] != "YAML":
            continue
        valor = _resolver(base, binding["caminho_yaml"])
        recusar_nulo_ou_pendente(valor)


def test_st9_toda_assertiva_yaml_e_verdadeira(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    """Cada `ASSERTIVA` de origem YAML se sustenta sobre a base corrente."""
    falsas = []

    for token, binding in _bindings(indice):
        if binding["mecanismo"] != "ASSERTIVA" or binding["origem"] != "YAML":
            continue
        valor = recusar_nulo_ou_pendente(
            _resolver(base, binding["caminho_yaml"])
        )
        if not avaliar_assertiva(binding["predicado"], valor):
            falsas.append(f"{token}.{binding['nome']}")

    assert falsas == []


def test_st9_todo_formato_renderizado_e_aplicavel(
    indice: dict[str, Any], base: dict[str, Any]
) -> None:
    """O formatador declarado aplica-se ao valor real, sem exceção."""
    for token, binding in _bindings(indice):
        if binding["mecanismo"] != "RENDERIZADO":
            continue
        valor = recusar_nulo_ou_pendente(
            _resolver(base, binding["caminho_yaml"])
        )
        formatado = _FORMATADORES[binding["formato"]](valor)

        assert isinstance(formatado, str)


# ---------------------------------------------------------------------------
# ST9 — RUNTIME_AUTORITATIVO: representação física, nunca verdade operacional


def test_st9_runtime_nao_afirma_verdade_operacional(
    indice: dict[str, Any],
) -> None:
    """Os *bindings* runtime são provados **só na representação física**.

    A verdade de um `fato_runtime` depende da consulta autoritativa do ciclo, e
    **não** da base versionada. Esta suíte **não** fabrica estado runtime e
    **não** exige que dois fragmentos alternativos sejam simultaneamente
    verdadeiros: o que se prova é que a representação passa por E1, que o fato
    pertence ao vocabulário fechado, que não há `caminho_yaml` e que o predicado
    físico previsto está preservado.
    """
    fatos_fechados = {"consulta_calendario_valida", "data_disponivel"}
    predicados_fechados = {"EH_VERDADEIRO", "EH_FALSO"}
    runtime = [
        (token, binding)
        for token, binding in _bindings(indice)
        if binding["origem"] == "RUNTIME_AUTORITATIVO"
    ]

    assert len(runtime) == TOTAL_ASSERTIVA_RUNTIME

    for token, binding in runtime:
        assert binding["mecanismo"] == "ASSERTIVA"
        assert binding["fato_runtime"] in fatos_fechados
        assert "caminho_yaml" not in binding
        assert "placeholder" not in binding
        assert "formato" not in binding
        assert binding["predicado"] in predicados_fechados


# ---------------------------------------------------------------------------
# PH7 / PH8 — ocorrência e correspondência de *placeholder* no template real


def test_ph7_ph8_template_e_bindings_correspondem(
    indice: dict[str, Any], markdown: str
) -> None:
    """Para cada fragmento: todo nome ocorre, e todo *placeholder* tem nome.

    O texto canônico vem de `extrair_textos_emitiveis`, e o julgamento é
    inteiramente de `decompor_template` — nenhuma expressão regular de
    *placeholder* é escrita aqui.
    """
    textos = dict(extrair_textos_emitiveis(markdown))

    assert len(textos) == TOTAL_FRAGMENTOS

    for token, fragmento in _fragmentos(indice):
        nomes = tuple(
            b["nome"]
            for b in fragmento["bindings"]
            if b["mecanismo"] == "RENDERIZADO"
        )
        decompor_template(textos[token], nomes)


def test_ph7_contagem_de_ocorrencias_fisicas(
    indice: dict[str, Any], markdown: str
) -> None:
    """65 ocorrências para 62 *bindings*: a repetição é legítima (`PH7c`)."""
    textos = dict(extrair_textos_emitiveis(markdown))
    ocorrencias = 0
    com_renderizado = 0

    for token, fragmento in _fragmentos(indice):
        nomes = tuple(
            b["nome"]
            for b in fragmento["bindings"]
            if b["mecanismo"] == "RENDERIZADO"
        )
        if not nomes:
            continue
        com_renderizado += 1
        partes = decompor_template(textos[token], nomes)
        # A decomposição alterna `literal, nome, literal, ...`: os nomes estão
        # nas posições ímpares, e repetições permanecem repetidas.
        ocorrencias += len(partes) // 2

    assert com_renderizado == TOTAL_FRAGMENTOS_COM_RENDERIZADO
    assert ocorrencias == TOTAL_OCORRENCIAS_PLACEHOLDER
    assert ocorrencias >= TOTAL_RENDERIZADO_YAML


def test_ph8_fragmento_sem_renderizado_nao_tem_placeholder(
    indice: dict[str, Any], markdown: str
) -> None:
    """Os 18 fragmentos estáticos não carregam *placeholder* algum."""
    textos = dict(extrair_textos_emitiveis(markdown))
    estaticos = 0

    for token, fragmento in _fragmentos(indice):
        if any(b["mecanismo"] == "RENDERIZADO" for b in fragmento["bindings"]):
            continue
        estaticos += 1
        assert decompor_template(textos[token], ()) == (textos[token],)

    assert estaticos == TOTAL_FRAGMENTOS - TOTAL_FRAGMENTOS_COM_RENDERIZADO


# ---------------------------------------------------------------------------
# Invariantes negativas — o que esta materialização NÃO fez


def test_markdown_preserva_rotulos_de_status_para_reconciliacao(
    markdown: str,
) -> None:
    """O Markdown preserva a representação física dos rótulos de status.

    Isso é **representação de reconciliação**, nunca autoridade: sob `C-11` a
    autoridade de status é `knowledge/indice-respostas-aprovadas.yaml`. Prova-se
    apenas que os cabeçalhos `Rxx` e a declaração `status-fragmento` exigida pelo
    contrato `PM` continuam fisicamente presentes.
    """
    assert "## R" in markdown
    assert "status-fragmento" in markdown


def test_base_factual_nao_e_alterada_por_esta_suite(base: dict[str, Any]) -> None:
    """Nenhuma fronteira consumida aqui muta a raiz factual recebida."""
    copia = yaml.safe_load(BASE_FACTUAL.read_text(encoding="utf-8"))

    assert base == copia
