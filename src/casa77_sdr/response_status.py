"""Canonicalização determinística de rótulo de status já extraído.

`C-A1-ST` fixa a correspondência entre o rótulo de status **escrito no
Markdown** e o status canônico de **`C-3`** — vocabulário **fechado** de três
valores: `APROVADO`, `AGUARDA_APROVACAO` e `BLOQUEADO`, **sem quarto status** e
**sem valor padrão**. Desse contrato, **apenas três linhas** foram arbitradas
como **tradução automática**: `C-A1-ST1`, `C-A1-ST2` e `C-A1-ST3`. Este módulo
materializa **essas três, e nada mais**.

**O rótulo chega pronto.** A função **não** extrai o rótulo do Markdown, **não**
analisa Markdown, **não** localiza a linha de status, **não** decide de qual
fragmento o rótulo veio e **não** verifica se esse fragmento existe. **A origem
correta do rótulo é pré-condição do chamador** e não é verificável nesta
fronteira sem transformá-la em extrator — que ela deliberadamente não é.

**`PARCIAL` não é traduzido aqui, e isso não é lacuna normativa.** `C-A1-ST4` já
arbitrou que `PARCIAL` é **descrição agregada do Markdown**, **não** é quarto
status de `C-3` e **exige mapeamento explícito no nível dos fragmentos
emitíveis**. Esta microentrega **não** implementa esse mapeamento; por isso
`PARCIAL` é recusado como `rotulo_nao_mapeado` — categoria que significa **"não
existe tradução automática nesta fronteira"**, jamais **"não arbitrado"**.

**`BLOQUEADO` como rótulo simples também não recebe tradução automática.**
`C-A1-ST5` trata especificamente de `BLOQUEADO` **em nota interna**, e nota
interna **não cria fragmento** e **não cria status**. Esta função recebe apenas
uma `str` e **não tem contexto** para decidir se o rótulo veio de nota interna,
de fragmento emitível ou de outro lugar. Inventar aqui `BLOQUEADO` →
`BLOQUEADO` seria criar regra normativa nova — ainda que `BLOQUEADO` seja, ele
próprio, status válido de `C-3` em outros contextos.

**Comparação literal.** O rótulo é comparado por **igualdade nativa exata de
`str`** contra as três linhas arbitradas: **sem `strip`, `lower`, `upper`,
`casefold`, `NFC`, `NFD`, `unicodedata`, colapso de espaços, substituição de
espaço inquebrável, tolerância de acento ou tolerância de caixa**. Uma variante
que não seja **exatamente** igual a uma das três linhas é recusada.

**`str` exata, nunca subclasse.** O rótulo precisa ser do **tipo `str`
exatamente**; uma subclasse de `str` é **recusada antes de qualquer consulta à
tabela**. A razão é técnica: uma subclasse pode redefinir `__eq__` e `__hash__`
e, com isso, decidir por conta própria quando se considera igual a uma entrada
da tabela fechada — a pertença deixaria de ser decidida aqui. O rótulo também
**não** é convertido: não há `str(...)`, `repr` nem coerção de espécie alguma.

Falha é **fail-closed** e imediata. A mensagem carrega **categoria e
localizador**, nunca o rótulo recebido, o conteúdo, o `repr`, o tipo concreto,
um comprimento, um índice ou o caractere ofensor. A entrada **não é alterada**.

**CANONICALIZAR STATUS NÃO É MATERIALIZAR `C`.** Um retorno bem-sucedido
significa **somente** que o rótulo fornecido corresponde exatamente a uma das
três traduções automáticas arbitradas. Ele **não** prova que exista fragmento,
que a origem do rótulo esteja correta, que algo seja emitível, que o índice real
exista ou seja válido, que o Markdown tenha sido integralmente extraído, que a
bijeção física tenha ocorrido, nem que **`C-A1-ST6`**, **`C-A1-ST7`**,
**`C-A1-ST8`**, **`C-A1-ST9`** ou **`C-A1-ST10`** estejam satisfeitas. **A
autoridade de status não migra aqui**: enquanto as cinco condições de
`C-A1-ST6`–`C-A1-ST10` não valerem integralmente,
`knowledge/respostas-aprovadas.md` **continua a autoridade de status** (`C-11`),
e o status **não é removido do Markdown**. Nada aqui prova equivalência `C-15`,
validade de *bindings* ou aprovação humana; e **cobertura estrutural não é
emissibilidade** (`C-A4-G8`).
"""

from __future__ import annotations

__all__ = ["StatusNaoCanonicalizavel", "canonicalizar_status"]


