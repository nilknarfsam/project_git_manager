"""
Entrypoint da CLI `projectgit`.

Execução típica (a partir da pasta `packages/cli` do monorepo):
  python -m projectgit.main status C:\\src\\projects\\auratime
  python -m projectgit

O pacote `projectgit` ajusta sys.path em __init__.py antes dos imports do core.
"""

from __future__ import annotations

import argparse
import sys

from projectgit import __version__
from projectgit.commands import clone, commit, overview, pull, status, sync


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="projectgit",
        description="CLI de workflows Git (usa project_git_core).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMANDO")

    status.register(sub)
    sync.register(sub)
    clone.register(sub)
    pull.register(sub)
    commit.register(sub)
    overview.register(sub)

    return parser


def _ensure_utf8_stdio() -> None:
    """Evita UnicodeEncodeError no Windows (ex.: cp1252) ao imprimir símbolos."""
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            try:
                reconf(encoding="utf-8", errors="replace")
            except (OSError, ValueError, AttributeError):
                pass


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "_handler", None)
    if handler is None:
        parser.print_help()
        return 2
    return int(handler(args))


if __name__ == "__main__":
    sys.exit(main())
