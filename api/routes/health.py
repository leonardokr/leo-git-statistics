"""Health check endpoint."""

from fastapi import APIRouter

from api.models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> dict:
    """Return a basic health check response."""
    return {"status": "ok", "message": "Leo's Git Statistics API is running"}
