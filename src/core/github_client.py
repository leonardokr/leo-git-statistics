"""GitHub API Client Module.

This module provides an async-first client for interacting with GitHub's
GraphQL (v4) and REST (v3) APIs with retry, circuit breaker, and rate
limit monitoring.
"""

import logging
import time
from asyncio import Semaphore, sleep
from typing import Dict, List, Optional, Union

import aiohttp
import pybreaker
import structlog
from json import loads, JSONDecodeError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)
slog = structlog.get_logger("github.client")


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors.

    :param message: Error description.
    :param status_code: HTTP status code if available.
    """

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded.

    :param message: Error description.
    :param retry_after: Seconds to wait before retrying.
    """

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status_code=403)
        self.retry_after = retry_after


class RateLimitState:
    """Tracks GitHub API rate limit state from response headers.

    :ivar remaining: Number of requests remaining in the current window.
    :ivar limit: Total requests allowed in the current window.
    :ivar reset: Unix timestamp when the rate limit resets.
    """

    def __init__(self):
        self.remaining: Optional[int] = None
        self.limit: Optional[int] = None
        self.reset: Optional[int] = None

    def update_from_headers(self, headers) -> None:
        """Parse rate limit information from GitHub response headers.

        :param headers: Response headers from a GitHub API call.
        """
        raw_remaining = headers.get("X-RateLimit-Remaining")
        raw_limit = headers.get("X-RateLimit-Limit")
        raw_reset = headers.get("X-RateLimit-Reset")

        if raw_remaining is not None:
            self.remaining = int(raw_remaining)
        if raw_limit is not None:
            self.limit = int(raw_limit)
        if raw_reset is not None:
            self.reset = int(raw_reset)

        if self.remaining is not None and self.remaining < 100:
            logger.warning(
                "GitHub rate limit low: %d/%s remaining (resets at %s)",
                self.remaining,
                self.limit,
                self.reset,
            )

    async def wait_if_critical(self) -> None:
        """Pause execution if rate limit is critically low (<10 remaining)."""
        if self.remaining is not None and self.remaining < 10 and self.reset is not None:
            wait_time = self.reset - int(time.time())
            if wait_time > 0:
                capped = min(wait_time, 60)
                logger.warning(
                    "Rate limit critical (%d remaining). Waiting %ds for reset.",
                    self.remaining,
                    capped,
                )
                await sleep(capped)


rate_limit_state = RateLimitState()

github_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    name="GitHubAPI",
    exclude=[
        lambda e: isinstance(e, GitHubAPIError)
        and e.status_code is not None
        and e.status_code < 500
        and not isinstance(e, RateLimitError),
    ],
)


def _is_retryable(exception: BaseException) -> bool:
    """Determine whether an exception should trigger a retry.

    :param exception: The exception to evaluate.
    :returns: True if the request should be retried.
    """
    if isinstance(exception, RateLimitError):
        return True
    if isinstance(exception, (aiohttp.ClientError, aiohttp.ServerTimeoutError)):
        return True
    if isinstance(exception, GitHubAPIError) and exception.status_code and exception.status_code >= 500:
        return True
    return False


def _rate_limit_aware_wait(retry_state) -> float:
    """Wait strategy that respects GitHub Retry-After header.

    :param retry_state: Tenacity retry state.
    :returns: Number of seconds to wait.
    """
    exc = retry_state.outcome.exception()
    if isinstance(exc, RateLimitError) and exc.retry_after:
        return min(exc.retry_after, 60)
    return wait_exponential(multiplier=1, min=1, max=10)(retry_state)


