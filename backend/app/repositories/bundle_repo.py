"""Database-backed bundle repository replacing sample_repo."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    Opportunity,
    QuestionCluster,
    Question,
    Signal,
    TrendSnapshot,
    SourceItem,
)
from app.schemas.signals import RawItem


def _cluster_to_opportunity_dict(cluster: QuestionCluster, opp: Opportunity, stats: dict[str, Any]) -> dict:
    """Convert cluster + opportunity to bundle opportunity dict."""
    sources_count: dict[str, int] = {}
    questions_data = stats.get("questions", [])
    for item in questions_data:
        if isinstance(item, tuple):
            q, si = item
            sources_count[si.source] = sources_count.get(si.source, 0) + 1
        else:
            sources_count[item.source] = sources_count.get(item.source, 0) + 1

    related_questions = []
    for item in questions_data[:5]:
        if isinstance(item, tuple):
            q, si = item
            related_questions.append(q.text)
        else:
            related_questions.append(item.question)

    return {
        "id": str(opp.id),
        "title": opp.title,
        "core_question": stats.get("representative_question", ""),
        "audience": opp.audience or "",
        "why_detected": f"Cluster of {len(questions_data)} questions from {len(sources_count)} sources.",
        "score": opp.overall_score,
        "band": "high" if opp.overall_score >= 75 else "medium" if opp.overall_score >= 50 else "low",
        "confidence": opp.confidence,
        "factors": opp.factors,
        "stats": {
            "related_questions": len(questions_data),
            "askers": stats.get("distinct_askers", 0),
            "communities": len(sources_count),
            "growth_7d": stats.get("growth", 0),
            "velocity": stats.get("velocity", "unknown"),
            "sources": sources_count,
        },
        "trend": stats.get("trend", []),
        "competition": {
            "level": "low",
            "creators": 0,
            "note": "Competitor analysis not yet implemented.",
        },
        "answer_gap": {
            "level": "high",
            "note": "Answer quality assessment pending.",
        },
        "evidence": stats.get("evidence", []),
        "related_questions": related_questions,
        "ideas": [],
    }


async def get_bundle(session: AsyncSession) -> dict:
    """Get all data needed for mobile app main screens in one query."""
    now = datetime.now(timezone.utc)

    # Get opportunities with their clusters
    opp_result = await session.execute(
        select(Opportunity, QuestionCluster)
        .join(QuestionCluster, Opportunity.cluster_id == QuestionCluster.id)
        .order_by(desc(Opportunity.overall_score))
    )
    opp_clusters = opp_result.all()

    # Get radar signals (recent signals)
    signal_result = await session.execute(
        select(Signal, QuestionCluster)
        .join(QuestionCluster, Signal.cluster_id == QuestionCluster.id)
        .where(Signal.detected_at >= now - timedelta(hours=24))
        .order_by(desc(Signal.detected_at))
        .limit(20)
    )
    signals = signal_result.all()

    # Get insufficient signal clusters (low question count)
    # This would need a more sophisticated query, for now return empty
    insufficient = []

    # Get categories from source items
    cat_result = await session.execute(
        select(SourceItem.source).distinct()
    )
    categories = [row[0] for row in cat_result.all()]

    opportunities = []
    for opp, cluster in opp_clusters:
        # Get questions for this cluster
        q_result = await session.execute(
            select(Question, SourceItem)
            .join(SourceItem, Question.source_item_id == SourceItem.id)
            .where(Question.cluster_id == cluster.id)
        )
        question_rows = q_result.all()

        # Get trend snapshots
        trend_result = await session.execute(
            select(TrendSnapshot)
            .where(TrendSnapshot.cluster_id == cluster.id)
            .order_by(TrendSnapshot.day)
        )
        trend_snapshots = trend_result.scalars().all()

        # Convert rows to (Question, SourceItem) tuples
        questions = [(row.Question, row.SourceItem) for row in question_rows]

        # Build evidence from source items
        evidence = []
        for q, si in questions:
            if len(evidence) >= 4:
                break
            evidence.append({
                "source": si.source,
                "kind": si.item_metadata.get("kind", "post"),
                "where": si.item_metadata.get("subreddit") or si.item_metadata.get("channel", ""),
                "excerpt": q.text[:300],
                "engagement": f"{int(si.engagement.get('views', 0))} views" if si.source == "youtube" else f"{int(si.engagement.get('score', 0))} upvotes",
                "days_ago": (now - si.created_at).days,
                "url": si.url,
            })

        stats = {
            "question_count": len(questions),
            "distinct_askers": len({(si.source, si.item_metadata.get("author_key", "")) for q, si in questions}),
            "growth": 0.0,
            "velocity": "stable",
            "questions": questions,
            "evidence": evidence,
            "trend": [s.signal_count for s in trend_snapshots],
        }

        opportunities.append(_cluster_to_opportunity_dict(cluster, opp, stats))

    # Build radar signals
    radar_signals = []
    for row in signals:
        signal = row.Signal
        cluster = row.QuestionCluster
        radar_signals.append({
            "question": cluster.representative_question,
            "opportunity_id": None,  # Would need to find matching opportunity
            "sources": ["youtube"],  # Simplified - would compute from questions
            "momentum": signal.momentum,
            "answer_gap": "high",
            "minutes_ago": int((now - signal.detected_at).total_seconds() / 60),
        })

    return {
        "is_sample": False,
        "opportunities": opportunities,
        "radar": radar_signals,
        "new_questions": [],
        "niches": [],
        "insufficient": insufficient,
        "categories": categories,
    }


async def get_opportunity_detail(session: AsyncSession, opp_id: uuid.UUID) -> dict | None:
    """Get full opportunity detail for opportunity screen."""
    result = await session.execute(
        select(Opportunity, QuestionCluster)
        .join(QuestionCluster, Opportunity.cluster_id == QuestionCluster.id)
        .where(Opportunity.id == opp_id)
    )
    row = result.first()
    if not row:
        return None

    opp, cluster = row

    # Get questions
    q_result = await session.execute(
        select(Question, SourceItem)
        .join(SourceItem, Question.source_item_id == SourceItem.id)
        .where(Question.cluster_id == cluster.id)
    )
    questions = q_result.all()

    # Get trend
    trend_result = await session.execute(
        select(TrendSnapshot)
        .where(TrendSnapshot.cluster_id == cluster.id)
        .order_by(TrendSnapshot.day)
    )
    trend = [s.signal_count for s in trend_result.scalars()]

    # Build evidence
    evidence = []
    for q, si in questions[:10]:
        evidence.append({
            "source": si.source,
            "kind": si.item_metadata.get("kind", "post"),
            "where": si.item_metadata.get("subreddit") or si.item_metadata.get("channel", ""),
            "excerpt": q.text[:300],
            "engagement": f"{int(si.engagement.get('views', 0))} views" if si.source == "youtube" else f"{int(si.engagement.get('score', 0))} upvotes",
            "days_ago": (datetime.now(timezone.utc) - si.created_at).days,
            "url": si.url,
        })

    sources_count: dict[str, int] = {}
    for q, si in questions:
        sources_count[si.source] = sources_count.get(si.source, 0) + 1

    return {
        "is_sample": False,
        "id": str(opp.id),
        "title": opp.title,
        "core_question": cluster.representative_question,
        "audience": opp.audience or "",
        "why_detected": f"Cluster of {len(questions)} questions from {len(sources_count)} sources.",
        "score": opp.overall_score,
        "band": "high" if opp.overall_score >= 75 else "medium" if opp.overall_score >= 50 else "low",
        "confidence": opp.confidence,
        "factors": opp.factors,
        "stats": {
            "related_questions": len(questions),
            "askers": len({(si.source, si.item_metadata.get("author_key", "")) for q, si in questions}),
            "communities": len(sources_count),
            "growth_7d": 0.0,
            "velocity": "stable",
            "sources": sources_count,
        },
        "trend": trend,
        "competition": {"level": "low", "creators": 0, "note": "Competitor analysis pending."},
        "answer_gap": {"level": "high", "note": "Answer quality assessment pending."},
        "evidence": evidence,
        "related_questions": [q.text for q, si in questions[:10]],
        "ideas": [],
    }


async def list_opportunities(
    session: AsyncSession,
    query: str | None = None,
    min_score: int = 0,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List opportunities with optional filtering."""
    stmt = (
        select(Opportunity, QuestionCluster)
        .join(QuestionCluster, Opportunity.cluster_id == QuestionCluster.id)
        .where(Opportunity.overall_score >= min_score)
        .order_by(desc(Opportunity.overall_score))
        .limit(limit)
        .offset(offset)
    )

    if query:
        needle = query.lower()
        # Simple text search - in production use pgvector similarity
        stmt = stmt.where(
            Opportunity.title.ilike(f"%{needle}%")
            | QuestionCluster.representative_question.ilike(f"%{needle}%")
        )

    result = await session.execute(stmt)
    items = []
    for opp, cluster in result.all():
        items.append({
            "id": str(opp.id),
            "title": opp.title,
            "core_question": cluster.representative_question,
            "audience": opp.audience or "",
            "score": opp.overall_score,
            "band": "high" if opp.overall_score >= 75 else "medium" if opp.overall_score >= 50 else "low",
        })
    return items


async def get_opportunity(session: AsyncSession, opp_id: uuid.UUID) -> dict | None:
    """Get single opportunity by ID."""
    return await get_opportunity_detail(session, opp_id)