"""
Gerenciador Git de Projetos — ponto de entrada (legado CustomTkinter).

Execute a partir desta pasta:
  pip install -r requirements.txt
  python main.py

Na raiz do repositório: cd legacy_python/customtkinter_app
"""

import sys
from pathlib import Path

# Raiz do app legado (ui/, core/) e raiz do monorepo (para importar project_git_core)
_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _ROOT.parent.parent
_PACKAGES_CORE = (_REPO_ROOT / "packages" / "core").resolve()
for p in (str(_PACKAGES_CORE), str(_ROOT)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_PACKAGES_CORE))

from ui.main_window import run_app  # noqa: E402

if __name__ == "__main__":
    run_app()
