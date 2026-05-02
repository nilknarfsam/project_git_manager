"""Execução segura de subprocess (sem shell)."""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from project_git_core.git.models import GitCommandResult


def run_process(command: list[str], cwd: str | None = None) -> "GitCommandResult":
    """
    Executa um comando com argumentos explícitos (lista), sem shell=True.

    No Windows usa CREATE_NO_WINDOW para evitar flash de console.
    """
    # Import local para evitar ciclo na importação de pacotes
    from project_git_core.git.models import GitCommandResult

    if not command:
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message="Lista de comando vazia.",
        )

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

    try:
        proc = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
        )
    except FileNotFoundError:
        exe = command[0]
        msg = (
            f"Executável não encontrado: {exe}. Verifique o PATH ou o caminho informado."
        )
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message=msg,
        )
    except OSError as e:
        return GitCommandResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            message=f"Erro ao iniciar processo: {e}",
        )

    assert proc.stdout is not None
    assert proc.stderr is not None
    stdout, stderr = proc.communicate()
    out = stdout or ""
    err = stderr or ""
    rc = 0 if proc.returncode is None else proc.returncode
    ok = rc == 0
    msg = ""
    if not ok:
        msg = (err or out).strip() or f"Processo terminou com código {rc}."
    return GitCommandResult(
        success=ok,
        returncode=rc,
        stdout=out,
        stderr=err,
        message=msg,
    )
