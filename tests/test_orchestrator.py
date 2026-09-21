"""Testes do recorte **R1** do `OrquestradorMotor` (doc 07 §4.1.10, `OMR1`).

Cobrem as etapas **1**, **2** e **3** do pipeline (§5) e o **tratamento
operacional dos bloqueios `S4`/`S5`** arbitrado em §7.1 (`TS45-1`–`TS45-20`).

Fixtures totalmente artificiais: canais, contatos, identificadores e conteúdos
claramente fictícios, sem dado pessoal real, sem telefone, sem nome e sem valor
comercial. Nenhum valor operacional de janela ou de limiar é fixado: as
durações abaixo são sintéticas e existem apenas para exercitar o contrato —
o **valor real** e o **mecanismo de carga** do limiar continuam pendentes
(`docs/07` §12, item 18).

Os gatilhos TS45 nascem das **fronteiras reais**: `normalizar_entrada`,
`PersistenciaOperacional` e `montar_projecoes_identidade_etapa3`. Nada aqui
faz *monkeypatch* de `casa77_sdr.context`, substitui
`montar_projecoes_identidade_etapa3` nem força `raise` artificial dentro do
módulo orquestrador.
"""

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

import casa77_sdr
from casa77_sdr import orchestrator
from casa77_sdr.context import (
    ConjuntoHumanoIncoerente,
    IdentificadorNaoResolvido,
    ProjecoesIdentidadeEtapa3,
)
from casa77_sdr.eligibility import (
    ConfiguracaoTemporalInvalida,
    ContextoElegibilidadeCorrompido,
    IdentificadoIncoerente,
    MarcoTemporalAusente,
)
from casa77_sdr.identity import VeredictoIdentificador
from casa77_sdr.normalization import (
    EntradaInvalida,
    EntradaMensagem,
    EntradaNormalizada,
    normalizar_entrada,
)
from casa77_sdr.orchestrator import coordenar_etapas_1_a_3
from casa77_sdr.persistence import (
    PersistenciaEmMemoria,
    PersistenciaOperacional,
    ProcessamentoPendente,
    RecuperacaoPorId,
    RegistroAtendimento,
    ResultadoRecuperacao,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "orchestrator.py"
MODULO_INIT = RAIZ / "src" / "casa77_sdr" / "__init__.py"

CANAL = "canal-ficticio"
CONTATO = "contato-ficticio"
MENSAGEM = "  Oi,   tudo   bem?  "
MENSAGEM_NORMALIZADA = "Oi, tudo bem?"
REFERENCIA = datetime(2000, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
JANELA = timedelta(minutes=3)
LIMIAR = timedelta(days=7)

AS_SETE_CLASSES = (
    "ConfiguracaoTemporalInvalida",
    "IdentificadorNaoResolvido",
    "ContextoElegibilidadeCorrompido",
    "MarcoTemporalAusente",
    "IdentificadoIncoerente",
    "ConjuntoHumanoIncoerente",
    "ProjecaoIdentificadorIncoerente",
)


# --------------------------------------------------------------------------
# Instrumentos de teste — fronteiras reais, sem monkeypatch
# --------------------------------------------------------------------------


class FalhaSimuladaDePreservacao(Exception):
    """Falha da fronteira de preservação, escolhida pelo teste."""


class FalhaSimuladaDeMarcacao(Exception):
    """Falha da fronteira de marcação de idempotência, escolhida pelo teste."""


class FalhaSimuladaDoAlerta(Exception):
    """Falha da dependência injetada de alerta, escolhida pelo teste."""


class FalhaSimuladaDeLeitura(Exception):
    """Falha de leitura da persistência — **fora** do gatilho de TS45 (`TS45-19`)."""


class FalhaDeLeituraQueEValueError(ValueError):
    """`ValueError` que **não** é uma das sete: prova que a captura é por classe."""


class AlertaEspiao:
    """Dependência de alerta injetada, com registro sanitizado das chamadas.

    Aceita **somente** palavras-chave: uma chamada posicional falharia, o que
    é exatamente a garantia exigida por `OMR1-6`.
    """

    def __init__(
        self, *, diario: list[str] | None = None, falhar: bool = False
    ) -> None:
        self.chamadas: list[dict[str, Any]] = []
        self.retorno = "retorno-que-deve-ser-ignorado"
        self._diario = diario
        self._falhar = falhar
        self.erro = FalhaSimuladaDoAlerta("falha simulada da tentativa de alerta")

    def __call__(self, **payload: Any) -> object:
        self.chamadas.append(payload)
        if self._diario is not None:
            self._diario.append("tentar_alerta")
        if self._falhar:
            raise self.erro
        return self.retorno


class PersistenciaInstrumentada(PersistenciaOperacional):
    """Persistência real em memória, com diário de chamadas e falhas injetáveis.

    As leituras podem ser **fixadas pelo teste** para representar contextos que
    a implementação volátil não consegue produzir — mesmo padrão já usado em
    `tests/test_context.py`. Nada aqui altera `persistence.py`.
    """

    def __init__(
        self,
        interna: PersistenciaEmMemoria | None = None,
        *,
        diario: list[str] | None = None,
        recuperacao: RecuperacaoPorId | None = None,
        registros: tuple[RegistroAtendimento, ...] | None = None,
        erro_de_leitura: Exception | None = None,
        erro_de_preservacao: Exception | None = None,
        erro_de_marcacao: Exception | None = None,
    ) -> None:
        self._interna = PersistenciaEmMemoria() if interna is None else interna
        self.chamadas: list[str] = [] if diario is None else diario
        self._recuperacao = recuperacao
        self._registros = registros
        self._erro_de_leitura = erro_de_leitura
        self._erro_de_preservacao = erro_de_preservacao
        self._erro_de_marcacao = erro_de_marcacao

    def criar(self, registro: RegistroAtendimento) -> None:
        self.chamadas.append("criar")
        raise AssertionError("o recorte R1 nunca cria atendimento")

    def gravar(self, registro: RegistroAtendimento) -> None:
        self.chamadas.append("gravar")
        raise AssertionError("o recorte R1 nunca grava atendimento")

    def recuperar_por_id(
        self, id_atendimento: str, canal: str, contato: str
    ) -> RecuperacaoPorId:
        self.chamadas.append("recuperar_por_id")
        if self._recuperacao is not None:
            return self._recuperacao
        return self._interna.recuperar_por_id(id_atendimento, canal, contato)

    def consultar_por_contato(
        self, canal: str, contato: str
    ) -> tuple[RegistroAtendimento, ...]:
        self.chamadas.append("consultar_por_contato")
        if self._erro_de_leitura is not None:
            raise self._erro_de_leitura
        if self._registros is not None:
            return self._registros
        return self._interna.consultar_por_contato(canal, contato)

    def chave_processada(self, chave: str) -> bool:
        self.chamadas.append("chave_processada")
        return self._interna.chave_processada(chave)

    def marcar_chave_processada(self, chave: str) -> None:
        self.chamadas.append("marcar_chave_processada")
        if self._erro_de_marcacao is not None:
            raise self._erro_de_marcacao
        self._interna.marcar_chave_processada(chave)

    def preservar_pendente(self, pendente: ProcessamentoPendente) -> None:
        self.chamadas.append("preservar_pendente")
        if self._erro_de_preservacao is not None:
            raise self._erro_de_preservacao
        self._interna.preservar_pendente(pendente)

    def recuperar_pendentes(self) -> tuple[ProcessamentoPendente, ...]:
        return self._interna.recuperar_pendentes()

    def ja_marcada(self, chave: str) -> bool:
        """Consulta auxiliar do teste, fora do diário."""
        return self._interna.chave_processada(chave)


def entrada_ficticia(
    *,
    mensagem: str = MENSAGEM,
    canal: str = CANAL,
    contato: str = CONTATO,
    recebida_em: datetime = REFERENCIA,
    id_mensagem_canal: str | None = None,
    id_atendimento: str | None = None,
) -> EntradaMensagem:
    return EntradaMensagem(
        canal=canal,
        contato=contato,
        mensagem=mensagem,
        recebida_em=recebida_em,
        id_mensagem_canal=id_mensagem_canal,
        id_atendimento=id_atendimento,
    )


def registro_ficticio(
    *,
    id_atendimento: str = "atendimento-fake-a",
    canal: str = CANAL,
    contato: str = CONTATO,
    estado: str | None = "novo",
    instante_ultima_transicao: datetime | None = None,
) -> RegistroAtendimento:
    return RegistroAtendimento(
        id_atendimento=id_atendimento,
        canal=canal,
        contato=contato,
        estado_conversa=estado,
        instante_ultima_transicao=instante_ultima_transicao,
    )


def memoria_com(*registros: RegistroAtendimento) -> PersistenciaEmMemoria:
    interna = PersistenciaEmMemoria()
    for registro in registros:
        interna.criar(registro)
    return interna


def coordenar(
    entrada: EntradaMensagem,
    persistencia: PersistenciaOperacional,
    tentar_alerta: Any,
    *,
    janela: timedelta = JANELA,
    limiar: timedelta | None = LIMIAR,
) -> tuple[EntradaNormalizada, ProjecoesIdentidadeEtapa3] | None:
    return coordenar_etapas_1_a_3(
        entrada,
        persistencia=persistencia,
        janela_idempotencia=janela,
        limiar_recencia=limiar,
        tentar_alerta=tentar_alerta,
    )


def chave_de(entrada: EntradaMensagem, janela: timedelta = JANELA) -> str:
    return normalizar_entrada(entrada, janela).chave_idempotencia


def codigo_executavel(caminho: Path) -> str:
    """O módulo **sem docstrings**: o contrato cita fronteiras que não invade."""
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


def nomes_usados(caminho: Path) -> set[str]:
    arvore = ast.parse(codigo_executavel(caminho))
    nomes = {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
            nomes.update(a.name for a in no.names)
        elif isinstance(no, ast.Import):
            nomes.update(a.name for a in no.names)
    return nomes


def arvore_do_modulo() -> ast.Module:
    return ast.parse(MODULO.read_text(encoding="utf-8"))


def handlers_do_modulo() -> list[ast.ExceptHandler]:
    return [
        no for no in ast.walk(arvore_do_modulo()) if isinstance(no, ast.ExceptHandler)
    ]


# --------------------------------------------------------------------------
# A. Caminho feliz (`OMR1-9`)
# --------------------------------------------------------------------------


def test_caminho_feliz_devolve_o_par_da_etapa_1_e_da_etapa_3() -> None:
    entrada = entrada_ficticia()
    persistencia = PersistenciaInstrumentada()
    alerta = AlertaEspiao()

    resultado = coordenar(entrada, persistencia, alerta)

    assert resultado is not None
    entrada_normalizada, projecoes = resultado
    assert isinstance(entrada_normalizada, EntradaNormalizada)
    assert isinstance(projecoes, ProjecoesIdentidadeEtapa3)
    assert entrada_normalizada == normalizar_entrada(entrada, JANELA)


def test_caminho_feliz_projeta_o_contexto_recuperado_da_etapa_3() -> None:
    entrada = entrada_ficticia()
    persistencia = PersistenciaInstrumentada(
        memoria_com(registro_ficticio(id_atendimento="atendimento-fake-a"))
    )

    resultado = coordenar(entrada, persistencia, AlertaEspiao())

    assert resultado is not None
    projecoes = resultado[1]
    assert projecoes.veredito_identificador is VeredictoIdentificador.NAO_INFORMADO
    assert [c.id_atendimento for c in projecoes.candidatos_elegiveis] == [
        "atendimento-fake-a"
    ]
    assert projecoes.havia_estado_esperado is True


def test_caminho_feliz_nao_marca_chave_nao_preserva_e_nao_alerta() -> None:
    """`OMR1-9` — a marcação do ciclo normal pertence a etapas posteriores."""
    entrada = entrada_ficticia()
    persistencia = PersistenciaInstrumentada()
    alerta = AlertaEspiao()

    coordenar(entrada, persistencia, alerta)

    assert persistencia.chamadas == [
        "chave_processada",
        "consultar_por_contato",
    ]
    assert persistencia.recuperar_pendentes() == ()
    assert persistencia.ja_marcada(chave_de(entrada)) is False
    assert alerta.chamadas == []


def test_caminho_feliz_com_identificador_consulta_por_id_antes_do_contato() -> None:
    entrada = entrada_ficticia(id_atendimento="atendimento-fake-a")
    persistencia = PersistenciaInstrumentada(
        memoria_com(registro_ficticio(id_atendimento="atendimento-fake-a"))
    )

    resultado = coordenar(entrada, persistencia, AlertaEspiao())

    assert resultado is not None
    assert persistencia.chamadas == [
        "chave_processada",
        "recuperar_por_id",
        "consultar_por_contato",
    ]
    assert resultado[1].id_atendimento_validado == "atendimento-fake-a"


def test_o_instante_do_ciclo_vem_da_entrada_e_nao_de_relogio_vivo() -> None:
    """`OMR1-8` — recência avaliada contra `recebida_em`, nunca contra o agora."""
    encerrado_antigo = registro_ficticio(
        id_atendimento="atendimento-fake-antigo",
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - LIMIAR - timedelta(days=1),
    )
    encerrado_recente = registro_ficticio(
        id_atendimento="atendimento-fake-recente",
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - timedelta(days=1),
    )
    persistencia = PersistenciaInstrumentada(
        memoria_com(encerrado_antigo, encerrado_recente)
    )

    resultado = coordenar(entrada_ficticia(), persistencia, AlertaEspiao())

    assert resultado is not None
    assert [c.id_atendimento for c in resultado[1].candidatos_elegiveis] == [
        "atendimento-fake-recente"
    ]


# --------------------------------------------------------------------------
# B. Terminais da etapa 1 e da etapa 2
# --------------------------------------------------------------------------


@pytest.mark.parametrize("mensagem", ["", "   ", "\n\t  \r\n", " "])
def test_mensagem_vazia_devolve_none_com_zero_efeito(mensagem: str) -> None:
    persistencia = PersistenciaInstrumentada()
    alerta = AlertaEspiao()

    assert coordenar(entrada_ficticia(mensagem=mensagem), persistencia, alerta) is None

    assert persistencia.chamadas == []
    assert persistencia.recuperar_pendentes() == ()
    assert alerta.chamadas == []


@pytest.mark.parametrize(
    "ajuste",
    [
        {"canal": "   "},
        {"contato": ""},
        {"recebida_em": datetime(2000, 6, 15, 12, 0, 0)},
        {"id_mensagem_canal": "  "},
        {"id_atendimento": ""},
    ],
)
def test_entrada_invalida_propaga_intacta(ajuste: dict[str, Any]) -> None:
    persistencia = PersistenciaInstrumentada()
    alerta = AlertaEspiao()

    with pytest.raises(EntradaInvalida):
        coordenar(entrada_ficticia(**ajuste), persistencia, alerta)

    assert persistencia.chamadas == []
    assert persistencia.recuperar_pendentes() == ()
    assert alerta.chamadas == []


def test_janela_invalida_propaga_como_entrada_invalida_e_nao_como_ts45() -> None:
    """A janela é validada **só** por `normalizar_entrada` (`OMR1-4`)."""
    persistencia = PersistenciaInstrumentada()
    alerta = AlertaEspiao()

    with pytest.raises(EntradaInvalida):
        coordenar(
            entrada_ficticia(), persistencia, alerta, janela=timedelta(0)
        )

    assert persistencia.chamadas == []
    assert alerta.chamadas == []


def test_duplicata_encerra_na_etapa_2_sem_tocar_a_etapa_3() -> None:
    entrada = entrada_ficticia()
    interna = PersistenciaEmMemoria()
    interna.marcar_chave_processada(chave_de(entrada))
    persistencia = PersistenciaInstrumentada(interna)
    alerta = AlertaEspiao()

    assert coordenar(entrada, persistencia, alerta) is None

    assert persistencia.chamadas == ["chave_processada"]
    assert persistencia.recuperar_pendentes() == ()
    assert alerta.chamadas == []


# --------------------------------------------------------------------------
# C. Passo 0 — contrato da dependência injetada (`OMR1-5`)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "nao_chamavel", [None, "alerta", 7, object(), ["alerta"], {"a": 1}]
)
def test_alerta_nao_chamavel_levanta_type_error_antes_de_qualquer_leitura(
    nao_chamavel: object,
) -> None:
    persistencia = PersistenciaInstrumentada()

    with pytest.raises(TypeError) as erro:
        coordenar(entrada_ficticia(), persistencia, nao_chamavel)

    assert persistencia.chamadas == []
    assert persistencia.recuperar_pendentes() == ()
    assert "tentar_alerta" in str(erro.value)


@pytest.mark.parametrize("nao_chamavel", ["conteudo-secreto-ficticio", 4242])
def test_a_mensagem_do_type_error_nao_reproduz_o_valor_recebido(
    nao_chamavel: object,
) -> None:
    with pytest.raises(TypeError) as erro:
        coordenar(entrada_ficticia(), PersistenciaInstrumentada(), nao_chamavel)

    assert str(nao_chamavel) not in str(erro.value)


def test_o_contrato_da_dependencia_precede_ate_a_mensagem_vazia() -> None:
    """Passo 0 vem **antes de qualquer etapa**, inclusive da etapa 1."""
    with pytest.raises(TypeError):
        coordenar(entrada_ficticia(mensagem="   "), PersistenciaInstrumentada(), None)


# --------------------------------------------------------------------------
# D. Gatilhos TS45 exercitados em runtime (`OMR1-7`)
# --------------------------------------------------------------------------


def cenario_configuracao_temporal_invalida() -> tuple[
    EntradaMensagem, PersistenciaInstrumentada, timedelta | None
]:
    return entrada_ficticia(), PersistenciaInstrumentada(), None


def cenario_identificador_nao_resolvido() -> tuple[
    EntradaMensagem, PersistenciaInstrumentada, timedelta | None
]:
    return (
        entrada_ficticia(id_atendimento="atendimento-fake-inexistente"),
        PersistenciaInstrumentada(),
        LIMIAR,
    )


def cenario_contexto_corrompido() -> tuple[
    EntradaMensagem, PersistenciaInstrumentada, timedelta | None
]:
    return (
        entrada_ficticia(),
        PersistenciaInstrumentada(memoria_com(registro_ficticio(estado=None))),
        LIMIAR,
    )


def cenario_marco_temporal_ausente() -> tuple[
    EntradaMensagem, PersistenciaInstrumentada, timedelta | None
]:
    return (
        entrada_ficticia(),
        PersistenciaInstrumentada(
            memoria_com(
                registro_ficticio(estado="encerrado", instante_ultima_transicao=None)
            )
        ),
        LIMIAR,
    )


def cenario_identificado_incoerente() -> tuple[
    EntradaMensagem, PersistenciaInstrumentada, timedelta | None
]:
    """Snapshot do identificado divergente da ocorrência recuperada (N-a-F1)."""
    identificado = registro_ficticio(id_atendimento="atendimento-fake-a", estado="novo")
    divergente = registro_ficticio(
        id_atendimento="atendimento-fake-a", estado="coletando_dados"
    )
    persistencia = PersistenciaInstrumentada(
        recuperacao=RecuperacaoPorId(
            resultado=ResultadoRecuperacao.ENCONTRADO, registro=identificado
        ),
        registros=(divergente,),
    )
    return (
        entrada_ficticia(id_atendimento="atendimento-fake-a"),
        persistencia,
        LIMIAR,
    )


def cenario_conjunto_humano_incoerente() -> tuple[
    EntradaMensagem, PersistenciaInstrumentada, timedelta | None
]:
    """Duplicata em **H** (H4), que a implementação volátil não representa."""
    repetido = registro_ficticio(
        id_atendimento="atendimento-fake-humano", estado="atendimento_humano"
    )
    persistencia = PersistenciaInstrumentada(registros=(repetido, repetido))
    return entrada_ficticia(), persistencia, LIMIAR


CENARIOS_TS45 = {
    "ConfiguracaoTemporalInvalida": (
        cenario_configuracao_temporal_invalida,
        ConfiguracaoTemporalInvalida,
    ),
    "IdentificadorNaoResolvido": (
        cenario_identificador_nao_resolvido,
        IdentificadorNaoResolvido,
    ),
    "ContextoElegibilidadeCorrompido": (
        cenario_contexto_corrompido,
        ContextoElegibilidadeCorrompido,
    ),
    "MarcoTemporalAusente": (
        cenario_marco_temporal_ausente,
        MarcoTemporalAusente,
    ),
    "IdentificadoIncoerente": (
        cenario_identificado_incoerente,
        IdentificadoIncoerente,
    ),
    "ConjuntoHumanoIncoerente": (
        cenario_conjunto_humano_incoerente,
        ConjuntoHumanoIncoerente,
    ),
}


@pytest.mark.parametrize("nome", sorted(CENARIOS_TS45))
def test_cada_gatilho_alcancavel_produz_o_mesmo_desfecho_observavel(
    nome: str,
) -> None:
    """`TS45-3` — sete bloqueios, um desfecho; a causa distingue só a categoria."""
    construir, _ = CENARIOS_TS45[nome]
    entrada, persistencia, limiar = construir()
    alerta = AlertaEspiao()

    assert coordenar(entrada, persistencia, alerta, limiar=limiar) is None

    pendentes = persistencia.recuperar_pendentes()
    assert pendentes == (
        ProcessamentoPendente(
            canal=CANAL, contato=CONTATO, conteudo=MENSAGEM_NORMALIZADA
        ),
    )
    assert persistencia.ja_marcada(chave_de(entrada)) is True
    assert [chamada["categoria"] for chamada in alerta.chamadas] == [nome]


@pytest.mark.parametrize("nome", sorted(CENARIOS_TS45))
def test_cada_gatilho_alcancavel_nasce_da_fronteira_real(nome: str) -> None:
    """A exceção é produzida pela etapa 3, não fabricada pelo orquestrador."""
    construir, classe = CENARIOS_TS45[nome]
    entrada, persistencia, limiar = construir()

    with pytest.raises(classe):
        from casa77_sdr.context import montar_projecoes_identidade_etapa3

        montar_projecoes_identidade_etapa3(
            persistencia,
            canal=entrada.canal,
            contato=entrada.contato,
            id_atendimento_informado=entrada.id_atendimento,
            instante_de_referencia_do_ciclo=entrada.recebida_em,
            limiar_recencia=limiar,
        )


def test_ts45_nao_cria_nem_grava_atendimento_e_nao_chama_etapas_posteriores() -> None:
    """`TS45-17` — zero máquina, zero etapa 5, zero etapa 13, zero emissão."""
    entrada, persistencia, limiar = cenario_marco_temporal_ausente()

    coordenar(entrada, persistencia, AlertaEspiao(), limiar=limiar)

    assert persistencia.chamadas == [
        "chave_processada",
        "consultar_por_contato",
        "preservar_pendente",
        "marcar_chave_processada",
    ]


# --------------------------------------------------------------------------
# E. Ordem normativa e conteúdo preservado (`TS45-5`, `TS45-7`)
# --------------------------------------------------------------------------


def test_a_ordem_e_preservar_depois_alertar_depois_marcar() -> None:
    diario: list[str] = []
    entrada = entrada_ficticia()
    persistencia = PersistenciaInstrumentada(
        memoria_com(registro_ficticio(estado=None)), diario=diario
    )
    alerta = AlertaEspiao(diario=diario)

    coordenar(entrada, persistencia, alerta)

    assert diario == [
        "chave_processada",
        "consultar_por_contato",
        "preservar_pendente",
        "tentar_alerta",
        "marcar_chave_processada",
    ]


def test_o_conteudo_preservado_e_a_mensagem_normalizada_e_nao_a_bruta() -> None:
    entrada = entrada_ficticia(mensagem="  Posso    levar\tbolo? ")
    persistencia = PersistenciaInstrumentada(
        memoria_com(registro_ficticio(estado=None))
    )

    coordenar(entrada, persistencia, AlertaEspiao())

    (pendente,) = persistencia.recuperar_pendentes()
    assert pendente.conteudo == "Posso levar bolo?"
    assert pendente.conteudo != entrada.mensagem


def test_o_pendente_usa_exatamente_os_tres_campos_existentes() -> None:
    """`TS45-4` — zero campo novo, zero DTO novo."""
    entrada, persistencia, limiar = cenario_contexto_corrompido()

    coordenar(entrada, persistencia, AlertaEspiao(), limiar=limiar)

    (pendente,) = persistencia.recuperar_pendentes()
    assert isinstance(pendente, ProcessamentoPendente)
    assert pendente.canal == CANAL
    assert pendente.contato == CONTATO
    assert pendente.conteudo == MENSAGEM_NORMALIZADA


# --------------------------------------------------------------------------
# F. Alerta — payload fechado e sanitizado (`TS45-14`)
# --------------------------------------------------------------------------


def test_o_alerta_e_chamado_por_palavras_chave_com_exatamente_tres_informacoes() -> None:
    entrada, persistencia, limiar = cenario_identificador_nao_resolvido()
    alerta = AlertaEspiao()

    coordenar(entrada, persistencia, alerta, limiar=limiar)

    (payload,) = alerta.chamadas
    assert set(payload) == {"categoria", "pendente_preservado", "correlacao"}


def test_a_categoria_do_alerta_pertence_as_sete_classes_autorizadas() -> None:
    for nome in sorted(CENARIOS_TS45):
        construir, _ = CENARIOS_TS45[nome]
        entrada, persistencia, limiar = construir()
        alerta = AlertaEspiao()

        coordenar(entrada, persistencia, alerta, limiar=limiar)

        (payload,) = alerta.chamadas
        assert payload["categoria"] == nome
        assert payload["categoria"] in AS_SETE_CLASSES


def test_a_correlacao_do_alerta_e_a_chave_de_idempotencia_opaca() -> None:
    entrada, persistencia, limiar = cenario_marco_temporal_ausente()
    alerta = AlertaEspiao()

    coordenar(entrada, persistencia, alerta, limiar=limiar)

    (payload,) = alerta.chamadas
    assert payload["correlacao"] == chave_de(entrada)
    assert payload["pendente_preservado"] is True


def test_o_alerta_nao_transporta_mensagem_contato_canal_nem_identificador() -> None:
    entrada = entrada_ficticia(
        mensagem="conteudo-ficticio-sensivel", id_atendimento="atendimento-fake-segredo"
    )
    persistencia = PersistenciaInstrumentada()
    alerta = AlertaEspiao()

    coordenar(entrada, persistencia, alerta)

    (payload,) = alerta.chamadas
    serializado = repr(payload)
    for proibido in (
        "conteudo-ficticio-sensivel",
        "atendimento-fake-segredo",
        CANAL,
        CONTATO,
    ):
        assert proibido not in serializado


def test_o_alerta_nao_transporta_repr_nem_texto_da_excecao() -> None:
    entrada, persistencia, limiar = cenario_identificador_nao_resolvido()
    alerta = AlertaEspiao()

    coordenar(entrada, persistencia, alerta, limiar=limiar)

    (payload,) = alerta.chamadas
    serializado = repr(payload)
    assert "Traceback" not in serializado
    assert "não foi resolvido" not in serializado
    assert payload["categoria"] == "IdentificadorNaoResolvido"


def test_o_retorno_do_alerta_e_ignorado() -> None:
    entrada, persistencia, limiar = cenario_contexto_corrompido()
    alerta = AlertaEspiao()

    assert coordenar(entrada, persistencia, alerta, limiar=limiar) is None
    assert alerta.chamadas != []


def test_uma_dependencia_posicional_nao_satisfaz_o_contrato_do_alerta() -> None:
    """`OMR1-6` — a chamada é por palavras-chave, sem DTO e sem `Protocol`."""

    def apenas_posicional(categoria: str, /) -> None:  # pragma: no cover - contrato
        raise AssertionError("o alerta nunca é chamado posicionalmente")

    entrada, persistencia, limiar = cenario_contexto_corrompido()

    assert coordenar(entrada, persistencia, apenas_posicional, limiar=limiar) is None
    assert persistencia.ja_marcada(chave_de(entrada)) is True


# --------------------------------------------------------------------------
# G. OL-4 — semântica e precedência de falhas
# --------------------------------------------------------------------------


def persistencia_que_falha_ao_preservar(
    diario: list[str] | None = None,
    interna: PersistenciaEmMemoria | None = None,
) -> tuple[PersistenciaInstrumentada, FalhaSimuladaDePreservacao]:
    erro = FalhaSimuladaDePreservacao("falha simulada ao preservar o pendente")
    return (
        PersistenciaInstrumentada(
            memoria_com(registro_ficticio(estado=None)) if interna is None else interna,
            diario=diario,
            erro_de_preservacao=erro,
        ),
        erro,
    )


def test_falha_de_preservacao_relanca_por_identidade_e_nao_marca_a_chave() -> None:
    """`TS45-11` — o tratamento não conclui e a chave permanece desmarcada."""
    entrada = entrada_ficticia()
    persistencia, erro = persistencia_que_falha_ao_preservar()
    alerta = AlertaEspiao()

    with pytest.raises(FalhaSimuladaDePreservacao) as capturado:
        coordenar(entrada, persistencia, alerta)

    assert capturado.value is erro
    assert persistencia.ja_marcada(chave_de(entrada)) is False
    assert "marcar_chave_processada" not in persistencia.chamadas


def test_falha_de_preservacao_ainda_tenta_o_alerta_com_pendente_preservado_falso() -> None:
    entrada = entrada_ficticia()
    persistencia, _ = persistencia_que_falha_ao_preservar()
    alerta = AlertaEspiao()

    with pytest.raises(FalhaSimuladaDePreservacao):
        coordenar(entrada, persistencia, alerta)

    (payload,) = alerta.chamadas
    assert payload["pendente_preservado"] is False
    assert payload["categoria"] == "ContextoElegibilidadeCorrompido"


def test_falha_de_preservacao_tenta_o_alerta_antes_de_propagar() -> None:
    diario: list[str] = []
    persistencia, _ = persistencia_que_falha_ao_preservar(diario)
    alerta = AlertaEspiao(diario=diario)

    with pytest.raises(FalhaSimuladaDePreservacao):
        coordenar(entrada_ficticia(), persistencia, alerta)

    assert diario == [
        "chave_processada",
        "consultar_por_contato",
        "preservar_pendente",
        "tentar_alerta",
    ]


def test_falha_do_alerta_nao_substitui_a_falha_da_preservacao() -> None:
    """OL-4 B — a exceção que propaga é a da preservação, por identidade."""
    entrada = entrada_ficticia()
    persistencia, erro = persistencia_que_falha_ao_preservar()
    alerta = AlertaEspiao(falhar=True)

    with pytest.raises(FalhaSimuladaDePreservacao) as capturado:
        coordenar(entrada, persistencia, alerta)

    assert capturado.value is erro
    assert capturado.value is not alerta.erro
    assert alerta.chamadas != []
    assert persistencia.ja_marcada(chave_de(entrada)) is False


def test_falha_do_alerta_apos_preservacao_marca_a_chave_e_encerra_sem_transicao() -> None:
    """`TS45-12` — a mensagem já está protegida pelo pendente."""
    entrada = entrada_ficticia()
    persistencia = PersistenciaInstrumentada(
        memoria_com(registro_ficticio(estado=None))
    )
    alerta = AlertaEspiao(falhar=True)

    assert coordenar(entrada, persistencia, alerta) is None

    assert persistencia.recuperar_pendentes() != ()
    assert persistencia.ja_marcada(chave_de(entrada)) is True
    assert len(alerta.chamadas) == 1


def test_a_tentativa_de_alerta_nao_tem_retry() -> None:
    entrada, persistencia, limiar = cenario_marco_temporal_ausente()
    alerta = AlertaEspiao(falhar=True)

    coordenar(entrada, persistencia, alerta, limiar=limiar)

    assert len(alerta.chamadas) == 1


def test_falha_da_marcacao_propaga_por_identidade_e_nao_apaga_o_pendente() -> None:
    """`TS45-13` — sem retry, sem compensação, sem apagar o pendente."""
    erro = FalhaSimuladaDeMarcacao("falha simulada ao marcar a chave")
    entrada = entrada_ficticia()
    persistencia = PersistenciaInstrumentada(
        memoria_com(registro_ficticio(estado=None)), erro_de_marcacao=erro
    )
    alerta = AlertaEspiao()

    with pytest.raises(FalhaSimuladaDeMarcacao) as capturado:
        coordenar(entrada, persistencia, alerta)

    assert capturado.value is erro
    assert persistencia.recuperar_pendentes() != ()
    assert len(alerta.chamadas) == 1
    assert persistencia.chamadas.count("marcar_chave_processada") == 1


# --------------------------------------------------------------------------
# H. Reentrega técnica (`TS45-9`, `E4-9`)
# --------------------------------------------------------------------------


def test_reentrega_depois_do_ts45_concluido_encerra_na_etapa_2() -> None:
    entrada = entrada_ficticia()
    interna = memoria_com(registro_ficticio(estado=None))
    primeira = PersistenciaInstrumentada(interna)
    alerta = AlertaEspiao()

    assert coordenar(entrada, primeira, alerta) is None
    assert len(interna.recuperar_pendentes()) == 1
    assert len(alerta.chamadas) == 1

    segunda = PersistenciaInstrumentada(interna)
    assert coordenar(entrada, segunda, alerta) is None

    assert segunda.chamadas == ["chave_processada"]
    assert len(interna.recuperar_pendentes()) == 1
    assert len(alerta.chamadas) == 1


def test_reentrega_depois_de_preservacao_falha_repete_o_tratamento() -> None:
    """`TS45-11` — *at-least-once*: a prioridade é não perder a mensagem."""
    entrada = entrada_ficticia()
    interna = memoria_com(registro_ficticio(estado=None))
    persistencia, _ = persistencia_que_falha_ao_preservar(interna=interna)
    alerta = AlertaEspiao()

    with pytest.raises(FalhaSimuladaDePreservacao):
        coordenar(entrada, persistencia, alerta)

    segunda = PersistenciaInstrumentada(interna)
    assert coordenar(entrada, segunda, alerta) is None
    assert "preservar_pendente" in segunda.chamadas
    assert len(alerta.chamadas) == 2


# --------------------------------------------------------------------------
# I. Fora do gatilho fechado (`TS45-2`, `TS45-19`)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "erro",
    [
        FalhaSimuladaDeLeitura("falha simulada de leitura"),
        FalhaDeLeituraQueEValueError("value error que não é das sete"),
        RuntimeError("erro fora do contrato"),
        KeyError("chave ausente"),
    ],
)
def test_excecao_fora_das_sete_propaga_intacta_e_nao_dispara_ts45(
    erro: Exception,
) -> None:
    entrada = entrada_ficticia()
    persistencia = PersistenciaInstrumentada(erro_de_leitura=erro)
    alerta = AlertaEspiao()

    with pytest.raises(type(erro)) as capturado:
        coordenar(entrada, persistencia, alerta)

    assert capturado.value is erro
    assert persistencia.recuperar_pendentes() == ()
    assert persistencia.ja_marcada(chave_de(entrada)) is False
    assert alerta.chamadas == []


def test_value_error_generico_nao_e_capturado_como_ts45() -> None:
    """A captura é por classe nomeada: `except ValueError:` seria proibido."""
    entrada = entrada_ficticia()
    erro = ValueError("value error cru")
    persistencia = PersistenciaInstrumentada(erro_de_leitura=erro)
    alerta = AlertaEspiao()

    with pytest.raises(ValueError) as capturado:
        coordenar(entrada, persistencia, alerta)

    assert capturado.value is erro
    assert alerta.chamadas == []


# --------------------------------------------------------------------------
# J. Camada B — provas estruturais por AST
# --------------------------------------------------------------------------


def test_a_captura_ts45_contem_exatamente_as_sete_classes_nomeadas() -> None:
    tuplas = [
        handler
        for handler in handlers_do_modulo()
        if isinstance(handler.type, ast.Tuple)
    ]
    assert len(tuplas) == 1

    nomes = [elemento.id for elemento in tuplas[0].type.elts]  # type: ignore[union-attr]
    assert tuple(nomes) == AS_SETE_CLASSES
    assert len(set(nomes)) == 7


def test_existe_exatamente_um_except_exception_e_ele_envolve_so_o_alerta() -> None:
    arvore = arvore_do_modulo()
    genericos = [
        handler
        for handler in ast.walk(arvore)
        if isinstance(handler, ast.ExceptHandler)
        and isinstance(handler.type, ast.Name)
        and handler.type.id == "Exception"
    ]
    assert len(genericos) == 1

    donos = [
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef)
        and any(genericos[0] is filho for filho in ast.walk(no))
    ]
    assert [no.name for no in donos] == ["_tentar_alerta_operacional"]

    (tentativa,) = [
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.Try) and genericos[0] in no.handlers
    ]
    assert len(tentativa.body) == 1
    corpo = tentativa.body[0]
    assert isinstance(corpo, ast.Expr)
    assert isinstance(corpo.value, ast.Call)
    assert isinstance(corpo.value.func, ast.Name)
    assert corpo.value.func.id == "tentar_alerta"
    assert corpo.value.args == []
    assert sorted(palavra.arg for palavra in corpo.value.keywords) == [
        "categoria",
        "correlacao",
        "pendente_preservado",
    ]


