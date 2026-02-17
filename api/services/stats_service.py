"""Business logic for creating StatsCollector instances and formatting responses."""

import os

from aiohttp import ClientSession

from src.core.environment import Environment
from src.core.github_client import GitHubClient
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


async def create_stats_collector(username: str, session: ClientSession) -> StatsCollector:
    """Create a StatsCollector instance for the given username.

    :param username: GitHub username.
    :param session: Shared aiohttp.ClientSession.
    :returns: Configured StatsCollector instance.
    :rtype: StatsCollector
    """
    token = get_github_token()
    env = Environment(username=username, access_token=token)
    return StatsCollector(env, session)
