"""Raiz de composição do motor — carga única da base e contêiner de dependências."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from casa77_sdr.knowledge import KnowledgeError
from casa77_sdr.motor_deps import BaseMotor, DependenciasMotor, carregar_base_motor
from casa77_sdr.response_consistency import ResultadoConsistencia

RAIZ = Path(__file__).resolve().parents[1]


def test_carrega_base_real_sem_erro():
    bm = carregar_base_motor(RAIZ)
    assert isinstance(bm, BaseMotor)
    assert bm.textos, "textos aprovados não podem ser vazios"
    assert all("/" in token for token in bm.textos)
    assert isinstance(bm.consistencia, ResultadoConsistencia)


def test_raiz_inexistente_falha_fechado(tmp_path):
    with pytest.raises(KnowledgeError):
        carregar_base_motor(tmp_path)


def test_dependencias_motor_sem_defaults_e_congelada():
    campos = dataclasses.fields(DependenciasMotor)
    assert [c.name for c in campos] == [
        "base_motor", "persistencia", "produtor", "prompt_sistema",
        "janela_idempotencia", "limiar_recencia", "calendario_integrado",
        "tentar_alerta", "enviar_mensagem", "entregar_resumo",
    ]
    assert all(c.default is dataclasses.MISSING for c in campos)
    assert DependenciasMotor.__dataclass_params__.frozen
