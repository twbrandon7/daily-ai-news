---
title: 'Fix Gemini Model Deprecation'
type: 'bugfix'
created: '2026-07-25T14:06:00+08:00'
status: 'done'
route: 'one-shot'
---

# Fix Gemini Model Deprecation

## Intent

**Problem:** Summarization pipeline fails because `models/gemini-2.0-flash` is deprecated, raising a 404 NOT_FOUND error.

**Approach:** Update model references from `gemini-2.0-flash` to `gemini-3.5-flash-lite` across `src/summarizer.py`, `src/publisher.py`, and `src/translator.py`.

## Suggested Review Order

**Model Configuration Update**

- Update model to gemini-3.5-flash-lite in summarizer.
  [`summarizer.py:122`](../../src/summarizer.py#L122)

- Update models and docstrings to gemini-3.5-flash-lite in publisher.
  [`publisher.py:64`](../../src/publisher.py#L64)

- Update model to gemini-3.5-flash-lite in translator.
  [`translator.py:166`](../../src/translator.py#L166)
