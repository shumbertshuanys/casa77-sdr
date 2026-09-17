"""Testes do produtor determinístico dos eventos internos do ciclo.

Cobre o contrato vivo de `docs/07-arquitetura-motor-respostas.md` §6.3
(`CIE-1`–`CIE-10`): a saída fechada em `E07`/`E08`/`E09`, as regras exatas dos
três eventos, a ordem canônica sem precedência, a ausência de agregação e a
pureza.

`src/casa77_sdr/qualification.py`, `src/casa77_sdr/coverage_decision.py` e
`src/casa77_sdr/state_machine.py` permanecem **inalterados** e continuam as
autoridades das suas próprias fronteiras: aqui eles são apenas **exercitados**,
nunca corrigidos. Os testes de composição com a máquina **não** transformam
`cycle_events.py` em chamador dela.

Todas as fixtures são **fictícias e genéricas**: zero PII, zero conversa real,
zero valor comercial. Os limites de capacidade usados em `qualificar(...)` são
**artificiais** e não replicam a base aprovada.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import cycle_events
from casa77_sdr.coverage_decision import (
    CausaE09,
    ClassificacaoPendencia,
    MotivoE09,
    ResultadoS2D8,
)
from casa77_sdr.cycle_events import produzir_eventos_internos_ciclo
from casa77_sdr.interpretation import AssuntoComercial
from casa77_sdr.qualification import (
    DadosQualificacao,
    FormatoEvento,
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
    qualificar,
)
from casa77_sdr.rules import DadosAtendimento, MotivoViolacao, Violacao
from casa77_sdr.state_machine import (
    AcaoMaquina,
    CondicoesCiclo,
    EfeitoParalelo,
    Estado,
    Evento,
    Transicao,
    decidir,
)

MODULO_CICLO = (
    Path(__file__).resolve().parents[1] / "src" / "casa77_sdr" / "cycle_events.py"
)


def codigo_executavel(caminho: Path) -> str:
    """Devolve o módulo **sem docstrings e sem comentários**.

    As proibições deste mandato são sobre o que o módulo **faz**, não sobre o
    que a prosa **cita**: o contrato é explicado citando as fronteiras que a
    fronteira não invade, e confundir a citação com a dependência produziria
    falso positivo.
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


#: Conjunto fechado desta capacidade.
TRES = (Evento.E07, Evento.E08, Evento.E09)

#: Tudo que a fronteira **nunca** pode produzir.
PROIBIDOS = tuple(evento for evento in Evento if evento not in TRES)

#: Limites **artificiais**, jamais comerciais (I06).
SENTADOS = 7
COQUETEL = 9

RESULTADOS_POSITIVOS = (
    ResultadoQualificacao.QUALIFICADO,
    ResultadoQualificacao.QUALIFICADO_COM_RESSALVA,
)
RESULTADOS_NAO_POSITIVOS = tuple(
    r for r in ResultadoQualificacao if r not in RESULTADOS_POSITIVOS
)
RESULTADOS_NAO_INCOMPATIVEIS = tuple(
    r for r in ResultadoQualificacao if r is not ResultadoQualificacao.INCOMPATIVEL
)


# --------------------------------------------------------------------------
# Fixtures genéricas
# --------------------------------------------------------------------------

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
    """`Qualificacao` já calculada, sem recalcular nada."""
    base: dict[str, Any] = {
        "resultado": resultado,
        "motivo": _MOTIVO_POR_RESULTADO[resultado],
    }
    base.update(ajustes)
    return Qualificacao(**base)


def base_ficticia() -> dict[str, Any]:
    """Base mínima com limites **artificiais**, não comerciais."""
    return {
        "capacidade": {
            "convidados_sentados": SENTADOS,
            "formato_coquetel": COQUETEL,
        }
    }


def dados_ficticios(**ajustes: Any) -> DadosQualificacao:
    campos = {
        "tipo_evento": "tipo-artificial",
        "data_nomeada": "data-artificial",
        "convidados": 3,
    }
    atendimento = {k: ajustes.pop(k, v) for k, v in campos.items()}
    base: dict[str, Any] = {
        "atendimento": DadosAtendimento(**atendimento),
        "nome": "nome-artificial",
        "contato": "contato-artificial",
        "formato": None,
    }
    base.update(ajustes)
    return DadosQualificacao(**base)


