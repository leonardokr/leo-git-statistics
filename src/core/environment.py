#!/usr/bin/python3
"""Environment and configuration management."""

from typing import Any, Dict, Optional

import yaml

from src.db.db import GitRepoStatsDB
from src.core.repository_filter import RepositoryFilter
from src.core.traffic_stats import TrafficStats
from src.core.display_settings import DisplaySettings


class Environment:
    """Manages GitHub credentials and aggregates configuration settings."""

    def __init__(self, username: str, access_token: str, *,
                 db: GitRepoStatsDB = None,
                 repo_filter: RepositoryFilter = None,
                 traffic: TrafficStats = None,
                 display: DisplaySettings = None,
                 config_path: str = "config.yml",
                 config_overrides: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """
        :param username: GitHub username.
        :param access_token: GitHub personal access token.
        :param db: Database instance. Defaults to a new ``GitRepoStatsDB``.
        :param repo_filter: Repository filter. Defaults to a new ``RepositoryFilter``.
        :param traffic: Traffic stats tracker. Defaults to a new ``TrafficStats``.
        :param display: Display settings. Defaults to a new ``DisplaySettings``.
        """
        self.username = username
        self.access_token = access_token

        config = self._load_config(config_path)
        if isinstance(config_overrides, dict) and config_overrides:
            self._deep_merge(config, config_overrides)
        config_stats = config.get("stats_generation", {}) or {}
        resolved_options = self._resolve_options(config, config_stats, kwargs)

        self.timezone = resolved_options.get("timezone", "UTC") or "UTC"

        self._db = db or GitRepoStatsDB()
        self.filter = repo_filter or RepositoryFilter(**resolved_options)
        self.traffic = traffic or TrafficStats(self._db, **resolved_options)
        self.display = display or DisplaySettings(**resolved_options)

        more_collabs = resolved_options.get("more_collabs", 0)
        try:
            self.more_collabs = int(more_collabs) if more_collabs else 0
        except ValueError:
            self.more_collabs = 0

    @staticmethod
    def _load_config(config_path: str = "config.yml") -> dict:
        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                loaded = yaml.safe_load(fh) or {}
                return loaded if isinstance(loaded, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
        for key, value in (src or {}).items():
            if isinstance(value, dict) and isinstance(dst.get(key), dict):
                Environment._deep_merge(dst[key], value)
            else:
                dst[key] = value

    @staticmethod
    def _resolve_options(
        config: Dict[str, Any],
        stats: Dict[str, Any],
        explicit: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve runtime options from config and explicit overrides.

        Source of truth is ``config.yml``. Explicit kwargs override config values.
        """
        if not isinstance(stats, dict):
            stats = {}

        resolved = {
            "timezone": config.get("timezone") or "UTC",
            "exclude_repos": stats.get("excluded_repos", ""),
            "exclude_langs": stats.get("excluded_langs", ""),
            "include_forked_repos": stats.get("include_forked_repos", "false"),
            "exclude_contrib_repos": stats.get("exclude_contrib_repos", "false"),
            "exclude_archive_repos": stats.get("exclude_archive_repos", "true"),
            "exclude_private_repos": stats.get("exclude_private_repos", "false"),
            "exclude_public_repos": stats.get("exclude_public_repos", "false"),
            "mask_private_repos": stats.get("mask_private_repos", "true"),
            "store_repo_view_count": stats.get("store_repo_views", "true"),
            "store_repo_clone_count": stats.get("store_repo_clones", "true"),
            "more_collabs": stats.get("more_collabs", 0),
            "manually_added_repos": stats.get("manually_added_repos", ""),
            "only_included_repos": stats.get("only_included_repos", ""),
            "show_total_contributions": stats.get("show_total_contributions", "true"),
            "show_repositories": stats.get("show_repositories", "true"),
            "show_lines_changed": stats.get("show_lines_changed", "true"),
            "show_avg_percent": stats.get("show_avg_percent", "true"),
            "show_collaborators": stats.get("show_collaborators", "true"),
            "show_contributors": stats.get("show_contributors", "true"),
            "show_views": stats.get("show_views", "true"),
            "show_clones": stats.get("show_clones", "true"),
            "show_forks": stats.get("show_forks", "true"),
            "show_stars": stats.get("show_stars", "true"),
            "show_pull_requests": stats.get("show_pull_requests", "true"),
            "show_issues": stats.get("show_issues", "true"),
        }

        for key, value in explicit.items():
            if value is not None and value != "":
                resolved[key] = value

        return resolved