def test_nenhum_except_value_error_e_nenhum_except_base_exception() -> None:
    for handler in handlers_do_modulo():
        alvos: list[ast.expr] = []
        if isinstance(handler.type, ast.Tuple):
            alvos.extend(handler.type.elts)
        elif handler.type is not None:
            alvos.append(handler.type)
        else:  # pragma: no cover - `except:` nu seria falha imediata
            raise AssertionError("except nu é proibido")
        for alvo in alvos:
            assert isinstance(alvo, ast.Name)
            assert alvo.id not in {"ValueError", "BaseException"}


def test_nenhuma_classe_enum_dto_ou_excecao_nova() -> None:
    arvore = arvore_do_modulo()
    assert [no.name for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)] == []


def test_a_superficie_publica_tem_exatamente_um_nome() -> None:
    assert orchestrator.__all__ == ["coordenar_etapas_1_a_3"]

    arvore = arvore_do_modulo()
    definidos = [
        no.name
        for no in arvore.body
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not no.name.startswith("_")
    ]
    assert definidos == ["coordenar_etapas_1_a_3"]


def test_o_modulo_nao_e_exportado_pelo_init_do_pacote() -> None:
    assert "coordenar_etapas_1_a_3" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "coordenar_etapas_1_a_3")

    arvore = ast.parse(MODULO_INIT.read_text(encoding="utf-8"))
    modulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert "casa77_sdr.orchestrator" not in modulos


