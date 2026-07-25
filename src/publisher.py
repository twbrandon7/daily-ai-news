import os
import sys
import json
import re
import datetime
import yaml
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

DAILY_HIGHLIGHT_PROMPT = """You are a technical editor summarizing the day's AI news.
Given a list of article titles and their brief TL;DR summaries, write a concise daily highlight summary in English.
Focus only on the most important technical developments, trends, or breakthroughs of the day.
Keep the summary to one short paragraph. Do not include any HTML, markdown formatting, or extra commentary.
"""

HIGHLIGHT_TRANSLATE_PROMPT = """You are a professional technical translator. Translate the given English daily highlight summary into Traditional Chinese (Taiwan).

Strict Guidelines:
1. Translate the content naturally to Traditional Chinese (Taiwan).
2. Keep these technical terms in English verbatim (case-insensitive, do not translate them to Chinese): "prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token".
3. Return ONLY the translated text. Do not include any HTML, markdown blocks, formatting, or extra commentary.
"""

def _log_publish_error(error_message: str) -> None:
    """Log a structured JSON error entry to stderr for publishing failures."""
    log_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stage": "publish",
        "error_message": error_message,
    }
    print(json.dumps(log_data), file=sys.stderr)

def _validate_highlight_terms(english: str, translated: str) -> None:
    """Validate that required English developer terms are preserved case-insensitively verbatim."""
    TERMS = ["prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token"]
    for term in TERMS:
        # Use regex to find term with word boundaries (allowing space or hyphen for fine-tuning)
        term_pattern = r"\b" + re.escape(term).replace(r"\-", r"[\-\s]?") + r"\b"
        if re.search(term_pattern, english, re.I):
            if not re.search(term_pattern, translated, re.I):
                raise ValueError(f"Term '{term}' missing in translated daily highlight.")

async def generate_daily_highlight(articles: list[dict]) -> str | None:
    """
    Generate a daily highlight summary in English from a list of articles using Google ADK and gemini-3.5-flash-lite.
    """
    if not articles:
        return None

    if not (os.environ.get("GOOGLE_API_KEY") or "").strip():
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    articles_info = []
    for idx, art in enumerate(articles, 1):
        title = art.get("title", "Untitled")
        tldr = (art.get("summary") or {}).get("tldr", "")
        articles_info.append(f"{idx}. Title: {title}\n   TL;DR: {tldr}")
    user_message_text = "\n\n".join(articles_info)

    try:
        agent = LlmAgent(
            model="gemini-3.5-flash-lite",
            name="daily_highlight_generator",
            instruction=DAILY_HIGHLIGHT_PROMPT,
        )
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name="daily_highlight_generator",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="daily_highlight_generator",
            user_id="pipeline",
        )

        new_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=user_message_text)],
        )

        response_text = None
        async for event in runner.run_async(
            user_id="pipeline",
            session_id=session.id,
            new_message=new_message,
        ):
            if event.is_final_response():
                try:
                    parts_text = "".join(
                        p.text for p in event.content.parts if getattr(p, "text", None)
                    )
                    if parts_text:
                        response_text = parts_text
                except (AttributeError, TypeError):
                    pass

        if response_text is None:
            return None

        return response_text.strip()

    except Exception as exc:
        raise RuntimeError(f"Error during daily highlight generation: {exc}") from exc

async def translate_highlight(highlight: str) -> str | None:
    """
    Translate an English highlight into Traditional Chinese (Taiwan) using Google ADK and gemini-3.5-flash-lite.
    """
    if not highlight:
        return None

    if not (os.environ.get("GOOGLE_API_KEY") or "").strip():
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    try:
        agent = LlmAgent(
            model="gemini-3.5-flash-lite",
            name="highlight_translator",
            instruction=HIGHLIGHT_TRANSLATE_PROMPT,
        )
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name="highlight_translator",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="highlight_translator",
            user_id="pipeline",
        )

        new_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=highlight)],
        )

        response_text = None
        async for event in runner.run_async(
            user_id="pipeline",
            session_id=session.id,
            new_message=new_message,
        ):
            if event.is_final_response():
                try:
                    parts_text = "".join(
                        p.text for p in event.content.parts if getattr(p, "text", None)
                    )
                    if parts_text:
                        response_text = parts_text
                except (AttributeError, TypeError):
                    pass

        if response_text is None:
            return None

        return response_text.strip()

    except Exception as exc:
        raise RuntimeError(f"Error during highlight translation: {exc}") from exc

