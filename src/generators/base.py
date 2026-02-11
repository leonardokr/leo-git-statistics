from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional

from src.core.config import Config
from src.core.stats_collector import StatsCollector
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate


class BaseGenerator(ABC):
    """
    Abstract base class for all SVG template generators.
    """

    def __init__(
        self,
        config: Config,
        stats: StatsCollector,
        formatter: StatsFormatter,
        template_engine: SVGTemplate
    ):
        self.config = config
        self.stats = stats
        self.formatter = formatter
        self.template_engine = template_engine

    @abstractmethod
    async def generate(self) -> None:
        """
        Generates SVG files for all enabled themes.
        Must be implemented by subclasses.
        """
        pass

    def render_for_all_themes(
        self,
        template_name: str,
        output_name: str,
        base_replacements: Dict[str, Any],
        theme_callback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ) -> None:
        """
        Renders the template for all enabled themes.

        :param theme_callback: Optional function that receives theme colors and returns additional replacements.
        """
        for theme_name, theme_config in self.config.THEMES.items():
            colors = theme_config["colors"]
            replacements = base_replacements.copy()
            replacements.update(colors)

            if theme_callback:
                replacements.update(theme_callback(colors))

            self.template_engine.render_and_save(
                template_name,
                output_name,
                replacements,
                theme_config["suffix"]
            )
