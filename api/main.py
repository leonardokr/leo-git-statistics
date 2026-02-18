"""FastAPI application entry point with CORS, lifecycle events and routers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from prometheus_fastapi_instrumentator import Instrumentator

from api.deps.http_session import close_shared_session, create_shared_session, get_shared_session
from api.middleware.logging import RequestLoggingMiddleware, configure_structlog
from api.middleware.metrics import update_infrastructure_gauges
from api.middleware.rate_limiter import limiter
from api.routes import cards, compare, health, history, users, webhooks
from src.core.github_client import probe_rate_limit

# FIX: Inject tornado.gen into sys.modules to satisfy pybreaker's missing import
import tornado.gen as gen
sys.modules['gen'] = gen

configure_structlog()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
    force=True,
)

formatter = structlog.stdlib.ProcessorFormatter(
    processor=structlog.dev.ConsoleRenderer(),
)

root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.setFormatter(formatter)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage startup and shutdown of shared resources."""
    await create_shared_session()
    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        await probe_rate_limit(get_shared_session(), token)
    yield
    await close_shared_session()


app = FastAPI(
    title="Leo's Git Statistics API",
    description="REST API providing GitHub statistics and metrics. The same data used to generate SVG cards is available via JSON endpoints.",
    version="latest",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(users.router, prefix="/v1")
app.include_router(cards.router, prefix="/v1")
app.include_router(compare.router, prefix="/v1")
app.include_router(history.router, prefix="/v1")
app.include_router(webhooks.router, prefix="/v1")

Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics", "/health"],
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)



@app.middleware("http")
async def refresh_gauges(request: Request, call_next):
    """Update Prometheus infrastructure gauges after each request."""
    response = await call_next(request)
    update_infrastructure_gauges()
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle configuration and validation errors."""
    logger.error("Configuration error: %s", exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.error("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
