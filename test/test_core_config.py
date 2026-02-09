import os
import pytest
from src.core.config import Config

class TestConfig:
    """
    Tests for the Config class.
    """

    def test_github_token_missing(self, monkeypatch):
        """
        Tests that an exception is raised when the access token is missing.
        """
        monkeypatch.delenv("ACCESS_TOKEN", raising=False)
        with pytest.raises(Exception, match="A personal access token is required to proceed!"):
            Config.get_github_token()

    def test_github_token_present(self, monkeypatch):
        """
        Tests that the access token is correctly retrieved.
        """
        monkeypatch.setenv("ACCESS_TOKEN", "fake_token")
        assert Config.get_github_token() == "fake_token"

    def test_github_actor_missing(self, monkeypatch):
        """
        Tests that an exception is raised when the GitHub actor is missing.
        """
        monkeypatch.delenv("GITHUB_ACTOR", raising=False)
        with pytest.raises(RuntimeError, match="Environment variable GITHUB_ACTOR must be set"):
            Config.get_github_actor()

    def test_github_actor_present(self, monkeypatch):
        """
        Tests that the GitHub actor is correctly retrieved.
        """
        monkeypatch.setenv("GITHUB_ACTOR", "fake_user")
        assert Config.get_github_actor() == "fake_user"

    def test_themes_configuration(self):
        """
        Tests that theme configurations are correctly defined.
        """
        assert "light" in Config.THEMES
        assert "dark" in Config.THEMES
        assert Config.THEMES["light"]["suffix"] == "LightMode"
        assert "bg_color" in Config.THEMES["light"]["colors"]
