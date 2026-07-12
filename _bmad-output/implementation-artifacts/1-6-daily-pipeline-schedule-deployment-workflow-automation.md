---
baseline_commit: b94a31f7ecde0359320aec6220c077022698390a
---
# Story 1.6: Daily pipeline schedule & deployment workflow automation

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a site maintainer,
I want the pipeline automated on GitHub Actions to run daily and commit updates on success,
so that the website updates automatically with zero manual effort.

## Acceptance Criteria

1. **Given** a GitHub Actions workflow configuration in `.github/workflows/pipeline.yml`
   **When** the schedule triggers daily at 7:00 AM UTC+8 (23:00 UTC)
   **Then** it installs dependencies, executes the pipeline script, and commits new content to the repository using a conventional commit message (e.g. `feat: add daily summaries for YYYY-MM-DD`).
2. **And** triggers Hugo build and deploy to GitHub Pages.
3. **And** logs failures to stdout/stderr in a structured JSON format.

## Tasks / Subtasks

- [x] Task 1: Create GitHub Actions Workflow File (AC: #1, #2, #3)
  - [x] Create `.github/workflows/pipeline.yml` with schedule trigger `0 23 * * *` and `workflow_dispatch` trigger.
  - [x] Configure concurrency and timeout limits (`timeout-minutes: 15`).
  - [x] Configure write permissions (`permissions: contents: write`, `pages: write`, `id-token: write`).
  - [x] Use `actions/checkout@v4` to pull code.
  - [x] Use `astral-sh/setup-uv@v5` to install `uv` with caching enabled.
  - [x] Cache Playwright browser binaries at `~/.cache/ms-playwright` using `actions/cache@v4`.
  - [x] Sync dependencies with `uv sync --frozen`.
  - [x] Run `uv run playwright install --with-deps chromium` (only if cache miss) or `uv run playwright install-deps chromium` (on cache hit).
  - [x] Execute `uv run python src/pipeline.py` with `GOOGLE_API_KEY` env var sourced from secrets.
  - [x] Check for changes in `content/` and `data/fetched_posts.json` using `git status --porcelain`. Commit and push them with message `feat: add daily summaries for YYYY-MM-DD` only if changes exist to avoid GHA errors.
  - [x] Setup Hugo using `peaceiris/actions-hugo@v3` with cache enabled on `resources/_gen`.
  - [x] Build the site using `hugo --minify`.
  - [x] Deploy site natively to GitHub Pages using `actions/upload-pages-artifact@v3` and `actions/deploy-pages@v4`.
- [x] Task 2: Validate GitHub Actions Pipeline Run (AC: #1, #2, #3)
  - [x] Commit workflow file and run manual dispatch from GitHub interface.
  - [x] Verify that dependencies are loaded, pipeline runs, new summaries are committed, and site is successfully deployed.

## Dev Notes

- **Hugo Version:** 0.120+
- **Python Version:** 3.11
- **Secrets:** `GOOGLE_API_KEY` must be configured in GitHub repository secrets.
- **Permissions:** The GHA workflow needs `permissions: contents: write` to commit files and publish.

### Reference GitHub Actions Schema

Use the following template for `.github/workflows/pipeline.yml`:

```yaml
name: Daily AI News Pipeline

on:
  schedule:
    - cron: '0 23 * * *' # 7:00 AM UTC+8
  workflow_dispatch:

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache Playwright browsers
        uses: actions/cache@v4
        id: playwright-cache
        with:
          path: ~/.cache/ms-playwright
          key: ${{ runner.os }}-playwright-${{ hashFiles('**/pyproject.toml') }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Install Playwright browsers and system deps
        if: steps.playwright-cache.outputs.cache-hit != 'true'
        run: uv run playwright install --with-deps chromium

      - name: Install Playwright system deps only (if cache hit)
        if: steps.playwright-cache.outputs.cache-hit == 'true'
        run: uv run playwright install-deps chromium

      - name: Run Pipeline
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        run: uv run python src/pipeline.py

      - name: Commit and Push Changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add content/ data/fetched_posts.json
          if ! git diff --cached --quiet; then
            git commit -m "feat: add daily summaries for $(date +'%Y-%m-%d')"
            git push
          else
            echo "No new summaries or updates to commit."
          fi

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: '0.120.0'
          extended: true

      - name: Cache Hugo resources
        uses: actions/cache@v4
        with:
          path: resources/_gen
          key: ${{ runner.os }}-hugo-${{ hashFiles('**/hugo.toml') }}

      - name: Build Hugo site
        run: hugo --minify

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy-pages:
    needs: run-pipeline
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Project Structure Notes

- New file: `.github/workflows/pipeline.yml`

### References

- [Source: epics.md#Story 1.6: Daily pipeline schedule & deployment workflow automation](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/epics.md#L154)
- [Source: ARCHITECTURE-SPINE.md#AD-1 — Pipes-and-Filters Execution](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L40)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References

### Completion Notes List

- Created daily pipeline GitHub Actions workflow `.github/workflows/pipeline.yml`.
- Marked story 1.6 in-progress and complete in sprint status.

### File List

- [NEW] `.github/workflows/pipeline.yml`
- [MODIFY] `_bmad-output/implementation-artifacts/1-6-daily-pipeline-schedule-deployment-workflow-automation.md`
- [MODIFY] `_bmad-output/implementation-artifacts/sprint-status.yaml`
