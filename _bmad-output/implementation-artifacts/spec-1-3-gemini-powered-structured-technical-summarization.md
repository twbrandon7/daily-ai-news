---
title: 'Gemini-powered Structured Technical Summarization'
type: 'feature'
created: '2026-07-11T20:50:48+08:00'
status: 'in-review'
baseline_commit: '1346a92822533da48dee65ccd878fce499b76e06'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** The pipeline crawls and deduplicates articles but produces no AI-generated content. New articles stall after deduplication with no structured summaries, making the site unable to render any article content.

**Approach:** Add `src/summarizer.py` with a `summarize_article()` function backed by Google ADK + Gemini. Integrate as the next pipeline stage after deduplication. English summaries (5-element structure + 1–5 star rating) are attached to each article dict and persisted to `data/parsed_articles.json`.

## Boundaries & Constraints

**Always:**
- Use the `google-adk` package (not raw `google-generativeai`) per AD-4.
- Summarization (English) and translation (Chinese) are distinct steps; this story implements English summarization only.
- Single-article summarization failures log structured JSON with `stage: "summarize"` and do not block remaining articles.
- Missing `GOOGLE_API_KEY` environment variable must cause the pipeline to exit with a clear error at startup (before crawling).
- Structured summary must contain exactly: `tldr` (str), `problem_why` (str), `solution_how` (str), `insights_tradeoffs` (`{pros: list[str], cons: list[str]}`), `tags_action` (list[str]), `rating` (int 1–5).

**Block If:**
- The google-adk public API surface differs significantly from the runner/session/agent pattern (e.g., no `Runner`, no `InMemorySessionService`) — halt with status `blocked` and blocking condition `google-adk API incompatible`.

**Never:**
- Translate summaries to Chinese (story 1.4).
- Write Hugo content files (story 1.5).
- Combine summarize + translate in one LLM prompt.
- Use a streaming API; await the full response before parsing.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Valid article body | Non-empty `body`, non-empty `title` | Dict with all 6 fields; `rating` is 1–5 int | No error expected |
| Empty body | `body=""`, any title | `None` | Log structured JSON error, stage=`summarize`, skip article |
| ADK/API call raises exception | Any article | `None` | Log structured JSON error, stage=`summarize`, skip article |
| LLM response missing or unparseable fields | Valid body, malformed model response | `None` | Log parse error, stage=`summarize`, skip article |
| `GOOGLE_API_KEY` not set | Pipeline startup | Exit with error message to stderr, non-zero exit code | No crawl initiated |

</intent-contract>

## Code Map

- `src/pipeline.py` — orchestration; add `GOOGLE_API_KEY` check at startup, call `summarize_article()` per successful crawl, attach summary to article dict
- `src/summarizer.py` — new; `summarize_article(body: str, title: str) -> dict | None` using google-adk LlmAgent + Runner
- `pyproject.toml` — add `google-adk>=0.1` to production dependencies
- `tests/test_summarizer.py` — new; unit tests for `summarize_article()`
- `data/parsed_articles.json` — output; each article object gains a `summary` key

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml` -- add `google-adk>=0.1` to `[project] dependencies` -- required for ADK import
- [x] `src/summarizer.py` -- create module: define `summarize_article(body: str, title: str) -> dict | None` using google-adk `LlmAgent` + `Runner` + `InMemorySessionService`; prompt instructs Gemini to return a JSON block with `tldr`, `problem_why`, `solution_how`, `insights_tradeoffs` (object with `pros` and `cons` arrays), `tags_action` (array), and `rating` (int 1–5); parse JSON from response; return `None` and log on any failure -- encapsulates all ADK interaction
- [x] `src/pipeline.py` -- add `GOOGLE_API_KEY` presence check at startup (before loading blogs); call `summarize_article(parsed_data['body'], parsed_data['title'])` immediately after each successful crawl; attach the result as `parsed_data['summary']`; if result is `None`, log structured JSON error and exclude the article from `successes` -- integrates summarization into the pipeline flow
- [x] `tests/test_summarizer.py` -- add unit tests: (1) happy path with mocked ADK runner returning valid JSON, (2) empty body returns `None`, (3) API exception returns `None` and logs error, (4) malformed JSON response returns `None` -- validates summarizer in isolation

**Acceptance Criteria:**
- Given a non-empty article body and title, when `summarize_article()` is called, then it returns a dict with exactly: `tldr` (non-empty str), `problem_why` (non-empty str), `solution_how` (non-empty str), `insights_tradeoffs` (dict with `pros` list and `cons` list), `tags_action` (non-empty list), `rating` (int between 1 and 5 inclusive).
- Given a summarization ADK call that raises an exception, when the pipeline processes the article, then the article is excluded from output and a structured JSON log entry is written with `stage: "summarize"` and the error message.
- Given an empty `body` string, when `summarize_article("", title)` is called, then it returns `None`.
- Given `GOOGLE_API_KEY` is not set in the environment, when the pipeline runs, then it exits with a non-zero code and an error message to stderr before any crawling begins.
- Given 3 crawled articles where 1 summarization fails, when the pipeline completes, then `data/parsed_articles.json` contains exactly 2 articles (each with a `summary` field) and 1 failure is logged.

## Spec Change Log

## Review Triage Log

### 2026-07-11 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 8: (high 1, medium 4, low 3)
- defer: 3: (medium 2, low 1)
- reject: 4
- addressed_findings:
  - `[high]` `[patch]` pipeline.py called `log_error()` (stage=crawl) on summarization failure while summarize_article already logs internally — removed redundant double-log
  - `[medium]` `[patch]` Whitespace-only GOOGLE_API_KEY passed env check — added `.strip()` guard
  - `[medium]` `[patch]` `_parse_summary` regex only matched `\`\`\`json` (lowercase) — made case-insensitive and also matched generic ` ``` ` fencing
  - `[medium]` `[patch]` Final response read only `parts[0].text` — changed to concat all parts with text content
  - `[medium]` `[patch]` Empty-string values for tldr/problem_why/solution_how passed field validation — added `.strip()` check
  - `[low]` `[patch]` `isinstance(True, int)` returns True in Python — changed to `type(rating) is int` to exclude booleans
  - `[low]` `[patch]` List items in pros/cons/tags_action not validated as strings — added per-item type check
  - `[low]` `[patch]` Missing pipeline integration test for summarization failure exclusion (AC5) — added `test_pipeline_summarization_failure_excludes_article`

## Design Notes

The google-adk runner pattern requires a session service and a runner to invoke an `LlmAgent`. A minimal usage looks like:

```python
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

agent = LlmAgent(model="gemini-2.0-flash", instruction=SUMMARIZE_PROMPT)
session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name="summarizer", session_service=session_service)
session = await session_service.create_session(app_name="summarizer", user_id="pipeline")
async for event in runner.run_async(user_id="pipeline", session_id=session.id, new_message=...):
    if event.is_final_response():
        response_text = event.content.parts[0].text
```

Extract the JSON block from `response_text` using a regex for ` ```json ... ``` ` or a direct `json.loads()` attempt. Keep the prompt concise and instruct the model to return only valid JSON.

## Verification

**Commands:**
- `uv run pytest tests/test_summarizer.py -v` -- expected: all tests pass
- `uv run pytest tests/test_pipeline.py -v` -- expected: all existing tests pass (no regressions)
