"""Montagem canônica de **uma** emissão — os textos já compostos numa mensagem.

Esta fronteira recebe o `ResultadoComposicao` **já produzido** por
`compor_textos_emitiveis` (§4.1.4) e devolve a **forma canônica** da emissão:
as unidades **na ordem recebida**, numa **única mensagem**, separadas por
**`"\\n\\n"`**. É a materialização física de **`PC-3`**, e nada além disso.

**Uma emissão, nunca um ciclo.** Ela monta **o que já foi decidido**. Ela não
sabe fase, estado, ação, evento, destino, canal, interessado, atendimento
humano, `E15` ou `E12` — e **não** os decide. O que entra é uma sequência de
textos; o que sai é a mesma sequência, materializada.

**Pureza.** **Zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero relógio**, **zero calendário**, **zero ambiente**, **zero logging**,
**zero *cache*** e **zero mutação** de qualquer entrada. `knowledge/**` não é
aberto, o YAML não é lido, o índice não é carregado e status algum é consultado.

**Preservação integral.** Cardinalidade, ordem e conteúdo de
`textos_emitiveis` saem intactos: **nenhum** filtro, escolha, ordenação,
omissão, repetição ou *fallback*. A montagem **não** decide o que dizer — ela
**não** sabe decidir.

**Zero conteúdo lexical novo.** O texto final é, literalmente, os textos
recebidos unidos por **`"\\n\\n"`**: nenhum prefixo, nenhum sufixo, nenhuma
pontuação, nenhum conector e nenhuma quebra a mais. O separador aparece
**exatamente** entre unidades adjacentes — nunca antes da primeira, nunca depois
da última.

**Zero reinterpretação.** O conteúdo de cada `TextoEmitivel.texto` é **opaco**.
Espaço inicial ou final, quebra de linha já presente, pontuação e algo que se
pareça com `{{nome}}` permanecem **literais**. Nada de `strip`, `replace`,
`format`, `format_map`, expressão regular, `casefold` ou normalização Unicode.

**Cardinalidade zero fecha.** Uma composição **sem** unidades não é uma emissão
vazia: é **incoerência do chamador**. Esta fronteira **não conhece
`SEM_EMISSAO`**; silêncio legítimo significa que ela **não é chamada**, e essa é
responsabilidade futura do orquestrador.

***Fail-closed*, sem resultado parcial.** Forma inválida da composição, item não
canônico, campo estrutural que não seja `str` exata, token repetido e
cardinalidade zero **fecham** — sem correção silenciosa e sem montagem
improvisada.

**Zero valor comercial em `repr`.** `RespostaMontada.texto` é declarado
`repr=False`: é o texto pronto para emissão, **não** material de log. `tokens`
são identificadores estruturais e podem aparecer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from casa77_sdr.response_composition import ResultadoComposicao, TextoEmitivel

__all__ = [
    "MontagemRespostaNaoAvaliavel",
    "RespostaMontada",
    "montar_resposta_final",
]


@dataclass(frozen=True, slots=True)
class RespostaMontada:
    """A forma canônica de **uma** emissão já decidida.

    `tokens` tem **uma entrada por unidade**, na **mesma ordem** dos textos
    montados: é a proveniência estrutural da emissão, e nada é acrescentado,
    removido, reordenado ou deduplicado.

    `texto` é `repr=False`: é conteúdo pronto para emissão, jamais material de
    log.
    """

    tokens: tuple[str, ...]
    texto: str = field(repr=False)


class MontagemRespostaNaoAvaliavel(Exception):
    """Erro de montagem **próprio** desta fronteira.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o token, o texto, o `Rxx`, o identificador de fragmento, a origem, um valor,
    uma cardinalidade concreta, um índice, uma posição, o `repr` ou o tipo
    concreto.

    Ela cobre **apenas** o que nenhuma fronteira existente julga: a forma da
    composição recebida, a unicidade dos tokens e a cardinalidade zero.
    """


# Categorias privadas e fechadas. Elas nomeiam o impedimento e **nao** sao
# vocabulario normativo novo: nenhum enum publico e criado para elas.
_TIPO_INVALIDO = "tipo_invalido"
_DUPLICIDADE = "duplicidade"
_CARDINALIDADE_VAZIA = "cardinalidade_vazia"

# Localizadores estruturais fechados. Nomeiam a **posicao da chamada**, jamais o
# conteudo recebido.
_COMPOSICAO = "composicao"
_EMITIVEIS = "composicao.textos_emitiveis"
_EMITIVEIS_ITEM = "composicao.textos_emitiveis.item"

# `PC-3`, materializado. O separador e **uma constante literal**: ele nao e
# escolhido, configurado, derivado nem negociado aqui.
_SEPARADOR = "\n\n"


def montar_resposta_final(composicao: object) -> RespostaMontada:
    """Monta a forma canônica de **uma** emissão já composta.

    `composicao` é o `ResultadoComposicao` **já produzido** por
    `compor_textos_emitiveis` (§4.1.4). Esta fronteira **não abre arquivo
    algum**, **não consulta o índice** e **não reavalia a autorização**.

    A ordem é **fixa**: **1.** o tipo da composição; **2.** a forma de
    `textos_emitiveis` — `tuple` exata; **3.** a cardinalidade, que **não pode
    ser zero**; **4.** a forma de cada item — `TextoEmitivel` exato, com `token`
    e `texto` `str` exatas —, junto da **unicidade do token**; **5.** a
    materialização.

    Devolve `RespostaMontada` com `tokens` na **ordem recebida** e `texto` igual
    aos textos recebidos unidos por **`"\\n\\n"`** — **uma** ocorrência do
    separador entre cada par adjacente, e nenhuma nas pontas. Com **uma só**
    unidade, o texto final é **exatamente** o texto dela.

    Levanta `MontagemRespostaNaoAvaliavel` com `tipo_invalido` (`composicao`,
    `composicao.textos_emitiveis`, `composicao.textos_emitiveis.item`),
    `cardinalidade_vazia` (`composicao.textos_emitiveis`) e `duplicidade`
    (`composicao.textos_emitiveis.item`). **Nada é capturado** e **nenhum
    resultado parcial é devolvido**.

    **MONTAR NÃO É DECIDIR O QUE DIZER, NEM VALIDAR, NEM EMITIR.** A cobertura
    já foi decidida por S2-D8; as ações, pela máquina; os fatos e os textos,
    pelas fronteiras de §4.1.3 e §4.1.4. A validação final pertence ao
    `ValidadorResposta`, que **não** existe aqui, e o envio pertence ao
    orquestrador, que **não** é chamado daqui.
    """
    if type(composicao) is not ResultadoComposicao:
        raise _nao_avaliavel(_TIPO_INVALIDO, _COMPOSICAO)

    emitiveis = composicao.textos_emitiveis
    if type(emitiveis) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _EMITIVEIS)

    # Cardinalidade zero **nao** e emissao vazia: e incoerencia do chamador.
    # Silencio legitimo significa que esta funcao nao e chamada, e isso pertence
    # ao orquestrador futuro — `SEM_EMISSAO` nao existe aqui.
    if not emitiveis:
        raise _nao_avaliavel(_CARDINALIDADE_VAZIA, _EMITIVEIS)

    vistos: set[str] = set()
    for emitivel in emitiveis:
        if type(emitivel) is not TextoEmitivel:
            raise _nao_avaliavel(_TIPO_INVALIDO, _EMITIVEIS_ITEM)
        # Subclasse de `str` e recusada: ela poderia redefinir `__eq__`,
        # `__hash__` ou `__str__` e decidir por conta propria quando dois tokens
        # sao o mesmo, ou o que a montagem produz.
        if type(emitivel.token) is not str or type(emitivel.texto) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _EMITIVEIS_ITEM)
        # Token repetido e **erro de contrato** do chamador: a deduplicacao ja
        # correu a montante, e aqui nada e corrigido em silencio.
        if emitivel.token in vistos:
            raise _nao_avaliavel(_DUPLICIDADE, _EMITIVEIS_ITEM)
        vistos.add(emitivel.token)

    # Zero conteudo lexical novo: a uniao e **exatamente** `PC-3`, e o conteudo
    # de cada unidade atravessa **opaco**.
    return RespostaMontada(
        tuple(emitivel.token for emitivel in emitiveis),
        _SEPARADOR.join(emitivel.texto for emitivel in emitiveis),
    )


def _nao_avaliavel(
    categoria: str,
    localizador: str,
) -> MontagemRespostaNaoAvaliavel:
    return MontagemRespostaNaoAvaliavel(f"{categoria}: {localizador}")
