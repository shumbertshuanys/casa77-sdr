"""Testes da montagem das projeções de identidade da etapa 3 (doc 07 §6.2).

Fixtures totalmente artificiais: canais, contatos e identificadores
claramente fictícios, sem dado pessoal real, sem valor comercial, sem
telefone, sem nome e sem relação com a operação real.

Os testes provam que a montagem é **determinística e somente-leitura**: nada
aqui grava, cria atendimento, marca idempotência, consulta relógio vivo, lê
YAML, usa LLM, usa rede ou chama o `ResolvedorIdentidade`. O encadeamento
3 → 5 é feito **pelo teste**, nunca por `context.py`.

Nenhum valor operacional de limiar é fixado: as durações abaixo são
artificiais e existem apenas para exercitar a borda da regra de recência.
"""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import context
from casa77_sdr.context import (
    ConjuntoHumanoIncoerente,
    IdentificadorNaoResolvido,
    ProjecaoIdentificadorIncoerente,
    ProjecoesIdentidadeEtapa3,
    _verificar_invariantes_de_produtor,
    montar_projecoes_identidade_etapa3,
)
from casa77_sdr.eligibility import (
    ConfiguracaoTemporalInvalida,
    ContextoElegibilidadeCorrompido,
    IdentificadoIncoerente,
    canonicalizar_conjunto_elegivel,
    exigir_limiar_valido,
    produzir_conjunto_elegivel,
    projetar_registros,
    selecionar_conjunto_elegivel,
)
from casa77_sdr.identity import (
    CandidatoAtendimento,
    Confianca,
    CriterioIdentidade,
    DecisaoIdentidade,
    IntencaoIdentidade,
    ProjecaoInterpretacao,
    ReferenciaEventoAnterior,
    SituacaoTakeover,
    VeredictoIdentificador,
    resolver_identidade,
)
from casa77_sdr.persistence import (
    PersistenciaEmMemoria,
    PersistenciaOperacional,
    RecuperacaoPorId,
    RegistroAtendimento,
    ResultadoRecuperacao,
)
from casa77_sdr.state_machine import Estado, Identidade

RAIZ = Path(__file__).resolve().parents[1]
MODULO_CONTEXTO = RAIZ / "src" / "casa77_sdr" / "context.py"

