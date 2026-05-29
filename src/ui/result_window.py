"""Janela secundária para visualização de resultado — UX 3.1."""

from __future__ import annotations

import tkinter.filedialog as fd
from typing import Callable, Optional

import customtkinter as ctk

from src.core.export_service import ExportService
from src.core.settings_service import SettingsService
from src.models.transcription_job import JobStatus, TranscriptionJob
from src.semantic.semantic_engine import analyze_text
from src.ui.design.fonts import badge, body_small, caption, mono, panel_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager

PREVIEW_CHAR_LIMIT = 12_000


class ResultViewerWindow:
    """Abre o texto transcrito sob demanda, fora da janela principal."""

    _instance: Optional["ResultViewerWindow"] = None

    def __init__(
        self,
        parent: ctk.CTk,
        theme: ThemeManager,
        settings: SettingsService,
        on_status: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._parent = parent
        self.theme = theme
        self.settings = settings
        self.on_status = on_status
        self._export = ExportService()
        self._window: Optional[ctk.CTkToplevel] = None
        self._current_job: Optional[TranscriptionJob] = None
        self._current_text = ""
        self._semantic_summary: dict = {}
        self._widgets: dict = {}

    @classmethod
    def get(
        cls,
        parent: ctk.CTk,
        theme: ThemeManager,
        settings: SettingsService,
        on_status: Optional[Callable[[str], None]] = None,
    ) -> "ResultViewerWindow":
        if cls._instance is None:
            cls._instance = cls(parent, theme, settings, on_status)
        return cls._instance

    def show_job(self, job: Optional[TranscriptionJob]) -> None:
        if job is None:
            return
        self._ensure_window()
        self._populate(job)

    def export_via_shortcut(self) -> None:
        if self._window is None or not self._window.winfo_exists():
            return
        import tkinter.simpledialog as sd

        opcoes = {"1": "txt", "2": "json", "3": "md"}
        escolha = sd.askstring(
            "Exportar",
            "Escolha o formato:\n1 - TXT\n2 - JSON\n3 - Markdown",
            parent=self._window,
        )
        if escolha and escolha.strip() in opcoes:
            self._export_manual(opcoes[escolha.strip()])

    def refresh_theme(self) -> None:
        if self._window is None or not self._window.winfo_exists():
            return
        colors = self.theme.colors()
        self._window.configure(fg_color=colors["surface"])
        self._widgets["meta"].configure(text_color=colors["text_muted"])
        self._widgets["preview_info"].configure(text_color=colors["text_muted"])
        self._widgets["semantic"].configure(text_color=colors["text_secondary"])
        self._widgets["text_box"].configure(
            fg_color=colors["surface"],
            border_color=colors["border"],
        )

    def _ensure_window(self) -> None:
        if self._window is not None and self._window.winfo_exists():
            self._window.deiconify()
            self._window.lift()
            self._window.focus()
            return

        colors = self.theme.colors()
        self._window = ctk.CTkToplevel(self._parent)
        self._window.title("Resultado da transcrição")
        self._window.geometry("720x560")
        self._window.minsize(520, 400)
        self._window.configure(fg_color=colors["surface"])

        title_row = ctk.CTkFrame(self._window, fg_color="transparent")
        title_row.pack(fill="x", padx=Layout.LG, pady=(Layout.LG, Layout.SM))

        ctk.CTkLabel(
            title_row,
            text="Resultado",
            font=panel_title(),
            text_color=colors["text_primary"],
        ).pack(side="left")

        self._widgets["semantic_badge"] = ctk.CTkLabel(
            title_row,
            text="Semantic Ready",
            font=badge(),
            text_color="#FFFFFF",
            fg_color=colors["border"],
            corner_radius=6,
            padx=8,
            pady=2,
        )
        self._widgets["study_badge"] = ctk.CTkLabel(
            title_row,
            text="Study Ready",
            font=badge(),
            text_color="#FFFFFF",
            fg_color=colors["border"],
            corner_radius=6,
            padx=8,
            pady=2,
        )

        ctk.CTkButton(
            title_row,
            text="Fechar",
            width=90,
            command=self._close,
            **self.theme.ghost_button_kwargs(),
        ).pack(side="right")

        self._widgets["meta"] = ctk.CTkLabel(
            self._window,
            text="",
            text_color=colors["text_muted"],
            font=body_small(),
            anchor="w",
            wraplength=660,
        )
        self._widgets["meta"].pack(fill="x", padx=Layout.LG, pady=(0, Layout.XS))

        self._widgets["semantic"] = ctk.CTkLabel(
            self._window,
            text="",
            text_color=colors["text_secondary"],
            font=caption(),
            anchor="w",
            wraplength=660,
            justify="left",
        )
        self._widgets["semantic"].pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))

        preview_bar = ctk.CTkFrame(self._window, fg_color="transparent")
        preview_bar.pack(fill="x", padx=Layout.LG, pady=(0, Layout.XS))

        self._widgets["preview_info"] = ctk.CTkLabel(
            preview_bar,
            text="",
            text_color=colors["text_muted"],
            font=caption(),
            anchor="w",
        )
        self._widgets["preview_info"].pack(side="left", fill="x", expand=True)

        self._widgets["btn_load_full"] = ctk.CTkButton(
            preview_bar,
            text="Carregar texto completo",
            width=170,
            height=26,
            font=body_small(),
            command=self._load_full_text,
            **self.theme.ghost_button_kwargs(),
        )

        self._widgets["text_box"] = ctk.CTkTextbox(
            self._window,
            font=mono(12),
            wrap="word",
            fg_color=colors["surface"],
            border_color=colors["border"],
            border_width=1,
        )
        self._widgets["text_box"].pack(fill="both", expand=True, padx=Layout.LG, pady=(0, Layout.SM))

        export_row = ctk.CTkFrame(self._window, fg_color="transparent")
        export_row.pack(fill="x", padx=Layout.LG, pady=(0, Layout.LG))

        self._widgets["btn_txt"] = ctk.CTkButton(
            export_row,
            text="Exportar TXT",
            width=110,
            state="disabled",
            command=lambda: self._export_manual("txt"),
            **self.theme.ghost_button_kwargs(),
        )
        self._widgets["btn_txt"].pack(side="left", padx=Layout.XS)

        self._widgets["btn_json"] = ctk.CTkButton(
            export_row,
            text="Exportar JSON",
            width=110,
            state="disabled",
            command=lambda: self._export_manual("json"),
            **self.theme.ghost_button_kwargs(),
        )
        self._widgets["btn_json"].pack(side="left", padx=Layout.XS)

        self._widgets["btn_md"] = ctk.CTkButton(
            export_row,
            text="Exportar MD",
            width=110,
            state="disabled",
            command=lambda: self._export_manual("md"),
            **self.theme.primary_button_kwargs(),
        )
        self._widgets["btn_md"].pack(side="left", padx=Layout.XS)

        self._window.protocol("WM_DELETE_WINDOW", self._close)

    def _close(self) -> None:
        if self._window is not None and self._window.winfo_exists():
            self._window.withdraw()

    def _populate(self, job: TranscriptionJob) -> None:
        self._current_job = job
        self._widgets["semantic_badge"].pack_forget()
        self._widgets["study_badge"].pack_forget()
        self._widgets["btn_load_full"].pack_forget()
        self._widgets["semantic"].configure(text="")
        self._widgets["preview_info"].configure(text="")

        if job.status == JobStatus.PROCESSING:
            self._set_text("Aguarde, processando…", full_text="", meta=f"Processando: {job.file_name}")
            self._set_export_enabled(False)
            return

        if job.status == JobStatus.ERROR:
            detail = job.error_message or "Erro desconhecido."
            if job.error_code:
                detail = f"[{job.error_code}] {detail}"
            self._set_text(detail, full_text="", meta=f"Erro: {job.file_name}")
            self._set_export_enabled(False)
            return

        if job.status == JobStatus.CANCELLED:
            self._set_text(
                job.error_message or "Item cancelado.",
                full_text="",
                meta=f"Cancelado: {job.file_name}",
            )
            self._set_export_enabled(False)
            return

        if job.status == JobStatus.COMPLETED:
            meta = f"{job.file_name} — salvo em: {job.output_path or '—'}"
            self._update_semantic_preview(job)
            self._update_study_preview(job)
            self._set_text(job.result_text or "(vazio)", full_text=job.result_text, meta=meta)
            self._set_export_enabled(bool((job.result_text or "").strip()))
            return

        self._set_text(
            "Aguardando processamento na fila.",
            full_text="",
            meta=f"{job.file_name} — {job.status.value}",
        )
        self._set_export_enabled(False)

    def _update_study_preview(self, job: TranscriptionJob) -> None:
        sm = job.study_metadata or {}
        if not sm.get("study_ready"):
            return
        from src.ui.design.colors import SEMANTIC

        self._widgets["study_badge"].configure(fg_color=SEMANTIC["success"])
        self._widgets["study_badge"].pack(side="left", padx=(Layout.SM, 0), before=self._widgets["meta"])
        extra = (
            f"  ·  Study: {sm.get('flashcards_count', 0)} flashcards, "
            f"{sm.get('quizzes_count', 0)} quizzes, {sm.get('difficulty', '—')}"
        )
        current = self._widgets["semantic"].cget("text")
        if extra.strip() not in (current or ""):
            self._widgets["semantic"].configure(text=(current or "") + extra)

    def _update_semantic_preview(self, job: TranscriptionJob) -> None:
        text = job.result_text or ""
        if not text.strip():
            return

        if job.semantic_metadata.get("semantic_ready"):
            self._semantic_summary = dict(job.semantic_metadata)
        else:
            self._semantic_summary = analyze_text(text).to_metadata()

        colors = self.theme.colors()
        refs = self._semantic_summary.get("reference_count", 0)
        hi = self._semantic_summary.get("highlight_count", 0)
        chunks = self._semantic_summary.get("chunk_count", 0)
        topics = self._semantic_summary.get("topics", [])
        if isinstance(topics, str):
            topics_list = [t.strip() for t in topics.split(",") if t.strip()]
        else:
            topics_list = list(topics)[:5]

        self._widgets["semantic_badge"].configure(fg_color=colors["primary"])
        self._widgets["semantic_badge"].pack(side="left", padx=(Layout.SM, 0))

        topic_text = ", ".join(topics_list) if topics_list else "—"
        self._widgets["semantic"].configure(
            text=(
                f"Referências: {refs}  ·  Highlights: {hi}  ·  "
                f"Chunks: {chunks}  ·  Tópicos: {topic_text}"
            )
        )

    def _set_text(self, display_text: str, *, full_text: str, meta: str) -> None:
        self._widgets["meta"].configure(text=meta)
        self._current_text = full_text if full_text != "" else display_text

        if len(display_text) > PREVIEW_CHAR_LIMIT:
            shown = display_text[:PREVIEW_CHAR_LIMIT]
            remaining = len(display_text) - PREVIEW_CHAR_LIMIT
            self._current_text = display_text
            display_text = (
                f"{shown}\n\n"
                f"… preview limitado ({remaining:,} caracteres ocultos). "
                f"Use «Carregar texto completo» ou exporte o arquivo."
            )
            self._widgets["preview_info"].configure(
                text=f"Exibindo {PREVIEW_CHAR_LIMIT:,} de {len(self._current_text):,} caracteres"
            )
            self._widgets["btn_load_full"].pack(side="right")
        else:
            self._widgets["preview_info"].configure(
                text=f"{len(display_text):,} caracteres" if display_text.strip() else ""
            )

        box = self._widgets["text_box"]
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", display_text)
        box.configure(state="disabled")

    def _load_full_text(self) -> None:
        if not self._current_text:
            return
        self._widgets["btn_load_full"].pack_forget()
        self._widgets["preview_info"].configure(
            text=f"Texto completo: {len(self._current_text):,} caracteres"
        )
        box = self._widgets["text_box"]
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", self._current_text)
        box.configure(state="disabled")
        box.see("1.0")

    def _set_export_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self._widgets["btn_txt"].configure(state=state)
        self._widgets["btn_json"].configure(state=state)
        self._widgets["btn_md"].configure(state=state)

    def _export_manual(self, fmt: str) -> None:
        if not self._current_text.strip():
            return

        extensions = {
            "txt": [("Arquivo TXT", "*.txt")],
            "json": [("JSON", "*.json")],
            "md": [("Markdown", "*.md")],
        }
        default_ext = f".{fmt}"
        path = fd.asksaveasfilename(defaultextension=default_ext, filetypes=extensions.get(fmt, []))
        if path:
            source = self._current_job.file_path if self._current_job else path
            self._export.save(
                path,
                self._current_text,
                fmt,  # type: ignore[arg-type]
                source_path=source,
                export_mode=self.settings.export_mode,
                content_template=self.settings.content_template,
                language=self.settings.language,
                model=self.settings.whisper_model,
            )
            if self.on_status:
                self.on_status(f"Arquivo salvo: {path}")
