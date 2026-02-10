#!/usr/bin/env python3
"""
Script to test SVG generation with mock data.
Does not require a connection to the GitHub API.

Set OUTPUT_SUFFIX to add a suffix to output filenames (e.g., "_sample" for README images).
"""

import asyncio

from src.core.config import Config
from src.core.mock_stats import MockStatsCollector, MockEnvironment
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate
from src.generators.languages import LanguagesGenerator
from src.generators.languages_puzzle import LanguagesPuzzleGenerator
from src.generators.overview import OverviewGenerator
from src.generators.streak import StreakGenerator
from src.generators.streak_battery import StreakBatteryGenerator

OUTPUT_SUFFIX = ""


async def main():
    config = Config()
    formatter = StatsFormatter()
    template_engine = SVGTemplate(config.TEMPLATE_PATH, config.OUTPUT_DIR)
    environment = MockEnvironment()
    mock_stats = MockStatsCollector()

    languages_gen = LanguagesGenerator(config, mock_stats, formatter, template_engine)
    await languages_gen.generate(output_name=f"languages{OUTPUT_SUFFIX}")
    print("Generated languages SVGs")

    languages_puzzle_gen = LanguagesPuzzleGenerator(config, mock_stats, formatter, template_engine)
    await languages_puzzle_gen.generate(output_name=f"languages_puzzle{OUTPUT_SUFFIX}")
    print("Generated languages_puzzle SVGs")

    overview_gen = OverviewGenerator(config, mock_stats, formatter, template_engine, environment)
    await overview_gen.generate(output_name=f"overview{OUTPUT_SUFFIX}")
    print("Generated overview SVGs")

    streak_gen = StreakGenerator(config, mock_stats, formatter, template_engine)
    await streak_gen.generate(output_name=f"streak{OUTPUT_SUFFIX}")
    print("Generated streak SVGs")

    streak_battery_gen = StreakBatteryGenerator(config, mock_stats, formatter, template_engine)
    await streak_battery_gen.generate(output_name=f"streak_battery{OUTPUT_SUFFIX}")
    print("Generated streak_battery SVGs")

    print(f"\nAll test images generated in 'generated_images/' folder{' with suffix: ' + OUTPUT_SUFFIX if OUTPUT_SUFFIX else ''}.")


if __name__ == "__main__":
    asyncio.run(main())
