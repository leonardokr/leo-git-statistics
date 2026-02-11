from src.generators.base import BaseGenerator


class StreakGenerator(BaseGenerator):
    """
    Generates the streak SVG template with contribution streak statistics.
    """

    OUTPUT_NAME = "streak"
    TEMPLATE_NAME = "streak.svg"

    async def generate(self) -> None:
        base_replacements = {
            "current_streak": str(await self.stats.get_current_streak()),
            "longest_streak": str(await self.stats.get_longest_streak()),
            "current_streak_range": await self.stats.get_current_streak_range(),
            "longest_streak_range": await self.stats.get_longest_streak_range(),
            "total_contributions": self.formatter.format_number(await self.stats.get_total_contributions()),
            "contribution_year": "All time"
        }

        self.render_for_all_themes(
            self.TEMPLATE_NAME,
            self.OUTPUT_NAME,
            base_replacements
        )