def causa(
    motivo: MotivoE09 = MotivoE09.SEM_RESPOSTA_APROVADA_EMITIVEL,
    classificacao: ClassificacaoPendencia = ClassificacaoPendencia.ACESSORIA,
    assunto: AssuntoComercial | None = AssuntoComercial.PRECO_LOCACAO,
    caminho_yaml: str | None = None,
) -> CausaE09:
    return CausaE09(
        motivo=motivo,
        classificacao=classificacao,
        assunto=assunto,
        caminho_yaml=caminho_yaml,
    )


def s2d8(
    causas: tuple[CausaE09, ...] = (),
    *,
    pendencia_impeditiva: bool = False,
    resposta_aprovada_disponivel: bool = True,
) -> ResultadoS2D8:
    return ResultadoS2D8(
        pendencia_impeditiva=pendencia_impeditiva,
        pendencias_impeditivas=(),
        resposta_aprovada_disponivel=resposta_aprovada_disponivel,
        fragmentos_autorizados=(),
        pendencias_resposta=(),
        causas_e09=causas,
    )


# --------------------------------------------------------------------------
# A. Ausência total e saída fechada
# --------------------------------------------------------------------------


def test_ausencia_total_produz_tupla_vazia() -> None:
    resultado = produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS), False, s2d8()
    )
    assert resultado == ()


def test_a_saida_e_sempre_subconjunto_dos_tres() -> None:
    for resultado_q in ResultadoQualificacao:
        for insumo in (True, False):
            for causas in ((), (causa(),)):
                saida = produzir_eventos_internos_ciclo(
                    qual(resultado_q), insumo, s2d8(causas)
                )
                assert set(saida) <= set(TRES)
                assert isinstance(saida, tuple)
                assert all(isinstance(item, Evento) for item in saida)


def test_o_vocabulario_proibido_tem_quinze_eventos() -> None:
    assert len(PROIBIDOS) == 15
    assert set(PROIBIDOS) == set(Evento) - set(TRES)


@pytest.mark.parametrize("proibido", PROIBIDOS, ids=lambda e: e.value)
def test_evento_proibido_nunca_aparece(proibido: Evento) -> None:
    for resultado_q in ResultadoQualificacao:
        for insumo in (True, False):
            for causas in ((), (causa(),), (causa(), causa(assunto=None))):
                assert proibido not in produzir_eventos_internos_ciclo(
                    qual(resultado_q), insumo, s2d8(causas)
                )


def test_zero_duplicata_em_qualquer_combinacao() -> None:
    for resultado_q in ResultadoQualificacao:
        for insumo in (True, False):
            for causas in ((), (causa(),), (causa(), causa(), causa())):
                saida = produzir_eventos_internos_ciclo(
                    qual(resultado_q), insumo, s2d8(causas)
                )
                assert len(saida) == len(set(saida))


# --------------------------------------------------------------------------
# B. `E07`
# --------------------------------------------------------------------------


@pytest.mark.parametrize("resultado_q", RESULTADOS_POSITIVOS, ids=lambda r: r.value)
def test_e07_com_resultado_positivo_e_insumo_verdadeiro(
    resultado_q: ResultadoQualificacao,
) -> None:
    assert produzir_eventos_internos_ciclo(qual(resultado_q), True, s2d8()) == (
        Evento.E07,
    )


@pytest.mark.parametrize("resultado_q", RESULTADOS_POSITIVOS, ids=lambda r: r.value)
def test_resultado_positivo_com_insumo_falso_nao_produz_e07(
    resultado_q: ResultadoQualificacao,
) -> None:
    """`docs/06` §2.2: `E07` exige **as duas** condições no mesmo ciclo."""
    assert produzir_eventos_internos_ciclo(qual(resultado_q), False, s2d8()) == ()


@pytest.mark.parametrize(
    "resultado_q", RESULTADOS_NAO_POSITIVOS, ids=lambda r: r.value
)
def test_insumo_verdadeiro_com_resultado_nao_positivo_nao_produz_e07(
    resultado_q: ResultadoQualificacao,
) -> None:
    assert Evento.E07 not in produzir_eventos_internos_ciclo(
        qual(resultado_q), True, s2d8()
    )


def test_existem_tres_resultados_nao_positivos() -> None:
    assert len(RESULTADOS_NAO_POSITIVOS) == 3
    assert len(list(ResultadoQualificacao)) == 5


