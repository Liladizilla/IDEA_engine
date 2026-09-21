"""Tiny TTL cache. Swap for Redis by implementing the same two methods."""
import time
from typing import Any, Protocol


class Cache(Protocol):
    def get(self, key: str) -> Any | None: ...
    def set(self, key: str, value: Any, ttl: float) -> None: ...


class MemoryTTLCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        hit = self._data.get(key)
        if hit is None:
            return None
        expires, value = hit
        if expires < time.monotonic():
            del self._data[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        self._data[key] = (time.monotonic() + ttl, value)
