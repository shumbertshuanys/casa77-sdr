"""`ProjetorEmissao` — quais fragmentos aprovados são destinados à emissão.

Esta fronteira junta **duas projeções já decididas a montante** e devolve **uma
só** tupla de identificadores:

| Entrada | Quem decidiu |
|---|---|
| `fragmentos_autorizados` | **S2-D8** (§4.4.1, `SF-D4-10`) |
| `acoes` | a **primeira decisão** da máquina (§4.5) |

A saída alimenta `materializar_fatos_autorizados` (§4.1.3). Nada além disso
acontece aqui.

**O que esta fronteira NÃO faz.** Ela **não** escolhe o fragmento que cobre uma
consulta, **não implementa** emissibilidade, **não** avalia regra comercial,
**não** resolve *binding*, **não** monta texto, **não** chama LLM e **não**
executa ação alguma. Ela **projeta identificadores**, e mais nada.

**Emissibilidade é consumida aqui, nunca implementada.** No **único** caso
fechado da rota *action-owner* de `R06/F1`, esta fronteira **consome
exclusivamente** a autoridade compartilhada `avaliar_emissibilidade` (§4.4.5)
sobre uma `FotografiaFragmento` **já recebida** e pronta. Ela continua **não**
comparando status, **não** percorrendo referentes, **não** avaliando `ASSERTIVA`
diretamente, **não** resolvendo *binding*, **não** lendo YAML, **não** lendo o
índice e **não** tomando decisão comercial: **nenhuma segunda implementação de
`D8-F` nasce aqui**.

**Pureza.** **Zero I/O**, **zero *filesystem***, **zero rede**, **zero LLM**,
**zero relógio**, **zero calendário**, **zero ambiente**, **zero logging**,
**zero *cache*** e **zero mutação** de qualquer entrada. `knowledge/**` não é
aberto, o índice não é carregado e nenhuma consulta ao corpus é feita: os
identificadores chegam prontos. A coerência da tabela privada com o corpus
versionado é provada **no teste de integração**, nunca por leitura em produção.

**A tabela é total e explícita.** Todas as **20** ações do vocabulário fechado
de §4.5 têm entrada declarada, escrita **literalmente**, uma a uma. Isso é
deliberado: uma vigésima primeira ação, no futuro, **quebra o teste de
totalidade** e exige arbitragem — em vez de cair silenciosamente num
comportamento padrão.

**Tupla vazia na tabela significa UMA coisa só.** Ela diz que **esta fronteira
não acrescenta fragmento aprovado para aquela ação** — e **nada além disso**.
Ela **não** diz que a ação foi atendida, que a ação não é textual, que a ação foi
dispensada, nem que a obrigação conversacional desapareceu. Para ação textual sem
unidade aprovada canônica, a obrigação **permanece pendente** fora daqui.

**Ordem.** A saída é, literalmente, os identificadores recebidos **na ordem
recebida**, seguidos dos mandatórios **na ordem das ações**. Nada é ordenado
lexicalmente, nada é reordenado e nenhum identificador recebido é removido.

**Primeira dupla rota — `R05/F1`, com exceção fechada.** Ela satisfaz a mesma
obrigação textual de **T15** por **duas** rotas: a cobertura de S2-D8 ou a ação
de não confirmação de disponibilidade. Quando a cobertura já o trouxe, **ela é a
owner** — o bloco mandatório não acrescenta segunda ocorrência e o token
permanece na **posição original** de `fragmentos_autorizados`. Quando a
cobertura não o trouxe, **a ação o completa**. Isso vale **somente** para esse
par ação/token: **não existe deduplicação *cross-source* genérica**, e nenhum
identificador futuro herda a exceção por analogia.

**Segunda dupla rota — `R06/F1`, com regra própria.** A obrigação textual de
**T16** também admite duas rotas: a cobertura de S2-D8 ou a ação de condições de
visita. A diferença material é que `R06/F1` **tem *bindings*** — de origem
`YAML`, nunca `RUNTIME_AUTORITATIVO` —, e por isso a **rota da ação não pode
acrescentá-lo sem veredito**: ela consulta a **autoridade única** de
emissibilidade sobre a `FotografiaFragmento` recebida. **Cobertura presente →
cobertura é a *owner***, e a fotografia **nem é lida**. **Cobertura ausente →
ação é a *owner***: com o fragmento **emitível**, ele entra; **não emitível**,
**zero fragmento é acrescentado**, sob a leitura literal de `PE-7` — não é erro,
não é resultado parcial, não há substituto e **nenhum evento nasce daqui**.
**Nada disso é herdado de `R05` por analogia**: são duas exceções fechadas e
independentes, e fora delas `PE-10` continua *fail-closed*.

**Variantes incompatíveis.** Com a ação de T15 presente, `R05/F2` ou `R05/F3`
em `fragmentos_autorizados` são insumos **contraditórios** — elas sustentam uma
resposta de disponibilidade a partir de consulta autoritativa válida, e T15
ordena o *fallback* de **não** confirmação. Esta fronteira **não escolhe** qual
origem está certa, **não corrige** a condição 6 e **não toca** os fatos de
runtime: ela apenas **fecha**.

***Fail-closed*.** Forma inválida, repetição no bloco recebido, ação sem entrada
na tabela e colisão entre as duas origens — **fora das duas duplas rotas**
explicitamente fechadas acima — **fecham**, assim como as variantes
incompatíveis. Sem resultado parcial, sem correção silenciosa e sem composição
improvisada.
"""

