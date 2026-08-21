"""Máquina de estados do atendimento (3B.6).

Implementa `docs/06-maquina-de-estados.md` — os oito estados da §1.1, os eventos
`E01`–`E18` da §2, as transições T01–T41 da §3, a ordem de avaliação C0–C11 da
§4.2, os efeitos paralelos P1–P6 da §4.3 e as inércias N1–N4 da §4.4 — sob as
arbitragens S2 e S3.

A máquina é **pura e determinística**. Ela recebe o estado, os eventos **já
confirmados**, a `Qualificacao` **já calculada** e as condições **já
estruturadas**, e devolve uma decisão auditável. Por construção ela **não** lê o
YAML (I23), não interpreta texto, não recalcula regra comercial nem
qualificação, não fabrica evento, não executa ação e não produz efeito externo:
as ações devolvidas são **declarativas** (doc 07 §4.5).

Não há estado interno entre chamadas: o fechamento do ciclo (`E15` e depois
`E12`, doc 06 §4.2) reentra pela mesma função, e quem garante o número de
chamadas é o futuro `OrquestradorMotor`, não este módulo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable

from casa77_sdr.qualification import Qualificacao, ResultadoQualificacao
from casa77_sdr.rules import MotivoViolacao


class Estado(StrEnum):
    """Os oito estados operacionais da conversa (doc 06 §1.1, I08)."""

    NOVO = "novo"
    COLETANDO_DADOS = "coletando_dados"
    RESPONDENDO_DUVIDAS = "respondendo_duvidas"
    AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE = "aguardando_confirmacao_disponibilidade"
    PRONTO_PARA_HANDOFF = "pronto_para_handoff"
    ENCAMINHADO_HUMANO = "encaminhado_humano"
    ATENDIMENTO_HUMANO = "atendimento_humano"
    ENCERRADO = "encerrado"


class Evento(StrEnum):
    """Os eventos oficiais `E01`–`E18` (doc 06 §2). Zero evento novo.

    `E11` e `E17` permanecem no vocabulário para preservar a numeração, mas são
    **reduzidos a `E18` a montante** (§2.1) e nunca chegam a esta máquina.
    """

    E01 = "E01"
    E02 = "E02"
    E03 = "E03"
    E04 = "E04"
    E05 = "E05"
    E06 = "E06"
    E07 = "E07"
    E08 = "E08"
    E09 = "E09"
    E10 = "E10"
    E11 = "E11"
    E12 = "E12"
    E13 = "E13"
    E14 = "E14"
    E15 = "E15"
    E16 = "E16"
    E17 = "E17"
    E18 = "E18"


class MotivoEncerramento(StrEnum):
    """As quatro modalidades já enumeradas pela linha T35 (doc 06 §3, S3.4).

    Vocabulário fechado: nenhuma quinta modalidade existe. A máquina **recebe**
    o motivo já estruturado — não o interpreta e não o deduz da mensagem.
    """

    SEM_INTERESSE = "sem_interesse"
    ENGANO = "engano"
    SPAM = "spam"
    INCOMPATIBILIDADE_ACEITA = "incompatibilidade_aceita"


class AcaoMaquina(StrEnum):
    """Vocabulário técnico fechado de 20 códigos (doc 07 §4.5, S3.5).

    Ações são **semânticas e declarativas**: descrevem *o que deve acontecer*,
    nunca *como será dito*. Não citam `Rxx`, não carregam conteúdo comercial e
    **não são executadas** por esta máquina.
    """

    APRESENTAR_ATENDIMENTO_INICIAL = "apresentar_atendimento_inicial"
    RESPONDER_PERGUNTA_COMERCIAL = "responder_pergunta_comercial"
    PERGUNTAR_PROXIMO_CAMPO_AUSENTE = "perguntar_proximo_campo_ausente"
    PERGUNTAR_FORMATO = "perguntar_formato"
    RETOMAR_COLETA_SEM_REPETIR = "retomar_coleta_sem_repetir"
    INFORMAR_REGRA_INCOMPATIVEL = "informar_regra_incompativel"
    INFORMAR_RESSALVA_DE_CAPACIDADE = "informar_ressalva_de_capacidade"
    INFORMAR_CONDICOES_DE_VISITA = "informar_condicoes_de_visita"
    INFORMAR_LACUNA_DE_INFORMACAO = "informar_lacuna_de_informacao"
    INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE = (
        "informar_nao_confirmacao_de_disponibilidade"
    )
    DESPEDIR_SEM_CONTINUIDADE = "despedir_sem_continuidade"
    REFORCAR_ENCAMINHAMENTO = "reforcar_encaminhamento"
    EMITIR_MENSAGEM_DE_ENCAMINHAMENTO = "emitir_mensagem_de_encaminhamento"
    NAO_AVANCAR_COLETA = "nao_avancar_coleta"
    SILENCIAR_RESPOSTA_AUTOMATICA = "silenciar_resposta_automatica"
    PREPARAR_RESUMO = "preparar_resumo"
    ENTREGAR_RESUMO = "entregar_resumo"
    SOLICITAR_CONSULTA_CALENDARIO = "solicitar_consulta_calendario"
    REABRIR_ATENDIMENTO = "reabrir_atendimento"
    ABRIR_NOVO_ATENDIMENTO = "abrir_novo_atendimento"


class EfeitoParalelo(StrEnum):
    """Lista fechada P1–P6 (doc 06 §4.3). Não existe P7."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P6 = "P6"


class Inercia(StrEnum):
    """Lista fechada N1–N4 (doc 06 §4.4). Não existe N5."""

    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4 = "N4"


