"""Business logic for creating StatsCollector instances and formatting responses."""

import logging
import os
from typing import Any, Awaitable, List, Optional, TypeVar

from aiohttp import ClientSession

from src.core.environment import Environment
from src.core.repository_filter import RepositoryFilter
from src.core.stats_collector import StatsCollector

logger = logging.getLogger(__name__)
T = TypeVar("T")


class PartialCollector:
    """Wraps async collector calls to capture failures without aborting the request.

    Each call to :meth:`safe` tries to await the given coroutine. On failure the
    default value is returned and a human-readable warning is recorded.

    :example:
        pc = PartialCollector()
        stars = await pc.safe(collector.get_stargazers(), 0, "stargazers")
        data = {"stars": stars, **pc.warnings_payload()}
    """

    def __init__(self):
        self._warnings: List[str] = []

    async def safe(self, coro: Awaitable[T], default: T, label: str) -> T:
        """Await *coro* and return its result, or *default* on failure.

        :param coro: The awaitable to execute.
        :param default: Value returned when *coro* raises.
        :param label: Short description used in the warning message.
        :returns: The coroutine result or *default*.
        """
        try:
            return await coro
        except Exception as exc:
            msg = f"{label} unavailable: {exc}"
            logger.warning(msg)
            self._warnings.append(msg)
            return default

    def warnings_payload(self) -> dict:
        """Return a dict fragment to merge into the response.

        :returns: ``{"warnings": [...]}`` if any warnings were recorded,
                  otherwise an empty dict.
        """
        if self._warnings:
            return {"warnings": list(self._warnings)}
        return {}


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
