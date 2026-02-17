#!/usr/bin/python3
"""GitHub Statistics Collector Module.

This module provides a facade that delegates to specialized collectors
while maintaining a unified public API for generators.
"""

import logging
from typing import Dict, Optional, Set, Tuple, Any
from aiohttp import ClientSession

from src.core.environment import Environment
from src.core.github_client import GitHubClient
from src.core.repo_stats_collector import RepoStatsCollector
from src.core.contribution_tracker import ContributionTracker
from src.core.code_change_analyzer import CodeChangeAnalyzer
from src.core.traffic_collector import TrafficCollector
from src.core.engagement_collector import EngagementCollector
from src.core.commit_schedule_collector import CommitScheduleCollector
from src.utils.decorators import lazy_async_property

logger = logging.getLogger(__name__)


class StatsCollector:
    """Facade that composes specialized collectors and exposes a unified API.

    New collectors can be registered via :meth:`register_collector` so that
    additional metrics are available without modifying this class.

    :param environment_vars: Configuration and environment settings.
    :param session: aiohttp ClientSession for making requests.
    :param github_client: Optional pre-built GitHubClient.
    """

    def __init__(self, environment_vars: Environment, session: ClientSession,
                 github_client: Optional[GitHubClient] = None):
        self.environment_vars: Environment = environment_vars
        self.queries = github_client or GitHubClient(
            username=self.environment_vars.username,
            access_token=self.environment_vars.access_token,
            session=session,
        )

        self._collectors: Dict[str, Any] = {}

        self._repo_stats = RepoStatsCollector(environment_vars, self.queries)
        self._contributions = ContributionTracker(self.queries)
        self._code_changes = CodeChangeAnalyzer(environment_vars.username, self.queries)
        self._traffic = TrafficCollector(environment_vars, self.queries)
        self._engagement = EngagementCollector(environment_vars, self.queries)
        self._commit_schedule = CommitScheduleCollector(environment_vars, self.queries)

        self.register_collector("repo_stats", self._repo_stats)
        self.register_collector("contributions", self._contributions)
        self.register_collector("code_changes", self._code_changes)
        self.register_collector("traffic", self._traffic)
        self.register_collector("engagement", self._engagement)
        self.register_collector("commit_schedule", self._commit_schedule)

    def register_collector(self, name: str, collector: Any) -> None:
        """Register a named collector for later retrieval.

        :param name: Unique identifier for the collector.
        :param collector: The collector instance.
        """
        self._collectors[name] = collector

    def get_collector(self, name: str) -> Any:
        """Retrieve a registered collector by name.

        :param name: The collector identifier.
        :return: The collector instance.
        :raises KeyError: If no collector is registered under the given name.
        """
        return self._collectors[name]

    async def get_stats(self) -> None:
        """Fetch and aggregate general repository statistics from GitHub."""
        await self._repo_stats.collect()

    @lazy_async_property("_repo_stats.name", "get_stats")
    async def get_name(self) -> str:
        """Retrieve the GitHub user's name or login.

        :return: The user's name, or login if name is not available.
        """
        return "No Name"

    @lazy_async_property("_repo_stats.stargazers", "get_stats")
    async def get_stargazers(self) -> int:
        """Retrieve the total number of stargazers across repositories.

        :return: Total stargazer count.
        """
        return 0

    @lazy_async_property("_repo_stats.forks", "get_stats")
    async def get_forks(self) -> int:
        """Retrieve the total number of forks across repositories.

        :return: Total fork count.
        """
        return 0

    @lazy_async_property("_repo_stats.languages", "get_stats")
    async def get_languages(self) -> Dict[str, Any]:
        """Retrieve a summary of languages used across repositories.

        :return: A dictionary containing language stats (size, occurrences, color).
        """
        return {}

    async def get_languages_proportional(self) -> Dict[str, float]:
        """Retrieve a summary of language usage as percentages.

        :return: A dictionary mapping language names to their usage percentage.
        """
        langs = await self.get_languages()
        return {k: v.get("prop", 0) for (k, v) in langs.items()}

    @lazy_async_property("_repo_stats.repos", "get_stats")
    async def get_repos(self) -> Set[str]:
        """Retrieve the set of names for all processed repositories.

        :return: A set of repository names in 'owner/repo' format.
        """
        return set()

    async def get_total_contributions(self) -> int:
        """Retrieve the total number of contributions as defined by GitHub.

        :return: Total contribution count.
        """
        return await self._contributions.fetch_total_contributions()

    async def get_lines_changed(self) -> Tuple[int, int]:
        """Calculate the total lines added and deleted by the user.

        :return: A tuple containing (total_additions, total_deletions) by the user.
        """
        repos = await self.get_repos()
        empty = self._repo_stats.empty_repos or set()
        return await self._code_changes.analyze(repos, empty)

    @lazy_async_property("_code_changes.contributions_percentage", "get_lines_changed")
    async def get_contributions_percentage(self) -> str:
        """Retrieve the percentage of code changes made by the user.

        :return: A formatted percentage string (e.g., '25.00%').
        """
        return "0.00%"

    @lazy_async_property("_code_changes.avg_percent", "get_lines_changed")
    async def get_avg_contribution_percent(self) -> str:
        """Retrieve the average percentage of contributions per repository.

        :return: A formatted percentage string (e.g., '10.50%').
        """
        return "0.00%"

    @lazy_async_property("_code_changes.contributors", "get_lines_changed")
    async def get_contributors(self) -> Set[str]:
        """Retrieve the set of unique contributors across all repositories.

        :return: A set of contributor usernames.
        """
        return set()

    async def get_views(self) -> int:
        """Retrieve the cumulative count of repository views.

        :return: Total repository view count.
        """
        repos = await self.get_repos()
        return await self._traffic.fetch_views(repos)

    @lazy_async_property("_traffic.views_from_date", "get_views")
    async def get_views_from_date(self) -> str:
        """Retrieve the starting date from which repository views are counted.

        :return: A date string in 'YYYY-MM-DD' format.
        """
        return "0000-00-00"

    async def get_clones(self) -> int:
        """Retrieve the cumulative count of repository clones.

        :return: Total repository clone count.
        """
        repos = await self.get_repos()
        return await self._traffic.fetch_clones(repos)

    @lazy_async_property("_traffic.clones_from_date", "get_clones")
    async def get_clones_from_date(self) -> str:
        """Retrieve the starting date from which repository clones are counted.

        :return: A date string in 'YYYY-MM-DD' format.
        """
        return "0000-00-00"

    async def get_collaborators(self) -> int:
        """Retrieve the total number of unique collaborators.

        :return: Total collaborator count.
        """
        repos = await self.get_repos()
        contributors = await self.get_contributors()
        return await self._engagement.fetch_collaborators(repos, contributors)

    async def get_pull_requests(self) -> int:
        """Retrieve the total number of pull requests across all repositories.

        :return: Total pull request count.
        """
        repos = await self.get_repos()
        return await self._engagement.fetch_pull_requests(repos)

    async def get_issues(self) -> int:
        """Retrieve the total number of issues across all repositories.

        :return: Total issue count (excluding pull requests).
        """
        repos = await self.get_repos()
        return await self._engagement.fetch_issues(repos)

    async def get_contribution_calendar(self) -> None:
        """Fetch the contribution calendar data and calculate streak information."""
        await self._contributions.fetch_contribution_calendar()

    @lazy_async_property("_contributions.current_streak", "get_contribution_calendar")
    async def get_current_streak(self) -> int:
        """Retrieve the current contribution streak in days.

        :return: Number of consecutive days with contributions.
        """
        return 0

    @lazy_async_property("_contributions.longest_streak", "get_contribution_calendar")
    async def get_longest_streak(self) -> int:
        """Retrieve the longest contribution streak in days.

        :return: Maximum number of consecutive days with contributions.
        """
        return 0

    @lazy_async_property("_contributions.current_streak_range", "get_contribution_calendar")
    async def get_current_streak_range(self) -> str:
        """Retrieve the date range of the current streak.

        :return: Formatted date range string.
        """
        return "No streak"

    @lazy_async_property("_contributions.longest_streak_range", "get_contribution_calendar")
    async def get_longest_streak_range(self) -> str:
        """Retrieve the date range of the longest streak.

        :return: Formatted date range string.
        """
        return "No streak"

    async def get_recent_contributions(self) -> list:
        """Retrieve the contribution counts for the last 10 days.

        :return: List of contribution counts (most recent last).
        """
        await self.get_contribution_calendar()
        return self._contributions.get_recent_contributions()

    async def get_weekly_commit_schedule(self) -> list:
        """Retrieve commit-level events for the current week.

        :return: List of commit event dictionaries.
        """
        repos = await self.get_repos()
        return await self._commit_schedule.fetch_weekly_schedule(
            repos=repos,
            username=self.environment_vars.username,
            timezone_name=self.environment_vars.timezone,
        )
