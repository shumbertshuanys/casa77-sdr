"""`SeletorFatos` — materialização dos fatos dos fragmentos já autorizados.

Esta fronteira **não escolhe o que responder**. A escolha — candidatura,
emissibilidade, alternativa concreta e a projeção final dos *witnesses* — já
aconteceu **a montante**, em **S2-D8** (§4.4.1). Aqui chega apenas a tupla
`fragmentos_autorizados`, e o trabalho é **um só**: materializar, para cada um
desses fragmentos, os fatos dos seus *bindings* `RENDERIZADO` e transportar o
texto canônico correspondente.

**Pureza.** **Zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero relógio**, **zero calendário**, **zero ambiente**, **zero logging**,
**zero *cache*** e **zero mutação** de qualquer entrada. Nada é aberto aqui: o
índice, a raiz factual e o mapa de textos chegam **já carregados** pelo
chamador. `knowledge/**` não é lido.

**Composição, nunca duplicação.** Cada juízo é delegado à fronteira que tem
autoridade sobre ele — `validar_indice` e `derivar_tokens_do_indice` para a
forma e a identidade do índice; as três linhas de `CY13` para caminho, contexto
e resolução; `recusar_nulo_ou_pendente` para `C-7`; os formatadores de `C-6`.
**Nenhum *parser*, resolver, formatador, gramática ou vocabulário paralelo é
escrito aqui.**

**O que esta fronteira NÃO é:**

| Não é | De quem é |
|---|---|
| segunda autoridade de consistência | `ValidadorConsistenciaBase` (§4.1.2) |
| autoridade de candidatura, emissibilidade ou alternativa | **S2-D8** (§4.4.1) |
| autoridade de status | o índice (`C-11`) |
| *renderer* | **não existe** (`PH11`) |
| redator | o LLM (§4.2) |
| validador de saída | `ValidadorResposta` (§4.1) |

**Status não é lido aqui.** Esta fronteira **não** consulta, projeta, compara ou
filtra o status de fragmento algum, e **não** importa a fronteira que o consulta.
A pré-condição é que a tupla recebida **já tenha sido autorizada** por S2-D8;
esta fronteira **não** a reaudita e **não** a corrige.

**`ASSERTIVA` não produz fato.** Um *binding* `ASSERTIVA` é **consistency-only**
(`C-5`, `C-5.1`): ele não materializa valor, não entra na saída e **não é
avaliado aqui** — o predicado não é sequer importado. Como o fato de origem
runtime só sustenta `ASSERTIVA` (`C-A2-V`), segue que **nenhuma verdade
operacional é afirmada nesta fronteira**: zero *snapshot* de runtime, zero
consulta de calendário, zero juízo de disponibilidade.

**Decompor não é renderizar.** O texto canônico é transportado **exatamente como
recebido**, *placeholder* incluído. Nada é substituído, concatenado, formatado
por *template* ou montado. **Não existe *renderer* aqui.**

**Fail-closed, sem resultado parcial.** Se um fragmento declarado autorizado
encontrar referente que não resolve, valor recusado por `C-7` ou formato que não
o representa, a exceção da fronteira de origem atravessa **intacta**. Isso
significa que o *witness* autorizado ficou **incoerente com a fotografia factual
recebida** — é falha de contrato do chamador, **não** caso de negócio, e **não**
é convertido em motivo conversacional, evento, alerta ou divergência.

**Zero valor comercial em `repr`.** `valor_formatado` e `texto` são *payload* de
runtime da redação, **não** material de log: ambos são declarados `repr=False`.
Os DTOs carregam, além deles, **somente identificadores e o referente
declarado**.

**Determinismo.** A ordem da saída é, e só é: a **ordem recebida** em
`fragmentos_autorizados`, depois a **ordem física** dos *bindings* do fragmento,
depois a **ordem física** da coleção iterada. Nada é ordenado, preferido ou
deduplicado aqui.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from casa77_sdr.response_format import (
    formatar_hora,
    formatar_inteiro,
    formatar_inteiro_agrupado,
    formatar_lista,
    formatar_simbolo_moeda,
    formatar_texto,
)
from casa77_sdr.response_index import validar_indice
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice
from casa77_sdr.response_null_pending import recusar_nulo_ou_pendente
from casa77_sdr.response_yaml_path_context import (
    validar_caminho_de_binding,
    validar_itera_sobre,
)
from casa77_sdr.response_yaml_resolve import resolver_caminho, resolver_itera_sobre

__all__ = [
    "FatoAutorizado",
    "ResultadoSelecaoFatos",
    "SelecaoNaoAvaliavel",
    "TextoAutorizado",
    "materializar_fatos_autorizados",
]


@dataclass(frozen=True, slots=True)
class FatoAutorizado:
    """Uma ocorrência materializada de um *binding* `RENDERIZADO`.

    Carrega a **proveniência completa** — o token do fragmento, as suas duas
    projeções estruturais, o nome do *binding*, o `caminho_yaml` declarado e o
    nome do formato declarado — e o **valor já formatado**.

    O **valor bruto não é transportado**: ele existe apenas transitoriamente,
    durante a aplicação de `C-7` e do formatador. Não há `raw`, *snapshot*,
    *hash* factual ou objeto do YAML aqui.

    `valor_formatado` é `repr=False`: ele é fato comercial destinado à redação,
    jamais material de log.
    """

    token: str
    rxx: str
    fragmento_id: str
    binding: str
    referente: str
    formato: str
    valor_formatado: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class TextoAutorizado:
    """O texto canônico de um fragmento autorizado, transportado como recebido.

    Vale igualmente para o fragmento **estático** e para o fragmento com
    *template*: **nenhum *placeholder* é substituído** e nada é concatenado.

    `texto` é `repr=False`: redação aprovada é *payload* da resposta, jamais
    material de log.
    """

    token: str
    rxx: str
    fragmento_id: str
    texto: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class ResultadoSelecaoFatos:
    """Saída estrutural da materialização, na ordem recebida.

    `fatos` — uma entrada por **ocorrência** de *binding* `RENDERIZADO`, na
    ordem `fragmento autorizado` → *binding* → item da coleção iterada.
    **Nenhuma deduplicação**: dois *bindings* que apontem para o mesmo referente
    produzem duas entradas, com proveniências distintas.

    `textos_autorizados` — **exatamente um** por fragmento recebido, na mesma
    ordem, com o texto canônico **literal**.

    Um fragmento **sem** *binding* `RENDERIZADO` contribui com **zero** fatos e
    **um** texto. Isso é **sucesso normal**, e **não** significa ausência de
    resposta: essa leitura pertence a **S2-D8**.
    """

    fatos: tuple[FatoAutorizado, ...]
    textos_autorizados: tuple[TextoAutorizado, ...]


class SelecaoNaoAvaliavel(Exception):
    """Erro de composição **próprio** desta fronteira.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o token recebido, o valor factual, o valor formatado, o texto, o `repr`, o
    tipo concreto, um índice numérico ou uma cardinalidade.

    Ela cobre **apenas** o que nenhuma fronteira existente julga: a forma da
    tupla de fragmentos autorizados, a pertinência de cada token ao domínio
    canônico do índice e a estrutura de transporte do mapa de textos. Toda outra
    invalidez pertence à fronteira de origem e atravessa **intacta**.
    """


# Despacho fechado de `C-6`. A **autoridade** do vocabulário de formato é
# `validar_indice` (`_FORMATOS`), que corre antes; esta tabela apenas liga o
# nome já validado a fronteira que o aplica. Nenhum formato é definido aqui.
_FORMATADORES = {
    "inteiro": formatar_inteiro,
    "inteiro_agrupado": formatar_inteiro_agrupado,
    "simbolo_moeda": formatar_simbolo_moeda,
    "hora": formatar_hora,
    "texto": formatar_texto,
    "lista": formatar_lista,
}

# Categorias privadas e fechadas de `SelecaoNaoAvaliavel`. Elas nomeiam o
# impedimento e **nao** sao vocabulario normativo novo: nenhum enum publico e
# criado para elas.
_TIPO_INVALIDO = "tipo_invalido"
_TOKEN_DESCONHECIDO = "token_desconhecido"
_DUPLICIDADE = "duplicidade"
_TEXTO_AUSENTE = "texto_ausente"

# Localizadores estruturais fechados. Nomeiam a **posicao da chamada**, jamais
# o conteudo recebido.
_TEXTOS = "textos"
_TEXTOS_ITEM = "textos.item"
_AUTORIZADOS = "fragmentos_autorizados"
_AUTORIZADOS_ITEM = "fragmentos_autorizados.item"

# Chaves do indice ja validado.
_RESPOSTAS = "respostas"
_FRAGMENTOS = "fragmentos"
_BINDINGS = "bindings"
_ID = "id"
_NOME = "nome"
_MECANISMO = "mecanismo"
_FORMATO = "formato"
_CAMINHO_YAML = "caminho_yaml"
_ITERA_SOBRE = "itera_sobre"
_SEPARADOR = "/"

_RENDERIZADO = "RENDERIZADO"

# Sentinela privada: o fragmento nao declara `itera_sobre`, logo nao existe item
# corrente algum. Jamais vocabulario publico.
_SEM_ITEM_CORRENTE = object()


def materializar_fatos_autorizados(
    indice: object,
    base: object,
    textos: object,
    fragmentos_autorizados: object,
) -> ResultadoSelecaoFatos:
    """Materializa os fatos dos fragmentos **já autorizados a montante**.

    `indice` é o índice **já carregado**; `base` é a **raiz factual já
    carregada**; `textos` é o mapa `token -> texto canônico` **já produzido pelo
    chamador**; `fragmentos_autorizados` é a tupla de tokens **já escolhida por
    S2-D8**. Esta fronteira **não abre arquivo algum** e **não reavalia a
    autorização**.

    A ordem é **fixa**: **1.** `validar_indice` — `IndiceInvalido` atravessa
    intacta; **2.** `derivar_tokens_do_indice` — `ProjecaoDeIdentidadeInvalida`
    atravessa intacta e **fixa o domínio canônico de tokens**; **3.** o tipo do
    mapa de textos; **4.** a forma da tupla de autorizados — `tuple` exata,
    itens `str` exatos, **sem duplicata** e **todos pertencentes ao domínio**;
    **5.** o percurso, na **ordem recebida**.

    Por fragmento autorizado: o texto canônico é exigido no mapa e transportado
    **literalmente**; a coleção de `itera_sobre`, quando declarada, é obtida por
    `validar_itera_sobre` + `resolver_itera_sobre`; e cada *binding*
    `RENDERIZADO` é materializado na ordem física. *Bindings* de outro mecanismo
    são **ignorados sem juízo** — eles não produzem fato, não são avaliados e
    não aparecem na saída.

    A cardinalidade da materialização vem do **caminho**, exatamente como na
    fronteira de consistência: um *binding* **absoluto** é resolvido **uma vez
    contra a raiz**, mesmo com coleção vazia; um *binding* **relativo** é
    resolvido **uma vez por item corrente**, de modo que coleção vazia produz
    **zero ocorrências** dele.

    Levanta `SelecaoNaoAvaliavel` com `tipo_invalido` (`textos`, `textos.item`,
    `fragmentos_autorizados`, `fragmentos_autorizados.item`),
    `token_desconhecido` e `duplicidade` (`fragmentos_autorizados.item`) e
    `texto_ausente` (`textos`). Toda outra invalidez — `IndiceInvalido`,
    `ProjecaoDeIdentidadeInvalida`, `CaminhoYamlInvalido`,
    `CaminhoYamlContextoInvalido`, `CaminhoYamlNaoResolvido`,
    `ValorNuloOuPendente`, `FormatoInaplicavel` — atravessa **intacta**, e
    **nenhum resultado parcial é devolvido**. **Nada é capturado aqui.**

    **MATERIALIZAR NÃO É DECIDIR O QUE DIZER.** O resultado é estrutural e
    determinístico; a escolha do que responder pertence a **S2-D8** e a redação
    pertence ao LLM.
    """
    validar_indice(indice)
    tokens_do_indice = derivar_tokens_do_indice(indice)

    if type(textos) is not dict:
        raise _nao_avaliavel(_TIPO_INVALIDO, _TEXTOS)

    _exigir_tupla_de_tokens(fragmentos_autorizados, tokens_do_indice)

    fragmento_por_token = _indexar_fragmentos(indice)

    fatos: list[FatoAutorizado] = []
    textos_autorizados: list[TextoAutorizado] = []

    for token in fragmentos_autorizados:
        rxx, fragmento = fragmento_por_token[token]
        fragmento_id = fragmento[_ID]

        textos_autorizados.append(
            TextoAutorizado(
                token,
                rxx,
                fragmento_id,
                _exigir_texto(textos, token),
            )
        )

        itens = _colecao_do_fragmento(base, fragmento)

        for binding in fragmento[_BINDINGS]:
            if binding[_MECANISMO] != _RENDERIZADO:
                continue

            for valor_formatado in _materializar_binding(base, binding, itens):
                fatos.append(
                    FatoAutorizado(
                        token,
                        rxx,
                        fragmento_id,
                        binding[_NOME],
                        binding[_CAMINHO_YAML],
                        binding[_FORMATO],
                        valor_formatado,
                    )
                )

    return ResultadoSelecaoFatos(
        fatos=tuple(fatos),
        textos_autorizados=tuple(textos_autorizados),
    )


def _exigir_tupla_de_tokens(
    fragmentos_autorizados: object,
    tokens_do_indice: tuple[str, ...],
) -> None:
    """Exige a forma da tupla de autorizados contra o domínio canônico.

    `tuple` **exata** — `list`, `set`, gerador ou subclasse são recusados, para
    que a **ordem recebida** seja um contrato e não um acidente. Cada item é
    `str` **exata**, pertence ao domínio derivado do índice e **não se repete**:
    token duplicado é **erro de contrato do chamador**, porque a deduplicação da
    projeção pertence a S2-D8.
    """
    if type(fragmentos_autorizados) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _AUTORIZADOS)

    dominio = frozenset(tokens_do_indice)
    vistos: set[str] = set()

    for token in fragmentos_autorizados:
        if type(token) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _AUTORIZADOS_ITEM)
        if token not in dominio:
            raise _nao_avaliavel(_TOKEN_DESCONHECIDO, _AUTORIZADOS_ITEM)
        if token in vistos:
            raise _nao_avaliavel(_DUPLICIDADE, _AUTORIZADOS_ITEM)
        vistos.add(token)


def _indexar_fragmentos(indice: dict) -> dict[str, tuple[str, dict]]:
    """Projeta `token -> (rxx, fragmento)` do índice **já validado**.

    O token é **composto** a partir do `Rxx` e do `id` declarados, exatamente
    como em `C-A5-T1`/`C-A5-T2`. Ele **não é parseado de volta**: a autoridade
    sobre o domínio de identidades é `derivar_tokens_do_indice`, e aqui só se
    refaz a mesma composição para localizar o fragmento.
    """
    return {
        resposta[_ID] + _SEPARADOR + fragmento[_ID]: (resposta[_ID], fragmento)
        for resposta in indice[_RESPOSTAS]
        for fragmento in resposta[_FRAGMENTOS]
    }


def _colecao_do_fragmento(base: object, fragmento: dict) -> object:
    """Resolve `itera_sobre`, quando declarado, pelas fronteiras de `CY13`.

    Devolve a **própria lista** da base — nunca uma cópia, nunca ordenada —, ou
    `_SEM_ITEM_CORRENTE` quando o fragmento não itera. `CaminhoYamlInvalido`,
    `CaminhoYamlContextoInvalido` e `CaminhoYamlNaoResolvido` atravessam
    intactas.
    """
    if _ITERA_SOBRE not in fragmento:
        return _SEM_ITEM_CORRENTE

    return resolver_itera_sobre(base, validar_itera_sobre(fragmento[_ITERA_SOBRE]))


def _materializar_binding(
    base: object,
    binding: dict,
    itens: object,
) -> tuple[str, ...]:
    """Materializa **todas** as ocorrências de um *binding* `RENDERIZADO`.

    O discriminante da cardinalidade é o `relativo` **já produzido** por
    `validar_caminho_de_binding`: nenhum caminho é reparseado aqui, e nenhuma
    gramática, prefixo ou heurística textual é reconhecida nesta fronteira.

    *Binding* **absoluto** — inclusive em fragmento que itera — produz
    **exatamente uma** ocorrência, contra a raiz, qualquer que seja a
    cardinalidade da coleção. *Binding* **relativo** produz **uma por item
    corrente**, na ordem física da coleção, e **zero** quando ela é vazia.
    """
    itera = itens is not _SEM_ITEM_CORRENTE
    decomposicao = validar_caminho_de_binding(
        binding[_CAMINHO_YAML], fragmento_itera=itera
    )
    relativo = decomposicao[0]

    if not itera or relativo is False:
        return (_materializar_ocorrencia(base, binding, decomposicao, _SEM_ITEM_CORRENTE),)

    return tuple(
        _materializar_ocorrencia(base, binding, decomposicao, item) for item in itens
    )


def _materializar_ocorrencia(
    base: object,
    binding: dict,
    decomposicao: object,
    item: object,
) -> str:
    """Materializa **uma** ocorrência — resolução, `C-7` e formato declarado.

    A cadeia é fixa e **nada é capturado**: resolver o caminho, aplicar `C-7` e
    aplicar o formatador declarado. `CaminhoYamlNaoResolvido`,
    `ValorNuloOuPendente` e `FormatoInaplicavel` atravessam **intactas** — um
    fragmento declarado autorizado que falhe aqui está incoerente com a
    fotografia factual recebida, e a falha fecha.

    O valor bruto vive **somente nesta pilha**: só o valor formatado sai.
    """
    if item is _SEM_ITEM_CORRENTE:
        valor = resolver_caminho(base, decomposicao)
    else:
        valor = resolver_caminho(base, decomposicao, item_corrente=item)

    return _FORMATADORES[binding[_FORMATO]](recusar_nulo_ou_pendente(valor))


def _exigir_texto(textos: dict, token: str) -> str:
    """Exige o texto canônico do token no mapa de transporte recebido."""
    if token not in textos:
        raise _nao_avaliavel(_TEXTO_AUSENTE, _TEXTOS)

    texto = textos[token]
    if type(texto) is not str:
        raise _nao_avaliavel(_TIPO_INVALIDO, _TEXTOS_ITEM)

    return texto


def _nao_avaliavel(categoria: str, localizador: str) -> SelecaoNaoAvaliavel:
    return SelecaoNaoAvaliavel(f"{categoria}: {localizador}")
