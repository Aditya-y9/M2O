# DESIGN.md - ModernizeIQ Architectural Assessment Dashboard

## Context (from discovery)

- Artifact type: dashboard / decision tool
- Positioning: technical / enterprise architecture / high-stakes infrastructure decision
- Audience: Enterprise Architects, Cloud Migration Directors, Mainframe System Programmers, Engineering Executives
- Primary action: Confidently decide and justify target distributed hosting platform (Red Hat OpenShift vs Linux VM) with dependency blast radius and domain boundary evidence.
- Adjectives: Rigorous, Authoritative, Architectural, Calibrated, Clear
- Visual word translations:
  - Rigorous: High-density structured tables with tabular figures, explicit metrics, zero vague placeholders.
  - Authoritative: IBM Plex typography (the standard of mainframe & enterprise cloud computing), high-contrast legible headings, crisp borders.
  - Architectural: Neutral matte slate base with precision hairline dividers (1px), subtle elevation, blueprint-like canvas graph.
  - Calibrated: Color used strictly for semantic state (OpenShift Mint, VM Amber, Blocker Crimson), never decorative gradients or neon glows.
  - Clear: Consolidated 3-layer information hierarchy resolving the primary decision above the fold, replacing 8 overwhelming fragmented tabs.
- Aesthetic essence (3 words): Industrial Precision Instrument
- Archetype: Sage / Ruler (governance, precision, architectural authority)
- References:
  - Admire: AWS Architecture Center / Red Hat OpenShift Console (clean technical status), Linear Insights (low-latency, crisp borders, tabular numerals), Stripe Dashboard (calm hierarchy, disciplined tables).
  - Avoid: Generic AI startup neon slop (purple/cyan gradients, glowing box-shadows, glassmorphic blur, 24px blob-rounded cards, gradient text).
- Mode: Dark mode (technical console)
- Density: High density, disciplined (5-8 core metrics, structured tables, interactive canvas)
- Constraints: Self-contained single-page HTML5 output; must render 100% offline without Node.js or npm dependencies; WCAG 2.2 AA contrast compliance.

## Aesthetic

- Direction: Industrial / Swiss Utilitarian (Console)
- Defining trait: Crisp hairline architectural rules (`1px solid #232d3f`), monospace numerics, high-contrast typography, and purposeful data density without decorative fluff.
- Signature move: A unified **Platform Decision Command Center** that contrasts OpenShift containerization vs Linux VM rehosting directly against detected blockers and 12-factor compliance, driving an interactive Canvas topology graph with real-time blast-radius calculation.

## Typography

- Display & Body: `IBM Plex Sans`, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
- Monospace: `IBM Plex Mono`, "JetBrains Mono", Consolas, monospace
- Source: Google Fonts / System Fallback
- Scale: Ratio 1.15 (Minor Third / Compact Pro Tool Scale), Base 14px
  - Title / Verdict: 22px / 1.25 / Bold (700)
  - Section Heading: 16px / 1.3 / SemiBold (600)
  - Subheading / Card Title: 13px / 1.4 / Medium (500)
  - Body Text: 13px / 1.5 / Regular (400)
  - Meta / Badges / Labels: 11px / 1.4 / SemiBold (600) / Uppercase tracking 0.05em
  - Code / Monospace Metrics: 12px / 1.4 / Regular (400) & Bold (700)
- Numeric formatting: `font-variant-numeric: tabular-nums;` strictly enforced across all metrics, LOC, percentages, and table cells.

## Color (Tokens in OKLCH & Hex Fallback)

