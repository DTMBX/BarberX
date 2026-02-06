# 🚀 Scalable Production Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  NETLIFY (Frontend - LIVE)                              │
│  https://Evident.info                                   │
│  • Static Jekyll site                                   │
│  • Forms collection                                     │
│  • Global CDN                                           │
│  • Auto-scaling                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ API Calls
                 ↓
┌─────────────────────────────────────────────────────────┐
│  RENDER/RAILWAY (Backend API)                           │
│  https://api.Evident.info                               │
│  • Flask REST API                                       │
│  • PostgreSQL database                                  │
│  • File processing                                      │
│  • Auto-scaling                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Storage
                 ↓
┌─────────────────────────────────────────────────────────┐
│  AWS S3 (File Storage - Future)                         │
│  • PDF documents                                        │
│  • BWC videos                                           │
│  • Analysis reports                                     │
│  • Unlimited scaling                                    │
└─────────────────────────────────────────────────────────┘
```

--

## Option 1: Deploy to Render (Recommended)

**Why Render:**

- ✅ Free tier available
- ✅ Auto-scaling
- ✅ PostgreSQL included
- ✅ Zero-config deployments
- ✅ SSL certificates automatic
- ✅ GitHub auto-deploy

### Step 1: Push to GitHub (Already Done ✅)

```powershell
git add .
git commit -m "Production-ready scalable deployment"
git push origin main
```

### Step 2: Deploy on Render

1. **Go to:** https://render.com
2. **Sign up** with GitHub account
3. **New** → **Blueprint**
4. **Connect repository:** `DTB396/Evident.info`
5. **Render will auto-detect** `render.yaml`
6. **Click:** "Apply"

**Render creates:**

- Web service (Flask API)
- PostgreSQL database
- Auto environment variables
- SSL certificate
- Custom domain support

### Step 3: Configure Environment Variables

In Render dashboard, add:

```bash
SECRET_KEY=<generate-strong-key>
FLASK_ENV=production
CORS_ORIGINS=https://Evident.info,https://www.Evident.info
ADMIN_EMAIL=admin@Evident.info
ADMIN_PASSWORD=<secure-password>
```

### Step 4: Get Your API URL

```
https://Evident-api.onrender.com
```

Custom domain:

```
https://api.Evident.info
```

--

## Option 2: Deploy to Railway (Fastest)

**Why Railway:**

- ✅ $5 free credit monthly
- ✅ Instant deploys
- ✅ PostgreSQL with 1 click
- ✅ Auto-scaling
- ✅ Excellent DX

### Quick Deploy:

```powershell
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to GitHub repo
railway link

# Add PostgreSQL
railway add

# Deploy
railway up

# Get URL
railway open
```

**Your API will be live in ~2 minutes!**

--

## Option 3: Deploy to Fly.io (Most Control)

**Why Fly.io:**

- ✅ Deploy to multiple regions
- ✅ Auto-scaling
- ✅ PostgreSQL clusters
- ✅ Custom routing
- ✅ Advanced features

### Deploy:

```powershell
# Install flyctl
iwr https://fly.io/install.ps1 -useb | iex

# Login
fly auth login

# Launch app
fly launch

# Deploy
fly deploy
```

--

## Database Migration (Local to Production)

### Option A: Manual Migration

```powershell
# Export local data
python -c "
from app import app, db, User, Analysis, PDFUpload
import json

with app.app_context():
    users = [u.to_dict() for u in User.query.all()]
    with open('users_backup.json', 'w') as f:
        json.dump(users, f)
"

# Import to production (after deployment)
# Set DATABASE_URL to production
# Run migration script
```

### Option B: Use Production Database from Start

Just let Render/Railway create the database fresh.
Run `create_admin.py` on production.

--

## File Storage Strategy (Scale-Ready)

### Current: Local Storage

```python
UPLOAD_FOLDER = './uploads/pdfs'
```

### Future: AWS S3 (Unlimited Scale)

**Install:**

```powershell
pip install boto3
```

**Configure:**

```python
import boto3
from botocore.config import Config

s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-west-2')
)

