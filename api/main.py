"""FastAPI application entry point with CORS, lifecycle events and routers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.deps.http_session import close_shared_session, create_shared_session
from api.routes import health, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage startup and shutdown of shared resources."""
    await create_shared_session()
    yield
    await close_shared_session()


app = FastAPI(
    title="Leo's Git Statistics API",
    description="REST API providing GitHub statistics and metrics. The same data used to generate SVG cards is available via JSON endpoints.",
    version="latest",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(users.router)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle configuration and validation errors."""
    logger.error("Configuration error: %s", exc)
    return JSONResponse(status_code=500, content={"error": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.error("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
