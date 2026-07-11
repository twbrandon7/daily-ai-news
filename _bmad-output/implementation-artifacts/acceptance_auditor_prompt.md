# Acceptance Auditor Prompt

You are an Acceptance Auditor. Review the provided diff against the spec/story file and any loaded context docs. Check for: violations of acceptance criteria, deviations from spec intent, missing implementation of specified behavior, contradictions between spec constraints and actual code. Output findings as a Markdown list. Each finding: one-line title, which AC/constraint it violates, and evidence from the diff.

## Story & Spec Context (from 1-4-localization-translation.md)

```markdown
# Story 1.4: Localization & Translation

Status: review

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
```

## Diff

```diff
diff --git a/src/pipeline.py b/src/pipeline.py
index 781b954..164729e 100644
--- a/src/pipeline.py
+++ b/src/pipeline.py
@@ -12,6 +12,7 @@ from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
 from crawl4ai.content_filter_strategy import PruningContentFilter

 from src.summarizer import summarize_article
+from src.translator import translate_summary

 def log_error(blog_url: str, error_message: str):
     """Log error in the required JSON format."""
@@ -266,13 +267,18 @@ async def main():
                         failures.append((url, "summarization failed"))
                     else:
                         parsed_data['summary'] = summary
-                        successes.append(parsed_data)
-                        print(f"Successfully crawled: {url}")
-                        print(f"  Title: {parsed_data['title']}")
-                        print(f"  Author: {parsed_data['author']}")
-                        print(f"  Date: {parsed_data['publication_date']}")
-                        print(f"  Body length: {len(parsed_data['body'])} characters")
-                        print("-" * 40)
+                        translated = await translate_summary(url, summary)
+                        if translated is None:
+                            failures.append((url, "translation failed"))
+                        else:
+                            parsed_data['summary_zh_tw'] = translated
+                            successes.append(parsed_data)
+                            print(f"Successfully crawled: {url}")
+                            print(f"  Title: {parsed_data['title']}")
+                            print(f"  Author: {parsed_data['author']}")
+                            print(f"  Date: {parsed_data['publication_date']}")
+                            print(f"  Body length: {len(parsed_data['body'])} characters")
+                            print("-" * 40)

         # Final reporting
         print(f"\nCrawl execution summary:")
diff --git a/tests/test_pipeline.py b/tests/test_pipeline.py
index bc6d989..2ddcd8a 100644
--- a/tests/test_pipeline.py
+++ b/tests/test_pipeline.py
@@ -206,6 +206,15 @@ async def test_pipeline_deduplication_integration(tmp_path, monkeypatch, capsys)
         "rating": 4,
     }
     monkeypatch.setattr(pipeline, "summarize_article", AsyncMock(return_value=mock_summary))
+    mock_translation = {
+        "tldr": "測試摘要",
+        "problem_why": "測試問題",
+        "solution_how": "測試方案",
+        "insights_tradeoffs": {"pros": ["優點"], "cons": ["缺點"]},
+        "tags_action": ["標籤"],
+        "rating": 4,
+    }
+    monkeypatch.setattr(pipeline, "translate_summary", AsyncMock(return_value=mock_translation))

     # Run pipeline main
     await pipeline.main()
@@ -231,6 +240,7 @@ async def test_pipeline_deduplication_integration(tmp_path, monkeypatch, capsys)
     assert parsed_articles[0]["url"] == "https://new-url.com"
     assert parsed_articles[0]["title"] == "New Title"
     assert parsed_articles[0]["summary"] == mock_summary
+    assert parsed_articles[0]["summary_zh_tw"] == mock_translation

 def test_normalize_url():
     from src.pipeline import normalize_url
@@ -301,6 +311,15 @@ async def test_pipeline_deduplication_failure_does_not_save_dedup(tmp_path, monk
         "rating": 4,
     }
     monkeypatch.setattr(pipeline, "summarize_article", AsyncMock(return_value=mock_summary))
+    mock_translation = {
+        "tldr": "測試摘要",
+        "problem_why": "測試問題",
+        "solution_how": "測試方案",
+        "insights_tradeoffs": {"pros": ["優點"], "cons": ["缺點"]},
+        "tags_action": ["標籤"],
+        "rating": 4,
+    }
+    monkeypatch.setattr(pipeline, "translate_summary", AsyncMock(return_value=mock_translation))

     # Force a failure during saving of parsed_articles.json by mocking open
     import builtins
@@ -377,10 +396,81 @@ async def test_pipeline_summarization_failure_excludes_article(tmp_path, monkeyp

     monkeypatch.setattr(pipeline, "summarize_article", fake_summarize)

+    async def fake_translate(url, summary):
+        return summary
+    monkeypatch.setattr(pipeline, "translate_summary", fake_translate)
+
+    await pipeline.main()
+
+    parsed = json.loads((tmp_path / "data/parsed_articles.json").read_text())
+    assert len(parsed) == 2
+    for article in parsed:
+        assert "summary" in article
+        assert "summary_zh_tw" in article
+        assert "fail" not in article["url"]
+
+
+@pytest.mark.asyncio
+async def test_pipeline_translation_failure_excludes_article(tmp_path, monkeypatch):
+    """
+    Given 3 articles where 1 translation fails, when pipeline runs,
+    then parsed_articles.json contains exactly 2 articles (each with summary and summary_zh_tw)
+    and the failing article is recorded in failures.
+    """
+    import os, json, yaml
+    from src import pipeline
+
+    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
+    monkeypatch.chdir(tmp_path)
+    os.makedirs(tmp_path / "data")
+
+    urls = ["https://ok1.com", "https://fail.com", "https://ok2.com"]
+    (tmp_path / "data/blogs.yaml").write_text(yaml.dump({"blogs": urls}))
+    (tmp_path / "data/fetched_posts.json").write_text("[]")
+
+    def make_crawl_result(url):
+        return MockCrawlResult(
+            success=True,
+            url=url,
+            markdown=f"body of {url}",
+            metadata={"title": f"Title {url}", "author": "A", "article:published_time": "2026-07-11T00:00:00Z"},
+        )
+
+    class MockCrawler:
+        async def arun(self, url, config):
+            return make_crawl_result(url)
+
+    class MockCrawlerCtx:
+        async def __aenter__(self): return MockCrawler()
+        async def __aexit__(self, *_): pass
+
+    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockCrawlerCtx)
+
+    mock_summary = {
+        "tldr": "ok",
+        "problem_why": "p",
+        "solution_how": "s",
+        "insights_tradeoffs": {"pros": ["a"], "cons": ["b"]},
+        "tags_action": ["t"],
+        "rating": 3,
+    }
+
+    async def fake_summarize(url, body, title):
+        return mock_summary
+
+    async def fake_translate(url, summary):
+        if "fail" in url:
+            return None
+        return summary
+
+    monkeypatch.setattr(pipeline, "summarize_article", fake_summarize)
+    monkeypatch.setattr(pipeline, "translate_summary", fake_translate)
+
     await pipeline.main()

     parsed = json.loads((tmp_path / "data/parsed_articles.json").read_text())
     assert len(parsed) == 2
     for article in parsed:
         assert "summary" in article
+        assert "summary_zh_tw" in article
         assert "fail" not in article["url"]
diff --git a/src/translator.py b/src/translator.py
new file mode 100644
index 0000000..1e0145e
--- /dev/null
+++ b/src/translator.py
@@ -0,0 +1,164 @@
+import asyncio
+import datetime
+import json
+import re
+import sys
+
+from google.adk.agents import LlmAgent
+from google.adk.runners import Runner
+from google.adk.sessions import InMemorySessionService
+from google.genai import types as genai_types
+
+TRANSLATE_PROMPT = """You are a professional technical translator. Translate the given English structured JSON summary into Traditional Chinese (Taiwan).
+
+Strict Guidelines:
+1. Translate the values of the fields: "tldr", "problem_why", "solution_how", the list items in "insights_tradeoffs.pros" and "insights_tradeoffs.cons", and the list items in "tags_action".
+2. Keep these technical terms in English verbatim (case-insensitive, do not translate them to Chinese): "prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token".
+3. Do NOT translate or modify the "rating" field value. Preserve it exactly as an integer.
+4. Maintain the exact JSON structure and keys of the input.
+5. Return ONLY a valid JSON object wrapped in ```json ... ``` fencing. Do not include any other text outside the fenced block.
+"""
+
+def _log_translate_error(url: str, error_message: str) -> None:
+    """Log a structured JSON error entry to stderr for translation failures."""
+    log_data = {
+        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
+        "stage": "translate",
+        "blog_url": url,
+        "error_message": error_message,
+    }
+    print(json.dumps(log_data), file=sys.stderr)
+
+def _parse_translation(response_text: str, original_rating: int) -> dict | None:
+    """
+    Parse the JSON translation from a model response string.
+
+    Accepts either a ```json ... ``` fenced block or a bare JSON object.
+    Returns the parsed dict if all required fields are present and valid, else None.
+    """
+    # Try to extract from ```json ... ``` fencing first
+    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
+    if fenced:
+        candidate = fenced.group(1).strip()
+    else:
+        # Fall back to the whole response text
+        candidate = response_text.strip()
+
+    try:
+        data = json.loads(candidate)
+    except (json.JSONDecodeError, ValueError):
+        return None
+
+    # Validate required fields and types
+    if not isinstance(data, dict):
+        return None
+
+    required_str_fields = ("tldr", "problem_why", "solution_how")
+    for field in required_str_fields:
+        value = data.get(field)
+        if not isinstance(value, str) or not value.strip():
+            return None
+
+    it = data.get("insights_tradeoffs")
+    if not isinstance(it, dict):
+        return None
+    if not isinstance(it.get("pros"), list) or not isinstance(it.get("cons"), list):
+        return None
+    if any(not isinstance(x, str) for x in it.get("pros", []) + it.get("cons", [])):
+        return None
+
+    tags = data.get("tags_action")
+    if not isinstance(tags, list):
+        return None
+    if any(not isinstance(x, str) for x in tags):
+        return None
+
+    rating = data.get("rating")
+    if type(rating) is not int or rating != original_rating:
+        return None
+
+    return data
+
+async def translate_summary(url: str, summary: dict) -> dict | None:
+    """
+    Translate an English summary into Traditional Chinese (Taiwan) using Google ADK + Gemini.
+
+    Parameters
+    ----------
+    url : str
+        The article URL (used as identifier in error logs).
+    summary : dict
+        The English structured summary dict.
+
+    Returns
+    -------
+    dict | None
+        The translated summary dict, or None on failure.
+    """
+    if not summary or not isinstance(summary, dict):
+        _log_translate_error(url, "Invalid or empty summary dict for translation.")
+        return None
+
+    original_rating = summary.get("rating")
+    if type(original_rating) is not int:
+        _log_translate_error(url, "Original summary is missing a valid integer rating.")
+        return None
+
+    user_message_text = json.dumps(summary, indent=2)
+
+    try:
+        agent = LlmAgent(
+            model="gemini-2.0-flash",
+            name="translator",
+            instruction=TRANSLATE_PROMPT,
+        )
+        session_service = InMemorySessionService()
+        runner = Runner(
+            agent=agent,
+            app_name="translator",
+            session_service=session_service,
+        )
+
+        session = await session_service.create_session(
+            app_name="translator",
+            user_id="pipeline",
+        )
+
+        new_message = genai_types.Content(
+            role="user",
+            parts=[genai_types.Part.from_text(text=user_message_text)],
+        )
+
+        response_text = None
+        async for event in runner.run_async(
+            user_id="pipeline",
+            session_id=session.id,
+            new_message=new_message,
+        ):
+            if event.is_final_response():
+                try:
+                    parts_text = "".join(
+                        p.text for p in event.content.parts if getattr(p, "text", None)
+                    )
+                    if parts_text:
+                        response_text = parts_text
+                except (AttributeError, TypeError):
+                    pass
+
+    except Exception as exc:
+        _log_translate_error(url, f"ADK/API error: {exc}")
+        return None
+
+    if response_text is None:
+        _log_translate_error(url, "No final response received from model.")
+        return None
+
+    parsed = _parse_translation(response_text, original_rating)
+    if parsed is None:
+        _log_translate_error(
+            url,
+            f"Failed to parse translation JSON or validate rating. Response: {response_text[:200]}",
+        )
+        return None
+
+    return parsed
diff --git a/tests/test_translator.py b/tests/test_translator.py
new file mode 100644
index 0000000..5006392
--- /dev/null
+++ b/tests/test_translator.py
@@ -0,0 +1,147 @@
+"""
+Unit tests for src/translator.py
+"""
+
+import json
+import pytest
+from unittest.mock import AsyncMock, MagicMock, patch
+
+# Fake English summary input
+ENG_SUMMARY = {
+    "tldr": "This is a prompt agent in a RAG pipeline.",
+    "problem_why": "Why fine-tuning is needed.",
+    "solution_how": "How checkpoint embeddings work.",
+    "insights_tradeoffs": {
+        "pros": ["Good token economy"],
+        "cons": ["High latency"],
+    },
+    "tags_action": ["RAG", "fine-tuning"],
+    "rating": 5,
+}
+
+# Expected Traditional Chinese translated output preserving key English terms
+ZH_TW_SUMMARY = {
+    "tldr": "這是一個在 RAG pipeline 中的 prompt agent。",
+    "problem_why": "為什麼需要 fine-tuning。",
+    "solution_how": "checkpoint embeddings 如何運作。",
+    "insights_tradeoffs": {
+        "pros": ["良好的 token 經濟"],
+        "cons": ["高延遲"],
+    },
+    "tags_action": ["RAG", "fine-tuning"],
+    "rating": 5,  # must match exactly
+}
+
+ZH_TW_JSON_RESPONSE = "```json\n" + json.dumps(ZH_TW_SUMMARY) + "\n```"
+
+def _make_event(text: str, is_final: bool = True):
+    part = MagicMock()
+    part.text = text
+    content = MagicMock()
+    content.parts = [part]
+    event = MagicMock()
+    event.is_final_response.return_value = is_final
+    event.content = content
+    return event
+
+async def _async_gen(*events):
+    for e in events:
+        yield e
+
+@pytest.mark.asyncio
+async def test_translate_summary_happy_path():
+    """Mock ADK runner to return valid Traditional Chinese JSON; verify English terms preserved."""
+    from src.translator import translate_summary
+
+    final_event = _make_event(ZH_TW_JSON_RESPONSE, is_final=True)
+
+    with (
+        patch("src.translator.LlmAgent") as MockAgent,
+        patch("src.translator.Runner") as MockRunner,
+        patch("src.translator.InMemorySessionService") as MockSessionSvc,
+    ):
+        mock_session = MagicMock()
+        mock_session.id = "sess-002"
+        mock_svc_instance = AsyncMock()
+        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
+        MockSessionSvc.return_value = mock_svc_instance
+
+        mock_runner_instance = MagicMock()
+        mock_runner_instance.run_async.return_value = _async_gen(final_event)
+        MockRunner.return_value = mock_runner_instance
+
+        result = await translate_summary(
+            url="https://example.com/article",
+            summary=ENG_SUMMARY,
+        )
+
+    assert result is not None
+    assert result["tldr"] == ZH_TW_SUMMARY["tldr"]
+    assert "prompt" in result["tldr"]
+    assert "agent" in result["tldr"]
+    assert "RAG" in result["tldr"]
+    assert "pipeline" in result["tldr"]
+    assert result["rating"] == 5
+
+@pytest.mark.asyncio
+async def test_translate_summary_altered_rating(capsys):
+    """If the translator alters the rating, it should reject and return None."""
+    from src.translator import translate_summary
+
+    altered = ZH_TW_SUMMARY.copy()
+    altered["rating"] = 4  # original is 5
+    final_event = _make_event(json.dumps(altered), is_final=True)
+
+    with (
+        patch("src.translator.LlmAgent"),
+        patch("src.translator.Runner") as MockRunner,
+        patch("src.translator.InMemorySessionService") as MockSessionSvc,
+    ):
+        mock_session = MagicMock()
+        mock_session.id = "sess-002"
+        mock_svc_instance = AsyncMock()
+        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
+        MockSessionSvc.return_value = mock_svc_instance
+
+        mock_runner_instance = MagicMock()
+        mock_runner_instance.run_async.return_value = _async_gen(final_event)
+        MockRunner.return_value = mock_runner_instance
+
+        result = await translate_summary(
+            url="https://example.com/article",
+            summary=ENG_SUMMARY,
+        )
+
+    assert result is None
+    captured = capsys.readouterr()
+    assert "translate" in captured.err
+
+@pytest.mark.asyncio
+async def test_translate_summary_api_exception(capsys):
+    """If ADK runner raises exception, return None and log error with stage translate."""
+    from src.translator import translate_summary
+
+    with (
+        patch("src.translator.LlmAgent"),
+        patch("src.translator.Runner") as MockRunner,
+        patch("src.translator.InMemorySessionService") as MockSessionSvc,
+    ):
+        mock_session = MagicMock()
+        mock_svc_instance = AsyncMock()
+        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
+        MockSessionSvc.return_value = mock_svc_instance
+
+        mock_runner_instance = MagicMock()
+        mock_runner_instance.run_async.side_effect = RuntimeError("API key invalid")
+        MockRunner.return_value = mock_runner_instance
+
+        result = await translate_summary(
+            url="https://example.com/article",
+            summary=ENG_SUMMARY,
+        )
+
+    assert result is None
+    captured = capsys.readouterr()
+    err_log = json.loads(captured.err.strip())
+    assert err_log["stage"] == "translate"
+    assert "API key invalid" in err_log["error_message"]
```
