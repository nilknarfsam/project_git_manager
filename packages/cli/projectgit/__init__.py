"""
CLI `projectgit` — workflows Git via `project_git_core`.

Se `project_git_core` já estiver instalado (pip), não altera sys.path.
Caso contrário, inclui `packages/core` e `packages/cli` do monorepo (fallback dev).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

__version__ = "0.1.0"


def _bootstrap_sys_path() -> None:
    """Fallback: monorepo local sem `pip install -e`."""
    pkg_dir = Path(__file__).resolve().parent
    repo_root = pkg_dir.parents[2]
    core_parent = repo_root / "packages" / "core"
    cli_parent = repo_root / "packages" / "cli"
    for p in (str(core_parent), str(cli_parent)):
        if p not in sys.path:
            sys.path.insert(0, p)


def _ensure_core_importable() -> None:
    """Prioriza import normal (pacote instalado); só então aplica fallback."""
    if importlib.util.find_spec("project_git_core") is not None:
        return
    _bootstrap_sys_path()


_ensure_core_importable()
