"""Índices globais a partir dos datasets registrados."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class KnowledgeIndexBuilder:
    def build(
        self,
        knowledge_datasets: dict[str, dict[str, Any]],
        chunk_datasets: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        topics_index: dict[str, list[str]] = defaultdict(list)
        references_index: dict[str, list[str]] = defaultdict(list)
        authors_index: dict[str, list[str]] = defaultdict(list)
        speakers_index: dict[str, list[str]] = defaultdict(list)
        collections_index: dict[str, list[str]] = defaultdict(list)
        workspaces_index: dict[str, list[str]] = defaultdict(list)

        for ds_id, ds in knowledge_datasets.items():
            doc_id = str(ds.get("document_id", ""))
            if not doc_id:
                continue
            for topic in ds.get("topics") or []:
                t = str(topic).strip()
                if t and doc_id not in topics_index[t]:
                    topics_index[t].append(doc_id)
            for ref in ds.get("references") or []:
                r = str(ref).strip()
                if r and doc_id not in references_index[r]:
                    references_index[r].append(doc_id)
            author = str(ds.get("author", "")).strip()
            if author and doc_id not in authors_index[author]:
                authors_index[author].append(doc_id)
            speaker = str(ds.get("speaker", "")).strip()
            if speaker and doc_id not in speakers_index[speaker]:
                speakers_index[speaker].append(doc_id)
            col = str(ds.get("collection", "")).strip()
            if col and doc_id not in collections_index[col]:
                collections_index[col].append(doc_id)
            ws = str(ds.get("workspace", "")).strip()
            if ws and doc_id not in workspaces_index[ws]:
                workspaces_index[ws].append(doc_id)

        for chunk_id, ch in chunk_datasets.items():
            doc_id = str(ch.get("document_id", ""))
            if not doc_id:
                continue
            for topic in ch.get("topics") or []:
                t = str(topic).strip()
                key = f"{t}::chunk"
                if t and chunk_id not in topics_index.get(key, []):
                    topics_index.setdefault(key, []).append(chunk_id)

        return {
            "topics_index": dict(topics_index),
            "references_index": dict(references_index),
            "authors_index": dict(authors_index),
            "speakers_index": dict(speakers_index),
            "collections_index": dict(collections_index),
            "workspaces_index": dict(workspaces_index),
            "document_count": len(knowledge_datasets),
            "chunk_count": len(chunk_datasets),
        }
