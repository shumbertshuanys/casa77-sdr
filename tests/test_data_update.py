"""Testes do `AtualizadorDadosAtendimento` — etapa 6 do pipeline.

Cobre o contrato vivo de `docs/07-arquitetura-motor-respostas.md` §4.1.8
(`AD-1`–`AD-12`): o domínio fechado dos seis campos, a política de confiança e
correção, o conflito sem correção explícita, a igualdade estrita de domínio
(**P-1**), a definição de mutação efetiva, a fronteira entre os dois `contato` e
a pureza.

`src/casa77_sdr/interpretation.py`, `src/casa77_sdr/qualification.py`,
`src/casa77_sdr/rules.py`, `src/casa77_sdr/cycle_events.py` e
`src/casa77_sdr/persistence.py` permanecem **inalterados** e continuam as
autoridades das suas próprias fronteiras: aqui eles são apenas **exercitados**.
Os testes de integração contratual compõem as fronteiras **nos testes**; eles
**não** transformam `data_update.py` em chamador de nenhuma delas.

Todas as fixtures são **fictícias e genéricas**: zero PII real, zero conversa
real, zero valor comercial. Os limites de capacidade usados em `qualificar(...)`
são **artificiais** e não replicam a base aprovada.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import data_update, interpretation
from casa77_sdr.coverage_decision import ResultadoS2D8
from casa77_sdr.cycle_events import produzir_eventos_internos_ciclo
from casa77_sdr.data_update import (
    ResultadoAtualizacaoDados,
    atualizar_dados_atendimento,
)
from casa77_sdr.identity import Confianca
from casa77_sdr.interpretation import (
    AssuntoComercial,
    CorrecaoInterpretada,
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
    DadosQualificacao,
    FormatoEvento,
    ResultadoQualificacao,
    qualificar,
)
from casa77_sdr.rules import DadosAtendimento, MotivoViolacao, Violacao, avaliar_regras
from casa77_sdr.state_machine import Evento

MODULO_DATA_UPDATE = (
    Path(__file__).resolve().parents[1] / "src" / "casa77_sdr" / "data_update.py"
)

ALTA = Confianca.ALTA
BAIXA = Confianca.BAIXA

#: Ordem canônica **importada**, jamais redeclarada.
CAMPOS = interpretation._CAMPOS_DADOS

#: Limites **artificiais**, jamais comerciais (I06).
SENTADOS = 7
COQUETEL = 9

#: Um par de valores distintos por campo, para exercitar a política.
VALOR_A: dict[str, Any] = {
    "tipo_evento": "tipo-artificial-a",
    "data_nomeada": "data-artificial-a",
    "convidados": 3,
    "formato": FormatoEvento.SENTADO,
    "nome": "nome-artificial-a",
    "contato": "contato-artificial-a",
}
VALOR_B: dict[str, Any] = {
    "tipo_evento": "tipo-artificial-b",
    "data_nomeada": "data-artificial-b",
    "convidados": 4,
    "formato": FormatoEvento.COQUETEL,
    "nome": "nome-artificial-b",
    "contato": "contato-artificial-b",
}


# --------------------------------------------------------------------------
# Fixtures genéricas
# --------------------------------------------------------------------------


def dados(**ajustes: Any) -> DadosQualificacao:
    """`DadosQualificacao` fictícia; cada teste ajusta só o que exercita."""
    atendimento = {
        campo: ajustes.pop(campo, None)
        for campo in ("tipo_evento", "data_nomeada", "convidados")
    }
    base: dict[str, Any] = {"nome": None, "contato": None, "formato": None}
    base.update(ajustes)
    return DadosQualificacao(atendimento=DadosAtendimento(**atendimento), **base)


def extraidos(**ajustes: Any) -> DadosExtraidos:
    """`DadosExtraidos` com `campo=valor` e `confianca_campo` emparelhados."""
    return DadosExtraidos(**ajustes)


def com_campo(campo: str, valor: Any, confianca: Confianca) -> DadosExtraidos:
    return DadosExtraidos(**{campo: valor, f"confianca_{campo}": confianca})


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


def turno(campo: str, valor: Any, confianca: Confianca, *, corrigido: bool = False):
    """Interpretação canônica com **um** campo e, opcionalmente, a correção."""
    correcoes = (
        (CorrecaoInterpretada(campo=campo, valor_novo=valor, confianca=confianca),)
        if corrigido
        else ()
    )
    return interpretacao(
        dados_extraidos=com_campo(campo, valor, confianca), correcoes=correcoes
    )


def vigente_de(alvo: DadosQualificacao, campo: str) -> Any:
    if campo in ("tipo_evento", "data_nomeada", "convidados"):
        return getattr(alvo.atendimento, campo)
    return getattr(alvo, campo)


def base_ficticia() -> dict[str, Any]:
    """Base mínima com valores **artificiais**, não comerciais."""
    return {
        "eventos": {
            "aceitos": ["tipo-artificial-a"],
            "nao_aceitos": ["tipo-proibido-ficticio"],
            "datas_nao_aceitas": ["data-bloqueada-ficticia"],
        },
        "capacidade": {
            "convidados_sentados": SENTADOS,
            "formato_coquetel": COQUETEL,
        },
    }


def s2d8_neutro() -> ResultadoS2D8:
    return ResultadoS2D8(
        pendencia_impeditiva=False,
        pendencias_impeditivas=(),
        resposta_aprovada_disponivel=True,
        fragmentos_autorizados=(),
        pendencias_resposta=(),
        causas_e09=(),
    )


# --------------------------------------------------------------------------
# A. Domínio fechado dos seis campos
# --------------------------------------------------------------------------


def test_o_dominio_tem_exatamente_seis_campos_em_ordem_canonica() -> None:
    assert CAMPOS == (
        "tipo_evento",
        "data_nomeada",
        "convidados",
        "formato",
        "nome",
        "contato",
    )
    assert len(CAMPOS) == 6


def test_nao_existe_setimo_campo_em_dados_qualificacao() -> None:
    campos = {c.name for c in dataclasses.fields(DadosQualificacao)} - {"atendimento"}
    campos |= {c.name for c in dataclasses.fields(DadosAtendimento)}
    assert campos == set(CAMPOS)


@pytest.mark.parametrize("campo", CAMPOS)
def test_ausente_recebe_alta_aplica_e_marca_mutacao(campo: str) -> None:
    """Caso C: vigente ausente + `ALTA` → admite, com mutação."""
    resultado = atualizar_dados_atendimento(
        dados(), turno(campo, VALOR_A[campo], ALTA)
    )
    assert vigente_de(resultado.dados_atualizados, campo) == VALOR_A[campo]
    assert resultado.insumo_qualificacao_atualizado is True
    assert resultado.correcoes_registradas == ()
    assert resultado.campos_em_conflito == ()


@pytest.mark.parametrize("campo", CAMPOS)
def test_ausente_recebe_baixa_e_ignorado(campo: str) -> None:
    """Caso B: `BAIXA` não grava, não corrige, não conflita, não muta."""
    resultado = atualizar_dados_atendimento(
        dados(), turno(campo, VALOR_A[campo], BAIXA)
    )
    assert vigente_de(resultado.dados_atualizados, campo) is None
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.campos_em_conflito == ()


@pytest.mark.parametrize("campo", CAMPOS)
def test_vigente_igual_ao_recebido_alta_nao_muta(campo: str) -> None:
    """Caso D: estritamente igual → idempotente, sem mutação."""
    resultado = atualizar_dados_atendimento(
        dados(**{campo: VALOR_A[campo]}), turno(campo, VALOR_A[campo], ALTA)
    )
    assert vigente_de(resultado.dados_atualizados, campo) == VALOR_A[campo]
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.campos_em_conflito == ()


@pytest.mark.parametrize("campo", CAMPOS)
def test_vigente_diferente_alta_sem_correcao_preserva_e_conflita(campo: str) -> None:
    """Caso F: contradição sem correção → **não gravar** + evidência."""
    resultado = atualizar_dados_atendimento(
        dados(**{campo: VALOR_A[campo]}), turno(campo, VALOR_B[campo], ALTA)
    )
    assert vigente_de(resultado.dados_atualizados, campo) == VALOR_A[campo]
    assert resultado.campos_em_conflito == (campo,)
    assert resultado.correcoes_registradas == ()
    assert resultado.insumo_qualificacao_atualizado is False


@pytest.mark.parametrize("campo", CAMPOS)
def test_vigente_diferente_baixa_e_ignorado_sem_conflito(campo: str) -> None:
    resultado = atualizar_dados_atendimento(
        dados(**{campo: VALOR_A[campo]}), turno(campo, VALOR_B[campo], BAIXA)
    )
    assert vigente_de(resultado.dados_atualizados, campo) == VALOR_A[campo]
    assert resultado.campos_em_conflito == ()
    assert resultado.insumo_qualificacao_atualizado is False


# --------------------------------------------------------------------------
# B. Correções
# --------------------------------------------------------------------------


@pytest.mark.parametrize("campo", CAMPOS)
def test_correcao_alta_de_a_para_b_aplica_registra_e_muta(campo: str) -> None:
    """Caso E: correção explícita sobrescreve."""
    resultado = atualizar_dados_atendimento(
        dados(**{campo: VALOR_A[campo]}),
        turno(campo, VALOR_B[campo], ALTA, corrigido=True),
    )
    assert vigente_de(resultado.dados_atualizados, campo) == VALOR_B[campo]
    assert resultado.correcoes_registradas == (campo,)
    assert resultado.campos_em_conflito == ()
    assert resultado.insumo_qualificacao_atualizado is True


@pytest.mark.parametrize("campo", CAMPOS)
def test_correcao_alta_de_a_para_a_registra_sem_mutacao(campo: str) -> None:
    resultado = atualizar_dados_atendimento(
        dados(**{campo: VALOR_A[campo]}),
        turno(campo, VALOR_A[campo], ALTA, corrigido=True),
    )
    assert resultado.correcoes_registradas == (campo,)
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.campos_em_conflito == ()


@pytest.mark.parametrize("campo", CAMPOS)
def test_correcao_alta_sobre_vigente_ausente_aplica_registra_e_muta(
    campo: str,
) -> None:
    resultado = atualizar_dados_atendimento(
        dados(), turno(campo, VALOR_B[campo], ALTA, corrigido=True)
    )
    assert vigente_de(resultado.dados_atualizados, campo) == VALOR_B[campo]
    assert resultado.correcoes_registradas == (campo,)
    assert resultado.insumo_qualificacao_atualizado is True


@pytest.mark.parametrize("campo", CAMPOS)
def test_correcao_baixa_nao_aplica_nao_registra_e_nao_conflita(campo: str) -> None:
    resultado = atualizar_dados_atendimento(
        dados(**{campo: VALOR_A[campo]}),
        turno(campo, VALOR_B[campo], BAIXA, corrigido=True),
    )
    assert vigente_de(resultado.dados_atualizados, campo) == VALOR_A[campo]
    assert resultado.correcoes_registradas == ()
    assert resultado.campos_em_conflito == ()
    assert resultado.insumo_qualificacao_atualizado is False


def test_valor_da_correcao_nunca_e_aplicado_como_segunda_escrita() -> None:
    """`dados_extraidos` é a única origem operacional do valor (AD-5).

    O módulo **não percorre** `correcoes` para escrever: prova estrutural de que
    `valor_novo` não é lido no código executável.
    """
    nomes = nomes_usados(MODULO_DATA_UPDATE)
    assert "valor_novo" not in nomes
    assert "campo" in nomes  # `correcoes` é lida apenas como predicado
    assert "correcoes" in nomes


def test_ordem_de_correcoes_registradas_segue_campos_dados() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    resultado = atualizar_dados_atendimento(
        alvo,
        interpretacao(
            dados_extraidos=DadosExtraidos(
                **{
                    chave: valor
                    for campo in CAMPOS
                    for chave, valor in (
                        (campo, VALOR_B[campo]),
                        (f"confianca_{campo}", ALTA),
                    )
                }
            ),
            correcoes=tuple(
                CorrecaoInterpretada(
                    campo=campo, valor_novo=VALOR_B[campo], confianca=ALTA
                )
                for campo in CAMPOS
            ),
        ),
    )
    assert resultado.correcoes_registradas == CAMPOS
    assert len(set(resultado.correcoes_registradas)) == 6


def test_correcoes_registradas_sem_duplicata() -> None:
    resultado = atualizar_dados_atendimento(
        dados(tipo_evento=VALOR_A["tipo_evento"]),
        turno("tipo_evento", VALOR_B["tipo_evento"], ALTA, corrigido=True),
    )
    assert len(resultado.correcoes_registradas) == len(
        set(resultado.correcoes_registradas)
    )


# --------------------------------------------------------------------------
# C. Conflitos
# --------------------------------------------------------------------------


def test_correcao_explicita_nunca_aparece_tambem_como_conflito() -> None:
    for campo in CAMPOS:
        resultado = atualizar_dados_atendimento(
            dados(**{campo: VALOR_A[campo]}),
            turno(campo, VALOR_B[campo], ALTA, corrigido=True),
        )
        assert campo in resultado.correcoes_registradas
        assert campo not in resultado.campos_em_conflito
        assert set(resultado.correcoes_registradas).isdisjoint(
            resultado.campos_em_conflito
        )


def test_ordem_de_campos_em_conflito_segue_campos_dados() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    resultado = atualizar_dados_atendimento(
        alvo,
        interpretacao(
            dados_extraidos=DadosExtraidos(
                **{
                    chave: valor
                    for campo in CAMPOS
                    for chave, valor in (
                        (campo, VALOR_B[campo]),
                        (f"confianca_{campo}", ALTA),
                    )
                }
            )
        ),
    )
    assert resultado.campos_em_conflito == CAMPOS
    assert len(set(resultado.campos_em_conflito)) == 6
    # Nenhum dado foi gravado.
    for campo in CAMPOS:
        assert vigente_de(resultado.dados_atualizados, campo) == VALOR_A[campo]
    assert resultado.insumo_qualificacao_atualizado is False


def test_campos_em_conflito_carrega_somente_nomes_tecnicos() -> None:
    alvo = dados(nome="nome-artificial-a", contato="contato-artificial-a")
    resultado = atualizar_dados_atendimento(
        alvo,
        interpretacao(
            dados_extraidos=DadosExtraidos(
                nome="nome-artificial-b",
                confianca_nome=ALTA,
                contato="contato-artificial-b",
                confianca_contato=ALTA,
            )
        ),
    )
    assert resultado.campos_em_conflito == ("nome", "contato")
    assert all(item in CAMPOS for item in resultado.campos_em_conflito)
    # Nenhum valor, nenhuma PII.
    for item in resultado.campos_em_conflito:
        assert "artificial" not in item


def test_conflito_em_um_campo_nao_impede_mutacao_em_outro() -> None:
    resultado = atualizar_dados_atendimento(
        dados(tipo_evento=VALOR_A["tipo_evento"]),
        interpretacao(
            dados_extraidos=DadosExtraidos(
                tipo_evento=VALOR_B["tipo_evento"],
                confianca_tipo_evento=ALTA,
                convidados=5,
                confianca_convidados=ALTA,
            )
        ),
    )
    assert resultado.campos_em_conflito == ("tipo_evento",)
    assert resultado.dados_atualizados.atendimento.tipo_evento == VALOR_A["tipo_evento"]
    assert resultado.dados_atualizados.atendimento.convidados == 5
    assert resultado.insumo_qualificacao_atualizado is True


def test_campos_em_conflito_nao_e_evento_condicao_nem_acao() -> None:
    """`AD-6`: a evidência é estrutural, e não vira vocabulário da máquina."""
    nomes = nomes_usados(MODULO_DATA_UPDATE)
    for proibido in ("Evento", "CondicoesCiclo", "AcaoMaquina", "Transicao"):
        assert proibido not in nomes


# --------------------------------------------------------------------------
# D. Mutação efetiva
# --------------------------------------------------------------------------


def test_pergunta_comercial_pura_nao_muta() -> None:
    resultado = atualizar_dados_atendimento(
        dados(tipo_evento=VALOR_A["tipo_evento"]),
        interpretacao(
            perguntas_comerciais=(
                PerguntaComercial(
                    texto="quanto custa?",
                    confianca=ALTA,
                    assunto=AssuntoComercial.PRECO_LOCACAO,
                ),
            )
        ),
    )
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.dados_atualizados == dados(tipo_evento=VALOR_A["tipo_evento"])


@pytest.mark.parametrize("confianca", [ALTA, BAIXA], ids=lambda c: c.value)
def test_pedido_de_humano_nao_muta(confianca: Confianca) -> None:
    """A exceção de N-b-PH3 **não** se aplica a dados (AD-4)."""
    resultado = atualizar_dados_atendimento(
        dados(),
        interpretacao(
            pedido_de_humano=True, confianca_pedido_de_humano=confianca
        ),
    )
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.dados_atualizados == dados()


def test_turno_vazio_nao_muta() -> None:
    resultado = atualizar_dados_atendimento(dados(), interpretacao())
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.correcoes_registradas == ()
    assert resultado.campos_em_conflito == ()


def test_sinais_autonomos_nao_mutam() -> None:
    resultado = atualizar_dados_atendimento(
        dados(),
        interpretacao(
            intencoes_autonomas=(
                IntencaoAutonomaRecebida(
                    codigo=IntencaoConversacional.INTERESSE_EM_VISITA, confianca=ALTA
                ),
                IntencaoAutonomaRecebida(
                    codigo=IntencaoConversacional.PEDIDO_DE_RESERVA, confianca=ALTA
                ),
            )
        ),
    )
    assert resultado.insumo_qualificacao_atualizado is False


def test_multiplos_campos_com_um_que_muda_produz_true() -> None:
    alvo = dados(tipo_evento=VALOR_A["tipo_evento"], convidados=3)
    resultado = atualizar_dados_atendimento(
        alvo,
        interpretacao(
            dados_extraidos=DadosExtraidos(
                tipo_evento=VALOR_A["tipo_evento"],
                confianca_tipo_evento=ALTA,
                convidados=3,
                confianca_convidados=ALTA,
                nome="nome-artificial-a",
                confianca_nome=ALTA,
            )
        ),
    )
    assert resultado.insumo_qualificacao_atualizado is True
    assert resultado.dados_atualizados.nome == "nome-artificial-a"


def test_todos_os_campos_repetidos_nao_mutam() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    resultado = atualizar_dados_atendimento(
        alvo,
        interpretacao(
            dados_extraidos=DadosExtraidos(
                **{
                    chave: valor
                    for campo in CAMPOS
                    for chave, valor in (
                        (campo, VALOR_A[campo]),
                        (f"confianca_{campo}", ALTA),
                    )
                }
            )
        ),
    )
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.dados_atualizados == alvo


def test_uma_correcao_efetiva_entre_varios_campos_produz_true() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    resultado = atualizar_dados_atendimento(
        alvo,
        interpretacao(
            dados_extraidos=DadosExtraidos(
                **{
                    chave: valor
                    for campo in CAMPOS
                    for chave, valor in (
                        (
                            campo,
                            VALOR_B[campo] if campo == "convidados" else VALOR_A[campo],
                        ),
                        (f"confianca_{campo}", ALTA),
                    )
                }
            ),
            correcoes=(
                CorrecaoInterpretada(
                    campo="convidados", valor_novo=VALOR_B["convidados"], confianca=ALTA
                ),
            ),
        ),
    )
    assert resultado.insumo_qualificacao_atualizado is True
    assert resultado.correcoes_registradas == ("convidados",)
    assert resultado.dados_atualizados.atendimento.convidados == VALOR_B["convidados"]


def test_a_saida_da_mutacao_e_bool_real_nunca_none() -> None:
    for alvo, interp in (
        (dados(), interpretacao()),
        (dados(), turno("nome", "nome-artificial-a", ALTA)),
        (dados(nome="nome-artificial-a"), turno("nome", "nome-artificial-b", ALTA)),
    ):
        flag = atualizar_dados_atendimento(alvo, interp).insumo_qualificacao_atualizado
        assert isinstance(flag, bool)
        assert flag is not None
        assert type(flag) is bool


# --------------------------------------------------------------------------
# E. Igualdade estrita de domínio (P-1)
# --------------------------------------------------------------------------


def test_a_fronteira_usa_a_mesma_autoridade_de_igualdade_de_n_b() -> None:
    """`AD-7`: `_mesmo_valor` é **importado**, não reimplementado."""
    arvore = ast.parse(MODULO_DATA_UPDATE.read_text(encoding="utf-8"))
    importados = {
        alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module == "casa77_sdr.interpretation"
        for alias in no.names
    }
    assert "_mesmo_valor" in importados
    assert "_CAMPOS_DADOS" in importados

    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }
    assert "_mesmo_valor" in chamadas
    # Nenhuma função de equivalência paralela é definida aqui.
    definidas = {no.name for no in ast.walk(arvore) if isinstance(no, ast.FunctionDef)}
    assert "_mesmo_valor" not in definidas


def test_caixa_diferente_nao_e_igual() -> None:
    """`"Casamento"` ≠ `"casamento"`: sem `lower`, sem `casefold`."""
    resultado = atualizar_dados_atendimento(
        dados(tipo_evento="Casamento"), turno("tipo_evento", "casamento", ALTA)
    )
    assert resultado.campos_em_conflito == ("tipo_evento",)
    assert resultado.dados_atualizados.atendimento.tipo_evento == "Casamento"


def test_espaco_em_branco_nao_e_igual() -> None:
    """`"abc"` ≠ `"abc "`: sem `strip`."""
    resultado = atualizar_dados_atendimento(
        dados(nome="abc"), turno("nome", "abc ", ALTA)
    )
    assert resultado.campos_em_conflito == ("nome",)
    assert resultado.dados_atualizados.nome == "abc"


def test_texto_identico_e_igual() -> None:
    resultado = atualizar_dados_atendimento(
        dados(nome="abc"), turno("nome", "abc", ALTA)
    )
    assert resultado.campos_em_conflito == ()
    assert resultado.insumo_qualificacao_atualizado is False


def test_inteiro_identico_e_igual() -> None:
    resultado = atualizar_dados_atendimento(
        dados(convidados=42), turno("convidados", 42, ALTA)
    )
    assert resultado.insumo_qualificacao_atualizado is False
    assert resultado.campos_em_conflito == ()


def test_formato_identico_e_igual() -> None:
    resultado = atualizar_dados_atendimento(
        dados(formato=FormatoEvento.SENTADO),
        turno("formato", FormatoEvento.SENTADO, ALTA),
    )
    assert resultado.insumo_qualificacao_atualizado is False


def test_bool_nao_e_aceito_como_convidados_vigente() -> None:
    """N-b-D4: `bool` nunca equivale a `int`, nem como valor vigente."""
    invalido = DadosQualificacao(
        atendimento=DadosAtendimento(convidados=True)  # type: ignore[arg-type]
    )
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(invalido, interpretacao())


def test_nenhuma_normalizacao_nominal_acontece() -> None:
    """`AD-7`: nada de caixa, acento, Unicode, sinônimo, regex ou calendário."""
    nomes = nomes_usados(MODULO_DATA_UPDATE)
    for proibido in (
        "lower",
        "casefold",
        "strip",
        "unicodedata",
        "normalize",
        "re",
        "datetime",
        "strptime",
        "replace",
        "sub",
        "match",
    ):
        assert proibido not in nomes


# --------------------------------------------------------------------------
# F. Preservação
# --------------------------------------------------------------------------


def test_campo_vigente_nao_mencionado_e_preservado() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    resultado = atualizar_dados_atendimento(
        alvo, turno("convidados", VALOR_A["convidados"], ALTA)
    )
    assert resultado.dados_atualizados == alvo


def test_nenhum_campo_e_apagado() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    resultado = atualizar_dados_atendimento(alvo, interpretacao())
    for campo in CAMPOS:
        assert vigente_de(resultado.dados_atualizados, campo) is not None


def test_a_saida_usa_dados_qualificacao_com_seis_campos() -> None:
    resultado = atualizar_dados_atendimento(dados(), interpretacao())
    assert isinstance(resultado.dados_atualizados, DadosQualificacao)
    assert isinstance(resultado.dados_atualizados.atendimento, DadosAtendimento)


def test_as_entradas_nao_sao_mutadas() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    interp = turno("tipo_evento", VALOR_B["tipo_evento"], ALTA, corrigido=True)
    copia_dados = dataclasses.replace(alvo)
    antes_interp = (interp.dados_extraidos, interp.correcoes, interp.confianca_global)

    resultado = atualizar_dados_atendimento(alvo, interp)

    assert alvo == copia_dados
    assert (interp.dados_extraidos, interp.correcoes, interp.confianca_global) == (
        antes_interp
    )
    # A saída é um objeto **novo**, não a entrada mutada.
    assert resultado.dados_atualizados is not alvo


def test_dados_vazios_representam_atendimento_novo_sem_heranca() -> None:
    resultado = atualizar_dados_atendimento(
        dados(), turno("tipo_evento", VALOR_A["tipo_evento"], ALTA)
    )
    assert resultado.dados_atualizados.atendimento.tipo_evento == VALOR_A["tipo_evento"]
    assert resultado.dados_atualizados.nome is None
    assert resultado.dados_atualizados.contato is None
    assert resultado.insumo_qualificacao_atualizado is True


def test_dados_existentes_representam_preservacao_do_atendimento() -> None:
    alvo = dados(**{campo: VALOR_A[campo] for campo in CAMPOS})
    resultado = atualizar_dados_atendimento(alvo, interpretacao())
    assert resultado.dados_atualizados == alvo
    assert resultado.insumo_qualificacao_atualizado is False


def test_a_fronteira_nao_conhece_identidade_nem_takeover() -> None:
    """`AD-2`: ela não sabe se veio de T36, T37 ou primeiro contato."""
    nomes = nomes_usados(MODULO_DATA_UPDATE)
    for proibido in (
        "DecisaoIdentidade",
        "SituacaoTakeover",
        "Identidade",
        "id_atendimento",
    ):
        assert proibido not in nomes


# --------------------------------------------------------------------------
# G. `contato` — as duas fronteiras
# --------------------------------------------------------------------------


def test_contato_interpretado_pode_mudar_por_correcao_alta() -> None:
    resultado = atualizar_dados_atendimento(
        dados(contato="contato-artificial-a"),
        turno("contato", "contato-artificial-b", ALTA, corrigido=True),
    )
    assert resultado.dados_atualizados.contato == "contato-artificial-b"
    assert resultado.correcoes_registradas == ("contato",)
    assert resultado.insumo_qualificacao_atualizado is True


def test_o_modulo_nao_conhece_o_contato_operacional() -> None:
    """`AD-10`: `RegistroAtendimento.contato` é outra matéria."""
    arvore = ast.parse(MODULO_DATA_UPDATE.read_text(encoding="utf-8"))
    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert "casa77_sdr.persistence" not in submodulos

    nomes = nomes_usados(MODULO_DATA_UPDATE)
    for proibido in (
        "RegistroAtendimento",
        "persistence",
        "casa77_sdr.persistence",
        "PersistenciaOperacional",
        "canal",
        "dados_coletados",
        "estado_conversa",
    ):
        assert proibido not in nomes


def test_nenhum_registro_atendimento_e_construido() -> None:
    arvore = ast.parse(MODULO_DATA_UPDATE.read_text(encoding="utf-8"))
    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }
    assert "RegistroAtendimento" not in chamadas
    assert chamadas <= {
        "isinstance",
        "getattr",
        "frozenset",
        "TypeError",
        "ValueError",
        "any",
        "tuple",
        "field",
        "dataclass",
        "DadosQualificacao",
        "DadosAtendimento",
        "ResultadoAtualizacaoDados",
        "_validar_dados_vigentes",
        "_validar_interpretacao_canonica",
        "_campos_corrigidos",
        "_vigente",
        "_mesmo_valor",
    }


# --------------------------------------------------------------------------
# H. Pureza e superfície
# --------------------------------------------------------------------------


def nomes_usados(caminho: Path) -> set[str]:
    """Identificadores realmente referenciados no **código executável**.

    Busca por substring produziria falso positivo — `Evento` é substring de
    `FormatoEvento` e de `tipo_evento`, e `Qualificacao` é substring de
    `DadosQualificacao`. O que precisa ser provado é a ausência do **símbolo**.
    """
    arvore = ast.parse(codigo_executavel(caminho))
    nomes = {no.id for no in ast.walk(arvore) if isinstance(no, ast.Name)}
    nomes |= {no.attr for no in ast.walk(arvore) if isinstance(no, ast.Attribute)}
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
            nomes.update(a.name for a in no.names)
        elif isinstance(no, ast.Import):
            nomes.update(a.name for a in no.names)
    return nomes


def codigo_executavel(caminho: Path) -> str:
    """Devolve o módulo **sem docstrings e sem comentários**.

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


