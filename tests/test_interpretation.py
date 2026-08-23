"""Testes da fronteira determinística da interpretação da etapa 4 (N-b / AJ1).

Cobre o contrato de `docs/07-arquitetura-motor-respostas.md` §6.3 — a arbitragem
**N-b** e a micro-arbitragem **AJ1** — e os cenários **K-Nb-1–K-Nb-40** de §8.2,
conforme a classificação AJ1 vigente:

* **recebíveis / runtime** — provados por exceção sobre a entrada realmente
  recebida;
* **invariantes internos da canonicalização** — provados como **propriedade /
  pós-condição** sobre toda `Interpretacao` canônica, nunca fabricando entrada
  externa artificial (AJ1-13c);
* **invariante estrutural do módulo** (`E-Nb-19`) — provado sobre a superfície
  pública, os tipos de retorno, os campos das estruturas e os produtores.

`K-Nb-39` é coberto **somente na parte local**: a parte dependente de
orquestração — etapa 5 não executar, `MaquinaEstados` não ser chamada, nada ser
gravado, alertas e coordenação do modo degradado — **não** é testada aqui e
**não** se alega cobertura dela.

Todas as fixtures são **fictícias e genéricas**: nenhum dado pessoal real,
nenhuma conversa real, nenhum valor comercial. A fronteira não lê a base, não
faz I/O e não usa LLM.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import re
from pathlib import Path

import pytest

from casa77_sdr import interpretation
from casa77_sdr.identity import (
    Confianca,
    IntencaoIdentidade,
    ProjecaoInterpretacao,
    ReferenciaEventoAnterior,
)
from casa77_sdr.interpretation import (
    CorrecaoInterpretada,
    DadosExtraidos,
    EntradaInterpretacao,
    IntencaoAutonomaRecebida,
    IntencaoConversacional,
    IntencaoDetectada,
    Interpretacao,
    PerguntaComercial,
    ReferenciaAoEventoAnterior,
    TrechoAmbiguo,
    TrechoAmbiguoRecebido,
    canonicalizar_interpretacao,
    decidir_interesse_confirmar_disponibilidade,
    projetar_para_identidade,
)
from casa77_sdr.qualification import FormatoEvento

MODULO_INTERPRETACAO = (
    Path(__file__).resolve().parents[1] / "src" / "casa77_sdr" / "interpretation.py"
)

ALTA = Confianca.ALTA
BAIXA = Confianca.BAIXA


# --------------------------------------------------------------------------
# Fixtures genéricas
# --------------------------------------------------------------------------


def entrada(**ajustes: object) -> EntradaInterpretacao:
    """Entrada mínima válida; cada teste ajusta apenas o que exercita."""
    base: dict[str, object] = {
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


def autonoma(
    codigo: IntencaoConversacional, confianca: Confianca | None
) -> tuple[IntencaoAutonomaRecebida, ...]:
    return (IntencaoAutonomaRecebida(codigo=codigo, confianca=confianca),)


def confianca_de(
    resultado: Interpretacao, codigo: IntencaoConversacional
) -> Confianca | None:
    for item in resultado.intencoes_detectadas:
        if item.codigo is codigo:
            return item.confianca
    return None


def agregacao_de_referencia(confiancas: tuple[Confianca, ...]) -> Confianca:
    """Reimplementação **independente** de N-b-X3, para não provar tautologia."""
    return ALTA if any(c is ALTA for c in confiancas) else BAIXA


# --------------------------------------------------------------------------
# A. Vocabulário — IntencaoConversacional com exatamente 11 valores
# --------------------------------------------------------------------------


def test_intencao_conversacional_tem_exatamente_onze_valores() -> None:
    assert len(list(IntencaoConversacional)) == 11


def test_particao_a1_a2_b_e_fechada_e_exata() -> None:
    a1 = [
        IntencaoConversacional.TIPO_EVENTO_INFORMADO,
        IntencaoConversacional.DATA_INFORMADA,
        IntencaoConversacional.CONVIDADOS_INFORMADOS,
        IntencaoConversacional.FORMATO_INFORMADO,
        IntencaoConversacional.PERGUNTA_COMERCIAL,
        IntencaoConversacional.PEDIDO_DE_HUMANO,
    ]
    a2 = [
        IntencaoConversacional.INTERESSE_EM_VISITA,
        IntencaoConversacional.EXCECAO_SOLICITADA,
    ]
    b = [
        IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE,
        IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA,
        IntencaoConversacional.EVENTO_NOVO_DECLARADO,
    ]
    assert len(a1) == 6 and len(a2) == 2 and len(b) == 3
    assert list(IntencaoConversacional) == a1 + a2 + b


def test_nao_existe_decimo_segundo_valor() -> None:
    with pytest.raises(ValueError):
        IntencaoConversacional("intencao_inexistente")


# --------------------------------------------------------------------------
# B. AJ1-1 — A1 não é entrada semântica independente
# --------------------------------------------------------------------------


def test_entrada_nao_possui_slot_de_intencoes_a1() -> None:
    """AJ1-1/AJ1-2: a entrada só tem as categorias reais e o slot autônomo."""
    nomes = [campo.name for campo in dataclasses.fields(EntradaInterpretacao)]
    assert nomes == [
        "dados_extraidos",
        "correcoes",
        "perguntas_comerciais",
        "pedido_de_humano",
        "confianca_pedido_de_humano",
        "referencias_evento_anterior",
        "trechos_ambiguos",
        "confianca_global",
        "intencoes_autonomas",
    ]
    assert "intencoes_detectadas" not in nomes


@pytest.mark.parametrize("codigo", sorted(interpretation._CODIGOS_A1, key=str))
def test_a1_no_slot_autonomo_sem_confianca_e_e_nb_5(
    codigo: IntencaoConversacional,
) -> None:
    """AJ1, caso B."""
    with pytest.raises(ValueError, match="E-Nb-5"):
        canonicalizar_interpretacao(entrada(intencoes_autonomas=autonoma(codigo, None)))


@pytest.mark.parametrize("codigo", sorted(interpretation._CODIGOS_A1, key=str))
@pytest.mark.parametrize("confianca", [ALTA, BAIXA])
def test_a1_no_slot_autonomo_com_confianca_e_e_nb_3(
    codigo: IntencaoConversacional, confianca: Confianca
) -> None:
    """AJ1, caso A — `E-Nb-3` **prevalece** sobre `E-Nb-5` (K-Nb-34)."""
    with pytest.raises(ValueError, match="E-Nb-3"):
        canonicalizar_interpretacao(
            entrada(intencoes_autonomas=autonoma(codigo, confianca))
        )


def test_a1_no_slot_autonomo_nunca_produz_interpretacao() -> None:
    """Ambos os casos bloqueiam **antes** da canonicalização."""
    for confianca in (None, ALTA):
        with pytest.raises(ValueError):
            canonicalizar_interpretacao(
                entrada(
                    intencoes_autonomas=autonoma(
                        IntencaoConversacional.PEDIDO_DE_HUMANO, confianca
                    )
                )
            )


def test_e_nb_13_nao_prevalece_sobre_e_nb_3() -> None:
    """AJ1-13c: tentar declarar confiança A1 é `E-Nb-3`, nunca `E-Nb-13`."""
    with pytest.raises(ValueError) as excecao:
        canonicalizar_interpretacao(
            entrada(
                intencoes_autonomas=autonoma(
                    IntencaoConversacional.TIPO_EVENTO_INFORMADO, ALTA
                )
            )
        )
    assert str(excecao.value).startswith("E-Nb-3")
    assert "E-Nb-13" not in str(excecao.value)


# --------------------------------------------------------------------------
# C. Derivação A1 — presença pelo payload (N-b-X2, N-b-X4)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("ajuste", "codigo"),
    [
        (
            {"tipo_evento": "evento generico", "confianca_tipo_evento": ALTA},
            IntencaoConversacional.TIPO_EVENTO_INFORMADO,
        ),
        (
            {"data_nomeada": "mes que vem", "confianca_data_nomeada": ALTA},
            IntencaoConversacional.DATA_INFORMADA,
        ),
        (
            {"convidados": 30, "confianca_convidados": ALTA},
            IntencaoConversacional.CONVIDADOS_INFORMADOS,
        ),
        (
            {"formato": FormatoEvento.COQUETEL, "confianca_formato": ALTA},
            IntencaoConversacional.FORMATO_INFORMADO,
        ),
    ],
)
def test_payload_presente_deriva_o_codigo_a1(
    ajuste: dict[str, object], codigo: IntencaoConversacional
) -> None:
    resultado = canonicalizar_interpretacao(
        entrada(dados_extraidos=DadosExtraidos(**ajuste))  # type: ignore[arg-type]
    )
    assert codigo in {item.codigo for item in resultado.intencoes_detectadas}


def test_payload_ausente_nao_deriva_nenhum_a1() -> None:
    resultado = canonicalizar_interpretacao(entrada())
    assert resultado.intencoes_detectadas == ()


def test_perguntas_nao_vazias_derivam_pergunta_comercial() -> None:
    resultado = canonicalizar_interpretacao(
        entrada(perguntas_comerciais=(PerguntaComercial("tem estacionamento?", ALTA),))
    )
    assert confianca_de(resultado, IntencaoConversacional.PERGUNTA_COMERCIAL) is ALTA


def test_pedido_de_humano_verdadeiro_deriva_o_codigo() -> None:
    resultado = canonicalizar_interpretacao(
        entrada(pedido_de_humano=True, confianca_pedido_de_humano=ALTA)
    )
    assert (
        confianca_de(resultado, IntencaoConversacional.PEDIDO_DE_HUMANO) is ALTA
    )


def test_pedido_de_humano_falso_nao_deriva_o_codigo() -> None:
    resultado = canonicalizar_interpretacao(entrada())
    assert (
        IntencaoConversacional.PEDIDO_DE_HUMANO
        not in {item.codigo for item in resultado.intencoes_detectadas}
    )


# --------------------------------------------------------------------------
# D. Confiança A1 calculada por N-b-X3 — e K-Nb-18 como propriedade
# --------------------------------------------------------------------------


@pytest.mark.parametrize("confianca", [ALTA, BAIXA])
def test_payload_unitario_transporta_a_mesma_confianca(confianca: Confianca) -> None:
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento="evento generico", confianca_tipo_evento=confianca
            )
        )
    )
    assert (
        confianca_de(resultado, IntencaoConversacional.TIPO_EVENTO_INFORMADO)
        is confianca
    )


@pytest.mark.parametrize(
    ("confiancas", "esperada"),
    [
        ((ALTA,), ALTA),
        ((BAIXA,), BAIXA),
        ((ALTA, BAIXA), ALTA),
        ((BAIXA, ALTA), ALTA),
        ((BAIXA, BAIXA), BAIXA),
        ((ALTA, ALTA), ALTA),
    ],
)
def test_agregacao_de_perguntas_segue_n_b_x3(
    confiancas: tuple[Confianca, ...], esperada: Confianca
) -> None:
    perguntas = tuple(
        PerguntaComercial(f"pergunta generica {indice}", confianca)
        for indice, confianca in enumerate(confiancas)
    )
    resultado = canonicalizar_interpretacao(entrada(perguntas_comerciais=perguntas))
    assert (
        confianca_de(resultado, IntencaoConversacional.PERGUNTA_COMERCIAL) is esperada
    )


def _combinacoes_para_propriedade() -> list[EntradaInterpretacao]:
    """Amostra ampla e determinística de entradas canonicalizáveis."""
    casos: list[EntradaInterpretacao] = []
    for confianca_tipo in (ALTA, BAIXA):
        for confianca_data in (ALTA, BAIXA):
            for perguntas in (
                (),
                (PerguntaComercial("pergunta generica", BAIXA),),
                (
                    PerguntaComercial("pergunta generica a", BAIXA),
                    PerguntaComercial("pergunta generica b", ALTA),
                ),
            ):
                for pedido, confianca_pedido in (
                    (False, None),
                    (True, ALTA),
                    (True, BAIXA),
                ):
                    casos.append(
                        entrada(
                            dados_extraidos=DadosExtraidos(
                                tipo_evento="evento generico",
                                confianca_tipo_evento=confianca_tipo,
                                data_nomeada="data generica",
                                confianca_data_nomeada=confianca_data,
                                convidados=10,
                                confianca_convidados=BAIXA,
                                formato=FormatoEvento.SENTADO,
                                confianca_formato=ALTA,
                            ),
                            perguntas_comerciais=perguntas,
                            pedido_de_humano=pedido,
                            confianca_pedido_de_humano=confianca_pedido,
                        )
                    )
    return casos


@pytest.mark.parametrize("caso", _combinacoes_para_propriedade())
def test_k_nb_18_confianca_a1_sempre_corresponde_a_n_b_x3(
    caso: EntradaInterpretacao,
) -> None:
    """K-Nb-18 — **estrutural**: pós-condição sobre toda `Interpretacao` canônica.

    `E-Nb-13` é invariante / program error da derivação (AJ1-13a): a prova é a
    propriedade "confiança A1 == resultado de N-b-X3", **não** uma exceção
    provocada por confiança A1 recebida divergente — nenhuma confiança A1
    independente é aceita do produtor (AJ1-13c).
    """
    resultado = canonicalizar_interpretacao(caso)
    dados = resultado.dados_extraidos

    esperado: dict[IntencaoConversacional, Confianca] = {}
    if dados.tipo_evento is not None:
        esperado[IntencaoConversacional.TIPO_EVENTO_INFORMADO] = (
            dados.confianca_tipo_evento
        )
    if dados.data_nomeada is not None:
        esperado[IntencaoConversacional.DATA_INFORMADA] = dados.confianca_data_nomeada
    if dados.convidados is not None:
        esperado[IntencaoConversacional.CONVIDADOS_INFORMADOS] = (
            dados.confianca_convidados
        )
    if dados.formato is not None:
        esperado[IntencaoConversacional.FORMATO_INFORMADO] = dados.confianca_formato
    if resultado.perguntas_comerciais:
        esperado[IntencaoConversacional.PERGUNTA_COMERCIAL] = agregacao_de_referencia(
            tuple(p.confianca for p in resultado.perguntas_comerciais)
        )
    if resultado.pedido_de_humano:
        esperado[IntencaoConversacional.PEDIDO_DE_HUMANO] = (
            resultado.confianca_pedido_de_humano
        )

    obtido = {
        item.codigo: item.confianca
        for item in resultado.intencoes_detectadas
        if item.codigo in interpretation._CODIGOS_A1
    }
    assert obtido == esperado


def test_confianca_a1_armazenada_nao_significa_declarada() -> None:
    """AJ1-A1c: o valor armazenado é **resultado** da derivação, não insumo."""
    resultado = canonicalizar_interpretacao(
        entrada(
            perguntas_comerciais=(
                PerguntaComercial("pergunta generica a", BAIXA),
                PerguntaComercial("pergunta generica b", ALTA),
            )
        )
    )
    armazenada = confianca_de(resultado, IntencaoConversacional.PERGUNTA_COMERCIAL)
    assert armazenada is ALTA
    assert armazenada is not resultado.perguntas_comerciais[0].confianca


# --------------------------------------------------------------------------
# E. Ordem canônica e ausência de repetição (AJ1-A1d, AJ1-A1e)
# --------------------------------------------------------------------------


def test_ordem_canonica_segue_a_declaracao_do_enum() -> None:
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento="evento generico",
                confianca_tipo_evento=ALTA,
                convidados=12,
                confianca_convidados=ALTA,
            ),
            pedido_de_humano=True,
            confianca_pedido_de_humano=ALTA,
            intencoes_autonomas=(
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.EVENTO_NOVO_DECLARADO, ALTA
                ),
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.INTERESSE_EM_VISITA, ALTA
                ),
            ),
        )
    )
    codigos = [item.codigo for item in resultado.intencoes_detectadas]
    assert codigos == [
        IntencaoConversacional.TIPO_EVENTO_INFORMADO,
        IntencaoConversacional.CONVIDADOS_INFORMADOS,
        IntencaoConversacional.PEDIDO_DE_HUMANO,
        IntencaoConversacional.INTERESSE_EM_VISITA,
        IntencaoConversacional.EVENTO_NOVO_DECLARADO,
    ]


def test_intencoes_detectadas_nao_tem_repeticao() -> None:
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento="evento generico", confianca_tipo_evento=ALTA
            ),
            intencoes_autonomas=(
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.EXCECAO_SOLICITADA, BAIXA
                ),
            ),
        )
    )
    codigos = [item.codigo for item in resultado.intencoes_detectadas]
    assert len(codigos) == len(set(codigos))


def test_ordem_canonica_nao_cria_precedencia_semantica() -> None:
    """A ordem não altera projeção nem condição 5 — é só auditabilidade."""
    a = entrada(
        intencoes_autonomas=(
            IntencaoAutonomaRecebida(
                IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA
            ),
            IntencaoAutonomaRecebida(IntencaoConversacional.INTERESSE_EM_VISITA, BAIXA),
        )
    )
    b = entrada(
        intencoes_autonomas=(
            IntencaoAutonomaRecebida(IntencaoConversacional.INTERESSE_EM_VISITA, BAIXA),
            IntencaoAutonomaRecebida(
                IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA
            ),
        )
    )
    primeira = canonicalizar_interpretacao(a)
    segunda = canonicalizar_interpretacao(b)
    assert primeira.intencoes_detectadas == segunda.intencoes_detectadas
    assert projetar_para_identidade(primeira) == projetar_para_identidade(segunda)
    assert decidir_interesse_confirmar_disponibilidade(
        primeira
    ) == decidir_interesse_confirmar_disponibilidade(segunda)


# --------------------------------------------------------------------------
# F. Dados extraídos — seis campos, confiança e domínios (N-b-D1–N-b-D7)
# --------------------------------------------------------------------------


def test_dados_extraidos_tem_exatamente_os_seis_campos_e_suas_confiancas() -> None:
    nomes = [campo.name for campo in dataclasses.fields(DadosExtraidos)]
    assert nomes == [
        "tipo_evento",
        "confianca_tipo_evento",
        "data_nomeada",
        "confianca_data_nomeada",
        "convidados",
        "confianca_convidados",
        "formato",
        "confianca_formato",
        "nome",
        "confianca_nome",
        "contato",
        "confianca_contato",
    ]


@pytest.mark.parametrize(
    "ajuste",
    [
        {"tipo_evento": "evento generico"},
        {"data_nomeada": "data generica"},
        {"convidados": 40},
        {"formato": FormatoEvento.SENTADO},
        {"nome": "Fulano Ficticio"},
        {"contato": "contato-ficticio"},
    ],
)
def test_campo_presente_sem_confianca_e_e_nb_1(ajuste: dict[str, object]) -> None:
    """K-Nb-11 na família dos dados extraídos."""
    with pytest.raises(ValueError, match="E-Nb-1"):
        canonicalizar_interpretacao(
            entrada(dados_extraidos=DadosExtraidos(**ajuste))  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "ajuste",
    [
        {"confianca_tipo_evento": ALTA},
        {"confianca_data_nomeada": BAIXA},
        {"confianca_convidados": ALTA},
        {"confianca_formato": BAIXA},
        {"confianca_nome": ALTA},
        {"confianca_contato": BAIXA},
    ],
)
def test_confianca_em_campo_ausente_e_e_nb_3(ajuste: dict[str, object]) -> None:
    with pytest.raises(ValueError, match="E-Nb-3"):
        canonicalizar_interpretacao(
            entrada(dados_extraidos=DadosExtraidos(**ajuste))  # type: ignore[arg-type]
        )


def test_campo_ausente_tem_confianca_none() -> None:
    """K-Nb-15."""
    resultado = canonicalizar_interpretacao(entrada())
    dados = resultado.dados_extraidos
    assert dados.tipo_evento is None and dados.confianca_tipo_evento is None
    assert dados.data_nomeada is None and dados.confianca_data_nomeada is None


@pytest.mark.parametrize("valor", [-1, -100, True, False, 3.5, "12"])
def test_convidados_invalido_e_e_nb_8(valor: object) -> None:
    """K-Nb-20 — negativo, `bool` ou não inteiro (N-b-D4)."""
    with pytest.raises(ValueError, match="E-Nb-8"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    convidados=valor, confianca_convidados=ALTA  # type: ignore[arg-type]
                )
            )
        )


def test_convidados_zero_e_valido() -> None:
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(convidados=0, confianca_convidados=ALTA)
        )
    )
    assert resultado.dados_extraidos.convidados == 0


def test_formato_texto_fora_do_vocabulario_e_e_nb_9() -> None:
    """K-Nb-21, primeira metade."""
    with pytest.raises(ValueError, match="E-Nb-9"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    formato="buffet",  # type: ignore[arg-type]
                    confianca_formato=ALTA,
                )
            )
        )


def test_formato_de_outro_dominio_e_e_nb_5() -> None:
    """K-Nb-21, segunda metade."""
    with pytest.raises(ValueError, match="E-Nb-5"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    formato=7,  # type: ignore[arg-type]
                    confianca_formato=ALTA,
                )
            )
        )


@pytest.mark.parametrize("formato", list(FormatoEvento))
def test_formato_aceita_exatamente_sentado_e_coquetel(formato: FormatoEvento) -> None:
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(formato=formato, confianca_formato=ALTA)
        )
    )
    assert resultado.dados_extraidos.formato is formato


def test_formato_evento_e_importado_e_tem_dois_valores() -> None:
    """AJ1-F2: o enum é **reutilizado por import**, não movido nem redeclarado."""
    assert [membro.value for membro in FormatoEvento] == ["sentado", "coquetel"]
    assert FormatoEvento.__module__ == "casa77_sdr.qualification"


def test_tipo_evento_e_data_nao_sofrem_normalizacao_semantica() -> None:
    """N-b-D2 e N-b-D3: texto nominal, zero parsing de calendário."""
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento="  Jantar Sentado  ",
                confianca_tipo_evento=ALTA,
                data_nomeada="sabado que vem",
                confianca_data_nomeada=ALTA,
            )
        )
    )
    assert resultado.dados_extraidos.tipo_evento == "  Jantar Sentado  "
    assert resultado.dados_extraidos.data_nomeada == "sabado que vem"


# --------------------------------------------------------------------------
# G. Correções (N-b-C1–N-b-C5)
# --------------------------------------------------------------------------


def test_correcao_interpretada_tem_exatamente_tres_campos() -> None:
    nomes = [campo.name for campo in dataclasses.fields(CorrecaoInterpretada)]
    assert nomes == ["campo", "valor_novo", "confianca"]


def test_correcao_coerente_e_valida() -> None:
    """K-Nb-32 — a etapa 4 **relata** e não grava."""
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(convidados=50, confianca_convidados=ALTA),
            correcoes=(CorrecaoInterpretada("convidados", 50, ALTA),),
        )
    )
    assert resultado.correcoes == (CorrecaoInterpretada("convidados", 50, ALTA),)


@pytest.mark.parametrize(
    "correcao",
    [
        CorrecaoInterpretada("data_nomeada", "outra data", ALTA),  # campo ausente
        CorrecaoInterpretada("convidados", 99, ALTA),  # valor divergente
        CorrecaoInterpretada("convidados", 50, BAIXA),  # confiança divergente
    ],
)
def test_correcao_divergente_e_e_nb_17(correcao: CorrecaoInterpretada) -> None:
    """K-Nb-33."""
    with pytest.raises(ValueError, match="E-Nb-17"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    convidados=50, confianca_convidados=ALTA
                ),
                correcoes=(correcao,),
            )
        )


def test_campo_repetido_em_correcoes_e_e_nb_7() -> None:
    with pytest.raises(ValueError, match="E-Nb-7"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    convidados=50, confianca_convidados=ALTA
                ),
                correcoes=(
                    CorrecaoInterpretada("convidados", 50, ALTA),
                    CorrecaoInterpretada("convidados", 50, ALTA),
                ),
            )
        )


def test_correcao_com_identificador_de_campo_invalido_e_e_nb_5() -> None:
    with pytest.raises(ValueError, match="E-Nb-5"):
        canonicalizar_interpretacao(
            entrada(
                correcoes=(
                    CorrecaoInterpretada("campo_inexistente", "valor generico", ALTA),
                )
            )
        )


def test_correcao_nao_carrega_valor_anterior() -> None:
    """N-b-C3."""
    nomes = {campo.name for campo in dataclasses.fields(CorrecaoInterpretada)}
    assert "valor_anterior" not in nomes


# --------------------------------------------------------------------------
# H. Perguntas comerciais (N-b-Q1–N-b-Q6)
# --------------------------------------------------------------------------


def test_pergunta_comercial_tem_dois_campos() -> None:
    assert [campo.name for campo in dataclasses.fields(PerguntaComercial)] == [
        "texto",
        "confianca",
    ]


def test_pergunta_alta_e_efetiva() -> None:
    """K-Nb-23."""
    resultado = canonicalizar_interpretacao(
        entrada(perguntas_comerciais=(PerguntaComercial("pergunta generica", ALTA),))
    )
    assert confianca_de(resultado, IntencaoConversacional.PERGUNTA_COMERCIAL) is ALTA


def test_pergunta_baixa_preserva_texto_e_deriva_baixa() -> None:
    """K-Nb-24 — texto preservado para diagnóstico, não efetivo."""
    resultado = canonicalizar_interpretacao(
        entrada(perguntas_comerciais=(PerguntaComercial("pergunta generica", BAIXA),))
    )
    assert resultado.perguntas_comerciais[0].texto == "pergunta generica"
    assert confianca_de(resultado, IntencaoConversacional.PERGUNTA_COMERCIAL) is BAIXA


def test_pergunta_mista_deriva_alta() -> None:
    """K-Nb-25."""
    resultado = canonicalizar_interpretacao(
        entrada(
            perguntas_comerciais=(
                PerguntaComercial("pergunta generica a", BAIXA),
                PerguntaComercial("pergunta generica b", ALTA),
            )
        )
    )
    assert confianca_de(resultado, IntencaoConversacional.PERGUNTA_COMERCIAL) is ALTA


def test_pergunta_sem_confianca_e_e_nb_1() -> None:
    with pytest.raises(ValueError, match="E-Nb-1"):
        canonicalizar_interpretacao(
            entrada(perguntas_comerciais=(PerguntaComercial("pergunta generica", None),))
        )


def test_confianca_declarada_sem_valor_correspondente_e_e_nb_2() -> None:
    with pytest.raises(ValueError, match="E-Nb-2"):
        canonicalizar_interpretacao(
            entrada(perguntas_comerciais=(PerguntaComercial(None, ALTA),))
        )


# --------------------------------------------------------------------------
# I. Pedido de humano (N-b-PH1–N-b-PH6)
# --------------------------------------------------------------------------


def test_pedido_de_humano_alta_e_sinal_efetivo() -> None:
    """K-Nb-28 — quem emite `E18` continua sendo o `DetectorHandoff`."""
    resultado = canonicalizar_interpretacao(
        entrada(pedido_de_humano=True, confianca_pedido_de_humano=ALTA)
    )
    assert resultado.pedido_de_humano is True
    assert confianca_de(resultado, IntencaoConversacional.PEDIDO_DE_HUMANO) is ALTA


def test_pedido_de_humano_baixa_permanece_sinal_efetivo() -> None:
    """K-Nb-29 — exceção única de N-b-PH3/N-b-PH4; não cria `E18` aqui."""
    resultado = canonicalizar_interpretacao(
        entrada(pedido_de_humano=True, confianca_pedido_de_humano=BAIXA)
    )
    assert resultado.pedido_de_humano is True
    assert confianca_de(resultado, IntencaoConversacional.PEDIDO_DE_HUMANO) is BAIXA
    # A exceção **não** atravessa para a projeção de identidade.
    projecao = projetar_para_identidade(resultado)
    assert "pedido" not in str(projecao)


def test_pedido_de_humano_falso_com_confianca_e_e_nb_3() -> None:
    """K-Nb-30."""
    with pytest.raises(ValueError, match="E-Nb-3"):
        canonicalizar_interpretacao(
            entrada(pedido_de_humano=False, confianca_pedido_de_humano=ALTA)
        )


def test_pedido_de_humano_verdadeiro_sem_confianca_e_e_nb_1() -> None:
    with pytest.raises(ValueError, match="E-Nb-1"):
        canonicalizar_interpretacao(
            entrada(pedido_de_humano=True, confianca_pedido_de_humano=None)
        )


def test_pedido_de_humano_falso_tem_confianca_none() -> None:
    resultado = canonicalizar_interpretacao(entrada())
    assert resultado.pedido_de_humano is False
    assert resultado.confianca_pedido_de_humano is None


# --------------------------------------------------------------------------
# J. Referências ao evento anterior (N-b-R1–N-b-R5)
# --------------------------------------------------------------------------


def test_referencia_tem_dois_campos() -> None:
    assert [
        campo.name for campo in dataclasses.fields(ReferenciaAoEventoAnterior)
    ] == ["texto", "confianca"]


def test_referencia_unica_alta() -> None:
    """K-Nb-7."""
    projecao = projetar_para_identidade(
        canonicalizar_interpretacao(
            entrada(
                referencias_evento_anterior=(
                    ReferenciaAoEventoAnterior("referencia generica", ALTA),
                )
            )
        )
    )
    assert projecao.referencia_evento_anterior is ReferenciaEventoAnterior.COM_REFERENCIA
    assert projecao.confianca_referencia is ALTA


def test_referencias_mistas_agregam_alta() -> None:
    """K-Nb-8."""
    projecao = projetar_para_identidade(
        canonicalizar_interpretacao(
            entrada(
                referencias_evento_anterior=(
                    ReferenciaAoEventoAnterior("referencia generica a", ALTA),
                    ReferenciaAoEventoAnterior("referencia generica b", BAIXA),
                )
            )
        )
    )
    assert projecao.confianca_referencia is ALTA


def test_referencias_todas_baixas_agregam_baixa() -> None:
    """K-Nb-9 — o consumidor é quem aplica C3."""
    projecao = projetar_para_identidade(
        canonicalizar_interpretacao(
            entrada(
                referencias_evento_anterior=(
                    ReferenciaAoEventoAnterior("referencia generica a", BAIXA),
                    ReferenciaAoEventoAnterior("referencia generica b", BAIXA),
                )
            )
        )
    )
    assert projecao.referencia_evento_anterior is ReferenciaEventoAnterior.COM_REFERENCIA
    assert projecao.confianca_referencia is BAIXA


def test_referencias_vazias_produzem_sem_referencia() -> None:
    """K-Nb-10."""
    projecao = projetar_para_identidade(canonicalizar_interpretacao(entrada()))
    assert projecao.referencia_evento_anterior is ReferenciaEventoAnterior.SEM_REFERENCIA
    assert projecao.confianca_referencia is None


def test_referencia_sem_confianca_e_e_nb_1() -> None:
    """K-Nb-11."""
    with pytest.raises(ValueError, match="E-Nb-1"):
        canonicalizar_interpretacao(
            entrada(
                referencias_evento_anterior=(
                    ReferenciaAoEventoAnterior("referencia generica", None),
                )
            )
        )


# --------------------------------------------------------------------------
# K. Trechos ambíguos (N-b-T1–N-b-T5)
# --------------------------------------------------------------------------


def test_trecho_ambiguo_canonico_tem_apenas_texto() -> None:
    """N-b-T5: a estrutura canônica sequer possui campo de confiança."""
    nomes = [campo.name for campo in dataclasses.fields(TrechoAmbiguo)]
    assert nomes == ["texto"]
    assert "confianca" not in nomes


def test_confianca_em_trecho_ambiguo_e_e_nb_3() -> None:
    """K-Nb-34, primeira metade."""
    with pytest.raises(ValueError, match="E-Nb-3"):
        canonicalizar_interpretacao(
            entrada(
                trechos_ambiguos=(TrechoAmbiguoRecebido("trecho generico", ALTA),)
            )
        )


def test_trecho_ambiguo_valido_vira_canonico_sem_confianca() -> None:
    resultado = canonicalizar_interpretacao(
        entrada(trechos_ambiguos=(TrechoAmbiguoRecebido("trecho generico"),))
    )
    assert resultado.trechos_ambiguos == (TrechoAmbiguo("trecho generico"),)


def test_trecho_ambiguo_nao_atravessa_a_projecao() -> None:
    """N-b-T3."""
    resultado = canonicalizar_interpretacao(
        entrada(trechos_ambiguos=(TrechoAmbiguoRecebido("trecho generico"),))
    )
    assert "trecho generico" not in str(projetar_para_identidade(resultado))


@pytest.mark.parametrize("texto", ["", "   ", "\t\n"])
@pytest.mark.parametrize(
    "categoria",
    ["perguntas_comerciais", "referencias_evento_anterior", "trechos_ambiguos"],
)
def test_texto_vazio_ou_em_branco_e_e_nb_10(texto: str, categoria: str) -> None:
    """K-Nb-12."""
    construtores = {
        "perguntas_comerciais": lambda: (PerguntaComercial(texto, ALTA),),
        "referencias_evento_anterior": lambda: (
            ReferenciaAoEventoAnterior(texto, ALTA),
        ),
        "trechos_ambiguos": lambda: (TrechoAmbiguoRecebido(texto),),
    }
    with pytest.raises(ValueError, match="E-Nb-10"):
        canonicalizar_interpretacao(entrada(**{categoria: construtores[categoria]()}))


# --------------------------------------------------------------------------
# L. Confiança global (N-b-CG1–N-b-CG4)
# --------------------------------------------------------------------------


def test_confianca_global_ausente_e_e_nb_4() -> None:
    """K-Nb-36."""
    with pytest.raises(ValueError, match="E-Nb-4"):
        canonicalizar_interpretacao(entrada(confianca_global=None))


def test_confianca_global_divergente_nao_tem_efeito() -> None:
    """K-Nb-35 — a confiança do campo prevalece; sem erro, sem alerta."""
    resultado = canonicalizar_interpretacao(
        entrada(
            confianca_global=BAIXA,
            dados_extraidos=DadosExtraidos(
                tipo_evento="evento generico", confianca_tipo_evento=ALTA
            ),
        )
    )
    assert resultado.confianca_global is BAIXA
    assert (
        confianca_de(resultado, IntencaoConversacional.TIPO_EVENTO_INFORMADO) is ALTA
    )


def test_confianca_global_nao_participa_da_projecao() -> None:
    """N-b-CG2."""
    alta = canonicalizar_interpretacao(entrada(confianca_global=ALTA))
    baixa = canonicalizar_interpretacao(entrada(confianca_global=BAIXA))
    assert projetar_para_identidade(alta) == projetar_para_identidade(baixa)


# --------------------------------------------------------------------------
# M. Intenções autônomas
# --------------------------------------------------------------------------


@pytest.mark.parametrize("codigo", sorted(interpretation._CODIGOS_AUTONOMOS, key=str))
@pytest.mark.parametrize("confianca", [ALTA, BAIXA])
def test_intencao_autonoma_valida_e_transportada(
    codigo: IntencaoConversacional, confianca: Confianca
) -> None:
    resultado = canonicalizar_interpretacao(
        entrada(intencoes_autonomas=autonoma(codigo, confianca))
    )
    assert confianca_de(resultado, codigo) is confianca


@pytest.mark.parametrize("codigo", sorted(interpretation._CODIGOS_AUTONOMOS, key=str))
def test_intencao_autonoma_sem_confianca_e_e_nb_1(
    codigo: IntencaoConversacional,
) -> None:
    with pytest.raises(ValueError, match="E-Nb-1"):
        canonicalizar_interpretacao(entrada(intencoes_autonomas=autonoma(codigo, None)))


def test_intencao_autonoma_duplicada_e_e_nb_6() -> None:
    """`E-Nb-6` recebível: **somente** duplicação de intenção autônoma."""
    with pytest.raises(ValueError, match="E-Nb-6"):
        canonicalizar_interpretacao(
            entrada(
                intencoes_autonomas=(
                    IntencaoAutonomaRecebida(
                        IntencaoConversacional.INTERESSE_EM_VISITA, ALTA
                    ),
                    IntencaoAutonomaRecebida(
                        IntencaoConversacional.INTERESSE_EM_VISITA, BAIXA
                    ),
                )
            )
        )


def test_continuidade_e_evento_novo_simultaneos_e_e_nb_18() -> None:
    """K-Nb-6 — mutuamente exclusivas; nenhuma projeção é produzida."""
    with pytest.raises(ValueError, match="E-Nb-18"):
        canonicalizar_interpretacao(
            entrada(
                intencoes_autonomas=(
                    IntencaoAutonomaRecebida(
                        IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA, ALTA
                    ),
                    IntencaoAutonomaRecebida(
                        IntencaoConversacional.EVENTO_NOVO_DECLARADO, ALTA
                    ),
                )
            )
        )


def test_multiplas_intencoes_autonomas_sao_todas_relatadas() -> None:
    """K-Nb-37 — nenhuma precedência é criada e nenhuma vira `Exx`."""
    resultado = canonicalizar_interpretacao(
        entrada(
            intencoes_autonomas=(
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.INTERESSE_EM_VISITA, ALTA
                ),
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.EXCECAO_SOLICITADA, BAIXA
                ),
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA
                ),
            )
        )
    )
    assert {item.codigo for item in resultado.intencoes_detectadas} == {
        IntencaoConversacional.INTERESSE_EM_VISITA,
        IntencaoConversacional.EXCECAO_SOLICITADA,
        IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE,
    }


def test_codigo_fora_do_enum_e_e_nb_5() -> None:
    with pytest.raises(ValueError, match="E-Nb-5"):
        canonicalizar_interpretacao(
            entrada(
                intencoes_autonomas=(
                    IntencaoAutonomaRecebida("codigo_inexistente", ALTA),  # type: ignore[arg-type]
                )
            )
        )


# --------------------------------------------------------------------------
# N. Projeção para a identidade (N-b-K1–N-b-K8) — K-Nb-1..K-Nb-5, K-Nb-40
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("codigo", "confianca", "esperada"),
    [
        (
            IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA,
            ALTA,
            IntencaoIdentidade.CONTINUIDADE_DECLARADA,
        ),
        (
            IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA,
            BAIXA,
            IntencaoIdentidade.NAO_DISCRIMINANTE,
        ),
        (
            IntencaoConversacional.EVENTO_NOVO_DECLARADO,
            ALTA,
            IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
        ),
        (
            IntencaoConversacional.EVENTO_NOVO_DECLARADO,
            BAIXA,
            IntencaoIdentidade.NAO_DISCRIMINANTE,
        ),
    ],
)
def test_intencao_identidade_k_nb_1_a_4(
    codigo: IntencaoConversacional,
    confianca: Confianca,
    esperada: IntencaoIdentidade,
) -> None:
    projecao = projetar_para_identidade(
        canonicalizar_interpretacao(entrada(intencoes_autonomas=autonoma(codigo, confianca)))
    )
    assert projecao.intencao_identidade is esperada


def test_sem_intencoes_de_identidade_e_nao_discriminante() -> None:
    """K-Nb-5."""
    projecao = projetar_para_identidade(canonicalizar_interpretacao(entrada()))
    assert projecao.intencao_identidade is IntencaoIdentidade.NAO_DISCRIMINANTE


@pytest.mark.parametrize("confianca", [ALTA, BAIXA])
def test_tipo_e_data_sao_transportados_inclusive_com_baixa(
    confianca: Confianca,
) -> None:
    """K-Nb-13 e K-Nb-14 — a derivação **não** aplica C3."""
    projecao = projetar_para_identidade(
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    tipo_evento="evento generico",
                    confianca_tipo_evento=confianca,
                    data_nomeada="data generica",
                    confianca_data_nomeada=confianca,
                )
            )
        )
    )
    assert projecao.tipo_evento_extraido == "evento generico"
    assert projecao.confianca_tipo is confianca
    assert projecao.data_nomeada_extraida == "data generica"
    assert projecao.confianca_data is confianca


def test_tipo_e_data_ausentes_projetam_none() -> None:
    """K-Nb-15."""
    projecao = projetar_para_identidade(canonicalizar_interpretacao(entrada()))
    assert projecao.tipo_evento_extraido is None and projecao.confianca_tipo is None
    assert projecao.data_nomeada_extraida is None and projecao.confianca_data is None


def test_projecao_tem_exatamente_sete_campos() -> None:
    """K-Nb-40, primeira metade."""
    assert len(dataclasses.fields(ProjecaoInterpretacao)) == 7


def test_projecao_nao_carrega_pii_nem_texto_conversacional() -> None:
    """K-Nb-19, K-Nb-22 e K-Nb-40 — N-b-K8, lista fechada do que não atravessa."""
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento="evento generico",
                confianca_tipo_evento=ALTA,
                convidados=80,
                confianca_convidados=ALTA,
                formato=FormatoEvento.COQUETEL,
                confianca_formato=ALTA,
                nome="Fulano Ficticio",
                confianca_nome=ALTA,
                contato="contato-ficticio",
                confianca_contato=ALTA,
            ),
            perguntas_comerciais=(PerguntaComercial("pergunta generica", ALTA),),
            pedido_de_humano=True,
            confianca_pedido_de_humano=ALTA,
            trechos_ambiguos=(TrechoAmbiguoRecebido("trecho generico"),),
        )
    )
    texto = str(projetar_para_identidade(resultado))
    for proibido in (
        "Fulano Ficticio",
        "contato-ficticio",
        "pergunta generica",
        "trecho generico",
        "80",
        "coquetel",
    ):
        assert proibido not in texto


def test_convidados_e_formato_nao_atravessam() -> None:
    """K-Nb-19 — relatados na `Interpretacao`, ausentes da projeção."""
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                convidados=25,
                confianca_convidados=ALTA,
                formato=FormatoEvento.SENTADO,
                confianca_formato=ALTA,
            )
        )
    )
    assert resultado.dados_extraidos.convidados == 25
    nomes = {campo.name for campo in dataclasses.fields(ProjecaoInterpretacao)}
    assert nomes.isdisjoint({"convidados", "formato", "nome", "contato"})


def test_projecao_exige_interpretacao_canonica() -> None:
    """K-Nb-39, parte local: a projeção não aceita ausência nem objeto alheio."""
    with pytest.raises(TypeError):
        projetar_para_identidade(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        projetar_para_identidade(entrada())  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# O. Condição 5 (N-b-CD1–N-b-CD4) — K-Nb-38 e a parte local de K-Nb-39
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("intencoes", "esperado"),
    [
        (
            autonoma(IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA),
            True,
        ),
        (
            autonoma(IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, BAIXA),
            False,
        ),
        ((), False),
    ],
)
def test_condicao_5_k_nb_38(
    intencoes: tuple[IntencaoAutonomaRecebida, ...], esperado: bool
) -> None:
    resultado = canonicalizar_interpretacao(entrada(intencoes_autonomas=intencoes))
    assert decidir_interesse_confirmar_disponibilidade(resultado) is esperado


def test_condicao_5_sem_interpretacao_e_none() -> None:
    """K-Nb-39, parte local — N-b-CD4 / N-b-M6."""
    assert decidir_interesse_confirmar_disponibilidade(None) is None


def test_ausencia_de_interpretacao_nao_equivale_a_interpretacao_vazia() -> None:
    """K-Nb-39, parte local — N-b-G8.

    A parte **futura** de K-Nb-39 — etapa 5 não executar, `MaquinaEstados` não
    ser chamada, nada ser gravado, alertas e coordenação do modo degradado —
    pertence à orquestração, que não existe. **Não** é coberta aqui.
    """
    vazia = canonicalizar_interpretacao(entrada())
    assert decidir_interesse_confirmar_disponibilidade(vazia) is False
    assert decidir_interesse_confirmar_disponibilidade(None) is None
    assert decidir_interesse_confirmar_disponibilidade(
        vazia
    ) is not decidir_interesse_confirmar_disponibilidade(None)


def test_condicao_5_rejeita_valor_alheio() -> None:
    with pytest.raises(TypeError):
        decidir_interesse_confirmar_disponibilidade(entrada())  # type: ignore[arg-type]


def _codigo_do_modulo_sem_docstrings() -> str:
    """Código efetivo do módulo — sem docstrings e sem comentários.

    A prova estrutural incide sobre o que o módulo **faz**, não sobre o texto
    que explica o que ele deliberadamente **não** faz.
    """
    arvore = ast.parse(MODULO_INTERPRETACAO.read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            corpo = no.body
            if (
                corpo
                and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)
            ):
                no.body = corpo[1:] or [ast.Pass()]
    return ast.unparse(arvore)


def test_condicao_5_e_a_unica_condicao_produzida() -> None:
    """N-b-G3 — as condições 2, 4 e 8 continuam NÃO ATRIBUÍDAS."""
    codigo = _codigo_do_modulo_sem_docstrings()
    for proibida in (
        "pendencia_impeditiva",
        "resposta_aprovada_disponivel",
        "motivo_encerramento",
        "insumo_qualificacao_atualizado",
        "motivos_handoff",
        "calendario_integrado",
        "CondicoesCiclo",
    ):
        assert proibida not in codigo
    assert "interesse_confirmar_disponibilidade" in codigo


# --------------------------------------------------------------------------
# P. E-Nb-19 — prova estrutural do módulo
# --------------------------------------------------------------------------


def test_superficie_publica_e_exatamente_a_declarada() -> None:
    assert interpretation.__all__ == [
        "IntencaoConversacional",
        "DadosExtraidos",
        "CorrecaoInterpretada",
        "PerguntaComercial",
        "ReferenciaAoEventoAnterior",
        "TrechoAmbiguo",
        "TrechoAmbiguoRecebido",
        "IntencaoAutonomaRecebida",
        "IntencaoDetectada",
        "EntradaInterpretacao",
        "Interpretacao",
        "canonicalizar_interpretacao",
        "projetar_para_identidade",
        "decidir_interesse_confirmar_disponibilidade",
    ]


def test_nenhum_nome_publico_definido_fora_de_all() -> None:
    definidos = {
        nome
        for nome, objeto in vars(interpretation).items()
        if not nome.startswith("_")
        and getattr(objeto, "__module__", None) == "casa77_sdr.interpretation"
    }
    assert definidos == set(interpretation.__all__)


def test_ha_exatamente_tres_produtores_publicos() -> None:
    funcoes = [
        nome
        for nome in interpretation.__all__
        if inspect.isfunction(getattr(interpretation, nome))
    ]
    assert funcoes == [
        "canonicalizar_interpretacao",
        "projetar_para_identidade",
        "decidir_interesse_confirmar_disponibilidade",
    ]


def test_tipos_de_retorno_sao_fechados() -> None:
    retornos = {
        nome: inspect.signature(getattr(interpretation, nome)).return_annotation
        for nome in (
            "canonicalizar_interpretacao",
            "projetar_para_identidade",
            "decidir_interesse_confirmar_disponibilidade",
        )
    }
    assert retornos == {
        "canonicalizar_interpretacao": "Interpretacao",
        "projetar_para_identidade": "ProjecaoInterpretacao",
        "decidir_interesse_confirmar_disponibilidade": "bool | None",
    }


def test_interpretacao_canonica_tem_os_campos_das_oito_categorias() -> None:
    nomes = [campo.name for campo in dataclasses.fields(Interpretacao)]
    assert nomes == [
        "intencoes_detectadas",
        "dados_extraidos",
        "correcoes",
        "perguntas_comerciais",
        "pedido_de_humano",
        "confianca_pedido_de_humano",
        "referencias_evento_anterior",
        "confianca_global",
        "trechos_ambiguos",
    ]


@pytest.mark.parametrize(
    "classe",
    [
        DadosExtraidos,
        CorrecaoInterpretada,
        PerguntaComercial,
        ReferenciaAoEventoAnterior,
        TrechoAmbiguo,
        TrechoAmbiguoRecebido,
        IntencaoAutonomaRecebida,
        IntencaoDetectada,
        EntradaInterpretacao,
        Interpretacao,
    ],
)
def test_estruturas_sao_congeladas(classe: type) -> None:
    assert classe.__dataclass_params__.frozen is True  # type: ignore[attr-defined]


def test_modulo_nao_produz_saidas_de_outras_camadas() -> None:
    """E-Nb-19: o módulo não produz nem representa `Exx`, `Txx`, estado etc."""
    fonte = MODULO_INTERPRETACAO.read_text(encoding="utf-8")
    arvore = ast.parse(fonte)
    definidos = {
        no.name
        for no in ast.walk(arvore)
        if isinstance(no, (ast.ClassDef, ast.FunctionDef))
    }
    proibidos = {
        "Evento",
        "Transicao",
        "Estado",
        "Qualificacao",
        "Violacao",
        "Pendencia",
        "CondicoesCiclo",
        "DecisaoMaquina",
        "RegistroAtendimento",
        "AcaoMaquina",
    }
    assert definidos.isdisjoint(proibidos)
    importados = {
        alias.asname or alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom)
        for alias in no.names
    }
    assert importados.isdisjoint(proibidos)


def test_modulo_e_puro_por_fechamento_de_imports() -> None:
    """Evidência **complementar** de pureza — import não prova `E-Nb-19` sozinho."""
    arvore = ast.parse(MODULO_INTERPRETACAO.read_text(encoding="utf-8"))
    modulos: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom):
            modulos.add(no.module or "")
    assert modulos == {
        "__future__",
        "dataclasses",
        "enum",
        "casa77_sdr.identity",
        "casa77_sdr.qualification",
    }


def test_modulo_nao_e_exportado_no_pacote() -> None:
    import casa77_sdr

    assert "interpretation" not in getattr(casa77_sdr, "__all__", [])


def test_nenhuma_excecao_publica_nova() -> None:
    """AJ1: erros de contrato usam `TypeError`/`ValueError`, sem classe nova."""
    novas = [
        nome
        for nome, objeto in vars(interpretation).items()
        if inspect.isclass(objeto)
        and issubclass(objeto, BaseException)
        and getattr(objeto, "__module__", None) == "casa77_sdr.interpretation"
    ]
    assert novas == []


# --------------------------------------------------------------------------
# Q. Pureza, determinismo e não mutação
# --------------------------------------------------------------------------


def test_canonicalizacao_e_deterministica() -> None:
    caso = entrada(
        dados_extraidos=DadosExtraidos(
            tipo_evento="evento generico", confianca_tipo_evento=ALTA
        ),
        perguntas_comerciais=(PerguntaComercial("pergunta generica", BAIXA),),
        intencoes_autonomas=autonoma(IntencaoConversacional.INTERESSE_EM_VISITA, ALTA),
    )
    primeiro = canonicalizar_interpretacao(caso)
    segundo = canonicalizar_interpretacao(caso)
    assert primeiro == segundo
    assert projetar_para_identidade(primeiro) == projetar_para_identidade(segundo)
    assert decidir_interesse_confirmar_disponibilidade(
        primeiro
    ) == decidir_interesse_confirmar_disponibilidade(segundo)


def test_entrada_nao_e_mutada() -> None:
    caso = entrada(
        dados_extraidos=DadosExtraidos(
            tipo_evento="evento generico", confianca_tipo_evento=ALTA
        ),
        trechos_ambiguos=(TrechoAmbiguoRecebido("trecho generico"),),
    )
    copia = dataclasses.replace(caso)
    canonicalizar_interpretacao(caso)
    assert caso == copia
    assert caso.trechos_ambiguos == (TrechoAmbiguoRecebido("trecho generico"),)


def test_interpretacao_canonica_e_imutavel() -> None:
    resultado = canonicalizar_interpretacao(entrada())
    with pytest.raises(dataclasses.FrozenInstanceError):
        resultado.pedido_de_humano = True  # type: ignore[misc]


@pytest.mark.parametrize(
    "entrada_invalida", [None, "texto", 7, DadosExtraidos(), ()]
)
def test_canonicalizacao_rejeita_entrada_de_outro_tipo(
    entrada_invalida: object,
) -> None:
    with pytest.raises(TypeError):
        canonicalizar_interpretacao(entrada_invalida)  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# R. Invariantes internos — pós-condições verificadas por propriedade
# --------------------------------------------------------------------------


@pytest.mark.parametrize("caso", _combinacoes_para_propriedade())
def test_pos_condicoes_valem_para_toda_interpretacao_canonica(
    caso: EntradaInterpretacao,
) -> None:
    """E-Nb-6 (ramo A1) e E-Nb-11–E-Nb-16 como invariantes, não como recebíveis.

    Numa canonicalização correta eles são **impossíveis por construção**; a
    prova é a bi-implicação valer sempre, e nenhuma entrada externa artificial é
    fabricada para provocá-los (AJ1).
    """
    resultado = canonicalizar_interpretacao(caso)
    presentes = {item.codigo for item in resultado.intencoes_detectadas}
    dados = resultado.dados_extraidos

    # E-Nb-11 / E-Nb-12 — bi-implicação dos pares A–D
    assert (dados.tipo_evento is not None) == (
        IntencaoConversacional.TIPO_EVENTO_INFORMADO in presentes
    )
    assert (dados.data_nomeada is not None) == (
        IntencaoConversacional.DATA_INFORMADA in presentes
    )
    assert (dados.convidados is not None) == (
        IntencaoConversacional.CONVIDADOS_INFORMADOS in presentes
    )
    assert (dados.formato is not None) == (
        IntencaoConversacional.FORMATO_INFORMADO in presentes
    )
    # E-Nb-14 / E-Nb-15 — par E
    assert bool(resultado.perguntas_comerciais) == (
        IntencaoConversacional.PERGUNTA_COMERCIAL in presentes
    )
    # E-Nb-16 — par F
    assert resultado.pedido_de_humano == (
        IntencaoConversacional.PEDIDO_DE_HUMANO in presentes
    )
    # E-Nb-6 no ramo A1 — sem repetição
    codigos = [item.codigo for item in resultado.intencoes_detectadas]
    assert len(codigos) == len(set(codigos))


def test_intencao_detectada_sempre_tem_confianca_nao_nula() -> None:
    for caso in _combinacoes_para_propriedade():
        resultado = canonicalizar_interpretacao(caso)
        for item in resultado.intencoes_detectadas:
            assert isinstance(item, IntencaoDetectada)
            assert item.confianca in (ALTA, BAIXA)


# --------------------------------------------------------------------------
# T. Canonicidade exigida dos consumidores — `Interpretacao` é pública
# --------------------------------------------------------------------------
#
# `Interpretacao` pode ser construída diretamente. `isinstance` prova o tipo,
# **não** a validade: uma instância inválida jamais pode produzir projeção nem
# condição derivada. O que os consumidores exigem é **validade estrutural**, não
# proveniência — uma `Interpretacao` montada à mão que satisfaça o contrato é
# aceita, e não existe token de fábrica nem marca de origem.
#
# Complemento de K-Nb-39: "Interpretacao canônica válida" passa a ser
# efetivamente verificado.


def interpretacao_manual(**ajustes: object) -> Interpretacao:
    """Monta uma `Interpretacao` **sem passar pela canonicalização**."""
    base: dict[str, object] = {
        "intencoes_detectadas": (),
        "dados_extraidos": DadosExtraidos(),
        "correcoes": (),
        "perguntas_comerciais": (),
        "pedido_de_humano": False,
        "confianca_pedido_de_humano": None,
        "referencias_evento_anterior": (),
        "confianca_global": ALTA,
        "trechos_ambiguos": (),
    }
    base.update(ajustes)
    return Interpretacao(**base)  # type: ignore[arg-type]


CONSUMIDORES = [projetar_para_identidade, decidir_interesse_confirmar_disponibilidade]


def test_interpretacao_manual_valida_e_aceita_pelos_consumidores() -> None:
    """Validade, não proveniência: montada à mão porém canônica → aceita."""
    valida = interpretacao_manual(
        dados_extraidos=DadosExtraidos(
            tipo_evento="evento generico", confianca_tipo_evento=ALTA
        ),
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.TIPO_EVENTO_INFORMADO, ALTA),
            IntencaoDetectada(
                IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA
            ),
        ),
    )
    projecao = projetar_para_identidade(valida)
    assert projecao.tipo_evento_extraido == "evento generico"
    assert decidir_interesse_confirmar_disponibilidade(valida) is True


def test_interpretacao_manual_valida_equivale_a_canonicalizada() -> None:
    canonica = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento="evento generico", confianca_tipo_evento=ALTA
            )
        )
    )
    manual = interpretacao_manual(
        dados_extraidos=DadosExtraidos(
            tipo_evento="evento generico", confianca_tipo_evento=ALTA
        ),
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.TIPO_EVENTO_INFORMADO, ALTA),
        ),
    )
    assert projetar_para_identidade(manual) == projetar_para_identidade(canonica)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_mutua_exclusao_violada_e_e_nb_18(consumidor) -> None:
    """K-Nb-6 pela via manual: `E-Nb-18` bloqueia **antes** de qualquer derivação.

    Antes desta verificação a instância atravessava e a ordem defensiva de
    N-b-K1 escolhia `NOVO_EVENTO_DECLARADO` — o que violaria E-Nb-18 e AJ1.
    """
    invalida = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(
                IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA, ALTA
            ),
            IntencaoDetectada(IntencaoConversacional.EVENTO_NOVO_DECLARADO, ALTA),
        )
    )
    with pytest.raises(ValueError, match="E-Nb-18"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_a1_sem_payload_e_e_nb_12(consumidor) -> None:
    invalida = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.TIPO_EVENTO_INFORMADO, ALTA),
        )
    )
    with pytest.raises(ValueError, match="E-Nb-12"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_payload_sem_a1_e_e_nb_11(consumidor) -> None:
    invalida = interpretacao_manual(
        dados_extraidos=DadosExtraidos(
            tipo_evento="evento generico", confianca_tipo_evento=ALTA
        )
    )
    with pytest.raises(ValueError, match="E-Nb-11"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_confianca_a1_divergente_e_e_nb_13(consumidor) -> None:
    """`E-Nb-13` como invariante: payload `ALTA`, código derivado `BAIXA`."""
    invalida = interpretacao_manual(
        dados_extraidos=DadosExtraidos(
            tipo_evento="evento generico", confianca_tipo_evento=ALTA
        ),
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.TIPO_EVENTO_INFORMADO, BAIXA),
        ),
    )
    with pytest.raises(ValueError, match="E-Nb-13"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_agregacao_de_perguntas_divergente_e_e_nb_13(consumidor) -> None:
    invalida = interpretacao_manual(
        perguntas_comerciais=(
            PerguntaComercial("pergunta generica a", ALTA),
            PerguntaComercial("pergunta generica b", BAIXA),
        ),
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.PERGUNTA_COMERCIAL, BAIXA),
        ),
    )
    with pytest.raises(ValueError, match="E-Nb-13"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_referencia_sem_confianca_nao_atravessa(consumidor) -> None:
    invalida = interpretacao_manual(
        referencias_evento_anterior=(
            ReferenciaAoEventoAnterior("referencia generica", None),
        )
    )
    with pytest.raises(ValueError, match="E-Nb-1"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_referencia_de_texto_vazio_nao_atravessa(consumidor) -> None:
    invalida = interpretacao_manual(
        referencias_evento_anterior=(ReferenciaAoEventoAnterior("   ", ALTA),)
    )
    with pytest.raises(ValueError, match="E-Nb-10"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_confianca_autonoma_invalida_nao_atravessa(consumidor) -> None:
    """Confiança que não é `Confianca` não alimenta projeção nem condição 5.

    **Tipo** errado é erro de programa (`TypeError`); **ausência** de confiança
    é erro de contrato (`E-Nb-1`) — ver os testes de tipagem adiante.
    """
    invalida = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(
                IntencaoConversacional.INTERESSE_EM_VISITA,
                "alta",  # type: ignore[arg-type]
            ),
        )
    )
    with pytest.raises(TypeError):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_codigo_repetido_nao_atravessa(consumidor) -> None:
    invalida = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.INTERESSE_EM_VISITA, ALTA),
            IntencaoDetectada(IntencaoConversacional.INTERESSE_EM_VISITA, ALTA),
        )
    )
    with pytest.raises(ValueError, match="E-Nb-6"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_fora_da_ordem_canonica_e_aceita(consumidor) -> None:
    """A ordem é **apenas de auditoria** (AJ1-A1e): não é exigida de quem consome.

    Exigi-la transformaria a ordem em regra semântica — exatamente o que AJ1
    proíbe. `E-Nb-6` volta a significar **somente código repetido**.
    """
    fora_de_ordem = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.EVENTO_NOVO_DECLARADO, ALTA),
            IntencaoDetectada(IntencaoConversacional.INTERESSE_EM_VISITA, ALTA),
        )
    )
    consumidor(fora_de_ordem)  # não levanta


def _permutacoes_equivalentes() -> tuple[Interpretacao, Interpretacao]:
    itens = (
        IntencaoDetectada(IntencaoConversacional.TIPO_EVENTO_INFORMADO, ALTA),
        IntencaoDetectada(IntencaoConversacional.INTERESSE_EM_VISITA, BAIXA),
        IntencaoDetectada(
            IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE, ALTA
        ),
        IntencaoDetectada(
            IntencaoConversacional.CONTINUIDADE_DE_EVENTO_DECLARADA, ALTA
        ),
    )
    dados = DadosExtraidos(tipo_evento="evento generico", confianca_tipo_evento=ALTA)
    canonica = interpretacao_manual(dados_extraidos=dados, intencoes_detectadas=itens)
    permutada = interpretacao_manual(
        dados_extraidos=dados, intencoes_detectadas=tuple(reversed(itens))
    )
    return canonica, permutada


def test_duas_permutacoes_validas_sao_semanticamente_equivalentes() -> None:
    """Mesma projeção e mesma condição 5 sob ordens distintas."""
    canonica, permutada = _permutacoes_equivalentes()
    assert projetar_para_identidade(canonica) == projetar_para_identidade(permutada)
    assert decidir_interesse_confirmar_disponibilidade(
        canonica
    ) == decidir_interesse_confirmar_disponibilidade(permutada)
    assert (
        projetar_para_identidade(permutada).intencao_identidade
        is IntencaoIdentidade.CONTINUIDADE_DECLARADA
    )
    assert decidir_interesse_confirmar_disponibilidade(permutada) is True


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_ambas_as_permutacoes_sao_aceitas(consumidor) -> None:
    for candidata in _permutacoes_equivalentes():
        consumidor(candidata)  # não levanta


def test_canonicalizacao_continua_produzindo_ordem_canonica() -> None:
    """A produção da ordem permanece determinística, mesmo sem ser exigida."""
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento="evento generico", confianca_tipo_evento=ALTA
            ),
            intencoes_autonomas=(
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.EVENTO_NOVO_DECLARADO, ALTA
                ),
                IntencaoAutonomaRecebida(
                    IntencaoConversacional.INTERESSE_EM_VISITA, ALTA
                ),
            ),
        )
    )
    posicao = {codigo: i for i, codigo in enumerate(IntencaoConversacional)}
    indices = [posicao[item.codigo] for item in resultado.intencoes_detectadas]
    assert indices == sorted(indices)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_e_nb_6_significa_somente_codigo_repetido(consumidor) -> None:
    """Duplicata continua `E-Nb-6`; ordem diferente **não** é `E-Nb-6`."""
    duplicada = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.INTERESSE_EM_VISITA, ALTA),
            IntencaoDetectada(IntencaoConversacional.INTERESSE_EM_VISITA, BAIXA),
        )
    )
    with pytest.raises(ValueError, match="E-Nb-6"):
        consumidor(duplicada)


# --- Tipagem: ausência é erro de contrato; tipo errado é erro de programa ---


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_confianca_global_none_e_e_nb_4(consumidor) -> None:
    invalida = interpretacao_manual(confianca_global=None)
    with pytest.raises(ValueError, match="E-Nb-4"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_confianca_global_de_tipo_errado_e_type_error(consumidor) -> None:
    invalida = interpretacao_manual(confianca_global="alta")
    with pytest.raises(TypeError):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_confianca_pedido_de_humano_de_tipo_errado_e_type_error(consumidor) -> None:
    invalida = interpretacao_manual(
        pedido_de_humano=True, confianca_pedido_de_humano="alta"
    )
    with pytest.raises(TypeError):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_intencao_detectada_com_confianca_none_e_e_nb_1(consumidor) -> None:
    invalida = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.INTERESSE_EM_VISITA, None),  # type: ignore[arg-type]
        )
    )
    with pytest.raises(ValueError, match="E-Nb-1"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_intencao_detectada_com_confianca_de_tipo_errado_e_type_error(
    consumidor,
) -> None:
    invalida = interpretacao_manual(
        intencoes_detectadas=(
            IntencaoDetectada(
                IntencaoConversacional.INTERESSE_EM_VISITA,
                "alta",  # type: ignore[arg-type]
            ),
        )
    )
    with pytest.raises(TypeError):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_pedido_de_humano_incoerente_nao_atravessa(consumidor) -> None:
    invalida = interpretacao_manual(
        pedido_de_humano=True, confianca_pedido_de_humano=None
    )
    with pytest.raises(ValueError, match="E-Nb-1"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_correcao_incoerente_nao_atravessa(consumidor) -> None:
    invalida = interpretacao_manual(
        correcoes=(CorrecaoInterpretada("convidados", 10, ALTA),)
    )
    with pytest.raises(ValueError, match="E-Nb-17"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_confianca_global_invalida_nao_atravessa(consumidor) -> None:
    invalida = interpretacao_manual(confianca_global=None)
    with pytest.raises(ValueError, match="E-Nb-4"):
        consumidor(invalida)


@pytest.mark.parametrize("consumidor", CONSUMIDORES)
def test_manual_com_convidados_invalido_nao_atravessa(consumidor) -> None:
    invalida = interpretacao_manual(
        dados_extraidos=DadosExtraidos(
            convidados=-5, confianca_convidados=ALTA  # type: ignore[arg-type]
        ),
        intencoes_detectadas=(
            IntencaoDetectada(IntencaoConversacional.CONVIDADOS_INFORMADOS, ALTA),
        ),
    )
    with pytest.raises(ValueError, match="E-Nb-8"):
        consumidor(invalida)


def test_validacao_de_canonicidade_nao_entra_na_superficie_publica() -> None:
    assert "_validar_interpretacao_canonica" not in interpretation.__all__
    assert hasattr(interpretation, "_validar_interpretacao_canonica")


def test_nenhum_token_de_fabrica_ou_marca_de_origem_foi_criado() -> None:
    """A exigência é **validade**, não proveniência."""
    nomes = {campo.name for campo in dataclasses.fields(Interpretacao)}
    assert nomes.isdisjoint({"_origem", "origem", "_token", "token", "_canonica"})


# --------------------------------------------------------------------------
# U. E-Nb-10 permanece fechado nas três categorias previstas (K-Nb-12)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("texto", ["", "   ", "\t\n"])
@pytest.mark.parametrize(
    "campo", ["tipo_evento", "data_nomeada", "nome", "contato"]
)
def test_texto_em_branco_nos_dados_extraidos_nao_e_e_nb_10(
    texto: str, campo: str
) -> None:
    """`E-Nb-10` vale **somente** para pergunta, referência e trecho ambíguo.

    Ampliá-lo aos dados extraídos exigiria arbitragem, que não existe.
    """
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                **{campo: texto, f"confianca_{campo}": ALTA}  # type: ignore[arg-type]
            )
        )
    )
    assert getattr(resultado.dados_extraidos, campo) == texto


@pytest.mark.parametrize("texto", ["", "   ", "\t\n"])
def test_dado_textual_em_branco_e_preservado_sem_transformacao(texto: str) -> None:
    """Sem `strip`, sem normalização e sem virar `None` (N-b-D2, N-b-D3)."""
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento=texto, confianca_tipo_evento=BAIXA
            )
        )
    )
    assert resultado.dados_extraidos.tipo_evento == texto
    assert resultado.dados_extraidos.tipo_evento is not None


@pytest.mark.parametrize("texto", ["", "   "])
def test_dado_textual_em_branco_ainda_deriva_o_a1(texto: str) -> None:
    """Presença é `is not None`, não "texto não vazio" (N-b-X2)."""
    resultado = canonicalizar_interpretacao(
        entrada(
            dados_extraidos=DadosExtraidos(
                tipo_evento=texto, confianca_tipo_evento=ALTA
            )
        )
    )
    assert (
        confianca_de(resultado, IntencaoConversacional.TIPO_EVENTO_INFORMADO) is ALTA
    )
    projecao = projetar_para_identidade(resultado)
    assert projecao.tipo_evento_extraido == texto


def test_e_nb_10_continua_produzido_nas_tres_categorias() -> None:
    """K-Nb-12 **não** é alterado."""
    for construir in (
        lambda: entrada(perguntas_comerciais=(PerguntaComercial("  ", ALTA),)),
        lambda: entrada(
            referencias_evento_anterior=(ReferenciaAoEventoAnterior("  ", ALTA),)
        ),
        lambda: entrada(trechos_ambiguos=(TrechoAmbiguoRecebido("  "),)),
    ):
        with pytest.raises(ValueError, match="E-Nb-10"):
            canonicalizar_interpretacao(construir())


# --------------------------------------------------------------------------
# V. E-Nb-2 — confiança declarada sem valor correspondente (N-b-G6c)
# --------------------------------------------------------------------------


def test_correcao_sem_valor_com_confianca_e_e_nb_2() -> None:
    """Precede a comparação de C4: é ausência de valor, não divergência."""
    with pytest.raises(ValueError, match="E-Nb-2"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    convidados=50, confianca_convidados=ALTA
                ),
                correcoes=(CorrecaoInterpretada("convidados", None, ALTA),),
            )
        )


def test_correcao_sem_valor_e_sem_confianca_continua_e_nb_1() -> None:
    with pytest.raises(ValueError, match="E-Nb-1"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    convidados=50, confianca_convidados=ALTA
                ),
                correcoes=(CorrecaoInterpretada("convidados", None, None),),
            )
        )


def test_e_nb_17_continua_para_divergencia_real() -> None:
    """A correção C não desloca `E-Nb-17` do seu escopo."""
    with pytest.raises(ValueError, match="E-Nb-17"):
        canonicalizar_interpretacao(
            entrada(
                dados_extraidos=DadosExtraidos(
                    convidados=50, confianca_convidados=ALTA
                ),
                correcoes=(CorrecaoInterpretada("convidados", 51, ALTA),),
            )
        )


# --------------------------------------------------------------------------
# S. Segurança das fixtures — repositório público
# --------------------------------------------------------------------------


# SENTINELA-VERIFICACAO — a checagem abaixo escaneia apenas o que vem antes daqui,
# para não encontrar os próprios padrões que ela procura.
def test_fixtures_nao_contem_dado_comercial_nem_pii_real() -> None:
    """Repositório público: fixtures fictícias, sem PII e sem valor comercial."""
    corpo = Path(__file__).read_text(encoding="utf-8").split("# SENTINELA-" + "VERIFICACAO")[0]
    arroba, cifrao = chr(64), chr(36)
    padroes = {
        "e-mail": r"[\w.-]+" + arroba + r"[\w.-]+\.[A-Za-z]{2,}",
        "valor monetario": "R" + re.escape(cifrao) + r"\s*\d",
        "telefone internacional": r"\+\d{2}\s?\d{4}",
        "url": "http" + r"s?:" + "//",
        "base comercial": "casa77" + re.escape(".") + "yaml",
    }
    for nome, padrao in padroes.items():
        assert re.search(padrao, corpo) is None, f"padrão proibido encontrado: {nome}"
