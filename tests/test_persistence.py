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
    permitidos = {"__future__", "abc", "copy", "dataclasses", "enum", "typing"}
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
