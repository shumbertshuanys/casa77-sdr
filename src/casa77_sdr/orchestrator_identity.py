"""Etapas 4 e 5 do ciclo — interpretação única, identidade e desfechos terminais.

Coordena a **etapa 4** (`executar_interpretacao_do_ciclo`, chamada **uma única
vez** por ciclo — CN4) e a **etapa 5** (`resolver_identidade`), e encerra o
ciclo nos desfechos terminais anteriores à `MaquinaEstados`
(`docs/07-arquitetura-motor-respostas.md` §5; `docs/06-maquina-de-estados.md`
§4.5):

- `FalhaProdutorInterpretacao` — nenhuma `Interpretacao` (N-b-M1/M2): preservar
  o pendente, **tentar** o alerta e **não** marcar a chave (reprocessável);
  zero emissão neste marco (decisão do controlador; N-b-M4/M5);
- `HUMANO_MULTIPLO` — R5-P0: preservar, alertar, marcar; zero máquina;
- `SEM_CANDIDATO_ELEGIVEL` — contrato E4 (`E4-6`–`E4-12`): preservar, alertar,
  marcar; zero emissão;
- `AMBIGUA` — A1–A7: sem transição, nada herdado, pendente persistido (A7).

Nos demais caminhos devolve o `AlvoDoCiclo` com o atendimento hidratado:
`HUMANO_UNICO` sobre o registro em `atendimento_humano`; `NOVA_SOLICITACAO` e
primeiro contato sobre um atendimento novo (nada herdado, I15);
`ATENDIMENTO_ATIVO` e `MESMA_SOLICITACAO` sobre o alvo persistido.

`ValueError`/`TypeError` de contrato propagam intactos. Nenhum relógio vivo,
nenhuma emissão.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from casa77_sdr.context import ProjecoesIdentidadeEtapa3
from casa77_sdr.hydration import AtendimentoHidratado, hidratar
from casa77_sdr.identity import (
    CriterioIdentidade,
    DecisaoIdentidade,
    SituacaoTakeover,
    resolver_identidade,
)
from casa77_sdr.interpretation_llm import FalhaProdutorInterpretacao
from casa77_sdr.interpretation_stage import (
    ArtefatosInterpretacao,
    executar_interpretacao_do_ciclo,
)
from casa77_sdr.motor_deps import DependenciasMotor
from casa77_sdr.normalization import EntradaMensagem, EntradaNormalizada
from casa77_sdr.persistence import (
    PersistenciaOperacional,
    ProcessamentoPendente,
    ResultadoRecuperacao,
)
from casa77_sdr.state_machine import Estado, Identidade

__all__ = ["AlvoDoCiclo", "DesfechoTerminal", "coordenar_etapas_4_e_5"]


class DesfechoTerminal(StrEnum):
    """Ciclos que encerram nas etapas 4–5, antes da `MaquinaEstados`."""

    INTERPRETACAO_INDISPONIVEL = "interpretacao_indisponivel"
    AMBIGUA = "ambigua"
    SEM_CANDIDATO_ELEGIVEL = "sem_candidato_elegivel"
    HUMANO_MULTIPLO = "humano_multiplo"


@dataclass(frozen=True)
class AlvoDoCiclo:
    """O ciclo prossegue para a etapa 6 sobre este atendimento."""

    artefatos: ArtefatosInterpretacao
    decisao_identidade: DecisaoIdentidade
    atendimento: AtendimentoHidratado


def coordenar_etapas_4_e_5(
    entrada: EntradaMensagem,
    entrada_normalizada: EntradaNormalizada,
    projecoes: ProjecoesIdentidadeEtapa3,
    deps: DependenciasMotor,
) -> AlvoDoCiclo | DesfechoTerminal:
    """Executa as etapas 4 e 5 e devolve o alvo do ciclo ou o desfecho terminal."""
    # Etapa 4 — interpretação **uma única vez** por ciclo (CN4).
    try:
        artefatos = executar_interpretacao_do_ciclo(
            entrada_normalizada.mensagem_normalizada,
            produtor=deps.produtor,
            prompt_sistema=deps.prompt_sistema,
        )
    except FalhaProdutorInterpretacao as falha:
        # N-b-M1/M2 — sem `Interpretacao` a etapa 5 não executa. A chave
        # **não** é marcada: a mensagem continua reprocessável.
        _preservar_e_alertar(
            categoria=type(falha).__name__,
            entrada=entrada,
            entrada_normalizada=entrada_normalizada,
            persistencia=deps.persistencia,
            tentar_alerta=deps.tentar_alerta,
        )
        return DesfechoTerminal.INTERPRETACAO_INDISPONIVEL

    # Etapa 5 — identidade.
    decisao = resolver_identidade(
        projecoes.candidatos_elegiveis,
        artefatos.projecao_identidade,
        projecoes.veredito_identificador,
        projecoes.id_atendimento_validado,
        projecoes.havia_estado_esperado,
        projecoes.ids_em_atendimento_humano,
    )

    # R5-P0 — takeover precede a cascata.
    if decisao.situacao_takeover is SituacaoTakeover.HUMANO_MULTIPLO:
        _preservar_alertar_marcar(
            categoria=SituacaoTakeover.HUMANO_MULTIPLO.name,
            entrada=entrada,
            entrada_normalizada=entrada_normalizada,
            persistencia=deps.persistencia,
            tentar_alerta=deps.tentar_alerta,
        )
        return DesfechoTerminal.HUMANO_MULTIPLO

    if decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO:
        atendimento = _hidratar_alvo(decisao, entrada, deps.persistencia)
        if atendimento.estado is not Estado.ATENDIMENTO_HUMANO:
            raise ValueError("alvo HUMANO_UNICO fora de atendimento_humano")
        return AlvoDoCiclo(artefatos, decisao, atendimento)

    # SEM_TAKEOVER — os seis resultados da cascata.
    if decisao.criterio is CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL:
        # Contrato E4 (`E4-8`): preservar → alertar → marcar → encerrar.
        _preservar_alertar_marcar(
            categoria=CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL.name,
            entrada=entrada,
            entrada_normalizada=entrada_normalizada,
            persistencia=deps.persistencia,
            tentar_alerta=deps.tentar_alerta,
        )
        return DesfechoTerminal.SEM_CANDIDATO_ELEGIVEL

    if decisao.identidade is Identidade.AMBIGUA:
        # A1–A7 — sem transição e nada herdado; A7 exige persistir o pendente.
        # A1–A7 não pedem alerta; a chave fica para quem emitir o
        # esclarecimento (A3), depois da emissão.
        deps.persistencia.preservar_pendente(_pendente(entrada, entrada_normalizada))
        return DesfechoTerminal.AMBIGUA

    if decisao.identidade in (Identidade.ATENDIMENTO_ATIVO, Identidade.MESMA_SOLICITACAO):
        atendimento = _hidratar_alvo(decisao, entrada, deps.persistencia)
        return AlvoDoCiclo(artefatos, decisao, atendimento)

    if decisao.identidade is Identidade.NOVA_SOLICITACAO or (
        decisao.criterio is CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO
    ):
        # I15 — atendimento novo, sem reutilizar dado do anterior.
        return AlvoDoCiclo(artefatos, decisao, hidratar(None))

    raise ValueError("decisão de identidade fora do vocabulário da etapa 5")


def _hidratar_alvo(
    decisao: DecisaoIdentidade,
    entrada: EntradaMensagem,
    persistencia: PersistenciaOperacional,
) -> AtendimentoHidratado:
    """Recupera e hidrata o alvo; alvo ausente ou irrecuperável falha fechado."""
    if decisao.id_atendimento_alvo is None:
        raise ValueError("decisão de identidade sem alvo obrigatório")
    recuperacao = persistencia.recuperar_por_id(
        decisao.id_atendimento_alvo, entrada.canal, entrada.contato
    )
    if recuperacao.resultado is not ResultadoRecuperacao.ENCONTRADO:
        raise ValueError("alvo da etapa 5 não recuperável da persistência")
    return hidratar(recuperacao.registro)


def _pendente(
    entrada: EntradaMensagem, entrada_normalizada: EntradaNormalizada
) -> ProcessamentoPendente:
    return ProcessamentoPendente(
        canal=entrada.canal,
        contato=entrada.contato,
        conteudo=entrada_normalizada.mensagem_normalizada,
    )


def _preservar_alertar_marcar(
    *,
    categoria: str,
    entrada: EntradaMensagem,
    entrada_normalizada: EntradaNormalizada,
    persistencia: PersistenciaOperacional,
    tentar_alerta: Callable[..., object],
) -> None:
    """Ordem normativa de `E4-8`/`TS45-7`: preservar → alertar → marcar.

    Falha da preservação propaga por identidade, depois da tentativa de alerta,
    e a chave **não** é marcada (`E4-11`). Falha do alerta não impede a
    marcação (`E4-12`).
    """
    _preservar_e_alertar(
        categoria=categoria,
        entrada=entrada,
        entrada_normalizada=entrada_normalizada,
        persistencia=persistencia,
        tentar_alerta=tentar_alerta,
    )
    persistencia.marcar_chave_processada(entrada_normalizada.chave_idempotencia)


def _preservar_e_alertar(
    *,
    categoria: str,
    entrada: EntradaMensagem,
    entrada_normalizada: EntradaNormalizada,
    persistencia: PersistenciaOperacional,
    tentar_alerta: Callable[..., object],
) -> None:
    """Preserva o pendente e **sempre** tenta o alerta, mesmo se preservar falhar."""
    pendente_preservado = False
    try:
        persistencia.preservar_pendente(_pendente(entrada, entrada_normalizada))
        pendente_preservado = True
    finally:
        _tentar_alerta_operacional(
            tentar_alerta,
            categoria=categoria,
            pendente_preservado=pendente_preservado,
            correlacao=entrada_normalizada.chave_idempotencia,
        )


def _tentar_alerta_operacional(
    tentar_alerta: Callable[..., object],
    *,
    categoria: str,
    pendente_preservado: bool,
    correlacao: str,
) -> None:
    """Tentativa isolada de alerta (mesmo padrão de `orchestrator`, `TS45-12`/`E4-12`).

    Cópia deliberada: importar de `orchestrator` criaria ciclo de importação
    quando `processar_mensagem` (em `orchestrator`) passar a usar este módulo.
    Payload fechado em três campos sanitizados; retorno ignorado. Este é o
    **único** `except Exception` do módulo e envolve só a chamada injetada.
    """
    try:
        tentar_alerta(
            categoria=categoria,
            pendente_preservado=pendente_preservado,
            correlacao=correlacao,
        )
    except Exception:
        return
