"""
Utility decorators for the git-statistics project.
"""

from functools import wraps
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


def lazy_async_property(cache_attr: str, loader_method: str):
    """
    Decorator for async methods that cache their result.

    This decorator eliminates the repetitive pattern of:
        if self._cached_value is not None:
            return self._cached_value
        await self.loader_method()
        return self._cached_value or default

    :param cache_attr: Name of the instance attribute to cache the value (e.g., "_stargazers").
    :param loader_method: Name of the async method to call if cache is empty (e.g., "get_stats").

    Example usage:
        @lazy_async_property("_stargazers", "get_stats")
        async def get_stargazers(self, default: int = 0) -> int:
            return default
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            cached = getattr(self, cache_attr, None)
            if cached is not None:
                return cached

            loader = getattr(self, loader_method)
            await loader()

            cached = getattr(self, cache_attr, None)
            if cached is not None:
                return cached

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator
