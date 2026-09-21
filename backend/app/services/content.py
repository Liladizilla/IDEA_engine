"""Content generation job processing."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers import get_ai_provider
from app.core.config import get_settings
from app.database.models import Job, Opportunity, QuestionCluster, Question, SourceItem, ContentProject
from app.prompts.content import CONTENT_SYSTEM, CONTENT_USER_TEMPLATE


async def _gather_research_brief(session: AsyncSession, opportunity_id: uuid.UUID) -> dict[str, Any]:
    """Get the latest research report for an opportunity."""
    from app.database.models import ResearchReport

    result = await session.execute(
        select(ResearchReport)
        .where(ResearchReport.opportunity_id == opportunity_id)
        .order_by(ResearchReport.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    if not report:
        return {}
    return report.body


async def run_content_job(session: AsyncSession, job_id: uuid.UUID) -> None:
    """Execute a content generation job and save the project."""
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
        format_type = payload.get("format", "youtube_long")
        difficulty = payload.get("difficulty", "medium")

        # Get research brief
        research_brief = await _gather_research_brief(session, opp_id)
        if not research_brief:
            raise ValueError("No research report found. Run research first.")

        # Generate content using AI
        settings = get_settings()
        ai_provider = get_ai_provider(settings)

        user_prompt = CONTENT_USER_TEMPLATE.format(
            research_brief=json.dumps(research_brief, indent=2),
            format=format_type,
            difficulty=difficulty,
        )

        result = await ai_provider.generate(
            system=CONTENT_SYSTEM,
            user=user_prompt,
            json_mode=True,
            max_tokens=3000,
        )

        content_data = json.loads(result.text)

        # Save content project
        project = ContentProject(
            user_id=user_id,
            opportunity_id=opp_id,
            format=format_type,
            status="draft",
            body=content_data,
        )
        session.add(project)

        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        job.result = {"project_id": str(project.id)}

    except Exception as e:
        job.status = "failed"
        job.completed_at = datetime.now(timezone.utc)
        job.error = str(e)

    await session.commit()


async def start_content_job(
    session: AsyncSession,
    opportunity_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    format_type: str = "youtube_long",
    difficulty: str = "medium",
) -> Job:
    """Create and start a content generation job."""
    job = Job(
        type="content",
        payload={
            "opportunity_id": str(opportunity_id),
            "user_id": str(user_id) if user_id else None,
            "format": format_type,
            "difficulty": difficulty,
        },
        status="pending",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Run in background with a NEW session
    import asyncio
    from app.database.session import SessionLocal
    asyncio.create_task(run_content_job_in_background(job.id))

    return job


async def run_content_job_in_background(job_id: uuid.UUID) -> None:
    """Run content job with a fresh database session."""
    from app.database.session import SessionLocal
    async with SessionLocal() as session:
        await run_content_job(session, job_id)