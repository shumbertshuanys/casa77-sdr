"""Etapa 13 do ciclo — persistir o estado final e marcar a chave (doc 07 §5, §7.2).

A etapa 13 **antecede** a 14 sem exceção: nada é emitido por quem chama
enquanto este módulo não devolver `True`.

- O registro é montado por `desidratar` com a **última** decisão do ciclo
  (estado final), a qualificação e o S2-D8 da primeira decisão, e os dados
  **atualizados** pela etapa 6 (não os do início do ciclo).
- Atendimento novo (`id_atendimento is None`) → `criar_com_marco_de_transicao`
  com o id vindo de `gerar_id`; existente → `gravar_com_marco_de_transicao`
  com o `marco_atual` hidratado.
- Sucesso → `marcar_chave_processada` e `True`. Se a marcação falhar, a exceção
  propaga (TS45-13).
- `FalhaDePersistencia` (capturada **por classe**) → preservar pendente →
  alertar (`alerta_operacional`) → **não** marcar a chave → `False` (§7.2).
  Qualquer outro erro (contrato, `TypeError`, `ValueError`) propaga intacto.

Sem relógio vivo: o instante do ciclo é `EntradaMensagem.recebida_em`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from casa77_sdr.alerta_operacional import preservar_e_alertar
from casa77_sdr.hydration import desidratar
from casa77_sdr.motor_deps import DependenciasMotor
from casa77_sdr.normalization import EntradaMensagem, EntradaNormalizada
from casa77_sdr.orchestrator_decision import PrimeiraDecisao
from casa77_sdr.orchestrator_emission import TextoFinal
from casa77_sdr.orchestrator_identity import AlvoDoCiclo
from casa77_sdr.persistence import FalhaDePersistencia, ProcessamentoPendente
from casa77_sdr.transition_marker_write import (
    criar_com_marco_de_transicao,
    gravar_com_marco_de_transicao,
)

__all__ = ["persistir_ciclo"]


def persistir_ciclo(
    *,
    deps: DependenciasMotor,
    alvo: AlvoDoCiclo,
    primeira: PrimeiraDecisao,
    texto_final: TextoFinal,
    entrada: EntradaMensagem,
    entrada_normalizada: EntradaNormalizada,
    gerar_id: Callable[[], str],
) -> bool:
    """Grava o ciclo; `True` se gravado e chave marcada, `False` se bloqueado."""
    atendimento = alvo.atendimento
    novo = atendimento.id_atendimento is None
    id_atendimento = gerar_id() if novo else atendimento.id_atendimento
    atual = replace(atendimento, dados=primeira.atualizacao.dados_atualizados)
    registro_base = desidratar(
        atual,
        id_atendimento=id_atendimento,
        canal=entrada.canal,
        contato=entrada.contato,
        decisao=texto_final.decisoes_do_ciclo[-1],
        qualificacao=primeira.qualificacao,
        s2d8=primeira.s2d8,
    )
    chave = entrada_normalizada.chave_idempotencia
    try:
        if novo:
            criar_com_marco_de_transicao(
                persistencia=deps.persistencia,
                registro_base=registro_base,
                instante_de_referencia_do_ciclo=entrada.recebida_em,
                decisoes_do_ciclo=texto_final.decisoes_do_ciclo,
            )
        else:
            gravar_com_marco_de_transicao(
                persistencia=deps.persistencia,
                registro_base=registro_base,
                instante_de_referencia_do_ciclo=entrada.recebida_em,
                marco_atual=atendimento.marco_atual,
                decisoes_do_ciclo=texto_final.decisoes_do_ciclo,
            )
    except FalhaDePersistencia as falha:
        preservar_e_alertar(
            persistencia=deps.persistencia,
            pendente=ProcessamentoPendente(
                canal=entrada.canal,
                contato=entrada.contato,
                conteudo=entrada_normalizada.mensagem_normalizada,
            ),
            categoria=type(falha).__name__,
            correlacao=chave,
            tentar_alerta=deps.tentar_alerta,
        )
        return False
    deps.persistencia.marcar_chave_processada(chave)
    return True
