"""Testes do produtor determinístico de eventos da `Interpretacao` (`N-b-RES2`).

Cobre o contrato vivo de `docs/07-arquitetura-motor-respostas.md` §6.3
(`RES2-1`–`RES2-12`): o mapeamento fechado dos seis eventos, a regra
"`BAIXA` = ausência para consumo estruturado", os sinais que **não** geram
evento, a ordem canônica, o fecho da saída, a reutilização da validação de
canonicidade da fronteira N-b e a compatibilidade estrutural com a
`MaquinaEstados`.

`tests/test_interpretation.py` e `tests/test_state_machine.py` permanecem
**inalterados** e continuam as autoridades das suas próprias fronteiras.

Todas as fixtures são **fictícias e genéricas**: zero PII, zero conversa real,
zero valor comercial. Nenhum teste lê YAML, `knowledge/**`, rede ou credencial.
"""

from __future__ import annotations

import ast
import itertools
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import interpretation_events
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    AssuntoComercial,
    CorrecaoInterpretada,
    DadosExtraidos,
    EntradaInterpretacao,
    IntencaoAutonomaRecebida,
    IntencaoConversacional,
    IntencaoDetectada,
    Interpretacao,
    PerguntaComercial,
    ReferenciaAoEventoAnterior,
    TrechoAmbiguo,
    TrechoAmbiguoRecebido,
    canonicalizar_interpretacao,
)
from casa77_sdr.interpretation_events import produzir_eventos_da_interpretacao
from casa77_sdr.qualification import (
    FormatoEvento,
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.state_machine import (
    CondicoesCiclo,
    Estado,
    Evento,
    TransicaoInexistente,
    decidir,
)

MODULO_RES2 = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "casa77_sdr"
    / "interpretation_events.py"
)

ALTA = Confianca.ALTA
BAIXA = Confianca.BAIXA

ASSUNTO = AssuntoComercial.PRECO_LOCACAO
NAO_CLASSIFICADO = AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO

#: Conjunto fechado desta capacidade.
SEIS = (Evento.E02, Evento.E03, Evento.E04, Evento.E05, Evento.E06, Evento.E10)

#: Tudo que a fronteira **nunca** pode produzir.
PROIBIDOS = tuple(evento for evento in Evento if evento not in SEIS)


# --------------------------------------------------------------------------
# Fixtures genéricas
# --------------------------------------------------------------------------


def entrada(**ajustes: Any) -> EntradaInterpretacao:
    base: dict[str, Any] = {
        "dados_extraidos": DadosExtraidos(),
        "correcoes": (),
        "perguntas_comerciais": (),
        "pedido_de_humano": False,
        "confianca_pedido_de_humano": None,
        "referencias_evento_anterior": (),
        "trechos_ambiguos": (),
        "confianca_global": ALTA,
        "intencoes_autonomas": (),
    }
    base.update(ajustes)
    return EntradaInterpretacao(**base)  # type: ignore[arg-type]


def interpretacao(**ajustes: Any) -> Interpretacao:
    """Sempre canônica: passa pela fronteira determinística de N-b."""
    return canonicalizar_interpretacao(entrada(**ajustes))


def pergunta(
    confianca: Confianca = ALTA,
    texto: str = "quanto custa?",
    assunto: AssuntoComercial = ASSUNTO,
) -> PerguntaComercial:
    return PerguntaComercial(texto=texto, confianca=confianca, assunto=assunto)


def autonoma(
    codigo: IntencaoConversacional, confianca: Confianca = ALTA
) -> tuple[IntencaoAutonomaRecebida, ...]:
    return (IntencaoAutonomaRecebida(codigo=codigo, confianca=confianca),)


#: Valor genérico e confiança de cada campo que confirma um evento de dado.
VALOR_POR_CAMPO: dict[str, Any] = {
    "tipo_evento": "festa fictícia",
    "data_nomeada": "maio",
    "convidados": 60,
    "formato": FormatoEvento.SENTADO,
}

EVENTO_POR_CAMPO: dict[str, Evento] = {
    "tipo_evento": Evento.E02,
    "data_nomeada": Evento.E03,
    "convidados": Evento.E04,
    "formato": Evento.E05,
}


def dados(campo: str, confianca: Confianca | None) -> DadosExtraidos:
    """Um campo presente com a confiança dada; `None` deixa o campo ausente."""
    if confianca is None:
        return DadosExtraidos()
    return DadosExtraidos(
        **{campo: VALOR_POR_CAMPO[campo], f"confianca_{campo}": confianca}
    )


