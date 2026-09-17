"""Testes do produtor determinístico de `E14` e do motivo de encerramento.

Cobre o contrato vivo de `docs/07-arquitetura-motor-respostas.md` §6.3
(`S3D1-1`–`S3D1-12`) e a extensão semântica **AJ3**: o mapeamento fechado dos
quatro sinais, a regra de que **somente `ALTA` conta**, a cardinalidade
**fail-closed** do conflito, o *gate* cumulativo da incompatibilidade, a
reutilização da validação de canonicidade da fronteira N-b, a pureza e a
composição com a `MaquinaEstados` vigente.

`src/casa77_sdr/state_machine.py` permanece **inalterado** e continua a
autoridade da sua própria fronteira: aqui ele é apenas **exercitado**, nunca
corrigido.

Todas as fixtures são **fictícias e genéricas**: zero PII, zero conversa real,
zero valor comercial. Nenhum teste lê YAML, `knowledge/**`, rede ou credencial.
"""

from __future__ import annotations

import ast
import dataclasses
import itertools
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import closure_decision
from casa77_sdr.closure_decision import (
    EncerramentoInterpretado,
    decidir_encerramento,
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
from casa77_sdr.qualification import (
    FormatoEvento,
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.state_machine import (
    AcaoMaquina,
    CondicoesCiclo,
    Estado,
    Evento,
    Inercia,
    MotivoEncerramento,
    Transicao,
    decidir,
)

MODULO_S3D1 = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "casa77_sdr"
    / "closure_decision.py"
)

ALTA = Confianca.ALTA
BAIXA = Confianca.BAIXA

DESINTERESSE = IntencaoConversacional.DESINTERESSE_DECLARADO
ENGANO = IntencaoConversacional.CONTATO_POR_ENGANO
SPAM = IntencaoConversacional.MENSAGEM_NAO_SOLICITADA
ACEITACAO = IntencaoConversacional.ACEITACAO_DE_INCOMPATIBILIDADE

#: Os quatro sinais de encerramento de **AJ3**, na ordem documental de A2.
SINAIS = (DESINTERESSE, ENGANO, SPAM, ACEITACAO)

#: Mapeamento esperado, reescrito **independentemente** do módulo sob teste.
MOTIVO_ESPERADO: dict[IntencaoConversacional, MotivoEncerramento] = {
    DESINTERESSE: MotivoEncerramento.SEM_INTERESSE,
    ENGANO: MotivoEncerramento.ENGANO,
    SPAM: MotivoEncerramento.SPAM,
    ACEITACAO: MotivoEncerramento.INCOMPATIBILIDADE_ACEITA,
}

INCOMPATIVEL = ResultadoQualificacao.INCOMPATIVEL

#: Os quatro resultados que **não** abrem o *gate* de `INCOMPATIBILIDADE_ACEITA`.
NAO_INCOMPATIVEIS = tuple(
    resultado for resultado in ResultadoQualificacao if resultado is not INCOMPATIVEL
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


def qualificacao(resultado: ResultadoQualificacao) -> Qualificacao:
    """Só existe para a composição com a máquina — S3-D1 não a recebe."""
    return Qualificacao(
        resultado=resultado,
        motivo=MotivoQualificacao.COMPATIVEL
        if resultado
        in (
            ResultadoQualificacao.QUALIFICADO,
            ResultadoQualificacao.QUALIFICADO_COM_RESSALVA,
        )
        else MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES,
    )


# --------------------------------------------------------------------------
# A. Mapeamento fechado — um único sinal ALTA (S3D1-8)
# --------------------------------------------------------------------------


def test_desinteresse_alta_produz_e14_sem_interesse() -> None:
    resultado = decidir_encerramento(
        com_sinais((DESINTERESSE, ALTA)), ResultadoQualificacao.DADOS_INCOMPLETOS
    )
    assert resultado == EncerramentoInterpretado(
        evento=Evento.E14, motivo=MotivoEncerramento.SEM_INTERESSE
    )


def test_engano_alta_produz_e14_engano() -> None:
    resultado = decidir_encerramento(
        com_sinais((ENGANO, ALTA)), ResultadoQualificacao.DADOS_INCOMPLETOS
    )
    assert resultado == EncerramentoInterpretado(
        evento=Evento.E14, motivo=MotivoEncerramento.ENGANO
    )


def test_spam_alta_produz_e14_spam() -> None:
    resultado = decidir_encerramento(
        com_sinais((SPAM, ALTA)), ResultadoQualificacao.DADOS_INCOMPLETOS
    )
    assert resultado == EncerramentoInterpretado(
        evento=Evento.E14, motivo=MotivoEncerramento.SPAM
    )


def test_aceitacao_alta_com_incompativel_produz_incompatibilidade_aceita() -> None:
    resultado = decidir_encerramento(com_sinais((ACEITACAO, ALTA)), INCOMPATIVEL)
    assert resultado == EncerramentoInterpretado(
        evento=Evento.E14, motivo=MotivoEncerramento.INCOMPATIBILIDADE_ACEITA
    )


@pytest.mark.parametrize("sinal", SINAIS, ids=lambda c: c.value)
def test_o_evento_produzido_e_sempre_e14(sinal: IntencaoConversacional) -> None:
    resultado = decidir_encerramento(com_sinais((sinal, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    assert resultado.evento is Evento.E14
    assert resultado.motivo is MOTIVO_ESPERADO[sinal]


def test_o_mapeamento_e_uma_bijecao_sobre_as_quatro_modalidades() -> None:
    """Nenhuma quinta modalidade, e nenhum motivo sem sinal correspondente."""
    produzidos = {
        decidir_encerramento(com_sinais((sinal, ALTA)), INCOMPATIVEL).motivo  # type: ignore[union-attr]
        for sinal in SINAIS
    }
    assert produzidos == set(MotivoEncerramento)
    assert len(list(MotivoEncerramento)) == 4


# --------------------------------------------------------------------------
# B. `BAIXA` não entra em S (S3D1-6)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("sinal", SINAIS, ids=lambda c: c.value)
def test_sinal_baixa_sozinho_nao_encerra(sinal: IntencaoConversacional) -> None:
    assert decidir_encerramento(com_sinais((sinal, BAIXA)), INCOMPATIVEL) is None


def test_os_quatro_sinais_baixa_juntos_nao_encerram() -> None:
    alvo = com_sinais(*((sinal, BAIXA) for sinal in SINAIS))
    assert decidir_encerramento(alvo, INCOMPATIVEL) is None


@pytest.mark.parametrize(
    ("alta", "baixa"),
    [(a, b) for a in SINAIS for b in SINAIS if a is not b],
    ids=lambda c: c.value,
)
def test_um_alta_mais_outro_baixa_resolve_pela_alta(
    alta: IntencaoConversacional, baixa: IntencaoConversacional
) -> None:
    """`BAIXA` não entra em `S` e **não impede** o único `ALTA` diferente."""
    resultado = decidir_encerramento(com_sinais((alta, ALTA), (baixa, BAIXA)), INCOMPATIVEL)
    assert resultado is not None
    assert resultado.motivo is MOTIVO_ESPERADO[alta]


# --------------------------------------------------------------------------
# C. Cardinalidade fail-closed (S3D1-7)
# --------------------------------------------------------------------------


def test_nenhum_sinal_devolve_none() -> None:
    assert decidir_encerramento(interpretacao(), INCOMPATIVEL) is None


def test_interpretacao_sem_sinal_algum_mas_com_outros_codigos_devolve_none() -> None:
    alvo = interpretacao(
        dados_extraidos=DadosExtraidos(
            tipo_evento="festa fictícia", confianca_tipo_evento=ALTA
        ),
        perguntas_comerciais=(
            PerguntaComercial(
                texto="quanto custa?",
                confianca=ALTA,
                assunto=AssuntoComercial.PRECO_LOCACAO,
            ),
        ),
        pedido_de_humano=True,
        confianca_pedido_de_humano=ALTA,
        intencoes_autonomas=(
            IntencaoAutonomaRecebida(
                codigo=IntencaoConversacional.INTERESSE_EM_VISITA, confianca=ALTA
            ),
        ),
    )
    assert decidir_encerramento(alvo, INCOMPATIVEL) is None


@pytest.mark.parametrize(
    "par", list(itertools.combinations(SINAIS, 2)), ids=lambda p: "+".join(c.value for c in p)
)
def test_dois_sinais_alta_sao_fail_closed(
    par: tuple[IntencaoConversacional, ...]
) -> None:
    assert decidir_encerramento(com_sinais(*((s, ALTA) for s in par)), INCOMPATIVEL) is None


def test_existem_exatamente_seis_pares_possiveis() -> None:
    assert len(list(itertools.combinations(SINAIS, 2))) == 6


@pytest.mark.parametrize(
    "trio",
    list(itertools.combinations(SINAIS, 3)),
    ids=lambda t: "+".join(c.value for c in t),
)
def test_tres_sinais_alta_sao_fail_closed(
    trio: tuple[IntencaoConversacional, ...]
) -> None:
    assert decidir_encerramento(com_sinais(*((s, ALTA) for s in trio)), INCOMPATIVEL) is None


def test_quatro_sinais_alta_sao_fail_closed() -> None:
    alvo = com_sinais(*((sinal, ALTA) for sinal in SINAIS))
    assert decidir_encerramento(alvo, INCOMPATIVEL) is None


def test_nao_existe_ranking_oculto_entre_os_sinais() -> None:
    """Nenhum sinal "vence" outro: **todo** conflito de `ALTA` devolve `None`."""
    for tamanho in (2, 3, 4):
        for grupo in itertools.combinations(SINAIS, tamanho):
            for resultado_q in ResultadoQualificacao:
                assert (
                    decidir_encerramento(
                        com_sinais(*((s, ALTA) for s in grupo)), resultado_q
                    )
                    is None
                )


def test_a_ordem_dos_sinais_na_entrada_nao_altera_o_resultado() -> None:
    direto = com_sinais((DESINTERESSE, ALTA), (ENGANO, BAIXA), (SPAM, BAIXA))
    invertido = com_sinais((SPAM, BAIXA), (ENGANO, BAIXA), (DESINTERESSE, ALTA))
    assert decidir_encerramento(direto, INCOMPATIVEL) == decidir_encerramento(
        invertido, INCOMPATIVEL
    )


# --------------------------------------------------------------------------
# D. *Gate* cumulativo da incompatibilidade (S3D1-9)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("resultado_q", NAO_INCOMPATIVEIS, ids=lambda r: r.value)
def test_aceitacao_alta_sem_incompativel_devolve_none(
    resultado_q: ResultadoQualificacao,
) -> None:
    assert decidir_encerramento(com_sinais((ACEITACAO, ALTA)), resultado_q) is None


def test_existem_quatro_resultados_nao_incompativeis() -> None:
    assert len(NAO_INCOMPATIVEIS) == 4
    assert len(list(ResultadoQualificacao)) == 5


def test_incompativel_sem_aceite_nao_encerra() -> None:
    """Estar incompatível **não basta**: o sinal de aceitação é obrigatório."""
    assert decidir_encerramento(interpretacao(), INCOMPATIVEL) is None


def test_aceitacao_baixa_com_incompativel_nao_encerra() -> None:
    """O *gate* é **cumulativo**: `BAIXA` não satisfaz a primeira exigência."""
    assert decidir_encerramento(com_sinais((ACEITACAO, BAIXA)), INCOMPATIVEL) is None


@pytest.mark.parametrize(
    "sinal", [DESINTERESSE, ENGANO, SPAM], ids=lambda c: c.value
)
@pytest.mark.parametrize("resultado_q", list(ResultadoQualificacao), ids=lambda r: r.value)
def test_os_outros_tres_motivos_nao_dependem_da_qualificacao(
    sinal: IntencaoConversacional, resultado_q: ResultadoQualificacao
) -> None:
    resultado = decidir_encerramento(com_sinais((sinal, ALTA)), resultado_q)
    assert resultado is not None
    assert resultado.motivo is MOTIVO_ESPERADO[sinal]


# --------------------------------------------------------------------------
# E. Validação e erros (S3D1-4)
# --------------------------------------------------------------------------


def test_none_como_interpretacao_e_type_error() -> None:
    with pytest.raises(TypeError):
        decidir_encerramento(None, INCOMPATIVEL)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "valor", ["texto", 1, 1.5, True, (), [], {}, object()], ids=repr
)
def test_tipo_errado_de_interpretacao_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        decidir_encerramento(valor, INCOMPATIVEL)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "valor", [None, "incompativel", 1, True, (), object(), Evento.E14], ids=repr
)
def test_tipo_errado_de_resultado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        decidir_encerramento(com_sinais((DESINTERESSE, ALTA)), valor)  # type: ignore[arg-type]


def test_qualificacao_completa_nao_e_aceita_no_lugar_do_resultado() -> None:
    """S3D1-3: a função recebe `ResultadoQualificacao`, não a `Qualificacao`."""
    with pytest.raises(TypeError):
        decidir_encerramento(
            com_sinais((ACEITACAO, ALTA)),
            qualificacao(INCOMPATIVEL),  # type: ignore[arg-type]
        )


def test_interpretacao_construida_diretamente_mas_invalida_e_bloqueada() -> None:
    """`isinstance` prova o tipo, não a validade (S3D1-4)."""
    invalida = Interpretacao(
        intencoes_detectadas=(
            IntencaoDetectada(codigo=DESINTERESSE, confianca=ALTA),
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
        decidir_encerramento(invalida, INCOMPATIVEL)


def test_confianca_global_ausente_bloqueia_sem_saida_parcial() -> None:
    invalida = Interpretacao(
        intencoes_detectadas=(
            IntencaoDetectada(codigo=DESINTERESSE, confianca=ALTA),
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
        decidir_encerramento(invalida, INCOMPATIVEL)


def test_a_validacao_canonica_e_reutilizada_e_nao_duplicada() -> None:
    """A fronteira **importa** o validador existente — não o reescreve."""
    arvore = ast.parse(MODULO_S3D1.read_text(encoding="utf-8"))
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
    assert definidas == {"decidir_encerramento", "__post_init__"}


# --------------------------------------------------------------------------
# F. Invariante de `EncerramentoInterpretado` (S3D1-5)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "evento", [e for e in Evento if e is not Evento.E14], ids=lambda e: e.value
)
def test_construcao_com_evento_diferente_de_e14_e_rejeitada(evento: Evento) -> None:
    with pytest.raises(ValueError):
        EncerramentoInterpretado(
            evento=evento, motivo=MotivoEncerramento.SEM_INTERESSE
        )


def test_construcao_com_e14_e_aceita() -> None:
    alvo = EncerramentoInterpretado(
        evento=Evento.E14, motivo=MotivoEncerramento.SEM_INTERESSE
    )
    assert alvo.evento is Evento.E14


@pytest.mark.parametrize("valor", [None, "E14", 14, object()], ids=repr)
def test_evento_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        EncerramentoInterpretado(evento=valor, motivo=MotivoEncerramento.SPAM)


@pytest.mark.parametrize("valor", [None, "spam", 1, object()], ids=repr)
def test_motivo_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        EncerramentoInterpretado(evento=Evento.E14, motivo=valor)


def test_a_estrutura_tem_exatamente_dois_campos_e_e_imutavel() -> None:
    campos = [campo.name for campo in dataclasses.fields(EncerramentoInterpretado)]
    assert campos == ["evento", "motivo"]
    alvo = EncerramentoInterpretado(
        evento=Evento.E14, motivo=MotivoEncerramento.ENGANO
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        alvo.motivo = MotivoEncerramento.SPAM  # type: ignore[misc]


# --------------------------------------------------------------------------
# G. Composição com a `MaquinaEstados` — o contrato vigente não muda
# --------------------------------------------------------------------------

#: Estados em que **T35** é cabível: qualquer um exceto `atendimento_humano`,
#: `encaminhado_humano` (T32 tem precedência) e `encerrado`.
ESTADOS_DE_T35 = tuple(
    estado
    for estado in Estado
    if estado
    not in (
        Estado.ATENDIMENTO_HUMANO,
        Estado.ENCAMINHADO_HUMANO,
        Estado.ENCERRADO,
    )
)


def condicoes_de(resultado: EncerramentoInterpretado) -> CondicoesCiclo:
    """O que o futuro `OrquestradorMotor` faria: repassar o motivo produzido."""
    return CondicoesCiclo(motivo_encerramento=resultado.motivo)


@pytest.mark.parametrize("estado", ESTADOS_DE_T35, ids=lambda e: e.value)
@pytest.mark.parametrize("sinal", SINAIS, ids=lambda c: c.value)
def test_o_resultado_alimenta_t35_nos_estados_cabiveis(
    estado: Estado, sinal: IntencaoConversacional
) -> None:
    resultado = decidir_encerramento(com_sinais((sinal, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    decisao = decidir(
        estado,
        (resultado.evento,),
        qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes_de(resultado),
    )
    assert Transicao.T35 in decisao.caminho
    assert decisao.estado_final is Estado.ENCERRADO
    assert decisao.motivo_encerramento is resultado.motivo


@pytest.mark.parametrize("estado", ESTADOS_DE_T35, ids=lambda e: e.value)
def test_somente_sem_interesse_adiciona_despedida(estado: Estado) -> None:
    resultado = decidir_encerramento(com_sinais((DESINTERESSE, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    decisao = decidir(
        estado,
        (Evento.E14,),
        qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes_de(resultado),
    )
    assert AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE in decisao.acoes


@pytest.mark.parametrize("estado", ESTADOS_DE_T35, ids=lambda e: e.value)
@pytest.mark.parametrize("sinal", [ENGANO, SPAM, ACEITACAO], ids=lambda c: c.value)
def test_os_outros_tres_motivos_nao_adicionam_despedida(
    estado: Estado, sinal: IntencaoConversacional
) -> None:
    resultado = decidir_encerramento(com_sinais((sinal, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    decisao = decidir(
        estado,
        (Evento.E14,),
        qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes_de(resultado),
    )
    assert AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE not in decisao.acoes


#: Estados em que **`E18` é resolvível** pelo contrato vigente e o `E14`
#: concomitante sobra para **N3**. `pronto_para_handoff` e `atendimento_humano`
#: ficam de fora porque **o próprio `E18` não é resolvido ali** — fato vigente da
#: `MaquinaEstados`, anterior e alheio a S3-D1, que **não é corrigido aqui**.
#: `encaminhado_humano` também fica de fora: lá o `E14` é **consumido por T32**,
#: e a prova própria está em `test_e14_em_encaminhado_humano_preserva_t32`.
ESTADOS_DE_N3 = (
    Estado.NOVO,
    Estado.COLETANDO_DADOS,
    Estado.RESPONDENDO_DUVIDAS,
    Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
)


@pytest.mark.parametrize("estado", ESTADOS_DE_N3, ids=lambda e: e.value)
@pytest.mark.parametrize("sinal", SINAIS, ids=lambda c: c.value)
def test_e14_com_e18_preserva_n3(estado: Estado, sinal: IntencaoConversacional) -> None:
    """S3D1-11: com `E18` concomitante, T35 não entra e o motivo não é ecoado."""
    resultado = decidir_encerramento(com_sinais((sinal, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    decisao = decidir(
        estado,
        (resultado.evento, Evento.E18),
        qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
        CondicoesCiclo(
            motivo_encerramento=resultado.motivo, motivos_handoff=("gatilho_ficticio",)
        ),
    )
    assert Transicao.T35 not in decisao.caminho
    assert Inercia.N3 in decisao.inercias
    assert decisao.motivo_encerramento is None
    assert AcaoMaquina.DESPEDIR_SEM_CONTINUIDADE not in decisao.acoes


@pytest.mark.parametrize("sinal", SINAIS, ids=lambda c: c.value)
def test_e14_em_encaminhado_humano_preserva_t32(
    sinal: IntencaoConversacional,
) -> None:
    resultado = decidir_encerramento(com_sinais((sinal, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    decisao = decidir(
        Estado.ENCAMINHADO_HUMANO,
        (resultado.evento,),
        qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes_de(resultado),
    )
    assert decisao.caminho == (Transicao.T32,)
    assert decisao.estado_final is Estado.ENCERRADO
    assert decisao.motivo_encerramento is None


@pytest.mark.parametrize("sinal", SINAIS, ids=lambda c: c.value)
def test_e14_em_atendimento_humano_preserva_t34(
    sinal: IntencaoConversacional,
) -> None:
    resultado = decidir_encerramento(com_sinais((sinal, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO,
        (resultado.evento,),
        qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
        condicoes_de(resultado),
    )
    assert decisao.caminho == (Transicao.T34,)
    assert decisao.estado_final is Estado.ENCERRADO
    assert decisao.motivo_encerramento is None
    assert decisao.acoes == ()


def test_o_motivo_nao_e_ecoado_quando_t35_nao_entrou() -> None:
    """Em T32 e T34 o motivo existe nas condições e **não** sai na decisão."""
    resultado = decidir_encerramento(com_sinais((DESINTERESSE, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    for estado in (Estado.ENCAMINHADO_HUMANO, Estado.ATENDIMENTO_HUMANO):
        decisao = decidir(
            estado,
            (Evento.E14,),
            qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
            condicoes_de(resultado),
        )
        assert Transicao.T35 not in decisao.caminho
        assert decisao.motivo_encerramento is None


def test_nenhuma_transicao_nova_aparece_no_caminho() -> None:
    """S3D1-10: a máquina resolve `E14` só por T32, T34 ou T35."""
    resultado = decidir_encerramento(com_sinais((SPAM, ALTA)), INCOMPATIVEL)
    assert resultado is not None
    vistas: set[Transicao] = set()
    for estado in Estado:
        if estado is Estado.ENCERRADO:
            continue
        decisao = decidir(
            estado,
            (Evento.E14,),
            qualificacao(ResultadoQualificacao.DADOS_INCOMPLETOS),
            condicoes_de(resultado),
        )
        vistas.update(decisao.caminho)
    assert vistas <= {Transicao.T32, Transicao.T34, Transicao.T35}


def test_a_maquina_nao_muda_e_o_vocabulario_de_motivo_continua_fechado() -> None:
    assert len(list(MotivoEncerramento)) == 4
    assert set(MotivoEncerramento) == {
        MotivoEncerramento.SEM_INTERESSE,
        MotivoEncerramento.ENGANO,
        MotivoEncerramento.SPAM,
        MotivoEncerramento.INCOMPATIBILIDADE_ACEITA,
    }
    assert len(list(Evento)) == 18


# --------------------------------------------------------------------------
# H. Pureza e fronteira do módulo (S3D1-12)
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
    assert modulos_importados(MODULO_S3D1) <= {
        "__future__",
        "dataclasses",
        "casa77_sdr",
    }

    arvore = ast.parse(MODULO_S3D1.read_text(encoding="utf-8"))
    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert submodulos == {
        "__future__",
        "dataclasses",
        "casa77_sdr.identity",
        "casa77_sdr.interpretation",
        "casa77_sdr.qualification",
        "casa77_sdr.state_machine",
    }
    for proibido in (
        "casa77_sdr.interpretation_llm",
        "casa77_sdr.interpretation_anthropic",
        "casa77_sdr.interpretation_events",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.persistence",
        "casa77_sdr.knowledge",
        "casa77_sdr.context",
        "casa77_sdr.rules",
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
    } == set()


def test_a_superficie_publica_e_fechada_em_dois_nomes() -> None:
    assert closure_decision.__all__ == [
        "EncerramentoInterpretado",
        "decidir_encerramento",
    ]


def test_a_fronteira_nao_e_exportada_pelo_pacote() -> None:
    """M-NB1 preservado: nada desta fronteira sai pelo `__init__.py`."""
    import casa77_sdr

    for nome in ("EncerramentoInterpretado", "decidir_encerramento"):
        assert nome not in casa77_sdr.__all__
        assert not hasattr(casa77_sdr, nome)


def test_nenhuma_excecao_publica_nova_e_criada() -> None:
    arvore = ast.parse(MODULO_S3D1.read_text(encoding="utf-8"))
    classes = [no for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)]
    assert [no.name for no in classes] == ["EncerramentoInterpretado"]
    assert classes[0].bases == []


def test_a_assinatura_nao_recebe_estado_takeover_nem_contexto() -> None:
    """S3D1-3/S3D1-10: a fronteira é agnóstica ao estado."""
    import inspect

    parametros = inspect.signature(decidir_encerramento).parameters
    assert list(parametros) == ["interpretacao", "resultado_qualificacao"]
    anotacoes = {nome: str(p.annotation) for nome, p in parametros.items()}
    for proibido in (
        "Estado",
        "SituacaoTakeover",
        "CondicoesCiclo",
        "Contexto",
        "dict",
        "str",
    ):
        assert all(proibido not in valor for valor in anotacoes.values())


def test_a_funcao_nao_le_texto_para_decidir() -> None:
    """S3D1-7/S3D1-12: a decisão vem só dos códigos e da confiança."""
    fonte = MODULO_S3D1.read_text(encoding="utf-8")
    corpo = fonte.split('"""', 2)[2]
    arvore = ast.parse(fonte)
    alvo = next(
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef) and no.name == "decidir_encerramento"
    )
    atributos = {no.attr for no in ast.walk(alvo) if isinstance(no, ast.Attribute)}
    # Só o eixo de códigos e confiança, mais os membros de enum usados na saída.
    assert atributos == {
        "intencoes_detectadas",
        "codigo",
        "confianca",
        "ALTA",
        "INCOMPATIVEL",
        "ACEITACAO_DE_INCOMPATIBILIDADE",
        "E14",
    }
    for proibido in (
        "texto",
        "dados_extraidos",
        "perguntas_comerciais",
        "trechos_ambiguos",
        "referencias_evento_anterior",
        "correcoes",
        "confianca_global",
        "nome",
        "contato",
    ):
        assert proibido not in atributos
    # Nenhuma palavra-chave, regex, score ou contador semântico no módulo.
    for proibido in ("re.", "import re", "score", "len(texto", "lower()", "strip()"):
        assert proibido not in corpo


def test_a_entrada_nao_e_mutada() -> None:
    alvo = com_sinais((DESINTERESSE, ALTA), (ENGANO, BAIXA))
    antes = (
        alvo.intencoes_detectadas,
        alvo.dados_extraidos,
        alvo.perguntas_comerciais,
        alvo.confianca_global,
    )
    decidir_encerramento(alvo, INCOMPATIVEL)
    assert (
        alvo.intencoes_detectadas,
        alvo.dados_extraidos,
        alvo.perguntas_comerciais,
        alvo.confianca_global,
    ) == antes


def test_a_funcao_e_deterministica() -> None:
    alvo = com_sinais((SPAM, ALTA))
    assert len({decidir_encerramento(alvo, INCOMPATIVEL) for _ in range(5)}) == 1


def test_a_saida_e_sempre_encerramento_interpretado_ou_none() -> None:
    for sinal in SINAIS:
        for confianca in (ALTA, BAIXA):
            for resultado_q in ResultadoQualificacao:
                saida = decidir_encerramento(
                    com_sinais((sinal, confianca)), resultado_q
                )
                assert saida is None or isinstance(saida, EncerramentoInterpretado)


def test_a_matriz_de_sinal_confianca_resultado_e_exaustiva() -> None:
    """Todas as combinações úteis, sem ranking oculto e sem redundância."""
    esperados: dict[tuple[IntencaoConversacional, Confianca, ResultadoQualificacao], Any] = {}
    for sinal in SINAIS:
        for confianca in (ALTA, BAIXA):
            for resultado_q in ResultadoQualificacao:
                if confianca is BAIXA:
                    esperado = None
                elif sinal is ACEITACAO and resultado_q is not INCOMPATIVEL:
                    esperado = None
                else:
                    esperado = EncerramentoInterpretado(
                        evento=Evento.E14, motivo=MOTIVO_ESPERADO[sinal]
                    )
                esperados[(sinal, confianca, resultado_q)] = esperado

    assert len(esperados) == 4 * 2 * 5 == 40
    for (sinal, confianca, resultado_q), esperado in esperados.items():
        assert (
            decidir_encerramento(com_sinais((sinal, confianca)), resultado_q)
            is esperado
            or decidir_encerramento(com_sinais((sinal, confianca)), resultado_q)
            == esperado
        )


def test_a_etapa_4_continua_sem_produzir_e14_ou_motivo() -> None:
    """S3D1-1: quem produz é esta fronteira, nunca a etapa 4."""
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
    for proibido in ("Evento", "MotivoEncerramento", "E14", "motivo_encerramento"):
        assert proibido not in nomes

    import casa77_sdr.interpretation as etapa4

    assert not hasattr(etapa4, "Evento")
    assert not hasattr(etapa4, "MotivoEncerramento")
    assert "decidir_encerramento" not in etapa4.__all__


def test_o_formato_do_evento_continua_fora_da_fronteira_de_qualificacao() -> None:
    """A fronteira lê **somente** o `ResultadoQualificacao` recebido."""
    fonte = MODULO_S3D1.read_text(encoding="utf-8")
    corpo = fonte.split('"""', 2)[2]
    for proibido in ("Qualificacao(", "motivos", "violacoes", FormatoEvento.__name__):
        assert proibido not in corpo
