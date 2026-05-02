"""
Testes mínimos do pacote project_git_core (sem pytest obrigatório).

Execute na raiz do repositório:
  python tests/test_core_imports.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_core_path() -> None:
    repo = Path(__file__).resolve().parent.parent
    core_parent = repo / "packages" / "core"
    s = str(core_parent)
    if s not in sys.path:
        sys.path.insert(0, s)


def test_import_package() -> None:
    _ensure_core_path()
    import project_git_core  # noqa: PLC0415

    assert hasattr(project_git_core, "git_available")


def test_dataclasses() -> None:
    _ensure_core_path()
    from project_git_core.git.models import GitCommandResult, RepositoryOverview  # noqa: PLC0415

    r = GitCommandResult(success=True, returncode=0, stdout="out", stderr="", message="")
    assert r.success and r.returncode == 0

    o = RepositoryOverview(
        is_git_repo=False,
        path="",
        branch="-",
        has_changes=False,
        last_commit="-",
        message="ok",
    )
    assert o.is_git_repo is False


def test_git_available_is_bool() -> None:
    _ensure_core_path()
    from project_git_core.git.service import git_available  # noqa: PLC0415

    assert isinstance(git_available(), bool)


def main() -> None:
    test_import_package()
    test_dataclasses()
    test_git_available_is_bool()
    print("test_core_imports: OK")


if __name__ == "__main__":
    main()
