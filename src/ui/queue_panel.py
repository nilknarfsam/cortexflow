from __future__ import annotations

import os
import subprocess
import sys
from typing import Callable, Optional

import customtkinter as ctk

from src.core.queue_manager import QueueManager, QueueStats
from src.models.transcription_job import JobStatus, TranscriptionJob
from src.ui.design.fonts import body_small, caption, panel_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager


class QueuePanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        queue: QueueManager,
        theme: ThemeManager,
        on_selection_change: Optional[Callable[[Optional[TranscriptionJob]], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.queue = queue
        self.theme = theme
        self.on_selection_change = on_selection_change
        self._row_widgets: dict[str, ctk.CTkFrame] = {}

        self._apply_frame_style()
        self._build_header()
        self._build_stats()
        self._build_table_header()
        self._build_scroll()
        self._build_actions()

        self._on_add_files: Optional[Callable[[], None]] = None
        self._on_status: Optional[Callable[[str], None]] = None
        self.update_progress(0.0, self.queue.stats)

    def _apply_frame_style(self) -> None:
        self.configure(**self.theme.frame_kwargs(elevated=True))

    def refresh_theme(self) -> None:
        self._apply_frame_style()
        colors = self.theme.colors()
        self.drop_hint.configure(text_color=colors["text_muted"])
        self.stats_label.configure(text_color=colors["text_secondary"])
        self.table_header.configure(fg_color=colors["table_header"])
        self.refresh()

    def _build_header(self) -> None:
        colors = self.theme.colors()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=Layout.LG, pady=(Layout.LG, Layout.SM))

        ctk.CTkLabel(
            header,
            text="Pipeline de processamento",
            font=panel_title(),
            text_color=colors["text_primary"],
        ).pack(side="left")

        self.drop_hint = ctk.CTkLabel(
            header,
            text="Arraste arquivos aqui",
            text_color=colors["text_muted"],
            font=body_small(),
        )
        self.drop_hint.pack(side="right", padx=Layout.SM)

    def _build_stats(self) -> None:
        colors = self.theme.colors()
        self.stats_label = ctk.CTkLabel(
            self,
            text=self._stats_text(QueueStats(0, 0, 0, 0, 0, 0)),
            font=caption(),
            text_color=colors["text_secondary"],
            anchor="w",
            justify="left",
        )
        self.stats_label.pack(fill="x", padx=Layout.LG, pady=(0, Layout.XS))

        self.overall_progress = ctk.CTkProgressBar(
            self,
            progress_color=self.theme.colors()["primary"],
        )
        self.overall_progress.set(0)
        self.overall_progress.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))

    def _build_table_header(self) -> None:
        colors = self.theme.colors()
        self.table_header = ctk.CTkFrame(
            self,
            fg_color=colors["table_header"],
            corner_radius=Layout.CORNER_RADIUS_SM,
        )
        self.table_header.pack(fill="x", padx=Layout.LG, pady=(0, Layout.XS))

        for i, (text, width) in enumerate(
            [("Arquivo", 180), ("Tipo", 70), ("Status", 90), ("Saída", 200)]
        ):
            ctk.CTkLabel(
                self.table_header,
                text=text,
                width=width,
                anchor="w",
                font=body_small(),
                text_color=colors["text_secondary"],
            ).grid(row=0, column=i, padx=Layout.SM, pady=Layout.SM, sticky="w")

    def _build_scroll(self) -> None:
        self.scroll = ctk.CTkScrollableFrame(self, label_text="", fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=Layout.LG, pady=(0, Layout.SM))

    def _build_actions(self) -> None:
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))

        self.btn_add = ctk.CTkButton(
            actions,
            text="Adicionar Arquivos",
            width=140,
            command=self._on_add_clicked,
            **self.theme.primary_button_kwargs(),
        )
        self.btn_add.pack(side="left", padx=(0, Layout.SM))

        self.btn_start = ctk.CTkButton(
            actions,
            text="Iniciar Fila",
            width=110,
            command=self._start_queue,
            **self.theme.accent_button_kwargs(),
        )
        self.btn_start.pack(side="left", padx=Layout.XS)

        self.btn_cancel = ctk.CTkButton(
            actions,
            text="Cancelar Fila",
            width=110,
            command=self._cancel_queue,
            state="disabled",
            **self.theme.warning_button_kwargs(),
        )
        self.btn_cancel.pack(side="left", padx=Layout.XS)

        self.btn_open_folder = ctk.CTkButton(
            actions,
            text="Abrir pasta de saída",
            width=150,
            command=self._open_output_folder,
            **self.theme.ghost_button_kwargs(),
        )
        self.btn_open_folder.pack(side="left", padx=Layout.XS)

        actions2 = ctk.CTkFrame(self, fg_color="transparent")
        actions2.pack(fill="x", padx=Layout.LG, pady=(0, Layout.LG))

        ctk.CTkButton(
            actions2,
            text="Remover Selecionado",
            width=150,
            command=self._remove_selected,
            **self.theme.ghost_button_kwargs(),
        ).pack(side="left", padx=(0, Layout.SM))

        ctk.CTkButton(
            actions2,
            text="Limpar Fila",
            width=110,
            command=self._clear_queue,
            **self.theme.danger_button_kwargs(),
        ).pack(side="left", padx=Layout.XS)

    def set_add_files_handler(self, handler: Callable[[], None]) -> None:
        self._on_add_files = handler

    def set_status_handler(self, handler: Callable[[str], None]) -> None:
        self._on_status = handler

    @staticmethod
    def _stats_text(stats: QueueStats) -> str:
        return (
            f"Total: {stats.total}  ·  Aguardando: {stats.waiting}  ·  "
            f"Processando: {stats.processing}  ·  Concluídos: {stats.completed}  ·  "
            f"Erros: {stats.errors}"
            + (f"  ·  Cancelados: {stats.cancelled}" if stats.cancelled else "")
        )

    def update_progress(self, value: float, stats: QueueStats) -> None:
        self.overall_progress.set(max(0.0, min(1.0, value)))
        self.stats_label.configure(text=self._stats_text(stats))
        processing = self.queue.is_processing
        self.btn_start.configure(state="disabled" if processing else "normal")
        self.btn_cancel.configure(state="normal" if processing else "disabled")

    def _on_add_clicked(self) -> None:
        if self._on_add_files:
            self._on_add_files()

    def _start_queue(self) -> None:
        if not self.queue.start_queue():
            if self._on_status and self.queue.is_processing:
                self._on_status("A fila já está em processamento.")

    def _cancel_queue(self) -> None:
        self.queue.cancel_queue()

    def _open_output_folder(self) -> None:
        job = self.queue.selected_job
        folder = self.queue.resolve_output_folder_for_job(job)
        if not folder:
            if self._on_status:
                self._on_status("Nenhuma pasta de saída disponível.")
            return
        try:
            if sys.platform == "win32":
                os.startfile(folder)  # noqa: S606
            elif sys.platform == "darwin":
                subprocess.run(["open", folder], check=False)
            else:
                subprocess.run(["xdg-open", folder], check=False)
            if self._on_status:
                self._on_status(f"Pasta aberta: {folder}")
        except OSError as exc:
            if self._on_status:
                self._on_status(f"Não foi possível abrir a pasta: {exc}")

    def _remove_selected(self) -> None:
        if self.queue.remove_selected():
            self.refresh()

    def _clear_queue(self) -> None:
        self.queue.clear_queue()
        self.refresh()

    def refresh(self) -> None:
        for widget in self.scroll.winfo_children():
            widget.destroy()
        self._row_widgets.clear()

        for job in self.queue.jobs:
            self._create_row(job)

        self.update_progress(self.queue.get_overall_progress(), self.queue.stats)

    def _status_key(self, status: JobStatus) -> str:
        return {
            JobStatus.WAITING: "waiting",
            JobStatus.PROCESSING: "processing",
            JobStatus.COMPLETED: "completed",
            JobStatus.ERROR: "error",
            JobStatus.CANCELLED: "cancelled",
        }.get(status, "waiting")

    def _create_row(self, job: TranscriptionJob) -> None:
        colors = self.theme.colors()
        selected = self.queue.selected_job
        is_selected = selected is not None and selected.id == job.id

        row = ctk.CTkFrame(
            self.scroll,
            fg_color=colors["card_selected"] if is_selected else colors["card_bg"],
            border_color=colors["border"],
            border_width=1 if is_selected else 0,
            corner_radius=Layout.CORNER_RADIUS_CARD,
        )
        row.pack(fill="x", pady=Layout.XS)
        self._row_widgets[job.id] = row

        status_color = self.theme.status_color(self._status_key(job.status))
        status_text = job.status.value

        out_display = job.output_path or "—"
        if len(out_display) > 42:
            out_display = "…" + out_display[-39:]

        values = [
            (job.file_name[:28] + "…" if len(job.file_name) > 29 else job.file_name, 180),
            (job.file_type, 70),
            (status_text, 90),
            (out_display, 200),
        ]

        for col, (text, width) in enumerate(values):
            lbl = ctk.CTkLabel(
                row,
                text=text,
                width=width,
                anchor="w",
                font=body_small(),
                text_color=colors["text_primary"],
            )
            if col == 2:
                lbl.configure(text_color=status_color)
            lbl.grid(row=0, column=col, padx=Layout.SM, pady=Layout.SM, sticky="w")
            lbl.bind("<Button-1>", lambda e, jid=job.id: self._select(jid))

        row.bind("<Button-1>", lambda e, jid=job.id: self._select(jid))

    def _select(self, job_id: str) -> None:
        self.queue.select_job(job_id)
        self._highlight_all()
        if self.on_selection_change:
            self.on_selection_change(self.queue.selected_job)

    def _highlight_all(self) -> None:
        colors = self.theme.colors()
        selected = self.queue.selected_job
        for jid, row in self._row_widgets.items():
            if selected and jid == selected.id:
                row.configure(fg_color=colors["card_selected"], border_width=1, border_color=colors["primary"])
            else:
                row.configure(fg_color=colors["card_bg"], border_width=0)

    def update_job(self, job: TranscriptionJob) -> None:
        self.refresh()
        if self.queue.selected_job and self.queue.selected_job.id == job.id:
            if self.on_selection_change:
                self.on_selection_change(job)
