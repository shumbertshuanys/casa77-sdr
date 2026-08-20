"""Testes da persistência operacional (3B.3).

Fixtures totalmente artificiais: canais, contatos, identificadores e
conteúdos claramente fictícios, sem dado pessoal real, sem valor comercial
e sem relação com a operação real.

Os testes provam que a persistência é infraestrutura de estado, nunca
camada de decisão: nada aqui exercita transição, qualificação, identidade
(T36/T37), handoff ou emissão — esses pertencem aos componentes futuros.
"""

from __future__ import annotations

import ast
from dataclasses import replace
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path

import pytest

from casa77_sdr.persistence import (
    FalhaDePersistencia,
    PersistenciaEmMemoria,
    ProcessamentoPendente,
    RecuperacaoPorId,
    RegistroAtendimento,
    ResultadoRecuperacao,
)

RAIZ = Path(__file__).resolve().parents[1]
MODULO_PERSISTENCIA = RAIZ / "src" / "casa77_sdr" / "persistence.py"


def registro_ficticio(
    id_atendimento: str = "atendimento-fake-1",
    canal: str = "canal-teste",
    contato: str = "contato-fake-1",
) -> RegistroAtendimento:
    """Registro artificial com valores opacos não comerciais."""
    return RegistroAtendimento(
        id_atendimento=id_atendimento,
        canal=canal,
        contato=contato,
        estado_conversa="estado-opaco-a",
        dados_coletados={"campo-artificial": "valor-artificial"},
        resultado_qualificacao="qualificacao-opaca-x",
        pendencias_resposta=("pergunta-artificial-1",),
        motivo_incompatibilidade=None,
        motivos_handoff=(),
    )


# 1. Criação explícita de atendimento


def test_criacao_explicita_e_recuperacao() -> None:
    persistencia = PersistenciaEmMemoria()
    registro = registro_ficticio()

    persistencia.criar(registro)
    resultado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )

    assert resultado.resultado is ResultadoRecuperacao.ENCONTRADO
    assert resultado.registro == registro


def test_criar_com_id_ja_existente_e_erro_explicito() -> None:
    """Criação nunca substitui silenciosamente um registro existente."""
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio())

    with pytest.raises(ValueError):
        persistencia.criar(registro_ficticio())


# 2. Recuperação correta por ID + canal + contato


def test_recuperacao_compativel_devolve_o_registro() -> None:
    persistencia = PersistenciaEmMemoria()
    registro = registro_ficticio()
    persistencia.criar(registro)

    resultado = persistencia.recuperar_por_id(
        registro.id_atendimento, registro.canal, registro.contato
    )

    assert resultado == RecuperacaoPorId(
        resultado=ResultadoRecuperacao.ENCONTRADO, registro=registro
    )


# 3. ID inexistente: NÃO ENCONTRADO e nenhum registro criado


def test_id_inexistente_devolve_nao_encontrado_sem_criar() -> None:
    persistencia = PersistenciaEmMemoria()

    resultado = persistencia.recuperar_por_id(
        "atendimento-inexistente", "canal-teste", "contato-fake-1"
    )

    assert resultado.resultado is ResultadoRecuperacao.NAO_ENCONTRADO
    assert resultado.registro is None
    assert persistencia.consultar_por_contato("canal-teste", "contato-fake-1") == ()


# 4. ID pertencente a outro contato: INCOMPATÍVEL, sem expor o registro


def test_id_de_outro_contato_devolve_incompativel_sem_expor() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio(contato="contato-fake-1"))

    resultado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-2"
    )

    assert resultado.resultado is ResultadoRecuperacao.INCOMPATIVEL
    assert resultado.registro is None


# 5. ID pertencente a outro canal: INCOMPATÍVEL, sem expor o registro


def test_id_de_outro_canal_devolve_incompativel_sem_expor() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio(canal="canal-teste"))

    resultado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-outro", "contato-fake-1"
    )

    assert resultado.resultado is ResultadoRecuperacao.INCOMPATIVEL
    assert resultado.registro is None


# 6. Consulta por canal + contato não mistura contatos nem canais


