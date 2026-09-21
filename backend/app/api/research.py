"""Research job endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database.models import Job, Opportunity, ResearchReport, User
from app.database.session import get_session
from app.services.research import start_research_job

router = APIRouter(prefix="/v1", tags=["research"])


class ResearchStartRequest(BaseModel):
    opportunity_id: str


class ResearchStartResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    id: str
    type: str
    status: str
    payload: dict
    result: dict | None = None
    error: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None


class ResearchReportResponse(BaseModel):
    id: str
    opportunity_id: str
    body: dict
    created_at: str


@router.post("/opportunities/{opp_id}/research", response_model=ResearchStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_research(
    opp_id: str,
    payload: ResearchStartRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        opp_uuid = uuid.UUID(opp_id)
    except ValueError:
        raise HTTPException(404, "Opportunity not found")

    # Verify opportunity exists
    opp_result = await session.execute(select(Opportunity).where(Opportunity.id == opp_uuid))
    if not opp_result.scalar_one_or_none():
        raise HTTPException(404, "Opportunity not found")

    job = await start_research_job(session, opp_uuid, user.id)
    return ResearchStartResponse(job_id=str(job.id), status=job.status)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(404, "Job not found")

    result = await session.execute(select(Job).where(Job.id == job_uuid))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")

    # Check ownership (unless admin)
    if job.payload.get("user_id") and job.payload["user_id"] != str(user.id):
        raise HTTPException(403, "Not authorized")

    return JobStatusResponse(
        id=str(job.id),
        type=job.type,
        status=job.status,
        payload=job.payload,
        result=job.result,
        error=job.error,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )


@router.get("/opportunities/{opp_id}/research", response_model=ResearchReportResponse)
async def get_research_report(
    opp_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        opp_uuid = uuid.UUID(opp_id)
    except ValueError:
        raise HTTPException(404, "Opportunity not found")

    # Get latest completed research report for this opportunity
    result = await session.execute(
        select(ResearchReport)
        .where(ResearchReport.opportunity_id == opp_uuid)
        .order_by(ResearchReport.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "No research report found. Start a research job first.")

    return ResearchReportResponse(
        id=str(report.id),
        opportunity_id=str(report.opportunity_id),
        body=report.body,
        created_at=report.created_at.isoformat(),
    )