"""RSS/Atom collector for public feeds. `query` filters entries by keyword."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

from app.providers.base import SourceProvider
from app.schemas.signals import RawItem

ATOM = "{http://www.w3.org/2005/Atom}"


def _when(text: str | None) -> datetime:
    if not text:
        return datetime.now(timezone.utc)
    try:
        return parsedate_to_datetime(text).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


class RSSCollector(SourceProvider):
    name = "rss"

    def __init__(self, feed_urls: list[str], client: httpx.AsyncClient | None = None) -> None:
        self.feed_urls = feed_urls
        self.client = client or httpx.AsyncClient(timeout=15, follow_redirects=True)

    def is_configured(self) -> bool:
        return bool(self.feed_urls)

    async def collect(self, query: str, limit: int = 25) -> list[RawItem]:
        needle = query.lower()
        out: list[RawItem] = []
        for url in self.feed_urls:
            r = await self.client.get(url)
            r.raise_for_status()
            out.extend(self.parse(r.text, url, needle))
        return out[:limit]

    @staticmethod
    def parse(xml_text: str, feed_url: str, needle: str = "") -> list[RawItem]:
        root = ET.fromstring(xml_text)
        items: list[RawItem] = []
        for node in root.iter("item"):
            title = (node.findtext("title") or "").strip()
            body = (node.findtext("description") or "").strip()
            link = (node.findtext("link") or feed_url).strip()
            guid = (node.findtext("guid") or link).strip()
            stamp = node.findtext("pubDate")
            items.append((guid, title, body, link, stamp))
        for node in root.iter(f"{ATOM}entry"):
            link_node = node.find(f"{ATOM}link")
            link = link_node.get("href") if link_node is not None else feed_url
            items.append(
                (
                    (node.findtext(f"{ATOM}id") or link).strip(),
                    (node.findtext(f"{ATOM}title") or "").strip(),
                    (node.findtext(f"{ATOM}summary") or "").strip(),
                    link,
                    node.findtext(f"{ATOM}updated"),
                )
            )
        return [
            RawItem(source="rss", external_id=g, title=t, content=b, url=l, created_at=_when(s), metadata={"kind": "article", "feed": feed_url})
            for g, t, b, l, s in items
            if not needle or needle in f"{t} {b}".lower()
        ]