REFERENCIA = datetime(2000, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
LIMIAR = timedelta(days=7)
CANAL = "canal-ficticio"
CONTATO = "contato-ficticio"


def registro_ficticio(
    *,
    id_atendimento: str = "atendimento-fake-a",
    canal: str = CANAL,
    contato: str = CONTATO,
    estado: str | None = "novo",
    dados_coletados: dict[str, Any] | None = None,
    instante_ultima_transicao: datetime | None = None,
) -> RegistroAtendimento:
    """Registro sintético mínimo, sem PII e sem dado comercial."""
    return RegistroAtendimento(
        id_atendimento=id_atendimento,
        canal=canal,
        contato=contato,
        estado_conversa=estado,
        dados_coletados={} if dados_coletados is None else dados_coletados,
        instante_ultima_transicao=instante_ultima_transicao,
    )


# 1. Reuso — validação do limiar (N-a-L1–N-a-L6, S10)


def test_exigir_limiar_valido_devolve_a_duracao_recebida() -> None:
    assert exigir_limiar_valido(LIMIAR) == LIMIAR


@pytest.mark.parametrize(
    "limiar",
    [None, "sete dias", 7, True, timedelta(0), timedelta(seconds=-1)],
)
def test_exigir_limiar_valido_rejeita_limiar_invalido(limiar: object) -> None:
    with pytest.raises(ConfiguracaoTemporalInvalida):
        exigir_limiar_valido(limiar)  # type: ignore[arg-type]


# 2. Reuso — projeção integral dos registros (N-a-P1–N-a-P6)


def test_projetar_registros_preserva_a_ordem_recebida() -> None:
    registros = (
        registro_ficticio(id_atendimento="atendimento-fake-z"),
        registro_ficticio(id_atendimento="atendimento-fake-a"),
    )

    projetados = projetar_registros(registros)

    assert [candidato.id_atendimento for candidato in projetados] == [
        "atendimento-fake-z",
        "atendimento-fake-a",
    ]


def test_projetar_registros_nao_filtra_por_elegibilidade() -> None:
    """Todos os oito estados projetam; a filtragem N-a não acontece aqui."""
    registros = tuple(
        registro_ficticio(id_atendimento=f"atendimento-fake-{i}", estado=estado.value)
        for i, estado in enumerate(Estado)
    )

    projetados = projetar_registros(registros)

    assert len(projetados) == len(tuple(Estado))
    assert {candidato.estado for candidato in projetados} == set(Estado)


def test_projetar_registros_nao_deduplica_ids_repetidos() -> None:
    registros = (
        registro_ficticio(id_atendimento="atendimento-fake-repetido"),
        registro_ficticio(id_atendimento="atendimento-fake-repetido"),
    )

    assert len(projetar_registros(registros)) == 2


def test_projetar_registros_produz_candidatos_de_quatro_campos() -> None:
    registros = (
        registro_ficticio(
            dados_coletados={"tipo_evento": "evento-ficticio", "data_nomeada": "data-ficticia"}
        ),
    )

    assert projetar_registros(registros) == (
        CandidatoAtendimento(
            id_atendimento="atendimento-fake-a",
            estado=Estado.NOVO,
            tipo_evento_registrado="evento-ficticio",
            data_nomeada_registrada="data-ficticia",
        ),
    )


def test_projetar_registros_bloqueia_estado_fora_dos_oito(
) -> None:
    registros = (registro_ficticio(estado="estado-inexistente"),)

    with pytest.raises(ContextoElegibilidadeCorrompido):
        projetar_registros(registros)


def test_projetar_registros_bloqueia_campo_opcional_nao_textual() -> None:
    registros = (registro_ficticio(dados_coletados={"tipo_evento": 7}),)

    with pytest.raises(ContextoElegibilidadeCorrompido):
        projetar_registros(registros)


# 3. Contrato do DTO da fronteira 3 → 5


def test_projecoes_expõem_exatamente_os_cinco_campos_da_fronteira() -> None:
    """Projeção mínima da identidade: nem registro bruto, nem canal, nem PII."""
    assert [campo.name for campo in fields(ProjecoesIdentidadeEtapa3)] == [
        "candidatos_elegiveis",
        "veredito_identificador",
        "id_atendimento_validado",
        "havia_estado_esperado",
        "ids_em_atendimento_humano",
    ]


def test_projecoes_sao_imutaveis() -> None:
    projecoes = ProjecoesIdentidadeEtapa3(
        candidatos_elegiveis=(),
        veredito_identificador=VeredictoIdentificador.NAO_INFORMADO,
        id_atendimento_validado=None,
        havia_estado_esperado=False,
        ids_em_atendimento_humano=(),
    )

    with pytest.raises(FrozenInstanceError):
        projecoes.havia_estado_esperado = True  # type: ignore[misc]


# 4. Montagem sem identificador informado (N1, P-I1)


def montar(
    persistencia: PersistenciaOperacional,
    *,
    id_informado: str | None = None,
    limiar: timedelta | None = LIMIAR,
    instante: datetime = REFERENCIA,
) -> ProjecoesIdentidadeEtapa3:
    return montar_projecoes_identidade_etapa3(
        persistencia,
        canal=CANAL,
        contato=CONTATO,
        id_atendimento_informado=id_informado,
        instante_de_referencia_do_ciclo=instante,
        limiar_recencia=limiar,
    )


def persistencia_com(*registros: RegistroAtendimento) -> PersistenciaEmMemoria:
    persistencia = PersistenciaEmMemoria()
    for registro in registros:
        persistencia.criar(registro)
    return persistencia


def test_sem_identificador_o_veredito_e_nao_informado_e_o_id_validado_e_none() -> None:
    projecoes = montar(persistencia_com(registro_ficticio()))

    assert projecoes.veredito_identificador is VeredictoIdentificador.NAO_INFORMADO
    assert projecoes.id_atendimento_validado is None


def test_conjunto_elegivel_e_delegado_e_chega_canonicalizado() -> None:
    persistencia = persistencia_com(
        registro_ficticio(id_atendimento="atendimento-fake-z"),
        registro_ficticio(id_atendimento="atendimento-fake-a", estado="coletando_dados"),
    )

    projecoes = montar(persistencia)

    assert [
        candidato.id_atendimento for candidato in projecoes.candidatos_elegiveis
    ] == ["atendimento-fake-a", "atendimento-fake-z"]


def test_contato_sem_nenhum_registro_produz_projecoes_vazias() -> None:
    projecoes = montar(PersistenciaEmMemoria())

    assert projecoes.candidatos_elegiveis == ()
    assert projecoes.ids_em_atendimento_humano == ()
    assert projecoes.havia_estado_esperado is False
    assert projecoes.id_atendimento_validado is None


# 5. Ordem normativa dos 14 passos (§6.2)


class PersistenciaEspia(PersistenciaOperacional):
    """Espião somente-leitura: registra a ordem das chamadas do contrato.

    Qualquer operação de **escrita** falha imediatamente — a etapa 3 não cria,
    não grava, não marca idempotência e não preserva pendente.
    """

    def __init__(self, interna: PersistenciaEmMemoria) -> None:
        self._interna = interna
        self.chamadas: list[str] = []

    def _escrita_proibida(self, operacao: str) -> None:
        self.chamadas.append(operacao)
        raise AssertionError(f"a etapa 3 nunca chama '{operacao}'")

    def criar(self, registro: RegistroAtendimento) -> None:
        self._escrita_proibida("criar")

    def gravar(self, registro: RegistroAtendimento) -> None:
        self._escrita_proibida("gravar")

    def marcar_chave_processada(self, chave: str) -> None:
        self._escrita_proibida("marcar_chave_processada")

    def preservar_pendente(self, pendente: Any) -> None:
        self._escrita_proibida("preservar_pendente")

    def chave_processada(self, chave: str) -> bool:
        self.chamadas.append("chave_processada")
        return self._interna.chave_processada(chave)

    def recuperar_pendentes(self) -> tuple[Any, ...]:
        self.chamadas.append("recuperar_pendentes")
        return self._interna.recuperar_pendentes()

    def recuperar_por_id(self, id_atendimento: str, canal: str, contato: str) -> Any:
        self.chamadas.append("recuperar_por_id")
        return self._interna.recuperar_por_id(id_atendimento, canal, contato)

    def consultar_por_contato(
        self, canal: str, contato: str
    ) -> tuple[RegistroAtendimento, ...]:
        self.chamadas.append("consultar_por_contato")
        return self._interna.consultar_por_contato(canal, contato)


def espia_com(*registros: RegistroAtendimento) -> PersistenciaEspia:
    return PersistenciaEspia(persistencia_com(*registros))


@pytest.mark.parametrize("limiar", [None, "sete dias", timedelta(0)])
def test_limiar_invalido_bloqueia_antes_de_qualquer_leitura(limiar: object) -> None:
    espia = espia_com(registro_ficticio())

    with pytest.raises(ConfiguracaoTemporalInvalida):
        montar(espia, limiar=limiar)  # type: ignore[arg-type]

    assert espia.chamadas == []


def test_com_identificador_recuperar_por_id_precede_consultar_por_contato() -> None:
    espia = espia_com(registro_ficticio(id_atendimento="atendimento-fake-a"))

    montar(espia, id_informado="atendimento-fake-a")

    assert espia.chamadas == ["recuperar_por_id", "consultar_por_contato"]


@pytest.mark.parametrize(
    ("id_informado", "esperado"),
    [
        ("atendimento-fake-inexistente", VeredictoIdentificador.NAO_ENCONTRADO),
        ("atendimento-fake-de-outro", VeredictoIdentificador.INCOMPATIVEL),
    ],
)
def test_identificador_nao_resolvido_consulta_o_contato_e_so_entao_bloqueia(
    id_informado: str, esperado: VeredictoIdentificador
) -> None:
    """A ordem normativa é recuperar por ID → consultar contato → validar."""
    espia = espia_com(
        registro_ficticio(id_atendimento="atendimento-fake-a"),
        registro_ficticio(
            id_atendimento="atendimento-fake-de-outro", contato="outro-contato-ficticio"
        ),
    )

    with pytest.raises(IdentificadorNaoResolvido) as erro:
        montar(espia, id_informado=id_informado)

    assert espia.chamadas == ["recuperar_por_id", "consultar_por_contato"]
    assert erro.value.veredito is esperado


def test_bloqueio_do_identificador_nao_transporta_dado_operacional() -> None:
    espia = espia_com()

    with pytest.raises(IdentificadorNaoResolvido) as erro:
        montar(espia, id_informado="atendimento-fake-secreto")

    mensagem = str(erro.value)
    assert "atendimento-fake-secreto" not in mensagem
    assert CANAL not in mensagem
    assert CONTATO not in mensagem


def test_montagem_nunca_chama_operacao_de_escrita() -> None:
    espia = espia_com(
        registro_ficticio(id_atendimento="atendimento-fake-a"),
        registro_ficticio(id_atendimento="atendimento-fake-b", estado="atendimento_humano"),
    )

    montar(espia, id_informado="atendimento-fake-a")

    assert espia.chamadas == ["recuperar_por_id", "consultar_por_contato"]


# 6. Identificador validado — obrigações do produtor N-I-1–N-I-4


class PersistenciaControlada(PersistenciaEspia):
    """Espião cujas respostas de leitura são fixadas pelo teste.

    Permite exercitar contextos que a implementação em memória não consegue
    produzir — snapshot divergente, ausência do identificado no contexto e IDs
    repetidos —, provando que a etapa 3 **verifica** e não confia.
    """

    def __init__(
        self,
        *,
        recuperacao: RecuperacaoPorId,
        registros: tuple[RegistroAtendimento, ...],
    ) -> None:
        super().__init__(PersistenciaEmMemoria())
        self._recuperacao = recuperacao
        self._registros = registros

    def recuperar_por_id(self, id_atendimento: str, canal: str, contato: str) -> Any:
        self.chamadas.append("recuperar_por_id")
        return self._recuperacao

    def consultar_por_contato(
        self, canal: str, contato: str
    ) -> tuple[RegistroAtendimento, ...]:
        self.chamadas.append("consultar_por_contato")
        return self._registros


def controlada(
    identificado: RegistroAtendimento, registros: tuple[RegistroAtendimento, ...]
) -> PersistenciaControlada:
    return PersistenciaControlada(
        recuperacao=RecuperacaoPorId(
            resultado=ResultadoRecuperacao.ENCONTRADO, registro=identificado
        ),
        registros=registros,
    )


def test_encontrado_projeta_o_id_valida_o_estado_esperado_e_ocorre_uma_vez() -> None:
    persistencia = persistencia_com(
        registro_ficticio(id_atendimento="atendimento-fake-a"),
        registro_ficticio(id_atendimento="atendimento-fake-b", estado="coletando_dados"),
    )

    projecoes = montar(persistencia, id_informado="atendimento-fake-a")

    assert projecoes.veredito_identificador is VeredictoIdentificador.ENCONTRADO
    assert projecoes.id_atendimento_validado == "atendimento-fake-a"
    assert projecoes.havia_estado_esperado is True
    assert [
        candidato.id_atendimento for candidato in projecoes.candidatos_elegiveis
    ].count("atendimento-fake-a") == 1


def test_identificado_encerrado_fora_do_limiar_entra_por_na_f1() -> None:
    """K-Na-4 — nenhuma regra de recência remove o identificado do ciclo."""
    antigo = registro_ficticio(
        id_atendimento="atendimento-fake-antigo",
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - LIMIAR - timedelta(days=30),
    )
    persistencia = persistencia_com(antigo)

    sem_identificador = montar(persistencia)
    com_identificador = montar(persistencia, id_informado="atendimento-fake-antigo")

    assert sem_identificador.candidatos_elegiveis == ()
    assert [
        candidato.id_atendimento
        for candidato in com_identificador.candidatos_elegiveis
    ] == ["atendimento-fake-antigo"]


def test_identificado_em_atendimento_humano_entra_em_e_e_tambem_integra_h() -> None:
    """K-Na-6 — H5 satisfeita: o ID está em E por N-a-F1 e em H por estado."""
    sob_humano = registro_ficticio(
        id_atendimento="atendimento-fake-humano", estado="atendimento_humano"
    )
    persistencia = persistencia_com(sob_humano)

    projecoes = montar(persistencia, id_informado="atendimento-fake-humano")

    assert [
        candidato.id_atendimento for candidato in projecoes.candidatos_elegiveis
    ] == ["atendimento-fake-humano"]
    assert projecoes.ids_em_atendimento_humano == ("atendimento-fake-humano",)


def test_snapshot_do_identificado_divergente_do_contexto_bloqueia() -> None:
    identificado = registro_ficticio(id_atendimento="atendimento-fake-a", estado="novo")
    divergente = registro_ficticio(
        id_atendimento="atendimento-fake-a", estado="coletando_dados"
    )

    with pytest.raises(IdentificadoIncoerente):
        montar(controlada(identificado, (divergente,)), id_informado="atendimento-fake-a")


@pytest.mark.parametrize("repeticoes", [0, 2])
def test_identificado_com_zero_ou_multiplas_ocorrencias_bloqueia(
    repeticoes: int,
) -> None:
    """K-Na-11 — N-a-D1 / N-I-2 / P-I5."""
    identificado = registro_ficticio(id_atendimento="atendimento-fake-a")
    registros = (identificado,) * repeticoes

    with pytest.raises(IdentificadoIncoerente):
        montar(controlada(identificado, registros), id_informado="atendimento-fake-a")


# 7. Conjunto H — produzido por estado, fora de N-a (H1–H5)


def test_h_e_produzido_por_estado_e_nao_por_elegibilidade() -> None:
    """K-Na-5 — `atendimento_humano` fica fora de E por N-a-E2, mas integra H."""
    persistencia = persistencia_com(
        registro_ficticio(id_atendimento="atendimento-fake-humano", estado="atendimento_humano"),
        registro_ficticio(id_atendimento="atendimento-fake-ativo", estado="novo"),
    )

    projecoes = montar(persistencia)

    assert projecoes.ids_em_atendimento_humano == ("atendimento-fake-humano",)
    assert [
        candidato.id_atendimento for candidato in projecoes.candidatos_elegiveis
    ] == ["atendimento-fake-ativo"]


def test_h_pode_conter_id_ausente_do_conjunto_elegivel() -> None:
    """H5 não exige a recíproca: canal sob controle humano não expira."""
    persistencia = persistencia_com(
        registro_ficticio(id_atendimento="atendimento-fake-humano", estado="atendimento_humano"),
    )

    projecoes = montar(persistencia)

    assert projecoes.ids_em_atendimento_humano == ("atendimento-fake-humano",)
    assert projecoes.candidatos_elegiveis == ()


def test_duplicata_em_h_e_erro_de_contrato() -> None:
    """H4 — duplicata não conta como `HUMANO_MULTIPLO`."""
    repetido = registro_ficticio(
        id_atendimento="atendimento-fake-humano", estado="atendimento_humano"
    )
    persistencia = PersistenciaControlada(
        recuperacao=RecuperacaoPorId(resultado=ResultadoRecuperacao.NAO_ENCONTRADO),
        registros=(repetido, repetido),
    )

    with pytest.raises(ConjuntoHumanoIncoerente):
        montar(persistencia)


# 8. Invariantes de produtor verificadas no passo 12 (N-I, H4, H5)


def projecoes_de(
    *,
    candidatos: tuple[CandidatoAtendimento, ...] = (),
    veredito: VeredictoIdentificador = VeredictoIdentificador.NAO_INFORMADO,
    id_validado: str | None = None,
    havia_estado_esperado: bool = False,
    humanos: tuple[str, ...] = (),
) -> ProjecoesIdentidadeEtapa3:
    return ProjecoesIdentidadeEtapa3(
        candidatos_elegiveis=candidatos,
        veredito_identificador=veredito,
        id_atendimento_validado=id_validado,
        havia_estado_esperado=havia_estado_esperado,
        ids_em_atendimento_humano=humanos,
    )


def candidato_ficticio(
    *, id_atendimento: str = "atendimento-fake-a", estado: Estado = Estado.NOVO
) -> CandidatoAtendimento:
    return CandidatoAtendimento(
        id_atendimento=id_atendimento,
        estado=estado,
        tipo_evento_registrado=None,
        data_nomeada_registrada=None,
    )


def test_invariante_rejeita_candidato_humano_em_e_ausente_de_h() -> None:
    """H5 — a verificação existe mesmo que a construção de H a torne improvável."""
    projecoes = projecoes_de(
        candidatos=(candidato_ficticio(estado=Estado.ATENDIMENTO_HUMANO),),
        havia_estado_esperado=True,
        humanos=(),
    )

    with pytest.raises(ConjuntoHumanoIncoerente):
        _verificar_invariantes_de_produtor(projecoes)


def test_invariante_rejeita_duplicata_em_h() -> None:
    projecoes = projecoes_de(humanos=("atendimento-fake-a", "atendimento-fake-a"))

    with pytest.raises(ConjuntoHumanoIncoerente):
        _verificar_invariantes_de_produtor(projecoes)


@pytest.mark.parametrize("id_validado", [None, ""])
def test_invariante_exige_id_validado_nao_vazio_sob_encontrado(
    id_validado: str | None,
) -> None:
    projecoes = projecoes_de(
        candidatos=(candidato_ficticio(),),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado=id_validado,
        havia_estado_esperado=True,
    )

    with pytest.raises(ProjecaoIdentificadorIncoerente):
        _verificar_invariantes_de_produtor(projecoes)


def test_invariante_exige_estado_esperado_verdadeiro_sob_encontrado() -> None:
    """N-I-3 — `ENCONTRADO` implica `havia_estado_esperado = true`."""
    projecoes = projecoes_de(
        candidatos=(candidato_ficticio(),),
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="atendimento-fake-a",
        havia_estado_esperado=False,
    )

    with pytest.raises(ProjecaoIdentificadorIncoerente):
        _verificar_invariantes_de_produtor(projecoes)


@pytest.mark.parametrize("ocorrencias", [0, 2])
def test_invariante_exige_uma_unica_ocorrencia_do_id_validado_em_e(
    ocorrencias: int,
) -> None:
    """N-I-2 — espelho produtor de P-I5."""
    projecoes = projecoes_de(
        candidatos=(candidato_ficticio(),) * ocorrencias,
        veredito=VeredictoIdentificador.ENCONTRADO,
        id_validado="atendimento-fake-a",
        havia_estado_esperado=True,
    )

    with pytest.raises(ProjecaoIdentificadorIncoerente):
        _verificar_invariantes_de_produtor(projecoes)


def test_invariante_rejeita_veredito_bloqueado_na_saida() -> None:
    """P-I3 — `NAO_ENCONTRADO`/`INCOMPATIVEL` nunca chegam à etapa 5."""
    for veredito in (
        VeredictoIdentificador.NAO_ENCONTRADO,
        VeredictoIdentificador.INCOMPATIVEL,
    ):
        with pytest.raises(ProjecaoIdentificadorIncoerente):
            _verificar_invariantes_de_produtor(projecoes_de(veredito=veredito))


def test_invariante_exige_id_validado_none_sob_nao_informado() -> None:
    """P-I1 — espelho produtor."""
    projecoes = projecoes_de(id_validado="atendimento-fake-a")

    with pytest.raises(ProjecaoIdentificadorIncoerente):
        _verificar_invariantes_de_produtor(projecoes)


# 9. `havia_estado_esperado` — calculado sobre o contexto, nunca sobre E


def test_historico_existente_com_e_vazio_mantem_estado_esperado_verdadeiro() -> None:
    """Filtrar todo o histórico para fora de E não cria primeiro contato."""
    persistencia = persistencia_com(
        registro_ficticio(
            id_atendimento="atendimento-fake-antigo",
            estado="encerrado",
            instante_ultima_transicao=REFERENCIA - LIMIAR - timedelta(days=1),
        )
    )

    projecoes = montar(persistencia)

    assert projecoes.candidatos_elegiveis == ()
    assert projecoes.havia_estado_esperado is True


def test_sem_nenhum_historico_o_estado_esperado_e_falso() -> None:
    projecoes = montar(PersistenciaEmMemoria())

    assert projecoes.candidatos_elegiveis == ()
    assert projecoes.havia_estado_esperado is False


def test_registros_de_outro_contato_nao_criam_estado_esperado() -> None:
    persistencia = persistencia_com(
        registro_ficticio(
            id_atendimento="atendimento-fake-de-outro", contato="outro-contato-ficticio"
        )
    )

    assert montar(persistencia).havia_estado_esperado is False


# 10. Integração 3 → 5 — a saída da etapa 3 é aceita pelo `ResolvedorIdentidade`
#
# O encadeamento é feito **pelo teste**: `context.py` não chama o resolvedor.


def projecao_fixa(
    *,
    intencao: IntencaoIdentidade = IntencaoIdentidade.NAO_DISCRIMINANTE,
    referencia: ReferenciaEventoAnterior = ReferenciaEventoAnterior.SEM_REFERENCIA,
    confianca_referencia: Confianca | None = None,
) -> ProjecaoInterpretacao:
    """Projeção da etapa 4 **fixa**, criada no teste: zero LLM, zero rede."""
    return ProjecaoInterpretacao(
        intencao_identidade=intencao,
        referencia_evento_anterior=referencia,
        confianca_referencia=confianca_referencia,
        tipo_evento_extraido=None,
        confianca_tipo=None,
        data_nomeada_extraida=None,
        confianca_data=None,
    )


def resolver_com(
    projecoes: ProjecoesIdentidadeEtapa3,
    projecao: ProjecaoInterpretacao | None = None,
) -> DecisaoIdentidade:
    """Alimenta o resolvedor com os cinco campos produzidos pela etapa 3."""
    return resolver_identidade(
        projecoes.candidatos_elegiveis,
        projecao if projecao is not None else projecao_fixa(),
        projecoes.veredito_identificador,
        projecoes.id_atendimento_validado,
        projecoes.havia_estado_esperado,
        projecoes.ids_em_atendimento_humano,
    )


def test_cenario_valido_nao_falha_por_h4_h5_ou_p_i() -> None:
    """A saída da etapa 3 é aceita pelas pré-condições da etapa 5."""
    persistencia = persistencia_com(
        registro_ficticio(id_atendimento="atendimento-fake-a", estado="coletando_dados"),
        registro_ficticio(id_atendimento="atendimento-fake-humano", estado="atendimento_humano"),
    )

    projecoes = montar(persistencia, id_informado="atendimento-fake-a")
    decisao = resolver_com(projecoes)

    assert isinstance(decisao, DecisaoIdentidade)


def test_identificado_sob_takeover_e_aceito_pelo_resolvedor() -> None:
    """K-Na-6 — o identificado em `atendimento_humano` satisfaz H5 na etapa 5."""
    persistencia = persistencia_com(
        registro_ficticio(id_atendimento="atendimento-fake-humano", estado="atendimento_humano"),
    )

    projecoes = montar(persistencia, id_informado="atendimento-fake-humano")
    decisao = resolver_com(projecoes)

    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO


def test_k_na_13_h_nao_vazio_com_e_vazio_produz_takeover() -> None:
    persistencia = persistencia_com(
        registro_ficticio(id_atendimento="atendimento-fake-humano", estado="atendimento_humano"),
    )

    projecoes = montar(persistencia)
    decisao = resolver_com(projecoes)

    assert projecoes.candidatos_elegiveis == ()
    assert decisao.situacao_takeover is SituacaoTakeover.HUMANO_UNICO
    assert decisao.identidade is None
    assert decisao.criterio is None


def test_k_na_14_h_vazio_e_vazio_com_contradicao_declarada_produz_d0() -> None:
    projecoes = montar(PersistenciaEmMemoria())
    contraditoria = projecao_fixa(
        intencao=IntencaoIdentidade.NOVO_EVENTO_DECLARADO,
        referencia=ReferenciaEventoAnterior.COM_REFERENCIA,
        confianca_referencia=Confianca.ALTA,
    )

    decisao = resolver_com(projecoes, contraditoria)

    assert decisao.identidade is Identidade.AMBIGUA
    assert decisao.criterio is CriterioIdentidade.AMBIGUIDADE_SINAIS_CONTRADITORIOS


def test_k_na_15_h_vazio_e_vazio_com_historico_produz_sem_candidato_elegivel() -> None:
    persistencia = persistencia_com(
        registro_ficticio(
            id_atendimento="atendimento-fake-antigo",
            estado="encerrado",
            instante_ultima_transicao=REFERENCIA - LIMIAR - timedelta(days=1),
        )
    )

    projecoes = montar(persistencia)
    decisao = resolver_com(projecoes)

    assert projecoes.havia_estado_esperado is True
    assert decisao.criterio is CriterioIdentidade.SEM_CANDIDATO_ELEGIVEL


def test_k_na_16_h_vazio_e_vazio_sem_historico_produz_primeiro_contato() -> None:
    projecoes = montar(PersistenciaEmMemoria())

    decisao = resolver_com(projecoes)

    assert projecoes.havia_estado_esperado is False
    assert decisao.criterio is CriterioIdentidade.PRIMEIRO_CONTATO_COMPROVADO


# 11. Fronteiras do módulo — provadas sobre o código, não sobre a docstring


def _modulos_importados() -> set[str]:
    arvore = ast.parse(MODULO_CONTEXTO.read_text(encoding="utf-8"))
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)
    return importados


