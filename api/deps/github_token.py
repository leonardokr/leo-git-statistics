"""User GitHub token resolution and validation."""

import logging
from typing import Optional

import aiohttp
from fastapi import Depends, Header, HTTPException, Request

from api.deps.http_session import get_shared_session
from api.deps.token_scope import resolve_repo_filter
from api.services.stats_service import get_github_token
from src.core.repository_filter import RepositoryFilter

logger = logging.getLogger(__name__)


class ResolvedToken:
    """Holds the resolved GitHub token and associated repository filter.

    :param token: The GitHub personal access token to use for API calls.
    :param repo_filter: RepositoryFilter configured for the resolved scope.
    :param user_owns_token: True when the token belongs to the requested user.
    """

    __slots__ = ("token", "repo_filter", "user_owns_token")

    def __init__(self, token: str, repo_filter: RepositoryFilter, user_owns_token: bool):
        self.token = token
        self.repo_filter = repo_filter
        self.user_owns_token = user_owns_token


async def _validate_user_token(token: str, username: str, session: aiohttp.ClientSession) -> bool:
    """Verify that a GitHub token belongs to the specified user.

    :param token: The user-supplied GitHub token.
    :param username: The username from the request path.
    :param session: Shared aiohttp session.
    :returns: True if the token's owner matches the username.
    :rtype: bool
    """
    try:
        async with session.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}"},
        ) as resp:
            if resp.status != 200:
                return False
            data = await resp.json()
            return data.get("login", "").lower() == username.lower()
    except aiohttp.ClientError:
        return False


async def resolve_github_token(
    request: Request,
    username: str,
    x_github_token: Optional[str] = Header(None),
    session: aiohttp.ClientSession = Depends(get_shared_session),
) -> ResolvedToken:
    """Resolve the GitHub token to use for a request.

    When ``X-GitHub-Token`` is provided, it is validated against the
    ``username`` path parameter.  If valid, the user's token is used and
    private repositories are visible.  Otherwise a 403 is returned.

    When no user token is provided, the server's ``GITHUB_TOKEN`` is used
    in restricted mode (private repositories excluded).

    :param request: The incoming request.
    :param username: GitHub username from the URL path.
    :param x_github_token: Optional user-supplied GitHub token header.
    :param session: Shared aiohttp session for validation calls.
    :returns: A ResolvedToken with the token and scope configuration.
    :rtype: ResolvedToken
    :raises HTTPException: 403 when the user token does not match the username.
    """
    if x_github_token:
        valid = await _validate_user_token(x_github_token, username, session)
        if not valid:
            raise HTTPException(
                status_code=403,
                detail="X-GitHub-Token does not belong to the requested user",
            )
        repo_filter = resolve_repo_filter(user_owns_token=True)
        return ResolvedToken(
            token=x_github_token,
            repo_filter=repo_filter,
            user_owns_token=True,
        )

    server_token = get_github_token()
    repo_filter = resolve_repo_filter(user_owns_token=False)
    return ResolvedToken(
        token=server_token,
        repo_filter=repo_filter,
        user_owns_token=False,
    )
