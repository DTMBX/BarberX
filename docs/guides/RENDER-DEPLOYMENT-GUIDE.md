# ?? Deploy Evident.info to Render - COMPLETE GUIDE

## ? Prerequisites

- ? GitHub account with Evident.info repo
- ? All code pushed to GitHub (DONE!)

--

## ?? STEP-BY-STEP DEPLOYMENT

### **Step 1: Create Render Account (2 minutes)**

1. Open your browser and go to: **https://dashboard.render.com/register**

2. Click **"Sign up with GitHub"**
   - This is easiest - it auto-connects your repos
   - Authorize Render to access your GitHub

3. You'll see the Render dashboard

--

### **Step 2: Create Web Service (3 minutes)**

1. **Click the big blue button:** `New +` (top right)

2. **Select:** `Web Service`

3. **Connect Repository:**
   - You'll see a list of your GitHub repos
   - Find: `DTB396/Evident.info`
   - Click: `Connect`

4. **Configure Service:**

   **Name:** `Evident-legal-tech`

   **Region:** `Oregon (US West)` (or closest to you)

   **Branch:** `main`

   **Runtime:** `Python 3`

   **Build Command:**

   ```bash
   pip install -r requirements.txt
   ```

   **Start Command:**

   ```bash
   gunicorn app:app -bind 0.0.0.0:$PORT -workers 2 -timeout 300
   ```

   **Instance Type:** `Free`

5. **Click:** `Create Web Service`

--

### **Step 3: Add Environment Variables (2 minutes)**

While the service is deploying, click **"Environment"** in left sidebar:

**Add these variables** (click "+ Add Environment Variable"):

1. **SECRET_KEY**

   ```
   Evident-legal-tech-2026-production-secure-key-change-me-to-random-string
   ```

2. **FLASK_ENV**

   ```
   production
   ```

3. **MAX_CONTENT_LENGTH**

   ```
   5368709120
   ```

4. **CORS_ORIGINS**

   ```
   https://Evident-legal-tech.onrender.com
   ```

5. **DATABASE_URL** (Render will auto-create this when you add a database)
   - Click "New +" ? "PostgreSQL"
   - Name: `Evident-db`
   - Plan: Free
   - Create
   - It will auto-add `DATABASE_URL`

**Optional (for AI features):**

6. **OPENAI_API_KEY** (if you have one)

   ```
   sk-your-openai-key-here
   ```

7. **ANTHROPIC_API_KEY** (if you have one)

   ```
   sk-ant-your-anthropic-key-here
   ```

8. **HUGGINGFACE_TOKEN** (if you have one)
   ```
   hf_your-huggingface-token-here
   ```

**Click:** `Save Changes`

--

### **Step 4: Wait for Deployment (5-10 minutes)**

1. Go to **"Events"** tab
2. You'll see the build progress:

   ```
   ?? Installing dependencies...
   ?? Building...
   ?? Deploying...
   ? Live!
   ```

3. **First deployment takes 5-10 minutes** (subsequent deploys are faster)

--

### **Step 5: Your App is LIVE! ??**

Once you see **"Live"** in green, your URL is ready:

**Your live URL:**

```
https://Evident-legal-tech.onrender.com
```

**Test it:**

1. Open that URL in your browser
2. You should see the Evident.info homepage
3. Click "Login"
4. Use:
   - Email: `admin@Evident.info`
   - Password: `Evident2026!`

--

## ?? IMPORTANT: Update Admin Password

After first login, change the default password!

--

## ?? What's Deployed:

? **Full Flask Application**

- User authentication
- Dashboard
- PDF upload
- BWC video upload
- Database (PostgreSQL)
- File storage (Render disk)

? **Features Working:**

- Login/Logout
- User management
- PDF processing
- Video uploads
- Case management

?? **AI Features:**

- Requires API keys (optional)
- Add keys in Environment Variables

--

## ?? Render Dashboard Features:

### **Logs:**

- Click "Logs" to see real-time server output
- Debug errors here

### **Metrics:**

- See CPU, Memory, Request stats

### **Settings:**

- Update environment variables
- Change instance size (upgrade from free)
- Configure custom domains

### **Auto-Deploy:**

- Every `git push` to `main` auto-deploys!
- Takes 2-3 minutes

--

## ?? Custom Domain (Optional)

If you own `Evident.info`:

1. **In Render Dashboard:**
   - Go to Settings ? Custom Domains
   - Click "Add Custom Domain"
   - Enter: `app.Evident.info`

2. **In Your Domain Registrar (GoDaddy, Namecheap, etc):**
   - Add CNAME record:
     - Name: `app`
     - Value: `Evident-legal-tech.onrender.com`
     - TTL: 3600

3. **Wait 10-60 minutes for DNS to propagate**

4. **Update CORS_ORIGINS:**
   ```
   https://app.Evident.info,https://Evident.info
   ```

--

## ?? Troubleshooting

### **Build Failed**

- Check "Logs" tab
- Common issue: Missing dependency in `requirements.txt`
- Fix: Update `requirements.txt`, commit, push

### **App Crashes**

- Check "Logs" tab for errors
- Common: Database connection issues
- Fix: Verify `DATABASE_URL` is set

### **404 Not Found**

- Render is sleeping (free tier sleeps after 15 min inactivity)
- Wait 30 seconds for wake-up
- Solution: Upgrade to paid tier ($7/month for always-on)

### **File Uploads Not Working**

- Free tier has limited disk space
- Solution: Use AWS S3 for uploads (config needed)

### **Database Full**

- Free PostgreSQL: 256MB limit
- Solution: Upgrade database or clean old data

--

## ?? Pricing

**Current Setup (FREE):**

- Web Service: Free tier (750 hrs/month)
- PostgreSQL: Free tier (256MB)
- **Total: $0/month**

**Upgrade Options:**

- Starter Web Service: $7/month (always-on, no sleep)
- Starter PostgreSQL: $7/month (1GB storage)
- Pro: $25/month (more resources)

--

## ?? Next Steps After Deployment:

1. ? Test all features
2. ? Update admin password
3. ? Add API keys for AI features (optional)
4. ? Set up custom domain (optional)
5. ? Monitor logs for errors
6. ? Share with users!

--

## ?? Support

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **Your App Logs:** https://dashboard.render.com ? Your Service ? Logs

--

## ? READY TO DEPLOY?

**Just follow Steps 1-5 above!**

**Your app will be live in 15 minutes!** ??

--

**Need help?** Screenshot any errors and I'll help debug!
