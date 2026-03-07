# Cross-Repo Consistency Strategy

> Step 8 of the Evident Ecosystem Architecture Series
>
> Principle: **Coherent where it matters. Independent where it should be.
> Enforced by structure, not by memory.**

---

## 1. Consistency Layers

The ecosystem spans 11+ repositories across three product families (Evident,
Tillerstead, Personal) with divergent stacks (Jekyll, React+Vite, FastAPI,
vanilla HTML). Forcing uniform UI is wrong. Instead, consistency is applied in
**five layers**, each with different enforcement strength.

```
Layer 5 — Product Personality        (per-repo, flexible)
Layer 4 — Component Patterns         (per-family, guided)
Layer 3 — Design Tokens              (per-family, standardized)
Layer 2 — Conventions & Metadata     (ecosystem-wide, required)
Layer 1 — Governance & Legal         (ecosystem-wide, mandatory)
```

**Enforcement rule:** Layers 1–2 apply to every repo in the ecosystem. Layer 3
applies per product family. Layers 4–5 are advisory guides, not mandates.

---

## 2. Layer 1 — Governance & Legal (Mandatory, All Repos)

These elements must appear in every public-facing repo and every deployed
product. Non-negotiable.

### 2.1 Footer Legal Band

Every deployed page must include a bottom-of-page legal band containing:

| Element | Required | Example |
|---------|----------|---------|
| Copyright line | Yes | `© 2026 Evident Technologies. All rights reserved.` or `© 2026 Tillerstead LLC` |
| Entity name | Yes | Legal entity owning the product |
| Privacy link | If collecting data | `/privacy` |
| Terms link | If offering a service | `/terms` |
| Disclaimer link | If providing calculations, data, or legal-adjacent content | `/disclaimers` |

**For Evident family products:** footer references "Evident Technologies"
regardless of the satellite's display name.

**For Tillerstead family products:** footer references "Tillerstead LLC".

**For Independent/Personal products:** footer references the operator's name or
a neutral entity.

**Implementation:** This is text-only, not a visual component. A plain `<footer>`
with a paragraph is sufficient. No specific styling is required — it inherits
from the product's own design.

### 2.2 Repository Identity Files

Every repo must contain at its root:

| File | Purpose |
|------|---------|
| `.evident-repo.json` | Machine-readable manifest (schema v1) |
| `README.md` | Human-readable identity with product family label |
| `LICENSE` | License file appropriate to the product |

The `.evident-repo.json` `brand` field determines which family's conventions
apply.

### 2.3 Data Handling Disclosure

Any product that stores user data, processes evidence, or performs calculations
must disclose:

- What data is stored and where
- Whether data leaves the device
- Whether calculations are deterministic

This can be a sentence in the footer, a `/privacy` page, or an in-app notice.
The format is flexible; the presence is not.

---

## 3. Layer 2 — Conventions & Metadata (Required, All Repos)

Structural patterns that make the ecosystem recognizable to search engines,
social shares, and developers inspecting the source.

### 3.1 HTML Metadata Template

Every deployed HTML page must include this baseline `<head>` content:

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="description" content="[60-160 character description]">
<meta name="theme-color" content="[brand-appropriate dark color]">

<!-- Open Graph -->
<meta property="og:title" content="[Page Title]">
<meta property="og:description" content="[Same as meta description]">
<meta property="og:image" content="[1200×630 OG image]">
<meta property="og:type" content="website">
<meta property="og:url" content="[Canonical URL]">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[Page Title]">
<meta name="twitter:description" content="[Same]">
<meta name="twitter:image" content="[Same OG image]">

<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

**The metadata fields are required. The specific values vary per product.**

### 3.2 Naming Conventions

| Scope | Convention | Example |
|-------|-----------|---------|
| Product display name | Title case, no abbreviations in public text | "Informed Consent Companion", not "ICC" |
| Repo slug | Lowercase kebab-case | `informed-consent-companion` |
| URL paths | Lowercase with hyphens | `/case-management/`, not `/CaseManagement/` |
| Page titles | `[Page] — [Product]` or `[Page] \| [Product]` | `Dashboard — Evident` |
| CSS class prefix | Product abbreviation, lowercase | `.ev-`, `.ts-`, `.fh-` |
| CSS custom property prefix | Product abbreviation + category | `--ev-color-*`, `--ts-spacing-*` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `EVIDENT_API_KEY` |
| API endpoints | `/api/v{n}/resource` | `/api/v1/cases` |

