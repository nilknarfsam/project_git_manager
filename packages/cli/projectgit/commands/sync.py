"""Subcomando: sincronização forçada com o remoto (fetch + reset --hard + clean)."""

from __future__ import annotations

import argparse

from project_git_core.git.service import force_sync_repo

from projectgit.out import err, ok, warn


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "sync",
        help="Alinha o repo com origin (destructivo: descarta alterações locais).",
    )
    p.add_argument("path", help="Pasta raiz do repositório Git.")
    p.set_defaults(_handler=run)


def run(args: argparse.Namespace) -> int:
    warn("Esta operação pode descartar commits locais e arquivos não rastreados.")
    r = force_sync_repo(args.path)
    if r.stdout:
        print(r.stdout, end="" if r.stdout.endswith("\n") else "\n")
    if not r.success:
        err(r.message or "Sincronização falhou.")
        return r.returncode if r.returncode not in (None, 0) else 1
    ok("Repositório sincronizado com o remoto.")
    return 0
