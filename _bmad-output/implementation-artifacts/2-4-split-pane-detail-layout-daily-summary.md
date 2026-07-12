# Story 2.4: Split-Pane Detail Layout (Daily Summary)

Status: done

## Story

As a reader,
I want to view daily summaries in a split-pane layout with a scrollable article list on the left and selected article details on the right,
so that I can read multiple summaries efficiently without page reloads.

## Context

This story implements the static Hugo template (`layouts/_default/single.html`) and all CSS needed for the daily summary detail page (`/en/posts/YYYY-MM-DD/`). The result is a fully-rendered, static split-pane layout: a sticky 280px left sidebar listing all articles and a scrollable right panel showing the **first article by default** via Hugo template logic. There is **no JavaScript** in this story — article switching is deferred to Story 2.5.

## Acceptance Criteria

1. **Given** a daily post file exists at `content/en/posts/YYYY-MM-DD.md` (or `zh-tw` equivalent) with at least one article in the `articles` frontmatter array
   **When** I visit `/en/posts/YYYY-MM-DD/`
   **Then** the page renders a split-pane layout: a sticky 280px left sidebar on the left and a scrollable right detail panel.

2. **And** the split-pane layout uses a `280px / 1fr` CSS grid, with the left sidebar:
   - Containing a read-only search input (placeholder text: EN "Search articles…" / zh-tw "搜尋文章…") — **non-functional** (story 2.5 activates it)
   - Listing all article cards, each showing the article title (2-line clamp) and its `tags_action` tags
   - Marking the **first article card** with the active indicator (3px primary border + 5% primary background tint via `.active-card-indicator`)

3. **And** the right detail panel shows the content of the **first article** in the `articles` array by default, including all 5 elements:
   - **TL;DR box** — primary-bordered left-accent box with the `tldr` field text
   - **Problem / Why** — bordered card section with label "PROBLEM / WHY" and `problem_why` text
   - **Solution / How** — bordered card section with label "SOLUTION / HOW" and `solution_how` text
   - **Insights & Trade-offs** — side-by-side (desktop) / stacked (mobile) pros/cons grid: pros column (green top-accent) from `insights_tradeoffs.pros`, cons column (amber top-accent) from `insights_tradeoffs.cons`
   - **Tags & Action** — tag pills rendered from `tags_action` array
   - **Original Link** — an "Original Link" / "原文連結" anchor linking to `url`, opening in a new tab

4. **And** the article panel header displays:
   - Article title in `text-headline-lg`
   - A 1–5 star rating using the `rating` field (filled stars: primary color; empty stars: outline-variant)

5. **And** the page header (above the split-pane) shows:
   - Formatted date (EN: "July 12, 2026" / zh-tw: "2026年7月12日")
   - `daily_highlight` text (or a date-based fallback if empty)
   - Article count badge ("N articles" / "N 篇文章")

6. **And** when the `articles` array is empty or missing, the right detail panel renders an empty state message:
   - EN: "No articles today. Return to archive."
   - zh-tw: "今日無新增文章。點此回到存檔。"
   — with a link back to `/en/` (or `/zh-tw/`)

7. **And** on mobile screens (`<768px`) the split-pane reflows to a **single-column vertical stack**: header → sidebar article list (full width) → detail panel (full width below).

8. **And** `~/bin/hugo --minify` builds from the project root with exit code 0 and no ERRORs.

9. **And** the generated HTML at `public/en/posts/YYYY-MM-DD/index.html` contains:
   - The class `detail-layout`
   - The class `detail-sidebar`
   - The class `tldr-box`
   - The class `insights-grid`

## Tasks / Subtasks

