"""Validação estrutural **contextual** de `caminho_yaml` — linha 2 de `CY13`.

`CY13` separou **três** responsabilidades: o **parser da gramática**, a
**validação estrutural do índice** e o **resolver**. A linha 1 já está
materializada em `casa77_sdr.response_yaml_path`. Este módulo materializa
**exatamente a segunda, e nada mais** — e, dentro dela, **somente** as duas
regras que `CY13` e `CY12` de fato enunciam:

**Regra A.** Um `caminho_yaml` **relativo** de *binding* só é admissível quando o
fragmento declara `itera_sobre`, porque a raiz de um caminho relativo é **o item
corrente da coleção percorrida**. Sem `itera_sobre` não existe item corrente e,
portanto, o caminho não tem raiz alguma.

**Regra B.** O próprio `itera_sobre` **nunca** pode ser relativo (`CY12`): ele
usa a **forma ABSOLUTA** da mesma gramática-base, pois é ele quem **estabelece**
o item corrente — não pode ancorar-se num contexto que ainda não existe.

**A gramática não pertence a esta fronteira.** Ela pertence **exclusivamente** a
`analisar_caminho_yaml`, importado aqui sob nome privado. Este módulo **não**
procura `@`, **não** usa `startswith`, **não** relê a `str`, **não** normaliza,
**não** reimplementa a gramática e **não** faz uma segunda interpretação da
entrada. O predicado de forma relativa é obtido **unicamente** do resultado do
parser.

**O parser vem primeiro, sempre.** Cada função pública chama
`analisar_caminho_yaml` **uma única vez**, **antes** de qualquer juízo
contextual. Se a `str` for gramaticalmente inválida, a `CaminhoYamlInvalido`
original **atravessa intacta**: **zero `try`**, **zero `except`**, **zero
`raise from`**, **zero *wrapping*** e **zero recategorização**. A classe da
exceção e a sua mensagem chegam a quem chamou **exatamente** como o parser as
produziu. Por consequência, uma entrada que viole a gramática **e** traga um
contexto de tipo inválido falha como `CaminhoYamlInvalido` — a precedência é do
parser.

**O sucesso repassa o resultado do parser.** As funções devolvem **o mesmo**
`(relativo, segmentos)` recebido: **sem reparsear**, **sem reconstruir
segmentos**, **sem converter em `list`**, **sem DTO**, **sem `dataclass`**, **sem
`NamedTuple`**, **sem `Enum`** e **sem `dict`**. Isso permite que o futuro
resolver consuma a decomposição **sem tocar de novo na `str`**.

**Vocabulário contextual fechado.** Existem **exatamente três** falhas próprias
desta fronteira — `tipo_invalido: contexto`,
`relativo_sem_itera_sobre: caminho_yaml` e `arroba_em_itera_sobre: itera_sobre`
—, todas na forma `<categoria>: <localizador>`. A mensagem **nunca** carrega o
caminho recebido, um fragmento da entrada, o tipo concreto do contexto, o
`repr`, uma posição, um índice, um *offset*, um comprimento ou uma
cardinalidade.

**`CaminhoYamlContextoInvalido` é independente de `CaminhoYamlInvalido`.** Uma
diz que a `str` **não é um caminho**; a outra diz que um caminho **legítimo está
no lugar errado**. Quem chama distingue as duas **sem** inspecionar mensagem.

**Pureza.** O módulo importa **exatamente duas** coisas: `annotations` e o
parser. **Zero `re`**, **zero `unicodedata`**, **zero YAML**, **zero JSON**,
**zero `pathlib`**, **zero `os`**, **zero I/O**, **zero *filesystem***, **zero
rede**, **zero LLM**, **zero relógio**, **zero aleatoriedade**, **zero variável
de ambiente**, **zero banco**, **zero cache**, **zero logging**, **zero estado
mutável de módulo**, **zero `global`/`nonlocal`**, **zero `assert`**, **zero
`try`/`except`**, **zero `raise from`**, **zero `eval`/`exec`**, **zero
normalização** e **zero coerção**. A entrada **não é alterada**.

**VALIDAR O CONTEXTO NÃO É RESOLVER E NÃO É MATERIALIZAR `C`.** Um retorno
bem-sucedido afirma **somente** que a `str` satisfaz a gramática e que a sua
forma — absoluta ou relativa — é admissível na posição declarada. Ele **não**
lê o YAML factual, **não** abre `knowledge/**`, **não** verifica existência de
chave, **não** executa seletor, **não** conta *matches*, **não** confere se
`itera_sobre` termina em coleção, **não** percorre o índice, **não** substitui
`validar_indice` e **não** conhece fato comercial algum. Esta fronteira **não
executa nem prova a sua própria integração a `E1`**, **não executa nem substitui
a linha 3 de `CY13` — o resolver**, não aplica nem substitui `C-7`, não cria nem
prova a existência de `knowledge/indice-respostas-aprovadas.yaml`, não decide
nem migra a autoridade de status — externa a ela (`C-11`) — e, isoladamente,
não materializa `C` nem prova a integração completa de `C`.
"""

from __future__ import annotations

from casa77_sdr.response_yaml_path import (
    analisar_caminho_yaml as _analisar_caminho_yaml,
)

__all__ = [
    "CaminhoYamlContextoInvalido",
    "validar_caminho_de_binding",
    "validar_itera_sobre",
]


