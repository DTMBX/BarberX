# CI/CD Pipeline Overview

This document provides an overview of the automated CI/CD workflows configured for the Geneva Bible Study application.

## 🔄 Automated Workflows

### 1. Deploy to GitHub Pages
**File:** `.github/workflows/deploy.yml`

**Triggers:**
- Push to `main` branch
- Manual trigger via GitHub Actions UI

**Purpose:**
Automatically builds and deploys the application to GitHub Pages.

**Steps:**
1. Checkout repository
2. Setup Node.js 20
3. Install dependencies
4. Build application
5. Verify build output
6. Configure GitHub Pages
7. Upload artifact
8. Deploy to GitHub Pages

**Environment:**
- Node.js: 20.x
- npm: Uses package-lock.json for consistent builds

**Outputs:**
- Live deployment at GitHub Pages URL
- Build artifacts (retained for deployment)

**Permissions Required:**
- `contents: read`
- `pages: write`
- `id-token: write`

---

### 2. Lighthouse CI (Pull Requests)
**File:** `.github/workflows/lighthouse-ci.yml`

**Triggers:**
- Pull requests to `main` branch
- Push to `main` branch
- Manual trigger via GitHub Actions UI

**Purpose:**
Runs automated performance, accessibility, and best practices audits on every code change.

**Configuration:**
- **Device:** Desktop
- **Runs:** 3 (averaged)
- **Config:** `lighthouserc.json`

**Steps:**
1. Checkout repository
2. Setup Node.js 20
3. Install dependencies
4. Build application
5. Install Lighthouse CI
6. Run Lighthouse audits
7. Upload results as artifacts
8. Parse scores
9. Post PR comment with results
10. Check performance thresholds

**Thresholds:**
- Performance: ≥70 (❌ fails build if below)
- Accessibility: ≥90 (⚠️ warning)
- Best Practices: ≥80 (⚠️ warning)
- SEO: ≥80 (⚠️ warning)

**Outputs:**
- PR comment with detailed scores
- Lighthouse report artifacts (30-day retention)
- Pass/fail status

**Permissions Required:**
- `contents: read`
- `pull-requests: write`
- `issues: write`

---

### 3. Lighthouse CI - Full Audit (Weekly)
**File:** `.github/workflows/lighthouse-full.yml`

**Triggers:**
- Schedule: Every Sunday at 00:00 UTC (`0 0 * * 0`)
- Manual trigger via GitHub Actions UI

**Purpose:**
Comprehensive performance testing across both desktop and mobile configurations with detailed reporting.

**Jobs:**

#### Job 1: Desktop Audit
- **Device:** Desktop (1350×940)
- **Runs:** 3 (averaged)
- **Config:** `lighthouserc.json`
- **Output:** Desktop performance scores

#### Job 2: Mobile Audit
- **Device:** Mobile (412×823)
- **Runs:** 3 (averaged)
- **Config:** `lighthouserc.mobile.json`
- **Network:** Simulated 4G
- **Output:** Mobile performance scores

#### Job 3: Report Generation
- Downloads results from both audits
- Creates comprehensive GitHub issue
- Includes side-by-side comparison
- Provides actionable recommendations

**Outputs:**
- Desktop Lighthouse report (artifact)
- Mobile Lighthouse report (artifact)
- GitHub issue with weekly report
- Side-by-side score comparison

**Permissions Required:**
- `contents: read`
- `issues: write`

---

## 📊 Workflow Comparison

| Feature | Deploy | Lighthouse CI (PR) | Full Audit (Weekly) |
|---------|--------|-------------------|-------------------|
| **Trigger** | Push to main | PR + Push | Weekly schedule |
| **Frequency** | Every push | Every PR | Weekly |
| **Duration** | ~2-3 min | ~3-5 min | ~6-10 min |
| **Desktop Test** | No | Yes | Yes |
| **Mobile Test** | No | No | Yes |
| **PR Comments** | No | Yes | No |
| **GitHub Issues** | No | No | Yes |
| **Artifacts** | Build only | Lighthouse reports | Both audits |
| **Blocks Merge** | No | Yes (if perf < 70) | No |

