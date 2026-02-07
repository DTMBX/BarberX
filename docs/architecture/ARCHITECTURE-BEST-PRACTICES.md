# Evident Legal Suite - Production Architecture & Deployment Strategy

**Industry Best Practices for High-Volume Legal Tech Platform**  
**Date:** January 26, 2026

--

## 🎯 TL;DR - What Goes Where

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR PRODUCTION ARCHITECTURE (Recommended)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GITHUB                    RENDER (or AWS)        CDN        │
│  ═══════                   ═══════════════        ═══        │
│  ✓ Source code             ✓ Flask app            ✓ Static   │
│  ✓ Version control         ✓ API endpoints          assets   │
│  ✓ Documentation           ✓ Database (PG)       ✓ Images    │
│  ✓ CI/CD triggers          ✓ File processing     ✓ CSS/JS    │
│                            ✓ User sessions                    │
│  NO:                       ✓ Background jobs                  │
│  ✗ Hosting                                                    │
│  ✗ Running code            NO:                    NO:         │
│  ✗ User data               ✗ Source code          ✗ User data │
│  ✗ Databases               ✗ Git history          ✗ Videos    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

--

## 📚 FUNDAMENTAL CONCEPT: Separation of Concerns

### GitHub = Library (Code Storage)

- **Purpose:** Store and version control source code
- **Analogy:** Like a library that holds the recipe book
- **NOT for:** Running the restaurant, serving customers

### Render/AWS = Restaurant Kitchen (Application Server)

- **Purpose:** Run your code, serve users, process requests
- **Analogy:** The kitchen that cooks the food using the recipes
- **NOT for:** Storing the recipe book long-term

### CDN = Fast Food Window (Content Delivery)

- **Purpose:** Serve static files fast (images, CSS, JS)
- **Analogy:** Express window for quick pickup
- **NOT for:** Complex operations or dynamic content

--

## ✅ CORRECT ARCHITECTURE (Industry Standard)

### Tier 1: Code Repository (GitHub)

```yaml
What Lives Here: ✓ Source code (.py, .js, .html files) ✓ Configuration files (render.yaml,
  requirements.txt) ✓ Documentation (.md files) ✓ Version history (git commits)

What NEVER Lives Here: ✗ User-uploaded files (PDFs, videos, images) ✗ Database data (user accounts,
  analysis results) ✗ Generated reports ✗ Cache data ✗ Environment secrets (API
  keys)

Access: Public or Private repository
Cost: FREE for public, $4/month for private
Storage Limit: 1-100 GB (not for large files!)
```

### Tier 2: Application Server (Render/AWS/Azure)

```yaml
What Lives Here: ✓ Running Flask application ✓ Python environment & dependencies ✓ Active user
  sessions ✓ Temporary processing files ✓ Application logs

What NEVER Lives Here: ✗ Git repository (.git folder - too large) ✗ Long-term file storage (use
  S3/Azure Blob) ✗ Large video files (use cloud storage)

Access: HTTP/HTTPS endpoints
Cost: $7-25/month (Render), $20-200/month (AWS)
Storage Limit: 10-50 GB ephemeral (resets on deploy!)
```

### Tier 3: Database (PostgreSQL on Render/AWS)

```yaml
What Lives Here: ✓ User accounts & profiles ✓ Analysis metadata ✓ Case information ✓
  Subscription data ✓ Audit logs

What NEVER Lives Here: ✗ Large files (videos, PDFs) - use file paths to S3 ✗ Source code ✗
  Application logic

Access: Private connection string
Cost: $7/month (Render), $15-100/month (AWS RDS)
Storage Limit: 1 GB - 1 TB+ (scalable)
```

### Tier 4: Object Storage (AWS S3 / Azure Blob)

```yaml
What Lives Here: ✓ User-uploaded PDFs ✓ BWC video files ✓ Generated reports ✓ Evidence images ✓
  Audio transcriptions

Why Separate Storage: ✓ Unlimited scalability ✓ 99.99% durability ✓ CDN integration ✓ Automatic
  backups ✓ Cost-effective ($0.023/GB/month)

Access: Pre-signed URLs or CDN
Cost: ~$2-50/month for 100-1000 GB
```

