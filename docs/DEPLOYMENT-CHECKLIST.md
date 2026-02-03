# Production Deployment Checklist

**Last Updated:** January 27, 2026  
**Target Deploy Date:** TBD  
**Environment:** Production (Render.com)

---

## 📋 Pre-Deployment Checklist

### Code Quality

- [ ] **All tests passing**

  ```powershell
  pytest
  # Expected: All tests pass
  ```

- [ ] **Security audit clean**

  ```powershell
  python security_audit.py
  # Expected: 0 vulnerabilities
  ```

- [ ] **Mobile validation passing**

  ```powershell
  python validate_mobile.py
  # Expected: All checks pass
  ```

- [ ] **No linting errors**

  ```powershell
  npx prettier --check .
  npx stylelint "**/*.css"
  npx htmlhint "**/*.html"
  ```

- [ ] **Git status clean**
  ```powershell
  git status
  # Expected: working tree clean or only documented changes
  ```

---

### Environment Configuration

#### Required Environment Variables

- [ ] **Flask Core**
  - [ ] `SECRET_KEY` - Secure random key (generate new for production)
  - [ ] `FLASK_ENV=production`
  - [ ] `FORCE_HTTPS=true` (enables HSTS)
  - [ ] `DEBUG=false`

- [ ] **Database**
  - [ ] `DATABASE_URL` - PostgreSQL connection string
  - [ ] Database initialized with schema
  - [ ] Migrations applied

- [ ] **Stripe Payment Processing**
  - [ ] `STRIPE_SECRET_KEY` - Live key (sk*live*...)
  - [ ] `STRIPE_PUBLISHABLE_KEY` - Live key (pk*live*...)
  - [ ] `STRIPE_WEBHOOK_SECRET` - Webhook signing secret
  - [ ] `STRIPE_PRICE_PRO` - Professional tier price ID
  - [ ] `STRIPE_PRICE_PREMIUM` - Premium tier price ID
  - [ ] `STRIPE_PRICE_ENTERPRISE` - Enterprise tier price ID

- [ ] **Analytics**
  - [ ] `AMPLITUDE_API_KEY` - Production API key

- [ ] **Email (Optional)**
  - [ ] `SENDGRID_API_KEY` - For transactional emails
  - [ ] `SMTP_HOST` - If using SMTP
  - [ ] `SMTP_PORT`
  - [ ] `SMTP_USER`
  - [ ] `SMTP_PASSWORD`

- [ ] **External Services**
  - [ ] `OPENAI_API_KEY` - For AI features
  - [ ] `S3_BUCKET` - If using AWS S3 for uploads
  - [ ] `S3_ACCESS_KEY`
  - [ ] `S3_SECRET_KEY`

---

### Database

- [ ] **Production database created**
  - Provider: PostgreSQL (Render, AWS RDS, or other)
  - Connection tested successfully
  - SSL enabled

- [ ] **Schema initialized**

  ```python
  from app import app, db
  with app.app_context():
      db.create_all()
  ```

- [ ] **Admin account created**
  - Email: Set via ADMIN_EMAIL environment variable
  - Password: Set via ADMIN_PASSWORD environment variable
  - Tier: ADMIN

- [ ] **Test data removed** (if any)

- [ ] **Backup strategy configured**
  - Daily automated backups
  - Retention policy: 30 days minimum
  - Restore procedure documented

---

### PWA Requirements

- [ ] **HTTPS enabled** (required for service workers)
  - SSL certificate valid
  - Redirects HTTP → HTTPS
  - Mixed content warnings resolved

- [ ] **Service worker accessible at root**
  - [ ] `https://Evident.info/sw.js` returns 200
  - [ ] `Cache-Control` header allows caching
  - [ ] MIME type: `application/javascript`

- [ ] **PWA manifest accessible**
  - [ ] `https://Evident.info/manifest.json` returns 200
  - [ ] All icon files exist (72px - 512px)
  - [ ] `start_url` is valid