def test_consulta_por_contato_devolve_somente_os_correspondentes() -> None:
    persistencia = PersistenciaEmMemoria()
    do_par = registro_ficticio("atendimento-fake-1", "canal-teste", "contato-fake-1")
    outro_contato = registro_ficticio(
        "atendimento-fake-2", "canal-teste", "contato-fake-2"
    )
    outro_canal = registro_ficticio(
        "atendimento-fake-3", "canal-outro", "contato-fake-1"
    )
    persistencia.criar(do_par)
    persistencia.criar(outro_contato)
    persistencia.criar(outro_canal)

    resultado = persistencia.consultar_por_contato("canal-teste", "contato-fake-1")

    assert resultado == (do_par,)


def test_consulta_de_par_sem_registros_devolve_vazio() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio())

    assert persistencia.consultar_por_contato("canal-vazio", "contato-vazio") == ()


# 7. Gravação substitui e preserva valores opacos sem transformação


def test_gravacao_substitui_e_valor_armazenado_e_recuperado() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio())
    atualizado = RegistroAtendimento(
        id_atendimento="atendimento-fake-1",
        canal="canal-teste",
        contato="contato-fake-1",
        estado_conversa="estado-opaco-b",
        dados_coletados={"campo-artificial": "valor-corrigido"},
        resultado_qualificacao="qualificacao-opaca-y",
        pendencias_resposta=("pergunta-artificial-2",),
        motivo_incompatibilidade="motivo-artificial",
        motivos_handoff=("motivo-handoff-artificial",),
    )

    persistencia.gravar(atualizado)
    resultado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )

    assert resultado.registro == atualizado


def test_estado_e_qualificacao_sao_preservados_sem_transformacao() -> None:
    """Valores arbitrários e desconhecidos fazem ida e volta intactos."""
    persistencia = PersistenciaEmMemoria()
    registro = RegistroAtendimento(
        id_atendimento="atendimento-fake-1",
        canal="canal-teste",
        contato="contato-fake-1",
        estado_conversa="  Estado Opaco COM Caixa e espaços  ",
        resultado_qualificacao="valor-desconhecido-da-persistencia",
    )

    persistencia.criar(registro)
    recuperado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    ).registro

    assert recuperado is not None
    assert recuperado.estado_conversa == "  Estado Opaco COM Caixa e espaços  "
    assert recuperado.resultado_qualificacao == "valor-desconhecido-da-persistencia"


def test_gravar_id_inexistente_e_erro_explicito_e_nao_cria() -> None:
    """Gravação nunca cria atendimento (N6)."""
    persistencia = PersistenciaEmMemoria()

    with pytest.raises(ValueError):
        persistencia.gravar(registro_ficticio())

    assert (
        persistencia.recuperar_por_id(
            "atendimento-fake-1", "canal-teste", "contato-fake-1"
        ).resultado
        is ResultadoRecuperacao.NAO_ENCONTRADO
    )


# 7a. Vínculo id_atendimento × canal × contato é imutável após a criação


def test_gravar_com_mesmo_vinculo_continua_funcionando() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio())
    atualizado = RegistroAtendimento(
        id_atendimento="atendimento-fake-1",
        canal="canal-teste",
        contato="contato-fake-1",
        estado_conversa="estado-opaco-b",
    )

    persistencia.gravar(atualizado)

    assert (
        persistencia.recuperar_por_id(
            "atendimento-fake-1", "canal-teste", "contato-fake-1"
        ).registro
        == atualizado
    )


def test_gravar_com_contato_diferente_e_rejeitado_sem_reassociar() -> None:
    """Gravação nunca transfere o atendimento para outro contato."""
    persistencia = PersistenciaEmMemoria()
    original = registro_ficticio()
    persistencia.criar(original)

    with pytest.raises(ValueError):
        persistencia.gravar(
            RegistroAtendimento(
                id_atendimento="atendimento-fake-1",
                canal="canal-teste",
                contato="contato-fake-2",
                estado_conversa="estado-que-nao-deve-entrar",
            )
        )

    assert (
        persistencia.recuperar_por_id(
            "atendimento-fake-1", "canal-teste", "contato-fake-1"
        ).registro
        == original
    )
    assert persistencia.consultar_por_contato("canal-teste", "contato-fake-2") == ()


def test_gravar_com_canal_diferente_e_rejeitado_sem_reassociar() -> None:
    """Gravação nunca transfere o atendimento para outro canal."""
    persistencia = PersistenciaEmMemoria()
    original = registro_ficticio()
    persistencia.criar(original)

    with pytest.raises(ValueError):
        persistencia.gravar(
            RegistroAtendimento(
                id_atendimento="atendimento-fake-1",
                canal="canal-outro",
                contato="contato-fake-1",
                estado_conversa="estado-que-nao-deve-entrar",
            )
        )

    assert (
        persistencia.recuperar_por_id(
            "atendimento-fake-1", "canal-teste", "contato-fake-1"
        ).registro
        == original
    )
    assert persistencia.consultar_por_contato("canal-outro", "contato-fake-1") == ()