from __future__ import annotations

from casa77_sdr.fragment_emissibility import (
    FotografiaFragmento,
    avaliar_emissibilidade,
)
from casa77_sdr.state_machine import AcaoMaquina

__all__ = [
    "ProjecaoEmissaoNaoAvaliavel",
    "projetar_fragmentos_para_emissao",
]


class ProjecaoEmissaoNaoAvaliavel(Exception):
    """Erro de composição **próprio** desta fronteira.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o identificador recebido, o nome ou o valor da ação, o texto, um valor
    comercial, um índice, uma posição, uma cardinalidade, o tipo concreto ou o
    `repr`.

    Ela cobre **apenas** o que nenhuma fronteira existente julga: a forma das
    **duas entradas base** — e, **somente** na rota *action-owner* de `R06/F1`,
    a da **terceira entrada condicional** `fotografia_r06` —, a unicidade
    dentro da tupla recebida, a totalidade da tabela e a colisão entre as duas
    origens.
    """


# Categorias privadas e fechadas. Elas nomeiam o impedimento e **nao** sao
# vocabulario normativo novo: nenhum enum publico e criado para elas.
_TIPO_INVALIDO = "tipo_invalido"
_DUPLICIDADE = "duplicidade"
_ACAO_SEM_MAPEAMENTO = "acao_sem_mapeamento"
_CONFLITO_ORIGEM = "conflito_origem"

# Localizadores estruturais fechados. Nomeiam a **posicao da chamada**, jamais o
# conteudo recebido.
_AUTORIZADOS = "fragmentos_autorizados"
_AUTORIZADOS_ITEM = "fragmentos_autorizados.item"
_ACOES = "acoes"
_ACOES_ITEM = "acoes.item"
_FOTOGRAFIA_R06 = "fotografia_r06"

# Mandatorio PURO: ele so chega por esta fronteira, pela acao de lacuna, e nunca
# por cobertura — colisao cross-source com ele continua fail-closed (PE-10). Ele
# e admissivel porque o corpus versionado prova mecanicamente — no teste de
# integracao, nunca aqui — que ele existe, que o seu rotulo canonico o admite e
# que ele **nao tem binding algum**, de modo que nenhuma decisao factual de
# runtime e necessaria para emiti-lo.
_LACUNA = "R03/F1"

