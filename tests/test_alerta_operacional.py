"""Testes do módulo-folha `alerta_operacional`.

Prova a precedência de falhas de OL-4 (`TS45-7`, `TS45-11`, `E4-11`, `E4-12`)
e fixa, por AST, que o **único** `except Exception` do código de orquestração
vive aqui e envolve só a chamada injetada. Valores sintéticos apenas.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr.alerta_operacional import (
    preservar_e_alertar,
    tentar_alerta_operacional,
)
from casa77_sdr.persistence import PersistenciaEmMemoria, ProcessamentoPendente

PACOTE = Path(__file__).resolve().parents[1] / "src" / "casa77_sdr"
MODULO = PACOTE / "alerta_operacional.py"
PENDENTE = ProcessamentoPendente(canal="teste", contato="c-ficticio", conteudo="m")
CORRELACAO = "composta:ficticia"


class Alertas:
    def __init__(self, erro: Exception | None = None) -> None:
        self.chamadas: list[dict[str, Any]] = []
        self.erro = erro

    def __call__(self, **kwargs: Any) -> None:
        self.chamadas.append(kwargs)
        if self.erro is not None:
            raise self.erro


def _preservar(persistencia: Any, alertas: Alertas) -> None:
    preservar_e_alertar(
        persistencia=persistencia,
        pendente=PENDENTE,
        categoria="CategoriaFicticia",
        correlacao=CORRELACAO,
        tentar_alerta=alertas,
    )


def test_preserva_e_alerta_com_payload_fechado() -> None:
    persistencia = PersistenciaEmMemoria()
    alertas = Alertas()
    _preservar(persistencia, alertas)
    assert persistencia.recuperar_pendentes() == (PENDENTE,)
    assert alertas.chamadas == [
        {
            "categoria": "CategoriaFicticia",
            "pendente_preservado": True,
            "correlacao": CORRELACAO,
        }
    ]
    assert not persistencia.chave_processada(CORRELACAO)


def test_falha_ao_preservar_tenta_alerta_e_propaga_por_identidade() -> None:
    erro = OSError("falha ficticia")

    class Falha(PersistenciaEmMemoria):
        def preservar_pendente(self, pendente: Any) -> None:
            raise erro

    alertas = Alertas(erro=RuntimeError("alerta tambem falha"))
    with pytest.raises(OSError) as capturado:
        _preservar(Falha(), alertas)
    assert capturado.value is erro
    assert alertas.chamadas[-1]["pendente_preservado"] is False


def test_falha_do_alerta_e_absorvida() -> None:
    persistencia = PersistenciaEmMemoria()
    alertas = Alertas(erro=RuntimeError("alerta indisponivel"))
    _preservar(persistencia, alertas)
    assert persistencia.recuperar_pendentes() == (PENDENTE,)
    assert len(alertas.chamadas) == 1


def test_retorno_do_alerta_e_ignorado() -> None:
    assert (
        tentar_alerta_operacional(
            lambda **_: "ignorado",
            categoria="C",
            pendente_preservado=True,
            correlacao=CORRELACAO,
        )
        is None
    )


def _genericos(caminho: Path) -> tuple[ast.Module, list[ast.ExceptHandler]]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    return arvore, [
        h
        for h in ast.walk(arvore)
        if isinstance(h, ast.ExceptHandler)
        and isinstance(h.type, ast.Name)
        and h.type.id == "Exception"
    ]


def test_existe_exatamente_um_except_exception_e_ele_envolve_so_o_alerta() -> None:
    arvore, genericos = _genericos(MODULO)
    assert len(genericos) == 1
    donos = [
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef)
        and any(genericos[0] is filho for filho in ast.walk(no))
    ]
    assert [no.name for no in donos] == ["tentar_alerta_operacional"]
    (tentativa,) = [
        no for no in ast.walk(arvore) if isinstance(no, ast.Try) and genericos[0] in no.handlers
    ]
    assert len(tentativa.body) == 1
    corpo = tentativa.body[0]
    assert isinstance(corpo, ast.Expr)
    assert isinstance(corpo.value, ast.Call)
    assert isinstance(corpo.value.func, ast.Name)
    assert corpo.value.func.id == "tentar_alerta"
    assert corpo.value.args == []
    assert sorted(k.arg for k in corpo.value.keywords) == [
        "categoria",
        "correlacao",
        "pendente_preservado",
    ]


@pytest.mark.parametrize("nome", ["orchestrator.py", "orchestrator_identity.py"])
def test_modulos_do_orquestrador_nao_tem_except_exception(nome: str) -> None:
    _, genericos = _genericos(PACOTE / nome)
    assert genericos == []


def test_modulo_folha_nao_importa_o_orquestrador() -> None:
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    modulos = {
        no.module for no in ast.walk(arvore) if isinstance(no, ast.ImportFrom) and no.module
    }
    assert modulos == {"__future__", "collections.abc", "casa77_sdr.persistence"}
