# Custom Domain Setup - GoDaddy

## If Your Domain is on GoDaddy:

### 1. Login to GoDaddy

https://dcc.godaddy.com/manage/

### 2. Find Your Domain

- Click on your domain `Evident.info`
- Click "DNS" or "Manage DNS"

### 3. Add CNAME Record for App Subdomain

Click "Add" and enter:

```
Type: CNAME
Name: app
Value: Evident-legal-tech.onrender.com
TTL: 1 Hour
```

Click "Save"

### 4. Verify in Render

Go back to Render dashboard:

- Settings ? Custom Domains
- You should see "Verifying..." ? "Verified" ?

### 5. SSL Certificate

Render auto-provisions SSL (5-15 minutes after verification)

Your app will be live at:
**https://app.Evident.info** ??

--

## Alternative: Root Domain

If you want `Evident.info` (no subdomain):

### Option A: Domain Forwarding (Easy)

In GoDaddy:

1. Go to Domain Settings
2. Set up forwarding: `Evident.info` ? `https://app.Evident.info`

### Option B: A Records (Advanced)

Add these A records:

```
Type: A
Name: @
Value: 216.24.57.1
TTL: 1 Hour
```

Get exact IP from Render dashboard ? Custom Domains section
