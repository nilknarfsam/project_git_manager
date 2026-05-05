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
        _mono = ("Consolas", 12)
        _mono_bold = ("Consolas", 12, "bold")
        tb.tag_configure("error", foreground="#ffa8a8", font=_mono_bold, spacing1=1)
        tb.tag_configure("ok", foreground="#8fff9f", font=_mono_bold, spacing1=1)
        tb.tag_configure("normal", font=_mono)

    def append(self, text: str, *, error: bool = False, success: bool = False) -> None:
        tb = self._text._textbox  # noqa: SLF001
        self._text.configure(state="normal")
        if error:
            tb.insert("end", text, "error")
        elif success:
            tb.insert("end", text, "ok")
        else:
            tb.insert("end", text, "normal")
        self._text.configure(state="disabled")
        tb.see("end")

    def clear(self) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")
