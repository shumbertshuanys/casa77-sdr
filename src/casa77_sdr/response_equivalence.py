"""Equivalência textual determinística de `C-15b`.

Este módulo materializa **apenas** o julgamento de equivalência entre duas `str`
já em **representação canônica**: o **fragmento aprovado já extraído** e a
**renderização textual do mesmo fragmento** (D1). A unidade é o **fragmento
inteiro** (`C-15c`, `C-A4-P1`) — nunca um *placeholder* isolado.

Ele **não é um analisador de Markdown** (D2). A separação entre estrutura e
conteúdo pertence a uma **futura fronteira de extração**, que ainda não existe:
a representação canônica **chega pronta**. Aqui não se identifica *blockquote*,
título, lista, bloco de código ou indentação, não se remove prefixo algum e não
se extrai fragmento de documento nenhum.

O domínio é fechado por D3–D5 e D7. Dentro dele, a normalização é **exatamente**
a de `C-15b`: **NFC** e, em seguida, a **dobra da quebra suave** — um `LF`
isolado vira **um único `U+0020`**, enquanto `\\n\\n` é **preservado
literalmente** como fronteira de parágrafo real. Nenhum outro espaço é
colapsado, e não há `casefold`, *trim* semântico, remoção de pontuação,
tolerância aproximada ou paráfrase.

Os desfechos são **três**, e não dois (D6). Fora do domínio canônico o veredito
**não existe**: em vez de `False`, levanta-se `EquivalenciaNaoDeterminavel`, e
cabe ao chamador **parar ou escalar**. Dentro do domínio, o resultado é
`True` — `C-15a(2)` satisfeita — ou `False`, que aciona `C-15d`.

**Limite da garantia.** A equivalência só tem garantia semântica quando **ambos
os insumos satisfazem a representação canônica** e o fragmento aprovado foi
**corretamente separado da estrutura Markdown pelo produtor responsável**. Essa
segunda condição é **pré-condição do chamador** e **não é integralmente
verificável aqui** sem transformar este módulo em analisador de Markdown. Fora
do domínio canônico, **não há garantia de correção do veredito**.

**Comparar não é materializar `C`.**
"""

from __future__ import annotations

import unicodedata

__all__ = ["EquivalenciaNaoDeterminavel", "sao_textualmente_equivalentes"]


class EquivalenciaNaoDeterminavel(Exception):
    """A representação recebida não é canônica, e o veredito não existe.

    A mensagem tem a forma `<categoria>: <lado>` ou
    `<categoria>: <lado>.<localizador>`. Ela diz **o que** viola a representação
    e **onde** — nunca o texto recebido, o trecho, o caractere ofensor, um
    deslocamento, um índice ou um comprimento.

    Isto **não é `False`**: é a ausência de veredito (D6-A). Quem chama **deve
    parar ou escalar**, nunca tratar como não-equivalência.
    """


# Categorias técnicas privadas. Fechadas, e **não** identificadores normativos
# novos de C: elas nomeiam as violações de D7 para efeito de mensagem.
_TERMINADOR_PROIBIDO = "terminador_proibido"
_QUEBRA_NA_BORDA = "quebra_na_borda"
_SEQUENCIA_DE_QUEBRAS_EXCESSIVA = "sequencia_de_quebras_excessiva"
_BRANCO_ADJACENTE_A_QUEBRA = "branco_adjacente_a_quebra"

# Lados fechados.
_APROVADO = "aprovado"
_RENDERIZADO = "renderizado"

# Localizadores fechados.
_INICIO = "inicio"
_FIM = "fim"
_ANTES = "antes"
_DEPOIS = "depois"

_QUEBRA = "\n"
_PARAGRAFO = "\n\n"
_ESPACO = " "

# D5: tudo o que não é `LF` e ainda assim termina linha. `CRLF` é recusado pela
# presença de `CR` — e **nunca** convertido.
_TERMINADORES_PROIBIDOS = (
    "\r",       # CR (U+000D) - cobre CRLF, que nunca e convertido
    "\u2028",   # LINE SEPARATOR
    "\u2029",   # PARAGRAPH SEPARATOR
    "\u0085",   # NEXT LINE
    "\u000b",   # LINE TABULATION
    "\u000c",   # FORM FEED
)

