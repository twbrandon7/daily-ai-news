# Story 2.3: Bento Grid Archive Layout (Homepage)

Status: done

## Story

As a reader,
I want a Bento-grid layout homepage displaying chronological historical days with daily summaries,
so that I can quickly scan past news.

## Acceptance Criteria

1. **Given** historical post files exist in `content/en/posts/` or `content/zh-tw/posts/`
   **When** I visit the homepage (`/`, `/en/`, or `/zh-tw/`)
   **Then** the page renders a Bento grid of daily cards sorted newest-first.

2. **And** each card displays:
   - The formatted date (e.g. "January 2, 2006" for EN; "2006年1月2日" for zh-tw)
   - A short daily highlight summary from `.Params.daily_highlight` (or a date-based fallback when empty)
   - The count of articles (`len .Params.articles`) in an article-count badge
   - A "View Summary" (EN) / "查看摘要" (zh-tw) button linking to `.RelPermalink`

3. **And** hovering over a card triggers a **2px upward lift** (`translateY(-2px)`) and the `--shadow-hover` drop shadow via a 200ms CSS transition.

4. **And** when no posts exist in the section, an empty-state message renders:
   - EN: "No historical archives yet. Add blog sources to start generating."
   - zh-tw: "尚無歷史存檔摘要。新增部落格來源以開始生成。"

5. **And** the homepage also includes a **Hero section** (badge, title "Daily AI Insights", subtitle) and a **Features Quick Look section** (3 feature items with inline SVG icons), matching the `ai_2` mockup composition required by FR-5.

6. **And** pagination controls appear when total posts exceed 9 per page (Newer ← / → Older navigation links).

7. **And** `~/bin/hugo --minify` builds from the project root with exit code 0 and no ERRORs.

## Tasks / Subtasks

