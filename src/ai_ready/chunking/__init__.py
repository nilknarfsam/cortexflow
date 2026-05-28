"""Fundação de chunking para RAG e vetorização futura."""

from src.ai_ready.chunking.chunk_builder import (
    Chunk,
    chunk_by_headers,
    chunk_by_size,
    chunk_by_timestamps,
    chunk_semantic_basic,
)

__all__ = [
    "Chunk",
    "chunk_by_headers",
    "chunk_by_size",
    "chunk_by_timestamps",
    "chunk_semantic_basic",
]
