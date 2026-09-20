from time import monotonic
from typing import Any
from app.core.config import CACHE_TTL_SECONDS
_cache: dict[str, tuple[float, Any]] = {}

def get(key: str):
    item = _cache.get(key)
    if not item: return None
    if monotonic() - item[0] > CACHE_TTL_SECONDS:
        _cache.pop(key, None); return None
    return item[1]

def set(key: str, value: Any): _cache[key] = (monotonic(), value); return value

def clear(): _cache.clear()
