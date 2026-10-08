"""`OrquestradorMotor` — o ciclo ponta a ponta (doc 07 §4.1, §5).

Dois níveis convivem neste módulo:

- **`coordenar_etapas_1_a_3`** — o recorte **R1** (§4.1.10, `OMR1-1`–`OMR1-14`):
  **normalização** da entrada (etapa 1), **decisão de idempotência** (etapa
  2), **recuperação de contexto** (etapa 3) e o **tratamento operacional dos
  bloqueios `S4`/`S5`** arbitrado em §7.1 (`TS45-1`–`TS45-20`). Seu
  comportamento é o do R1 e não toca as etapas 4 a 14.
- **`processar_mensagem`** — o **ciclo completo** do M2: encadeia R1, as
  etapas 4–5 (`orchestrator_identity`), 6–7 (`orchestrator_decision`), 8–12
  (`orchestrator_emission`) e 13 (`orchestrator_persist`), e executa aqui a
  **etapa 14** (emissão). Devolve `ResultadoCiclo` com o `DesfechoCiclo`.

Etapa 14 (doc 07 §5; doc 06 §10) — **somente depois** de a etapa 13 gravar e
marcar a chave: 1) enviar o texto principal, se houver; 2) havendo resumo de
*handoff*, **tentar** entregá-lo; 3) **somente após sucesso**, enviar a
mensagem de encaminhamento. Falha de entrega (`FalhaEntregaResumo`) não
reverte o estado registrado, preserva o pendente e tenta o alerta, e o
encaminhamento **não** é enviado. `deve responder = false` sempre que
`situacao_takeover != SEM_TAKEOVER` ou estado `atendimento_humano`.

Desfechos antes da etapa 13: `AMBIGUA` — sem texto aprovado de esclarecimento
— é **silêncio** + alerta + marcação da chave; os demais desfechos terminais
de identidade já foram tratados pelas etapas 4–5; **Classe I** da etapa 7 →
preservar + alertar, chave **não** marcada, nada emitido (`BLOQUEADA_BASE`).

Este módulo **não é um 15º componente**: §4.1 permanece com **14**, §2 com
**nove** responsabilidades e o pipeline de §5 com **catorze** etapas. Nenhum
nome é exportado pelo `__init__.py` do pacote.

**Zero default operacional.** Janela, limiar, alerta, envio, entrega e
`gerar_id` chegam **explícitos do chamador** (§4.3, risco 3b; §6.2), e o
**item 3a de §12 continua ABERTO** (destino, canal e provedor do alerta).

Fronteira: **nenhum relógio vivo** — o instante de referência do ciclo é o
campo "data e hora" da entrada (§6.1, N-a-R2) —, nenhum YAML, nenhuma rede,
nenhum SDK, nenhum *logging* e nenhuma constante temporal operacional.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum

from casa77_sdr.alerta_operacional import (
    preservar_e_alertar,
    tentar_alerta_operacional,
)
from casa77_sdr.context import (
    ConjuntoHumanoIncoerente,
    IdentificadorNaoResolvido,
    ProjecaoIdentificadorIncoerente,
    ProjecoesIdentidadeEtapa3,
    montar_projecoes_identidade_etapa3,
)
from casa77_sdr.coverage_decision import DecisaoCoberturaNaoAvaliavel
from casa77_sdr.coverage_map import MapaCoberturaInvalido
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
from casa77_sdr.identity import SituacaoTakeover
from casa77_sdr.motor_deps import DependenciasMotor
from casa77_sdr.orchestrator_decision import decidir_primeira_chamada
from casa77_sdr.orchestrator_emission import TextoFinal, produzir_texto_final
from casa77_sdr.orchestrator_identity import (
    AlvoDoCiclo,
    DesfechoTerminal,
    coordenar_etapas_4_e_5,
)
from casa77_sdr.orchestrator_persist import persistir_ciclo
from casa77_sdr.persistence import PersistenciaOperacional, ProcessamentoPendente
from casa77_sdr.pricing_applicability import AplicabilidadeNaoAvaliavel
from casa77_sdr.response_assertion import AssertivaNaoAvaliavel
from casa77_sdr.response_index import IndiceInvalido
from casa77_sdr.response_index_tokens import ProjecaoDeIdentidadeInvalida
from casa77_sdr.state_machine import Estado

__all__ = [
    "DesfechoCiclo",
    "FalhaEntregaResumo",
    "ResultadoCiclo",
    "coordenar_etapas_1_a_3",
    "processar_mensagem",
]


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

    A sequência preservar → tentar alerta, com a precedência de falhas de
    **OL-4**, vive em `alerta_operacional.preservar_e_alertar`: se
    `preservar_pendente` falhar, o alerta ainda é tentado — com
    `pendente_preservado=False` (`TS45-11`) —, a chave **não** é marcada, e a
    **exceção da preservação** propaga **por identidade**.
    """
    pendente = ProcessamentoPendente(
        canal=entrada.canal,
        contato=entrada.contato,
        # `TS45-5` — a mensagem **normalizada** da etapa 1, nunca a bruta.
        conteudo=entrada_normalizada.mensagem_normalizada,
    )

    preservar_e_alertar(
        persistencia=persistencia,
        pendente=pendente,
        # `TS45-3`/`TS45-14` — categoria **estrutural** do bloqueio: o nome da
        # classe, que distingue a causa para auditoria sem virar enum, DTO,
        # motivo de handoff ou evento, e sem `repr` da exceção.
        categoria=type(bloqueio).__name__,
        # A chave de idempotência é **opaca por construção** (§4.3) e por isso
        # serve de correlação auditável sem transportar mensagem, canal,
        # contato, `id_atendimento`, dado comercial nem segredo.
        correlacao=entrada_normalizada.chave_idempotencia,
        tentar_alerta=tentar_alerta,
    )

    # `TS45-8` — marcada **fora da etapa 13** e **somente após preservação
    # bem-sucedida**. Falha aqui propaga **por identidade** (`TS45-13`): sem
    # retry, sem compensação e sem apagar o pendente já protegido.
    persistencia.marcar_chave_processada(entrada_normalizada.chave_idempotencia)