class GitHubClient:
    """Client for interacting with GitHub's GraphQL (v4) and REST (v3) APIs.

    Provides methods to perform asynchronous queries with automatic retry,
    circuit breaker protection, and rate limit monitoring.
    """

    __GITHUB_API_URL = "https://api.github.com/"
    __GRAPHQL_PATH = "graphql"
    __REST_202_RETRY_LIMIT = 60
    __ASYNCIO_SLEEP_TIME = 2
    __DEFAULT_MAX_CONNECTIONS = 10

    def __init__(
        self,
        username: str,
        access_token: str,
        session: aiohttp.ClientSession,
        max_connections: int = __DEFAULT_MAX_CONNECTIONS,
    ):
        """Initialize the GitHubClient.

        :param username: GitHub username.
        :param access_token: GitHub personal access token.
        :param session: aiohttp ClientSession for making requests.
        :param max_connections: Maximum number of concurrent connections.
        """
        if not username or not username.strip():
            raise ValueError("GitHub username must not be empty")
        if not access_token or not access_token.strip():
            raise ValueError("GitHub access token must not be empty")

        self.username = username
        self.access_token = access_token
        self.session = session
        self.semaphore = Semaphore(max_connections)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=_rate_limit_aware_wait,
        retry=retry_if_exception(_is_retryable),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """Execute an HTTP request with retry and rate limit awareness.

        :param method: HTTP method (GET, POST, etc.).
        :param url: Full URL to request.
        :param kwargs: Additional arguments passed to aiohttp.
        :returns: The aiohttp response object.
        :raises RateLimitError: When GitHub rate limit is exceeded.
        :raises GitHubAPIError: When the server returns a 5xx error.
        :raises aiohttp.ClientError: On network-level failures.
        """
        await rate_limit_state.wait_if_critical()

        start = time.perf_counter()
        async with self.semaphore:
            resp = await self.session.request(method, url, headers=self.headers, **kwargs)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        rate_limit_state.update_from_headers(resp.headers)

        slog.info(
            "github_api_call",
            method=method,
            url=url,
            status=resp.status,
            duration_ms=duration_ms,
            rate_limit_remaining=rate_limit_state.remaining,
        )

        try:
            from api.middleware.metrics import github_api_calls, github_api_duration
            github_api_calls.labels(method=method, status=str(resp.status)).inc()
            github_api_duration.labels(method=method).observe(duration_ms / 1000)
        except Exception:
            pass

        if resp.status == 403:
            body = await resp.json()
            message = str(body.get("message", ""))
            if "rate limit" in message.lower():
                retry_after_raw = resp.headers.get("Retry-After")
                retry_after = int(retry_after_raw) if retry_after_raw else None
                raise RateLimitError("GitHub rate limit exceeded", retry_after=retry_after)

        if resp.status >= 500:
            raise GitHubAPIError(f"GitHub server error: {resp.status}", status_code=resp.status)

        return resp

    async def query(self, generated_query: str) -> Dict:
        """Make a request to the GitHub GraphQL API.

        :param generated_query: The GraphQL query string to be sent.
        :returns: Decoded GraphQL JSON response as a dictionary.
        """
        try:
            resp = await github_breaker.call_async(
                self._request,
                "POST",
                self.__GITHUB_API_URL + self.__GRAPHQL_PATH,
                json={"query": generated_query},
            )
            result = await resp.json()
            if result is not None:
                return result
        except pybreaker.CircuitBreakerError:
            logger.error("Circuit breaker open - GitHub API temporarily unavailable")
        except (aiohttp.ClientError, aiohttp.ServerTimeoutError, JSONDecodeError) as e:
            logger.error("GraphQL query failed after retries: %s", e)
        except GitHubAPIError as e:
            logger.error("GraphQL query returned error: %s (status %s)", e.message, e.status_code)

        return dict()

    async def query_rest(
        self,
        path: str,
        params: Optional[Dict] = None,
    ) -> Union[Dict, List]:
        """Make a request to the GitHub REST API.

        :param path: The API path to query (e.g., 'repos/owner/repo').
        :param params: Optional dictionary of query parameters.
        :returns: Deserialized REST JSON response as a dictionary or list.
        """
        if params is None:
            params = dict()
        if path.startswith("/"):
            path = path[1:]

        for i in range(self.__REST_202_RETRY_LIMIT):
            try:
                resp = await github_breaker.call_async(
                    self._request,
                    "GET",
                    self.__GITHUB_API_URL + path,
                    params=tuple(params.items()),
                )

                if resp.status == 202:
                    logger.debug("Path %s returned 202. Retrying attempt %d...", path, i + 1)
                    await sleep(self.__ASYNCIO_SLEEP_TIME)
                    continue

                result = await resp.json()
                if result is not None:
                    return result
            except pybreaker.CircuitBreakerError:
                logger.error("Circuit breaker open - GitHub API temporarily unavailable")
                return dict()
            except (aiohttp.ClientError, aiohttp.ServerTimeoutError, JSONDecodeError) as e:
                logger.error("REST query failed for %s after retries: %s", path, e)
                return dict()
            except GitHubAPIError as e:
                logger.error("REST query %s returned error: %s (status %s)", path, e.message, e.status_code)
                return dict()

        logger.warning("Too many 202s for path %s. Data will be incomplete.", path)
        return dict()

    @staticmethod
    def get_language_colors() -> Dict:
        """Retrieve a mapping of programming languages to their respective colors.

        :returns: Dictionary mapping language names to hex color codes.
        """
        import requests

        try:
            response = requests.get(
                "https://raw.githubusercontent.com/ozh/github-colors/master/colors.json"
            )
            response.raise_for_status()
            return loads(response.text)
        except Exception as e:
            logger.error("Failed to fetch language colors: %s", e)
            return dict()