def interpretacao_com(eventos: frozenset[Evento]) -> Interpretacao:
    """Constrói a `Interpretacao` canônica que confirma **exatamente** `eventos`."""
    argumentos: dict[str, Any] = {}
    valores: dict[str, Any] = {}
    for campo, evento in EVENTO_POR_CAMPO.items():
        if evento in eventos:
            valores[campo] = VALOR_POR_CAMPO[campo]
            valores[f"confianca_{campo}"] = ALTA
    argumentos["dados_extraidos"] = DadosExtraidos(**valores)
    if Evento.E06 in eventos:
        argumentos["perguntas_comerciais"] = (pergunta(),)
    if Evento.E10 in eventos:
        argumentos["intencoes_autonomas"] = autonoma(
            IntencaoConversacional.INTERESSE_EM_VISITA
        )
    return interpretacao(**argumentos)


#: Os 63 subconjuntos **não vazios** dos seis eventos.
SUBCONJUNTOS: tuple[frozenset[Evento], ...] = tuple(
    frozenset(combinacao)
    for tamanho in range(1, len(SEIS) + 1)
    for combinacao in itertools.combinations(SEIS, tamanho)
)


def qual(
    resultado: ResultadoQualificacao, *, campos_ausentes: tuple[str, ...] = ()
) -> Qualificacao:
    motivos = {
        ResultadoQualificacao.DADOS_INCOMPLETOS: (
            MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES
        ),
        ResultadoQualificacao.QUALIFICADO: MotivoQualificacao.COMPATIVEL,
    }
    return Qualificacao(
        resultado=resultado,
        motivo=motivos[resultado],
        campos_ausentes=campos_ausentes,
    )


#: Qualificação **neutra e coerente** para o teste de compatibilidade: dados
#: ainda incompletos, sem `formato` entre os ausentes — nada é fabricado para
#: forçar PASS, e nenhuma guarda condicionada é ativada artificialmente.
INCOMPLETOS = qual(
    ResultadoQualificacao.DADOS_INCOMPLETOS, campos_ausentes=("nome", "contato")
)


# --------------------------------------------------------------------------
# Mapeamento por evento — ALTA confirma, BAIXA não, ausente não
# --------------------------------------------------------------------------


@pytest.mark.parametrize("campo", sorted(EVENTO_POR_CAMPO))
def test_campo_alta_confirma_o_evento_de_dado(campo: str) -> None:
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(dados_extraidos=dados(campo, ALTA))
    )
    assert resultado == (EVENTO_POR_CAMPO[campo],)


@pytest.mark.parametrize("campo", sorted(EVENTO_POR_CAMPO))
def test_campo_baixa_nao_confirma_o_evento_de_dado(campo: str) -> None:
    assert produzir_eventos_da_interpretacao(
        interpretacao(dados_extraidos=dados(campo, BAIXA))
    ) == ()


@pytest.mark.parametrize("campo", sorted(EVENTO_POR_CAMPO))
def test_campo_ausente_nao_confirma_o_evento_de_dado(campo: str) -> None:
    assert produzir_eventos_da_interpretacao(
        interpretacao(dados_extraidos=dados(campo, None))
    ) == ()


def test_pergunta_alta_confirma_e06() -> None:
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=(pergunta(ALTA),))
    )
    assert resultado == (Evento.E06,)


def test_pergunta_baixa_nao_confirma_e06() -> None:
    assert produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=(pergunta(BAIXA),))
    ) == ()


def test_ausencia_de_pergunta_nao_confirma_e06() -> None:
    assert produzir_eventos_da_interpretacao(interpretacao()) == ()


def test_interesse_em_visita_alta_confirma_e10() -> None:
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(
            intencoes_autonomas=autonoma(
                IntencaoConversacional.INTERESSE_EM_VISITA, ALTA
            )
        )
    )
    assert resultado == (Evento.E10,)


def test_interesse_em_visita_baixa_nao_confirma_e10() -> None:
    assert produzir_eventos_da_interpretacao(
        interpretacao(
            intencoes_autonomas=autonoma(
                IntencaoConversacional.INTERESSE_EM_VISITA, BAIXA
            )
        )
    ) == ()


def test_ausencia_de_interesse_em_visita_nao_confirma_e10() -> None:
    assert produzir_eventos_da_interpretacao(interpretacao()) == ()


# --------------------------------------------------------------------------
# `E06` — exatamente um, qualquer que seja a quantidade ou o assunto
# --------------------------------------------------------------------------


def test_varias_perguntas_alta_confirmam_um_unico_e06() -> None:
    perguntas = tuple(pergunta(ALTA, texto=f"pergunta {indice}") for indice in range(4))
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=perguntas)
    )
    assert resultado == (Evento.E06,)
    assert resultado.count(Evento.E06) == 1


def test_mistura_de_alta_e_baixa_confirma_um_unico_e06() -> None:
    perguntas = (pergunta(BAIXA), pergunta(ALTA), pergunta(BAIXA))
    assert produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=perguntas)
    ) == (Evento.E06,)


def test_todas_as_perguntas_baixa_nao_confirmam_e06() -> None:
    perguntas = (pergunta(BAIXA), pergunta(BAIXA, texto="e o horário?"))
    assert produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=perguntas)
    ) == ()


