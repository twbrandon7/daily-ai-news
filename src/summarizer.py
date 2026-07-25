import asyncio
import datetime
import json
import re
import sys

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from pydantic import BaseModel, Field, ConfigDict

class InsightsTradeoffs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pros: list[str] = Field(description="Key advantages or positive aspects.")
    cons: list[str] = Field(description="Key drawbacks, limitations, or negative aspects.")

class ArticleSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tldr: str = Field(description="One-sentence summary of the article.")
    problem_why: str = Field(description="What problem does this article address and why it matters.")
    solution_how: str = Field(description="How the article solves the problem or what approach is described.")
    insights_tradeoffs: InsightsTradeoffs = Field(description="Key advantages and drawbacks.")
    tags_action: list[str] = Field(description="Relevant tags or action items.")
    rating: int = Field(ge=1, le=5, description="Integer from 1 to 5 representing the article's technical depth and usefulness.")

SUMMARIZE_PROMPT = """You are a technical article summarizer. Given an article's title and body text, produce a structured summary in English.

Ensure all fields in the output schema are fully populated based on the article's content.
"""


def _log_summarize_error(url: str, error_message: str) -> None:
    """Log a structured JSON error entry to stderr for summarization failures."""
    log_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "stage": "summarize",
        "blog_url": url,
        "error_message": error_message,
    }
    print(json.dumps(log_data), file=sys.stderr)


async def summarize_article(url: str, body: str, title: str) -> dict | None:
    """
    Summarize an article using Google ADK + Gemini.

    Parameters
    ----------
    url : str
        The article URL (used as identifier in error logs).
    body : str
        The main text body of the article.
    title : str
        The article title.

    Returns
    -------
    dict | None
        A dict with keys ``tldr``, ``problem_why``, ``solution_how``,
        ``insights_tradeoffs``, ``tags_action``, and ``rating``, or ``None``
        on any failure.
    """
    if not body or not body.strip():
        _log_summarize_error(url or title, "Empty article body; skipping summarization.")
        return None

    user_message_text = f"Title: {title}\n\nBody:\n{body}"

    try:
        agent = LlmAgent(
            model="gemini-3.5-flash-lite",
            name="summarizer",
            instruction=SUMMARIZE_PROMPT,
            output_schema=ArticleSummary,
            output_key="summary",
        )
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name="summarizer",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="summarizer",
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

        # Retrieve structured output from session state
        updated_session = await session_service.get_session(
            app_name="summarizer",
            user_id="pipeline",
            session_id=session.id,
        )
        parsed = updated_session.state.get("summary")

    except Exception as exc:
        _log_summarize_error(url or title, f"ADK/API error: {exc}")
        return None

    if parsed is None:
        _log_summarize_error(
            url or title,
            f"Failed to parse summary JSON from model response: {response_text[:200] if response_text else 'No response'}",
        )
        return None

    return parsed

