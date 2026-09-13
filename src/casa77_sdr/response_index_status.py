"""Consulta de status por fragmento, na autoridade estruturada (`C-11`).

Esta fronteira responde **uma única pergunta**: qual é o status que o índice
declara para um token `<Rxx>/<Fxx>`. A autoridade de status por fragmento é
`knowledge/indice-respostas-aprovadas.yaml` (`C-11`); esta fronteira **lê essa
autoridade** e **não** a substitui, não a redefine e não a complementa.

**Nenhum vocabulário paralelo de status vive aqui.** O conjunto fechado de
rótulos, a sua grafia e a recusa de qualquer rótulo fora dele pertencem
**integralmente** a `validar_indice` (`casa77_sdr.response_index`, `C-3`), que
é chamada **antes** de qualquer leitura. Um índice que declare rótulo fora do
vocabulário falha lá, como `IndiceInvalido`, e **não** ganha categoria própria
aqui. Este módulo devolve **o rótulo que está no índice já validado** — nunca um
rótulo que ele próprio conheça.

**A identidade também não é reanalisada.** O domínio de tokens admissível é
**exatamente** o produzido por `derivar_tokens_do_indice`
(`casa77_sdr.response_index_tokens`, `C-A5-T1`). A gramática `<Rxx>/<Fxx>`
**não** é reparseada aqui: um token fora desse domínio é recusado por não
pertencer à projeção, não por análise léxica local.

**Zero valor padrão.** Não existe *fallback*, não existe status presumido e
nenhum rótulo é inferido. **O Markdown não é consultado**: este módulo não
importa fronteira alguma de status do Markdown, não lê `knowledge/**` e não
conhece rótulo de cabeçalho, `status-fragmento` ou propagação `SP1`–`SP7`.

**Pureza.** **Zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero relógio**, **zero ambiente**, **zero logging**, **zero *cache*** e
**zero mutação** do índice recebido, que é lido por projeção.

**CONSULTAR STATUS NÃO É DECIDIR EMISSÃO.** O sucesso afirma **somente** qual
rótulo o índice declara para aquele fragmento. Ele **não** decide
emissibilidade, candidatura, cobertura, consistência factual, disponibilidade
de referente, `resposta_aprovada_disponivel`, `pendencia_impeditiva`, `E09`,
handoff nem condição de ciclo (`C-12`; `S2-D8`).
"""

from __future__ import annotations

from casa77_sdr.response_index import validar_indice
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice

__all__ = ["StatusNaoLocalizado", "consultar_status"]


class StatusNaoLocalizado(Exception):
    """O token não pertence ao domínio de identidade do índice validado.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o token recebido, o seu `repr`, o tipo concreto, um índice numérico ou uma
    cardinalidade.

    Ela **não** é invalidez do índice: estrutura e vocabulário são julgados
    **antes**, por `validar_indice` e `derivar_tokens_do_indice`, cujas exceções
    atravessam esta fronteira **intactas**.
    """


_TIPO_INVALIDO = "tipo_invalido"
_TOKEN_INEXISTENTE = "token_inexistente"
_TOKEN = "token"

_RESPOSTAS = "respostas"
_ID = "id"
_FRAGMENTOS = "fragmentos"
_STATUS_DO_FRAGMENTO = "status"
_SEPARADOR = "/"


def consultar_status(indice: object, token: str) -> str:
    """Devolve o status que `indice` declara para `token`.

    A ordem é **fixa** e começa pelas autoridades existentes: **1.**
    `validar_indice(indice)` — uma `IndiceInvalido` atravessa **intacta**;
    **2.** `derivar_tokens_do_indice(indice)` — uma
    `ProjecaoDeIdentidadeInvalida` atravessa **intacta**; **3.** o tipo de
    `token`; **4.** a pertinência de `token` ao domínio projetado; **5.** a
    localização na estrutura física já validada; **6.** a devolução do rótulo
    **que está no índice**.

    A estrutura entra pelos portões **antes** do token deliberadamente: um
    índice inválido é defeito de base e precisa falhar como tal, mesmo quando a
    chamada também traz token errado.

    Levanta `StatusNaoLocalizado` com `tipo_invalido` quando `token` não é `str`
    **exata**, e com `token_inexistente` quando ele não pertence ao domínio
    projetado. **Não existe valor padrão**: nada é presumido, nada é inferido e
    o Markdown não é consultado.

    **CONSULTAR STATUS NÃO É DECIDIR EMISSÃO.** O rótulo devolvido é a
    autoridade de status daquele fragmento e **nada mais** — não afirma
    consistência factual, disponibilidade de referente, cobertura,
    candidatura nem emissibilidade.
    """
    validar_indice(indice)
    dominio = derivar_tokens_do_indice(indice)

    if type(token) is not str:
        raise _nao_localizado(_TIPO_INVALIDO, _TOKEN)

    if token not in dominio:
        raise _nao_localizado(_TOKEN_INEXISTENTE, _TOKEN)

    for resposta in indice[_RESPOSTAS]:
        rxx = resposta[_ID]
        for fragmento in resposta[_FRAGMENTOS]:
            if rxx + _SEPARADOR + fragmento[_ID] == token:
                return fragmento[_STATUS_DO_FRAGMENTO]

    # `dominio` é derivado desta mesma estrutura já validada: um token presente
    # nele e ausente aqui seria defeito interno, nunca invalidez do documento.
    raise RuntimeError("invariante_estrutural")


def _nao_localizado(categoria: str, localizador: str) -> StatusNaoLocalizado:
    return StatusNaoLocalizado(f"{categoria}: {localizador}")
