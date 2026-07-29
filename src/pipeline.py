import asyncio
import datetime
import email.utils
import json
import os
import re
import sys
import argparse
import yaml
import hashlib
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

from src.summarizer import summarize_article
from src.translator import translate_summary
from src.publisher import write_daily_posts

DEFAULT_CUTOFF_DATE = "2026-07-24"

def parse_date_to_iso(date_str: str) -> str | None:
    """Parse various RSS/Atom/HTML date formats into YYYY-MM-DD string."""
    if not date_str or not isinstance(date_str, str) or not date_str.strip():
        return None
    date_str = date_str.strip()
    
    # Check for YYYY-MM-DD pattern directly
    match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
    if match:
        return match.group(0)
        
    # Try RFC 2822 (common in RSS pubDate: e.g. "Sun, 25 Jul 2026 12:00:00 GMT")
    try:
        parsed_dt = email.utils.parsedate_to_datetime(date_str)
        if parsed_dt:
            return parsed_dt.date().isoformat()
    except Exception:
        pass
        
    return None

def log_error(blog_url: str, error_message: str):
    """Log error in the required JSON format."""
    log_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        "stage": "crawl",
        "blog_url": blog_url,
        "error_message": error_message
    }
    print(json.dumps(log_data))

def normalize_url(url: str) -> str:
    """Normalize URL by lowering case of scheme and host, and stripping trailing slash."""
    url = url.strip()
    parts = url.split("://", 1)
    if len(parts) == 2:
        scheme, rest = parts[0].lower(), parts[1]
        host_parts = rest.split("/", 1)
        host = host_parts[0].lower()
        path = "/" + host_parts[1] if len(host_parts) == 2 else ""
        if path.endswith("/"):
            path = path[:-1]
        return f"{scheme}://{host}{path}"
    else:
        url = url.lower()
        if url.endswith("/"):
            url = url[:-1]
        return url

