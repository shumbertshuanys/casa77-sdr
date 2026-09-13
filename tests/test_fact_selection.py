"""`SeletorFatos` — materialização dos fatos dos fragmentos já autorizados.

Esta suíte exercita a fronteira sobre **estruturas sintéticas mínimas** e, uma
única vez, sobre os **artefatos versionados reais**. **Zero valor comercial** é
reproduzido: nenhum preço, capacidade, horário, prazo, percentual, quantidade ou
frase aprovada aparece no código. Os cenários sintéticos usam valores neutros,
sem correspondência com `knowledge/casa77.yaml`, e o cenário de corpus é
**inteiramente mecânico** — as expectativas são derivadas do próprio índice em
tempo de execução, e **nenhum valor é congelado**.

O teste de corpus fornece os tokens do índice como **stub de chamador**,
exclusivamente para exercitar a fronteira. Ele **não afirma** que os 37 tokens
estejam autorizados num mesmo ciclo: a autorização pertence a S2-D8.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest
import yaml

from casa77_sdr.fact_selection import (
    FatoAutorizado,
    ResultadoSelecaoFatos,
    SelecaoNaoAvaliavel,
    TextoAutorizado,
    materializar_fatos_autorizados,
)
from casa77_sdr.response_emittable_text import extrair_textos_emitiveis
from casa77_sdr.response_format import FormatoInaplicavel
from casa77_sdr.response_index import IndiceInvalido
from casa77_sdr.response_index_load import carregar_indice
from casa77_sdr.response_index_tokens import (
    ProjecaoDeIdentidadeInvalida,
    derivar_tokens_do_indice,
)
from casa77_sdr.response_null_pending import ValorNuloOuPendente
from casa77_sdr.response_yaml_resolve import CaminhoYamlNaoResolvido

RAIZ = Path(__file__).resolve().parents[1]
INDICE = RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml"
MARKDOWN = RAIZ / "knowledge" / "respostas-aprovadas.md"
BASE_FACTUAL = RAIZ / "knowledge" / "casa77.yaml"
MODULO_SF = RAIZ / "src" / "casa77_sdr" / "fact_selection.py"

# Cardinalidade estrutural do corpus corrente — contagem, não dado comercial.
TOTAL_FRAGMENTOS = 37

# Único rótulo de status usado nos cenários sintéticos. Ele existe apenas para
# satisfazer `validar_indice`: esta fronteira **não** lê status, e nada aqui
# afirma que um fragmento de outro status seria autorizado.
_STATUS_SINTETICO = "APROVADO"


# ---------------------------------------------------------------------------
# Construtores de cenário — sintéticos, mecânicos, sem literal comercial


def _renderizado(
    nome: str,
    caminho: str,
    formato: str = "texto",
) -> dict[str, Any]:
    return {
        "nome": nome,
        "mecanismo": "RENDERIZADO",
        "origem": "YAML",
        "caminho_yaml": caminho,
        "placeholder": "{{" + nome + "}}",
        "formato": formato,
    }


def _assertiva(
    nome: str,
    caminho: str,
    origem: str = "YAML",
) -> dict[str, Any]:
    binding: dict[str, Any] = {
        "nome": nome,
        "mecanismo": "ASSERTIVA",
        "origem": origem,
        "predicado": "EH_VERDADEIRO",
    }
    if origem == "YAML":
        binding["caminho_yaml"] = caminho
    else:
        binding["fato_runtime"] = caminho
    return binding


def _fragmento(
    fragmento_id: str,
    bindings: list[dict[str, Any]],
    itera_sobre: str | None = None,
) -> dict[str, Any]:
    fragmento: dict[str, Any] = {
        "id": fragmento_id,
        "status": _STATUS_SINTETICO,
        "bindings": bindings,
    }
    if itera_sobre is not None:
        fragmento["itera_sobre"] = itera_sobre
    return fragmento


def _indice_de(respostas: list[tuple[str, list[dict[str, Any]]]]) -> dict[str, Any]:
    return {
        "respostas": [
            {"id": rxx, "fragmentos": fragmentos} for rxx, fragmentos in respostas
        ]
    }


def _indice_simples(
    bindings: list[dict[str, Any]],
    itera_sobre: str | None = None,
) -> dict[str, Any]:
    return _indice_de([("R01", [_fragmento("F1", bindings, itera_sobre)])])


# Um nome do vocabulário fechado de fato runtime (`C-A2-V`), grafado como na
# suíte do corpus. Ele é **estrutural**, não comercial, e a autoridade continua
# sendo `validar_indice`: um nome fora do vocabulário falharia neste próprio
# cenário.
_FATO_RUNTIME = "consulta_calendario_valida"


# ---------------------------------------------------------------------------
# SF-T1 — caso simples


def test_sf_t1_um_renderizado_produz_um_fato_e_um_texto() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])
    base = {"fato": {"rotulo": "alfa"}}

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "prefixo {{rotulo}}"}, ("R01/F1",)
    )

    assert isinstance(resultado, ResultadoSelecaoFatos)
    assert len(resultado.fatos) == 1
    assert len(resultado.textos_autorizados) == 1

    fato = resultado.fatos[0]
    assert fato == FatoAutorizado(
        token="R01/F1",
        rxx="R01",
        fragmento_id="F1",
        binding="rotulo",
        referente="fato.rotulo",
        formato="texto",
        valor_formatado="alfa",
    )

    texto = resultado.textos_autorizados[0]
    assert texto == TextoAutorizado(
        token="R01/F1", rxx="R01", fragmento_id="F1", texto="prefixo {{rotulo}}"
    )


def test_sf_t1_tupla_vazia_e_sucesso_vazio() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])

    resultado = materializar_fatos_autorizados(
        indice, {"fato": {"rotulo": "alfa"}}, {"R01/F1": "x"}, ()
    )

    assert resultado.fatos == ()
    assert resultado.textos_autorizados == ()


# ---------------------------------------------------------------------------
# SF-T2 — o valor corrente da base, nunca um snapshot


def test_sf_t2_saida_reflete_o_valor_corrente_da_base() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])
    textos = {"R01/F1": "prefixo {{rotulo}}"}

    antes = materializar_fatos_autorizados(
        indice, {"fato": {"rotulo": "alfa"}}, textos, ("R01/F1",)
    )
    depois = materializar_fatos_autorizados(
        indice, {"fato": {"rotulo": "beta"}}, textos, ("R01/F1",)
    )

    assert antes.fatos[0].valor_formatado == "alfa"
    assert depois.fatos[0].valor_formatado == "beta"
    # A proveniência não muda: o que muda é apenas o fato corrente.
    assert antes.fatos[0].referente == depois.fatos[0].referente
    assert antes.textos_autorizados == depois.textos_autorizados


# ---------------------------------------------------------------------------
# SF-T3 — fragmento estático


def test_sf_t3_fragmento_estatico_produz_zero_fatos_e_um_texto() -> None:
    indice = _indice_simples([])
    base = {"fato": {"rotulo": "alfa"}}

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "texto integralmente estatico"}, ("R01/F1",)
    )

    assert resultado.fatos == ()
    assert len(resultado.textos_autorizados) == 1
    assert resultado.textos_autorizados[0].texto == "texto integralmente estatico"


# ---------------------------------------------------------------------------
# SF-T4 — formato inaplicável propaga intacto


def test_sf_t4_formato_inaplicavel_propaga() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo", "inteiro")])
    base = {"fato": {"rotulo": "nao_e_inteiro"}}

    with pytest.raises(FormatoInaplicavel):
        materializar_fatos_autorizados(
            indice, base, {"R01/F1": "{{rotulo}}"}, ("R01/F1",)
        )


def test_sf_t4_formato_inaplicavel_nao_vira_resultado() -> None:
    """A falha fecha: nenhum resultado parcial é devolvido."""
    indice = _indice_de(
        [
            (
                "R01",
                [
                    _fragmento("F1", [_renderizado("bom", "fato.rotulo")]),
                    _fragmento("F2", [_renderizado("ruim", "fato.rotulo", "inteiro")]),
                ],
            )
        ]
    )
    base = {"fato": {"rotulo": "alfa"}}
    textos = {"R01/F1": "{{bom}}", "R01/F2": "{{ruim}}"}

    resultado = None
    with pytest.raises(FormatoInaplicavel):
        resultado = materializar_fatos_autorizados(
            indice, base, textos, ("R01/F1", "R01/F2")
        )

    assert resultado is None


# ---------------------------------------------------------------------------
# SF-T5 — `C-7` propaga intacto


@pytest.mark.parametrize(
    "terminal",
    [None, {"status": "pendente"}],
    ids=["nulo", "pendente"],
)
def test_sf_t5_c7_propaga_intacto(terminal: object) -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])
    base = {"fato": {"rotulo": terminal}}

    with pytest.raises(ValorNuloOuPendente):
        materializar_fatos_autorizados(
            indice, base, {"R01/F1": "{{rotulo}}"}, ("R01/F1",)
        )


def test_sf_t5_caminho_inexistente_propaga_nao_resolvido() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.inexistente")])

    with pytest.raises(CaminhoYamlNaoResolvido):
        materializar_fatos_autorizados(
            indice, {"fato": {"rotulo": "alfa"}}, {"R01/F1": "{{rotulo}}"}, ("R01/F1",)
        )


# ---------------------------------------------------------------------------
# SF-T6 — status está inteiramente fora desta fronteira (prova estrutural)


def _arvore_do_modulo() -> ast.Module:
    return ast.parse(MODULO_SF.read_text(encoding="utf-8"))


def _modulos_importados() -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(_arvore_do_modulo()):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module is not None:
            importados.add(no.module)
            importados.update(f"{no.module}.{alias.name}" for alias in no.names)
    return importados


def _nomes_chamados() -> set[str]:
    chamados: set[str] = set()
    for no in ast.walk(_arvore_do_modulo()):
        if not isinstance(no, ast.Call):
            continue
        alvo = no.func
        if isinstance(alvo, ast.Name):
            chamados.add(alvo.id)
        elif isinstance(alvo, ast.Attribute):
            chamados.add(alvo.attr)
    return chamados


def test_sf_t6_modulo_nao_importa_a_fronteira_de_status() -> None:
    importados = _modulos_importados()

    assert not any("response_index_status" in nome for nome in importados)
    assert not any("consultar_status" in nome for nome in importados)


def test_sf_t6_modulo_nao_chama_consulta_de_status() -> None:
    assert "consultar_status" not in _nomes_chamados()


def test_sf_t6_modulo_nao_contem_vocabulario_de_status() -> None:
    fonte = MODULO_SF.read_text(encoding="utf-8")

    for rotulo in ("APROVADO", "AGUARDA_APROVACAO", "BLOQUEADO"):
        assert rotulo not in fonte

    # Zero *fallback* de status: a chave sequer é lida.
    assert '"status"' not in fonte
    assert "'status'" not in fonte


# ---------------------------------------------------------------------------
# SF-T7 — a ordem recebida é preservada, sem preferência própria


def _indice_de_tres() -> dict[str, Any]:
    return _indice_de(
        [
            ("R01", [_fragmento("F1", [_renderizado("a", "fato.a")])]),
            ("R02", [_fragmento("F1", [_renderizado("b", "fato.b")])]),
            ("R03", [_fragmento("F1", [_renderizado("c", "fato.c")])]),
        ]
    )


_BASE_DE_TRES = {"fato": {"a": "alfa", "b": "beta", "c": "gama"}}
_TEXTOS_DE_TRES = {
    "R01/F1": "{{a}}",
    "R02/F1": "{{b}}",
    "R03/F1": "{{c}}",
}


@pytest.mark.parametrize(
    "ordem",
    [
        ("R01/F1", "R02/F1", "R03/F1"),
        ("R03/F1", "R01/F1", "R02/F1"),
        ("R02/F1", "R03/F1"),
    ],
    ids=["fisica", "embaralhada", "subconjunto"],
)
def test_sf_t7_saida_acompanha_a_ordem_recebida(ordem: tuple[str, ...]) -> None:
    resultado = materializar_fatos_autorizados(
        _indice_de_tres(), _BASE_DE_TRES, _TEXTOS_DE_TRES, ordem
    )

    assert tuple(t.token for t in resultado.textos_autorizados) == ordem
    assert tuple(f.token for f in resultado.fatos) == ordem


def test_sf_t7_ordem_dos_bindings_e_a_ordem_fisica() -> None:
    indice = _indice_simples(
        [
            _renderizado("terceiro", "fato.c"),
            _renderizado("primeiro", "fato.a"),
            _renderizado("segundo", "fato.b"),
        ]
    )

    resultado = materializar_fatos_autorizados(
        indice, _BASE_DE_TRES, {"R01/F1": "x"}, ("R01/F1",)
    )

    assert tuple(f.binding for f in resultado.fatos) == (
        "terceiro",
        "primeiro",
        "segundo",
    )


# ---------------------------------------------------------------------------
# SF-T8 — mesmo referente, proveniências distintas, zero deduplicação


def test_sf_t8_dois_bindings_no_mesmo_referente_produzem_dois_fatos() -> None:
    indice = _indice_simples(
        [
            _renderizado("primeiro", "fato.rotulo"),
            _renderizado("segundo", "fato.rotulo"),
        ]
    )

    resultado = materializar_fatos_autorizados(
        indice, {"fato": {"rotulo": "alfa"}}, {"R01/F1": "x"}, ("R01/F1",)
    )

    assert len(resultado.fatos) == 2
    assert {f.binding for f in resultado.fatos} == {"primeiro", "segundo"}
    assert {f.referente for f in resultado.fatos} == {"fato.rotulo"}
    assert {f.valor_formatado for f in resultado.fatos} == {"alfa"}


def test_sf_t8_dois_fragmentos_no_mesmo_referente_produzem_dois_fatos() -> None:
    indice = _indice_de(
        [
            (
                "R01",
                [
                    _fragmento("F1", [_renderizado("rotulo", "fato.rotulo")]),
                    _fragmento("F2", [_renderizado("rotulo", "fato.rotulo")]),
                ],
            )
        ]
    )
    textos = {"R01/F1": "x", "R01/F2": "y"}

    resultado = materializar_fatos_autorizados(
        indice, {"fato": {"rotulo": "alfa"}}, textos, ("R01/F1", "R01/F2")
    )

    assert tuple(f.token for f in resultado.fatos) == ("R01/F1", "R01/F2")
    assert tuple(f.fragmento_id for f in resultado.fatos) == ("F1", "F2")


# ---------------------------------------------------------------------------
# SF-T9 — `itera_sobre`: a cardinalidade vem do caminho


_ITERA = "colecao.itens"


def test_sf_t9_relativo_materializa_um_fato_por_item() -> None:
    indice = _indice_simples([_renderizado("rotulo", "@.rotulo")], itera_sobre=_ITERA)
    base = {"colecao": {"itens": [{"rotulo": "alfa"}, {"rotulo": "beta"}]}}

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "{{rotulo}}"}, ("R01/F1",)
    )

    assert tuple(f.valor_formatado for f in resultado.fatos) == ("alfa", "beta")
    assert {f.binding for f in resultado.fatos} == {"rotulo"}
    assert len(resultado.textos_autorizados) == 1


def test_sf_t9_absoluto_em_fragmento_iterado_materializa_uma_vez() -> None:
    indice = _indice_simples(
        [_renderizado("raiz_rotulo", "fato.rotulo")], itera_sobre=_ITERA
    )
    base = {"colecao": {"itens": [{}, {}, {}]}, "fato": {"rotulo": "alfa"}}

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "{{raiz_rotulo}}"}, ("R01/F1",)
    )

    assert len(resultado.fatos) == 1
    assert resultado.fatos[0].valor_formatado == "alfa"


def test_sf_t9_absoluto_continua_com_colecao_vazia() -> None:
    indice = _indice_simples(
        [_renderizado("raiz_rotulo", "fato.rotulo")], itera_sobre=_ITERA
    )
    base = {"colecao": {"itens": []}, "fato": {"rotulo": "alfa"}}

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "{{raiz_rotulo}}"}, ("R01/F1",)
    )

    assert len(resultado.fatos) == 1
    assert resultado.fatos[0].valor_formatado == "alfa"


def test_sf_t9_relativo_com_colecao_vazia_produz_zero_ocorrencias() -> None:
    indice = _indice_simples([_renderizado("rotulo", "@.rotulo")], itera_sobre=_ITERA)
    base = {"colecao": {"itens": []}}

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "{{rotulo}}"}, ("R01/F1",)
    )

    assert resultado.fatos == ()
    assert len(resultado.textos_autorizados) == 1


def test_sf_t9_absoluto_e_relativo_coexistem_na_ordem_fisica() -> None:
    indice = _indice_simples(
        [
            _renderizado("raiz_rotulo", "fato.rotulo"),
            _renderizado("rotulo", "@.rotulo"),
        ],
        itera_sobre=_ITERA,
    )
    base = {
        "colecao": {"itens": [{"rotulo": "alfa"}, {"rotulo": "beta"}]},
        "fato": {"rotulo": "gama"},
    }

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "x"}, ("R01/F1",)
    )

    assert tuple(
        (f.binding, f.valor_formatado) for f in resultado.fatos
    ) == (
        ("raiz_rotulo", "gama"),
        ("rotulo", "alfa"),
        ("rotulo", "beta"),
    )


# ---------------------------------------------------------------------------
# SF-T10 — runtime e `ASSERTIVA` não materializam fato


def test_sf_t10_assertiva_yaml_nao_produz_fato() -> None:
    indice = _indice_simples(
        [
            _renderizado("rotulo", "fato.rotulo"),
            _assertiva("confere", "fato.ativo"),
        ]
    )
    # A `ASSERTIVA` resolveria para um predicado **falso**, e ainda assim nada
    # sai daqui: esta fronteira não é segunda autoridade de consistência.
    base = {"fato": {"rotulo": "alfa", "ativo": False}}

    resultado = materializar_fatos_autorizados(
        indice, base, {"R01/F1": "{{rotulo}}"}, ("R01/F1",)
    )

    assert tuple(f.binding for f in resultado.fatos) == ("rotulo",)


def test_sf_t10_fato_runtime_nao_produz_fato_nem_verdade_operacional() -> None:
    indice = _indice_simples(
        [_assertiva("runtime", _FATO_RUNTIME, origem="RUNTIME_AUTORITATIVO")]
    )

    resultado = materializar_fatos_autorizados(
        indice, {}, {"R01/F1": "texto estatico"}, ("R01/F1",)
    )

    assert resultado.fatos == ()
    assert len(resultado.textos_autorizados) == 1


def test_sf_t10_assinatura_nao_recebe_snapshot_de_runtime() -> None:
    import inspect

    parametros = tuple(
        inspect.signature(materializar_fatos_autorizados).parameters
    )

    assert parametros == ("indice", "base", "textos", "fragmentos_autorizados")


# ---------------------------------------------------------------------------
# SF-T11 — determinismo


def test_sf_t11_duas_execucoes_dao_o_mesmo_resultado() -> None:
    indice = _indice_de_tres()
    ordem = ("R02/F1", "R01/F1", "R03/F1")

    primeira = materializar_fatos_autorizados(
        indice, _BASE_DE_TRES, _TEXTOS_DE_TRES, ordem
    )
    segunda = materializar_fatos_autorizados(
        indice, _BASE_DE_TRES, _TEXTOS_DE_TRES, ordem
    )

    assert primeira == segunda


# ---------------------------------------------------------------------------
# SF-T12 — imutabilidade das quatro entradas


def test_sf_t12_nenhuma_entrada_e_mutada() -> None:
    indice = _indice_simples(
        [
            _renderizado("raiz_rotulo", "fato.rotulo"),
            _renderizado("rotulo", "@.rotulo"),
        ],
        itera_sobre=_ITERA,
    )
    base = {
        "colecao": {"itens": [{"rotulo": "alfa"}, {"rotulo": "beta"}]},
        "fato": {"rotulo": "gama"},
    }
    textos = {"R01/F1": "{{raiz_rotulo}} {{rotulo}}"}
    autorizados = ("R01/F1",)

    copias = (
        copy.deepcopy(indice),
        copy.deepcopy(base),
        copy.deepcopy(textos),
        copy.deepcopy(autorizados),
    )

    materializar_fatos_autorizados(indice, base, textos, autorizados)

    assert (indice, base, textos, autorizados) == copias


# ---------------------------------------------------------------------------
# SF-T13 — isolamento de S2-D8 na superfície funcional


_VOCABULARIO_DE_S2D8 = (
    "E09",
    "handoff",
    "cobertura",
    "pendencia_impeditiva",
    "resposta_aprovada_disponivel",
    "CAMPO_INDISPONIVEL",
    "SEM_RESPOSTA_APROVADA_EMITIVEL",
)


def test_sf_t13_modulo_nao_carrega_vocabulario_de_s2d8() -> None:
    fonte = MODULO_SF.read_text(encoding="utf-8").casefold()

    for termo in _VOCABULARIO_DE_S2D8:
        assert termo.casefold() not in fonte


def test_sf_t13_superficie_publica_e_minima() -> None:
    import casa77_sdr.fact_selection as modulo

    assert sorted(modulo.__all__) == [
        "FatoAutorizado",
        "ResultadoSelecaoFatos",
        "SelecaoNaoAvaliavel",
        "TextoAutorizado",
        "materializar_fatos_autorizados",
    ]
    assert not hasattr(modulo, "selecionar_fatos")


def test_sf_t13_saida_tem_exatamente_dois_campos() -> None:
    assert ResultadoSelecaoFatos.__slots__ == ("fatos", "textos_autorizados")


# ---------------------------------------------------------------------------
# SF-T14 — zero renderer


def test_sf_t14_texto_com_placeholder_permanece_identico() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])
    template = "prefixo {{rotulo}} sufixo"

    resultado = materializar_fatos_autorizados(
        indice, {"fato": {"rotulo": "alfa"}}, {"R01/F1": template}, ("R01/F1",)
    )

    assert resultado.textos_autorizados[0].texto == template
    assert "{{rotulo}}" in resultado.textos_autorizados[0].texto
    assert "alfa" not in resultado.textos_autorizados[0].texto


def test_sf_t14_modulo_nao_substitui_nem_formata_template() -> None:
    chamados = _nomes_chamados()

    assert "replace" not in chamados
    assert "format" not in chamados
    assert "format_map" not in chamados
    assert "join" not in chamados


def test_sf_t14_modulo_nao_importa_a_gramatica_de_placeholder() -> None:
    importados = _modulos_importados()

    assert not any("decompor_template" in nome for nome in importados)
    assert not any("response_placeholder" in nome for nome in importados)
    assert not any("avaliar_assertiva" in nome for nome in importados)
    assert not any("response_assertion" in nome for nome in importados)


# ---------------------------------------------------------------------------
# SF-T15 — segurança do `repr` dos DTOs


def test_sf_t15_repr_do_fato_nao_expoe_o_valor_formatado() -> None:
    fato = FatoAutorizado(
        token="R01/F1",
        rxx="R01",
        fragmento_id="F1",
        binding="rotulo",
        referente="fato.rotulo",
        formato="texto",
        valor_formatado="segredo_comercial_sintetico",
    )

    texto = repr(fato)

    assert "segredo_comercial_sintetico" not in texto
    assert "valor_formatado" not in texto
    # A proveniência continua legível.
    assert "R01/F1" in texto
    assert "fato.rotulo" in texto


def test_sf_t15_repr_do_texto_nao_expoe_a_redacao() -> None:
    autorizado = TextoAutorizado(
        token="R01/F1",
        rxx="R01",
        fragmento_id="F1",
        texto="redacao_aprovada_sintetica",
    )

    texto = repr(autorizado)

    assert "redacao_aprovada_sintetica" not in texto
    assert "texto=" not in texto
    assert "R01/F1" in texto


def test_sf_t15_dtos_sao_congelados_e_sem_dicionario() -> None:
    fato = FatoAutorizado("R01/F1", "R01", "F1", "n", "fato.rotulo", "texto", "v")
    autorizado = TextoAutorizado("R01/F1", "R01", "F1", "t")
    resultado = ResultadoSelecaoFatos(fatos=(fato,), textos_autorizados=(autorizado,))

    for dto in (fato, autorizado, resultado):
        assert not hasattr(dto, "__dict__")
        with pytest.raises(Exception):
            dto.token = "outro"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SF-T16 — erros próprios, sem eco de conteúdo


def _mensagem(excecao: pytest.ExceptionInfo[SelecaoNaoAvaliavel]) -> str:
    return str(excecao.value)


def test_sf_t16_token_desconhecido() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])

    with pytest.raises(SelecaoNaoAvaliavel) as erro:
        materializar_fatos_autorizados(
            indice, {"fato": {"rotulo": "a"}}, {"R01/F1": "x"}, ("R99/F1",)
        )

    assert _mensagem(erro) == "token_desconhecido: fragmentos_autorizados.item"
    assert "R99" not in _mensagem(erro)


def test_sf_t16_duplicidade() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])

    with pytest.raises(SelecaoNaoAvaliavel) as erro:
        materializar_fatos_autorizados(
            indice, {"fato": {"rotulo": "a"}}, {"R01/F1": "x"}, ("R01/F1", "R01/F1")
        )

    assert _mensagem(erro) == "duplicidade: fragmentos_autorizados.item"


def test_sf_t16_texto_ausente() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])

    with pytest.raises(SelecaoNaoAvaliavel) as erro:
        materializar_fatos_autorizados(
            indice, {"fato": {"rotulo": "a"}}, {}, ("R01/F1",)
        )

    assert _mensagem(erro) == "texto_ausente: textos"


@pytest.mark.parametrize(
    ("transporte", "localizador"),
    [
        (["R01/F1"], "fragmentos_autorizados"),
        ({"R01/F1"}, "fragmentos_autorizados"),
        (("R01/F1", 0), "fragmentos_autorizados.item"),
    ],
    ids=["lista", "conjunto", "item_nao_str"],
)
def test_sf_t16_tipo_invalido_dos_autorizados(
    transporte: object, localizador: str
) -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])

    with pytest.raises(SelecaoNaoAvaliavel) as erro:
        materializar_fatos_autorizados(
            indice, {"fato": {"rotulo": "a"}}, {"R01/F1": "x"}, transporte
        )

    assert _mensagem(erro) == f"tipo_invalido: {localizador}"


@pytest.mark.parametrize(
    ("textos", "localizador"),
    [
        ([("R01/F1", "x")], "textos"),
        ({"R01/F1": 0}, "textos.item"),
    ],
    ids=["transporte", "item"],
)
def test_sf_t16_tipo_invalido_dos_textos(textos: object, localizador: str) -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])

    with pytest.raises(SelecaoNaoAvaliavel) as erro:
        materializar_fatos_autorizados(
            indice, {"fato": {"rotulo": "a"}}, textos, ("R01/F1",)
        )

    assert _mensagem(erro) == f"tipo_invalido: {localizador}"


def test_sf_t16_mensagens_nunca_ecoam_conteudo() -> None:
    indice = _indice_simples([_renderizado("rotulo", "fato.rotulo")])

    with pytest.raises(SelecaoNaoAvaliavel) as erro:
        materializar_fatos_autorizados(
            indice,
            {"fato": {"rotulo": "a"}},
            {"R01/F1": "conteudo_sensivel_sintetico"},
            ("R01/F1", "R01/F1"),
        )

    assert "conteudo_sensivel_sintetico" not in _mensagem(erro)


def test_sf_t16_portoes_do_indice_propagam_intactos() -> None:
    with pytest.raises(IndiceInvalido):
        materializar_fatos_autorizados({"respostas": [{}]}, {}, {}, ())

    # `validar_indice` aceita `id` como `str` nao vazia; `C-A5-I3` exige a
    # forma fechada `F<n>`. Um `id` fora dela passa o primeiro portao e falha
    # no segundo — e a excecao da fronteira de origem atravessa intacta.
    fora_da_gramatica = _indice_de([("R01", [_fragmento("X1", [])])])
    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        materializar_fatos_autorizados(fora_da_gramatica, {}, {}, ())


# ---------------------------------------------------------------------------
# SF-T17 — corpus físico, inteiramente mecânico
#
# Este cenário fornece os tokens do índice como **stub de chamador**. Ele NÃO
# afirma que os 37 fragmentos estejam autorizados num mesmo ciclo: a autorização
# pertence a S2-D8.


@pytest.fixture(scope="module")
def indice_real() -> dict[str, Any]:
    return carregar_indice(INDICE)


@pytest.fixture(scope="module")
def base_real() -> dict[str, Any]:
    return yaml.safe_load(BASE_FACTUAL.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def textos_reais() -> dict[str, str]:
    return dict(extrair_textos_emitiveis(MARKDOWN.read_text(encoding="utf-8")))


def _bindings_por_token(indice: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        f"{resposta['id']}/{fragmento['id']}": fragmento["bindings"]
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
    }


def test_sf_t17_corpus_materializa_sem_excecao(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    tokens = derivar_tokens_do_indice(indice_real)
    assert len(tokens) == TOTAL_FRAGMENTOS

    resultado = materializar_fatos_autorizados(
        indice_real, base_real, textos_reais, tokens
    )

    assert len(resultado.textos_autorizados) == TOTAL_FRAGMENTOS
    assert tuple(t.token for t in resultado.textos_autorizados) == tokens


def test_sf_t17_fatos_correspondem_exatamente_aos_renderizado(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    tokens = derivar_tokens_do_indice(indice_real)
    por_token = _bindings_por_token(indice_real)

    esperados = {
        (token, binding["nome"])
        for token, bindings in por_token.items()
        for binding in bindings
        if binding["mecanismo"] == "RENDERIZADO"
    }
    assert esperados, "o corpus precisa ter ao menos um RENDERIZADO"

    resultado = materializar_fatos_autorizados(
        indice_real, base_real, textos_reais, tokens
    )

    assert {(f.token, f.binding) for f in resultado.fatos} == esperados


def test_sf_t17_nenhuma_assertiva_produz_fato(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    tokens = derivar_tokens_do_indice(indice_real)
    por_token = _bindings_por_token(indice_real)

    assertivas = {
        (token, binding["nome"])
        for token, bindings in por_token.items()
        for binding in bindings
        if binding["mecanismo"] == "ASSERTIVA"
    }
    assert assertivas, "o corpus precisa ter ao menos uma ASSERTIVA"

    resultado = materializar_fatos_autorizados(
        indice_real, base_real, textos_reais, tokens
    )

    assert not ({(f.token, f.binding) for f in resultado.fatos} & assertivas)


def test_sf_t17_textos_sao_transportados_literalmente(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    tokens = derivar_tokens_do_indice(indice_real)

    resultado = materializar_fatos_autorizados(
        indice_real, base_real, textos_reais, tokens
    )

    for autorizado in resultado.textos_autorizados:
        assert autorizado.texto == textos_reais[autorizado.token]