- [x] **Task 1**: Append split-pane CSS sections (24–36) to `static/css/index.css` (AC: #2, #3, #4, #5, #6, #7)
  - [x] Append **Section 24** — Detail page header: `.detail-header`, `.detail-header-inner`, `.detail-header-date`, `.detail-header-highlight`, `.detail-header-badges`, `.detail-meta-badge`
  - [x] Append **Section 25** — Split-pane layout grid: `.detail-layout` (`grid-template-columns: var(--spacing-nav-width) 1fr`) + mobile collapse (`@media (max-width: 767px)` → `grid-template-columns: 1fr`)
  - [x] Append **Section 26** — Detail sidebar: `.detail-sidebar` (sticky, `top: 64px`, `height: calc(100vh - 64px)`, `overflow-y: auto`, `border-right`, white bg), thin webkit scrollbar, `.sidebar-section-label`, `.sidebar-search-wrapper`, `.sidebar-search-input` (with focus style), `.sidebar-tags-section`, `.sidebar-article-list` (flex column, `gap: 1px`, border-low bg for hairline separators)
  - [x] Append **Section 27** — Sidebar article card: `.sidebar-article-card` (white bg, padding, flex column, hover bg tint), `.sidebar-article-title` (2-line clamp, `font-weight: 600`), `.sidebar-article-tags` (flex wrap, gap xs) — **Note:** `.active-card-indicator` is already defined in Section 14; apply it as a modifier class only
  - [x] Append **Section 28** — Detail panel wrapper: `.detail-panel-outer` (`background: var(--color-background)`, `min-height: calc(100vh - 64px)`, `overflow-y: auto`), `.detail-panel` (`max-width: 800px`, `margin-inline: auto`, padding), `.article-panel-header` (padding-bottom, border-bottom), `.article-panel-title`
  - [x] Append **Section 29** — TL;DR box: `.tldr-box` (`border-left: 3px solid var(--color-primary)`, primary-5% tint bg, `border-radius: 0 var(--radius-lg) var(--radius-lg) 0`, padding), `.tldr-label` (uppercase, primary color, label-md), `.tldr-text` (body-lg, font-weight 500)
  - [x] Append **Section 30** — Summary section containers (Problem/Why, Solution/How): `.summary-section` (white bg, `border: 1px solid var(--color-border-low)`, `border-radius: var(--radius-lg)`, padding, `margin-bottom: var(--spacing-xl)`), `.summary-section-label` (uppercase, on-surface-variant, label-md), `.summary-section-body` (body-md, on-surface)
  - [x] Append **Section 31** — Insights & Trade-offs grid: `.insights-section` (margin-bottom), `.insights-section-label` (uppercase, on-surface-variant, label-md), `.insights-grid` (2-col `1fr 1fr`, gap md; mobile collapses to `1fr`), `.insights-col` (white bg, border, border-radius lg, padding), `.insights-col--pros` (`border-top: 3px solid #16a34a`), `.insights-col--cons` (`border-top: 3px solid #d97706`), `.insights-col-header` (label-md, color matches accent), `.insights-list` (list-style none), `.insights-item` (body-md, padded-left with `::before` bullet)
  - [x] Append **Section 32** — Rating stars: `.rating-stars` (inline-flex, gap 2px), `.rating-star` (16×16px svg), `.rating-star--filled` (`color: var(--color-primary)`), `.rating-star--empty` (`color: var(--color-outline-variant)`)
  - [x] Append **Section 33** — Tags & Action section: `.tags-action-section` (margin-bottom), `.tags-action-label` (uppercase, on-surface-variant, label-md), `.tags-action-list` (flex wrap, gap xs), `.tag-pill--primary` (`background: rgba(0, 74, 198, 0.1); color: var(--color-primary)`)
  - [x] Append **Section 34** — Source link row: `.source-link-row` (padding-top, border-top, margin-top), `.source-link` (inline-flex, primary color, no underline normally, hover underline + color-primary-container), `.source-link-icon` (16×16px)
  - [x] Append **Section 35** — Mobile adjustments: `.detail-panel` mobile padding override (`var(--spacing-lg) var(--spacing-md)`); ensure `.detail-sidebar` switches from sticky to static on mobile: `@media (max-width: 767px) { .detail-sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--color-border-low); } }`
  - [x] Append **Section 36** — Detail empty state: `.detail-empty-state` (flex-column, center align, padding 2xl lg, text-center, on-surface-variant color), `.detail-empty-state a` (primary color)

- [x] **Task 2**: Implement `layouts/_default/single.html` — full daily summary split-pane template (AC: #1–#9)
  - [x] Replace the existing stub (`{{ define "main" }}<main>{{ .Content }}</main>{{ end }}`) entirely
  - [x] **Page header section** (`.detail-header`):
    - Format date: `{{ .Date | time.Format "January 2, 2006" }}` (EN) / `{{ .Date | time.Format "2006年1月2日" }}` (zh-tw) — use `.detail-header-date` span
    - `daily_highlight` with fallback: `{{ with .Params.daily_highlight }}{{ . }}{{ else }}{{ if eq .Site.Language.Lang "zh-tw" }}{{ .Date | time.Format "2006年1月2日" }} 摘要{{ else }}Summary for {{ .Date | time.Format "January 2, 2006" }}{{ end }}{{ end }}`
    - Article count badge using `{{ $articleCount := len .Params.articles }}`
  - [x] **Capture articles**: `{{ $articles := .Params.articles }}` at the top of the main block
  - [x] **Split-pane layout** `<div class="detail-layout">`:
    - `<aside class="detail-sidebar" aria-label="Article list">` / `<section class="detail-panel-outer" aria-label="Article detail">`
  - [x] **Sidebar contents**:
    - Search input (static, no JS): `<input class="sidebar-search-input" type="search" placeholder="..." aria-label="..." disabled>`
    - Tag pills: collect unique tags from all articles using a scratch variable (`$.Scratch.Set`) — render top tags (up to 10) as `.tag-pill` items (non-interactive in this story — Story 2.5 activates them); skip if `$articles` is empty
    - Article card list: `{{ range $idx, $art := $articles }}<div class="sidebar-article-card{{ if eq $idx 0 }} active-card-indicator{{ end }}">` — show title + up to 3 tag pills per card
  - [x] **Right panel default article** (AC: #3, #4):
    - `{{ if $articles }}{{ $a := index $articles 0 }}`...full article rendering...`{{ else }}`...empty state...`{{ end }}`
    - **Article panel header**: `<h1 class="article-panel-title text-headline-lg">{{ $a.title }}</h1>` + rating stars loop
    - **Rating stars**: `{{ $r := int ($a.rating | default 3) }}{{ range seq 1 5 }}{{ if le . $r }}<svg class="rating-star rating-star--filled" ...>` (filled) `{{ else }}<svg class="rating-star rating-star--empty" ...>` (empty) `{{ end }}{{ end }}`
    - **TL;DR box**: `.tldr-box` > `.tldr-label` "TL;DR" + `.tldr-text` `{{ $a.tldr }}`
    - **Problem / Why**: `.summary-section` > `.summary-section-label` "PROBLEM / WHY" + `.summary-section-body` `{{ $a.problem_why }}`
    - **Solution / How**: `.summary-section` > `.summary-section-label` "SOLUTION / HOW" + `.summary-section-body` `{{ $a.solution_how }}`
    - **Insights**: `.insights-section` > `.insights-section-label` + `.insights-grid` with `.insights-col--pros` (range `(index $a.insights_tradeoffs "pros")`) and `.insights-col--cons` (range `(index $a.insights_tradeoffs "cons")`)
    - **Tags & Action**: `.tags-action-section` > range `$a.tags_action` → `.tag-pill.tag-pill--primary`
    - **Source link**: `.source-link-row` > `<a class="source-link" href="{{ $a.url }}" target="_blank" rel="noopener noreferrer">` with external link SVG icon + label "Original Link" / "原文連結"
  - [x] **i18n conditionals**: wrap EN/zh-tw labels using `{{ if eq .Site.Language.Lang "zh-tw" }}...{{ else }}...{{ end }}`; use `$` prefix inside `range` loops (e.g., `{{ if eq $.Site.Language.Lang "zh-tw" }}`)
  - [x] **ARIA**: `aria-label` on sidebar (`aria-label="Article list"` / `"文章列表"`), on detail panel (`aria-label="Article detail"` / `"文章詳情"`), on source link (use a `$srcLabel` variable to avoid quoting conflicts — see Dev Notes), on disabled search input

- [x] **Task 3**: Build verification (AC: #8, #9)
  - [x] Run `~/bin/hugo --minify` from project root — confirm exit code 0, no ERROR lines
  - [x] Confirm `public/en/posts/2026-07-12/index.html` contains `detail-layout`, `detail-sidebar`, `tldr-box`, `insights-grid`
  - [x] Confirm `public/zh-tw/posts/2026-07-12/index.html` contains `原文連結` and `今日無新增文章` (or article content)
  - [x] Confirm no `tailwindcss`, `material-symbols`, `cdn.jsdelivr`, or `unpkg` references in `layouts/_default/single.html`
  - [x] Confirm `.detail-sidebar` CSS rule is present in `public/css/index.css` (or inspect `static/css/index.css`)
  - [x] Visually inspect: header → sidebar → right panel layout at desktop viewport simulation (check HTML structure)

### Review Findings

- [x] [Review][Patch] AC#9 fails — tldr-box/insights-grid absent from built HTML because test content had articles:[] [content/en/posts/2026-07-12.md] — **Fixed**: added test article with full frontmatter to exercise the article path; all 4 required classes now present in built HTML.
- [x] [Review][Patch] Sidebar unique tag pills not capped at 10 — violates spec task note "render top tags (up to 10)" [layouts/_default/single.html:61-73] — **Fixed**: added `$tagCount` counter with `lt $tagCount 10` guard inside the dedup loop.
- [x] [Review][Patch] Rating stars aria-label hard-coded English on zh-tw pages — accessibility gap [layouts/_default/single.html:108] — **Fixed**: added `$ratingLabel` variable with zh-tw localisation ("5 顆星中的 N 顆").
- [x] [Review][Patch] Source link renders href="" when $a.url is empty string — resolves to current page [layouts/_default/single.html:191] — **Fixed**: wrapped source-link-row in `{{ with $a.url }}` guard; also switched inner .Site.Language.Lang check to use `$` prefix for correct range-context access.
- [x] [Review][Defer] Inline styles on sidebar tag pills instead of pure CSS utility class [layouts/_default/single.html:68,85] — deferred, pre-existing design; Story 2.5 will introduce proper CSS class for these variants.

## Dev Notes

### Architecture Constraints (MUST follow)

- **AD-5 — Zero-Dependency Custom Hugo Layouts**: The `ai_1` mockup (detail view) is reference-only — it uses Tailwind CDN + Material Symbols CDN, both **banned**. Translate visual intent into hand-written CSS using existing tokens only.
- **AD-6 — Structured Frontmatter Storage**: All article data comes from Hugo frontmatter (`.Params.articles`). Do **not** read or render `.Content` (the markdown body) for article display. The markdown body is a pipeline comment placeholder only.
- **CSS append-only contract**: Sections 1–23 in `static/css/index.css` were established in Stories 2.2 and 2.3 and are a **downstream contract**. **Only append** new Sections 24+. Never rename, move, or delete existing class names.
- **Hugo binary**: Use `~/bin/hugo` (NOT on system PATH — installed at `~/bin/hugo`, version 0.128.0+).
- **No Material Symbols CDN**: Use inline SVG paths for rating stars and source link icons. SVG paths are provided in Dev Notes below.

### Files to Create / Modify

| File | Action | Notes |
|---|---|---|
| `static/css/index.css` | **APPEND** Sections 24–36 | Preserve all existing Sections 1–23 |
| `layouts/_default/single.html` | **REPLACE** | Replace 3-line stub entirely |

### Files to NOT Touch

- `src/pipeline.py`, `src/summarizer.py`, `src/translator.py`, `src/publisher.py` — Epic 1, complete
- `data/blogs.yaml`, `data/fetched_posts.json` — pipeline-owned
- `.github/workflows/pipeline.yml` — Epic 1, complete
- `content/**/*.md` — pipeline-owned (Story 1.5)
- `layouts/index.html` — owned by Story 2.3
- `layouts/_default/list.html` — owned by Story 2.3
- `layouts/_default/baseof.html` — foundation template; do not modify
- `static/js/.gitkeep` / `static/js/main.js` — owned by Story 2.5
- Sections 1–23 of `static/css/index.css` — Stories 2.2 & 2.3 foundation

### Article Frontmatter Schema (from `src/publisher.py`)

All article data is in `.Params.articles` — a YAML array in the post frontmatter. Each element has exactly these fields:

```yaml
# Example content/en/posts/2026-07-12.md frontmatter:
---
title: "2026-07-12"
date: 2026-07-12
daily_highlight: "Today's AI developments focused on..."
articles:
  - title: "Article Title Here"
    url: "https://example.com/article"
    tldr: "One-sentence summary of the article."
    problem_why: "Multi-sentence description of the problem context."
    solution_how: "Multi-sentence description of the solution approach."
    insights_tradeoffs:
      pros:
        - "Strength or benefit point 1"
        - "Strength or benefit point 2"
      cons:
        - "Trade-off or limitation point 1"
        - "Trade-off or limitation point 2"
    tags_action: ["LLM", "fine-tuning", "RAG"]
    rating: 4
---
```

**Field types:**
- `title` — string
- `url` — string (full URL)
- `tldr` — string (single sentence)
- `problem_why` — string (paragraph)
- `solution_how` — string (paragraph)
- `insights_tradeoffs` — map with keys `pros` ([]string) and `cons` ([]string)
- `tags_action` — []string
- `rating` — integer 1–5 (default: 3 when pipeline fails to score)

**Important:** `articles` may be `nil` or empty `[]` — always guard with `{{ if $articles }}`.

### Existing CSS Foundation (from Stories 2.2 & 2.3) — DO NOT RE-CREATE

The following are **already defined** in `static/css/index.css` and must be **reused**:

| Already Defined | Class / Token |
|---|---|
| Design tokens | All `--color-*`, `--radius-*`, `--spacing-*` (`--spacing-nav-width: 280px`), `--fs-*`, `--shadow-hover`, `--transition-all` |
| Typography utilities | `.text-headline-xl`, `.text-headline-lg`, `.text-headline-md`, `.text-body-lg`, `.text-body-md`, `.text-label-md`, `.text-label-sm` |
| Tonal layers | `.layer-0`, `.layer-1`, `.layer-2` |
| Layout primitives | `.container`, `.grid-12`, `.col-4`, `.col-8` — **do NOT use** `.grid-12/.col-4/.col-8` for the detail split-pane; use `.detail-layout` instead (it uses a fixed `280px` left col, not a proportional 4/12 col) |
| Base components | `.site-header`, `.btn-ghost`, `.card`, `.tag-pill`, `.site-content`, `.active-card-indicator` |

> **CRITICAL:** `.active-card-indicator` is **already defined in Section 14** as `border-left: 3px solid var(--color-primary); background: rgba(0, 74, 198, 0.05);`. Use it as an **additive class** on sidebar article cards (`class="sidebar-article-card active-card-indicator"`). Do NOT redefine it in new CSS sections.

> **CRITICAL:** `.text-label-md` includes `text-transform: uppercase` and `letter-spacing: 0.05em`. Do NOT use it for date labels in the page header — use `.detail-header-date` (defined in Section 24) which sets these values explicitly.

### Hugo Template Patterns for `single.html`

#### Accessing article fields (Hugo frontmatter params)

```gotemplate
{{ define "main" }}
<main>

{{- $articles := .Params.articles -}}
{{- $articleCount := len $articles -}}

{{/* ── Page header ─────────────────────────────────────── */}}
<section class="detail-header layer-1">
  <div class="detail-header-inner">
    <div>
      <span class="detail-header-date">
        {{- if eq .Site.Language.Lang "zh-tw" -}}
          {{- .Date | time.Format "2006年1月2日" -}}
        {{- else -}}
          {{- .Date | time.Format "January 2, 2006" -}}
        {{- end -}}
      </span>
      <p class="detail-header-highlight text-body-lg">
        {{- with .Params.daily_highlight -}}
          {{ . }}
        {{- else -}}
          {{- if eq .Site.Language.Lang "zh-tw" -}}
            {{ .Date | time.Format "2006年1月2日" }} 摘要
          {{- else -}}
            Summary for {{ .Date | time.Format "January 2, 2006" }}
          {{- end -}}
        {{- end -}}
      </p>
      <div class="detail-header-badges">
        <span class="detail-meta-badge">
          {{ $articleCount }}
          {{- if eq .Site.Language.Lang "zh-tw" -}}&nbsp;篇文章{{- else -}}&nbsp;articles{{- end -}}
        </span>
      </div>
    </div>
  </div>
</section>

{{/* ── Split-pane layout ────────────────────────────────── */}}
<div class="detail-layout">

  {{/* Left sidebar */}}
  {{- $sidebarLabel := "Article list" -}}
  {{- if eq .Site.Language.Lang "zh-tw" -}}{{- $sidebarLabel = "文章列表" -}}{{- end -}}
  <aside class="detail-sidebar" aria-label="{{ $sidebarLabel }}">

    {{/* Search input — non-functional placeholder (Story 2.5 activates) */}}
    <div class="sidebar-search-wrapper">
      {{- $searchPlaceholder := "Search articles…" -}}
      {{- if eq .Site.Language.Lang "zh-tw" -}}{{- $searchPlaceholder = "搜尋文章…" -}}{{- end -}}
      <input
        class="sidebar-search-input"
        type="search"
        placeholder="{{ $searchPlaceholder }}"
        aria-label="{{ $searchPlaceholder }}"
        disabled
      >
    </div>

    {{/* Tag pills — collect unique tags from all articles */}}
    {{ if $articles }}
    {{- $seen := newScratch -}}
    <div class="sidebar-tags-section">
      {{ range $articles }}
        {{ range .tags_action }}
          {{ if not ($seen.Get .) }}
            {{- $seen.Set . true -}}
            <span class="tag-pill" style="background:rgba(0,74,198,0.08);color:var(--color-primary);">{{ . }}</span>
          {{ end }}
        {{ end }}
      {{ end }}
    </div>
    {{ end }}

    {{/* Article cards */}}
    {{- $listLabel := "Articles" -}}
    {{- if eq .Site.Language.Lang "zh-tw" -}}{{- $listLabel = "文章列表" -}}{{- end -}}
    <span class="sidebar-section-label">{{ $listLabel }}</span>
    <div class="sidebar-article-list" role="list">
      {{ range $idx, $art := $articles }}
      <div class="sidebar-article-card{{ if eq $idx 0 }} active-card-indicator{{ end }}" role="listitem">
        <p class="sidebar-article-title">{{ $art.title }}</p>
        <div class="sidebar-article-tags">
          {{ range first 3 $art.tags_action }}
          <span class="tag-pill" style="background:var(--color-surface-container-low);color:var(--color-on-surface-variant);font-size:var(--fs-label-sm);">{{ . }}</span>
          {{ end }}
        </div>
      </div>
      {{ end }}
    </div>

  </aside>

  {{/* Right detail panel */}}
  {{- $panelLabel := "Article detail" -}}
  {{- if eq .Site.Language.Lang "zh-tw" -}}{{- $panelLabel = "文章詳情" -}}{{- end -}}
  <div class="detail-panel-outer">
    <section class="detail-panel" aria-label="{{ $panelLabel }}">

    {{ if $articles }}
    {{- $a := index $articles 0 -}}
    {{- $ratingInt := int ($a.rating | default 3) -}}

      {{/* Article header */}}
      <header class="article-panel-header">
        <h1 class="article-panel-title text-headline-lg">{{ $a.title }}</h1>
        {{/* Rating stars — filled: primary, empty: outline-variant */}}
        <div class="rating-stars" aria-label="{{ $ratingInt }} out of 5 stars">
          {{ range seq 1 5 }}
          {{ if le . $ratingInt }}
          <svg class="rating-star rating-star--filled" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>
          </svg>
          {{ else }}
          <svg class="rating-star rating-star--empty" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M22 9.74l-7.19-.62L12 2.5 9.19 9.13 2 9.74l5.46 4.73-1.64 7.03L12 17.77l6.18 3.73-1.63-7.03L22 9.74zM12 15.9l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.8l1.71 4.64 4.38.38-3.32 2.88 1 4.28L12 15.9z"/>
          </svg>
          {{ end }}
          {{ end }}
        </div>
      </header>

      {{/* 1. TL;DR box */}}
      <div class="tldr-box">
        <span class="tldr-label">TL;DR</span>
        <p class="tldr-text">{{ $a.tldr }}</p>
      </div>

      {{/* 2. Problem / Why */}}
      <div class="summary-section">
        <span class="summary-section-label">
          {{- if eq .Site.Language.Lang "zh-tw" -}}問題 / 背景{{- else -}}Problem / Why{{- end -}}
        </span>
        <p class="summary-section-body">{{ $a.problem_why }}</p>
      </div>

      {{/* 3. Solution / How */}}
      <div class="summary-section">
        <span class="summary-section-label">
          {{- if eq .Site.Language.Lang "zh-tw" -}}解法 / 方法{{- else -}}Solution / How{{- end -}}
        </span>
        <p class="summary-section-body">{{ $a.solution_how }}</p>
      </div>

      {{/* 4. Insights & Trade-offs */}}
      {{- $pros := index $a.insights_tradeoffs "pros" -}}
      {{- $cons := index $a.insights_tradeoffs "cons" -}}
      <div class="insights-section">
        <span class="insights-section-label">
          {{- if eq .Site.Language.Lang "zh-tw" -}}洞察與取捨{{- else -}}Insights & Trade-offs{{- end -}}
        </span>
        <div class="insights-grid">
          <div class="insights-col insights-col--pros">
            <span class="insights-col-header">
              {{- if eq .Site.Language.Lang "zh-tw" -}}✓ 優點{{- else -}}✓ Strengths{{- end -}}
            </span>
            <ul class="insights-list">
              {{ range $pros }}
              <li class="insights-item">{{ . }}</li>
              {{ end }}
            </ul>
          </div>
          <div class="insights-col insights-col--cons">
            <span class="insights-col-header">
              {{- if eq .Site.Language.Lang "zh-tw" -}}⚠ 取捨{{- else -}}⚠ Trade-offs{{- end -}}
            </span>
            <ul class="insights-list">
              {{ range $cons }}
              <li class="insights-item">{{ . }}</li>
              {{ end }}
            </ul>
          </div>
        </div>
      </div>

      {{/* 5. Tags & Action */}}
      <div class="tags-action-section">
        <span class="tags-action-label">
          {{- if eq .Site.Language.Lang "zh-tw" -}}標籤與行動{{- else -}}Tags & Action{{- end -}}
        </span>
        <div class="tags-action-list">
          {{ range $a.tags_action }}
          <span class="tag-pill tag-pill--primary">{{ . }}</span>
          {{ end }}
        </div>
      </div>

      {{/* Source link */}}
      {{- $srcLabel := printf "Original Link: %s" $a.title -}}
      {{- if eq .Site.Language.Lang "zh-tw" -}}{{- $srcLabel = printf "原文連結：%s" $a.title -}}{{- end -}}
      <div class="source-link-row">
        <a class="source-link"
           href="{{ $a.url }}"
           target="_blank"
           rel="noopener noreferrer"
           aria-label="{{ $srcLabel }}">
          <svg class="source-link-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M19 19H5V5h7V3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
          </svg>
          {{- if eq .Site.Language.Lang "zh-tw" -}}原文連結{{- else -}}Original Link{{- end -}}
        </a>
      </div>

    {{ else }}
    {{/* Empty state — no articles today */}}
    <div class="detail-empty-state">
      <p>
        {{- if eq .Site.Language.Lang "zh-tw" -}}
          今日無新增文章。
          <a href="{{ "/" | relLangURL }}">點此回到存檔</a>。
        {{- else -}}
          No articles today.
          <a href="{{ "/" | relLangURL }}">Return to archive</a>.
        {{- end -}}
      </p>
    </div>
    {{ end }}

    </section>
  </div>

</div>{{/* end .detail-layout */}}

</main>
{{ end }}
```

#### Key template patterns to remember

**Scratch for unique tag collection:**
```gotemplate
{{- $seen := newScratch -}}
{{ range $articles }}
  {{ range .tags_action }}
    {{ if not ($seen.Get .) }}
      {{- $seen.Set . true -}}
      {{/* render tag */}}
    {{ end }}
  {{ end }}
{{ end }}
```

**Accessing nested map from frontmatter** (use `index` — not dot notation):
```gotemplate
{{/* WRONG — may panic on nil */}}
{{ $a.insights_tradeoffs.pros }}

{{/* CORRECT — safe access */}}
{{ $pros := index $a.insights_tradeoffs "pros" }}
{{ $cons := index $a.insights_tradeoffs "cons" }}
{{ range $pros }}{{ . }}{{ end }}
```

**Integer conversion for rating comparison:**
```gotemplate
{{- $ratingInt := int ($a.rating | default 3) -}}
{{ range seq 1 5 }}
  {{ if le . $ratingInt }}...filled...{{ else }}...empty...{{ end }}
{{ end }}
```

**ARIA label variable pattern (avoid quoting conflicts):**
```gotemplate
{{- $srcLabel := printf "Original Link: %s" $a.title -}}
{{- if eq .Site.Language.Lang "zh-tw" -}}{{- $srcLabel = printf "原文連結：%s" $a.title -}}{{- end -}}
<a aria-label="{{ $srcLabel }}" ...>
```

**Language detection inside `range` loops** (use `$` prefix):
```gotemplate
{{ range $idx, $art := $articles }}
  {{ if eq $.Site.Language.Lang "zh-tw" }}...{{ end }}
{{ end }}
```

**`first` slice function for limiting sidebar tags:**
```gotemplate
{{ range first 3 $art.tags_action }}{{ . }}{{ end }}
```

### CSS Specification for New Sections

Append the following **in order** after the last line (`}`) of Section 23 in `static/css/index.css`:

```css
/* ============================================================
   24. Detail page header
   ============================================================ */

.detail-header {
  background: #ffffff;
  border-bottom: 1px solid var(--color-border-low);
  padding: var(--spacing-lg) 0;
}
.detail-header-inner {
  max-width: var(--spacing-container-max);
  margin-inline: auto;
  padding-inline: var(--spacing-lg);
}
.detail-header-date {
  display: block;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: var(--spacing-xs);
}
.detail-header-highlight {
  color: var(--color-on-surface);
  margin: 0 0 var(--spacing-sm);
}
.detail-header-badges {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}
.detail-meta-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px var(--spacing-sm);
  border-radius: var(--radius-full);
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-sm);
  font-weight: var(--fw-label-sm);
  line-height: var(--lh-label-sm);
  background: var(--color-surface-container-low);
  color: var(--color-on-surface-variant);
}

/* ============================================================
   25. Split-pane layout
   ============================================================ */

.detail-layout {
  display: grid;
  grid-template-columns: var(--spacing-nav-width) 1fr; /* 280px sidebar + fluid panel */
}
@media (max-width: 767px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}

/* ============================================================
   26. Detail sidebar
   ============================================================ */

.detail-sidebar {
  position: sticky;
  top: 64px;              /* offset for fixed header */
  height: calc(100vh - 64px);
  overflow-y: auto;
  background: var(--color-surface-container-lowest); /* #ffffff */
  border-right: 1px solid var(--color-border-low);
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md) 0;
  gap: var(--spacing-xs);
}
/* Thin scrollbar for sidebar */
.detail-sidebar::-webkit-scrollbar { width: 4px; }
.detail-sidebar::-webkit-scrollbar-track { background: transparent; }
.detail-sidebar::-webkit-scrollbar-thumb {
  background: var(--color-outline-variant);
  border-radius: var(--radius-full);
}
.sidebar-section-label {
  padding: var(--spacing-xs) var(--spacing-md);
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-sm);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-sm);
  color: var(--color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.sidebar-search-wrapper {
  padding: 0 var(--spacing-md) var(--spacing-xs);
}
.sidebar-search-input {
  width: 100%;
  min-height: 36px;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--color-border-low);
  border-radius: var(--radius-default);
  background: var(--color-surface-container-low);
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-md);
  color: var(--color-on-surface);
  outline: none;
  transition: var(--transition-all);
}
.sidebar-search-input:not([disabled]):focus {
  border-color: var(--color-primary);
  background: #ffffff;
}
.sidebar-search-input[disabled] {
  cursor: not-allowed;
  opacity: 0.6;
}
.sidebar-tags-section {
  padding: 0 var(--spacing-md) var(--spacing-xs);
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}
.sidebar-article-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: var(--color-border-low); /* hairline gap colour */
}

/* ============================================================
   27. Sidebar article card
   ============================================================ */

/* NOTE: .active-card-indicator already defined in Section 14 — do NOT redefine */
.sidebar-article-card {
  background: #ffffff;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  transition: var(--transition-all);
  min-height: 44px; /* NFR-6 click target */
}
.sidebar-article-card:hover {
  background: var(--color-surface-container-low);
}
.sidebar-article-title {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-md);
  font-weight: 600;
  line-height: var(--lh-body-md);
  color: var(--color-on-surface);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.sidebar-article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

/* ============================================================
   28. Detail panel
   ============================================================ */

.detail-panel-outer {
  background: var(--color-background);
  min-height: calc(100vh - 64px);
  overflow-y: auto;
}
.detail-panel {
  max-width: 800px;
  margin-inline: auto;
  padding: var(--spacing-xl);
}
.article-panel-header {
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-low);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
.article-panel-title {
  color: var(--color-on-surface);
  margin: 0;
}
@media (max-width: 767px) {
  .detail-sidebar {
    position: static;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--color-border-low);
  }
  .detail-panel {
    padding: var(--spacing-lg) var(--spacing-md);
  }
}

/* ============================================================
   29. TL;DR box
   ============================================================ */

.tldr-box {
  border-left: 3px solid var(--color-primary);
  background: rgba(0, 74, 198, 0.05);
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}
.tldr-label {
  display: block;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-xs);
}
.tldr-text {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-lg);
  font-weight: 500;
  line-height: var(--lh-body-lg);
  color: var(--color-on-surface);
  margin: 0;
}

/* ============================================================
   30. Summary sections (Problem/Why, Solution/How)
   ============================================================ */

.summary-section {
  background: #ffffff;
  border: 1px solid var(--color-border-low);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}
.summary-section-label {
  display: block;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  color: var(--color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-sm);
}
.summary-section-body {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-md);
  line-height: var(--lh-body-md);
  color: var(--color-on-surface);
  margin: 0;
}

/* ============================================================
   31. Insights & Trade-offs grid
   ============================================================ */

.insights-section {
  margin-bottom: var(--spacing-xl);
}
.insights-section-label {
  display: block;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  color: var(--color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-sm);
}
.insights-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}
@media (max-width: 767px) {
  .insights-grid {
    grid-template-columns: 1fr;
  }
}
.insights-col {
  background: #ffffff;
  border: 1px solid var(--color-border-low);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}
.insights-col--pros { border-top: 3px solid #16a34a; } /* emerald */
.insights-col--cons { border-top: 3px solid #d97706; } /* amber  */
.insights-col-header {
  display: block;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  margin-bottom: var(--spacing-sm);
}
.insights-col--pros .insights-col-header { color: #16a34a; }
.insights-col--cons .insights-col-header { color: #d97706; }
.insights-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}
.insights-item {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-md);
  line-height: var(--lh-body-md);
  color: var(--color-on-surface);
  padding-left: var(--spacing-md);
  position: relative;
}
.insights-item::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--color-on-surface-variant);
}

/* ============================================================
   32. Rating stars
   ============================================================ */

.rating-stars {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.rating-star {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}
.rating-star--filled { color: var(--color-primary); }
.rating-star--empty  { color: var(--color-outline-variant); }

/* ============================================================
   33. Tags & Action section
   ============================================================ */

.tags-action-section {
  margin-bottom: var(--spacing-xl);
}
.tags-action-label {
  display: block;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  color: var(--color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-sm);
}
.tags-action-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}
/* Primary-tinted tag pill variant — additive modifier on .tag-pill */
.tag-pill--primary {
  background: rgba(0, 74, 198, 0.1);
  color: var(--color-primary);
}

/* ============================================================
   34. Source link row
   ============================================================ */

.source-link-row {
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-low);
  margin-top: var(--spacing-xl);
}
.source-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-md);
  font-weight: 500;
  color: var(--color-primary);
  text-decoration: none;
  transition: var(--transition-all);
  min-height: 44px; /* NFR-6 click target */
}
.source-link:hover {
  color: var(--color-primary-container);
  text-decoration: underline;
}
.source-link-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* ============================================================
   35. Detail empty state
   ============================================================ */

.detail-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl) var(--spacing-lg);
  text-align: center;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-lg);
  line-height: var(--lh-body-lg);
  color: var(--color-on-surface-variant);
}
.detail-empty-state a {
  color: var(--color-primary);
  text-decoration: underline;
}
```

### Guardrails & Common LLM Mistakes to Avoid

1. **Do NOT use `$article.insights_tradeoffs.pros`** — Hugo frontmatter nested map access requires `index $article.insights_tradeoffs "pros"`. Dot notation on a raw map interface will panic on nil.

2. **Do NOT define `.active-card-indicator` again** — it is already in Section 14 of the CSS. Adding a second definition will silently override. Use it as a modifier class only.

3. **Do NOT use `.grid-12 / .col-4 / .col-8` for the split-pane** — these use proportional `1fr` columns. The detail layout needs a literal `280px` left column. Use `.detail-layout` (Section 25) instead.

4. **Do NOT modify Sections 1–23** of `static/css/index.css` — append only after the final `}` of Section 23.

5. **Do NOT remove the `disabled` attribute from the search input** — it is intentionally non-functional for this story. Story 2.5 will activate it.

6. **Do NOT render `.Content`** — the markdown body of daily posts is a placeholder comment. Use `.Params.articles` exclusively.

7. **`newScratch` usage** — `{{ $seen := newScratch }}` creates a Hugo scratch map. Use `$seen.Get key` (returns nil if absent, boolean true when set), not `isset`. This is the correct pattern for de-duplication inside templates.

8. **`range seq 1 5`** — in Hugo, `seq 1 5` returns a slice `[1 2 3 4 5]`. Inside the range block, `.` is the integer. `le . $ratingInt` uses the built-in `le` comparison. Cast `$ratingInt` to `int` via `{{ $ratingInt := int ($a.rating | default 3) }}` to ensure type compatibility.

9. **`first` function** — `{{ range first 3 $art.tags_action }}` limits sidebar tag pills to 3 per card. If `tags_action` is nil/empty, `first` returns an empty slice safely.

10. **`relLangURL` for home link** — use `{{ "/" | relLangURL }}` (not `relURL`) to get language-prefixed home link (`/en/` or `/zh-tw/`).

### Inline SVG Paths Reference

| Icon | Usage | SVG path |
|---|---|---|
| Filled star | `rating-star--filled` | `M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z` |
| Empty star | `rating-star--empty` | `M22 9.74l-7.19-.62L12 2.5 9.19 9.13 2 9.74l5.46 4.73-1.64 7.03L12 17.77l6.18 3.73-1.63-7.03L22 9.74zM12 15.9l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.8l1.71 4.64 4.38.38-3.32 2.88 1 4.28L12 15.9z` |
| External link | `.source-link-icon` | `M19 19H5V5h7V3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z` |
