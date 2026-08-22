"""Testes da fronteira de aplicação e escrita do marco temporal (doc 07 §6.2).

As duas funções sob teste **aplicam** a decisão já materializada em
`transition_marker.py` sobre um `RegistroAtendimento` **recebido pronto** e
**escrevem** pelo contrato existente da persistência. Elas **não** montam o
registro, **não** decidem se a etapa 13 executa, **não** escolhem entre criar e
gravar — a operação chega pronta na função chamada —, **não** geram
`id_atendimento`, **não** marcam idempotência e **não** tratam falha.

Fixtures totalmente artificiais: canais, contatos, identificadores e instantes
claramente fictícios, sem dado pessoal, sem conversa real e sem dado comercial.

Onde o comportamento da `MaquinaEstados` é o que está sendo provado — T33 que
preserva estado e o ciclo `encerrado` → reabertura → `encerrado` —, as decisões
vêm de `decidir(...)` **real**, nunca fabricadas à mão.
"""

from __future__ import annotations

import ast
import inspect
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from casa77_sdr.persistence import (
    FalhaDePersistencia,
    PersistenciaEmMemoria,
    PersistenciaOperacional,
    RegistroAtendimento,
    ResultadoRecuperacao,
)
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
from casa77_sdr.transition_marker_write import (
    criar_com_marco_de_transicao,
    gravar_com_marco_de_transicao,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "casa77_sdr" / "transition_marker_write.py"

CICLO = datetime(2000, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
MARCO_ANTERIOR = datetime(2000, 6, 1, 8, 30, 0, tzinfo=timezone.utc)

CANAL = "canal-ficticio"
CONTATO = "contato-ficticio"

SEM_CONDICOES = CondicoesCiclo()
INCOMPLETOS = Qualificacao(
    resultado=ResultadoQualificacao.DADOS_INCOMPLETOS,
    motivo=MotivoQualificacao.CAMPOS_OBRIGATORIOS_AUSENTES,
    campos_ausentes=("nome",),
)


def registro_ficticio(
    *,
    id_atendimento: str = "atendimento-fake-a",
    canal: str = CANAL,
    contato: str = CONTATO,
    instante_ultima_transicao: datetime | None = None,
) -> RegistroAtendimento:
    """Registro sintético completo, sem PII e sem dado comercial."""
    return RegistroAtendimento(
        id_atendimento=id_atendimento,
        canal=canal,
        contato=contato,
        estado_conversa="coletando_dados",
        dados_coletados={"tipo_evento": "evento-ficticio"},
        resultado_qualificacao="dados_incompletos",
        pendencias_resposta=("pendencia-ficticia",),
        motivo_incompatibilidade=None,
        motivos_handoff=("motivo-ficticio",),
        instante_ultima_transicao=instante_ultima_transicao,
    )


def decisao_vazia() -> DecisaoMaquina:
    return DecisaoMaquina(estado_final=Estado.COLETANDO_DADOS)


def decisao_com_mudanca() -> DecisaoMaquina:
    return DecisaoMaquina(
        estado_final=Estado.COLETANDO_DADOS,
        caminho=(Transicao.T01,),
        transicoes_que_mudaram_estado=(Transicao.T01,),
    )


class PersistenciaEspia(PersistenciaOperacional):
    """Espião que registra a ordem das operações do contrato."""

    def __init__(self, interna: PersistenciaEmMemoria | None = None) -> None:
        self._interna = interna if interna is not None else PersistenciaEmMemoria()
        self.chamadas: list[str] = []

    def criar(self, registro: RegistroAtendimento) -> None:
        self.chamadas.append("criar")
        self._interna.criar(registro)

    def gravar(self, registro: RegistroAtendimento) -> None:
        self.chamadas.append("gravar")
        self._interna.gravar(registro)

    def recuperar_por_id(self, id_atendimento: str, canal: str, contato: str):
        self.chamadas.append("recuperar_por_id")
        return self._interna.recuperar_por_id(id_atendimento, canal, contato)

    def consultar_por_contato(self, canal: str, contato: str):
        self.chamadas.append("consultar_por_contato")
        return self._interna.consultar_por_contato(canal, contato)

    def chave_processada(self, chave: str) -> bool:
        self.chamadas.append("chave_processada")
        return self._interna.chave_processada(chave)

    def marcar_chave_processada(self, chave: str) -> None:
        self.chamadas.append("marcar_chave_processada")
        self._interna.marcar_chave_processada(chave)

    def preservar_pendente(self, pendente) -> None:
        self.chamadas.append("preservar_pendente")
        self._interna.preservar_pendente(pendente)

    def recuperar_pendentes(self):
        self.chamadas.append("recuperar_pendentes")
        return self._interna.recuperar_pendentes()


def criar(
    persistencia: PersistenciaOperacional,
    *,
    registro: RegistroAtendimento | None = None,
    decisoes: tuple[DecisaoMaquina, ...] = (),
    ciclo: datetime = CICLO,
) -> RegistroAtendimento:
    return criar_com_marco_de_transicao(
        persistencia=persistencia,
        registro_base=registro if registro is not None else registro_ficticio(),
        instante_de_referencia_do_ciclo=ciclo,
        decisoes_do_ciclo=decisoes,
    )


def gravar(
    persistencia: PersistenciaOperacional,
    *,
    registro: RegistroAtendimento | None = None,
    marco: datetime | None = MARCO_ANTERIOR,
    decisoes: tuple[DecisaoMaquina, ...] = (),
    ciclo: datetime = CICLO,
) -> RegistroAtendimento:
    return gravar_com_marco_de_transicao(
        persistencia=persistencia,
        registro_base=registro if registro is not None else registro_ficticio(),
        instante_de_referencia_do_ciclo=ciclo,
        marco_atual=marco,
        decisoes_do_ciclo=decisoes,
    )


# --------------------------------------------------------------------------
# A. Criação — N-a-T3
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "decisoes",
    [(), (decisao_vazia(),), (decisao_com_mudanca(),)],
    ids=["zero-decisoes", "decisao-vazia", "decisao-com-mudanca"],
)
def test_criacao_grava_o_instante_do_ciclo(decisoes: tuple[DecisaoMaquina, ...]) -> None:
    """A projeção não é pré-requisito: criação sempre usa o instante do ciclo."""
    persistencia = PersistenciaEmMemoria()

    registro = criar(persistencia, decisoes=decisoes)

    assert registro.instante_ultima_transicao is CICLO


def test_criacao_persiste_o_marco_recuperavel() -> None:
    persistencia = PersistenciaEmMemoria()

    criar(persistencia)

    recuperado = persistencia.recuperar_por_id("atendimento-fake-a", CANAL, CONTATO)
    assert recuperado.resultado is ResultadoRecuperacao.ENCONTRADO
    assert recuperado.registro.instante_ultima_transicao == CICLO


# --------------------------------------------------------------------------
# B. Atualização — N-a-T4/T5/T6/T7
# --------------------------------------------------------------------------


def persistencia_com_registro(
    marco: datetime | None = MARCO_ANTERIOR,
) -> PersistenciaEmMemoria:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio(instante_ultima_transicao=marco))
    return persistencia


