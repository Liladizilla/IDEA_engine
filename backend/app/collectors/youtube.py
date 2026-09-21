"""YouTube Data API v3 collector. The key stays on the backend.

Quota (default 10,000 units/day): search.list = 100, videos.list = 1, commentThreads.list = 1.
So one query costs ~100 + 1 + N comment calls. Everything is cached and budget-checked.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone

import httpx

from app.core.cache import Cache, MemoryTTLCache
from app.providers.base import SourceProvider
from app.schemas.signals import RawItem

BASE = "https://www.googleapis.com/youtube/v3"
COSTS = {"search": 100, "videos": 1, "commentThreads": 1}


class QuotaExceeded(RuntimeError):
    pass


class YouTubeQuota:
    def __init__(self, daily_budget: int = 8000) -> None:
        self.daily_budget = daily_budget
        self.used = 0
        self._day = date.today()

    def charge(self, operation: str) -> None:
        if date.today() != self._day:
            self._day, self.used = date.today(), 0
        cost = COSTS[operation]
        if self.used + cost > self.daily_budget:
            raise QuotaExceeded(f"YouTube quota budget of {self.daily_budget} units reached")
        self.used += cost


def _iso_duration_seconds(value: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class YouTubeCollector(SourceProvider):
    name = "youtube"

    def __init__(
        self,
        api_key: str,
        client: httpx.AsyncClient | None = None,
        cache: Cache | None = None,
        quota: YouTubeQuota | None = None,
        cache_ttl: float = 6 * 3600,
        comment_videos: int = 5,
        comments_per_video: int = 20,
    ) -> None:
        self.api_key = api_key
        self.client = client or httpx.AsyncClient(timeout=15)
        self.cache = cache or MemoryTTLCache()
        self.quota = quota or YouTubeQuota()
        self.cache_ttl = cache_ttl
        self.comment_videos = comment_videos
        self.comments_per_video = comments_per_video

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def _get(self, path: str, params: dict) -> dict:
        cache_key = f"yt:{path}:{json.dumps(params, sort_keys=True)}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        self.quota.charge(path)
        response = await self.client.get(f"{BASE}/{path}", params={**params, "key": self.api_key})
        response.raise_for_status()
        data = response.json()
        self.cache.set(cache_key, data, self.cache_ttl)
        return data

    async def collect(self, query: str, limit: int = 25) -> list[RawItem]:
        search = await self._get(
            "search",
            {"part": "snippet", "q": query, "type": "video", "order": "relevance", "maxResults": min(limit, 50)},
        )
        ids = [i["id"]["videoId"] for i in search.get("items", []) if i.get("id", {}).get("videoId")]
        if not ids:
            return []
        rank = {vid: n + 1 for n, vid in enumerate(ids)}
        details = await self._get(
            "videos", {"part": "snippet,statistics,contentDetails", "id": ",".join(ids)}
        )
        items: list[RawItem] = []
        for v in details.get("items", []):
            snip, stats = v.get("snippet", {}), v.get("statistics", {})
            items.append(
                RawItem(
                    source="youtube",
                    external_id=f"video:{v['id']}",
                    title=snip.get("title", ""),
                    content=snip.get("description", ""),
                    url=f"https://www.youtube.com/watch?v={v['id']}",
                    created_at=_parse_time(snip["publishedAt"]),
                    engagement={
                        "views": float(stats.get("viewCount", 0)),
                        "likes": float(stats.get("likeCount", 0)),
                        "comments": float(stats.get("commentCount", 0)),
                    },
                    metadata={
                        "kind": "video",
                        "channel_id": snip.get("channelId"),
                        "channel": snip.get("channelTitle"),
                        "category_id": snip.get("categoryId"),
                        "duration_seconds": _iso_duration_seconds(v.get("contentDetails", {}).get("duration", "")),
                        "search_rank": rank.get(v["id"]),
                        "query": query,
                    },
                )
            )
        commented = sorted(items, key=lambda i: i.engagement.get("comments", 0), reverse=True)
        for video in commented[: self.comment_videos]:
            items.extend(await self._comments(video, query))
        return items

    async def _comments(self, video: RawItem, query: str) -> list[RawItem]:
        video_id = video.external_id.split(":", 1)[1]
        if self.cache.get(f"yt:nocomments:{video_id}"):
            return []  # comments were disabled last time; do not spend quota re-asking
        try:
            data = await self._get(
                "commentThreads",
                {
                    "part": "snippet",
                    "videoId": video_id,
                    "order": "relevance",
                    "maxResults": self.comments_per_video,
                    "textFormat": "plainText",
                },
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (403, 404):  # comments disabled or video gone
                self.cache.set(f"yt:nocomments:{video_id}", True, self.cache_ttl)
                return []
            raise
        out: list[RawItem] = []
        for thread in data.get("items", []):
            top = thread["snippet"]["topLevelComment"]
            s = top["snippet"]
            out.append(
                RawItem(
                    source="youtube",
                    external_id=f"comment:{top['id']}",
                    title=video.title,
                    content=s.get("textDisplay", ""),
                    url=f"{video.url}&lc={top['id']}",
                    created_at=_parse_time(s["publishedAt"]),
                    engagement={"likes": float(s.get("likeCount", 0)), "replies": float(thread["snippet"].get("totalReplyCount", 0))},
                    metadata={"kind": "comment", "video_id": video_id, "author_key": s.get("authorChannelId", {}).get("value"), "query": query},
                )
            )
        return out
