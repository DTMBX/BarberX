# Mobile CSS Repair - Deprecated Files

## Date: January 29, 2026

## Summary
This document lists CSS and HTML files that have been deprecated or removed as part of the mobile CSS correctness repair. These files contained unsafe global overrides, conflicting rules, and broken navigation implementations.

## Deprecated CSS Files (DO NOT USE)

### Emergency Fix Files - **REMOVED/REPLACED**
These files forced `display: block !important` and `transform: none !important` globally, breaking all animations and the mobile navigation drawer.

1. **mobile-layout-emergency.css** → Replaced by `mobile-base.css`
   - Reason: Forced hiding of mobile nav drawer with `display: none !important`
   - Broke: Mobile navigation toggle and drawer
   - Impact: Navigation completely non-functional on mobile

2. **mobile-emergency-fix.css** → Replaced by `mobile-base.css`
   - Reason: Blanket `display: block !important` on all elements
   - Broke: Drawer transforms, overlays, accessibility
   - Impact: All interactive elements visible even when hidden

3. **mobile-critical-fix.css** → Removed
   - Reason: Duplicate of mobile-emergency-fix with additional conflicts
   - Broke: Z-index stacking, layering
   - Impact: Modals and drawers behind content

### Fix Cascade Conflicts - **DEPRECATED**
Files that fought each other with !important declarations:

4. **mobile-master-fix.css** → Consolidated into mobile-base.css
5. **header-emergency-fix.css** → Moved to navigation.css
6. **header-nav-critical-fixes.css** → Moved to navigation.css
7. **header-nav-fixed.css** → Removed (duplicate)
8. **desktop-layout-fix.css** → Removed (not needed with proper mobile-first)
9. **critical-ux-fixes.css** → Rules moved to appropriate components
10. **contrast-alignment-fix.css** → Contrast rules in accessibility.css
11. **button-contrast-fix.css** → Button styles in main.css
12. **nav-hero-text-fix.css** → Removed (incorrect approach)
13. **popup-fixes.css** → Modal/popup rules in components
14. **navigation-complete.css** → Duplicate of navigation.css
15. **mobile-ios-fixes.css** → iOS-specific rules in mobile-base.css
16. **mobile-header-nav-fixes.css** → Consolidated
17. **hero-fixes.css** → Hero styles in page-specific CSS
18. **contrast-fixes.css** → Accessibility.css
19. **scroll-fix.css** → Removed (incorrect body scroll handling)
20. **scaling-fixes.css** → Scaling in modern-devices.css

### Duplicate/Redundant Files - **DEPRECATED**

21. **tillerpro-contrast-fix.css** → Page-specific contrast in pages/tillerpro.css
22. **mobile-experience-fix-2026-01-28.css** → Consolidated into mobile-base.css
23. **mobile-homepage-beautiful.css** → Page-specific home.css

## Deprecated HTML Patterns

### Inline Styles in Templates - **REMOVED**

**File**: `_includes/layout/page-shell.html`

**Removed**: Inline `<style>` block (lines 4-50)
```html
<!-- THIS WAS REMOVED - DO NOT ADD BACK -->
<style>
  @media (max-width: 768px) {
    * { animation: none !important; transform: none !important; }
    .mobile-nav__toggle { display: none !important; }
  }
</style>
```

**Reason**: 
- Forced all content visible with `display: block !important`
- Disabled all animations globally
- **CRITICALLY**: Hid the mobile navigation toggle and drawer
- Created cascade conflicts with 60+ loaded stylesheets

**Impact**: Mobile navigation completely broken, no way to access menu

### Duplicate Stylesheet Loads - **CLEANED**

**File**: `_includes/layout/head.html`

**Before**: 73 CSS files loaded
**After**: 18 CSS files loaded (75% reduction)

**Removed duplicate/conflicting loads**:
- mobile-layout-emergency.css (line 14, 112)
- mobile-emergency-fix.css (line 15, 118)
- mobile-critical-fix.css (line 213)
- navigation-complete.css + navigation.css (duplicates)
- 15+ "fix" files with conflicting rules

## New Architecture

### Replacement Files

1. **mobile-base.css** - Proper mobile-first foundation
   - CSS layers: `@layer reset, tokens, mobile-base, base, layout, components, utilities`
   - NO blanket !important overrides
   - Proper mobile nav drawer implementation
   - Touch target sizing (WCAG 2.5.5)
   - Reduced motion support
   - Focus management

2. **head-clean.html** - Streamlined CSS loading
   - 18 CSS files (down from 73)
   - Proper cascade order
   - CSS layer declarations
   - No emergency inline styles
   - Conditional page-specific CSS

### Linting Infrastructure Added

