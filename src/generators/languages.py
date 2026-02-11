from src.generators.base import BaseGenerator


class LanguagesGenerator(BaseGenerator):
    """Generates the languages SVG template with programming language statistics."""

    OUTPUT_NAME = "languages"
    TEMPLATE_NAME = "languages.svg"

    async def generate(self) -> None:
        languages = await self.stats.get_languages()

        base_replacements = {
            "progress": self.formatter.format_language_progress(languages),
        }

        def theme_callback(colors):
            return {
                "lang_list": self.formatter.format_language_list(
                    languages,
                    text_color=colors.get("text_color", "#24292f"),
                    percent_color=colors.get("percent_color", "#57606a")
                )
            }

        self.render_for_all_themes(
            self.TEMPLATE_NAME,
            self.OUTPUT_NAME,
            base_replacements,
            theme_callback
        )
