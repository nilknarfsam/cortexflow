"""Transforma dados do catálogo e estudo em nós do grafo."""

from __future__ import annotations

import re
from typing import Any

from src.library.catalog.catalog_registry import CatalogEntry

_NODE_TYPES = frozenset({
    "document",
    "topic",
    "tag",
    "speaker",
    "author",
    "collection",
    "workspace",
    "bible_reference",
    "chunk",
    "flashcard",
    "quiz",
})


def slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    return (s[:64] or "unknown").strip("-")


def make_node_id(node_type: str, key: str) -> str:
    return f"{node_type}:{slugify(key)}"


def document_node_id(catalog_id: str) -> str:
    return f"document:{catalog_id}"


class NodeBuilder:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}

    @property
    def nodes(self) -> dict[str, dict[str, Any]]:
        return self._nodes

    def clear(self) -> None:
        self._nodes.clear()

    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if node_type not in _NODE_TYPES:
            node_type = "document"
        node = {
            "node_id": node_id,
            "type": node_type,
            "label": label[:200] if label else node_id,
            "metadata": metadata or {},
        }
        self._nodes[node_id] = node
        return node

    def get(self, node_id: str) -> dict[str, Any] | None:
        return self._nodes.get(node_id)

    def build_workspace_nodes(self, workspaces: dict[str, dict[str, Any]]) -> None:
        for ws in workspaces.values():
            ws_id = str(ws.get("id", ""))
            if not ws_id:
                continue
            node_id = f"workspace:{ws_id}"
            self.add_node(
                node_id,
                "workspace",
                str(ws.get("name", ws_id)),
                {"workspace_id": ws_id, "description": str(ws.get("description", ""))},
            )

    def build_collection_nodes(self, collections: dict[str, dict[str, Any]]) -> None:
        for col in collections.values():
            col_id = str(col.get("id", ""))
            if not col_id:
                continue
            node_id = f"collection:{col_id}"
            self.add_node(
                node_id,
                "collection",
                str(col.get("name", col_id)),
                {
                    "collection_id": col_id,
                    "tags": list(col.get("tags") or []),
                    "workspace_ids": list(col.get("workspace_ids") or []),
                },
            )

    def build_document_nodes(
        self,
        entry: CatalogEntry,
        *,
        flashcards: list[dict[str, Any]] | None = None,
        quizzes: list[dict[str, Any]] | None = None,
    ) -> str:
        doc_id = document_node_id(entry.id)
        self.add_node(
            doc_id,
            "document",
            entry.title,
            {
                "catalog_id": entry.id,
                "source_path": entry.source_path,
                "output_path": entry.output_path,
                "workspace_id": entry.workspace_id,
                "collection_id": entry.collection_id,
                "semantic_score": entry.semantic_score,
                "pipeline_stage": entry.pipeline_stage,
            },
        )

        if entry.workspace_id:
            ws_nid = f"workspace:{entry.workspace_id}"
            if ws_nid not in self._nodes:
                self.add_node(ws_nid, "workspace", entry.workspace_name or entry.workspace_id)

        if entry.collection_id:
            col_nid = f"collection:{entry.collection_id}"
            if col_nid not in self._nodes:
                self.add_node(col_nid, "collection", entry.collection_name or entry.collection_id)

        if entry.speaker.strip():
            sp_id = make_node_id("speaker", entry.speaker)
            self.add_node(sp_id, "speaker", entry.speaker, {"catalog_id": entry.id})

        if entry.author.strip():
            au_id = make_node_id("author", entry.author)
            self.add_node(au_id, "author", entry.author, {"catalog_id": entry.id})

        for topic in entry.topics:
            t = str(topic).strip()
            if not t:
                continue
            tid = make_node_id("topic", t)
            self.add_node(tid, "topic", t, {"normalized": t.lower()})

        for tag in entry.tags:
            tg = str(tag).strip()
            if not tg:
                continue
            self.add_node(make_node_id("tag", tg), "tag", tg)

        for ref in entry.references:
            r = str(ref).strip()
            if not r:
                continue
            self.add_node(
                make_node_id("bible_reference", r),
                "bible_reference",
                r,
                {"reference": r},
            )

        for idx, chunk in enumerate(entry.chunks or []):
            if not isinstance(chunk, dict):
                continue
            chunk_key = str(chunk.get("chunk_id") or f"{entry.id}-chunk-{idx}")
            cid = f"chunk:{slugify(chunk_key)}"
            self.add_node(
                cid,
                "chunk",
                str(chunk.get("title") or chunk_key)[:120],
                {
                    "catalog_id": entry.id,
                    "chunk_id": chunk_key,
                    "topics": list(chunk.get("topics") or []),
                    "parent_id": str(chunk.get("parent_id", "")),
                },
            )

        for i, fc in enumerate(flashcards or []):
            if not isinstance(fc, dict):
                continue
            fc_nid = f"flashcard:{entry.id}:{i}"
            self.add_node(
                fc_nid,
                "flashcard",
                str(fc.get("question", ""))[:120],
                {
                    "catalog_id": entry.id,
                    "topic": str(fc.get("topic", "")),
                    "difficulty": str(fc.get("difficulty", "")),
                },
            )

        for i, qz in enumerate(quizzes or []):
            if not isinstance(qz, dict):
                continue
            qz_nid = f"quiz:{entry.id}:{i}"
            self.add_node(
                qz_nid,
                "quiz",
                str(qz.get("question", ""))[:120],
                {
                    "catalog_id": entry.id,
                    "difficulty": str(qz.get("difficulty", "")),
                    "type": str(qz.get("type", "")),
                },
            )

        return doc_id

    def count_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for node in self._nodes.values():
            t = str(node.get("type", "unknown"))
            counts[t] = counts.get(t, 0) + 1
        return counts
