---
title: 'Add Polish/Refinement Sub-Step to Translation'
type: 'feature'
created: '2026-07-25T21:05:00+08:00'
status: 'done'
baseline_commit: '6a1665b32d4f6822d920e9d1c9c414559c219928'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Literal English-to-Traditional-Chinese translations can be rigid, contain English-style long sentence structures, and lack terminology formatting (e.g., missing original English jargon in parentheses or over-translating tech terms like Agent).

**Approach:** Add a second refinement agent pass in `src/translator.py` using `gemini-3.5-flash-lite` that receives the initial translation and applies Chinese technical translation polishing rules (breaking long sentences, fixing verb-object collocations, formatting specialized jargon with original English in parentheses, preserving tech terms), while validating constraints on the final result.

## Boundaries & Constraints

**Always:**
- Keep `rating` integer intact across initial translation and refinement steps.
- Retain exact terms intact (`prompt`, `fine-tuning`, `agent`, `RAG`, `pipeline`, `checkpoint`, `embeddings`, `token`).
- Format specialized jargon as `Chinese (English Jargon)` when applicable.
- Pass existing unit tests and add unit test coverage for the refinement sub-step.

**Ask First:**
- Modifying `TranslationSummary` Pydantic model structure.

**Never:**
- Force translate tech terms like `Agent` into `代理`.
- Skip constraint validation on final output.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Refined Translation Success | English summary dict | Polished Traditional Chinese summary dict with broken long sentences, proper collocations, and jargon parenthetical formatting | Return None if refinement fails or times out, fallback gracefully |
| Term Preserved in Refinement | English summary with terms like `agent`, `fine-tuning` | Refined Chinese summary preserves all specified verbatim terms | Validation raises error and logs error entry |

</frozen-after-approval>

## Code Map

- `src/translator.py` -- Add `REFINE_PROMPT` instructions and chain the translation refinement sub-step in `translate_summary`.
- `tests/test_translator.py` -- Update test mocks and add unit tests verifying refinement sub-step behavior.

## Tasks & Acceptance

**Execution:**
- [x] `src/translator.py` -- Add `REFINE_PROMPT` and implement refinement LLM sub-step in `translate_summary`.
- [x] `tests/test_translator.py` -- Update existing translation tests for 2-step agent execution and add tests for translation refinement.

**Acceptance Criteria:**
- Given an English summary dict, when `translate_summary` is invoked, then both translation and refinement sub-steps run and return a polished Traditional Chinese summary.
- Given a successful translation, when dynamic constraint validation runs on the refined result, then terms and rating rules pass.

## Design Notes

Refinement Prompt Guidelines:
1. Break long sentences into 2-3 shorter clauses to eliminate rigid English structures.
2. Fix verb-object collocations.
3. Keep original English term in parentheses for specialized jargon (e.g. `模型蒸餾 (Model Distillation)`).
4. Do not over-translate accepted tech terms (e.g. `Agent`, `Prompt`, `RAG`, `Pipeline`, `Checkpoint`, `Embeddings`, `Token`, `Fine-tuning`).
5. Preserve JSON structure and `rating` integer exactly.

## Verification

**Commands:**
- `.venv/bin/pytest tests/test_translator.py` -- expected: PASS

## Suggested Review Order

**Translation Refinement Implementation**

- Added REFINE_PROMPT containing technical Chinese editing guidelines
  [`translator.py:34`](../../src/translator.py#L34)

- Chained second LlmAgent pass (refiner) to polish initial translation output
  [`translator.py:179`](../../src/translator.py#L179)

**Peripherals**

- Added unit test for translation refinement sub-step
  [`test_translator.py:327`](../../tests/test_translator.py#L327)

