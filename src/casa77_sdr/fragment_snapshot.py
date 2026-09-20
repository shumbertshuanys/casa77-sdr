"""Montagem compartilhada da **`FotografiaFragmento`** de um token candidato.

Esta fronteira responde a **uma** pergunta, e nada mais —

> qual é a **fotografia** deste fragmento, dado o `ResultadoConsistencia` já
> produzido e os pares de `ASSERTIVA` de runtime já resolvidos?

**Montar não é avaliar.** Ela **não** decide emissibilidade: **`D8-F`**
continua com **uma única implementação de decisão**, `avaliar_emissibilidade`
(`docs/07` §4.4.5). O que passa a existir aqui é **uma única fronteira de
montagem** da fotografia que aquela primitiva consome — antes duplicada
*inline* dentro de S2-D8.

**O que ela NÃO faz.** Ela **não** decide candidatura, **não** decide
cobertura, **não** resolve *binding*, **não** lê índice, **não** lê YAML,
**não** abre `knowledge/**`, **não** consulta calendário, **não** produz `E09`
ou `E18`, **não** decide *handoff*, **não** decide ação e **não** chama a
`MaquinaEstados`. Ela **projeta** quatro campos a partir do que já foi
decidido a montante.

**Ela também não é um segundo `ValidadorConsistenciaBase`.** O
`ResultadoConsistencia` chega **já produzido**, e a conferência integral do
domínio, do índice, do status canônico, de **`VCB-7`** e de **`VCB-10`**
permanece na fronteira de origem e em S2-D8. Aqui só se confere o que a
**própria superfície** exige e o que é **necessário para uma projeção
unívoca** — nada além disso.

**Autoridade de cada campo.** `status` vem de `status_por_fragmento`, pelo par
do token, que precisa existir **exatamente uma vez**. `divergente` vem de
`tokens_divergentes`, sem reavaliar `ASSERTIVA` e sem reabrir **Classe II**.
`referentes_indisponiveis` vem de `referentes_indisponiveis`, filtrado pelo
token, projetando **somente** o `referente`, na **ordem física recebida** e
**sem deduplicação**. `assertivas_runtime` é **transportado literalmente** —
ordem, duplicatas, predicado e `bool` exato preservados.

**Runtime é fotografia recebida, nunca consulta** (**`D8P-10`**). Nenhuma
`ASSERTIVA` é resolvida ou avaliada aqui: resolver o valor do fato continua
sendo de **S2-D8**, e avaliá-lo continua sendo de `avaliar_emissibilidade`.

**Dois consumidores autorizados**, e nenhum outro por analogia: **S2-D8**
(§4.4.3), que fotografa cada alternativa candidata antes da etapa 7; e o
**futuro `OrquestradorMotor`**, na rota *action-owner* de **T16**/`R06`
(§4.1.5, **`PE-15`**–**`PE-20`**). **A segunda invocação não existe ainda**:
materializar esta primitiva **não** integra o ciclo, **não** implementa o
`OrquestradorMotor` e **não** conclui **T16** *end-to-end*.

**Pureza.** **Zero I/O**, ***filesystem***, rede, LLM, SDK, YAML,
`knowledge/**`, relógio, calendário, ambiente, *logging*, *cache*, *retry*,
fila, *sleep* e mutação de entrada.

**Sem exceção pública nova.** Forma inválida levanta `TypeError`; fotografia
não projetável univocamente levanta `ValueError`. A mensagem é
`<categoria>: <localizador>` e é **estrutural**: ela **nunca** carrega o token
recebido, o valor recebido, o `repr`, a cardinalidade, a posição, PII ou dado
comercial.
"""

from __future__ import annotations

from casa77_sdr.fragment_emissibility import FotografiaFragmento
from casa77_sdr.response_consistency import (
    ReferenteIndisponivel,
    ResultadoConsistencia,
)

__all__ = ["montar_fotografia_fragmento"]


# Categorias privadas e fechadas. Elas nomeiam o impedimento estrutural e
# **nao** sao vocabulario normativo novo: nenhum enum publico nasce delas.
_TIPO_INVALIDO = "tipo_invalido"
_STATUS_AUSENTE = "status_ausente"
_STATUS_AMBIGUO = "status_ambiguo"

# Localizadores estruturais fechados. Nomeiam a **posicao da chamada** ou o
# campo do resultado recebido, jamais o conteudo.
_TOKEN = "token"
_CONSISTENCIA = "consistencia"
_STATUS = "consistencia.status_por_fragmento"
_STATUS_ITEM = "consistencia.status_por_fragmento.item"
_INDISPONIVEIS_ITEM = "consistencia.referentes_indisponiveis.item"
_RUNTIME = "assertivas_runtime"
_RUNTIME_ITEM = "assertivas_runtime.item"
_RUNTIME_PREDICADO = "assertivas_runtime.item.predicado"
_RUNTIME_VALOR = "assertivas_runtime.item.valor"


