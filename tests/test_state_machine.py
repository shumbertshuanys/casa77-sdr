"""Testes da MaquinaEstados (3B.6) — Fatia 1: contrato e núcleo.

Cobre as cardinalidades dos vocabulários fechados, a assinatura pública, as
validações de contrato, um caminho representativo por família C0–C11, as
precedências semânticas aprovadas, o consumo único e os invariantes estruturais
do módulo. A matriz comportamental exaustiva de T01–T41 pertence à Fatia 2.

Todas as fixtures são artificiais: nenhum dado pessoal, nenhum valor comercial e
nenhuma base carregada — a máquina não lê YAML.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from casa77_sdr.qualification import (
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.rules import MotivoViolacao, Violacao
from casa77_sdr.state_machine import (
    AcaoMaquina,
    CondicoesCiclo,
    DecisaoMaquina,
    EfeitoParalelo,
    Estado,
    Evento,
    Identidade,
    Inercia,
    MotivoEncerramento,
    Transicao,
    TransicaoInexistente,
    decidir,
)

MODULO_MAQUINA = Path(__file__).resolve().parents[1] / "src" / "casa77_sdr" / "state_machine.py"


# --------------------------------------------------------------------------
# Fixtures artificiais
# --------------------------------------------------------------------------


def qual(
    resultado: ResultadoQualificacao,
    *,
    campos_ausentes: tuple[str, ...] = (),
    violacoes: tuple[Violacao, ...] = (),
    pendencias: tuple[str, ...] = (),
) -> Qualificacao:
    """Constrói uma `Qualificacao` já calculada, sem recalcular nada."""
    motivos = {
        ResultadoQualificacao.DADOS_INCOMPLETOS: MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES,
        ResultadoQualificacao.INCOMPATIVEL: MotivoQualificacao.VIOLACAO_OBJETIVA,
        ResultadoQualificacao.INDEFINIDO: MotivoQualificacao.PENDENCIA_IMPEDITIVA,
        ResultadoQualificacao.QUALIFICADO: MotivoQualificacao.COMPATIVEL,
        ResultadoQualificacao.QUALIFICADO_COM_RESSALVA: (
            MotivoQualificacao.FORMATO_SENTADO_ACIMA_CAPACIDADE_SENTADA
        ),
    }
    return Qualificacao(
        resultado=resultado,
        motivo=motivos[resultado],
        campos_ausentes=campos_ausentes,
        violacoes=violacoes,
        pendencias_impeditivas=pendencias,
    )


INCOMPLETOS = qual(ResultadoQualificacao.DADOS_INCOMPLETOS, campos_ausentes=("nome",))
QUALIFICADO = qual(ResultadoQualificacao.QUALIFICADO)
RESSALVA = qual(ResultadoQualificacao.QUALIFICADO_COM_RESSALVA)

VIOLACAO_DATA = Violacao(
    motivo=MotivoViolacao.DATA_NAO_ACEITA,
    campo_yaml="eventos.datas_nao_aceitas",
    valor_informado="data-x",
)
VIOLACAO_TIPO = Violacao(
    motivo=MotivoViolacao.TIPO_NAO_ACEITO,
    campo_yaml="eventos.nao_aceitos",
    valor_informado="tipo-x",
)
VIOLACAO_CONVIDADOS = Violacao(
    motivo=MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
    campo_yaml="capacidade.formato_coquetel",
    valor_informado=1,
)

SEM_CONDICOES = CondicoesCiclo()


def incompativel(*violacoes: Violacao) -> Qualificacao:
    return qual(ResultadoQualificacao.INCOMPATIVEL, violacoes=violacoes)


# --------------------------------------------------------------------------
# A. Cardinalidades dos vocabulários fechados
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "enumeracao, esperado",
    [
        (Estado, 8),
        (Evento, 18),
        (MotivoEncerramento, 4),
        (AcaoMaquina, 20),
        (EfeitoParalelo, 6),
        (Inercia, 4),
        (Transicao, 41),
        (Identidade, 4),
    ],
)
def test_cardinalidade_dos_vocabularios_fechados(enumeracao, esperado) -> None:
    assert len(list(enumeracao)) == esperado


def test_eventos_sao_exatamente_e01_a_e18() -> None:
    assert [evento.value for evento in Evento] == [f"E{i:02d}" for i in range(1, 19)]


def test_transicoes_sao_exatamente_t01_a_t41() -> None:
    assert [t.value for t in Transicao] == [f"T{i:02d}" for i in range(1, 42)]


def test_nao_existe_p7_nem_n5() -> None:
    assert not hasattr(EfeitoParalelo, "P7")
    assert not hasattr(Inercia, "N5")


# --------------------------------------------------------------------------
# B. Assinatura pública
# --------------------------------------------------------------------------


def test_decidir_tem_exatamente_quatro_argumentos() -> None:
    parametros = list(inspect.signature(decidir).parameters)
    assert parametros == ["estado", "eventos", "qualificacao", "condicoes"]


def test_fase_ciclo_nao_existe() -> None:
    import casa77_sdr.state_machine as modulo

    assert not hasattr(modulo, "FaseCiclo")


def test_condicoes_ciclo_tem_exatamente_oito_campos() -> None:
    assert list(CondicoesCiclo.__dataclass_fields__) == [
        "insumo_qualificacao_atualizado",
        "pendencia_impeditiva",
        "motivos_handoff",
        "resposta_aprovada_disponivel",
        "interesse_confirmar_disponibilidade",
        "calendario_integrado",
        "identidade",
        "motivo_encerramento",
    ]


def test_decisao_maquina_tem_exatamente_oito_campos() -> None:
    assert list(DecisaoMaquina.__dataclass_fields__) == [
        "estado_final",
        "caminho",
        "acoes",
        "efeitos",
        "inercias",
        "eventos_consumidos",
        "motivos_handoff",
        "motivo_encerramento",
    ]


# --------------------------------------------------------------------------
# C. Validações de tipo
# --------------------------------------------------------------------------


def test_estado_invalido_e_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        decidir("novo", (Evento.E01,), INCOMPLETOS, SEM_CONDICOES)


def test_eventos_precisam_ser_tupla() -> None:
    with pytest.raises(TypeError):
        decidir(Estado.NOVO, [Evento.E01], INCOMPLETOS, SEM_CONDICOES)


def test_item_de_evento_invalido_e_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        decidir(Estado.NOVO, ("E01",), INCOMPLETOS, SEM_CONDICOES)


def test_qualificacao_invalida_e_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        decidir(Estado.NOVO, (Evento.E01,), "qualificado", SEM_CONDICOES)


def test_condicoes_invalidas_sao_erro_de_tipo() -> None:
    with pytest.raises(TypeError):
        decidir(Estado.NOVO, (Evento.E01,), INCOMPLETOS, {})


@pytest.mark.parametrize(
    "campo",
    [
        "insumo_qualificacao_atualizado",
        "pendencia_impeditiva",
        "resposta_aprovada_disponivel",
        "interesse_confirmar_disponibilidade",
        "calendario_integrado",
    ],
)
def test_condicao_booleana_nao_aceita_inteiro(campo: str) -> None:
    with pytest.raises(TypeError):
        decidir(
            Estado.NOVO,
            (Evento.E01,),
            INCOMPLETOS,
            CondicoesCiclo(**{campo: 1}),
        )


def test_motivos_handoff_precisam_ser_tupla_de_texto() -> None:
    with pytest.raises(TypeError):
        decidir(
            Estado.NOVO,
            (Evento.E01,),
            INCOMPLETOS,
            CondicoesCiclo(motivos_handoff=["pedido_humano"]),
        )
    with pytest.raises(TypeError):
        decidir(
            Estado.NOVO,
            (Evento.E01,),
            INCOMPLETOS,
            CondicoesCiclo(motivos_handoff=(1,)),
        )


def test_identidade_e_motivo_precisam_ser_enums() -> None:
    with pytest.raises(TypeError):
        decidir(
            Estado.ENCERRADO,
            (Evento.E01,),
            INCOMPLETOS,
            CondicoesCiclo(identidade="mesma_solicitacao"),
        )
    with pytest.raises(TypeError):
        decidir(
            Estado.COLETANDO_DADOS,
            (Evento.E14,),
            INCOMPLETOS,
            CondicoesCiclo(motivo_encerramento="engano"),
        )


# --------------------------------------------------------------------------
# D/E/F/G/H/I. Validações de coerência
# --------------------------------------------------------------------------


def test_evento_repetido_e_incoerencia_estrutural() -> None:
    with pytest.raises(ValueError):
        decidir(
            Estado.COLETANDO_DADOS,
            (Evento.E04, Evento.E04),
            INCOMPLETOS,
            SEM_CONDICOES,
        )


@pytest.mark.parametrize("evento", [Evento.E11, Evento.E17])
def test_e11_e_e17_nunca_alcancam_a_maquina(evento: Evento) -> None:
    with pytest.raises(ValueError):
        decidir(Estado.COLETANDO_DADOS, (evento,), INCOMPLETOS, SEM_CONDICOES)


def test_e18_sem_motivo_e_incoerencia() -> None:
    with pytest.raises(ValueError):
        decidir(Estado.NOVO, (Evento.E18,), INCOMPLETOS, SEM_CONDICOES)


def test_motivo_de_handoff_em_branco_e_incoerencia() -> None:
    with pytest.raises(ValueError):
        decidir(
            Estado.NOVO,
            (Evento.E18,),
            INCOMPLETOS,
            CondicoesCiclo(motivos_handoff=("  ",)),
        )


def test_e07_com_mutacao_e_resultado_positivo_e_valido() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E07,),
        QUALIFICADO,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF


@pytest.mark.parametrize("insumo", [False, None])
def test_e07_sem_mutacao_efetiva_e_incoerencia(insumo) -> None:
    with pytest.raises(ValueError):
        decidir(
            Estado.COLETANDO_DADOS,
            (Evento.E07,),
            QUALIFICADO,
            CondicoesCiclo(insumo_qualificacao_atualizado=insumo),
        )


@pytest.mark.parametrize(
    "resultado",
    [
        ResultadoQualificacao.DADOS_INCOMPLETOS,
        ResultadoQualificacao.INDEFINIDO,
    ],
)
def test_e07_com_resultado_nao_positivo_e_incoerencia(resultado) -> None:
    with pytest.raises(ValueError):
        decidir(
            Estado.COLETANDO_DADOS,
            (Evento.E07,),
            qual(resultado),
            CondicoesCiclo(insumo_qualificacao_atualizado=True),
        )


def test_insumo_falso_sem_e07_e_valido() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E10,),
        INCOMPLETOS,
        CondicoesCiclo(insumo_qualificacao_atualizado=False),
    )
    assert Transicao.T16 in decisao.caminho


def test_e09_sem_classificacao_e_incoerencia() -> None:
    with pytest.raises(ValueError):
        decidir(Estado.COLETANDO_DADOS, (Evento.E09,), INCOMPLETOS, SEM_CONDICOES)


@pytest.mark.parametrize(
    "estado",
    [Estado.COLETANDO_DADOS, Estado.RESPONDENDO_DUVIDAS, Estado.ENCAMINHADO_HUMANO],
)
@pytest.mark.parametrize("disponivel", [False, None])
def test_e06_sem_resposta_aprovada_e_sem_e09_e_incoerencia(estado, disponivel) -> None:
    with pytest.raises(ValueError):
        decidir(
            estado,
            (Evento.E06,),
            INCOMPLETOS,
            CondicoesCiclo(resposta_aprovada_disponivel=disponivel),
        )


def test_e06_sem_resposta_aprovada_com_e09_e_valido() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E06, Evento.E09),
        INCOMPLETOS,
        CondicoesCiclo(resposta_aprovada_disponivel=False, pendencia_impeditiva=False),
    )
    assert Transicao.T12 in decisao.caminho
    assert EfeitoParalelo.P3 in decisao.efeitos


def test_t02_em_novo_nao_ganhou_condicao_nova() -> None:
    decisao = decidir(Estado.NOVO, (Evento.E06,), INCOMPLETOS, SEM_CONDICOES)
    assert decisao.caminho == (Transicao.T02,)
    assert decisao.estado_final is Estado.RESPONDENDO_DUVIDAS


def test_e08_sem_violacao_e_incoerencia() -> None:
    with pytest.raises(ValueError):
        decidir(Estado.COLETANDO_DADOS, (Evento.E08,), INCOMPLETOS, SEM_CONDICOES)


def test_e08_com_motivo_sem_classe_documentada_e_incoerencia() -> None:
    desconhecida = Violacao(
        motivo="motivo_inexistente",
        campo_yaml="campo.qualquer",
        valor_informado="x",
    )
    with pytest.raises(ValueError):
        decidir(
            Estado.COLETANDO_DADOS,
            (Evento.E08,),
            incompativel(desconhecida),
            SEM_CONDICOES,
        )


def test_t35_sem_motivo_estruturado_e_incoerencia() -> None:
    with pytest.raises(ValueError):
        decidir(Estado.COLETANDO_DADOS, (Evento.E14,), INCOMPLETOS, SEM_CONDICOES)


@pytest.mark.parametrize(
    "estado, eventos",
    [
        (Estado.NOVO, (Evento.E01,)),
        (Estado.COLETANDO_DADOS, (Evento.E10,)),
        (Estado.ENCERRADO, (Evento.E01,)),
        (Estado.ENCAMINHADO_HUMANO, (Evento.E13,)),
        (Estado.ATENDIMENTO_HUMANO, (Evento.E01,)),
    ],
)
def test_identidade_ambigua_e_sempre_incoerencia(estado, eventos) -> None:
    with pytest.raises(ValueError):
        decidir(
            estado,
            eventos,
            INCOMPLETOS,
            CondicoesCiclo(identidade=Identidade.AMBIGUA),
        )


# --------------------------------------------------------------------------
# Correções da auditoria intermediária (C1–C5)
# --------------------------------------------------------------------------


def test_c1_motivos_handoff_so_ecoam_quando_e18_e_consumido() -> None:
    """T33 sem `E18` no ciclo não fabrica motivo a partir das condições."""
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO,
        (Evento.E01,),
        INCOMPLETOS,
        CondicoesCiclo(motivos_handoff=("motivo-tecnico",)),
    )
    assert decisao.caminho == (Transicao.T33,)
    assert decisao.acoes == (AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA,)
    assert decisao.motivos_handoff == ()
    assert Evento.E18 not in decisao.eventos_consumidos


def test_c1_t33_com_e18_absorve_e_preserva_o_motivo() -> None:
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO,
        (Evento.E01, Evento.E18),
        INCOMPLETOS,
        CondicoesCiclo(motivos_handoff=("motivo-tecnico",)),
    )
    assert decisao.caminho == (Transicao.T33,)
    assert decisao.acoes == (AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA,)
    assert decisao.motivos_handoff == ("motivo-tecnico",)
    assert Evento.E18 in decisao.eventos_consumidos


def test_c2_transicao_posterior_a_c8_nao_torna_e07_inerte() -> None:
    """T28 pertence a C9: não pode produzir N2 retroativamente para `E07`."""
    with pytest.raises(TransicaoInexistente):
        decidir(
            Estado.ENCAMINHADO_HUMANO,
            (Evento.E07, Evento.E06),
            QUALIFICADO,
            CondicoesCiclo(
                insumo_qualificacao_atualizado=True,
                resposta_aprovada_disponivel=True,
            ),
        )


def test_c2_n2_permanece_quando_c7_determina_o_estado() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03, Evento.E07),
        QUALIFICADO,
        CondicoesCiclo(
            insumo_qualificacao_atualizado=True,
            interesse_confirmar_disponibilidade=True,
            calendario_integrado=False,
        ),
    )
    assert decisao.caminho == (Transicao.T15,)
    assert decisao.inercias == (Inercia.N2,)


@pytest.mark.parametrize(
    "resultado",
    [
        ResultadoQualificacao.QUALIFICADO,
        ResultadoQualificacao.DADOS_INCOMPLETOS,
        ResultadoQualificacao.QUALIFICADO_COM_RESSALVA,
        ResultadoQualificacao.INDEFINIDO,
    ],
)
def test_c3_e08_exige_resultado_incompativel(resultado) -> None:
    with pytest.raises(ValueError):
        decidir(
            Estado.COLETANDO_DADOS,
            (Evento.E08,),
            qual(resultado, violacoes=(VIOLACAO_TIPO,)),
            SEM_CONDICOES,
        )


def test_c4_e07_com_pendencia_impeditiva_e_incoerencia() -> None:
    with pytest.raises(ValueError):
        decidir(
            Estado.COLETANDO_DADOS,
            (Evento.E07, Evento.E09),
            QUALIFICADO,
            CondicoesCiclo(
                insumo_qualificacao_atualizado=True, pendencia_impeditiva=True
            ),
        )


def test_c4_e07_com_pendencia_acessoria_permanece_coerente() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E07, Evento.E09),
        QUALIFICADO,
        CondicoesCiclo(
            insumo_qualificacao_atualizado=True, pendencia_impeditiva=False
        ),
    )
    # C8 decide primeiro (T13 consome `E07`) e leva o estado a
    # `pronto_para_handoff`; C10 é posterior, então T12 já não se aplica e a
    # pendência acessória sobrevive como P5.
    assert Transicao.T13 in decisao.caminho
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF
    assert EfeitoParalelo.P5 in decisao.efeitos


@pytest.mark.parametrize(
    "eventos",
    [
        (Evento.E13, Evento.E01),
        (Evento.E15, Evento.E06),
        (Evento.E15, Evento.E12),
        (Evento.E12, Evento.E01),
    ],
)
def test_c5_eventos_de_ciclo_proprio_nao_coocorrem(eventos) -> None:
    with pytest.raises(ValueError):
        decidir(
            Estado.ENCAMINHADO_HUMANO,
            eventos,
            QUALIFICADO,
            CondicoesCiclo(resposta_aprovada_disponivel=True),
        )


def test_c5_chamadas_singleton_permanecem_validas() -> None:
    assert decidir(
        Estado.ENCAMINHADO_HUMANO, (Evento.E13,), QUALIFICADO, SEM_CONDICOES
    ).caminho == (Transicao.T31,)
    assert decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E15,), INCOMPLETOS, SEM_CONDICOES
    ).caminho == (Transicao.T20,)
    assert decidir(
        Estado.PRONTO_PARA_HANDOFF, (Evento.E12,), QUALIFICADO, SEM_CONDICOES
    ).caminho == (Transicao.T27,)


# --------------------------------------------------------------------------
# H. Classes de E08
# --------------------------------------------------------------------------


def test_e08_apenas_data_usa_a_classe_de_handoff_documentado() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E08,),
        incompativel(VIOLACAO_DATA),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T05,)
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF


@pytest.mark.parametrize(
    "violacoes",
    [(VIOLACAO_TIPO,), (VIOLACAO_CONVIDADOS,), (VIOLACAO_TIPO, VIOLACAO_CONVIDADOS)],
)
def test_e08_somente_tipo_ou_convidados_informa_e_aguarda(violacoes) -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E08,),
        incompativel(*violacoes),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T06,)
    assert decisao.estado_final is Estado.COLETANDO_DADOS


def test_e08_misto_basta_uma_violacao_de_data() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E08,),
        incompativel(VIOLACAO_TIPO, VIOLACAO_DATA, VIOLACAO_CONVIDADOS),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T05,)


def test_e08_misto_em_respondendo_duvidas_usa_t22() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E08,),
        incompativel(VIOLACAO_CONVIDADOS, VIOLACAO_DATA),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T22,)


# --------------------------------------------------------------------------
# J. Smoke por família C0–C11
# --------------------------------------------------------------------------


def test_c0_abertura_por_t01() -> None:
    decisao = decidir(Estado.NOVO, (Evento.E01,), INCOMPLETOS, SEM_CONDICOES)
    assert decisao.caminho == (Transicao.T01,)
    assert decisao.acoes == (AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL,)


def test_c1_t33_absorve_e18_sem_resposta_automatica() -> None:
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO,
        (Evento.E01, Evento.E18),
        INCOMPLETOS,
        CondicoesCiclo(motivos_handoff=("pedido_humano",)),
    )
    assert decisao.caminho == (Transicao.T33,)
    assert decisao.acoes == (AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA,)
    assert decisao.motivos_handoff == ("pedido_humano",)


def test_c2_handoff_obrigatorio_por_t07() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E18,),
        INCOMPLETOS,
        CondicoesCiclo(motivos_handoff=("pedido_desconto",)),
    )
    assert decisao.caminho == (Transicao.T07,)
    assert decisao.acoes == (AcaoMaquina.PREPARAR_RESUMO,)


def test_c3_encerramento_por_t35() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E14,),
        INCOMPLETOS,
        CondicoesCiclo(motivo_encerramento=MotivoEncerramento.SEM_INTERESSE),
    )
    assert decisao.caminho == (Transicao.T35,)
    assert decisao.estado_final is Estado.ENCERRADO
    assert decisao.motivo_encerramento is MotivoEncerramento.SEM_INTERESSE


def test_c4_humano_assumiu_por_t31() -> None:
    decisao = decidir(
        Estado.ENCAMINHADO_HUMANO, (Evento.E13,), QUALIFICADO, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T31,)
    assert decisao.estado_final is Estado.ATENDIMENTO_HUMANO


def test_c5_incompatibilidade_por_t23() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E08,),
        incompativel(VIOLACAO_TIPO),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T23,)
    assert decisao.acoes == (
        AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL,
        AcaoMaquina.NAO_AVANCAR_COLETA,
    )


def test_c6_pendencia_impeditiva_por_t18() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E09,),
        qual(ResultadoQualificacao.INDEFINIDO, pendencias=("campo.pendente",)),
        CondicoesCiclo(pendencia_impeditiva=True),
    )
    assert decisao.caminho == (Transicao.T18,)


def test_c7_disponibilidade_com_calendario_integrado() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03,),
        INCOMPLETOS,
        CondicoesCiclo(
            interesse_confirmar_disponibilidade=True, calendario_integrado=True
        ),
    )
    assert decisao.caminho == (Transicao.T14,)
    assert decisao.estado_final is Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE
    assert decisao.acoes == (AcaoMaquina.SOLICITAR_CONSULTA_CALENDARIO,)


def test_c7_disponibilidade_sem_calendario_integrado() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03,),
        INCOMPLETOS,
        CondicoesCiclo(
            interesse_confirmar_disponibilidade=True, calendario_integrado=False
        ),
    )
    assert decisao.caminho == (Transicao.T15,)
    assert decisao.acoes == (AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE,)


def test_c8_qualificacao_por_t13() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E07,),
        QUALIFICADO,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.caminho == (Transicao.T13,)
    assert decisao.acoes == (AcaoMaquina.PREPARAR_RESUMO,)


def test_c9_resposta_comercial_por_t28() -> None:
    decisao = decidir(
        Estado.ENCAMINHADO_HUMANO,
        (Evento.E06,),
        QUALIFICADO,
        CondicoesCiclo(resposta_aprovada_disponivel=True),
    )
    assert decisao.caminho == (Transicao.T28,)
    assert decisao.acoes == (
        AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,
        AcaoMaquina.REFORCAR_ENCAMINHAMENTO,
    )


def test_c10_pendencia_acessoria_por_t19() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E09,),
        QUALIFICADO,
        CondicoesCiclo(pendencia_impeditiva=False),
    )
    assert decisao.caminho == (Transicao.T19,)


def test_c11_coleta_por_t04() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E02,), INCOMPLETOS, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T04,)
    assert decisao.acoes == (AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,)


def test_t04_nao_e_elegivel_quando_incompativel() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E02,),
        incompativel(VIOLACAO_TIPO),
        SEM_CONDICOES,
    )
    assert decisao.caminho == ()
    assert decisao.efeitos == (EfeitoParalelo.P1,)


# --------------------------------------------------------------------------
# K. Precedências semânticas aprovadas
# --------------------------------------------------------------------------


def test_c0_t03_precede_t02_e_t01() -> None:
    decisao = decidir(
        Estado.NOVO,
        (Evento.E01, Evento.E06, Evento.E18),
        INCOMPLETOS,
        CondicoesCiclo(motivos_handoff=("pedido_humano",)),
    )
    assert decisao.caminho == (Transicao.T03,)
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF


def test_c0_t02_precede_t01() -> None:
    decisao = decidir(
        Estado.NOVO, (Evento.E01, Evento.E06), INCOMPLETOS, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T02,)
    assert Transicao.T01 not in decisao.caminho


def test_c3_t32_precede_t35_no_mesmo_e14() -> None:
    decisao = decidir(
        Estado.ENCAMINHADO_HUMANO,
        (Evento.E14,),
        QUALIFICADO,
        CondicoesCiclo(motivo_encerramento=MotivoEncerramento.SEM_INTERESSE),
    )
    assert decisao.caminho == (Transicao.T32,)
    assert Transicao.T35 not in decisao.caminho
    assert decisao.motivo_encerramento is None


def test_t34_permanece_separado_de_t35() -> None:
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO, (Evento.E14,), QUALIFICADO, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T34,)
    assert decisao.motivo_encerramento is None


def test_c11_t09_precede_t04_no_mesmo_e04() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E04,),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS, campos_ausentes=("formato",)),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T09,)
    assert Transicao.T04 not in decisao.caminho
    assert decisao.eventos_consumidos == (Evento.E04,)


def test_c8_t08_precede_t13_para_ressalva() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E07,),
        RESSALVA,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.caminho == (Transicao.T08,)
    assert Transicao.T13 not in decisao.caminho
    assert decisao.acoes == (AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE,)


def test_c8_t40_atende_respondendo_duvidas() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E07,),
        QUALIFICADO,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.caminho == (Transicao.T40,)
    assert decisao.acoes == (AcaoMaquina.PREPARAR_RESUMO,)


# --------------------------------------------------------------------------
# L. Múltiplas Txx independentes no mesmo ciclo
# --------------------------------------------------------------------------


def test_e04_e_e10_produzem_duas_transicoes() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E04, Evento.E10),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS, campos_ausentes=("formato",)),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T09, Transicao.T16)
    assert decisao.acoes == (
        AcaoMaquina.PERGUNTAR_FORMATO,
        AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,
    )
    assert decisao.efeitos == (EfeitoParalelo.P1, EfeitoParalelo.P2)


def test_e01_e_e10_produzem_t16_e_t41() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E01, Evento.E10),
        INCOMPLETOS,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.caminho == (Transicao.T16, Transicao.T41)
    assert decisao.eventos_consumidos == (Evento.E10, Evento.E01)


# --------------------------------------------------------------------------
# F/M. Consumo único e múltiplos E02–E05
# --------------------------------------------------------------------------


def test_t01_consome_e01_e_t41_nao_o_reutiliza() -> None:
    decisao = decidir(
        Estado.NOVO,
        (Evento.E01,),
        INCOMPLETOS,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.caminho == (Transicao.T01,)
    assert Transicao.T41 not in decisao.caminho
    assert decisao.eventos_consumidos == (Evento.E01,)


def test_t39_e_t41_nunca_disparam_pelo_mesmo_e01() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E01,),
        INCOMPLETOS,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.caminho == (Transicao.T39,)
    assert Transicao.T41 not in decisao.caminho


def test_t02_consome_e06_e_c9_nao_o_reutiliza() -> None:
    decisao = decidir(Estado.NOVO, (Evento.E06,), INCOMPLETOS, SEM_CONDICOES)
    assert decisao.caminho == (Transicao.T02,)
    assert Transicao.T17 not in decisao.caminho
    assert decisao.efeitos == ()


def test_multiplos_eventos_de_dado_aplicam_t04_uma_unica_vez() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E02, Evento.E03, Evento.E05),
        INCOMPLETOS,
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T04,)
    assert decisao.eventos_consumidos == (Evento.E02,)
    assert decisao.acoes == (AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,)
    assert decisao.efeitos == (EfeitoParalelo.P1,)


def test_t04_escolhe_o_proximo_gatilho_disponivel_apos_t09() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E04, Evento.E05),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS, campos_ausentes=("formato",)),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T09, Transicao.T04)
    assert decisao.eventos_consumidos == (Evento.E04, Evento.E05)


# --------------------------------------------------------------------------
# O. T27 e ordem das ações
# --------------------------------------------------------------------------


def test_t27_entrega_resumo_antes_de_emitir_encaminhamento() -> None:
    decisao = decidir(
        Estado.PRONTO_PARA_HANDOFF, (Evento.E12,), QUALIFICADO, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T27,)
    assert decisao.estado_final is Estado.ENCAMINHADO_HUMANO
    assert decisao.acoes == (
        AcaoMaquina.ENTREGAR_RESUMO,
        AcaoMaquina.EMITIR_MENSAGEM_DE_ENCAMINHAMENTO,
    )


def test_t35_despede_somente_para_sem_interesse() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E14,),
        INCOMPLETOS,
        CondicoesCiclo(motivo_encerramento=MotivoEncerramento.SEM_INTERESSE),
    )
    assert decisao.acoes == (AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE,)


@pytest.mark.parametrize(
    "motivo",
    [
        MotivoEncerramento.ENGANO,
        MotivoEncerramento.SPAM,
        MotivoEncerramento.INCOMPATIBILIDADE_ACEITA,
    ],
)
def test_t35_nao_despede_para_os_demais_motivos(motivo) -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E14,),
        INCOMPLETOS,
        CondicoesCiclo(motivo_encerramento=motivo),
    )
    assert decisao.caminho == (Transicao.T35,)
    assert decisao.acoes == ()
    assert decisao.motivo_encerramento is motivo


# --------------------------------------------------------------------------
# Efeitos, inércias e fechamento — smoke da Fatia 1
# --------------------------------------------------------------------------


def test_p6_vale_quando_disponibilidade_decide_o_estado() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03, Evento.E07),
        RESSALVA,
        CondicoesCiclo(
            insumo_qualificacao_atualizado=True,
            interesse_confirmar_disponibilidade=True,
            calendario_integrado=True,
        ),
    )
    assert decisao.caminho == (Transicao.T14,)
    assert EfeitoParalelo.P6 in decisao.efeitos
    assert Inercia.N2 in decisao.inercias
    assert decisao.acoes == (
        AcaoMaquina.SOLICITAR_CONSULTA_CALENDARIO,
        AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE,
    )


def test_p6_vale_quando_t40_decide_em_respondendo_duvidas() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E07,),
        RESSALVA,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert decisao.caminho == (Transicao.T40,)
    assert EfeitoParalelo.P6 in decisao.efeitos
    assert decisao.acoes == (
        AcaoMaquina.PREPARAR_RESUMO,
        AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE,
    )


def test_p6_nao_se_generaliza_quando_t08_decide() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E07,),
        RESSALVA,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert EfeitoParalelo.P6 not in decisao.efeitos


def test_n3_torna_e14_inerte_quando_ha_e18() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E14, Evento.E18),
        INCOMPLETOS,
        CondicoesCiclo(motivos_handoff=("pedido_humano",)),
    )
    assert decisao.caminho == (Transicao.T07,)
    assert decisao.inercias == (Inercia.N3,)


def test_n4_torna_e15_inerte_em_pronto_para_handoff() -> None:
    decisao = decidir(
        Estado.PRONTO_PARA_HANDOFF, (Evento.E15,), QUALIFICADO, SEM_CONDICOES
    )
    assert decisao.caminho == ()
    assert decisao.inercias == (Inercia.N4,)
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF


def test_fechamento_e15_retoma_coleta_por_t20() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E15,), INCOMPLETOS, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T20,)
    assert decisao.estado_final is Estado.COLETANDO_DADOS


def test_fechamento_e15_mantem_estado_por_t38() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E15,),
        incompativel(VIOLACAO_TIPO),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T38,)
    assert decisao.acoes == (AcaoMaquina.NAO_AVANCAR_COLETA,)


# --------------------------------------------------------------------------
# TransicaoInexistente
# --------------------------------------------------------------------------


def test_e15_sem_transicao_nem_inercia_e_erro_de_contrato() -> None:
    with pytest.raises(TransicaoInexistente):
        decidir(Estado.COLETANDO_DADOS, (Evento.E15,), INCOMPLETOS, SEM_CONDICOES)


def test_e12_fora_de_pronto_para_handoff_e_erro_de_contrato() -> None:
    with pytest.raises(TransicaoInexistente):
        decidir(Estado.COLETANDO_DADOS, (Evento.E12,), INCOMPLETOS, SEM_CONDICOES)


def test_e16_sem_t25_aplicavel_e_erro_de_contrato() -> None:
    with pytest.raises(TransicaoInexistente):
        decidir(Estado.COLETANDO_DADOS, (Evento.E16,), INCOMPLETOS, SEM_CONDICOES)


# --------------------------------------------------------------------------
# Pureza e ausência de estado interno
# --------------------------------------------------------------------------


def test_maquina_e_stateless_entre_chamadas() -> None:
    inicial = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E07,),
        QUALIFICADO,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert inicial.estado_final is Estado.PRONTO_PARA_HANDOFF

    apos_e15 = decidir(
        inicial.estado_final, (Evento.E15,), QUALIFICADO, SEM_CONDICOES
    )
    assert apos_e15.inercias == (Inercia.N4,)

    apos_e12 = decidir(
        apos_e15.estado_final, (Evento.E12,), QUALIFICADO, SEM_CONDICOES
    )
    assert apos_e12.estado_final is Estado.ENCAMINHADO_HUMANO

    repeticao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E07,),
        QUALIFICADO,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert repeticao == inicial


def test_entradas_nao_sao_mutadas() -> None:
    eventos = (Evento.E04, Evento.E10)
    condicoes = CondicoesCiclo(motivos_handoff=("pedido_humano",))
    qualificacao = qual(
        ResultadoQualificacao.DADOS_INCOMPLETOS, campos_ausentes=("formato",)
    )
    decidir(Estado.COLETANDO_DADOS, eventos, qualificacao, condicoes)

    assert eventos == (Evento.E04, Evento.E10)
    assert condicoes == CondicoesCiclo(motivos_handoff=("pedido_humano",))
    assert qualificacao.campos_ausentes == ("formato",)


# --------------------------------------------------------------------------
# P. Invariantes estruturais do módulo
# --------------------------------------------------------------------------


def _arvore_do_modulo() -> ast.Module:
    return ast.parse(MODULO_MAQUINA.read_text(encoding="utf-8"))


def test_maquina_nao_importa_recurso_externo_nem_camada_indevida() -> None:
    arvore = _arvore_do_modulo()
    importados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)

    proibidos = (
        "yaml",
        "casa77_sdr.knowledge",
        "casa77_sdr.persistence",
        "casa77_sdr.normalization",
        "json",
        "pathlib",
        "os",
        "socket",
        "datetime",
        "random",
    )
    for proibido in proibidos:
        assert proibido not in importados


def test_maquina_nao_faz_io_nem_usa_relogio() -> None:
    arvore = _arvore_do_modulo()
    nomes = {no.id for no in ast.walk(arvore) if isinstance(no, ast.Name)}
    atributos = {no.attr for no in ast.walk(arvore) if isinstance(no, ast.Attribute)}
    for proibido in ("open", "read_text", "write_text", "now", "today", "load"):
        assert proibido not in nomes | atributos


def test_maquina_nao_cria_fase_ciclo() -> None:
    arvore = _arvore_do_modulo()
    classes = {no.name for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)}
    assert "FaseCiclo" not in classes


def test_acoes_nao_usam_set_nem_deduplicacao_generica() -> None:
    fonte = MODULO_MAQUINA.read_text(encoding="utf-8")
    # Nenhuma rotina genérica de deduplicação: a ordem das ações é normativa
    # (doc 07 §4.5) e repetição legítima jamais é colapsada.
    assert "dict.fromkeys" not in fonte
    assert "deduplic" not in fonte.lower()
    assert "sorted(set(" not in fonte
    assert "set(self.acoes" not in fonte

    arvore = _arvore_do_modulo()
    # `frozenset` sobre os eventos confirmados é legítimo — é consulta de
    # pertinência, não acumulador de ações. O que não pode existir é literal ou
    # compreensão de conjunto colapsando qualquer coleção do módulo.
    assert not [no for no in ast.walk(arvore) if isinstance(no, ast.Set)]
    assert not [no for no in ast.walk(arvore) if isinstance(no, ast.SetComp)]


def test_maquina_nao_cita_resposta_aprovada_nem_valor_comercial() -> None:
    fonte = MODULO_MAQUINA.read_text(encoding="utf-8")
    for proibido in ("R$", "casa77.yaml", "precos", "capacidade.", "horarios"):
        assert proibido not in fonte

    arvore = _arvore_do_modulo()
    textos = [
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    ]
    import re

    for texto in textos:
        assert not re.search(r"\bR\d{2}\b", texto)


def test_maquina_nao_tem_constante_numerica_comercial() -> None:
    """I06: nenhum número do módulo pode ser valor comercial.

    A lista permitida é deliberadamente mínima e explícita: qualquer literal
    numérico novo faz este teste falhar e exige revisão consciente.
    """
    arvore = _arvore_do_modulo()
    numeros = sorted(
        {
            no.value
            for no in ast.walk(arvore)
            if isinstance(no, ast.Constant)
            and isinstance(no.value, (int, float))
            and not isinstance(no.value, bool)
        }
    )
    # 1 — checagem de cardinalidade de evento isolado (`len(confirmados) != 1`).
    # Nenhum preço, capacidade, horário, duração ou quantidade de pacotes.
    assert numeros == [1]


# ==========================================================================
# FATIA 2 — MATRIZ COMPORTAMENTAL EXAUSTIVA
# ==========================================================================
#
# Cada caso abaixo chama `decidir()` de verdade: a cobertura de T01–T41 é
# comportamental, não inspeção do mapa interno.


COND_INSUMO = CondicoesCiclo(insumo_qualificacao_atualizado=True)
COND_RESPOSTA = CondicoesCiclo(resposta_aprovada_disponivel=True)
COND_IMPEDITIVA = CondicoesCiclo(pendencia_impeditiva=True)
COND_ACESSORIA = CondicoesCiclo(pendencia_impeditiva=False)
COND_HANDOFF = CondicoesCiclo(motivos_handoff=("motivo-tecnico",))
FORMATO_AUSENTE = qual(
    ResultadoQualificacao.DADOS_INCOMPLETOS, campos_ausentes=("formato",)
)
INDEFINIDO = qual(ResultadoQualificacao.INDEFINIDO, pendencias=("campo.pendente",))

# (transicao, estado, eventos, qualificacao, condicoes, estado_final, acoes)
MATRIZ_POSITIVA = [
    (
        Transicao.T01, Estado.NOVO, (Evento.E01,), INCOMPLETOS, SEM_CONDICOES,
        Estado.COLETANDO_DADOS, (AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL,),
    ),
    (
        Transicao.T02, Estado.NOVO, (Evento.E06,), INCOMPLETOS, SEM_CONDICOES,
        Estado.RESPONDENDO_DUVIDAS, (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,),
    ),
    (
        Transicao.T03, Estado.NOVO, (Evento.E18,), INCOMPLETOS, COND_HANDOFF,
        Estado.PRONTO_PARA_HANDOFF, (AcaoMaquina.PREPARAR_RESUMO,),
    ),
    (
        Transicao.T04, Estado.COLETANDO_DADOS, (Evento.E02,), INCOMPLETOS,
        SEM_CONDICOES, Estado.COLETANDO_DADOS,
        (AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,),
    ),
    (
        Transicao.T05, Estado.COLETANDO_DADOS, (Evento.E08,),
        incompativel(VIOLACAO_DATA), SEM_CONDICOES, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL,),
    ),
    (
        Transicao.T06, Estado.COLETANDO_DADOS, (Evento.E08,),
        incompativel(VIOLACAO_TIPO), SEM_CONDICOES, Estado.COLETANDO_DADOS,
        (AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL, AcaoMaquina.NAO_AVANCAR_COLETA),
    ),
    (
        Transicao.T07, Estado.COLETANDO_DADOS, (Evento.E18,), INCOMPLETOS,
        COND_HANDOFF, Estado.PRONTO_PARA_HANDOFF, (AcaoMaquina.PREPARAR_RESUMO,),
    ),
    (
        Transicao.T08, Estado.COLETANDO_DADOS, (Evento.E07,), RESSALVA,
        COND_INSUMO, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE,),
    ),
    (
        Transicao.T09, Estado.COLETANDO_DADOS, (Evento.E04,), FORMATO_AUSENTE,
        SEM_CONDICOES, Estado.COLETANDO_DADOS, (AcaoMaquina.PERGUNTAR_FORMATO,),
    ),
    (
        Transicao.T10, Estado.COLETANDO_DADOS, (Evento.E06,), INCOMPLETOS,
        COND_RESPOSTA, Estado.RESPONDENDO_DUVIDAS,
        (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,),
    ),
    (
        Transicao.T11, Estado.COLETANDO_DADOS, (Evento.E09,), INDEFINIDO,
        COND_IMPEDITIVA, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    ),
    (
        Transicao.T12, Estado.COLETANDO_DADOS, (Evento.E09,), QUALIFICADO,
        COND_ACESSORIA, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    ),
    (
        Transicao.T13, Estado.COLETANDO_DADOS, (Evento.E07,), QUALIFICADO,
        COND_INSUMO, Estado.PRONTO_PARA_HANDOFF, (AcaoMaquina.PREPARAR_RESUMO,),
    ),
    (
        Transicao.T14, Estado.COLETANDO_DADOS, (Evento.E03,), INCOMPLETOS,
        CondicoesCiclo(
            interesse_confirmar_disponibilidade=True, calendario_integrado=True
        ),
        Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
        (AcaoMaquina.SOLICITAR_CONSULTA_CALENDARIO,),
    ),
    (
        Transicao.T15, Estado.COLETANDO_DADOS, (Evento.E03,), INCOMPLETOS,
        CondicoesCiclo(
            interesse_confirmar_disponibilidade=True, calendario_integrado=False
        ),
        Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE,),
    ),
    (
        Transicao.T16, Estado.COLETANDO_DADOS, (Evento.E10,), INCOMPLETOS,
        SEM_CONDICOES, Estado.COLETANDO_DADOS,
        (AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,),
    ),
    (
        Transicao.T17, Estado.RESPONDENDO_DUVIDAS, (Evento.E06,), INCOMPLETOS,
        COND_RESPOSTA, Estado.RESPONDENDO_DUVIDAS,
        (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,),
    ),
    (
        Transicao.T18, Estado.RESPONDENDO_DUVIDAS, (Evento.E09,), INDEFINIDO,
        COND_IMPEDITIVA, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    ),
    (
        Transicao.T19, Estado.RESPONDENDO_DUVIDAS, (Evento.E09,), QUALIFICADO,
        COND_ACESSORIA, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    ),
    (
        Transicao.T20, Estado.RESPONDENDO_DUVIDAS, (Evento.E15,), INCOMPLETOS,
        SEM_CONDICOES, Estado.COLETANDO_DADOS,
        (AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR,),
    ),
    (
        Transicao.T21, Estado.RESPONDENDO_DUVIDAS, (Evento.E15,), QUALIFICADO,
        SEM_CONDICOES, Estado.PRONTO_PARA_HANDOFF, (AcaoMaquina.PREPARAR_RESUMO,),
    ),
    (
        Transicao.T22, Estado.RESPONDENDO_DUVIDAS, (Evento.E08,),
        incompativel(VIOLACAO_DATA), SEM_CONDICOES, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL,),
    ),
    (
        Transicao.T23, Estado.RESPONDENDO_DUVIDAS, (Evento.E08,),
        incompativel(VIOLACAO_CONVIDADOS), SEM_CONDICOES,
        Estado.RESPONDENDO_DUVIDAS,
        (AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL, AcaoMaquina.NAO_AVANCAR_COLETA),
    ),
    (
        Transicao.T24, Estado.RESPONDENDO_DUVIDAS, (Evento.E18,), INCOMPLETOS,
        COND_HANDOFF, Estado.PRONTO_PARA_HANDOFF, (AcaoMaquina.PREPARAR_RESUMO,),
    ),
    (
        Transicao.T25, Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
        (Evento.E16,), INCOMPLETOS, SEM_CONDICOES, Estado.PRONTO_PARA_HANDOFF, (),
    ),
    (
        Transicao.T26, Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
        (Evento.E18,), INCOMPLETOS, COND_HANDOFF, Estado.PRONTO_PARA_HANDOFF,
        (AcaoMaquina.PREPARAR_RESUMO,),
    ),
    (
        Transicao.T27, Estado.PRONTO_PARA_HANDOFF, (Evento.E12,), QUALIFICADO,
        SEM_CONDICOES, Estado.ENCAMINHADO_HUMANO,
        (AcaoMaquina.ENTREGAR_RESUMO, AcaoMaquina.EMITIR_MENSAGEM_DE_ENCAMINHAMENTO),
    ),
    (
        Transicao.T28, Estado.ENCAMINHADO_HUMANO, (Evento.E06,), QUALIFICADO,
        COND_RESPOSTA, Estado.ENCAMINHADO_HUMANO,
        (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL, AcaoMaquina.REFORCAR_ENCAMINHAMENTO),
    ),
    (
        Transicao.T29, Estado.ENCAMINHADO_HUMANO, (Evento.E15,), QUALIFICADO,
        SEM_CONDICOES, Estado.ENCAMINHADO_HUMANO, (AcaoMaquina.NAO_AVANCAR_COLETA,),
    ),
    (
        Transicao.T30, Estado.ENCAMINHADO_HUMANO, (Evento.E18,), QUALIFICADO,
        COND_HANDOFF, Estado.ENCAMINHADO_HUMANO, (),
    ),
    (
        Transicao.T31, Estado.ENCAMINHADO_HUMANO, (Evento.E13,), QUALIFICADO,
        SEM_CONDICOES, Estado.ATENDIMENTO_HUMANO,
        (AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA,),
    ),
    (
        Transicao.T32, Estado.ENCAMINHADO_HUMANO, (Evento.E14,), QUALIFICADO,
        SEM_CONDICOES, Estado.ENCERRADO, (),
    ),
    (
        Transicao.T33, Estado.ATENDIMENTO_HUMANO, (Evento.E01,), QUALIFICADO,
        SEM_CONDICOES, Estado.ATENDIMENTO_HUMANO,
        (AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA,),
    ),
    (
        Transicao.T34, Estado.ATENDIMENTO_HUMANO, (Evento.E14,), QUALIFICADO,
        SEM_CONDICOES, Estado.ENCERRADO, (),
    ),
    (
        Transicao.T35, Estado.COLETANDO_DADOS, (Evento.E14,), INCOMPLETOS,
        CondicoesCiclo(motivo_encerramento=MotivoEncerramento.ENGANO),
        Estado.ENCERRADO, (),
    ),
    (
        Transicao.T36, Estado.ENCERRADO, (Evento.E01,), INCOMPLETOS,
        CondicoesCiclo(identidade=Identidade.MESMA_SOLICITACAO),
        Estado.COLETANDO_DADOS, (AcaoMaquina.REABRIR_ATENDIMENTO,),
    ),
    (
        Transicao.T37, Estado.ENCERRADO, (Evento.E01,), INCOMPLETOS,
        CondicoesCiclo(identidade=Identidade.NOVA_SOLICITACAO),
        Estado.COLETANDO_DADOS, (AcaoMaquina.ABRIR_NOVO_ATENDIMENTO,),
    ),
    (
        Transicao.T38, Estado.RESPONDENDO_DUVIDAS, (Evento.E15,),
        incompativel(VIOLACAO_TIPO), SEM_CONDICOES, Estado.RESPONDENDO_DUVIDAS,
        (AcaoMaquina.NAO_AVANCAR_COLETA,),
    ),
    (
        Transicao.T39, Estado.RESPONDENDO_DUVIDAS, (Evento.E01,), INCOMPLETOS,
        COND_INSUMO, Estado.COLETANDO_DADOS,
        (AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR,),
    ),
    (
        Transicao.T40, Estado.RESPONDENDO_DUVIDAS, (Evento.E07,), QUALIFICADO,
        COND_INSUMO, Estado.PRONTO_PARA_HANDOFF, (AcaoMaquina.PREPARAR_RESUMO,),
    ),
    (
        Transicao.T41, Estado.COLETANDO_DADOS, (Evento.E01,), INCOMPLETOS,
        COND_INSUMO, Estado.COLETANDO_DADOS,
        (AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,),
    ),
]


@pytest.mark.parametrize(
    "transicao, estado, eventos, qualificacao, condicoes, esperado, acoes",
    MATRIZ_POSITIVA,
    ids=[caso[0].value for caso in MATRIZ_POSITIVA],
)
def test_matriz_positiva_t01_a_t41(
    transicao, estado, eventos, qualificacao, condicoes, esperado, acoes
) -> None:
    decisao = decidir(estado, eventos, qualificacao, condicoes)
    assert decisao.caminho == (transicao,)
    assert decisao.estado_final is esperado
    assert decisao.acoes == acoes
    assert decisao.eventos_consumidos == eventos


def test_matriz_positiva_cobre_todas_as_quarenta_e_uma_transicoes() -> None:
    assert {caso[0] for caso in MATRIZ_POSITIVA} == set(Transicao)


def test_preparar_resumo_produzido_por_exatamente_sete_transicoes_reais() -> None:
    produtores = set()
    for caso in MATRIZ_POSITIVA:
        transicao, estado, eventos, qualificacao, condicoes, _, _ = caso
        decisao = decidir(estado, eventos, qualificacao, condicoes)
        if AcaoMaquina.PREPARAR_RESUMO in decisao.acoes:
            produtores.add(transicao)
    assert produtores == {
        Transicao.T03,
        Transicao.T07,
        Transicao.T13,
        Transicao.T21,
        Transicao.T24,
        Transicao.T26,
        Transicao.T40,
    }


# --------------------------------------------------------------------------
# Negativos discriminantes
# --------------------------------------------------------------------------


def test_negativo_t08_qualificado_sem_ressalva_vai_para_t13() -> None:
    decisao = decidir(Estado.COLETANDO_DADOS, (Evento.E07,), QUALIFICADO, COND_INSUMO)
    assert Transicao.T08 not in decisao.caminho
    assert decisao.caminho == (Transicao.T13,)


def test_negativo_t09_sem_formato_ausente_vai_para_t04() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E04,), INCOMPLETOS, SEM_CONDICOES
    )
    assert Transicao.T09 not in decisao.caminho
    assert decisao.caminho == (Transicao.T04,)


def test_negativo_t10_sem_resposta_aprovada_nao_responde() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E06, Evento.E09),
        QUALIFICADO,
        CondicoesCiclo(resposta_aprovada_disponivel=False, pendencia_impeditiva=False),
    )
    assert Transicao.T10 not in decisao.caminho
    assert decisao.caminho == (Transicao.T12,)
    assert EfeitoParalelo.P3 in decisao.efeitos


def test_negativo_t17_sem_resposta_aprovada_nao_responde() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E06, Evento.E09),
        QUALIFICADO,
        CondicoesCiclo(resposta_aprovada_disponivel=None, pendencia_impeditiva=False),
    )
    assert Transicao.T17 not in decisao.caminho
    assert decisao.caminho == (Transicao.T19,)


def test_negativo_t28_sem_resposta_aprovada_nao_responde() -> None:
    decisao = decidir(
        Estado.ENCAMINHADO_HUMANO,
        (Evento.E06, Evento.E09),
        QUALIFICADO,
        CondicoesCiclo(resposta_aprovada_disponivel=False, pendencia_impeditiva=False),
    )
    assert decisao.caminho == ()
    assert EfeitoParalelo.P3 in decisao.efeitos
    assert EfeitoParalelo.P5 in decisao.efeitos


def test_negativo_t11_com_pendencia_acessoria_vai_para_t12() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E09,), QUALIFICADO, COND_ACESSORIA
    )
    assert Transicao.T11 not in decisao.caminho
    assert decisao.caminho == (Transicao.T12,)


def test_negativo_t12_com_pendencia_impeditiva_vai_para_t11() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E09,), INDEFINIDO, COND_IMPEDITIVA
    )
    assert Transicao.T12 not in decisao.caminho
    assert decisao.caminho == (Transicao.T11,)


def test_negativo_t18_com_pendencia_acessoria_vai_para_t19() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E09,), QUALIFICADO, COND_ACESSORIA
    )
    assert Transicao.T18 not in decisao.caminho
    assert decisao.caminho == (Transicao.T19,)


def test_negativo_t19_com_pendencia_impeditiva_vai_para_t18() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E09,), INDEFINIDO, COND_IMPEDITIVA
    )
    assert Transicao.T19 not in decisao.caminho
    assert decisao.caminho == (Transicao.T18,)


def test_negativo_t14_sem_interesse_cai_na_coleta() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03,),
        INCOMPLETOS,
        CondicoesCiclo(calendario_integrado=True),
    )
    assert Transicao.T14 not in decisao.caminho
    assert Transicao.T15 not in decisao.caminho
    assert decisao.caminho == (Transicao.T04,)


def test_negativo_t15_com_calendario_integrado_vai_para_t14() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03,),
        INCOMPLETOS,
        CondicoesCiclo(
            interesse_confirmar_disponibilidade=True, calendario_integrado=True
        ),
    )
    assert Transicao.T15 not in decisao.caminho
    assert decisao.caminho == (Transicao.T14,)


def test_negativo_t20_com_resultado_positivo_vai_para_t21() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E15,), QUALIFICADO, SEM_CONDICOES
    )
    assert Transicao.T20 not in decisao.caminho
    assert Transicao.T38 not in decisao.caminho
    assert decisao.caminho == (Transicao.T21,)


def test_negativo_t21_com_dados_incompletos_vai_para_t20() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E15,), INCOMPLETOS, SEM_CONDICOES
    )
    assert Transicao.T21 not in decisao.caminho
    assert Transicao.T38 not in decisao.caminho
    assert decisao.caminho == (Transicao.T20,)


def test_negativo_t35_com_e18_nao_entra() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E14, Evento.E18),
        INCOMPLETOS,
        CondicoesCiclo(
            motivos_handoff=("motivo-tecnico",),
            motivo_encerramento=MotivoEncerramento.SEM_INTERESSE,
        ),
    )
    assert Transicao.T35 not in decisao.caminho
    assert decisao.caminho == (Transicao.T07,)
    assert decisao.inercias == (Inercia.N3,)
    assert decisao.motivo_encerramento is None
    assert AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE not in decisao.acoes


def test_negativo_t36_com_nova_solicitacao_vai_para_t37() -> None:
    decisao = decidir(
        Estado.ENCERRADO,
        (Evento.E01,),
        INCOMPLETOS,
        CondicoesCiclo(identidade=Identidade.NOVA_SOLICITACAO),
    )
    assert Transicao.T36 not in decisao.caminho
    assert decisao.caminho == (Transicao.T37,)


def test_negativo_t37_com_mesma_solicitacao_vai_para_t36() -> None:
    decisao = decidir(
        Estado.ENCERRADO,
        (Evento.E01,),
        INCOMPLETOS,
        CondicoesCiclo(identidade=Identidade.MESMA_SOLICITACAO),
    )
    assert Transicao.T37 not in decisao.caminho
    assert decisao.caminho == (Transicao.T36,)


def test_negativo_identidade_ausente_em_encerrado_torna_e01_inerte() -> None:
    decisao = decidir(Estado.ENCERRADO, (Evento.E01,), INCOMPLETOS, SEM_CONDICOES)
    assert decisao.caminho == ()
    assert decisao.inercias == (Inercia.N1,)


@pytest.mark.parametrize(
    "condicoes, qualificacao",
    [
        (CondicoesCiclo(insumo_qualificacao_atualizado=False), INCOMPLETOS),
        (CondicoesCiclo(), INCOMPLETOS),
        (COND_INSUMO, QUALIFICADO),
    ],
)
def test_negativo_t39_sem_condicoes_torna_e01_inerte(condicoes, qualificacao) -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E01,), qualificacao, condicoes
    )
    assert Transicao.T39 not in decisao.caminho
    assert decisao.inercias == (Inercia.N1,)


def test_negativo_t39_com_e06_no_ciclo_nao_entra() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E01, Evento.E06),
        INCOMPLETOS,
        CondicoesCiclo(
            insumo_qualificacao_atualizado=True, resposta_aprovada_disponivel=True
        ),
    )
    assert Transicao.T39 not in decisao.caminho
    assert decisao.caminho == (Transicao.T17,)
    assert decisao.inercias == (Inercia.N1,)


@pytest.mark.parametrize(
    "condicoes, qualificacao",
    [
        (CondicoesCiclo(insumo_qualificacao_atualizado=False), INCOMPLETOS),
        (CondicoesCiclo(), INCOMPLETOS),
        (COND_INSUMO, QUALIFICADO),
    ],
)
def test_negativo_t41_sem_condicoes_torna_e01_inerte(condicoes, qualificacao) -> None:
    decisao = decidir(Estado.COLETANDO_DADOS, (Evento.E01,), qualificacao, condicoes)
    assert Transicao.T41 not in decisao.caminho
    assert decisao.inercias == (Inercia.N1,)


def test_negativo_t41_com_evento_de_dado_no_ciclo_nao_entra() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E01, Evento.E02), INCOMPLETOS, COND_INSUMO
    )
    assert Transicao.T41 not in decisao.caminho
    assert decisao.caminho == (Transicao.T04,)
    assert decisao.inercias == (Inercia.N1,)


# --------------------------------------------------------------------------
# Caminhos multi-Txx
# --------------------------------------------------------------------------


def test_multi_t01_continua_o_ciclo_apos_c0() -> None:
    """Após T01 o mesmo ciclo segue: T16 (C11) entra a partir do novo estado."""
    decisao = decidir(
        Estado.NOVO, (Evento.E01, Evento.E10), INCOMPLETOS, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T01, Transicao.T16)
    assert decisao.estado_final is Estado.COLETANDO_DADOS
    assert decisao.acoes == (
        AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL,
        AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,
    )


def test_t15_muda_o_estado_e_preempta_t16_que_sobrevive_por_p2() -> None:
    """T15 (C7) leva a `pronto_para_handoff`; T16 exige `coletando_dados`.

    O `E10` não é consumido por transição alguma, mas o interesse de visita é
    preservado por P2 — é exatamente o papel do efeito paralelo.
    """
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03, Evento.E10),
        INCOMPLETOS,
        CondicoesCiclo(
            interesse_confirmar_disponibilidade=True, calendario_integrado=False
        ),
    )
    assert decisao.caminho == (Transicao.T15,)
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF
    assert decisao.eventos_consumidos == (Evento.E03,)
    assert decisao.efeitos == (EfeitoParalelo.P1, EfeitoParalelo.P2)


def test_multi_t09_e_t16_permanecem_no_mesmo_estado() -> None:
    """Duas Txx que preservam `coletando_dados` entram no mesmo caminho."""
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E04, Evento.E10),
        FORMATO_AUSENTE,
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T09, Transicao.T16)
    assert decisao.estado_final is Estado.COLETANDO_DADOS
    assert decisao.eventos_consumidos == (Evento.E04, Evento.E10)


# --------------------------------------------------------------------------
# Múltiplos E02–E05
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "eventos, gatilho",
    [
        ((Evento.E02, Evento.E03), Evento.E02),
        ((Evento.E02, Evento.E04), Evento.E02),
        ((Evento.E03, Evento.E04), Evento.E03),
        ((Evento.E02, Evento.E03, Evento.E04, Evento.E05), Evento.E02),
    ],
)
def test_multiplos_dados_aplicam_t04_uma_vez(eventos, gatilho) -> None:
    decisao = decidir(Estado.COLETANDO_DADOS, eventos, INCOMPLETOS, SEM_CONDICOES)
    assert decisao.caminho == (Transicao.T04,)
    assert decisao.eventos_consumidos == (gatilho,)
    assert decisao.acoes == (AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,)
    assert EfeitoParalelo.P1 in decisao.efeitos


def test_t04_respeita_e03_consumido_por_t15() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03, Evento.E04),
        FORMATO_AUSENTE,
        CondicoesCiclo(
            interesse_confirmar_disponibilidade=True, calendario_integrado=False
        ),
    )
    # T15 (C7) consome E03 e leva a pronto_para_handoff; C11 já não roda.
    assert decisao.caminho == (Transicao.T15,)
    assert decisao.eventos_consumidos == (Evento.E03,)
    assert EfeitoParalelo.P1 in decisao.efeitos


# --------------------------------------------------------------------------
# P1–P6 — positivos e negativos
# --------------------------------------------------------------------------


def test_p1_negativo_sem_evento_de_dado() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E10,), INCOMPLETOS, SEM_CONDICOES
    )
    assert EfeitoParalelo.P1 not in decisao.efeitos


def test_p1_presente_mesmo_com_dado_consumido_por_t09() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E04,), FORMATO_AUSENTE, SEM_CONDICOES
    )
    assert decisao.caminho == (Transicao.T09,)
    assert EfeitoParalelo.P1 in decisao.efeitos


def test_p2_negativo_sem_e10() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS, (Evento.E02,), INCOMPLETOS, SEM_CONDICOES
    )
    assert EfeitoParalelo.P2 not in decisao.efeitos


def test_p3_positivo_quando_decisao_anterior_impede_consumo_de_e06() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E06, Evento.E18),
        INCOMPLETOS,
        CondicoesCiclo(
            motivos_handoff=("motivo-tecnico",), resposta_aprovada_disponivel=True
        ),
    )
    assert decisao.caminho == (Transicao.T07,)
    assert EfeitoParalelo.P3 in decisao.efeitos


@pytest.mark.parametrize(
    "estado, transicao",
    [
        (Estado.NOVO, Transicao.T02),
        (Estado.COLETANDO_DADOS, Transicao.T10),
        (Estado.RESPONDENDO_DUVIDAS, Transicao.T17),
        (Estado.ENCAMINHADO_HUMANO, Transicao.T28),
    ],
)
def test_p3_negativo_quando_e06_e_consumido(estado, transicao) -> None:
    decisao = decidir(estado, (Evento.E06,), QUALIFICADO, COND_RESPOSTA)
    assert decisao.caminho == (transicao,)
    assert EfeitoParalelo.P3 not in decisao.efeitos


def test_p4_positivo_quando_e08_e_preemptado() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E08, Evento.E18),
        incompativel(VIOLACAO_TIPO),
        COND_HANDOFF,
    )
    assert decisao.caminho == (Transicao.T07,)
    assert EfeitoParalelo.P4 in decisao.efeitos


def test_p4_negativo_com_incompatibilidade_historica_sem_e08() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E10,),
        incompativel(VIOLACAO_TIPO),
        SEM_CONDICOES,
    )
    assert decisao.caminho == (Transicao.T16,)
    assert EfeitoParalelo.P4 not in decisao.efeitos


@pytest.mark.parametrize(
    "impeditiva, qualificacao",
    [(True, INDEFINIDO), (False, QUALIFICADO)],
)
def test_p5_positivo_quando_e09_e_preemptado(impeditiva, qualificacao) -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E09, Evento.E18),
        qualificacao,
        CondicoesCiclo(
            motivos_handoff=("motivo-tecnico",), pendencia_impeditiva=impeditiva
        ),
    )
    assert decisao.caminho == (Transicao.T07,)
    assert EfeitoParalelo.P5 in decisao.efeitos


@pytest.mark.parametrize(
    "estado, impeditiva, qualificacao, transicao",
    [
        (Estado.COLETANDO_DADOS, True, INDEFINIDO, Transicao.T11),
        (Estado.COLETANDO_DADOS, False, QUALIFICADO, Transicao.T12),
        (Estado.RESPONDENDO_DUVIDAS, True, INDEFINIDO, Transicao.T18),
        (Estado.RESPONDENDO_DUVIDAS, False, QUALIFICADO, Transicao.T19),
    ],
)
def test_p5_negativo_quando_e09_e_consumido(
    estado, impeditiva, qualificacao, transicao
) -> None:
    decisao = decidir(
        estado,
        (Evento.E09,),
        qualificacao,
        CondicoesCiclo(pendencia_impeditiva=impeditiva),
    )
    assert decisao.caminho == (transicao,)
    assert EfeitoParalelo.P5 not in decisao.efeitos


def test_p6_negativo_com_qualificado_sem_ressalva() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03, Evento.E07),
        QUALIFICADO,
        CondicoesCiclo(
            insumo_qualificacao_atualizado=True,
            interesse_confirmar_disponibilidade=True,
            calendario_integrado=True,
        ),
    )
    assert decisao.caminho == (Transicao.T14,)
    assert EfeitoParalelo.P6 not in decisao.efeitos
    assert AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE not in decisao.acoes


def test_p6_acrescenta_exatamente_uma_acao() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E07,), RESSALVA, COND_INSUMO
    )
    assert decisao.efeitos == (EfeitoParalelo.P6,)
    assert decisao.acoes == (
        AcaoMaquina.PREPARAR_RESUMO,
        AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE,
    )


# --------------------------------------------------------------------------
# N1–N4 — positivos e negativos
# --------------------------------------------------------------------------


def test_n1_negativo_quando_e01_e_consumido() -> None:
    decisao = decidir(Estado.NOVO, (Evento.E01,), INCOMPLETOS, SEM_CONDICOES)
    assert decisao.inercias == ()


def test_n2_positivo_com_t14() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E03, Evento.E07),
        QUALIFICADO,
        CondicoesCiclo(
            insumo_qualificacao_atualizado=True,
            interesse_confirmar_disponibilidade=True,
            calendario_integrado=True,
        ),
    )
    assert decisao.caminho == (Transicao.T14,)
    assert Inercia.N2 in decisao.inercias


def test_n2_negativo_quando_nenhuma_txx_anterior_a_c8_decide() -> None:
    """`E02` só é resolvido por P1 (C11 não alcança este estado).

    Sem qualquer transição anterior a C8, `E07` não vira inércia: fica sem
    transição, efeito ou inércia e fecha como erro de contrato.
    """
    with pytest.raises(TransicaoInexistente):
        decidir(
            Estado.ENCAMINHADO_HUMANO,
            (Evento.E07, Evento.E02),
            QUALIFICADO,
            COND_INSUMO,
        )


def test_n3_negativo_quando_e14_e_consumido() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        (Evento.E14,),
        INCOMPLETOS,
        CondicoesCiclo(motivo_encerramento=MotivoEncerramento.SPAM),
    )
    assert decisao.caminho == (Transicao.T35,)
    assert decisao.inercias == ()


def test_n4_negativo_quando_e15_encontra_transicao() -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E15,), INCOMPLETOS, SEM_CONDICOES
    )
    assert Inercia.N4 not in decisao.inercias


# --------------------------------------------------------------------------
# Eventos de ciclo próprio e encadeamento stateless
# --------------------------------------------------------------------------


def test_e12_fora_de_pronto_para_handoff_nao_transiciona() -> None:
    with pytest.raises(TransicaoInexistente):
        decidir(Estado.ENCAMINHADO_HUMANO, (Evento.E12,), QUALIFICADO, SEM_CONDICOES)


def test_e15_em_estado_sem_transicao_nem_inercia() -> None:
    with pytest.raises(TransicaoInexistente):
        decidir(Estado.NOVO, (Evento.E15,), INCOMPLETOS, SEM_CONDICOES)


def test_e13_fora_de_encaminhado_humano_nao_transiciona() -> None:
    with pytest.raises(TransicaoInexistente):
        decidir(Estado.COLETANDO_DADOS, (Evento.E13,), INCOMPLETOS, SEM_CONDICOES)


def test_encadeamento_completo_em_chamadas_separadas() -> None:
    """Ciclo inicial → fechamento por `E15` → fechamento por `E12`."""
    inicial = decidir(
        Estado.RESPONDENDO_DUVIDAS, (Evento.E06,), INCOMPLETOS, COND_RESPOSTA
    )
    assert inicial.caminho == (Transicao.T17,)
    assert inicial.estado_final is Estado.RESPONDENDO_DUVIDAS

    apos_e15 = decidir(inicial.estado_final, (Evento.E15,), QUALIFICADO, SEM_CONDICOES)
    assert apos_e15.caminho == (Transicao.T21,)
    assert apos_e15.estado_final is Estado.PRONTO_PARA_HANDOFF

    apos_e12 = decidir(apos_e15.estado_final, (Evento.E12,), QUALIFICADO, SEM_CONDICOES)
    assert apos_e12.caminho == (Transicao.T27,)
    assert apos_e12.estado_final is Estado.ENCAMINHADO_HUMANO

    # Reexecutar a primeira chamada devolve exatamente a mesma decisão: não há
    # memória oculta nem contador de chamadas.
    assert (
        decidir(Estado.RESPONDENDO_DUVIDAS, (Evento.E06,), INCOMPLETOS, COND_RESPOSTA)
        == inicial
    )


# --------------------------------------------------------------------------
# T35 — as quatro modalidades
# --------------------------------------------------------------------------


@pytest.mark.parametrize("motivo", list(MotivoEncerramento))
def test_t35_ecoa_as_quatro_modalidades(motivo) -> None:
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        (Evento.E14,),
        INCOMPLETOS,
        CondicoesCiclo(motivo_encerramento=motivo),
    )
    assert decisao.caminho == (Transicao.T35,)
    assert decisao.estado_final is Estado.ENCERRADO
    assert decisao.motivo_encerramento is motivo
    esperado = (
        (AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE,)
        if motivo is MotivoEncerramento.SEM_INTERESSE
        else ()
    )
    assert decisao.acoes == esperado


# --------------------------------------------------------------------------
# E08 — matriz completa por estado e classe
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "estado, violacoes, transicao, estado_final",
    [
        (
            Estado.COLETANDO_DADOS, (VIOLACAO_DATA,), Transicao.T05,
            Estado.PRONTO_PARA_HANDOFF,
        ),
        (
            Estado.COLETANDO_DADOS, (VIOLACAO_TIPO,), Transicao.T06,
            Estado.COLETANDO_DADOS,
        ),
        (
            Estado.COLETANDO_DADOS, (VIOLACAO_CONVIDADOS,), Transicao.T06,
            Estado.COLETANDO_DADOS,
        ),
        (
            Estado.COLETANDO_DADOS, (VIOLACAO_TIPO, VIOLACAO_DATA), Transicao.T05,
            Estado.PRONTO_PARA_HANDOFF,
        ),
        (
            Estado.RESPONDENDO_DUVIDAS, (VIOLACAO_DATA,), Transicao.T22,
            Estado.PRONTO_PARA_HANDOFF,
        ),
        (
            Estado.RESPONDENDO_DUVIDAS, (VIOLACAO_TIPO,), Transicao.T23,
            Estado.RESPONDENDO_DUVIDAS,
        ),
        (
            Estado.RESPONDENDO_DUVIDAS, (VIOLACAO_CONVIDADOS,), Transicao.T23,
            Estado.RESPONDENDO_DUVIDAS,
        ),
        (
            Estado.RESPONDENDO_DUVIDAS,
            (VIOLACAO_CONVIDADOS, VIOLACAO_DATA, VIOLACAO_TIPO),
            Transicao.T22,
            Estado.PRONTO_PARA_HANDOFF,
        ),
    ],
)
def test_matriz_e08(estado, violacoes, transicao, estado_final) -> None:
    decisao = decidir(estado, (Evento.E08,), incompativel(*violacoes), SEM_CONDICOES)
    assert decisao.caminho == (transicao,)
    assert decisao.estado_final is estado_final
    assert decisao.eventos_consumidos == (Evento.E08,)
    assert EfeitoParalelo.P4 not in decisao.efeitos


# --------------------------------------------------------------------------
# E06 / D6 — matriz por estado
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "estado, transicao, estado_final",
    [
        (Estado.NOVO, Transicao.T02, Estado.RESPONDENDO_DUVIDAS),
        (Estado.COLETANDO_DADOS, Transicao.T10, Estado.RESPONDENDO_DUVIDAS),
        (Estado.RESPONDENDO_DUVIDAS, Transicao.T17, Estado.RESPONDENDO_DUVIDAS),
        (Estado.ENCAMINHADO_HUMANO, Transicao.T28, Estado.ENCAMINHADO_HUMANO),
    ],
)
def test_matriz_e06_com_resposta_aprovada(estado, transicao, estado_final) -> None:
    decisao = decidir(estado, (Evento.E06,), QUALIFICADO, COND_RESPOSTA)
    assert decisao.caminho == (transicao,)
    assert decisao.estado_final is estado_final
    assert EfeitoParalelo.P3 not in decisao.efeitos


def test_e06_em_novo_dispensa_resposta_aprovada() -> None:
    decisao = decidir(Estado.NOVO, (Evento.E06,), INCOMPLETOS, SEM_CONDICOES)
    assert decisao.caminho == (Transicao.T02,)
