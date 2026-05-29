"""Gerador de índice automático baseado em estrutura do conteúdo."""

from __future__ import annotations

import re
from dataclasses import dataclass

_HEADER = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_TIMESTAMP = re.compile(
    r"(?:\[(\d{1,2}:\d{2}(?::\d{2})?)\]|^(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(.+)$)",
    re.MULTILINE,
)


@dataclass(frozen=True)
class IndexEntry:
    number: int
    title: str
    source: str  # header | timestamp | semantic


def build_auto_index(text: str, *, max_entries: int = 12) -> list[IndexEntry]:
    """Gera índice a partir de títulos, timestamps e blocos semânticos."""
    entries: list[IndexEntry] = []
    seen: set[str] = set()

    for match in _HEADER.finditer(text):
        title = match.group(2).strip()
        key = title.lower()
        if key in seen or title.startswith("#"):
            continue
        seen.add(key)
        entries.append(IndexEntry(number=len(entries) + 1, title=title, source="header"))

    for match in _TIMESTAMP.finditer(text):
        ts = match.group(1) or match.group(2) or ""
        label = (match.group(3) or "").strip()
        title = label if label else f"Segmento {ts}"
        key = f"{ts}:{title}".lower()
        if key in seen:
            continue
        seen.add(key)
        entries.append(IndexEntry(number=len(entries) + 1, title=title, source="timestamp"))

    if not entries:
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text.strip()) if p.strip()]
        for para in paragraphs[:max_entries]:
            title = para[:60].rsplit(" ", 1)[0] + "…" if len(para) > 60 else para
            entries.append(IndexEntry(number=len(entries) + 1, title=title, source="semantic"))

    for i, entry in enumerate(entries[:max_entries], start=1):
        if entry.number != i:
            entries[i - 1] = IndexEntry(number=i, title=entry.title, source=entry.source)

    return entries[:max_entries]


def format_index_markdown(entries: list[IndexEntry]) -> str:
    """Formata seção Markdown de índice."""
    if not entries:
        return "# Índice\n\n_Índice não disponível._\n"
    lines = ["# Índice", ""]
    for entry in entries:
        lines.append(f"{entry.number}. {entry.title}")
    return "\n".join(lines) + "\n"
