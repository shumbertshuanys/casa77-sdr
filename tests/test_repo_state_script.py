"""Testes do script determinístico de prestate/poststate `scripts/repo_state.py`.

Todos os cenários são construídos em **repositórios Git temporários**, criados e
mutados livremente pelos próprios testes. Nenhum teste toca o repositório real,
acessa a rede, consulta o GitHub, usa credential helper, dorme, repete tentativa,
pula ou marca falha esperada.

A configuração global e de sistema do Git é neutralizada por ambiente, e a
identidade do autor é fornecida **apenas** no ambiente do processo de teste.
"""

from __future__ import annotations

import ast
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "repo_state.py"

URL_CANONICA = "https://github.com/shumbertshuanys/casa77-sdr.git"

ZERO40 = "0" * 40
SHA_INEXISTENTE = "0123456789abcdef0123456789abcdef01234567"


def _ambiente(teto: Path) -> dict[str, str]:
    """Ambiente isolado: sem config global/sistema, sem prompt, sem rede."""
    ambiente = dict(os.environ)
    ambiente.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CEILING_DIRECTORIES": str(teto),
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "Teste",
            "GIT_AUTHOR_EMAIL": "teste@example.invalid",
            "GIT_COMMITTER_NAME": "Teste",
            "GIT_COMMITTER_EMAIL": "teste@example.invalid",
        }
    )
    return ambiente


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    processo = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=_ambiente(repo.parent),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and processo.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} falhou: {processo.stderr}")
    return processo


