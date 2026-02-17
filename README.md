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

## Features

- **Multiple Statistics Cards** - Overview stats, language distribution, contribution streaks, streak battery, language puzzle, and weekly commit calendar
- **25+ Built-in Themes** - From Dracula to Nord, Catppuccin to Tokyo Night
- **Extensible Theme System** - Add your own themes via YAML files
- **Animated SVGs** - Smooth fade-in and slide animations
- **Fully Configurable** - Control which stats to show, filter repositories, and more
- **Reusable GitHub Action** - Run the generator from any repository (great for profile repos)
- **Accumulated Metrics** - Track views and clones beyond GitHub's 14-day limit
- **REST API** - Access all statistics data as JSON for portfolios and web applications (requires backend hosting)

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

This project also provides a **REST API** that exposes all statistics data as JSON. Perfect for portfolios, dashboards, and web applications.

> **Note:** The API is a Flask application that requires backend hosting (Render, Railway, PythonAnywhere, etc.). It cannot run on GitHub Pages.

<details>
<summary><b>Click to view API Documentation</b></summary>

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (see api/.env.example)
export GITHUB_TOKEN=your_token_here

# 3. Run the API
python api/app.py

# 4. Access interactive docs at http://localhost:5000/docs
```

### Key Endpoints

| Endpoint                                             | Description                  |
| ------------------------------------------------------| ------------------------------|
| `GET /users/{username}/overview`              | Complete overview statistics |
| `GET /users/{username}/languages`             | Language distribution        |
| `GET /users/{username}/repositories`          | Repository list (names only) |
| `GET /users/{username}/repositories/detailed` | Detailed repository info     |
| `GET /users/{username}/streak`                | Contribution streak data     |
| `GET /users/{username}/stats/full`            | All data in one request      |

### Example Response

```bash
curl http://localhost:5000/users/leonardokr/overview
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

### Interactive Documentation

The API includes **Swagger/OpenAPI** documentation. After running the API, visit:

```
http://localhost:5000/docs
```

You'll see an interactive interface where you can test all endpoints directly in your browser.

### Deployment Options

The API needs a backend platform that supports Python:

