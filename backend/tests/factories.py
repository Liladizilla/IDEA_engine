"""Synthetic datasets (spec section 78): duplicates, similar, unrelated, spam, emerging, declining."""
from datetime import datetime, timedelta, timezone

from app.schemas.signals import RawItem

NOW = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)

WEBSITE_QUESTIONS = [
    "How do I build a cheap website for my small business?",
    "What's the cheapest way to build a website for a small business?",
    "Can I build a business website cheaply without an agency?",
    "How can a small business build a website cheaply?",
    "Is there a cheap way to build a small business website?",
    "How do I make a cheap website for my business without an agency?",
]
SOURDOUGH = [
    "Why does my sourdough starter smell like acetone?",
    "Why is my sourdough starter smelling like nail polish remover?",
]
UNRELATED = [
    "How do I replace a bicycle chain quickly?",
    "What is the best way to learn the violin as an adult?",
    "Why is the moon sometimes visible during the day?",
]


def post(n: int, text: str, days_ago: int, source="reddit", author=None, score=10, kind="post") -> RawItem:
    return RawItem(
        source=source, external_id=f"{kind}-{n}", title=text, content="", url=f"https://example.test/{n}",
        created_at=NOW - timedelta(days=days_ago, hours=1), engagement={"score": float(score)},
        metadata={"kind": kind, "author_key": author or f"user{n}"},
    )


def video(n: int, title: str, views=50000) -> RawItem:
    return RawItem(
        source="youtube", external_id=f"video-{n}", title=title, content="", url=f"https://example.test/v{n}",
        created_at=NOW - timedelta(days=30), engagement={"views": float(views)}, metadata={"kind": "video", "author_key": f"ch{n}"},
    )


def strong_cluster_items() -> list[RawItem]:
    """30 different people asking about cheap websites, across 2 sources, accelerating over 14 days."""
    items, n = [], 0
    for day in range(14):
        for k in range(1 + day // 3 * 1):  # more each day
            q = WEBSITE_QUESTIONS[(n + k) % len(WEBSITE_QUESTIONS)]
            src = "reddit" if n % 2 == 0 else "youtube"
            items.append(post(n, q, 13 - day, source=src, kind="post" if src == "reddit" else "comment"))
            n += 1
    return items


def noisy_dataset() -> list[RawItem]:
    items = strong_cluster_items()
    base = len(items) + 100
    items += [post(base, "Check out my channel for free giveaways!!!", 1)]  # spam: not a question
    items += [post(base + 1 + i, q, 2) for i, q in enumerate(UNRELATED)]  # unrelated singles
    items += [post(base + 10 + i, q, 3, author="same_person") for i, q in enumerate(SOURDOUGH[:1] * 3)]  # one person repeating
    items += [video(1, "Build a website in 10 minutes"), video(2, "Cheap website for small business owners")]
    return items
