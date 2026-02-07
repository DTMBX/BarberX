# Evident Feature & Access Level Testing Plan

## Subscription Tiers Overview

### 1. **FREE Tier (Explorer)** - $0/month

**Access Level:** Demo & Educational **Limits:**

- ✅ 1 BWC video per month (5 min max)
- ✅ 1 PDF document per month (10 pages max)
- ✅ ONE-TIME file upload (lifetime - PDF OR video, 50MB max)
- ✅ 3 pre-loaded demo cases
- ✅ 10 transcription minutes/month
- ✅ 100 search queries/month
- ✅ 1 GB storage
- ✅ Educational resources & templates
- ✅ Basic AI assistant
- ❌ Watermarked exports
- ❌ 7-day data retention (auto-delete)
- ❌ 1 case limit
- ❌ No court-ready reports
- ❌ No API access

### 2. **STARTER Tier (Practitioner)** - $29/month

**Access Level:** Entry-tier professionals **Limits:**

- ✅ 10 BWC videos/month (10 hours total) - HARD CAP
- ✅ 5 PDF documents/month (250 pages) - HARD CAP
- ✅ 60 transcription minutes/month
- ✅ Unlimited search queries
- ✅ 10 GB storage
- ✅ Basic AI assistant
- ✅ 5 cases - HARD CAP
- ✅ Basic court-ready reports
- ✅ No watermarks
- ✅ 7-day FREE TRIAL
- ✅ **PREDICTABLE PRICING** - No surprise overage bills
- ❌ No API access
- ❌ No overage allowed (hard limits for budget protection)

### 3. **PROFESSIONAL Tier (Counselor)** - $79/month

**Access Level:** Solo practitioners & small firms **Limits:**

- ✅ 25 BWC videos/month (3 hours max each) - SOFT CAP
- ✅ 15 PDF documents/month (150 pages) - SOFT CAP
- ✅ 180 transcription minutes/month
- ✅ 1,500 search queries/month
- ✅ 50 GB storage - SOFT CAP
- ✅ Basic AI assistant
- ✅ 15 cases - SOFT CAP
- ✅ Basic court-ready reports
- ✅ 3-day FREE TRIAL
- ✅ **FLEXIBLE GROWTH** - Overage billing for busy months:
  - $1.50 per extra video (cheaper than PREMIUM)
  - $0.75 per extra PDF
  - $3.00 per extra case
  - $0.40 per extra GB
- ❌ No API access

### 4. **PREMIUM Tier (Advocate)** - $199/month

**Access Level:** Power users with advanced features **Limits:**

- ✅ 75 BWC videos/month - SOFT CAP
- ✅ 10 video hours/month - SOFT CAP
- ✅ 50 PDF documents/month - SOFT CAP
- ✅ 600 transcription minutes/month
- ✅ 10,000 search queries/month
- ✅ 250 GB storage
- ✅ FULL AI assistant
- ✅ 40 cases - SOFT CAP
- ✅ Advanced court-ready reports
- ✅ Timeline builder
- ✅ API access
- ✅ Forensic analysis
- ✅ Priority support
- ✅ Overage billing:
  - $2.00 per extra video
  - $5.00 per extra video hour
  - $1.00 per extra PDF
  - $5.00 per extra case

### 5. **ENTERPRISE Tier** - $599/month

**Access Level:** Organizations with unlimited usage **Limits:**

- ✅ UNLIMITED BWC videos
- ✅ UNLIMITED video hours
- ✅ UNLIMITED PDF documents
- ✅ UNLIMITED transcription minutes
- ✅ UNLIMITED search queries
- ✅ UNLIMITED storage
- ✅ Private AI instance
- ✅ UNLIMITED cases
- ✅ Firm-branded reports
- ✅ Timeline builder
- ✅ 20 multi-BWC sync
- ✅ API access
- ✅ Forensic analysis
- ✅ White-label
- ✅ Priority support + SLA
- ✅ Dedicated project manager
- ✅ On-premises data option
- ✅ UNLIMITED concurrent users
- ✅ NO overages (no limits)

### 6. **ADMIN Tier** - Internal Use

**Access Level:** Full system administration

- ✅ UNLIMITED everything
- ✅ Backend access
- ✅ Admin dashboard
- ✅ All features enabled

---

## Feature Testing Matrix

### Core Authentication Features