class Transicao(StrEnum):
    """As 41 transições da tabela do doc 06 §3."""

    T01 = "T01"
    T02 = "T02"
    T03 = "T03"
    T04 = "T04"
    T05 = "T05"
    T06 = "T06"
    T07 = "T07"
    T08 = "T08"
    T09 = "T09"
    T10 = "T10"
    T11 = "T11"
    T12 = "T12"
    T13 = "T13"
    T14 = "T14"
    T15 = "T15"
    T16 = "T16"
    T17 = "T17"
    T18 = "T18"
    T19 = "T19"
    T20 = "T20"
    T21 = "T21"
    T22 = "T22"
    T23 = "T23"
    T24 = "T24"
    T25 = "T25"
    T26 = "T26"
    T27 = "T27"
    T28 = "T28"
    T29 = "T29"
    T30 = "T30"
    T31 = "T31"
    T32 = "T32"
    T33 = "T33"
    T34 = "T34"
    T35 = "T35"
    T36 = "T36"
    T37 = "T37"
    T38 = "T38"
    T39 = "T39"
    T40 = "T40"
    T41 = "T41"


class Identidade(StrEnum):
    """Resultado estruturado do `ResolvedorIdentidade` (doc 07 §7.1).

    `AMBIGUA` nunca é entrada válida desta máquina: o pipeline termina na etapa
    5 quando a identidade é ambígua, e a máquina só é chamada depois disso.
    """

    ATENDIMENTO_ATIVO = "atendimento_ativo"
    MESMA_SOLICITACAO = "mesma_solicitacao"
    NOVA_SOLICITACAO = "nova_solicitacao"
    AMBIGUA = "ambigua"


class TransicaoInexistente(Exception):
    """Evento coerente na fronteira que nenhuma `Txx`, `P` ou `N` resolveu.

    É o fecho do doc 06 §4.5: **não existe fallback genérico**. Distinta de
    `TypeError`/`ValueError`, que sinalizam contrato de entrada malformado antes
    de qualquer avaliação de transição.
    """


@dataclass(frozen=True)
class CondicoesCiclo:
    """As oito condições já determinadas a montante (doc 07 §4.4, S3.8).

    Nenhum campo carrega dado pessoal, texto de mensagem ou valor comercial:
    apenas booleanos, enums fechados e identificadores técnicos opacos.
    """

    insumo_qualificacao_atualizado: bool | None = None
    pendencia_impeditiva: bool | None = None
    motivos_handoff: tuple[str, ...] = ()
    resposta_aprovada_disponivel: bool | None = None
    interesse_confirmar_disponibilidade: bool | None = None
    calendario_integrado: bool | None = None
    identidade: Identidade | None = None
    motivo_encerramento: MotivoEncerramento | None = None


@dataclass(frozen=True)
class DecisaoMaquina:
    """Decisão auditável do ciclo: um estado final e o caminho que o produziu.

    `caminho` pode conter **mais de uma** `Txx` (I19): o ciclo percorre as
    famílias C0–C11 e não para na primeira aplicável. `motivos_handoff` só é
    ecoado quando o caminho efetivamente registra ou absorve `E18`;
    `motivo_encerramento` só quando T35 entra no caminho.

    `transicoes_que_mudaram_estado` é a **subsequência ordenada de `caminho`**
    com as `Txx` que **efetivamente mudaram o estado** intermediário no
    instante de sua aplicação — contrato do doc 06 §4.2.
    """

    estado_final: Estado
    caminho: tuple[Transicao, ...] = ()
    acoes: tuple[AcaoMaquina, ...] = ()
    efeitos: tuple[EfeitoParalelo, ...] = ()
    inercias: tuple[Inercia, ...] = ()
    eventos_consumidos: tuple[Evento, ...] = ()
    motivos_handoff: tuple[str, ...] = ()
    motivo_encerramento: MotivoEncerramento | None = None
    transicoes_que_mudaram_estado: tuple[Transicao, ...] = ()


# --------------------------------------------------------------------------
# Mapa fechado Txx → ações (doc 07 §4.5)
# --------------------------------------------------------------------------

