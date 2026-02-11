#!/usr/bin/python3
"""Repository filtering configuration."""

from os import getenv
from typing import Set

from src.utils.helpers import to_bool


class RepositoryFilter:
    """Manages repository filtering rules and exclusions."""

    def __init__(self, **kwargs):
        self._init_exclusions(kwargs)
        self._init_type_filters(kwargs)
        self._init_repo_lists(kwargs)

    def _init_exclusions(self, kwargs) -> None:
        """Initializes repository and language exclusions."""
        exclude_repos = kwargs.get("exclude_repos", getenv("EXCLUDED"))
        exclude_langs = kwargs.get("exclude_langs", getenv("EXCLUDED_LANGS"))

        self.exclude_repos: Set[str] = {x.strip() for x in exclude_repos.split(",")} if exclude_repos else set()
        self.exclude_langs: Set[str] = {x.strip() for x in exclude_langs.split(",")} if exclude_langs else set()

    def _init_type_filters(self, kwargs) -> None:
        """Initializes repository type filters."""
        self.include_forked_repos = to_bool(kwargs.get("include_forked_repos", getenv("INCLUDE_FORKED_REPOS")))
        self.exclude_contrib_repos = to_bool(kwargs.get("exclude_contrib_repos", getenv("EXCLUDE_CONTRIB_REPOS")))
        self.exclude_archive_repos = to_bool(kwargs.get("exclude_archive_repos", getenv("EXCLUDE_ARCHIVE_REPOS")))
        self.exclude_private_repos = to_bool(kwargs.get("exclude_private_repos", getenv("EXCLUDE_PRIVATE_REPOS")))
        self.exclude_public_repos = to_bool(kwargs.get("exclude_public_repos", getenv("EXCLUDE_PUBLIC_REPOS")))

    def _init_repo_lists(self, kwargs) -> None:
        """Initializes manually added and only-included repo lists."""
        more_repos = kwargs.get("manually_added_repos", getenv("MORE_REPOS"))
        self.manually_added_repos: Set[str] = {x.strip() for x in more_repos.split(",")} if more_repos else set()

        only_included = kwargs.get("only_included_repos", getenv("ONLY_INCLUDED"))
        self.only_included_repos: Set[str] = {x.strip() for x in only_included.split(",")} if only_included and only_included != "" else set()
