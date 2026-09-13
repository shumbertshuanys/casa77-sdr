"""`ValidadorConsistenciaBase` — primeiro consumidor operacional de `C`.

Esta fronteira confere, **fragmento a fragmento**, se o corpus aprovado e a base
factual estão **mutuamente consistentes** sob o contrato `C` (§2.3): o
*template* é fisicamente bem formado, cada *binding* `RENDERIZADO` resolve para
um valor que o formato declarado consegue representar, e cada `ASSERTIVA` de
origem `YAML` se sustenta sobre a base recebida (**F3**).

**Pureza.** **Zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero relógio**, **zero calendário**, **zero ambiente**, **zero logging**,
**zero *cache*** e **zero mutação** de qualquer entrada. Nada é aberto aqui: o
índice, a raiz factual e o mapa de textos chegam **já carregados** pelo
chamador.

**Composição, nunca duplicação.** Cada juízo é delegado à fronteira que tem
autoridade sobre ele — `validar_indice` e `derivar_tokens_do_indice` para a
forma e a identidade do índice; `consultar_status` para o status; a gramática de
*placeholder* de `decompor_template`; as três linhas de `CY13` para caminho,
contexto e resolução; `recusar_nulo_ou_pendente` para `C-7`; os formatadores de
`C-6`; `avaliar_assertiva` para o predicado. **Nenhum *parser*, resolver,
formatador, gramática ou vocabulário paralelo é escrito aqui.**

**Identidade.** A unidade de validação é o fragmento emitível `<Rxx>/<Fxx>`
(`C-A5-T1`). `rxx` e `fragmento_id` aparecem nos resultados como **projeções
estruturais** dessa identidade, para localizar o defeito — o `Rxx` agregado
**não** volta a ser a identidade principal.

**Status não filtra consistência.** Todos os fragmentos do índice físico são
conferidos, qualquer que seja o seu status. Um fragmento que aguarda aprovação
pode estar factualmente consistente ou inconsistente, e isso **não** o torna
emitível. `status_por_fragmento` é informação **separada**, projetada da
autoridade do índice (`C-11`).

**Três espécies distintas de desfecho, que esta fronteira não mistura:**

| Espécie | O que é | Como sai |
|---|---|---|
| **Classe II** | base **avaliável** e **divergente** (`D8-CII`) | `Divergencia` |
| **`C-7`** | referente **indisponível** — `null` ou `status: pendente` | `ReferenteIndisponivel` |
| **Classe I** | base **não avaliável** (`D8-CI`) — erro de contrato | **exceção propagada** |

`C-7` **não** é divergência: o fato não contradiz a redação, ele simplesmente
não está disponível. E Classe I **nunca** vira resultado: a exceção da fronteira
de origem atravessa **intacta**, e **não existe resultado parcial**.

**`C-15` não é repetido em runtime.** A equivalência textual entre redação
aprovada e renderização foi o **gate de materialização** do *template*
(`C-A1-ST10`), já cumprido sobre o corpus físico. Aqui o *template* carrega
*placeholders*, não valores: uma mudança legítima de valor no YAML **não é
divergência** enquanto o referente resolver, `C-7` permitir, o formato se
aplicar e o *binding* continuar correspondendo ao *template*. Por isso esta
fronteira **não** chama `sao_textualmente_equivalentes`, **não** guarda
*snapshot*, valor anterior, *hash* factual ou texto renderizado congelado.

**Decompor não é renderizar.** A decomposição do *template* é **validada e
descartada**: nada é concatenado, nenhum valor é inserido, nenhum texto final é
montado. **Não existe *renderer* aqui** (`PH11`).

**`RUNTIME_AUTORITATIVO` está fora do escopo factual desta fronteira.** Ela não
recebe *snapshot* de runtime, não consulta calendário e não decide
disponibilidade. Cada *binding* de origem runtime é apenas **registrado** em
`bindings_runtime_nao_avaliados`, sem divergência e sem indisponibilidade —
**nenhuma verdade operacional é afirmada**.

**Fronteira `C` × `S2-D8` (`C-12`).** Esta fronteira produz **resultado
estrutural** e **nada mais**. Ela **não** decide emissibilidade, candidatura,
cobertura, `resposta_aprovada_disponivel`, `pendencia_impeditiva`,
`CAMPO_INDISPONIVEL`, `SEM_RESPOSTA_APROVADA_EMITIVEL`, `E09`, grupo `R2`,
escolha de alternativa, handoff, alerta, condição de ciclo ou resposta
conversacional. O consumo desse resultado pertence a **S2-D8**.

**Zero valor comercial na saída.** Nenhum DTO carrega valor factual, `repr`,
texto de resposta, *template*, valor formatado, segredo ou mensagem livre —
apenas **identificadores e referentes** (`C-1h`–`C-1m`, `C-15e`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from casa77_sdr.response_assertion import avaliar_assertiva
from casa77_sdr.response_format import (
    FormatoInaplicavel,
    formatar_hora,
    formatar_inteiro,
    formatar_inteiro_agrupado,
    formatar_lista,
    formatar_simbolo_moeda,
    formatar_texto,
)
from casa77_sdr.response_index import validar_indice
from casa77_sdr.response_index_status import consultar_status
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice
from casa77_sdr.response_null_pending import (
    ValorNuloOuPendente,
    recusar_nulo_ou_pendente,
)
from casa77_sdr.response_placeholder import decompor_template
from casa77_sdr.response_yaml_path_context import (
    validar_caminho_de_binding,
    validar_itera_sobre,
)
from casa77_sdr.response_yaml_resolve import resolver_caminho, resolver_itera_sobre

__all__ = [
    "CategoriaDivergencia",
    "ConsistenciaNaoAvaliavel",
    "Divergencia",
    "ReferenteIndisponivel",
    "ResultadoConsistencia",
    "validar_consistencia_base",
]


class CategoriaDivergencia(StrEnum):
    """Vocabulário **fechado** das divergências de Classe II desta fronteira.

    `ASSERTIVA_FALSA` — a `ASSERTIVA` é avaliável e o predicado **não** se
    sustenta sobre a base recebida. É o exemplo canônico de `D8-CII`.

    `FORMATO_INAPLICAVEL` — o referente resolveu e `C-7` **não** o recusou, mas
    o formato declarado no *binding* **não consegue representar** aquele fato.
    O fragmento fica inconsistente: o *template* não pode ser honrado sob o
    contrato declarado.

    Nenhum dos dois é `C-7`, e nenhum dos dois é motivo de ciclo, `E09` ou
    handoff — a consequência conversacional pertence a **S2-D8** (`C-12`).
    """

    ASSERTIVA_FALSA = "ASSERTIVA_FALSA"
    FORMATO_INAPLICAVEL = "FORMATO_INAPLICAVEL"


@dataclass(frozen=True, slots=True)
class Divergencia:
    """Um *binding* avaliável cuja avaliação acusou divergência (Classe II).

    Carrega **somente identificadores e o referente declarado**: o token do
    fragmento, as suas duas projeções estruturais, o nome do *binding*, o seu
    mecanismo, a sua origem e o `caminho_yaml` declarado. **Nunca** o valor
    resolvido, o `repr`, o texto aprovado, o *template* ou o valor formatado.
    """

    token: str
    rxx: str
    fragmento_id: str
    binding: str
    mecanismo: str
    origem: str
    referente: str
    categoria: CategoriaDivergencia


@dataclass(frozen=True, slots=True)
class ReferenteIndisponivel:
    """Um *binding* cujo referente foi recusado por `C-7`.

    **Isto não é divergência.** O fato não contradiz a redação: ele está
    ausente (`null`) ou explicitamente pendente na base. A saída **não**
    distingue os dois casos — ambos pertencem, futuramente, ao mesmo motivo
    conceitual de `S2-D8`, que esta fronteira **não** produz.

    O DTO afirma **exatamente** isto: *este binding necessário encontrou
    referente indisponível*. Nada sobre `CAMPO_INDISPONIVEL`, `E09`, pendência,
    alerta, handoff ou consequência conversacional.
    """

    token: str
    rxx: str
    fragmento_id: str
    binding: str
    mecanismo: str
    origem: str
    referente: str


@dataclass(frozen=True, slots=True)
class ResultadoConsistencia:
    """Resultado **estrutural** da conferência, na ordem física do índice.

    `divergencias` — **somente** Classe II, na ordem `Rxx` → fragmento →
    *binding*.

    `referentes_indisponiveis` — **somente** fatos `C-7`, na mesma ordem. Eles
    **não** aparecem em `divergencias` nem em `tokens_divergentes`.

    `tokens_divergentes` — os tokens que têm **alguma** `Divergencia`, pela
    **primeira ocorrência** e na ordem física. `C-7` **não** entra aqui.

    `status_por_fragmento` — projeção da autoridade de status do índice
    (`C-11`), produzida **exclusivamente** por `consultar_status`, com um par
    `(token, status)` por fragmento, na ordem física.

    `bindings_runtime_nao_avaliados` — registro auditável, na forma
    `<token>.<nome>`, dos *bindings* deixados **fora do escopo factual** desta
    entrega, na ordem física.

    **Nenhum campo decide emissibilidade.**
    """

    divergencias: tuple[Divergencia, ...]
    referentes_indisponiveis: tuple[ReferenteIndisponivel, ...]
    tokens_divergentes: tuple[str, ...]
    status_por_fragmento: tuple[tuple[str, str], ...]
    bindings_runtime_nao_avaliados: tuple[str, ...]


class ConsistenciaNaoAvaliavel(Exception):
    """Erro de composição **próprio** desta fronteira — Classe I (`D8-CI`).

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o token, o texto, o valor recebido, o `repr`, o tipo concreto, um índice
    numérico ou uma cardinalidade.

    Ela cobre **apenas** o que nenhuma fronteira existente julga: a estrutura de
    transporte do mapa de textos e a ausência de texto para um token do índice.
    Toda outra invalidez pertence à fronteira de origem e atravessa **intacta**.
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