### Tier 5: CDN (Cloudflare / AWS CloudFront)

```yaml
What Lives Here: ✓ CSS stylesheets ✓ JavaScript files ✓ Logo images ✓ Fonts ✓ Icons

Why CDN: ✓ 10-100x faster load times ✓ Reduced server bandwidth ✓ Global edge locations
  ✓ DDoS protection

Access: Public HTTPS URLs
Cost: FREE (Cloudflare) or $1-20/month
```

--

## 🏗️ Evident OPTIMAL ARCHITECTURE

### Current Setup (NOT OPTIMAL)

```
❌ CURRENT - Everything on Render:
┌────────────────────────────┐
│  Render Free Tier          │
│  ─────────────────          │
│  • Flask App               │
│  • PostgreSQL (1GB)        │
│  • Uploaded files          │ ← PROBLEM: Limited storage
│  • Generated reports       │ ← PROBLEM: Lost on redeploy
│  • Static assets           │ ← PROBLEM: Slow delivery
│                            │
│  Issues:                   │
│  ⚠️  10GB storage limit    │
│  ⚠️  Files lost on deploy  │
│  ⚠️  Slow file delivery    │
│  ⚠️  Not scalable          │
└────────────────────────────┘
```

### Recommended Setup (OPTIMAL)

```
✅ RECOMMENDED - Distributed Architecture:

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  GitHub      │───▶│  Render      │───▶│  AWS S3      │
│  (Code)      │    │  (App+DB)    │    │  (Files)     │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ Source code  │    │ Flask app    │    │ Videos       │
│ Config files │    │ PostgreSQL   │    │ PDFs         │
│ Docs         │    │ API server   │    │ Reports      │
│              │    │ Processing   │    │ Evidence     │
└──────────────┘    └──────────────┘    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │  Cloudflare  │
                    │  (CDN)       │
                    ├──────────────┤
                    │ CSS/JS       │
                    │ Images       │
                    │ Fonts        │
                    └──────────────┘
```

--

## 💰 COST COMPARISON

### Option A: All-in-One (Current)

```
Render Pro (for 100GB storage): $85/month
  ├─ App Server: $25
  ├─ Database: $20
  └─ Extra Storage: $40

TOTAL: $85/month
Scalability: Limited to Render's offerings
Performance: Moderate (no CDN)
```

### Option B: Distributed (Recommended)

```
GitHub:        FREE (public) or $4/month (private)
Render:        $25/month (app) + $7/month (database)
AWS S3:        $2-10/month (100-1000 GB files)
Cloudflare:    FREE (CDN)

TOTAL: $34-46/month
Scalability: Infinite (each service scales independently)
Performance: Excellent (CDN + optimized storage)

SAVINGS: $39-51/month (46-60% cheaper!)
```

### Option C: Full AWS (Enterprise)

```
AWS EC2:       $50/month (t3.medium instance)
AWS RDS:       $50/month (PostgreSQL)
AWS S3:        $5-20/month (storage)
AWS CloudFront: $5/month (CDN)

TOTAL: $110-125/month
Scalability: Maximum control and performance
Performance: Best (dedicated resources)
Best For: 10,000+ users, high traffic
```

--

## 🚀 DEPLOYMENT WORKFLOW (Best Practice)

### Development → Production Pipeline

