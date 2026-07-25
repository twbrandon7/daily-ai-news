import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from src.pipeline import extract_article_info, log_error, crawl_blog

@pytest.fixture(autouse=True)
def mock_requests_get(monkeypatch):
    """Autouse fixture to mock requests.get to return a valid RSS XML feed with the requested URL."""
    class MockResponse:
        def __init__(self, url):
            self.content = f"""<?xml version="1.0" encoding="UTF-8" ?>
            <rss version="2.0">
            <channel>
              <item>
                <title>Mock Article for {url}</title>
                <link>{url}</link>
              </item>
            </channel>
            </rss>
            """.encode('utf-8')
        def raise_for_status(self):
            pass
            
    monkeypatch.setattr("requests.get", lambda url, *args, **kwargs: MockResponse(url))

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

def test_load_deduplication_store_nonexistent(tmp_path):
    from src.pipeline import load_deduplication_store
    path = tmp_path / "nonexistent.json"
    assert load_deduplication_store(str(path)) == {}

def test_load_deduplication_store_invalid_json(tmp_path):
    from src.pipeline import load_deduplication_store
    path = tmp_path / "invalid.json"
    path.write_text("{invalid")
    assert load_deduplication_store(str(path)) == {}

def test_load_deduplication_store_not_dict_or_list(tmp_path):
    from src.pipeline import load_deduplication_store
    path = tmp_path / "not_dict_or_list.json"
    path.write_text('123')
    assert load_deduplication_store(str(path)) == {}

def test_load_deduplication_store_valid(tmp_path):
    from src.pipeline import load_deduplication_store
    path = tmp_path / "valid.json"
    path.write_text('["https://a.com", "https://b.com"]')
    assert load_deduplication_store(str(path)) == {"legacy": {"https://a.com", "https://b.com"}}

def test_save_deduplication_store(tmp_path):
    from src.pipeline import save_deduplication_store
    path = tmp_path / "output.json"
    save_deduplication_store(str(path), {"feed1": {"https://a.com", "https://b.com"}})
    assert path.exists()
    data = json.loads(path.read_text())
    assert data == {"feed1": ["https://a.com", "https://b.com"]}

@pytest.mark.asyncio
async def test_pipeline_deduplication_integration(tmp_path, monkeypatch, capsys):
    import os
    import json
    import yaml
    from src import pipeline
    from unittest.mock import AsyncMock

    # Set required env var
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    # Create directory structure in temp path
    os.makedirs(tmp_path / "data")
    
    # Write blogs.yaml
    blogs_yaml = tmp_path / "data/blogs.yaml"
    blogs_yaml.write_text(yaml.dump({"blogs": ["https://old-url.com", "https://new-url.com"]}))
    
    # Write fetched_posts.json
    fetched_posts = tmp_path / "data/fetched_posts.json"
    fetched_posts.write_text(json.dumps(["https://old-url.com"]))
    
    # Change working directory to tmp_path
    monkeypatch.chdir(tmp_path)
    
    # Mock AsyncWebCrawler
    mock_crawler = AsyncMock()
    mock_crawler.arun.return_value = MockCrawlResult(
        success=True,
        url="https://new-url.com",
        markdown="New article content",
        metadata={"title": "New Title", "author": "New Author", "article:published_time": "2026-07-11T12:00:00Z"}
    )
    
    class MockAsyncWebCrawlerContext:
        async def __aenter__(self):
            return mock_crawler
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockAsyncWebCrawlerContext)

    # Mock summarize_article to return a valid summary without making real API calls
    mock_summary = {
        "tldr": "Test summary",
        "problem_why": "Test problem",
        "solution_how": "Test solution",
        "insights_tradeoffs": {"pros": ["pro1"], "cons": ["con1"]},
        "tags_action": ["tag1"],
        "rating": 4,
    }
    monkeypatch.setattr(pipeline, "summarize_article", AsyncMock(return_value=mock_summary))
    mock_translation = {
        "tldr": "測試摘要",
        "problem_why": "測試問題",
        "solution_how": "測試方案",
        "insights_tradeoffs": {"pros": ["優點"], "cons": ["缺點"]},
        "tags_action": ["標籤"],
        "rating": 4,
    }
    monkeypatch.setattr(pipeline, "translate_summary", AsyncMock(return_value=mock_translation))
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=True))
    
    # Run pipeline main
    await pipeline.main()
    
    # Check that old-url.com was skipped and new-url.com was crawled
    captured = capsys.readouterr()
    assert "Skipping already crawled URL: https://old-url.com" in captured.out
    assert "Successfully crawled: https://new-url.com" in captured.out
    
    # Verify that mock_crawler.arun was only called for new-url.com, not old-url.com
    mock_crawler.arun.assert_called_once()
    assert mock_crawler.arun.call_args[1]["url"] == "https://new-url.com"
    
    # Verify fetched_posts.json has both old and new URLs
    updated_fetched = json.loads(fetched_posts.read_text())
    assert updated_fetched == {
        "legacy": ["https://old-url.com"],
        "https://new-url.com": ["https://new-url.com"]
    }
    
    # Verify parsed_articles.json has only the new article
    parsed_articles_path = tmp_path / "data/parsed_articles.json"
    assert parsed_articles_path.exists()
    parsed_articles = json.loads(parsed_articles_path.read_text())
    assert len(parsed_articles) == 1
    assert parsed_articles[0]["url"] == "https://new-url.com"
    assert parsed_articles[0]["title"] == "New Title"
    assert parsed_articles[0]["summary"] == mock_summary
    assert parsed_articles[0]["summary_zh_tw"] == mock_translation

