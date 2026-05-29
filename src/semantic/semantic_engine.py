"""Orquestrador da Semantic Intelligence Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.semantic.highlights.highlight_extractor import extract_highlights, format_highlights_markdown
from src.semantic.indexing.auto_index_builder import build_auto_index, format_index_markdown
from src.semantic.references.bible_reference_detector import (
    detect_bible_references,
    format_bible_references_markdown,
)
from src.semantic.timestamps.timestamp_formatter import format_timestamps_markdown, parse_timestamps
from src.semantic.topics.topic_extractor import extract_topics_and_tags


@dataclass
class SemanticResult:
    """Resultado consolidado da análise semântica."""

    topics: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    bible_references: list[dict[str, str]] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    index_entries: list[dict[str, Any]] = field(default_factory=list)
    timestamps: list[dict[str, str]] = field(default_factory=list)
    chunks: list[dict[str, Any]] = field(default_factory=list)
    reference_count: int = 0
    highlight_count: int = 0
    chunk_count: int = 0

    def to_metadata(self) -> dict[str, Any]:
        return {
            "topics": self.topics,
            "tags": self.tags,
            "reference_count": self.reference_count,
            "highlight_count": self.highlight_count,
            "chunk_count": self.chunk_count,
            "topics_detected": ", ".join(self.topics[:5]),
            "semantic_ready": True,
        }

    def to_history_fields(self) -> dict[str, str]:
        return {
            "referencias": str(self.reference_count),
            "highlights": str(self.highlight_count),
            "chunks": str(self.chunk_count),
            "topicos": ", ".join(self.topics[:5]),
        }


class SemanticEngine:
    """Engine de inteligência semântica — 100% local e determinística."""

    def analyze(self, text: str) -> SemanticResult:
        from src.ai_ready.chunking.chunk_builder import build_semantic_chunks

        topics, tags = extract_topics_and_tags(text)
        refs = detect_bible_references(text)
        highlights = extract_highlights(text)
        index = build_auto_index(text)
        timestamps = parse_timestamps(text)
        chunks = build_semantic_chunks(text, topics=topics)

        return SemanticResult(
            topics=topics,
            tags=tags,
            bible_references=[
                {"book": r.book, "chapter": r.chapter, "verse": r.verse, "reference": r.reference}
                for r in refs
            ],
            highlights=highlights,
            index_entries=[
                {"number": e.number, "title": e.title, "source": e.source} for e in index
            ],
            timestamps=[
                {"normalized": t.normalized, "label": t.label, "raw": t.raw} for t in timestamps
            ],
            chunks=chunks,
            reference_count=len(refs),
            highlight_count=len(highlights),
            chunk_count=len(chunks),
        )

    def enrich_markdown(self, content: str, analysis: SemanticResult, *, insert_index: bool = True) -> str:
        """Injeta seções semânticas no markdown existente."""
        parts: list[str] = []

        if insert_index and analysis.index_entries:
            from src.semantic.indexing.auto_index_builder import IndexEntry

            entries = [
                IndexEntry(number=e["number"], title=e["title"], source=e["source"])
                for e in analysis.index_entries
            ]
            parts.append(format_index_markdown(entries))

        parts.append(content)

        from src.semantic.references.bible_reference_detector import BibleReference

        bible_objs = [
            BibleReference(
                book=r["book"], chapter=r["chapter"], verse=r["verse"], reference=r["reference"]
            )
            for r in analysis.bible_references
        ]
        parts.append(format_bible_references_markdown(bible_objs))
        parts.append(format_highlights_markdown(analysis.highlights))

        from src.semantic.timestamps.timestamp_formatter import TimestampEntry

        ts_objs = [
            TimestampEntry(normalized=t["normalized"], label=t["label"], raw=t["raw"])
            for t in analysis.timestamps
        ]
        parts.append(format_timestamps_markdown(ts_objs))

        return "\n\n".join(p.strip() for p in parts if p.strip())


def analyze_text(text: str) -> SemanticResult:
    return SemanticEngine().analyze(text)
