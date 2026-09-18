"""Testes da composição dos insumos da primeira decisão do ciclo.

Cobre o contrato vivo de `docs/07-arquitetura-motor-respostas.md` §4.1.9
(`IC-1`–`IC-12`): a agregação dos eventos confirmados por produtores distintos, a
obrigatoriedade de `E01`, os domínios fechados por slot, a ordem canônica sem
precedência, o *fail-closed* de duplicatas, a montagem das oito condições, o par
*all-or-none* de S2-D8 e a pureza.

`src/casa77_sdr/state_machine.py` e todos os produtores permanecem
**inalterados** e continuam as autoridades das suas próprias fronteiras: aqui
eles são apenas **exercitados**. A composição com a máquina vive **nos testes**;
ela **não** transforma `cycle_inputs.py` em chamador dela.

Todas as fixtures são **fictícias e genéricas**: zero PII, zero conversa real,
zero valor comercial.
"""

from __future__ import annotations

import ast
import inspect
import itertools
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import cycle_inputs
from casa77_sdr.closure_decision import EncerramentoInterpretado
from casa77_sdr.cycle_inputs import (
    agregar_eventos_primeira_decisao,
    montar_condicoes_ciclo,
)
from casa77_sdr.handoff_detection import DeteccaoHandoff, MotivoHandoff
from casa77_sdr.qualification import (
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.state_machine import (
    AcaoMaquina,
    CondicoesCiclo,
    Estado,
    Evento,
    Identidade,
    Inercia,
    MotivoEncerramento,
    Transicao,
    decidir,
)

MODULO = (
    Path(__file__).resolve().parents[1] / "src" / "casa77_sdr" / "cycle_inputs.py"
)

#: Domínios fechados por slot, reescritos **independentemente** do módulo.
DOMINIO_INTERPRETACAO = (
    Evento.E02,
    Evento.E03,
    Evento.E04,
    Evento.E05,
    Evento.E06,
    Evento.E10,
)
DOMINIO_INTERNOS = (Evento.E07, Evento.E08, Evento.E09)

#: Domínio final desta fronteira — doze eventos.
DOMINIO_FINAL = (
    Evento.E01,
    *DOMINIO_INTERPRETACAO[:5],
    *DOMINIO_INTERNOS,
    Evento.E10,
    Evento.E14,
    Evento.E18,
)

#: Os seis que **não** entram na primeira agregação.
FORA_DA_FRONTEIRA = (
    Evento.E11,
    Evento.E12,
    Evento.E13,
    Evento.E15,
    Evento.E16,
    Evento.E17,
)


# --------------------------------------------------------------------------
# Fixtures genéricas
# --------------------------------------------------------------------------


def handoff(*motivos: MotivoHandoff) -> DeteccaoHandoff:
    escolhidos = motivos or (MotivoHandoff.PEDIDO_HUMANO,)
    posicao = {m: i for i, m in enumerate(MotivoHandoff)}
    return DeteccaoHandoff(
        evento=Evento.E18,
        motivos=tuple(sorted(escolhidos, key=lambda m: posicao[m])),
    )


def encerramento(
    motivo: MotivoEncerramento = MotivoEncerramento.SEM_INTERESSE,
) -> EncerramentoInterpretado:
    return EncerramentoInterpretado(evento=Evento.E14, motivo=motivo)


def agregar(**ajustes: Any) -> tuple[Evento, ...]:
    base: dict[str, Any] = {
        "e01_confirmado": True,
        "eventos_interpretacao": (),
        "eventos_internos": (),
        "handoff": None,
        "encerramento": None,
    }
    base.update(ajustes)
    return agregar_eventos_primeira_decisao(**base)


def condicoes(**ajustes: Any) -> CondicoesCiclo:
    base: dict[str, Any] = {
        "insumo_qualificacao_atualizado": None,
        "pendencia_impeditiva": None,
        "handoff": None,
        "resposta_aprovada_disponivel": None,
        "interesse_confirmar_disponibilidade": None,
        "calendario_integrado": None,
        "identidade": None,
        "encerramento": None,
    }
    base.update(ajustes)
    return montar_condicoes_ciclo(**base)


_MOTIVO_POR_RESULTADO = {
    ResultadoQualificacao.DADOS_INCOMPLETOS: (
        MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES
    ),
    ResultadoQualificacao.INCOMPATIVEL: MotivoQualificacao.VIOLACAO_OBJETIVA,
    ResultadoQualificacao.INDEFINIDO: MotivoQualificacao.PENDENCIA_IMPEDITIVA,
    ResultadoQualificacao.QUALIFICADO: MotivoQualificacao.COMPATIVEL,
    ResultadoQualificacao.QUALIFICADO_COM_RESSALVA: (
        MotivoQualificacao.FORMATO_SENTADO_ACIMA_CAPACIDADE_SENTADA
    ),
}


def qual(resultado: ResultadoQualificacao, **ajustes: Any) -> Qualificacao:
    base: dict[str, Any] = {
        "resultado": resultado,
        "motivo": _MOTIVO_POR_RESULTADO[resultado],
    }
    base.update(ajustes)
    return Qualificacao(**base)


def codigo_executavel(caminho: Path) -> str:
    """O módulo **sem docstrings e sem comentários**.

    As proibições são sobre o que o módulo **faz**, não sobre o que a prosa
    **cita**: o contrato é explicado nomeando as fronteiras que ele não invade.
    """
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(
            no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            corpo = no.body
            if (
                corpo
                and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)
            ):
                no.body = corpo[1:] or [ast.Pass()]
    return ast.unparse(ast.fix_missing_locations(arvore))


def nomes_usados(caminho: Path) -> set[str]:
    """Identificadores realmente referenciados no código executável."""
    arvore = ast.parse(codigo_executavel(caminho))
    nomes = {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
            nomes.update(a.name for a in no.names)
        elif isinstance(no, ast.Import):
            nomes.update(a.name for a in no.names)
    return nomes


# --------------------------------------------------------------------------
# A. `E01` — obrigatório e explícito
# --------------------------------------------------------------------------


def test_e01_true_produz_e01() -> None:
    assert agregar() == (Evento.E01,)


def test_e01_false_e_value_error() -> None:
    """`IC-3`: a primeira decisão de um ciclo de nova mensagem exige `E01`."""
    with pytest.raises(ValueError):
        agregar(e01_confirmado=False)


@pytest.mark.parametrize("valor", [1, 0, "sim", "", None, (), [], 1.0], ids=repr)
def test_e01_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        agregar(e01_confirmado=valor)


def test_nenhuma_entrada_valida_produz_tupla_vazia() -> None:
    for interp in ((), (Evento.E02,), DOMINIO_INTERPRETACAO):
        for internos in ((), (Evento.E07,), DOMINIO_INTERNOS):
            for h in (None, handoff()):
                for e in (None, encerramento()):
                    saida = agregar(
                        eventos_interpretacao=interp,
                        eventos_internos=internos,
                        handoff=h,
                        encerramento=e,
                    )
                    assert saida != ()
                    assert Evento.E01 in saida


def test_e01_nao_e_fabricado_pela_fronteira() -> None:
    """`IC-3`: o fato chega por parâmetro explícito, nunca é inferido."""
    parametros = inspect.signature(agregar_eventos_primeira_decisao).parameters
    assert "e01_confirmado" in parametros
    assert parametros["e01_confirmado"].default is inspect.Parameter.empty


def test_todos_os_parametros_da_agregacao_sao_obrigatorios() -> None:
    for p in inspect.signature(agregar_eventos_primeira_decisao).parameters.values():
        assert p.default is inspect.Parameter.empty


# --------------------------------------------------------------------------
# B. Combinações exigidas
# --------------------------------------------------------------------------


def test_e01_mais_eventos_de_dado() -> None:
    assert agregar(
        eventos_interpretacao=(Evento.E05, Evento.E02, Evento.E04, Evento.E03)
    ) == (Evento.E01, Evento.E02, Evento.E03, Evento.E04, Evento.E05)


@pytest.mark.parametrize("evento", DOMINIO_INTERPRETACAO, ids=lambda e: e.value)
def test_e01_mais_cada_evento_de_interpretacao(evento: Evento) -> None:
    assert agregar(eventos_interpretacao=(evento,)) == (Evento.E01, evento)


@pytest.mark.parametrize("evento", DOMINIO_INTERNOS, ids=lambda e: e.value)
def test_e01_mais_cada_evento_interno(evento: Evento) -> None:
    assert agregar(eventos_internos=(evento,)) == (Evento.E01, evento)


def test_e01_mais_e14() -> None:
    assert agregar(encerramento=encerramento()) == (Evento.E01, Evento.E14)


def test_e01_mais_e18() -> None:
    assert agregar(handoff=handoff()) == (Evento.E01, Evento.E18)


def test_e01_mais_e14_mais_e18() -> None:
    """`IC-6`: nenhum evento concorrente é suprimido."""
    assert agregar(handoff=handoff(), encerramento=encerramento()) == (
        Evento.E01,
        Evento.E14,
        Evento.E18,
    )


def test_e01_mais_e08_mais_e18() -> None:
    assert agregar(eventos_internos=(Evento.E08,), handoff=handoff()) == (
        Evento.E01,
        Evento.E08,
        Evento.E18,
    )


def test_e01_mais_e09_mais_e18() -> None:
    assert agregar(eventos_internos=(Evento.E09,), handoff=handoff()) == (
        Evento.E01,
        Evento.E09,
        Evento.E18,
    )


def test_e01_mais_e06_mais_e07() -> None:
    assert agregar(
        eventos_interpretacao=(Evento.E06,), eventos_internos=(Evento.E07,)
    ) == (Evento.E01, Evento.E06, Evento.E07)


def test_e01_mais_e06_mais_e09() -> None:
    assert agregar(
        eventos_interpretacao=(Evento.E06,), eventos_internos=(Evento.E09,)
    ) == (Evento.E01, Evento.E06, Evento.E09)


def test_multiplos_produtores_simultaneos() -> None:
    saida = agregar(
        eventos_interpretacao=(Evento.E10, Evento.E06, Evento.E02),
        eventos_internos=(Evento.E09, Evento.E08),
        handoff=handoff(),
        encerramento=encerramento(),
    )
    assert saida == (
        Evento.E01,
        Evento.E02,
        Evento.E06,
        Evento.E08,
        Evento.E09,
        Evento.E10,
        Evento.E14,
        Evento.E18,
    )


def test_saida_maxima_cobre_o_dominio_final() -> None:
    saida = agregar(
        eventos_interpretacao=DOMINIO_INTERPRETACAO,
        eventos_internos=DOMINIO_INTERNOS,
        handoff=handoff(),
        encerramento=encerramento(),
    )
    assert set(saida) == set(DOMINIO_FINAL)
    assert len(saida) == 12


# --------------------------------------------------------------------------
# C. Domínio e duplicata
# --------------------------------------------------------------------------


@pytest.mark.parametrize("slot", ["eventos_interpretacao", "eventos_internos"])
@pytest.mark.parametrize("valor", [None, [Evento.E02], {Evento.E02}, "E02", 1], ids=repr)
def test_slot_que_nao_e_tupla_e_type_error(slot: str, valor: Any) -> None:
    with pytest.raises(TypeError):
        agregar(**{slot: valor})


@pytest.mark.parametrize("slot", ["eventos_interpretacao", "eventos_internos"])
@pytest.mark.parametrize("valor", ["E02", 2, None, object()], ids=repr)
def test_item_que_nao_e_evento_e_type_error(slot: str, valor: Any) -> None:
    with pytest.raises(TypeError):
        agregar(**{slot: (valor,)})


@pytest.mark.parametrize("evento", DOMINIO_INTERNOS, ids=lambda e: e.value)
def test_evento_interno_no_slot_de_interpretacao_e_value_error(
    evento: Evento,
) -> None:
    with pytest.raises(ValueError):
        agregar(eventos_interpretacao=(evento,))


@pytest.mark.parametrize("evento", DOMINIO_INTERPRETACAO, ids=lambda e: e.value)
def test_evento_de_interpretacao_no_slot_interno_e_value_error(
    evento: Evento,
) -> None:
    with pytest.raises(ValueError):
        agregar(eventos_internos=(evento,))


@pytest.mark.parametrize("evento", FORA_DA_FRONTEIRA, ids=lambda e: e.value)
@pytest.mark.parametrize("slot", ["eventos_interpretacao", "eventos_internos"])
def test_evento_fora_da_fronteira_e_value_error(evento: Evento, slot: str) -> None:
    """`IC-5`: E11, E12, E13, E15, E16 e E17 não entram na primeira agregação."""
    with pytest.raises(ValueError):
        agregar(**{slot: (evento,)})


def test_os_seis_fora_da_fronteira_sao_exatamente_esses() -> None:
    assert set(FORA_DA_FRONTEIRA) == set(Evento) - set(DOMINIO_FINAL)
    assert len(FORA_DA_FRONTEIRA) == 6


@pytest.mark.parametrize(
    ("slot", "evento"),
    [("eventos_interpretacao", Evento.E02), ("eventos_internos", Evento.E07)],
)
def test_duplicata_interna_e_value_error(slot: str, evento: Evento) -> None:
    with pytest.raises(ValueError):
        agregar(**{slot: (evento, evento)})


def test_nenhuma_deduplicacao_silenciosa() -> None:
    """Colisão é erro de contrato, não ruído a esconder."""
    with pytest.raises(ValueError, match="repetido"):
        agregar(eventos_interpretacao=(Evento.E06, Evento.E06))


def test_a_saida_nunca_tem_duplicata() -> None:
    for interp in ((), (Evento.E02,), DOMINIO_INTERPRETACAO):
        for internos in ((), DOMINIO_INTERNOS):
            saida = agregar(
                eventos_interpretacao=interp,
                eventos_internos=internos,
                handoff=handoff(),
                encerramento=encerramento(),
            )
            assert len(saida) == len(set(saida))


def test_a_saida_fica_sempre_no_dominio_fechado() -> None:
    for interp in ((), DOMINIO_INTERPRETACAO):
        for internos in ((), DOMINIO_INTERNOS):
            for h in (None, handoff()):
                for e in (None, encerramento()):
                    saida = agregar(
                        eventos_interpretacao=interp,
                        eventos_internos=internos,
                        handoff=h,
                        encerramento=e,
                    )
                    assert set(saida) <= set(DOMINIO_FINAL)
                    for proibido in FORA_DA_FRONTEIRA:
                        assert proibido not in saida


def test_a_pos_condicao_de_duplicata_global_existe() -> None:
    """`IC-8`: defensiva, mesmo sendo impossível sob os domínios corretos."""
    corpo = codigo_executavel(MODULO)
    assert "duplicado na agregação" in corpo


@pytest.mark.parametrize("valor", ["E18", 1, object(), Evento.E18], ids=repr)
def test_handoff_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        agregar(handoff=valor)


@pytest.mark.parametrize("valor", ["E14", 1, object(), Evento.E14], ids=repr)
def test_encerramento_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        agregar(encerramento=valor)


# --------------------------------------------------------------------------
# D. Ordem canônica — auditoria, não precedência
# --------------------------------------------------------------------------


def test_a_ordem_final_e_a_ordem_do_enum() -> None:
    saida = agregar(
        eventos_interpretacao=DOMINIO_INTERPRETACAO,
        eventos_internos=DOMINIO_INTERNOS,
        handoff=handoff(),
        encerramento=encerramento(),
    )
    posicao = {evento: i for i, evento in enumerate(Evento)}
    assert list(saida) == sorted(saida, key=lambda e: posicao[e])


def test_permutar_a_entrada_nao_altera_a_saida() -> None:
    for perm_interp in itertools.permutations(
        (Evento.E02, Evento.E06, Evento.E10)
    ):
        for perm_int in itertools.permutations(DOMINIO_INTERNOS):
            assert agregar(
                eventos_interpretacao=perm_interp, eventos_internos=perm_int
            ) == agregar(
                eventos_interpretacao=(Evento.E02, Evento.E06, Evento.E10),
                eventos_internos=DOMINIO_INTERNOS,
            )


def test_a_ordem_nao_estabelece_precedencia() -> None:
    """`IC-9`: `E18` sai por último e ainda assim a máquina o prioriza."""
    eventos = agregar(eventos_interpretacao=(Evento.E06,), handoff=handoff())
    assert eventos.index(Evento.E06) < eventos.index(Evento.E18)
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        eventos,
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(handoff=handoff(), resposta_aprovada_disponivel=True,
                  pendencia_impeditiva=False),
    )
    # A máquina resolve por T24 — `E18` vence apesar de sair depois na tupla.
    assert Transicao.T24 in decisao.caminho


def test_o_modulo_nao_copia_as_familias_c0_c11() -> None:
    corpo = codigo_executavel(MODULO)
    for proibido in ("C0", "C10", "C11", "_FAMILIAS", "precedencia", "prioridade"):
        assert proibido not in corpo


# --------------------------------------------------------------------------
# E. Montagem das oito condições
# --------------------------------------------------------------------------


def test_condicoes_ciclo_tem_exatamente_oito_campos() -> None:
    import dataclasses

    campos = [c.name for c in dataclasses.fields(CondicoesCiclo)]
    assert campos == [
        "insumo_qualificacao_atualizado",
        "pendencia_impeditiva",
        "motivos_handoff",
        "resposta_aprovada_disponivel",
        "interesse_confirmar_disponibilidade",
        "calendario_integrado",
        "identidade",
        "motivo_encerramento",
    ]
    assert len(campos) == 8


def test_a_saida_e_um_condicoes_ciclo() -> None:
    assert isinstance(condicoes(), CondicoesCiclo)


@pytest.mark.parametrize("valor", [True, False, None], ids=repr)
def test_condicao_1_transportada_literalmente(valor: bool | None) -> None:
    assert condicoes(insumo_qualificacao_atualizado=valor).insumo_qualificacao_atualizado is valor


@pytest.mark.parametrize("valor", [True, False, None], ids=repr)
def test_condicao_5_transportada_literalmente(valor: bool | None) -> None:
    alvo = condicoes(interesse_confirmar_disponibilidade=valor)
    assert alvo.interesse_confirmar_disponibilidade is valor


@pytest.mark.parametrize("valor", [True, False, None], ids=repr)
def test_condicao_6_transportada_literalmente(valor: bool | None) -> None:
    assert condicoes(calendario_integrado=valor).calendario_integrado is valor


@pytest.mark.parametrize(
    "identidade", [*list(Identidade), None], ids=lambda i: getattr(i, "value", "None")
)
def test_condicao_7_transportada_literalmente(identidade: Identidade | None) -> None:
    assert condicoes(identidade=identidade).identidade is identidade


def test_identidade_tem_quatro_membros() -> None:
    assert len(list(Identidade)) == 4


@pytest.mark.parametrize(
    "nome",
    [
        "insumo_qualificacao_atualizado",
        "interesse_confirmar_disponibilidade",
        "calendario_integrado",
    ],
)
@pytest.mark.parametrize("valor", [1, 0, "sim", (), object()], ids=repr)
def test_condicao_booleana_de_tipo_errado_e_type_error(nome: str, valor: Any) -> None:
    with pytest.raises(TypeError):
        condicoes(**{nome: valor})


@pytest.mark.parametrize("valor", ["ativo", 1, object()], ids=repr)
def test_identidade_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        condicoes(identidade=valor)


# --------------------------------------------------------------------------
# F. Par S2-D8 — all-or-none
# --------------------------------------------------------------------------


@pytest.mark.parametrize("impeditiva", [True, False], ids=repr)
@pytest.mark.parametrize("resposta", [True, False], ids=repr)
def test_par_s2d8_bool_bool_e_valido(impeditiva: bool, resposta: bool) -> None:
    alvo = condicoes(
        pendencia_impeditiva=impeditiva, resposta_aprovada_disponivel=resposta
    )
    assert alvo.pendencia_impeditiva is impeditiva
    assert alvo.resposta_aprovada_disponivel is resposta


def test_par_s2d8_none_none_e_valido() -> None:
    alvo = condicoes(pendencia_impeditiva=None, resposta_aprovada_disponivel=None)
    assert alvo.pendencia_impeditiva is None
    assert alvo.resposta_aprovada_disponivel is None


@pytest.mark.parametrize("resposta", [True, False], ids=repr)
def test_par_s2d8_none_bool_e_value_error(resposta: bool) -> None:
    with pytest.raises(ValueError, match="S2-D8"):
        condicoes(pendencia_impeditiva=None, resposta_aprovada_disponivel=resposta)


@pytest.mark.parametrize("impeditiva", [True, False], ids=repr)
def test_par_s2d8_bool_none_e_value_error(impeditiva: bool) -> None:
    with pytest.raises(ValueError, match="S2-D8"):
        condicoes(pendencia_impeditiva=impeditiva, resposta_aprovada_disponivel=None)


def test_false_de_s2d8_nunca_vira_none() -> None:
    alvo = condicoes(pendencia_impeditiva=False, resposta_aprovada_disponivel=False)
    assert alvo.pendencia_impeditiva is False
    assert alvo.resposta_aprovada_disponivel is False
    assert alvo.pendencia_impeditiva is not None


def test_a_fronteira_nao_recebe_resultado_s2d8() -> None:
    """`IC-10`: `pendencias_resposta` não pertence a `CondicoesCiclo`."""
    parametros = inspect.signature(montar_condicoes_ciclo).parameters
    anotacoes = {str(p.annotation) for p in parametros.values()}
    assert all("ResultadoS2D8" not in a for a in anotacoes)
    nomes = nomes_usados(MODULO)
    assert "ResultadoS2D8" not in nomes
    assert "casa77_sdr.coverage_decision" not in nomes
    assert "pendencias_resposta" not in nomes


# --------------------------------------------------------------------------
# G. Projeção de handoff e de encerramento
# --------------------------------------------------------------------------


def test_handoff_ausente_produz_tupla_vazia() -> None:
    alvo = condicoes(handoff=None)
    assert alvo.motivos_handoff == ()
    assert alvo.motivos_handoff is not None


def test_handoff_presente_projeta_strings_na_ordem_do_detector() -> None:
    alvo = condicoes(
        handoff=handoff(MotivoHandoff.PEDIDO_HUMANO, MotivoHandoff.CANCELAMENTO)
    )
    assert alvo.motivos_handoff == ("pedido_humano", "cancelamento")
    assert all(isinstance(m, str) for m in alvo.motivos_handoff)
    assert all(type(m) is str for m in alvo.motivos_handoff)


def test_motivos_nao_transportam_o_enum_para_a_maquina() -> None:
    alvo = condicoes(handoff=handoff())
    assert not any(isinstance(m, MotivoHandoff) for m in alvo.motivos_handoff)


def test_todos_os_dez_motivos_projetam_sem_duplicata() -> None:
    alvo = condicoes(handoff=handoff(*MotivoHandoff))
    assert len(alvo.motivos_handoff) == 10
    assert len(set(alvo.motivos_handoff)) == 10
    assert alvo.motivos_handoff == tuple(m.value for m in MotivoHandoff)


def test_encerramento_ausente_produz_motivo_none() -> None:
    assert condicoes(encerramento=None).motivo_encerramento is None


@pytest.mark.parametrize("motivo", list(MotivoEncerramento), ids=lambda m: m.value)
def test_encerramento_presente_projeta_o_motivo(motivo: MotivoEncerramento) -> None:
    alvo = condicoes(encerramento=encerramento(motivo))
    assert alvo.motivo_encerramento is motivo


def test_o_motivo_nao_e_suprimido_quando_ha_handoff() -> None:
    """`E14` × `E18` continua sendo resolvido pela máquina, por N3."""
    alvo = condicoes(handoff=handoff(), encerramento=encerramento())
    assert alvo.motivo_encerramento is MotivoEncerramento.SEM_INTERESSE
    assert alvo.motivos_handoff == ("pedido_humano",)


@pytest.mark.parametrize("valor", ["pedido_humano", 1, object()], ids=repr)
def test_handoff_de_tipo_errado_na_montagem_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        condicoes(handoff=valor)


@pytest.mark.parametrize("valor", ["sem_interesse", 1, object()], ids=repr)
def test_encerramento_de_tipo_errado_na_montagem_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        condicoes(encerramento=valor)


# --------------------------------------------------------------------------
# H. `None`, `False` e `()` são distintos
# --------------------------------------------------------------------------


def test_none_false_e_tupla_vazia_nunca_sao_coagidos() -> None:
    avaliado = condicoes(
        insumo_qualificacao_atualizado=False,
        pendencia_impeditiva=False,
        resposta_aprovada_disponivel=False,
        interesse_confirmar_disponibilidade=False,
        calendario_integrado=False,
    )
    nao_avaliado = condicoes()

    for campo in (
        "insumo_qualificacao_atualizado",
        "pendencia_impeditiva",
        "resposta_aprovada_disponivel",
        "interesse_confirmar_disponibilidade",
        "calendario_integrado",
    ):
        assert getattr(avaliado, campo) is False
        assert getattr(nao_avaliado, campo) is None
        assert getattr(avaliado, campo) is not getattr(nao_avaliado, campo)

    # `motivos_handoff` usa `()` para ausência, por contrato histórico.
    assert nao_avaliado.motivos_handoff == ()
    assert nao_avaliado.motivos_handoff is not None


# --------------------------------------------------------------------------
# I. Composição com a `MaquinaEstados` — só nos testes
# --------------------------------------------------------------------------


def test_novo_mais_e01_resolve_por_t01() -> None:
    decisao = decidir(
        Estado.NOVO,
        agregar(),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(),
    )
    assert decisao.caminho == (Transicao.T01,)
    assert decisao.estado_final is Estado.COLETANDO_DADOS


def test_novo_mais_e01_mais_e18_respeita_a_precedencia_da_maquina() -> None:
    decisao = decidir(
        Estado.NOVO,
        agregar(handoff=handoff()),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(handoff=handoff()),
    )
    assert Transicao.T03 in decisao.caminho
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF
    assert decisao.motivos_handoff == ("pedido_humano",)
    assert Inercia.N1 in decisao.inercias


def test_coleta_mais_e01_mais_dados() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        agregar(eventos_interpretacao=(Evento.E02, Evento.E03)),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(),
    )
    assert Transicao.T04 in decisao.caminho
    assert decisao.estado_final is Estado.COLETANDO_DADOS


