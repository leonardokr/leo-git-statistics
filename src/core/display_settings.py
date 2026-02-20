#!/usr/bin/python3
"""Display settings for controlling which stats are shown."""

from src.utils.helpers import to_bool


class DisplaySettings:
    """Manages visual toggle settings for statistics display."""

    def __init__(self, **kwargs):
        self.show_total_contributions = to_bool(
            kwargs.get("show_total_contributions"),
            True,
        )
        self.show_repositories = to_bool(
            kwargs.get("show_repositories"), True
        )
        self.show_lines_changed = to_bool(
            kwargs.get("show_lines_changed"), True
        )
        self.show_avg_percent = to_bool(
            kwargs.get("show_avg_percent"), True
        )
        self.show_collaborators = to_bool(
            kwargs.get("show_collaborators"), True
        )
        self.show_contributors = to_bool(
            kwargs.get("show_contributors"), True
        )
        self.show_views = to_bool(kwargs.get("show_views"), True)
        self.show_clones = to_bool(
            kwargs.get("show_clones"), True
        )
        self.show_forks = to_bool(kwargs.get("show_forks"), True)
        self.show_stars = to_bool(kwargs.get("show_stars"), True)
        self.show_pull_requests = to_bool(
            kwargs.get("show_pull_requests"), True
        )
        self.show_issues = to_bool(
            kwargs.get("show_issues"), True
        )
