"""Testes da fronteira operacional da cadeia N-b (`docs/07` §6.3, `EN4`).

Cobre o contrato vivo de `EN4-1`–`EN4-12`: a **chamada única ao produtor por
invocação** da fronteira, a **identidade de objeto** da `Interpretacao` que
atravessa as três derivações, a forma do DTO, a ausência de PII no `repr`, a
**propagação intacta** de `FalhaProdutorInterpretacao`, `TypeError` e
`ValueError`, e os limites estruturais do módulo.

A garantia provada aqui é **por invocação**, nunca "uma chamada por ciclo
completo": o `OrquestradorMotor` não existe e a unicidade global por ciclo
continua sendo obrigação futura dele.

`tests/test_interpretation.py`, `tests/test_interpretation_llm.py`,
`tests/test_interpretation_events.py` e `tests/test_identity.py` permanecem
**inalterados** e continuam as autoridades das suas próprias fronteiras. Nenhuma
função existente foi alterada para facilitar estes testes.

Todas as fixtures são **fictícias e genéricas**: zero PII, zero conversa real,
zero valor comercial. Nenhum teste toca rede, credencial, `knowledge/**` ou YAML.
"""

from __future__ import annotations

import ast
import dataclasses
import json
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import interpretation_stage
from casa77_sdr.identity import Confianca, ProjecaoInterpretacao
from casa77_sdr.interpretation import (
    AssuntoComercial,
    DadosExtraidos,
    EntradaInterpretacao,
    IntencaoAutonomaRecebida,
    IntencaoConversacional,
    Interpretacao,
    PerguntaComercial,
    canonicalizar_interpretacao,
)
from casa77_sdr.interpretation_llm import (
    FalhaProdutorInterpretacao,
    MotivoFalhaProdutor,
)
from casa77_sdr.interpretation_stage import (
    ArtefatosInterpretacao,
    executar_interpretacao_do_ciclo,
)
from casa77_sdr.qualification import (
    FormatoEvento,
    MotivoQualificacao,
    Qualificacao,
    ResultadoQualificacao,
)
from casa77_sdr.state_machine import CondicoesCiclo, Estado, Evento, decidir

MODULO_STAGE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "casa77_sdr"
    / "interpretation_stage.py"
)

ALTA = Confianca.ALTA
BAIXA = Confianca.BAIXA

PROMPT = "prompt de sistema fictício"
MENSAGEM = "mensagem fictícia do interessado"

ASSUNTO = AssuntoComercial.PRECO_LOCACAO