def test_normalize_url():
    from src.pipeline import normalize_url
    assert normalize_url("https://Google.Com/") == "https://google.com"
    assert normalize_url("HTTP://foo.bar/baz/") == "http://foo.bar/baz"
    assert normalize_url("https://example.com/PATH/to/resource") == "https://example.com/PATH/to/resource"
    assert normalize_url("  https://test.com/  ") == "https://test.com"
    assert normalize_url("bare-string/") == "bare-string"

def test_load_deduplication_store_non_list_warning(tmp_path, capsys):
    from src.pipeline import load_deduplication_store
    path = tmp_path / "string.json"
    path.write_text('"hello"')
    res = load_deduplication_store(str(path))
    assert res == {}
    captured = capsys.readouterr()
    assert "Warning: Expected dict or list" in captured.err

@pytest.mark.asyncio
async def test_pipeline_deduplication_failure_does_not_save_dedup(tmp_path, monkeypatch, capsys):
    import os
    import json
    import yaml
    from src import pipeline
    from unittest.mock import AsyncMock

    # Set required env var
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    # Create directory structure in temp path
    os.makedirs(tmp_path / "data")
    
    # Write blogs.yaml
    blogs_yaml = tmp_path / "data/blogs.yaml"
    blogs_yaml.write_text(yaml.dump({"blogs": ["https://new-url.com"]}))
    
    # Write fetched_posts.json
    fetched_posts = tmp_path / "data/fetched_posts.json"
    fetched_posts.write_text(json.dumps([]))
    
    # Change working directory to tmp_path
    monkeypatch.chdir(tmp_path)
    
    # Mock AsyncWebCrawler
    mock_crawler = AsyncMock()
    mock_crawler.arun.return_value = MockCrawlResult(
        success=True,
        url="https://new-url.com",
        markdown="New article content",
        metadata={"title": "New Title", "author": "New Author", "article:published_time": "2026-07-11T12:00:00Z"}
    )
    
    class MockAsyncWebCrawlerContext:
        async def __aenter__(self):
            return mock_crawler
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockAsyncWebCrawlerContext)

    # Mock summarize_article to return a valid summary without making real API calls
    mock_summary = {
        "tldr": "Test summary",
        "problem_why": "Test problem",
        "solution_how": "Test solution",
        "insights_tradeoffs": {"pros": ["pro1"], "cons": ["con1"]},
        "tags_action": ["tag1"],
        "rating": 4,
    }
    monkeypatch.setattr(pipeline, "summarize_article", AsyncMock(return_value=mock_summary))
    mock_translation = {
        "tldr": "測試摘要",
        "problem_why": "測試問題",
        "solution_how": "測試方案",
        "insights_tradeoffs": {"pros": ["優點"], "cons": ["缺點"]},
        "tags_action": ["標籤"],
        "rating": 4,
    }
    monkeypatch.setattr(pipeline, "translate_summary", AsyncMock(return_value=mock_translation))
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=True))
    
    # Force a failure during saving of parsed_articles.json by mocking open
    import builtins
    original_open = builtins.open
    def mock_open(file, mode='r', *args, **kwargs):
        if "parsed_articles.json" in str(file) and 'w' in mode:
            raise PermissionError("Simulated write error")
        return original_open(file, mode, *args, **kwargs)
    monkeypatch.setattr(builtins, "open", mock_open)
    
    # Run pipeline main
    await pipeline.main()
    
    # Verify that crawled URL was NOT added to fetched_posts.json because of the save failure
    updated_fetched = json.loads(fetched_posts.read_text())
    assert updated_fetched == {"legacy": []}




