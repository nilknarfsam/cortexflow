from __future__ import annotations

import json
import os
from typing import Callable, Optional

import customtkinter as ctk

from src.models.transcription_job import TranscriptionJob
from src.study.study_engine import StudyResult
from src.ui.design.colors import SEMANTIC
from src.ui.design.fonts import body_small, caption, panel_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager


class StudyPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        theme: ThemeManager,
        on_status: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.theme = theme
        self.on_status = on_status
        self._study: Optional[StudyResult] = None

        self._apply_frame_style()
        self._build_header()
        self._build_stats()
        self._build_previews()

    def _apply_frame_style(self) -> None:
        self.configure(**self.theme.frame_kwargs(elevated=True))

    def refresh_theme(self) -> None:
        self._apply_frame_style()
        colors = self.theme.colors()
        self.stats_label.configure(text_color=colors["text_secondary"])
        for box in (self.flash_preview, self.quiz_preview, self.review_preview):
            box.configure(text_color=colors["text_primary"])

    def _build_header(self) -> None:
        colors = self.theme.colors()
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=Layout.LG, pady=(Layout.LG, Layout.SM))

        ctk.CTkLabel(
            row,
            text="Inteligência Educacional",
            font=panel_title(),
            text_color=colors["text_primary"],
        ).pack(side="left")

        self.study_badge = ctk.CTkLabel(
            row,
            text="Study Ready",
            font=caption(),
            text_color="#FFFFFF",
            fg_color=colors["border"],
            corner_radius=6,
            padx=8,
            pady=2,
        )
        self.study_badge.pack(side="left", padx=(Layout.SM, 0))
        self.study_badge.pack_forget()

    def _build_stats(self) -> None:
        colors = self.theme.colors()
        self.stats_label = ctk.CTkLabel(
            self,
            text="Selecione um item processado em modo Study ou visualize após concluir a fila.",
            font=caption(),
            text_color=colors["text_secondary"],
            anchor="w",
            justify="left",
        )
        self.stats_label.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))

    def _build_previews(self) -> None:
        colors = self.theme.colors()
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=Layout.LG, pady=(0, Layout.LG))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_rowconfigure(0, weight=1)
        grid.grid_rowconfigure(1, weight=1)

        self.flash_preview = self._preview_box(grid, "Flashcards", 0, 0)
        self.quiz_preview = self._preview_box(grid, "Quizzes", 0, 1)
        self.review_preview = self._preview_box(grid, "Revisão Rápida", 1, 0, colspan=2)

    def _preview_box(self, parent, title: str, row: int, col: int, *, colspan: int = 1) -> ctk.CTkTextbox:
        frame = ctk.CTkFrame(parent, fg_color=self.theme.colors()["card_bg"], corner_radius=Layout.CORNER_RADIUS_CARD)
        frame.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=Layout.XS, pady=Layout.XS)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=title, font=body_small()).grid(row=0, column=0, sticky="w", padx=Layout.SM, pady=Layout.SM)
        box = ctk.CTkTextbox(frame, height=120, font=body_small())
        box.grid(row=1, column=0, sticky="nsew", padx=Layout.SM, pady=(0, Layout.SM))
        box.configure(state="disabled")
        return box

    def show_job(self, job: Optional[TranscriptionJob]) -> None:
        colors = self.theme.colors()
        if not job or job.status.value != "concluído":
            self.study_badge.pack_forget()
            self.stats_label.configure(
                text="Processe conteúdo com modo de exportação «study_mode» para gerar materiais de estudo."
            )
            self._clear_previews("Nenhum material de estudo disponível.")
            return

        sm = job.study_metadata or {}
        if not sm.get("study_ready") and not sm.get("study_package"):
            self.study_badge.pack_forget()
            self.stats_label.configure(text="Este item não foi processado em study_mode.")
            self._clear_previews("Ative «study_mode» nas configurações e reprocesse.")
            return

        self.study_badge.configure(fg_color=SEMANTIC["success"])
        self.study_badge.pack(side="left", padx=(Layout.SM, 0))

        fc = sm.get("flashcards_count", 0)
        qz = sm.get("quizzes_count", 0)
        diff = sm.get("difficulty", "—")
        exports = sm.get("study_exports", {})
        if isinstance(exports, dict):
            export_txt = ", ".join(os.path.basename(p) for p in exports.values())
        else:
            export_txt = str(exports) if exports else "—"

        self.stats_label.configure(
            text=(
                f"{job.file_name}  ·  Flashcards: {fc}  ·  Quizzes: {qz}  ·  "
                f"Dificuldade: {diff}  ·  Exports: {export_txt}"
            )
        )

        package = sm.get("study_package", {})
        if not package and exports:
            package = self._load_package_from_exports(exports)
        if package:
            self._study = StudyResult.from_package(package)
            self._fill_previews(self._study)
        else:
            self._clear_previews("Pacote de estudo não encontrado.")

    def _load_package_from_exports(self, exports: dict) -> dict:
        fc_path = exports.get("flashcards", "")
        if fc_path and os.path.isfile(fc_path):
            try:
                with open(fc_path, encoding="utf-8") as f:
                    data = json.load(f)
                return {
                    "flashcards": data.get("flashcards", []),
                    "quizzes": [],
                    "flashcards_count": data.get("count", 0),
                    "study_ready": True,
                }
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _fill_previews(self, study: StudyResult) -> None:
        flash_lines = []
        for card in study.flashcards[:8]:
            flash_lines.append(f"Q: {card.get('question', '')[:120]}")
            flash_lines.append(f"A: {card.get('answer', '')[:120]}")
            flash_lines.append("")
        self._set_box(self.flash_preview, "\n".join(flash_lines) or "(sem flashcards)")

        quiz_lines = []
        for q in study.quizzes[:6]:
            quiz_lines.append(f"• [{q.get('type', '')}] {q.get('question', '')[:100]}")
            opts = q.get("options") or []
            if opts:
                quiz_lines.append(f"  → {', '.join(str(o) for o in opts[:4])}")
        self._set_box(self.quiz_preview, "\n".join(quiz_lines) or "(sem quizzes)")

        review = study.quick_review_md[:2500] if study.quick_review_md else "(sem revisão)"
        self._set_box(self.review_preview, review)

    def _clear_previews(self, message: str) -> None:
        for box in (self.flash_preview, self.quiz_preview, self.review_preview):
            self._set_box(box, message)

    @staticmethod
    def _set_box(box: ctk.CTkTextbox, text: str) -> None:
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")
