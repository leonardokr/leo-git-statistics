"""Async tests for ContributionTracker."""

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock

from src.core.contribution_tracker import ContributionTracker


class TestContributionTracker:
    """Tests for contribution calendar and streak calculations."""

    def _years_response(self, years):
        return {
            "data": {
                "viewer": {
                    "contributionsCollection": {
                        "contributionYears": years,
                    },
                },
            },
        }

    def _contributions_response(self, year_data):
        viewer = {}
        for year, total in year_data.items():
            viewer[f"year_{year}"] = {
                "contributionCalendar": {"totalContributions": total},
            }
        return {"data": {"viewer": viewer}}

    def _calendar_response(self, days):
        return {
            "data": {
                "viewer": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "weeks": [{"contributionDays": days}],
                        },
                    },
                },
            },
        }

    async def test_fetch_total_contributions(self, mock_github_client):
        """Total contributions are summed across all years."""
        mock_github_client.query.side_effect = [
            self._years_response([2025, 2026]),
            self._contributions_response({2025: 500, 2026: 200}),
        ]
        tracker = ContributionTracker(mock_github_client)
        total = await tracker.fetch_total_contributions()

        assert total == 700

    async def test_total_contributions_cached(self, mock_github_client):
        """Second call returns cached value without new API call."""
        mock_github_client.query.side_effect = [
            self._years_response([2026]),
            self._contributions_response({2026: 300}),
        ]
        tracker = ContributionTracker(mock_github_client)
        first = await tracker.fetch_total_contributions()
        second = await tracker.fetch_total_contributions()

        assert first == second == 300
        assert mock_github_client.query.call_count == 2

    async def test_streak_calculation(self, mock_github_client):
        """Current and longest streaks are calculated from calendar data."""
        today = date.today()
        days = []
        for i in range(10, -1, -1):
            d = today - timedelta(days=i)
            days.append({
                "date": d.strftime("%Y-%m-%d"),
                "contributionCount": 1 if i <= 4 else 0,
            })

        mock_github_client.query.side_effect = [
            self._years_response([today.year]),
            self._calendar_response(days),
        ]
        tracker = ContributionTracker(mock_github_client)
        await tracker.fetch_contribution_calendar()

        assert tracker.current_streak == 5
        assert tracker.longest_streak == 5

    async def test_no_contributions_zero_streak(self, mock_github_client):
        """All-zero calendar produces zero streaks."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        days = [
            {"date": (today - timedelta(days=i)).strftime("%Y-%m-%d"), "contributionCount": 0}
            for i in range(5, -1, -1)
        ]
        mock_github_client.query.side_effect = [
            self._years_response([today.year]),
            self._calendar_response(days),
        ]
        tracker = ContributionTracker(mock_github_client)
        await tracker.fetch_contribution_calendar()

        assert tracker.current_streak == 0
        assert tracker.longest_streak == 0
        assert tracker.current_streak_range == "No streak"

    async def test_recent_contributions(self, mock_github_client):
        """get_recent_contributions returns last 10 days of counts."""
        today = date.today()
        days = [
            {"date": (today - timedelta(days=i)).strftime("%Y-%m-%d"), "contributionCount": i}
            for i in range(15, -1, -1)
        ]
        mock_github_client.query.side_effect = [
            self._years_response([today.year]),
            self._calendar_response(days),
        ]
        tracker = ContributionTracker(mock_github_client)
        await tracker.fetch_contribution_calendar()
        recent = tracker.get_recent_contributions()

        assert len(recent) == 10

    async def test_empty_calendar(self, mock_github_client):
        """Handles empty years list gracefully."""
        mock_github_client.query.side_effect = [
            self._years_response([]),
        ]
        tracker = ContributionTracker(mock_github_client)
        await tracker.fetch_contribution_calendar()

        assert tracker.current_streak == 0
        assert tracker.longest_streak == 0
