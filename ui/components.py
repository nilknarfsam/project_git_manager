"""
Componentes reutilizáveis da UI: console de log com rolagem automática e estilo opcional de erro.
"""

from __future__ import annotations

import customtkinter as ctk


class LogConsole(ctk.CTkFrame):
    """Saída de log rolável; usa tk.Text por baixo para colorir stderr."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._text = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self._text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        # Tag de erro no widget subjacente (CustomTkinter envolve tk.Text)
        tb = self._text._textbox  # noqa: SLF001 — padrão comum com CTkTextbox
        tb.tag_configure("error", foreground="#ff6b6b")
        tb.tag_configure("ok", foreground="#69db7c")

    def append(self, text: str, *, error: bool = False, success: bool = False) -> None:
        tb = self._text._textbox  # noqa: SLF001
        self._text.configure(state="normal")
        tag = "error" if error else ("ok" if success else None)
        if tag:
            tb.insert("end", text, tag)
        else:
            tb.insert("end", text)
        self._text.configure(state="disabled")
        tb.see("end")

    def clear(self) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")