def test_assunto_nao_classificado_alta_confirma_e06() -> None:
    """A cobertura **não** é consultada: `R2` e S2-D8 ficam fora desta fronteira."""
    assert produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=(pergunta(ALTA, assunto=NAO_CLASSIFICADO),))
    ) == (Evento.E06,)


@pytest.mark.parametrize("assunto", list(AssuntoComercial))
def test_qualquer_assunto_alta_confirma_o_mesmo_e06(assunto: AssuntoComercial) -> None:
    assert produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=(pergunta(ALTA, assunto=assunto),))
    ) == (Evento.E06,)


def test_duplicatas_exatas_de_pergunta_nao_duplicam_e06() -> None:
    perguntas = (pergunta(ALTA), pergunta(ALTA))
    assert produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=perguntas)
    ) == (Evento.E06,)


# --------------------------------------------------------------------------
# Correções — não possuem evento próprio
# --------------------------------------------------------------------------


def correcao_coerente(campo: str, confianca: Confianca) -> dict[str, Any]:
    """Correção coerente com o dado extraído — a única forma canônica (N-b-C4)."""
    return {
        "dados_extraidos": dados(campo, confianca),
        "correcoes": (
            CorrecaoInterpretada(
                campo=campo,
                valor_novo=VALOR_POR_CAMPO[campo],
                confianca=confianca,
            ),
        ),
    }


@pytest.mark.parametrize("campo", sorted(EVENTO_POR_CAMPO))
def test_correcao_coerente_nao_duplica_o_evento_do_campo(campo: str) -> None:
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(**correcao_coerente(campo, ALTA))
    )
    assert resultado == (EVENTO_POR_CAMPO[campo],)
    assert len(resultado) == len(set(resultado))


@pytest.mark.parametrize("campo", sorted(EVENTO_POR_CAMPO))
def test_correcao_baixa_nao_cria_evento(campo: str) -> None:
    assert produzir_eventos_da_interpretacao(
        interpretacao(**correcao_coerente(campo, BAIXA))
    ) == ()


@pytest.mark.parametrize("campo", sorted(EVENTO_POR_CAMPO))
def test_correcao_nao_possui_evento_proprio(campo: str) -> None:
    """A saída é **idêntica** com e sem a correção declarada."""
    com_correcao = produzir_eventos_da_interpretacao(
        interpretacao(**correcao_coerente(campo, ALTA))
    )
    sem_correcao = produzir_eventos_da_interpretacao(
        interpretacao(dados_extraidos=dados(campo, ALTA))
    )
    assert com_correcao == sem_correcao


# --------------------------------------------------------------------------
# Sinais que NÃO geram evento nesta fronteira
# --------------------------------------------------------------------------


SINAIS_SEM_EVENTO: dict[str, dict[str, Any]] = {
    "nome": {
        "dados_extraidos": DadosExtraidos(nome="Fulano Fictício", confianca_nome=ALTA)
    },
    "contato": {
        "dados_extraidos": DadosExtraidos(
            contato="contato-ficticio", confianca_contato=ALTA
        )
    },
    "nome_e_contato": {
        "dados_extraidos": DadosExtraidos(
            nome="Fulano Fictício",
            confianca_nome=ALTA,
            contato="contato-ficticio",
            confianca_contato=ALTA,
        )
    },
    "pedido_de_humano_alta": {
        "pedido_de_humano": True,
        "confianca_pedido_de_humano": ALTA,
    },
    "pedido_de_humano_baixa": {
        "pedido_de_humano": True,
        "confianca_pedido_de_humano": BAIXA,
    },
    "excecao_solicitada": {
        "intencoes_autonomas": autonoma(IntencaoConversacional.EXCECAO_SOLICITADA, ALTA)
    },
    "interesse_confirmar_disponibilidade": {
        "intencoes_autonomas": autonoma(
            IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA
        )
    },
    # Os quatro sinais de encerramento de **AJ3** são **neutros em RES2**: quem
    # os consome é **S3-D1**, fronteira posterior e separada (`RES2-10`).
    "desinteresse_declarado": {
        "intencoes_autonomas": autonoma(
            IntencaoConversacional.DESINTERESSE_DECLARADO, ALTA
        )
    },
    "contato_por_engano": {
        "intencoes_autonomas": autonoma(
            IntencaoConversacional.CONTATO_POR_ENGANO, ALTA
        )
    },
    "mensagem_nao_solicitada": {
        "intencoes_autonomas": autonoma(
            IntencaoConversacional.MENSAGEM_NAO_SOLICITADA, ALTA
        )
    },
    "aceitacao_de_incompatibilidade": {
        "intencoes_autonomas": autonoma(
            IntencaoConversacional.ACEITACAO_DE_INCOMPATIBILIDADE, ALTA
        )
    },
    "continuidade_declarada": {
        "intencoes_autonomas": autonoma(
            IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA, ALTA
        )
    },
    "evento_novo_declarado": {
        "intencoes_autonomas": autonoma(
            IntencaoConversacional.EVENTO_NOVO_DECLARADO, ALTA
        )
    },
    "referencia_evento_anterior": {
        "referencias_evento_anterior": (
            ReferenciaAoEventoAnterior(texto="aquele orçamento", confianca=ALTA),
        )
    },
    "trecho_ambiguo": {
        "trechos_ambiguos": (TrechoAmbiguoRecebido(texto="não entendi bem"),)
    },
    "confianca_global_baixa": {"confianca_global": BAIXA},
}


