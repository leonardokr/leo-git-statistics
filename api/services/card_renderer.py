"""Render SVG card templates to strings for API responses."""

import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.stats_collector import StatsCollector
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.visual_algorithms import generate_palette_colors
from src.themes.loader import get_theme, list_themes

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "templates"


def _apply_replacements(content: str, replacements: Dict[str, Any]) -> str:
    """Apply placeholder replacements to template content.

    :param content: Raw SVG template string.
    :param replacements: Mapping of placeholder names to values.
    :returns: Rendered SVG string.
    :rtype: str
    """
    for placeholder, value in replacements.items():
        content = re.sub(rf"{{{{ {placeholder} }}}}", str(value), content)
    return content


def _render(template_name: str, theme_name: str, base_replacements: Dict[str, Any],
            theme_callback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None) -> str:
    """Render a single SVG template with a specific theme.

    :param template_name: Template filename inside ``src/templates/``.
    :param theme_name: Theme name to apply.
    :param base_replacements: Theme-independent placeholder values.
    :param theme_callback: Optional callback receiving theme colors and returning
        additional replacements.
    :returns: Rendered SVG string.
    :rtype: str
    :raises FileNotFoundError: If the template file does not exist.
    :raises ValueError: If the theme name is unknown.
    """
    theme = get_theme(theme_name)
    if theme is None:
        raise ValueError(f"Unknown theme: {theme_name}")

    template_path = TEMPLATE_DIR / template_name
    content = template_path.read_text(encoding="utf-8")

    colors = theme["colors"]
    replacements = base_replacements.copy()
    replacements.update(colors)

    if theme_callback:
        replacements.update(theme_callback(colors))

    return _apply_replacements(content, replacements)


def available_themes() -> List[str]:
    """Return all available theme names.

    :returns: Sorted list of theme names.
    :rtype: list[str]
    """
    return sorted(list_themes())


async def render_overview(collector: StatsCollector, theme: str, formatter: StatsFormatter) -> str:
    """Render the overview SVG card.

    :param collector: Populated stats collector.
    :param theme: Theme name.
    :param formatter: Stats formatter instance.
    :returns: Rendered SVG string.
    :rtype: str
    """
    lines_added, lines_removed = await collector.get_lines_changed()
    total_lines_changed = lines_added + lines_removed

    base = {
        "name": formatter.format_name(await collector.get_name()),
        "views": formatter.format_number(await collector.get_views()),
        "clones": formatter.format_number(await collector.get_clones()),
        "stars": formatter.format_number(await collector.get_stargazers()),
        "forks": formatter.format_number(await collector.get_forks()),
        "contributions": formatter.format_number(await collector.get_total_contributions()),
        "lines_changed": formatter.format_number(total_lines_changed),
        "avg_contribution_percent": await collector.get_avg_contribution_percent(),
        "repos": formatter.format_number(len(await collector.get_repos())),
        "collaborators": formatter.format_number(await collector.get_collaborators()),
        "contributors": formatter.format_number(max(len(await collector.get_contributors()) - 1, 0)),
        "views_from_date": f"Repository views (as of {await collector.get_views_from_date()})",
        "clones_from_date": f"Repository clones (as of {await collector.get_clones_from_date()})",
        "issues": formatter.format_number(await collector.get_issues()),
        "pull_requests": formatter.format_number(await collector.get_pull_requests()),
        "show_total_contributions": "table-row",
        "show_repositories": "table-row",
        "show_lines_changed": "table-row",
        "show_avg_percent": "table-row",
        "show_collaborators": "table-row",
        "show_contributors": "table-row",
        "show_views": "table-row",
        "show_clones": "table-row",
        "show_forks": "table-row",
        "show_stars": "table-row",
        "show_pull_requests": "table-row",
        "show_issues": "table-row",
    }

    return _render("overview.svg", theme, base)


async def render_languages(collector: StatsCollector, theme: str, formatter: StatsFormatter) -> str:
    """Render the languages SVG card.

    :param collector: Populated stats collector.
    :param theme: Theme name.
    :param formatter: Stats formatter instance.
    :returns: Rendered SVG string.
    :rtype: str
    """
    languages = await collector.get_languages()

    base = {
        "progress": formatter.format_language_progress(languages),
    }

    def theme_callback(colors: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "lang_list": formatter.format_language_list(
                languages,
                text_color=colors["text_color"],
                percent_color=colors["percent_color"],
            )
        }

    return _render("languages.svg", theme, base, theme_callback)


async def render_streak(collector: StatsCollector, theme: str, formatter: StatsFormatter) -> str:
    """Render the streak SVG card.

    :param collector: Populated stats collector.
    :param theme: Theme name.
    :param formatter: Stats formatter instance.
    :returns: Rendered SVG string.
    :rtype: str
    """
    base = {
        "current_streak": str(await collector.get_current_streak()),
        "longest_streak": str(await collector.get_longest_streak()),
        "current_streak_range": await collector.get_current_streak_range(),
        "longest_streak_range": await collector.get_longest_streak_range(),
        "total_contributions": formatter.format_number(await collector.get_total_contributions()),
        "contribution_year": "All time",
    }

    return _render("streak.svg", theme, base)