# A PRIMEIRA dupla rota autorizada (PE-13). `R05/F1` satisfaz a mesma obrigacao
# textual de T15 por duas rotas — cobertura de S2-D8 ou a acao de nao confirmacao
# de disponibilidade — e o corpus versionado prova, no teste de integracao, que
# ele tambem existe, e emitivel e tem **zero bindings**. A excecao vale SOMENTE
# para este par acao/token: nenhum outro identificador a herda por analogia, e
# `PE-10` continua fail-closed em toda colisao cross-source fora dela.
_FALLBACK_DISPONIBILIDADE = "R05/F1"
_ACAO_DUPLA_ROTA = AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE

# Variantes da MESMA superficie R05 que sustentam uma resposta de disponibilidade
# a partir de consulta autoritativa valida. Com a acao de T15 presente, elas sao
# contradicao estrutural (PE-14): T15 ordena o fallback de **nao** confirmacao.
# Esta fronteira nao escolhe qual origem esta certa — ela so fecha.
_VARIANTES_INCOMPATIVEIS: frozenset[str] = frozenset({"R05/F2", "R05/F3"})

# A SEGUNDA dupla rota autorizada, e ela tem regra **propria** — nada aqui e
# herdado de `R05` por analogia. `R06/F1` satisfaz a obrigacao textual de T16
# por duas rotas: a cobertura de S2-D8 ou a acao de condicoes de visita. A
# diferenca material e que ele **tem bindings** de origem `YAML`, e por isso a
# rota da acao **nao pode** acrescenta-lo sem veredito: ela consulta a
# **autoridade unica** de emissibilidade (§4.4.5) sobre a fotografia recebida.
# O corpus versionado prova, no teste de integracao, que ele existe, que o seu
# rotulo canonico o admite e que **nenhum** dos seus bindings e de origem
# `RUNTIME_AUTORITATIVO` — logo nenhum fato de runtime entra nesta fronteira.
_CONDICOES_VISITA = "R06/F1"
_ACAO_VISITA = AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA

# Sentinela local: distingue "ainda nao avaliado" de um veredito booleano. Ela
# garante **no maximo uma** avaliacao de `R06/F1` por chamada, e morre com a
# chamada — **zero cache global**.
_NAO_AVALIADO = object()

# Tabela TOTAL e LITERAL das 20 acoes de §4.5, na ordem do vocabulario fechado.
# Escrita uma a uma de proposito: nada de compreensao, nada de valor padrao. Uma
# acao nova no vocabulario precisa aparecer aqui explicitamente, e ate la o teste
# de totalidade fica vermelho.
#
# Tupla vazia diz **somente** que esta fronteira nao acrescenta fragmento
# aprovado para aquela acao — jamais que a acao foi atendida.
_FRAGMENTOS_POR_ACAO: dict[AcaoMaquina, tuple[str, ...]] = {
    AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL: (),
    AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL: (),
    AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE: (),
    AcaoMaquina.PERGUNTAR_FORMATO: (),
    AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR: (),
    AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL: (),
    AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE: (),
    AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA: (_CONDICOES_VISITA,),
    AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO: (_LACUNA,),
    AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE: (
        _FALLBACK_DISPONIBILIDADE,
    ),
    AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE: (),
    AcaoMaquina.REFORCAR_ENCAMINHAMENTO: (),
    AcaoMaquina.EMITIR_MENSAGEM_DE_ENCAMINHAMENTO: (),
    AcaoMaquina.NAO_AVANCAR_COLETA: (),
    AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA: (),
    AcaoMaquina.PREPARAR_RESUMO: (),
    AcaoMaquina.ENTREGAR_RESUMO: (),
    AcaoMaquina.SOLICITAR_CONSULTA_CALENDARIO: (),
    AcaoMaquina.REABRIR_ATENDIMENTO: (),
    AcaoMaquina.ABRIR_NOVO_ATENDIMENTO: (),
}