---

## 🎯 Performance Standards

### Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | ≤2.5s | 2.5s - 4.0s | >4.0s |
| FID (First Input Delay) | ≤100ms | 100ms - 300ms | >300ms |
| CLS (Cumulative Layout Shift) | ≤0.1 | 0.1 - 0.25 | >0.25 |

### Score Categories

| Score Range | Rating | Color |
|-------------|--------|-------|
| 90-100 | Good | 🟢 Green |
| 50-89 | Needs Improvement | 🟡 Orange |
| 0-49 | Poor | 🔴 Red |

---

## 🔧 Configuration Files

### `lighthouserc.json` (Desktop)
```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop",
        "formFactor": "desktop"
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.7 }],
        "categories:accessibility": ["warn", { "minScore": 0.9 }]
      }
    }
  }
}
```

### `lighthouserc.mobile.json` (Mobile)
```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "settings": {
        "preset": "mobile",
        "formFactor": "mobile"
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.6 }],
        "categories:accessibility": ["warn", { "minScore": 0.9 }]
      }
    }
  }
}
```

### `performance-budget.json`
Defines resource size and count budgets:
- Scripts: 500KB max
- Stylesheets: 100KB max
- Images: 300KB max
- Fonts: 150KB max
- Total: 1000KB max

---

## 📈 Monitoring & Alerts

### PR Comments
Automatic comments on pull requests include:
- ✅ Performance scores with status
- 📊 Key metrics (FCP, LCP, TBT, CLS, SI)
- 📦 Bundle size information
- 💡 Quick tips and recommendations

### Weekly Reports
Comprehensive GitHub issues created every Sunday with:
- 🖥️ Desktop performance breakdown
- 📱 Mobile performance breakdown
- 📈 Trend analysis recommendations
- 🔗 Links to detailed reports

### Build Status
- ✅ Green: All checks passed
- ⚠️ Yellow: Warnings present
- ❌ Red: Performance below threshold (blocks merge)

---

## 🚨 Troubleshooting

### Deployment Fails
1. Check build logs in Actions tab
2. Verify `dist` folder is created
3. Check for TypeScript errors
4. Ensure all dependencies install correctly

### Lighthouse CI Fails
1. Check if build completed successfully
2. Verify preview server starts
3. Review specific failing audits
4. Check performance threshold violations

### Low Performance Scores
1. Download HTML report from artifacts
2. Review specific audit failures
3. Check bundle size analysis
4. Implement recommended optimizations

---

## 🔐 Secrets Configuration

### Optional Secrets

| Secret | Purpose | Required |
|--------|---------|----------|
| `LHCI_GITHUB_APP_TOKEN` | Enhanced Lighthouse integration | No |
| `LHCI_SERVER_TOKEN` | Persistent report storage | No |

To add secrets:
1. Repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Save

---

## 📚 Additional Resources

- **Lighthouse CI Docs:** [LIGHTHOUSE_CI.md](./LIGHTHOUSE_CI.md)
- **Quick Reference:** [LIGHTHOUSE_QUICK_REF.md](./LIGHTHOUSE_QUICK_REF.md)
- **Deployment Guide:** [DEPLOYMENT.md](./DEPLOYMENT.md)
- **GitHub Actions Docs:** https://docs.github.com/actions

---

## 🎓 Best Practices

### Before Merging
1. ✅ Review Lighthouse PR comment
2. ✅ Address any performance issues
3. ✅ Ensure all checks pass
4. ✅ Check artifact reports if needed

### Regular Maintenance
1. 📊 Review weekly performance reports
2. 🎯 Track performance trends
3. 🔧 Address degradation proactively
4. 📈 Set improvement goals

### Performance Culture
1. 🚀 Make performance a priority
2. 📏 Use metrics to guide decisions
3. 🔄 Iterate based on feedback
4. 🎉 Celebrate improvements

---

**Last Updated:** 2024  
**Maintained By:** Geneva Bible Study Team
