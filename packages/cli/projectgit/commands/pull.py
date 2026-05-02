"""Subcomando: git pull."""

from __future__ import annotations

import argparse
import sys

from project_git_core.git.service import pull_repo

from projectgit.out import err


def register(subparsers) -> None:
    p = subparsers.add_parser("pull", help="Executa git pull no repositório.")
    p.add_argument("path", help="Pasta raiz do repositório Git.")
    p.set_defaults(_handler=run)


def run(args: argparse.Namespace) -> int:
    r = pull_repo(args.path)
    if r.stdout:
        sys.stdout.write(r.stdout if r.stdout.endswith("\n") else r.stdout + "\n")
    if r.stderr:
        sys.stderr.write(r.stderr if r.stderr.endswith("\n") else r.stderr + "\n")
    if not r.success:
        err(r.message or "git pull falhou.")
        return r.returncode if r.returncode not in (None, 0) else 1
    return 0