def _identificadores() -> set[str]:
    arvore = ast.parse(MODULO_CONTEXTO.read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
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


def test_contexto_importa_exatamente_os_modulos_autorizados() -> None:
    assert _modulos_importados() == {
        "__future__",
        "dataclasses",
        "datetime",
        "casa77_sdr.eligibility",
        "casa77_sdr.identity",
        "casa77_sdr.persistence",
        "casa77_sdr.state_machine",
    }


def test_contexto_sem_import_de_rede_yaml_llm_ou_servico_externo() -> None:
    proibidos = {
        "os",
        "io",
        "time",
        "pathlib",
        "socket",
        "http",
        "urllib",
        "requests",
        "sqlite3",
        "json",
        "yaml",
        "random",
        "anthropic",
        "openai",
        "casa77_sdr.knowledge",
        "casa77_sdr.normalization",
        "casa77_sdr.qualification",
        "casa77_sdr.rules",
    }

    assert not (_modulos_importados() & proibidos)


def test_contexto_nao_consulta_relogio_vivo() -> None:
    proibidos = {"now", "utcnow", "today", "fromtimestamp", "monotonic"}

    assert not (_identificadores() & proibidos)


def test_contexto_nao_escreve_na_persistencia_nem_orquestra() -> None:
    """Somente leitura, e nenhuma etapa alheia à montagem das projeções."""
    proibidos = {
        "criar",
        "gravar",
        "marcar_chave_processada",
        "preservar_pendente",
        "recuperar_pendentes",
        "chave_processada",
        "resolver_identidade",
        "decidir",
        "qualificar",
        "avaliar_regras",
        "normalizar_entrada",
        "load_knowledge",
        "OrquestradorMotor",
        "MaquinaEstados",
    }

    assert not (_identificadores() & proibidos)


def test_contexto_nao_reimplementa_a_politica_n_a() -> None:
    """E continua delegado: nada de recência, limiar ou ordem canônica aqui."""
    proibidos = {
        "_e_recente",
        "_chave_canonica",
        "_projetar",
        "_GRUPO_I",
        "_ESTADOS_VALIDOS",
    }

    assert not (_identificadores() & proibidos)


# 12. Separação entre seleção de E (passos 9/10) e canonicalização (passo 13)


def selecionar(
    registros: tuple[RegistroAtendimento, ...],
    identificado: RegistroAtendimento | None = None,
) -> tuple[CandidatoAtendimento, ...]:
    return selecionar_conjunto_elegivel(
        registros,
        registro_identificado=identificado,
        instante_de_referencia_do_ciclo=REFERENCIA,
        limiar_recencia=LIMIAR,
    )


def test_selecionar_devolve_e_ainda_nao_canonicalizado() -> None:
    """Passos 9/10 preservam a ordem de recuperação; ordenar é o passo 13."""
    registros = (
        registro_ficticio(id_atendimento="atendimento-fake-z"),
        registro_ficticio(id_atendimento="atendimento-fake-a"),
    )

    assert [candidato.id_atendimento for candidato in selecionar(registros)] == [
        "atendimento-fake-z",
        "atendimento-fake-a",
    ]


def test_selecionar_aplica_classificacao_recencia_e_na_f1() -> None:
    antigo = registro_ficticio(
        id_atendimento="atendimento-fake-antigo",
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - LIMIAR - timedelta(days=1),
    )
    sob_humano = registro_ficticio(
        id_atendimento="atendimento-fake-humano", estado="atendimento_humano"
    )
    ativo = registro_ficticio(id_atendimento="atendimento-fake-ativo")

    assert [c.id_atendimento for c in selecionar((antigo, sob_humano, ativo))] == [
        "atendimento-fake-ativo"
    ]
    assert [
        c.id_atendimento for c in selecionar((antigo, sob_humano, ativo), antigo)
    ] == ["atendimento-fake-antigo", "atendimento-fake-ativo"]


def test_selecionar_valida_o_limiar_sempre() -> None:
    with pytest.raises(ConfiguracaoTemporalInvalida):
        selecionar_conjunto_elegivel(
            (),
            registro_identificado=None,
            instante_de_referencia_do_ciclo=REFERENCIA,
            limiar_recencia=None,
        )


def test_canonicalizar_aplica_apenas_a_ordem_estrutural() -> None:
    """N-a-O1–N-a-O5: ordena, não elimina, não deduplica, não muda cardinalidade."""
    candidatos = (
        candidato_ficticio(id_atendimento="atendimento-fake-z"),
        candidato_ficticio(id_atendimento="atendimento-fake-a"),
        candidato_ficticio(id_atendimento="atendimento-fake-a"),
    )

    canonico = canonicalizar_conjunto_elegivel(candidatos)

    assert [c.id_atendimento for c in canonico] == [
        "atendimento-fake-a",
        "atendimento-fake-a",
        "atendimento-fake-z",
    ]


def test_produzir_permanece_equivalente_a_canonicalizar_apos_selecionar() -> None:
    """A API pública histórica não muda de comportamento."""
    registros = (
        registro_ficticio(id_atendimento="atendimento-fake-z"),
        registro_ficticio(id_atendimento="atendimento-fake-a", estado="coletando_dados"),
    )

    assert produzir_conjunto_elegivel(
        registros,
        registro_identificado=None,
        instante_de_referencia_do_ciclo=REFERENCIA,
        limiar_recencia=LIMIAR,
    ) == canonicalizar_conjunto_elegivel(selecionar(registros))


# 13. Ordem real 12 → 13: verificar as invariantes ANTES de canonicalizar


def test_invariantes_do_produtor_precedem_a_canonicalizacao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Passo 12 antes do passo 13, provado por observação, não por comentário.

    A prova é dupla: a sequência das chamadas e o **conteúdo** de E que chega
    ao passo 12 — ainda na ordem de recuperação, não na ordem canônica.
    """
    eventos: list[str] = []
    e_verificado: list[tuple[str, ...]] = []

    invariantes_reais = context._verificar_invariantes_de_produtor
    canonicalizar_real = context.canonicalizar_conjunto_elegivel

    def espiar_invariantes(projecoes: ProjecoesIdentidadeEtapa3) -> None:
        eventos.append("invariantes")
        e_verificado.append(
            tuple(c.id_atendimento for c in projecoes.candidatos_elegiveis)
        )
        invariantes_reais(projecoes)

    def espiar_canonicalizacao(
        candidatos: tuple[CandidatoAtendimento, ...],
    ) -> tuple[CandidatoAtendimento, ...]:
        eventos.append("canonicalizar")
        return canonicalizar_real(candidatos)

    monkeypatch.setattr(
        context, "_verificar_invariantes_de_produtor", espiar_invariantes
    )
    monkeypatch.setattr(
        context, "canonicalizar_conjunto_elegivel", espiar_canonicalizacao
    )

    persistencia = PersistenciaControlada(
        recuperacao=RecuperacaoPorId(resultado=ResultadoRecuperacao.NAO_ENCONTRADO),
        registros=(
            registro_ficticio(id_atendimento="atendimento-fake-z"),
            registro_ficticio(id_atendimento="atendimento-fake-a"),
        ),
    )

    projecoes = montar(persistencia)

    assert eventos == ["invariantes", "canonicalizar"]
    assert e_verificado == [("atendimento-fake-z", "atendimento-fake-a")]
    assert [c.id_atendimento for c in projecoes.candidatos_elegiveis] == [
        "atendimento-fake-a",
        "atendimento-fake-z",
    ]


def test_dto_entregue_carrega_e_canonicalizado() -> None:
    persistencia = PersistenciaControlada(
        recuperacao=RecuperacaoPorId(resultado=ResultadoRecuperacao.NAO_ENCONTRADO),
        registros=(
            registro_ficticio(id_atendimento="atendimento-fake-z"),
            registro_ficticio(id_atendimento="atendimento-fake-m"),
            registro_ficticio(id_atendimento="atendimento-fake-a"),
        ),
    )

    projecoes = montar(persistencia)

    assert [c.id_atendimento for c in projecoes.candidatos_elegiveis] == [
        "atendimento-fake-a",
        "atendimento-fake-m",
        "atendimento-fake-z",
    ]
