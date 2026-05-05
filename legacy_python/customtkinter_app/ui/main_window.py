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
        self.geometry("920x820")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._selected_path = ctk.StringVar(value="")
        self._project_names: list[str] = []
        self._busy = False
        self._overview_loading = False

        self._path_overview_after_id: str | None = None
        self._build_layout()

        def _on_path_var_write(*_args: object) -> None:
            self._ui(self._update_current_project_display)
            self._schedule_overview_refresh_debounced()

        self._selected_path.trace_add("write", _on_path_var_write)
        self._refresh_saved_projects()
        self._update_action_states()
        self._update_current_project_display()
        self._update_status_bar()
        self.refresh_repository_overview()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        title = ctk.CTkLabel(
            self, text="Gerenciador Git de Projetos", font=ctk.CTkFont(size=22, weight="bold")
        )
        title.grid(row=0, column=0, pady=(18, 10), padx=20)

        # --- Resumo do repositório ---
        overview_card = ctk.CTkFrame(self, corner_radius=10, border_width=1, border_color=("gray70", "gray30"))
        overview_card.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        overview_card.grid_columnconfigure(1, weight=1)

        title_row = ctk.CTkFrame(overview_card, fg_color="transparent")
        title_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(10, 4))
        title_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            title_row,
            text="Resumo do repositório",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        self._btn_refresh_overview = ctk.CTkButton(
            title_row,
            text="Atualizar resumo",
            width=150,
            command=self.refresh_repository_overview,
        )
        self._btn_refresh_overview.grid(row=0, column=1, padx=(8, 4), pady=0)

        self._overview_hint = ctk.CTkLabel(
            overview_card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#93c5fd",
            anchor="w",
        )
        self._overview_hint.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 6))

        neutral = ("gray20", "#D1D5DB")
        ctk.CTkLabel(overview_card, text="Projeto:", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, padx=(12, 8), pady=2, sticky="nw"
        )
        self._ov_project_val = ctk.CTkLabel(overview_card, text="—", anchor="w", text_color=neutral)
        self._ov_project_val.grid(row=2, column=1, padx=4, pady=2, sticky="ew")
        ctk.CTkLabel(overview_card, text="Branch:", font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, padx=(12, 8), pady=2, sticky="w"
        )
        self._ov_branch_val = ctk.CTkLabel(overview_card, text="—", anchor="w", text_color=neutral)
        self._ov_branch_val.grid(row=3, column=1, padx=4, pady=2, sticky="w")
        ctk.CTkLabel(overview_card, text="Modificados:", font=ctk.CTkFont(weight="bold")).grid(
            row=4, column=0, padx=(12, 8), pady=2, sticky="w"
        )
        self._ov_modified_val = ctk.CTkLabel(overview_card, text="—", anchor="w", text_color=neutral)
        self._ov_modified_val.grid(row=4, column=1, padx=4, pady=2, sticky="w")
        ctk.CTkLabel(overview_card, text="Não rastreados:", font=ctk.CTkFont(weight="bold")).grid(
            row=5, column=0, padx=(12, 8), pady=2, sticky="w"
        )
        self._ov_untracked_val = ctk.CTkLabel(overview_card, text="—", anchor="w", text_color=neutral)
        self._ov_untracked_val.grid(row=5, column=1, padx=4, pady=2, sticky="w")
        ctk.CTkLabel(overview_card, text="Status:", font=ctk.CTkFont(weight="bold")).grid(
            row=6, column=0, padx=(12, 8), pady=2, sticky="w"
        )
        self._ov_status_val = ctk.CTkLabel(overview_card, text="—", anchor="w", text_color="gray60")
        self._ov_status_val.grid(row=6, column=1, padx=4, pady=2, sticky="w")
        ctk.CTkLabel(overview_card, text="Último commit:", font=ctk.CTkFont(weight="bold")).grid(
            row=7, column=0, padx=(12, 8), pady=(2, 6), sticky="nw"
        )
        self._ov_last_commit_val = ctk.CTkLabel(
            overview_card,
            text="—",
            anchor="w",
            justify="left",
            wraplength=700,
            text_color=neutral,
        )
        self._ov_last_commit_val.grid(row=7, column=1, padx=4, pady=(2, 6), sticky="ew")
        ctk.CTkLabel(overview_card, text="Arquivos alterados", font=ctk.CTkFont(weight="bold")).grid(
            row=8, column=0, columnspan=2, padx=12, pady=(4, 4), sticky="w"
        )
        self._ov_files_box = ctk.CTkTextbox(
            overview_card,
            height=108,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none",
            activate_scrollbars=True,
        )
        self._ov_files_box.grid(row=9, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        overview_card.grid_rowconfigure(9, weight=0)

        # --- Seleção de projeto ---
        proj_frame = ctk.CTkFrame(self, corner_radius=10, border_width=1, border_color=("gray70", "gray30"))
        proj_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        proj_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            proj_frame,
            text="Projeto e pastas",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 6), sticky="w")

        banner = ctk.CTkFrame(proj_frame, fg_color=("gray88", "gray22"), corner_radius=8)
        banner.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        banner.grid_columnconfigure(0, weight=1)
        self._lbl_current_project = ctk.CTkLabel(
            banner,
            text="Projeto atual: —",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        self._lbl_current_project.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")
        self._lbl_current_project_sub = ctk.CTkLabel(
            banner,
            text="Selecione uma pasta ou um projeto salvo.",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            anchor="w",
        )
        self._lbl_current_project_sub.grid(row=1, column=0, padx=12, pady=(2, 10), sticky="ew")

        ctk.CTkLabel(proj_frame, text="Caminho da pasta").grid(row=2, column=0, padx=10, pady=6, sticky="w")
        self._path_entry = ctk.CTkEntry(
            proj_frame,
            textvariable=self._selected_path,
            placeholder_text="Caminho da pasta do projeto",
        )
        self._path_entry.grid(row=2, column=1, padx=4, pady=6, sticky="ew")

        btn_row = ctk.CTkFrame(proj_frame, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=6, pady=(4, 8))
        self._btn_select_folder = ctk.CTkButton(btn_row, text="Escolher pasta", command=self._select_folder)
        self._btn_select_folder.pack(side="left", padx=4)
        self._btn_vscode = ctk.CTkButton(btn_row, text="Abrir no VS Code", command=self._open_vscode)
        self._btn_vscode.pack(side="left", padx=4)
        self._btn_save_project = ctk.CTkButton(btn_row, text="Salvar projeto", command=self._save_project_dialog)
        self._btn_save_project.pack(side="left", padx=4)

        ctk.CTkLabel(proj_frame, text="Projetos salvos").grid(row=4, column=0, padx=10, pady=(4, 4), sticky="w")
        self._saved_combo = ctk.CTkComboBox(proj_frame, values=[], command=self._on_saved_selected, width=400)
        self._saved_combo.grid(row=4, column=1, padx=4, pady=(4, 10), sticky="ew")

        # --- Ações Git ---
        git_frame = ctk.CTkFrame(self, corner_radius=10, border_width=1, border_color=("gray70", "gray30"))
        git_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        git_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(git_frame, text="Ações Git", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=10, pady=(10, 6), sticky="w"
        )

        row1 = ctk.CTkFrame(git_frame, fg_color="transparent")
        row1.grid(row=1, column=0, columnspan=4, sticky="ew", padx=8, pady=(4, 10))
        self._btn_clone = ctk.CTkButton(row1, text="Clonar repositório", command=self._clone_dialog)
        self._btn_clone.pack(side="left", padx=4)
        self._btn_status = ctk.CTkButton(row1, text="Git status", command=self._git_status)
        self._btn_status.pack(side="left", padx=4)
        self._btn_pull = ctk.CTkButton(row1, text="Pull", command=self._git_pull)
        self._btn_pull.pack(side="left", padx=4)
        self._btn_commit = ctk.CTkButton(row1, text="Commit e push", command=self._commit_push_dialog)
        self._btn_commit.pack(side="left", padx=4)

        # --- Log ---
        log_frame = ctk.CTkFrame(self, corner_radius=10, border_width=1, border_color=("gray70", "gray30"))
        log_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 8))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(log_frame, text="Saída do log", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 6), sticky="w"
        )
        self._log = LogConsole(log_frame)
        self._log.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 10))

        # --- Barra de status (Git / resumo) ---
        status_wrap = ctk.CTkFrame(self, fg_color="transparent")
        status_wrap.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 14))
        status_wrap.grid_columnconfigure(0, weight=1)
        self._status_bar = ctk.CTkFrame(status_wrap, corner_radius=8, fg_color=("gray85", "gray25"))
        self._status_bar.grid(row=0, column=0, sticky="ew")
        self._status_label = ctk.CTkLabel(
            self._status_bar,
            text="Pronto",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray35", "gray75"),
        )
        self._status_label.pack(fill="x", padx=14, pady=8)

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
        self._ui(self._update_status_bar)

    def _update_status_bar(self) -> None:
        if self._busy:
            self._status_label.configure(
                text="Executando comando Git…",
                text_color="#93c5fd",
            )
        elif self._overview_loading:
            self._status_label.configure(
                text="Atualizando resumo do repositório…",
                text_color="#93c5fd",
            )
        else:
            self._status_label.configure(
                text="Pronto",
                text_color=("gray35", "gray75"),
            )

    def _schedule_overview_refresh_debounced(self) -> None:
        if self._path_overview_after_id is not None:
            self.after_cancel(self._path_overview_after_id)
        self._path_overview_after_id = self.after(550, self._debounced_refresh_overview)

    def _debounced_refresh_overview(self) -> None:
        self._path_overview_after_id = None
        if self._busy or self._overview_loading:
            return
        p = self._selected_path.get().strip()
        if not p:
            return
        ok, _ = git_service.folder_exists(p)
        if not ok:
            return
        self.refresh_repository_overview()

    def _cancel_debounced_overview(self) -> None:
        if self._path_overview_after_id is not None:
            self.after_cancel(self._path_overview_after_id)
            self._path_overview_after_id = None

    def _set_overview_files_text(self, lines: list[str] | None) -> None:
        box = self._ov_files_box
        box.configure(state="normal")
        box.delete("1.0", "end")
        if lines:
            box.insert("1.0", "\n".join(lines))
        else:
            box.insert("1.0", "—")
        box.configure(state="disabled")

    def _update_current_project_display(self) -> None:
        raw = self._selected_path.get().strip()
        if not raw:
            self._lbl_current_project.configure(text="Projeto atual: —", text_color="gray60")
            self._lbl_current_project_sub.configure(
                text="Selecione uma pasta ou um projeto salvo.",
                text_color="gray60",
            )
            return
        p = Path(raw)
        name = p.name or raw
        self._lbl_current_project.configure(
            text=f"Projeto atual: {name}",
            text_color=("gray10", "#F3F4F6"),
        )
        disp = str(p)
        if len(disp) > 88:
            disp = "…" + disp[-85:]
        self._lbl_current_project_sub.configure(text=disp, text_color="gray60")

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
        if hasattr(self, "_btn_refresh_overview"):
            self._btn_refresh_overview.configure(
                state="disabled" if (busy or self._overview_loading) else "normal"
            )

    def _apply_repository_overview_ui(
        self,
        *,
        folder_name: str,
        branch: str,
        last_commit: str,
        status_text: str,
        status_color: str,
        modified_display: str | None,
        untracked_display: str | None,
        changed_files: list[str] | None,
    ) -> None:
        neutral = ("gray20", "#D1D5DB")
        self._ov_project_val.configure(text=folder_name, text_color=neutral)
        self._ov_branch_val.configure(text=branch, text_color=neutral)
        self._ov_last_commit_val.configure(text=last_commit, text_color=neutral)
        self._ov_status_val.configure(text=status_text, text_color=status_color)
        mod_disp = modified_display if modified_display is not None else "—"
        unt_disp = untracked_display if untracked_display is not None else "—"
        self._ov_modified_val.configure(text=mod_disp, text_color=neutral)
        self._ov_untracked_val.configure(text=unt_disp, text_color=neutral)
        self._set_overview_files_text(changed_files)

    def _finish_repository_overview(self, folder_name: str, data: dict) -> None:
        self._overview_loading = False
        self._overview_hint.configure(text="")
        self._update_action_states()
        self._update_status_bar()

        is_git = bool(data.get("is_git_repo"))
        branch = str(data.get("branch", "-"))
        last_c = str(data.get("last_commit", "-"))
        has_ch = bool(data.get("has_changes"))
        message = str(data.get("message", ""))
        mod_n = int(data.get("modified_count", 0) or 0)
        unt_n = int(data.get("untracked_count", 0) or 0)
        files = list(data.get("changed_files") or [])

        if not is_git:
            msg = message
            if "Nenhuma pasta" in msg:
                self._apply_repository_overview_ui(
                    folder_name="—",
                    branch="—",
                    last_commit="—",
                    status_text="—",
                    status_color="gray60",
                    modified_display=None,
                    untracked_display=None,
                    changed_files=None,
                )
            else:
                self._apply_repository_overview_ui(
                    folder_name=folder_name,
                    branch="-",
                    last_commit="-",
                    status_text="❌ Não é repositório Git",
                    status_color="#ff6b6b",
                    modified_display=None,
                    untracked_display=None,
                    changed_files=None,
                )
        elif branch == "-" and message and message != "Repositório carregado com sucesso.":
            short = message if len(message) <= 100 else message[:97] + "…"
            self._apply_repository_overview_ui(
                folder_name=folder_name,
                branch="-",
                last_commit=last_c,
                status_text=f"⚠ {short}",
                status_color="#fcc419",
                modified_display=str(mod_n),
                untracked_display=str(unt_n),
                changed_files=files,
            )
        elif has_ch:
            parts: list[str] = []
            if mod_n:
                parts.append(f"{mod_n} modificados")
            if unt_n:
                parts.append(f"{unt_n} não rastreados")
            suffix = f" ({', '.join(parts)})" if parts else ""
            self._apply_repository_overview_ui(
                folder_name=folder_name,
                branch=branch,
                last_commit=last_c,
                status_text=f"⚠ Alterações pendentes{suffix}",
                status_color="#fcc419",
                modified_display=str(mod_n),
                untracked_display=str(unt_n),
                changed_files=files,
            )
        else:
            self._apply_repository_overview_ui(
                folder_name=folder_name,
                branch=branch,
                last_commit=last_c,
                status_text="✔ Limpo",
                status_color="#69db7c",
                modified_display="0",
                untracked_display="0",
                changed_files=[],
            )

        self._log_repository_overview(data)

    def _log_repository_overview(self, data: dict) -> None:
        if bool(data.get("is_git_repo")):
            self._log_line("Resumo do repositório atualizado.\n", success=True)
            self._log_line(f"  Branch: {data.get('branch', '-')}\n")
            mod_n = int(data.get("modified_count", 0) or 0)
            unt_n = int(data.get("untracked_count", 0) or 0)
            self._log_line(f"  Modificados: {mod_n}  |  Não rastreados: {unt_n}\n")
            st = "Alterações pendentes" if data.get("has_changes") else "Limpo"
            self._log_line(f"  Status: {st}\n")
            self._log_line(f"  Último commit: {data.get('last_commit', '-')}\n")
            paths = list(data.get("changed_files") or [])
            if paths:
                self._log_line("  Arquivos:\n")
                max_lines = 40
                for rel in paths[:max_lines]:
                    self._log_line(f"    • {rel}\n")
                if len(paths) > max_lines:
                    self._log_line(f"    … e mais {len(paths) - max_lines} arquivo(s).\n")
        else:
            msg = str(data.get("message", "Erro desconhecido."))
            if "Nenhuma pasta" in msg:
                self._log_line(f"{msg}\n")
            else:
                self._log_line(f"Resumo: {msg}\n", error=True)

    def refresh_repository_overview(self) -> None:
        """Atualiza o card de resumo em thread; desativa o botão durante a leitura."""
        self._cancel_debounced_overview()
        if self._overview_loading:
            return
        path_snapshot = self._selected_path.get().strip()
        self._overview_loading = True
        self._btn_refresh_overview.configure(state="disabled")
        self._overview_hint.configure(text="Atualizando resumo do repositório...")
        self._update_action_states()
        self._update_status_bar()

        def worker() -> None:
            folder_name = Path(path_snapshot).name if path_snapshot else "—"
            try:
                data = git_service.get_repository_overview(path_snapshot)
            except OSError as e:
                data = {
                    "is_git_repo": False,
                    "branch": "-",
                    "has_changes": False,
                    "last_commit": "-",
                    "message": f"Erro ao acessar a pasta: {e}",
                    "modified_count": 0,
                    "untracked_count": 0,
                    "changed_files": [],
                }
            except Exception as e:
                data = {
                    "is_git_repo": False,
                    "branch": "-",
                    "has_changes": False,
                    "last_commit": "-",
                    "message": f"Erro inesperado: {e}",
                    "modified_count": 0,
                    "untracked_count": 0,
                    "changed_files": [],
                }
            self._ui(
                lambda f=folder_name, d=data: self._finish_repository_overview(f, d),
            )

        threading.Thread(target=worker, daemon=True).start()

    def _select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Selecionar pasta do projeto")
        if folder:
            self._cancel_debounced_overview()
            self._selected_path.set(str(Path(folder).resolve()))
            self._log_line(f"Pasta selecionada: {folder}\n")
            self._update_action_states()
            self.refresh_repository_overview()

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
                self._cancel_debounced_overview()
                self._selected_path.set(p["path"])
                self._log_line(f"Projeto carregado: {choice} → {p['path']}\n")
                self._update_action_states()
                self.refresh_repository_overview()
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
                if rc == 0:
                    self._ui(self.refresh_repository_overview)
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
            if rc == 0:
                self._ui(self.refresh_repository_overview)
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
            if rc == 0:
                self._ui(self.refresh_repository_overview)

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
            if rc == 0:
                self._ui(self.refresh_repository_overview)
            self._set_busy(False)

        threading.Thread(target=worker, daemon=True).start()


def run_app() -> None:
    app = MainWindow()
    app.mainloop()
