from __future__ import annotations

import json
import tkinter.filedialog as fd
from typing import Callable, Optional

import customtkinter as ctk

from src.core.export_service import ExportService
from src.models.transcription_job import JobStatus, TranscriptionJob


class ResultPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_status: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, corner_radius=12, **kwargs)
        self.on_status = on_status
        self._export = ExportService()
        self._current_job: Optional[TranscriptionJob] = None
        self._current_text = ""

        ctk.CTkLabel(
            self,
            text="Resultado",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(12, 8), padx=16, anchor="w")

        self.meta_label = ctk.CTkLabel(
            self,
            text="Selecione um item da fila para visualizar.",
            text_color="gray55",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self.meta_label.pack(fill="x", padx=16, pady=(0, 6))

        self.text_box = ctk.CTkTextbox(
            self,
            height=160,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
        )
        self.text_box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        self.text_box.insert("1.0", "O texto transcrito ou extraído aparecerá aqui.")
        self.text_box.configure(state="disabled")

        export_row = ctk.CTkFrame(self, fg_color="transparent")
        export_row.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_txt = ctk.CTkButton(
            export_row, text="Exportar TXT", width=110, state="disabled", command=lambda: self.export_manual("txt")
        )
        self.btn_txt.pack(side="left", padx=4)

        self.btn_json = ctk.CTkButton(
            export_row, text="Exportar JSON", width=110, state="disabled", command=lambda: self.export_manual("json")
        )
        self.btn_json.pack(side="left", padx=4)

        self.btn_md = ctk.CTkButton(
            export_row, text="Exportar MD", width=110, state="disabled", command=lambda: self.export_manual("md")
        )
        self.btn_md.pack(side="left", padx=4)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.set(0)
        self.progress.pack_forget()

    def show_job(self, job: Optional[TranscriptionJob]) -> None:
        self._current_job = job
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        if not job:
            self.meta_label.configure(text="Selecione um item da fila para visualizar.")
            self.text_box.insert("1.0", "O texto transcrito ou extraído aparecerá aqui.")
            self._current_text = ""
            self._set_export_enabled(False)
        elif job.status == JobStatus.PROCESSING:
            self.meta_label.configure(text=f"Processando: {job.file_name}")
            self.text_box.insert("1.0", "Aguarde, processando…")
            self._current_text = ""
            self._set_export_enabled(False)
        elif job.status == JobStatus.ERROR:
            self.meta_label.configure(text=f"Erro: {job.file_name}")
            self.text_box.insert("1.0", job.error_message or "Erro desconhecido.")
            self._current_text = ""
            self._set_export_enabled(False)
        elif job.status == JobStatus.COMPLETED:
            self.meta_label.configure(
                text=f"{job.file_name} — salvo em: {job.output_path or '—'}"
            )
            self.text_box.insert("1.0", job.result_text or "(vazio)")
            self._current_text = job.result_text
            self._set_export_enabled(bool(job.result_text.strip()))
        else:
            self.meta_label.configure(text=f"{job.file_name} — {job.status.value}")
            self.text_box.insert("1.0", "Aguardando processamento na fila.")
            self._current_text = ""
            self._set_export_enabled(False)

        self.text_box.configure(state="disabled")

    def set_status_message(self, message: str) -> None:
        if message and self.on_status:
            self.on_status(message)

    def show_progress(self, visible: bool, value: float = 0.0) -> None:
        if visible:
            self.progress.pack(fill="x", padx=16, pady=(0, 8))
            self.progress.set(value)
        else:
            self.progress.pack_forget()

    def _set_export_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.btn_txt.configure(state=state)
        self.btn_json.configure(state=state)
        self.btn_md.configure(state=state)

    def export_manual(self, fmt: str) -> None:
        if not self._current_text.strip():
            return

        extensions = {"txt": [("Arquivo TXT", "*.txt")], "json": [("JSON", "*.json")], "md": [("Markdown", "*.md")]}
        default_ext = f".{fmt}"
        path = fd.asksaveasfilename(defaultextension=default_ext, filetypes=extensions.get(fmt, []))
        if path:
            self._export.save(path, self._current_text, fmt)  # type: ignore[arg-type]
            self.set_status_message(f"Arquivo salvo: {path}")

    def export_via_shortcut(self) -> None:
        import tkinter.simpledialog as sd

        opcoes = {"1": "txt", "2": "json", "3": "md"}
        escolha = sd.askstring(
            "Exportar",
            "Escolha o formato:\n1 - TXT\n2 - JSON\n3 - Markdown",
            parent=self.winfo_toplevel(),
        )
        if escolha and escolha.strip() in opcoes:
            self.export_manual(opcoes[escolha.strip()])
