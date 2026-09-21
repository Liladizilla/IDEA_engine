"""Common schema every collector emits (spec section 39) plus extracted-question records."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    QUESTION = "QUESTION"
    PROBLEM = "PROBLEM"
    COMPLAINT = "COMPLAINT"
    REQUEST = "REQUEST"
    TUTORIAL_REQUEST = "TUTORIAL_REQUEST"
    COMPARISON = "COMPARISON"
    PURCHASE_INTENT = "PURCHASE_INTENT"
    OPINION = "OPINION"
    NEWS = "NEWS"
    DISCUSSION = "DISCUSSION"
    EXPERIENCE = "EXPERIENCE"
    OTHER = "OTHER"


class RawItem(BaseModel):
    source: str
    external_id: str
    title: str
    content: str = ""
    url: str
    created_at: datetime
    engagement: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.content}".strip()


class ExtractedQuestion(BaseModel):
    question: str
    source: str
    item_id: str
    created_at: datetime
    signal_type: SignalType = SignalType.QUESTION
    problem: str | None = None
    audience: str | None = None
    intent: str | None = None
    author_key: str | None = None
    engagement: float = 0.0
    dissatisfied: bool = False
