# 🚀 Quick Deployment Guide

Get your Geneva Bible Study Platform live on GitHub Pages in 5 minutes!

## Prerequisites

- ✅ GitHub account
- ✅ Git installed
- ✅ Node.js 20+ installed
- ✅ Code pushed to GitHub repository

---

## Step 1: Configure Repository (2 minutes)

### Option A: Automated Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x setup-github-pages.sh
./setup-github-pages.sh
```

**Windows:**
```bash
setup-github-pages.bat
```

The script will:
- Detect your GitHub repository
- Update `vite.config.ts`
- Update `package.json`
- Update `README.md`

### Option B: Manual Setup

1. **Update `vite.config.ts`:**
   ```typescript
   base: process.env.GITHUB_ACTIONS ? '/YOUR_REPO_NAME/' : '/',
   ```

2. **Update `package.json`:**
   ```json
   {
     "repository": {
       "url": "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
     },
     "homepage": "https://YOUR_USERNAME.github.io/YOUR_REPO/"
   }
   ```

3. **Update `README.md`:**
   - Replace `YOUR_USERNAME` with your GitHub username
   - Replace `YOUR_REPO` with your repository name

---

## Step 2: Enable GitHub Pages (1 minute)

1. Go to your repository on GitHub
2. Click **Settings** (top navigation)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source:** Select **"GitHub Actions"**
   - (NOT "Deploy from a branch")
5. Save changes

---

## Step 3: Deploy (1 minute)

```bash
# Commit your configuration changes
git add .
git commit -m "Configure for GitHub Pages deployment"

# Push to GitHub
git push origin main
```

The GitHub Actions workflow will:
1. Install dependencies
2. Build the application
3. Deploy to GitHub Pages

---

## Step 4: Verify (1 minute)

1. **Monitor Progress:**
   - Go to the **Actions** tab in your repository
   - Click on the running "Deploy to GitHub Pages" workflow
   - Wait for ✅ green checkmarks on both jobs

2. **Access Your Site:**
   - Once complete, visit:
   - `https://YOUR_USERNAME.github.io/YOUR_REPO/`

3. **Test Functionality:**
   - Home page loads
   - Bible reader works
   - Navigation functions
   - No console errors (F12)

---

## 🎉 Success!

Your site is now live! Every push to the `main` branch will automatically deploy updates.

---

## Common Issues & Solutions

### ❌ 404 Page Not Found

**Problem:** Site shows 404 error  
**Solution:**
- Verify Pages source is "GitHub Actions" (not "Deploy from a branch")
- Check base path in `vite.config.ts` matches your repo name
- Ensure workflow completed successfully

### ❌ Build Fails

**Problem:** Workflow shows red ❌  
**Solution:**
```bash
# Test build locally first
npm install
npm run build

# If successful, push again
git push origin main
```

### ❌ Blank Page

**Problem:** Site loads but shows nothing  
**Solution:**
- Check browser console (F12) for errors
- Verify base path in `vite.config.ts`
- Clear browser cache (Ctrl+Shift+R)

### ❌ Assets Not Loading (404 on CSS/JS)

**Problem:** Page loads but no styling  
**Solution:**
- Base path must match repository name exactly
- Must include trailing slash: `/repo-name/`

---

## Next Steps

### ✅ Use the Full Checklist
See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for comprehensive testing.

### 📚 Read the Full Guide
See [GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md) for advanced configuration.

### 🔒 Add Custom Domain (Optional)
1. Create `public/CNAME` with your domain
2. Configure DNS records
3. Enable HTTPS in GitHub settings

### 📊 Monitor Performance
Run Lighthouse audit:
1. Open your site
2. Press F12
3. Go to Lighthouse tab
4. Run audit

---

## Support

**Build Issues:**
```bash
npm run build
npm run preview
```

**Deployment Issues:**
- Check [Actions logs](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)
- Review workflow file: `.github/workflows/deploy.yml`

**General Questions:**
- Open an issue on GitHub
- Check existing documentation

---

## Quick Reference

| What | Where |
|------|-------|
| Your site | `https://YOUR_USERNAME.github.io/YOUR_REPO/` |
| Monitor deployments | [Actions tab] |
| Enable Pages | Settings → Pages |
| Build locally | `npm run build` |
| Test locally | `npm run preview` |

---

**Happy Deploying! 🚀**

*Last Updated: January 2025*
