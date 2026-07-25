"""
Unit tests for src/translator.py
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Fake English summary input
ENG_SUMMARY = {
    "tldr": "This is a prompt agent in a RAG pipeline.",
    "problem_why": "Why fine-tuning is needed.",
    "solution_how": "How checkpoint embeddings work.",
    "insights_tradeoffs": {
        "pros": ["Good token economy"],
        "cons": ["High latency"],
    },
    "tags_action": ["RAG", "fine-tuning"],
    "rating": 5,
}

# Expected Traditional Chinese translated output preserving key English terms
ZH_TW_SUMMARY = {
    "tldr": "這是一個在 RAG pipeline 中的 prompt agent。",
    "problem_why": "為什麼需要 fine-tuning。",
    "solution_how": "checkpoint embeddings 如何運作。",
    "insights_tradeoffs": {
        "pros": ["良好的 token 經濟"],
        "cons": ["高延遲"],
    },
    "tags_action": ["RAG", "fine-tuning"],
    "rating": 5,  # must match exactly
}

ZH_TW_JSON_RESPONSE = "```json\n" + json.dumps(ZH_TW_SUMMARY) + "\n```"

def _make_event(text: str, is_final: bool = True):
    part = MagicMock()
    part.text = text
    content = MagicMock()
    content.parts = [part]
    event = MagicMock()
    event.is_final_response.return_value = is_final
    event.content = content
    return event

async def _async_gen(*events):
    for e in events:
        yield e

@pytest.mark.asyncio
async def test_translate_summary_happy_path():
    """Mock ADK runner to return valid Traditional Chinese JSON; verify English terms preserved."""
    from src.translator import translate_summary

    final_event = _make_event(ZH_TW_JSON_RESPONSE, is_final=True)

    with (
        patch("src.translator.LlmAgent") as MockAgent,
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-002"
        mock_session.state = {"translation": ZH_TW_SUMMARY}
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        mock_svc_instance.get_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    assert result is not None
    assert result["tldr"] == ZH_TW_SUMMARY["tldr"]
    assert "prompt" in result["tldr"]
    assert "agent" in result["tldr"]
    assert "RAG" in result["tldr"]
    assert "pipeline" in result["tldr"]
    assert result["rating"] == 5

@pytest.mark.asyncio
async def test_translate_summary_altered_rating(capsys):
    """If the translator alters the rating, it should reject and return None."""
    from src.translator import translate_summary

    altered = ZH_TW_SUMMARY.copy()
    altered["rating"] = 4  # original is 5
    final_event = _make_event(json.dumps(altered), is_final=True)

    with (
        patch("src.translator.LlmAgent"),
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-002"
        mock_session.state = {"translation": altered}
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        mock_svc_instance.get_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    assert result is None
    captured = capsys.readouterr()
    assert "translate" in captured.err

@pytest.mark.asyncio
async def test_translate_summary_api_exception(capsys):
    """If ADK runner raises exception, return None and log error with stage translate."""
    from src.translator import translate_summary

    with (
        patch("src.translator.LlmAgent"),
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.state = {}
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        mock_svc_instance.get_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.side_effect = RuntimeError("API key invalid")
        MockRunner.return_value = mock_runner_instance

        result = await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    assert result is None
    captured = capsys.readouterr()
    err_log = json.loads(captured.err.strip())
    assert err_log["stage"] == "translate"
    assert "API key invalid" in err_log["error_message"]


@pytest.mark.asyncio
async def test_translate_summary_extra_keys_rejected(capsys):
    """If translation JSON contains extra root keys, it should be rejected."""
    from src.translator import translate_summary

    bad_summary = ZH_TW_SUMMARY.copy()
    bad_summary["extra_field"] = "some value"
    final_event = _make_event(json.dumps(bad_summary), is_final=True)

    with (
        patch("src.translator.LlmAgent"),
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-002"
        mock_session.state = {}
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        mock_svc_instance.get_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.side_effect = ValueError("Schema mismatch. Extra keys: {'extra_field'}")
        MockRunner.return_value = mock_runner_instance

        result = await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    assert result is None
    captured = capsys.readouterr()
    assert "Schema mismatch" in captured.err or "Extra keys" in captured.err


@pytest.mark.asyncio
async def test_translate_summary_missing_terms_rejected(capsys):
    """If translation fails to preserve required English terms, it should be rejected."""
    from src.translator import translate_summary

    bad_summary = ZH_TW_SUMMARY.copy()
    # "prompt" and "agent" in original tldr are missing here
    bad_summary["tldr"] = "這是一個在 RAG pipeline 中的東西。"
    final_event = _make_event(json.dumps(bad_summary), is_final=True)

    with (
        patch("src.translator.LlmAgent"),
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-002"
        mock_session.state = {"translation": bad_summary}
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        mock_svc_instance.get_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    assert result is None
    captured = capsys.readouterr()
    assert "Term 'prompt' missing" in captured.err or "Term 'agent' missing" in captured.err


@pytest.mark.asyncio
async def test_translate_summary_multiple_code_blocks():
    """If LLM outputs conversational text first and then JSON, it should parse correctly."""
    from src.translator import translate_summary

    mixed_response = (
        "Here is the translation:\n"
        "```markdown\nSome note about translation\n```\n"
        "And the JSON:\n"
        "```json\n" + json.dumps(ZH_TW_SUMMARY) + "\n```"
    )
    final_event = _make_event(mixed_response, is_final=True)

    with (
        patch("src.translator.LlmAgent"),
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-002"
        mock_session.state = {"translation": ZH_TW_SUMMARY}
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        mock_svc_instance.get_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    assert result is not None
    assert result["tldr"] == ZH_TW_SUMMARY["tldr"]


@pytest.mark.asyncio
async def test_translate_summary_log_timestamp_format(capsys):
    """Log error timestamps must use YYYY-MM-DDTHH:MM:SSZ format (ending with Z)."""
    from src.translator import translate_summary

    with (
        patch("src.translator.LlmAgent"),
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.state = {}
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        mock_svc_instance.get_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.side_effect = RuntimeError("API error")
        MockRunner.return_value = mock_runner_instance

        await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    captured = capsys.readouterr()
    err_log = json.loads(captured.err.strip())
    timestamp = err_log["timestamp"]
    # Check it matches YYYY-MM-DDTHH:MM:SSZ format
    import re
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", timestamp) is not None


def test_parse_translation_substring_terms_not_matched():
    """Words like 'coverage' containing 'rag' as a substring should NOT falsely trigger term checks."""
    from src.translator import _validate_translation_constraints

    original = {
        "tldr": "Broad coverage of model distillation.",
        "problem_why": "Geopolitical coverage around model distillation.",
        "solution_how": "Unified architecture.",
        "insights_tradeoffs": {"pros": ["Good"], "cons": ["None"]},
        "tags_action": ["news"],
        "rating": 5,
    }
    translated = {
        "tldr": "廣泛涵蓋模型蒸餾。",
        "problem_why": "圍繞模型蒸餾的地緣政治局勢。",
        "solution_how": "統一架構。",
        "insights_tradeoffs": {"pros": ["好"], "cons": ["無"]},
        "tags_action": ["新聞"],
        "rating": 5,
    }

    # Should validate successfully without raising ValueError for missing 'RAG'
    _validate_translation_constraints(translated, original)


@pytest.mark.asyncio
async def test_translate_summary_refinement_step():
    """Verify refinement sub-step executes with REFINE_PROMPT and returns polished summary."""
    from src.translator import translate_summary, REFINE_PROMPT, TRANSLATE_PROMPT

    refined_summary = {
        "tldr": "這是一套統一架構。關注「模型蒸餾 (Model Distillation)」與 prompt agent 在 RAG pipeline 的應用。",
        "problem_why": "說明為什麼需要 fine-tuning。",
        "solution_how": "說明 checkpoint embeddings 如何運作。",
        "insights_tradeoffs": {
            "pros": ["良好的 token 經濟"],
            "cons": ["高延遲"],
        },
        "tags_action": ["RAG", "fine-tuning"],
        "rating": 5,
    }

    final_event = _make_event(json.dumps(refined_summary), is_final=True)

    with (
        patch("src.translator.LlmAgent") as MockAgent,
        patch("src.translator.Runner") as MockRunner,
        patch("src.translator.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session_1 = MagicMock()
        mock_session_1.id = "sess-trans"
        mock_session_1.state = {"translation": ZH_TW_SUMMARY}

        mock_session_2 = MagicMock()
        mock_session_2.id = "sess-refine"
        mock_session_2.state = {"refinement": refined_summary}

        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(side_effect=[mock_session_1, mock_session_2])
        mock_svc_instance.get_session = AsyncMock(side_effect=[mock_session_1, mock_session_2])
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await translate_summary(
            url="https://example.com/article",
            summary=ENG_SUMMARY,
        )

    assert result is not None
    assert result["tldr"] == refined_summary["tldr"]
    assert "模型蒸餾 (Model Distillation)" in result["tldr"]
    assert MockAgent.call_count == 2
    # Verify first call instructions contain translation prompt and second call contains refine prompt
    assert MockAgent.call_args_list[0].kwargs["instruction"] == TRANSLATE_PROMPT
    assert MockAgent.call_args_list[1].kwargs["instruction"] == REFINE_PROMPT



