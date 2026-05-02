"""Modelos de dados para resultados Git e visão do repositório."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GitCommandResult:
    """Resultado unificado de um comando externo (ex.: Git via subprocess)."""

    success: bool
    returncode: int
    stdout: str = ""
    stderr: str = ""
    message: str = ""


@dataclass(frozen=True)
class RepositoryOverview:
    """Resumo somente leitura de um diretório como repositório Git."""

    is_git_repo: bool
    path: str
    branch: str
    has_changes: bool
    last_commit: str
    message: str
