"""Pydantic request models for input validation and sanitization."""

import re
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

GITHUB_USERNAME_PATTERN = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$"
)


def validated_username(
    username: str = Path(..., min_length=1, max_length=39),
) -> str:
    """Validate a GitHub username against GitHub's naming rules.

    :param username: The username path parameter.
    :returns: The validated username.
    :rtype: str
    :raises HTTPException: 422 when the username format is invalid.
    """
    if not GITHUB_USERNAME_PATTERN.match(username):
        raise HTTPException(
            status_code=422,
            detail="Invalid GitHub username format",
        )
    return username


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=30, ge=1, le=100)


class RepoQueryParams(BaseModel):
    """Query parameters for the detailed repositories endpoint."""

    visibility: Literal["public", "private", "all"] = "public"
    sort: Literal["stars", "forks", "updated", "name"] = "updated"
    limit: int = Field(default=100, ge=1, le=500)
    exclude_forks: bool = True
    exclude_archived: bool = True
