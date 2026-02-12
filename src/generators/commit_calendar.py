"""Weekly commit calendar SVG generator."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.generators.base import BaseGenerator, register_generator
from src.core.protocols import CommitCalendarProvider
from src.presentation.visual_algorithms import generate_palette_colors


@register_generator
class CommitCalendarGenerator(BaseGenerator):
    """
    Generates a weekly agenda-like SVG with commit blocks by repository.
    """

    stats: CommitCalendarProvider

    OUTPUT_NAME = "commit_calendar"
    TEMPLATE_NAME = "commit_calendar.svg"
    _DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _SVG_WIDTH = 900
    _GRID_X = 110
    _GRID_Y = 84
    _GRID_WIDTH = 707
    _GRID_HEIGHT = 240
    _DAY_WIDTH = 101
    _SLOT_HEIGHT = 10
    _DAY_LABEL_Y = 80
    _HOUR_LABEL_Y_START = 94
    _LEGEND_START_Y = 348
    _LEGEND_ITEM_WIDTH = 170
    _LEGEND_ROW_HEIGHT = 18
    _LEGEND_COLUMNS = 4
    _FOOTER_HEIGHT = 6
    _BOTTOM_PADDING = 18

    async def generate(self) -> None:
        """
        Generate commit calendar SVG for all enabled themes.
        """
        timezone_name = getattr(self.environment, "timezone", "UTC")
        tz = self._resolve_timezone(timezone_name)
        now_local = datetime.now(tz)
        week_start = now_local.date() - timedelta(days=now_local.weekday())
        week_end = week_start + timedelta(days=6)

        commits = await self.stats.get_weekly_commit_schedule()
        visible_repos = self._ordered_repositories(commits)
        svg_height = self._compute_svg_height(len(visible_repos))
        footer_y = svg_height - self._FOOTER_HEIGHT

        base_replacements = {
            "timezone_label": timezone_name,
            "week_range": f"{week_start.isoformat()} to {week_end.isoformat()}",
            "day_labels": self._build_day_labels(),
            "hour_labels": self._build_hour_labels(),
            "grid_lines": self._build_grid_lines(),
            "svg_width": self._SVG_WIDTH,
            "svg_height": svg_height,
            "viewbox_width": self._SVG_WIDTH,
            "viewbox_height": svg_height,
            "clip_height": svg_height,
            "footer_y": footer_y,
        }

        def theme_callback(colors: Dict[str, Any]) -> Dict[str, Any]:
            palette = generate_palette_colors(
                count=max(len(visible_repos), 1),
                hue=int(colors["calendar_hue"]),
                saturation_range=self._parse_range(colors["calendar_saturation_range"]),
                lightness_range=self._parse_range(colors["calendar_lightness_range"]),
                hue_spread=int(colors["calendar_hue_spread"]),
            )
            color_map = self._build_repo_color_map(visible_repos, palette)
            return {
                "calendar_title_color": colors["calendar_title_color"],
                "calendar_subtitle_color": colors["calendar_subtitle_color"],
                "calendar_day_label_color": colors["calendar_day_label_color"],
                "calendar_hour_label_color": colors["calendar_hour_label_color"],
                "calendar_grid_color": colors["calendar_grid_color"],
                "calendar_grid_opacity": colors["calendar_grid_opacity"],
                "calendar_legend_text_color": colors["calendar_legend_text_color"],
                "calendar_slot_opacity": colors["calendar_slot_opacity"],
                "commit_blocks": self._build_commit_blocks(commits, color_map, tz),
                "legend_items": self._build_legend_items(visible_repos, color_map),
            }

        self.render_for_all_themes(
            self.TEMPLATE_NAME,
            self.OUTPUT_NAME,
            base_replacements,
            theme_callback=theme_callback,
        )

    def _ordered_repositories(self, commits: List[Dict[str, Any]]) -> List[str]:
        """
        Order repositories by commit frequency.

        :param commits: Commit event list.
        :return: Ordered repository names.
        """
        counts: Dict[str, int] = {}
        for commit in commits:
            repo = commit.get("repo", "unknown")
            counts[repo] = counts.get(repo, 0) + 1
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return [name for (name, _) in ordered[:10]]

    def _build_repo_color_map(self, repos: List[str], palette: List[str]) -> Dict[str, str]:
        """
        Build deterministic colors for repository legend.

        :param repos: Ordered repository names.
        :return: Mapping repo name to color hex.
        """
        return {repo: palette[idx % len(palette)] for idx, repo in enumerate(repos)}

    def _build_day_labels(self) -> str:
        """
        Build SVG text nodes for day labels.

        :return: SVG fragment string.
        """
        x_start = self._GRID_X
        day_width = self._DAY_WIDTH
        labels = []
        for index, day in enumerate(self._DAY_LABELS):
            x = x_start + index * day_width + (day_width / 2)
            labels.append(
                f'<text x="{x:.1f}" y="{self._DAY_LABEL_Y}" text-anchor="middle" class="day-label">{day}</text>'
            )
        return "".join(labels)

    def _build_hour_labels(self) -> str:
        """
        Build SVG text nodes for hourly labels.

        :return: SVG fragment string.
        """
        labels = []
        y_start = self._HOUR_LABEL_Y_START
        slot_height = self._SLOT_HEIGHT
        for hour in (0, 4, 8, 12, 16, 20):
            y = y_start + hour * slot_height
            labels.append(f'<text x="56" y="{y}" class="hour-label">{hour:02d}:00</text>')
        labels.append(f'<text x="56" y="{y_start + 24 * slot_height}" class="hour-label">23:59</text>')
        return "".join(labels)

    def _build_grid_lines(self) -> str:
        """
        Build SVG lines for the weekly grid.

        :return: SVG fragment string.
        """
        x_start = self._GRID_X
        y_start = self._GRID_Y
        width = self._GRID_WIDTH
        height = self._GRID_HEIGHT
        day_width = self._DAY_WIDTH
        slot_height = self._SLOT_HEIGHT

        lines = []
        for d in range(8):
            x = x_start + d * day_width
            lines.append(
                f'<line x1="{x}" y1="{y_start}" x2="{x}" y2="{y_start + height}" class="grid-line" />'
            )
        for h in range(25):
            y = y_start + h * slot_height
            lines.append(
                f'<line x1="{x_start}" y1="{y}" x2="{x_start + width}" y2="{y}" class="grid-line" />'
            )
        return "".join(lines)

    def _build_commit_blocks(
        self, commits: List[Dict[str, Any]], color_map: Dict[str, str], tz: ZoneInfo
    ) -> str:
        """
        Build SVG rectangles for commit events.

        :param commits: Commit event list.
        :param color_map: Repo-to-color map.
        :param tz: Local timezone.
        :return: SVG fragment string.
        """
        x_start = self._GRID_X
        y_start = self._GRID_Y
        day_width = self._DAY_WIDTH
        slot_height = self._SLOT_HEIGHT
        grid_height = self._GRID_HEIGHT
        y_max = y_start + grid_height
        blocks: List[str] = []

        for item in commits:
            repo = item.get("repo", "unknown")
            if repo not in color_map:
                continue

            timestamp = item.get("timestamp")
            parsed = self._parse_timestamp(timestamp)
            if parsed is None:
                continue
            local_dt = parsed.astimezone(tz)

            day_index = local_dt.weekday()
            minute_of_day = local_dt.hour * 60 + local_dt.minute

            x = x_start + day_index * day_width + 2
            y = y_start + (minute_of_day / 60.0) * slot_height
            width = day_width - 4
            height = 8
            if y + height > y_max:
                y = y_max - height
            description = self._escape_xml(item.get("description", "Commit"))
            repo_name = self._escape_xml(repo)

            blocks.append(
                '<g>'
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{width}" height="{height}" '
                f'rx="1.5" ry="1.5" fill="{color_map[repo]}" opacity="{{{{ calendar_slot_opacity }}}}" />'
                f"<title>{repo_name} | {description} | {local_dt.strftime('%Y-%m-%d %H:%M')}</title>"
                "</g>"
            )

        return "".join(blocks)

    def _build_legend_items(self, repos: List[str], color_map: Dict[str, str]) -> str:
        """
        Build legend blocks with repository names.

        :param repos: Ordered repository names.
        :param color_map: Repo-to-color mapping.
        :return: SVG fragment string.
        """
        items: List[str] = []
        start_x = self._GRID_X
        start_y = self._LEGEND_START_Y
        item_width = self._LEGEND_ITEM_WIDTH
        for index, repo in enumerate(repos):
            row = index // self._LEGEND_COLUMNS
            col = index % self._LEGEND_COLUMNS
            x = start_x + col * item_width
            y = start_y + row * self._LEGEND_ROW_HEIGHT
            label = self._escape_xml(repo if len(repo) <= 26 else f"{repo[:23]}...")
            items.append(
                f'<rect x="{x}" y="{y - 9}" width="10" height="10" rx="2" ry="2" fill="{color_map[repo]}" />'
                f'<text x="{x + 16}" y="{y}" class="legend-label">{label}</text>'
            )
        return "".join(items)

    def _compute_svg_height(self, repo_count: int) -> int:
        """
        Compute card height according to legend rows.

        :param repo_count: Number of repositories shown in legend.
        :return: Dynamic SVG height.
        """
        rows = max(1, (repo_count + self._LEGEND_COLUMNS - 1) // self._LEGEND_COLUMNS)
        return self._LEGEND_START_Y + rows * self._LEGEND_ROW_HEIGHT + self._BOTTOM_PADDING

    @staticmethod
    def _resolve_timezone(timezone_name: str) -> ZoneInfo:
        """
        Resolve a timezone string to :class:`zoneinfo.ZoneInfo`.

        :param timezone_name: IANA timezone name.
        :return: Timezone instance.
        """
        try:
            return ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            return ZoneInfo("UTC")

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime | None:
        """
        Parse an ISO timestamp.

        :param value: Timestamp value.
        :return: Parsed datetime or ``None``.
        """
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _escape_xml(value: str) -> str:
        """
        Escape basic XML entities.

        :param value: Raw string.
        :return: Escaped text.
        """
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    @staticmethod
    def _parse_range(value: Any) -> List[int]:
        """
        Parse theme range values into two integers.

        :param value: Sequence-like range value.
        :return: Two-item integer range.
        """
        if isinstance(value, list) and len(value) >= 2:
            return [int(value[0]), int(value[1])]
        return [60, 85]
