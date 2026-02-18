"""Integration tests for /users/<username>/* endpoints."""

import os

import pytest
from unittest.mock import AsyncMock, patch

# FIX: Inject tornado.gen into sys.modules to satisfy pybreaker's missing import
import sys
import tornado.gen as gen
sys.modules['gen'] = gen


class TestOverview:
    """Tests for GET /users/{username}/overview."""

    async def test_returns_overview_data(self, client):
        """Endpoint returns 200 with all overview fields."""
        resp = await client.get("/users/testuser/overview")
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "testuser"
        assert body["name"] == "Test User"
        assert body["total_contributions"] == 1200
        assert body["total_stars"] == 42
        assert body["total_forks"] == 10
        assert body["total_views"] == 500
        assert body["total_clones"] == 80
        assert body["total_pull_requests"] == 15
        assert body["total_issues"] == 8
        assert body["lines_added"] == 5000
        assert body["lines_deleted"] == 2000

    async def test_cache_miss_header(self, client):
        """First request sets X-Cache: MISS."""
        resp = await client.get("/users/testuser/overview")
        assert resp.headers.get("x-cache") == "MISS"

    async def test_cache_hit_returns_cached(self, client):
        """When cache has data, it is returned directly."""
        cached = {"username": "testuser", "name": "Cached"}
        with patch("api.routes.users.cache_get", return_value=(True, cached)):
            resp = await client.get("/users/testuser/overview")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Cached"
        assert resp.headers.get("x-cache") == "HIT"

    async def test_no_cache_param_bypasses_cache(self, client):
        """no_cache=true should skip cache lookup."""
        resp = await client.get("/users/testuser/overview?no_cache=true")
        assert resp.status_code == 200
        assert resp.headers.get("x-cache") == "MISS"

    async def test_invalid_username_returns_422(self, client):
        """Invalid GitHub username format returns 422."""
        resp = await client.get("/users/-invalid/overview")
        assert resp.status_code == 422

    async def test_username_too_long_returns_422(self, client):
        """Username exceeding 39 chars returns 422."""
        long_name = "a" * 40
        resp = await client.get(f"/users/{long_name}/overview")
        assert resp.status_code == 422

    async def test_partial_failure_includes_warnings(self, client, mock_collector):
        """When a collector call fails, warnings are returned."""
        mock_collector.get_views.side_effect = Exception("permission denied")
        with patch("api.routes.users.create_stats_collector", return_value=mock_collector):
            resp = await client.get("/users/testuser/overview")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_views"] is None
        assert any("views" in w for w in body.get("warnings", []))


class TestLanguages:
    """Tests for GET /users/{username}/languages."""

    async def test_returns_language_data(self, client):
        """Endpoint returns language distribution."""
        resp = await client.get("/users/testuser/languages")
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "testuser"
        assert "Python" in body["languages"]

    async def test_proportional_mode(self, client):
        """proportional=true returns percentage values."""
        resp = await client.get("/users/testuser/languages?proportional=true")
        assert resp.status_code == 200
        body = resp.json()
        assert body["languages"]["Python"] == 80.0


class TestStreak:
    """Tests for GET /users/{username}/streak."""

    async def test_returns_streak_data(self, client):
        """Endpoint returns streak information."""
        resp = await client.get("/users/testuser/streak")
        assert resp.status_code == 200
        body = resp.json()
        assert body["current_streak"] == 7
        assert body["longest_streak"] == 30
        assert "current_streak_range" in body
        assert "longest_streak_range" in body


class TestRecentContributions:
    """Tests for GET /users/{username}/contributions/recent."""

    async def test_returns_recent_contributions(self, client):
        """Endpoint returns list of recent contribution counts."""
        resp = await client.get("/users/testuser/contributions/recent")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["recent_contributions"]) == 10


class TestWeeklyCommits:
    """Tests for GET /users/{username}/commits/weekly."""

    async def test_returns_weekly_commits(self, client):
        """Endpoint returns weekly commit schedule."""
        resp = await client.get("/users/testuser/commits/weekly")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["weekly_commits"]) == 1
        assert body["weekly_commits"][0]["repo"] == "user/repo-a"