def test_a_fronteira_e_pura_e_nao_importa_nada_proibido() -> None:
    arvore = ast.parse(MODULO_DATA_UPDATE.read_text(encoding="utf-8"))
    raizes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            raizes.update(a.name.split(".")[0] for a in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            raizes.add(no.module.split(".")[0])
    assert raizes <= {"__future__", "dataclasses", "casa77_sdr"}

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
        "casa77_sdr.rules",
    }
    for proibido in (
        "casa77_sdr.persistence",
        "casa77_sdr.state_machine",
        "casa77_sdr.cycle_events",
        "casa77_sdr.context",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.knowledge",
        "yaml",
    ):
        assert proibido not in submodulos


def test_ausencias_exigidas_no_codigo_executavel() -> None:
    nomes = nomes_usados(MODULO_DATA_UPDATE)
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
        "print",
        "persistence",
        "casa77_sdr.persistence",
        "state_machine",
        "casa77_sdr.state_machine",
        "Evento",
        "CondicoesCiclo",
        "decidir",
        "qualificar",
        "avaliar_regras",
        "produzir_eventos_internos_ciclo",
        "cycle_events",
        "casa77_sdr.cycle_events",
        "Qualificacao",
        "Violacao",
        "getenv",
        "environ",
    ):
        assert proibido not in nomes