# Categorias fechadas de `ConsistenciaNaoAvaliavel`.
_TIPO_INVALIDO = "tipo_invalido"
_TEXTO_AUSENTE = "texto_ausente"
_TEXTOS = "textos"
_TEXTOS_ITEM = "textos.item"

# Chaves do índice já validado.
_RESPOSTAS = "respostas"
_FRAGMENTOS = "fragmentos"
_BINDINGS = "bindings"
_ID = "id"
_NOME = "nome"
_MECANISMO = "mecanismo"
_ORIGEM = "origem"
_FORMATO = "formato"
_PREDICADO = "predicado"
_CAMINHO_YAML = "caminho_yaml"
_ITERA_SOBRE = "itera_sobre"
_SEPARADOR = "/"
_PONTO = "."

_RENDERIZADO = "RENDERIZADO"
_RUNTIME_AUTORITATIVO = "RUNTIME_AUTORITATIVO"

# Desfechos internos da avaliação de um *binding*. São **sentinelas privadas**,
# jamais vocabulário público: o vocabulário público de divergência é
# `CategoriaDivergencia`.
_CONSISTENTE = object()
_FORA_DO_ESCOPO_FACTUAL = object()
_INDISPONIVEL = object()
_SEM_ITEM_CORRENTE = object()


def validar_consistencia_base(
    indice: object,
    base: object,
    textos: object,
) -> ResultadoConsistencia:
    """Confere o corpus aprovado contra a base factual recebida (**F3**).

    `indice` é o índice **já carregado**; `base` é a **raiz factual já
    carregada**; `textos` é o mapa `token -> texto canônico` **já produzido pelo
    chamador**. Esta fronteira **não abre arquivo algum**.

    A ordem é **fixa**: **1.** `validar_indice` — `IndiceInvalido` atravessa
    intacta; **2.** `derivar_tokens_do_indice` — `ProjecaoDeIdentidadeInvalida`
    atravessa intacta; **3.** o tipo do mapa de textos; **4.** o percurso, na
    ordem física `Rxx` → fragmento → *binding*. A raiz factual **não** ganha
    portão próprio aqui: a sua forma é exigida pelo resolver de `CY13`, que é a
    autoridade sobre ela, e a recusa sai como `CaminhoYamlNaoResolvido`.

    Por fragmento: o status é projetado por `consultar_status`; o texto é
    exigido no mapa; o *template* é validado por `decompor_template` **e
    descartado**; e então cada *binding* é avaliado na ordem física.

    Quando o fragmento declara `itera_sobre`, a coleção é obtida por
    `validar_itera_sobre` + `resolver_itera_sobre`, e a cardinalidade da
    avaliação de cada *binding* é decidida pelo **caminho**: um *binding*
    **absoluto** é avaliado **uma única vez contra a raiz**, mesmo com coleção
    vazia, porque um fato global não depende da cardinalidade da coleção; um
    *binding* **relativo** é avaliado **por item corrente**, parando no
    **primeiro** desfecho não consistente daquele *binding* — a identidade do
    resultado é o *binding*, não o item. Com coleção vazia, portanto, um
    *binding* relativo não tem item corrente algum a avaliar, e isso **não** é
    juízo operacional aqui.

    Levanta `ConsistenciaNaoAvaliavel` com `tipo_invalido` (`textos`,
    `textos.item`) e `texto_ausente` (`textos`). Toda outra invalidez —
    `IndiceInvalido`, `ProjecaoDeIdentidadeInvalida`, `CaminhoYamlInvalido`,
    `CaminhoYamlContextoInvalido`, `CaminhoYamlNaoResolvido`,
    `AssertivaNaoAvaliavel`, `PlaceholderInvalido` — atravessa **intacta**, e
    **nenhum resultado parcial é devolvido**. As **únicas** capturas funcionais
    são `ValorNuloOuPendente` e `FormatoInaplicavel`.

    **CONFERIR NÃO É DECIDIR O QUE DIZER.** O resultado é estrutural e
    determinístico; a consequência conversacional pertence a **S2-D8**
    (`C-12`).
    """
    validar_indice(indice)
    derivar_tokens_do_indice(indice)

    if type(textos) is not dict:
        raise _nao_avaliavel(_TIPO_INVALIDO, _TEXTOS)

    divergencias: list[Divergencia] = []
    indisponiveis: list[ReferenteIndisponivel] = []
    tokens_divergentes: list[str] = []
    status_por_fragmento: list[tuple[str, str]] = []
    runtime_nao_avaliados: list[str] = []

    for resposta in indice[_RESPOSTAS]:
        rxx = resposta[_ID]
        for fragmento in resposta[_FRAGMENTOS]:
            token = rxx + _SEPARADOR + fragmento[_ID]
            status_por_fragmento.append((token, consultar_status(indice, token)))

            bindings = fragmento[_BINDINGS]
            nomes = tuple(
                binding[_NOME]
                for binding in bindings
                if binding[_MECANISMO] == _RENDERIZADO
            )
            # Validada e **descartada**: nada é concatenado nem renderizado.
            decompor_template(_exigir_texto(textos, token), nomes)

            itens = _colecao_do_fragmento(base, fragmento)

            for binding in bindings:
                desfecho = _avaliar_binding(base, binding, itens)

                if desfecho is _CONSISTENTE:
                    continue

                if desfecho is _FORA_DO_ESCOPO_FACTUAL:
                    runtime_nao_avaliados.append(token + _PONTO + binding[_NOME])
                    continue

                identidade = (
                    token,
                    rxx,
                    fragmento[_ID],
                    binding[_NOME],
                    binding[_MECANISMO],
                    binding[_ORIGEM],
                    binding[_CAMINHO_YAML],
                )

                if desfecho is _INDISPONIVEL:
                    indisponiveis.append(ReferenteIndisponivel(*identidade))
                    continue

                divergencias.append(Divergencia(*identidade, categoria=desfecho))
                if token not in tokens_divergentes:
                    tokens_divergentes.append(token)

    return ResultadoConsistencia(
        divergencias=tuple(divergencias),
        referentes_indisponiveis=tuple(indisponiveis),
        tokens_divergentes=tuple(tokens_divergentes),
        status_por_fragmento=tuple(status_por_fragmento),
        bindings_runtime_nao_avaliados=tuple(runtime_nao_avaliados),
    )


