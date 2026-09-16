"""Testes do adaptador Anthropic do produtor da etapa 4 — **offline**.

O módulo real `src/casa77_sdr/interpretation_anthropic.py` é **importado e
exercitado**: o SDK está instalado, mas **nenhuma chamada real é feita**.

A ausência de rede não é convenção aqui — é **prova**. Uma **guarda de socket**
levanta exceção em qualquer tentativa de conexão durante **todos** os testes
deste módulo, e um teste dedicado comprova que a guarda dispara. Nenhum teste lê
`ANTHROPIC_API_KEY`, variável de credencial, `.env`, `knowledge/**` ou YAML.

O cliente do SDK é **injetado** como duplo com a mesma assinatura. Os tipos do
SDK aparecem **somente** onde a fronteira precisa deles — as exceções
construídas localmente para provar o mapeamento de falhas —, e **nenhum** deles
atravessa o `Protocol` do produtor.

Todas as fixtures são fictícias e genéricas: zero PII, zero conversa real, zero
valor comercial, zero segredo.
"""

from __future__ import annotations

import ast
import json
import socket
from pathlib import Path
from typing import Any

import anthropic
import httpx2
import pytest

from casa77_sdr import interpretation_anthropic
from casa77_sdr.interpretation_anthropic import AdaptadorAnthropic
from casa77_sdr.interpretation_llm import (
    FalhaProdutorInterpretacao,
    MotivoFalhaProdutor,
    ProdutorTextoEstruturado,
    gerar_schema_interpretacao,
    interpretar_mensagem,
)

MODULO_ADAPTADOR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "casa77_sdr"
    / "interpretation_anthropic.py"
)
MODULO_PRODUTOR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "casa77_sdr"
    / "interpretation_llm.py"
)

MODELO = "claude-sonnet-5"
MAX_TOKENS = 4096
TIMEOUT = 30.0
PROMPT = "prompt de sistema fictício"
MENSAGEM = "mensagem fictícia do interessado"


class RedeProibidaNoTeste(RuntimeError):
    """Levantada pela guarda de socket. Nenhum teste pode abrir conexão."""


@pytest.fixture(autouse=True)
def guarda_de_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    """Guarda de socket ativa em **todos** os testes deste módulo."""

    def proibir(*_: Any, **__: Any) -> None:
        raise RedeProibidaNoTeste("tentativa de conexão de rede num teste offline")

    monkeypatch.setattr(socket, "socket", proibir)
    monkeypatch.setattr(socket, "create_connection", proibir)
    monkeypatch.setattr(socket, "getaddrinfo", proibir)


# --------------------------------------------------------------------------
# Duplos do SDK
# --------------------------------------------------------------------------


class BlocoTexto:
    type = "text"

    def __init__(self, text: str) -> None:
        self.text = text


class BlocoNaoTexto:
    def __init__(self, tipo: str = "thinking") -> None:
        self.type = tipo
        self.thinking = "conteúdo que o adaptador jamais deve inspecionar"


class RespostaFalsa:
    def __init__(self, stop_reason: Any, content: list[Any]) -> None:
        self.stop_reason = stop_reason
        self.content = content


class MessagesFalso:
    def __init__(self, resultado: Any) -> None:
        self._resultado = resultado
        self.chamadas: list[dict[str, Any]] = []

    def create(self, **argumentos: Any) -> Any:
        self.chamadas.append(argumentos)
        if isinstance(self._resultado, BaseException):
            raise self._resultado
        return self._resultado


class ClienteFalso:
    """Duplo do cliente Anthropic, com a mesma superfície usada pelo adaptador."""

    def __init__(self, resultado: Any) -> None:
        self.messages = MessagesFalso(resultado)
        self.opcoes: list[dict[str, Any]] = []

    def with_options(self, **argumentos: Any) -> ClienteFalso:
        self.opcoes.append(argumentos)
        return self


def requisicao() -> httpx2.Request:
    return httpx2.Request("POST", "https://exemplo.invalido/v1/messages")


def resposta_http(status: int) -> httpx2.Response:
    return httpx2.Response(status, request=requisicao())


