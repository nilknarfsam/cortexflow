"""Métricas agregadas para o Knowledge Dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.settings_service import SettingsService
from src.knowledge_graph import get_knowledge_graph
from src.library import get_library


@dataclass
class KnowledgeDashboardStats:
    documents: int = 0
    chunks: int = 0
    flashcards: int = 0
    quizzes: int = 0
    topics: int = 0
    relations: int = 0
    workspaces: int = 0
    collections: int = 0
    datasets: int = 0
    avg_readiness_score: float = 0.0
    cache_hits: int = 0
    cache_total: int = 0
    avg_processing_seconds: float = 0.0

    def to_cards(self) -> list[tuple[str, str, str]]:
        cache_pct = (
            f"{100 * self.cache_hits // self.cache_total}%"
            if self.cache_total
            else "—"
        )
        avg_time = (
            f"{self.avg_processing_seconds:.1f}s"
            if self.avg_processing_seconds > 0
            else "—"
        )
        readiness = (
            f"{self.avg_readiness_score:.0f}"
            if self.avg_readiness_score > 0
            else "—"
        )
        return [
            ("Documentos", str(self.documents), "catalog"),
            ("Datasets", str(self.datasets), "dataset"),
            ("Readiness", readiness, "readiness"),
            ("Chunks", str(self.chunks), "chunk"),
            ("Flashcards", str(self.flashcards), "flashcard"),
            ("Quizzes", str(self.quizzes), "quiz"),
            ("Tópicos", str(self.topics), "topic"),
            ("Relações", str(self.relations), "relation"),
            ("Cache hits", cache_pct, "cache"),
            ("Tempo médio", avg_time, "time"),
        ]


def compute_dashboard_stats(settings: SettingsService | None = None) -> KnowledgeDashboardStats:
    lib = get_library()
    lib.catalog.load()
    graph = get_knowledge_graph()
    graph.load()

    lib_stats = lib.stats()
    gstats = graph.stats or {}

    flashcards = int(gstats.get("flashcards", 0))
    quizzes = int(gstats.get("quizzes", 0))

    cache_hits = 0
    cache_total = 0
    try:
        from src.cache.cache_engine import CacheEngine

        cstats = CacheEngine().stats()
        cache_total = int(cstats.get("entries", 0) or 0)
        cache_hits = cache_total
    except Exception:
        pass

    avg_seconds = 0.0
    count = 0
    history_cache_hits = 0
    history_completed = 0
    if settings:
        for row in settings.history:
            if row.get("status") != "concluído":
                continue
            history_completed += 1
            if row.get("cache_hit") == "sim":
                history_cache_hits += 1
            pt = str(row.get("processing_time", "")).replace("s", "").strip()
            try:
                avg_seconds += float(pt)
                count += 1
            except ValueError:
                pass
    if history_completed:
        cache_hits = history_cache_hits
        cache_total = max(cache_total, history_completed)
    if count:
        avg_seconds /= count

    datasets_count = 0
    avg_readiness = 0.0
    try:
        from src.datasets.statistics.dataset_stats import compute_dataset_statistics
        from src.datasets.registry.dataset_registry import get_dataset_registry

        reg = get_dataset_registry()
        dstats = compute_dataset_statistics(
            reg.knowledge_datasets,
            reg.chunk_datasets,
            reg.knowledge_index,
        )
        datasets_count = dstats.total_datasets
        avg_readiness = dstats.avg_readiness_score
    except Exception:
        pass

    return KnowledgeDashboardStats(
        documents=lib_stats.documents,
        chunks=lib_stats.chunks,
        flashcards=flashcards,
        quizzes=quizzes,
        topics=int(gstats.get("topics", lib_stats.topics)),
        relations=int(gstats.get("total_edges", 0)),
        workspaces=lib_stats.workspaces,
        collections=lib_stats.collections,
        datasets=datasets_count,
        avg_readiness_score=avg_readiness,
        cache_hits=cache_hits,
        cache_total=cache_total,
        avg_processing_seconds=avg_seconds,
    )
