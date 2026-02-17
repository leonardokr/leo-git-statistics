"""In-memory TTL cache for API responses.

Provides a shared cache instance to avoid redundant GitHub API calls
when multiple requests ask for the same user data within a short window.
"""

from typing import Any, Optional, Tuple

from cachetools import TTLCache

_cache: TTLCache = TTLCache(maxsize=100, ttl=300)


def cache_get(username: str, endpoint: str) -> Tuple[bool, Optional[Any]]:
    """Retrieve a cached response.

    :param username: GitHub username used as part of the cache key.
    :param endpoint: Endpoint name used as part of the cache key.
    :returns: Tuple of (hit, value). hit is True when a cached value exists.
    :rtype: tuple[bool, Any | None]
    """
    key = (username, endpoint)
    value = _cache.get(key)
    if value is not None:
        return True, value
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
    _cache.clear()