def test_e01_mais_e07_com_mutacao_e_qualificacao_positiva() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        agregar(eventos_internos=(Evento.E07,)),
        qual(ResultadoQualificacao.QUALIFICADO),
        condicoes(insumo_qualificacao_atualizado=True),
    )
    assert Transicao.T13 in decisao.caminho
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF


def test_e01_mais_e09_com_classificacao() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        agregar(eventos_internos=(Evento.E09,)),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(pendencia_impeditiva=False, resposta_aprovada_disponivel=False),
    )
    assert Transicao.T12 in decisao.caminho


def test_e01_mais_e14_mais_e18_preserva_n3_e_nao_aplica_t35() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        agregar(handoff=handoff(), encerramento=encerramento()),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(handoff=handoff(), encerramento=encerramento()),
    )
    assert Transicao.T35 not in decisao.caminho
    assert Inercia.N3 in decisao.inercias
    assert decisao.motivo_encerramento is None


def test_atendimento_humano_mais_e01_mais_e18_resolve_por_t33() -> None:
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO,
        agregar(handoff=handoff()),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(handoff=handoff()),
    )
    assert decisao.caminho == (Transicao.T33,)
    assert decisao.estado_final is Estado.ATENDIMENTO_HUMANO
    assert AcaoMaquina.SILENCIAR_RESPOSTA_AUTOMATICA in decisao.acoes


