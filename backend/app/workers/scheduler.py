"""MVP scheduler: APScheduler in one process. Move to Celery + Redis when you need multiple workers.
Run:  python -m app.workers.scheduler
"""
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.ai.providers import get_ai_provider
from app.collectors.reddit import RedditCollector
from app.collectors.rss import RSSCollector
from app.collectors.youtube import YouTubeCollector
from app.core.config import get_settings
from app.workers.jobs import run_collection_cycle
from app.repositories.pipeline_repo import run_persist_cycle

SEED_QUERIES = ["ai automation small business", "deploy ai agent cheap"]

DEFAULT_RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://www.producthunt.com/feed",
    "https://news.ycombinator.com/rss",
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
]


async def cycle() -> None:
    s = get_settings()
    providers = [
        YouTubeCollector(s.youtube_api_key),
    ]
    if s.reddit_client_id and s.reddit_client_secret:
        providers.append(RedditCollector(s.reddit_client_id, s.reddit_client_secret, s.reddit_user_agent))
    if s.rss_feed_urls:
        feeds = [u.strip() for u in s.rss_feed_urls.split(",") if u.strip()]
    else:
        feeds = DEFAULT_RSS_FEEDS
    providers.append(RSSCollector(feeds))

    ai_provider = get_ai_provider(s) if (s.hf_token or s.openai_api_key) else None

    output, collected = await run_collection_cycle(providers, ai_provider, SEED_QUERIES)
    print(f"items={len(collected.items)} errors={collected.errors} skipped={collected.skipped} opportunities={len(output.candidates)}")

    if output.candidates:
        await run_persist_cycle(output, collected.items)
        print("Persisted to database")


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cycle, "interval", hours=6, next_run_time=None)
    scheduler.start()
    await cycle()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())