| Feature            | FREE | STARTER | PRO | PREMIUM | ENTERPRISE | ADMIN |
| ------------------ | ---- | ------- | --- | ------- | ---------- | ----- |
| Registration       | ✅   | ✅      | ✅  | ✅      | ✅         | ✅    |
| Login/Logout       | ✅   | ✅      | ✅  | ✅      | ✅         | ✅    |
| Password Reset     | ✅   | ✅      | ✅  | ✅      | ✅         | ✅    |
| Email Verification | ✅   | ✅      | ✅  | ✅      | ✅         | ✅    |
| 2FA/MFA            | ❌   | ❌      | ❌  | ✅      | ✅         | ✅    |

### File Upload Features

| Feature                    | FREE            | STARTER    | PRO        | PREMIUM    | ENTERPRISE | ADMIN  |
| -------------------------- | --------------- | ---------- | ---------- | ---------- | ---------- | ------ |
| One-time upload (lifetime) | ✅ (1 file)     | ❌         | ❌         | ❌         | ❌         | ❌     |
| BWC video upload           | ✅ (1/mo, 5min) | ✅ (10/mo) | ✅ (25/mo) | ✅ (75/mo) | ✅ (∞)     | ✅ (∞) |
| PDF upload                 | ✅ (1/mo, 10pg) | ✅ (5/mo)  | ✅ (15/mo) | ✅ (50/mo) | ✅ (∞)     | ✅ (∞) |
| Batch upload               | ❌              | ✅         | ✅         | ✅         | ✅         | ✅     |
| Max file size              | 50MB            | 512MB      | 1GB        | 5GB        | 20GB       | ∞      |

### Analysis Features

| Feature               | FREE         | STARTER    | PRO         | PREMIUM     | ENTERPRISE | ADMIN  |
| --------------------- | ------------ | ---------- | ----------- | ----------- | ---------- | ------ |
| Demo case viewing     | ✅ (3 cases) | ✅         | ✅          | ✅          | ✅         | ✅     |
| Video analysis        | ✅ (basic)   | ✅         | ✅          | ✅          | ✅         | ✅     |
| Transcription         | ✅ (10min)   | ✅ (60min) | ✅ (180min) | ✅ (600min) | ✅ (∞)     | ✅ (∞) |
| Voice stress analysis | ❌           | ❌         | ✅          | ✅          | ✅         | ✅     |
| Forensic analysis     | ❌           | ❌         | ❌          | ✅          | ✅         | ✅     |
| Timeline builder      | ❌           | ❌         | ❌          | ✅          | ✅         | ✅     |
| Multi-BWC sync        | ❌           | ❌         | ❌          | ❌          | ✅ (20)    | ✅ (∞) |

### AI Assistant Features

| Feature             | FREE | STARTER | PRO | PREMIUM | ENTERPRISE | ADMIN |
| ------------------- | ---- | ------- | --- | ------- | ---------- | ----- |
| Basic Q&A           | ✅   | ✅      | ✅  | ✅      | ✅         | ✅    |
| Legal research      | ❌   | ✅      | ✅  | ✅      | ✅         | ✅    |
| Citation generation | ❌   | ✅      | ✅  | ✅      | ✅         | ✅    |
| Advanced analysis   | ❌   | ❌      | ❌  | ✅      | ✅         | ✅    |
| Private instance    | ❌   | ❌      | ❌  | ❌      | ✅         | ✅    |

### Report & Export Features

| Feature             | FREE           | STARTER    | PRO        | PREMIUM       | ENTERPRISE   | ADMIN |
| ------------------- | -------------- | ---------- | ---------- | ------------- | ------------ | ----- |
| Basic reports       | ✅ (watermark) | ✅         | ✅         | ✅            | ✅           | ✅    |
| Court-ready reports | ❌             | ✅ (basic) | ✅ (basic) | ✅ (advanced) | ✅ (branded) | ✅    |
| PDF export          | ✅ (watermark) | ✅         | ✅         | ✅            | ✅           | ✅    |
| Word export         | ❌             | ✅         | ✅         | ✅            | ✅           | ✅    |
| Excel export        | ❌             | ❌         | ✅         | ✅            | ✅           | ✅    |
| White-label         | ❌             | ❌         | ❌         | ❌            | ✅           | ✅    |

### Storage & Data Features

| Feature           | FREE   | STARTER  | PRO   | PREMIUM   | ENTERPRISE | ADMIN |
| ----------------- | ------ | -------- | ----- | --------- | ---------- | ----- |
| Storage limit     | 1GB    | 10GB     | 50GB  | 250GB     | ∞          | ∞     |
| Data retention    | 7 days | ∞        | ∞     | ∞         | ∞          | ∞     |
| Case limit        | 1      | 5 (soft) | 15    | 40 (soft) | ∞          | ∞     |
| Search queries/mo | 100    | ∞        | 1,500 | 10,000    | ∞          | ∞     |
| On-premises data  | ❌     | ❌       | ❌    | ❌        | ✅         | ✅    |

