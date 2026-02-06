# GitHub Pages Deployment (FREE Alternative to Netlify)

## ✅ Your Site is Already Configured!

Your `_config.yml` is set up perfectly for GitHub Pages.

--

## 🚀 Enable GitHub Pages (2 Clicks)

### Method 1: Use VS Code (Easiest)

Open this URL in the Simple Browser:

```
https://github.com/DTB396/Evident.info/settings/pages
```

Then:

1. **Source:** Deploy from a branch
2. **Branch:** `main`
3. **Folder:** `/ (root)`
4. Click **Save**

**Your site will be live in 30 seconds at:**

```
https://dtb396.github.io/Evident.info
```

--

## 🌐 Custom Domain (Evident.info)

After GitHub Pages is enabled:

1. Go to: https://github.com/DTB396/Evident.info/settings/pages
2. Scroll to "Custom domain"
3. Enter: `Evident.info`
4. Click **Save**

Then update your DNS:

- **Type:** CNAME
- **Name:** www
- **Value:** dtb396.github.io

- **Type:** A Record
- **Name:** @
- **Value:** 185.199.108.153
- Add 3 more A records: 185.199.109.153, 185.199.110.153, 185.199.111.153

--

## 💰 Cost Comparison

| Platform         | Cost      | Build Minutes | Bandwidth   |
| ---------------- | --------- | ------------- | ----------- |
| **GitHub Pages** | **FREE**  | Unlimited     | 100GB/month |
| Netlify          | $19/month | 300 min       | 100GB       |
| Vercel           | FREE      | Unlimited     | 100GB       |

**Winner:** GitHub Pages (completely free, no credit card needed)

--

## ⚡ GitHub Actions (Auto-Deploy)

Your site auto-deploys on every push to `main` branch.

No configuration needed - GitHub detects Jekyll automatically.

**Check build status:**

```
https://github.com/DTB396/Evident.info/actions
```

--

## 🔧 What About Netlify Forms?

GitHub Pages doesn't have built-in forms, but you have 3 FREE options:

### Option 1: Formspree (Recommended)

```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
  <input type="email" name="email" required />
  <button type="submit">Subscribe</button>
</form>
```

- FREE: 50 submissions/month
- Paid: $10/month for unlimited

### Option 2: Google Forms

Embed Google Forms (100% free, unlimited)

### Option 3: Backend API (Railway)

Use your Flask backend for form submissions (what we already set up!)

--

## 🎯 Recommended Architecture (All FREE)

```
┌─────────────────────────────────┐
│  GitHub Pages (Frontend)         │
│  https://Evident.info           │
│  ✅ FREE Forever               │
│  ✅ Unlimited builds           │
│  ✅ 100GB bandwidth/month      │
└────────────┬────────────────────┘
             │
             │ API Calls
             ↓
┌─────────────────────────────────┐
│  Railway (Backend API)          │
│  https://api.Evident.info       │
│  ✅ $5 free credit/month       │
│  ✅ Auto-scaling               │
│  ✅ PostgreSQL included        │
└─────────────────────────────────┘
```

**Total Cost: $0/month** (until you exceed Railway's $5 credit)

--

## 🚀 Deploy Backend to Railway NOW

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up

# Your API will be at:
# https://Evident-api-production.up.railway.app
```

Then update forms to use Railway API instead of Netlify Forms.

--

## ✅ Your New Deployment is Live!

After enabling GitHub Pages, your site will be at:

**Temporary URL:**

```
https://dtb396.github.io/Evident.info
```

**Custom Domain (after DNS setup):**

```
https://Evident.info
```

**Build logs:**

```
https://github.com/DTB396/Evident.info/actions
```

--

## 💡 Next Steps

1. ✅ Enable GitHub Pages (link above)
2. ✅ Wait 30 seconds for first deploy
3. ✅ Visit https://dtb396.github.io/Evident.info
4. ✅ Deploy backend: `railway up`
5. ✅ Configure custom domain (optional)

**No credit card. No billing. Just works.** 🎉
