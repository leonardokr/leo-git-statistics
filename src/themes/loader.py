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
    "gradient_end": "#58a6ff"
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
    normalized_colors = {key: colors.get(key, default) for key, default in DEFAULT_COLORS.items()}

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
