"""Parser puro e determinístico da gramática de `caminho_yaml`.

O bloco **"Micro-arbitragem documental da gramática de `caminho_yaml`"** de
`docs/07` arbitrou a alternativa **`A2`**: `caminho_yaml` é, **depois do parsing
YAML**, uma **`str`**, com **CAMINHO ABSOLUTO SEM MARCADOR** e **CAMINHO RELATIVO
EXPLICITAMENTE MARCADO POR `@`**. `CY13` separou **três** responsabilidades — o
**parser da gramática**, a **validação estrutural do índice** e o **resolver**.
Este módulo materializa **exatamente a primeira, e nada mais**.

**A gramática, literal.**

```text
caminho           ::= caminho_absoluto | caminho_relativo

caminho_absoluto  ::= segmento ( "." segmento )*
caminho_relativo  ::= "@" ( "." segmento )*

segmento          ::= chave seletor?
seletor           ::= "[" chave "=" literal "]"

chave             ::= NOME, exceto se composta exclusivamente por dígitos
literal           ::= NOME

NOME              ::= (A-Z | a-z | 0-9 | "_")+
```

O **alfabeto semântico total** é `A-Z`, `a-z`, `0-9`, `_`, `.`, `[`, `]`, `=` e
`@` — **nada além**. Qualquer outro caractere torna a forma **inválida**.

**A saída é a decomposição já validada.** A função devolve
`(relativo, segmentos)`: `relativo` é `False` para caminho absoluto e `True` para
relativo; `segmentos` é uma `tuple` de pares `(chave, seletor)`, com `seletor`
igual a `None` ou ao par `(chave_seletora, literal)`. Tudo é **imutável** —
`bool`, `str`, `tuple` e `None` —, **sem `dict`**, **sem `list`**, **sem
`dataclass`**, **sem `NamedTuple`**, **sem `Enum`** e **sem DTO**. A decomposição
pertence naturalmente ao papel de parser e permite que a futura validação
contextual e o futuro resolver a consumam **sem reparsear a gramática**.

**`@` isolado** (`CY11`) é caminho relativo válido e devolve `(True, ())`:
nenhum segmento é inventado.

**A entrada é `str` exata.** Uma **subclasse de `str` é recusada** como
`tipo_invalido`, **antes** de qualquer leitura. A razão é técnica: uma subclasse
pode redefinir `__eq__`, `__hash__`, `startswith`, `find` ou `__getitem__` e,
com isso, decidir por conta própria o que o caminho diz. A entrada também **não**
é convertida: não há `str(...)`, `repr` nem coerção de espécie alguma.

**Canonicalidade estrita** (`CY5`). São **recusados**: `str` vazia; *whitespace*
de qualquer espécie; aspas como caracteres do valor; `\\`; `/`; `-`; `:`; `*`;
Unicode não ASCII; `.` inicial; `.` final; `..`; segmento vazio; seletor vazio;
chave seletora vazia; literal vazio; `=` ausente no seletor; `[` sem `]`; `]` sem
abertura correspondente; caracteres após `]` no mesmo segmento; **dois seletores
no mesmo segmento**; `@` fora da primeira posição; e `@@`. **Zero `strip`, zero
`lower`, zero `upper`, zero `casefold`, zero `NFC`/`NFD`, zero `unicodedata`,
zero *escape*, zero inferência e zero tolerância.**

**Chave exclusivamente numérica é deliberadamente NÃO ENDEREÇÁVEL** (`CY9`), tanto
como **chave de segmento** quanto como **chave seletora**. **Isto não afirma que
"chave numérica = posição"**: a chave YAML textual `"123"` **não** é
semanticamente uma posição — ela simplesmente **não é endereçável** nesta
gramática do MVP, por fechamento conservador, auditabilidade estática e
compatibilidade com a materialização vigente de `C-A1-S1` em `E1`. O **literal
seletor**, ao contrário, **pode ser exclusivamente numérico**, porque ele é
**sempre semanticamente uma `str`** (`CY7`).

**Falha é *fail-closed* e imediata**, com **três categorias fechadas** —
`tipo_invalido`, `forma_invalida` e `chave_nao_enderecavel` — e **seis
localizadores semânticos fechados** — `caminho`, `segmento`, `seletor`, `chave`,
`chave_seletora` e `literal`. A mensagem carrega **categoria e localizador**, e
**nunca** o caminho recebido, um fragmento da entrada, o caractere ofensor, o
`repr`, o tipo concreto, um comprimento, um índice, um *offset*, uma posição, uma
linha, uma coluna ou uma cardinalidade observada.

**Precedência fixa desta implementação** — decisão técnica local, **não**
identificador normativo novo de `C`: **1.** tipo da entrada; **2.** caminhada
gramatical da **esquerda para a direita**; **3.** em cada chave **sintaticamente
completa**, primeiro a **forma**, depois a **endereçabilidade**; **4.** a
**primeira** violação encerra; **5.** **nada é acumulado**; **6.** **nada é
devolvido parcialmente**. Por isso `123.` falha em `chave_nao_enderecavel: chave`
— a primeira chave completa e não endereçável é encontrada **antes** da borda
final inválida.

**Pureza.** Fora `annotations`, o módulo **não importa nada**: **zero `re`**,
**zero `unicodedata`**, **zero YAML**, **zero JSON**, **zero `pathlib`**, **zero
`os`**, **zero `locale`**, **zero `subprocess`**, **zero módulo interno**, **zero
terceiro**, **zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero relógio**, **zero calendário**, **zero aleatoriedade**, **zero variável de
ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero estado
mutável de módulo**, **zero `global`/`nonlocal`**, **zero `assert`**, **zero
`try`/`except`**, **zero `raise from`**, **zero `eval`/`exec`**, **zero
normalização** e **zero coerção**. A entrada **não é alterada**.

**ANALISAR O CAMINHO NÃO É RESOLVER E NÃO É MATERIALIZAR `C`.** Um retorno
bem-sucedido afirma **somente** que a `str` recebida satisfaz a gramática e a
canonicalidade. Ele **não** diz se a `str` veio de `caminho_yaml` ou de
`itera_sobre`; se o fragmento possui `itera_sobre`; se um caminho relativo é
contextualmente permitido; se a chave existe no YAML; se o seletor tem *match*;
se o caminho resolve; se o terminal é `null`; se existe `status: pendente`; se
existe índice físico; nem se o corpus é oficial. **A validação estrutural do
índice e o resolver de `CY13` continuam NÃO IMPLEMENTADOS**, `C-7` continua **NÃO
MATERIALIZADA**, `knowledge/indice-respostas-aprovadas.yaml` continua
**INEXISTENTE**, a autoridade de status continua no Markdown aprovado (`C-11`) e
**`C` continua ARBITRADA / NÃO MATERIALIZADA**.
"""

