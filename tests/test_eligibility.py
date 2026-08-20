"""Testes da política N-a — produção do conjunto elegível E (doc 07 §6.2).

Fixtures totalmente artificiais: canais, contatos, identificadores e valores
claramente fictícios, sem dado pessoal real, sem valor comercial e sem
relação com a operação real.

Os testes provam que a política é **pura e determinística**: nada aqui
recupera, persiste, produz **H**, produz `havia_estado_esperado`, produz
`id_atendimento_validado`, escreve o marco temporal (N-a-T3–N-a-T7) ou chama
o `ResolvedorIdentidade` — esses pertencem a componentes futuros.

Nenhum valor operacional de limiar é fixado: as durações abaixo são
artificiais e existem apenas para exercitar a borda da regra de recência.
"""

from __future__ import annotations

import ast
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from casa77_sdr.eligibility import (
    ConfiguracaoTemporalInvalida,
    ContextoElegibilidadeCorrompido,
    IdentificadoIncoerente,
    MarcoTemporalAusente,
    produzir_conjunto_elegivel,
)
from casa77_sdr.identity import CandidatoAtendimento
from casa77_sdr.persistence import RegistroAtendimento
from casa77_sdr.state_machine import Estado

RAIZ = Path(__file__).resolve().parents[1]
MODULO_ELEGIBILIDADE = RAIZ / "src" / "casa77_sdr" / "eligibility.py"

