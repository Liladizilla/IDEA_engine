"""AIProvider abstraction (spec section 43). Providers implement `generate` and `embed`; the rest is shared."""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.ai import prompts

T = TypeVar("T", bound=BaseModel)


@dataclass
class AIResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""


class AIParseError(ValueError):
    """The model answered, but not in the requested structure. Never patched up with invented data."""


class AIProvider(ABC):
    name: str
    chat_model: str = ""
    embedding_model: str = ""

    @abstractmethod
    async def generate(self, system: str, user: str, *, json_mode: bool = False, max_tokens: int = 1024) -> AIResult: ...

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    async def classify(self, text: str, labels: list[str]) -> str:
        r = await self.generate(prompts.CLASSIFY_SYSTEM, f"Labels: {labels}\nText: {text}", json_mode=True, max_tokens=50)
        label = str(parse_json(r.text).get("label", "")).upper()
        return label if label in labels else "OTHER"

    async def summarize(self, text: str, max_words: int = 80) -> str:
        r = await self.generate(
            "Summarize the supplied text faithfully in plain language. Add nothing that is not in the text.",
            f"Max {max_words} words.\n\n{text}",
            max_tokens=300,
        )
        return r.text.strip()


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)


def parse_json(text: str) -> dict:
    cleaned = _FENCE.sub("", text.strip())
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise AIParseError("model did not return JSON") from None
        try:
            value = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise AIParseError("model returned malformed JSON") from exc
    if not isinstance(value, dict):
        raise AIParseError("expected a JSON object")
    return value


def parse_model(text: str, model: type[T]) -> T:
    try:
        return model.model_validate(parse_json(text))
    except ValidationError as exc:
        raise AIParseError(f"response did not match {model.__name__}: {exc.error_count()} errors") from exc