#: Qualificação **neutra e coerente** para a prova de encaixe estrutural: dados
#: ainda incompletos, sem `formato` entre os ausentes — nada é fabricado para
#: forçar PASS, e nenhuma guarda condicionada é ativada artificialmente.
QUALIFICACAO_NEUTRA = Qualificacao(
    resultado=ResultadoQualificacao.DADOS_INCOMPLETOS,
    motivo=MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES,
    campos_ausentes=("nome", "contato"),
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


def interpretacao_vazia() -> Interpretacao:
    return interpretacao()


def interpretacao_rica() -> Interpretacao:
    """Vários sinais de confiança `ALTA`, em campos e intenções distintos."""
    return interpretacao(
        dados_extraidos=DadosExtraidos(
            tipo_evento="festa fictícia",
            confianca_tipo_evento=ALTA,
            data_nomeada="maio",
            confianca_data_nomeada=ALTA,
            convidados=60,
            confianca_convidados=ALTA,
            formato=FormatoEvento.SENTADO,
            confianca_formato=ALTA,
        ),
        perguntas_comerciais=(
            PerguntaComercial(texto="quanto custa?", confianca=ALTA, assunto=ASSUNTO),
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


class ProdutorContado:
    """Produtor de teste: conta invocações e devolve um `str` fixo."""

    def __init__(self, bruto: str = "{}") -> None:
        self.bruto = bruto
        self.chamadas = 0

    def produzir(
        self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]
    ) -> str:
        self.chamadas += 1
        return self.bruto


class ProdutorQueFalha:
    """Produtor de teste que sempre levanta a falha do motivo pedido."""

    def __init__(self, motivo: MotivoFalhaProdutor) -> None:
        self.motivo = motivo
        self.chamadas = 0

    def produzir(
        self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]
    ) -> str:
        self.chamadas += 1
        raise FalhaProdutorInterpretacao(self.motivo)


class Espiao:
    """Registra as instâncias recebidas por cada derivação, sem alterá-las."""

    def __init__(self) -> None:
        self.recebidos: list[Interpretacao] = []

    def envolver(self, funcao: Any) -> Any:
        def espiado(interpretacao_recebida: Interpretacao) -> Any:
            self.recebidos.append(interpretacao_recebida)
            return funcao(interpretacao_recebida)

        return espiado


def montar_cenario(
    monkeypatch: pytest.MonkeyPatch, produzida: Interpretacao
) -> dict[str, Any]:
    """Substitui a etapa 4 do módulo novo por um retorno conhecido.

    A troca é **local ao módulo sob teste**: nenhuma fronteira existente é
    alterada, e `interpretar_mensagem` continua intacta no seu próprio módulo.
    """
    chamadas: dict[str, Any] = {"etapa4": 0, "argumentos": []}

    def etapa4_falsa(
        mensagem: str, *, produtor: Any, prompt_sistema: str
    ) -> Interpretacao:
        chamadas["etapa4"] += 1
        chamadas["argumentos"].append((mensagem, produtor, prompt_sistema))
        return produzida

    monkeypatch.setattr(interpretation_stage, "interpretar_mensagem", etapa4_falsa)
    return chamadas


# --------------------------------------------------------------------------
# Chamada única ao produtor — POR INVOCAÇÃO da fronteira
# --------------------------------------------------------------------------


def test_caminho_feliz_chama_o_produtor_exatamente_uma_vez() -> None:
    """Uma invocação bem formada → **uma** chamada ao produtor."""
    produtor = ProdutorContado(bruto=PAYLOAD_VAZIO)
    executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert produtor.chamadas == 1


def test_interpretacao_sem_sinais_chama_o_produtor_exatamente_uma_vez() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_VAZIO)
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert produtor.chamadas == 1
    assert artefatos.eventos_interpretacao == ()


def test_interpretacao_rica_chama_o_produtor_exatamente_uma_vez() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_RICO)
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert produtor.chamadas == 1
    assert artefatos.eventos_interpretacao != ()


def test_falha_do_produtor_nao_provoca_retry() -> None:
    """Falha → **uma** chamada e nenhuma retentativa."""
    produtor = ProdutorQueFalha(MotivoFalhaProdutor.TIMEOUT)
    with pytest.raises(FalhaProdutorInterpretacao):
        executar_interpretacao_do_ciclo(
            MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
        )
    assert produtor.chamadas == 1


def test_duas_invocacoes_produzem_duas_chamadas() -> None:
    """A garantia é **por invocação**, não por ciclo.

    Nada neste módulo impede que um chamador o invoque duas vezes: a unicidade
    por ciclo é obrigação do `OrquestradorMotor` futuro, que não existe.
    """
    produtor = ProdutorContado(bruto=PAYLOAD_VAZIO)
    executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert produtor.chamadas == 2


# --------------------------------------------------------------------------
# A MESMA `Interpretacao` atravessa as três derivações
# --------------------------------------------------------------------------


def test_a_mesma_instancia_chega_as_tres_derivacoes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    produzida = interpretacao_rica()
    montar_cenario(monkeypatch, produzida)

    espiao_projecao = Espiao()
    espiao_interesse = Espiao()
    espiao_eventos = Espiao()

    monkeypatch.setattr(
        interpretation_stage,
        "projetar_para_identidade",
        espiao_projecao.envolver(interpretation_stage.projetar_para_identidade),
    )
    monkeypatch.setattr(
        interpretation_stage,
        "decidir_interesse_confirmar_disponibilidade",
        espiao_interesse.envolver(
            interpretation_stage.decidir_interesse_confirmar_disponibilidade
        ),
    )
    monkeypatch.setattr(
        interpretation_stage,
        "produzir_eventos_da_interpretacao",
        espiao_eventos.envolver(
            interpretation_stage.produzir_eventos_da_interpretacao
        ),
    )

    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorContado(), prompt_sistema=PROMPT
    )

    assert espiao_projecao.recebidos == [produzida]
    assert espiao_interesse.recebidos == [produzida]
    assert espiao_eventos.recebidos == [produzida]
    assert espiao_projecao.recebidos[0] is produzida
    assert espiao_interesse.recebidos[0] is produzida
    assert espiao_eventos.recebidos[0] is produzida
    assert artefatos.interpretacao is produzida


