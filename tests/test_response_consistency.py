"""`ValidadorConsistenciaBase` — conferência do corpus contra a base factual.

Esta suíte exercita a fronteira **sobre os artefatos versionados reais** e
sobre estruturas sintéticas mínimas. **Zero valor comercial** é reproduzido:
nenhum preço, capacidade, horário, prazo, percentual, quantidade ou frase
aprovada aparece no código. As mutações de cenário são **mecânicas** — obtidas
do próprio índice em tempo de execução e aplicadas a uma **cópia em memória** da
base — e as asserções são **estruturais**.

As fronteiras de produção são usadas como estão: o *parser* de `caminho_yaml` e
o resolver de `CY13` também **localizam** o ponto de mutação, de modo que nenhum
*parser*, resolver ou gramática paralela é escrito aqui.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.response_assertion import AssertivaNaoAvaliavel
from casa77_sdr.response_consistency import (
    CategoriaDivergencia,
    ConsistenciaNaoAvaliavel,
    Divergencia,
    ReferenteIndisponivel,
    ResultadoConsistencia,
    validar_consistencia_base,
)
from casa77_sdr.response_emittable_text import extrair_textos_emitiveis
from casa77_sdr.response_index import IndiceInvalido
from casa77_sdr.response_index_load import carregar_indice
from casa77_sdr.response_yaml_path import analisar_caminho_yaml
from casa77_sdr.response_yaml_resolve import (
    CaminhoYamlNaoResolvido,
    resolver_caminho,
)

RAIZ = Path(__file__).resolve().parents[1]
INDICE = RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml"
MARKDOWN = RAIZ / "knowledge" / "respostas-aprovadas.md"
BASE_FACTUAL = RAIZ / "knowledge" / "casa77.yaml"
MODULO_VCB = RAIZ / "src" / "casa77_sdr" / "response_consistency.py"

# Cardinalidades estruturais do corpus corrente — contagens, não dado comercial.
TOTAL_FRAGMENTOS = 37
TOTAL_ASSERTIVA_RUNTIME = 4

_CAMPOS_DE_IDENTIDADE = (
    "token",
    "rxx",
    "fragmento_id",
    "binding",
    "mecanismo",
    "origem",
    "referente",
)


@pytest.fixture(scope="module")
def indice() -> dict[str, Any]:
    return carregar_indice(INDICE)


@pytest.fixture(scope="module")
def base() -> dict[str, Any]:
    return yaml.safe_load(BASE_FACTUAL.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def textos() -> dict[str, str]:
    return dict(
        extrair_textos_emitiveis(MARKDOWN.read_text(encoding="utf-8"))
    )


# ---------------------------------------------------------------------------
# Utilitários de cenário — todos mecânicos, nenhum literal comercial


def _bindings(indice: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    return [
        (f"{resposta['id']}/{fragmento['id']}", binding)
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
        for binding in fragmento["bindings"]
    ]


def _caminhos_de_assertiva(indice: dict[str, Any]) -> set[str]:
    return {
        binding["caminho_yaml"]
        for _, binding in _bindings(indice)
        if binding["mecanismo"] == "ASSERTIVA" and binding["origem"] == "YAML"
    }


def _terminal_simples(caminho: str) -> bool:
    """O caminho é absoluto e o seu último segmento não tem seletor."""
    relativo, segmentos = analisar_caminho_yaml(caminho)
    return relativo is False and segmentos[-1][1] is None


def _pai_e_chave(base: dict[str, Any], caminho: str) -> tuple[dict[str, Any], str]:
    """Localiza o **mapa pai** do terminal, pelas fronteiras de `CY13`."""
    _, segmentos = analisar_caminho_yaml(caminho)
    if len(segmentos) == 1:
        return base, segmentos[0][0]

    pai = resolver_caminho(base, (False, segmentos[:-1]))
    assert isinstance(pai, dict)
    return pai, segmentos[-1][0]


def _definir(base: dict[str, Any], caminho: str, valor: object) -> None:
    pai, chave = _pai_e_chave(base, caminho)
    pai[chave] = valor


def _remover(base: dict[str, Any], caminho: str) -> None:
    pai, chave = _pai_e_chave(base, caminho)
    del pai[chave]


def _assertiva_booleana(
    indice: dict[str, Any], base: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    """Primeira `ASSERTIVA` YAML, em ordem física, que resolve para `bool`."""
    for token, binding in _bindings(indice):
        if binding["mecanismo"] != "ASSERTIVA" or binding["origem"] != "YAML":
            continue
        caminho = binding["caminho_yaml"]
        if not _terminal_simples(caminho):
            continue
        _, segmentos = analisar_caminho_yaml(caminho)
        if isinstance(resolver_caminho(base, (False, segmentos)), bool):
            return token, binding
    raise AssertionError("corpus sem ASSERTIVA booleana endereçável")


def _renderizado_exclusivo(
    indice: dict[str, Any], *, formato: str | None = None
) -> tuple[str, dict[str, Any]]:
    """Primeiro `RENDERIZADO` YAML cujo caminho nenhuma `ASSERTIVA` usa."""
    de_assertiva = _caminhos_de_assertiva(indice)
    for token, binding in _bindings(indice):
        if binding["mecanismo"] != "RENDERIZADO" or binding["origem"] != "YAML":
            continue
        if formato is not None and binding["formato"] != formato:
            continue
        caminho = binding["caminho_yaml"]
        if caminho in de_assertiva or not _terminal_simples(caminho):
            continue
        return token, binding
    raise AssertionError("corpus sem RENDERIZADO endereçável exclusivo")


def _dto_do_binding(
    itens: tuple[Any, ...], token: str, nome: str
) -> Any:
    encontrados = [d for d in itens if d.token == token and d.binding == nome]
    assert len(encontrados) == 1
    return encontrados[0]


# ---------------------------------------------------------------------------
# T1 — corpus real: consistente, sem divergência e sem indisponibilidade


def test_t1_corpus_real_e_consistente(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    resultado = validar_consistencia_base(indice, base, textos)

    assert isinstance(resultado, ResultadoConsistencia)
    assert resultado.divergencias == ()
    assert resultado.referentes_indisponiveis == ()
    assert resultado.tokens_divergentes == ()
    assert len(resultado.status_por_fragmento) == TOTAL_FRAGMENTOS
    assert len(resultado.bindings_runtime_nao_avaliados) == TOTAL_ASSERTIVA_RUNTIME


def test_t1_status_projetado_vem_da_autoridade(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    """A projeção coincide, token a token, com o que o índice declara."""
    resultado = validar_consistencia_base(indice, base, textos)
    do_indice = [
        (f"{resposta['id']}/{fragmento['id']}", fragmento["status"])
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
    ]

    assert list(resultado.status_por_fragmento) == do_indice


# ---------------------------------------------------------------------------
# T2 — divergência F3–F5: `ASSERTIVA` avaliável e falsa (Classe II)


def test_t2_assertiva_falsa_e_divergencia_classe_ii(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    token, binding = _assertiva_booleana(indice, base)
    caminho = binding["caminho_yaml"]

    copia = copy.deepcopy(base)
    _, segmentos = analisar_caminho_yaml(caminho)
    _definir(copia, caminho, not resolver_caminho(copia, (False, segmentos)))

    resultado = validar_consistencia_base(indice, copia, textos)

    assert resultado.divergencias != ()
    assert {d.categoria for d in resultado.divergencias} == {
        CategoriaDivergencia.ASSERTIVA_FALSA
    }
    assert resultado.referentes_indisponiveis == ()

    divergencia = _dto_do_binding(
        resultado.divergencias, token, binding["nome"]
    )
    rxx, fragmento_id = token.split("/")

    assert divergencia.token == token
    assert divergencia.rxx == rxx
    assert divergencia.fragmento_id == fragmento_id
    assert divergencia.binding == binding["nome"]
    assert divergencia.mecanismo == "ASSERTIVA"
    assert divergencia.origem == "YAML"
    assert divergencia.referente == caminho
    assert token in resultado.tokens_divergentes


def test_t2_tokens_divergentes_sem_repeticao_e_em_ordem_fisica(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    _, binding = _assertiva_booleana(indice, base)
    caminho = binding["caminho_yaml"]

    copia = copy.deepcopy(base)
    _, segmentos = analisar_caminho_yaml(caminho)
    _definir(copia, caminho, not resolver_caminho(copia, (False, segmentos)))

    resultado = validar_consistencia_base(indice, copia, textos)
    esperado: list[str] = []
    for divergencia in resultado.divergencias:
        if divergencia.token not in esperado:
            esperado.append(divergencia.token)

    assert list(resultado.tokens_divergentes) == esperado
    assert len(set(resultado.tokens_divergentes)) == len(
        resultado.tokens_divergentes
    )


# ---------------------------------------------------------------------------
# T3 — `C-7`: referente indisponível, jamais divergência


@pytest.mark.parametrize(
    "indisponivel", [None, {"status": "pendente"}], ids=["nulo", "pendente"]
)
def test_t3_c7_produz_referente_indisponivel(
    indice: dict[str, Any],
    base: dict[str, Any],
    textos: dict[str, str],
    indisponivel: object,
) -> None:
    token, binding = _renderizado_exclusivo(indice)

    copia = copy.deepcopy(base)
    _definir(copia, binding["caminho_yaml"], indisponivel)

    resultado = validar_consistencia_base(indice, copia, textos)

    assert resultado.divergencias == ()
    assert resultado.tokens_divergentes == ()
    assert resultado.referentes_indisponiveis != ()

    registro = _dto_do_binding(
        resultado.referentes_indisponiveis, token, binding["nome"]
    )

    assert isinstance(registro, ReferenteIndisponivel)
    assert registro.referente == binding["caminho_yaml"]
    assert registro.origem == "YAML"


# ---------------------------------------------------------------------------
# T4 — formato inaplicável: divergência estrutural do fragmento


def test_t4_formato_inaplicavel_e_divergencia(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    """Fato existe, caminho resolve, `C-7` não recusa — o formato não aplica."""
    token, binding = _renderizado_exclusivo(indice)

    copia = copy.deepcopy(base)
    # Nenhum dos seis formatadores de `C-6` aceita um `set`: não é `int`, não é
    # `str` e não é `Sequence`. O valor é sintético e não representa fato algum.
    _definir(copia, binding["caminho_yaml"], set())

    resultado = validar_consistencia_base(indice, copia, textos)

    assert resultado.referentes_indisponiveis == ()
    assert {d.categoria for d in resultado.divergencias} == {
        CategoriaDivergencia.FORMATO_INAPLICAVEL
    }

    divergencia = _dto_do_binding(
        resultado.divergencias, token, binding["nome"]
    )

    assert divergencia.mecanismo == "RENDERIZADO"
    assert divergencia.referente == binding["caminho_yaml"]
    assert token in resultado.tokens_divergentes


# ---------------------------------------------------------------------------
# T5 — valor legítimo mudou: `C-15` NÃO é repetido em runtime


def test_t5_outro_valor_valido_do_mesmo_dominio_nao_diverge(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    """O *template* carrega *placeholder*, não valor: mudar o fato é legítimo.

    Se esta fronteira guardasse *snapshot*, valor anterior ou *hash*, ou se
    repetisse `C-15` em runtime, esta mudança apareceria como divergência.
    """
    _, binding = _renderizado_exclusivo(indice, formato="texto")

    copia = copy.deepcopy(base)
    _, segmentos = analisar_caminho_yaml(binding["caminho_yaml"])
    anterior = resolver_caminho(copia, (False, segmentos))
    assert isinstance(anterior, str)
    _definir(copia, binding["caminho_yaml"], anterior + anterior)

    resultado = validar_consistencia_base(indice, copia, textos)

    assert resultado.divergencias == ()
    assert resultado.referentes_indisponiveis == ()
    assert resultado.tokens_divergentes == ()


def test_t5_modulo_nao_chama_equivalencia_textual() -> None:
    """`sao_textualmente_equivalentes` não é importada nem chamada.

    A prova é sobre a **árvore sintática**, e não sobre o texto do arquivo: a
    docstring do módulo cita a função justamente para declarar que ela **não**
    é usada, e isso não pode fazer o teste passar nem falhar por engano.
    """
    arvore = ast.parse(MODULO_VCB.read_text(encoding="utf-8"))
    modulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module is not None
    }
    importados = {
        alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom)
        for alias in no.names
    }
    chamados = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }

    assert "casa77_sdr.response_equivalence" not in modulos
    assert "sao_textualmente_equivalentes" not in importados
    assert "sao_textualmente_equivalentes" not in chamados


# ---------------------------------------------------------------------------
# T6 — fragmento estático


def test_t6_fragmento_estatico_nao_gera_divergencia_artificial(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    estaticos = [
        f"{resposta['id']}/{fragmento['id']}"
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
        if not any(
            b["mecanismo"] == "RENDERIZADO" for b in fragmento["bindings"]
        )
    ]
    resultado = validar_consistencia_base(indice, base, textos)

    assert estaticos != []
    assert set(estaticos) & set(resultado.tokens_divergentes) == set()


def test_t6_template_estatico_e_validado_sem_nomes(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    """Um *placeholder* órfão num fragmento estático é erro de contrato."""
    estatico = next(
        f"{resposta['id']}/{fragmento['id']}"
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
        if not fragmento["bindings"]
    )
    corrompidos = dict(textos)
    corrompidos[estatico] = corrompidos[estatico] + " {{orfao}}"

    from casa77_sdr.response_placeholder import PlaceholderInvalido

    with pytest.raises(PlaceholderInvalido):
        validar_consistencia_base(indice, base, corrompidos)


# ---------------------------------------------------------------------------
# T7 — determinismo


def test_t7_duas_execucoes_dao_o_mesmo_resultado(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    primeiro = validar_consistencia_base(indice, base, textos)
    segundo = validar_consistencia_base(indice, base, textos)

    assert primeiro == segundo
    assert primeiro.status_por_fragmento == segundo.status_por_fragmento
    assert (
        primeiro.bindings_runtime_nao_avaliados
        == segundo.bindings_runtime_nao_avaliados
    )


def test_t7_ordem_fisica_dos_resultados(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    """A ordem pública é `Rxx` → fragmento → *binding*, sem `sorted`."""
    _, binding = _assertiva_booleana(indice, base)
    caminho = binding["caminho_yaml"]

    copia = copy.deepcopy(base)
    _, segmentos = analisar_caminho_yaml(caminho)
    _definir(copia, caminho, not resolver_caminho(copia, (False, segmentos)))

    resultado = validar_consistencia_base(indice, copia, textos)
    fisica = [t for t, _ in _bindings(indice)]
    posicoes = [fisica.index(d.token) for d in resultado.divergencias]

    assert posicoes == sorted(posicoes)


# ---------------------------------------------------------------------------
# T8 — imutabilidade das três entradas


def test_t8_nenhuma_entrada_e_mutada(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    antes = (
        copy.deepcopy(indice),
        copy.deepcopy(base),
        copy.deepcopy(textos),
    )

    validar_consistencia_base(indice, base, textos)

    assert (indice, base, textos) == antes


# ---------------------------------------------------------------------------
# T9 — `RUNTIME_AUTORITATIVO` fora do escopo factual


def test_t9_runtime_e_apenas_registrado(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    esperado = tuple(
        f"{token}.{binding['nome']}"
        for token, binding in _bindings(indice)
        if binding["origem"] == "RUNTIME_AUTORITATIVO"
    )
    resultado = validar_consistencia_base(indice, base, textos)

    assert len(esperado) == TOTAL_ASSERTIVA_RUNTIME
    assert resultado.bindings_runtime_nao_avaliados == esperado

    nomes_runtime = {
        binding["nome"]
        for _, binding in _bindings(indice)
        if binding["origem"] == "RUNTIME_AUTORITATIVO"
    }

    assert {d.binding for d in resultado.divergencias} & nomes_runtime == set()
    assert {
        r.binding for r in resultado.referentes_indisponiveis
    } & nomes_runtime == set()


# ---------------------------------------------------------------------------
# T10 — Classe I: exceção propagada, nunca resultado parcial


def test_t10_caminho_inexistente_propaga_nao_resolvido(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    _, binding = _renderizado_exclusivo(indice)

    copia = copy.deepcopy(base)
    _remover(copia, binding["caminho_yaml"])

    with pytest.raises(CaminhoYamlNaoResolvido):
        validar_consistencia_base(indice, copia, textos)


def test_t10_assertiva_nao_avaliavel_propaga(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    _, binding = _assertiva_booleana(indice, base)

    copia = copy.deepcopy(base)
    # Um terminal não booleano não tem veredito: `C-7` não o recusa e o
    # predicado não o julga.
    _definir(copia, binding["caminho_yaml"], 1)

    with pytest.raises(AssertivaNaoAvaliavel):
        validar_consistencia_base(indice, copia, textos)


def test_t10_indice_invalido_propaga(
    base: dict[str, Any], textos: dict[str, str]
) -> None:
    invalido = {
        "respostas": [
            {
                "id": "R01",
                "fragmentos": [
                    {"id": "F1", "status": "PARCIAL", "bindings": []}
                ],
            }
        ]
    }

    with pytest.raises(IndiceInvalido):
        validar_consistencia_base(invalido, base, textos)


def test_t10_texto_ausente_e_consistencia_nao_avaliavel(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    incompletos = dict(textos)
    incompletos.pop(next(iter(incompletos)))

    with pytest.raises(ConsistenciaNaoAvaliavel) as erro:
        validar_consistencia_base(indice, base, incompletos)

    assert str(erro.value) == "texto_ausente: textos"


@pytest.mark.parametrize("transporte", [None, (), [], "R01/F1", 0])
def test_t10_transporte_de_textos_invalido(
    indice: dict[str, Any], base: dict[str, Any], transporte: object
) -> None:
    with pytest.raises(ConsistenciaNaoAvaliavel) as erro:
        validar_consistencia_base(indice, base, transporte)

    assert str(erro.value) == "tipo_invalido: textos"


def test_t10_texto_de_tipo_invalido(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    corrompidos: dict[str, Any] = dict(textos)
    corrompidos[next(iter(corrompidos))] = None

    with pytest.raises(ConsistenciaNaoAvaliavel) as erro:
        validar_consistencia_base(indice, base, corrompidos)

    assert str(erro.value) == "tipo_invalido: textos.item"


def test_t10_classe_i_nao_devolve_resultado_parcial(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    _, binding = _renderizado_exclusivo(indice)

    copia = copy.deepcopy(base)
    _remover(copia, binding["caminho_yaml"])

    resultado = None
    try:
        resultado = validar_consistencia_base(indice, copia, textos)
    except CaminhoYamlNaoResolvido:
        pass

    assert resultado is None


# ---------------------------------------------------------------------------
# T11 — `itera_sobre`: composição das fronteiras existentes


_INDICE_ITERA: dict[str, Any] = {
    "respostas": [
        {
            "id": "R01",
            "fragmentos": [
                {
                    "id": "F1",
                    "status": "APROVADO",
                    "itera_sobre": "colecao.itens",
                    "bindings": [
                        {
                            "nome": "rotulo",
                            "mecanismo": "RENDERIZADO",
                            "origem": "YAML",
                            "caminho_yaml": "@.rotulo",
                            "placeholder": "{{rotulo}}",
                            "formato": "texto",
                        }
                    ],
                }
            ],
        }
    ]
}

_TEXTOS_ITERA = {"R01/F1": "item {{rotulo}}"}


def test_t11_caminho_relativo_resolve_por_item() -> None:
    base = {"colecao": {"itens": [{"rotulo": "a"}, {"rotulo": "b"}]}}

    resultado = validar_consistencia_base(_INDICE_ITERA, base, _TEXTOS_ITERA)

    assert resultado.divergencias == ()
    assert resultado.referentes_indisponiveis == ()
    assert resultado.status_por_fragmento == (("R01/F1", "APROVADO"),)


def test_t11_item_com_referente_indisponivel() -> None:
    base = {"colecao": {"itens": [{"rotulo": "a"}, {"rotulo": None}]}}

    resultado = validar_consistencia_base(_INDICE_ITERA, base, _TEXTOS_ITERA)

    assert resultado.divergencias == ()
    assert len(resultado.referentes_indisponiveis) == 1
    assert resultado.referentes_indisponiveis[0].referente == "@.rotulo"


def test_t11_item_com_formato_inaplicavel() -> None:
    base = {"colecao": {"itens": [{"rotulo": "a"}, {"rotulo": 1}]}}

    resultado = validar_consistencia_base(_INDICE_ITERA, base, _TEXTOS_ITERA)

    assert len(resultado.divergencias) == 1
    assert (
        resultado.divergencias[0].categoria
        == CategoriaDivergencia.FORMATO_INAPLICAVEL
    )
    assert resultado.tokens_divergentes == ("R01/F1",)


def test_t11_colecao_vazia_nao_avalia_nem_diverge() -> None:
    base = {"colecao": {"itens": []}}

    resultado = validar_consistencia_base(_INDICE_ITERA, base, _TEXTOS_ITERA)

    assert resultado.divergencias == ()
    assert resultado.referentes_indisponiveis == ()


def test_t11_contexto_invalido_propaga_nao_resolvido() -> None:
    """`itera_sobre` que não resolve para coleção é Classe I, não divergência."""
    base = {"colecao": {"itens": {"rotulo": "a"}}}

    with pytest.raises(CaminhoYamlNaoResolvido):
        validar_consistencia_base(_INDICE_ITERA, base, _TEXTOS_ITERA)


# ---------------------------------------------------------------------------
# IT — `itera_sobre`: a cardinalidade da avaliação vem do **caminho**


def _fragmento_iterado(bindings: list[dict[str, Any]]) -> dict[str, Any]:
    """Índice sintético mínimo com um único fragmento que declara `itera_sobre`."""
    return {
        "respostas": [
            {
                "id": "R01",
                "fragmentos": [
                    {
                        "id": "F1",
                        "status": "APROVADO",
                        "itera_sobre": "colecao.itens",
                        "bindings": bindings,
                    }
                ],
            }
        ]
    }


_BINDING_ABSOLUTO = {
    "nome": "rotulo_global",
    "mecanismo": "RENDERIZADO",
    "origem": "YAML",
    "caminho_yaml": "fato.rotulo",
    "placeholder": "{{rotulo_global}}",
    "formato": "texto",
}

_BINDING_RELATIVO = {
    "nome": "rotulo",
    "mecanismo": "RENDERIZADO",
    "origem": "YAML",
    "caminho_yaml": "@.rotulo",
    "placeholder": "{{rotulo}}",
    "formato": "texto",
}

_BINDING_ASSERTIVA_ABSOLUTA = {
    "nome": "fato_sustentado",
    "mecanismo": "ASSERTIVA",
    "origem": "YAML",
    "caminho_yaml": "fato.ativo",
    "predicado": "EH_VERDADEIRO",
}


def test_it1_absoluto_com_colecao_vazia_continua_sendo_avaliado() -> None:
    """Coleção vazia **não** dispensa a avaliação de um `RENDERIZADO` absoluto."""
    indice = _fragmento_iterado([_BINDING_ABSOLUTO])
    base = {"colecao": {"itens": []}, "fato": {"rotulo": None}}

    resultado = validar_consistencia_base(
        indice, base, {"R01/F1": "item {{rotulo_global}}"}
    )

    assert resultado.divergencias == ()
    assert len(resultado.referentes_indisponiveis) == 1
    assert resultado.referentes_indisponiveis[0].referente == "fato.rotulo"
    assert resultado.referentes_indisponiveis[0].binding == "rotulo_global"


def test_it2_assertiva_absoluta_com_colecao_vazia_diverge() -> None:
    """Um fato global não depende da cardinalidade da coleção iterada."""
    indice = _fragmento_iterado([_BINDING_ASSERTIVA_ABSOLUTA])
    base = {"colecao": {"itens": []}, "fato": {"ativo": False}}

    resultado = validar_consistencia_base(indice, base, {"R01/F1": "texto fixo"})

    assert len(resultado.divergencias) == 1
    assert (
        resultado.divergencias[0].categoria == CategoriaDivergencia.ASSERTIVA_FALSA
    )
    assert resultado.divergencias[0].referente == "fato.ativo"
    assert resultado.tokens_divergentes == ("R01/F1",)
    assert resultado.referentes_indisponiveis == ()


def test_it3_relativo_com_colecao_vazia_nao_tem_item_a_avaliar() -> None:
    """Sem item corrente, o *binding* relativo não é avaliado — o absoluto é."""
    indice = _fragmento_iterado([_BINDING_ABSOLUTO, _BINDING_RELATIVO])
    base = {"colecao": {"itens": []}, "fato": {"rotulo": "a"}}

    resultado = validar_consistencia_base(
        indice, base, {"R01/F1": "{{rotulo_global}} {{rotulo}}"}
    )

    assert resultado.divergencias == ()
    assert resultado.referentes_indisponiveis == ()
    assert resultado.tokens_divergentes == ()


def test_it4_absoluto_nao_e_multiplicado_por_item() -> None:
    """Vários itens não multiplicam o registro de um *binding* absoluto."""
    indice = _fragmento_iterado([_BINDING_ABSOLUTO])
    base = {"colecao": {"itens": [{}, {}, {}]}, "fato": {"rotulo": 1}}

    resultado = validar_consistencia_base(
        indice, base, {"R01/F1": "item {{rotulo_global}}"}
    )

    assert len(resultado.divergencias) == 1
    assert (
        resultado.divergencias[0].categoria
        == CategoriaDivergencia.FORMATO_INAPLICAVEL
    )
    assert resultado.divergencias[0].binding == "rotulo_global"
    assert resultado.tokens_divergentes == ("R01/F1",)
    assert resultado.referentes_indisponiveis == ()


# ---------------------------------------------------------------------------
# T12 — segurança da saída


def test_t12_dtos_carregam_apenas_identidade_e_referente(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    """Nenhum DTO expõe valor factual, `repr`, texto, *template* ou mensagem."""
    token, binding = _assertiva_booleana(indice, base)
    caminho = binding["caminho_yaml"]

    copia = copy.deepcopy(base)
    _, segmentos = analisar_caminho_yaml(caminho)
    valor_novo = not resolver_caminho(copia, (False, segmentos))
    _definir(copia, caminho, valor_novo)
    _definir(copia, _renderizado_exclusivo(indice)[1]["caminho_yaml"], None)

    resultado = validar_consistencia_base(indice, copia, textos)
    conhecidos = _identificadores_estruturais(indice)
    emitidos = resultado.divergencias + resultado.referentes_indisponiveis

    assert emitidos != ()

    for dto in emitidos:
        campos = tuple(type(dto).__dataclass_fields__)

        assert campos[: len(_CAMPOS_DE_IDENTIDADE)] == _CAMPOS_DE_IDENTIDADE

        for nome in _CAMPOS_DE_IDENTIDADE:
            valor = getattr(dto, nome)

            assert isinstance(valor, str)
            assert valor in conhecidos
            assert valor != repr(valor_novo)
            assert valor not in textos.values()


def test_t12_dtos_sao_congelados_e_sem_dicionario(
    indice: dict[str, Any], base: dict[str, Any], textos: dict[str, str]
) -> None:
    token, binding = _renderizado_exclusivo(indice)

    copia = copy.deepcopy(base)
    _definir(copia, binding["caminho_yaml"], None)

    resultado = validar_consistencia_base(indice, copia, textos)
    registro = _dto_do_binding(
        resultado.referentes_indisponiveis, token, binding["nome"]
    )

    assert not hasattr(registro, "__dict__")
    with pytest.raises(Exception):
        registro.token = "R01/F1"  # type: ignore[misc]

    assert not hasattr(resultado, "__dict__")
    with pytest.raises(Exception):
        resultado.divergencias = ()  # type: ignore[misc]


def test_t12_vocabulario_de_divergencia_e_fechado() -> None:
    assert [membro.value for membro in CategoriaDivergencia] == [
        "ASSERTIVA_FALSA",
        "FORMATO_INAPLICAVEL",
    ]
    assert issubclass(Divergencia, object)


def _identificadores_estruturais(indice: dict[str, Any]) -> set[str]:
    """Tudo o que um DTO pode legitimamente conter — e nada além disso."""
    conhecidos: set[str] = set()
    for resposta in indice["respostas"]:
        rxx = resposta["id"]
        conhecidos.add(rxx)
        for fragmento in resposta["fragmentos"]:
            conhecidos.add(fragmento["id"])
            conhecidos.add(f"{rxx}/{fragmento['id']}")
            for binding in fragmento["bindings"]:
                conhecidos.add(binding["nome"])
                conhecidos.add(binding["mecanismo"])
                conhecidos.add(binding["origem"])
                if "caminho_yaml" in binding:
                    conhecidos.add(binding["caminho_yaml"])
    return conhecidos