### 3.3 Copy Conventions

All user-facing text across the ecosystem follows these rules:

| Rule | Correct | Incorrect |
|------|---------|-----------|
| No superlatives | "This system preserves evidence integrity." | "The most powerful evidence platform ever." |
| No emotional hooks | "Access your case files." | "Don't miss out on your case files!" |
| Declarative statements | "Calculations are deterministic and reproducible." | "Amazing AI that changes everything!" |
| Short sentences | Two clauses maximum per sentence. | Avoid run-on compound-complex constructions. |
| Active voice | "The system logs every action." | "Every action is logged by the system." |
| No exaggeration | "Licensed and insured." | "The gold standard of contractors." |
| Measured confidence | "Built for accountability." | "Guaranteed to revolutionize the industry." |

**Evident family products** use a formal, institutional tone. Think: court
filing, not marketing brochure.

**Tillerstead family products** use a direct, knowledgeable trade tone. Think:
experienced contractor explaining the work, not a salesperson.

**Independent products** may adopt their own voice but must still avoid
superlatives and emotional hooks.

### 3.4 Product Family Labels

When a satellite references its parent ecosystem, use these exact phrases:

| Context | Label |
|---------|-------|
| Evident companion satellite | `"by Evident Technologies"` or `"An Evident Technologies product"` |
| Tillerstead venture satellite | `"by Tillerstead LLC"` or `"A Tillerstead product"` |
| Independent satellite | No ecosystem label required |
| Founder-Hub (ops) | `"Evident Technologies — Operations"` |
| Main suite | `"Evident Technologies"` (no qualifier needed) |

These labels appear in footers, about pages, and OG metadata — never in
primary headlines or hero sections.

---

## 4. Layer 3 — Design Tokens (Standardized per Family)

Each product family maintains its own token set. Tokens are not shared across
families (Evident blue is not Tillerstead emerald). But within a family, all
products draw from the same palette.

### 4.1 Token Architecture

```
evident-tokens/
├── evident.foundation.css      Evident family base tokens
├── tillerstead.foundation.css  Tillerstead family base tokens
└── README.md                   Token documentation
```

Each foundation file defines CSS custom properties organized in these
categories:

| Category | Prefix Pattern | Purpose |
|----------|---------------|---------|
| Color | `--{brand}-color-{name}` | Brand palette + semantic colors |
| Text | `--{brand}-text-{role}` | Text color hierarchy |
| Background | `--{brand}-bg-{level}` | Surface and elevation colors |
| Font | `--{brand}-font-{role}` | Font family stacks |
| Size | `--{brand}-size-{scale}` | Type scale |
| Spacing | `--{brand}-space-{scale}` | Margin/padding scale |
| Radius | `--{brand}-radius-{size}` | Border radius |
| Shadow | `--{brand}-shadow-{level}` | Elevation shadows |
| Duration | `--{brand}-dur-{speed}` | Animation timing |
| Ease | `--{brand}-ease-{curve}` | Easing functions |
| Z-index | `--{brand}-z-{layer}` | Stacking order |

### 4.2 Evident Family Tokens (Starter)

Derived from the existing `evident-design-tokens.css` and `brand-tokens.css`.

