"""Async tests for RepoStatsCollector."""

import pytest
from unittest.mock import AsyncMock

from src.core.repo_stats_collector import RepoStatsCollector


class TestRepoStatsCollector:
    """Tests for repository statistics collection."""

    def _graphql_response(self, repos, has_next=False, cursor="cursor1"):
        """Build a minimal GraphQL repos_overview response."""
        nodes = []
        for name, stars, forks, lang_size in repos:
            nodes.append({
                "nameWithOwner": name,
                "stargazers": {"totalCount": stars},
                "forkCount": forks,
                "isFork": False,
                "isArchived": False,
                "isPrivate": False,
                "isEmpty": False,
                "languages": {
                    "edges": [
                        {"node": {"name": "Python", "color": "#3572A5"}, "size": lang_size},
                    ],
                },
            })
        return {
            "data": {
                "viewer": {
                    "name": "Test User",
                    "login": "testuser",
                    "repositories": {
                        "nodes": nodes,
                        "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
                    },
                    "repositoriesContributedTo": {
                        "nodes": [],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    },
                },
            },
        }

    async def test_collect_aggregates_repos(self, mock_environment, mock_github_client):
        """Repos, stars, forks and languages are aggregated correctly."""
        mock_github_client.query.return_value = self._graphql_response([
            ("user/repo-a", 10, 2, 5000),
            ("user/repo-b", 5, 1, 3000),
        ])
        collector = RepoStatsCollector(mock_environment, mock_github_client)
        await collector.collect()

        assert collector.repos == {"user/repo-a", "user/repo-b"}
        assert collector.stargazers == 15
        assert collector.forks == 3
        assert "Python" in collector.languages
        assert collector.languages["Python"]["size"] == 8000

    async def test_collect_paginates(self, mock_environment, mock_github_client):
        """Multiple GraphQL pages are fetched until hasNextPage is False."""
        page1 = self._graphql_response([("user/repo-a", 10, 1, 1000)], has_next=True)
        page2 = self._graphql_response([("user/repo-b", 5, 0, 2000)], has_next=False)
        mock_github_client.query.side_effect = [page1, page2]

        collector = RepoStatsCollector(mock_environment, mock_github_client)
        await collector.collect()

        assert len(collector.repos) == 2
        assert mock_github_client.query.call_count == 2

    async def test_excludes_forked_repos(self, mock_environment, mock_github_client):
        """Forked repos are excluded when include_forked_repos is False."""
        mock_environment.filter.include_forked_repos = False
        resp = self._graphql_response([("user/repo-a", 10, 1, 1000)])
        resp["data"]["viewer"]["repositories"]["nodes"][0]["isFork"] = True
        mock_github_client.query.return_value = resp

        collector = RepoStatsCollector(mock_environment, mock_github_client)
        await collector.collect()

        assert len(collector.repos) == 0

    async def test_empty_repos_tracked(self, mock_environment, mock_github_client):
        """Empty repos are added to the empty_repos set."""
        resp = self._graphql_response([("user/empty", 0, 0, 0)])
        resp["data"]["viewer"]["repositories"]["nodes"][0]["isEmpty"] = True
        mock_github_client.query.return_value = resp

        collector = RepoStatsCollector(mock_environment, mock_github_client)
        await collector.collect()

        assert "user/empty" in collector.empty_repos

    async def test_language_proportions(self, mock_environment, mock_github_client):
        """Language proportions are calculated as percentages."""
        mock_github_client.query.return_value = self._graphql_response([
            ("user/repo-a", 0, 0, 8000),
            ("user/repo-b", 0, 0, 2000),
        ])
        collector = RepoStatsCollector(mock_environment, mock_github_client)
        await collector.collect()

        assert collector.languages["Python"]["prop"] == pytest.approx(100.0, rel=0.01)

    async def test_empty_response(self, mock_environment, mock_github_client):
        """Handles empty GraphQL response gracefully."""
        mock_github_client.query.return_value = {}
        collector = RepoStatsCollector(mock_environment, mock_github_client)
        await collector.collect()

        assert collector.repos == set()
        assert collector.stargazers == 0

    async def test_exclude_contrib_repos_skips_non_owned_from_repositories(
        self, mock_environment, mock_github_client
    ):
        """When exclude_contrib_repos is true, keep only owner repos."""
        mock_environment.username = "leonardokr"
        mock_environment.filter.exclude_contrib_repos = True
        mock_github_client.query.return_value = self._graphql_response([
            ("leonardokr/owned-repo", 10, 1, 1000),
            ("tiga-alves/contrib-repo", 5, 1, 1000),
        ])

        collector = RepoStatsCollector(mock_environment, mock_github_client)
        await collector.collect()

        assert collector.repos == {"leonardokr/owned-repo"}
