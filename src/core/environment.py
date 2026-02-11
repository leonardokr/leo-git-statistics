#!/usr/bin/python3
"""Environment and configuration management."""

from os import getenv

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

        self._db = db or GitRepoStatsDB()
        self.filter = repo_filter or RepositoryFilter(**kwargs)
        self.traffic = traffic or TrafficStats(self._db, **kwargs)
        self.display = display or DisplaySettings(**kwargs)

        more_collabs = kwargs.get("more_collabs", getenv("MORE_COLLABS"))
        try:
            self.more_collabs = int(more_collabs) if more_collabs else 0
        except ValueError:
            self.more_collabs = 0
