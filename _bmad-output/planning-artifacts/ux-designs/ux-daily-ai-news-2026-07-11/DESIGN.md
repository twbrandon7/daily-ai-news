---
name: Nexus Technical Journal
description: Daily AI News Summary Website. Technical, high-signal, developer-focused.
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#434655'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#4648d4'
  on-secondary: '#ffffff'
  secondary-container: '#6063ee'
  on-secondary-container: '#fffbff'
  tertiary: '#943700'
  on-tertiary: '#ffffff'
  tertiary-container: '#bc4800'
  on-tertiary-container: '#ffede6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#ffdbcd'
  tertiary-fixed-dim: '#ffb596'
  on-tertiary-fixed: '#360f00'
  on-tertiary-fixed-variant: '#7d2d00'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  headline-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  container-max: 1440px
  nav-width: 280px
status: final
created: 2026-07-11
updated: 2026-07-11
---

## Brand & Style

The design system is built on a foundation of **Minimalism** and **Modern Corporate** aesthetics, specifically tailored for high-density information environments. It prioritizes cognitive ease, aiming to evoke a sense of precision, reliability, and "AI-native" intelligence. 

The visual language avoids unnecessary decoration, instead using generous whitespace and a strict mathematical grid to create an organized "command center" feel. Interfaces should feel lightweight but sturdy, utilizing subtle micro-interactions to provide feedback without distracting the user from the content.

## Colors

This design system utilizes a high-clarity palette centered around "Tech Blue" to signify intelligence and action. 

- **Primary:** Used for active navigation states, primary call-to-actions, and key data points.
- **Surface & Background:** A subtle distinction is made between the `#f8fafc` canvas and `#ffffff` surface cards to create a natural "stacking" effect without heavy shadows.
- **Typography:** Contrast is strictly managed. Headings use Deep Slate for maximum legibility, while body text uses a softer Slate-600 to reduce eye strain during long-form reading.
- **Semantic Accents:** Emerald and Amber are reserved strictly for technical metadata—Emerald for optimizations/performance and Amber for trade-offs/warnings.

## Typography

The system relies exclusively on **Inter**, a typeface designed for screen readability. 

- **Hierarchy:** Dramatic weight shifts (from 700 to 400) differentiate between summary titles and technical details.
- **Tracking:** Headings use slight negative letter spacing (-0.01em to -0.02em) to appear tighter and more professional.
- **Utility:** Small labels (11px-12px) are used for metadata, tags, and language switchers, ensuring the UI remains compact.
- **Line Height:** A generous 1.5x ratio is maintained for body text to facilitate the skimming of technical summaries.

## Layout & Spacing

The design system employs a **Fixed Grid** approach for the main dashboard architecture to ensure a consistent tool-like experience.

- **Dashboard Structure:** A fixed 280px sidebar on the left for navigation, with a fluid main content area that caps at 1440px. 
- **The "5 Core Elements" Detail View:** This section uses a 2-column layout on desktop, reflowing to a single column on mobile.
- **Rhythm:** An 8px base unit (4px for tight clusters) dictates all margins and padding. 
- **Breakpoints:**
  - **Desktop (1024px+):** Sidebar visible, dual-pane detail view.
  - **Tablet (768px - 1023px):** Sidebar collapses into a drawer; content padding reduces to 16px.
  - **Mobile (<768px):** Vertical stack; headline-lg-mobile scale activated.

## Elevation & Depth

This design system uses **Tonal Layering** and **Low-Contrast Outlines** instead of traditional shadows to maintain a clean, "flat" technical aesthetic.

- **Level 0 (Background):** `#f8fafc` — The canvas.
- **Level 1 (Cards/Sidebar):** `#ffffff` — Elevated with a 1px border of `#e2e8f0`. No shadow.
- **Level 2 (Active States/Dropdowns):** Elevated with a very soft, diffused shadow: `0 4px 6px -1px rgb(0 0 0 / 0.05)`.
- **Interactive Depth:** Hovering over article cards in the sidebar should trigger a subtle shift to a `#f1f5f9` background rather than an elevation change.

## Shapes

The shape language is **Soft** (Level 1). This provides a professional balance—rounded enough to feel modern and accessible, but sharp enough to feel precise and technical.

- **Standard Elements:** 0.25rem (4px) for buttons, small input fields, and tags.
- **Large Elements:** 0.5rem (8px) for article cards and summary containers.
- **Interactive Focus:** Focus states should utilize a 2px offset border in the primary color to maintain accessibility.

## Components

- **Global Header** — A slim 64px bar. Language switchers (EN/TW) are styled as ghost buttons with a subtle divider.
- **Bento Card** — Elevated with a 1px border of `#e2e8f0`. High-contrast titles (`headline-md`) with 2 lines of summary text. Hover state scale transition.
- **Tag Pill** — Small, pill-shaped tags (`label-sm`) with 10% opacity backgrounds of their respective accent colors and 100% opacity text.
- **Search Input** — Rounded search bar in the left sidebar menu. Background `#f2f4f6`, search icon on left.
- **Article Card** — Sidebar list card. High-contrast titles (`headline-md`) with category icon and tag pills. Active state features 3px vertical indicator in primary color.
- **Rating Stars** — High-contrast star icons showing a 5-star visual rating using `primary_color`.
- **Summary Section** — The "5 Core Elements" are presented as distinct bordered sections. Each element begins with a `label-md` header.
- **Daily Overview** — A full-width card at the top of the main view using a subtle gradient border or a very light `secondary_color` tint to distinguish it as the "Daily Pulse."
