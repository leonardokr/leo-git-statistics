#!/usr/bin/python3

import logging
from json import load, dumps, JSONDecodeError
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).parent / "db.json"
DEFAULT_DB = {
    "views": {"count": "0", "from": "0000-00-00", "to": "0000-00-00"},
    "clones": {"count": "0", "from": "0000-00-00", "to": "0000-00-00"}
}

logger = logging.getLogger(__name__)


class GitRepoStatsDB:
    """Manages persistence of repository statistics in a JSON database."""

    def __init__(self, db_path: Path = None):
        """
        :param db_path: Path to the JSON database file. Defaults to ``db.json``
                        in the same directory as this module.
        """
        self._db_path = db_path or DEFAULT_DB_PATH
        self.__db = self._load_db()

        self.views = int(self.__db['views']['count'])
        self.views_from_date = self.__db['views']['from']
        self.views_to_date = self.__db['views']['to']

        self.clones = int(self.__db['clones']['count'])
        self.clones_from_date = self.__db['clones']['from']
        self.clones_to_date = self.__db['clones']['to']

    def _load_db(self) -> dict:
        """Load database from file or create with defaults if not exists."""
        try:
            with open(self._db_path, "r") as db:
                return load(db)
        except FileNotFoundError:
            logger.warning("Database file not found, creating with defaults: %s", self._db_path)
            self._write_db(DEFAULT_DB)
            return DEFAULT_DB.copy()
        except JSONDecodeError as e:
            logger.error("Invalid JSON in database file: %s", e)
            return DEFAULT_DB.copy()

    def _write_db(self, data: dict) -> None:
        """Write data to database file."""
        try:
            with open(self._db_path, "w") as db:
                db.write(dumps(data, indent=2))
        except IOError as e:
            logger.error("Failed to write database: %s", e)

    def __update_db(self) -> None:
        """Saves the current state of the database to the JSON file."""
        self._write_db(self.__db)

    def set_views_count(self, count: Any) -> None:
        """
        Updates the view count in the database.

        :param count: The new view counts.
        """
        self.views = int(count)
        self.__db['views']['count'] = str(self.views)
        self.__update_db()

    def set_views_from_date(self, date: str) -> None:
        """
        Updates the starting date for views in the database.

        :param date: The starting date string.
        """
        self.views_from_date = date
        self.__db['views']['from'] = self.views_from_date
        self.__update_db()

    def set_views_to_date(self, date: str) -> None:
        """
        Updates the end date for views in the database.

        :param date: The end date string.
        """
        self.views_to_date = date
        self.__db['views']['to'] = self.views_to_date
        self.__update_db()

    def set_clones_count(self, count: Any) -> None:
        """
        Updates the clone count in the database.

        :param count: The new clone count.
        """
        self.clones = int(count)
        self.__db['clones']['count'] = str(self.clones)
        self.__update_db()

    def set_clones_from_date(self, date: str) -> None:
        """
        Updates the starting date for clones in the database.

        :param date: The starting date string.
        """
        self.clones_from_date = date
        self.__db['clones']['from'] = self.clones_from_date
        self.__update_db()

    def set_clones_to_date(self, date: str) -> None:
        """
        Updates the end date for clones in the database.

        :param date: The end date string.
        """
        self.clones_to_date = date
        self.__db['clones']['to'] = self.clones_to_date
        self.__update_db()
