"""Repository traffic collection: views and clones."""

import asyncio
import logging
from typing import Dict, Optional, Set, Tuple
from datetime import date, timedelta

from src.core.environment import Environment
from src.core.github_client import GitHubClient

logger = logging.getLogger(__name__)


class TrafficCollector:
    """
    Collects cumulative view and clone traffic across repositories.

    :param environment_vars: Environment configuration.
    :param queries: GitHub API client instance.
    """

    __DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, environment_vars: Environment, queries: GitHubClient):
        self._env = environment_vars
        self._queries = queries

        self._views: Optional[int] = None
        self._clones: Optional[int] = None
        self._views_from_date: Optional[str] = None
        self._clones_from_date: Optional[str] = None

    @property
    def views(self) -> Optional[int]:
        return self._views

    @property
    def clones(self) -> Optional[int]:
        return self._clones

    @property
    def views_from_date(self) -> Optional[str]:
        return self._views_from_date

    @property
    def clones_from_date(self) -> Optional[str]:
        return self._clones_from_date

    async def _collect_traffic_entries(
        self, metric_type: str, last_date: str, accumulate_fn, repos: Set[str]
    ) -> Tuple[int, Set[str]]:
        """
        Collect traffic entries from all repos for a given metric.

        Repositories are fetched in parallel using a semaphore to avoid
        exceeding GitHub API rate limits.

        :param metric_type: Either "views" or "clones".
        :param last_date: The last recorded date for this metric.
        :param accumulate_fn: Callable to accumulate new counts.
        :param repos: Set of repository names.
        :return: Tuple of (today_count, all_relevant_dates).
        """
        today = date.today().strftime(self.__DATE_FORMAT)
        yesterday = (date.today() - timedelta(1)).strftime(self.__DATE_FORMAT)
        dates = {last_date, yesterday}
        today_count = 0

        sem = asyncio.Semaphore(10)
        repo_list = list(repos)

        async def fetch_one(repo: str) -> Dict:
            async with sem:
                return await self._queries.query_rest(
                    f"/repos/{repo}/traffic/{metric_type}"
                )

        results = await asyncio.gather(
            *[fetch_one(r) for r in repo_list], return_exceptions=True
        )

        for repo, result in zip(repo_list, results):
            if isinstance(result, BaseException):
                logger.warning(
                    "Failed to fetch %s traffic for %s: %s", metric_type, repo, result
                )
                continue

            for entry in result.get(metric_type, []):
                timestamp = (entry.get("timestamp") or "")[:10]
                if timestamp == today:
                    today_count += entry.get("count", 0)
                elif timestamp > last_date:
                    accumulate_fn(entry.get("count", 0))
                    dates.add(timestamp)

        if last_date == "0000-00-00":
            dates.discard(last_date)

        return today_count, dates

    async def fetch_views(self, repos: Set[str]) -> int:
        """
        Retrieve the cumulative count of repository views.

        :param repos: Set of repository names to collect traffic for.
        :return: Total repository view count.
        """
        if self._views is not None:
            return self._views

        traffic = self._env.traffic
        today_count, dates = await self._collect_traffic_entries(
            "views", traffic.repo_last_viewed, traffic.set_views, repos
        )
        yesterday = (date.today() - timedelta(1)).strftime(self.__DATE_FORMAT)

        if traffic.store_repo_view_count:
            traffic.set_last_viewed(yesterday)
            if traffic.repo_first_viewed == "0000-00-00":
                traffic.repo_first_viewed = min(dates)
            traffic.set_first_viewed(traffic.repo_first_viewed)
            self._views_from_date = traffic.repo_first_viewed
        else:
            self._views_from_date = min(dates)

        self._views = traffic.repo_views + today_count
        return self._views

    async def fetch_clones(self, repos: Set[str]) -> int:
        """
        Retrieve the cumulative count of repository clones.

        :param repos: Set of repository names to collect traffic for.
        :return: Total repository clone count.
        """
        if self._clones is not None:
            return self._clones

        traffic = self._env.traffic
        today_count, dates = await self._collect_traffic_entries(
            "clones", traffic.repo_last_cloned, traffic.set_clones, repos
        )
        yesterday = (date.today() - timedelta(1)).strftime(self.__DATE_FORMAT)

        if traffic.store_repo_clone_count:
            traffic.set_last_cloned(yesterday)
            if traffic.repo_first_cloned == "0000-00-00":
                traffic.repo_first_cloned = min(dates)
            traffic.set_first_cloned(traffic.repo_first_cloned)
            self._clones_from_date = traffic.repo_first_cloned
        else:
            self._clones_from_date = min(dates)

        self._clones = traffic.repo_clones + today_count
        return self._clones
