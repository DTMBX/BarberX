# Evident Brand Guide

**Legal Entity:** Evident Technologies, LLC  
**DBA:** EVIDENT  
**Est.:** 2024

--

## Brand Identity

### Primary Tagline

**"Cut away all the extra. Get to the truth."**

Followed by the single-word brand voice: **Evident.**

### Mission Statement

Born from lived experience. Evidence processing shouldn't require guesswork or
endless hours. EVIDENT aims to change that.

### Core Values

- **Truth before persuasion** — Facts over spin
- **Integrity before convenience** — Doing it right, not fast
- **Restraint before expression** — Professional discipline
- **Due process before outcomes** — System integrity matters
- **Structure before style** — Architecture over decoration

--

## Visual Identity

### Scales of Justice

The scales of justice icon represents our commitment to legal integrity:

- **Geometric Design**: Clean lines, professional restraint
- **Blue & Gold**: Evident brand colors (trust and authority)
- **Balanced**: Representing fairness and due process
- **Modern**: Contemporary interpretation of classical symbol

### Usage

- Header: Nav-sized (24px height)
- Footer: Small (32px height)
- Decorative: Medium (48px height)
- Hero: Large (64-80px height)

--

## Color Palette

### Primary Colors (Evident Brand)

```css
--color-primary: #2F5D9F  /* Evident Blue - trust, authority */
--color-accent: #F7B32B   /* Gold - clarity, illumination */
--color-fg: #0B0D10       /* Near black - text */
--color-bg: #F8FAFC       /* Paper white - surface */
```

### Semantic Colors

```css
--color-success: #10b981  /* Green - verification complete */
--color-warning: #f59e0b  /* Amber - attention needed */
--color-error: #ef4444    /* Red - critical issue */
--color-info: #3b82f6     /* Blue - informational */
```

### Neutrals (Slate Scale)

```css
--color-slate-50: #f8fafc
--color-slate-100: #f1f5f9
--color-slate-200: #e2e8f0
--color-slate-300: #cbd5e1
--color-slate-400: #94a3b8
--color-slate-500: #64748b
--color-slate-600: #475569
--color-slate-700: #334155
--color-slate-800: #1e293b
--color-slate-900: #0f172a
--color-slate-950: #020617
```

--

## Typography

### Font Stack

```css
--font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Weights

- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700

--

## Spacing & Layout

### The 4px Grid

All spacing follows a 4px base unit:

```
4px → 8px → 12px → 16px → 24px → 32px → 48px → 64px → 96px
```

### Border Radius (Professional Restraint)

- XS: 4px — Small elements
- SM: 8px — Buttons, inputs
- MD: 12px — Cards
- LG: 16px — Panels
- XL: 24px — Large containers
- 2XL: 32px — Hero sections
- Full: 9999px — Pills, circular elements

--

## Transitions

### Easing Functions

- **Smooth**: `cubic-bezier(0.4, 0, 0.2, 1)` — Default, clean
- **Bounce**: `cubic-bezier(0.68, -0.55, 0.265, 1.55)` — Playful
- **Elastic**: `cubic-bezier(0.68, -0.25, 0.265, 1.25)` — Subtle spring

### Durations

- **Instant**: 100ms — Micro-interactions
- **Fast**: 200ms — Hover states
- **Base**: 300ms — Default transitions
- **Slow**: 500ms — Large movements
- **Slower**: 700ms — Dramatic effects

**Rule**: Every interactive element should have a smooth transition.

--

## Shadows & Depth

### Elevation Levels

```css
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06) /* Subtle lift */ --shadow-md: 0 4px 8px
  rgba(0, 0, 0, 0.08) /* Card depth */ --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.1) /* Modals */
  --shadow-xl: 0 16px 32px rgba(0, 0, 0, 0.12) /* Overlays */;
```

### Glows (Brand Accents)

```css
--shadow-glow-red: 0 0 24px rgba(196, 30, 58, 0.2) --shadow-glow-blue: 0 0 24px
  rgba(30, 64, 175, 0.2) --shadow-glow-gold: 0 0 24px rgba(212, 165, 116, 0.2);
```

--

## Brand Messages

### Consistent Copy

- **Primary Tagline**: "Cut away all the extra. Get to the truth."
- **Brand Voice Closer**: "Evident."
- **Footer Mission**: "Born from lived experience. Evidence processing shouldn't require guesswork or endless hours."
- **Legal Entity**: "Evident Technologies, LLC"
- **DBA**: "EVIDENT"
- **Est. Date**: "EST. 2024"

### Tone of Voice

- Mission-driven with professional humor from lived experience
- Direct and restrained, not playful
- Truth before persuasion
- Empathetic without being sentimental
- Confident through discipline, not hype

--

## Accessibility

### Motion Preferences

Always respect `prefers-reduced-motion`:

- Disable all animations
- Maintain functionality without motion
- Reduce opacity slightly to indicate "paused" state

### Color Contrast

- All text meets WCAG AA standards (4.5:1 minimum)
- Interactive elements have clear focus states
- Never rely on color alone to convey information

### Keyboard Navigation

- All interactive elements keyboard accessible
- Clear focus indicators
- Logical tab order

--

## File Structure

### Brand Assets

```
assets/
├── css/
│   ├── brand-tokens.css              # Color, spacing, transitions
│   ├── components/
│   │   ├── barber-pole-spinner.css   # The iconic pole
│   │   └── barber-branding.css       # Header/footer integration
│   └── style.css                     # Main styles
└── img/
    └── logo/
        ├── barbercam-header-lockup.svg
        └── barbercam-footer-min.svg
```

--

## Implementation Checklist

When adding the barber pole to a new page:

- [ ] Include `brand-tokens.css` in layout head
- [ ] Include `barber-branding.css` for header/footer styles
- [ ] Include `barber-pole-spinner.css` for the component
- [ ] Add pole to header (nav size)
- [ ] Add pole to footer (small size)
- [ ] Add corner pole unless `hide_barber_pole: true` in front matter
- [ ] Verify smooth transitions on all interactive elements
- [ ] Test with `prefers-reduced-motion` enabled
- [ ] Verify mobile responsive behavior
- [ ] Check print styles hide decorative poles

--

**Remember**: Like a barber perfecting a fade, attention to detail makes the
difference between good and great. Every pixel, every transition, every shadow
should be intentional.

**A CUT ABOVE** ✂️