```bash
┌──────────────────────────────────────────────────────────┐
│  STEP 1: LOCAL DEVELOPMENT                               │
├──────────────────────────────────────────────────────────┤
│  Your Computer:                                          │
│  $ git clone https://github.com/user/Evident.info      │
│  $ python app.py                                         │
│  $ # Make changes, test locally                          │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 2: VERSION CONTROL                                 │
├──────────────────────────────────────────────────────────┤
│  GitHub:                                                 │
│  $ git add .                                             │
│  $ git commit -m "Add new feature"                       │
│  $ git push origin main                                  │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 3: AUTOMATIC DEPLOYMENT (CI/CD)                    │
├──────────────────────────────────────────────────────────┤
│  Render Auto-Deploy:                                     │
│  1. Detects push to GitHub                              │
│  2. Pulls latest code                                    │
│  3. Runs build.sh (install dependencies)                │
│  4. Starts app with gunicorn                             │
│  5. Runs health checks                                   │
│  6. Switches traffic to new version                      │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 4: PRODUCTION RUNNING                              │
├──────────────────────────────────────────────────────────┤
│  Live App:                                               │
│  https://Evident-legal-tech.onrender.com                │
│  - Serves user requests                                  │
│  - Processes files                                       │
│  - Stores data in PostgreSQL                             │
│  - Uploads files to S3                                   │
└──────────────────────────────────────────────────────────┘
```

**KEY POINT:** GitHub stores code, Render runs code. They work together but
serve different purposes!

--

## 📊 WHAT GOES WHERE - Evident Specific

### GitHub Repository

```
Evident.info/
├── app.py                    ✓ YES - Application code
├── requirements.txt          ✓ YES - Dependencies list
├── render.yaml              ✓ YES - Deployment config
├── templates/               ✓ YES - HTML templates
├── static/                  ✓ YES - CSS, JS, small images
│   ├── css/
│   ├── js/
│   └── images/ (< 1MB each)
├── models/                  ✓ YES - Database models
├── routes/                  ✓ YES - API endpoints
├── utils/                   ✓ YES - Helper functions
└── docs/                    ✓ YES - Documentation

DO NOT PUT IN GITHUB:
├── uploads/                 ✗ NO - User uploaded files
├── bwc_videos/             ✗ NO - Large video files
├── reports/                 ✗ NO - Generated reports
├── .env                     ✗ NO - Environment secrets
└── instance/Evident.db     ✗ NO - Database file
```

### Render (Application Server)

```
/app/ (Render working directory)
├── app.py                   ✓ Copied from GitHub
├── requirements.txt         ✓ Copied from GitHub
├── templates/               ✓ Copied from GitHub
├── /tmp/uploads/           ✓ Temporary storage
│   └── processing/         ✓ Files being processed
├── logs/                    ✓ Application logs
└── .env                     ✓ Environment variables (set in Render dashboard)

EPHEMERAL (Lost on redeploy):
├── /tmp/                    ⚠️ Cleared periodically
└── uploads/                 ⚠️ Lost when container restarts

PERMANENT (Persists):
└── PostgreSQL Database      ✓ Managed by Render
```

### AWS S3 (File Storage)

```
Evident-files/ (S3 Bucket)
├── uploads/
│   ├── pdfs/
│   │   └── user123/
│   │       └── evidence_2026_01.pdf
│   ├── videos/
│   │   └── user123/
│   │       └── bwc_footage.mp4
│   └── images/
│       └── user123/
│           └── scene_001.jpg
├── reports/
│   └── user123/
│       ├── analysis_456.pdf
│       └── discovery_789.docx
└── transcripts/
    └── user123/
        └── audio_001.json

Benefits:
✓ Unlimited storage
✓ 99.999999999% durability (11 nines!)
✓ Automatic backups
✓ Versioning enabled
✓ Lifecycle policies (auto-delete old files)
```

### PostgreSQL Database (on Render)

```sql
- What's stored in database:
users (
  id, email, password_hash, tier, created_at
)
analyses (
  id, user_id, filename,
  file_path,  - S3 URL: s3://bucket/uploads/videos/file.mp4
  status, created_at
)
reports (
  id, analysis_id,
  report_path,  - S3 URL: s3://bucket/reports/report.pdf
  generated_at
)

- NOT in database:
✗ Actual video files
✗ Actual PDF files
✗ Report content (just path to S3)
```

--

## 🔧 IMPLEMENTATION GUIDE

### Phase 1: Current State (Keep Working)

```bash
# What you have now:
✓ GitHub: Source code
✓ Render: App + Database
✓ Local storage: Uploaded files (⚠️ not ideal)

# Works but NOT scalable
```

