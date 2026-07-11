---
stepsCompleted: ["step-01-validate-prerequisites", "step-02-design-epics", "step-03-create-stories", "step-04-final-validation"]
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

FR-1: Epic 1 - Crawling registered blogs using crawl4AI
FR-2: Epic 1 - Deduplicating crawled articles using fetched_posts.json
FR-3: Epic 1 - Generating 5-element English summaries and rating via Gemini ADK
FR-4: Epic 1 - Translating English summaries to Traditional Chinese (Taiwan) via Gemini ADK
FR-5: Epic 2 - Render archive homepage with bento-grid days and highlights
FR-6: Epic 2 - Render daily summaries in responsive split-pane detail layout
FR-7: Epic 2 - Multilingual routing (/en/ and /zh-tw/) and language toggle
FR-8: Epic 1 - Run GitHub Actions cron job daily at 7:00 AM UTC+8
FR-9: Epic 1 - Commit newly generated post content and deduplication store updates

## Epic List

### Epic 1: Daily News Pipeline
Configure and automate the backend pipeline to crawl AI blogs, filter duplicates, generate structured English summaries and Traditional Chinese translations, and save them daily.
**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-8, FR-9

### Epic 2: Multilingual Static Website
Build a zero-dependency, responsive, high-density multilingual static website with a Bento-grid archive, a split-pane reader with search/tags, and context-preserving language switching.
**FRs covered:** FR-5, FR-6, FR-7

## Epic 1: Daily News Pipeline

Configure and automate the backend pipeline to crawl AI blogs, filter duplicates, generate structured English summaries and Traditional Chinese translations, and save them daily.

### Story 1.1: Local Blog Scraper & Parser

As a developer,
I want a Python script that parses configured blogs from a YAML file and extracts clean article body text using crawl4AI,
So that the pipeline can retrieve news content without page boilerplate clutter.

**Acceptance Criteria:**

**Given** a YAML configuration in `data/blogs.yaml` with a list of blog URLs
**When** the script `src/pipeline.py` is executed using `uv run`
**Then** it successfully crawls each URL using `crawl4AI`
**And** extracts the title, publication date, author, and main article text body into a parsed data structure, excluding headers, footers, and sidebars.

### Story 1.2: Deduplication Store

As a developer,
I want the pipeline to cross-reference fetched post URLs with a JSON store,
So that the system only processes new articles and avoids duplicate summaries.

**Acceptance Criteria:**

**Given** a deduplication file at `data/fetched_posts.json` containing previously processed URLs
**When** the pipeline processes crawled URLs
**Then** it skips any URL already recorded in the JSON file
**And** logs skipped URLs to stdout
**And** appends new URLs to the JSON file only after successful processing.

### Story 1.3: Gemini-powered Structured Technical Summarization

As an AI engineer reader,
I want the pipeline to generate a structured 5-element English summary and 1-5 star technical rating via Gemini,
So that I can quickly understand the architectural depth of the article.

**Acceptance Criteria:**

**Given** new article content extracted from a crawled blog
**When** the pipeline invokes the Gemini model via `google-adk`
**Then** it returns a structured summary containing exactly: TL;DR (one sentence), Problem/Why, Solution/How, Insights & Trade-offs (pros/cons list), and Tags & Action
**And** computes a rating score of 1-5 stars reflecting technical depth and actionability.

### Story 1.4: Localization & Translation

As a Taiwanese developer reader,
I want the structured summaries translated into Traditional Chinese (Taiwan) while keeping core developer terms in English,
So that I can read updates in my native language without losing technical precision.

**Acceptance Criteria:**

**Given** a generated English structured summary
**When** the pipeline translates the summary into Traditional Chinese
**Then** terms like "prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", and "token" remain in English
**And** the translated summary maintains the exact 5-element markdown structure.

### Story 1.5: Content Publishing & Static File Writing

As a site maintainer,
I want compiled daily summaries saved as structured frontmatter YAML arrays in daily markdown files,
So that the static site generator can read and display them.

**Acceptance Criteria:**

**Given** processed English and Traditional Chinese summaries for the day
**When** the pipeline writes the daily output files
**Then** it creates `content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md`
**And** saves the summaries as a YAML array under the `articles` key in the frontmatter of these files.

