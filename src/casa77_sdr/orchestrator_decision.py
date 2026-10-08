"""Etapas 6 e 7 do ciclo — dados, avaliação a montante e primeira decisão.

Coordena, sobre o `AlvoDoCiclo` devolvido pelas etapas 4–5, a **etapa 6**
(`atualizar_dados_atendimento`) e a **ordem conceitual determinística anterior
à etapa 7** de `docs/07-arquitetura-motor-respostas.md` §5:

1. `RegrasComerciais` (`avaliar_regras`);
2. `Qualificador` com `pendencias_impeditivas = ()` → qualificação provisória;
3–5. S2-D8 (`decidir_pendencias_e_cobertura`) — eixos A e B e causas de `E09`;
6. `Qualificador` com as pendências impeditivas do eixo A → qualificação final;
7. eventos internos, *handoff*, encerramento, agregação dos eventos, montagem
   das oito condições de §4.4 e **primeira chamada** de `decidir`.

**Classe I bloqueia antes da etapa 7** (D8-CI7–D8-CI14): a exceção da fronteira
de origem atravessa **intacta** e `decidir` **não** é chamado. Preservar e
alertar pertence ao chamador.

Três montagens são deste coordenador:

- **`fatos_runtime`** — sem calendário integrado (condição 6 *fail-closed*), a
  fotografia factual é `{"consulta_calendario_valida": False}`: `R05/F1` é o
  único candidato de `R05`, e `R05/F2`/`R05/F3` nunca o são. `{}` **não** serve:
  S2-D8 o aceita na forma, mas fecha como Classe I assim que avalia qualquer
  token de `R05` (campo ausente — `coverage_decision._e_candidato`).
- **aplicabilidade de pacote** — `decidir_aplicabilidade_de_pacote` exige
  `DadosExtraidos` (§4.4.4, AP-1: *"o que se sabe do evento neste ciclo"*). Os
  dados **já atualizados** pela etapa 6 são projetados com confiança `ALTA`,
  porque a etapa 6 só admite valor de confiança `ALTA` (§4.1.8). Só
  `convidados` e `formato` são projetados; nenhuma PII atravessa.
- **contato do canal** — `docs/06` §6: *"telefone obtido automaticamente pelo
  canal"*. Quando a entrada traz identificador de canal não vazio e, depois da
  etapa 6, `DadosQualificacao.contato` continua vazio, o contato da
  qualificação é preenchido com ele (fora da interpretação do LLM). O contato
  dado explicitamente pelo interessado **nunca** é sobrescrito: um vigente igual
  ao identificador do canal é tratado como ainda vazio diante da etapa 6, de
  modo que um contato explícito posterior é admitido. Consequência aceita:
  `R31/F5` deixa de ser perguntado quando o canal fornece o número.

Sem I/O, sem relógio, sem persistência, sem emissão.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from casa77_sdr.closure_decision import decidir_encerramento
from casa77_sdr.coverage_decision import ResultadoS2D8, decidir_pendencias_e_cobertura
from casa77_sdr.cycle_events import produzir_eventos_internos_ciclo
from casa77_sdr.cycle_inputs import (
    agregar_eventos_primeira_decisao,
    montar_condicoes_ciclo,
)
from casa77_sdr.data_update import (
    ResultadoAtualizacaoDados,
    atualizar_dados_atendimento,
)
from casa77_sdr.handoff_detection import detectar_handoff
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    _CAMPOS_DADOS,
    DadosExtraidos,
    Interpretacao,
    _mesmo_valor,
)
from casa77_sdr.motor_deps import BaseMotor
from casa77_sdr.orchestrator_identity import AlvoDoCiclo
from casa77_sdr.pricing_applicability import decidir_aplicabilidade_de_pacote
from casa77_sdr.qualification import DadosQualificacao, Qualificacao, qualificar
from casa77_sdr.rules import avaliar_regras
from casa77_sdr.state_machine import CondicoesCiclo, DecisaoMaquina, Evento, decidir

__all__ = ["PrimeiraDecisao", "dados_para_aplicabilidade", "decidir_primeira_chamada"]

#: Fotografia factual sem calendário integrado: nenhuma consulta válida.
_FATOS_RUNTIME_SEM_CALENDARIO = "consulta_calendario_valida"


@dataclass(frozen=True)
class PrimeiraDecisao:
    """Resultado da etapa 7 e os insumos exatos que a produziram.

    `eventos` e `condicoes` são os **mesmos objetos** passados a `decidir`, para
    que as reentradas de fechamento (`E15`, `E12`) não recalculem nada.
    """

    decisao: DecisaoMaquina
    qualificacao: Qualificacao
    s2d8: ResultadoS2D8
    atualizacao: ResultadoAtualizacaoDados
    eventos: tuple[Evento, ...]
    condicoes: CondicoesCiclo


def decidir_primeira_chamada(
    alvo: AlvoDoCiclo,
    *,
    base_motor: BaseMotor,
    calendario_integrado: bool,
    e01_confirmado: bool,
    contato_canal: str | None = None,
) -> PrimeiraDecisao:
    """Executa as etapas 6 e 7 na ordem de §5 e devolve a primeira decisão."""
    interpretacao = alvo.artefatos.interpretacao
    base = base_motor.base

    # Etapa 6 — dados e correções; depois, o contato do canal se ainda vazio.
    atualizacao = _atualizar_com_contato_do_canal(
        alvo.atendimento.dados, interpretacao, contato_canal
    )
    dados = atualizacao.dados_atualizados

    # 1–2. Regras e qualificação provisória.
    violacoes = tuple(avaliar_regras(dados.atendimento, base))
    q_provisoria = qualificar(dados, violacoes, (), base)

    # 3–5. S2-D8. Classe I atravessa intacta: a máquina não executa.
    aplicabilidade = decidir_aplicabilidade_de_pacote(dados_para_aplicabilidade(dados), base)
    s2d8 = decidir_pendencias_e_cobertura(
        interpretacao,
        q_provisoria,
        base_motor.mapa,
        base_motor.indice,
        base_motor.consistencia,
        {_FATOS_RUNTIME_SEM_CALENDARIO: False},
        aplicabilidade,
    )

    # 6. Qualificação final.
    q_final = qualificar(dados, violacoes, s2d8.pendencias_impeditivas, base)

    # 7. Eventos e condições já decididos, depois a primeira chamada.
    internos = produzir_eventos_internos_ciclo(
        q_final, atualizacao.insumo_qualificacao_atualizado, s2d8
    )
    handoff = detectar_handoff(interpretacao)
    encerramento = decidir_encerramento(interpretacao, q_final.resultado)
    eventos = agregar_eventos_primeira_decisao(
        e01_confirmado,
        alvo.artefatos.eventos_interpretacao,
        internos,
        handoff,
        encerramento,
    )
    condicoes = montar_condicoes_ciclo(
        atualizacao.insumo_qualificacao_atualizado,
        s2d8.pendencia_impeditiva,
        handoff,
        s2d8.resposta_aprovada_disponivel,
        alvo.artefatos.interesse_confirmar_disponibilidade,
        calendario_integrado,
        alvo.decisao_identidade.identidade,
        encerramento,
    )
    decisao = decidir(alvo.atendimento.estado, eventos, q_final, condicoes)
    return PrimeiraDecisao(
        decisao=decisao,
        qualificacao=q_final,
        s2d8=s2d8,
        atualizacao=atualizacao,
        eventos=eventos,
        condicoes=condicoes,
    )


def _atualizar_com_contato_do_canal(
    vigentes: DadosQualificacao,
    interpretacao: Interpretacao,
    contato_canal: str | None,
) -> ResultadoAtualizacaoDados:
    """Etapa 6 e, na sua fronteira, o preenchimento do contato pelo canal.

    Sem identificador de canal, é exatamente a etapa 6. Com ele: um vigente
    igual ao identificador (preenchido pelo canal num ciclo anterior) entra na
    etapa 6 como vazio, para que um contato explícito do interessado seja
    admitido; se o contato final continuar vazio, recebe o identificador. A
    mutação efetiva é recalculada contra os vigentes originais.
    """
    if contato_canal is None or not contato_canal.strip():
        return atualizar_dados_atendimento(vigentes, interpretacao)
    entrada_etapa_6 = (
        replace(vigentes, contato=None) if vigentes.contato == contato_canal else vigentes
    )
    atualizacao = atualizar_dados_atendimento(entrada_etapa_6, interpretacao)
    dados = atualizacao.dados_atualizados
    if dados.contato is None:
        dados = replace(dados, contato=contato_canal)
    return replace(
        atualizacao,
        dados_atualizados=dados,
        insumo_qualificacao_atualizado=_mutou(vigentes, dados),
    )


def _mutou(antes: DadosQualificacao, depois: DadosQualificacao) -> bool:
    """Mutação efetiva (igualdade estrita de domínio, P-1) entre os seis campos."""

    def valor(dados: DadosQualificacao, campo: str) -> object:
        if campo in ("tipo_evento", "data_nomeada", "convidados"):
            return getattr(dados.atendimento, campo)
        return getattr(dados, campo)

    return any(
        not _mesmo_valor(valor(antes, campo), valor(depois, campo))
        for campo in _CAMPOS_DADOS
    )


def dados_para_aplicabilidade(dados: DadosQualificacao) -> DadosExtraidos:
    """Projeta o que se sabe do evento (após a etapa 6) para §4.4.4.

    A etapa 6 só admite valor de confiança `ALTA`; por isso todo valor vigente é
    projetado com `ALTA`, e valor ausente sem confiança (N-b-D*).
    """
    convidados = dados.atendimento.convidados
    formato = dados.formato
    return DadosExtraidos(
        convidados=convidados,
        confianca_convidados=None if convidados is None else Confianca.ALTA,
        formato=formato,
        confianca_formato=None if formato is None else Confianca.ALTA,
    )
