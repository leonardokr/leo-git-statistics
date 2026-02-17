"""Pydantic response models for API endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    """Response model for user overview statistics."""

    username: str
    name: Optional[str] = None
    total_contributions: Optional[int] = None
    repositories_count: Optional[int] = None
    total_stars: Optional[int] = None
    total_forks: Optional[int] = None
    total_views: Optional[int] = None
    views_from_date: Optional[str] = None
    total_clones: Optional[int] = None
    clones_from_date: Optional[str] = None
    total_pull_requests: Optional[int] = None
    total_issues: Optional[int] = None
    lines_added: Optional[int] = None
    lines_deleted: Optional[int] = None
    avg_contribution_percent: Optional[str] = None
    collaborators_count: Optional[int] = None
    contributors_count: Optional[int] = None
    warnings: Optional[List[str]] = None


class LanguagesResponse(BaseModel):
    """Response model for language distribution statistics."""

    username: str
    languages: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None


class StreakResponse(BaseModel):
    """Response model for contribution streak statistics."""

    username: str
    current_streak: Optional[int] = None
    current_streak_range: Optional[str] = None
    longest_streak: Optional[int] = None
    longest_streak_range: Optional[str] = None
    total_contributions: Optional[int] = None
    warnings: Optional[List[str]] = None


class RecentContributionsResponse(BaseModel):
    """Response model for recent contribution counts."""

    username: str
    recent_contributions: Optional[List[int]] = None
    warnings: Optional[List[str]] = None


class WeeklyCommitsResponse(BaseModel):
    """Response model for weekly commit schedule."""

    username: str
    weekly_commits: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None


class RepositoriesResponse(BaseModel):
    """Response model for repository listing."""

    username: str
    repositories_count: Optional[int] = None
    repositories: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class DetailedRepoItem(BaseModel):
    """Response model for a single detailed repository entry."""

    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = ""
    html_url: Optional[str] = None
    homepage: Optional[str] = ""
    language: Optional[str] = None
    languages: Dict[str, Any] = {}
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    watchers_count: int = 0
    topics: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    is_fork: bool = False
    is_archived: bool = False
    is_private: bool = False


class DetailedRepositoriesResponse(BaseModel):
    """Response model for detailed repository listing."""

    username: str
    repositories_count: int
    repositories: List[DetailedRepoItem]
    warnings: Optional[List[str]] = None


class FullStatsResponse(BaseModel):
    """Response model for full statistics."""

    username: str
    overview: Optional[Dict[str, Any]] = None
    languages: Optional[Dict[str, Any]] = None
    streak: Optional[Dict[str, Any]] = None
    contributions: Optional[Dict[str, Any]] = None
    repositories: Optional[Dict[str, Any]] = None
    weekly_commits: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None


class GitHubApiHealth(BaseModel):
    """Health status of the GitHub API connection."""

    status: str
    rate_limit_remaining: Optional[int] = None
    rate_limit_limit: Optional[int] = None
    rate_limit_reset: Optional[str] = None


class CacheHealth(BaseModel):
    """Health status of the cache subsystem."""

    entries: int = 0
    maxsize: int = 0
    hit_ratio: float = 0.0


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str
    uptime_seconds: float
    github_api: GitHubApiHealth
    cache: CacheHealth
    circuit_breaker: str


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedRepositoriesResponse(BaseModel):
    """Response model for paginated repository listing."""

    username: str
    data: List[str]
    pagination: PaginationMeta
    warnings: Optional[List[str]] = None


class PaginatedDetailedRepositoriesResponse(BaseModel):
    """Response model for paginated detailed repository listing."""

    username: str
    data: List[DetailedRepoItem]
    pagination: PaginationMeta
    warnings: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error: str
    message: Optional[str] = None
