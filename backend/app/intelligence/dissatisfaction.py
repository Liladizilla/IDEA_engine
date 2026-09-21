"""Rule-based dissatisfaction detection (spec section 21). A cheap first pass; AI refines it later."""
import re

PATTERNS: dict[str, re.Pattern[str]] = {
    "cant_find": re.compile(r"\bi can'?t (?:seem to )?find\b", re.I),
    "nobody_explains": re.compile(r"\b(?:nobody|no one)\s+(?:actually\s+)?(?:explains|shows|talks about|covers)\b", re.I),
    "still_confused": re.compile(r"\bstill (?:confused|stuck|lost)\b", re.I),
    "doesnt_work": re.compile(r"\b(?:doesn'?t|does not|didn'?t|did not|won'?t) (?:actually )?work\b", re.I),
    "outdated": re.compile(r"\b(?:outdated|out of date|deprecated)\b", re.I),
    "every_tutorial": re.compile(r"\bevery (?:tutorial|video|guide|article)\b", re.I),
    "none_of_them": re.compile(r"\bnone of (?:them|the (?:tutorials|videos|guides))\b", re.I),
    "ive_tried": re.compile(r"\bi'?ve (?:tried|watched|read|followed)\b", re.I),
    "can_someone_actually": re.compile(r"\bcan (?:someone|anyone) actually\b", re.I),
    "why_doesnt_anyone": re.compile(r"\bwhy (?:doesn'?t|does not|won'?t) (?:anyone|anybody|nobody)\b", re.I),
    "no_clear_explanation": re.compile(r"\bno (?:clear|proper|real) (?:explanation|guide|tutorial|answer)\b", re.I),
}


def detect_dissatisfaction(text: str) -> list[str]:
    return [name for name, pattern in PATTERNS.items() if pattern.search(text)]


def is_dissatisfied(text: str) -> bool:
    return bool(detect_dissatisfaction(text))
