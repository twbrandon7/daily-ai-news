---
baseline_commit: ce668c051134ebdf9847b10d41f59a8ebd16610c
---
# Story 1.1: Local Blog Scraper & Parser

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want a Python script that parses configured blogs from a YAML file and extracts clean article body text using crawl4AI,
so that the pipeline can retrieve news content without page boilerplate clutter.

## Acceptance Criteria

1. **Given** a YAML configuration in `data/blogs.yaml` with a list of blog URLs
2. **When** the script `src/pipeline.py` is executed using `uv run`
3. **Then** it successfully crawls each URL using `crawl4AI`
4. **And** extracts the title, publication date, author, and main article text body into a parsed data structure, excluding headers, footers, and sidebars.

## Tasks / Subtasks

- [x] Task 1: Environment & Project Directory Initialization (AC: #1)
  - [x] Initialize Python environment configurations using standard `uv` patterns if needed.
  - [x] Create `data/` and `src/` directories if not present.
  - [x] Create `data/blogs.yaml` with initial test URLs (e.g., standard AI research blog URLs).
- [ ] Task 2: Implement Crawl Filter in `src/pipeline.py` (AC: #2, #3, #4)
  - [ ] Write asynchronous parser in `src/pipeline.py` using `AsyncWebCrawler` from `crawl4AI`.
  - [ ] Setup `CrawlerRunConfig` with automatic content filtering (e.g., `fit_markdown`) to exclude sidebars, headers, and footers.
  - [ ] Extract title, publication date, author, and main article body.
- [ ] Task 3: Error Handling & Logging (AC: #3)
  - [ ] Log output in structured JSON format with keys: `timestamp`, `stage`, `blog_url`, and `error_message`.
  - [ ] Ensure that single blog failures (network timeout, page load fail) do not block the pipeline from processing other blogs.
- [ ] Task 4: Local Execution & Verification (AC: #2)
  - [ ] Run crawler using `uv run python3 src/pipeline.py`.
  - [ ] Verify extracted content is structured and cleanly excludes boilerplate.

## Dev Notes

- **Paradigm & Execution:** The pipeline runs in a sequential Pipes-and-Filters pattern (AD-1). The entrypoint must be `src/pipeline.py` (AD-2).
- **Libraries & Tooling:** Use `crawl4ai` (v0.4+) and standard python asyncio libraries. Ensure browser setup is performed (`crawl4ai-setup` or Playwright installation).
- **Error Handling (AD-7):** Failures during crawling of a single blog must be logged and reported at the end. The pipeline must proceed to process all other blogs.
- **Logging format:**
  ```json
  {"timestamp": "2026-07-11T19:46:00", "stage": "crawl", "blog_url": "https://example.com", "error_message": "Timeout"}
  ```

### Project Structure Notes

- Keep all source code in the `src/` directory.
- Keep all data files (like registries and temporary caches) in the `data/` directory.

### References

- [Source: epics.md#Story 1.1: Local Blog Scraper & Parser](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/epics.md#L88)
- [Source: ARCHITECTURE-SPINE.md#AD-1 — Pipes-and-Filters Execution](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L40)
- [Source: ARCHITECTURE-SPINE.md#AD-2 — Single Entrypoint Python Script](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L46)
- [Source: ARCHITECTURE-SPINE.md#AD-3 — YAML Registry & JSON Deduplication Store](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L52)
- [Source: ARCHITECTURE-SPINE.md#AD-7 — Fault-Tolerant Pipeline Execution](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L76)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References

### Completion Notes List

- Initialize python 3.11 project using uv.
- Create data/ and src/ folders.
- Create data/blogs.yaml with sample URLs.

### File List

- `.python-version`
- `pyproject.toml`
- `README.md`
- `data/blogs.yaml`
- `src/__init__.py`
