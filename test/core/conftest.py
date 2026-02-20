"""Shared fixtures for collector tests."""

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("ACCESS_TOKEN", "test-token")


@pytest.fixture()
def mock_github_client():
    """Return a mocked GitHubClient with query and query_rest stubs."""
    client = AsyncMock()
    client.username = "testuser"
    client.access_token = "test-token"
    client.get_language_colors = MagicMock(return_value={})
    return client


@pytest.fixture()
def mock_environment():
    """Return a minimal mocked Environment."""
    from src.core.repository_filter import RepositoryFilter
    env = MagicMock()
    env.username = "testuser"
    env.access_token = "test-token"
    env.timezone = "UTC"
    env.more_collabs = 0
    env.filter = RepositoryFilter()
    env.traffic = MagicMock()
    env.traffic.repo_views = 0
    env.traffic.repo_clones = 0
    env.traffic.repo_last_viewed = "0000-00-00"
    env.traffic.repo_last_cloned = "0000-00-00"
    env.traffic.repo_first_viewed = "0000-00-00"
    env.traffic.repo_first_cloned = "0000-00-00"
    env.traffic.store_repo_view_count = False
    env.traffic.store_repo_clone_count = False
    return env
