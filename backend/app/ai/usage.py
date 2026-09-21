"""Cost control (spec section 44). A runaway worker must hit a limit, not your card."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone

from app.ai.base import AIProvider, AIResult


class BudgetExceeded(RuntimeError):
    def __init__(self, scope: str, limit: float):
        super().__init__(f"AI {scope} limit reached ({limit:g})")
        self.scope = scope


@dataclass
class Limits:
    daily_tokens_global: int = 500_000
    daily_tokens_per_user: int = 40_000
    monthly_cost_usd: float = 25.0
    daily_requests_per_provider: dict[str, int] | None = None


@dataclass
class UsageRecord:
    user_id: str | None
    provider: str
    model: str
    operation: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    at: datetime


class AIUsageService:
    """In-memory ledger. Persist `records` to the provider_usage table in production; the checks stay the same."""

    def __init__(self, limits: Limits | None = None, price_per_1k_tokens: dict[str, float] | None = None):
        self.limits = limits or Limits()
        self.prices = price_per_1k_tokens or {}
        self.records: list[UsageRecord] = []

    def _today(self, r: UsageRecord) -> bool:
        return r.at.date() == date.today()

    def check(self, user_id: str | None, provider: str, estimated_tokens: int = 0) -> None:
        today = [r for r in self.records if self._today(r)]
        total = sum(r.input_tokens + r.output_tokens for r in today)
        if total + estimated_tokens > self.limits.daily_tokens_global:
            raise BudgetExceeded("daily global token", self.limits.daily_tokens_global)
        if user_id is not None:
            mine = sum(r.input_tokens + r.output_tokens for r in today if r.user_id == user_id)
            if mine + estimated_tokens > self.limits.daily_tokens_per_user:
                raise BudgetExceeded("daily per-user token", self.limits.daily_tokens_per_user)
        month = sum(r.cost_usd for r in self.records if r.at.year == date.today().year and r.at.month == date.today().month)
        if month >= self.limits.monthly_cost_usd:
            raise BudgetExceeded("monthly cost", self.limits.monthly_cost_usd)
        caps = self.limits.daily_requests_per_provider or {}
        if provider in caps and sum(1 for r in today if r.provider == provider) >= caps[provider]:
            raise BudgetExceeded(f"{provider} daily request", caps[provider])

    def record(self, user_id: str | None, provider: str, model: str, operation: str, input_tokens: int, output_tokens: int) -> UsageRecord:
        cost = (input_tokens + output_tokens) / 1000 * self.prices.get(model, 0.0)
        rec = UsageRecord(user_id, provider, model, operation, input_tokens, output_tokens, cost, datetime.now(timezone.utc))
        self.records.append(rec)
        return rec


class MeteredAIProvider(AIProvider):
    """Wrap any provider so every call is limit-checked and recorded."""

    def __init__(self, inner: AIProvider, usage: AIUsageService, user_id: str | None = None):
        self.inner, self.usage, self.user_id = inner, usage, user_id
        self.name = inner.name
        self.chat_model, self.embedding_model = inner.chat_model, inner.embedding_model

    async def generate(self, system: str, user: str, *, json_mode: bool = False, max_tokens: int = 1024) -> AIResult:
        estimate = (len(system) + len(user)) // 4 + max_tokens
        self.usage.check(self.user_id, self.inner.name, estimate)
        r = await self.inner.generate(system, user, json_mode=json_mode, max_tokens=max_tokens)
        self.usage.record(self.user_id, self.inner.name, r.model or self.chat_model, "generate", r.input_tokens, r.output_tokens)
        return r

    async def embed(self, texts: list[str]) -> list[list[float]]:
        estimate = sum(len(t) for t in texts) // 4
        self.usage.check(self.user_id, self.inner.name, estimate)
        out = await self.inner.embed(texts)
        self.usage.record(self.user_id, self.inner.name, self.embedding_model, "embed", estimate, 0)
        return out
