"""Formatação inteligente de timestamps em Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass

_TS_BRACKET = re.compile(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.*)")
_TS_INLINE = re.compile(r"^(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(.+)$", re.MULTILINE)
_TS_RAW = re.compile(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b")


@dataclass(frozen=True)
class TimestampEntry:
    normalized: str
    label: str
    raw: str


def normalize_timestamp(raw: str) -> str:
    """Normaliza timestamp para HH:MM:SS."""
    raw = raw.strip().strip("[]")
    parts = raw.split(":")
    if len(parts) == 2:
        h, m = parts
        return f"{int(h):02d}:{int(m):02d}:00"
    if len(parts) == 3:
        h, m, s = parts
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    return raw


def parse_timestamps(text: str) -> list[TimestampEntry]:
    """Extrai e normaliza timestamps do texto."""
    entries: list[TimestampEntry] = []
    seen: set[str] = set()

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = _TS_BRACKET.match(line)
        if match:
            ts = normalize_timestamp(match.group(1))
            label = match.group(2).strip() or f"Segmento {ts}"
            key = f"{ts}:{label}"
            if key not in seen:
                seen.add(key)
                entries.append(TimestampEntry(normalized=ts, label=label, raw=line))
            continue

        match = _TS_INLINE.match(line)
        if match:
            ts = normalize_timestamp(match.group(1))
            label = match.group(2).strip()
            key = f"{ts}:{label}"
            if key not in seen:
                seen.add(key)
                entries.append(TimestampEntry(normalized=ts, label=label, raw=line))

    if not entries:
        for match in _TS_RAW.finditer(text):
            ts = normalize_timestamp(match.group(0))
            if ts not in seen:
                seen.add(ts)
                entries.append(TimestampEntry(normalized=ts, label=f"Marca {ts}", raw=match.group(0)))

    return entries


def format_timestamps_markdown(entries: list[TimestampEntry]) -> str:
    """Formata seção Markdown de timestamps."""
    if not entries:
        return "# Timestamps\n\n_Sem timestamps detectados._\n"
    lines = ["# Timestamps", ""]
    for entry in entries:
        lines.append(f"## [{entry.normalized}] {entry.label}")
    return "\n".join(lines) + "\n"
