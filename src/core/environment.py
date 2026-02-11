#!/usr/bin/python3
"""Environment and configuration management."""

from os import getenv

from src.db.db import GitRepoStatsDB
from src.core.repository_filter import RepositoryFilter
from src.core.traffic_stats import TrafficStats
from src.core.display_settings import DisplaySettings


class Environment:
    """Manages GitHub credentials and aggregates configuration settings."""

    def __init__(self, username: str, access_token: str, **kwargs):
        self.username = username
        self.access_token = access_token

        self._db = GitRepoStatsDB()
        self.filter = RepositoryFilter(**kwargs)
        self.traffic = TrafficStats(self._db, **kwargs)
        self.display = DisplaySettings(**kwargs)

        more_collabs = kwargs.get("more_collabs", getenv("MORE_COLLABS"))
        try:
            self.more_collabs = int(more_collabs) if more_collabs else 0
        except ValueError:
            self.more_collabs = 0