# Tupla ordenada por transição: a ordem interna é normativa quando o documento
# a fixa (T27 entrega o resumo antes de emitir a mensagem de encaminhamento).
_ACOES: dict[Transicao, tuple[AcaoMaquina, ...]] = {
    Transicao.T01: (AcaoMaquina.APRESENTAR_ATENDIMENTO_INICIAL,),
    Transicao.T02: (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,),
    Transicao.T03: (AcaoMaquina.PREPARAR_RESUMO,),
    Transicao.T04: (AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,),
    Transicao.T05: (AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL,),
    Transicao.T06: (
        AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL,
        AcaoMaquina.NAO_AVANCAR_COLETA,
    ),
    Transicao.T07: (AcaoMaquina.PREPARAR_RESUMO,),
    Transicao.T08: (AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE,),
    Transicao.T09: (AcaoMaquina.PERGUNTAR_FORMATO,),
    Transicao.T10: (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,),
    Transicao.T11: (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    Transicao.T12: (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    Transicao.T13: (AcaoMaquina.PREPARAR_RESUMO,),
    Transicao.T14: (AcaoMaquina.SOLICITAR_CONSULTA_CALENDARIO,),
    Transicao.T15: (AcaoMaquina.INFORMAR_NAO_CONFIRMACAO_DE_DISPONIBILIDADE,),
    Transicao.T16: (AcaoMaquina.INFORMAR_CONDICOES_DE_VISITA,),
    Transicao.T17: (AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,),
    Transicao.T18: (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    Transicao.T19: (AcaoMaquina.INFORMAR_LACUNA_DE_INFORMACAO,),
    Transicao.T20: (AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR,),
    Transicao.T21: (AcaoMaquina.PREPARAR_RESUMO,),
    Transicao.T22: (AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL,),
    Transicao.T23: (
        AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL,
        AcaoMaquina.NAO_AVANCAR_COLETA,
    ),
    Transicao.T24: (AcaoMaquina.PREPARAR_RESUMO,),
    Transicao.T25: (),
    Transicao.T26: (AcaoMaquina.PREPARAR_RESUMO,),
    Transicao.T27: (
        AcaoMaquina.ENTREGAR_RESUMO,
        AcaoMaquina.EMITIR_MENSAGEM_DE_ENCAMINHAMENTO,
    ),
    Transicao.T28: (
        AcaoMaquina.RESPONDER_PERGUNTA_COMERCIAL,
        AcaoMaquina.REFORCAR_ENCAMINHAMENTO,
    ),
    Transicao.T29: (AcaoMaquina.NAO_AVANCAR_COLETA,),
    Transicao.T30: (),
    Transicao.T31: (AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA,),
    Transicao.T32: (),
    Transicao.T33: (AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA,),
    Transicao.T34: (),
    # T35 é a única linha cuja ação depende de uma condição estruturada: a
    # despedida é obrigação semântica exclusiva de SEM_INTERESSE (S3.4).
    Transicao.T35: (),
    Transicao.T36: (AcaoMaquina.REABRIR_ATENDIMENTO,),
    Transicao.T37: (AcaoMaquina.ABRIR_NOVO_ATENDIMENTO,),
    Transicao.T38: (AcaoMaquina.NAO_AVANCAR_COLETA,),
    Transicao.T39: (AcaoMaquina.RETOMAR_COLETA_SEM_REPETIR,),
    Transicao.T40: (AcaoMaquina.PREPARAR_RESUMO,),
    Transicao.T41: (AcaoMaquina.PERGUNTAR_PROXIMO_CAMPO_AUSENTE,),
}


# --------------------------------------------------------------------------
# Classificação das violações de `E08` (doc 06 §3, notas da S3; S3.2)
# --------------------------------------------------------------------------


class _ClasseViolacao(StrEnum):
    """Classe de tratamento documentado da violação objetiva."""

    HANDOFF_DOCUMENTADO = "handoff_documentado"  # T05 / T22
    INFORMA_E_AGUARDA = "informa_e_aguarda"  # T06 / T23


_CLASSE_POR_MOTIVO: dict[MotivoViolacao, _ClasseViolacao] = {
    MotivoViolacao.DATA_NAO_ACEITA: _ClasseViolacao.HANDOFF_DOCUMENTADO,
    MotivoViolacao.TIPO_NAO_ACEITO: _ClasseViolacao.INFORMA_E_AGUARDA,
    MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE: _ClasseViolacao.INFORMA_E_AGUARDA,
}


_RESULTADOS_POSITIVOS = (
    ResultadoQualificacao.QUALIFICADO,
    ResultadoQualificacao.QUALIFICADO_COM_RESSALVA,
)

_EVENTOS_DE_DADO = (Evento.E02, Evento.E03, Evento.E04, Evento.E05)


# --------------------------------------------------------------------------
# Tabela declarativa das transições
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class _Regra:
    """Uma linha da §3: origem, gatilho e destino.

    `origem = None` representa a única linha com origem aberta — T35, "qualquer
    exceto `atendimento_humano`".
    """

    origem: Estado | None
    gatilho: Evento
    destino: Estado


_REGRAS: dict[Transicao, _Regra] = {
    Transicao.T01: _Regra(Estado.NOVO, Evento.E01, Estado.COLETANDO_DADOS),
    Transicao.T02: _Regra(Estado.NOVO, Evento.E06, Estado.RESPONDENDO_DUVIDAS),
    Transicao.T03: _Regra(Estado.NOVO, Evento.E18, Estado.PRONTO_PARA_HANDOFF),
    # T04 é a única linha com gatilho alternativo (E02/E03/E04/E05); o gatilho
    # declarado aqui é apenas o primeiro da ordem técnica, e a escolha efetiva
    # acontece em `_gatilho_disponivel`.
    Transicao.T04: _Regra(Estado.COLETANDO_DADOS, Evento.E02, Estado.COLETANDO_DADOS),
    Transicao.T05: _Regra(Estado.COLETANDO_DADOS, Evento.E08, Estado.PRONTO_PARA_HANDOFF),
    Transicao.T06: _Regra(Estado.COLETANDO_DADOS, Evento.E08, Estado.COLETANDO_DADOS),
    Transicao.T07: _Regra(Estado.COLETANDO_DADOS, Evento.E18, Estado.PRONTO_PARA_HANDOFF),
    Transicao.T08: _Regra(Estado.COLETANDO_DADOS, Evento.E07, Estado.PRONTO_PARA_HANDOFF),
    Transicao.T09: _Regra(Estado.COLETANDO_DADOS, Evento.E04, Estado.COLETANDO_DADOS),
    Transicao.T10: _Regra(Estado.COLETANDO_DADOS, Evento.E06, Estado.RESPONDENDO_DUVIDAS),
    Transicao.T11: _Regra(Estado.COLETANDO_DADOS, Evento.E09, Estado.PRONTO_PARA_HANDOFF),
    Transicao.T12: _Regra(Estado.COLETANDO_DADOS, Evento.E09, Estado.PRONTO_PARA_HANDOFF),
    Transicao.T13: _Regra(Estado.COLETANDO_DADOS, Evento.E07, Estado.PRONTO_PARA_HANDOFF),
    Transicao.T14: _Regra(
        Estado.COLETANDO_DADOS,
        Evento.E03,
        Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
    ),
    Transicao.T15: _Regra(Estado.COLETANDO_DADOS, Evento.E03, Estado.PRONTO_PARA_HANDOFF),
    Transicao.T16: _Regra(Estado.COLETANDO_DADOS, Evento.E10, Estado.COLETANDO_DADOS),
    Transicao.T17: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E06, Estado.RESPONDENDO_DUVIDAS
    ),
    Transicao.T18: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E09, Estado.PRONTO_PARA_HANDOFF
    ),
    Transicao.T19: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E09, Estado.PRONTO_PARA_HANDOFF
    ),
    Transicao.T20: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E15, Estado.COLETANDO_DADOS
    ),
    Transicao.T21: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E15, Estado.PRONTO_PARA_HANDOFF
    ),
    Transicao.T22: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E08, Estado.PRONTO_PARA_HANDOFF
    ),
    Transicao.T23: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E08, Estado.RESPONDENDO_DUVIDAS
    ),
    Transicao.T24: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E18, Estado.PRONTO_PARA_HANDOFF
    ),
    Transicao.T25: _Regra(
        Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
        Evento.E16,
        Estado.PRONTO_PARA_HANDOFF,
    ),
    Transicao.T26: _Regra(
        Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
        Evento.E18,
        Estado.PRONTO_PARA_HANDOFF,
    ),
    Transicao.T27: _Regra(
        Estado.PRONTO_PARA_HANDOFF, Evento.E12, Estado.ENCAMINHADO_HUMANO
    ),
    Transicao.T28: _Regra(
        Estado.ENCAMINHADO_HUMANO, Evento.E06, Estado.ENCAMINHADO_HUMANO
    ),
    Transicao.T29: _Regra(
        Estado.ENCAMINHADO_HUMANO, Evento.E15, Estado.ENCAMINHADO_HUMANO
    ),
    Transicao.T30: _Regra(
        Estado.ENCAMINHADO_HUMANO, Evento.E18, Estado.ENCAMINHADO_HUMANO
    ),
    Transicao.T31: _Regra(
        Estado.ENCAMINHADO_HUMANO, Evento.E13, Estado.ATENDIMENTO_HUMANO
    ),
    Transicao.T32: _Regra(Estado.ENCAMINHADO_HUMANO, Evento.E14, Estado.ENCERRADO),
    Transicao.T33: _Regra(
        Estado.ATENDIMENTO_HUMANO, Evento.E01, Estado.ATENDIMENTO_HUMANO
    ),
    Transicao.T34: _Regra(Estado.ATENDIMENTO_HUMANO, Evento.E14, Estado.ENCERRADO),
    Transicao.T35: _Regra(None, Evento.E14, Estado.ENCERRADO),
    Transicao.T36: _Regra(Estado.ENCERRADO, Evento.E01, Estado.COLETANDO_DADOS),
    Transicao.T37: _Regra(Estado.ENCERRADO, Evento.E01, Estado.COLETANDO_DADOS),
    Transicao.T38: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E15, Estado.RESPONDENDO_DUVIDAS
    ),
    Transicao.T39: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E01, Estado.COLETANDO_DADOS
    ),
    Transicao.T40: _Regra(
        Estado.RESPONDENDO_DUVIDAS, Evento.E07, Estado.PRONTO_PARA_HANDOFF
    ),
    Transicao.T41: _Regra(Estado.COLETANDO_DADOS, Evento.E01, Estado.COLETANDO_DADOS),
}