class TestRepositories:
    """Tests for GET /users/{username}/repositories."""

    async def test_returns_paginated_repos(self, client):
        """Endpoint returns paginated repository list."""
        resp = await client.get("/users/testuser/repositories")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "pagination" in body
        assert body["pagination"]["total"] == 2

    async def test_pagination_params(self, client):
        """Custom page/per_page are respected."""
        resp = await client.get("/users/testuser/repositories?page=1&per_page=1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["per_page"] == 1
        assert body["pagination"]["has_next"] is True


class TestRepositoriesDetailed:
    """Tests for GET /users/{username}/repositories/detailed."""

    async def test_returns_detailed_repos(self, client):
        """Endpoint returns detailed repository information."""
        mock_repos = [
            {
                "name": "repo-a",
                "full_name": "user/repo-a",
                "description": "A repo",
                "html_url": "https://github.com/user/repo-a",
                "homepage": "",
                "language": "Python",
                "stargazers_count": 10,
                "forks_count": 2,
                "open_issues_count": 1,
                "watchers_count": 10,
                "topics": ["python"],
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "pushed_at": "2026-01-01T00:00:00Z",
                "fork": False,
                "archived": False,
                "private": False,
            },
        ]
        mock_client = AsyncMock()
        mock_client.query_rest.side_effect = [mock_repos, {"Python": 5000}]

        with patch("api.routes.users.GitHubClient", return_value=mock_client):
            resp = await client.get("/users/testuser/repositories/detailed")

        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "repo-a"


class TestFullStats:
    """Tests for GET /users/{username}/stats/full."""

    async def test_returns_full_stats(self, client):
        """Endpoint returns aggregated statistics."""
        resp = await client.get("/users/testuser/stats/full")
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "testuser"
        assert "overview" in body
        assert "languages" in body
        assert "streak" in body
        assert "contributions" in body
        assert "repositories" in body
        assert "weekly_commits" in body


class TestAuth:
    """Tests for API key authentication."""

    async def test_auth_required_returns_401(self):
        """When auth is enabled, missing key returns 401."""
        import api.deps.auth as auth_mod

        old_keys = auth_mod._cached_keys
        try:
            auth_mod._cached_keys = None
            with patch.dict(os.environ, {"API_AUTH_ENABLED": "true", "API_KEYS": "secret-key"}):
                from api.main import app
                from httpx import ASGITransport, AsyncClient

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as ac:
                    resp = await ac.get("/users/testuser/overview")
                assert resp.status_code == 401
        finally:
            auth_mod._cached_keys = old_keys

    async def test_auth_valid_key_passes(self):
        """When auth is enabled, a valid key allows access."""
        import api.deps.auth as auth_mod
        from api.main import app
        from api.deps.http_session import get_shared_session
        from httpx import ASGITransport, AsyncClient
        from unittest.mock import MagicMock

        old_keys = auth_mod._cached_keys
        try:
            auth_mod._cached_keys = None
            with patch.dict(os.environ, {"API_AUTH_ENABLED": "true", "API_KEYS": "secret-key"}):
                with (
                    patch("api.routes.users.create_stats_collector") as mock_create,
                    patch("api.routes.users.cache_get", return_value=(False, None)),
                    patch("api.routes.users.cache_set"),
                ):
                    from test.api.conftest import _make_mock_collector
                    mock_create.return_value = _make_mock_collector()
                    app.dependency_overrides[get_shared_session] = lambda: MagicMock()

                    transport = ASGITransport(app=app)
                    async with AsyncClient(transport=transport, base_url="http://test") as ac:
                        resp = await ac.get(
                            "/users/testuser/overview",
                            headers={"Authorization": "Bearer secret-key"},
                        )
                    assert resp.status_code == 200

                    app.dependency_overrides.pop(get_shared_session, None)
        finally:
            auth_mod._cached_keys = old_keys
