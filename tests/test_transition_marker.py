"""Testes da decisão determinística do marco temporal (doc 07 §6.2, N-a-T3–T7).

A função sob teste responde **uma única pergunta**: qual valor de
`instante_ultima_transicao` o futuro chamador da etapa 13 deverá usar. Ela
**não** escreve na persistência, **não** monta `RegistroAtendimento`, **não**
integra a etapa 13 e **não** implementa o `OrquestradorMotor`.

Fixtures totalmente artificiais: instantes claramente fictícios, sem dado
pessoal, sem conversa real e sem dado comercial.

Onde o comportamento da `MaquinaEstados` é o que está sendo provado — T33 que
preserva estado e o ciclo `encerrado` → reabertura → `encerrado` —, as decisões
vêm de `decidir(...)` **real**, nunca fabricadas à mão.
"""

from __future__ import annotations

import ast
import inspect
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from casa77_sdr.qualification import (
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.state_machine import (
    CondicoesCiclo,
    DecisaoMaquina,
    Estado,
    Evento,
    Identidade,
    MotivoEncerramento,
    Transicao,
    decidir,
)
from casa77_sdr.transition_marker import decidir_instante_ultima_transicao

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "transition_marker.py"

CICLO = datetime(2000, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
MARCO_ANTERIOR = datetime(2000, 6, 1, 8, 30, 0, tzinfo=timezone.utc)

SEM_CONDICOES = CondicoesCiclo()
# Qualificação mínima aceita pela máquina real; o conteúdo é irrelevante para a
# decisão do marco — ela só observa `transicoes_que_mudaram_estado`.
INCOMPLETOS = Qualificacao(
    resultado=ResultadoQualificacao.DADOS_INCOMPLETOS,
    motivo=MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES,
    campos_ausentes=("nome",),
)


def decisao_vazia() -> DecisaoMaquina:
    """Decisão cuja projeção é vazia — nenhuma `Txx` mudou estado."""
    return DecisaoMaquina(estado_final=Estado.COLETANDO_DADOS)


def decisao_com_mudanca() -> DecisaoMaquina:
    """Decisão cuja projeção não é vazia."""
    return DecisaoMaquina(
        estado_final=Estado.COLETANDO_DADOS,
        caminho=(Transicao.T01,),
        transicoes_que_mudaram_estado=(Transicao.T01,),
    )


def decidir_marco(
    *,
    criacao: bool,
    decisoes: tuple[DecisaoMaquina, ...],
    marco: datetime | None = MARCO_ANTERIOR,
    ciclo: datetime = CICLO,
) -> datetime | None:
    return decidir_instante_ultima_transicao(
        criacao_de_atendimento=criacao,
        instante_de_referencia_do_ciclo=ciclo,
        marco_atual=marco,
        decisoes_do_ciclo=decisoes,
    )


# --------------------------------------------------------------------------
# A–C. Criação — N-a-T3
# --------------------------------------------------------------------------


def test_criacao_sem_decisoes_usa_o_instante_do_ciclo() -> None:
    assert decidir_marco(criacao=True, decisoes=(), marco=None) is CICLO


def test_criacao_com_decisao_vazia_usa_o_instante_do_ciclo() -> None:
    """A projeção da máquina **não é pré-requisito** para inicializar o marco."""
    assert decidir_marco(criacao=True, decisoes=(decisao_vazia(),), marco=None) is CICLO


def test_criacao_com_mudanca_usa_o_instante_do_ciclo() -> None:
    assert (
        decidir_marco(criacao=True, decisoes=(decisao_com_mudanca(),), marco=None)
        is CICLO
    )


def test_criacao_com_marco_atual_preenchido_nao_e_rejeitada() -> None:
    """Nenhuma regra nova é inventada sobre esse caso: criação vence."""
    assert decidir_marco(criacao=True, decisoes=()) is CICLO


# --------------------------------------------------------------------------
# D–G. Atendimento existente sem mudança — N-a-T6
# --------------------------------------------------------------------------


def test_existente_sem_decisoes_preserva_o_marco() -> None:
    assert decidir_marco(criacao=False, decisoes=()) is MARCO_ANTERIOR


def test_existente_sem_decisoes_com_marco_none_devolve_none() -> None:
    assert decidir_marco(criacao=False, decisoes=(), marco=None) is None


def test_existente_com_uma_decisao_vazia_preserva_o_marco() -> None:
    assert decidir_marco(criacao=False, decisoes=(decisao_vazia(),)) is MARCO_ANTERIOR


def test_t33_real_preserva_o_estado_e_portanto_preserva_o_marco() -> None:
    """G — decisão vinda da `MaquinaEstados` REAL, não fabricada."""
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO, (Evento.E01,), INCOMPLETOS, SEM_CONDICOES
    )

    assert decisao.caminho == (Transicao.T33,)
    assert decisao.transicoes_que_mudaram_estado == ()
    assert decidir_marco(criacao=False, decisoes=(decisao,)) is MARCO_ANTERIOR


# --------------------------------------------------------------------------
# H–L. Atendimento existente com mudança — N-a-T4/T5/T7
# --------------------------------------------------------------------------


def test_existente_com_uma_decisao_com_mudanca_atualiza() -> None:
    assert decidir_marco(criacao=False, decisoes=(decisao_com_mudanca(),)) is CICLO


def test_duas_decisoes_vazia_depois_com_mudanca_atualiza() -> None:
    decisoes = (decisao_vazia(), decisao_com_mudanca())

    assert decidir_marco(criacao=False, decisoes=decisoes) is CICLO


def test_duas_decisoes_com_mudanca_depois_vazia_atualiza() -> None:
    decisoes = (decisao_com_mudanca(), decisao_vazia())

    assert decidir_marco(criacao=False, decisoes=decisoes) is CICLO


def test_tres_decisoes_todas_vazias_preservam_o_marco() -> None:
    decisoes = (decisao_vazia(), decisao_vazia(), decisao_vazia())

    assert decidir_marco(criacao=False, decisoes=decisoes) is MARCO_ANTERIOR


@pytest.mark.parametrize("posicao", [0, 1, 2])
def test_tres_decisoes_com_ao_menos_uma_mudanca_atualizam(posicao: int) -> None:
    decisoes = [decisao_vazia(), decisao_vazia(), decisao_vazia()]
    decisoes[posicao] = decisao_com_mudanca()

    assert decidir_marco(criacao=False, decisoes=tuple(decisoes)) is CICLO


# --------------------------------------------------------------------------
# M–N. Ciclo que muda e volta ao mesmo estado — N-a-T5 e N-a-T7
# --------------------------------------------------------------------------


def test_encerrado_reaberto_e_encerrado_atualiza_mesmo_com_estado_final_igual() -> None:
    """M — `encerrado` → T36 → T35 → `encerrado`, pela máquina REAL."""
    decisao = decidir(
        Estado.ENCERRADO,
        (Evento.E01, Evento.E14),
        INCOMPLETOS,
        CondicoesCiclo(
            identidade=Identidade.MESMA_SOLICITACAO,
            motivo_encerramento=MotivoEncerramento.SEM_INTERESSE,
        ),
    )

    assert decisao.estado_final is Estado.ENCERRADO
    assert decisao.transicoes_que_mudaram_estado == (Transicao.T36, Transicao.T35)
    assert decidir_marco(criacao=False, decisoes=(decisao,)) is CICLO


def test_multiplas_mudancas_produzem_um_unico_instante() -> None:
    """N — a cardinalidade da projeção não vira um marco por transição."""
    muitas = DecisaoMaquina(
        estado_final=Estado.ENCERRADO,
        caminho=(Transicao.T36, Transicao.T35),
        transicoes_que_mudaram_estado=(Transicao.T36, Transicao.T35),
    )

    assert decidir_marco(criacao=False, decisoes=(muitas, decisao_com_mudanca())) is CICLO


# --------------------------------------------------------------------------
# O–P. Identidade dos objetos: zero conversão, zero recriação
# --------------------------------------------------------------------------


def test_instante_com_fuso_nao_utc_e_devolvido_por_identidade() -> None:
    outro_fuso = datetime(
        2000, 6, 15, 9, 0, 0, tzinfo=timezone(timedelta(hours=-3))
    )

    resultado = decidir_marco(
        criacao=True, decisoes=(), marco=None, ciclo=outro_fuso
    )

    assert resultado is outro_fuso
    assert resultado.tzinfo is outro_fuso.tzinfo
    assert resultado.utcoffset() == timedelta(hours=-3)


def test_marco_preservado_e_devolvido_por_identidade() -> None:
    marco = datetime(1999, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=5, minutes=30)))

    resultado = decidir_marco(criacao=False, decisoes=(), marco=marco)

    assert resultado is marco
    assert resultado.tzinfo is marco.tzinfo


