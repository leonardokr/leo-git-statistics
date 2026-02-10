#!/usr/bin/env python3
"""
Script to test SVG generation with mock data.
Does not require a connection to the GitHub API.
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


async def main():
    config = Config()
    formatter = StatsFormatter()
    template_engine = SVGTemplate(config.TEMPLATE_PATH, config.OUTPUT_DIR)
    environment = MockEnvironment()
    mock_stats = MockStatsCollector()

    languages_gen = LanguagesGenerator(config, mock_stats, formatter, template_engine)
    await languages_gen.generate()
    print("Generated languages SVGs")

    languages_puzzle_gen = LanguagesPuzzleGenerator(config, mock_stats, formatter, template_engine)
    await languages_puzzle_gen.generate()
    print("Generated languages_puzzle SVGs")

    overview_gen = OverviewGenerator(config, mock_stats, formatter, template_engine, environment)
    await overview_gen.generate()
    print("Generated overview SVGs")

    streak_gen = StreakGenerator(config, mock_stats, formatter, template_engine)
    await streak_gen.generate()
    print("Generated streak SVGs")

    streak_battery_gen = StreakBatteryGenerator(config, mock_stats, formatter, template_engine)
    await streak_battery_gen.generate()
    print("Generated streak_battery SVGs")

    record_stats = MockStatsCollector({
        "current_streak": 50,
        "longest_streak": 42,
        "current_streak_range": "Jan 1 - Feb 19, 2026",
        "longest_streak_range": "Mar 1 - Apr 12, 2024",
        "recent_contributions": [5, 8, 12, 15, 10, 18, 14, 20, 16, 22],
    })
    streak_battery_record_gen = StreakBatteryGenerator(config, record_stats, formatter, template_engine)
    await streak_battery_record_gen.generate(output_name="streak_battery_record")
    print("Generated streak_battery_record SVGs (with glow effect)")

    print("\nAll test images generated in 'generated_images/' folder.")


if __name__ == "__main__":
    asyncio.run(main())
