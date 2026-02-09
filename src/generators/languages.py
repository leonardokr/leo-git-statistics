from src.generators.base import BaseGenerator


class LanguagesGenerator(BaseGenerator):
    """
    Generates the languages SVG template with programming language statistics.
    """

    async def generate(self) -> None:
        languages = await self.stats.languages

        for theme_name, theme_config in self.config.THEMES.items():
            colors = theme_config["colors"]

            replacements = {
                "progress": self.formatter.format_language_progress(languages),
                "lang_list": self.formatter.format_language_list(
                    languages,
                    text_color=colors.get("text_color", "#24292f"),
                    percent_color=colors.get("percent_color", "#57606a")
                )
            }
            replacements.update(colors)

            self.template_engine.render_and_save(
                self.config.LANGUAGES_TEMPLATE,
                "languages",
                replacements,
                theme_config["suffix"]
            )
