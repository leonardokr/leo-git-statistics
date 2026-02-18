"""Integration tests for /users/{username}/history endpoints."""

import pytest
from unittest.mock import patch, AsyncMock

# FIX: Inject tornado.gen into sys.modules to satisfy pybreaker's missing import
import sys
import tornado.gen as gen
sys.modules['gen'] = gen


class TestHistory:
    """Tests for history/snapshot endpoints."""

    async def test_get_history_empty(self, client):
        """GET returns empty list when no snapshots exist."""
        with patch("api.routes.history.snapshot_store") as mock_store:
            mock_store.get_snapshots.return_value = []
            resp = await client.get("/v1/users/testuser/history")
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "testuser"
        assert body["snapshots"] == []

    async def test_get_history_with_data(self, client):
        """GET returns stored snapshots."""
        snapshots = [
            {"date": "2026-02-15", "total_stars": 40, "total_forks": 9},
            {"date": "2026-02-16", "total_stars": 42, "total_forks": 10},
        ]
        with patch("api.routes.history.snapshot_store") as mock_store:
            mock_store.get_snapshots.return_value = snapshots
            resp = await client.get("/v1/users/testuser/history")
        assert resp.status_code == 200
        assert len(resp.json()["snapshots"]) == 2

    async def test_get_history_with_date_filter(self, client):
        """GET passes date filters to the store."""
        with patch("api.routes.history.snapshot_store") as mock_store:
            mock_store.get_snapshots.return_value = []
            resp = await client.get(
                "/v1/users/testuser/history?from=2026-02-01&to=2026-02-17"
            )
        assert resp.status_code == 200
        mock_store.get_snapshots.assert_called_once_with(
            "testuser", from_date="2026-02-01", to_date="2026-02-17", limit=100,
        )

    async def test_create_snapshot(self, client, mock_collector):
        """POST /snapshot collects stats and saves a snapshot."""
        with (
            patch("api.routes.history.snapshot_store") as mock_store,
            patch("api.routes.history.dispatch_webhooks", new_callable=AsyncMock),
            patch("api.routes.history.create_stats_collector", return_value=mock_collector),
        ):
            resp = await client.post("/v1/users/testuser/history/snapshot")
        assert resp.status_code == 201
        body = resp.json()
        assert body["username"] == "testuser"
        assert "snapshot" in body
        assert body["snapshot"]["total_stars"] == 42
        mock_store.save_snapshot.assert_called_once()
