"""Dataset Explorer — visualização e exportação de datasets de conhecimento."""

from __future__ import annotations

import json
import os
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from src.datasets.exporters.dataset_exporter import DatasetExporter
from src.datasets.registry.dataset_registry import DATASETS_DIR, get_dataset_registry
from src.datasets.statistics.dataset_stats import compute_dataset_statistics
from src.datasets.validators.dataset_validator import DatasetValidator
from src.models.transcription_job import JobStatus, TranscriptionJob
from src.ui.design.fonts import body_small, caption, panel_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager


class DatasetPanel(ctk.CTkFrame):
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
        self._selected_dataset_id: str | None = None

        self._apply_frame_style()
        self._build_header()
        self._build_stats()
        self._build_list()
        self._build_actions()
        self._build_preview()
        self.refresh()

    def _apply_frame_style(self) -> None:
        self.configure(**self.theme.frame_kwargs(elevated=True))

    def refresh_theme(self) -> None:
        self._apply_frame_style()
        colors = self.theme.colors()
        self.stats_label.configure(text_color=colors["text_secondary"])
        self.preview.configure(text_color=colors["text_primary"])

    def _build_header(self) -> None:
        colors = self.theme.colors()
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=Layout.LG, pady=(Layout.LG, Layout.SM))

        ctk.CTkLabel(
            row,
            text="Dataset Explorer",
            font=panel_title(),
            text_color=colors["text_primary"],
        ).pack(side="left")

        self.readiness_badge = ctk.CTkLabel(
            row,
            text="Readiness —",
            font=caption(),
            text_color="#FFFFFF",
            fg_color=colors["accent"],
            corner_radius=6,
            padx=8,
            pady=2,
        )
        self.readiness_badge.pack(side="right")

    def _build_stats(self) -> None:
        colors = self.theme.colors()
        self.stats_label = ctk.CTkLabel(
            self,
            text="Carregando estatísticas…",
            font=caption(),
            text_color=colors["text_secondary"],
            anchor="w",
            justify="left",
        )
        self.stats_label.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))

    def _build_list(self) -> None:
        colors = self.theme.colors()
        list_frame = ctk.CTkFrame(self, fg_color=colors["card_bg"], corner_radius=Layout.CORNER_RADIUS_CARD)
        list_frame.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))
        list_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            list_frame,
            text="Datasets gerados",
            font=body_small(),
            text_color=colors["text_muted"],
        ).grid(row=0, column=0, sticky="w", padx=Layout.MD, pady=(Layout.SM, 0))

        self.dataset_menu = ctk.CTkOptionMenu(
            list_frame,
            values=["(nenhum)"],
            command=self._on_dataset_selected,
            width=400,
        )
        self.dataset_menu.grid(row=1, column=0, sticky="ew", padx=Layout.MD, pady=Layout.SM)

    def _build_actions(self) -> None:
        colors = self.theme.colors()
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))

        ctk.CTkButton(
            row,
            text="Abrir pasta data/datasets",
            command=self._open_datasets_folder,
            fg_color=colors["surface_elevated"],
            text_color=colors["text_primary"],
            width=180,
        ).pack(side="left", padx=(0, Layout.SM))

        ctk.CTkButton(
            row,
            text="Exportar dataset",
            command=self._export_selected,
            fg_color=colors["accent"],
            width=140,
        ).pack(side="left", padx=(0, Layout.SM))

        ctk.CTkButton(
            row,
            text="Validar datasets",
            command=self._validate_datasets,
            fg_color=colors["surface_elevated"],
            text_color=colors["text_primary"],
            width=140,
        ).pack(side="left")

    def _build_preview(self) -> None:
        colors = self.theme.colors()
        self.preview = ctk.CTkTextbox(
            self,
            font=body_small(),
            text_color=colors["text_primary"],
            fg_color=colors["card_bg"],
            corner_radius=Layout.CORNER_RADIUS_CARD,
            wrap="word",
        )
        self.preview.pack(fill="both", expand=True, padx=Layout.LG, pady=(0, Layout.LG))

    def refresh(self) -> None:
        reg = get_dataset_registry()
        reg.load()
        stats = compute_dataset_statistics(
            reg.knowledge_datasets,
            reg.chunk_datasets,
            reg.knowledge_index,
        )
        self.stats_label.configure(
            text=(
                f"{stats.total_datasets} datasets · {stats.total_chunks} chunks · "
                f"{stats.total_topics} tópicos · {stats.total_references} referências · "
                f"{stats.total_flashcards} flashcards · {stats.total_quizzes} quizzes · "
                f"readiness médio: {stats.avg_readiness_score:.0f}/100"
            )
        )
        self.readiness_badge.configure(
            text=f"Readiness médio {stats.avg_readiness_score:.0f}"
            if stats.avg_readiness_score > 0
            else "Readiness —"
        )

        ids = sorted(reg.knowledge_datasets.keys())
        labels = []
        id_map: dict[str, str] = {}
        for ds_id in ids:
            ds = reg.knowledge_datasets[ds_id]
            title = str(ds.get("title", ds_id))[:40]
            chunks_n = len(ds.get("chunks") or [])
            ver = str(ds.get("dataset_version", "?"))
            label = f"{title} · {chunks_n} chunks · v{ver}"
            labels.append(label)
            id_map[label] = ds_id

        self._id_map = id_map
        if not labels:
            self.dataset_menu.configure(values=["(nenhum)"])
            self.dataset_menu.set("(nenhum)")
            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", "Processe documentos em modo ai_ready, notebooklm ou study_mode para gerar datasets.")
            return

        self.dataset_menu.configure(values=labels)
        if self._selected_dataset_id and self._selected_dataset_id in ids:
            for lbl, did in id_map.items():
                if did == self._selected_dataset_id:
                    self.dataset_menu.set(lbl)
                    self._show_dataset(did)
                    return
        self.dataset_menu.set(labels[0])
        self._on_dataset_selected(labels[0])

    def show_job(self, job: TranscriptionJob | None) -> None:
        if not job or job.status != JobStatus.COMPLETED:
            return
        meta = job.dataset_metadata or {}
        ds_id = str(meta.get("dataset_id", ""))
        if ds_id:
            self._selected_dataset_id = ds_id
            self.refresh()

    def _on_dataset_selected(self, label: str) -> None:
        ds_id = getattr(self, "_id_map", {}).get(label)
        if ds_id:
            self._selected_dataset_id = ds_id
            self._show_dataset(ds_id)

    def _show_dataset(self, dataset_id: str) -> None:
        reg = get_dataset_registry()
        ds = reg.get_knowledge(dataset_id)
        if not ds:
            return
        score = (ds.get("metadata") or {}).get("knowledge_readiness_score", "—")
        self.readiness_badge.configure(text=f"Readiness {score}/100")
        preview = {
            "dataset_id": ds.get("dataset_id"),
            "document_id": ds.get("document_id"),
            "title": ds.get("title"),
            "workspace": ds.get("workspace"),
            "collection": ds.get("collection"),
            "topics": ds.get("topics"),
            "chunks_count": len(ds.get("chunks") or []),
            "flashcards_count": len(ds.get("flashcards") or []),
            "quizzes_count": len(ds.get("quizzes") or []),
            "dataset_version": ds.get("dataset_version"),
            "updated_at": ds.get("updated_at"),
        }
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", json.dumps(preview, ensure_ascii=False, indent=2))

    def _open_datasets_folder(self) -> None:
        DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        os.startfile(str(DATASETS_DIR))
        if self.on_status:
            self.on_status("Pasta data/datasets aberta.")

    def _export_selected(self) -> None:
        if not self._selected_dataset_id:
            mb.showinfo("Datasets", "Nenhum dataset selecionado.")
            return
        dest = fd.askdirectory(title="Pasta para exportar dataset")
        if not dest:
            return
        path = DatasetExporter().export_dataset_copy(self._selected_dataset_id, Path(dest))
        if path:
            mb.showinfo("Exportação", f"Dataset salvo em:\n{path}")
            if self.on_status:
                self.on_status(f"Dataset exportado: {os.path.basename(path)}")
        else:
            mb.showerror("Erro", "Não foi possível exportar o dataset.")

    def _validate_datasets(self) -> None:
        reg = get_dataset_registry()
        report = DatasetValidator().validate_all(
            reg.knowledge_datasets,
            reg.chunk_datasets,
            reg.knowledge_index,
        )
        paths = DatasetExporter().export_all()
        status = "válidos" if report.valid else "com erros"
        msg = (
            f"Datasets {status}.\n"
            f"Verificados: {report.datasets_checked} knowledge, {report.chunks_checked} chunks.\n"
            f"Erros: {len(report.errors)}\n"
            f"Avisos: {len(report.warnings)}\n\n"
            f"Relatório: {paths.get('dataset_validation_report', '')}"
        )
        mb.showinfo("Validação de datasets", msg)
        if self.on_status:
            self.on_status(f"Validação concluída — {status}.")
