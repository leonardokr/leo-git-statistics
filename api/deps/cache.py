"""TTL cache for API responses with Redis or in-memory backend.

When ``REDIS_URL`` is set, values are stored in Redis so that the cache
survives restarts and is shared across gunicorn workers. Otherwise, a
local ``cachetools.TTLCache`` is used as a zero-dependency fallback.
"""

import json
import os
from typing import Any, Optional, Tuple

import structlog
from cachetools import TTLCache

log = structlog.get_logger("api.cache")

_CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
_CACHE_MAXSIZE: int = int(os.getenv("CACHE_MAXSIZE", "100"))
_REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

_hits: int = 0
_misses: int = 0

_local_cache: TTLCache = TTLCache(maxsize=_CACHE_MAXSIZE, ttl=_CACHE_TTL)
_redis = None


def _get_redis():
    """Return a lazy-initialized Redis client or None.

    :returns: Redis client instance, or None when unavailable.
    """
    global _redis
    if _redis is not None:
        return _redis
    if not _REDIS_URL:
        return None
    try:
        import redis
        _redis = redis.from_url(_REDIS_URL, decode_responses=True)
        _redis.ping()
        log.info("redis_connected", url=_REDIS_URL)
        return _redis
    except Exception as exc:
        log.warning("redis_unavailable_falling_back_to_memory", error=str(exc))
        return None


def _make_key(username: str, endpoint: str) -> str:
    """Build a string cache key.

    :param username: GitHub username.
    :param endpoint: Endpoint name.
    :returns: Cache key string.
    :rtype: str
    """
    return f"cache:{username}:{endpoint}"


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
    r = _get_redis()
    if r is not None:
        key = _make_key(username, endpoint)
        try:
            raw = r.get(key)
            if raw is not None:
                _hits += 1
                log.debug("cache_hit", username=username, endpoint=endpoint, backend="redis")
                _increment_prometheus_hit()
                return True, json.loads(raw)
        except Exception as exc:
            log.warning("redis_get_error", error=str(exc))

        _misses += 1
        log.debug("cache_miss", username=username, endpoint=endpoint, backend="redis")
        _increment_prometheus_miss()
        return False, None

    local_key = (username, endpoint)
    value = _local_cache.get(local_key)
    if value is not None:
        _hits += 1
        log.debug("cache_hit", username=username, endpoint=endpoint, backend="memory")
        _increment_prometheus_hit()
        return True, value
    _misses += 1
    log.debug("cache_miss", username=username, endpoint=endpoint, backend="memory")
    _increment_prometheus_miss()
    return False, None


def cache_set(username: str, endpoint: str, value: Any) -> None:
    """Store a response in the cache.

    :param username: GitHub username used as part of the cache key.
    :param endpoint: Endpoint name used as part of the cache key.
    :param value: The response data to cache.
    """
    r = _get_redis()
    if r is not None:
        key = _make_key(username, endpoint)
        try:
            r.setex(key, _CACHE_TTL, json.dumps(value, default=str))
            return
        except Exception as exc:
            log.warning("redis_set_error", error=str(exc))

    _local_cache[(username, endpoint)] = value


def cache_clear() -> None:
    """Remove all entries from the cache."""
    global _hits, _misses
    r = _get_redis()
    if r is not None:
        try:
            cursor = "0"
            while cursor != 0:
                cursor, keys = r.scan(cursor=cursor, match="cache:*", count=100)
                if keys:
                    r.delete(*keys)
        except Exception as exc:
            log.warning("redis_clear_error", error=str(exc))

    _local_cache.clear()
    _hits = 0
    _misses = 0


def cache_stats() -> dict:
    """Return current cache statistics.

    :returns: Dictionary with entries count, hit and miss totals, hit ratio,
              and the active backend name.
    :rtype: dict
    """
    total = _hits + _misses
    r = _get_redis()

    if r is not None:
        try:
            cursor, keys = r.scan(cursor=0, match="cache:*", count=1000)
            entries = len(keys)
            while cursor != 0:
                cursor, batch = r.scan(cursor=cursor, match="cache:*", count=1000)
                entries += len(batch)
        except Exception:
            entries = -1

        return {
            "backend": "redis",
            "entries": entries,
            "hits": _hits,
            "misses": _misses,
            "hit_ratio": round(_hits / total, 2) if total > 0 else 0.0,
        }

    return {
        "backend": "memory",
        "entries": len(_local_cache),
        "maxsize": _local_cache.maxsize,
        "hits": _hits,
        "misses": _misses,
        "hit_ratio": round(_hits / total, 2) if total > 0 else 0.0,
    }
