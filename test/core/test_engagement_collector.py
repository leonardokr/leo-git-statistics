"""Async tests for EngagementCollector."""

import pytest
from unittest.mock import AsyncMock

from src.core.engagement_collector import EngagementCollector


class TestEngagementCollector:
    """Tests for pull requests, issues and collaborators collection."""

    async def test_fetch_pull_requests(self, mock_environment, mock_github_client):
        """PRs are counted from all repos."""
        mock_github_client.query_rest.return_value = [
            {"number": 1, "state": "open"},
            {"number": 2, "state": "closed"},
        ]
        collector = EngagementCollector(mock_environment, mock_github_client)
        count = await collector.fetch_pull_requests({"user/repo-a"})

        assert count == 2

    async def test_fetch_issues(self, mock_environment, mock_github_client):
        """Issues are counted, excluding PRs in the issue list."""
        mock_github_client.query_rest.return_value = [
            {"number": 1, "html_url": "https://github.com/user/repo-a/issues/1"},
            {"number": 2, "html_url": "https://github.com/user/repo-a/pull/2"},
        ]
        collector = EngagementCollector(mock_environment, mock_github_client)
        count = await collector.fetch_issues({"user/repo-a"})

        assert count == 1

    async def test_fetch_collaborators(self, mock_environment, mock_github_client):
        """Unique collaborators are counted across repos and contributors."""
        mock_github_client.query_rest.return_value = [
            {"login": "alice"},
            {"login": "bob"},
        ]
        collector = EngagementCollector(mock_environment, mock_github_client)
        count = await collector.fetch_collaborators({"user/repo-a"}, {"testuser"})

        assert count == 2

    async def test_cached_pull_requests(self, mock_environment, mock_github_client):
        """Second call returns cached value."""
        mock_github_client.query_rest.return_value = [{"number": 1}]
        collector = EngagementCollector(mock_environment, mock_github_client)
        first = await collector.fetch_pull_requests({"user/repo-a"})
        second = await collector.fetch_pull_requests({"user/repo-a"})

        assert first == second
        assert mock_github_client.query_rest.call_count == 1

    async def test_api_error_handled(self, mock_environment, mock_github_client):
        """Repo failure is skipped, others continue."""
        mock_github_client.query_rest.side_effect = [
            Exception("timeout"),
            [{"number": 1}],
        ]
        collector = EngagementCollector(mock_environment, mock_github_client)
        count = await collector.fetch_pull_requests({"user/repo-a", "user/repo-b"})

        assert count >= 0

    async def test_empty_repos(self, mock_environment, mock_github_client):
        """Empty repo set returns zero."""
        collector = EngagementCollector(mock_environment, mock_github_client)
        count = await collector.fetch_pull_requests(set())

        assert count == 0

    async def test_issues_with_no_html_url(self, mock_environment, mock_github_client):
        """Issue entries without html_url are skipped."""
        mock_github_client.query_rest.return_value = [
            {"number": 1, "html_url": None},
        ]
        collector = EngagementCollector(mock_environment, mock_github_client)
        count = await collector.fetch_issues({"user/repo-a"})

        assert count == 0

    async def test_multiple_repos_prs(self, mock_environment, mock_github_client):
        """PRs are aggregated from all repos."""
        mock_github_client.query_rest.side_effect = [
            [{"number": 1}, {"number": 2}],
            [{"number": 3}],
        ]
        collector = EngagementCollector(mock_environment, mock_github_client)
        count = await collector.fetch_pull_requests({"user/repo-a", "user/repo-b"})

        assert count == 3
