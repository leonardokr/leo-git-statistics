"""
Segregated Protocol definitions for stats providers and infrastructure.

Defines narrow interfaces so each generator depends only on the
subset of statistics it actually uses.
"""

from typing import Dict, Any, List, Set, Tuple, Protocol, runtime_checkable


@runtime_checkable
class StreakProvider(Protocol):
    """
    Provides streak and total contribution statistics.

    Used by :class:`StreakGenerator`.
    """

    async def get_current_streak(self) -> int: ...
    async def get_longest_streak(self) -> int: ...
    async def get_current_streak_range(self) -> str: ...
    async def get_longest_streak_range(self) -> str: ...
    async def get_total_contributions(self) -> int: ...


@runtime_checkable
class BatteryProvider(Protocol):
    """
    Provides streak and recent contribution data for battery visualization.

    Used by :class:`StreakBatteryGenerator`.
    """

    async def get_current_streak(self) -> int: ...
    async def get_longest_streak(self) -> int: ...
    async def get_current_streak_range(self) -> str: ...
    async def get_longest_streak_range(self) -> str: ...
    async def get_recent_contributions(self) -> list: ...


@runtime_checkable
class LanguageProvider(Protocol):
    """
    Provides programming language statistics.

    Used by :class:`LanguagesGenerator` and :class:`LanguagesPuzzleGenerator`.
    """

    async def get_languages(self) -> Dict[str, Any]: ...


@runtime_checkable
class OverviewProvider(Protocol):
    """
    Provides general overview statistics for the profile card.

    Used by :class:`OverviewGenerator`.
    """

    async def get_name(self) -> str: ...
    async def get_stargazers(self) -> int: ...
    async def get_forks(self) -> int: ...
    async def get_followers(self) -> int: ...
    async def get_following(self) -> int: ...
    async def get_views(self) -> int: ...
    async def get_clones(self) -> int: ...
    async def get_total_contributions(self) -> int: ...
    async def get_lines_changed(self) -> Tuple[int, int]: ...
    async def get_avg_contribution_percent(self) -> str: ...
    async def get_repos(self) -> Set[str]: ...
    async def get_collaborators(self) -> int: ...
    async def get_contributors(self) -> Set[str]: ...
    async def get_pull_requests(self) -> int: ...
    async def get_issues(self) -> int: ...
    async def get_views_from_date(self) -> str: ...
    async def get_clones_from_date(self) -> str: ...


@runtime_checkable
class CommitCalendarProvider(Protocol):
    """
    Provides commit events for weekly calendar visualization.

    Used by :class:`CommitCalendarGenerator`.
    """

    async def get_weekly_commit_schedule(self) -> List[Dict[str, Any]]: ...


@runtime_checkable
class StatsHistoryProvider(Protocol):
    """
    Provides historical statistics snapshots for line chart visualization.

    Used by :class:`StatsHistoryGenerator`.
    """

    async def get_stats_history(self) -> list: ...
    async def get_name(self) -> str: ...


@runtime_checkable
class TemplateRenderer(Protocol):
    """
    Renders templates with variable replacements and saves to disk.
    """

    def render_and_save(
        self,
        template_file: str,
        output_filename_base: str,
        replacements: Dict[str, str],
        theme_suffix: str = "",
    ) -> None: ...


@runtime_checkable
class Formatter(Protocol):
    """
    Formats statistics values into display-ready strings and SVG fragments.
    """

    @staticmethod
    def format_name(name: str) -> str: ...

    @staticmethod
    def format_number(number: Any) -> str: ...

    @staticmethod
    def format_language_progress(
        languages: Dict[str, Dict[str, Any]], total_width: int = 455
    ) -> str: ...

    @staticmethod
    def format_language_list(
        languages: Dict[str, Dict[str, Any]],
        max_items: int = 8,
        text_color: str = "#24292f",
        percent_color: str = "#57606a",
    ) -> str: ...

    @staticmethod
    def format_puzzle_blocks(
        languages: Dict[str, Dict[str, Any]],
        width: int = 400,
        height: int = 200,
        hue: int = 210,
        saturation_range: List[int] = None,
        lightness_range: List[int] = None,
        hue_spread: int = 60,
        gap: int = 2,
    ) -> str: ...


@runtime_checkable
class Database(Protocol):
    """
    Persistence interface for repository traffic statistics.
    """

    def set_views_count(self, count: Any) -> None: ...
    def set_views_from_date(self, date: str) -> None: ...
    def set_views_to_date(self, date: str) -> None: ...
    def set_clones_count(self, count: Any) -> None: ...
    def set_clones_from_date(self, date: str) -> None: ...
    def set_clones_to_date(self, date: str) -> None: ...
