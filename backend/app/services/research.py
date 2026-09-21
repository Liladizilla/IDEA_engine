"""Research job processing."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers import get_ai_provider
from app.core.config import get_settings
from app.database.models import Job, Opportunity, QuestionCluster, Question, SourceItem, ResearchReport
from app.prompts.research import RESEARCH_SYSTEM, RESEARCH_USER_TEMPLATE


async def _gather_evidence(session: AsyncSession, cluster_id: uuid.UUID) -> dict[str, Any]:
    """Gather all evidence for a cluster."""
    # Get cluster
    cluster_result = await session.execute(
        select(QuestionCluster).where(QuestionCluster.id == cluster_id)
    )
    cluster = cluster_result.scalar_one_or_none()
    if not cluster:
        return {}

    # Get questions with source items
    q_result = await session.execute(
        select(Question, SourceItem)
        .join(SourceItem, Question.source_item_id == SourceItem.id)
        .where(Question.cluster_id == cluster_id)
    )
    questions = q_result.all()

    evidence = []
    for q, si in questions:
        evidence.append({
            "source": si.source,
            "kind": si.item_metadata.get("kind", "post"),
            "where": si.item_metadata.get("subreddit") or si.item_metadata.get("channel", ""),
            "excerpt": q.text[:500],
            "engagement": f"{int(si.engagement.get('views', 0))} views" if si.source == "youtube" else f"{int(si.engagement.get('score', 0))} upvotes",
            "url": si.url,
        })

    return {
        "representative_question": cluster.representative_question,
        "audience": cluster.audience,
        "question_count": len(questions),
        "sources": list(set(si.source for q, si in questions)),
        "evidence": evidence,
    }


async def run_research_job(session: AsyncSession, job_id: uuid.UUID) -> None:
    """Execute a research job and save the report."""
    job_result = await session.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        return

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    await session.commit()

    try:
        payload = job.payload
        opp_id = uuid.UUID(payload["opportunity_id"])
        user_id = uuid.UUID(payload["user_id"]) if payload.get("user_id") else None

        # Get opportunity and cluster
        opp_result = await session.execute(
            select(Opportunity, QuestionCluster)
            .join(QuestionCluster, Opportunity.cluster_id == QuestionCluster.id)
            .where(Opportunity.id == opp_id)
        )
        opp_row = opp_result.first()
        if not opp_row:
            raise ValueError("Opportunity not found")

        opp, cluster = opp_row

        # Gather evidence
        evidence_data = await _gather_evidence(session, cluster.id)

        # Generate research using AI
        settings = get_settings()
        ai_provider = get_ai_provider(settings)

        user_prompt = RESEARCH_USER_TEMPLATE.format(
            title=opp.title,
            core_question=evidence_data.get("representative_question", ""),
            audience=opp.audience or evidence_data.get("audience", ""),
            question_count=evidence_data.get("question_count", 0),
            sources=", ".join(evidence_data.get("sources", [])),
            evidence=json.dumps(evidence_data.get("evidence", []), indent=2),
        )

        result = await ai_provider.generate(
            system=RESEARCH_SYSTEM,
            user=user_prompt,
            json_mode=True,
            max_tokens=3000,
        )

        # Save research report
        report = ResearchReport(
            opportunity_id=opp_id,
            user_id=user_id,
            body=json.loads(result.text),
        )
        session.add(report)

        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        job.result = {"report_id": str(report.id)}

    except Exception as e:
        job.status = "failed"
        job.completed_at = datetime.now(timezone.utc)
        job.error = str(e)

    await session.commit()


async def start_research_job(session: AsyncSession, opportunity_id: uuid.UUID, user_id: uuid.UUID | None = None) -> Job:
    """Create and start a research job."""
    job = Job(
        type="research",
        payload={"opportunity_id": str(opportunity_id), "user_id": str(user_id) if user_id else None},
        status="pending",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Run in background with a NEW session (in production, use a proper task queue)
    import asyncio
    from app.database.session import SessionLocal
    asyncio.create_task(run_research_job_in_background(job.id))

    return job


async def run_research_job_in_background(job_id: uuid.UUID) -> None:
    """Run research job with a fresh database session."""
    from app.database.session import SessionLocal
    async with SessionLocal() as session:
        await run_research_job(session, job_id)