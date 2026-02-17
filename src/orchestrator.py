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
from src.db.snapshots import SnapshotStore
from src.core.config import Config
from src.core.credentials import GitHubCredentials
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate
import src.generators  # noqa: F401 – triggers @register_generator decorators
from src.generators import BaseGenerator, GeneratorRegistry

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

    def _create_generators(self) -> list[BaseGenerator]:
        """
        Creates generator instances from the registry.

        :return: List of instantiated generators.
        """
        common = (
            self.config,
            self._stats,
            self.formatter,
            self.template_engine,
            self.environment,
        )
        return [cls(*common) for cls in GeneratorRegistry.get_all()]

    async def run(self) -> None:
        """
        Execute the full image generation pipeline.

        Fetches statistics from GitHub and generates all configured SVG images.
        """
        async with ClientSession() as session:
            snapshot_store = SnapshotStore()
            self._stats = StatsCollector(
                environment_vars=self.environment,
                session=session,
                snapshot_store=snapshot_store,
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

            generators = self._create_generators()
            await gather(*[g.generate() for g in generators])

    @classmethod
    async def create_and_run(
        cls,
        config: Config = None,
        environment: Environment = None,
    ) -> "ImageOrchestrator":
        """
        Factory method to create and run the orchestrator.

        :param config: Optional configuration instance. Defaults to ``Config()``.
        :param environment: Optional environment instance. Defaults to one
                            built from ``GitHubCredentials``.
        :return: Configured ImageOrchestrator instance after execution.
        """
        if config is None:
            config = Config()
        if environment is None:
            access_token = GitHubCredentials.get_github_token()
            user = GitHubCredentials.get_github_actor()
            environment = Environment(username=user, access_token=access_token)

        orchestrator = cls(config, environment)
        await orchestrator.run()
        return orchestrator
