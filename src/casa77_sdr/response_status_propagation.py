"""Propagação pura e determinística de status `ST1`–`ST3` aos fragmentos associados.

`SP1`–`SP7` fecharam a **propagação** de status. `SP1` fixa o escopo: a regra
opera **conceitualmente** sobre **um `Rxx`**, **os seus fragmentos emitíveis
declarados** e **um rótulo de status já corretamente identificado e associado
àquele `Rxx`**. `SP2` manda aplicar o status canônico **uniformemente a todos**
esses fragmentos quando o rótulo for exatamente uma das três traduções
automáticas de `C-A1-ST1`–`C-A1-ST3`. `SP3` proíbe qualquer exceção por posição,
ordem, índice, redação, conteúdo, quantidade ou `id`. Este módulo materializa
**essas regras, e nada mais**.

**A associação já chegou pronta.** A função **não** analisa Markdown, **não**
localiza `Rxx`, **não** localiza cabeçalho, **não** localiza marcador, **não**
resolve contenção física e **não** decide de onde o rótulo veio nem a que `Rxx`
cada fragmento pertence. **A associação correta entre o rótulo e os fragmentos é
pré-condição do chamador** e não é verificável nesta fronteira sem transformá-la
em extrator ou em compositor — que ela deliberadamente não é. Um retorno
bem-sucedido **não** prova a origem do rótulo, a existência do `Rxx`, o
pertencimento dos fragmentos, a completude do conjunto, a proveniência, a
contenção física ou a validade da identidade.

**Os fragmentos são tokens opacos.** Cada elemento é uma `str` e **nada além
disso**: o módulo **não** interpreta a identidade canônica, **não** interpreta o
separador, **não** lê `Rxx`, **não** lê `id`, **não** lê prefixo, sufixo,
gramática, posição ou conteúdo, e **não compõe nem decompõe token algum**.
Também **não** valida `C-A5`, unicidade, cobertura ou cardinalidade — nada disso
pertence a esta fronteira.

**O rótulo é julgado primeiro, e por quem já o julga.** A **primeira** operação
funcional é `canonicalizar_status(rotulo)` (`response_status`), **sem
alteração**: a tradução continua sendo exatamente a já materializada lá, e
**nenhuma quarta tradução é criada** — o vocabulário de `C-3` permanece fechado e
não existe tabela local aqui. Nenhuma validação de `fragmentos` a precede; por
consequência, com rótulo **e** fragmentos inválidos, **o rótulo falha primeiro**.
Isso é **decisão técnica local de determinismo**, e **não** norma nova de `C`.

**`StatusNaoCanonicalizavel` propaga intacta** — **sem `try`/`except`, sem
wrapper, sem reclassificação, sem enriquecimento de mensagem, sem `raise from`,
sem alterar `__cause__` ou `__context__`**.

**`PARCIAL` continua NÃO RESOLVIDO.** `C-A1-ST4` e `SP4` mantêm-no
**integralmente** fora da tradução automática, e por isso `canonicalizar_status`
o recusa. Este módulo **não** captura essa recusa, **não** traduz, **não**
propaga, **não** mapeia, **não** converte e **não** cria quarto status. A recusa
é falha **daquela invocação**, e nada mais: esta fronteira **não conhece
documento algum** e, portanto, **não afirma** que `PARCIAL` invalide globalmente
um documento.

**Uniformidade é o coração de `SP3`.** Todos os elementos de uma mesma chamada
recebem **o mesmo** status canônico. A sequência recebida determina **apenas**
quais tokens aparecem e em que ordem são devolvidos — **jamais** o status. Isso
preserva literalmente `C-A5-I5` (identidade declarada, nunca derivada de posição,
ordem, índice, redação ou conteúdo) e `C-A5-M6` (posição e ordem são apenas
localizador de evidência apresentado ao responsável humano).

**Sem lógica de homônimo.** Não há agrupamento por `Rxx`, deduplicação, `dict`,
`zip`, pareamento por posição ou lógica de instância física. Tokens repetidos são
**aceitos e preservados**, nunca deduplicados e nunca tratados como erro: esta
fronteira **não julga unicidade de identidade**. A composição documental que
decidirá isso é **outra entrega**.

**Pureza.** Fora `Sequence` e `canonicalizar_status`, o módulo não importa nada:
**zero I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero
Markdown**, **zero YAML**, **zero índice**, **zero corpus**, **zero rede**,
**zero LLM**, **zero relógio**, **zero calendário**, **zero *locale***, **zero
variável de ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero
estado mutável de módulo**, **zero `global`**, **zero `nonlocal`**, **zero
normalização**, **zero coerção**. A entrada **não é alterada**.

**PROPAGAR STATUS NÃO É MATERIALIZAR `C`.** Conforme `SP6` e `SP7`, o status
devolvido é **DERIVADO** da autoridade Markdown vigente: ele **não** cria
declaração de status no Markdown (`C-2d`), **não** altera o Markdown, **não**
cria índice, **não** cria fragmento, **não** altera identidade, **não** extrai
rótulo, **não** resolve `PARCIAL`, **não** executa a bijeção física, **não**
satisfaz `C-A1-ST6`–`C-A1-ST10` e **não** migra a autoridade de status — a
autoridade de status **continua onde está** (`C-11`). `C` continua **ARBITRADA /
NÃO MATERIALIZADA**.
"""

from __future__ import annotations

from collections.abc import Sequence

from casa77_sdr.response_status import canonicalizar_status

