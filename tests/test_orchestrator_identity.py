"""Testes das etapas 4–5 do ciclo (`orchestrator_identity`).

Cobre a interpretação **única** por ciclo (CN4), os quatro desfechos terminais
(`INTERPRETACAO_INDISPONIVEL`, `HUMANO_MULTIPLO`, `SEM_CANDIDATO_ELEGIVEL` —
contrato E4 — e `AMBIGUA` — A1–A7) e a hidratação do alvo nos caminhos que
prosseguem (`HUMANO_UNICO`, primeiro contato, nova solicitação, atendimento
ativo e mesma solicitação).

Valores sintéticos apenas: zero PII, zero conversa real, zero valor comercial.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import orchestrator_identity
from casa77_sdr.context import ProjecoesIdentidadeEtapa3
from casa77_sdr.identity import (
    CandidatoAtendimento,
    CriterioIdentidade,
    DecisaoIdentidade,
    SituacaoTakeover,
    VeredictoIdentificador,
    Vinculo,
)
from casa77_sdr.interpretation_llm import (
    FalhaProdutorInterpretacao,
    MotivoFalhaProdutor,
)
from casa77_sdr.motor_deps import BaseMotor, DependenciasMotor, carregar_base_motor
from casa77_sdr.normalization import (
    EntradaMensagem,
    EntradaNormalizada,
    normalizar_entrada,
)
from casa77_sdr.orchestrator_identity import (
    AlvoDoCiclo,
    DesfechoTerminal,
    coordenar_etapas_4_e_5,
)
from casa77_sdr.persistence import PersistenciaEmMemoria, RegistroAtendimento
from casa77_sdr.state_machine import Estado, Identidade

RAIZ = Path(__file__).resolve().parents[1]
CANAL = "teste"
CONTATO = "contato-ficticio"
MENSAGEM = "mensagem ficticia"
REFERENCIA = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
JANELA = timedelta(minutes=5)
MARCO = datetime(2026, 1, 10, 9, 0, tzinfo=UTC)


# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------


def _slot(valor: str | None) -> dict[str, Any]:
    if valor is None:
        return {"presente": False, "valor": "alta"}
    return {"presente": True, "valor": valor}


def _payload_vazio(*, tipo_evento_sem_confianca: str | None = None) -> str:
    dados: dict[str, Any] = {}
    for campo in ("tipo_evento", "data_nomeada", "convidados", "formato", "nome", "contato"):
        dados[campo] = None
        dados[f"confianca_{campo}"] = _slot(None)
    # Valor presente sem confiança declarada — erro de contrato `E-Nb-*` (C2).
    dados["tipo_evento"] = tipo_evento_sem_confianca
    return json.dumps(
        {
            "dados_extraidos": dados,
            "correcoes": [],
            "perguntas_comerciais": [],
            "pedido_de_humano": False,
            "confianca_pedido_de_humano": _slot(None),
            "referencias_evento_anterior": [],
            "trechos_ambiguos": [],
            "confianca_global": _slot("alta"),
            "intencoes_autonomas": [],
        }
    )


class ProdutorContado:
    """Conta invocações e devolve um payload fixo."""

    def __init__(self, bruto: str) -> None:
        self.bruto = bruto
        self.chamadas = 0

    def produzir(self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]) -> str:
        self.chamadas += 1
        return self.bruto


class ProdutorQueFalha:
    def __init__(self) -> None:
        self.chamadas = 0

    def produzir(self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]) -> str:
        self.chamadas += 1
        raise FalhaProdutorInterpretacao(MotivoFalhaProdutor.TIMEOUT)


@dataclass(frozen=True)
class DepsTeste(DependenciasMotor):
    """`DependenciasMotor` com o registro das tentativas de alerta."""

    alertas: list[dict[str, Any]] = field(default_factory=list)


@pytest.fixture(scope="module")
def base_motor() -> BaseMotor:
    return carregar_base_motor(RAIZ)


def _montar_deps(base_motor: BaseMotor, produtor: Any) -> DepsTeste:
    alertas: list[dict[str, Any]] = []

    def tentar_alerta(**kwargs: Any) -> None:
        alertas.append(kwargs)

    def nao_chamar(*_: Any) -> None:
        raise AssertionError("emissão proibida nas etapas 4–5")

    return DepsTeste(
        base_motor=base_motor,
        persistencia=PersistenciaEmMemoria(),
        produtor=produtor,
        prompt_sistema="prompt ficticio",
        janela_idempotencia=JANELA,
        limiar_recencia=timedelta(days=30),
        calendario_integrado=False,
        tentar_alerta=tentar_alerta,
        enviar_mensagem=nao_chamar,
        entregar_resumo=nao_chamar,
        alertas=alertas,
    )


@pytest.fixture
def deps_fake(base_motor: BaseMotor) -> DepsTeste:
    return _montar_deps(base_motor, ProdutorContado(_payload_vazio()))


@pytest.fixture
def deps_produtor_falha(base_motor: BaseMotor) -> DepsTeste:
    return _montar_deps(base_motor, ProdutorQueFalha())


@pytest.fixture
def entrada() -> EntradaMensagem:
    return EntradaMensagem(
        canal=CANAL, contato=CONTATO, mensagem=MENSAGEM, recebida_em=REFERENCIA
    )


@pytest.fixture
def normalizada(entrada: EntradaMensagem) -> EntradaNormalizada:
    return normalizar_entrada(entrada, JANELA)


def _projecoes(
    *,
    candidatos: tuple[CandidatoAtendimento, ...] = (),
    havia_estado_esperado: bool = False,
    humanos: tuple[str, ...] = (),
) -> ProjecoesIdentidadeEtapa3:
    return ProjecoesIdentidadeEtapa3(
        candidatos_elegiveis=candidatos,
        veredito_identificador=VeredictoIdentificador.NAO_INFORMADO,
        id_atendimento_validado=None,
        havia_estado_esperado=havia_estado_esperado,
        ids_em_atendimento_humano=humanos,
    )


@pytest.fixture
def projecoes_vazias() -> ProjecoesIdentidadeEtapa3:
    return _projecoes()


def _candidato(id_atendimento: str, estado: Estado) -> CandidatoAtendimento:
    return CandidatoAtendimento(
        id_atendimento=id_atendimento,
        estado=estado,
        tipo_evento_registrado=None,
        data_nomeada_registrada=None,
    )


def _registro(id_atendimento: str, estado: Estado) -> RegistroAtendimento:
    return RegistroAtendimento(
        id_atendimento=id_atendimento,
        canal=CANAL,
        contato=CONTATO,
        estado_conversa=estado.value,
        dados_coletados={"tipo_evento": "evento ficticio"},
        instante_ultima_transicao=MARCO,
    )


def _decisao(
    identidade: Identidade | None, alvo: str | None, criterio: CriterioIdentidade
) -> DecisaoIdentidade:
    return DecisaoIdentidade(
        identidade=identidade,
        id_atendimento_alvo=alvo,
        criterio=criterio,
        candidatos_avaliados=(),
        classificacao_por_candidato=(),
        vinculo_declarado=Vinculo.SEM_DECLARACAO,
        situacao_takeover=SituacaoTakeover.SEM_TAKEOVER,
        escopo_restrito_por_identificador=False,
    )


def _fixar_decisao(monkeypatch: pytest.MonkeyPatch, decisao: DecisaoIdentidade) -> None:
    monkeypatch.setattr(
        orchestrator_identity, "resolver_identidade", lambda *a, **k: decisao
    )


def _sem_efeito(deps: DepsTeste, chave: str) -> None:
    assert deps.persistencia.recuperar_pendentes() == ()
    assert deps.alertas == []
    assert not deps.persistencia.chave_processada(chave)


# --------------------------------------------------------------------------
# Interpretação única (CN4)
# --------------------------------------------------------------------------


def test_interpretacao_chamada_exatamente_uma_vez(
    deps_fake, entrada, normalizada, projecoes_vazias
):
    coordenar_etapas_4_e_5(entrada, normalizada, projecoes_vazias, deps_fake)
    assert deps_fake.produtor.chamadas == 1


# --------------------------------------------------------------------------
# FalhaProdutorInterpretacao
# --------------------------------------------------------------------------


def test_llm_indisponivel_preserva_e_alerta_sem_marcar_chave(
    deps_produtor_falha, entrada, normalizada, projecoes_vazias
):
    r = coordenar_etapas_4_e_5(entrada, normalizada, projecoes_vazias, deps_produtor_falha)
    assert r is DesfechoTerminal.INTERPRETACAO_INDISPONIVEL
    assert deps_produtor_falha.persistencia.recuperar_pendentes()
    assert deps_produtor_falha.alertas[-1]["categoria"] == "FalhaProdutorInterpretacao"
    assert not deps_produtor_falha.persistencia.chave_processada(normalizada.chave_idempotencia)


def test_llm_indisponivel_preserva_mensagem_normalizada_e_alerta_sanitizado(
    deps_produtor_falha, entrada, normalizada, projecoes_vazias
):
    coordenar_etapas_4_e_5(entrada, normalizada, projecoes_vazias, deps_produtor_falha)
    (pendente,) = deps_produtor_falha.persistencia.recuperar_pendentes()
    assert (pendente.canal, pendente.contato, pendente.conteudo) == (
        CANAL,
        CONTATO,
        normalizada.mensagem_normalizada,
    )
    assert deps_produtor_falha.alertas == [
        {
            "categoria": "FalhaProdutorInterpretacao",
            "pendente_preservado": True,
            "correlacao": normalizada.chave_idempotencia,
        }
    ]
    assert deps_produtor_falha.produtor.chamadas == 1


def test_erro_de_contrato_da_interpretacao_propaga_intacto(
    base_motor, entrada, normalizada, projecoes_vazias
):
    deps = _montar_deps(
        base_motor, ProdutorContado(_payload_vazio(tipo_evento_sem_confianca="festa"))
    )
    with pytest.raises(ValueError, match="E-Nb"):
        coordenar_etapas_4_e_5(entrada, normalizada, projecoes_vazias, deps)
    _sem_efeito(deps, normalizada.chave_idempotencia)


# --------------------------------------------------------------------------
# HUMANO_MULTIPLO (R5-P0)
# --------------------------------------------------------------------------


def test_humano_multiplo_preserva_alerta_e_marca_chave(deps_fake, entrada, normalizada):
    for id_ in ("at-h1", "at-h2"):
        deps_fake.persistencia.criar(_registro(id_, Estado.ATENDIMENTO_HUMANO))
    projecoes = _projecoes(
        candidatos=(
            _candidato("at-h1", Estado.ATENDIMENTO_HUMANO),
            _candidato("at-h2", Estado.ATENDIMENTO_HUMANO),
        ),
        havia_estado_esperado=True,
        humanos=("at-h1", "at-h2"),
    )
    r = coordenar_etapas_4_e_5(entrada, normalizada, projecoes, deps_fake)
    assert r is DesfechoTerminal.HUMANO_MULTIPLO
    assert len(deps_fake.persistencia.recuperar_pendentes()) == 1
    assert deps_fake.alertas == [
        {
            "categoria": "HUMANO_MULTIPLO",
            "pendente_preservado": True,
            "correlacao": normalizada.chave_idempotencia,
        }
    ]
    assert deps_fake.persistencia.chave_processada(normalizada.chave_idempotencia)


# --------------------------------------------------------------------------
# SEM_CANDIDATO_ELEGIVEL (contrato E4)
# --------------------------------------------------------------------------


def test_sem_candidato_elegivel_preserva_alerta_e_marca_chave(
    deps_fake, entrada, normalizada
):
    projecoes = _projecoes(havia_estado_esperado=True)
    r = coordenar_etapas_4_e_5(entrada, normalizada, projecoes, deps_fake)
    assert r is DesfechoTerminal.SEM_CANDIDATO_ELEGIVEL
    assert len(deps_fake.persistencia.recuperar_pendentes()) == 1
    assert deps_fake.alertas == [
        {
            "categoria": "SEM_CANDIDATO_ELEGIVEL",
            "pendente_preservado": True,
            "correlacao": normalizada.chave_idempotencia,
        }
    ]
    assert deps_fake.persistencia.chave_processada(normalizada.chave_idempotencia)


def test_sem_candidato_elegivel_alerta_que_falha_ainda_marca_chave(
    deps_fake, entrada, normalizada
):
    """E4-12 — pendente já preservado: a falha do alerta não impede a marcação."""

    def alerta_que_falha(**_: Any) -> None:
        raise RuntimeError("alerta indisponivel")

    deps = DepsTeste(**{**deps_fake.__dict__, "tentar_alerta": alerta_que_falha})
    r = coordenar_etapas_4_e_5(entrada, normalizada, _projecoes(havia_estado_esperado=True), deps)
    assert r is DesfechoTerminal.SEM_CANDIDATO_ELEGIVEL
    assert deps.persistencia.chave_processada(normalizada.chave_idempotencia)


def test_sem_candidato_elegivel_falha_ao_preservar_nao_marca_e_tenta_alerta(
    deps_fake, entrada, normalizada
):
    """E4-11 — preservação falhou: alerta tentado, chave não marcada, erro propaga."""
    erro = OSError("falha de preservacao ficticia")

    class PersistenciaQueFalha(PersistenciaEmMemoria):
        def preservar_pendente(self, pendente: Any) -> None:
            raise erro

    deps = DepsTeste(**{**deps_fake.__dict__, "persistencia": PersistenciaQueFalha()})
    with pytest.raises(OSError) as capturado:
        coordenar_etapas_4_e_5(
            entrada, normalizada, _projecoes(havia_estado_esperado=True), deps
        )
    assert capturado.value is erro
    assert deps.alertas[-1]["pendente_preservado"] is False
    assert not deps.persistencia.chave_processada(normalizada.chave_idempotencia)


# --------------------------------------------------------------------------
# AMBIGUA (A1–A7)
# --------------------------------------------------------------------------


def test_ambigua_preserva_pendente_sem_alerta_e_sem_marcar_chave(
    deps_fake, entrada, normalizada, monkeypatch
):
    deps_fake.persistencia.criar(_registro("at-1", Estado.ENCERRADO))
    antes = deps_fake.persistencia.recuperar_por_id("at-1", CANAL, CONTATO).registro
    _fixar_decisao(
        monkeypatch,
        _decisao(Identidade.AMBIGUA, None, CriterioIdentidade.AMBIGUIDADE_SINAIS_INSUFICIENTES),
    )
    r = coordenar_etapas_4_e_5(entrada, normalizada, _projecoes(), deps_fake)
    assert r is DesfechoTerminal.AMBIGUA
    # A7 — pendente persistido; A2 — atendimento anterior intacto.
    assert len(deps_fake.persistencia.recuperar_pendentes()) == 1
    assert deps_fake.persistencia.recuperar_por_id("at-1", CANAL, CONTATO).registro == antes
    assert deps_fake.alertas == []
    assert not deps_fake.persistencia.chave_processada(normalizada.chave_idempotencia)


# --------------------------------------------------------------------------
# HUMANO_UNICO (R5-P0)
# --------------------------------------------------------------------------


def test_humano_unico_prossegue_com_estado_atendimento_humano(
    deps_fake, entrada, normalizada
):
    deps_fake.persistencia.criar(_registro("at-h1", Estado.ATENDIMENTO_HUMANO))
    projecoes = _projecoes(
        candidatos=(_candidato("at-h1", Estado.ATENDIMENTO_HUMANO),),
        havia_estado_esperado=True,
        humanos=("at-h1",),
    )
    r = coordenar_etapas_4_e_5(entrada, normalizada, projecoes, deps_fake)
    assert isinstance(r, AlvoDoCiclo)
    assert r.decisao_identidade.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert r.decisao_identidade.identidade is None
    assert r.atendimento.id_atendimento == "at-h1"
    assert r.atendimento.estado is Estado.ATENDIMENTO_HUMANO
    assert r.atendimento.marco_atual == MARCO
    _sem_efeito(deps_fake, normalizada.chave_idempotencia)


# --------------------------------------------------------------------------
# NOVA_SOLICITACAO / PRIMEIRO_CONTATO_COMPROVADO — nada herdado (I15)
# --------------------------------------------------------------------------


def test_primeiro_contato_hidrata_atendimento_novo(
    deps_fake, entrada, normalizada, projecoes_vazias
):
    r = coordenar_etapas_4_e_5(entrada, normalizada, projecoes_vazias, deps_fake)
    assert isinstance(r, AlvoDoCiclo)
    assert r.decisao_identidade.criterio is CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO
    assert r.atendimento.id_atendimento is None
    assert r.atendimento.estado is Estado.NOVO
    assert r.atendimento.marco_atual is None
    _sem_efeito(deps_fake, normalizada.chave_idempotencia)


def test_nova_solicitacao_nao_herda_dado_do_anterior(
    deps_fake, entrada, normalizada, monkeypatch
):
    deps_fake.persistencia.criar(_registro("at-1", Estado.ENCERRADO))
    _fixar_decisao(
        monkeypatch,
        _decisao(
            Identidade.NOVA_SOLICITACAO, None, CriterioIdentidade.NOVO_EVENTO_DECLARADO
        ),
    )
    r = coordenar_etapas_4_e_5(entrada, normalizada, _projecoes(), deps_fake)
    assert isinstance(r, AlvoDoCiclo)
    assert r.atendimento.id_atendimento is None
    assert r.atendimento.estado is Estado.NOVO
    assert r.atendimento.dados.atendimento.tipo_evento is None
    _sem_efeito(deps_fake, normalizada.chave_idempotencia)


# --------------------------------------------------------------------------
# ATENDIMENTO_ATIVO / MESMA_SOLICITACAO — hidratar o alvo persistido
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("identidade", "estado", "criterio"),
    [
        (
            Identidade.ATENDIMENTO_ATIVO,
            Estado.COLETANDO_DADOS,
            CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO,
        ),
        (
            Identidade.MESMA_SOLICITACAO,
            Estado.ENCERRADO,
            CriterioIdentidade.CONTINUIDADE_DECLARADA_CANDIDATO_UNICO,
        ),
    ],
)
def test_alvo_existente_e_hidratado_da_persistencia(
    deps_fake, entrada, normalizada, monkeypatch, identidade, estado, criterio
):
    deps_fake.persistencia.criar(_registro("at-1", estado))
    _fixar_decisao(monkeypatch, _decisao(identidade, "at-1", criterio))
    r = coordenar_etapas_4_e_5(entrada, normalizada, _projecoes(), deps_fake)
    assert isinstance(r, AlvoDoCiclo)
    assert r.decisao_identidade.identidade is identidade
    assert r.atendimento.id_atendimento == "at-1"
    assert r.atendimento.estado is estado
    assert r.atendimento.dados.atendimento.tipo_evento == "evento ficticio"
    assert r.atendimento.marco_atual == MARCO
    _sem_efeito(deps_fake, normalizada.chave_idempotencia)


def test_atendimento_ativo_real_pela_cascata(deps_fake, entrada, normalizada):
    deps_fake.persistencia.criar(_registro("at-1", Estado.COLETANDO_DADOS))
    projecoes = _projecoes(
        candidatos=(_candidato("at-1", Estado.COLETANDO_DADOS),),
        havia_estado_esperado=True,
    )
    r = coordenar_etapas_4_e_5(entrada, normalizada, projecoes, deps_fake)
    assert isinstance(r, AlvoDoCiclo)
    assert r.decisao_identidade.identidade is Identidade.ATENDIMENTO_ATIVO
    assert r.atendimento.id_atendimento == "at-1"
    assert r.atendimento.estado is Estado.COLETANDO_DADOS


def test_alvo_nao_recuperavel_falha_fechado(deps_fake, entrada, normalizada, monkeypatch):
    _fixar_decisao(
        monkeypatch,
        _decisao(
            Identidade.ATENDIMENTO_ATIVO, "at-ausente", CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO
        ),
    )
    with pytest.raises(ValueError, match="não recuperável"):
        coordenar_etapas_4_e_5(entrada, normalizada, _projecoes(), deps_fake)
    _sem_efeito(deps_fake, normalizada.chave_idempotencia)


def test_alvo_humano_unico_fora_de_atendimento_humano_falha_fechado(
    deps_fake, entrada, normalizada
):
    deps_fake.persistencia.criar(_registro("at-h1", Estado.COLETANDO_DADOS))
    projecoes = _projecoes(
        candidatos=(_candidato("at-h1", Estado.ATENDIMENTO_HUMANO),),
        havia_estado_esperado=True,
        humanos=("at-h1",),
    )
    with pytest.raises(ValueError, match="fora de atendimento_humano"):
        coordenar_etapas_4_e_5(entrada, normalizada, projecoes, deps_fake)


def test_alvo_obrigatorio_ausente_falha_fechado(deps_fake, entrada, normalizada, monkeypatch):
    _fixar_decisao(
        monkeypatch,
        _decisao(Identidade.ATENDIMENTO_ATIVO, None, CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO),
    )
    with pytest.raises(ValueError, match="sem alvo obrigatório"):
        coordenar_etapas_4_e_5(entrada, normalizada, _projecoes(), deps_fake)
    _sem_efeito(deps_fake, normalizada.chave_idempotencia)


def test_decisao_fora_do_vocabulario_falha_fechado(deps_fake, entrada, normalizada, monkeypatch):
    # Identidade None com critério que não é primeiro contato nem E4.
    _fixar_decisao(
        monkeypatch,
        _decisao(None, None, CriterioIdentidade.INERCIA_ATENDIMENTO_ATIVO),
    )
    with pytest.raises(ValueError, match="fora do vocabulário"):
        coordenar_etapas_4_e_5(entrada, normalizada, _projecoes(), deps_fake)
    _sem_efeito(deps_fake, normalizada.chave_idempotencia)