REFERENCIA = datetime(2000, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
LIMIAR = timedelta(days=7)

GRUPO_I = (
    Estado.NOVO,
    Estado.COLETANDO_DADOS,
    Estado.RESPONDENDO_DUVIDAS,
    Estado.AGUARDANDO_CONFIRMACAO_DISPONIBILIDADE,
    Estado.PRONTO_PARA_HANDOFF,
    Estado.ENCAMINHADO_HUMANO,
)


def registro_ficticio(
    id_atendimento: str = "atendimento-fake-1",
    estado: str | None = "novo",
    *,
    tipo_evento: object = "tipo-artificial-a",
    data_nomeada: object = "data-artificial-a",
    instante_ultima_transicao: datetime | None = None,
) -> RegistroAtendimento:
    """Registro artificial com valores opacos não comerciais."""
    dados: dict[str, object] = {}
    if tipo_evento is not ...:
        dados["tipo_evento"] = tipo_evento
    if data_nomeada is not ...:
        dados["data_nomeada"] = data_nomeada
    return RegistroAtendimento(
        id_atendimento=id_atendimento,
        canal="canal-teste",
        contato="contato-fake-1",
        estado_conversa=estado,
        dados_coletados=dados,
        instante_ultima_transicao=instante_ultima_transicao,
    )


def produzir(
    registros: tuple[RegistroAtendimento, ...],
    *,
    identificado: RegistroAtendimento | None = None,
    referencia: datetime = REFERENCIA,
    limiar: timedelta | None = LIMIAR,
) -> tuple[CandidatoAtendimento, ...]:
    return produzir_conjunto_elegivel(
        registros,
        registro_identificado=identificado,
        instante_de_referencia_do_ciclo=referencia,
        limiar_recencia=limiar,
    )


# 1. K-Na-1 — Grupo I é elegível sem consultar recência


@pytest.mark.parametrize("estado", GRUPO_I)
def test_grupo_i_e_elegivel_sem_consultar_recencia(estado: Estado) -> None:
    registro = registro_ficticio(estado=estado.value)

    elegiveis = produzir((registro,))

    assert len(elegiveis) == 1
    assert elegiveis[0].estado is estado


@pytest.mark.parametrize("estado", GRUPO_I)
def test_grupo_i_sem_marco_temporal_nao_bloqueia(estado: Estado) -> None:
    """Marco ausente no Grupo I é irrelevante: a recência não é consultada."""
    registro = registro_ficticio(estado=estado.value, instante_ultima_transicao=None)

    elegiveis = produzir((registro,))

    assert len(elegiveis) == 1


# 2. K-Na-2 e K-Na-3 — recência exclusiva de `encerrado`


def test_encerrado_dentro_do_limiar_e_elegivel() -> None:
    registro = registro_ficticio(
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - LIMIAR + timedelta(seconds=1),
    )

    assert len(produzir((registro,))) == 1


def test_encerrado_exatamente_no_limiar_e_elegivel_borda_inclusiva() -> None:
    registro = registro_ficticio(
        estado="encerrado", instante_ultima_transicao=REFERENCIA - LIMIAR
    )

    assert len(produzir((registro,))) == 1


def test_encerrado_fora_do_limiar_nao_e_elegivel() -> None:
    registro = registro_ficticio(
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - LIMIAR - timedelta(seconds=1),
    )

    assert produzir((registro,)) == ()


# 3. K-Na-4 e K-Na-6 (parcela N-a-F1) — o identificado prevalece


def test_identificado_fora_do_limiar_entra_por_na_f1() -> None:
    registro = registro_ficticio(
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - LIMIAR - timedelta(days=3650),
    )

    elegiveis = produzir((registro,), identificado=registro)

    assert len(elegiveis) == 1
    assert elegiveis[0].estado is Estado.ENCERRADO


def test_identificado_sem_marco_temporal_nao_consulta_recencia() -> None:
    """N-a-F1 dispensa a recência — logo o marco sequer é lido."""
    registro = registro_ficticio(estado="encerrado", instante_ultima_transicao=None)

    assert len(produzir((registro,), identificado=registro)) == 1


def test_atendimento_humano_fica_fora_de_e_sem_identificado() -> None:
    registro = registro_ficticio(estado="atendimento_humano")

    assert produzir((registro,)) == ()


def test_atendimento_humano_identificado_entra_exatamente_uma_vez() -> None:
    """K-Na-6, somente na parcela N-a-F1. **Não** prova H5 — H não é produzido aqui."""
    registro = registro_ficticio(estado="atendimento_humano")

    elegiveis = produzir((registro,), identificado=registro)

    assert len(elegiveis) == 1
    assert elegiveis[0].estado is Estado.ATENDIMENTO_HUMANO
    assert [c.id_atendimento for c in elegiveis].count("atendimento-fake-1") == 1


def test_identificado_nao_duplica_candidato_do_grupo_i() -> None:
    registro = registro_ficticio(estado="coletando_dados")

    elegiveis = produzir((registro,), identificado=registro)

    assert len(elegiveis) == 1


# 4. K-Na-7 — marco temporal exigido e ausente


def test_encerrado_sem_marco_temporal_bloqueia() -> None:
    registro = registro_ficticio(estado="encerrado", instante_ultima_transicao=None)

    with pytest.raises(MarcoTemporalAusente):
        produzir((registro,))


# 5. K-Na-8 — limiar inválido bloqueia, inclusive sem candidato encerrado


@pytest.mark.parametrize(
    "limiar",
    [None, "7 dias", 7, 7.0, True, timedelta(0), timedelta(seconds=-1)],
)
def test_limiar_invalido_bloqueia(limiar: object) -> None:
    registro = registro_ficticio(estado="novo")

    with pytest.raises(ConfiguracaoTemporalInvalida):
        produzir((registro,), limiar=limiar)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "limiar",
    [None, "7 dias", 7, timedelta(0), timedelta(seconds=-1)],
)
def test_limiar_invalido_bloqueia_mesmo_sem_registros(limiar: object) -> None:
    """N-a-L5: configuração inválida não fica latente esperando um encerrado."""
    with pytest.raises(ConfiguracaoTemporalInvalida):
        produzir((), limiar=limiar)  # type: ignore[arg-type]


def test_limiar_positivo_e_aceito() -> None:
    assert produzir((), limiar=timedelta(microseconds=1)) == ()


# 6. K-Na-9 — projeção sem inferência


@pytest.mark.parametrize("ausente", [..., None])
def test_tipo_evento_ausente_ou_none_projeta_none(ausente: object) -> None:
    registro = registro_ficticio(tipo_evento=ausente)

    assert produzir((registro,))[0].tipo_evento_registrado is None


