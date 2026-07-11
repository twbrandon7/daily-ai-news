import asyncio
import datetime
import json
import re
import sys

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

TRANSLATE_PROMPT = """You are a professional technical translator. Translate the given English structured JSON summary into Traditional Chinese (Taiwan).

Strict Guidelines:
1. Translate the values of the fields: "tldr", "problem_why", "solution_how", the list items in "insights_tradeoffs.pros" and "insights_tradeoffs.cons", and the list items in "tags_action".
2. Keep these technical terms in English verbatim (case-insensitive, do not translate them to Chinese): "prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token".
3. Do NOT translate or modify the "rating" field value. Preserve it exactly as an integer.
4. Maintain the exact JSON structure and keys of the input.
5. Return ONLY a valid JSON object wrapped in ```json ... ``` fencing. Do not include any other text outside the fenced block.
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

def _parse_translation(response_text: str, original_summary: dict) -> dict:
    """
    Parse and validate the JSON translation from a model response string.

    Accepts either a ```json ... ``` fenced block or a bare JSON object.
    Returns the parsed dict if all required fields are present and valid,
    otherwise raises ValueError with specific failure details.
    """
    # Find all fenced blocks
    candidates = re.findall(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
    if not candidates:
        candidates = [response_text.strip()]

    data = None
    last_err = None
    for candidate in candidates:
        candidate = candidate.strip()
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                break
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e

    if not isinstance(data, dict):
        if last_err:
            raise ValueError(f"Failed to decode response as JSON dict: {last_err}")
        raise ValueError("Response is not a valid JSON dict.")

    # Check for exact root keys
    expected_root_keys = {"tldr", "problem_why", "solution_how", "insights_tradeoffs", "tags_action", "rating"}
    actual_root_keys = set(data.keys())
    if actual_root_keys != expected_root_keys:
        missing = expected_root_keys - actual_root_keys
        extra = actual_root_keys - expected_root_keys
        raise ValueError(f"Schema mismatch. Missing keys: {missing}, Extra keys: {extra}")

    # Validate required string fields
    required_str_fields = ("tldr", "problem_why", "solution_how")
    for field in required_str_fields:
        value = data[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Field '{field}' must be a non-empty string.")

    # Validate insights_tradeoffs
    it = data["insights_tradeoffs"]
    if not isinstance(it, dict):
        raise ValueError("Field 'insights_tradeoffs' must be a dict.")
    if set(it.keys()) != {"pros", "cons"}:
        raise ValueError("Field 'insights_tradeoffs' must contain exactly 'pros' and 'cons'.")
    if not isinstance(it.get("pros"), list) or not isinstance(it.get("cons"), list):
        raise ValueError("'pros' and 'cons' must be lists.")
    if any(not isinstance(x, str) for x in it["pros"] + it["cons"]):
        raise ValueError("All items in 'pros' and 'cons' must be strings.")

    # Validate tags_action
    tags = data["tags_action"]
    if not isinstance(tags, list):
        raise ValueError("Field 'tags_action' must be a list.")
    if any(not isinstance(x, str) for x in tags):
        raise ValueError("All items in 'tags_action' must be strings.")

    # Validate rating
    original_rating = original_summary.get("rating")
    rating = data["rating"]
    if isinstance(rating, str) and rating.isdigit():
        rating = int(rating)
    if type(rating) is not int or rating != original_rating:
        raise ValueError(f"Rating mismatch. Expected integer {original_rating}, got {type(rating).__name__} {rating}")

    # Validate key terms are preserved verbatim (case-insensitive)
    TERMS = ["prompt", "fine-tuning", "agent", "RAG", "pipeline", "checkpoint", "embeddings", "token"]
    
    # Check string fields
    for field in required_str_fields:
        orig_val = original_summary.get(field, "")
        trans_val = data[field]
        for term in TERMS:
            if term.lower() in orig_val.lower():
                if term.lower() not in trans_val.lower():
                    raise ValueError(f"Term '{term}' missing in translated field '{field}'")

    # Check insights_tradeoffs
    for key in ("pros", "cons"):
        orig_val = " ".join(original_summary.get("insights_tradeoffs", {}).get(key, []))
        trans_val = " ".join(data["insights_tradeoffs"][key])
        for term in TERMS:
            if term.lower() in orig_val.lower():
                if term.lower() not in trans_val.lower():
                    raise ValueError(f"Term '{term}' missing in translated insights_tradeoffs.{key}")

    # Check tags_action
    orig_tags = " ".join(original_summary.get("tags_action", []))
    trans_tags = " ".join(data["tags_action"])
    for term in TERMS:
        if term.lower() in orig_tags.lower():
            if term.lower() not in trans_tags.lower():
                raise ValueError(f"Term '{term}' missing in translated tags_action")

    return data

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
            model="gemini-2.0-flash",
            name="translator",
            instruction=TRANSLATE_PROMPT,
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

    except asyncio.TimeoutError:
        _log_translate_error(url, "API call timed out after 30.0 seconds.")
        return None
    except Exception as exc:
        _log_translate_error(url, f"ADK/API error: {exc}")
        return None

    if response_text is None:
        _log_translate_error(url, "No final response received from model.")
        return None

    try:
        parsed = _parse_translation(response_text, summary)
    except ValueError as err:
        _log_translate_error(
            url,
            f"Validation/Parsing error: {err}. Response: {response_text[:200]}"
        )
        return None

    return parsed
