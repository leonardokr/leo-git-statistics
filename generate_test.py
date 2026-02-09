#!/usr/bin/env python3
"""
Script to test SVG generation with mock data.
Does not require a connection to the GitHub API.
"""

from src.core.config import Config
from src.presentation.stats_formatter import StatsFormatter
from src.presentation.svg_template import SVGTemplate


def main():
    config = Config()
    formatter = StatsFormatter()
    template_engine = SVGTemplate(config.TEMPLATE_PATH, config.OUTPUT_DIR)

    mock_languages = {
        "Python": {"size": 45000, "prop": 45.0, "color": "#3572A5"},
        "TypeScript": {"size": 25000, "prop": 25.0, "color": "#3178c6"},
        "JavaScript": {"size": 15000, "prop": 15.0, "color": "#f1e05a"},
        "Rust": {"size": 8000, "prop": 8.0, "color": "#dea584"},
        "Go": {"size": 4000, "prop": 4.0, "color": "#00ADD8"},
        "Shell": {"size": 3000, "prop": 3.0, "color": "#89e051"},
    }

    for theme_name, theme_config in config.THEMES.items():
        colors = theme_config["colors"]

        replacements = {
            "progress": formatter.format_language_progress(mock_languages),
            "lang_list": formatter.format_language_list(
                mock_languages,
                text_color=colors.get("text_color", "#24292f"),
                percent_color=colors.get("percent_color", "#57606a")
            )
        }
        replacements.update(colors)

        template_engine.render_and_save(
            config.LANGUAGES_TEMPLATE,
            "languages",
            replacements,
            theme_config["suffix"]
        )
        print(f"Generated languages{theme_config['suffix']}.svg")

    mock_overview = {
        "name": "User's",
        "views": "12,345",
        "clones": "1,234",
        "stars": "567",
        "forks": "89",
        "contributions": "2,345",
        "lines_changed": "123,456",
        "avg_contribution_percent": "78.5",
        "repos": "42",
        "collaborators": "15",
        "contributors": "28",
        "views_from_date": "Repository views (as of 2024-01-01)",
        "clones_from_date": "Repository clones (as of 2024-01-01)",
        "issues": "23",
        "pull_requests": "45",
        "show_total_contributions": "table-row",
        "show_repositories": "table-row",
        "show_lines_changed": "table-row",
        "show_avg_percent": "table-row",
        "show_collaborators": "table-row",
        "show_contributors": "table-row",
        "show_views": "table-row",
        "show_clones": "table-row",
        "show_forks": "table-row",
        "show_stars": "table-row",
        "show_pull_requests": "table-row",
        "show_issues": "table-row",
    }

    for theme_name, theme_config in config.THEMES.items():
        replacements = mock_overview.copy()
        replacements.update(theme_config["colors"])

        template_engine.render_and_save(
            config.OVERVIEW_TEMPLATE,
            "overview",
            replacements,
            theme_config["suffix"]
        )
        print(f"Generated overview{theme_config['suffix']}.svg")

    mock_streak = {
        "current_streak": "15",
        "longest_streak": "42",
        "current_streak_range": "Jan 25 - Feb 9",
        "longest_streak_range": "Mar 1 - Apr 12, 2024",
        "total_contributions": "2,345",
        "contribution_year": "All time",
    }

    for theme_name, theme_config in config.THEMES.items():
        replacements = mock_streak.copy()
        replacements.update(theme_config["colors"])

        template_engine.render_and_save(
            config.STREAK_TEMPLATE,
            "streak",
            replacements,
            theme_config["suffix"]
        )
        print(f"Generated streak{theme_config['suffix']}.svg")

    print("\nAll test images generated in 'generated_images/' folder.")

if __name__ == "__main__":
    main()