Created configuration files:
- `.stylelintrc.json` - CSS linting
- `.eslintrc.cjs` - JavaScript linting
- `.htmlvalidate.json` - HTML validation
- `.prettierrc.json` - Code formatting

Added npm scripts:
- `npm run lint` - Run all linters
- `npm run lint:fix` - Auto-fix issues
- `npm run lint:css` - CSS only
- `npm run lint:js` - JavaScript only
- `npm run lint:html` - HTML validation
- `npm run format` - Prettier formatting

## Migration Guide

### For Developers

**DO THIS**:
```html
<!-- Use the new clean head -->
{% include layout/head-clean.html %}
```

**DON'T DO THIS**:
```html
<!-- Old bloated head with 73 CSS files -->
{% include layout/head.html %}

<!-- Inline emergency styles -->
<style>
  * { display: block !important; }
</style>
```

### CSS Architecture Rules

1. **NO global !important** except documented utility classes
2. **USE CSS layers** for predictable cascade
3. **SCOPE selectors** to components, not `*, body, div`
4. **MOBILE-FIRST** - base styles for mobile, enhance for desktop
5. **NO "fix" or "emergency" files** - fix the root cause

### Navigation Implementation

**Correct pattern** (mobile-base.css):
```css
/* Toggle visible */
.ts-nav-toggle {
  display: flex; /* NOT display: none */
}

/* Drawer hidden by default */
.ts-mobile-nav {
  transform: translateX(100%);
}

/* Drawer visible when opened */
.ts-mobile-nav[aria-hidden="false"] {
  transform: translateX(0);
}
```

**WRONG pattern** (deprecated emergency files):
```css
/* This breaks navigation */
.mobile-nav__toggle {
  display: none !important; /* ❌ Toggle invisible */
}
```

## Testing Checklist

After migration, verify:

- [ ] Mobile nav toggle visible on mobile (< 768px)
- [ ] Toggle opens drawer (transform: translateX(0))
- [ ] Drawer closes on overlay click
- [ ] Drawer closes on ESC key
- [ ] Body scroll locked when drawer open
- [ ] Focus trapped in drawer when open
- [ ] Focus returns to toggle on close
- [ ] No layout shift from emergency overrides
- [ ] Content visible without forced display: block
- [ ] Animations work (respect prefers-reduced-motion)
- [ ] Contrast meets WCAG AA (4.5:1 normal text)
- [ ] Touch targets minimum 44x44px

## File Deletion Checklist

Safe to delete (backed up in git history):

```bash
# Emergency fix files
rm assets/css/mobile-layout-emergency.css
rm assets/css/mobile-emergency-fix.css
rm assets/css/mobile-critical-fix.css
rm assets/css/mobile-master-fix.css
rm assets/css/header-emergency-fix.css

# Duplicate/conflicting fix files
rm assets/css/header-nav-critical-fixes.css
rm assets/css/header-nav-fixed.css
rm assets/css/desktop-layout-fix.css
rm assets/css/critical-ux-fixes.css
rm assets/css/contrast-alignment-fix.css
rm assets/css/button-contrast-fix.css
rm assets/css/nav-hero-text-fix.css
rm assets/css/popup-fixes.css
rm assets/css/navigation-complete.css
rm assets/css/hero-fixes.css
rm assets/css/contrast-fixes.css
rm assets/css/scroll-fix.css
rm assets/css/scaling-fixes.css

# Redundant mobile files
rm assets/css/mobile-ios-fixes.css
rm assets/css/mobile-header-nav-fixes.css
rm assets/css/mobile-experience-fix-2026-01-28.css
rm assets/css/mobile-homepage-beautiful.css
```

## Rollback Plan

If issues arise, git history contains all removed files:

```bash
# View file history
git log --all --full-history -- assets/css/mobile-emergency-fix.css

# Restore specific file
git checkout <commit-hash> -- assets/css/mobile-emergency-fix.css
```

**However**: Restoring these files will break mobile navigation again. Instead:
1. Check mobile-base.css for the correct pattern
2. Verify navigation.js is loaded and error-free
3. Ensure no inline styles override the drawer
4. Test with browser DevTools mobile emulation

## Support

Questions or issues? Check:
1. This DEPRECATION.md document
2. mobile-base.css comments
3. navigation.js documentation
4. Git commit messages for detailed changes

## References

- WCAG 2.5.5 Target Size: https://www.w3.org/WAI/WCAG21/Understanding/target-size.html
- CSS Cascade Layers: https://developer.mozilla.org/en-US/docs/Web/CSS/@layer
- Mobile-First CSS: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Responsive/Mobile_first
- ARIA Drawer Pattern: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
