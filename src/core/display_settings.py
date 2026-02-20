#!/usr/bin/python3
"""Display settings for controlling which stats are shown."""

from os import getenv

from src.utils.helpers import to_bool


class DisplaySettings:
    """Manages visual toggle settings for statistics display."""

    def __init__(self, **kwargs):
        self.show_total_contributions = to_bool(
            kwargs.get("show_total_contributions", getenv("SHOW_TOTAL_CONTRIBUTIONS")),
            True,
        )
        self.show_repositories = to_bool(
            kwargs.get("show_repositories", getenv("SHOW_REPOSITORIES")), True
        )
        self.show_lines_changed = to_bool(
            kwargs.get("show_lines_changed", getenv("SHOW_LINES_CHANGED")), True
        )
        self.show_avg_percent = to_bool(
            kwargs.get("show_avg_percent", getenv("SHOW_AVG_PERCENT")), True
        )
        self.show_collaborators = to_bool(
            kwargs.get("show_collaborators", getenv("SHOW_COLLABORATORS")), True
        )
        self.show_contributors = to_bool(
            kwargs.get("show_contributors", getenv("SHOW_CONTRIBUTORS")), True
        )
        self.show_views = to_bool(kwargs.get("show_views", getenv("SHOW_VIEWS")), True)
        self.show_clones = to_bool(
            kwargs.get("show_clones", getenv("SHOW_CLONES")), True
        )
        self.show_forks = to_bool(kwargs.get("show_forks", getenv("SHOW_FORKS")), True)
        self.show_stars = to_bool(kwargs.get("show_stars", getenv("SHOW_STARS")), True)
        self.show_pull_requests = to_bool(
            kwargs.get("show_pull_requests", getenv("SHOW_PULL_REQUESTS")), True
        )
        self.show_issues = to_bool(
            kwargs.get("show_issues", getenv("SHOW_ISSUES")), True
        )
