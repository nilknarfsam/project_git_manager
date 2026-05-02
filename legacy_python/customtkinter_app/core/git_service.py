"""
Operações Git via subprocess. Caminhos são normalizados para compatibilidade com Windows.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable


def _normalize_path(path: str) -> str:
    return str(Path(path).resolve())


def validate_git_repo(path: str) -> tuple[bool, str]:
    """
    Retorna (ok, mensagem). ok é True se o caminho existe e contém .git.
    """
    if not path or not path.strip():
        return False, "Nenhuma pasta selecionada."
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        return False, "A pasta selecionada não existe."
    if not resolved.is_dir():
        return False, "O caminho não é uma pasta."
    git_dir = resolved / ".git"
    if not git_dir.exists():
        return False, "Esta pasta não é um repositório Git (.git não encontrado)."
    return True, ""


def folder_exists(path: str) -> tuple[bool, str]:
    if not path or not path.strip():
        return False, "Nenhuma pasta selecionada."
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        return False, "A pasta selecionada não existe."
    if not resolved.is_dir():
        return False, "O caminho não é uma pasta."
    return True, ""


def git_executable_available() -> tuple[bool, str]:
    """Verifica se o executável git está disponível no PATH (sem abrir janela de console)."""
    if shutil.which("git"):
        return True, ""
    return (
        False,
        "O Git não foi encontrado no PATH. Instale o Git for Windows e confira se "
        "'git' está acessível no terminal (reinicie o app após alterar o PATH).",
    )


def run_git_command(
    command: list[str],
    path: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[int, str, str]:
    """
    Executa git com os argumentos informados (sem o prefixo 'git') no diretório path.
    on_line(linha, é_stderr): callback opcional para saída em fluxo.
    Retorna (código_de_retorno, stdout, stderr).
    """
    cwd = _normalize_path(path)
    cmd = ["git", *command]
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
        )
    except FileNotFoundError:
        return (
            -1,
            "",
            "O comando 'git' não foi encontrado. Instale o Git e adicione-o ao PATH do sistema.",
        )
    out_chunks: list[str] = []
    err_chunks: list[str] = []

    assert proc.stdout is not None
    assert proc.stderr is not None

    stdout, stderr = proc.communicate()
    if stdout:
        out_chunks.append(stdout)
        if on_line:
            for line in stdout.splitlines():
                on_line(line + "\n", False)
    if stderr:
        err_chunks.append(stderr)
        if on_line:
            for line in stderr.splitlines():
                on_line(line + "\n", True)

    full_out = "".join(out_chunks)
    full_err = "".join(err_chunks)
    return proc.returncode or 0, full_out, full_err


def get_current_branch(path: str) -> tuple[bool, str]:
    """
    Retorna (ok, nome_da_branch). Se ok for False, a string contém mensagem de erro ou stderr.
    Em HEAD destacado, ok é False com aviso explícito (rev-parse retorna "HEAD").
    """
    rc, out, err = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], path)
    if rc != 0:
        detail = (err or out).strip() or f"código {rc}"
        return False, detail
    name = (out or "").strip()
    if not name:
        return False, "Branch vazia."
    if name == "HEAD":
        return (
            False,
            "HEAD destacado: não há branch nomeada. Faça checkout de uma branch "
            "(ex.: git checkout main).",
        )
    return True, name


def get_last_commit(path: str) -> tuple[bool, str]:
    """Último commit em formato curto: hash - assunto (git log -1)."""
    rc, out, err = run_git_command(
        ["log", "-1", "--pretty=format:%h - %s"],
        path,
    )
    if rc != 0:
        detail = (err or out).strip() or f"código {rc}"
        return False, detail
    text = (out or "").strip()
    return True, text if text else "-"


def has_pending_changes(path: str) -> tuple[bool, bool]:
    """
    Retorna (ok, tem_alteracoes). tem_alteracoes só é confiável se ok for True.
    """
    rc, out, err = run_git_command(["status", "--porcelain"], path)
    if rc != 0:
        return False, False
    return True, bool((out or "").strip())


def get_repository_overview(path: str) -> dict[str, object]:
    """
    Resumo do repositório na pasta indicada (sem efeitos colaterais além de leitura Git).

    Retorna dicionário com chaves: is_git_repo, branch, has_changes, last_commit, message.
    """
    not_git: dict[str, object] = {
        "is_git_repo": False,
        "branch": "-",
        "has_changes": False,
        "last_commit": "-",
        "message": "A pasta selecionada não é um repositório Git.",
    }

    raw = (path or "").strip()
    if not raw:
        out = dict(not_git)
        out["message"] = "Nenhuma pasta selecionada."
        return out

    ok_repo, _msg = validate_git_repo(raw)
    if not ok_repo:
        return dict(not_git)

    ok_lc, last_txt = get_last_commit(raw)
    last_commit = last_txt if ok_lc else "-"

    ok_br, branch_or_err = get_current_branch(raw)
    ok_st, dirty = has_pending_changes(raw)
    has_ch = bool(dirty) if ok_st else False

    if not ok_br:
        return {
            "is_git_repo": True,
            "branch": "-",
            "has_changes": has_ch,
            "last_commit": last_commit,
            "message": branch_or_err,
        }

    return {
        "is_git_repo": True,
        "branch": branch_or_err,
        "has_changes": has_ch,
        "last_commit": last_commit,
        "message": "Repositório carregado com sucesso.",
    }


def force_sync_repo(
    path: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[bool, str]:
    """
    Força o repositório local a alinhar com o remoto na branch atual:
    fetch origin, reset --hard origin/<branch>, clean -fd.

    Sobrescreve alterações locais e remove arquivos não rastreados.
    Retorna (ok, log_completo_com_saida_dos_comandos).
    """
    is_repo, msg = validate_git_repo(path)
    if not is_repo:
        p = Path(path).expanduser().resolve()
        if p.exists() and p.is_dir():
            return False, "A pasta existe, mas não é um repositório Git."
        return False, msg or "A pasta existe, mas não é um repositório Git."

    rc, bout, berr = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], path, on_line=on_line)
    branch = (bout or "").strip()
    if rc != 0 or not branch:
        detail = (berr or bout or "").strip()
        tail = f"\n{detail}" if detail else ""
        return False, f"Não foi possível detectar a branch atual.{tail}"
    if branch == "HEAD":
        return (
            False,
            "Repositório em HEAD destacado; faça checkout de uma branch antes de sincronizar.",
        )

    commands: list[list[str]] = [
        ["fetch", "origin"],
        ["reset", "--hard", f"origin/{branch}"],
        ["clean", "-fd"],
    ]

    output_log = ""
    for cmd in commands:
        line_cmd = f"> git {' '.join(cmd)}\n"
        output_log += line_cmd
        if on_line:
            on_line(line_cmd, False)

        rc, out, err = run_git_command(cmd, path, on_line=on_line)
        block = ""
        if (out or "").strip():
            block += out if out.endswith("\n") else out + "\n"
        if (err or "").strip():
            block += err if err.endswith("\n") else err + "\n"
        output_log += block

        if rc != 0:
            fail = (err or out or "").strip() or f"código {rc}"
            return False, output_log + f"\n(comando falhou: {fail})\n"

    return True, output_log


def clone_repo(
    repo_url: str,
    destination_path: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[int, str, str]:
    """
    Clona em destination_path (caminho completo da pasta que será criada).

    Executa na pasta pai: git clone <repo_url> <nome_da_pasta_final>
    (padrão recomendado no Windows; evita passar caminho absoluto longo como último argumento).

    Se destination_path já existir e for um repositório Git, executa force_sync_repo
    (fetch, reset --hard origin/<branch>, clean -fd) em vez de clonar de novo.
    """
    repo_url = (repo_url or "").strip()
    dest_raw = (destination_path or "").strip()

    if not repo_url:
        return -1, "", "A URL do repositório não foi informada."
    if not dest_raw:
        return -1, "", "A pasta de destino não foi informada."

    destination = Path(dest_raw).expanduser().resolve()
    parent_folder = destination.parent
    folder_name = destination.name

    if not folder_name or folder_name in (".", ".."):
        return (
            -1,
            "",
            "Informe o caminho completo da pasta do clone, incluindo o nome da pasta "
            "que será criada (ex.: C:\\src\\projects\\auratime).",
        )

    if any(sep in folder_name for sep in ("/", "\\")):
        return (
            -1,
            "",
            "O nome da pasta final não pode conter barras. Use um caminho como "
            "C:\\src\\projects\\auratime (a última parte é só o nome da pasta).",
        )

    if not parent_folder.exists():
        return -1, "", f"A pasta pai não existe: {parent_folder}"
    if not parent_folder.is_dir():
        return -1, "", f"A pasta pai não é um diretório: {parent_folder}"

    if destination.exists():
        sync_ok, sync_log = force_sync_repo(str(destination), on_line=on_line)
        if sync_ok:
            return 0, sync_log, ""
        return -1, "", sync_log

    ok_git, git_msg = git_executable_available()
    if not ok_git:
        return -1, "", git_msg

    return run_git_command(
        ["clone", repo_url, folder_name],
        str(parent_folder),
        on_line=on_line,
    )


def get_status(path: str, on_line: Callable[[str, bool], None] | None = None) -> tuple[int, str, str]:
    return run_git_command(["status"], path, on_line=on_line)


def pull_repo(path: str, on_line: Callable[[str, bool], None] | None = None) -> tuple[int, str, str]:
    return run_git_command(["pull"], path, on_line=on_line)


def commit_and_push(
    path: str,
    message: str,
    on_line: Callable[[str, bool], None] | None = None,
) -> tuple[int, str, str]:
    """git add ., commit -m, push. Retorna o código da última etapa que falhou, ou 0 se tudo der certo."""
    rc, out, err = run_git_command(["add", "."], path, on_line=on_line)
    if rc != 0:
        return rc, out, err

    rc, out, err = run_git_command(["commit", "-m", message], path, on_line=on_line)
    if rc != 0:
        return rc, out, err

    return run_git_command(["push"], path, on_line=on_line)
