"""Integration tests for the /health endpoint."""

import pytest
from unittest.mock import patch

from src.core.github_client import RateLimitState


class TestHealthEndpoint:
    """Tests for GET /health."""

    async def test_healthy_status(self, client):
        """Endpoint returns 200 with healthy status when subsystems are normal."""
        state = RateLimitState()
        state.remaining = 4500
        state.limit = 5000
        state.reset = 1739800000

        with (
            patch("api.routes.health.rate_limit_state", state),
            patch("api.routes.health.github_breaker") as mock_breaker,
        ):
            mock_breaker.current_state = "closed"
            resp = await client.get("/health")

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "healthy"
        assert body["version"] == "latest"
        assert body["circuit_breaker"] == "closed"
        assert body["github_api"]["status"] == "connected"
        assert body["github_api"]["rate_limit_remaining"] == 4500
        assert "uptime_seconds" in body
        assert "cache" in body

    async def test_degraded_when_rate_limit_low(self, client):
        """Endpoint returns 503 when rate limit is degraded."""
        state = RateLimitState()
        state.remaining = 50
        state.limit = 5000
        state.reset = 1739800000

        with (
            patch("api.routes.health.rate_limit_state", state),
            patch("api.routes.health.github_breaker") as mock_breaker,
        ):
            mock_breaker.current_state = "closed"
            resp = await client.get("/health")

        assert resp.status_code == 503
        assert resp.json()["status"] == "degraded"
        assert resp.json()["github_api"]["status"] == "degraded"

    async def test_unhealthy_when_circuit_open(self, client):
        """Endpoint returns 503 when circuit breaker is open."""
        state = RateLimitState()
        state.remaining = 4000
        state.limit = 5000

        with (
            patch("api.routes.health.rate_limit_state", state),
            patch("api.routes.health.github_breaker") as mock_breaker,
        ):
            mock_breaker.current_state = "open"
            resp = await client.get("/health")

        assert resp.status_code == 503
        assert resp.json()["status"] == "unhealthy"

    async def test_unknown_github_status_when_no_data(self, client):
        """When rate limit has never been populated, status is unknown/degraded."""
        state = RateLimitState()

        with (
            patch("api.routes.health.rate_limit_state", state),
            patch("api.routes.health.github_breaker") as mock_breaker,
        ):
            mock_breaker.current_state = "closed"
            resp = await client.get("/health")

        body = resp.json()
        assert body["github_api"]["status"] == "unknown"
