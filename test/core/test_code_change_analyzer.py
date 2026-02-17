"""Async tests for CodeChangeAnalyzer."""

import pytest
from unittest.mock import AsyncMock

from src.core.code_change_analyzer import CodeChangeAnalyzer


class TestCodeChangeAnalyzer:
    """Tests for lines changed, contributors and percentages."""

    def _contributor_response(self, authors):
        """Build a /stats/contributors-style response.

        :param authors: List of (login, additions, deletions) tuples.
        """
        result = []
        for login, adds, dels in authors:
            result.append({
                "author": {"login": login},
                "weeks": [{"a": adds, "d": dels, "c": 5}],
            })
        return result

    async def test_analyze_single_repo(self, mock_github_client):
        """User lines are counted correctly for a single repo."""
        mock_github_client.query_rest.return_value = self._contributor_response([
            ("testuser", 100, 20),
            ("other", 50, 10),
        ])
        analyzer = CodeChangeAnalyzer("testuser", mock_github_client)
        adds, dels = await analyzer.analyze({"user/repo-a"}, set())

        assert adds == 100
        assert dels == 20
        assert analyzer.contributors == {"testuser", "other"}

    async def test_analyze_multiple_repos(self, mock_github_client):
        """Lines are aggregated across multiple repositories."""
        mock_github_client.query_rest.side_effect = [
            self._contributor_response([("testuser", 100, 20)]),
            self._contributor_response([("testuser", 200, 30)]),
        ]
        analyzer = CodeChangeAnalyzer("testuser", mock_github_client)
        adds, dels = await analyzer.analyze({"user/repo-a", "user/repo-b"}, set())

        assert adds == 300
        assert dels == 50

    async def test_empty_repos_skipped(self, mock_github_client):
        """Repositories in empty_repos set are not queried."""
        mock_github_client.query_rest.return_value = self._contributor_response([
            ("testuser", 10, 5),
        ])
        analyzer = CodeChangeAnalyzer("testuser", mock_github_client)
        await analyzer.analyze({"user/repo-a", "user/empty"}, {"user/empty"})

        assert mock_github_client.query_rest.call_count == 1

    async def test_cached_result(self, mock_github_client):
        """Second call returns cached result without new API calls."""
        mock_github_client.query_rest.return_value = self._contributor_response([
            ("testuser", 10, 5),
        ])
        analyzer = CodeChangeAnalyzer("testuser", mock_github_client)
        first = await analyzer.analyze({"user/repo-a"}, set())
        second = await analyzer.analyze({"user/repo-a"}, set())

        assert first == second
        assert mock_github_client.query_rest.call_count == 1

    async def test_api_error_handled(self, mock_github_client):
        """Repo failures do not crash; they are skipped."""
        mock_github_client.query_rest.side_effect = Exception("timeout")
        analyzer = CodeChangeAnalyzer("testuser", mock_github_client)
        adds, dels = await analyzer.analyze({"user/repo-a"}, set())

        assert adds == 0
        assert dels == 0

    async def test_contribution_percentage(self, mock_github_client):
        """Contribution percentage is calculated correctly."""
        mock_github_client.query_rest.return_value = self._contributor_response([
            ("testuser", 80, 20),
            ("other", 80, 20),
        ])
        analyzer = CodeChangeAnalyzer("testuser", mock_github_client)
        await analyzer.analyze({"user/repo-a"}, set())

        assert analyzer.contributions_percentage is not None
        assert "%" in analyzer.contributions_percentage

    async def test_no_repos(self, mock_github_client):
        """Empty repos set returns zero lines."""
        analyzer = CodeChangeAnalyzer("testuser", mock_github_client)
        adds, dels = await analyzer.analyze(set(), set())

        assert adds == 0
        assert dels == 0
        assert mock_github_client.query_rest.call_count == 0