@pytest.mark.parametrize("nome", sorted(SINAIS_SEM_EVENTO))
def test_sinal_fora_da_fronteira_nao_gera_evento(nome: str) -> None:
    assert produzir_eventos_da_interpretacao(
        interpretacao(**SINAIS_SEM_EVENTO[nome])
    ) == ()


@pytest.mark.parametrize("nome", sorted(SINAIS_SEM_EVENTO))
def test_sinal_fora_da_fronteira_nao_altera_saida_existente(nome: str) -> None:
    """Somado a um sinal confirmado, o sinal de fora **não acrescenta nada**."""
    base = {"dados_extraidos": dados("tipo_evento", ALTA)}
    ajustes = dict(SINAIS_SEM_EVENTO[nome])
    if "dados_extraidos" in ajustes:
        # Combina os dois payloads de dados num único `DadosExtraidos`.
        outro = ajustes.pop("dados_extraidos")
        ajustes["dados_extraidos"] = DadosExtraidos(
            tipo_evento=VALOR_POR_CAMPO["tipo_evento"],
            confianca_tipo_evento=ALTA,
            nome=outro.nome,
            confianca_nome=outro.confianca_nome,
            contato=outro.contato,
            confianca_contato=outro.confianca_contato,
        )
        base = {}
    assert produzir_eventos_da_interpretacao(interpretacao(**base, **ajustes)) == (
        Evento.E02,
    )


def test_confianca_global_nao_influencia_a_saida() -> None:
    saidas = {
        produzir_eventos_da_interpretacao(
            interpretacao(
                dados_extraidos=dados("convidados", ALTA), confianca_global=global_
            )
        )
        for global_ in (ALTA, BAIXA)
    }
    assert saidas == {(Evento.E04,)}


# --------------------------------------------------------------------------
# Combinação total, ordem e fecho
# --------------------------------------------------------------------------


def test_os_seis_confirmados_simultaneamente() -> None:
    resultado = produzir_eventos_da_interpretacao(interpretacao_com(frozenset(SEIS)))
    assert resultado == (
        Evento.E02,
        Evento.E03,
        Evento.E04,
        Evento.E05,
        Evento.E06,
        Evento.E10,
    )


def test_interpretacao_vazia_produz_tupla_vazia() -> None:
    resultado = produzir_eventos_da_interpretacao(interpretacao())
    assert resultado == ()
    assert isinstance(resultado, tuple)


def test_a_ordem_da_entrada_nao_altera_a_saida() -> None:
    """Permutações semanticamente equivalentes devolvem a **mesma** tupla."""
    perguntas = (
        pergunta(BAIXA, texto="a"),
        pergunta(ALTA, texto="b"),
        pergunta(BAIXA, texto="c"),
    )
    autonomas = (
        IntencaoAutonomaRecebida(
            codigo=IntencaoConversacional.INTERESSE_EM_VISITA, confianca=ALTA
        ),
        IntencaoAutonomaRecebida(
            codigo=IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE,
            confianca=ALTA,
        ),
    )
    referencias = (
        ReferenciaAoEventoAnterior(texto="um", confianca=BAIXA),
        ReferenciaAoEventoAnterior(texto="dois", confianca=ALTA),
    )
    saidas = set()
    for perm_p in itertools.permutations(perguntas):
        for perm_a in itertools.permutations(autonomas):
            for perm_r in itertools.permutations(referencias):
                saidas.add(
                    produzir_eventos_da_interpretacao(
                        interpretacao(
                            dados_extraidos=dados("formato", ALTA),
                            perguntas_comerciais=perm_p,
                            intencoes_autonomas=perm_a,
                            referencias_evento_anterior=perm_r,
                        )
                    )
                )
    assert saidas == {(Evento.E05, Evento.E06, Evento.E10)}


@pytest.mark.parametrize(
    "subconjunto", SUBCONJUNTOS, ids=lambda s: "+".join(sorted(e.value for e in s))
)
def test_cada_subconjunto_e_produzivel_exatamente(
    subconjunto: frozenset[Evento],
) -> None:
    resultado = produzir_eventos_da_interpretacao(interpretacao_com(subconjunto))
    assert set(resultado) == set(subconjunto)


@pytest.mark.parametrize(
    "subconjunto", SUBCONJUNTOS, ids=lambda s: "+".join(sorted(e.value for e in s))
)
def test_a_saida_respeita_a_ordem_canonica_e_nao_repete(
    subconjunto: frozenset[Evento],
) -> None:
    resultado = produzir_eventos_da_interpretacao(interpretacao_com(subconjunto))
    assert list(resultado) == [e for e in SEIS if e in subconjunto]
    assert len(resultado) == len(set(resultado))