@pytest.mark.parametrize(
    "valor", [None, 1, 0, "True", "", (), [], 1.0], ids=repr
)
def test_insumo_de_tipo_errado_e_type_error(valor: Any) -> None:
    """Inteiro, texto e `None` **não** são substituto silencioso do booleano."""
    with pytest.raises(TypeError):
        produzir_eventos_internos_ciclo(
            qual(ResultadoQualificacao.QUALIFICADO), valor, s2d8()
        )


def test_o_modulo_nao_decide_a_mutacao_do_insumo() -> None:
    """`CIE-3`: a mutação é fato recebido, não calculado aqui."""
    corpo = codigo_executavel(MODULO_CICLO)
    for proibido in (
        "DadosQualificacao",
        "contexto",
        "anterior",
        "campos_ausentes",
        "DadosAtendimento",
    ):
        assert proibido not in corpo


# --------------------------------------------------------------------------
# C. `E08`
# --------------------------------------------------------------------------


def test_e08_com_incompativel() -> None:
    assert produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.INCOMPATIVEL), False, s2d8()
    ) == (Evento.E08,)


@pytest.mark.parametrize(
    "resultado_q", RESULTADOS_NAO_INCOMPATIVEIS, ids=lambda r: r.value
)
def test_demais_resultados_nao_produzem_e08(
    resultado_q: ResultadoQualificacao,
) -> None:
    for insumo in (True, False):
        assert Evento.E08 not in produzir_eventos_internos_ciclo(
            qual(resultado_q), insumo, s2d8()
        )


def test_e08_nao_depende_do_insumo() -> None:
    incompativel = qual(ResultadoQualificacao.INCOMPATIVEL)
    assert produzir_eventos_internos_ciclo(
        incompativel, True, s2d8()
    ) == produzir_eventos_internos_ciclo(incompativel, False, s2d8())


def test_e08_nao_depende_das_violacoes_recebidas() -> None:
    """A classe da violação — T05/T22 × T06/T23 — pertence à máquina."""
    sem = qual(ResultadoQualificacao.INCOMPATIVEL)
    com = qual(
        ResultadoQualificacao.INCOMPATIVEL,
        violacoes=(
            Violacao(
                motivo=MotivoViolacao.DATA_NAO_ACEITA,
                campo_yaml="eventos.datas_nao_aceitas",
                valor_informado="data-artificial",
            ),
            Violacao(
                motivo=MotivoViolacao.TIPO_NAO_ACEITO,
                campo_yaml="eventos.nao_aceitos",
                valor_informado="tipo-artificial",
            ),
        ),
    )
    assert produzir_eventos_internos_ciclo(sem, False, s2d8()) == (Evento.E08,)
    assert produzir_eventos_internos_ciclo(com, False, s2d8()) == (Evento.E08,)


def test_o_modulo_nao_recalcula_incompatibilidade() -> None:
    """`CIE-4`: nem YAML, nem `Violacao`, nem classe de tratamento."""
    corpo = codigo_executavel(MODULO_CICLO)
    for proibido in ("Violacao", "MotivoViolacao", "violacoes", "capacidade", "yaml"):
        assert proibido not in corpo


def test_e08_a_partir_de_qualificar_real() -> None:
    """Evidência do contrato real: a `Qualificacao` vem de `qualificar(...)`."""
    violacao = Violacao(
        motivo=MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
        campo_yaml="capacidade.formato_coquetel",
        valor_informado=COQUETEL + 1,
    )
    calculada = qualificar(
        dados_ficticios(convidados=COQUETEL + 1),
        (violacao,),
        (),
        base_ficticia(),
    )
    assert calculada.resultado is ResultadoQualificacao.INCOMPATIVEL
    assert produzir_eventos_internos_ciclo(calculada, False, s2d8()) == (Evento.E08,)


def test_e07_a_partir_de_qualificar_real() -> None:
    calculada = qualificar(dados_ficticios(), (), (), base_ficticia())
    assert calculada.resultado is ResultadoQualificacao.QUALIFICADO
    assert produzir_eventos_internos_ciclo(calculada, True, s2d8()) == (Evento.E07,)


def test_e07_com_ressalva_a_partir_de_qualificar_real() -> None:
    calculada = qualificar(
        dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO),
        (),
        (),
        base_ficticia(),
    )
    assert calculada.resultado is ResultadoQualificacao.QUALIFICADO_COM_RESSALVA
    assert produzir_eventos_internos_ciclo(calculada, True, s2d8()) == (Evento.E07,)


def test_dados_incompletos_real_nao_produz_evento_algum() -> None:
    calculada = qualificar(dados_ficticios(tipo_evento=None), (), (), base_ficticia())
    assert calculada.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS
    assert produzir_eventos_internos_ciclo(calculada, True, s2d8()) == ()


