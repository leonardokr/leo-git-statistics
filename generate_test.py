#!/usr/bin/env python3
"""
Test SVG Generation Script.

This script generates SVG images using mock data for testing purposes.
Does not require a connection to the GitHub API.

Set OUTPUT_SUFFIX to add a suffix to output filenames (e.g., "_sample" for README images).
"""

import asyncio
import logging

from src.core.config import Config
from src.core.mock_stats import MockStatsCollector, MockEnvironment
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate
from src.generators.languages import LanguagesGenerator
from src.generators.languages_puzzle import LanguagesPuzzleGenerator
from src.generators.overview import OverviewGenerator
from src.generators.streak import StreakGenerator
from src.generators.streak_battery import StreakBatteryGenerator
from src.generators.commit_calendar import CommitCalendarGenerator
from src.generators.stats_history import StatsHistoryGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_SUFFIX = ""


async def main():
    """Generate test SVG images with mock data."""
    config = Config()
    formatter = StatsFormatter()
    template_engine = SVGTemplate(config.TEMPLATE_PATH, config.OUTPUT_DIR)
    environment = MockEnvironment()
    mock_stats = MockStatsCollector()

    languages_gen = LanguagesGenerator(config, mock_stats, formatter, template_engine)
    await languages_gen.generate()
    logger.info("Generated languages SVGs")

    languages_puzzle_gen = LanguagesPuzzleGenerator(
        config, mock_stats, formatter, template_engine
    )
    await languages_puzzle_gen.generate()
    logger.info("Generated languages_puzzle SVGs")

    overview_gen = OverviewGenerator(
        config, mock_stats, formatter, template_engine, environment
    )
    await overview_gen.generate()
    logger.info("Generated overview SVGs")

    streak_gen = StreakGenerator(config, mock_stats, formatter, template_engine)
    await streak_gen.generate()
    logger.info("Generated streak SVGs")

    streak_battery_gen = StreakBatteryGenerator(
        config, mock_stats, formatter, template_engine
    )
    await streak_battery_gen.generate()
    logger.info("Generated streak_battery SVGs")

    commit_calendar_gen = CommitCalendarGenerator(
        config, mock_stats, formatter, template_engine, environment
    )
    await commit_calendar_gen.generate()
    logger.info("Generated commit_calendar SVGs")

    stats_history_gen = StatsHistoryGenerator(
        config, mock_stats, formatter, template_engine, environment
    )
    await stats_history_gen.generate()
    logger.info("Generated stats_history SVGs")

    suffix_msg = f" with suffix: {OUTPUT_SUFFIX}" if OUTPUT_SUFFIX else ""
    logger.info("All test images generated in 'generated_images/' folder%s.", suffix_msg)


if __name__ == "__main__":
    asyncio.run(main())
