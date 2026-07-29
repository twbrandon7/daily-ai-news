---
title: Save individual parsed articles to data/parsed/{url_hash}.json
type: feature
created: 2026-07-29
status: 'done'
baseline_commit: 'a31ec4fdcea5e205bef20c444a4919b7355fc4c4'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Currently `run_publish()` squashes all published articles into a single `data/parsed_articles.json` file instead of storing standalone parsed article files.

**Approach:** Save each published article into `data/parsed/{url_hash}.json` during `run_publish()` in `src/pipeline.py`, omit generating `data/parsed_articles.json`, and update pipeline unit tests.

## Boundaries & Constraints

**Always:** Save individual parsed article JSON files to `data/parsed/{url_hash}.json` matching schema. Ensure directory `data/parsed` exists.

**Ask First:** Changing schema of parsed article JSON or altering other directories (`data/crawled`, `data/summarized`, `data/translated`).

**Never:** Produce or overwrite monolithic `data/parsed_articles.json`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Publish with articles | List of translated articles | Creates `data/parsed/{url_hash}.json` for each article | Log error if file write fails |
| Publish empty articles | Empty translated articles list | Creates empty `data/parsed` directory, no error | Exit cleanly |

</frozen-after-approval>

## Code Map

- `src/pipeline.py` -- Modify `run_publish()` to save each article into `data/parsed/{url_hash}.json` and remove `PARSED_ARTICLES_PATH` creation.
- `tests/test_pipeline.py` -- Update pipeline deduplication test to check `data/parsed/{url_hash}.json` output instead of `data/parsed_articles.json`.

## Tasks & Acceptance

**Execution:**
- [x] `src/pipeline.py` -- Update `run_publish()` to write standalone files to `data/parsed/{url_hash}.json` and remove `PARSED_ARTICLES_PATH` saving logic.
- [x] `tests/test_pipeline.py` -- Update test assertions from `parsed_articles.json` to `data/parsed/{url_hash}.json`.

**Acceptance Criteria:**
- Given `run_publish()` runs, when articles exist, then each article is saved to `data/parsed/{url_hash}.json` and `data/parsed_articles.json` is not created.
- Given pytest runs, when `pytest tests/` is executed, then all tests pass.

## Verification

**Commands:**
- `pytest tests/test_pipeline.py` -- expected: All unit tests pass.

## Suggested Review Order

**Pipeline Publishing Changes**

- Update `run_publish()` to write standalone files to `data/parsed/{url_hash}.json` and omit monolithic file.
  [`pipeline.py:657`](../../src/pipeline.py#L657)

**Pipeline Test Updates**

- Update unit test assertions to verify `data/parsed/*.json` outputs.
  [`test_pipeline.py:267`](../../tests/test_pipeline.py#L267)