```css
/* === evident.foundation.css === */

:root {
  /* ── Color ── */
  --ev-color-primary:          #2f5d9f;   /* Evidentiary blue */
  --ev-color-primary-hover:    #3a6db5;
  --ev-color-primary-active:   #254a80;
  --ev-color-accent:           #f59e0b;   /* Brass gold */
  --ev-color-accent-hover:     #d97706;
  --ev-color-danger:           #7a1e2b;   /* Seal red */
  --ev-color-success:          #16a34a;
  --ev-color-warning:          #f59e0b;
  --ev-color-info:             #0284c7;

  --ev-color-primary-accessible: #1d4a85; /* WCAG AA on light bg */
  --ev-color-accent-accessible:  #b45309; /* WCAG AA on light bg */

  /* ── Background ── */
  --ev-bg-ink:                 #0b0d10;   /* Deepest dark */
  --ev-bg-elevated:            #141820;
  --ev-bg-card:                #1a1f2a;
  --ev-bg-paper:               #f6f3ed;   /* Light / archival */
  --ev-bg-surface:             #ffffff;

  /* ── Text ── */
  --ev-text-primary:           #f1f5f9;   /* On dark backgrounds */
  --ev-text-secondary:         #94a3b8;
  --ev-text-muted:             #64748b;
  --ev-text-ink:               #0b0d10;   /* On light backgrounds */

  /* ── Font ── */
  --ev-font-sans:              'Inter', ui-sans-serif, system-ui, sans-serif;
  --ev-font-serif:             'Merriweather', ui-serif, Georgia, serif;
  --ev-font-mono:              'JetBrains Mono', ui-monospace, monospace;

  /* ── Size (type scale) ── */
  --ev-size-xs:                0.75rem;   /* 12px */
  --ev-size-sm:                0.875rem;  /* 14px */
  --ev-size-base:              1rem;      /* 16px */
  --ev-size-lg:                1.125rem;  /* 18px */
  --ev-size-xl:                1.25rem;   /* 20px */
  --ev-size-2xl:               1.5rem;    /* 24px */
  --ev-size-3xl:               2rem;      /* 32px */
  --ev-size-4xl:               2.5rem;    /* 40px */

  /* ── Spacing ── */
  --ev-space-xs:               0.25rem;   /* 4px */
  --ev-space-sm:               0.5rem;    /* 8px */
  --ev-space-md:               1rem;      /* 16px */
  --ev-space-lg:               1.5rem;    /* 24px */
  --ev-space-xl:               2rem;      /* 32px */
  --ev-space-2xl:              3rem;      /* 48px */
  --ev-space-3xl:              4rem;      /* 64px */

  /* ── Radius ── */
  --ev-radius-sm:              4px;
  --ev-radius-md:              8px;
  --ev-radius-lg:              12px;
  --ev-radius-xl:              16px;
  --ev-radius-full:            9999px;

  /* ── Shadow ── */
  --ev-shadow-sm:              0 1px 2px rgb(0 0 0 / 0.15);
  --ev-shadow-md:              0 4px 8px rgb(0 0 0 / 0.2);
  --ev-shadow-lg:              0 10px 20px rgb(0 0 0 / 0.25);
  --ev-shadow-focus:           0 0 0 3px rgb(47 93 159 / 0.4);

  /* ── Duration ── */
  --ev-dur-fast:               120ms;
  --ev-dur-normal:             200ms;
  --ev-dur-slow:               350ms;

  /* ── Ease ── */
  --ev-ease-default:           cubic-bezier(0.2, 0, 0, 1);
  --ev-ease-out:               cubic-bezier(0, 0, 0.2, 1);

  /* ── Z-Index ── */
  --ev-z-base:                 1;
  --ev-z-dropdown:             100;
  --ev-z-sticky:               200;
  --ev-z-overlay:              300;
  --ev-z-modal:                400;
  --ev-z-toast:                500;
}
```

### 4.3 Tillerstead Family Tokens (Starter)

Derived from the existing `root-vars.css` and `brand.yml`.

