---
stepsCompleted: ["step-01-validate-prerequisites"]
inputDocuments:
  - "/home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/prds/prd-daily-ai-news-2026-07-11/prd.md"
  - "/home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md"
  - "/home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/SOLUTION-DESIGN.md"
  - "/home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/DESIGN.md"
  - "/home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/EXPERIENCE.md"
---

# daily-ai-news - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for daily-ai-news, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: Crawl Blog Registry: The crawling script must parse configured URLs in the Blog Registry and extract the main article content (title, publication date, author, text body) using `crawl4AI`.
FR-2: Deduplicate Crawled Articles: The system must cross-reference crawled article URLs with the Deduplication Store before processing them.
FR-3: Generate Structured Technical Summaries: The ADK Agent must parse crawled article content and output a Technical Summary matching the 5-element framework (TL;DR, Problem/Why, Solution/How, Insights & Trade-offs, Tags & Action), including rating score (1-5 stars) using specific rating prompt.
FR-4: Translate Technical Summaries: The ADK Agent must translate the Technical Summary into Traditional Chinese (Taiwan) while retaining industry-standard terms in English ("prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token").
FR-5: Render Archive Page (Home View): The website homepage must display a chronological archive of daily summaries matching the `ai_2` mockup design. Includes Hero banner, quick-look feature summary, Bento-grid styled historical days with date, daily highlight summary, count of articles, and "View Summary" button, plus pagination controls.
FR-6: Render Daily Summary Split-Pane Page (Detail View): The daily summary pages must use a split-pane layout matching the `ai_1` mockup. Header: date, daily highlights, generation metadata. Left Sidebar: tag-filtering pills, tag search input, scrollable article cards (category icon, title, tags). Right Panel: details for selected article (TL;DR box, Problem/Why container, Solution/How container, Insights & Trade-offs side-by-side pros/cons, Tags & Action, original source link).
FR-7: Multilingual Routing and Language Switcher: English content routes under `/en/`, Traditional Chinese under `/zh-tw/`. Persistent navigation header has language toggle button.
FR-8: Execute Daily Pipeline Schedule: The GitHub Actions workflow must run automatically at 7:00 AM UTC+8 (23:00 UTC) every day, executing `uv`, crawling, ADK summaries/translations, committing changes, and deploying via Hugo to GitHub Pages.
FR-9: Commit Output and Deduplication Store Updates: On success, commit newly generated markdown/JSON summaries and updated `fetched_posts.json` with a conventional commit message. Pipeline failures must not commit or deploy.

### NonFunctional Requirements

NFR-1: Zero Server Hosting Costs: System must run serverless, hosting the static site on GitHub Pages.
NFR-2: Zero-Maintenance Automation: System runs fully automated daily pipeline execution without manual intervention.
NFR-3: Technical Localization: Traditional Chinese translations must retain targeted English developer terms.
NFR-4: Performance: Hugo static site build and deploy duration must be under 2 minutes.
NFR-5: Scraper Reliability: Scraper must successfully process at least 90% of configured blogs without page-layout parsing failures.
NFR-6: Accessibility: Contrast ratios must be at least 4.5:1, with 44px min click targets and screen-reader ARIA tags.

### Additional Requirements

- AR-1: Pipes-and-Filters execution flow coordinated by a single Python script (`src/pipeline.py`) running modular filters sequentially.
- AR-2: Python components must run using `uv run`.
- AR-3: Blog registry stored in YAML (`data/blogs.yaml`) and processed URLs tracked in JSON (`data/fetched_posts.json`).
- AR-4: Structured English summarization and subsequent translation must run in two distinct steps using Gemini via Google ADK.
- AR-5: Zero-dependency custom Hugo layouts under `layouts/` with custom CSS in `static/css/index.css`. No external Hugo themes.
- AR-6: Daily summaries stored as a structured YAML array (`articles` key) in the frontmatter of daily markdown files (`content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md`).
- AR-7: Single blog failures during crawling or summarization must log/report errors but not block the rest of the pipeline.
- AR-8: Logging must output structured JSON to stdout/stderr with timestamp, stage, blog_url, and error_message.

### UX Design Requirements

UX-DR-1: Design tokens implementation: Implement brand color palette (Primary `#004ac6`, Surface `#f7f9fb`, low-contrast outlines `#e2e8f0`) and Inter typography hierarchies.
UX-DR-2: Tonal Layering: Canvas Level 0 background, Level 1 cards/sidebar with 1px border and no shadow, Level 2 active dropdowns with soft shadow. Rounding standard elements 0.25rem, large elements 0.5rem.
UX-DR-3: Bento Card Archive: Interactive Bento cards on homepage archive showing date, highlights, article count, and a hover scale transition.
UX-DR-4: Detail Split-Pane: Desktop 12-column grid with a fixed 280px left sidebar (4 cols) and scrollable right detail panel (8 cols). Collapses to vertical stack on mobile.
UX-DR-5: Interactive switcher: Client-side JS (`static/js/main.js`) parses YAML frontmatter array to dynamically change right detail panel contents on sidebar card clicks without reloading.
UX-DR-6: Language switch: Ghost button EN/TW switcher in the global header preserving current date and selected article state.
UX-DR-7: Voice and Tone: Strictly professional microcopy: "Deep Dive", "閱讀時間：約 4 分鐘", "今日 AI 領域聚焦於...", "Original Link".
UX-DR-8: Accessibility floor: Custom ARIA labels for category icons, dynamic `lang` attributes, and minimum 44px click target.

### FR Coverage Map

{{requirements_coverage_map}}

## Epic List

{{epics_list}}
