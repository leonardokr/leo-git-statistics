"""Health check endpoint with internal subsystem probes."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.models.responses import HealthResponse
from src.core.github_client import github_breaker, rate_limit_state

router = APIRouter(tags=["Health"])


def _github_status() -> str:
    """Determine GitHub API status from current rate limit state.

    :returns: One of 'connected', 'degraded', 'critical', or 'unknown'.
    :rtype: str
    """
    remaining = rate_limit_state.remaining
    if remaining is None:
        return "unknown"
    if remaining > 100:
        return "connected"
    if remaining > 10:
        return "degraded"
    return "critical"


def _overall_status() -> str:
    """Determine the overall health status from all subsystems.

    :returns: One of 'ok', 'degraded', or 'unavailable'.
    :rtype: str
    """
    cb_state = str(github_breaker.current_state)
    github = _github_status()

    if cb_state == "open" or github == "critical":
        return "unavailable"
    if cb_state == "half-open" or github in ("degraded", "unknown"):
        return "degraded"
    return "ok"


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse}},
)
async def health() -> JSONResponse:
    """Return health status without exposing internal details."""
    status = _overall_status()
    body = HealthResponse(status=status)
    http_status = 200 if status != "unavailable" else 503
    return JSONResponse(content=body.model_dump(), status_code=http_status)
