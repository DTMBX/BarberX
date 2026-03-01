# 🚀 Performance Optimization Tools

## Overview
This directory contains comprehensive performance optimization tools for the Tillerstead website. These tools help achieve **sub-2-second load times** and perfect **Core Web Vitals scores**.

---

## 🎯 Quick Start

### Production Build (Fully Optimized)
```bash
npm run build:prod
```
This runs:
1. Minifies CSS & JavaScript
2. Extracts critical CSS
3. Minifies HTML (removes comments, whitespace)
4. Generates Service Worker for offline support
5. Builds Jekyll site

### Individual Commands

#### Asset Optimization
```bash
npm run minify:all      # Minify CSS + JS
npm run minify:css      # Minify CSS only
npm run minify:js       # Minify JavaScript only
npm run minify:html     # Minify HTML in _site/
```

#### Critical CSS
```bash
npm run critical:css    # Extract above-the-fold CSS
npm run critical:inline # Inline critical CSS (requires server)
```

#### Service Worker
```bash
npm run sw:generate     # Generate SW from workbox-config.js
npm run sw:inject       # Inject manifest into custom SW
```

#### Image Optimization
```bash
npm run images:optimize # Convert to WebP + AVIF + optimize
npm run images:webp     # Convert to WebP only
npm run images:avif     # Convert to AVIF only
```

#### Performance Analysis
```bash
npm run perf:vitals     # Generate Web Vitals monitoring code
npm run perf:report     # Analyze bundle sizes
npm run analyze:css     # Find unused CSS
npm run analyze:size    # Size limit checks
```

---

## 📦 Installed Tools

### Minification & Compression
- **clean-css-cli** - CSS minification
- **terser** - JavaScript minification  
- **html-minifier-terser** - HTML minification
- **brotli-webpack-plugin** - Brotli compression (20-30% better than gzip)
- **compression-webpack-plugin** - Gzip compression fallback

### Critical CSS
- **critical** - Extract above-the-fold CSS
- **penthouse** - High-accuracy critical CSS extraction

### Service Workers & PWA
- **workbox-cli** - Service Worker generation
- **workbox-webpack-plugin** - Webpack integration
- Configuration: `workbox-config.js`

### Performance Monitoring
- **web-vitals** - Core Web Vitals tracking (LCP, FID, CLS)
- **perfume.js** - Advanced performance monitoring
- **size-limit** - Bundle size enforcement

### Image Optimization
- **sharp** - Image processing (resize, format conversion)
- **imagemin** - Image compression
- **imagemin-webp** - WebP conversion
- **svgo** - SVG optimization

### Webpack Optimization
- **preload-webpack-plugin** - Auto-generate preload tags
- **webpack-bundle-analyzer** - Bundle size visualization
- **speed-measure-webpack-plugin** - Build performance profiling

---

## 📊 Configuration Files

### `workbox-config.js`
Service Worker configuration:
- **Cache strategies**: CacheFirst, StaleWhileRevalidate, NetworkFirst
- **Runtime caching**: Images (30 days), CSS/JS (7 days), HTML (1 day), Fonts (1 year)
- **Offline fallback**: `/offline.html`
- **Ignore patterns**: UTM params, admin pages

### `webpack.config.js`
Already configured with:
- Terser for JS minification
- CSS Minimizer
- Brotli + Gzip compression
- Code splitting
- Bundle analyzer

---

## 🎨 Critical CSS Extraction

### How It Works
1. Puppeteer renders pages at multiple viewport sizes:
   - Mobile: 375x667
   - Tablet: 768x1024
   - Desktop: 1920x1080
2. Extracts CSS needed for above-the-fold content
3. Inlines critical CSS in `<head>`
4. Defers non-critical CSS

### Pages Optimized
- `index.html` (homepage)
- `services.html`
- `portfolio.html`
- `contact.html`
- `about.html`

### Add More Pages
Edit `scripts/extract-critical-css.js`:
```javascript
const criticalPages = [
  { src: 'your-page.html', dest: 'your-page.html' },
];
```

---

## 🔄 Service Worker Caching

### Cache Strategies

#### CacheFirst (Images, Fonts)
- Checks cache first, network as fallback
- Best for immutable assets
- Expiration: 30 days (images), 1 year (fonts)

#### StaleWhileRevalidate (CSS, JS)
- Serves cached version immediately
- Updates in background
- Expiration: 7 days

#### NetworkFirst (HTML)
- Tries network first
- Falls back to cache if offline
- Expiration: 1 day

### Offline Support
- Cached assets work offline
- Fallback page: `/offline.html`
- Automatic cache cleanup

---

## 📈 Performance Monitoring

### Web Vitals Tracking

The `web-vitals-tracker.js` monitors:
- **LCP** (Largest Contentful Paint) - Target: <2.5s
- **FID** (First Input Delay) - Target: <100ms
- **CLS** (Cumulative Layout Shift) - Target: <0.1
- **FCP** (First Contentful Paint) - Target: <1.8s
- **TTFB** (Time to First Byte) - Target: <600ms

### Usage
Add to your layout:
```html
<script type="module" src="/assets/js/web-vitals-tracker.js"></script>
```

Metrics are sent to:
- Google Analytics (if configured)
- Console (in development)
- Custom analytics endpoint (optional)

