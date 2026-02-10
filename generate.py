#!/usr/bin/python3
"""
Generate GitHub Statistics Images.

This script generates SVG images visualizing GitHub repository statistics
by fetching data from the GitHub API and rendering configured templates.
"""

import asyncio
import logging

from src.orchestrator import ImageOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():
    """Entry point for the statistics generation script."""
    asyncio.run(ImageOrchestrator.create_and_run())


if __name__ == "__main__":
    main()