def _escrever(repo: Path, caminho: str, conteudo: str) -> None:
    destino = repo / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8", newline="\n")


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _rodar(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=repo,
        env=_ambiente(repo.parent),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class Relatorio:
    """Leitura estruturada do stdout `CHAVE=VALOR` do script."""

    def __init__(self, processo: subprocess.CompletedProcess[str]) -> None:
        self.processo = processo
        self.pares: dict[str, list[str]] = {}
        for linha in processo.stdout.splitlines():
            chave, _, valor = linha.partition("=")
            self.pares.setdefault(chave, []).append(valor)

    def um(self, chave: str) -> str:
        valores = self.pares.get(chave, [])
        assert len(valores) == 1, f"{chave} apareceu {len(valores)} vezes"
        return valores[0]

    @property
    def stops(self) -> list[str]:
        return self.pares.get("STOP", [])

    @property
    def warns(self) -> list[str]:
        return self.pares.get("WARN", [])

    @property
    def erros(self) -> list[str]:
        return self.pares.get("ERROR", [])

    @property
    def resultado(self) -> str:
        return self.um("RESULT")

    def ultima_linha_e_result(self) -> bool:
        return self.processo.stdout.splitlines()[-1].startswith("RESULT=")


def _pre(repo: Path, *args: str) -> Relatorio:
    return Relatorio(_rodar(repo, "pre", *args))


def _post(repo: Path, *args: str) -> Relatorio:
    return Relatorio(_rodar(repo, "post", *args))


def _assert_pass(relatorio: Relatorio) -> None:
    assert relatorio.resultado == "PASS", relatorio.processo.stdout
    assert relatorio.processo.returncode == 0
    assert relatorio.stops == []
    assert relatorio.erros == []
    assert relatorio.ultima_linha_e_result()


def _assert_stop(relatorio: Relatorio, codigo: str) -> None:
    assert relatorio.resultado == "STOP", relatorio.processo.stdout
    assert relatorio.processo.returncode == 1
    assert codigo in relatorio.stops, relatorio.processo.stdout
    assert relatorio.ultima_linha_e_result()


def _assert_error(relatorio: Relatorio) -> None:
    assert relatorio.resultado == "ERROR", relatorio.processo.stdout
    assert relatorio.processo.returncode == 2
    assert relatorio.erros, relatorio.processo.stdout
    assert relatorio.ultima_linha_e_result()


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Repositório temporário com branch `main`, remote canônico e origin/main."""
    caminho = tmp_path / "repo"
    caminho.mkdir()
    _git(caminho, "init", "-b", "main")
    _escrever(caminho, "docs/a.md", "linha inicial\n")
    _escrever(caminho, "tests/existente.py", "valor = 1\n")
    _git(caminho, "add", "docs/a.md", "tests/existente.py")
    _git(caminho, "commit", "-m", "inicial")
    _git(caminho, "remote", "add", "origin", URL_CANONICA)
    _git(caminho, "update-ref", "refs/remotes/origin/main", _head(caminho))
    return caminho


# ---------------------------------------------------------------------------
# 1–2 — caminho feliz e ausência de repositório
# ---------------------------------------------------------------------------


def test_pre_repo_correto_e_limpo_resulta_pass(repo: Path) -> None:
    """Caso 1."""
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_pass(relatorio)
    assert relatorio.um("MODE") == "pre"
    assert relatorio.um("REPO_STATE_FORMAT") == "1"
    assert relatorio.um("ORIGIN_REPO") == "shumbertshuanys/casa77-sdr"
    assert relatorio.um("BRANCH") == "main"
    assert relatorio.um("HEAD") == _head(repo)
    assert relatorio.um("ORIGIN_MAIN_LOCAL") == _head(repo)
    assert relatorio.um("OPERATIONS") == "NONE"
    assert relatorio.um("STAGED_COUNT") == "0"
    assert relatorio.um("UNSTAGED_COUNT") == "0"
    assert relatorio.um("UNTRACKED_COUNT") == "0"
    assert relatorio.um("UNMERGED_COUNT") == "0"
    assert relatorio.um("OPEN_PRS") == "NOT_CHECKED"
    assert relatorio.um("NETWORK") == "NOT_USED"
    assert relatorio.um("TESTS") == "NOT_RUN_BY_SCRIPT"


def test_diretorio_sem_git_resulta_error(tmp_path: Path) -> None:
    """Caso 2."""
    fora = tmp_path / "fora"
    fora.mkdir()
    relatorio = Relatorio(_rodar(fora, "pre", "--expect-main", ZERO40))
    _assert_error(relatorio)
    assert relatorio.erros == ["NOT_A_GIT_WORKTREE"]


# ---------------------------------------------------------------------------
# 3–6 — identidade do `origin`
# ---------------------------------------------------------------------------


def test_origin_ausente_resulta_stop(repo: Path) -> None:
    """Caso 3."""
    _git(repo, "remote", "remove", "origin")
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_MISSING")
    assert relatorio.um("ORIGIN_REPO") == "NONE"


def _sem_repo_root(relatorio: Relatorio) -> str:
    """stdout sem a linha `REPO_ROOT`.

    `REPO_ROOT` é o caminho real da working tree, informado deliberadamente e
    alheio ao remote; o `tmp_path` do pytest embute o nome do próprio teste
    nesse caminho, o que tornaria a busca por vazamento ambígua.
    """
    return "\n".join(
        linha
        for linha in relatorio.processo.stdout.splitlines()
        if not linha.startswith("REPO_ROOT=")
    )


def test_origin_de_repositorio_divergente_resulta_stop_sem_ecoar(repo: Path) -> None:
    """Caso 4, reforçado pelo caso 7 da correção: o owner/repo não é ecoado."""
    _git(
        repo, "config", "remote.origin.url", "https://github.com/alheia/projetozz.git"
    )
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_REPO_MISMATCH")
    assert relatorio.um("ORIGIN_REPO") == "MISMATCH"
    for vazado in ("alheia", "projetozz", "github.com"):
        assert vazado not in _sem_repo_root(relatorio)
        assert vazado not in relatorio.processo.stderr


@pytest.mark.parametrize(
    "url",
    [
        # Transporte fora do contrato.
        "git+ssh://git@github.com/shumbertshuanys/casa77-sdr.git",
        "http://github.com/shumbertshuanys/casa77-sdr.git",
        "git://github.com/shumbertshuanys/casa77-sdr.git",
        # Porta explícita, inclusive as convencionais.
        "ssh://git@github.com:2222/shumbertshuanys/casa77-sdr.git",
        "ssh://git@github.com:22/shumbertshuanys/casa77-sdr.git",
        "https://github.com:8443/shumbertshuanys/casa77-sdr.git",
        "https://github.com:443/shumbertshuanys/casa77-sdr.git",
        # Host e usuário fora do contrato.
        "https://gitlab.com/shumbertshuanys/casa77-sdr.git",
        "ssh://outro@github.com/shumbertshuanys/casa77-sdr.git",
        "outro@github.com:shumbertshuanys/casa77-sdr.git",
        # Formas adicionais não previstas.
        "git@github.com:shumbertshuanys/casa77-sdr/",
        "https://github.com/shumbertshuanys/casa77-sdr/extra.git",
        "/caminho/local/casa77-sdr",
    ],
)
def test_forma_de_origin_fora_do_contrato_resulta_stop(repo: Path, url: str) -> None:
    """Casos 2, 3 e 4 da correção: só as três famílias previstas são aceitas."""
    _git(repo, "config", "remote.origin.url", url)
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_REPO_MISMATCH")
    assert relatorio.um("ORIGIN_REPO") == "UNPARSEABLE"


@pytest.mark.parametrize(
    "molde",
    [
        "https://github.com/shumbertshuanys/casa77-sdr.git?token={segredo}",
        "https://github.com/shumbertshuanys/casa77-sdr.git#{segredo}",
    ],
)
def test_query_ou_fragment_com_segredo_nao_vaza(repo: Path, molde: str) -> None:
    """Casos 5 e 6 da correção."""
    segredo = "ghp-segredo-ficticio-em-query-987"
    _git(repo, "config", "remote.origin.url", molde.format(segredo=segredo))
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_REPO_MISMATCH")
    assert relatorio.um("ORIGIN_REPO") == "UNPARSEABLE"
    assert segredo not in relatorio.processo.stdout
    assert segredo not in relatorio.processo.stderr


def test_origin_com_credencial_nao_vaza_o_segredo(repo: Path) -> None:
    """Caso 5."""
    segredo = "ghp-segredo-ficticio-123"
    _git(
        repo,
        "config",
        "remote.origin.url",
        f"https://usuario:{segredo}@github.com/shumbertshuanys/casa77-sdr.git",
    )
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_URL_HAS_CREDENTIALS")
    assert segredo not in relatorio.processo.stdout
    assert segredo not in relatorio.processo.stderr
    assert "usuario" not in relatorio.processo.stdout
    assert relatorio.um("ORIGIN_REPO") == "REDACTED"


def test_origin_url_multipla_resulta_stop(repo: Path) -> None:
    """Complemento do caso 3/4: ambiguidade de URL."""
    _git(repo, "config", "--add", "remote.origin.url", URL_CANONICA)
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_URL_AMBIGUOUS")


def test_pushurl_divergente_resulta_stop(repo: Path) -> None:
    """Caso 6."""
    _git(
        repo, "config", "remote.origin.pushurl", "https://github.com/outro/projeto.git"
    )
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "PUSHURL_MISMATCH")


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/shumbertshuanys/casa77-sdr",
        "https://github.com/shumbertshuanys/casa77-sdr.git",
        "https://github.com/shumbertshuanys/casa77-sdr/",
        "https://github.com/SHUMBERTSHUANYS/Casa77-SDR.git",
        "git@github.com:shumbertshuanys/casa77-sdr",
        "git@github.com:shumbertshuanys/casa77-sdr.git",
        "ssh://git@github.com/shumbertshuanys/casa77-sdr",
        "ssh://git@github.com/shumbertshuanys/casa77-sdr.git",
    ],
)
def test_formas_equivalentes_de_url_sao_aceitas(repo: Path, url: str) -> None:
    """As formas canônicas listadas no contrato são todas aceitas."""
    _git(repo, "config", "remote.origin.url", url)
    _assert_pass(_pre(repo, "--expect-main", _head(repo)))


# ---------------------------------------------------------------------------
# 7–12 — branch, HEAD e referência remota local
# ---------------------------------------------------------------------------


def test_branch_errada_resulta_stop(repo: Path) -> None:
    """Caso 7."""
    _git(repo, "switch", "-c", "outra")
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "BRANCH_MISMATCH")
    assert relatorio.um("BRANCH") == "outra"


def test_expect_branch_explicito_em_branch_nao_main_resulta_pass(repo: Path) -> None:
    """Caso 8."""
    _git(repo, "switch", "-c", "feat/x")
    _assert_pass(
        _pre(repo, "--expect-main", _head(repo), "--expect-branch", "feat/x")
    )


def test_head_diferente_do_esperado_resulta_stop(repo: Path) -> None:
    """Caso 9."""
    relatorio = _pre(repo, "--expect-main", SHA_INEXISTENTE)
    _assert_stop(relatorio, "HEAD_MISMATCH")


def test_origin_main_ausente_resulta_stop(repo: Path) -> None:
    """Caso 10."""
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_MAIN_MISSING")
    assert relatorio.um("ORIGIN_MAIN_LOCAL") == "NONE"


def test_origin_main_diferente_do_esperado_resulta_stop(repo: Path) -> None:
    """Caso 11."""
    primeiro = _head(repo)
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    _git(repo, "add", "docs/a.md")
    _git(repo, "commit", "-m", "segundo")
    _git(repo, "update-ref", "refs/remotes/origin/main", primeiro)
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "ORIGIN_MAIN_MISMATCH")


def test_detached_head_resulta_stop(repo: Path) -> None:
    """Caso 12."""
    _git(repo, "checkout", "--detach", "HEAD")
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "DETACHED_HEAD")
    assert relatorio.um("BRANCH") == "DETACHED"


def test_detached_head_no_post_resulta_stop(repo: Path) -> None:
    """Caso 1 da correção: `post` aplica a mesma regra estrutural do `pre`."""
    _git(repo, "checkout", "--detach", "HEAD")
    relatorio = _post(repo, "--base", _head(repo))
    _assert_stop(relatorio, "DETACHED_HEAD")
    assert relatorio.processo.returncode == 1
    assert relatorio.um("BRANCH") == "DETACHED"
    # As demais informações seguramente avaliáveis continuam sendo coletadas.
    assert relatorio.um("HEAD") == _head(repo)
    assert relatorio.um("COMMITS_AHEAD") == "0"
    assert relatorio.um("DIFF_CHECK") == "OK"


# ---------------------------------------------------------------------------
# 13–16 — limpeza, conflito e operações em andamento
# ---------------------------------------------------------------------------


def test_working_tree_suja_resulta_stop(repo: Path) -> None:
    """Caso 13."""
    _escrever(repo, "docs/a.md", "linha inicial\nalterada\n")
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "DIRTY_WORKTREE")
    assert relatorio.um("UNSTAGED_COUNT") == "1"
    assert relatorio.pares["UNSTAGED_PATH"] == ["docs/a.md"]


def test_allow_dirty_converte_sujeira_em_warn(repo: Path) -> None:
    """Caso 14."""
    _escrever(repo, "docs/a.md", "linha inicial\nalterada\n")
    _escrever(repo, "novo.txt", "novo\n")
    relatorio = _pre(repo, "--expect-main", _head(repo), "--allow-dirty")
    _assert_pass(relatorio)
    assert relatorio.warns == ["DIRTY_ALLOWED"]
    assert relatorio.um("ALLOW_DIRTY") == "true"


def _criar_conflito(repo: Path) -> None:
    _escrever(repo, "conflito.txt", "base\n")
    _git(repo, "add", "conflito.txt")
    _git(repo, "commit", "-m", "base do conflito")
    _git(repo, "switch", "-c", "lado")
    _escrever(repo, "conflito.txt", "lado\n")
    _git(repo, "add", "conflito.txt")
    _git(repo, "commit", "-m", "lado")
    _git(repo, "switch", "main")
    _escrever(repo, "conflito.txt", "principal\n")
    _git(repo, "add", "conflito.txt")
    _git(repo, "commit", "-m", "principal")
    resultado = _git(repo, "merge", "lado", check=False)
    assert resultado.returncode != 0, "o merge deveria conflitar"
    _git(repo, "update-ref", "refs/remotes/origin/main", _head(repo))


def test_unmerged_para_mesmo_com_allow_dirty(repo: Path) -> None:
    """Caso 15."""
    _criar_conflito(repo)
    relatorio = _pre(repo, "--expect-main", _head(repo), "--allow-dirty")
    _assert_stop(relatorio, "UNMERGED_PATHS")
    assert int(relatorio.um("UNMERGED_COUNT")) >= 1


@pytest.mark.parametrize(
    ("nome", "e_diretorio"),
    [
        ("MERGE_HEAD", False),
        ("CHERRY_PICK_HEAD", False),
        ("REVERT_HEAD", False),
        ("BISECT_LOG", False),
        ("rebase-merge", True),
        ("rebase-apply", True),
    ],
)
def test_operacao_em_andamento_resulta_stop(
    repo: Path, nome: str, e_diretorio: bool
) -> None:
    """Caso 16."""
    alvo = repo / ".git" / nome
    if e_diretorio:
        alvo.mkdir()
    else:
        alvo.write_text(_head(repo) + "\n", encoding="utf-8")
    relatorio = _pre(repo, "--expect-main", _head(repo))
    _assert_stop(relatorio, "OPERATION_IN_PROGRESS")
    assert relatorio.um("OPERATIONS") == nome


# ---------------------------------------------------------------------------
# 17 e 37 — argumentos inválidos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("valor", ["abc123", "", "0" * 39, "0" * 41, "0" * 39 + "Z"])
def test_sha_invalido_resulta_error(repo: Path, valor: str) -> None:
    """Caso 17."""
    _assert_error(_pre(repo, "--expect-main", valor))


@pytest.mark.parametrize(
    "valor",
    [
        "../fora.md",
        "docs/../a.md",
        "./docs/a.md",
        "docs\\a.md",
        "/docs/a.md",
        "C:/docs/a.md",
        "docs/*.md",
        "docs/a?.md",
        "docs/[ab].md",
        "docs//a.md",
        " docs/a.md",
        "docs/a.md ",
        ".",
        "..",
        "/",
    ],
)
def test_allow_invalido_resulta_error(repo: Path, valor: str) -> None:
    """Caso 37."""
    _assert_error(_post(repo, "--base", _head(repo), "--allow", valor))


# ---------------------------------------------------------------------------
# 18–27 — escopo do `post`
# ---------------------------------------------------------------------------


def test_post_modificado_permitido_resulta_pass(repo: Path) -> None:
    """Caso 18."""
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    relatorio = _post(repo, "--base", _head(repo), "--allow", "docs/a.md")
    _assert_pass(relatorio)
    assert relatorio.um("CHANGED_COUNT") == "1"
    assert relatorio.um("UNEXPECTED_COUNT") == "0"
    assert relatorio.um("DIFF_CHECK") == "OK"
    assert relatorio.um("UNTRACKED_DIFF_CHECK") == "NOT_APPLICABLE"


def test_post_modificado_inesperado_resulta_stop(repo: Path) -> None:
    """Caso 19."""
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    relatorio = _post(repo, "--base", _head(repo), "--allow", "tests/existente.py")
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/a.md")


def test_post_untracked_permitido_difere_o_check(repo: Path) -> None:
    """Caso 20."""
    _escrever(repo, "docs/novo.md", "novo\n")
    relatorio = _post(repo, "--base", _head(repo), "--allow", "docs/novo.md")
    _assert_pass(relatorio)
    assert relatorio.um("UNTRACKED_DIFF_CHECK") == "DEFERRED_UNTIL_STAGED"
    assert relatorio.um("UNTRACKED_COUNT") == "1"


def test_post_untracked_inesperado_resulta_stop(repo: Path) -> None:
    """Caso 21."""
    _escrever(repo, "docs/novo.md", "novo\n")
    relatorio = _post(repo, "--base", _head(repo))
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/novo.md")


def test_post_staged_permitido_resulta_pass(repo: Path) -> None:
    """Caso 22."""
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    _git(repo, "add", "docs/a.md")
    _assert_pass(_post(repo, "--base", _head(repo), "--allow", "docs/a.md"))


def test_post_staged_inesperado_resulta_stop(repo: Path) -> None:
    """Caso 23."""
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    _git(repo, "add", "docs/a.md")
    relatorio = _post(repo, "--base", _head(repo))
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/a.md")


def test_prefixo_acidental_de_arquivo_resulta_stop(repo: Path) -> None:
    """Caso 24."""
    _escrever(repo, "docs/a.md.bak", "copia\n")
    relatorio = _post(repo, "--base", _head(repo), "--allow", "docs/a.md")
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/a.md.bak")


def test_prefixo_acidental_de_diretorio_resulta_stop(repo: Path) -> None:
    """Caso 25."""
    _escrever(repo, "tests_extra/a.py", "valor = 2\n")
    relatorio = _post(repo, "--base", _head(repo), "--allow", "tests/")
    _assert_stop(relatorio, "UNEXPECTED_PATH tests_extra/a.py")


def test_diretorio_permitido_casa_descendente_real(repo: Path) -> None:
    """Caso 26."""
    _escrever(repo, "tests/novo.py", "valor = 3\n")
    _assert_pass(_post(repo, "--base", _head(repo), "--allow", "tests/"))


def test_delecao_inesperada_resulta_stop(repo: Path) -> None:
    """Caso 27."""
    (repo / "docs" / "a.md").unlink()
    relatorio = _post(repo, "--base", _head(repo))
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/a.md")


def test_rename_exige_os_dois_caminhos_permitidos(repo: Path) -> None:
    """Caso 28."""
    _git(repo, "mv", "docs/a.md", "docs/b.md")
    relatorio = _post(repo, "--base", _head(repo), "--allow", "docs/b.md")
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/a.md")
    _assert_pass(
        _post(
            repo,
            "--base",
            _head(repo),
            "--allow",
            "docs/a.md",
            "--allow",
            "docs/b.md",
        )
    )


# ---------------------------------------------------------------------------
# 29–30 — gate nativo de whitespace
# ---------------------------------------------------------------------------


def test_whitespace_invalido_em_tracked_resulta_stop(repo: Path) -> None:
    """Caso 29."""
    _escrever(repo, "docs/a.md", "linha inicial\nlinha com espaco   \n")
    relatorio = _post(repo, "--base", _head(repo), "--allow", "docs/a.md")
    _assert_stop(relatorio, "DIFF_CHECK_FAILED")
    assert relatorio.um("DIFF_CHECK") == "FAILED"


def test_whitespace_invalido_em_arquivo_novo_apos_staging_resulta_stop(
    repo: Path,
) -> None:
    """Caso 30."""
    _escrever(repo, "docs/novo.md", "linha com espaco   \n")
    base = _head(repo)
    relatorio = _post(repo, "--base", base, "--allow", "docs/novo.md")
    _assert_pass(relatorio)
    assert relatorio.um("UNTRACKED_DIFF_CHECK") == "DEFERRED_UNTIL_STAGED"

    _git(repo, "add", "docs/novo.md")
    relatorio = _post(repo, "--base", base, "--allow", "docs/novo.md")
    _assert_stop(relatorio, "DIFF_CHECK_FAILED")


# ---------------------------------------------------------------------------
# 31–34 — commits à frente e base
# ---------------------------------------------------------------------------


def test_commit_a_frente_com_caminho_permitido_resulta_pass(repo: Path) -> None:
    """Caso 31."""
    base = _head(repo)
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    _git(repo, "add", "docs/a.md")
    _git(repo, "commit", "-m", "avanco permitido")
    relatorio = _post(repo, "--base", base, "--allow", "docs/a.md")
    _assert_pass(relatorio)
    assert relatorio.um("COMMITS_AHEAD") == "1"
    assert "NUMSTAT" in relatorio.pares


def test_commit_a_frente_com_caminho_inesperado_resulta_stop(repo: Path) -> None:
    """Caso 32."""
    base = _head(repo)
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    _git(repo, "add", "docs/a.md")
    _git(repo, "commit", "-m", "avanco inesperado")
    relatorio = _post(repo, "--base", base, "--allow", "tests/")
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/a.md")


def test_base_inexistente_resulta_stop(repo: Path) -> None:
    """Caso 33."""
    relatorio = _post(repo, "--base", SHA_INEXISTENTE)
    _assert_stop(relatorio, "BASE_UNKNOWN")
    assert relatorio.um("COMMITS_AHEAD") == "UNKNOWN"
    assert relatorio.um("DIFF_CHECK") == "NOT_RUN"


def test_base_fora_da_ancestralidade_resulta_stop(repo: Path) -> None:
    """Caso 34."""
    _git(repo, "switch", "-c", "lado")
    _escrever(repo, "docs/lado.md", "lado\n")
    _git(repo, "add", "docs/lado.md")
    _git(repo, "commit", "-m", "lado")
    base_lateral = _head(repo)
    _git(repo, "switch", "main")
    _escrever(repo, "docs/a.md", "linha inicial\nprincipal\n")
    _git(repo, "add", "docs/a.md")
    _git(repo, "commit", "-m", "principal")
    relatorio = _post(repo, "--base", base_lateral)
    _assert_stop(relatorio, "HEAD_NOT_DESCENDANT_OF_BASE")


# ---------------------------------------------------------------------------
# 35–36 — zero `--allow`
# ---------------------------------------------------------------------------


def test_zero_allow_sem_mudanca_resulta_pass(repo: Path) -> None:
    """Caso 35."""
    relatorio = _post(repo, "--base", _head(repo))
    _assert_pass(relatorio)
    assert relatorio.um("ALLOW_COUNT") == "0"
    assert relatorio.um("CHANGED_COUNT") == "0"


def test_zero_allow_com_mudanca_resulta_stop(repo: Path) -> None:
    """Caso 36."""
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    relatorio = _post(repo, "--base", _head(repo))
    _assert_stop(relatorio, "UNEXPECTED_PATH docs/a.md")


# ---------------------------------------------------------------------------
# 38–39 — determinismo e ausência de efeito colateral
# ---------------------------------------------------------------------------


def test_execucoes_iguais_produzem_stdout_igual(repo: Path) -> None:
    """Caso 38."""
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    _escrever(repo, "docs/novo.md", "novo\n")
    primeira = _post(repo, "--base", _head(repo), "--allow", "docs/")
    segunda = _post(repo, "--base", _head(repo), "--allow", "docs/")
    assert primeira.processo.stdout == segunda.processo.stdout
    assert primeira.processo.returncode == segunda.processo.returncode

    uma = _pre(repo, "--expect-main", _head(repo), "--allow-dirty")
    outra = _pre(repo, "--expect-main", _head(repo), "--allow-dirty")
    assert uma.processo.stdout == outra.processo.stdout


def _impressao(raiz: Path) -> dict[str, str]:
    """Assinatura de conteúdo de todos os arquivos, incluindo os de `.git`."""
    assinatura = {}
    for caminho in sorted(raiz.rglob("*")):
        if caminho.is_file():
            digesto = hashlib.sha256(caminho.read_bytes()).hexdigest()
            assinatura[str(caminho.relative_to(raiz)).replace("\\", "/")] = digesto
    return assinatura


def test_script_nao_altera_o_repositorio(repo: Path) -> None:
    """Caso 39."""
    _escrever(repo, "docs/a.md", "linha inicial\nsegunda\n")
    _escrever(repo, "docs/novo.md", "novo\n")
    antes = _impressao(repo)

    # As duas execuções da prova precisam ser PASS: um STOP precoce poderia
    # abortar antes de exercitar os comandos que tocariam o repositório.
    _assert_pass(_pre(repo, "--expect-main", _head(repo), "--allow-dirty"))
    _assert_pass(_post(repo, "--base", _head(repo), "--allow", "docs/"))

    assert _impressao(repo) == antes


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argumentos",
    [("--help",), ("pre", "--help"), ("post", "--help")],
)
def test_help_descreve_a_interface(repo: Path, argumentos: tuple[str, ...]) -> None:
    processo = _rodar(repo, *argumentos)
    assert processo.returncode == 0
    assert "usage" in processo.stdout.lower()
    assert "RESULT=ERROR" not in processo.stdout


def test_sem_subcomando_resulta_error(repo: Path) -> None:
    relatorio = Relatorio(_rodar(repo))
    _assert_error(relatorio)
    assert relatorio.erros == ["USAGE"]


def _literais_de_codigo(arvore: ast.Module) -> list[str]:
    """Literais `str` do código, excluindo docstrings de módulo, classe e função."""
    docstrings = set()
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            corpo = getattr(no, "body", [])
            if (
                corpo
                and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)
            ):
                docstrings.add(id(corpo[0].value))
    return [
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant)
        and isinstance(no.value, str)
        and id(no) not in docstrings
    ]


def test_script_nao_tem_caminho_de_rede_nem_ferramenta_externa() -> None:
    """Nenhum literal do código pode invocar rede, e nenhum import pode habilitá-la.

    A verificação é feita sobre a árvore sintática: as menções em prosa nos
    docstrings, que existem justamente para **negar** essas operações, não
    contam.
    """
    fonte = SCRIPT.read_text(encoding="utf-8")
    arvore = ast.parse(fonte)

    # Um subcomando de rede só alcança o Git como argumento exato. A comparação
    # é por igualdade: a prosa da ajuda pode citar `git fetch origin` para dizer
    # que ele roda FORA deste script, e isso não é uma invocação.
    literais = set(_literais_de_codigo(arvore))
    for proibido in ("fetch", "clone", "ls-remote", "push", "pull", "remote"):
        assert proibido not in literais, proibido

    modulos = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            modulos.add(no.module.split(".")[0])
    assert modulos == {"argparse", "os", "platform", "re", "subprocess", "sys", "__future__"}

    assert "shell=True" not in fonte
