"""Contribution calendar, streaks and total contributions tracking."""

import logging
from typing import Dict, List, Optional, Any, cast
from datetime import date, timedelta

from src.core.github_client import GitHubClient
from src.core.graphql_queries import GraphQLQueries

logger = logging.getLogger(__name__)


class ContributionTracker:
    """
    Tracks contribution calendar data and calculates streak information.

    :param queries: GitHub API client instance.
    """

    __DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, queries: GitHubClient):
        self._queries = queries

        self._total_contributions: Optional[int] = None
        self._current_streak: Optional[int] = None
        self._longest_streak: Optional[int] = None
        self._current_streak_range: Optional[str] = None
        self._longest_streak_range: Optional[str] = None
        self._contribution_calendar: Optional[Dict[str, Any]] = None

    @property
    def total_contributions(self) -> Optional[int]:
        return self._total_contributions

    @property
    def current_streak(self) -> Optional[int]:
        return self._current_streak

    @property
    def longest_streak(self) -> Optional[int]:
        return self._longest_streak

    @property
    def current_streak_range(self) -> Optional[str]:
        return self._current_streak_range

    @property
    def longest_streak_range(self) -> Optional[str]:
        return self._longest_streak_range

    @property
    def contribution_calendar(self) -> Optional[Dict[str, Any]]:
        return self._contribution_calendar

    async def fetch_total_contributions(self) -> int:
        """
        Retrieve the total number of contributions as defined by GitHub.

        :return: Total contribution count.
        """
        if self._total_contributions is not None:
            return self._total_contributions
        self._total_contributions = 0

        years = (
            (await self._queries.query(GraphQLQueries.contributions_all_years()))
            .get("data", {})
            .get("viewer", {})
            .get("contributionsCollection", {})
            .get("contributionYears", [])
        )

        by_year = (
            (await self._queries.query(GraphQLQueries.all_contributions(years)))
            .get("data", {})
            .get("viewer", {})
            .values()
        )

        for year in by_year:
            self._total_contributions += year.get("contributionCalendar", {}).get(
                "totalContributions", 0
            )
        return cast(int, self._total_contributions)

    async def fetch_contribution_calendar(self) -> None:
        """
        Fetch the contribution calendar data and calculate streak information.

        Queries GitHub's GraphQL API for contribution data and calculates
        both current and longest contribution streaks.
        """
        if self._contribution_calendar is not None:
            return

        years = (
            (await self._queries.query(GraphQLQueries.contributions_all_years()))
            .get("data", {})
            .get("viewer", {})
            .get("contributionsCollection", {})
            .get("contributionYears", [])
        )

        all_days: List[Dict[str, Any]] = []
        for year in years:
            query = f"""
            {{
              viewer {{
                contributionsCollection(from: "{year}-01-01T00:00:00Z", to: "{year}-12-31T23:59:59Z") {{
                  contributionCalendar {{
                    weeks {{
                      contributionDays {{
                        contributionCount
                        date
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            result = await self._queries.query(query)
            weeks = (
                result.get("data", {})
                .get("viewer", {})
                .get("contributionsCollection", {})
                .get("contributionCalendar", {})
                .get("weeks", [])
            )

            for week in weeks:
                for day in week.get("contributionDays", []):
                    all_days.append(
                        {"date": day.get("date"), "count": day.get("contributionCount", 0)}
                    )

        all_days.sort(key=lambda x: x["date"])

        if all_days:
            logger.debug(
                "Contribution calendar: %d days, last 10: %s",
                len(all_days),
                all_days[-10:],
            )

        current_streak = 0
        longest_streak = 0
        current_streak_start = None
        current_streak_end = None
        longest_streak_start = None
        longest_streak_end = None
        temp_streak = 0
        temp_streak_start = None

        today = date.today().strftime(self.__DATE_FORMAT)

        for i, day in enumerate(all_days):
            if day["count"] > 0:
                if temp_streak == 0:
                    temp_streak_start = day["date"]
                temp_streak += 1

                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                    longest_streak_start = temp_streak_start
                    longest_streak_end = day["date"]

                if day["date"] == today or (i == len(all_days) - 1):
                    current_streak = temp_streak
                    current_streak_start = temp_streak_start
                    current_streak_end = day["date"]
            else:
                if i < len(all_days) - 1 or day["date"] == today:
                    temp_streak = 0
                    temp_streak_start = None

        yesterday = (date.today() - timedelta(1)).strftime(self.__DATE_FORMAT)
        if all_days and all_days[-1]["date"] < yesterday:
            current_streak = 0
            current_streak_start = None
            current_streak_end = None

        self._current_streak = current_streak
        self._longest_streak = longest_streak
        self._current_streak_range = self._format_date_range(
            current_streak_start, current_streak_end
        )
        self._longest_streak_range = self._format_date_range(
            longest_streak_start, longest_streak_end
        )
        self._contribution_calendar = {"days": all_days}

    def get_recent_contributions(self) -> list:
        """
        Retrieve the contribution counts for the last 10 days.

        :return: List of contribution counts (most recent last).
        """
        days = self._contribution_calendar.get("days", [])
        today = date.today().strftime(self.__DATE_FORMAT)
        past_days = [d for d in days if d["date"] <= today]
        recent = past_days[-10:] if len(past_days) >= 10 else past_days
        return [day.get("count", 0) for day in recent]

    @staticmethod
    def _format_date_range(start: Optional[str], end: Optional[str]) -> str:
        """
        Format a date range for display.

        :param start: Start date string in YYYY-MM-DD format.
        :param end: End date string in YYYY-MM-DD format.
        :return: Formatted date range string.
        """
        if not start or not end:
            return "No streak"

        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            start_fmt = start_date.strftime("%b %d")
            end_fmt = end_date.strftime("%b %d, %Y")

            if start_date.year != end_date.year:
                start_fmt = start_date.strftime("%b %d, %Y")

            return f"{start_fmt} - {end_fmt}"
        except ValueError:
            return "No streak"
