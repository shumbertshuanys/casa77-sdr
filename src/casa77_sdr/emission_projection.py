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

**Superfícies conversacionais do M2.1 (PE-21–PE-25).** Saudação (`R01/F1`),
despedida (`R15/F1`), ressalva de capacidade (`R34/F1`) e reforço de
encaminhamento (`R35/F1`) entram pela tabela fixa. Três ações escolhem o
fragmento por **dado estruturado** recebido explicitamente, nunca por texto: a
pergunta de coleta pelo primeiro campo ausente na **prioridade natural** (tipo,
data, convidados, nome, contato; `R31/F1`–`F5`) — omitida quando a saudação está
na mensagem, porque `R01/F1` já pergunta o tipo —, a
retomada (`R32/F1`) **seguida** dessa mesma pergunta, e a regra incompatível pelo
**motivo** de cada violação em `motivos_violacao` (`R33/F1` capacidade, `R17/F1`
tipo não aceito, `R18/F1` data bloqueada; cobertura com o mesmo token é a owner). Tokens com *bindings* (`R01/F1`, `R17/F1`, `R18/F1`,
`R33/F1`, `R34/F1`) só entram com veredito da **autoridade única** de emissibilidade sobre
a fotografia devolvida por `fotografar`; não emitível → zero fragmento (PE-7).
A mensagem fica **saudação → cobertura → demais mandatórios → coleta**.
"""

from __future__ import annotations

from collections.abc import Callable

from casa77_sdr.fragment_emissibility import (
    FotografiaFragmento,
    avaliar_emissibilidade,
)
from casa77_sdr.rules import MotivoViolacao
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
_CAMPOS_AUSENTES = "campos_ausentes"
_MOTIVOS_VIOLACAO = "motivos_violacao"
_FOTOGRAFAR = "fotografar"

# Mandatorio PURO: ele so chega por esta fronteira, pela acao de lacuna, e nunca
# por cobertura — colisao cross-source com ele continua fail-closed (PE-10). Ele
# e admissivel porque o corpus versionado prova mecanicamente — no teste de
# integracao, nunca aqui — que ele existe, que o seu rotulo canonico o admite e
# que ele **nao tem binding algum**, de modo que nenhuma decisao factual de
# runtime e necessaria para emiti-lo.
_LACUNA = "R03/F1"

# Mandatorio PURO da mensagem de encaminhamento ao interessado (`docs/04`
# "Mensagem ao interessado": e a resposta aprovada **R08**). Mesma classe
# estatica de `R03/F1`: so chega pela acao de T27, nunca por cobertura, e o
# corpus versionado prova no teste de integracao que ele existe, que o seu
# rotulo canonico o admite e que **nao tem binding algum**.
_ENCAMINHAMENTO = "R08/F1"

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

# --- M2.1: superficies conversacionais aprovadas pelo Victor (2026-10-08). ---

# Saudacao do 1o contato. Condicionada: tem bindings `RENDERIZADO` de origem
# `YAML`, logo so entra com veredito da autoridade unica (PE-24). Vai na FRENTE
# da cobertura (PE-25).
_SAUDACAO = "R01/F1"
# Ressalva de capacidade (so cabe coquetel). Condicionada, como a saudacao.
_RESSALVA_CAPACIDADE = "R34/F1"
# Despedida sem continuidade e reforco de encaminhamento: estaticos (zero
# bindings), como `R03/F1`.
_DESPEDIDA = "R15/F1"
_REFORCO_ENCAMINHAMENTO = "R35/F1"

# PE-21. Pergunta de coleta por campo tecnico de `Qualificacao.campos_ausentes`.
# Tabela FECHADA: campo fora dela (hoje, `formato`, que nao e perguntado por
# decisao do Victor) nao tem pergunta aprovada e nada acrescenta (PE-7).
_PERGUNTA_POR_CAMPO: dict[str, str] = {
    "nome": "R31/F1",
    "tipo_evento": "R31/F2",
    "data_nomeada": "R31/F3",
    "convidados": "R31/F4",
    "contato": "R31/F5",
}
# Prioridade natural da conversa (controller, 2026-10-08): pergunta-se o
# primeiro campo AUSENTE nesta ordem — a ordem de `campos_ausentes` nao conta.
_PRIORIDADE_COLETA: tuple[str, ...] = (
    "tipo_evento",
    "data_nomeada",
    "convidados",
    "nome",
    "contato",
)

# PE-22. Abertura da retomada; so existe seguida da pergunta do proximo campo.
_RETOMADA = "R32/F1"

# PE-23. Regra incompativel pelo motivo da violacao. Tabela FECHADA: motivo fora
# dela nada acrescenta (PE-7). `DATA_NAO_ACEITA` nasce de
# `eventos.datas_nao_aceitas`, exatamente o que `R18/F1` (datas bloqueadas)
# renderiza. `R33/F2` (horario) esta aprovado na base, mas nao ha motivo de
# violacao de horario: fica sem rota.
_INCOMPATIVEL_POR_MOTIVO: dict[MotivoViolacao, str] = {
    MotivoViolacao.TIPO_NAO_ACEITO: "R17/F1",
    MotivoViolacao.DATA_NAO_ACEITA: "R18/F1",
    MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE: "R33/F1",
}

# PE-24. Tokens com bindings fora de `R06/F1`: exigem veredito de emissibilidade
# sobre a fotografia devolvida por `fotografar`.
_CONDICIONADOS: frozenset[str] = frozenset(
    {_SAUDACAO, _RESSALVA_CAPACIDADE, *_INCOMPATIVEL_POR_MOTIVO.values()}
)

_ACAO_SAUDACAO = AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL
_ACAO_PERGUNTA = AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE
_ACAO_RETOMADA = AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR
_ACAO_INCOMPATIVEL = AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL

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
    AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL: (_SAUDACAO,),
    AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL: (),
    # As tres acoes de selecao por dado estruturado (PE-21–PE-23) tem `()` aqui:
    # o fragmento delas sai das tabelas fechadas acima, nunca desta.
    AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE: (),
    AcaoMaquina.PERGUNTAR_FORMATO: (),
    AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR: (),
    AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL: (),
    AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE: (_RESSALVA_CAPACIDADE,),
    AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA: (_CONDICOES_VISITA,),
    AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO: (_LACUNA,),
    AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE: (
        _FALLBACK_DISPONIBILIDADE,
    ),
    AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE: (_DESPEDIDA,),
    AcaoMaquina.REFORCAR_ENCAMINHAMENTO: (_REFORCO_ENCAMINHAMENTO,),
    AcaoMaquina.EMITIR_MENSAGEM_DE_ENCAMINHAMENTO: (_ENCAMINHAMENTO,),
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
    campos_ausentes: object = None,
    motivos_violacao: object = None,
    fotografar: object = None,
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

    **M2.1 (PE-21–PE-25).** `campos_ausentes` (tupla de `str`, na ordem do
    `Qualificador`) é exigido só com a ação de pergunta ou de retomada;
    `motivos_violacao` (tupla de `MotivoViolacao`) só com a regra incompatível;
    `fotografar` (`token -> FotografiaFragmento`) só quando um token condicionado
    é de fato acrescentado — chamado **no máximo uma vez por token**. Forma
    inválida fecha com `tipo_invalido` no localizador do parâmetro. Saída:
    **saudação**, depois os recebidos, depois os demais mandatórios na ordem das
    ações, e por último a **coleta** (retomada + pergunta, uma vez só).

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
    # PE-24. Vereditos locais dos condicionados do M2.1, um por token, na
    # propria chamada — zero cache global.
    vereditos: dict[str, bool] = {}
    # PE-25. A saudacao abre a mensagem; a coleta a fecha.
    abertura: list[str] = []
    coleta_pedida = False
    retomar = False

    for acao in acoes:
        if type(acao) is not AcaoMaquina:
            raise _nao_avaliavel(_TIPO_INVALIDO, _ACOES_ITEM)
        if acao not in _FRAGMENTOS_POR_ACAO:
            raise _nao_avaliavel(_ACAO_SEM_MAPEAMENTO, _ACOES_ITEM)

        if acao is _ACAO_PERGUNTA or acao is _ACAO_RETOMADA:
            # PE-21/PE-22. A pergunta e escolhida uma vez so, depois do laco:
            # pergunta e retomada no mesmo ciclo perguntam **uma** vez.
            coleta_pedida = True
            retomar = retomar or acao is _ACAO_RETOMADA
            continue

        if acao is _ACAO_INCOMPATIVEL:
            # PE-23. Um fragmento por motivo, na ordem das violacoes. Quando a
            # cobertura ja trouxe o mesmo token (ex.: `R18/F1` para pergunta de
            # datas), a cobertura e a owner e ele mantem a posicao original.
            tokens = tuple(
                _INCOMPATIVEL_POR_MOTIVO[motivo]
                for motivo in _conferir_motivos(motivos_violacao)
                if motivo in _INCOMPATIVEL_POR_MOTIVO
                and _INCOMPATIVEL_POR_MOTIVO[motivo] not in recebidos
            )
        else:
            tokens = _FRAGMENTOS_POR_ACAO[acao]

        for token in tokens:
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
            if token in _CONDICIONADOS:
                # PE-24. Mesma regra de `R06/F1` pela rota da acao: veredito da
                # autoridade unica; nao emitivel → zero fragmento (PE-7).
                if token not in vereditos:
                    vereditos[token] = _veredito(fotografar, token)
                if not vereditos[token]:
                    continue
            ja_mandatorios.add(token)
            if token == _SAUDACAO:
                abertura.append(token)
            else:
                mandatorios.append(token)

    coleta: list[str] = []
    # Com a saudacao na mensagem nao ha pergunta de coleta: `R01/F1` ja pergunta
    # o tipo de evento (controller, 2026-10-08).
    if coleta_pedida and not abertura:
        campos = _conferir_campos(campos_ausentes)
        pergunta = next(
            (_PERGUNTA_POR_CAMPO[campo] for campo in _PRIORIDADE_COLETA if campo in campos),
            None,
        )
        # Sem pergunta aprovada para o primeiro campo, a retomada nao fica solta.
        if pergunta is not None:
            if retomar:
                coleta.append(_RETOMADA)
            coleta.append(pergunta)

    for token in (*abertura, *mandatorios, *coleta):
        # Zero deduplicacao cross-source generica: um identificador que chegue
        # pelas duas origens significa modelagem incoerente a montante. As
        # excecoes sao **duas**, explicitas e independentes — `R05/F1` por
        # `PE-13` e `R06/F1` por `PE-15`-`PE-20` —, e ambas ja foram resolvidas
        # acima **por owner**: o token sequer entra neste bloco. Fora delas,
        # `PE-10` continua fail-closed.
        if token in recebidos:
            raise _nao_avaliavel(_CONFLITO_ORIGEM, _AUTORIZADOS_ITEM)

    return tuple(abertura) + fragmentos_autorizados + tuple(mandatorios) + tuple(coleta)


def _conferir_campos(campos_ausentes: object) -> tuple[str, ...]:
    if type(campos_ausentes) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _CAMPOS_AUSENTES)
    for campo in campos_ausentes:
        if type(campo) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _CAMPOS_AUSENTES)
    return campos_ausentes


def _conferir_motivos(motivos_violacao: object) -> tuple[MotivoViolacao, ...]:
    if type(motivos_violacao) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _MOTIVOS_VIOLACAO)
    for motivo in motivos_violacao:
        if type(motivo) is not MotivoViolacao:
            raise _nao_avaliavel(_TIPO_INVALIDO, _MOTIVOS_VIOLACAO)
    return motivos_violacao


def _veredito(fotografar: object, token: str) -> bool:
    """Consome a autoridade unica sobre a fotografia que o chamador monta."""
    if not isinstance(fotografar, Callable):
        raise _nao_avaliavel(_TIPO_INVALIDO, _FOTOGRAFAR)
    fotografia = fotografar(token)
    if type(fotografia) is not FotografiaFragmento:
        raise _nao_avaliavel(_TIPO_INVALIDO, _FOTOGRAFAR)
    return avaliar_emissibilidade(fotografia).emitivel


def _nao_avaliavel(categoria: str, localizador: str) -> ProjecaoEmissaoNaoAvaliavel:
    return ProjecaoEmissaoNaoAvaliavel(f"{categoria}: {localizador}")