def test_indefinido_real_nao_produz_evento_algum() -> None:
    calculada = qualificar(
        dados_ficticios(), (), ("pendencia-artificial",), base_ficticia()
    )
    assert calculada.resultado is ResultadoQualificacao.INDEFINIDO
    assert produzir_eventos_internos_ciclo(calculada, True, s2d8()) == ()


# --------------------------------------------------------------------------
# D. `E09`
# --------------------------------------------------------------------------


def test_e09_com_uma_causa() -> None:
    assert produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS), False, s2d8((causa(),))
    ) == (Evento.E09,)


@pytest.mark.parametrize("quantidade", [1, 2, 3, 7], ids=lambda n: f"{n}causas")
def test_multiplas_causas_produzem_um_unico_e09(quantidade: int) -> None:
    """`docs/06` §2.2, regra 2: **no máximo um `E09` por ciclo**."""
    causas = tuple(causa() for _ in range(quantidade))
    saida = produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS), False, s2d8(causas)
    )
    assert saida == (Evento.E09,)
    assert saida.count(Evento.E09) == 1


def test_sem_causas_nao_produz_e09() -> None:
    assert Evento.E09 not in produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS), False, s2d8(())
    )


def test_resposta_aprovada_indisponivel_sem_causa_nao_inventa_e09() -> None:
    """`CIE-5`: a condição 4 isolada **não** confirma `E09`."""
    resultado = produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        False,
        s2d8((), resposta_aprovada_disponivel=False),
    )
    assert resultado == ()


def test_pendencia_impeditiva_sem_causa_nao_inventa_e09() -> None:
    """`CIE-5`: a condição 2 isolada **não** confirma `E09`."""
    resultado = produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        False,
        s2d8((), pendencia_impeditiva=True),
    )
    assert resultado == ()


def test_as_duas_condicoes_falsas_juntas_sem_causa_nao_inventam_e09() -> None:
    resultado = produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS),
        False,
        s2d8((), pendencia_impeditiva=True, resposta_aprovada_disponivel=False),
    )
    assert resultado == ()


@pytest.mark.parametrize("motivo", list(MotivoE09), ids=lambda m: m.value)
@pytest.mark.parametrize(
    "classificacao", list(ClassificacaoPendencia), ids=lambda c: c.value
)
def test_qualquer_motivo_e_classificacao_confirmam_o_mesmo_e09(
    motivo: MotivoE09, classificacao: ClassificacaoPendencia
) -> None:
    """`CIE-6`: `IMPEDITIVA` pertence ao contrato; nada aqui exige acessória."""
    alvo = causa(motivo=motivo, classificacao=classificacao)
    assert produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.DADOS_INCOMPLETOS), False, s2d8((alvo,))
    ) == (Evento.E09,)


def test_o_modulo_nao_reinterpreta_as_causas() -> None:
    """`CIE-5`: nem motivo, nem classificação, nem deduplicação."""
    corpo = codigo_executavel(MODULO_CICLO)
    for proibido in (
        "MotivoE09",
        "ClassificacaoPendencia",
        "CausaE09",
        "IMPEDITIVA",
        "ACESSORIA",
        "caminho_yaml",
        "pendencias_resposta",
        "fragmentos_autorizados",
    ):
        assert proibido not in corpo


def test_causas_de_tipo_errado_e_type_error() -> None:
    invalido = ResultadoS2D8(
        pendencia_impeditiva=False,
        pendencias_impeditivas=(),
        resposta_aprovada_disponivel=True,
        fragmentos_autorizados=(),
        pendencias_resposta=(),
        causas_e09=[causa()],  # type: ignore[arg-type]
    )
    with pytest.raises(TypeError):
        produzir_eventos_internos_ciclo(
            qual(ResultadoQualificacao.DADOS_INCOMPLETOS), False, invalido
        )


# --------------------------------------------------------------------------
# E. Composições válidas e ordem canônica
# --------------------------------------------------------------------------

#: As **seis** composições que o contrato admite (`CIE-8`).
COMPOSICOES_VALIDAS = (
    (),
    (Evento.E07,),
    (Evento.E08,),
    (Evento.E09,),
    (Evento.E07, Evento.E09),
    (Evento.E08, Evento.E09),
)


def test_e07_mais_e09() -> None:
    assert produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.QUALIFICADO), True, s2d8((causa(),))
    ) == (Evento.E07, Evento.E09)


