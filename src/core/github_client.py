#!/usr/bin/python3

from asyncio import Semaphore, sleep
from requests import post, get
from aiohttp import ClientSession
from typing import Dict, Optional, List
from requests import get
from json import loads

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

    def __init__(self,
                 username: str,
                 access_token: str,
                 session: ClientSession,
                 max_connections: int = __DEFAULT_MAX_CONNECTIONS):
        """
        Initializes the GitHubClient.

        :param username: GitHub username.
        :param access_token: GitHub personal access token.
        :param session: aiohttp ClientSession for making requests.
        :param max_connections: Maximum number of concurrent connections.
        """
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
        except:
            print("aiohttp failed for GraphQL query")

            # Fall back on non-async requests
            async with self.semaphore:
                r_requests = post(
                    self.__GITHUB_API_URL + self.__GRAPHQL_PATH,
                    headers=self.headers,
                    json={"query": generated_query},
                )
                result = r_requests.json()

                if result is not None:
                    return result
        return dict()

    async def query_rest(self,
                         path: str,
                         params: Optional[Dict] = None) -> Dict:
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
                    print(f"A path returned 202. Retrying...")
                    await sleep(self.__ASYNCIO_SLEEP_TIME)
                    continue

                result = await r_async.json()

                if result is not None:
                    return result
            except:
                print("aiohttp failed for REST query attempt #" + str(i + 1))

                # Fall back on non-async requests
                async with self.semaphore:
                    r_requests = get(
                        self.__GITHUB_API_URL + path,
                        headers=self.headers,
                        params=tuple(params.items()),
                    )

                    if r_requests.status_code == 202:
                        print(f"A path returned 202. Retrying...")
                        await sleep(self.__ASYNCIO_SLEEP_TIME)
                        continue
                    elif r_requests.status_code == 200:
                        return r_requests.json()

        print("Too many 202s. Data for this repository will be incomplete.")
        return dict()

    @staticmethod
    def repos_overview(contrib_cursor: Optional[str] = None,
                       owned_cursor: Optional[str] = None) -> str:
        """
        Generates a GraphQL query for an overview of repositories.

        :param contrib_cursor: Cursor for paginating contributed repositories.
        :param owned_cursor: Cursor for paginating owned repositories.
        :return: GraphQL query string.
        """
        """
        :return: GraphQL queries with overview of user repositories
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
                    after: {
                        "null" if owned_cursor is None 
                        else '"' + owned_cursor + '"'
                    }) {{
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
                    after: {
                    "null" if contrib_cursor is None 
                    else '"' + contrib_cursor + '"'}) {{
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
        Generates a GraphQL query to retrieve all years the user has contributions.

        :return: GraphQL query string.
        """
        """
        :return: GraphQL query to get all years the user has been a contributor
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
        Generates a GraphQL query for contributions in a specific year.

        :param year: The year to query.
        :return: GraphQL query string.
        """
        """
        :param year: year to query for
        :return: portion of a GraphQL query with desired info for a given year
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
        Generates a GraphQL query for contributions across multiple years.

        :param years: List of years to include in the query.
        :return: GraphQL query string.
        """
        """
        :param years: list of years to get contributions for
        :return: query to retrieve contribution information for all user years
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
        Retrieves a mapping of programming languages to their respective colors.

        :return: Dictionary mapping language names to hex color codes.
        """
        url = get("https://raw.githubusercontent.com/ozh/github-colors/master/colors.json")
        return loads(url.text)