```css
/* === tillerstead.foundation.css === */

:root {
  /* ── Color ── */
  --ts-color-primary:          #00e184;   /* Emerald */
  --ts-color-primary-hover:    #3bf0aa;
  --ts-color-primary-active:   #00b46a;
  --ts-color-accent:           #d4af37;   /* Gold */
  --ts-color-accent-hover:     #f2d75c;
  --ts-color-danger:           #f87171;
  --ts-color-success:          #00e184;
  --ts-color-warning:          #d4af37;
  --ts-color-info:             #38bdf8;

  --ts-color-primary-accessible: #008f5d;  /* WCAG AA */
  --ts-color-accent-accessible:  #8c6a12;  /* WCAG AA */

  /* ── Background ── */
  --ts-bg-ink:                 #000000;
  --ts-bg-elevated:            #0f0f0f;
  --ts-bg-card:                #161616;
  --ts-bg-hover:               #222222;
  --ts-bg-surface:             #ffffff;

  /* ── Text ── */
  --ts-text-primary:           #ffffff;
  --ts-text-secondary:         #e5e7eb;
  --ts-text-tertiary:          #9ca3af;
  --ts-text-muted:             #6b7280;
  --ts-text-ink:               #0f0f0f;

  /* ── Font ── */
  --ts-font-sans:              'Inter', ui-sans-serif, system-ui, sans-serif;
  --ts-font-display:           'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
  --ts-font-mono:              'JetBrains Mono', ui-monospace, monospace;

  /* ── Size (fluid type scale) ── */
  --ts-size-xs:                clamp(0.75rem, 1vw, 0.875rem);
  --ts-size-sm:                clamp(0.875rem, 1.2vw, 1rem);
  --ts-size-base:              clamp(1rem, 1.5vw, 1.125rem);
  --ts-size-lg:                clamp(1.125rem, 2vw, 1.25rem);
  --ts-size-xl:                clamp(1.25rem, 2.5vw, 1.5rem);
  --ts-size-2xl:               clamp(1.5rem, 3vw, 2rem);
  --ts-size-3xl:               clamp(2rem, 4vw, 3rem);
  --ts-size-4xl:               clamp(2.5rem, 5vw, 4rem);

  /* ── Spacing (fluid) ── */
  --ts-space-xs:               clamp(0.25rem, 0.5vw, 0.5rem);
  --ts-space-sm:               clamp(0.5rem, 1vw, 0.75rem);
  --ts-space-md:               clamp(1rem, 2vw, 1.5rem);
  --ts-space-lg:               clamp(1.5rem, 3vw, 2.5rem);
  --ts-space-xl:               clamp(2rem, 4vw, 4rem);
  --ts-space-2xl:              clamp(3rem, 6vw, 6rem);

  /* ── Radius ── */
  --ts-radius-sm:              4px;
  --ts-radius-md:              8px;
  --ts-radius-lg:              12px;
  --ts-radius-xl:              16px;

  /* ── Shadow ── */
  --ts-shadow-md:              0 4px 8px rgb(0 0 0 / 0.5);
  --ts-shadow-lg:              0 10px 20px rgb(0 0 0 / 0.6);
  --ts-shadow-glow-primary:    0 0 20px rgb(0 225 132 / 0.3);
  --ts-shadow-glow-accent:     0 0 15px rgb(212 175 55 / 0.45);

  /* ── Duration ── */
  --ts-dur-fast:               150ms;
  --ts-dur-normal:             250ms;
  --ts-dur-slow:               400ms;

  /* ── Ease ── */
  --ts-ease-smooth:            cubic-bezier(0.4, 0, 0.2, 1);
  --ts-ease-bounce:            cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ── Z-Index ── */
  --ts-z-base:                 1;
  --ts-z-dropdown:             100;
  --ts-z-sticky:               200;
  --ts-z-overlay:              300;
  --ts-z-modal:                400;
  --ts-z-toast:                500;
}
```

### 4.4 Token Adoption Rules

| Repo Category | Token File | Required? |
|---------------|-----------|-----------|
| Main Evident suite | `evident.foundation.css` | Yes — import and use |
| Evident companion satellites | `evident.foundation.css` | Yes — import and use |
| Tillerstead family products | `tillerstead.foundation.css` | Yes — import and use |
| Independent / Personal | Neither | Optional — may define own |

**A satellite may extend its family's tokens** by adding product-specific
custom properties with its own prefix. Example: `--icc-color-calm: #a7c7e7;`
for a unique Informed Consent Companion accent, on top of the Evident
foundation palette.

**A satellite must not redefine or override** foundation token values. If a
color needs to change, it goes through a token review, not a local override.

---

## 5. Layer 4 — Component Patterns (Guided per Family)

These patterns are recommended, not mandated. Each describes the expected
structure for common UI elements. Repos may adapt them to their stack.

### 5.1 Navigation Pattern

**Evident family (institutional):**

```
┌──────────────────────────────────────────────┐
│  [Logo]   Nav Link  Nav Link  Nav Link  [CTA]│
└──────────────────────────────────────────────┘
```

