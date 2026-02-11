"""Code change analysis: lines changed, contributors and percentages."""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from src.core.github_client import GitHubClient

logger = logging.getLogger(__name__)


def _ensure_list(data: Union[Dict, List, Any]) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "message" in data:
        logger.warning("API returned error response: %s", data.get("message"))
    return []


class CodeChangeAnalyzer:
    """
    Analyses lines changed, contribution percentages and contributor sets.

    :param username: GitHub username whose changes are tracked.
    :param queries: GitHub API client instance.
    """

    def __init__(self, username: str, queries: GitHubClient):
        self._username = username
        self._queries = queries

        self._users_lines_changed: Optional[Tuple[int, int]] = None
        self._total_lines_changed: Optional[Tuple[int, int]] = None
        self._contributions_percentage: Optional[str] = None
        self._avg_percent: Optional[str] = None
        self._contributors: Optional[Set[str]] = None

    @property
    def users_lines_changed(self) -> Optional[Tuple[int, int]]:
        return self._users_lines_changed

    @property
    def total_lines_changed(self) -> Optional[Tuple[int, int]]:
        return self._total_lines_changed

    @property
    def contributions_percentage(self) -> Optional[str]:
        return self._contributions_percentage

    @property
    def avg_percent(self) -> Optional[str]:
        return self._avg_percent

    @property
    def contributors(self) -> Optional[Set[str]]:
        return self._contributors

    async def analyze(self, repos: Set[str], empty_repos: Set[str]) -> Tuple[int, int]:
        """
        Calculate lines added and deleted by the user across repositories.

        Also populates total lines changed, contribution percentages and
        contributor set as side-effects.

        :param repos: Set of repository names to analyze.
        :param empty_repos: Set of empty repository names to skip.
        :return: Tuple of (user_additions, user_deletions).
        """
        if self._users_lines_changed is not None:
            return self._users_lines_changed

        contributor_set: Set[str] = set()
        total_additions = 0
        total_deletions = 0
        additions = 0
        deletions = 0
        total_percentage = 0.0

        for repo in repos:
            if repo in empty_repos:
                continue
            repo_total_changes = 0
            author_total_changes = 0

            r = _ensure_list(await self._queries.query_rest(f"/repos/{repo}/stats/contributors"))

            for author_obj in r:
                if not isinstance(author_obj, dict) or not isinstance(
                    author_obj.get("author", {}), dict
                ):
                    continue
                author = author_obj.get("author", {}).get("login", "")
                contributor_set.add(author)

                if author != self._username:
                    for week in author_obj.get("weeks", []):
                        total_additions += week.get("a", 0)
                        total_deletions += week.get("d", 0)
                        repo_total_changes += week.get("a", 0)
                        repo_total_changes += week.get("d", 0)
                else:
                    for week in author_obj.get("weeks", []):
                        additions += week.get("a", 0)
                        deletions += week.get("d", 0)
                        author_total_changes += week.get("a", 0)
                        author_total_changes += week.get("d", 0)

            repo_total_changes += author_total_changes
            if author_total_changes > 0:
                total_percentage += author_total_changes / repo_total_changes

        non_empty_count = len(repos) - len(empty_repos)
        if total_percentage > 0 and non_empty_count > 0:
            total_percentage /= non_empty_count
        else:
            total_percentage = 0.0
        self._avg_percent = f"{total_percentage * 100:0.2f}%"

        total_additions += additions
        total_deletions += deletions
        self._users_lines_changed = (additions, deletions)
        self._total_lines_changed = (total_additions, total_deletions)

        if sum(self._users_lines_changed) > 0:
            ttl_changes = sum(self._total_lines_changed)
            user_changes = sum(self._users_lines_changed)
            percent_contribs = user_changes / ttl_changes * 100
        else:
            percent_contribs = 0.0
        self._contributions_percentage = f"{percent_contribs:0.2f}%"

        self._contributors = contributor_set

        return self._users_lines_changed
