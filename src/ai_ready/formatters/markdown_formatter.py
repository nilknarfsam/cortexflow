"""Utilitários de formatação Markdown — processamento local e determinístico."""

from __future__ import annotations

import re

_MULTI_BLANK = re.compile(r"\n{3,}")
_TRAILING_SPACE = re.compile(r"[ \t]+$", re.MULTILINE)
_HEADER_FIX = re.compile(r"^(#{1,6})([^\s#])", re.MULTILINE)
_DUP_LINE = re.compile(r"^(.+)\n\1$", re.MULTILINE)


def normalize_spacing(text: str) -> str:
    """Remove espaços finais e colapsa linhas em branco excessivas."""
    text = _TRAILING_SPACE.sub("", text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def build_headers(text: str) -> str:
    """Garante espaço após marcadores de cabeçalho Markdown."""
    return _HEADER_FIX.sub(r"\1 \2", text)


def semantic_paragraphs(text: str, *, max_sentences: int = 4) -> str:
    """Agrupa frases em parágrafos semânticos básicos."""
    if not text.strip():
        return text

    if text.lstrip().startswith("#"):
        return text

    sentences = re.split(r"(?<=[.!?…])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\"'])", text.strip())
    if len(sentences) <= max_sentences:
        return text.strip()

    paragraphs: list[str] = []
    chunk: list[str] = []
    for sentence in sentences:
        chunk.append(sentence.strip())
        if len(chunk) >= max_sentences:
            paragraphs.append(" ".join(chunk))
            chunk = []
    if chunk:
        paragraphs.append(" ".join(chunk))
    return "\n\n".join(paragraphs)


def clean_repetitions(text: str) -> str:
    """Remove linhas consecutivas duplicadas."""
    lines = text.splitlines()
    if not lines:
        return text
    result: list[str] = [lines[0]]
    for line in lines[1:]:
        if line.strip() and line.strip() == result[-1].strip():
            continue
        result.append(line)
    return "\n".join(result)


def beautify_markdown(text: str) -> str:
    """Pipeline completo de embelezamento Markdown."""
    text = normalize_spacing(text)
    text = clean_repetitions(text)
    text = build_headers(text)
    text = semantic_paragraphs(text)
    return normalize_spacing(text)
