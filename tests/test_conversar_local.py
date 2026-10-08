"""Laço do REPL local `scripts/conversar_local.py` — offline, produtor fake.

O script não é pacote: é carregado por caminho (`importlib`). Os imports de rede
(`anthropic`) são tardios no script, então nada de rede é tocado aqui.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from casa77_sdr.motor_deps import DependenciasMotor, carregar_base_motor
from casa77_sdr.persistence import PersistenciaEmMemoria

RAIZ = Path(__file__).resolve().parents[1]


def _carregar_script() -> Any:
    caminho = RAIZ / "scripts" / "conversar_local.py"
    especificacao = importlib.util.spec_from_file_location("conversar_local", caminho)
    assert especificacao is not None and especificacao.loader is not None
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def _payload_vazio() -> str:
    extraidos: dict[str, Any] = {}
    for campo in ("tipo_evento", "data_nomeada", "convidados", "formato", "nome", "contato"):
        extraidos[campo] = None
        extraidos[f"confianca_{campo}"] = {"presente": False, "valor": "alta"}
    return json.dumps(
        {
            "dados_extraidos": extraidos,
            "correcoes": [],
            "perguntas_comerciais": [],
            "pedido_de_humano": False,
            "confianca_pedido_de_humano": {"presente": False, "valor": "alta"},
            "referencias_evento_anterior": [],
            "trechos_ambiguos": [],
            "confianca_global": {"presente": True, "valor": "alta"},
            "intencoes_autonomas": [],
        }
    )


class _Produtor:
    def produzir(self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]) -> str:
        return _payload_vazio()


def test_laco_processa_duas_linhas_e_escreve_status() -> None:
    from datetime import timedelta

    modulo = _carregar_script()
    deps = DependenciasMotor(
        base_motor=carregar_base_motor(RAIZ),
        persistencia=PersistenciaEmMemoria(),
        produtor=_Produtor(),
        prompt_sistema="prompt ficticio",
        janela_idempotencia=timedelta(minutes=5),
        limiar_recencia=timedelta(days=30),
        calendario_integrado=False,
        tentar_alerta=lambda **_: None,
        enviar_mensagem=lambda canal, contato, texto: None,
        entregar_resumo=lambda resumo: None,
    )
    saida: list[str] = []
    modulo.conversar(
        iter(["oi", "tudo bem?", "sair", "nunca lida"]),
        saida.append,
        deps,
        canal="local",
        contato="contato-local",
    )
    status = [linha for linha in saida if "[desfecho=" in linha]
    assert len(status) == 2
    assert all("estado=" in linha for linha in status)
