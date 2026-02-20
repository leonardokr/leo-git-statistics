"""Token scope resolution for controlling private repository visibility."""

from src.core.repository_filter import RepositoryFilter


def resolve_repo_filter(*, user_owns_token: bool) -> RepositoryFilter:
    """Build a RepositoryFilter with private repo access based on token ownership.

    When the caller provides their own GitHub token (validated to match the
    requested username), private repositories are visible.  Otherwise, the
    server token operates in restricted mode and private repos are excluded
    regardless of the ``EXCLUDE_PRIVATE_REPOS`` environment variable.

    Private repositories are allowed only when a caller provides a validated
    `X-GitHub-Token` that belongs to the requested username. Server token
    requests are always restricted to public repositories.

    :param user_owns_token: True when the request carries a validated user token.
    :returns: A configured RepositoryFilter instance.
    :rtype: RepositoryFilter
    """
    if user_owns_token:
        return RepositoryFilter()

    return RepositoryFilter(exclude_private_repos=True)
