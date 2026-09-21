import httpx
import pytest

from app.collectors.reddit import RedditCollector
from app.collectors.rss import RSSCollector
from app.collectors.youtube import QuotaExceeded, YouTubeCollector, YouTubeQuota
from app.providers.base import SourceProvider, collect_all
from app.schemas.signals import RawItem


def yt_transport(calls: list):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path.rsplit("/", 1)[-1]
        calls.append(path)
        if path == "search":
            return httpx.Response(200, json={"items": [{"id": {"videoId": "v1"}}, {"id": {"videoId": "v2"}}]})
        if path == "videos":
            return httpx.Response(200, json={"items": [
                {"id": "v1", "snippet": {"title": "Deploy tutorial", "description": "d", "publishedAt": "2026-09-01T10:00:00Z", "channelId": "c1", "channelTitle": "C1", "categoryId": "28"},
                 "statistics": {"viewCount": "1000", "likeCount": "50", "commentCount": "12"}, "contentDetails": {"duration": "PT12M30S"}},
                {"id": "v2", "snippet": {"title": "Other", "description": "", "publishedAt": "2026-09-02T10:00:00Z"}, "statistics": {"viewCount": "5"}, "contentDetails": {"duration": "PT45S"}},
            ]})
        if path == "commentThreads":
            if request.url.params["videoId"] == "v2":
                return httpx.Response(403, json={"error": {"errors": [{"reason": "commentsDisabled"}]}})
            return httpx.Response(200, json={"items": [{"snippet": {"totalReplyCount": 2, "topLevelComment": {"id": "cm1", "snippet": {
                "textDisplay": "Where does this run when my laptop is off?", "publishedAt": "2026-09-03T10:00:00Z", "likeCount": 9, "authorChannelId": {"value": "a1"}}}}}]})
        return httpx.Response(404)
    return httpx.MockTransport(handler)


async def test_youtube_collects_videos_and_comments_and_survives_disabled_comments():
    calls: list[str] = []
    c = YouTubeCollector("KEY", client=httpx.AsyncClient(transport=yt_transport(calls)))
    items = await c.collect("deploy ai agent")
    kinds = sorted(i.metadata["kind"] for i in items)
    assert kinds == ["comment", "video", "video"]
    video = next(i for i in items if i.external_id == "video:v1")
    assert video.metadata["duration_seconds"] == 750 and video.metadata["search_rank"] == 1 and video.engagement["views"] == 1000


async def test_youtube_caches_identical_requests_and_tracks_quota():
    calls: list[str] = []
    quota = YouTubeQuota(daily_budget=1000)
    c = YouTubeCollector("KEY", client=httpx.AsyncClient(transport=yt_transport(calls)), quota=quota)
    await c.collect("q")
    first = len(calls)
    await c.collect("q")
    assert len(calls) == first  # second run served entirely from cache
    assert quota.used == 100 + 1 + 2


async def test_youtube_stops_at_quota_budget():
    c = YouTubeCollector("KEY", client=httpx.AsyncClient(transport=yt_transport([])), quota=YouTubeQuota(daily_budget=50))
    with pytest.raises(QuotaExceeded):
        await c.collect("q")


async def test_reddit_auth_search_and_comments():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("access_token"):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        assert request.headers["authorization"] == "bearer tok"
        assert "idea-test" in request.headers["user-agent"]
        if request.url.path == "/search":
            return httpx.Response(200, json={"data": {"children": [{"kind": "t3", "data": {"id": "p1", "title": "Deploy help?", "selftext": "", "permalink": "/r/x/p1", "created_utc": 1789900000, "score": 10, "num_comments": 3, "upvote_ratio": 0.9, "subreddit": "x", "author": "u1"}}]}})
        return httpx.Response(200, json=[{}, {"data": {"children": [{"kind": "t1", "data": {"id": "c1", "body": "Still confused about hosting", "permalink": "/r/x/p1/c1", "created_utc": 1789900100, "score": 4, "author": "u2"}}]}}])

    c = RedditCollector("id", "secret", "idea-test/0.1", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    items = await c.collect("deploy")
    assert [i.metadata["kind"] for i in items] == ["post", "comment"]


def test_rss_parses_rss_and_atom_and_filters():
    rss = "<rss><channel><item><title>How to host an agent</title><description>guide</description><link>https://a.test/1</link><guid>1</guid><pubDate>Mon, 14 Sep 2026 10:00:00 GMT</pubDate></item><item><title>Cooking</title><link>https://a.test/2</link></item></channel></rss>"
    assert [i.title for i in RSSCollector.parse(rss, "f", "agent")] == ["How to host an agent"]
    atom = '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x</id><title>Agent hosting</title><link href="https://a.test/3"/><updated>2026-09-10T10:00:00Z</updated></entry></feed>'
    assert RSSCollector.parse(atom, "f")[0].url == "https://a.test/3"


class Good(SourceProvider):
    name = "good"
    def is_configured(self): return True
    async def collect(self, query, limit=25):
        return [RawItem(source="good", external_id="1", title="t", url="u", created_at="2026-09-01T00:00:00Z")]


class Broken(Good):
    name = "broken"
    async def collect(self, query, limit=25):
        raise RuntimeError("quota exhausted")


class Off(Good):
    name = "off"
    def is_configured(self): return False


async def test_one_failing_provider_never_blocks_the_others():
    result = await collect_all([Broken(), Good(), Off()], "q")
    assert len(result.items) == 1
    assert "broken" in result.errors and result.skipped == ["off"]
