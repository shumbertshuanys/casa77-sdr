"""Verificação determinística da correspondência bijetiva de `C-A1-B3`/`C-A1-B4`.

`C-A1-B3` exige que **cada fragmento do índice** corresponda a **exatamente
uma** unidade emitível do Markdown, e `C-A1-B4` exige a recíproca: **cada
unidade emitível** corresponde a **exatamente um** fragmento. A unidade continua
sendo o **fragmento emitível**, nunca o `Rxx` agregado (`C-A1-B1`); notas e
instruções internas permanecem **fora da bijeção** (`C-A1-B2`) e, por isso,
simplesmente não chegam aqui.

**Os três domínios chegam prontos.** Este módulo **não** extrai fragmento do
índice, **não** extrai unidade do Markdown, **não** decide o que é unidade
emitível, **não** define identidade física de fragmento, **não** cria
identificador, **não** analisa Markdown, **não** lê índice real e **não** afere
a completude do produtor ou do extrator. Ele julga **uma única coisa**: se a
relação recebida é bijetiva **entre os domínios recebidos**.

**Limite da garantia.** Um retorno bem-sucedido significa **somente** que a
relação fornecida é bijetiva sobre os domínios fornecidos. Ele **não** significa
que o índice real esteja completo, que o Markdown tenha sido integralmente
extraído, que a execução física da bijeção do corpus real tenha ocorrido, que
`C-A1-ST7` esteja satisfeita no sistema, nem que a autoridade de status possa
migrar (`C-A1-ST6`–`C-A1-ST10`). A **completude correta dos dois domínios é
pré-condição do chamador** e não é verificável nesta fronteira sem transformá-la
em extrator — que ela deliberadamente não é.

**Tokens opacos.** Fragmentos e unidades são `str` **não interpretadas**: não há
formato `Rxx`, gramática, prefixo, separador, sufixo, `UUID`, número, posição ou
qualquer outra estrutura exigida, e o conteúdo do token **nunca** é lido. A
comparação é **igualdade exata de `str`** — sem `strip`, `casefold`, `lower`,
`upper`, `NFC` ou normalização de espécie alguma. Duas representações Unicode
distintas do mesmo texto são, aqui, **tokens distintos**.

**`str` exata, nunca subclasse.** O token precisa ser do **tipo `str`
exatamente**; uma subclasse de `str` é **recusada**. A razão é técnica: uma
subclasse pode redefinir `__eq__` e `__hash__` e, com isso, decidir por conta
própria quando dois tokens são o mesmo token — a igualdade deixaria de ser a
nativa da `str` e a opacidade prometida acima seria violada pelo chamador. O
token também **não** é convertido: não há `str(...)`, `repr` nem coerção de
espécie alguma.

**Sequência explícita de pares, não `Mapping`.** A relação chega como sequência
de pares — nunca como mapa — porque um mapa **colapsaria silenciosamente** uma
origem repetida ao sobrescrever a chave, escondendo exatamente a violação que
precisa ser observada *fail-closed*. Pela mesma razão o domínio dos tokens é
`str`, e não `Hashable` arbitrário: um `Hashable` qualquer traria `__hash__` e
`__eq__` próprios, e a identidade dos tokens deixaria de ser decidível aqui.

Falha é **fail-closed** e imediata: a primeira violação encerra, e nada é
acumulado (P5). A mensagem carrega **categoria e localizador**, nunca o token
recebido, o conteúdo, o `repr`, o tipo concreto, um índice numérico, um tamanho
ou uma cardinalidade. As entradas **não são alteradas**.

**VERIFICAR A RELAÇÃO NÃO É MATERIALIZAR `C`.** O índice continua inexistente,
nenhum fragmento real é validado e nenhum consumidor é integrado.
"""

from __future__ import annotations

from collections.abc import Sequence

__all__ = ["BijecaoInvalida", "validar_bijecao"]


class BijecaoInvalida(Exception):
    """A relação recebida não é bijetiva sobre os domínios recebidos.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **onde** — nunca o token recebido, o
    conteúdo, o tipo concreto, uma posição ou uma quantidade.

    Levantá-la significa que a relação **não** é bijetiva sobre o que foi
    entregue. Não levantá-la significa apenas o oposto disso: **nada** é
    afirmado sobre o índice real, sobre o Markdown real ou sobre `C-A1-ST7`.
    """


