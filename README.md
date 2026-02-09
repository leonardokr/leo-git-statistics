# git-statistics

This project automates the generation of GitHub statistics images for your profile. It uses GitHub Actions to collect data from the GitHub API and render custom SVGs that you can display on your README.

## How to use

### 1. Use this repository as a Template
Click the **"Use this template"** button to create a copy of this project in your account.

### 2. Configure your Profile (`config.yml`)
All configuration is centralized in the `config.yml` file at the root of the project. You don't need to edit the workflow files.

*   **`github_user`**: Your GitHub username.
*   **`timezone`**: Your timezone (e.g., `America/New_York`).
*   **`metrics`**: Settings for the `lowlighter/metrics` plugin (generates `github-metrics.svg`).
*   **`stats_generation`**: Settings for the custom images of this project (generates `overview.svg` and `languages.svg`). Here you can filter repositories, include forks, hide private repositories, etc.

### 3. Create a Personal Access Token (PAT)
1. Go to **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2. Generate a new token with the following scopes (recommended):
    - `repo` (for private repository statistics)
    - `read:user`
    - `read:org`
3. Save this token.

### 4. Add the Token to Repository Secrets
1. In your new repository, go to **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret**.
3. Name: `ACCESS_TOKEN`.
4. Value: Paste the token you generated.

---

## Generated Images

Images are automatically saved in the `generated_images/` folder and updated periodically.

### Overview Stats
General statistics such as stars, forks, total contributions, and lines of code changed. Supports Light and Dark themes.
- `generated_images/overview.svg`
- `generated_images/overviewDarkMode.svg`

### Most Used Languages
Bar chart and list with the programming languages you use the most.
- `generated_images/languages.svg`
- `generated_images/languagesDarkMode.svg`

### GitHub Metrics (External Plugin)
Detailed metrics provided by `lowlighter/metrics`, configured entirely via `config.yml`.
- `generated_images/github-metrics.svg`

---

## Advanced Customization

### Themes
You can change the colors of the Light and Dark themes by editing the `Config` class in `src/core/config.py`.

### Repository Filters
In the `stats_generation` section of `config.yml`, you can define:
- `excluded_repos`: List of repositories to ignore.
- `include_forked_repos`: Whether to count forks in statistics.
- `exclude_private_repos`: Whether to hide data from private repositories.

---

_Based on the original project [NazmusSayad/Git-Stats](https://github.com/NazmusSayad/Git-Stats)_