def projetar_fragmentos_para_emissao(
    fragmentos_autorizados: object,
    acoes: object,
    *,
    fotografia_r06: object = None,
) -> tuple[str, ...]:
    """Projeta os fragmentos destinados à emissão neste ciclo.

    `fragmentos_autorizados` é a tupla **já produzida** por S2-D8
    (`SF-D4-10`); `acoes` são as ações da **primeira** decisão da máquina
    (§4.5). Esta fronteira **não reavalia** nenhuma das duas.

    `fotografia_r06` é a **terceira entrada, *keyword-only* e condicional**: ela
    é exigida **somente** quando a ação de **T16** é a *owner* de `R06/F1` — isto
    é, quando a ação está presente **e** a cobertura **não** trouxe o token.
    Fora desse caminho ela é **irrelevante**: não é lida, não é validada e não
    é avaliada. Ausente ou de tipo diferente de `FotografiaFragmento` naquele
    caminho, a fronteira **fecha** com `tipo_invalido: fotografia_r06`.

    A ordem é **fixa**: **1.** a forma da tupla recebida — `tuple` exata, itens
    `str` exatos, **sem repetição**; **2.** a forma das ações — `tuple` exata,
    itens do vocabulário fechado, **todos com entrada na tabela**; **3.** o
    bloco mandatório, percorrendo `acoes` na ordem recebida e acrescentando cada
    identificador declarado **apenas na sua primeira ocorrência**, com a **dupla
    rota fechada** de `R05/F1` e a de `R06/F1` resolvidas por *owner*; **4.** a
    ausência de colisão entre as duas origens.

    Devolve `fragmentos_autorizados + mandatórios`: **todos** os identificadores
    recebidos primeiro, **na ordem recebida**, e então os mandatórios, **na
    ordem das ações**. Nenhum identificador se repete, nenhum é removido e
    nenhuma ordenação própria é aplicada.

    Para a ação de não confirmação de disponibilidade, `R05/F1` chega por **uma**
    de duas rotas: se a cobertura já o autorizou, ela é a **owner** e o token
    mantém a sua posição; caso contrário, a ação o acrescenta como mandatório. A
    presença de `R05/F2` ou `R05/F3` na cobertura, com essa ação, é contradição
    estrutural e **fecha**.

    Levanta `ProjecaoEmissaoNaoAvaliavel` com `tipo_invalido`
    (`fragmentos_autorizados`, `fragmentos_autorizados.item`, `acoes`,
    `acoes.item`), `duplicidade` (`fragmentos_autorizados.item`),
    `acao_sem_mapeamento` (`acoes.item`), `conflito_origem`
    (`fragmentos_autorizados.item`) e `tipo_invalido` (`fotografia_r06`).
    **Nada é capturado** e **nenhum resultado parcial é devolvido**. `R06/F1`
    **não emitível não é erro**: ele apenas **não contribui**.

    **PROJETAR NÃO É DECIDIR O QUE RESPONDER, NEM DIZER.** O que cobre a
    consulta já foi decidido por S2-D8; o que a conversa exige já foi decidido
    pela máquina; o texto pertence às fronteiras seguintes.
    """
    if type(fragmentos_autorizados) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _AUTORIZADOS)

    recebidos: set[str] = set()
    for token in fragmentos_autorizados:
        if type(token) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _AUTORIZADOS_ITEM)
        # `SF-D4-9` ja deduplica a montante: repeticao aqui e erro de contrato
        # do chamador, **nunca** algo a corrigir silenciosamente.
        if token in recebidos:
            raise _nao_avaliavel(_DUPLICIDADE, _AUTORIZADOS_ITEM)
        recebidos.add(token)

    if type(acoes) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _ACOES)

    mandatorios: list[str] = []
    ja_mandatorios: set[str] = set()
    # Veredito local de `R06/F1`: avaliado **no maximo uma vez** por chamada, e
    # **somente** quando a acao de T16 e efetivamente a *owner*.
    veredito_r06: object = _NAO_AVALIADO

    for acao in acoes:
        if type(acao) is not AcaoMaquina:
            raise _nao_avaliavel(_TIPO_INVALIDO, _ACOES_ITEM)
        if acao not in _FRAGMENTOS_POR_ACAO:
            raise _nao_avaliavel(_ACAO_SEM_MAPEAMENTO, _ACOES_ITEM)

        for token in _FRAGMENTOS_POR_ACAO[acao]:
            if acao is _ACAO_DUPLA_ROTA and token == _FALLBACK_DISPONIBILIDADE:
                # PE-14. `R05/F2` e `R05/F3` sustentam uma resposta de
                # disponibilidade vinda de consulta autoritativa valida; a acao
                # de T15 ordena o fallback de **nao** confirmacao. Juntas, sao
                # insumos contraditorios: fecha, sem escolher variante alguma.
                if recebidos & _VARIANTES_INCOMPATIVEIS:
                    raise _nao_avaliavel(_CONFLITO_ORIGEM, _AUTORIZADOS_ITEM)
                # PE-13. Quando a cobertura ja trouxe exatamente este token, ela
                # e a **owner** da unidade neste ciclo: o bloco mandatorio nao
                # acrescenta segunda ocorrencia, e o token permanece **na posicao
                # original** de `fragmentos_autorizados` (PE-4, PE-8).
                if token in recebidos:
                    continue
            # Acao repetida, ou duas acoes que declarem o mesmo identificador,
            # contribuem **uma vez**: vence a primeira ocorrencia.
            if acao is _ACAO_VISITA and token == _CONDICOES_VISITA:
                # Cobertura *owner*: quando S2-D8 ja autorizou o token, ele
                # permanece **na posicao original** e o bloco mandatorio nao
                # acrescenta segunda ocorrencia (PE-4, PE-8). A fotografia e
                # **irrelevante** aqui — ela nao e lida, nem validada.
                if token in recebidos:
                    continue
                # Acao *owner*: ela **precisa** de um veredito, porque `R06/F1`
                # tem bindings. A fotografia passa a ser obrigatoria, e a
                # decisao pertence a **autoridade unica** de §4.4.5 — esta
                # fronteira **nao** compara status, **nao** percorre referentes
                # e **nao** avalia `ASSERTIVA`.
                if veredito_r06 is _NAO_AVALIADO:
                    if type(fotografia_r06) is not FotografiaFragmento:
                        raise _nao_avaliavel(_TIPO_INVALIDO, _FOTOGRAFIA_R06)
                    veredito_r06 = avaliar_emissibilidade(fotografia_r06).emitivel
                if not veredito_r06:
                    # Nao emitivel: **zero fragmento** acrescentado por T16, sob
                    # `PE-7`. Nao e erro, nao e resultado parcial, nao ha
                    # substituto e **nenhum evento** nasce daqui.
                    continue
            if token in ja_mandatorios:
                continue
            ja_mandatorios.add(token)
            mandatorios.append(token)

    for token in mandatorios:
        # Zero deduplicacao cross-source generica: um identificador que chegue
        # pelas duas origens significa modelagem incoerente a montante. As
        # excecoes sao **duas**, explicitas e independentes — `R05/F1` por
        # `PE-13` e `R06/F1` por `PE-15`-`PE-20` —, e ambas ja foram resolvidas
        # acima **por owner**: o token sequer entra neste bloco. Fora delas,
        # `PE-10` continua fail-closed.
        if token in recebidos:
            raise _nao_avaliavel(_CONFLITO_ORIGEM, _AUTORIZADOS_ITEM)

    return fragmentos_autorizados + tuple(mandatorios)


def _nao_avaliavel(categoria: str, localizador: str) -> ProjecaoEmissaoNaoAvaliavel:
    return ProjecaoEmissaoNaoAvaliavel(f"{categoria}: {localizador}")
