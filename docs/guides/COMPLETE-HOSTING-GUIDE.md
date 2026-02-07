# Complete Hosting Architecture Guide

# GitHub Pages + Render + Custom DNS Setup

## ?? **Overview: Two-Part Architecture**

Your Evident.info needs BOTH services working together:

```
???????????????????????????????????????????????????????????
?                    Evident.info                         ?
?                  (Custom Domain)                        ?
???????????????????????????????????????????????????????????
               ?                      ?
               ?                      ?
    ??????????????????????  ?????????????????????
    ?  GitHub Pages      ?  ?    Render         ?
    ?  (Static Site)     ?  ?  (Flask App)      ?
    ?                    ?  ?                    ?
    ?  Marketing pages   ?  ?  Web application  ?
    ?  - Homepage        ?  ?  - Login          ?
    ?  - Docs            ?  ?  - Dashboard      ?
    ?  - Pricing         ?  ?  - Upload         ?
    ?  - Contact         ?  ?  - API            ?
    ??????????????????????  ?????????????????????
```

--

## ?? **Part 1: GitHub Pages Setup**

### **What It Does:**

- Hosts your static marketing website
- Shows: docs.html, pricing.html, contact.html
- No backend, no database
- Free, fast CDN

### **Setup Steps:**

#### **1. Enable GitHub Pages:**

```
1. Go to: https://github.com/DTB396/Evident.info/settings/pages
2. Under "Build and deployment":
   - Source: Deploy from a branch
   - Branch: main
   - Folder: / (root)
3. Click "Save"
4. Wait 2-3 minutes
5. Access at: https://dtb396.github.io/Evident.info
```

#### **2. Configure for GitHub Pages:**

Your repo needs a `_config.yml`:

```yaml
title: Evident Legal Technologies
description: Professional AI-powered eDiscovery platform
url: "https://dtb396.github.io"
baseurl: "/Evident.info"
markdown: kramdown

exclude:
  - "*.py"
  - requirements.txt
  - app.py
  - venv
  - -pycache-
  - instance
  - logs
  - uploads
```

#### **3. What Gets Deployed:**

GitHub Pages will serve:

- ? `index.html` ? https://dtb396.github.io/Evident.info/
- ? `docs.html` ? https://dtb396.github.io/Evident.info/docs.html
- ? `pricing.html` ? https://dtb396.github.io/Evident.info/pricing.html
- ? `contact.html` ? https://dtb396.github.io/Evident.info/contact.html
- ? `assets/` ? All CSS, JS, images
- ? `app.py` ? Excluded (Python files ignored)
- ? `templates/` ? Excluded (Flask templates ignored)

--

## ?? **Part 2: Render Setup**

### **What It Does:**

- Hosts your Flask application
- Runs Python backend
- Connects to PostgreSQL
- Handles file uploads, user auth, BWC analysis

### **Setup Steps:**

#### **1. Already Configured:**

Your `render.yaml` is already set up correctly:

```yaml
services:
  - type: web
    name: Evident-legal-tech
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app -bind 0.0.0.0:$PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: Evident-db
          property: connectionString

databases:
  - name: Evident-db
    databaseName: Evident_production
```

#### **2. Auto-Deploy:**

- Render watches your GitHub repo
- On push to `main` branch
- Automatically rebuilds and deploys
- Takes 5-7 minutes

#### **3. What Gets Deployed:**

Render deploys:

- ? `app.py` ? Flask application
- ? `requirements.txt` ? Python dependencies
- ? `templates/` ? Flask templates
- ? Database connection
- ? File upload handling

--

## ?? **Part 3: DNS Configuration (Custom Domain)**

### **Goal: Use Evident.info for BOTH services**

#### **Recommended DNS Setup:**

```
Evident.info                    ? GitHub Pages (marketing site)
www.Evident.info                ? GitHub Pages (marketing site)
app.Evident.info                ? Render (Flask application)
api.Evident.info                ? Render API (optional)
```

--

### **DNS Records You Need:**

#### **For GitHub Pages (Evident.info):**

**At your domain registrar (GoDaddy, Namecheap, Cloudflare):**

```
Type: A
Name: @
Value: 185.199.108.153
TTL: 3600

Type: A
Name: @
Value: 185.199.109.153
TTL: 3600

Type: A
Name: @
Value: 185.199.110.153
TTL: 3600

Type: A
Name: @
Value: 185.199.111.153
TTL: 3600

Type: CNAME
Name: www
Value: dtb396.github.io
TTL: 3600
```

**These are GitHub's IP addresses for custom domains.**

--

#### **For Render (app.Evident.info):**

```
Type: CNAME
Name: app
Value: Evident-legal-tech.onrender.com
TTL: 3600
```

--

### **Complete DNS Setup Example (GoDaddy):**

| Type  | Name | Value                           | TTL    |
| ----- | ---- | ------------------------------- | ------ |
| A     | @    | 185.199.108.153                 | 1 Hour |
| A     | @    | 185.199.109.153                 | 1 Hour |
| A     | @    | 185.199.110.153                 | 1 Hour |
| A     | @    | 185.199.111.153                 | 1 Hour |
| CNAME | www  | dtb396.github.io                | 1 Hour |
| CNAME | app  | Evident-legal-tech.onrender.com | 1 Hour |

--

### **After DNS is Set:**

#### **1. Configure GitHub Pages for Custom Domain:**

```
1. Go to: https://github.com/DTB396/Evident.info/settings/pages
2. Under "Custom domain"
3. Enter: Evident.info
4. Click "Save"
5. Wait for DNS check (green checkmark)
6. Enable "Enforce HTTPS"
```

#### **2. Configure Render for Custom Domain:**

