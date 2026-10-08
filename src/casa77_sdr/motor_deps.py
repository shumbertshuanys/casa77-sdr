"""Raiz de composição do motor: base carregada uma vez e dependências explícitas.

`BaseMotor` reúne a base factual, o índice, o mapa de cobertura, os textos
aprovados e o resultado de consistência, todos carregados e validados uma única
vez. `DependenciasMotor` é o contêiner imutável das dependências do ciclo; nenhum
campo tem valor padrão, tudo chega explícito do chamador.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

from casa77_sdr.coverage_map import conferir_referencias, validar_mapa_cobertura
from casa77_sdr.coverage_map_load import carregar_mapa_cobertura
from casa77_sdr.interpretation_llm import ProdutorTextoEstruturado
from casa77_sdr.knowledge import load_knowledge
from casa77_sdr.persistence import PersistenciaOperacional
from casa77_sdr.response_consistency import (
    ResultadoConsistencia,
    validar_consistencia_base,
)
from casa77_sdr.response_emittable_text import extrair_textos_emitiveis
from casa77_sdr.response_index import validar_indice
from casa77_sdr.response_index_load import carregar_indice

__all__ = ["BaseMotor", "DependenciasMotor", "carregar_base_motor"]


@dataclass(frozen=True)
class BaseMotor:
    """Conhecimento aprovado, carregado e validado uma vez."""

    base: dict[str, Any]
    indice: dict[str, Any]
    mapa: dict[str, Any]
    textos: dict[str, str]
    consistencia: ResultadoConsistencia


@dataclass(frozen=True)
class DependenciasMotor:
    """Raiz de composição: tudo que o ciclo precisa, sem valores padrão.

    `entregar_resumo(resumo)` sinaliza falha de entrega **somente** levantando
    `casa77_sdr.orchestrator.FalhaEntregaResumo`; qualquer outra exceção não é
    tratada como falha de entrega e se propaga.
    """

    base_motor: BaseMotor
    persistencia: PersistenciaOperacional
    produtor: ProdutorTextoEstruturado
    prompt_sistema: str
    janela_idempotencia: timedelta
    limiar_recencia: timedelta
    calendario_integrado: bool
    tentar_alerta: Callable[..., object]
    enviar_mensagem: Callable[[str, str, str], None]
    entregar_resumo: Callable[[str], None]


def carregar_base_motor(raiz: Path) -> BaseMotor:
    """Carrega e valida a base em `raiz/knowledge`; falha fechado em qualquer erro."""
    k = raiz / "knowledge"
    base = load_knowledge(k / "casa77.yaml")
    indice = carregar_indice(k / "indice-respostas-aprovadas.yaml")
    validar_indice(indice)
    mapa = carregar_mapa_cobertura(k / "mapa-cobertura.yaml")
    validar_mapa_cobertura(mapa)
    conferir_referencias(mapa, indice)
    textos = dict(
        extrair_textos_emitiveis(
            (k / "respostas-aprovadas.md").read_text(encoding="utf-8")
        )
    )
    consistencia = validar_consistencia_base(indice, base, textos)
    return BaseMotor(base, indice, mapa, textos, consistencia)
