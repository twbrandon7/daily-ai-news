# Epic 1 Context: Daily News Pipeline

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epic 1 delivers the fully automated content pipeline behind the site: it crawls configured AI blogs, skips already-processed articles, generates structured English technical summaries, translates them into Traditional Chinese while preserving standard developer terminology, writes daily bilingual content files, and runs on a daily GitHub Actions schedule so the site can update without manual work.

## Stories

- Story 1.1: Local Blog Scraper & Parser
- Story 1.2: Deduplication Store
- Story 1.3: Gemini-powered Structured Technical Summarization
- Story 1.4: Localization & Translation
- Story 1.5: Content Publishing & Static File Writing
- Story 1.6: Daily pipeline schedule & deployment workflow automation

## Requirements & Constraints

The pipeline must read target blogs from a YAML registry and use crawl4AI to extract title, publication date, author, and clean article body text while excluding boilerplate such as headers, footers, and sidebars. Every crawled URL must be checked against the committed deduplication store before summarization; known URLs are skipped and logged, and new URLs are only recorded after successful downstream processing. New articles must be summarized into a fixed 5-part English structure consisting of TL;DR, Problem/Why, Solution/How, Insights & Trade-offs, and Tags & Action, plus a 1–5 star rating based on technical depth and actionability. Each English summary must then be translated into Traditional Chinese with the same structure preserved exactly, while terms such as prompt, fine-tuning, agent, RAG, pipeline, checkpoint, embeddings, and token remain in English.

Published output must create paired daily files for English and Traditional Chinese and store article data under the `articles` frontmatter key so the static site can consume it. The daily run must also produce a short day-level highlight summary from the compiled article set. Automation must run on GitHub Actions every day at 23:00 UTC (7:00 AM UTC+8), install and execute the pipeline with `uv`, commit generated markdown/JSON content plus deduplication updates only on success, and avoid both commit and deploy when the run fails. The system is expected to run fully unattended, process at least 90% of configured blogs without layout failures, and emit structured JSON error logs with timestamp, stage, blog URL, and error message.

## Technical Decisions

The architecture is a pipes-and-filters workflow with strict sequential stage boundaries: crawl, deduplicate, summarize, translate, then publish/build. Orchestration is centralized in a single Python entrypoint at `src/pipeline.py`, which runs via `uv run` and delegates work to modular code under `src/` rather than separate ad hoc scripts. Persistent pipeline state is intentionally minimal and file-based: blog inputs come from `data/blogs.yaml`, and processed article tracking lives in `data/fetched_posts.json`.

Summarization and translation are separate AI steps rather than a combined prompt. English summaries are generated first through Gemini via Google ADK, then translated to Traditional Chinese in a second pass to preserve structure and terminology control. Publishing writes bilingual daily markdown files at `content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md` with structured YAML frontmatter for downstream site rendering. Fault tolerance is required: a single crawl or summarization failure must be logged and reported without stopping the rest of the day’s run.

## UX & Interaction Patterns

Although this epic is backend-focused, its outputs are reader-facing content and must support a concise, professional technical reading experience. Generated summaries should optimize for fast scanning by engineers, preserve the fixed section structure across languages, and keep core English AI/developer terms untranslated in Traditional Chinese to avoid awkward or non-standard localization.

## Cross-Story Dependencies

Story 1.2 depends on the crawler output from Story 1.1. Story 1.3 depends on clean extracted article content and must complete before Story 1.4 can translate anything. Story 1.5 depends on completed English and Traditional Chinese summaries, plus the deduplication decision about which articles are new. Story 1.6 depends on the end-to-end pipeline being runnable in its final paths and formats so scheduled automation can execute, commit, and deploy reliably.