# 8. Idempotência: chave opaca recebida pronta


def test_chave_nao_processada_depois_marcada() -> None:
    persistencia = PersistenciaEmMemoria()

    assert persistencia.chave_processada("chave-opaca-1") is False

    persistencia.marcar_chave_processada("chave-opaca-1")

    assert persistencia.chave_processada("chave-opaca-1") is True


def test_chaves_distintas_nao_colidem() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.marcar_chave_processada("chave-opaca-1")

    assert persistencia.chave_processada("chave-opaca-2") is False
    assert persistencia.chave_processada("chave-opaca-1 ") is False


# 9. Processamento pendente: preservado e recuperado sem interpretação


def test_pendente_preservado_e_recuperado_verbatim() -> None:
    persistencia = PersistenciaEmMemoria()
    pendente = ProcessamentoPendente(
        canal="canal-teste",
        contato="contato-fake-1",
        conteudo="conteudo opaco {não interpretado} 123",
    )

    persistencia.preservar_pendente(pendente)

    assert persistencia.recuperar_pendentes() == (pendente,)


def test_varios_pendentes_preservados_na_ordem() -> None:
    persistencia = PersistenciaEmMemoria()
    primeiro = ProcessamentoPendente("canal-teste", "contato-fake-1", "conteudo-1")
    segundo = ProcessamentoPendente("canal-teste", "contato-fake-2", "conteudo-2")

    persistencia.preservar_pendente(primeiro)
    persistencia.preservar_pendente(segundo)

    assert persistencia.recuperar_pendentes() == (primeiro, segundo)


# 10. Falha de gravação simulada: explícita e distinta de NÃO ENCONTRADO


def test_falha_simulada_de_criacao_e_explicita_e_nao_grava() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(FalhaDePersistencia):
        persistencia.criar(registro_ficticio())

    persistencia.simular_falha_de_gravacao = False
    assert (
        persistencia.recuperar_por_id(
            "atendimento-fake-1", "canal-teste", "contato-fake-1"
        ).resultado
        is ResultadoRecuperacao.NAO_ENCONTRADO
    )


def test_falha_simulada_de_gravacao_nao_altera_o_registro_existente() -> None:
    persistencia = PersistenciaEmMemoria()
    original = registro_ficticio()
    persistencia.criar(original)
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(FalhaDePersistencia):
        persistencia.gravar(
            RegistroAtendimento(
                id_atendimento="atendimento-fake-1",
                canal="canal-teste",
                contato="contato-fake-1",
                estado_conversa="estado-que-nao-deve-entrar",
            )
        )

    persistencia.simular_falha_de_gravacao = False
    assert (
        persistencia.recuperar_por_id(
            "atendimento-fake-1", "canal-teste", "contato-fake-1"
        ).registro
        == original
    )


def test_falha_de_persistencia_nao_e_confundida_com_nao_encontrado() -> None:
    """Falha é exceção própria; ausência é veredito de consulta."""
    assert issubclass(FalhaDePersistencia, Exception)
    assert not isinstance(
        RecuperacaoPorId(resultado=ResultadoRecuperacao.NAO_ENCONTRADO),
        Exception,
    )


def test_mecanismo_de_pendentes_segue_disponivel_na_falha_especifica_de_gravacao() -> None:
    """A simulação cobre somente criar/gravar; o mecanismo separado de
    pendentes continua operando nessa falha específica. Nada aqui afirma
    que uma indisponibilidade total preserva dados."""
    persistencia = PersistenciaEmMemoria()
    persistencia.simular_falha_de_gravacao = True
    pendente = ProcessamentoPendente("canal-teste", "contato-fake-1", "conteudo-1")

    persistencia.preservar_pendente(pendente)

    assert persistencia.recuperar_pendentes() == (pendente,)


# 11. Consulta não cria estado