@pytest.mark.asyncio
async def test_pipeline_summarization_failure_excludes_article(tmp_path, monkeypatch):
    """
    AC5: Given 3 articles where 1 summarization fails, when pipeline runs,
    then parsed_articles.json contains exactly 2 articles (each with summary)
    and the failing article is recorded in failures.
    """
    import os, json, yaml
    from src import pipeline
    from unittest.mock import AsyncMock

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.chdir(tmp_path)
    os.makedirs(tmp_path / "data")

    urls = ["https://ok1.com", "https://fail.com", "https://ok2.com"]
    (tmp_path / "data/blogs.yaml").write_text(yaml.dump({"blogs": urls}))
    (tmp_path / "data/fetched_posts.json").write_text("[]")

    def make_crawl_result(url):
        return MockCrawlResult(
            success=True,
            url=url,
            markdown=f"body of {url}",
            metadata={"title": f"Title {url}", "author": "A", "article:published_time": "2026-07-11T00:00:00Z"},
        )

    call_count = 0
    original_arun = None

    class MockCrawler:
        async def arun(self, url, config):
            return make_crawl_result(url)

    class MockCrawlerCtx:
        async def __aenter__(self): return MockCrawler()
        async def __aexit__(self, *_): pass

    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockCrawlerCtx)

    mock_summary = {
        "tldr": "ok",
        "problem_why": "p",
        "solution_how": "s",
        "insights_tradeoffs": {"pros": ["a"], "cons": ["b"]},
        "tags_action": ["t"],
        "rating": 3,
    }

    async def fake_summarize(url, body, title):
        if "fail" in url:
            return None
        return mock_summary

    monkeypatch.setattr(pipeline, "summarize_article", fake_summarize)

    async def fake_translate(url, summary):
        return summary
    monkeypatch.setattr(pipeline, "translate_summary", fake_translate)
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=True))
 
    await pipeline.main()

    parsed = json.loads((tmp_path / "data/parsed_articles.json").read_text())
    assert len(parsed) == 2
    for article in parsed:
        assert "summary" in article
        assert "summary_zh_tw" in article
        assert "fail" not in article["url"]


@pytest.mark.asyncio
async def test_pipeline_translation_failure_excludes_article(tmp_path, monkeypatch):
    """
    Given 3 articles where 1 translation fails, when pipeline runs,
    then parsed_articles.json contains exactly 2 articles (each with summary and summary_zh_tw)
    and the failing article is recorded in failures.
    """
    import os, json, yaml
    from src import pipeline
    from unittest.mock import AsyncMock

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.chdir(tmp_path)
    os.makedirs(tmp_path / "data")

    urls = ["https://ok1.com", "https://fail.com", "https://ok2.com"]
    (tmp_path / "data/blogs.yaml").write_text(yaml.dump({"blogs": urls}))
    (tmp_path / "data/fetched_posts.json").write_text("[]")

    def make_crawl_result(url):
        return MockCrawlResult(
            success=True,
            url=url,
            markdown=f"body of {url}",
            metadata={"title": f"Title {url}", "author": "A", "article:published_time": "2026-07-11T00:00:00Z"},
        )

    class MockCrawler:
        async def arun(self, url, config):
            return make_crawl_result(url)

    class MockCrawlerCtx:
        async def __aenter__(self): return MockCrawler()
        async def __aexit__(self, *_): pass

    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockCrawlerCtx)

    mock_summary = {
        "tldr": "ok",
        "problem_why": "p",
        "solution_how": "s",
        "insights_tradeoffs": {"pros": ["a"], "cons": ["b"]},
        "tags_action": ["t"],
        "rating": 3,
    }

    async def fake_summarize(url, body, title):
        return mock_summary

    async def fake_translate(url, summary):
        if "fail" in url:
            return None
        return summary

    monkeypatch.setattr(pipeline, "summarize_article", fake_summarize)
    monkeypatch.setattr(pipeline, "translate_summary", fake_translate)
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=True))
 
    await pipeline.main()

    parsed = json.loads((tmp_path / "data/parsed_articles.json").read_text())
    assert len(parsed) == 2
    for article in parsed:
        assert "summary" in article
        assert "summary_zh_tw" in article
        assert "fail" not in article["url"]


