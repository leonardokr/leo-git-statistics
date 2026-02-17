"""Temporal statistics history endpoints."""

import logging

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, Query, Request, Response

from api.deps.auth import verify_api_key
from api.deps.github_token import ResolvedToken, resolve_github_token
from api.deps.http_session import get_shared_session
from api.middleware.rate_limiter import DEFAULT_LIMIT, HEAVY_LIMIT, limiter
from api.models.requests import validated_username
from api.models.responses import ErrorResponse
from api.services.stats_service import PartialCollector, create_stats_collector
from api.services.notification_dispatcher import dispatch_webhooks
from src.core.stats_assembler import build_snapshot_payload
from src.db.snapshots import snapshot_store

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users/{username}/history",
    tags=["History"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "",
    summary="Get historical statistics snapshots",
    responses={500: {"model": ErrorResponse}},
)
@limiter.limit(DEFAULT_LIMIT)
async def get_history(
    request: Request,
    username: str = Depends(validated_username),
    from_date: str = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
) -> dict:
    """Retrieve stored statistics snapshots for a user over time."""
    snapshots = snapshot_store.get_snapshots(
        username,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )
    return {"username": username, "snapshots": snapshots}


@router.post(
    "/snapshot",
    summary="Take a statistics snapshot now",
    responses={500: {"model": ErrorResponse}},
    status_code=201,
)
@limiter.limit(HEAVY_LIMIT)
async def create_snapshot(
    request: Request,
    username: str = Depends(validated_username),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Collect current statistics and save a snapshot for historical tracking."""
    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    data = await build_snapshot_payload(collector, partial_collector=pc)

    await dispatch_webhooks(username, data)
    snapshot_store.save_snapshot(username, data)

    return {"username": username, "snapshot": data, **pc.warnings_payload()}
