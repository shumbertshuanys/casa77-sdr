"""Testes do produtor determinístico de **S2-D8**.

Tudo aqui é **sintético**: os `Rxx`, os fragmentos, os caminhos e os
agrupamentos são inventados para exercitar a **decisão**, e **nenhum deles é
mapeamento real de cobertura**. Nenhum teste abre `knowledge/**`, nenhum cria
`knowledge/mapa-cobertura.yaml` e **nenhum valor comercial real** aparece como
conteúdo ou como expectativa.

Os `AssuntoComercial` empregados são membros reais do enum de **AJ2**, porque o
vocabulário é reutilizado e nunca duplicado. As estruturas sintéticas servem
para **isolar S2-D8**; a cobertura sobre o **corpus real** é testada em
`tests/test_mapa_cobertura_corpus.py`.

Os identificadores `R05/F1`, `R05/F2` e `R05/F3` aparecem porque o **gate de
candidatura** arbitrado os nomeia estruturalmente, como §4.1.5 nomeia `R03/F1`.
Os fragmentos usados aqui têm a **forma** do corpus, nunca o seu texto.

A prova de que a fronteira não conhece LLM, rede, relógio, `filesystem`,
calendário e máquina de estados é feita sobre a **AST do módulo de produção**.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr.coverage_decision import (
    CausaE09,
    ClassificacaoPendencia,
    DecisaoCoberturaNaoAvaliavel,
    MotivoE09,
    ResultadoS2D8,
    decidir_pendencias_e_cobertura,
)
from casa77_sdr.coverage_map import MapaCoberturaInvalido
from casa77_sdr.emission_projection import projetar_fragmentos_para_emissao
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    AssuntoComercial,
    DadosExtraidos,
    Interpretacao,
    PerguntaComercial,
)
from casa77_sdr.pricing_applicability import AplicabilidadePacote
from casa77_sdr.qualification import (
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.response_consistency import (
    CategoriaDivergencia,
    Divergencia,
    ReferenteIndisponivel,
    ResultadoConsistencia,
)
from casa77_sdr.response_index import IndiceInvalido
from casa77_sdr.response_index_tokens import ProjecaoDeIdentidadeInvalida

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "coverage_decision.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

PRECO = AssuntoComercial.PRECO_LOCACAO
CAPACIDADE = AssuntoComercial.CAPACIDADE_MAXIMA_E_FORMATO
DESCONTO = AssuntoComercial.DESCONTO
NAO_CLASSIFICADO = AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO

VALORES_CANONICOS = [membro.value for membro in AssuntoComercial]

APROVADO = "APROVADO"
AGUARDA = "AGUARDA_APROVACAO"
BLOQUEADO = "BLOQUEADO"

QUALIFICACAO = Qualificacao(
    ResultadoQualificacao.QUALIFICADO, MotivoQualificacao.COMPATIVEL
)


# --------------------------------------------------------------------------
# Fixtures sinteticos


def indice_de(*respostas: tuple[str, tuple[tuple[str, str], ...]]) -> dict[str, Any]:
    """Índice **sintético** de fragmentos sem *binding*, na forma de `C-2`."""
    return {
        "respostas": [
            {
                "id": rxx,
                "fragmentos": [
                    {"id": fid, "status": status, "bindings": []}
                    for fid, status in fragmentos
                ],
            }
            for rxx, fragmentos in respostas
        ]
    }


def binding_runtime(nome: str, fato: str, predicado: str) -> dict[str, Any]:
    return {
        "nome": nome,
        "mecanismo": "ASSERTIVA",
        "origem": "RUNTIME_AUTORITATIVO",
        "fato_runtime": fato,
        "predicado": predicado,
    }


def indice_r05() -> dict[str, Any]:
    """Índice **sintético** com a **forma** de `R05` — zero texto, zero valor."""
    return {
        "respostas": [
            {
                "id": "R05",
                "fragmentos": [
                    {"id": "F1", "status": APROVADO, "bindings": []},
                    {
                        "id": "F2",
                        "status": APROVADO,
                        "bindings": [
                            binding_runtime(
                                "consulta_calendario_valida",
                                "consulta_calendario_valida",
                                "EH_VERDADEIRO",
                            ),
                            binding_runtime(
                                "data_disponivel",
                                "data_disponivel",
                                "EH_VERDADEIRO",
                            ),
                        ],
                    },
                    {
                        "id": "F3",
                        "status": APROVADO,
                        "bindings": [
                            binding_runtime(
                                "consulta_calendario_valida",
                                "consulta_calendario_valida",
                                "EH_VERDADEIRO",
                            ),
                            binding_runtime(
                                "data_disponivel",
                                "data_disponivel",
                                "EH_FALSO",
                            ),
                        ],
                    },
                ],
            }
        ]
    }


INDICE_PADRAO = indice_de(
    ("R40", (("F1", APROVADO), ("F2", APROVADO))),
    ("R41", (("F1", APROVADO), ("F2", APROVADO))),
)


def tokens_do(indice: dict[str, Any]) -> list[str]:
    return [
        f"{resposta['id']}/{fragmento['id']}"
        for resposta in indice["respostas"]
        for fragmento in resposta["fragmentos"]
    ]


def divergencia(
    token: str,
    categoria: CategoriaDivergencia = CategoriaDivergencia.ASSERTIVA_FALSA,
) -> Divergencia:
    rxx, fid = token.split("/")
    return Divergencia(
        token=token,
        rxx=rxx,
        fragmento_id=fid,
        binding="sintetico",
        mecanismo="ASSERTIVA",
        origem="YAML",
        referente="bloco.campo",
        categoria=categoria,
    )


def indisponivel(
    token: str, mecanismo: str = "RENDERIZADO", referente: str = "bloco.campo"
) -> ReferenteIndisponivel:
    rxx, fid = token.split("/")
    return ReferenteIndisponivel(
        token=token,
        rxx=rxx,
        fragmento_id=fid,
        binding="sintetico",
        mecanismo=mecanismo,
        origem="YAML",
        referente=referente,
    )


def registro_runtime_de(indice: dict[str, Any]) -> tuple[str, ...]:
    """`<token>.<nome>` de todo *binding* runtime, na ordem física (VCB-7)."""
    registro: list[str] = []
    for resposta in indice["respostas"]:
        for fragmento in resposta["fragmentos"]:
            token = f"{resposta['id']}/{fragmento['id']}"
            registro.extend(
                f"{token}.{binding['nome']}"
                for binding in fragmento["bindings"]
                if binding["origem"] == "RUNTIME_AUTORITATIVO"
            )
    return tuple(registro)


def consistencia_de(
    indice: dict[str, Any],
    *,
    divergencias: tuple[Divergencia, ...] = (),
    indisponiveis: tuple[ReferenteIndisponivel, ...] = (),
    runtime_nao_avaliados: tuple[str, ...] | None = None,
    tokens_divergentes: tuple[str, ...] | None = None,
) -> ResultadoConsistencia:
    """`ResultadoConsistencia` **coerente** com o índice, por padrão.

    `runtime_nao_avaliados` e `tokens_divergentes` são derivados do índice e das
    divergências; os parâmetros existem **apenas** para construir resultados
    deliberadamente incoerentes nos testes de Classe I.
    """
    status: list[tuple[str, str]] = []
    for resposta in indice["respostas"]:
        for fragmento in resposta["fragmentos"]:
            status.append(
                (f"{resposta['id']}/{fragmento['id']}", fragmento["status"])
            )
    derivados: list[str] = []
    for item in divergencias:
        if item.token not in derivados:
            derivados.append(item.token)
    return ResultadoConsistencia(
        divergencias=divergencias,
        referentes_indisponiveis=indisponiveis,
        tokens_divergentes=(
            tuple(derivados) if tokens_divergentes is None else tokens_divergentes
        ),
        status_por_fragmento=tuple(status),
        bindings_runtime_nao_avaliados=(
            registro_runtime_de(indice)
            if runtime_nao_avaliados is None
            else runtime_nao_avaliados
        ),
    )


def alternativa(token: str) -> dict[str, str]:
    rxx, fid = token.split("/")
    return {"rxx": rxx, "fragmento": fid}


def grupos(*blocos: tuple[str, ...]) -> list[dict[str, Any]]:
    return [
        {"alternativas": [alternativa(token) for token in bloco]}
        for bloco in blocos
    ]


def mapa_de(*itens: tuple[AssuntoComercial, list[dict[str, Any]]]) -> dict[str, Any]:
    """Mapa **total** — os 54 assuntos, com grupos só onde declarado."""
    declarados = {assunto.value: corpo for assunto, corpo in itens}
    return {
        "assuntos": [
            {"assunto": valor, "grupos": declarados.get(valor, [])}
            for valor in VALORES_CANONICOS
        ]
    }


def pergunta(
    assunto: AssuntoComercial, confianca: Confianca = Confianca.ALTA
) -> PerguntaComercial:
    return PerguntaComercial(
        texto="pergunta sintética", confianca=confianca, assunto=assunto
    )


def interpretacao_de(*perguntas: PerguntaComercial) -> Interpretacao:
    return Interpretacao(
        intencoes_detectadas=(),
        dados_extraidos=DadosExtraidos(),
        correcoes=(),
        perguntas_comerciais=tuple(perguntas),
        pedido_de_humano=False,
        confianca_pedido_de_humano=None,
        referencias_evento_anterior=(),
        confianca_global=Confianca.ALTA,
        trechos_ambiguos=(),
    )


def decidir(
    *,
    interpretacao: Any = None,
    mapa: Any = None,
    indice: Any = None,
    consistencia: Any = None,
    fatos_runtime: Any = None,
    qualificacao: Any = QUALIFICACAO,
    aplicabilidade: Any = None,
) -> ResultadoS2D8:
    indice = INDICE_PADRAO if indice is None else indice
    return decidir_pendencias_e_cobertura(
        interpretacao_de() if interpretacao is None else interpretacao,
        qualificacao,
        mapa_de() if mapa is None else mapa,
        indice,
        consistencia_de(indice) if consistencia is None else consistencia,
        {} if fatos_runtime is None else fatos_runtime,
        aplicabilidade,
    )


def categoria_de(erro: pytest.ExceptionInfo[Any]) -> str:
    return str(erro.value).split(":", 1)[0]


def sem_resposta(assunto: AssuntoComercial) -> CausaE09:
    """Causa do eixo B — sempre **`ACESSORIA`** e **sem** `caminho_yaml`."""
    return CausaE09(
        MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL,
        ClassificacaoPendencia.ACESSORIA,
        assunto,
    )


def campo_indisponivel(assunto: AssuntoComercial, caminho: str) -> CausaE09:
    """Causa do eixo B — **`ACESSORIA`**, com o `caminho_yaml` transportado."""
    return CausaE09(
        MotivoE09.CAMPO_INDISPONIVEL,
        ClassificacaoPendencia.ACESSORIA,
        assunto,
        caminho,
    )


# --------------------------------------------------------------------------
# 1. Eixo A — Q1 literal


def test_eixo_a_nunca_produz_pendencia_impeditiva() -> None:
    resultado = decidir()

    assert resultado.pendencia_impeditiva is False
    assert resultado.pendencias_impeditivas == ()


@pytest.mark.parametrize("resultado_q", list(ResultadoQualificacao))
def test_eixo_a_independe_da_qualificacao_recebida(
    resultado_q: ResultadoQualificacao,
) -> None:
    qualificacao = Qualificacao(resultado_q, MotivoQualificacao.COMPATIVEL)

    resultado = decidir(qualificacao=qualificacao)

    assert resultado.pendencia_impeditiva is False
    assert resultado.pendencias_impeditivas == ()


def test_eixo_a_nunca_produz_causa() -> None:
    """Zero pergunta: nenhuma causa pode vir do eixo A no schema vigente."""
    assert decidir().causas_e09 == ()


# --------------------------------------------------------------------------
# 2. Perguntas efetivas


def test_zero_perguntas() -> None:
    resultado = decidir()

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert resultado.pendencias_resposta == ()
    assert resultado.causas_e09 == ()


def test_somente_baixa_nao_entra() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO, Confianca.BAIXA)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
    )

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert resultado.pendencias_resposta == ()
    assert resultado.causas_e09 == ()


def test_baixa_nao_entra_em_pendencias_mesmo_descoberta() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO, Confianca.BAIXA)),
        mapa=mapa_de(),
    )

    assert resultado.pendencias_resposta == ()
    assert resultado.causas_e09 == ()


def test_uma_alta_coberta() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
    )

    assert resultado.resposta_aprovada_disponivel is True
    assert resultado.fragmentos_autorizados == ("R40/F1",)
    assert resultado.pendencias_resposta == ()
    assert resultado.causas_e09 == ()


# --------------------------------------------------------------------------
# 3. Grupos — conjuncao, disjuncao e witness


def test_dois_grupos_produzem_dois_witnesses() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",), ("R41/F1",)))),
    )

    assert resultado.fragmentos_autorizados == ("R40/F1", "R41/F1")


def test_primeira_alternativa_bloqueada_segunda_segura() -> None:
    indice = indice_de(("R40", (("F1", BLOQUEADO), ("F2", APROVADO))))

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa_de((PRECO, grupos(("R40/F1", "R40/F2")))),
    )

    assert resultado.fragmentos_autorizados == ("R40/F2",)
    assert resultado.causas_e09 == ()
    assert resultado.resposta_aprovada_disponivel is True


def test_witness_e_a_primeira_emitivel_na_ordem_declarada() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R41/F2", "R40/F1")))),
    )

    assert resultado.fragmentos_autorizados == ("R41/F2",)


def test_grupo_descoberto_zera_o_assunto_inteiro() -> None:
    """SF-D4-6: não existe resposta parcial de assunto."""
    indice = indice_de(("R40", (("F1", APROVADO), ("F2", BLOQUEADO))))

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa_de((PRECO, grupos(("R40/F1",), ("R40/F2",)))),
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
    )


def test_zero_grupos_nao_e_respondivel() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)), mapa=mapa_de()
    )

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
    )


def test_assunto_nao_classificado_nao_e_respondivel() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(NAO_CLASSIFICADO))
    )

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.causas_e09 == (
        sem_resposta(NAO_CLASSIFICADO),
    )


# --------------------------------------------------------------------------
# 4. Multiplos assuntos, duplicatas e dedupe


def test_assunto_duplicado_nao_repete_a_selecao() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO), pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
    )

    assert resultado.fragmentos_autorizados == ("R40/F1",)


def test_ordem_e_da_primeira_ocorrencia_efetiva() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(
            pergunta(CAPACIDADE), pergunta(PRECO), pergunta(CAPACIDADE)
        ),
        mapa=mapa_de(
            (PRECO, grupos(("R40/F1",))),
            (CAPACIDADE, grupos(("R41/F1",))),
        ),
    )

    assert resultado.fragmentos_autorizados == ("R41/F1", "R40/F1")


def test_multiplos_assuntos_mistos() -> None:
    """D8-T4e: um coberto e outro descoberto → `True` **mais** causa."""
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO), pergunta(CAPACIDADE)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
    )

    assert resultado.resposta_aprovada_disponivel is True
    assert resultado.fragmentos_autorizados == ("R40/F1",)
    assert resultado.causas_e09 == (
        sem_resposta(CAPACIDADE),
    )


def test_witness_duplicado_entre_assuntos_e_deduplicado() -> None:
    """SF-D4-9: dedupe global pela primeira ocorrência, preservando a ordem."""
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO), pergunta(CAPACIDADE)),
        mapa=mapa_de(
            (PRECO, grupos(("R40/F1",))),
            (CAPACIDADE, grupos(("R40/F1",), ("R41/F1",))),
        ),
    )

    assert resultado.fragmentos_autorizados == ("R40/F1", "R41/F1")


def test_witness_duplicado_dentro_do_mesmo_assunto_e_deduplicado() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",), ("R40/F1",)))),
    )

    assert resultado.fragmentos_autorizados == ("R40/F1",)


# --------------------------------------------------------------------------
# 5. D8-F — status


@pytest.mark.parametrize("status", [AGUARDA, BLOQUEADO])
def test_status_nao_emitivel_nao_habilita(status: str) -> None:
    indice = indice_de(("R40", (("F1", status),)))

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
    )


def test_status_nao_emitivel_em_grupo_coberto_nao_cria_causa() -> None:
    """D8-L2: alternativa bloqueada dentro de grupo coberto não cria lacuna."""
    indice = indice_de(("R40", (("F1", AGUARDA), ("F2", APROVADO))))

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa_de((PRECO, grupos(("R40/F1", "R40/F2")))),
    )

    assert resultado.causas_e09 == ()
    assert resultado.fragmentos_autorizados == ("R40/F2",)


# --------------------------------------------------------------------------
# 6. D8-F — C-7 e Classe II


def test_c7_renderizado_deixa_grupo_descoberto() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        indisponiveis=(indisponivel("R40/F1", "RENDERIZADO", "bloco.preco"),),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert resultado.causas_e09 == (
        campo_indisponivel(PRECO, "bloco.preco"),
    )
    assert resultado.fragmentos_autorizados == ()


def test_c7_assertiva_tambem_e_campo_indisponivel() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        indisponiveis=(indisponivel("R40/F1", "ASSERTIVA", "bloco.flag"),),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert resultado.causas_e09 == (
        campo_indisponivel(PRECO, "bloco.flag"),
    )


def test_assertiva_falsa_bloqueia_por_classe_ii() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        divergencias=(
            divergencia("R40/F1", CategoriaDivergencia.ASSERTIVA_FALSA),
        ),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
    )


def test_formato_inaplicavel_bloqueia_por_classe_ii() -> None:
    """R2F-12: é Classe II quando detectado a montante, não quarta condição."""
    consistencia = consistencia_de(
        INDICE_PADRAO,
        divergencias=(
            divergencia("R40/F1", CategoriaDivergencia.FORMATO_INAPLICAVEL),
        ),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
    )


def test_divergencia_em_grupo_coberto_nao_cria_causa() -> None:
    """D8-CII5: o ciclo continua se houver cobertura segura no mesmo grupo."""
    consistencia = consistencia_de(
        INDICE_PADRAO,
        divergencias=(
            divergencia("R40/F1", CategoriaDivergencia.FORMATO_INAPLICAVEL),
        ),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1", "R40/F2")))),
        consistencia=consistencia,
    )

    assert resultado.fragmentos_autorizados == ("R40/F2",)
    assert resultado.causas_e09 == ()


def test_multiplas_causas_deduplicadas_e_ordenadas() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        indisponiveis=(indisponivel("R40/F1", "RENDERIZADO", "bloco.a"),),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO), pergunta(CAPACIDADE)),
        mapa=mapa_de(
            (PRECO, grupos(("R40/F1",), ("R40/F1",))),
            (CAPACIDADE, grupos()),
        ),
        consistencia=consistencia,
    )

    assert resultado.causas_e09 == (
        campo_indisponivel(PRECO, "bloco.a"),
        sem_resposta(CAPACIDADE),
    )


def test_vocabulario_de_motivo_tem_exatamente_dois() -> None:
    assert [membro.name for membro in MotivoE09] == [
        "CAMPO_INDISPONIVEL",
        "SEM_RESPOSTA_APROVADA_EMITIVEL",
    ]


def test_vocabulario_de_classificacao_tem_exatamente_dois() -> None:
    assert [membro.name for membro in ClassificacaoPendencia] == [
        "IMPEDITIVA",
        "ACESSORIA",
    ]


def test_causa_tem_exatamente_quatro_campos() -> None:
    assert list(CausaE09.__dataclass_fields__) == [
        "motivo",
        "classificacao",
        "assunto",
        "caminho_yaml",
    ]


def test_causa_nao_possui_campo_referente() -> None:
    """O metadado normativo de `D8-E7` é `caminho_yaml`, não `referente`."""
    assert "referente" not in CausaE09.__dataclass_fields__
    assert not hasattr(campo_indisponivel(PRECO, "bloco.a"), "referente")


def test_causa_e_frozen_e_slots() -> None:
    causa = sem_resposta(PRECO)

    with pytest.raises(Exception):
        causa.motivo = MotivoE09.CAMPO_INDISPONIVEL  # type: ignore[misc]
    assert not hasattr(causa, "__dict__")


@pytest.mark.parametrize(
    "cenario",
    [
        "status",
        "divergencia",
        "c7",
        "zero_grupos",
        "nao_classificado",
        "runtime",
    ],
)
def test_toda_causa_do_eixo_b_e_acessoria(cenario: str) -> None:
    """D8-E6: causa do eixo B é **acessória**, sempre."""
    if cenario == "status":
        indice = indice_de(("R40", (("F1", BLOQUEADO),)))
        resultado = decidir(
            interpretacao=interpretacao_de(pergunta(PRECO)),
            indice=indice,
            mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        )
    elif cenario == "divergencia":
        resultado = decidir(
            interpretacao=interpretacao_de(pergunta(PRECO)),
            mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
            consistencia=consistencia_de(
                INDICE_PADRAO, divergencias=(divergencia("R40/F1"),)
            ),
        )
    elif cenario == "c7":
        resultado = decidir(
            interpretacao=interpretacao_de(pergunta(PRECO)),
            mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
            consistencia=consistencia_de(
                INDICE_PADRAO, indisponiveis=(indisponivel("R40/F1"),)
            ),
        )
    elif cenario == "zero_grupos":
        resultado = decidir(
            interpretacao=interpretacao_de(pergunta(PRECO)), mapa=mapa_de()
        )
    elif cenario == "nao_classificado":
        resultado = decidir(
            interpretacao=interpretacao_de(pergunta(NAO_CLASSIFICADO))
        )
    else:
        resultado = contexto_r05(
            fatos={"consulta_calendario_valida": True, "data_disponivel": True},
            ordem=("R05/F3",),
        )

    assert resultado.causas_e09 != ()
    assert all(
        causa.classificacao is ClassificacaoPendencia.ACESSORIA
        for causa in resultado.causas_e09
    )


def test_campo_indisponivel_leva_o_caminho_em_caminho_yaml() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        indisponiveis=(indisponivel("R40/F1", "RENDERIZADO", "bloco.campo_x"),),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    (causa,) = resultado.causas_e09
    assert causa.motivo is MotivoE09.CAMPO_INDISPONIVEL
    assert causa.caminho_yaml == "bloco.campo_x"
    assert causa.assunto is PRECO


def test_sem_resposta_aprovada_emitivel_nao_leva_caminho() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)), mapa=mapa_de()
    )

    (causa,) = resultado.causas_e09
    assert causa.motivo is MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL
    assert causa.caminho_yaml is None


def test_causa_nunca_carrega_rxx() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        indisponiveis=(indisponivel("R40/F1", "RENDERIZADO", "bloco.campo_x"),),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert "R40" not in repr(resultado.causas_e09)


def test_deduplicacao_considera_a_classificacao() -> None:
    """A identidade estrutural inclui `classificacao`: ela separa as causas."""
    acessoria = sem_resposta(PRECO)
    impeditiva = CausaE09(
        MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL,
        ClassificacaoPendencia.IMPEDITIVA,
        PRECO,
    )

    assert acessoria != impeditiva
    assert len({acessoria, impeditiva}) == 2
    assert acessoria == sem_resposta(PRECO)


def test_deduplicacao_colapsa_causa_identica_e_preserva_ordem() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO), pergunta(CAPACIDADE)),
        mapa=mapa_de(
            (PRECO, grupos(("R40/F1",), ("R40/F1",))),
            (CAPACIDADE, grupos()),
        ),
        indice=indice_de(("R40", (("F1", BLOQUEADO),))),
        consistencia=consistencia_de(indice_de(("R40", (("F1", BLOQUEADO),)))),
    )

    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
        sem_resposta(CAPACIDADE),
    )


# --------------------------------------------------------------------------
# 7. Runtime — gate de candidatura de R05


def contexto_r05(
    *, fatos: dict[str, bool], ordem: tuple[str, ...] = ("R05/F1", "R05/F2", "R05/F3")
) -> ResultadoS2D8:
    indice = indice_r05()
    return decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa_de((PRECO, grupos(ordem))),
        consistencia=consistencia_de(indice),
        fatos_runtime=fatos,
    )


def test_runtime_consulta_invalida_elege_f1() -> None:
    resultado = contexto_r05(fatos={"consulta_calendario_valida": False})

    assert resultado.fragmentos_autorizados == ("R05/F1",)
    assert resultado.causas_e09 == ()


def test_runtime_consulta_valida_e_disponivel_elege_f2() -> None:
    resultado = contexto_r05(
        fatos={"consulta_calendario_valida": True, "data_disponivel": True}
    )

    assert resultado.fragmentos_autorizados == ("R05/F2",)
    assert resultado.causas_e09 == ()


def test_runtime_consulta_valida_e_indisponivel_elege_f3() -> None:
    resultado = contexto_r05(
        fatos={"consulta_calendario_valida": True, "data_disponivel": False}
    )

    assert resultado.fragmentos_autorizados == ("R05/F3",)
    assert resultado.causas_e09 == ()


def test_runtime_f1_declarado_primeiro_nao_vence_com_consulta_valida() -> None:
    """O *fallback* não depende da ordem futura das alternativas em `R2`."""
    resultado = contexto_r05(
        fatos={"consulta_calendario_valida": True, "data_disponivel": True},
        ordem=("R05/F1", "R05/F2", "R05/F3"),
    )

    assert resultado.fragmentos_autorizados == ("R05/F2",)


def test_runtime_consulta_invalida_com_f1_seguro_nao_produz_e09() -> None:
    resultado = contexto_r05(
        fatos={"consulta_calendario_valida": False},
        ordem=("R05/F2", "R05/F3", "R05/F1"),
    )

    assert resultado.fragmentos_autorizados == ("R05/F1",)
    assert resultado.causas_e09 == ()
    assert resultado.resposta_aprovada_disponivel is True


def test_runtime_ausencia_de_consulta_e_classe_i() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        contexto_r05(fatos={})

    assert str(erro.value) == (
        "campo_ausente: fatos_runtime.consulta_calendario_valida"
    )


def test_runtime_consulta_valida_sem_data_e_classe_i() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        contexto_r05(
            fatos={"consulta_calendario_valida": True},
            ordem=("R05/F2",),
        )

    assert str(erro.value) == "campo_ausente: fatos_runtime.data_disponivel"


@pytest.mark.parametrize("valor", [0, 1, "True", None, [], 1.0])
def test_runtime_tipo_invalido_e_classe_i(valor: object) -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(fatos_runtime={"consulta_calendario_valida": valor})

    assert str(erro.value) == "tipo_invalido: fatos_runtime.valor"


def test_runtime_false_nao_equivale_a_ausencia() -> None:
    com_false = contexto_r05(fatos={"consulta_calendario_valida": False})

    assert com_false.fragmentos_autorizados == ("R05/F1",)
    with pytest.raises(DecisaoCoberturaNaoAvaliavel):
        contexto_r05(fatos={})


def test_runtime_chave_fora_do_vocabulario_e_classe_i() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(fatos_runtime={"outro_fato": True})

    assert str(erro.value) == "valor_invalido: fatos_runtime.chave"


def test_fatos_runtime_precisa_ser_dict() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(fatos_runtime=())

    assert str(erro.value) == "tipo_invalido: fatos_runtime"


def test_runtime_fora_do_contrato_arbitrado_fecha() -> None:
    indice = {
        "respostas": [
            {
                "id": "R40",
                "fragmentos": [
                    {
                        "id": "F1",
                        "status": APROVADO,
                        "bindings": [
                            binding_runtime(
                                "data_disponivel",
                                "data_disponivel",
                                "EH_VERDADEIRO",
                            )
                        ],
                    }
                ],
            }
        ]
    }

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(indice=indice, consistencia=consistencia_de(indice))

    assert str(erro.value) == "combinacao_invalida: indice.binding_runtime"


def test_runtime_predicado_e_avaliado_pela_fronteira_existente() -> None:
    """`R05/F3` exige `data_disponivel` falso: com `True` ele não é emitível."""
    resultado = contexto_r05(
        fatos={"consulta_calendario_valida": True, "data_disponivel": True},
        ordem=("R05/F3",),
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
    )


# --------------------------------------------------------------------------
# 8. Classe I — base nao avaliavel


def test_indice_invalido_propaga_intacto() -> None:
    with pytest.raises(IndiceInvalido):
        decidir(
            indice={"respostas": "nao-e-lista"},
            consistencia=consistencia_de(INDICE_PADRAO),
        )


def test_projecao_de_identidade_invalida_propaga_intacta() -> None:
    """`F01` passa por `validar_indice`, mas `C-A5-I3` o recusa."""
    indice = indice_de(("R40", (("F01", APROVADO),)))

    with pytest.raises(ProjecaoDeIdentidadeInvalida):
        decidir(indice=indice, consistencia=consistencia_de(indice))


def test_mapa_invalido_propaga_intacto() -> None:
    with pytest.raises(MapaCoberturaInvalido):
        decidir(mapa={"assuntos": []})


def test_referencia_pendurada_propaga_intacta() -> None:
    with pytest.raises(MapaCoberturaInvalido) as erro:
        decidir(mapa=mapa_de((PRECO, grupos(("R77/F9",)))))

    assert categoria_de(erro) == "referencia_pendurada"


def test_consistencia_de_tipo_invalido() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=object())

    assert str(erro.value) == "tipo_invalido: consistencia"


def test_consistencia_incompleta_fecha() -> None:
    parcial = ResultadoConsistencia(
        divergencias=(),
        referentes_indisponiveis=(),
        tokens_divergentes=(),
        status_por_fragmento=(("R40/F1", APROVADO),),
        bindings_runtime_nao_avaliados=(),
    )

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=parcial)

    assert str(erro.value) == "campo_ausente: consistencia.status_por_fragmento"


def test_consistencia_com_token_fora_do_dominio_fecha() -> None:
    consistencia = consistencia_de(INDICE_PADRAO)
    fora = ResultadoConsistencia(
        divergencias=(divergencia("R77/F1"),),
        referentes_indisponiveis=(),
        tokens_divergentes=("R77/F1",),
        status_por_fragmento=consistencia.status_por_fragmento,
        bindings_runtime_nao_avaliados=(),
    )

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=fora)

    assert str(erro.value) == "valor_invalido: consistencia.divergencias.item"


def test_tokens_divergentes_incoerente_fecha() -> None:
    consistencia = consistencia_de(INDICE_PADRAO)
    incoerente = ResultadoConsistencia(
        divergencias=(divergencia("R40/F1"),),
        referentes_indisponiveis=(),
        tokens_divergentes=(),
        status_por_fragmento=consistencia.status_por_fragmento,
        bindings_runtime_nao_avaliados=(),
    )

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=incoerente)

    assert str(erro.value) == (
        "combinacao_invalida: consistencia.tokens_divergentes"
    )


def test_status_fora_do_vocabulario_fecha() -> None:
    incoerente = ResultadoConsistencia(
        divergencias=(),
        referentes_indisponiveis=(),
        tokens_divergentes=(),
        status_por_fragmento=tuple(
            (token, "PARCIAL") for token in tokens_do(INDICE_PADRAO)
        ),
        bindings_runtime_nao_avaliados=(),
    )

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=incoerente)

    assert str(erro.value) == (
        "valor_invalido: consistencia.status_por_fragmento.item"
    )


def test_status_duplicado_fecha() -> None:
    duplicado = ResultadoConsistencia(
        divergencias=(),
        referentes_indisponiveis=(),
        tokens_divergentes=(),
        status_por_fragmento=tuple(
            (token, APROVADO) for token in tokens_do(INDICE_PADRAO)
        )
        + (("R40/F1", APROVADO),),
        bindings_runtime_nao_avaliados=(),
    )

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=duplicado)

    assert str(erro.value) == (
        "duplicidade: consistencia.status_por_fragmento.item"
    )


def test_binding_runtime_nao_avaliado_fora_do_dominio_fecha() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO, runtime_nao_avaliados=("R77/F1.flag",)
    )

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=consistencia)

    assert str(erro.value) == (
        "combinacao_invalida: consistencia.bindings_runtime_nao_avaliados"
    )


def test_interpretacao_de_tipo_invalido() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(interpretacao=object())

    assert str(erro.value) == "tipo_invalido: interpretacao"


def test_qualificacao_de_tipo_invalido() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(qualificacao=object())

    assert str(erro.value) == "tipo_invalido: qualificacao_provisoria"


def test_classe_i_nao_devolve_resultado_parcial() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel):
        decidir(consistencia=object())


# --------------------------------------------------------------------------
# 9. pendencias_resposta


def test_pendencias_resposta_registra_pergunta_nao_respondida() -> None:
    p1 = pergunta(PRECO)

    resultado = decidir(interpretacao=interpretacao_de(p1), mapa=mapa_de())

    assert resultado.pendencias_resposta == (p1,)


def test_pendencias_resposta_preserva_duplicatas() -> None:
    p1 = pergunta(PRECO)
    p2 = pergunta(PRECO)

    resultado = decidir(
        interpretacao=interpretacao_de(p1, p2), mapa=mapa_de()
    )

    assert resultado.pendencias_resposta == (p1, p2)


def test_pendencias_resposta_preserva_a_ordem_original() -> None:
    p1 = pergunta(CAPACIDADE)
    p2 = pergunta(PRECO)
    p3 = pergunta(DESCONTO)

    resultado = decidir(
        interpretacao=interpretacao_de(p1, p2, p3),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
    )

    assert resultado.pendencias_resposta == (p1, p3)


def test_pendencias_resposta_vazia_quando_tudo_coberto() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
    )

    assert resultado.pendencias_resposta == ()


# --------------------------------------------------------------------------
# 10. DTO, repr e pureza


def test_resultado_e_frozen_e_slots() -> None:
    resultado = decidir()

    with pytest.raises(Exception):
        resultado.pendencia_impeditiva = True  # type: ignore[misc]
    assert not hasattr(resultado, "__dict__")


def test_resultado_nao_possui_e09_confirmado() -> None:
    assert "e09_confirmado" not in ResultadoS2D8.__dataclass_fields__


def test_resultado_tem_exatamente_os_seis_campos() -> None:
    assert list(ResultadoS2D8.__dataclass_fields__) == [
        "pendencia_impeditiva",
        "pendencias_impeditivas",
        "resposta_aprovada_disponivel",
        "fragmentos_autorizados",
        "pendencias_resposta",
        "causas_e09",
    ]


def test_repr_nao_carrega_pergunta() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)), mapa=mapa_de()
    )

    assert "pendencias_resposta" not in repr(resultado)
    assert "pergunta sintética" not in repr(resultado)


def test_causa_nao_carrega_texto_nem_valor() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        indisponiveis=(indisponivel("R40/F1", "RENDERIZADO", "bloco.preco"),),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert "pergunta sintética" not in repr(resultado.causas_e09)


def test_entradas_nao_sao_mutadas() -> None:
    indice = copy.deepcopy(INDICE_PADRAO)
    mapa = mapa_de((PRECO, grupos(("R40/F1", "R40/F2"))))
    consistencia = consistencia_de(indice)
    fatos = {"consulta_calendario_valida": True, "data_disponivel": True}
    antes = (
        copy.deepcopy(indice),
        copy.deepcopy(mapa),
        copy.deepcopy(fatos),
    )

    decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa,
        consistencia=consistencia,
        fatos_runtime=fatos,
    )

    assert (indice, mapa, fatos) == antes


def test_decisao_e_deterministica() -> None:
    argumentos = {
        "interpretacao": interpretacao_de(pergunta(PRECO), pergunta(CAPACIDADE)),
        "mapa": mapa_de((PRECO, grupos(("R40/F1",)))),
    }

    assert decidir(**argumentos) == decidir(**argumentos)


# --------------------------------------------------------------------------
# 11. Compatibilidade com o ProjetorEmissao


def test_fragmentos_autorizados_alimentam_o_projetor() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO), pergunta(CAPACIDADE)),
        mapa=mapa_de(
            (PRECO, grupos(("R40/F1",))),
            (CAPACIDADE, grupos(("R40/F1",), ("R41/F1",))),
        ),
    )

    assert projetar_fragmentos_para_emissao(
        resultado.fragmentos_autorizados, ()
    ) == ("R40/F1", "R41/F1")


def test_projecao_vazia_tambem_e_aceita_pelo_projetor() -> None:
    resultado = decidir()

    assert projetar_fragmentos_para_emissao(
        resultado.fragmentos_autorizados, ()
    ) == ()


# --------------------------------------------------------------------------
# 11-bis. Coerencia exata do registro runtime e de tokens_divergentes


def test_registro_runtime_exato_e_aceito() -> None:
    indice = indice_r05()

    resultado = decidir(
        indice=indice,
        consistencia=consistencia_de(indice),
        fatos_runtime={"consulta_calendario_valida": False},
    )

    assert resultado.fragmentos_autorizados == ()


def test_registro_runtime_vazio_com_indice_runtime_fecha() -> None:
    indice = indice_r05()

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(
            indice=indice,
            consistencia=consistencia_de(indice, runtime_nao_avaliados=()),
        )

    assert str(erro.value) == (
        "combinacao_invalida: consistencia.bindings_runtime_nao_avaliados"
    )


def test_registro_runtime_faltante_fecha() -> None:
    indice = indice_r05()
    completo = registro_runtime_de(indice)

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(
            indice=indice,
            consistencia=consistencia_de(
                indice, runtime_nao_avaliados=completo[:-1]
            ),
        )

    assert str(erro.value) == (
        "combinacao_invalida: consistencia.bindings_runtime_nao_avaliados"
    )


def test_registro_runtime_extra_fecha() -> None:
    indice = indice_r05()
    completo = registro_runtime_de(indice)

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(
            indice=indice,
            consistencia=consistencia_de(
                indice,
                runtime_nao_avaliados=completo + ("R05/F2.data_disponivel",),
            ),
        )

    assert str(erro.value) == (
        "combinacao_invalida: consistencia.bindings_runtime_nao_avaliados"
    )


def test_registro_runtime_reordenado_fecha() -> None:
    """Mesmos itens, ordem física trocada: continua incoerente."""
    indice = indice_r05()
    completo = registro_runtime_de(indice)
    trocado = (completo[1], completo[0]) + completo[2:]

    assert sorted(trocado) == sorted(completo)
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(
            indice=indice,
            consistencia=consistencia_de(
                indice, runtime_nao_avaliados=trocado
            ),
        )

    assert str(erro.value) == (
        "combinacao_invalida: consistencia.bindings_runtime_nao_avaliados"
    )


def test_registro_runtime_tem_a_forma_token_ponto_nome() -> None:
    assert registro_runtime_de(indice_r05()) == (
        "R05/F2.consulta_calendario_valida",
        "R05/F2.data_disponivel",
        "R05/F3.consulta_calendario_valida",
        "R05/F3.data_disponivel",
    )


def test_tokens_divergentes_reordenado_fecha() -> None:
    """A comparação é **literal**, nunca por conjunto."""
    divergencias = (divergencia("R40/F1"), divergencia("R41/F1"))
    consistencia = consistencia_de(
        INDICE_PADRAO,
        divergencias=divergencias,
        tokens_divergentes=("R41/F1", "R40/F1"),
    )

    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(consistencia=consistencia)

    assert str(erro.value) == (
        "combinacao_invalida: consistencia.tokens_divergentes"
    )


def test_tokens_divergentes_na_ordem_de_primeira_ocorrencia_e_aceito() -> None:
    divergencias = (
        divergencia("R41/F1"),
        divergencia("R40/F1"),
        divergencia("R41/F1", CategoriaDivergencia.FORMATO_INAPLICAVEL),
    )
    consistencia = consistencia_de(INDICE_PADRAO, divergencias=divergencias)

    assert consistencia.tokens_divergentes == ("R41/F1", "R40/F1")
    assert decidir(consistencia=consistencia).causas_e09 == ()


# --------------------------------------------------------------------------
# 11-ter. Todas as causas estruturais da lacuna


def test_dois_referentes_indisponiveis_preservam_os_dois_caminhos() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        indisponiveis=(
            indisponivel("R40/F1", "RENDERIZADO", "bloco.primeiro"),
            indisponivel("R40/F1", "RENDERIZADO", "bloco.segundo"),
        ),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert resultado.causas_e09 == (
        campo_indisponivel(PRECO, "bloco.primeiro"),
        campo_indisponivel(PRECO, "bloco.segundo"),
    )


def test_divergencia_e_c7_no_mesmo_token_produzem_os_dois_motivos() -> None:
    consistencia = consistencia_de(
        INDICE_PADRAO,
        divergencias=(divergencia("R40/F1"),),
        indisponiveis=(indisponivel("R40/F1", "RENDERIZADO", "bloco.campo"),),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        consistencia=consistencia,
    )

    assert resultado.causas_e09 == (
        sem_resposta(PRECO),
        campo_indisponivel(PRECO, "bloco.campo"),
    )
    assert {causa.motivo for causa in resultado.causas_e09} == {
        MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL,
        MotivoE09.CAMPO_INDISPONIVEL,
    }


def test_alternativa_segura_no_mesmo_grupo_descarta_todas_as_causas() -> None:
    """D8-L2 é absoluto: grupo coberto não fabrica causa alguma."""
    consistencia = consistencia_de(
        INDICE_PADRAO,
        divergencias=(divergencia("R40/F1"),),
        indisponiveis=(
            indisponivel("R40/F1", "RENDERIZADO", "bloco.primeiro"),
            indisponivel("R40/F1", "RENDERIZADO", "bloco.segundo"),
        ),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1", "R40/F2")))),
        consistencia=consistencia,
    )

    assert resultado.fragmentos_autorizados == ("R40/F2",)
    assert resultado.causas_e09 == ()


# --------------------------------------------------------------------------
# 11-quater. Grupo descoberto sem alternativa candidata


def test_grupo_so_com_f2_f3_e_consulta_invalida_produz_causa() -> None:
    resultado = contexto_r05(
        fatos={"consulta_calendario_valida": False},
        ordem=("R05/F2", "R05/F3"),
    )

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert resultado.causas_e09 == (sem_resposta(PRECO),)


def test_grupo_so_com_f1_e_consulta_valida_produz_causa() -> None:
    resultado = contexto_r05(
        fatos={"consulta_calendario_valida": True, "data_disponivel": True},
        ordem=("R05/F1",),
    )

    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.fragmentos_autorizados == ()
    assert resultado.causas_e09 == (sem_resposta(PRECO),)


def test_caso_normal_com_f1_f2_f3_continua_sem_causa() -> None:
    for fatos in (
        {"consulta_calendario_valida": False},
        {"consulta_calendario_valida": True, "data_disponivel": True},
        {"consulta_calendario_valida": True, "data_disponivel": False},
    ):
        resultado = contexto_r05(fatos=fatos)

        assert len(resultado.fragmentos_autorizados) == 1
        assert resultado.causas_e09 == ()


# --------------------------------------------------------------------------
# 11-quinquies. D8-G — gate de candidatura de preco


INDICE_R09 = indice_de(("R09", (("F1", APROVADO), ("F2", APROVADO))))

# As duas faixas sao **grupos singleton**: nunca substitutas uma da outra.
MAPA_PRECO = mapa_de((PRECO, grupos(("R09/F1",), ("R09/F2",))))


def contexto_preco(
    *,
    aplicabilidade: Any,
    indice: Any = None,
    consistencia: Any = None,
) -> ResultadoS2D8:
    indice = INDICE_R09 if indice is None else indice
    return decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=MAPA_PRECO,
        consistencia=consistencia_de(indice) if consistencia is None else consistencia,
        aplicabilidade=aplicabilidade,
    )


def test_indeterminado_exige_as_duas_faixas() -> None:
    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.INDETERMINADO
    )

    assert resultado.fragmentos_autorizados == ("R09/F1", "R09/F2")
    assert resultado.resposta_aprovada_disponivel is True
    assert resultado.causas_e09 == ()


def test_indeterminado_com_f1_nao_emitivel_descobre_o_assunto() -> None:
    """Nunca só F2: as faixas não se substituem."""
    indice = indice_de(("R09", (("F1", BLOQUEADO), ("F2", APROVADO))))

    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.INDETERMINADO, indice=indice
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.causas_e09 == (sem_resposta(PRECO),)


def test_indeterminado_com_f2_nao_emitivel_descobre_o_assunto() -> None:
    """Nunca só F1."""
    indice = indice_de(("R09", (("F1", APROVADO), ("F2", BLOQUEADO))))

    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.INDETERMINADO, indice=indice
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.causas_e09 == (sem_resposta(PRECO),)


def test_faixa_inferior_elege_somente_f1() -> None:
    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.FAIXA_INFERIOR
    )

    assert resultado.fragmentos_autorizados == ("R09/F1",)
    assert resultado.causas_e09 == ()


def test_faixa_inferior_sem_f1_emitivel_nao_cai_em_f2() -> None:
    indice = indice_de(("R09", (("F1", BLOQUEADO), ("F2", APROVADO))))

    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.FAIXA_INFERIOR, indice=indice
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.causas_e09 == (sem_resposta(PRECO),)


def test_faixa_superior_elege_somente_f2() -> None:
    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.FAIXA_SUPERIOR
    )

    assert resultado.fragmentos_autorizados == ("R09/F2",)
    assert resultado.causas_e09 == ()


def test_faixa_superior_sem_f2_emitivel_nao_cai_em_f1() -> None:
    indice = indice_de(("R09", (("F1", APROVADO), ("F2", BLOQUEADO))))

    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.FAIXA_SUPERIOR, indice=indice
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.causas_e09 == (sem_resposta(PRECO),)


def test_nenhum_aplicavel_descobre_o_assunto() -> None:
    """D8-L4: zero grupos aplicáveis não é cobertura vazia verdadeira."""
    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.NENHUM_APLICAVEL
    )

    assert resultado.fragmentos_autorizados == ()
    assert resultado.resposta_aprovada_disponivel is False
    assert resultado.causas_e09 == (sem_resposta(PRECO),)
    assert resultado.pendencias_resposta != ()


def test_aplicabilidade_ausente_com_r09_avaliado_e_classe_i() -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        contexto_preco(aplicabilidade=None)

    assert str(erro.value) == "campo_ausente: aplicabilidade"


def test_aplicabilidade_ausente_sem_r09_no_ciclo_e_legitimo() -> None:
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1",)))),
        aplicabilidade=None,
    )

    assert resultado.fragmentos_autorizados == ("R40/F1",)


@pytest.mark.parametrize(
    "valor", ["FAIXA_INFERIOR", 0, 1, object(), ["FAIXA_INFERIOR"]]
)
def test_aplicabilidade_de_tipo_invalido_e_classe_i(valor: object) -> None:
    with pytest.raises(DecisaoCoberturaNaoAvaliavel) as erro:
        decidir(aplicabilidade=valor)

    assert str(erro.value) == "tipo_invalido: aplicabilidade"


def test_r05_permanece_inalterado_com_o_gate_de_preco() -> None:
    """Regressão: o gate de preço não toca o caminho de `R05`."""
    for fatos, esperado in (
        ({"consulta_calendario_valida": False}, "R05/F1"),
        (
            {"consulta_calendario_valida": True, "data_disponivel": True},
            "R05/F2",
        ),
        (
            {"consulta_calendario_valida": True, "data_disponivel": False},
            "R05/F3",
        ),
    ):
        resultado = contexto_r05(fatos=fatos)

        assert resultado.fragmentos_autorizados == (esperado,)
        assert resultado.causas_e09 == ()


def test_gate_nao_alcanca_token_fora_dos_cinco_autorizados() -> None:
    """Qualquer outro token do corpus continua candidato por padrão."""
    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        mapa=mapa_de((PRECO, grupos(("R40/F1", "R41/F1")))),
    )

    assert resultado.fragmentos_autorizados == ("R40/F1",)


# --------------------------------------------------------------------------
# 11-sexies. D8-L4 — grupos aplicaveis


def test_grupo_inaplicavel_sai_da_avaliacao_sem_causa() -> None:
    """Um grupo sem candidata não é coberto nem descoberto."""
    indice = indice_de(
        ("R09", (("F1", APROVADO), ("F2", APROVADO))),
        ("R40", (("F1", APROVADO),)),
    )

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa_de((PRECO, grupos(("R09/F2",), ("R40/F1",)))),
        consistencia=consistencia_de(indice),
        aplicabilidade=AplicabilidadePacote.FAIXA_INFERIOR,
    )

    assert resultado.fragmentos_autorizados == ("R40/F1",)
    assert resultado.resposta_aprovada_disponivel is True
    assert resultado.causas_e09 == ()


def test_grupo_parcialmente_candidato_preserva_a_semantica() -> None:
    """Com uma candidata segura no grupo, o grupo é coberto por ela."""
    indice = indice_de(("R09", (("F1", APROVADO), ("F2", APROVADO))))

    resultado = decidir(
        interpretacao=interpretacao_de(pergunta(PRECO)),
        indice=indice,
        mapa=mapa_de((PRECO, grupos(("R09/F1", "R09/F2")))),
        consistencia=consistencia_de(indice),
        aplicabilidade=AplicabilidadePacote.FAIXA_SUPERIOR,
    )

    assert resultado.fragmentos_autorizados == ("R09/F2",)
    assert resultado.causas_e09 == ()


def test_todos_os_grupos_inaplicaveis_produz_causa() -> None:
    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.NENHUM_APLICAVEL
    )

    assert resultado.causas_e09 == (sem_resposta(PRECO),)


def test_grupo_inaplicavel_nao_torna_assunto_verdadeiro_por_vacuidade() -> None:
    """Zero grupos aplicáveis nunca vira cobertura."""
    resultado = contexto_preco(
        aplicabilidade=AplicabilidadePacote.NENHUM_APLICAVEL
    )

    assert resultado.resposta_aprovada_disponivel is False


# --------------------------------------------------------------------------
# 12. Isolamento estrutural — provado sobre a AST do modulo


def _arvore(caminho: Path) -> ast.Module:
    return ast.parse(caminho.read_text(encoding="utf-8"))


def _modulos_importados(caminho: Path) -> set[str]:
    importados: set[str] = set()
    for no in ast.walk(_arvore(caminho)):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module is not None:
            importados.add(no.module)
    return importados


def _codigo_sem_prosa(caminho: Path) -> str:
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


def test_importa_somente_o_necessario() -> None:
    assert _modulos_importados(MODULO) == {
        "__future__",
        "dataclasses",
        "enum",
        "typing",
        "casa77_sdr.coverage_map",
        "casa77_sdr.fragment_emissibility",
        "casa77_sdr.fragment_snapshot",
        "casa77_sdr.identity",
        "casa77_sdr.interpretation",
        "casa77_sdr.pricing_applicability",
        "casa77_sdr.qualification",
        "casa77_sdr.response_consistency",
        "casa77_sdr.response_index",
        "casa77_sdr.response_index_tokens",
    }


@pytest.mark.parametrize(
    "proibido",
    [
        "casa77_sdr.state_machine",
        "casa77_sdr.knowledge",
        "casa77_sdr.rules",
        "casa77_sdr.persistence",
        "casa77_sdr.coverage_map_load",
        "casa77_sdr.response_index_load",
        "casa77_sdr.response_yaml_resolve",
        "casa77_sdr.response_format",
        "casa77_sdr.fact_selection",
        "casa77_sdr.response_composition",
        "casa77_sdr.emission_projection",
        "casa77_sdr.response_assembly",
        "casa77_sdr.response_validation",
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
def test_nao_importa_fronteira_proibida(proibido: str) -> None:
    assert proibido not in _modulos_importados(MODULO)


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
        "calendario_consultar",
        "sorted(",
        "reverse",
        ".sort(",
        "Evento",
        "AcaoMaquina",
        "e09_confirmado",
    ],
)
def test_superficie_executavel_nao_toca_fronteira_proibida(termo: str) -> None:
    assert termo not in _codigo_sem_prosa(MODULO)


def test_nao_menciona_caminho_de_knowledge_no_codigo() -> None:
    assert "knowledge" not in _codigo_sem_prosa(MODULO)


def test_codigo_nao_cita_nenhum_assunto_especifico() -> None:
    """Nenhum mapeamento real `AssuntoComercial → Rxx/Fxx` foi inventado."""
    codigo = _codigo_sem_prosa(MODULO)
    especificos = [
        membro.value
        for membro in AssuntoComercial
        if membro is not AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO
    ]

    assert [valor for valor in especificos if valor in codigo] == []


def test_unicos_rxx_citados_sao_os_do_gate_arbitrado() -> None:
    codigo = _codigo_sem_prosa(MODULO)
    literais = {
        no.value
        for no in ast.walk(ast.parse(codigo))
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    }

    suspeitos = {
        valor
        for valor in literais
        if len(valor) == 3 and valor[0] == "R" and valor[1:].isdigit()
    }
    assert suspeitos == {"R05", "R09"}


def test_nao_e_exportado_pelo_init() -> None:
    codigo = MODULO_INIT.read_text(encoding="utf-8")

    assert "coverage_decision" not in codigo
    assert "decidir_pendencias_e_cobertura" not in codigo


def test_api_publica_e_minima() -> None:
    from casa77_sdr import coverage_decision

    assert coverage_decision.__all__ == [
        "CausaE09",
        "ClassificacaoPendencia",
        "DecisaoCoberturaNaoAvaliavel",
        "MotivoE09",
        "ResultadoS2D8",
        "decidir_pendencias_e_cobertura",
    ]
