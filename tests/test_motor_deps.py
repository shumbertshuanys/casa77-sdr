"""Raiz de composição do motor — carga única da base e contêiner de dependências."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from casa77_sdr.knowledge import KnowledgeError
from casa77_sdr.fact_selection import materializar_fatos_autorizados
from casa77_sdr.motor_deps import (
    BaseMotor,
    DependenciasMotor,
    carregar_base_motor,
    dobrar_quebras_suaves,
)
from casa77_sdr.response_assembly import montar_resposta_final
from casa77_sdr.response_composition import compor_textos_emitiveis
from casa77_sdr.response_consistency import ResultadoConsistencia
from casa77_sdr.response_emittable_text import extrair_textos_emitiveis
from casa77_sdr.response_validation import validar_resposta_final

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


def _montar_r06_f1(bm: BaseMotor) -> str:
    selecao = materializar_fatos_autorizados(bm.indice, bm.base, bm.textos, ("R06/F1",))
    return montar_resposta_final(compor_textos_emitiveis(selecao)).texto


def test_r06_f1_emitido_como_paragrafo_continuo():
    """Quebra manual do Markdown aprovado não vira quebra de linha no WhatsApp."""
    bm = carregar_base_motor(RAIZ)
    texto = _montar_r06_f1(bm)
    assert "\n" not in texto
    extraido = dict(
        extrair_textos_emitiveis(
            (RAIZ / "knowledge" / "respostas-aprovadas.md").read_text(encoding="utf-8")
        )
    )["R06/F1"]
    assert texto.startswith("A visita é feita com o responsável comercial e leva de ")
    assert texto.endswith(
        " minutos. A confirmação do horário também é feita pelo responsável comercial."
        " Vou registrar seu interesse e encaminhar para confirmação dos detalhes."
    )
    palavras_extraidas = [p for p in extraido.split() if "{{" not in p]
    palavras_emitidas = texto.split()
    assert len(palavras_emitidas) == len(extraido.split())
    restantes = iter(palavras_emitidas)
    assert all(p in restantes for p in palavras_extraidas)


def test_r06_f1_continuo_aprovado_pelo_validador():
    bm = carregar_base_motor(RAIZ)
    selecao = materializar_fatos_autorizados(bm.indice, bm.base, bm.textos, ("R06/F1",))
    montada = montar_resposta_final(compor_textos_emitiveis(selecao))
    assert validar_resposta_final(montada.texto, montada).aprovado


def test_textos_da_base_nao_tem_quebra_suave():
    bm = carregar_base_motor(RAIZ)
    for texto in bm.textos.values():
        assert "\n" not in texto.replace("\n\n", "")


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("uma linha", "uma linha"),
        ("a\nb\nc", "a b c"),
        ("a\nb\n\nc\nd", "a b\n\nc d"),
        ("{{x}} a\n{{y}}", "{{x}} a {{y}}"),
    ],
)
def test_dobrar_quebras_suaves_preserva_paragrafo(entrada, esperado):
    assert dobrar_quebras_suaves(entrada) == esperado
