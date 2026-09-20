"""Testes da **primitiva única de emissibilidade** de um fragmento.

Tudo aqui é **estrutural e sintético**: rótulos de status, caminhos YAML e
predicados têm a **forma** do corpus, nunca o seu conteúdo. **Zero valor
comercial** aparece — nenhum preço, capacidade, horário, prazo, percentual,
quantidade ou frase aprovada —, e `knowledge/**` **não é aberto**.

A suíte prova três coisas distintas: **(1)** a primitiva aplica `D8-F` e
`D8-CII` na ordem fixa, sobre uma fotografia já recebida; **(2)** ela **não**
conhece assunto, causa, motivo, cobertura ou evento; **(3)** os *gates* que
**continuam** sendo de S2-D8 — a validação da fotografia factual e a coerência
do `ResultadoConsistencia` — **não se mudaram** para cá com a extração.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from casa77_sdr.coverage_decision import (
    DecisaoCoberturaNaoAvaliavel,
    decidir_pendencias_e_cobertura,
)
from casa77_sdr.fragment_emissibility import (
    FotografiaFragmento,
    ImpedimentoEmissao,
    ResultadoEmissibilidade,
    avaliar_emissibilidade,
)
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import DadosExtraidos, Interpretacao
from casa77_sdr.qualification import (
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.response_assertion import AssertivaNaoAvaliavel

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "fragment_emissibility.py"
MODULO_S2D8 = RAIZ / "src" / "casa77_sdr" / "coverage_decision.py"

# Rotulos canonicos de `C-3` — estruturais, nunca conteudo.
APROVADO = "APROVADO"
AGUARDA = "AGUARDA_APROVACAO"
BLOQUEADO = "BLOQUEADO"

# Predicados do vocabulario fechado de `C-5`.
EH_VERDADEIRO = "EH_VERDADEIRO"
EH_FALSO = "EH_FALSO"

# Caminhos **sinteticos**, na forma estrutural de um `caminho_yaml`.
CAMINHO_A = "secao_sintetica.campo_a"
CAMINHO_B = "secao_sintetica.campo_b"
CAMINHO_C = "secao_sintetica.campo_c"

SEM_CAMINHO = ImpedimentoEmissao()


def _arvore(caminho: Path) -> ast.Module:
    return ast.parse(caminho.read_text(encoding="utf-8"))


def _codigo_sem_prosa(caminho: Path) -> str:
    """O código sem docstring — prosa negativa não é acesso (mesma forma de S2-D8)."""
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
# FE-T1 — fragmento emitível


def test_fe_t1_aprovado_sem_impedimento_e_emitivel() -> None:
    resultado = avaliar_emissibilidade(FotografiaFragmento(status=APROVADO))

    assert resultado.emitivel is True
    assert resultado.impedimentos == ()


def test_fe_t1_resultado_vazio_por_padrao_e_emitivel() -> None:
    assert ResultadoEmissibilidade().emitivel is True


# ---------------------------------------------------------------------------
# FE-T2 — status não emitível (D8-F1, D8-F4)


@pytest.mark.parametrize("status", [AGUARDA, BLOQUEADO], ids=["aguarda", "bloqueado"])
def test_fe_t2_status_nao_emitivel_produz_um_impedimento_sem_caminho(
    status: str,
) -> None:
    resultado = avaliar_emissibilidade(FotografiaFragmento(status=status))

    assert resultado.emitivel is False
    assert resultado.impedimentos == (SEM_CAMINHO,)


def test_fe_t2_rotulo_desconhecido_nao_habilita() -> None:
    """*Fail-closed*: só `APROVADO` habilita; nada mais é presumido."""
    resultado = avaliar_emissibilidade(FotografiaFragmento(status="OUTRO"))

    assert resultado.impedimentos == (SEM_CAMINHO,)


# ---------------------------------------------------------------------------
# FE-T3 — curto-circuito do status


def test_fe_t3_status_nao_emitivel_curto_circuita_o_resto() -> None:
    """Divergência, `C-7` e runtime **não são avaliados** sem aprovação."""
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=BLOQUEADO,
            divergente=True,
            referentes_indisponiveis=(CAMINHO_A, CAMINHO_B),
            assertivas_runtime=((EH_VERDADEIRO, False),),
        )
    )

    assert resultado.impedimentos == (SEM_CAMINHO,)


def test_fe_t3_curto_circuito_nao_avalia_predicado_invalido() -> None:
    """Prova de que a avaliação **nem chega** ao runtime: nada é levantado."""
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=AGUARDA, assertivas_runtime=(("PREDICADO_INEXISTENTE", True),)
        )
    )

    assert resultado.impedimentos == (SEM_CAMINHO,)


# ---------------------------------------------------------------------------
# FE-T4 — Classe II (D8-CII)


def test_fe_t4_divergencia_produz_impedimento_sem_caminho() -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(status=APROVADO, divergente=True)
    )

    assert resultado.emitivel is False
    assert resultado.impedimentos == (SEM_CAMINHO,)


# ---------------------------------------------------------------------------
# FE-T5 — `C-7`, um impedimento por referente


def test_fe_t5_um_referente_produz_um_impedimento_com_caminho() -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(status=APROVADO, referentes_indisponiveis=(CAMINHO_A,))
    )

    assert resultado.impedimentos == (ImpedimentoEmissao(CAMINHO_A),)


def test_fe_t5_varios_referentes_preservam_a_ordem_fisica() -> None:
    """**D8-E4**: um impedimento por referente, na ordem recebida."""
    recebidos = (CAMINHO_C, CAMINHO_A, CAMINHO_B)

    resultado = avaliar_emissibilidade(
        FotografiaFragmento(status=APROVADO, referentes_indisponiveis=recebidos)
    )

    assert resultado.impedimentos == tuple(
        ImpedimentoEmissao(caminho) for caminho in recebidos
    )


def test_fe_t5_ordem_dos_referentes_nao_e_lexical() -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=APROVADO, referentes_indisponiveis=(CAMINHO_C, CAMINHO_A)
        )
    )

    caminhos = tuple(item.caminho_yaml for item in resultado.impedimentos)

    assert caminhos == (CAMINHO_C, CAMINHO_A)
    assert caminhos != tuple(sorted(caminhos))


# ---------------------------------------------------------------------------
# FE-T6 — acúmulo de causas estruturais


def test_fe_t6_divergencia_e_referente_produzem_os_dois_na_ordem_fixa() -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=APROVADO, divergente=True, referentes_indisponiveis=(CAMINHO_A,)
        )
    )

    assert resultado.impedimentos == (SEM_CAMINHO, ImpedimentoEmissao(CAMINHO_A))


def test_fe_t6_ordem_fixa_classe_ii_depois_c7_depois_runtime() -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=APROVADO,
            divergente=True,
            referentes_indisponiveis=(CAMINHO_A, CAMINHO_B),
            assertivas_runtime=((EH_VERDADEIRO, False),),
        )
    )

    assert resultado.impedimentos == (
        SEM_CAMINHO,
        ImpedimentoEmissao(CAMINHO_A),
        ImpedimentoEmissao(CAMINHO_B),
        SEM_CAMINHO,
    )


# ---------------------------------------------------------------------------
# FE-T7 — `ASSERTIVA` de runtime (D8-F3)


@pytest.mark.parametrize(
    ("predicado", "valor"),
    [(EH_VERDADEIRO, True), (EH_FALSO, False)],
    ids=["eh_verdadeiro", "eh_falso"],
)
def test_fe_t7_assertiva_verdadeira_nao_acrescenta_impedimento(
    predicado: str, valor: bool
) -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(status=APROVADO, assertivas_runtime=((predicado, valor),))
    )

    assert resultado.emitivel is True


@pytest.mark.parametrize(
    ("predicado", "valor"),
    [(EH_VERDADEIRO, False), (EH_FALSO, True)],
    ids=["eh_verdadeiro", "eh_falso"],
)
def test_fe_t7_assertiva_falsa_produz_impedimento_sem_caminho(
    predicado: str, valor: bool
) -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(status=APROVADO, assertivas_runtime=((predicado, valor),))
    )

    assert resultado.impedimentos == (SEM_CAMINHO,)


def test_fe_t7_predicado_fora_do_vocabulario_atravessa_intacto() -> None:
    """`AssertivaNaoAvaliavel` **não** vira impedimento nem veredito."""
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_emissibilidade(
            FotografiaFragmento(
                status=APROVADO, assertivas_runtime=(("EH_TALVEZ", True),)
            )
        )

    assert str(erro.value) == "valor_invalido: predicado"


def test_fe_t7_valor_nao_booleano_atravessa_intacto() -> None:
    with pytest.raises(AssertivaNaoAvaliavel) as erro:
        avaliar_emissibilidade(
            FotografiaFragmento(
                status=APROVADO, assertivas_runtime=((EH_VERDADEIRO, 1),)
            )
        )

    assert str(erro.value) == "tipo_invalido: valor"


# ---------------------------------------------------------------------------
# FE-T8 — zero deduplicação interna


def test_fe_t8_referentes_repetidos_nao_sao_deduplicados() -> None:
    """Deduplicar é decisão da **projeção posterior** de S2-D8 (**D8-E4**)."""
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=APROVADO, referentes_indisponiveis=(CAMINHO_A, CAMINHO_A)
        )
    )

    assert resultado.impedimentos == (
        ImpedimentoEmissao(CAMINHO_A),
        ImpedimentoEmissao(CAMINHO_A),
    )


def test_fe_t8_assertivas_falsas_repetidas_nao_sao_deduplicadas() -> None:
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=APROVADO,
            assertivas_runtime=((EH_VERDADEIRO, False), (EH_FALSO, True)),
        )
    )

    assert resultado.impedimentos == (SEM_CAMINHO, SEM_CAMINHO)


# ---------------------------------------------------------------------------
# FE-T9 — a primitiva não conhece o vocabulário de S2-D8


@pytest.mark.parametrize(
    "termo",
    [
        "AssuntoComercial",
        "PerguntaComercial",
        "CausaE09",
        "MotivoE09",
        "ClassificacaoPendencia",
        "witness",
        "cobertura",
        "grupo",
        "Evento",
        "AcaoMaquina",
        "handoff",
    ],
)
def test_fe_t9_nenhum_vocabulario_de_cobertura_no_codigo(termo: str) -> None:
    assert termo not in _codigo_sem_prosa(MODULO)


# ---------------------------------------------------------------------------
# FE-T10 — pureza por AST


def test_fe_t10_importa_somente_o_necessario() -> None:
    assert _importados(MODULO) == {
        "__future__",
        "dataclasses",
        "casa77_sdr.response_assertion",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "os",
        "sys",
        "io",
        "pathlib",
        "yaml",
        "json",
        "time",
        "datetime",
        "random",
        "logging",
        "socket",
        "importlib",
        "casa77_sdr.knowledge",
        "casa77_sdr.state_machine",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.coverage_map",
        "casa77_sdr.interpretation",
        "casa77_sdr.emission_projection",
    ],
)
def test_fe_t10_nao_importa_o_proibido(proibido: str) -> None:
    assert proibido not in _importados(MODULO)


@pytest.mark.parametrize(
    "termo", ["open(", "knowledge", "Path", "requests", "datetime", "sleep"]
)
def test_fe_t10_nenhum_acesso_externo_no_codigo(termo: str) -> None:
    assert termo not in _codigo_sem_prosa(MODULO)


def test_fe_t10_superficie_publica_fechada() -> None:
    import casa77_sdr.fragment_emissibility as modulo

    assert modulo.__all__ == [
        "FotografiaFragmento",
        "ImpedimentoEmissao",
        "ResultadoEmissibilidade",
        "avaliar_emissibilidade",
    ]


def test_fe_t10_dtos_sao_frozen_com_slots() -> None:
    for classe in (FotografiaFragmento, ImpedimentoEmissao, ResultadoEmissibilidade):
        assert classe.__dataclass_params__.frozen is True
        assert classe.__dataclass_params__.slots is True


def test_fe_t10_nenhuma_excecao_publica_nova() -> None:
    """A primitiva é **total** sobre a fotografia: ela não valida forma."""
    arvore = _arvore(MODULO)
    classes = [
        no.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ClassDef)
        and any(
            isinstance(base, ast.Name) and base.id == "Exception" for base in no.bases
        )
    ]
    levanta = [no for no in ast.walk(arvore) if isinstance(no, ast.Raise)]

    assert classes == []
    assert levanta == []


# ---------------------------------------------------------------------------
# FE-T11 — os gates que continuam sendo de S2-D8


QUALIFICACAO = Qualificacao(
    ResultadoQualificacao.QUALIFICADO, MotivoQualificacao.COMPATIVEL
)

INTERPRETACAO = Interpretacao(
    intencoes_detectadas=(),
    dados_extraidos=DadosExtraidos(),
    correcoes=(),
    perguntas_comerciais=(),
    pedido_de_humano=False,
    confianca_pedido_de_humano=None,
    referencias_evento_anterior=(),
    confianca_global=Confianca.ALTA,
    trechos_ambiguos=(),
)


def test_fe_t11_fotografia_de_runtime_invalida_continua_fechando_em_s2d8() -> None:
    """A precedência não se mudou: `fatos_runtime` fecha **antes** do índice."""
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir_pendencias_e_cobertura(
            INTERPRETACAO,
            QUALIFICACAO,
            mapa=object(),
            indice=object(),
            consistencia=object(),
            fatos_runtime="nao-e-dicionario",
        )

    assert str(erro.value) == "tipo_invalido: fatos_runtime"


def test_fe_t11_coerencia_continua_sendo_julgada_em_s2d8() -> None:
    """`_validar_consistencia` **não** migrou para a primitiva.

    A **projeção de `C-7` para a fotografia** saiu de S2-D8 — ela pertence
    agora à fronteira única de montagem —, e por isso
    `_projetar_indisponiveis` **deixou de existir aqui**: o que se prova é que
    ela não sobreviveu como *helper* morto. Os **gates** que continuam sendo de
    S2-D8 permanecem em S2-D8 e **não** migraram para a primitiva de
    emissibilidade.
    """
    nomes_s2d8 = {
        no.name
        for no in ast.walk(_arvore(MODULO_S2D8))
        if isinstance(no, ast.FunctionDef)
    }
    nomes_primitiva = {
        no.name for no in ast.walk(_arvore(MODULO)) if isinstance(no, ast.FunctionDef)
    }

    for gate in (
        "_validar_consistencia",
        "_validar_fatos_runtime",
        "_projetar_runtime",
        "_e_candidato",
        "_e_candidato_por_faixa",
    ):
        assert gate in nomes_s2d8
        assert gate not in nomes_primitiva

    assert "_projetar_indisponiveis" not in nomes_s2d8
    assert "_projetar_indisponiveis" not in nomes_primitiva


def test_fe_t11_s2d8_consome_a_primitiva_compartilhada() -> None:
    assert "casa77_sdr.fragment_emissibility" in _importados(MODULO_S2D8)
