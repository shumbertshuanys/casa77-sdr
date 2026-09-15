"""Validação estrutural pura do futuro mapa de grupos de cobertura — `R2`.

Este módulo valida a **forma** de uma estrutura já analisada que pretende ser o
artefato futuro do **caminho reservado** `knowledge/mapa-cobertura.yaml`. Ele
**não cria** esse arquivo, **não o lê**, **não o descobre** e **não conhece
caminho algum**: a entrada é uma estrutura Python já em memória.

**O conteúdo do mapa NÃO existe e NÃO é criado aqui.** Esta fronteira materializa
**apenas a representação estrutural genérica** de `R2-1`–`R2-7` (§4.4.1). Ela
**não** associa nenhum `AssuntoComercial` a nenhum `Rxx`/`Fxx`, **não** decide
grupo, **não** decide ordem concreta e **não** contém uma única linha de mapa. A
associação real depende de **decisão humana futura** e permanece ausente.

A forma validada é esta, e somente esta::

    assuntos:
      - assunto: <AssuntoComercial>
        grupos:
          - alternativas:
              - rxx: <Rxx>
                fragmento: <Fxx>

**O esqueleto é fechado em todos os níveis.** A raiz aceita **somente**
`assuntos`; o item de assunto, **somente** `assunto` e `grupos`; o grupo,
**somente** `alternativas`; a alternativa, **somente** `rxx` e `fragmento`.
Logo `priority` (**SF-D4-4**), `texto`, `status`, `binding`, `caminho_yaml`,
`predicado`, `formato` e qualquer valor comercial **não são representáveis** —
`R2-3`: o mapa **referencia**, ele **não copia** o que já vive no índice de `C`
ou no YAML.

**`R2-1` é um mapeamento TOTAL.** O vocabulário fechado de `AssuntoComercial`
aparece **inteiro**: os **54** valores, cada um **exatamente uma vez**. Assunto
**ausente fecha**, e assunto **repetido fecha**. Isso não é zelo: a
respondibilidade de `R2-5` é decidida **por assunto**, e um assunto que
simplesmente não aparece no artefato é **indistinguível** de um assunto
esquecido. A totalidade obriga a declaração explícita — **`grupos: []`** diz
"sem cobertura" **de propósito**, e a omissão deixa de ser um silêncio
ambíguo.

**Cardinalidades literais.** `R2-1`: cada assunto declara **0..N** grupos — a
lista vazia é **válida**, e é a forma canônica de "nenhum grupo". `R2-2`: cada
grupo contém **1..N** alternativas — a lista vazia **fecha**. `R2-6`:
**`ASSUNTO_NAO_CLASSIFICADO` tem zero grupos por definição** — ele está
**presente exatamente uma vez**, como todos os demais, e o seu `grupos`
**precisa ser a lista vazia**; declarar grupo para ele **fecha**.

**A totalidade é estrutural, nunca conteúdo.** Exigir que os 54 valores
apareçam **não** cria cobertura, **não** associa assunto a `Rxx`/`Fxx` e **não**
antecipa decisão alguma: um mapa em que **todos** os assuntos declaram
`grupos: []` é **estruturalmente válido** e **semanticamente vazio**.

**Ordem.** A ordem física declarada das listas é **preservada integralmente**.
Esta fronteira **não ordena**, **não reordena**, **não prefere** e **não
deduplica** — ela **não devolve projeção alguma** e **não altera a estrutura
recebida**. A ordem declarada é o que **SF-D4-2**, **SF-D4-3** e **SF-D4-8**
consomem no futuro; o desempate é a própria ordem, nunca um campo novo.

**Semântica é de quem consome.** `R2-4` — **conjunção entre grupos**,
**disjunção dentro do grupo** — e `R2-5` — respondibilidade — **não são
avaliadas aqui**. Elas pertencem ao produtor **S2-D8**, que **não existe**.

**O que esta fronteira deliberadamente NÃO faz.** Ela **não** consulta status
(**D8-F1**), **não** resolve *binding*, **não** aplica formatador, **não**
avalia `ASSERTIVA` (**D8-F3**), **não** avalia `MD-15'`, **não** consulta
calendário ou runtime, **não** implementa **D8-F**, **não** decide cobertura,
**não** escolhe *witness*, **não** produz `fragmentos_autorizados`, **não**
produz `E09` e **não** torna **S2-D8** operacional.

**Duas propriedades NÃO são invalidade estrutural.** Uma alternativa que
referencie fragmento com *binding* **`RUNTIME_AUTORITATIVO`** ou fragmento que
declare **`itera_sobre`** é **estruturalmente válida**: `R2-1`–`R2-7` não as
mencionam, e transformá-las em invalidade seria criar restrição inexistente. O
que essas propriedades significam para **emissibilidade** pertence a **D8-F**, na
etapa posterior.

**A deduplicação não é antecipada.** Alternativa repetida dentro do grupo, grupo
repetido dentro do assunto e a mesma alternativa em assuntos distintos **não são
proibidos**: nenhuma regra de `R2-1`–`R2-7` os proíbe, e a deduplicação da tupla
global pertence a **SF-D4-9**, a jusante. A **única** unicidade aplicada é a do
`assunto`, e ela decorre do próprio `R2-1`: um mapeamento com duas entradas para
a mesma chave **deixa de ser um mapeamento** — não se saberia quais são "os"
grupos daquele assunto.

**Vocabulário reutilizado, nunca duplicado.** O vocabulário de assunto é o enum
`AssuntoComercial` de **AJ2** (§6.3), com os seus **54** valores. **Nenhum enum
paralelo é criado** e nenhum valor é redeclarado aqui.

**A conferência de referências alcança IDENTIDADE, e só ela.** O domínio contra
o qual as alternativas são conferidas é o **domínio canônico de identidade**
derivado por `derivar_tokens_do_indice`, que **não substitui `validar_indice`**:
ele lê apenas a projeção mínima — raiz, `respostas`, o `id` da resposta e o `id`
do fragmento — e **não julga** `status`, *bindings*, `itera_sobre`, `formato`,
`predicado`, mecanismo, origem, fato runtime nem chave desconhecida. Logo, um
índice **defeituoso fora dessa projeção** atravessa esta fronteira **sem ser
julgado**, e isso é correto: aqui se prova **existência da referência**, não
validade do índice. A **validação estrutural integral do índice**, que é o que
`D8-CI2` exige, pertence à **futura cadeia de S2-D8** e deve **reutilizar
`validar_indice`** — esta fronteira **não a substitui e não a prova**.

***Fail-closed*, sem resultado parcial.** A **primeira** violação encerra e nada
é acumulado. A mensagem de `MapaCoberturaInvalido` tem a forma
`<categoria>: <localizador>` e carrega **apenas** categoria e posição
estrutural — **nunca** o assunto recebido, o `Rxx`, o fragmento, o texto, o
valor, PII ou qualquer conteúdo do YAML.
"""

