"""Testes do `DetectorHandoff` — produtor determinístico de `E18` e motivos.

Cobre o contrato vivo de `docs/07-arquitetura-motor-respostas.md` §6.3
(`DH-1`–`DH-12`) e a extensão semântica **AJ4**: as dez famílias de gatilho, a
regra "`ALTA` confirma; `BAIXA` não confirma" com a **única exceção** de
`pedido_de_humano`, a multiplicidade sem precedência, os invariantes do DTO, a
reutilização da validação de canonicidade da fronteira N-b e a pureza.

`docs/04-handoff-humano.md` é a **autoridade dos gatilhos** e permanece
**inalterado**: aqui nenhum gatilho é criado, removido ou reinterpretado.
`src/casa77_sdr/state_machine.py` permanece **inalterado** e continua a autoridade
da sua própria fronteira.

Todas as fixtures são **fictícias e genéricas**: zero PII, zero conversa real,
zero valor comercial. Nenhum teste lê YAML, `knowledge/**`, rede ou credencial.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import itertools
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import handoff_detection
from casa77_sdr.handoff_detection import (
    DeteccaoHandoff,
    MotivoHandoff,
    detectar_handoff,
)
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    AssuntoComercial,
    DadosExtraidos,
    EntradaInterpretacao,
    IntencaoAutonomaRecebida,
    IntencaoConversacional,
    IntencaoDetectada,
    Interpretacao,
    PerguntaComercial,
    canonicalizar_interpretacao,
)
from casa77_sdr.state_machine import Evento

MODULO_DETECTOR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "casa77_sdr"
    / "handoff_detection.py"
)

ALTA = Confianca.ALTA
BAIXA = Confianca.BAIXA

#: Os **oito** sinais de handoff acrescentados ao grupo **A2** por **AJ4**,
#: emparelhados ao motivo que cada um produz.
MOTIVO_POR_SINAL_AJ4: dict[IntencaoConversacional, MotivoHandoff] = {
    IntencaoConversacional.PEDIDO_DE_CONDICAO_ESPECIAL: MotivoHandoff.PEDIDO_DESCONTO,
    IntencaoConversacional.PEDIDO_DE_CONFIRMACAO_DE_VISITA: (
        MotivoHandoff.CONFIRMACAO_VISITA
    ),
    IntencaoConversacional.PEDIDO_DE_RESERVA: MotivoHandoff.CONFIRMACAO_RESERVA,
    IntencaoConversacional.INTENCAO_DE_CONTRATAR: MotivoHandoff.CONTRATACAO,
    IntencaoConversacional.PEDIDO_DE_CANCELAMENTO: MotivoHandoff.CANCELAMENTO,
    IntencaoConversacional.PEDIDO_DE_ALTERACAO_DE_DATA: MotivoHandoff.ALTERACAO_DATA,
    IntencaoConversacional.ASSUNTO_JURIDICO_OU_CONTRATUAL: (
        MotivoHandoff.INTERPRETACAO_CONTRATUAL
    ),
    IntencaoConversacional.RECLAMACAO_OU_TOM_HOSTIL: (
        MotivoHandoff.RECLAMACAO_OU_TOM_HOSTIL
    ),
}

SINAIS_AJ4 = tuple(MOTIVO_POR_SINAL_AJ4)

#: Os **nove** códigos autônomos que exigem `ALTA` — os oito de AJ4 mais a
#: `EXCECAO_SOLICITADA` já vigente.
MOTIVO_POR_CODIGO_ALTA: dict[IntencaoConversacional, MotivoHandoff] = {
    IntencaoConversacional.EXCECAO_SOLICITADA: MotivoHandoff.EXCECAO_SOLICITADA,
    **MOTIVO_POR_SINAL_AJ4,
}

CODIGOS_ALTA = tuple(MOTIVO_POR_CODIGO_ALTA)

#: Ordem canônica esperada, reescrita **independentemente** do módulo sob teste.
ORDEM_CANONICA = (
    MotivoHandoff.PEDIDO_HUMANO,
    MotivoHandoff.EXCECAO_SOLICITADA,
    MotivoHandoff.PEDIDO_DESCONTO,
    MotivoHandoff.CONFIRMACAO_VISITA,
    MotivoHandoff.CONFIRMACAO_RESERVA,
    MotivoHandoff.CONTRATACAO,
    MotivoHandoff.CANCELAMENTO,
    MotivoHandoff.ALTERACAO_DATA,
    MotivoHandoff.INTERPRETACAO_CONTRATUAL,
    MotivoHandoff.RECLAMACAO_OU_TOM_HOSTIL,
)


# --------------------------------------------------------------------------
# Fixtures genéricas
# --------------------------------------------------------------------------


def entrada(**ajustes: Any) -> EntradaInterpretacao:
    base: dict[str, Any] = {
        "dados_extraidos": DadosExtraidos(),
        "correcoes": (),
        "perguntas_comerciais": (),
        "pedido_de_humano": False,
        "confianca_pedido_de_humano": None,
        "referencias_evento_anterior": (),
        "trechos_ambiguos": (),
        "confianca_global": ALTA,
        "intencoes_autonomas": (),
    }
    base.update(ajustes)
    return EntradaInterpretacao(**base)  # type: ignore[arg-type]


def interpretacao(**ajustes: Any) -> Interpretacao:
    """Sempre canônica: passa pela fronteira determinística de N-b."""
    return canonicalizar_interpretacao(entrada(**ajustes))


def com_sinais(*pares: tuple[IntencaoConversacional, Confianca]) -> Interpretacao:
    return interpretacao(
        intencoes_autonomas=tuple(
            IntencaoAutonomaRecebida(codigo=codigo, confianca=confianca)
            for codigo, confianca in pares
        )
    )


def com_humano(confianca: Confianca) -> Interpretacao:
    return interpretacao(pedido_de_humano=True, confianca_pedido_de_humano=confianca)


# --------------------------------------------------------------------------
# A. Vocabulário fechado de motivos
# --------------------------------------------------------------------------


def test_o_vocabulario_de_motivo_tem_exatamente_dez_membros() -> None:
    assert len(list(MotivoHandoff)) == 10
    assert tuple(MotivoHandoff) == ORDEM_CANONICA


def test_os_valores_correspondem_aos_motivos_do_doc_06() -> None:
    """`docs/06` §2.1 é a autoridade do vocabulário; nada é inventado."""
    assert {motivo.value for motivo in MotivoHandoff} == {
        "pedido_humano",
        "excecao_solicitada",
        "pedido_desconto",
        "confirmacao_visita",
        "confirmacao_reserva",
        "contratacao",
        "cancelamento",
        "alteracao_data",
        "interpretacao_contratual",
        "reclamacao_ou_tom_hostil",
    }


def test_informacao_pendente_nao_pertence_ao_detector() -> None:
    """Gatilhos 1–2 chegam como `E09` e não são reemitidos (`docs/06` §9)."""
    assert "informacao_pendente" not in {motivo.value for motivo in MotivoHandoff}


def test_nao_existe_decimo_primeiro_motivo() -> None:
    with pytest.raises(ValueError):
        MotivoHandoff("motivo_inexistente")


# --------------------------------------------------------------------------
# B. Os dez gatilhos isoladamente
# --------------------------------------------------------------------------


@pytest.mark.parametrize("confianca", [ALTA, BAIXA], ids=lambda c: c.value)
def test_pedido_de_humano_confirma_em_alta_e_em_baixa(confianca: Confianca) -> None:
    """Exceção única vigente de N-b-PH3 — e ela não se estende por analogia."""
    resultado = detectar_handoff(com_humano(confianca))
    assert resultado == DeteccaoHandoff(
        evento=Evento.E18, motivos=(MotivoHandoff.PEDIDO_HUMANO,)
    )


@pytest.mark.parametrize(
    ("codigo", "motivo"), list(MOTIVO_POR_CODIGO_ALTA.items()), ids=lambda x: str(x)
)
def test_cada_codigo_alta_produz_o_seu_motivo(
    codigo: IntencaoConversacional, motivo: MotivoHandoff
) -> None:
    resultado = detectar_handoff(com_sinais((codigo, ALTA)))
    assert resultado == DeteccaoHandoff(evento=Evento.E18, motivos=(motivo,))


@pytest.mark.parametrize("codigo", CODIGOS_ALTA, ids=lambda c: c.value)
def test_cada_codigo_baixa_nao_confirma(codigo: IntencaoConversacional) -> None:
    assert detectar_handoff(com_sinais((codigo, BAIXA))) is None


def test_as_dez_familias_sao_cobertas_e_sao_exatamente_dez() -> None:
    produzidos = {detectar_handoff(com_humano(ALTA)).motivos[0]}  # type: ignore[union-attr]
    for codigo in CODIGOS_ALTA:
        produzidos.add(detectar_handoff(com_sinais((codigo, ALTA))).motivos[0])  # type: ignore[union-attr]
    assert produzidos == set(MotivoHandoff)
    assert len(produzidos) == 10


# --------------------------------------------------------------------------
# C. Ausência e totalidade
# --------------------------------------------------------------------------


def test_interpretacao_vazia_devolve_none() -> None:
    assert detectar_handoff(interpretacao()) is None


def test_pedido_de_humano_falso_nao_confirma() -> None:
    assert detectar_handoff(interpretacao(pedido_de_humano=False)) is None


def test_sinais_alheios_ao_handoff_nao_confirmam() -> None:
    """Dados, perguntas e os demais autônomos não são gatilho desta fronteira."""
    alvo = interpretacao(
        dados_extraidos=DadosExtraidos(
            tipo_evento="festa fictícia",
            confianca_tipo_evento=ALTA,
            convidados=60,
            confianca_convidados=ALTA,
        ),
        perguntas_comerciais=(
            PerguntaComercial(
                texto="quanto custa?",
                confianca=ALTA,
                assunto=AssuntoComercial.PRECO_LOCACAO,
            ),
        ),
        intencoes_autonomas=(
            IntencaoAutonomaRecebida(
                codigo=IntencaoConversacional.INTERESSE_EM_VISITA, confianca=ALTA
            ),
            IntencaoAutonomaRecebida(
                codigo=IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE,
                confianca=ALTA,
            ),
        ),
    )
    assert detectar_handoff(alvo) is None


def test_interesse_simples_em_visita_nao_e_handoff() -> None:
    """Gatilho 4 de `docs/04`: interesse simples segue `E10`/T16, não `E18`."""
    assert (
        detectar_handoff(
            com_sinais((IntencaoConversacional.INTERESSE_EM_VISITA, ALTA))
        )
        is None
    )


def test_interesse_confirmar_disponibilidade_nao_e_handoff() -> None:
    """Disponibilidade fica nas condições 5/6 e em T14/T15/T25 — fora do detector."""
    assert (
        detectar_handoff(
            com_sinais(
                (IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA)
            )
        )
        is None
    )


@pytest.mark.parametrize(
    "codigo",
    [
        IntencaoConversacional.DESINTERESSE_DECLARADO,
        IntencaoConversacional.CONTATO_POR_ENGANO,
        IntencaoConversacional.MENSAGEM_NAO_SOLICITADA,
        IntencaoConversacional.ACEITACAO_DE_INCOMPATIBILIDADE,
    ],
    ids=lambda c: c.value,
)
def test_sinais_de_encerramento_nao_sao_handoff(
    codigo: IntencaoConversacional,
) -> None:
    """Os quatro sinais de **AJ3** pertencem a S3-D1, não a esta fronteira."""
    assert detectar_handoff(com_sinais((codigo, ALTA))) is None


# --------------------------------------------------------------------------
# D. Multiplicidade, deduplicação e ordem canônica
# --------------------------------------------------------------------------


def test_pedido_humano_mais_cancelamento_produz_dois_motivos() -> None:
    alvo = interpretacao(
        pedido_de_humano=True,
        confianca_pedido_de_humano=ALTA,
        intencoes_autonomas=(
            IntencaoAutonomaRecebida(
                codigo=IntencaoConversacional.PEDIDO_DE_CANCELAMENTO, confianca=ALTA
            ),
        ),
    )
    resultado = detectar_handoff(alvo)
    assert resultado is not None
    assert resultado.evento is Evento.E18
    assert resultado.motivos == (
        MotivoHandoff.PEDIDO_HUMANO,
        MotivoHandoff.CANCELAMENTO,
    )


def test_todos_os_dez_gatilhos_juntos_produzem_um_unico_e18() -> None:
    alvo = interpretacao(
        pedido_de_humano=True,
        confianca_pedido_de_humano=ALTA,
        intencoes_autonomas=tuple(
            IntencaoAutonomaRecebida(codigo=codigo, confianca=ALTA)
            for codigo in CODIGOS_ALTA
        ),
    )
    resultado = detectar_handoff(alvo)
    assert resultado is not None
    assert resultado.evento is Evento.E18
    assert resultado.motivos == ORDEM_CANONICA
    assert len(resultado.motivos) == 10


@pytest.mark.parametrize(
    "par", list(itertools.combinations(CODIGOS_ALTA, 2)), ids=lambda p: "+".join(c.value for c in p)
)
def test_cada_par_produz_um_e18_com_dois_motivos(
    par: tuple[IntencaoConversacional, ...]
) -> None:
    resultado = detectar_handoff(com_sinais(*((c, ALTA) for c in par)))
    assert resultado is not None
    assert resultado.evento is Evento.E18
    assert set(resultado.motivos) == {MOTIVO_POR_CODIGO_ALTA[c] for c in par}
    assert len(resultado.motivos) == 2


def test_a_saida_esta_sempre_em_ordem_canonica_e_sem_duplicata() -> None:
    posicao = {motivo: i for i, motivo in enumerate(ORDEM_CANONICA)}
    for tamanho in (1, 2, 3, 9):
        for grupo in itertools.combinations(CODIGOS_ALTA, tamanho):
            resultado = detectar_handoff(com_sinais(*((c, ALTA) for c in grupo)))
            assert resultado is not None
            motivos = list(resultado.motivos)
            assert motivos == sorted(motivos, key=lambda m: posicao[m])
            assert len(motivos) == len(set(motivos))


def test_a_ordem_da_entrada_nao_altera_a_saida() -> None:
    direto = com_sinais(*((c, ALTA) for c in CODIGOS_ALTA))
    invertido = com_sinais(*((c, ALTA) for c in reversed(CODIGOS_ALTA)))
    assert detectar_handoff(direto) == detectar_handoff(invertido)


def test_baixa_nao_impede_que_outro_alta_confirme() -> None:
    resultado = detectar_handoff(
        com_sinais(
            (IntencaoConversacional.PEDIDO_DE_RESERVA, ALTA),
            (IntencaoConversacional.PEDIDO_DE_CANCELAMENTO, BAIXA),
        )
    )
    assert resultado is not None
    assert resultado.motivos == (MotivoHandoff.CONFIRMACAO_RESERVA,)


def test_nao_existe_motivo_principal_nem_precedencia() -> None:
    """Todo motivo reconhecido aparece; nenhum derrota outro."""
    for grupo in itertools.combinations(CODIGOS_ALTA, 3):
        resultado = detectar_handoff(com_sinais(*((c, ALTA) for c in grupo)))
        assert resultado is not None
        assert set(resultado.motivos) == {MOTIVO_POR_CODIGO_ALTA[c] for c in grupo}


def test_juridico_coexiste_com_pergunta_comercial() -> None:
    """Gatilho 8 vale **inclusive em forma de pergunta** (`docs/04`)."""
    alvo = interpretacao(
        perguntas_comerciais=(
            PerguntaComercial(
                texto="e se houver multa?",
                confianca=ALTA,
                assunto=AssuntoComercial.MULTAS_E_PENALIDADES,
            ),
        ),
        intencoes_autonomas=(
            IntencaoAutonomaRecebida(
                codigo=IntencaoConversacional.ASSUNTO_JURIDICO_OU_CONTRATUAL,
                confianca=ALTA,
            ),
        ),
    )
    resultado = detectar_handoff(alvo)
    assert resultado is not None
    assert resultado.motivos == (MotivoHandoff.INTERPRETACAO_CONTRATUAL,)
    # A pergunta comercial segue o seu próprio caminho e não é suprimida.
    assert IntencaoConversacional.PERGUNTA_COMERCIAL in {
        item.codigo for item in alvo.intencoes_detectadas
    }


# --------------------------------------------------------------------------
# E. Invariantes de `DeteccaoHandoff`
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "evento", [e for e in Evento if e is not Evento.E18], ids=lambda e: e.value
)
def test_dto_rejeita_evento_diferente_de_e18(evento: Evento) -> None:
    with pytest.raises(ValueError):
        DeteccaoHandoff(evento=evento, motivos=(MotivoHandoff.PEDIDO_HUMANO,))


def test_dto_rejeita_motivos_vazios() -> None:
    with pytest.raises(ValueError):
        DeteccaoHandoff(evento=Evento.E18, motivos=())


def test_dto_rejeita_duplicata() -> None:
    with pytest.raises(ValueError):
        DeteccaoHandoff(
            evento=Evento.E18,
            motivos=(MotivoHandoff.CANCELAMENTO, MotivoHandoff.CANCELAMENTO),
        )


def test_dto_rejeita_ordem_nao_canonica() -> None:
    with pytest.raises(ValueError):
        DeteccaoHandoff(
            evento=Evento.E18,
            motivos=(MotivoHandoff.CANCELAMENTO, MotivoHandoff.PEDIDO_HUMANO),
        )


@pytest.mark.parametrize("valor", [None, "E18", 18, object()], ids=repr)
def test_dto_rejeita_evento_de_tipo_errado(valor: Any) -> None:
    with pytest.raises(TypeError):
        DeteccaoHandoff(evento=valor, motivos=(MotivoHandoff.PEDIDO_HUMANO,))


@pytest.mark.parametrize(
    "valor",
    [None, "pedido_humano", [MotivoHandoff.PEDIDO_HUMANO], ("pedido_humano",), (1,)],
    ids=repr,
)
def test_dto_rejeita_motivos_de_tipo_errado(valor: Any) -> None:
    with pytest.raises(TypeError):
        DeteccaoHandoff(evento=Evento.E18, motivos=valor)


def test_dto_tem_dois_campos_e_e_imutavel() -> None:
    assert [c.name for c in dataclasses.fields(DeteccaoHandoff)] == [
        "evento",
        "motivos",
    ]
    alvo = DeteccaoHandoff(evento=Evento.E18, motivos=(MotivoHandoff.CONTRATACAO,))
    with pytest.raises(dataclasses.FrozenInstanceError):
        alvo.motivos = ()  # type: ignore[misc]


def test_todo_e18_produzido_carrega_ao_menos_um_motivo() -> None:
    for codigo in CODIGOS_ALTA:
        resultado = detectar_handoff(com_sinais((codigo, ALTA)))
        assert resultado is not None
        assert resultado.evento is Evento.E18
        assert len(resultado.motivos) >= 1


# --------------------------------------------------------------------------
# F. Validação e erros
# --------------------------------------------------------------------------


def test_none_e_type_error() -> None:
    with pytest.raises(TypeError):
        detectar_handoff(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "valor", ["texto", 1, 1.5, True, (), [], {}, object()], ids=repr
)
def test_tipo_errado_de_interpretacao_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        detectar_handoff(valor)  # type: ignore[arg-type]


def test_interpretacao_construida_diretamente_mas_invalida_e_bloqueada() -> None:
    """`isinstance` prova o tipo, não a validade."""
    invalida = Interpretacao(
        intencoes_detectadas=(
            IntencaoDetectada(
                codigo=IntencaoConversacional.PEDIDO_DE_RESERVA, confianca=ALTA
            ),
        ),
        dados_extraidos=DadosExtraidos(tipo_evento="festa fictícia"),
        correcoes=(),
        perguntas_comerciais=(),
        pedido_de_humano=False,
        confianca_pedido_de_humano=None,
        referencias_evento_anterior=(),
        confianca_global=ALTA,
        trechos_ambiguos=(),
    )
    with pytest.raises(ValueError, match="E-Nb-1"):
        detectar_handoff(invalida)


def test_entrada_invalida_nao_produz_saida_parcial() -> None:
    invalida = Interpretacao(
        intencoes_detectadas=(
            IntencaoDetectada(
                codigo=IntencaoConversacional.PEDIDO_DE_CANCELAMENTO, confianca=ALTA
            ),
        ),
        dados_extraidos=DadosExtraidos(),
        correcoes=(),
        perguntas_comerciais=(),
        pedido_de_humano=False,
        confianca_pedido_de_humano=None,
        referencias_evento_anterior=(),
        confianca_global=None,  # type: ignore[arg-type]
        trechos_ambiguos=(),
    )
    with pytest.raises(ValueError, match="E-Nb-4"):
        detectar_handoff(invalida)


def test_a_validacao_canonica_e_reutilizada_e_nao_duplicada() -> None:
    """A fronteira **importa** o validador existente — não o reescreve."""
    arvore = ast.parse(MODULO_DETECTOR.read_text(encoding="utf-8"))
    importados = {
        alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module == "casa77_sdr.interpretation"
        for alias in no.names
    }
    assert "_validar_interpretacao_canonica" in importados

    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }
    assert "_validar_interpretacao_canonica" in chamadas

    definidas = {no.name for no in ast.walk(arvore) if isinstance(no, ast.FunctionDef)}
    assert definidas == {"detectar_handoff", "__post_init__"}


# --------------------------------------------------------------------------
# G. Pureza e fronteira do módulo
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
    assert modulos_importados(MODULO_DETECTOR) <= {
        "__future__",
        "dataclasses",
        "enum",
        "casa77_sdr",
    }

    arvore = ast.parse(MODULO_DETECTOR.read_text(encoding="utf-8"))
    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert submodulos == {
        "__future__",
        "dataclasses",
        "enum",
        "casa77_sdr.identity",
        "casa77_sdr.interpretation",
        "casa77_sdr.state_machine",
    }
    for proibido in (
        "casa77_sdr.qualification",
        "casa77_sdr.closure_decision",
        "casa77_sdr.interpretation_events",
        "casa77_sdr.interpretation_llm",
        "casa77_sdr.interpretation_anthropic",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.knowledge",
        "casa77_sdr.persistence",
        "casa77_sdr.context",
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
        "compile",
        "search",
        "match",
    } == set()


def test_a_superficie_publica_e_fechada_em_tres_nomes() -> None:
    assert handoff_detection.__all__ == [
        "MotivoHandoff",
        "DeteccaoHandoff",
        "detectar_handoff",
    ]


def test_a_fronteira_nao_e_exportada_pelo_pacote() -> None:
    """M-NB1 preservado: nada desta fronteira sai pelo `__init__.py`."""
    import casa77_sdr

    for nome in ("MotivoHandoff", "DeteccaoHandoff", "detectar_handoff"):
        assert nome not in casa77_sdr.__all__
        assert not hasattr(casa77_sdr, nome)


def test_nenhuma_excecao_publica_nova_e_criada() -> None:
    arvore = ast.parse(MODULO_DETECTOR.read_text(encoding="utf-8"))
    classes = [no for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)]
    assert [no.name for no in classes] == ["MotivoHandoff", "DeteccaoHandoff"]
    # `MotivoHandoff` herda `StrEnum`; `DeteccaoHandoff` não herda de nada.
    assert [b.id for b in classes[0].bases if isinstance(b, ast.Name)] == ["StrEnum"]
    assert classes[1].bases == []


def test_a_assinatura_recebe_somente_a_interpretacao() -> None:
    parametros = inspect.signature(detectar_handoff).parameters
    assert list(parametros) == ["interpretacao"]
    anotacao = str(parametros["interpretacao"].annotation)
    for proibido in (
        "Qualificacao",
        "ResultadoQualificacao",
        "Estado",
        "SituacaoTakeover",
        "CondicoesCiclo",
        "dict",
        "str",
    ):
        assert proibido not in anotacao


def test_o_detector_nao_constroi_condicoes_ciclo() -> None:
    """§17 do contrato: projetar os motivos é papel do `OrquestradorMotor`."""
    corpo = MODULO_DETECTOR.read_text(encoding="utf-8").split('"""', 2)[2]
    assert "CondicoesCiclo" not in corpo
    assert "motivos_handoff" not in corpo


