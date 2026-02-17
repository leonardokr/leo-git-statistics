"""User comparison endpoint."""

import asyncio
import logging
from typing import Any, Dict, Optional

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, Query, Request, Response

from api.deps.auth import verify_api_key
from api.deps.cache import cache_get, cache_set
from api.deps.github_token import ResolvedToken, resolve_github_token
from api.deps.http_session import get_shared_session
from api.middleware.rate_limiter import HEAVY_LIMIT, limiter
from api.models.requests import validated_username
from api.models.responses import ErrorResponse
from api.services.stats_service import PartialCollector, create_stats_collector

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users/{username}/compare",
    tags=["Compare"],
    dependencies=[Depends(verify_api_key)],
)


async def _collect_user_stats(
    username: str,
    session: ClientSession,
    resolved: ResolvedToken,
) -> Dict[str, Any]:
    """Collect overview stats for a single user.

    :param username: GitHub username.
    :param session: Shared aiohttp session.
    :param resolved: Resolved token with scope.
    :returns: Dictionary of collected stats.
    :rtype: dict
    """
    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    total_contributions = await pc.safe(collector.get_total_contributions(), 0, "total contributions")
    repos = await pc.safe(collector.get_repos(), set(), "repositories")
    stars = await pc.safe(collector.get_stargazers(), 0, "stargazers")
    forks = await pc.safe(collector.get_forks(), 0, "forks")
    pull_requests = await pc.safe(collector.get_pull_requests(), 0, "pull requests")
    issues = await pc.safe(collector.get_issues(), 0, "issues")
    lines = await pc.safe(collector.get_lines_changed(), (0, 0), "lines changed")
    current_streak = await pc.safe(collector.get_current_streak(), 0, "current streak")
    longest_streak = await pc.safe(collector.get_longest_streak(), 0, "longest streak")

    return {
        "username": username,
        "total_contributions": total_contributions,
        "repositories_count": len(repos),
        "total_stars": stars,
        "total_forks": forks,
        "total_pull_requests": pull_requests,
        "total_issues": issues,
        "lines_added": lines[0],
        "lines_deleted": lines[1],
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        **pc.warnings_payload(),
    }


def _compare_field(a_val: Any, b_val: Any) -> Optional[Dict[str, Any]]:
    """Compute diff and ratio between two numeric values.

    :param a_val: Value from user A.
    :param b_val: Value from user B.
    :returns: Dict with diff and ratio, or None if not comparable.
    :rtype: dict or None
    """
    if not isinstance(a_val, (int, float)) or not isinstance(b_val, (int, float)):
        return None
    diff = a_val - b_val
    ratio = round(a_val / b_val, 2) if b_val != 0 else None
    return {"diff": diff, "ratio": ratio}


COMPARE_FIELDS = [
    "total_contributions", "repositories_count", "total_stars", "total_forks",
    "total_pull_requests", "total_issues", "lines_added", "lines_deleted",
    "current_streak", "longest_streak",
]


@router.get(
    "/{other_username}",
    summary="Compare two GitHub users",
    responses={500: {"model": ErrorResponse}},
)
@limiter.limit(HEAVY_LIMIT)
async def compare_users(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    other_username: str = None,
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Compare statistics between two GitHub users side by side."""
    endpoint = f"compare:{other_username}"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            response.headers["X-Cache"] = "HIT"
            return cached

    user_a_task = _collect_user_stats(username, session, resolved)
    user_b_task = _collect_user_stats(other_username, session, resolved)
    user_a, user_b = await asyncio.gather(user_a_task, user_b_task)

    comparison = {}
    for field in COMPARE_FIELDS:
        result = _compare_field(user_a.get(field), user_b.get(field))
        if result is not None:
            comparison[field] = result

    data = {
        "user_a": user_a,
        "user_b": user_b,
        "comparison": comparison,
    }

    cache_set(username, endpoint, data)
    response.headers["X-Cache"] = "MISS"
    return data