# Ordem de avaliação do doc 06 §4.2. A ordem intra-família é **canônica** (de
# varredura e auditoria); as únicas precedências semânticas aprovadas são
# T03 > T02 > T01 (C0), T32 > T35 (C3), T08 → T13 → T40 (C8) e T09 > T04 (C11).
_FAMILIAS: tuple[tuple[str, tuple[Transicao, ...]], ...] = (
    ("C0", (Transicao.T03, Transicao.T02, Transicao.T01)),
    ("C1", (Transicao.T33, Transicao.T36, Transicao.T37)),
    ("C2", (Transicao.T07, Transicao.T24, Transicao.T26, Transicao.T30)),
    ("C3", (Transicao.T32, Transicao.T34, Transicao.T35)),
    ("C4", (Transicao.T31,)),
    ("C5", (Transicao.T05, Transicao.T06, Transicao.T22, Transicao.T23)),
    ("C6", (Transicao.T11, Transicao.T18)),
    ("C7", (Transicao.T14, Transicao.T15, Transicao.T25)),
    ("C8", (Transicao.T08, Transicao.T13, Transicao.T40)),
    ("C9", (Transicao.T10, Transicao.T17, Transicao.T28)),
    ("C10", (Transicao.T12, Transicao.T19)),
    ("C11", (Transicao.T09, Transicao.T04, Transicao.T16, Transicao.T39, Transicao.T41)),
)

# Fechamento do ciclo: `E15` primeiro, `E12` depois (doc 06 §4.2).
_FECHAMENTO: tuple[tuple[Transicao, ...], ...] = (
    (Transicao.T20, Transicao.T21, Transicao.T29, Transicao.T38),
    (Transicao.T27,),
)

# Transições das famílias C0–C7, isto é, tudo que pode determinar o estado
# **antes** de C8 avaliar `E07`. Uma transição posterior a C8 (C9–C11 ou o
# fechamento) não torna `E07` retroativamente inerte (N2).
_FAMILIAS_ANTES_DE_C8 = ("C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7")

_TRANSICOES_ANTES_DE_C8: frozenset[Transicao] = frozenset(
    transicao
    for nome, transicoes in _FAMILIAS
    if nome in _FAMILIAS_ANTES_DE_C8
    for transicao in transicoes
)

_CONSUMIDORES_E06 = (Transicao.T02, Transicao.T10, Transicao.T17, Transicao.T28)
_CONSUMIDORES_E08 = (Transicao.T05, Transicao.T06, Transicao.T22, Transicao.T23)
_CONSUMIDORES_E09 = (Transicao.T11, Transicao.T12, Transicao.T18, Transicao.T19)
# Estados em que responder `E06` depende da condição estruturada
# `resposta_aprovada_disponivel` (S3.7). `novo` fica de fora: T02 responde de
# imediato e não ganhou condição nova.
_ESTADOS_COM_RESPOSTA_CONDICIONADA = (
    Estado.COLETANDO_DADOS,
    Estado.RESPONDENDO_DUVIDAS,
    Estado.ENCAMINHADO_HUMANO,
)


