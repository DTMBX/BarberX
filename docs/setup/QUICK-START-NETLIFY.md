# 🚀 QUICK START: Deploy Evident.info to Netlify

**You're 3 steps away from going live!**

--

## ✅ Files Created

I've set up everything you need:

1. ✅ **netlify.toml** - Netlify configuration (build settings, headers,
   redirects)
2. ✅ **Gemfile** - Ruby dependencies for Jekyll
3. ✅ **runtime.txt** - Ruby version (3.1.0)
4. ✅ **.nvmrc** - Node version (18)
5. ✅ **deploy-netlify.ps1** - Windows deployment script
6. ✅ **NETLIFY-DEPLOYMENT-GUIDE.md** - Complete documentation

--

## 🎯 Option 1: Deploy via Netlify Dashboard (EASIEST)

### Step 1: Push to GitHub

```powershell
git add .
git commit -m "Add Netlify deployment configuration"
git push origin main
```

### Step 2: Connect to Netlify

1. Go to **[app.netlify.com](https://app.netlify.com)**
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **"GitHub"** and select your `Evident.info` repository
4. Netlify will auto-detect settings from `netlify.toml`:
   - **Build command:** `bundle exec jekyll build`
   - **Publish directory:** `_site`
5. Click **"Deploy site"**

### Step 3: Add Custom Domain

1. In Netlify dashboard → **Site Settings** → **Domain Management**
2. Click **"Add custom domain"**
3. Enter: **`Evident.info`**
4. Follow DNS configuration instructions

**Done! Your site will be live at https://Evident.info in 24-48 hours (DNS
propagation time)**

--

## 🎯 Option 2: Deploy via Netlify CLI (FASTER)

### Step 1: Install Netlify CLI

```powershell
npm install -g netlify-cli
```

### Step 2: Login to Netlify

```powershell
netlify login
```

This opens your browser to authenticate.

### Step 3: Initialize Your Site

```powershell
netlify init
```

Follow the prompts:

- **Create & configure a new site?** → Yes
- **Team:** Select your team
- **Site name:** Evident (or your choice)
- **Build command:** `bundle exec jekyll build`
- **Directory to deploy:** `_site`

### Step 4: Deploy!

```powershell
netlify deploy -prod
```

**Done! Your site is live!**

--

## 🎯 Option 3: Use My PowerShell Script (AUTOMATED)

I created a deployment script for you:

```powershell
.\deploy-netlify.ps1
```

This script:

- ✅ Checks if Netlify CLI is installed
- ✅ Tests Jekyll build locally
- ✅ Checks Git status
- ✅ Offers to commit changes
- ✅ Deploys to production or preview
- ✅ Opens your site in browser

**Choose option 1 for production deployment!**

--

## 📊 What Happens During Deployment?

1. **Netlify clones your repo** from GitHub
2. **Installs Ruby 3.1.0** (specified in runtime.txt)
3. **Runs `bundle install`** (installs Jekyll + plugins)
4. **Runs `bundle exec jekyll build`** (generates static site)
5. **Optimizes assets** (minifies CSS/JS, compresses images)
6. **Deploys to global CDN** (publishes \_site/ folder)
7. **Provisions SSL certificate** (free HTTPS)
8. **Your site is live!** ✨

**Build time:** 2-4 minutes  
**Deploy time:** ~30 seconds  
**Total:** ~5 minutes to live site

--

## 🌐 DNS Configuration (For Custom Domain)

### If Using Netlify DNS (Recommended):

1. In Netlify: **Domain Management** → **"Use Netlify DNS"**
2. Copy the 4 nameservers
3. Update at your domain registrar (GoDaddy, Namecheap, etc.)
4. Wait 24-48 hours for propagation

### If Using External DNS:

Add these records at your registrar:

| Type      | Name | Value                   | TTL  |
| --------- | ---- | ----------------------- | ---- |
| **A**     | @    | `75.2.60.5`             | 3600 |
| **CNAME** | www  | `your-site.netlify.app` | 3600 |

**HTTPS:** Netlify provides free SSL automatically!

--

## 🐛 Troubleshooting

### "Bundle install failed"

**Fix:** Jekyll dependencies need to be installed by Netlify (not locally). The
netlify.toml handles this.

### "Build failed - Ruby version mismatch"

**Fix:** Check runtime.txt has `3.1.0`

### "404 on all pages"

**Fix:** Check \_config.yml:

```yaml
baseurl: "" # Must be empty for root domain
```

### "Custom domain not working"

**Fix:** Wait 24-48 hours for DNS propagation. Check status at
[whatsmydns.net](https://whatsmydns.net)

--

## 📈 After Deployment

### Check Your Site

```powershell
netlify open:site
```

### View Build Logs

```powershell
netlify logs
```

### Check Deployment Status

```powershell
netlify status
```

### Redeploy

```powershell
netlify deploy -prod
```

--

## 💰 Netlify Pricing

**Free Starter Plan includes:**

- ✅ 100 GB bandwidth/month
- ✅ 300 build minutes/month
- ✅ Unlimited sites
- ✅ Free SSL certificates
- ✅ Global CDN
- ✅ Continuous deployment

**Perfect for Evident.info!** Your traffic will easily fit in the free tier.

--

## 🔄 Continuous Deployment (Auto-Deploy)

Once connected to GitHub:

- **Push to `main`** → Auto-deploys to production
- **Create PR** → Auto-creates preview deployment
- **Merge PR** → Auto-deploys to production

**No manual deploys needed!**

--

## 📞 Need Help?

1. **Complete Guide:** Read
   [NETLIFY-DEPLOYMENT-GUIDE.md](NETLIFY-DEPLOYMENT-GUIDE.md)
2. **Netlify Docs:** [docs.netlify.com](https://docs.netlify.com)
3. **Netlify Support:** [answers.netlify.com](https://answers.netlify.com)

--

## 🎉 YOU'RE READY!

**Recommended next steps:**

1. **Commit all files:**

   ```powershell
   git add .
   git commit -m "Add Netlify deployment configuration"
   git push origin main
   ```

2. **Deploy via Netlify dashboard** (Option 1 above)

3. **Configure custom domain** (Evident.info)

4. **Celebrate!** 🎊

Your site will be live at:

- **Temporary:** https://your-site.netlify.app (immediately)
- **Custom:** https://Evident.info (after DNS propagation)

**Happy deploying! 🚀**
