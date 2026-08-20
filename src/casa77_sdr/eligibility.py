"""Política N-a — produção determinística do conjunto elegível E (doc 07 §6.2).

Política **interna da etapa 3**, não componente arquitetural: a tabela de
componentes de `docs/07` §4.1 permanece com **14** e a de responsabilidades
de §2 com **nove**. Este módulo é organização de código, não uma nova
responsabilidade do motor.

A função pública recebe os registros **já recuperados** pela persistência e
devolve o conjunto elegível **pronto**, que o `ResolvedorIdentidade` consome
sem recalcular elegibilidade nem recência (§7.1).

Fronteira (N-a-1–N-a-6): esta política **não** recupera, **não** persiste,
**não** interpreta texto, **não** lê YAML, **não** usa LLM, **não** consulta
relógio vivo e **não** resolve identidade. Ela também **não** produz o
conjunto **H**, **não** produz `havia_estado_esperado`, **não** produz
`id_atendimento_validado` (N-I) e **não** implementa N-a-T3–N-a-T7 — a
escrita do marco temporal continua pertencendo ao chamador da etapa 13.

As exceções aqui **apenas sinalizam**. Preservar a mensagem, emitir alerta
operacional e decidir o que o motor faz com o bloqueio (S4, S5) pertencem ao
`OrquestradorMotor`, que permanece não implementado.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from casa77_sdr.identity import CandidatoAtendimento
from casa77_sdr.persistence import RegistroAtendimento
from casa77_sdr.state_machine import Estado


class ConfiguracaoTemporalInvalida(ValueError):
    """Limiar de recência ausente, de tipo inválido ou não positivo.

    Erro de contrato da **configuração** da etapa 3 (N-a-L4, S10), distinto
    da integridade do contexto: é verificado **sempre**, inclusive quando o
    ciclo não possui candidato `encerrado` (N-a-L5).
    """


class MarcoTemporalAusente(ValueError):
    """Candidato `encerrado` precisa de recência sem `instante_ultima_transicao`.

    Erro de **integridade do contexto** da etapa 3 (S9). Não é `N-I-4`, que
    permanece específico à projeção coerente do identificador validado.
    """


class ContextoElegibilidadeCorrompido(ValueError):
    """Registro recuperado que não projeta em `CandidatoAtendimento`.

    Cobre `estado_conversa` ausente ou fora dos oito valores (N-a-P1) e
    `tipo_evento`/`data_nomeada` presentes com valor não textual (N-a-P4,
    S11).
    """


class IdentificadoIncoerente(ValueError):
    """O atendimento identificado não ocorre exatamente uma vez no contexto.

    Zero ou duas ou mais ocorrências violam **N-a-F1** / **N-I-2** / **P-I5**.
    Não institui unicidade global: IDs **não identificados** repetidos são
    preservados (N-a-D2).
    """


_ESTADOS_VALIDOS = frozenset(estado.value for estado in Estado)

# N-a-E1 — elegíveis sem consultar o marco temporal.
_GRUPO_I = frozenset(
    {
        Estado.NOVO,
        Estado.COLETANDO_DADOS,
        Estado.RESPONDENDO_DUVIDAS,
        Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
        Estado.PRONTO_PARA_HANDOFF,
        Estado.ENCAMINHADO_HUMANO,
    }
)


def _exigir_limiar_valido(limiar_recencia: timedelta | None) -> timedelta:
    """Valida o limiar antes de qualquer filtragem (N-a-L1–N-a-L6).

    Nenhum valor padrão é definido e nenhum mecanismo de carga é escolhido: o
    limiar chega como argumento explícito e o valor concreto permanece
    pendente de aprovação específica (`docs/07` §12, item 18).

    `bool` é rejeitado junto com os demais tipos: `True` não é duração.
    """
    if limiar_recencia is None:
        raise ConfiguracaoTemporalInvalida(
            "O limiar de recência é obrigatório e não possui valor padrão"
        )
    if not isinstance(limiar_recencia, timedelta):
        raise ConfiguracaoTemporalInvalida(
            "O limiar de recência deve ser uma duração"
        )
    if limiar_recencia <= timedelta(0):
        raise ConfiguracaoTemporalInvalida(
            "O limiar de recência deve ser positivo"
        )
    return limiar_recencia


def _texto_opcional(dados: dict[str, object], campo: str) -> str | None:
    """Projeta um campo opcional de `dados_coletados` (N-a-P2–N-a-P5).

    Ausente ou `None` devolve `None`; valor presente e não textual é
    corrupção. **Zero inferência**: nada é derivado de outro campo.
    """
    valor = dados.get(campo)
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise ContextoElegibilidadeCorrompido(
            f"O campo '{campo}' do registro recuperado deve ser texto"
        )
    return valor


def _projetar(registro: RegistroAtendimento) -> CandidatoAtendimento:
    """`RegistroAtendimento` → `CandidatoAtendimento`, quatro campos (N-a-P1–P6).

    Nenhum outro campo é transportado: sem nome, telefone, mensagem, preço,
    capacidade, convidados, formato, qualificação, pendência ou motivo.
    """
    estado_bruto = registro.estado_conversa
    # O teste textual precede a busca no conjunto: valor não-hashável — `list`,
    # `dict` — nunca pode virar `TypeError` incidental. N-a-P1 exige corrupção.
    if not isinstance(estado_bruto, str) or estado_bruto not in _ESTADOS_VALIDOS:
        raise ContextoElegibilidadeCorrompido(
            "O estado da conversa do registro recuperado não é um dos oito "
            "estados oficiais"
        )
    return CandidatoAtendimento(
        id_atendimento=registro.id_atendimento,
        estado=Estado(estado_bruto),
        tipo_evento_registrado=_texto_opcional(
            registro.dados_coletados, "tipo_evento"
        ),
        data_nomeada_registrada=_texto_opcional(
            registro.dados_coletados, "data_nomeada"
        ),
    )


def _e_recente(
    registro: RegistroAtendimento,
    instante_de_referencia_do_ciclo: datetime,
    limiar_recencia: timedelta,
) -> bool:
    """Recência de um candidato `encerrado` (N-a-R1–N-a-R5).

    A comparação usa o instante de referência do ciclo, **nunca** relógio
    vivo, e a borda é **inclusiva**: exatamente sobre o limiar entra. Nenhum
    fuso é convertido e nenhum instante é alterado.
    """
    marco = registro.instante_ultima_transicao
    if marco is None:
        raise MarcoTemporalAusente(
            "Candidato encerrado exige 'instante_ultima_transicao' para "
            "avaliar recência"
        )
    return marco >= instante_de_referencia_do_ciclo - limiar_recencia


def _chave_canonica(candidato: CandidatoAtendimento) -> tuple[str, str, int, str, int, str]:
    """Chave estrutural ascendente de N-a-O1/N-a-O2.

    `None` precede texto — daí o marcador `0`/`1` antes de cada campo
    opcional. A chave **não** usa recência, ordem da persistência, índice de
    entrada nem qualquer desempate temporal (N-a-O4).
    """
    tipo = candidato.tipo_evento_registrado
    data = candidato.data_nomeada_registrada
    return (
        candidato.id_atendimento,
        candidato.estado.value,
        0 if tipo is None else 1,
        "" if tipo is None else tipo,
        0 if data is None else 1,
        "" if data is None else data,
    )


def produzir_conjunto_elegivel(
    registros_recuperados: tuple[RegistroAtendimento, ...],
    *,
    registro_identificado: RegistroAtendimento | None,
    instante_de_referencia_do_ciclo: datetime,
    limiar_recencia: timedelta | None,
) -> tuple[CandidatoAtendimento, ...]:
    """Produz o conjunto elegível **E** a partir dos registros já recuperados.

    Ordem interna, espelhando a precedência conceitual da etapa 3 (§6.2):

    1. validar a configuração temporal (N-a-L4, N-a-L5);
    2. projetar **todos** os registros, validando integridade **antes** de
       qualquer filtragem — registro corrompido não é ignorado só porque
       seria excluído depois;
    3. validar a coerência do identificado, quando houver (N-a-F1, P-I5);
    4. aplicar classificação por estado e, só para `encerrado`, recência;
    5. aplicar N-a-F1;
    6. canonicalizar E (N-a-O1–N-a-O5);
    7. devolver a tupla.

    `registro_identificado` representa um atendimento que a etapa 3 **já**
    encontrou e validou; esta função não valida canal/contato, não recupera e
    não produz veredito — usa apenas sua existência para materializar N-a-F1.
    """
    limiar = _exigir_limiar_valido(limiar_recencia)

    projetados = tuple(_projetar(registro) for registro in registros_recuperados)

    id_identificado: str | None = None
    if registro_identificado is not None:
        id_identificado = registro_identificado.id_atendimento
        correspondentes = [
            registro
            for registro in registros_recuperados
            if registro.id_atendimento == id_identificado
        ]
        if len(correspondentes) != 1:
            raise IdentificadoIncoerente(
                "O atendimento identificado deve ocorrer exatamente uma vez "
                "no contexto recuperado"
            )
        # O identificado precisa **ser** a ocorrência do contexto, não apenas
        # coincidir no ID: um snapshot divergente entraria em E com conteúdo
        # que a etapa 3 não recuperou. A comparação é por **valor** — uma cópia
        # de conteúdo igual é aceita —, nunca por identidade de objeto.
        if correspondentes[0] != registro_identificado:
            raise IdentificadoIncoerente(
                "O atendimento identificado diverge da ocorrência presente no "
                "contexto recuperado"
            )

    elegiveis: list[CandidatoAtendimento] = []
    for registro, candidato in zip(registros_recuperados, projetados, strict=True):
        if (
            id_identificado is not None
            and candidato.id_atendimento == id_identificado
        ):
            # N-a-F1 prevalece: entra independentemente de estado e recência.
            elegiveis.append(candidato)
            continue
        if candidato.estado in _GRUPO_I:
            elegiveis.append(candidato)
            continue
        if candidato.estado is Estado.ENCERRADO and _e_recente(
            registro, instante_de_referencia_do_ciclo, limiar
        ):
            elegiveis.append(candidato)
        # `atendimento_humano` fica fora de E por N-a (N-a-E2); H é produzido
        # à parte, fora desta política (H1, H2).

    return tuple(sorted(elegiveis, key=_chave_canonica))
