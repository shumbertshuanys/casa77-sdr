"""Sintaxe física de *placeholder* — derivação e decomposição de *template*.

Esta fronteira fecha **uma única** matéria: **a forma física do *placeholder* no
*template* de um fragmento emitível** (`PH1`). Ela **não** rege `caminho_yaml`,
formato, predicado, valor factual, *renderer* nem equivalência.

**Forma canônica.** Um *placeholder* é **exatamente** `{{nome}}` — a
concatenação literal `"{{" + nome + "}}"`, **sem conteúdo adicional entre os
delimitadores** (`PH2`): sem espaço, sem filtro, sem formato, sem caminho, sem
qualificador.

**O campo explícito permanece.** `binding.placeholder` continua **obrigatório**
para `RENDERIZADO`, como `C-4c` já exige; o que esta fronteira fecha é que o seu
valor canônico é `derivar_placeholder(binding.nome)`, conferido por **comparação
literal** (`PH3`). O nome é o identificador lógico; o *placeholder* é a sua
representação física. **Nada é removido do índice, e `C-4c` não é alterada.**

**Gramática do nome** (`PH4`), válida **somente** para *bindings*
`RENDERIZADO` e **não** estendida a `ASSERTIVA`::

    nome   ::= letra ( letra | digito )* ( "_" ( letra | digito )+ )*
    letra  ::= a-z ASCII
    digito ::= 0-9 ASCII

Ou seja: não vazio; primeiro caractere em `a-z`; somente `a-z`, `0-9` e `_`;
`_` apenas interno, nunca inicial, nunca final e nunca duplicado; sem
maiúscula; sem Unicode não ASCII; sem espaço, tab ou LF. **Nenhum limite
artificial de tamanho é criado.**

**As chaves são reservadas** (`PH5`). No MVP, `{` e `}` pertencem à sintaxe de
*placeholder*: fora de um *placeholder* canônico, ambos são inválidos. **Não
existe *escaping*** e **nenhuma intenção é inferida**. Chave literal legítima
encontrada em corpus futuro **bloqueia aquele fragmento** e volta à arbitragem —
nunca se resolve por tolerância local.

***Parsing* literal** (`PH6`). Varredura da esquerda para a direita: ao
encontrar `{`, exige-se um segundo `{`, extrai-se o conteúdo, exige-se `}}` e
valida-se o conteúdo pela gramática do nome. Envelope incompleto ou divergente é
***fail-closed***, sem normalização e sem correção.

**Cardinalidade** (`PH7`). Cada *binding* precisa de **pelo menos uma**
ocorrência do seu *placeholder*; **duas ou mais são válidas**, e o **mesmo**
*binding* abastece **todas** elas. Zero ocorrências é falha. *Bindings*
artificiais adicionais, criados só porque o mesmo fato é citado novamente, são
**proibidos** — `C-4a` continua exigindo nome único no fragmento.

**Decomposição alternada** (`PH10`). O sucesso produz
`literal, nome, literal, ..., literal`: os nomes na **ordem física de ocorrência
no *template***, um nome podendo repetir-se, todos os nomes fornecidos ocorrendo
ao menos uma vez, nenhum nome desconhecido, e **literais possivelmente vazios**
— inclusive nas extremidades e entre *placeholders* adjacentes. O comprimento é
sempre ímpar.

**Nenhuma normalização** (`PH9`). Sem `strip`, `lower`, `upper`, `casefold`,
NFC, NFD, coerção, tolerância de *whitespace* ou correspondência aproximada.
**NFC pertence exclusivamente à equivalência de `C-15b`** e **não** é reaberta
aqui. `LF`, espaço e qualquer outro caractere fora dos delimitadores permanecem
**literalmente** no literal que os contém.

**Tipo exato.** `type(x) is str` e `type(x) is tuple`: **subclasse não é a forma
canônica** desta fronteira, porque uma subclasse pode redefinir `__eq__`,
`__hash__` ou `__iter__` e decidir por conta própria o que a entrada diz.

**A mensagem não vaza.** A exceção **não** carrega o *template*, o nome
recebido, um trecho, uma posição, um comprimento, conteúdo factual, o `repr` ou
o tipo concreto. O vocabulário é fechado: categorias `tipo_invalido`,
`valor_invalido`, `duplicidade`, `forma_invalida`, `placeholder_sem_binding` e
`binding_sem_placeholder`; localizadores `nome`, `template`, `nomes`,
`nomes.item` e `placeholder`.

**Pureza.** O módulo importa **apenas** `annotations`: **zero `re`**, **zero
`string`**, **zero `unicodedata`**, **zero `collections`**, **zero módulo do
projeto**, **zero *parser* externo**, **zero motor de *template***, **zero
`.format`**, **zero `format_map`**, **zero `replace` iterativo**, **zero I/O**,
**zero *filesystem***, **zero rede**, **zero ambiente**, **zero logging**,
**zero cache** e **zero LLM**. O *parser* é explícito e pequeno.

**O RENDERER NÃO É IMPLEMENTADO AQUI** (`PH11`). Quem futuramente consumir a
decomposição fará **uma única passada** sobre ela, e **valor formatado não é
reinterpretado como *template***: um valor factual que contenha algo semelhante
a `{{x}}` permanece **texto factual literal**.

**DECOMPOR NÃO É MATERIALIZAR `C`** (`PH12`). Esta fronteira não cria índice,
não cria *renderer*, não altera `knowledge/**`, não converte `Rxx` reais, não
integra `E1` — `src/casa77_sdr/response_index.py` continua **INALTERADO** —, não
resolve *binding* factual, não aplica `C-7`, não executa formato, não executa
`C-15`, não resolve `S2-D8`, não satisfaz `C-A1-ST6`–`C-A1-ST10` e não migra a
autoridade de status.
"""

