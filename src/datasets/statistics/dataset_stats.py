"""Estatísticas agregadas dos datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DatasetStatistics:
    total_datasets: int = 0
    total_chunks: int = 0
    total_topics: int = 0
    total_references: int = 0
    total_flashcards: int = 0
    total_quizzes: int = 0
    total_workspaces: int = 0
    total_collections: int = 0
    avg_readiness_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_datasets": self.total_datasets,
            "total_chunks": self.total_chunks,
            "total_topics": self.total_topics,
            "total_references": self.total_references,
            "total_flashcards": self.total_flashcards,
            "total_quizzes": self.total_quizzes,
            "total_workspaces": self.total_workspaces,
            "total_collections": self.total_collections,
            "avg_readiness_score": round(self.avg_readiness_score, 1),
        }


def compute_dataset_statistics(
    knowledge_datasets: dict[str, dict[str, Any]],
    chunk_datasets: dict[str, dict[str, Any]],
    knowledge_index: dict[str, Any] | None = None,
) -> DatasetStatistics:
    topics: set[str] = set()
    refs: set[str] = set()
    workspaces: set[str] = set()
    collections: set[str] = set()
    flashcards = 0
    quizzes = 0
    readiness_sum = 0.0
    readiness_n = 0

    for ds in knowledge_datasets.values():
        for t in ds.get("topics") or []:
            if str(t).strip():
                topics.add(str(t).strip())
        for r in ds.get("references") or []:
            if str(r).strip():
                refs.add(str(r).strip())
        ws = str(ds.get("workspace", "")).strip()
        if ws:
            workspaces.add(ws)
        col = str(ds.get("collection", "")).strip()
        if col:
            collections.add(col)
        flashcards += len(ds.get("flashcards") or [])
        quizzes += len(ds.get("quizzes") or [])
        meta = ds.get("metadata") or {}
        score = meta.get("knowledge_readiness_score")
        if score is not None:
            try:
                readiness_sum += float(score)
                readiness_n += 1
            except (TypeError, ValueError):
                pass

    if knowledge_index:
        topics.update(str(k).replace("::chunk", "") for k in (knowledge_index.get("topics_index") or {}))
        workspaces.update((knowledge_index.get("workspaces_index") or {}).keys())
        collections.update((knowledge_index.get("collections_index") or {}).keys())

    return DatasetStatistics(
        total_datasets=len(knowledge_datasets),
        total_chunks=len(chunk_datasets),
        total_topics=len(topics),
        total_references=len(refs),
        total_flashcards=flashcards,
        total_quizzes=quizzes,
        total_workspaces=len(workspaces),
        total_collections=len(collections),
        avg_readiness_score=readiness_sum / readiness_n if readiness_n else 0.0,
    )
