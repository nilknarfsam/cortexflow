"""Estatísticas agregadas da biblioteca de conhecimento."""

from __future__ import annotations

from dataclasses import dataclass

from src.library.catalog.catalog_registry import CatalogRegistry
from src.library.collections.collection_manager import CollectionManager
from src.library.workspaces.workspace_manager import WorkspaceManager


@dataclass
class LibraryStats:
    documents: int = 0
    chunks: int = 0
    references: int = 0
    topics: int = 0
    workspaces: int = 0
    collections: int = 0

    def to_display(self) -> str:
        return (
            f"Docs: {self.documents}  ·  Chunks: {self.chunks}  ·  "
            f"Refs: {self.references}  ·  Tópicos: {self.topics}  ·  "
            f"Workspaces: {self.workspaces}  ·  Coleções: {self.collections}"
        )


def compute_library_stats(
    catalog: CatalogRegistry,
    workspaces: WorkspaceManager,
    collections: CollectionManager,
) -> LibraryStats:
    topic_set: set[str] = set()
    total_chunks = 0
    total_refs = 0

    for entry in catalog.all_entries:
        total_chunks += entry.chunk_count or len(entry.chunks)
        total_refs += len(entry.references)
        for t in entry.topics:
            if t:
                topic_set.add(str(t).lower())

    return LibraryStats(
        documents=catalog.count(),
        chunks=total_chunks,
        references=total_refs,
        topics=len(topic_set),
        workspaces=len(workspaces.all),
        collections=len(collections.all),
    )
