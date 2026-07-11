---
id: SPEC-daily-ai-news
companions:
  - ../../planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/DESIGN.md
  - ../../planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/EXPERIENCE.md
  - ../../planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md
  - ../../planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/SOLUTION-DESIGN.md
sources:
  - ../../planning-artifacts/prds/prd-daily-ai-news-2026-07-11/prd.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability only — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Daily AI News Summary Website

## Why

Technical AI practitioners (engineers and researchers) need a clean, distraction-free way to digest newly published AI engineering breakthroughs daily in their native language without marketing fluff. Standard developer terminology must be preserved in Traditional Chinese (Taiwan) translations to avoid ambiguity. The solution must operate serverless on a scheduled pipeline with zero server hosting costs.

## Capabilities

- **CAP-1**
  - **intent:** System scrapes configured technical blog URLs to extract clean article content including title, publication date, author, and main body text.
  - **success:** The crawled content matches the original article's core text but contains no headers, footers, sidebars, navigation bars, or advertisements.
- **CAP-2**
  - **intent:** System checks crawled articles against a deduplication record before processing to prevent duplicate summaries.
  - **success:** If an article URL is in `fetched_posts.json`, it is skipped; new URLs are processed and successfully appended to the registry.
- **CAP-3**
  - **intent:** System uses an LLM via Google ADK to generate a structured 5-element summary and a quality/depth rating for each crawled article.
  - **success:** Summaries match the template structure (TL;DR, Problem/Why, Solution/How, Insights & Trade-offs, Tags & Action) and include a 1-to-5 star rating based on technical depth.
- **CAP-4**
  - **intent:** System translates generated summaries into Traditional Chinese (Taiwan) while retaining standard English developer terminology.
  - **success:** Output structure matches the English original, and standard terms (prompt, fine-tuning, RAG, agent, pipeline, checkpoint, embeddings, token) remain in English.
- **CAP-5**
  - **intent:** User can view a chronological archive grid of historical daily news summaries with daily highlight overviews.
  - **success:** The homepage displays Bento-grid cards showing the date, daily summary highlights, crawled article count, and a detail link, with pagination.
- **CAP-6**
  - **intent:** User can browse the daily articles and read their detailed 5-element summaries using an interactive split-pane interface.
  - **success:** Tapping a card in the left sidebar instantly updates the right details panel with the selected summary using client-side JavaScript without page reloads.
- **CAP-7**
  - **intent:** User can toggle the display language of the active page between English and Traditional Chinese (Taiwan).
  - **success:** Tapping the language switcher changes the path locale between `/en/` and `/zh-tw/` while keeping the currently selected date and active article in view.
- **CAP-8**
  - **intent:** System executes the entire crawling, summarization, translation, static site build, and deployment pipeline automatically on a daily schedule.
  - **success:** A GitHub Actions workflow triggers daily at 7:00 AM UTC+8 and runs all pipeline stages sequentially to build and deploy the Hugo static site.
- **CAP-9**
  - **intent:** System commits newly generated files and updated deduplication registry to GitHub repository.
  - **success:** Git commits are successfully pushed to the repository using conventional commits syntax (`feat: add daily summaries for YYYY-MM-DD`).

## Constraints

- **C-1:** Execution must be serverless with zero server hosting costs, using GitHub Actions for pipeline execution and GitHub Pages for static site hosting.
- **C-2:** Hugo site must use custom templates and layouts with no third-party themes, with styling managed in `static/css/index.css`.
- **C-3:** All pipeline code must be written in Python 3.11+ and execute via `uv run` to ensure a consistent virtual environment.
- **C-4:** Search, filtering, and split-pane view switching must be implemented in client-side vanilla JavaScript without external runtime framework dependencies.
- **C-5:** Translation must leave targeted technical terms (prompt, fine-tuning, RAG, agent, pipeline, embeddings, token, checkpoint) in English.
- **C-6:** Daily article data must be structured as YAML frontmatter arrays in `content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md`.
- **C-7:** Individual blog crawl or summarization failures must be logged but must not abort the overall pipeline run.

## Non-goals

- **N-1:** No user registration, authentication, login, or user profiles.
- **N-2:** No dynamic server-side interactions, database backends, comments sections, or user bookmark storage.
- **N-3:** No automated email newsletter subscription, signup, or mail-delivery systems.
- **N-4:** No backend search index engines (e.g. Elasticsearch).

## Success signal

- The pipeline automatically runs in under 2 minutes daily via GitHub Actions, publishing bilingual static pages on GitHub Pages where Taiwanese developers can read structured 30-second AI insights and toggle between locales with active state preservation.

## Assumptions

- **A-1:** Crawl4AI can bypass blog rate-limiting when running within GitHub Actions runner environments.
- **A-2:** The Gemini LLM used via Google ADK has sufficient capabilities to produce high-fidelity summaries and follow translation terminology constraints.
- **A-3:** Hugo's multilingual routing structure works on GitHub Pages subdirectories without requiring dynamic URL rewriting.
