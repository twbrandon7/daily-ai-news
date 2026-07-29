---
title: 'Run Tracking Registry and Summary Page Isolation'
type: 'feature'
created: '2026-07-29'
status: 'done'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `run_publish()` currently loads all articles from `data/translated/*.json` indiscriminately, causing all historical summaries to dump into every newly generated summary page.

**Approach:** Introduce `data/runs.json` to track processed article hashes and publication status (`published: false/true`) per run date (`YYYY-MM-DD`). In `run_publish()`, iterate over all unpublished runs, writing date-isolated posts for each run while preserving all historical data files.

## Boundaries & Constraints

**Always:**
- Record article hashes under `runs[date_str]["articles"]` with `"published": false` in `data/runs.json`.
- Preserve all intermediate data files under `data/crawled/`, `data/summarized/`, `data/translated/`, and `data/parsed/`.
- Process and publish all unpublished runs when `run_publish()` executes.

**Ask First:**
- Modifying `content/` layout or directory structure.

**Never:**
- Delete or overwrite historical JSON files in `data/crawled/`, `data/summarized/`, or `data/translated/`.
- Mix summaries from different run dates into a single daily post file.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Single Run Publish | 1 unpublished run in `data/runs.json` | Post generated with only run's articles; `published` set to `true` | Log error, raise exception |
| Multiple Unpublished Runs | 2 unpublished runs (e.g. 2026-07-28, 2026-07-29) in `runs.json` | Both post files (`2026-07-28.md`, `2026-07-29.md`) generated independently with their respective articles; both marked `published: true` | Partial failure cleanup |
| No Unpublished Runs | All runs marked `published: true` | Skip publishing; output "No unpublished runs to publish" | Clean return |

</frozen-after-approval>

## Code Map

- `src/pipeline.py` -- Pipeline execution logic, `data/runs.json` load/save helpers, run tracking in `run_crawl()`, `run_summarize()`, `run_translate()`, and unpublished run processing in `run_publish()`.
- `tests/test_pipeline.py` -- Unit tests for run registry read/write, per-run summary post isolation, and multi-day unpublished run processing.

## Tasks & Acceptance

**Execution:**
- [x] `src/pipeline.py` -- Implement `load_runs_registry()` and `save_runs_registry()`, register hashes during crawl/summarize/translate, and refactor `run_publish()` to process unpublished runs from `data/runs.json`.
- [x] `tests/test_pipeline.py` -- Add unit tests for `data/runs.json` management, per-run daily post isolation, and multi-day unpublished run processing.


**Acceptance Criteria:**
- Given `data/runs.json` has an unpublished run, when `run_publish()` runs, then `content/en/posts/<date>.md` and `content/zh-tw/posts/<date>.md` contain ONLY articles registered for that run.
- Given multiple unpublished runs exist in `data/runs.json`, when `run_publish()` runs, then a post file is created for each unpublished date with its corresponding articles, and all are marked `published: true`.
- Given articles are published, then all files in `data/crawled/`, `data/summarized/`, and `data/translated/` remain preserved.

## Verification

**Commands:**
- `.venv/bin/pytest` -- expected: All unit tests pass cleanly without errors.
