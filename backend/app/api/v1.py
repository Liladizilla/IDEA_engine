from fastapi import APIRouter, HTTPException, Query, Depends
import uuid

from app.database.session import get_session
from app.repositories import bundle_repo
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1")


@router.get("/bundle")
async def bundle(session: AsyncSession = Depends(get_session)):
    """Everything the mobile app needs for its main screens in one cached round trip."""
    return await bundle_repo.get_bundle(session)


@router.get("/home")
async def home(session: AsyncSession = Depends(get_session)):
    b = await bundle_repo.get_bundle(session)
    return {"is_sample": b["is_sample"], "opportunities": b["opportunities"][:3], "new_questions": b["new_questions"], "niches": b["niches"]}


@router.get("/opportunities")
async def list_opportunities(q: str | None = None, min_score: int = Query(0, ge=0, le=100), session: AsyncSession = Depends(get_session)):
    return {"is_sample": False, "items": await bundle_repo.list_opportunities(session, q, min_score)}


@router.get("/opportunities/{opp_id}")
async def get_opportunity(opp_id: str, session: AsyncSession = Depends(get_session)):
    try:
        opp_uuid = uuid.UUID(opp_id)
    except ValueError:
        raise HTTPException(404, "Invalid opportunity ID")
    found = await bundle_repo.get_opportunity(session, opp_uuid)
    if found is None:
        raise HTTPException(404, "That opportunity no longer exists. It may have expired from the radar.")
    return found


@router.get("/radar")
async def radar(session: AsyncSession = Depends(get_session)):
    b = await bundle_repo.get_bundle(session)
    return {"is_sample": b["is_sample"], "signals": b["radar"], "insufficient": b["insufficient"]}


@router.get("/niches")
async def niches(session: AsyncSession = Depends(get_session)):
    b = await bundle_repo.get_bundle(session)
    return {"is_sample": b["is_sample"], "items": b["niches"], "categories": b["categories"]}


@router.get("/discover")
async def discover(niche: str | None = None, session: AsyncSession = Depends(get_session)):
    """No niche given: scan across categories. Niche given: analyse that ecosystem."""
    b = await bundle_repo.get_bundle(session)
    if niche and any(i["scope"].lower() == niche.lower() for i in b["insufficient"]):
        return {"is_sample": False, "status": "insufficient_signal", "detail": next(i for i in b["insufficient"] if i["scope"].lower() == niche.lower())}
    return {"is_sample": False, "status": "ok", "opportunities": b["opportunities"][:3]}