from asyncio import run, gather
from aiohttp import ClientSession
from src.core.environment import Environment
from src.core.stats_collector import StatsCollector
from src.core.config import Config
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate

class ImageOrchestrator:
    """
    Orchestrates the generation of GitHub statistics images.

    This class coordinates the process of fetching statistics from GitHub,
    formatting them, and rendering them into SVG templates.
    """

    def __init__(self):
        """
        Initializes the orchestrator and starts the image generation process.
        """
        self.config = Config()
        self.formatter = StatsFormatter()
        self.template_engine = SVGTemplate(self.config.TEMPLATE_PATH, self.config.OUTPUT_DIR)
        
        access_token = self.config.get_github_token()
        user = self.config.get_github_actor()
        
        self.__environment = Environment(username=user, access_token=access_token)
        self.__stats = None

        run(self.start())

    async def start(self) -> None:
        """
        Initializes the StatsCollector and triggers concurrent generation of images.
        """
        async with ClientSession() as session:
            self.__stats = StatsCollector(environment_vars=self.__environment, session=session)
            await gather(
                self.generate_languages(),
                self.generate_overview(),
                self.generate_streak()
            )

    async def generate_overview(self) -> None:
        """
        Fetches overview statistics and renders the overview SVG templates.
        """
        stats = self.__stats
        env = self.__environment
        
        lines_added, lines_removed = await stats.lines_changed
        total_lines_changed = lines_added + lines_removed

        base_replacements = {
            "name": self.formatter.format_name(await stats.name),
            "views": self.formatter.format_number(await stats.views),
            "clones": self.formatter.format_number(await stats.clones),
            "stars": self.formatter.format_number(await stats.stargazers),
            "forks": self.formatter.format_number(await stats.forks),
            "contributions": self.formatter.format_number(await stats.total_contributions),
            "lines_changed": self.formatter.format_number(total_lines_changed),
            "avg_contribution_percent": await stats.avg_contribution_percent,
            "repos": self.formatter.format_number(len(await stats.repos)),
            "collaborators": self.formatter.format_number(await stats.collaborators),
            "contributors": self.formatter.format_number(max(len(await stats.contributors) - 1, 0)),
            "views_from_date": f"Repository views (as of {await stats.views_from_date})",
            "clones_from_date": f"Repository clones (as of {await stats.clones_from_date})",
            "issues": self.formatter.format_number(await stats.issues),
            "pull_requests": self.formatter.format_number(await stats.pull_requests),
            
            # Visibility toggles (CSS display property)
            "show_total_contributions": "table-row" if env.show_total_contributions else "none",
            "show_repositories": "table-row" if env.show_repositories else "none",
            "show_lines_changed": "table-row" if env.show_lines_changed else "none",
            "show_avg_percent": "table-row" if env.show_avg_percent else "none",
            "show_collaborators": "table-row" if env.show_collaborators else "none",
            "show_contributors": "table-row" if env.show_contributors else "none",
            "show_views": "table-row" if env.show_views else "none",
            "show_clones": "table-row" if env.show_clones else "none",
            "show_forks": "table-row" if env.show_forks else "none",
            "show_stars": "table-row" if env.show_stars else "none",
            "show_pull_requests": "table-row" if env.show_pull_requests else "none",
            "show_issues": "table-row" if env.show_issues else "none",
        }
        
        for theme_name, theme_config in self.config.THEMES.items():
            replacements = base_replacements.copy()
            replacements.update(theme_config["colors"])
            
            self.template_engine.render_and_save(
                self.config.OVERVIEW_TEMPLATE,
                "overview",
                replacements,
                theme_config["suffix"]
            )

    async def generate_languages(self) -> None:
        """
        Fetches language statistics and renders the languages SVG templates.
        """
        languages = await self.__stats.languages

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

    async def generate_streak(self) -> None:
        """
        Fetches streak statistics and renders the streak SVG templates.
        """
        stats = self.__stats
        current_year = str(__import__('datetime').date.today().year)

        base_replacements = {
            "current_streak": str(await stats.current_streak),
            "longest_streak": str(await stats.longest_streak),
            "current_streak_range": await stats.current_streak_range,
            "longest_streak_range": await stats.longest_streak_range,
            "total_contributions": self.formatter.format_number(await stats.total_contributions),
            "contribution_year": f"All time"
        }

        for theme_name, theme_config in self.config.THEMES.items():
            replacements = base_replacements.copy()
            replacements.update(theme_config["colors"])

            self.template_engine.render_and_save(
                self.config.STREAK_TEMPLATE,
                "streak",
                replacements,
                theme_config["suffix"]
            )
