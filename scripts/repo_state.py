"""Verificação determinística e read-only do estado Git do repositório Casa 77 SDR.

Dois subcomandos:

* `pre`  — confirma que a working tree está no ponto de partida esperado antes de
  uma execução: repositório canônico, branch, `HEAD`, `origin/main` local e
  limpeza da árvore.
* `post` — confirma que o delta produzido por uma execução cabe **inteiramente**
  dentro de um conjunto explícito de caminhos permitidos.

O script é **estritamente read-only** e **não acessa a rede**: não faz `fetch`,
não executa `git ls-remote`, não consulta a API do GitHub, não depende de `gh`,
não lê nem escreve credencial e não corrige nada automaticamente. A atualização
da referência remota é responsabilidade de um `git fetch origin` explícito,
executado **fora** deste script quando o mandato exigir frescor remoto.

Ele também **não executa testes**: o comando real de testes continua sendo
responsabilidade do mandato vigente.

Contrato de saída: linhas `CHAVE=VALOR` em ordem estável, terminando **sempre**
por `RESULT=PASS`, `RESULT=STOP` ou `RESULT=ERROR`. Códigos de saída:
`0` para `PASS`, `1` para `STOP`, `2` para `ERROR`, com precedência
`ERROR > STOP > PASS`.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Repositório canônico do projeto. Nenhum SHA temporal é embutido aqui.
REPO_CANONICO = "shumbertshuanys/casa77-sdr"

FORMATO = "1"
TIMEOUT_GIT = 60

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_DRIVE_WINDOWS = re.compile(r"^[A-Za-z]:")
_GLOB = "*?[]"

# Operações Git em andamento detectadas por existência física do caminho que o
# próprio Git informa. Nenhuma delas é corrigida por este script.
OPERACOES = (
    "MERGE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
    "BISECT_LOG",
    "rebase-merge",
    "rebase-apply",
)


class ErroGit(Exception):
    """Falha ao invocar o Git, já reduzida a um código sanitizado."""

    def __init__(self, codigo: str) -> None:
        super().__init__(codigo)
        self.codigo = codigo


class ErroUso(Exception):
    """Argumento inválido detectado fora do argparse."""

    def __init__(self, codigo: str) -> None:
        super().__init__(codigo)
        self.codigo = codigo


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------


def escapar(valor: str) -> str:
    """Escapa barra invertida e caracteres de controle de um valor de saída."""
    saida = []
    for caractere in valor:
        if caractere == "\\":
            saida.append("\\\\")
        elif ord(caractere) < 0x20 or ord(caractere) == 0x7F:
            saida.append(f"\\x{ord(caractere):02x}")
        else:
            saida.append(caractere)
    return "".join(saida)


class Saida:
    """Acumula pares `CHAVE=VALOR` e fecha com a linha `RESULT`."""

    def __init__(self) -> None:
        self._pares: list[str] = []
        self._warns: list[str] = []
        self._stops: list[str] = []
        self._erro: str | None = None

    def par(self, chave: str, valor: object) -> None:
        self._pares.append(f"{chave}={escapar(str(valor))}")

    def warn(self, codigo: str) -> None:
        self._warns.append(codigo)

    def stop(self, codigo: str) -> None:
        self._stops.append(codigo)

    def erro(self, codigo: str) -> None:
        self._erro = codigo

    def emitir(self) -> int:
        linhas = list(self._pares)
        linhas.extend(f"WARN={w}" for w in self._warns)
        linhas.extend(f"STOP={s}" for s in self._stops)
        if self._erro is not None:
            linhas.append(f"ERROR={self._erro}")
        if self._erro is not None:
            resultado = "ERROR"
        elif self._stops:
            resultado = "STOP"
        else:
            resultado = "PASS"
        linhas.append(f"RESULT={resultado}")
        sys.stdout.write("\n".join(linhas) + "\n")
        return {"PASS": 0, "STOP": 1, "ERROR": 2}[resultado]


def emitir_erro_simples(codigo: str) -> None:
    """Emite o bloco mínimo de erro, usado quando nem o modo é conhecido."""
    sys.stdout.write(f"REPO_STATE_FORMAT={FORMATO}\nERROR={codigo}\nRESULT=ERROR\n")


# ---------------------------------------------------------------------------
# Invocação do Git
# ---------------------------------------------------------------------------


def executar_git(
    args: list[str],
    *,
    raiz: str | None = None,
    permitir_falha: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    """Invoca o Git sem shell, sem stdin e sem prompt interativo.

    `stderr` do Git nunca é ecoado automaticamente: falhas viram códigos
    sanitizados.
    """
    ambiente = dict(os.environ)
    ambiente["GIT_OPTIONAL_LOCKS"] = "0"
    ambiente["GIT_TERMINAL_PROMPT"] = "0"
    ambiente["GCM_INTERACTIVE"] = "never"
    comando = [
        "git",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.quotepath=false",
        *args,
    ]
    try:
        processo = subprocess.run(
            comando,
            cwd=raiz,
            env=ambiente,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=TIMEOUT_GIT,
        )
    except FileNotFoundError as erro:
        raise ErroGit("GIT_NOT_FOUND") from erro
    except subprocess.TimeoutExpired as erro:
        raise ErroGit("GIT_TIMEOUT") from erro
    if processo.returncode != 0 and not permitir_falha:
        raise ErroGit("GIT_COMMAND_FAILED")
    return processo


def texto(processo: subprocess.CompletedProcess[bytes]) -> str:
    return processo.stdout.decode("utf-8", errors="replace").strip()


def campos_z(processo: subprocess.CompletedProcess[bytes]) -> list[str]:
    """Divide uma saída `-z` em campos, descartando o vazio final."""
    bruto = processo.stdout.decode("utf-8", errors="replace")
    return [campo for campo in bruto.split("\0") if campo != ""]


# ---------------------------------------------------------------------------
# Identidade do `origin`
# ---------------------------------------------------------------------------


def _owner_repo(caminho: str, *, barra_final: bool) -> str | None:
    """Reduz o caminho da URL a `owner/repo` minúsculo, ou `None`."""
    if caminho.endswith("/"):
        if not barra_final:
            return None
        caminho = caminho[:-1]
    if caminho.lower().endswith(".git"):
        caminho = caminho[: -len(".git")]
    partes = caminho.split("/")
    if len(partes) != 2 or not all(partes):
        return None
    return f"{partes[0].lower()}/{partes[1].lower()}"


def normalizar_url(url: str) -> tuple[str, str]:
    """Reduz uma URL de remote a `(estado, owner/repo)`.

    Estados: `OK` (forma permitida e `owner/repo` extraído), `CREDENCIAL` e
    `UNPARSEABLE`. Só três famílias são aceitas — `https://github.com/…`,
    `git@github.com:…` e `ssh://git@github.com/…` —, todas sem porta explícita,
    sem query e sem fragment; `ssh` exige o usuário exatamente `git` e `https`
    não admite userinfo. Nenhuma URL, nem parte dela, é devolvida quando a forma
    não é reconhecida.
    """
    valor = url.strip()
    if not valor:
        return ("UNPARSEABLE", "")

    if "://" in valor:
        esquema, _, corpo = valor.partition("://")
        autoridade, _, caminho = corpo.partition("/")
        userinfo, arroba, host = autoridade.rpartition("@")
        if not arroba:
            userinfo, host = "", autoridade
        if ":" in userinfo:
            return ("CREDENCIAL", "")
        if esquema.lower() == "https":
            if userinfo:
                return ("CREDENCIAL", "")
        elif esquema.lower() == "ssh":
            if userinfo != "git":
                return ("UNPARSEABLE", "")
        else:
            # `http`, `git+ssh`, `git`, `file` e quaisquer outros ficam de fora.
            return ("UNPARSEABLE", "")
        barra_final = True
    elif "@" in valor and ":" in valor.rpartition("@")[2]:
        # Forma scp-like: `git@github.com:owner/repo.git`, sem barra final.
        userinfo, _, resto = valor.rpartition("@")
        host, _, caminho = resto.partition(":")
        if ":" in userinfo:
            return ("CREDENCIAL", "")
        if userinfo != "git":
            return ("UNPARSEABLE", "")
        barra_final = False
    else:
        return ("UNPARSEABLE", "")

    if ":" in host:
        # Porta explícita não é forma prevista, inclusive 22 e 443.
        return ("UNPARSEABLE", "")
    if host.lower() != "github.com":
        return ("UNPARSEABLE", "")
    if "?" in caminho or "#" in caminho:
        # Query e fragment podem carregar conteúdo sensível; nunca são lidos.
        return ("UNPARSEABLE", "")

    repositorio = _owner_repo(caminho, barra_final=barra_final)
    if repositorio is None:
        return ("UNPARSEABLE", "")
    return ("OK", repositorio)


def conferir_origin(saida: Saida, raiz: str) -> None:
    """Valida `remote.origin.url` e, quando existir, `remote.origin.pushurl`."""
    processo = executar_git(
        ["config", "--get-all", "remote.origin.url"], raiz=raiz, permitir_falha=True
    )
    urls = [linha for linha in texto(processo).splitlines() if linha.strip()]

    if processo.returncode != 0 or not urls:
        saida.par("ORIGIN_REPO", "NONE")
        saida.stop("ORIGIN_MISSING")
    elif len(urls) > 1:
        saida.par("ORIGIN_REPO", "AMBIGUOUS")
        saida.stop("ORIGIN_URL_AMBIGUOUS")
    else:
        estado, repositorio = normalizar_url(urls[0])
        if estado == "CREDENCIAL":
            # Nem a URL nem parte dela é impressa em qualquer hipótese.
            saida.par("ORIGIN_REPO", "REDACTED")
            saida.stop("ORIGIN_URL_HAS_CREDENTIALS")
        elif estado == "OK" and repositorio == REPO_CANONICO:
            saida.par("ORIGIN_REPO", repositorio)
        elif estado == "OK":
            # Forma reconhecida, repositório divergente: o owner/repo lido não
            # é ecoado.
            saida.par("ORIGIN_REPO", "MISMATCH")
            saida.stop("ORIGIN_REPO_MISMATCH")
        else:
            saida.par("ORIGIN_REPO", "UNPARSEABLE")
            saida.stop("ORIGIN_REPO_MISMATCH")

    processo = executar_git(
        ["config", "--get-all", "remote.origin.pushurl"], raiz=raiz, permitir_falha=True
    )
    pushurls = [linha for linha in texto(processo).splitlines() if linha.strip()]
    if processo.returncode != 0 or not pushurls:
        saida.par("ORIGIN_PUSHURL", "NONE")
        return

    credencial = False
    divergente = False
    ilegivel = False
    for url in pushurls:
        estado, repositorio = normalizar_url(url)
        if estado == "CREDENCIAL":
            credencial = True
        elif estado != "OK":
            ilegivel = True
        elif repositorio != REPO_CANONICO:
            divergente = True
    if credencial:
        saida.par("ORIGIN_PUSHURL", "REDACTED")
        saida.stop("ORIGIN_URL_HAS_CREDENTIALS")
    elif divergente or ilegivel:
        # Mesmo princípio do `url`: nada derivado do remote é ecoado.
        saida.par("ORIGIN_PUSHURL", "UNPARSEABLE" if ilegivel else "MISMATCH")
        saida.stop("PUSHURL_MISMATCH")
    else:
        saida.par("ORIGIN_PUSHURL", REPO_CANONICO)


# ---------------------------------------------------------------------------
# Estado da working tree
# ---------------------------------------------------------------------------


class EstadoArvore:
    """Contagens e listas derivadas de `git status --porcelain=v2`."""

    def __init__(self) -> None:
        self.staged: list[str] = []
        self.unstaged: list[str] = []
        self.untracked: list[str] = []
        self.unmerged: list[str] = []

    @property
    def suja(self) -> bool:
        return bool(self.staged or self.unstaged or self.untracked)


def ler_arvore(raiz: str) -> EstadoArvore:
    processo = executar_git(
        [
            "status",
            "--porcelain=v2",
            "-z",
            "--untracked-files=all",
            "--no-renames",
        ],
        raiz=raiz,
    )
    estado = EstadoArvore()
    for registro in campos_z(processo):
        marcador = registro[:1]
        if marcador == "1":
            partes = registro.split(" ", 8)
            if len(partes) < 9:
                continue
            xy, caminho = partes[1], partes[8]
            if xy[0] != ".":
                estado.staged.append(caminho)
            if xy[1] != ".":
                estado.unstaged.append(caminho)
        elif marcador == "u":
            partes = registro.split(" ", 10)
            if len(partes) >= 11:
                estado.unmerged.append(partes[10])
        elif marcador == "?":
            estado.untracked.append(registro[2:])
    estado.staged.sort()
    estado.unstaged.sort()
    estado.untracked.sort()
    estado.unmerged.sort()
    return estado


def operacoes_em_andamento(raiz: str) -> list[str]:
    encontradas = []
    for nome in OPERACOES:
        processo = executar_git(["rev-parse", "--git-path", nome], raiz=raiz)
        caminho = texto(processo)
        if not os.path.isabs(caminho):
            caminho = os.path.join(raiz, caminho)
        if os.path.exists(caminho):
            encontradas.append(nome)
    return sorted(encontradas)


def localizar_raiz() -> str:
    processo = executar_git(["rev-parse", "--show-toplevel"], permitir_falha=True)
    if processo.returncode != 0:
        raise ErroGit("NOT_A_GIT_WORKTREE")
    raiz = texto(processo)
    if not raiz:
        raise ErroGit("NOT_A_GIT_WORKTREE")
    dentro = executar_git(
        ["rev-parse", "--is-inside-work-tree"], raiz=raiz, permitir_falha=True
    )
    if dentro.returncode != 0 or texto(dentro) != "true":
        raise ErroGit("NOT_A_GIT_WORKTREE")
    return raiz


def versao_git() -> str:
    partes = texto(executar_git(["--version"])).split()
    return partes[2] if len(partes) >= 3 else "UNKNOWN"


def cabecalho(saida: Saida, modo: str, raiz: str) -> None:
    saida.par("REPO_STATE_FORMAT", FORMATO)
    saida.par("MODE", modo)
    saida.par("PLATFORM", sys.platform)
    saida.par("PYTHON_VERSION", platform.python_version())
    saida.par("GIT_VERSION", versao_git())
    saida.par("REPO_ROOT", raiz)


def rodape(saida: Saida) -> None:
    saida.par("OPEN_PRS", "NOT_CHECKED")
    saida.par("NETWORK", "NOT_USED")
    saida.par("TESTS", "NOT_RUN_BY_SCRIPT")


# ---------------------------------------------------------------------------
# Caminhos permitidos
# ---------------------------------------------------------------------------


def validar_allow(valor: str) -> str:
    """Valida um `--allow`. Rejeita tudo que não seja caminho literal POSIX."""
    if valor != valor.strip(" "):
        raise argparse.ArgumentTypeError("caminho com espaco nas pontas")
    if not valor:
        raise argparse.ArgumentTypeError("caminho vazio")
    if "\\" in valor:
        raise argparse.ArgumentTypeError("barra invertida nao e permitida")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in valor):
        raise argparse.ArgumentTypeError("caractere de controle no caminho")
    if any(c in valor for c in _GLOB):
        raise argparse.ArgumentTypeError("glob nao e permitido")
    if valor.startswith("/"):
        raise argparse.ArgumentTypeError("caminho absoluto nao e permitido")
    if _DRIVE_WINDOWS.match(valor):
        raise argparse.ArgumentTypeError("drive do Windows nao e permitido")
    if valor.startswith("./"):
        raise argparse.ArgumentTypeError("prefixo ./ nao e permitido")
    nucleo = valor[:-1] if valor.endswith("/") else valor
    if not nucleo:
        raise argparse.ArgumentTypeError("caminho vazio")
    for segmento in nucleo.split("/"):
        if segmento in ("", ".", ".."):
            raise argparse.ArgumentTypeError("segmento invalido no caminho")
    return valor


def caminho_permitido(caminho: str, permitidos: list[str]) -> bool:
    """Diretório casa somente descendentes; arquivo casa somente igualdade."""
    for permitido in permitidos:
        if permitido.endswith("/"):
            if caminho.startswith(permitido):
                return True
        elif caminho == permitido:
            return True
    return False


def validar_sha40(valor: str) -> str:
    if not _SHA40.match(valor):
        raise argparse.ArgumentTypeError("SHA deve ter 40 caracteres hexadecimais")
    return valor


# ---------------------------------------------------------------------------
# Subcomando `pre`
# ---------------------------------------------------------------------------


def comando_pre(args: argparse.Namespace) -> int:
    saida = Saida()
    raiz = localizar_raiz()
    cabecalho(saida, "pre", raiz)
    conferir_origin(saida, raiz)

    ref = executar_git(
        ["symbolic-ref", "--quiet", "--short", "HEAD"], raiz=raiz, permitir_falha=True
    )
    destacada = ref.returncode != 0
    branch = "DETACHED" if destacada else texto(ref)
    saida.par("BRANCH", branch)
    saida.par("EXPECTED_BRANCH", args.expect_branch)

    cabeca = executar_git(
        ["rev-parse", "--verify", "--quiet", "HEAD"], raiz=raiz, permitir_falha=True
    )
    head = texto(cabeca) if cabeca.returncode == 0 else ""
    saida.par("HEAD", head or "NONE")
    saida.par("EXPECTED_MAIN", args.expect_main)

    origem = executar_git(
        ["rev-parse", "--verify", "--quiet", "refs/remotes/origin/main"],
        raiz=raiz,
        permitir_falha=True,
    )
    origin_main = texto(origem) if origem.returncode == 0 else ""
    saida.par("ORIGIN_MAIN_LOCAL", origin_main or "NONE")

    operacoes = operacoes_em_andamento(raiz)
    saida.par("OPERATIONS", ",".join(operacoes) if operacoes else "NONE")

    arvore = ler_arvore(raiz)
    saida.par("STAGED_COUNT", len(arvore.staged))
    saida.par("UNSTAGED_COUNT", len(arvore.unstaged))
    saida.par("UNTRACKED_COUNT", len(arvore.untracked))
    saida.par("UNMERGED_COUNT", len(arvore.unmerged))
    for caminho in arvore.staged:
        saida.par("STAGED_PATH", caminho)
    for caminho in arvore.unstaged:
        saida.par("UNSTAGED_PATH", caminho)
    for caminho in arvore.untracked:
        saida.par("UNTRACKED_PATH", caminho)
    for caminho in arvore.unmerged:
        saida.par("UNMERGED_PATH", caminho)
    saida.par("ALLOW_DIRTY", "true" if args.allow_dirty else "false")
    rodape(saida)

    if destacada:
        saida.stop("DETACHED_HEAD")
    elif branch != args.expect_branch:
        saida.stop("BRANCH_MISMATCH")
    if not head:
        saida.stop("HEAD_MISSING")
    if operacoes:
        saida.stop("OPERATION_IN_PROGRESS")
    if arvore.unmerged:
        saida.stop("UNMERGED_PATHS")
    if arvore.suja:
        if args.allow_dirty:
            saida.warn("DIRTY_ALLOWED")
        else:
            saida.stop("DIRTY_WORKTREE")
    if not origin_main:
        saida.stop("ORIGIN_MAIN_MISSING")
    elif origin_main != args.expect_main:
        saida.stop("ORIGIN_MAIN_MISMATCH")
    if head and head != args.expect_main:
        saida.stop("HEAD_MISMATCH")

    return saida.emitir()


# ---------------------------------------------------------------------------
# Subcomando `post`
# ---------------------------------------------------------------------------


def nomes_diff(raiz: str, args: list[str]) -> list[str]:
    processo = executar_git(
        ["diff", "--name-only", "--no-renames", "-z", *args], raiz=raiz
    )
    return campos_z(processo)


def numstat_diff(raiz: str, args: list[str]) -> list[tuple[str, str, str]]:
    processo = executar_git(
        ["diff", "--numstat", "--no-renames", "-z", *args], raiz=raiz
    )
    registros = []
    for campo in campos_z(processo):
        partes = campo.split("\t", 2)
        if len(partes) == 3:
            registros.append((partes[0], partes[1], partes[2]))
    return registros


def rodar_diff_check(raiz: str, args: list[str]) -> bool:
    """Roda o gate nativo do Git. `True` quando há problema reportado."""
    processo = executar_git(["diff", "--check", *args], raiz=raiz, permitir_falha=True)
    if processo.returncode == 0:
        return False
    if processo.returncode in (1, 2):
        return True
    raise ErroGit("GIT_COMMAND_FAILED")


def comando_post(args: argparse.Namespace) -> int:
    saida = Saida()
    raiz = localizar_raiz()
    cabecalho(saida, "post", raiz)
    conferir_origin(saida, raiz)

    ref = executar_git(
        ["symbolic-ref", "--quiet", "--short", "HEAD"], raiz=raiz, permitir_falha=True
    )
    destacada = ref.returncode != 0
    saida.par("BRANCH", "DETACHED" if destacada else texto(ref))

    cabeca = executar_git(
        ["rev-parse", "--verify", "--quiet", "HEAD"], raiz=raiz, permitir_falha=True
    )
    head = texto(cabeca) if cabeca.returncode == 0 else ""
    saida.par("HEAD", head or "NONE")
    saida.par("BASE", args.base)

    permitidos = sorted(set(args.allow or []))
    saida.par("ALLOW_COUNT", len(permitidos))
    for permitido in permitidos:
        saida.par("ALLOW", permitido)

    operacoes = operacoes_em_andamento(raiz)
    saida.par("OPERATIONS", ",".join(operacoes) if operacoes else "NONE")

    arvore = ler_arvore(raiz)
    saida.par("STAGED_COUNT", len(arvore.staged))
    saida.par("UNSTAGED_COUNT", len(arvore.unstaged))
    saida.par("UNTRACKED_COUNT", len(arvore.untracked))
    saida.par("UNMERGED_COUNT", len(arvore.unmerged))

    base_conhecida = (
        executar_git(
            ["cat-file", "-e", f"{args.base}^{{commit}}"], raiz=raiz, permitir_falha=True
        ).returncode
        == 0
    )
    descendente = False
    if base_conhecida and head:
        descendente = (
            executar_git(
                ["merge-base", "--is-ancestor", args.base, "HEAD"],
                raiz=raiz,
                permitir_falha=True,
            ).returncode
            == 0
        )

    if base_conhecida and descendente:
        commits_ahead = texto(
            executar_git(["rev-list", "--count", f"{args.base}..HEAD"], raiz=raiz)
        )
    else:
        commits_ahead = "UNKNOWN"
    saida.par("COMMITS_AHEAD", commits_ahead)

    escopos: list[tuple[str, list[str]]] = []
    if base_conhecida and descendente:
        escopos.append(("COMMITTED", nomes_diff(raiz, [args.base, "HEAD"])))
    if head:
        escopos.append(("STAGED", nomes_diff(raiz, ["--cached", "HEAD"])))
    escopos.append(("UNSTAGED", nomes_diff(raiz, [])))
    escopos.append(
        (
            "UNTRACKED",
            campos_z(
                executar_git(
                    ["ls-files", "--others", "--exclude-standard", "-z"], raiz=raiz
                )
            ),
        )
    )

    uniao: set[str] = set()
    for escopo, caminhos in escopos:
        for caminho in sorted(set(caminhos)):
            saida.par("PATH", f"{escopo} {caminho}")
            uniao.add(caminho)
    saida.par("CHANGED_COUNT", len(uniao))

    inesperados = sorted(
        caminho for caminho in uniao if not caminho_permitido(caminho, permitidos)
    )
    saida.par("UNEXPECTED_COUNT", len(inesperados))

    if base_conhecida and descendente:
        for rotulo, argumentos in (
            ("COMMITTED", [args.base, "HEAD"]),
            ("STAGED", ["--cached", "HEAD"]),
            ("UNSTAGED", []),
        ):
            for adicionadas, removidas, caminho in numstat_diff(raiz, argumentos):
                saida.par("NUMSTAT", f"{rotulo} {adicionadas} {removidas} {caminho}")

    falhou_check = False
    if base_conhecida and descendente:
        falhou_check = rodar_diff_check(raiz, [args.base]) or rodar_diff_check(
            raiz, ["--cached", args.base]
        )
        saida.par("DIFF_CHECK", "FAILED" if falhou_check else "OK")
    else:
        saida.par("DIFF_CHECK", "NOT_RUN")

    if arvore.untracked:
        saida.par("UNTRACKED_DIFF_CHECK", "DEFERRED_UNTIL_STAGED")
    else:
        saida.par("UNTRACKED_DIFF_CHECK", "NOT_APPLICABLE")
    rodape(saida)

    if destacada:
        saida.stop("DETACHED_HEAD")
    if operacoes:
        saida.stop("OPERATION_IN_PROGRESS")
    if arvore.unmerged:
        saida.stop("UNMERGED_PATHS")
    if not base_conhecida:
        saida.stop("BASE_UNKNOWN")
    elif not descendente:
        saida.stop("HEAD_NOT_DESCENDANT_OF_BASE")
    for caminho in inesperados:
        saida.stop(f"UNEXPECTED_PATH {escapar(caminho)}")
    if falhou_check:
        saida.stop("DIFF_CHECK_FAILED")

    return saida.emitir()


# ---------------------------------------------------------------------------
# Interface de linha de comando
# ---------------------------------------------------------------------------


class Parser(argparse.ArgumentParser):
    """`ArgumentParser` que fecha todo erro com `RESULT=ERROR` e código 2."""

    def error(self, message: str) -> None:  # type: ignore[override]
        sys.stderr.write(f"repo_state: {message}\n")
        emitir_erro_simples("USAGE")
        raise SystemExit(2)

    def exit(self, status: int = 0, message: str | None = None) -> None:  # type: ignore[override]
        if status == 0:
            if message:
                sys.stdout.write(message)
            raise SystemExit(0)
        if message:
            sys.stderr.write(message)
        emitir_erro_simples("USAGE")
        raise SystemExit(2)


def construir_parser() -> Parser:
    parser = Parser(
        prog="repo_state.py",
        description=(
            "Verificacao determinista e read-only do estado Git do repositorio "
            f"{REPO_CANONICO}. Nao acessa a rede e nao executa testes."
        ),
    )
    subcomandos = parser.add_subparsers(dest="modo", required=True)

    pre = subcomandos.add_parser(
        "pre",
        help="confirma o ponto de partida esperado da working tree",
        description=(
            "Confirma repositorio canonico, branch, HEAD, origin/main local e "
            "limpeza da arvore. A atualizacao da referencia remota depende de um "
            "'git fetch origin' explicito executado fora deste script."
        ),
    )
    pre.add_argument(
        "--expect-main",
        required=True,
        type=validar_sha40,
        metavar="SHA40",
        help="SHA de 40 hexadecimais esperado em HEAD e em origin/main local",
    )
    pre.add_argument(
        "--expect-branch",
        default="main",
        metavar="BRANCH",
        help="branch esperada (default: main)",
    )
    pre.add_argument(
        "--allow-dirty",
        action="store_true",
        help="nao parar por arvore suja; emite WARN=DIRTY_ALLOWED",
    )
    pre.set_defaults(funcao=comando_pre)

    post = subcomandos.add_parser(
        "post",
        help="confirma que o delta cabe nos caminhos permitidos",
        description=(
            "Audita a uniao de COMMITTED (base->HEAD), STAGED (index->HEAD), "
            "UNSTAGED (worktree->index) e UNTRACKED contra os caminhos "
            "declarados em --allow. Renames sao tratados como delete + add."
        ),
    )
    post.add_argument(
        "--base",
        required=True,
        type=validar_sha40,
        metavar="SHA40",
        help="SHA de 40 hexadecimais da base ancestral de HEAD",
    )
    post.add_argument(
        "--allow",
        action="append",
        default=[],
        type=validar_allow,
        metavar="PATH",
        help=(
            "caminho permitido, relativo a raiz e com '/'. Sem barra final casa "
            "somente o arquivo identico; com barra final casa apenas descendentes "
            "do diretorio. Repetivel; zero ocorrencias e permitido"
        ),
    )
    post.set_defaults(funcao=comando_post)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)
    try:
        return args.funcao(args)
    except ErroGit as erro:
        emitir_erro_simples(erro.codigo)
        return 2
    except ErroUso as erro:
        emitir_erro_simples(erro.codigo)
        return 2
    except Exception as erro:  # noqa: BLE001 - traceback nunca é impresso
        emitir_erro_simples(f"INTERNAL_{type(erro).__name__}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
