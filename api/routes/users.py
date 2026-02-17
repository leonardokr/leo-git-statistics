"""User statistics endpoints."""

import logging

from fastapi import APIRouter, Depends, Query, Response
from aiohttp import ClientSession

from api.deps.cache import cache_get, cache_set
from api.deps.http_session import get_shared_session
from api.models.responses import (
    DetailedRepoItem,
    DetailedRepositoriesResponse,
    ErrorResponse,
    FullStatsResponse,
    LanguagesResponse,
    OverviewResponse,
    RecentContributionsResponse,
    RepositoriesResponse,
    StreakResponse,
    WeeklyCommitsResponse,
)
from api.services.stats_service import create_stats_collector, get_github_token
from src.core.github_client import GitHubClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/{username}", tags=["Users"])


def _set_cache_header(response: Response, hit: bool) -> None:
    response.headers["X-Cache"] = "HIT" if hit else "MISS"


@router.get("/overview", response_model=OverviewResponse, responses={500: {"model": ErrorResponse}})
async def get_user_overview(
    username: str,
    response: Response,
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get comprehensive overview statistics for a GitHub user."""
    endpoint = "overview"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(username, session)

    name = await collector.get_name()
    total_contributions = await collector.get_total_contributions()
    repos = await collector.get_repos()
    stars = await collector.get_stargazers()
    forks = await collector.get_forks()
    views = await collector.get_views()
    views_from = await collector.get_views_from_date()
    clones = await collector.get_clones()
    clones_from = await collector.get_clones_from_date()
    pull_requests = await collector.get_pull_requests()
    issues = await collector.get_issues()
    lines_added, lines_deleted = await collector.get_lines_changed()
    avg_percent = await collector.get_avg_contribution_percent()
    collaborators = await collector.get_collaborators()
    contributors = await collector.get_contributors()

    data = {
        "username": username,
        "name": name,
        "total_contributions": total_contributions,
        "repositories_count": len(repos),
        "total_stars": stars,
        "total_forks": forks,
        "total_views": views,
        "views_from_date": views_from,
        "total_clones": clones,
        "clones_from_date": clones_from,
        "total_pull_requests": pull_requests,
        "total_issues": issues,
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "avg_contribution_percent": avg_percent,
        "collaborators_count": collaborators,
        "contributors_count": len(contributors),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data


@router.get("/languages", response_model=LanguagesResponse, responses={500: {"model": ErrorResponse}})
async def get_user_languages(
    username: str,
    response: Response,
    proportional: bool = Query(False),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get programming language distribution for a GitHub user."""
    endpoint = "languages_proportional" if proportional else "languages"

    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(username, session)

    if proportional:
        languages = await collector.get_languages_proportional()
    else:
        languages = await collector.get_languages()

    data = {
        "username": username,
        "languages": languages,
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data


@router.get("/streak", response_model=StreakResponse, responses={500: {"model": ErrorResponse}})
async def get_user_streak(
    username: str,
    response: Response,
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get contribution streak information for a GitHub user."""
    endpoint = "streak"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(username, session)

    current_streak = await collector.get_current_streak()
    current_range = await collector.get_current_streak_range()
    longest_streak = await collector.get_longest_streak()
    longest_range = await collector.get_longest_streak_range()
    total_contributions = await collector.get_total_contributions()

    data = {
        "username": username,
        "current_streak": current_streak,
        "current_streak_range": current_range,
        "longest_streak": longest_streak,
        "longest_streak_range": longest_range,
        "total_contributions": total_contributions,
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data


@router.get(
    "/contributions/recent",
    response_model=RecentContributionsResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_recent_contributions(
    username: str,
    response: Response,
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get recent contribution counts (last 10 days)."""
    endpoint = "contributions_recent"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(username, session)
    recent = await collector.get_recent_contributions()

    data = {
        "username": username,
        "recent_contributions": recent,
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data


@router.get(
    "/commits/weekly",
    response_model=WeeklyCommitsResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_weekly_commits(
    username: str,
    response: Response,
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get weekly commit schedule for a GitHub user."""
    endpoint = "commits_weekly"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(username, session)
    weekly = await collector.get_weekly_commit_schedule()

    data = {
        "username": username,
        "weekly_commits": weekly,
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data


@router.get(
    "/repositories",
    response_model=RepositoriesResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_user_repositories(
    username: str,
    response: Response,
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get list of repositories for a GitHub user."""
    endpoint = "repositories"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(username, session)
    repos = await collector.get_repos()

    data = {
        "username": username,
        "repositories_count": len(repos),
        "repositories": sorted(list(repos)),
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data


@router.get(
    "/repositories/detailed",
    response_model=DetailedRepositoriesResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_user_repositories_detailed(
    username: str,
    response: Response,
    visibility: str = Query("public"),
    sort: str = Query("updated"),
    limit: int = Query(100),
    exclude_forks: bool = Query(True),
    exclude_archived: bool = Query(True),
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get detailed repository information for a GitHub user."""
    endpoint = f"repositories_detailed:{visibility}:{sort}:{limit}:{exclude_forks}:{exclude_archived}"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    token = get_github_token()
    client = GitHubClient(username=username, access_token=token, session=session)

    repos_url = f"users/{username}/repos?per_page={limit}&sort={sort}&type={visibility}"
    raw_repos = await client.query_rest(repos_url)

    if not raw_repos:
        _set_cache_header(response, False)
        return {"username": username, "repositories_count": 0, "repositories": []}

    repositories = []
    for repo in raw_repos:
        if exclude_forks and repo.get("fork", False):
            continue
        if exclude_archived and repo.get("archived", False):
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

    data = {
        "username": username,
        "repositories_count": len(repositories),
        "repositories": repositories,
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data


@router.get(
    "/stats/full",
    response_model=FullStatsResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_full_stats(
    username: str,
    response: Response,
    no_cache: bool = Query(False),
    session: ClientSession = Depends(get_shared_session),
) -> dict:
    """Get all statistics for a GitHub user in a single request."""
    endpoint = "stats_full"
    if not no_cache:
        hit, cached = cache_get(username, endpoint)
        if hit:
            _set_cache_header(response, True)
            return cached

    collector = await create_stats_collector(username, session)

    name = await collector.get_name()
    total_contributions = await collector.get_total_contributions()
    repos = await collector.get_repos()
    stars = await collector.get_stargazers()
    forks = await collector.get_forks()
    views = await collector.get_views()
    views_from = await collector.get_views_from_date()
    clones = await collector.get_clones()
    clones_from = await collector.get_clones_from_date()
    pull_requests = await collector.get_pull_requests()
    issues = await collector.get_issues()
    lines_added, lines_deleted = await collector.get_lines_changed()
    avg_percent = await collector.get_avg_contribution_percent()
    collaborators = await collector.get_collaborators()
    contributors = await collector.get_contributors()
    languages = await collector.get_languages()
    current_streak = await collector.get_current_streak()
    current_range = await collector.get_current_streak_range()
    longest_streak = await collector.get_longest_streak()
    longest_range = await collector.get_longest_streak_range()
    recent = await collector.get_recent_contributions()
    weekly = await collector.get_weekly_commit_schedule()

    data = {
        "username": username,
        "overview": {
            "name": name,
            "total_contributions": total_contributions,
            "repositories_count": len(repos),
            "total_stars": stars,
            "total_forks": forks,
            "total_views": views,
            "views_from_date": views_from,
            "total_clones": clones,
            "clones_from_date": clones_from,
            "total_pull_requests": pull_requests,
            "total_issues": issues,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "avg_contribution_percent": avg_percent,
            "collaborators_count": collaborators,
            "contributors_count": len(contributors),
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
            "count": len(repos),
            "list": sorted(list(repos)),
        },
        "weekly_commits": weekly,
    }

    cache_set(username, endpoint, data)
    _set_cache_header(response, False)
    return data
