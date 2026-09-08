"""Resolver factual de `caminho_yaml` — linha 3 de `CY13`.

`CY13` separou **três** responsabilidades: o **parser da gramática**, a
**validação estrutural do índice** e o **resolver**. As linhas 1 e 2 já estão
materializadas em `casa77_sdr.response_yaml_path` e
`casa77_sdr.response_yaml_path_context`. Este módulo materializa **exatamente a
terceira, e nada mais**.

**Ele é a primeira das três fronteiras que toca a estrutura factual.** E é
justamente por isso que o seu perímetro é o mais estreito: a estrutura chega
**já carregada em memória**, por argumento, e o módulo **não abre arquivo**,
**não importa `yaml`**, **não conhece o caminho de `knowledge/casa77.yaml`**,
**não descobre artefato**, **não faz I/O** e **não lê o índice**. Quem carregou
a estrutura, e se ela é o corpus oficial, é **pré-condição do chamador**.

**A gramática não pertence a esta fronteira.** O resolver recebe a
**decomposição já produzida** — `(relativo, segmentos)` — e **jamais** a
rejulga: **não** importa `analisar_caminho_yaml`, **não** procura `@`, **não**
valida alfabeto, *whitespace*, canonicalidade ou chave exclusivamente numérica,
**não** reconstrói o caminho e **não** concatena segmentos. Uma decomposição
**tecnicamente bem formada** cujas `str` seriam gramaticalmente absurdas **não é
recusada como erro gramatical**: ela é simplesmente usada **estruturalmente**
contra a raiz recebida, e falhará — se falhar — por ausência de chave ou por
tipo incompatível, nunca por gramática.

**O que ele valida é a FORMA TÉCNICA, com tipo exato.** `type(x) is dict` e
`type(x) is list` para a estrutura YAML; `tuple`, `bool` e `str` exatos para os
componentes da decomposição. **Subclasse não é aceita** como estrutura canônica
desta fronteira, porque uma subclasse pode redefinir `__contains__`,
`__getitem__`, `__eq__` ou `__iter__` e decidir por conta própria o que a
estrutura diz. **Zero coerção**, **zero `str(...)`**, **zero conversão**.

**A forma é exigida em DOIS momentos distintos, e isso é normativo.** Primeiro o
**envelope externo** da decomposição — o par `(relativo, segmentos)`, com
`relativo` `bool` exato e `segmentos` `tuple` exata, mais a recusa de
`(False, ())`. Depois, e **somente quando o segmento é alcançado**, a **forma
daquele segmento**. A decomposição **não** é varrida por inteiro de antemão:
fazê-lo permitiria que um segmento malformado **futuro** mascarasse uma falha
que o precede — a **ausência do item corrente**, a recusa de **caminho relativo
em `itera_sobre`**, uma **chave inexistente** ou uma **travessia em nulo**
anteriores. **A primeira violação em ordem de percurso encerra**, e o que vem
depois dela **não é sequer inspecionado**. Já a forma do segmento **corrente**
vence o estado estrutural **do mesmo passo**.

**Ausência não é `None`.** `None` é **valor factual legítimo** do YAML e
**nunca** significa "não fornecido". Por isso a ausência do item corrente é
marcada pela sentinela privada `_AUSENTE`, e **nunca** por `None`. Um
`item_corrente=None` explícito é um item corrente **presente cujo valor é
nulo** — e `@` isolado sobre ele devolve `None` com **SUCESSO**.

**`(False, ())` é tecnicamente inválida.** O parser **jamais** produz caminho
absoluto sem segmento algum: absoluto sem segmento não tem referente. A
decomposição é recusada como `tipo_invalido: decomposicao`. Já **`(True, ())` é
válida** e é exatamente o `@` isolado de `CY11` — o **próprio item corrente**,
devolvido **por identidade**, seja ele `dict`, `list`, `str`, número, `bool` ou
`None`.

**O SELETOR É OPERADOR DE CONFORMIDADE, NÃO DE BUSCA TOLERANTE.** Antes de
decidir **zero / um / múltiplos *matches***, a **coleção inteira** precisa estar
estruturalmente conforme: cada item `dict` exato, com a chave seletora
**presente** e com valor `str` **exato**. A conformidade da coleção **precede a
cardinalidade** — de modo que um item malformado **vence** mesmo quando um
*match* anterior já ocorreu, e mesmo quando dois já ocorreram. A comparação é
**literal, por `str`, sem coerção**: um literal `"2026"` casa com a `str`
`"2026"` e **não** com o inteiro `2026`.

**Terminal é devolvido como está.** Alcançado o nó terminal, a resolução é
**SUCESSO** e o valor volta **pelo próprio objeto**, sem cópia, sem
normalização e sem juízo adicional de tipo. **Terminal `None` é SUCESSO** — a
admissibilidade posterior pertence a `C-5`, `C-6` e `C-7`, e **`C-7` NÃO é
aplicada, reaberta nem materializada aqui**. Atravessar `None` **no meio** do
percurso, ao contrário, é falha estrutural.

**Taxonomia fechada.** Existem **exatamente nove** categorias —
`tipo_invalido`, `item_corrente_ausente`, `relativo_em_itera_sobre`,
`segmento_inexistente`, `tipo_incompativel`, `travessia_em_nulo`,
`zero_matches`, `multiplos_matches` e `itera_sobre_nao_colecao` — e **exatamente
seis** localizadores — `raiz`, `decomposicao`, `item_corrente`, `segmento`,
`seletor` e `itera_sobre`. A mensagem tem a forma `<categoria>: <localizador>`.

**A mensagem NUNCA vaza.** Como este módulo toca dado factual real, a exceção
**não** carrega o valor recebido, o valor factual, a chave concreta, o literal,
o caminho, um fragmento dele, uma posição, um índice, um *offset*, uma
cardinalidade observada, um comprimento, o `repr` ou o tipo concreto. Isso vale
nas **nove** categorias, sem exceção.

**Pureza.** O módulo importa **apenas** `annotations`: **zero `yaml`**, **zero
JSON**, **zero `re`**, **zero `unicodedata`**, **zero `pathlib`**, **zero
`os`**, **zero `open`**, **zero I/O**, **zero *filesystem***, **zero rede**,
**zero LLM**, **zero relógio**, **zero calendário**, **zero aleatoriedade**,
**zero variável de ambiente**, **zero banco**, **zero cache**, **zero
logging**, **zero `try`/`except`**, **zero `raise from`**, **zero
`eval`/`exec`**, **zero `assert`**, **zero `global`/`nonlocal`**, **zero estado
mutável de módulo**, **zero normalização** e **zero coerção**. A **raiz não é
mutada**, o **item corrente não é mutado**, e **nada é copiado em
profundidade**.

**RESOLVER NÃO É MATERIALIZAR `C`.** Um retorno bem-sucedido afirma **somente**
que a decomposição recebida percorre a estrutura recebida e alcança um valor.
Ele **não** diz que a estrutura é o corpus oficial; **não** conhece `Rxx`,
fragmento emitível, *binding* físico, *placeholder*, formato ou `ASSERTIVA`;
**não** formata valor; **não** aplica `C-7`; e **não** integra coisa alguma a
`E1` — `src/casa77_sdr/response_index.py` **não consome** esta fronteira e
**continua INALTERADO**. `knowledge/indice-respostas-aprovadas.yaml` continua
**INEXISTENTE**, a autoridade de status continua no Markdown aprovado (`C-11`) e
**`C` continua ARBITRADA / NÃO MATERIALIZADA**.
"""

