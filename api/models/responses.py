"""Pydantic response models for API endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    """Response model for user overview statistics."""

    username: str
    name: str
    total_contributions: int
    repositories_count: int
    total_stars: int
    total_forks: int
    total_views: int
    views_from_date: str
    total_clones: int
    clones_from_date: str
    total_pull_requests: int
    total_issues: int
    lines_added: int
    lines_deleted: int
    avg_contribution_percent: str
    collaborators_count: int
    contributors_count: int


class LanguagesResponse(BaseModel):
    """Response model for language distribution statistics."""

    username: str
    languages: Dict[str, Any]


class StreakResponse(BaseModel):
    """Response model for contribution streak statistics."""

    username: str
    current_streak: int
    current_streak_range: str
    longest_streak: int
    longest_streak_range: str
    total_contributions: int


class RecentContributionsResponse(BaseModel):
    """Response model for recent contribution counts."""

    username: str
    recent_contributions: List[int]


class WeeklyCommitsResponse(BaseModel):
    """Response model for weekly commit schedule."""

    username: str
    weekly_commits: List[Dict[str, Any]]


class RepositoriesResponse(BaseModel):
    """Response model for repository listing."""

    username: str
    repositories_count: int
    repositories: List[str]


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


class FullStatsResponse(BaseModel):
    """Response model for full statistics."""

    username: str
    overview: Dict[str, Any]
    languages: Dict[str, Any]
    streak: Dict[str, Any]
    contributions: Dict[str, Any]
    repositories: Dict[str, Any]
    weekly_commits: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    message: str


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error: str
    message: Optional[str] = None
