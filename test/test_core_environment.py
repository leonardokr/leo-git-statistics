import pytest
import yaml
from src.core.environment import Environment

class TestEnvironment:
    """
    Tests for the Environment class.
    """

    def test_environment_initialization(self, tmp_path):
        """
        Tests basic initialization of the Environment class from config.yml.
        """
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            yaml.safe_dump(
                {
                    "timezone": "UTC",
                    "stats_generation": {
                        "excluded_repos": "repo1,repo2",
                        "excluded_langs": "lang1",
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        env = Environment(
            username="testuser",
            access_token="testtoken",
            config_path=str(config_path),
        )
        
        assert env.username == "testuser"
        assert env.access_token == "testtoken"
        assert "repo1" in env.filter.exclude_repos
        assert "repo2" in env.filter.exclude_repos
        assert "lang1" in env.filter.exclude_langs

    def test_environment_boolean_filters(self, tmp_path):
        """
        Tests boolean filter initialization from config.yml.
        """
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            yaml.safe_dump(
                {
                    "timezone": "UTC",
                    "stats_generation": {
                        "include_forked_repos": "true",
                        "exclude_private_repos": "false",
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        env = Environment(
            username="testuser",
            access_token="testtoken",
            config_path=str(config_path),
        )
        
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