def test_uma_decisao_com_mudanca_atualiza_o_marco() -> None:
    registro = gravar(
        persistencia_com_registro(), decisoes=(decisao_com_mudanca(),)
    )

    assert registro.instante_ultima_transicao is CICLO


def test_uma_decisao_vazia_preserva_o_marco() -> None:
    registro = gravar(persistencia_com_registro(), decisoes=(decisao_vazia(),))

    assert registro.instante_ultima_transicao is MARCO_ANTERIOR


def test_zero_decisoes_preserva_o_marco() -> None:
    registro = gravar(persistencia_com_registro(), decisoes=())

    assert registro.instante_ultima_transicao is MARCO_ANTERIOR


def test_marco_none_sem_mudanca_preserva_none() -> None:
    registro = gravar(
        persistencia_com_registro(marco=None), marco=None, decisoes=(decisao_vazia(),)
    )

    assert registro.instante_ultima_transicao is None


@pytest.mark.parametrize("posicao", [0, 1], ids=["primeira", "segunda"])
def test_duas_decisoes_com_mudanca_em_qualquer_posicao_atualizam(posicao: int) -> None:
    decisoes = [decisao_vazia(), decisao_vazia()]
    decisoes[posicao] = decisao_com_mudanca()

    registro = gravar(persistencia_com_registro(), decisoes=tuple(decisoes))

    assert registro.instante_ultima_transicao is CICLO


