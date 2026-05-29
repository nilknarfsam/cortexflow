from __future__ import annotations

import tkinter.filedialog as fd
from typing import Callable, Optional

import customtkinter as ctk

from src.core.settings_service import SettingsService
from src.ui.design.fonts import APP_NAME, APP_TAGLINE, APP_VERSION, body_small, mono, panel_title, section_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager


class SettingsPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        settings: SettingsService,
        theme: ThemeManager,
        on_theme_change: Optional[Callable[[str], None]] = None,
        on_settings_change: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.settings = settings
        self.theme = theme
        self.on_theme_change = on_theme_change
        self.on_settings_change = on_settings_change

        self._apply_frame_style()
        self._build_brand_header()
        self._build_controls()
        self._build_history()

    def _apply_frame_style(self) -> None:
        self.configure(**self.theme.sidebar_kwargs())

    def refresh_theme(self) -> None:
        self._apply_frame_style()
        colors = self.theme.colors()
        self.brand_tagline.configure(text_color=colors["text_secondary"])
        self.version_badge.configure(
            text_color=colors["text_muted"],
            fg_color=colors["surface_elevated"],
        )
        self.output_label.configure(text_color=colors["text_muted"])

    def _build_brand_header(self) -> None:
        colors = self.theme.colors()
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", padx=Layout.LG, pady=(Layout.LG, Layout.MD))

        ctk.CTkLabel(
            brand,
            text=APP_NAME,
            font=section_title(),
            text_color=colors["text_primary"],
            anchor="w",
        ).pack(fill="x")

        meta = ctk.CTkFrame(brand, fg_color="transparent")
        meta.pack(fill="x", pady=(Layout.XS, 0))

        self.version_badge = ctk.CTkLabel(
            meta,
            text=f"v{APP_VERSION}",
            font=body_small(),
            text_color=colors["text_muted"],
            fg_color=colors["surface_elevated"],
            corner_radius=6,
            padx=6,
            pady=1,
        )
        self.version_badge.pack(side="left")

        self.brand_tagline = ctk.CTkLabel(
            meta,
            text=APP_TAGLINE,
            font=body_small(),
            text_color=colors["text_secondary"],
            wraplength=220,
            justify="left",
        )
        self.brand_tagline.pack(fill="x", pady=(Layout.SM, 0))

        divider = ctk.CTkFrame(self, height=1, fg_color=colors["border"], corner_radius=0)
        divider.pack(fill="x", padx=Layout.LG, pady=(0, Layout.MD))

    def _build_controls(self) -> None:
        pad = {"padx": Layout.LG, "anchor": "w"}

        ctk.CTkLabel(
            self,
            text="Configurações",
            font=panel_title(),
        ).pack(pady=(0, Layout.SM), **pad)

        ctk.CTkLabel(self, text="Tema", anchor="w", font=body_small()).pack(fill="x", **pad)
        self.theme_menu = ctk.CTkOptionMenu(
            self,
            values=["System", "Light", "Dark"],
            command=self._change_theme,
            width=220,
            **self.theme.option_menu_kwargs(),
        )
        self.theme_menu.set(self.settings.theme)
        self.theme_menu.pack(padx=Layout.LG, pady=(Layout.XS, Layout.MD), anchor="w")

        ctk.CTkLabel(self, text="Idioma (Whisper / OCR)", anchor="w", font=body_small()).pack(fill="x", **pad)
        idiomas = ["auto", "pt", "en", "es", "fr", "de", "it", "ru", "zh"]
        self.language_var = ctk.StringVar(value=self.settings.language)
        self.language_menu = ctk.CTkOptionMenu(
            self,
            values=idiomas,
            variable=self.language_var,
            command=self._change_language,
            width=220,
        )
        self.language_menu.pack(padx=Layout.LG, pady=(Layout.XS, Layout.MD), anchor="w")

        ctk.CTkLabel(self, text="Formato padrão de saída", anchor="w", font=body_small()).pack(fill="x", **pad)
        self.format_menu = ctk.CTkOptionMenu(
            self,
            values=["txt", "md", "json"],
            command=self._change_format,
            width=220,
        )
        self.format_menu.set(self.settings.default_export_format)
        self.format_menu.pack(padx=Layout.LG, pady=(Layout.XS, Layout.MD), anchor="w")

        ctk.CTkLabel(self, text="Modo de exportação", anchor="w", font=body_small()).pack(fill="x", **pad)
        self.export_mode_menu = ctk.CTkOptionMenu(
            self,
            values=["raw", "clean", "ai_ready", "notebooklm"],
            command=self._change_export_mode,
            width=220,
        )
        self.export_mode_menu.set(self.settings.export_mode)
        self.export_mode_menu.pack(padx=Layout.LG, pady=(Layout.XS, Layout.MD), anchor="w")

        ctk.CTkLabel(self, text="Tipo de conteúdo", anchor="w", font=body_small()).pack(fill="x", **pad)
        self.template_menu = ctk.CTkOptionMenu(
            self,
            values=["generic", "sermon", "podcast", "course"],
            command=self._change_template,
            width=220,
        )
        self.template_menu.set(self.settings.content_template)
        self.template_menu.pack(padx=Layout.LG, pady=(Layout.XS, Layout.MD), anchor="w")

        ctk.CTkLabel(self, text="Pasta global de saída", anchor="w", font=body_small()).pack(fill="x", **pad)
        self.output_label = ctk.CTkLabel(
            self,
            text=self._output_label_text(),
            wraplength=230,
            justify="left",
            text_color=self.theme.colors()["text_muted"],
            font=body_small(),
        )
        self.output_label.pack(padx=Layout.LG, pady=(Layout.XS, Layout.SM), anchor="w")

        ctk.CTkButton(
            self,
            text="Escolher Pasta",
            command=self._choose_output_folder,
            width=220,
            **self.theme.primary_button_kwargs(),
        ).pack(padx=Layout.LG, pady=(0, Layout.SM), anchor="w")

        ctk.CTkButton(
            self,
            text="Usar pasta do arquivo",
            command=self._clear_output_folder,
            width=220,
            **self.theme.ghost_button_kwargs(),
        ).pack(padx=Layout.LG, pady=(0, Layout.LG), anchor="w")

    def _build_history(self) -> None:
        ctk.CTkLabel(
            self,
            text="Histórico recente",
            font=panel_title(),
        ).pack(padx=Layout.LG, pady=(Layout.SM, Layout.XS), anchor="w")

        self.history_box = ctk.CTkTextbox(self, height=140, font=mono())
        self.history_box.pack(padx=Layout.LG, pady=(0, Layout.LG), fill="both", expand=True)
        self.history_box.configure(state="disabled")
        self.refresh_history()

    def _output_label_text(self) -> str:
        folder = self.settings.output_folder.strip()
        if folder:
            return folder
        return "(mesma pasta do arquivo original)"

    def _change_theme(self, value: str) -> None:
        self.settings.theme = value
        if self.on_theme_change:
            self.on_theme_change(value)

    def _change_language(self, value: str) -> None:
        self.settings.language = value
        self._notify_change()

    def _change_format(self, value: str) -> None:
        self.settings.default_export_format = value
        self._notify_change()

    def _change_export_mode(self, value: str) -> None:
        self.settings.export_mode = value
        self._notify_change()

    def _change_template(self, value: str) -> None:
        self.settings.content_template = value
        self._notify_change()

    def _choose_output_folder(self) -> None:
        folder = fd.askdirectory(title="Pasta global de saída")
        if folder:
            self.settings.output_folder = folder
            self.output_label.configure(text=self._output_label_text())
            self._notify_change()

    def _clear_output_folder(self) -> None:
        self.settings.output_folder = ""
        self.output_label.configure(text=self._output_label_text())
        self._notify_change()

    def _notify_change(self) -> None:
        if self.on_settings_change:
            self.on_settings_change()

    def refresh_history(self) -> None:
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        history = self.settings.history
        if not history:
            self.history_box.insert("1.0", "Nenhuma transcrição recente.")
        else:
            for item in reversed(history):
                status = item.get("status", "concluído")
                line = f"- {item['arquivo']} ({item['tipo']}) [{status}]"
                if item.get("export_mode"):
                    line += f" · {item['export_mode']}"
                if item.get("template_usado"):
                    line += f" · {item['template_usado']}"
                if item.get("pipeline_stage"):
                    line += f" · {item['pipeline_stage']}"
                if item.get("topicos"):
                    line += f" · {item['topicos'][:40]}"
                if item.get("referencias"):
                    line += f" · refs:{item['referencias']}"
                if item.get("mensagem"):
                    line += f" — {item['mensagem'][:60]}"
                self.history_box.insert("end", line + "\n")
        self.history_box.configure(state="disabled")
