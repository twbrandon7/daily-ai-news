"""
Unit tests for src/summarizer.py
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_SUMMARY_DICT = {
    "tldr": "This is a brief summary.",
    "problem_why": "Explains the core problem.",
    "solution_how": "Describes the solution approach.",
    "insights_tradeoffs": {
        "pros": ["Fast execution", "Easy integration"],
        "cons": ["Limited scalability"],
    },
    "tags_action": ["AI", "Python", "Performance"],
    "rating": 4,
}

VALID_JSON_RESPONSE = "```json\n" + json.dumps(VALID_SUMMARY_DICT) + "\n```"


def _make_event(text: str, is_final: bool = True):
    """Build a minimal fake ADK event."""
    part = MagicMock()
    part.text = text

    content = MagicMock()
    content.parts = [part]

    event = MagicMock()
    event.is_final_response.return_value = is_final
    event.content = content
    return event


async def _async_gen(*events):
    """Yield events as an async generator (simulates runner.run_async)."""
    for e in events:
        yield e


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_summarize_article_happy_path():
    """Mock the ADK runner to return a valid JSON response; verify all fields."""
    from src.summarizer import summarize_article

    final_event = _make_event(VALID_JSON_RESPONSE, is_final=True)

    with (
        patch("src.summarizer.LlmAgent") as MockAgent,
        patch("src.summarizer.Runner") as MockRunner,
        patch("src.summarizer.InMemorySessionService") as MockSessionSvc,
    ):
        # Set up session service mock
        mock_session = MagicMock()
        mock_session.id = "sess-001"
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        # Set up runner mock
        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await summarize_article(
            url="https://example.com/article",
            body="Detailed article body text about AI systems.",
            title="AI Systems Overview",
        )

    assert result is not None, "Expected a dict result, got None"

    # Verify all required fields with correct types
    assert isinstance(result["tldr"], str) and result["tldr"]
    assert isinstance(result["problem_why"], str) and result["problem_why"]
    assert isinstance(result["solution_how"], str) and result["solution_how"]

    it = result["insights_tradeoffs"]
    assert isinstance(it, dict)
    assert isinstance(it["pros"], list)
    assert isinstance(it["cons"], list)

    assert isinstance(result["tags_action"], list) and len(result["tags_action"]) > 0

    assert isinstance(result["rating"], int)
    assert 1 <= result["rating"] <= 5

    # Verify values match expected
    assert result["tldr"] == VALID_SUMMARY_DICT["tldr"]
    assert result["rating"] == 4


@pytest.mark.asyncio
async def test_summarize_article_empty_body(capsys):
    """Empty body should return None immediately and log an error."""
    from src.summarizer import summarize_article

    result = await summarize_article(
        url="https://example.com/empty",
        body="",
        title="Some Title",
    )

    assert result is None

    captured = capsys.readouterr()
    err_line = captured.err.strip()
    assert err_line, "Expected a structured JSON error on stderr"
    error_log = json.loads(err_line)
    assert error_log["stage"] == "summarize"
    assert error_log["blog_url"] == "https://example.com/empty"
    assert "timestamp" in error_log


@pytest.mark.asyncio
async def test_summarize_article_api_exception(capsys):
    """If the ADK runner raises an exception, return None and log the error."""
    from src.summarizer import summarize_article

    with (
        patch("src.summarizer.LlmAgent"),
        patch("src.summarizer.Runner") as MockRunner,
        patch("src.summarizer.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-err"
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        # Runner constructor or run_async raises an exception
        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.side_effect = RuntimeError("Network timeout")
        MockRunner.return_value = mock_runner_instance

        result = await summarize_article(
            url="https://example.com/broken",
            body="Some article content here.",
            title="Broken Article",
        )

    assert result is None

    captured = capsys.readouterr()
    err_line = captured.err.strip()
    assert err_line, "Expected a structured JSON error on stderr"
    error_log = json.loads(err_line)
    assert error_log["stage"] == "summarize"
    assert error_log["blog_url"] == "https://example.com/broken"
    assert "Network timeout" in error_log["error_message"]
    assert "timestamp" in error_log


@pytest.mark.asyncio
async def test_summarize_article_malformed_response(capsys):
    """If the model returns non-JSON text, return None and log the error."""
    from src.summarizer import summarize_article

    garbage_event = _make_event("This is not JSON at all, sorry!", is_final=True)

    with (
        patch("src.summarizer.LlmAgent"),
        patch("src.summarizer.Runner") as MockRunner,
        patch("src.summarizer.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-bad"
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(garbage_event)
        MockRunner.return_value = mock_runner_instance

        result = await summarize_article(
            url="https://example.com/malformed",
            body="Valid article body with plenty of content.",
            title="Malformed Response Article",
        )

    assert result is None

    captured = capsys.readouterr()
    err_line = captured.err.strip()
    assert err_line, "Expected a structured JSON error on stderr"
    error_log = json.loads(err_line)
    assert error_log["stage"] == "summarize"
    assert error_log["blog_url"] == "https://example.com/malformed"
    assert "timestamp" in error_log
