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

    env = Environment()
    env.username = username

    session = ClientSession()
    collector = StatsCollector(env, session)

    try:
        base_dir = Path(output_dir)
        api_dir = base_dir / "users" / username
        api_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Fetching statistics...")

        name = await collector.get_name()
        total_contributions = await collector.get_total_contributions()
        repos = await collector.get_repos()
        stars = await collector.get_stargazers()
        forks = await collector.get_forks()
        views = await collector.get_views()
        views_from = await collector.get_views_from_date()
        clones = await collector.get_clones()
        clones_from = await collector.get_clones_from_date()
        pull_requests = await collector.get_pull_requests()
        issues = await collector.get_issues()
        lines_added, lines_deleted = await collector.get_lines_changed()
        avg_percent = await collector.get_avg_contribution_percent()
        collaborators = await collector.get_collaborators()
        contributors = await collector.get_contributors()
        languages = await collector.get_languages()
        languages_prop = await collector.get_languages_proportional()
        current_streak = await collector.get_current_streak()
        current_range = await collector.get_current_streak_range()
        longest_streak = await collector.get_longest_streak()
        longest_range = await collector.get_longest_streak_range()
        recent = await collector.get_recent_contributions()
        weekly = await collector.get_weekly_commit_schedule()

        overview_data = {
            "username": username,
            "name": name,
            "total_contributions": total_contributions,
            "repositories_count": len(repos),
            "total_stars": stars,
            "total_forks": forks,
            "total_views": views,
            "views_from_date": views_from,
            "total_clones": clones,
            "clones_from_date": clones_from,
            "total_pull_requests": pull_requests,
            "total_issues": issues,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "avg_contribution_percent": avg_percent,
            "collaborators_count": collaborators,
            "contributors_count": len(contributors),
        }

        with open(api_dir / "overview.json", "w") as f:
            json.dump(overview_data, f, indent=2)
        logger.info("Generated overview.json")

        languages_data = {
            "username": username,
            "languages": languages,
        }

        with open(api_dir / "languages.json", "w") as f:
            json.dump(languages_data, f, indent=2)
        logger.info("Generated languages.json")

        languages_prop_data = {
            "username": username,
            "languages": languages_prop,
        }

        with open(api_dir / "languages-proportional.json", "w") as f:
            json.dump(languages_prop_data, f, indent=2)
        logger.info("Generated languages-proportional.json")

        streak_data = {
            "username": username,
            "current_streak": current_streak,
            "current_streak_range": current_range,
            "longest_streak": longest_streak,
            "longest_streak_range": longest_range,
            "total_contributions": total_contributions,
        }

        with open(api_dir / "streak.json", "w") as f:
            json.dump(streak_data, f, indent=2)
        logger.info("Generated streak.json")

        recent_data = {
            "username": username,
            "recent_contributions": recent,
        }

        with open(api_dir / "contributions-recent.json", "w") as f:
            json.dump(recent_data, f, indent=2)
        logger.info("Generated contributions-recent.json")

        weekly_data = {
            "username": username,
            "weekly_commits": weekly,
        }

        with open(api_dir / "commits-weekly.json", "w") as f:
            json.dump(weekly_data, f, indent=2)
        logger.info("Generated commits-weekly.json")

        repos_data = {
            "username": username,
            "repositories_count": len(repos),
            "repositories": sorted(list(repos)),
        }

        with open(api_dir / "repositories.json", "w") as f:
            json.dump(repos_data, f, indent=2)
        logger.info("Generated repositories.json")

        full_data = {
            "username": username,
            "overview": {
                "name": name,
                "total_contributions": total_contributions,
                "repositories_count": len(repos),
                "total_stars": stars,
                "total_forks": forks,
                "total_views": views,
                "views_from_date": views_from,
                "total_clones": clones,
                "clones_from_date": clones_from,
                "total_pull_requests": pull_requests,
                "total_issues": issues,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "avg_contribution_percent": avg_percent,
                "collaborators_count": collaborators,
                "contributors_count": len(contributors),
            },
            "languages": languages,
            "streak": {
                "current_streak": current_streak,
                "current_streak_range": current_range,
                "longest_streak": longest_streak,
                "longest_streak_range": longest_range,
            },
            "contributions": {
                "total": total_contributions,
                "recent": recent,
            },
            "repositories": {
                "count": len(repos),
                "list": sorted(list(repos)),
            },
            "weekly_commits": weekly,
        }

        with open(api_dir / "stats-full.json", "w") as f:
            json.dump(full_data, f, indent=2)
        logger.info("Generated stats-full.json")

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