def test_a_funcao_nao_le_texto_para_decidir() -> None:
    """A decisão vem só do booleano, dos códigos e da confiança."""
    fonte = MODULO_DETECTOR.read_text(encoding="utf-8")
    corpo = fonte.split('"""', 2)[2]
    arvore = ast.parse(fonte)
    alvo = next(
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef) and no.name == "detectar_handoff"
    )
    atributos = {no.attr for no in ast.walk(alvo) if isinstance(no, ast.Attribute)}
    assert atributos == {
        "pedido_de_humano",
        "intencoes_detectadas",
        "codigo",
        "confianca",
        "ALTA",
        "E18",
        "PEDIDO_HUMANO",
        "add",
        "get",
    }
    for proibido in (
        "texto",
        "dados_extraidos",
        "perguntas_comerciais",
        "trechos_ambiguos",
        "referencias_evento_anterior",
        "correcoes",
        "confianca_global",
    ):
        assert proibido not in atributos
    # Nenhuma palavra-chave, regex, score ou contador semântico no módulo.
    for proibido in ("import re", "re.", "score", "sentiment", "lower()", "strip()"):
        assert proibido not in corpo


def test_a_entrada_nao_e_mutada() -> None:
    alvo = interpretacao(
        pedido_de_humano=True,
        confianca_pedido_de_humano=ALTA,
        intencoes_autonomas=tuple(
            IntencaoAutonomaRecebida(codigo=codigo, confianca=ALTA)
            for codigo in CODIGOS_ALTA
        ),
    )
    antes = (
        alvo.intencoes_detectadas,
        alvo.pedido_de_humano,
        alvo.dados_extraidos,
        alvo.confianca_global,
    )
    detectar_handoff(alvo)
    assert (
        alvo.intencoes_detectadas,
        alvo.pedido_de_humano,
        alvo.dados_extraidos,
        alvo.confianca_global,
    ) == antes


