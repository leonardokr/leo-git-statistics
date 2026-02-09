import pytest
from src.presentation.stats_formatter import StatsFormatter


class TestStatsFormatter:
    """
    Tests for the StatsFormatter class.
    """

    def test_format_name(self):
        """
        Tests the possessive name formatting.
        """
        assert StatsFormatter.format_name("Alice") == "Alice's"
        assert StatsFormatter.format_name("James") == "James'"
        assert StatsFormatter.format_name("") == ""

    def test_format_number(self):
        """
        Tests number formatting with separators.
        """
        assert StatsFormatter.format_number(1234) == "1,234"
        assert StatsFormatter.format_number("5678") == "5,678"
        assert StatsFormatter.format_number(1000000) == "1,000,000"
        assert StatsFormatter.format_number("abc") == "abc"

    def test_format_language_progress(self):
        """
        Tests the generation of SVG rect elements for the language progress bar.
        """
        languages = {
            "Python": {"size": 100, "color": "#3572A5", "prop": 50.0},
            "JavaScript": {"size": 100, "color": "#f1e05a", "prop": 50.0}
        }
        svg = StatsFormatter.format_language_progress(languages)
        assert 'fill="#3572A5"' in svg
        assert 'fill="#f1e05a"' in svg
        assert '<rect' in svg
        assert 'width="150.00"' in svg

    def test_format_language_progress_custom_width(self):
        """
        Tests the language progress bar with custom total width.
        """
        languages = {
            "Python": {"size": 100, "color": "#3572A5", "prop": 100.0}
        }
        svg = StatsFormatter.format_language_progress(languages, total_width=200)
        assert 'width="200.00"' in svg

    def test_format_language_list(self):
        """
        Tests the generation of HTML for the language list.
        """
        languages = {
            "Python": {"size": 100, "color": "#3572A5", "prop": 100.0}
        }
        html = StatsFormatter.format_language_list(languages)
        assert 'Python' in html
        assert '100.0%' in html
        assert 'background-color: #3572A5' in html

    def test_format_language_list_max_items(self):
        """
        Tests that the language list respects the max_items limit.
        """
        languages = {
            "Python": {"size": 100, "color": "#3572A5", "prop": 25.0},
            "JavaScript": {"size": 80, "color": "#f1e05a", "prop": 20.0},
            "TypeScript": {"size": 60, "color": "#2b7489", "prop": 15.0},
            "Go": {"size": 40, "color": "#00ADD8", "prop": 10.0},
            "Rust": {"size": 30, "color": "#dea584", "prop": 7.5},
        }
        html = StatsFormatter.format_language_list(languages, max_items=3)
        assert 'Python' in html
        assert 'JavaScript' in html
        assert 'TypeScript' in html
        assert 'Go' not in html
        assert 'Rust' not in html
