"""Trend and question-suggestion collectors. Both are optional; failures never block the pipeline."""
from __future__ import annotations

from app.providers.base import ProviderNotConfigured, SourceProvider, TrendPoint, TrendProvider
from app.schemas.signals import RawItem


class TrendCollector:
    """Fans out to every configured TrendProvider and returns whichever ones answered."""

    def __init__(self, providers: list[TrendProvider]) -> None:
        self.providers = providers

    async def interest(self, term: str, days: int = 30) -> dict[str, list[TrendPoint]]:
        out: dict[str, list[TrendPoint]] = {}
        for p in self.providers:
            if not p.is_configured():
                continue
            try:
                out[p.name] = await p.interest_over_time(term, days)
            except Exception:  # noqa: BLE001
                continue
        return out


class GoogleTrendsProvider(TrendProvider):
    """Placeholder. Google's Trends API access is limited; implement against whichever access you get.
    https://developers.google.com/search/apis/trends"""

    name = "google_trends"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def interest_over_time(self, term: str, days: int = 30) -> list[TrendPoint]:
        raise ProviderNotConfigured("GoogleTrendsProvider is not implemented yet")


class AnswerThePublicCollector(SourceProvider):
    """Optional question-discovery provider. Implement once you have API access:
    https://answerthepublic.zendesk.com/hc/en-us/articles/15219088022555"""

    name = "answerthepublic"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def collect(self, query: str, limit: int = 25) -> list[RawItem]:
        raise ProviderNotConfigured("AnswerThePublicCollector is not implemented yet")