async def render_languages_puzzle(collector: StatsCollector, theme: str, formatter: StatsFormatter) -> str:
    """Render the languages puzzle SVG card.

    :param collector: Populated stats collector.
    :param theme: Theme name.
    :param formatter: Stats formatter instance.
    :returns: Rendered SVG string.
    :rtype: str
    """
    languages = await collector.get_languages()

    base: Dict[str, Any] = {}

    def theme_callback(colors: Dict[str, Any]) -> Dict[str, Any]:
        hue = int(colors["puzzle_hue"])
        sat = colors["puzzle_saturation_range"]
        light = colors["puzzle_lightness_range"]
        hue_spread = int(colors["puzzle_hue_spread"])
        puzzle_text_color = colors["puzzle_text_color"]

        return {
            "puzzle_blocks": formatter.format_puzzle_blocks(
                languages,
                width=455,
                height=135,
                hue=hue,
                saturation_range=list(sat),
                lightness_range=list(light),
                hue_spread=hue_spread,
            ),
            "puzzle_text_color": puzzle_text_color,
        }

    return _render("languages_puzzle.svg", theme, base, theme_callback)


async def render_streak_battery(collector: StatsCollector, theme: str, formatter: StatsFormatter) -> str:
    """Render the streak battery SVG card.

    :param collector: Populated stats collector.
    :param theme: Theme name.
    :param formatter: Stats formatter instance.
    :returns: Rendered SVG string.
    :rtype: str
    """
    current_streak = await collector.get_current_streak()
    longest_streak = await collector.get_longest_streak()
    recent_contributions = await collector.get_recent_contributions()

    battery_max_height = 87
    battery_y_offset = 4
    bar_width = 14
    bar_gap = 4
    bar_max_height = 100
    bar_min_height = 4

    if longest_streak > 0:
        streak_percentage = min(100, int((current_streak / longest_streak) * 100))
    else:
        streak_percentage = 0 if current_streak == 0 else 100

    battery_fill_height = int((streak_percentage / 100) * battery_max_height)
    battery_fill_y = battery_y_offset + (battery_max_height - battery_fill_height)
    is_record = current_streak > 0 and current_streak >= longest_streak

    base = {
        "current_streak": str(current_streak),
        "longest_streak": str(longest_streak),
        "current_streak_range": await collector.get_current_streak_range(),
        "longest_streak_range": await collector.get_longest_streak_range(),
        "streak_percentage": str(streak_percentage),
        "battery_fill_height": str(battery_fill_height),
        "battery_fill_y": str(battery_fill_y),
        "is_record_class": "animate-glow" if is_record else "",
        "record_icon_class": "animate-pulse" if is_record else "",
        "battery_gradient_id": "glow-gradient" if is_record else "battery-gradient",
        "shimmer_display": "block" if streak_percentage > 10 else "none",
    }

    def _generate_bars(contributions: list, bar_color: str, text_color: str) -> str:
        if not contributions:
            return ""
        max_c = max(contributions) if max(contributions) > 0 else 1
        bars = []
        for i, count in enumerate(contributions):
            bh = max(bar_min_height, int((count / max_c) * bar_max_height)) if count > 0 else bar_min_height
            x = i * (bar_width + bar_gap)
            y = bar_max_height - bh
            dc = f"delay-{i + 1}"
            bars.append(
                f'<g class="animate-fill {dc}" style="transform-origin: {x + bar_width // 2}px bottom;">'
                f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bh}" rx="2" fill="{bar_color}"/>'
                f'</g>'
            )
            if count > 0:
                ty = y - 5
                bars.append(
                    f'<text x="{x + bar_width // 2}" y="{ty}" font-family="\'Segoe UI\', Ubuntu, Sans-Serif" '
                    f'font-size="9" fill="{text_color}" text-anchor="middle" class="animate-fade {dc}">{count}</text>'
                )
        return "\n  ".join(bars)

    def theme_callback(colors: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "contribution_bars": _generate_bars(
                recent_contributions,
                colors["accent_color"],
                colors["text_color"],
            ),
        }

    return _render("streak_battery.svg", theme, base, theme_callback)


