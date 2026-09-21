"""Persist pipeline output to PostgreSQL."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    AIRequest,
    CreatorProfile,
    Opportunity,
    Question,
    QuestionCluster,
    SavedItem,
    Signal,
    Source,
    SourceItem,
    TrendSnapshot,
    User,
)
from app.intelligence.pipeline import Candidate, PipelineOutput
from app.schemas.signals import RawItem


async def get_or_create_source(session: AsyncSession, kind: str, name: str, config: dict | None = None) -> Source:
    result = await session.execute(select(Source).where(Source.kind == kind, Source.name == name))
    source = result.scalar_one_or_none()
    if source is None:
        source = Source(kind=kind, name=name, config=config or {})
        session.add(source)
        await session.flush()
    return source


async def persist_source_items(session: AsyncSession, items: list[RawItem]) -> dict[str, uuid.UUID]:
    """Save source items, return mapping of external_id -> internal UUID."""
    mapping = {}
    for item in items:
        ext_key = (item.source, item.external_id)
        existing = await session.execute(
            select(SourceItem).where(SourceItem.source == item.source, SourceItem.external_id == item.external_id)
        )
        si = existing.scalar_one_or_none()
        if si is None:
            si = SourceItem(
                source=item.source,
                external_id=item.external_id,
                title=item.title,
                content=item.content,
                url=item.url,
                created_at=item.created_at,
                engagement=item.engagement,
                item_metadata=item.metadata,
            )
            session.add(si)
            await session.flush()
        mapping[f"{item.source}:{item.external_id}"] = si.id
    return mapping


async def persist_questions_and_clusters(
    session: AsyncSession,
    candidates: list[Candidate],
    source_item_map: dict[str, uuid.UUID],
    embedder,
) -> list[uuid.UUID]:
    """Persist questions, clusters, and return cluster IDs."""
    cluster_ids = []
    for cand in candidates:
        cluster = cand.cluster
        rep = cluster.representative
        db_cluster = QuestionCluster(
            representative_question=rep.question,
            audience=rep.audience,
            intent=rep.intent,
            question_count=len(cluster.members),
            source_count=len(cluster.sources),
            growth=cand.stats.growth_ratio,
            velocity=cand.velocity.value,
            centroid=cluster.centroid,
        )
        session.add(db_cluster)
        await session.flush()

        for i, member in enumerate(cluster.members):
            si_key = f"{member.source}:{member.item_id}"
            source_item_id = source_item_map.get(si_key)
            embedding = cluster.vectors[i] if i < len(cluster.vectors) else None
            question = Question(
                cluster_id=db_cluster.id,
                source_item_id=source_item_id,
                text=member.question,
                signal_type=member.signal_type,
                problem=member.problem,
                audience=member.audience,
                dissatisfied=member.dissatisfied,
                embedding=embedding,
                created_at=member.created_at,
            )
            session.add(question)

        cluster_ids.append(db_cluster.id)
    await session.flush()
    return cluster_ids


async def persist_opportunities(session: AsyncSession, candidates: list[Candidate], cluster_ids: list[uuid.UUID]) -> None:
    for cand, cluster_id in zip(candidates, cluster_ids):
        rep = cand.cluster.representative
        # Use representative question as title, truncate if needed
        title = rep.question[:200]
        opp = Opportunity(
            cluster_id=cluster_id,
            title=title,
            audience=rep.audience,
            overall_score=cand.result.score,
            confidence=cand.result.confidence,
            factors=[f.model_dump() for f in cand.result.factors],
            embedding=cand.cluster.centroid,
        )
        session.add(opp)
    await session.flush()


async def persist_signals_and_trends(session: AsyncSession, candidates: list[Candidate], cluster_ids: list[uuid.UUID]) -> None:
    now = datetime.now(timezone.utc)
    for cand, cluster_id in zip(candidates, cluster_ids):
        signal = Signal(
            cluster_id=cluster_id,
            detected_at=now,
            momentum=cand.velocity.value if isinstance(cand.velocity.value, float) else 0.0,
            sources=list(cand.cluster.sources),
        )
        session.add(signal)

        for i, count in enumerate(cand.daily):
            day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            from datetime import timedelta
            day = day - timedelta(days=len(cand.daily) - 1 - i)
            snapshot = TrendSnapshot(
                cluster_id=cluster_id,
                day=day,
                signal_count=count,
            )
            await session.merge(snapshot)
    await session.flush()


async def run_persist_cycle(output: PipelineOutput, collected_items: list[RawItem]) -> None:
    from app.database.session import SessionLocal
    from app.ai.providers import get_ai_provider
    from app.core.config import get_settings

    settings = get_settings()
    ai_provider = get_ai_provider(settings) if settings.hf_token or settings.openai_api_key else None

    async with SessionLocal() as session:
        async with session.begin():
            source_item_map = await persist_source_items(session, collected_items)

            cluster_ids = await persist_questions_and_clusters(session, output.candidates, source_item_map, ai_provider)
            await persist_opportunities(session, output.candidates, cluster_ids)
            await persist_signals_and_trends(session, output.candidates, cluster_ids)
            await session.commit()