async def write_daily_posts(date_str: str, articles: list[dict]) -> bool:
    """
    Generate bilingual daily posts and save them under content/en/posts and content/zh-tw/posts.
    """
    if not articles:
        return True

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        exc = ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
        _log_publish_error(str(exc))
        raise exc

    en_path = os.path.join("content", "en", "posts", f"{date_str}.md")
    zh_path = os.path.join("content", "zh-tw", "posts", f"{date_str}.md")

    created_files = []
    try:
        # Generate English Daily Highlight
        highlight_en = await generate_daily_highlight(articles)
        if not highlight_en:
            raise RuntimeError("Failed to generate English daily highlight summary.")

        # Translate Daily Highlight to Traditional Chinese (Taiwan)
        highlight_zh = await translate_highlight(highlight_en)
        if not highlight_zh:
            raise RuntimeError("Failed to translate daily highlight summary to Traditional Chinese.")

        # Validate English developer terms in highlight_zh
        _validate_highlight_terms(highlight_en, highlight_zh)

        # Build English article summaries list for frontmatter
        en_articles_frontmatter = []
        for art in articles:
            summary = art.get("summary")
            if not summary or not isinstance(summary, dict):
                raise ValueError(f"Article {art.get('url')} is missing English summary.")
            en_articles_frontmatter.append({
                "title": art.get("title", "Untitled"),
                "author": art.get("author", "Unknown"),
                "url": art.get("url", ""),
                "publication_date": art.get("publication_date", date_str),
                "tldr": summary.get("tldr") or "",
                "problem_why": summary.get("problem_why") or "",
                "solution_how": summary.get("solution_how") or "",
                "insights_tradeoffs": summary.get("insights_tradeoffs") or {"pros": [], "cons": []},
                "tags_action": summary.get("tags_action") or [],
                "rating": summary.get("rating") if summary.get("rating") is not None else 3
            })

        # Build Chinese article summaries list for frontmatter
        zh_articles_frontmatter = []
        for art in articles:
            summary_zh = art.get("summary_zh_tw")
            if not summary_zh or not isinstance(summary_zh, dict):
                raise ValueError(f"Article {art.get('url')} is missing Traditional Chinese summary.")
            zh_articles_frontmatter.append({
                "title": art.get("title", "Untitled"),
                "author": art.get("author", "Unknown"),
                "url": art.get("url", ""),
                "publication_date": art.get("publication_date", date_str),
                "tldr": summary_zh.get("tldr") or "",
                "problem_why": summary_zh.get("problem_why") or "",
                "solution_how": summary_zh.get("solution_how") or "",
                "insights_tradeoffs": summary_zh.get("insights_tradeoffs") or {"pros": [], "cons": []},
                "tags_action": summary_zh.get("tags_action") or [],
                "rating": summary_zh.get("rating") if summary.get("rating") is not None else 3
            })

        # Format frontmatter as YAML block style
        en_frontmatter = {
            "title": date_str,
            "date": date_str,
            "daily_highlight": highlight_en,
            "articles": en_articles_frontmatter
        }
        zh_frontmatter = {
            "title": date_str,
            "date": date_str,
            "daily_highlight": highlight_zh,
            "articles": zh_articles_frontmatter
        }

        # Write to files
        os.makedirs(os.path.dirname(en_path), exist_ok=True)
        os.makedirs(os.path.dirname(zh_path), exist_ok=True)

        en_yaml = yaml.safe_dump(en_frontmatter, default_flow_style=False, allow_unicode=True)
        zh_yaml = yaml.safe_dump(zh_frontmatter, default_flow_style=False, allow_unicode=True)

        with open(en_path, "w", encoding="utf-8") as f:
            f.write(f"---\n{en_yaml}---\n")
        created_files.append(en_path)

        with open(zh_path, "w", encoding="utf-8") as f:
            f.write(f"---\n{zh_yaml}---\n")
        created_files.append(zh_path)

        return True

    except Exception as e:
        # Clean up any created files to prevent partial state
        for path in created_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
        _log_publish_error(str(e))
        raise e
