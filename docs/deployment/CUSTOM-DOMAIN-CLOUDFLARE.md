# Custom Domain Setup - Cloudflare

## If Your Domain is on Cloudflare:

### 1. Login to Cloudflare

https://dash.cloudflare.com/

### 2. Select Your Domain

Click on `Evident.info`

### 3. Go to DNS Settings

Click "DNS" in the left sidebar

### 4. Add CNAME Record

Click "Add record" and enter:

```
Type: CNAME
Name: app
Target: Evident-legal-tech.onrender.com
Proxy status: DNS only (gray cloud) ? IMPORTANT!
TTL: Auto
```

**?? IMPORTANT:** Click the orange cloud to turn it gray!

- Gray cloud = DNS only (required for Render SSL)
- Orange cloud = Proxied (breaks Render's SSL)

Click "Save"

### 5. Verify in Render

- Go to Render dashboard
- Settings ? Custom Domains
- Wait for "Verified" status ?

### 6. SSL Certificate

Render auto-provisions SSL (5-15 minutes)

Your app will be live at:
**https://app.Evident.info** ??

--

## Alternative: Root Domain

For `Evident.info` (no subdomain):

### Method 1: Page Rules Redirect

1. Go to "Rules" ? "Page Rules"
2. Create rule:
   - URL: `Evident.info/*`
   - Setting: Forwarding URL (301)
   - Destination: `https://app.Evident.info/$1`

### Method 2: CNAME Flattening (Cloudflare Only)

Cloudflare supports CNAME at root:

```
Type: CNAME
Name: @
Target: Evident-legal-tech.onrender.com
Proxy status: DNS only (gray cloud)
TTL: Auto
```

--

## Enable Cloudflare Proxy (After SSL Works)

Once Render SSL is active:

1. Go back to DNS settings
2. Click the gray cloud to turn it orange
3. This enables:
   - Cloudflare CDN
   - DDoS protection
   - Analytics
   - Rate limiting

--

## Troubleshooting:

**"Too many redirects" error?**

- Turn off orange cloud (use gray "DNS only")

**SSL not working?**

- Ensure gray cloud is enabled during initial setup
- Wait for Render to provision SSL first
- Then you can enable orange cloud

**DNS not updating?**

- Purge Cloudflare cache: Caching ? Purge Everything
