"""Adaptador **Claude Code headless** do produtor não determinístico da etapa 4.

Segundo produtor do `ProdutorTextoEstruturado` de `interpretation_llm.py`,
pensado para o **REPL local**: em vez da Messages API cobrada por chave, ele
executa a CLI `claude -p` (Claude Code em modo não interativo), que usa a
**assinatura Claude Pro/Max** em que o operador já fez login. Como o adaptador
Anthropic, ele monta uma chamada, extrai a saída estruturada e devolve uma
`str`. Ele **não** conhece `Interpretacao`, **não** traduz payload, **não**
canonicaliza, **não** decide nada comercial e **não** lê `knowledge/**`.

**Uma chamada, um desfecho.** Nenhum retry, nenhum *fallback*, nenhum cache e
nenhuma sessão persistida (`--no-session-persistence`). O `timeout` mata o
processo filho.

**Isolamento.** O processo roda com:

- `cwd` em um diretório temporário **vazio e novo** a cada chamada, para que o
  Claude Code não carregue `CLAUDE.md`, configuração de projeto ou arquivos do
  repositório como contexto;
- `--tools ""`, `--strict-mcp-config` e `--disable-slash-commands`: nenhuma
  ferramenta, nenhum servidor MCP, nenhum comando;
- o prompt de sistema em arquivo temporário (`--system-prompt-file`), fora do
  `cwd`, removido ao fim da chamada;
- a mensagem do interessado **somente via stdin** — nunca na linha de comando,
  onde ficaria visível na lista de processos;
- um ambiente copiado de `os.environ` **sem** `ANTHROPIC_API_KEY`,
  `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK` e
  `CLAUDE_CODE_USE_VERTEX`. Assim o Claude Code usa o login da assinatura e a API
  **nunca** é cobrada por acidente. Os valores dessas variáveis não são lidos:
  as chaves são apenas omitidas da cópia.

**Nenhum segredo é lido aqui.** A credencial da assinatura pertence ao próprio
Claude Code; este módulo não a lê, não a imprime e não a pede.

**Nada da conversa vaza nas falhas.** Toda falha vira
`FalhaProdutorInterpretacao` com um motivo fechado; stdout, stderr, a mensagem
e o prompt nunca entram em exceção nem em log.

`executavel`, `model` e `timeout` são **injetados e validados**: o domínio não
contém esses valores. `resolver_executavel_claude` localiza a CLI para a raiz
de composição, sem passar por `cmd.exe` no Windows.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from casa77_sdr.interpretation_llm import (
    FalhaProdutorInterpretacao,
    MotivoFalhaProdutor,
)

__all__ = [
    "AdaptadorClaudeCode",
    "ExecutavelClaudeNaoEncontrado",
    "resolver_executavel_claude",
    "verificar_login_claude",
]

#: Variáveis de credencial da API **omitidas** do ambiente do processo filho.
#: Inclui as que desviam o Claude Code para outro endpoint ou provedor cobrado
#: (base URL, Bedrock, Vertex): este caminho usa **somente** a assinatura.
_VARIAVEIS_OMITIDAS: frozenset[str] = frozenset(
    {
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_BASE_URL",
        "CLAUDE_CODE_USE_BEDROCK",
        "CLAUDE_CODE_USE_VERTEX",
    }
)

#: Caminho, relativo ao diretório do *shim* npm, do executável nativo.
_EXE_NATIVO_NPM = Path("node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe")
#: Caminho, relativo ao diretório do *shim* npm, do ponto de entrada em Node.
_CLI_JS_NPM = Path("node_modules", "@anthropic-ai", "claude-code", "cli.js")

#: Sufixos de *shim* que exigem `cmd.exe` — nunca executados diretamente.
_SUFIXOS_SHIM_WINDOWS: frozenset[str] = frozenset({".cmd", ".bat", ".ps1"})

Executor = Callable[..., subprocess.CompletedProcess[str]]


class ExecutavelClaudeNaoEncontrado(LookupError):
    """A CLI `claude` não foi encontrada de forma executável sem shell."""


def _falha(motivo: MotivoFalhaProdutor) -> FalhaProdutorInterpretacao:
    return FalhaProdutorInterpretacao(motivo)


def _ambiente_sem_credencial_da_api() -> dict[str, str]:
    """Cópia de `os.environ` sem as variáveis de credencial da API."""
    return {
        chave: valor
        for chave, valor in os.environ.items()
        if chave.upper() not in _VARIAVEIS_OMITIDAS
    }


# --------------------------------------------------------------------------
# Resolução do executável e preflight (raiz de composição)
# --------------------------------------------------------------------------


def resolver_executavel_claude(
    *, localizar: Callable[[str], str | None] = shutil.which
) -> list[str]:
    """Devolve o comando (lista de argumentos) que executa a CLI `claude`.

    No Windows, a instalação npm expõe `claude.cmd`, que só roda via `cmd.exe`
    — e `cmd.exe` reinterpreta aspas, `%`, `&` e `|` do JSON Schema. Por isso o
    *shim* nunca é executado: resolve-se o executável nativo ao lado dele
    (`node_modules/@anthropic-ai/claude-code/bin/claude.exe`) ou, na falta
    dele, `node <...>/cli.js`. Fora do Windows o *shim* é um executável comum.

    :raises ExecutavelClaudeNaoEncontrado: a CLI não está no `PATH` ou só
        existe como *shim* de shell sem alvo executável.
    """
    encontrado = localizar("claude")
    if not encontrado:
        raise ExecutavelClaudeNaoEncontrado("claude")
    caminho = Path(encontrado)
    if caminho.suffix.lower() not in _SUFIXOS_SHIM_WINDOWS:
        return [str(caminho)]
    nativo = caminho.parent / _EXE_NATIVO_NPM
    if nativo.is_file():
        return [str(nativo)]
    cli_js = caminho.parent / _CLI_JS_NPM
    node = localizar("node")
    if cli_js.is_file() and node:
        return [node, str(cli_js)]
    raise ExecutavelClaudeNaoEncontrado("claude")


def verificar_login_claude(
    comando: Sequence[str],
    *,
    timeout: float,
    executar: Executor = subprocess.run,
) -> bool:
    """`claude auth status` relata `loggedIn: true`? Sem levantar exceção.

    Só o campo booleano `loggedIn` é consultado; e-mail, organização e demais
    campos da resposta não são lidos nem devolvidos.
    """
    try:
        processo = executar(
            [*comando, "auth", "status"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            env=_ambiente_sem_credencial_da_api(),
        )
    except subprocess.TimeoutExpired:
        return False
    except OSError:
        return False
    except UnicodeDecodeError:
        return False
    if processo.returncode != 0:
        return False
    try:
        situacao = json.loads(processo.stdout)
    except json.JSONDecodeError:
        return False
    return isinstance(situacao, dict) and situacao.get("loggedIn") is True


# --------------------------------------------------------------------------
# Adaptador
# --------------------------------------------------------------------------


class AdaptadorClaudeCode:
    """Produtor de texto estruturado sobre `claude -p` (assinatura do operador).

    Implementa `ProdutorTextoEstruturado` estruturalmente — sem herdar do
    `Protocol`. `executavel` é o caminho resolvido da CLI (ou o comando já
    resolvido por `resolver_executavel_claude`); `executar` é a costura do
    processo filho, com a assinatura de `subprocess.run`, substituível nos
    testes.
    """

    def __init__(
        self,
        *,
        executavel: str | Sequence[str],
        model: str,
        timeout: float,
        executar: Executor = subprocess.run,
    ) -> None:
        if isinstance(executavel, str):
            comando = [executavel]
        elif isinstance(executavel, Sequence):
            comando = list(executavel)
        else:
            raise TypeError("executavel precisa ser str ou sequência de str")
        if not comando or not all(
            isinstance(parte, str) and parte.strip() for parte in comando
        ):
            raise ValueError("executavel precisa ser um caminho não vazio")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model precisa ser um identificador de modelo não vazio")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout precisa ser numérico")
        if timeout <= 0:
            raise ValueError("timeout precisa ser positivo")
        if not callable(executar):
            raise TypeError("executar precisa ser chamável")

        self._comando = comando
        self._model = model
        self._timeout = float(timeout)
        self._executar = executar

    # ----------------------------------------------------------------
    # Montagem da chamada
    # ----------------------------------------------------------------

    def montar_argumentos(
        self,
        *,
        caminho_prompt_sistema: str,
        schema: dict[str, Any],
    ) -> list[str]:
        """Monta a linha de comando, **sem executá-la**.

        Superfície inspecionável sem rede: modelo, prompt de sistema por
        arquivo, ferramentas e MCP desligados, sessão não persistida, saída
        JSON e o schema **compacto** em `--json-schema`. A mensagem do
        interessado **não** aparece aqui: ela vai somente pelo stdin.
        """
        return [
            *self._comando,
            "-p",
            "--model",
            self._model,
            "--system-prompt-file",
            caminho_prompt_sistema,
            "--tools",
            "",
            "--strict-mcp-config",
            "--disable-slash-commands",
            "--no-session-persistence",
            "--output-format",
            "json",
            "--json-schema",
            json.dumps(schema, ensure_ascii=False, separators=(",", ":")),
        ]

    # ----------------------------------------------------------------
    # Execução
    # ----------------------------------------------------------------

    def produzir(
        self,
        *,
        prompt_sistema: str,
        mensagem: str,
        schema: dict[str, Any],
    ) -> str:
        """Uma chamada, um desfecho. Devolve o **texto JSON** da saída.

        :raises FalhaProdutorInterpretacao: processo que não termina com
            sucesso, saída ilegível, erro relatado pela CLI ou ausência de
            `structured_output` objeto.
        """
        processo = self._chamar(
            prompt_sistema=prompt_sistema, mensagem=mensagem, schema=schema
        )
        if processo.returncode != 0:
            raise _falha(MotivoFalhaProdutor.ERRO_DO_PROVEDOR)
        return self._selecionar_saida(processo.stdout)

    def _chamar(
        self,
        *,
        prompt_sistema: str,
        mensagem: str,
        schema: dict[str, Any],
    ) -> subprocess.CompletedProcess[str]:
        try:
            with (
                # `ignore_cleanup_errors`: no Windows, a limpeza logo após o
                # término forçado do filho pode falhar por arquivo ainda
                # aberto, e isso não pode mascarar o desfecho real (TIMEOUT).
                tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as diretorio_prompt,
                tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as diretorio_trabalho,
            ):
                caminho_prompt = Path(diretorio_prompt) / "prompt-sistema.md"
                caminho_prompt.write_text(prompt_sistema, encoding="utf-8")
                argumentos = self.montar_argumentos(
                    caminho_prompt_sistema=str(caminho_prompt), schema=schema
                )
                return self._executar(
                    argumentos,
                    input=mensagem,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=self._timeout,
                    cwd=diretorio_trabalho,
                    env=_ambiente_sem_credencial_da_api(),
                )
        except subprocess.TimeoutExpired:
            # `from None` em todos os ramos: nenhuma saída do processo, nenhuma
            # mensagem e nenhum prompt atravessam a fronteira.
            raise _falha(MotivoFalhaProdutor.TIMEOUT) from None
        except UnicodeDecodeError:
            raise _falha(MotivoFalhaProdutor.JSON_INVALIDO) from None
        except ValueError:
            # Prompt ou mensagem não codificáveis (surrogate isolado, byte nulo
            # em argumento): a chamada nem chega a ser feita.
            raise _falha(MotivoFalhaProdutor.ERRO_DE_TRANSPORTE) from None
        except OSError:
            raise _falha(MotivoFalhaProdutor.ERRO_DE_TRANSPORTE) from None

    @staticmethod
    def _selecionar_saida(stdout: Any) -> str:
        """Lê o envelope JSON da CLI e devolve **só** `structured_output`.

        Vocabulário fechado: `is_error` precisa ser exatamente `False` e
        `subtype` exatamente `"success"`; `result` (texto livre) nunca é usado.
        """
        if not isinstance(stdout, str):
            raise _falha(MotivoFalhaProdutor.JSON_INVALIDO)
        try:
            envelope = json.loads(stdout)
        except json.JSONDecodeError:
            raise _falha(MotivoFalhaProdutor.JSON_INVALIDO) from None
        if not isinstance(envelope, dict):
            raise _falha(MotivoFalhaProdutor.JSON_INVALIDO)
        if envelope.get("is_error") is not False:
            raise _falha(MotivoFalhaProdutor.ERRO_DO_PROVEDOR)
        if envelope.get("subtype") != "success":
            raise _falha(MotivoFalhaProdutor.ERRO_DO_PROVEDOR)
        saida = envelope.get("structured_output")
        if not isinstance(saida, dict):
            raise _falha(MotivoFalhaProdutor.SEM_BLOCO_ESTRUTURADO)
        return json.dumps(saida, ensure_ascii=False)
