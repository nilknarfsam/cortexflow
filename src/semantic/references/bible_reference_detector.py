"""Detecção automática de referências bíblicas — processamento local."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_BIBLE_BOOKS = (
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio",
    "Josué", "Juízes", "Rute", "1 Samuel", "2 Samuel",
    "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas",
    "Esdras", "Neemias", "Ester", "Jó", "Salmos", "Salmo",
    "Provérbios", "Eclesiastes", "Cânticos", "Isaías", "Jeremias",
    "Lamentações", "Ezequiel", "Daniel", "Oséias", "Joel",
    "Amós", "Obadias", "Jonas", "Miqueias", "Naum",
    "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias",
    "Mateus", "Marcos", "Lucas", "João", "Atos",
    "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios",
    "Filipenses", "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses",
    "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus",
    "Tiago", "1 Pedro", "2 Pedro", "1 João", "2 João",
    "3 João", "Judas", "Apocalipse",
)

_BOOK_PATTERN = "|".join(re.escape(b) for b in sorted(_BIBLE_BOOKS, key=len, reverse=True))
# Variantes sem acento para transcrições Whisper
_BOOK_ALIASES = (
    "Joao", "1 Corintios", "2 Corintios", "Salmo", "Salmos",
    "Mateus", "Romanos", "Genesis", "Exodo",
)
_ALT_PATTERN = "|".join(re.escape(b) for b in sorted(set(_BOOK_ALIASES), key=len, reverse=True))
_REF_PATTERN = re.compile(
    rf"\b((?:[1-3]\s)?(?:(?:{_BOOK_PATTERN})|(?:{_ALT_PATTERN})))\s+(\d{{1,3}})(?::(\d{{1,3}})(?:-(\d{{1,3}}))?)?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BibleReference:
    book: str
    chapter: str
    verse: str
    reference: str


def detect_bible_references(text: str) -> list[BibleReference]:
    """Detecta referências bíblicas no texto."""
    found: list[BibleReference] = []
    seen: set[str] = set()

    for match in _REF_PATTERN.finditer(text):
        book = _normalize_book(match.group(1))
        chapter = match.group(2)
        verse = match.group(3) or ""
        end_verse = match.group(4)

        if verse and end_verse:
            ref = f"{book} {chapter}:{verse}-{end_verse}"
            verse_str = f"{verse}-{end_verse}"
        elif verse:
            ref = f"{book} {chapter}:{verse}"
            verse_str = verse
        else:
            ref = f"{book} {chapter}"
            verse_str = ""

        key = ref.lower()
        if key in seen:
            continue
        seen.add(key)
        found.append(BibleReference(book=book, chapter=chapter, verse=verse_str, reference=ref))

    return found


_ALIAS_MAP: dict[str, str] = {
    "joao": "João",
    "genesis": "Gênesis",
    "exodo": "Êxodo",
    "1 corintios": "1 Coríntios",
    "2 corintios": "2 Coríntios",
    "salmo": "Salmos",
    "salmos": "Salmos",
}


def _normalize_book(raw: str) -> str:
    cleaned = re.sub(r"\s+", " ", raw.strip())
    cleaned_fold = _fold(cleaned)
    if cleaned_fold in _ALIAS_MAP:
        return _ALIAS_MAP[cleaned_fold]
    for book in _BIBLE_BOOKS:
        if _fold(book) == cleaned_fold:
            return book
    return cleaned.title()


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def format_bible_references_markdown(refs: list[BibleReference]) -> str:
    """Formata seção Markdown de referências detectadas."""
    if not refs:
        return "## Referências Bíblicas Detectadas\n\n_Nenhuma referência detectada._\n"
    lines = ["## Referências Bíblicas Detectadas", ""]
    lines.extend(f"- {r.reference}" for r in refs)
    return "\n".join(lines) + "\n"
