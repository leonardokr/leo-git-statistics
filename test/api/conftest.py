"""Shared fixtures for API integration tests."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("API_AUTH_ENABLED", "false")
os.environ.setdefault("RATE_LIMIT_DEFAULT", "9999/minute")
os.environ.setdefault("RATE_LIMIT_AUTH", "9999/minute")
os.environ.setdefault("RATE_LIMIT_HEAVY", "9999/minute")


def _make_mock_collector():
    """Build a StatsCollector mock with sensible defaults."""
    collector = AsyncMock()
    collector.get_name.return_value = "Test User"
    collector.get_total_contributions.return_value = 1200
    collector.get_repos.return_value = {"user/repo-a", "user/repo-b"}
    collector.get_stargazers.return_value = 42
    collector.get_forks.return_value = 10
    collector.get_views.return_value = 500
    collector.get_views_from_date.return_value = "2025-01-01"
    collector.get_clones.return_value = 80
    collector.get_clones_from_date.return_value = "2025-01-01"
    collector.get_pull_requests.return_value = 15
    collector.get_issues.return_value = 8
    collector.get_lines_changed.return_value = (5000, 2000)
    collector.get_avg_contribution_percent.return_value = "65.00%"
    collector.get_collaborators.return_value = 5
    collector.get_contributors.return_value = {"alice", "bob"}
    collector.get_languages.return_value = {
        "Python": {"size": 8000, "occurrences": 3, "color": "#3572A5", "prop": 80.0},
        "Shell": {"size": 2000, "occurrences": 1, "color": "#89e051", "prop": 20.0},
    }
    collector.get_languages_proportional.return_value = {"Python": 80.0, "Shell": 20.0}
    collector.get_current_streak.return_value = 7
    collector.get_current_streak_range.return_value = "Feb 10 - Feb 17, 2026"
    collector.get_longest_streak.return_value = 30
    collector.get_longest_streak_range.return_value = "Jan 01 - Jan 30, 2026"
    collector.get_recent_contributions.return_value = [1, 3, 0, 5, 2, 4, 7, 1, 0, 3]
    collector.get_weekly_commit_schedule.return_value = [
        {"repo": "user/repo-a", "sha": "abc1234", "description": "feat: init", "is_private": False, "timestamp": "2026-02-16T10:00:00+00:00"},
    ]
    return collector


@pytest.fixture()
def mock_collector():
    """Return a fresh mock StatsCollector instance."""
    return _make_mock_collector()


@pytest.fixture()
async def client(mock_collector):
    """Provide an httpx AsyncClient wired to the FastAPI app with mocked deps."""
    mock_session = MagicMock()

    with (
        patch("api.routes.users.create_stats_collector", return_value=mock_collector),
        patch("api.routes.cards.create_stats_collector", return_value=mock_collector),
        patch("api.routes.compare.create_stats_collector", return_value=mock_collector),
        patch("api.routes.history.create_stats_collector", return_value=mock_collector),
        patch("api.routes.users.cache_get", return_value=(False, None)),
        patch("api.routes.users.cache_set"),
        patch("api.routes.cards.cache_get", return_value=(False, None)),
        patch("api.routes.cards.cache_set"),
        patch("api.routes.compare.cache_get", return_value=(False, None)),
        patch("api.routes.compare.cache_set"),
        patch("api.deps.cache.cache_stats", return_value={
            "backend": "memory", "entries": 0, "maxsize": 100,
            "hits": 0, "misses": 0, "hit_ratio": 0.0,
        }),
    ):
        from api.main import app
        from api.deps.http_session import get_shared_session

        app.dependency_overrides[get_shared_session] = lambda: mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.pop(get_shared_session, None)