def test_a_funcao_e_deterministica() -> None:
    alvo = com_sinais((IntencaoConversacional.INTENCAO_DE_CONTRATAR, ALTA))
    assert len({detectar_handoff(alvo) for _ in range(5)}) == 1


def test_a_saida_e_sempre_deteccao_ou_none() -> None:
    for codigo in CODIGOS_ALTA:
        for confianca in (ALTA, BAIXA):
            saida = detectar_handoff(com_sinais((codigo, confianca)))
            assert saida is None or isinstance(saida, DeteccaoHandoff)


def test_a_projecao_futura_para_a_maquina_e_tupla_de_str() -> None:
    """§17: a máquina continua recebendo `tuple[str, ...]`, montada a jusante."""
    resultado = detectar_handoff(
        com_sinais(
            (IntencaoConversacional.PEDIDO_DE_CANCELAMENTO, ALTA),
            (IntencaoConversacional.PEDIDO_DE_RESERVA, ALTA),
        )
    )
    assert resultado is not None
    projetado = tuple(motivo.value for motivo in resultado.motivos)
    assert projetado == ("confirmacao_reserva", "cancelamento")
    assert all(isinstance(item, str) for item in projetado)


def test_a_etapa_4_continua_sem_produzir_e18() -> None:
    """A etapa 4 relata o sinal; quem emite `E18` é esta fronteira."""
    modulo = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "casa77_sdr"
        / "interpretation.py"
    )
    arvore = ast.parse(modulo.read_text(encoding="utf-8"))
    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert "casa77_sdr.state_machine" not in submodulos

    nomes = {no.id for no in ast.walk(arvore) if isinstance(no, ast.Name)}
    nomes |= {no.attr for no in ast.walk(arvore) if isinstance(no, ast.Attribute)}
    for proibido in ("Evento", "E18", "MotivoHandoff", "motivos_handoff"):
        assert proibido not in nomes
