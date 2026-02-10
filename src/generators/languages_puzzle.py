from src.generators.base import BaseGenerator


class LanguagesPuzzleGenerator(BaseGenerator):
    """
    Generates the languages puzzle SVG template with a treemap visualization.
    """

    async def generate(self) -> None:
        languages = await self.stats.languages

        for theme_name, theme_config in self.config.THEMES.items():
            colors = theme_config["colors"]

            hue = colors.get("puzzle_hue", 210)
            saturation_range = colors.get("puzzle_saturation_range", [65, 85])
            lightness_range = colors.get("puzzle_lightness_range", [40, 60])
            hue_spread = colors.get("puzzle_hue_spread", 80)
            puzzle_gap = colors.get("puzzle_gap", 2)
            puzzle_text_color = colors.get("puzzle_text_color", "#FFFFFF")

            puzzle_blocks = self.formatter.format_puzzle_blocks(
                languages,
                width=400,
                height=200,
                hue=hue,
                saturation_range=saturation_range,
                lightness_range=lightness_range,
                hue_spread=hue_spread,
                gap=puzzle_gap
            )

            replacements = {
                "puzzle_blocks": puzzle_blocks,
                "puzzle_text_color": puzzle_text_color
            }
            replacements.update(colors)

            self.template_engine.render_and_save(
                self.config.LANGUAGES_PUZZLE_TEMPLATE,
                "languages_puzzle",
                replacements,
                theme_config["suffix"]
            )