@pytest.mark.parametrize("posicao", [0, 1, 2])
def test_tres_decisoes_com_mudanca_em_qualquer_posicao_atualizam(posicao: int) -> None:
    decisoes = [decisao_vazia(), decisao_vazia(), decisao_vazia()]
    decisoes[posicao] = decisao_com_mudanca()

    registro = gravar(persistencia_com_registro(), decisoes=tuple(decisoes))

    assert registro.instante_ultima_transicao is CICLO


def test_tres_decisoes_vazias_preservam_o_marco() -> None:
    decisoes = (decisao_vazia(), decisao_vazia(), decisao_vazia())

    registro = gravar(persistencia_com_registro(), decisoes=decisoes)

    assert registro.instante_ultima_transicao is MARCO_ANTERIOR


# --------------------------------------------------------------------------
# C. Máquina real
# --------------------------------------------------------------------------


def test_t33_real_preserva_o_marco() -> None:
    decisao = decidir(
        Estado.ATENDIMENTO_HUMANO, (Evento.E01,), INCOMPLETOS, SEM_CONDICOES
    )

    assert decisao.transicoes_que_mudaram_estado == ()

    registro = gravar(persistencia_com_registro(), decisoes=(decisao,))
    assert registro.instante_ultima_transicao is MARCO_ANTERIOR


def test_encerrado_reaberto_e_encerrado_atualiza_o_marco() -> None:
    """Estado inicial igual ao final, com mudança real no caminho."""
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

    registro = gravar(persistencia_com_registro(), decisoes=(decisao,))
    assert registro.instante_ultima_transicao is CICLO


# --------------------------------------------------------------------------
# D. Registro: só o marco muda
# --------------------------------------------------------------------------


def test_somente_o_marco_muda_no_registro_criado() -> None:
    base = registro_ficticio()

    registro = criar(PersistenciaEmMemoria(), registro=base)

    assert registro == replace(base, instante_ultima_transicao=CICLO)


def test_somente_o_marco_muda_no_registro_gravado() -> None:
    base = registro_ficticio(instante_ultima_transicao=MARCO_ANTERIOR)

    registro = gravar(
        persistencia_com_registro(), registro=base, decisoes=(decisao_com_mudanca(),)
    )

    assert registro == replace(base, instante_ultima_transicao=CICLO)
    assert registro.id_atendimento == base.id_atendimento
    assert registro.canal == base.canal
    assert registro.contato == base.contato
    assert registro.estado_conversa == base.estado_conversa
    assert registro.dados_coletados == base.dados_coletados
    assert registro.resultado_qualificacao == base.resultado_qualificacao
    assert registro.pendencias_resposta == base.pendencias_resposta
    assert registro.motivo_incompatibilidade == base.motivo_incompatibilidade
    assert registro.motivos_handoff == base.motivos_handoff


def test_registro_base_nao_e_mutado() -> None:
    base = registro_ficticio(instante_ultima_transicao=MARCO_ANTERIOR)
    antes = replace(base)
    dados_antes = dict(base.dados_coletados)

    criar(PersistenciaEmMemoria(), registro=base)

    assert base == antes
    assert base.dados_coletados == dados_antes
    assert base.instante_ultima_transicao is MARCO_ANTERIOR


def test_retorno_e_exatamente_o_registro_submetido() -> None:
    espia = PersistenciaEspia()
    submetidos: list[RegistroAtendimento] = []
    original = espia.criar

    def capturar(registro: RegistroAtendimento) -> None:
        submetidos.append(registro)
        original(registro)

    espia.criar = capturar  # type: ignore[method-assign]

    registro = criar(espia)

    assert submetidos == [registro]


# --------------------------------------------------------------------------
# E. Operação: a função escolhida define criar × gravar
# --------------------------------------------------------------------------


def test_criar_chama_somente_criar() -> None:
    espia = PersistenciaEspia()

    criar(espia)

    assert espia.chamadas == ["criar"]


def test_gravar_chama_somente_gravar() -> None:
    interna = PersistenciaEmMemoria()
    interna.criar(registro_ficticio(instante_ultima_transicao=MARCO_ANTERIOR))
    espia = PersistenciaEspia(interna)

    gravar(espia, decisoes=(decisao_com_mudanca(),))

    assert espia.chamadas == ["gravar"]


# --------------------------------------------------------------------------
# F. Persistência real em memória
# --------------------------------------------------------------------------


