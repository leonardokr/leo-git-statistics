import pytest
from src.core.environment import Environment

class TestEnvironment:
    """
    Tests for the Environment class.
    """

    def test_environment_initialization(self, monkeypatch):
        """
        Tests basic initialization of the Environment class.
        """
        monkeypatch.setenv("EXCLUDED", "repo1,repo2")
        monkeypatch.setenv("EXCLUDED_LANGS", "lang1")
        
        env = Environment(username="testuser", access_token="testtoken")
        
        assert env.username == "testuser"
        assert env.access_token == "testtoken"
        assert "repo1" in env.filter.exclude_repos
        assert "repo2" in env.filter.exclude_repos
        assert "lang1" in env.filter.exclude_langs

    def test_environment_boolean_filters(self, monkeypatch):
        """
        Tests boolean filter initialization from environment variables.
        """
        monkeypatch.setenv("INCLUDE_FORKED_REPOS", "true")
        monkeypatch.setenv("EXCLUDE_PRIVATE_REPOS", "false")
        
        env = Environment(username="testuser", access_token="testtoken")
        
        assert env.filter.include_forked_repos is True
        assert env.filter.exclude_private_repos is False

    def test_validate_date(self):
        """
        Tests date validation logic.
        """
        env = Environment(username="u", access_token="t")
        assert env.traffic._validate_date("2023-01-01") == "2023-01-01"
        assert env.traffic._validate_date("invalid-date") == ""
        assert env.traffic._validate_date("01-01-2023") == ""