- Horizontal top bar, sticky on scroll
- Logo left-aligned, primary nav centered or right-aligned
- Single CTA button (right edge) if applicable
- Mobile: hamburger → full-screen overlay or slide drawer
- Background: `--ev-bg-ink` or `--ev-bg-elevated`
- No dropdowns deeper than one level

**Tillerstead family (trade/professional):**

```
┌──────────────────────────────────────────────┐
│  [Logo + Tagline]   Nav  Nav  Nav   [CTA]    │
│  [Trust badges row — optional]               │
└──────────────────────────────────────────────┘
```

- Logo may include tagline or license number
- Trust badges (HIC, insured, TCNA) in a secondary bar
- Mobile: hamburger → drawer with service areas
- Background: dark with subtle grid overlay

### 5.2 Footer Pattern

**Evident family (minimal/institutional):**

```
┌──────────────────────────────────────────────┐
│  [Logo]  [Nav Links]  [Social]               │
│  ─────────────────────────────────────────── │
│  © 2026 Evident Technologies. All rights     │
│  reserved.  Privacy · Terms · Disclaimers    │
└──────────────────────────────────────────────┘
```

- Two rows: content row + legal band
- No more than 3 columns in the content row
- Social icons use a consistent icon set (Lucide or inline SVG)
- Legal band is always the last element on the page

**Tillerstead family (comprehensive):**

```
┌──────────────────────────────────────────────┐
│  [Logo]     │ [Service Areas] │ [Learn]      │
│  [Contact]  │ [Build Guides]  │ [Company]    │
│  ─────────────────────────────────────────── │
│  [Social]  [HIC Badge]  © 2026 Tillerstead   │
│  LLC. Privacy · Terms · Warranty · DMCA      │
└──────────────────────────────────────────────┘
```

- Multi-column grid with rich content (service areas, guides, contact)
- License/credential badges in the legal band
- More legal links (warranty, DMCA) reflecting trade obligations

### 5.3 Card Pattern

All products that display items in grids or lists should follow this structure:

```html
<article class="{prefix}-card">
  <div class="{prefix}-card-header">
    <!-- Badge/icon/status indicator -->
    <h3>Title</h3>
  </div>
  <div class="{prefix}-card-body">
    <!-- Content -->
  </div>
  <footer class="{prefix}-card-footer">
    <!-- Actions/metadata -->
  </footer>
</article>
```

- Semantic `<article>` element
- Three-zone internal structure (header, body, footer)
- Product prefix on all classes
- No fixed dimensions — cards are responsive by default

### 5.4 Badge and Status Indicator Pattern

Badges communicate state across the ecosystem. Consistent shapes and meanings
reduce cognitive load.

| Badge Type | Shape | Colors | Usage |
|-----------|-------|--------|-------|
| Status | Pill (border-radius: full) | Green=active, Yellow=pending, Red=error, Gray=inactive | Release status, account state, connection health |
| Trust credential | Rounded rectangle with icon | Gold outline on dark, dark outline on light | HIC license, compliance marks, certifications |
| Family label | Plain text, small caps | Muted text color | "by Evident Technologies" attribution |
| Version | Monospace pill | Neutral background | `v1.2.0`, `Beta`, `Alpha` |
| Role tag | Pill with colored left border | Color matches role (blue=core, green=companion, amber=venture) | Registry cards, manifest displays |

### 5.5 Icon Conventions

| Context | Recommended Source | Fallback |
|---------|--------------------|----------|
| React apps | Lucide React | Inline SVG |
| Jekyll / static sites | Inline SVG (hand-optimized) | SVG sprite |
| Web-builder | Inline SVG (self-contained) | Unicode symbols |

**Icon rules:**
- 24×24 default grid, 2px stroke weight
- Use `currentColor` for fill/stroke (inherits text color)
- No icon fonts (accessibility concern)
- No raster icons (scaling concern)
- Consistent metaphors: shield = security, file = document, scale = legal,
  badge = credential, lock = integrity

---

## 6. Layer 5 — Product Personality (Flexible, Per-Repo)

This layer is explicitly **not standardized**. Each product may express its own
character within the boundaries set by Layers 1–4.

### 6.1 What Can Vary

