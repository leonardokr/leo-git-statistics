"""Integration tests for /users/{username}/webhooks endpoints."""

import pytest
from unittest.mock import MagicMock, patch

# FIX: Inject tornado.gen into sys.modules to satisfy pybreaker's missing import
import sys
import tornado.gen as gen
sys.modules['gen'] = gen


class TestWebhooks:
    """Tests for webhook CRUD operations."""

    async def test_create_webhook(self, client):
        """POST creates a webhook and returns 201."""
        record = {
            "id": "abc-123",
            "username": "testuser",
            "url": "https://example.com/hook",
            "conditions": {"stars_threshold": 100},
        }
        with patch("api.routes.webhooks.webhook_store") as mock_store:
            mock_store.create.return_value = record
            resp = await client.post(
                "/v1/users/testuser/webhooks",
                json={
                    "url": "https://example.com/hook",
                    "conditions": {"stars_threshold": 100},
                },
            )
        assert resp.status_code == 201
        assert resp.json()["id"] == "abc-123"

    async def test_list_webhooks(self, client):
        """GET returns all webhooks for the user."""
        records = [
            {"id": "abc-123", "username": "testuser", "url": "https://example.com/hook",
             "conditions": {"stars_threshold": 100}, "created_at": "2026-02-17"},
        ]
        with patch("api.routes.webhooks.webhook_store") as mock_store:
            mock_store.list_by_user.return_value = records
            resp = await client.get("/v1/users/testuser/webhooks")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_delete_webhook(self, client):
        """DELETE removes a webhook and returns 204."""
        hook = {"id": "abc-123", "username": "testuser", "url": "https://example.com/hook",
                "conditions": {}}
        with patch("api.routes.webhooks.webhook_store") as mock_store:
            mock_store.get.return_value = hook
            mock_store.delete.return_value = True
            resp = await client.delete("/v1/users/testuser/webhooks/abc-123")
        assert resp.status_code == 204

    async def test_delete_nonexistent_webhook_returns_404(self, client):
        """DELETE returns 404 when webhook does not exist."""
        with patch("api.routes.webhooks.webhook_store") as mock_store:
            mock_store.get.return_value = None
            resp = await client.delete("/v1/users/testuser/webhooks/nope")
        assert resp.status_code == 404

    async def test_create_webhook_invalid_body_returns_422(self, client):
        """POST with missing fields returns 422."""
        resp = await client.post(
            "/v1/users/testuser/webhooks",
            json={"url": "not-a-url"},
        )
        assert resp.status_code == 422
