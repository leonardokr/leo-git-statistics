#!/usr/bin/env python3
"""
Test SVG Generation Script.

This script generates SVG images using mock data for testing purposes.
Does not require a connection to the GitHub API.

Set OUTPUT_SUFFIX to add a suffix to output filenames (e.g., "_sample" for README images).
"""

import asyncio
import logging
import os
import yaml

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


def _load_runtime_options(config_path: str = "config.yml") -> dict:
    with open(config_path, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    if not isinstance(config, dict):
        raise ValueError("config.yml must contain a YAML object at root")

    stats = config["stats_generation"]

    return {
        "timezone": config["timezone"],
        "show_total_contributions": stats["show_total_contributions"],
        "show_repositories": stats["show_repositories"],
        "show_lines_changed": stats["show_lines_changed"],
        "show_avg_percent": stats["show_avg_percent"],
        "show_collaborators": stats["show_collaborators"],
        "show_contributors": stats["show_contributors"],
        "show_views": stats["show_views"],
        "show_clones": stats["show_clones"],
        "show_forks": stats["show_forks"],
        "show_stars": stats["show_stars"],
        "show_pull_requests": stats["show_pull_requests"],
        "show_issues": stats["show_issues"],
        "mask_private_repos": stats["mask_private_repos"],
    }


async def main():
    """Generate test SVG images with mock data."""
    config = Config()
    formatter = StatsFormatter()
    template_engine = SVGTemplate(config.TEMPLATE_PATH, config.OUTPUT_DIR)
    runtime_options = _load_runtime_options()
    os.environ["MASK_PRIVATE_REPOS"] = str(runtime_options["mask_private_repos"])
    environment = MockEnvironment(**runtime_options)
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