# Upload to S3
s3_client.upload_fileobj(
    file,
    os.getenv('AWS_S3_BUCKET'),
    f'pdfs/{filename}'
)
```

**Benefits:**

- Unlimited storage
- Global CDN
- $0.023/GB
- Auto-backups

--

## Scaling Roadmap

### Phase 1: MVP (Now) - FREE

- ✅ Netlify frontend (free)
- ✅ Render backend (free tier)
- ✅ PostgreSQL (free tier)
- ✅ Local file storage
- **Capacity:** ~100 users, 10GB storage

### Phase 2: Growth ($50/month)

- ✅ Render Pro ($25/month)
- ✅ PostgreSQL Pro ($25/month)
- ✅ S3 storage (~$5/month for 200GB)
- **Capacity:** ~10,000 users, unlimited storage

### Phase 3: Scale ($500/month)

- ✅ Multiple regions
- ✅ Redis caching
- ✅ CDN for files
- ✅ Background job workers
- **Capacity:** ~1M users, petabyte storage

### Phase 4: Enterprise ($5,000+/month)

- ✅ Kubernetes clusters
- ✅ Multi-region database
- ✅ Dedicated support
- ✅ SLA (see terms)
- **Capacity:** Unlimited

--

## Performance Optimizations

### 1. Database Indexing

```python
# Already in models
class User(db.Model):
    email = db.Column(db.String(120), unique=True, index=True)  # ✅
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # ✅

class PDFUpload(db.Model):
    file_hash = db.Column(db.String(64), unique=True, index=True)  # ✅
    case_number = db.Column(db.String(100), index=True)  # ✅
```

### 2. Caching (Future)

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL')
})

@app.route('/api/cases/<case_id>')
@cache.cached(timeout=300)  # 5 min cache
def get_case(case_id):
    # Expensive database query
    pass
```

### 3. Background Jobs (Celery)

```python
# For long-running BWC analysis
from celery import Celery

celery = Celery('Evident', broker=os.getenv('REDIS_URL'))

@celery.task
def analyze_bwc_video(video_path):
    # Run analysis in background
    pass
```

### 4. CDN for Static Files

```nginx
# In Netlify, automatically handled
# For API responses, use CloudFlare
```

--

## Monitoring & Analytics

### 1. Sentry (Error Tracking)

```powershell
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### 2. Logging (Production)

```python
import logging
from logging.handlers import RotatingFileHandler

if os.getenv('FLASK_ENV') == 'production':
    handler = RotatingFileHandler('logs/production.log', maxBytes=10000000, backupCount=10)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
```

### 3. Metrics (Prometheus)

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Automatic metrics:
# - Request count
# - Request duration
# - HTTP status codes
```

--

## Security Hardening

### 1. Rate Limiting

```powershell
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/upload/pdf')
@limiter.limit("10 per hour")
def upload_pdf():
    pass
```

### 2. HTTPS Only

```python
from flask_talisman import Talisman

if os.getenv('FLASK_ENV') == 'production':
    Talisman(app, force_https=True)
```

### 3. API Authentication

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not APIKey.verify(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/upload/pdf')
@require_api_key
def upload_pdf():
    pass
```

--

## Cost Estimates

### Startup Phase (0-1K users)

- Netlify: **FREE**
- Render Free Tier: **FREE**
- PostgreSQL Free: **FREE**
- **Total: $0/month**

### Growth Phase (1K-100K users)

- Netlify Pro: **FREE** (generous limits)
- Render Starter: **$25/month**
- PostgreSQL: **$25/month**
- S3 Storage (500GB): **$12/month**
- **Total: ~$60/month**

### Scale Phase (100K+ users)

- Netlify Enterprise: **$500/month**
- Render Team: **$250/month**
- PostgreSQL Pro: **$200/month**
- S3 + CloudFront: **$500/month**
- Redis: **$50/month**
- **Total: ~$1,500/month**

--

## Next Steps - Deploy NOW

### Fastest Path (5 minutes):

1. **Railway:**

   ```powershell
   npm i -g @railway/cli
   railway login
   railway init
   railway up
   ```

2. **Get URL:**

   ```
   https://your-app.railway.app
   ```

3. **Update Netlify:**

   ```javascript
   // In your frontend forms
   fetch("https://your-app.railway.app/api/upload/pdf", {
     method: "POST",
     body: formData,
   });
   ```

4. **Done!** ✅

--

## Long-Term Architecture (Next 6 Months)

```
Production Stack:
├── Frontend: Netlify (Static + Forms)
├── API: Render/Railway (Flask + PostgreSQL)
├── Storage: AWS S3 (Files)
├── Cache: Redis (Performance)
├── Queue: Celery (Background jobs)
├── Monitor: Sentry (Errors)
├── Analytics: Google Analytics
└── Payments: Stripe
```

**Ready to scale to millions of users.** 🚀
