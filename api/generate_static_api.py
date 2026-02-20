#!/usr/bin/env python3
"""
Generate static API JSON files for GitHub Pages deployment.

This script fetches all statistics and saves them as static JSON files
that can be deployed to GitHub Pages and consumed by static portfolios.

Usage:
    export GITHUB_TOKEN=your_token
    export GITHUB_ACTOR=your_username
    python api/generate_static_api.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import json
import logging
import os

from aiohttp import ClientSession

from src.core.environment import Environment
from src.core.stats_collector import StatsCollector
from src.core.stats_assembler import build_overview_payload, build_full_payload, build_snapshot_payload
from src.db.snapshots import snapshot_store
from src.utils.privacy import mask_repo_names, should_mask_private

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def generate_static_api(username: str, output_dir: str = "api-data"):
    """
    Generate static JSON files for all API endpoints.

    :param username: GitHub username
    :param output_dir: Output directory for JSON files
    """
    logger.info(f"Generating static API for user: {username}")

    token = os.getenv("GITHUB_TOKEN") or os.getenv("ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN or ACCESS_TOKEN environment variable not set")

    env = Environment(username=username, access_token=token)

    session = ClientSession()
    collector = StatsCollector(env, session)

    try:
        base_dir = Path(output_dir)
        api_dir = base_dir / "users" / username
        api_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Fetching statistics...")

        overview_data = await build_overview_payload(collector, username)

        with open(api_dir / "overview.json", "w", encoding="utf-8") as f:
            json.dump(overview_data, f, indent=2)
        logger.info("Generated overview.json")

        languages = await collector.get_languages()
        languages_prop = await collector.get_languages_proportional()

        languages_data = {
            "username": username,
            "languages": languages,
        }

        with open(api_dir / "languages.json", "w", encoding="utf-8") as f:
            json.dump(languages_data, f, indent=2)
        logger.info("Generated languages.json")

        languages_prop_data = {
            "username": username,
            "languages": languages_prop,
        }

        with open(api_dir / "languages-proportional.json", "w", encoding="utf-8") as f:
            json.dump(languages_prop_data, f, indent=2)
        logger.info("Generated languages-proportional.json")

        current_streak = await collector.get_current_streak()
        current_range = await collector.get_current_streak_range()
        longest_streak = await collector.get_longest_streak()
        longest_range = await collector.get_longest_streak_range()
        total_contributions = overview_data["total_contributions"]

        streak_data = {
            "username": username,
            "current_streak": current_streak,
            "current_streak_range": current_range,
            "longest_streak": longest_streak,
            "longest_streak_range": longest_range,
            "total_contributions": total_contributions,
        }

        with open(api_dir / "streak.json", "w", encoding="utf-8") as f:
            json.dump(streak_data, f, indent=2)
        logger.info("Generated streak.json")

        recent = await collector.get_recent_contributions()

        recent_data = {
            "username": username,
            "recent_contributions": recent,
        }

        with open(api_dir / "contributions-recent.json", "w", encoding="utf-8") as f:
            json.dump(recent_data, f, indent=2)
        logger.info("Generated contributions-recent.json")

        weekly = await collector.get_weekly_commit_schedule()

        weekly_data = {
            "username": username,
            "weekly_commits": weekly,
        }

        with open(api_dir / "commits-weekly.json", "w", encoding="utf-8") as f:
            json.dump(weekly_data, f, indent=2)
        logger.info("Generated commits-weekly.json")

        repos = await collector.get_repos()
        visibility = await collector.get_repo_visibility()
        mask_enabled = should_mask_private(env.filter.mask_private_repos)
        repo_names = sorted(
            mask_repo_names(
                repos,
                visibility,
                username,
                mask_enabled=mask_enabled,
            )
        )

        repos_data = {
            "username": username,
            "repositories_count": len(repos),
            "repositories": repo_names,
        }

        with open(api_dir / "repositories.json", "w", encoding="utf-8") as f:
            json.dump(repos_data, f, indent=2)
        logger.info("Generated repositories.json")

        full_data = await build_full_payload(collector, username)

        with open(api_dir / "stats-full.json", "w", encoding="utf-8") as f:
            json.dump(full_data, f, indent=2)
        logger.info("Generated stats-full.json")

        snapshot_data = await build_snapshot_payload(collector)
        snapshot_store.save_snapshot(username, snapshot_data)
        logger.info("Saved statistics snapshot")

        history_data = {
            "username": username,
            "snapshots": snapshot_store.get_snapshots(username, limit=1000),
        }
        with open(api_dir / "history.json", "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2)
        logger.info("Generated history.json")

        logger.info(f"All static API files generated in: {api_dir}")
        logger.info(f"You can now deploy the '{output_dir}' directory to GitHub Pages")
        logger.info(f"Access via: https://username.github.io/repo/{api_dir.relative_to(base_dir)}/overview.json")

    finally:
        await session.close()


def main():
    """Main entry point."""
    username = os.getenv("GITHUB_ACTOR")
    if not username:
        raise ValueError("GITHUB_ACTOR environment variable not set")

    asyncio.run(generate_static_api(username))


if __name__ == "__main__":
    main()
