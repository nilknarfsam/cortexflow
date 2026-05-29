"""Relações semânticas simples entre documentos do catálogo."""

from __future__ import annotations

from typing import Any

from src.library.catalog.catalog_registry import CatalogEntry, CatalogRegistry


class RelationshipBuilder:
    def __init__(self, catalog: CatalogRegistry) -> None:
        self._catalog = catalog

    def build_for_document(self, catalog_id: str, *, limit: int = 12) -> list[dict[str, Any]]:
        source = self._catalog.get(catalog_id)
        if not source:
            return []
        relations: list[dict[str, Any]] = []
        for other in self._catalog.all_entries:
            if other.id == source.id:
                continue
            shared = self._shared_facets(source, other)
            if not shared["reasons"]:
                continue
            strength = len(shared["reasons"])
            relations.append({
                "catalog_id": other.id,
                "title": other.title,
                "strength": strength,
                "reasons": shared["reasons"],
                "shared_topics": shared["topics"],
                "shared_references": shared["references"],
                "shared_speaker": shared["speaker"],
                "shared_collection": shared["collection"],
            })
        relations.sort(key=lambda r: (-r["strength"], r["title"]))
        return relations[:limit]

    def build_graph_summary(self) -> dict[str, Any]:
        """Resumo para futuro semantic / navigation graph."""
        entries = self._catalog.all_entries
        edges = 0
        for entry in entries[:100]:
            edges += len(self.build_for_document(entry.id, limit=5))
        return {
            "nodes": len(entries),
            "edges_estimated": edges,
            "ready_for_graph": len(entries) > 0,
        }

    @staticmethod
    def _shared_facets(a: CatalogEntry, b: CatalogEntry) -> dict[str, Any]:
        topics_a = {t.lower() for t in a.topics if t}
        topics_b = {t.lower() for t in b.topics if t}
        shared_topics = sorted(topics_a & topics_b)

        refs_a = {r.lower() for r in a.references if r}
        refs_b = {r.lower() for r in b.references if r}
        shared_refs = sorted(refs_a & refs_b)

        shared_speaker = (
            a.speaker.strip().lower() == b.speaker.strip().lower()
            and bool(a.speaker.strip())
        )
        shared_collection = (
            a.collection_id == b.collection_id
            and bool(a.collection_id)
        )

        reasons: list[str] = []
        if shared_topics:
            reasons.append("shared_topics")
        if shared_refs:
            reasons.append("shared_references")
        if shared_speaker:
            reasons.append("shared_speaker")
        if shared_collection:
            reasons.append("shared_collection")

        return {
            "reasons": reasons,
            "topics": shared_topics[:8],
            "references": shared_refs[:8],
            "speaker": a.speaker if shared_speaker else "",
            "collection": a.collection_name if shared_collection else "",
        }

    def format_for_history(self, catalog_id: str) -> str:
        rels = self.build_for_document(catalog_id, limit=5)
        if not rels:
            return ""
        parts = [f"{r['title']} ({','.join(r['reasons'])})" for r in rels[:3]]
        return "; ".join(parts)
