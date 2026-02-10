import os
import yaml
from typing import Dict, Any, Optional, List
from src.themes import load_all_themes


class Config:
    """
    Centralized configuration settings for the application.
    Supports extensible themes loaded from YAML files in src/themes/.
    """

    OUTPUT_DIR = "generated_images"
    TEMPLATE_PATH = "src/templates/"

    OVERVIEW_TEMPLATE = "overview.svg"
    LANGUAGES_TEMPLATE = "languages.svg"
    LANGUAGES_PUZZLE_TEMPLATE = "languages_puzzle.svg"
    STREAK_TEMPLATE = "streak.svg"
    STREAK_BATTERY_TEMPLATE = "streak_battery.svg"

    def __init__(self, config_path: str = "config.yml"):
        """
        Initializes the configuration by loading themes and reading config.yml.

        :param config_path: Path to the configuration file.
        """
        self._all_themes = load_all_themes()
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

    @staticmethod
    def get_github_token() -> str:
        """
        Retrieves the GitHub personal access token from environment variables.

        :return: The access token.
        :raises Exception: If the token is not set.
        """
        token = os.getenv("ACCESS_TOKEN")
        if not token:
            raise Exception("A personal access token is required to proceed!")
        return token

    @staticmethod
    def get_github_actor() -> str:
        """
        Retrieves the GitHub actor (username) from environment variables.

        :return: The GitHub username.
        :raises RuntimeError: If GITHUB_ACTOR is not set.
        """
        actor = os.getenv("GITHUB_ACTOR")
        if not actor:
            raise RuntimeError("Environment variable GITHUB_ACTOR must be set")
        return actor