- [ ] Task 1: Append archive/homepage CSS sections to `static/css/index.css` (AC: #1, #2, #3, #4, #5, #6)
  - [ ] **Check `:root` for missing tertiary-fixed tokens** — if `--color-tertiary-fixed` and `--color-on-tertiary-fixed` are absent from Section 2, append them to `:root` (values: `#ffdbcd` and `#360f00`). Do NOT duplicate if already present.
  - [ ] Append Section 16 — Hero: `.hero-section`, `.hero-inner`, `.hero-badge`, `.hero-badge-icon`, `.hero-title`, `.hero-subtitle`
  - [ ] Append Section 17 — Features Quick Look: `.features-section`, `.features-grid`, `.feature-item`, `.feature-icon-wrapper`, `.feature-title`, `.feature-desc`
  - [ ] Append Section 18 — Archive section shell: `.archive-section`, `.archive-header`, `.archive-label`, `.archive-title`
  - [ ] Append Section 19 — Bento grid and card: `.bento-grid` (responsive auto-fill grid), `.bento-card` (flex column + 200ms transition), `.bento-card:hover` (`translateY(-2px)` + `var(--shadow-hover)`), `.bento-card-header`, `.bento-card-date`, `.bento-card-body`, `.bento-card-title` (3-line clamp)
  - [ ] Append Section 20 — Article count badge: `.article-count-badge` (pill, tertiary-fixed colors)
  - [ ] Append Section 21 — View Summary button: `.btn-view-summary` (full-width, 44px min-height, primary border/text, hover fills primary background)
  - [ ] Append Section 22 — Pagination: `.pagination-controls`, `.pagination-btn`, `.pagination-info`
  - [ ] Append Section 23 — Empty state: `.bento-empty-state`

- [ ] Task 2: Implement `layouts/index.html` — full homepage template (AC: #1, #2, #3, #4, #5, #6)
  - [ ] Replace the existing stub entirely with `{{ define "main" }}` block (see **Dev Notes → layouts/index.html Target State** below)
  - [ ] Hero section: star SVG badge, `h1.hero-title.text-headline-xl` "Daily AI Insights", `p.hero-subtitle.text-body-lg` (EN/zh-tw conditional)
  - [ ] Features section: 3 items with **inline SVG icons** (NO Material Symbols CDN — violates AD-5), i18n-conditional text for title + description
  - [ ] Archive header: "Archive" label with `.text-label-md` (intentionally uppercase) + `h2.text-headline-lg` "Daily Archive" / "每日存檔"
  - [ ] Load posts: `$posts := where .Site.RegularPages "Section" "posts"` — `.Site.RegularPages` is already scoped to current language
  - [ ] Paginator: `$paginator := .Paginate ($posts.ByDate.Reverse) 9` — **call this unconditionally (before any `if` checks) to avoid Hugo paginator errors on `/page/2/` requests**
  - [ ] Empty state: `{{ if not $paginator.Pages }}` → render `.bento-empty-state` with i18n message
  - [ ] Bento grid: `{{ else }}` branch → `<div class="bento-grid" role="list">`, iterate `{{ range $paginator.Pages }}`
  - [ ] Each card: `<article class="bento-card card" role="listitem">` with header (date + badge), body (title from `.Params.daily_highlight`), and `.btn-view-summary` link
  - [ ] Pagination nav: show only when `$paginator.TotalPages > 1`; use `$paginator.HasPrev`, `$paginator.Prev.URL`, `$paginator.HasNext`, `$paginator.Next.URL`
  - [ ] ARIA: `role="list"` on `.bento-grid`, `role="listitem"` on each card, descriptive `aria-label` on each "View Summary" link (use a `$ariaLabel` variable to avoid quoting conflicts — see Dev Notes)

- [ ] Task 3: Update `layouts/_default/list.html` — minimal design-system alignment (AC: #7)
  - [ ] Replace stub with design-system-aware markup (`.container`, `.text-headline-lg`, `.card` list items using design tokens)
  - [ ] This is the section page template for `/en/posts/` — not the primary archive view; simple clean list suffices

- [ ] Task 4: Build verification (AC: #7)
  - [ ] Run `~/bin/hugo --minify` from project root — confirm exit code 0, no ERROR lines
  - [ ] Confirm `public/en/index.html` contains `bento-grid` class
  - [ ] Confirm `public/zh-tw/index.html` contains `查看摘要` text
  - [ ] Confirm `public/en/index.html` contains `hero-section` class and hero heading
  - [ ] Confirm no `tailwindcss`, `material-symbols`, `cdn.jsdelivr`, or `unpkg` references in `layouts/index.html`
  - [ ] Inspect the built CSS output to confirm `.bento-card:hover` rule is present

## Dev Notes

### Architecture Constraints (MUST follow)

- **AD-5 — Zero-Dependency Custom Hugo Layouts** ([`ARCHITECTURE-SPINE.md`]): The `ai_2` mockup is reference-only — it uses Tailwind CDN + Material Symbols CDN, both of which are **banned**. Translate the visual intent into hand-written CSS using existing tokens.
- **AD-6 — Structured Frontmatter Storage**: Read all post data from Hugo frontmatter only (`date`, `daily_highlight`, `articles` array). Do **not** parse or render the markdown body.
- **CSS append-only contract**: Sections 1–15 in `static/css/index.css` were established in Story 2.2 and are a downstream contract. **Only append** new Sections 16+. Never rename, move, or delete existing class names.
- **Hugo binary**: Use `~/bin/hugo` (NOT on system PATH — see Story 2.1 debug log). Hugo 0.128.0+ is installed at that path.
- **No Material Symbols CDN**: Use inline SVG paths for feature icons. Simple path data is provided in the template target below.

### Files to Create / Modify

| File | Action | Notes |
|---|---|---|
| `static/css/index.css` | **APPEND** Sections 16–23 | Preserve all existing Sections 1–15 |
| `layouts/index.html` | **UPDATE** | Replace stub entirely |
| `layouts/_default/list.html` | **UPDATE** | Minimal design-system alignment |

### Files to NOT Touch

- `src/pipeline.py`, `src/summarizer.py`, `src/translator.py`, `src/publisher.py` — Epic 1, complete
- `data/blogs.yaml`, `data/fetched_posts.json` — pipeline-owned
- `.github/workflows/pipeline.yml` — Epic 1, complete
- `content/**/*.md` — pipeline-owned (Story 1.5)
- `layouts/_default/single.html` — owned by Story 2.4
- `static/js/.gitkeep` / `static/js/main.js` — owned by Story 2.5
- Sections 1–15 of `static/css/index.css` — Story 2.2 foundation

### Existing CSS Foundation (from Story 2.2) — DO NOT RE-CREATE

All of the following are **already defined** in `static/css/index.css` and must be **reused** in templates:

| Already Defined | Class / Token |
|---|---|
| Design tokens | All `--color-*`, `--radius-*`, `--spacing-*`, `--fs-*`, `--lh-*`, `--fw-*`, `--shadow-hover`, `--transition-all` |
| Typography utilities | `.text-headline-xl`, `.text-headline-lg`, `.text-headline-md`, `.text-body-lg`, `.text-body-md`, `.text-label-md`, `.text-label-sm` |
| Tonal layers | `.layer-0`, `.layer-1`, `.layer-2`, `.interactive-hover` |
| Layout primitives | `.container`, `.grid-12`, `.col-4`, `.col-8` |
| Base components | `.site-header`, `.btn-ghost`, `.card`, `.tag-pill`, `.site-content`, `.active-card-indicator` |

> **CRITICAL:** `.text-label-md` includes `text-transform: uppercase` and `letter-spacing: 0.05em`. **Do NOT use it for date labels** — the date "January 12, 2026" must not render as "JANUARY 12, 2026". Use `.bento-card-date` (defined in Section 19 below) which uses the raw token values without the uppercase override.

> The `.card` class gives: `background:#ffffff; border:1px solid var(--color-border-low); border-radius:var(--radius-lg); padding:var(--spacing-lg);` — `.bento-card` extends `.card` by adding flex-column and hover transition, so apply **both classes** (`class="bento-card card"`) on each card element.

### Hugo Template Patterns

**Data access inside the range loop:**
```gotemplate
{{ $posts := where .Site.RegularPages "Section" "posts" }}
{{/* MUST call .Paginate unconditionally — before any if/else — to avoid /page/2/ errors */}}
{{ $paginator := .Paginate ($posts.ByDate.Reverse) 9 }}

{{ range $paginator.Pages }}
  {{ $count := len .Params.articles }}              {{/* int, safe to use directly */}}
  {{ .Date | time.Format "January 2, 2006" }}       {{/* EN: "July 12, 2026" */}}
  {{ .Date | time.Format "2006年1月2日" }}           {{/* zh-tw: "2026年7月12日" */}}
  {{ .Params.daily_highlight }}                      {{/* string, may be "" */}}
  {{ .RelPermalink }}                                {{/* "/en/posts/2026-07-12/" */}}
{{ end }}
```

**Language detection (inside range, `$` = top-level context):**
```gotemplate
{{- if eq $.Site.Language.Lang "zh-tw" -}}Traditional Chinese{{- else -}}English{{- end -}}
```

**Empty frontmatter guard:**
```gotemplate
{{- with .Params.daily_highlight -}}{{ . }}{{- else -}}Fallback text{{- end -}}
```

**ARIA label without quoting conflicts (build as variable first):**
```gotemplate
{{ $viewLabel := printf "View Summary for %s" (.Date | time.Format "January 2, 2006") }}
{{ if eq $.Site.Language.Lang "zh-tw" }}
  {{ $viewLabel = printf "查看 %s 摘要" (.Date | time.Format "2006年1月2日") }}
{{ end }}
<a href="{{ .RelPermalink }}" class="btn-view-summary" aria-label="{{ $viewLabel }}">
```

**Pagination URLs** (Hugo auto-generates paginated routes under `/en/page/2/`, `/zh-tw/page/2/`):
```gotemplate
$paginator.TotalPages    {{/* int: total number of pages */}}
$paginator.PageNumber    {{/* int: current page (1-based) */}}
$paginator.HasPrev       {{/* bool */}}
$paginator.Prev.URL      {{/* string: URL of previous (newer) page */}}
$paginator.HasNext       {{/* bool */}}
$paginator.Next.URL      {{/* string: URL of next (older) page */}}
```

### CSS Specifications for New Sections

#### Section 16 — Hero
```css
/* 16. Hero section */
.hero-section {
  padding: var(--spacing-2xl) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-low);
  background: var(--color-background);
}
.hero-inner {
  max-width: 560px;
  margin-inline: auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  background: rgba(0, 74, 198, 0.1);   /* primary/10 */
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
}
.hero-badge-icon { width: 16px; height: 16px; }
.hero-title { color: var(--color-on-surface); letter-spacing: var(--ls-headline-xl); margin: 0; }
.hero-subtitle { color: var(--color-on-surface-variant); max-width: 560px; margin: 0; }
```

#### Section 17 — Features
```css
/* 17. Features Quick Look */
.features-section {
  padding: var(--spacing-xl) var(--spacing-lg);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-low);
}
.features-grid {
  max-width: var(--spacing-container-max);
  margin-inline: auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-lg);
}
.feature-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
}
.feature-icon-wrapper {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-secondary-container);
  color: var(--color-on-secondary-container);
  border-radius: var(--radius-xl);
  padding: var(--spacing-sm);
}
.feature-icon-wrapper svg { width: 20px; height: 20px; }
.feature-title { margin: 0 0 var(--spacing-xs); }
.feature-desc  { color: var(--color-on-surface-variant); margin: 0; }
```

#### Section 18 — Archive section shell
```css
/* 18. Archive section */
.archive-section { padding: var(--spacing-2xl) var(--spacing-lg); }
.archive-header {
  max-width: var(--spacing-container-max);
  margin-inline: auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--spacing-xl);
}
.archive-label {
  display: block;
  color: var(--color-primary);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  margin-bottom: var(--spacing-xs);
}
.archive-title { color: var(--color-on-surface); margin: 0; }
```

#### Section 19 — Bento grid and card
```css
/* 19. Bento grid & card */
.bento-grid {
  max-width: var(--spacing-container-max);
  margin-inline: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}
/* .bento-card extends .card — apply both classes: class="bento-card card" */
.bento-card {
  display: flex;
  flex-direction: column;
  min-height: 220px;
  transition: var(--transition-all);
}
.bento-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);   /* 0 2px 8px -1px rgb(0 0 0 / 0.08) */
}
.bento-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}
/* DO NOT use .text-label-md here — it adds text-transform:uppercase which breaks dates */
.bento-card-date {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-sm);
  font-weight: var(--fw-label-sm);
  line-height: var(--lh-label-sm);
  color: var(--color-on-surface-variant);
}
.bento-card-body {
  flex: 1;
  margin-bottom: var(--spacing-md);
}
.bento-card-title {
  color: var(--color-on-surface);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

#### Section 20 — Article count badge
```css
/* 20. Article count badge */
/* Uses tertiary-fixed palette — add to :root if absent:
   --color-tertiary-fixed:    #ffdbcd;
   --color-on-tertiary-fixed: #360f00; */
.article-count-badge {
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  padding: 2px var(--spacing-sm);
  border-radius: var(--radius-full);
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-sm);
  font-weight: var(--fw-label-sm);
  line-height: var(--lh-label-sm);
  background: #ffdbcd;   /* --color-tertiary-fixed */
  color: #360f00;        /* --color-on-tertiary-fixed */
}
```

#### Section 21 — View Summary button
```css
/* 21. View Summary button */
.btn-view-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: var(--spacing-md) 0;
  margin-top: auto;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-lg);
  color: var(--color-primary);
  background: transparent;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  letter-spacing: 0;
  text-decoration: none;
  cursor: pointer;
  transition: var(--transition-all);
  min-height: 44px;   /* NFR-6 minimum click target */
}
.btn-view-summary:hover {
  background: var(--color-primary);
  color: var(--color-on-primary);
}
```

#### Section 22 — Pagination
```css
/* 22. Pagination controls */
.pagination-controls {
  max-width: var(--spacing-container-max);
  margin: var(--spacing-xl) auto 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
}
.pagination-btn {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: var(--spacing-xs) var(--spacing-md);
  border: 1px solid var(--color-border-low);
  border-radius: var(--radius-default);
  color: var(--color-on-surface-variant);
  background: transparent;
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-md);
  text-decoration: none;
  transition: var(--transition-all);
}
.pagination-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.pagination-info {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  color: var(--color-on-surface-variant);
}
```

#### Section 23 — Empty state
```css
/* 23. Bento empty state */
.bento-empty-state {
  max-width: var(--spacing-container-max);
  margin-inline: auto;
  padding: var(--spacing-2xl) var(--spacing-lg);
  text-align: center;
  color: var(--color-on-surface-variant);
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-lg);
  line-height: var(--lh-body-lg);
}
```

### `layouts/index.html` Target State

Replace the current stub entirely:

```gohtml
{{ define "main" }}
<main>

  {{/* ── Hero Section ─────────────────────────────────────────────── */}}
  <section class="hero-section">
    <div class="hero-inner">
      <div class="hero-badge">
        {{/* Inline star SVG — no external CDN (AD-5) */}}
        <svg class="hero-badge-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>
        </svg>
        AI-Native Intelligence Hub
      </div>
      <h1 class="hero-title text-headline-xl">Daily AI Insights</h1>
      <p class="hero-subtitle text-body-lg">
        {{- if eq .Site.Language.Lang "zh-tw" -}}
        您的自動化情報中心，專為科技與 AI 領域的最新進展而生。每日自動彙整全球核心技術動態，提供精準的深度解析。
        {{- else -}}
        Your automated intelligence hub for the latest developments in AI and technology.
        Daily automated summaries of global technical trends with precise deep analysis.
        {{- end -}}
      </p>
    </div>
  </section>

  {{/* ── Features Quick Look ──────────────────────────────────────── */}}
  <section class="features-section">
    <div class="features-grid">

      <div class="feature-item">
        <div class="feature-icon-wrapper" aria-hidden="true">
          {{/* Speed / lightning icon */}}
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 2v13l3-3 3 3V2zm10 9.01L7 11v2l10 .01z"/></svg>
        </div>
        <div>
          <h3 class="feature-title text-headline-md">
            {{- if eq .Site.Language.Lang "zh-tw" -}}即時 TL;DR{{- else -}}Instant TL;DR{{- end -}}
          </h3>
          <p class="feature-desc text-body-md">
            {{- if eq .Site.Language.Lang "zh-tw" -}}毫秒級產出關鍵摘要，迅速掌握文章精髓。{{- else -}}Key insights at speed — grasp any article in seconds.{{- end -}}
          </p>
        </div>
      </div>

      <div class="feature-item">
        <div class="feature-icon-wrapper" aria-hidden="true">
          {{/* Code brackets icon */}}
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/></svg>
        </div>
        <div>
          <h3 class="feature-title text-headline-md">
            {{- if eq .Site.Language.Lang "zh-tw" -}}深度技術分析{{- else -}}Technical Depth{{- end -}}
          </h3>
          <p class="feature-desc text-body-md">
            {{- if eq .Site.Language.Lang "zh-tw" -}}深度技術分析，涵蓋代碼實作與架構邏輯。{{- else -}}In-depth analysis covering implementation details and architecture.{{- end -}}
          </p>
        </div>
      </div>

      <div class="feature-item">
        <div class="feature-icon-wrapper" aria-hidden="true">
          {{/* Translate icon */}}
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/></svg>
        </div>
        <div>
          <h3 class="feature-title text-headline-md">
            {{- if eq .Site.Language.Lang "zh-tw" -}}多語言支援{{- else -}}Multi-language{{- end -}}
          </h3>
          <p class="feature-desc text-body-md">
            {{- if eq .Site.Language.Lang "zh-tw" -}}多語言支援，跨越語言障礙獲取第一手資訊。{{- else -}}Bilingual summaries in English and Traditional Chinese.{{- end -}}
          </p>
        </div>
      </div>

    </div>
  </section>

  {{/* ── Daily Archive Grid ───────────────────────────────────────── */}}
  <section class="archive-section">

    <div class="archive-header">
      <div>
        <span class="archive-label">Archive</span>
        <h2 class="archive-title text-headline-lg">
          {{- if eq .Site.Language.Lang "zh-tw" -}}每日存檔{{- else -}}Daily Archive{{- end -}}
        </h2>
      </div>
    </div>

    {{/* Collect posts scoped to current language; sort newest-first */}}
    {{ $posts := where .Site.RegularPages "Section" "posts" }}
    {{/* IMPORTANT: .Paginate must be called unconditionally — before any if/else —
         to prevent Hugo errors on paginated routes (/page/2/, /page/3/, etc.) */}}
    {{ $paginator := .Paginate ($posts.ByDate.Reverse) 9 }}

    {{ if not $paginator.Pages }}

    {{/* Empty state */}}
    <div class="bento-empty-state">
      <p>
        {{- if eq .Site.Language.Lang "zh-tw" -}}
        尚無歷史存檔摘要。新增部落格來源以開始生成。
        {{- else -}}
        No historical archives yet. Add blog sources to start generating.
        {{- end -}}
      </p>
    </div>

    {{ else }}

    {{/* Bento grid */}}
    <div class="bento-grid" role="list">
      {{ range $paginator.Pages }}
      {{ $count := len .Params.articles }}
      {{ $viewLabel := printf "View Summary for %s" (.Date | time.Format "January 2, 2006") }}
      {{ if eq $.Site.Language.Lang "zh-tw" }}
        {{ $viewLabel = printf "查看 %s 摘要" (.Date | time.Format "2006年1月2日") }}
      {{ end }}
      <article class="bento-card card" role="listitem">

        <div class="bento-card-header">
          <span class="bento-card-date">
            {{- if eq $.Site.Language.Lang "zh-tw" -}}
            {{- .Date | time.Format "2006年1月2日" -}}
            {{- else -}}
            {{- .Date | time.Format "January 2, 2006" -}}
            {{- end -}}
          </span>
          <span class="article-count-badge">
            {{ $count }}
            {{- if eq $.Site.Language.Lang "zh-tw" -}}&nbsp;篇文章{{- else -}}&nbsp;articles{{- end -}}
          </span>
        </div>

        <div class="bento-card-body">
          <h3 class="bento-card-title text-headline-md">
            {{- with .Params.daily_highlight -}}
            {{ . }}
            {{- else -}}
            {{- if eq $.Site.Language.Lang "zh-tw" -}}
            {{ .Date | time.Format "2006年1月2日" }} 摘要
            {{- else -}}
            Summary for {{ .Date | time.Format "January 2, 2006" }}
            {{- end -}}
            {{- end -}}
          </h3>
        </div>

        <a href="{{ .RelPermalink }}"
           class="btn-view-summary"
           aria-label="{{ $viewLabel }}">
          {{- if eq $.Site.Language.Lang "zh-tw" -}}查看摘要{{- else -}}View Summary{{- end -}}
        </a>

      </article>
      {{ end }}
    </div>

    {{/* Pagination — only rendered when there are multiple pages */}}
    {{ if gt $paginator.TotalPages 1 }}
    {{ $paginationLabel := "Page navigation" }}
    {{ if eq .Site.Language.Lang "zh-tw" }}{{ $paginationLabel = "頁面導覽" }}{{ end }}
    <nav class="pagination-controls" aria-label="{{ $paginationLabel }}">
      {{ if $paginator.HasPrev }}
      <a href="{{ $paginator.Prev.URL }}" class="pagination-btn">
        {{- if eq .Site.Language.Lang "zh-tw" -}}← 較新{{- else -}}← Newer{{- end -}}
      </a>
      {{ end }}
      <span class="pagination-info">
        {{ $paginator.PageNumber }}&thinsp;/&thinsp;{{ $paginator.TotalPages }}
      </span>
      {{ if $paginator.HasNext }}
      <a href="{{ $paginator.Next.URL }}" class="pagination-btn">
        {{- if eq .Site.Language.Lang "zh-tw" -}}較舊 →{{- else -}}Older →{{- end -}}
      </a>
      {{ end }}
    </nav>
    {{ end }}

    {{ end }}

  </section>