from __future__ import annotations

__all__ = ["CaminhoYamlInvalido", "analisar_caminho_yaml"]


class CaminhoYamlInvalido(Exception):
    """A `str` recebida não satisfaz a gramática de `caminho_yaml`.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** impede a análise e o localizador diz **em que construção** — nunca o
    caminho recebido, um fragmento dele, o caractere ofensor, o `repr`, o tipo
    concreto, um comprimento, um índice, um *offset*, uma posição, uma linha,
    uma coluna ou uma cardinalidade observada.

    Levantá-la significa **apenas** que a `str` dada é gramaticalmente inválida.
    Ela **não** afirma coisa alguma sobre `itera_sobre`, sobre a existência da
    chave no YAML, sobre *match* de seletor, sobre resolução, sobre `C-7` ou
    sobre o índice — nada disso pertence a esta fronteira.
    """


# Categorias tecnicas privadas e fechadas. Elas nomeiam o impedimento e **nao**
# sao identificadores normativos novos de `C`. Sao exatamente tres.
_TIPO_INVALIDO = "tipo_invalido"
_FORMA_INVALIDA = "forma_invalida"
_CHAVE_NAO_ENDERECAVEL = "chave_nao_enderecavel"

# Localizadores semanticos fechados. Eles nomeiam **a especie de construcao**
# onde o impedimento esta, jamais a sua posicao no caminho.
_CAMINHO = "caminho"
_SEGMENTO = "segmento"
_SELETOR = "seletor"
_CHAVE = "chave"
_CHAVE_SELETORA = "chave_seletora"
_LITERAL = "literal"

