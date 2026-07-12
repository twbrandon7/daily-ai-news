# Story 2.5: Interactive JavaScript Switcher Integration

Status: done

## Story

As a reader,
I want clicking an article card in the sidebar to instantly load its summary on the right without reloading the page,
so that the reading experience is fast and smooth.

## Context

Story 2.4 delivered the **fully static** split-pane detail layout for `/en/posts/YYYY-MM-DD/`. The `layouts/_default/single.html` template renders all article cards in the left sidebar and the **first article by default** in the right panel — all via Hugo server-side rendering. No JavaScript exists yet.

This story wires up the interactivity layer:
- **Hugo template update** — embed all article data as JSON and add `data-article-index` attributes so JS can target each card.
- **`static/js/main.js` creation** — the switcher that listens for card clicks and re-renders the right panel from the embedded JSON, without any page reload.
- **`layouts/_default/baseof.html` update** — replace the `<!-- Story 2.5 will add js/main.js -->` placeholder comment with the real `<script>` tag.

**No new CSS is needed for the active-card visual state** — `.active-card-indicator` was defined in Section 14 of `static/css/index.css` during Story 2.2 (`border-left: 3px solid var(--color-primary); background: rgba(0, 74, 198, 0.05);`). The JS will simply add/remove this class.

The sidebar search input remains `disabled` in this story — search and tag filtering are owned by Story 2.6.

## Acceptance Criteria

1. **Given** a daily post page (`/en/posts/YYYY-MM-DD/` or `/zh-tw/posts/YYYY-MM-DD/`) with two or more articles in the frontmatter `articles` array
   **When** the page loads
   **Then** the right detail panel shows the first article's full content (same as Story 2.4 static default)
   **And** the first sidebar card has the `.active-card-indicator` class applied.

2. **Given** the page has loaded
   **When** I click a sidebar article card (index ≥ 1)
   **Then** the right detail panel is immediately replaced with the clicked article's full content (all 5 elements: TL;DR, Problem/Why, Solution/How, Insights & Trade-offs, Tags & Action, source link) — **without any page reload**
   **And** the clicked card receives the `.active-card-indicator` class
   **And** the previously active card loses the `.active-card-indicator` class.

3. **Given** I have switched to a non-first article
   **When** I click the first sidebar card again
   **Then** the right panel reverts to displaying the first article's content
   **And** only the first card has the `.active-card-indicator` class.

4. **Given** a sidebar card has `tabindex="0"` and focus
   **When** I press `Enter` or `Space`
   **Then** the same article-switch behaviour fires as a mouse click (keyboard accessibility).

5. **Given** the active card indicator
   **Then** it renders as a `3px left border` using `var(--color-primary)` and a `rgba(0, 74, 198, 0.05)` background tint (provided by the pre-existing `.active-card-indicator` CSS class — no new CSS needed).

6. **Given** a daily post page with zero articles (`articles: []` or missing)
   **When** the page loads
   **Then** JS finds no article data and exits silently — the static empty-state HTML rendered by Hugo is shown intact.

7. **Given** `~/bin/hugo --minify` runs from the project root
   **Then** the build exits 0 with no ERRORs
   **And** `public/en/posts/2026-07-12/index.html` contains the `id="articles-data"` JSON script element
   **And** `public/en/posts/2026-07-12/index.html` contains `data-article-index="0"` on the first sidebar card.

8. **Given** `static/js/main.js` is loaded on every page (via `baseof.html`)
   **When** the JS runs on a page that does **not** have `#articles-data` (e.g., the homepage archive)
   **Then** it exits immediately without errors or console warnings.

## Tasks / Subtasks