def test_apenas_imports_permitidos() -> None:
    arvore = arvore_do_modulo()
    raizes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            raizes.update(a.name.split(".")[0] for a in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            raizes.add(no.module.split(".")[0])
    assert raizes == {"__future__", "collections", "datetime", "casa77_sdr"}

    submodulos = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
    }
    assert submodulos == {
        "__future__",
        "collections.abc",
        "datetime",
        "casa77_sdr.context",
        "casa77_sdr.eligibility",
        "casa77_sdr.normalization",
        "casa77_sdr.persistence",
    }


def test_nenhum_import_das_etapas_4_a_14_nem_de_infraestrutura_externa() -> None:
    nomes = nomes_usados(MODULO)
    for proibido in (
        "casa77_sdr.interpretation",
        "casa77_sdr.interpretation_llm",
        "casa77_sdr.interpretation_anthropic",
        "casa77_sdr.interpretation_events",
        "casa77_sdr.interpretation_stage",
        "casa77_sdr.identity",
        "casa77_sdr.data_update",
        "casa77_sdr.rules",
        "casa77_sdr.qualification",
        "casa77_sdr.coverage_decision",
        "casa77_sdr.coverage_map",
        "casa77_sdr.coverage_map_load",
        "casa77_sdr.cycle_events",
        "casa77_sdr.cycle_inputs",
        "casa77_sdr.handoff_detection",
        "casa77_sdr.closure_decision",
        "casa77_sdr.state_machine",
        "casa77_sdr.fragment_snapshot",
        "casa77_sdr.fragment_emissibility",
        "casa77_sdr.emission_projection",
        "casa77_sdr.fact_selection",
        "casa77_sdr.response_assembly",
        "casa77_sdr.knowledge",
        "casa77_sdr.pricing_applicability",
        "anthropic",
        "openai",
        "yaml",
        "requests",
        "httpx",
        "logging",
        "os",
        "socket",
        "random",
    ):
        assert proibido not in nomes


