"""Theme loader module - handles loading themes from YAML files."""

import os
import yaml
from typing import Dict, Any, Optional, List

THEMES_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_COLORS = {
    "bg_color": "#FFFFFF",
    "title_color": "#0969da",
    "text_color": "#24292f",
    "icon_color": "#57606a",
    "percent_color": "#57606a",
    "border_color": "#d0d7de",
    "accent_color": "#0969da",
    "gradient_start": "#0969da",
    "gradient_end": "#58a6ff",
    "puzzle_hue": 210,
    "puzzle_saturation_range": [60, 85],
    "puzzle_lightness_range": [35, 65],
    "puzzle_text_color": "#FFFFFF",
    "calendar_title_color": "#0969da",
    "calendar_subtitle_color": "#57606a",
    "calendar_day_label_color": "#24292f",
    "calendar_hour_label_color": "#57606a",
    "calendar_grid_color": "#d0d7de",
    "calendar_grid_opacity": 0.55,
    "calendar_legend_text_color": "#24292f",
    "calendar_slot_opacity": 0.95,
    "calendar_hue": 210,
    "calendar_saturation_range": [60, 85],
    "calendar_lightness_range": [40, 60],
    "calendar_hue_spread": 90,
}


def _load_theme_file(filepath: str) -> Dict[str, Dict[str, Any]]:
    """Load themes from a single YAML file."""
    themes = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            for theme_name, theme_data in data.items():
                if isinstance(theme_data, dict):
                    themes[theme_name] = _normalize_theme(theme_name, theme_data)
    except Exception:
        pass
    return themes


def _normalize_theme(name: str, theme_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure a theme has all required color properties with defaults."""
    colors = theme_data.get("colors", {})
    normalized_colors = {}

    for key, default in DEFAULT_COLORS.items():
        if key in colors:
            normalized_colors[key] = colors[key]
        else:
            normalized_colors[key] = default

    if "calendar_title_color" not in colors:
        normalized_colors["calendar_title_color"] = normalized_colors["title_color"]
    if "calendar_subtitle_color" not in colors:
        normalized_colors["calendar_subtitle_color"] = normalized_colors["percent_color"]
    if "calendar_day_label_color" not in colors:
        normalized_colors["calendar_day_label_color"] = normalized_colors["text_color"]
    if "calendar_hour_label_color" not in colors:
        normalized_colors["calendar_hour_label_color"] = normalized_colors["percent_color"]
    if "calendar_grid_color" not in colors:
        normalized_colors["calendar_grid_color"] = normalized_colors["border_color"]
    if "calendar_legend_text_color" not in colors:
        normalized_colors["calendar_legend_text_color"] = normalized_colors["text_color"]
    if "calendar_hue" not in colors:
        normalized_colors["calendar_hue"] = normalized_colors["puzzle_hue"]
    if "calendar_saturation_range" not in colors:
        normalized_colors["calendar_saturation_range"] = normalized_colors["puzzle_saturation_range"]
    if "calendar_lightness_range" not in colors:
        normalized_colors["calendar_lightness_range"] = normalized_colors["puzzle_lightness_range"]
    if "calendar_hue_spread" not in colors:
        normalized_colors["calendar_hue_spread"] = normalized_colors.get("puzzle_hue_spread", 90)

    suffix = theme_data.get("suffix")
    if suffix is None:
        suffix = name.title().replace("_", "")
        if name == "default":
            suffix = ""

    return {
        "suffix": suffix,
        "colors": normalized_colors
    }


def load_all_themes() -> Dict[str, Dict[str, Any]]:
    """Load all themes from YAML files in the themes directory."""
    all_themes = {}

    for filename in sorted(os.listdir(THEMES_DIR)):
        if filename.endswith(('.yml', '.yaml')):
            filepath = os.path.join(THEMES_DIR, filename)
            file_themes = _load_theme_file(filepath)
            all_themes.update(file_themes)

    return all_themes


def get_theme(theme_name: str) -> Optional[Dict[str, Any]]:
    """Get a specific theme by name."""
    all_themes = load_all_themes()
    return all_themes.get(theme_name)


def list_themes() -> List[str]:
    """List all available theme names."""
    return list(load_all_themes().keys())