# D7: branco imediatamente colado à quebra, dos dois lados.
_BRANCOS_ANTES = (" \n", "\t\n")
_BRANCOS_DEPOIS = ("\n ", "\n\t")


def sao_textualmente_equivalentes(aprovado: str, renderizado: str) -> bool:
    """Decide a equivalência textual de `C-15b` entre os dois lados canônicos.

    Recebe o **fragmento aprovado já extraído** e a **renderização textual do
    mesmo fragmento**, ambos em **representação canônica**. Devolve `True`
    quando as normalizações são **exatamente iguais** e `False` quando diferem.

    Levanta `TypeError` quando um dos argumentos não é `str` — erro de contrato
    de chamada, verificado antes de qualquer outra coisa. Levanta
    `EquivalenciaNaoDeterminavel` quando algum dos lados viola a representação
    canônica: nesse caso **não há veredito**, e `False` **não** é devolvido.

    A validação percorre `aprovado` inteiro antes de `renderizado`, de modo que
    o lado aprovado tem **precedência** quando ambos são não canônicos. Dentro
    de cada lado vale a ordem de D7. A **primeira** violação encerra: nada é
    acumulado.
    """
    if not isinstance(aprovado, str):
        raise TypeError("aprovado: esperado str")
    if not isinstance(renderizado, str):
        raise TypeError("renderizado: esperado str")

    _exigir_canonico(aprovado, _APROVADO)
    _exigir_canonico(renderizado, _RENDERIZADO)

    return _normalizar_texto_canonico(aprovado) == _normalizar_texto_canonico(
        renderizado
    )


def _exigir_canonico(texto: str, lado: str) -> None:
    """Recusa `texto` se ele violar a representação canônica de D5 e D7.

    A ordem é fixa — terminador, borda, sequência excessiva, branco adjacente —
    e a borda avalia `inicio` antes de `fim`, como o branco avalia `antes` antes
    de `depois`. A `str` vazia **não viola nada** e permanece no domínio.
    """
    for proibido in _TERMINADORES_PROIBIDOS:
        if proibido in texto:
            raise _nao_determinavel(_TERMINADOR_PROIBIDO, lado)

    if texto.startswith(_QUEBRA):
        raise _nao_determinavel(_QUEBRA_NA_BORDA, lado, _INICIO)
    if texto.endswith(_QUEBRA):
        raise _nao_determinavel(_QUEBRA_NA_BORDA, lado, _FIM)

    if _QUEBRA * 3 in texto:
        raise _nao_determinavel(_SEQUENCIA_DE_QUEBRAS_EXCESSIVA, lado)

    for branco in _BRANCOS_ANTES:
        if branco in texto:
            raise _nao_determinavel(_BRANCO_ADJACENTE_A_QUEBRA, lado, _ANTES)
    for branco in _BRANCOS_DEPOIS:
        if branco in texto:
            raise _nao_determinavel(_BRANCO_ADJACENTE_A_QUEBRA, lado, _DEPOIS)


def _normalizar_texto_canonico(texto: str) -> str:
    """Aplica a normalização de `C-15b`: NFC e, depois, a dobra da quebra suave.

    A dobra é feita **por parágrafo**: o texto é particionado em `\\n\\n`, cada
    parte tem seus `LF` isolados trocados por **um** espaço, e as partes são
    reunidas com `\\n\\n` intacto. Substituir `LF` globalmente destruiria a
    fronteira de parágrafo real de D4.

    Só é chamada depois que **os dois** lados passaram por `_exigir_canonico`,
    de modo que aqui não existe corrida de três ou mais `LF`.
    """
    composto = unicodedata.normalize("NFC", texto)
    return _PARAGRAFO.join(
        paragrafo.replace(_QUEBRA, _ESPACO)
        for paragrafo in composto.split(_PARAGRAFO)
    )


def _nao_determinavel(
    categoria: str, lado: str, localizador: str | None = None
) -> EquivalenciaNaoDeterminavel:
    onde = lado if localizador is None else f"{lado}.{localizador}"
    return EquivalenciaNaoDeterminavel(f"{categoria}: {onde}")