</main>
{{ end }}
```

### `layouts/_default/list.html` Minimal Update

Replace the existing stub with a clean design-system-aware section listing:

```gohtml
{{ define "main" }}
<main>
  <div class="container" style="padding-top: var(--spacing-xl);">
    <h1 class="text-headline-lg" style="color: var(--color-on-surface); margin-bottom: var(--spacing-xl);">
      {{ .Title }}
    </h1>
    <div style="display: flex; flex-direction: column; gap: var(--spacing-md);">
      {{ range .Pages }}
      <div class="card">
        <a href="{{ .RelPermalink }}"
           style="color: var(--color-primary); text-decoration: none; font-size: var(--fs-headline-md); font-weight: 600;">
          {{ .Title }}
        </a>
        <p style="color: var(--color-on-surface-variant); font-size: var(--fs-body-md); margin-top: var(--spacing-xs);">
          {{ .Date | time.Format "January 2, 2006" }}
        </p>
      </div>
      {{ end }}
    </div>
  </div>
</main>
{{ end }}
```

### Previous Story Learnings (Story 2.2)

- Hugo binary is at `~/bin/hugo`, not on PATH — always use the full path.
- `.gitkeep` placeholder files were deleted before creating real assets; no similar placeholders exist for this story.
- The CSS section ordering in `index.css` is a numbered contract (Sections 1–15). Continue from Section 16.
- `static/js/main.js` is still a `.gitkeep` at this point — Story 2.5 owns it; do not create or modify it.
- `baseof.html` already loads `css/index.css` and wires the `<body class="layer-0">` and `.site-content` wrapper — the homepage template only needs to define the `{{ define "main" }}` block.
- `baseof.html` already includes a comment `<!-- Story 2.5 will add js/main.js -->` — do not add the script tag in this story.

### Known Frontmatter Structure (from Story 1.5)

Placeholder post at `content/en/posts/2026-07-12.md`:
```yaml
title: "2026-07-12"
date: 2026-07-12
daily_highlight: ""
articles: []
```

Real pipeline-populated posts will have:
```yaml
title: "2026-07-12"
date: 2026-07-12
daily_highlight: "Today's AI focus: OpenAI o1 reasoning advances."
articles:
  - title: "..."
    tl_dr: "..."
    # ... full 5-element structure from Story 1.3