# --------------------------------------------------------------------------
# Q–R. Contrato de erros
# --------------------------------------------------------------------------


def test_mais_de_tres_decisoes_e_erro_de_contrato() -> None:
    decisoes = (decisao_vazia(),) * 4

    with pytest.raises(ValueError):
        decidir_marco(criacao=False, decisoes=decisoes)


@pytest.mark.parametrize(
    ("criacao", "ciclo", "marco", "decisoes"),
    [
        ("sim", CICLO, MARCO_ANTERIOR, ()),
        (1, CICLO, MARCO_ANTERIOR, ()),
        (False, "2000-06-15", MARCO_ANTERIOR, ()),
        (False, None, MARCO_ANTERIOR, ()),
        (False, CICLO, "2000-06-01", ()),
        (False, CICLO, MARCO_ANTERIOR, None),
        (False, CICLO, MARCO_ANTERIOR, decisao_vazia()),
        (False, CICLO, MARCO_ANTERIOR, (decisao_vazia(), "outra")),
    ],
)
def test_tipos_invalidos_sao_erro_de_tipo(
    criacao: object, ciclo: object, marco: object, decisoes: object
) -> None:
    with pytest.raises(TypeError):
        decidir_instante_ultima_transicao(
            criacao_de_atendimento=criacao,  # type: ignore[arg-type]
            instante_de_referencia_do_ciclo=ciclo,  # type: ignore[arg-type]
            marco_atual=marco,  # type: ignore[arg-type]
            decisoes_do_ciclo=decisoes,  # type: ignore[arg-type]
        )


