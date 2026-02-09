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
        Tests the generation of HTML for the language progress bar.
        """
        languages = {
            "Python": {"size": 100, "color": "#3572A5", "prop": 50.0},
            "JavaScript": {"size": 100, "color": "#f1e05a", "prop": 50.0}
        }
        html = StatsFormatter.format_language_progress(languages)
        assert 'background-color: #3572A5' in html
        assert 'width: 50.00000%' in html
        assert 'background-color: #f1e05a' in html

    def test_format_language_list(self):
        """
        Tests the generation of HTML for the language list.
        """
        languages = {
            "Python": {"size": 100, "color": "#3572A5", "prop": 100.0}
        }
        html = StatsFormatter.format_language_list(languages)
        assert 'Python' in html
        assert '100.000%' in html
        assert 'fill:#3572A5' in html
