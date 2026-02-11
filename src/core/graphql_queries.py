"""GraphQL query builders for the GitHub API."""

from typing import List, Optional


class GraphQLQueries:
    """Generates GraphQL query strings for the GitHub API."""

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
