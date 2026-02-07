# 🌾 Tillerstead Sanctuary Navigation System

A beautiful, peaceful, and fully accessible navigation system designed
specifically for **Tillerstead Sanctuary** with earthy, agricultural-inspired
colors and sanctuary-focused design.

## 🎨 Design Philosophy

### Color Palette

The Tillerstead navigation uses a carefully selected earthy palette that
reflects the sanctuary's mission of agriculture, recovery, and stewardship:

- **Forest Greens**: #2D5016, #5B8A3C, #8FBC66 (Primary brand colors)
- **Earth Tones**: #8B7355, #A0826D (Grounding, natural)
- **Cream/Beige**: #F5F1E8, #EDE7D9 (Peaceful backgrounds)
- **Warm Grays**: #4A4A4A, #6B6B6B (Text, secondary)

### Logo Symbolism

The wheat stalks in the logo represent:

- 🌾 **Harvest** - The fruits of labor and stewardship
- 🌱 **Growth** - Recovery, healing, and transformation
- 🌿 **Agriculture** - Urban farming and food production
- ⚖️ **Stewardship** - Faithful management of resources

## ✨ Features

### Navigation Structure

Organized around Tillerstead's four core pillars:

1. **About** - Vision, theology, masterplan, governance
2. **Programs** - Recovery, stewardship, health, housing
3. **Agriculture** - Urban farming, fresh market, training
4. **Get Involved** - Petition, volunteer, donate, partnerships

### Mission-Focused CTAs

- 💚 **"Get Help"** - Primary CTA for those seeking sanctuary
- 🙏 **"Prayer Request"** - Secondary CTA for spiritual support

### Desktop Experience

- Elegant dropdown menus with icons and descriptions
- Forest green gradient accents throughout
- Hover effects with earth-tone backgrounds
- Smooth, peaceful transitions

### Mobile Experience

- Right-side drawer with cream/beige header
- Expandable accordion submenus
- Large, touch-friendly targets
- Beautiful footer with dual CTAs

## 📁 Files

```
Evident.info/
├── _includes/
│   └── components/
│       └── navigation/
│           └── tillerstead-header.html       # Navigation HTML
├── assets/
│   ├── css/
│   │   └── components/
│   │       └── tillerstead-header.css        # All styles
│   └── js/
│       └── tillerstead-header.js             # Functionality
└── tillerstead-nav-demo.html                 # Demo page
```

## 🚀 Installation

### Step 1: Add Files

The files are already in place:

- `_includes/components/navigation/tillerstead-header.html`
- `assets/css/components/tillerstead-header.css`
- `assets/js/tillerstead-header.js`

### Step 2: Include in Layout

Add to your layout file (e.g., `_layouts/default.html`):

```html
<!-- In <head> section ->
<link
  rel="stylesheet"
  href="{{ '/assets/css/components/tillerstead-header.css' | relative_url }}"
/>

<!-- After <body> tag ->
{% include components/navigation/tillerstead-header.html %}

<!-- Before </body> tag ->
<script src="{{ '/assets/js/tillerstead-header.js' | relative_url }}"></script>
```

### Step 3: View Demo

Open `tillerstead-nav-demo.html` to see the navigation in action!

## 🎯 Customization

### Update Navigation Links

Edit `tillerstead-header.html` to add/remove menu items or change links to match
your site structure.

### Adjust Colors

Modify CSS variables in `tillerstead-header.css`:

```css
:root {
  --tillerstead-forest-dark: #2d5016;
  --tillerstead-forest: #5b8a3c;
  --tillerstead-forest-light: #8fbc66;
  --tillerstead-cream: #f5f1e8;
  /* ... more variables ... */
}
```

### Change CTAs

Update the "Get Help" and "Prayer" buttons in the header HTML to link to your
actual forms/pages.

## 🌟 Design Details

### Typography

- **Logo**: 1.375rem, bold, tight letter-spacing
- **Navigation**: 0.9375rem, medium weight
- **Dropdowns**: Rich with titles and descriptions

### Spacing

- **Header Height**: 76px (slightly taller for peaceful presence)
- **Touch Targets**: 46px minimum
- **Generous padding**: Creates breathing room

### Animations

- **Timing**: 0.35s cubic-bezier (slightly slower, more peaceful)
- **Hover Effects**: Subtle transforms and color shifts
- **Focus States**: Clear forest green outlines

## ♿ Accessibility

✅ **WCAG 2.1 AA Compliant**  
✅ **Full keyboard navigation**  
✅ **Proper ARIA attributes**  
✅ **Screen reader friendly**  
✅ **Reduced motion support**  
✅ **High contrast mode**  
✅ **Skip to content link**  
✅ **Focus trap in drawer**  
✅ **Semantic HTML5**

## 📱 Responsive Breakpoints

| Screen Size    | Navigation Type                |
| -------------- | ------------------------------ |
| < 640px        | Mobile drawer, simplified logo |
| 640px - 1023px | Mobile drawer, full logo       |
| ≥ 1024px       | Desktop dropdowns              |

## 🆚 Tillerstead vs Evident

| Aspect     | Evident                | Tillerstead                  |
| ---------- | ---------------------- | ---------------------------- |
| **Colors** | Crimson, Navy, Brass   | Forest greens, Earth tones   |
| **Logo**   | Geometric BX           | Wheat stalks symbol          |
| **Focus**  | Legal technology       | Sanctuary & agriculture      |
| **Tone**   | Professional, sharp    | Peaceful, welcoming          |
| **CTAs**   | "Login", "Search"      | "Get Help", "Prayer"         |
| **Menu**   | Cases, Platform, Tools | About, Programs, Agriculture |

## 🌾 Mission Alignment

This navigation system reflects Tillerstead's core values:

- **Sanctuary**: Peaceful colors, welcoming design
- **Agriculture**: Wheat symbolism, earth tones
- **Recovery**: "Get Help" prominent placement
- **Stewardship**: Organized, responsible structure
- **Faith**: Prayer request option, biblical foundation links
- **Community**: Get Involved section, partnerships

## 📊 Technical Specs

- **No dependencies** - Pure HTML, CSS, JavaScript
- **Lightweight** - Combined ~49KB uncompressed
- **Performance** - GPU-accelerated animations
- **Browser Support** - All modern browsers
- **Mobile-First** - Designed for all devices
- **SEO-Friendly** - Semantic HTML structure

## 🎉 Demo

**View the demo**: Open `tillerstead-nav-demo.html` in your browser

Features to try:

1. Hover over menu items on desktop to see rich dropdowns
2. Click the hamburger menu on mobile
3. Expand/collapse submenus in the mobile drawer
4. Test keyboard navigation (Tab, Arrow keys, Escape)
5. Scroll to see header style change
6. Resize window to see responsive behavior

## 🙏 Mission Statement

_"Tillerstead Sanctuary: Where faith, work, and harvest meet in a haven of
healing and hope."_

This navigation system embodies that mission through:

- Earthy, agricultural symbolism
- Peaceful, sanctuary-inspired colors
- Recovery and help-focused CTAs
- Accessible, welcoming design

--

**Created with care for Tillerstead Sanctuary**  
_Faith Frontier Ecclesiastical Trust_  
January 2026