from __future__ import annotations

from typing import Any

from casa77_sdr.interpretation import AssuntoComercial
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice

__all__ = [
    "MapaCoberturaInvalido",
    "conferir_referencias",
    "validar_mapa_cobertura",
]


class MapaCoberturaInvalido(Exception):
    """A estrutura recebida não satisfaz o contrato estrutural de `R2`.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **onde**, por posição estrutural —
    nunca o assunto, o `Rxx`, o fragmento, o valor, o `repr`, o tipo concreto ou
    qualquer trecho do conteúdo recebido.

    Artefato que sequer pôde ser lido ou analisado **não** é caso desta exceção:
    isso é `MapaCoberturaIlegivel`, levantada por `coverage_map_load`.
    """


# Categorias fechadas de invalidade. Nenhuma delas descreve conteudo.
_TIPO_INVALIDO = "tipo_invalido"
_CAMPO_AUSENTE = "campo_ausente"
_CAMPO_DESCONHECIDO = "campo_desconhecido"
_VALOR_INVALIDO = "valor_invalido"
_DUPLICIDADE = "duplicidade"
_COMBINACAO_INVALIDA = "combinacao_invalida"
_REFERENCIA_PENDURADA = "referencia_pendurada"

# Localizador estrutural da totalidade. Ele nomeia **o item que falta**, jamais
# **qual** assunto falta: revelar o nome seria vazar conteudo do mapa.
_ASSUNTOS_ITEM = "assuntos.item"