def test_consultas_nao_criam_estado() -> None:
    persistencia = PersistenciaEmMemoria()

    persistencia.recuperar_por_id(
        "atendimento-inexistente", "canal-teste", "contato-fake-1"
    )
    persistencia.consultar_por_contato("canal-teste", "contato-fake-1")
    persistencia.chave_processada("chave-opaca-1")
    persistencia.recuperar_pendentes()

    assert persistencia.consultar_por_contato("canal-teste", "contato-fake-1") == ()
    assert persistencia.chave_processada("chave-opaca-1") is False
    assert persistencia.recuperar_pendentes() == ()


# 12. Sem rede, banco, SQLite, filesystem persistente ou LLM


def test_persistencia_sem_import_de_rede_banco_arquivo_ou_llm() -> None:
    permitidos = {
        "__future__",
        "abc",
        "copy",
        "dataclasses",
        "datetime",
        "enum",
        "typing",
    }
    proibidos = {
        "sqlite3",
        "dbm",
        "shelve",
        "pickle",
        "json",
        "os",
        "io",
        "pathlib",
        "shutil",
        "tempfile",
        "http",
        "urllib",
        "socket",
        "requests",
        "anthropic",
        "openai",
    }

    arvore = ast.parse(MODULO_PERSISTENCIA.read_text(encoding="utf-8"))
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module.split(".")[0])

    assert importados <= permitidos
    assert not (importados & proibidos)


# 13. Estruturas retornadas não permitem mutação silenciosa do estado interno


def test_mutacao_do_registro_recuperado_nao_altera_o_estado_interno() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio())

    recuperado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    ).registro
    assert recuperado is not None
    recuperado.dados_coletados["campo-artificial"] = "valor-adulterado"

    intacto = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    ).registro
    assert intacto is not None
    assert intacto.dados_coletados == {"campo-artificial": "valor-artificial"}


def test_mutacao_do_registro_de_entrada_nao_altera_o_estado_interno() -> None:
    persistencia = PersistenciaEmMemoria()
    registro = registro_ficticio()
    persistencia.criar(registro)

    registro.dados_coletados["campo-artificial"] = "valor-adulterado"

    armazenado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    ).registro
    assert armazenado is not None
    assert armazenado.dados_coletados == {"campo-artificial": "valor-artificial"}


# 14. Marco temporal `instante_ultima_transicao` — transporte e representação

INSTANTE_COM_FUSO = datetime(2000, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
INSTANTE_OUTRO_FUSO = datetime(
    2000, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=-3))
)
INSTANTE_NAIVE = datetime(2000, 1, 2, 3, 4, 5)


class _FusoSemDeslocamento(tzinfo):
    """`tzinfo` preenchido cujo `utcoffset()` devolve `None`.

    Instante assim não é comparável como instante absoluto, que é
    exatamente o que N-a-T8 exige do marco.
    """

    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        return None

    def tzname(self, dt: datetime | None) -> str | None:
        return "sem-deslocamento"

    def dst(self, dt: datetime | None) -> timedelta | None:
        return None


def test_marco_temporal_tem_default_none_e_e_aceito() -> None:
    persistencia = PersistenciaEmMemoria()
    registro = registro_ficticio()

    assert registro.instante_ultima_transicao is None

    persistencia.criar(registro)
    recuperado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )

    assert recuperado.registro is not None
    assert recuperado.registro.instante_ultima_transicao is None


def test_marco_com_fuso_efetivo_sobrevive_a_criar_e_recuperar() -> None:
    persistencia = PersistenciaEmMemoria()
    registro = replace(
        registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
    )

    persistencia.criar(registro)
    recuperado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )

    assert recuperado.registro is not None
    assert recuperado.registro.instante_ultima_transicao == INSTANTE_COM_FUSO


def test_marco_nao_e_convertido_para_utc_pela_persistencia() -> None:
    persistencia = PersistenciaEmMemoria()
    registro = replace(
        registro_ficticio(), instante_ultima_transicao=INSTANTE_OUTRO_FUSO
    )

    persistencia.criar(registro)
    recuperado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )

    assert recuperado.registro is not None
    devolvido = recuperado.registro.instante_ultima_transicao
    assert devolvido is not None
    assert devolvido.utcoffset() == timedelta(hours=-3)
    assert devolvido.tzinfo == INSTANTE_OUTRO_FUSO.tzinfo


def test_marco_sobrevive_a_consulta_por_contato() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(
        replace(
            registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
        )
    )

    encontrados = persistencia.consultar_por_contato(
        "canal-teste", "contato-fake-1"
    )

    assert len(encontrados) == 1
    assert encontrados[0].instante_ultima_transicao == INSTANTE_COM_FUSO


