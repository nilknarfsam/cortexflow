"""Fundação de chunking para RAG e vetorização futura."""

from src.ai_ready.chunking.chunk_builder import (
    Chunk,
    build_semantic_chunks,
    chunk_by_headers,
    chunk_by_size,
    chunk_by_timestamps,
    chunk_by_topic,
    chunk_semantic_basic,
)

__all__ = [
    "Chunk",
    "build_semantic_chunks",
    "chunk_by_headers",
    "chunk_by_size",
    "chunk_by_timestamps",
    "chunk_by_topic",
    "chunk_semantic_basic",
]
