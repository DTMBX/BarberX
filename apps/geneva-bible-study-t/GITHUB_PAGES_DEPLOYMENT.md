# GitHub Pages Deployment Guide

Complete guide for deploying the Geneva Bible Study Platform to GitHub Pages with automated workflows.

## 🚀 Quick Start (5 Minutes)

### Step 1: Prepare Your Repository

1. **Update Repository URLs** in `package.json`:
   ```json
   {
     "repository": {
       "type": "git",
       "url": "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
     },
     "bugs": {
       "url": "https://github.com/YOUR_USERNAME/YOUR_REPO/issues"
     },
     "homepage": "https://YOUR_USERNAME.github.io/YOUR_REPO/"
   }
   ```

2. **Update Base Path** in `vite.config.ts`:
   ```typescript
   export default defineConfig({
     base: process.env.GITHUB_ACTIONS ? '/YOUR_REPO/' : '/',
     // ... rest of config
   })
   ```
   
   Replace `/spark-template/` with `/YOUR_REPO/` (your actual repository name)

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top navigation)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source:** Select **GitHub Actions** (not "Deploy from a branch")
   - This enables the automated workflow

### Step 3: Deploy

```bash
# Commit any changes
git add .
git commit -m "Configure for GitHub Pages deployment"

# Push to main branch
git push origin main
```

### Step 4: Monitor & Access

1. **Monitor Deployment:**
   - Go to the **Actions** tab in your repository
   - Watch the "Deploy to GitHub Pages" workflow
   - It will show:
     - ✅ Build step (npm install & build)
     - ✅ Deploy step (upload to Pages)

2. **Access Your Site:**
   - Once complete (usually 2-5 minutes), your site will be live at:
   - `https://YOUR_USERNAME.github.io/YOUR_REPO/`

---

## 🔧 How It Works

### Automated Workflow

The `.github/workflows/deploy.yml` file contains a GitHub Actions workflow that:

1. **Triggers on:**
   - Every push to `main` branch
   - Manual workflow dispatch (Actions tab → Run workflow)

2. **Build Job:**
   - Checks out your code
   - Sets up Node.js 20
   - Installs dependencies with `npm ci`
   - Builds production bundle with `npm run build`
   - Uploads `dist` folder as artifact

3. **Deploy Job:**
   - Takes the build artifact
   - Deploys to GitHub Pages
   - Updates your live site

### Build Configuration

**Vite Config (`vite.config.ts`):**
```typescript
{
  base: process.env.GITHUB_ACTIONS ? '/YOUR_REPO/' : '/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['@radix-ui/react-dialog', ...],
          'phosphor-icons': ['@phosphor-icons/react'],
        },
      },
    },
  },
}
```

**Benefits:**
- ✅ Correct asset paths for subdirectory hosting
- ✅ Code splitting for faster loads
- ✅ Optimized chunks for caching
- ✅ No sourcemaps in production

---

## 📋 Deployment Checklist

Before first deployment:

- [ ] Repository name updated in `package.json`
- [ ] Base path updated in `vite.config.ts`
- [ ] GitHub Pages source set to "GitHub Actions"
- [ ] Build succeeds locally: `npm run build`
- [ ] Preview works locally: `npm run preview`

After deployment:

- [ ] Site loads at GitHub Pages URL
- [ ] All pages navigate correctly
- [ ] Bible reader functions properly
- [ ] Audio playback works
- [ ] Search functionality works
- [ ] Dark mode toggles correctly
- [ ] Social features operate
- [ ] No console errors

---

## 🔄 Continuous Deployment

Once configured, your site automatically deploys when you:

```bash
# Make changes to your code
git add .
git commit -m "Add new feature"
git push origin main
```

**Automatic Process:**
1. GitHub detects push to `main`
2. Workflow starts automatically
3. Builds and deploys new version
4. Site updates in 2-5 minutes

---

## 🛠️ Manual Deployment (Alternative)

If you prefer manual control or want to deploy from your local machine:

### Option 1: Using gh-pages Package

```bash
# Install gh-pages
npm install -D gh-pages

# Deploy manually
npm run deploy:manual
```

This:
- Builds your project
- Pushes `dist` folder to `gh-pages` branch
- GitHub Pages serves from that branch

**Note:** Change Pages source to "Deploy from a branch" → `gh-pages` → `/ (root)`

### Option 2: Manual Upload

```bash
# Build locally
npm run build

# The dist folder contains your site
# Upload contents manually via GitHub web interface
```

---

## 🌐 Custom Domain (Optional)

To use your own domain (e.g., `bible.example.com`):

### Step 1: Add CNAME to Repository

Create `public/CNAME` file:
```
bible.example.com
```