### API & Integration Features

| Feature                  | FREE | STARTER | PRO | PREMIUM | ENTERPRISE | ADMIN |
| ------------------------ | ---- | ------- | --- | ------- | ---------- | ----- |
| REST API access          | ❌   | ❌      | ❌  | ✅      | ✅         | ✅    |
| API key management       | ❌   | ❌      | ❌  | ✅      | ✅         | ✅    |
| Webhooks                 | ❌   | ❌      | ❌  | ✅      | ✅         | ✅    |
| Third-party integrations | ❌   | ❌      | ❌  | ❌      | ✅         | ✅    |

### Support Features

| Feature          | FREE | STARTER | PRO | PREMIUM | ENTERPRISE | ADMIN |
| ---------------- | ---- | ------- | --- | ------- | ---------- | ----- |
| Email support    | ✅   | ✅      | ✅  | ✅      | ✅         | ✅    |
| Priority support | ❌   | ❌      | ❌  | ✅      | ✅         | ✅    |
| SLA guarantee    | ❌   | ❌      | ❌  | ❌      | ✅         | ✅    |
| Dedicated PM     | ❌   | ❌      | ❌  | ❌      | ✅         | ✅    |

---

## Testing Checklist

### 1. Authentication & Authorization Tests

- [ ] User registration (all tiers)
- [ ] Email verification flow
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Password reset flow
- [ ] Session management
- [ ] Logout functionality
- [ ] Tier-based route protection (@require_tier decorator)
- [ ] Usage limit enforcement (@check_usage_limit decorator)

### 2. Tier-Specific Feature Tests

- [ ] FREE tier: One-time upload enforcement
- [ ] FREE tier: Demo case access (3 cases)
- [ ] FREE tier: 7-day data retention
- [ ] FREE tier: Watermark on exports
- [ ] STARTER tier: Soft cap with overage billing
- [ ] STARTER tier: 10 video limit (soft)
- [ ] PROFESSIONAL tier: Hard cap enforcement
- [ ] PROFESSIONAL tier: 3-day trial
- [ ] PREMIUM tier: API access enabled
- [ ] PREMIUM tier: Overage billing calculation
- [ ] ENTERPRISE tier: Unlimited usage verification
- [ ] ENTERPRISE tier: White-label features
- [ ] ADMIN tier: Backend access

### 3. File Upload & Processing Tests

- [ ] BWC video upload (per tier limits)
- [ ] PDF document upload (per tier limits)
- [ ] File size validation (per tier)
- [ ] Video duration validation (FREE: 5min, PRO: 3hrs)
- [ ] PDF page count validation (FREE: 10pg)
- [ ] Batch upload (disabled for FREE)
- [ ] Upload counter incrementation
- [ ] Storage quota tracking

### 4. Analysis & Processing Tests

- [ ] Video transcription (per tier minutes)
- [ ] Voice stress analysis (PREMIUM+)
- [ ] Forensic analysis (PREMIUM+)
- [ ] Scene detection
- [ ] Timeline builder (PREMIUM+)
- [ ] Multi-BWC sync (ENTERPRISE only)
- [ ] Demo case viewing (all tiers)

### 5. AI Assistant Tests

- [ ] Basic Q&A (all tiers)
- [ ] Legal research (STARTER+)
- [ ] Citation generation (STARTER+)
- [ ] Advanced analysis (PREMIUM+)
- [ ] Query limit enforcement (FREE: 100/mo)

### 6. Report & Export Tests

- [ ] Watermark presence (FREE tier only)
- [ ] No watermark (STARTER+)
- [ ] Basic court-ready report (STARTER, PRO)
- [ ] Advanced court-ready report (PREMIUM)
- [ ] Firm-branded report (ENTERPRISE)
- [ ] PDF export (all tiers with tier checks)
- [ ] Word export (STARTER+)
- [ ] Excel export (PRO+)
- [ ] White-label export (ENTERPRISE only)

### 7. Storage & Data Management Tests

- [ ] Storage quota tracking (per tier)
- [ ] Storage overage calculation (STARTER)
- [ ] Data retention enforcement (FREE: 7 days)
- [ ] Case limit enforcement (per tier)
- [ ] Auto-deletion after retention period (FREE)