def test_e08_mais_e09() -> None:
    assert produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.INCOMPATIVEL), True, s2d8((causa(),))
    ) == (Evento.E08, Evento.E09)


def test_as_seis_composicoes_sao_produziveis() -> None:
    produzidas = set()
    for resultado_q in ResultadoQualificacao:
        for insumo in (True, False):
            for causas in ((), (causa(),)):
                produzidas.add(
                    produzir_eventos_internos_ciclo(
                        qual(resultado_q), insumo, s2d8(causas)
                    )
                )
    assert produzidas == set(COMPOSICOES_VALIDAS)
    assert len(produzidas) == 6


def test_e07_e_e08_nunca_coexistem() -> None:
    """Os resultados de qualificação são mutuamente exclusivos."""
    for resultado_q in ResultadoQualificacao:
        for insumo in (True, False):
            for causas in ((), (causa(),)):
                saida = produzir_eventos_internos_ciclo(
                    qual(resultado_q), insumo, s2d8(causas)
                )
                assert not {Evento.E07, Evento.E08} <= set(saida)


def test_e07_e_e08_nunca_coexistem_com_qualificacao_real() -> None:
    """Nenhuma `Qualificacao` de `qualificar(...)` produz os dois."""
    cenarios = (
        qualificar(dados_ficticios(), (), (), base_ficticia()),
        qualificar(
            dados_ficticios(convidados=COQUETEL + 1),
            (
                Violacao(
                    motivo=MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE,
                    campo_yaml="capacidade.formato_coquetel",
                    valor_informado=COQUETEL + 1,
                ),
            ),
            (),
            base_ficticia(),
        ),
        qualificar(
            dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO),
            (),
            (),
            base_ficticia(),
        ),
        qualificar(dados_ficticios(tipo_evento=None), (), (), base_ficticia()),
        qualificar(dados_ficticios(), (), ("pendencia-artificial",), base_ficticia()),
    )
    for calculada in cenarios:
        for insumo in (True, False):
            saida = produzir_eventos_internos_ciclo(
                calculada, insumo, s2d8((causa(),))
            )
            assert not {Evento.E07, Evento.E08} <= set(saida)


def test_a_saida_respeita_a_ordem_canonica() -> None:
    posicao = {evento: i for i, evento in enumerate(TRES)}
    for resultado_q in ResultadoQualificacao:
        for insumo in (True, False):
            for causas in ((), (causa(),)):
                saida = list(
                    produzir_eventos_internos_ciclo(
                        qual(resultado_q), insumo, s2d8(causas)
                    )
                )
                assert saida == sorted(saida, key=lambda e: posicao[e])


def test_a_ordem_canonica_e_e07_e08_e09() -> None:
    assert cycle_events._ORDEM_CANONICA == (Evento.E07, Evento.E08, Evento.E09)


def test_nenhuma_exclusao_artificial_entre_e07_e_e09_acessorio() -> None:
    acessoria = causa(classificacao=ClassificacaoPendencia.ACESSORIA)
    assert produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.QUALIFICADO), True, s2d8((acessoria,))
    ) == (Evento.E07, Evento.E09)


def test_nenhuma_exclusao_artificial_entre_e08_e_e09_acessorio() -> None:
    acessoria = causa(classificacao=ClassificacaoPendencia.ACESSORIA)
    assert produzir_eventos_internos_ciclo(
        qual(ResultadoQualificacao.INCOMPATIVEL), False, s2d8((acessoria,))
    ) == (Evento.E08, Evento.E09)


# --------------------------------------------------------------------------
# F. Tipos inválidos
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "valor", [None, "qualificado", 1, True, (), [], {}, object()], ids=repr
)
def test_qualificacao_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        produzir_eventos_internos_ciclo(valor, True, s2d8())


@pytest.mark.parametrize(
    "valor", [None, "s2d8", 1, True, (), [], {}, object()], ids=repr
)
def test_resultado_s2d8_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        produzir_eventos_internos_ciclo(
            qual(ResultadoQualificacao.QUALIFICADO), True, valor
        )


def test_resultado_de_qualificacao_de_tipo_errado_e_type_error() -> None:
    invalida = Qualificacao(
        resultado="qualificado",  # type: ignore[arg-type]
        motivo=MotivoQualificacao.COMPATIVEL,
    )
    with pytest.raises(TypeError):
        produzir_eventos_internos_ciclo(invalida, True, s2d8())


