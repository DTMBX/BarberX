# Deployment Guide

Complete guide for deploying the Geneva Bible Study Platform to various hosting services.

## 📋 Table of Contents

- [GitHub Pages](#github-pages-recommended)
- [Vercel](#vercel)
- [Netlify](#netlify)
- [Firebase Hosting](#firebase-hosting)
- [AWS S3 + CloudFront](#aws-s3--cloudfront)
- [Self-Hosted](#self-hosted)
- [Docker Deployment](#docker-deployment)

---

## GitHub Pages (Recommended)

**Best for:** Free hosting, automatic deployments, GitHub integration

### Prerequisites
- GitHub repository with your code
- GitHub account with Pages enabled

### Automatic Deployment (GitHub Actions)

This repository includes a pre-configured GitHub Actions workflow.

**Step 1: Enable GitHub Pages**
1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Build and deployment":
   - Source: **GitHub Actions**
   - (Not "Deploy from a branch")

**Step 2: Configure Base Path (if using project pages)**

If deploying to `username.github.io/repository-name`, update `vite.config.ts`:

```typescript
export default defineConfig({
  base: '/repository-name/', // Add this line
  plugins: [
    // ... existing plugins
  ],
})
```

**Step 3: Push to Main Branch**

```bash
git add .
git commit -m "Configure for GitHub Pages"
git push origin main
```

**Step 4: Monitor Deployment**
- Go to **Actions** tab in your repository
- Watch the "Deploy to GitHub Pages" workflow
- Once complete, visit: `https://username.github.io/repository-name/`

### Manual Deployment

If you prefer manual control:

```bash
# Build the project
npm run build

# Install gh-pages package
npm install -D gh-pages

# Add deploy script to package.json
# "deploy": "gh-pages -d dist"

# Deploy
npm run deploy
```

---

## Vercel

**Best for:** Instant deployments, automatic HTTPS, global CDN

### Via Vercel CLI

**Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

**Step 2: Login**
```bash
vercel login
```

**Step 3: Deploy**
```bash
# For preview deployment
vercel

# For production deployment
vercel --prod
```

### Via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click **Add New Project**
3. Import your Git repository
4. Configure:
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Click **Deploy**

**Environment Variables:** None required for this application

---

## Netlify

**Best for:** Drag-and-drop deployment, form handling, serverless functions

### Via Netlify CLI

**Step 1: Install Netlify CLI**
```bash
npm install -g netlify-cli
```

**Step 2: Login**
```bash
netlify login
```

**Step 3: Deploy**
```bash
# Build first
npm run build

# Deploy to preview
netlify deploy

# Deploy to production
netlify deploy --prod
```

### Via Netlify Dashboard

1. Go to [netlify.com](https://netlify.com)
2. Click **Add new site** → **Import an existing project**
3. Connect your Git repository
4. Configure:
   - Build command: `npm run build`
   - Publish directory: `dist`
5. Click **Deploy**

### Drag-and-Drop Deployment

1. Build locally: `npm run build`
2. Go to [netlify.com/drop](https://app.netlify.com/drop)
3. Drag the `dist` folder to the upload area

---

## Firebase Hosting

**Best for:** Google Cloud integration, Firebase services, global CDN

### Step 1: Install Firebase CLI

```bash
npm install -g firebase-tools
```

### Step 2: Login

```bash
firebase login
```

### Step 3: Initialize Firebase

```bash
firebase init hosting
```

Configure:
- Public directory: `dist`
- Single-page app: **Yes**
- Automatic builds with GitHub: **Optional**

### Step 4: Create `firebase.json`

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

### Step 5: Deploy

```bash
# Build
npm run build

# Deploy
firebase deploy --only hosting
```

---

## AWS S3 + CloudFront

**Best for:** AWS ecosystem, custom domains, fine-grained control

### Step 1: Create S3 Bucket

```bash
aws s3 mb s3://your-bucket-name
```

### Step 2: Configure Bucket for Static Hosting

```bash
aws s3 website s3://your-bucket-name \
  --index-document index.html \
  --error-document index.html
```

### Step 3: Set Bucket Policy

Create `bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy \
  --bucket your-bucket-name \
  --policy file://bucket-policy.json
```

### Step 4: Build and Upload

```bash
# Build
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name --delete
```

### Step 5: Create CloudFront Distribution (Optional)

1. Go to AWS CloudFront Console
2. Create distribution
3. Origin: Your S3 bucket
4. Default Root Object: `index.html`
5. Create distribution

---

## Self-Hosted

**Best for:** Full control, existing infrastructure, on-premise deployment

### Using Node.js + Express

Create `server.js`:

```javascript
import express from 'express'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const PORT = process.env.PORT || 3000

// Serve static files
app.use(express.static(path.join(__dirname, 'dist')))

// Handle SPA routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'))
})

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})
```

Deploy:
```bash
npm run build
node server.js
```

### Using Nginx

Create `/etc/nginx/sites-available/bible-study`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/bible-study/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/bible-study /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Apache

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

---

## Docker Deployment

**Best for:** Containerized environments, Kubernetes, cloud-native deployment

### Create `Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Create `nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Build and Run

```bash
# Build image
docker build -t bible-study-app .

# Run container
docker run -d -p 80:80 bible-study-app
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "80:80"
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

---

## 🔧 Configuration Checklist

Before deploying, ensure:

- [ ] Build command works: `npm run build`
- [ ] Environment variables configured (if any)
- [ ] Base path set correctly (for subdirectory hosting)
- [ ] CORS configured (if using separate API)
- [ ] HTTPS enabled on production
- [ ] Custom domain configured (optional)
- [ ] Analytics integrated (optional)
- [ ] Error tracking setup (optional)

## 🚀 Post-Deployment

After deploying:

1. **Test functionality:**
   - Bible reader works
   - Search functions
   - Audio playback
   - Social features
   - Dark mode

2. **Performance:**
   - Run Lighthouse audit
   - Check load times
   - Verify caching

3. **SEO:**
   - Submit sitemap
   - Verify meta tags
   - Check Open Graph tags

4. **Monitoring:**
   - Setup uptime monitoring
   - Configure error tracking
   - Enable analytics

---

## 📞 Support

For deployment issues:
- Check hosting provider documentation
- Review build logs for errors
- Verify node and npm versions match requirements
- Test build locally first: `npm run build && npm run preview`

---

**Last Updated:** January 2025