async def render_commit_calendar(collector: StatsCollector, theme: str, formatter: StatsFormatter) -> str:
    """Render the commit calendar SVG card.

    :param collector: Populated stats collector.
    :param theme: Theme name.
    :param formatter: Stats formatter instance.
    :returns: Rendered SVG string.
    :rtype: str
    """
    from src.generators.commit_calendar import CommitCalendarGenerator

    commits = await collector.get_weekly_commit_schedule()
    gen = CommitCalendarGenerator.__new__(CommitCalendarGenerator)

    visible_repos = gen._ordered_repositories(commits)
    svg_height = gen._compute_svg_height(len(visible_repos))
    footer_y = svg_height - CommitCalendarGenerator._FOOTER_HEIGHT

    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    timezone_name = "UTC"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")

    now_local = datetime.now(tz)
    week_start = now_local.date() - timedelta(days=now_local.weekday())
    week_end = week_start + timedelta(days=6)

    base = {
        "timezone_label": timezone_name,
        "week_range": f"{week_start.isoformat()} to {week_end.isoformat()}",
        "day_labels": gen._build_day_labels(),
        "hour_labels": gen._build_hour_labels(),
        "grid_lines": gen._build_grid_lines(),
        "svg_width": CommitCalendarGenerator._SVG_WIDTH,
        "svg_height": svg_height,
        "viewbox_width": CommitCalendarGenerator._SVG_WIDTH,
        "viewbox_height": svg_height,
        "clip_height": svg_height,
        "footer_y": footer_y,
    }

    def theme_callback(colors: Dict[str, Any]) -> Dict[str, Any]:
        palette = generate_palette_colors(
            count=max(len(visible_repos), 1),
            hue=int(colors["calendar_hue"]),
            saturation_range=gen._parse_range(colors["calendar_saturation_range"]),
            lightness_range=gen._parse_range(colors["calendar_lightness_range"]),
            hue_spread=int(colors["calendar_hue_spread"]),
        )
        color_map = gen._build_repo_color_map(visible_repos, palette)
        return {
            "calendar_title_color": colors["calendar_title_color"],
            "calendar_subtitle_color": colors["calendar_subtitle_color"],
            "calendar_day_label_color": colors["calendar_day_label_color"],
            "calendar_hour_label_color": colors["calendar_hour_label_color"],
            "calendar_grid_color": colors["calendar_grid_color"],
            "calendar_grid_opacity": colors["calendar_grid_opacity"],
            "calendar_legend_text_color": colors["calendar_legend_text_color"],
            "calendar_slot_opacity": colors["calendar_slot_opacity"],
            "commit_blocks": gen._build_commit_blocks(commits, color_map, tz),
            "legend_items": gen._build_legend_items(visible_repos, color_map),
        }

    return _render("commit_calendar.svg", theme, base, theme_callback)


async def render_stats_history(collector: StatsCollector, theme: str, formatter: StatsFormatter) -> str:
    """Render the stats history line chart SVG card.

    :param collector: Populated stats collector.
    :param theme: Theme name.
    :param formatter: Stats formatter instance.
    :returns: Rendered SVG string.
    :rtype: str
    """
    from src.generators.stats_history import StatsHistoryGenerator

    history = await collector.get_stats_history()
    if not history:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="100"><text x="24" y="50" font-size="14">No history data available</text></svg>'

    name = await collector.get_name()
    gen = StatsHistoryGenerator.__new__(StatsHistoryGenerator)

    visible_series = gen._filter_active_series(history)
    if not visible_series:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="100"><text x="24" y="50" font-size="14">No history data available</text></svg>'

    y_max = gen._compute_y_max(history, visible_series)
    y_ticks = gen._compute_y_ticks(y_max)
    dates = [entry.get("date", "") for entry in history]

    svg_height = gen._compute_svg_height(len(visible_series))
    footer_y = svg_height - StatsHistoryGenerator._FOOTER_HEIGHT

    chart_title = gen._escape_xml(f"{name} Stats History")
    date_range = f"{dates[0]} to {dates[-1]}" if len(dates) > 1 else dates[0]

    base = {
        "chart_title": chart_title,
        "chart_subtitle": f"Period: {date_range}",
        "svg_width": StatsHistoryGenerator._SVG_WIDTH,
        "svg_height": svg_height,
        "viewbox_width": StatsHistoryGenerator._SVG_WIDTH,
        "viewbox_height": svg_height,
        "clip_height": svg_height,
        "footer_y": footer_y,
    }

    def theme_callback(colors: Dict[str, Any]) -> Dict[str, Any]:
        palette = generate_palette_colors(
            count=max(len(visible_series), 1),
            hue=int(colors["line_chart_hue"]),
            saturation_range=gen._parse_range(
                colors["line_chart_saturation_range"]
            ),
            lightness_range=gen._parse_range(
                colors["line_chart_lightness_range"]
            ),
            hue_spread=int(colors["line_chart_hue_spread"]),
        )
        color_map = {
            series: palette[idx % len(palette)]
            for idx, series in enumerate(visible_series)
        }
        return {
            "y_axis_labels": gen._build_y_axis_labels(y_ticks),
            "x_axis_labels": gen._build_x_axis_labels(dates),
            "grid_lines": gen._build_grid_lines(y_ticks),
            "chart_lines": gen._build_chart_lines(
                history, visible_series, color_map, y_max
            ),
            "legend_items": gen._build_legend_items(visible_series, color_map),
        }

    return _render("stats_history.svg", theme, base, theme_callback)


CARD_RENDERERS = {
    "overview": render_overview,
    "languages": render_languages,
    "streak": render_streak,
    "languages-puzzle": render_languages_puzzle,
    "streak-battery": render_streak_battery,
    "commit-calendar": render_commit_calendar,
    "stats-history": render_stats_history,
}