# Esqueleto fechado, nivel a nivel. Campo fora destes conjuntos e recusado: e o
# que torna `priority`, texto, status, *binding* e valor comercial
# estruturalmente irrepresentaveis (R2-3, SF-D4-4).
_CHAVES_RAIZ = frozenset({"assuntos"})
_CHAVES_ASSUNTO = frozenset({"assunto", "grupos"})
_CHAVES_GRUPO = frozenset({"alternativas"})
_CHAVES_ALTERNATIVA = frozenset({"rxx", "fragmento"})

# Vocabulario REUTILIZADO de AJ2 (§6.3). Nenhum enum paralelo e criado, e
# nenhum valor e redeclarado: o enum continua sendo a autoridade.
_VALORES_DE_ASSUNTO = frozenset(membro.value for membro in AssuntoComercial)
_ASSUNTO_SEM_GRUPOS = AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO.value

# Separador normativo da identidade canonica (C-A5-T2). Ele so aparece aqui como
# **composicao** do token ja arbitrado; a gramatica de `Rxx` e de `Fxx` continua
# fora deste modulo.
_SEPARADOR = "/"

# O fragmento de lacuna NAO pertence a `R2`: o registro externo a SF-D4 fecha
# que nenhum grupo ficticio de lacuna e criado, e §4.1.5 (PE) o trata como
# contribuicao mandataria das acoes, jamais como alternativa de cobertura.
_ALTERNATIVA_PROIBIDA = f"R03{_SEPARADOR}F1"


def validar_mapa_cobertura(mapa: object) -> None:
    """Valida a forma de `mapa`, já analisado, e devolve `None` se ela for válida.

    A estrutura recebida **não é lida por caminho**, **não é copiada** e **não é
    alterada**. Levanta `MapaCoberturaInvalido` na **primeira** violação
    encontrada, **sem resultado parcial**.

    Ela julga **exclusivamente forma**: esqueleto fechado, tipos, vocabulário de
    assunto, **totalidade e unicidade** do vocabulário, cardinalidades de `R2-1`
    e `R2-2`, a regra de `R2-6` e a proibição estrutural do fragmento de lacuna
    como alternativa. Ela **não** julga existência da referência — isso é
    `conferir_referencias`, que precisa do índice —, **não** julga
    emissibilidade, cobertura, status, *binding*, `ASSERTIVA`, formato,
    calendário ou runtime.

    O mapa é **total**: os **54** valores de `AssuntoComercial`, cada um
    **exatamente uma vez**. Um mapa **sem nenhum assunto declarado** é
    **inválido**, e um mapa a que falte **um único** assunto também. A ordem em
    que eles aparecem **não é julgada**.
    """
    _exigir_mapeamento(mapa, "<raiz>")
    _exigir_chaves(mapa, _CHAVES_RAIZ, _CHAVES_RAIZ, "<raiz>")

    assuntos = mapa["assuntos"]
    if not isinstance(assuntos, list):
        raise _erro(_TIPO_INVALIDO, "assuntos")

    vistos: set[str] = set()
    for posicao, item in enumerate(assuntos):
        _validar_assunto(item, f"assuntos[{posicao}]", vistos)

    # R2-1 como mapeamento **TOTAL**: cada valor ja foi provado pertencente ao
    # vocabulario e nao repetido, entao basta comparar os conjuntos. A mensagem
    # diz que **falta item**, e **nunca qual**.
    if vistos != _VALORES_DE_ASSUNTO:
        raise _erro(_CAMPO_AUSENTE, _ASSUNTOS_ITEM)