@dataclass
class _Percurso:
    """Estado intermediário do ciclo — vive apenas dentro de `decidir`."""

    estado: Estado
    estado_inicial: Estado
    eventos: frozenset[Evento]
    qualificacao: Qualificacao
    condicoes: CondicoesCiclo
    classe_violacao: _ClasseViolacao | None
    caminho: list[Transicao] = field(default_factory=list)
    transicoes_que_mudaram_estado: list[Transicao] = field(default_factory=list)
    acoes: list[AcaoMaquina] = field(default_factory=list)
    consumidos: list[Evento] = field(default_factory=list)

    def disponivel(self, evento: Evento) -> bool:
        return evento in self.eventos and evento not in self.consumidos


def _guarda_verdadeira(_: _Percurso) -> bool:
    return True


def _classe_e(alvo: _ClasseViolacao) -> Callable[[_Percurso], bool]:
    return lambda p: p.classe_violacao is alvo


def _resultado_em(*alvos: ResultadoQualificacao) -> Callable[[_Percurso], bool]:
    return lambda p: p.qualificacao.resultado in alvos


def _t04(p: _Percurso) -> bool:
    # S3.1: a condição "dado compatível com o YAML" é materializada pelo
    # resultado já estruturado — a máquina não lê a base.
    return p.qualificacao.resultado is not ResultadoQualificacao.INCOMPATIVEL


def _t09(p: _Percurso) -> bool:
    return (
        p.qualificacao.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS
        and "formato" in p.qualificacao.campos_ausentes
    )


def _t14(p: _Percurso) -> bool:
    return (
        p.condicoes.interesse_confirmar_disponibilidade is True
        and p.condicoes.calendario_integrado is True
    )


def _t15(p: _Percurso) -> bool:
    return (
        p.condicoes.interesse_confirmar_disponibilidade is True
        and p.condicoes.calendario_integrado is False
    )


def _t35(p: _Percurso) -> bool:
    # N3: `E18` concomitante já determina handoff, e T35 não se aplica.
    return p.condicoes.motivo_encerramento is not None and Evento.E18 not in p.eventos


def _t39(p: _Percurso) -> bool:
    return (
        p.condicoes.insumo_qualificacao_atualizado is True
        and p.qualificacao.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS
        and Evento.E06 not in p.eventos
    )


def _t41(p: _Percurso) -> bool:
    return (
        p.condicoes.insumo_qualificacao_atualizado is True
        and p.qualificacao.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS
        and not any(evento in p.eventos for evento in _EVENTOS_DE_DADO)
    )


_RESPOSTA_DISPONIVEL: Callable[[_Percurso], bool] = (
    lambda p: p.condicoes.resposta_aprovada_disponivel is True
)
_PENDENCIA_IMPEDITIVA: Callable[[_Percurso], bool] = (
    lambda p: p.condicoes.pendencia_impeditiva is True
)
_PENDENCIA_ACESSORIA: Callable[[_Percurso], bool] = (
    lambda p: p.condicoes.pendencia_impeditiva is False
)

_GUARDAS: dict[Transicao, Callable[[_Percurso], bool]] = {
    Transicao.T01: _guarda_verdadeira,
    Transicao.T02: _guarda_verdadeira,
    Transicao.T03: _guarda_verdadeira,
    Transicao.T04: _t04,
    Transicao.T05: _classe_e(_ClasseViolacao.HANDOFF_DOCUMENTADO),
    Transicao.T06: _classe_e(_ClasseViolacao.INFORMA_E_AGUARDA),
    Transicao.T07: _guarda_verdadeira,
    Transicao.T08: _resultado_em(ResultadoQualificacao.QUALIFICADO_COM_RESSALVA),
    Transicao.T09: _t09,
    Transicao.T10: _RESPOSTA_DISPONIVEL,
    Transicao.T11: _PENDENCIA_IMPEDITIVA,
    Transicao.T12: _PENDENCIA_ACESSORIA,
    Transicao.T13: _resultado_em(*_RESULTADOS_POSITIVOS),
    Transicao.T14: _t14,
    Transicao.T15: _t15,
    Transicao.T16: _guarda_verdadeira,
    Transicao.T17: _RESPOSTA_DISPONIVEL,
    Transicao.T18: _PENDENCIA_IMPEDITIVA,
    Transicao.T19: _PENDENCIA_ACESSORIA,
    Transicao.T20: _resultado_em(ResultadoQualificacao.DADOS_INCOMPLETOS),
    Transicao.T21: _resultado_em(*_RESULTADOS_POSITIVOS),
    Transicao.T22: _classe_e(_ClasseViolacao.HANDOFF_DOCUMENTADO),
    Transicao.T23: _classe_e(_ClasseViolacao.INFORMA_E_AGUARDA),
    Transicao.T24: _guarda_verdadeira,
    Transicao.T25: _guarda_verdadeira,
    Transicao.T26: _guarda_verdadeira,
    Transicao.T27: _guarda_verdadeira,
    Transicao.T28: _RESPOSTA_DISPONIVEL,
    Transicao.T29: _guarda_verdadeira,
    Transicao.T30: _guarda_verdadeira,
    Transicao.T31: _guarda_verdadeira,
    Transicao.T32: _guarda_verdadeira,
    Transicao.T33: _guarda_verdadeira,
    Transicao.T34: _guarda_verdadeira,
    Transicao.T35: _t35,
    Transicao.T36: lambda p: p.condicoes.identidade is Identidade.MESMA_SOLICITACAO,
    Transicao.T37: lambda p: p.condicoes.identidade is Identidade.NOVA_SOLICITACAO,
    Transicao.T38: _resultado_em(
        ResultadoQualificacao.INCOMPATIVEL, ResultadoQualificacao.INDEFINIDO
    ),
    Transicao.T39: _t39,
    Transicao.T40: _resultado_em(*_RESULTADOS_POSITIVOS),
    Transicao.T41: _t41,
}