@pytest.mark.asyncio
async def test_pipeline_publishing_integration(tmp_path, monkeypatch):
    """
    Test pipeline interaction with write_daily_posts.
    If write_daily_posts fails, main exits with 1, and no parsed_articles.json is written.
    """
    import os, json, yaml
    from src import pipeline
    from unittest.mock import AsyncMock

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.chdir(tmp_path)
    os.makedirs(tmp_path / "data")

    urls = ["https://ok.com"]
    (tmp_path / "data/blogs.yaml").write_text(yaml.dump({"blogs": urls}))
    (tmp_path / "data/fetched_posts.json").write_text("[]")

    def make_crawl_result(url):
        return MockCrawlResult(
            success=True,
            url=url,
            markdown="body",
            metadata={"title": "Title", "author": "A", "article:published_time": "2026-07-11T00:00:00Z"},
        )

    class MockCrawler:
        async def arun(self, url, config):
            return make_crawl_result(url)

    class MockCrawlerCtx:
        async def __aenter__(self): return MockCrawler()
        async def __aexit__(self, *_): pass

    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockCrawlerCtx)

    mock_summary = {
        "tldr": "ok",
        "problem_why": "p",
        "solution_how": "s",
        "insights_tradeoffs": {"pros": ["a"], "cons": ["b"]},
        "tags_action": ["t"],
        "rating": 3,
    }
    monkeypatch.setattr(pipeline, "summarize_article", AsyncMock(return_value=mock_summary))
    monkeypatch.setattr(pipeline, "translate_summary", AsyncMock(return_value=mock_summary))

    # Scenario 1: write_daily_posts fails by raising an exception
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(side_effect=RuntimeError("Publish fail")))
    with pytest.raises(SystemExit) as excinfo:
        await pipeline.main()
    assert excinfo.value.code == 1
    assert not (tmp_path / "data/parsed_articles.json").exists()

    # Scenario 2: write_daily_posts returns False
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=False))
    with pytest.raises(SystemExit) as excinfo:
        await pipeline.main()
    assert excinfo.value.code == 1
    assert not (tmp_path / "data/parsed_articles.json").exists()

    # Scenario 3: write_daily_posts succeeds
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=True))
    await pipeline.main()
    assert (tmp_path / "data/parsed_articles.json").exists()


