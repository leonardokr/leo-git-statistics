import os

class Config:
    """
    Centralized configuration settings for the application.
    """
    OUTPUT_DIR = "generated_images"
    TEMPLATE_PATH = "src/templates/"
    
    OVERVIEW_TEMPLATE = "overview.svg"
    LANGUAGES_TEMPLATE = "languages.svg"

    THEMES = {
        "light": {
            "suffix": "LightMode",
            "colors": {
                "bg_color": "#FFFFFF",
                "title_color": "#0969da",
                "text_color": "#24292f",
                "icon_color": "#57606a",
                "percent_color": "#57606a",
                "border_color": "#d0d7de"
            }
        },
        "dark": {
            "suffix": "DarkMode",
            "colors": {
                "bg_color": "#0d1117",
                "title_color": "#58a6ff",
                "text_color": "#ffffff",
                "icon_color": "#8b949e",
                "percent_color": "#8b949e",
                "border_color": "#30363d"
            }
        },
        "default": {
            "suffix": "",
            "colors": {
                "bg_color": "#FFFFFF",
                "title_color": "#0969da",
                "text_color": "#24292f",
                "icon_color": "#57606a",
                "percent_color": "#57606a",
                "border_color": "#d0d7de"
            }
        }
    }
    
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