def test_encerrado_mais_e01_com_mesma_solicitacao_resolve_por_t36() -> None:
    decisao = decidir(
        Estado.ENCERRADO,
        agregar(),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(identidade=Identidade.MESMA_SOLICITACAO),
    )
    assert Transicao.T36 in decisao.caminho


def test_encerrado_mais_e01_com_nova_solicitacao_resolve_por_t37() -> None:
    decisao = decidir(
        Estado.ENCERRADO,
        agregar(),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(identidade=Identidade.NOVA_SOLICITACAO),
    )
    assert Transicao.T37 in decisao.caminho


def test_e01_mais_e03_com_calendario_none_respeita_a_maquina_vigente() -> None:
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        agregar(eventos_interpretacao=(Evento.E03,)),
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes(calendario_integrado=None),
    )
    assert Transicao.T04 in decisao.caminho
    assert Transicao.T14 not in decisao.caminho
    assert Transicao.T15 not in decisao.caminho


# --------------------------------------------------------------------------
# J. Incoerência semântica continua sendo rejeitada pela MÁQUINA
# --------------------------------------------------------------------------


def test_e07_sem_mutacao_e_aceito_na_composicao_e_rejeitado_pela_maquina() -> None:
    """`IC-11`: a coerência semântica não é reimplementada aqui."""
    eventos = agregar(eventos_internos=(Evento.E07,))
    alvo = condicoes(insumo_qualificacao_atualizado=False)
    assert eventos == (Evento.E01, Evento.E07)  # a composição aceita

    with pytest.raises(ValueError, match="E07"):
        decidir(
            Estado.COLETANDO_DADOS, eventos, qual(ResultadoQualificacao.QUALIFICADO), alvo
        )


