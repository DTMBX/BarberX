# Elegant Navigation System

A beautiful, modern, and fully accessible navigation system designed for Evident
Legal Technologies.

## 🎨 Design Highlights

### Desktop Navigation

- **Elegant Dropdown Menus**: Rich dropdowns with icons, titles, and
  descriptions
- **Glassmorphism Header**: Modern backdrop blur effect with semi-transparent
  background
- **Smooth Animations**: Subtle hover effects and transitions throughout
- **Hover & Click Support**: Works with both mouse hover and touch/click
  interactions

### Mobile Navigation

- **Slide-in Drawer**: Smooth right-side drawer with elegant animations
- **Expandable Submenus**: Accordion-style navigation with chevron indicators
- **Touch-Optimized**: Large tap targets and smooth scrolling
- **Beautiful Footer**: Login CTA and branding at the bottom of drawer

## ✨ Features

### 🎯 User Experience

- **Responsive Design**: Seamlessly adapts from mobile to desktop
- **Smart Scroll Detection**: Header style changes subtly on scroll
- **Focus Management**: Proper focus handling when opening/closing menus
- **Body Scroll Lock**: Prevents background scrolling when drawer is open
- **Smooth Transitions**: All animations use cubic-bezier easing

### ♿ Accessibility

- **WCAG 2.1 AA Compliant**: Meets accessibility standards
- **Keyboard Navigation**: Full keyboard support with Tab, Arrow keys, Escape
- **ARIA Attributes**: Proper `aria-expanded`, `aria-hidden`, `aria-label`
- **Focus Visible States**: Clear focus indicators for keyboard users
- **Screen Reader Friendly**: Semantic HTML and descriptive labels
- **Skip to Content**: Quick navigation for keyboard users
- **Reduced Motion**: Respects user's motion preferences
- **High Contrast Mode**: Enhanced visibility in high contrast mode

### ⌨️ Keyboard Shortcuts

- **Ctrl+K (Cmd+K)**: Open search
- **Ctrl+M (Cmd+M)**: Toggle mobile menu (mobile only)
- **Tab / Shift+Tab**: Navigate between elements
- **Arrow Up/Down**: Navigate dropdown menu items
- **Escape**: Close active dropdown or drawer
- **Enter / Space**: Activate focused element

## 📁 File Structure

```
Evident.info/
├── _includes/
│   └── components/
│       └── navigation/
│           └── elegant-header.html      # Navigation HTML structure
├── assets/
│   ├── css/
│   │   └── components/
│   │       └── elegant-header.css       # All styles
│   └── js/
│       └── elegant-header.js            # Interactive functionality
└── elegant-nav-demo.html                # Demo page
```

## 🚀 Installation

### 1. Copy Files

Copy these three files to your project:

- `_includes/components/navigation/elegant-header.html`
- `assets/css/components/elegant-header.css`
- `assets/js/elegant-header.js`

### 2. Include in Layout

Add to your layout file (e.g., `_layouts/default.html`):

```html
<!-- In <head> section ->
<link
  rel="stylesheet"
  href="{{ '/assets/css/components/elegant-header.css' | relative_url }}"
/>

<!-- After <body> tag ->
{% include components/navigation/elegant-header.html %}

<!-- Before </body> tag ->
<script src="{{ '/assets/js/elegant-header.js' | relative_url }}"></script>
```

### 3. That's It!

The navigation is now active and fully functional. No configuration needed.

## 🎨 Customization

### Colors

Edit CSS variables in `elegant-header.css`:

```css
:root {
  --elegant-primary: #c41e3a; /* Primary brand color */
  --elegant-primary-dark: #a01729; /* Darker shade for hover */
  --elegant-secondary: #1e3a8a; /* Secondary color */
  --elegant-accent: #d4a574; /* Accent color */
  --elegant-text: #0f172a; /* Main text color */
  --elegant-text-light: #64748b; /* Secondary text */
  --elegant-bg: #ffffff; /* Background color */
  /* ... more variables ... */
}
```

### Navigation Items

Edit `elegant-header.html` to add, remove, or modify menu items:

