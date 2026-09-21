"""Idea generation grounded in evidence. Refuses to run without evidence instead of inventing some."""
from __future__ import annotations

import json

from pydantic import BaseModel

from app.ai import prompts
from app.ai.base import AIProvider, parse_model
from app.intelligence.scoring import InsufficientSignal


class Idea(BaseModel):
    title: str
    hook: str
    audience: str
    core_question: str
    problem: str
    content_angle: str
    format: str
    difficulty: str
    why_now: str
    evidence_summary: str


class IdeaBatch(BaseModel):
    ideas: list[Idea]


async def generate_ideas(provider: AIProvider, evidence: list[dict], min_evidence: int = 3) -> IdeaBatch | InsufficientSignal:
    if len(evidence) < min_evidence:
        return InsufficientSignal(
            reason="IDEA needs more evidence before identifying a reliable content opportunity.",
            questions_found=len(evidence),
            questions_needed=min_evidence,
            sources_found=len({e.get("source") for e in evidence}),
            sources_needed=1,
        )
    result = await provider.generate(prompts.IDEA_SYSTEM, json.dumps({"evidence": evidence}), json_mode=True, max_tokens=1500)
    return parse_model(result.text, IdeaBatch)
