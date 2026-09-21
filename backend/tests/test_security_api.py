import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security.passwords import hash_password, verify_password
from app.security.tokens import TokenError, create_access_token, create_refresh_token, decode_token

SECRET = "x" * 40


def test_password_hashing():
    h = hash_password("correct horse")
    assert h != "correct horse" and verify_password("correct horse", h) and not verify_password("wrong", h)
    assert not verify_password("anything", "not-a-hash")


def test_tokens_are_typed_and_verified():
    access = create_access_token(SECRET, "user-1")
    refresh, jti = create_refresh_token(SECRET, "user-1")
    assert decode_token(SECRET, access, "access")["sub"] == "user-1"
    assert decode_token(SECRET, refresh, "refresh")["jti"] == jti
    with pytest.raises(TokenError):
        decode_token(SECRET, refresh, "access")  # a refresh token cannot be used as an access token
    with pytest.raises(TokenError):
        decode_token("y" * 40, access, "access")
    expired = jwt.encode({"sub": "u", "typ": "access", "exp": int(time.time()) - 5}, SECRET, algorithm="HS256")
    with pytest.raises(TokenError):
        decode_token(SECRET, expired, "access")


client = TestClient(app)


def test_health_and_sample_flag():
    assert client.get("/health").json() == {"status": "ok"}
    body = client.get("/v1/opportunities").json()
    assert body["is_sample"] is True and body["items"][0]["score"] >= body["items"][-1]["score"]


def test_opportunity_detail_and_friendly_404():
    first = client.get("/v1/opportunities").json()["items"][0]
    detail = client.get(f"/v1/opportunities/{first['id']}").json()
    assert sum(f["points"] for f in detail["factors"]) == pytest.approx(detail["score"], abs=1)
    missing = client.get("/v1/opportunities/nope")
    assert missing.status_code == 404 and "expired" in missing.json()["detail"]


def test_discover_reports_insufficient_signal():
    body = client.get("/v1/discover", params={"niche": "Gaming"}).json()
    assert body["status"] == "insufficient_signal" and body["detail"]["questions_needed"] == 12


def test_bundle_has_everything_the_app_renders():
    b = client.get("/v1/bundle").json()
    assert b["is_sample"] is True
    assert {"opportunities", "radar", "new_questions", "niches", "insufficient", "categories"} <= set(b)
