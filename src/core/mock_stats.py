"""Mock classes for testing SVG generation without GitHub API."""

import os
from typing import Dict, Any, List, Set, Tuple
from src.utils.privacy import mask_weekly_commits, should_mask_private
from src.utils.helpers import to_bool


class MockDisplaySettings:
    """Mock display settings for testing."""

    def __init__(self, **kwargs):
        self.show_total_contributions = to_bool(kwargs.get("show_total_contributions"), True)
        self.show_repositories = to_bool(kwargs.get("show_repositories"), True)
        self.show_lines_changed = to_bool(kwargs.get("show_lines_changed"), True)
        self.show_avg_percent = to_bool(kwargs.get("show_avg_percent"), True)
        self.show_collaborators = to_bool(kwargs.get("show_collaborators"), True)
        self.show_contributors = to_bool(kwargs.get("show_contributors"), True)
        self.show_views = to_bool(kwargs.get("show_views"), True)
        self.show_clones = to_bool(kwargs.get("show_clones"), True)
        self.show_forks = to_bool(kwargs.get("show_forks"), True)
        self.show_stars = to_bool(kwargs.get("show_stars"), True)
        self.show_pull_requests = to_bool(kwargs.get("show_pull_requests"), True)
        self.show_issues = to_bool(kwargs.get("show_issues"), True)


class MockEnvironment:
    """Mock Environment for testing."""

    def __init__(self, **kwargs):
        self.timezone = kwargs.get("timezone", "UTC") or "UTC"
        self.display = MockDisplaySettings(**kwargs)