def _colecao_do_fragmento(base: object, fragmento: dict) -> object:
    """Resolve `itera_sobre`, quando declarado, pelas fronteiras de `CY13`.

    Devolve a **própria lista** da base — nunca uma cópia, nunca ordenada —, ou
    `_SEM_ITEM_CORRENTE` quando o fragmento não itera. `CaminhoYamlInvalido`,
    `CaminhoYamlContextoInvalido` e `CaminhoYamlNaoResolvido` atravessam
    intactas.
    """
    if _ITERA_SOBRE not in fragmento:
        return _SEM_ITEM_CORRENTE

    return resolver_itera_sobre(
        base, validar_itera_sobre(fragmento[_ITERA_SOBRE])
    )


def _avaliar_binding(base: object, binding: dict, itens: object) -> object:
    """Avalia um *binding* e devolve o seu desfecho interno.

    Devolve `_FORA_DO_ESCOPO_FACTUAL` para origem `RUNTIME_AUTORITATIVO`,
    `_CONSISTENTE` quando nada há a registrar, `_INDISPONIVEL` para `C-7`, ou um
    membro de `CategoriaDivergencia`.

    Sob `itera_sobre`, quem decide a cardinalidade da avaliação é o **caminho**,
    não o fragmento: um *binding* **relativo** é avaliado **por item**, e o
    **primeiro** desfecho não consistente encerra a sua avaliação — a identidade
    registrada é a do *binding*, e não a do item —, enquanto um *binding*
    **absoluto** endereça a **raiz** e é avaliado **exatamente uma vez**,
    qualquer que seja a cardinalidade da coleção, inclusive quando ela é vazia.

    O discriminante é o `relativo` **já produzido** por
    `validar_caminho_de_binding`. Nenhum caminho é reparseado aqui, e nenhuma
    gramática, prefixo ou heurística textual é reconhecida nesta fronteira.
    """
    if binding[_ORIGEM] == _RUNTIME_AUTORITATIVO:
        return _FORA_DO_ESCOPO_FACTUAL

    itera = itens is not _SEM_ITEM_CORRENTE
    decomposicao = validar_caminho_de_binding(
        binding[_CAMINHO_YAML], fragmento_itera=itera
    )
    relativo = decomposicao[0]

    if not itera or relativo is False:
        return _avaliar_ocorrencia(base, binding, decomposicao, _SEM_ITEM_CORRENTE)

    for item in itens:
        desfecho = _avaliar_ocorrencia(base, binding, decomposicao, item)
        if desfecho is not _CONSISTENTE:
            return desfecho

    return _CONSISTENTE


