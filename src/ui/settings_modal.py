"""Modal de configurações — UX 3.1."""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from src.core.settings_service import SettingsService
from src.ui.design.fonts import panel_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager
from src.ui.settings_panel import AppSettingsPanel


class SettingsModal:
    """Abre preferências em janela modal sobre a janela principal."""

    def __init__(
        self,
        parent: ctk.CTk,
        settings: SettingsService,
        theme: ThemeManager,
        on_theme_change: Optional[Callable[[str], None]] = None,
        on_settings_change: Optional[Callable[[], None]] = None,
        on_restore_queue: Optional[Callable[[], None]] = None,
        on_clear_cache: Optional[Callable[[], None]] = None,
    ) -> None:
        self._parent = parent
        self.settings = settings
        self.theme = theme
        self.on_theme_change = on_theme_change
        self.on_settings_change = on_settings_change
        self.on_restore_queue = on_restore_queue
        self.on_clear_cache = on_clear_cache
        self._window: Optional[ctk.CTkToplevel] = None
        self._panel: Optional[AppSettingsPanel] = None

    @property
    def panel(self) -> Optional[AppSettingsPanel]:
        return self._panel

    def show(self) -> None:
        if self._window is not None and self._window.winfo_exists():
            self._window.focus()
            self._window.lift()
            return

        colors = self.theme.colors()
        self._window = ctk.CTkToplevel(self._parent)
        self._window.title("Configurações")
        self._window.geometry("560x640")
        self._window.minsize(480, 520)
        self._window.transient(self._parent)
        self._window.grab_set()
        self._window.configure(fg_color=colors["surface"])

        header = ctk.CTkFrame(self._window, fg_color="transparent")
        header.pack(fill="x", padx=Layout.LG, pady=(Layout.LG, Layout.SM))

        ctk.CTkLabel(
            header,
            text="Configurações",
            font=panel_title(),
            text_color=colors["text_primary"],
            anchor="w",
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Fechar",
            width=90,
            command=self._close,
            **self.theme.ghost_button_kwargs(),
        ).pack(side="right")

        body = ctk.CTkFrame(self._window, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=Layout.LG, pady=(0, Layout.LG))

        self._panel = AppSettingsPanel(
            body,
            self.settings,
            self.theme,
            on_theme_change=self._on_theme_change,
            on_settings_change=self._on_settings_change,
            on_restore_queue=self.on_restore_queue,
            on_clear_cache=self.on_clear_cache,
        )
        self._panel.pack(fill="both", expand=True)

        self._window.protocol("WM_DELETE_WINDOW", self._close)
        self._window.bind("<Escape>", lambda _e: self._close())

    def refresh_theme(self) -> None:
        if self._panel is not None:
            self._panel.refresh_theme()

    def refresh_history(self) -> None:
        if self._panel is not None:
            self._panel.refresh_history()

    def _on_theme_change(self, theme: str) -> None:
        if self._window is not None and self._window.winfo_exists():
            self._window.configure(fg_color=self.theme.colors()["surface"])
        if self.on_theme_change:
            self.on_theme_change(theme)

    def _on_settings_change(self) -> None:
        if self.on_settings_change:
            self.on_settings_change()

    def _close(self) -> None:
        if self._window is not None and self._window.winfo_exists():
            self._window.grab_release()
            self._window.destroy()
        self._window = None
