"""Auth routes: register, login, refresh, me."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.models import User
from app.database.session import get_session
from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_access_token, create_refresh_token, decode_token, TokenError

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _jwt_secret() -> str:
    return get_settings().jwt_secret


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    id: str
    email: str
    locale: str
    plan: str
    created_at: datetime


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    access = create_access_token(_jwt_secret(), str(user.id))
    refresh = create_refresh_token(_jwt_secret(), str(user.id))[0]
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(_jwt_secret(), str(user.id))
    refresh = create_refresh_token(_jwt_secret(), str(user.id))[0]
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest):
    try:
        claims = decode_token(_jwt_secret(), payload.refresh_token, "refresh")
    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access = create_access_token(_jwt_secret(), claims["sub"])
    refresh = create_refresh_token(_jwt_secret(), claims["sub"])[0]
    return TokenResponse(access_token=access, refresh_token=refresh)


async def get_current_user(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        claims = decode_token(_jwt_secret(), token, "access")
    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(select(User).where(User.id == claims["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user)):
    return MeResponse(
        id=str(user.id),
        email=user.email,
        locale=user.locale,
        plan=user.plan,
        created_at=user.created_at,
    )