def test_e08_sem_incompativel_e_rejeitado_pela_maquina() -> None:
    eventos = agregar(eventos_internos=(Evento.E08,))
    assert eventos == (Evento.E01, Evento.E08)

    with pytest.raises(ValueError, match="E08"):
        decidir(
            Estado.COLETANDO_DADOS,
            eventos,
            qual(ResultadoQualificacao.QUALIFICADO),
            condicoes(),
        )


def test_e09_sem_classificacao_e_rejeitado_pela_maquina() -> None:
    eventos = agregar(eventos_internos=(Evento.E09,))
    assert eventos == (Evento.E01, Evento.E09)

    with pytest.raises(ValueError, match="E09"):
        decidir(
            Estado.COLETANDO_DADOS,
            eventos,
            qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
            condicoes(),
        )


def test_e18_sem_motivos_e_rejeitado_pela_maquina() -> None:
    """A composição não fabrica motivo: sem detector, `motivos_handoff` é `()`."""
    eventos = agregar(handoff=handoff())
    alvo = condicoes(handoff=None)
    assert Evento.E18 in eventos
    assert alvo.motivos_handoff == ()

    with pytest.raises(ValueError):
        decidir(
            Estado.COLETANDO_DADOS,
            eventos,
            qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
            alvo,
        )