- [ ] **Icons generated** (8 sizes)
  - [ ] 72x72 (`/assets/images/icon-72.png`)
  - [ ] 96x96 (`/assets/images/icon-96.png`)
  - [ ] 128x128 (`/assets/images/icon-128.png`)
  - [ ] 144x144 (`/assets/images/icon-144.png`)
  - [ ] 152x152 (`/assets/images/icon-152.png`)
  - [ ] 192x192 (`/assets/images/icon-192.png`)
  - [ ] 384x384 (`/assets/images/icon-384.png`)
  - [ ] 512x512 (`/assets/images/icon-512.png`)

- [ ] **Apple touch icons**
  - [ ] 180x180 (`/apple-touch-icon.png`)
  - [ ] 167x167 (iPad)
  - [ ] 152x152 (iPad)

- [ ] **Favicon**
  - [ ] 32x32 (`/favicon-32x32.png`)
  - [ ] 16x16 (`/favicon-16x16.png`)
  - [ ] ICO format (`/favicon.ico`)

---

### Static Files

- [ ] **All CSS files present**
  - [ ] `/assets/css/main.css`
  - [ ] `/assets/css/critical.css`
  - [ ] `/assets/css/mobile.css`
  - [ ] All component CSS files

- [ ] **All JavaScript files present**
  - [ ] `/assets/js/main.js`
  - [ ] Any vendor scripts

- [ ] **Images optimized**
  - [ ] All images compressed (TinyPNG, ImageOptim)
  - [ ] WebP versions created where appropriate
  - [ ] Lazy loading implemented

- [ ] **Fonts loaded**
  - [ ] Font files accessible
  - [ ] `font-display: swap` in CSS

---

### SEO & Social

- [ ] **Structured data component integrated**
  - [ ] All pages include `{% include 'components/structured-data.html' %}`
  - [ ] Page-specific data passed correctly (breadcrumbs, FAQs, articles)

- [ ] **Social media images created**
  - [ ] Open Graph image: 1200×630px (`/assets/images/og-image.jpg`)
  - [ ] Twitter Card image: 1200×675px (`/assets/images/twitter-card.jpg`)
  - [ ] Images meet platform requirements (size, format)

- [ ] **Meta tags complete**
  - [ ] Title tags unique per page
  - [ ] Meta descriptions unique per page (150-160 chars)
  - [ ] Canonical URLs set correctly
  - [ ] Robots.txt configured
  - [ ] Sitemap.xml generated and submitted

- [ ] **Google Search Console**
  - [ ] Property verified
  - [ ] Sitemap submitted
  - [ ] No crawl errors

- [ ] **Bing Webmaster Tools**
  - [ ] Site added and verified
  - [ ] Sitemap submitted

---

### Security

- [ ] **Security headers configured** (13 total)
  - Verified in `app.py` `@app.after_request` middleware
  - [ ] Content-Security-Policy
  - [ ] Strict-Transport-Security (HSTS)
  - [ ] X-Frame-Options
  - [ ] X-Content-Type-Options
  - [ ] X-XSS-Protection
  - [ ] Referrer-Policy
  - [ ] Permissions-Policy
  - [ ] Cross-Origin policies (COEP, COOP, CORP)

- [ ] **CSP violations monitored**
  - [ ] Report-URI endpoint configured (optional)
  - [ ] Monitoring dashboard set up

- [ ] **File upload security**
  - [ ] Max file size enforced (100MB)
  - [ ] File type validation (MIME + extension)
  - [ ] Virus scanning enabled (optional: ClamAV)
  - [ ] Uploaded files stored securely (S3 or protected directory)

- [ ] **Rate limiting configured**
  - [ ] Login attempts: 5 per 15 minutes
  - [ ] API calls: Tier-based limits
  - [ ] Upload endpoints: 10 per hour (FREE tier)

- [ ] **CSRF protection enabled**
  - Flask-WTF CSRF tokens on all forms
  - SameSite cookie attribute set

- [ ] **SQL injection prevention**
  - All queries use parameterized statements
  - ORM (SQLAlchemy) used correctly

