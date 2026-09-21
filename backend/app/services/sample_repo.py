"""Serves fixture data until the database pipeline is wired. Every payload carries is_sample = true."""
import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "sample" / "data.json"


@lru_cache
def bundle() -> dict:
    return json.loads(DATA.read_text())


def opportunities(q: str | None = None, min_score: int = 0) -> list[dict]:
    items = [o for o in bundle()["opportunities"] if o["score"] >= min_score]
    if q:
        needle = q.lower()
        items = [o for o in items if needle in f"{o['title']} {o['core_question']} {o['audience']}".lower()]
    return items


def opportunity(opp_id: str) -> dict | None:
    return next((o for o in bundle()["opportunities"] if o["id"] == opp_id), None)
