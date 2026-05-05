"""
Camada de compatibilidade: delega operações Git ao pacote `project_git_core`.

Mantém assinaturas e tipos de retorno esperados pela UI CustomTkinter.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from project_git_core.git import service as _pgc
from project_git_core.git.models import GitCommandResult


def _emit_git_result(r: GitCommandResult, on_line: Callable[[str, bool], None] | None) -> None:
    """Reproduz o callback por linha como no subprocess antigo (pós-communicate)."""
    if not on_line:
        return
    if r.stdout:
        for line in r.stdout.splitlines():
            on_line(line + "\n", False)
    if r.stderr:
        for line in r.stderr.splitlines():
            on_line(line + "\n", True)


def folder_exists(path: str) -> tuple[bool, str]:
    """Validação de pasta (não Git); permanece na camada legada."""
    if not path or not path.strip():
        return False, "Nenhuma pasta selecionada."
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        return False, "A pasta selecionada não existe."
    if not resolved.is_dir():
        return False, "O caminho não é uma pasta."
    return True, ""


def git_executable_available() -> tuple[bool, str]:
    if _pgc.git_available():
        return True, ""
    return (
        False,
        "O Git não foi encontrado no PATH. Instale o Git for Windows e confira se "
        "'git' está acessível no terminal (reinicie o app após alterar o PATH).",
    )


def validate_git_repo(path: str) -> tuple[bool, str]:
    r = _pgc.validate_git_repo(path)
    return r.success, r.message or ""


def run_git_command(
    command: list[str],
    path: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[int, str, str]:
    r = _pgc.run_git_command(command, path)
    _emit_git_result(r, on_line)
    rc = r.returncode
    return (rc if rc is not None else 0), r.stdout, r.stderr


def get_current_branch(path: str) -> tuple[bool, str]:
    r = _pgc.get_current_branch(path)
    if r.success:
        return True, (r.stdout or "").strip()
    return False, r.message or (r.stderr or r.stdout).strip() or f"código {r.returncode}"


def get_last_commit(path: str) -> tuple[bool, str]:
    r = _pgc.get_last_commit(path)
    if r.success:
        return True, (r.stdout or "").strip() or "-"
    return False, r.message or (r.stderr or r.stdout).strip() or f"código {r.returncode}"


def has_pending_changes(path: str) -> tuple[bool, bool]:
    r = _pgc.has_pending_changes(path)
    if not r.success:
        return False, False
    return True, bool((r.stdout or "").strip())


def get_repository_overview(path: str) -> dict[str, object]:
    o = _pgc.get_repository_overview(path)
    return {
        "is_git_repo": o.is_git_repo,
        "branch": o.branch,
        "has_changes": o.has_changes,
        "last_commit": o.last_commit,
        "message": o.message,
        "modified_count": o.modified_count,
        "untracked_count": o.untracked_count,
        "changed_files": list(o.changed_files),
    }


def force_sync_repo(
    path: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[bool, str]:
    r = _pgc.force_sync_repo(path)
    _emit_git_result(r, on_line)
    log = r.stdout or r.stderr or ""
    if not log.strip() and r.message:
        log = r.message
    return r.success, log


def clone_repo(
    repo_url: str,
    destination_path: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[int, str, str]:
    r = _pgc.clone_repo(repo_url, destination_path)
    _emit_git_result(r, on_line)
    rc = r.returncode
    return (rc if rc is not None else 0), r.stdout, r.stderr


def get_status(path: str, on_line: Callable[[str, bool], None] | None = None) -> tuple[int, str, str]:
    r = _pgc.get_status(path)
    _emit_git_result(r, on_line)
    rc = r.returncode
    return (rc if rc is not None else 0), r.stdout, r.stderr


def pull_repo(path: str, on_line: Callable[[str, bool], None] | None = None) -> tuple[int, str, str]:
    r = _pgc.pull_repo(path)
    _emit_git_result(r, on_line)
    rc = r.returncode
    return (rc if rc is not None else 0), r.stdout, r.stderr


def commit_and_push(
    path: str,
    message: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[int, str, str]:
    r_add = _pgc.run_git_command(["add", "."], path)
    _emit_git_result(r_add, on_line)
    if not r_add.success:
        rc = r_add.returncode
        return (rc if rc is not None else 0), r_add.stdout, r_add.stderr

    r_commit = _pgc.run_git_command(["commit", "-m", message], path)
    _emit_git_result(r_commit, on_line)
    if not r_commit.success:
        rc = r_commit.returncode
        return (rc if rc is not None else 0), r_commit.stdout, r_commit.stderr

    r_push = _pgc.run_git_command(["push"], path)
    _emit_git_result(r_push, on_line)
    rc = r_push.returncode
    return (rc if rc is not None else 0), r_push.stdout, r_push.stderr
