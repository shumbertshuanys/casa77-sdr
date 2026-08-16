"""Motor de respostas do bot SDR da Casa 77."""

from casa77_sdr.knowledge import KnowledgeError, load_knowledge
from casa77_sdr.normalization import (
    EntradaInvalida,
    EntradaMensagem,
    EntradaNormalizada,
    MensagemVazia,
    OrigemChave,
    normalizar_entrada,
)
from casa77_sdr.persistence import (
    FalhaDePersistencia,
    PersistenciaEmMemoria,
    PersistenciaOperacional,
    ProcessamentoPendente,
    RecuperacaoPorId,
    RegistroAtendimento,
    ResultadoRecuperacao,
)
from casa77_sdr.rules import (
    DadosAtendimento,
    MotivoViolacao,
    Violacao,
    avaliar_regras,
)

__all__ = [
    "KnowledgeError",
    "load_knowledge",
    "DadosAtendimento",
    "MotivoViolacao",
    "Violacao",
    "avaliar_regras",
    "FalhaDePersistencia",
    "PersistenciaEmMemoria",
    "PersistenciaOperacional",
    "ProcessamentoPendente",
    "RecuperacaoPorId",
    "RegistroAtendimento",
    "ResultadoRecuperacao",
    "EntradaInvalida",
    "EntradaMensagem",
    "EntradaNormalizada",
    "MensagemVazia",
    "OrigemChave",
    "normalizar_entrada",
]