- Strategy: Appropriateness for enterprise mainframe architecture. Strict 60-30-10 distribution. Neutral technical slate dominates; color is reserved solely for semantic state (recommended platform, blocker alert, factor compliance).
- Palette:
  - bg: `oklch(0.14 0.02 260)` | `#0a0e17` (Deep Console Base)
  - surface: `oklch(0.18 0.02 258)` | `#111726` (Precision Panel Surface)
  - surface-elevated: `oklch(0.22 0.025 255)` | `#182033` (Elevated Panel)
  - surface-subtle: `oklch(0.16 0.015 260)` | `#0e1320` (Subtle Table Header / Inset)
  - border: `oklch(0.28 0.03 255)` | `#232d3f` (Hairline Structural Divider)
  - border-light: `oklch(0.35 0.04 255)` | `#334158` (Interactive Focus / Hover Divider)
  - fg: `oklch(0.96 0.01 250)` | `#f1f5f9` (Primary Legible Text)
  - fg-muted: `oklch(0.70 0.03 250)` | `#94a3b8` (Secondary Descriptive Text)
  - fg-subtle: `oklch(0.50 0.03 250)` | `#64748b` (Tertiary Metadata & Captions)
  - accent-ocp: `oklch(0.68 0.16 165)` | `#059669` / `#10b981` (OpenShift Container Mint)
  - accent-vm: `oklch(0.72 0.16 75)` | `#d97706` / `#f59e0b` (Linux VM Rehost Amber)
  - status-danger: `oklch(0.62 0.22 25)` | `#ef4444` (Blocker / Critical Risk Crimson)
  - status-neutral: `oklch(0.65 0.12 235)` | `#3b82f6` (COBOL Program / Information Blue)

## Spacing, Radius, Shadow

- Spacing base: 4px. Scale: 4px, 8px, 12px, 16px, 20px, 24px, 32px.
- Radius: Max 2 values.
  - Micro / Controls / Badges / Buttons: `4px`
  - Container Panels / Cards: `6px`
  - *Hard rule*: No radii exceeding 8px. Zero blob-rounding.
- Shadow approach: Defined edge over diffuse blur. `1px solid var(--border)` with subtle single-layer depth: `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);`. Zero colored neon glow shadows.

## Layout & Composition

- Information Architecture:
  1. Top Global Bar: App Identity, Architecture Scope, Export Controls, Live Status.
  2. Hero Decision Command Center: The verdict (OCP vs VM score comparison bar, blocker count, Gartner 7R disposition, 12-factor summary).
  3. 3-Mode Focused Workbench:
     - Tab 1: Topology & Blast Radius (Interactive Canvas graph + Node Search/Filter + Right-hand Blast Radius detail panel).
     - Tab 2: Semantic Domain Decomposition (2D scatter plot from `all-MiniLM-L6-v2` dense vectors + Microservice candidate table).
     - Tab 3: Technical Audit & ADR (8-dimension progress metrics, full Risk Catalog with filterable severities, Michael Nygard ADR).
- Spacing rhythm: Tight 8-12px within cards; structured 16-20px between sections.
- Anti-overwhelm principle: Replace 8 scattered, disconnected tabs with 3 purposeful, synchronized views.

## Components & States

- Mode Switcher: Segmented button group with visible active state (`bg-surface-elevated text-fg border-border`).
- Buttons: Primary filled (`bg-accent-ocp text-white hover:brightness-110 active:brightness-95`), Secondary outline (`border-border text-fg hover:bg-surface-elevated`), Focus visible (`box-shadow: 0 0 0 2px var(--border-light)`).
- Tables: Left-aligned text labels, right-aligned numbers with `tabular-nums`, hairline row borders (`1px solid #1a2233`), hover state on rows (`bg-surface-elevated/40`).
- Canvas Graph: White/light-gray background or deep technical charcoal (`#0c101a`), crisp circle nodes with 1.5px borders, labeled nodes, clear directional arrows.

## Slop-Audit Verification

- [x] NO purple/indigo gradients.
- [x] NO gradient text on headings.
- [x] NO glowing colored box-shadows.
- [x] NO glassmorphism / backdrop-blur abuse.
- [x] NO hero-metric triptych reflex.
- [x] NO blob-rounding (> 8px).
- [x] NO Inter/system-ui default. Uses IBM Plex Sans + IBM Plex Mono.
- [x] Numbers formatted with tabular numerals.
- [x] Replaced overwhelming 8-tab maze with unified 3-mode Workbench.
