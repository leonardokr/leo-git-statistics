from src.generators.base import BaseGenerator


class LanguagesPuzzleGenerator(BaseGenerator):
    """Generates the languages puzzle SVG template with a treemap visualization."""

    PUZZLE_WIDTH = 455
    PUZZLE_HEIGHT = 135

    OUTPUT_NAME = "languages_puzzle"
    TEMPLATE_NAME = "languages_puzzle.svg"

    async def generate(self) -> None:
        languages = await self.stats.get_languages()

        def theme_callback(colors):
            puzzle_blocks = self.formatter.format_puzzle_blocks(
                languages,
                width=self.PUZZLE_WIDTH,
                height=self.PUZZLE_HEIGHT,
                hue=colors.get("puzzle_hue", 210),
                saturation_range=colors.get("puzzle_saturation_range", [65, 85]),
                lightness_range=colors.get("puzzle_lightness_range", [40, 60]),
                hue_spread=colors.get("puzzle_hue_spread", 80),
                gap=colors.get("puzzle_gap", 2)
            )
            return {
                "puzzle_blocks": puzzle_blocks,
                "puzzle_text_color": colors.get("puzzle_text_color", "#FFFFFF")
            }

        self.render_for_all_themes(
            self.TEMPLATE_NAME,
            self.OUTPUT_NAME,
            {},
            theme_callback
        )
