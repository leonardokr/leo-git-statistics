"""Health check endpoint with real subsystem probes."""

import time
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.deps.cache import cache_stats
from api.models.responses import CacheHealth, GitHubApiHealth, HealthResponse
from src.core.github_client import github_breaker, rate_limit_state

router = APIRouter(tags=["Health"])

_start_time: float = time.monotonic()


def _circuit_breaker_label() -> str:
    """Return the human-readable circuit breaker state.

    :returns: One of 'closed', 'half-open', or 'open'.
    :rtype: str
    """
    return str(github_breaker.current_state)


def _github_api_health() -> GitHubApiHealth:
    """Build the GitHub API health payload from current rate limit state.

    :returns: GitHub API health information.
    :rtype: GitHubApiHealth
    """
    reset_iso = None
    if rate_limit_state.reset is not None:
        reset_iso = datetime.fromtimestamp(
            rate_limit_state.reset, tz=timezone.utc
        ).isoformat()

    remaining = rate_limit_state.remaining
    if remaining is None:
        status = "unknown"
    elif remaining > 100:
        status = "connected"
    elif remaining > 10:
        status = "degraded"
    else:
        status = "critical"

    return GitHubApiHealth(
        status=status,
        rate_limit_remaining=remaining,
        rate_limit_limit=rate_limit_state.limit,
        rate_limit_reset=reset_iso,
    )


def _overall_status(github: GitHubApiHealth, cb_state: str) -> str:
    """Determine the overall health status.

    :param github: GitHub API health info.
    :param cb_state: Circuit breaker state string.
    :returns: One of 'healthy', 'degraded', or 'unhealthy'.
    :rtype: str
    """
    if cb_state == "open" or github.status == "critical":
        return "unhealthy"
    if cb_state == "half-open" or github.status in ("degraded", "unknown"):
        return "degraded"
    return "healthy"


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse}},
)
async def health() -> JSONResponse:
    """Return health status with subsystem probes."""
    github = _github_api_health()
    cb_state = _circuit_breaker_label()
    status = _overall_status(github, cb_state)

    stats = cache_stats()
    cache = CacheHealth(
        entries=stats["entries"],
        maxsize=stats["maxsize"],
        hit_ratio=stats["hit_ratio"],
    )

    body = HealthResponse(
        status=status,
        version="latest",
        uptime_seconds=round(time.monotonic() - _start_time, 1),
        github_api=github,
        cache=cache,
        circuit_breaker=cb_state,
    )

    http_status = 200 if status == "healthy" else 503
    return JSONResponse(content=body.model_dump(), status_code=http_status)
