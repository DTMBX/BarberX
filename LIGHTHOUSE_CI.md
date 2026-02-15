# Lighthouse CI Performance Testing

## Overview

This project uses **Lighthouse CI** to automatically audit web performance, accessibility, best practices, SEO, and PWA capabilities on every pull request and deployment. This ensures the Geneva Bible Study app maintains high quality standards and optimal user experience.

## 🔍 What is Lighthouse CI?

Lighthouse CI is an automated performance monitoring tool that:
- Runs Google Lighthouse audits in CI/CD pipelines
- Tracks performance metrics over time
- Provides detailed reports on performance bottlenecks
- Ensures accessibility standards compliance
- Validates SEO best practices

## 🚀 Features

### Automated Testing
- ✅ Runs on every pull request
- ✅ Runs on every push to main branch
- ✅ Manual trigger via GitHub Actions UI
- ✅ Tests desktop configuration (optimized for Bible study)
- ✅ Multiple runs (3x) for accurate averages

### Performance Metrics Tracked
1. **Performance Score** (threshold: 70+)
   - First Contentful Paint (FCP)
   - Largest Contentful Paint (LCP)
   - Total Blocking Time (TBT)
   - Cumulative Layout Shift (CLS)
   - Speed Index

2. **Accessibility Score** (threshold: 90+)
   - ARIA attributes
   - Color contrast
   - Form labels
   - Image alt text
   - Keyboard navigation

3. **Best Practices Score** (threshold: 80+)
   - HTTPS usage
   - Console errors
   - Image aspects
   - JavaScript libraries

4. **SEO Score** (threshold: 80+)
   - Meta tags
   - Crawlability
   - Mobile-friendliness
   - Structured data

5. **PWA Score** (informational)
   - Service worker
   - Offline capability
   - Installability

### PR Comments
Lighthouse CI automatically posts detailed performance reports as PR comments, including:
- 📊 Score breakdown with visual indicators
- 📈 Key web vitals metrics
- 📦 Bundle size information
- 💡 Actionable recommendations

### Artifacts
All Lighthouse reports are stored as GitHub Actions artifacts for 30 days, allowing detailed analysis of:
- HTML reports with full audit details
- JSON data for programmatic analysis
- Historical trend tracking

## 📋 Configuration

### Lighthouse RC Configuration (`lighthouserc.json`)

```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop",
        "formFactor": "desktop",
        "screenEmulation": {
          "width": 1350,
          "height": 940
        }
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.7 }],
        "categories:accessibility": ["warn", { "minScore": 0.9 }],
        "categories:best-practices": ["warn", { "minScore": 0.8 }],
        "categories:seo": ["warn", { "minScore": 0.8 }]
      }
    }
  }
}
```

### Performance Thresholds

| Category | Threshold | Level |
|----------|-----------|-------|
| Performance | 70 | ❌ Error (blocks PR) |
| Accessibility | 90 | ⚠️ Warning |
| Best Practices | 80 | ⚠️ Warning |
| SEO | 80 | ⚠️ Warning |
| PWA | N/A | ℹ️ Informational |

### Key Metrics Budgets

| Metric | Budget | Level |
|--------|--------|-------|
| First Contentful Paint | 2.0s | ⚠️ Warning |
| Largest Contentful Paint | 3.0s | ⚠️ Warning |
| Total Blocking Time | 300ms | ⚠️ Warning |
| Cumulative Layout Shift | 0.1 | ⚠️ Warning |
| Speed Index | 3.5s | ⚠️ Warning |
| Time to Interactive | 5.0s | ⚠️ Warning |
| Max Potential FID | 200ms | ⚠️ Warning |

## 🔧 Usage

### Running Lighthouse CI Locally

1. **Install dependencies:**
```bash
npm install
```

2. **Build the application:**
```bash
npm run build
```

3. **Install Lighthouse CI:**
```bash
npm install -g @lhci/cli
```

4. **Run Lighthouse CI:**
```bash
lhci autorun
```

5. **View results:**
Results will be saved in `.lighthouseci/` directory and also uploaded to temporary public storage with a shareable link.

### Viewing Results in CI

#### Pull Request Comments
When you create or update a PR, Lighthouse CI will automatically:
1. Build your application
2. Run performance audits
3. Post detailed results as a PR comment
4. Update the comment on subsequent runs

#### GitHub Actions Artifacts
1. Go to the Actions tab in GitHub
2. Click on the Lighthouse CI workflow run
3. Download the `lighthouse-results` artifact
4. Open the HTML reports for detailed analysis

#### Example PR Comment
```markdown
## 🔦 Lighthouse Performance Report

| Category | Score | Status |
|----------|-------|--------|
| 🟢 Performance | **85** | ✅ |
| 🟢 Accessibility | **95** | ✅ |
| 🟢 Best Practices | **92** | ✅ |
| 🟢 SEO | **100** | ✅ |
| 🟡 PWA | **67** | ⚠️ |

### 📈 Key Metrics

| Metric | Value |
|--------|-------|
| First Contentful Paint | 1.2s |
| Largest Contentful Paint | 2.1s |
| Total Blocking Time | 180ms |
| Cumulative Layout Shift | 0.05 |
| Speed Index | 2.8s |
```

