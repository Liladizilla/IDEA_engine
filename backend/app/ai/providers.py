"""Concrete providers. All are replaceable; the intelligence engine only sees AIProvider."""
from __future__ import annotations

import httpx

from app.ai.base import AIProvider, AIResult
from app.core.config import Settings


class OpenAICompatibleProvider(AIProvider):
    """Anything that speaks POST {base_url}/chat/completions (OpenAI, Groq, Together, vLLM, Ollama...)."""

    name = "openai_compatible"

    def __init__(self, base_url: str, api_key: str, chat_model: str, embedding_model: str = "", client: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.client = client or httpx.AsyncClient(timeout=60)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def generate(self, system: str, user: str, *, json_mode: bool = False, max_tokens: int = 1024) -> AIResult:
        body: dict = {
            "model": self.chat_model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        r = await self.client.post(f"{self.base_url}/chat/completions", json=body, headers=self._headers())
        r.raise_for_status()
        data = r.json()
        usage = data.get("usage", {})
        return AIResult(
            text=data["choices"][0]["message"]["content"] or "",
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            model=data.get("model", self.chat_model),
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        r = await self.client.post(
            f"{self.base_url}/embeddings", json={"model": self.embedding_model, "input": texts}, headers=self._headers()
        )
        r.raise_for_status()
        return [row["embedding"] for row in r.json()["data"]]


class HuggingFaceProvider(OpenAICompatibleProvider):
    """Hugging Face Inference Providers. Chat goes through the OpenAI-compatible router; embeddings use the
    feature-extraction task (the router's OpenAI endpoint covers chat only). Free-tier credits are limited:
    treat this as replaceable and keep AIUsageService limits on."""

    name = "huggingface"
    ROUTER = "https://router.huggingface.co/v1"

    def __init__(self, token: str, chat_model: str, embedding_model: str, client: httpx.AsyncClient | None = None):
        super().__init__(self.ROUTER, token, chat_model, embedding_model, client)
        self.token = token

    async def embed(self, texts: list[str]) -> list[list[float]]:
        from huggingface_hub import AsyncInferenceClient  # lazy: only needed when embedding through HF

        hf = AsyncInferenceClient(provider="hf-inference", api_key=self.token)
        out = []
        for text in texts:  # one call per text keeps the return shape unambiguous
            arr = await hf.feature_extraction(text, model=self.embedding_model)
            vec = arr.reshape(-1, arr.shape[-1]).mean(axis=0) if arr.ndim > 1 else arr  # mean-pool if token-level
            out.append([float(x) for x in vec])
        return out


class LocalAIProvider(OpenAICompatibleProvider):
    """Ollama / llama.cpp / vLLM on your own machine. No key, no per-token cost."""

    name = "local"

    def __init__(self, base_url: str, chat_model: str, embedding_model: str = "", client: httpx.AsyncClient | None = None):
        super().__init__(base_url, "", chat_model, embedding_model, client)


def get_ai_provider(s: Settings) -> AIProvider:
    if s.ai_provider == "huggingface":
        return HuggingFaceProvider(s.hf_token, s.hf_chat_model, s.hf_embedding_model)
    if s.ai_provider == "openai_compatible":
        return OpenAICompatibleProvider(s.openai_base_url, s.openai_api_key, s.openai_chat_model)
    if s.ai_provider == "local":
        return LocalAIProvider(s.local_ai_base_url, s.local_ai_chat_model)
    raise ValueError(f"Unknown AI_PROVIDER: {s.ai_provider}")
