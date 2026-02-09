"""
Mock StatsCollector and Environment for testing SVG generation without GitHub API.
"""

from typing import Dict, Any, Set, Tuple


class MockEnvironment:
    """
    A mock implementation of Environment for testing.
    All show_* properties return True by default.
    """

    def __init__(self, **kwargs):
        self.show_total_contributions = kwargs.get("show_total_contributions", True)
        self.show_repositories = kwargs.get("show_repositories", True)
        self.show_lines_changed = kwargs.get("show_lines_changed", True)
        self.show_avg_percent = kwargs.get("show_avg_percent", True)
        self.show_collaborators = kwargs.get("show_collaborators", True)
        self.show_contributors = kwargs.get("show_contributors", True)
        self.show_views = kwargs.get("show_views", True)
        self.show_clones = kwargs.get("show_clones", True)
        self.show_forks = kwargs.get("show_forks", True)
        self.show_stars = kwargs.get("show_stars", True)
        self.show_pull_requests = kwargs.get("show_pull_requests", True)
        self.show_issues = kwargs.get("show_issues", True)


class MockStatsCollector:
    """
    A mock implementation of StatsCollector that returns predefined data.
    Used for testing SVG templates without requiring GitHub API access.
    """

    def __init__(self, data: Dict[str, Any] = None):
        """
        Initialize with optional custom mock data.

        :param data: Dictionary with mock values for stats properties.
        """
        self._data = data or self._default_data()

    @staticmethod
    def _default_data() -> Dict[str, Any]:
        """Returns default mock data for testing."""
        return {
            "name": "User's",
            "stargazers": 567,
            "forks": 89,
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
        }

    @property
    async def name(self) -> str:
        return self._data["name"]

    @property
    async def stargazers(self) -> int:
        return self._data["stargazers"]

    @property
    async def forks(self) -> int:
        return self._data["forks"]

    @property
    async def total_contributions(self) -> int:
        return self._data["total_contributions"]

    @property
    async def languages(self) -> Dict[str, Any]:
        return self._data["languages"]

    @property
    async def repos(self) -> Set[str]:
        return self._data["repos"]

    @property
    async def lines_changed(self) -> Tuple[int, int]:
        return self._data["lines_changed"]

    @property
    async def avg_contribution_percent(self) -> str:
        return self._data["avg_contribution_percent"]

    @property
    async def views(self) -> int:
        return self._data["views"]

    @property
    async def clones(self) -> int:
        return self._data["clones"]

    @property
    async def collaborators(self) -> int:
        return self._data["collaborators"]

    @property
    async def contributors(self) -> Set[str]:
        return self._data["contributors"]

    @property
    async def views_from_date(self) -> str:
        return self._data["views_from_date"]

    @property
    async def clones_from_date(self) -> str:
        return self._data["clones_from_date"]

    @property
    async def pull_requests(self) -> int:
        return self._data["pull_requests"]

    @property
    async def issues(self) -> int:
        return self._data["issues"]

    @property
    async def current_streak(self) -> int:
        return self._data["current_streak"]

    @property
    async def longest_streak(self) -> int:
        return self._data["longest_streak"]

    @property
    async def current_streak_range(self) -> str:
        return self._data["current_streak_range"]

    @property
    async def longest_streak_range(self) -> str:
        return self._data["longest_streak_range"]

    @property
    async def recent_contributions(self) -> list:
        return self._data["recent_contributions"]