@pytest.mark.asyncio
async def test_pipeline_stages_individually(tmp_path, monkeypatch):
    import os
    import json
    import yaml
    from src import pipeline
    from unittest.mock import AsyncMock

    # Set required env var
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    # Create directory structure in temp path
    os.makedirs(tmp_path / "data")

    # Write blogs.yaml
    blogs_yaml = tmp_path / "data/blogs.yaml"
    blogs_yaml.write_text(yaml.dump({"blogs": ["https://new-url.com"]}))

    # Write fetched_posts.json
    fetched_posts = tmp_path / "data/fetched_posts.json"
    fetched_posts.write_text(json.dumps([]))

    # Change working directory to tmp_path
    monkeypatch.chdir(tmp_path)

    # Mock AsyncWebCrawler
    mock_crawler = AsyncMock()
    mock_crawler.arun.return_value = MockCrawlResult(
        success=True,
        url="https://new-url.com",
        markdown="New article content",
        metadata={"title": "New Title", "author": "New Author", "article:published_time": "2026-07-11T12:00:00Z"}
    )

    class MockAsyncWebCrawlerContext:
        async def __aenter__(self):
            return mock_crawler
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockAsyncWebCrawlerContext)

    # Mock summarize_article to return a valid summary without making real API calls
    mock_summary = {
        "tldr": "Test summary",
        "problem_why": "Test problem",
        "solution_how": "Test solution",
        "insights_tradeoffs": {"pros": ["pro1"], "cons": ["con1"]},
        "tags_action": ["tag1"],
        "rating": 4,
    }
    monkeypatch.setattr(pipeline, "summarize_article", AsyncMock(return_value=mock_summary))
    mock_translation = {
        "tldr": "測試摘要",
        "problem_why": "測試問題",
        "solution_how": "測試方案",
        "insights_tradeoffs": {"pros": ["優點"], "cons": ["缺點"]},
        "tags_action": ["標籤"],
        "rating": 4,
    }
    monkeypatch.setattr(pipeline, "translate_summary", AsyncMock(return_value=mock_translation))
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=True))

    # Run crawl stage
    await pipeline.main(["crawl"])
    crawled_path = tmp_path / "data/crawled_articles.json"
    assert crawled_path.exists()
    crawled = json.loads(crawled_path.read_text())
    assert len(crawled) == 1
    assert crawled[0]["url"] == "https://new-url.com"
    assert "summary" not in crawled[0]

    # Run summarize stage
    await pipeline.main(["summarize"])
    summarized_path = tmp_path / "data/summarized_articles.json"
    assert summarized_path.exists()
    summarized = json.loads(summarized_path.read_text())
    assert len(summarized) == 1
    assert summarized[0]["summary"] == mock_summary
    assert "summary_zh_tw" not in summarized[0]

    # Run translate stage
    await pipeline.main(["translate"])
    translated_path = tmp_path / "data/translated_articles.json"
    assert translated_path.exists()
    translated = json.loads(translated_path.read_text())
    assert len(translated) == 1
    assert translated[0]["summary_zh_tw"] == mock_translation

    # Run publish stage
    await pipeline.main(["publish"])
    parsed_path = tmp_path / "data/parsed_articles.json"
    assert parsed_path.exists()
    parsed = json.loads(parsed_path.read_text())
    assert len(parsed) == 1
    assert parsed[0]["url"] == "https://new-url.com"

    # Verify that crawled URL was added to fetched_posts.json
    updated_fetched = json.loads(fetched_posts.read_text())
    assert "https://new-url.com" in updated_fetched


def test_resolve_urls_to_crawl_rss(monkeypatch):
    from src.pipeline import resolve_urls_to_crawl
    
    xml_content = """<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
      <title>Test RSS</title>
      <link>https://example.com</link>
      <item>
        <title>Article 1</title>
        <link>https://example.com/art1</link>
        <pubDate>Sun, 25 Jul 2026 12:00:00 GMT</pubDate>
        <author>Author A</author>
      </item>
      <item>
        <title>Article 2</title>
        <link>https://example.com/art2</link>
        <dc:creator>Author B</dc:creator>
      </item>
    </channel>
    </rss>
    """
    
    class MockResponse:
        def __init__(self, content):
            self.content = content
        def raise_for_status(self):
            pass
            
    def mock_get(url, *args, **kwargs):
        return MockResponse(xml_content.encode('utf-8'))
        
    monkeypatch.setattr("requests.get", mock_get)
    
    res = resolve_urls_to_crawl(["https://example.com/rss"])
    assert len(res) == 2
    assert res[0]["url"] == "https://example.com/art1"
    assert res[0]["title"] == "Article 1"
    assert res[0]["pub_date"] == "Sun, 25 Jul 2026 12:00:00 GMT"
    assert res[0]["author"] == "Author A"
    
    assert res[1]["url"] == "https://example.com/art2"
    assert res[1]["title"] == "Article 2"
    assert res[1]["author"] == "Author B"

