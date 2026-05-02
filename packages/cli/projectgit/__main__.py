"""Permite: python -m projectgit (a partir de packages/cli)."""

from __future__ import annotations

import sys

from projectgit.main import main

if __name__ == "__main__":
    sys.exit(main())
