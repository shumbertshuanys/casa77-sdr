"""Testes da **montagem compartilhada** da `FotografiaFragmento`.

Tudo aqui é **estrutural e sintético**: rótulos de status, caminhos e
predicados têm a **forma** do corpus, nunca o seu conteúdo. **Zero valor
comercial** aparece — nenhum preço, capacidade, horário, prazo, percentual,
quantidade ou frase aprovada —, e `knowledge/**` **não é aberto**.

A suíte prova quatro coisas distintas: **(1)** cada um dos quatro campos da
fotografia vem da autoridade que lhe cabe, com ordem e duplicatas preservadas;
**(2)** a fronteira **fecha** quando a fotografia não é projetável
univocamente, sem exceção pública nova; **(3)** ela **monta e não avalia** —
`D8-F` continua com uma única implementação de decisão; e **(4)** o resultado
**encaixa** na rota *action-owner* de **T16**/`R06`, por composição direta das
três fronteiras, **sem** coordenador, *pipeline* ou ciclo.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from casa77_sdr.emission_projection import projetar_fragmentos_para_emissao
from casa77_sdr.fragment_emissibility import (
    FotografiaFragmento,
    avaliar_emissibilidade,
)
from casa77_sdr.fragment_snapshot import montar_fotografia_fragmento
from casa77_sdr.response_consistency import (
    ReferenteIndisponivel,
    ResultadoConsistencia,
)
from casa77_sdr.state_machine import AcaoMaquina

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "fragment_snapshot.py"
MODULO_S2D8 = RAIZ / "src" / "casa77_sdr" / "coverage_decision.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

# Rotulos canonicos de `C-3` — estruturais, nunca conteudo.
APROVADO = "APROVADO"
AGUARDA = "AGUARDA_APROVACAO"
BLOQUEADO = "BLOQUEADO"

# Tokens sinteticos. `VISITA` e o unico token real citado, porque a prova de
# encaixe de T16 exige o identificador que `PE-15`–`PE-20` ja arbitraram.
ALVO = "R97/F1"
OUTRO = "R98/F1"
VISITA = "R06/F1"

CAMINHO_A = "secao_a.campo_um"
CAMINHO_B = "secao_b.campo_dois"

PREDICADO_A = "EH_VERDADEIRO"
PREDICADO_B = "EH_FALSO"


def _consistencia(
    *,
    status: tuple[tuple[str, str], ...] = ((ALVO, APROVADO),),
    divergentes: tuple[str, ...] = (),
    indisponiveis: tuple[ReferenteIndisponivel, ...] = (),
) -> ResultadoConsistencia:
    """Um `ResultadoConsistencia` sintético e coerente para a montagem.

    `divergencias` fica vazia de propósito: a montagem lê **somente**
    `tokens_divergentes`, e provar isso exige que ela **não** possa recompor a
    divergência a partir de `divergencias`.
    """
    return ResultadoConsistencia(
        divergencias=(),
        referentes_indisponiveis=indisponiveis,
        tokens_divergentes=divergentes,
        status_por_fragmento=status,
        bindings_runtime_nao_avaliados=(),
    )


def _indisponivel(token: str, referente: str) -> ReferenteIndisponivel:
    """Um `C-7` sintético; só o `referente` deve atravessar a montagem."""
    return ReferenteIndisponivel(
        token=token,
        rxx=token.split("/")[0],
        fragmento_id=token.split("/")[1],
        binding="binding_estrutural",
        mecanismo="RENDERIZADO",
        origem="YAML",
        referente=referente,
    )


def _arvore(caminho: Path) -> ast.Module:
    return ast.parse(caminho.read_text(encoding="utf-8"))


def _codigo_sem_prosa(caminho: Path) -> str:
    """O código sem docstring — prosa negativa não é acesso."""
    arvore = _arvore(caminho)
    portadores = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for no in ast.walk(arvore):
        if not isinstance(no, portadores):
            continue
        corpo = no.body
        primeiro = corpo[0] if corpo else None
        if (
            isinstance(primeiro, ast.Expr)
            and isinstance(primeiro.value, ast.Constant)
            and isinstance(primeiro.value.value, str)
        ):
            no.body = corpo[1:] or [ast.Pass()]
    return ast.unparse(arvore)


def _importados(caminho: Path) -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(_arvore(caminho)):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module is not None:
            importados.add(no.module)
    return importados


# ---------------------------------------------------------------------------
# FF-T1 — os quatro campos


def test_ff_t1_monta_os_quatro_campos() -> None:
    """A saída é **uma** `FotografiaFragmento`, com os quatro campos projetados."""
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(
            divergentes=(ALVO,),
            indisponiveis=(_indisponivel(ALVO, CAMINHO_A),),
        ),
        assertivas_runtime=((PREDICADO_A, True),),
    )

    assert type(fotografia) is FotografiaFragmento
    assert fotografia.status == APROVADO
    assert fotografia.divergente is True
    assert fotografia.referentes_indisponiveis == (CAMINHO_A,)
    assert fotografia.assertivas_runtime == ((PREDICADO_A, True),)


# ---------------------------------------------------------------------------
# FF-T2 — status: autoridade única em `status_por_fragmento`


@pytest.mark.parametrize("rotulo", [APROVADO, AGUARDA, BLOQUEADO])
def test_ff_t2_status_e_transportado_literalmente(rotulo: str) -> None:
    """Os três rótulos canônicos atravessam **sem** tradução e **sem** juízo."""
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(status=((OUTRO, BLOQUEADO), (ALVO, rotulo))),
        assertivas_runtime=(),
    )

    assert fotografia.status == rotulo


def test_ff_t3_status_vem_do_par_do_token_e_nao_do_primeiro() -> None:
    """A seleção é **pelo token**, nunca pela posição física."""
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(status=((OUTRO, BLOQUEADO), (ALVO, APROVADO))),
        assertivas_runtime=(),
    )

    assert fotografia.status == APROVADO


# ---------------------------------------------------------------------------
# FF-T4 — divergência: autoridade única em `tokens_divergentes`


def test_ff_t4_divergente_falso_quando_o_token_nao_consta() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(divergentes=(OUTRO,)), assertivas_runtime=()
    )

    assert fotografia.divergente is False


def test_ff_t5_divergente_verdadeiro_quando_o_token_consta() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(divergentes=(OUTRO, ALVO)), assertivas_runtime=()
    )

    assert fotografia.divergente is True


# ---------------------------------------------------------------------------
# FF-T6 — `C-7`: ordem física, zero deduplicação, só o referente


def test_ff_t6_zero_referentes() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(), assertivas_runtime=()
    )

    assert fotografia.referentes_indisponiveis == ()


def test_ff_t7_um_referente() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(indisponiveis=(_indisponivel(ALVO, CAMINHO_A),)),
        assertivas_runtime=(),
    )

    assert fotografia.referentes_indisponiveis == (CAMINHO_A,)


def test_ff_t8_varios_referentes_do_token() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(
            indisponiveis=(
                _indisponivel(ALVO, CAMINHO_A),
                _indisponivel(ALVO, CAMINHO_B),
            )
        ),
        assertivas_runtime=(),
    )

    assert fotografia.referentes_indisponiveis == (CAMINHO_A, CAMINHO_B)


def test_ff_t9_ordem_fisica_preservada_com_outro_token_no_meio() -> None:
    """Filtrar pelo token **não** reordena o que sobra."""
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(
            indisponiveis=(
                _indisponivel(ALVO, CAMINHO_B),
                _indisponivel(OUTRO, CAMINHO_A),
                _indisponivel(ALVO, CAMINHO_A),
            )
        ),
        assertivas_runtime=(),
    )

    assert fotografia.referentes_indisponiveis == (CAMINHO_B, CAMINHO_A)


def test_ff_t10_duplicatas_de_referente_sao_preservadas() -> None:
    """**D8-E4**: reduzir perderia causa estrutural."""
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(
            indisponiveis=(
                _indisponivel(ALVO, CAMINHO_A),
                _indisponivel(ALVO, CAMINHO_A),
            )
        ),
        assertivas_runtime=(),
    )

    assert fotografia.referentes_indisponiveis == (CAMINHO_A, CAMINHO_A)


def test_ff_t11_somente_o_referente_atravessa() -> None:
    """`mecanismo`, `binding`, `origem`, `rxx` e `fragmento_id` ficam fora."""
    item = _indisponivel(ALVO, CAMINHO_A)
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(indisponiveis=(item,)), assertivas_runtime=()
    )

    projetado = fotografia.referentes_indisponiveis
    assert projetado == (CAMINHO_A,)
    for descartado in (item.mecanismo, item.binding, item.origem, item.rxx):
        assert descartado not in projetado


def test_ff_t12_referente_de_outro_token_nao_entra() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO,
        _consistencia(indisponiveis=(_indisponivel(OUTRO, CAMINHO_A),)),
        assertivas_runtime=(),
    )

    assert fotografia.referentes_indisponiveis == ()


# ---------------------------------------------------------------------------
# FF-T13 — runtime: transportado, nunca resolvido, nunca avaliado


def test_ff_t13_runtime_vazio() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(), assertivas_runtime=()
    )

    assert fotografia.assertivas_runtime == ()


def test_ff_t14_runtime_com_um_par() -> None:
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(), assertivas_runtime=((PREDICADO_A, False),)
    )

    assert fotografia.assertivas_runtime == ((PREDICADO_A, False),)


def test_ff_t15_runtime_com_varios_pares_preserva_a_ordem() -> None:
    pares = ((PREDICADO_B, False), (PREDICADO_A, True))
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(), assertivas_runtime=pares
    )

    assert fotografia.assertivas_runtime == pares


def test_ff_t16_runtime_preserva_duplicata() -> None:
    pares = ((PREDICADO_A, True), (PREDICADO_A, True))
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(), assertivas_runtime=pares
    )

    assert fotografia.assertivas_runtime == pares


def test_ff_t17_runtime_nao_e_avaliado() -> None:
    """Um par **falso** atravessa intacto: julgá-lo é de `avaliar_emissibilidade`."""
    fotografia = montar_fotografia_fragmento(
        ALVO, _consistencia(), assertivas_runtime=((PREDICADO_A, False),)
    )

    assert fotografia.assertivas_runtime == ((PREDICADO_A, False),)
    assert fotografia.status == APROVADO
    assert fotografia.divergente is False


def test_ff_t18_assertivas_runtime_e_keyword_only_e_obrigatoria() -> None:
    """Sem valor padrão: um `()` implícito deixaria runtime escapar em silêncio."""
    with pytest.raises(TypeError):
        montar_fotografia_fragmento(ALVO, _consistencia())  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        montar_fotografia_fragmento(ALVO, _consistencia(), ())  # type: ignore[misc]


# ---------------------------------------------------------------------------
# FF-T19 — fail-closed da projeção unívoca


def test_ff_t19_token_sem_status_fecha() -> None:
    with pytest.raises(ValueError) as erro:
        montar_fotografia_fragmento(
            ALVO, _consistencia(status=((OUTRO, APROVADO),)), assertivas_runtime=()
        )

    assert str(erro.value) == "status_ausente: consistencia.status_por_fragmento"


def test_ff_t20_token_com_dois_status_fecha() -> None:
    with pytest.raises(ValueError) as erro:
        montar_fotografia_fragmento(
            ALVO,
            _consistencia(status=((ALVO, APROVADO), (ALVO, BLOQUEADO))),
            assertivas_runtime=(),
        )

    assert str(erro.value) == "status_ambiguo: consistencia.status_por_fragmento"


# ---------------------------------------------------------------------------
# FF-T21 — tipos exatos da superfície


@pytest.mark.parametrize(
    "invalido",
    [None, 1, (ALVO,), [ALVO], {ALVO}],
    ids=["nulo", "inteiro", "tupla", "lista", "conjunto"],
)
def test_ff_t21_token_tipo_invalido(invalido: object) -> None:
    with pytest.raises(TypeError) as erro:
        montar_fotografia_fragmento(invalido, _consistencia(), assertivas_runtime=())

    assert str(erro.value) == "tipo_invalido: token"


@pytest.mark.parametrize(
    "invalido",
    [None, "consistencia", (), {}],
    ids=["nulo", "texto", "tupla", "dicionario"],
)
def test_ff_t22_consistencia_tipo_invalido(invalido: object) -> None:
    with pytest.raises(TypeError) as erro:
        montar_fotografia_fragmento(ALVO, invalido, assertivas_runtime=())

    assert str(erro.value) == "tipo_invalido: consistencia"


@pytest.mark.parametrize(
    "invalido",
    [None, [], {}, "pares"],
    ids=["nulo", "lista", "dicionario", "texto"],
)
def test_ff_t23_runtime_tipo_invalido(invalido: object) -> None:
    with pytest.raises(TypeError) as erro:
        montar_fotografia_fragmento(ALVO, _consistencia(), assertivas_runtime=invalido)

    assert str(erro.value) == "tipo_invalido: assertivas_runtime"


@pytest.mark.parametrize(
    "item",
    [
        [PREDICADO_A, True],
        (PREDICADO_A,),
        (PREDICADO_A, True, True),
        (),
    ],
    ids=["lista", "curta", "longa", "vazia"],
)
def test_ff_t24_item_de_runtime_com_forma_invalida(item: object) -> None:
    with pytest.raises(TypeError) as erro:
        montar_fotografia_fragmento(
            ALVO, _consistencia(), assertivas_runtime=(item,)
        )

    assert str(erro.value) == "tipo_invalido: assertivas_runtime.item"


@pytest.mark.parametrize(
    "predicado", [None, 1, True, ("x",)], ids=["nulo", "inteiro", "bool", "tupla"]
)
def test_ff_t25_predicado_tipo_invalido(predicado: object) -> None:
    with pytest.raises(TypeError) as erro:
        montar_fotografia_fragmento(
            ALVO, _consistencia(), assertivas_runtime=((predicado, True),)
        )

    assert str(erro.value) == "tipo_invalido: assertivas_runtime.item.predicado"


@pytest.mark.parametrize(
    "valor", [None, 1, 0, "True", ()], ids=["nulo", "um", "zero", "texto", "tupla"]
)
def test_ff_t26_valor_de_runtime_exige_bool_exato(valor: object) -> None:
    """`1`/`0` passariam por verdade booleana sem serem o fato resolvido."""
    with pytest.raises(TypeError) as erro:
        montar_fotografia_fragmento(
            ALVO, _consistencia(), assertivas_runtime=((PREDICADO_A, valor),)
        )

    assert str(erro.value) == "tipo_invalido: assertivas_runtime.item.valor"


def test_ff_t27_mensagem_nunca_carrega_o_conteudo_recebido() -> None:
    """A mensagem é `<categoria>: <localizador>`, e nada além disso."""
    with pytest.raises(ValueError) as erro:
        montar_fotografia_fragmento(
            ALVO, _consistencia(status=((OUTRO, APROVADO),)), assertivas_runtime=()
        )

    mensagem = str(erro.value)
    for vazado in (ALVO, OUTRO, APROVADO, CAMINHO_A, "1", "2"):
        assert vazado not in mensagem


# ---------------------------------------------------------------------------
# FF-T28 — pureza, imports e vocabulário


def test_ff_t28_entradas_nao_sao_mutadas() -> None:
    consistencia = _consistencia(
        divergentes=(ALVO,),
        indisponiveis=(_indisponivel(ALVO, CAMINHO_A),),
    )
    pares = ((PREDICADO_A, True),)
    antes_consistencia = copy.deepcopy(consistencia)
    antes_pares = copy.deepcopy(pares)

    montar_fotografia_fragmento(ALVO, consistencia, assertivas_runtime=pares)

    assert consistencia == antes_consistencia
    assert pares == antes_pares


@pytest.mark.parametrize(
    "termo",
    [
        "open(",
        "read_text",
        "write_text",
        "Path(",
        "glob",
        "environ",
        "now(",
        "today(",
        "sleep(",
        "request",
        "knowledge",
        "yaml",
        "sorted(",
        "reverse",
        ".sort(",
        "set(",
    ],
)
def test_ff_t29_superficie_executavel_nao_toca_fronteira_proibida(termo: str) -> None:
    assert termo not in _codigo_sem_prosa(MODULO)


def test_ff_t30_importa_somente_o_necessario() -> None:
    assert _importados(MODULO) == {
        "__future__",
        "casa77_sdr.fragment_emissibility",
        "casa77_sdr.response_consistency",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "casa77_sdr.coverage_decision",
        "casa77_sdr.emission_projection",
        "casa77_sdr.state_machine",
        "casa77_sdr.interpretation",
        "casa77_sdr.handoff_detection",
        "casa77_sdr.response_index",
        "casa77_sdr.response_assertion",
        "casa77_sdr.coverage_map",
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
        "socket",
        "urllib",
        "http",
        "subprocess",
    ],
)
def test_ff_t31_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _importados(MODULO)


@pytest.mark.parametrize(
    "termo",
    [
        "AssuntoComercial",
        "PerguntaComercial",
        "CausaE09",
        "MotivoE09",
        "ClassificacaoPendencia",
        "Evento",
        "AcaoMaquina",
        "MotivoHandoff",
        "Transicao",
        "E09",
        "E18",
        "handoff",
        "witness",
        "cobertura",
        "candidatura",
        "emitivel",
        "avaliar_emissibilidade",
    ],
)
def test_ff_t32_zero_vocabulario_comercial_evento_acao_ou_maquina(termo: str) -> None:
    """Montar não conhece causa, evento, ação, máquina — nem decide emissibilidade."""
    assert termo not in _codigo_sem_prosa(MODULO)


def test_ff_t33_api_publica_e_minima() -> None:
    from casa77_sdr import fragment_snapshot

    assert fragment_snapshot.__all__ == ["montar_fotografia_fragmento"]


def test_ff_t34_nao_e_exportado_pelo_init() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "fragment_snapshot" not in codigo
    assert "montar_fotografia_fragmento" not in codigo


def test_ff_t35_nenhum_dto_enum_ou_excecao_publica_nova() -> None:
    """`FotografiaFragmento` é reutilizada; nada novo nasce aqui."""
    arvore = _arvore(MODULO)
    classes = [no.name for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)]

    assert classes == []


# ---------------------------------------------------------------------------
# FF-T36 — S2-D8 consome a primitiva, e não monta mais inline


def test_ff_t36_s2d8_nao_constroi_mais_a_fotografia_inline() -> None:
    chamadas = {
        no.func.id
        for no in ast.walk(_arvore(MODULO_S2D8))
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }

    assert "FotografiaFragmento" not in chamadas
    assert "FotografiaFragmento" not in _codigo_sem_prosa(MODULO_S2D8)


def test_ff_t37_s2d8_importa_e_usa_a_primitiva_de_montagem() -> None:
    chamadas = {
        no.func.id
        for no in ast.walk(_arvore(MODULO_S2D8))
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }

    assert "casa77_sdr.fragment_snapshot" in _importados(MODULO_S2D8)
    assert "montar_fotografia_fragmento" in chamadas
    # `D8-F` continua com **uma** implementacao de decisao, e S2-D8 a consome.
    assert "avaliar_emissibilidade" in chamadas


# ---------------------------------------------------------------------------
# FF-T38 — prova de encaixe com a rota action-owner de T16/R06
#
# Composicao direta das tres fronteiras, sem coordenador, sem pipeline e sem
# ciclo: montar -> avaliar -> projetar. A invocacao real dentro de um ciclo
# continua sendo do futuro `OrquestradorMotor`.


def test_ff_t38_r06_emitivel_entra_uma_vez_na_projecao() -> None:
    fotografia = montar_fotografia_fragmento(
        VISITA,
        _consistencia(status=((VISITA, APROVADO),)),
        assertivas_runtime=(),
    )
    veredito = avaliar_emissibilidade(fotografia)

    assert veredito.emitivel is True

    resultado = projetar_fragmentos_para_emissao(
        (),
        (AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,),
        fotografia_r06=fotografia,
    )

    assert resultado == (VISITA,)


@pytest.mark.parametrize(
    "consistencia_sintetica",
    [
        _consistencia(status=((VISITA, AGUARDA),)),
        _consistencia(status=((VISITA, BLOQUEADO),)),
        _consistencia(status=((VISITA, APROVADO),), divergentes=(VISITA,)),
        _consistencia(
            status=((VISITA, APROVADO),),
            indisponiveis=(_indisponivel(VISITA, CAMINHO_A),),
        ),
    ],
    ids=["aguarda", "bloqueado", "divergente", "referente_indisponivel"],
)
def test_ff_t39_r06_nao_emitivel_produz_zero_contribuicao(
    consistencia_sintetica: ResultadoConsistencia,
) -> None:
    """**PE-7** e **PE-18**: zero fragmento, e **não** é erro."""
    fotografia = montar_fotografia_fragmento(
        VISITA, consistencia_sintetica, assertivas_runtime=()
    )
    veredito = avaliar_emissibilidade(fotografia)

    assert veredito.emitivel is False

    resultado = projetar_fragmentos_para_emissao(
        (),
        (AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,),
        fotografia_r06=fotografia,
    )

    assert resultado == ()


def test_ff_t40_r06_nao_emitivel_por_assertiva_de_runtime_falsa() -> None:
    """O par falso atravessa a montagem e **só** é julgado por `D8-F`."""
    fotografia = montar_fotografia_fragmento(
        VISITA,
        _consistencia(status=((VISITA, APROVADO),)),
        assertivas_runtime=((PREDICADO_A, False),),
    )

    assert avaliar_emissibilidade(fotografia).emitivel is False
    assert (
        projetar_fragmentos_para_emissao(
            (),
            (AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,),
            fotografia_r06=fotografia,
        )
        == ()
    )


def test_ff_t41_a_prova_de_encaixe_nao_cria_coordenador() -> None:
    """Composição estrutural, não *pipeline*: nada aqui sequencia um ciclo.

    A prova é pelos **imports** e pelas **chamadas** desta suíte: ela toca
    exatamente três fronteiras de produção — montar, avaliar e projetar — e
    **nenhuma** fronteira de coordenação. Nenhum *fake* `OrquestradorMotor`,
    mini *pipeline* ou coordenador de ciclo é definido aqui.
    """
    importados = _importados(Path(__file__))
    for coordenacao in (
        "casa77_sdr.interpretation_stage",
        "casa77_sdr.cycle_inputs",
        "casa77_sdr.cycle_events",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.handoff_detection",
        "casa77_sdr.closure_decision",
    ):
        assert coordenacao not in importados

    arvore = _arvore(Path(__file__))
    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }
    producao = chamadas & {
        "montar_fotografia_fragmento",
        "avaliar_emissibilidade",
        "projetar_fragmentos_para_emissao",
        "executar_interpretacao_do_ciclo",
        "montar_condicoes_ciclo",
        "agregar_eventos_primeira_decisao",
        "decidir_pendencias_e_cobertura",
        "decidir",
    }

    assert producao == {
        "montar_fotografia_fragmento",
        "avaliar_emissibilidade",
        "projetar_fragmentos_para_emissao",
    }

    classes = [no.name for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)]
    assert classes == []