def montar_fotografia_fragmento(
    token: object,
    consistencia: object,
    *,
    assertivas_runtime: object,
) -> FotografiaFragmento:
    """Projeta a `FotografiaFragmento` de **um** token já candidato.

    `token` é o identificador estrutural `<Rxx>/<Fxx>` de um fragmento; a
    **gramática** e a **identidade canônica** dele pertencem às autoridades já
    existentes e **não** são reconferidas aqui. `consistencia` é o
    `ResultadoConsistencia` **já produzido** pelo `ValidadorConsistenciaBase`.

    `assertivas_runtime` é ***keyword-only* e obrigatória, sem valor padrão**.
    Um `()` implícito faria um token com *binding* `RUNTIME_AUTORITATIVO`
    escapar **em silêncio** sem a sua fotografia factual; exigir o argumento
    obriga o chamador a declarar o que resolveu. Para **`R06`/`F1`** o chamador
    pode passar literalmente `()`, porque o *gate* de corpus já versionado de
    **`PE-11`** prova que ele **tem *bindings*** e **zero
    `RUNTIME_AUTORITATIVO`** — e **nenhum *gate* de corpus novo nasce aqui**.

    Levanta `TypeError` com `tipo_invalido` para forma inválida e `ValueError`
    com `status_ausente` ou `status_ambiguo` quando o token não tem
    **exatamente um** par de status. **Sem resultado parcial.**
    """
    if type(token) is not str:
        raise _tipo_invalido(_TOKEN)
    if type(consistencia) is not ResultadoConsistencia:
        raise _tipo_invalido(_CONSISTENCIA)

    runtime = _conferir_runtime(assertivas_runtime)
    status = _status_do_token(consistencia, token)

    return FotografiaFragmento(
        status=status,
        # `tokens_divergentes` ja e a projecao de **Classe II** pela primeira
        # ocorrencia. Nada e reavaliado: nem `ASSERTIVA`, nem `divergencias`.
        divergente=token in consistencia.tokens_divergentes,
        referentes_indisponiveis=_referentes_do_token(consistencia, token),
        # Transporte literal: ordem, duplicatas, predicado e `bool` exato.
        assertivas_runtime=runtime,
    )


def _conferir_runtime(assertivas_runtime: object) -> tuple[tuple[str, bool], ...]:
    """Confere a forma dos pares recebidos e os devolve **sem alteração**.

    **Nenhuma `ASSERTIVA` e avaliada aqui**, e **nenhum valor e resolvido**: a
    avaliacao continua em `avaliar_emissibilidade`, e a resolucao do fato
    continua em S2-D8. O `bool` e exigido **exato** porque `1`/`0` passariam
    por verdade booleana sem serem o fato resolvido.
    """
    if type(assertivas_runtime) is not tuple:
        raise _tipo_invalido(_RUNTIME)
    for par in assertivas_runtime:
        if type(par) is not tuple or len(par) != 2:
            raise _tipo_invalido(_RUNTIME_ITEM)
        predicado, valor = par
        if type(predicado) is not str:
            raise _tipo_invalido(_RUNTIME_PREDICADO)
        if type(valor) is not bool:
            raise _tipo_invalido(_RUNTIME_VALOR)
    return assertivas_runtime


def _status_do_token(consistencia: ResultadoConsistencia, token: str) -> str:
    """O rótulo de `C-3` do token, exigindo **exatamente uma** ocorrência.

    Zero ocorrência e mais de uma ocorrência **fecham**: nos dois casos a
    fotografia **não é projetável univocamente**, e inventar um padrão seria
    decidir status fora da autoridade que o produziu. **Zero *fallback*, zero
    valor padrão e zero consulta ao índice.**
    """
    if type(consistencia.status_por_fragmento) is not tuple:
        raise _tipo_invalido(_STATUS)

    encontrado: str | None = None
    for par in consistencia.status_por_fragmento:
        # Guarda minima: ler o par e **pre-requisito** da projecao unívoca. O
        # vocabulario canonico de status continua sendo julgado a montante.
        if type(par) is not tuple or len(par) != 2:
            raise _tipo_invalido(_STATUS_ITEM)
        if type(par[0]) is not str or type(par[1]) is not str:
            raise _tipo_invalido(_STATUS_ITEM)
        if par[0] != token:
            continue
        if encontrado is not None:
            raise ValueError(f"{_STATUS_AMBIGUO}: {_STATUS}")
        encontrado = par[1]

    if encontrado is None:
        raise ValueError(f"{_STATUS_AUSENTE}: {_STATUS}")
    return encontrado


def _referentes_do_token(
    consistencia: ResultadoConsistencia, token: str
) -> tuple[str, ...]:
    """Os caminhos de **`C-7`** do token, na **ordem física recebida**.

    **Zero deduplicação**: reduzir perderia causa estrutural, porque **D8-E4**
    manda avaliar **todas** as causas da lacuna e cada `ReferenteIndisponivel`
    carrega o seu próprio caminho. Só o `referente` atravessa — `mecanismo`,
    `binding`, `origem`, `rxx` e `fragmento_id` **ficam fora da fotografia**.
    """
    referentes: list[str] = []
    for item in consistencia.referentes_indisponiveis:
        if type(item) is not ReferenteIndisponivel:
            raise _tipo_invalido(_INDISPONIVEIS_ITEM)
        if item.token != token:
            continue
        referentes.append(item.referente)
    return tuple(referentes)


def _tipo_invalido(localizador: str) -> TypeError:
    return TypeError(f"{_TIPO_INVALIDO}: {localizador}")
