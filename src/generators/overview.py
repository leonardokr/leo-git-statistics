from src.generators.base import BaseGenerator
from src.core.environment import Environment


class OverviewGenerator(BaseGenerator):
    """
    Generates the overview SVG template with general GitHub statistics.
    """

    def __init__(self, config, stats, formatter, template_engine, environment: Environment):
        super().__init__(config, stats, formatter, template_engine)
        self.environment = environment

    OUTPUT_NAME = "overview"

    async def generate(self) -> None:
        lines_added, lines_removed = await self.stats.get_lines_changed()
        total_lines_changed = lines_added + lines_removed

        base_replacements = {
            "name": self.formatter.format_name(await self.stats.get_name()),
            "views": self.formatter.format_number(await self.stats.get_views()),
            "clones": self.formatter.format_number(await self.stats.get_clones()),
            "stars": self.formatter.format_number(await self.stats.get_stargazers()),
            "forks": self.formatter.format_number(await self.stats.get_forks()),
            "contributions": self.formatter.format_number(await self.stats.get_total_contributions()),
            "lines_changed": self.formatter.format_number(total_lines_changed),
            "avg_contribution_percent": await self.stats.get_avg_contribution_percent(),
            "repos": self.formatter.format_number(len(await self.stats.get_repos())),
            "collaborators": self.formatter.format_number(await self.stats.get_collaborators()),
            "contributors": self.formatter.format_number(max(len(await self.stats.get_contributors()) - 1, 0)),
            "views_from_date": f"Repository views (as of {await self.stats.get_views_from_date()})",
            "clones_from_date": f"Repository clones (as of {await self.stats.get_clones_from_date()})",
            "issues": self.formatter.format_number(await self.stats.get_issues()),
            "pull_requests": self.formatter.format_number(await self.stats.get_pull_requests()),
            "show_total_contributions": "table-row" if self.environment.display.show_total_contributions else "none",
            "show_repositories": "table-row" if self.environment.display.show_repositories else "none",
            "show_lines_changed": "table-row" if self.environment.display.show_lines_changed else "none",
            "show_avg_percent": "table-row" if self.environment.display.show_avg_percent else "none",
            "show_collaborators": "table-row" if self.environment.display.show_collaborators else "none",
            "show_contributors": "table-row" if self.environment.display.show_contributors else "none",
            "show_views": "table-row" if self.environment.display.show_views else "none",
            "show_clones": "table-row" if self.environment.display.show_clones else "none",
            "show_forks": "table-row" if self.environment.display.show_forks else "none",
            "show_stars": "table-row" if self.environment.display.show_stars else "none",
            "show_pull_requests": "table-row" if self.environment.display.show_pull_requests else "none",
            "show_issues": "table-row" if self.environment.display.show_issues else "none",
        }

        self.render_for_all_themes(
            self.config.OVERVIEW_TEMPLATE,
            self.OUTPUT_NAME,
            base_replacements
        )