def test_a_etapa_4_executa_uma_unica_vez_por_invocacao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chamadas = montar_cenario(monkeypatch, interpretacao_vazia())
    executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorContado(), prompt_sistema=PROMPT
    )
    assert chamadas["etapa4"] == 1


def test_os_argumentos_chegam_intactos_a_etapa_4(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chamadas = montar_cenario(monkeypatch, interpretacao_vazia())
    produtor = ProdutorContado()
    executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    mensagem, recebido, prompt = chamadas["argumentos"][0]
    assert mensagem == MENSAGEM
    assert recebido is produtor
    assert prompt == PROMPT


# --------------------------------------------------------------------------
# Saída
# --------------------------------------------------------------------------


def test_a_projecao_e_a_da_interpretacao_produzida() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_RICO)
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert isinstance(artefatos.projecao_identidade, ProjecaoInterpretacao)
    assert artefatos.projecao_identidade == interpretation_stage.projetar_para_identidade(
        artefatos.interpretacao
    )


def test_a_condicao_5_e_a_da_interpretacao_produzida() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_RICO)
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert artefatos.interesse_confirmar_disponibilidade is True


def test_a_condicao_5_e_falsa_sem_a_intencao() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_VAZIO)
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert artefatos.interesse_confirmar_disponibilidade is False


def test_os_eventos_sao_os_da_interpretacao_produzida() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_RICO)
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    assert artefatos.eventos_interpretacao == (
        Evento.E02,
        Evento.E03,
        Evento.E04,
        Evento.E05,
        Evento.E06,
        Evento.E10,
    )


def test_o_dto_e_frozen() -> None:
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorContado(bruto=PAYLOAD_VAZIO), prompt_sistema=PROMPT
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        artefatos.eventos_interpretacao = ()  # type: ignore[misc]


def test_o_dto_usa_slots() -> None:
    assert ArtefatosInterpretacao.__slots__ == (
        "interpretacao",
        "projecao_identidade",
        "eventos_interpretacao",
        "interesse_confirmar_disponibilidade",
    )
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorContado(bruto=PAYLOAD_VAZIO), prompt_sistema=PROMPT
    )
    assert not hasattr(artefatos, "__dict__")


def test_o_dto_tem_exatamente_quatro_campos() -> None:
    assert tuple(f.name for f in dataclasses.fields(ArtefatosInterpretacao)) == (
        "interpretacao",
        "projecao_identidade",
        "eventos_interpretacao",
        "interesse_confirmar_disponibilidade",
    )


# --------------------------------------------------------------------------
# PII / repr
# --------------------------------------------------------------------------


def test_o_repr_nao_expoe_a_interpretacao_nem_a_projecao() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_COM_PII)
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
    )
    texto = repr(artefatos)
    for proibido in (
        "Fulano Fictício",
        "5500000000",
        "quanto custa?",
        "trecho ambíguo fictício",
        "festa fictícia",
        "maio",
    ):
        assert proibido not in texto


def test_os_dois_campos_de_runtime_ficam_fora_do_repr() -> None:
    por_nome = {f.name: f for f in dataclasses.fields(ArtefatosInterpretacao)}
    assert por_nome["interpretacao"].repr is False
    assert por_nome["projecao_identidade"].repr is False
    assert por_nome["eventos_interpretacao"].repr is True
    assert por_nome["interesse_confirmar_disponibilidade"].repr is True


def test_o_repr_carrega_os_dois_campos_auditaveis() -> None:
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorContado(bruto=PAYLOAD_VAZIO), prompt_sistema=PROMPT
    )
    texto = repr(artefatos)
    assert "eventos_interpretacao" in texto
    assert "interesse_confirmar_disponibilidade" in texto


def test_o_modulo_nao_define_repr_manual() -> None:
    fonte = MODULO_STAGE.read_text(encoding="utf-8")
    assert "__repr__" not in fonte


# --------------------------------------------------------------------------
# Falha do produtor — os nove motivos vigentes
# --------------------------------------------------------------------------


