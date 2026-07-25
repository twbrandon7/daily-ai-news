---
title: 'Fix Translation Term Validation Substring Bug'
type: 'bugfix'
created: '2026-07-25'
status: 'done'
route: 'one-shot'
---

# Fix Translation Term Validation Substring Bug

## Intent

**Problem:** Translation validation in `src/translator.py` used crude substring matching (`term.lower() in orig_val.lower()`), causing words like "coverage" or "fragment" to falsely trigger a requirement for "RAG" in translated fields.

**Approach:** Added `_contains_term()` helper using ASCII word-boundary regex (`\b{term}[s]?\b`) to ensure terms are matched as whole words rather than substrings.

## Suggested Review Order

1. [src/translator.py](file:///home/clx/projects/daily-ai-news/src/translator.py#L32-L132) -- `_contains_term` helper and word boundary term checking in `_parse_translation`
2. [tests/test_translator.py](file:///home/clx/projects/daily-ai-news/tests/test_translator.py#L288-L313) -- Unit test covering non-matching of substring occurrences like "coverage"
