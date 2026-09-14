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
consulta, **não** avalia se um fragmento é emitível agora, **não** avalia regra
comercial, **não** resolve *binding*, **não** monta texto, **não** chama LLM e
**não** executa ação alguma. Ela **projeta identificadores**, e mais nada.

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

***Fail-closed*.** Forma inválida, repetição no bloco recebido, ação sem entrada
na tabela e colisão entre as duas origens **fecham** — sem resultado parcial,
sem correção silenciosa e sem composição improvisada.
"""

from __future__ import annotations

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
    duas entradas, a unicidade dentro da tupla recebida, a totalidade da tabela
    e a colisão entre as duas origens.
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

# Unico fragmento aprovado materializado como mandatorio nesta versao. Ele e
# admissivel porque o corpus versionado prova mecanicamente — no teste de
# integracao, nunca aqui — que ele existe, que o seu rotulo canonico o admite e
# que ele **nao tem binding algum**, de modo que nenhuma decisao factual de
# runtime e necessaria para emiti-lo.
_LACUNA = "R03/F1"

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
    AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA: (),
    AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO: (_LACUNA,),
    AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE: (),
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
) -> tuple[str, ...]:
    """Projeta os fragmentos destinados à emissão neste ciclo.

    `fragmentos_autorizados` é a tupla **já produzida** por S2-D8
    (`SF-D4-10`); `acoes` são as ações da **primeira** decisão da máquina
    (§4.5). Esta fronteira **não reavalia** nenhuma das duas.

    A ordem é **fixa**: **1.** a forma da tupla recebida — `tuple` exata, itens
    `str` exatos, **sem repetição**; **2.** a forma das ações — `tuple` exata,
    itens do vocabulário fechado, **todos com entrada na tabela**; **3.** o
    bloco mandatório, percorrendo `acoes` na ordem recebida e acrescentando cada
    identificador declarado **apenas na sua primeira ocorrência**; **4.** a
    ausência de colisão entre as duas origens.

    Devolve `fragmentos_autorizados + mandatórios`: **todos** os identificadores
    recebidos primeiro, **na ordem recebida**, e então os mandatórios, **na
    ordem das ações**. Nenhum identificador se repete, nenhum é removido e
    nenhuma ordenação própria é aplicada.

    Levanta `ProjecaoEmissaoNaoAvaliavel` com `tipo_invalido`
    (`fragmentos_autorizados`, `fragmentos_autorizados.item`, `acoes`,
    `acoes.item`), `duplicidade` (`fragmentos_autorizados.item`),
    `acao_sem_mapeamento` (`acoes.item`) e `conflito_origem`
    (`fragmentos_autorizados.item`). **Nada é capturado** e **nenhum resultado
    parcial é devolvido**.

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

    for acao in acoes:
        if type(acao) is not AcaoMaquina:
            raise _nao_avaliavel(_TIPO_INVALIDO, _ACOES_ITEM)
        if acao not in _FRAGMENTOS_POR_ACAO:
            raise _nao_avaliavel(_ACAO_SEM_MAPEAMENTO, _ACOES_ITEM)

        for token in _FRAGMENTOS_POR_ACAO[acao]:
            # Acao repetida, ou duas acoes que declarem o mesmo identificador,
            # contribuem **uma vez**: vence a primeira ocorrencia.
            if token in ja_mandatorios:
                continue
            ja_mandatorios.add(token)
            mandatorios.append(token)

    for token in mandatorios:
        # Zero deduplicacao entre as duas origens: um identificador que chegue
        # pelas duas significa modelagem incoerente a montante.
        if token in recebidos:
            raise _nao_avaliavel(_CONFLITO_ORIGEM, _AUTORIZADOS_ITEM)

    return fragmentos_autorizados + tuple(mandatorios)


def _nao_avaliavel(categoria: str, localizador: str) -> ProjecaoEmissaoNaoAvaliavel:
    return ProjecaoEmissaoNaoAvaliavel(f"{categoria}: {localizador}")
