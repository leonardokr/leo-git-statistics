from src.generators.base import BaseGenerator, register_generator
from src.core.protocols import LanguageProvider


@register_generator
class LanguagesPuzzleGenerator(BaseGenerator):
    """Generates the languages puzzle SVG template with a treemap visualization."""

    stats: LanguageProvider

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
                hue=colors["puzzle_hue"],
                saturation_range=colors["puzzle_saturation_range"],
                lightness_range=colors["puzzle_lightness_range"],
                hue_spread=colors["puzzle_hue_spread"],
                gap=colors["puzzle_gap"]
            )
            return {
                "puzzle_blocks": puzzle_blocks,
                "puzzle_text_color": colors["puzzle_text_color"]
            }

        self.render_for_all_themes(
            self.TEMPLATE_NAME,
            self.OUTPUT_NAME,
            {},
            theme_callback
        )