@pytest.mark.parametrize("motivo", tuple(MotivoFalhaProdutor), ids=lambda m: m.name)
def test_a_falha_do_produtor_propaga_intacta(motivo: MotivoFalhaProdutor) -> None:
    produtor = ProdutorQueFalha(motivo)
    with pytest.raises(FalhaProdutorInterpretacao) as excecao:
        executar_interpretacao_do_ciclo(
            MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
        )
    assert excecao.value.motivo is motivo
    assert produtor.chamadas == 1


@pytest.mark.parametrize("motivo", tuple(MotivoFalhaProdutor), ids=lambda m: m.name)
def test_a_falha_nao_produz_dto_nem_derivacao(
    monkeypatch: pytest.MonkeyPatch, motivo: MotivoFalhaProdutor
) -> None:
    chamadas: list[str] = []

    for nome in (
        "projetar_para_identidade",
        "decidir_interesse_confirmar_disponibilidade",
        "produzir_eventos_da_interpretacao",
    ):
        def registrar(_: Any, nome: str = nome) -> Any:
            chamadas.append(nome)
            raise AssertionError(f"{nome} não deve executar sem Interpretacao")

        monkeypatch.setattr(interpretation_stage, nome, registrar)

    with pytest.raises(FalhaProdutorInterpretacao):
        executar_interpretacao_do_ciclo(
            MENSAGEM, produtor=ProdutorQueFalha(motivo), prompt_sistema=PROMPT
        )

    assert chamadas == []


def test_o_enum_de_falha_continua_com_nove_membros() -> None:
    assert len(tuple(MotivoFalhaProdutor)) == 9


# --------------------------------------------------------------------------
# Erros de contrato
# --------------------------------------------------------------------------


def test_mensagem_de_tipo_errado_propaga_type_error() -> None:
    with pytest.raises(TypeError):
        executar_interpretacao_do_ciclo(
            123,  # type: ignore[arg-type]
            produtor=ProdutorContado(),
            prompt_sistema=PROMPT,
        )


def test_prompt_de_tipo_errado_propaga_type_error() -> None:
    with pytest.raises(TypeError):
        executar_interpretacao_do_ciclo(
            MENSAGEM,
            produtor=ProdutorContado(),
            prompt_sistema=None,  # type: ignore[arg-type]
        )


def test_erro_de_contrato_e_nb_propaga_value_error() -> None:
    """Payload estruturalmente válido que viola um `E-Nb-*`."""
    produtor = ProdutorContado(bruto=PAYLOAD_E_NB)
    with pytest.raises(ValueError) as excecao:
        executar_interpretacao_do_ciclo(
            MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
        )
    assert not isinstance(excecao.value, FalhaProdutorInterpretacao)
    assert "E-Nb" in str(excecao.value)


def test_o_erro_de_contrato_nao_vira_falha_do_produtor() -> None:
    produtor = ProdutorContado(bruto=PAYLOAD_E_NB)
    with pytest.raises(ValueError):
        executar_interpretacao_do_ciclo(
            MENSAGEM, produtor=produtor, prompt_sistema=PROMPT
        )


def test_o_type_error_nao_chega_a_chamar_o_produtor() -> None:
    produtor = ProdutorContado()
    with pytest.raises(TypeError):
        executar_interpretacao_do_ciclo(
            123,  # type: ignore[arg-type]
            produtor=produtor,
            prompt_sistema=PROMPT,
        )
    assert produtor.chamadas == 0


# --------------------------------------------------------------------------
# Estrutura do módulo
# --------------------------------------------------------------------------


def test_a_superficie_publica_tem_exatamente_dois_nomes() -> None:
    assert interpretation_stage.__all__ == [
        "ArtefatosInterpretacao",
        "executar_interpretacao_do_ciclo",
    ]


def test_o_modulo_nao_e_exportado_pelo_pacote() -> None:
    import casa77_sdr

    assert not hasattr(casa77_sdr, "ArtefatosInterpretacao")
    assert not hasattr(casa77_sdr, "executar_interpretacao_do_ciclo")


IMPORTS_PROIBIDOS = (
    "interpretation_anthropic",
    "anthropic",
    "handoff_detection",
    "closure_decision",
    "data_update",
    "coverage_decision",
    "cycle_events",
    "cycle_inputs",
    "qualification",
    "rules",
    "persistence",
    "context",
    "normalization",
    "response_",
    "os",
    "sys",
    "pathlib",
    "socket",
    "requests",
    "httpx",
    "logging",
    "random",
    "time",
    "datetime",
    "yaml",
)


