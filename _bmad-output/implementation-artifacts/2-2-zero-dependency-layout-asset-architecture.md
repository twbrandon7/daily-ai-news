# Story 2.2: Zero-Dependency Layout & Asset Architecture

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a reader,
I want the static site styled with a premium, zero-dependency layout matching the styling system,
So that the interface feels professional, clean, and highly readable.

## Acceptance Criteria

1. **Given** brand colors, typography (Inter), and layout units in `DESIGN.md`
2. **When** the CSS is compiled in `static/css/index.css` and loaded by Hugo layouts
3. **Then** the UI elements render with low-contrast borders (1px `#e2e8f0`), rounded corners (4px standard, 8px large), canvas background `#f7f9fb`, and correct typography scales.
4. **And** all CSS custom properties (design tokens) match the values in `DESIGN.md` exactly.
5. **And** Inter typeface is loaded from Google Fonts in `layouts/_default/baseof.html` and applied globally.
6. **And** `static/css/index.css` defines all design tokens, typography scale, tonal-layer elevation rules, spacing primitives, and base component shell styles (global header, card, tag pill, button).
7. **And** the Hugo site still builds with `hugo --minify` from the project root with exit code 0 and no ERRORs.
8. **And** no external Hugo themes, Tailwind CDN, or external CSS frameworks are referenced anywhere in `layouts/` or `static/`.

## Tasks / Subtasks

