"""Motor de respostas do bot SDR da Casa 77."""

from casa77_sdr.knowledge import KnowledgeError, load_knowledge
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
]