def adaptador(resultado: Any) -> tuple[AdaptadorAnthropic, ClienteFalso]:
    cliente = ClienteFalso(resultado)
    return (
        AdaptadorAnthropic(
            cliente, model=MODELO, max_tokens=MAX_TOKENS, timeout=TIMEOUT
        ),
        cliente,
    )


def resposta_ok(texto: str) -> RespostaFalsa:
    return RespostaFalsa("end_turn", [BlocoTexto(texto)])


def produzir(resultado: Any) -> str:
    alvo, _ = adaptador(resultado)
    return alvo.produzir(
        prompt_sistema=PROMPT,
        mensagem=MENSAGEM,
        schema=gerar_schema_interpretacao(),
    )


def motivo_de(resultado: Any) -> MotivoFalhaProdutor:
    with pytest.raises(FalhaProdutorInterpretacao) as excecao:
        produzir(resultado)
    return excecao.value.motivo


def payload_minimo() -> dict[str, Any]:
    campos = ("tipo_evento", "data_nomeada", "convidados", "formato", "nome", "contato")
    ausente = {"presente": False, "valor": "alta"}
    dados: dict[str, Any] = {}
    for campo in campos:
        dados[campo] = None
        dados[f"confianca_{campo}"] = dict(ausente)
    return {
        "dados_extraidos": dados,
        "correcoes": [],
        "perguntas_comerciais": [],
        "pedido_de_humano": False,
        "confianca_pedido_de_humano": dict(ausente),
        "referencias_evento_anterior": [],
        "trechos_ambiguos": [],
        "confianca_global": {"presente": True, "valor": "alta"},
        "intencoes_autonomas": [],
    }


# --------------------------------------------------------------------------
# A guarda de socket é real
# --------------------------------------------------------------------------


