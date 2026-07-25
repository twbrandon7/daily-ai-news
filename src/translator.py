import asyncio
import datetime
import json
import re
import sys

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from pydantic import BaseModel, Field

class InsightsTradeoffs(BaseModel):
    pros: list[str] = Field(description="Key advantages or positive aspects.")
    cons: list[str] = Field(description="Key drawbacks, limitations, or negative aspects.")

class TranslationSummary(BaseModel):
    tldr: str = Field(description="One-sentence summary of the article.")
    problem_why: str = Field(description="What problem does this article address and why it matters.")
    solution_how: str = Field(description="How the article solves the problem or what approach is described.")
    insights_tradeoffs: InsightsTradeoffs = Field(description="Key advantages and drawbacks.")
    tags_action: list[str] = Field(description="Relevant tags or action items.")
    rating: int = Field(ge=1, le=5, description="Integer from 1 to 5 representing the article's technical depth and usefulness.")

TRANSLATE_PROMPT = """You are a professional technical translator. Translate the given English structured JSON summary into Traditional Chinese (Taiwan).

Strict Guidelines:
1. Translate the values of the fields: "tldr", "problem_why", "solution_how", the list items in "insights_tradeoffs.pros" and "insights_tradeoffs.cons", and the list items in "tags_action".
2. Keep these technical terms in English verbatim (case-insensitive, do not translate them to Chinese): "prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token".
3. Do NOT translate or modify the "rating" field value. Preserve it exactly as an integer.
4. Maintain the exact structure of the input.
"""

def _log_translate_error(url: str, error_message: str) -> None:
    """Log a structured JSON error entry to stderr for translation failures."""
    log_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stage": "translate",
        "blog_url": url,
        "error_message": error_message,
    }
    print(json.dumps(log_data), file=sys.stderr)

def _contains_term(term: str, text: str) -> bool:
    """Check if term (or common plural/singular variant) exists as a whole word in text."""
    if term.lower() == "embeddings":
        pattern = r"\bembedding[s]?\b"
    else:
        pattern = rf"\b{re.escape(term)}[s]?\b"
    return bool(re.search(pattern, text, flags=re.ASCII | re.IGNORECASE))

def _validate_translation_constraints(data: dict, original_summary: dict) -> None:
    """
    Validate dynamic translation constraints that cannot be validated statically by Pydantic.
    Raises ValueError with details on failure.
    """
    # Validate rating matches original summary
    original_rating = original_summary.get("rating")
    rating = data.get("rating")
    if isinstance(rating, str) and rating.isdigit():
        rating = int(rating)
    if type(rating) is not int or rating != original_rating:
        raise ValueError(f"Rating mismatch. Expected integer {original_rating}, got {type(rating).__name__} {rating}")

    # Validate key terms are preserved verbatim (case-insensitive)
    TERMS = ["prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token"]
    required_str_fields = ("tldr", "problem_why", "solution_how")
    
    # Check string fields
    for field in required_str_fields:
        orig_val = original_summary.get(field, "")
        trans_val = data.get(field, "")
        for term in TERMS:
            if _contains_term(term, orig_val):
                if not _contains_term(term, trans_val):
                    raise ValueError(f"Term '{term}' missing in translated field '{field}'")

    # Check insights_tradeoffs
    for key in ("pros", "cons"):
        orig_val = " ".join(original_summary.get("insights_tradeoffs", {}).get(key, []))
        trans_val = " ".join(data.get("insights_tradeoffs", {}).get(key, []))
        for term in TERMS:
            if _contains_term(term, orig_val):
                if not _contains_term(term, trans_val):
                    raise ValueError(f"Term '{term}' missing in translated insights_tradeoffs.{key}")

    # Check tags_action
    orig_tags = " ".join(original_summary.get("tags_action", []))
    trans_tags = " ".join(data.get("tags_action", []))
    for term in TERMS:
        if _contains_term(term, orig_tags):
            if not _contains_term(term, trans_tags):
                raise ValueError(f"Term '{term}' missing in translated tags_action")


async def translate_summary(url: str, summary: dict) -> dict | None:
    """
    Translate an English summary into Traditional Chinese (Taiwan) using Google ADK + Gemini.

    Parameters
    ----------
    url : str
        The article URL (used as identifier in error logs).
    summary : dict
        The English structured summary dict.

    Returns
    -------
    dict | None
        The translated summary dict, or None on failure.
    """
    if not summary or not isinstance(summary, dict):
        _log_translate_error(url, "Invalid or empty summary dict for translation.")
        return None

    original_rating = summary.get("rating")
    if type(original_rating) is not int:
        _log_translate_error(url, "Original summary is missing a valid integer rating.")
        return None

    try:
        user_message_text = json.dumps(summary, indent=2)
    except (TypeError, ValueError) as err:
        _log_translate_error(url, f"Serialization error: {err}")
        return None

    try:
        agent = LlmAgent(
            model="gemini-3.5-flash-lite",
            name="translator",
            instruction=TRANSLATE_PROMPT,
            output_schema=TranslationSummary,
            output_key="translation",
        )
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name="translator",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="translator",
            user_id="pipeline",
        )

        new_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=user_message_text)],
        )

        response_text = None

        async def run_with_timeout():
            nonlocal response_text
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

        await asyncio.wait_for(run_with_timeout(), timeout=30.0)

        # Retrieve structured output from session state
        updated_session = await session_service.get_session(
            app_name="translator",
            user_id="pipeline",
            session_id=session.id,
        )
        parsed = updated_session.state.get("translation")

        if parsed is not None:
            _validate_translation_constraints(parsed, summary)

    except asyncio.TimeoutError:
        _log_translate_error(url, "API call timed out after 30.0 seconds.")
        return None
    except Exception as exc:
        _log_translate_error(url, f"ADK/API/Validation error: {exc}")
        return None

    if parsed is None:
        _log_translate_error(url, "No final response received from model.")
        return None

    return parsed

