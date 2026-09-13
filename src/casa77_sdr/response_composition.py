"""Compositor determinístico — o *template* aprovado com os valores no lugar.

Esta fronteira recebe o `ResultadoSelecaoFatos` **já autorizado e materializado**
(§4.1.3) e produz **exatamente um texto emitível por fragmento**, substituindo
cada *placeholder* pelo `valor_formatado` do *binding* correspondente **dentro do
mesmo token**.

Ela **não decide o que responder** — isso já aconteceu a montante. Ela decide
**somente como materializar o *template* que já foi escolhido**.

**Unidade: o fragmento, nunca a resposta.** Um `TextoAutorizado` entra, um
`TextoEmitivel` sai, na **mesma ordem**. Esta fronteira **não** concatena
fragmentos, **não** monta resposta final, **não** escolhe delimitador ou
pontuação entre fragmentos, **não** reordena, **não** omite, **não** repete e
**não** produz rascunho para canal algum. Tudo isso pertence a arbitragem
posterior, junto da etapa 10 e do `ValidadorResposta`.

**Pureza.** **Zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero relógio**, **zero calendário**, **zero ambiente**, **zero logging**,
**zero *cache*** e **zero mutação** de qualquer entrada. `knowledge/**` não é
lido; o YAML não é lido; o índice não é lido nem consultado.

**Composição, nunca duplicação.** A **autoridade gramatical** do *template* é
`decompor_template` (`PH`). Aqui **não** existe *parser* de `{{...}}`, **não**
existe expressão regular, **não** existe `replace`, `format` ou `format_map`, e
**não** existe segunda gramática. Esta fronteira recebe a decomposição pronta e
apenas **percorre uma vez** a sequência devolvida.

**Cardinalidade fechada nesta versão.** Cada *binding* necessário a um
*placeholder* precisa ter **exatamente um** `FatoAutorizado` naquele token. Zero
é julgado pela própria autoridade — `decompor_template` recusa *placeholder* sem
*binding* —, e **mais de um é erro de contrato**: nada é enumerado, juntado com
vírgula, transformado em lista, repetido, escolhido pelo primeiro ou pelo último,
nem deduplicado. A apresentação de múltiplas ocorrências é **decisão futura**.

**O valor é texto factual, nunca *template*.** A substituição é feita em **uma
única passada** e o resultado **não é reprocessado**: um `valor_formatado` que
por acaso contenha `{{algo}}` permanece literal.

**Zero normalização.** Nada de `strip`, `lower`, `upper`, `casefold`, NFC, NFD,
conserto de espaço em branco, conserto de pontuação ou correspondência
aproximada. Literal, nome e valor entram exatamente como foram recebidos.

***Fail-closed*, sem resultado parcial.** Incoerência da seleção recebida sai
como `ComposicaoNaoAvaliavel`; invalidez do *template* sai como
`PlaceholderInvalido`, **intacta**, da fronteira que tem autoridade sobre ela.
Em nenhum dos casos há resultado parcial.

**Zero valor comercial em `repr`.** `TextoEmitivel.texto` é declarado
`repr=False`: ele é o texto pronto para emissão, **não** material de log.
`OrigemValor` carrega **só proveniência estrutural**.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from casa77_sdr.fact_selection import (
    FatoAutorizado,
    ResultadoSelecaoFatos,
    TextoAutorizado,
)
from casa77_sdr.response_placeholder import decompor_template

__all__ = [
    "ComposicaoNaoAvaliavel",
    "OrigemValor",
    "ResultadoComposicao",
    "TextoEmitivel",
    "compor_textos_emitiveis",
]


@dataclass(frozen=True, slots=True)
class OrigemValor:
    """Proveniência estrutural de **um** *binding* efetivamente inserido.

    Carrega o nome do *binding*, o `caminho_yaml` declarado e o nome do formato
    declarado — e **nada mais**. **Nunca** o valor inserido, o texto composto, o
    YAML, a posição no *template* ou um índice.
    """

    binding: str
    referente: str
    formato: str


@dataclass(frozen=True, slots=True)
class TextoEmitivel:
    """O texto de **um** fragmento, com os valores já nos seus lugares.

    `origens` tem **uma entrada por *binding* distinto realmente inserido**, na
    ordem da **primeira ocorrência física do *placeholder* no *template***.
    *Placeholder* repetido **não** duplica a origem. Um fragmento **estático**
    tem `origens == ()`.

    `texto` é `repr=False`: é conteúdo pronto para emissão, jamais material de
    log.
    """

    token: str
    rxx: str
    fragmento_id: str
    origens: tuple[OrigemValor, ...]
    texto: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class ResultadoComposicao:
    """Os textos emitíveis, **um por fragmento**, na ordem recebida.

    A ordem é **exatamente** a de `selecao.textos_autorizados`. Não existe aqui
    texto final, rascunho, mensagem, separador ou delimitador: esta fronteira
    **não monta a resposta**.
    """

    textos_emitiveis: tuple[TextoEmitivel, ...]


class ComposicaoNaoAvaliavel(Exception):
    """Erro de composição **próprio** desta fronteira.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o token, o *binding*, o referente, o valor, o texto, uma cardinalidade, um
    índice, uma posição, o `repr` ou o tipo concreto.

    Ela cobre **apenas** o que nenhuma fronteira existente julga: a forma da
    seleção recebida, a sua coerência interna e a cardinalidade fechada desta
    versão. A invalidez do *template* pertence a `PlaceholderInvalido` e
    atravessa **intacta**.
    """


# Categorias privadas e fechadas. Elas nomeiam o impedimento e **nao** sao
# vocabulario normativo novo: nenhum enum publico e criado para elas.
_TIPO_INVALIDO = "tipo_invalido"
_DUPLICIDADE = "duplicidade"
_TOKEN_DESCONHECIDO = "token_desconhecido"
_PROVENIENCIA_INCOERENTE = "proveniencia_incoerente"
_CARDINALIDADE_INCOMPATIVEL = "cardinalidade_incompativel"

# Localizadores estruturais fechados. Nomeiam a **posicao da chamada**, jamais o
# conteudo recebido.
_SELECAO = "selecao"
_FATOS = "selecao.fatos"
_FATOS_ITEM = "selecao.fatos.item"
_TEXTOS = "selecao.textos_autorizados"
_TEXTOS_ITEM = "selecao.textos_autorizados.item"

_VAZIO = ""


def compor_textos_emitiveis(selecao: object) -> ResultadoComposicao:
    """Compõe **um** texto emitível por fragmento da seleção recebida.

    `selecao` é o `ResultadoSelecaoFatos` **já produzido** por
    `materializar_fatos_autorizados` (§4.1.3). Esta fronteira **não abre arquivo
    algum**, **não consulta o índice** e **não reavalia a autorização**.

    A ordem é **fixa**: **1.** o tipo da seleção; **2.** a forma dos fatos —
    `tuple`, itens canônicos, campos `str` exatos; **3.** a forma dos textos
    autorizados, do mesmo modo; **4.** a unicidade do token entre os textos;
    **5.** a coerência de cada fato — token conhecido e `rxx`/`fragmento_id`
    **literalmente** coincidentes; **6.** o percurso, na ordem de
    `textos_autorizados`.

    Por fragmento: os fatos daquele token são agrupados por *binding* **na ordem
    de entrada**; um *binding* repetido é **erro de contrato**
    (`cardinalidade_incompativel`); os nomes resultantes vão a
    `decompor_template`, que é a **autoridade** sobre o *template*; e a sequência
    devolvida é percorrida **uma única vez**, copiando cada literal e inserindo o
    `valor_formatado` do único fato de cada nome. O resultado **não é
    reprocessado**.

    Levanta `ComposicaoNaoAvaliavel` com `tipo_invalido` (`selecao`,
    `selecao.fatos`, `selecao.fatos.item`, `selecao.textos_autorizados`,
    `selecao.textos_autorizados.item`), `duplicidade`
    (`selecao.textos_autorizados.item`), `token_desconhecido`,
    `proveniencia_incoerente` e `cardinalidade_incompativel`
    (`selecao.fatos.item`). `PlaceholderInvalido` — *placeholder* sem *binding*,
    *binding* sem *placeholder*, *template* malformado — atravessa **intacta**.
    **Nenhum resultado parcial é devolvido** e **nada é capturado aqui**.

    **COMPOR NÃO É DECIDIR O QUE DIZER, NEM MONTAR A RESPOSTA.** Cada fragmento
    é materializado isoladamente; a sequência final, a eventual omissão, os
    separadores e o papel do LLM pertencem a arbitragem posterior.
    """
    if type(selecao) is not ResultadoSelecaoFatos:
        raise _nao_avaliavel(_TIPO_INVALIDO, _SELECAO)

    fatos = selecao.fatos
    if type(fatos) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _FATOS)
    for fato in fatos:
        if type(fato) is not FatoAutorizado:
            raise _nao_avaliavel(_TIPO_INVALIDO, _FATOS_ITEM)
        _exigir_textos_exatos(
            (
                fato.token,
                fato.rxx,
                fato.fragmento_id,
                fato.binding,
                fato.referente,
                fato.formato,
                fato.valor_formatado,
            ),
            _FATOS_ITEM,
        )

    textos = selecao.textos_autorizados
    if type(textos) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _TEXTOS)
    for autorizado in textos:
        if type(autorizado) is not TextoAutorizado:
            raise _nao_avaliavel(_TIPO_INVALIDO, _TEXTOS_ITEM)
        _exigir_textos_exatos(
            (
                autorizado.token,
                autorizado.rxx,
                autorizado.fragmento_id,
                autorizado.texto,
            ),
            _TEXTOS_ITEM,
        )

    identidade: dict[str, tuple[str, str]] = {}
    for autorizado in textos:
        if autorizado.token in identidade:
            raise _nao_avaliavel(_DUPLICIDADE, _TEXTOS_ITEM)
        identidade[autorizado.token] = (autorizado.rxx, autorizado.fragmento_id)

    por_token: dict[str, list[FatoAutorizado]] = {}
    for fato in fatos:
        if fato.token not in identidade:
            raise _nao_avaliavel(_TOKEN_DESCONHECIDO, _FATOS_ITEM)
        if identidade[fato.token] != (fato.rxx, fato.fragmento_id):
            raise _nao_avaliavel(_PROVENIENCIA_INCOERENTE, _FATOS_ITEM)
        por_token.setdefault(fato.token, []).append(fato)

    emitiveis = [
        _compor_fragmento(autorizado, por_token.get(autorizado.token, ()))
        for autorizado in textos
    ]

    return ResultadoComposicao(textos_emitiveis=tuple(emitiveis))


def _compor_fragmento(
    autorizado: TextoAutorizado,
    fatos_do_token: object,
) -> TextoEmitivel:
    """Compõe **um** fragmento, do agrupamento à passada única.

    Os fatos chegam **na ordem de entrada**, já restritos a este token. Um
    *binding* que apareça duas vezes é `cardinalidade_incompativel`: nesta
    versão, cada *binding* necessário tem **exatamente um** fato, e **nada** é
    escolhido, juntado, ordenado ou deduplicado em seu lugar.

    Os nomes seguem para `decompor_template` na ordem da **primeira ocorrência
    nos fatos**; a ordem devolvida, porém, é a do **próprio *template*** — e é
    ela que rege tanto a composição quanto `origens`.
    """
    fato_por_binding: dict[str, FatoAutorizado] = {}
    nomes: list[str] = []
    for fato in fatos_do_token:
        if fato.binding in fato_por_binding:
            raise _nao_avaliavel(_CARDINALIDADE_INCOMPATIVEL, _FATOS_ITEM)
        fato_por_binding[fato.binding] = fato
        nomes.append(fato.binding)

    # Autoridade unica sobre a gramatica do *template*. `PlaceholderInvalido`
    # atravessa intacta — inclusive `placeholder_sem_binding`, que e como a
    # cardinalidade zero e julgada, e `binding_sem_placeholder`.
    partes = decompor_template(autorizado.texto, tuple(nomes))

    pedacos: list[str] = []
    origens: list[OrigemValor] = []
    ja_registrados: set[str] = set()

    # Passada unica: posicao par e literal, posicao impar e nome de *binding*
    # (`PH`: a sequencia alterna e tem comprimento impar).
    for posicao, parte in enumerate(partes):
        if posicao % 2 == 0:
            pedacos.append(parte)
            continue

        fato = fato_por_binding[parte]
        pedacos.append(fato.valor_formatado)

        # *Placeholder* repetido reutiliza o mesmo fato e **nao** duplica a
        # origem: ela fica na sua primeira ocorrencia fisica.
        if parte not in ja_registrados:
            ja_registrados.add(parte)
            origens.append(
                OrigemValor(fato.binding, fato.referente, fato.formato)
            )

    return TextoEmitivel(
        autorizado.token,
        autorizado.rxx,
        autorizado.fragmento_id,
        tuple(origens),
        _VAZIO.join(pedacos),
    )


def _exigir_textos_exatos(campos: tuple[object, ...], localizador: str) -> None:
    """Exige `str` **exata** em cada campo estrutural lido desta posição.

    Subclasse de `str` é recusada: ela poderia redefinir `__eq__`, `__hash__` ou
    `__str__` e decidir por conta própria quando dois tokens são o mesmo, ou o
    que a composição produz.
    """
    for campo in campos:
        if type(campo) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, localizador)


def _nao_avaliavel(categoria: str, localizador: str) -> ComposicaoNaoAvaliavel:
    return ComposicaoNaoAvaliavel(f"{categoria}: {localizador}")
