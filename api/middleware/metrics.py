"""Prometheus metrics middleware and custom metric definitions."""

from prometheus_client import Counter, Gauge, Histogram

from api.deps.cache import cache_stats
from src.core.github_client import github_breaker, rate_limit_state

github_api_calls = Counter(
    "github_api_calls_total",
    "Total GitHub API calls",
    ["method", "status"],
)

github_api_duration = Histogram(
    "github_api_duration_seconds",
    "GitHub API call latency in seconds",
    ["method"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

cache_hits = Counter("cache_hits_total", "Total cache hits")
cache_misses = Counter("cache_misses_total", "Total cache misses")

github_rate_limit_remaining = Gauge(
    "github_rate_limit_remaining",
    "GitHub API rate limit remaining requests",
)

circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=half-open, 2=open)",
)


def update_infrastructure_gauges() -> None:
    """Refresh Prometheus gauges from current infrastructure state."""
    if rate_limit_state.remaining is not None:
        github_rate_limit_remaining.set(rate_limit_state.remaining)

    state_map = {"closed": 0, "half-open": 1, "open": 2}
    circuit_breaker_state.set(state_map.get(github_breaker.current_state, -1))