- [ ] **Secrets management**
  - [ ] No secrets in code or git history
  - [ ] Environment variables used
  - [ ] `.env` file in `.gitignore`

---

### Monitoring & Logging

- [ ] **Error monitoring**
  - [ ] Sentry.io configured (or alternative)
  - [ ] Error alerts sent to email/Slack
  - [ ] Source maps uploaded for JS debugging

- [ ] **Application logging**
  - [ ] Log level: INFO in production
  - [ ] Logs centralized (CloudWatch, Papertrail, Logtail)
  - [ ] PII redacted from logs

- [ ] **Performance monitoring**
  - [ ] Amplitude analytics integrated
  - [ ] Custom events tracked:
    - [ ] User signups
    - [ ] Video uploads
    - [ ] Payment events
    - [ ] API usage
  - [ ] Funnels configured

- [ ] **Uptime monitoring**
  - [ ] Uptime Robot or Pingdom configured
  - [ ] Check frequency: 5 minutes
  - [ ] Alerts: Email + SMS

- [ ] **Status page** (optional)
  - Status page URL: https://status.Evident.info
  - Linked from footer

---

### Performance

- [ ] **CDN configured** (optional)
  - Static assets served from CDN (Cloudflare, CloudFront)
  - Cache headers optimized
  - Purge strategy defined

- [ ] **Gzip compression enabled**
  - Flask-Compress middleware active
  - All text assets compressed (HTML, CSS, JS)

- [ ] **Browser caching configured**
  - Static assets: 1 year (`Cache-Control: public, max-age=31536000`)
  - HTML: No cache or short cache
  - Service worker: No cache

- [ ] **Database optimization**
  - Indexes created on frequently queried columns
  - Connection pooling configured
  - Query performance profiled

---

## 🚀 Deployment Steps

### 1. Final Code Review

- [ ] **Code committed to git**

  ```powershell
  git add .
  git commit -m "Production optimization: PWA, CSP, SEO, CSS split"
  git push origin main
  ```

- [ ] **Branch protection enabled**
  - Require pull request reviews
  - Require status checks to pass
  - Enforce linear history

### 2. Database Migration

- [ ] **Backup current database** (if updating existing)

  ```bash
  pg_dump -U username -h hostname dbname > backup.sql
  ```

- [ ] **Run migrations**

  ```python
  # If using Flask-Migrate
  flask db upgrade
  ```

- [ ] **Verify migration success**
  ```sql
  SELECT * FROM alembic_version;
  ```

### 3. Deploy to Staging (if available)

- [ ] **Deploy to staging environment**
  - URL: https://staging.Evident.info

- [ ] **Run smoke tests**
  - [ ] Homepage loads
  - [ ] Login works
  - [ ] Signup works
  - [ ] Dashboard loads
  - [ ] Video upload works
  - [ ] Payment flow works (test mode)

- [ ] **Run full test suite**
  ```powershell
  pytest --env=staging
  ```

### 4. Deploy to Production

- [ ] **Deploy via Render dashboard** (or your platform)
  - Trigger manual deploy OR
  - Merge to main branch (auto-deploy)

- [ ] **Monitor deploy logs**
  - Check for errors during build
  - Verify all services start

- [ ] **Verify deployment**
  - [ ] Homepage: https://Evident.info
  - [ ] Service worker: https://Evident.info/sw.js
  - [ ] Manifest: https://Evident.info/manifest.json

### 5. Post-Deployment Verification

- [ ] **Health check endpoint**

  ```powershell
  curl https://Evident.info/health
  # Expected: {"status": "ok"}
  ```

- [ ] **Critical paths work**
  - [ ] Homepage loads (200 OK)
  - [ ] Login page loads
  - [ ] Signup page loads
  - [ ] Dashboard (authenticated)
  - [ ] Pricing page
  - [ ] Documentation

- [ ] **PWA features work**
  - [ ] Service worker registers (DevTools → Application)
  - [ ] Manifest loads (DevTools → Application → Manifest)
  - [ ] Offline page accessible
  - [ ] Install prompt appears (mobile)

