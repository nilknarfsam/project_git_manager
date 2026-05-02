"""
Smoke tests da CLI (sem executar git destrutivo).

Execute na raiz do repositório:
  python tests/test_cli_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_cli_overview_runs() -> None:
    cli = _repo_root() / "packages" / "cli"
    if str(cli) not in sys.path:
        sys.path.insert(0, str(cli))
    from projectgit.main import main  # noqa: PLC0415

    code = main(["overview", str(_repo_root())])
    assert code in (0, 1)


def test_build_parser() -> None:
    cli = _repo_root() / "packages" / "cli"
    if str(cli) not in sys.path:
        sys.path.insert(0, str(cli))
    from projectgit.main import build_parser  # noqa: PLC0415

    p = build_parser()
    assert p.prog == "projectgit"


def main() -> None:
    test_cli_overview_runs()
    test_build_parser()
    print("test_cli_smoke: OK")


if __name__ == "__main__":
    main()