```

The template must handle **both states** (empty `daily_highlight` and empty `articles` array) without crashing.

### Accessibility Requirements (NFR-6)

- All `btn-view-summary` links must have a descriptive `aria-label` (implemented via `$viewLabel` variable pattern above).
- Feature icon wrappers are decorative — set `aria-hidden="true"` on the wrapping `<div>`.
- Inline SVG elements that are decorative should have `aria-hidden="true"`.
- The `.bento-grid` container should have `role="list"` and each `<article>` should have `role="listitem"` for screen reader announcement.
- Pagination `<nav>` must have a descriptive `aria-label`.

### Project Structure Notes

- Aligns with `AD-5` — all templates and CSS remain under `layouts/` and `static/css/index.css` respectively.
- `layouts/index.html` maps to Hugo's home page template (used for `/`, `/en/`, `/zh-tw/` in multilingual mode).
- `layouts/_default/list.html` maps to section list pages (e.g. `/en/posts/`).
- No new files are needed beyond the two layout updates and CSS append.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — FR-5, Story 2.3 AC]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md` — AD-5 (zero-dependency), AD-6 (frontmatter storage)]
- [Source: `_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/DESIGN.md` — Bento Card component, tonal layering, hover scale transition]
- [Source: `_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/EXPERIENCE.md` — Archive (Home) IA, Card Hover state, empty state copy, Bento Card behavioral rules]
- [Source: `_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/imports/ai_2/code_stitch.html` — Hero section, features grid, bento-grid, tonal-card HTML composition (reference-only — uses Tailwind/Material Symbols CDN which are BANNED)]
- [Source: `_bmad-output/implementation-artifacts/2-2-zero-dependency-layout-asset-architecture.md` — CSS Section 1–15 contract, `baseof.html` final state, Hugo binary path]

