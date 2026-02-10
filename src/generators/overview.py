from src.generators.base import BaseGenerator
from src.core.environment import Environment


class OverviewGenerator(BaseGenerator):
    """
    Generates the overview SVG template with general GitHub statistics.
    """

    def __init__(self, config, stats, formatter, template_engine, environment: Environment):
        super().__init__(config, stats, formatter, template_engine)
        self.environment = environment

    async def generate(self, output_name: str = "overview") -> None:
        lines_added, lines_removed = await self.stats.lines_changed
        total_lines_changed = lines_added + lines_removed

        base_replacements = {
            "name": self.formatter.format_name(await self.stats.name),
            "views": self.formatter.format_number(await self.stats.views),
            "clones": self.formatter.format_number(await self.stats.clones),
            "stars": self.formatter.format_number(await self.stats.stargazers),
            "forks": self.formatter.format_number(await self.stats.forks),
            "contributions": self.formatter.format_number(await self.stats.total_contributions),
            "lines_changed": self.formatter.format_number(total_lines_changed),
            "avg_contribution_percent": await self.stats.avg_contribution_percent,
            "repos": self.formatter.format_number(len(await self.stats.repos)),
            "collaborators": self.formatter.format_number(await self.stats.collaborators),
            "contributors": self.formatter.format_number(max(len(await self.stats.contributors) - 1, 0)),
            "views_from_date": f"Repository views (as of {await self.stats.views_from_date})",
            "clones_from_date": f"Repository clones (as of {await self.stats.clones_from_date})",
            "issues": self.formatter.format_number(await self.stats.issues),
            "pull_requests": self.formatter.format_number(await self.stats.pull_requests),
            "show_total_contributions": "table-row" if self.environment.show_total_contributions else "none",
            "show_repositories": "table-row" if self.environment.show_repositories else "none",
            "show_lines_changed": "table-row" if self.environment.show_lines_changed else "none",
            "show_avg_percent": "table-row" if self.environment.show_avg_percent else "none",
            "show_collaborators": "table-row" if self.environment.show_collaborators else "none",
            "show_contributors": "table-row" if self.environment.show_contributors else "none",
            "show_views": "table-row" if self.environment.show_views else "none",
            "show_clones": "table-row" if self.environment.show_clones else "none",
            "show_forks": "table-row" if self.environment.show_forks else "none",
            "show_stars": "table-row" if self.environment.show_stars else "none",
            "show_pull_requests": "table-row" if self.environment.show_pull_requests else "none",
            "show_issues": "table-row" if self.environment.show_issues else "none",
        }

        self.render_for_all_themes(
            self.config.OVERVIEW_TEMPLATE,
            output_name,
            base_replacements
        )
