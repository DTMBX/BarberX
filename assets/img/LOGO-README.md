# Evident Logo System - Official Brand Assets

**Version:** 2.0 (January 2026)  
**Status:** Production Ready  
**Designer:** Devon Tyler (DTMB)

---

## Logo Variants & Usage Guide

### 📁 Available Logo Files

#### **1. Standard Logos (Light Backgrounds)**

| File | Dimensions | Use Case | Background |
|------|------------|----------|------------|
| `logo-Evident-horizontal.svg` | 360×80 | Navigation headers, light pages | White, light gray |
| `logo-Evident-full.svg` | Full size | Hero sections, large displays | Light backgrounds |
| `logo-Evident-icon.svg` | Square | Favicon, app icons, avatars | Light backgrounds |

**Color Scheme (Light Variant):**
- Primary Navy: `#0a1f44`
- Steel Gray: `#64748b`
- Muted Red: `#b91c1c`

---

#### **2. Dark Surface Logos (Dark Backgrounds)** ✨ NEW

| File | Dimensions | Use Case | Background |
|------|------------|----------|------------|
| `logo-Evident-horizontal-dark.svg` | 360×80 | Dark hero sections, modals | Dark navy, charcoal |
| `logo-Evident-footer.svg` | 300×60 | **Footer sections** (optimized) | Navy `#0a1f44`, dark blue |

**Color Scheme (Dark Variant):**
- Primary Light: `#f8fafc` / `#e2e8f0` (white/off-white)
- Accent Gold: `#D4C470` / `#C5B358` (visible on dark)
- Accent Red: `#f87171` / `#ef4444` (bright red)
- Text Light: `#ffffff` (pure white)
- Text Muted: `#cbd5e1` (light gray)

**Key Enhancements:**
- ✅ High contrast white text (instead of navy)
- ✅ Gold star border (replaces dark red on light backgrounds)
- ✅ Brighter corner accent dots (red instead of dark red)
- ✅ Subtle glow effect option for very dark backgrounds
- ✅ Drop shadow support for depth

---

## Usage Examples

### ✅ **Correct Usage - Footer (Dark Background)**

```html
<!-- Use the footer-optimized logo -->
<footer style="background: #0a1f44; padding: 2rem;">
  <img 
    src="/assets/img/logo-Evident-footer.svg" 
    alt="Evident Legal Technologies"
    style="height: 50px; filter: drop-shadow(0 1px 3px rgba(0,0,0,0.3));"
  />
</footer>
```

### ✅ **Correct Usage - Navigation Header (Light Background)**

```html
<!-- Use the standard horizontal logo -->
<nav style="background: white;">
  <img 
    src="/assets/img/logo-Evident-horizontal.svg" 
    alt="Evident Legal Technologies"
    style="height: 60px;"
  />
</nav>
```

### ❌ **Incorrect Usage - Don't Do This**

```html
<!-- WRONG: Using light logo on dark background -->
<footer style="background: #0a1f44;">
  <img src="/assets/img/logo-Evident-horizontal.svg" /> <!-- Navy text invisible on navy -->
</footer>

<!-- WRONG: Using dark logo on light background -->
<nav style="background: white;">
  <img src="/assets/img/logo-Evident-footer.svg" /> <!-- White text invisible on white -->
</nav>
```

---

## Quick Reference Table

| Background Color | Logo File | Height | Additional Styling |
|-----------------|-----------|--------|-------------------|
| White / Light Gray | `logo-Evident-horizontal.svg` | 50-60px | None needed |
| Navy `#0a1f44` | `logo-Evident-footer.svg` | 45-50px | `filter: drop-shadow(...)` |
| Dark Charcoal | `logo-Evident-horizontal-dark.svg` | 50-70px | Optional glow |
| Hero Sections (Light) | `logo-Evident-full.svg` | 80-120px | None |
| Hero Sections (Dark) | `logo-Evident-horizontal-dark.svg` | 70-100px | `filter: drop-shadow(...)` |

---

## Technical Specifications

### SVG Structure

All logos use:
- **Viewbox-based scaling** (no fixed pixel sizes)
- **CSS classes** for colors (easy theme switching)
- **Clean semantic markup** (accessible, SEO-friendly)
- **Embedded fonts** (Rockwell, Georgia fallbacks)

### Color Accessibility

**Light Logo (WCAG AAA Compliant):**
- Navy `#0a1f44` on white: **Contrast Ratio 14.5:1** ✅
- Gray `#64748b` on white: **Contrast Ratio 4.8:1** ✅

**Dark Logo (WCAG AAA Compliant):**
- White `#ffffff` on Navy `#0a1f44`: **Contrast Ratio 14.5:1** ✅
- Light Gray `#cbd5e1` on Navy: **Contrast Ratio 9.2:1** ✅

---

## Implementation Checklist

- [x] Standard horizontal logo (light backgrounds)
- [x] Dark surface horizontal logo (dark backgrounds)
- [x] Footer-optimized logo (compact, high contrast)
- [x] Icon/square logo (favicon, avatars)
- [x] Full-size logo (hero sections)
- [x] Updated landing-public.html footer
- [x] Updated about.html footer
- [ ] Update all other dark footer instances
- [ ] Create PNG exports for email/print
- [ ] Add logo to brand guidelines

---

## Design Philosophy

**"Constitutional Precision in Every Pixel"**

The Evident logo system reflects our core values:

1. **Precision:** Clean geometric shapes, precise alignment
2. **Integrity:** High contrast, accessible, honest design
3. **Constitutional:** Star symbolism (50 stars = 50 states), patriotic colors
4. **Professional:** Serif typography (Rockwell), legal industry standard
5. **Adaptive:** Works on any background while maintaining brand identity

**The Star Symbol:**
- Represents the 50 states of the Union
- Honors the 1.3 million Americans who died defending the Constitution
- Connects to our constitutional literacy mission

**Color Meaning:**
- **Navy Blue:** Authority, trust, legal professionalism
- **Gold:** Excellence, constitutional importance
- **Red:** Vigilance, courage, sacrifice

---

## File Maintenance

**Last Updated:** January 29, 2026  
**Updated By:** Devon Tyler  
**Changes:** Added dark surface variants for footer optimization

**Version History:**
- v2.0 (2026-01): Dark surface variants, footer optimization
- v1.0 (2025): Initial logo system

---

## Contact

**Questions about logo usage?**  
Contact: devon@Evident.info  
Brand Guidelines: `/docs/brand-guidelines.md`  
Design System: `/docs/design-system.md`

---

**License:** Proprietary - Evident Legal Technologies (DTMB)  
**Copyright:** © 2026 All Rights Reserved  
**Usage:** Internal company use only - External usage requires written permission
