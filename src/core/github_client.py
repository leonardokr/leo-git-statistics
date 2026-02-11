#!/usr/bin/python3
"""
GitHub API Client Module.

This module provides an async-first client for interacting with GitHub's
GraphQL (v4) and REST (v3) APIs with proper error handling and rate limiting.
"""

import logging
from asyncio import Semaphore, sleep
from typing import Dict, Optional, List, Union

import aiohttp
import requests
from json import loads, JSONDecodeError

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """
    Custom exception for GitHub API errors.

    :param message: Error description.
    :param status_code: HTTP status code if available.
    """

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GitHubClient:
    """
    Client for interacting with GitHub's GraphQL (v4) and REST (v3) APIs.

    This class provides methods to perform asynchronous and synchronous queries
    to GitHub, handling authentication and rate limiting through semaphores.
    """

    __GITHUB_API_URL = "https://api.github.com/"
    __GRAPHQL_PATH = "graphql"
    __REST_QUERY_LIMIT = 60
    __ASYNCIO_SLEEP_TIME = 2
    __DEFAULT_MAX_CONNECTIONS = 10

    def __init__(
        self,
        username: str,
        access_token: str,
        session: aiohttp.ClientSession,
        max_connections: int = __DEFAULT_MAX_CONNECTIONS,
    ):
        """
        Initializes the GitHubClient.

        :param username: GitHub username.
        :param access_token: GitHub personal access token.
        :param session: aiohttp ClientSession for making requests.
        :param max_connections: Maximum number of concurrent connections.
        """
        if not username or not username.strip():
            raise ValueError("GitHub username must not be empty")
        if not access_token or not access_token.strip():
            raise ValueError("GitHub access token must not be empty")

        self.username = username
        self.access_token = access_token
        self.session = session
        self.semaphore = Semaphore(max_connections)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

    async def query(self, generated_query: str) -> Dict:
        """
        Makes a request to the GitHub GraphQL API.

        :param generated_query: The GraphQL query string to be sent.
        :return: Decoded GraphQL JSON response as a dictionary.
        """
        try:
            async with self.semaphore:
                r_async = await self.session.post(
                    self.__GITHUB_API_URL + self.__GRAPHQL_PATH,
                    headers=self.headers,
                    json={"query": generated_query},
                )
            result = await r_async.json()

            if result is not None:
                return result
        except (aiohttp.ClientError, aiohttp.ServerTimeoutError, JSONDecodeError) as e:
            logger.warning("aiohttp failed for GraphQL query: %s. Falling back to sync.", e)

            try:
                async with self.semaphore:
                    r_requests = requests.post(
                        self.__GITHUB_API_URL + self.__GRAPHQL_PATH,
                        headers=self.headers,
                        json={"query": generated_query},
                    )
                    result = r_requests.json()

                    if result is not None:
                        return result
            except (requests.RequestException, JSONDecodeError, ValueError) as fallback_error:
                logger.error("Sync fallback also failed: %s", fallback_error)

        return dict()

    async def query_rest(self,
                         path: str,
                         params: Optional[Dict] = None) -> Union[Dict, List]:
        """
        Makes a request to the GitHub REST API.

        :param path: The API path to query (e.g., 'repos/owner/repo').
        :param params: Optional dictionary of query parameters.
        :return: Deserialized REST JSON response as a dictionary.
        """
        for i in range(self.__REST_QUERY_LIMIT):
            if params is None:
                params = dict()
            if path.startswith("/"):
                path = path[1:]

            try:
                async with self.semaphore:
                    r_async = await self.session.get(
                        self.__GITHUB_API_URL + path,
                        headers=self.headers,
                        params=tuple(params.items()),
                    )

                if r_async.status == 202:
                    logger.debug("Path %s returned 202. Retrying attempt %d...", path, i + 1)
                    await sleep(self.__ASYNCIO_SLEEP_TIME)
                    continue

                result = await r_async.json()

                if result is not None:
                    return result
            except (aiohttp.ClientError, aiohttp.ServerTimeoutError, JSONDecodeError) as e:
                logger.warning("aiohttp failed for REST query attempt #%d: %s", i + 1, e)

                try:
                    async with self.semaphore:
                        r_requests = requests.get(
                            self.__GITHUB_API_URL + path,
                            headers=self.headers,
                            params=tuple(params.items()),
                        )

                        if r_requests.status_code == 202:
                            logger.debug("Sync fallback returned 202. Retrying...")
                            await sleep(self.__ASYNCIO_SLEEP_TIME)
                            continue
                        elif r_requests.status_code == 200:
                            return r_requests.json()
                except (requests.RequestException, JSONDecodeError, ValueError) as fallback_error:
                    logger.error("Sync fallback failed: %s", fallback_error)

        logger.warning("Too many 202s for path %s. Data will be incomplete.", path)
        return dict()

    @staticmethod
    def repos_overview(
        contrib_cursor: Optional[str] = None,
        owned_cursor: Optional[str] = None,
    ) -> str:
        """
        Generate a GraphQL query for an overview of repositories.

        :param contrib_cursor: Cursor for paginating contributed repositories.
        :param owned_cursor: Cursor for paginating owned repositories.
        :return: GraphQL query string.
        """
        return f"""
            {{
                viewer {{
                    login,
                    name,
                    repositories(
                    first: 100,
                    orderBy: {{
                        field: UPDATED_AT,
                        direction: DESC
                    }},
                    after: {"null" if owned_cursor is None else '"' + owned_cursor + '"'}) {{
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                        nodes {{
                            nameWithOwner
                            stargazers {{
                                totalCount
                            }}
                            forkCount
                            isFork
                            isEmpty
                            isArchived
                            isPrivate
                            languages(first: 20, orderBy: {{
                                field: SIZE, 
                                direction: DESC
                            }}) {{
                                edges {{
                                    size
                                    node {{
                                        name
                                        color
                                    }}
                                }}
                            }}
                        }}
                    }}
                    repositoriesContributedTo(
                    first: 100,
                    includeUserRepositories: false,
                    orderBy: {{
                        field: UPDATED_AT,
                        direction: DESC
                    }},
                    contributionTypes: [
                        COMMIT,
                        PULL_REQUEST,
                        REPOSITORY,
                        PULL_REQUEST_REVIEW
                    ]
                    after: {"null" if contrib_cursor is None else '"' + contrib_cursor + '"'}) {{
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                        nodes {{
                            nameWithOwner
                            stargazers {{
                                totalCount
                            }}
                            forkCount
                            isFork
                            isEmpty
                            isArchived
                            isPrivate
                            languages(first: 20, orderBy: {{
                                field: SIZE, 
                                direction: DESC
                            }}) {{
                                edges {{
                                    size
                                    node {{
                                        name
                                        color
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}"""

    @staticmethod
    def contributions_all_years() -> str:
        """
        Generate a GraphQL query to retrieve all years the user has contributions.

        :return: GraphQL query string.
        """
        return """
            query {
                viewer {
                    contributionsCollection {
                        contributionYears
                    }
                }
            }"""

    @staticmethod
    def contributions_by_year(year: str) -> str:
        """
        Generate a GraphQL query for contributions in a specific year.

        :param year: The year to query.
        :return: GraphQL query string.
        """
        return f"""
            year{year}: contributionsCollection(
            from: "{year}-01-01T00:00:00Z",
            to: "{int(year) + 1}-01-01T00:00:00Z"
            ) {{
                contributionCalendar {{
                    totalContributions
                }}
            }}"""

    @classmethod
    def all_contributions(cls, years: List[str]) -> str:
        """
        Generate a GraphQL query for contributions across multiple years.

        :param years: List of years to include in the query.
        :return: GraphQL query string.
        """
        by_years = "\n".join(map(cls.contributions_by_year, years))
        return f"""
            query {{
                viewer {{
                    {by_years}
                }}
            }}"""

    @staticmethod
    def get_language_colors() -> Dict:
        """
        Retrieve a mapping of programming languages to their respective colors.

        :return: Dictionary mapping language names to hex color codes.
        """
        try:
            response = requests.get(
                "https://raw.githubusercontent.com/ozh/github-colors/master/colors.json"
            )
            response.raise_for_status()
            return loads(response.text)
        except (requests.RequestException, JSONDecodeError, ValueError) as e:
            logger.error("Failed to fetch language colors: %s", e)
            return dict()