# Alfabeto de `NOME`, escrito por extenso: a pertenca e decidida por `in` sobre
# uma `str` imutavel, sem `set`, sem `dict` e sem `re`.
_CARACTERES_DE_NOME = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" "0123456789" "_"
)

# Digitos ASCII, e somente eles: digito decimal de outro sistema de escrita nao
# e digito aqui — alias, ele sequer pertence a `NOME`.
_DIGITOS_ASCII = "0123456789"

# Sintaxe fisica fechada da gramatica.
_MARCADOR_RELATIVO = "@"
_PONTO = "."
_ABRE = "["
_FECHA = "]"
_IGUAL = "="


def analisar_caminho_yaml(
    caminho: str,
) -> tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]:
    """Analisa `caminho` e devolve a sua decomposição gramatical já validada.

    Devolve `(relativo, segmentos)`. `relativo` é `False` para **caminho
    absoluto** — sem marcador, com raiz no mapeamento raiz do YAML — e `True`
    para **caminho relativo** — marcado por `@` **exatamente na posição
    inicial**, com raiz no item corrente da coleção percorrida por
    `itera_sobre`. `segmentos` é uma `tuple` de pares `(chave, seletor)`, na
    **ordem em que aparecem**, com `seletor` igual a `None` ou ao par
    `(chave_seletora, literal)`.

    A entrada `@` isolada devolve `(True, ())`: nenhum segmento é inventado.

    `caminho` precisa ser do tipo `str` **exatamente** — subclasse de `str` é
    recusada como `tipo_invalido`, **antes** de qualquer leitura. A entrada
    **não é alterada** e **não é convertida**.

    Levanta `CaminhoYamlInvalido` com **três** categorias fechadas:
    `tipo_invalido` — a entrada não é `str` exata; `forma_invalida` — qualquer
    violação léxico-sintática ou de canonicalidade da gramática; e
    `chave_nao_enderecavel` — uma chave **sintaticamente bem formada** porém
    **composta exclusivamente por dígitos**, seja **chave de segmento**, seja
    **chave seletora**. Os localizadores são `caminho`, `segmento`, `seletor`,
    `chave`, `chave_seletora` e `literal`.

    O **literal seletor pode ser exclusivamente numérico** — `colecao[id=2026]`
    é **válido** —, porque o literal é **sempre semanticamente uma `str`**
    (`CY7`). A restrição de endereçabilidade alcança **apenas chaves**.

    A ordem de validação é **fixa**: **1.** tipo da entrada; **2.** caminhada da
    esquerda para a direita; **3.** por chave sintaticamente completa, primeiro
    a **forma**, depois a **endereçabilidade**; **4.** a primeira violação
    encerra; **5.** nada é acumulado; **6.** nada é devolvido parcialmente.

    **ANALISAR O CAMINHO NÃO É RESOLVER E NÃO É MATERIALIZAR `C`.** O sucesso
    afirma **somente** conformidade gramatical da `str` dada — nada sobre
    `itera_sobre`, existência de chave, *match* de seletor, resolução, terminal
    `null`, `C-7`, índice físico ou origem do corpus.
    """
    if type(caminho) is not str:
        raise _invalido(_TIPO_INVALIDO, _CAMINHO)

    if not caminho:
        raise _invalido(_FORMA_INVALIDA, _CAMINHO)

    if caminho[0] == _MARCADOR_RELATIVO:
        resto = caminho[1:]
        if not resto:
            # `CY11`: `@` isolado e o proprio item corrente, sem segmento algum.
            return (True, ())
        if resto[0] != _PONTO:
            # Depois do marcador so cabe o fim da `str` ou um `.` seguido de
            # segmentos: `@@`, `@a` e afins nao tem forma de caminho.
            raise _invalido(_FORMA_INVALIDA, _CAMINHO)
        return (True, _segmentos(resto[1:]))

    return (False, _segmentos(caminho))


