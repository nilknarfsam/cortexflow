"""Constrói datasets independentes por chunk."""

from __future__ import annotations

from typing import Any


class ChunkDatasetBuilder:
    def build_all(
        self,
        *,
        document_id: str,
        workspace: str = "",
        collection: str = "",
        topics: list[str] | None = None,
        references: list[Any] | None = None,
        chunks: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        doc_topics = list(topics or [])
        doc_refs = self._refs_as_strings(references or [])

        for chunk in chunks or []:
            chunk_id = str(chunk.get("chunk_id") or chunk.get("id") or "")
            if not chunk_id:
                continue
            chunk_topics = list(chunk.get("topics") or doc_topics)
            records.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "workspace": workspace,
                    "collection": collection,
                    "topics": chunk_topics,
                    "references": doc_refs,
                    "content": str(chunk.get("content", "")),
                    "metadata": dict(chunk.get("metadata") or {}),
                }
            )
        return records

    @staticmethod
    def _refs_as_strings(refs: list[Any]) -> list[str]:
        out: list[str] = []
        for r in refs:
            if isinstance(r, dict):
                book = r.get("book") or r.get("reference") or ""
                if book:
                    out.append(str(book))
            elif r:
                out.append(str(r))
        return out[:40]
