"""Content generation endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database.models import Job, ContentProject, Opportunity, User
from app.database.session import get_session
from app.services.content import start_content_job

router = APIRouter(prefix="/v1", tags=["content"])


class ContentGenerateRequest(BaseModel):
    opportunity_id: str
    format: str = "youtube_long"
    difficulty: str = "medium"


class ContentGenerateResponse(BaseModel):
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


class ContentProjectResponse(BaseModel):
    id: str
    opportunity_id: str
    format: str
    status: str
    body: dict
    created_at: str


@router.post("/content/generate", response_model=ContentGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_content(
    payload: ContentGenerateRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        opp_uuid = uuid.UUID(payload.opportunity_id)
    except ValueError:
        raise HTTPException(404, "Opportunity not found")

    # Verify opportunity exists
    opp_result = await session.execute(select(Opportunity).where(Opportunity.id == opp_uuid))
    if not opp_result.scalar_one_or_none():
        raise HTTPException(404, "Opportunity not found")

    # Check if there's a research report
    from app.database.models import ResearchReport
    report_result = await session.execute(
        select(ResearchReport).where(ResearchReport.opportunity_id == opp_uuid).limit(1)
    )
    if not report_result.scalar_one_or_none():
        raise HTTPException(400, "Run research first before generating content")

    job = await start_content_job(
        session,
        opp_uuid,
        user.id,
        payload.format,
        payload.difficulty,
    )
    return ContentGenerateResponse(job_id=str(job.id), status=job.status)


@router.get("/content/projects/{project_id}", response_model=ContentProjectResponse)
async def get_content_project(
    project_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(404, "Content project not found")

    result = await session.execute(select(ContentProject).where(ContentProject.id == proj_uuid))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Content project not found")

    # Check ownership
    if project.user_id != user.id:
        raise HTTPException(403, "Not authorized")

    return ContentProjectResponse(
        id=str(project.id),
        opportunity_id=str(project.opportunity_id),
        format=project.format,
        status=project.status,
        body=project.body,
        created_at=project.created_at.isoformat(),
    )