def test_nenhuma_chamada_das_etapas_4_a_14() -> None:
    nomes = nomes_usados(MODULO)
    for proibido in (
        "interpretar_mensagem",
        "executar_interpretacao_do_ciclo",
        "resolver_identidade",
        "atualizar_dados_atendimento",
        "avaliar_regras",
        "qualificar",
        "decidir_pendencias_e_cobertura",
        "produzir_eventos_da_interpretacao",
        "produzir_eventos_internos_ciclo",
        "detectar_handoff",
        "decidir_encerramento",
        "agregar_eventos_primeira_decisao",
        "montar_condicoes_ciclo",
        "decidir",
        "montar_fotografia_fragmento",
        "projetar_emissao",
        "selecionar_fatos",
        "montar_resposta",
        "validar_resposta",
        "criar",
        "gravar",
        "load_knowledge",
    ):
        assert proibido not in nomes


def test_zero_relogio_vivo_e_zero_io() -> None:
    nomes = nomes_usados(MODULO)
    for proibido in (
        "now",
        "today",
        "utcnow",
        "monotonic",
        "perf_counter",
        "time",
        "sleep",
        "open",
        "Path",
        "logger",
        "print",
        "environ",
        "getenv",
    ):
        assert proibido not in nomes

    arvore = arvore_do_modulo()
    (importado,) = [
        no
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module == "datetime"
    ]
    assert {a.name for a in importado.names} == {"timedelta"}


def test_zero_duracao_literal_operacional() -> None:
    """Janela e limiar chegam do chamador: o módulo não os fabrica."""
    arvore = ast.parse(codigo_executavel(MODULO))
    chamadas = [
        no.func.id
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
    ]
    assert "timedelta" not in chamadas
    assert "datetime" not in chamadas

    numericas = [
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, (int, float))
        and not isinstance(no.value, bool)
    ]
    assert numericas == []


def test_nenhum_valor_default_para_janela_limiar_ou_alerta() -> None:
    """`OMR1-4` e `OMR1-5` — zero default; tudo chega explícito do chamador."""
    (funcao,) = [
        no
        for no in arvore_do_modulo().body
        if isinstance(no, ast.FunctionDef) and no.name == "coordenar_etapas_1_a_3"
    ]
    assert funcao.args.defaults == []
    assert funcao.args.kw_defaults == [None, None, None, None]
    assert [arg.arg for arg in funcao.args.kwonlyargs] == [
        "persistencia",
        "janela_idempotencia",
        "limiar_recencia",
        "tentar_alerta",
    ]
    assert [arg.arg for arg in funcao.args.args] == ["entrada"]