# Categorias técnicas privadas e fechadas. Elas nomeiam o impedimento e **não**
# são identificadores normativos novos de `C`.
_TIPO_INVALIDO = "tipo_invalido"
_ESTRUTURA_INVALIDA = "estrutura_invalida"
_DUPLICIDADE = "duplicidade"
_REFERENCIA_DESCONHECIDA = "referencia_desconhecida"
_COBERTURA_INCOMPLETA = "cobertura_incompleta"

# Localizadores fechados, um por argumento.
_FRAGMENTOS_INDICE = "fragmentos_indice"
_UNIDADES_MARKDOWN = "unidades_markdown"
_CORRESPONDENCIAS = "correspondencias"

# Localização estrutural dentro da relação.
_ITEM = "correspondencias.item"
_ORIGEM = "correspondencias.origem"
_DESTINO = "correspondencias.destino"

# Um par é origem e destino, e nada mais.
_TAMANHO_DO_PAR = 2
_POSICAO_DA_ORIGEM = 0
_POSICAO_DO_DESTINO = 1


def validar_bijecao(
    fragmentos_indice: Sequence[str],
    unidades_markdown: Sequence[str],
    correspondencias: Sequence[tuple[str, str]],
) -> None:
    """Verifica se `correspondencias` é bijetiva entre os dois domínios dados.

    Devolve `None` quando a relação é **total, injetiva e sobrejetiva** nos dois
    sentidos: toda origem e todo destino são conhecidos, nenhum se repete, e
    nenhum fragmento ou unidade fica sem par. Levanta `BijecaoInvalida` na
    **primeira** violação, sem acumular nada.

    A ordem de validação é **fixa**: tipo dos três argumentos; tipo dos tokens
    de `fragmentos_indice`; tipo dos tokens de `unidades_markdown`; tipo e, em
    seguida, forma dos itens da relação; tipo de origem e destino de cada par;
    duplicidade em `fragmentos_indice`; duplicidade em `unidades_markdown`;
    origem repetida; destino repetido; origem desconhecida; destino
    desconhecido; fragmento sem par; unidade sem par. Cada etapa percorre
    **toda** a entrada antes da seguinte, de modo que a precedência não depende
    da posição do defeito; dentro de um mesmo par, origem precede destino.

    A relação **de topo** é uma `Sequence` — `list`, `tuple` ou outra —, mas
    **cada item dela é obrigatoriamente uma `tuple` exata de exatamente dois
    elementos**, origem e destino, ambos `str` **exata** — subclasse de `str` é
    recusada, nos dois domínios e nos dois lados. **Subclasse de `tuple`
    também é recusada**: ela poderia redefinir `__len__` ou `__getitem__` e
    apresentar valores diferentes a cada leitura, de modo que a forma
    verificada não seria a mesma que a lida depois. Uma `list` de dois
    elementos **não** é um par válido: o contrato público é `tuple[str, str]`,
    e o runtime não o amplia. `str`, `bytes` e `bytearray` também **não** são
    contêineres válidos para nenhum dos três argumentos, porque seus elementos
    não são tokens.

    **Três domínios vazios são uma bijeção trivial válida** e devolvem `None`.
    Isso afirma **apenas** que a relação é bijetiva sobre os domínios
    fornecidos — não que o corpus real esteja vazio, extraído, validado, nem que
    `C-A1-ST7` esteja satisfeita.
    """
    _exigir_sequencia(fragmentos_indice, _FRAGMENTOS_INDICE)
    _exigir_sequencia(unidades_markdown, _UNIDADES_MARKDOWN)
    _exigir_sequencia(correspondencias, _CORRESPONDENCIAS)

    fragmentos = tuple(fragmentos_indice)
    unidades = tuple(unidades_markdown)
    pares = tuple(correspondencias)

    _exigir_tokens(fragmentos, _FRAGMENTOS_INDICE)
    _exigir_tokens(unidades, _UNIDADES_MARKDOWN)

    for par in pares:
        if type(par) is not tuple:
            raise _invalida(_TIPO_INVALIDO, _ITEM)
    for par in pares:
        if len(par) != _TAMANHO_DO_PAR:
            raise _invalida(_ESTRUTURA_INVALIDA, _ITEM)

    for par in pares:
        if type(par[_POSICAO_DA_ORIGEM]) is not str:
            raise _invalida(_TIPO_INVALIDO, _ORIGEM)
        if type(par[_POSICAO_DO_DESTINO]) is not str:
            raise _invalida(_TIPO_INVALIDO, _DESTINO)

    _exigir_tokens_distintos(fragmentos, _FRAGMENTOS_INDICE)
    _exigir_tokens_distintos(unidades, _UNIDADES_MARKDOWN)

    origens = tuple(par[_POSICAO_DA_ORIGEM] for par in pares)
    destinos = tuple(par[_POSICAO_DO_DESTINO] for par in pares)

    _exigir_tokens_distintos(origens, _ORIGEM)
    _exigir_tokens_distintos(destinos, _DESTINO)

    _exigir_conhecidos(origens, frozenset(fragmentos), _ORIGEM)
    _exigir_conhecidos(destinos, frozenset(unidades), _DESTINO)

    _exigir_cobertura(fragmentos, frozenset(origens), _FRAGMENTOS_INDICE)
    _exigir_cobertura(unidades, frozenset(destinos), _UNIDADES_MARKDOWN)


