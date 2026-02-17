#!/usr/bin/python3
"""
Flask API for Leo's Git Statistics.

Provides REST endpoints to access GitHub repository data with enriched statistics.
The same data used to generate SVG cards is available via JSON endpoints.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
import os
from functools import wraps
from typing import Optional

from aiohttp import ClientSession
from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger, swag_from

from src.core.environment import Environment
from src.core.github_client import GitHubClient
from src.core.stats_collector import StatsCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Leo's Git Statistics API",
        "description": "REST API providing GitHub statistics and metrics. The same data used to generate SVG cards is available via JSON endpoints.",
        "version": "latest",
        "contact": {
            "name": "Leonardo Klein",
            "url": "https://github.com/leonardokr/leo-git-statistics",
        },
    },
    "host": os.getenv("API_HOST", "localhost:5000"),
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Overview",
            "description": "General GitHub statistics and metrics",
        },
        {
            "name": "Languages",
            "description": "Programming language distribution and statistics",
        },
        {
            "name": "Contributions",
            "description": "Contribution streaks and calendar data",
        },
        {
            "name": "Repositories",
            "description": "Repository information and details",
        },
        {
            "name": "Health",
            "description": "API health and status checks",
        },
    ],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)


def async_route(f):
    """Decorator to run async functions in Flask routes."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def get_github_token():
    """Get GitHub token from environment."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN or ACCESS_TOKEN environment variable not set")
    return token


async def create_stats_collector(username: str) -> StatsCollector:
    """
    Create a StatsCollector instance for the given username.

    :param username: GitHub username
    :return: Configured StatsCollector instance
    """
    token = get_github_token()

    env = Environment(username=username, access_token=token)

    session = ClientSession()

    collector = StatsCollector(env, session)

    return collector, session


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    ---
    tags:
      - Health
    responses:
      200:
        description: API is running
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            message:
              type: string
              example: Leo's Git Statistics API is running
    """
    return jsonify({"status": "ok", "message": "Leo's Git Statistics API is running"})


@app.route("/users/<username>/overview", methods=["GET"])
@async_route
async def get_user_overview(username):
    """
    Get comprehensive overview statistics for a GitHub user.
    ---
    tags:
      - Overview
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
    responses:
      200:
        description: User overview statistics
        schema:
          type: object
          properties:
            username:
              type: string
            name:
              type: string
            total_contributions:
              type: integer
            repositories_count:
              type: integer
            total_stars:
              type: integer
            total_forks:
              type: integer
            total_views:
              type: integer
            views_from_date:
              type: string
            total_clones:
              type: integer
            clones_from_date:
              type: string
            total_pull_requests:
              type: integer
            total_issues:
              type: integer
            lines_added:
              type: integer
            lines_deleted:
              type: integer
            avg_contribution_percent:
              type: string
            collaborators_count:
              type: integer
            contributors_count:
              type: integer
      500:
        description: Internal server error
    """
    session = None
    try:
        collector, session = await create_stats_collector(username)

        name = await collector.get_name()
        total_contributions = await collector.get_total_contributions()
        repos = await collector.get_repos()
        stars = await collector.get_stargazers()
        forks = await collector.get_forks()
        views = await collector.get_views()
        views_from = await collector.get_views_from_date()
        clones = await collector.get_clones()
        clones_from = await collector.get_clones_from_date()
        pull_requests = await collector.get_pull_requests()
        issues = await collector.get_issues()
        lines_added, lines_deleted = await collector.get_lines_changed()
        avg_percent = await collector.get_avg_contribution_percent()
        collaborators = await collector.get_collaborators()
        contributors = await collector.get_contributors()

        return jsonify({
            "username": username,
            "name": name,
            "total_contributions": total_contributions,
            "repositories_count": len(repos),
            "total_stars": stars,
            "total_forks": forks,
            "total_views": views,
            "views_from_date": views_from,
            "total_clones": clones,
            "clones_from_date": clones_from,
            "total_pull_requests": pull_requests,
            "total_issues": issues,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "avg_contribution_percent": avg_percent,
            "collaborators_count": collaborators,
            "contributors_count": len(contributors),
        })
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching overview for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        if session:
            await session.close()


@app.route("/users/<username>/languages", methods=["GET"])
@async_route
async def get_user_languages(username):
    """
    Get programming language distribution for a GitHub user.
    ---
    tags:
      - Languages
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
      - name: proportional
        in: query
        type: boolean
        required: false
        description: Return only proportional percentages (simplified format)
    responses:
      200:
        description: Language distribution statistics
        schema:
          type: object
          properties:
            username:
              type: string
            languages:
              type: object
              description: Language statistics with size, occurrences, color, and proportion
      500:
        description: Internal server error
    """
    session = None
    try:
        collector, session = await create_stats_collector(username)

        proportional = request.args.get("proportional", "false").lower() == "true"

        if proportional:
            languages = await collector.get_languages_proportional()
        else:
            languages = await collector.get_languages()

        return jsonify({
            "username": username,
            "languages": languages,
        })
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching languages for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        if session:
            await session.close()