- [ ] **Security headers present**

  ```powershell
  curl -I https://Evident.info
  # Check for: CSP, HSTS, X-Frame-Options, etc.
  ```

- [ ] **Database connection works**
  - Test login with existing account
  - Test signup with new account

- [ ] **Stripe integration works**
  - Test checkout flow (test mode first!)
  - Verify webhook receives events

---

## 📱 Mobile Device Testing

### iOS Testing

- [ ] **iPhone (iOS 16+)**
  - [ ] Safari: Site loads correctly
  - [ ] Install PWA: Add to Home Screen
  - [ ] PWA runs standalone (no browser UI)
  - [ ] Offline mode works
  - [ ] Touch targets ≥48px
  - [ ] Viewport zooming disabled on inputs
  - [ ] Safe area respected (notch devices)

### Android Testing

- [ ] **Android device (12+)**
  - [ ] Chrome: Site loads correctly
  - [ ] Install PWA: Add to Home Screen
  - [ ] PWA runs standalone
  - [ ] Offline mode works
  - [ ] Touch targets ≥48px
  - [ ] Tap highlights styled

---

## 🔍 Performance Testing

### Lighthouse Audit

- [ ] **Run Lighthouse on production**
  - Tool: https://pagespeed.web.dev/
  - URL: https://Evident.info

- [ ] **Target Scores (Mobile)**
  - [ ] Performance: 90+ (target: 95)
  - [ ] Accessibility: 100
  - [ ] Best Practices: 90+ (target: 96)
  - [ ] SEO: 90+ (target: 92)

- [ ] **Target Scores (Desktop)**
  - [ ] Performance: 95+
  - [ ] Accessibility: 100
  - [ ] Best Practices: 95+
  - [ ] SEO: 95+

### Core Web Vitals

- [ ] **Field Data (Real User Monitoring)**
  - [ ] LCP < 2.5s
  - [ ] INP < 200ms
  - [ ] CLS < 0.1

- [ ] **Lab Data (Lighthouse)**
  - [ ] LCP < 1.5s
  - [ ] INP < 100ms
  - [ ] CLS < 0.05

---

## 🎯 User Acceptance Testing

### Critical User Flows

- [ ] **New user signup**
  - Navigate to /signup
  - Enter email, password
  - Verify email sent
  - Complete signup
  - Redirected to dashboard

- [ ] **Existing user login**
  - Navigate to /login
  - Enter credentials
  - Redirected to dashboard
  - Tier displayed correctly

- [ ] **Video upload (FREE tier)**
  - Navigate to /upload
  - Select video file
  - Upload progresses
  - Video appears in dashboard
  - Usage count incremented

- [ ] **Upgrade to PRO**
  - Navigate to /pricing
  - Click "Upgrade to PRO"
  - Stripe checkout opens
  - Complete payment (test card)
  - Tier upgraded in database
  - Dashboard reflects new tier

- [ ] **API key generation (PRO+)**
  - Navigate to /dashboard/api-keys
  - Click "Generate API Key"
  - Key displayed
  - Key works in API call

- [ ] **Admin features**
  - Login as admin (admin@Evident.info)
  - Navigate to /admin
  - View all users
  - View usage statistics
  - Modify user tier (test only)

---

## 📊 Analytics Verification

- [ ] **Amplitude events firing**
  - Login event
  - Signup event
  - Video upload event
  - Payment event
  - Page view events

- [ ] **Funnels configured**
  - Signup funnel (visit → signup → verify → complete)
  - Conversion funnel (visit → pricing → checkout → payment)

- [ ] **User properties tracked**
  - User tier
  - Signup date
  - Total uploads
  - Total spend

---

## 🔐 Security Testing

### Automated Scans

- [ ] **OWASP ZAP scan**
  - Run automated scan
  - Review results
  - Address high/medium findings

- [ ] **Security headers check**
  - Tool: https://securityheaders.com
  - Expected: A+ grade