def test_a_superficie_publica_e_fechada_em_dois_nomes() -> None:
    assert data_update.__all__ == [
        "ResultadoAtualizacaoDados",
        "atualizar_dados_atendimento",
    ]


def test_a_fronteira_nao_e_exportada_pelo_pacote() -> None:
    import casa77_sdr

    for nome in ("ResultadoAtualizacaoDados", "atualizar_dados_atendimento"):
        assert nome not in casa77_sdr.__all__
        assert not hasattr(casa77_sdr, nome)


def test_nenhum_enum_nem_excecao_publica_nova() -> None:
    arvore = ast.parse(MODULO_DATA_UPDATE.read_text(encoding="utf-8"))
    classes = [no for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)]
    assert [no.name for no in classes] == ["ResultadoAtualizacaoDados"]
    assert classes[0].bases == []


def test_a_assinatura_recebe_somente_as_duas_entradas() -> None:
    parametros = inspect.signature(atualizar_dados_atendimento).parameters
    assert list(parametros) == ["dados_vigentes", "interpretacao"]
    # As anotações são exatamente os dois tipos do contrato — comparadas como
    # identificador, não por substring: `Qualificacao` é substring de
    # `DadosQualificacao`, e confundir as duas seria falso positivo.
    anotacoes = [str(p.annotation) for p in parametros.values()]
    assert anotacoes == ["DadosQualificacao", "Interpretacao"]


