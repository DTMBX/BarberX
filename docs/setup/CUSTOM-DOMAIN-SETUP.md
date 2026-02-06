# ?? Deploy Evident.info to Custom Domain - Complete Guide

## ?? Goal:

Get your Render app live at **app.Evident.info** (or **Evident.info**)

--

## ?? **Quick Start (5 Minutes):**

### **Step 1: Add Domain in Render**

1. Go to **https://dashboard.render.com**
2. Click your service: **Evident-legal-tech**
3. Click **"Settings"** (left sidebar)
4. Scroll to **"Custom Domains"**
5. Click **"Add Custom Domain"**
6. Enter: `app.Evident.info`
7. Click **"Add"**

Render will show you DNS instructions.

--

### **Step 2: Update DNS (Choose Your Registrar)**

**Where did you buy Evident.info?**

- [**GoDaddy**](#godaddy) ? See CUSTOM-DOMAIN-GODADDY.md
- [**Namecheap**](#namecheap) ? See CUSTOM-DOMAIN-NAMECHEAP.md
- [**Cloudflare**](#cloudflare) ? See CUSTOM-DOMAIN-CLOUDFLARE.md
- [**Other**](#other-registrars) ? See below

--

### **Step 3: Update Render Environment**

In Render dashboard:

1. Go to **Environment** tab
2. Find `CORS_ORIGINS` variable
3. Update value to:
   ```
   https://app.Evident.info,https://Evident.info,https://www.Evident.info
   ```
4. Click **"Save Changes"**
5. Render will auto-redeploy

--

### **Step 4: Wait for Verification**

- **DNS Propagation:** 5 minutes - 2 hours
- **SSL Certificate:** Auto-provisioned after DNS verifies
- **Check Status:** Render dashboard ? Custom Domains

When status shows **"Verified"** ? with ??, you're live!

--

## ?? **Detailed Instructions by Registrar:**

### **GoDaddy:**

1. Login: https://dcc.godaddy.com/manage/
2. Click domain ? "Manage DNS"
3. Add CNAME record:
   ```
   Type: CNAME
   Name: app
   Value: Evident-legal-tech.onrender.com
   TTL: 1 Hour
   ```
4. Save

?? **Full guide:** `CUSTOM-DOMAIN-GODADDY.md`

--

### **Namecheap:**

1. Login: https://www.namecheap.com/myaccount/login/
2. Domain List ? Manage ? Advanced DNS
3. Add CNAME:
   ```
   Type: CNAME Record
   Host: app
   Value: Evident-legal-tech.onrender.com
   TTL: Automatic
   ```
4. Save All Changes

?? **Full guide:** `CUSTOM-DOMAIN-NAMECHEAP.md`

--

### **Cloudflare:**

1. Login: https://dash.cloudflare.com/
2. Select domain ? DNS
3. Add CNAME:
   ```
   Type: CNAME
   Name: app
   Target: Evident-legal-tech.onrender.com
   Proxy: DNS only (gray cloud) ? IMPORTANT!
   TTL: Auto
   ```
4. Save

?? **Must use gray cloud initially for SSL!**

?? **Full guide:** `CUSTOM-DOMAIN-CLOUDFLARE.md`

--

### **Other Registrars:**

**General DNS Setup:**

Add a CNAME record with these values:

```
Type: CNAME
Name/Host: app
Value/Target: Evident-legal-tech.onrender.com
TTL: 3600 (or Auto)
```

--

## ? **Verification Checklist:**

### **1. DNS Records Added?**

Check with: https://dnschecker.org

- Enter: `app.Evident.info`
- Should show: `Evident-legal-tech.onrender.com`

### **2. Render Domain Verified?**

In Render dashboard ? Custom Domains:

- Status should be: **"Verified"** ?

### **3. SSL Certificate Active?**

Look for ?? icon in Render dashboard

- Usually takes 5-15 minutes after verification

### **4. CORS Updated?**

Environment variables should include your custom domain

### **5. Test the Site:**

```
https://app.Evident.info
```

Should load your Evident app!

--

## ?? **Recommended Domain Structure:**

```
Evident.info                    ? Main marketing site (GitHub Pages)
app.Evident.info                ? Flask application (Render) ? YOU ARE HERE
api.Evident.info                ? API endpoints (future)
docs.Evident.info               ? Documentation (future)
```

--

## ?? **SSL/HTTPS Certificate:**

**Render provides FREE SSL automatically!**

Once DNS is verified:

1. ? Render detects custom domain
2. ? Auto-requests Let's Encrypt certificate
3. ? Installs certificate (5-15 mins)
4. ? Force HTTPS redirect enabled
5. ? Auto-renews every 90 days

**No configuration needed - it's automatic!** ??

--

## ?? **Timeline:**

| Step                 | Time                          |
| -------------------- | ----------------------------- |
| Add domain in Render | 1 minute                      |
| Update DNS records   | 2 minutes                     |
| DNS propagation      | 5 mins - 2 hours              |
| Render verification  | Instant (once DNS propagates) |
| SSL provisioning     | 5-15 minutes                  |
| **Total**            | **15 mins - 3 hours**         |

--

## ?? **Troubleshooting:**

### **"Domain not verified" in Render**

- Check DNS with dnschecker.org
- Wait longer (DNS can take 2 hours)
- Verify CNAME points to correct Render URL

### **"SSL Certificate Pending"**

- Normal - takes 5-15 minutes
- Render uses Let's Encrypt
- Auto-completes once DNS is stable

### **"Too Many Redirects"**

- If using Cloudflare: Turn off orange cloud
- Check CORS_ORIGINS includes your domain
- Clear browser cache

### **"ERR_SSL_VERSION_OR_CIPHER_MISMATCH"**

- Wait for SSL to finish provisioning
- Use http:// temporarily to test (not recommended)
- Check Render logs for SSL errors

### **Site works on .onrender.com but not custom domain**

- CORS issue - update CORS_ORIGINS environment variable
- Check app.py has correct CORS configuration

--

## ?? **Support:**

- **Render Docs:** https://render.com/docs/custom-domains
- **DNS Checker:** https://dnschecker.org
- **SSL Checker:** https://www.sslshopper.com/ssl-checker.html

--

## ? **Once Live:**

Your Evident app will be accessible at:

**Main App:** https://app.Evident.info
**Login:** https://app.Evident.info/auth/login
**Dashboard:** https://app.Evident.info/auth/dashboard

**Credentials:**

- Email: admin@Evident.info
- Password: Evident2026!

--

## ?? **Next Steps After Domain is Live:**

1. ? Update GitHub Pages to link to app.Evident.info
2. ? Add app.Evident.info to your marketing site
3. ? Set up monitoring (UptimeRobot, Pingdom)
4. ? Configure email notifications for downtime
5. ? Consider upgrading Render plan for:
   - No cold starts (always-on)
   - More resources
   - Better performance

--

**Ready to set up? Tell me which domain registrar you use and I'll help you through it!** ??