from __future__ import annotations

__all__ = [
    "CaminhoYamlNaoResolvido",
    "resolver_caminho",
    "resolver_itera_sobre",
]


class CaminhoYamlNaoResolvido(Exception):
    """A decomposição recebida não resolve contra a estrutura recebida.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** impediu a resolução e o localizador diz **em que construção** — nunca
    o valor recebido, o valor factual, a chave concreta, o literal, o caminho,
    um fragmento dele, uma posição, um índice, um *offset*, uma cardinalidade
    observada, um comprimento, o `repr` ou o tipo concreto.

    Ela é **irmã**, e não parente, de `CaminhoYamlInvalido` e de
    `CaminhoYamlContextoInvalido`: a primeira recusa a `str` como caminho, a
    segunda recusa um caminho legítimo **no lugar errado**, e esta afirma que um
    caminho legítimo, bem posicionado, **não alcança valor** nesta estrutura.
    Levantá-la **não** afirma coisa alguma sobre `C-7`, sobre o índice físico,
    sobre `Rxx`, sobre *binding* ou sobre a oficialidade do corpus.
    """


# Sentinela privada de ausência. Ela existe porque `None` é **valor factual
# legítimo** do YAML: usar `None` como "não fornecido" tornaria indistinguíveis
# um item corrente nulo e um item corrente ausente. Nunca entra em `__all__`.
_AUSENTE = object()

