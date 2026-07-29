---
title: Save individual parsed articles to data/parsed/{url_hash}.json
type: feature
created: 2026-07-29
status: 'done'
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

### Review Findings

- [~] [Review][Decision] Stale parsed files survive rerun — resolved: accumulate all-time is intentional; each article keyed by URL hash, different daily summaries tracked by Hugo content, not by directory state.
- [x] [Review][Patch] No test asserts `data/parsed_articles.json` is absent — "Never" constraint has no test coverage. Code could reintroduce monolith write and most tests would still pass. `tests/test_pipeline.py`
- [x] [Review][Patch] No test verifies filename equals `get_url_hash(url)` — tests count files and check content but do not assert the file is named `<hash>.json`. `tests/test_pipeline.py`
- [x] [Review][Patch] Stale comments/test descriptions still mention `parsed_articles.json` — test intent contradicts new contract. `tests/test_pipeline.py`
- [x] [Review][Patch] `spec-rss-crawler-standalone-files.md` AC still references `data/parsed_articles.json` — spec internally inconsistent with CAP-10. `_bmad-output/implementation-artifacts/spec-rss-crawler-standalone-files.md`
- [x] [Review][Defer] Non-atomic write — partial batch failure leaves orphan files, no rollback. `src/pipeline.py:657-663` — deferred, pre-existing
- [x] [Review][Defer] Swallowed write failures — pipeline exits success when file write errors occur. `src/pipeline.py:665-666` — deferred, pre-existing
- [x] [Review][Defer] Old `data/parsed_articles.json` may persist on existing deployments after migration. `src/pipeline.py` — deferred, pre-existing
- [x] [Review][Defer] Missing `item['url']` key aborts full batch on malformed input. `src/pipeline.py:659` — deferred, pre-existing
- [x] [Review][Defer] MD5 hash collision would silently overwrite an article's parsed file. `src/pipeline.py:659-660` — deferred, pre-existing