def test_o_dto_tem_quatro_campos_e_dados_fora_do_repr() -> None:
    campos = dataclasses.fields(ResultadoAtualizacaoDados)
    assert [c.name for c in campos] == [
        "dados_atualizados",
        "correcoes_registradas",
        "campos_em_conflito",
        "insumo_qualificacao_atualizado",
    ]
    assert campos[0].repr is False


def test_o_repr_nao_vaza_pii() -> None:
    resultado = atualizar_dados_atendimento(
        dados(nome="nome-artificial-a", contato="contato-artificial-a"),
        interpretacao(),
    )
    texto = repr(resultado)
    assert "nome-artificial-a" not in texto
    assert "contato-artificial-a" not in texto
    assert "dados_atualizados" not in texto


def test_o_dto_e_imutavel() -> None:
    resultado = atualizar_dados_atendimento(dados(), interpretacao())
    with pytest.raises(dataclasses.FrozenInstanceError):
        resultado.insumo_qualificacao_atualizado = True  # type: ignore[misc]


def test_a_funcao_e_deterministica() -> None:
    alvo = dados(tipo_evento=VALOR_A["tipo_evento"])
    interp = turno("convidados", 5, ALTA)
    resultados = [atualizar_dados_atendimento(alvo, interp) for _ in range(5)]
    assert all(r == resultados[0] for r in resultados)


