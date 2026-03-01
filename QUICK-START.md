# 🚀 Quick Start Guide - Premium Development Tools

## Instant Commands

### Development
```bash
npm run dev              # Jekyll dev server
npm run dev:vite         # Vite dev server (faster, modern)
npm run dev:webpack      # Webpack dev server
```

### Production Build
```bash
npm run build:prod       # Full production build
npm run build:vite       # Vite production build
npm run build:webpack    # Webpack production build
npm run build:tailwind   # Tailwind CSS build
```

### Testing & Quality
```bash
npm run test             # Run tests
npm run lint             # Lint all code
npm run check:a11y       # Accessibility check
npm run check:perf       # Performance check
npm run lighthouse       # Lighthouse audit
```

### Analysis
```bash
npm run analyze:bundle   # Webpack bundle analysis
npm run analyze:size     # Check bundle size limits
npm run analyze          # Full analysis suite
```

## 🎨 Animation Quick Reference

### HTML Data Attributes
```html
<!-- Fade in on load -->
<div data-animate="fade-in">Content</div>

<!-- Slide up on load -->
<div data-animate="slide-up">Content</div>

<!-- Animate on scroll -->
<div data-animate="scroll">Content</div>

<!-- Parallax effect -->
<div data-animate="parallax">Background</div>

<!-- Scale on hover -->
<button data-hover="scale">Click Me</button>

<!-- Counter animation -->
<span data-counter="1250">0</span>

<!-- AOS Animation -->
<div data-aos="fade-up" data-aos-duration="1000">Content</div>
```

### JavaScript Animation API
```javascript
import { fadeIn, slideUp, staggerIn, animateCounter } from './assets/js/animations.js';

// Basic animations
fadeIn('.element');
slideUp('.element', { duration: 1.2 });
staggerIn('.list > li', { stagger: 0.15 });

// Counters
animateCounter(element, 1250, { duration: 2 });
```

## ⚡ Performance Optimization

### Lazy Load Images
```html
<img class="lazy" data-src="path/to/image.jpg" alt="Description">
```

### Responsive Images
```html
<img 
  class="lazy"
  data-src="image-large.jpg"
  data-srcset="image-small.jpg 480w, image-medium.jpg 768w, image-large.jpg 1200w"
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="Responsive image"
>
```

### Defer Non-Critical CSS
```html
<link rel="stylesheet" href="non-critical.css" data-defer>
```

## 🎯 VS Code Extensions Quick Access

### Code Quality
- `Ctrl+Shift+P` → "SonarLint: Analyze" - Run code quality check
- `Ctrl+Shift+P` → "ESLint: Fix all auto-fixable Problems"
- `Shift+Alt+F` - Format with Prettier

### Git Operations
- `Ctrl+Shift+G` → Open Git Graph
- `Ctrl+Shift+P` → "GitLens: Show" - View GitLens features
- `Ctrl+Shift+P` → "GitHub Pull Requests" - Manage PRs

### AI Assistance
- `Ctrl+I` - Open GitHub Copilot inline chat
- `Ctrl+Shift+P` → "Sourcery: Review Code"
- `Ctrl+Space` - Trigger Copilot suggestions

## 📊 Performance Metrics

### Web Vitals Targets
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **FCP** (First Contentful Paint): < 1.8s
- **TTFB** (Time to First Byte): < 600ms

### Bundle Size Targets
- Main JS Bundle: < 50 KB (gzipped)
- CSS Bundle: < 30 KB (gzipped)
- Critical CSS: < 14 KB (gzipped)

## 🔧 Configuration Files

- `vite.config.js` - Vite configuration
- `webpack.config.js` - Webpack configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `.size-limit.js` - Bundle size limits
- `.pa11yci.json` - Accessibility testing
- `lighthouserc.js` - Lighthouse CI (already exists)

## 🚨 Common Issues & Solutions

### Dependency Conflicts
```bash
npm install --legacy-peer-deps [package-name]
```

### Clear Cache
```bash
npm run clean
npm cache clean --force
```

### Rebuild Node Modules
```bash
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Fix Vulnerabilities
```bash
npm audit fix
npm audit fix --force  # For major updates
```

## 📚 Key Documentation

- **GSAP**: https://greensock.com/docs/
- **Vite**: https://vitejs.dev/
- **Webpack**: https://webpack.js.org/
- **Tailwind**: https://tailwindcss.com/
- **Web Vitals**: https://web.dev/vitals/
- **Lottie**: https://airbnb.io/lottie/

## 🎉 What's New

### Animation Tools
✅ GSAP - Professional animation library
✅ Lottie - Vector animations
✅ AOS - Scroll animations
✅ Custom animation utilities

### Performance Tools
✅ Web Vitals tracking
✅ Lazy loading system
✅ Prefetching/preloading
✅ Image optimization pipeline

### Build Tools
✅ Vite - Lightning-fast builds
✅ Webpack - Advanced bundling
✅ Tailwind CSS - Utility framework
✅ PostCSS - Modern CSS processing

### Quality Tools
✅ Bundle analysis
✅ Size limits enforcement
✅ Accessibility testing
✅ Performance monitoring

### AI & Productivity
✅ GitHub Copilot integration
✅ Sourcery code reviews
✅ Cody AI assistant
✅ SonarLint analysis

---

**Need Help?** Check `PREMIUM-TOOLS-INSTALLED.md` for full documentation.