| Aspect | Flexibility |
|--------|-------------|
| Hero section design | Fully flexible — each product's hero is its own |
| Illustration style | No restriction |
| Accent color extensions | May add product-specific accents beyond foundation palette |
| Animation personality | May add motion within `prefers-reduced-motion` respect |
| Layout density | Dense (data tools) vs. spacious (marketing pages) |
| Dark/light mode default | Product chooses its default mode |
| Onboarding flow | Each product designs its own |
| Internal navigation depth | Sidebar, tabs, breadcrumbs — whatever fits |
| Content organization | Determined by the product's domain |
| Retro/specialty aesthetics | Tillerstead's grout grid, EGL's forensic theme — allowed |

### 6.2 What Must Not Vary

| Aspect | Reason |
|--------|--------|
| Legal footer band | Layer 1 requirement |
| Metadata `<head>` structure | Layer 2 requirement |
| Font families (within a family) | Layer 3 token |
| Semantic color meanings | Green=success, Red=error, Yellow=warning — never swapped |
| Accessibility minimums | WCAG 2.1 AA is floor, not ceiling |
| Copy tone rules | No superlatives or emotional hooks anywhere |

---

## 7. What Should Be Standardized vs. Flexible — Summary

### Standardized (Layers 1–3)

| Area | Scope | Enforcement |
|------|-------|-------------|
| Legal footer band | All repos | Mandatory — audit on deploy |
| `.evident-repo.json` manifest | All repos | Mandatory — machine-readable |
| `<head>` metadata template | All deployed pages | Required |
| CSS custom property naming | Per-family convention | Required — `--{brand}-{category}-{name}` |
| Product family labeling | Footer + about page | Required text patterns |
| Copy tone (no superlatives) | All user-facing text | Required |
| Naming conventions (slugs, classes, paths) | All repos | Required |
| Color semantics | Per-family token file | Required foundation tokens |
| Font family stacks | Per-family token file | Required foundation tokens |
| Accessibility minimum | All deployed pages | WCAG 2.1 AA required |
| `prefers-reduced-motion` | All animated elements | Required media query |
| Icon approach | Per-stack (Lucide/SVG) | Recommended |

### Flexible (Layers 4–5)

| Area | Scope | Guidance |
|------|-------|----------|
| Hero/landing design | Per product | Free expression |
| Layout structure | Per product | Fit the domain |
| Color extensions | Per product | Add accents, don't override foundation |
| Animation style | Per product | Within reduced-motion respect |
| Dark/light default | Per product | Product decides |
| Navigation depth | Per product | Fit the content |
| Card/list design | Per product | Follow card pattern structure, style freely |
| Illustration | Per product | No restriction |
| Retro/specialty themes | Per product | Allowed where appropriate |

---

## 8. How the Web-Builder Can Enforce Consistency

The web-builder already has a registry and manifest system. It can act as a
practical consistency checkpoint.

### 8.1 Token Injection on Export

When exporting to a registered repo, the web-builder can:

1. **Read the target's `.evident-repo.json`** `brand` field
2. **Inject the correct foundation token file** as a `<link>` or inline
   `<style>` block in the exported HTML
3. **Map generic builder colors** to the target family's token variables

This means a page built in the web-builder automatically gets `--ev-*` tokens
when exported to an Evident family repo, or `--ts-*` tokens when exported to a
Tillerstead family repo.

### 8.2 Metadata Prefill on Export

The export preflight already checks file structure. It can also:

1. **Pre-fill OG metadata** from the target repo's manifest (name, description,
   URL)
2. **Insert the correct legal footer band** based on the target's brand field
3. **Set `theme-color`** to match the target family's `--{brand}-bg-ink` value

### 8.3 Naming Validation

The export system can warn when:

- A filename uses spaces or uppercase (`My Page.html` → suggest `my-page.html`)
- CSS classes lack the expected prefix for the target family
- A `<title>` tag doesn't follow the `[Page] — [Product]` pattern

### 8.4 Consistency Checklist

Add a "Consistency" section to the export preflight panel:

| Check | Status |
|-------|--------|
| Foundation tokens linked | ✓ / ✗ |
| Legal footer band present | ✓ / ✗ |
| OG metadata complete | ✓ / ✗ |
| Filename convention | ✓ / ✗ |
| CSS prefix matches target | ✓ / ✗ |
| Title format correct | ✓ / ✗ |

