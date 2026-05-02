"""Subcomando: clone ou sync se a pasta já existir como repo Git."""

from __future__ import annotations

import argparse
import sys

from project_git_core.git.service import clone_repo

from projectgit.out import err, ok


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "clone",
        help="Clona URL na pasta destino (ou sincroniza se já for repositório Git).",
    )
    p.add_argument("url", help="URL do repositório remoto.")
    p.add_argument("destination", help="Caminho completo da pasta do clone.")
    p.set_defaults(_handler=run)


def run(args: argparse.Namespace) -> int:
    r = clone_repo(args.url, args.destination)
    if r.stdout:
        sys.stdout.write(r.stdout if r.stdout.endswith("\n") else r.stdout + "\n")
    if r.stderr:
        sys.stderr.write(r.stderr if r.stderr.endswith("\n") else r.stderr + "\n")
    if not r.success:
        err(r.message or "Clone ou sincronização falhou.")
        return r.returncode if r.returncode not in (None, 0) else 1
    ok("Operação concluída com sucesso.")
    return 0
