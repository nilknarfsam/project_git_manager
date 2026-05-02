"""Subcomando: resumo do repositório (somente leitura)."""

from __future__ import annotations

import argparse
from pathlib import Path

from project_git_core.git.service import get_repository_overview

def register(subparsers) -> None:
    p = subparsers.add_parser(
        "overview",
        help="Mostra branch, limpeza, último commit e avisos.",
    )
    p.add_argument("path", help="Pasta do projeto (repositório Git ou pasta qualquer).")
    p.set_defaults(_handler=run)


def _project_label(overview_path: str, arg_path: str) -> str:
    raw = (overview_path or "").strip()
    if raw:
        return Path(raw).name
    return Path(arg_path).expanduser().resolve().name if arg_path.strip() else "—"


def run(args: argparse.Namespace) -> int:
    o = get_repository_overview(args.path)
    name = _project_label(o.path, args.path)

    if not o.is_git_repo:
        if "Nenhuma pasta" in (o.message or ""):
            print(f"Projeto: {name}")
            print(f"Status: ⚠ {o.message}")
            return 0
        print(f"Projeto: {name}")
        print(f"Branch: —")
        print(f"Status: ❌ {o.message or 'Não é repositório Git.'}")
        print(f"Último commit: —")
        return 1

    branch_disp = o.branch if o.branch != "-" else "—"
    last_disp = o.last_commit if o.last_commit else "—"

    if o.branch == "-" and o.message and o.message != "Repositório carregado com sucesso.":
        short = o.message if len(o.message) <= 120 else o.message[:117] + "…"
        status_line = f"⚠ {short}"
    elif o.has_changes:
        status_line = "⚠ Alterações pendentes"
    else:
        status_line = "✔ Limpo"

    print(f"Projeto: {name}")
    print(f"Branch: {branch_disp}")
    print(f"Status: {status_line}")
    print(f"Último commit: {last_disp}")
    return 0
