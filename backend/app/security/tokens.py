"""JWT access + refresh tokens. Refresh tokens carry a jti so they can be revoked/rotated in the database."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

ALGORITHM = "HS256"
ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=30)


class TokenError(ValueError):
    pass


def _make(secret: str, subject: str, kind: str, ttl: timedelta) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = uuid.uuid4().hex
    token = jwt.encode({"sub": subject, "typ": kind, "jti": jti, "iat": now, "exp": now + ttl}, secret, algorithm=ALGORITHM)
    return token, jti


def create_access_token(secret: str, subject: str) -> str:
    return _make(secret, subject, "access", ACCESS_TTL)[0]


def create_refresh_token(secret: str, subject: str) -> tuple[str, str]:
    return _make(secret, subject, "refresh", REFRESH_TTL)


def decode_token(secret: str, token: str, expected_type: str) -> dict:
    try:
        claims = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    if claims.get("typ") != expected_type:
        raise TokenError("wrong token type")
    return claims