### Performance Report
```bash
npm run perf:report
```

Generates `performance-report.json` with:
- Bundle sizes by file type
- Files exceeding size limits
- Optimization recommendations

---

## 🎯 Expected Performance Gains

### Before → After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **FCP** | 2.1s | 1.2s | -900ms (43%) |
| **LCP** | 3.5s | 2.0s | -1.5s (43%) |
| **TBT** | 450ms | 180ms | -270ms (60%) |
| **CLS** | 0.15 | 0.05 | -0.10 (67%) |
| **JS Size** | 500 KB | 300 KB | -200 KB (40%) |
| **CSS Size** | 200 KB | 100 KB | -100 KB (50%) |
| **HTML Size** | 50 KB | 35 KB | -15 KB (30%) |
| **Repeat Visit** | 1.2s | <100ms | Instant (92%) |

---

## 🚀 Resource Hints Added

### Preconnect
```html
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
```
Establishes early connection to third-party origins.

### DNS Prefetch
```html
<link rel="dns-prefetch" href="//www.google-analytics.com" />
```
Resolves DNS before resource needed.

### Preload Critical Assets
```html
<link rel="preload" as="style" href="/assets/css/critical.css" />
<link rel="preload" as="script" href="/assets/js/main.js" />
<link rel="preload" as="font" href="/assets/fonts/inter-var.woff2" crossorigin />
```
Loads critical resources immediately.

### Prefetch Next Pages
```html
<link rel="prefetch" href="/services/" />
<link rel="prefetch" href="/contact/" />
```
Speculatively loads likely next pages.

---

## 🔧 Build Pipeline

### Development
```bash
npm run dev
```
- No minification
- Source maps enabled
- Live reload

### Production
```bash
npm run build:prod
```
1. **Minify CSS** - CleanCSS removes whitespace, comments
2. **Minify JS** - Terser removes console.logs, dead code
3. **Extract Critical CSS** - Inline above-the-fold styles
4. **Minify HTML** - 30%+ size reduction
5. **Generate SW** - Offline support + caching
6. **Build Jekyll** - Final site generation

### Deploy
```bash
npm run deploy
```
Runs `build:prod` + commits + pushes to origin.

---

## 📊 Monitoring & Debugging

### Check Web Vitals (Local)
Open DevTools Console after page load:
```
📊 LCP: { value: 1890ms, rating: good }
📊 FID: { value: 12ms, rating: good }
📊 CLS: { value: 0.03, rating: good }
```

### Lighthouse Audits
```bash
npm run lighthouse           # Production site
npm run lighthouse:local     # Local server (port 4000)
```

### Bundle Analysis
```bash
npm run analyze:bundle
```
Opens interactive bundle visualization.

### Size Limits
```bash
npm run analyze:size
```
Checks if bundles exceed thresholds.

---

## ⚠️ Important Notes

### Service Worker Updates
- SW caches aggressively for performance
- Users may see stale content briefly
- Force update: Clear site data or hard refresh (Ctrl+Shift+R)
- Production: SW updates on navigation after 24 hours

### Critical CSS
- Run after major CSS changes
- Requires built site (_site/ directory)
- Best run on production server for accuracy
- May need manual tweaking for edge cases

### Brotli Compression
- Requires server support (GitHub Pages ✓, Netlify ✓)
- Falls back to Gzip if unsupported
- Pre-compressed files: `bundle.min.css.br`

### Image Optimization
- Run manually, not in build pipeline (slow)
- Original images preserved in `assets/images/originals/`
- AVIF for Chrome/Edge, WebP for Safari, JPEG fallback

---

## 🎓 Best Practices

### 1. Critical CSS First
Extract critical CSS before HTML minification.

### 2. Service Worker Last
Generate SW after all other optimizations.

### 3. Test Locally
```bash
npm run serve:test  # Port 4173, no live reload
npm run lighthouse:local
```

### 4. Monitor Production
```bash
npm run lighthouse
npm run perf:report
```

### 5. Incremental Improvements
Don't optimize prematurely. Profile first:
```bash
npm run analyze:bundle
npm run perf:report
```

---

## 📚 Resources

- [Web Vitals](https://web.dev/vitals/)
- [Workbox Documentation](https://developers.google.com/web/tools/workbox)
- [Critical CSS Guide](https://web.dev/extract-critical-css/)
- [Image Optimization](https://web.dev/fast/#optimize-your-images)
- [Resource Hints](https://www.w3.org/TR/resource-hints/)

---

## 🆘 Troubleshooting

### Critical CSS extraction fails
- Ensure Jekyll site is built first: `bundle exec jekyll build`
- Check that pages exist in `_site/`
- Increase timeout in `extract-critical-css.js`

### Service Worker not updating
- Clear cache in DevTools → Application → Clear Storage
- Unregister SW: DevTools → Application → Service Workers → Unregister
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### HTML minification breaks site
- Check for inline scripts that need whitespace
- Adjust `minifyOptions` in `scripts/minify-html.js`
- Exclude specific files if needed

### Bundle too large
```bash
npm run analyze:bundle      # Visualize what's large
npm run analyze:css         # Find unused CSS
npm run perf:report         # Get recommendations
```

---

**Last Updated**: February 1, 2026  
**Maintained by**: Tillerstead Dev Team
