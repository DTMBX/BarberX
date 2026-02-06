# Evident Brand Guide

## Like a Fresh NYC Fade — Clean, Rounded, Crisp

**EST. 2024 | A CUT ABOVE**

--

## Brand Identity

### Tagline

**"A Cut Above"** — Precision, patience, virtue, and honor in every detail.

### Core Values

- **Precision**: Every line matters, every detail counts
- **Patience**: Quality takes time, rushing leads to mistakes
- **Virtue**: Built on integrity and ethical principles
- **Honor**: Respecting dignity and due process

--

## Visual Identity

### The Barber Pole

The classic 1920s spinning barber pole is our primary brand symbol:

- **Glass Cylinder**: Smooth, transparent, honest
- **Red, White, Blue Stripes**: Classic American Evident tradition
- **Brass Finials**: Premium quality, attention to detail
- **Spinning Motion**: Continuous progress, always working

### Usage

- Header: Nav-sized (18px × 48px)
- Footer: Small (24px × 64px)
- Decorative: Medium (36px × 100px) - default for page corners
- Hero: Large/Hero (56-70px × 180-220px)

--

## Color Palette

### Primary Colors (The Barber Trio)

```css
--barber-red: #c41e3a /* Classic barber red */ --barber-white: #ffffff
  /* Pure white */ --barber-blue: #1e40af /* Deep American blue */;
```

### Brass Accents

```css
--brass-light: #fff8dc /* Cornsilk highlight */ --brass-gold: #ffd700
  /* Gold shine */ --brass-mid: #d4a574 /* Vintage brass */
  --brass-dark: #daa520 /* Goldenrod depth */ --brass-shadow: #b8860b
  /* Dark goldenrod shadow */;
```

### Neutrals

```css
--ink: #0a0a0f /* Near black */ --ink-light: #1a1a2e /* Charcoal */
  --muted: #6b7280 /* Gray */ --bg: #fafafa /* Off white */ --card: #ffffff
  /* Pure white */;
```

--

## Typography

### Font Stack

```css
--font-display:
  "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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

### Border Radius (Rounded Like a Fade)

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
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06) /* Subtle lift */ --shadow-md: 0 4px
  8px rgba(0, 0, 0, 0.08) /* Card depth */ --shadow-lg: 0 8px 16px
  rgba(0, 0, 0, 0.1) /* Modals */ --shadow-xl: 0 16px 32px rgba(0, 0, 0, 0.12)
  /* Overlays */;
```

### Glows (Brand Accents)

```css
--shadow-glow-red: 0 0 24px rgba(196, 30, 58, 0.2) --shadow-glow-blue: 0 0 24px
  rgba(30, 64, 175, 0.2) --shadow-glow-gold: 0 0 24px rgba(212, 165, 116, 0.2);
```

--

## Brand Messages

### Consistent Copy

- **Footer tagline**: "Precision. Patience. Virtue. Honor."
- **Footer motto**: "Built with precision in NYC. Like a fresh fade — clean, rounded, crisp."
- **EST date**: "EST. 2024"
- **Slogan**: "A CUT ABOVE"

### Tone of Voice

- Professional but approachable
- Confident without arrogance
- Detail-oriented but not pedantic
- Respectful of the craft

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

**Remember**: Like a barber perfecting a fade, attention to detail makes the difference between good and great. Every pixel, every transition, every shadow should be intentional.

**A CUT ABOVE** ✂️
