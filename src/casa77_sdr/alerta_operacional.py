"""Alerta operacional compartilhado pelos desfechos terminais do orquestrador.

Módulo-folha: **não** importa nenhum módulo do orquestrador, para que
`orchestrator` e `orchestrator_identity` possam usá-lo sem ciclo de importação.
Concentra a sequência crítica **preservar → tentar alerta** com a precedência
de falhas de **OL-4** (`TS45-7`, `TS45-11`, `E4-8`, `E4-11`) e a **única**
tentativa isolada de alerta do código de orquestração (`TS45-12`, `E4-12`).

A marcação da chave de idempotência **fica com o chamador**, porque a ordem
difere entre desfechos (TS45 e E4 marcam depois; a falha do produtor de
interpretação não marca).

Fronteira: nenhum relógio, nenhum *logging*, nenhuma rede, nenhum retry.
"""

from __future__ import annotations

from collections.abc import Callable

from casa77_sdr.persistence import PersistenciaOperacional, ProcessamentoPendente

__all__ = ["preservar_e_alertar", "tentar_alerta_operacional"]


def preservar_e_alertar(
    *,
    persistencia: PersistenciaOperacional,
    pendente: ProcessamentoPendente,
    categoria: str,
    correlacao: str,
    tentar_alerta: Callable[..., object],
) -> None:
    """Preserva o pendente e **sempre** tenta o alerta operacional.

    O `finally` materializa a precedência de **OL-4** sem capturar a exceção da
    preservação: se `preservar_pendente` falhar, o alerta ainda é tentado — com
    `pendente_preservado=False` (`TS45-11`, `E4-11`) — e a **exceção da
    preservação** propaga **por identidade**. Uma falha do alerta **não a
    substitui**, porque a tentativa é isolada e absorvida em
    `tentar_alerta_operacional`. Quem chama decide se marca a chave depois.
    """
    pendente_preservado = False
    try:
        persistencia.preservar_pendente(pendente)
        pendente_preservado = True
    finally:
        tentar_alerta_operacional(
            tentar_alerta,
            categoria=categoria,
            pendente_preservado=pendente_preservado,
            correlacao=correlacao,
        )


def tentar_alerta_operacional(
    tentar_alerta: Callable[..., object],
    *,
    categoria: str,
    pendente_preservado: bool,
    correlacao: str,
) -> None:
    """**Tenta** o alerta operacional, em caminho separado da conversa.

    `TS45-14` — o *payload* é fechado em **exatamente três** informações
    sanitizadas: a **categoria estrutural**, o **sucesso ou falha da
    preservação** e uma **correlação opaca**. A chamada é **por palavras-
    chave**, sem DTO e sem `Protocol`, e o retorno é **ignorado**: sucesso é a
    **ausência de exceção**, nunca uma confirmação de entrega.

    `TS45-12`/`E4-12` — a entrega **não é garantida**. A falha da tentativa é
    absorvida aqui e **somente aqui**: este é o **único** `except Exception`
    do código de orquestração, e ele envolve **exclusivamente** a chamada
    injetada. Zero retry, zero fila, zero contador, zero status de entrega e
    zero *fallback* para o canal da conversa.
    """
    try:
        tentar_alerta(
            categoria=categoria,
            pendente_preservado=pendente_preservado,
            correlacao=correlacao,
        )
    except Exception:
        return
