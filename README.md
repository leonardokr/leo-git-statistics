<p align="center">
  <img src="generated_images/samples/overview_sample_light.svg" alt="GitHub Stats Overview" />
</p>

<h1 align="center">Leo's Git Statistics</h1>

<p align="center">
  <strong>Generate beautiful, customizable SVG statistics cards for your GitHub profile</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#themes">Themes</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## Entry Points

| Entry point | Description | Reads snapshots? | Writes snapshots? |
|---|---|---|---|
| `generate.py` | Generates SVG cards (including stats history) | Yes (for stats_history chart) | No |
| `generate_test.py` | Generates SVG cards with mock data | No (mock returns fake history) | No |
| `api/` | Serves live stats + SVG cards via HTTP | Yes (for history endpoint + stats-history card) | Yes (POST /history/snapshot) |
| `api/generate_static_api.py` | Generates JSON files + saves snapshot | No | Yes |
| `.github/workflows/snapshot.yml` | Daily cron job that saves a stats snapshot | No | Yes |

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
</div>
</details>

## Quick Start

### 1. Choose How You Want to Use It
- Recommended: call this repository as a reusable GitHub Action from your profile repository.
- Use **Use this template** only when you need advanced customization not exposed by action inputs (for example: editing generators, templates, themes source files, architecture, or custom business rules).

### 2. Create a Personal Access Token
1. Go to **Settings** -> **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**
2. Generate a new token with scopes: `repo`, `read:user`, `read:org`
3. Copy the token

### 3. Add Repository Secret
1. In your profile repository (`<username>/<username>`): **Settings** -> **Secrets and variables** -> **Actions**
2. Create secret named `PROFILE_STATS_TOKEN` with your token

### 4. Add a Workflow in Your Profile Repository
Use this action from your profile repository workflow:

```yaml
- name: Generate profile SVG stats
  uses: leonardokr/leo-git-statistics@v1
  with:
    github-token: ${{ secrets.PROFILE_STATS_TOKEN }}
    github-username: leonardokr
    output-dir: profile
```

### 5. Configure (Optional)
Pass optional `with:` inputs in your profile workflow (see full list below in **Workflow Configuration (Profile Repository)**).

## Workflow Configuration (Profile Repository)

Use this repository as an Action in your profile repository. This is the recommended path for most users.

Required secret in your profile repository:

- `PROFILE_STATS_TOKEN`: token used by `generate.py` to query GitHub APIs.

### Example Workflow (profile repository)

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
        uses: leonardokr/leo-git-statistics@v1
        with:
          github-token: ${{ secrets.PROFILE_STATS_TOKEN }}
          github-username: leonardokr
          output-dir: profile
          themes: dark,light
          excluded-repos: owner/repo1,owner/repo2
          exclude-archive-repos: "true"
          show-stars: "true"
          show-issues: "false"

      - name: Keep README-friendly filenames
        run: |
          cp profile/overviewdark.svg profile/stats.svg
          cp profile/languagesdark.svg profile/top-langs.svg

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

### Action Inputs (`with:`)

