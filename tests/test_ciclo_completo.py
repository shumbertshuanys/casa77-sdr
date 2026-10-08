"""Ciclo ponta a ponta — `processar_mensagem` e a etapa 14 (doc 07 §5; doc 06 §10).

Base real (`carregar_base_motor`), `PersistenciaEmMemoria` com registro da
ordem das chamadas, produtor fake roteirizado (um *payload* estruturado por
chamada) e `enviar_mensagem`/`entregar_resumo`/`tentar_alerta` gravadores. O
`gerar_id` é um contador determinístico.

As asserções são por enum (`DesfechoCiclo`, `Estado`) e por ordem de efeitos;
o texto esperado, quando existe, é obtido pela mesma cadeia aprovada — nunca
escrito à mão. Valores sintéticos; zero valor comercial literal.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import orchestrator, orchestrator_identity
from casa77_sdr.coverage_decision import DecisaoCoberturaNaoAvaliavel
from casa77_sdr.coverage_map import MapaCoberturaInvalido
from casa77_sdr.fact_selection import materializar_fatos_autorizados
from casa77_sdr.identity import (
    CriterioIdentidade,
    DecisaoIdentidade,
    Identidade,
    SituacaoTakeover,
    Vinculo,
)
from casa77_sdr.motor_deps import BaseMotor, DependenciasMotor, carregar_base_motor
from casa77_sdr.normalization import EntradaMensagem, normalizar_entrada
from casa77_sdr.orchestrator import (
    DesfechoCiclo,
    FalhaEntregaResumo,
    ResultadoCiclo,
    processar_mensagem,
)
from casa77_sdr.persistence import (
    FalhaDePersistencia,
    PersistenciaEmMemoria,
    ProcessamentoPendente,
    RegistroAtendimento,
)
from casa77_sdr.pricing_applicability import AplicabilidadeNaoAvaliavel
from casa77_sdr.response_assembly import montar_resposta_final
from casa77_sdr.response_assertion import AssertivaNaoAvaliavel
from casa77_sdr.response_composition import compor_textos_emitiveis
from casa77_sdr.response_index import IndiceInvalido
from casa77_sdr.response_index_tokens import ProjecaoDeIdentidadeInvalida
from casa77_sdr.state_machine import Estado

RAIZ = Path(__file__).resolve().parents[1]
INICIO = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
JANELA = timedelta(minutes=5)
LIMIAR = timedelta(days=30)
CANAL = "teste"
CONTATO = "contato-ficticio"


# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------


def _slot(valor: str | None) -> dict[str, Any]:
    if valor is None:
        return {"presente": False, "valor": "alta"}
    return {"presente": True, "valor": valor}


def _payload(
    *,
    dados: dict[str, Any] | None = None,
    perguntas: tuple[str, ...] = (),
    pedido_de_humano: bool = False,
    intencoes: tuple[str, ...] = (),
) -> str:
    extraidos: dict[str, Any] = {}
    for campo in ("tipo_evento", "data_nomeada", "convidados", "formato", "nome", "contato"):
        valor = (dados or {}).get(campo)
        extraidos[campo] = valor
        extraidos[f"confianca_{campo}"] = _slot(None if valor is None else "alta")
    return json.dumps(
        {
            "dados_extraidos": extraidos,
            "correcoes": [],
            "perguntas_comerciais": [
                {"texto": f"pergunta ficticia {a}", "confianca": _slot("alta"), "assunto": a}
                for a in perguntas
            ],
            "pedido_de_humano": pedido_de_humano,
            "confianca_pedido_de_humano": _slot("alta" if pedido_de_humano else None),
            "referencias_evento_anterior": [],
            "trechos_ambiguos": [],
            "confianca_global": _slot("alta"),
            "intencoes_autonomas": [
                {"codigo": codigo, "confianca": _slot("alta")} for codigo in intencoes
            ],
        }
    )


class ProdutorRoteirizado:
    """Devolve o próximo *payload* do roteiro a cada chamada."""

    def __init__(self, roteiro: list[str]) -> None:
        self.roteiro = list(roteiro)
        self.chamadas = 0

    def produzir(self, *, prompt_sistema: str, mensagem: str, schema: dict[str, Any]) -> str:
        self.chamadas += 1
        return self.roteiro.pop(0)


class PersistenciaGravadora(PersistenciaEmMemoria):
    """`PersistenciaEmMemoria` que registra a ordem das escritas num log comum."""

    def __init__(self, log: list[tuple[str, Any]]) -> None:
        super().__init__()
        self.log = log

    def criar(self, registro: RegistroAtendimento) -> None:
        super().criar(registro)
        self.log.append(("criar", registro.estado_conversa))

    def gravar(self, registro: RegistroAtendimento) -> None:
        super().gravar(registro)
        self.log.append(("gravar", registro.estado_conversa))

    def marcar_chave_processada(self, chave: str) -> None:
        super().marcar_chave_processada(chave)
        self.log.append(("marcar", chave))

    def preservar_pendente(self, pendente: ProcessamentoPendente) -> None:
        super().preservar_pendente(pendente)
        self.log.append(("preservar", None))


class PersistenciaQueFalha(PersistenciaGravadora):
    def criar(self, registro: RegistroAtendimento) -> None:
        raise FalhaDePersistencia("falha sintetica")

    def gravar(self, registro: RegistroAtendimento) -> None:
        raise FalhaDePersistencia("falha sintetica")


class Cenario:
    """Dependências do ciclo com todos os efeitos gravados num único log."""

    def __init__(
        self,
        base_motor: BaseMotor,
        roteiro: list[str],
        *,
        falha_entrega: bool = False,
        persistencia_falha: bool = False,
    ) -> None:
        self.log: list[tuple[str, Any]] = []
        self.envios: list[tuple[str, str, str]] = []
        self.resumos: list[str] = []
        self.alertas: list[dict[str, Any]] = []
        self.produtor = ProdutorRoteirizado(roteiro)
        classe = PersistenciaQueFalha if persistencia_falha else PersistenciaGravadora
        self.persistencia = classe(self.log)
        self._ids = 0

        def enviar(canal: str, contato: str, texto: str) -> None:
            self.envios.append((canal, contato, texto))
            self.log.append(("enviar", texto))

        def entregar(resumo: str) -> None:
            self.log.append(("entregar_resumo", None))
            if falha_entrega:
                raise FalhaEntregaResumo("falha sintetica")
            self.resumos.append(resumo)

        def alertar(**kwargs: Any) -> None:
            self.alertas.append(kwargs)
            self.log.append(("alerta", kwargs["categoria"]))

        self.deps = DependenciasMotor(
            base_motor=base_motor,
            persistencia=self.persistencia,
            produtor=self.produtor,
            prompt_sistema="prompt ficticio",
            janela_idempotencia=JANELA,
            limiar_recencia=LIMIAR,
            calendario_integrado=False,
            tentar_alerta=alertar,
            enviar_mensagem=enviar,
            entregar_resumo=entregar,
        )

    def gerar_id(self) -> str:
        self._ids += 1
        return f"at-{self._ids}"

    def processar(self, entrada: EntradaMensagem) -> ResultadoCiclo:
        return processar_mensagem(entrada, self.deps, gerar_id=self.gerar_id)

    def registro(self, id_atendimento: str = "at-1") -> RegistroAtendimento:
        recuperacao = self.persistencia.recuperar_por_id(id_atendimento, CANAL, CONTATO)
        assert recuperacao.registro is not None
        return recuperacao.registro

    def efeitos(self) -> list[str]:
        return [nome for nome, _ in self.log]


@pytest.fixture(scope="module")
def base_motor() -> BaseMotor:
    return carregar_base_motor(RAIZ)


def _entrada(mensagem: str, minutos: int = 0) -> EntradaMensagem:
    return EntradaMensagem(
        canal=CANAL,
        contato=CONTATO,
        mensagem=mensagem,
        recebida_em=INICIO + timedelta(minutes=minutos),
    )


def _chave(entrada: EntradaMensagem) -> str:
    return normalizar_entrada(entrada, JANELA).chave_idempotencia


def _texto_aprovado(base_motor: BaseMotor, tokens: tuple[str, ...]) -> str:
    selecao = materializar_fatos_autorizados(
        base_motor.indice, base_motor.base, base_motor.textos, tokens
    )
    return montar_resposta_final(compor_textos_emitiveis(selecao)).texto


def _decisao_identidade(identidade: Identidade, criterio: CriterioIdentidade) -> DecisaoIdentidade:
    return DecisaoIdentidade(
        identidade=identidade,
        id_atendimento_alvo=None,
        criterio=criterio,
        candidatos_avaliados=(),
        classificacao_por_candidato=(),
        vinculo_declarado=Vinculo.SEM_DECLARACAO,
        situacao_takeover=SituacaoTakeover.SEM_TAKEOVER,
        escopo_restrito_por_identificador=False,
    )


def _gravar_registro(cenario: Cenario, estado: Estado) -> None:
    cenario.persistencia.criar(
        RegistroAtendimento(
            id_atendimento="at-existente",
            canal=CANAL,
            contato=CONTATO,
            estado_conversa=estado.value,
            dados_coletados={},
            instante_ultima_transicao=INICIO - timedelta(hours=1),
        )
    )
    cenario.log.clear()


# --------------------------------------------------------------------------
# Conversa de três mensagens
# --------------------------------------------------------------------------


def test_conversa_de_tres_mensagens_avanca_pela_maquina(base_motor):
    convidados = base_motor.base["capacidade"]["convidados_sentados"]
    cenario = Cenario(
        base_motor,
        [
            _payload(),
            _payload(dados={"tipo_evento": "evento ficticio", "convidados": convidados}),
            _payload(dados={"nome": "Nome Ficticio"}),
        ],
    )

    r1 = cenario.processar(_entrada("ola, mensagem ficticia"))
    assert r1.estado_final is Estado.COLETANDO_DADOS
    assert cenario.registro().estado_conversa == Estado.COLETANDO_DADOS.value

    r2 = cenario.processar(_entrada("evento ficticio para convidados", minutos=10))
    assert r2.estado_final is Estado.COLETANDO_DADOS
    dados = cenario.registro().dados_coletados
    assert dados["tipo_evento"] == "evento ficticio"
    assert dados["convidados"] == convidados

    r3 = cenario.processar(_entrada("meu nome e ficticio", minutos=20))
    assert r3.estado_final is Estado.COLETANDO_DADOS
    assert cenario.registro().dados_coletados["nome"] == "Nome Ficticio"

    # Um único atendimento (a identidade reconheceu o atendimento ativo).
    assert cenario._ids == 1
    assert cenario.produtor.chamadas == 3
    # M2.1: saudação no 1º contato e, depois, a pergunta do primeiro campo
    # ausente na prioridade natural (tipo, data, convidados, nome, contato): a
    # data continua ausente nas duas mensagens seguintes.
    esperados = (
        _texto_aprovado(base_motor, ("R01/F1",)),
        _texto_aprovado(base_motor, ("R31/F3",)),
        _texto_aprovado(base_motor, ("R31/F3",)),
    )
    for r, esperado in zip((r1, r2, r3), esperados, strict=True):
        assert r.desfecho is DesfechoCiclo.RESPONDIDA
        assert r.texto_emitido == esperado
    assert cenario.envios == [(CANAL, CONTATO, texto) for texto in esperados]
    assert [e for e in cenario.efeitos() if e in ("criar", "gravar")] == [
        "criar",
        "gravar",
        "gravar",
    ]
    assert cenario.efeitos().count("marcar") == 3


def test_pergunta_comercial_e_respondida_com_o_texto_aprovado(base_motor):
    cenario = Cenario(base_motor, [_payload(perguntas=("preco_locacao",))])
    r = cenario.processar(_entrada("quanto custa, mensagem ficticia"))
    assert r.desfecho is DesfechoCiclo.RESPONDIDA
    assert r.texto_emitido is not None
    assert cenario.envios == [(CANAL, CONTATO, r.texto_emitido)]
    assert r.estado_final is not None
    assert cenario.registro().estado_conversa == r.estado_final.value


def test_convidados_acima_da_capacidade_sentada_recebem_a_ressalva_sem_pergunta_de_formato(
    base_motor,
):
    # Decisão do Victor (2026-10-08): o bot não pergunta o formato; acima de
    # `capacidade.convidados_sentados` (até `formato_coquetel`) envia a
    # ressalva de capacidade aprovada e segue.
    acima = base_motor.base["capacidade"]["convidados_sentados"] + 1
    assert acima <= base_motor.base["capacidade"]["formato_coquetel"]
    cenario = Cenario(
        base_motor,
        [
            _payload(),
            _payload(
                dados={
                    "tipo_evento": "evento ficticio",
                    "data_nomeada": "data ficticia",
                    "nome": "Nome Ficticio",
                    "contato": "contato-ficticio",
                }
            ),
            _payload(dados={"convidados": acima}),
        ],
    )
    cenario.processar(_entrada("ola, mensagem ficticia"))
    r2 = cenario.processar(_entrada("dados ficticios do evento", minutos=10))
    # Falta só convidados: a pergunta é a de convidados.
    assert r2.texto_emitido == _texto_aprovado(base_motor, ("R31/F4",))

    r3 = cenario.processar(_entrada("convidados ficticios", minutos=20))

    # A ressalva aprovada (R34/F1) é dita e o atendimento segue para o
    # encaminhamento (T08): nenhuma pergunta de formato, nenhum silêncio.
    ressalva = _texto_aprovado(base_motor, ("R34/F1",))
    encaminhamento = _texto_aprovado(base_motor, ("R08/F1",))
    assert r3.desfecho is DesfechoCiclo.RESPONDIDA
    assert r3.texto_emitido == ressalva
    assert cenario.envios[-2:] == [
        (CANAL, CONTATO, ressalva),
        (CANAL, CONTATO, encaminhamento),
    ]
    assert r3.estado_final is Estado.ENCAMINHADO_HUMANO
    assert len(cenario.resumos) == 1
    assert cenario.registro().dados_coletados.get("formato") is None


# --------------------------------------------------------------------------
# Aceitação M2.1 — conversa útil
# --------------------------------------------------------------------------


def test_saudacao_com_interesse_em_visita_vira_uma_mensagem_continua(base_motor):
    cenario = Cenario(base_motor, [_payload(intencoes=("INTERESSE_EM_VISITA",))])
    r = cenario.processar(
        _entrada("Ola boa noite. Muito linda a casa, tenho interesse visitar.")
    )

    saudacao = _texto_aprovado(base_motor, ("R01/F1",))
    visita = _texto_aprovado(base_motor, ("R06/F1",))
    esperado = saudacao + "\n\n" + visita
    assert r.desfecho is DesfechoCiclo.RESPONDIDA
    assert r.texto_emitido == esperado
    # Uma única mensagem enviada; nenhuma quebra simples dentro de parágrafo.
    assert cenario.envios == [(CANAL, CONTATO, esperado)]
    for paragrafo in esperado.split("\n\n"):
        assert "\n" not in paragrafo


def test_conversa_de_cinco_mensagens_responde_cada_turno_e_encaminha(base_motor):
    cenario = Cenario(
        base_motor,
        [
            _payload(),
            _payload(perguntas=("preco_locacao",)),
            _payload(dados={"tipo_evento": "evento ficticio"}),
            _payload(
                dados={
                    "data_nomeada": "data ficticia",
                    "convidados": base_motor.base["capacidade"]["convidados_sentados"],
                    "nome": "Nome Ficticio",
                }
            ),
            _payload(dados={"contato": "contato-ficticio"}),
        ],
    )
    textos = lambda *tokens: _texto_aprovado(base_motor, tokens)  # noqa: E731

    r1 = cenario.processar(_entrada("ola, mensagem ficticia"))
    assert r1.desfecho is DesfechoCiclo.RESPONDIDA
    assert r1.texto_emitido == textos("R01/F1")

    # Resposta comercial: resposta aprovada, retomada e a próxima pergunta
    # (tipo de evento, primeiro na prioridade).
    r2 = cenario.processar(_entrada("quanto custa, mensagem ficticia", minutos=10))
    assert r2.desfecho is DesfechoCiclo.RESPONDIDA
    assert r2.texto_emitido is not None
    assert r2.texto_emitido.endswith(textos("R32/F1") + "\n\n" + textos("R31/F2"))

    # Falta data, convidados, nome, contato: pergunta a data.
    r3 = cenario.processar(_entrada("evento ficticio", minutos=20))
    assert r3.desfecho is DesfechoCiclo.RESPONDIDA
    assert r3.texto_emitido == textos("R31/F3")

    # Falta só o contato.
    r4 = cenario.processar(_entrada("dados ficticios", minutos=30))
    assert r4.desfecho is DesfechoCiclo.RESPONDIDA
    assert r4.texto_emitido == textos("R31/F5")
    assert r4.estado_final is Estado.COLETANDO_DADOS
    assert cenario.resumos == []

    r5 = cenario.processar(_entrada("contato ficticio", minutos=40))
    assert r5.desfecho is DesfechoCiclo.RESPONDIDA
    assert r5.estado_final is Estado.ENCAMINHADO_HUMANO
    assert r5.texto_emitido == textos("R08/F1")
    assert len(cenario.resumos) == 1
    assert cenario.log[-1] == ("enviar", textos("R08/F1"))
    efeitos = cenario.efeitos()
    assert efeitos.index("entregar_resumo") < len(efeitos) - 1
    assert cenario.registro().estado_conversa == Estado.ENCAMINHADO_HUMANO.value
    # Nenhum turno silencioso: um envio por mensagem recebida.
    assert len(cenario.envios) == 5


# --------------------------------------------------------------------------
# Review Focus 1 — idempotência ponta a ponta
# --------------------------------------------------------------------------


def test_reentrega_da_mesma_entrada_e_ignorada_sem_envio_adicional(base_motor):
    cenario = Cenario(
        base_motor, [_payload(perguntas=("preco_locacao",)), _payload(perguntas=("preco_locacao",))]
    )
    entrada = _entrada("quanto custa, mensagem ficticia")
    primeira = cenario.processar(entrada)
    assert primeira.desfecho is DesfechoCiclo.RESPONDIDA
    envios = list(cenario.envios)

    segunda = cenario.processar(entrada)
    assert segunda == ResultadoCiclo(DesfechoCiclo.IGNORADA, None, None)
    assert cenario.envios == envios
    assert cenario.produtor.chamadas == 1


def test_mensagem_vazia_e_ignorada(base_motor):
    cenario = Cenario(base_motor, [])
    r = cenario.processar(_entrada("   "))
    assert r == ResultadoCiclo(DesfechoCiclo.IGNORADA, None, None)
    assert cenario.log == []


# --------------------------------------------------------------------------
# Review Focus 4 — atendimento humano
# --------------------------------------------------------------------------


def test_atendimento_humano_e_silencioso_sem_envio(base_motor):
    cenario = Cenario(base_motor, [_payload(perguntas=("preco_locacao",))])
    _gravar_registro(cenario, Estado.ATENDIMENTO_HUMANO)

    r = cenario.processar(_entrada("quanto custa, mensagem ficticia"))
    assert r.desfecho is DesfechoCiclo.SILENCIOSA
    assert r.texto_emitido is None
    assert r.estado_final is Estado.ATENDIMENTO_HUMANO
    assert cenario.envios == []
    assert cenario.resumos == []
    assert "enviar" not in cenario.efeitos()


# --------------------------------------------------------------------------
# Etapa 13 antecede a 14
# --------------------------------------------------------------------------


def test_nada_e_enviado_antes_da_etapa_13_gravar_e_marcar(base_motor):
    cenario = Cenario(base_motor, [_payload(perguntas=("preco_locacao",))])
    cenario.processar(_entrada("quanto custa, mensagem ficticia"))
    efeitos = cenario.efeitos()
    assert "enviar" in efeitos
    assert efeitos.index("criar") < efeitos.index("marcar") < efeitos.index("enviar")


def test_falha_de_persistencia_bloqueia_sem_envio(base_motor):
    cenario = Cenario(
        base_motor, [_payload(perguntas=("preco_locacao",))], persistencia_falha=True
    )
    entrada = _entrada("quanto custa, mensagem ficticia")
    r = cenario.processar(entrada)
    assert r == ResultadoCiclo(DesfechoCiclo.BLOQUEADA_PERSISTENCIA, None, None)
    assert cenario.envios == []
    assert not cenario.persistencia.chave_processada(_chave(entrada))
    assert len(cenario.persistencia.recuperar_pendentes()) == 1


# --------------------------------------------------------------------------
# Handoff — entrega do resumo e mensagem de encaminhamento (doc 06 §10)
# --------------------------------------------------------------------------


def test_handoff_entrega_resumo_antes_do_encaminhamento(base_motor):
    cenario = Cenario(base_motor, [_payload(pedido_de_humano=True)])
    r = cenario.processar(_entrada("quero falar com uma pessoa, ficticio"))

    encaminhamento = _texto_aprovado(base_motor, ("R08/F1",))
    assert r.desfecho is DesfechoCiclo.RESPONDIDA
    assert r.estado_final is Estado.ENCAMINHADO_HUMANO
    assert len(cenario.resumos) == 1
    assert cenario.envios[-1] == (CANAL, CONTATO, encaminhamento)
    efeitos = cenario.efeitos()
    assert (
        efeitos.index("criar")
        < efeitos.index("marcar")
        < efeitos.index("entregar_resumo")
        < len(efeitos) - 1
    )
    assert cenario.log[-1] == ("enviar", encaminhamento)
    # Só o encaminhamento foi dito: ele é o texto emitido.
    assert r.texto_emitido == encaminhamento


def test_falha_na_entrega_do_resumo_nao_envia_encaminhamento(base_motor):
    cenario = Cenario(base_motor, [_payload(pedido_de_humano=True)], falha_entrega=True)
    entrada = _entrada("quero falar com uma pessoa, ficticio")
    r = cenario.processar(entrada)

    encaminhamento = _texto_aprovado(base_motor, ("R08/F1",))
    assert all(texto != encaminhamento for _, _, texto in cenario.envios)
    assert cenario.envios == []
    assert r.desfecho is DesfechoCiclo.SILENCIOSA
    assert r.texto_emitido is None
    # Doc 06 §10: o estado registrado não é revertido; pendente preservado e alerta.
    assert r.estado_final is Estado.ENCAMINHADO_HUMANO
    assert cenario.registro().estado_conversa == Estado.ENCAMINHADO_HUMANO.value
    assert len(cenario.persistencia.recuperar_pendentes()) == 1
    (alerta,) = cenario.alertas
    assert alerta["categoria"] == "FalhaEntregaResumo"
    assert alerta["pendente_preservado"] is True
    assert alerta["correlacao"] == _chave(entrada)
    assert cenario.efeitos()[-2:] == ["preservar", "alerta"]


def test_falha_de_outra_classe_na_entrega_propaga(base_motor):
    cenario = Cenario(base_motor, [_payload(pedido_de_humano=True)])

    def explode(resumo: str) -> None:
        raise RuntimeError("defeito sintetico")

    cenario.deps = replace(cenario.deps, entregar_resumo=explode)
    with pytest.raises(RuntimeError):
        cenario.processar(_entrada("quero falar com uma pessoa, ficticio"))
    assert cenario.envios == []


# --------------------------------------------------------------------------
# AMBIGUA — sem texto aprovado de esclarecimento
# --------------------------------------------------------------------------


def test_ambigua_silencia_alerta_e_marca_a_chave(base_motor, monkeypatch):
    monkeypatch.setattr(
        orchestrator_identity,
        "resolver_identidade",
        lambda *a, **k: _decisao_identidade(
            Identidade.AMBIGUA, CriterioIdentidade.AMBIGUIDADE_SINAIS_INSUFICIENTES
        ),
    )
    cenario = Cenario(base_motor, [_payload()])
    entrada = _entrada("mensagem ficticia ambigua")
    r = cenario.processar(entrada)

    assert r == ResultadoCiclo(DesfechoCiclo.TERMINAL_IDENTIDADE, None, None)
    assert cenario.envios == []
    assert cenario.efeitos() == ["preservar", "alerta", "marcar"]
    (alerta,) = cenario.alertas
    assert alerta == {
        "categoria": "AMBIGUA",
        "pendente_preservado": True,
        "correlacao": _chave(entrada),
    }

    # Reentrega: a chave marcada encerra na etapa 2.
    assert cenario.processar(entrada).desfecho is DesfechoCiclo.IGNORADA
    assert cenario.produtor.chamadas == 1


def test_outro_desfecho_terminal_vira_terminal_identidade(base_motor, monkeypatch):
    monkeypatch.setattr(
        orchestrator_identity,
        "resolver_identidade",
        lambda *a, **k: replace(
            _decisao_identidade(
                Identidade.AMBIGUA, CriterioIdentidade.AMBIGUIDADE_SINAIS_INSUFICIENTES
            ),
            identidade=None,
            criterio=CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL,
        ),
    )
    cenario = Cenario(base_motor, [_payload()])
    r = cenario.processar(_entrada("mensagem ficticia"))
    assert r == ResultadoCiclo(DesfechoCiclo.TERMINAL_IDENTIDADE, None, None)
    assert cenario.envios == []


# --------------------------------------------------------------------------
# Classe I — a base não permite avaliar
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "classe",
    [
        DecisaoCoberturaNaoAvaliavel,
        AplicabilidadeNaoAvaliavel,
        IndiceInvalido,
        MapaCoberturaInvalido,
        ProjecaoDeIdentidadeInvalida,
        AssertivaNaoAvaliavel,
    ],
)
def test_classe_i_bloqueia_sem_envio_e_sem_marcar(base_motor, monkeypatch, classe):
    def falha(*a: Any, **k: Any) -> Any:
        raise classe("categoria_sintetica: localizador")

    monkeypatch.setattr(orchestrator, "decidir_primeira_chamada", falha)
    cenario = Cenario(base_motor, [_payload(perguntas=("preco_locacao",))])
    entrada = _entrada("quanto custa, mensagem ficticia")
    r = cenario.processar(entrada)

    assert r == ResultadoCiclo(DesfechoCiclo.BLOQUEADA_BASE, None, None)
    assert cenario.envios == []
    assert not cenario.persistencia.chave_processada(_chave(entrada))
    assert cenario.efeitos() == ["preservar", "alerta"]
    (alerta,) = cenario.alertas
    assert alerta["categoria"] == classe.__name__


def test_classe_i_nascida_da_fronteira_real(base_motor):
    """Mapa de cobertura corrompido: a fronteira real levanta Classe I."""
    corrompida = replace(base_motor, mapa={})
    cenario = Cenario(corrompida, [_payload(perguntas=("preco_locacao",))])
    entrada = _entrada("quanto custa, mensagem ficticia")
    r = cenario.processar(entrada)
    assert r.desfecho is DesfechoCiclo.BLOQUEADA_BASE
    assert cenario.envios == []
    assert not cenario.persistencia.chave_processada(_chave(entrada))


# --------------------------------------------------------------------------
# Contrato da superfície
# --------------------------------------------------------------------------


def test_desfechos_do_ciclo() -> None:
    assert {d.value for d in DesfechoCiclo} == {
        "ignorada",
        "terminal_identidade",
        "bloqueada_persistencia",
        "bloqueada_base",
        "respondida",
        "silenciosa",
    }


def test_gerar_id_e_obrigatorio_por_palavra_chave(base_motor) -> None:
    cenario = Cenario(base_motor, [])
    chamada: Callable[..., Any] = processar_mensagem
    with pytest.raises(TypeError):
        chamada(_entrada("x"), cenario.deps)
