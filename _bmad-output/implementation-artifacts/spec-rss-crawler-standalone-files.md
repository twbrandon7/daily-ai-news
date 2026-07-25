---
title: 'RSS Crawler and Standalone File Processing'
type: 'feature'
created: '2026-07-25T19:50:00Z'
status: 'done'
baseline_commit: '405bb24e7be17c8799fd7c24de7c3a2fc5c13cc4'
review_loop_iteration: 0
context: []
---

## Intent

**Problem:** The crawler only crawls exact configured URLs without finding new content from RSS feeds. The pipeline concatenates all crawled, summarized, and translated articles into single monolithic JSON files, which is fragile and does not scale well.

**Approach:** Modify the pipeline to parse RSS feed URLs from config, fetch new article links from RSS, crawl them, and process each article in standalone files through crawl, summarize, and translate stages.

## Boundaries & Constraints

**Always:**
- Use `BeautifulSoup` to parse RSS and Atom XML feeds.
- Save standalone files under `data/crawled/`, `data/summarized/`, and `data/translated/` named with the MD5 hash of the normalized URL (e.g. `{url_hash}.json`).
- Ensure all intermediate stages work with standalone files.
- Retain `data/fetched_posts.json` as the source of truth for deduplication.

**Ask First:**
- Modifying the keys or format of `data/blogs.yaml`.

**Never:**
- Install/use external feed parsing libraries (e.g., `feedparser`). Only use standard library or existing dependencies (`beautifulsoup4`, `httpx`, `requests`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| RSS Parse Success | XML with valid <item> tags | List of article dicts (url, title, pub_date, author) | N/A |
| Atom Parse Success | XML with valid <entry> tags | List of article dicts (url, title, pub_date, author) | N/A |
| Crawl Standalone | 2 new articles crawled | 2 files in `data/crawled/` named by MD5 hash | Log error if single article fails, continue with others |
| Summarize Standalone | 2 files in `data/crawled/`, 1 already summarized | Only 1 new file written to `data/summarized/` | Skip and log errors on failure |
| Translate Standalone | 2 files in `data/summarized/`, 1 already translated | Only 1 new file written to `data/translated/` | Skip and log errors on failure |
| Publish Daily Post | Standalone translated files in `data/translated/` | Daily post files created under `content/en/posts/` and `content/zh-tw/posts/` | Delete partially created posts on failure |

## Code Map

- `src/pipeline.py` -- Main pipeline implementation containing stages: crawl, summarize, translate, publish.
- `tests/test_pipeline.py` -- Pipeline tests verifying the stages, deduplication, and file outputs.

## Tasks & Acceptance

**Execution:**
- [x] `src/pipeline.py` -- Implement RSS/Atom feed parsing, feed fetching, and standalone file read/write logic for all stages.
- [x] `tests/test_pipeline.py` -- Update and add tests to verify RSS parsing, crawler delegation, and standalone file processing.

**Acceptance Criteria:**
- Given a list of RSS feed URLs in `data/blogs.yaml`, when running the crawl stage, then the new article URLs are extracted, crawled, and saved as separate `{url_hash}.json` files under `data/crawled/`.
- Given crawled articles in `data/crawled/`, when running the summarize stage, then each article is summarized and saved as a separate `{url_hash}.json` file under `data/summarized/`.
- Given summarized articles in `data/crawled/`, when running the translate stage, then each summary is translated and saved as a separate `{url_hash}.json` file under `data/translated/`.
- Given translated summaries in `data/translated/`, when running the publish stage, then a daily post is generated for the English and Chinese versions, and the articles are marked as published in `data/fetched_posts.json` and `data/parsed_articles.json`.

## Design Notes

The standalone file structure will use the MD5 hash of the normalized URL:
```python
import hashlib
def get_url_hash(url: str) -> str:
    return hashlib.md5(normalize_url(url).encode('utf-8')).hexdigest()
```
Each JSON file will contain the fields representing the state of that article at that stage. For example, a file in `data/crawled/` will have `url`, `title`, `publication_date`, `author`, and `body`.

## Verification

**Commands:**
- `.venv/bin/pytest` -- expected: all tests pass successfully

## Suggested Review Order

**Feed Resolution and Crawling**

- Fetches and parses RSS/Atom XML feeds using BeautifulSoup and requests.
  [`pipeline.py:55`](../../src/pipeline.py#L55)

- Crawls resolved articles and saves them to standalone files in data/crawled.
  [`pipeline.py:333`](../../src/pipeline.py#L333)

**Standalone File Pipeline Processing**

- Summarizes articles from standalone crawled files and outputs to data/summarized.
  [`pipeline.py:430`](../../src/pipeline.py#L430)

- Translates summaries from standalone summarized files and outputs to data/translated.
  [`pipeline.py:507`](../../src/pipeline.py#L507)

- Publishes articles from standalone translated files and updates the deduplication store.
  [`pipeline.py:589`](../../src/pipeline.py#L589)

**Peripherals**

- Updated configuration with list of target RSS feeds.
  [`blogs.yaml:1`](../../data/blogs.yaml#L1)

- Added tests for RSS/Atom parsing and standalone folder output structure.
  [`test_pipeline.py:652`](../../tests/test_pipeline.py#L652)
