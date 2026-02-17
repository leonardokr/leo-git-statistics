"""Locust load testing scenarios for the Git Statistics API.

Run with::

    locust -f test/load/locustfile.py --host http://localhost:8000

Scenarios
---------
- **CacheUser**: 10 concurrent users hitting /overview for the same username
  to validate cache effectiveness.
- **MixedUser**: 50 concurrent users accessing different endpoints to test
  overall concurrency and latency.
- **BurstUser**: Short burst of 100 requests in ~10 seconds targeting various
  endpoints to validate rate limiting.
"""

from locust import HttpUser, between, tag, task


class CacheUser(HttpUser):
    """Simulates multiple clients requesting the same user overview.

    All requests target the same username so the cache (task 1.2) should
    serve most of them as HITs after the first MISS.
    """

    wait_time = between(0.5, 1.5)
    weight = 2

    @tag("cache")
    @task
    def get_overview(self):
        """Request the overview endpoint for a fixed user."""
        self.client.get("/users/testuser/overview")


class MixedUser(HttpUser):
    """Simulates realistic traffic across different endpoints."""

    wait_time = between(1, 3)
    weight = 5

    @tag("mixed")
    @task(5)
    def get_overview(self):
        """Most common request: user overview."""
        self.client.get("/users/testuser/overview")

    @tag("mixed")
    @task(3)
    def get_languages(self):
        """Language distribution endpoint."""
        self.client.get("/users/testuser/languages")

    @tag("mixed")
    @task(3)
    def get_streak(self):
        """Streak information endpoint."""
        self.client.get("/users/testuser/streak")

    @tag("mixed")
    @task(2)
    def get_recent_contributions(self):
        """Recent contributions endpoint."""
        self.client.get("/users/testuser/contributions/recent")

    @tag("mixed")
    @task(2)
    def get_weekly_commits(self):
        """Weekly commit schedule endpoint."""
        self.client.get("/users/testuser/commits/weekly")

    @tag("mixed")
    @task(2)
    def get_repositories(self):
        """Paginated repository listing."""
        self.client.get("/users/testuser/repositories?page=1&per_page=10")

    @tag("mixed")
    @task(1)
    def get_full_stats(self):
        """Heavy full-stats endpoint (less frequent)."""
        self.client.get("/users/testuser/stats/full")

    @tag("mixed")
    @task(1)
    def get_health(self):
        """Health check (should always be fast)."""
        self.client.get("/health")


class BurstUser(HttpUser):
    """Simulates a burst of rapid requests to test rate limiting.

    Short wait time means many requests in a small window. Expect 429
    responses when rate limiting is active.
    """

    wait_time = between(0.05, 0.2)
    weight = 1

    @tag("burst")
    @task(3)
    def burst_overview(self):
        """Rapid overview requests."""
        with self.client.get("/users/testuser/overview", catch_response=True) as resp:
            if resp.status_code == 429:
                resp.success()

    @tag("burst")
    @task(2)
    def burst_languages(self):
        """Rapid language requests."""
        with self.client.get("/users/testuser/languages", catch_response=True) as resp:
            if resp.status_code == 429:
                resp.success()

    @tag("burst")
    @task(1)
    def burst_full_stats(self):
        """Rapid full-stats requests (most likely to trigger rate limit)."""
        with self.client.get("/users/testuser/stats/full", catch_response=True) as resp:
            if resp.status_code == 429:
                resp.success()
