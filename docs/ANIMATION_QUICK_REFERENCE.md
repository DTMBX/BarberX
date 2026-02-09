# Animation Quick Reference — Copy & Paste Examples

## 🎯 Basic Scroll Reveals

```html
<!-- Fade in -->
<div class="will-animate fade-in">Content fades in</div>

<!-- Slide up (most common) -->
<div class="will-animate slide-up">Content slides up</div>

<!-- Slide from sides -->
<div class="will-animate slide-left">From left</div>
<div class="will-animate slide-right">From right</div>

<!-- Zoom effects -->
<div class="will-animate zoom-in">Zooms in</div>
<div class="will-animate blur-in">Blurs into focus</div>
```

## ⏱️ Delays & Stagger

```html
<!-- Single element with delay -->
<div class="will-animate fade-in" data-animation-delay="200">
  Waits 200ms before revealing
</div>

<!-- Stagger children automatically -->
<div class="will-animate stagger-container">
  <div>Reveals first</div>
  <div>Then this (100ms later)</div>
  <div>Then this (200ms later)</div>
  <div>And this (300ms later)</div>
</div>
```

## 📊 Animated Counters

```html
<!-- Basic counter -->
<span data-counter="87">0</span>

<!-- With percentage -->
<span data-counter="92.5" data-suffix="%">0</span>

<!-- With prefix (currency) -->
<span data-counter="15000" data-prefix="$">0</span>

<!-- Custom duration (3 seconds) -->
<span data-counter="1000" data-duration="3000">0</span>

<!-- Complete example -->
<div class="stat-box">
  <span class="stat-number" data-counter="10000" data-suffix="+" data-duration="2500">0</span>
  <p class="stat-label">Cases Processed</p>
</div>
```

## 🎴 Interactive Cards

```html
<!-- Auto-hover card (3D tilt) -->
<div class="card">
  <h3>Title</h3>
  <p>Content automatically gets hover effects</p>
</div>

<!-- Card with lift -->
<a href="#" class="card hover-lift">
  Lifts 12px on hover with shadow
</a>

<!-- Card with glow -->
<div class="card hover-glow">
  Gets blue glow on hover
</div>

<!-- Card with grow -->
<div class="card hover-grow">
  Scales to 1.05x on hover
</div>
```

## 🌊 Parallax Backgrounds

```html
<!-- Slow parallax (0.3 = 30% of scroll speed) -->
<div class="hero" data-parallax="0.3">
  <img src="bg.jpg" alt="">
</div>

<!-- Medium parallax -->
<div class="section-bg" data-parallax="0.5">
  Moves at half scroll speed
</div>

<!-- Fast parallax -->
<div class="accent-layer" data-parallax="0.8">
  Moves almost with scroll
</div>
```

## 🔘 Enhanced Buttons

```html
<!-- Button with lift effect -->
<a href="#" class="btn btn-primary hover-lift">Click Me</a>

<!-- Button with glow -->
<button class="btn btn-secondary hover-glow">Learn More</button>

<!-- Button with all effects -->
<a href="/register" class="btn btn-primary hover-lift hover-glow">
  Get Started
</a>
```

## 📄 Full Section Example

```html
<section class="py-16 bg-gray-50">
  <div class="container">
    <!-- Header fades in first -->
    <div class="text-center mb-12 will-animate fade-in">
      <h2>Our Features</h2>
      <p>Everything you need to succeed</p>
    </div>

    <!-- Cards stagger in -->
    <div class="grid grid-cols-3 gap-8 will-animate stagger-container" data-animation-delay="100">
      <div class="card">
        <h3>Feature 1</h3>
        <p>Description</p>
      </div>
      <div class="card">
        <h3>Feature 2</h3>
        <p>Description</p>
      </div>
      <div class="card">
        <h3>Feature 3</h3>
        <p>Description</p>
      </div>
    </div>

    <!-- CTA zooms in last -->
    <div class="text-center mt-12 will-animate zoom-in" data-animation-delay="300">
      <a href="#" class="btn btn-primary hover-lift">Get Started</a>
    </div>
  </div>
</section>
```

## 📈 Statistics Row

```html
<div class="stats-row">
  <div class="stat will-animate slide-up" data-animation-delay="0">
    <span data-counter="10000" data-suffix="+">0</span>
    <p>Happy Clients</p>
  </div>
  <div class="stat will-animate slide-up" data-animation-delay="100">
    <span data-counter="99.9" data-suffix="%">0</span>
    <p>Uptime</p>
  </div>
  <div class="stat will-animate slide-up" data-animation-delay="200">
    <span data-counter="24" data-suffix="/7">0</span>
    <p>Support</p>
  </div>
</div>
```

## 🎨 Color Classes (Use with animations)

```css
/* Apply wholesome colors */
.bg-earth { background: var(--color-earth-brown); }
.bg-fresh { background: var(--color-fresh-green); }
.bg-sky { background: var(--color-sky-blue); }
.bg-warm { background: var(--color-warm-beige); }
.bg-gold { background: var(--color-soft-gold); }
```

## 🔍 Logo Animation (Automatic)

```html
<!-- Logo automatically pulses when scrolling to top -->
<a href="/" class="site-logo">
  <img src="logo.svg" alt="Evident">
</a>
<!-- Or use class="logo" or any element with "logo" in className -->
```

## ⚡ Performance Tips

1. **Don't overuse**: 3-5 animated elements per viewport is ideal
2. **Stagger wisely**: Keep delays under 500ms total
3. **Test on mobile**: Reduce animations if laggy
4. **Use will-animate**: Only on elements you want to reveal
5. **Avoid nesting**: Don't put `will-animate` inside another `will-animate`

## 🚫 What NOT to Do

```html
<!-- ❌ Don't nest will-animates -->
<div class="will-animate">
  <div class="will-animate">Nested - will break</div>
</div>

<!-- ❌ Don't animate everything -->
<p class="will-animate">Every</p>
<p class="will-animate">single</p>
<p class="will-animate">paragraph</p>
<!-- This is overkill -->

<!-- ✅ Do animate containers -->
<div class="will-animate stagger-container">
  <p>Every</p>
  <p>single</p>
  <p>paragraph</p>
</div>
```

## 🎯 Recommended Patterns

### Hero Section
```html
<section class="hero will-animate fade-in">
  <h1 class="will-animate slide-up" data-animation-delay="100">Title</h1>
  <p class="will-animate slide-up" data-animation-delay="200">Subtitle</p>
  <div class="will-animate fade-in" data-animation-delay="300">
    <a href="#" class="btn hover-lift">CTA</a>
  </div>
</section>
```

### Feature Grid
```html
<div class="grid will-animate stagger-container">
  <div class="card">Feature 1</div>
  <div class="card">Feature 2</div>
  <div class="card">Feature 3</div>
  <div class="card">Feature 4</div>
</div>
```

### Testimonial
```html
<div class="testimonial will-animate zoom-in">
  <blockquote>"Amazing product!"</blockquote>
  <cite>— Happy Customer</cite>
</div>
```

---

**Pro Tip**: Open DevTools, throttle CPU to "4x slowdown", and scroll to see animations in slow motion. Adjust delays until it feels perfect.