@pytest.mark.parametrize("proibido", IMPORTS_PROIBIDOS)
def test_o_modulo_nao_importa_o_proibido(proibido: str) -> None:
    arvore = ast.parse(MODULO_STAGE.read_text(encoding="utf-8"))
    modulos: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            modulos.add(no.module)
    assert not any(proibido in modulo for modulo in modulos)


def test_os_imports_sao_exatamente_os_permitidos() -> None:
    arvore = ast.parse(MODULO_STAGE.read_text(encoding="utf-8"))
    modulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert modulos == {
        "__future__",
        "dataclasses",
        "casa77_sdr.identity",
        "casa77_sdr.interpretation",
        "casa77_sdr.interpretation_events",
        "casa77_sdr.interpretation_llm",
        "casa77_sdr.state_machine",
    }


CHAMADAS_FORA_DE_ESCOPO = (
    "detectar_handoff",
    "decidir_encerramento",
    "atualizar_dados_atendimento",
    "decidir_pendencias_e_cobertura",
    "produzir_eventos_internos_ciclo",
    "agregar_eventos_primeira_decisao",
    "montar_condicoes_ciclo",
    "resolver_identidade",
    "decidir",
)


@pytest.mark.parametrize("nome", CHAMADAS_FORA_DE_ESCOPO)
def test_o_modulo_nao_chama_fronteira_fora_de_escopo(nome: str) -> None:
    arvore = ast.parse(MODULO_STAGE.read_text(encoding="utf-8"))
    chamadas = {
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    }
    assert nome not in chamadas


def test_existe_exatamente_uma_chamada_sintatica_a_etapa_4() -> None:
    arvore = ast.parse(MODULO_STAGE.read_text(encoding="utf-8"))
    chamadas = [
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call)
        and isinstance(no.func, ast.Name)
        and no.func.id == "interpretar_mensagem"
    ]
    assert len(chamadas) == 1


def test_nao_existe_laco_nem_retry_em_torno_da_etapa_4() -> None:
    arvore = ast.parse(MODULO_STAGE.read_text(encoding="utf-8"))
    alvo = next(
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef)
        and no.name == "executar_interpretacao_do_ciclo"
    )
    for no in ast.walk(alvo):
        assert not isinstance(no, (ast.For, ast.While, ast.Try, ast.AsyncFor))


def test_cada_derivacao_e_chamada_uma_unica_vez_no_codigo() -> None:
    arvore = ast.parse(MODULO_STAGE.read_text(encoding="utf-8"))
    nomes = [
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    ]
    for derivacao in (
        "projetar_para_identidade",
        "decidir_interesse_confirmar_disponibilidade",
        "produzir_eventos_da_interpretacao",
    ):
        assert nomes.count(derivacao) == 1


# --------------------------------------------------------------------------
# Integração estrutural — apenas COMPATIBILIDADE, nunca pipeline integrado
# --------------------------------------------------------------------------


def test_os_artefatos_encaixam_em_cycle_inputs_e_na_maquina() -> None:
    """Prova de encaixe estrutural, com fixtures neutras para o resto.

    Não afirma que o pipeline real está integrado: a coordenação continua
    ausente, e nenhuma fronteira é chamada pelo módulo sob teste.
    """
    from casa77_sdr.cycle_inputs import (
        agregar_eventos_primeira_decisao,
        montar_condicoes_ciclo,
    )

    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorContado(bruto=PAYLOAD_RICO), prompt_sistema=PROMPT
    )

    eventos = agregar_eventos_primeira_decisao(
        e01_confirmado=True,
        eventos_interpretacao=artefatos.eventos_interpretacao,
        eventos_internos=(),
        handoff=None,
        encerramento=None,
    )
    condicoes = montar_condicoes_ciclo(
        insumo_qualificacao_atualizado=None,
        pendencia_impeditiva=None,
        handoff=None,
        resposta_aprovada_disponivel=None,
        interesse_confirmar_disponibilidade=(
            artefatos.interesse_confirmar_disponibilidade
        ),
        calendario_integrado=None,
        identidade=None,
        encerramento=None,
    )

    assert Evento.E01 in eventos
    assert isinstance(condicoes, CondicoesCiclo)
    assert condicoes.interesse_confirmar_disponibilidade is True

    decisao = decidir(Estado.NOVO, eventos, QUALIFICACAO_NEUTRA, condicoes)
    assert decisao is not None