def _segmentos(texto: str) -> tuple[tuple[str, tuple[str, str] | None], ...]:
    """Decompõe `texto` nos seus segmentos, da esquerda para a direita.

    A divisão é por `.` literal. O `.` não pertence a `NOME`, de modo que ele
    **nunca** ocorre legitimamente dentro de um seletor: um `.` intercalado ali
    apenas produz partes malformadas, que são recusadas adiante. A avaliação é
    preguiçosa e a `tuple` a consome em ordem, de modo que a **primeira**
    violação física encerra a análise.
    """
    return tuple(_segmento(bruto) for bruto in texto.split(_PONTO))


def _segmento(bruto: str) -> tuple[str, tuple[str, str] | None]:
    """Analisa um segmento: a sua chave e, quando houver, o seu seletor.

    A chave é julgada **antes** do seletor — primeiro a forma, depois a
    endereçabilidade —, conforme a precedência fixa desta fronteira.
    """
    if not bruto:
        raise _invalido(_FORMA_INVALIDA, _SEGMENTO)

    abertura = bruto.find(_ABRE)
    if abertura < 0:
        chave = bruto
        resto = ""
    else:
        chave = bruto[:abertura]
        resto = bruto[abertura:]

    _exigir_chave(chave, _CHAVE)

    if not resto:
        return (chave, None)

    return (chave, _seletor(resto))


def _seletor(resto: str) -> tuple[str, str]:
    """Analisa `[chave=literal]`, do qual existe **no máximo um** por segmento.

    Um segundo seletor, um `]` sobrando ou qualquer caractere depois do
    fechamento deixam conteúdo estranho dentro do envelope, e por isso caem
    todos em `forma_invalida: seletor`.
    """
    if not resto.endswith(_FECHA):
        raise _invalido(_FORMA_INVALIDA, _SELETOR)

    interno = resto[1:-1]
    if _ABRE in interno or _FECHA in interno:
        raise _invalido(_FORMA_INVALIDA, _SELETOR)

    igual = interno.find(_IGUAL)
    if igual < 0:
        raise _invalido(_FORMA_INVALIDA, _SELETOR)

    chave_seletora = interno[:igual]
    literal = interno[igual + 1 :]

    _exigir_chave(chave_seletora, _CHAVE_SELETORA)

    if not _e_nome(literal):
        raise _invalido(_FORMA_INVALIDA, _LITERAL)

    return (chave_seletora, literal)


def _exigir_chave(valor: str, localizador: str) -> None:
    """Exige que `valor` seja `NOME` e que não seja exclusivamente numérico.

    A ordem é normativa desta fronteira: **forma primeiro, endereçabilidade
    depois**. Uma chave malformada é `forma_invalida`; uma chave bem formada
    porém só de dígitos é `chave_nao_enderecavel`.
    """
    if not _e_nome(valor):
        raise _invalido(_FORMA_INVALIDA, localizador)
    if _so_digitos(valor):
        raise _invalido(_CHAVE_NAO_ENDERECAVEL, localizador)


def _e_nome(valor: str) -> bool:
    """Diz se `valor` é um `NOME`: não vazio e restrito ao alfabeto fechado.

    Toda a canonicalidade cabe aqui: *whitespace*, aspas, `\\`, `/`, `-`, `:`,
    `*`, `@` fora da posição inicial e qualquer caractere não ASCII ficam de
    fora do alfabeto e, portanto, são recusados **sem** normalização, coerção
    ou tolerância.
    """
    if not valor:
        return False
    for caractere in valor:
        if caractere not in _CARACTERES_DE_NOME:
            return False
    return True


def _so_digitos(valor: str) -> bool:
    """Diz se `valor` é composto **exclusivamente** por dígitos ASCII.

    Só é consultada depois de `_e_nome`, de modo que `valor` já é não vazio e
    já está restrito ao alfabeto — um dígito decimal de outro sistema de escrita
    sequer chega até aqui.
    """
    for caractere in valor:
        if caractere not in _DIGITOS_ASCII:
            return False
    return True


def _invalido(categoria: str, localizador: str) -> CaminhoYamlInvalido:
    return CaminhoYamlInvalido(f"{categoria}: {localizador}")