These are informational warnings, not blocking errors. The operator can
override if they know what they're doing.

---

## 9. Suggested Starter Token/Branding Structure

### 9.1 File Layout

```
Evident/
├── docs/
│   └── architecture/
│       └── CROSS-REPO-CONSISTENCY.md    ← this document
├── tokens/
│   ├── evident.foundation.css           ← Evident family design tokens
│   ├── tillerstead.foundation.css       ← Tillerstead family design tokens
│   └── README.md                        ← Token documentation and usage guide
├── .evident-repo.json                   ← manifest (already exists)
└── ...

ventures/Tillerstead/
├── assets/css/
│   ├── root-vars.css                    ← existing (migrate to foundation)
│   └── ...
├── .evident-repo.json                   ← manifest (already exists)
└── ...
```

The `tokens/` directory lives in the Evident repo as the canonical source. Each
family's foundation file is self-contained CSS — no build step required. A
satellite repo can copy the file, link to it via CDN, or reference a git
submodule.

### 9.2 Migration Path

**Phase 1 — Publish foundation tokens** (immediate)

1. Create `tokens/evident.foundation.css` from existing Evident token files
2. Create `tokens/tillerstead.foundation.css` from existing Tillerstead root-vars
3. Create `tokens/README.md` with usage instructions
4. No existing code changes — these are new reference files

**Phase 2 — Align new work** (ongoing)

5. New pages in any Evident family repo import `evident.foundation.css`
6. New pages in any Tillerstead family repo import `tillerstead.foundation.css`
7. Web-builder export injects the correct file automatically
8. Existing pages are not retroactively changed (avoid churn)

**Phase 3 — Gradual migration** (as repos are touched)

9. When touching an existing page, swap hard-coded colors for token references
10. When creating a new satellite, start from the foundation tokens
11. When auditing a satellite, check Layer 1–2 compliance

### 9.3 Manifest Brand Field Reference

The `.evident-repo.json` `brand` field determines which tokens apply:

| `brand` value | Foundation file | Token prefix |
|---------------|----------------|--------------|
| `evident` | `evident.foundation.css` | `--ev-` |
| `tillerstead` | `tillerstead.foundation.css` | `--ts-` |
| (empty or other) | None required | Custom prefix |

---

## 10. Current State Audit — What Needs to Change

| Finding | Current State | Target State | Priority |
|---------|---------------|--------------|----------|
| Token naming | 4+ prefix conventions (`--ff-`, `--tiller-`, `--ink`, `--color-*`) | Two standardized prefixes (`--ev-`, `--ts-`) | High — new work only |
| Typography | 5 different font combinations across repos | 2 canonical stacks (per family) | Medium — gradual |
| Footer legal band | Present in Tillerstead, partial in Evident, missing in React apps | Present in all deployed pages | High |
| OG metadata | Complete in Tillerstead/Founder-Hub, missing in React apps | Complete everywhere | Medium |
| CSS class prefixes | Inconsistent (`.ts-`, `.ff-`, `.ev-`, unprefixed) | Consistent per-family prefix | Low — new work only |
| Copy tone | Tillerstead has voice guide; others improvise | All repos reference copy conventions | Medium |
| Brand guidelines | Only Tillerstead has comprehensive guide | Each family has a token file + this document | Medium |
| Foundation token files | Non-existent as standalone files | Published in `tokens/` | High — immediate |
| `.evident-repo.json` | Exists in 3 repos | Exists in all repos | Medium — as repos are touched |
| Accessibility variants | Tillerstead has `*-accessible`; Evident partial | Both foundation files include accessible variants | High |

---

## 11. Governance

This document is the canonical reference for cross-repo consistency. It is
maintained in the Evident repository at
`docs/architecture/CROSS-REPO-CONSISTENCY.md`.

**Review cadence:** When a new satellite is created or an existing one is
significantly redesigned.

**Enforcement:** Layers 1–2 are auditable (check for footer, metadata,
manifest). Layers 3–5 are advisory. The web-builder provides automated
assistance but does not block exports.

**Version:** This document follows the same `sharedStandardsVersion` field in
`.evident-repo.json`. When this document changes materially, increment the
version and note it in the manifests.
