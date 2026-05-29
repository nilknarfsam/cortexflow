"""Painel Grafo / Conexões — busca semântica e navegação."""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from src.knowledge_graph import get_knowledge_graph
from src.knowledge_graph.graph_stats import stats_display
from src.ui.design.fonts import body_small, caption, panel_title
from src.ui.design.spacing import Layout
from src.ui.design.theme_manager import ThemeManager


class GraphPanel(ctk.CTkFrame):
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
        self._graph = get_knowledge_graph()

        self._apply_frame_style()
        self._build_header()
        self._build_stats()
        self._build_search()
        self._build_results()
        self._build_topic()
        self.refresh()

    def _apply_frame_style(self) -> None:
        self.configure(**self.theme.frame_kwargs(elevated=True))

    def refresh_theme(self) -> None:
        self._apply_frame_style()
        colors = self.theme.colors()
        self.stats_label.configure(text_color=colors["text_secondary"])
        self.refresh()

    def _build_header(self) -> None:
        colors = self.theme.colors()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=Layout.LG, pady=(Layout.LG, Layout.SM))
        ctk.CTkLabel(
            header,
            text="Grafo / Conexões",
            font=panel_title(),
            text_color=colors["text_primary"],
        ).pack(side="left")
        ctk.CTkButton(
            header,
            text="Reconstruir grafo",
            width=130,
            command=self._rebuild,
            **self.theme.ghost_button_kwargs(),
        ).pack(side="right", padx=(Layout.SM, 0))
        ctk.CTkButton(
            header,
            text="Exportar MD",
            width=100,
            command=self._export,
            **self.theme.ghost_button_kwargs(),
        ).pack(side="right")

    def _build_stats(self) -> None:
        colors = self.theme.colors()
        self.stats_label = ctk.CTkLabel(
            self,
            text="",
            font=caption(),
            text_color=colors["text_secondary"],
            anchor="w",
            justify="left",
        )
        self.stats_label.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))

    def _build_search(self) -> None:
        colors = self.theme.colors()
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=Layout.LG, pady=(0, Layout.SM))
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="Busca semântica",
            font=body_small(),
            text_color=colors["text_secondary"],
        ).grid(row=0, column=0, sticky="w", padx=(0, Layout.SM))
        self.search_entry = ctk.CTkEntry(
            row,
            placeholder_text="tópico, referência, tag, chunk, flashcard…",
        )
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<Return>", lambda _e: self._run_search())
        ctk.CTkButton(
            row,
            text="Buscar",
            width=80,
            command=self._run_search,
            **self.theme.accent_button_kwargs(),
        ).grid(row=0, column=2, padx=(Layout.SM, 0))

    def _build_results(self) -> None:
        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            label_text="Resultados conectados",
            fg_color="transparent",
        )
        self.results_scroll.pack(fill="both", expand=True, padx=Layout.LG, pady=(0, Layout.SM))

    def _build_topic(self) -> None:
        colors = self.theme.colors()
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=Layout.LG, pady=(0, Layout.LG))
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="Navegar tópico",
            font=body_small(),
            text_color=colors["text_secondary"],
        ).grid(row=0, column=0, sticky="w", padx=(0, Layout.SM))
        self.topic_entry = ctk.CTkEntry(row, placeholder_text="ex.: ressurreição")
        self.topic_entry.grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(
            row,
            text="Explorar",
            width=80,
            command=self._explore_topic,
            **self.theme.ghost_button_kwargs(),
        ).grid(row=0, column=2, padx=(Layout.SM, 0))

    def refresh(self) -> None:
        self._graph.load()
        self.stats_label.configure(text=stats_display(self._graph.stats))

    def _rebuild(self) -> None:
        try:
            self._graph.rebuild()
            self.refresh()
            if self.on_status:
                self.on_status("Grafo de conhecimento reconstruído.")
        except OSError as exc:
            if self.on_status:
                self.on_status(f"Erro ao reconstruir grafo: {exc}")

    def _export(self) -> None:
        try:
            path = self._graph.export_markdown()
            if self.on_status:
                self.on_status(f"Grafo exportado: {path}")
        except OSError as exc:
            if self.on_status:
                self.on_status(f"Erro na exportação: {exc}")

    def _run_search(self) -> None:
        query = self.search_entry.get().strip()
        for w in self.results_scroll.winfo_children():
            w.destroy()
        colors = self.theme.colors()

        if not query:
            ctk.CTkLabel(
                self.results_scroll,
                text="Digite um termo para busca semântica local.",
                font=body_small(),
                text_color=colors["text_muted"],
            ).pack(anchor="w")
            return

        result = self._graph.search.search(query)
        self._section(
            f"Documentos ({len(result.documents)})",
            result.documents,
            lambda i: f"{i.get('label', '')} — score {i.get('score', 0)}",
        )
        self._section(
            f"Chunks ({len(result.chunks)})",
            result.chunks,
            lambda i: str(i.get("label", ""))[:80],
        )
        self._section(
            f"Flashcards ({len(result.flashcards)})",
            result.flashcards,
            lambda i: str(i.get("label", ""))[:80],
        )
        self._section(
            f"Quizzes ({len(result.quizzes)})",
            result.quizzes,
            lambda i: str(i.get("label", ""))[:80],
        )
        self._section(
            f"Tópicos ({len(result.topics)})",
            result.topics,
            lambda i: str(i.get("label", "")),
        )
        self._section(
            f"Referências ({len(result.references)})",
            result.references,
            lambda i: str(i.get("label", "")),
        )
        if result.connection_reasons:
            ctk.CTkLabel(
                self.results_scroll,
                text=f"Motivos: {', '.join(result.connection_reasons[:12])}",
                font=caption(),
                text_color=colors["text_muted"],
                wraplength=680,
                justify="left",
            ).pack(anchor="w", pady=Layout.SM)

        if self.on_status:
            self.on_status(f"Busca semântica: {result.total_hits} correspondência(s).")

    def _explore_topic(self) -> None:
        topic = self.topic_entry.get().strip()
        if not topic:
            return
        nav = self._graph.topics.explore(topic)
        for w in self.results_scroll.winfo_children():
            w.destroy()
        colors = self.theme.colors()
        ctk.CTkLabel(
            self.results_scroll,
            text=f"Tópico: {nav.get('topic', topic)} — {nav.get('total_connections', 0)} conexões",
            font=body_small(),
            text_color=colors["text_primary"],
        ).pack(anchor="w", pady=(0, Layout.SM))
        self._section(
            "Documentos",
            nav.get("documents", []),
            lambda i: f"{i.get('title', '')} ({i.get('collection', '—')})",
        )
        self._section("Chunks", nav.get("chunks", []), lambda i: str(i.get("label", ""))[:70])
        self._section("Flashcards", nav.get("flashcards", []), lambda i: str(i.get("label", ""))[:70])
        self._section("Quizzes", nav.get("quizzes", []), lambda i: str(i.get("label", ""))[:70])
        self._section("Referências", nav.get("references", []), lambda i: str(i.get("reference") or i.get("label", "")))
        if self.on_status:
            self.on_status(f"Tópico «{topic}»: {nav.get('total_connections', 0)} itens.")

    def show_related(self, catalog_id: str, title: str = "") -> None:
        """Exibe documentos relacionados a um catalog_id (chamado pela Biblioteca)."""
        for w in self.results_scroll.winfo_children():
            w.destroy()
        colors = self.theme.colors()
        related = self._graph.related.find_related(catalog_id)
        heading = title or catalog_id
        ctk.CTkLabel(
            self.results_scroll,
            text=f"Relacionados a: {heading[:60]}",
            font=body_small(),
            text_color=colors["text_primary"],
        ).pack(anchor="w", pady=(0, Layout.SM))
        if not related:
            ctk.CTkLabel(
                self.results_scroll,
                text="Nenhum documento relacionado encontrado.",
                font=caption(),
                text_color=colors["text_muted"],
            ).pack(anchor="w")
            return
        for rel in related:
            reasons = ", ".join(rel.get("reasons", []))
            line = f"{rel.get('title', rel.get('document_id', ''))} — score {rel.get('score', 0):.1f}"
            if reasons:
                line += f" · {reasons}"
            ctk.CTkLabel(
                self.results_scroll,
                text=line,
                font=caption(),
                text_color=colors["text_secondary"],
                anchor="w",
                wraplength=700,
                justify="left",
            ).pack(anchor="w", pady=2)

    def _section(self, title: str, items: list, fmt: Callable) -> None:
        if not items:
            return
        colors = self.theme.colors()
        ctk.CTkLabel(
            self.results_scroll,
            text=title,
            font=body_small(),
            text_color=colors["text_primary"],
        ).pack(anchor="w", pady=(Layout.SM, Layout.XS))
        for item in items[:15]:
            ctk.CTkLabel(
                self.results_scroll,
                text=f"  · {fmt(item)}",
                font=caption(),
                text_color=colors["text_muted"],
                anchor="w",
                wraplength=680,
                justify="left",
            ).pack(anchor="w")