# ==========================================================================
# Ciclo completo — `processar_mensagem` e etapa 14
# ==========================================================================


class DesfechoCiclo(StrEnum):
    """Como o ciclo de uma mensagem terminou."""

    IGNORADA = "ignorada"  # vazia, duplicada ou bloqueio TS45
    TERMINAL_IDENTIDADE = "terminal_identidade"  # desfechos terminais das etapas 4–5
    BLOQUEADA_PERSISTENCIA = "bloqueada_persistencia"  # etapa 13 falhou (§7.2)
    BLOQUEADA_BASE = "bloqueada_base"  # Classe I antes da etapa 7
    RESPONDIDA = "respondida"  # algo foi enviado ao interessado
    SILENCIOSA = "silenciosa"  # gravado, nada enviado ao interessado


@dataclass(frozen=True)
class ResultadoCiclo:
    """Resultado observável do ciclo.

    `texto_emitido` é o texto principal enviado — ou a mensagem de
    encaminhamento quando foi a única enviada —; `estado_final` é o estado
    **gravado** pela etapa 13, `None` quando nada foi gravado.
    """

    desfecho: DesfechoCiclo
    texto_emitido: str | None
    estado_final: Estado | None


class FalhaEntregaResumo(Exception):
    """Contrato de `entregar_resumo`: a entrega do resumo a Douglas falhou.

    É a **única** falha de entrega que a etapa 14 trata (doc 06 §10); qualquer
    outra exceção do chamável injetado propaga intacta.
    """


#: Categoria estrutural do alerta de `AMBIGUA` sem esclarecimento aprovado.
_CATEGORIA_AMBIGUA = DesfechoTerminal.AMBIGUA.name

