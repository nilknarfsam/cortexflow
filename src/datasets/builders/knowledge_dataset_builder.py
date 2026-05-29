"""Constrói dataset completo por documento."""

from __future__ import annotations

import uuid
from typing import Any


class KnowledgeDatasetBuilder:
    def build(
        self,
        *,
        document_id: str,
        title: str,
        workspace: str = "",
        collection: str = "",
        author: str = "",
        speaker: str = "",
        topics: list[str] | None = None,
        references: list[Any] | None = None,
        difficulty: str = "",
        highlights: list[str] | None = None,
        chunks: list[dict[str, Any]] | None = None,
        flashcards: list[dict[str, Any]] | None = None,
        quizzes: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
        dataset_id: str | None = None,
    ) -> dict[str, Any]:
        refs = self._normalize_references(references or [])
        chunk_list = list(chunks or [])
        return {
            "dataset_id": dataset_id or f"ds-{uuid.uuid4().hex[:12]}",
            "document_id": document_id,
            "title": title,
            "workspace": workspace,
            "collection": collection,
            "author": author,
            "speaker": speaker,
            "topics": list(topics or []),
            "references": refs,
            "difficulty": difficulty or "básico",
            "highlights": [str(h) for h in (highlights or [])[:50]],
            "chunks": chunk_list,
            "flashcards": list(flashcards or []),
            "quizzes": list(quizzes or []),
            "metadata": dict(metadata or {}),
        }

    @staticmethod
    def _normalize_references(refs: list[Any]) -> list[str]:
        out: list[str] = []
        for r in refs:
            if isinstance(r, dict):
                book = r.get("book") or r.get("reference") or ""
                chapter = r.get("chapter", "")
                verse = r.get("verse", "")
                if book:
                    out.append(f"{book} {chapter}:{verse}".strip(" :"))
            else:
                s = str(r).strip()
                if s:
                    out.append(s)
        return out[:80]