# --------------------------------------------------------------------------
# G. Composição com a `MaquinaEstados` — o contrato vigente não muda
# --------------------------------------------------------------------------


def test_e07_produzido_e_aceito_pela_maquina() -> None:
    """`QUALIFICADO` puro resolve por **T13** — a guarda de T08 exige ressalva."""
    calculada = qualificar(dados_ficticios(), (), (), base_ficticia())
    assert calculada.resultado is ResultadoQualificacao.QUALIFICADO
    eventos = produzir_eventos_internos_ciclo(calculada, True, s2d8())
    assert eventos == (Evento.E07,)
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        eventos,
        calculada,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert Transicao.T13 in decisao.caminho
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF
    assert Evento.E07 in decisao.eventos_consumidos


def test_e07_com_ressalva_produzido_e_aceito_pela_maquina() -> None:
    """`QUALIFICADO_COM_RESSALVA` satisfaz a guarda de **T08**."""
    calculada = qualificar(
        dados_ficticios(convidados=SENTADOS + 1, formato=FormatoEvento.SENTADO),
        (),
        (),
        base_ficticia(),
    )
    assert calculada.resultado is ResultadoQualificacao.QUALIFICADO_COM_RESSALVA
    eventos = produzir_eventos_internos_ciclo(calculada, True, s2d8())
    assert eventos == (Evento.E07,)
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        eventos,
        calculada,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert Transicao.T08 in decisao.caminho
    assert AcaoMaquina.INFORMAR_RESSALVA_DE_CAPACIDADE in decisao.acoes


def test_e07_produzido_e_aceito_em_respondendo_duvidas() -> None:
    """A mesma saída alimenta **T40** a partir de `respondendo_duvidas`."""
    calculada = qualificar(dados_ficticios(), (), (), base_ficticia())
    eventos = produzir_eventos_internos_ciclo(calculada, True, s2d8())
    decisao = decidir(
        Estado.RESPONDENDO_DUVIDAS,
        eventos,
        calculada,
        CondicoesCiclo(insumo_qualificacao_atualizado=True),
    )
    assert Transicao.T40 in decisao.caminho


def test_e08_produzido_e_aceito_pela_maquina_com_qualificacao_real() -> None:
    violacao = Violacao(
        motivo=MotivoViolacao.DATA_NAO_ACEITA,
        campo_yaml="eventos.datas_nao_aceitas",
        valor_informado="data-artificial",
    )
    calculada = qualificar(
        dados_ficticios(), (violacao,), (), base_ficticia()
    )
    eventos = produzir_eventos_internos_ciclo(calculada, False, s2d8())
    assert eventos == (Evento.E08,)
    decisao = decidir(
        Estado.COLETANDO_DADOS, eventos, calculada, CondicoesCiclo()
    )
    assert Transicao.T05 in decisao.caminho
    assert AcaoMaquina.INFORMAR_REGRA_INCOMPATIVEL in decisao.acoes


def test_e09_produzido_e_aceito_pela_maquina_com_a_condicao_correspondente() -> None:
    calculada = qual(ResultadoQualificacao.DADOS_INCOMPLETOS)
    eventos = produzir_eventos_internos_ciclo(calculada, False, s2d8((causa(),)))
    assert eventos == (Evento.E09,)
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        eventos,
        calculada,
        # A classificação chega **separadamente** — `causas_e09` não atravessa.
        CondicoesCiclo(pendencia_impeditiva=False),
    )
    assert Transicao.T12 in decisao.caminho


def test_e09_impeditivo_produzido_e_aceito_pela_maquina() -> None:
    calculada = qual(ResultadoQualificacao.INDEFINIDO)
    eventos = produzir_eventos_internos_ciclo(
        calculada,
        False,
        s2d8((causa(classificacao=ClassificacaoPendencia.IMPEDITIVA),), pendencia_impeditiva=True),
    )
    assert eventos == (Evento.E09,)
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        eventos,
        calculada,
        CondicoesCiclo(pendencia_impeditiva=True),
    )
    assert Transicao.T11 in decisao.caminho


