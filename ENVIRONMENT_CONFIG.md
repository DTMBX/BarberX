# Environment Configuration Guide

This document explains how to configure the application for different deployment environments.

## 📋 Overview

The Geneva Bible Study Platform is a client-side application that requires minimal configuration. Most settings are handled automatically, but you may need to adjust for specific deployment scenarios.

## 🔧 Required Configuration

### GitHub Pages Deployment

If deploying to GitHub Pages as a **project site** (not user/org site), you need to configure the base path.

#### Project Pages (username.github.io/repo-name)

**Edit `vite.config.ts`:**

```typescript
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig, PluginOption } from "vite";
import sparkPlugin from "@github/spark/spark-vite-plugin";
import createIconImportProxy from "@github/spark/vitePhosphorIconProxyPlugin";
import { resolve } from 'path'

const projectRoot = process.env.PROJECT_ROOT || import.meta.dirname

export default defineConfig({
  base: '/repo-name/',  // Add this line - replace 'repo-name' with your repository name
  plugins: [
    react(),
    tailwindcss(),
    createIconImportProxy() as PluginOption,
    sparkPlugin() as PluginOption,
  ],
  resolve: {
    alias: {
      '@': resolve(projectRoot, 'src')
    }
  },
});
```

**Replace `repo-name` with your actual repository name.**

#### User/Org Pages (username.github.io)

No configuration needed. The default base path `/` works.

**Keep `vite.config.ts` as is (no base property).**

### Other Hosting Platforms

Most platforms work with default configuration:

- **Vercel:** No configuration needed
- **Netlify:** No configuration needed
- **Firebase:** Configured via `firebase.json`
- **AWS S3:** No configuration needed
- **Self-hosted:** Depends on web server setup

## 🌍 Environment Variables

This application **does not require environment variables** for normal operation.

### Optional Environment Variables

You can use environment variables for customization:

#### Development

Create `.env.local` (not tracked by git):

```bash
# Development server port (optional)
VITE_PORT=5173

# Enable verbose logging (optional)
VITE_DEBUG=true
```

#### Production

For production builds, you can set:

```bash
# Build mode
NODE_ENV=production

# Public URL (for advanced routing scenarios)
PUBLIC_URL=https://yourdomain.com
```

**Note:** Most deployments don't need these variables.

## 📝 Configuration Files

### package.json

Update metadata for your deployment:

```json
{
  "name": "geneva-bible-study",
  "version": "1.0.0",
  "description": "Your description",
  "author": "Your Name",
  "repository": {
    "type": "git",
    "url": "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
  },
  "homepage": "https://YOUR_USERNAME.github.io/YOUR_REPO/"
}
```

### index.html

Update the page title:

```html
<title>Geneva Bible Study</title>
```

Add analytics or other meta tags as needed:

```html
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="Your app description" />
  <meta name="keywords" content="bible, study, scripture" />
  <title>Geneva Bible Study</title>
  
  <!-- Optional: Add favicon -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  
  <!-- Fonts (already included) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;500;600;700&family=JetBrains+Mono:wght@400&family=Literata:opsz,wght@7..72,400;7..72,500&display=swap" rel="stylesheet">
  
  <link href="/src/main.css" rel="stylesheet" />
</head>
```

### vite.config.ts

Full configuration reference:

```typescript
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig, PluginOption } from "vite";
import sparkPlugin from "@github/spark/spark-vite-plugin";
import createIconImportProxy from "@github/spark/vitePhosphorIconProxyPlugin";
import { resolve } from 'path'

const projectRoot = process.env.PROJECT_ROOT || import.meta.dirname

export default defineConfig({
  // Base path for GitHub Pages project sites
  // base: '/repo-name/',  // Uncomment and update for project pages
  
  plugins: [
    react(),
    tailwindcss(),
    createIconImportProxy() as PluginOption,
    sparkPlugin() as PluginOption,
  ],
  
  resolve: {
    alias: {
      '@': resolve(projectRoot, 'src')
    }
  },
  
  // Optional: Customize dev server
  // server: {
  //   port: 3000,
  //   open: true,
  // },
  
  // Optional: Customize build output
  // build: {
  //   outDir: 'dist',
  //   sourcemap: false,
  // },
});
```

## 🚀 Deployment-Specific Configuration

### Vercel

Create `vercel.json` (optional):

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Netlify

Create `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Firebase

Create `firebase.json`:

```json
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

### Nginx

Create nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    root /var/www/bible-study/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Apache

Create `.htaccess` in `dist/`:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

## 🔒 Security Headers

Add security headers at your hosting provider:

### Recommended Headers

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://bolls.life;
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(self), microphone=(self)
```

### Platform-Specific Implementation

**Netlify (`netlify.toml`):**
```toml
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = "default-src 'self'; ..."
    X-Frame-Options = "SAMEORIGIN"
```

**Vercel (`vercel.json`):**
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; ..."
        }
      ]
    }
  ]
}
```

## 🧪 Testing Configuration

### Test Locally

```bash
# Build for production
npm run build

# Preview build
npm run preview

# Open http://localhost:4173
```

### Test Deployed Version

1. Deploy to staging/preview environment first
2. Test all features:
   - Bible reader loads
   - Search works
   - Audio plays
   - Social features function
   - Dark mode toggles
3. Check browser console for errors
4. Test on mobile and desktop

## ❓ Troubleshooting

### 404 on Refresh

**Problem:** Page refreshes result in 404 errors.

**Solution:** Configure server to redirect all requests to `index.html` (see platform-specific configs above).

### Assets Not Loading

**Problem:** CSS/JS files return 404.

**Solution:** Check `base` path in `vite.config.ts` matches your deployment URL structure.

### API Requests Blocked

**Problem:** Bible API requests fail.

**Solution:** Check CSP headers allow `connect-src https://bolls.life`.

### Dark Mode Not Persisting

**Problem:** Dark mode resets on page reload.

**Solution:** Ensure browser allows localStorage/IndexedDB (KV storage).

## 📞 Support

For configuration help:
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for platform-specific guides
- Review [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup
- Open an issue on GitHub

---

**Last Updated:** January 2025
