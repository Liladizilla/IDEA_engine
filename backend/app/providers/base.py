"""Provider interfaces. Nothing in the intelligence engine imports a concrete provider."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date

from app.schemas.signals import RawItem


class ProviderNotConfigured(RuntimeError):
    pass


class SourceProvider(ABC):
    """A place we can read public questions from (YouTube, Reddit, RSS...)."""

    name: str

    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    async def collect(self, query: str, limit: int = 25) -> list[RawItem]: ...


@dataclass
class TrendPoint:
    day: date
    value: float


class TrendProvider(ABC):
    """Interest-over-time for a term. Google Trends is one implementation, never a dependency."""

    name: str

    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    async def interest_over_time(self, term: str, days: int = 30) -> list[TrendPoint]: ...


@dataclass
class CollectionResult:
    items: list[RawItem] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)


async def collect_all(providers: list[SourceProvider], query: str, limit: int = 25) -> CollectionResult:
    """Run every configured provider; one failing provider never blocks the others."""
    result = CollectionResult()
    for provider in providers:
        if not provider.is_configured():
            result.skipped.append(provider.name)
            continue
        try:
            result.items.extend(await provider.collect(query, limit))
        except Exception as exc:  # noqa: BLE001 - isolate provider failures by design
            result.errors[provider.name] = f"{type(exc).__name__}: {exc}"
    return result