# --------------------------------------------------------------------------
# I. Erros
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "valor", [None, "dados", 1, True, (), [], {}, object()], ids=repr
)
def test_dados_vigentes_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(valor, interpretacao())


def test_atendimento_de_tipo_errado_e_type_error() -> None:
    invalido = DadosQualificacao(atendimento="atendimento")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(invalido, interpretacao())


@pytest.mark.parametrize(
    "campo", ["tipo_evento", "data_nomeada", "nome", "contato"]
)
def test_campo_textual_vigente_de_tipo_errado_e_type_error(campo: str) -> None:
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(dados(**{campo: 123}), interpretacao())


def test_convidados_vigente_bool_e_type_error() -> None:
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(dados(convidados=True), interpretacao())


def test_convidados_vigente_texto_e_type_error() -> None:
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(dados(convidados="3"), interpretacao())


def test_convidados_vigente_negativo_e_value_error() -> None:
    with pytest.raises(ValueError):
        atualizar_dados_atendimento(dados(convidados=-1), interpretacao())


def test_formato_vigente_de_tipo_errado_e_type_error() -> None:
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(dados(formato="sentado"), interpretacao())


@pytest.mark.parametrize(
    "valor", [None, "interpretacao", 1, True, (), [], {}, object()], ids=repr
)
def test_interpretacao_de_tipo_errado_e_type_error(valor: Any) -> None:
    with pytest.raises(TypeError):
        atualizar_dados_atendimento(dados(), valor)