@app.route("/users/<username>/streak", methods=["GET"])
@async_route
async def get_user_streak(username):
    """
    Get contribution streak information for a GitHub user.
    ---
    tags:
      - Contributions
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
    responses:
      200:
        description: Contribution streak statistics
        schema:
          type: object
          properties:
            username:
              type: string
            current_streak:
              type: integer
            current_streak_range:
              type: string
            longest_streak:
              type: integer
            longest_streak_range:
              type: string
            total_contributions:
              type: integer
      500:
        description: Internal server error
    """
    session = None
    try:
        collector, session = await create_stats_collector(username)

        current_streak = await collector.get_current_streak()
        current_range = await collector.get_current_streak_range()
        longest_streak = await collector.get_longest_streak()
        longest_range = await collector.get_longest_streak_range()
        total_contributions = await collector.get_total_contributions()

        return jsonify({
            "username": username,
            "current_streak": current_streak,
            "current_streak_range": current_range,
            "longest_streak": longest_streak,
            "longest_streak_range": longest_range,
            "total_contributions": total_contributions,
        })
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching streak for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        if session:
            await session.close()


@app.route("/users/<username>/contributions/recent", methods=["GET"])
@async_route
async def get_recent_contributions(username):
    """
    Get recent contribution counts (last 10 days).
    ---
    tags:
      - Contributions
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
    responses:
      200:
        description: Recent contribution counts
        schema:
          type: object
          properties:
            username:
              type: string
            recent_contributions:
              type: array
              items:
                type: integer
              description: Contribution counts for the last 10 days (most recent last)
      500:
        description: Internal server error
    """
    session = None
    try:
        collector, session = await create_stats_collector(username)

        recent = await collector.get_recent_contributions()

        return jsonify({
            "username": username,
            "recent_contributions": recent,
        })
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching recent contributions for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        if session:
            await session.close()


@app.route("/users/<username>/commits/weekly", methods=["GET"])
@async_route
async def get_weekly_commits(username):
    """
    Get weekly commit schedule for a GitHub user.
    ---
    tags:
      - Contributions
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
    responses:
      200:
        description: Weekly commit schedule
        schema:
          type: object
          properties:
            username:
              type: string
            weekly_commits:
              type: array
              items:
                type: object
                properties:
                  repo:
                    type: string
                  commit_time:
                    type: string
                  message:
                    type: string
      500:
        description: Internal server error
    """
    session = None
    try:
        collector, session = await create_stats_collector(username)

        weekly = await collector.get_weekly_commit_schedule()

        return jsonify({
            "username": username,
            "weekly_commits": weekly,
        })
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching weekly commits for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        if session:
            await session.close()


@app.route("/users/<username>/repositories", methods=["GET"])
@async_route
async def get_user_repositories(username):
    """
    Get list of repositories for a GitHub user.
    ---
    tags:
      - Repositories
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
    responses:
      200:
        description: User repositories
        schema:
          type: object
          properties:
            username:
              type: string
            repositories_count:
              type: integer
            repositories:
              type: array
              items:
                type: string
      500:
        description: Internal server error
    """
    session = None
    try:
        collector, session = await create_stats_collector(username)

        repos = await collector.get_repos()

        return jsonify({
            "username": username,
            "repositories_count": len(repos),
            "repositories": sorted(list(repos)),
        })
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching repositories for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        if session:
            await session.close()