def decidir(
    estado: Estado,
    eventos: tuple[Evento, ...],
    qualificacao: Qualificacao,
    condicoes: CondicoesCiclo,
) -> DecisaoMaquina:
    """Decide o estado final do ciclo a partir de insumos já estruturados.

    Função pura: sem I/O, sem rede, sem relógio, sem persistência, sem LLM, sem
    leitura de YAML e sem mutação dos argumentos. Não guarda estado entre
    chamadas — o fechamento (`E15`, depois `E12`) reentra por esta mesma função.

    O ciclo percorre as famílias C0–C11 na ordem, atualizando o **estado
    intermediário** a cada transição aplicada e seguindo para as famílias
    seguintes: o caminho pode conter mais de uma `Txx`. Cada evento é consumido
    no máximo uma vez como gatilho e cada `Txx` entra no caminho no máximo uma
    vez (doc 06 §4.2).

    Erros:

    - `TypeError` — tipo estrutural inválido em qualquer argumento;
    - `ValueError` — incoerência estrutural tipada (evento repetido, `E11`/`E17`
      na entrada, `E18` sem motivo, `E07` sem mutação efetiva ou sem resultado
      positivo, `E09` sem classificação, `E06` sem resposta aprovada nem `E09`,
      `E08` sem violação conhecida, T35 sem motivo, identidade ambígua);
    - `TransicaoInexistente` — evento coerente que nenhuma `Txx`, `P` ou `N`
      resolveu (doc 06 §4.5). Não existe fallback genérico.
    """
    _validar_tipos(estado, eventos, qualificacao, condicoes)
    _validar_coerencia(estado, eventos, qualificacao, condicoes)

    confirmados = frozenset(eventos)
    percurso = _Percurso(
        estado=estado,
        estado_inicial=estado,
        eventos=confirmados,
        qualificacao=qualificacao,
        condicoes=condicoes,
        classe_violacao=_classificar_violacoes(qualificacao)
        if Evento.E08 in confirmados
        else None,
    )

    for _, transicoes in _FAMILIAS:
        for transicao in transicoes:
            _tentar(percurso, transicao)

    for grupo in _FECHAMENTO:
        for transicao in grupo:
            _tentar(percurso, transicao)

    efeitos = _efeitos_paralelos(percurso)
    inercias = _inercias(percurso)
    _exigir_cobertura(percurso, efeitos, inercias)

    return DecisaoMaquina(
        estado_final=percurso.estado,
        caminho=tuple(percurso.caminho),
        acoes=tuple(percurso.acoes),
        efeitos=efeitos,
        inercias=inercias,
        eventos_consumidos=tuple(percurso.consumidos),
        # O campo só é ecoado quando `E18` foi **efetivamente** consumido ou
        # absorvido nesta decisão: um caminho que não registrou `E18` jamais
        # fabrica motivo de handoff a partir das condições recebidas.
        motivos_handoff=(
            condicoes.motivos_handoff
            if Evento.E18 in percurso.consumidos
            else ()
        ),
        transicoes_que_mudaram_estado=tuple(
            percurso.transicoes_que_mudaram_estado
        ),
        motivo_encerramento=(
            condicoes.motivo_encerramento
            if Transicao.T35 in percurso.caminho
            else None
        ),
    )


def _tentar(percurso: _Percurso, transicao: Transicao) -> None:
    """Aplica a transição quando estado, gatilho e guarda coincidem."""
    regra = _REGRAS[transicao]
    if transicao in percurso.caminho:
        return
    if regra.origem is None:
        # T35: qualquer origem exceto `atendimento_humano`.
        if percurso.estado is Estado.ATENDIMENTO_HUMANO:
            return
    elif percurso.estado is not regra.origem:
        return

    gatilho = _gatilho_disponivel(percurso, transicao)
    if gatilho is None:
        return
    if not _GUARDAS[transicao](percurso):
        return

    percurso.caminho.append(transicao)
    percurso.consumidos.append(gatilho)
    # A classificação acontece **aqui**, antes da atualização: só neste ponto o
    # estado intermediário vigente ainda é a origem efetiva desta aplicação.
    # Nada é reconstruído depois, e T35 não recebe tratamento especial — a
    # regra genérica basta (doc 06 §4.2).
    if regra.destino is not percurso.estado:
        percurso.transicoes_que_mudaram_estado.append(transicao)
    percurso.estado = regra.destino
    percurso.acoes.extend(_ACOES[transicao])
    if (
        transicao is Transicao.T35
        and percurso.condicoes.motivo_encerramento is MotivoEncerramento.SEM_INTERESSE
    ):
        percurso.acoes.append(AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE)
    if transicao is Transicao.T33 and percurso.disponivel(Evento.E18):
        # T33 **absorve** o `E18` concomitante: o motivo é preservado para o
        # humano, sem resposta automática e sem handoff concorrente (C1, I03).
        percurso.consumidos.append(Evento.E18)


def _gatilho_disponivel(percurso: _Percurso, transicao: Transicao) -> Evento | None:
    """Devolve o evento-gatilho ainda não consumido, ou `None`.

    T04 é a única linha com gatilho alternativo: entre `E02`–`E05` ela consome
    **um** evento, na ordem técnica, respeitando o que outras transições já
    consumiram. Os demais eventos de dado do ciclo são preservados por P1.
    """
    if transicao is Transicao.T04:
        for evento in _EVENTOS_DE_DADO:
            if percurso.disponivel(evento):
                return evento
        return None
    gatilho = _REGRAS[transicao].gatilho
    return gatilho if percurso.disponivel(gatilho) else None


