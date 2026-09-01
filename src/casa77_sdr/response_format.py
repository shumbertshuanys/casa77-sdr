"""Formatadores determinísticos dos formatos de apresentação pura de `C-6`.

Este módulo materializa **cinco** dos formatos do vocabulário fechado de `C-6`:
`inteiro` (C-6a), `inteiro_agrupado` (C-6b), `simbolo_moeda` (C-6c), `texto`
(C-6e) e `lista` (C-6f). Cada um é uma função **pura**: recebe um valor já
resolvido, devolve a sua **representação de apresentação** e nada mais.

O formato `hora` (C-6d) **NÃO é implementado aqui**. `C-A1-F3` fixa dois padrões
fechados — `HH:MM` e `Hh`, este último somente com minutos `00` —, mas **não
existe regra arbitrada** que escolha mecanicamente entre eles a partir do valor.
Escolher seria arbitrar, e arbitrar não é formatar: o formato fica **fora desta
fronteira** até que a lacuna seja fechada.

**Apresentação pura, sem dependência oculta** (C-6, C-8). Nenhum formatador
calcula, arredonda, resume, parafraseia, recorta, infere, consulta *locale*,
abre arquivo, lê base comercial ou busca campo adicional por conta própria — em
particular, `simbolo_moeda` recebe o código monetário **explicitamente**, e
**nunca** o deduz (C-6c, C-A1-F2, C-A4-F2f). O módulo **não importa nada de
`casa77_sdr`**: ele não conhece índice, carregador, comparador, *template*,
*placeholder*, Markdown, *renderer* nem consumidor. Nenhum preço, capacidade,
horário ou condição comercial vive aqui.

Falha é **fail-closed** e imediata: a primeira violação levanta
`FormatoInaplicavel`, e nada é acumulado. O que **não** é formatável não é
"quase formatado" — é recusado.

**FORMATAR NÃO É MATERIALIZAR `C`.** O índice continua inexistente, nenhum
fragmento real é renderizado e nenhum consumidor é integrado.
"""

from __future__ import annotations

from collections.abc import Sequence

__all__ = [
    "FormatoInaplicavel",
    "formatar_inteiro",
    "formatar_inteiro_agrupado",
    "formatar_simbolo_moeda",
    "formatar_texto",
    "formatar_lista",
]


class FormatoInaplicavel(Exception):
    """O formato não se aplica ao que foi recebido.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** viola o contrato do formato e o localizador diz **onde** — nunca o
    valor, o item, o código ou o conteúdo textual recebido.
    """


# Categorias técnicas fechadas. Duas bastam para esta fronteira: ou o que
# chegou não tem o tipo que o formato exige, ou tem o tipo e ainda assim está
# fora do que o contrato admite.
_TIPO_INVALIDO = "tipo_invalido"
_VALOR_INVALIDO = "valor_invalido"

# Localizadores fechados.
_VALOR = "valor"
_CODIGO = "codigo"
_ITENS = "itens"
_ITEM = "itens.item"

# C-A4-F1b-C-A4-F1d: grupos de tres digitos, da direita para a esquerda,
# separados por `.`. Constantes de apresentacao - nenhuma delas e fato
# comercial.
_DIGITOS_POR_GRUPO = 3
_SEPARADOR_DE_MILHAR = "."
_SINAL_NEGATIVO = "-"

# C-A1-L3 e C-A1-L4: virgula entre os anteriores, conjuncao antes do ultimo.
_SEPARADOR_DE_ITEM = ", "
_CONJUNCAO = " e "

# C-A1-F2 / C-A4-F2d: tabela fechada, do tamanho exato do contrato atual, e
# **nao ampliada** aqui. Pertence a implementacao do formato, nunca ao indice.
_SIMBOLO_POR_CODIGO = {"BRL": "R$"}


def formatar_inteiro(valor: int) -> str:
    """Representação decimal do **mesmo** inteiro, sem agrupamento (C-6a).

    Aceita **somente** `int` estrito. `bool` é recusado — apesar de ser
    subclasse de `int`, ele não é um inteiro de apresentação —, e `float`,
    `Decimal` e texto numérico também: **não há coerção**. Nada é arredondado,
    calculado ou completado com zero, e o sinal decorrente do valor é
    preservado.
    """
    _exigir_inteiro(valor)

    return str(valor)