| Input                      | Required | Default                    | Description                                              |
| ----------------------------| ----------| ----------------------------| ----------------------------------------------------------|
| `github-token`             | Yes      | -                          | GitHub token consumed as `ACCESS_TOKEN`.                 |
| `github-username`          | No       | `github.actor`             | GitHub user to collect stats for.                        |
| `python-version`           | No       | `3.11`                     | Python runtime version.                                  |
| `output-dir`               | No       | `generated_images`         | Destination folder in caller repository.                 |
| `themes`                   | No       | from `config.yml`          | Comma-separated themes (example: `dark,light`) or `all`. |
| `timezone`                 | No       | from `config.yml` or `UTC` | IANA timezone (example: `America/Sao_Paulo`).            |
| `excluded-repos`           | No       | from `config.yml`          | Comma-separated repos to exclude.                        |
| `excluded-langs`           | No       | from `config.yml`          | Comma-separated languages to exclude.                    |
| `include-forked-repos`     | No       | from `config.yml`          | `true` or `false`.                                       |
| `exclude-contrib-repos`    | No       | from `config.yml`          | `true` or `false`.                                       |
| `exclude-archive-repos`    | No       | from `config.yml`          | `true` or `false`.                                       |
| `exclude-private-repos`    | No       | from `config.yml`          | `true` or `false`.                                       |
| `exclude-public-repos`     | No       | from `config.yml`          | `true` or `false`.                                       |
| `store-repo-views`         | No       | from `config.yml`          | `true` or `false`.                                       |
| `store-repo-clones`        | No       | from `config.yml`          | `true` or `false`.                                       |
| `more-collabs`             | No       | from `config.yml`          | Integer to manually add collaborator count.              |
| `manually-added-repos`     | No       | from `config.yml`          | Comma-separated `owner/repo` list to include.            |
| `only-included-repos`      | No       | from `config.yml`          | If set, only these `owner/repo` entries are used.        |
| `show-total-contributions` | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-repositories`        | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-lines-changed`       | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-avg-percent`         | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-collaborators`       | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-contributors`        | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-views`               | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-clones`              | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-forks`               | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-stars`               | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-pull-requests`       | No       | from `config.yml`          | `true` or `false`.                                       |
| `show-issues`              | No       | from `config.yml`          | `true` or `false`.                                       |

## Repository Configuration (config.yml)

This section is for repository-level configuration in `config.yml` (mainly for template/advanced customization). For normal usage via Action, prefer workflow `with:` inputs shown below.

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

## Versioning and Releases

This repository uses automated releases with `release-please` on `main`.

- Create changes in branches and merge with Conventional Commits.
- `release-please` opens/updates a release PR with changelog entries.
- When the release PR is merged, it creates a GitHub Release and a semver tag (`v1.2.3`).
- The workflow also updates the floating major tag (`v1`, `v2`, ...) to the latest patch/minor of that major.

For consumers:

- Use `@v1` for stable major updates with automatic minor/patch refreshes.
- Pin exact versions (`@v1.2.3`) only when strict reproducibility is required.
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

Then enable it in `config.yml`:

```yaml
themes:
  enabled:
    - my_awesome_theme
```

## REST API

This project provides a **FastAPI-based async REST API** that exposes statistics as JSON and SVG cards. Built for production with caching, authentication, rate limiting, structured logging, and Prometheus metrics.

> **Note:** The API requires backend hosting (Docker, Render, Railway, etc.). It cannot run on GitHub Pages. For static sites, see the static JSON generation option below.

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
| `GET /users/{username}/overview` | Overview statistics (contributions, stars, forks, lines changed) |
| `GET /users/{username}/languages` | Language distribution |
| `GET /users/{username}/repositories` | Repository list (names only, paginated) |
| `GET /users/{username}/repositories/detailed` | Detailed repository info (paginated) |
| `GET /users/{username}/streak` | Contribution streak data |
| `GET /users/{username}/weekly-commits` | Weekly commit schedule |
| `GET /users/{username}/recent-contributions` | Recent contribution activity |
| `GET /users/{username}/stats/full` | All data in one request |

#### SVG Cards

| Endpoint | Description |
|---|---|
| `GET /users/{username}/cards/overview?theme=dracula` | Overview SVG card |
| `GET /users/{username}/cards/languages?theme=dark` | Language distribution SVG card |
| `GET /users/{username}/cards/streak?theme=nord` | Contribution streak SVG card |
| `GET /users/{username}/cards/streak-battery?theme=tokyo_night` | Streak battery SVG card |
| `GET /users/{username}/cards/languages-puzzle?theme=catppuccin_mocha` | Language puzzle SVG card |
| `GET /users/{username}/cards/commit-calendar?theme=dracula` | Commit calendar SVG card |

SVG cards can be embedded directly in Markdown:
```markdown
![Stats](https://your-api.example.com/users/leonardokr/cards/overview?theme=dracula)
```

#### Comparison, History & Webhooks