def _efeitos_paralelos(percurso: _Percurso) -> tuple[EfeitoParalelo, ...]:
    """Lista fechada P1–P6 (doc 06 §4.3), na ordem canônica."""
    efeitos: list[EfeitoParalelo] = []
    eventos = percurso.eventos

    if any(evento in eventos for evento in _EVENTOS_DE_DADO):
        efeitos.append(EfeitoParalelo.P1)
    if Evento.E10 in eventos:
        efeitos.append(EfeitoParalelo.P2)
    if Evento.E06 in eventos and not any(
        t in percurso.caminho for t in _CONSUMIDORES_E06
    ):
        efeitos.append(EfeitoParalelo.P3)
    if Evento.E08 in eventos and not any(
        t in percurso.caminho for t in _CONSUMIDORES_E08
    ):
        efeitos.append(EfeitoParalelo.P4)
    if Evento.E09 in eventos and not any(
        t in percurso.caminho for t in _CONSUMIDORES_E09
    ):
        efeitos.append(EfeitoParalelo.P5)
    if _p6_aplicavel(percurso):
        efeitos.append(EfeitoParalelo.P6)
        percurso.acoes.append(AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE)
    return tuple(efeitos)


def _p6_aplicavel(percurso: _Percurso) -> bool:
    """P6 vale **exatamente** nas duas famílias enumeradas — não se generaliza."""
    if Evento.E07 not in percurso.eventos:
        return False
    if percurso.qualificacao.resultado is not ResultadoQualificacao.QUALIFICADO_COM_RESSALVA:
        return False
    if Transicao.T08 in percurso.caminho:
        return False
    disponibilidade_decidiu = (
        Transicao.T14 in percurso.caminho or Transicao.T15 in percurso.caminho
    )
    duvidas_com_t40 = (
        percurso.estado_inicial is Estado.RESPONDENDO_DUVIDAS
        and Transicao.T40 in percurso.caminho
    )
    return disponibilidade_decidiu or duvidas_com_t40


def _inercias(percurso: _Percurso) -> tuple[Inercia, ...]:
    """Lista fechada N1–N4 (doc 06 §4.4), na ordem canônica. Não existe N5."""
    inercias: list[Inercia] = []
    if Evento.E01 in percurso.eventos and Evento.E01 not in percurso.consumidos:
        inercias.append(Inercia.N1)
    if (
        Evento.E07 in percurso.eventos
        and Evento.E07 not in percurso.consumidos
        # N2 exige que uma transição **anterior à avaliação de C8** já tenha
        # determinado o estado. Uma `Txx` de C9–C11 ou do fechamento não
        # transforma `E07` em inércia retroativamente.
        and any(t in _TRANSICOES_ANTES_DE_C8 for t in percurso.caminho)
    ):
        inercias.append(Inercia.N2)
    if (
        Evento.E14 in percurso.eventos
        and Evento.E14 not in percurso.consumidos
        and Evento.E18 in percurso.eventos
    ):
        inercias.append(Inercia.N3)
    if (
        Evento.E15 in percurso.eventos
        and Evento.E15 not in percurso.consumidos
        and percurso.estado is Estado.PRONTO_PARA_HANDOFF
    ):
        inercias.append(Inercia.N4)
    return tuple(inercias)


def _exigir_cobertura(
    percurso: _Percurso,
    efeitos: tuple[EfeitoParalelo, ...],
    inercias: tuple[Inercia, ...],
) -> None:
    """Fecho do doc 06 §4.5: sem transição, efeito ou inércia, é erro de contrato."""
    cobertura: dict[Evento, EfeitoParalelo | Inercia] = {
        Evento.E01: Inercia.N1,
        Evento.E02: EfeitoParalelo.P1,
        Evento.E03: EfeitoParalelo.P1,
        Evento.E04: EfeitoParalelo.P1,
        Evento.E05: EfeitoParalelo.P1,
        Evento.E06: EfeitoParalelo.P3,
        Evento.E07: Inercia.N2,
        Evento.E08: EfeitoParalelo.P4,
        Evento.E09: EfeitoParalelo.P5,
        Evento.E10: EfeitoParalelo.P2,
        Evento.E14: Inercia.N3,
        Evento.E15: Inercia.N4,
    }
    for evento in sorted(percurso.eventos, key=lambda item: item.value):
        if evento in percurso.consumidos:
            continue
        resolvedor = cobertura.get(evento)
        if resolvedor in efeitos or resolvedor in inercias:
            continue
        raise TransicaoInexistente(
            f"O evento {evento.value} não foi resolvido por transição, "
            f"efeito paralelo ou inércia no estado {percurso.estado_inicial.value}"
        )


# --------------------------------------------------------------------------
# Validação de contrato
# --------------------------------------------------------------------------


