"""Compositor determinístico — o *template* aprovado com os valores no lugar.

Esta suíte exercita a fronteira sobre **estruturas sintéticas mínimas** e, no
fim, sobre os **artefatos versionados reais**. **Zero valor comercial** é
reproduzido: nenhum preço, capacidade, horário, prazo, percentual, quantidade ou
frase aprovada aparece no código. Os cenários sintéticos usam valores neutros,
sem correspondência com `knowledge/casa77.yaml`, e o cenário de corpus é
**inteiramente mecânico** — as expectativas são derivadas dos próprios artefatos
em tempo de execução, e **nenhum valor é congelado**.

O cenário de corpus fornece os tokens do índice como **stub de chamador**,
exclusivamente para exercitar a cadeia. Ele **não afirma** que os 37 tokens
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
    TextoAutorizado,
    materializar_fatos_autorizados,
)
from casa77_sdr.response_composition import (
    ComposicaoNaoAvaliavel,
    OrigemValor,
    ResultadoComposicao,
    TextoEmitivel,
    compor_textos_emitiveis,
)
from casa77_sdr.response_emittable_text import extrair_textos_emitiveis
from casa77_sdr.response_index_load import carregar_indice
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice
from casa77_sdr.response_placeholder import (
    PlaceholderInvalido,
    decompor_template,
    derivar_placeholder,
)

RAIZ = Path(__file__).resolve().parents[1]
INDICE = RAIZ / "knowledge" / "indice-respostas-aprovadas.yaml"
MARKDOWN = RAIZ / "knowledge" / "respostas-aprovadas.md"
BASE_FACTUAL = RAIZ / "knowledge" / "casa77.yaml"
MODULO_CMP = RAIZ / "src" / "casa77_sdr" / "response_composition.py"

# Cardinalidade estrutural do corpus corrente — contagem, não dado comercial.
TOTAL_FRAGMENTOS = 37


# ---------------------------------------------------------------------------
# Construtores de cenário — sintéticos, mecânicos, sem literal comercial


def _texto(token: str, texto: str, rxx: str = "R01", fid: str = "F1") -> TextoAutorizado:
    return TextoAutorizado(token, rxx, fid, texto)


def _fato(
    token: str,
    binding: str,
    valor: str,
    rxx: str = "R01",
    fid: str = "F1",
    referente: str | None = None,
    formato: str = "texto",
) -> FatoAutorizado:
    return FatoAutorizado(
        token,
        rxx,
        fid,
        binding,
        referente if referente is not None else f"fato.{binding}",
        formato,
        valor,
    )


def _selecao(
    fatos: tuple[FatoAutorizado, ...],
    textos: tuple[TextoAutorizado, ...],
) -> ResultadoSelecaoFatos:
    return ResultadoSelecaoFatos(fatos=fatos, textos_autorizados=textos)


# ---------------------------------------------------------------------------
# CMP-T1 — fragmento estático


def test_cmp_t1_estatico_preserva_o_texto_e_nao_tem_origem() -> None:
    original = "texto integralmente estatico, sem marcador algum."
    selecao = _selecao((), (_texto("R01/F1", original),))

    resultado = compor_textos_emitiveis(selecao)

    assert isinstance(resultado, ResultadoComposicao)
    assert len(resultado.textos_emitiveis) == 1

    emitivel = resultado.textos_emitiveis[0]
    assert emitivel.texto == original
    assert emitivel.origens == ()
    assert (emitivel.token, emitivel.rxx, emitivel.fragmento_id) == (
        "R01/F1",
        "R01",
        "F1",
    )


def test_cmp_t1_selecao_vazia_e_sucesso_vazio() -> None:
    resultado = compor_textos_emitiveis(_selecao((), ()))

    assert resultado.textos_emitiveis == ()


# ---------------------------------------------------------------------------
# CMP-T2 — template simples


def test_cmp_t2_um_placeholder_um_fato() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "alfa", formato="texto"),),
        (_texto("R01/F1", "prefixo {{rotulo}} sufixo"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "prefixo alfa sufixo"
    assert emitivel.origens == (
        OrigemValor(binding="rotulo", referente="fato.rotulo", formato="texto"),
    )


def test_cmp_t2_placeholder_nas_extremidades() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "a", "X"), _fato("R01/F1", "b", "Y")),
        (_texto("R01/F1", "{{a}}{{b}}"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "XY"
    assert tuple(o.binding for o in emitivel.origens) == ("a", "b")


# ---------------------------------------------------------------------------
# CMP-T3 — a ordem é a do template, não a dos fatos


def test_cmp_t3_ordem_segue_o_template_e_nao_a_entrada() -> None:
    # Os fatos chegam em ordem inversa à do *template*.
    selecao = _selecao(
        (_fato("R01/F1", "segundo", "DOIS"), _fato("R01/F1", "primeiro", "UM")),
        (_texto("R01/F1", "[{{primeiro}}]-[{{segundo}}]"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "[UM]-[DOIS]"
    assert tuple(o.binding for o in emitivel.origens) == ("primeiro", "segundo")


# ---------------------------------------------------------------------------
# CMP-T4 — placeholder repetido


def test_cmp_t4_placeholder_repetido_usa_o_mesmo_fato_e_uma_origem() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "V"),),
        (_texto("R01/F1", "{{rotulo}} no meio {{rotulo}} no fim {{rotulo}}"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "V no meio V no fim V"
    assert len(emitivel.origens) == 1
    assert emitivel.origens[0].binding == "rotulo"


def test_cmp_t4_origem_fica_na_primeira_ocorrencia_fisica() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "a", "A"), _fato("R01/F1", "b", "B")),
        (_texto("R01/F1", "{{b}} {{a}} {{b}}"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "B A B"
    assert tuple(o.binding for o in emitivel.origens) == ("b", "a")


# ---------------------------------------------------------------------------
# CMP-T5 — o valor é texto factual, nunca template


def test_cmp_t5_valor_semelhante_a_template_nao_e_reprocessado() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "{{x}}"),),
        (_texto("R01/F1", "antes {{rotulo}} depois"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "antes {{x}} depois"
    assert len(emitivel.origens) == 1


def test_cmp_t5_valor_com_nome_de_binding_conhecido_nao_e_reprocessado() -> None:
    # O valor contém o *placeholder* do **outro** *binding* do mesmo fragmento;
    # ainda assim ele é literal, e a passada é única.
    selecao = _selecao(
        (_fato("R01/F1", "a", "{{b}}"), _fato("R01/F1", "b", "B")),
        (_texto("R01/F1", "{{a}}|{{b}}"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "{{b}}|B"


# ---------------------------------------------------------------------------
# CMP-T6 / CMP-T7 — a autoridade do template é `decompor_template`


def test_cmp_t6_placeholder_sem_fato_propaga_placeholder_invalido() -> None:
    selecao = _selecao((), (_texto("R01/F1", "tem {{rotulo}} aqui"),))

    with pytest.raises(PlaceholderInvalido):
        compor_textos_emitiveis(selecao)


def test_cmp_t7_fato_sem_placeholder_propaga_placeholder_invalido() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "V"),),
        (_texto("R01/F1", "texto sem marcador"),),
    )

    with pytest.raises(PlaceholderInvalido):
        compor_textos_emitiveis(selecao)


def test_cmp_t6_template_malformado_propaga_placeholder_invalido() -> None:
    selecao = _selecao((), (_texto("R01/F1", "abertura {{ sem fechamento"),))

    with pytest.raises(PlaceholderInvalido):
        compor_textos_emitiveis(selecao)


def test_cmp_t6_nenhum_resultado_parcial_quando_o_template_falha() -> None:
    selecao = _selecao(
        (_fato("R01/F2", "rotulo", "V", fid="F2"),),
        (
            _texto("R01/F1", "estatico"),
            _texto("R01/F2", "sem marcador", fid="F2"),
        ),
    )

    resultado = None
    with pytest.raises(PlaceholderInvalido):
        resultado = compor_textos_emitiveis(selecao)

    assert resultado is None


# ---------------------------------------------------------------------------
# CMP-T8 — cardinalidade múltipla é erro de contrato


def test_cmp_t8_dois_fatos_do_mesmo_binding_sao_recusados() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "UM"), _fato("R01/F1", "rotulo", "DOIS")),
        (_texto("R01/F1", "{{rotulo}}"),),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "cardinalidade_incompativel: selecao.fatos.item"


def test_cmp_t8_cardinalidade_multipla_com_valores_iguais_tambem_e_recusada() -> None:
    """Valores idênticos **não** autorizam deduplicação silenciosa."""
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "V"), _fato("R01/F1", "rotulo", "V")),
        (_texto("R01/F1", "{{rotulo}}"),),
    )

    with pytest.raises(ComposicaoNaoAvaliavel):
        compor_textos_emitiveis(selecao)


def test_cmp_t8_cardinalidade_multipla_nao_devolve_resultado_parcial() -> None:
    selecao = _selecao(
        (
            _fato("R01/F2", "rotulo", "UM", fid="F2"),
            _fato("R01/F2", "rotulo", "DOIS", fid="F2"),
        ),
        (
            _texto("R01/F1", "estatico"),
            _texto("R01/F2", "{{rotulo}}", fid="F2"),
        ),
    )

    resultado = None
    with pytest.raises(ComposicaoNaoAvaliavel):
        resultado = compor_textos_emitiveis(selecao)

    assert resultado is None


def test_cmp_t8_mesmo_binding_em_tokens_distintos_e_normal() -> None:
    """A cardinalidade é **por token**, não global."""
    selecao = _selecao(
        (
            _fato("R01/F1", "rotulo", "UM"),
            _fato("R01/F2", "rotulo", "DOIS", fid="F2"),
        ),
        (
            _texto("R01/F1", "{{rotulo}}"),
            _texto("R01/F2", "{{rotulo}}", fid="F2"),
        ),
    )

    resultado = compor_textos_emitiveis(selecao)

    assert tuple(e.texto for e in resultado.textos_emitiveis) == ("UM", "DOIS")


# ---------------------------------------------------------------------------
# CMP-T9 — homógrafos mantêm proveniências distintas


def test_cmp_t9_bindings_distintos_com_mesmo_valor_mantem_origens_distintas() -> None:
    selecao = _selecao(
        (
            _fato("R01/F1", "primeiro", "IGUAL", referente="fato.a"),
            _fato("R01/F1", "segundo", "IGUAL", referente="fato.b"),
        ),
        (_texto("R01/F1", "{{primeiro}} {{segundo}}"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert emitivel.texto == "IGUAL IGUAL"
    assert emitivel.origens == (
        OrigemValor(binding="primeiro", referente="fato.a", formato="texto"),
        OrigemValor(binding="segundo", referente="fato.b", formato="texto"),
    )


# ---------------------------------------------------------------------------
# CMP-T10 / CMP-T11 / CMP-T12 — coerência da seleção recebida


@pytest.mark.parametrize(
    ("rxx", "fid"),
    [("R02", "F1"), ("R01", "F2"), ("R02", "F2")],
    ids=["rxx", "fragmento_id", "ambos"],
)
def test_cmp_t10_proveniencia_incoerente_e_recusada(rxx: str, fid: str) -> None:
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "V", rxx=rxx, fid=fid),),
        (_texto("R01/F1", "{{rotulo}}"),),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "proveniencia_incoerente: selecao.fatos.item"


def test_cmp_t11_fato_de_token_desconhecido_e_recusado() -> None:
    selecao = _selecao(
        (_fato("R09/F1", "rotulo", "V", rxx="R09"),),
        (_texto("R01/F1", "estatico"),),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "token_desconhecido: selecao.fatos.item"


def test_cmp_t12_token_duplicado_entre_textos_e_recusado() -> None:
    selecao = _selecao(
        (),
        (_texto("R01/F1", "um"), _texto("R01/F1", "outro")),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "duplicidade: selecao.textos_autorizados.item"


def test_cmp_t12_mensagens_nunca_ecoam_conteudo() -> None:
    selecao = _selecao(
        (),
        (
            _texto("R01/F1", "conteudo_sensivel_sintetico"),
            _texto("R01/F1", "outro"),
        ),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    mensagem = str(erro.value)
    assert "conteudo_sensivel_sintetico" not in mensagem
    assert "R01/F1" not in mensagem


# ---------------------------------------------------------------------------
# CMP-T13 — tipos exatos e precedência das recusas


@pytest.mark.parametrize(
    "entrada",
    [None, (), [], "selecao", object()],
    ids=["nulo", "tupla", "lista", "texto", "objeto"],
)
def test_cmp_t13_selecao_de_tipo_invalido(entrada: object) -> None:
    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(entrada)

    assert str(erro.value) == "tipo_invalido: selecao"


def test_cmp_t13_fatos_precisam_ser_tupla() -> None:
    selecao = ResultadoSelecaoFatos(
        fatos=[_fato("R01/F1", "rotulo", "V")],  # type: ignore[arg-type]
        textos_autorizados=(_texto("R01/F1", "{{rotulo}}"),),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.fatos"


def test_cmp_t13_textos_precisam_ser_tupla() -> None:
    selecao = ResultadoSelecaoFatos(
        fatos=(),
        textos_autorizados=[_texto("R01/F1", "estatico")],  # type: ignore[arg-type]
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.textos_autorizados"


@pytest.mark.parametrize(
    "item",
    [None, "R01/F1", ("R01/F1", "R01", "F1", "t")],
    ids=["nulo", "texto", "tupla"],
)
def test_cmp_t13_item_de_fatos_precisa_ser_canonico(item: object) -> None:
    selecao = ResultadoSelecaoFatos(
        fatos=(item,),  # type: ignore[arg-type]
        textos_autorizados=(_texto("R01/F1", "estatico"),),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.fatos.item"


def test_cmp_t13_item_de_textos_precisa_ser_canonico() -> None:
    selecao = ResultadoSelecaoFatos(
        fatos=(),
        textos_autorizados=("R01/F1",),  # type: ignore[arg-type]
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.textos_autorizados.item"


@pytest.mark.parametrize(
    "campo",
    ["token", "rxx", "fragmento_id", "binding", "referente", "formato", "valor"],
)
def test_cmp_t13_campos_do_fato_exigem_str_exata(campo: str) -> None:
    valores: dict[str, Any] = {
        "token": "R01/F1",
        "rxx": "R01",
        "fragmento_id": "F1",
        "binding": "rotulo",
        "referente": "fato.rotulo",
        "formato": "texto",
        "valor": "V",
    }
    valores[campo] = 0

    fato = FatoAutorizado(
        valores["token"],
        valores["rxx"],
        valores["fragmento_id"],
        valores["binding"],
        valores["referente"],
        valores["formato"],
        valores["valor"],
    )
    selecao = _selecao((fato,), (_texto("R01/F1", "{{rotulo}}"),))

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.fatos.item"


def test_cmp_t13_texto_exige_str_exata() -> None:
    selecao = _selecao((), (TextoAutorizado("R01/F1", "R01", "F1", 0),))  # type: ignore[arg-type]

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.textos_autorizados.item"


def test_cmp_t13_precedencia_fatos_antes_de_textos() -> None:
    """A forma dos fatos é exigida **antes** da forma dos textos."""
    selecao = ResultadoSelecaoFatos(
        fatos=[],  # type: ignore[arg-type]
        textos_autorizados=[],  # type: ignore[arg-type]
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.fatos"


def test_cmp_t13_precedencia_forma_antes_de_coerencia() -> None:
    """Um item malformado é recusado **antes** do juízo de token desconhecido."""
    selecao = ResultadoSelecaoFatos(
        fatos=(None,),  # type: ignore[arg-type]
        textos_autorizados=(),
    )

    with pytest.raises(ComposicaoNaoAvaliavel) as erro:
        compor_textos_emitiveis(selecao)

    assert str(erro.value) == "tipo_invalido: selecao.fatos.item"


# ---------------------------------------------------------------------------
# CMP-T14 — segurança do `repr`


def test_cmp_t14_repr_do_emitivel_nao_expoe_o_texto() -> None:
    emitivel = TextoEmitivel(
        token="R01/F1",
        rxx="R01",
        fragmento_id="F1",
        origens=(),
        texto="redacao_composta_sintetica",
    )

    representacao = repr(emitivel)

    assert "redacao_composta_sintetica" not in representacao
    assert "texto=" not in representacao
    assert "R01/F1" in representacao


def test_cmp_t14_origem_nao_carrega_valor_comercial() -> None:
    origem = OrigemValor(binding="rotulo", referente="fato.rotulo", formato="texto")

    assert OrigemValor.__slots__ == ("binding", "referente", "formato")
    assert "valor" not in repr(origem)
    assert not hasattr(origem, "valor_formatado")


def test_cmp_t14_composto_real_nao_vaza_pelo_repr() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "rotulo", "valor_sintetico_secreto"),),
        (_texto("R01/F1", "antes {{rotulo}} depois"),),
    )

    emitivel = compor_textos_emitiveis(selecao).textos_emitiveis[0]

    assert "valor_sintetico_secreto" in emitivel.texto
    assert "valor_sintetico_secreto" not in repr(emitivel)


def test_cmp_t14_dtos_sao_congelados_e_sem_dicionario() -> None:
    origem = OrigemValor("n", "fato.n", "texto")
    emitivel = TextoEmitivel("R01/F1", "R01", "F1", (origem,), "t")
    resultado = ResultadoComposicao(textos_emitiveis=(emitivel,))

    for dto in (origem, emitivel, resultado):
        assert not hasattr(dto, "__dict__")
        with pytest.raises(Exception):
            dto.binding = "outro"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# CMP-T15 — imutabilidade


def test_cmp_t15_nenhuma_entrada_e_mutada() -> None:
    selecao = _selecao(
        (
            _fato("R01/F1", "a", "A"),
            _fato("R01/F1", "b", "B"),
            _fato("R01/F2", "c", "C", fid="F2"),
        ),
        (
            _texto("R01/F1", "{{a}} {{b}} {{a}}"),
            _texto("R01/F2", "{{c}}", fid="F2"),
        ),
    )
    copia = copy.deepcopy(selecao)

    compor_textos_emitiveis(selecao)

    assert selecao == copia


# ---------------------------------------------------------------------------
# CMP-T16 — determinismo


def test_cmp_t16_duas_execucoes_dao_o_mesmo_resultado() -> None:
    selecao = _selecao(
        (_fato("R01/F1", "a", "A"), _fato("R01/F1", "b", "B")),
        (_texto("R01/F1", "{{b}}-{{a}}-{{b}}"),),
    )

    assert compor_textos_emitiveis(selecao) == compor_textos_emitiveis(selecao)


# ---------------------------------------------------------------------------
# CMP-T17 — a ordem dos fragmentos é a recebida


@pytest.mark.parametrize(
    "ordem",
    [("R01/F1", "R02/F1", "R03/F1"), ("R03/F1", "R01/F1", "R02/F1")],
    ids=["direta", "embaralhada"],
)
def test_cmp_t17_ordem_dos_fragmentos_e_a_de_textos_autorizados(
    ordem: tuple[str, ...],
) -> None:
    por_token = {
        "R01/F1": (_texto("R01/F1", "{{a}}"), _fato("R01/F1", "a", "A")),
        "R02/F1": (
            _texto("R02/F1", "{{b}}", rxx="R02"),
            _fato("R02/F1", "b", "B", rxx="R02"),
        ),
        "R03/F1": (
            _texto("R03/F1", "{{c}}", rxx="R03"),
            _fato("R03/F1", "c", "C", rxx="R03"),
        ),
    }
    textos = tuple(por_token[t][0] for t in ordem)
    # Os fatos entram sempre na mesma ordem fixa, independente da dos textos.
    fatos = tuple(por_token[t][1] for t in ("R01/F1", "R02/F1", "R03/F1"))

    resultado = compor_textos_emitiveis(_selecao(fatos, textos))

    assert tuple(e.token for e in resultado.textos_emitiveis) == ordem


def test_cmp_t17_nenhum_fragmento_e_omitido_repetido_ou_concatenado() -> None:
    selecao = _selecao(
        (),
        (
            _texto("R01/F1", "um"),
            _texto("R01/F2", "dois", fid="F2"),
            _texto("R01/F3", "tres", fid="F3"),
        ),
    )

    resultado = compor_textos_emitiveis(selecao)

    assert len(resultado.textos_emitiveis) == 3
    assert tuple(e.texto for e in resultado.textos_emitiveis) == ("um", "dois", "tres")
    # Nenhum campo de resposta final existe.
    assert ResultadoComposicao.__slots__ == ("textos_emitiveis",)


# ---------------------------------------------------------------------------
# CMP-T18 — isolamento estrutural do módulo


def _arvore_do_modulo() -> ast.Module:
    return ast.parse(MODULO_CMP.read_text(encoding="utf-8"))


def _modulos_importados() -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(_arvore_do_modulo()):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module is not None:
            importados.add(no.module)
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


def test_cmp_t18_importa_somente_o_necessario() -> None:
    assert _modulos_importados() == {
        "__future__",
        "dataclasses",
        "casa77_sdr.fact_selection",
        "casa77_sdr.response_placeholder",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_status",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_yaml_resolve",
        "casa77_sdr.state_machine",
        "casa77_sdr.interpretation",
        "casa77_sdr.qualification",
        "casa77_sdr.persistence",
        "yaml",
        "pathlib",
        "os",
        "io",
        "re",
        "json",
        "logging",
        "datetime",
        "time",
        "random",
        "functools",
    ],
)
def test_cmp_t18_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _modulos_importados()


def test_cmp_t18_nao_substitui_nem_formata_template() -> None:
    chamados = _nomes_chamados()

    for proibido in ("replace", "format", "format_map", "sub", "compile", "open"):
        assert proibido not in chamados

    # A composição usa `join`, que é explicitamente permitido.
    assert "join" in chamados
    # E delega a gramática à autoridade.
    assert "decompor_template" in chamados


def test_cmp_t18_nao_conhece_vocabulario_de_montante() -> None:
    fonte = MODULO_CMP.read_text(encoding="utf-8").casefold()

    for termo in (
        "PerguntaComercial",
        "AssuntoComercial",
        "witness",
        "cobertura",
        "candidatura",
        "emissibilidade",
        "knowledge/casa77",
        "indice-respostas",
    ):
        assert termo.casefold() not in fonte


def test_cmp_t18_superficie_publica_e_minima() -> None:
    import casa77_sdr.response_composition as modulo

    assert sorted(modulo.__all__) == [
        "ComposicaoNaoAvaliavel",
        "OrigemValor",
        "ResultadoComposicao",
        "TextoEmitivel",
        "compor_textos_emitiveis",
    ]
    for ausente in ("texto_final", "rascunho", "mensagem", "separador", "delimiter"):
        assert not hasattr(modulo, ausente)


# ---------------------------------------------------------------------------
# CMP-T19 / CMP-T20 / CMP-T21 — corpus físico, inteiramente mecânico


@pytest.fixture(scope="module")
def indice_real() -> dict[str, Any]:
    return carregar_indice(INDICE)


@pytest.fixture(scope="module")
def base_real() -> dict[str, Any]:
    return yaml.safe_load(BASE_FACTUAL.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def textos_reais() -> dict[str, str]:
    return dict(extrair_textos_emitiveis(MARKDOWN.read_text(encoding="utf-8")))


def _cadeia_do_corpus(
    indice: dict[str, Any],
    base: dict[str, Any],
    textos: dict[str, str],
) -> ResultadoComposicao:
    tokens = derivar_tokens_do_indice(indice)
    selecao = materializar_fatos_autorizados(indice, base, textos, tokens)
    return compor_textos_emitiveis(selecao)


def test_cmp_t19_corpus_compoe_um_emitivel_por_fragmento(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    tokens = derivar_tokens_do_indice(indice_real)
    selecao = materializar_fatos_autorizados(indice_real, base_real, textos_reais, tokens)

    resultado = compor_textos_emitiveis(selecao)

    assert len(selecao.textos_autorizados) == TOTAL_FRAGMENTOS
    assert len(resultado.textos_emitiveis) == TOTAL_FRAGMENTOS
    assert tuple(e.token for e in resultado.textos_emitiveis) == tokens


def test_cmp_t20_corpus_fisico_nao_declara_itera_sobre(
    indice_real: dict[str, Any],
) -> None:
    """Pré-condição declarada desta versão do compositor.

    A cardinalidade fechada de **um fato por *binding*** só é segura enquanto
    nenhum fragmento físico iterar. Se este teste ficar vermelho, a premissa
    mudou e a apresentação de múltiplas ocorrências precisa de arbitragem —
    **não** de adaptação silenciosa.
    """
    fragmentos = [
        fragmento
        for resposta in indice_real["respostas"]
        for fragmento in resposta["fragmentos"]
    ]

    assert len(fragmentos) == TOTAL_FRAGMENTOS
    assert [f for f in fragmentos if "itera_sobre" in f] == []


def test_cmp_t21_nenhum_placeholder_do_template_sobrevive(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    """Todo *placeholder* declarado no *template* foi efetivamente substituído.

    A prova usa as **autoridades estruturais** — `decompor_template` para extrair
    os nomes na ordem física e `derivar_placeholder` para a forma canônica —, e
    **nenhuma gramática paralela**.
    """
    tokens = derivar_tokens_do_indice(indice_real)
    selecao = materializar_fatos_autorizados(indice_real, base_real, textos_reais, tokens)
    resultado = compor_textos_emitiveis(selecao)

    por_token = {a.token: a for a in selecao.textos_autorizados}
    nomes_por_token: dict[str, tuple[str, ...]] = {}
    for fato in selecao.fatos:
        atuais = nomes_por_token.get(fato.token, ())
        if fato.binding not in atuais:
            nomes_por_token[fato.token] = atuais + (fato.binding,)

    com_template = 0
    for emitivel in resultado.textos_emitiveis:
        nomes = nomes_por_token.get(emitivel.token, ())
        partes = decompor_template(por_token[emitivel.token].texto, nomes)
        declarados = {parte for posicao, parte in enumerate(partes) if posicao % 2}

        if declarados:
            com_template += 1
        for nome in declarados:
            assert derivar_placeholder(nome) not in emitivel.texto

    assert com_template > 0, "o corpus precisa ter ao menos um *template*"


def test_cmp_t21_origens_correspondem_aos_bindings_do_template(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    resultado = _cadeia_do_corpus(indice_real, base_real, textos_reais)

    for emitivel in resultado.textos_emitiveis:
        nomes = [o.binding for o in emitivel.origens]
        # Uma origem por *binding* distinto, sem repetição.
        assert len(nomes) == len(set(nomes))


def test_cmp_t19_corpus_e_deterministico(
    indice_real: dict[str, Any],
    base_real: dict[str, Any],
    textos_reais: dict[str, str],
) -> None:
    primeira = _cadeia_do_corpus(indice_real, base_real, textos_reais)
    segunda = _cadeia_do_corpus(indice_real, base_real, textos_reais)

    assert primeira == segunda
