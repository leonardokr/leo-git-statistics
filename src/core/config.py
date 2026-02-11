import yaml
from typing import Callable, Dict, Any, Optional, List
from src.themes import load_all_themes


class Config:
    """
    Centralized configuration settings for the application.
    Supports extensible themes loaded from YAML files in src/themes/.
    """

    OUTPUT_DIR = "generated_images"
    TEMPLATE_PATH = "src/templates/"

    def __init__(self, config_path: str = "config.yml",
                 theme_loader: Callable[[], Dict[str, Dict[str, Any]]] = None):
        """
        Initializes the configuration by loading themes and reading config.yml.

        :param config_path: Path to the configuration file.
        :param theme_loader: Callable that returns available themes. Defaults to
                             ``load_all_themes``.
        """
        self._all_themes = (theme_loader or load_all_themes)()
        self._enabled_themes: List[str] = []
        self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """
        Load theme selection from config.yml.

        :param config_path: Path to the configuration file.
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

            themes_config = config.get('themes', {})
            self._enabled_themes = themes_config.get('enabled', ['default', 'light', 'dark'])

        except FileNotFoundError:
            self._enabled_themes = ['default', 'light', 'dark']
        except Exception:
            self._enabled_themes = ['default', 'light', 'dark']

    @property
    def THEMES(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the active themes based on configuration.
        Filters all available themes by the enabled list in config.yml.

        :return: Dictionary of enabled themes.
        """
        if 'all' in self._enabled_themes:
            return self._all_themes

        return {
            name: theme
            for name, theme in self._all_themes.items()
            if name in self._enabled_themes
        }

    def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific theme by name.

        :param theme_name: Name of the theme to retrieve.
        :return: Theme configuration or None if not found.
        """
        return self._all_themes.get(theme_name)

    def list_available_themes(self) -> List[str]:
        """
        List all available theme names.

        :return: List of theme names.
        """
        return list(self._all_themes.keys())
