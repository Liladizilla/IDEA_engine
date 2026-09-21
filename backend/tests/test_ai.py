import httpx
import pytest

from app.ai.base import AIParseError, AIProvider, AIResult, parse_json
from app.ai.ideas import IdeaBatch, generate_ideas
from app.ai.providers import HuggingFaceProvider, OpenAICompatibleProvider
from app.ai.usage import AIUsageService, BudgetExceeded, Limits, MeteredAIProvider
from app.intelligence.scoring import InsufficientSignal


class Fake(AIProvider):
    name = "fake"
    def __init__(self, text="{}"): self.text, self.calls = text, 0
    async def generate(self, system, user, *, json_mode=False, max_tokens=1024):
        self.calls += 1
        return AIResult(self.text, 100, 50, "fake-1")
    async def embed(self, texts): return [[0.0] for _ in texts]


def test_parse_json_handles_fences_and_prose():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Sure! {"a": 1} hope that helps') == {"a": 1}


def test_parse_json_refuses_garbage():
    with pytest.raises(AIParseError):
        parse_json("I cannot help with that")


IDEA = {"title": "t", "hook": "h", "audience": "a", "core_question": "q", "problem": "p", "content_angle": "c", "format": "youtube_long", "difficulty": "easy", "why_now": "w", "evidence_summary": "e"}


async def test_ideas_refuse_to_run_without_evidence():
    p = Fake()
    out = await generate_ideas(p, [{"source": "reddit", "text": "one"}])
    assert isinstance(out, InsufficientSignal) and p.calls == 0  # no AI call, nothing invented


async def test_ideas_parse_structured_output():
    import json
    p = Fake(json.dumps({"ideas": [IDEA]}))
    out = await generate_ideas(p, [{"source": "reddit", "text": str(i)} for i in range(4)])
    assert isinstance(out, IdeaBatch) and out.ideas[0].format == "youtube_long"


async def test_malformed_ideas_raise_instead_of_being_patched():
    p = Fake('{"ideas": [{"title": "only a title"}]}')
    with pytest.raises(AIParseError):
        await generate_ideas(p, [{"source": "reddit", "text": str(i)} for i in range(4)])


async def test_classify_falls_back_to_other():
    assert await Fake('{"label": "NONSENSE"}').classify("x", ["QUESTION", "OTHER"]) == "OTHER"
    assert await Fake('{"label": "question"}').classify("x", ["QUESTION", "OTHER"]) == "QUESTION"


async def test_usage_limits_stop_a_runaway_worker():
    usage = AIUsageService(Limits(daily_tokens_global=2000, daily_tokens_per_user=100000))
    metered = MeteredAIProvider(Fake(), usage, user_id="worker")
    with pytest.raises(BudgetExceeded):
        for _ in range(50):
            await metered.generate("s", "u", max_tokens=200)
    assert 0 < len(usage.records) < 50


async def test_per_user_limit_is_independent():
    usage = AIUsageService(Limits(daily_tokens_global=10**9, daily_tokens_per_user=400))
    a, b = MeteredAIProvider(Fake(), usage, "a"), MeteredAIProvider(Fake(), usage, "b")
    await a.generate("s", "u", max_tokens=100)
    with pytest.raises(BudgetExceeded):
        await a.generate("s", "u", max_tokens=400)
    await b.generate("s", "u", max_tokens=100)


async def test_monthly_cost_limit():
    usage = AIUsageService(Limits(monthly_cost_usd=0.01), price_per_1k_tokens={"fake-1": 1.0})
    m = MeteredAIProvider(Fake(), usage)
    await m.generate("s", "u", max_tokens=10)
    with pytest.raises(BudgetExceeded):
        await m.generate("s", "u", max_tokens=10)


async def test_openai_compatible_and_hf_share_one_wire_format():
    seen = {}
    def handler(req: httpx.Request):
        seen["url"], seen["auth"] = str(req.url), req.headers.get("authorization")
        return httpx.Response(200, json={"model": "m", "choices": [{"message": {"content": "hi"}}], "usage": {"prompt_tokens": 3, "completion_tokens": 2}})
    hf = HuggingFaceProvider("hf_x", "chat-model", "embed-model", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    r = await hf.generate("s", "u")
    assert (r.text, r.input_tokens, r.output_tokens) == ("hi", 3, 2)
    assert seen["url"] == "https://router.huggingface.co/v1/chat/completions" and seen["auth"] == "Bearer hf_x"
    oa = OpenAICompatibleProvider("http://localhost:11434/v1/", "", "llama", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    await oa.generate("s", "u")
    assert seen["url"] == "http://localhost:11434/v1/chat/completions" and seen["auth"] is None