```html
<!-- Add a new menu item ->
<li class="elegant-nav-item">
  <a href="/your-page/" class="elegant-nav-link">
    <svg
      class="nav-icon"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
    >
      <!-- Your icon SVG path ->
    </svg>
    <span>Your Page</span>
  </a>
</li>
```

### Dropdown Menus

Add a dropdown menu:

```html
<li class="elegant-nav-item elegant-nav-item-dropdown">
  <button class="elegant-nav-link" aria-expanded="false" aria-haspopup="true">
    <svg class="nav-icon"><!-- Icon -></svg>
    <span>Menu Name</span>
    <svg class="chevron-icon"><!-- Chevron -></svg>
  </button>
  <div class="elegant-dropdown">
    <div class="elegant-dropdown-inner">
      <a href="/link1/" class="elegant-dropdown-link">
        <span class="dropdown-icon">🎯</span>
        <div>
          <div class="dropdown-title">Title</div>
          <div class="dropdown-desc">Description</div>
        </div>
      </a>
      <!-- More links... ->
    </div>
  </div>
</li>
```

## 🔧 Technical Details

### Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- iOS Safari (latest)
- Android Chrome (latest)

### Dependencies

- **None!** Pure HTML, CSS, and vanilla JavaScript
- Uses modern CSS features (CSS Grid, Flexbox, CSS Variables)
- Uses modern JavaScript (ES6+)

### Performance

- **Optimized animations**: Uses `requestAnimationFrame` for smooth scrolling
- **GPU acceleration**: `transform` and `opacity` for animations
- **Lazy evaluation**: Event listeners only attached when needed
- **Debounced resize**: Window resize handler is debounced to 250ms

### CSS Features Used

- CSS Custom Properties (variables)
- CSS Grid and Flexbox
- Backdrop filter (glassmorphism)
- CSS Transitions and Transforms
- Media queries (responsive + preferences)
- `prefers-color-scheme` for dark mode
- `prefers-reduced-motion` for accessibility
- `prefers-contrast` for high contrast mode

### JavaScript Features Used

- Event delegation where appropriate
- Focus trap for mobile drawer
- ARIA attribute management
- Smooth scroll with `scrollTo()`
- `requestAnimationFrame` for scroll detection
- Debounced resize handler

## 🎯 Best Practices Implemented

### Design

✅ Mobile-first approach  
✅ Consistent spacing and sizing  
✅ Clear visual hierarchy  
✅ Subtle, purposeful animations  
✅ High contrast for readability  
✅ Touch-friendly tap targets (44px minimum)

### Development

✅ Semantic HTML5  
✅ BEM-inspired class naming  
✅ Modular, maintainable code  
✅ No dependencies or frameworks  
✅ Progressive enhancement  
✅ Cross-browser compatibility

### Accessibility

✅ WCAG 2.1 AA compliant  
✅ Keyboard navigable  
✅ Screen reader friendly  
✅ Focus management  
✅ Proper ARIA labels  
✅ High contrast mode support  
✅ Reduced motion support

## 📱 Responsive Breakpoints

```css
/* Mobile: < 640px */
/* Tablet: 640px - 1023px */
/* Desktop: >= 1024px */
```

The navigation automatically switches between desktop and mobile modes at
1024px.

## 🐛 Troubleshooting

### Dropdown menus not appearing

- Check that the dropdown has the class `elegant-nav-item-dropdown`
- Ensure JavaScript is loaded after the HTML

### Mobile drawer not opening

- Check that `elegant-header.js` is included
- Verify that the drawer has `id="mobile-drawer"`
- Check browser console for errors

### Glassmorphism not working

- Ensure your browser supports `backdrop-filter`
- For Safari, check that `-webkit-backdrop-filter` is included

### Styles not applying

- Verify CSS file is loaded in `<head>`
- Check for CSS conflicts with existing styles
- Use browser DevTools to inspect elements

## 📝 License

Part of Evident Legal Technologies. See main project license.

## 🎉 Demo

View the demo page: `elegant-nav-demo.html`

Try it out:

1. Hover over "Platform", "Tools", or "Resources" on desktop
2. Click the hamburger menu on mobile
3. Test keyboard navigation with Tab and Arrow keys
4. Try the shortcuts: Ctrl+K for search
5. Scroll down to see the header change

--

**Created with ❤️ for Evident Legal Technologies**
