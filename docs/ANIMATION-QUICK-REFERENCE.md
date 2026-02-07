# Animation Quick Reference Card

## 🎯 Quick Start (3 Steps)

### 1. Add CSS & JS

```html
<head>
  <link rel="stylesheet" href="/assets/css/enhanced-animations.css" />
</head>
<body>
  <script src="/assets/js/enhanced-animations.js" defer></script>
</body>
```

### 2. Add Classes

```html
<div class="slide-up">I slide from bottom!</div>
```

### 3. Done! 🎉

--

## 📋 Animation Classes Cheat Sheet

### Scroll Reveals

| Class          | Effect               |
| -------------- | -------------------- |
| `.fade-in`     | Simple fade in       |
| `.slide-up`    | Slide from bottom    |
| `.slide-down`  | Slide from top       |
| `.slide-left`  | Slide from right     |
| `.slide-right` | Slide from left      |
| `.zoom-in`     | Scale up from 80%    |
| `.zoom-out`    | Scale down from 120% |
| `.rotate-in`   | Rotate 180°          |
| `.flip-in`     | 3D flip on Y-axis    |
| `.blur-in`     | Blur to focus        |

### Hover Effects

| Class         | Effect            |
| ------------- | ----------------- |
| `.hover-lift` | Elevate on hover  |
| `.hover-grow` | Scale up on hover |
| `.hover-glow` | Add glow on hover |

### Loading States

| Class      | Effect             |
| ---------- | ------------------ |
| `.spinner` | Rotating animation |
| `.pulse`   | Pulsing opacity    |
| `.bounce`  | Bouncing motion    |
| `.float`   | Floating up/down   |

--

## 🔧 Data Attributes

### Animated Counters

```html
<h3 data-counter="5000"           <!-- Target number ->
    data-counter-start="0"        <!-- Start from (default: 0) ->
    data-counter-suffix="+"       <!-- Add after (optional) ->
    data-counter-prefix="$"       <!-- Add before (optional) ->
    data-counter-duration="2000"> <!-- Duration in ms ->
  0
</h3>
```

### Parallax

```html
<div data-parallax="0.5"              <!-- Speed (0-1) ->
     data-parallax-direction="up">    <!-- up/down/left/right ->
  Content
</div>
```

### Magnetic Hover

```html
<button data-magnetic="0.3">
  <!-- Strength (0-1) ->
  Hover me
</button>
```

### Ripple Effect

```html
<button data-ripple>Click me</button>
```

### Animation Delay

```html
<div class="slide-up" data-delay="200">
  <!-- Delay in ms ->
  Delayed reveal
</div>
```

--

## 💡 Common Patterns

### Hero Section

```html
<section class="hero">
  <h1 class="slide-down" data-delay="0">Welcome</h1>
  <p class="fade-in" data-delay="200">Subtitle here</p>
  <button class="zoom-in hover-lift" data-delay="400" data-ripple>Get Started</button>
</section>
```

### Stats Section

```html
<div class="stats">
  <div class="stat slide-up" data-delay="0">
    <h3 data-counter="5000" data-counter-suffix="+">0</h3>
    <p>Happy Clients</p>
  </div>
</div>
```

### Feature Grid

```html
<div class="stagger-container feature-grid">
  <div class="feature">Feature 1</div>
  <div class="feature">Feature 2</div>
  <div class="feature">Feature 3</div>
  <!-- Auto-staggers children ->
</div>
```

### Card with Hover

```html
<div class="card hover-lift" data-ripple>
  <h3>Card Title</h3>
  <p>Card content</p>
</div>
```

--

## 🎨 CSS Variables

```css
:root {
  /* Durations */
  --anim-duration-fast: 200ms;
  --anim-duration-normal: 400ms;
  --anim-duration-slow: 600ms;

  /* Easing */
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);

  /* Distances */
  --slide-distance: 60px;
  --float-distance: 20px;
}
```

--

## 🎭 JavaScript API

### Access Animation Engine

```javascript
// Engine is globally available
window.animationEngine;

// Stagger children manually
AnimationEngine.stagger(
  document.querySelector(".container"),
  ".item",
  100 // delay in ms
);

// Text reveal
TextReveal.reveal(document.querySelector("h1"), {
  duration: 50,
  delay: 0,
  stagger: true,
});

// Floating animation
FloatingAnimation.apply(".icon", {
  distance: 20,
  duration: 3000,
  delay: 0,
});
```

### Custom Events

```javascript
// Element revealed
document.addEventListener("element-revealed", (e) => {
  console.log(e.detail.target);
});

// Theme changed
document.addEventListener("theme:change", (e) => {
  console.log(e.detail.theme);
});

// App ready
document.addEventListener("Evident:ready", () => {
  // Your code here
});
```

### Theme Toggle

```javascript
// Toggle theme
window.themeManager.toggleTheme();

// Get current theme
const theme = window.themeManager.getCurrentTheme();

// Get theme colors
const colors = window.themeManager.getThemeColors();
```

--

## ⌨️ Keyboard Shortcuts

| Shortcut       | Action       |
| -------------- | ------------ |
| `Ctrl+Shift+D` | Toggle theme |

--

## ♿ Accessibility

### Reduced Motion

Automatically disabled for users with `prefers-reduced-motion: reduce`

### Screen Readers

- ARIA labels on interactive elements
- Live region announcements
- Semantic HTML structure

### Keyboard Navigation

- All interactive elements keyboard accessible
- Focus indicators visible
- Logical tab order

--

## 🚀 Performance Tips

### DO ✅

- Use `translate3d()` instead of `left/top`
- Add `data-delay` for stagger effects
- Use `.stagger-container` for lists
- Limit parallax to hero sections
- Use CSS animations when possible

### DON'T ❌

- Animate `width`, `height`, `left`, `top`
- Add animations to every element
- Use heavy animations on mobile
- Nest multiple parallax layers deep
- Ignore `prefers-reduced-motion`

--

## 📱 Mobile Optimization

```css
@media (max-width: 768px) {
  /* Reduce animation distances */
  :root {
    --slide-distance: 30px;
    --float-distance: 10px;
  }

  /* Disable parallax on mobile */
  [data-parallax] {
    transform: none !important;
  }
}
```

--

## 🐛 Debugging

### Check if loaded

```javascript
console.log(window.animationEngine); // Should be object
console.log(window.themeManager); // Should be object
```

### Test specific animation

```javascript
// Add class manually
document.querySelector(".my-element").classList.add("revealed");
```

### Check for conflicts

```javascript
// See all observers
console.log(window.animationEngine.observers);
```

--

## 📖 Full Documentation

- [Complete Guide](docs/JAVASCRIPT-ANIMATION-UPGRADE.md)
- [Demo Page](animation-demo.html)
- [Completion Summary](ANIMATION-UPGRADE-COMPLETE.md)

--

## 🎯 Most Common Use Cases

### 1. Page Load Animations

```html
<header class="slide-down">Header</header>
<main class="fade-in" data-delay="200">Content</main>
```

### 2. Scroll Reveals

```html
<section class="slide-up">Reveals on scroll</section>
```

### 3. Interactive Buttons

```html
<button class="hover-lift" data-ripple>Click</button>
```

### 4. Statistics

```html
<h2 data-counter="5000" data-counter-suffix="+">0</h2>
```

### 5. Hero Sections

```html
<div class="hero">
  <h1 class="slide-down">Title</h1>
  <p class="fade-in" data-delay="200">Subtitle</p>
  <button class="zoom-in hover-lift" data-delay="400">CTA</button>
</div>
```

--

**Print this card for quick reference!** 📄
