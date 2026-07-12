---
baseline_commit: 848acd9
---
# Story 2.1: Hugo Multilingual Setup & Configuration Research

Status: done

<!-- Note: Validate with checklist before running dev-story if quality assurance is required. -->

## Story

As a developer,
I want to research and configure the Hugo site for English and Traditional Chinese multilingual routing,
So that content is properly organized under `/en/` and `/zh-tw/` without external themes.

## Acceptance Criteria

1. **Given** a `hugo.toml` file configured with English and Traditional Chinese (`zh-tw`) languages
2. **When** the Hugo site builds
3. **Then** English post files build under `/en/posts/` and Traditional Chinese posts under `/zh-tw/posts/`
4. **And** no third-party themes are imported in the configuration.

## Tasks / Subtasks

- [x] Task 1: Install Hugo and verify version (AC: prerequisite)
  - [x] Install Hugo 0.120+ (extended version recommended for SCSS support, though not required here).
  - [x] Verify `hugo version` outputs 0.120+.
  - [x] Confirm Hugo is available in the GitHub Actions runner environment (will be used in Story 1.6 workflow).

- [x] Task 2: Create `hugo.toml` with multilingual configuration (AC: #1, #3, #4)
  - [x] Create `hugo.toml` at the project root (NOT inside any subdirectory).
  - [x] Set `baseURL`, `defaultContentLanguage = "en"`, and `defaultContentLanguageInSubdir = true`.
  - [x] Define `[languages.en]` with `contentDir = "content/en"`, `weight = 1`, `languageCode = "en-US"`, `languageName = "English"`.
  - [x] Define `[languages.zh-tw]` with `contentDir = "content/zh-tw"`, `weight = 2`, `languageCode = "zh-TW"`, `languageName = "繁體中文"`, `hasCJKLanguage = true`.
  - [x] Set `hasCJKLanguage = true` at global level for CJK tokenization.
  - [x] Set `theme = ""` (empty) — do NOT reference any theme directory (enforces AD-5).

- [x] Task 3: Create the content directory skeleton (AC: #3)
  - [x] Create `content/en/posts/` directory with a `.gitkeep` file or placeholder `_index.md`.
  - [x] Create `content/zh-tw/posts/` directory with a `.gitkeep` file or placeholder `_index.md`.
  - [x] Create `content/en/_index.md` with basic frontmatter (`title: "Daily AI News"`, `layout: "home"`).
  - [x] Create `content/zh-tw/_index.md` with basic frontmatter (`title: "每日 AI 新聞"`, `layout: "home"`).

- [x] Task 4: Create stub layout files (AC: #4, prerequisite for later stories)
  - [x] Create `layouts/` directory.
  - [x] Create `layouts/_default/baseof.html` — minimal valid base template with `{{ block "main" . }}{{ end }}`.
  - [x] Create `layouts/_default/single.html` — stub extending baseof.
  - [x] Create `layouts/_default/list.html` — stub extending baseof.
  - [x] Create `layouts/index.html` — stub for homepage, extending baseof.
  - [x] Create `static/css/` and `static/js/` directories (empty, with `.gitkeep`) to establish the structure expected by later stories.

- [x] Task 5: Add a sample daily post file for both languages (AC: #3)
  - [x] Create `content/en/posts/2026-07-12.md` with valid frontmatter (title, date, `articles: []` key — empty array as placeholder).
  - [x] Create `content/zh-tw/posts/2026-07-12.md` with the same structure.
  - [x] These files validate the routing but are clearly marked as placeholders. They may be deleted or overwritten by the pipeline.

- [x] Task 6: Build verification (AC: #1, #2, #3, #4)
  - [x] Run `hugo build` (or `hugo --minify`) from the project root.
  - [x] Confirm output in `public/en/posts/2026-07-12/index.html` exists.
  - [x] Confirm output in `public/zh-tw/posts/2026-07-12/index.html` exists.
  - [x] Confirm no theme-related errors in the build log.
  - [x] Confirm `public/en/` and `public/zh-tw/` subdirectories are present (proving `defaultContentLanguageInSubdir = true` is working).

- [x] Task 7: Add `public/` to `.gitignore` (AC: housekeeping)
  - [x] Ensure `public/` is listed in `.gitignore` so Hugo's build output is not committed.
  - [x] Ensure `resources/_gen/` is also listed (Hugo caches).

## Dev Notes

### Architecture Constraints (MUST follow)

- **AD-5 — Zero-Dependency Custom Hugo Layouts:** The Hugo site MUST be at the **project root** with custom layouts under `layouts/`. No `themes/` directory, no `theme =` reference in `hugo.toml`. Violations here break all downstream layout stories (2.2–2.6).
- **AD-6 — Structured Frontmatter Storage:** Daily post files MUST use the `articles` key in YAML frontmatter. While the sample placeholder files in this story will have `articles: []` (empty), the schema must be established now so the pipeline (Stories 1.5) and layout stories (2.3–2.6) can rely on it.
- **Stack:** Hugo 0.120+ (from ARCHITECTURE-SPINE.md). Python is irrelevant to this story. No `uv` commands needed.

### Hugo Multilingual Configuration Details

#### Correct `hugo.toml` (minimal valid starting point)

```toml
baseURL = "https://YOUR_USERNAME.github.io/daily-ai-news/"
defaultContentLanguage = "en"
defaultContentLanguageInSubdir = true
hasCJKLanguage = true

[languages]
  [languages.en]
    languageName = "English"
    weight = 1
    title = "Daily AI News"
    contentDir = "content/en"
    languageCode = "en-US"

  [languages.zh-tw]
    languageName = "繁體中文"
    weight = 2
    title = "每日 AI 新聞"
    contentDir = "content/zh-tw"
    languageCode = "zh-TW"
    hasCJKLanguage = true

[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
```

Key decisions:
- `defaultContentLanguageInSubdir = true` is **critical** — without it, English would serve at `/` instead of `/en/`, breaking FR-7 routing requirements.
- `baseURL` should point to the GitHub Pages URL. For local dev testing, it can be `http://localhost:1313/`.
- `theme` must NOT be set. Setting `theme = ""` explicitly or omitting it entirely both work. Avoid `theme = "some-theme"` entirely.
- `[markup.goldmark.renderer] unsafe = true` is needed if any layout uses raw HTML in markdown body (likely for split-pane HTML structure).

#### Content Directory Structure (required by AR-6)

```text
content/
  en/
    _index.md            # homepage for /en/ (layout: home)
    posts/
      _index.md          # list page for /en/posts/
      2026-07-12.md      # sample daily post
  zh-tw/
    _index.md            # homepage for /zh-tw/ (layout: home)
    posts/
      _index.md          # list page for /zh-tw/posts/
      2026-07-12.md      # sample daily post
```

#### Frontmatter Schema for Daily Posts (AR-6)

```yaml
---
title: "2026-07-12"
date: 2026-07-12
daily_highlight: ""
articles: []
---
```

The `articles` key is the structured YAML array that the pipeline (Story 1.5) writes and the JS switcher (Story 2.5) reads. Even in the stub file, the key must exist with an empty array `[]` — not omitted.

#### Stub Layout Files (AD-5)

Layouts use Go templates. The minimal required structure for Hugo to build without errors:

**`layouts/_default/baseof.html`:**
```html
<!DOCTYPE html>
<html lang="{{ .Site.Language.Lang }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ .Title }} | {{ .Site.Title }}</title>
  <link rel="stylesheet" href="{{ "css/index.css" | relURL }}">
</head>
<body>
  {{ block "main" . }}{{ end }}
  <script src="{{ "js/main.js" | relURL }}"></script>
</body>
</html>
```

**`layouts/_default/single.html`:**
```html
{{ define "main" }}
  <main>{{ .Content }}</main>
{{ end }}
```

**`layouts/_default/list.html`:**
```html
{{ define "main" }}
  <main>
    {{ range .Pages }}
      <a href="{{ .RelPermalink }}">{{ .Title }}</a>
    {{ end }}
  </main>
{{ end }}
```

**`layouts/index.html`** (homepage at `/en/` or `/zh-tw/`):
```html
{{ define "main" }}
  <main>
    <h1>{{ .Site.Title }}</h1>
    {{ range (where .Site.RegularPages "Type" "posts") }}
      <a href="{{ .RelPermalink }}">{{ .Title }}</a>
    {{ end }}
  </main>
{{ end }}
```

> ⚠️ These are stubs. They will be fully replaced by Stories 2.2 (styling), 2.3 (bento archive), and 2.4 (split-pane). **Do not implement design or interactivity in this story.**

### Language Switcher — Context for Later Stories

The language switcher (FR-7, Story 2.6) will use Hugo's `.Translations` range to link between `/en/` and `/zh-tw/` equivalent pages. This story does NOT implement it, but the multilingual config established here enables it. No action needed now.

The switcher template snippet (for reference/documentation, implement in Story 2.6):
```html
{{ range .Translations }}
  <a href="{{ .RelPermalink }}">{{ .Language.LanguageName }}</a>
{{ end }}
```

### i18n String Files (Optional, deferred)

Hugo i18n files (`i18n/en.toml`, `i18n/zh-tw.toml`) are NOT required for this story. They can be added in Story 2.6 if the language switcher uses localized UI strings like "View Summary" / "查看摘要". Skip for now.

### `.gitignore` Requirements

Ensure these entries exist in `.gitignore`:
```
public/
resources/_gen/
.hugo_build.lock
```

### Hugo Installation for CI (Story 1.6 Reference)

Hugo is not a Python package. In GitHub Actions (Story 1.6 workflow), it must be installed separately:
```yaml
- name: Install Hugo
  uses: peaceiris/actions-hugo@v3
  with:
    hugo-version: '0.120.0'
    extended: false
```
This story does not modify `.github/workflows/pipeline.yml`. That is Story 1.6's concern. However, if `pipeline.yml` already exists (it does, from Story 1.6), confirm the Hugo install step is present — do NOT break that workflow.

### Prior Pipeline Artifacts to NOT Break

Epic 1 is complete. The following files must not be modified by this story:
- `src/pipeline.py`, `src/summarizer.py`, `src/translator.py`, `src/publisher.py`
- `data/blogs.yaml`, `data/fetched_posts.json`
- `.github/workflows/pipeline.yml`
- `pyproject.toml`, `uv.lock`

The `publisher.py` (Story 1.5) writes to `content/en/posts/YYYY-MM-DD.md` and `content/zh-tw/posts/YYYY-MM-DD.md`. This story creates the **directory structure** that `publisher.py` expects. Check `src/publisher.py` to confirm the exact path format used and ensure the created directories match. Do not change `publisher.py`.

### Testing Approach

No automated test framework is expected for this story (Hugo build is the test). Verification is manual:

1. `hugo version` → should be 0.120+
2. `hugo --minify` from project root → exits 0 with no ERRORs or WARNINGs (WARNINGs about missing SCSS are acceptable only if not using extended Hugo)
3. `ls public/en/posts/` → should list `2026-07-12/`
4. `ls public/zh-tw/posts/` → should list `2026-07-12/`
5. `cat public/en/index.html` → should exist and contain rendered content
6. No `themes/` directory should exist in the project.

## References

- [Source: epics.md#Story 2.1](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/epics.md#L172)
- [Source: ARCHITECTURE-SPINE.md#AD-5 — Zero-Dependency Custom Hugo Layouts](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L65)
- [Source: ARCHITECTURE-SPINE.md#AD-6 — Structured Frontmatter Storage](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L73)
- [Source: SOLUTION-DESIGN.md#4. Frontend & Layout Design](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/SOLUTION-DESIGN.md#L73)
- [Source: EXPERIENCE.md#Information Architecture](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/EXPERIENCE.md#L18)
- [Hugo Multilingual Docs](https://gohugo.io/content-management/multilingual/)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4.6

### Debug Log References

- Hugo 0.92.2 available via apt was too old (< 0.120). Manually installed Hugo v0.128.0-extended from GitHub releases to `~/bin/hugo`.
- `layouts/` directory did not exist; created with `mkdir -p`.
- `static/css/` and `static/js/` `.gitkeep` files use comment format `# placeholder`.
- Hugo build produced 11 EN pages and 10 ZH-TW pages with no errors or warnings.
- No `themes/` directory created; `theme` key omitted from `hugo.toml` per AD-5.

### Completion Notes List

- Hugo v0.128.0+extended installed to `~/bin/hugo` (not system-wide; GitHub Actions runner must install via `peaceiris/actions-hugo` as Story 1.6 documents).
- `hugo.toml` created at project root with full multilingual config (en + zh-tw), `defaultContentLanguageInSubdir = true`, `hasCJKLanguage = true`, and goldmark unsafe renderer.
- Content skeleton: `content/en/` and `content/zh-tw/` each have `_index.md` and `posts/_index.md` plus a sample post `2026-07-12.md` with correct AR-6 frontmatter schema (`articles: []`).
- Stub layouts created: `layouts/_default/baseof.html`, `single.html`, `list.html`, and `layouts/index.html` — all are placeholders for Stories 2.2–2.6.
- `static/css/` and `static/js/` directories scaffolded with `.gitkeep`.
- `.gitignore` updated with `public/`, `resources/_gen/`, and `.hugo_build.lock`.
- Verified build outputs: `public/en/posts/2026-07-12/index.html` ✅ and `public/zh-tw/posts/2026-07-12/index.html` ✅.
- Epic 1 files (src/, tests/, .github/workflows/, pyproject.toml, uv.lock, data/) were NOT modified.
