# 🚀 Netlify Deployment Guide for Evident.info

**Status:** Ready for Production Deployment  
**Platform:** Netlify  
**Site Type:** Jekyll Static Site + Serverless Functions  
**Custom Domain:** Evident.info

--

## 📋 Quick Start Deployment

### Option 1: Deploy via Netlify CLI (Recommended)

```bash
# 1. Install Netlify CLI globally
npm install -g netlify-cli

# 2. Login to your Netlify account
netlify login

# 3. Initialize your site
netlify init

# 4. Deploy to production
netlify deploy -prod
```

### Option 2: Deploy via Git (GitHub Integration)

1. **Push to GitHub:**

   ```bash
   git add .
   git commit -m "Add Netlify configuration"
   git push origin main
   ```

2. **Connect to Netlify:**
   - Go to [app.netlify.com](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Choose "GitHub" and select your `Evident.info` repository
   - Netlify will auto-detect settings from `netlify.toml`
   - Click "Deploy site"

3. **Configure Custom Domain:**
   - In Netlify dashboard → Site Settings → Domain Management
   - Click "Add custom domain"
   - Enter: `Evident.info`
   - Follow DNS configuration instructions

--

## 🔧 Configuration Files Created

### 1. `netlify.toml` (Main Configuration)

✅ **Build command:** `bundle exec jekyll build`  
✅ **Publish directory:** `_site`  
✅ **Environment:** Production/Staging/Development contexts  
✅ **Headers:** Security + Performance optimized  
✅ **Redirects:** Pretty URLs + API routing  
✅ **Ruby version:** 3.1.0  
✅ **Node version:** 18

### 2. `Gemfile` (Ruby Dependencies)

✅ Jekyll 4.3.2  
✅ Required plugins (feed, sitemap, SEO)  
✅ Development dependencies

### 3. `runtime.txt` (Ruby Version)

✅ Specifies Ruby 3.1.0 for Netlify build

### 4. `.nvmrc` (Node Version)

✅ Specifies Node 18 for build environment

--

## 🌐 Custom Domain Setup

### DNS Configuration for Evident.info

**Option A: Use Netlify DNS (Recommended)**

1. In Netlify: Site Settings → Domain Management → "Use Netlify DNS"
2. Copy the 4 Netlify nameservers
3. Update your domain registrar with these nameservers:
   ```
   dns1.p02.nsone.net
   dns2.p02.nsone.net
   dns3.p02.nsone.net
   dns4.p02.nsone.net
   ```
4. Wait for DNS propagation (up to 24-48 hours)

**Option B: External DNS (Keep Current Provider)**

Add these DNS records at your domain registrar:

| Type  | Name | Value                 | TTL  |
| ----- | ---- | --------------------- | ---- |
| A     | @    | `75.2.60.5`           | 3600 |
| CNAME | www  | `Evident.netlify.app` | 3600 |

**HTTPS/SSL Certificate:**

- ✅ Netlify provides free SSL via Let's Encrypt
- ✅ Auto-renews every 90 days
- ✅ Force HTTPS redirect enabled in `netlify.toml`

--

## 🏗️ Build Process

### What Happens During Deployment

1. **Netlify Clone:** Fetches your Git repository
2. **Install Ruby 3.1.0:** Sets up Ruby environment
3. **Install Gems:** Runs `bundle install`
4. **Install Node 18:** Sets up Node environment
5. **Install npm packages:** Runs `npm install`
6. **Jekyll Build:** Executes `bundle exec jekyll build`
7. **Optimize Assets:** Minifies CSS/JS, compresses images
8. **Deploy to CDN:** Publishes `_site/` to global CDN
9. **SSL Certificate:** Provisions HTTPS certificate
10. **Cache Invalidation:** Clears CDN cache

**Typical Build Time:** 2-4 minutes

--

## 📦 What Gets Deployed

### Static Site (Jekyll)

✅ All HTML pages (`index.html`, `admin.html`, etc.)  
✅ Jekyll layouts from `_layouts/`  
✅ CSS from `assets/css/`  
✅ JavaScript files  
✅ Images and media  
✅ Collections (cases, essays, OPRA requests)

### What's EXCLUDED

❌ `app.py` (Flask backend - see serverless functions below)  
❌ `*.py` files (Python backend)  
❌ `node_modules/`  
❌ `vendor/`  
❌ `.git/`  
❌ Development files (README.md, etc.)

--

## ⚡ Flask Backend Integration (Optional)

Your site has Flask backend components (`app.py`, auth routes, etc.). Here are
your options:

### Option 1: Netlify Functions (Serverless)

Convert Flask routes to Netlify Functions:

```javascript
// netlify/functions/auth-handler.js
exports.handler = async (event, context) => {
  // Handle /auth/* routes
  const path = event.path.replace("/.netlify/functions/auth-handler/", "");

  // Your auth logic here
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "Auth handler" }),
  };
};
```

**Pros:** Free tier, auto-scaling, integrated with static site  
**Cons:** Cold starts, function timeout limits

### Option 2: Separate Backend (Heroku/Railway/Render)

Deploy `app.py` to a separate platform:

1. Deploy Flask to Heroku/Railway/Render
2. Update API endpoints in frontend to point to backend URL
3. Configure CORS in Flask to allow requests from `Evident.info`

**Pros:** Full Flask capabilities, longer execution time  
**Cons:** Separate deployment, additional hosting cost

### Option 3: Hybrid (Recommended for Now)

1. **Static pages** → Netlify (instant, free)
2. **Simple forms** → Netlify Forms (included)
3. **Complex backend** → Deploy Flask separately when needed

--

## 🔒 Environment Variables

### Set in Netlify Dashboard

Go to: Site Settings → Environment Variables → Add Variable

**Recommended Variables:**

```bash
JEKYLL_ENV=production
SITE_URL=https://Evident.info
CONTACT_EMAIL=contact@Evident.info

# If using backend
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
API_KEY=your-api-key
```

**Access in Jekyll templates:**

```liquid
{{ site.env.SITE_URL }}
```

--

## 🎨 Pre-Deployment Checklist

### Before Your First Deploy

- [x] `netlify.toml` configuration created
- [x] `Gemfile` with Jekyll dependencies
- [x] `runtime.txt` specifies Ruby version
- [x] `.nvmrc` specifies Node version
- [ ] **Update `_config.yml`:** Verify `url: "https://Evident.info"`
- [ ] **Test local build:** Run `bundle exec jekyll build`
- [ ] **Check `_site/` output:** Ensure all pages generated
- [ ] **Commit all changes:** `git add . && git commit -m "Netlify config"`
- [ ] **Push to GitHub:** `git push origin main`

### Post-Deployment Verification

- [ ] Visit `https://your-site.netlify.app` (temporary URL)
- [ ] Check all pages load correctly
- [ ] Verify navigation works
- [ ] Test forms (if any)
- [ ] Check mobile responsiveness
- [ ] Verify SSL certificate (HTTPS)
- [ ] Test custom domain (after DNS propagation)
- [ ] Check 404 page
- [ ] Verify redirects work

--

## 📊 Performance Optimization

### Already Configured in `netlify.toml`

✅ **Asset Optimization:**

- CSS bundling and minification
- JavaScript bundling and minification
- Image compression
- HTML pretty URLs

✅ **Caching Strategy:**

- Static assets: 1 year cache
- HTML pages: 1 hour cache
- Service worker: No cache

✅ **Security Headers:**

- X-Frame-Options
- X-XSS-Protection
- Content-Security-Policy
- Referrer-Policy

✅ **CDN:**

- Global edge network
- Auto-scaling
- DDoS protection

--

## 🐛 Troubleshooting

### Common Build Errors

**Error: `Jekyll not found`**

```bash
# Solution: Ensure Gemfile includes Jekyll
gem "jekyll", "~> 4.3.2"
```

**Error: `Ruby version mismatch`**

```bash
# Solution: Check runtime.txt matches Gemfile
# runtime.txt: 3.1.0
```

**Error: `Cannot find module 'jekyll-feed'`**

```bash
# Solution: Add to Gemfile plugins group
group :jekyll_plugins do
  gem "jekyll-feed"
end
```

**Error: `404 on all pages`**

```bash
# Solution: Check _config.yml baseurl
baseurl: "" # Must be empty for root domain
```

### Build is Slow

1. **Optimize images** before committing (use ImageOptim, TinyPNG)
2. **Reduce dependencies** in Gemfile
3. **Use incremental builds** (add to \_config.yml):
   ```yaml
   incremental: true
   ```

### Custom Domain Not Working

1. **Wait for DNS propagation:** Can take 24-48 hours
2. **Check DNS settings:** Use [WhatsMyDNS.net](https://www.whatsmydns.net)
3. **Verify Netlify domain config:** Must match exactly
4. **Force HTTPS:** Enable in Netlify dashboard

--

## 💰 Netlify Pricing

### Free Starter Plan (Perfect for Evident.info)

✅ 100 GB bandwidth/month  
✅ 300 build minutes/month  
✅ Unlimited sites  
✅ Free SSL certificates  
✅ Global CDN  
✅ Continuous deployment  
✅ Form submissions (100/month)  
✅ Serverless functions (125k requests/month)

### When to Upgrade

- More than 100 GB bandwidth
- Need team collaboration
- Advanced analytics
- Priority support

**Current Estimate:** Free tier is sufficient for your traffic level

--

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push

Once connected to GitHub, every push triggers:

1. **`main` branch** → Production deployment
2. **`develop` branch** → Preview deployment
3. **Pull requests** → Deploy previews

**Deploy Previews:**

- Each PR gets unique URL: `https://deploy-preview-123--Evident.netlify.app`
- Test changes before merging
- Share with team for review

--

## 📈 Monitoring & Analytics

### Built-in Netlify Analytics

Enable in dashboard for:

- Page views
- Unique visitors
- Bandwidth usage
- Top pages
- Traffic sources

**Cost:** $9/month (optional)

### Free Alternatives

1. **Google Analytics** - Add to `_layouts/default.html`
2. **Cloudflare Analytics** - If using Cloudflare DNS
3. **Plausible** - Privacy-friendly alternative

--

## 🎯 Quick Commands Reference

```bash
# Local development
bundle exec jekyll serve

# Build locally (test before deploy)
bundle exec jekyll build

# Deploy to Netlify (production)
netlify deploy -prod

# Deploy preview
netlify deploy

# Check build logs
netlify logs

# Open site in browser
netlify open:site

# Open Netlify dashboard
netlify open:admin

# Check site status
netlify status
```

--

## 📞 Support Resources

### Netlify Documentation

- [Netlify Docs](https://docs.netlify.com)
- [Jekyll on Netlify](https://docs.netlify.com/configure-builds/common-configurations/jekyll/)
- [Custom Domains](https://docs.netlify.com/domains-https/custom-domains/)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)

### Community

- [Netlify Community Forums](https://answers.netlify.com)
- [Netlify Discord](https://discord.com/invite/netlify)

### Evident Specific

- Site URL: `https://Evident.info`
- Git Repo: `github.com/your-username/Evident.info`
- Netlify Dashboard: `app.netlify.com/sites/your-site-name`

--

## 🚀 Ready to Deploy!

**You're all set!** Your Netlify configuration is production-ready.

### Next Steps:

1. **Test local build:**

   ```bash
   bundle install
   bundle exec jekyll build
   ```

2. **Commit configuration:**

   ```bash
   git add netlify.toml Gemfile runtime.txt .nvmrc
   git commit -m "Add Netlify deployment configuration"
   git push origin main
   ```

3. **Deploy to Netlify:**
   - Option A: Connect GitHub repo in Netlify dashboard
   - Option B: Run `netlify init` and `netlify deploy -prod`

4. **Configure custom domain:**
   - Add `Evident.info` in Netlify dashboard
   - Update DNS settings at your registrar

**Expected Timeline:**

- Initial deployment: 5 minutes
- DNS propagation: 24-48 hours
- SSL certificate: Automatic after DNS

--

**Happy deploying! 🎉**

Need help? Check the troubleshooting section or contact Netlify support.
