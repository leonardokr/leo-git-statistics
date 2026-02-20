<p align="center">
  <img src="generated_images/samples/overview_sample_light.svg" alt="GitHub Stats Overview" />
</p>

<h1 align="center">Leo's Git Statistics</h1>

<p align="center">
  <strong>Generate beautiful, customizable SVG statistics cards for your GitHub profile</strong>
</p>

<p align="center">
  <a href="#features">Features</a> â€¢
  <a href="#themes">Themes</a> â€¢
  <a href="#quick-start">Quick Start</a> â€¢
  <a href="#configuration">Configuration</a> â€¢
  <a href="#architecture">Architecture</a>
</p>

---

## Entry Points

### CLI

| Entry point        | Description                        |
|--------------------|------------------------------------|
| `generate.py`      | Generates SVG cards from live data |
| `generate_test.py` | Generates SVG cards with mock data |

### API

| Entry point                  | Description                            |
|------------------------------|----------------------------------------|
| `api/`                       | Serves live stats + SVG cards via HTTP |
| `api/generate_static_api.py` | Generates JSON files + saves snapshot  |

### CI (Consumer Repository)

| Entry point                                                                     | Description                                                              |
| ---------------------------------------------------------------------------------| --------------------------------------------------------------------------|
| Consumer workflow (for example: `.github/workflows/update-static-api-data.yml`) | Scheduled job in the consuming repository that generates/saves snapshots |

### When to Use Each Mode

| Mode | Use when | Data source | Config source |
|---|---|---|---|
| `generate.py` | You want SVGs directly from GitHub APIs | Live GitHub API | `config.yml` (if you cloned the repo) or Action `config-overrides` (if you use a workflow) |
| `generate.py` + `STATIC_API_DATA_DIR` | You want SVGs from pre-generated JSON (no live API calls during render). Requires a workflow in the consumer repository to generate/update `api-data` first. | `api-data/users/{username}/*.json` | `config.yml` (if you cloned the repo) or Action `config-overrides` (if you use a workflow) |
| `generate_test.py` | You want sample/mock SVG output for testing templates/themes | Mock data in code | `config.yml` |
| `api/` (FastAPI) | You want HTTP endpoints/cards for external consumers | Live GitHub API | `config.yml` (generation settings) + server env/runtime scope rules |
| `api/generate_static_api.py` | You want to publish static JSON for GitHub Pages/CDN | Live GitHub API at generation time | `config.yml` (default or `CONFIG_PATH`) + optional `CONFIG_OVERRIDES` (script/workflow env) |

For card/stat generation settings, `config.yml` is the single base source.  
Overrides are explicit:
- Action: `with: config-overrides`
- Static API script: `CONFIG_OVERRIDES`

These are two override channels for two different entry points:
- `with: config-overrides` is consumed by the reusable GitHub Action (`uses: leonardokr/leo-git-statistics@v2`).
- `CONFIG_OVERRIDES` is consumed by the static JSON generator script (`api/generate_static_api.py`).
- In both cases, `config.yml` remains the base configuration and overrides are merged at runtime.
- In mixed workflows (generate JSON first, then render SVGs), both channels can appear in the same workflow:
  script step uses `CONFIG_OVERRIDES`, action step uses `with: config-overrides`.

