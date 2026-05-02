"""
Gerenciador Git de Projetos — ponto de entrada.
Execute nesta pasta: python main.py
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