def formatar_inteiro_agrupado(valor: int) -> str:
    """O **mesmo** inteiro, com agrupamento visual de milhar (C-6b, C-A4-F1).

    Os dígitos são agrupados de três em três **da direita para a esquerda** e
    unidos por `.`; o grupo mais à esquerda fica com o que sobrar, **sem zero
    para completá-lo**. Não há casas decimais, arredondamento, cálculo,
    alteração do valor, *locale* nem biblioteca cujo resultado dependa do
    ambiente: o agrupamento é montado aqui, dígito a dígito. O sinal é
    preservado e **não** é agrupado.

    Aceita **somente** `int` estrito, com a mesma recusa de `bool` de
    `formatar_inteiro`.
    """
    _exigir_inteiro(valor)

    digitos = str(abs(valor))
    grupos: list[str] = []
    while len(digitos) > _DIGITOS_POR_GRUPO:
        grupos.append(digitos[-_DIGITOS_POR_GRUPO:])
        digitos = digitos[:-_DIGITOS_POR_GRUPO]
    grupos.append(digitos)
    grupos.reverse()

    sinal = _SINAL_NEGATIVO if valor < 0 else ""
    return sinal + _SEPARADOR_DE_MILHAR.join(grupos)


def formatar_simbolo_moeda(codigo: str) -> str:
    """Símbolo do código monetário **explicitamente recebido** (C-6c, C-A4-F2).

    Devolve **somente** o símbolo: o espaço que o cerca pertence ao fragmento
    estático, nunca ao formatador (C-A4-F2c). O código é consultado **como
    chegou** — sem `upper`, sem `strip` e sem tolerância de caixa —, e a tabela
    de moedas suportadas não é ampliada. Código não suportado **falha**, e a
    moeda **nunca** é inferida a partir de outro campo.
    """
    if not isinstance(codigo, str):
        raise _inaplicavel(_TIPO_INVALIDO, _CODIGO)
    if codigo not in _SIMBOLO_POR_CODIGO:
        raise _inaplicavel(_VALOR_INVALIDO, _CODIGO)

    return _SIMBOLO_POR_CODIGO[codigo]


def formatar_texto(valor: str) -> str:
    """Identidade exata: insere o valor **sem modificação alguma** (C-6e).

    Devolve a mesma `str` que recebeu. Não há normalização Unicode, `strip`,
    `casefold`, colapso de espaço, dobra de quebra, ajuste de pontuação nem
    qualquer outra transformação — a `str` vazia continua vazia.
    """
    if not isinstance(valor, str):
        raise _inaplicavel(_TIPO_INVALIDO, _VALOR)

    return valor


def formatar_lista(itens: Sequence[str]) -> str:
    """Enumeração de apresentação dos itens, na ordem recebida (C-6f, C-A1-L).

    Um item devolve o próprio item; dois são unidos por ` e `; três ou mais
    separam os anteriores por `, ` e o último por ` e `. **Zero itens falha**
    (C-A1-L1).

    Todos os itens são preservados, na ordem e **literalmente** (C-A1-L5,
    C-A1-L6): nada é filtrado, reordenado, flexionado, parafraseado nem ganha
    prefixo ou sufixo por item (C-A1-L7, C-A1-L8) — inclusive o item vazio, que
    o contrato **não** proíbe e que portanto entra na composição como qualquer
    outro. A entrada não é alterada.

    Uma `str` **não** é contêiner válido: seus caracteres não são itens. Cada
    item precisa ser `str`.
    """
    if isinstance(itens, str) or not isinstance(itens, Sequence):
        raise _inaplicavel(_TIPO_INVALIDO, _ITENS)

    materializados = tuple(itens)
    if not materializados:
        raise _inaplicavel(_VALOR_INVALIDO, _ITENS)
    for item in materializados:
        if not isinstance(item, str):
            raise _inaplicavel(_TIPO_INVALIDO, _ITEM)

    if len(materializados) == 1:
        return materializados[0]
    anteriores = _SEPARADOR_DE_ITEM.join(materializados[:-1])
    return anteriores + _CONJUNCAO + materializados[-1]


def _exigir_inteiro(valor: object) -> None:
    """Recusa tudo o que não for `int` estrito, `bool` inclusive.

    A checagem de `bool` vem primeiro porque `bool` **é** subclasse de `int`:
    sem ela, `True` passaria como inteiro e seria apresentado como um número
    que ninguém forneceu.
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _inaplicavel(_TIPO_INVALIDO, _VALOR)


def _inaplicavel(categoria: str, localizador: str) -> FormatoInaplicavel:
    return FormatoInaplicavel(f"{categoria}: {localizador}")
