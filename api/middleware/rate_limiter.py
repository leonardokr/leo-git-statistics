"""Rate limiting middleware using slowapi."""

import os

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse


def _key_func(request: Request) -> str:
    """Build a rate-limit key from the API key or client IP.

    Authenticated requests are keyed by API key so they share a higher
    limit pool.  Anonymous requests fall back to the remote IP address.

    :param request: The incoming request.
    :returns: A string key for the rate limiter.
    :rtype: str
    """
    if getattr(request.state, "authenticated", False):
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            return f"key:{auth[7:]}"
    return get_remote_address(request)


DEFAULT_LIMIT = os.getenv("RATE_LIMIT_DEFAULT", "30/minute")
AUTH_LIMIT = os.getenv("RATE_LIMIT_AUTH", "100/minute")
HEAVY_LIMIT = os.getenv("RATE_LIMIT_HEAVY", "10/minute")

limiter = Limiter(key_func=_key_func)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Return a 429 response with standard rate-limit headers.

    :param request: The incoming request.
    :param exc: The rate limit exception.
    :returns: JSON response with error details.
    :rtype: Response
    """
    response = JSONResponse(
        status_code=429,
        content={"error": "Too many requests", "detail": str(exc.detail)},
    )
    response.headers["Retry-After"] = str(exc.detail)
    return response
