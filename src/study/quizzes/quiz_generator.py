"""Gerador determinístico de quizzes."""

from __future__ import annotations

import random
from typing import Any

_MAX_QUESTIONS = 16


class QuizGenerator:
    def __init__(self, *, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def generate(
        self,
        *,
        chunks: list[dict[str, Any]],
        highlights: list[str],
        topics: list[str],
        difficulty: str = "básico",
    ) -> list[dict[str, Any]]:
        questions: list[dict[str, Any]] = []
        pool_topics = list(topics) or ["conteúdo geral"]
        distractor_pool = pool_topics + [
            "contexto histórico",
            "aplicação prática",
            "revisão geral",
        ]

        for topic in pool_topics[:6]:
            if len(questions) >= _MAX_QUESTIONS:
                break
            others = [t for t in distractor_pool if t != topic]
            self._rng.shuffle(others)
            options = [topic] + others[:3]
            self._rng.shuffle(options)
            questions.append({
                "question": f"Qual tópico é central neste material relacionado a «{topic}»?",
                "options": options,
                "correct_answer": topic,
                "difficulty": difficulty,
                "type": "múltipla_escolha",
            })

        for hi in highlights[:5]:
            if len(questions) >= _MAX_QUESTIONS:
                break
            h = hi.strip()
            if len(h) < 20:
                continue
            questions.append({
                "question": f"Verdadeiro ou falso: «{_short(h, 100)}»",
                "options": ["Verdadeiro", "Falso"],
                "correct_answer": "Verdadeiro",
                "difficulty": difficulty,
                "type": "verdadeiro_falso",
            })

        for ch in chunks[:4]:
            if len(questions) >= _MAX_QUESTIONS:
                break
            title = str(ch.get("title", "") or "este trecho").strip()
            questions.append({
                "question": f"Pergunta aberta: explique com suas palavras «{title}».",
                "options": [],
                "correct_answer": "(resposta aberta — consulte o material)",
                "difficulty": difficulty,
                "type": "pergunta_aberta",
            })

        if pool_topics:
            questions.append({
                "question": f"Revisão rápida: cite três ideias sobre {', '.join(pool_topics[:3])}.",
                "options": [],
                "correct_answer": ", ".join(pool_topics[:3]),
                "difficulty": difficulty,
                "type": "revisão_rápida",
            })

        return questions[:_MAX_QUESTIONS]


def _short(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1] + "…"