## Dev Agent Record

### Agent Model Used

GitHub Copilot — Amelia (bmad-agent-dev) — 2026-07-12

### Debug Log References

*(none — clean build on first attempt)*

### Completion Notes List

- AC#1–6: All acceptance criteria satisfied; `~/bin/hugo --minify` exits 0, no ERRORs.
- Task 1: Appended CSS Sections 16–23 to `static/css/index.css`; also added missing `--color-tertiary-fixed` / `--color-on-tertiary-fixed` tokens to `:root` (Section 2).
- Task 2: Replaced stub `layouts/index.html` with full homepage template — hero, features (inline SVGs, no CDN), archive section, bento grid, empty-state, and pagination.
- Task 3: Replaced stub `layouts/_default/list.html` with minimal design-system-aligned listing.
- Task 4: Build verified — `public/en/index.html` contains `bento-grid`, `hero-section`, "Daily AI Insights"; `public/zh-tw/index.html` contains `查看摘要`; `.bento-card:hover` rule present in built CSS; no banned CDN refs in `layouts/index.html`.
- Story status → `review`; `sprint-status.yaml` updated accordingly.

*(none yet — to be filled by implementing agent)*

### File List

*(to be filled by implementing agent upon completion)*

### Review Findings

- [x] [Review][Patch] `archive-label` missing `text-label-md` class [layouts/index.html:83] — Story Task 2 explicitly requires "Archive label with `.text-label-md` (intentionally uppercase)". Fixed: added `text-label-md` to span class.
- [x] [Review][Patch] `article-count-badge` CSS uses hardcoded hex instead of `var(--color-tertiary-fixed)` [static/css/index.css:555-556] — CSS tokens were added to `:root` specifically for this badge. Fixed: replaced `#ffdbcd`/`#360f00` with `var(--color-tertiary-fixed)`/`var(--color-on-tertiary-fixed)`.
- [x] [Review][Patch] `_default/list.html` date format hardcoded English [layouts/_default/list.html:15] — zh-tw list/section pages rendered English month names. Fixed: added language-conditional date format.
- [x] [Review][Defer] Document `<title>` vs H1 heading mismatch [layouts/partials/head.html] — deferred, pre-existing base template issue outside story scope.
- [x] [Review][Defer] Article count badge "1 articles" plural grammar [layouts/index.html] — deferred, no i18n plural infrastructure exists; out of this story's scope.
