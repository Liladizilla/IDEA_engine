"""Reddit collector using the official OAuth API (app-only token).

Check Reddit's current Data API terms and approval requirements before shipping commercially.
Send a descriptive User-Agent and respect the rate-limit headers.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

import httpx

from app.providers.base import SourceProvider
from app.schemas.signals import RawItem

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API = "https://oauth.reddit.com"


class RedditRateLimited(RuntimeError):
    pass


class RedditCollector(SourceProvider):
    name = "reddit"

    def __init__(self, client_id: str, client_secret: str, user_agent: str, client: httpx.AsyncClient | None = None) -> None:
        self.client_id, self.client_secret, self.user_agent = client_id, client_secret, user_agent
        self.client = client or httpx.AsyncClient(timeout=15)
        self._token: str | None = None
        self._token_expiry = 0.0

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def _auth(self) -> str:
        if self._token and time.monotonic() < self._token_expiry:
            return self._token
        r = await self.client.post(
            TOKEN_URL,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": self.user_agent},
        )
        r.raise_for_status()
        body = r.json()
        self._token = body["access_token"]
        self._token_expiry = time.monotonic() + int(body.get("expires_in", 3600)) - 60
        return self._token

    async def _get(self, path: str, params: dict) -> dict:
        token = await self._auth()
        r = await self.client.get(
            f"{API}{path}",
            params={**params, "raw_json": 1},
            headers={"Authorization": f"bearer {token}", "User-Agent": self.user_agent},
        )
        if r.status_code == 429 or float(r.headers.get("x-ratelimit-remaining", 10)) < 1:
            raise RedditRateLimited(f"retry after {r.headers.get('x-ratelimit-reset', '?')}s")
        r.raise_for_status()
        return r.json()

    async def collect(self, query: str, limit: int = 25, subreddit: str | None = None, with_comments: int = 3) -> list[RawItem]:
        path = f"/r/{subreddit}/search" if subreddit else "/search"
        params = {"q": query, "sort": "relevance", "t": "month", "limit": min(limit, 100), "type": "link"}
        if subreddit:
            params["restrict_sr"] = 1
        listing = await self._get(path, params)
        posts = [c["data"] for c in listing.get("data", {}).get("children", []) if c.get("kind") == "t3"]
        items = [self._post(p, query) for p in posts]
        for p in sorted(posts, key=lambda x: x.get("num_comments", 0), reverse=True)[:with_comments]:
            items.extend(await self._comments(p, query))
        return items

    @staticmethod
    def _post(p: dict, query: str) -> RawItem:
        return RawItem(
            source="reddit",
            external_id=f"post:{p['id']}",
            title=p.get("title", ""),
            content=p.get("selftext", ""),
            url=f"https://www.reddit.com{p.get('permalink', '')}",
            created_at=datetime.fromtimestamp(p.get("created_utc", 0), tz=timezone.utc),
            engagement={"score": float(p.get("score", 0)), "comments": float(p.get("num_comments", 0)), "upvote_ratio": float(p.get("upvote_ratio", 0))},
            metadata={"kind": "post", "subreddit": p.get("subreddit"), "author_key": p.get("author"), "query": query},
        )

    async def _comments(self, post: dict, query: str) -> list[RawItem]:
        data = await self._get(f"/comments/{post['id']}", {"limit": 25, "depth": 1, "sort": "top"})
        if not isinstance(data, list) or len(data) < 2:
            return []
        out = []
        for c in data[1].get("data", {}).get("children", []):
            if c.get("kind") != "t1":
                continue
            d = c["data"]
            out.append(
                RawItem(
                    source="reddit",
                    external_id=f"comment:{d['id']}",
                    title=post.get("title", ""),
                    content=d.get("body", ""),
                    url=f"https://www.reddit.com{d.get('permalink', '')}",
                    created_at=datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc),
                    engagement={"score": float(d.get("score", 0))},
                    metadata={"kind": "comment", "subreddit": post.get("subreddit"), "author_key": d.get("author"), "query": query},
                )
            )
        return out