### 8. Payment & Subscription Tests

- [ ] Stripe pricing table display
- [ ] Subscription upgrade flow
- [ ] Subscription downgrade flow
- [ ] Trial period activation (PRO: 3 days)
- [ ] Overage billing calculation (STARTER, PREMIUM)
- [ ] Payment method management
- [ ] Subscription cancellation
- [ ] Refund processing

### 9. API Access Tests (PREMIUM+ only)

- [ ] API key generation
- [ ] API key revocation
- [ ] API authentication
- [ ] Rate limiting per tier
- [ ] Webhook configuration (PREMIUM+)
- [ ] Third-party integration (ENTERPRISE)

### 10. Admin Features Tests

- [ ] Admin dashboard access (ADMIN only)
- [ ] User management
- [ ] Tier assignment
- [ ] Usage analytics
- [ ] System health monitoring
- [ ] Backend configuration
- [ ] Audit logs

---

## Automated E2E Test Coverage

### Existing Playwright Tests (150+ tests)

✅ **Authentication Suite** (11 tests)

- Login/logout flows
- Registration validation
- Password reset
- Session management

✅ **Payment Suite** (13 tests)

- Pricing page functionality
- Stripe integration
- Subscription flows

✅ **Stripe COEP Suite** (18 tests - NEW)

- Pricing table loading
- COEP/CORS headers
- Crossorigin attribute validation
- Responsive design
- Accessibility

✅ **Dashboard Suite** (14 tests)

- Dashboard navigation
- File upload features
- Legal analysis pages
- Evidence intake

✅ **API Suite** (19 tests)

- REST API endpoints
- Authentication
- Rate limiting
- Error handling

✅ **Site Health Suite** (13 tests)

- Homepage loading
- Security headers
- Performance metrics
- Error pages

✅ **UI Components Suite** (6 tests)

- Navigation
- Forms
- Buttons
- Accessibility

✅ **Cross-Platform Suite** (40 tests - NEW)

- API CORS/COEP validation
- Mobile responsive design (5 viewports)
- Touch interaction sizing
- REST conventions
- Security headers (CSP, X-Frame-Options)
- Performance benchmarks
- Service Worker support

---

## Manual Testing Required

### 1. Tier Upgrade/Downgrade Scenarios

- Test upgrade from FREE → STARTER → PRO → PREMIUM → ENTERPRISE
- Test downgrade path and feature restrictions
- Verify data retention during downgrades
- Test overage billing during tier transitions

### 2. Edge Cases

- User at exact tier limit (e.g., 10/10 videos for STARTER)
- User attempting to upload beyond limit
- Overage calculation with partial usage
- Data retention enforcement at boundary (day 6 → day 7 → day 8)
- Trial expiration handling

### 3. Integration Points

- Stripe webhook handling (subscription.updated, etc.)
- Email delivery (verification, password reset)
- Storage backend (file upload → storage → retrieval)
- AI assistant API calls
- Third-party API integrations (ENTERPRISE)

---

## Security Testing

### Access Control

- [ ] Unauthorized access to premium features
- [ ] Tier bypass attempts (URL manipulation)
- [ ] API authentication enforcement
- [ ] CSRF protection
- [ ] SQL injection prevention
- [ ] XSS prevention

### Data Protection

- [ ] Sensitive data encryption at rest
- [ ] Secure file upload handling
- [ ] Session security
- [ ] Password hashing (bcrypt)
- [ ] API key security
- [ ] GDPR compliance (data export/deletion)

---

## Performance Testing

### Load Testing

- [ ] Concurrent user handling (per tier)
- [ ] File upload under load
- [ ] Database query performance
- [ ] API rate limiting effectiveness
- [ ] Video processing queue management

### Stress Testing

- [ ] Maximum storage capacity
- [ ] Large file uploads (20GB for ENTERPRISE)
- [ ] Simultaneous video processing
- [ ] High API call volume
- [ ] Database connection pool limits

---

## Next Steps

1. **Run Full Playwright Suite**: Execute all 150+ automated E2E tests
2. **Manual Tier Testing**: Test each tier's limits and features manually
3. **Security Audit**: Run OWASP ZAP or similar security scanner
4. **Performance Baseline**: Establish performance benchmarks
5. **Load Testing**: Use k6 or Artillery for load testing
6. **Documentation**: Update API documentation with tier-specific endpoints
7. **Monitoring**: Set up alerting for tier limit violations
8. **User Acceptance Testing**: Get feedback from beta users at each tier