### Step 2: Configure DNS

Add DNS records at your domain registrar:

**Option A: Apex Domain** (`example.com`)
```
A     @     185.199.108.153
A     @     185.199.109.153
A     @     185.199.110.153
A     @     185.199.111.153
```

**Option B: Subdomain** (`bible.example.com`)
```
CNAME bible YOUR_USERNAME.github.io
```

### Step 3: Update GitHub Settings

1. Go to Settings → Pages
2. Custom domain: Enter `bible.example.com`
3. Enable "Enforce HTTPS" (after DNS propagates)

### Step 4: Update Config

In `vite.config.ts`:
```typescript
base: process.env.GITHUB_ACTIONS ? '/' : '/',
```

In `package.json`:
```json
"homepage": "https://bible.example.com/"
```

---

## 🐛 Troubleshooting

### Build Fails

**Error: "Cannot find module"**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Error: "TypeScript errors"**
```bash
# Check TypeScript version
npm list typescript

# Fix type errors or use --noCheck flag (already in package.json)
npm run build
```

### Pages Not Loading

**404 Errors on Refresh**
- ✅ GitHub Pages automatically handles SPA routing
- ✅ Workflow includes proper configuration

**Assets Not Loading (404 on CSS/JS)**
- ❌ Base path incorrect in `vite.config.ts`
- ✅ Should be `/YOUR_REPO/` (with trailing slash)

**Blank Page**
- Check browser console for errors
- Verify build works locally: `npm run preview`
- Check Actions tab for workflow errors

### Workflow Not Running

**Push doesn't trigger deploy:**
1. Check `.github/workflows/deploy.yml` exists
2. Verify you pushed to `main` branch
3. Check Actions tab for error messages
4. Verify Pages source is "GitHub Actions"

**Workflow fails with permissions error:**
1. Go to Settings → Actions → General
2. Workflow permissions: Select "Read and write permissions"
3. Save changes and re-run workflow

### Site Not Updating

**Changes don't appear after deploy:**
1. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Check Actions tab - workflow must complete successfully
4. Wait 2-5 minutes after workflow completes

---

## 📊 Monitoring & Analytics

### Build Status Badge

Add to `README.md`:
```markdown
![Build Status](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/YOUR_REPO/deploy.yml?branch=main)
```

### Deployment History

View all deployments:
1. Go to **Actions** tab
2. Click **Deploy to GitHub Pages** workflow
3. See all runs with timestamps and status

### Performance Monitoring

After deployment:

```bash
# Use Lighthouse (Chrome DevTools)
1. Open your site
2. F12 → Lighthouse tab
3. Run audit

# Use PageSpeed Insights
# Visit: https://pagespeed.web.dev/
# Enter your GitHub Pages URL
```

---

## 🔒 Security & Best Practices

### Environment Variables

**Do NOT commit secrets to repository!**

For production environment variables:
1. Go to Settings → Secrets and variables → Actions
2. New repository secret
3. Use in workflow: `${{ secrets.YOUR_SECRET }}`

### Dependencies

```bash
# Regular security audits
npm audit

# Fix vulnerabilities
npm audit fix

# Update dependencies
npm update
```

### HTTPS

- ✅ GitHub Pages enforces HTTPS automatically
- ✅ Custom domains: Enable "Enforce HTTPS" after DNS propagates

---

## 🚀 Advanced Configuration

### Multiple Environments

Deploy to staging and production:

```yaml
# .github/workflows/deploy-staging.yml
on:
  push:
    branches:
      - develop  # Staging from develop branch

# .github/workflows/deploy.yml
on:
  push:
    branches:
      - main  # Production from main branch
```

### Preview Deployments

Preview pull requests before merging:

```yaml
name: Preview PR

on:
  pull_request:
    branches:
      - main

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run build
      - name: Comment PR with preview info
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Build successful! Preview the changes locally.'
            })
```

### Build Optimization

Improve build performance:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    target: 'es2015',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remove console.log in production
      },
    },
  },
})
```

---

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [Project PRD](./PRD.md)
- [Full Deployment Guide](./DEPLOYMENT.md)

---

## 🆘 Getting Help

**Deployment Issues:**
1. Check [GitHub Actions logs](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)
2. Review this guide's Troubleshooting section
3. Search existing [GitHub Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)
4. Create new issue with:
   - Error message
   - Actions log
   - Steps to reproduce

**Build Issues:**
```bash
# Test locally first
npm run build
npm run preview

# Check build output
ls -la dist/

# Verify asset paths
cat dist/index.html
```

---

**Last Updated:** January 2025

**Status:** ✅ Production Ready

Enjoy your deployed Geneva Bible Study Platform! 🎉
