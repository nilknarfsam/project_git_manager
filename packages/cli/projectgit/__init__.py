"""
CLI `projectgit` — workflows Git via `project_git_core`.

O bootstrap de sys.path roda na importação do pacote para que o core
(`packages/core`) e o pacote `projectgit` (`packages/cli`) estejam resolvíveis
sem instalação pip (útil para `python -m projectgit.main` a partir de `packages/cli`).
"""

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.1.0"


def _bootstrap_sys_path() -> None:
    """Inclui `packages/core` e `packages/cli` no sys.path (raiz do monorepo inferida)."""
    pkg_dir = Path(__file__).resolve().parent
    repo_root = pkg_dir.parents[2]
    core_parent = repo_root / "packages" / "core"
    cli_parent = repo_root / "packages" / "cli"
    for p in (str(core_parent), str(cli_parent)):
        if p not in sys.path:
            sys.path.insert(0, p)


_bootstrap_sys_path()
