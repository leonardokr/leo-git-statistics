"""User statistics endpoints."""

import logging

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, Query, Request, Response

from api.deps.auth import verify_api_key
from api.deps.cache import cache_get, cache_set
from api.deps.github_token import ResolvedToken, resolve_github_token
from api.deps.http_session import get_shared_session
from api.middleware.rate_limiter import AUTH_LIMIT, DEFAULT_LIMIT, HEAVY_LIMIT, limiter
import math

from api.models.requests import PaginationParams, RepoQueryParams, validated_username
from api.models.responses import (
    DetailedRepoItem,
    DetailedRepositoriesResponse,
    ErrorResponse,
    FullStatsResponse,
    LanguagesResponse,
    OverviewResponse,
    PaginatedDetailedRepositoriesResponse,
    PaginatedRepositoriesResponse,
    PaginationMeta,
    RecentContributionsResponse,
    RepositoriesResponse,
    StreakResponse,
    WeeklyCommitsResponse,
)
from api.services.stats_service import PartialCollector, create_stats_collector
from src.core.github_client import GitHubClient, rate_limit_state

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users/{username}",
    tags=["Users"],
    dependencies=[Depends(verify_api_key)],
)


def _paginate(items: list, page: int, per_page: int) -> tuple[list, PaginationMeta]:
    """Slice a list according to pagination parameters.

    :param items: Full list of items.
    :param page: 1-based page number.
    :param per_page: Items per page.
    :returns: Tuple of (page_items, pagination_meta).
    :rtype: tuple
    """
    total = len(items)
    total_pages = max(1, math.ceil(total / per_page))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def _set_cache_header(response: Response, hit: bool) -> None:
    response.headers["X-Cache"] = "HIT" if hit else "MISS"


def _set_rate_limit_headers(response: Response) -> None:
    if rate_limit_state.remaining is not None:
        response.headers["X-GitHub-RateLimit-Remaining"] = str(rate_limit_state.remaining)
    if rate_limit_state.limit is not None:
        response.headers["X-GitHub-RateLimit-Limit"] = str(rate_limit_state.limit)
    if rate_limit_state.reset is not None:
        response.headers["X-GitHub-RateLimit-Reset"] = str(rate_limit_state.reset)


