"""Avaliação determinística de `ASSERTIVA` sobre um valor já resolvido.

Uma `ASSERTIVA` declara uma condição que precisa ser verdadeira para que a
redação já aprovada de um fragmento continue verdadeira (C-5). Ela é
**consistency-only** (C-5i–C-5q, C-A2-NR7): não cria regra comercial, não altera
dado, não produz ação, evento, handoff nem condição de ciclo, e não decide
`resposta_aprovada_disponivel` nem `pendencia_impeditiva`.

Este módulo materializa **somente o julgamento**: dado um predicado do
vocabulário fechado de C-5 — `EH_VERDADEIRO` e `EH_FALSO`, sem nenhum terceiro
(C-A1-R) — e um valor **já resolvido pelo chamador**, decide se a assertiva se
sustenta.

**Escopo do domínio, deliberadamente estreito.** A fronteira avalia **apenas o
domínio booleano**, que é o único hoje decidível sem coerção nem semântica
inventada. Um valor fora desse domínio é **NÃO AVALIÁVEL** e levanta
`AssertivaNaoAvaliavel` — ele **não** é tratado como assertiva falsa, e **nenhum
significado** lhe é atribuído (C-7). Esta entrega **não afirma** que todo domínio
futuro de `ASSERTIVA` seja booleano: ela **não infere** nenhum outro domínio, e
**ampliar o domínio exigiria contrato posterior explícito**.

**Sem coerção.** Não há *truthiness*, `bool(...)`, comparação com `1` ou `0`,
leitura de texto como `"true"`/`"false"`, análise, normalização ou *fallback*.
Em Python `0 == False` e `1 == True`, mas aqui `0` **não** é `False` e `1`
**não** é `True`: a decisão é por tipo estrito, nunca por igualdade permissiva.
O predicado, do mesmo modo, é consultado **como chegou** — sem `upper`, sem
`strip` e sem tolerância de caixa (C-A1-R4).

**O que chega pronto.** O predicado e o valor são **entregues pelo chamador**.
Este módulo **não** resolve referente, **não** lê a base autoritativa, **não**
conhece a origem do fato, o índice, o fragmento, o `Rxx`, o Markdown, o
*template*, o *placeholder*, o *renderer* nem qualquer consumidor; **não**
renderiza, **não** formata, **não** compara texto, **não** seleciona resposta e
**não** decide candidatura, disponibilidade ou ciclo (C-12, C-A2-ESC10).

Falha é **fail-closed** e imediata: a primeira violação encerra, e nada é
acumulado (P5). A mensagem carrega **categoria e localizador**, nunca o predicado
recebido, o valor recebido, o tipo concreto ou qualquer conteúdo.

**AVALIAR NÃO É MATERIALIZAR `C`.** O índice continua inexistente, nenhum
fragmento real é validado e nenhum consumidor é integrado.
"""

from __future__ import annotations

__all__ = ["AssertivaNaoAvaliavel", "avaliar_assertiva"]


class AssertivaNaoAvaliavel(Exception):
    """A assertiva não pode ser julgada com o que foi recebido.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** impede o julgamento e o localizador diz **onde** — nunca o predicado,
    o valor, o tipo concreto ou o conteúdo recebido.

    Isto **não é `False`**: é a **ausência de veredito**. Quem chama **deve
    parar ou escalar**, nunca tratar como assertiva não satisfeita.
    """


# Categorias técnicas privadas e fechadas. Elas nomeiam o impedimento e **não**
# são identificadores normativos novos de `C`.
_TIPO_INVALIDO = "tipo_invalido"
_VALOR_INVALIDO = "valor_invalido"

# Localizadores fechados.
_PREDICADO = "predicado"
_VALOR = "valor"

# C-5g, C-5h e C-A1-R: vocabulario fechado, sem terceiro predicado.
_EH_VERDADEIRO = "EH_VERDADEIRO"
_EH_FALSO = "EH_FALSO"
_PREDICADOS = frozenset({_EH_VERDADEIRO, _EH_FALSO})


def avaliar_assertiva(predicado: str, valor: object) -> bool:
    """Decide se a assertiva se sustenta sobre o valor já resolvido.

    Devolve `True` quando o predicado se verifica e `False` quando não se
    verifica — os **quatro** casos avaliáveis são `EH_VERDADEIRO` com `True` ou
    `False`, e `EH_FALSO` com `False` ou `True`.

    A validação segue uma ordem fixa: **tipo do predicado**, **valor do
    predicado**, **domínio do valor**, avaliação. A **primeira violação
    encerra**, e nada é acumulado.

    Levanta `AssertivaNaoAvaliavel` quando o predicado não é `str`, quando ele
    está fora do vocabulário fechado, ou quando o valor não é booleano estrito.
    Nesse último caso **não há veredito**: `False` **não** é devolvido, e o valor
    **não** ganha significado algum.
    """
    if not isinstance(predicado, str):
        raise _nao_avaliavel(_TIPO_INVALIDO, _PREDICADO)
    if predicado not in _PREDICADOS:
        raise _nao_avaliavel(_VALOR_INVALIDO, _PREDICADO)
    if not isinstance(valor, bool):
        raise _nao_avaliavel(_TIPO_INVALIDO, _VALOR)

    if predicado == _EH_VERDADEIRO:
        return valor
    return not valor


def _nao_avaliavel(categoria: str, localizador: str) -> AssertivaNaoAvaliavel:
    return AssertivaNaoAvaliavel(f"{categoria}: {localizador}")
