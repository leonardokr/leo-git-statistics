"""
Image Orchestrator Module.

This module coordinates the generation of GitHub statistics images by
managing the flow between data collection, formatting, and SVG rendering.
"""

import logging
from asyncio import gather
from aiohttp import ClientSession

from src.core.environment import Environment
from src.core.stats_collector import StatsCollector
from src.core.config import Config
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate
from src.generators import (
    OverviewGenerator,
    LanguagesGenerator,
    LanguagesPuzzleGenerator,
    StreakGenerator,
    StreakBatteryGenerator,
)

logger = logging.getLogger(__name__)


class ImageOrchestrator:
    """
    Orchestrate the generation of GitHub statistics images.

    This class coordinates the process of fetching statistics from GitHub,
    formatting them, and rendering them into SVG templates using specialized generators.

    :param config: Configuration instance.
    :param environment: Environment variables instance.
    """

    def __init__(self, config: Config, environment: Environment):
        self.config = config
        self.environment = environment
        self.formatter = StatsFormatter()
        self.template_engine = SVGTemplate(
            self.config.TEMPLATE_PATH, self.config.OUTPUT_DIR
        )
        self._stats = None

    async def run(self) -> None:
        """
        Execute the full image generation pipeline.

        Fetches statistics from GitHub and generates all configured SVG images.
        """
        async with ClientSession() as session:
            self._stats = StatsCollector(
                environment_vars=self.environment,
                session=session,
            )

            await self._stats.get_stats()
            await self._stats.get_contribution_calendar()

            repos = await self._stats.get_repos()
            languages = await self._stats.get_languages()
            recent = await self._stats.get_recent_contributions()

            logger.info(
                "Stats collected: %d repos, %d languages", len(repos), len(languages)
            )
            logger.info("Recent contributions: %s", recent)

            generators = [
                OverviewGenerator(
                    self.config,
                    self._stats,
                    self.formatter,
                    self.template_engine,
                    self.environment,
                ),
                LanguagesGenerator(
                    self.config,
                    self._stats,
                    self.formatter,
                    self.template_engine,
                ),
                LanguagesPuzzleGenerator(
                    self.config,
                    self._stats,
                    self.formatter,
                    self.template_engine,
                ),
                StreakGenerator(
                    self.config,
                    self._stats,
                    self.formatter,
                    self.template_engine,
                ),
                StreakBatteryGenerator(
                    self.config,
                    self._stats,
                    self.formatter,
                    self.template_engine,
                ),
            ]

            await gather(*[g.generate() for g in generators])

    @classmethod
    async def create_and_run(cls) -> "ImageOrchestrator":
        """
        Factory method to create and run the orchestrator.

        :return: Configured ImageOrchestrator instance after execution.
        """
        config = Config()
        access_token = config.get_github_token()
        user = config.get_github_actor()
        environment = Environment(username=user, access_token=access_token)

        orchestrator = cls(config, environment)
        await orchestrator.run()
        return orchestrator
