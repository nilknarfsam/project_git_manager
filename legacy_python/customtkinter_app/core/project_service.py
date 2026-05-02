"""
Projetos favoritos persistidos em data/projects.json (ao lado de core/ e ui/).
"""

from __future__ import annotations

import json
from pathlib import Path


def _json_path() -> Path:
    # legacy_python/customtkinter_app/data/projects.json
    base = Path(__file__).resolve().parent.parent / "data" / "projects.json"
    base.parent.mkdir(parents=True, exist_ok=True)
    return base


def load_projects() -> list[dict[str, str]]:
    path = _json_path()
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
        return []
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        out: list[dict[str, str]] = []
        for item in data:
            if isinstance(item, dict) and "name" in item and "path" in item:
                out.append({"name": str(item["name"]), "path": str(item["path"])})
        return out
    except (json.JSONDecodeError, OSError):
        return []


def save_project(name: str, path: str) -> tuple[bool, str]:
    """
    Adiciona ou atualiza um projeto pelo nome. Evita caminhos duplicados (mesmo caminho normalizado).
    """
    name = name.strip()
    path_norm = str(Path(path).expanduser().resolve())
    if not name:
        return False, "Informe um nome de projeto."
    if not path_norm:
        return False, "Informe um caminho válido."

    projects = load_projects()
    # Remove entradas com o mesmo caminho
    filtered = [p for p in projects if Path(p["path"]).resolve() != Path(path_norm)]
    # Remove o mesmo nome para substituir
    filtered = [p for p in filtered if p["name"].lower() != name.lower()]
    filtered.append({"name": name, "path": path_norm})

    try:
        _json_path().write_text(
            json.dumps(filtered, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        return False, f"Não foi possível salvar: {e}"
    return True, ""


def get_projects() -> list[dict[str, str]]:
    return load_projects()
