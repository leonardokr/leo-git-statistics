"""SQLite-backed persistence for repository traffic statistics."""

import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(os.getenv("DATABASE_PATH", str(Path(__file__).parent / "traffic.db")))

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS traffic_stats (
    metric TEXT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0,
    date_from TEXT NOT NULL DEFAULT '0000-00-00',
    date_to TEXT NOT NULL DEFAULT '0000-00-00'
);
"""

_SEED = """
INSERT OR IGNORE INTO traffic_stats (metric, count, date_from, date_to)
VALUES ('views', 0, '0000-00-00', '0000-00-00'),
       ('clones', 0, '0000-00-00', '0000-00-00');
"""

logger = logging.getLogger(__name__)


class GitRepoStatsDB:
    """Manages persistence of repository traffic statistics in SQLite.

    :param db_path: Path to the SQLite database file.
                    Defaults to ``traffic.db`` in the same directory
                    as this module, or the ``DATABASE_PATH`` env var.
    """

    def __init__(self, db_path: Path = None):
        self._db_path = db_path or DEFAULT_DB_PATH
        self._ensure_schema()
        self._load()

    def _connect(self) -> sqlite3.Connection:
        """Open a connection with WAL mode for concurrent reads.

        :returns: SQLite connection.
        :rtype: sqlite3.Connection
        """
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        """Create tables and seed default rows if they do not exist."""
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE)
            conn.executescript(_SEED)

    def _load(self) -> None:
        """Load current values from the database into instance attributes."""
        with self._connect() as conn:
            rows = conn.execute("SELECT metric, count, date_from, date_to FROM traffic_stats").fetchall()

        data = {row["metric"]: row for row in rows}

        views = data.get("views")
        self.views = views["count"] if views else 0
        self.views_from_date = views["date_from"] if views else "0000-00-00"
        self.views_to_date = views["date_to"] if views else "0000-00-00"

        clones = data.get("clones")
        self.clones = clones["count"] if clones else 0
        self.clones_from_date = clones["date_from"] if clones else "0000-00-00"
        self.clones_to_date = clones["date_to"] if clones else "0000-00-00"

    def _update(self, metric: str, **fields) -> None:
        """Update specific fields for a traffic metric.

        :param metric: Either ``views`` or ``clones``.
        :param fields: Column names and values to update.
        """
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [metric]
        with self._connect() as conn:
            conn.execute(f"UPDATE traffic_stats SET {set_clause} WHERE metric = ?", values)

    def set_views_count(self, count: Any) -> None:
        """Update the view count.

        :param count: The new view count.
        """
        self.views = int(count)
        self._update("views", count=self.views)

    def set_views_from_date(self, date: str) -> None:
        """Update the starting date for views.

        :param date: The starting date string.
        """
        self.views_from_date = date
        self._update("views", date_from=self.views_from_date)

    def set_views_to_date(self, date: str) -> None:
        """Update the end date for views.

        :param date: The end date string.
        """
        self.views_to_date = date
        self._update("views", date_to=self.views_to_date)

    def set_clones_count(self, count: Any) -> None:
        """Update the clone count.

        :param count: The new clone count.
        """
        self.clones = int(count)
        self._update("clones", count=self.clones)

    def set_clones_from_date(self, date: str) -> None:
        """Update the starting date for clones.

        :param date: The starting date string.
        """
        self.clones_from_date = date
        self._update("clones", date_from=self.clones_from_date)

    def set_clones_to_date(self, date: str) -> None:
        """Update the end date for clones.

        :param date: The end date string.
        """
        self.clones_to_date = date
        self._update("clones", date_to=self.clones_to_date)