@pytest.mark.parametrize("ausente", [..., None])
def test_data_nomeada_ausente_ou_none_projeta_none(ausente: object) -> None:
    registro = registro_ficticio(data_nomeada=ausente)

    assert produzir((registro,))[0].data_nomeada_registrada is None


def test_valores_textuais_sao_transportados_sem_transformacao() -> None:
    registro = registro_ficticio(
        tipo_evento="tipo-artificial-b", data_nomeada="data-artificial-b"
    )

    candidato = produzir((registro,))[0]

    assert candidato.tipo_evento_registrado == "tipo-artificial-b"
    assert candidato.data_nomeada_registrada == "data-artificial-b"


@pytest.mark.parametrize("valor", [7, 7.0, True, ["texto"], {"a": "b"}, object()])
def test_tipo_evento_nao_textual_e_corrupcao(valor: object) -> None:
    registro = registro_ficticio(tipo_evento=valor)

    with pytest.raises(ContextoElegibilidadeCorrompido):
        produzir((registro,))


@pytest.mark.parametrize("valor", [7, 7.0, ["texto"], {"a": "b"}, object()])
def test_data_nomeada_nao_textual_e_corrupcao(valor: object) -> None:
    registro = registro_ficticio(data_nomeada=valor)

    with pytest.raises(ContextoElegibilidadeCorrompido):
        produzir((registro,))


@pytest.mark.parametrize("estado", [None, "", "estado-inexistente", "NOVO", "Encerrado"])
def test_estado_ausente_ou_fora_dos_oito_e_corrupcao(estado: str | None) -> None:
    registro = registro_ficticio(estado=estado)

    with pytest.raises(ContextoElegibilidadeCorrompido):
        produzir((registro,))


@pytest.mark.parametrize("estado", [7, 7.0, True, object()])
def test_estado_nao_textual_hashavel_e_corrupcao(estado: object) -> None:
    registro = registro_ficticio(estado=estado)  # type: ignore[arg-type]

    with pytest.raises(ContextoElegibilidadeCorrompido):
        produzir((registro,))


@pytest.mark.parametrize("estado", [["novo"], {}, {"estado": "novo"}, {"novo"}])
def test_estado_nao_hashavel_e_corrupcao_e_nao_typeerror(estado: object) -> None:
    """Valor não-hashável não pode virar `TypeError` incidental de `in` (N-a-P1)."""
    registro = registro_ficticio(estado=estado)  # type: ignore[arg-type]

    with pytest.raises(ContextoElegibilidadeCorrompido):
        produzir((registro,))


def test_os_oito_estados_oficiais_projetam(   ) -> None:
    for estado in Estado:
        registro = registro_ficticio(
            estado=estado.value, instante_ultima_transicao=REFERENCIA
        )
        # Projeta sem erro; a elegibilidade é decidida depois.
        produzir((registro,))


# 7. Integridade é validada ANTES da filtragem


def test_registro_que_seria_excluido_ainda_e_validado() -> None:
    """`atendimento_humano` sairia de E — mas corrupção estrutural bloqueia antes."""
    corrompido = registro_ficticio(
        id_atendimento="atendimento-fake-2",
        estado="atendimento_humano",
        tipo_evento=7,
    )

    with pytest.raises(ContextoElegibilidadeCorrompido):
        produzir((registro_ficticio(), corrompido))


def test_encerrado_fora_do_limiar_com_estado_corrompido_bloqueia() -> None:
    corrompido = registro_ficticio(
        id_atendimento="atendimento-fake-3", estado="estado-inexistente"
    )

    with pytest.raises(ContextoElegibilidadeCorrompido):
        produzir((corrompido,))


def test_limiar_invalido_precede_a_corrupcao_do_contexto() -> None:
    corrompido = registro_ficticio(estado=None)

    with pytest.raises(ConfiguracaoTemporalInvalida):
        produzir((corrompido,), limiar=None)


# 8. K-Na-10 e K-Na-11 — duplicatas


def test_duplicatas_nao_identificadas_sao_preservadas() -> None:
    primeiro = registro_ficticio(id_atendimento="atendimento-fake-dup")
    segundo = registro_ficticio(
        id_atendimento="atendimento-fake-dup", tipo_evento="tipo-artificial-b"
    )

    elegiveis = produzir((primeiro, segundo))

    assert len(elegiveis) == 2
    assert {c.id_atendimento for c in elegiveis} == {"atendimento-fake-dup"}