# Categorias tecnicas privadas e fechadas. Elas nomeiam o impedimento e **nao**
# sao identificadores normativos novos de `C`. Sao exatamente nove.
_TIPO_INVALIDO = "tipo_invalido"
_ITEM_CORRENTE_AUSENTE = "item_corrente_ausente"
_RELATIVO_EM_ITERA_SOBRE = "relativo_em_itera_sobre"
_SEGMENTO_INEXISTENTE = "segmento_inexistente"
_TIPO_INCOMPATIVEL = "tipo_incompativel"
_TRAVESSIA_EM_NULO = "travessia_em_nulo"
_ZERO_MATCHES = "zero_matches"
_MULTIPLOS_MATCHES = "multiplos_matches"
_ITERA_SOBRE_NAO_COLECAO = "itera_sobre_nao_colecao"

# Localizadores semanticos fechados. Eles nomeiam **a especie de construcao**
# onde o impedimento esta, jamais a sua posicao ou o seu conteudo.
_RAIZ = "raiz"
_DECOMPOSICAO = "decomposicao"
_ITEM_CORRENTE = "item_corrente"
_SEGMENTO = "segmento"
_SELETOR = "seletor"
_ITERA_SOBRE = "itera_sobre"

# Alias privado da anotacao da decomposicao, para nao repetir a forma inteira em
# cada assinatura. Nao e publico e nao e DTO, dataclass, Enum ou tipo novo.
_Decomposicao = tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]


def resolver_caminho(
    raiz: object,
    decomposicao: _Decomposicao,
    *,
    item_corrente: object = _AUSENTE,
) -> object:
    """Resolve `decomposicao` contra `raiz` e devolve o valor terminal.

    `raiz` é o **mapeamento raiz do YAML já carregado em memória** — `dict`
    **exato**. `decomposicao` é o par `(relativo, segmentos)` **já produzido**
    pelo parser da gramática; ele **não é rejulgado gramaticalmente aqui**.
    `item_corrente` é **keyword-only** e só é exigido quando a decomposição é
    **relativa**; para caminho absoluto ele é **ignorado**, mesmo se fornecido.

    A ordem de validação é **fixa**: **1.** tipo da raiz; **2.** envelope
    externo da decomposição; **3.** recusa de `(False, ())`; **4.** presença do
    item corrente quando relativo; **5.** percurso da esquerda para a direita,
    exigindo a forma de **cada segmento apenas quando ele é alcançado**. Por
    isso `(True, ("nao_e_segmento",))` **sem** item corrente falha como
    `item_corrente_ausente`, e não como `tipo_invalido`: o segmento malformado
    nunca chega a ser inspecionado.

    Com `relativo` `True` e `segmentos` vazios — o **`@` isolado** de `CY11` —
    devolve o **próprio `item_corrente`**, **por identidade**, seja ele `dict`,
    `list`, `str`, número, `bool` ou `None`, **sem juízo terminal adicional**.

    O valor terminal volta **como está**, pelo próprio objeto. **Terminal
    `None` é SUCESSO**; atravessar `None` **no meio** do percurso é falha.

    Levanta `CaminhoYamlNaoResolvido` com as categorias `tipo_invalido`
    (`raiz`, `decomposicao`), `item_corrente_ausente` (`item_corrente`),
    `travessia_em_nulo`, `tipo_incompativel`, `segmento_inexistente`,
    `zero_matches` e `multiplos_matches` (`segmento` ou `seletor`).

    **RESOLVER NÃO É MATERIALIZAR `C`.** O sucesso afirma **somente** que o
    percurso alcançou um valor nesta estrutura — nada sobre oficialidade do
    corpus, `Rxx`, *binding*, formato, `ASSERTIVA`, *placeholder* ou `C-7`.
    """
    if type(raiz) is not dict:
        raise _nao_resolvido(_TIPO_INVALIDO, _RAIZ)

    relativo, segmentos = _exigir_envelope(decomposicao)

    if relativo is False:
        base = raiz
    else:
        if item_corrente is _AUSENTE:
            raise _nao_resolvido(_ITEM_CORRENTE_AUSENTE, _ITEM_CORRENTE)
        base = item_corrente

    return _percorrer(base, segmentos)


