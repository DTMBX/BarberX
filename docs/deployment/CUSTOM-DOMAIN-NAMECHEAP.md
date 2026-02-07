# Custom Domain Setup - Namecheap

## If Your Domain is on Namecheap:

### 1. Login to Namecheap

https://www.namecheap.com/myaccount/login/

### 2. Navigate to Domain List

- Click "Domain List" in left sidebar
- Find `Evident.info`
- Click "Manage"

### 3. Go to Advanced DNS

Click "Advanced DNS" tab

### 4. Add CNAME Record

Click "Add New Record" and enter:

```
Type: CNAME Record
Host: app
Value: Evident-legal-tech.onrender.com
TTL: Automatic
```

Click "Save All Changes" (green checkmark)

### 5. Verify in Render

- Go to Render dashboard
- Settings ? Custom Domains
- Status should change from "Verifying..." to "Verified" ?

### 6. SSL Certificate

Render automatically provisions free SSL certificate (5-15 min)

Your app will be live at: **https://app.Evident.info** ??

--

## Alternative: Root Domain Setup

For `Evident.info` (no subdomain):

### Option 1: URL Redirect (Easiest)

In Namecheap Advanced DNS:

```
Type: URL Redirect Record
Host: @
Value: https://app.Evident.info
Unmasked
```

### Option 2: A Records (Advanced)

Get Render's IP address from dashboard, then add:

```
Type: A Record
Host: @
Value: [Render IP from dashboard]
TTL: Automatic
```

--

## Troubleshooting:

**DNS not propagating?**

- Clear Namecheap cache: Advanced DNS ? Reset to Default
- Check: https://dnschecker.org

**Still showing Namecheap parking page?**

- Wait 15-30 minutes for propagation
- Clear browser cache (Ctrl+Shift+Delete)
