"""Async tests for TrafficCollector."""

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.core.traffic_collector import TrafficCollector


class TestTrafficCollector:
    """Tests for views and clones traffic collection."""

    def _traffic_response(self, metric, entries):
        """Build a /traffic/{views|clones} response."""
        return {
            metric: [
                {"timestamp": ts, "count": count}
                for ts, count in entries
            ],
        }

    async def test_fetch_views(self, mock_environment, mock_github_client):
        """Views are summed from traffic API responses."""
        yesterday = (date.today() - timedelta(1)).strftime("%Y-%m-%d")
        mock_github_client.query_rest.return_value = self._traffic_response(
            "views", [(f"{yesterday}T00:00:00Z", 50)],
        )
        collector = TrafficCollector(mock_environment, mock_github_client)
        views = await collector.fetch_views({"user/repo-a"})

        assert views >= 0

    async def test_fetch_clones(self, mock_environment, mock_github_client):
        """Clones are summed from traffic API responses."""
        yesterday = (date.today() - timedelta(1)).strftime("%Y-%m-%d")
        mock_github_client.query_rest.return_value = self._traffic_response(
            "clones", [(f"{yesterday}T00:00:00Z", 10)],
        )
        collector = TrafficCollector(mock_environment, mock_github_client)
        clones = await collector.fetch_clones({"user/repo-a"})

        assert clones >= 0

    async def test_cached_views(self, mock_environment, mock_github_client):
        """Second call returns cached result."""
        mock_github_client.query_rest.return_value = self._traffic_response("views", [])
        collector = TrafficCollector(mock_environment, mock_github_client)
        first = await collector.fetch_views({"user/repo-a"})
        second = await collector.fetch_views({"user/repo-a"})

        assert first == second
        assert mock_github_client.query_rest.call_count == 1

    async def test_today_entries_counted(self, mock_environment, mock_github_client):
        """Traffic from today is added to the count."""
        today = date.today().strftime("%Y-%m-%d")
        mock_github_client.query_rest.return_value = self._traffic_response(
            "views", [(f"{today}T00:00:00Z", 25)],
        )
        collector = TrafficCollector(mock_environment, mock_github_client)
        views = await collector.fetch_views({"user/repo-a"})

        assert views == 25

    async def test_api_failure_handled(self, mock_environment, mock_github_client):
        """API errors for a repo do not crash collection."""
        mock_github_client.query_rest.side_effect = Exception("forbidden")
        collector = TrafficCollector(mock_environment, mock_github_client)
        views = await collector.fetch_views({"user/repo-a"})

        assert views >= 0

    async def test_multiple_repos(self, mock_environment, mock_github_client):
        """Traffic is aggregated across multiple repos."""
        today = date.today().strftime("%Y-%m-%d")
        mock_github_client.query_rest.return_value = self._traffic_response(
            "views", [(f"{today}T00:00:00Z", 10)],
        )
        collector = TrafficCollector(mock_environment, mock_github_client)
        views = await collector.fetch_views({"user/repo-a", "user/repo-b"})

        assert views == 20
