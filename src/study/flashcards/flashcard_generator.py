"""Gerador determinístico de flashcards."""

from __future__ import annotations

import re
from typing import Any

_MAX_CARDS = 24


def _truncate(text: str, n: int = 280) -> str:
    t = " ".join(text.split())
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


class FlashcardGenerator:
    def generate(
        self,
        *,
        chunks: list[dict[str, Any]],
        highlights: list[str],
        topics: list[str],
        references: list[Any],
        difficulty: str = "básico",
    ) -> list[dict[str, str]]:
        cards: list[dict[str, str]] = []
        seen: set[str] = set()

        def add(question: str, answer: str, topic: str, card_type: str = "conceito") -> None:
            q = question.strip()
            a = answer.strip()
            if not q or not a:
                return
            key = f"{q[:80]}|{a[:80]}"
            if key in seen or len(cards) >= _MAX_CARDS:
                return
            seen.add(key)
            cards.append({
                "question": q,
                "answer": a,
                "topic": topic or "geral",
                "difficulty": difficulty,
                "type": card_type,
            })

        for ch in chunks[:12]:
            title = str(ch.get("title", "") or "").strip()
            content = str(ch.get("content", "") or "").strip()
            ch_topics = ch.get("topics") or []
            topic = ch_topics[0] if ch_topics else (topics[0] if topics else "conteúdo")
            if title and content:
                add(f"O que aborda «{title}»?", _truncate(content), str(topic), "pergunta_resposta")
            elif content:
                first = content.split(".")[0].strip()
                if len(first) > 20:
                    add(f"Explique: {first[:90]}?", _truncate(content), str(topic), "conceito_definição")

        for hi in highlights[:10]:
            h = hi.strip()
            if len(h) < 15:
                continue
            topic = topics[0] if topics else "destaque"
            add("Qual é o significado desta frase marcante?", h, topic, "conceito_definição")
            if "?" not in h:
                add(f"Complete: «{h[:60]}…»", h, topic, "pergunta_resposta")

        for topic in topics[:8]:
            t = topic.strip()
            if not t:
                continue
            add(f"Defina o conceito «{t}» no contexto deste conteúdo.", f"Conceito central: {t}.", t, "conceito_definição")

        for ref in references[:8]:
            if isinstance(ref, dict):
                label = str(ref.get("reference") or ref.get("book", ""))
            else:
                label = str(ref)
            label = label.strip()
            if not label:
                continue
            add(f"Qual passagem ou referência é «{label}»?", f"Referência bíblica: {label}.", "referências", "referência_pergunta")

        return cards
