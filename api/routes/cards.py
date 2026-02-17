"""SVG card endpoints that return themed GitHub statistics cards."""

import logging
from typing import Literal

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import Response as StarletteResponse

from api.deps.auth import verify_api_key
from api.deps.cache import cache_get, cache_set
from api.deps.github_token import ResolvedToken, resolve_github_token
from api.deps.http_session import get_shared_session
from api.middleware.rate_limiter import DEFAULT_LIMIT, limiter
from api.models.requests import validated_username
from api.services.card_renderer import CARD_RENDERERS, available_themes
from api.services.stats_service import create_stats_collector
from src.presentation.stats_formatter import StatsFormatter

logger = logging.getLogger(__name__)

CardType = Literal[
    "overview", "languages", "streak",
    "languages-puzzle", "streak-battery", "commit-calendar",
]

router = APIRouter(
    prefix="/users/{username}/cards",
    tags=["Cards"],
    dependencies=[Depends(verify_api_key)],
)

_formatter = StatsFormatter()


@router.get(
    "/themes",
    summary="List available themes",
    response_model=list[str],
)
@limiter.limit(DEFAULT_LIMIT)
async def list_themes(request: Request) -> list[str]:
    """Return all available theme names."""
    return available_themes()


@router.get(
    "/{card_type}",
    summary="Get an SVG statistics card",
    responses={
        200: {"content": {"image/svg+xml": {}}, "description": "SVG card image"},
        422: {"description": "Invalid card type or theme"},
    },
)
@limiter.limit(DEFAULT_LIMIT)
async def get_card(
    request: Request,
    card_type: CardType,
    username: str = Depends(validated_username),
    theme: str = Query("default", description="Theme name (e.g. dracula, dark, nord)"),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> StarletteResponse:
    """Render and return an SVG statistics card for a GitHub user.

    Supported card types: overview, languages, streak, languages-puzzle,
    streak-battery, commit-calendar.
    """
    cache_key = f"card:{card_type}:{theme}"
    if not no_cache:
        hit, cached = cache_get(username, cache_key)
        if hit:
            return StarletteResponse(
                content=cached,
                media_type="image/svg+xml",
                headers={
                    "Cache-Control": "public, max-age=300",
                    "X-Cache": "HIT",
                },
            )

    renderer = CARD_RENDERERS.get(card_type)
    if renderer is None:
        return StarletteResponse(
            content=f"Unknown card type: {card_type}",
            status_code=422,
            media_type="text/plain",
        )

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    try:
        svg = await renderer(collector, theme, _formatter)
    except ValueError as exc:
        return StarletteResponse(
            content=str(exc),
            status_code=422,
            media_type="text/plain",
        )

    cache_set(username, cache_key, svg)

    return StarletteResponse(
        content=svg,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=300",
            "X-Cache": "MISS",
        },
    )