- [x] Task 1: Create `static/css/index.css` — design token layer (AC: #2, #3, #4)
  - [x] Remove (or replace) the existing `static/css/.gitkeep` placeholder — the `.gitkeep` must be deleted and replaced with the real `index.css` file.
  - [x] Declare all CSS custom properties under `:root` matching every color, typography, spacing, border-radius, and shadow value from `DESIGN.md` (see **Dev Notes → Token Reference** below).
  - [x] Include a minimal CSS reset (box-sizing border-box, margin/padding 0, `inherit` font).

- [x] Task 2: Add typography scale to `static/css/index.css` (AC: #3, #5, #6)
  - [x] Define `.text-headline-xl`, `.text-headline-lg`, `.text-headline-lg-mobile`, `.text-headline-md`, `.text-body-lg`, `.text-body-md`, `.text-label-md`, `.text-label-sm` utility classes using the token values.
  - [x] Apply `font-family: var(--font-inter), sans-serif` as the global body font.

- [x] Task 3: Add tonal layering utilities to `static/css/index.css` (AC: #3, #6)
  - [x] Implement `.layer-0` (canvas, `background: var(--color-background)`).
  - [x] Implement `.layer-1` (cards/sidebar, `background: #ffffff; border: 1px solid var(--color-border-low)`).
  - [x] Implement `.layer-2` (active dropdowns, `background: #ffffff; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05)`).
  - [x] Implement `.interactive-hover` (sidebar card hover: `background: #f1f5f9`, transition 200ms).

- [x] Task 4: Add layout primitives to `static/css/index.css` (AC: #6)
  - [x] Implement `.container` — max-width 1440px, margin auto, horizontal padding 24px.
  - [x] Implement `.grid-12` — CSS Grid with 12 columns and `gap: var(--spacing-xl)`.
  - [x] Implement `.col-4` (4 of 12 columns) and `.col-8` (8 of 12 columns) for the split-pane layout (Stories 2.3–2.4 will use these).
  - [x] Add responsive collapse: on screens < 768px, `.grid-12 .col-4` and `.grid-12 .col-8` each expand to full width (12 columns / single column stack).

- [x] Task 5: Add base component shell styles to `static/css/index.css` (AC: #6)
  - [x] `.site-header` — `position: fixed; top: 0; width: 100%; height: 64px; background: #ffffff; border-bottom: 1px solid var(--color-border-low); z-index: 50; display: flex; align-items: center; justify-content: space-between; padding: 0 var(--spacing-lg)`.
  - [x] `.site-header .site-title` — `font-size: var(--fs-headline-md); font-weight: 600; color: var(--color-primary); text-decoration: none`.
  - [x] `.btn-ghost` — ghost button style for the EN/TW switcher: transparent background, `color: var(--color-on-surface-variant)`, `padding: var(--spacing-xs) var(--spacing-sm)`, `border: 1px solid transparent`, `border-radius: var(--radius-default)`, hover brightens border.
  - [x] `.card` — base card: `background: #ffffff; border: 1px solid var(--color-border-low); border-radius: var(--radius-lg); padding: var(--spacing-lg)`.
  - [x] `.tag-pill` — tag pill: `display: inline-flex; align-items: center; padding: 2px var(--spacing-sm); border-radius: var(--radius-full); font-size: var(--fs-label-sm); font-weight: 500; line-height: var(--lh-label-sm)`.
  - [x] `.site-content` — main content wrapper: `padding-top: 64px; min-height: 100vh; background: var(--color-background)`. (The 64px offset accounts for the fixed header.)
  - [x] `.active-card-indicator` — sidebar active article card indicator: `border-left: 3px solid var(--color-primary); background: rgba(0, 74, 198, 0.05)`.

- [x] Task 6: Update `layouts/_default/baseof.html` — wire Inter font & semantic header (AC: #5, #7, #8)
  - [x] Add the Google Fonts `<link>` for Inter in the `<head>` **before** `index.css`: `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap`.
  - [x] Add `<link rel="preconnect" href="https://fonts.googleapis.com">` and `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` before the Inter link for performance.
  - [x] Set `<body class="layer-0">` so the canvas background token is applied globally.
  - [x] Replace the bare `{{ block "main" . }}{{ end }}` body with a semantic scaffold:
    ```html
    <header class="site-header">
      {{ block "header" . }}
      <a href="{{ "/" | relLangURL }}" class="site-title">{{ .Site.Title }}</a>
      <div class="header-actions">
        {{ block "lang-switcher" . }}<!-- Story 2.6 will fill this -->{{ end }}
      </div>
      {{ end }}
    </header>
    <div class="site-content">
      {{ block "main" . }}{{ end }}
    </div>
    ```
  - [x] Keep the existing `<link rel="stylesheet" href="{{ "css/index.css" | relURL }}">` and `<script src="{{ "js/main.js" | relURL }}"></script>` unchanged.
  - [x] Keep the `lang="{{ .Site.Language.Lang }}"` attribute on `<html>` unchanged (required for accessibility — NFR-6).

- [x] Task 7: Build verification (AC: #7, #8)
  - [x] Run `~/bin/hugo --minify` from the project root (Hugo 0.128.0+ is installed at `~/bin/hugo`, not on system PATH — see Story 2.1 debug log).
  - [x] Confirm exit code 0 with no ERROR lines in output.
  - [x] Confirm `public/en/index.html` contains `<link` referencing `css/index.css` (CSS wired).
  - [x] Confirm no `tailwind`, `bootstrap`, `bulma`, or theme references appear in `layouts/` or `static/css/index.css`.
  - [x] Visually load `public/en/index.html` in a browser (or inspect the HTML) and confirm the canvas background `#f7f9fb` is applied to `<body>`.

## Dev Notes

### Architecture Constraints (MUST follow)

- **AD-5 — Zero-Dependency Custom Hugo Layouts** (`ARCHITECTURE-SPINE.md`): The site MUST use custom layouts under `layouts/` and custom CSS in `static/css/index.css`. **No external Hugo themes, no CDN CSS frameworks (no Tailwind CDN, no Bootstrap), no `@import url(...)` pointing to any non-Google-Fonts external CDN are permitted in the CSS.** The UX mockups (`imports/ai_1/`, `imports/ai_2/`) were prototyped with Tailwind — those are reference-only. Translate their visual intent into hand-written CSS using the tokens below.
- **AD-6 — Structured Frontmatter Storage** (`ARCHITECTURE-SPINE.md`): This story does NOT change any frontmatter schema. The `articles` YAML array established in Story 2.1 must not be touched.
- This story creates the **CSS foundation** that Stories 2.3–2.6 will build on. Every class name defined here is a contract — downstream stories will use them. Do NOT rename after this story is merged.

### Files to Create / Modify

| File | Action | Notes |
|---|---|---|
| `static/css/.gitkeep` | **DELETE** | Replace with real `index.css` |
| `static/css/index.css` | **CREATE** | Full design system — see Token Reference |
| `layouts/_default/baseof.html` | **UPDATE** | Add Inter font + semantic scaffold |

### Files to NOT Touch (Epic 1 — complete)

The following must not be modified at all:
- `src/pipeline.py`, `src/summarizer.py`, `src/translator.py`, `src/publisher.py`
- `data/blogs.yaml`, `data/fetched_posts.json`
- `.github/workflows/pipeline.yml`
- `pyproject.toml`, `uv.lock`
- `content/en/posts/*.md`, `content/zh-tw/posts/*.md` (pipeline-owned)
- `layouts/_default/single.html` — stub; owned by Story 2.4
- `layouts/_default/list.html` — stub; owned by Story 2.3
- `layouts/index.html` — stub; owned by Story 2.3
- `static/js/.gitkeep` / `static/js/main.js` — owned by Story 2.5

### Token Reference — CSS Custom Properties

Implement ALL of these under `:root` in `index.css`. Values sourced verbatim from `DESIGN.md` frontmatter and the UX mockups.

#### Colors

```css
:root {
  /* --- Brand --- */
  --color-primary:                  #004ac6;
  --color-on-primary:               #ffffff;
  --color-primary-container:        #2563eb;
  --color-on-primary-container:     #eeefff;
  --color-inverse-primary:          #b4c5ff;

  /* --- Secondary --- */
  --color-secondary:                #4648d4;
  --color-on-secondary:             #ffffff;
  --color-secondary-container:      #6063ee;
  --color-on-secondary-container:   #fffbff;

  /* --- Tertiary (semantic accents) --- */
  --color-tertiary:                 #943700;
  --color-tertiary-container:       #bc4800;
  --color-on-tertiary-container:    #ffede6;

  /* --- Error --- */
  --color-error:                    #ba1a1a;
  --color-error-container:          #ffdad6;
  --color-on-error-container:       #93000a;

  /* --- Surface tonal layers --- */
  --color-background:               #f7f9fb;  /* L0: Canvas */
  --color-surface:                  #f7f9fb;
  --color-surface-container-lowest: #ffffff;  /* L1: Cards/sidebar */
  --color-surface-container-low:    #f2f4f6;
  --color-surface-container:        #eceef0;
  --color-surface-container-high:   #e6e8ea;
  --color-surface-container-highest:#e0e3e5;
  --color-surface-dim:              #d8dadc;
  --color-surface-bright:           #f7f9fb;
  --color-surface-tint:             #0053db;
  --color-inverse-surface:          #2d3133;
  --color-inverse-on-surface:       #eff1f3;

  /* --- Text --- */
  --color-on-surface:               #191c1e;  /* Primary text */
  --color-on-surface-variant:       #434655;  /* Secondary text */
  --color-on-background:            #191c1e;

  /* --- Outlines / Borders --- */
  --color-outline:                  #737686;
  --color-outline-variant:          #c3c6d7;
  --color-border-low:               #e2e8f0;  /* L1 card borders (tonal) */

  /* --- Fixed --- */
  --color-primary-fixed:            #dbe1ff;
  --color-primary-fixed-dim:        #b4c5ff;
  --color-on-primary-fixed:         #00174b;
  --color-on-primary-fixed-variant: #003ea8;
}
```

#### Border Radii

```css
:root {
  --radius-sm:      0.125rem;  /* 2px  */
  --radius-default: 0.25rem;   /* 4px  — standard elements: buttons, inputs, tags */
  --radius-md:      0.375rem;  /* 6px  */
  --radius-lg:      0.5rem;    /* 8px  — large elements: article cards, summary containers */
  --radius-xl:      0.75rem;   /* 12px */
  --radius-full:    9999px;    /* pill shape */
}
```

#### Spacing

```css
:root {
  --spacing-xs:            4px;
  --spacing-sm:            8px;
  --spacing-md:            16px;
  --spacing-lg:            24px;
  --spacing-xl:            32px;
  --spacing-2xl:           48px;
  --spacing-container-max: 1440px;
  --spacing-nav-width:     280px;
}
```

#### Typography

```css
:root {
  --font-inter: 'Inter';  /* loaded from Google Fonts */

  /* Font sizes */
  --fs-headline-xl:         30px;
  --fs-headline-lg:         24px;
  --fs-headline-lg-mobile:  20px;
  --fs-headline-md:         18px;
  --fs-body-lg:             16px;
  --fs-body-md:             14px;
  --fs-label-md:            12px;
  --fs-label-sm:            11px;

  /* Line heights */
  --lh-headline-xl:         38px;
  --lh-headline-lg:         32px;
  --lh-headline-lg-mobile:  28px;
  --lh-headline-md:         26px;
  --lh-body-lg:             24px;
  --lh-body-md:             20px;
  --lh-label-md:            16px;
  --lh-label-sm:            14px;

  /* Font weights */
  --fw-headline-xl:  700;
  --fw-headline-lg:  600;
  --fw-headline-md:  600;
  --fw-body-lg:      400;
  --fw-body-md:      400;
  --fw-label-md:     600;
  --fw-label-sm:     500;

  /* Letter spacing */
  --ls-headline-xl: -0.02em;
  --ls-headline-lg: -0.01em;
  --ls-label-md:     0.05em;
}
```

#### Elevation / Shadow

```css
:root {
  --shadow-none:   none;                               /* L0 and L1 */
  --shadow-l2:     0 4px 6px -1px rgb(0 0 0 / 0.05);  /* L2: active dropdowns */
  --shadow-hover:  0 2px 8px -1px rgb(0 0 0 / 0.08);  /* interactive card hover */
}
```

#### Transitions

```css
:root {
  --transition-all: all 0.2s ease-in-out;
}
```

### Complete `index.css` Structure (implementation guide)

The developer should produce `index.css` in the following section order. The full file should be self-contained — no `@import` of other local files.

```
/* 1. Google Fonts @import — Inter */
/* 2. CSS Custom Properties (:root) — all tokens above */
/* 3. CSS Reset */
/* 4. Base typography — body font, global text color */
/* 5. Typography utility classes (.text-headline-xl, etc.) */
/* 6. Tonal layer utilities (.layer-0, .layer-1, .layer-2, .interactive-hover) */
/* 7. Layout primitives (.container, .grid-12, .col-4, .col-8) */
/* 8. Responsive collapse (@media max-width: 767px) */
/* 9. Global header (.site-header, .site-title, .header-actions) */
/* 10. Button base (.btn-ghost) */
/* 11. Card base (.card) */
/* 12. Tag pill (.tag-pill) */
/* 13. Content wrapper (.site-content) */
/* 14. Active card indicator (.active-card-indicator) */
/* 15. Accessibility — focus ring */
```

### `baseof.html` Final Target State

The updated `layouts/_default/baseof.html` should look like this after Story 2.2:

```html
<!DOCTYPE html>
<html lang="{{ .Site.Language.Lang }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ .Title }} | {{ .Site.Title }}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="{{ "css/index.css" | relURL }}">
</head>
<body class="layer-0">
  <header class="site-header">
    {{ block "header" . }}
    <a href="{{ "/" | relLangURL }}" class="site-title">{{ .Site.Title }}</a>
    <div class="header-actions">
      {{ block "lang-switcher" . }}<!-- Story 2.6 will implement language switcher -->{{ end }}
    </div>
    {{ end }}
  </header>
  <div class="site-content">
    {{ block "main" . }}{{ end }}
  </div>
  <script src="{{ "js/main.js" | relURL }}"></script>
</body>
</html>
```

**Key decisions:**
- `relLangURL` on the logo link ensures `/en/` vs `/zh-tw/` home routing (Hugo multilingual).
- The `lang-switcher` block is intentionally left empty — Story 2.6 will `define` it in a partial.
- `layer-0` on `<body>` applies `background: var(--color-background)` (#f7f9fb) globally (AC #3).
- Google Fonts preconnect hints reduce TTFB for font loading.

### Tonal Layering Rules (UX-DR-2)

| Layer | Class | Background | Border | Shadow |
|---|---|---|---|---|
| L0 — Canvas | `.layer-0` | `#f7f9fb` (--color-background) | none | none |
| L1 — Cards / Sidebar | `.layer-1` | `#ffffff` (--color-surface-container-lowest) | `1px solid #e2e8f0` (--color-border-low) | none |
| L2 — Active / Dropdowns | `.layer-2` | `#ffffff` | `1px solid #e2e8f0` | `--shadow-l2` |
| Interactive Hover | `.interactive-hover` | `#f1f5f9` on hover | unchanged | optional `--shadow-hover` |

### Typography Utility Class Examples

```css
.text-headline-xl {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-headline-xl);
  font-weight: var(--fw-headline-xl);
  line-height: var(--lh-headline-xl);
  letter-spacing: var(--ls-headline-xl);
}
.text-headline-lg {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-headline-lg);
  font-weight: var(--fw-headline-lg);
  line-height: var(--lh-headline-lg);
  letter-spacing: var(--ls-headline-lg);
}
.text-label-md {
  font-family: var(--font-inter), sans-serif;
  font-size: var(--fs-label-md);
  font-weight: var(--fw-label-md);
  line-height: var(--lh-label-md);
  letter-spacing: var(--ls-label-md);
  text-transform: uppercase;
}
/* ... etc for all 8 scales */
```

### Layout Primitive Rules

```css
.container {
  max-width: var(--spacing-container-max); /* 1440px */
  margin-inline: auto;
  padding-inline: var(--spacing-lg);       /* 24px each side */
}

.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--spacing-xl);                  /* 32px */
}

.col-4  { grid-column: span 4; }
.col-8  { grid-column: span 8; }
.col-12 { grid-column: span 12; }

/* Mobile collapse — full-width stack below 768px */
@media (max-width: 767px) {
  .grid-12 {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  .col-4, .col-8, .col-12 { grid-column: span 1; }
}
```

> **Note:** `col-4` (280px sidebar) and `col-8` (right detail panel) are used in Story 2.4. `grid-12` is used for the bento grid in Story 2.3. Do not remove or rename these.

### Accessibility Notes (NFR-6)

- Global focus ring: All interactive elements (links, buttons, inputs) must have a visible focus indicator — use a 2px offset ring in `--color-primary`:
  ```css
  :focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
    border-radius: var(--radius-default);
  }
  ```
- Minimum click target enforcement for `.btn-ghost`: minimum height 44px (UX-DR-8 / NFR-6).
- `lang` attribute on `<html>` is already set in baseof.html via `{{ .Site.Language.Lang }}` — do NOT remove it.

### Google Fonts Note — Zero-Dependency Compliance

Importing Inter from Google Fonts via a `<link>` tag is **not** a Hugo theme dependency — it is a runtime font load, consistent with **AD-5** (which prohibits external Hugo themes and framework CDNs). The `@import url(...)` for Google Fonts inside CSS is equivalent and also acceptable, but the `<link>` approach in `<head>` has better performance (preconnect hints work). Either approach passes.

If internet access is not guaranteed at build-time (offline CI), you may instead self-host the Inter font in `static/fonts/` and reference it via `@font-face` in `index.css`. This is optional for Story 2.2 — use the Google Fonts CDN approach unless offline build is flagged.

### What This Story Does NOT Implement (Scope Boundary)

| Feature | Story |
|---|---|
| Bento grid homepage layout | 2.3 |
| Split-pane detail layout | 2.4 |
| `static/js/main.js` JavaScript switcher | 2.5 |
| Tag pill filters, search input, language switcher behavior | 2.6 |
| `i18n/*.toml` translation files | 2.6 (optional) |

The CSS classes created here (`.grid-12`, `.col-4`, `.card`, `.tag-pill`, etc.) serve as the style foundation for those stories. Their HTML usage/composition is deferred.

### Previous Story Learnings (Story 2.1)

From Story 2.1 debug log and completion notes — important context:

- **Hugo binary location**: Hugo 0.128.0+extended is installed at `~/bin/hugo` (NOT at `/usr/bin/hugo`). Always run builds as `~/bin/hugo --minify`, not `hugo --minify`. GitHub Actions uses `peaceiris/actions-hugo@v3` (Story 1.6) and has its own Hugo install.
- **`.gitkeep` files**: `static/css/.gitkeep` and `static/js/.gitkeep` use a comment-format placeholder (`# placeholder`). **Delete `static/css/.gitkeep` and create `static/css/index.css` in its place** — do NOT append CSS to the gitkeep file.
- **`layouts/_default/baseof.html` current state**: The file was created as a minimal stub in Story 2.1. See the "baseof.html Final Target State" section above — this story replaces it with the semantic version.
- **`hugo.toml` — `[markup.goldmark.renderer] unsafe = true`** is already set (Story 2.1). This allows raw HTML in layout templates if needed — no change required.
- **No `themes/` directory exists** — enforce by not creating one. Any Hugo build warning about missing theme can be ignored if exit code is 0.

### Testing Approach

No automated test framework for this story. Verification is the Hugo build + visual spot-check:

1. `~/bin/hugo --minify` from project root → exit code 0, no ERROR lines.
2. `grep -r "tailwind\|bootstrap\|bulma" layouts/ static/css/` → zero matches (enforces AD-5).
3. `grep "fonts.googleapis.com/css2?family=Inter" layouts/_default/baseof.html` → confirms Inter is wired.
4. `grep "css/index.css" public/en/index.html` → CSS is included in built output.
5. Open `public/en/index.html` in a browser or inspect HTML — body background should be `#f7f9fb` (canvas L0), the header should be 64px tall with white background and `#e2e8f0` bottom border.
6. Inspect rendered text to confirm Inter font is used.

## References

- [Source: epics.md#Story 2.2](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/epics.md#L185)
- [Source: DESIGN.md — Colors, Typography, Layout, Elevation, Shapes, Components](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/DESIGN.md)
- [Source: EXPERIENCE.md — Information Architecture, Component Patterns, Accessibility Floor](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/EXPERIENCE.md)
- [Source: ARCHITECTURE-SPINE.md#AD-5 — Zero-Dependency Custom Hugo Layouts](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L65)
- [Source: ARCHITECTURE-SPINE.md#AD-6 — Structured Frontmatter Storage](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/ARCHITECTURE-SPINE.md#L73)
- [Source: SOLUTION-DESIGN.md#4. Frontend & Layout Design](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/architecture/architecture-daily-ai-news-2026-07-11/SOLUTION-DESIGN.md#L73)
- [UX Mockup — Detail View HTML](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/imports/ai_1/code_stitch.html)
- [UX Mockup — Archive View HTML](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/imports/ai_2/code_stitch.html)
- [Story 2.1 completion notes](file:///home/clx/projects/daily-ai-news/_bmad-output/implementation-artifacts/2-1-hugo-multilingual-setup-configuration-research.md)
- [Google Fonts — Inter](https://fonts.google.com/specimen/Inter)
- [Hugo relLangURL docs](https://gohugo.io/functions/urls/rellangurl/)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6 (GitHub Copilot CLI)

### Debug Log References

- No blocking issues encountered.
- `static/css/.gitkeep` deleted; `static/css/index.css` created with all 15 sections as specified.
- `layouts/_default/baseof.html` updated from minimal stub to semantic scaffold with Inter font preconnect links and `body class="layer-0"`.
- `~/bin/hugo --minify` exited 0 with no ERROR lines (17 ms, 11 EN + 10 ZH-TW pages).
- `static/js/.gitkeep` left untouched (owned by Story 2.5 per story constraints).

### Completion Notes List

- All 8 ACs satisfied.
- Design tokens (colors, radii, spacing, typography, elevation, transitions) declared verbatim from DESIGN.md under `:root`.
- CSS structure follows the 15-section order specified in Dev Notes exactly.
- `layer-0` on `<body>` applies `#f7f9fb` canvas background globally (AC #3).
- Inter loaded via Google Fonts `<link>` with preconnect hints (AC #5); `--font-inter` token wired to body font-family.
- No external Hugo themes, Tailwind CDN, or CSS framework references anywhere (`grep` confirmed zero matches).
- `public/en/index.html` confirmed to contain `/daily-ai-news/css/index.css` reference.
- `.btn-ghost` minimum height 44px enforced (NFR-6 accessibility).
- `:focus-visible` global focus ring using `--color-primary` with 2px offset (NFR-6).

### File List

- `static/css/.gitkeep` — DELETED
- `static/css/index.css` — CREATED (full design system: tokens, reset, typography, tonal layers, layout primitives, component shells, accessibility)
- `layouts/_default/baseof.html` — UPDATED (Inter preconnect + font link, semantic header scaffold, `layer-0` on body)
