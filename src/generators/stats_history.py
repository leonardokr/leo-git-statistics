"""Stats history multi-series line chart SVG generator."""

from __future__ import annotations

from typing import Any, Dict, List

from src.generators.base import BaseGenerator, register_generator
from src.core.protocols import StatsHistoryProvider
from src.presentation.visual_algorithms import generate_palette_colors


@register_generator
class StatsHistoryGenerator(BaseGenerator):
    """Generates a multi-series line chart SVG showing stats over time."""

    stats: StatsHistoryProvider

    OUTPUT_NAME = "stats_history"
    TEMPLATE_NAME = "stats_history.svg"

    _SVG_WIDTH = 900
    _CHART_X = 80
    _CHART_Y = 70
    _CHART_WIDTH = 760
    _CHART_HEIGHT = 250
    _POINT_RADIUS = 4
    _LINE_WIDTH = 2.5
    _LEGEND_START_Y = 348
    _LEGEND_ITEM_WIDTH = 170
    _LEGEND_ROW_HEIGHT = 18
    _LEGEND_COLUMNS = 4
    _FOOTER_HEIGHT = 6
    _BOTTOM_PADDING = 18

    _SERIES = [
        "total_stars",
        "total_followers",
        "total_following",
        "total_contributions",
        "total_forks",
        "total_pull_requests",
        "total_issues",
    ]

    _SERIES_LABELS = {
        "total_stars": "Stars",
        "total_followers": "Followers",
        "total_following": "Following",
        "total_contributions": "Contributions",
        "total_forks": "Forks",
        "total_pull_requests": "Pull Requests",
        "total_issues": "Issues",
    }

    async def generate(self) -> None:
        """Generate stats history line chart SVG for all enabled themes."""
        history = await self.stats.get_stats_history()
        if not history:
            return

        name = await self.stats.get_name()
        visible_series = self._filter_active_series(history)
        if not visible_series:
            return

        y_max = self._compute_y_max(history, visible_series)
        y_ticks = self._compute_y_ticks(y_max)
        dates = [entry.get("date", "") for entry in history]

        svg_height = self._compute_svg_height(len(visible_series))
        footer_y = svg_height - self._FOOTER_HEIGHT

        chart_title = self._escape_xml(f"{name} Stats History")
        date_range = f"{dates[0]} to {dates[-1]}" if len(dates) > 1 else dates[0]

        base_replacements = {
            "chart_title": chart_title,
            "chart_subtitle": f"Period: {date_range}",
            "svg_width": self._SVG_WIDTH,
            "svg_height": svg_height,
            "viewbox_width": self._SVG_WIDTH,
            "viewbox_height": svg_height,
            "clip_height": svg_height,
            "footer_y": footer_y,
        }

        def theme_callback(colors: Dict[str, Any]) -> Dict[str, Any]:
            palette = generate_palette_colors(
                count=max(len(visible_series), 1),
                hue=int(colors.get("line_chart_hue", 210)),
                saturation_range=self._parse_range(
                    colors.get("line_chart_saturation_range", [60, 85])
                ),
                lightness_range=self._parse_range(
                    colors.get("line_chart_lightness_range", [40, 65])
                ),
                hue_spread=int(colors.get("line_chart_hue_spread", 120)),
            )
            color_map = {
                series: palette[idx % len(palette)]
                for idx, series in enumerate(visible_series)
            }
            return {
                "y_axis_labels": self._build_y_axis_labels(y_ticks, colors),
                "x_axis_labels": self._build_x_axis_labels(dates, colors),
                "grid_lines": self._build_grid_lines(y_ticks),
                "chart_lines": self._build_chart_lines(
                    history, visible_series, color_map, y_max
                ),
                "legend_items": self._build_legend_items(visible_series, color_map),
            }

        self.render_for_all_themes(
            self.TEMPLATE_NAME,
            self.OUTPUT_NAME,
            base_replacements,
            theme_callback=theme_callback,
        )

    def _filter_active_series(self, history: List[Dict[str, Any]]) -> List[str]:
        """Return series that have at least one non-zero value.

        :param history: List of snapshot dicts.
        :returns: Filtered series keys.
        :rtype: list[str]
        """
        active = []
        for series in self._SERIES:
            for entry in history:
                if entry.get(series, 0) not in (0, None):
                    active.append(series)
                    break
        return active

    def _compute_y_max(
        self, history: List[Dict[str, Any]], series: List[str]
    ) -> int:
        """Compute the maximum Y value across all active series.

        :param history: Snapshot data.
        :param series: Active series keys.
        :returns: Maximum value found.
        :rtype: int
        """
        max_val = 0
        for entry in history:
            for s in series:
                val = entry.get(s, 0) or 0
                if val > max_val:
                    max_val = val
        return max(max_val, 1)

    def _compute_y_ticks(self, y_max: int) -> List[int]:
        """Compute Y-axis tick values with nice rounding.

        :param y_max: Raw maximum value.
        :returns: List of tick values from 0 to the nice max.
        :rtype: list[int]
        """
        nice = self._nice_max(y_max)
        step = nice // 5 if nice >= 5 else 1
        return list(range(0, nice + 1, step))

    def _build_grid_lines(self, y_ticks: List[int]) -> str:
        """Build horizontal SVG grid lines.

        :param y_ticks: Y-axis tick values.
        :returns: SVG fragment string.
        :rtype: str
        """
        lines = []
        y_max = y_ticks[-1] if y_ticks else 1
        for tick in y_ticks:
            y = self._CHART_Y + self._CHART_HEIGHT - (
                tick / y_max * self._CHART_HEIGHT
            )
            lines.append(
                f'<line x1="{self._CHART_X}" y1="{y:.1f}" '
                f'x2="{self._CHART_X + self._CHART_WIDTH}" y2="{y:.1f}" '
                f'class="grid-line" />'
            )
        return "".join(lines)

    def _build_y_axis_labels(
        self, y_ticks: List[int], colors: Dict[str, Any]
    ) -> str:
        """Build Y-axis value labels.

        :param y_ticks: Tick values.
        :param colors: Theme color dict.
        :returns: SVG fragment string.
        :rtype: str
        """
        labels = []
        y_max = y_ticks[-1] if y_ticks else 1
        for tick in y_ticks:
            y = self._CHART_Y + self._CHART_HEIGHT - (
                tick / y_max * self._CHART_HEIGHT
            )
            labels.append(
                f'<text x="{self._CHART_X - 8}" y="{y:.1f}" '
                f'text-anchor="end" dominant-baseline="central" '
                f'class="axis-label">{self._format_tick(tick)}</text>'
            )
        return "".join(labels)

    def _build_x_axis_labels(
        self, dates: List[str], colors: Dict[str, Any]
    ) -> str:
        """Build X-axis date labels.

        :param dates: List of date strings.
        :param colors: Theme color dict.
        :returns: SVG fragment string.
        :rtype: str
        """
        if not dates:
            return ""
        labels = []
        n = len(dates)
        max_labels = 10
        step = max(1, n // max_labels)
        y = self._CHART_Y + self._CHART_HEIGHT + 16
        for i in range(0, n, step):
            x = self._CHART_X + (i / max(n - 1, 1)) * self._CHART_WIDTH
            short_date = dates[i][5:] if len(dates[i]) >= 10 else dates[i]
            labels.append(
                f'<text x="{x:.1f}" y="{y}" text-anchor="middle" '
                f'class="axis-label">{short_date}</text>'
            )
        if (n - 1) % step != 0 and n > 1:
            x = self._CHART_X + self._CHART_WIDTH
            short_date = dates[-1][5:] if len(dates[-1]) >= 10 else dates[-1]
            labels.append(
                f'<text x="{x:.1f}" y="{y}" text-anchor="middle" '
                f'class="axis-label">{short_date}</text>'
            )
        return "".join(labels)

    def _build_chart_lines(
        self,
        history: List[Dict[str, Any]],
        series: List[str],
        color_map: Dict[str, str],
        y_max: int,
    ) -> str:
        """Build polylines and data point circles for each series.

        :param history: Snapshot data.
        :param series: Active series keys.
        :param color_map: Series-to-color mapping.
        :param y_max: Y-axis maximum for scaling.
        :returns: SVG fragment string.
        :rtype: str
        """
        nice = self._nice_max(y_max)
        n = len(history)
        fragments = []
        for s in series:
            color = color_map[s]
            points = []
            circles = []
            for i, entry in enumerate(history):
                val = entry.get(s, 0) or 0
                x = self._CHART_X + (i / max(n - 1, 1)) * self._CHART_WIDTH
                y = self._CHART_Y + self._CHART_HEIGHT - (
                    val / nice * self._CHART_HEIGHT
                )
                points.append(f"{x:.1f},{y:.1f}")
                circles.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{self._POINT_RADIUS}" '
                    f'fill="{color}" />'
                )
            polyline = (
                f'<polyline points="{" ".join(points)}" '
                f'fill="none" stroke="{color}" '
                f'stroke-width="{self._LINE_WIDTH}" '
                f'stroke-linecap="round" stroke-linejoin="round" />'
            )
            fragments.append(polyline)
            fragments.extend(circles)
        return "".join(fragments)

    def _build_legend_items(
        self, series: List[str], color_map: Dict[str, str]
    ) -> str:
        """Build legend with colored squares and series names.

        :param series: Active series keys.
        :param color_map: Series-to-color mapping.
        :returns: SVG fragment string.
        :rtype: str
        """
        items = []
        start_x = self._CHART_X
        start_y = self._LEGEND_START_Y
        for index, s in enumerate(series):
            row = index // self._LEGEND_COLUMNS
            col = index % self._LEGEND_COLUMNS
            x = start_x + col * self._LEGEND_ITEM_WIDTH
            y = start_y + row * self._LEGEND_ROW_HEIGHT
            label = self._SERIES_LABELS.get(s, s)
            items.append(
                f'<rect x="{x}" y="{y - 9}" width="10" height="10" '
                f'rx="2" ry="2" fill="{color_map[s]}" />'
                f'<text x="{x + 16}" y="{y}" class="legend-label">{label}</text>'
            )
        return "".join(items)

    def _compute_svg_height(self, series_count: int) -> int:
        """Compute card height according to legend rows.

        :param series_count: Number of active series.
        :returns: Dynamic SVG height.
        :rtype: int
        """
        rows = max(
            1, (series_count + self._LEGEND_COLUMNS - 1) // self._LEGEND_COLUMNS
        )
        return (
            self._LEGEND_START_Y
            + rows * self._LEGEND_ROW_HEIGHT
            + self._BOTTOM_PADDING
        )

    @staticmethod
    def _nice_max(value: int) -> int:
        """Round up to a visually clean Y-axis maximum.

        :param value: Raw maximum value.
        :returns: Rounded-up nice value.
        :rtype: int
        """
        if value <= 0:
            return 10
        if value <= 10:
            return 10
        magnitude = 1
        while magnitude * 10 < value:
            magnitude *= 10
        residual = value / magnitude
        if residual <= 1.5:
            return int(1.5 * magnitude)
        if residual <= 2:
            return 2 * magnitude
        if residual <= 3:
            return 3 * magnitude
        if residual <= 5:
            return 5 * magnitude
        return 10 * magnitude

    @staticmethod
    def _format_tick(value: int) -> str:
        """Format a numeric tick value for display.

        :param value: Tick value.
        :returns: Formatted string (e.g. '1.2k').
        :rtype: str
        """
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if value >= 1_000:
            return f"{value / 1_000:.1f}k"
        return str(value)

    @staticmethod
    def _escape_xml(value: str) -> str:
        """Escape basic XML entities.

        :param value: Raw string.
        :returns: Escaped text.
        :rtype: str
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
        """Parse theme range values into two integers.

        :param value: Sequence-like range value.
        :returns: Two-item integer range.
        :rtype: list[int]
        """
        if isinstance(value, list) and len(value) >= 2:
            return [int(value[0]), int(value[1])]
        return [60, 85]
