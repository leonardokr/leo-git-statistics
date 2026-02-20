"""Static JSON-backed stats collector for offline SVG generation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from src.utils.privacy import (
    mask_repo_names,
    mask_weekly_commits,
    should_mask_private,
)


class StaticStatsCollector:
    """Load statistics from generated static JSON files."""

    def __init__(self, username: str, data_root: str):
        if not username or not username.strip():
            raise ValueError("GitHub username must not be empty")
        if not data_root or not str(data_root).strip():
            raise ValueError("STATIC_API_DATA_DIR must not be empty")

        self.username = username
        self._base = Path(data_root) / "users" / username
        self._overview = self._load_json("overview.json")
        self._languages = self._load_json("languages.json")
        self._streak = self._load_json("streak.json")
        self._recent = self._load_json("contributions-recent.json")
        self._weekly = self._load_json("commits-weekly.json")
        self._repos = self._load_json("repositories.json")
        self._full = self._load_json("stats-full.json")
        self._history = self._load_json("history.json", required=False) or {
            "username": username,
            "snapshots": [],
        }

    def _load_json(self, filename: str, *, required: bool = True) -> Optional[Dict[str, Any]]:
        path = self._base / filename
        if not path.exists():
            if required:
                raise FileNotFoundError(
                    f"Static data file not found: {path}. "
                    "Run api/generate_static_api.py first."
                )
            return None

        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    async def get_stats(self) -> None:
        return None

    async def get_contribution_calendar(self) -> None:
        return None

    async def get_name(self) -> str:
        return self._overview.get("name") or self.username

    async def get_stargazers(self) -> int:
        return int(self._overview.get("total_stars") or 0)

    async def get_forks(self) -> int:
        return int(self._overview.get("total_forks") or 0)

    async def get_followers(self) -> int:
        return int(self._overview.get("total_followers") or 0)

    async def get_following(self) -> int:
        return int(self._overview.get("total_following") or 0)

    async def get_total_contributions(self) -> int:
        return int(self._overview.get("total_contributions") or 0)

    async def get_languages(self) -> Dict[str, Any]:
        return self._languages.get("languages", {})

    async def get_languages_proportional(self) -> Dict[str, float]:
        languages = await self.get_languages()
        return {name: float(data.get("prop", 0)) for name, data in languages.items()}

    async def get_repos(self) -> Set[str]:
        repos = self._repos.get("repositories")
        if repos is None:
            repos = self._full.get("repositories", {}).get("list")
        if repos is None:
            return set()
        visibility = {}
        for commit in self._weekly.get("weekly_commits", []):
            repo = commit.get("repo")
            if repo:
                visibility[repo] = bool(commit.get("is_private"))
        masked = mask_repo_names(
            repos,
            visibility,
            self.username,
            mask_enabled=should_mask_private(os.getenv("MASK_PRIVATE_REPOS")),
        )
        return set(masked)

    async def get_lines_changed(self) -> Tuple[int, int]:
        return (
            int(self._overview.get("lines_added") or 0),
            int(self._overview.get("lines_deleted") or 0),
        )

    async def get_avg_contribution_percent(self) -> str:
        return str(self._overview.get("avg_contribution_percent") or "0.00%")

    async def get_views(self) -> int:
        return int(self._overview.get("total_views") or 0)

    async def get_views_from_date(self) -> str:
        return str(self._overview.get("views_from_date") or "0000-00-00")

    async def get_clones(self) -> int:
        return int(self._overview.get("total_clones") or 0)

    async def get_clones_from_date(self) -> str:
        return str(self._overview.get("clones_from_date") or "0000-00-00")

    async def get_collaborators(self) -> int:
        return int(self._overview.get("collaborators_count") or 0)

    async def get_contributors(self) -> Set[str]:
        count = int(self._overview.get("contributors_count") or 0)
        if count <= 0:
            return set()
        return {f"contributor_{idx}" for idx in range(count)}

    async def get_pull_requests(self) -> int:
        return int(self._overview.get("total_pull_requests") or 0)

    async def get_issues(self) -> int:
        return int(self._overview.get("total_issues") or 0)

    async def get_current_streak(self) -> int:
        return int(self._streak.get("current_streak") or 0)

    async def get_longest_streak(self) -> int:
        return int(self._streak.get("longest_streak") or 0)

    async def get_current_streak_range(self) -> str:
        return str(self._streak.get("current_streak_range") or "No streak")

    async def get_longest_streak_range(self) -> str:
        return str(self._streak.get("longest_streak_range") or "No streak")

    async def get_recent_contributions(self) -> list:
        return list(self._recent.get("recent_contributions", []))

    async def get_weekly_commit_schedule(self) -> list:
        return mask_weekly_commits(
            self._weekly.get("weekly_commits", []),
            self.username,
            mask_enabled=should_mask_private(os.getenv("MASK_PRIVATE_REPOS")),
        )

    async def get_stats_history(self) -> List[Dict[str, Any]]:
        return list(self._history.get("snapshots", []))