def test_e07_mais_e09_acessorio_preserva_a_precedencia_da_maquina() -> None:
    calculada = qualificar(dados_ficticios(), (), (), base_ficticia())
    eventos = produzir_eventos_internos_ciclo(calculada, True, s2d8((causa(),)))
    assert eventos == (Evento.E07, Evento.E09)
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        eventos,
        calculada,
        CondicoesCiclo(
            insumo_qualificacao_atualizado=True, pendencia_impeditiva=False
        ),
    )
    # A máquina decide a precedência; o produtor apenas entregou os dois.
    # Contrato vigente: T13 (C8) resolve primeiro e move o estado, de modo que
    # T12 (C10) não encontra mais a sua origem `coletando_dados`. O `E09`
    # sobrevive e é resolvido pelo efeito paralelo **P5** — nada disso é
    # decidido aqui.
    assert Transicao.T13 in decisao.caminho
    assert decisao.eventos_consumidos == (Evento.E07,)
    assert EfeitoParalelo.P5 in decisao.efeitos
    assert decisao.estado_final is Estado.PRONTO_PARA_HANDOFF


def test_e08_mais_e09_acessorio_preserva_a_precedencia_da_maquina() -> None:
    violacao = Violacao(
        motivo=MotivoViolacao.TIPO_NAO_ACEITO,
        campo_yaml="eventos.nao_aceitos",
        valor_informado="tipo-artificial",
    )
    calculada = qualificar(dados_ficticios(), (violacao,), (), base_ficticia())
    eventos = produzir_eventos_internos_ciclo(calculada, False, s2d8((causa(),)))
    assert eventos == (Evento.E08, Evento.E09)
    decisao = decidir(
        Estado.COLETANDO_DADOS,
        eventos,
        calculada,
        CondicoesCiclo(pendencia_impeditiva=False),
    )
    # `docs/06` §8, A8-b: T06/T23 preserva o estado e C10 consome o `E09`.
    assert Transicao.T06 in decisao.caminho
    assert Transicao.T12 in decisao.caminho


def test_a_maquina_permanece_inalterada() -> None:
    assert len(list(Evento)) == 18
    assert len(list(Transicao)) == 41
    assert len(list(ResultadoQualificacao)) == 5


# --------------------------------------------------------------------------
# H. Pureza e fronteira do módulo
# --------------------------------------------------------------------------


def modulos_importados(caminho: Path) -> set[str]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    raizes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            raizes.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            raizes.add(no.module.split(".")[0])
    return raizes


def test_a_fronteira_e_pura_e_nao_importa_nada_proibido() -> None:
    assert modulos_importados(MODULO_CICLO) <= {"__future__", "casa77_sdr"}

    arvore = ast.parse(MODULO_CICLO.read_text(encoding="utf-8"))
    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert submodulos == {
        "__future__",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.qualification",
        "casa77_sdr.state_machine",
    }
    for proibido in (
        "casa77_sdr.interpretation",
        "casa77_sdr.interpretation_events",
        "casa77_sdr.handoff_detection",
        "casa77_sdr.closure_decision",
        "casa77_sdr.knowledge",
        "casa77_sdr.persistence",
        "casa77_sdr.context",
        "casa77_sdr.response_assembly",
        "yaml",
    ):
        assert proibido not in submodulos

    chamadas = {
        no.func.attr if isinstance(no.func, ast.Attribute) else getattr(no.func, "id", "")
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call)
    }
    assert chamadas & {
        "open",
        "getenv",
        "sleep",
        "now",
        "safe_load",
        "read_text",
        "print",
        "decidir",
        "qualificar",
        "decidir_pendencias_e_cobertura",
    } == set()


def test_a_superficie_publica_e_fechada_em_um_produtor() -> None:
    assert cycle_events.__all__ == ["produzir_eventos_internos_ciclo"]


def test_a_fronteira_nao_e_exportada_pelo_pacote() -> None:
    import casa77_sdr

    assert "produzir_eventos_internos_ciclo" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "produzir_eventos_internos_ciclo")


def test_nenhum_dto_nem_excecao_publica_nova_e_criada() -> None:
    arvore = ast.parse(MODULO_CICLO.read_text(encoding="utf-8"))
    classes = [no for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)]
    assert classes == []


def test_a_assinatura_e_exatamente_a_do_contrato() -> None:
    parametros = inspect.signature(produzir_eventos_internos_ciclo).parameters
    assert list(parametros) == [
        "qualificacao",
        "insumo_qualificacao_atualizado",
        "resultado_s2d8",
    ]
    anotacoes = {nome: str(p.annotation) for nome, p in parametros.items()}
    for proibido in ("Estado", "CondicoesCiclo", "Interpretacao", "dict"):
        assert all(proibido not in valor for valor in anotacoes.values())


