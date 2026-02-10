from asyncio import run, gather
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


class ImageOrchestrator:
    """
    Orchestrates the generation of GitHub statistics images.

    This class coordinates the process of fetching statistics from GitHub,
    formatting them, and rendering them into SVG templates using specialized generators.
    """

    def __init__(self):
        self.config = Config()
        self.formatter = StatsFormatter()
        self.template_engine = SVGTemplate(self.config.TEMPLATE_PATH, self.config.OUTPUT_DIR)

        access_token = self.config.get_github_token()
        user = self.config.get_github_actor()

        self.__environment = Environment(username=user, access_token=access_token)
        self.__stats = None

        run(self.start())

    async def start(self) -> None:
        async with ClientSession() as session:
            self.__stats = StatsCollector(
                environment_vars=self.__environment,
                session=session
            )

            await self.__stats.get_stats()
            await self.__stats._get_contribution_calendar()

            print(f"Stats collected: {len(await self.__stats.repos)} repos, {len(await self.__stats.languages)} languages")

            generators = [
                OverviewGenerator(
                    self.config,
                    self.__stats,
                    self.formatter,
                    self.template_engine,
                    self.__environment
                ),
                LanguagesGenerator(
                    self.config,
                    self.__stats,
                    self.formatter,
                    self.template_engine
                ),
                LanguagesPuzzleGenerator(
                    self.config,
                    self.__stats,
                    self.formatter,
                    self.template_engine
                ),
                StreakGenerator(
                    self.config,
                    self.__stats,
                    self.formatter,
                    self.template_engine
                ),
                StreakBatteryGenerator(
                    self.config,
                    self.__stats,
                    self.formatter,
                    self.template_engine
                ),
            ]

            await gather(*[g.generate() for g in generators])
