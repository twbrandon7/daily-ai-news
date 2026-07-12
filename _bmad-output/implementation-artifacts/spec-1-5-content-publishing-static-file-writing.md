---
title: 'Content Publishing & Static File Writing'
type: 'feature'
created: '2026-07-12T15:33:29+08:00'
status: 'done'
baseline_commit: '32fbb7f50b26b5d77ee6baba9c8e143a2a6b2002'
final_commit: '6276cc6f96a478c91961058141a3903c36a45674'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** The pipeline crawls, summarizes, and translates articles but does not save them to disk as daily markdown post files or generate a daily highlight summary, leaving the static Hugo site without any content to render.

**Approach:** Implement `src/publisher.py` to generate an English daily highlight summary using Gemini via Google ADK (`gemini-2.0-flash`), translate it to Traditional Chinese (Taiwan), and write bilingual markdown files with the summaries and highlights in YAML frontmatter. Integrate this publisher as a post-translation stage in `src/pipeline.py`.

## Boundaries & Constraints

**Always:**
- Create daily post files at `content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md`.
- Save the summaries list under the `articles` key and the daily highlight under the `daily_highlight` key in the frontmatter of these files.
- Automatically create the directories `content/en/posts` and `content/zh-tw/posts` if they do not exist.
- Use `google-adk` (`LlmAgent`, `Runner`, `InMemorySessionService`) and `gemini-2.0-flash` to generate the English daily highlight.
- Translate this daily highlight into Traditional Chinese (Taiwan) utilizing translation logic that preserves English terms (`prompt`, `fine-tuning`, `RAG`, `agent`, `pipeline`, `checkpoint`, `embeddings`, `token`) case-insensitively.
- If the `articles` list is empty, exit immediately without writing any files or calling Gemini.
- On any write or highlight generation failure, log a structured JSON error to stderr with `stage: "publish"` and fail the pipeline run (exit code 1).
- Format markdown frontmatter using YAML block style (`default_flow_style=False`).

**Block If:**
- `GOOGLE_API_KEY` is missing when highlight generation or translation is initiated.

**Never:**
- Do not write or modify any daily post files if no articles were successfully processed for the day.
- Do not commit any partial updates for today's posts if publishing fails.
- Do not use third-party libraries for YAML/JSON other than python-yaml and standard json.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy Path | `date_str="2026-07-12"`, `articles=[{"title": "...", "summary": "...", "summary_zh_tw": "..."}]` | Creates `content/en/posts/2026-07-12.md` and `content/zh-tw/posts/2026-07-12.md` containing `articles` and `daily_highlight` in frontmatter. | No error expected. |
| No Articles | `date_str="2026-07-12"`, `articles=[]` | Exits successfully. No files created or modified. | No error expected. |
| Highlight Generation Failure | `date_str="2026-07-12"`, `articles=[...]`, ADK API error | Exits with status code 1. No files created or modified. | Catches exception, logs structured JSON with `stage: "publish"`. |
| Disk Write Failure | `date_str="2026-07-12"`, `articles=[...]`, disk full / permission error | Exits with status code 1. Cleans up any partially written files. | Catches OSError, logs structured JSON with `stage: "publish"`. |

</intent-contract>

## Code Map

- `src/publisher.py` -- Implement highlight generation and markdown writing.
- `src/pipeline.py` -- Integrate publisher into pipeline filters.
- `tests/test_publisher.py` -- Unit tests for highlight generation and markdown writing.
- `tests/test_pipeline.py` -- Integration tests for content publishing.

## Tasks & Acceptance

**Execution:**
- [x] `src/publisher.py` -- Implement highlight generation and markdown writer -- Encapsulate publishing logic.
- [x] `src/pipeline.py` -- Integrate publisher into pipeline -- Execute publishing after translation.
- [x] `tests/test_publisher.py` -- Implement unit tests -- Test happy paths and failures.
- [x] `tests/test_pipeline.py` -- Implement integration tests -- Test end-to-end publishing.

**Acceptance Criteria:**
- Given processed English and Traditional Chinese summaries for the day, when the pipeline writes the daily output files, then it creates `content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md` in the project root.
- And it saves the summaries as a YAML array under the `articles` key in the frontmatter of these files.
- Given multiple successfully processed articles for the day, when the pipeline publishes the content, then it generates a short, day-level highlight summary (in English) from the day's compiled article set (titles + TL;DRs) using Gemini via Google ADK (`gemini-2.0-flash`).
- And it translates this daily highlight into Traditional Chinese (Taiwan) using the translator (retaining standard English terms: prompt, fine-tuning, RAG, agent, pipeline, checkpoint, embeddings, token).
- And it saves the highlight under the `daily_highlight` key in the frontmatter of the respective daily posts.
- Given no articles were successfully processed today (e.g., all skipped due to deduplication), when the pipeline finishes executing, then it does NOT create or modify any daily post files at `content/en/posts/YYYY-MM-DD.md` or `content/zh-tw/posts/YYYY-MM-DD.md`, and exits successfully.
- Given a file write or highlight generation failure, when the pipeline processes the write stage, then it logs a structured JSON error to stderr with `stage: "publish"` containing the error message, does NOT commit any partial updates for today's post, and fails the pipeline run (exit code 1).

## Spec Change Log

None.

## Review Triage Log

### 2026-07-12T15:33:29+08:00 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 2, medium 1, low 1)
- defer: 1: (low 1)
- reject: 2: (low 2)
- addressed_findings:
  - `[high]` `[patch]` Substring match in `_validate_highlight_terms` causes false alarms. Changed to use word boundary regex search.
  - `[high]` `[patch]` `generate_daily_highlight` fails with `AttributeError` when `summary` is `None`. Changed to check `art.get("summary") or {}`.
  - `[medium]` `[patch]` Missing trailing newlines in output markdown posts. Added trailing newline to YAML block frontmatter.
  - `[low]` `[patch]` Unsafe `yaml.dump` call. Changed to `yaml.safe_dump`.

## Design Notes

None.

## Verification

**Commands:**
- `pytest tests/test_publisher.py` -- expected: Unit tests pass.
- `pytest tests/test_pipeline.py` -- expected: Pipeline integration tests pass.

## Auto Run Result

### Summary of Implemented Change
Implemented content publishing and daily static file writing for the daily news pipeline. It crawls articles, translates and localizes daily highlight summaries using Gemini via Google ADK (`gemini-2.0-flash`), and outputs them into Hugo content files.

### Files Changed
- `src/publisher.py`: New module to generate highlights, translate highlights, and write daily bilingual markdown post files.
- `src/pipeline.py`: Integrated `write_daily_posts` into the pipeline filter sequence.
- `tests/test_publisher.py`: New test suite for highlight generator and publisher.
- `tests/test_pipeline.py`: Added integration tests for publishing failures and successful runs.
- `_bmad-output/implementation-artifacts/deferred-work.md`: Logged minor deferred code review suggestions.

### Review Findings Breakdown
- Patches applied: 4 (regex term matching, None safety guard, trailing newline, safe YAML dump).
- Items deferred: 1 (Session service, Runner, and Agent instantiated per call).
- Items rejected: 2 (sys.exit testing logic, base folder cleanup).

### Follow-up Review Recommendation
`false`. The review findings were minor patches easily covered by the test suite, with no design or API changes.

### Verification Performed
Ran `uv run pytest` successfully:
- All 35 tests passed.

### Residual Risks
None.
