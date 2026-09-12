"""Recusa determinística de `null` e de `status: pendente` sobre valor terminal.

`C-7` **não** atribui significado positivo a `null` nem a `pendente`: a regra
normativa continua **fora** do índice, nas fontes já existentes. O que este
módulo materializa é **somente a fronteira de reconhecimento e recusa do valor
terminal** pertinente a `C-7` — e **nada além disso**.

**O terminal chega pronto.** A entrada é o **valor terminal já resolvido** pelo
chamador, na forma que `CY14` devolve: escalar, lista, mapa ou `None`. Este
módulo **não** resolve caminho, **não** rejulga gramática, **não** conhece a
decomposição usada, **não** lê a base autoritativa, **não** importa `yaml` e
**não** abre arquivo. Ter resolvido o caminho certo é **pré-condição do
chamador**.

**Chave inexistente não chega aqui como `None`.** `CY14` é literal nesse ponto:
**chave inexistente ≠ `null`**, e **atravessar `None` no meio do percurso é
falha estrutural**. Ambos falham **antes**, no resolver, e nunca alcançam esta
fronteira. O `None` que chega aqui é **terminal resolvido com sucesso**.

**Escopo espacial estreito: somente o terminal recebido.** A fronteira **não**
sobe ao pai, **não** lê chaves irmãs fora do terminal e **não** percorre
descendentes. Uma `str` cujo conteúdo seja `pendente` **não** é uma estrutura
pendente; um mapa cujo *valor* de alguma chave seja um mapa pendente **não** é
percorrido; e uma lista que contenha `None` ou um mapa pendente **não** é
inspecionada internamente.

**Tipo exato, como no resolver factual.** `type(valor) is dict` e
`type(valor["status"]) is str`. **Subclasse não é a forma canônica** desta
fronteira, porque uma subclasse pode redefinir `__contains__`, `__getitem__` ou
`__eq__` e decidir por conta própria o que a estrutura diz. A verificação de
tipo exato **precede** a consulta à chave, de modo que **nenhum `__contains__`
alheio é executado**.

**Comparação literal, sem tolerância.** Não há coerção, normalização Unicode,
`strip`, transformação de caixa nem tolerância de *whitespace*. `"Pendente"`,
`" pendente"`, `"pendente "` e `"pendente\\n"` **não** são a forma canônica.
Simetricamente, `None` permanece inequivocamente distinto de `False`, `0`,
`0.0`, `""`, `()`, `[]`, `{}`, `"null"` e `"None"`.

**Forma não canônica é devolvida, não julgada.** Um `dict` exato sem `status`,
um `status` que não seja `str` exata e um `status` textual diferente de
`pendente` **não** são `C-7` nesta fronteira: o valor volta **pelo próprio
objeto**. Isso **não** os declara válidos, admissíveis, formatáveis ou
aprovados — declara **apenas** que `C-7` não os recusou. A admissibilidade
pertence a `C-5`, a `C-6` e às fronteiras de validação apropriadas.

**Devolução por identidade.** No caso de sucesso o valor volta **pelo próprio
objeto**: sem cópia, sem cópia profunda, sem normalização, sem coerção, sem
ordenação e **sem mutação** da entrada.

**A mensagem não vaza.** Como esta fronteira toca valor factual real, a exceção
**não** carrega o valor recebido, o conteúdo de chave irmã, a chave concreta, o
caminho, um fragmento dele, uma posição, um comprimento, o `repr` ou o tipo
concreto. O vocabulário público é **fechado e tem exatamente dois termos**:
`nulo: valor` e `pendente: status`.

**Pureza.** O módulo importa **apenas** `annotations`: **zero `yaml`**, **zero
`collections`**, **zero módulo interno do projeto**, **zero I/O**, **zero
*filesystem***, **zero rede**, **zero variável de ambiente**, **zero relógio**,
**zero calendário**, **zero banco**, **zero cache**, **zero logging**, **zero
LLM**, **zero `try`/`except`**, **zero `raise from`**, **zero `global`/
`nonlocal`**, **zero estado mutável de módulo**, **zero normalização** e **zero
coerção**.

**RECUSAR NÃO É MATERIALIZAR `C-7`, E MUITO MENOS `C`.** Esta fronteira **não**
decide se existe *binding*, se o *binding* é **necessário**, mecanismo, origem,
fragmento, status do fragmento, candidatura ou aprovação; **não** decide
`resposta_aprovada_disponivel`, `CAMPO_INDISPONIVEL`, `E09`,
`pendencia_impeditiva`, handoff nem condição de ciclo; e **não** implementa
`S2-D8` (`C-12`). A consequência de `C-7` sobre um *binding* necessário a um
fragmento que se pretende `APROVADO` — o bloqueio do fragmento — pertence
**integralmente a consumidor futuro**. Esta fronteira não cria, não carrega nem
prova a existência do índice físico oficial, não avalia fragmento real, não
integra consumidor algum e, isoladamente, não materializa `C` nem prova a
integração completa de `C`.
"""

