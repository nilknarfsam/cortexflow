"""Construção de chunks para preparação RAG — sem embeddings."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any

_HEADER_PATTERN = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)
_TIMESTAMP_PATTERN = re.compile(
    r"(?:\[\d{1,2}:\d{2}(?::\d{2})?\]|\d{1,2}:\d{2}(?::\d{2})?\s*[-–—])",
    re.MULTILINE,
)
_TOPIC_HINT = re.compile(r"\b(fé|graça|salvação|ressurreição|oração|amor|perdão|discipulado)\b", re.I)


@dataclass
class Chunk:
    """Bloco de conteúdo com identificador e metadados opcionais."""

    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    title: str = ""
    start_timestamp: str = ""
    topics: list[str] = field(default_factory=list)
    parent_id: str | None = None

    @property
    def char_count(self) -> int:
        return len(self.content)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.id,
            "title": self.title,
            "start_timestamp": self.start_timestamp,
            "topics": self.topics,
            "content": self.content,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
        }


def _new_chunk_id(prefix: str = "chunk") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def chunk_by_size(text: str, *, max_chars: int = 1500, overlap: int = 100) -> list[Chunk]:
    """Divide texto em blocos por tamanho com sobreposição opcional."""
    text = text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            break_at = text.rfind("\n\n", start, end)
            if break_at > start + max_chars // 2:
                end = break_at
            else:
                break_at = text.rfind(" ", start, end)
                if break_at > start + max_chars // 2:
                    end = break_at

        content = text[start:end].strip()
        if content:
            chunks.append(
                Chunk(
                    id=f"chunk-{index:03d}",
                    content=content,
                    metadata={"strategy": "size", "start": start, "end": end},
                )
            )
            index += 1

        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks


def chunk_by_headers(text: str) -> list[Chunk]:
    """Separa conteúdo por cabeçalhos Markdown."""
    matches = list(_HEADER_PATTERN.finditer(text))
    if not matches:
        return [Chunk(id="chunk-000", content=text.strip(), metadata={"strategy": "headers", "header": ""})]

    chunks: list[Chunk] = []
    for i, match in enumerate(matches):
        header = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        content = f"{header}\n\n{body}".strip() if body else header
        chunks.append(
            Chunk(
                id=f"chunk-{i:03d}",
                content=content,
                metadata={"strategy": "headers", "header": header},
            )
        )
    return chunks


def chunk_by_timestamps(text: str) -> list[Chunk]:
    """Separa conteúdo por marcadores de timestamp."""
    parts = _TIMESTAMP_PATTERN.split(text)
    markers = _TIMESTAMP_PATTERN.findall(text)
    if not markers:
        return [Chunk(id="chunk-000", content=text.strip(), metadata={"strategy": "timestamps"})]

    chunks: list[Chunk] = []
    preamble = parts[0].strip()
    if preamble:
        chunks.append(
            Chunk(id="chunk-000", content=preamble, metadata={"strategy": "timestamps", "timestamp": ""})
        )

    for i, marker in enumerate(markers):
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        content = f"{marker.strip()} {body}".strip()
        if content:
            chunks.append(
                Chunk(
                    id=f"chunk-{len(chunks):03d}",
                    content=content,
                    metadata={"strategy": "timestamps", "timestamp": marker.strip()},
                )
            )
    return chunks


def chunk_semantic_basic(text: str, *, min_chars: int = 200, max_chars: int = 1500) -> list[Chunk]:
    """Agrupa parágrafos adjacentes em chunks semânticos básicos."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text.strip()) if p.strip()]
    if not paragraphs:
        return []

    chunks: list[Chunk] = []
    buffer: list[str] = []
    buffer_len = 0
    index = 0

    def flush() -> None:
        nonlocal index, buffer, buffer_len
        if not buffer:
            return
        content = "\n\n".join(buffer)
        chunks.append(
            Chunk(
                id=f"chunk-{index:03d}",
                content=content,
                metadata={"strategy": "semantic"},
            )
        )
        index += 1
        buffer = []
        buffer_len = 0

    for para in paragraphs:
        para_len = len(para)
        if buffer and buffer_len + para_len > max_chars:
            flush()
        buffer.append(para)
        buffer_len += para_len
        if buffer_len >= min_chars and buffer_len >= max_chars * 0.6:
            flush()

    flush()
    return chunks


def chunk_by_topic(text: str, topics: list[str] | None = None) -> list[Chunk]:
    """Agrupa parágrafos que mencionam tópicos detectados."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text.strip()) if p.strip()]
    if not paragraphs:
        return []

    topic_list = topics or []
    chunks: list[Chunk] = []
    parent_id = _new_chunk_id("parent")

    for i, para in enumerate(paragraphs):
        para_topics = [t for t in topic_list if t.lower() in para.lower()]
        if not para_topics:
            hints = list(dict.fromkeys(_TOPIC_HINT.findall(para.lower())))
            para_topics = hints[:3]

        title = para[:50].rsplit(" ", 1)[0] + "…" if len(para) > 50 else para[:50]
        chunks.append(
            Chunk(
                id=_new_chunk_id(),
                content=para,
                title=title,
                topics=para_topics,
                parent_id=parent_id if i > 0 else None,
                metadata={"strategy": "topic", "index": i},
            )
        )
    return chunks


def build_semantic_chunks(text: str, *, topics: list[str] | None = None) -> list[dict[str, Any]]:
    """Pipeline de chunking semântico avançado — retorna dicts RAG-ready."""
    if not text.strip():
        return []

    header_chunks = chunk_by_headers(text)
    if len(header_chunks) > 1:
        base = header_chunks
    else:
        ts_chunks = chunk_by_timestamps(text)
        base = ts_chunks if len(ts_chunks) > 1 else chunk_semantic_basic(text)

    if len(base) <= 1:
        base = chunk_by_topic(text, topics) or chunk_semantic_basic(text)

    result: list[dict[str, Any]] = []
    parent_id = _new_chunk_id("doc")

    for i, chunk in enumerate(base):
        ts_match = _TIMESTAMP_PATTERN.search(chunk.content)
        ts = ts_match.group(0).strip("[]-–— ") if ts_match else ""
        title = chunk.metadata.get("header", "") or chunk.title
        if not title:
            title = chunk.content[:48].rsplit(" ", 1)[0] + "…" if len(chunk.content) > 48 else chunk.content[:48]

        chunk_topics = list(topics or [])
        for t in chunk_topics:
            if t.lower() in chunk.content.lower() and t not in chunk.topics:
                chunk.topics.append(t)

        enriched = Chunk(
            id=chunk.id if chunk.id.startswith("chunk-") and len(chunk.id) > 10 else _new_chunk_id(),
            content=chunk.content,
            title=str(title).lstrip("# ").strip(),
            start_timestamp=ts,
            topics=chunk.topics,
            parent_id=parent_id if i > 0 else None,
            metadata={**chunk.metadata, "strategy": "semantic_advanced", "index": i},
        )
        result.append(enriched.to_dict())

    return result
