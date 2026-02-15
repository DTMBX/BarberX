# Lighthouse CI Quick Reference

## 🚀 Quick Start

### Run Locally

```bash
# 1. Build the app
npm run build

# 2. Install Lighthouse CI (if not already installed)
npm install -g @lhci/cli

# 3. Run desktop audit
lhci autorun --config=lighthouserc.json

# 4. Run mobile audit
lhci autorun --config=lighthouserc.mobile.json
```

### View Results

Results are saved in `.lighthouseci/` directory:
- HTML reports: `.lighthouseci/*.report.html`
- JSON data: `.lighthouseci/*.report.json`
- Manifest: `.lighthouseci/manifest.json`

Open HTML reports in your browser for interactive exploration.

---

## 📊 CI/CD Workflows

### 1. Lighthouse CI (Pull Requests)
- **Trigger:** Every PR and push to main
- **Configuration:** Desktop only
- **File:** `.github/workflows/lighthouse-ci.yml`
- **Features:**
  - Automatic PR comments with scores
  - Performance threshold enforcement (70+)
  - Artifact uploads (30 days retention)
  - Fails build if performance < 70

### 2. Full Audit (Weekly)
- **Trigger:** Every Sunday at midnight (UTC) + manual
- **Configuration:** Desktop AND mobile
- **File:** `.github/workflows/lighthouse-full.yml`
- **Features:**
  - Comprehensive desktop + mobile testing
  - Automatic GitHub issue with report
  - Side-by-side comparison
  - Detailed recommendations

---

## 🎯 Score Thresholds

| Category | Desktop | Mobile | Level |
|----------|---------|--------|-------|
| Performance | 70+ | 60+ | Error |
| Accessibility | 90+ | 90+ | Warning |
| Best Practices | 80+ | 80+ | Warning |
| SEO | 80+ | 80+ | Warning |
| PWA | - | 50+ | Warning |

**Legend:**
- ❌ **Error**: Fails CI build
- ⚠️ **Warning**: Shows warning but doesn't fail build
- ℹ️ **Informational**: Tracked but not enforced

---

## 📈 Key Metrics Budget

### Desktop
- First Contentful Paint: **< 2.0s**
- Largest Contentful Paint: **< 3.0s**
- Total Blocking Time: **< 300ms**
- Cumulative Layout Shift: **< 0.1**
- Speed Index: **< 3.5s**
- Time to Interactive: **< 5.0s**

### Mobile  
- First Contentful Paint: **< 3.0s**
- Largest Contentful Paint: **< 4.0s**
- Total Blocking Time: **< 400ms**
- Cumulative Layout Shift: **< 0.1**
- Speed Index: **< 5.0s**
- Time to Interactive: **< 6.0s**

---

## 🔧 Configuration Files

### `lighthouserc.json`
Desktop configuration with:
- 3 runs for averaging
- Desktop preset
- Fast network simulation
- Performance threshold: 70+

### `lighthouserc.mobile.json`
Mobile configuration with:
- 3 runs for averaging
- Mobile preset
- 4G network simulation
- Performance threshold: 60+
- Additional PWA checks

### `performance-budget.json`
Resource budgets:
- Script: 500KB
- Stylesheet: 100KB
- Images: 300KB
- Fonts: 150KB
- Total: 1000KB

---

## 💡 Common Commands

```bash
# Run standard desktop audit
lhci autorun

# Run mobile audit
lhci autorun --config=lighthouserc.mobile.json

# Run with specific URL
lhci autorun --url=http://localhost:4173

# Collect only (no assertions)
lhci collect

# Assert only (after collect)
lhci assert

# Upload results to temporary storage
lhci upload --target=temporary-public-storage
```

---

## 🐛 Troubleshooting

### Build Fails
```bash
# Check if dist exists
ls -la dist/

# Manually build
npm run build

# Check preview server
npm run preview
```

### No Reports Generated
```bash
# Check Lighthouse CI directory
ls -la .lighthouseci/

# Run with verbose logging
lhci autorun --verbose

# Check server started correctly
npm run preview
# Wait for "Local: http://localhost:4173"
```

### Low Performance Scores
```bash
# Analyze bundle size
npm run build
ls -lh dist/assets/

# Check for large dependencies
npm list --depth=0

# Run lighthouse manually for debugging
npx lighthouse http://localhost:4173 --view
```

### Accessibility Issues
```bash
# Run specific category
lhci autorun --only-categories=accessibility

# Generate detailed report
npx lighthouse http://localhost:4173 --only-categories=accessibility --view
```

---

## 📖 Understanding Scores

### 🟢 Green (90-100): Good
- Keep maintaining this level
- Make incremental improvements
- Use as baseline for future work

### 🟡 Orange (50-89): Needs Improvement
- Review specific audits that failed
- Prioritize fixes based on impact
- Set goals to reach green

### 🔴 Red (0-49): Poor
- **Critical**: Address immediately
- Usually indicates major issues
- May affect user experience significantly

---

## 🎓 Key Audit Categories

### Performance
- **FCP**: Time until first content appears
- **LCP**: Time until largest content appears
- **TBT**: Total time main thread blocked
- **CLS**: Visual stability score
- **SI**: How quickly content is visually displayed

### Accessibility
- **ARIA**: Proper use of ARIA attributes
- **Contrast**: Text readable against background
- **Navigation**: Keyboard and screen reader support
- **Labels**: Forms properly labeled

### Best Practices
- **HTTPS**: Secure connection
- **Console**: No errors in console
- **Libraries**: No known vulnerabilities
- **Images**: Proper aspect ratios

### SEO
- **Meta tags**: Title and description present
- **Mobile**: Mobile-friendly viewport
- **Crawlable**: No blocked resources
- **Status codes**: Valid HTTP responses

---

## 🔗 Useful Resources

- [Lighthouse Docs](https://developer.chrome.com/docs/lighthouse/)
- [Lighthouse CI Docs](https://github.com/GoogleChrome/lighthouse-ci)
- [Web Vitals](https://web.dev/vitals/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Performance Best Practices](https://web.dev/performance/)

---

## ⚡ Quick Wins

### Improve Performance
1. ✅ Enable compression (gzip/brotli)
2. ✅ Optimize images (WebP, lazy loading)
3. ✅ Code splitting (dynamic imports)
4. ✅ Remove unused CSS/JS
5. ✅ Use CDN for static assets

### Improve Accessibility
1. ✅ Add alt text to all images
2. ✅ Ensure color contrast ratios (4.5:1)
3. ✅ Label all form inputs
4. ✅ Test keyboard navigation
5. ✅ Use semantic HTML

### Improve SEO
1. ✅ Add meta description
2. ✅ Set viewport meta tag
3. ✅ Use heading hierarchy (h1→h6)
4. ✅ Add structured data
5. ✅ Create sitemap.xml

---

**Last Updated:** 2024  
**For Detailed Guide:** See [LIGHTHOUSE_CI.md](./LIGHTHOUSE_CI.md)