def test_o_modulo_nao_agrega_nem_monta_condicoes_ciclo() -> None:
    """`CIE-9`: nem agregação, nem `CondicoesCiclo`, nem chamada à máquina."""
    corpo = codigo_executavel(MODULO_CICLO)
    for proibido in (
        "CondicoesCiclo",
        "decidir(",
        "produzir_eventos_da_interpretacao",
        "decidir_encerramento",
        "detectar_handoff",
        "Estado",
        "Interpretacao",
    ):
        assert proibido not in corpo


def test_as_entradas_nao_sao_mutadas() -> None:
    calculada = qualificar(dados_ficticios(), (), (), base_ficticia())
    resultado = s2d8((causa(), causa(assunto=None)))
    antes_q = (
        calculada.resultado,
        calculada.motivo,
        calculada.campos_ausentes,
        calculada.violacoes,
        calculada.pendencias_impeditivas,
    )
    antes_s = (
        resultado.pendencia_impeditiva,
        resultado.pendencias_impeditivas,
        resultado.resposta_aprovada_disponivel,
        resultado.fragmentos_autorizados,
        resultado.causas_e09,
    )
    produzir_eventos_internos_ciclo(calculada, True, resultado)
    assert (
        calculada.resultado,
        calculada.motivo,
        calculada.campos_ausentes,
        calculada.violacoes,
        calculada.pendencias_impeditivas,
    ) == antes_q
    assert (
        resultado.pendencia_impeditiva,
        resultado.pendencias_impeditivas,
        resultado.resposta_aprovada_disponivel,
        resultado.fragmentos_autorizados,
        resultado.causas_e09,
    ) == antes_s


def test_a_funcao_e_deterministica() -> None:
    alvo = qual(ResultadoQualificacao.QUALIFICADO)
    resultado = s2d8((causa(),))
    assert (
        len({produzir_eventos_internos_ciclo(alvo, True, resultado) for _ in range(5)})
        == 1
    )


# --------------------------------------------------------------------------
# I. Preservação das fronteiras já aprovadas
# --------------------------------------------------------------------------

CONGELADOS = (
    "src/casa77_sdr/qualification.py",
    "src/casa77_sdr/coverage_decision.py",
    "src/casa77_sdr/interpretation_events.py",
    "src/casa77_sdr/handoff_detection.py",
    "src/casa77_sdr/closure_decision.py",
    "src/casa77_sdr/state_machine.py",
    "src/casa77_sdr/__init__.py",
)


@pytest.mark.parametrize("caminho", CONGELADOS, ids=lambda c: c.split("/")[-1])
def test_nenhum_congelado_importa_a_nova_fronteira(caminho: str) -> None:
    """A fronteira é **posterior**: nenhum módulo aprovado passa a depender dela."""
    fonte = (Path(__file__).resolve().parents[1] / caminho).read_text(encoding="utf-8")
    assert "cycle_events" not in fonte
    assert "produzir_eventos_internos_ciclo" not in fonte


def test_s2d8_continua_sem_criar_nem_confirmar_e09() -> None:
    """`D8-E8` preservado: `coverage_decision.py` não conhece `Evento`."""
    fonte = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "casa77_sdr"
        / "coverage_decision.py"
    ).read_text(encoding="utf-8")
    arvore = ast.parse(fonte)
    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert "casa77_sdr.state_machine" not in submodulos
    nomes = {no.id for no in ast.walk(arvore) if isinstance(no, ast.Name)}
    assert "Evento" not in nomes
    # A docstring **afirma** que `e09_confirmado` não existe; o que precisa ser
    # provado é que o campo não existe no DTO, não que a palavra não apareça.
    import dataclasses

    assert "e09_confirmado" not in {
        campo.name for campo in dataclasses.fields(ResultadoS2D8)
    }


def test_o_resultado_s2d8_continua_com_seis_campos() -> None:
    import dataclasses

    assert [campo.name for campo in dataclasses.fields(ResultadoS2D8)] == [
        "pendencia_impeditiva",
        "pendencias_impeditivas",
        "resposta_aprovada_disponivel",
        "fragmentos_autorizados",
        "pendencias_resposta",
        "causas_e09",
    ]


def test_as_causas_continuam_fora_de_condicoes_ciclo() -> None:
    """`D8-E8`: `causas_e09` não integra `CondicoesCiclo`, e nada aqui a leva."""
    import dataclasses

    campos = {campo.name for campo in dataclasses.fields(CondicoesCiclo)}
    assert "causas_e09" not in campos
    assert "motivo_e09" not in campos
    assert len(campos) == 8
