"""Semantic clustering (greedy leader clustering over embeddings) and deduplication."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from app.schemas.signals import ExtractedQuestion


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def _norm(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


def dedupe(questions: list[ExtractedQuestion]) -> list[ExtractedQuestion]:
    """Drop the same author repeating the same text. Different people asking the same thing IS demand, so it stays."""
    seen: set[tuple[str, str, str]] = set()
    out = []
    for q in questions:
        key = (q.source, q.author_key or q.item_id, _norm(q.question))
        if key in seen:
            continue
        seen.add(key)
        out.append(q)
    return out


@dataclass
class QuestionCluster:
    members: list[ExtractedQuestion] = field(default_factory=list)
    vectors: list[list[float]] = field(default_factory=list)
    centroid: list[float] = field(default_factory=list)

    def add(self, q: ExtractedQuestion, v: list[float]) -> None:
        n = len(self.members)
        self.members.append(q)
        self.vectors.append(v)
        self.centroid = list(v) if n == 0 else [(c * n + x) / (n + 1) for c, x in zip(self.centroid, v)]

    @property
    def representative(self) -> ExtractedQuestion:
        best = max(range(len(self.members)), key=lambda i: cosine(self.vectors[i], self.centroid))
        return self.members[best]

    @property
    def sources(self) -> set[str]:
        return {m.source for m in self.members}

    @property
    def distinct_askers(self) -> int:
        return len({(m.source, m.author_key or m.item_id) for m in self.members})


def cluster_questions(
    questions: list[ExtractedQuestion], vectors: list[list[float]], threshold: float = 0.5
) -> list[QuestionCluster]:
    order = sorted(range(len(questions)), key=lambda i: questions[i].engagement, reverse=True)
    clusters: list[QuestionCluster] = []
    for i in order:
        best, best_sim = None, threshold
        for c in clusters:
            sim = cosine(vectors[i], c.centroid)
            if sim >= best_sim:
                best, best_sim = c, sim
        if best is None:
            best = QuestionCluster()
            clusters.append(best)
        best.add(questions[i], vectors[i])
    return sorted(clusters, key=lambda c: len(c.members), reverse=True)