def test_a_projecao_encaixa_no_contrato_da_identidade() -> None:
    artefatos = executar_interpretacao_do_ciclo(
        MENSAGEM, produtor=ProdutorContado(bruto=PAYLOAD_RICO), prompt_sistema=PROMPT
    )
    assert len(dataclasses.fields(artefatos.projecao_identidade)) == 7


# --------------------------------------------------------------------------
# Payloads de transporte — fictícios, sem PII real e sem valor comercial
# --------------------------------------------------------------------------
#
# A forma do transporte **não é redigitada**: ela é montada a partir das mesmas
# chaves que `gerar_schema_interpretacao()` declara, exatamente como a Camada B
# já faz em `tests/test_interpretation_llm.py`.

CAMPOS = (
    "tipo_evento",
    "data_nomeada",
    "convidados",
    "formato",
    "nome",
    "contato",
)


def slot(confianca: Confianca | None) -> dict[str, Any]:
    """`ConfidenceSlot`. `presente=False` é **ausência**, nunca `BAIXA`."""
    if confianca is None:
        # O `valor` deste ramo é preenchimento estrutural sem semântica.
        return {"presente": False, "valor": ALTA.value}
    return {"presente": True, "valor": confianca.value}


def dados(**ajustes: Any) -> dict[str, Any]:
    base: dict[str, Any] = {}
    for campo in CAMPOS:
        base[campo] = None
        base[f"confianca_{campo}"] = slot(None)
    base.update(ajustes)
    return base


def payload(**ajustes: Any) -> str:
    base: dict[str, Any] = {
        "dados_extraidos": dados(),
        "correcoes": [],
        "perguntas_comerciais": [],
        "pedido_de_humano": False,
        "confianca_pedido_de_humano": slot(None),
        "referencias_evento_anterior": [],
        "trechos_ambiguos": [],
        "confianca_global": slot(ALTA),
        "intencoes_autonomas": [],
    }
    base.update(ajustes)
    return json.dumps(base)


PAYLOAD_VAZIO = payload()

PAYLOAD_RICO = payload(
    dados_extraidos=dados(
        tipo_evento="festa ficticia",
        confianca_tipo_evento=slot(ALTA),
        data_nomeada="maio",
        confianca_data_nomeada=slot(ALTA),
        convidados=60,
        confianca_convidados=slot(ALTA),
        formato=FormatoEvento.SENTADO.value,
        confianca_formato=slot(ALTA),
    ),
    perguntas_comerciais=[
        {
            "texto": "quanto custa?",
            "confianca": slot(ALTA),
            "assunto": ASSUNTO.value,
        }
    ],
    intencoes_autonomas=[
        {
            "codigo": IntencaoConversacional.INTERESSE_EM_VISITA.value,
            "confianca": slot(ALTA),
        },
        {
            "codigo": (
                IntencaoConversacional.INTERESSE_CONFIRMAR_DISPONIBILIDADE.value
            ),
            "confianca": slot(ALTA),
        },
    ],
)

PAYLOAD_COM_PII = payload(
    dados_extraidos=dados(
        tipo_evento="festa ficticia",
        confianca_tipo_evento=slot(ALTA),
        data_nomeada="maio",
        confianca_data_nomeada=slot(ALTA),
        nome="Fulano Fictício",
        confianca_nome=slot(ALTA),
        contato="5500000000",
        confianca_contato=slot(ALTA),
    ),
    perguntas_comerciais=[
        {
            "texto": "quanto custa?",
            "confianca": slot(ALTA),
            "assunto": ASSUNTO.value,
        }
    ],
    # Trecho ambíguo **não admite** confiança declarada (`E-Nb-3`, N-b-T5).
    trechos_ambiguos=[
        {"texto": "trecho ambíguo fictício", "confianca": slot(None)}
    ],
)

#: Valor presente **sem** confiança declarada — erro de contrato `E-Nb-*` (C2).
PAYLOAD_E_NB = payload(
    dados_extraidos=dados(
        tipo_evento="festa ficticia", confianca_tipo_evento=slot(None)
    )
)