@router.get("/overview", response_model=OverviewResponse, responses={500: {"model": ErrorResponse}})
@limiter.limit(DEFAULT_LIMIT)
async def get_user_overview(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get comprehensive overview statistics for a GitHub user."""
    endpoint = "overview"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    name = await pc.safe(collector.get_name(), None, "name")
    total_contributions = await pc.safe(collector.get_total_contributions(), None, "total contributions")
    repos = await pc.safe(collector.get_repos(), set(), "repositories")
    stars = await pc.safe(collector.get_stargazers(), None, "stargazers")
    forks = await pc.safe(collector.get_forks(), None, "forks")
    views = await pc.safe(collector.get_views(), None, "views")
    views_from = await pc.safe(collector.get_views_from_date(), None, "views from date")
    clones = await pc.safe(collector.get_clones(), None, "clones")
    clones_from = await pc.safe(collector.get_clones_from_date(), None, "clones from date")
    pull_requests = await pc.safe(collector.get_pull_requests(), None, "pull requests")
    issues = await pc.safe(collector.get_issues(), None, "issues")
    lines = await pc.safe(collector.get_lines_changed(), (None, None), "lines changed")
    avg_percent = await pc.safe(collector.get_avg_contribution_percent(), None, "avg contribution percent")
    collaborators = await pc.safe(collector.get_collaborators(), None, "collaborators")
    contributors = await pc.safe(collector.get_contributors(), set(), "contributors")

    data = {
        "username": username,
        "name": name,
        "total_contributions": total_contributions,
        "repositories_count": len(repos) if repos is not None else None,
        "total_stars": stars,
        "total_forks": forks,
        "total_views": views,
        "views_from_date": views_from,
        "total_clones": clones,
        "clones_from_date": clones_from,
        "total_pull_requests": pull_requests,
        "total_issues": issues,
        "lines_added": lines[0],
        "lines_deleted": lines[1],
        "avg_contribution_percent": avg_percent,
        "collaborators_count": collaborators,
        "contributors_count": len(contributors) if contributors is not None else None,
        **pc.warnings_payload(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data


@router.get("/languages", response_model=LanguagesResponse, responses={500: {"model": ErrorResponse}})
@limiter.limit(DEFAULT_LIMIT)
async def get_user_languages(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    proportional: bool = Query(False),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get programming language distribution for a GitHub user."""
    endpoint = "languages_proportional" if proportional else "languages"

    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    if proportional:
        languages = await pc.safe(collector.get_languages_proportional(), None, "languages")
    else:
        languages = await pc.safe(collector.get_languages(), None, "languages")

    data = {
        "username": username,
        "languages": languages,
        **pc.warnings_payload(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data


@router.get("/streak", response_model=StreakResponse, responses={500: {"model": ErrorResponse}})
@limiter.limit(DEFAULT_LIMIT)
async def get_user_streak(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get contribution streak information for a GitHub user."""
    endpoint = "streak"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    current_streak = await pc.safe(collector.get_current_streak(), None, "current streak")
    current_range = await pc.safe(collector.get_current_streak_range(), None, "current streak range")
    longest_streak = await pc.safe(collector.get_longest_streak(), None, "longest streak")
    longest_range = await pc.safe(collector.get_longest_streak_range(), None, "longest streak range")
    total_contributions = await pc.safe(collector.get_total_contributions(), None, "total contributions")

    data = {
        "username": username,
        "current_streak": current_streak,
        "current_streak_range": current_range,
        "longest_streak": longest_streak,
        "longest_streak_range": longest_range,
        "total_contributions": total_contributions,
        **pc.warnings_payload(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data


@router.get(
    "/contributions/recent",
    response_model=RecentContributionsResponse,
    responses={500: {"model": ErrorResponse}},
)
@limiter.limit(DEFAULT_LIMIT)
async def get_recent_contributions(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get recent contribution counts (last 10 days)."""
    endpoint = "contributions_recent"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    recent = await pc.safe(collector.get_recent_contributions(), None, "recent contributions")

    data = {
        "username": username,
        "recent_contributions": recent,
        **pc.warnings_payload(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data


@router.get(
    "/commits/weekly",
    response_model=WeeklyCommitsResponse,
    responses={500: {"model": ErrorResponse}},
)
@limiter.limit(DEFAULT_LIMIT)
async def get_weekly_commits(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get weekly commit schedule for a GitHub user."""
    endpoint = "commits_weekly"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    weekly = await pc.safe(collector.get_weekly_commit_schedule(), None, "weekly commits")

    data = {
        "username": username,
        "weekly_commits": weekly,
        **pc.warnings_payload(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data


@router.get(
    "/repositories",
    response_model=PaginatedRepositoriesResponse,
    responses={500: {"model": ErrorResponse}},
)
@limiter.limit(DEFAULT_LIMIT)
async def get_user_repositories(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    pagination: PaginationParams = Depends(),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get paginated list of repositories for a GitHub user."""
    endpoint = f"repositories:p{pagination.page}:{pagination.per_page}"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    repos = await pc.safe(collector.get_repos(), None, "repositories")

    all_repos = sorted(list(repos)) if repos is not None else []
    page_items, meta = _paginate(all_repos, pagination.page, pagination.per_page)

    data = {
        "username": username,
        "data": page_items,
        "pagination": meta.model_dump(),
        **pc.warnings_payload(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data


@router.get(
    "/repositories/detailed",
    response_model=PaginatedDetailedRepositoriesResponse,
    responses={500: {"model": ErrorResponse}},
)
@limiter.limit(DEFAULT_LIMIT)
async def get_user_repositories_detailed(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    params: RepoQueryParams = Depends(),
    pagination: PaginationParams = Depends(),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get paginated detailed repository information for a GitHub user."""
    visibility = params.visibility
    if not resolved.user_owns_token and visibility in ("private", "all"):
        visibility = "public"

    endpoint = (
        f"repositories_detailed:{visibility}:{params.sort}:{params.limit}"
        f":{params.exclude_forks}:{params.exclude_archived}"
        f":p{pagination.page}:{pagination.per_page}"
    )
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    client = GitHubClient(username=username, access_token=resolved.token, session=session)

    repos_url = (
        f"users/{username}/repos?per_page={params.limit}"
        f"&sort={params.sort}&type={visibility}"
    )
    raw_repos = await client.query_rest(repos_url)

    if not raw_repos:
        _set_cache_header(response, False)
        _set_rate_limit_headers(response)
        empty_meta = PaginationMeta(
            page=1, per_page=pagination.per_page,
            total=0, total_pages=1, has_next=False, has_prev=False,
        )
        return {"username": username, "data": [], "pagination": empty_meta.model_dump()}

    repositories = []
    for repo in raw_repos:
        if params.exclude_forks and repo.get("fork", False):
            continue
        if params.exclude_archived and repo.get("archived", False):
            continue
        if not resolved.user_owns_token and repo.get("private", False):
            continue

        repo_data = {
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "description": repo.get("description", ""),
            "html_url": repo.get("html_url"),
            "homepage": repo.get("homepage", ""),
            "language": repo.get("language"),
            "stargazers_count": repo.get("stargazers_count", 0),
            "forks_count": repo.get("forks_count", 0),
            "open_issues_count": repo.get("open_issues_count", 0),
            "watchers_count": repo.get("watchers_count", 0),
            "topics": repo.get("topics", []),
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
            "is_fork": repo.get("fork", False),
            "is_archived": repo.get("archived", False),
            "is_private": repo.get("private", False),
        }

        try:
            languages = await client.query_rest(
                f"repos/{username}/{repo.get('name')}/languages"
            )
            if languages:
                repo_data["languages"] = languages
        except Exception as exc:
            logger.warning("Failed to fetch languages for %s: %s", repo.get("name"), exc)
            repo_data["languages"] = {}

        repositories.append(repo_data)

    page_items, meta = _paginate(repositories, pagination.page, pagination.per_page)

    data = {
        "username": username,
        "data": page_items,
        "pagination": meta.model_dump(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data


@router.get(
    "/stats/full",
    response_model=FullStatsResponse,
    responses={500: {"model": ErrorResponse}},
)
@limiter.limit(HEAVY_LIMIT)
async def get_full_stats(
    request: Request,
    response: Response,
    username: str = Depends(validated_username),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
    resolved: ResolvedToken = Depends(resolve_github_token),
) -> dict:
    """Get all statistics for a GitHub user in a single request."""
    endpoint = "stats_full"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(
        username, session, token=resolved.token, repo_filter=resolved.repo_filter,
    )

    pc = PartialCollector()
    name = await pc.safe(collector.get_name(), None, "name")
    total_contributions = await pc.safe(collector.get_total_contributions(), None, "total contributions")
    repos = await pc.safe(collector.get_repos(), set(), "repositories")
    stars = await pc.safe(collector.get_stargazers(), None, "stargazers")
    forks = await pc.safe(collector.get_forks(), None, "forks")
    views = await pc.safe(collector.get_views(), None, "views")
    views_from = await pc.safe(collector.get_views_from_date(), None, "views from date")
    clones = await pc.safe(collector.get_clones(), None, "clones")
    clones_from = await pc.safe(collector.get_clones_from_date(), None, "clones from date")
    pull_requests = await pc.safe(collector.get_pull_requests(), None, "pull requests")
    issues = await pc.safe(collector.get_issues(), None, "issues")
    lines = await pc.safe(collector.get_lines_changed(), (None, None), "lines changed")
    avg_percent = await pc.safe(collector.get_avg_contribution_percent(), None, "avg contribution percent")
    collaborators = await pc.safe(collector.get_collaborators(), None, "collaborators")
    contributors = await pc.safe(collector.get_contributors(), set(), "contributors")
    languages = await pc.safe(collector.get_languages(), None, "languages")
    current_streak = await pc.safe(collector.get_current_streak(), None, "current streak")
    current_range = await pc.safe(collector.get_current_streak_range(), None, "current streak range")
    longest_streak = await pc.safe(collector.get_longest_streak(), None, "longest streak")
    longest_range = await pc.safe(collector.get_longest_streak_range(), None, "longest streak range")
    recent = await pc.safe(collector.get_recent_contributions(), None, "recent contributions")
    weekly = await pc.safe(collector.get_weekly_commit_schedule(), None, "weekly commits")

    data = {
        "username": username,
        "overview": {
            "name": name,
            "total_contributions": total_contributions,
            "repositories_count": len(repos) if repos is not None else None,
            "total_stars": stars,
            "total_forks": forks,
            "total_views": views,
            "views_from_date": views_from,
            "total_clones": clones,
            "clones_from_date": clones_from,
            "total_pull_requests": pull_requests,
            "total_issues": issues,
            "lines_added": lines[0],
            "lines_deleted": lines[1],
            "avg_contribution_percent": avg_percent,
            "collaborators_count": collaborators,
            "contributors_count": len(contributors) if contributors is not None else None,
        },
        "languages": languages,
        "streak": {
            "current_streak": current_streak,
            "current_streak_range": current_range,
            "longest_streak": longest_streak,
            "longest_streak_range": longest_range,
        },
        "contributions": {
            "total": total_contributions,
            "recent": recent,
        },
        "repositories": {
            "count": len(repos) if repos is not None else None,
            "list": sorted(list(repos)) if repos is not None else None,
        },
        "weekly_commits": weekly,
        **pc.warnings_payload(),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    _set_rate_limit_headers(response)
    return data
