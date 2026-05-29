from __future__ import annotations

import tkinter.filedialog as fd
import tkinter.messagebox as mb

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

from src.core.file_utils import FILE_DIALOG_TYPES, collect_supported_files, parse_dropped_paths
from src.core.log_service import setup_logging
from src.core.queue_manager import QueueManager, QueueStats
from src.core.settings_service import SettingsService
from src.core.transcription_service import TranscriptionService
from src.models.transcription_job import JobStatus, TranscriptionJob
from src.ui.design.fonts import APP_NAME, APP_SUBTITLE, APP_VERSION, brand_subtitle, brand_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager
from src.ui.queue_panel import QueuePanel
from src.ui.result_panel import ResultPanel
from src.ui.settings_panel import AppSettingsPanel, BrandSidebar

_LEGACY_VIEW_ALIASES = {
    "Pipeline": "transcription",
    "Transcrição": "transcription",
    "Configurações": "settings",
    "Conhecimento": "transcription",
    "Biblioteca": "transcription",
    "Grafo / Conexões": "transcription",
    "Estudo": "transcription",
    "Datasets": "transcription",
}


class MainWindow:
    def __init__(self) -> None:
        setup_logging()
        try:
            TranscriptionService().ensure_whisper()
        except RuntimeError as exc:
            mb.showerror("Erro", str(exc))
            raise SystemExit(1) from exc

        self.settings = SettingsService()
        self.theme = ThemeManager(self.settings.theme)
        self.theme.apply(self.settings.theme)

        self.root = TkinterDnD.Tk()
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("1280x740")
        self.root.minsize(1000, 620)
        self._apply_root_background()

        self.queue_manager = QueueManager(
            self.settings,
            on_job_updated=self._on_job_updated_threadsafe,
            on_queue_idle=self._on_queue_idle_threadsafe,
            on_status_message=self._on_status_threadsafe,
            on_progress=self._on_progress_threadsafe,
            on_queue_recovered=self._on_queue_recovered_threadsafe,
        )

        self._last_status_message = "Pronto."
        self._current_view = "transcription"
        self.status_label = None

        self._build_layout()
        self._setup_dnd()
        self._setup_shortcuts()
        self._restore_last_view()
        self._try_queue_recovery()

    def _apply_root_background(self) -> None:
        """TkinterDnD.Tk() usa bg nativo — fg_color é exclusivo do CTk."""
        self.root.configure(bg=self.theme.colors()["surface"])

    def _build_layout(self) -> None:
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = BrandSidebar(
            self.root,
            self.theme,
            width=Layout.SIDEBAR_WIDTH,
            on_open_settings=self._show_settings,
            on_open_transcription=self._show_transcription,
        )
        self.sidebar.grid(
            row=0, column=0, sticky="nsew", padx=(Layout.MD, Layout.SM), pady=Layout.LG
        )

        center = ctk.CTkFrame(self.root, fg_color="transparent")
        center.grid(row=0, column=1, sticky="nsew", padx=(Layout.SM, Layout.LG), pady=Layout.LG)
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(1, weight=1)
        center.grid_rowconfigure(2, weight=0)

        self._build_header(center)

        self.view_host = ctk.CTkFrame(center, fg_color="transparent")
        self.view_host.grid(row=1, column=0, sticky="nsew")
        self.view_host.grid_columnconfigure(0, weight=1)
        self.view_host.grid_rowconfigure(0, weight=1)

        self.transcription_frame = ctk.CTkFrame(self.view_host, fg_color="transparent")
        self.transcription_frame.grid(row=0, column=0, sticky="nsew")
        self.transcription_frame.grid_columnconfigure(0, weight=7)
        self.transcription_frame.grid_columnconfigure(1, weight=3)
        self.transcription_frame.grid_rowconfigure(0, weight=1)

        self.queue_panel = QueuePanel(
            self.transcription_frame,
            self.queue_manager,
            self.theme,
            on_selection_change=self._on_job_selected,
        )
        self.queue_panel.grid(row=0, column=0, sticky="nsew", padx=(0, Layout.SM))
        self.queue_panel.set_add_files_handler(self.add_files_dialog)
        self.queue_panel.set_add_folder_handler(self.add_folder_dialog)
        self.queue_panel.set_status_handler(self._set_status)

        self.result_panel = ResultPanel(
            self.transcription_frame,
            self.theme,
            self.settings,
            on_status=self._set_status,
        )
        self.result_panel.grid(row=0, column=1, sticky="nsew")

        self.settings_frame = ctk.CTkFrame(self.view_host, fg_color="transparent")
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_rowconfigure(0, weight=1)

        settings_top = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        settings_top.pack(fill="x", pady=(0, Layout.SM))

        ctk.CTkButton(
            settings_top,
            text="← Voltar à transcrição",
            width=180,
            command=self._show_transcription,
            **self.theme.ghost_button_kwargs(),
        ).pack(side="left")

        self.settings_panel = AppSettingsPanel(
            self.settings_frame,
            self.settings,
            self.theme,
            on_theme_change=self._on_theme_change,
            on_settings_change=self._on_settings_change,
        )
        self.settings_panel.pack(fill="both", expand=True)

        self.status_label = ctk.CTkLabel(
            center,
            text=self._last_status_message,
            font=brand_subtitle(),
            text_color=self.theme.colors()["accent"],
            anchor="w",
        )
        self.status_label.grid(row=2, column=0, sticky="ew", pady=(Layout.SM, 0))

        self._show_transcription()
        self._set_status(self._last_status_message)

    def _build_header(self, parent: ctk.CTkFrame) -> None:
        colors = self.theme.colors()
        header = ctk.CTkFrame(
            parent,
            fg_color=colors["header_bg"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=Layout.CORNER_RADIUS,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, Layout.SM))
        header.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=Layout.LG, pady=Layout.MD)

        ctk.CTkLabel(
            inner,
            text=APP_NAME,
            font=brand_title(),
            text_color=colors["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text=APP_SUBTITLE,
            font=brand_subtitle(),
            text_color=colors["text_secondary"],
            anchor="w",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(Layout.XS, 0))

    def _show_transcription(self) -> None:
        self._current_view = "transcription"
        self.settings_frame.grid_remove()
        self.transcription_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar.set_active_view("transcription")
        self.settings.ui_last_tab = "Transcrição"

    def _show_settings(self) -> None:
        self._current_view = "settings"
        self.transcription_frame.grid_remove()
        self.settings_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar.set_active_view("settings")
        self.settings.ui_last_tab = "Configurações"

    def _restore_last_view(self) -> None:
        tab = self.settings.ui_last_tab
        view = _LEGACY_VIEW_ALIASES.get(tab, "transcription")
        if view == "settings":
            self._show_settings()
        else:
            self._show_transcription()

    def _setup_dnd(self) -> None:
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self._drop_event)
        try:
            self.queue_panel.drop_target_register(DND_FILES)
            self.queue_panel.dnd_bind("<<Drop>>", self._drop_event)
        except Exception:
            pass

    def _setup_shortcuts(self) -> None:
        self.root.bind_all("<Control-o>", lambda _e: self.add_files_dialog())
        self.root.bind_all("<Control-t>", lambda _e: self.queue_manager.start_queue())
        self.root.bind_all("<Control-e>", lambda _e: self.result_panel.export_via_shortcut())
        self.root.bind_all("<Control-comma>", lambda _e: self._show_settings())
        self.root.bind_all("<Escape>", lambda _e: self._show_transcription())
        self.root.bind_all("<Control-q>", lambda _e: self.root.destroy())

    def _drop_event(self, event) -> None:
        if self._current_view != "transcription":
            self._show_transcription()
        paths = parse_dropped_paths(event.data)
        if paths:
            self._add_paths(paths)
            self._set_status(f"{len(paths)} arquivo(s) adicionado(s) à fila.")
        else:
            self._set_status("Arquivo não encontrado no drag & drop.")

    def add_files_dialog(self) -> None:
        paths = list(
            fd.askopenfilenames(title="Escolha arquivos para processar", filetypes=FILE_DIALOG_TYPES)
        )
        if paths:
            self._add_paths(list(paths))

    def add_folder_dialog(self) -> None:
        folder = fd.askdirectory(title="Escolha uma pasta com arquivos para processar")
        if not folder:
            return
        paths = collect_supported_files(folder)
        if not paths:
            self._set_status("Nenhum arquivo suportado encontrado na pasta.")
            return
        self._add_paths(paths)

    def _add_paths(self, paths: list[str]) -> None:
        added = self.queue_manager.add_files(paths)
        self.queue_panel.refresh()
        if added:
            self._set_status(f"{len(added)} arquivo(s) na fila.")
            self.queue_manager.select_job(added[-1].id)
            self._on_job_selected(self.queue_manager.selected_job)

    def _on_job_selected(self, job: TranscriptionJob | None) -> None:
        self.result_panel.show_job(job)

    def _on_settings_change(self) -> None:
        for job in self.queue_manager.jobs:
            if job.status == JobStatus.WAITING:
                from src.core.export_service import ExportService

                output_dir = self.settings.resolve_output_dir(job.file_path)
                fmt = self.settings.default_export_format  # type: ignore[arg-type]
                job.output_path = ExportService.build_output_path(job.file_path, output_dir, fmt)
        self.queue_panel.refresh()

    def _on_theme_change(self, theme: str) -> None:
        self.theme.apply(theme)
        colors = self.theme.colors()
        self._apply_root_background()
        if self.status_label is not None:
            self.status_label.configure(text_color=colors["accent"])
        self.sidebar.refresh_theme()
        self.settings_panel.refresh_theme()
        self.queue_panel.refresh_theme()
        self.result_panel.refresh_theme()
        self._set_status(f"Tema alterado para {theme}")

    def _on_job_updated_threadsafe(self, job: TranscriptionJob) -> None:
        self.root.after(0, lambda j=job: self._on_job_updated(j))

    def _on_queue_idle_threadsafe(self) -> None:
        self.root.after(0, self._on_queue_idle)

    def _on_status_threadsafe(self, message: str) -> None:
        self.root.after(0, lambda m=message: self._set_status(m))

    def _on_progress_threadsafe(self, value: float, stats: QueueStats) -> None:
        self.root.after(0, lambda v=value, s=stats: self.queue_panel.update_progress(v, s))

    def _on_queue_recovered_threadsafe(self, meta: dict) -> None:
        self.root.after(0, lambda m=meta: self._on_queue_recovered(m))

    def _try_queue_recovery(self) -> None:
        if self.queue_manager.try_recover_queue(auto=True):
            self.queue_panel.refresh()
            self.queue_panel.set_queue_restored(True)
            pending = sum(
                1 for j in self.queue_manager.jobs
                if j.status in (JobStatus.WAITING, JobStatus.ERROR)
            )
            reset = meta.get("processing_reset", 0) if (meta := self.queue_manager.recovery_meta) else 0
            msg = f"Fila restaurada ({len(self.queue_manager.jobs)} item(ns))."
            if reset:
                msg += f" {reset} em processamento voltaram a aguardar."
            if pending:
                msg += " Clique em Iniciar transcrição para continuar."
            self._set_status(msg)
            if self.queue_manager.jobs:
                self.queue_manager.select_job(self.queue_manager.jobs[0].id)
                self._on_job_selected(self.queue_manager.selected_job)
        self.queue_panel.refresh_cache_stats()

    def _on_queue_recovered(self, meta: dict) -> None:
        self.queue_panel.set_queue_restored(bool(meta.get("restored")))
        self.queue_panel.refresh()
        self.queue_panel.refresh_cache_stats()

    def _on_job_updated(self, job: TranscriptionJob) -> None:
        self.queue_panel.update_job(job)
        selected = self.queue_manager.selected_job
        if selected and selected.id == job.id:
            self.result_panel.show_job(job)
        if job.status == JobStatus.COMPLETED:
            self.settings_panel.refresh_history()

    def _on_queue_idle(self) -> None:
        self.queue_panel.update_progress(
            self.queue_manager.get_overall_progress(),
            self.queue_manager.stats,
        )
        self.settings_panel.refresh_history()

    def _set_status(self, message: str) -> None:
        self._last_status_message = message

        if hasattr(self, "status_label") and self.status_label is not None:
            self.status_label.configure(text=message)

    def run(self) -> None:
        self.root.mainloop()


def run_app() -> None:
    MainWindow().run()
