"""GitHub credential resolution."""

import os


class GitHubCredentials:
    """Resolves GitHub authentication credentials from environment variables."""

    @staticmethod
    def get_github_token() -> str:
        """
        Retrieves the GitHub personal access token from environment variables.

        :return: The access token.
        :raises Exception: If the token is not set.
        """
        token = os.getenv("ACCESS_TOKEN")
        if not token:
            raise Exception("A personal access token is required to proceed!")
        return token

    @staticmethod
    def get_github_actor() -> str:
        """
        Retrieves the GitHub actor (username) from environment variables.

        :return: The GitHub username.
        :raises RuntimeError: If GITHUB_ACTOR is not set.
        """
        actor = os.getenv("GITHUB_ACTOR")
        if not actor:
            raise RuntimeError("Environment variable GITHUB_ACTOR must be set")
        return actor