def test_a_composicao_nao_reimplementa_validar_coerencia() -> None:
    nomes = nomes_usados(MODULO)
    assert "_validar_coerencia" not in nomes
    assert "decidir" not in nomes


# --------------------------------------------------------------------------
# K. Pureza e superfície
# --------------------------------------------------------------------------


def test_a_superficie_publica_tem_exatamente_dois_nomes() -> None:
    assert cycle_inputs.__all__ == [
        "agregar_eventos_primeira_decisao",
        "montar_condicoes_ciclo",
    ]


def test_nenhuma_classe_enum_ou_excecao_nova() -> None:
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    assert [no.name for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)] == []


def test_apenas_imports_permitidos() -> None:
    arvore = ast.parse(MODULO.read_text(encoding="utf-8"))
    raizes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            raizes.update(a.name.split(".")[0] for a in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            raizes.add(no.module.split(".")[0])
    assert raizes <= {"__future__", "casa77_sdr"}

    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert submodulos == {
        "__future__",
        "casa77_sdr.closure_decision",
        "casa77_sdr.handoff_detection",
        "casa77_sdr.state_machine",
    }
    for proibido in (
        "casa77_sdr.coverage_decision",
        "casa77_sdr.interpretation",
        "casa77_sdr.interpretation_events",
        "casa77_sdr.identity",
        "casa77_sdr.qualification",
        "casa77_sdr.rules",
        "casa77_sdr.cycle_events",
        "casa77_sdr.data_update",
        "casa77_sdr.persistence",
        "casa77_sdr.context",
        "yaml",
    ):
        assert proibido not in submodulos


def test_zero_io_rede_clock_llm_persistencia() -> None:
    nomes = nomes_usados(MODULO)
    for proibido in (
        "open",
        "Path",
        "requests",
        "httpx",
        "anthropic",
        "datetime",
        "time",
        "sleep",
        "logging",
        "logger",
        "print",
        "getenv",
        "environ",
        "yaml",
        "safe_load",
        "random",
        "cache",
        "retry",
    ):
        assert proibido not in nomes


def test_zero_chamada_a_produtores_e_a_decidir() -> None:
    nomes = nomes_usados(MODULO)
    for proibido in (
        "decidir",
        "produzir_eventos_da_interpretacao",
        "produzir_eventos_internos_ciclo",
        "detectar_handoff",
        "decidir_encerramento",
        "atualizar_dados_atendimento",
        "decidir_pendencias_e_cobertura",
        "qualificar",
        "avaliar_regras",
        "decidir_interesse_confirmar_disponibilidade",
    ):
        assert proibido not in nomes


def test_a_fronteira_nao_recebe_estado_nem_qualificacao() -> None:
    for funcao in (agregar_eventos_primeira_decisao, montar_condicoes_ciclo):
        anotacoes = {
            str(p.annotation) for p in inspect.signature(funcao).parameters.values()
        }
        for proibido in ("Estado", "Qualificacao", "DecisaoIdentidade", "dict"):
            assert all(proibido not in a for a in anotacoes)


def test_a_fronteira_nao_e_exportada_pelo_pacote() -> None:
    import casa77_sdr

    for nome in ("agregar_eventos_primeira_decisao", "montar_condicoes_ciclo"):
        assert nome not in casa77_sdr.__all__
        assert not hasattr(casa77_sdr, nome)


def test_as_entradas_nao_sao_mutadas() -> None:
    interp = (Evento.E06, Evento.E02)
    internos = (Evento.E09,)
    h = handoff(MotivoHandoff.PEDIDO_HUMANO, MotivoHandoff.CANCELAMENTO)
    e = encerramento()
    antes = (interp, internos, h.motivos, h.evento, e.motivo, e.evento)

    agregar(eventos_interpretacao=interp, eventos_internos=internos, handoff=h, encerramento=e)
    condicoes(handoff=h, encerramento=e)

    assert (interp, internos, h.motivos, h.evento, e.motivo, e.evento) == antes


def test_as_funcoes_sao_deterministicas() -> None:
    assert len({agregar(eventos_interpretacao=(Evento.E06,)) for _ in range(5)}) == 1
    assert len({condicoes(handoff=handoff()) for _ in range(5)}) == 1


CONGELADOS = (
    "src/casa77_sdr/state_machine.py",
    "src/casa77_sdr/interpretation.py",
    "src/casa77_sdr/interpretation_events.py",
    "src/casa77_sdr/handoff_detection.py",
    "src/casa77_sdr/closure_decision.py",
    "src/casa77_sdr/cycle_events.py",
    "src/casa77_sdr/data_update.py",
    "src/casa77_sdr/coverage_decision.py",
    "src/casa77_sdr/identity.py",
    "src/casa77_sdr/qualification.py",
    "src/casa77_sdr/rules.py",
    "src/casa77_sdr/persistence.py",
    "src/casa77_sdr/context.py",
    "src/casa77_sdr/__init__.py",
)


@pytest.mark.parametrize("caminho", CONGELADOS, ids=lambda c: c.split("/")[-1])
def test_nenhum_congelado_importa_a_nova_fronteira(caminho: str) -> None:
    """A fronteira é **posterior**: nada aprovado passa a depender dela."""
    fonte = (Path(__file__).resolve().parents[1] / caminho).read_text(encoding="utf-8")
    assert "cycle_inputs" not in fonte
    assert "agregar_eventos_primeira_decisao" not in fonte
    assert "montar_condicoes_ciclo" not in fonte
