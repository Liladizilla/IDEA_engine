"""Question extraction and rule-based signal typing. The AI layer refines these; it never replaces the source text."""
from __future__ import annotations

import re

from app.intelligence.dissatisfaction import is_dissatisfied
from app.schemas.signals import ExtractedQuestion, RawItem, SignalType

_STARTS = re.compile(
    r"^(?:how (?:do|can|would|should|to|does|did)\b|why (?:does|do|is|isn'?t|doesn'?t|can'?t|won'?t|did|are)\b|"
    r"can (?:i|you|we|anyone|someone)\b|is it possible|what(?:'s| is| are| does| do)\b|does anyone know|"
    r"is there (?:a|an|any)\b|should i\b|which (?:is|one|should)\b|where (?:do|can|to)\b)",
    re.I,
)
_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_REQUEST = re.compile(r"\b(?:can someone|please help|need help|looking for|anyone know|any recommendations?)\b", re.I)
_TUTORIAL = re.compile(r"\b(?:tutorial|walkthrough|step[- ]by[- ]step|guide|course)\b", re.I)
_COMPARE = re.compile(r"\b(?:vs\.?|versus|better than|alternatives? to|compared to)\b", re.I)
_PURCHASE = re.compile(r"\b(?:buy|price|pricing|worth it|cheapest|best value|subscription)\b", re.I)


def classify_signal(sentence: str) -> SignalType:
    if is_dissatisfied(sentence):
        return SignalType.COMPLAINT
    if _COMPARE.search(sentence):
        return SignalType.COMPARISON
    if _TUTORIAL.search(sentence) and (_REQUEST.search(sentence) or sentence.strip().endswith("?")):
        return SignalType.TUTORIAL_REQUEST
    if _PURCHASE.search(sentence):
        return SignalType.PURCHASE_INTENT
    if _REQUEST.search(sentence):
        return SignalType.REQUEST
    if sentence.strip().endswith("?") or _STARTS.match(sentence.strip()):
        return SignalType.QUESTION
    return SignalType.OTHER


def extract_questions(text: str, min_words: int = 4, max_words: int = 60) -> list[str]:
    out = []
    for part in _SPLIT.split(text):
        s = part.strip(" \t\"'")
        words = len(s.split())
        if not (min_words <= words <= max_words):
            continue
        if s.endswith("?") or _STARTS.match(s):
            out.append(s)
    return out


def extract_signals(item: RawItem) -> list[ExtractedQuestion]:
    """Questions plus non-question complaints ("none of the tutorials show deployment")."""
    kind = item.metadata.get("kind")
    if kind in ("video", "article"):  # videos are existing answers, not demand
        return []
    engagement = sum(item.engagement.get(k, 0) for k in ("score", "likes", "comments", "replies"))
    found: list[ExtractedQuestion] = []
    seen: set[str] = set()
    for part in _SPLIT.split(item.text):
        s = part.strip(" \t\"'")
        words = len(s.split())
        if not (4 <= words <= 60) or s.lower() in seen:
            continue
        is_q = s.endswith("?") or bool(_STARTS.match(s))
        unhappy = is_dissatisfied(s)
        if not (is_q or unhappy):
            continue
        seen.add(s.lower())
        found.append(
            ExtractedQuestion(
                question=s,
                source=item.source,
                item_id=item.external_id,
                created_at=item.created_at,
                signal_type=classify_signal(s),
                author_key=item.metadata.get("author_key"),
                engagement=engagement,
                dissatisfied=unhappy,
            )
        )
    return found
