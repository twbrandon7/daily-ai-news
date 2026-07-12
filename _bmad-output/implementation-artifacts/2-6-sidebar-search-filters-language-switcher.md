# Story 2.6: Sidebar Search, Filters & Language Switcher

Status: done

## Story

As a reader,
I want to filter articles by tags, search by title/tag, and toggle languages while keeping my active reading context,
so that I can quickly find relevant articles and compare translations.

## Context

Story 2.5 delivered `static/js/main.js` (vanilla JS IIFE) wiring the card-click switcher, and left two explicit placeholders for this story:

1. **Search input**: `<input ... disabled>` in `single.html` — disabled, no event listeners.
2. **Tag pills**: static `<span>` elements in `.sidebar-tags-section` — rendered by Hugo, no JS interaction.
3. **Language switcher**: `{{ block "lang-switcher" . }}<!-- Story 2.6 will implement language switcher -->{{ end }}` in `baseof.html` — placeholder block.

This story wires all three. **`static/js/main.js` is extended in-place** — the existing IIFE is not replaced.

## Acceptance Criteria

1. **Given** a daily post page with articles
   **When** I type a query into the search bar
   **Then** the sidebar article list instantly filters to cards whose `title` OR `tags_action` contain the query (case-insensitive substring match)
   **And** cards not matching are hidden (not removed from DOM)
   **And** the right detail panel retains whatever was last rendered.

2. **Given** the sidebar has tag filter pills
   **When** I click a tag pill
   **Then** the sidebar filters to articles that contain that exact tag
   **And** the clicked pill gains `.tag-pill--filter-active` visual state
   **And** clicking the same pill again deselects it and restores the full list.

3. **Given** both a search query and a tag pill are active simultaneously
   **Then** only articles matching BOTH the search query AND the tag are shown.

4. **Given** search/filter returns zero results
   **Then** a message "No matching articles found." (EN) or "找不到符合的文章或標籤。" (ZH-TW) appears
   **And** a "Clear search" / "清除搜尋" ghost button appears beside it
   **And** clicking the button resets both search and tag filter, restoring all cards.

5. **Given** the global site header on any page (homepage, detail, archive pagination)
   **Then** two ghost buttons [EN] and [TW] are visible, separated by a 1px vertical divider
   **And** the current language button has `.btn-ghost--active` style (primary-color border + faint tint)
   **And** each button's minimum click target is 44px (inherited from `.btn-ghost`).

6. **Given** I am on `/en/posts/2026-07-12/` with article index 3 active
   **When** I click [TW] in the header
   **Then** I am redirected to `/zh-tw/posts/2026-07-12/`
   **And** on load, the JS reads `localStorage` key `articleIdx_2026-07-12` and calls `activateCard(3)`
   **And** card 3 is highlighted and its content rendered in the detail panel.

7. **Given** `~/bin/hugo --minify` runs from project root
   **Then** exit code 0 with no ERRORs
   **And** `public/en/index.html` contains the EN/TW ghost button links.

8. **Given** `static/js/main.js` runs on a non-detail page (e.g., homepage)
   **Then** the bootstrap guard (`!dataEl → return`) fires before any filter/search/localStorage code runs — no errors.

## Tasks / Subtasks

