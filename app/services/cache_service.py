import time
from dataclasses import dataclass
from typing import Any


CACHE_TTL_SECONDS = 300


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


_cache: dict[str, CacheEntry] = {}


async def get_cached(key: str) -> Any | None:
    entry = _cache.get(key)

    if entry is None:
        return None

    if time.time() >= entry.expires_at:
        del _cache[key]
        return None

    return entry.value


async def set_cached(
    key: str,
    value: Any,
    ttl_seconds: int = CACHE_TTL_SECONDS,
) -> None:
    _cache[key] = CacheEntry(
        value=value,
        expires_at=time.time() + ttl_seconds,
    )