@app.route("/users/<username>/repositories/detailed", methods=["GET"])
@async_route
async def get_user_repositories_detailed(username):
    """
    Get detailed repository information for a GitHub user (perfect for portfolios).
    ---
    tags:
      - Repositories
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
      - name: visibility
        in: query
        type: string
        required: false
        description: Filter by visibility (all, public, private)
        default: public
      - name: sort
        in: query
        type: string
        required: false
        description: Sort by (updated, created, pushed, stars)
        default: updated
      - name: limit
        in: query
        type: integer
        required: false
        description: Maximum number of repos to return
        default: 100
      - name: exclude_forks
        in: query
        type: boolean
        required: false
        description: Exclude forked repositories
        default: true
      - name: exclude_archived
        in: query
        type: boolean
        required: false
        description: Exclude archived repositories
        default: true
    responses:
      200:
        description: Detailed repository information
        schema:
          type: object
          properties:
            username:
              type: string
            repositories_count:
              type: integer
            repositories:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  full_name:
                    type: string
                  description:
                    type: string
                  html_url:
                    type: string
                  homepage:
                    type: string
                  language:
                    type: string
                  languages:
                    type: object
                  stargazers_count:
                    type: integer
                  forks_count:
                    type: integer
                  topics:
                    type: array
                    items:
                      type: string
                  created_at:
                    type: string
                  updated_at:
                    type: string
                  pushed_at:
                    type: string
      500:
        description: Internal server error
    """
    session = None
    try:
        token = get_github_token()
        client = GitHubClient(username=username, access_token=token)

        visibility = request.args.get("visibility", "public")
        sort = request.args.get("sort", "updated")
        limit = int(request.args.get("limit", "100"))
        exclude_forks = request.args.get("exclude_forks", "true").lower() == "true"
        exclude_archived = request.args.get("exclude_archived", "true").lower() == "true"

        repos_url = f"users/{username}/repos?per_page={limit}&sort={sort}&type={visibility}"
        response = await client.query_rest_async(repos_url)

        if not response:
            return jsonify({"error": "Failed to fetch repositories"}), 500

        repositories = []
        for repo in response:
            if exclude_forks and repo.get("fork", False):
                continue
            if exclude_archived and repo.get("archived", False):
                continue

            repo_data = {
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description", ""),
                "html_url": repo.get("html_url"),
                "homepage": repo.get("homepage", ""),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "open_issues_count": repo.get("open_issues_count", 0),
                "watchers_count": repo.get("watchers_count", 0),
                "topics": repo.get("topics", []),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "is_fork": repo.get("fork", False),
                "is_archived": repo.get("archived", False),
                "is_private": repo.get("private", False),
            }

            try:
                languages = await client.query_rest_async(
                    f"repos/{username}/{repo.get('name')}/languages"
                )
                if languages:
                    repo_data["languages"] = languages
            except Exception as e:
                logger.warning(f"Failed to fetch languages for {repo.get('name')}: {e}")
                repo_data["languages"] = {}

            repositories.append(repo_data)

        return jsonify({
            "username": username,
            "repositories_count": len(repositories),
            "repositories": repositories,
        })

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching detailed repositories for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@app.route("/users/<username>/stats/full", methods=["GET"])
@async_route
async def get_full_stats(username):
    """
    Get all statistics for a GitHub user in a single request.
    This endpoint returns the complete dataset used to generate all SVG cards.
    ---
    tags:
      - Overview
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: GitHub username
    responses:
      200:
        description: Complete user statistics
        schema:
          type: object
          properties:
            username:
              type: string
            overview:
              type: object
            languages:
              type: object
            streak:
              type: object
            contributions:
              type: object
            repositories:
              type: object
      500:
        description: Internal server error
    """
    session = None
    try:
        collector, session = await create_stats_collector(username)

        name = await collector.get_name()
        total_contributions = await collector.get_total_contributions()
        repos = await collector.get_repos()
        stars = await collector.get_stargazers()
        forks = await collector.get_forks()
        views = await collector.get_views()
        views_from = await collector.get_views_from_date()
        clones = await collector.get_clones()
        clones_from = await collector.get_clones_from_date()
        pull_requests = await collector.get_pull_requests()
        issues = await collector.get_issues()
        lines_added, lines_deleted = await collector.get_lines_changed()
        avg_percent = await collector.get_avg_contribution_percent()
        collaborators = await collector.get_collaborators()
        contributors = await collector.get_contributors()
        languages = await collector.get_languages()
        current_streak = await collector.get_current_streak()
        current_range = await collector.get_current_streak_range()
        longest_streak = await collector.get_longest_streak()
        longest_range = await collector.get_longest_streak_range()
        recent = await collector.get_recent_contributions()
        weekly = await collector.get_weekly_commit_schedule()

        return jsonify({
            "username": username,
            "overview": {
                "name": name,
                "total_contributions": total_contributions,
                "repositories_count": len(repos),
                "total_stars": stars,
                "total_forks": forks,
                "total_views": views,
                "views_from_date": views_from,
                "total_clones": clones,
                "clones_from_date": clones_from,
                "total_pull_requests": pull_requests,
                "total_issues": issues,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "avg_contribution_percent": avg_percent,
                "collaborators_count": collaborators,
                "contributors_count": len(contributors),
            },
            "languages": languages,
            "streak": {
                "current_streak": current_streak,
                "current_streak_range": current_range,
                "longest_streak": longest_streak,
                "longest_streak_range": longest_range,
            },
            "contributions": {
                "total": total_contributions,
                "recent": recent,
            },
            "repositories": {
                "count": len(repos),
                "list": sorted(list(repos)),
            },
            "weekly_commits": weekly,
        })
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error fetching full stats for {username}: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        if session:
            await session.close()


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
