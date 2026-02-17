"""Centralized data assembly functions for stats payloads.

Provides shared assembly logic used by the static API generator,
the REST API endpoints and the snapshot system, eliminating
data-assembly duplication across entry points.
"""

from typing import Any, Dict, Optional, Set, Tuple


async def build_overview_payload(
    collector,
    username: str,
    *,
    partial_collector=None,
) -> Dict[str, Any]:
    """Build the overview stats dict used by static JSON and API.

    :param collector: Stats collector instance.
    :param username: GitHub username.
    :param partial_collector: Optional :class:`PartialCollector` for
        fault-tolerant collection.  When ``None``, exceptions propagate.
    :returns: Overview statistics dictionary.
    :rtype: dict
    """
    pc = partial_collector

    if pc is not None:
        name = await pc.safe(collector.get_name(), None, "name")
        total_contributions = await pc.safe(collector.get_total_contributions(), None, "total contributions")
        repos = await pc.safe(collector.get_repos(), set(), "repositories")
        stars = await pc.safe(collector.get_stargazers(), None, "stargazers")
        forks = await pc.safe(collector.get_forks(), None, "forks")
        followers = await pc.safe(collector.get_followers(), None, "followers")
        following = await pc.safe(collector.get_following(), None, "following")
        views = await pc.safe(collector.get_views(), None, "views")
        views_from = await pc.safe(collector.get_views_from_date(), None, "views from date")
        clones = await pc.safe(collector.get_clones(), None, "clones")
        clones_from = await pc.safe(collector.get_clones_from_date(), None, "clones from date")
        pull_requests = await pc.safe(collector.get_pull_requests(), None, "pull requests")
        issues = await pc.safe(collector.get_issues(), None, "issues")
        lines = await pc.safe(collector.get_lines_changed(), (None, None), "lines changed")
        avg_percent = await pc.safe(collector.get_avg_contribution_percent(), None, "avg contribution percent")
        collaborators = await pc.safe(collector.get_collaborators(), None, "collaborators")
        contributors = await pc.safe(collector.get_contributors(), set(), "contributors")
    else:
        name = await collector.get_name()
        total_contributions = await collector.get_total_contributions()
        repos = await collector.get_repos()
        stars = await collector.get_stargazers()
        forks = await collector.get_forks()
        followers = await collector.get_followers()
        following = await collector.get_following()
        views = await collector.get_views()
        views_from = await collector.get_views_from_date()
        clones = await collector.get_clones()
        clones_from = await collector.get_clones_from_date()
        pull_requests = await collector.get_pull_requests()
        issues = await collector.get_issues()
        lines = await collector.get_lines_changed()
        avg_percent = await collector.get_avg_contribution_percent()
        collaborators = await collector.get_collaborators()
        contributors = await collector.get_contributors()

    repos_count = len(repos) if repos is not None else None
    contributors_count = len(contributors) if contributors is not None else None

    return {
        "username": username,
        "name": name,
        "total_contributions": total_contributions,
        "repositories_count": repos_count,
        "total_stars": stars,
        "total_forks": forks,
        "total_followers": followers,
        "total_following": following,
        "total_views": views,
        "views_from_date": views_from,
        "total_clones": clones,
        "clones_from_date": clones_from,
        "total_pull_requests": pull_requests,
        "total_issues": issues,
        "lines_added": lines[0],
        "lines_deleted": lines[1],
        "avg_contribution_percent": avg_percent,
        "collaborators_count": collaborators,
        "contributors_count": contributors_count,
    }


async def build_snapshot_payload(
    collector,
    *,
    partial_collector=None,
) -> Dict[str, Any]:
    """Build the snapshot dict stored in snapshots.db.

    :param collector: Stats collector instance.
    :param partial_collector: Optional :class:`PartialCollector` for
        fault-tolerant collection.
    :returns: Flat statistics dictionary for snapshot storage.
    :rtype: dict
    """
    pc = partial_collector

    if pc is not None:
        total_contributions = await pc.safe(collector.get_total_contributions(), 0, "total contributions")
        repos = await pc.safe(collector.get_repos(), set(), "repositories")
        stars = await pc.safe(collector.get_stargazers(), 0, "stargazers")
        forks = await pc.safe(collector.get_forks(), 0, "forks")
        followers = await pc.safe(collector.get_followers(), 0, "followers")
        following = await pc.safe(collector.get_following(), 0, "following")
        pull_requests = await pc.safe(collector.get_pull_requests(), 0, "pull requests")
        issues = await pc.safe(collector.get_issues(), 0, "issues")
        lines = await pc.safe(collector.get_lines_changed(), (0, 0), "lines changed")
        current_streak = await pc.safe(collector.get_current_streak(), 0, "current streak")
        longest_streak = await pc.safe(collector.get_longest_streak(), 0, "longest streak")
    else:
        total_contributions = await collector.get_total_contributions()
        repos = await collector.get_repos()
        stars = await collector.get_stargazers()
        forks = await collector.get_forks()
        followers = await collector.get_followers()
        following = await collector.get_following()
        pull_requests = await collector.get_pull_requests()
        issues = await collector.get_issues()
        lines = await collector.get_lines_changed()
        current_streak = await collector.get_current_streak()
        longest_streak = await collector.get_longest_streak()

    return {
        "total_contributions": total_contributions,
        "repositories_count": len(repos),
        "total_stars": stars,
        "total_forks": forks,
        "total_followers": followers,
        "total_following": following,
        "total_pull_requests": pull_requests,
        "total_issues": issues,
        "lines_added": lines[0],
        "lines_deleted": lines[1],
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }


async def build_full_payload(
    collector,
    username: str,
    *,
    partial_collector=None,
) -> Dict[str, Any]:
    """Build the full stats payload combining overview with extra sections.

    :param collector: Stats collector instance.
    :param username: GitHub username.
    :param partial_collector: Optional :class:`PartialCollector`.
    :returns: Complete statistics dictionary.
    :rtype: dict
    """
    pc = partial_collector
    overview = await build_overview_payload(collector, username, partial_collector=pc)

    if pc is not None:
        languages = await pc.safe(collector.get_languages(), None, "languages")
        current_streak = await pc.safe(collector.get_current_streak(), None, "current streak")
        current_range = await pc.safe(collector.get_current_streak_range(), None, "current streak range")
        longest_streak = await pc.safe(collector.get_longest_streak(), None, "longest streak")
        longest_range = await pc.safe(collector.get_longest_streak_range(), None, "longest streak range")
        recent = await pc.safe(collector.get_recent_contributions(), None, "recent contributions")
        weekly = await pc.safe(collector.get_weekly_commit_schedule(), None, "weekly commits")
    else:
        languages = await collector.get_languages()
        current_streak = await collector.get_current_streak()
        current_range = await collector.get_current_streak_range()
        longest_streak = await collector.get_longest_streak()
        longest_range = await collector.get_longest_streak_range()
        recent = await collector.get_recent_contributions()
        weekly = await collector.get_weekly_commit_schedule()

    repos_count = overview["repositories_count"]

    return {
        "username": username,
        "overview": {k: v for k, v in overview.items() if k != "username"},
        "languages": languages,
        "streak": {
            "current_streak": current_streak,
            "current_streak_range": current_range,
            "longest_streak": longest_streak,
            "longest_streak_range": longest_range,
        },
        "contributions": {
            "total": overview["total_contributions"],
            "recent": recent,
        },
        "repositories": {
            "count": repos_count,
            "list": sorted(list(await collector.get_repos())) if repos_count else None,
        },
        "weekly_commits": weekly,
    }
