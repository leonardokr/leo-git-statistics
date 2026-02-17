"""SQLite-backed webhook registration storage."""

import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = Path(os.getenv("WEBHOOKS_DB_PATH", str(Path(__file__).parent / "webhooks.db")))

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS webhooks (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    url TEXT NOT NULL,
    conditions TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_webhooks_user
ON webhooks (username);
"""


class WebhookStore:
    """Persist and query webhook registrations in SQLite.

    :param db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Path = None):
        self._db_path = db_path or DEFAULT_DB_PATH
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        """Open a connection with WAL mode.

        :returns: SQLite connection.
        :rtype: sqlite3.Connection
        """
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        """Create tables and indexes if they do not exist."""
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE)
            conn.execute(_CREATE_INDEX)

    def create(self, username: str, url: str, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new webhook.

        :param username: GitHub username to monitor.
        :param url: Callback URL to POST notifications to.
        :param conditions: Trigger conditions dictionary.
        :returns: The created webhook record.
        :rtype: dict
        """
        webhook_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO webhooks (id, username, url, conditions) VALUES (?, ?, ?, ?)",
                (webhook_id, username.lower(), url, json.dumps(conditions)),
            )
        return {
            "id": webhook_id,
            "username": username.lower(),
            "url": url,
            "conditions": conditions,
        }

    def list_by_user(self, username: str) -> List[Dict[str, Any]]:
        """List all webhooks for a user.

        :param username: GitHub username.
        :returns: List of webhook records.
        :rtype: list[dict]
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, username, url, conditions, created_at FROM webhooks WHERE username = ? ORDER BY created_at",
                (username.lower(),),
            ).fetchall()

        return [
            {
                "id": row["id"],
                "username": row["username"],
                "url": row["url"],
                "conditions": json.loads(row["conditions"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get a webhook by ID.

        :param webhook_id: Webhook UUID.
        :returns: Webhook record or None.
        :rtype: dict or None
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, url, conditions, created_at FROM webhooks WHERE id = ?",
                (webhook_id,),
            ).fetchone()

        if row is None:
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "url": row["url"],
            "conditions": json.loads(row["conditions"]),
            "created_at": row["created_at"],
        }

    def delete(self, webhook_id: str) -> bool:
        """Delete a webhook by ID.

        :param webhook_id: Webhook UUID.
        :returns: True if a record was deleted.
        :rtype: bool
        """
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM webhooks WHERE id = ?", (webhook_id,))
            return cursor.rowcount > 0

    def get_all_active(self) -> List[Dict[str, Any]]:
        """Return all registered webhooks (used by the notification dispatcher).

        :returns: List of all webhook records.
        :rtype: list[dict]
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, username, url, conditions, created_at FROM webhooks ORDER BY username",
            ).fetchall()

        return [
            {
                "id": row["id"],
                "username": row["username"],
                "url": row["url"],
                "conditions": json.loads(row["conditions"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]


webhook_store = WebhookStore()
