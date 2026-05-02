"""Saída formatada para o terminal (UTF-8, prefixos visuais)."""

from __future__ import annotations

import sys


def ok(msg: str) -> None:
    print(f"✔ {msg}")


def warn(msg: str) -> None:
    print(f"⚠ {msg}")


def err(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(f"• {msg}")
