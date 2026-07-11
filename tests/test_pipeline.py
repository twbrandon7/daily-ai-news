import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from src.pipeline import extract_article_info, log_error, crawl_blog

class MockMarkdown:
    def __init__(self, text=""):
        self.fit_markdown = text
        self.raw_markdown = text
        self.markdown = text
    def __str__(self):
        return self.markdown

class MockCrawlResult:
    def __init__(self, success=True, url="https://example.com", html="<html></html>", markdown="", metadata=None, error_message=None):
        self.success = success
        self.url = url
        self.html = html
        self.markdown = MockMarkdown(markdown) if isinstance(markdown, str) else markdown
        self.metadata = metadata or {}
        self.error_message = error_message

def test_extract_article_info_basic():
    # Test extract with basic metadata
    mock_result = MockCrawlResult(
        success=True,
        markdown="This is the article body",
        metadata={
            "title": "Test Title",
            "author": "John Doe",
            "article:published_time": "2026-07-11T12:00:00Z"
        }
    )
    info = extract_article_info("https://example.com", mock_result)
    assert info["title"] == "Test Title"
    assert info["author"] == "John Doe"
    assert info["publication_date"] == "2026-07-11"
    assert info["body"] == "This is the article body"
    assert info["url"] == "https://example.com"

def test_extract_article_info_fallback():
    # Test extract with minimal metadata but HTML tags
    html_content = """
    <html>
      <head>
        <meta name="author" content="Alice Smith">
      </head>
      <body>
        <h1>Headline Title</h1>
        <time datetime="2026-05-20T10:00:00">May 20</time>
      </body>
    </html>
    """
    mock_result = MockCrawlResult(
        success=True,
        html=html_content,
        markdown="Article main content",
        metadata={}
    )
    info = extract_article_info("https://example.com", mock_result)
    assert info["title"] == "Headline Title"
    assert info["author"] == "Alice Smith"
    assert info["publication_date"] == "2026-05-20"
    assert info["body"] == "Article main content"

def test_log_error(capsys):
    log_error("https://fail.com", "Connection timeout")
    captured = capsys.readouterr()
    json_line = None
    for line in captured.out.strip().split("\n"):
        if line.strip().startswith("{"):
            json_line = line.strip()
            break
    assert json_line is not None
    log_line = json.loads(json_line)
    assert log_line["stage"] == "crawl"
    assert log_line["blog_url"] == "https://fail.com"
    assert log_line["error_message"] == "Connection timeout"
    assert "timestamp" in log_line

@pytest.mark.asyncio
async def test_crawl_blog_success():
    mock_crawler = AsyncMock()
    mock_result = MockCrawlResult(
        success=True,
        markdown="Hello news",
        metadata={"title": "Latest News", "author": "Staff"}
    )
    mock_crawler.arun.return_value = mock_result
    
    url, parsed_data, error_msg = await crawl_blog(mock_crawler, "https://success.com", None)
    
    assert url == "https://success.com"
    assert error_msg is None
    assert parsed_data["title"] == "Latest News"
    assert parsed_data["author"] == "Staff"
    assert parsed_data["body"] == "Hello news"

@pytest.mark.asyncio
async def test_crawl_blog_failure(capsys):
    mock_crawler = AsyncMock()
    mock_result = MockCrawlResult(
        success=False,
        error_message="HTTP 500 Internal Server Error"
    )
    mock_crawler.arun.return_value = mock_result
    
    url, parsed_data, error_msg = await crawl_blog(mock_crawler, "https://fail.com", None)
    
    assert url == "https://fail.com"
    assert parsed_data is None
    assert error_msg == "HTTP 500 Internal Server Error"
    
    # Check that error was logged
    captured = capsys.readouterr()
    json_line = None
    for line in captured.out.strip().split("\n"):
        if line.strip().startswith("{"):
            json_line = line.strip()
            break
    assert json_line is not None
    log_line = json.loads(json_line)
    assert log_line["blog_url"] == "https://fail.com"
    assert log_line["error_message"] == "HTTP 500 Internal Server Error"