@pytest.mark.parametrize(
    "subconjunto", SUBCONJUNTOS, ids=lambda s: "+".join(sorted(e.value for e in s))
)
def test_a_saida_e_sempre_subconjunto_dos_seis(
    subconjunto: frozenset[Evento],
) -> None:
    resultado = produzir_eventos_da_interpretacao(interpretacao_com(subconjunto))
    assert set(resultado) <= set(SEIS)
    assert isinstance(resultado, tuple)


def test_existem_63_subconjuntos_nao_vazios() -> None:
    assert len(SUBCONJUNTOS) == 63
    assert len(set(SUBCONJUNTOS)) == 63


# --------------------------------------------------------------------------
# Eventos proibidos — nunca produzidos por esta fronteira
# --------------------------------------------------------------------------


def test_o_vocabulario_proibido_tem_doze_eventos() -> None:
    assert len(PROIBIDOS) == 12
    assert set(PROIBIDOS) == {
        Evento.E01,
        Evento.E07,
        Evento.E08,
        Evento.E09,
        Evento.E11,
        Evento.E12,
        Evento.E13,
        Evento.E14,
        Evento.E15,
        Evento.E16,
        Evento.E17,
        Evento.E18,
    }


@pytest.mark.parametrize("proibido", PROIBIDOS, ids=lambda e: e.value)
def test_evento_proibido_nunca_aparece_em_subconjunto_algum(
    proibido: Evento,
) -> None:
    for subconjunto in SUBCONJUNTOS:
        assert proibido not in produzir_eventos_da_interpretacao(
            interpretacao_com(subconjunto)
        )


@pytest.mark.parametrize("nome", sorted(SINAIS_SEM_EVENTO))
def test_nenhum_sinal_de_handoff_produz_e11_e17_ou_e18(nome: str) -> None:
    """`E11`/`E17` continuam reduzidos a `E18` pelo `DetectorHandoff` (doc 06 §2.1)."""
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(**SINAIS_SEM_EVENTO[nome])
    )
    assert Evento.E11 not in resultado
    assert Evento.E17 not in resultado
    assert Evento.E18 not in resultado


#: Os quatro sinais de encerramento acrescentados ao grupo **A2** por **AJ3**.
SINAIS_DE_ENCERRAMENTO = (
    IntencaoConversacional.DESINTERESSE_DECLARADO,
    IntencaoConversacional.CONTATO_POR_ENGANO,
    IntencaoConversacional.MENSAGEM_NAO_SOLICITADA,
    IntencaoConversacional.ACEITACAO_DE_INCOMPATIBILIDADE,
)


@pytest.mark.parametrize("codigo", SINAIS_DE_ENCERRAMENTO, ids=lambda c: c.value)
@pytest.mark.parametrize("confianca", [ALTA, BAIXA])
def test_sinal_de_encerramento_e_neutro_em_res2(
    codigo: IntencaoConversacional, confianca: Confianca
) -> None:
    """`RES2-10`: `E14` pertence a **S3-D1**, e RES2 não muda por causa dela."""
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(intencoes_autonomas=autonoma(codigo, confianca))
    )
    assert resultado == ()
    assert Evento.E14 not in resultado


def test_os_quatro_sinais_juntos_nao_produzem_evento_algum() -> None:
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(
            intencoes_autonomas=tuple(
                IntencaoAutonomaRecebida(codigo=codigo, confianca=ALTA)
                for codigo in SINAIS_DE_ENCERRAMENTO
            )
        )
    )
    assert resultado == ()


def test_sinal_de_encerramento_nao_altera_os_seis_eventos_produzidos() -> None:
    """Os sinais novos são **aditivos e inertes**: a saída não muda."""
    base = interpretacao(
        dados_extraidos=DadosExtraidos(
            tipo_evento="festa fictícia", confianca_tipo_evento=ALTA
        ),
        perguntas_comerciais=(pergunta(),),
    )
    com_sinais = interpretacao(
        dados_extraidos=DadosExtraidos(
            tipo_evento="festa fictícia", confianca_tipo_evento=ALTA
        ),
        perguntas_comerciais=(pergunta(),),
        intencoes_autonomas=tuple(
            IntencaoAutonomaRecebida(codigo=codigo, confianca=ALTA)
            for codigo in SINAIS_DE_ENCERRAMENTO
        ),
    )
    assert produzir_eventos_da_interpretacao(com_sinais) == (
        produzir_eventos_da_interpretacao(base)
    )
    assert Evento.E14 not in produzir_eventos_da_interpretacao(com_sinais)


