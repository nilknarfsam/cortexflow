"""Extração determinística de frases marcantes."""

from __future__ import annotations

import re
from collections import Counter

_STRONG_WORDS = (
    "importante", "essencial", "fundamental", "sempre", "nunca", "deve", "precisa",
    "crucial", "verdade", "vida", "deus", "cristo", "espírito", "fé", "amor",
    "graça", "salvação", "ressurreição", "perdão", "eternidade", "chamado",
    "propósito", "transformação", "liberdade", "esperança", "poder",
)

_PAUSE_PATTERN = re.compile(r"\.\.\.|…|\[pausa\]|\(pausa\)", re.IGNORECASE)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")


def extract_highlights(text: str, *, limit: int = 8) -> list[str]:
    """Extrai frases importantes com heurísticas locais."""
    if not text.strip():
        return []

    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    if not sentences:
        return []

    freq = Counter(s.lower().strip() for s in sentences if len(s) > 20)
    repeated = {s for s, c in freq.items() if c >= 2}

    scored: list[tuple[float, str]] = []
    for sentence in sentences:
        if len(sentence) < 25:
            continue
        lower = sentence.lower()
        score = 0.0

        if lower in repeated:
            score += 3.0
        if sentence.endswith("!"):
            score += 2.0
        if _PAUSE_PATTERN.search(sentence):
            score += 1.5
        if 60 <= len(sentence) <= 180:
            score += 1.0
        score += sum(1.0 for w in _STRONG_WORDS if w in lower)
        if '"' in sentence or "'" in sentence:
            score += 0.5

        if score > 0:
            scored.append((score, sentence))

    scored.sort(key=lambda x: x[0], reverse=True)
    highlights: list[str] = []
    seen: set[str] = set()
    for _, sentence in scored:
        key = sentence.lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        highlights.append(sentence)
        if len(highlights) >= limit:
            break

    return highlights


def format_highlights_markdown(highlights: list[str]) -> str:
    """Formata seção Markdown de frases marcantes."""
    if not highlights:
        return "## Frases Marcantes\n\n_Nenhuma frase destacada automaticamente._\n"
    lines = ["## Frases Marcantes", ""]
    lines.extend(f"- {h}" for h in highlights)
    return "\n".join(lines) + "\n"
