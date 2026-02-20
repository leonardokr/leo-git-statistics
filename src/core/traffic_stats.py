#!/usr/bin/python3
"""Traffic statistics management for views and clones."""

from os import getenv
from typing import Any, Tuple
from datetime import datetime

from src.db.db import GitRepoStatsDB
from src.utils.helpers import to_bool


class TrafficStats:
    """Manages repository traffic statistics (views and clones)."""

    __DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, db: GitRepoStatsDB, **kwargs):
        self._db = db

        (
            self.store_repo_view_count,
            self.repo_views,
            self.repo_last_viewed,
            self.repo_first_viewed,
        ) = self._init_metric(
            kwargs,
            store_kwarg="store_repo_view_count",
            store_env="STORE_REPO_VIEWS",
            count_kwarg="repo_views",
            count_env="REPO_VIEWS",
            last_kwarg="repo_last_viewed",
            last_env="LAST_VIEWED",
            first_kwarg="repo_first_viewed",
            first_env="FIRST_VIEWED",
            db_count=self._db.views,
            db_to=self._db.views_to_date,
            db_from=self._db.views_from_date,
            set_count=self._db.set_views_count,
            set_from=self._db.set_views_from_date,
            set_to=self._db.set_views_to_date,
        )

        (
            self.store_repo_clone_count,
            self.repo_clones,
            self.repo_last_cloned,
            self.repo_first_cloned,
        ) = self._init_metric(
            kwargs,
            store_kwarg="store_repo_clone_count",
            store_env="STORE_REPO_CLONES",
            count_kwarg="repo_clones",
            count_env="REPO_CLONES",
            last_kwarg="repo_last_cloned",
            last_env="LAST_CLONED",
            first_kwarg="repo_first_cloned",
            first_env="FIRST_CLONED",
            db_count=self._db.clones,
            db_to=self._db.clones_to_date,
            db_from=self._db.clones_from_date,
            set_count=self._db.set_clones_count,
            set_from=self._db.set_clones_from_date,
            set_to=self._db.set_clones_to_date,
        )

    def _validate_date(self, date_str: str) -> str:
        """Validates date string format."""
        try:
            if (
                date_str
                == datetime.strptime(date_str, self.__DATE_FORMAT).strftime(
                    self.__DATE_FORMAT
                )
            ):
                return date_str
        except (ValueError, TypeError):
            pass
        return ""

    def _init_metric(
        self,
        kwargs,
        *,
        store_kwarg,
        store_env,
        count_kwarg,
        count_env,
        last_kwarg,
        last_env,
        first_kwarg,
        first_env,
        db_count,
        db_to,
        db_from,
        set_count,
        set_from,
        set_to,
    ) -> Tuple[bool, int, str, str]:
        """Initializes a single traffic metric (views or clones)."""
        store = to_bool(kwargs.get(store_kwarg, getenv(store_env)), default=True)

        if not store:
            set_count(0)
            set_from("0000-00-00")
            set_to("0000-00-00")
            return store, 0, "0000-00-00", "0000-00-00"

        count_val = kwargs.get(count_kwarg, getenv(count_env))
        try:
            count = int(count_val) if count_val else db_count
            if count_val:
                set_count(count)
        except ValueError:
            count = db_count

        last_val = kwargs.get(last_kwarg, getenv(last_env))
        last_date = self._validate_date(last_val) if last_val else db_to

        first_val = kwargs.get(first_kwarg, getenv(first_env))
        first_date = self._validate_date(first_val) if first_val else db_from

        return store, count, last_date, first_date

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