- [ ] **Task 1**: Update `layouts/_default/single.html` — activate search + tag pills + empty state (AC: #1–#4, #7)
  - [ ] Remove the `disabled` attribute from `.sidebar-search-input` (line ~57)
  - [ ] In the `.sidebar-tags-section` loop, replace bare `<span class="tag-pill" ...>` with:
    ```gotemplate
    <span class="tag-pill tag-pill--filter"
          data-filter-tag="{{ . }}"
          role="button"
          tabindex="0"
          aria-pressed="false"
          style="background:rgba(0,74,198,0.08);color:var(--color-primary);">{{ . }}</span>
    ```
  - [ ] Add search empty state div directly after `</div>{{/* end .sidebar-article-list */}}` and before `</aside>`:
    ```gotemplate
    {{- $noResultsMsg := "No matching articles found." -}}
    {{- if eq .Site.Language.Lang "zh-tw" -}}{{- $noResultsMsg = "找不到符合的文章或標籤。" -}}{{- end -}}
    {{- $clearLabel := "Clear search" -}}
    {{- if eq .Site.Language.Lang "zh-tw" -}}{{- $clearLabel = "清除搜尋" -}}{{- end -}}
    <div class="sidebar-search-empty" id="sidebar-no-results" style="display:none;" aria-live="polite">
      <p>{{ $noResultsMsg }}</p>
      <button class="btn-ghost" id="sidebar-reset-search" type="button">{{ $clearLabel }}</button>
    </div>
    ```

- [ ] **Task 2**: Update `layouts/_default/baseof.html` — implement language switcher (AC: #5, #6, #7)
  - [ ] Replace the single `{{ block "lang-switcher" . }}<!-- Story 2.6 will implement language switcher -->{{ end }}` line with:
    ```gotemplate
          {{ block "lang-switcher" . }}
          {{- $currentLang := .Site.Language.Lang -}}
          {{- $enURL := .RelPermalink | replace "/zh-tw/" "/en/" -}}
          {{- $zhURL := .RelPermalink | replace "/en/" "/zh-tw/" -}}
          <a href="{{ $enURL }}"
             class="btn-ghost{{ if eq $currentLang "en" }} btn-ghost--active{{ end }}"
             hreflang="en"
             aria-label="{{ if eq $currentLang "en" }}English (current language){{ else }}Switch to English{{ end }}">EN</a>
          <span class="lang-switcher-divider" aria-hidden="true"></span>
          <a href="{{ $zhURL }}"
             class="btn-ghost{{ if eq $currentLang "zh-tw" }} btn-ghost--active{{ end }}"
             hreflang="zh-TW"
             aria-label="{{ if eq $currentLang "zh-tw" }}繁體中文（目前語言）{{ else }}切換至繁體中文{{ end }}">TW</a>
          {{ end }}
    ```
  - [ ] Verify: indentation matches surrounding code; no other line in `baseof.html` is changed

- [ ] **Task 3**: Extend `static/js/main.js` — search filter (AC: #1, #4, #8)
  - [ ] After `var lang = document.documentElement.lang;` (current line 18), insert the new state variables and DOM refs block (see Dev Notes — JS Insertion Block A)
  - [ ] After the `buildInsightsList` function (before `/* ── 3. Render article */`), insert the `filterArticles()` function (see Dev Notes — JS Insertion Block B)
  - [ ] In `activateCard()`, add `try { localStorage.setItem(storageKey, idx); } catch (e) {}` as the **last line before the closing `}`** of the function
  - [ ] After the existing card `cards.forEach` event listener block (after current line 165, before `}());`), insert the init + search + tag + reset event listener blocks (see Dev Notes — JS Insertion Block C)

- [ ] **Task 4**: Append CSS to `static/css/index.css` — lang-switcher + tag filter + search empty state (AC: #4, #5)
  - [ ] Append Section 36, 37, 38 to the end of `static/css/index.css` (see Dev Notes — CSS Appendix)
  - [ ] Do NOT modify any of Sections 1–35

- [ ] **Task 5**: Build & smoke-test verification (AC: #7, #8)
  - [ ] Run `~/bin/hugo --minify` from project root — confirm exit 0, no ERROR lines
  - [ ] Inspect `public/en/index.html` — confirm EN/TW buttons with `.btn-ghost` present in header
  - [ ] Inspect `public/en/posts/2026-07-12/index.html` — confirm search input has no `disabled`, tag pills have `data-filter-tag`, `sidebar-no-results` div is present
  - [ ] Confirm `public/zh-tw/index.html` header has TW button with `btn-ghost--active`

## Dev Notes

### Architecture Constraints (MUST follow)

- **AD-5 — Zero-Dependency JS**: `static/js/main.js` must remain a single vanilla-JS IIFE. No libraries. Use `var`, not `const`/`let` (for IE11 safety, consistent with existing code).
- **AD-6 — Append-only CSS**: Sections 1–35 of `static/css/index.css` are frozen. Only append new sections at the end.
- **Hugo binary**: `~/bin/hugo` (not system PATH). Version 0.128.0+.
- **`baseof.html` minimal change**: Only replace the lang-switcher placeholder. The `{{ block "lang-switcher" . }}...{{ end }}` wrapper **stays**; only the default content (the comment) is replaced.
- **`main.js` is extended, not replaced**: The existing IIFE grows. Do not restart the file from scratch.
- **Inline style on filter tag pills**: The template uses inline `style="..."` on sidebar tag pills. The `.tag-pill--filter-active` CSS rule must use `!important` to override this inline style when a tag is selected.

### Files to Create / Modify

| File | Action | Scope |
|---|---|---|
| `layouts/_default/single.html` | **MODIFY** | Remove `disabled`; add `data-filter-tag` + `tag-pill--filter` to sidebar pills; add `sidebar-no-results` div |
| `layouts/_default/baseof.html` | **MODIFY** | Replace lang-switcher comment with Hugo template inside existing `{{ block }}` |
| `static/js/main.js` | **MODIFY** | Add state vars, `filterArticles()`, localStorage save in `activateCard`, init + event listeners |
| `static/css/index.css` | **MODIFY** | Append Sections 36–38 only |

### Files to NOT Touch

- `layouts/index.html` — homepage layout; lang-switcher is inherited from `baseof.html`
- `layouts/_default/list.html` — archive list; same inheritance
- `src/pipeline.py` and all Epic 1 Python files
- `content/**/*.md` — pipeline-owned
- `.github/workflows/pipeline.yml`
- Any of CSS Sections 1–35

### Current State of `baseof.html` (exact diff reference)

**Before** (line 17):
```html
      {{ block "lang-switcher" . }}<!-- Story 2.6 will implement language switcher -->{{ end }}
```

**After**: replaced with the full block (see Task 2 above).

### Current State of Search Input in `single.html` (exact diff reference)

**Before** (lines 51–57):
```gotemplate
      <input
        class="sidebar-search-input"
        type="search"
        placeholder="{{ $searchPlaceholder }}"
        aria-label="{{ $searchPlaceholder }}"
        disabled
      >
```

**After** (remove the `disabled` line):
```gotemplate
      <input
        class="sidebar-search-input"
        type="search"
        placeholder="{{ $searchPlaceholder }}"
        aria-label="{{ $searchPlaceholder }}"
      >
```

### Current State of Sidebar Tag Pill Loop in `single.html` (exact diff reference)

**Before** (inside `.sidebar-tags-section` range loop):
```gotemplate
            <span class="tag-pill" style="background:rgba(0,74,198,0.08);color:var(--color-primary);">{{ . }}</span>
```

**After**:
```gotemplate
            <span class="tag-pill tag-pill--filter"
                  data-filter-tag="{{ . }}"
                  role="button"
                  tabindex="0"
                  aria-pressed="false"
                  style="background:rgba(0,74,198,0.08);color:var(--color-primary);">{{ . }}</span>
```

### Language Switcher URL Strategy

The Hugo `replace` function replaces all occurrences, but our URL structure means each lang prefix appears exactly once:
- `/en/` → `replace "/zh-tw/" "/en/"` (no-op on EN page, applied on ZH-TW page)
- `/zh-tw/` → `replace "/en/" "/zh-tw/"` (no-op on ZH-TW page, applied on EN page)

Works for all page types:
| Page type | EN URL | ZH-TW URL |
|---|---|---|
| Homepage | `/en/` | `/zh-tw/` |
| Detail | `/en/posts/2026-07-12/` | `/zh-tw/posts/2026-07-12/` |
| Paginated | `/en/page/2/` | `/zh-tw/page/2/` |

No fallback needed — our pipeline always creates both language files simultaneously.

### JS Insertion Block A — State variables & DOM refs

Insert **immediately after** `var lang = document.documentElement.lang; // "en" or "zh-tw"` (current line 18):

```javascript
  // ── localStorage key for article index (language-switch context preservation) ──
  var dateMatch  = window.location.pathname.match(/\/posts\/(\d{4}-\d{2}-\d{2})\//);
  var storageKey = 'articleIdx_' + (dateMatch ? dateMatch[1] : 'default');

  // ── Search / filter state ──
  var activeSearchQuery = '';
  var activeTagFilter   = '';

  // ── Additional DOM refs ──
  var searchInput = document.querySelector('.sidebar-search-input');
  var tagPills    = Array.prototype.slice.call(document.querySelectorAll('.tag-pill--filter'));
  var emptyState  = document.getElementById('sidebar-no-results');
  var resetBtn    = document.getElementById('sidebar-reset-search');
```

### JS Insertion Block B — filterArticles() function

Insert **after `buildInsightsList`** function body ends (before `/* ── 3. Render article */`):

```javascript
  /* ── 3. Filter sidebar articles (Story 2.6) ─────────── */
  function filterArticles() {
    var query = activeSearchQuery.toLowerCase().trim();
    var tag   = activeTagFilter.toLowerCase().trim();
    var count = 0;

    cards.forEach(function (card) {
      var idx = parseInt(card.getAttribute('data-article-index'), 10);
      var art = articles[idx];
      if (!art) { card.style.display = 'none'; return; }

      var inTitle = !query || art.title.toLowerCase().indexOf(query) !== -1;
      var inTags  = !query || (Array.isArray(art.tags_action) && art.tags_action.some(function (t) {
        return t.toLowerCase().indexOf(query) !== -1;
      }));
      var tagMatch = !tag || (Array.isArray(art.tags_action) && art.tags_action.some(function (t) {
        return t.toLowerCase() === tag;
      }));

      var show = (inTitle || inTags) && tagMatch;
      card.style.display = show ? '' : 'none';
      if (show) count++;
    });

    if (emptyState) emptyState.style.display = count === 0 ? '' : 'none';
  }
```

### JS Insertion Block C — Init, search, tag, reset event listeners

Insert **after the existing `cards.forEach` event-listener block** (after current closing `});` of that forEach, before the IIFE's `}());`):

```javascript
  /* ── 6. Restore saved article on language switch ─────── */
  (function () {
    var savedIdx = 0;
    try {
      var saved = localStorage.getItem(storageKey);
      if (saved !== null) {
        var parsed = parseInt(saved, 10);
        if (!isNaN(parsed) && parsed > 0 && parsed < articles.length) {
          savedIdx = parsed;
        }
      }
    } catch (e) {}
    if (savedIdx > 0) activateCard(savedIdx);
  }());

  /* ── 7. Search input ─────────────────────────────────── */
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      activeSearchQuery = searchInput.value;
      filterArticles();
    });
  }

  /* ── 8. Tag pill filter ──────────────────────────────── */
  tagPills.forEach(function (pill) {
    pill.style.cursor = 'pointer';
    function toggleTag() {
      var tag = (pill.getAttribute('data-filter-tag') || '').toLowerCase();
      if (activeTagFilter === tag) {
        // Deselect current tag filter
        activeTagFilter = '';
        tagPills.forEach(function (p) {
          p.classList.remove('tag-pill--filter-active');
          p.setAttribute('aria-pressed', 'false');
        });
      } else {
        activeTagFilter = tag;
        tagPills.forEach(function (p) {
          var active = (p.getAttribute('data-filter-tag') || '').toLowerCase() === tag;
          p.classList.toggle('tag-pill--filter-active', active);
          p.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
      }
      filterArticles();
    }
    pill.addEventListener('click', toggleTag);
    pill.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleTag(); }
    });
  });

  /* ── 9. Reset search / filter ────────────────────────── */
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      activeSearchQuery = '';
      activeTagFilter   = '';
      if (searchInput) searchInput.value = '';
      tagPills.forEach(function (p) {
        p.classList.remove('tag-pill--filter-active');
        p.setAttribute('aria-pressed', 'false');
      });
      filterArticles();
    });
  }
```

### JS: Modified `activateCard()` function

Add `try { localStorage.setItem(storageKey, idx); } catch (e) {}` as the last line inside the function body (before the closing `}`):

```javascript
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
    try { localStorage.setItem(storageKey, idx); } catch (e) {} // Story 2.6: persist for lang-switch
  }
```

### CSS Appendix — Sections 36–38 (append to end of `static/css/index.css`)

```css
/* ============================================================
   36. Language switcher (.lang-switcher-divider, .btn-ghost--active)
   ============================================================ */

/* Active state for current-language ghost button */
.btn-ghost--active {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(0, 74, 198, 0.05);
}

/* Thin vertical divider between EN and TW buttons */
.lang-switcher-divider {
  display: inline-block;
  width: 1px;
  height: 20px;
  background: var(--color-border-low);
  margin: 0 2px;
  align-self: center;
}

/* ============================================================
   37. Tag filter active state (.tag-pill--filter-active)
   ============================================================ */

/* !important required to override the inline style="..." on sidebar tag pills */
.tag-pill--filter-active {
  background: var(--color-primary) !important;
  color: #ffffff !important;
}

/* ============================================================
   38. Sidebar search empty state (.sidebar-search-empty)
   ============================================================ */

.sidebar-search-empty {
  padding: var(--spacing-md);
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-body-md);
  line-height: var(--lh-body-md);
  color: var(--color-on-surface-variant);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}
```

### Previous Story Intelligence (Story 2.5)

Key learnings from Story 2.5 code review that apply here:

- **`</script>` injection fix**: `single.html` already applies `replace "</" "\\/" | safeHTML` to the JSON data block. **Do not change this**; our new template changes are not in a `<script>` block.
- **`javascript:`/`data:` URI guard**: `main.js` guards source URLs with `/^https?:\/\//i`. This story's new code does not generate `<a href>` with user-controlled data, so no additional URL sanitisation is needed.
- **Array type guards**: Story 2.5 fixed `!Array.isArray(tags)` checks. The new `filterArticles()` must also guard `tags_action` with `Array.isArray()` — see JS Insertion Block B (already included).
- **ARIA `aria-selected` violation deferred**: Story 2.5 deferred the `role="listbox"` refactor. **Do not attempt to fix this** in Story 2.6.
- **`var` not `const/let`**: Consistent with existing code style in `main.js`.

### UX Requirements Coverage

| Requirement | Source | Implementation |
|---|---|---|
| UX-DR-5: Client-side JS in `static/js/main.js` | DESIGN.md | Extended IIFE, no new file |
| UX-DR-6: Ghost button EN/TW in header, preserves date + article | DESIGN.md | `baseof.html` block + localStorage |
| FR-7: Persistent nav header with language toggle | epics.md | `baseof.html` global header |
| EXPERIENCE.md: Tag pill click filters article list | EXPERIENCE.md | `filterArticles()` with tag state |
| EXPERIENCE.md: Search empty state with reset button | EXPERIENCE.md | `sidebar-no-results` + `sidebar-reset-search` |
| EXPERIENCE.md: Language switch preserves date + article | EXPERIENCE.md | localStorage `articleIdx_YYYY-MM-DD` |
| NFR-6: 44px min click target on language buttons | epics.md | Inherited from `.btn-ghost { min-height: 44px }` |

### Project Structure Notes

- `layouts/partials/` directory exists but is **not required** for this story — the lang-switcher implementation lives directly in the `{{ block }}` default content in `baseof.html`. Creating a partial is a valid alternative but adds an extra file with no benefit at current scale.
- The `.sidebar-search-input` is queried in JS by class. If `.sidebar-search-input` is absent on a non-detail page (homepage), `searchInput` will be `null` and the `if (searchInput)` guard will skip it safely (AC #8).
- The `localStorage.setItem` calls are wrapped in `try/catch` to handle browsers in private mode where localStorage throws on write.

### References

- `static/js/main.js` — full current implementation (vanilla IIFE, 167 lines)
- `layouts/_default/single.html` — current template with `disabled` search input and tag pills
- `layouts/_default/baseof.html` — `{{ block "lang-switcher" }}` placeholder (line 17)
- `static/css/index.css` Section 10 (`.btn-ghost`), Section 12 (`.tag-pill`), Section 14 (`.active-card-indicator`) — all pre-existing, do not modify
- `_bmad-output/implementation-artifacts/2-5-interactive-javascript-switcher-integration.md` — previous story with full JS architecture and review findings
- `_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/EXPERIENCE.md` — State Patterns table (Search Empty state, Language Switch state)
- `_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/DESIGN.md` — Components section ("Language switchers (EN/TW) are styled as ghost buttons with a subtle divider")

## Dev Agent Record

### Agent Model Used

claude-sonnet-4.6 (bmad-agent-dev, story creation run 2026-07-12)

### Debug Log References

### Completion Notes List

### File List

## Review Findings

*Code review performed by Amelia (bmad-agent-dev) — 2026-07-12*

- [x] [Review][Patch] Null `art.title` crashes `filterArticles()` [static/js/main.js:86] — fixed: `String(art.title || '').toLowerCase()`
- [x] [Review][Patch] Null/non-string tag item crashes `.some()` in `filterArticles()` [static/js/main.js:87-92] — fixed: `tagList` pre-filtered with `typeof t === 'string'`
- [x] [Review][Patch] Duplicate `/* ── 6. */` section comment label [static/js/main.js:195,209] — fixed: renumbered restore→7, search→8, tag→9, reset→10
