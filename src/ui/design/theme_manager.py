"""Gerencia tema CustomTkinter e paleta CortexFlow."""

from __future__ import annotations

from typing import Literal

import customtkinter as ctk

from src.ui.design.colors import BRAND, DARK, LIGHT, SEMANTIC, STATUS

PaletteKey = Literal["light", "dark"]


class ThemeManager:
    def __init__(self, initial_mode: str = "System") -> None:
        self._user_mode = initial_mode

    @property
    def user_mode(self) -> str:
        return self._user_mode

    def apply(self, mode: str) -> None:
        self._user_mode = mode
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")


    def resolved_palette(self) -> PaletteKey:
        mode = ctk.get_appearance_mode()
        if mode == "Light":
            return "light"
        if mode == "Dark":
            return "dark"
        return "dark"

    def colors(self) -> dict[str, str]:
        base = LIGHT if self.resolved_palette() == "light" else DARK
        return {**base, **BRAND}

    def status_color(self, status_key: str) -> str:
        pair = STATUS.get(status_key, STATUS["waiting"])
        idx = 0 if self.resolved_palette() == "light" else 1
        return pair[idx]

    def primary_button_kwargs(self) -> dict:
        return {
            "fg_color": BRAND["primary"],
            "hover_color": BRAND["primary_hover"],
        }

    def accent_button_kwargs(self) -> dict:
        return {
            "fg_color": BRAND["accent"],
            "hover_color": BRAND["accent_hover"],
            "text_color": "#FFFFFF",
        }

    def danger_button_kwargs(self) -> dict:
        return {
            "fg_color": SEMANTIC["danger"],
            "hover_color": SEMANTIC["danger_hover"],
        }

    def warning_button_kwargs(self) -> dict:
        return {
            "fg_color": SEMANTIC["warning"],
            "hover_color": SEMANTIC["warning_hover"],
        }

    def ghost_button_kwargs(self) -> dict:
        c = self.colors()
        return {
            "fg_color": "transparent",
            "border_width": 1,
            "border_color": c["border"],
            "text_color": c["text_primary"],
        }

    def frame_kwargs(self, *, elevated: bool = False) -> dict:
        c = self.colors()
        fg = c["surface_elevated"] if elevated else c["card_bg"]
        return {
            "fg_color": fg,
            "border_color": c["border"],
            "border_width": 1,
            "corner_radius": 12,
        }

    def sidebar_kwargs(self) -> dict:
        c = self.colors()
        return {
            "fg_color": c["sidebar"],
            "corner_radius": 12,
        }
