"""Laço do REPL local `scripts/conversar_local.py` — offline, produtor fake.

O script não é pacote: é carregado por caminho (`importlib`). Os imports de rede
(`anthropic`) são tardios no script, então nada de rede é tocado aqui.
"""

from __future__ import annotations

import importlib.util
import sys
import json
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

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


def test_silencio_vai_ao_status_e_bot_vai_ao_stdout() -> None:
    modulo = _carregar_script()
    envios: list[str] = []
    deps = DependenciasMotor(
        base_motor=carregar_base_motor(RAIZ),
        persistencia=PersistenciaEmMemoria(),
        produtor=_Produtor(),
        prompt_sistema="prompt ficticio",
        janela_idempotencia=timedelta(minutes=5),
        limiar_recencia=timedelta(days=30),
        calendario_integrado=False,
        tentar_alerta=lambda **_: None,
        enviar_mensagem=lambda canal, contato, texto: envios.append(texto),
        entregar_resumo=lambda resumo: None,
    )
    saida: list[str] = []
    modulo.conversar(iter(["oi"]), saida.append, deps, canal="local", contato="c")
    assert "desfecho=silenciosa" in saida[0]
    assert saida[1] == "  (bot sem texto aprovado para esta situação)"
    assert envios == []


class _ProdutorContratoInvalido:
    """Valor presente sem confiança declarada — erro de contrato E-Nb."""

    def produzir(self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]) -> str:
        carga = json.loads(_payload_vazio())
        carga["dados_extraidos"]["tipo_evento"] = "festa"
        return json.dumps(carga)


def test_erro_de_contrato_nao_derruba_o_repl(capsys: pytest.CaptureFixture[str]) -> None:
    modulo = _carregar_script()
    deps = DependenciasMotor(
        base_motor=carregar_base_motor(RAIZ),
        persistencia=PersistenciaEmMemoria(),
        produtor=_ProdutorContratoInvalido(),
        prompt_sistema="prompt ficticio",
        janela_idempotencia=timedelta(minutes=5),
        limiar_recencia=timedelta(days=30),
        calendario_integrado=False,
        tentar_alerta=lambda **_: None,
        enviar_mensagem=lambda canal, contato, texto: None,
        entregar_resumo=lambda resumo: None,
    )
    saida: list[str] = []
    modulo.conversar(iter(["oi", "outra"]), saida.append, deps, canal="local", contato="c")
    erro = capsys.readouterr().err
    assert erro.count("[erro de contrato: ValueError] mensagem descartada") == 2
    assert saida == []


_ARGS = [
    "conversar_local.py",
    "--provedor", "anthropic",
    "--janela-idempotencia-segundos", "300",
    "--limiar-recencia-dias", "30",
    "--model", "m",
    "--max-tokens", "10",
    "--timeout", "5",
]


def test_main_sem_credencial_falha_claro(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    modulo = _carregar_script()
    for variavel in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        monkeypatch.delenv(variavel, raising=False)
    monkeypatch.setattr(sys, "argv", _ARGS)
    assert modulo.main() == 1
    erro = capsys.readouterr().err
    assert "ANTHROPIC_API_KEY" in erro
    assert "Traceback" not in erro


def test_main_argumento_obrigatorio_ausente_sai_com_2(monkeypatch: pytest.MonkeyPatch) -> None:
    modulo = _carregar_script()
    monkeypatch.setattr(sys, "argv", ["conversar_local.py"])
    with pytest.raises(SystemExit) as saida:
        modulo.main()
    assert saida.value.code == 2


_ARGS_CLAUDE_CODE = [
    "conversar_local.py",
    "--provedor", "claude-code",
    "--janela-idempotencia-segundos", "300",
    "--limiar-recencia-dias", "30",
    "--model", "sonnet",
    "--timeout", "5",
]


def _sem_argumento(argumentos: list[str], nome: str) -> list[str]:
    indice = argumentos.index(nome)
    return argumentos[:indice] + argumentos[indice + 2 :]


def test_main_provedor_e_obrigatorio(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    modulo = _carregar_script()
    monkeypatch.setattr(sys, "argv", _sem_argumento(_ARGS, "--provedor"))
    with pytest.raises(SystemExit) as saida:
        modulo.main()
    assert saida.value.code == 2
    assert "--provedor" in capsys.readouterr().err


def test_main_provedor_desconhecido_sai_com_2(monkeypatch: pytest.MonkeyPatch) -> None:
    modulo = _carregar_script()
    argumentos = list(_ARGS)
    argumentos[argumentos.index("anthropic")] = "openai"
    monkeypatch.setattr(sys, "argv", argumentos)
    with pytest.raises(SystemExit) as saida:
        modulo.main()
    assert saida.value.code == 2


def test_main_anthropic_exige_max_tokens(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    modulo = _carregar_script()
    monkeypatch.setattr(sys, "argv", _sem_argumento(_ARGS, "--max-tokens"))
    with pytest.raises(SystemExit) as saida:
        modulo.main()
    assert saida.value.code == 2
    assert "--max-tokens" in capsys.readouterr().err


def test_main_claude_code_cli_ausente_falha_claro(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from casa77_sdr import interpretation_claude_code

    def ausente() -> list[str]:
        raise interpretation_claude_code.ExecutavelClaudeNaoEncontrado("claude")

    monkeypatch.setattr(interpretation_claude_code, "resolver_executavel_claude", ausente)
    modulo = _carregar_script()
    monkeypatch.setattr(sys, "argv", _ARGS_CLAUDE_CODE)
    assert modulo.main() == 1
    erro = capsys.readouterr().err
    assert "/login" in erro
    assert "Traceback" not in erro


def test_main_claude_code_sem_login_falha_claro(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from casa77_sdr import interpretation_claude_code

    chamadas: list[tuple[list[str], float]] = []

    def sem_login(comando: list[str], *, timeout: float) -> bool:
        chamadas.append((comando, timeout))
        return False

    monkeypatch.setattr(
        interpretation_claude_code, "resolver_executavel_claude", lambda: ["claude-ficticio"]
    )
    monkeypatch.setattr(interpretation_claude_code, "verificar_login_claude", sem_login)
    modulo = _carregar_script()
    monkeypatch.setattr(sys, "argv", _ARGS_CLAUDE_CODE)
    assert modulo.main() == 1
    erro = capsys.readouterr().err
    assert "`claude`" in erro and "/login" in erro
    assert "ANTHROPIC_API_KEY" not in erro
    assert "Traceback" not in erro
    assert chamadas == [(["claude-ficticio"], 5.0)]


def test_main_claude_code_nao_exige_max_tokens_nem_credencial_da_api(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from casa77_sdr import interpretation_claude_code

    for variavel in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        monkeypatch.delenv(variavel, raising=False)
    monkeypatch.setattr(
        interpretation_claude_code, "resolver_executavel_claude", lambda: ["claude-ficticio"]
    )
    monkeypatch.setattr(
        interpretation_claude_code, "verificar_login_claude", lambda comando, *, timeout: True
    )
    modulo = _carregar_script()
    monkeypatch.setattr(modulo, "_linhas_do_terminal", lambda: iter(()))
    monkeypatch.setattr(sys, "argv", _ARGS_CLAUDE_CODE)
    assert modulo.main() == 0
    assert "Traceback" not in capsys.readouterr().err
