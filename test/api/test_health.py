"""Integration tests for the /health endpoint."""

from unittest.mock import patch

from src.core.github_client import RateLimitState

import sys
import tornado.gen as gen
sys.modules['gen'] = gen


class TestHealthEndpoint:
    """Tests for GET /health."""

    async def test_ok_status(self, client):
        """Endpoint returns 200 with ok status when subsystems are normal."""
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
        assert resp.json() == {"status": "ok"}

    async def test_degraded_when_rate_limit_low(self, client):
        """Endpoint returns 200 with degraded status when rate limit is low."""
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

        assert resp.status_code == 200
        assert resp.json() == {"status": "degraded"}

    async def test_unavailable_when_circuit_open(self, client):
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
        assert resp.json() == {"status": "unavailable"}

    async def test_degraded_when_no_rate_limit_data(self, client):
        """When rate limit has never been populated, status is degraded."""
        state = RateLimitState()

        with (
            patch("api.routes.health.rate_limit_state", state),
            patch("api.routes.health.github_breaker") as mock_breaker,
        ):
            mock_breaker.current_state = "closed"
            resp = await client.get("/health")

        assert resp.status_code == 200
        assert resp.json() == {"status": "degraded"}

    async def test_unavailable_when_rate_limit_critical(self, client):
        """Endpoint returns 503 when rate limit is critically low."""
        state = RateLimitState()
        state.remaining = 5
        state.limit = 5000

        with (
            patch("api.routes.health.rate_limit_state", state),
            patch("api.routes.health.github_breaker") as mock_breaker,
        ):
            mock_breaker.current_state = "closed"
            resp = await client.get("/health")

        assert resp.status_code == 503
        assert resp.json() == {"status": "unavailable"}

    async def test_no_internal_details_exposed(self, client):
        """Response must not contain internal infrastructure details."""
        state = RateLimitState()
        state.remaining = 4500
        state.limit = 5000

        with (
            patch("api.routes.health.rate_limit_state", state),
            patch("api.routes.health.github_breaker") as mock_breaker,
        ):
            mock_breaker.current_state = "closed"
            resp = await client.get("/health")

        body = resp.json()
        assert list(body.keys()) == ["status"]
