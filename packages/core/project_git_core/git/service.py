"""
Serviço Git: subprocess com argv explícito, sem shell.
Comportamento alinhado ao legado CustomTkinter (clone vs sync, Windows).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from project_git_core.git.models import GitCommandResult, RepositoryOverview
from project_git_core.utils.process import run_process


def _normalize_cwd(path: str) -> str:
    return str(Path(path).expanduser().resolve())


def git_available() -> bool:
    """True se o executável `git` estiver no PATH."""
    return shutil.which("git") is not None


def run_git_command(command: list[str], path: str | None = None) -> GitCommandResult:
    """
    Executa `git` com argumentos (sem o prefixo 'git') no diretório `path`.

    Se `path` for None, cwd do subprocess fica None (diretório atual do processo).
    """
    cwd: str | None = None
    if path is not None and str(path).strip():
        cwd = _normalize_cwd(path)
    full = ["git", *command]
    return run_process(full, cwd=cwd)


def validate_git_repo(path: str) -> GitCommandResult:
    """
    Valida existência de diretório e `.git` (sem invocar git).

    success=True quando for repositório Git válido.
    """
    if not path or not path.strip():
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message="Nenhuma pasta selecionada.",
        )
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message="A pasta selecionada não existe.",
        )
    if not resolved.is_dir():
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message="O caminho não é uma pasta.",
        )
    if not (resolved / ".git").exists():
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message="Esta pasta não é um repositório Git (.git não encontrado).",
        )
    return GitCommandResult(
        success=True,
        returncode=0,
        stdout="",
        stderr="",
        message="",
    )


def get_current_branch(path: str) -> GitCommandResult:
    """
    Branch atual ou erro (HEAD destacado ou falha do git).

    Em sucesso, o nome da branch está em stdout (trimmed).
    """
    r = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], path)
    if not r.success:
        detail = (r.stderr or r.stdout).strip() or f"código {r.returncode}"
        return GitCommandResult(
            success=False,
            returncode=r.returncode,
            stdout="",
            stderr=r.stderr,
            message=detail,
        )
    name = (r.stdout or "").strip()
    if not name:
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message="Branch vazia.",
        )
    if name == "HEAD":
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="HEAD",
            stderr="",
            message=(
                "HEAD destacado: não há branch nomeada. Faça checkout de uma branch "
                "(ex.: git checkout main)."
            ),
        )
    return GitCommandResult(
        success=True,
        returncode=0,
        stdout=name,
        stderr="",
        message="",
    )


def get_last_commit(path: str) -> GitCommandResult:
    """Último commit curto em stdout (hash - assunto) ou message de erro."""
    r = run_git_command(["log", "-1", "--pretty=format:%h - %s"], path)
    if not r.success:
        detail = (r.stderr or r.stdout).strip() or f"código {r.returncode}"
        return GitCommandResult(
            success=False,
            returncode=r.returncode,
            stdout="",
            stderr=r.stderr,
            message=detail,
        )
    text = (r.stdout or "").strip()
    return GitCommandResult(
        success=True,
        returncode=0,
        stdout=text if text else "-",
        stderr="",
        message="",
    )


def has_pending_changes(path: str) -> GitCommandResult:
    """
    `git status --porcelain`.

    success indica que o comando git terminou com rc==0.
    Alterações pendentes: stdout não vazio.
    """
    return run_git_command(["status", "--porcelain"], path)


def get_repository_overview(path: str) -> RepositoryOverview:
    """Resumo do repositório (somente leitura)."""
    not_git_msg = "A pasta selecionada não é um repositório Git."
    raw = (path or "").strip()
    if not raw:
        return RepositoryOverview(
            is_git_repo=False,
            path="",
            branch="-",
            has_changes=False,
            last_commit="-",
            message="Nenhuma pasta selecionada.",
        )

    resolved = Path(raw).expanduser().resolve()
    path_str = str(resolved) if resolved.exists() else raw

    vr = validate_git_repo(raw)
    if not vr.success:
        return RepositoryOverview(
            is_git_repo=False,
            path=path_str,
            branch="-",
            has_changes=False,
            last_commit="-",
            message=not_git_msg,
        )

    ok_lc = get_last_commit(raw)
    last_commit = (ok_lc.stdout or "").strip() if ok_lc.success else "-"

    ok_br = get_current_branch(raw)
    st = has_pending_changes(raw)
    has_ch = bool((st.stdout or "").strip()) if st.success else False

    if not ok_br.success:
        return RepositoryOverview(
            is_git_repo=True,
            path=path_str,
            branch="-",
            has_changes=has_ch,
            last_commit=last_commit,
            message=ok_br.message or (ok_br.stderr or ok_br.stdout).strip() or "-",
        )

    return RepositoryOverview(
        is_git_repo=True,
        path=path_str,
        branch=(ok_br.stdout or "").strip(),
        has_changes=has_ch,
        last_commit=last_commit,
        message="Repositório carregado com sucesso.",
    )


def force_sync_repo(path: str) -> GitCommandResult:
    """
    fetch origin, reset --hard origin/<branch>, clean -fd.

    Retorna log completo em stdout em caso de sucesso; em falha, stdout acumula
    o log e message stderr detalham a falha (compatível com consumo legado).
    """
    vr = validate_git_repo(path)
    if not vr.success:
        p = Path(path).expanduser().resolve()
        if p.exists() and p.is_dir():
            msg = "A pasta existe, mas não é um repositório Git."
        else:
            msg = vr.message or "A pasta existe, mas não é um repositório Git."
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message=msg,
        )

    br = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], path)
    branch = (br.stdout or "").strip()
    if not br.success or not branch:
        detail = (br.stderr or br.stdout or "").strip()
        tail = f"\n{detail}" if detail else ""
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message=f"Não foi possível detectar a branch atual.{tail}",
        )
    if branch == "HEAD":
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message="Repositório em HEAD destacado; faça checkout de uma branch antes de sincronizar.",
        )

    commands: list[list[str]] = [
        ["fetch", "origin"],
        ["reset", "--hard", f"origin/{branch}"],
        ["clean", "-fd"],
    ]
    output_log = ""
    for cmd in commands:
        line_cmd = f"> git {' '.join(cmd)}\n"
        output_log += line_cmd
        gr = run_git_command(cmd, path)
        block = ""
        if (gr.stdout or "").strip():
            o = gr.stdout
            block += o if o.endswith("\n") else o + "\n"
        if (gr.stderr or "").strip():
            e = gr.stderr
            block += e if e.endswith("\n") else e + "\n"
        output_log += block
        if not gr.success:
            fail = (gr.stderr or gr.stdout or "").strip() or f"código {gr.returncode}"
            return GitCommandResult(
                success=False,
                returncode=gr.returncode,
                stdout=output_log + f"\n(comando falhou: {fail})\n",
                stderr="",
                message=fail,
            )

    return GitCommandResult(
        success=True,
        returncode=0,
        stdout=output_log,
        stderr="",
        message="",
    )


def clone_repo(repo_url: str, destination_path: str) -> GitCommandResult:
    """
    Clone em destination_path (caminho completo da pasta final).

    Se a pasta já existir e for repo Git: force_sync_repo.
    Se pasta existe e não é Git: erro claro.
    """
    repo_url = (repo_url or "").strip()
    dest_raw = (destination_path or "").strip()

    if not repo_url:
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="A URL do repositório não foi informada.",
            message="A URL do repositório não foi informada.",
        )
    if not dest_raw:
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="A pasta de destino não foi informada.",
            message="A pasta de destino não foi informada.",
        )

    destination = Path(dest_raw).expanduser().resolve()
    parent_folder = destination.parent
    folder_name = destination.name

    if not folder_name or folder_name in (".", ".."):
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=(
                "Informe o caminho completo da pasta do clone, incluindo o nome da pasta "
                "que será criada (ex.: C:\\src\\projects\\auratime)."
            ),
            message=(
                "Informe o caminho completo da pasta do clone, incluindo o nome da pasta "
                "que será criada (ex.: C:\\src\\projects\\auratime)."
            ),
        )

    if any(sep in folder_name for sep in ("/", "\\")):
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=(
                "O nome da pasta final não pode conter barras. Use um caminho como "
                "C:\\src\\projects\\auratime (a última parte é só o nome da pasta)."
            ),
            message=(
                "O nome da pasta final não pode conter barras. Use um caminho como "
                "C:\\src\\projects\\auratime (a última parte é só o nome da pasta)."
            ),
        )

    if not parent_folder.exists():
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=f"A pasta pai não existe: {parent_folder}",
            message=f"A pasta pai não existe: {parent_folder}",
        )
    if not parent_folder.is_dir():
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=f"A pasta pai não é um diretório: {parent_folder}",
            message=f"A pasta pai não é um diretório: {parent_folder}",
        )

    if destination.exists():
        vr = validate_git_repo(str(destination))
        if not vr.success:
            return GitCommandResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=(
                    "A pasta de destino já existe e não é um repositório Git válido. "
                    "Escolha outro caminho ou use uma pasta vazia/inexistente para clonar."
                ),
                message=(
                    "A pasta de destino já existe e não é um repositório Git válido. "
                    "Escolha outro caminho ou use uma pasta vazia/inexistente para clonar."
                ),
            )
        sync = force_sync_repo(str(destination))
        if sync.success:
            return GitCommandResult(
                success=True,
                returncode=0,
                stdout=sync.stdout,
                stderr="",
                message="",
            )
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=sync.stdout or sync.message,
            message=sync.message or "Falha ao sincronizar.",
        )

    if not git_available():
        msg = (
            "O Git não foi encontrado no PATH. Instale o Git for Windows e confira se "
            "'git' está acessível no terminal (reinicie o app após alterar o PATH)."
        )
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=msg,
            message=msg,
        )

    return run_git_command(["clone", repo_url, folder_name], str(parent_folder))


def get_status(path: str) -> GitCommandResult:
    return run_git_command(["status"], path)


def pull_repo(path: str) -> GitCommandResult:
    return run_git_command(["pull"], path)


def commit_and_push(path: str, message: str) -> GitCommandResult:
    """git add ., commit -m, push."""
    r = run_git_command(["add", "."], path)
    if not r.success:
        return r
    r = run_git_command(["commit", "-m", message], path)
    if not r.success:
        return r
    return run_git_command(["push"], path)