```
1. Go to: https://dashboard.render.com
2. Click "evident-legal-tech" service
3. Go to "Settings"
4. Scroll to "Custom Domains"
5. Click "Add Custom Domain"
6. Enter: app.Evident.info
7. Click "Save"
8. Wait for verification
9. SSL auto-provisions
```

--

## ?? **How It All Works Together:**

### **User visits Evident.info:**

```
User ? Evident.info
        ?
    DNS lookup
        ?
    185.199.108.153 (GitHub Pages)
        ?
    GitHub serves index.html
        ?
    User sees marketing site
```

### **User clicks "Login" button:**

```
User clicks "Login"
        ?
    Redirects to app.Evident.info/auth/login
        ?
    DNS lookup for app.Evident.info
        ?
    CNAME points to Evident-legal-tech.onrender.com
        ?
    Render serves Flask app
        ?
    User sees login page
```

--

## ?? **Complete User Journey:**

### **Scenario: User wants to analyze BWC footage**

**Step 1: Discovery** (GitHub Pages)

```
https://Evident.info
?
User reads about features
User clicks "Get Started"
```

**Step 2: Registration** (Render)

```
Redirects to: https://app.Evident.info/auth/register
?
User creates account (saved in PostgreSQL on Render)
```

**Step 3: Login** (Render)

```
https://app.Evident.info/auth/login
?
User logs in (Flask session on Render)
```

**Step 4: Dashboard** (Render)

```
https://app.Evident.info/auth/dashboard
?
User uploads BWC videos
Flask processes uploads
PostgreSQL stores metadata
```

**Step 5: Analysis** (Render)

```
https://app.Evident.info/analysis/123
?
User views AI analysis results
```

**Step 6: Documentation** (GitHub Pages)

```
User clicks "Help" ? https://Evident.info/docs.html
?
Redirects back to GitHub Pages
User reads documentation
```

--

## ?? **SSL/HTTPS (Automatic):**

### **GitHub Pages:**

- Free SSL from Let's Encrypt
- Automatically enabled for custom domains
- No configuration needed

### **Render:**

- Free SSL from Let's Encrypt
- Automatically provisioned for custom domains
- Auto-renews every 90 days

**Both services handle SSL for you!**

--

## ?? **Costs:**

| Service              | Cost        | What You Get                         |
| -------------------- | ----------- | ------------------------------------ |
| **GitHub Pages**     | FREE        | Unlimited bandwidth, free SSL        |
| **Render Free Tier** | FREE        | 750 hours/month, sleeps after 15 min |
| **Render Starter**   | $7/month    | Always-on, no sleep                  |
| **Custom Domain**    | $10-15/year | Your own Evident.info domain         |
| **PostgreSQL Free**  | FREE        | 256MB storage                        |

**Total minimum cost: ~$10-15/year (just domain)**

--

## ?? **Step-by-Step Setup (Complete):**

### **Phase 1: Commit Current Changes**

```bash
git add .
git commit -m "docs: Complete hosting architecture guides"
git push origin main
```

### **Phase 2: Enable GitHub Pages**

```
1. GitHub ? Settings ? Pages
2. Source: Deploy from branch main
3. Wait 2 minutes
4. Check: https://dtb396.github.io/Evident.info
```

### **Phase 3: Wait for Render Deployment**

```
1. Render auto-detects push
2. Builds in 5-7 minutes
3. Check: https://Evident-legal-tech.onrender.com
```

### **Phase 4: Configure Custom Domain (Optional)**

**If you own Evident.info:**

**4a. DNS Records:**

- Add GitHub Pages A records
- Add Render CNAME record

**4b. GitHub Pages:**

- Add custom domain: Evident.info
- Enable HTTPS

**4c. Render:**

- Add custom domain: app.Evident.info
- Wait for SSL

--

## ?? **Current Status Check:**

### **What's Already Done:**

? Code pushed to GitHub ? Render.yaml configured ? Database linked ? Circular
imports fixed ? All files ready

### **What Happens Next:**

**In 5 minutes:**

1. ? GitHub Pages builds (if enabled)
2. ? Render deploys Flask app
3. ? PostgreSQL database created

**You'll have:**

- ? https://dtb396.github.io/Evident.info (marketing)
- ? https://Evident-legal-tech.onrender.com (app)

**Later (optional):**

- ? Custom domain: Evident.info
- ? Custom app domain: app.Evident.info

--

## ?? **Key Takeaways:**

1. **GitHub Pages** = Static marketing site (free, fast)
2. **Render** = Flask application (Python, database)
3. **Both deploy from same repo** but serve different purposes
4. **DNS splits traffic** between them
5. **SSL is automatic** on both
6. **Everything is free** (except custom domain)

--

## ?? **Troubleshooting:**

### **GitHub Pages not showing:**

- Check Settings ? Pages ? Source is set
- Wait 2-3 minutes for build
- Check Actions tab for errors

### **Render not working:**

- Check dashboard.render.com for logs
- Look for red errors
- Database should say "Available"

### **Custom domain not working:**

- DNS propagation takes 1-48 hours
- Check with: https://dnschecker.org
- Verify DNS records are correct

--

## ? **Quick Start Checklist:**

**Right Now:**

- [ ] Enable GitHub Pages (Settings ? Pages)
- [ ] Wait for Render deployment (5-7 min)
- [ ] Test both URLs

**Later (Optional):**

- [ ] Buy custom domain (Evident.info)
- [ ] Configure DNS records
- [ ] Add custom domain to GitHub Pages
- [ ] Add custom domain to Render
- [ ] Enable HTTPS on both

--

**Both services work together perfectly! GitHub Pages for marketing, Render for
the app! ??**
