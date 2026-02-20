"""SQLite-backed snapshot storage for temporal statistics history."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = Path(os.getenv("SNAPSHOTS_DB_PATH", str(Path(__file__).parent / "snapshots.db")))

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    data TEXT NOT NULL
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_snapshots_user_time
ON snapshots (username, timestamp);
"""


class SnapshotStore:
    """Persist and query periodic statistics snapshots in SQLite.

    :param db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Path = None):
        self._db_path = db_path or DEFAULT_DB_PATH
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        """Open a connection with WAL mode for concurrent reads.

        :returns: SQLite connection.
        :rtype: sqlite3.Connection
        """
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        """Create tables and indexes if they do not exist."""
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE)
            conn.execute(_CREATE_INDEX)

    def save_snapshot(self, username: str, data: Dict[str, Any],
                      timestamp: Optional[str] = None) -> None:
        """Store a statistics snapshot.

        :param username: GitHub username.
        :param data: Statistics dictionary to persist.
        :param timestamp: ISO-8601 timestamp. Defaults to current UTC time.
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO snapshots (username, timestamp, data) VALUES (?, ?, ?)",
                (username.lower(), ts, json.dumps(data)),
            )

    def get_snapshots(
        self,
        username: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieve snapshots for a user within an optional date range.

        :param username: GitHub username.
        :param from_date: ISO-8601 start date filter (inclusive).
        :param to_date: ISO-8601 end date filter (inclusive).
        :param limit: Maximum number of snapshots to return.
        :returns: List of snapshot dictionaries with ``date`` and stat fields.
        :rtype: list[dict]
        """
        query = "SELECT timestamp, data FROM snapshots WHERE username = ?"
        params: list = [username.lower()]

        if from_date:
            query += " AND timestamp >= ?"
            params.append(from_date)
        if to_date:
            query += " AND timestamp <= ?"
            params.append(to_date + "T23:59:59")

        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        results = []
        for row in rows:
            entry = json.loads(row["data"])
            entry["date"] = row["timestamp"][:10]
            results.append(entry)
        return results

    def get_latest_snapshot(self, username: str) -> Optional[Dict[str, Any]]:
        """Return the most recent snapshot for a user.

        :param username: GitHub username.
        :returns: Snapshot dict or None.
        :rtype: dict or None
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT timestamp, data FROM snapshots WHERE username = ? ORDER BY timestamp DESC LIMIT 1",
                (username.lower(),),
            ).fetchone()

        if row is None:
            return None
        entry = json.loads(row["data"])
        entry["date"] = row["timestamp"][:10]
        return entry


snapshot_store = SnapshotStore()
