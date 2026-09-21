"""Recorte **R1** do `OrquestradorMotor` — etapas 1 a 3 e tratamento TS45.

Este módulo materializa o **primeiro prefixo executável** do componente
`OrquestradorMotor` de `docs/07-arquitetura-motor-respostas.md` §4.1: a
**normalização** da entrada (etapa 1), a **decisão de idempotência** (etapa
2), a **recuperação de contexto** (etapa 3) e o **tratamento operacional dos
bloqueios `S4`/`S5`** arbitrado em §7.1 (`TS45-1`–`TS45-20`). O contrato vivo
deste recorte está em §4.1.10 (`OMR1-1`–`OMR1-14`).

**Não é o `OrquestradorMotor` completo.** As etapas **4** a **14** — em
especial interpretação, identidade, atualização de dados, qualificação,
cobertura, composição dos insumos, `MaquinaEstados`, persistência da etapa 13
e emissão — **não** são coordenadas aqui. Este recorte **não é um 15º
componente**: §4.1 permanece com **14**, §2 com **nove** responsabilidades e o
pipeline de §5 com **catorze** etapas.

Superfície pública de **exatamente um** nome — `coordenar_etapas_1_a_3` —,
**não exportada** pelo `__init__.py` do pacote. **Nenhuma classe**, **nenhum
DTO**, **nenhum enum**, **nenhuma exceção pública nova** e **nenhum
`Protocol`**: as saídas são os tipos **já existentes** `EntradaNormalizada`
(etapa 1) e `ProjecoesIdentidadeEtapa3` (etapa 3).

**Zero default operacional.** A `janela_idempotencia` e o `limiar_recencia`
chegam **explícitos do chamador** (§4.3, risco 3b; §6.2, N-a-L1–N-a-L6), e a
**tentativa de alerta** chega **injetada** como dependência obrigatória
(`TS45-14`, `TS45-15`): este módulo **não escolhe** destino, canal, provedor,
transporte, formato nem confirmação de entrega — o **item 3a de §12 continua
ABERTO**, e ele bloqueia a **composição de produção**, não a existência deste
runtime local.

Fronteira: **nenhum relógio vivo** — o instante de referência do ciclo é o
campo "data e hora" da entrada (§6.1, N-a-R2) —, nenhum YAML, nenhuma base de
conhecimento, nenhum LLM, nenhuma rede, nenhum SDK, nenhum *logging*, nenhum
calendário e nenhuma constante temporal operacional.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta

from casa77_sdr.context import (
    ConjuntoHumanoIncoerente,
    IdentificadorNaoResolvido,
    ProjecaoIdentificadorIncoerente,
    ProjecoesIdentidadeEtapa3,
    montar_projecoes_identidade_etapa3,
)
from casa77_sdr.eligibility import (
    ConfiguracaoTemporalInvalida,
    ContextoElegibilidadeCorrompido,
    IdentificadoIncoerente,
    MarcoTemporalAusente,
)
from casa77_sdr.normalization import (
    EntradaMensagem,
    EntradaNormalizada,
    MensagemVazia,
    normalizar_entrada,
)
from casa77_sdr.persistence import PersistenciaOperacional, ProcessamentoPendente

__all__ = ["coordenar_etapas_1_a_3"]


def coordenar_etapas_1_a_3(
    entrada: EntradaMensagem,
    *,
    persistencia: PersistenciaOperacional,
    janela_idempotencia: timedelta,
    limiar_recencia: timedelta | None,
    tentar_alerta: Callable[..., object],
) -> tuple[EntradaNormalizada, ProjecoesIdentidadeEtapa3] | None:
    """Executa as etapas 1, 2 e 3 do pipeline, com o tratamento TS45.

    Devolve o par `(EntradaNormalizada, ProjecoesIdentidadeEtapa3)` quando a
    etapa 3 conclui. Devolve `None` nos **três** desfechos terminais deste
    recorte — mensagem vazia (§5, etapa 1), chave já processada (§4.3, etapa
    2) e bloqueio TS45 (§7.1) —, que são **estados distintos** e permanecem
    distinguíveis pelos **efeitos observáveis** na persistência, não por um
    código de retorno que este recorte não cria.

    `EntradaInvalida` — defeito de contrato de quem montou a entrada (§6.1) —
    **propaga intacta**: não é bloqueio de etapa 3 e **não** entra no gatilho
    fechado de TS45.

    No caminho feliz, **nada é marcado e nada é gravado**: a marcação da chave
    de idempotência do ciclo normal pertence às etapas posteriores, quando o
    ciclo completo existir.
    """
    # Passo 0 — contrato da dependência injetada, ANTES de qualquer etapa e
    # antes de tocar a persistência: um alerta inexequível tornaria o
    # tratamento TS45 incompleto justamente no caminho de falha. A mensagem
    # cita apenas o nome do parâmetro, nunca o valor recebido (§6.6).
    if not callable(tentar_alerta):
        raise TypeError("A dependência 'tentar_alerta' deve ser chamável")

    # Etapa 1 — normalizar e derivar a chave (§4.3). A janela é validada
    # exclusivamente por `normalizar_entrada`; este recorte não a revalida.
    try:
        entrada_normalizada = normalizar_entrada(entrada, janela_idempotencia)
    except MensagemVazia:
        # §5, etapa 1 — mensagem vazia não é processada, não produz transição
        # e **não produz efeito algum**: nem pendente, nem alerta, nem chave.
        return None

    # Etapa 2 — decidir duplicidade. Chave já marcada encerra o ciclo aqui,
    # com zero novo efeito (`TS45-9`, `E4-9`; doc 06 §4, passo 1).
    if persistencia.chave_processada(entrada_normalizada.chave_idempotencia):
        return None

    # Etapa 3 — recuperar contexto e montar as projeções de identidade (§6.2).
    # O limiar é **transportado**, não revalidado: `ConfiguracaoTemporalInvalida`
    # precisa nascer da autoridade já existente — `exigir_limiar_valido`, no
    # passo 1 de §6.2 — para cair no gatilho fechado de TS45 (S10).
    try:
        projecoes_identidade = montar_projecoes_identidade_etapa3(
            persistencia,
            canal=entrada.canal,
            contato=entrada.contato,
            id_atendimento_informado=entrada.id_atendimento,
            instante_de_referencia_do_ciclo=entrada.recebida_em,
            limiar_recencia=limiar_recencia,
        )
    except (
        ConfiguracaoTemporalInvalida,
        IdentificadorNaoResolvido,
        ContextoElegibilidadeCorrompido,
        MarcoTemporalAusente,
        IdentificadoIncoerente,
        ConjuntoHumanoIncoerente,
        ProjecaoIdentificadorIncoerente,
    ) as bloqueio:
        # `TS45-2` — gatilho fechado nas **sete** classes nomeadas. A captura
        # é por classe, nunca por `except ValueError:` genérico, e qualquer
        # outra exceção propaga intacta (`TS45-19`).
        _tratar_bloqueio_ts45(
            bloqueio,
            entrada=entrada,
            entrada_normalizada=entrada_normalizada,
            persistencia=persistencia,
            tentar_alerta=tentar_alerta,
        )
        return None

    return (entrada_normalizada, projecoes_identidade)


def _tratar_bloqueio_ts45(
    bloqueio: Exception,
    *,
    entrada: EntradaMensagem,
    entrada_normalizada: EntradaNormalizada,
    persistencia: PersistenciaOperacional,
    tentar_alerta: Callable[..., object],
) -> None:
    """Executa os efeitos de TS45 na ordem normativa (`TS45-7`).

    **1.** preservar o `ProcessamentoPendente`; **2.** **tentar** o alerta
    operacional; **3.** marcar a chave de idempotência; **4.** encerrar sem
    transição. Nada além disso: zero máquina, zero evento, zero transição,
    zero emissão, zero handoff, zero atendimento criado, zero etapa 5, zero
    etapa 13, zero `CondicoesCiclo`, zero S2-D8 e zero atualização de
    `instante_ultima_transicao` (`TS45-17`).

    O `finally` materializa a precedência de falhas de **OL-4** sem capturar a
    exceção da preservação: se `preservar_pendente` falhar, o alerta ainda é
    tentado — com `pendente_preservado=False` (`TS45-11`) —, a chave **não** é
    marcada, e a **exceção da preservação** propaga **por identidade**. Uma
    falha do alerta **não a substitui**, porque a tentativa é isolada e
    absorvida em `_tentar_alerta_operacional`.
    """
    pendente = ProcessamentoPendente(
        canal=entrada.canal,
        contato=entrada.contato,
        # `TS45-5` — a mensagem **normalizada** da etapa 1, nunca a bruta.
        conteudo=entrada_normalizada.mensagem_normalizada,
    )

    pendente_preservado = False
    try:
        persistencia.preservar_pendente(pendente)
        pendente_preservado = True
    finally:
        _tentar_alerta_operacional(
            tentar_alerta,
            # `TS45-3`/`TS45-14` — categoria **estrutural** do bloqueio: o
            # nome da classe, que distingue a causa para auditoria sem virar
            # enum, DTO, motivo de handoff ou evento, e sem `repr` da exceção.
            categoria=type(bloqueio).__name__,
            pendente_preservado=pendente_preservado,
            # A chave de idempotência é **opaca por construção** (§4.3) e por
            # isso serve de correlação auditável sem transportar mensagem,
            # canal, contato, `id_atendimento`, dado comercial nem segredo.
            correlacao=entrada_normalizada.chave_idempotencia,
        )

    # `TS45-8` — marcada **fora da etapa 13** e **somente após preservação
    # bem-sucedida**. Falha aqui propaga **por identidade** (`TS45-13`): sem
    # retry, sem compensação e sem apagar o pendente já protegido.
    persistencia.marcar_chave_processada(entrada_normalizada.chave_idempotencia)


def _tentar_alerta_operacional(
    tentar_alerta: Callable[..., object],
    *,
    categoria: str,
    pendente_preservado: bool,
    correlacao: str,
) -> None:
    """**Tenta** o alerta operacional, em caminho separado da conversa.

    `TS45-14` — o *payload* é fechado em **exatamente três** informações
    sanitizadas: a **categoria estrutural** do bloqueio, o **sucesso ou falha
    da preservação** e uma **correlação opaca**. A chamada é **por palavras-
    chave**, sem DTO e sem `Protocol`, e o retorno é **ignorado**: sucesso é a
    **ausência de exceção**, nunca uma confirmação de entrega.

    `TS45-12` — a entrega **não é garantida**. A falha da tentativa é
    absorvida aqui e **somente aqui**: este é o **único** `except Exception`
    do módulo, e ele envolve **exclusivamente** a chamada injetada. Zero
    retry, zero fila, zero contador, zero status de entrega e zero *fallback*
    para o canal da conversa.
    """
    try:
        tentar_alerta(
            categoria=categoria,
            pendente_preservado=pendente_preservado,
            correlacao=correlacao,
        )
    except Exception:
        return
