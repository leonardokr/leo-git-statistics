"""Engagement metrics collection: pull requests, issues and collaborators."""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any, Union

from src.core.environment import Environment
from src.core.github_client import GitHubClient

logger = logging.getLogger(__name__)


def _ensure_list(data: Union[Dict, List, Any]) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "message" in data:
        logger.warning("API returned error response: %s", data.get("message"))
    return []


class EngagementCollector:
    """
    Collects engagement metrics: pull requests, issues and collaborators.

    :param environment_vars: Environment configuration.
    :param queries: GitHub API client instance.
    """

    def __init__(self, environment_vars: Environment, queries: GitHubClient):
        self._env = environment_vars
        self._queries = queries

        self._pull_requests: Optional[int] = None
        self._issues: Optional[int] = None
        self._collaborators: Optional[int] = None

    @property
    def pull_requests(self) -> Optional[int]:
        return self._pull_requests

    @property
    def issues(self) -> Optional[int]:
        return self._issues

    @property
    def collaborators(self) -> Optional[int]:
        return self._collaborators

    async def fetch_pull_requests(self, repos: Set[str]) -> int:
        """
        Retrieve the total number of pull requests across all repositories.

        Repositories are fetched in parallel using a semaphore to avoid
        exceeding GitHub API rate limits.

        :param repos: Set of repository names.
        :return: Total pull request count.
        """
        if self._pull_requests is not None:
            return self._pull_requests

        sem = asyncio.Semaphore(10)
        repo_list = list(repos)

        async def fetch_one(repo: str) -> List:
            async with sem:
                return _ensure_list(
                    await self._queries.query_rest(f"/repos/{repo}/pulls?state=all")
                )

        results = await asyncio.gather(
            *[fetch_one(r) for r in repo_list], return_exceptions=True
        )

        self._pull_requests = 0
        for repo, result in zip(repo_list, results):
            if isinstance(result, BaseException):
                logger.warning("Failed to fetch pull requests for %s: %s", repo, result)
                continue
            for obj in result:
                if isinstance(obj, dict):
                    self._pull_requests += 1
        return self._pull_requests

    async def fetch_issues(self, repos: Set[str]) -> int:
        """
        Retrieve the total number of issues across all repositories.

        Repositories are fetched in parallel using a semaphore to avoid
        exceeding GitHub API rate limits.

        :param repos: Set of repository names.
        :return: Total issue count (excluding pull requests).
        """
        if self._issues is not None:
            return self._issues

        sem = asyncio.Semaphore(10)
        repo_list = list(repos)

        async def fetch_one(repo: str) -> List:
            async with sem:
                return _ensure_list(
                    await self._queries.query_rest(f"/repos/{repo}/issues?state=all")
                )

        results = await asyncio.gather(
            *[fetch_one(r) for r in repo_list], return_exceptions=True
        )

        self._issues = 0
        for repo, result in zip(repo_list, results):
            if isinstance(result, BaseException):
                logger.warning("Failed to fetch issues for %s: %s", repo, result)
                continue
            for obj in result:
                if isinstance(obj, dict):
                    try:
                        if obj.get("html_url").split("/")[-2] == "issues":
                            self._issues += 1
                    except AttributeError:
                        continue
        return self._issues

    async def fetch_collaborators(
        self, repos: Set[str], contributors: Set[str]
    ) -> int:
        """
        Retrieve the total number of unique collaborators.

        Repositories are fetched in parallel using a semaphore to avoid
        exceeding GitHub API rate limits.

        :param repos: Set of repository names.
        :param contributors: Set of known contributors for union.
        :return: Total collaborator count.
        """
        if self._collaborators is not None:
            return self._collaborators

        sem = asyncio.Semaphore(10)
        repo_list = list(repos)

        async def fetch_one(repo: str) -> List:
            async with sem:
                return _ensure_list(
                    await self._queries.query_rest(f"/repos/{repo}/collaborators")
                )

        results = await asyncio.gather(
            *[fetch_one(r) for r in repo_list], return_exceptions=True
        )

        collaborator_set: Set[str] = set()
        for repo, result in zip(repo_list, results):
            if isinstance(result, BaseException):
                logger.warning("Failed to fetch collaborators for %s: %s", repo, result)
                continue
            for obj in result:
                if isinstance(obj, dict):
                    collaborator_set.add(obj.get("login"))

        collabs = max(0, len(collaborator_set.union(contributors)) - 1)
        self._collaborators = self._env.more_collabs + collabs
        return self._collaborators