def test_duplicatas_identicas_nao_sao_deduplicadas() -> None:
    registro = registro_ficticio(id_atendimento="atendimento-fake-dup")

    elegiveis = produzir((registro, registro))

    assert len(elegiveis) == 2


def test_identificado_com_zero_ocorrencias_bloqueia() -> None:
    ausente = registro_ficticio(id_atendimento="atendimento-fake-ausente")

    with pytest.raises(IdentificadoIncoerente):
        produzir((registro_ficticio(),), identificado=ausente)


def test_identificado_com_duas_ocorrencias_bloqueia() -> None:
    repetido = registro_ficticio(id_atendimento="atendimento-fake-dup")

    with pytest.raises(IdentificadoIncoerente):
        produzir((repetido, repetido), identificado=repetido)


def test_identificado_externo_com_mesmo_id_e_conteudo_divergente_bloqueia() -> None:
    """Coincidir no ID não basta: o identificado deve ser a ocorrência do contexto."""
    no_contexto = registro_ficticio(id_atendimento="atendimento-fake-x", estado="novo")
    externo = registro_ficticio(
        id_atendimento="atendimento-fake-x", estado="encerrado"
    )

    with pytest.raises(IdentificadoIncoerente):
        produzir((no_contexto,), identificado=externo)


def test_identificado_externo_divergente_apenas_nos_dados_bloqueia() -> None:
    no_contexto = registro_ficticio(id_atendimento="atendimento-fake-x")
    externo = replace(
        no_contexto, dados_coletados={"tipo_evento": "tipo-artificial-divergente"}
    )

    with pytest.raises(IdentificadoIncoerente):
        produzir((no_contexto,), identificado=externo)


def test_identificado_copia_igual_em_conteudo_e_aceito() -> None:
    """A comparação é por valor: uma cópia distinta em identidade é válida."""
    no_contexto = registro_ficticio(id_atendimento="atendimento-fake-x")
    copia = replace(no_contexto)

    assert copia is not no_contexto
    assert copia == no_contexto

    elegiveis = produzir((no_contexto,), identificado=copia)

    assert len(elegiveis) == 1
    assert elegiveis[0].id_atendimento == "atendimento-fake-x"


def test_identificado_unico_convive_com_duplicatas_de_outro_id() -> None:
    identificado = registro_ficticio(id_atendimento="atendimento-fake-id")
    outro = registro_ficticio(id_atendimento="atendimento-fake-dup")

    elegiveis = produzir((identificado, outro, outro), identificado=identificado)

    assert len(elegiveis) == 3


# 9. K-Na-12 — ordem canônica


def test_ordem_de_entrada_nao_afeta_a_saida() -> None:
    a = registro_ficticio(id_atendimento="atendimento-fake-a")
    b = registro_ficticio(id_atendimento="atendimento-fake-b", estado="coletando_dados")
    c = registro_ficticio(
        id_atendimento="atendimento-fake-c", estado="respondendo_duvidas"
    )

    assert produzir((a, b, c)) == produzir((c, a, b)) == produzir((b, c, a))


def test_ordem_canonica_e_ascendente_por_id() -> None:
    a = registro_ficticio(id_atendimento="atendimento-fake-a")
    b = registro_ficticio(id_atendimento="atendimento-fake-b")

    elegiveis = produzir((b, a))

    assert [c.id_atendimento for c in elegiveis] == [
        "atendimento-fake-a",
        "atendimento-fake-b",
    ]


def test_none_precede_texto_nos_campos_opcionais() -> None:
    com_texto = registro_ficticio(tipo_evento="tipo-artificial-a")
    sem_texto = registro_ficticio(tipo_evento=None)

    elegiveis = produzir((com_texto, sem_texto))

    assert elegiveis[0].tipo_evento_registrado is None
    assert elegiveis[1].tipo_evento_registrado == "tipo-artificial-a"


