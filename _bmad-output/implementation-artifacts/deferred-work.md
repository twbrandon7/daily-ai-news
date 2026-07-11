## Deferred from: code review of 1-1-local-blog-scraper-parser.md (2026-07-11)

- Sequential crawl execution: Crawler crawls sequentially instead of concurrently. Concurrency might be optimization but isn't required by spec.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-gemini-powered-structured-technical-summarization.md`
  summary: No timeout/retry/backoff around ADK runner.run_async — a hung or rate-limited call stalls the whole pipeline.
  evidence: runner.run_async is awaited in a bare async-for loop with no asyncio.wait_for or retry wrapper; any Gemini network hang blocks the pipeline indefinitely.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-gemini-powered-structured-technical-summarization.md`
  summary: Article body sent to Gemini unbounded — very long crawls can hit token limits silently.
  evidence: user_message_text = f"Title: {title}\n\nBody:\n{body}" with no truncation; long crawl4AI markdown outputs can exceed model context windows.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-gemini-powered-structured-technical-summarization.md`
  summary: LlmAgent + Runner + InMemorySessionService are re-created per article — unnecessary overhead for multi-article runs.
  evidence: All three objects are instantiated inside summarize_article() on every call; should be created once and reused across articles in the pipeline run.
