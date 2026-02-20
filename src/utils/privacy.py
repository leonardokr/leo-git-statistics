"""Helpers to mask private repository data in outputs."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


def should_mask_private(mask_flag: Any) -> bool:
    """Normalize truthy values used by env/config toggles."""
    if isinstance(mask_flag, bool):
        return mask_flag
    if mask_flag is None:
        return False
    return str(mask_flag).strip().lower() in {"1", "true", "yes", "on"}


def masked_repo_name(username: str) -> str:
    """Build canonical masked repository name."""
    return f"{username}/private-repo"


def mask_repo_names(
    repos: Iterable[str],
    repo_visibility: Mapping[str, bool],
    username: str,
    *,
    mask_enabled: bool,
) -> List[str]:
    """Mask private repository names while keeping public names unchanged."""
    names: List[str] = []
    for repo in repos:
        is_private = bool(repo_visibility.get(repo, False))
        if mask_enabled and is_private:
            names.append(masked_repo_name(username))
        else:
            names.append(repo)
    return names


def mask_weekly_commits(
    commits: Iterable[Dict[str, Any]],
    username: str,
    *,
    mask_enabled: bool,
) -> List[Dict[str, Any]]:
    """Mask sensitive commit details for private repositories."""
    if not mask_enabled:
        return list(commits)

    safe: List[Dict[str, Any]] = []
    private_repo = masked_repo_name(username)
    for commit in commits:
        item = dict(commit)
        if item.get("is_private"):
            item["repo"] = private_repo
            item["sha"] = "private"
            item["description"] = "Private commit"
        safe.append(item)
    return safe


def mask_detailed_repo(repo_data: Dict[str, Any], username: str, *, mask_enabled: bool) -> Dict[str, Any]:
    """Mask a detailed repository payload when it is private."""
    if not mask_enabled or not repo_data.get("is_private", False):
        return repo_data

    item = dict(repo_data)
    masked_full = masked_repo_name(username)
    masked_name = masked_full.split("/", 1)[1]
    item["name"] = masked_name
    item["full_name"] = masked_full
    item["description"] = ""
    item["html_url"] = None
    item["homepage"] = ""
    item["language"] = None
    item["languages"] = {}
    item["topics"] = []
    return item