class StatusNaoCanonicalizavel(Exception):
    """O rótulo recebido não tem tradução automática nesta fronteira.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** impede a canonicalização e o localizador diz **onde** — nunca o
    rótulo recebido, o conteúdo, o `repr`, o tipo concreto, um comprimento ou um
    índice.

    Levantá-la significa **apenas** que não existe tradução automática para o
    rótulo dado. **Não** significa que o caso seja normativamente indefinido:
    `C-A1-ST4` e `C-A1-ST5` estão arbitrados, e é justamente por isso que
    `PARCIAL` e `BLOQUEADO` não são traduzidos aqui.
    """


# Categorias tecnicas privadas e fechadas. Elas nomeiam o impedimento e **nao**
# sao identificadores normativos novos de `C`.
_TIPO_INVALIDO = "tipo_invalido"
_ROTULO_NAO_MAPEADO = "rotulo_nao_mapeado"

# Localizador unico: a fronteira tem um unico argumento.
_ROTULO = "rotulo"

# Status canonicos de `C-3` alcancaveis por traducao automatica. `BLOQUEADO`
# pertence a `C-3`, mas nenhuma linha de `C-A1-ST` o produz automaticamente a
# partir de um rotulo simples, e por isso ele nao figura como imagem aqui.
_APROVADO = "APROVADO"
_AGUARDA_APROVACAO = "AGUARDA_APROVACAO"

# Tabela fechada das tres traducoes automaticas arbitradas. E uma `tuple` de
# pares, e nao um mapa: a fronteira nao precisa de hash, e nada aqui pode ser
# mutado em tempo de execucao. `C-A1-ST4` (`PARCIAL`) e `C-A1-ST5` (`BLOQUEADO`
# em nota interna) **nao** tem entrada, deliberadamente.
_TRADUCOES_AUTOMATICAS = (
    # C-A1-ST1
    ("APROVADO", _APROVADO),
    # C-A1-ST2
    ("AGUARDA APROVAÇÃO", _AGUARDA_APROVACAO),
    # C-A1-ST3 — o sufixo de handoff e instrucao operacional e fica fora de `C`
    # (C-2f, C-5.1); por isso ele **nao** e transportado pela saida.
    ("APROVADO com handoff obrigatório", _APROVADO),
)


def canonicalizar_status(rotulo: str) -> str:
    """Traduz um rótulo de status já extraído para o status canônico de `C-3`.

    Devolve o status canônico quando `rotulo` é **exatamente** uma das três
    linhas com tradução automática arbitrada:

    | `C-A1-ST` | rótulo recebido | status devolvido |
    |---|---|---|
    | `C-A1-ST1` | `APROVADO` | `APROVADO` |
    | `C-A1-ST2` | `AGUARDA APROVAÇÃO` | `AGUARDA_APROVACAO` |
    | `C-A1-ST3` | `APROVADO com handoff obrigatório` | `APROVADO` |

    O **sufixo de handoff não é transportado** pela saída: ele é instrução
    operacional e fica fora de `C` (C-2f, C-5.1).

    Levanta `StatusNaoCanonicalizavel` em qualquer outro caso. A ordem de
    validação é **fixa**: **1.** tipo do rótulo; **2.** pertença à tabela
    automática; **3.** retorno. A **primeira** violação encerra, e **nada é
    acumulado**.

    O rótulo precisa ser do tipo `str` **exatamente** — subclasse de `str` é
    recusada como `tipo_invalido`, **antes** de qualquer comparação com a
    tabela. A comparação é **literal**: nenhuma normalização, coerção,
    conversão ou tolerância precede a igualdade.

    Um rótulo `str` fora das três linhas recebe `rotulo_nao_mapeado` — o que
    inclui, entre outros, `PARCIAL` (`C-A1-ST4`, que exige **mapeamento
    explícito no nível dos fragmentos emitíveis**, não implementado aqui),
    `BLOQUEADO` (`C-A1-ST5` trata de **nota interna**, e esta fronteira não
    recebe esse contexto), o próprio `AGUARDA_APROVACAO` já canônico, a `str`
    vazia e toda variante de caixa, espaçamento ou acentuação.

    **CANONICALIZAR STATUS NÃO É MATERIALIZAR `C`.** O sucesso afirma **apenas**
    a correspondência exata com uma linha arbitrada — nada sobre fragmento,
    emissibilidade, índice real, bijeção física, `C-A1-ST6`–`C-A1-ST10`,
    equivalência `C-15`, *bindings* ou aprovação humana. **A autoridade de
    status não migra**: `knowledge/respostas-aprovadas.md` continua a autoridade
    (`C-11`).
    """
    if type(rotulo) is not str:
        raise _nao_canonicalizavel(_TIPO_INVALIDO)

    for rotulo_markdown, status_canonico in _TRADUCOES_AUTOMATICAS:
        if rotulo == rotulo_markdown:
            return status_canonico

    raise _nao_canonicalizavel(_ROTULO_NAO_MAPEADO)


def _nao_canonicalizavel(categoria: str) -> StatusNaoCanonicalizavel:
    return StatusNaoCanonicalizavel(f"{categoria}: {_ROTULO}")