__all__ = ["PropagacaoInvalida", "propagar_status"]


class PropagacaoInvalida(Exception):
    """A forma do contêiner de fragmentos, ou de um dos seus elementos, é inválida.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** impede a propagação e o localizador diz **onde** — nunca o token
    recebido, o rótulo, o conteúdo, o `repr`, o tipo concreto, um índice, uma
    posição, um comprimento ou uma cardinalidade.

    Levantá-la significa **apenas** que os fragmentos recebidos não têm a forma
    exigida por esta fronteira. **Não** significa que o rótulo seja inválido —
    esse julgamento é anterior e pertence a `StatusNaoCanonicalizavel` —, nem
    afirma coisa alguma sobre `Rxx`, pertencimento, unicidade ou cobertura.
    """


# Categoria tecnica privada e fechada. Ela nomeia o impedimento e **nao** e
# identificador normativo novo de `C`. E a unica: nenhuma segunda categoria
# existe nesta fronteira.
_TIPO_INVALIDO = "tipo_invalido"

# Localizadores fechados: o contentor de topo e o elemento dele. O rotulo nao
# figura aqui porque ele nunca falha por esta excecao.
_FRAGMENTOS = "fragmentos"
_FRAGMENTOS_ITEM = "fragmentos.item"


def propagar_status(
    rotulo: str,
    fragmentos: Sequence[str],
) -> tuple[tuple[str, str], ...]:
    """Aplica o status canônico de `rotulo` a **todos** os `fragmentos` recebidos.

    Devolve um par `(fragmento_opaco, status_canonico)` por elemento de
    `fragmentos`, **na ordem da entrada**, **preservando duplicidades** e **sem
    deduplicar**. A saída é uma `tuple` de pares — nunca um `dict`, nunca uma
    tupla paralela de status.

    A ordem de execução é **fixa**: **1.** `canonicalizar_status(rotulo)`;
    **2.** tipo do contêiner `fragmentos`; **3.** materialização única da
    sequência; **4.** tipo de **todos** os elementos; **5.** montagem dos pares;
    **6.** retorno. A validação dos elementos percorre **toda** a entrada antes
    da montagem, e **nada é devolvido parcialmente**.

    `rotulo` é **um rótulo de status já corretamente identificado**, e
    `fragmentos` são **tokens já associados pelo chamador ao mesmo `Rxx` daquele
    rótulo**. Essa associação é **pré-condição do chamador** (`SP1`): nada aqui a
    verifica, e o sucesso **não** a prova.

    A **primeira** operação funcional é `canonicalizar_status(rotulo)`, e
    **nenhuma** validação de `fragmentos` a precede. Com rótulo e fragmentos
    ambos inválidos, portanto, **o rótulo falha primeiro** —
    `StatusNaoCanonicalizavel` sobe **intacta**, com classe, mensagem,
    `__cause__` e `__context__` inalterados. Isso inclui `PARCIAL`, que
    permanece **NÃO RESOLVIDO** (`C-A1-ST4`, `SP4`) e cuja recusa é falha
    **daquela invocação**, jamais um veredito sobre um documento inteiro.

    `fragmentos` precisa ser uma `Sequence`; `str`, `bytes` e `bytearray` são
    **recusados como contêiner**, porque os seus elementos são caracteres e
    octetos, nunca tokens. Cada elemento precisa ser do tipo `str`
    **exatamente** — subclasse de `str` é recusada, porque poderia redefinir
    `__eq__` e `__hash__` e decidir por conta própria a sua própria identidade.
    Ambas as violações produzem a **mesma e única** categoria `tipo_invalido`,
    distinguidas apenas pelo localizador.

    Uma sequência **vazia** com rótulo válido devolve `tuple()`. Isso afirma
    **somente** que nada foi recebido — **não** que um `Rxx` real possa não ter
    fragmentos.

    Todos os elementos recebem **o mesmo** status (`SP3`): ele **não** depende de
    posição, ordem, índice, conteúdo, token, `id`, quantidade ou redação. Os
    tokens são **opacos** — a `str` vazia e qualquer outra `str` são aceitas sem
    que a sua forma seja interpretada.

    **PROPAGAR STATUS NÃO É MATERIALIZAR `C`** (`SP7`): nada aqui cria índice,
    cria fragmento, altera identidade, extrai rótulo, resolve `PARCIAL`, executa
    a bijeção física, satisfaz `C-A1-ST6`–`C-A1-ST10` ou migra a autoridade de
    status.
    """
    status = canonicalizar_status(rotulo)

    if not _e_contentor(fragmentos):
        raise _invalida(_FRAGMENTOS)

    tokens = tuple(fragmentos)

    for token in tokens:
        if type(token) is not str:
            raise _invalida(_FRAGMENTOS_ITEM)

    return tuple((token, status) for token in tokens)


def _e_contentor(valor: object) -> bool:
    """Diz se `valor` é uma sequência capaz de conter tokens.

    Uma `str`, um `bytes` e um `bytearray` são sequências, mas os seus elementos
    são caracteres e octetos — nunca tokens. Por isso são recusados como
    contêiner. `isinstance` sobrevive **apenas** para decidir isso; o token
    individual é conferido por **tipo exato**, e não por `isinstance`.
    """
    if isinstance(valor, (str, bytes, bytearray)):
        return False
    return isinstance(valor, Sequence)


def _invalida(localizador: str) -> PropagacaoInvalida:
    return PropagacaoInvalida(f"{_TIPO_INVALIDO}: {localizador}")