- [ ] **SSL test**
  - Tool: https://www.ssllabs.com/ssltest/
  - Expected: A+ grade

### Manual Testing

- [ ] **XSS prevention**
  - Try injecting `<script>alert('XSS')</script>` in forms
  - Expected: Escaped or blocked

- [ ] **CSRF protection**
  - Try submitting form without CSRF token
  - Expected: 403 Forbidden

- [ ] **SQL injection**
  - Try `' OR '1'='1` in login form
  - Expected: Login fails, no database error

- [ ] **File upload security**
  - Try uploading .exe file
  - Expected: Rejected
  - Try uploading oversized file (>100MB)
  - Expected: Rejected

---

## 🎉 Launch Checklist

### Marketing & Communication

- [ ] **Announcement blog post** (optional)
  - Published on company blog
  - Shared on social media

- [ ] **Social media posts**
  - Twitter: Launch announcement
  - LinkedIn: Company update
  - Reddit: r/legaltech post (if appropriate)

- [ ] **Email to beta users**
  - Thank you message
  - Launch announcement
  - New features highlight

- [ ] **Press release** (optional)
  - Distributed to relevant media

### Support Preparation

- [ ] **Support email configured**
  - support@Evident.info
  - Forwarding to team

- [ ] **Documentation published**
  - User guide
  - API documentation
  - FAQ page

- [ ] **Support ticket system** (optional)
  - Zendesk, Intercom, or similar
  - Integration tested

---

## 🛟 Rollback Plan

### If Critical Issues Found

1. **Identify severity**
   - Critical: Immediate rollback
   - High: Fix within 4 hours
   - Medium: Fix within 24 hours
   - Low: Fix in next release

2. **Rollback procedure**

   ```bash
   # Render: Rollback to previous deployment
   # In Render dashboard → Deployments → Select previous → Redeploy
   ```

3. **Database rollback** (if needed)

   ```bash
   # Restore from backup
   pg_restore -U username -h hostname -d dbname backup.sql
   ```

4. **Communication**
   - Status page update
   - Email to active users (if downtime >15 min)
   - Post-mortem report

---

## 📝 Post-Launch Monitoring (First 48 Hours)

### Hour 1-4 (Critical Window)

- [ ] Monitor error logs every 15 minutes
- [ ] Check uptime status
- [ ] Verify key metrics:
  - [ ] Server CPU < 70%
  - [ ] Memory usage < 80%
  - [ ] Database connections < max
  - [ ] Response times < 500ms (p95)

### Day 1

- [ ] Review all error logs
- [ ] Check analytics events flowing
- [ ] Monitor payment transactions
- [ ] Review security alerts
- [ ] User feedback collection started

### Day 2

- [ ] Run Lighthouse audit again
- [ ] Review performance metrics
- [ ] Check for any security issues
- [ ] Analyze user behavior (Amplitude)
- [ ] Plan hotfixes if needed

---

## ✅ Final Sign-Off

**Deployed By:** \***\*\*\*\*\***\_\***\*\*\*\*\***  
**Date:** \***\*\*\*\*\***\_\***\*\*\*\*\***  
**Time:** \***\*\*\*\*\***\_\***\*\*\*\*\***  
**Version:** \***\*\*\*\*\***\_\***\*\*\*\*\***  
**Git Commit:** \***\*\*\*\*\***\_\***\*\*\*\*\***

**Approvals:**

- [ ] **Tech Lead:** \***\*\*\*\*\***\_\***\*\*\*\*\*** Date: **\_**
- [ ] **Product Owner:** \***\*\*\*\*\***\_\***\*\*\*\*\*** Date: **\_**
- [ ] **QA Lead:** \***\*\*\*\*\***\_\***\*\*\*\*\*** Date: **\_**

---

**Deployment Status:** ⏳ Pending / ✅ Complete / ❌ Failed

**Notes:**

---

---

---

---

**Last Updated:** January 27, 2026  
**Next Review:** Upon deployment completion