def conferir_referencias(mapa: object, indice: object) -> None:
    """Confere que **toda** alternativa referencia fragmento **existente**.

    `indice` é a estrutura do índice de `C` **já carregada pelo chamador**: esta
    fronteira **não abre `knowledge/**`** e **não conhece caminho**. O domínio
    conferido é o **domínio canônico de identidade**, derivado por
    `derivar_tokens_do_indice` (`C-A5-T1`–`C-A5-T5`) — **a autoridade da
    identidade continua lá**, e nenhuma gramática de `Rxx` ou de `Fxx` é escrita
    aqui.

    **`derivar_tokens_do_indice` não substitui `validar_indice`.** Ele lê apenas
    a projeção mínima de identidade, de modo que `status`, *bindings*,
    `itera_sobre`, `formato`, `predicado`, mecanismo, origem e chave
    desconhecida **não são julgados por esta função** — um índice defeituoso
    **fora** dessa projeção passa por aqui **sem veredito**.

    O mapa é **revalidado** antes de ser percorrido: percorrer estrutura não
    validada seria abrir mão do *fail-closed*. Em seguida, cada alternativa é
    composta em `<rxx>/<fragmento>` e conferida contra o domínio.

    **Referência pendurada fecha** como `MapaCoberturaInvalido` de categoria
    `referencia_pendurada` — é a **Classe I** de `R2-7` e `D8-CI4`, tratada pelo
    caminho de falha já vigente, **nunca** convertida em `E09`, pendência,
    handoff ou decisão de cobertura (**D8-CI14**).

    Quando a **própria projeção de identidade** é inviável, a
    `ProjecaoDeIdentidadeInvalida` **atravessa intacta**: o defeito é do índice,
    não do mapa, e o chamador precisa distinguir os dois. Isso **não prova
    `D8-CI2`**: a **validação estrutural integral do índice** que `D8-CI2` exige
    pertence à **futura cadeia de S2-D8** e deve **reutilizar `validar_indice`**.

    Esta conferência **não** julga status, *binding*, `ASSERTIVA`, formato,
    emissibilidade (**D8-F**) nem cobertura (**R2-5**). Existência da referência,
    e nada além disso.
    """
    validar_mapa_cobertura(mapa)

    dominio = frozenset(derivar_tokens_do_indice(indice))

    for onde, rxx, fragmento in _percorrer_alternativas(mapa):
        if f"{rxx}{_SEPARADOR}{fragmento}" not in dominio:
            raise _erro(_REFERENCIA_PENDURADA, onde)


def _validar_assunto(item: Any, onde: str, vistos: set[str]) -> None:
    _exigir_mapeamento(item, onde)
    _exigir_chaves(item, _CHAVES_ASSUNTO, _CHAVES_ASSUNTO, onde)

    # Tipo **exato**: a chave semantica do mapa nao pode ser decidida por uma
    # subclasse de `str` que redefina `__eq__` ou `__hash__`. E a mesma defesa
    # local ja adotada pela fronteira de identidade do indice, e ela **nao**
    # altera AJ2 nem o enum. Na forma fisica — YAML — o assunto e sempre texto.
    assunto = item["assunto"]
    if type(assunto) is not str:
        raise _erro(_TIPO_INVALIDO, f"{onde}.assunto")
    if assunto not in _VALORES_DE_ASSUNTO:
        raise _erro(_VALOR_INVALIDO, f"{onde}.assunto")
    if assunto in vistos:
        # R2-1 fala de **um** mapeamento por assunto: duas entradas para a mesma
        # chave tornariam indefinido qual e o conjunto de grupos dele.
        raise _erro(_DUPLICIDADE, f"{onde}.assunto")
    vistos.add(assunto)

    # R2-1: 0..N grupos. A lista existe sempre; vazia e **valida**.
    grupos = item["grupos"]
    if not isinstance(grupos, list):
        raise _erro(_TIPO_INVALIDO, f"{onde}.grupos")

    # R2-6: `ASSUNTO_NAO_CLASSIFICADO` tem **zero grupos por definicao**. Ele
    # esta **presente**, como todos — a totalidade o exige —, e o seu `grupos`
    # precisa ser a **lista vazia**; declarar grupo para ele fecha.
    if assunto == _ASSUNTO_SEM_GRUPOS and grupos:
        raise _erro(_COMBINACAO_INVALIDA, f"{onde}.grupos")

    for posicao, grupo in enumerate(grupos):
        _validar_grupo(grupo, f"{onde}.grupos[{posicao}]")


