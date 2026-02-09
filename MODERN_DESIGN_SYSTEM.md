# Modern Design System Implementation

**Evident Technologies** – Professional-grade, accessible web design  
**Status:** Complete & Production-Ready  
**Last Updated:** February 8, 2026

---

## Overview

Your website has been completely modernized with a clean, flexible, professional design system. This document describes what was updated, how to use it, and how to customize it for your brand.

### What Changed

✅ **Design Tokens** – CSS custom properties for colors, spacing, typography  
✅ **Component Library** – Pre-built, reusable UI elements  
✅ **Modern HTML** – Semantic markup with accessibility built-in  
✅ **Responsive Design** – Mobile-first, works on all devices  
✅ **Dark Mode** – Automatic system preference detection  
✅ **Open Source** – Zero proprietary dependencies  
✅ **Performance** – Minimal CSS, optimized fonts, fast loading

---

## Architecture

### File Structure

```
evident/
├── _layouts/
│   └── default.html              Modern base template (semantic HTML)
├── assets/
│   ├── css/
│   │   ├── design-tokens.css     Color, spacing, typography tokens
│   │   ├── components.css        Buttons, cards, forms, alerts
│   │   ├── utilities.css         Layouts, grids, spacing helpers
│   │   └── styles.css            Page-specific styles
│   └── js/
│       ├── navigation.js         Mobile menu with keyboard nav
│       └── theme.js              Dark mode toggle & system pref
├── DESIGN_SYSTEM.md              This documentation
└── tailwind.config.js            Tailwind CSS configuration
```

### Design Token System

All design decisions are stored as CSS variables in `assets/css/design-tokens.css`:

