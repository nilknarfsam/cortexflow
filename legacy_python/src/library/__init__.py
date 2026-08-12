"""Knowledge Library Engine — biblioteca inteligente de conhecimento local."""

from __future__ import annotations

from typing import Optional

from src.library.library_engine import KnowledgeLibrary

_instance: Optional[KnowledgeLibrary] = None


def get_library() -> KnowledgeLibrary:
    global _instance
    if _instance is None:
        _instance = KnowledgeLibrary()
    return _instance


__all__ = ["KnowledgeLibrary", "get_library"]
