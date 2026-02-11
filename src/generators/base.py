from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Optional, Type

from src.core.config import Config
from src.core.stats_collector import StatsCollector
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate


class GeneratorRegistry:
    """
    Registry that tracks all available generator classes.

    Generator classes register themselves via the :func:`register_generator`
    decorator and the orchestrator retrieves them with :meth:`get_all`.
    """

    _generators: List[Type["BaseGenerator"]] = []

    @classmethod
    def register(cls, generator_cls: Type["BaseGenerator"]) -> Type["BaseGenerator"]:
        """
        Register a generator class.

        :param generator_cls: The generator class to register.
        :return: The same class, unchanged.
        """
        cls._generators.append(generator_cls)
        return generator_cls

    @classmethod
    def get_all(cls) -> List[Type["BaseGenerator"]]:
        """
        Return all registered generator classes.

        :return: List of registered generator classes.
        """
        return list(cls._generators)


def register_generator(cls: Type["BaseGenerator"]) -> Type["BaseGenerator"]:
    """
    Class decorator that registers a generator in the :class:`GeneratorRegistry`.

    :param cls: The generator class to register.
    :return: The same class, unchanged.
    """
    return GeneratorRegistry.register(cls)


class BaseGenerator(ABC):
    """
    Abstract base class for all SVG template generators.
    """

    OUTPUT_NAME: str = ""
    TEMPLATE_NAME: str = ""

    def __init__(
        self,
        config: Config,
        stats: StatsCollector,
        formatter: StatsFormatter,
        template_engine: SVGTemplate,
        environment=None,
    ):
        self.config = config
        self.stats = stats
        self.formatter = formatter
        self.template_engine = template_engine
        self.environment = environment

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
