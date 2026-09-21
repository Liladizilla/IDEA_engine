"""Explainable opportunity score (spec sections 20-23, 64).

score = sum(weight_i * effective_value_i), weights sum to 1, values are 0-100.
Competition and answer saturation are inverted (100 - value): open space earns points.
Every point of the score is attributable to a named factor, so the UI can always answer "why?".
This is the strength of detected evidence. It is NOT a prediction of virality.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pydantic import BaseModel, Field

WEIGHTS: dict[str, float] = {
    "demand": 0.18,
    "question_density": 0.14,
    "growth": 0.14,
    "dissatisfaction": 0.16,
    "engagement": 0.08,
    "audience_value": 0.06,
    "recency": 0.06,
    "competition": 0.10,
    "answer_saturation": 0.08,
}
INVERTED = {"competition", "answer_saturation"}
LABELS = {
    "demand": "Demand",
    "question_density": "Question density",
    "growth": "Growth",
    "dissatisfaction": "Dissatisfaction",
    "engagement": "Engagement",
    "audience_value": "Audience value",
    "recency": "Recency",
    "competition": "Competition",
    "answer_saturation": "Answer coverage",
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

MIN_QUESTIONS = 12
MIN_SOURCES = 2


class ScoreInputs(BaseModel):
    demand: float = Field(ge=0, le=100)
    question_density: float = Field(ge=0, le=100)
    growth: float = Field(ge=0, le=100)
    dissatisfaction: float = Field(ge=0, le=100)
    engagement: float = Field(ge=0, le=100)
    audience_value: float = Field(ge=0, le=100)
    recency: float = Field(ge=0, le=100)
    competition: float = Field(ge=0, le=100)
    answer_saturation: float = Field(ge=0, le=100)


class FactorScore(BaseModel):
    key: str
    label: str
    value: float
    weight: float
    inverted: bool
    points: float
    max_points: float
    note: str = ""


class ScoreResult(BaseModel):
    score: int
    band: str  # high | medium | low
    confidence: str  # high | medium | low
    factors: list[FactorScore]


class InsufficientSignal(BaseModel):
    reason: str
    questions_found: int
    questions_needed: int
    sources_found: int
    sources_needed: int


@dataclass(frozen=True)
class EvidenceStats:
    question_count: int
    source_count: int


def scale_log(x: float, reference: float) -> float:
    """0 at x=0, 100 at x>=reference, log-shaped in between (early counts matter most)."""
    if x <= 0:
        return 0.0
    return min(100.0, 100.0 * math.log1p(x) / math.log1p(reference))


def band(score: float) -> str:
    return "high" if score >= 75 else "medium" if score >= 50 else "low"


def confidence(e: EvidenceStats) -> str:
    if e.question_count >= 60 and e.source_count >= 3:
        return "high"
    if e.question_count >= 25 and e.source_count >= 2:
        return "medium"
    return "low"


def score_opportunity(
    inputs: ScoreInputs,
    evidence: EvidenceStats,
    notes: dict[str, str] | None = None,
    min_questions: int = MIN_QUESTIONS,
    min_sources: int = MIN_SOURCES,
) -> ScoreResult | InsufficientSignal:
    if evidence.question_count < min_questions or evidence.source_count < min_sources:
        return InsufficientSignal(
            reason="IDEA needs more evidence before identifying a reliable content opportunity.",
            questions_found=evidence.question_count,
            questions_needed=min_questions,
            sources_found=evidence.source_count,
            sources_needed=min_sources,
        )
    notes = notes or {}
    factors: list[FactorScore] = []
    total = 0.0
    for key, weight in WEIGHTS.items():
        value = getattr(inputs, key)
        effective = 100 - value if key in INVERTED else value
        points = weight * effective
        total += points
        factors.append(
            FactorScore(
                key=key,
                label=LABELS[key],
                value=round(value, 1),
                weight=weight,
                inverted=key in INVERTED,
                points=round(points, 2),
                max_points=round(weight * 100, 2),
                note=notes.get(key, ""),
            )
        )
    score = int(round(total))
    return ScoreResult(score=score, band=band(score), confidence=confidence(evidence), factors=factors)


@dataclass(frozen=True)
class ClusterStats:
    distinct_askers: int
    question_count: int
    growth_ratio: float
    dissatisfied_ratio: float
    median_engagement: float
    recent_share: float
    competing_videos: int
    answer_count: int
    answer_quality: float = 50.0  # 0-100; stays neutral until AI/human judges existing answers
    audience_value: float = 50.0


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


def derive_inputs(s: ClusterStats) -> ScoreInputs:
    return ScoreInputs(
        demand=scale_log(s.distinct_askers, 100),
        question_density=scale_log(s.question_count, 200),
        growth=_clamp(s.growth_ratio * 100),
        dissatisfaction=_clamp(s.dissatisfied_ratio * 250),
        engagement=scale_log(s.median_engagement, 300),
        audience_value=_clamp(s.audience_value),
        recency=_clamp(s.recent_share * 100),
        competition=scale_log(s.competing_videos, 60),
        answer_saturation=scale_log(s.answer_count, 30) * _clamp(s.answer_quality) / 100,
    )