def test_res2_continua_fechado_nos_seis_eventos_apos_aj3() -> None:
    """`E14` continua **fora** de RES2, e nenhum evento novo aparece."""
    fonte = MODULO_RES2.read_text(encoding="utf-8")
    assert "E14" not in fonte.split('"""', 2)[2]
    assert Evento.E14 in PROIBIDOS
    assert len(SEIS) == 6


def test_pedido_de_humano_e_excecao_juntos_nao_produzem_evento_algum() -> None:
    resultado = produzir_eventos_da_interpretacao(
        interpretacao(
            pedido_de_humano=True,
            confianca_pedido_de_humano=ALTA,
            intencoes_autonomas=autonoma(
                IntencaoConversacional.EXCECAO_SOLICITADA, ALTA
            ),
        )
    )
    assert resultado == ()


def test_pergunta_alta_nunca_produz_e09() -> None:
    """As **causas** de `E09` pertencem a S2-D8; RES2 não as conhece."""
    for perguntas in (
        (pergunta(ALTA),),
        (pergunta(ALTA, assunto=NAO_CLASSIFICADO),),
        (pergunta(ALTA), pergunta(BAIXA)),
    ):
        resultado = produzir_eventos_da_interpretacao(
            interpretacao(perguntas_comerciais=perguntas)
        )
        assert Evento.E09 not in resultado
        assert resultado == (Evento.E06,)


def test_nenhum_subconjunto_produz_e07_ou_e08() -> None:
    for subconjunto in SUBCONJUNTOS:
        resultado = produzir_eventos_da_interpretacao(interpretacao_com(subconjunto))
        assert Evento.E07 not in resultado
        assert Evento.E08 not in resultado


# --------------------------------------------------------------------------
# Canonicidade — validação reutilizada, nunca duplicada
# --------------------------------------------------------------------------


def test_none_e_type_error() -> None:
    with pytest.raises(TypeError):
        produzir_eventos_da_interpretacao(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "valor", [object(), "E02", 42, (), [], {"E02": True}, DadosExtraidos()]
)
def test_tipo_incompativel_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        produzir_eventos_da_interpretacao(valor)  # type: ignore[arg-type]


def test_interpretacao_construida_diretamente_mas_invalida_e_bloqueada() -> None:
    """Invariante N-b violado: `E-Nb-11` — payload sem o código derivado."""
    invalida = Interpretacao(
        intencoes_detectadas=(),
        dados_extraidos=DadosExtraidos(tipo_evento="festa", confianca_tipo_evento=ALTA),
        correcoes=(),
        perguntas_comerciais=(),
        pedido_de_humano=False,
        confianca_pedido_de_humano=None,
        referencias_evento_anterior=(),
        confianca_global=ALTA,
        trechos_ambiguos=(),
    )
    with pytest.raises(ValueError) as excecao:
        produzir_eventos_da_interpretacao(invalida)
    assert str(excecao.value).startswith("E-Nb-")


@pytest.mark.parametrize(
    ("invalida", "codigo"),
    [
        (
            Interpretacao(
                intencoes_detectadas=(),
                dados_extraidos=DadosExtraidos(),
                correcoes=(),
                perguntas_comerciais=(),
                pedido_de_humano=False,
                confianca_pedido_de_humano=None,
                referencias_evento_anterior=(),
                confianca_global=None,  # type: ignore[arg-type]
                trechos_ambiguos=(),
            ),
            "E-Nb-4",
        ),
        (
            Interpretacao(
                intencoes_detectadas=(),
                dados_extraidos=DadosExtraidos(confianca_nome=ALTA),
                correcoes=(),
                perguntas_comerciais=(),
                pedido_de_humano=False,
                confianca_pedido_de_humano=None,
                referencias_evento_anterior=(),
                confianca_global=ALTA,
                trechos_ambiguos=(),
            ),
            "E-Nb-3",
        ),
        (
            Interpretacao(
                intencoes_detectadas=(),
                dados_extraidos=DadosExtraidos(),
                correcoes=(),
                perguntas_comerciais=(pergunta(ALTA),),
                pedido_de_humano=False,
                confianca_pedido_de_humano=None,
                referencias_evento_anterior=(),
                confianca_global=ALTA,
                trechos_ambiguos=(),
            ),
            "E-Nb-14",
        ),
        (
            Interpretacao(
                intencoes_detectadas=(
                    IntencaoDetectada(
                        codigo=IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA,
                        confianca=ALTA,
                    ),
                    IntencaoDetectada(
                        codigo=IntencaoConversacional.EVENTO_NOVO_DECLARADO,
                        confianca=ALTA,
                    ),
                ),
                dados_extraidos=DadosExtraidos(),
                correcoes=(),
                perguntas_comerciais=(),
                pedido_de_humano=False,
                confianca_pedido_de_humano=None,
                referencias_evento_anterior=(),
                confianca_global=ALTA,
                trechos_ambiguos=(),
            ),
            "E-Nb-18",
        ),
        (
            Interpretacao(
                intencoes_detectadas=(),
                dados_extraidos=DadosExtraidos(),
                correcoes=(),
                perguntas_comerciais=(),
                pedido_de_humano=False,
                confianca_pedido_de_humano=None,
                referencias_evento_anterior=(),
                confianca_global=ALTA,
                trechos_ambiguos=(TrechoAmbiguo(texto="   "),),
            ),
            "E-Nb-10",
        ),
    ],
    ids=["E-Nb-4", "E-Nb-3", "E-Nb-14", "E-Nb-18", "E-Nb-10"],
)
def test_invariantes_n_b_bloqueiam_antes_de_qualquer_producao(
    invalida: Interpretacao, codigo: str
) -> None:
    with pytest.raises(ValueError) as excecao:
        produzir_eventos_da_interpretacao(invalida)
    assert str(excecao.value).startswith(codigo)