def test_interpretacao_nao_canonica_e_bloqueada() -> None:
    """Reutiliza a validação de N-b: `isinstance` prova o tipo, não a validade."""
    invalida = Interpretacao(
        intencoes_detectadas=(),
        dados_extraidos=DadosExtraidos(tipo_evento="festa-artificial"),
        correcoes=(),
        perguntas_comerciais=(),
        pedido_de_humano=False,
        confianca_pedido_de_humano=None,
        referencias_evento_anterior=(),
        confianca_global=ALTA,
        trechos_ambiguos=(),
    )
    with pytest.raises(ValueError, match="E-Nb-1"):
        atualizar_dados_atendimento(dados(), invalida)


def test_entrada_invalida_nao_produz_saida_parcial() -> None:
    invalida = Interpretacao(
        intencoes_detectadas=(
            IntencaoDetectada(
                codigo=IntencaoConversacional.TIPO_EVENTO_INFORMADO, confianca=ALTA
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
        atualizar_dados_atendimento(dados(), invalida)


def test_a_validacao_canonica_e_reutilizada_e_nao_duplicada() -> None:
    arvore = ast.parse(MODULO_DATA_UPDATE.read_text(encoding="utf-8"))
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


@pytest.mark.parametrize(
    ("alvo", "excecao"),
    [
        (dados(nome=123), TypeError),
        (dados(convidados=-1), ValueError),
        (dados(formato="sentado"), TypeError),
    ],
    ids=["nome", "convidados", "formato"],
)
def test_mensagens_de_erro_citam_somente_o_nome_tecnico(
    alvo: DadosQualificacao, excecao: type[Exception]
) -> None:
    with pytest.raises(excecao) as capturado:
        atualizar_dados_atendimento(alvo, interpretacao())
    mensagem = str(capturado.value)
    for proibido in ("123", "-1", "sentado", "artificial"):
        assert proibido not in mensagem


# --------------------------------------------------------------------------
# J. Integração contratual — a composição vive **nos testes**
# --------------------------------------------------------------------------


def test_data_update_alimenta_avaliar_regras_e_qualificar_sem_conversao() -> None:
    """`AD-1`: os DTOs encaixam diretamente, sem adaptador."""
    resultado = atualizar_dados_atendimento(
        dados(),
        interpretacao(
            dados_extraidos=DadosExtraidos(
                tipo_evento="tipo-artificial-a",
                confianca_tipo_evento=ALTA,
                data_nomeada="data-artificial-a",
                confianca_data_nomeada=ALTA,
                convidados=3,
                confianca_convidados=ALTA,
                nome="nome-artificial-a",
                confianca_nome=ALTA,
                contato="contato-artificial-a",
                confianca_contato=ALTA,
            )
        ),
    )
    atualizados = resultado.dados_atualizados
    violacoes = tuple(avaliar_regras(atualizados.atendimento, base_ficticia()))
    calculada = qualificar(atualizados, violacoes, (), base_ficticia())
    assert calculada.resultado is ResultadoQualificacao.QUALIFICADO


def test_cenario_minimo_incompletos_para_e07() -> None:
    """dados incompletos → dado novo `ALTA` → completos → positivo → `E07`."""
    vigentes = dados(
        tipo_evento="tipo-artificial-a",
        data_nomeada="data-artificial-a",
        convidados=3,
        nome="nome-artificial-a",
    )
    incompleta = qualificar(vigentes, (), (), base_ficticia())
    assert incompleta.resultado is ResultadoQualificacao.DADOS_INCOMPLETOS

    resultado = atualizar_dados_atendimento(
        vigentes, turno("contato", "contato-artificial-a", ALTA)
    )
    assert resultado.insumo_qualificacao_atualizado is True

    atualizados = resultado.dados_atualizados
    calculada = qualificar(
        atualizados,
        tuple(avaliar_regras(atualizados.atendimento, base_ficticia())),
        (),
        base_ficticia(),
    )
    assert calculada.resultado is ResultadoQualificacao.QUALIFICADO

    eventos = produzir_eventos_internos_ciclo(
        calculada, resultado.insumo_qualificacao_atualizado, s2d8_neutro()
    )
    assert eventos == (Evento.E07,)


def test_lead_completo_com_pergunta_pura_nao_produz_e07_espurio() -> None:
    vigentes = dados(
        tipo_evento="tipo-artificial-a",
        data_nomeada="data-artificial-a",
        convidados=3,
        nome="nome-artificial-a",
        contato="contato-artificial-a",
    )
    resultado = atualizar_dados_atendimento(
        vigentes,
        interpretacao(
            perguntas_comerciais=(
                PerguntaComercial(
                    texto="quanto custa?",
                    confianca=ALTA,
                    assunto=AssuntoComercial.PRECO_LOCACAO,
                ),
            )
        ),
    )
    assert resultado.insumo_qualificacao_atualizado is False

    atualizados = resultado.dados_atualizados
    calculada = qualificar(
        atualizados,
        tuple(avaliar_regras(atualizados.atendimento, base_ficticia())),
        (),
        base_ficticia(),
    )
    assert calculada.resultado is ResultadoQualificacao.QUALIFICADO

    eventos = produzir_eventos_internos_ciclo(
        calculada, resultado.insumo_qualificacao_atualizado, s2d8_neutro()
    )
    assert eventos == ()
    assert Evento.E07 not in eventos


def test_a_flag_atravessa_como_bool_real_para_cycle_events() -> None:
    resultado = atualizar_dados_atendimento(
        dados(), turno("nome", "nome-artificial-a", ALTA)
    )
    flag = resultado.insumo_qualificacao_atualizado
    assert type(flag) is bool
    # `cycle_events` rejeita substituto silencioso; o `bool` real atravessa.
    calculada = qualificar(
        resultado.dados_atualizados, (), (), base_ficticia()
    )
    produzir_eventos_internos_ciclo(calculada, flag, s2d8_neutro())


def test_conflito_nao_altera_a_qualificacao_vigente() -> None:
    """Contradição sem correção não grava — e por isso não recalcula nada."""
    vigentes = dados(
        tipo_evento="tipo-artificial-a",
        data_nomeada="data-artificial-a",
        convidados=3,
        nome="nome-artificial-a",
        contato="contato-artificial-a",
    )
    antes = qualificar(vigentes, (), (), base_ficticia())
    resultado = atualizar_dados_atendimento(
        vigentes, turno("tipo_evento", "tipo-artificial-b", ALTA)
    )
    assert resultado.campos_em_conflito == ("tipo_evento",)
    depois = qualificar(resultado.dados_atualizados, (), (), base_ficticia())
    assert depois == antes
    assert resultado.insumo_qualificacao_atualizado is False


def test_correcao_que_torna_incompativel_atravessa_para_e08() -> None:
    """A etapa 6 grava; quem classifica é o `Qualificador` (AD-12)."""
    vigentes = dados(
        tipo_evento="tipo-artificial-a",
        data_nomeada="data-artificial-a",
        convidados=3,
        nome="nome-artificial-a",
        contato="contato-artificial-a",
    )
    resultado = atualizar_dados_atendimento(
        vigentes, turno("convidados", COQUETEL + 1, ALTA, corrigido=True)
    )
    assert resultado.insumo_qualificacao_atualizado is True
    assert resultado.correcoes_registradas == ("convidados",)

    atualizados = resultado.dados_atualizados
    violacoes = tuple(avaliar_regras(atualizados.atendimento, base_ficticia()))
    assert any(
        v.motivo is MotivoViolacao.CONVIDADOS_ACIMA_DA_CAPACIDADE for v in violacoes
    )
    calculada = qualificar(atualizados, violacoes, (), base_ficticia())
    assert calculada.resultado is ResultadoQualificacao.INCOMPATIVEL

    eventos = produzir_eventos_internos_ciclo(
        calculada, resultado.insumo_qualificacao_atualizado, s2d8_neutro()
    )
    assert eventos == (Evento.E08,)


# --------------------------------------------------------------------------
# K. Preservação das fronteiras já aprovadas
# --------------------------------------------------------------------------

CONGELADOS = (
    "src/casa77_sdr/interpretation.py",
    "src/casa77_sdr/interpretation_events.py",
    "src/casa77_sdr/qualification.py",
    "src/casa77_sdr/rules.py",
    "src/casa77_sdr/cycle_events.py",
    "src/casa77_sdr/persistence.py",
    "src/casa77_sdr/context.py",
    "src/casa77_sdr/identity.py",
    "src/casa77_sdr/state_machine.py",
    "src/casa77_sdr/__init__.py",
)


@pytest.mark.parametrize("caminho", CONGELADOS, ids=lambda c: c.split("/")[-1])
def test_nenhum_congelado_importa_a_nova_fronteira(caminho: str) -> None:
    """A fronteira é **posterior**: nada aprovado passa a depender dela."""
    fonte = (Path(__file__).resolve().parents[1] / caminho).read_text(encoding="utf-8")
    assert "data_update" not in fonte
    assert "atualizar_dados_atendimento" not in fonte


def test_registro_atendimento_preservado_na_persistencia() -> None:
    """Pendência `B`: a dataclass mantém nome, campos e exportação."""
    from casa77_sdr import persistence

    assert hasattr(persistence, "RegistroAtendimento")
    assert persistence.RegistroAtendimento.__name__ == "RegistroAtendimento"
    campos = [c.name for c in dataclasses.fields(persistence.RegistroAtendimento)]
    assert campos[:3] == ["id_atendimento", "canal", "contato"]
    assert "dados_coletados" in campos


def test_nenhum_alias_de_registro_atendimento_foi_criado() -> None:
    """Dois referentes, dois nomes — e nenhuma terceira abstração."""
    assert not hasattr(data_update, "RegistroAtendimento")
    assert not hasattr(data_update, "AtualizadorDadosAtendimento")
    fonte = MODULO_DATA_UPDATE.read_text(encoding="utf-8")
    # O nome novo é **conceitual**, registrado em docs/07; ele não vira símbolo.
    assert "AtualizadorDadosAtendimento" in fonte  # citado na docstring
    assert "AtualizadorDadosAtendimento" not in nomes_usados(MODULO_DATA_UPDATE)


def test_campos_dados_continua_com_seis_e_e_importado() -> None:
    assert interpretation._CAMPOS_DADOS == CAMPOS
    assert len(interpretation._CAMPOS_DADOS) == 6