### Manual Trigger

You can manually trigger Lighthouse CI:
1. Go to Actions tab
2. Select "Lighthouse CI" workflow
3. Click "Run workflow"
4. Select branch and run

## 🎯 Optimization Tips

### Improving Performance Scores

1. **Code Splitting**
   - Use dynamic imports for routes
   - Lazy load components not immediately needed
   - Split vendor bundles

2. **Image Optimization**
   - Use WebP format
   - Implement lazy loading
   - Provide responsive images
   - Add width/height attributes

3. **Bundle Size**
   - Remove unused dependencies
   - Use tree-shaking
   - Minify and compress assets
   - Use CDN for static assets

4. **Caching Strategy**
   - Implement service worker
   - Set proper cache headers
   - Use long-term caching for static assets

### Improving Accessibility Scores

1. **ARIA Attributes**
   - Add proper ARIA labels
   - Use semantic HTML
   - Ensure keyboard navigation

2. **Color Contrast**
   - Maintain 4.5:1 contrast ratio for text
   - Use color-blind friendly palettes
   - Test with accessibility tools

3. **Forms**
   - Label all inputs
   - Provide clear error messages
   - Support keyboard-only navigation

### Improving Best Practices Scores

1. **Console Errors**
   - Fix all console errors
   - Remove console.log statements
   - Handle promise rejections

2. **Security**
   - Use HTTPS
   - Set proper CSP headers
   - Avoid vulnerable libraries

### Improving SEO Scores

1. **Meta Tags**
   - Add descriptive title and description
   - Use Open Graph tags
   - Add structured data

2. **Crawlability**
   - Create sitemap.xml
   - Add robots.txt
   - Use semantic HTML

## 📊 Monitoring and Tracking

### Historical Trends
To track performance over time:
1. Download artifacts from multiple runs
2. Compare JSON reports
3. Monitor score trends
4. Identify performance regressions

### Setting Up Lighthouse Server (Optional)
For persistent storage and trend analysis:

1. Deploy Lighthouse Server
2. Add server URL to `lighthouserc.json`:
```json
{
  "ci": {
    "upload": {
      "target": "lhci",
      "serverBaseUrl": "https://your-lighthouse-server.com",
      "token": "YOUR_TOKEN"
    }
  }
}
```
3. Set `LHCI_SERVER_TOKEN` secret in GitHub

## 🔐 GitHub Secrets (Optional)

For enhanced features, configure these secrets:

| Secret | Purpose | Required |
|--------|---------|----------|
| `LHCI_GITHUB_APP_TOKEN` | Enhanced PR integration | No |
| `LHCI_SERVER_TOKEN` | Persistent storage | No |

To add secrets:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Save

## 🐛 Troubleshooting

### Build Fails Before Lighthouse
- Check build logs in GitHub Actions
- Ensure all dependencies are installed
- Verify build script works locally

### Low Performance Scores
- Check bundle size (aim for <500KB initial JS)
- Optimize images and assets
- Review Chrome DevTools Performance panel
- Enable production build optimizations

### Accessibility Issues
- Use Chrome DevTools Lighthouse tab
- Test with screen readers
- Verify keyboard navigation
- Check color contrast ratios

### Missing Reports
- Ensure build completes successfully
- Check that `dist` folder is created
- Verify preview server starts correctly
- Check `.lighthouseci` directory exists

## 📚 Additional Resources

- [Lighthouse Documentation](https://developer.chrome.com/docs/lighthouse/)
- [Lighthouse CI Documentation](https://github.com/GoogleChrome/lighthouse-ci)
- [Web Vitals](https://web.dev/vitals/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Performance Best Practices](https://web.dev/performance/)

## 🎓 Understanding Scores

### Score Ranges
- **90-100**: Good (🟢 Green)
- **50-89**: Needs Improvement (🟡 Orange)
- **0-49**: Poor (🔴 Red)

### Core Web Vitals (Google Ranking Factors)
- **LCP** (Largest Contentful Paint): <2.5s
- **FID** (First Input Delay): <100ms
- **CLS** (Cumulative Layout Shift): <0.1

### Priority Hierarchy
1. Fix critical errors (red scores)
2. Improve warnings (orange scores)
3. Optimize for perfect scores (green, 90+)
4. Monitor trends over time

## 🔄 Continuous Improvement

Lighthouse CI helps maintain quality by:
- ✅ Catching performance regressions early
- ✅ Enforcing accessibility standards
- ✅ Validating best practices
- ✅ Tracking improvements over time
- ✅ Educating developers on web performance

Make performance testing part of your development workflow by:
1. Running Lighthouse locally during development
2. Reviewing PR comments before merging
3. Setting performance budgets
4. Celebrating improvements! 🎉

---

**Last Updated:** 2024
**Maintained By:** Geneva Bible Study Team