def test_gravar_substitui_o_marco_pelo_valor_recebido() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio())

    persistencia.gravar(
        replace(
            registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
        )
    )
    apos_preencher = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )
    assert apos_preencher.registro is not None
    assert (
        apos_preencher.registro.instante_ultima_transicao == INSTANTE_COM_FUSO
    )

    persistencia.gravar(registro_ficticio())
    apos_limpar = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )
    assert apos_limpar.registro is not None
    assert apos_limpar.registro.instante_ultima_transicao is None


def test_persistencia_nunca_preenche_o_marco_sozinha() -> None:
    """Sem valor do chamador, nada é criado — N-a-T3–N-a-T7 são da etapa 13."""
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(registro_ficticio())
    persistencia.gravar(
        replace(registro_ficticio(), estado_conversa="estado-opaco-b")
    )

    recuperado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )

    assert recuperado.registro is not None
    assert recuperado.registro.estado_conversa == "estado-opaco-b"
    assert recuperado.registro.instante_ultima_transicao is None


@pytest.mark.parametrize(
    "valor",
    [
        INSTANTE_NAIVE,
        datetime(2000, 1, 2, 3, 4, 5, tzinfo=_FusoSemDeslocamento()),
        "2000-01-02T03:04:05+00:00",
        946782245,
    ],
)
def test_marco_com_representacao_invalida_e_rejeitado_em_criar(
    valor: object,
) -> None:
    persistencia = PersistenciaEmMemoria()
    registro = replace(registro_ficticio(), instante_ultima_transicao=valor)

    with pytest.raises(ValueError) as erro:
        persistencia.criar(registro)

    assert "instante_ultima_transicao" in str(erro.value)
    assert persistencia.consultar_por_contato(
        "canal-teste", "contato-fake-1"
    ) == ()


@pytest.mark.parametrize(
    "valor",
    [
        INSTANTE_NAIVE,
        datetime(2000, 1, 2, 3, 4, 5, tzinfo=_FusoSemDeslocamento()),
        "2000-01-02T03:04:05+00:00",
    ],
)
def test_gravacao_com_marco_invalido_nao_corrompe_o_registro_anterior(
    valor: object,
) -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(
        replace(
            registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
        )
    )

    with pytest.raises(ValueError):
        persistencia.gravar(
            replace(
                registro_ficticio(),
                estado_conversa="estado-opaco-b",
                instante_ultima_transicao=valor,
            )
        )

    preservado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )
    assert preservado.registro is not None
    assert preservado.registro.estado_conversa == "estado-opaco-a"
    assert preservado.registro.instante_ultima_transicao == INSTANTE_COM_FUSO


def test_mensagem_de_marco_invalido_nao_expoe_id_contato_nem_conteudo() -> None:
    persistencia = PersistenciaEmMemoria()
    registro = replace(
        registro_ficticio(), instante_ultima_transicao=INSTANTE_NAIVE
    )

    with pytest.raises(ValueError) as erro:
        persistencia.criar(registro)

    mensagem = str(erro.value)
    assert "atendimento-fake-1" not in mensagem
    assert "contato-fake-1" not in mensagem
    assert "valor-artificial" not in mensagem
    assert "pergunta-artificial-1" not in mensagem


def test_vinculo_continua_imutavel_com_marco_presente() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(
        replace(
            registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
        )
    )

    with pytest.raises(ValueError):
        persistencia.gravar(
            replace(
                registro_ficticio(),
                contato="contato-fake-2",
                instante_ultima_transicao=INSTANTE_COM_FUSO,
            )
        )

    preservado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )
    assert preservado.registro is not None
    assert preservado.registro.contato == "contato-fake-1"
    assert preservado.registro.instante_ultima_transicao == INSTANTE_COM_FUSO


def test_copia_defensiva_preservada_com_marco_presente() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(
        replace(
            registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
        )
    )

    recuperado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )
    assert recuperado.registro is not None
    recuperado.registro.dados_coletados["campo-artificial"] = "mutado"

    novamente = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )
    assert novamente.registro is not None
    assert (
        novamente.registro.dados_coletados["campo-artificial"]
        == "valor-artificial"
    )
    assert novamente.registro.instante_ultima_transicao == INSTANTE_COM_FUSO


