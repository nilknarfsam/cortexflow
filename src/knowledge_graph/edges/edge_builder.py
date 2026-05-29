"""Cria relações entre nós do grafo de conhecimento."""

from __future__ import annotations

import uuid
from typing import Any

from src.knowledge_graph.nodes.node_builder import (
    document_node_id,
    make_node_id,
    slugify,
)
from src.library.catalog.catalog_registry import CatalogEntry


class EdgeBuilder:
    def __init__(self) -> None:
        self._edges: dict[str, dict[str, Any]] = {}

    @property
    def edges(self) -> dict[str, dict[str, Any]]:
        return self._edges

    def clear(self) -> None:
        self._edges.clear()

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        *,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        edge_id = f"edge-{uuid.uuid4().hex[:12]}"
        edge = {
            "edge_id": edge_id,
            "source": source,
            "target": target,
            "relation": relation,
            "weight": round(weight, 3),
            "metadata": metadata or {},
        }
        self._edges[edge_id] = edge
        return edge

    def _edge_key(self, source: str, target: str, relation: str) -> str:
        return f"{source}|{target}|{relation}"

    def add_edge_unique(
        self,
        source: str,
        target: str,
        relation: str,
        *,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        key = self._edge_key(source, target, relation)
        for edge in self._edges.values():
            if self._edge_key(edge["source"], edge["target"], edge["relation"]) == key:
                return None
        return self.add_edge(source, target, relation, weight=weight, metadata=metadata)

    def build_document_edges(
        self,
        entry: CatalogEntry,
        *,
        flashcard_count: int = 0,
        quiz_count: int = 0,
    ) -> None:
        doc_id = document_node_id(entry.id)

        if entry.workspace_id:
            self.add_edge_unique(
                doc_id,
                f"workspace:{entry.workspace_id}",
                "belongs_to_workspace",
            )

        if entry.collection_id:
            self.add_edge_unique(
                doc_id,
                f"collection:{entry.collection_id}",
                "belongs_to_collection",
            )

        for topic in entry.topics:
            t = str(topic).strip()
            if t:
                self.add_edge_unique(doc_id, make_node_id("topic", t), "has_topic")

        for tag in entry.tags:
            tg = str(tag).strip()
            if tg:
                self.add_edge_unique(doc_id, make_node_id("tag", tg), "has_tag")

        for ref in entry.references:
            r = str(ref).strip()
            if r:
                self.add_edge_unique(
                    doc_id,
                    make_node_id("bible_reference", r),
                    "has_reference",
                )

        if entry.speaker.strip():
            self.add_edge_unique(
                doc_id,
                make_node_id("speaker", entry.speaker),
                "has_tag",
                metadata={"facet": "speaker"},
            )

        if entry.author.strip():
            self.add_edge_unique(
                doc_id,
                make_node_id("author", entry.author),
                "has_tag",
                metadata={"facet": "author"},
            )

        for idx, chunk in enumerate(entry.chunks or []):
            if not isinstance(chunk, dict):
                continue
            chunk_key = str(chunk.get("chunk_id") or f"{entry.id}-chunk-{idx}")
            cid = f"chunk:{slugify(chunk_key)}"
            self.add_edge_unique(doc_id, cid, "has_chunk")
            for t in chunk.get("topics") or []:
                ts = str(t).strip()
                if ts:
                    self.add_edge_unique(cid, make_node_id("topic", ts), "has_topic")

        for i in range(flashcard_count):
            fc_nid = f"flashcard:{entry.id}:{i}"
            self.add_edge_unique(doc_id, fc_nid, "has_flashcard")

        for i in range(quiz_count):
            qz_nid = f"quiz:{entry.id}:{i}"
            self.add_edge_unique(doc_id, qz_nid, "has_quiz")

    def build_cross_document_edges(self, entries: list[CatalogEntry]) -> None:
        """Relações documento ↔ documento por facetas compartilhadas."""
        for i, a in enumerate(entries):
            doc_a = document_node_id(a.id)
            topics_a = {t.lower() for t in a.topics if t}
            refs_a = {r.lower() for r in a.references if r}
            for b in entries[i + 1 :]:
                doc_b = document_node_id(b.id)
                shared_topics = sorted(topics_a & {t.lower() for t in b.topics if t})
                if shared_topics:
                    self.add_edge_unique(
                        doc_a,
                        doc_b,
                        "related_by_topic",
                        weight=min(5.0, len(shared_topics) * 1.2),
                        metadata={"shared_topics": shared_topics[:8]},
                    )

                shared_refs = sorted(refs_a & {r.lower() for r in b.references if r})
                if shared_refs:
                    self.add_edge_unique(
                        doc_a,
                        doc_b,
                        "related_by_reference",
                        weight=min(5.0, len(shared_refs) * 1.3),
                        metadata={"shared_references": shared_refs[:8]},
                    )

                if (
                    a.speaker.strip()
                    and a.speaker.strip().lower() == b.speaker.strip().lower()
                ):
                    self.add_edge_unique(
                        doc_a,
                        doc_b,
                        "related_by_speaker",
                        weight=1.5,
                        metadata={"speaker": a.speaker},
                    )

                if a.collection_id and a.collection_id == b.collection_id:
                    self.add_edge_unique(
                        doc_a,
                        doc_b,
                        "related_by_collection",
                        weight=1.0,
                        metadata={"collection_id": a.collection_id},
                    )

    def count_by_relation(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for edge in self._edges.values():
            rel = str(edge.get("relation", "unknown"))
            counts[rel] = counts.get(rel, 0) + 1
        return counts