def test_ordem_nao_usa_recencia_como_criterio() -> None:
    antigo = registro_ficticio(
        id_atendimento="atendimento-fake-a",
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA - timedelta(days=6),
    )
    recente = registro_ficticio(
        id_atendimento="atendimento-fake-b",
        estado="encerrado",
        instante_ultima_transicao=REFERENCIA,
    )

    elegiveis = produzir((recente, antigo))

    assert [c.id_atendimento for c in elegiveis] == [
        "atendimento-fake-a",
        "atendimento-fake-b",
    ]


# 10. Pureza do módulo


def _modulos_importados() -> set[str]:
    """Módulos importados por `eligibility.py`, com o caminho **completo**.

    Sem colapsar `casa77_sdr.<modulo>` em `casa77_sdr`: a prova precisa
    distinguir `casa77_sdr.identity` de `casa77_sdr.rules`.
    """
    arvore = ast.parse(MODULO_ELEGIBILIDADE.read_text(encoding="utf-8"))
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module)
    return importados


def test_elegibilidade_importa_exatamente_os_modulos_autorizados() -> None:
    assert _modulos_importados() == {
        "__future__",
        "datetime",
        "casa77_sdr.identity",
        "casa77_sdr.persistence",
        "casa77_sdr.state_machine",
    }


def test_elegibilidade_sem_import_de_rede_yaml_llm_ou_persistencia_concreta() -> None:
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


def test_elegibilidade_nao_consulta_relogio_vivo() -> None:
    proibidos = {"now", "utcnow", "today", "fromtimestamp", "time", "monotonic"}

    arvore = ast.parse(MODULO_ELEGIBILIDADE.read_text(encoding="utf-8"))
    chamados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call):
            alvo = no.func
            if isinstance(alvo, ast.Attribute):
                chamados.add(alvo.attr)
            elif isinstance(alvo, ast.Name):
                chamados.add(alvo.id)

    assert not (chamados & proibidos)


def test_modulo_nao_referencia_componentes_fora_do_escopo() -> None:
    """Nem H, nem `havia_estado_esperado`, nem N-I, nem orquestração.

    A varredura é sobre **identificadores do código**, não sobre o texto: a
    docstring do módulo cita esses nomes justamente para negá-los.
    """
    proibidos = {
        "ids_em_atendimento_humano",
        "havia_estado_esperado",
        "id_atendimento_validado",
        "OrquestradorMotor",
        "resolver_identidade",
        "MaquinaEstados",
    }

    arvore = ast.parse(MODULO_ELEGIBILIDADE.read_text(encoding="utf-8"))
    identificadores = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Name):
            identificadores.add(no.id)
        elif isinstance(no, ast.Attribute):
            identificadores.add(no.attr)
        elif isinstance(no, ast.arg):
            identificadores.add(no.arg)
        elif isinstance(no, (ast.FunctionDef, ast.ClassDef)):
            identificadores.add(no.name)
        elif isinstance(no, ast.keyword) and no.arg:
            identificadores.add(no.arg)

    assert not (identificadores & proibidos)


# 11. Determinismo e ausência de mutação


def test_duas_chamadas_com_as_mesmas_entradas_produzem_a_mesma_saida() -> None:
    registros = (
        registro_ficticio(id_atendimento="atendimento-fake-a"),
        registro_ficticio(id_atendimento="atendimento-fake-b", estado="coletando_dados"),
    )

    assert produzir(registros) == produzir(registros)


def test_registros_de_entrada_nao_sao_mutados() -> None:
    registro = registro_ficticio()
    antes = replace(registro)
    dados_antes = dict(registro.dados_coletados)

    produzir((registro,), identificado=registro)

    assert registro == antes
    assert registro.dados_coletados == dados_antes


def test_saida_nao_compartilha_estado_mutavel_com_a_entrada() -> None:
    registro = registro_ficticio()

    elegiveis = produzir((registro,))

    registro.dados_coletados["tipo_evento"] = "mutado"
    assert elegiveis[0].tipo_evento_registrado == "tipo-artificial-a"


def test_conjunto_vazio_devolve_tupla_vazia() -> None:
    assert produzir(()) == ()
