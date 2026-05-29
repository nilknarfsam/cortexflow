"""Orquestrador da Knowledge Library — coleções, workspaces, catálogo e busca."""

from __future__ import annotations

import os
from typing import Any

from src.library.catalog.catalog_registry import CatalogEntry, CatalogRegistry
from src.library.collections.collection_manager import CollectionManager
from src.library.metadata.library_stats import LibraryStats, compute_library_stats
from src.library.metadata.relationship_builder import RelationshipBuilder
from src.library.search.search_engine import LibrarySearchEngine, SearchResult
from src.library.workspaces.workspace_manager import WorkspaceManager


class KnowledgeLibrary:
    def __init__(self) -> None:
        self.collections = CollectionManager()
        self.workspaces = WorkspaceManager()
        self.catalog = CatalogRegistry()
        self.search = LibrarySearchEngine(self.catalog)
        self.relationships = RelationshipBuilder(self.catalog)

    def stats(self) -> LibraryStats:
        return compute_library_stats(self.catalog, self.workspaces, self.collections)

    def resolve_workspace(self, workspace_id: str) -> tuple[str, str]:
        ws_id = workspace_id or self.workspaces.get_default_id()
        ws = self.workspaces.get(ws_id)
        if ws:
            return ws_id, str(ws.get("name", ""))
        default = self.workspaces.get(self.workspaces.get_default_id())
        name = str(default.get("name", "")) if default else "Biblioteca Principal"
        return self.workspaces.get_default_id(), name

    def resolve_collection(self, collection_id: str, collection_name: str = "") -> tuple[str, str]:
        if collection_id:
            col = self.collections.get(collection_id)
            if col:
                return collection_id, str(col.get("name", ""))
        if collection_name:
            col = self.collections.get_by_name(collection_name)
            if col:
                return str(col["id"]), str(col.get("name", ""))
            created = self.collections.create(collection_name)
            return str(created["id"]), str(created.get("name", ""))
        return "", ""

    def register_processed_document(
        self,
        *,
        source_path: str,
        output_path: str,
        file_hash: str,
        workspace_id: str,
        collection_id: str,
        collection_name: str,
        speaker: str,
        author: str,
        tags: list[str],
        category: str,
        knowledge_type: str,
        export_mode: str,
        template: str,
        pipeline_stage: str,
        semantic_metadata: dict[str, Any],
        stage_metadata: dict[str, Any] | None = None,
    ) -> tuple[CatalogEntry, list[dict[str, Any]]]:
        ws_id, ws_name = self.resolve_workspace(workspace_id)
        col_id, col_name = self.resolve_collection(collection_id, collection_name)

        if col_id and ws_id:
            self.workspaces.link_collection(ws_id, col_id)

        meta = stage_metadata or {}
        topics = list(semantic_metadata.get("topics") or meta.get("topics") or [])
        if isinstance(topics, str):
            topics = [t.strip() for t in topics.split(",") if t.strip()]

        refs = meta.get("references") or meta.get("bible_references") or []
        if not isinstance(refs, list):
            refs = []
        highlights = meta.get("highlights") or []
        if not isinstance(highlights, list):
            highlights = []

        chunks = meta.get("chunks") or []
        chunk_count = int(semantic_metadata.get("chunk_count") or len(chunks) or 0)

        entry = CatalogEntry(
            title=CatalogRegistry.title_from_path(source_path),
            source_path=source_path,
            output_path=output_path,
            file_hash=file_hash,
            workspace_id=ws_id,
            workspace_name=ws_name,
            collection_id=col_id,
            collection_name=col_name,
            speaker=speaker,
            author=author,
            topics=topics,
            tags=list(tags),
            references=[str(r) for r in refs[:50]],
            highlights=[str(h) for h in highlights[:30]],
            chunks=chunks if isinstance(chunks, list) else [],
            export_mode=export_mode,
            template=template,
            pipeline_stage=pipeline_stage,
            category=category,
            knowledge_type=knowledge_type or "document",
            semantic_score=CatalogRegistry.compute_semantic_score(
                reference_count=len(refs) or int(semantic_metadata.get("reference_count", 0)),
                highlight_count=len(highlights) or int(semantic_metadata.get("highlight_count", 0)),
                topic_count=len(topics),
                chunk_count=chunk_count,
            ),
            chunk_count=chunk_count,
        )

        saved = self.catalog.register(entry)
        rels = self.relationships.build_for_document(saved.id)
        return saved, rels

    def search_documents(self, **kwargs: Any) -> list[SearchResult]:
        return self.search.search(**kwargs)

    def open_output_path(self, catalog_id: str) -> str | None:
        entry = self.catalog.get(catalog_id)
        if not entry or not entry.output_path:
            return None
        path = os.path.abspath(entry.output_path)
        return path if os.path.isfile(path) else None
