"""RawItem[] -> questions -> clusters -> stats -> scores. Pure function of its inputs (embedder is injected)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from statistics import median
from typing import Protocol

from app.ai.base import AIProvider
from app.intelligence.clustering import QuestionCluster, cluster_questions, cosine, dedupe
from app.intelligence.questions import extract_signals
from app.intelligence.scoring import (
    ClusterStats,
    EvidenceStats,
    InsufficientSignal,
    ScoreResult,
    derive_inputs,
    score_opportunity,
)
from app.intelligence.velocity import Velocity, classify_velocity, daily_counts, growth_ratio
from app.schemas.signals import RawItem

COMPETITOR_SIMILARITY = 0.3


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass
class Candidate:
    cluster: QuestionCluster
    stats: ClusterStats
    result: ScoreResult
    velocity: Velocity
    daily: list[int]
    competing: list[RawItem] = field(default_factory=list)


@dataclass
class PipelineOutput:
    candidates: list[Candidate] = field(default_factory=list)
    insufficient: list[tuple[str, InsufficientSignal]] = field(default_factory=list)
    questions_extracted: int = 0


async def run_pipeline(
    items: list[RawItem],
    embedder: Embedder | AIProvider,
    now: datetime | None = None,
    threshold: float = 0.5,
    audience_value: float = 50.0,
    min_questions: int = 12,
    min_sources: int = 2,
) -> PipelineOutput:
    now = now or datetime.now(timezone.utc)
    out = PipelineOutput()
    questions = dedupe([q for item in items for q in extract_signals(item)])
    out.questions_extracted = len(questions)
    if not questions:
        return out

    videos = [i for i in items if i.metadata.get("kind") == "video"]
    question_texts = [q.question for q in questions]
    vectors = await embedder.embed(question_texts)
    video_vectors = await embedder.embed([v.title for v in videos]) if videos else []

    for cluster in cluster_questions(questions, vectors, threshold):
        rep = cluster.representative
        competing = [
            v for v, vv in zip(videos, video_vectors) if cosine(vv, cluster.centroid) >= COMPETITOR_SIMILARITY
        ]
        counts = daily_counts([m.created_at for m in cluster.members], 14, now)
        n = len(cluster.members)
        stats = ClusterStats(
            distinct_askers=cluster.distinct_askers,
            question_count=n,
            growth_ratio=max(0.0, growth_ratio(counts)),
            dissatisfied_ratio=sum(m.dissatisfied for m in cluster.members) / n,
            median_engagement=median(m.engagement for m in cluster.members),
            recent_share=sum(m.created_at >= now - timedelta(days=14) for m in cluster.members) / n,
            competing_videos=len(competing),
            answer_count=len(competing),
            audience_value=audience_value,
        )
        result = score_opportunity(
            derive_inputs(stats),
            EvidenceStats(question_count=n, source_count=len(cluster.sources)),
            notes={"answer_saturation": "Answer quality not yet assessed; treated as neutral."},
            min_questions=min_questions,
            min_sources=min_sources,
        )
        if isinstance(result, InsufficientSignal):
            out.insufficient.append((rep.question, result))
        else:
            out.candidates.append(Candidate(cluster, stats, result, classify_velocity(counts), counts, competing))
    out.candidates.sort(key=lambda c: c.result.score, reverse=True)
    return out
