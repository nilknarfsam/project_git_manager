"""Núcleo reutilizável: operações Git e modelos de resultado."""

from __future__ import annotations

from project_git_core.git.models import GitCommandResult, RepositoryOverview
from project_git_core.git.service import (
    clone_repo,
    commit_and_push,
    force_sync_repo,
    get_current_branch,
    get_last_commit,
    get_repository_overview,
    get_status,
    git_available,
    has_pending_changes,
    pull_repo,
    run_git_command,
    validate_git_repo,
)

__all__ = [
    "GitCommandResult",
    "RepositoryOverview",
    "clone_repo",
    "commit_and_push",
    "force_sync_repo",
    "get_current_branch",
    "get_last_commit",
    "get_repository_overview",
    "get_status",
    "git_available",
    "has_pending_changes",
    "pull_repo",
    "run_git_command",
    "validate_git_repo",
]