def get_url_hash(url: str) -> str:
    """Get MD5 hash of normalized URL."""
    normalized = normalize_url(url)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def resolve_urls_to_crawl(config_urls: list[str], dedup_store: dict[str, str] = None, cutoff_date: str = DEFAULT_CUTOFF_DATE) -> list[dict]:
    """Resolve a list of config URLs (RSS feeds) to a list of article dicts to crawl."""
    if dedup_store is None:
        dedup_store = {}
    normalized_dedup = {normalize_url(u) for u in dedup_store.keys()}
    resolved = []
    for url in config_urls:
        url = url.strip()
        if not url:
            continue
        try:
            print(f"Fetching RSS feed: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            content = response.content
            
            # Check if XML
            is_xml = False
            content_start = content[:500].strip().lower()
            if b"<?xml" in content_start or b"<rss" in content_start or b"<feed" in content_start or b"<item" in content_start or b"<entry" in content_start:
                is_xml = True
                
            if not is_xml:
                print(f"Error: Feed URL {url} did not return valid XML. Skipping.", file=sys.stderr)
                continue
                
            print(f"  Detected RSS/Atom feed XML for: {url}")
            soup = BeautifulSoup(content, "xml")
            feed_articles = []
            
            # RSS
            items = soup.find_all("item")
            if items:
                for item in items:
                    link_el = item.find("link")
                    link = link_el.get_text(strip=True) if link_el else ""
                    
                    title_el = item.find("title")
                    title = title_el.get_text(strip=True) if title_el else "Untitled"
                    
                    pub_date_el = item.find("pubDate")
                    pub_date = pub_date_el.get_text(strip=True) if pub_date_el else ""
                    
                    author_el = item.find("creator") or item.find("dc:creator") or item.find("author")
                    author = author_el.get_text(strip=True) if author_el else "Unknown"
                    
                    if link:
                        link = urljoin(url, link)
                        norm_link = normalize_url(link)
                        if norm_link in normalized_dedup:
                            print(f"  Skipping already recorded article: {link}")
                            continue
                        pub_date_iso = parse_date_to_iso(pub_date)
                        if pub_date_iso and pub_date_iso < cutoff_date:
                            print(f"  Skipping article published before cutoff ({pub_date_iso} < {cutoff_date}): {link}")
                            dedup_store[link] = "skipped"
                            continue
                        feed_articles.append({
                            "url": link,
                            "title": title,
                            "pub_date": pub_date,
                            "author": author,
                            "feed_url": url
                        })
            else:
                # Atom
                entries = soup.find_all("entry")
                for entry in entries:
                    link_el = entry.find("link")
                    link = ""
                    if link_el:
                        link = link_el.get("href") or link_el.get_text(strip=True)
                    
                    title_el = entry.find("title")
                    title = title_el.get_text(strip=True) if title_el else "Untitled"
                    
                    pub_date_el = entry.find("published") or entry.find("updated")
                    pub_date = pub_date_el.get_text(strip=True) if pub_date_el else ""
                    
                    author_el = entry.find("author")
                    author = "Unknown"
                    if author_el:
                        name_el = author_el.find("name")
                        if name_el:
                            author = name_el.get_text(strip=True)
                        else:
                            author = author_el.get_text(strip=True)
                            
                    if link:
                        link = urljoin(url, link)
                        norm_link = normalize_url(link)
                        if norm_link in normalized_dedup:
                            print(f"  Skipping already recorded article: {link}")
                            continue
                        pub_date_iso = parse_date_to_iso(pub_date)
                        if pub_date_iso and pub_date_iso < cutoff_date:
                            print(f"  Skipping article published before cutoff ({pub_date_iso} < {cutoff_date}): {link}")
                            dedup_store[link] = "skipped"
                            continue
                        feed_articles.append({
                            "url": link,
                            "title": title,
                            "pub_date": pub_date,
                            "author": author,
                            "feed_url": url
                        })
            if not feed_articles:
                print(f"Error: No new articles found in feed {url}. Skipping.", file=sys.stderr)
                continue
                
            print(f"  Found {len(feed_articles)} new articles in feed.")
            resolved.extend(feed_articles)
        except Exception as e:
            print(f"Error accessing or parsing feed {url}: {e}. Skipping.", file=sys.stderr)
    return resolved



def load_deduplication_store(file_path: str) -> dict[str, str]:
    """Load deduplication store from JSON file, returning a dict of url -> status ('fetched' | 'skipped')."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            if "articles" in data and isinstance(data["articles"], dict):
                return {str(k): str(v) for k, v in data["articles"].items()}
            else:
                # Fallback for previous per-feed dict format
                res = {}
                for k, v in data.items():
                    if isinstance(v, (list, set)):
                        for url in v:
                            res[str(url)] = "fetched"
                return res
        elif isinstance(data, list):
            # Fallback for legacy flat list format
            return {str(url): "fetched" for url in data}
        else:
            print(f"Warning: Expected dict or list in deduplication store at {file_path}, got {type(data).__name__}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to load deduplication store from {file_path}: {e}", file=sys.stderr)
    return {}

def save_deduplication_store(file_path: str, store: dict[str, str]):
    """Save deduplication store to JSON file under {"articles": {"<url>": "status"}}."""
    temp_path = None
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        temp_path = file_path + ".tmp"
        sorted_articles = {k: store[k] for k in sorted(store.keys())}
        payload = {"articles": sorted_articles}
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(temp_path, file_path)
    except Exception as e:
        print(f"Warning: Failed to save deduplication store to {file_path}: {e}", file=sys.stderr)
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


def extract_article_info(url, result):
    """Extract title, publication date, author, and main article body from CrawlResult."""
    metadata = result.metadata or {}
    html = result.html
    soup = BeautifulSoup(html, 'html.parser') if html else None
    
    # 1. Title
    title = metadata.get('title') or metadata.get('og:title')
    if isinstance(title, list):
        title = title[0] if title else ""
    elif title is not None:
        title = str(title)
        
    if not title and soup:
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
            
    # 2. Author
    author = metadata.get('author') or metadata.get('og:author') or metadata.get('twitter:creator')
    if isinstance(author, list):
        author = author[0] if author else ""
    elif author is not None:
        author = str(author)
        
    if not author and soup:
        author_meta = (
            soup.find('meta', attrs={'name': 'author'}) or
            soup.find('meta', attrs={'property': 'article:author'})
        )
        if author_meta:
            author = author_meta.get('content', '').strip()
        else:
            author_el = soup.find(class_=re.compile(r'author|byline', re.I))
            if author_el:
                author = author_el.get_text(strip=True)
                
    # 3. Publication Date
    pub_date = (
        metadata.get('article:published_time') or 
        metadata.get('og:article:published_time') or
        metadata.get('published_time') or
        metadata.get('date') or
        metadata.get('pubdate') or
        metadata.get('sailthru.date') or
        metadata.get('parsely-pub-date')
    )
    if isinstance(pub_date, list):
        pub_date = pub_date[0] if pub_date else ""
    elif pub_date is not None:
        pub_date = str(pub_date)
        
    if not pub_date and soup:
        for name in ['article:published_time', 'published_time', 'date', 'pubdate', 'parsely-pub-date', 'datePublished']:
            meta = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': name}) or soup.find('meta', attrs={'itemprop': name})
            if meta:
                pub_date = meta.get('content', '').strip()
                break
        if not pub_date:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    if not script.string:
                        continue
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        pub_date = data.get('datePublished') or data.get('dateCreated')
                        if not pub_date and '@graph' in data:
                            for item in data['@graph']:
                                pub_date = item.get('datePublished') or item.get('dateCreated')
                                if pub_date:
                                    break
                    elif isinstance(data, list):
                        for item in data:
                            pub_date = item.get('datePublished') or item.get('dateCreated')
                            if pub_date:
                                break
                    if pub_date:
                        break
                except Exception:
                    pass
        if not pub_date:
            time_el = soup.find('time')
            if time_el:
                pub_date = time_el.get('datetime') or time_el.get_text(strip=True)
                
    if not pub_date:
        pub_date = datetime.date.today().isoformat()
    else:
        pub_date = str(pub_date)
        match = re.search(r'\d{4}-\d{2}-\d{2}', pub_date)
        if match:
            pub_date = match.group(0)
        else:
            pub_date = datetime.date.today().isoformat()
            
    # 4. Main article body text
    body = ""
    if result.markdown:
        if isinstance(result.markdown, str):
            body = result.markdown
        else:
            body = getattr(result.markdown, 'fit_markdown', None) or getattr(result.markdown, 'raw_markdown', None) or str(result.markdown)
    
    return {
        'url': url,
        'title': (title or 'Untitled').strip(),
        'publication_date': pub_date,
        'author': (author or 'Unknown').strip(),
        'body': (body or '').strip()
    }

async def crawl_blog(crawler, url, run_config):
    """Crawl a single blog URL and return parsed article details."""
    try:
        result = await crawler.arun(url=url, config=run_config)
        if not result.success:
            error_msg = result.error_message or "Unknown crawl failure"
            log_error(url, error_msg)
            return url, None, error_msg
        
        parsed_data = extract_article_info(url, result)
        return url, parsed_data, None
    except Exception as e:
        error_msg = str(e)
        log_error(url, error_msg)
        return url, None, error_msg

PARSED_DIR = "data/parsed"
DEDUP_PATH = "data/fetched_posts.json"
BLOGS_CONFIG_PATH = "data/blogs.yaml"
RUNS_PATH = "data/runs.json"

def load_runs_registry(file_path: str = RUNS_PATH) -> dict:
    """Load runs registry from JSON file, returning a dict structured as {"runs": {}}."""
    if not os.path.exists(file_path):
        return {"runs": {}}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "runs" in data and isinstance(data["runs"], dict):
            return data
    except Exception as e:
        print(f"Warning: Failed to load runs registry from {file_path}: {e}", file=sys.stderr)
    return {"runs": {}}

def save_runs_registry(file_path: str, store: dict):
    """Save runs registry to JSON file under {"runs": ...} atomically."""
    temp_path = None
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        temp_path = file_path + ".tmp"
        sorted_runs = {}
        for k in sorted(store.get("runs", {}).keys()):
            sorted_runs[k] = store["runs"][k]
        payload = {"runs": sorted_runs}
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(temp_path, file_path)
    except Exception as e:
        print(f"Warning: Failed to save runs registry to {file_path}: {e}", file=sys.stderr)
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def register_run_articles(run_date: str, url_hashes: list[str], runs_path: str = RUNS_PATH):
    """Register a list of article url_hashes under runs[run_date]["articles"] with published: False."""
    if not url_hashes:
        return
    store = load_runs_registry(runs_path)
    runs = store.setdefault("runs", {})
    if run_date not in runs:
        runs[run_date] = {"articles": [], "published": False}
    elif not isinstance(runs[run_date], dict):
        runs[run_date] = {"articles": [], "published": False}

    current_hashes = list(runs[run_date].get("articles", []))
    for h in url_hashes:
        if h not in current_hashes:
            current_hashes.append(h)
    runs[run_date]["articles"] = current_hashes
    if "published" not in runs[run_date]:
        runs[run_date]["published"] = False
    save_runs_registry(runs_path, store)

def validate_google_api_key():
    if not (os.environ.get("GOOGLE_API_KEY") or "").strip():
        print(
            "Error: GOOGLE_API_KEY environment variable is not set. "
            "Set it before running the pipeline.",
            file=sys.stderr,
        )
        sys.exit(1)

async def run_crawl():
    # Load configuration
    try:
        with open(BLOGS_CONFIG_PATH, "r") as f:
            blog_config = yaml.safe_load(f) or {}
    except OSError as e:
        print(f"Error reading configuration file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
            
    urls = blog_config.get("blogs", [])
    cutoff_date = blog_config.get("cutoff_date", DEFAULT_CUTOFF_DATE)
    if not urls:
        print("Warning: No URLs found in data/blogs.yaml")
        os.makedirs("data/crawled", exist_ok=True)
        return []

    dedup_store = load_deduplication_store(DEDUP_PATH)
    articles_to_crawl = resolve_urls_to_crawl(urls, dedup_store=dedup_store, cutoff_date=cutoff_date)
    save_deduplication_store(DEDUP_PATH, dedup_store)

    # Setup CrawlerRunConfig with PruningContentFilter to exclude headers, footers, sidebars
    run_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter()
        ),
        cache_mode=CacheMode.BYPASS
    )
    
    failures = []
    successes = []
    
    os.makedirs("data/crawled", exist_ok=True)
    
    try:
        print(f"Starting crawl for {len(articles_to_crawl)} resolved URLs...")
        async with AsyncWebCrawler() as crawler:
            for art in articles_to_crawl:
                url = art["url"]
                feed_url = art.get("feed_url", "direct")
                
                normalized_url = normalize_url(url)
                normalized_dedup = {normalize_url(u) for u in dedup_store.keys()}
                if normalized_url in normalized_dedup:
                    print(f"Skipping already recorded URL: {url}")
                    continue
                    
                url, parsed_data, error_msg = await crawl_blog(crawler, url, run_config)
                if error_msg:
                    failures.append((url, error_msg))
                else:
                    # Enrich parsed_data with info from feed if crawler metadata is missing
                    if parsed_data.get("title") == "Untitled" and art.get("title") != "Untitled":
                        parsed_data["title"] = art["title"]
                    if parsed_data.get("author") == "Unknown" and art.get("author") != "Unknown":
                        parsed_data["author"] = art["author"]
                    if art.get("pub_date"):
                        match = re.search(r'\d{4}-\d{2}-\d{2}', art["pub_date"])
                        if match and parsed_data["publication_date"] == datetime.date.today().isoformat():
                            parsed_data["publication_date"] = match.group(0)
                            
                    # Double check cutoff date after crawl
                    crawled_date = parse_date_to_iso(parsed_data.get("publication_date"))
                    if crawled_date and crawled_date < cutoff_date:
                        print(f"Skipping crawled article published before cutoff ({crawled_date} < {cutoff_date}): {url}")
                        dedup_store[url] = "skipped"
                        continue
                        
                    parsed_data["feed_url"] = feed_url

                    successes.append(parsed_data)
                    print(f"Successfully crawled: {url}")
                    print(f"  Title: {parsed_data['title']}")
                    print(f"  Author: {parsed_data['author']}")
                    print(f"  Date: {parsed_data['publication_date']}")
                    print(f"  Body length: {len(parsed_data['body'])} characters")
                    print("-" * 40)
                    
                    # Save standalone file
                    url_hash = get_url_hash(url)
                    file_path = os.path.join("data", "crawled", f"{url_hash}.json")
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(parsed_data, f, indent=2)
                    
        # Final reporting
        print(f"\nCrawl execution summary:")
        print(f"Total processed: {len(articles_to_crawl)}")
        print(f"Successful crawls: {len(successes)}")
        print(f"Failed crawls: {len(failures)}")
        
        print(f"Successfully saved crawled articles to standalone files under data/crawled/")
        
        if failures:
            print("\nFailed URLs and errors:")
            for url, err in failures:
                print(f" - {url}: {err}")

        if successes:
            today_str = datetime.date.today().isoformat()
            hashes = [get_url_hash(a["url"]) for a in successes]
            register_run_articles(today_str, hashes)
                
        return successes
    except Exception as e:
        print(f"Error during crawl: {e}", file=sys.stderr)
        sys.exit(1)

async def run_summarize():
    validate_google_api_key()
    
    crawled_dir = os.path.join("data", "crawled")
    os.makedirs(crawled_dir, exist_ok=True)
    os.makedirs(os.path.join("data", "summarized"), exist_ok=True)
    
    crawled_files = [os.path.join(crawled_dir, f) for f in os.listdir(crawled_dir) if f.endswith(".json")]
    
    articles = []
    for file_path in crawled_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                articles.append(json.load(f))
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    if not articles:
        print("No crawled articles found.")
        return []

    print(f"Starting summarization for {len(articles)} articles...")
    
    successes = []
    failures = []
    
    for art in articles:
        url = art['url']
        url_hash = get_url_hash(url)
        summarized_file_path = os.path.join("data", "summarized", f"{url_hash}.json")
        
        # Optimization: skip if already has a valid summary
        if os.path.exists(summarized_file_path):
            try:
                with open(summarized_file_path, "r", encoding="utf-8") as f:
                    sum_art = json.load(f)
                if "summary" in sum_art and sum_art["summary"]:
                    successes.append(sum_art)
                    print(f"Skipping already summarized: {url}")
                    continue
            except Exception:
                pass
                
        summary = await summarize_article(url, art['body'], art['title'])
        if summary is None:
            failures.append((url, "summarization failed"))
        else:
            art['summary'] = summary
            successes.append(art)
            with open(summarized_file_path, "w", encoding="utf-8") as f:
                json.dump(art, f, indent=2)
            print(f"Successfully summarized: {url}")
            
    print(f"Successfully saved summarized articles to standalone files under data/summarized/")
    
    if failures:
        print("\nFailed summarizations:")
        for url, err in failures:
            print(f" - {url}: {err}")

    if successes:
        today_str = datetime.date.today().isoformat()
        hashes = [get_url_hash(a["url"]) for a in successes]
        register_run_articles(today_str, hashes)
            
    return successes

async def run_translate():
    validate_google_api_key()
    
    summarized_dir = os.path.join("data", "summarized")
    os.makedirs(summarized_dir, exist_ok=True)
    os.makedirs(os.path.join("data", "translated"), exist_ok=True)
    
    summarized_files = [os.path.join(summarized_dir, f) for f in os.listdir(summarized_dir) if f.endswith(".json")]
    
    articles = []
    for file_path in summarized_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                articles.append(json.load(f))
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    if not articles:
        print("No summarized articles found.")
        return []

    print(f"Starting translation for {len(articles)} articles...")
    
    successes = []
    failures = []
    
    for art in articles:
        url = art['url']
        url_hash = get_url_hash(url)
        translated_file_path = os.path.join("data", "translated", f"{url_hash}.json")
        
        # Optimization: skip if already has a valid translation
        if os.path.exists(translated_file_path):
            try:
                with open(translated_file_path, "r", encoding="utf-8") as f:
                    trans_art = json.load(f)
                if "summary_zh_tw" in trans_art and trans_art["summary_zh_tw"]:
                    successes.append(trans_art)
                    print(f"Skipping already translated: {url}")
                    continue
            except Exception:
                pass
                
        summary = art.get('summary')
        if not summary:
            failures.append((url, "missing summary"))
            continue
            
        translated = await translate_summary(url, summary)
        if translated is None:
            failures.append((url, "translation failed"))
        else:
            art['summary_zh_tw'] = translated
            successes.append(art)
            with open(translated_file_path, "w", encoding="utf-8") as f:
                json.dump(art, f, indent=2)
            print(f"Successfully translated: {url}")
            
    print(f"Successfully saved translated articles to standalone files under data/translated/")
    
    if failures:
        print("\nFailed translations:")
        for url, err in failures:
            print(f" - {url}: {err}")

    if successes:
        today_str = datetime.date.today().isoformat()
        hashes = [get_url_hash(a["url"]) for a in successes]
        register_run_articles(today_str, hashes)
            
    return successes

async def run_publish():
    runs_store = load_runs_registry(RUNS_PATH)
    runs = runs_store.get("runs", {})
    
    # Backfill if runs is empty but translated files exist
    translated_dir = os.path.join("data", "translated")
    if not runs and os.path.exists(translated_dir):
        translated_files = [f[:-5] for f in os.listdir(translated_dir) if f.endswith(".json")]
        if translated_files:
            today_str = datetime.date.today().isoformat()
            register_run_articles(today_str, translated_files)
            runs_store = load_runs_registry(RUNS_PATH)
            runs = runs_store.get("runs", {})

    unpublished_dates = [
        d for d, info in runs.items()
        if isinstance(info, dict) and not info.get("published", False) and info.get("articles")
    ]

    if not unpublished_dates:
        print("No unpublished runs to publish.")
        os.makedirs(PARSED_DIR, exist_ok=True)
        return

    # Check for GOOGLE_API_KEY as publishing generates and translates highlights
    validate_google_api_key()
    
    dedup_store = load_deduplication_store(DEDUP_PATH)
    os.makedirs(PARSED_DIR, exist_ok=True)

    try:
        for run_date in sorted(unpublished_dates):
            hashes = runs[run_date].get("articles", [])
            if not hashes:
                continue
                
            articles = []
            for h in hashes:
                file_path = os.path.join(translated_dir, f"{h}.json")
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            articles.append(json.load(f))
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}", file=sys.stderr)
                else:
                    print(f"Warning: Translated file {file_path} for run {run_date} not found.", file=sys.stderr)

            if not articles:
                print(f"No translated articles found for run date {run_date}. Skipping.")
                continue

            print(f"Starting publishing for {len(articles)} articles in run date {run_date}...")
            try:
                pub_success = await write_daily_posts(run_date, articles)
                if not pub_success:
                    print(f"Error: Publishing daily posts failed for run date {run_date}.", file=sys.stderr)
                    sys.exit(1)
            except Exception as e:
                print(f"Error: Publishing failed for run date {run_date}: {e}", file=sys.stderr)
                sys.exit(1)

            try:
                for item in articles:
                    url_hash = get_url_hash(item['url'])
                    parsed_file_path = os.path.join(PARSED_DIR, f"{url_hash}.json")
                    with open(parsed_file_path, "w", encoding="utf-8") as f:
                        json.dump(item, f, indent=2)
                    dedup_store[item['url']] = "fetched"
                print(f"Successfully saved {len(articles)} articles to standalone files under {PARSED_DIR}/")
            except Exception as e:
                print(f"Error saving parsed articles to file: {e}", file=sys.stderr)

            runs[run_date]["published"] = True
            save_runs_registry(RUNS_PATH, runs_store)
            print(f"Successfully published {len(articles)} articles for run date {run_date}.")
    finally:
        save_deduplication_store(DEDUP_PATH, dedup_store)



async def main(args=None):
    if args is None:
        if any("pytest" in arg or "py.test" in arg for arg in sys.argv) or "pytest" in sys.modules:
            args = ["all"]
        else:
            args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Daily AI News Pipeline")
    parser.add_argument(
        "stage",
        nargs="?",
        choices=["crawl", "summarize", "translate", "publish", "all"],
        default="all",
        help="Stage of the pipeline to run (default: all)"
    )
    parsed_args = parser.parse_args(args)
    stage = parsed_args.stage

    if stage == "crawl":
        await run_crawl()
    elif stage == "summarize":
        await run_summarize()
    elif stage == "translate":
        await run_translate()
    elif stage == "publish":
        await run_publish()
    elif stage == "all":
        await run_crawl()
        await run_summarize()
        await run_translate()
        await run_publish()

if __name__ == "__main__":
    asyncio.run(main())
