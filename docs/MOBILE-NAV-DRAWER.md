# Mobile Navigation Drawer

Modern, accessible slide-out navigation menu with animated hamburger icon.

## ✨ Features

- **Animated Hamburger Icon** - Smooth 3-line → X transformation
- **Slide-in Drawer** - Smooth slide from right side
- **Backdrop Blur** - Modern frosted glass overlay effect
- **Touch Gestures** - Swipe right to close on mobile
- **Keyboard Navigation** - ESC key, focus management, screen reader support
- **Submenu Support** - Collapsible nested navigation
- **Body Scroll Lock** - Prevents background scrolling when open
- **Responsive** - Auto-hides on desktop (>1024px)
- **Dark Mode** - Automatic dark theme support
- **Accessibility** - ARIA labels, keyboard navigation, screen reader
  announcements

## 📁 Files Created

```
/assets/css/components/mobile-nav-drawer.css  - Styles
/assets/js/mobile-nav-drawer.js               - Functionality
/_includes/mobile-nav-drawer.html             - HTML template
```

## 🚀 Quick Start

### Step 1: Add CSS to your layout

In `_layouts/default.html`, add to `<head>`:

```html
<link rel="stylesheet" href="{{ '/assets/css/components/mobile-nav-drawer.css' | relative_url }}" />
```

### Step 2: Add JavaScript before `</body>`

```html
<script src="{{ '/assets/js/mobile-nav-drawer.js' | relative_url }}" defer></script>
```

### Step 3: Include HTML component

In your header (e.g., `_includes/header.html` or directly in
`_layouts/default.html`):

```liquid
{% include mobile-nav-drawer.html %}
```

Or copy the HTML from `_includes/mobile-nav-drawer.html` directly into your
layout.

## 🎨 Customization

### Colors

Edit these CSS custom properties in `mobile-nav-drawer.css`:

```css
--Evident-red-primary: #c41e3a; /* Brand red */
--color-background: #ffffff; /* Drawer background */
--color-text: #1f2937; /* Text color */
--color-border: #e5e7eb; /* Border color */
```

### Width

Change drawer width in `mobile-nav-drawer.js`:

```javascript
const CONFIG = {
  drawerWidth: "85%", // Mobile width
  maxDrawerWidth: "400px", // Desktop max width
  // ...
};
```

### Animation Speed

```javascript
const CONFIG = {
  animationDuration: 300, // Milliseconds
  // ...
};
```

## 📝 HTML Structure

### Basic Link

```html
<li class="mobile-nav-item">
  <a href="/page" class="mobile-nav-link">
    <span>
      <svg class="mobile-nav-link-icon"><!-- icon -></svg>
      Page Name
    </span>
  </a>
</li>
```

### Link with Submenu

```html
<li class="mobile-nav-item">
  <a
    href="/features"
    class="mobile-nav-link"
    data-submenu-toggle
    aria-expanded="false"
  >
    <span>
      <svg class="mobile-nav-link-icon"><!-- icon -></svg>
      Features
    </span>
    <span class="mobile-nav-submenu-toggle">
      <svg class="mobile-nav-submenu-toggle-icon"><!-- arrow -></svg>
    </span>
  </a>

  <div class="mobile-nav-submenu">
    <ul class="mobile-nav-submenu-list">
      <li>
        <a href="/features/item1" class="mobile-nav-submenu-link">Item 1</a>
      </li>
      <li>
        <a href="/features/item2" class="mobile-nav-submenu-link">Item 2</a>
      </li>
    </ul>
  </div>
</li>
```

### Active State

Add `.is-active` class to highlight current page:

```html
<a href="/current-page" class="mobile-nav-link is-active"> Current Page </a>
```

## 🔧 JavaScript API

Control the drawer programmatically:

```javascript
// Open drawer
MobileNav.open();

// Close drawer
MobileNav.close();

// Toggle drawer
MobileNav.toggle();

// Check if open
if (MobileNav.isOpen()) {
  console.log("Drawer is open");
}
```

## 🎯 Events

The drawer automatically:

- Closes when window resized above 1024px
- Closes when ESC key pressed
- Closes when backdrop clicked
- Closes when nav link clicked
- Closes when swiped right >50px

## ♿ Accessibility Features

- **ARIA Labels**: Proper `aria-expanded`, `aria-hidden`, `aria-label`
- **Focus Management**: Auto-focuses first link when opened
- **Keyboard Navigation**: ESC to close, Tab to navigate
- **Screen Reader**: Status announcements on open/close
- **High Contrast**: Enhanced borders in high-contrast mode
- **Reduced Motion**: Removes animations when preferred

## 🎨 Icons

The template uses inline SVG icons. Replace with your preferred icon system:

### Using Font Awesome

```html
<i class="fas fa-home mobile-nav-link-icon"></i>
```

### Using Heroicons

Already implemented in the template! Just swap the SVG paths.

### Using Image Icons

```html
<img src="/assets/images/icon-home.svg" class="mobile-nav-link-icon" alt="" />
```

## 🌙 Dark Mode

Dark mode works automatically with `prefers-color-scheme: dark`.

### Custom Dark Mode Class

If using a toggle, add to CSS:

```css
.dark-mode .mobile-nav-drawer {
  background: var(--color-gray-900, #111827);
}

.dark-mode .mobile-nav-link {
  color: var(--color-gray-100, #f3f4f6);
}
```

## 📱 Touch Gestures

- **Swipe Right**: Close drawer (threshold: 50px)
- **Tap Backdrop**: Close drawer
- **Smooth Dragging**: Drawer follows finger while swiping

## 🔍 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ iOS Safari 14+
- ✅ Chrome Android

## 🐛 Troubleshooting

### Drawer doesn't open

1. Check console for JavaScript errors
2. Verify elements exist: `.mobile-nav-hamburger`, `.mobile-nav-drawer`,
   `.mobile-nav-backdrop`
3. Ensure JS file is loaded (check Network tab)

### Hamburger icon not visible

1. Check you're on mobile (<1024px) or resize window
2. Verify CSS file is loaded
3. Check for conflicting CSS

### Body still scrolls when drawer open

1. Make sure JS is running (no console errors)
2. Check `body` element doesn't have `overflow: auto !important`

### Icons not showing

1. Icons are inline SVG - check if paths are correct
2. Replace with your icon system (Font Awesome, etc.)
3. Check SVG `viewBox` attribute

## 🎬 Demo Usage

```html
<!DOCTYPE html>
<html>
  <head>
    <link
      rel="stylesheet"
      href="/assets/css/components/mobile-nav-drawer.css"
    />
  </head>
  <body>
    <!-- Header ->
    <header>
      <div class="logo">Evident</div>

      <!-- Hamburger Button ->
      <button class="mobile-nav-hamburger" aria-label="Open menu">
        <span class="mobile-nav-hamburger-line"></span>
        <span class="mobile-nav-hamburger-line"></span>
        <span class="mobile-nav-hamburger-line"></span>
      </button>
    </header>

    <!-- Backdrop ->
    <div class="mobile-nav-backdrop"></div>

    <!-- Drawer ->
    <nav class="mobile-nav-drawer">
      <!-- Content from _includes/mobile-nav-drawer.html ->
    </nav>

    <script src="/assets/js/mobile-nav-drawer.js"></script>
  </body>
</html>
```

## 📄 License

Part of Evident.info project - use freely within this project.

## 🙏 Credits

Built for Evident Legal Technologies Modern design with accessibility and UX
best practices
