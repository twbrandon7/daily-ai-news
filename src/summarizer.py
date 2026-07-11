import asyncio
import datetime
import json
import re
import sys

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

SUMMARIZE_PROMPT = """You are a technical article summarizer. Given an article's title and body text, produce a structured JSON summary in English.

Return ONLY a JSON object with exactly these fields (no extra commentary, no markdown prose around it):

{
  "tldr": "<one-sentence summary of the article>",
  "problem_why": "<what problem does this article address and why it matters>",
  "solution_how": "<how the article solves the problem or what approach is described>",
  "insights_tradeoffs": {
    "pros": ["<key advantage 1>", "<key advantage 2>"],
    "cons": ["<key drawback or limitation 1>"]
  },
  "tags_action": ["<relevant tag 1>", "<relevant tag 2>", "<relevant tag 3>"],
  "rating": <integer from 1 to 5 representing the article's technical depth and usefulness>
}

Wrap the JSON in ```json ... ``` fencing. Do not include any other text outside the fenced block.
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


def _parse_summary(response_text: str) -> dict | None:
    """
    Parse the JSON summary from a model response string.

    Accepts either a ```json ... ``` fenced block or a bare JSON object.
    Returns the parsed dict if all required fields are present and valid, else None.
    """
    # Try to extract from ```json ... ``` fencing first
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidate = fenced.group(1).strip()
    else:
        # Fall back to the whole response text
        candidate = response_text.strip()

    try:
        data = json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        return None

    # Validate required fields and types
    if not isinstance(data, dict):
        return None

    required_str_fields = ("tldr", "problem_why", "solution_how")
    for field in required_str_fields:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            return None

    it = data.get("insights_tradeoffs")
    if not isinstance(it, dict):
        return None
    if not isinstance(it.get("pros"), list) or not isinstance(it.get("cons"), list):
        return None
    if any(not isinstance(x, str) for x in it.get("pros", []) + it.get("cons", [])):
        return None

    tags = data.get("tags_action")
    if not isinstance(tags, list):
        return None
    if any(not isinstance(x, str) for x in tags):
        return None

    rating = data.get("rating")
    if type(rating) is not int or not (1 <= rating <= 5):
        return None

    return data


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
            model="gemini-2.0-flash",
            name="summarizer",
            instruction=SUMMARIZE_PROMPT,
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

    except Exception as exc:
        _log_summarize_error(url or title, f"ADK/API error: {exc}")
        return None

    if response_text is None:
        _log_summarize_error(url or title, "No final response received from model.")
        return None

    parsed = _parse_summary(response_text)
    if parsed is None:
        _log_summarize_error(
            url or title,
            f"Failed to parse summary JSON from model response: {response_text[:200]}",
        )
        return None

    return parsed
