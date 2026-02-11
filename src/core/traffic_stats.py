#!/usr/bin/python3
"""Traffic statistics management for views and clones."""

from os import getenv
from typing import Any
from datetime import datetime

from src.db.db import GitRepoStatsDB


class TrafficStats:
    """Manages repository traffic statistics (views and clones)."""

    __DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, db: GitRepoStatsDB, **kwargs):
        self._db = db
        self._init_views(kwargs)
        self._init_clones(kwargs)

    def _validate_date(self, date_str: str) -> str:
        """Validates date string format."""
        try:
            if date_str == datetime.strptime(date_str, self.__DATE_FORMAT).strftime(self.__DATE_FORMAT):
                return date_str
        except (ValueError, TypeError):
            pass
        return ""

    def _init_views(self, kwargs) -> None:
        """Initializes repository view statistics."""
        store_view_count = kwargs.get("store_repo_view_count", getenv("STORE_REPO_VIEWS"))
        self.store_repo_view_count = not store_view_count or store_view_count.strip().lower() != "false"

        if not self.store_repo_view_count:
            self.repo_views = 0
            self._db.set_views_count(self.repo_views)
            self.repo_last_viewed = "0000-00-00"
            self.repo_first_viewed = "0000-00-00"
            self._db.set_views_from_date(self.repo_first_viewed)
            self._db.set_views_to_date(self.repo_last_viewed)
            return

        repo_views = kwargs.get("repo_views", getenv("REPO_VIEWS"))
        try:
            self.repo_views = int(repo_views) if repo_views else self._db.views
            if repo_views:
                self._db.set_views_count(self.repo_views)
        except ValueError:
            self.repo_views = self._db.views

        last_v = kwargs.get("repo_last_viewed", getenv("LAST_VIEWED"))
        self.repo_last_viewed = self._validate_date(last_v) if last_v else self._db.views_to_date

        first_v = kwargs.get("repo_first_viewed", getenv("FIRST_VIEWED"))
        self.repo_first_viewed = self._validate_date(first_v) if first_v else self._db.views_from_date

    def _init_clones(self, kwargs) -> None:
        """Initializes repository clone statistics."""
        store_clone_count = kwargs.get("store_repo_clone_count", getenv("STORE_REPO_CLONES"))
        self.store_repo_clone_count = not store_clone_count or store_clone_count.strip().lower() != "false"

        if not self.store_repo_clone_count:
            self.repo_clones = 0
            self._db.set_clones_count(self.repo_clones)
            self.repo_last_cloned = "0000-00-00"
            self.repo_first_cloned = "0000-00-00"
            self._db.set_clones_from_date(self.repo_first_cloned)
            self._db.set_clones_to_date(self.repo_last_cloned)
            return

        repo_clones = kwargs.get("repo_clones", getenv("REPO_CLONES"))
        try:
            self.repo_clones = int(repo_clones) if repo_clones else self._db.clones
            if repo_clones:
                self._db.set_clones_count(self.repo_clones)
        except ValueError:
            self.repo_clones = self._db.clones

        last_c = kwargs.get("repo_last_cloned", getenv("LAST_CLONED"))
        self.repo_last_cloned = self._validate_date(last_c) if last_c else self._db.clones_to_date

        first_c = kwargs.get("repo_first_cloned", getenv("FIRST_CLONED"))
        self.repo_first_cloned = self._validate_date(first_c) if first_c else self._db.clones_from_date

    def set_views(self, views: Any) -> None:
        """Updates the total repository views count and persists it."""
        self.repo_views += int(views)
        self._db.set_views_count(self.repo_views)

    def set_last_viewed(self, new_last_viewed_date: str) -> None:
        """Updates the date of the last repository view and persists it."""
        self.repo_last_viewed = new_last_viewed_date
        self._db.set_views_to_date(self.repo_last_viewed)

    def set_first_viewed(self, new_first_viewed_date: str) -> None:
        """Updates the date of the first repository view and persists it."""
        self.repo_first_viewed = new_first_viewed_date
        self._db.set_views_from_date(self.repo_first_viewed)

    def set_clones(self, clones: Any) -> None:
        """Updates the total repository clones count and persists it."""
        self.repo_clones += int(clones)
        self._db.set_clones_count(self.repo_clones)

    def set_last_cloned(self, new_last_cloned_date: str) -> None:
        """Updates the date of the last repository clone and persists it."""
        self.repo_last_cloned = new_last_cloned_date
        self._db.set_clones_to_date(self.repo_last_cloned)

    def set_first_cloned(self, new_first_cloned_date: str) -> None:
        """Updates the date of the first repository clone and persists it."""
        self.repo_first_cloned = new_first_cloned_date
        self._db.set_clones_from_date(self.repo_first_cloned)
