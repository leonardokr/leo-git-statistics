"""Weekly commit schedule collection by repository."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import logging

from src.core.environment import Environment
from src.core.github_client import GitHubClient

logger = logging.getLogger(__name__)


class CommitScheduleCollector:
    """
    Collects weekly commit data grouped by repository.

    :param environment_vars: Environment settings and filters.
    :param queries: GitHub API client.
    """

    def __init__(self, environment_vars: Environment, queries: GitHubClient):
        self._env = environment_vars
        self._queries = queries
        self._visibility_cache: Dict[str, bool] = {}
        self._schedule_cache: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

    async def fetch_weekly_schedule(
        self, repos: Set[str], username: str, timezone_name: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch commits from current local week for all provided repositories.

        :param repos: Repository names in ``owner/repo`` format.
        :param username: GitHub username used to filter authored commits.
        :param timezone_name: IANA timezone used to define the current week.
        :return: List of commit dictionaries sorted by timestamp.
        """
        cache_key = (username, timezone_name)
        if cache_key in self._schedule_cache:
            return self._schedule_cache[cache_key]

        tz = self._resolve_timezone(timezone_name)
        now_local = datetime.now(tz)
        week_start_date = now_local.date() - timedelta(days=now_local.weekday())
        week_start_local = datetime.combine(week_start_date, time.min, tz)
        week_end_local = week_start_local + timedelta(days=7)

        since_utc = week_start_local.astimezone(timezone.utc).isoformat()
        until_utc = week_end_local.astimezone(timezone.utc).isoformat()

        entries: List[Dict[str, Any]] = []
        for repo in sorted(repos):
            is_private = await self._is_private_repo(repo)
            commits = await self._fetch_repo_commits(repo, username, since_utc, until_utc)
            for commit in commits:
                timestamp = self._extract_timestamp(commit)
                if timestamp is None:
                    continue

                local_dt = timestamp.astimezone(tz)
                if not (week_start_local <= local_dt < week_end_local):
                    continue

                sha = (commit.get("sha") or "")[:40]
                message = self._extract_message(commit)
                description = sha[:7] if is_private else message

                entries.append(
                    {
                        "repo": repo,
                        "sha": sha,
                        "description": description,
                        "is_private": is_private,
                        "timestamp": timestamp.isoformat(),
                    }
                )

        entries.sort(key=lambda item: item.get("timestamp", ""))
        self._schedule_cache[cache_key] = entries
        return entries

    async def _is_private_repo(self, repo: str) -> bool:
        """
        Resolve repository privacy and cache the result.

        :param repo: Repository full name.
        :return: ``True`` when repository is private.
        """
        if repo in self._visibility_cache:
            return self._visibility_cache[repo]

        result = await self._queries.query_rest(f"/repos/{repo}")
        is_private = bool(result.get("private")) if isinstance(result, dict) else False
        self._visibility_cache[repo] = is_private
        return is_private

    async def _fetch_repo_commits(
        self, repo: str, username: str, since_utc: str, until_utc: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch commits for a single repository in the requested time window.

        :param repo: Repository full name.
        :param username: GitHub username used in API filters.
        :param since_utc: Inclusive UTC start datetime string.
        :param until_utc: Exclusive UTC end datetime string.
        :return: List of commit payloads.
        """
        page = 1
        all_commits: List[Dict[str, Any]] = []

        while True:
            result = await self._queries.query_rest(
                f"/repos/{repo}/commits",
                params={
                    "author": username,
                    "since": since_utc,
                    "until": until_utc,
                    "per_page": 100,
                    "page": page,
                },
            )

            if not isinstance(result, list) or len(result) == 0:
                break

            all_commits.extend(result)
            if len(result) < 100:
                break
            page += 1

        return all_commits

    @staticmethod
    def _extract_message(commit_payload: Dict[str, Any]) -> str:
        """
        Extract first line of commit message.

        :param commit_payload: REST commit payload.
        :return: Sanitized first line or fallback text.
        """
        message = (
            commit_payload.get("commit", {})
            .get("message", "")
            .splitlines()
        )
        if len(message) == 0:
            return "Commit"
        return message[0][:120]

    @staticmethod
    def _extract_timestamp(commit_payload: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract commit timestamp from REST payload.

        :param commit_payload: REST commit payload.
        :return: Parsed timezone-aware datetime or ``None``.
        """
        commit_data = commit_payload.get("commit", {})
        author_date = commit_data.get("author", {}).get("date")
        committer_date = commit_data.get("committer", {}).get("date")
        source = author_date or committer_date
        if not source:
            return None
        try:
            return datetime.fromisoformat(source.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _resolve_timezone(timezone_name: str) -> ZoneInfo:
        """
        Resolve timezone name into :class:`zoneinfo.ZoneInfo`.

        :param timezone_name: IANA timezone name.
        :return: Resolved timezone.
        """
        try:
            return ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            logger.warning("Invalid timezone '%s'; falling back to UTC", timezone_name)
            return ZoneInfo("UTC")
