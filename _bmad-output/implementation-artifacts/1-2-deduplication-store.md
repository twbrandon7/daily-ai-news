---
baseline_commit: 09d7234c8dffc0b153a48128963c61e7d79d934d
---
# Story 1.2: Deduplication Store

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want the pipeline to cross-reference fetched post URLs with a JSON store,
so that the system only processes new articles and avoids duplicate summaries.

## Acceptance Criteria

1. **Given** a deduplication file at `data/fetched_posts.json` containing previously processed URLs
2. **When** the pipeline processes crawled URLs
3. **Then** it skips any URL already recorded in the JSON file
4. **And** logs skipped URLs to stdout
5. **And** appends new URLs to the JSON file only after successful processing.

## Tasks / Subtasks

- [x] Task 1: Deduplication Store Initialization and Loading (AC: #1)
  - [x] Load existing URLs from `data/fetched_posts.json` if it exists.
  - [x] Fallback to an empty list/set if the file does not exist or is invalid.
- [x] Task 2: Deduplication Filtering in Pipeline execution (AC: #2, #3, #4)
  - [x] Check if the URL to crawl exists in the deduplication store.
  - [x] If the URL exists, skip crawling and print "Skipping already crawled URL: <url>" to stdout.
- [x] Task 3: Deduplication Store Update & Saving (AC: #5)
  - [x] Append new successfully processed URLs to the deduplication store.
  - [x] Save the updated list back to `data/fetched_posts.json` in a structured JSON format (e.g. array of strings).
- [x] Task 4: Unit Testing (AC: #1, #3, #4, #5)
  - [x] Add tests in `tests/test_pipeline.py` that mock the presence of the deduplication store file.
  - [x] Test that existing URLs are correctly filtered out.
  - [x] Test that new crawled URLs are correctly appended and stored.

## Dev Notes

- **AD-1 (Pipes-and-Filters Execution)**: Keep the deduplication step as a distinct filtering function/logic within the pipeline.
- **AD-3 (YAML Registry & JSON Deduplication Store)**: Persist the deduplication data strictly in `data/fetched_posts.json`.
- **AD-7 (Fault-Tolerant Pipeline)**: Ensure that write failures or format errors on the deduplication store do not disrupt future pipeline runs, but are handled cleanly.
- **State Preservation**: The JSON file is the only state keeper in the pipeline execution (stateless run).

### Project Structure Notes

- Deduplication store path: `data/fetched_posts.json`
- Pipeline entrypoint: `src/pipeline.py`
- Test suite: `tests/test_pipeline.py`

### References

- [Source: epics.md#Story 1.2: Deduplication Store](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/epics.md#L101)
- [Source: SPEC.md#CAP-2](file:///home/clx/projects/daily-ai-news/_bmad-output/specs/spec-daily-ai-news/SPEC.md#L25)
- [Source: ARCHITECTURE-SPINE.md#AD-3 — YAML Registry & JSON Deduplication Store](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L52)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References

### Completion Notes List

- Implement `load_deduplication_store` to parse JSON from `data/fetched_posts.json` with fallback on format errors or missing file.
- Implement `save_deduplication_store` to write URLs back in a structured sorted JSON array.
- Integrate deduplication filtering in `pipeline.py` main crawler loop.
- Log skipped URLs to stdout using the exact prefix `Skipping already crawled URL: <url>`.
- Update unit tests with robust mocking/integration tests using `tmp_path` and `monkeypatch`.

### File List

- `src/pipeline.py`
- `tests/test_pipeline.py`

### Review Findings

- [x] [Review][Patch] Deduplication store updated even when saving parsed articles fails [src/pipeline.py:238-251]
- [x] [Review][Patch] Non-atomic file write in save_deduplication_store [src/pipeline.py:37-46]
- [x] [Review][Patch] Silently ignoring non-list or invalid JSON in deduplication store [src/pipeline.py:24-35]
- [x] [Review][Patch] Missing exception safety for saving dedup_store on crawl loop failure [src/pipeline.py:213-251]
- [x] [Review][Patch] URL formatting differences bypass deduplication checks [src/pipeline.py:215]