_IGNORADA = ResultadoCiclo(DesfechoCiclo.IGNORADA, None, None)


def processar_mensagem(
    entrada: EntradaMensagem,
    deps: DependenciasMotor,
    *,
    gerar_id: Callable[[], str],
) -> ResultadoCiclo:
    """Executa o ciclo completo (etapas 1–14) para uma mensagem recebida.

    Desfechos tratados (bloqueio TS45, terminais de identidade, Classe I,
    `FalhaDePersistencia`, `FalhaEntregaResumo`) voltam como `ResultadoCiclo`.
    Contrato de exceções para o adaptador de canal — as demais **propagam**:

    :raises ValueError: / :raises TypeError: erro de contrato das etapas 4–7
        (ex.: E-Nb da interpretação). Nada é preservado; a chave **não** é
        marcada.
    :raises SelecaoNaoAvaliavel: / :raises ComposicaoNaoAvaliavel: /
        :raises MontagemRespostaNaoAvaliavel: /
        :raises ProjecaoEmissaoNaoAvaliavel: etapas 8–12. Não há `pendente`
        e a chave **não** é marcada.
    :raises: falha de `preservar_pendente` (pelas etapas 4–5, TS45, Classe I,
        etapa 13 ou resumo): propaga **por identidade**.
    :raises: falha de `marcar_chave_processada` (etapa 13): o estado já foi
        gravado, mas a chave **não** fica marcada — a reentrega reaplica o ciclo.
    :raises: falha de `enviar_mensagem` (etapa 14): o estado permanece gravado
        e a chave marcada; sem retry.
    """
    # Etapas 1–3 (+ TS45).
    etapas_1_a_3 = coordenar_etapas_1_a_3(
        entrada,
        persistencia=deps.persistencia,
        janela_idempotencia=deps.janela_idempotencia,
        limiar_recencia=deps.limiar_recencia,
        tentar_alerta=deps.tentar_alerta,
    )
    if etapas_1_a_3 is None:
        return _IGNORADA
    entrada_normalizada, projecoes = etapas_1_a_3
    chave = entrada_normalizada.chave_idempotencia

    # Etapas 4–5.
    alvo = coordenar_etapas_4_e_5(entrada, entrada_normalizada, projecoes, deps)
    if isinstance(alvo, DesfechoTerminal):
        if alvo is DesfechoTerminal.AMBIGUA:
            # A3 — não existe texto aprovado de esclarecimento: silêncio, alerta
            # (superfície sem unidade aprovada) e marcação da chave. O pendente
            # já foi preservado pelas etapas 4–5 (A7).
            tentar_alerta_operacional(
                deps.tentar_alerta,
                categoria=_CATEGORIA_AMBIGUA,
                pendente_preservado=True,
                correlacao=chave,
            )
            deps.persistencia.marcar_chave_processada(chave)
        return ResultadoCiclo(DesfechoCiclo.TERMINAL_IDENTIDADE, None, None)

    # Etapas 6–7. Classe I bloqueia antes da máquina (D8-CI7–D8-CI14).
    try:
        primeira = decidir_primeira_chamada(
            alvo,
            base_motor=deps.base_motor,
            calendario_integrado=deps.calendario_integrado,
            e01_confirmado=True,
            contato_canal=entrada.contato,
        )
    except (
        DecisaoCoberturaNaoAvaliavel,
        AplicabilidadeNaoAvaliavel,
        IndiceInvalido,
        MapaCoberturaInvalido,
        ProjecaoDeIdentidadeInvalida,
        AssertivaNaoAvaliavel,
    ) as classe_i:
        # Preservar → alertar; a chave **não** é marcada (reprocessável depois
        # de a base ser corrigida); nada é emitido.
        preservar_e_alertar(
            persistencia=deps.persistencia,
            pendente=_pendente_do_ciclo(entrada, entrada_normalizada.mensagem_normalizada),
            categoria=type(classe_i).__name__,
            correlacao=chave,
            tentar_alerta=deps.tentar_alerta,
        )
        return ResultadoCiclo(DesfechoCiclo.BLOQUEADA_BASE, None, None)

    # Etapas 8–12.
    texto_final = produzir_texto_final(
        primeira,
        base_motor=deps.base_motor,
        estado_inicial=alvo.atendimento.estado,
        mensagem=entrada_normalizada.mensagem_normalizada,
        tentar_alerta=deps.tentar_alerta,
        correlacao=chave,
    )

    # Etapa 13 — antecede a 14 sem exceção.
    gravado = persistir_ciclo(
        deps=deps,
        alvo=alvo,
        primeira=primeira,
        texto_final=texto_final,
        entrada=entrada,
        entrada_normalizada=entrada_normalizada,
        gerar_id=gerar_id,
    )
    if not gravado:
        return ResultadoCiclo(DesfechoCiclo.BLOQUEADA_PERSISTENCIA, None, None)
    *_, ultima = texto_final.decisoes_do_ciclo
    estado_final = ultima.estado_final

    # Etapa 14.
    if not _deve_responder(alvo, estado_final):
        return ResultadoCiclo(DesfechoCiclo.SILENCIOSA, None, estado_final)
    emitido = _emitir(
        texto_final,
        entrada=entrada,
        mensagem_normalizada=entrada_normalizada.mensagem_normalizada,
        chave=chave,
        deps=deps,
    )
    desfecho = DesfechoCiclo.SILENCIOSA if emitido is None else DesfechoCiclo.RESPONDIDA
    return ResultadoCiclo(desfecho, emitido, estado_final)


