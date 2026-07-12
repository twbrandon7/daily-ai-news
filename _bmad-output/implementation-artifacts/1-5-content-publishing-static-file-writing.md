---
baseline_commit: 32fbb7f50b26b5d77ee6baba9c8e143a2a6b2002
---
# Story 1.5: Content Publishing & Static File Writing

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a site maintainer,
I want compiled daily summaries saved as structured frontmatter YAML arrays in daily markdown files,
so that the static site generator can read and display them.

## Acceptance Criteria

1. **Given** processed English and Traditional Chinese summaries for the day,
   **When** the pipeline writes the daily output files,
   **Then** it creates `content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md` in the project root.
2. **And** it saves the summaries as a YAML array under the `articles` key in the frontmatter of these files.
3. **Given** multiple successfully processed articles for the day,
   **When** the pipeline publishes the content,
   **Then** it generates a short, day-level highlight summary (in English) from the day's compiled article set (titles + TL;DRs) using Gemini via Google ADK (`gemini-2.0-flash`).
4. **And** it translates this daily highlight into Traditional Chinese (Taiwan) using the translator (retaining standard English terms: prompt, fine-tuning, RAG, agent, pipeline, checkpoint, embeddings, token).
5. **And** it saves the highlight under the `daily_highlight` key in the frontmatter of the respective daily posts.
6. **Given** no articles were successfully processed today (e.g., all skipped due to deduplication),
   **When** the pipeline finishes executing,
   **Then** it does NOT create or modify any daily post files at `content/en/posts/YYYY-MM-DD.md` or `content/zh-tw/posts/YYYY-MM-DD.md`, and exits successfully.
7. **Given** a file write or highlight generation failure,
   **When** the pipeline processes the write stage,
   **Then** it logs a structured JSON error to stderr with `stage: "publish"` containing the error message, does NOT commit any partial updates for today's post, and fails the pipeline run (exit code 1).

## Tasks / Subtasks

- [ ] Task 1: Highlight Generator & File Publisher Module (AC: #1, #2, #3, #4, #5, #6, #7)
  - [ ] Implement `src/publisher.py` with `generate_daily_highlight(articles: list[dict]) -> str | None` and `write_daily_posts(date_str: str, articles: list[dict]) -> bool`.
  - [ ] Use `google-adk` (`LlmAgent`, `Runner`, `InMemorySessionService`) and `gemini-2.0-flash` to generate the English daily highlight, and reuse/integrate translation logic for `zh-tw`.
  - [ ] Format markdown files with YAML frontmatter containing `title`, `date`, `daily_highlight`, and `articles` array.
  - [ ] Ensure that if `articles` list is empty, the function returns immediately without writing files.
  - [ ] Log structured JSON to stderr with `stage: "publish"` on any failure.
- [ ] Task 2: Pipeline Integration (AC: #1, #6, #7)
  - [ ] Import `write_daily_posts` in `src/pipeline.py`.
  - [ ] Extract today's date in YYYY-MM-DD format (either current date, or based on the articles' publication date if consistent).
  - [ ] Call `write_daily_posts(date_str, successes)` after the crawl/summarize/translate loop finishes.
  - [ ] If publishing fails, log and exit with status code 1.
- [ ] Task 3: Implement Unit & Integration Tests (AC: all)
  - [ ] Create `tests/test_publisher.py` unit testing highlight generation, markdown file writing, YAML frontmatter formatting, and empty-list handling.
  - [ ] Add integration tests in `tests/test_pipeline.py` verifying that successful pipeline execution writes the bilingual daily posts, and that failures exit/log correctly.

## Dev Notes

- **Unified Project Structure (AD-6):** Create directory structure `content/en/posts` and `content/zh-tw/posts` if they do not exist.
- **Pipes-and-Filters (AD-1):** Publishing is a distinct stage after translation.
- **Fault Tolerance (AD-7):** Write failures or highlight generation failures must fail the entire pipeline run (exit code 1) to prevent incomplete commits/deploys.
- **YAML Formatting:** Use `yaml.dump` with proper flow style (`default_flow_style=False`) and custom representers if needed to ensure clean block-format output.
- **Bilingual Highlight Structure:** Traditional Chinese daily highlight should use Traditional Chinese (Taiwan) localization while keeping standard English developer terms verbatim.

### Project Structure Notes

- New module: `src/publisher.py`
- New test suite: `tests/test_publisher.py`
- Modify: `src/pipeline.py` and `tests/test_pipeline.py`

### References

- [Source: epics.md#Story 1.5: Content Publishing & Static File Writing](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/epics.md#L141)
- [Source: ARCHITECTURE-SPINE.md#AD-6 — Structured Frontmatter Storage](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L70)
- [Source: epic-1-context.md#Requirements & Constraints](file:///home/clx/projects/daily-ai-news/_bmad-output/implementation-artifacts/epic-1-context.md#L18)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References

### Completion Notes List

### File List