def test_entrada_invalida_nao_produz_saida_parcial() -> None:
    """Sinais válidos coexistindo com invariante violado: **nada** é devolvido."""
    invalida = Interpretacao(
        intencoes_detectadas=(
            IntencaoDetectada(
                codigo=IntencaoConversacional.INTERESSE_EM_VISITA, confianca=ALTA
            ),
        ),
        dados_extraidos=DadosExtraidos(
            tipo_evento="festa",
            confianca_tipo_evento=ALTA,
            convidados=60,
            confianca_convidados=ALTA,
        ),
        correcoes=(),
        perguntas_comerciais=(pergunta(ALTA),),
        pedido_de_humano=False,
        confianca_pedido_de_humano=None,
        referencias_evento_anterior=(),
        confianca_global=None,  # type: ignore[arg-type]
        trechos_ambiguos=(),
    )
    with pytest.raises(ValueError):
        produzir_eventos_da_interpretacao(invalida)


def test_a_validacao_canonica_e_reutilizada_e_nao_duplicada() -> None:
    """A fronteira **importa** o validador existente — não o reescreve."""
    arvore = ast.parse(MODULO_RES2.read_text(encoding="utf-8"))
    importados = {
        alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom)
        and no.module == "casa77_sdr.interpretation"
        for alias in no.names
    }
    assert "_validar_interpretacao_canonica" in importados

    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }
    assert "_validar_interpretacao_canonica" in chamadas

    # Nenhum validador paralelo: a fronteira não redefine validação alguma.
    definidas = {
        no.name for no in ast.walk(arvore) if isinstance(no, ast.FunctionDef)
    }
    assert definidas == {"produzir_eventos_da_interpretacao"}


# --------------------------------------------------------------------------
# Compatibilidade estrutural com a `MaquinaEstados`
# --------------------------------------------------------------------------


#: Condições **neutras e coerentes**. `resposta_aprovada_disponivel = True`
#: descreve um ciclo em que a resposta aprovada existe — nada é fabricado para
#: forçar PASS, e a hipótese oposta é provada **separadamente** em D8-N1.
#: `interesse_confirmar_disponibilidade` fica `None`: RES2 não a produz, e o
#: eixo de disponibilidade é decidido por outra fronteira.
CONDICOES_NEUTRAS = CondicoesCiclo(resposta_aprovada_disponivel=True)


@pytest.mark.parametrize("estado", list(Estado), ids=lambda e: e.value)
@pytest.mark.parametrize(
    "subconjunto", SUBCONJUNTOS, ids=lambda s: "+".join(sorted(e.value for e in s))
)
def test_todo_conjunto_produzivel_e_resolvido_pela_maquina(
    subconjunto: frozenset[Evento], estado: Estado
) -> None:
    """63 subconjuntos × 8 estados = **504** combinações, zero `TransicaoInexistente`.

    O objetivo é estrutural: nenhum conjunto que **esta fronteira seja capaz de
    produzir** pode falhar por combinação de evento e estado. A saída de RES2 é
    usada literalmente como entrada da máquina — nada é fabricado.
    """
    eventos = produzir_eventos_da_interpretacao(interpretacao_com(subconjunto))
    assert set(eventos) == set(subconjunto)
    try:
        decisao = decidir(estado, eventos, INCOMPLETOS, CONDICOES_NEUTRAS)
    except TransicaoInexistente as erro:  # pragma: no cover - falha do contrato
        pytest.fail(
            f"{sorted(e.value for e in subconjunto)} em {estado.value}: {erro}"
        )
    assert isinstance(decisao.estado_final, Estado)


def test_a_matriz_de_compatibilidade_tem_504_combinacoes() -> None:
    assert len(SUBCONJUNTOS) * len(list(Estado)) == 504


# --------------------------------------------------------------------------
# D8-N1 — prova separada, e explicitamente fora de RES2
# --------------------------------------------------------------------------