def _deve_responder(alvo: AlvoDoCiclo, estado_final: Estado) -> bool:
    """R5 / I03 — takeover ou `atendimento_humano` silenciam a automação."""
    return (
        alvo.decisao_identidade.situacao_takeover is SituacaoTakeover.SEM_TAKEOVER
        and alvo.atendimento.estado is not Estado.ATENDIMENTO_HUMANO
        and estado_final is not Estado.ATENDIMENTO_HUMANO
    )


def _emitir(
    texto_final: TextoFinal,
    *,
    entrada: EntradaMensagem,
    mensagem_normalizada: str,
    chave: str,
    deps: DependenciasMotor,
) -> str | None:
    """Etapa 14 na ordem obrigatória; devolve o texto emitido (ou `None`).

    1. texto principal; 2. tentar entregar o resumo; 3. **somente após
    sucesso**, a mensagem de encaminhamento (doc 06 §10). Falha do envio ao
    interessado propaga (estado já gravado; sem retry).
    """
    emitido: str | None = None
    if texto_final.texto is not None:
        deps.enviar_mensagem(entrada.canal, entrada.contato, texto_final.texto)
        emitido = texto_final.texto

    if texto_final.resumo_handoff is None:
        return emitido
    try:
        deps.entregar_resumo(texto_final.resumo_handoff)
    except FalhaEntregaResumo as falha:
        # Doc 06 §10 — não reverte o estado; preserva o pendente de forma
        # opaca; tenta o alerta; não afirma o handoff ao interessado.
        preservar_e_alertar(
            persistencia=deps.persistencia,
            pendente=_pendente_do_ciclo(entrada, mensagem_normalizada),
            categoria=type(falha).__name__,
            correlacao=chave,
            tentar_alerta=deps.tentar_alerta,
        )
        return emitido

    if texto_final.texto_encaminhamento is not None:
        deps.enviar_mensagem(entrada.canal, entrada.contato, texto_final.texto_encaminhamento)
        if emitido is None:
            emitido = texto_final.texto_encaminhamento
    return emitido


def _pendente_do_ciclo(
    entrada: EntradaMensagem, mensagem_normalizada: str
) -> ProcessamentoPendente:
    return ProcessamentoPendente(
        canal=entrada.canal,
        contato=entrada.contato,
        conteudo=mensagem_normalizada,
    )
