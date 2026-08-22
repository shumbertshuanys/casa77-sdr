"""Aplicação e escrita do marco temporal (doc 07 §6.2, N-a-T2–N-a-T7).

Fronteira **chamável e mínima** entre a decisão já materializada em
`transition_marker.py` e o contrato de escrita já existente da persistência
operacional. Ela faz exatamente três coisas:

1. **delega** a decisão do marco a `decidir_instante_ultima_transicao(...)`;
2. **aplica** o valor decidido sobre um `RegistroAtendimento` **recebido
   pronto**, substituindo **somente** `instante_ultima_transicao`;
3. **escreve** pelo contrato existente — `criar` ou `gravar`.

**A operação chega pronta na função chamada**: `criar_com_marco_de_transicao`
sempre cria e `gravar_com_marco_de_transicao` sempre grava. Esta fronteira
**não deriva** criar × gravar de nada.

Fora do escopo, e **não implementados** aqui: a **montagem completa** do
registro, a **decisão de se a etapa 13 executa**, a **escolha** entre criar e
gravar no pipeline, a **geração** de `id_atendimento`, a **marcação de
idempotência**, a **preservação de pendente**, o **tratamento operacional de
falha** (S4, S5) e o `OrquestradorMotor` — que **continua não implementado**.
A **integração da etapa 13 no pipeline permanece pendente**.

Fronteira: **zero relógio vivo**, zero conversão de fuso, zero aritmética
temporal, zero leitura da persistência, zero `try`/`except` em torno da
escrita. A regra de decisão **não é duplicada**: este módulo chama, não
reimplementa — e **não lê** `transicoes_que_mudaram_estado`, `caminho` ou
qualquer outro campo de `DecisaoMaquina`.

A validação de **fuso efetivo** do marco também não é duplicada: ela pertence
à fronteira de escrita da persistência (M-T3), que rejeita o valor inválido.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime

from casa77_sdr.persistence import PersistenciaOperacional, RegistroAtendimento
from casa77_sdr.state_machine import DecisaoMaquina
from casa77_sdr.transition_marker import decidir_instante_ultima_transicao


def _exigir_fronteiras(
    persistencia: object, registro_base: object
) -> None:
    """Valida os dois insumos próprios desta fronteira.

    As mensagens citam **apenas o nome do parâmetro**: nunca o identificador do
    atendimento, o canal, o contato ou o conteúdo da conversa (§6.6).

    Os demais argumentos **não** são revalidados aqui — instante, marco e
    decisões já são validados por `decidir_instante_ultima_transicao(...)`, e o
    marco resultante pela persistência.
    """
    if not isinstance(persistencia, PersistenciaOperacional):
        raise TypeError(
            "O campo 'persistencia' deve ser uma PersistenciaOperacional"
        )
    if not isinstance(registro_base, RegistroAtendimento):
        raise TypeError(
            "O campo 'registro_base' deve ser um RegistroAtendimento"
        )


def _aplicar_marco(
    registro_base: RegistroAtendimento, marco_decidido: datetime | None
) -> RegistroAtendimento:
    """Projeta o marco decidido sobre o registro, sem tocar em mais nada.

    `replace` produz um **registro novo**: `registro_base` não é mutado, e
    nenhum outro campo é montado, derivado ou alterado.
    """
    return replace(registro_base, instante_ultima_transicao=marco_decidido)


def criar_com_marco_de_transicao(
    *,
    persistencia: PersistenciaOperacional,
    registro_base: RegistroAtendimento,
    instante_de_referencia_do_ciclo: datetime,
    decisoes_do_ciclo: Sequence[DecisaoMaquina],
) -> RegistroAtendimento:
    """Cria o atendimento com o marco decidido para a **criação** (N-a-T3).

    A decisão é delegada com `criacao_de_atendimento=True` e `marco_atual=None`
    — na criação não existe transição anterior a detectar, e a projeção da
    máquina **não é pré-requisito**.

    Devolve **exatamente** o registro submetido a `criar`.

    Erros da decisão (`TypeError`, `ValueError`) e da persistência
    (`FalhaDePersistencia`, `ValueError` de identificador já existente ou de
    marco sem fuso efetivo) **propagam intactos**: nada é capturado, convertido,
    encapsulado, registrado em log ou transformado em booleano.
    """
    _exigir_fronteiras(persistencia, registro_base)

    marco_decidido = decidir_instante_ultima_transicao(
        criacao_de_atendimento=True,
        instante_de_referencia_do_ciclo=instante_de_referencia_do_ciclo,
        marco_atual=None,
        decisoes_do_ciclo=decisoes_do_ciclo,
    )

    registro = _aplicar_marco(registro_base, marco_decidido)
    persistencia.criar(registro)
    return registro


def gravar_com_marco_de_transicao(
    *,
    persistencia: PersistenciaOperacional,
    registro_base: RegistroAtendimento,
    instante_de_referencia_do_ciclo: datetime,
    marco_atual: datetime | None,
    decisoes_do_ciclo: Sequence[DecisaoMaquina],
) -> RegistroAtendimento:
    """Grava o atendimento existente com o marco decidido (N-a-T4–N-a-T7).

    A decisão é delegada com `criacao_de_atendimento=False`: atualiza para o
    instante do ciclo quando **ao menos uma** das decisões produzidas tiver
    projeção não vazia, e **preserva** o `marco_atual` — inclusive `None` —
    quando nenhuma tiver.

    O `marco_atual` chega **do chamador**: esta fronteira **não o deriva** do
    registro recebido nem consulta a persistência para obtê-lo.

    Devolve **exatamente** o registro submetido a `gravar`. Erros da decisão e
    da persistência — incluindo identificador inexistente e vínculo
    canal × contato divergente — **propagam intactos**.
    """
    _exigir_fronteiras(persistencia, registro_base)

    marco_decidido = decidir_instante_ultima_transicao(
        criacao_de_atendimento=False,
        instante_de_referencia_do_ciclo=instante_de_referencia_do_ciclo,
        marco_atual=marco_atual,
        decisoes_do_ciclo=decisoes_do_ciclo,
    )

    registro = _aplicar_marco(registro_base, marco_decidido)
    persistencia.gravar(registro)
    return registro