class CaminhoYamlContextoInvalido(Exception):
    """O caminho é gramatical, mas a sua forma é inadmissível nesta posição.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **qual**
    regra contextual foi violada e o localizador diz **em que construção do
    índice** — nunca o caminho recebido, um fragmento dele, o tipo concreto do
    contexto, o `repr`, uma posição, um índice, um *offset*, um comprimento ou
    uma cardinalidade observada.

    Ela é **irmã**, e não parente, de `CaminhoYamlInvalido`: aquela recusa a
    `str` como caminho; esta aceita o caminho e recusa **o lugar**. Levantá-la
    **não** afirma coisa alguma sobre existência de chave no YAML, *match* de
    seletor, resolução, terminal `null`, `C-7` ou índice físico — nada disso
    pertence a esta fronteira.
    """


# Categorias tecnicas privadas e fechadas desta fronteira. Elas nomeiam a regra
# contextual violada e **nao** sao identificadores normativos novos de `C`. Sao
# exatamente tres.
_TIPO_INVALIDO = "tipo_invalido"
_RELATIVO_SEM_ITERA_SOBRE = "relativo_sem_itera_sobre"
_ARROBA_EM_ITERA_SOBRE = "arroba_em_itera_sobre"

# Localizadores contextuais fechados. Eles nomeiam **a construcao do indice**
# onde a regra foi violada, jamais o conteudo recebido.
_CONTEXTO = "contexto"
_CAMINHO_YAML = "caminho_yaml"
_ITERA_SOBRE = "itera_sobre"


def validar_caminho_de_binding(
    caminho: str,
    *,
    fragmento_itera: bool,
) -> tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]:
    """Valida `caminho` como `caminho_yaml` de um *binding*, no seu contexto.

    `fragmento_itera` diz — e diz **somente** — se o fragmento que hospeda o
    *binding* declara `itera_sobre`. Ele é **keyword-only** justamente para que
    a chamada nomeie o contexto e nunca o passe por acidente posicional.

    A ordem de validação é **fixa**: **1.** o parser analisa `caminho`;
    **2.** uma `CaminhoYamlInvalido` atravessa **intacta**; **3.** só então o
    tipo de `fragmento_itera` é exigido como `bool` **exato**; **4.** só então a
    regra contextual é aplicada. Um caminho gramaticalmente inválido, portanto,
    falha como `CaminhoYamlInvalido` **mesmo que** o contexto também esteja
    errado.

    Devolve **o mesmo** `(relativo, segmentos)` produzido pelo parser, sem
    reparsear e sem reconstruir coisa alguma.

    Levanta `CaminhoYamlInvalido` — propagada do parser, sem transformação — e
    `CaminhoYamlContextoInvalido` com duas categorias: `tipo_invalido` quando
    `fragmento_itera` não é `bool` exato, e `relativo_sem_itera_sobre` quando o
    caminho é **relativo** e o fragmento **não** declara `itera_sobre`, pois aí
    não existe item corrente que sirva de raiz.

    Um caminho **absoluto** é admissível **nas duas** situações: iterar não
    proíbe endereçar a raiz do YAML.

    **VALIDAR O CONTEXTO NÃO É RESOLVER.** O sucesso afirma **somente** que a
    forma do caminho cabe nesta posição — nada sobre existência de chave,
    *match* de seletor, resolução, terminal, `C-7` ou índice físico.
    """
    resultado = _analisar_caminho_yaml(caminho)

    if type(fragmento_itera) is not bool:
        raise _invalido(_TIPO_INVALIDO, _CONTEXTO)

    if resultado[0] is True and fragmento_itera is False:
        raise _invalido(_RELATIVO_SEM_ITERA_SOBRE, _CAMINHO_YAML)

    return resultado


def validar_itera_sobre(
    caminho: str,
) -> tuple[bool, tuple[tuple[str, tuple[str, str] | None], ...]]:
    """Valida `caminho` como o `itera_sobre` de um fragmento.

    `CY12` é literal: `itera_sobre` usa a **forma ABSOLUTA** da mesma
    gramática-base e **`@` é PROIBIDO** nele. A razão é estrutural — é o
    `itera_sobre` que **estabelece** o item corrente, de modo que ele não pode
    ancorar-se num item corrente que ainda não existe.

    A ordem é **fixa**: **1.** o parser analisa `caminho`; **2.** uma
    `CaminhoYamlInvalido` atravessa **intacta**; **3.** só então a forma
    relativa é recusada. Não há contexto adicional a receber: a proibição é
    incondicional, e por isso esta função **não** tem parâmetro de contexto.

    Devolve **o mesmo** `(relativo, segmentos)` produzido pelo parser — com a
    forma necessariamente absoluta no sucesso.

    Levanta `CaminhoYamlInvalido` — propagada do parser, sem transformação — e
    `CaminhoYamlContextoInvalido` com a categoria `arroba_em_itera_sobre`
    quando o caminho é relativo, inclusive no caso de `@` isolado (`CY11`).

    **VALIDAR O CONTEXTO NÃO É RESOLVER.** O sucesso afirma **somente** que a
    forma é absoluta — nada sobre a coleção existir, ser de fato uma coleção,
    estar vazia ou terminar em mapa, escalar ou `null`. Esse juízo pertence ao
    resolver, que esta fronteira **não executa nem substitui**.
    """
    resultado = _analisar_caminho_yaml(caminho)

    if resultado[0] is True:
        raise _invalido(_ARROBA_EM_ITERA_SOBRE, _ITERA_SOBRE)

    return resultado


def _invalido(categoria: str, localizador: str) -> CaminhoYamlContextoInvalido:
    return CaminhoYamlContextoInvalido(f"{categoria}: {localizador}")