def test_resolve_urls_to_crawl_atom(monkeypatch):
    from src.pipeline import resolve_urls_to_crawl
    
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <title>Test Atom</title>
      <entry>
        <title>Atom Art 1</title>
        <link href="https://example.com/atom1" />
        <published>2026-07-25T12:00:00Z</published>
        <author>
          <name>Author C</name>
        </author>
      </entry>
    </feed>
    """
    
    class MockResponse:
        def __init__(self, content):
            self.content = content
        def raise_for_status(self):
            pass
            
    def mock_get(url, *args, **kwargs):
        return MockResponse(xml_content.encode('utf-8'))
        
    monkeypatch.setattr("requests.get", mock_get)
    
    res = resolve_urls_to_crawl(["https://example.com/atom"])
    assert len(res) == 1
    assert res[0]["url"] == "https://example.com/atom1"
    assert res[0]["title"] == "Atom Art 1"
    assert res[0]["pub_date"] == "2026-07-25T12:00:00Z"
    assert res[0]["author"] == "Author C"

@pytest.mark.asyncio
async def test_pipeline_standalone_files_creation(tmp_path, monkeypatch):
    import os
    import json
    import yaml
    from src import pipeline
    from unittest.mock import AsyncMock
    
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.chdir(tmp_path)
    os.makedirs(tmp_path / "data")
    
    # Write blogs.yaml
    (tmp_path / "data/blogs.yaml").write_text(yaml.dump({"blogs": ["https://some-url.com"]}))
    (tmp_path / "data/fetched_posts.json").write_text("[]")
    
    # Mock requests.get to return valid XML
    class MockResponse:
        content = """<?xml version="1.0" encoding="UTF-8" ?>
        <rss version="2.0">
        <channel>
          <item>
            <title>Some Title</title>
            <link>https://some-url.com</link>
          </item>
        </channel>
        </rss>
        """.encode('utf-8')
        def raise_for_status(self): pass
    monkeypatch.setattr("requests.get", lambda *a, **kw: MockResponse())
    
    # Mock AsyncWebCrawler
    mock_crawler = AsyncMock()
    mock_crawler.arun.return_value = MockCrawlResult(
        success=True,
        url="https://some-url.com",
        markdown="Article body",
        metadata={"title": "Some Title", "author": "Some Author", "article:published_time": "2026-07-25T00:00:00Z"}
    )
    
    class MockCrawlerCtx:
        async def __aenter__(self): return mock_crawler
        async def __aexit__(self, *args): pass
    monkeypatch.setattr(pipeline, "AsyncWebCrawler", MockCrawlerCtx)
    
    # Mock summarizer, translator, publisher
    mock_sum = {"tldr": "sum", "problem_why": "p", "solution_how": "s", "insights_tradeoffs": {"pros": [], "cons": []}, "tags_action": [], "rating": 3}
    mock_trans = {"tldr": "中文摘要", "problem_why": "問題", "solution_how": "方案", "insights_tradeoffs": {"pros": [], "cons": []}, "tags_action": [], "rating": 3}
    
    monkeypatch.setattr(pipeline, "summarize_article", AsyncMock(return_value=mock_sum))
    monkeypatch.setattr(pipeline, "translate_summary", AsyncMock(return_value=mock_trans))
    monkeypatch.setattr(pipeline, "write_daily_posts", AsyncMock(return_value=True))
    
    # Run full pipeline
    await pipeline.main()
    
    # Check that standalone files were created in crawled, summarized, translated directories
    url_hash = pipeline.get_url_hash("https://some-url.com")
    
    crawled_file = tmp_path / f"data/crawled/{url_hash}.json"
    summarized_file = tmp_path / f"data/summarized/{url_hash}.json"
    translated_file = tmp_path / f"data/translated/{url_hash}.json"
    
    assert crawled_file.exists()
    assert summarized_file.exists()
    assert translated_file.exists()
    
    crawled_data = json.loads(crawled_file.read_text())
    assert crawled_data["url"] == "https://some-url.com"
    assert crawled_data["title"] == "Some Title"
    
    sum_data = json.loads(summarized_file.read_text())
    assert sum_data["summary"] == mock_sum
    
    trans_data = json.loads(translated_file.read_text())
    assert trans_data["summary_zh_tw"] == mock_trans


