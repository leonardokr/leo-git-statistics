"""API key authentication dependency."""

import os
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer_scheme = HTTPBearer(auto_error=False)

_cached_keys: Optional[set] = None


def _get_api_keys() -> set:
    """Load valid API keys from the ``API_KEYS`` environment variable.

    :returns: Set of valid API key strings.
    :rtype: set
    """
    global _cached_keys
    if _cached_keys is None:
        raw = os.getenv("API_KEYS", "")
        _cached_keys = {k.strip() for k in raw.split(",") if k.strip()}
    return _cached_keys


def _auth_required() -> bool:
    """Check whether API authentication is enabled.

    :returns: True when ``API_AUTH_ENABLED`` is ``"true"``.
    :rtype: bool
    """
    return os.getenv("API_AUTH_ENABLED", "false").lower() == "true"


async def verify_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Optional[str]:
    """FastAPI dependency that validates the ``Authorization: Bearer <key>`` header.

    When authentication is disabled (default), all requests pass through and
    ``None`` is returned.  When enabled, a valid API key must be present or
    a 401 response is returned.

    :param request: The incoming request.
    :param credentials: Parsed bearer token from the Authorization header.
    :returns: The validated API key, or None when auth is disabled.
    :rtype: str | None
    :raises HTTPException: 401 when auth is enabled and no valid key is provided.
    """
    if not _auth_required():
        if credentials:
            keys = _get_api_keys()
            if keys and credentials.credentials in keys:
                request.state.authenticated = True
                return credentials.credentials
        request.state.authenticated = False
        return None

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing API key")

    keys = _get_api_keys()
    if not keys:
        raise HTTPException(status_code=500, detail="No API keys configured on server")

    if credentials.credentials not in keys:
        raise HTTPException(status_code=401, detail="Invalid API key")

    request.state.authenticated = True
    return credentials.credentials