class MockStatsCollector:
    """Mock StatsCollector that returns predefined data for template testing."""

    def __init__(self, data: Dict[str, Any] = None):
        self._data = data or self._default_data()

    @staticmethod
    def _default_data() -> Dict[str, Any]:
        return {
            "name": "User's",
            "stargazers": 567,
            "forks": 89,
            "followers": 142,
            "following": 87,
            "total_contributions": 2345,
            "languages": {
                "Python": {"size": 45000, "prop": 45.0, "color": "#3572A5"},
                "TypeScript": {"size": 25000, "prop": 25.0, "color": "#3178c6"},
                "JavaScript": {"size": 15000, "prop": 15.0, "color": "#f1e05a"},
                "Rust": {"size": 8000, "prop": 8.0, "color": "#dea584"},
                "Go": {"size": 4000, "prop": 4.0, "color": "#00ADD8"},
                "Shell": {"size": 3000, "prop": 3.0, "color": "#89e051"},
            },
            "repos": {"repo1", "repo2", "repo3"},
            "lines_changed": (100000, 23456),
            "avg_contribution_percent": "78.5%",
            "views": 12345,
            "clones": 1234,
            "collaborators": 15,
            "contributors": {"user1", "user2", "user3"},
            "views_from_date": "2024-01-01",
            "clones_from_date": "2024-01-01",
            "pull_requests": 45,
            "issues": 23,
            "current_streak": 15,
            "longest_streak": 42,
            "current_streak_range": "Jan 25 - Feb 9",
            "longest_streak_range": "Mar 1 - Apr 12, 2024",
            "recent_contributions": [3, 7, 2, 12, 5, 8, 0, 4, 9, 6],
            "weekly_commit_schedule": [
                {
                    "repo": "leo-git-statistics",
                    "sha": "a1b2c3d4e5f6",
                    "description": "Improve overview card layout",
                    "is_private": False,
                    "timestamp": "2026-02-09T10:12:00+00:00",
                },
                {
                    "repo": "leo-git-statistics",
                    "sha": "b2c3d4e5f6a1",
                    "description": "Refactor generators registry",
                    "is_private": False,
                    "timestamp": "2026-02-10T18:45:00+00:00",
                },
                {
                    "repo": "private/research-notes",
                    "sha": "c3d4e5f6a1b2",
                    "description": "c3d4e5f",
                    "is_private": True,
                    "timestamp": "2026-02-11T02:21:00+00:00",
                },
                {
                    "repo": "portfolio-site",
                    "sha": "d4e5f6a1b2c3",
                    "description": "Update hero section",
                    "is_private": False,
                    "timestamp": "2026-02-12T14:30:00+00:00",
                },
                {
                    "repo": "private/experiments",
                    "sha": "e5f6a1b2c3d4",
                    "description": "e5f6a1b",
                    "is_private": True,
                    "timestamp": "2026-02-13T21:08:00+00:00",
                },
            ],
            "stats_history": [
                {"date": "2026-02-08", "total_stars": 520, "total_followers": 130, "total_following": 82, "total_contributions": 2100, "total_forks": 72, "total_pull_requests": 35, "total_issues": 18},
                {"date": "2026-02-09", "total_stars": 525, "total_followers": 131, "total_following": 83, "total_contributions": 2130, "total_forks": 74, "total_pull_requests": 36, "total_issues": 18},
                {"date": "2026-02-10", "total_stars": 530, "total_followers": 133, "total_following": 83, "total_contributions": 2170, "total_forks": 76, "total_pull_requests": 37, "total_issues": 19},
                {"date": "2026-02-11", "total_stars": 538, "total_followers": 134, "total_following": 84, "total_contributions": 2200, "total_forks": 78, "total_pull_requests": 38, "total_issues": 19},
                {"date": "2026-02-12", "total_stars": 542, "total_followers": 136, "total_following": 85, "total_contributions": 2240, "total_forks": 80, "total_pull_requests": 39, "total_issues": 20},
                {"date": "2026-02-13", "total_stars": 548, "total_followers": 137, "total_following": 85, "total_contributions": 2265, "total_forks": 82, "total_pull_requests": 40, "total_issues": 21},
                {"date": "2026-02-14", "total_stars": 553, "total_followers": 138, "total_following": 86, "total_contributions": 2290, "total_forks": 84, "total_pull_requests": 41, "total_issues": 21},
                {"date": "2026-02-15", "total_stars": 558, "total_followers": 139, "total_following": 86, "total_contributions": 2310, "total_forks": 85, "total_pull_requests": 43, "total_issues": 22},
                {"date": "2026-02-16", "total_stars": 562, "total_followers": 140, "total_following": 87, "total_contributions": 2330, "total_forks": 87, "total_pull_requests": 44, "total_issues": 22},
                {"date": "2026-02-17", "total_stars": 567, "total_followers": 142, "total_following": 87, "total_contributions": 2345, "total_forks": 89, "total_pull_requests": 45, "total_issues": 23},
            ],
        }

    async def get_name(self) -> str:
        return self._data["name"]

    async def get_stargazers(self) -> int:
        return self._data["stargazers"]

    async def get_forks(self) -> int:
        return self._data["forks"]

    async def get_followers(self) -> int:
        return self._data["followers"]

    async def get_following(self) -> int:
        return self._data["following"]

    async def get_total_contributions(self) -> int:
        return self._data["total_contributions"]

    async def get_languages(self) -> Dict[str, Any]:
        return self._data["languages"]

    async def get_repos(self) -> Set[str]:
        return self._data["repos"]

    async def get_lines_changed(self) -> Tuple[int, int]:
        return self._data["lines_changed"]

    async def get_avg_contribution_percent(self) -> str:
        return self._data["avg_contribution_percent"]

    async def get_views(self) -> int:
        return self._data["views"]

    async def get_clones(self) -> int:
        return self._data["clones"]

    async def get_collaborators(self) -> int:
        return self._data["collaborators"]

    async def get_contributors(self) -> Set[str]:
        return self._data["contributors"]

    async def get_views_from_date(self) -> str:
        return self._data["views_from_date"]

    async def get_clones_from_date(self) -> str:
        return self._data["clones_from_date"]

    async def get_pull_requests(self) -> int:
        return self._data["pull_requests"]

    async def get_issues(self) -> int:
        return self._data["issues"]

    async def get_current_streak(self) -> int:
        return self._data["current_streak"]

    async def get_longest_streak(self) -> int:
        return self._data["longest_streak"]

    async def get_current_streak_range(self) -> str:
        return self._data["current_streak_range"]

    async def get_longest_streak_range(self) -> str:
        return self._data["longest_streak_range"]

    async def get_recent_contributions(self) -> list:
        return self._data["recent_contributions"]

    async def get_weekly_commit_schedule(self) -> list:
        return mask_weekly_commits(
            self._data["weekly_commit_schedule"],
            "mock-user",
            mask_enabled=should_mask_private(os.getenv("MASK_PRIVATE_REPOS")),
        )

    async def get_stats_history(self) -> List[Dict[str, Any]]:
        return self._data["stats_history"]