### Phase 2: Add S3 Integration (Recommended Next Step)

```bash
# 1. Create AWS account (free tier available)
aws configure

# 2. Create S3 bucket
aws s3 mb s3://Evident-legal-files

# 3. Install boto3 (AWS SDK)
pip install boto3

# 4. Update app.py to upload to S3
import boto3
s3 = boto3.client('s3')
s3.upload_file('local_file.pdf', 'evident-legal-files', 'uploads/file.pdf')

# 5. Store S3 path in database (not actual file)
analysis.file_path = 's3://Evident-legal-files/uploads/file.pdf'

# 6. Generate pre-signed URLs for downloads
url = s3.generate_presigned_url('get_object',
    Params={'Bucket': 'evident-legal-files', 'Key': 'uploads/file.pdf'},
    ExpiresIn=3600)  # URL valid for 1 hour
```

### Phase 3: Add CDN (Optional but Recommended)

```bash
# 1. Sign up for Cloudflare (FREE)
# 2. Add your domain (Evident.info)
# 3. Enable CDN for static assets
# 4. Update app.py to use CDN URLs

# Before:
<link rel="stylesheet" href="/static/css/style.css">

# After:
<link rel="stylesheet" href="https://cdn.Evident.info/css/style.css">
```

--

## 📈 SCALABILITY ROADMAP

### Stage 1: Startup (0-100 users)

```
GitHub (FREE) + Render Free Tier ($0)
├─ Code: GitHub
├─ App: Render (512MB RAM, shared CPU)
├─ DB: Render Free PostgreSQL (1GB)
└─ Files: Local storage on Render

Limitations:
⚠️ 512MB RAM (enough for basic usage)
⚠️ 1GB database (enough for 100-500 users)
⚠️ Sleeps after 15 min inactivity
⚠️ Limited file storage

Cost: $0/month
Perfect for: Testing, MVP, early users
```

### Stage 2: Growth (100-1,000 users)

```
GitHub ($0) + Render Starter ($25) + AWS S3 ($5)
├─ Code: GitHub
├─ App: Render (1GB RAM, 0.5 CPU)
├─ DB: Render Starter PostgreSQL (10GB)
└─ Files: AWS S3 (100GB)

Improvements:
✓ No sleep time
✓ 10x more database storage
✓ Unlimited file storage
✓ 99.9% uptime SLA

Cost: $30/month
Perfect for: Growing user base
```

### Stage 3: Scale (1,000-10,000 users)

```
GitHub ($0) + Render Pro ($85) + AWS S3 ($20) + Cloudflare ($0)
├─ Code: GitHub
├─ App: Render (4GB RAM, 2 CPU)
├─ DB: Render Pro PostgreSQL (100GB)
├─ Files: AWS S3 (1TB)
└─ CDN: Cloudflare

Improvements:
✓ 4x more resources
✓ Auto-scaling
✓ CDN for fast delivery
✓ 99.95% uptime SLA

Cost: $105/month
Perfect for: Established platform
```

### Stage 4: Enterprise (10,000+ users)

```
GitHub ($0) + AWS ($500-2000/month)
├─ Code: GitHub
├─ App: AWS ECS (container orchestration)
│   ├─ 2-10 EC2 instances
│   ├─ Load balancer
│   └─ Auto-scaling
├─ DB: AWS RDS PostgreSQL (Multi-AZ, 500GB+)
├─ Files: AWS S3 (10TB+)
├─ CDN: AWS CloudFront
├─ Cache: AWS ElastiCache (Redis)
└─ Search: AWS OpenSearch

Improvements:
✓ Full redundancy
✓ Unlimited scaling
✓ 99.99% uptime SLA
✓ Advanced analytics
✓ Real-time processing

Cost: $500-2,000/month
Perfect for: Major legal tech platform
```

--

## ✅ ACTION PLAN - Migrate to Best Practices

### Immediate (This Week)

