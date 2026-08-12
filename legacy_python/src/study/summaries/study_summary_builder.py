"""Resumos de estudo e revisão rápida."""

from __future__ import annotations

from typing import Any


class StudySummaryBuilder:
    def build_quick_review(
        self,
        *,
        title: str,
        topics: list[str],
        highlights: list[str],
        concepts: list[str],
        difficulty: str,
    ) -> str:
        lines = [
            "# Revisão Rápida",
            "",
            f"**{title or 'Conteúdo'}** · Dificuldade: **{difficulty}**",
            "",
        ]
        if topics:
            lines.append("## Conceitos principais")
            lines.append("")
            for t in topics[:10]:
                lines.append(f"- {t}")
            lines.append("")

        if concepts:
            lines.append("## Pontos importantes")
            lines.append("")
            for c in concepts[:12]:
                lines.append(f"- {c}")
            lines.append("")

        if highlights:
            lines.append("## Frases-chave")
            lines.append("")
            for h in highlights[:8]:
                lines.append(f"> {h}")
            lines.append("")

        lines.append("## Resumo em uma linha")
        lines.append("")
        if topics:
            lines.append(f"Material focado em: {', '.join(topics[:5])}.")
        else:
            lines.append("Revise o conteúdo completo e os flashcards gerados.")
        lines.append("")
        return "\n".join(lines)

    def extract_concepts(
        self,
        *,
        topics: list[str],
        chunks: list[dict[str, Any]],
        highlights: list[str],
    ) -> list[str]:
        concepts: list[str] = []
        seen: set[str] = set()
        for t in topics:
            if t and t.lower() not in seen:
                seen.add(t.lower())
                concepts.append(f"Conceito: {t}")
        for ch in chunks[:8]:
            title = str(ch.get("title", "") or "").strip()
            if title and title.lower() not in seen:
                seen.add(title.lower())
                concepts.append(title)
        for h in highlights[:5]:
            short = h.strip()[:100]
            if short and short.lower() not in seen:
                seen.add(short.lower())
                concepts.append(short)
        return concepts[:15]

    def key_points(self, highlights: list[str], chunks: list[dict[str, Any]]) -> list[str]:
        points: list[str] = []
        for h in highlights[:6]:
            points.append(h.strip())
        for ch in chunks[:4]:
            c = str(ch.get("content", "") or "").strip()
            if c:
                first = c.split(".")[0].strip()
                if len(first) > 25:
                    points.append(first + ".")
        return points[:10]
