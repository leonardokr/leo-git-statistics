"""Repository statistics collection: repos, stars, forks and languages."""

import logging
from typing import Dict, Optional, Set, Any

from src.core.environment import Environment
from src.core.github_client import GitHubClient
from src.core.graphql_queries import GraphQLQueries

logger = logging.getLogger(__name__)


class RepoStatsCollector:
    """
    Collects repository-level statistics: repos, stars, forks, languages.

    :param environment_vars: Environment configuration.
    :param queries: GitHub API client instance.
    """

    def __init__(self, environment_vars: Environment, queries: GitHubClient):
        self._env = environment_vars
        self._queries = queries

        self._name: Optional[str] = None
        self._stargazers: Optional[int] = None
        self._forks: Optional[int] = None
        self._followers: Optional[int] = None
        self._following: Optional[int] = None
        self._languages: Optional[Dict[str, Any]] = None
        self._repos: Optional[Set[str]] = None
        self._empty_repos: Optional[Set[str]] = None
        self._repo_visibility: Optional[Dict[str, bool]] = None

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def stargazers(self) -> Optional[int]:
        return self._stargazers

    @property
    def forks(self) -> Optional[int]:
        return self._forks

    @property
    def followers(self) -> Optional[int]:
        return self._followers

    @property
    def following(self) -> Optional[int]:
        return self._following

    @property
    def languages(self) -> Optional[Dict[str, Any]]:
        return self._languages

    @property
    def repos(self) -> Optional[Set[str]]:
        return self._repos

    @property
    def empty_repos(self) -> Optional[Set[str]]:
        return self._empty_repos

    @property
    def repo_visibility(self) -> Optional[Dict[str, bool]]:
        return self._repo_visibility

    def is_repo_name_invalid(self, repo_name: Optional[str]) -> bool:
        """
        Check if a repository name is invalid or should be excluded.

        :param repo_name: The name of the repository (owner/name format).
        :return: True if the repository should be excluded, False otherwise.
        """
        if not repo_name:
            return True
        return (
            repo_name in self._repos
            or len(self._env.filter.only_included_repos) > 0
            and repo_name not in self._env.filter.only_included_repos
            or repo_name in self._env.filter.exclude_repos
        )

    def is_repo_type_excluded(self, repo_data: Dict[str, Any]) -> bool:
        """
        Check if a repository should be excluded based on its type.

        :param repo_data: Dictionary containing repository metadata from the API.
        :return: True if the repository type should be excluded, False otherwise.
        """
        return (
            (not self._env.filter.include_forked_repos
             and (repo_data.get("isFork") or repo_data.get("fork")))
            or (self._env.filter.exclude_archive_repos
                and (repo_data.get("isArchived") or repo_data.get("archived")))
            or (self._env.filter.exclude_private_repos
                and (repo_data.get("isPrivate") or repo_data.get("private")))
            or (self._env.filter.exclude_public_repos
                and not repo_data.get("isPrivate") and not repo_data.get("private"))
        )

    async def collect(self) -> None:
        """
        Fetch and aggregate general statistics from GitHub.

        Populates repos, stargazers, forks, languages and name via paginated
        GraphQL queries.
        """
        self._stargazers = 0
        self._forks = 0
        self._languages = dict()
        self._repos = set()
        self._empty_repos = set()
        self._repo_visibility = dict()

        next_owned = None
        next_contrib = None

        while True:
            raw_results = await self._queries.query(
                GraphQLQueries.repos_overview(
                    owned_cursor=next_owned, contrib_cursor=next_contrib
                )
            )
            raw_results = raw_results if raw_results is not None else {}

            viewer_data = raw_results.get("data", {}).get("viewer", {})
            self._name = viewer_data.get("name") or viewer_data.get("login", "No Name")
            self._followers = viewer_data.get("followers", {}).get("totalCount", 0)
            self._following = viewer_data.get("following", {}).get("totalCount", 0)

            contrib_repos = viewer_data.get("repositoriesContributedTo", {})
            owned_repos = viewer_data.get("repositories", {})

            repos = owned_repos.get("nodes", [])
            if not self._env.filter.exclude_contrib_repos:
                repos += contrib_repos.get("nodes", [])

            for repo in repos:
                if not repo or self.is_repo_type_excluded(repo):
                    continue

                full_name = repo.get("nameWithOwner")
                if self.is_repo_name_invalid(full_name):
                    continue

                self._repos.add(full_name)
                self._repo_visibility[full_name] = bool(
                    repo.get("isPrivate") or repo.get("private")
                )
                self._stargazers += repo.get("stargazers", {}).get("totalCount", 0)
                self._forks += repo.get("forkCount", 0)

                if repo.get("isEmpty"):
                    self._empty_repos.add(full_name)
                    continue

                self._process_languages(repo)

            owned_page_info = owned_repos.get("pageInfo", {})
            contrib_page_info = contrib_repos.get("pageInfo", {})

            if owned_page_info.get("hasNextPage") or contrib_page_info.get(
                "hasNextPage"
            ):
                next_owned = owned_page_info.get("endCursor", next_owned)
                next_contrib = contrib_page_info.get("endCursor", next_contrib)
            else:
                break

        if not self._env.filter.exclude_contrib_repos:
            await self._process_manually_added_repos()

        self._calculate_language_proportions()

    def _process_languages(self, repo_data: Dict[str, Any]) -> None:
        """
        Extract and aggregate language data from a single repository's metadata.

        :param repo_data: Dictionary containing repository metadata.
        """
        repo_name = repo_data.get("nameWithOwner", "unknown")
        for edge in repo_data.get("languages", {}).get("edges", []):
            lang_name = edge.get("node", {}).get("name", "Other")
            if lang_name in self._env.filter.exclude_langs:
                continue

            size = edge.get("size", 0)
            color = edge.get("node", {}).get("color")
            logger.debug("  %s: %s (%d bytes)", repo_name, lang_name, size)

            if lang_name in self._languages:
                self._languages[lang_name]["size"] += size
                self._languages[lang_name]["occurrences"] += 1
            else:
                self._languages[lang_name] = {
                    "size": size,
                    "occurrences": 1,
                    "color": color,
                }

    async def _process_manually_added_repos(self) -> None:
        """Fetch and aggregate statistics for manually specified repositories."""
        env_repos = self._env.filter.manually_added_repos
        lang_cols = self._queries.get_language_colors()

        for repo in env_repos:
            if self.is_repo_name_invalid(repo):
                continue

            repo_stats = await self._queries.query_rest(f"/repos/{repo}")
            if self.is_repo_type_excluded(repo_stats):
                continue

            self._repos.add(repo)
            self._repo_visibility[repo] = bool(repo_stats.get("private"))
            self._stargazers += repo_stats.get("stargazers_count", 0)
            self._forks += repo_stats.get("forks_count", 0)

            if repo_stats.get("size") == 0:
                self._empty_repos.add(repo)
                continue

            if repo_stats.get("language"):
                langs = await self._queries.query_rest(f"/repos/{repo}/languages")
                for lang, size in langs.items():
                    if lang in self._env.filter.exclude_langs:
                        continue

                    if lang in self._languages:
                        self._languages[lang]["size"] += size
                        self._languages[lang]["occurrences"] += 1
                    else:
                        color_data = lang_cols.get(lang)
                        self._languages[lang] = {
                            "size": size,
                            "occurrences": 1,
                            "color": color_data.get("color") if color_data else None,
                        }

    def _calculate_language_proportions(self) -> None:
        """Calculate the percentage of usage for each programming language."""
        langs_total = sum(v.get("size", 0) for v in self._languages.values())
        if langs_total > 0:
            for v in self._languages.values():
                v["prop"] = 100 * (v.get("size", 0) / langs_total)
        else:
            for v in self._languages.values():
                v["prop"] = 0.0
