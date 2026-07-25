---
title: 'Fix Summarization and Translation Schema'
type: 'bugfix'
created: '2026-07-25T20:54:00Z'
status: 'done'
route: 'one-shot'
---

# Fix Summarization and Translation Schema

## Intent

**Problem:** Pydantic `extra="forbid"` adds `"additionalProperties": false` to JSON schema, which Gemini API rejects with a 400 Bad Request error.

**Approach:** Remove `model_config = ConfigDict(extra="forbid")` and the unused `ConfigDict` import from both summarizer and translator schemas.

## Suggested Review Order

**Schema Fixes**

- Remove Pydantic extra="forbid" from ArticleSummary and InsightsTradeoffs to fix API payload validation error.
  [`summarizer.py:8`](../../src/summarizer.py#L8)

- Remove Pydantic extra="forbid" from TranslationSummary and InsightsTradeoffs to prevent 400 ClientError.
  [`translator.py:8`](../../src/translator.py#L8)
