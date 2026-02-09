from src.generators.base import BaseGenerator


class StreakBatteryGenerator(BaseGenerator):
    """
    Generates the streak battery SVG template with a visual battery indicator.
    The battery fills based on current streak relative to longest streak,
    with a glow effect when hitting a new record.
    """

    async def generate(self, output_name: str = "streak_battery") -> None:
        current_streak = await self.stats.current_streak
        longest_streak = await self.stats.longest_streak
        recent_contributions = await self.stats.recent_contributions

        if longest_streak > 0:
            streak_percentage = min(100, int((current_streak / longest_streak) * 100))
        else:
            streak_percentage = 0 if current_streak == 0 else 100

        battery_max_height = 87
        battery_fill_height = int((streak_percentage / 100) * battery_max_height)
        battery_fill_y = 4 + (battery_max_height - battery_fill_height)

        is_record = current_streak > 0 and current_streak >= longest_streak

        for theme_name, theme_config in self.config.THEMES.items():
            colors = theme_config["colors"]
            contribution_bars = self._generate_contribution_bars(
                recent_contributions,
                colors.get("accent_color", "#0969da"),
                colors.get("text_color", "#24292f")
            )

            replacements = {
                "current_streak": str(current_streak),
                "longest_streak": str(longest_streak),
                "current_streak_range": await self.stats.current_streak_range,
                "longest_streak_range": await self.stats.longest_streak_range,
                "streak_percentage": str(streak_percentage),
                "battery_fill_height": str(battery_fill_height),
                "battery_fill_y": str(battery_fill_y),
                "is_record_class": "animate-glow" if is_record else "",
                "record_icon_class": "animate-pulse" if is_record else "",
                "battery_gradient_id": "glow-gradient" if is_record else "battery-gradient",
                "shimmer_display": "block" if streak_percentage > 10 else "none",
                "contribution_bars": contribution_bars,
            }
            replacements.update(colors)

            self.template_engine.render_and_save(
                self.config.STREAK_BATTERY_TEMPLATE,
                output_name,
                replacements,
                theme_config["suffix"]
            )

    def _generate_contribution_bars(self, contributions: list, bar_color: str, text_color: str) -> str:
        if not contributions:
            return ""

        max_contrib = max(contributions) if max(contributions) > 0 else 1
        bar_width = 14
        bar_gap = 4
        max_bar_height = 100
        bars = []

        for i, count in enumerate(contributions):
            bar_height = max(4, int((count / max_contrib) * max_bar_height)) if count > 0 else 4
            x = i * (bar_width + bar_gap)
            y = max_bar_height - bar_height
            delay_class = f"delay-{i + 1}"

            bars.append(
                f'<g class="animate-fill {delay_class}" style="transform-origin: {x + bar_width // 2}px bottom;">'
                f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" rx="2" fill="{bar_color}"/>'
                f'</g>'
            )

            if count > 0:
                text_y = y - 5
                bars.append(
                    f'<text x="{x + bar_width // 2}" y="{text_y}" font-family="\'Segoe UI\', Ubuntu, Sans-Serif" '
                    f'font-size="9" fill="{text_color}" text-anchor="middle" class="animate-fade {delay_class}">{count}</text>'
                )

        return "\n  ".join(bars)