# --------------------------------------------------------------------------
# S–U. Fronteiras do módulo, provadas sobre o código
# --------------------------------------------------------------------------


def _arvore() -> ast.Module:
    return ast.parse(MODULO.read_text(encoding="utf-8"))


def _modulos_importados() -> set[str]:
    importados = set()
    for no in ast.walk(_arvore()):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)
    return importados


def _identificadores() -> set[str]:
    nomes = set()
    for no in ast.walk(_arvore()):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
        elif isinstance(no, ast.arg):
            nomes.add(no.arg)
        elif isinstance(no, (ast.FunctionDef, ast.ClassDef)):
            nomes.add(no.name)
        elif isinstance(no, ast.keyword) and no.arg:
            nomes.add(no.arg)
    return nomes


def test_modulo_nao_consulta_relogio_vivo() -> None:
    """S — zero relógio vivo e zero aritmética temporal."""
    proibidos = {
        "now",
        "utcnow",
        "today",
        "fromtimestamp",
        "monotonic",
        "time",
        "timestamp",
        "astimezone",
        "replace",
    }

    assert not (_identificadores() & proibidos)


def test_modulo_importa_exatamente_os_modulos_autorizados() -> None:
    """T — nenhuma importação de persistência, contexto, elegibilidade ou identidade."""
    assert _modulos_importados() == {
        "__future__",
        "collections.abc",
        "datetime",
        "casa77_sdr.state_machine",
    }


def test_modulo_nao_importa_fronteiras_proibidas() -> None:
    proibidos = {
        "casa77_sdr.persistence",
        "casa77_sdr.context",
        "casa77_sdr.eligibility",
        "casa77_sdr.identity",
        "casa77_sdr.knowledge",
        "casa77_sdr.normalization",
        "casa77_sdr.qualification",
        "casa77_sdr.rules",
        "os",
        "io",
        "pathlib",
        "socket",
        "http",
        "urllib",
        "requests",
        "sqlite3",
        "json",
        "yaml",
    }

    assert not (_modulos_importados() & proibidos)


def test_modulo_nao_persiste_nem_orquestra() -> None:
    proibidos = {
        "criar",
        "gravar",
        "marcar_chave_processada",
        "preservar_pendente",
        "RegistroAtendimento",
        "PersistenciaOperacional",
        "FalhaDePersistencia",
        "OrquestradorMotor",
        "replace",
        "decidir",
        "resolver_identidade",
    }

    assert not (_identificadores() & proibidos)


def test_modulo_le_apenas_o_campo_da_projecao_de_decisaomaquina() -> None:
    """U — nenhum outro campo de `DecisaoMaquina` é consultado."""
    outros_campos = {
        "estado_final",
        "caminho",
        "acoes",
        "efeitos",
        "inercias",
        "eventos_consumidos",
        "motivos_handoff",
        "motivo_encerramento",
    }

    identificadores = _identificadores()
    assert "transicoes_que_mudaram_estado" in identificadores
    assert not (identificadores & outros_campos)


def test_modulo_nao_compara_estado_inicial_com_estado_final() -> None:
    proibidos = {"estado_inicial", "max", "min"}

    assert not (_identificadores() & proibidos)


# --------------------------------------------------------------------------
# V–W. Determinismo e contrato da assinatura
# --------------------------------------------------------------------------


def test_duas_chamadas_com_as_mesmas_entradas_produzem_a_mesma_saida() -> None:
    decisoes = (decisao_vazia(), decisao_com_mudanca())

    primeiro = decidir_marco(criacao=False, decisoes=decisoes)
    segundo = decidir_marco(criacao=False, decisoes=decisoes)

    assert primeiro is segundo is CICLO


def test_assinatura_e_keyword_only_sem_defaults() -> None:
    """W — os quatro argumentos são obrigatórios e nomeados."""
    parametros = inspect.signature(decidir_instante_ultima_transicao).parameters

    assert list(parametros) == [
        "criacao_de_atendimento",
        "instante_de_referencia_do_ciclo",
        "marco_atual",
        "decisoes_do_ciclo",
    ]
    for parametro in parametros.values():
        assert parametro.kind is inspect.Parameter.KEYWORD_ONLY
        assert parametro.default is inspect.Parameter.empty