def _validar_tipos(
    estado: Any, eventos: Any, qualificacao: Any, condicoes: Any
) -> None:
    if not isinstance(estado, Estado):
        raise TypeError("O estado deve ser um Estado")
    if not isinstance(eventos, tuple):
        raise TypeError("Os eventos devem ser uma tupla")
    for item in eventos:
        if not isinstance(item, Evento):
            raise TypeError("Cada evento recebido deve ser um Evento")
    if not isinstance(qualificacao, Qualificacao):
        raise TypeError("A qualificação deve ser uma Qualificacao")
    if not isinstance(condicoes, CondicoesCiclo):
        raise TypeError("As condições devem ser um CondicoesCiclo")

    for campo in (
        "insumo_qualificacao_atualizado",
        "pendencia_impeditiva",
        "resposta_aprovada_disponivel",
        "interesse_confirmar_disponibilidade",
        "calendario_integrado",
    ):
        valor = getattr(condicoes, campo)
        # `bool` é subclasse de `int`: um inteiro não serve como condição aqui.
        if valor is not None and not isinstance(valor, bool):
            raise TypeError(f"A condição '{campo}' deve ser booleana quando informada")

    if not isinstance(condicoes.motivos_handoff, tuple):
        raise TypeError("Os motivos de handoff devem ser uma tupla")
    for motivo in condicoes.motivos_handoff:
        if not isinstance(motivo, str):
            raise TypeError("Cada motivo de handoff deve ser um identificador textual")
    if condicoes.identidade is not None and not isinstance(
        condicoes.identidade, Identidade
    ):
        raise TypeError("A identidade deve ser uma Identidade quando informada")
    if condicoes.motivo_encerramento is not None and not isinstance(
        condicoes.motivo_encerramento, MotivoEncerramento
    ):
        raise TypeError(
            "O motivo de encerramento deve ser um MotivoEncerramento quando informado"
        )


def _validar_coerencia(
    estado: Estado,
    eventos: tuple[Evento, ...],
    qualificacao: Qualificacao,
    condicoes: CondicoesCiclo,
) -> None:
    confirmados = frozenset(eventos)
    if len(confirmados) != len(eventos):
        raise ValueError(
            "Cada evento pode aparecer no máximo uma vez na entrada estruturada"
        )
    for proibido in (Evento.E11, Evento.E17):
        if proibido in confirmados:
            raise ValueError(
                f"{proibido.value} deve ser reduzido a E18 a montante e nunca "
                "alcança a máquina de estados"
            )
    for motivo in condicoes.motivos_handoff:
        if not motivo.strip():
            raise ValueError("Motivo de handoff não pode ser um identificador vazio")

    if condicoes.identidade is Identidade.AMBIGUA:
        raise ValueError(
            "Identidade ambígua encerra o ciclo antes da máquina de estados e "
            "nunca é entrada válida"
        )
    if Evento.E18 in confirmados and not condicoes.motivos_handoff:
        raise ValueError("E18 exige ao menos um motivo de handoff registrado")
    if Evento.E07 in confirmados:
        if condicoes.insumo_qualificacao_atualizado is not True:
            raise ValueError(
                "E07 exige mutação efetiva de insumo da qualificação neste ciclo"
            )
        if qualificacao.resultado not in _RESULTADOS_POSITIVOS:
            raise ValueError(
                "E07 exige resultado de qualificação positivo (qualificado ou "
                "qualificado_com_ressalva)"
            )
        if Evento.E09 in confirmados and condicoes.pendencia_impeditiva is True:
            # Doc 06 §2.2: E07 não é confirmado em caminho resolvido por E09
            # impeditiva, mesmo que o resultado recebido esteja positivo.
            raise ValueError(
                "E07 não é confirmado em caminho resolvido por E09 impeditiva"
            )
    if Evento.E09 in confirmados and condicoes.pendencia_impeditiva is None:
        raise ValueError("E09 chega à máquina já classificado em impeditivo × acessório")
    if (
        Evento.E06 in confirmados
        and estado in _ESTADOS_COM_RESPOSTA_CONDICIONADA
        and condicoes.resposta_aprovada_disponivel is not True
        and Evento.E09 not in confirmados
    ):
        raise ValueError(
            "E06 sem resposta aprovada disponível exige E09 confirmado no ciclo"
        )
    if Evento.E08 in confirmados:
        if qualificacao.resultado is not ResultadoQualificacao.INCOMPATIVEL:
            # Incompatibilidade objetiva nunca convive com outro resultado
            # (I20): a máquina lê a classificação, não a recalcula.
            raise ValueError(
                "E08 exige resultado de qualificação incompativel"
            )
        _classificar_violacoes(qualificacao)
    for isolado in (Evento.E13, Evento.E15, Evento.E12):
        # Eventos de ciclo próprio: `E13` é operacional e chega isolado, e
        # `E15`/`E12` só existem depois do efeito real, em chamada de
        # fechamento (doc 06 §2.2). Isto valida o contrato dos eventos já
        # confirmados — não cria fase nem contador de chamadas.
        if isolado in confirmados and len(confirmados) != 1:
            raise ValueError(
                f"{isolado.value} chega em ciclo próprio e não coocorre com "
                "outros eventos"
            )
    if (
        Evento.E14 in confirmados
        and estado not in (Estado.ENCAMINHADO_HUMANO, Estado.ATENDIMENTO_HUMANO)
        and Evento.E18 not in confirmados
        and condicoes.motivo_encerramento is None
    ):
        raise ValueError("T35 exige um motivo de encerramento estruturado")


def _classificar_violacoes(qualificacao: Qualificacao) -> _ClasseViolacao:
    """Classe de tratamento de `E08` a partir das violações já calculadas.

    Basta **uma** violação da classe T05/T22 para que ela prevaleça; T06/T23 só
    vale quando **todas** forem da segunda classe (S3.2). As violações são
    apenas lidas — nunca recalculadas nem modificadas.
    """
    if not qualificacao.violacoes:
        raise ValueError("E08 exige ao menos uma violação objetiva na qualificação")
    classes = []
    for violacao in qualificacao.violacoes:
        classe = _CLASSE_POR_MOTIVO.get(violacao.motivo)
        if classe is None:
            raise ValueError(
                f"Motivo de violação sem classe documentada: {violacao.motivo}"
            )
        classes.append(classe)
    if _ClasseViolacao.HANDOFF_DOCUMENTADO in classes:
        return _ClasseViolacao.HANDOFF_DOCUMENTADO
    return _ClasseViolacao.INFORMA_E_AGUARDA