#### Recommended: Render (Free)
1. Create account at [render.com](https://render.com)
2. New → Web Service → Connect GitHub repo
3. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `python api/app.py`
   - Environment variable: `GITHUB_TOKEN=your_token`
4. Deploy!

**Other Options:**
- **Railway** - $5 credit/month free tier
- **PythonAnywhere** - 1 free web app, always running
- **Fly.io** - 3 free VMs with limits

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
// In your portfolio site (e.g., leonardokr.github.io)
fetch('https://your-api.onrender.com/users/leonardokr/repositories/detailed')
  .then(res => res.json())
  .then(data => {
    // Render projects with full details
    data.repositories.forEach(repo => {
      renderProject(repo); // repo has name, description, stars, topics, etc.
    });
  });
```

**Option 2: Build-time generation (GitHub Actions)**
```yaml
# In your portfolio repository workflow
- name: Fetch latest projects
  run: |
    curl https://your-api.onrender.com/users/leonardokr/repositories/detailed \
      -o src/data/projects.json

- name: Build site with fresh data
  run: npm run build
```

**Option 3: Static JSON files (no backend needed)**
- Generate JSON files via GitHub Actions in this repo
- Deploy to `gh-pages` branch
- Your portfolio fetches: `https://username.github.io/leo-git-statistics/api/users/username/repositories.json`

### Usage Examples

**JavaScript (Fetch)**
```javascript
// Get all stats
const response = await fetch('https://api.example.com/users/leonardokr/stats/full');
const stats = await response.json();

// Get only repositories
const repos = await fetch('https://api.example.com/users/leonardokr/repositories');
const data = await repos.json();
console.log(data.repositories); // Array of repo names
```

**Python**
```python
import requests

# Get overview
stats = requests.get('https://api.example.com/users/leonardokr/overview').json()
print(f"Total stars: {stats['total_stars']}")

# Get languages
langs = requests.get('https://api.example.com/users/leonardokr/languages').json()
print(langs['languages'])
```

**cURL**
```bash
# Get repositories for portfolio
curl https://api.example.com/users/leonardokr/repositories

# Get full stats
curl https://api.example.com/users/leonardokr/stats/full
```

### Environment Variables

Create `api/.env` file (see `api/.env.example`):

```bash
# Required
GITHUB_TOKEN=your_github_personal_access_token

# Optional
PORT=5000
FLASK_DEBUG=false
API_HOST=localhost:5000
```

### CORS

CORS is enabled for all origins by default. To restrict, edit `api/app.py`:

```python
CORS(app, origins=["https://leonardokr.github.io"])
```

### Rate Limits

- **Authenticated:** 5000 requests/hour (with `GITHUB_TOKEN`)
- **Unauthenticated:** 60 requests/hour

Always use a token to avoid limits.

</details>

## Architecture

```
leo-git-statistics/
├── generate.py                          # Main SVG generation script
├── requirements.txt                     # Python dependencies
├── config.yml                           # Configuration file
├── .env.example                         # Environment variables example
├── api/                                 # REST API
│   ├── app.py                           # Flask API application
│   ├── generate_static_api.py           # Static JSON generator for GitHub Pages
│   └── .env.example                     # API environment variables
├── src/                                 # Core business logic
│   ├── core/                            # Domain logic & data collection
│   │   ├── config.py                    # Theme configuration management
│   │   ├── credentials.py               # GitHub token/actor resolution
│   │   ├── environment.py               # Environment variables & injectable dependencies
│   │   ├── display_settings.py          # Statistics visibility toggles
│   │   ├── repository_filter.py         # Repository inclusion/exclusion rules
│   │   ├── traffic_stats.py             # Accumulated traffic state
│   │   ├── protocols.py                 # Segregated Protocol interfaces (ISP)
│   │   ├── github_client.py             # GitHub API client (GraphQL + REST)
│   │   ├── graphql_queries.py           # GraphQL query builders
│   │   ├── stats_collector.py           # Facade composing all collectors
│   │   ├── repo_stats_collector.py      # Repos, stars, forks, languages
│   │   ├── contribution_tracker.py      # Streaks & contribution calendar
│   │   ├── commit_schedule_collector.py # Weekly commit schedule by repository
│   │   ├── code_change_analyzer.py      # Lines changed, percentages, contributors
│   │   ├── traffic_collector.py         # Views & clones traffic
│   │   ├── engagement_collector.py      # Pull requests, issues, collaborators
│   │   └── mock_stats.py                # Mock data for local testing
│   ├── db/                              # Data persistence
│   │   └── db.py                        # JSON database for accumulated metrics
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
│   │   ├── overview.svg
│   │   ├── languages.svg
│   │   ├── languages_puzzle.svg
│   │   ├── streak.svg
│   │   ├── streak_battery.svg
│   │   └── commit_calendar.svg
│   ├── themes/                          # Theme definitions (YAML)
│   │   ├── loader.py                    # Theme loading utilities
│   │   ├── github.yml
│   │   ├── popular.yml
│   │   ├── catppuccin.yml
│   │   ├── material.yml
│   │   └── creative.yml
│   ├── utils/                           # Utility functions
│   │   ├── file_system.py               # File system helpers
│   │   ├── decorators.py                # Async property decorators
│   │   └── helpers.py                   # Shared helper functions
│   └── orchestrator.py                  # Main coordinator
├── examples/                            # Integration examples
│   └── portfolio-integration.md         # Complete portfolio integration guide
└── test/                                # Unit tests
```

### Key Design Decisions

- **SOLID Architecture** - Each class has a single responsibility, dependencies are injected, and interfaces are segregated via `typing.Protocol`
- **Facade Pattern** - `StatsCollector` composes 6 specialized collectors (`RepoStatsCollector`, `ContributionTracker`, `CommitScheduleCollector`, `CodeChangeAnalyzer`, `TrafficCollector`, `EngagementCollector`) behind a unified API
- **Registry Pattern** - Generators self-register via `@register_generator` decorator; the orchestrator discovers them automatically without hardcoded lists
- **Protocol-based Interfaces** - Each generator depends only on the subset of stats it needs (`StreakProvider`, `LanguageProvider`, `OverviewProvider`, `BatteryProvider`, `CommitCalendarProvider`)
- **Dependency Injection** - All major classes accept optional dependencies in their constructors for testability
- **Async/Await** - Concurrent API calls for better performance
- **YAML-based Themes** - Easy to add, remove, or modify themes
- **Template Engine** - Simple placeholder replacement for maintainability
- **Persistent Storage** - JSON database for accumulated metrics beyond GitHub's 14-day limit

## Development

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
pip install -r requirements.txt
```

### Running Locally

#### With GitHub API (real data)

```bash
export ACCESS_TOKEN="your_github_token"
export GITHUB_ACTOR="your_username"
python generate.py
```

#### With Mock Data (no API required)

For testing templates, themes, and visual changes without needing a GitHub token:

```bash
python generate_test.py
```

This generates all SVG cards using mock data in the `generated_images/` folder. Useful for:
- Testing theme modifications
- Developing new SVG templates
- Previewing visual changes locally
- CI/CD pipelines without API access

### Running Tests

```bash
pytest test/
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
  <sub>Built with Python and GitHub Actions</sub>
</p>