from __future__ import annotations

__all__ = [
    "PlaceholderInvalido",
    "derivar_placeholder",
    "decompor_template",
]


class PlaceholderInvalido(Exception):
    """A entrada não satisfaz a sintaxe física de *placeholder*.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** impede a operação e o localizador diz **em que construção** — nunca o
    *template* recebido, o nome recebido, um trecho, um caractere ofensor, uma
    posição, um comprimento, conteúdo factual, o `repr` ou o tipo concreto.

    Ela é **irmã**, e não parente, de `CaminhoYamlInvalido`: aquela recusa uma
    `str` como `caminho_yaml`; esta recusa um nome como *placeholder* ou um
    *template* como decomponível. Levantá-la **não** afirma coisa alguma sobre o
    índice físico, sobre `Rxx`, sobre valor factual, sobre `C-7`, sobre formato
    ou sobre equivalência.
    """


# Categorias tecnicas privadas e fechadas. Elas nomeiam o impedimento e **nao**
# sao identificadores normativos novos de `C`. Sao exatamente seis.
_TIPO_INVALIDO = "tipo_invalido"
_VALOR_INVALIDO = "valor_invalido"
_DUPLICIDADE = "duplicidade"
_FORMA_INVALIDA = "forma_invalida"
_PLACEHOLDER_SEM_BINDING = "placeholder_sem_binding"
_BINDING_SEM_PLACEHOLDER = "binding_sem_placeholder"

# Localizadores semanticos fechados. Eles nomeiam **a especie de construcao**
# onde o impedimento esta, jamais a sua posicao ou o seu conteudo.
_NOME = "nome"
_TEMPLATE = "template"
_NOMES = "nomes"
_NOMES_ITEM = "nomes.item"
_PLACEHOLDER = "placeholder"

# Alfabeto de `PH4`, escrito por extenso: a pertenca e decidida por `in` sobre
# uma `str` imutavel, sem `set`, sem `dict`, sem `string` e sem `re`.
_MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
_DIGITOS = "0123456789"
_ALFANUMERICOS = _MINUSCULAS + _DIGITOS
_SUBLINHADO = "_"

# Sintaxe fisica fechada do envelope. `{` e `}` sao reservados (`PH5`).
_ABRE = "{"
_FECHA = "}"
_ABERTURA = _ABRE + _ABRE
_FECHAMENTO = _FECHA + _FECHA


def derivar_placeholder(nome: str) -> str:
    """Devolve a representação física canônica de `nome`.

    `nome` precisa ser `str` **exata** — subclasse é recusada como
    `tipo_invalido` **antes** de qualquer leitura — e precisa satisfazer a
    gramática de `PH4`, sob pena de `valor_invalido`.

    O resultado é **exatamente** `"{{" + nome + "}}"` (`PH2`). Não há
    normalização, não há *cache* e **não existe outra representação**: esta é a
    única autoridade sobre o valor canônico de `binding.placeholder` (`PH3b`).

    **DERIVAR NÃO É MATERIALIZAR `C`.** O sucesso afirma **somente** que o nome
    é gramaticalmente válido e qual é a sua forma física — nada sobre a
    existência do *binding*, do fragmento, do `Rxx` ou do índice.
    """
    if type(nome) is not str:
        raise _invalido(_TIPO_INVALIDO, _NOME)

    if not _e_nome_de_binding(nome):
        raise _invalido(_VALOR_INVALIDO, _NOME)

    return _ABERTURA + nome + _FECHAMENTO


