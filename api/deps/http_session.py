"""Shared aiohttp.ClientSession with connection pooling."""

from typing import Optional

import aiohttp


_shared_session: Optional[aiohttp.ClientSession] = None


async def create_shared_session() -> None:
    """Create the shared aiohttp.ClientSession on application startup."""
    global _shared_session
    connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300)
    _shared_session = aiohttp.ClientSession(connector=connector)


async def close_shared_session() -> None:
    """Close the shared aiohttp.ClientSession on application shutdown."""
    global _shared_session
    if _shared_session and not _shared_session.closed:
        await _shared_session.close()
    _shared_session = None


def get_shared_session() -> aiohttp.ClientSession:
    """Return the shared aiohttp.ClientSession.

    :returns: The shared ClientSession bound to the running event loop.
    :rtype: aiohttp.ClientSession
    :raises RuntimeError: If called before startup.
    """
    if _shared_session is None or _shared_session.closed:
        raise RuntimeError("Shared aiohttp session is not available")
    return _shared_session