Workflow example for this mode: [Option B: Static JSON Mode (requires 2 workflows)](#option-b-static-json-mode-requires-2-workflows)

### Snapshot Data Flow

A snapshot is a timestamped record of a user's GitHub statistics (stars, forks, followers, contributions, PRs, issues) saved to a SQLite database. Because GitHub does not provide historical data for most of these metrics, snapshots are the only way to track how they change over time. The stats history line chart is built entirely from these accumulated snapshots.

- **Writers:** `api/` (POST /history/snapshot), `api/generate_static_api.py`, consumer repository workflow (cron)
- **Readers:** `generate.py` (stats_history chart), `api/` (history endpoint + stats-history card)

## Features

- **Multiple Statistics Cards** - Overview stats, language distribution, contribution streaks, streak battery, language puzzle, weekly commit calendar, and stats history line chart
- **25+ Built-in Themes** - From Dracula to Nord, Catppuccin to Tokyo Night
- **Extensible Theme System** - Add your own themes via YAML files
- **Animated SVGs** - Smooth fade-in and slide animations
- **Fully Configurable** - Control which stats to show, filter repositories, and more
- **Reusable GitHub Action** - Run the generator from any repository (great for profile repos)
- **Historical Statistics Tracking** - Daily snapshots via GitHub Actions cron, with multi-series line chart visualization
- **Accumulated Metrics** - Track views and clones beyond GitHub's 14-day limit using SQLite with WAL mode
- **REST API** - FastAPI-based async API with JSON and SVG card endpoints, Swagger docs, caching (Redis or in-memory), rate limiting, API key auth, and Prometheus metrics
- **Production-Ready** - Docker/docker-compose deployment with gunicorn, Redis cache, structured logging, circuit breaker, and retry with exponential backoff

## Generated Cards

### Overview Statistics
Displays comprehensive GitHub statistics including contributions, repositories, stars, forks, and more.

<p align="center">
  <img src="generated_images/samples/overview_sample_dark.svg" alt="Overview Dark Mode" width="49%" />
  <img src="generated_images/samples/overview_sample_light.svg" alt="Overview Light Mode" width="49%" />
</p>

### Language Distribution
Shows your most used programming languages with an animated progress bar.

<p align="center">
  <img src="generated_images/samples/languages_sample_dark.svg" alt="Languages Dark Mode" width="49%" />
  <img src="generated_images/samples/languages_sample_light.svg" alt="Languages Light Mode" width="49%" />
</p>

### Contribution Streak
Tracks your current and longest contribution streaks.

<p align="center">
  <img src="generated_images/samples/streak_sample_dark.svg" alt="Streak Dark Mode" width="49%" />
  <img src="generated_images/samples/streak_sample_light.svg" alt="Streak Light Mode" width="49%" />
</p>

### Streak Battery
Visual battery indicator showing your streak progress with recent contribution history.

<p align="center">
  <img src="generated_images/samples/streak_battery_sample_dark.svg" alt="Streak Battery Dark Mode" width="49%" />
  <img src="generated_images/samples/streak_battery_sample_light.svg" alt="Streak Battery Light Mode" width="49%" />
</p>

### Language Puzzle
Treemap visualization of your programming languages - area proportional to usage percentage.

<p align="center">
  <img src="generated_images/samples/languages_puzzle_sample_dark.svg" alt="Language Puzzle Dark Mode" width="49%" />
  <img src="generated_images/samples/languages_puzzle_sample_light.svg" alt="Language Puzzle Light Mode" width="49%" />
</p>

### Weekly Commit Calendar
Agenda-style weekly calendar where each commit is a time block, with repositories separated by color.

<p align="center">
  <img src="generated_images/samples/commit_calendar_sample_dark.svg" alt="Commit Calendar Dark Mode" width="98%" />
</p>
<p align="center">
  <img src="generated_images/samples/commit_calendar_sample_light.svg" alt="Commit Calendar Light Mode" width="98%" />
</p>

### Stats History
Multi-series line chart showing how your stats (stars, followers, following, contributions, forks, PRs, issues) evolve over time. Requires historical snapshots collected via the daily cron workflow or `POST /history/snapshot`.

<p align="center">
  <img src="generated_images/samples/stats_history_sample_dark.svg" alt="Stats History Dark Mode" width="98%" />
</p>
<p align="center">
  <img src="generated_images/samples/stats_history_sample_light.svg" alt="Stats History Light Mode" width="98%" />
</p>

## Themes

Choose from **25+ built-in themes** or create your own:

| Category | Themes |
|----------|--------|
| **GitHub** | `default`, `light`, `dark`, `github_dimmed` |
| **Popular** | `dracula`, `nord`, `gruvbox`, `gruvbox_light`, `one_dark`, `monokai`, `tokyo_night`, `solarized_dark`, `solarized_light` |
| **Catppuccin** | `catppuccin_latte`, `catppuccin_frappe`, `catppuccin_macchiato`, `catppuccin_mocha` |
| **Material** | `palenight`, `material_darker`, `material_ocean`, `ayu`, `ayu_light`, `ayu_mirage` |
| **Creative** | `synthwave`, `cyberpunk`, `ocean`, `forest`, `sunset`, `midnight`, `aurora`, `neon`, `retro`, `lavender`, `rose_pine`, `rose_pine_dawn` |

### Theme Previews

<details>
<summary><b>Dracula</b></summary>
<div align="center">
<img src="generated_images/samples/overview_sample_dracula.svg" alt="Dracula Theme" width="49%" />
</div>
<div align="center">
<img src="generated_images/samples/streak_sample_dracula.svg" alt="Dracula Theme" width="49%" />
<img src="generated_images/samples/streak_battery_sample_dracula.svg" alt="Dracula Theme" width="49%" />
<img src="generated_images/samples/languages_sample_dracula.svg" alt="Dracula Theme" width="49%" />
<img src="generated_images/samples/languages_puzzle_sample_dracula.svg" alt="Dracula Theme" width="49%" />
<img src="generated_images/samples/commit_calendar_sample_dracula.svg" alt="Dracula Theme" width="98%" />
<img src="generated_images/samples/stats_history_sample_dracula.svg" alt="Dracula Theme" width="98%" />
</div>
</details>

<details>
<summary><b>Nord</b></summary>
<div align="center">
<img src="generated_images/samples/overview_sample_nord.svg" alt="Nord Theme" width="49%" />
</div>
<div align="center">
<img src="generated_images/samples/streak_sample_nord.svg" alt="Nord Theme" width="49%" />
<img src="generated_images/samples/streak_battery_sample_nord.svg" alt="Nord Theme" width="49%" />
<img src="generated_images/samples/languages_sample_nord.svg" alt="Nord Theme" width="49%" />
<img src="generated_images/samples/languages_puzzle_sample_nord.svg" alt="Nord Theme" width="49%" />
<img src="generated_images/samples/commit_calendar_sample_nord.svg" alt="Nord Theme" width="98%" />
<img src="generated_images/samples/stats_history_sample_nord.svg" alt="Nord Theme" width="98%" />
</div>
</details>

<details>
<summary><b>Tokyo Night</b></summary>
<div align="center">
<img src="generated_images/samples/overview_sample_tokyo_night.svg" alt="Tokyo Night Theme" width="49%" />
</div>
<div align="center">
<img src="generated_images/samples/streak_sample_tokyo_night.svg" alt="Tokyo Night Theme" width="49%" />
<img src="generated_images/samples/streak_battery_sample_tokyo_night.svg" alt="Tokyo Night Theme" width="49%" />
<img src="generated_images/samples/languages_sample_tokyo_night.svg" alt="Tokyo Night Theme" width="49%" />
<img src="generated_images/samples/languages_puzzle_sample_tokyo_night.svg" alt="Tokyo Night Theme" width="49%" />
<img src="generated_images/samples/commit_calendar_sample_tokyo_night.svg" alt="Tokyo Night Theme" width="98%" />
<img src="generated_images/samples/stats_history_sample_tokyo_night.svg" alt="Tokyo Night Theme" width="98%" />
</div>
</details>

<details>
<summary><b>Catppuccin Mocha</b></summary>
<div align="center">
<img src="generated_images/samples/overview_sample_catppuccin_mocha.svg" alt="Catppuccin Mocha Theme" width="49%" />
</div>
<div align="center">
<img src="generated_images/samples/streak_sample_catppuccin_mocha.svg" alt="Catppuccin Mocha Theme" width="49%" />
<img src="generated_images/samples/streak_battery_sample_catppuccin_mocha.svg" alt="Catppuccin Mocha Theme" width="49%" />
<img src="generated_images/samples/languages_sample_catppuccin_mocha.svg" alt="Catppuccin Mocha Theme" width="49%" />
<img src="generated_images/samples/languages_puzzle_sample_catppuccin_mocha.svg" alt="Catppuccin Mocha Theme" width="49%" />
<img src="generated_images/samples/commit_calendar_sample_catppuccin_mocha.svg" alt="Catppuccin Mocha Theme" width="98%" />
<img src="generated_images/samples/stats_history_sample_catppuccin_mocha.svg" alt="Catppuccin Mocha Theme" width="98%" />
</div>
</details>

## Quick Start

### 1. Choose Mode
Pick the mode that matches your goal in **When to Use Each Mode** above.
- For profile card generation, use the reusable action (`uses: leonardokr/leo-git-statistics@v2`).
- For static JSON + SVG render (no live API calls during render), use a consumer workflow with two steps: `api/generate_static_api.py` then the reusable action with [`static-api-data-dir`](#generate-svgs-from-static-json-offline-render-mode).
- For source-level customization, clone/template this repository.

### 2. Create a Personal Access Token
1. Go to **Settings** -> **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**
2. Generate a new token with scopes: `repo`, `read:user`, `read:org`
3. Copy the token

### 3. Add Secret in Profile Repository
1. In your profile repository (`<username>/<username>`): **Settings** -> **Secrets and variables** -> **Actions**
2. Create secret named `PROFILE_STATS_TOKEN` with your token

Then continue with the mode-specific sections below:
- **Consumer Workflow Examples (Reusable Action)**
- **Repository Configuration (Clone/Template Mode)**
- **REST API (Hosted Service Mode)**


## Consumer Workflow Examples (Reusable Action)

Use this mode when you do not want to maintain this codebase and only need workflows in your profile/consumer repository to generate cards.
<details>
<summary><b>Expand Action Workflows (Live API and Static JSON Render)</b></summary>

Use this repository as an Action in your profile repository.

Required secret:
- `PROFILE_STATS_TOKEN`: token used by `generate.py` to query GitHub APIs.

### Option A (Independent): Cards Only (Live GitHub API)

This mode calls the GitHub API directly during card generation (not the `leo-git-statistics` REST API).

```yaml
name: Update Profile SVG Stats

on:
  schedule:
    - cron: "0 */12 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout profile repository
        uses: actions/checkout@v4

      - name: Generate SVGs via leo-git-statistics action
        uses: leonardokr/leo-git-statistics@v2
        with:
          github-token: ${{ secrets.PROFILE_STATS_TOKEN }}
          github-username: leonardokr
          output-dir: profile
          config-path: config.yml
          config-overrides: |
            timezone: America/Sao_Paulo
            themes:
              enabled: [dark, light]
            stats_generation:
              exclude_contrib_repos: "true"
              mask_private_repos: "true"

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add profile/*.svg
          if ! git diff --quiet --staged; then
            git commit -m "chore(stats): update profile SVG stats"
            git push
          fi
```

### Option B: Static JSON Mode (requires 2 workflows)

Use this mode when you want cards rendered from pre-generated JSON instead of live GitHub API calls during render.
You must have two steps in your automation:
- `Workflow B1`: generate/update static JSON data.
- `Workflow B2`: render cards from that JSON data.

They do not need to run at the same schedule.
You can run B1 and B2 as separate workflows with different intervals (for example, data every 30 minutes and cards every 6 hours), or combine both in a single workflow with two steps/jobs.

If you run only B1, you will have JSON files but no updated cards.
If you run only B2 without existing JSON, card rendering from static data will fail/produce nothing.

#### Workflow B1: Generate Static Data (`api-data`)

```yaml
name: Update static API data

on:
  schedule:
    - cron: "30 0 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Checkout leo-git-statistics source
        uses: actions/checkout@v4
        with:
          repository: leonardokr/leo-git-statistics
          ref: v2
          path: leo-git-statistics

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: |
          python -m pip install --upgrade pip
          pip install -r leo-git-statistics/requirements.txt

      - name: Generate static API JSON files
        env:
          GITHUB_TOKEN: ${{ secrets.PROFILE_STATS_TOKEN }}
          GITHUB_ACTOR: ${{ github.repository_owner }}
          SNAPSHOTS_DB_PATH: ${{ github.workspace }}/api-data/snapshots.db
          CONFIG_OVERRIDES: |
            timezone: America/Sao_Paulo
            stats_generation:
              exclude_contrib_repos: "true"
              mask_private_repos: "true"
        run: python leo-git-statistics/api/generate_static_api.py

      - run: |
          git add api-data
          git commit -m "Update static API data" || exit 0
          git push
```

#### Workflow B2: Render Cards from Static Data

This workflow consumes the JSON generated by Workflow B1 (no live GitHub API calls during render).

```yaml
name: Render cards from static API data

on:
  schedule:
    - cron: "0 */6 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate SVGs from static JSON
        uses: leonardokr/leo-git-statistics@v2
        with:
          github-token: ${{ secrets.PROFILE_STATS_TOKEN }}
          github-username: leonardokr
          output-dir: profile
          config-path: config.yml
          static-api-data-dir: api-data
          config-overrides: |
            timezone: America/Sao_Paulo
            themes:
              enabled: [dark, light]
            stats_generation:
              mask_private_repos: "true"

      - run: |
          git add profile/*.svg
          git commit -m "Update profile SVG stats from static data" || exit 0
          git push
```

Under the hood, this maps to env `STATIC_API_DATA_DIR` in the action runtime.
Option A is independent and generates cards directly from the GitHub API.

### Action Inputs (`with:`)

| Input                 | Required | Default            | Description                                                                  |
| -----------------------| ----------| --------------------| ------------------------------------------------------------------------------|
| `github-token`        | Yes      | -                  | GitHub token consumed as `ACCESS_TOKEN`.                                     |
| `github-username`     | No       | `github.actor`     | GitHub user to collect stats for.                                            |
| `python-version`      | No       | `3.11`             | Python runtime version.                                                      |
| `output-dir`          | No       | `generated_images` | Destination folder in caller repository.                                     |
| `config-path`         | No       | `config.yml`       | Path to the config file in caller repository.                                |
| `config-overrides`    | No       | -                  | YAML fragment merged into config at runtime.                                 |
| `static-api-data-dir` | No       | -                  | Static JSON root path (example: `api-data`) to enable `STATIC_API_DATA_DIR`. |

### Action Override Reference (`config-overrides`)

This section applies to any workflow that calls the reusable action (`uses: leonardokr/leo-git-statistics@v2`), including:
- Option A (live GitHub API cards)
- Option B / Workflow B2 (render cards from static JSON)

It does not apply to Workflow B1 (`api/generate_static_api.py`), which uses `CONFIG_OVERRIDES` env instead.

In action-based workflows, you can configure behavior with:
- `with: config-path` (read a config file from the caller repository, optional)
- `with: config-overrides` (inline YAML overrides)

If `config-path` does not exist in the caller repository, the action uses its bundled `config.yml` as base and then applies `config-overrides`.

### Supported `config-overrides` Keys

```yaml
timezone:
themes:
  enabled:

stats_generation:
  excluded_repos:
  excluded_langs:
  include_forked_repos:
  exclude_contrib_repos:
  exclude_archive_repos:
  exclude_private_repos:
  exclude_public_repos:
  mask_private_repos:
  store_repo_views:
  store_repo_clones:
  more_collabs:
  manually_added_repos:
  only_included_repos:
  show_total_contributions:
  show_repositories:
  show_lines_changed:
  show_avg_percent:
  show_collaborators:
  show_contributors:
  show_views:
  show_clones:
  show_forks:
  show_stars:
  show_pull_requests:
  show_issues:
```

</details>

## Repository Configuration (Clone/Template Mode)

Use this mode when you cloned/template this repository and want to run/modify generation locally in this codebase (including templates and source code).
<details>
<summary><b>Expand config.yml Setup for Cloned/Template Repositories</b></summary>

Use this section only if you cloned this repository (or used it as a template) and will run scripts from this codebase directly.

### Clone/Template Example Workflow

```yaml
name: Generate cards from cloned repo

on:
  schedule:
    - cron: "0 */6 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - env:
          ACCESS_TOKEN: ${{ secrets.PROFILE_STATS_TOKEN }}
          GITHUB_ACTOR: ${{ github.repository_owner }}
        run: python generate.py
      - run: |
          git add generated_images/*.svg
          git commit -m "Update cards" || exit 0
          git push
```

### Theme Selection

```yaml
themes:
  enabled:
    - default
    - dark
    - dracula
    - nord
    # Use 'all' to generate all themes
```

### Repository Filters

```yaml
stats_generation:
  excluded_repos: "repo1,repo2"
  excluded_langs: "HTML,CSS"
  include_forked_repos: "false"
  mask_private_repos: "true"
  exclude_private_repos: "false"
  exclude_archive_repos: "true"
```

### Statistics Visibility

```yaml
stats_generation:
  show_total_contributions: "true"
  show_repositories: "true"
  show_lines_changed: "true"
  show_stars: "true"
  show_pull_requests: "true"
  # ... more options
```

</details>

## REST API (Hosted Service Mode)

This project provides a **FastAPI-based async REST API** that exposes statistics as JSON and SVG cards. Built for production with caching, authentication, rate limiting, structured logging, and Prometheus metrics.

> **Note:** The API requires backend hosting (Docker, Render, Railway, etc.) and cannot run on GitHub Pages. For static sites, use the workflow mode in [Consumer Workflow Examples (Reusable Action)](#consumer-workflow-examples-reusable-action), especially [Option B: Static JSON Mode (requires 2 workflows)](#option-b-static-json-mode-requires-2-workflows).

<details>
<summary><b>Click to view API Documentation</b></summary>

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (see api/.env.example)
export GITHUB_TOKEN=your_token_here

# 3. Run the API (development)
uvicorn api.main:app --reload --port 8000

# 4. Access interactive docs at http://localhost:8000/docs
```

### Endpoints

#### Statistics (JSON)

| Endpoint | Description |
|---|---|
| `GET /v1/users/{username}/overview` | Overview statistics (contributions, stars, forks, lines changed) |
| `GET /v1/users/{username}/languages` | Language distribution |
| `GET /v1/users/{username}/repositories` | Repository list (names only, paginated) |
| `GET /v1/users/{username}/repositories/detailed` | Detailed repository info (paginated) |
| `GET /v1/users/{username}/streak` | Contribution streak data |
| `GET /v1/users/{username}/commits/weekly` | Weekly commit schedule |
| `GET /v1/users/{username}/contributions/recent` | Recent contribution activity |
| `GET /v1/users/{username}/stats/full` | All data in one request |

#### SVG Cards

| Endpoint | Description |
|---|---|
| `GET /v1/users/{username}/cards/themes` | List available card themes |
| `GET /v1/users/{username}/cards/overview?theme=dracula` | Overview SVG card |
| `GET /v1/users/{username}/cards/languages?theme=dark` | Language distribution SVG card |
| `GET /v1/users/{username}/cards/streak?theme=nord` | Contribution streak SVG card |
| `GET /v1/users/{username}/cards/streak-battery?theme=tokyo_night` | Streak battery SVG card |
| `GET /v1/users/{username}/cards/languages-puzzle?theme=catppuccin_mocha` | Language puzzle SVG card |
| `GET /v1/users/{username}/cards/commit-calendar?theme=dracula` | Commit calendar SVG card |
| `GET /v1/users/{username}/cards/stats-history?theme=dracula` | Historical stats SVG card |

SVG cards can be embedded directly in Markdown:
```markdown
![Stats](https://your-api.example.com/v1/users/leonardokr/cards/overview?theme=dracula)
```

#### Comparison, History & Webhooks

| Endpoint | Description |
|---|---|
| `GET /v1/users/{username}/compare/{other}` | Side-by-side user comparison |
| `GET /v1/users/{username}/history` | Historical stats snapshots |
| `POST /v1/users/{username}/webhooks` | Register a webhook for stat changes |
| `GET /v1/users/{username}/webhooks` | List registered webhooks |
| `DELETE /v1/users/{username}/webhooks/{id}` | Remove a webhook |

#### Webhook Conditions

`POST /v1/users/{username}/webhooks` supports these condition keys:

| Key | Type | Trigger |
|---|---|---|
| `stars_threshold` | `int` | Fires when `total_stars` crosses the threshold upward |
| `streak_broken` | `bool` | Fires when `current_streak` drops from `> 0` to `0` |
| `contributions_record` | `bool` | Fires when `total_contributions` becomes greater than previous snapshot |

Example:

```json
{
  "url": "https://example.com/hooks/stats",
  "conditions": {
    "stars_threshold": 500,
    "streak_broken": true,
    "contributions_record": true
  }
}
```

#### Infrastructure

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /metrics` | Prometheus metrics |
| `GET /docs` | Interactive Swagger documentation |

### Query Parameters

Endpoints that return repository lists support filtering and pagination:

| Parameter | Default | Description |
|---|---|---|
| `page` | `1` | Page number |
| `per_page` | `30` | Items per page (max 100) |
| `visibility` | `all` | `public`, `private`, or `all` |
| `sort` | `stars` | `stars`, `forks`, `updated`, or `name` |
| `limit` | `100` | Max repositories to return (1-500) |
| `exclude_forks` | `false` | Exclude forked repositories |
| `exclude_archived` | `false` | Exclude archived repositories |
| `no_cache` | `false` | Bypass cache and fetch fresh data |

### Example Response

```bash
curl http://localhost:8000/v1/users/leonardokr/overview
```

```json
{
  "username": "leonardokr",
  "name": "Leonardo Klein",
  "total_contributions": 1250,
  "repositories_count": 42,
  "total_stars": 320,
  "total_forks": 45,
  "lines_added": 45230,
  "lines_deleted": 12340,
  "avg_contribution_percent": "68.50%"
}
```

### Security

- **API Key Authentication** - Protect API routes with `Authorization: Bearer <key>`. Enable with `API_AUTH_ENABLED=true` and `API_KEYS`. Public endpoints remain available: `/health`, `/docs`, and `/metrics`.
- **Private Repo Isolation** - Server-token requests always exclude private repositories, preventing accidental private data exposure.
- **User Token Support** - Clients may send `X-GitHub-Token` to use their own GitHub token. The API verifies token ownership against `{username}` before enabling private-repo access.
- **Rate Limiting** - slowapi limits requests by API key (authenticated) or IP (anonymous). Configure with `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_AUTH`, and `RATE_LIMIT_HEAVY`.
- **Input Validation** - Request payloads and query/path parameters are validated with Pydantic. Usernames are validated against GitHub username rules.
- **Webhook Delivery Note** - Outbound webhook callbacks are currently unsigned (no HMAC signature header yet). Protect webhook receivers with your own validation controls (tokenized URL, allowlist, or proxy checks).

### Caching

Responses are cached with configurable TTL (`CACHE_TTL`, default `300` seconds / 5 minutes). Two backends are available:

- **In-memory** (`TTLCache`) - Default, no configuration needed. Lost on restart.
- **Redis** - Set `REDIS_URL=redis://localhost:6379/0`. Shared across workers, survives restarts.

Cache status is returned via `X-Cache: HIT/MISS` response header.

### Resilience

- **Retry with Exponential Backoff** - Automatic retries (up to 3 attempts) via tenacity for rate-limit errors, `aiohttp` client/server timeout errors, and GitHub `5xx` responses.
- **Circuit Breaker** - Fails fast when GitHub API is down (opens after 5 consecutive failures, resets after 30s) via pybreaker.
- **GitHub Rate Limit Monitoring** - Tracks `X-RateLimit-*` headers, logs warnings when low, and may pause briefly when remaining quota is critical.
- **Partial Responses** - If a collector fails, the response still includes successful sections plus a `warnings` field describing degraded parts.

### Deployment

#### Docker (Recommended)

```bash
# 1. Configure environment
cp api/.env.example api/.env
# Edit api/.env with your GITHUB_TOKEN

# 2. Run with docker-compose (API + Redis)
docker-compose up -d

# API available at http://localhost:8000
```

The `docker-compose.yml` includes the API service with gunicorn (4 workers) and a Redis cache.

#### Manual

```bash
# Production server
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Cloud Platforms

**Render:**
1. New -> Web Service -> Connect GitHub repo
2. Build: `pip install -r requirements.txt`
3. Start: `gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
4. Environment variable: `GITHUB_TOKEN=your_token`

**Other options:** Railway, Fly.io, any platform supporting Docker.

> Static-site JSON generation (GitHub Pages/CDN) is documented in [Consumer Workflow Examples (Reusable Action)](#consumer-workflow-examples-reusable-action), under **Option B: Static JSON Mode (requires 2 workflows)**.

### Portfolio Integration Example

Use the API from any platform that can make HTTP requests (frontend, backend, CI, mobile, etc.).
Example in Python:

```python
import requests

url = "https://your-api.example.com/v1/users/leonardokr/repositories/detailed"
response = requests.get(url, timeout=20)
response.raise_for_status()

payload = response.json()
for repo in payload.get("data", []):
    print(repo["name"], repo.get("stars"))
```

### Environment Variables

Create `api/.env` file (see `api/.env.example`).

What each variable is for and why it matters:

- **`GITHUB_TOKEN` / `ACCESS_TOKEN`**
  Used by the backend to call GitHub APIs. Without one of these, the API cannot collect stats.
  `GITHUB_TOKEN` is preferred; `ACCESS_TOKEN` is fallback.
- **`PORT`**
  HTTP port exposed by the API server. Change it to match your hosting/runtime requirements.
- **`WORKERS`**
  Number of API worker processes (used by gunicorn). Increase for more concurrency, at higher memory cost.
- **`API_AUTH_ENABLED` + `API_KEYS`**
  Enables API key protection for `/v1/*` endpoints. Use this when your API should not be publicly callable.
- **`CORS_ORIGINS`**
  Browser allowlist for cross-origin requests. Use specific origins in production; keep `*` only for development/testing.
- **`RATE_LIMIT_DEFAULT`, `RATE_LIMIT_AUTH`, `RATE_LIMIT_HEAVY`**
  Protects the service from abuse and accidental overload. Limits use slowapi format like `30/minute`, `100/hour`, `1000/day`.
- **`REDIS_URL`**
  Enables shared cache across workers/instances. Recommended for production; if omitted, cache is in-memory per process.
- **`CACHE_TTL`**
  How long cached responses live (seconds). Higher TTL reduces GitHub API calls but increases staleness.
- **`CACHE_MAXSIZE`**
  Max entries for in-memory cache backend. Tune based on memory budget and traffic.
- **`DATABASE_PATH`, `SNAPSHOTS_DB_PATH`, `WEBHOOKS_DB_PATH`**
  File paths for SQLite databases (traffic, snapshots/history, webhooks). Override when you need custom storage layout.

Example:

```bash
# Required
GITHUB_TOKEN=your_github_personal_access_token
# or ACCESS_TOKEN=your_github_personal_access_token

# Server
PORT=8000
WORKERS=4

# Security
API_AUTH_ENABLED=false
API_KEYS=
CORS_ORIGINS=*

# Rate limiting
RATE_LIMIT_DEFAULT=30/minute
RATE_LIMIT_AUTH=100/minute
RATE_LIMIT_HEAVY=10/minute

# Cache
# Optional (if omitted, in-memory cache is used)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
CACHE_MAXSIZE=100

# Database
# Optional (defaults are used when omitted)
DATABASE_PATH=src/db/traffic.db
SNAPSHOTS_DB_PATH=src/db/snapshots.db
WEBHOOKS_DB_PATH=src/db/webhooks.db
```

<details>
<summary><b>Rate Limit Configuration Guide</b></summary>

`RATE_LIMIT_DEFAULT`
- Applied to standard endpoints (most `/v1/users/*` and `/v1/users/{username}/cards/*` routes).
- Example: `RATE_LIMIT_DEFAULT=60/minute` allows up to 60 requests per minute per client key.

`RATE_LIMIT_HEAVY`
- Applied to expensive endpoints (for example compare, full stats, and force snapshot routes).
- Example: `RATE_LIMIT_HEAVY=5/minute` protects GitHub quota on heavier operations.

`RATE_LIMIT_AUTH`
- Configured in middleware and available for authenticated-tier policies.
- Keep it defined for future/extended routing policies.

Result in practice:
- Lower values: better abuse protection, stricter throttling.
- Higher values: more throughput, higher load and GitHub API consumption risk.
</details>

<details>
<summary><b>API Authentication Configuration Guide</b></summary>

`API_AUTH_ENABLED`
- `false` (default): API routes under `/v1/*` are publicly accessible.
- `true`: `/v1/*` routes require `Authorization: Bearer <api_key>`.

`API_KEYS`
- Comma-separated list of accepted API keys.
- Example: `API_KEYS=key_prod_1,key_internal_2`

How to call:
- Header format: `Authorization: Bearer key_prod_1`

What stays public even with auth enabled:
- `/health`
- `/docs`
- `/metrics`

Result in practice:
- `API_AUTH_ENABLED=false`: simpler public access, higher abuse risk.
- `API_AUTH_ENABLED=true` + strong keys: controlled access and safer public deployments.

If `API_AUTH_ENABLED=true` and `API_KEYS` is empty, protected routes return server error (`500`) until keys are configured.
</details>

<details>
<summary><b>CORS Configuration Guide</b></summary>

CORS accepts all origins by default (`CORS_ORIGINS=*`).

For production, set an explicit comma-separated allowlist:

```bash
CORS_ORIGINS=https://leonardokr.github.io,https://myportfolio.com
```

Do not include spaces between origins.

Result in practice:
- `*`: easiest setup, least restrictive.
- Explicit allowlist: safer browser access control for production.
</details>

</details>



## Versioning and Releases

This repository uses automated releases with `release-please` on `main`.

- Create changes in branches and merge with Conventional Commits.
- `release-please` opens/updates a release PR with changelog entries.
- When the release PR is merged, it creates a GitHub Release and a semver tag (`v1.2.3`).
- The workflow also updates the floating major tag (`v1`, `v2`, ...) and the `latest` tag to the newest release.

For consumers:

- Use `@v2` for stable major updates with automatic minor/patch refreshes.
- Use `@latest` to always track the newest release regardless of major version (may include breaking changes).
- Pin exact versions (`@v2.0.3`) only when strict reproducibility is required.
## Creating Custom Themes

Add a new `.yml` file in `src/themes/`:

```yaml
# src/themes/my_theme.yml
my_awesome_theme:
  suffix: "MyAwesome"
  colors:
    bg_color: "#1a1b26"
    title_color: "#7aa2f7"
    text_color: "#a9b1d6"
    icon_color: "#bb9af7"
    percent_color: "#565f89"
    border_color: "#292e42"
    accent_color: "#9ece6a"
    gradient_start: "#7aa2f7"
    gradient_end: "#bb9af7"
```

The example above is a minimal theme. Missing keys are auto-filled from defaults in `src/themes/loader.py`.

If you want full control over all cards, also define these optional groups:

```yaml
my_awesome_theme:
  suffix: "MyAwesome"
  colors:
    # Commit calendar card
    calendar_title_color: "#7aa2f7"
    calendar_subtitle_color: "#565f89"
    calendar_day_label_color: "#a9b1d6"
    calendar_hour_label_color: "#565f89"
    calendar_grid_color: "#292e42"
    calendar_grid_opacity: 0.55
    calendar_legend_text_color: "#a9b1d6"
    calendar_slot_opacity: 0.95
    calendar_hue: 220
    calendar_saturation_range: [60, 85]
    calendar_lightness_range: [40, 60]
    calendar_hue_spread: 90

    # Languages puzzle card
    puzzle_hue: 210
    puzzle_saturation_range: [60, 85]
    puzzle_lightness_range: [35, 65]
    puzzle_hue_spread: 80
    puzzle_text_color: "#FFFFFF"
    puzzle_gap: 2

    # Stats history card
    line_chart_title_color: "#7aa2f7"
    line_chart_subtitle_color: "#565f89"
    line_chart_axis_color: "#565f89"
    line_chart_grid_color: "#292e42"
    line_chart_grid_opacity: 0.3
    line_chart_legend_text_color: "#a9b1d6"
    line_chart_hue: 220
    line_chart_saturation_range: [60, 85]
    line_chart_lightness_range: [40, 65]
    line_chart_hue_spread: 120
```

Use `src/themes/github.yml` as a full reference theme with all currently supported keys.

Then enable it in `config.yml`:

```yaml
themes:
  enabled:
    - my_awesome_theme
```

## Architecture

```text
.
|- generate.py / generate_test.py       # CLI entrypoints for SVG generation
|- api/
|  |- main.py                           # FastAPI app bootstrap
|  |- generate_static_api.py            # Static JSON exporter (api-data)
|  |- routes/                           # HTTP endpoints (users, cards, compare, history, webhooks, health)
|  |- services/                         # API service layer (collector wiring, rendering, notifications)
|  |- deps/                             # auth/cache/token/session dependencies
|  |- middleware/                       # logging, metrics, rate limiting
|  `- models/                           # request/response schemas
|- src/
|  |- core/                             # GitHub collection and domain orchestration
|  |- generators/                       # SVG generators (overview, languages, streak, calendar, history)
|  |- presentation/                     # SVG template rendering and visual algorithms
|  |- themes/                           # YAML theme definitions + loader
|  |- db/                               # SQLite stores (traffic, snapshots, webhooks)
|  `- utils/                            # shared helpers (privacy, filesystem, decorators)
|- test/                                # API/core/load tests
`- config.yml                           # base generation configuration
```

### Key Design Decisions

- **Collection and delivery are separated**: `src/core` handles GitHub data collection; `api/` handles HTTP concerns and exposes JSON/SVG.
- **Collector facade**: `StatsCollector` aggregates specialized collectors (repos, streak, commits, traffic, engagement, code changes) behind one interface.
- **Generator registry**: SVG generators register via `register_generator`, so orchestration does not depend on hardcoded generator lists.
- **Async GitHub client with resilience**: `GitHubClient` combines controlled concurrency, retry/backoff, and circuit breaker behavior.
- **Privacy controls are explicit**: repository filtering and masking are built into collectors/responses; API token scope restricts private data exposure.
- **Partial failure model**: API endpoints can return successful sections plus `warnings` when some collectors fail.
- **Pluggable runtime dependencies**: in-memory cache and local SQLite work by default; Redis and custom DB paths are optional via env.

## Development

### Prerequisites
- Python 3.11+
- pip
- Docker (optional, for containerized deployment)

### Setup

```bash
# Production dependencies
pip install -r requirements.txt

# Development/test dependencies (includes httpx, aioresponses, locust)
pip install -r requirements-dev.txt
```

### Running Locally

#### SVG Generation with Mock Data (Local)

Use `generate_test.py` when you want to validate templates/themes locally without GitHub API calls, token setup, or rate-limit impact.

```bash
python generate_test.py
```

#### API Development Server

```bash
export GITHUB_TOKEN="your_github_token"
uvicorn api.main:app --reload --port 8000
```

#### API with Docker

```bash
cp api/.env.example api/.env
# Edit api/.env with your GITHUB_TOKEN
docker-compose up -d
```

### Running Tests

```bash
# All tests
pytest test/

# API integration tests only
pytest test/api/

# Async collector tests only
pytest test/core/

# Load tests (requires running API)
locust -f test/load/locustfile.py --host http://localhost:8000
```

## Contributing

Contributions are welcome! Feel free to:

- Add new themes
- Improve SVG templates
- Add new statistics
- Fix bugs
- Improve documentation

## License

See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <sub>Built with Python, FastAPI, and GitHub Actions</sub>
</p>






