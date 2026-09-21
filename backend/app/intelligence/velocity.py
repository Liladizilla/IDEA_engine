"""Trend velocity (spec section 36): EMERGING / ACCELERATING / STABLE / DECLINING from daily signal counts."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from statistics import mean


class Velocity(str, Enum):
    EMERGING = "emerging"
    ACCELERATING = "accelerating"
    STABLE = "stable"
    DECLINING = "declining"
    UNKNOWN = "unknown"


def daily_counts(times: list[datetime], days: int = 14, now: datetime | None = None) -> list[int]:
    now = now or datetime.now(timezone.utc)
    start = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    counts = [0] * days
    for t in times:
        idx = (t - start).days
        if 0 <= idx < days:
            counts[idx] += 1
    return counts


def growth_ratio(counts: list[int]) -> float:
    """Relative change between the first and second half of the window (0.5 = +50%)."""
    half = len(counts) // 2
    early, late = mean(counts[:half]), mean(counts[-half:])
    return (late - early) / max(early, 1.0)


def classify_velocity(counts: list[int], baseline: float = 2.0, emerging_min: float = 5.0) -> Velocity:
    if len(counts) < 4 or sum(counts) == 0:
        return Velocity.UNKNOWN
    half = len(counts) // 2
    early, late = mean(counts[:half]), mean(counts[-half:])
    if early < baseline and late >= emerging_min:
        return Velocity.EMERGING
    g = growth_ratio(counts)
    if g >= 0.25:
        return Velocity.ACCELERATING
    if g <= -0.25:
        return Velocity.DECLINING
    return Velocity.STABLE
