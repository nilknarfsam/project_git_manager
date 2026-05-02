"""
Gerenciador Git de Projetos — ponto de entrada (legado CustomTkinter).

Execute a partir desta pasta:
  pip install -r requirements.txt
  python main.py

Na raiz do repositório: cd legacy_python/customtkinter_app
"""

import sys
from pathlib import Path

# Garante que a raiz do pacote esteja em sys.path ao rodar como script
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ui.main_window import run_app  # noqa: E402

if __name__ == "__main__":
    run_app()
