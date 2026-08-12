"""Detector de tópicos relevantes — heurísticas locais."""

from __future__ import annotations

import re
from collections import Counter

_TOPIC_LEXICON: dict[str, tuple[str, ...]] = {
    "fé": ("fé", "creio", "crer", "confiança", "confiar"),
    "graça": ("graça", "misericórdia", "graciosamente"),
    "salvação": ("salvação", "salvo", "salvar", "redenção", "redimido"),
    "ressurreição": ("ressurreição", "ressuscitar", "ressuscitou", "vida eterna"),
    "discipulado": ("discipulado", "discípulo", "discipular", "seguir a cristo"),
    "oração": ("oração", "orar", "oramos", "interceder"),
    "santidade": ("santidade", "santo", "santificar", "pureza"),
    "evangelho": ("evangelho", "boas novas", "pregação"),
    "amor": ("amor", "amar", "caridade"),
    "perdão": ("perdão", "perdoar", "perdoado"),
    "família": ("família", "casamento", "filhos", "lar"),
    "espírito santo": ("espírito santo", "espírito de deus", "consolador"),
    "joão 11": ("joão 11", "lázaro", "lazaro"),
    "cruz": ("cruz", "calvário", "crucificado"),
    "reino": ("reino de deus", "reino dos céus", "reino"),
}

_WORD = re.compile(r"[a-záàâãéêíóôõúç]+", re.IGNORECASE)


def extract_topics(text: str, *, limit: int = 8) -> list[str]:
    """Detecta tópicos por léxico e frequência."""
    topics, _ = extract_topics_and_tags(text, limit=limit)
    return topics


def extract_topics_and_tags(text: str, *, limit: int = 8) -> tuple[list[str], list[str]]:
    """Retorna tópicos principais e tags complementares."""
    lower = text.lower()
    scores: Counter[str] = Counter()

    for topic, keywords in _TOPIC_LEXICON.items():
        for kw in keywords:
            if kw in lower:
                scores[topic] += lower.count(kw)

    words = [w.lower() for w in _WORD.findall(lower) if len(w) > 4]
    word_freq = Counter(words)
    for word, count in word_freq.most_common(30):
        if count >= 3 and word not in scores:
            scores[word] = count * 0.5

    ranked = [t for t, _ in scores.most_common(limit)]
    topics = ranked[: max(3, limit // 2)]
    tags = ranked[:limit]
    return topics, tags
