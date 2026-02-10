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
            saturation_range = colors.get("puzzle_saturation_range", [60, 85])
            lightness_range = colors.get("puzzle_lightness_range", [35, 65])
            puzzle_text_color = colors.get("puzzle_text_color", "#FFFFFF")

            puzzle_blocks = self.formatter.format_puzzle_blocks(
                languages,
                width=400,
                height=200,
                hue=hue,
                saturation_range=saturation_range,
                lightness_range=lightness_range
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