def test_d8_n1_e06_sem_resposta_aprovada_exige_e09_no_estado_condicionado() -> None:
    """`E06` de RES2 **não basta** quando não há resposta aprovada.

    O `E09` exigido aqui **não é produzido por RES2**: as causas pertencem a
    **S2-D8** e a confirmação do evento pertence à integração futura. Este teste
    prova a **pré-condição de coerência** da máquina, não uma capacidade nova
    desta fronteira.
    """
    eventos = produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=(pergunta(ALTA),))
    )
    assert eventos == (Evento.E06,)
    indisponivel = CondicoesCiclo(resposta_aprovada_disponivel=False)

    for estado in (
        Estado.COLETANDO_DADOS,
        Estado.RESPONDENDO_DUVIDAS,
        Estado.ENCAMINHADO_HUMANO,
    ):
        with pytest.raises(ValueError) as excecao:
            decidir(estado, eventos, INCOMPLETOS, indisponivel)
        assert "E09" in str(excecao.value)


def test_d8_n1_com_e09_confirmado_a_combinacao_e_coerente() -> None:
    """Com o `E09` vindo de fora, a combinação resolve — **sem** RES2 produzi-lo."""
    eventos_res2 = produzir_eventos_da_interpretacao(
        interpretacao(perguntas_comerciais=(pergunta(ALTA),))
    )
    assert Evento.E09 not in eventos_res2

    # O `E09` é acrescentado **pelo teste**, representando o produtor externo.
    eventos_do_ciclo = eventos_res2 + (Evento.E09,)
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        eventos_do_ciclo,
        INCOMPLETOS,
        CondicoesCiclo(resposta_aprovada_disponivel=False, pendencia_impeditiva=True),
    )
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF


def test_res2_nao_e_capaz_de_produzir_o_e09_que_d8_n1_exige() -> None:
    for subconjunto in SUBCONJUNTOS:
        assert Evento.E09 not in produzir_eventos_da_interpretacao(
            interpretacao_com(subconjunto)
        )


# --------------------------------------------------------------------------
# Pureza e fronteira do módulo
# --------------------------------------------------------------------------


def modulos_importados(caminho: Path) -> set[str]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    raizes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            raizes.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            raizes.add(no.module.split(".")[0])
    return raizes


def test_a_fronteira_e_pura_e_nao_importa_nada_proibido() -> None:
    importados = modulos_importados(MODULO_RES2)
    assert importados <= {"__future__", "casa77_sdr"}

    arvore = ast.parse(MODULO_RES2.read_text(encoding="utf-8"))
    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert submodulos == {
        "__future__",
        "casa77_sdr.identity",
        "casa77_sdr.interpretation",
        "casa77_sdr.state_machine",
    }
    for proibido in (
        "casa77_sdr.qualification",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.rules",
        "casa77_sdr.persistence",
        "casa77_sdr.knowledge",
        "casa77_sdr.interpretation_anthropic",
        "casa77_sdr.interpretation_llm",
    ):
        assert proibido not in submodulos

    chamadas = {
        no.func.attr if isinstance(no.func, ast.Attribute) else getattr(no.func, "id", "")
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call)
    }
    assert chamadas & {
        "open",
        "getenv",
        "sleep",
        "now",
        "safe_load",
        "read_text",
        "print",
    } == set()


def test_a_superficie_publica_e_fechada_em_um_produtor() -> None:
    assert interpretation_events.__all__ == ["produzir_eventos_da_interpretacao"]
    publicos = [
        nome for nome in vars(interpretation_events) if not nome.startswith("_")
    ]
    assert "produzir_eventos_da_interpretacao" in publicos


def test_a_fronteira_nao_e_exportada_pelo_pacote() -> None:
    """M-NB1 preservado: nada desta fronteira sai pelo `__init__.py`."""
    import casa77_sdr

    assert "produzir_eventos_da_interpretacao" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "produzir_eventos_da_interpretacao")


def test_nenhuma_excecao_publica_nova_e_criada() -> None:
    arvore = ast.parse(MODULO_RES2.read_text(encoding="utf-8"))
    classes = [no for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)]
    assert classes == []


def test_a_saida_e_sempre_tupla_de_evento() -> None:
    for subconjunto in SUBCONJUNTOS:
        resultado = produzir_eventos_da_interpretacao(interpretacao_com(subconjunto))
        assert isinstance(resultado, tuple)
        assert not isinstance(resultado, list)
        assert all(isinstance(item, Evento) for item in resultado)


def test_a_entrada_nao_e_mutada() -> None:
    alvo = interpretacao_com(frozenset(SEIS))
    antes = (
        alvo.dados_extraidos,
        alvo.perguntas_comerciais,
        alvo.intencoes_detectadas,
        alvo.confianca_global,
    )
    produzir_eventos_da_interpretacao(alvo)
    assert (
        alvo.dados_extraidos,
        alvo.perguntas_comerciais,
        alvo.intencoes_detectadas,
        alvo.confianca_global,
    ) == antes


def test_a_funcao_e_deterministica() -> None:
    alvo = interpretacao_com(frozenset(SEIS))
    assert len({produzir_eventos_da_interpretacao(alvo) for _ in range(5)}) == 1