```css
:root {
  /* Colors */
  --color-primary-500: #0b73d2; /* Brand blue */
  --color-accent-500: #e07a5f; /* Accent orange */
  --color-text-primary: #0d0f12; /* Main text */

  /* Spacing (4px baseline) */
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;

  /* Typography */
  --font-size-base: 1rem;
  --font-weight-bold: 700;

  /* Borders & Shadows */
  --radius-lg: 0.75rem;
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

**Usage:** Any CSS file can reference these:

```css
.my-element {
  color: var(--color-text-primary);
  padding: var(--spacing-6);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
```

---

## Components

### Buttons

```html
<!-- Primary (main CTA) -->
<button class="btn btn-primary">Get Started</button>

<!-- Secondary -->
<button class="btn btn-secondary">Learn More</button>

<!-- Outline -->
<button class="btn btn-outline">Explore</button>

<!-- Ghost (minimal) -->
<button class="btn btn-ghost">Skip</button>

<!-- Sizes -->
<button class="btn btn-sm">Small</button>
<button class="btn btn-lg">Large</button>

<!-- Icon only -->
<button class="btn-icon btn-ghost">
  <svg>...</svg>
</button>
```

### Cards

```html
<!-- Basic card -->
<div class="card">
  <h3>Feature Title</h3>
  <p>Description text</p>
</div>

<!-- Elevated card -->
<div class="card card-elevated">Content</div>

<!-- With accent border -->
<div class="card card-border-accent">Content</div>
```

### Forms

```html
<form>
  <div class="form-group">
    <label for="name">Name</label>
    <input type="text" id="name" placeholder="Enter your name" />
  </div>

  <div class="form-group">
    <label for="message">Message</label>
    <textarea id="message"></textarea>
  </div>

  <button class="btn btn-primary">Submit</button>
</form>
```

### Alerts

```html
<div class="alert alert-info">ℹ️ Informational message</div>
<div class="alert alert-success">✓ Success message</div>
<div class="alert alert-warning">⚠️ Warning message</div>
<div class="alert alert-error">✕ Error message</div>
```

### Badges

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-accent">Featured</span>
<span class="badge badge-success">Active</span>
```

### Navigation

```html
<nav class="primary-nav">
  <a href="/" class="nav-link active">Home</a>
  <a href="/about/" class="nav-link">About</a>
  <a href="/docs/" class="nav-link">Docs</a>
</nav>
```

---

## Layouts

### Container

```html
<div class="layout-container">
  <!-- Max-width: 1280px, centered, responsive padding -->
</div>
```

### Grids

```html
<!-- 2-column grid, auto-responsive -->
<div class="layout-grid-2">
  <div>Column 1</div>
  <div>Column 2</div>
</div>

<!-- 3-column grid -->
<div class="layout-grid-3">
  <div>Col 1</div>
  <div>Col 2</div>
  <div>Col 3</div>
</div>

<!-- 4-column grid -->
<div class="layout-grid-4">...</div>
```

### Flexbox Layouts

```html
<!-- Flex row with wrapping -->
<div class="layout-flex">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Flex column -->
<div class="layout-flex-column">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Centered flex -->
<div class="layout-flex-center">
  <div>Centered content</div>
</div>

<!-- Space between -->
<div class="layout-flex-between">
  <div>Left</div>
  <div>Right</div>
</div>
```

---

## Typography

### Headings

```html
<h1>Page Title (5xl)</h1>
<!-- 48px -->
<h2>Section Heading (4xl)</h2>
<!-- 36px -->
<h3>Subsection (3xl)</h3>
<!-- 30px -->
<h4>Minor Heading (2xl)</h4>
<!-- 24px -->
<h5>Small Heading (xl)</h5>
<!-- 20px -->
<h6>Tiny Heading (lg)</h6>
<!-- 18px -->
```

### Text Classes

```html
<p class="text-sm">Small text</p>
<p class="text-base">Normal text</p>
<p class="text-lg">Large text</p>

<p class="text-primary">Primary color</p>
<p class="text-secondary">Secondary color</p>
<p class="text-accent">Accent color</p>

<p class="font-medium">Medium weight</p>
<p class="font-bold">Bold text</p>
<p class="font-extrabold">Extra bold</p>

<p class="leading-tight">Tight line-height</p>
<p class="leading-normal">Normal line-height</p>
<p class="leading-relaxed">Relaxed line-height</p>
```

---

## Spacing Utilities

All spacing is based on 4px units for pixel-perfect layouts:

```html
<!-- Padding -->
<div class="py-4">Vertical padding 1rem</div>
<div class="py-6">Vertical padding 1.5rem</div>
<div class="py-12">Vertical padding 3rem</div>

<div class="px-4">Horizontal padding 1rem</div>
<div class="px-6">Horizontal padding 1.5rem</div>

<!-- Margin -->
<div class="mt-6">Margin top 1.5rem</div>
<div class="mb-8">Margin bottom 2rem</div>
```

---

## Customization

### Change Brand Colors

Edit `assets/css/design-tokens.css`:

```css
:root {
  --color-primary-500: #0b73d2; /* Change this blue */
  --color-accent-500: #e07a5f; /* Change this orange */
}
```

**All components automatically update.**

### Add New Colors

```css
:root {
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

Then create component variants:

```css
.btn-success {
  background-color: var(--color-success);
}
```

### Modify Spacing Scale

Edit the `--spacing-*` variables in `design-tokens.css`. Change the baseline from 4px to another value, and all spacing updates automatically.

### Extend Typography

Add new font sizes:

```css
:root {
  --font-size-6xl: 3.75rem;
  --font-size-7xl: 4.5rem;
}
```

Then use:

```html
<h1 style="font-size: var(--font-size-6xl)">Extra Large</h1>
```

### Add Responsive Breakpoints

Edit `utilities.css` media queries:

```css
@media (max-width: 1024px) {
  /* Tablet and below */
}

@media (max-width: 768px) {
  /* Mobile and above */
}

@media (max-width: 640px) {
  /* Small mobile */
}
```

---

## Accessibility

### Built-In Features

✅ **Semantic HTML** – `<header>`, `<nav>`, `<main>`, `<footer>`  
✅ **ARIA Labels** – Buttons and interactive elements  
✅ **Skip Links** – Jump to main content  
✅ **Keyboard Navigation** – Tab through all interactive elements  
✅ **Focus Indicators** – 3px blue ring (high contrast)  
✅ **Color Contrast** – WCAG AA+ compliant color pairs  
✅ **Form Labels** – Associated with inputs  
✅ **Error Messages** – Clear validation feedback  
✅ **Screen Reader** – `.visually-hidden` for supplemental content

### Testing Accessibility

```bash
# Validate HTML semantic structure
npm run lint

# Check color contrast
# https://webaim.org/resources/contrastchecker/

# Screen reader test (browser developer tools)
# Enable screen reader: Settings → Accessibility
```

---

## Responsive Design

### Mobile-First Approach

All styles are written for mobile first, then enhanced for larger screens:

```css
/* Mobile (default) */
.layout-grid-2 {
  grid-template-columns: 1fr;
}

/* Tablet & above (768px) */
@media (min-width: 768px) {
  .layout-grid-2 {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### Breakpoints

- **sm**: 640px (small mobile)
- **md**: 768px (tablet)
- **lg**: 1024px (desktop)
- **xl**: 1280px (large desktop)

### Responsive Text

Use `clamp()` for fluid typography:

```css
h1 {
  font-size: clamp(2rem, 5vw, 3.75rem);
  /* min: 2rem, preferred: 5% of viewport, max: 3.75rem */
}
```

---

## Performance

### Optimization Techniques

1. **CSS Variables** – Reduce duplicate declarations
2. **Minimal CSS** – Only include what you use
3. **System Fonts** – Fallback to native system fonts
4. **Google Fonts** – With `display=swap` for fast rendering
5. **Lazy Images** – `loading="lazy"` attribute
6. **Modern Formats** – WebP with PNG fallback

### Build Process

```bash
# Build CSS and HTML
npm run build

# Serve locally
npm run dev

# Validate
npm run lint:css
npm run format:check
```

---

## Dark Mode

### Automatic Detection

The site automatically switches based on system preference:

- **Light (default)** – 9am-9pm or user preference
- **Dark** – 9pm-9am or user preference

### Manual Toggle

Click the icon in the header to toggle:

```js
// In theme.js
const themeManager = new ThemeManager();
themeManager.toggleTheme();
```

### Default Colors by Mode

```css
/* Light mode (default in :root) */
--color-bg: #ffffff;
--color-text-primary: #0d0f12;

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0d0f12;
    --color-text-primary: #fafbfc;
  }
}
```

---

## Open Source Dependencies

All technologies used are open-source with permissive licenses:

| Tool         | License | Purpose               |
| ------------ | ------- | --------------------- |
| Tailwind CSS | MIT     | Utility CSS framework |
| PostCSS      | MIT     | CSS transformation    |
| Inter Font   | OFL 1.1 | Modern typeface       |
| Prettier     | MIT     | Code formatting       |
| ESLint       | MIT     | JavaScript linting    |

**Zero proprietary dependencies!**

---

## Browser Support

| Browser       | Version | Support      |
| ------------- | ------- | ------------ |
| Chrome        | 90+     | Full support |
| Firefox       | 88+     | Full support |
| Safari        | 14+     | Full support |
| Edge          | 90+     | Full support |
| Mobile Chrome | Latest  | Full support |
| Mobile Safari | 14+     | Full support |

---

## Troubleshooting

### Styles Not Applying

1. **Clear cache:** `Ctrl+Shift+Delete` or `Cmd+Shift+Delete`
2. **Rebuild CSS:** `npm run build:css`
3. **Check import:** Verify `design-tokens.css` is imported first

### Mobile Menu Not Working

1. **Check JavaScript:** Ensure `navigation.js` loaded
2. **Verify ID:** Button has `id="mobile-nav-btn"`
3. **Browser console:** Look for JavaScript errors

### Dark Mode Not Toggling

1. **Check browser:** Refresh and try again
2. **Storage:** Clear `localStorage` (DevTools → Application)
3. **System preference:** Change OS dark mode setting

---

## Next Steps

1. **Customize colors** for your brand (DESIGN_SYSTEM.md)
2. **Update logo** in `_layouts/default.html`
3. **Modify copy** and content sections
4. **Add pages** using the base template
5. **Deploy** to GitHub Pages (`g8-pages` branch)

---

## Getting Help

📖 **Documentation:** See DESIGN_SYSTEM.md
🎨 **Tools & Resources:**

- Tailwind CSS Docs: https://tailwindcss.com
- CSS Variables Guide: https://developer.mozilla.org/en-US/docs/Web/CSS/--*
- Web Accessibility: https://www.w3.org/WAI/

🐛 **Report Issues:** GitHub Issues tab

---

**Ready to build with Evident Design System!** 🚀
