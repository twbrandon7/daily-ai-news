import os
import json
import pytest
import yaml
from unittest.mock import AsyncMock, MagicMock, patch
from src.publisher import generate_daily_highlight, translate_highlight, write_daily_posts

# Dummy data
ARTICLES = [
    {
        "url": "https://example.com/art1",
        "title": "New Agent RAG pipeline",
        "author": "Alice",
        "publication_date": "2026-07-12",
        "summary": {
            "tldr": "We built a new RAG pipeline with a custom prompt agent.",
            "problem_why": "Existing pipelines are slow.",
            "solution_how": "Custom embeddings and caching.",
            "insights_tradeoffs": {"pros": ["Fast"], "cons": ["High memory"]},
            "tags_action": ["RAG", "agent"],
            "rating": 5
        },
        "summary_zh_tw": {
            "tldr": "我們用自訂 prompt agent 建立了新的 RAG pipeline。",
            "problem_why": "現有 pipeline 慢。",
            "solution_how": "自訂 embeddings 與快取。",
            "insights_tradeoffs": {"pros": ["快速"], "cons": ["高記憶體"]},
            "tags_action": ["RAG", "agent"],
            "rating": 5
        }
    }
]

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
async def test_generate_daily_highlight_happy(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    final_event = _make_event("This is the daily highlight summarizing RAG pipelines.", is_final=True)

    with (
        patch("src.publisher.LlmAgent") as MockAgent,
        patch("src.publisher.Runner") as MockRunner,
        patch("src.publisher.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-001"
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await generate_daily_highlight(ARTICLES)

    assert result == "This is the daily highlight summarizing RAG pipelines."

@pytest.mark.asyncio
async def test_translate_highlight_happy(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    final_event = _make_event("這是關於 RAG pipeline 的每日亮點摘要。", is_final=True)

    with (
        patch("src.publisher.LlmAgent") as MockAgent,
        patch("src.publisher.Runner") as MockRunner,
        patch("src.publisher.InMemorySessionService") as MockSessionSvc,
    ):
        mock_session = MagicMock()
        mock_session.id = "sess-002"
        mock_svc_instance = AsyncMock()
        mock_svc_instance.create_session = AsyncMock(return_value=mock_session)
        MockSessionSvc.return_value = mock_svc_instance

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async.return_value = _async_gen(final_event)
        MockRunner.return_value = mock_runner_instance

        result = await translate_highlight("This is the daily highlight summarizing RAG pipelines.")

    assert result == "這是關於 RAG pipeline 的每日亮點摘要。"

@pytest.mark.asyncio
async def test_write_daily_posts_empty():
    # Empty articles should immediately return True
    result = await write_daily_posts("2026-07-12", [])
    assert result is True

@pytest.mark.asyncio
async def test_write_daily_posts_happy_path(tmp_path, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    monkeypatch.chdir(tmp_path)

    async def fake_highlight(articles):
        return "Highlight RAG pipeline and token."

    async def fake_translate(highlight):
        return "高亮 RAG pipeline 和 token。"

    monkeypatch.setattr("src.publisher.generate_daily_highlight", fake_highlight)
    monkeypatch.setattr("src.publisher.translate_highlight", fake_translate)

    success = await write_daily_posts("2026-07-12", ARTICLES)
    assert success is True

    en_file = tmp_path / "content/en/posts/2026-07-12.md"
    zh_file = tmp_path / "content/zh-tw/posts/2026-07-12.md"

    assert en_file.exists()
    assert zh_file.exists()

    # Verify English post content structure
    en_content = en_file.read_text(encoding="utf-8")
    assert en_content.startswith("---\n")
    assert en_content.endswith("---\n")
    en_data = yaml.safe_load(en_content.strip().strip("-").strip())
    assert en_data["title"] == "2026-07-12"
    assert en_data["date"] == "2026-07-12"
    assert en_data["daily_highlight"] == "Highlight RAG pipeline and token."
    assert len(en_data["articles"]) == 1
    assert en_data["articles"][0]["title"] == "New Agent RAG pipeline"
    assert en_data["articles"][0]["tldr"] == "We built a new RAG pipeline with a custom prompt agent."

    # Verify Chinese post content structure
    zh_content = zh_file.read_text(encoding="utf-8")
    assert zh_content.startswith("---\n")
    assert zh_content.endswith("---\n")
    zh_data = yaml.safe_load(zh_content.strip().strip("-").strip())
    assert zh_data["title"] == "2026-07-12"
    assert zh_data["date"] == "2026-07-12"
    assert zh_data["daily_highlight"] == "高亮 RAG pipeline 和 token。"
    assert len(zh_data["articles"]) == 1
    assert zh_data["articles"][0]["title"] == "New Agent RAG pipeline"
    assert zh_data["articles"][0]["tldr"] == "我們用自訂 prompt agent 建立了新的 RAG pipeline。"

@pytest.mark.asyncio
async def test_write_daily_posts_missing_key(monkeypatch, capsys):
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
        await write_daily_posts("2026-07-12", ARTICLES)

    captured = capsys.readouterr()
    assert "publish" in captured.err

@pytest.mark.asyncio
async def test_write_daily_posts_validation_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    monkeypatch.chdir(tmp_path)

    async def fake_highlight(articles):
        return "Highlight RAG pipeline."

    async def fake_translate(highlight):
        # Missing RAG and pipeline
        return "高亮其它東西。"

    monkeypatch.setattr("src.publisher.generate_daily_highlight", fake_highlight)
    monkeypatch.setattr("src.publisher.translate_highlight", fake_translate)

    with pytest.raises(ValueError, match="Term 'RAG' missing"):
        await write_daily_posts("2026-07-12", ARTICLES)

    # Ensure no partial files created
    en_file = tmp_path / "content/en/posts/2026-07-12.md"
    assert not en_file.exists()

    captured = capsys.readouterr()
    assert "publish" in captured.err

@pytest.mark.asyncio
async def test_write_daily_posts_disk_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    monkeypatch.chdir(tmp_path)

    async def fake_highlight(articles):
        return "Highlight."

    async def fake_translate(highlight):
        return "高亮。"

    monkeypatch.setattr("src.publisher.generate_daily_highlight", fake_highlight)
    monkeypatch.setattr("src.publisher.translate_highlight", fake_translate)

    # Force error by mocking open on file write
    import builtins
    original_open = builtins.open
    def mock_open(file, mode='r', *args, **kwargs):
        if "content/en/posts" in str(file) and 'w' in mode:
            raise PermissionError("Disk Write Protected")
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", mock_open)

    with pytest.raises(PermissionError):
        await write_daily_posts("2026-07-12", ARTICLES)

    # Verify error is logged and stage is publish
    captured = capsys.readouterr()
    err_log = json.loads(captured.err.strip())
    assert err_log["stage"] == "publish"
    assert "Disk Write Protected" in err_log["error_message"]