1. **Keep current setup working**
   - ✓ GitHub for code
   - ✓ Render for app + database
   - ✓ Temporary file storage on Render

2. **Document architecture**
   - ✓ Create architecture diagram
   - ✓ Document data flow
   - ✓ Identify bottlenecks

### Short-term (Next 2 Weeks)

1. **Integrate AWS S3**

   ```bash
   # Add to requirements.txt:
   boto3==1.35.84

   # Create cloud_storage.py:
   class S3Storage:
       def upload(file, key):
           s3.upload_fileobj(file, 'evident-files', key)

       def download_url(key):
           return s3.generate_presigned_url('get_object', ...)
   ```

2. **Migrate existing files**
   - Upload PDFs to S3
   - Upload videos to S3
   - Update database paths

### Medium-term (Next Month)

1. **Add CDN (Cloudflare)**
   - Serve CSS/JS from CDN
   - Serve images from CDN
   - 10x faster load times

2. **Optimize database**
   - Add indexes (already done!)
   - Enable connection pooling (already done!)
   - Set up automated backups

### Long-term (3-6 Months)

1. **Consider AWS migration** (when you hit 1,000+ users)
2. **Add caching layer** (Redis)
3. **Implement background jobs** (Celery + RabbitMQ)
4. **Set up monitoring** (DataDog, New Relic)

--

## 📊 DECISION MATRIX

**When to use each platform:**

| Platform           | Best For                            | NOT For                                               |
| ------------------ | ----------------------------------- | ----------------------------------------------------- |
| **GitHub**         | Source code, version control, CI/CD | Running apps, storing files, databases                |
| **Render**         | Small-medium apps, simple deploys   | Large-scale apps (>10k users), complex infrastructure |
| **AWS/Azure**      | Enterprise apps, full control       | Small projects (overkill), quick MVPs                 |
| **Netlify/Vercel** | Static sites, JAMstack              | Backend APIs, databases, file processing              |
| **Heroku**         | Rapid prototyping                   | Cost-effective production (expensive)                 |

--

## 🎯 RECOMMENDED ARCHITECTURE FOR Evident

```
┌─────────────────────────────────────────────────────────┐
│  PRODUCTION ARCHITECTURE - Evident Legal Suite          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│  │ GitHub   │─────▶│ Render   │─────▶│ AWS S3   │     │
│  │ (Code)   │      │ (App+DB) │      │ (Files)  │     │
│  └──────────┘      └──────────┘      └──────────┘     │
│                          │                              │
│                          ▼                              │
│                    ┌──────────┐                         │
│                    │Cloudflare│                         │
│                    │  (CDN)   │                         │
│                    └──────────┘                         │
│                                                          │
│  Benefits:                                               │
│  ✓ Best price/performance ratio                        │
│  ✓ Scalable to 10,000+ users                           │
│  ✓ ~$40-100/month total cost                           │
│  ✓ Industry standard approach                          │
│  ✓ Easy to manage                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

--

## 💡 KEY TAKEAWAYS

1. **GitHub ≠ Hosting**
   - GitHub stores code (library)
   - Render runs code (kitchen)
   - They're partners, not competitors

2. **Separation is GOOD**
   - Each service does what it's best at
   - Easier to scale individual components
   - More reliable (one failure doesn't kill everything)

3. **File Storage = Biggest Cost**
   - Videos/PDFs are 95% of storage needs
   - Store these in S3, not on app server
   - Saves $$$, improves performance

4. **Current Setup is OK for Now**
   - Works for development and early users
   - Not ideal for 1,000+ users
   - Easy to migrate later

5. **Migrate Gradually**
   - Don't rebuild everything at once
   - Add S3 first (biggest impact)
   - Add CDN second (speed boost)
   - Consider AWS much later (if needed)

--

**BOTTOM LINE:**  
Your current setup (GitHub + Render) is correct and industry-standard. Just add
AWS S3 for file storage when you're ready to scale. Don't overthink it!

--

_Last Updated: January 26, 2026_  
_Architecture: Production-Ready_  
_Scalability: Designed for 10,000+ users_
