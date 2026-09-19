"""Produtor determinístico de **S2-D8** — pendências e cobertura de resposta.

Esta fronteira materializa a arbitragem de `docs/07` §4.4.1: ela responde as
**duas** perguntas de **D8-0a**, em **dois eixos semanticamente independentes**
— o eixo **A**, de qualificação, e o eixo **B**, de resposta —, **antes da
etapa 7** (§5).

**Ela não é um 15º componente**: §4.1 permanece com **14**, e **nenhuma etapa
nova é criada**. Ela também **não pertence à máquina**: `state_machine` **não é
importado**, `Evento.E09` **não é criado nem confirmado** e nenhuma condição de
§4.4 é alterada. O que sai daqui são **causas estruturadas que podem confirmar
`E09`** — a transformação em evento pertence à **integração posterior**
(**D8-E8**).

**Fronteira pura.** Zero I/O, *filesystem*, rede, LLM, relógio, **calendário**,
ambiente, *logging*, *cache* e mutação de entrada. Tudo chega **já carregado**
pelo chamador: a `Interpretacao`, a `Qualificacao` provisória, o mapa `R2`, o
índice de `C`, o `ResultadoConsistencia` e a **fotografia factual de runtime**.
**`knowledge/**` não é aberto.**

**Eixo A — `Q1` literal.** No **schema e no corpus atuais**, `pendencia_impeditiva`
é **legitimamente inalcançável** (**Q1-d**): os campos determinantes da
qualificação são **pré-requisitos da base**, recusados pelo carregador (**Q1-a**,
**Q1-b**), e ali o motor **não inicia** — o que não é caso de ciclo. Logo esta
fronteira devolve **sempre** `pendencia_impeditiva = False`,
`pendencias_impeditivas = ()` e **zero causa do eixo A**. **Nenhum mecanismo é
inventado** para tornar **D8-T2f** alcançável, e **`Q2` permanece futura e não
autorizada** (**Q1-e**). `qualification.py`, `rules.py`, `knowledge.py` e a
máquina **não mudam** (**Q1-c**).

**Eixo B — cobertura.** Consome **somente** `PerguntaComercial` de confiança
**`ALTA`** (**D8-B1**); a chave semântica é o **`AssuntoComercial`** (**D8-B2**),
**nunca o texto**. Por assunto: a **primeira ocorrência efetiva** define a ordem
(**SF-D4-7**); **todos os grupos aplicáveis** são avaliados (**SF-D4-5**,
**SF-D4-5a**, **D8-L4**); vale
**conjunção entre grupos** e **disjunção dentro do grupo** (**R2-4**); o
***witness*** é a **primeira alternativa emitível na ordem declarada**
(**SF-D4-3**); e **qualquer grupo descoberto zera os tokens daquele assunto** —
**não existe resposta parcial de assunto** (**SF-D4-6**, **R2-5**, **D8-L3**).
Ao final, o ***witness*** escolhido mais de uma vez é **deduplicado pela
primeira ocorrência** (**SF-D4-9**), e a tupla resultante é
`fragmentos_autorizados` (**SF-D4-10**).

**D8-F, sem ampliação.** Um fragmento é emitível agora **somente se** o status é
`APROVADO` (**D8-F1**), **todos** os *bindings* `RENDERIZADO` necessários
resolvem para valor disponível (**D8-F2**) e **toda `ASSERTIVA` aplicável é
verdadeira** (**D8-F3**). `AGUARDA_APROVACAO` e `BLOQUEADO` **não habilitam**
(**D8-F4**). **Qualquer `Divergencia`** registrada pelo `ValidadorConsistenciaBase`
— inclusive **`FORMATO_INAPLICAVEL`** — **bloqueia o fragmento por Classe II**
(**D8-CII1**, **D8-CII3**), e isso **não** faz do formato uma **quarta
condição**: a conferência é de quem a produziu, e aqui ela é apenas **consumida**
(**R2F-12**). Esta fronteira **não executa formatador**, **não resolve YAML** e
**não reavalia `ASSERTIVA` de origem `YAML`**.

**Runtime é fotografia recebida, nunca consulta.** `fatos_runtime` é a
**fotografia factual autoritativa produzida a montante**. Esta fronteira **não
consulta calendário**, **não escolhe provedor** e **não afirma verdade
operacional própria**. Sobre o corpus atual, o fato runtime sustenta
**exclusivamente** `ASSERTIVA` (**C-A2-V**) e vive **somente** em `R05/F2` e
`R05/F3`; *binding* `RUNTIME_AUTORITATIVO` **fora desse contrato** exige **nova
arbitragem** e **fecha** aqui.

**Gate de candidatura de preço — `D8-G`.** Antes de **D8-F**, e **independente
da ordem declarada em `R2`**, a **aplicabilidade de pacote** (§4.4.4) decide a
candidatura de `R09/F1` e `R09/F2`, que são **faixas distintas e nunca
substitutas**: `FAIXA_INFERIOR` deixa **só `R09/F1`** candidato;
`FAIXA_SUPERIOR`, **só `R09/F2`**; `INDETERMINADO` deixa **os dois**, porque a
resposta correta ainda depende do que falta saber; `NENHUM_APLICAVEL` deixa
**nenhum**. Quando um desses dois tokens é **efetivamente avaliado** e a
aplicabilidade **não chega** — ou chega com tipo inválido —, a fronteira
**fecha** como **Classe I**: adivinhar faixa seria inventar preço.

**Grupos aplicáveis — `D8-L4`.** Um grupo é **aplicável** no ciclo quando tem
**ao menos uma alternativa candidata**. Grupo **sem nenhuma** candidata **não é
coberto nem descoberto**: ele **não produz *witness*, não produz causa** e fica
**fora da avaliação daquele ciclo**. Mas um assunto **com grupos declarados** e
**zero grupos aplicáveis** **não é respondível** e produz
`SEM_RESPOSTA_APROVADA_EMITIVEL` — **nunca** verdadeiro por vacuidade.

**Gate de candidatura de `R05`.** Antes de **D8-F**, e **independente da ordem
futura das alternativas em `R2`**: `R05/F1` é candidato **somente** quando
`consulta_calendario_valida is False`; `R05/F2` e `R05/F3` são candidatos
**somente** quando ela é `True`. Assim o caminho de *fallback* **não depende** de
como o mapa venha a declarar a ordem. Com a consulta **válida**,
`data_disponivel` **precisa existir e ser `bool`**, e os dois fragmentos seguem
**submetidos aos seus próprios predicados**. Com a consulta **não válida**,
`R05/F1` é o caminho candidato e **nenhum `E09` é produzido pelo runtime** se ele
cobrir o grupo. **`False` não equivale a ausência**: ausência, tipo inválido e
consulta válida sem `data_disponivel` são **Classe I**, *fail-closed*.

**Causas — exatamente dois motivos, e a classificação que os acompanha.**
`CAMPO_INDISPONIVEL` e `SEM_RESPOSTA_APROVADA_EMITIVEL`, **sem terceiro**
(**D8-E**). Cada causa carrega também a **classificação** de **D8-E6**, que é o
que separa **T11/T18** de **T12/T19**: causa do **eixo A** que satisfaça
`IMP-1`–`IMP-4` é **`IMPEDITIVA`**; causa do **eixo B** é **`ACESSORIA`**. Como
o eixo A é **inalcançável sob `Q1`**, **toda causa produzida hoje é
`ACESSORIA`** — a representação `IMPEDITIVA` existe porque o contrato já a
define, e **não** porque esta fronteira a torne alcançável.

Causas **só existem quando um grupo fica efetivamente descoberto**: alternativa
reprovada **dentro de grupo coberto** por alternativa segura **não cria lacuna,
não cria `E09` e não força handoff** (**D8-L2**, **D8-CII5**) — e nesse caso
**todas** as causas das alternativas rejeitadas daquele grupo são **descartadas**.

**Todas as causas estruturais da lacuna são avaliadas** (**D8-E4**), nunca só a
primeira: um fragmento com **vários** `ReferenteIndisponivel` produz **uma causa
por referente**, cada uma com o seu `caminho_yaml`; e um fragmento que acumule
**divergência de Classe II** e **`C-7`** em *bindings* distintos produz **os dois
motivos**. Um grupo que termine **sem *witness*** e **sem nenhuma causa
estrutural coletada** — porque todas as suas alternativas foram **não
candidatas** — produz, ainda assim,
`SEM_RESPOSTA_APROVADA_EMITIVEL`: **grupo descoberto nunca fica silencioso**.

A deduplicação é **determinística e estável**, pela primeira ocorrência sob a
ordem fixa de avaliação, e a identidade estrutural da causa é o conjunto
`(motivo, classificacao, assunto, caminho_yaml)` (**D8-E4**).

**Classe I — base não avaliável.** Índice ausente ou inválido, mapa inválido,
referência pendurada, `ResultadoConsistencia` incoerente e runtime fora do
contrato **bloqueiam antes da etapa 7**, **sem resultado parcial** (**D8-CI**).
A exceção da fronteira de origem **atravessa intacta**; o que é defeito **desta**
composição sai como `DecisaoCoberturaNaoAvaliavel`. Classe I **não** vira `E09`,
**não** vira `pendencia_impeditiva` e **não** vira item de `pendencias_resposta`
(**D8-CI14**).

**Escopo isolado.** Materializar este produtor **não** cria o conteúdo de `R2`,
**não** cria `knowledge/mapa-cobertura.yaml`, **não** integra a etapa 10
*end-to-end*, **não** implementa o `OrquestradorMotor` e **não** confirma evento
algum.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from casa77_sdr.coverage_map import conferir_referencias
from casa77_sdr.fragment_emissibility import (
    FotografiaFragmento,
    ImpedimentoEmissao,
    avaliar_emissibilidade,
)
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    AssuntoComercial,
    Interpretacao,
    PerguntaComercial,
)
from casa77_sdr.pricing_applicability import AplicabilidadePacote
from casa77_sdr.qualification import Qualificacao
from casa77_sdr.response_consistency import (
    Divergencia,
    ReferenteIndisponivel,
    ResultadoConsistencia,
)
from casa77_sdr.response_index import validar_indice
from casa77_sdr.response_index_tokens import derivar_tokens_do_indice

__all__ = [
    "CausaE09",
    "ClassificacaoPendencia",
    "DecisaoCoberturaNaoAvaliavel",
    "MotivoE09",
    "ResultadoS2D8",
    "decidir_pendencias_e_cobertura",
]


class MotivoE09(StrEnum):
    """Vocabulário **fechado** dos motivos de `E09` — **exatamente dois**.

    `CAMPO_INDISPONIVEL` — um *binding* necessário resolveu para `null` ou para
    estrutura cujo `status` é `pendente` (**C-7**), e isso deixou um **grupo
    descoberto**. No eixo B ele carrega o **caminho YAML estrutural** e o
    **assunto** (**D8-E7**).

    `SEM_RESPOSTA_APROVADA_EMITIVEL` — status não emitível, divergência de
    Classe II — inclusive `ASSERTIVA` falsa —, **zero grupos** ou
    **`ASSUNTO_NAO_CLASSIFICADO`** deixaram um grupo descoberto.

    **Nenhum terceiro motivo pode ser criado.**
    """

    CAMPO_INDISPONIVEL = "CAMPO_INDISPONIVEL"
    SEM_RESPOSTA_APROVADA_EMITIVEL = "SEM_RESPOSTA_APROVADA_EMITIVEL"


class ClassificacaoPendencia(StrEnum):
    """Vocabulário **fechado** de **D8-E6** — **impeditiva × acessória**.

    É esta classificação, e não o motivo, que separa **T11/T18** de
    **T12/T19** (doc 06 §2.2). Causa do **eixo A** que satisfaça
    `IMP-1`–`IMP-4` é **`IMPEDITIVA`**; causa do **eixo B** é **`ACESSORIA`**.

    **`IMPEDITIVA` existe porque o contrato a define**, não porque esta
    fronteira a produza: sob **`Q1`** o eixo A é **legitimamente inalcançável**
    (**Q1-d**), e **nada aqui o torna alcançável**.
    """

    IMPEDITIVA = "IMPEDITIVA"
    ACESSORIA = "ACESSORIA"


@dataclass(frozen=True, slots=True)
class CausaE09:
    """Uma causa estrutural que **pode** confirmar `E09` — nunca o evento.

    Carrega **exatamente quatro** coisas: o **motivo**, a **classificação** de
    **D8-E6**, o **assunto** — quando há consulta — e o **`caminho_yaml`**, que
    **`CAMPO_INDISPONIVEL` sempre carrega**. Ele é o metadado **estrutural** que
    **D8-E7** autoriza, transportado literalmente do `ReferenteIndisponivel`
    já conferido a montante, **sem reinterpretação e sem nova resolução**.

    **Nunca** o valor do campo, o texto da pergunta, PII, valor comercial ou
    `Rxx`. O contrato dos dois campos opcionais é este:
    **`CAMPO_INDISPONIVEL` sempre carrega `caminho_yaml`**, e o `assunto` é
    `None` no **eixo A** e preenchido no **eixo B**;
    **`SEM_RESPOSTA_APROVADA_EMITIVEL` é causa do eixo B**, `ACESSORIA`, com
    `assunto` e **`caminho_yaml = None`**. Sob `Q1`, a causa do eixo A é
    **inalcançável nesta versão**, e `Q2` **não é implementada**.

    Estas causas são **metadados estruturados de auditoria a montante**: elas
    **não integram `CondicoesCiclo`** e **não são entrada da `MaquinaEstados`**
    (**D8-E8**).
    """

    motivo: MotivoE09
    classificacao: ClassificacaoPendencia
    assunto: AssuntoComercial | None = None
    caminho_yaml: str | None = None


@dataclass(frozen=True, slots=True)
class ResultadoS2D8:
    """O que S2-D8 produz, e **nada além disso**.

    `pendencia_impeditiva` e `pendencias_impeditivas` são a **condição 2** e a
    evidência técnica do eixo A (**D8-A2**, **D8-A3**).
    `resposta_aprovada_disponivel` é a **condição 4** (**D8-B3**).
    `fragmentos_autorizados` é a projeção de **SF-D4-10**, já deduplicada.
    `pendencias_resposta` carrega **perguntas do interessado**, jamais motivos
    técnicos (**D8-P1**) — e por isso fica **fora do `repr`**.
    `causas_e09` são causas estruturadas — motivo **mais** a classificação de
    **D8-E6** —, **não** o evento.

    **Não existe `e09_confirmado`**: confirmar `E09` pertence à integração
    posterior, e esta fronteira **não decide evento** (**D8-E8**).
    """

    pendencia_impeditiva: bool
    pendencias_impeditivas: tuple[str, ...]
    resposta_aprovada_disponivel: bool
    fragmentos_autorizados: tuple[str, ...]
    pendencias_resposta: tuple[PerguntaComercial, ...] = field(repr=False)
    causas_e09: tuple[CausaE09, ...] = ()


class DecisaoCoberturaNaoAvaliavel(Exception):
    """Classe I desta composição — a base **não permite sequer avaliar**.

    A mensagem tem a forma `<categoria>: <localizador>`. A categoria diz **o
    que** está errado e o localizador diz **em que posição da chamada** — nunca
    o token, o `Rxx`, o fragmento, o assunto, o texto da pergunta, o valor
    recebido, o `repr`, o tipo concreto ou uma cardinalidade.

    Ela cobre **apenas** o que nenhuma fronteira existente julga. Índice, mapa e
    identidade continuam sendo julgados pelas suas próprias fronteiras, e as
    suas exceções **atravessam intactas**.
    """


# Categorias fechadas de Classe I desta fronteira.
_TIPO_INVALIDO = "tipo_invalido"
_VALOR_INVALIDO = "valor_invalido"
_CAMPO_AUSENTE = "campo_ausente"
_DUPLICIDADE = "duplicidade"
_COMBINACAO_INVALIDA = "combinacao_invalida"

# Localizadores estruturais. Nomeiam a posicao da chamada, nunca o conteudo.
_INTERPRETACAO = "interpretacao"
_QUALIFICACAO = "qualificacao_provisoria"
_CONSISTENCIA = "consistencia"
_STATUS = "consistencia.status_por_fragmento"
_STATUS_ITEM = "consistencia.status_por_fragmento.item"
_DIVERGENCIAS_ITEM = "consistencia.divergencias.item"
_INDISPONIVEIS_ITEM = "consistencia.referentes_indisponiveis.item"
_TOKENS_DIVERGENTES = "consistencia.tokens_divergentes"
_TOKENS_DIVERGENTES_ITEM = "consistencia.tokens_divergentes.item"
_RUNTIME_NAO_AVALIADOS = "consistencia.bindings_runtime_nao_avaliados"
_RUNTIME_NAO_AVALIADOS_ITEM = "consistencia.bindings_runtime_nao_avaliados.item"
_FATOS_RUNTIME = "fatos_runtime"
_FATOS_RUNTIME_CHAVE = "fatos_runtime.chave"
_FATOS_RUNTIME_VALOR = "fatos_runtime.valor"
_INDICE_BINDING_RUNTIME = "indice.binding_runtime"

# Vocabulario de status (C-3). A autoridade continua no indice; aqui ele so
# delimita o que pode chegar no resultado ja produzido a montante.
_APROVADO = "APROVADO"
_STATUS_CANONICO = frozenset({_APROVADO, "AGUARDA_APROVACAO", "BLOQUEADO"})

# Vocabulario fechado de fato runtime (C-A2-V). Nenhum valor novo e criado.
_CONSULTA_VALIDA = "consulta_calendario_valida"
_DATA_DISPONIVEL = "data_disponivel"
_FATOS_CANONICOS = frozenset({_CONSULTA_VALIDA, _DATA_DISPONIVEL})

# Mecanismos ja arbitrados (C-4, C-5).
_RENDERIZADO = "RENDERIZADO"
_ASSERTIVA = "ASSERTIVA"
_RUNTIME_AUTORITATIVO = "RUNTIME_AUTORITATIVO"

_SEPARADOR = "/"
_PONTO = "."

# Gate de candidatura de `R05` — os **unicos** tokens de runtime arbitrados.
# `R05/F1` e o caminho sem confirmacao segura; `R05/F2` e `R05/F3` dependem de
# consulta valida. Isto **nao** torna a fronteira conhecedora de conteudo
# comercial: sao identificadores estruturais, como `R03/F1` em §4.1.5.
_R05_SEM_CONSULTA = f"R05{_SEPARADOR}F1"
_R05_DISPONIVEL = f"R05{_SEPARADOR}F2"
_R05_INDISPONIVEL = f"R05{_SEPARADOR}F3"
_TOKENS_COM_GATE = frozenset(
    {_R05_SEM_CONSULTA, _R05_DISPONIVEL, _R05_INDISPONIVEL}
)
_TOKENS_COM_RUNTIME = frozenset({_R05_DISPONIVEL, _R05_INDISPONIVEL})

# Gate de candidatura de preco — `D8-G`. `R09/F1` e `R09/F2` sao **faixas
# distintas**, nunca substitutas: nenhuma delas cobre o grupo da outra. Sao
# identificadores estruturais, como `R05` acima e `R03/F1` em §4.1.5.
_R09_FAIXA_INFERIOR = f"R09{_SEPARADOR}F1"
_R09_FAIXA_SUPERIOR = f"R09{_SEPARADOR}F2"
_TOKENS_COM_GATE_PRECO = frozenset({_R09_FAIXA_INFERIOR, _R09_FAIXA_SUPERIOR})

_APLICABILIDADE = "aplicabilidade"

# Desfechos internos da avaliacao de uma alternativa. Sentinelas privadas: o
# vocabulario publico de motivo e `MotivoE09`, e ele nao descreve alternativa.
_EMITIVEL = object()

_AUSENTE = object()


def decidir_pendencias_e_cobertura(
    interpretacao: object,
    qualificacao_provisoria: object,
    mapa: object,
    indice: object,
    consistencia: object,
    fatos_runtime: object,
    aplicabilidade: object = None,
) -> ResultadoS2D8:
    """Decide pendências e cobertura **antes da etapa 7**, e nada além disso.

    Todas as entradas chegam **já carregadas**: esta fronteira **não abre
    arquivo algum**, **não consulta calendário** e **não chama LLM**.

    `aplicabilidade` é o veredito de **§4.4.4**, já decidido a montante. Ela é
    **opcional**: um ciclo em que **nenhum token de preço** é avaliado não
    precisa dela. Mas quando `R09/F1` ou `R09/F2` **é efetivamente avaliado** e
    ela **não chega**, a fronteira **fecha** — **D8-G**.

    A ordem é **fixa**: **1.** as formas das entradas; **2.** o índice
    (`validar_indice`); **3.** o mapa e as suas referências
    (`conferir_referencias`); **4.** o domínio canônico de identidade; **5.** a
    coerência do `ResultadoConsistencia`; **6.** o eixo A; **7.** o eixo B, por
    assunto, por grupo, por alternativa; **8.** a projeção deduplicada e as
    causas.

    Devolve `ResultadoS2D8`. Levanta `DecisaoCoberturaNaoAvaliavel` no que é
    defeito **desta** composição; `IndiceInvalido`, `MapaCoberturaInvalido`,
    `ProjecaoDeIdentidadeInvalida` e `AssertivaNaoAvaliavel` **atravessam
    intactas**. **Nenhum resultado parcial** é devolvido.

    **DECIDIR COBERTURA NÃO É RESPONDER.** O texto pertence às fronteiras de
    §4.1.3–§4.1.6; a emissão, à etapa 10; o evento, à máquina.
    """
    if type(interpretacao) is not Interpretacao:
        raise _nao_avaliavel(_TIPO_INVALIDO, _INTERPRETACAO)
    if type(qualificacao_provisoria) is not Qualificacao:
        raise _nao_avaliavel(_TIPO_INVALIDO, _QUALIFICACAO)

    fatos = _validar_fatos_runtime(fatos_runtime)
    if aplicabilidade is not None and (
        type(aplicabilidade) is not AplicabilidadePacote
    ):
        raise _nao_avaliavel(_TIPO_INVALIDO, _APLICABILIDADE)

    # Classe I por fronteira de origem: as excecoes atravessam intactas.
    validar_indice(indice)
    conferir_referencias(mapa, indice)

    dominio = frozenset(derivar_tokens_do_indice(indice))
    # A projecao de runtime vem **antes**: ela produz o registro esperado de
    # `bindings_runtime_nao_avaliados`, contra o qual a coerencia e conferida.
    runtime_por_token, registro_runtime = _projetar_runtime(indice)
    status_por_token = _validar_consistencia(
        consistencia, dominio, registro_runtime
    )
    bloqueados = frozenset(consistencia.tokens_divergentes)
    indisponiveis = _projetar_indisponiveis(consistencia)

    # Eixo A — `Q1` literal: nada e produzido no schema vigente.
    pendencia_impeditiva = False
    pendencias_impeditivas: tuple[str, ...] = ()

    grupos_por_assunto = _projetar_mapa(mapa)
    perguntas_efetivas = tuple(
        pergunta
        for pergunta in interpretacao.perguntas_comerciais
        if pergunta.confianca is Confianca.ALTA
    )

    assuntos: list[AssuntoComercial] = []
    for pergunta in perguntas_efetivas:
        # SF-D4-7: a ordem e a da **primeira ocorrencia efetiva**, e duplicata
        # do mesmo assunto **nao repete a selecao**.
        if pergunta.assunto not in assuntos:
            assuntos.append(pergunta.assunto)

    tokens: list[str] = []
    causas: list[CausaE09] = []
    nao_respondiveis: set[AssuntoComercial] = set()

    for assunto in assuntos:
        witnesses, causas_do_assunto = _avaliar_assunto(
            assunto,
            grupos_por_assunto,
            status_por_token,
            bloqueados,
            indisponiveis,
            runtime_por_token,
            fatos,
            aplicabilidade,
        )
        if witnesses is None:
            nao_respondiveis.add(assunto)
            causas.extend(causas_do_assunto)
            continue
        # SF-D4-6: os *witnesses* do assunto so entram com **todos** os grupos
        # cobertos; e ai nao ha causa conversacional alguma (D8-L2).
        tokens.extend(witnesses)

    # SF-D4-9: a deduplicacao acontece **aqui**, pela primeira ocorrencia.
    fragmentos_autorizados: list[str] = []
    for token in tokens:
        if token not in fragmentos_autorizados:
            fragmentos_autorizados.append(token)

    # D8-T4b/c/d: com zero pergunta efetiva a condicao 4 e `False`; com ao menos
    # um assunto integralmente coberto, `True`.
    respondiveis = [
        assunto for assunto in assuntos if assunto not in nao_respondiveis
    ]
    resposta_aprovada_disponivel = bool(respondiveis)

    # D8-P3/P4/P5: as **perguntas** do interessado, na ordem original, com
    # duplicatas preservadas. `BAIXA` nunca entra, e o eixo A nao cria pergunta.
    pendencias_resposta = tuple(
        pergunta
        for pergunta in perguntas_efetivas
        if pergunta.assunto in nao_respondiveis
    )

    return ResultadoS2D8(
        pendencia_impeditiva=pendencia_impeditiva,
        pendencias_impeditivas=pendencias_impeditivas,
        resposta_aprovada_disponivel=resposta_aprovada_disponivel,
        fragmentos_autorizados=tuple(fragmentos_autorizados),
        pendencias_resposta=pendencias_resposta,
        causas_e09=_deduplicar(causas),
    )


def _avaliar_assunto(
    assunto: AssuntoComercial,
    grupos_por_assunto: dict[str, list[Any]],
    status_por_token: dict[str, str],
    bloqueados: frozenset[str],
    indisponiveis: dict[str, tuple[str, str]],
    runtime_por_token: dict[str, tuple[tuple[str, str], ...]],
    fatos: dict[str, bool],
    aplicabilidade: object,
) -> tuple[list[str] | None, list[CausaE09]]:
    """Avalia **um** assunto: `None` de *witnesses* significa não respondível.

    **R2-6**: `ASSUNTO_NAO_CLASSIFICADO` tem **zero grupos por definição** e
    **não é respondível**. **R2-5**: um assunto é respondível quando possui ao
    menos um grupo e **todos** os seus grupos possuem ao menos uma alternativa
    emitível agora — lido agora sobre os **grupos aplicáveis** (**R2-5a**).

    **D8-L4.** Grupo **sem nenhuma alternativa candidata** é **inaplicável**:
    fica **fora da avaliação** do ciclo, sem *witness* e sem causa. Assunto com
    grupos declarados e **zero grupos aplicáveis** **não é respondível** e
    produz `SEM_RESPOSTA_APROVADA_EMITIVEL` — **nunca** verdadeiro por vacuidade.
    """
    if assunto is AssuntoComercial.ASSUNTO_NAO_CLASSIFICADO:
        return None, [_sem_resposta(assunto)]

    grupos = grupos_por_assunto[assunto.value]
    if not grupos:
        return None, [_sem_resposta(assunto)]

    witnesses: list[str] = []
    causas: list[CausaE09] = []
    coberto = True
    aplicaveis = 0

    for grupo in grupos:
        # D8-L4: a candidatura e decidida **antes**, e um grupo sem nenhuma
        # alternativa candidata sai inteiro da avaliacao deste ciclo.
        candidatas = [
            f"{alternativa['rxx']}{_SEPARADOR}{alternativa['fragmento']}"
            for alternativa in grupo["alternativas"]
        ]
        candidatas = [
            token
            for token in candidatas
            if _e_candidato(token, fatos, aplicabilidade)
        ]
        if not candidatas:
            continue
        aplicaveis += 1

        witness: str | None = None
        causas_do_grupo: list[CausaE09] = []
        for token in candidatas:
            desfecho = _avaliar_alternativa(
                token,
                assunto,
                status_por_token,
                bloqueados,
                indisponiveis,
                runtime_por_token,
                fatos,
            )
            if desfecho is _EMITIVEL:
                # SF-D4-3: a **primeira** alternativa emitivel na ordem
                # declarada, sem qualquer criterio implicito de desempate.
                witness = token
                break
            causas_do_grupo.extend(desfecho)
        if witness is None:
            # D8-L1/D8-L3: so o **grupo inteiro descoberto** produz causa.
            coberto = False
            if not causas_do_grupo:
                # Guarda defensiva: grupo descoberto **nunca fica silencioso**.
                causas_do_grupo.append(_sem_resposta(assunto))
            causas.extend(causas_do_grupo)
        else:
            witnesses.append(witness)

    if aplicaveis == 0:
        # D8-L4: grupos declarados, nenhum aplicavel. Nao e cobertura vazia
        # verdadeira — e ausencia de resposta.
        return None, [_sem_resposta(assunto)]
    if not coberto:
        return None, causas
    return witnesses, []


def _avaliar_alternativa(
    token: str,
    assunto: AssuntoComercial,
    status_por_token: dict[str, str],
    bloqueados: frozenset[str],
    indisponiveis: dict[str, tuple[str, str]],
    runtime_por_token: dict[str, tuple[tuple[str, str], ...]],
    fatos: dict[str, bool],
) -> object:
    """Devolve `_EMITIVEL` ou a **lista** de causas da alternativa.

    A alternativa recebida **já é candidata**: o *gate* de candidatura corre
    **antes**, em `_avaliar_assunto`, porque é ele que decide quais grupos são
    **aplicáveis** (**D8-L4**).

    A **emissibilidade estrutural** em si — **D8-F1**, **Classe II**, **C-7** e
    **`ASSERTIVA` de runtime**, nessa ordem fixa — pertence à **primitiva
    compartilhada** de §4.4.5, que é **uma só implementação** de **D8-F**. Aqui
    fica o que é **de S2-D8**: montar a fotografia do token e **projetar** cada
    impedimento devolvido na `CausaE09` correspondente, **com o assunto**.

    **Todas as causas estruturais da alternativa são coletadas** (**D8-E4**):
    um fragmento com vários `ReferenteIndisponivel` produz **uma causa por
    referente**, e um fragmento que acumule divergência e `C-7` em *bindings*
    distintos produz **os dois motivos**. O status não emitível é a exceção:
    ali o fragmento **sequer é aprovado**, e o veredito é único.
    """
    resultado = avaliar_emissibilidade(
        FotografiaFragmento(
            status=status_por_token[token],
            divergente=token in bloqueados,
            # A ordem fisica dos referentes e preservada; o mecanismo nao entra
            # na emissibilidade, so o caminho ja conferido a montante.
            referentes_indisponiveis=tuple(
                referente for _, referente in indisponiveis.get(token, ())
            ),
            # O valor do fato e resolvido **aqui**: a fotografia factual
            # autoritativa e de S2-D8, e a primitiva so recebe o par ja pronto.
            assertivas_runtime=tuple(
                (predicado, fatos[fato])
                for fato, predicado in runtime_por_token.get(token, ())
            ),
        )
    )
    if resultado.emitivel:
        return _EMITIVEL
    return [
        _projetar_causa(impedimento, assunto)
        for impedimento in resultado.impedimentos
    ]


def _projetar_causa(
    impedimento: ImpedimentoEmissao, assunto: AssuntoComercial
) -> CausaE09:
    """Projeta **um** impedimento estrutural na causa de S2-D8 que lhe cabe.

    É **aqui** que o vocabulário de **D8-E** entra, e **somente aqui**: a
    primitiva **não** conhece `MotivoE09`, `ClassificacaoPendencia` nem
    `AssuntoComercial`. **Impedimento com caminho** é `CAMPO_INDISPONIVEL`, com
    o `caminho_yaml` **transportado literalmente**; **impedimento sem caminho**
    é `SEM_RESPOSTA_APROVADA_EMITIVEL`. Ambos são do **eixo B**, logo
    **`ACESSORIA`** (**D8-E6**), e **nenhum terceiro motivo é criado**.
    """
    if impedimento.caminho_yaml is None:
        return _sem_resposta(assunto)
    return CausaE09(
        MotivoE09.CAMPO_INDISPONIVEL,
        ClassificacaoPendencia.ACESSORIA,
        assunto,
        impedimento.caminho_yaml,
    )


def _sem_resposta(assunto: AssuntoComercial) -> CausaE09:
    """Causa do **eixo B**, logo **`ACESSORIA`** (**D8-E6**), e sem caminho."""
    return CausaE09(
        MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL,
        ClassificacaoPendencia.ACESSORIA,
        assunto,
    )


def _e_candidato(
    token: str, fatos: dict[str, bool], aplicabilidade: object
) -> bool:
    """Gates de candidatura, aplicados **antes** de `D8-F`.

    São **dois**, e alcançam **cinco** tokens estruturais — nenhum outro:

    **`D8-G`, preço.** `R09/F1` e `R09/F2` são **faixas distintas e nunca
    substitutas**. `FAIXA_INFERIOR` deixa só `R09/F1` candidato;
    `FAIXA_SUPERIOR`, só `R09/F2`; `INDETERMINADO` deixa **os dois**, porque a
    faixa ainda depende do que falta saber; `NENHUM_APLICAVEL` deixa **nenhum**.
    Aplicabilidade **ausente** quando um desses tokens é avaliado é **Classe I**.

    **`R05`, disponibilidade.** Ele torna o caminho de *fallback* independente
    da ordem declarada em `R2`: `R05/F1` só é candidato sem consulta válida, e
    `R05/F2`/`R05/F3` só com consulta válida. **Ausência não é `False`.**

    Qualquer outro token do corpus **é candidato por padrão**: nenhum *gate*
    genérico é criado.
    """
    if token in _TOKENS_COM_GATE_PRECO:
        return _e_candidato_por_faixa(token, aplicabilidade)

    if token not in _TOKENS_COM_GATE:
        return True

    valida = fatos.get(_CONSULTA_VALIDA, _AUSENTE)
    if valida is _AUSENTE:
        raise _nao_avaliavel(_CAMPO_AUSENTE, f"{_FATOS_RUNTIME}.{_CONSULTA_VALIDA}")

    if token == _R05_SEM_CONSULTA:
        return not valida

    if not valida:
        return False
    if _DATA_DISPONIVEL not in fatos:
        raise _nao_avaliavel(
            _CAMPO_AUSENTE, f"{_FATOS_RUNTIME}.{_DATA_DISPONIVEL}"
        )
    return True


def _e_candidato_por_faixa(token: str, aplicabilidade: object) -> bool:
    """`D8-G`: a faixa aplicável decide qual token de preço é candidato.

    A tabela é **estrutural e fechada** — `R09/F1` ↔ faixa inferior, `R09/F2` ↔
    faixa superior —, e **não** carrega limite, valor ou qualquer dado
    comercial. **Nenhum dos dois é *fallback* do outro**: com a faixa decidida,
    o grupo do outro token simplesmente **não é aplicável** neste ciclo.
    """
    if aplicabilidade is None:
        # Adivinhar faixa seria inventar preco: fecha antes da etapa 7.
        raise _nao_avaliavel(_CAMPO_AUSENTE, _APLICABILIDADE)
    if type(aplicabilidade) is not AplicabilidadePacote:
        raise _nao_avaliavel(_TIPO_INVALIDO, _APLICABILIDADE)

    if aplicabilidade is AplicabilidadePacote.INDETERMINADO:
        return True
    if aplicabilidade is AplicabilidadePacote.NENHUM_APLICAVEL:
        return False
    if aplicabilidade is AplicabilidadePacote.FAIXA_INFERIOR:
        return token == _R09_FAIXA_INFERIOR
    return token == _R09_FAIXA_SUPERIOR


def _validar_fatos_runtime(fatos_runtime: object) -> dict[str, bool]:
    """Exige a forma de `dict[str, bool]` sobre o vocabulário fechado.

    A **ausência** de um fato é legítima aqui — ela só fecha quando `R05` é
    efetivamente avaliado. Chave fora de **C-A2-V** e valor que não seja `bool`
    **exato** fecham de imediato: `False` **não** equivale a ausência, e um
    inteiro **não** vira booleano.
    """
    if type(fatos_runtime) is not dict:
        raise _nao_avaliavel(_TIPO_INVALIDO, _FATOS_RUNTIME)

    for chave, valor in fatos_runtime.items():
        if type(chave) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _FATOS_RUNTIME_CHAVE)
        if chave not in _FATOS_CANONICOS:
            raise _nao_avaliavel(_VALOR_INVALIDO, _FATOS_RUNTIME_CHAVE)
        if type(valor) is not bool:
            raise _nao_avaliavel(_TIPO_INVALIDO, _FATOS_RUNTIME_VALOR)
    return dict(fatos_runtime)


def _validar_consistencia(
    consistencia: object,
    dominio: frozenset[str],
    registro_runtime: tuple[str, ...],
) -> dict[str, str]:
    """Exige coerência **integral** do `ResultadoConsistencia` recebido.

    A conferência é do chamador a montante; o que se prova aqui é que o
    resultado recebido **fala do mesmo corpus**: um status por token do domínio
    canônico, sem faltar nem sobrar, e todo token citado pertencente a esse
    domínio. Sem isso, consumir o resultado seria adivinhar.
    """
    if type(consistencia) is not ResultadoConsistencia:
        raise _nao_avaliavel(_TIPO_INVALIDO, _CONSISTENCIA)

    if type(consistencia.status_por_fragmento) is not tuple:
        raise _nao_avaliavel(_TIPO_INVALIDO, _STATUS)

    status_por_token: dict[str, str] = {}
    for par in consistencia.status_por_fragmento:
        if type(par) is not tuple or len(par) != 2:
            raise _nao_avaliavel(_TIPO_INVALIDO, _STATUS_ITEM)
        token, status = par
        if type(token) is not str or type(status) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _STATUS_ITEM)
        if token not in dominio:
            raise _nao_avaliavel(_VALOR_INVALIDO, _STATUS_ITEM)
        if status not in _STATUS_CANONICO:
            raise _nao_avaliavel(_VALOR_INVALIDO, _STATUS_ITEM)
        if token in status_por_token:
            raise _nao_avaliavel(_DUPLICIDADE, _STATUS_ITEM)
        status_por_token[token] = status

    if status_por_token.keys() != dominio:
        raise _nao_avaliavel(_CAMPO_AUSENTE, _STATUS)

    for item in consistencia.divergencias:
        if type(item) is not Divergencia:
            raise _nao_avaliavel(_TIPO_INVALIDO, _DIVERGENCIAS_ITEM)
        if item.token not in dominio:
            raise _nao_avaliavel(_VALOR_INVALIDO, _DIVERGENCIAS_ITEM)

    for item in consistencia.referentes_indisponiveis:
        if type(item) is not ReferenteIndisponivel:
            raise _nao_avaliavel(_TIPO_INVALIDO, _INDISPONIVEIS_ITEM)
        if item.token not in dominio:
            raise _nao_avaliavel(_VALOR_INVALIDO, _INDISPONIVEIS_ITEM)

    vistos: set[str] = set()
    for token in consistencia.tokens_divergentes:
        if type(token) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _TOKENS_DIVERGENTES_ITEM)
        if token in vistos:
            raise _nao_avaliavel(_DUPLICIDADE, _TOKENS_DIVERGENTES_ITEM)
        vistos.add(token)

    # VCB-10: `tokens_divergentes` e **exatamente** a projecao de
    # `divergencias` pela primeira ocorrencia, **na ordem recebida**. A
    # comparacao e **literal**: reordenar tambem e resultado incoerente, e por
    # isso nenhum conjunto decide a equivalencia aqui.
    esperado_divergentes: list[str] = []
    for item in consistencia.divergencias:
        if item.token not in esperado_divergentes:
            esperado_divergentes.append(item.token)
    if consistencia.tokens_divergentes != tuple(esperado_divergentes):
        raise _nao_avaliavel(_COMBINACAO_INVALIDA, _TOKENS_DIVERGENTES)

    for item in consistencia.bindings_runtime_nao_avaliados:
        if type(item) is not str:
            raise _nao_avaliavel(_TIPO_INVALIDO, _RUNTIME_NAO_AVALIADOS_ITEM)

    # VCB-7: o registro auditavel dos *bindings* deixados fora do escopo
    # factual e **exatamente** a projecao de runtime do indice, na ordem
    # fisica. Ausente, extra, repetido ou reordenado e resultado incoerente.
    if consistencia.bindings_runtime_nao_avaliados != registro_runtime:
        raise _nao_avaliavel(_COMBINACAO_INVALIDA, _RUNTIME_NAO_AVALIADOS)

    return status_por_token


def _projetar_indisponiveis(
    consistencia: ResultadoConsistencia,
) -> dict[str, tuple[tuple[str, str], ...]]:
    """`token -> ((mecanismo, referente), ...)`, **todos**, na ordem recebida.

    Reduzir ao primeiro perderia causa estrutural: **D8-E4** manda avaliar
    **todas** as causas da lacuna, e cada `ReferenteIndisponivel` carrega o seu
    próprio `caminho_yaml`. **D8-F6** continua valendo sobre a emissão — o
    fragmento é emitível inteiro ou não é —, e não sobre a auditoria da causa.
    """
    projecao: dict[str, list[tuple[str, str]]] = {}
    for item in consistencia.referentes_indisponiveis:
        projecao.setdefault(item.token, []).append(
            (item.mecanismo, item.referente)
        )
    return {token: tuple(itens) for token, itens in projecao.items()}


def _projetar_runtime(
    indice: object,
) -> tuple[dict[str, tuple[tuple[str, str], ...]], tuple[str, ...]]:
    """Projeta o runtime do índice: avaliação **e** registro esperado.

    Devolve `token -> ((fato_runtime, predicado), ...)`, na ordem física, e a
    tupla `<token>.<nome>` de **todos** os *bindings* `RUNTIME_AUTORITATIVO`,
    também na ordem física — a forma exata de `bindings_runtime_nao_avaliados`
    (**VCB-7**), contra a qual a coerência do resultado recebido é conferida.

    O índice já foi validado por `validar_indice`; **nenhuma gramática de
    índice é duplicada aqui**. **Runtime fora do contrato arbitrado** — isto é,
    em token diferente de `R05/F2` e `R05/F3` — **fecha**: ele exigiria **nova
    arbitragem**, e presumir semântica seria inventá-la.
    """
    projecao: dict[str, tuple[tuple[str, str], ...]] = {}
    registro: list[str] = []
    for resposta in indice["respostas"]:
        for fragmento in resposta["fragmentos"]:
            token = f"{resposta['id']}{_SEPARADOR}{fragmento['id']}"
            bindings = [
                binding
                for binding in fragmento["bindings"]
                if binding["origem"] == _RUNTIME_AUTORITATIVO
            ]
            if not bindings:
                continue
            if token not in _TOKENS_COM_RUNTIME:
                raise _nao_avaliavel(
                    _COMBINACAO_INVALIDA, _INDICE_BINDING_RUNTIME
                )
            projecao[token] = tuple(
                (binding["fato_runtime"], binding["predicado"])
                for binding in bindings
            )
            registro.extend(
                f"{token}{_PONTO}{binding['nome']}" for binding in bindings
            )
    return projecao, tuple(registro)


def _projetar_mapa(mapa: object) -> dict[str, list[Any]]:
    """`assunto -> grupos`, preservando a ordem física declarada.

    O mapa já foi validado e é **total** (`R2F-3`): cada assunto aparece
    exatamente uma vez, de modo que a projeção é uma bijeção.
    """
    return {item["assunto"]: item["grupos"] for item in mapa["assuntos"]}


def _deduplicar(causas: list[CausaE09]) -> tuple[CausaE09, ...]:
    """Deduplica pela **primeira ocorrência**, sob a ordem fixa de avaliação.

    A identidade estrutural comparada é o conjunto
    `(motivo, classificacao, assunto, caminho_yaml)` — a igualdade do próprio
    DTO `frozen`. A ordem é a de assunto → grupo → alternativa, e por isso é
    **estável**: a mesma entrada produz sempre a mesma sequência (**D8-E4**).
    **Nenhuma ordenação lexical é aplicada.**
    """
    vistas: list[CausaE09] = []
    for causa in causas:
        if causa not in vistas:
            vistas.append(causa)
    return tuple(vistas)


def _nao_avaliavel(
    categoria: str, localizador: str
) -> DecisaoCoberturaNaoAvaliavel:
    return DecisaoCoberturaNaoAvaliavel(f"{categoria}: {localizador}")
