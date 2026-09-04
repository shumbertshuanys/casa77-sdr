"""Composição determinística da correspondência canônica, em memória.

`C-A1-B3` exige que **cada fragmento do índice** corresponda a **exatamente uma**
unidade emitível do Markdown, e `C-A1-B4` exige a recíproca. `C-A5-T4` fixa que
a identidade canônica `<Rxx>/<id>` (`C-A5-T1`, com o separador `/` de
`C-A5-T2`) **será o token dos dois domínios físicos** dessas duas regras. Este
módulo **compõe** as três fronteiras que já existem para julgar essa relação
sobre **dois insumos recebidos**: ele deriva o domínio do lado do índice, lê o
domínio do lado do Markdown, monta a relação canônica e delega o julgamento.

**Nada de juiz novo.** O módulo **não** cria fronteira, contrato, exceção,
categoria, identidade, gramática ou regra alguma. Ele chama, nesta ordem fixa,
`derivar_tokens_do_indice` (o derivador do lado do índice),
`ler_unidades_marcadas` (o leitor da representação marcada) e `validar_bijecao`
(o verificador da correspondência bijetiva). Toda a validação **já pertence** a
essas fronteiras e **não é duplicada aqui**: este módulo **não** confere tipo de
entrada, estrutura, forma de token, duplicidade, cobertura ou cardinalidade.

**A relação é a diagonal da identidade, nunca a posição.** Para cada token do
domínio do índice é montado o par `(token, token)`. A correspondência é, por
construção, **igualdade da identidade canônica** — e isso é o que `C-A5-T4`
autoriza, porque `C-A5-T3` garante que a composição é injetiva e a decomposição
unívoca, ambas as gramáticas sendo fechadas e sem `/`. **Nada é pareado por
posição, ordem ou `zip`**, nada é normalizado, convertido ou interpretado
internamente: isso violaria `C-A5-I5`, que proíbe identidade derivada de
posição, ordem, índice, redação ou conteúdo. A relação é **efêmera**: ela não é
devolvida, não é armazenada e não é persistida (`C-A5-T5`).

**As exceções propagam intactas.** `ProjecaoDeIdentidadeInvalida` do lado do
índice, `RepresentacaoMarcadaInvalida` do lado do Markdown e `BijecaoInvalida`
do julgamento sobem **exatamente como foram levantadas** — **sem `try`/`except`,
sem reclassificação, sem enriquecimento de mensagem, sem alterar `__cause__` ou
`__context__`**. Com **ambos** os insumos inválidos, a ordem fixa faz o lado do
índice falhar primeiro; isso é **decisão técnica local de determinismo**, e
**não** norma nova de `C`.

**Pureza.** Fora as três fronteiras públicas, o módulo não importa nada: **zero
I/O**, **zero *filesystem***, **zero `open`**, **zero `pathlib`**, **zero
YAML**, **zero rede**, **zero LLM**, **zero relógio**, **zero calendário**,
**zero *locale***, **zero variável de ambiente**, **zero banco**, **zero
cache**, **zero estado mutável de módulo**. Os insumos **não são alterados**.

**COMPOR E VALIDAR EM MEMÓRIA NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É
MATERIALIZAR `C`.** Um retorno bem-sucedido afirma **somente** que os **dois
insumos fornecidos** produziram domínios de identidade cuja relação canônica é
**bijetiva entre eles**. Ele **não** afirma que `indice` seja o índice oficial,
que `texto_markdown` seja o corpus oficial, que o índice físico exista — ele
**continua INEXISTENTE** —, que o corpus esteja completo ou aprovado, que o
índice seja **integralmente válido** (isso é de `validar_indice`, que este
módulo **não** chama e **não** substitui), que a **bijeção física 37/37** do
corpus real tenha sido executada, que `C-A1-ST6`–`C-A1-ST10` estejam satisfeitas
ou que a autoridade de status tenha migrado. **A proveniência correta dos dois
insumos é pré-condição do chamador** e não é verificável nesta fronteira sem
transformá-la em carregador — que ela deliberadamente não é. `C` continua
**ARBITRADA / NÃO MATERIALIZADA**.
"""

from __future__ import annotations

from casa77_sdr.response_bijection import validar_bijecao
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice
from casa77_sdr.response_markdown_units import ler_unidades_marcadas

__all__ = ["validar_correspondencia_canonica"]


def validar_correspondencia_canonica(
    indice: object,
    texto_markdown: str,
) -> None:
    """Julga se `indice` e `texto_markdown` denotam as **mesmas** identidades.

    Devolve `None` quando os dois insumos produzem domínios de identidades
    canônicas `<Rxx>/<id>` cuja relação diagonal é **bijetiva entre eles**:
    todo token do índice tem par no Markdown, todo token do Markdown tem par no
    índice, e nenhum se repete de nenhum dos lados.

    A ordem é **fixa**: **1.** o domínio do índice, por
    `derivar_tokens_do_indice(indice)`; **2.** o domínio do Markdown, por
    `ler_unidades_marcadas(texto_markdown)`; **3.** a relação canônica
    `(token, token)`, um par por token do domínio do índice, **na ordem em que
    ele os devolveu**; **4.** o julgamento, por `validar_bijecao`, chamado
    **uma única vez**.

    A relação é montada **exclusivamente por identidade** — o par de um token é
    ele mesmo. **Nada é pareado por posição, ordem ou `zip`** (`C-A5-I5`), e o
    token **não é lido, normalizado nem convertido** em momento algum: a
    igualdade que decide é a **nativa e exata de `str`**, dentro de
    `validar_bijecao`. A relação **não é devolvida, armazenada ou persistida**
    (`C-A5-T5`).

    **Nenhuma validação é feita aqui.** Tipo dos insumos, estrutura do índice,
    estrutura do Markdown, forma do token, duplicidade, cobertura e cardinalidade
    **já pertencem** às três fronteiras chamadas, e as suas exceções propagam
    **intactas**: `ProjecaoDeIdentidadeInvalida`, `RepresentacaoMarcadaInvalida`
    e `BijecaoInvalida`. **Nenhuma exceção nova é criada** e **nada é capturado
    ou relançado**. Com ambos os insumos inválidos, o lado do índice falha
    primeiro, por causa da ordem fixa.

    **Dois domínios vazios são uma bijeção trivial válida** e devolvem `None` —
    o que afirma **apenas** isso, e nada sobre o corpus ou o índice reais.

    **COMPOR E VALIDAR EM MEMÓRIA NÃO É EXECUTAR A BIJEÇÃO FÍSICA E NÃO É
    MATERIALIZAR `C`.** O sucesso afirma **somente** a bijetividade entre os
    domínios dos **dois insumos fornecidos** — nada sobre a origem deles, sobre
    a existência do índice físico (que **continua INEXISTENTE**), sobre a
    completude ou a aprovação do corpus, sobre a validade integral do índice por
    `validar_indice`, sobre a execução da bijeção física 37/37, sobre
    `C-A1-ST6`–`C-A1-ST10` ou sobre a migração da autoridade de status.
    """
    dominio_indice = derivar_tokens_do_indice(indice)
    dominio_markdown = ler_unidades_marcadas(texto_markdown)

    # A correspondencia e a **diagonal da identidade** (`C-A5-T4`): o par de um
    # token e ele mesmo. Nunca posicao, nunca ordem, nunca `zip` (`C-A5-I5`).
    correspondencias = tuple((token, token) for token in dominio_indice)

    validar_bijecao(dominio_indice, dominio_markdown, correspondencias)
