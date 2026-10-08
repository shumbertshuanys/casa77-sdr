"""Hidratação do atendimento: `RegistroAtendimento` <-> (`Estado`, `DadosQualificacao`).

Conversão pura, sem I/O e sem relógio. `dados_coletados` usa as chaves
`tipo_evento`, `data_nomeada`, `convidados`, `nome`, `contato` e `formato`
(valor de `FormatoEvento`); chave ausente significa `None`, e `None` não é
gravado. Valor inválido (estado ou formato desconhecido, registro existente sem
estado) falha fechado com `ValueError`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from casa77_sdr.coverage_decision import ResultadoS2D8
from casa77_sdr.persistence import RegistroAtendimento
from casa77_sdr.qualification import (
    DadosQualificacao,
    FormatoEvento,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.rules import DadosAtendimento
from casa77_sdr.state_machine import DecisaoMaquina, Estado

__all__ = ["AtendimentoHidratado", "desidratar", "hidratar"]


@dataclass(frozen=True)
class AtendimentoHidratado:
    """Atendimento no início do ciclo; `id_atendimento None` => novo."""

    id_atendimento: str | None
    estado: Estado
    dados: DadosQualificacao
    marco_atual: datetime | None


def hidratar(registro: RegistroAtendimento | None) -> AtendimentoHidratado:
    """Reconstrói o atendimento a partir do registro persistido."""
    if registro is None:
        return AtendimentoHidratado(
            id_atendimento=None,
            estado=Estado.NOVO,
            dados=DadosQualificacao(atendimento=DadosAtendimento()),
            marco_atual=None,
        )
    if registro.estado_conversa is None:
        raise ValueError("registro persistido sem estado_conversa")
    estado = Estado(registro.estado_conversa)
    d = registro.dados_coletados
    formato = d.get("formato")
    dados = DadosQualificacao(
        atendimento=DadosAtendimento(
            tipo_evento=d.get("tipo_evento"),
            data_nomeada=d.get("data_nomeada"),
            convidados=d.get("convidados"),
        ),
        nome=d.get("nome"),
        contato=d.get("contato"),
        formato=None if formato is None else FormatoEvento(formato),
    )
    return AtendimentoHidratado(
        id_atendimento=registro.id_atendimento,
        estado=estado,
        dados=dados,
        marco_atual=registro.instante_ultima_transicao,
    )


def desidratar(
    at: AtendimentoHidratado,
    *,
    id_atendimento: str,
    canal: str,
    contato: str,
    decisao: DecisaoMaquina,
    qualificacao: Qualificacao,
    s2d8: ResultadoS2D8,
) -> RegistroAtendimento:
    """Monta o registro a persistir ao fim do ciclo.

    `instante_ultima_transicao` herda `at.marco_atual`; o marco de transição
    é aplicado depois pelos escritores de marco.
    """
    dados = at.dados
    candidatos = {
        "tipo_evento": dados.atendimento.tipo_evento,
        "data_nomeada": dados.atendimento.data_nomeada,
        "convidados": dados.atendimento.convidados,
        "nome": dados.nome,
        "contato": dados.contato,
        "formato": None if dados.formato is None else dados.formato.value,
    }
    motivo = (
        qualificacao.motivo.value
        if qualificacao.resultado is ResultadoQualificacao.INCOMPATIVEL
        else None
    )
    return RegistroAtendimento(
        id_atendimento=id_atendimento,
        canal=canal,
        contato=contato,
        estado_conversa=decisao.estado_final.value,
        dados_coletados={k: v for k, v in candidatos.items() if v is not None},
        resultado_qualificacao=qualificacao.resultado.value,
        pendencias_resposta=tuple(p.assunto.value for p in s2d8.pendencias_resposta),
        motivo_incompatibilidade=motivo,
        motivos_handoff=decisao.motivos_handoff,
        instante_ultima_transicao=at.marco_atual,
    )
