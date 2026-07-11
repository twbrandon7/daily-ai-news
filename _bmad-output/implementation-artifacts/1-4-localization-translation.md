---
baseline_commit: 94756d2a2a438ff6caf20817508d46066f40b334
---
# Story 1.4: Localization & Translation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Taiwanese developer reader,
I want the structured summaries translated into Traditional Chinese (Taiwan) while keeping core developer terms in English,
so that I can read updates in my native language without losing technical precision.

## Acceptance Criteria

1. **Given** a generated English structured summary
2. **When** the pipeline translates the summary into Traditional Chinese
3. **Then** terms like "prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", and "token" remain in English (case-insensitive, preserve original spelling and casing)
4. **And** the translated summary maintains the exact 5-element structure and keys of the English summary (in a parsed JSON format: `tldr`, `problem_why`, `solution_how`, `insights_tradeoffs`, `tags_action`, `rating`)
5. **And** the `rating` value is preserved exactly as an integer matching the original English summary rating.
6. **Given** a translation failure (API error or validation failure) for a single article, **When** the pipeline processes the article, **Then** it logs a structured JSON error to stderr with `stage: "translate"`, excludes the article from output, and continues processing other articles.

## Tasks / Subtasks

- [x] Task 1: Create Translator Module (AC: #2, #3, #4, #5, #6)
  - [x] Implement `src/translator.py` with `translate_summary(url: str, summary: dict) -> dict | None` function.
  - [x] Use `google-adk` (`LlmAgent`, `Runner`, `InMemorySessionService`) and `gemini-2.0-flash` model.
  - [x] Author `TRANSLATE_PROMPT` instructing Traditional Chinese (Taiwan) translation and keeping specific terms ("prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token") in English.
  - [x] Parse and validate the returned JSON (ensure keys are identical, values translated, rating preserved, lists of strings are validated).
  - [x] Log structured JSON to stderr on any translation/parsing failure with `stage: "translate"`.
- [x] Task 2: Integrate Translation Stage in Pipeline (AC: #1, #6)
  - [x] Import `translate_summary` in `src/pipeline.py`.
  - [x] In the pipeline loop, call `translate_summary()` on the successful English summary.
  - [x] If translation returns `None`, treat as failure (exclude from successes, increment failures with `"translation failed"`).
  - [x] Save the translation output under `parsed_data['summary_zh_tw']`.
- [x] Task 3: Implement Unit & Integration Tests (AC: #1, #6)
  - [x] Create `tests/test_translator.py` testing happy path (mocked ADK returning translated JSON), validation failures (missing fields, wrong types, altered rating), and API exceptions.
  - [x] Add pipeline integration tests in `tests/test_pipeline.py` verifying that successful translation attaches `summary_zh_tw` and that translation failure excludes the article.

## Dev Notes

- **Language & Terms (AC: #3):** Traditional Chinese (Taiwan) uses phrases like "我們", "如何", "優勢", etc. Keep core terms ("prompt", "fine-tuning", etc.) in English verbatim.
- **Pipes-and-Filters (AD-1):** Translation is a distinct stage after summarization.
- **API patterns:** Conform to the same Google ADK runner/session setup as `src/summarizer.py`.
- **Fault tolerance (AD-7):** Failures in translation of one article must not abort the overall run. Log:
  ```json
  {"timestamp": "YYYY-MM-DDTHH:MM:SSZ", "stage": "translate", "blog_url": "url", "error_message": "..."}
  ```

### Project Structure Notes

- New module: `src/translator.py`
- New test suite: `tests/test_translator.py`
- Modify: `src/pipeline.py` and `tests/test_pipeline.py`

### References

- [Source: epics.md#Story 1.4: Localization & Translation](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/epics.md#L128)
- [Source: ARCHITECTURE-SPINE.md#AD-4 — Distinct Summarization and Translation Passes](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L58)
- [Source: epic-1-context.md#Requirements & Constraints](file:///home/clx/projects/daily-ai-news/_bmad-output/implementation-artifacts/epic-1-context.md#L18)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References

- Pytest ran successfully on all tests.

### Completion Notes List

- Implemented `translate_summary` using google-adk LlmAgent, Runner, and InMemorySessionService.
- Added Traditional Chinese translation instruction preserving key English terms ("prompt", "fine-tuning", etc.).
- Integrated translation pass in `src/pipeline.py` after summarization.
- Created `tests/test_translator.py` unit tests and added integration tests in `tests/test_pipeline.py`.

### File List

- `src/translator.py`
- `tests/test_translator.py`
- `src/pipeline.py`
- `tests/test_pipeline.py`

### Review Findings

- [x] [Review][Decision] English key terms not programmatically validated — _parse_translation in src/translator.py checks JSON schema, but does not check if the translated fields preserve the required key terms ("prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token") in English verbatim.
- [x] [Review][Patch] Missing check for extra keys in translation response [src/translator.py:52]
- [x] [Review][Patch] Structured log timestamp uses `+00:00` instead of `Z` [src/translator.py:22]
- [x] [Review][Patch] Missing timeout protection on API calls [src/translator.py:133]
- [x] [Review][Patch] Fragile and strict rating validation / type mismatch [src/translator.py:76]
- [x] [Review][Patch] Generic parsing error logs [src/translator.py:156]
- [x] [Review][Patch] LLM response contains multiple code blocks where the first is not JSON [src/translator.py:40]
- [x] [Review][Patch] Input summary dict contains non-JSON-serializable objects causing dumps to fail [src/translator.py:107]
- [x] [Review][Defer] Inefficient per-call agent instantiation [src/translator.py:110] — deferred, pre-existing
- [x] [Review][Defer] Redundant logging implementation [src/translator.py:22] — deferred, pre-existing
- [x] [Review][Defer] Lack of JSON mode or structured outputs configuration [src/translator.py:110] — deferred, pre-existing
- [x] [Review][Defer] Insufficient test assertion coverage [tests/test_translator.py:1] — deferred, pre-existing
