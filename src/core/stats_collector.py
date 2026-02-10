#!/usr/bin/python3

from typing import Dict, Optional, Set, Tuple, Any, cast
from aiohttp import ClientSession
from datetime import date, timedelta

from src.core.environment import Environment
from src.core.github_client import GitHubClient

class StatsCollector:
    """
    Retrieves and aggregates statistics for GitHub users.

    This class provides a comprehensive set of statistics, including stargazers,
    forks, languages, contributions, and more, by querying the GitHub API.
    """

    __DATE_FORMAT = '%Y-%m-%d'

    def __init__(self,
                 environment_vars: Environment,
                 session: ClientSession):
        """
        Initializes the StatsCollector.

        :param environment_vars: Configuration and environment settings.
        :param session: aiohttp ClientSession for making requests.
        """
        self.environment_vars: Environment = environment_vars
        self.queries = GitHubClient(
            username=self.environment_vars.username,
            access_token=self.environment_vars.access_token,
            session=session)

        self._name: Optional[str] = None
        self._stargazers: Optional[int] = None
        self._forks: Optional[int] = None
        self._total_contributions: Optional[int] = None
        self._languages: Optional[Dict[str, Any]] = None
        self._repos: Optional[Set[str]] = None
        self._users_lines_changed: Optional[Tuple[int, int]] = None
        self._total_lines_changed: Optional[Tuple[int, int]] = None
        self._contributions_percentage: Optional[str] = None
        self._avg_percent: Optional[str] = None
        self._views: Optional[int] = None
        self._clones: Optional[int] = None
        self._collaborators: Optional[int] = None
        self._contributors: Optional[Set[str]] = None
        self._views_from_date: Optional[str] = None
        self._clones_from_date: Optional[str] = None
        self._pull_requests: Optional[int] = None
        self._issues: Optional[int] = None
        self._empty_repos: Optional[Set[str]] = None
        self._current_streak: Optional[int] = None
        self._longest_streak: Optional[int] = None
        self._current_streak_range: Optional[str] = None
        self._longest_streak_range: Optional[str] = None
        self._contribution_calendar: Optional[Dict[str, Any]] = None

    async def to_str(self) -> str:
        """
        Generates a string summary of all collected statistics.

        :return: A formatted summary of the statistics.
        """
        languages = await self.languages_proportional
        formatted_languages = "\n\t\t\t- ".join(
            [f"{k}: {v:0.4f}%" for k, v in languages.items()]
        )

        users_lines_changed = await self.lines_changed
        total_lines_changed = self._total_lines_changed

        if users_lines_changed[0] > 0:
            prcnt_added = users_lines_changed[0] / total_lines_changed[0] * 100
        else:
            prcnt_added = 0.0

        if users_lines_changed[1] > 0:
            prcnt_dltd = users_lines_changed[1] / total_lines_changed[1] * 100
        else:
            prcnt_dltd = 0.0
        ttl_prcnt = await self.contributions_percentage
        avg_prcnt = await self.avg_contribution_percent

        contribs = max(len(await self.contributors) - 1, 0)

        return f"""GitHub Repository Statistics:
        Stargazers: {await self.stargazers:,}
        Forks: {await self.forks:,}
        Pull requests: {await self.pull_requests:,}
        Issues: {await self.issues:,}
        All-time contributions: {await self.total_contributions:,}
        Repositories with contributions: {len(await self.repos):,}
        Lines of code added: {users_lines_changed[0]:,}
        Lines of code deleted: {users_lines_changed[1]:,}
        Lines of code changed: {sum(users_lines_changed):,}
        Percentage of total code line additions: {prcnt_added:0.2f}%
        Percentage of total code line deletions: {prcnt_dltd:0.2f}%
        Percentage of code change contributions: {ttl_prcnt}
        Avg. % of code change contributions: {avg_prcnt}
        Project page views: {await self.views:,}
        Project page views from date: {await self.views_from_date}
        Project repository clones: {await self.clones:,}
        Project repository clones from date: {await self.clones_from_date}
        Project repository collaborators: {await self.collaborators:,}
        Project repository contributors: {contribs:,}
        Languages:\n\t\t\t- {formatted_languages}"""

    async def is_repo_name_invalid(self, repo_name: str) -> bool:
        """
        Checks if a repository name is invalid or should be excluded.

        A repository is considered invalid if:
            - It has already been processed.
            - It is not in the explicit inclusion list (if one is provided).
            - It is in the exclusion list.

        :param repo_name: The name of the repository (owner/name format).
        :return: True if the repository should be excluded, False otherwise.
        """
        return repo_name in self._repos \
            or len(self.environment_vars.only_included_repos) > 0 \
            and repo_name not in self.environment_vars.only_included_repos \
            or repo_name in self.environment_vars.exclude_repos

    async def is_repo_type_excluded(self, repo_data: Dict[str, Any]) -> bool:
        """
        Checks if a repository should be excluded based on its type and user configuration.

        Criteria for exclusion:
            - Forks (if configured to exclude).
            - Archived repositories (if configured to exclude).
            - Private repositories (if configured to exclude).
            - Public repositories (if configured to exclude).

        :param repo_data: Dictionary containing repository metadata from the API.
        :return: True if the repository type should be excluded, False otherwise.
        """
        return not self.environment_vars.include_forked_repos \
            and (repo_data.get("isFork")
                 or repo_data.get("fork")) \
            or self.environment_vars.exclude_archive_repos \
            and (repo_data.get("isArchived")
                 or repo_data.get("archived")) \
            or self.environment_vars.exclude_private_repos \
            and (repo_data.get("isPrivate")
                 or repo_data.get("private")) \
            or self.environment_vars.exclude_public_repos \
            and (not repo_data.get("isPrivate")
                 or not repo_data.get("private"))

    async def _process_languages(self, repo_data: Dict[str, Any]) -> None:
        """
        Extracts and aggregates language data from a single repository's metadata.

        :param repo_data: Dictionary containing repository metadata.
        """
        repo_name = repo_data.get("nameWithOwner", "unknown")
        for edge in repo_data.get("languages", {}).get("edges", []):
            lang_name = edge.get("node", {}).get("name", "Other")
            if lang_name in self.environment_vars.exclude_langs:
                continue

            size = edge.get("size", 0)
            color = edge.get("node", {}).get("color")
            print(f"  {repo_name}: {lang_name} ({size} bytes)")
            
            if lang_name in self._languages:
                self._languages[lang_name]["size"] += size
                self._languages[lang_name]["occurrences"] += 1
            else:
                self._languages[lang_name] = {
                    "size": size,
                    "occurrences": 1,
                    "color": color,
                }

    async def get_stats(self) -> None:
        """
        Fetches and aggregates general statistics from GitHub.

        This method populates multiple attributes by performing paginated queries
        to the GitHub GraphQL API.
        """
        self._stargazers = 0
        self._forks = 0
        self._languages = dict()
        self._repos = set()
        self._empty_repos = set()

        next_owned = None
        next_contrib = None

        while True:
            raw_results = await self.queries.query(
                GitHubClient.repos_overview(owned_cursor=next_owned,
                                            contrib_cursor=next_contrib)
            )
            raw_results = raw_results if raw_results is not None else {}

            viewer_data = raw_results.get("data", {}).get("viewer", {})
            self._name = viewer_data.get("name") or viewer_data.get("login", "No Name")

            contrib_repos = viewer_data.get("repositoriesContributedTo", {})
            owned_repos = viewer_data.get("repositories", {})

            repos = owned_repos.get("nodes", [])
            if not self.environment_vars.exclude_contrib_repos:
                repos += contrib_repos.get("nodes", [])

            for repo in repos:
                if not repo or await self.is_repo_type_excluded(repo):
                    continue

                full_name = repo.get("nameWithOwner")
                if await self.is_repo_name_invalid(full_name):
                    continue
                
                self._repos.add(full_name)
                self._stargazers += repo.get("stargazers", {}).get("totalCount", 0)
                self._forks += repo.get("forkCount", 0)

                if repo.get("isEmpty"):
                    self._empty_repos.add(full_name)
                    continue

                await self._process_languages(repo)

            owned_page_info = owned_repos.get("pageInfo", {})
            contrib_page_info = contrib_repos.get("pageInfo", {})
            
            if owned_page_info.get("hasNextPage") or contrib_page_info.get("hasNextPage"):
                next_owned = owned_page_info.get("endCursor", next_owned)
                next_contrib = contrib_page_info.get("endCursor", next_contrib)
            else:
                break

        if not self.environment_vars.exclude_contrib_repos:
            await self._process_manually_added_repos()

        self._calculate_language_proportions()

    async def _process_manually_added_repos(self) -> None:
        """
        Fetches and aggregates statistics for manually specified repositories.
        """
        env_repos = self.environment_vars.manually_added_repos
        lang_cols = self.queries.get_language_colors()

        for repo in env_repos:
            if await self.is_repo_name_invalid(repo):
                continue

            repo_stats = await self.queries.query_rest(f"/repos/{repo}")
            if await self.is_repo_type_excluded(repo_stats):
                continue
            
            self._repos.add(repo)
            self._stargazers += repo_stats.get("stargazers_count", 0)
            self._forks += repo_stats.get("forks_count", 0)

            if repo_stats.get("size") == 0:
                self._empty_repos.add(repo)
                continue

            if repo_stats.get("language"):
                langs = await self.queries.query_rest(f"/repos/{repo}/languages")
                for lang, size in langs.items():
                    if lang in self.environment_vars.exclude_langs:
                        continue

                    if lang in self._languages:
                        self._languages[lang]["size"] += size
                        self._languages[lang]["occurrences"] += 1
                    else:
                        color_data = lang_cols.get(lang)
                        self._languages[lang] = {
                            "size": size,
                            "occurrences": 1,
                            "color": color_data.get("color") if color_data else None
                        }

    def _calculate_language_proportions(self) -> None:
        """
        Calculates the percentage of usage for each programming language.
        """
        langs_total = sum(v.get("size", 0) for v in self._languages.values())
        if langs_total > 0:
            for v in self._languages.values():
                v["prop"] = 100 * (v.get("size", 0) / langs_total)
        else:
            for v in self._languages.values():
                v["prop"] = 0.0

    @property
    async def name(self) -> str:
        """
        Retrieves the GitHub user's name or login.

        :return: The user's name, or login if name is not available.
        """
        if self._name is not None:
            return self._name
        await self.get_stats()
        assert self._name is not None
        return self._name

    @property
    async def stargazers(self) -> int:
        """
        Retrieves the total number of stargazers across the user's repositories.

        :return: Total stargazer count.
        """
        if self._stargazers is not None:
            return self._stargazers
        await self.get_stats()
        assert self._stargazers is not None
        return self._stargazers

    @property
    async def forks(self) -> int:
        """
        Retrieves the total number of forks across the user's repositories.

        :return: Total fork count.
        """
        if self._forks is not None:
            return self._forks
        await self.get_stats()
        assert self._forks is not None
        return self._forks

    @property
    async def languages(self) -> Dict[str, Any]:
        """
        Retrieves a summary of languages used across the user's repositories.

        :return: A dictionary containing language stats (size, occurrences, color).
        """
        if self._languages is not None:
            return self._languages
        await self.get_stats()
        assert self._languages is not None
        return self._languages

    @property
    async def languages_proportional(self) -> Dict[str, float]:
        """
        Retrieves a summary of language usage as percentages.

        :return: A dictionary mapping language names to their usage percentage.
        """
        if self._languages is None:
            await self.get_stats()
            assert self._languages is not None
        return {k: v.get("prop", 0) for (k, v) in self._languages.items()}

    @property
    async def repos(self) -> Set[str]:
        """
        Retrieves the set of names for all processed repositories.

        :return: A set of repository names in 'owner/repo' format.
        """
        if self._repos is not None:
            return self._repos
        await self.get_stats()
        assert self._repos is not None
        return self._repos

    @property
    async def total_contributions(self) -> int:
        """
        Retrieves the total number of contributions as defined by GitHub.

        :return: Total contribution count.
        """
        if self._total_contributions is not None:
            return self._total_contributions
        self._total_contributions = 0

        years = ((await self.queries.query(GitHubClient
                                           .contributions_all_years()))
                 .get("data", {})
                 .get("viewer", {})
                 .get("contributionsCollection", {})
                 .get("contributionYears", []))

        by_year = ((await self.queries.query(GitHubClient
                                             .all_contributions(years)))
                   .get("data", {})
                   .get("viewer", {})
                   .values())

        for year in by_year:
            self._total_contributions += year\
                .get("contributionCalendar", {})\
                .get("totalContributions", 0)
        return cast(int, self._total_contributions)

    @property
    async def lines_changed(self) -> Tuple[int, int]:
        """
        Calculates the total lines added and deleted by the user.

        This method also calculates the total lines changed across all repositories,
        the percentage of user contributions, and the set of contributors.

        :return: A tuple containing (total_additions, total_deletions) by the user.
        """
        if self._users_lines_changed is not None:
            return self._users_lines_changed
        contributor_set = set()
        total_additions = 0
        total_deletions = 0
        additions = 0
        deletions = 0
        total_percentage = 0

        for repo in await self.repos:
            if repo in self._empty_repos:
                continue
            repo_total_changes = 0
            author_total_changes = 0

            r = await self.queries\
                .query_rest(f"/repos/{repo}/stats/contributors")

            for author_obj in r:
                # Handle malformed response from API by skipping this repo
                if not isinstance(author_obj, dict) or not isinstance(
                        author_obj.get("author", {}), dict
                ):
                    continue
                author = author_obj.get("author", {}).get("login", "")
                contributor_set.add(author)

                if author != self.environment_vars.username:
                    for week in author_obj.get("weeks", []):
                        total_additions += week.get("a", 0)
                        total_deletions += week.get("d", 0)
                        repo_total_changes += week.get("a", 0)
                        repo_total_changes += week.get("d", 0)
                else:
                    for week in author_obj.get("weeks", []):
                        additions += week.get("a", 0)
                        deletions += week.get("d", 0)
                        author_total_changes += week.get("a", 0)
                        author_total_changes += week.get("d", 0)

            repo_total_changes += author_total_changes
            if author_total_changes > 0:
                total_percentage += author_total_changes / repo_total_changes
        if total_percentage > 0:
            total_percentage /= len(self._repos) - len(self._empty_repos)
        else:
            total_percentage = 0.0
        self._avg_percent = f"{total_percentage * 100:0.2f}%"

        total_additions += additions
        total_deletions += deletions
        self._users_lines_changed = (additions, deletions)
        self._total_lines_changed = (total_additions, total_deletions)

        if sum(self._users_lines_changed) > 0:
            ttl_changes = sum(self._total_lines_changed)
            user_changes = sum(self._users_lines_changed)
            percent_contribs = user_changes / ttl_changes * 100
        else:
            percent_contribs = 0.0
        self._contributions_percentage = f"{percent_contribs:0.2f}%"

        self._contributors = contributor_set

        return self._users_lines_changed

    @property
    async def contributions_percentage(self) -> str:
        """
        Retrieves the percentage of code changes made by the user relative to the total.

        :return: A formatted percentage string (e.g., '25.00%').
        """
        if self._contributions_percentage is not None:
            return self._contributions_percentage
        await self.lines_changed
        assert self._contributions_percentage is not None
        return self._contributions_percentage

    @property
    async def avg_contribution_percent(self) -> str:
        """
        Retrieves the average percentage of contributions per repository.

        :return: A formatted percentage string (e.g., '10.50%').
        """
        if self._avg_percent is not None:
            return self._avg_percent
        await self.lines_changed
        assert self._avg_percent is not None
        return self._avg_percent

    @property
    async def views(self) -> int:
        """
        Retrieves the cumulative count of repository views.

        Note: The GitHub API only returns view data for the last 14 days.
        This property aggregates historical data stored in the database with
        recent data from the API.

        :return: Total repository view count.
        """
        if self._views is not None:
            return self._views

        last_viewed = self.environment_vars.repo_last_viewed
        today = date.today().strftime(self.__DATE_FORMAT)
        yesterday = (date.today() - timedelta(1)).strftime(self.__DATE_FORMAT)
        dates = {last_viewed, yesterday}

        today_view_count = 0
        for repo in await self.repos:
            r = await self.queries.query_rest(f"/repos/{repo}/traffic/views")

            for view in r.get("views", []):
                if view.get("timestamp")[:10] == today:
                    today_view_count += view.get("count", 0)
                elif view.get("timestamp")[:10] > last_viewed:
                    self.environment_vars.set_views(view.get("count", 0))
                    dates.add(view.get("timestamp")[:10])

        if last_viewed == "0000-00-00":
            dates.remove(last_viewed)

        if self.environment_vars.store_repo_view_count:
            self.environment_vars.set_last_viewed(yesterday)

            if self.environment_vars.repo_first_viewed == "0000-00-00":
                self.environment_vars.repo_first_viewed = min(dates)
            self.environment_vars. \
                set_first_viewed(self.environment_vars.repo_first_viewed)
            self._views_from_date = self.environment_vars.repo_first_viewed
        else:
            self._views_from_date = min(dates)

        self._views = self.environment_vars.repo_views + today_view_count
        return self._views

    @property
    async def views_from_date(self) -> str:
        """
        Retrieves the starting date from which repository views are being counted.

        :return: A date string in 'YYYY-MM-DD' format.
        """
        if self._views_from_date is not None:
            return self._views_from_date
        await self.views
        assert self._views_from_date is not None
        return self._views_from_date

    @property
    async def clones(self) -> int:
        """
        Retrieves the cumulative count of repository clones.

        Note: Similar to views, GitHub API only returns clone data for the last 14 days.
        This property combines database records with recent API data.

        :return: Total repository clone count.
        """
        if self._clones is not None:
            return self._clones

        last_cloned = self.environment_vars.repo_last_cloned
        today = date.today().strftime(self.__DATE_FORMAT)
        yesterday = (date.today() - timedelta(1)).strftime(self.__DATE_FORMAT)
        dates = {last_cloned, yesterday}

        today_clone_count = 0
        for repo in await self.repos:
            r = await self.queries.query_rest(f"/repos/{repo}/traffic/clones")

            for clone in r.get("clones", []):
                if clone.get("timestamp")[:10] == today:
                    today_clone_count += clone.get("count", 0)
                elif clone.get("timestamp")[:10] > last_cloned:
                    self.environment_vars.set_clones(clone.get("count", 0))
                    dates.add(clone.get("timestamp")[:10])

        if last_cloned == "0000-00-00":
            dates.remove(last_cloned)

        if self.environment_vars.store_repo_clone_count:
            self.environment_vars.set_last_cloned(yesterday)

            if self.environment_vars.repo_first_cloned == "0000-00-00":
                self.environment_vars.repo_first_cloned = min(dates)
            self.environment_vars.\
                set_first_cloned(self.environment_vars.repo_first_cloned)
            self._clones_from_date = self.environment_vars.repo_first_cloned
        else:
            self._clones_from_date = min(dates)

        self._clones = self.environment_vars.repo_clones + today_clone_count
        return self._clones

    @property
    async def clones_from_date(self) -> str:
        """
        Retrieves the starting date from which repository clones are being counted.

        :return: A date string in 'YYYY-MM-DD' format.
        """
        if self._clones_from_date is not None:
            return self._clones_from_date
        await self.clones
        assert self._clones_from_date is not None
        return self._clones_from_date

    @property
    async def collaborators(self) -> int:
        """
        Retrieves the total number of unique collaborators across all repositories.

        :return: Total collaborator count.
        """
        if self._collaborators is not None:
            return self._collaborators

        collaborator_set = set()

        for repo in await self.repos:
            r = await self.queries\
                .query_rest(f"/repos/{repo}/collaborators")

            for obj in r:
                if isinstance(obj, dict):
                    collaborator_set.add(obj.get("login"))

        collabs = max(0, len(collaborator_set
                             .union(await self.contributors)) - 1)
        self._collaborators = self.environment_vars.more_collabs + collabs
        return self._collaborators

    @property
    async def contributors(self) -> Set[str]:
        """
        Retrieves the set of unique contributors across all repositories.

        :return: A set of contributor usernames.
        """
        if self._contributors is not None:
            return self._contributors
        await self.lines_changed
        assert self._contributors is not None
        return self._contributors

    @property
    async def pull_requests(self) -> int:
        """
        Retrieves the total number of pull requests across all repositories.

        :return: Total pull request count.
        """
        if self._pull_requests is not None:
            return self._pull_requests

        self._pull_requests = 0

        for repo in await self.repos:
            r = await self.queries\
                .query_rest(f"/repos/{repo}/pulls?state=all")

            for obj in r:
                if isinstance(obj, dict):
                    self._pull_requests += 1
        return self._pull_requests

    @property
    async def issues(self) -> int:
        """
        Retrieves the total number of issues across all repositories.

        :return: Total issue count (excluding pull requests).
        """
        if self._issues is not None:
            return self._issues

        self._issues = 0

        for repo in await self.repos:
            r = await self.queries\
                .query_rest(f"/repos/{repo}/issues?state=all")

            for obj in r:
                if isinstance(obj, dict):
                    try:
                        if obj.get("html_url").split("/")[-2] == "issues":
                            self._issues += 1
                    except AttributeError:
                        continue
        return self._issues

    async def _get_contribution_calendar(self) -> None:
        """
        Fetches the contribution calendar data and calculates streak information.

        This method queries GitHub's GraphQL API to get contribution data
        and calculates both current and longest contribution streaks.
        """
        if self._contribution_calendar is not None:
            return

        years = ((await self.queries.query(GitHubClient
                                           .contributions_all_years()))
                 .get("data", {})
                 .get("viewer", {})
                 .get("contributionsCollection", {})
                 .get("contributionYears", []))

        all_days = []
        for year in years:
            query = f"""
            {{
              viewer {{
                contributionsCollection(from: "{year}-01-01T00:00:00Z", to: "{year}-12-31T23:59:59Z") {{
                  contributionCalendar {{
                    weeks {{
                      contributionDays {{
                        contributionCount
                        date
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            result = await self.queries.query(query)
            weeks = (result
                     .get("data", {})
                     .get("viewer", {})
                     .get("contributionsCollection", {})
                     .get("contributionCalendar", {})
                     .get("weeks", []))

            for week in weeks:
                for day in week.get("contributionDays", []):
                    all_days.append({
                        "date": day.get("date"),
                        "count": day.get("contributionCount", 0)
                    })

        all_days.sort(key=lambda x: x["date"])

        if all_days:
            print(f"Contribution calendar: {len(all_days)} days, last 10: {all_days[-10:]}")

        current_streak = 0
        longest_streak = 0
        current_streak_start = None
        current_streak_end = None
        longest_streak_start = None
        longest_streak_end = None
        temp_streak = 0
        temp_streak_start = None

        today = date.today().strftime(self.__DATE_FORMAT)

        for i, day in enumerate(all_days):
            if day["count"] > 0:
                if temp_streak == 0:
                    temp_streak_start = day["date"]
                temp_streak += 1

                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                    longest_streak_start = temp_streak_start
                    longest_streak_end = day["date"]

                if day["date"] == today or (i == len(all_days) - 1):
                    current_streak = temp_streak
                    current_streak_start = temp_streak_start
                    current_streak_end = day["date"]
            else:
                if i < len(all_days) - 1 or day["date"] == today:
                    temp_streak = 0
                    temp_streak_start = None

        yesterday = (date.today() - timedelta(1)).strftime(self.__DATE_FORMAT)
        if all_days and all_days[-1]["date"] < yesterday:
            current_streak = 0
            current_streak_start = None
            current_streak_end = None

        self._current_streak = current_streak
        self._longest_streak = longest_streak
        self._current_streak_range = self._format_date_range(current_streak_start, current_streak_end)
        self._longest_streak_range = self._format_date_range(longest_streak_start, longest_streak_end)
        self._contribution_calendar = {"days": all_days}

    def _format_date_range(self, start: Optional[str], end: Optional[str]) -> str:
        """
        Formats a date range for display.

        :param start: Start date string in YYYY-MM-DD format.
        :param end: End date string in YYYY-MM-DD format.
        :return: Formatted date range string.
        """
        if not start or not end:
            return "No streak"

        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            start_fmt = start_date.strftime("%b %d")
            end_fmt = end_date.strftime("%b %d, %Y")

            if start_date.year != end_date.year:
                start_fmt = start_date.strftime("%b %d, %Y")

            return f"{start_fmt} - {end_fmt}"
        except ValueError:
            return "No streak"

    @property
    async def current_streak(self) -> int:
        """
        Retrieves the current contribution streak in days.

        :return: Number of consecutive days with contributions.
        """
        if self._current_streak is not None:
            return self._current_streak
        await self._get_contribution_calendar()
        return self._current_streak or 0

    @property
    async def longest_streak(self) -> int:
        """
        Retrieves the longest contribution streak in days.

        :return: Maximum number of consecutive days with contributions.
        """
        if self._longest_streak is not None:
            return self._longest_streak
        await self._get_contribution_calendar()
        return self._longest_streak or 0

    @property
    async def current_streak_range(self) -> str:
        """
        Retrieves the date range of the current streak.

        :return: Formatted date range string.
        """
        if self._current_streak_range is not None:
            return self._current_streak_range
        await self._get_contribution_calendar()
        return self._current_streak_range or "No streak"

    @property
    async def longest_streak_range(self) -> str:
        """
        Retrieves the date range of the longest streak.

        :return: Formatted date range string.
        """
        if self._longest_streak_range is not None:
            return self._longest_streak_range
        await self._get_contribution_calendar()
        return self._longest_streak_range or "No streak"

    @property
    async def recent_contributions(self) -> list:
        """
        Retrieves the contribution counts for the last 10 days.

        :return: List of contribution counts (most recent last).
        """
        await self._get_contribution_calendar()
        days = self._contribution_calendar.get("days", [])
        recent = days[-10:] if len(days) >= 10 else days
        return [day.get("count", 0) for day in recent]