from __future__ import annotations

__all__ = [
    "ValorNuloOuPendente",
    "recusar_nulo_ou_pendente",
]


class ValorNuloOuPendente(Exception):
    """O valor terminal recebido é `null` ou estrutura com `status: pendente`.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **qual
    das duas formas** foi reconhecida e o localizador diz **onde** — nunca o
    valor recebido, o conteúdo de chave irmã, a chave concreta, o caminho, o
    `repr` ou o tipo concreto.

    Ela é **irmã**, e não parente, de `CaminhoYamlNaoResolvido`: aquela afirma
    que um caminho **não alcança valor**; esta afirma que o caminho **alcançou**
    um valor e que esse valor é **exatamente** uma das duas formas de `C-7`.

    Levantá-la **não** é `CAMPO_INDISPONIVEL`, **não** é `E09`, **não** é
    `pendencia_impeditiva`, **não** é handoff e **não** é decisão de ciclo. É um
    **fato sobre o valor**, não uma decisão de ciclo (`C-12`). Quem chama
    **deve parar ou escalar**.
    """


# Vocabulario publico fechado desta fronteira, na forma `<categoria>:
# <localizador>`. Sao exatamente duas categorias e dois localizadores, e nenhum
# deles e identificador normativo novo de `C`, evento ou componente.
_NULO = "nulo"
_PENDENTE = "pendente"
_VALOR = "valor"
_STATUS = "status"

# `_PENDENTE` e `_STATUS` acumulam, cada um, dois papeis que coincidem por
# construcao: `_PENDENTE` e a categoria da recusa **e** o rotulo literal
# comparado; `_STATUS` e o localizador da recusa **e** a unica chave examinada
# no terminal. A coincidencia e deliberada - a categoria tem o nome exato da
# condicao detectada, e o localizador tem o nome exato da chave inspecionada.


def recusar_nulo_ou_pendente(valor: object) -> object:
    """Recusa o terminal quando ele é `null` ou estrutura `status: pendente`.

    `valor` é o **terminal já resolvido** pelo chamador. A ordem é **fixa**:
    **1.** `None`; **2.** a estrutura canônica de pendência; **3.** devolução.

    Levanta `ValorNuloOuPendente("nulo: valor")` quando `valor is None`, e
    `ValorNuloOuPendente("pendente: status")` quando — e **somente** quando —
    todas estas condições valem ao mesmo tempo: `valor` é `dict` **exato**, a
    chave literal `status` está presente, o seu valor é `str` **exata** e essa
    `str` é exatamente `pendente`.

    Em qualquer outro caso devolve **o próprio objeto recebido**, por
    identidade — sem cópia, sem normalização, sem coerção, sem mutação e **sem
    juízo adicional**. Devolver **afirma somente** que `C-7` não recusou este
    valor: **não** afirma validade, admissibilidade, formatabilidade,
    aprovação, cobertura, disponibilidade comercial nem ausência de pendência
    futura.

    O exame é **estritamente terminal**: chaves irmãs, mapas descendentes e
    itens de lista **não** são percorridos. `{"x": None}`,
    `{"x": {"status": "pendente"}}`, `[None]` e `[{"status": "pendente"}]`
    **não** são `C-7` nesta fronteira.

    **RECUSAR NÃO É MATERIALIZAR `C-7`.** A aplicação contextual a um *binding*
    necessário, e a consequência sobre o status de um fragmento, pertencem a
    **consumidor futuro** — jamais a esta função.
    """
    if valor is None:
        raise _nulo_ou_pendente(_NULO, _VALOR)

    if type(valor) is dict and _STATUS in valor:
        status = valor[_STATUS]
        if type(status) is str and status == _PENDENTE:
            raise _nulo_ou_pendente(_PENDENTE, _STATUS)

    return valor


def _nulo_ou_pendente(categoria: str, localizador: str) -> ValorNuloOuPendente:
    return ValorNuloOuPendente(f"{categoria}: {localizador}")