def resolver_itera_sobre(
    raiz: object,
    decomposicao: _Decomposicao,
) -> list:
    """Resolve `decomposicao` como o `itera_sobre` de um fragmento.

    `CY12` é literal: `itera_sobre` usa a **forma ABSOLUTA** e precisa
    **resolver para uma coleção**. Uma decomposição **relativa** é recusada aqui
    como `relativo_em_itera_sobre` — o que **duplica em nada** a linha 2 de
    `CY13`: aquela fronteira julga a `str` **antes** de qualquer estrutura, esta
    recusa a decomposição **na porta do resolver**, e as duas exceções são
    **independentes**. Por isso esta função **não** recebe contexto algum.

    A ordem é **fixa**: **1.** tipo da raiz; **2.** envelope externo da
    decomposição; **3.** recusa de `(False, ())`; **4.** recusa da forma
    relativa; **5.** percurso. Por isso `(True, ("nao_e_segmento",))` falha como
    `relativo_em_itera_sobre`, e não como `tipo_invalido`: a forma daquele
    segmento nunca chega a ser exigida.

    O percurso usa **exatamente** as mesmas regras estruturais e de seletor de
    `resolver_caminho`. No terminal, **`list` exata é o único tipo aceito**:
    mapa, escalar, `None`, `tuple` e `set` são ***FAIL-CLOSED* estrutural**, via
    `itera_sobre_nao_colecao`. **Isto não é `C-7`.**

    Devolve **a mesma lista**, pelo próprio objeto — **sem copiar, sem ordenar,
    sem filtrar e sem materializar iterador**. **Lista vazia é SUCESSO**: o
    comportamento operacional da iteração sobre coleção vazia **não é decidido
    aqui**.

    Levanta `CaminhoYamlNaoResolvido` com `tipo_invalido` (`raiz`,
    `decomposicao`), `relativo_em_itera_sobre` (`decomposicao`),
    `itera_sobre_nao_colecao` (`itera_sobre`) e as mesmas categorias de percurso
    e de seletor de `resolver_caminho`.
    """
    if type(raiz) is not dict:
        raise _nao_resolvido(_TIPO_INVALIDO, _RAIZ)

    relativo, segmentos = _exigir_envelope(decomposicao)

    if relativo is True:
        raise _nao_resolvido(_RELATIVO_EM_ITERA_SOBRE, _DECOMPOSICAO)

    terminal = _percorrer(raiz, segmentos)

    if type(terminal) is not list:
        raise _nao_resolvido(_ITERA_SOBRE_NAO_COLECAO, _ITERA_SOBRE)

    return terminal


def _exigir_envelope(decomposicao: object) -> tuple[bool, tuple]:
    """Exige **somente o envelope externo** da decomposição.

    Julga o par `(relativo, segmentos)` — `tuple` de dois, `relativo` `bool`
    exato, `segmentos` `tuple` exata — e a recusa de `(False, ())`. **A forma
    individual dos segmentos NÃO é julgada aqui**: ela pertence a
    `_exigir_segmento`, e só é exigida **quando aquele segmento é alcançado**.

    A separação é normativa desta fronteira. Validar todos os segmentos de
    antemão faria um segmento malformado **futuro** mascarar uma falha que
    precede o percurso — a ausência do item corrente, a recusa de caminho
    relativo em `itera_sobre` — ou uma falha estrutural **anterior** a ele, como
    chave inexistente ou travessia em nulo. **A primeira violação em ordem de
    percurso encerra**, e o que vem depois **não é sequer inspecionado**.
    """
    if type(decomposicao) is not tuple or len(decomposicao) != 2:
        raise _nao_resolvido(_TIPO_INVALIDO, _DECOMPOSICAO)

    relativo, segmentos = decomposicao

    if type(relativo) is not bool or type(segmentos) is not tuple:
        raise _nao_resolvido(_TIPO_INVALIDO, _DECOMPOSICAO)

    if relativo is False and not segmentos:
        raise _nao_resolvido(_TIPO_INVALIDO, _DECOMPOSICAO)

    return relativo, segmentos


