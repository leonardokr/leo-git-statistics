#!/usr/bin/python3

from os import getenv, environ
from typing import Optional, Any
from datetime import datetime

from src.db.db import GitRepoStatsDB


def _to_bool(val: Optional[str], default: bool = False) -> bool:
    """Convert a string value to boolean with a default fallback."""
    if val is None:
        return default
    return str(val).strip().lower() == "true"


class Environment:
    """
    Manages environment variables and persistent statistics from the database.

    This class centralizes the retrieval and management of configuration settings,
    providing a consistent interface for the rest of the application.
    """

    __DATE_FORMAT = '%Y-%m-%d'

    def __init__(self,
                 username: str,
                 access_token: str,
                 **kwargs):
        """
        Initializes the Environment with GitHub credentials and optional configurations.

        :param username: GitHub username.
        :param access_token: GitHub personal access token.
        :param kwargs: Optional configurations from environment variables.
        """
        self.__db = GitRepoStatsDB()
        self.username = username
        self.access_token = access_token

        self._init_exclusions(kwargs)
        self._init_filters(kwargs)
        self._init_views(kwargs)
        self._init_clones(kwargs)
        self._init_additional_configs(kwargs)

    def _init_exclusions(self, kwargs):
        """Initializes repository and language exclusions."""
        exclude_repos = kwargs.get("exclude_repos", getenv("EXCLUDED"))
        exclude_langs = kwargs.get("exclude_langs", getenv("EXCLUDED_LANGS"))

        self.exclude_repos = {x.strip() for x in exclude_repos.split(",")} if exclude_repos else set()
        self.exclude_langs = {x.strip() for x in exclude_langs.split(",")} if exclude_langs else set()

    def _init_filters(self, kwargs):
        """Initializes repository filters (forked, archived, etc.)."""
        self.include_forked_repos = _to_bool(kwargs.get("include_forked_repos", getenv("INCLUDE_FORKED_REPOS")))
        self.exclude_contrib_repos = _to_bool(kwargs.get("exclude_contrib_repos", getenv("EXCLUDE_CONTRIB_REPOS")))
        self.exclude_archive_repos = _to_bool(kwargs.get("exclude_archive_repos", getenv("EXCLUDE_ARCHIVE_REPOS")))
        self.exclude_private_repos = _to_bool(kwargs.get("exclude_private_repos", getenv("EXCLUDE_PRIVATE_REPOS")))
        self.exclude_public_repos = _to_bool(kwargs.get("exclude_public_repos", getenv("EXCLUDE_PUBLIC_REPOS")))

    def _init_views(self, kwargs):
        """Initializes repository view statistics."""
        store_view_count = kwargs.get("store_repo_view_count", getenv("STORE_REPO_VIEWS"))
        self.store_repo_view_count = not store_view_count or store_view_count.strip().lower() != "false"

        if not self.store_repo_view_count:
            self.repo_views = 0
            self.__db.set_views_count(self.repo_views)
            self.repo_last_viewed = "0000-00-00"
            self.repo_first_viewed = "0000-00-00"
            self.__db.set_views_from_date(self.repo_first_viewed)
            self.__db.set_views_to_date(self.repo_last_viewed)
            return

        repo_views = kwargs.get("repo_views", getenv("REPO_VIEWS"))
        try:
            self.repo_views = int(repo_views) if repo_views else self.__db.views
            if repo_views: self.__db.set_views_count(self.repo_views)
        except ValueError:
            self.repo_views = self.__db.views

        last_v = kwargs.get("repo_last_viewed", getenv("LAST_VIEWED"))
        self.repo_last_viewed = self._validate_date(last_v) if last_v else self.__db.views_to_date
        
        first_v = kwargs.get("repo_first_viewed", getenv("FIRST_VIEWED"))
        self.repo_first_viewed = self._validate_date(first_v) if first_v else self.__db.views_from_date

    def _init_clones(self, kwargs):
        """Initializes repository clone statistics."""
        store_clone_count = kwargs.get("store_repo_clone_count", getenv("STORE_REPO_CLONES"))
        self.store_repo_clone_count = not store_clone_count or store_clone_count.strip().lower() != "false"

        if not self.store_repo_clone_count:
            self.repo_clones = 0
            self.__db.set_clones_count(self.repo_clones)
            self.repo_last_cloned = "0000-00-00"
            self.repo_first_cloned = "0000-00-00"
            self.__db.set_clones_from_date(self.repo_first_cloned)
            self.__db.set_clones_to_date(self.repo_last_cloned)
            return

        repo_clones = kwargs.get("repo_clones", getenv("REPO_CLONES"))
        try:
            self.repo_clones = int(repo_clones) if repo_clones else self.__db.clones
            if repo_clones: self.__db.set_clones_count(self.repo_clones)
        except ValueError:
            self.repo_clones = self.__db.clones

        last_c = kwargs.get("repo_last_cloned", getenv("LAST_CLONED"))
        self.repo_last_cloned = self._validate_date(last_c) if last_c else self.__db.clones_to_date

        first_c = kwargs.get("repo_first_cloned", getenv("FIRST_CLONED"))
        self.repo_first_cloned = self._validate_date(first_c) if first_c else self.__db.clones_from_date

    def _init_additional_configs(self, kwargs):
        """Initializes additional configurations (collabs, extra repos)."""
        more_collabs = kwargs.get("more_collabs", getenv("MORE_COLLABS"))
        try:
            self.more_collabs = int(more_collabs) if more_collabs else 0
        except ValueError:
            self.more_collabs = 0

        more_repos = kwargs.get("manually_added_repos", getenv("MORE_REPOS"))
        self.manually_added_repos = {x.strip() for x in more_repos.split(",")} if more_repos else set()

        only_included = kwargs.get("only_included_repos", getenv("ONLY_INCLUDED"))
        self.only_included_repos = {x.strip() for x in only_included.split(",")} if only_included and only_included != "" else set()

        # Visual toggles
        self.show_total_contributions = _to_bool(kwargs.get("show_total_contributions", getenv("SHOW_TOTAL_CONTRIBUTIONS")), True)
        self.show_repositories = _to_bool(kwargs.get("show_repositories", getenv("SHOW_REPOSITORIES")), True)
        self.show_lines_changed = _to_bool(kwargs.get("show_lines_changed", getenv("SHOW_LINES_CHANGED")), True)
        self.show_avg_percent = _to_bool(kwargs.get("show_avg_percent", getenv("SHOW_AVG_PERCENT")), True)
        self.show_collaborators = _to_bool(kwargs.get("show_collaborators", getenv("SHOW_COLLABORATORS")), True)
        self.show_contributors = _to_bool(kwargs.get("show_contributors", getenv("SHOW_CONTRIBUTORS")), True)
        self.show_views = _to_bool(kwargs.get("show_views", getenv("SHOW_VIEWS")), True)
        self.show_clones = _to_bool(kwargs.get("show_clones", getenv("SHOW_CLONES")), True)
        self.show_forks = _to_bool(kwargs.get("show_forks", getenv("SHOW_FORKS")), True)
        self.show_stars = _to_bool(kwargs.get("show_stars", getenv("SHOW_STARS")), True)
        self.show_pull_requests = _to_bool(kwargs.get("show_pull_requests", getenv("SHOW_PULL_REQUESTS")), True)
        self.show_issues = _to_bool(kwargs.get("show_issues", getenv("SHOW_ISSUES")), True)

    def _validate_date(self, date_str: str) -> str:
        """Validates date string format."""
        try:
            if date_str == datetime.strptime(date_str, self.__DATE_FORMAT).strftime(self.__DATE_FORMAT):
                return date_str
        except (ValueError, TypeError):
            pass
        return "" # Will be overridden by fallback in init methods

    def set_views(self, views: Any) -> None:
        """
        Updates the total repository views count and persists it.

        :param views: Number of new views to add.
        """
        self.repo_views += int(views)
        environ["REPO_VIEWS"] = str(self.repo_views)
        self.__db.set_views_count(self.repo_views)

    def set_last_viewed(self, new_last_viewed_date: str) -> None:
        """
        Updates the date of the last repository view and persists it.

        :param new_last_viewed_date: The new last viewed date string.
        """
        self.repo_last_viewed = new_last_viewed_date
        environ["LAST_VIEWED"] = self.repo_last_viewed
        self.__db.set_views_to_date(self.repo_last_viewed)

    def set_first_viewed(self, new_first_viewed_date: str) -> None:
        """
        Updates the date of the first repository view and persists it.

        :param new_first_viewed_date: The new first viewed date string.
        """
        self.repo_first_viewed = new_first_viewed_date
        environ["FIRST_VIEWED"] = self.repo_first_viewed
        self.__db.set_views_from_date(self.repo_first_viewed)

    def set_clones(self, clones: Any) -> None:
        """
        Updates the total repository clones count and persists it.

        :param clones: Number of new clones to add.
        """
        self.repo_clones += int(clones)
        environ["REPO_CLONES"] = str(self.repo_clones)
        self.__db.set_clones_count(self.repo_clones)

    def set_last_cloned(self, new_last_cloned_date: str) -> None:
        """
        Updates the date of the last repository clone and persists it.

        :param new_last_cloned_date: The new last cloned date string.
        """
        self.repo_last_cloned = new_last_cloned_date
        environ["LAST_CLONED"] = self.repo_last_cloned
        self.__db.set_clones_to_date(self.repo_last_cloned)

    def set_first_cloned(self, new_first_cloned_date: str) -> None:
        """
        Updates the date of the first repository clone and persists it.

        :param new_first_cloned_date: The new first cloned date string.
        """
        self.repo_first_cloned = new_first_cloned_date
        environ["FIRST_CLONED"] = self.repo_first_cloned
        self.__db.set_clones_from_date(self.repo_first_cloned)