def _e_contentor(valor: object) -> bool:
    """Diz se `valor` é uma sequência capaz de conter tokens ou pares.

    Uma `str`, um `bytes` e um `bytearray` são sequências, mas os seus elementos
    são caracteres e octetos — nunca tokens nem pares. Por isso são recusados
    como contêiner.

    Vale para os **três argumentos de topo**. O item individual da relação não
    passa por aqui: ele precisa ser `tuple`, e nada mais.
    """
    if isinstance(valor, (str, bytes, bytearray)):
        return False
    return isinstance(valor, Sequence)


def _exigir_sequencia(valor: object, localizador: str) -> None:
    if not _e_contentor(valor):
        raise _invalida(_TIPO_INVALIDO, localizador)


def _exigir_tokens(tokens: tuple[object, ...], localizador: str) -> None:
    """Recusa o domínio se algum elemento não for uma `str` **exata**.

    A verificação é por **tipo exato**, não por `isinstance`: uma subclasse de
    `str` pode redefinir `__eq__` e `__hash__` e, com isso, decidir por conta
    própria quando dois tokens são o mesmo token. Aceitá-la entregaria ao
    chamador a semântica de identidade que esta fronteira precisa manter
    nativa.
    """
    for token in tokens:
        if type(token) is not str:
            raise _invalida(_TIPO_INVALIDO, localizador)


def _exigir_tokens_distintos(tokens: tuple[str, ...], localizador: str) -> None:
    """Recusa a repetição de um token, por **igualdade exata de `str`**.

    Nenhuma normalização precede a comparação: dois tokens só são o mesmo token
    quando são a mesma `str`, caractere a caractere.
    """
    vistos: set[str] = set()
    for token in tokens:
        if token in vistos:
            raise _invalida(_DUPLICIDADE, localizador)
        vistos.add(token)


def _exigir_conhecidos(
    tokens: tuple[str, ...], dominio: frozenset[str], localizador: str
) -> None:
    """Recusa um lado da relação que aponte para fora do seu domínio."""
    for token in tokens:
        if token not in dominio:
            raise _invalida(_REFERENCIA_DESCONHECIDA, localizador)


def _exigir_cobertura(
    tokens: tuple[str, ...], relacionados: frozenset[str], localizador: str
) -> None:
    """Recusa o domínio que contenha um token sem par na relação."""
    for token in tokens:
        if token not in relacionados:
            raise _invalida(_COBERTURA_INCOMPLETA, localizador)


def _invalida(categoria: str, localizador: str) -> BijecaoInvalida:
    return BijecaoInvalida(f"{categoria}: {localizador}")