| Endpoint | Description |
|---|---|
| `GET /users/{username}/compare/{other}` | Side-by-side user comparison |
| `GET /users/{username}/history` | Historical stats snapshots |
| `POST /webhooks` | Register a webhook for stat changes |
| `GET /webhooks` | List registered webhooks |
| `DELETE /webhooks/{id}` | Remove a webhook |

#### Infrastructure

| Endpoint | Description |
|---|---|
| `GET /health` | Health check (GitHub API connectivity, rate limits, cache, circuit breaker) |
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
curl http://localhost:8000/users/leonardokr/overview
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

- **API Key Authentication** - Protect endpoints with `Authorization: Bearer <key>` header. Enable via `API_AUTH_ENABLED=true` and `API_KEYS` env vars. `/health` and `/docs` remain public.
- **Private Repo Isolation** - Server token is restricted to public repos by default (`ALLOW_PRIVATE_REPOS=false`). Private repo data is never leaked to unauthenticated callers.
- **User Token Support** - Callers can pass `X-GitHub-Token` header with their own token to access their private repos. The API validates token ownership.
- **Rate Limiting** - Per-IP and per-key rate limits via slowapi. Configurable via `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_AUTH`, `RATE_LIMIT_HEAVY` env vars.
- **Input Validation** - All parameters validated with Pydantic models. Username validated against GitHub's format rules.

### Caching

Responses are cached with configurable TTL (default 5 minutes). Two backends available:

- **In-memory** (`TTLCache`) - Default, no configuration needed. Lost on restart.
- **Redis** - Set `REDIS_URL=redis://localhost:6379/0`. Shared across workers, survives restarts.

Cache status is returned via `X-Cache: HIT/MISS` response header.

### Resilience

- **Retry with Exponential Backoff** - Automatic retries on GitHub API failures (rate limits, timeouts, 5xx errors) via tenacity.
- **Circuit Breaker** - Fails fast when GitHub API is down (opens after 5 consecutive failures, resets after 30s) via pybreaker.
- **GitHub Rate Limit Monitoring** - Tracks `X-RateLimit-Remaining` headers. Logs warnings when low, pauses proactively when critical.
- **Partial Responses** - If a collector fails, the response includes data from successful collectors with a `_warnings` field listing failures.

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

#### Using with Static Sites (GitHub Pages)

For static portfolios, generate JSON files via GitHub Actions.

<details>
<summary>Click to view static API generation guide</summary>

**Generate Static JSON Files**

Use the `api/generate_static_api.py` script to create static JSON files for all endpoints:

```bash
export GITHUB_TOKEN=your_token
export GITHUB_ACTOR=your_username
python api/generate_static_api.py
```

This creates:
```
api-data/
└── users/
    └── {username}/
        ├── overview.json
        ├── languages.json
        ├── streak.json
        ├── repositories.json
        └── stats-full.json
```

**Deploy with GitHub Actions**

Create `.github/workflows/generate-api-data.yml`:

```yaml
name: Generate Static API Data

on:
  schedule:
    - cron: "0 */6 * * *"  # Every 6 hours
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Generate static API JSON files
        env:
          ACCESS_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_ACTOR: ${{ github.repository_owner }}
        run: python api/generate_static_api.py

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./api-data
          publish_branch: gh-pages
          destination_dir: api
```

Then access: `https://username.github.io/repo/api/users/username/overview.json`

</details>

### Portfolio Integration Example

**Option 1: Client-side fetch (hosted API)**
```javascript
fetch('https://your-api.example.com/users/leonardokr/repositories/detailed')
  .then(res => res.json())
  .then(data => {
    data.data.forEach(repo => {
      renderProject(repo);
    });
  });
```

**Option 2: Build-time generation (GitHub Actions)**
```yaml
- name: Fetch latest projects
  run: |
    curl https://your-api.example.com/users/leonardokr/repositories/detailed \
      -o src/data/projects.json

- name: Build site with fresh data
  run: npm run build
```

**Option 3: Static JSON files (no backend needed)**
- Generate JSON files via GitHub Actions in this repo
- Deploy to `gh-pages` branch
- Your portfolio fetches: `https://username.github.io/leo-git-statistics/api/users/username/repositories.json`

