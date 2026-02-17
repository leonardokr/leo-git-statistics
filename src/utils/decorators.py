"""Utility decorators for the git-statistics project."""

from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def _resolve_dotted_attr(obj: Any, dotted_path: str) -> Any:
    """Resolve a dotted attribute path on an object.

    :param obj: Root object to start resolution from.
    :param dotted_path: Dot-separated attribute path (e.g., ``_repo_stats.name``).
    :returns: The resolved attribute value, or ``None`` if any segment is missing.
    """
    for part in dotted_path.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


def lazy_async_property(cache_attr: str, loader_method: str):
    """Decorator for async methods that cache their result.

    Eliminates the repetitive check-None / call-loader / return-or-default
    pattern. Supports dotted ``cache_attr`` paths for attributes on
    sub-objects (e.g., ``_repo_stats.name``).

    When the cached value is still ``None`` after calling the loader, the
    decorated function body executes and its return value is used as default.

    :param cache_attr: Attribute path to read the cached value from
        (e.g., ``"_stargazers"`` or ``"_repo_stats.stargazers"``).
    :param loader_method: Name of the async method on ``self`` to populate
        the cache (e.g., ``"get_stats"``).

    Example usage::

        @lazy_async_property("_repo_stats.stargazers", "get_stats")
        async def get_stargazers(self) -> int:
            return 0
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            cached = _resolve_dotted_attr(self, cache_attr)
            if cached is not None:
                return cached

            loader = getattr(self, loader_method)
            await loader()

            cached = _resolve_dotted_attr(self, cache_attr)
            if cached is not None:
                return cached

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator
