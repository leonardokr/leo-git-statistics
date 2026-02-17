"""Business logic for creating StatsCollector instances and formatting responses."""

import os
from typing import Optional

from aiohttp import ClientSession

from src.core.environment import Environment
from src.core.repository_filter import RepositoryFilter
from src.core.stats_collector import StatsCollector


def get_github_token() -> str:
    """Return the GitHub token from environment variables.

    :returns: The GitHub personal access token.
    :rtype: str
    :raises ValueError: If no token is configured.
    """
    token = os.getenv("GITHUB_TOKEN") or os.getenv("ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN or ACCESS_TOKEN environment variable not set")
    return token


async def create_stats_collector(
    username: str,
    session: ClientSession,
    *,
    token: Optional[str] = None,
    repo_filter: Optional[RepositoryFilter] = None,
) -> StatsCollector:
    """Create a StatsCollector instance for the given username.

    :param username: GitHub username.
    :param session: Shared aiohttp.ClientSession.
    :param token: GitHub token to use. Falls back to the server token.
    :param repo_filter: Optional RepositoryFilter override for scope control.
    :returns: Configured StatsCollector instance.
    :rtype: StatsCollector
    """
    effective_token = token or get_github_token()
    env = Environment(
        username=username,
        access_token=effective_token,
        repo_filter=repo_filter,
    )
    return StatsCollector(env, session)
