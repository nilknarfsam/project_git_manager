"""Subcomando: git add, commit e push."""

from __future__ import annotations

import argparse
import sys

from project_git_core.git.service import commit_and_push

from projectgit.out import err, ok


def register(subparsers) -> None:
    p = subparsers.add_parser("commit", help="git add ., commit -m e push.")
    p.add_argument("path", help="Pasta raiz do repositório Git.")
    p.add_argument(
        "-m",
        "--message",
        required=True,
        dest="message",
        help="Mensagem do commit.",
    )
    p.set_defaults(_handler=run)


def run(args: argparse.Namespace) -> int:
    r = commit_and_push(args.path, args.message)
    if r.stdout:
        sys.stdout.write(r.stdout if r.stdout.endswith("\n") else r.stdout + "\n")
    if r.stderr:
        sys.stderr.write(r.stderr if r.stderr.endswith("\n") else r.stderr + "\n")
    if not r.success:
        err(r.message or "commit/push falhou.")
        return r.returncode if r.returncode not in (None, 0) else 1
    ok("Commit e push concluídos.")
    return 0
