import asyncio
import datetime
import json
import os
import re
import sys
import yaml
from bs4 import BeautifulSoup

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

from src.summarizer import summarize_article

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

def load_deduplication_store(file_path: str) -> set[str]:
    """Load existing URLs from a JSON file, returning a set. Fallback to empty set on error/missing."""
    if not os.path.exists(file_path):
        return set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return set(str(url) for url in data)
        else:
            print(f"Warning: Expected list in deduplication store at {file_path}, got {type(data).__name__}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to load deduplication store from {file_path}: {e}", file=sys.stderr)
    return set()

def save_deduplication_store(file_path: str, urls: set[str]):
    """Save the updated URL list to a JSON file in a structured JSON format (array of strings)."""
    temp_path = None
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        temp_path = file_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(sorted(list(urls)), f, indent=2)
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

async def main():
    # Check for required environment variable before any crawling
    if not (os.environ.get("GOOGLE_API_KEY") or "").strip():
        print(
            "Error: GOOGLE_API_KEY environment variable is not set. "
            "Set it before running the pipeline.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load configuration
    config_path = "data/blogs.yaml"
    blog_config = {}
    try:
        with open(config_path, "r") as f:
            blog_config = yaml.safe_load(f) or {}
    except OSError as e:
        print(f"Error reading configuration file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
        
    if not isinstance(blog_config, dict):
        print("Error: Configuration is not a valid dictionary", file=sys.stderr)
        sys.exit(1)
            
    urls = blog_config.get("blogs", [])
    if not urls:
        print("Warning: No URLs found in data/blogs.yaml")
        sys.exit(0)
        
    # Setup CrawlerRunConfig with PruningContentFilter to exclude headers, footers, sidebars
    run_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter()
        ),
        cache_mode=CacheMode.BYPASS
    )
    
    dedup_path = "data/fetched_posts.json"
    dedup_store = load_deduplication_store(dedup_path)
    dedup_set_normalized = {normalize_url(u) for u in dedup_store}
    
    failures = []
    successes = []
    
    try:
        print(f"Starting crawl for {len(urls)} URLs...")
        async with AsyncWebCrawler() as crawler:
            for url in urls:
                if normalize_url(url) in dedup_set_normalized:
                    print(f"Skipping already crawled URL: {url}")
                    continue
                    
                url, parsed_data, error_msg = await crawl_blog(crawler, url, run_config)
                if error_msg:
                    failures.append((url, error_msg))
                else:
                    summary = await summarize_article(url, parsed_data['body'], parsed_data['title'])
                    if summary is None:
                        failures.append((url, "summarization failed"))
                    else:
                        parsed_data['summary'] = summary
                        successes.append(parsed_data)
                        print(f"Successfully crawled: {url}")
                        print(f"  Title: {parsed_data['title']}")
                        print(f"  Author: {parsed_data['author']}")
                        print(f"  Date: {parsed_data['publication_date']}")
                        print(f"  Body length: {len(parsed_data['body'])} characters")
                        print("-" * 40)
                    
        # Final reporting
        print(f"\nCrawl execution summary:")
        print(f"Total processed: {len(urls)}")
        print(f"Successful crawls: {len(successes)}")
        print(f"Failed crawls: {len(failures)}")
        
        # Save parsed articles to data/parsed_articles.json
        if successes:
            output_dir = "data"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "parsed_articles.json")
            try:
                with open(output_path, "w") as f:
                    json.dump(successes, f, indent=2)
                print(f"Successfully saved {len(successes)} articles to {output_path}")
                for item in successes:
                    dedup_store.add(item['url'])
            except Exception as e:
                print(f"Error saving parsed articles to file: {e}", file=sys.stderr)
    finally:
        save_deduplication_store(dedup_path, dedup_store)
            
    if failures:
        print("\nFailed URLs and errors:")
        for url, err in failures:
            print(f" - {url}: {err}")

if __name__ == "__main__":
    asyncio.run(main())
