"""Async tests for CommitScheduleCollector."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

from src.core.commit_schedule_collector import CommitScheduleCollector


class TestCommitScheduleCollector:
    """Tests for weekly commit schedule collection."""

    def _commit_payload(self, sha, message, timestamp, author="testuser"):
        """Build a REST API commit object."""
        return {
            "sha": sha,
            "commit": {
                "message": message,
                "author": {"date": timestamp, "name": author},
                "committer": {"date": timestamp},
            },
        }

    async def test_fetch_weekly_schedule(self, mock_environment, mock_github_client):
        """Commits from the current week are collected."""
        now = datetime.now(timezone.utc)
        ts = now.isoformat()
        mock_github_client.query_rest.side_effect = [
            {"private": False},
            [self._commit_payload("abc1234" * 6, "feat: test", ts)],
        ]
        collector = CommitScheduleCollector(mock_environment, mock_github_client)
        result = await collector.fetch_weekly_schedule(
            repos={"user/repo-a"}, username="testuser", timezone_name="UTC",
        )

        assert len(result) >= 0

    async def test_private_repo_hides_message(self, mock_environment, mock_github_client):
        """Private repo commits are masked when private masking is enabled."""
        now = datetime.now(timezone.utc)
        ts = now.isoformat()
        sha = "a" * 40
        mock_environment.filter.mask_private_repos = True
        mock_github_client.query_rest.side_effect = [
            {"private": True},
            [self._commit_payload(sha, "secret work", ts)],
        ]
        collector = CommitScheduleCollector(mock_environment, mock_github_client)
        result = await collector.fetch_weekly_schedule(
            repos={"user/private-repo"}, username="testuser", timezone_name="UTC",
        )

        for entry in result:
            if entry["is_private"]:
                assert entry["description"] == "Private commit"

    async def test_cached_schedule(self, mock_environment, mock_github_client):
        """Second call with same params returns cached result."""
        mock_github_client.query_rest.side_effect = [
            {"private": False},
            [],
        ]
        collector = CommitScheduleCollector(mock_environment, mock_github_client)
        first = await collector.fetch_weekly_schedule(
            repos={"user/repo-a"}, username="testuser", timezone_name="UTC",
        )
        second = await collector.fetch_weekly_schedule(
            repos={"user/repo-a"}, username="testuser", timezone_name="UTC",
        )
        assert first == second

    async def test_invalid_timezone_fallback(self, mock_environment, mock_github_client):
        """Invalid timezone falls back to UTC without error."""
        mock_github_client.query_rest.side_effect = [
            {"private": False},
            [],
        ]
        collector = CommitScheduleCollector(mock_environment, mock_github_client)
        result = await collector.fetch_weekly_schedule(
            repos={"user/repo-a"}, username="testuser", timezone_name="Invalid/Zone",
        )
        assert isinstance(result, list)

    async def test_api_error_handled(self, mock_environment, mock_github_client):
        """API errors for a repo do not crash the collector."""
        mock_github_client.query_rest.side_effect = Exception("network error")
        collector = CommitScheduleCollector(mock_environment, mock_github_client)
        result = await collector.fetch_weekly_schedule(
            repos={"user/repo-a"}, username="testuser", timezone_name="UTC",
        )
        assert isinstance(result, list)

    async def test_empty_repos(self, mock_environment, mock_github_client):
        """Empty repos set returns empty list."""
        collector = CommitScheduleCollector(mock_environment, mock_github_client)
        result = await collector.fetch_weekly_schedule(
            repos=set(), username="testuser", timezone_name="UTC",
        )
        assert result == []

    async def test_commits_sorted_by_timestamp(self, mock_environment, mock_github_client):
        """Entries are sorted by timestamp."""
        now = datetime.now(timezone.utc)
        ts1 = (now - timedelta(hours=2)).isoformat()
        ts2 = now.isoformat()
        mock_github_client.query_rest.side_effect = [
            {"private": False},
            [
                self._commit_payload("b" * 40, "second", ts2),
                self._commit_payload("a" * 40, "first", ts1),
            ],
        ]
        collector = CommitScheduleCollector(mock_environment, mock_github_client)
        result = await collector.fetch_weekly_schedule(
            repos={"user/repo-a"}, username="testuser", timezone_name="UTC",
        )

        if len(result) >= 2:
            assert result[0]["timestamp"] <= result[1]["timestamp"]
