"""Embedder interface plus a deterministic hashing embedder.

HashingEmbedder is for tests and offline development ONLY. It matches shared word stems, not meaning.
Production clustering uses AIProvider.embed() (real embeddings stored in pgvector).
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

_STOP = set(
    "a an the and or but if of to in on for with without at by from as is are was were be been i me my we you your it its "
    "this that these those do does did can could would should will just so than then there here how what why when where which "
    "who whom any anyone someone way get got have has had not no yes very really".split()
)
_SUFFIXES = ("ingly", "edly", "ing", "est", "ers", "ies", "ed", "ly", "er", "es", "s")


def stem(word: str) -> str:
    for suf in _SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)]
    return word


def tokens(text: str) -> list[str]:
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower().replace("'", "")) if w not in _STOP]


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashingEmbedder:
    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in tokens(text):
            h = int.from_bytes(hashlib.md5(tok.encode()).digest()[:8], "big")
            vec[h % self.dim] += 1.0 if (h >> 63) & 1 else -1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
