---
name: Nexus Technical Journal
status: final
sources:
  - _bmad-output/planning-artifacts/prds/prd-daily-ai-news-2026-07-11/prd.md
created: 2026-07-11
updated: 2026-07-11
---

# Nexus Technical Journal — Experience Spine

## Foundation

Multilingual web application (desktop-first with responsive mobile views). Built on static HTML + Tailwind or Vanilla CSS matching `{name}` tokens. No dynamic server session state; entirely static and client-driven. 
Localization is mapped to strict routes: `/en/` and `/zh-tw/` with active state preservation. Visual identity reference is defined in `DESIGN.md`.

*Note on UJ-2:* Alex (Maintainer) registers blog sources via config file commit in the GitHub repository, which triggers the automated Daily News Pipeline (GitHub Actions). No Web UI is provided for source management.

## Information Architecture

| Surface | Reached from | Purpose |
|---|---|---|
| Archive (Home) | App URL open / Logo click | Chronological daily Bento grid, pagination, features quick look |
| Daily Summary (Split-Pane) | Archive card "View Summary" / Direct date link | Split-pane dashboard with tag filtering, search, article list, and technical summaries |

- Header: Static 64px height, persistent across all pages. Includes Title/Logo, active date (if on Detail), and language switcher.
- Detail layout: Desktop uses a 12-column grid. Left sidebar spans 4 cols; right detail panel spans 8 cols. Reflows to single-column vertical list on mobile view (<768px).

→ Composition references:
- [Archive Mockup HTML](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/imports/ai_2/code_stitch.html) · [Archive Mockup Screenshot](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/imports/ai_2/screen_stitch.png)
- [Detail Mockup HTML](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/imports/ai_1/code_stitch.html) · [Detail Mockup Screenshot](file:///home/clx/projects/daily-ai-news/_bmad-output/planning-artifacts/ux-designs/ux-daily-ai-news-2026-07-11/imports/ai_1/screen_stitch.png)

Spine wins on conflict.

## Voice and Tone

Microcopy is targeted at busy engineering professionals. No marketing fluff, no exclamation marks.

| Do | Don't |
|---|---|
| "Deep Dive" | "Super exciting read!" |
| "閱讀時間：約 4 分鐘" | "Read this fast in 4m!" |
| "今日 AI 領域聚焦於..." | "Guess what happened today in AI!" |
| "Original Link" / "原文連結" | "Go to website" |
| Retain original terms in TC: "prompt", "fine-tuning", "RAG", "pipeline", "embeddings". | Over-translate technical jargon into non-standard local terms. |

## Component Patterns

Visual parameters are specified in `DESIGN.md.Components`.

| Component | Use | Behavioral rules |
|---|---|---|
| Global Header | Top of all views | Logo/title clicks home. Language toggle preserves current view context. |
| Bento Card | Archive grid | Entire card is interactive. Hover scale transition. Shows article count badge. |
| Tag Pill | Detail sidebar | Clicking filters article list. Toggle state highlights with `{colors.primary}` background. |
| Search Input | Detail sidebar | Client-side fuzzy search matching article title and tags in real time. |
| Article Card | Detail list | Clicking loads article summary in right panel. Highlights active card with border `{colors.primary}`. |
| Rating Stars | Detail header | Read-only visual rating (1-5 stars). Uses custom star icons. |
| Summary Section | Detail panel | Presents 5-element summary. TL;DR has `{colors.primary}` left border. Pros/Cons side-by-side. |

## State Patterns

| State | Surface | Treatment |
|---|---|---|
| Archive Empty | Archive View | "尚無歷史存檔摘要。新增部落格來源以開始生成。" |
| No Articles | Detail View | Show empty state: "今日無新增文章。點此回到存檔。" |
| Search Empty | Detail View | "找不到符合的文章或標籤。" with a reset search button. |
| Language Switch | All views | Toggle changes language code path (e.g. `/en/` <-> `/zh-tw/`) preserving current selected date/article. |
| Card Hover | Archive View | Shift up by 2px and apply soft drop shadow `{colors.primary}` tint. |
| Card Active | Detail List | Left border indicator 3px wide in `{colors.primary}` with 5% background tint. |

## Interaction Primitives

- Tap/Click to select or navigate.
- Hover states on all buttons and cards transition over 200ms (`transition-all duration-200`).
- No infinite scroll; pagination is strictly page-based at grid bottom.
- Client-side routing for tab/search filtering ensures zero layout shift.

## Accessibility Floor

- Screen readers: Custom ARIA labels for category icons (e.g., `aria-label="LLM / AI Model"` for psychology icon).
- Language switch: Correct HTML `lang` attributes set dynamically (`en` vs `zh-Hant-TW`).
- Minimum click target size: 44px for buttons, pagination elements, and language switcher.
- Contrast: All text colors must adhere to a minimum of 4.5:1 ratio against their background surfaces (verified in `DESIGN.md`).

## Inspiration & Anti-patterns

- **Lifted from Google Labs / DevSite:** Split-pane layouts for developer documentation and dashboard feel.
- **Lifted from Bento Grid:** Modern, compact overview style for historical daily archives.
- **Rejected:** Continuous scroll on home page. A date-based archive is more structured and searchable.
- **Rejected:** Modal views for summaries. Direct in-page split layout preserves reading flow.

## Key Flows

### Flow 1 — Developer scans daily summaries

1. Chen opens the website, landing on Archive Home (`/zh-tw/` default or `/en/`).
2. Scans Bento cards showing recent days.
3. Taps the latest day card.
4. App routes to Detail View (`/zh-tw/daily/2026-07-11`).
5. Chen sees the Article List in the left sidebar and active detailed summary on the right.
6. **Climax:** Reads the side-by-side Pros and Cons and TL;DR, gaining full technical understanding under 30 seconds.
7. Taps "Original Link" to save source to reading list.

### Flow 2 — Switching languages for a precise term

1. Chen is reading a summary in Traditional Chinese.
2. An English technical term's context is unclear.
3. Chen taps the "EN/TW" switcher in the header.
4. **Climax:** The page instantly reloads under the `/en/` route with the exact same date and article selected.
5. Chen verifies the English phrasing and switches back.
