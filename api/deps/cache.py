"""In-memory TTL cache for API responses.

Provides a shared cache instance to avoid redundant GitHub API calls
when multiple requests ask for the same user data within a short window.
"""

from typing import Any, Optional, Tuple

import structlog
from cachetools import TTLCache

_cache: TTLCache = TTLCache(maxsize=100, ttl=300)
_hits: int = 0
_misses: int = 0

log = structlog.get_logger("api.cache")


def _increment_prometheus_hit() -> None:
    try:
        from api.middleware.metrics import cache_hits
        cache_hits.inc()
    except Exception:
        pass


def _increment_prometheus_miss() -> None:
    try:
        from api.middleware.metrics import cache_misses
        cache_misses.inc()
    except Exception:
        pass


def cache_get(username: str, endpoint: str) -> Tuple[bool, Optional[Any]]:
    """Retrieve a cached response.

    :param username: GitHub username used as part of the cache key.
    :param endpoint: Endpoint name used as part of the cache key.
    :returns: Tuple of (hit, value). hit is True when a cached value exists.
    :rtype: tuple[bool, Any | None]
    """
    global _hits, _misses
    key = (username, endpoint)
    value = _cache.get(key)
    if value is not None:
        _hits += 1
        log.debug("cache_hit", username=username, endpoint=endpoint)
        _increment_prometheus_hit()
        return True, value
    _misses += 1
    log.debug("cache_miss", username=username, endpoint=endpoint)
    _increment_prometheus_miss()
    return False, None


def cache_set(username: str, endpoint: str, value: Any) -> None:
    """Store a response in the cache.

    :param username: GitHub username used as part of the cache key.
    :param endpoint: Endpoint name used as part of the cache key.
    :param value: The response data to cache.
    """
    key = (username, endpoint)
    _cache[key] = value


def cache_clear() -> None:
    """Remove all entries from the cache."""
    global _hits, _misses
    _cache.clear()
    _hits = 0
    _misses = 0


def cache_stats() -> dict:
    """Return current cache statistics.

    :returns: Dictionary with entries count, hit and miss totals, and hit ratio.
    :rtype: dict
    """
    total = _hits + _misses
    return {
        "entries": len(_cache),
        "maxsize": _cache.maxsize,
        "hits": _hits,
        "misses": _misses,
        "hit_ratio": round(_hits / total, 2) if total > 0 else 0.0,
    }