- [ ] **Task 1**: Update `layouts/_default/single.html` — embed JSON data + add data attributes (AC: #1, #2, #6, #7)
  - [ ] In the sidebar article card loop, add `data-article-index="{{ $idx }}"` and `tabindex="0"` and `aria-selected="{{ if eq $idx 0 }}true{{ else }}false{{ end }}"` to each `.sidebar-article-card` div
  - [ ] After the closing `</div>{{/* end .detail-layout */}}` and before `</main>`, inject the articles JSON block:
    ```gotemplate
    {{/* ── Embedded article data for JS switcher ─────────── */}}
    {{ if $articles }}
    <script type="application/json" id="articles-data">{{ .Params.articles | jsonify }}</script>
    {{ end }}
    ```
  - [ ] Verify: the existing `{{ range $idx, $art := $articles }}` loop structure is preserved; only the opening `<div class="sidebar-article-card...">` tag changes

- [ ] **Task 2**: Update `layouts/_default/baseof.html` — replace placeholder with script tag (AC: #7, #8)
  - [ ] Replace the line `  <!-- Story 2.5 will add js/main.js -->` with:
    ```html
      <script src="{{ "js/main.js" | relURL }}" defer></script>
    ```
  - [ ] Keep the `defer` attribute — this ensures DOM is ready before JS runs

- [ ] **Task 3**: Create `static/js/main.js` — article switcher (AC: #1–#6, #8)
  - [ ] **Bootstrap guard**: read `document.getElementById('articles-data')`; if null, `return` immediately (safe on all non-detail pages)
  - [ ] **Parse JSON**: `JSON.parse(dataEl.textContent)` — if empty/null array, return
  - [ ] **Query DOM elements**: `.sidebar-article-card[data-article-index]` (all cards), `.detail-panel` (right panel target), `document.documentElement.lang` for i18n
  - [ ] **`renderArticle(article, lang)` function**: build inner HTML for `.detail-panel` matching the existing Hugo template structure exactly (see Dev Notes for the full HTML skeleton and CSS classes to use)
  - [ ] **`activateCard(idx)` function**: remove `.active-card-indicator` + `aria-selected="false"` from all cards, add `.active-card-indicator` + `aria-selected="true"` to card at `data-article-index=idx`, call `renderArticle(articles[idx], lang)`
  - [ ] **Event listeners**: for each card — `click` event calls `activateCard(parseInt(card.dataset.articleIndex, 10))`, `keydown` event handles `Enter` and `Space` keys (prevent default + call activateCard)
  - [ ] **Cursor style**: set `card.style.cursor = 'pointer'` on each card during init

- [ ] **Task 4**: Build and runtime verification (AC: #7, #8)
  - [ ] Run `~/bin/hugo --minify` from project root — confirm exit code 0 and no ERROR lines
  - [ ] Confirm `public/en/posts/2026-07-12/index.html` contains `id="articles-data"` and `data-article-index="0"`
  - [ ] Confirm `public/en/posts/2026-07-12/index.html` contains `<script src="/en/js/main.js"` (or `/js/main.js` for the language root)
  - [ ] Confirm `public/index.html` (homepage) does NOT break — open the file and verify no unexpected JS errors would occur (no `id="articles-data"` element on homepage = JS guard works)
  - [ ] Manual smoke test: open `public/en/posts/2026-07-12/index.html` in a browser (or simulate via `python3 -m http.server` from `public/`), click sidebar cards, verify right panel content switches

### Review Findings

- [x] [Review][Patch] `</script>` injection in JSON embedding — `safeHTML` bypass allows article content containing `</script>` to break out of the `<script type="application/json">` block, enabling HTML injection. Fixed by piping `jsonify` output through `replace "</" "\\/"` before `safeHTML`. [layouts/_default/single.html:236]
- [x] [Review][Patch] `javascript:`/`data:` URI not validated in source link — `esc()` HTML-encodes but does not block non-`http(s)` protocol URIs injected into `<a href>`. Fixed by adding `/^https?:\/\//i` guard before rendering the link. [static/js/main.js:128]
- [x] [Review][Patch] `tags_action` array not type-guarded — `buildTagPills` accepted truthy non-array values (e.g. a string), bypassing the falsy guard and causing a `.map()` TypeError. Fixed by replacing `!tags || tags.length === 0` with `!Array.isArray(tags) || tags.length === 0`. [static/js/main.js:46]
- [x] [Review][Patch] `pros`/`cons` array not type-guarded — `buildInsightsList` had the same non-array flaw. Fixed by replacing `!items || items.length === 0` with `!Array.isArray(items) || items.length === 0`. [static/js/main.js:53]
- [x] [Review][Defer] `aria-selected` on `role="listitem"` elements (ARIA spec violation) — `aria-selected` is only valid on option/row/tab/treeitem/gridcell roles. Requires sidebar to be refactored as a `role="listbox"` with `role="option"` cards; architectural change outside this story's scope — deferred

## Dev Notes

### Architecture Constraints (MUST follow)

- **AD-5 — Zero-Dependency Custom Hugo Layouts**: No external JS libraries. `static/js/main.js` must be **vanilla JS only** — no jQuery, no Alpine.js, no framework imports. The file must be a single self-contained IIFE.
- **AD-6 — Structured Frontmatter Storage**: All article data in Hugo comes from `.Params.articles`. The `jsonify` filter serializes the Go slice directly — field names will match the YAML frontmatter keys exactly (lowercase, underscored). See schema below.
- **CSS append-only contract**: Sections 1–36 in `static/css/index.css` are a downstream contract. **Do NOT touch `static/css/index.css` in this story** — `.active-card-indicator` (Section 14) is already fully correct.
- **Hugo binary**: `~/bin/hugo` (NOT on system PATH). Hugo version 0.128.0+.
- **`baseof.html` minimal change**: Only replace the single comment line — do not restructure or change anything else in this file. It is the foundation template for all pages.

### Files to Create / Modify

| File | Action | Notes |
|---|---|---|
| `layouts/_default/single.html` | **MODIFY** | Add `data-article-index`, `tabindex`, `aria-selected` to sidebar card divs; add JSON data script block at end of main |
| `layouts/_default/baseof.html` | **MODIFY** | Replace placeholder comment with `<script src="..." defer>` |
| `static/js/main.js` | **CREATE** | Vanilla JS IIFE — full switcher implementation |

### Files to NOT Touch

- `static/css/index.css` — `.active-card-indicator` already correct in Section 14; no CSS changes needed
- `src/pipeline.py`, `src/summarizer.py`, `src/translator.py`, `src/publisher.py` — Epic 1, complete
- `layouts/index.html`, `layouts/_default/list.html` — Epic 2 stories 2.3 done
- `content/**/*.md` — pipeline-owned (Story 1.5)
- `data/blogs.yaml`, `data/fetched_posts.json` — pipeline-owned
- `.github/workflows/pipeline.yml` — Epic 1, complete
- Sections 1–36 of `static/css/index.css` — complete, do not append further in this story

### Article Frontmatter JSON Schema (what `jsonify` produces)

Hugo's `jsonify` serializes `.Params.articles` with these exact lowercase keys:

```json
[
  {
    "title": "Article Title",
    "url": "https://example.com/article",
    "tldr": "One-sentence summary.",
    "problem_why": "Problem description.",
    "solution_how": "Solution description.",
    "insights_tradeoffs": {
      "pros": ["Strength 1", "Strength 2"],
      "cons": ["Trade-off 1", "Trade-off 2"]
    },
    "tags_action": ["LLM", "RAG", "fine-tuning"],
    "rating": 4
  }
]
```

**Key facts for JS:**
- `insights_tradeoffs.pros` and `insights_tradeoffs.cons` are arrays of strings
- `tags_action` is an array of strings
- `rating` is an integer 1–5 (default 3 if missing — use `article.rating || 3` in JS)
- `url` may be an empty string — guard with `if (article.url)` before rendering source link

### `single.html` Sidebar Card Diff (exact change)

**Before** (current Task 2 from Story 2.4):
```gotemplate
<div class="sidebar-article-card{{ if eq $idx 0 }} active-card-indicator{{ end }}" role="listitem">
```

**After** (this story):
```gotemplate
<div class="sidebar-article-card{{ if eq $idx 0 }} active-card-indicator{{ end }}"
     role="listitem"
     data-article-index="{{ $idx }}"
     tabindex="0"
     aria-selected="{{ if eq $idx 0 }}true{{ else }}false{{ end }}">
```

### `single.html` JSON Data Block to Append

Add this block **inside `{{ define "main" }}`**, directly before `</main>`, after the `</div>{{/* end .detail-layout */}}` closing tag:

```gotemplate
{{/* ── Embedded article data for JS switcher (Story 2.5) ─── */}}
{{ if $articles }}
<script type="application/json" id="articles-data">{{ .Params.articles | jsonify }}</script>
{{ end }}
```

### `baseof.html` Change (exact diff)

**Before** (line 24):
```html
  <!-- Story 2.5 will add js/main.js -->
```

**After**:
```html
  <script src="{{ "js/main.js" | relURL }}" defer></script>
```

### `static/js/main.js` — Detailed Implementation Spec

The JS must generate HTML that **exactly matches** the CSS class structure from `single.html` / `static/css/index.css`. Below are the full HTML skeletons each section must produce:

#### Full JS file structure

```javascript
(function () {
  'use strict';

  /* ── 1. Bootstrap guard ──────────────────────────────── */
  var dataEl = document.getElementById('articles-data');
  if (!dataEl) return;

  var articles;
  try { articles = JSON.parse(dataEl.textContent); } catch (e) { return; }
  if (!articles || articles.length === 0) return;

  var cards = Array.prototype.slice.call(
    document.querySelectorAll('.sidebar-article-card[data-article-index]')
  );
  var detailPanel = document.querySelector('.detail-panel');
  if (!detailPanel || cards.length === 0) return;

  var lang = document.documentElement.lang; // "en" or "zh-tw"

  /* ── 2. Helpers ──────────────────────────────────────── */
  function esc(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  var STAR_FILLED = '<svg class="rating-star rating-star--filled" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/></svg>';
  var STAR_EMPTY  = '<svg class="rating-star rating-star--empty"  viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M22 9.74l-7.19-.62L12 2.5 9.19 9.13 2 9.74l5.46 4.73-1.64 7.03L12 17.77l6.18 3.73-1.63-7.03L22 9.74zM12 15.9l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.8l1.71 4.64 4.38.38-3.32 2.88 1 4.28L12 15.9z"/></svg>';
  var EXTERNAL_ICON = '<svg class="source-link-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 19H5V5h7V3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/></svg>';

  function buildStars(rating) {
    var r = parseInt(rating, 10) || 3;
    var label = lang === 'zh-tw'
      ? '5 顆星中的 ' + r + ' 顆'
      : r + ' out of 5 stars';
    var html = '<div class="rating-stars" aria-label="' + esc(label) + '">';
    for (var i = 1; i <= 5; i++) {
      html += i <= r ? STAR_FILLED : STAR_EMPTY;
    }
    return html + '</div>';
  }

  function buildTagPills(tags, cssClass, style) {
    if (!tags || tags.length === 0) return '';
    return tags.map(function (t) {
      return '<span class="tag-pill ' + cssClass + '"' + (style ? ' style="' + style + '"' : '') + '>' + esc(t) + '</span>';
    }).join('');
  }

  function buildInsightsList(items) {
    if (!items || items.length === 0) return '';
    return '<ul class="insights-list">' +
      items.map(function (item) {
        return '<li class="insights-item">' + esc(item) + '</li>';
      }).join('') +
    '</ul>';
  }

  /* ── 3. Render article to detail panel ───────────────── */
  function renderArticle(article) {
    var isTw = lang === 'zh-tw';

    // Labels
    var labelProblem   = isTw ? '問題 / 背景' : 'Problem / Why';
    var labelSolution  = isTw ? '解法 / 方法' : 'Solution / How';
    var labelInsights  = isTw ? '洞察與取捨'  : 'Insights & Trade-offs';
    var labelPros      = isTw ? '✓ 優點'      : '✓ Strengths';
    var labelCons      = isTw ? '⚠ 取捨'      : '⚠ Trade-offs';
    var labelTags      = isTw ? '標籤與行動'  : 'Tags & Action';
    var labelLink      = isTw ? '原文連結'    : 'Original Link';
    var srcAriaLabel   = isTw
      ? '原文連結：' + (article.title || '')
      : 'Original Link: ' + (article.title || '');

    var pros = (article.insights_tradeoffs || {}).pros || [];
    var cons = (article.insights_tradeoffs || {}).cons || [];

    var html = '';

    // Article header
    html += '<header class="article-panel-header">';
    html += '<h1 class="article-panel-title text-headline-lg">' + esc(article.title) + '</h1>';
    html += buildStars(article.rating);
    html += '</header>';

    // TL;DR
    html += '<div class="tldr-box">';
    html += '<span class="tldr-label">TL;DR</span>';
    html += '<p class="tldr-text">' + esc(article.tldr) + '</p>';
    html += '</div>';

    // Problem / Why
    html += '<div class="summary-section">';
    html += '<span class="summary-section-label">' + esc(labelProblem) + '</span>';
    html += '<p class="summary-section-body">' + esc(article.problem_why) + '</p>';
    html += '</div>';

    // Solution / How
    html += '<div class="summary-section">';
    html += '<span class="summary-section-label">' + esc(labelSolution) + '</span>';
    html += '<p class="summary-section-body">' + esc(article.solution_how) + '</p>';
    html += '</div>';

    // Insights & Trade-offs
    html += '<div class="insights-section">';
    html += '<span class="insights-section-label">' + esc(labelInsights) + '</span>';
    html += '<div class="insights-grid">';
    html += '<div class="insights-col insights-col--pros">';
    html += '<span class="insights-col-header">' + esc(labelPros) + '</span>';
    html += buildInsightsList(pros);
    html += '</div>';
    html += '<div class="insights-col insights-col--cons">';
    html += '<span class="insights-col-header">' + esc(labelCons) + '</span>';
    html += buildInsightsList(cons);
    html += '</div>';
    html += '</div></div>';

    // Tags & Action
    html += '<div class="tags-action-section">';
    html += '<span class="tags-action-label">' + esc(labelTags) + '</span>';
    html += '<div class="tags-action-list">';
    html += buildTagPills(article.tags_action, 'tag-pill--primary', '');
    html += '</div></div>';

    // Source link (only if url present)
    if (article.url) {
      html += '<div class="source-link-row">';
      html += '<a class="source-link" href="' + esc(article.url) + '" target="_blank" rel="noopener noreferrer" aria-label="' + esc(srcAriaLabel) + '">';
      html += EXTERNAL_ICON;
      html += esc(labelLink);
      html += '</a></div>';
    }

    detailPanel.innerHTML = html;
  }

  /* ── 4. Activate card and render ─────────────────────── */
  function activateCard(idx) {
    cards.forEach(function (card) {
      card.classList.remove('active-card-indicator');
      card.setAttribute('aria-selected', 'false');
    });
    var target = document.querySelector('[data-article-index="' + idx + '"]');
    if (target) {
      target.classList.add('active-card-indicator');
      target.setAttribute('aria-selected', 'true');
    }
    if (articles[idx]) renderArticle(articles[idx]);
  }

  /* ── 5. Attach event listeners ───────────────────────── */
  cards.forEach(function (card) {
    card.style.cursor = 'pointer';
    card.addEventListener('click', function () {
      activateCard(parseInt(card.getAttribute('data-article-index'), 10));
    });
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activateCard(parseInt(card.getAttribute('data-article-index'), 10));
      }
    });
  });

}());
```

### SVG Paths Reference (same as `single.html` — do not alter)

| Icon | Path |
|---|---|
| Star filled | `M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z` |
| Star empty | `M22 9.74l-7.19-.62L12 2.5 9.19 9.13 2 9.74l5.46 4.73-1.64 7.03L12 17.77l6.18 3.73-1.63-7.03L22 9.74zM12 15.9l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.8l1.71 4.64 4.38.38-3.32 2.88 1 4.28L12 15.9z` |
| External link | `M19 19H5V5h7V3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z` |

### Existing CSS Classes Used by JS-Rendered HTML (DO NOT redefine)

All CSS classes referenced in `renderArticle()` are already present in `static/css/index.css`. The JS must use them exactly:

| CSS Class | Defined In | Purpose |
|---|---|---|
| `.article-panel-header` | Section 28 | Article header wrapper |
| `.article-panel-title` | Section 28 | `<h1>` title |
| `.rating-stars` | Section 32 | Star row container |
| `.rating-star`, `.rating-star--filled`, `.rating-star--empty` | Section 32 | Individual star SVGs |
| `.tldr-box`, `.tldr-label`, `.tldr-text` | Section 29 | TL;DR accent block |
| `.summary-section`, `.summary-section-label`, `.summary-section-body` | Section 30 | Problem/Solution cards |
| `.insights-section`, `.insights-section-label`, `.insights-grid` | Section 31 | Insights wrapper + 2-col grid |
| `.insights-col`, `.insights-col--pros`, `.insights-col--cons` | Section 31 | Pros/cons columns |
| `.insights-col-header`, `.insights-list`, `.insights-item` | Section 31 | Column internals |
| `.tags-action-section`, `.tags-action-label`, `.tags-action-list` | Section 33 | Tags section |
| `.tag-pill`, `.tag-pill--primary` | Section 5 / 33 | Tag pill styles |
| `.source-link-row`, `.source-link`, `.source-link-icon` | Section 34 | Source link row |
| `.active-card-indicator` | Section 14 | 3px primary left border + 5% tint |

### Previous Story Learnings (from Story 2.4 Review)

- **`.active-card-indicator` must NOT be redefined** — it lives in Section 14 and is correct. Simply add/remove it as a class on sidebar card divs.
- **Inline styles on sidebar tag pills are a deferred issue** — Story 2.4 review flagged this but explicitly deferred to Story 2.5. For the sidebar cards (`.sidebar-article-card`), the tag pills use inline styles (`style="background:..."`). This story does **not** need to fix this either — it only affects cards already in the static HTML, not the JS-rendered right panel.
- **`{{ with $a.url }}` guard** — the source link must only render if `url` is non-empty. The JS equivalent is `if (article.url)`.
- **Rating star aria-label must be i18n-aware** — use `lang === 'zh-tw'` check in `buildStars()`.
- **`.Site.Language.Lang` in Hugo is `zh-tw` (lowercase)** — the `<html lang="...">` attribute set in `baseof.html` mirrors this, so `document.documentElement.lang` returns `"zh-tw"`.
- **Hugo's `jsonify` is safe for embedding in `<script type="application/json">`** — it produces valid JSON. Hugo automatically HTML-escapes the output in an HTML context, but inside a `<script type="application/json">` it outputs raw JSON, which is what we want.

### Git History Context

The last two commits (`c8d0b2c`, `c68c33e`) confirm:
- `layouts/_default/single.html` was fully replaced with the Story 2.4 implementation
- `layouts/_default/baseof.html` has the placeholder comment at line 24
- `static/js/.gitkeep` exists but `static/js/main.js` does not

### Hugo `relURL` for JS Script Tag

In `baseof.html`, use `{{ "js/main.js" | relURL }}`. Hugo will resolve this to:
- `/js/main.js` (for root-level language or default)
- `/en/js/main.js` for English if the site uses language-prefixed URLs

Since `static/` assets are copied as-is to `public/`, the actual file at `public/js/main.js` will be served correctly regardless of the language prefix in the URL.

> **Note:** `relURL` (not `relLangURL`) is correct here — JS files are not language-specific. Using `relLangURL` would incorrectly produce `/en/js/main.js` for English pages, pointing to a non-existent file.
