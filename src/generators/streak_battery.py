from src.generators.base import BaseGenerator


class StreakBatteryGenerator(BaseGenerator):
    """
    Generates the streak battery SVG template with a visual battery indicator.
    The battery fills based on current streak relative to longest streak,
    with a glow effect when hitting a new record.
    """

    BATTERY_MAX_HEIGHT = 87
    BATTERY_Y_OFFSET = 4
    BAR_WIDTH = 14
    BAR_GAP = 4
    BAR_MAX_HEIGHT = 100
    BAR_MIN_HEIGHT = 4

    OUTPUT_NAME = "streak_battery"
    TEMPLATE_NAME = "streak_battery.svg"

    async def generate(self) -> None:
        current_streak = await self.stats.get_current_streak()
        longest_streak = await self.stats.get_longest_streak()
        recent_contributions = await self.stats.get_recent_contributions()

        if longest_streak > 0:
            streak_percentage = min(100, int((current_streak / longest_streak) * 100))
        else:
            streak_percentage = 0 if current_streak == 0 else 100

        battery_fill_height = int((streak_percentage / 100) * self.BATTERY_MAX_HEIGHT)
        battery_fill_y = self.BATTERY_Y_OFFSET + (self.BATTERY_MAX_HEIGHT - battery_fill_height)

        is_record = current_streak > 0 and current_streak >= longest_streak

        base_replacements = {
            "current_streak": str(current_streak),
            "longest_streak": str(longest_streak),
            "current_streak_range": await self.stats.get_current_streak_range(),
            "longest_streak_range": await self.stats.get_longest_streak_range(),
            "streak_percentage": str(streak_percentage),
            "battery_fill_height": str(battery_fill_height),
            "battery_fill_y": str(battery_fill_y),
            "is_record_class": "animate-glow" if is_record else "",
            "record_icon_class": "animate-pulse" if is_record else "",
            "battery_gradient_id": "glow-gradient" if is_record else "battery-gradient",
            "shimmer_display": "block" if streak_percentage > 10 else "none",
        }

        def theme_callback(colors):
            return {
                "contribution_bars": self._generate_contribution_bars(
                    recent_contributions,
                    colors.get("accent_color", "#0969da"),
                    colors.get("text_color", "#24292f"),
                ),
            }

        self.render_for_all_themes(
            self.TEMPLATE_NAME,
            self.OUTPUT_NAME,
            base_replacements,
            theme_callback,
        )

    def _generate_contribution_bars(self, contributions: list, bar_color: str, text_color: str) -> str:
        if not contributions:
            return ""

        max_contrib = max(contributions) if max(contributions) > 0 else 1
        bars = []

        for i, count in enumerate(contributions):
            bar_height = max(self.BAR_MIN_HEIGHT, int((count / max_contrib) * self.BAR_MAX_HEIGHT)) if count > 0 else self.BAR_MIN_HEIGHT
            x = i * (self.BAR_WIDTH + self.BAR_GAP)
            y = self.BAR_MAX_HEIGHT - bar_height
            delay_class = f"delay-{i + 1}"

            bars.append(
                f'<g class="animate-fill {delay_class}" style="transform-origin: {x + self.BAR_WIDTH // 2}px bottom;">'
                f'<rect x="{x}" y="{y}" width="{self.BAR_WIDTH}" height="{bar_height}" rx="2" fill="{bar_color}"/>'
                f'</g>'
            )

            if count > 0:
                text_y = y - 5
                bars.append(
                    f'<text x="{x + self.BAR_WIDTH // 2}" y="{text_y}" font-family="\'Segoe UI\', Ubuntu, Sans-Serif" '
                    f'font-size="9" fill="{text_color}" text-anchor="middle" class="animate-fade {delay_class}">{count}</text>'
                )

        return "\n  ".join(bars)