def decompor_template(
    template: str,
    nomes: tuple[str, ...],
) -> tuple[str, ...]:
    """Decompõe `template` alternando literais e nomes de *binding*.

    `template` é o texto do fragmento emitível e `nomes` são **exatamente** os
    nomes dos *bindings* `RENDERIZADO` **do mesmo fragmento**. Ambos exigem tipo
    **exato**, e cada nome é julgado pela **mesma** autoridade gramatical usada
    por `derivar_placeholder`.

    Devolve a sequência `literal, nome, literal, ..., literal` — comprimento
    sempre ímpar —, com os nomes na **ordem física de ocorrência no *template***
    e **não** na ordem de `nomes`. Um nome pode repetir-se (`PH7c`); literais
    podem ser vazios, inclusive nas extremidades e entre *placeholders*
    adjacentes (`PH10e`).

    A precedência é **fixa**: **1.** tipo de `template`; **2.** tipo de `nomes`;
    **3.** cada item de `nomes`, **na ordem recebida** — tipo, gramática e
    duplicidade; **4.** o `template`, **da esquerda para a direita** — forma e
    correspondência; **5.** nomes faltantes, **pela ordem de `nomes`**. A
    **primeira violação encerra**, e nada é acumulado nem devolvido
    parcialmente.

    Levanta `PlaceholderInvalido` com `tipo_invalido` (`template`, `nomes`,
    `nomes.item`), `valor_invalido` (`nomes.item`), `duplicidade`
    (`nomes.item`), `forma_invalida` (`template`), `placeholder_sem_binding`
    (`placeholder`) e `binding_sem_placeholder` (`placeholder`).

    **DECOMPOR NÃO É RENDERIZAR.** O sucesso afirma **somente** que o
    *template* é fisicamente bem formado e que ele e os nomes se correspondem
    exatamente — nada sobre valor factual, formato, `C-7`, equivalência ou
    emissibilidade.
    """
    if type(template) is not str:
        raise _invalido(_TIPO_INVALIDO, _TEMPLATE)

    if type(nomes) is not tuple:
        raise _invalido(_TIPO_INVALIDO, _NOMES)

    conhecidos: list[str] = []
    for nome in nomes:
        if type(nome) is not str:
            raise _invalido(_TIPO_INVALIDO, _NOMES_ITEM)
        if not _e_nome_de_binding(nome):
            raise _invalido(_VALOR_INVALIDO, _NOMES_ITEM)
        if nome in conhecidos:
            raise _invalido(_DUPLICIDADE, _NOMES_ITEM)
        conhecidos.append(nome)

    partes, ocorridos = _varrer(template, conhecidos)

    for nome in conhecidos:
        if nome not in ocorridos:
            raise _invalido(_BINDING_SEM_PLACEHOLDER, _PLACEHOLDER)

    return tuple(partes)


def _varrer(template: str, conhecidos: list[str]) -> tuple[list[str], list[str]]:
    """Varre `template` da esquerda para a direita, conforme `PH5`–`PH8`.

    Devolve as partes alternadas e os nomes que de fato ocorreram. Cada `{`
    precisa abrir um envelope canônico completo, e cada `}` fora de envelope é
    recusado: as chaves são **reservadas**, e não há *escaping*. A forma do
    nome extraído é julgada **antes** da sua correspondência com os *bindings*.
    """
    partes: list[str] = []
    ocorridos: list[str] = []
    tamanho = len(template)
    inicio_do_literal = 0
    posicao = 0

    while posicao < tamanho:
        caractere = template[posicao]

        if caractere == _FECHA:
            # `}` so existe como parte do fechamento de um envelope canonico,
            # que a propria varredura ja teria consumido.
            raise _invalido(_FORMA_INVALIDA, _TEMPLATE)

        if caractere != _ABRE:
            posicao += 1
            continue

        if template[posicao : posicao + 2] != _ABERTURA:
            # `{` isolado: nao ha segundo `{`, e nao ha escaping.
            raise _invalido(_FORMA_INVALIDA, _TEMPLATE)

        fim = template.find(_FECHAMENTO, posicao + 2)
        if fim < 0:
            raise _invalido(_FORMA_INVALIDA, _TEMPLATE)

        nome = template[posicao + 2 : fim]
        if not _e_nome_de_binding(nome):
            raise _invalido(_FORMA_INVALIDA, _TEMPLATE)

        if nome not in conhecidos:
            raise _invalido(_PLACEHOLDER_SEM_BINDING, _PLACEHOLDER)

        partes.append(template[inicio_do_literal:posicao])
        partes.append(nome)

        if nome not in ocorridos:
            ocorridos.append(nome)

        posicao = fim + 2
        inicio_do_literal = posicao

    partes.append(template[inicio_do_literal:])

    return partes, ocorridos


def _e_nome_de_binding(valor: str) -> bool:
    """Diz se `valor` satisfaz a gramática de nome de `PH4`.

    Toda a canonicalidade cabe aqui: maiúscula, `_` inicial, `_` final, `__`,
    dígito inicial, espaço, tab, LF, pontuação, delimitador e qualquer
    caractere não ASCII ficam de fora e são recusados **sem** normalização,
    coerção ou tolerância. Um dígito decimal de outro sistema de escrita **não**
    é dígito aqui.
    """
    if not valor:
        return False

    if valor[0] not in _MINUSCULAS:
        return False

    if valor[-1] == _SUBLINHADO:
        return False

    anterior_era_sublinhado = False
    for caractere in valor:
        if caractere == _SUBLINHADO:
            if anterior_era_sublinhado:
                return False
            anterior_era_sublinhado = True
            continue
        if caractere not in _ALFANUMERICOS:
            return False
        anterior_era_sublinhado = False

    return True


def _invalido(categoria: str, localizador: str) -> PlaceholderInvalido:
    return PlaceholderInvalido(f"{categoria}: {localizador}")