### Environment Variables

Create `api/.env` file (see `api/.env.example`):

```bash
# Required
GITHUB_TOKEN=your_github_personal_access_token

# Server
PORT=8000
WORKERS=4

# Security
ALLOW_PRIVATE_REPOS=false
API_AUTH_ENABLED=false
API_KEYS=
CORS_ORIGINS=*

# Rate limiting
RATE_LIMIT_DEFAULT=30/minute
RATE_LIMIT_AUTH=100/minute
RATE_LIMIT_HEAVY=10/minute

# Cache
# REDIS_URL=redis://localhost:6379/0
# CACHE_TTL=300

# Database
# DATABASE_PATH=src/db/traffic.db
# SNAPSHOTS_DB_PATH=src/db/snapshots.db
# WEBHOOKS_DB_PATH=src/db/webhooks.db
```

### CORS

CORS is enabled for all origins by default. To restrict, set the `CORS_ORIGINS` env var:

```bash
CORS_ORIGINS=https://leonardokr.github.io,https://myportfolio.com
```

</details>

## Architecture

```
leo-git-statistics/
├── generate.py                          # Main SVG generation script (CLI)
├── requirements.txt                     # Production dependencies
├── requirements-dev.txt                 # Development/test dependencies
├── config.yml                           # Configuration file
├── Dockerfile                           # Multi-stage Docker build
├── docker-compose.yml                   # API + Redis deployment
├── api/                                 # FastAPI REST API
│   ├── main.py                          # App entry point, CORS, lifecycle events
│   ├── generate_static_api.py           # Static JSON generator for GitHub Pages
│   ├── .env.example                     # API environment variables
│   ├── routes/                          # API route handlers
│   │   ├── users.py                     # /users/{username}/* endpoints
│   │   ├── cards.py                     # SVG card endpoints
│   │   ├── compare.py                   # User comparison endpoint
│   │   ├── history.py                   # Historical snapshots endpoint
│   │   ├── health.py                    # Health check with dependency status
│   │   └── webhooks.py                  # Webhook registration endpoints
│   ├── services/                        # Business logic layer
│   │   ├── stats_service.py             # StatsCollector creation, partial responses
│   │   ├── card_renderer.py             # SVG card rendering service
│   │   └── notification_dispatcher.py   # Webhook notification dispatcher
│   ├── deps/                            # FastAPI dependency injection
│   │   ├── http_session.py              # Shared aiohttp.ClientSession (connection pool)
│   │   ├── cache.py                     # Redis cache with in-memory TTLCache fallback
│   │   ├── auth.py                      # API key authentication
│   │   ├── github_token.py              # User GitHub token resolution
│   │   └── token_scope.py               # Private repo access control
│   ├── middleware/                      # FastAPI middleware
│   │   ├── logging.py                   # Structured logging (structlog)
│   │   ├── metrics.py                   # Prometheus metrics instrumentation
│   │   └── rate_limiter.py              # Rate limiting (slowapi)
│   └── models/                          # Pydantic models
│       ├── requests.py                  # Query parameter validation
│       └── responses.py                 # Response schemas
├── src/                                 # Core business logic
│   ├── core/                            # Domain logic & data collection
│   │   ├── github_client.py             # GitHub API client (retry, circuit breaker, rate limit tracking)
│   │   ├── stats_collector.py           # Facade composing all collectors
│   │   ├── repo_stats_collector.py      # Repos, stars, forks, languages
│   │   ├── contribution_tracker.py      # Streaks & contribution calendar
│   │   ├── commit_schedule_collector.py # Weekly commit schedule (async parallel)
│   │   ├── code_change_analyzer.py      # Lines changed, percentages (async parallel)
│   │   ├── traffic_collector.py         # Views & clones traffic (async parallel)
│   │   ├── engagement_collector.py      # Pull requests, issues (async parallel)
│   │   ├── graphql_queries.py           # GraphQL query builders
│   │   ├── config.py                    # Theme configuration management
│   │   ├── credentials.py               # GitHub token/actor resolution
│   │   ├── environment.py               # Environment variables & DI
│   │   ├── display_settings.py          # Statistics visibility toggles
│   │   ├── repository_filter.py         # Repository inclusion/exclusion rules
│   │   ├── traffic_stats.py             # Accumulated traffic state
│   │   ├── protocols.py                 # Segregated Protocol interfaces (ISP)
│   │   └── mock_stats.py                # Mock data for local testing
│   ├── db/                              # Data persistence (SQLite with WAL)
│   │   └── db.py                        # Traffic stats database
│   ├── generators/                      # SVG generators (auto-discovered via registry)
│   │   ├── base.py                      # BaseGenerator ABC + GeneratorRegistry
│   │   ├── overview.py                  # Overview statistics card
│   │   ├── languages.py                 # Language distribution card
│   │   ├── languages_puzzle.py          # Language treemap card
│   │   ├── streak.py                    # Contribution streak card
│   │   ├── streak_battery.py            # Streak battery card
│   │   └── commit_calendar.py           # Weekly commit calendar card
│   ├── presentation/                    # Rendering layer
│   │   ├── stats_formatter.py           # Data formatting utilities
│   │   ├── svg_template.py              # SVG template engine
│   │   └── visual_algorithms.py         # Treemap & color palette algorithms
│   ├── templates/                       # SVG templates
│   ├── themes/                          # Theme definitions (YAML)
│   └── utils/                           # Utility functions
├── test/                                # Test suite
│   ├── api/                             # API integration tests (httpx)
│   ├── core/                            # Async collector unit tests (aioresponses)
│   └── load/                            # Load tests (locust)
└── examples/                            # Integration examples
```

