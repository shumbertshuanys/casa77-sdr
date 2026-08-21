"""Decisão determinística do marco temporal (doc 07 §6.2, N-a-T2–N-a-T7).

Este módulo responde **uma única pergunta**: qual valor de
`instante_ultima_transicao` o **futuro chamador da etapa 13** deverá usar neste
ciclo. Ele materializa a **decisão**, não a escrita.

Fora do escopo, e **não implementados** aqui: a **aplicação** dessa decisão pelo
chamador da etapa 13, a **escrita efetiva** via `criar`/`gravar`, a montagem de
`RegistroAtendimento`, a criação operacional do atendimento, a integração do
pipeline e o `OrquestradorMotor` — que **continua não implementado**. Nada disso
decorre desta função.

Fronteira: **zero persistência**, zero I/O, zero rede, zero YAML, zero LLM e
**zero relógio vivo**. O instante devolvido é sempre um dos dois objetos
recebidos — o do ciclo ou o marco atual —, **nunca** um instante novo: não há
conversão de fuso, `astimezone`, substituição de `tzinfo` nem aritmética
temporal (N-a-T2).

A validação de **fuso efetivo** não é duplicada aqui: ela já pertence às
fronteiras existentes — `recebida_em` no `NormalizadorEntrada` e
`instante_ultima_transicao` na persistência (M-T3). Este módulo exige apenas
que os instantes sejam `datetime`.

De `DecisaoMaquina` é consultado **exclusivamente**
`transicoes_que_mudaram_estado`: a máquina é a autoridade sobre "mudou estado"
(doc 06 §4.2). Não há *replay*, não há concatenação de caminhos, não há acesso
à estrutura interna de regras da máquina e não há comparação entre estado
inicial e final.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from casa77_sdr.state_machine import DecisaoMaquina

# Teto normativo do ciclo: chamada inicial, mais eventual pós-`E15`, mais
# eventual pós-`E12` (doc 06 §4.2, *Limite de chamadas*). O contrato aceita
# **de zero a três** decisões efetivamente produzidas: nada aqui presume que as
# três existam.
_MAXIMO_DE_DECISOES_POR_CICLO = 3


def _exigir_instante(valor: object, campo: str) -> None:
    """Exige `datetime`. `bool` não é aceito por acidente em campo temporal."""
    if not isinstance(valor, datetime):
        raise TypeError(f"O campo '{campo}' deve ser um instante")


def _exigir_decisoes(decisoes_do_ciclo: object) -> Sequence[DecisaoMaquina]:
    """Valida a sequência de decisões efetivamente produzidas no ciclo.

    `str` e `bytes` são sequências para o runtime, mas não são sequências de
    decisões: são rejeitados junto com os demais tipos.
    """
    if isinstance(decisoes_do_ciclo, (str, bytes)) or not isinstance(
        decisoes_do_ciclo, Sequence
    ):
        raise TypeError(
            "O campo 'decisoes_do_ciclo' deve ser uma sequência de decisões"
        )
    for decisao in decisoes_do_ciclo:
        if not isinstance(decisao, DecisaoMaquina):
            raise TypeError(
                "Cada item de 'decisoes_do_ciclo' deve ser uma decisão da máquina"
            )
    if len(decisoes_do_ciclo) > _MAXIMO_DE_DECISOES_POR_CICLO:
        raise ValueError(
            "O ciclo produz no máximo três decisões da máquina de estados"
        )
    return decisoes_do_ciclo


def _houve_mudanca_no_ciclo(decisoes_do_ciclo: Sequence[DecisaoMaquina]) -> bool:
    """Composição das até três chamadas (doc 07 §6.2, regra 7).

    Houve mudança **no ciclo** se, e somente se, **ao menos uma** das decisões
    efetivamente produzidas tiver projeção **não vazia**. A ordem entre elas é
    irrelevante, e a **cardinalidade** da projeção não vira um marco por
    transição (N-a-T7).
    """
    return any(
        decisao.transicoes_que_mudaram_estado for decisao in decisoes_do_ciclo
    )


def decidir_instante_ultima_transicao(
    *,
    criacao_de_atendimento: bool,
    instante_de_referencia_do_ciclo: datetime,
    marco_atual: datetime | None,
    decisoes_do_ciclo: Sequence[DecisaoMaquina],
) -> datetime | None:
    """Decide o valor de `instante_ultima_transicao` para este ciclo.

    Três desfechos fechados:

    1. **Criação** (N-a-T3) — devolve o `instante_de_referencia_do_ciclo`. Não
       existe transição anterior a detectar, e a projeção da máquina **não é
       pré-requisito**: um `marco_atual` preenchido não altera o desfecho e
       não é tratado como erro.
    2. **Atendimento existente com mudança** (N-a-T4, N-a-T5, N-a-T7) — se ao
       menos uma decisão produzida tiver projeção não vazia, devolve o
       `instante_de_referencia_do_ciclo`. Vale inclusive quando o estado final
       do ciclo é igual ao inicial.
    3. **Atendimento existente sem mudança** (N-a-T6) — devolve o
       `marco_atual` **como está**, inclusive `None`.

    O valor devolvido é sempre **o mesmo objeto** recebido, nunca um instante
    reconstruído (N-a-T2).

    Erros:

    - `TypeError` — tipo runtime incompatível em qualquer argumento;
    - `ValueError` — mais de três decisões no ciclo.
    """
    if not isinstance(criacao_de_atendimento, bool):
        raise TypeError("O campo 'criacao_de_atendimento' deve ser booleano")
    _exigir_instante(
        instante_de_referencia_do_ciclo, "instante_de_referencia_do_ciclo"
    )
    if marco_atual is not None:
        _exigir_instante(marco_atual, "marco_atual")
    decisoes = _exigir_decisoes(decisoes_do_ciclo)

    # A validação é integral **antes** de qualquer desfecho: entrada malformada
    # nunca produz decisão, mesmo nos ramos que ignorariam o campo inválido.
    if criacao_de_atendimento:
        return instante_de_referencia_do_ciclo
    if _houve_mudanca_no_ciclo(decisoes):
        return instante_de_referencia_do_ciclo
    return marco_atual
