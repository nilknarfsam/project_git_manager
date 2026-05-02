"""
Janela principal: seleção de projeto, ações Git, console de log.
O Git roda em uma thread de trabalho para a interface permanecer responsiva.
"""

from __future__ import annotations

import subprocess
import threading
import tkinter.filedialog as filedialog
from pathlib import Path

import customtkinter as ctk

from core import git_service, project_service
from ui.components import LogConsole


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gerenciador Git de Projetos")
        self.geometry("920x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._selected_path = ctk.StringVar(value="")
        self._project_names: list[str] = []
        self._busy = False

        self._build_layout()
        self._refresh_saved_projects()
        self._update_action_states()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        title = ctk.CTkLabel(
            self, text="Gerenciador Git de Projetos", font=ctk.CTkFont(size=22, weight="bold")
        )
        title.grid(row=0, column=0, pady=(16, 8), padx=20)

        # --- Seleção de projeto ---
        proj_frame = ctk.CTkFrame(self)
        proj_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=8)
        proj_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(proj_frame, text="Projeto").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        self._path_entry = ctk.CTkEntry(
            proj_frame,
            textvariable=self._selected_path,
            placeholder_text="Caminho da pasta do projeto",
        )
        self._path_entry.grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        btn_row = ctk.CTkFrame(proj_frame, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        self._btn_select_folder = ctk.CTkButton(btn_row, text="Escolher pasta", command=self._select_folder)
        self._btn_select_folder.pack(side="left", padx=4)
        self._btn_vscode = ctk.CTkButton(btn_row, text="Abrir no VS Code", command=self._open_vscode)
        self._btn_vscode.pack(side="left", padx=4)
        self._btn_save_project = ctk.CTkButton(btn_row, text="Salvar projeto", command=self._save_project_dialog)
        self._btn_save_project.pack(side="left", padx=4)

        ctk.CTkLabel(proj_frame, text="Projetos salvos").grid(row=2, column=0, padx=8, pady=(12, 4), sticky="w")
        self._saved_combo = ctk.CTkComboBox(proj_frame, values=[], command=self._on_saved_selected, width=400)
        self._saved_combo.grid(row=2, column=1, padx=4, pady=(12, 4), sticky="ew")

        # --- Ações Git ---
        git_frame = ctk.CTkFrame(self)
        git_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=8)
        git_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(git_frame, text="Ações Git", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=8, pady=6, sticky="w"
        )

        row1 = ctk.CTkFrame(git_frame, fg_color="transparent")
        row1.grid(row=1, column=0, columnspan=4, sticky="ew", padx=4, pady=4)
        self._btn_clone = ctk.CTkButton(row1, text="Clonar repositório", command=self._clone_dialog)
        self._btn_clone.pack(side="left", padx=4)
        self._btn_status = ctk.CTkButton(row1, text="Git status", command=self._git_status)
        self._btn_status.pack(side="left", padx=4)
        self._btn_pull = ctk.CTkButton(row1, text="Pull", command=self._git_pull)
        self._btn_pull.pack(side="left", padx=4)
        self._btn_commit = ctk.CTkButton(row1, text="Commit e push", command=self._commit_push_dialog)
        self._btn_commit.pack(side="left", padx=4)

        # --- Log ---
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(8, 16))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(log_frame, text="Saída do log").grid(row=0, column=0, padx=8, pady=4, sticky="w")
        self._log = LogConsole(log_frame)
        self._log.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

    def _on_close(self) -> None:
        self.destroy()

    def _ui(self, fn, *args, **kwargs) -> None:
        self.after(0, lambda: fn(*args, **kwargs))

    def _log_line(self, text: str, *, error: bool = False, success: bool = False) -> None:
        def go() -> None:
            self._log.append(text, error=error, success=success)

        self.after(0, go)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._ui(self._update_action_states)

    def _update_action_states(self) -> None:
        path_ok, _ = git_service.folder_exists(self._selected_path.get())
        repo_ok, _ = git_service.validate_git_repo(self._selected_path.get())
        busy = self._busy

        self._btn_status.configure(state=("disabled" if (not repo_ok or busy) else "normal"))
        self._btn_pull.configure(state=("disabled" if (not repo_ok or busy) else "normal"))
        self._btn_commit.configure(state=("disabled" if (not repo_ok or busy) else "normal"))
        self._btn_clone.configure(state=("disabled" if busy else "normal"))

        proj_state = "disabled" if busy else "normal"
        self._path_entry.configure(state=proj_state)
        self._btn_select_folder.configure(state=proj_state)
        self._btn_vscode.configure(state=proj_state)
        self._btn_save_project.configure(state=proj_state)
        self._saved_combo.configure(state=proj_state)

    def _select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Selecionar pasta do projeto")
        if folder:
            self._selected_path.set(str(Path(folder).resolve()))
            self._log_line(f"Pasta selecionada: {folder}\n")
            self._update_action_states()

    def _open_vscode(self) -> None:
        ok, msg = git_service.folder_exists(self._selected_path.get())
        if not ok:
            self._log_line(msg + "\n", error=True)
            return
        path = self._selected_path.get()
        try:
            subprocess.Popen(
                ["code", path],
                shell=False,
                cwd=path,
            )
            self._log_line(f"Abrindo VS Code em: {path}\n", success=True)
        except FileNotFoundError:
            self._log_line(
                "Comando 'code' não encontrado. Instale o VS Code e adicione-o ao PATH.\n",
                error=True,
            )
        except OSError as e:
            self._log_line(f"Não foi possível abrir o VS Code: {e}\n", error=True)

    def _save_project_dialog(self) -> None:
        ok, msg = git_service.folder_exists(self._selected_path.get())
        if not ok:
            self._log_line(msg + "\n", error=True)
            return

        dialog = ctk.CTkInputDialog(text="Nome do projeto:", title="Salvar projeto")
        name = dialog.get_input()
        if name is None or not str(name).strip():
            self._log_line("Salvamento cancelado.\n")
            return
        success, err = project_service.save_project(str(name).strip(), self._selected_path.get())
        if success:
            self._log_line(f"Projeto salvo: {name}\n", success=True)
            self._refresh_saved_projects()
        else:
            self._log_line(err + "\n", error=True)

    def _refresh_saved_projects(self) -> None:
        projects = project_service.get_projects()
        self._project_names = [p["name"] for p in projects]
        # Evita disparar o callback de seleção ao reconstruir a lista
        self._saved_combo.configure(command=None)
        self._saved_combo.configure(values=self._project_names or ["(nenhum)"])
        if self._project_names:
            self._saved_combo.set(self._project_names[0])
        else:
            self._saved_combo.set("(nenhum)")
        self._saved_combo.configure(command=self._on_saved_selected)

    def _on_saved_selected(self, choice: str) -> None:
        if choice in ("(nenhum)", "") or not self._project_names:
            return
        for p in project_service.get_projects():
            if p["name"] == choice:
                self._selected_path.set(p["path"])
                self._log_line(f"Projeto carregado: {choice} → {p['path']}\n")
                self._update_action_states()
                break

    def _clone_dialog(self) -> None:
        top = ctk.CTkToplevel(self)
        top.title("Clonar repositório")
        top.geometry("560x280")
        top.transient(self)
        top.grab_set()

        url_var = ctk.StringVar()
        dest_var = ctk.StringVar()

        ctk.CTkLabel(top, text="URL do repositório").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ctk.CTkEntry(top, textvariable=url_var, width=400).grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top, text="Pasta final (será criada)").grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        dest_hint = ctk.CTkLabel(
            top,
            text="Caminho completo, ex.: C:\\src\\projects\\auratime\n"
            "(a pasta pai deve existir; se a pasta final não existir, o Git cria. "
            "Se já existir e for um repo Git, sincroniza com o remoto: fetch, reset e clean.)",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            justify="left",
        )
        dest_hint.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 4), sticky="w")

        dest_row = ctk.CTkFrame(top, fg_color="transparent")
        dest_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=4)
        dest_row.grid_columnconfigure(0, weight=1)
        dest_entry = ctk.CTkEntry(
            dest_row,
            textvariable=dest_var,
            placeholder_text="Ex.: C:\\src\\projects\\auratime",
        )
        dest_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        def browse_dest() -> None:
            d = filedialog.askdirectory(title="Escolha a pasta pai (depois inclua o nome do repo no campo)")
            if d:
                dest_var.set(str(Path(d).resolve()))

        ctk.CTkButton(dest_row, text="Procurar…", width=100, command=browse_dest).grid(row=0, column=1)

        def do_clone() -> None:
            url = url_var.get().strip()
            dest = dest_var.get().strip()
            top.destroy()
            if not url or not dest:
                self._log_line("Clone cancelado: URL e pasta de destino são obrigatórios.\n", error=True)
                return

            dest_resolved = str(Path(dest).expanduser().resolve())
            folder_name = Path(dest_resolved).name
            parent = str(Path(dest_resolved).parent)

            def worker() -> None:
                self._set_busy(True)
                will_sync = Path(dest_resolved).exists()
                self._log_line("Iniciando clone…\n")
                self._log_line(f"URL: {url}\n")
                self._log_line(f"Destino: {dest_resolved}\n")
                self._log_line(f"Diretório de trabalho (cwd): {parent}\n")

                if will_sync:
                    self._log_line(
                        "Pasta já existe. Sincronizando com o repositório remoto...\n",
                        error=False,
                    )
                    self._log_line(f"> git fetch / reset --hard / clean em: {dest_resolved}\n")
                else:
                    self._log_line(f"> git clone {url} {folder_name}\n")
                    self._log_line("Clonando repositório… (aguarde)\n")

                rc, out, err = git_service.clone_repo(url, dest_resolved, on_line=None)
                if (out or "").strip():
                    self._log_line(out if out.endswith("\n") else out + "\n", error=False)
                if (err or "").strip():
                    self._log_line(err if err.endswith("\n") else err + "\n", error=(rc != 0))

                if rc == 0:
                    if will_sync:
                        self._log_line("Repositório sincronizado com sucesso.\n", success=True)
                    else:
                        self._log_line("Repositório clonado com sucesso.\n", success=True)
                    self._log_line(f"Pasta do projeto atualizada para: {dest_resolved}\n", success=True)
                    self._ui(self._selected_path.set, dest_resolved)
                    self._ui(self._update_action_states)
                else:
                    if will_sync:
                        self._log_line("\nFalha ao sincronizar o repositório.\n", error=True)
                    else:
                        self._log_line("\nFalha ao clonar repositório.\n", error=True)
                    self._log_line(f"Código de saída: {rc}\n", error=True)
                self._set_busy(False)

            threading.Thread(target=worker, daemon=True).start()

        btn_bar = ctk.CTkFrame(top, fg_color="transparent")
        btn_bar.grid(row=4, column=0, columnspan=2, pady=16)
        ctk.CTkButton(btn_bar, text="Clonar", command=do_clone).pack(side="left", padx=8)
        ctk.CTkButton(btn_bar, text="Cancelar", command=top.destroy).pack(side="left", padx=8)

    def _commit_push_dialog(self) -> None:
        ok, _ = git_service.validate_git_repo(self._selected_path.get())
        if not ok:
            self._log_line("Selecione uma pasta válida de repositório Git.\n", error=True)
            return

        dialog = ctk.CTkInputDialog(text="Mensagem do commit:", title="Commit e push")
        msg = dialog.get_input()
        if msg is None or not str(msg).strip():
            self._log_line("Commit cancelado (mensagem vazia).\n")
            return

        path = self._selected_path.get()

        def worker() -> None:
            self._set_busy(True)

            def on_line(line: str, is_err: bool) -> None:
                self._log_line(line, error=is_err)

            self._log_line("> git add . && git commit && git push\n")
            rc, _, _ = git_service.commit_and_push(path, str(msg).strip(), on_line=on_line)
            if rc == 0:
                self._log_line("Commit realizado com sucesso.\n", success=True)
            else:
                self._log_line("Add, commit ou push falhou (veja a saída acima).\n", error=True)
            self._set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def _git_status(self) -> None:
        ok, msg = git_service.validate_git_repo(self._selected_path.get())
        if not ok:
            self._log_line(msg + "\n", error=True)
            return
        path = self._selected_path.get()

        def worker() -> None:
            self._set_busy(True)
            self._log_line("> git status\n")

            def on_line(line: str, is_err: bool) -> None:
                self._log_line(line, error=is_err)

            rc, _, _ = git_service.get_status(path, on_line=on_line)
            if rc != 0:
                self._log_line("git status reportou um erro.\n", error=True)
            self._set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def _git_pull(self) -> None:
        ok, msg = git_service.validate_git_repo(self._selected_path.get())
        if not ok:
            self._log_line(msg + "\n", error=True)
            return
        path = self._selected_path.get()

        def worker() -> None:
            self._set_busy(True)
            self._log_line("> git pull\n")

            def on_line(line: str, is_err: bool) -> None:
                self._log_line(line, error=is_err)

            rc, _, _ = git_service.pull_repo(path, on_line=on_line)
            if rc == 0:
                self._log_line("Projeto atualizado.\n", success=True)
            else:
                self._log_line("git pull falhou.\n", error=True)
            self._set_busy(False)

        threading.Thread(target=worker, daemon=True).start()


def run_app() -> None:
    app = MainWindow()
    app.mainloop()