### Key Design Decisions

- **SOLID Architecture** - Each class has a single responsibility, dependencies are injected, and interfaces are segregated via `typing.Protocol`
- **Facade Pattern** - `StatsCollector` composes 6 specialized collectors (`RepoStatsCollector`, `ContributionTracker`, `CommitScheduleCollector`, `CodeChangeAnalyzer`, `TrafficCollector`, `EngagementCollector`) behind a unified API
- **Registry Pattern** - Generators self-register via `@register_generator` decorator; the orchestrator discovers them automatically without hardcoded lists
- **Protocol-based Interfaces** - Each generator depends only on the subset of stats it needs (`StreakProvider`, `LanguageProvider`, `OverviewProvider`, `BatteryProvider`, `CommitCalendarProvider`)
- **Dependency Injection** - All major classes accept optional dependencies in their constructors for testability. FastAPI `Depends()` used for HTTP session, cache, auth, and token resolution
- **Async/Await with Parallel Execution** - All collectors use `asyncio.gather()` with `asyncio.Semaphore(10)` to fetch repository data concurrently while respecting GitHub rate limits
- **Resilience Patterns** - Retry with exponential backoff (tenacity) and circuit breaker (pybreaker) in `GitHubClient` for automatic failure recovery
- **Multi-tier Caching** - Redis cache backend with in-memory `TTLCache` fallback. Cache key is `(username, endpoint)` with configurable TTL
- **SQLite with WAL** - Traffic stats, snapshots, and webhooks stored in SQLite databases with Write-Ahead Logging for concurrent read/write safety
- **YAML-based Themes** - Easy to add, remove, or modify themes
- **Template Engine** - Simple placeholder replacement for maintainability
- **Structured Observability** - structlog for JSON logging, Prometheus metrics for monitoring, robust health checks for dependency status

## Development

### Prerequisites
- Python 3.10+
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

#### SVG Generation with GitHub API

```bash
export ACCESS_TOKEN="your_github_token"
export GITHUB_ACTOR="your_username"
python generate.py
```

#### SVG Generation with Mock Data (no API required)

```bash
python generate_test.py
```

Generates all SVG cards using mock data in `generated_images/`. Useful for testing themes and templates.

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

GPL-3.0 License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with Python, FastAPI, and GitHub Actions</sub>
</p>