def test_idempotencia_e_pendentes_intactos_com_marco_presente() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(
        replace(
            registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
        )
    )

    assert persistencia.chave_processada("chave-artificial-1") is False
    persistencia.marcar_chave_processada("chave-artificial-1")
    assert persistencia.chave_processada("chave-artificial-1") is True

    pendente = ProcessamentoPendente(
        canal="canal-teste",
        contato="contato-fake-1",
        conteudo="conteudo-artificial",
    )
    persistencia.preservar_pendente(pendente)
    assert persistencia.recuperar_pendentes() == (pendente,)


def test_persistencia_nao_consulta_relogio_vivo() -> None:
    """Nenhuma chamada a relógio: a mesma entrada persiste igual sempre."""
    proibidos = {
        "now",
        "utcnow",
        "today",
        "fromtimestamp",
        "time",
        "monotonic",
        "perf_counter",
    }

    arvore = ast.parse(MODULO_PERSISTENCIA.read_text(encoding="utf-8"))
    chamados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call):
            alvo = no.func
            if isinstance(alvo, ast.Attribute):
                chamados.add(alvo.attr)
            elif isinstance(alvo, ast.Name):
                chamados.add(alvo.id)

    assert not (chamados & proibidos)


def test_mesma_entrada_persiste_igual_independente_do_relogio() -> None:
    primeira = PersistenciaEmMemoria()
    segunda = PersistenciaEmMemoria()
    registro = replace(
        registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
    )

    primeira.criar(registro)
    segunda.criar(registro)

    assert primeira.consultar_por_contato(
        "canal-teste", "contato-fake-1"
    ) == segunda.consultar_por_contato("canal-teste", "contato-fake-1")


# 15. Precedência: erro de contrato antes de falha de infraestrutura simulada

def test_marco_invalido_em_criar_precede_a_falha_simulada() -> None:
    """Representação inválida é erro do chamador (M-T3), não indisponibilidade."""
    persistencia = PersistenciaEmMemoria()
    persistencia.simular_falha_de_gravacao = True
    registro = replace(
        registro_ficticio(), instante_ultima_transicao=INSTANTE_NAIVE
    )

    with pytest.raises(ValueError) as erro:
        persistencia.criar(registro)

    assert not isinstance(erro.value, FalhaDePersistencia)
    assert "instante_ultima_transicao" in str(erro.value)

    persistencia.simular_falha_de_gravacao = False
    assert persistencia.consultar_por_contato(
        "canal-teste", "contato-fake-1"
    ) == ()


def test_marco_invalido_em_gravar_precede_a_falha_simulada() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.criar(
        replace(
            registro_ficticio(), instante_ultima_transicao=INSTANTE_COM_FUSO
        )
    )
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(ValueError) as erro:
        persistencia.gravar(
            replace(
                registro_ficticio(),
                estado_conversa="estado-opaco-b",
                instante_ultima_transicao=INSTANTE_NAIVE,
            )
        )

    assert not isinstance(erro.value, FalhaDePersistencia)
    assert "instante_ultima_transicao" in str(erro.value)

    persistencia.simular_falha_de_gravacao = False
    preservado = persistencia.recuperar_por_id(
        "atendimento-fake-1", "canal-teste", "contato-fake-1"
    )
    assert preservado.registro is not None
    assert preservado.registro.estado_conversa == "estado-opaco-a"
    assert preservado.registro.instante_ultima_transicao == INSTANTE_COM_FUSO


def test_registro_valido_com_simulacao_ativa_ainda_e_falha_de_persistencia() -> None:
    """A precedência não engole a falha simulada: registro válido continua falhando."""
    persistencia = PersistenciaEmMemoria()
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(FalhaDePersistencia):
        persistencia.criar(
            replace(
                registro_ficticio(),
                instante_ultima_transicao=INSTANTE_COM_FUSO,
            )
        )

    persistencia.simular_falha_de_gravacao = False
    persistencia.criar(registro_ficticio())
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(FalhaDePersistencia):
        persistencia.gravar(
            replace(
                registro_ficticio(),
                instante_ultima_transicao=INSTANTE_COM_FUSO,
            )
        )


def test_registro_sem_marco_com_simulacao_ativa_continua_falha_simulada() -> None:
    persistencia = PersistenciaEmMemoria()
    persistencia.simular_falha_de_gravacao = True

    with pytest.raises(FalhaDePersistencia):
        persistencia.criar(registro_ficticio())