def codigo_efetivo(caminho: Path) -> str:
    """Código do módulo **sem** docstring e **sem** comentário.

    As provas de ausência precisam incidir sobre o que o módulo **faz**, não
    sobre o que ele **descreve**: a prosa cita `knowledge/**` justamente para
    declarar que não o lê.
    """
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    for no in list(ast.walk(arvore)):
        corpo = getattr(no, "body", None)
        if not isinstance(corpo, list) or not corpo:
            continue
        if not isinstance(
            no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        primeiro = corpo[0]
        if (
            isinstance(primeiro, ast.Expr)
            and isinstance(primeiro.value, ast.Constant)
            and isinstance(primeiro.value.value, str)
        ):
            corpo.pop(0)
    return ast.unparse(arvore)


def test_a_guarda_de_socket_dispara_em_qualquer_conexao() -> None:
    with pytest.raises(RedeProibidaNoTeste):
        socket.socket()
    with pytest.raises(RedeProibidaNoTeste):
        socket.create_connection(("exemplo.invalido", 443))
    with pytest.raises(RedeProibidaNoTeste):
        socket.getaddrinfo("exemplo.invalido", 443)


def test_nenhuma_credencial_e_lida_pelo_adaptador() -> None:
    codigo = codigo_efetivo(MODULO_ADAPTADOR)
    for proibido in ("ANTHROPIC_API_KEY", "api_key", "getenv", "environ", ".env"):
        assert proibido not in codigo, proibido


# --------------------------------------------------------------------------
# Montagem da chamada
# --------------------------------------------------------------------------


def test_a_chamada_repassa_model_max_tokens_system_e_turno_unico() -> None:
    alvo, cliente = adaptador(resposta_ok("{}"))
    alvo.produzir(
        prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=gerar_schema_interpretacao()
    )
    argumentos = cliente.messages.chamadas[0]
    assert argumentos["model"] == MODELO
    assert argumentos["max_tokens"] == MAX_TOKENS
    assert argumentos["system"] == PROMPT
    assert argumentos["messages"] == [{"role": "user", "content": MENSAGEM}]
    assert len(argumentos["messages"]) == 1


def test_output_config_format_esta_presente_e_com_a_forma_exigida() -> None:
    schema = gerar_schema_interpretacao()
    alvo, cliente = adaptador(resposta_ok("{}"))
    alvo.produzir(prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=schema)
    formato = cliente.messages.chamadas[0]["output_config"]["format"]
    assert formato["type"] == "json_schema"
    assert formato["schema"] is schema


def test_thinking_vai_explicitamente_desabilitado() -> None:
    alvo, cliente = adaptador(resposta_ok("{}"))
    alvo.produzir(
        prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=gerar_schema_interpretacao()
    )
    assert cliente.messages.chamadas[0]["thinking"] == {"type": "disabled"}


def test_retry_do_sdk_e_desligado_e_o_timeout_e_repassado() -> None:
    alvo, cliente = adaptador(resposta_ok("{}"))
    alvo.produzir(
        prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=gerar_schema_interpretacao()
    )
    assert cliente.opcoes == [{"max_retries": 0, "timeout": TIMEOUT}]


def test_a_chamada_nao_carrega_amostragem_tools_streaming_nem_historico() -> None:
    alvo, cliente = adaptador(resposta_ok("{}"))
    alvo.produzir(
        prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=gerar_schema_interpretacao()
    )
    argumentos = cliente.messages.chamadas[0]
    for proibido in (
        "temperature",
        "top_p",
        "top_k",
        "tools",
        "tool_choice",
        "stream",
        "citations",
        "cache_control",
        "betas",
        "effort",
    ):
        assert proibido not in argumentos, proibido
    assert set(argumentos) == {
        "model",
        "max_tokens",
        "thinking",
        "system",
        "messages",
        "output_config",
    }
    assert all(item["role"] == "user" for item in argumentos["messages"])


def test_montar_argumentos_nao_executa_chamada() -> None:
    alvo, cliente = adaptador(resposta_ok("{}"))
    argumentos = alvo.montar_argumentos(
        prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=gerar_schema_interpretacao()
    )
    assert cliente.messages.chamadas == []
    assert cliente.opcoes == []
    assert argumentos["model"] == MODELO


def test_a_chamada_e_feita_uma_unica_vez() -> None:
    alvo, cliente = adaptador(resposta_ok("{}"))
    alvo.produzir(
        prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=gerar_schema_interpretacao()
    )
    assert len(cliente.messages.chamadas) == 1


@pytest.mark.parametrize(
    ("model", "max_tokens", "timeout"),
    [
        ("", 10, 1.0),
        ("   ", 10, 1.0),
        (MODELO, 0, 1.0),
        (MODELO, -1, 1.0),
        (MODELO, 10, 0),
        (MODELO, 10, -1.0),
    ],
)
def test_parametros_operacionais_sao_validados(
    model: str, max_tokens: int, timeout: float
) -> None:
    with pytest.raises(ValueError):
        AdaptadorAnthropic(
            ClienteFalso(None), model=model, max_tokens=max_tokens, timeout=timeout
        )


@pytest.mark.parametrize(
    ("max_tokens", "timeout"), [(True, 1.0), ("10", 1.0), (10, True), (10, "1")]
)
def test_tipo_incompativel_nos_parametros_operacionais_e_type_error(
    max_tokens: Any, timeout: Any
) -> None:
    with pytest.raises(TypeError):
        AdaptadorAnthropic(
            ClienteFalso(None), model=MODELO, max_tokens=max_tokens, timeout=timeout
        )


def test_o_dominio_nao_contem_modelo_timeout_nem_max_tokens() -> None:
    # `claude-sonnet-5` aparece só na prosa do módulo, nunca como valor padrão.
    arvore = ast.parse(MODULO_ADAPTADOR.read_text(encoding="utf-8"))
    literais = {
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    }
    assert "claude-sonnet-5" not in literais
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == "__init__":
            assert no.args.kw_defaults == [None, None, None]


# --------------------------------------------------------------------------
# `stop_reason` primeiro, conteúdo depois
# --------------------------------------------------------------------------


def test_recusa_falha_fechada_sem_ler_conteudo() -> None:
    resposta = RespostaFalsa("refusal", [BlocoTexto('{"parcial": true}')])
    assert motivo_de(resposta) is MotivoFalhaProdutor.RECUSA_DO_MODELO


def test_truncamento_falha_fechado_e_nao_aproveita_payload_parcial() -> None:
    resposta = RespostaFalsa("max_tokens", [BlocoTexto('{"dados_extraidos":')])
    assert motivo_de(resposta) is MotivoFalhaProdutor.TRUNCADO


@pytest.mark.parametrize(
    "stop_reason", ["tool_use", "pause_turn", "desconhecido", None, ""]
)
def test_stop_reason_inesperado_falha_fechado(stop_reason: Any) -> None:
    resposta = RespostaFalsa(stop_reason, [BlocoTexto("{}")])
    assert motivo_de(resposta) is MotivoFalhaProdutor.ERRO_DO_PROVEDOR


@pytest.mark.parametrize("stop_reason", ["end_turn", "stop_sequence"])
def test_stop_reason_conclusivo_segue_para_o_conteudo(stop_reason: str) -> None:
    resposta = RespostaFalsa(stop_reason, [BlocoTexto("{}")])
    assert produzir(resposta) == "{}"


# --------------------------------------------------------------------------
# Seleção do bloco de texto
# --------------------------------------------------------------------------


def test_zero_bloco_de_texto_falha_fechado() -> None:
    resposta = RespostaFalsa("end_turn", [BlocoNaoTexto()])
    assert motivo_de(resposta) is MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO


def test_conteudo_vazio_falha_fechado() -> None:
    assert (
        motivo_de(RespostaFalsa("end_turn", []))
        is MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO
    )


def test_multiplos_blocos_de_texto_nunca_sao_concatenados() -> None:
    resposta = RespostaFalsa("end_turn", [BlocoTexto('{"a":1}'), BlocoTexto('{"b":2}')])
    assert motivo_de(resposta) is MotivoFalhaProdutor.MULTIPLOS_BLOCOS_ESTRUTURADOS


def test_bloco_nao_texto_antes_do_texto_e_ignorado_para_selecao() -> None:
    """O adaptador **nunca** acessa `content[0]`."""
    resposta = RespostaFalsa(
        "end_turn",
        [BlocoNaoTexto("thinking"), BlocoNaoTexto("redacted_thinking"), BlocoTexto("{}")],
    )
    assert produzir(resposta) == "{}"


def test_o_adaptador_nunca_indexa_o_primeiro_bloco() -> None:
    codigo = codigo_efetivo(MODULO_ADAPTADOR)
    assert "content[0]" not in codigo
    assert "conteudo[0]" not in codigo


def test_bloco_de_texto_sem_texto_utilizavel_falha_fechado() -> None:
    class BlocoQuebrado:
        type = "text"
        text = None

    resposta = RespostaFalsa("end_turn", [BlocoQuebrado()])
    assert motivo_de(resposta) is MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO


def test_conteudo_de_tipo_inesperado_falha_fechado() -> None:
    resposta = RespostaFalsa("end_turn", "{}")
    assert motivo_de(resposta) is MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO


# --------------------------------------------------------------------------
# Exceções do SDK
# --------------------------------------------------------------------------


def test_timeout_do_sdk_vira_timeout() -> None:
    erro = anthropic.APITimeoutError(request=requisicao())
    assert motivo_de(erro) is MotivoFalhaProdutor.TIMEOUT


def test_erro_de_conexao_do_sdk_vira_erro_de_transporte() -> None:
    erro = anthropic.APIConnectionError(message="falhou", request=requisicao())
    assert motivo_de(erro) is MotivoFalhaProdutor.ERRO_DE_TRANSPORTE


@pytest.mark.parametrize("status", [400, 401, 429, 500, 529])
def test_status_de_erro_do_provedor_vira_erro_do_provedor(status: int) -> None:
    erro = anthropic.APIStatusError(
        "erro", response=resposta_http(status), body=None
    )
    assert motivo_de(erro) is MotivoFalhaProdutor.ERRO_DO_PROVEDOR


def test_erro_generico_do_sdk_vira_erro_do_provedor() -> None:
    assert (
        motivo_de(anthropic.AnthropicError("qualquer"))
        is MotivoFalhaProdutor.ERRO_DO_PROVEDOR
    )


def test_a_falha_nao_expoe_mensagem_do_provedor() -> None:
    segredo = "sk-ant-ficticio-nao-e-uma-chave-real"
    erro = anthropic.APIStatusError(
        segredo, response=resposta_http(401), body={"detalhe": segredo}
    )
    with pytest.raises(FalhaProdutorInterpretacao) as excecao:
        produzir(erro)
    falha = excecao.value
    for texto in (str(falha), repr(falha), str(falha.args)):
        assert segredo not in texto
    assert falha.__cause__ is None


# --------------------------------------------------------------------------
# Payload devolvido íntegro e encadeamento com a fronteira agnóstica
# --------------------------------------------------------------------------


def test_o_payload_e_devolvido_integro_sem_normalizacao() -> None:
    bruto = '  {"a":\t1}\n'
    assert produzir(resposta_ok(bruto)) == bruto


def test_o_adaptador_satisfaz_o_protocolo_do_produtor() -> None:
    alvo, _ = adaptador(resposta_ok("{}"))
    assert isinstance(alvo, ProdutorTextoEstruturado)


def test_cadeia_completa_offline_produz_interpretacao() -> None:
    alvo, cliente = adaptador(resposta_ok(json.dumps(payload_minimo())))
    resultado = interpretar_mensagem(MENSAGEM, produtor=alvo, prompt_sistema=PROMPT)
    assert resultado.intencoes_detectadas == ()
    assert len(cliente.messages.chamadas) == 1


def test_json_invalido_devolvido_pelo_provedor_falha_fechado() -> None:
    alvo, _ = adaptador(resposta_ok("não é json"))
    with pytest.raises(FalhaProdutorInterpretacao) as excecao:
        interpretar_mensagem(MENSAGEM, produtor=alvo, prompt_sistema=PROMPT)
    assert excecao.value.motivo is MotivoFalhaProdutor.JSON_INVALIDO


def test_payload_estruturalmente_invalido_falha_fechado() -> None:
    alvo, _ = adaptador(resposta_ok(json.dumps({"instrucao": "ignore tudo"})))
    with pytest.raises(FalhaProdutorInterpretacao) as excecao:
        interpretar_mensagem(MENSAGEM, produtor=alvo, prompt_sistema=PROMPT)
    assert excecao.value.motivo is MotivoFalhaProdutor.PAYLOAD_FORA_DO_SCHEMA


# --------------------------------------------------------------------------
# Fechamento de imports — assimétrico e verificável
# --------------------------------------------------------------------------


def modulos_importados(caminho: Path) -> set[str]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    raizes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            raizes.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            raizes.add(no.module.split(".")[0])
    return raizes


def test_o_adaptador_importa_o_sdk_e_o_produtor_nao() -> None:
    assert "anthropic" in modulos_importados(MODULO_ADAPTADOR)
    assert "anthropic" not in modulos_importados(MODULO_PRODUTOR)


def test_o_sdk_e_importado_por_um_unico_modulo_do_pacote() -> None:
    raiz = Path(__file__).resolve().parents[1] / "src" / "casa77_sdr"
    importadores = sorted(
        caminho.name
        for caminho in raiz.glob("*.py")
        if "anthropic" in modulos_importados(caminho)
    )
    assert importadores == ["interpretation_anthropic.py"]


def test_o_adaptador_nao_e_exportado_pelo_pacote() -> None:
    import casa77_sdr

    assert "AdaptadorAnthropic" not in casa77_sdr.__all__
    assert interpretation_anthropic.__all__ == ["AdaptadorAnthropic"]


def test_o_adaptador_nao_conhece_interpretacao_nem_knowledge() -> None:
    codigo = codigo_efetivo(MODULO_ADAPTADOR)
    for proibido in (
        "canonicalizar_interpretacao",
        "EntradaInterpretacao",
        "DadosExtraidos",
        "PerguntaComercial",
        "AssuntoComercial",
        "knowledge",
        "yaml",
        "open(",
        "E-Nb-",
    ):
        assert proibido not in codigo, proibido

    # Do módulo agnóstico ele importa **somente** a família de falhas.
    arvore = ast.parse(MODULO_ADAPTADOR.read_text(encoding="utf-8"))
    importados = {
        alias.name
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom)
        and no.module == "casa77_sdr.interpretation_llm"
        for alias in no.names
    }
    assert importados == {"FalhaProdutorInterpretacao", "MotivoFalhaProdutor"}