def test_gravacao_atualiza_o_registro_existente() -> None:
    persistencia = persistencia_com_registro()

    gravar(persistencia, decisoes=(decisao_com_mudanca(),))

    recuperado = persistencia.recuperar_por_id("atendimento-fake-a", CANAL, CONTATO)
    assert recuperado.registro.instante_ultima_transicao == CICLO


def test_gravacao_sem_mudanca_preserva_o_marco_armazenado() -> None:
    persistencia = persistencia_com_registro()

    gravar(persistencia, decisoes=(decisao_vazia(),))

    recuperado = persistencia.recuperar_por_id("atendimento-fake-a", CANAL, CONTATO)
    assert recuperado.registro.instante_ultima_transicao == MARCO_ANTERIOR


# --------------------------------------------------------------------------
# G. Erros propagam intactos
# --------------------------------------------------------------------------


def test_falha_de_persistencia_em_criar_propaga() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(FalhaDePersistencia):
        criar(persistencia)


def test_falha_de_persistencia_em_gravar_propaga() -> None:
    persistencia = persistencia_com_registro()
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(FalhaDePersistencia):
        gravar(persistencia, decisoes=(decisao_com_mudanca(),))


def test_criar_com_id_existente_propaga_e_nao_substitui() -> None:
    persistencia = persistencia_com_registro()

    with pytest.raises(ValueError):
        criar(persistencia)

    recuperado = persistencia.recuperar_por_id("atendimento-fake-a", CANAL, CONTATO)
    assert recuperado.registro.instante_ultima_transicao == MARCO_ANTERIOR


def test_gravar_com_id_inexistente_propaga_e_nao_cria() -> None:
    persistencia = PersistenciaEmMemoria()

    with pytest.raises(ValueError):
        gravar(persistencia, decisoes=(decisao_com_mudanca(),))

    recuperado = persistencia.recuperar_por_id("atendimento-fake-a", CANAL, CONTATO)
    assert recuperado.resultado is ResultadoRecuperacao.NAO_ENCONTRADO


def test_vinculo_divergente_propaga() -> None:
    persistencia = persistencia_com_registro()
    outro_vinculo = registro_ficticio(contato="outro-contato-ficticio")

    with pytest.raises(ValueError):
        gravar(persistencia, registro=outro_vinculo, decisoes=(decisao_com_mudanca(),))


def test_marco_sem_fuso_efetivo_e_rejeitado_pela_persistencia() -> None:
    """A validação de fuso não é duplicada aqui: quem rejeita é a persistência."""
    ingenuo = datetime(2000, 6, 15, 12, 0, 0)

    with pytest.raises(ValueError):
        criar(PersistenciaEmMemoria(), ciclo=ingenuo)


def test_mais_de_tres_decisoes_propaga_erro_da_decisao() -> None:
    decisoes = (decisao_vazia(),) * 4

    with pytest.raises(ValueError):
        gravar(persistencia_com_registro(), decisoes=decisoes)


def test_decisoes_de_tipo_invalido_propagam_erro_da_decisao() -> None:
    with pytest.raises(TypeError):
        gravar(persistencia_com_registro(), decisoes=(decisao_vazia(), "outra"))  # type: ignore[arg-type]


@pytest.mark.parametrize("persistencia", [None, "memoria", 7, PersistenciaEmMemoria])
def test_persistencia_invalida_e_erro_de_tipo(persistencia: object) -> None:
    with pytest.raises(TypeError) as erro:
        criar_com_marco_de_transicao(
            persistencia=persistencia,  # type: ignore[arg-type]
            registro_base=registro_ficticio(),
            instante_de_referencia_do_ciclo=CICLO,
            decisoes_do_ciclo=(),
        )

    assert "persistencia" in str(erro.value)


@pytest.mark.parametrize("registro", [None, "registro", 7, {"id": "x"}])
def test_registro_base_invalido_e_erro_de_tipo(registro: object) -> None:
    with pytest.raises(TypeError) as erro:
        gravar_com_marco_de_transicao(
            persistencia=PersistenciaEmMemoria(),
            registro_base=registro,  # type: ignore[arg-type]
            instante_de_referencia_do_ciclo=CICLO,
            marco_atual=MARCO_ANTERIOR,
            decisoes_do_ciclo=(),
        )

    assert "registro_base" in str(erro.value)