def _avaliar_ocorrencia(
    base: object,
    binding: dict,
    decomposicao: object,
    item: object,
) -> object:
    """Avalia **uma** ocorrência do *binding* — resolução, `C-7` e mecanismo.

    A cadeia é fixa: resolver o caminho, aplicar `C-7`, e então o formatador
    declarado (`RENDERIZADO`) ou o predicado (`ASSERTIVA`). As **únicas**
    capturas são `ValorNuloOuPendente` e `FormatoInaplicavel`;
    `CaminhoYamlNaoResolvido` e `AssertivaNaoAvaliavel` atravessam intactas,
    como Classe I.
    """
    if item is _SEM_ITEM_CORRENTE:
        valor = resolver_caminho(base, decomposicao)
    else:
        valor = resolver_caminho(base, decomposicao, item_corrente=item)

    try:
        valor = recusar_nulo_ou_pendente(valor)
    except ValorNuloOuPendente:
        return _INDISPONIVEL

    if binding[_MECANISMO] == _RENDERIZADO:
        try:
            _FORMATADORES[binding[_FORMATO]](valor)
        except FormatoInaplicavel:
            return CategoriaDivergencia.FORMATO_INAPLICAVEL
        return _CONSISTENTE

    if avaliar_assertiva(binding[_PREDICADO], valor) is False:
        return CategoriaDivergencia.ASSERTIVA_FALSA

    return _CONSISTENTE


def _exigir_texto(textos: dict, token: str) -> str:
    """Exige o texto canônico do token no mapa de transporte recebido."""
    if token not in textos:
        raise _nao_avaliavel(_TEXTO_AUSENTE, _TEXTOS)

    texto = textos[token]
    if type(texto) is not str:
        raise _nao_avaliavel(_TIPO_INVALIDO, _TEXTOS_ITEM)

    return texto


def _nao_avaliavel(categoria: str, localizador: str) -> ConsistenciaNaoAvaliavel:
    return ConsistenciaNaoAvaliavel(f"{categoria}: {localizador}")