def _validar_grupo(grupo: Any, onde: str) -> None:
    _exigir_mapeamento(grupo, onde)
    _exigir_chaves(grupo, _CHAVES_GRUPO, _CHAVES_GRUPO, onde)

    alternativas = grupo["alternativas"]
    if not isinstance(alternativas, list):
        raise _erro(_TIPO_INVALIDO, f"{onde}.alternativas")
    # R2-2: 1..N alternativas. Grupo sem alternativa nao e disjuncao de nada.
    if not alternativas:
        raise _erro(_VALOR_INVALIDO, f"{onde}.alternativas")

    for posicao, alternativa in enumerate(alternativas):
        _validar_alternativa(alternativa, f"{onde}.alternativas[{posicao}]")


def _validar_alternativa(alternativa: Any, onde: str) -> None:
    _exigir_mapeamento(alternativa, onde)
    _exigir_chaves(
        alternativa, _CHAVES_ALTERNATIVA, _CHAVES_ALTERNATIVA, onde
    )

    rxx = _exigir_componente(alternativa["rxx"], f"{onde}.rxx")
    fragmento = _exigir_componente(alternativa["fragmento"], f"{onde}.fragmento")

    if f"{rxx}{_SEPARADOR}{fragmento}" == _ALTERNATIVA_PROIBIDA:
        raise _erro(_COMBINACAO_INVALIDA, onde)


def _exigir_componente(valor: object, onde: str) -> str:
    """Exige a forma mínima que torna a composição do token inequívoca.

    **Isto não é gramática de `Rxx` nem de `Fxx`.** Essa autoridade pertence a
    `C-A5` e à fronteira de identidade do índice, e a existência real da
    referência é provada por `conferir_referencias` contra o domínio canônico.
    O que se exige aqui é o mínimo sem o qual a composição `<rxx>/<fragmento>`
    deixaria de ser unívoca: **`str` exata**, **não vazia** e **sem o separador
    normativo dentro do componente** (`C-A5-T3`).
    """
    if type(valor) is not str:
        raise _erro(_TIPO_INVALIDO, onde)
    if not valor or _SEPARADOR in valor:
        raise _erro(_VALOR_INVALIDO, onde)
    return valor


def _percorrer_alternativas(mapa: Any) -> list[tuple[str, str, str]]:
    """Percorre as alternativas **na ordem física declarada**, sem alterar nada.

    A travessia é privada de propósito: **nenhuma projeção é exportada**. Quem
    consome alternativa é o produtor **S2-D8**, que não existe, e antecipar a
    sua entrada seria implementar cobertura nesta fronteira.
    """
    encontradas: list[tuple[str, str, str]] = []
    for posicao, item in enumerate(mapa["assuntos"]):
        onde_assunto = f"assuntos[{posicao}]"
        for posicao_grupo, grupo in enumerate(item["grupos"]):
            onde_grupo = f"{onde_assunto}.grupos[{posicao_grupo}]"
            for posicao_alt, alternativa in enumerate(grupo["alternativas"]):
                encontradas.append(
                    (
                        f"{onde_grupo}.alternativas[{posicao_alt}]",
                        alternativa["rxx"],
                        alternativa["fragmento"],
                    )
                )
    return encontradas


def _exigir_mapeamento(valor: object, onde: str) -> None:
    if not isinstance(valor, dict):
        raise _erro(_TIPO_INVALIDO, onde)


def _exigir_chaves(
    mapeamento: Any,
    permitidas: frozenset[str],
    obrigatorias: frozenset[str],
    onde: str,
) -> None:
    chaves = set(mapeamento)
    if not obrigatorias <= chaves:
        raise _erro(_CAMPO_AUSENTE, onde)
    if not chaves <= permitidas:
        raise _erro(_CAMPO_DESCONHECIDO, onde)


def _erro(categoria: str, localizador: str) -> MapaCoberturaInvalido:
    return MapaCoberturaInvalido(f"{categoria}: {localizador}")