def test_mensagens_de_tipo_nao_transportam_dado_de_usuario() -> None:
    with pytest.raises(TypeError) as erro:
        criar_com_marco_de_transicao(
            persistencia="memoria",  # type: ignore[arg-type]
            registro_base=registro_ficticio(),
            instante_de_referencia_do_ciclo=CICLO,
            decisoes_do_ciclo=(),
        )

    mensagem = str(erro.value)
    assert CANAL not in mensagem
    assert CONTATO not in mensagem
    assert "atendimento-fake-a" not in mensagem


# --------------------------------------------------------------------------
# H. Ausências provadas sobre o código
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
    proibidos = {"now", "utcnow", "today", "fromtimestamp", "monotonic", "timestamp"}

    assert not (_identificadores() & proibidos)


def test_modulo_nao_faz_replay_nem_le_a_projecao_diretamente() -> None:
    proibidos = {
        "transicoes_que_mudaram_estado",
        "caminho",
        "estado_final",
        "estado_inicial",
        "decidir",
        "_REGRAS",
    }

    assert not (_identificadores() & proibidos)


def test_modulo_nao_le_a_persistencia_nem_marca_idempotencia() -> None:
    proibidos = {
        "recuperar_por_id",
        "consultar_por_contato",
        "chave_processada",
        "marcar_chave_processada",
        "preservar_pendente",
        "recuperar_pendentes",
    }

    assert not (_identificadores() & proibidos)


def test_modulo_nao_captura_excecoes_nem_orquestra() -> None:
    assert not any(isinstance(no, ast.Try) for no in ast.walk(_arvore()))

    proibidos = {"OrquestradorMotor", "logging", "print", "uuid", "uuid4"}
    assert not (_identificadores() & proibidos)


def test_modulo_importa_exatamente_os_modulos_autorizados() -> None:
    assert _modulos_importados() == {
        "__future__",
        "collections.abc",
        "dataclasses",
        "datetime",
        "casa77_sdr.persistence",
        "casa77_sdr.state_machine",
        "casa77_sdr.transition_marker",
    }


def test_modulo_nao_cria_enum_dataclass_nem_vocabulario_novo() -> None:
    assert not any(isinstance(no, ast.ClassDef) for no in ast.walk(_arvore()))


def test_modulo_nao_duplica_a_regra_de_decisao() -> None:
    """A decisão é delegada: o módulo chama, não reimplementa."""
    identificadores = _identificadores()

    assert "decidir_instante_ultima_transicao" in identificadores
    assert not (identificadores & {"any", "_houve_mudanca_no_ciclo"})


def test_funcao_nao_e_exportada_pelo_pacote() -> None:
    import casa77_sdr

    assert "criar_com_marco_de_transicao" not in casa77_sdr.__all__
    assert "gravar_com_marco_de_transicao" not in casa77_sdr.__all__
    assert not hasattr(casa77_sdr, "criar_com_marco_de_transicao")
    assert not hasattr(casa77_sdr, "gravar_com_marco_de_transicao")


# --------------------------------------------------------------------------
# I. Assinatura
# --------------------------------------------------------------------------


def test_assinatura_de_criar_e_keyword_only_sem_defaults() -> None:
    parametros = inspect.signature(criar_com_marco_de_transicao).parameters

    assert list(parametros) == [
        "persistencia",
        "registro_base",
        "instante_de_referencia_do_ciclo",
        "decisoes_do_ciclo",
    ]
    for parametro in parametros.values():
        assert parametro.kind is inspect.Parameter.KEYWORD_ONLY
        assert parametro.default is inspect.Parameter.empty


def test_assinatura_de_gravar_e_keyword_only_sem_defaults() -> None:
    parametros = inspect.signature(gravar_com_marco_de_transicao).parameters

    assert list(parametros) == [
        "persistencia",
        "registro_base",
        "instante_de_referencia_do_ciclo",
        "marco_atual",
        "decisoes_do_ciclo",
    ]
    for parametro in parametros.values():
        assert parametro.kind is inspect.Parameter.KEYWORD_ONLY
        assert parametro.default is inspect.Parameter.empty


def test_instante_com_fuso_nao_utc_e_gravado_sem_conversao() -> None:
    outro_fuso = datetime(
        2000, 6, 15, 9, 0, 0, tzinfo=timezone(timedelta(hours=-3))
    )

    registro = criar(PersistenciaEmMemoria(), ciclo=outro_fuso)

    assert registro.instante_ultima_transicao is outro_fuso
    assert registro.instante_ultima_transicao.utcoffset() == timedelta(hours=-3)