### Story 1.6: Daily pipeline schedule & deployment workflow automation

As a site maintainer,
I want the pipeline automated on GitHub Actions to run daily and commit updates on success,
So that the website updates automatically with zero manual effort.

**Acceptance Criteria:**

**Given** a GitHub Actions workflow configuration in `.github/workflows/pipeline.yml`
**When** the schedule triggers daily at 7:00 AM UTC+8
**Then** it installs dependencies, executes the pipeline script, and commits new content to the repository using a conventional commit message (e.g. `feat: add daily summaries for YYYY-MM-DD`)
**And** triggers Hugo build and deploy to GitHub Pages
**And** logs failures to stdout/stderr in a structured JSON format.

## Epic 2: Multilingual Static Website

Build a zero-dependency, responsive, high-density multilingual static website with a Bento-grid archive, a split-pane reader with search/tags, and context-preserving language switching.

### Story 2.1: Hugo Multilingual Setup & Configuration Research

As a developer,
I want to research and configure the Hugo site for English and Traditional Chinese multilingual routing,
So that content is properly organized under `/en/` and `/zh-tw/` without external themes.

**Acceptance Criteria:**

**Given** a `hugo.toml` file configured with English and Traditional Chinese (`zh-tw`) languages
**When** the Hugo site builds
**Then** English post files build under `/en/posts/` and Traditional Chinese posts under `/zh-tw/posts/`
**And** no third-party themes are imported in the configuration.

### Story 2.2: Zero-Dependency Layout & Asset Architecture

As a reader,
I want the static site styled with a premium, zero-dependency layout matching the styling system,
So that the interface feels professional, clean, and highly readable.

**Acceptance Criteria:**

**Given** brand colors, typography (Inter), and layout units in `DESIGN.md`
**When** the CSS is compiled in `static/css/index.css` and loaded by Hugo layouts
**Then** the UI elements render with low-contrast borders (1px `#e2e8f0`), rounded corners (4px standard, 8px large), canvas background `#f7f9fb`, and correct typography scales.

### Story 2.3: Bento Grid Archive Layout (Homepage)

As a reader,
I want a Bento-grid layout homepage displaying chronological historical days with daily summaries,
So that I can quickly scan past news.

**Acceptance Criteria:**

**Given** historical post files in content folders
**When** I visit the homepage (`/` or `/en/` or `/zh-tw/`)
**Then** it renders a Bento grid of historical daily cards
**And** each card displays the date, a short daily highlight summary, the count of articles, and a "View Summary" button
**And** hovering over a card triggers a 2px lift transition and soft shadow.

### Story 2.4: Split-Pane Detail Layout (Daily summary)

As a reader,
I want to view daily summaries in a split-pane layout with a scrollable article list on the left and selected article details on the right,
So that I can read multiple summaries efficiently without page reloads.

**Acceptance Criteria:**

**Given** a daily summaries post page (`/en/posts/YYYY-MM-DD/`)
**When** viewed on desktop (1024px+)
**Then** it displays a split-pane layout: a fixed 280px left sidebar (4 cols) listing article cards and a right panel (8 cols) displaying the selected article
**And** reflows to a single-column vertical stack on mobile screens (<768px).

### Story 2.5: Interactive JavaScript Switcher Integration

As a reader,
I want clicking an article card in the sidebar to instantly load its summary on the right without reloading the page,
So that the reading experience is fast and smooth.

**Acceptance Criteria:**

**Given** the daily post frontmatter containing a YAML array of articles
**When** I click an article card in the sidebar
**Then** the client-side JavaScript (`static/js/main.js`) parses the frontmatter array and populates the details panel instantly
**And** highlights the active card with a 3px primary border and background tint.

### Story 2.6: Sidebar Search, Filters & Language Switcher

As a reader,
I want to filter articles by tags, search by title/tag, and toggle languages while keeping my active reading context,
So that I can quickly find relevant articles and compare translations.

**Acceptance Criteria:**

**Given** a split-pane daily summaries page
**When** I input a query in the search bar or click a tag pill
**Then** the sidebar list instantly filters matching articles
**And** when I click the "EN/TW" switcher in the header, the page transitions between `/en/` and `/zh-tw/` paths while preserving the selected date and article view.