def _exigir_segmento(segmento: object) -> tuple[str, tuple[str, str] | None]:
    """Exige a **forma técnica de um único segmento**, com tipo exato.

    Julga **somente** a forma — `tuple` de dois, chave `str` exata, seletor
    `None` ou `tuple` de duas `str` exatas —, **nunca** o conteúdo gramatical
    das `str`. É chamada **no início da iteração daquele segmento**, de modo que
    a forma do segmento **corrente** vence o estado estrutural do mesmo passo,
    enquanto um segmento **ainda não alcançado** não interfere em nada.
    """
    if type(segmento) is not tuple or len(segmento) != 2:
        raise _nao_resolvido(_TIPO_INVALIDO, _DECOMPOSICAO)

    chave, seletor = segmento
    if type(chave) is not str:
        raise _nao_resolvido(_TIPO_INVALIDO, _DECOMPOSICAO)

    if seletor is None:
        return chave, None

    if type(seletor) is not tuple or len(seletor) != 2:
        raise _nao_resolvido(_TIPO_INVALIDO, _DECOMPOSICAO)

    chave_seletora, literal = seletor
    if type(chave_seletora) is not str or type(literal) is not str:
        raise _nao_resolvido(_TIPO_INVALIDO, _DECOMPOSICAO)

    return chave, seletor


def _percorrer(base: object, segmentos: tuple) -> object:
    """Percorre `segmentos` a partir de `base`, da esquerda para a direita.

    Com `segmentos` vazios devolve `base` **por identidade** — o `@` isolado.
    A cada passo a **forma do segmento corrente é exigida primeiro**; só então
    `None` com percurso restante é falha estrutural, o nó precisa ser `dict`
    **exato** e a chave precisa **existir**; o seletor, quando houver, é
    aplicado ao valor já obtido. **Nenhum segmento posterior é inspecionado
    antes de ser alcançado.**
    """
    no = base
    for bruto in segmentos:
        chave, seletor = _exigir_segmento(bruto)

        if no is None:
            raise _nao_resolvido(_TRAVESSIA_EM_NULO, _SEGMENTO)
        if type(no) is not dict:
            raise _nao_resolvido(_TIPO_INCOMPATIVEL, _SEGMENTO)
        if chave not in no:
            raise _nao_resolvido(_SEGMENTO_INEXISTENTE, _SEGMENTO)

        no = no[chave]

        if seletor is not None:
            no = _aplicar_seletor(no, seletor)

    return no


def _aplicar_seletor(valor: object, seletor: tuple[str, str]) -> object:
    """Aplica `[chave=literal]` a `valor`, por **conformidade**.

    A coleção precisa ser `list` **exata** e é percorrida **inteira**: cada item
    é exigido como `dict` exato, com a chave seletora **presente** e com valor
    `str` **exato**. Só **depois** de toda a coleção estar conforme a
    cardinalidade é decidida — de modo que um item malformado vence um *match*
    anterior e vence até dois. A comparação é **literal, por `str`**.
    """
    chave_seletora, literal = seletor

    if valor is None:
        raise _nao_resolvido(_TRAVESSIA_EM_NULO, _SELETOR)
    if type(valor) is not list:
        raise _nao_resolvido(_TIPO_INCOMPATIVEL, _SELETOR)

    encontrado = _AUSENTE
    multiplos = False

    for item in valor:
        if type(item) is not dict:
            raise _nao_resolvido(_TIPO_INCOMPATIVEL, _SELETOR)
        if chave_seletora not in item:
            raise _nao_resolvido(_SEGMENTO_INEXISTENTE, _SELETOR)

        candidato = item[chave_seletora]
        if type(candidato) is not str:
            raise _nao_resolvido(_TIPO_INCOMPATIVEL, _SELETOR)

        if candidato == literal:
            if encontrado is _AUSENTE:
                encontrado = item
            else:
                multiplos = True

    if encontrado is _AUSENTE:
        raise _nao_resolvido(_ZERO_MATCHES, _SELETOR)
    if multiplos:
        raise _nao_resolvido(_MULTIPLOS_MATCHES, _SELETOR)

    return encontrado


def _nao_resolvido(categoria: str, localizador: str) -> CaminhoYamlNaoResolvido:
    return CaminhoYamlNaoResolvido(f"{categoria}: {localizador}")
