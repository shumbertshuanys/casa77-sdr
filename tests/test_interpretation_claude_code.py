"""Testes do adaptador Claude Code headless do produtor da etapa 4 — **offline**.

O módulo real `src/casa77_sdr/interpretation_claude_code.py` é importado e
exercitado com o executor de processo **injetado**: nenhum processo `claude` é
iniciado e nenhuma rede é tocada. Nenhum teste lê credencial; as variáveis de
credencial usadas aqui são valores fictícios postos pelo próprio teste.

Todas as fixtures são fictícias e genéricas: zero PII, zero conversa real, zero
valor comercial, zero segredo.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from casa77_sdr import interpretation_claude_code
from casa77_sdr.interpretation_claude_code import (
    AdaptadorClaudeCode,
    ExecutavelClaudeNaoEncontrado,
    resolver_executavel_claude,
    verificar_login_claude,
)
from casa77_sdr.interpretation_llm import (
    FalhaProdutorInterpretacao,
    MotivoFalhaProdutor,
    ProdutorTextoEstruturado,
    gerar_schema_interpretacao,
)

MODULO_ADAPTADOR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "casa77_sdr"
    / "interpretation_claude_code.py"
)

EXECUTAVEL = "/caminho/ficticio/claude"
MODELO = "sonnet"
TIMEOUT = 30.0
PROMPT = "prompt de sistema fictício"
MENSAGEM = "mensagem fictícia SEGREDO-DA-MENSAGEM com \"aspas\""
SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["eco"],
    "properties": {"eco": {"type": "string", "description": "aspas \"duplas\" & %x%"}},
}
SAIDA = {"eco": "ação"}
VAZAMENTO_STDOUT = "SEGREDO-DO-STDOUT"
VAZAMENTO_STDERR = "SEGREDO-DO-STDERR"


class _Executor:
    """Duplo de `subprocess.run`: registra a chamada e devolve/levanta o roteiro."""

    def __init__(
        self,
        *,
        stdout: Any = "",
        returncode: int = 0,
        erro: BaseException | None = None,
    ) -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.erro = erro
        self.chamadas: list[tuple[list[str], dict[str, Any]]] = []
        self.prompt_lido: str | None = None
        self.cwd_vazio: bool | None = None

    def __call__(self, argumentos: list[str], **opcoes: Any) -> Any:
        self.chamadas.append((list(argumentos), opcoes))
        if "--system-prompt-file" in argumentos:
            caminho = Path(argumentos[argumentos.index("--system-prompt-file") + 1])
            self.prompt_lido = caminho.read_text(encoding="utf-8")
        if opcoes.get("cwd") is not None:
            self.cwd_vazio = list(Path(opcoes["cwd"]).iterdir()) == []
        if self.erro is not None:
            raise self.erro
        return subprocess.CompletedProcess(
            argumentos, self.returncode, self.stdout, VAZAMENTO_STDERR
        )


def _envelope(**campos: Any) -> str:
    base: dict[str, Any] = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": VAZAMENTO_STDOUT,
        "structured_output": SAIDA,
        "num_turns": 2,
    }
    base.update(campos)
    return json.dumps(base)


def _adaptador(executor: _Executor) -> AdaptadorClaudeCode:
    return AdaptadorClaudeCode(
        executavel=EXECUTAVEL, model=MODELO, timeout=TIMEOUT, executar=executor
    )


def _produzir(adaptador: AdaptadorClaudeCode) -> str:
    return adaptador.produzir(prompt_sistema=PROMPT, mensagem=MENSAGEM, schema=SCHEMA)


def _falha_de(executor: _Executor) -> FalhaProdutorInterpretacao:
    with pytest.raises(FalhaProdutorInterpretacao) as capturada:
        _produzir(_adaptador(executor))
    falha = capturada.value
    for texto in (str(falha), repr(falha), *map(str, falha.args)):
        for segredo in (MENSAGEM, "SEGREDO-DA-MENSAGEM", VAZAMENTO_STDOUT, VAZAMENTO_STDERR, PROMPT):
            assert segredo not in texto
    assert falha.__cause__ is None
    assert falha.__context__ is None or falha.__suppress_context__ is True
    return falha


# --------------------------------------------------------------------------
# Sucesso e forma da chamada
# --------------------------------------------------------------------------


def test_sucesso_devolve_structured_output_como_texto_json() -> None:
    executor = _Executor(stdout=_envelope())
    texto = _produzir(_adaptador(executor))
    assert json.loads(texto) == SAIDA
    assert texto == json.dumps(SAIDA, ensure_ascii=False)
    assert VAZAMENTO_STDOUT not in texto


def test_e_um_produtor_texto_estruturado() -> None:
    adaptador: ProdutorTextoEstruturado = _adaptador(_Executor(stdout=_envelope()))
    assert isinstance(_produzir(adaptador), str)  # type: ignore[arg-type]


def test_mensagem_vai_somente_pelo_stdin() -> None:
    executor = _Executor(stdout=_envelope())
    _produzir(_adaptador(executor))
    [(argumentos, opcoes)] = executor.chamadas
    assert opcoes["input"] == MENSAGEM
    assert all("SEGREDO-DA-MENSAGEM" not in parte for parte in argumentos)
    assert all(PROMPT not in parte for parte in argumentos)


def test_json_schema_e_o_schema_compacto() -> None:
    executor = _Executor(stdout=_envelope())
    _produzir(_adaptador(executor))
    [(argumentos, _)] = executor.chamadas
    valor = argumentos[argumentos.index("--json-schema") + 1]
    assert valor == json.dumps(SCHEMA, ensure_ascii=False, separators=(",", ":"))
    assert json.loads(valor) == SCHEMA


def test_schema_real_da_interpretacao_cabe_compacto() -> None:
    schema = gerar_schema_interpretacao()
    adaptador = _adaptador(_Executor())
    argumentos = adaptador.montar_argumentos(caminho_prompt_sistema="p.md", schema=schema)
    valor = argumentos[argumentos.index("--json-schema") + 1]
    assert json.loads(valor) == schema
    assert valor == json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def test_linha_de_comando_isola_ferramentas_mcp_e_sessao() -> None:
    adaptador = _adaptador(_Executor())
    argumentos = adaptador.montar_argumentos(caminho_prompt_sistema="p.md", schema=SCHEMA)
    assert argumentos[0] == EXECUTAVEL
    assert argumentos[1] == "-p"
    assert argumentos[argumentos.index("--model") + 1] == MODELO
    assert argumentos[argumentos.index("--system-prompt-file") + 1] == "p.md"
    assert argumentos[argumentos.index("--tools") + 1] == ""
    assert argumentos[argumentos.index("--output-format") + 1] == "json"
    for bandeira in (
        "--strict-mcp-config",
        "--disable-slash-commands",
        "--no-session-persistence",
    ):
        assert bandeira in argumentos


def test_executavel_em_lista_e_prefixo_do_comando() -> None:
    adaptador = AdaptadorClaudeCode(
        executavel=["node", "/x/cli.js"], model=MODELO, timeout=TIMEOUT, executar=_Executor()
    )
    argumentos = adaptador.montar_argumentos(caminho_prompt_sistema="p.md", schema=SCHEMA)
    assert argumentos[:3] == ["node", "/x/cli.js", "-p"]


def test_prompt_vai_por_arquivo_temporario_e_cwd_e_vazio() -> None:
    executor = _Executor(stdout=_envelope())
    _produzir(_adaptador(executor))
    [(argumentos, opcoes)] = executor.chamadas
    assert executor.prompt_lido == PROMPT
    assert executor.cwd_vazio is True
    caminho_prompt = Path(argumentos[argumentos.index("--system-prompt-file") + 1])
    assert not caminho_prompt.exists()
    assert not Path(opcoes["cwd"]).exists()
    assert caminho_prompt.parent != Path(opcoes["cwd"])
    assert opcoes["timeout"] == TIMEOUT
    assert opcoes["capture_output"] is True
    assert opcoes["text"] is True
    assert opcoes["encoding"] == "utf-8"
    assert "shell" not in opcoes


def test_ambiente_sem_credencial_da_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "valor-ficticio")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "valor-ficticio")
    monkeypatch.setenv("VARIAVEL_FICTICIA_PRESERVADA", "1")
    executor = _Executor(stdout=_envelope())
    _produzir(_adaptador(executor))
    [(_, opcoes)] = executor.chamadas
    ambiente = opcoes["env"]
    assert "ANTHROPIC_API_KEY" not in ambiente
    assert "ANTHROPIC_AUTH_TOKEN" not in ambiente
    assert ambiente["VARIAVEL_FICTICIA_PRESERVADA"] == "1"
    assert os.environ["ANTHROPIC_API_KEY"] == "valor-ficticio"


# --------------------------------------------------------------------------
# Falhas
# --------------------------------------------------------------------------


def test_is_error_verdadeiro_e_erro_do_provedor() -> None:
    falha = _falha_de(_Executor(stdout=_envelope(is_error=True)))
    assert falha.motivo is MotivoFalhaProdutor.ERRO_DO_PROVEDOR


@pytest.mark.parametrize("valor", [None, 0, "false"])
def test_is_error_que_nao_e_falso_estrito_falha(valor: Any) -> None:
    falha = _falha_de(_Executor(stdout=_envelope(is_error=valor)))
    assert falha.motivo is MotivoFalhaProdutor.ERRO_DO_PROVEDOR


def test_subtype_diferente_de_success_falha() -> None:
    falha = _falha_de(_Executor(stdout=_envelope(subtype="error_max_turns")))
    assert falha.motivo is MotivoFalhaProdutor.ERRO_DO_PROVEDOR


def test_saida_nao_zero_e_erro_do_provedor() -> None:
    falha = _falha_de(_Executor(stdout=_envelope(), returncode=1))
    assert falha.motivo is MotivoFalhaProdutor.ERRO_DO_PROVEDOR


def test_timeout() -> None:
    erro = subprocess.TimeoutExpired(
        ["claude"], TIMEOUT, output=VAZAMENTO_STDOUT, stderr=VAZAMENTO_STDERR
    )
    falha = _falha_de(_Executor(erro=erro))
    assert falha.motivo is MotivoFalhaProdutor.TIMEOUT


def test_executavel_inexistente_e_erro_de_transporte() -> None:
    falha = _falha_de(_Executor(erro=FileNotFoundError(VAZAMENTO_STDERR)))
    assert falha.motivo is MotivoFalhaProdutor.ERRO_DE_TRANSPORTE


def test_saida_nao_decodificavel_e_json_invalido() -> None:
    erro = UnicodeDecodeError("utf-8", b"\xff", 0, 1, "byte inválido")
    falha = _falha_de(_Executor(erro=erro))
    assert falha.motivo is MotivoFalhaProdutor.JSON_INVALIDO


@pytest.mark.parametrize(
    "stdout", [VAZAMENTO_STDOUT, "", "[1, 2]", '"texto"', None]
)
def test_stdout_ilegivel_e_json_invalido(stdout: Any) -> None:
    falha = _falha_de(_Executor(stdout=stdout))
    assert falha.motivo is MotivoFalhaProdutor.JSON_INVALIDO


def test_structured_output_ausente() -> None:
    envelope = json.loads(_envelope())
    del envelope["structured_output"]
    falha = _falha_de(_Executor(stdout=json.dumps(envelope)))
    assert falha.motivo is MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO


@pytest.mark.parametrize("valor", [None, [SAIDA], VAZAMENTO_STDOUT, 1])
def test_structured_output_que_nao_e_objeto(valor: Any) -> None:
    falha = _falha_de(_Executor(stdout=_envelope(structured_output=valor)))
    assert falha.motivo is MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO


# --------------------------------------------------------------------------
# Validação do construtor
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("campos", "erro"),
    [
        ({"executavel": ""}, ValueError),
        ({"executavel": []}, ValueError),
        ({"executavel": ["claude", " "]}, ValueError),
        ({"executavel": 3}, TypeError),
        ({"model": ""}, ValueError),
        ({"model": None}, ValueError),
        ({"timeout": 0}, ValueError),
        ({"timeout": -1.0}, ValueError),
        ({"timeout": True}, TypeError),
        ({"timeout": "30"}, TypeError),
        ({"executar": None}, TypeError),
    ],
)
def test_construtor_valida(campos: dict[str, Any], erro: type[Exception]) -> None:
    argumentos: dict[str, Any] = {
        "executavel": EXECUTAVEL,
        "model": MODELO,
        "timeout": TIMEOUT,
        "executar": _Executor(),
    }
    argumentos.update(campos)
    with pytest.raises(erro):
        AdaptadorClaudeCode(**argumentos)


# --------------------------------------------------------------------------
# Resolução do executável
# --------------------------------------------------------------------------


def _localizador(mapa: dict[str, str | None]) -> Any:
    return lambda nome: mapa.get(nome)


def test_resolver_cli_ausente() -> None:
    with pytest.raises(ExecutavelClaudeNaoEncontrado):
        resolver_executavel_claude(localizar=_localizador({}))


def test_resolver_executavel_direto(tmp_path: Path) -> None:
    caminho = str(tmp_path / "claude")
    assert resolver_executavel_claude(localizar=_localizador({"claude": caminho})) == [caminho]


def test_resolver_shim_npm_prefere_executavel_nativo(tmp_path: Path) -> None:
    shim = tmp_path / "claude.CMD"
    shim.write_text("@ECHO off", encoding="utf-8")
    nativo = tmp_path / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
    nativo.parent.mkdir(parents=True)
    nativo.write_bytes(b"")
    resolvido = resolver_executavel_claude(localizar=_localizador({"claude": str(shim)}))
    assert resolvido == [str(nativo)]


def test_resolver_shim_npm_cai_para_node_cli_js(tmp_path: Path) -> None:
    shim = tmp_path / "claude.cmd"
    shim.write_text("@ECHO off", encoding="utf-8")
    cli_js = tmp_path / "node_modules" / "@anthropic-ai" / "claude-code" / "cli.js"
    cli_js.parent.mkdir(parents=True)
    cli_js.write_text("", encoding="utf-8")
    resolvido = resolver_executavel_claude(
        localizar=_localizador({"claude": str(shim), "node": "/x/node"})
    )
    assert resolvido == ["/x/node", str(cli_js)]


def test_resolver_shim_sem_alvo_nao_executa_cmd(tmp_path: Path) -> None:
    shim = tmp_path / "claude.cmd"
    shim.write_text("@ECHO off", encoding="utf-8")
    with pytest.raises(ExecutavelClaudeNaoEncontrado):
        resolver_executavel_claude(
            localizar=_localizador({"claude": str(shim), "node": "/x/node"})
        )


# --------------------------------------------------------------------------
# Preflight de login
# --------------------------------------------------------------------------


def test_login_verdadeiro() -> None:
    executor = _Executor(stdout=json.dumps({"loggedIn": True, "authMethod": "claude.ai"}))
    assert verificar_login_claude(["claude"], timeout=5.0, executar=executor) is True
    [(argumentos, opcoes)] = executor.chamadas
    assert argumentos == ["claude", "auth", "status"]
    assert "ANTHROPIC_API_KEY" not in opcoes["env"]
    assert opcoes["timeout"] == 5.0


@pytest.mark.parametrize(
    "executor",
    [
        _Executor(stdout=json.dumps({"loggedIn": False})),
        _Executor(stdout=json.dumps({"loggedIn": "true"})),
        _Executor(stdout=json.dumps({})),
        _Executor(stdout="[]"),
        _Executor(stdout="não é json"),
        _Executor(stdout=json.dumps({"loggedIn": True}), returncode=1),
        _Executor(erro=FileNotFoundError("x")),
        _Executor(erro=subprocess.TimeoutExpired(["claude"], 5.0)),
    ],
)
def test_login_ausente_ou_ilegivel(executor: _Executor) -> None:
    assert verificar_login_claude(["claude"], timeout=5.0, executar=executor) is False


# --------------------------------------------------------------------------
# Estrutura
# --------------------------------------------------------------------------


def test_o_adaptador_nao_importa_sdk_nem_conhece_interpretacao() -> None:
    arvore = ast.parse(MODULO_ADAPTADOR.read_text(encoding="utf-8"))
    raizes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            raizes.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            raizes.add(no.module.split(".")[0])
    assert "anthropic" not in raizes
    assert "logging" not in raizes
    assert "yaml" not in raizes
    codigo = MODULO_ADAPTADOR.read_text(encoding="utf-8")
    for proibido in ("canonicalizar_interpretacao", "shell=True", "print("):
        assert proibido not in codigo, proibido


def test_o_adaptador_nao_e_exportado_pelo_pacote() -> None:
    import casa77_sdr

    assert "AdaptadorClaudeCode" not in casa77_sdr.__all__
    assert "AdaptadorClaudeCode" in interpretation_claude_code.__all__
