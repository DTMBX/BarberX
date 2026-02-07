# Evident Testing Execution Plan

**Status:** Ready for Comprehensive Testing **Date:** January 31, 2026

---

## ✅ **Tier Structure Optimization Complete**

### **FIXED: Fair Tier Pricing Strategy**

| Tier             | Price   | Cap Type     | Rationale                                                       |
| ---------------- | ------- | ------------ | --------------------------------------------------------------- |
| **STARTER**      | $29/mo  | 🔒 HARD CAP  | Budget users get predictable pricing - no surprise bills        |
| **PROFESSIONAL** | $79/mo  | 📈 SOFT CAP  | Growing practices can handle busy months with fair overage fees |
| **PREMIUM**      | $199/mo | 📈 SOFT CAP  | Power users with flexible capacity needs                        |
| **ENTERPRISE**   | $599/mo | ♾️ UNLIMITED | No caps, no worries                                             |

### **Free Trial Strategy**

- **STARTER**: 7-day free trial (longer to prove value at lower price)
- **PROFESSIONAL**: 3-day free trial (faster decision for growing firms)
- **PREMIUM**: No trial (enterprise sales cycle with demos)
- **ENTERPRISE**: Custom onboarding with POC period

### **Overage Pricing (Fair & Progressive)**

| Resource         | PROFESSIONAL ($79) | PREMIUM ($199)       |
| ---------------- | ------------------ | -------------------- |
| Extra Video      | $1.50              | $2.00                |
| Extra PDF        | $0.75              | $1.00                |
| Extra Case       | $3.00              | $5.00                |
| Extra GB Storage | $0.40              | N/A (soft unlimited) |

**Logic**: Professional tier gets LOWER overage fees to support growth without
forcing immediate upgrade.

---

## 1. ✅ **Automated E2E Testing with Playwright**

### **Command Execution**

```powershell
cd c:\web-dev\github-repos\Evident.info
npx playwright test --config=playwright.config.cjs --reporter=html
npx playwright show-report
```

### **Test Coverage (144 tests across 8 suites)**

#### **Authentication Suite** (11 tests)

- [ ] User registration flow
- [ ] Email verification
- [ ] Login with valid/invalid credentials
- [ ] Password reset flow
- [ ] Session management
- [ ] Logout functionality
- [ ] Protected route access control

#### **Payment & Subscription Suite** (13 tests)

- [ ] Pricing page loads correctly
- [ ] Stripe pricing table displays
- [ ] Subscription checkout flow
- [ ] Payment success/cancel redirects
- [ ] Tier upgrade/downgrade UI
- [ ] Trial activation (STARTER: 7 days, PRO: 3 days)

#### **Stripe COEP Integration** (18 tests)

- [ ] Pricing table loads without COEP blocking
- [ ] Crossorigin attributes present on Stripe scripts
- [ ] COEP header is "credentialless"
- [ ] No CORS errors in console
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Accessibility compliance

#### **Dashboard Features** (14 tests)

- [ ] Dashboard navigation
- [ ] File upload interfaces
- [ ] Legal analysis pages
- [ ] Evidence intake forms
- [ ] Feature card visibility by tier

#### **API Endpoints** (19 tests)

- [ ] Public endpoints (health, rate-limit status)
- [ ] Authentication enforcement
- [ ] Protected endpoints return 401 without auth
- [ ] CORS headers validation
- [ ] Rate limiting per tier
- [ ] Error handling (400, 401, 403, 404, 500)

#### **Site Health** (13 tests)

- [ ] Homepage loads < 3s
- [ ] All public pages load correctly
- [ ] Static assets (CSS, JS, images)
- [ ] Security headers (CSP, X-Frame-Options, COEP)
- [ ] 404 error page displays

#### **UI Components** (6 tests)

- [ ] Navigation menu functionality
- [ ] Mobile menu toggle
- [ ] Form labels and accessibility
- [ ] Password field masking
- [ ] Responsive design (3 viewports)

#### **Cross-Platform Architecture** (40 tests)

- [ ] API CORS/COEP headers
- [ ] Mobile responsive design (5 viewports)
- [ ] Touch interaction sizing (≥44px)
- [ ] REST API conventions
- [ ] Security headers validation
- [ ] Performance benchmarks (<3s homepage, <1s API)
- [ ] Service Worker support
- [ ] Asset loading optimization

### **Test Execution Steps**

1. **Start Flask development server**

   ```powershell
   python app.py
   ```

   Wait for: `Running on http://127.0.0.1:5000`

2. **Run Playwright tests in parallel**

   ```powershell
   npx playwright test --config=playwright.config.cjs --workers=4
   ```

3. **Generate HTML report**

   ```powershell
   npx playwright test --config=playwright.config.cjs --reporter=html
   npx playwright show-report
   ```

4. **Review results**
   - Check `playwright-report/index.html`
   - Identify failures
   - Fix issues
   - Rerun: `npx playwright test --config=playwright.config.cjs --only-failed`

---

## 2. 📋 **Manual Tier-Specific Testing**

### **Test Matrix: Feature Access by Tier**

#### **STARTER Tier ($29/mo - HARD CAP)**

**Test Scenario 1: Upload Limits**

- [ ] Upload 10 BWC videos successfully
- [ ] Attempt 11th video → expect HARD CAP error message
- [ ] Error should suggest upgrade to PROFESSIONAL
- [ ] No overage billing option visible

**Test Scenario 2: Storage Limits**

- [ ] Upload files totaling 9.8 GB
- [ ] Attempt upload that exceeds 10 GB
- [ ] Expect HARD CAP error
- [ ] No overage fee calculation shown

**Test Scenario 3: Trial Period**

- [ ] New STARTER user gets 7-day free trial
- [ ] Trial countdown displayed in dashboard
- [ ] Features unlocked during trial
- [ ] Trial expiration notification at day 6
- [ ] Payment required after 7 days

**Test Scenario 4: Case Management**

- [ ] Create 5 cases successfully
- [ ] Attempt 6th case → expect HARD CAP error
- [ ] Error message: "Upgrade to PROFESSIONAL for 15 cases"

#### **PROFESSIONAL Tier ($79/mo - SOFT CAP)**

**Test Scenario 1: Overage Billing**

- [ ] Upload 25 videos (base limit)
- [ ] Upload 26th video → expect overage confirmation
- [ ] Modal displays: "Extra video: +$1.50"
- [ ] User accepts → video uploaded
- [ ] Invoice shows: Base $79 + Overage $1.50 = $80.50

**Test Scenario 2: PDF Overage**

- [ ] Upload 15 PDFs (base limit)
- [ ] Upload 16th PDF → overage modal
- [ ] Cost shown: +$0.75
- [ ] Confirm and verify billing

**Test Scenario 3: Storage Overage**

- [ ] Use 50 GB (base limit)
- [ ] Upload file pushing to 55 GB
- [ ] Overage: 5 GB × $0.40 = $2.00
- [ ] Confirm and verify monthly invoice

**Test Scenario 4: Trial Period**

- [ ] New PRO user gets 3-day trial
- [ ] Trial countdown in dashboard
- [ ] Full feature access during trial
- [ ] Payment required after 3 days

#### **PREMIUM Tier ($199/mo - SOFT CAP)**

**Test Scenario 1: API Access**

- [ ] Generate API key in dashboard
- [ ] Make authenticated API call
- [ ] Verify rate limiting (10,000 queries/month)
- [ ] Test API key revocation

**Test Scenario 2: Advanced Features**

- [ ] Access forensic analysis tools
- [ ] Use timeline builder
- [ ] Priority support ticket submission
- [ ] Advanced court-ready report generation

**Test Scenario 3: Overage at Higher Rate**

- [ ] Upload 75 videos (base limit)
- [ ] Upload 76th video → overage $2.00 (higher than PRO)
- [ ] Verify PREMIUM users pay more per overage
- [ ] Confirm this incentivizes upgrade from PRO

#### **ENTERPRISE Tier ($599/mo - UNLIMITED)**

**Test Scenario 1: Unlimited Usage**

- [ ] Upload 100+ videos (no limit)
- [ ] Process 1000+ PDFs (no limit)
- [ ] Create 50+ cases (no limit)
- [ ] Use 500+ GB storage (no limit)
- [ ] No overage fees or warnings

**Test Scenario 2: White-Label Features**

- [ ] Generate firm-branded report
- [ ] Custom logo on exports
- [ ] Custom color scheme
- [ ] No Evident branding visible

**Test Scenario 3: Enterprise Support**

- [ ] Contact dedicated project manager
- [ ] Submit priority ticket → response < 1 hour
- [ ] SLA guarantee validation
- [ ] On-premises data option configuration

---

## 3. 🔐 **Security Audit with OWASP ZAP**

### **Setup OWASP ZAP**

```powershell
# Download OWASP ZAP
# https://www.zaproxy.org/download/

# Install ZAP
choco install zap

# Or download installer from website
```

### **Security Scan Execution**

#### **Step 1: Passive Scan**

1. Start Evident application: `python app.py`
2. Launch OWASP ZAP
3. Set target URL: `http://localhost:5000`
4. Enable "Automated Scan"
5. Select "Passive Scan Only" (non-intrusive)
6. Wait for scan completion (~10-15 minutes)

#### **Step 2: Active Scan (Intrusive)**

1. Configure ZAP to use authentication
2. Login as test user (each tier)
3. Run active scan on authenticated pages
4. Test injection attacks:
   - SQL injection
   - XSS (Cross-Site Scripting)
   - CSRF token validation
   - Path traversal
   - Command injection

#### **Step 3: API Security Testing**

1. Import OpenAPI/Swagger spec (if available)
2. Scan API endpoints: `/api/*`
3. Test authentication bypass attempts
4. Verify rate limiting enforcement
5. Test API key validation
6. Check for sensitive data exposure

### **Security Checklist**

- [ ] **Authentication**
  - [ ] Password strength enforcement
  - [ ] Bcrypt hashing (not plaintext)
  - [ ] Session timeout (30 minutes)
  - [ ] CSRF protection on forms
  - [ ] SQL injection prevention (parameterized queries)

- [ ] **Authorization**
  - [ ] Tier-based access control (@require_tier)
  - [ ] Usage limit enforcement (@check_usage_limit)
  - [ ] Admin-only routes protected
  - [ ] API key validation
  - [ ] No privilege escalation vulnerabilities

- [ ] **Data Protection**
  - [ ] HTTPS/TLS in production
  - [ ] Sensitive files encrypted (141 files via git-crypt)
  - [ ] Environment variables for secrets (.env)
  - [ ] No secrets in git history
  - [ ] Secure file upload handling

- [ ] **Headers & CORS**
  - [ ] Content-Security-Policy (CSP) configured
  - [ ] X-Frame-Options: DENY
  - [ ] X-Content-Type-Options: nosniff
  - [ ] Strict-Transport-Security (HSTS)
  - [ ] COEP: credentialless (for Stripe)
  - [ ] CORS properly configured

- [ ] **Input Validation**
  - [ ] File upload type validation
  - [ ] File size limits enforced
  - [ ] Sanitized user input
  - [ ] No XSS vulnerabilities
  - [ ] Email validation on registration

### **Expected Scan Results**

- **High Risk**: 0 issues (must fix immediately)
- **Medium Risk**: < 5 issues (prioritize fixes)
- **Low Risk**: < 20 issues (document and monitor)
- **Informational**: Unlimited (review for improvements)

---

## 4. ⚡ **Load Testing for Concurrent Users**

### **Tool: k6 (Grafana Load Testing)**

#### **Install k6**

```powershell
choco install k6
# Or download from https://k6.io/
```

#### **Create Load Test Script**

```javascript
// load-test.js
import http from "k6/http";
import { check, sleep } from "k6";

export let options = {
  stages: [
    { duration: "2m", target: 10 }, // Ramp up to 10 users
    { duration: "5m", target: 50 }, // Ramp up to 50 users
    { duration: "10m", target: 100 }, // Ramp up to 100 users
    { duration: "5m", target: 200 }, // Peak load: 200 users
    { duration: "5m", target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"], // 95% requests < 500ms
    http_req_failed: ["rate<0.01"], // Error rate < 1%
  },
};

export default function () {
  // Test homepage
  let res = http.get("http://localhost:5000/");
  check(res, {
    "homepage status 200": (r) => r.status === 200,
    "homepage loads fast": (r) => r.timings.duration < 1000,
  });

  sleep(1);

  // Test API health endpoint
  res = http.get("http://localhost:5000/health");
  check(res, {
    "health check 200": (r) => r.status === 200,
    "health check fast": (r) => r.timings.duration < 100,
  });

  sleep(2);

  // Test authentication
  res = http.post("http://localhost:5000/auth/login", {
    email: "test@example.com",
    password: "testpass123",
  });
  check(res, {
    "login responds": (r) => r.status === 200 || r.status === 401,
  });

  sleep(3);
}
```

#### **Run Load Tests**

```powershell
# Start application
python app.py

# Run load test
k6 run load-test.js

# View real-time metrics in terminal
```

### **Load Test Scenarios**

#### **Scenario 1: Concurrent Free Users (100 users)**

- Target: 100 simultaneous FREE tier users
- Actions: Browse demo cases, view educational resources
- Expected: < 2s response time, < 1% error rate

#### **Scenario 2: Concurrent Paid Users (50 users)**

- Target: 50 STARTER/PRO users uploading files
- Actions: File uploads, video processing, transcription
- Expected: < 5s upload time, < 2% error rate

#### **Scenario 3: API Load (200 requests/second)**

- Target: PREMIUM/ENTERPRISE API users
- Actions: 200 API calls per second
- Expected: < 200ms API response, rate limiting active

#### **Scenario 4: Peak Load (500 users)**

- Target: Black Friday / major event traffic
- Actions: Mixed usage (browse, upload, API)
- Expected: Graceful degradation, no crashes

### **Performance Benchmarks**

| Metric            | Target  | Acceptable | Critical |
| ----------------- | ------- | ---------- | -------- |
| Homepage Load     | < 1s    | < 3s       | > 5s     |
| API Response      | < 100ms | < 500ms    | > 1s     |
| File Upload Start | < 2s    | < 5s       | > 10s    |
| Video Processing  | < 30s   | < 2min     | > 5min   |
| Database Query    | < 50ms  | < 200ms    | > 500ms  |
| Concurrent Users  | 200+    | 100+       | < 50     |

---

## 5. 👥 **User Acceptance Testing (UAT)**

### **Beta User Recruitment**

#### **Target Beta Cohorts**

1. **FREE Tier** (10 users)
   - Pro se litigants
   - Law students
   - Community advocates
   - **Goal**: Validate educational resources, demo cases

2. **STARTER Tier** (15 users)
   - Solo practitioners
   - Small immigration attorneys
   - Public defenders
   - **Goal**: Test hard cap enforcement, 7-day trial

3. **PROFESSIONAL Tier** (10 users)
   - Small law firms (2-5 attorneys)
   - Private defense attorneys
   - **Goal**: Validate overage billing, 3-day trial

4. **PREMIUM Tier** (5 users)
   - Medium firms (5-15 attorneys)
   - Litigation boutiques
   - **Goal**: Test API access, forensic tools

5. **ENTERPRISE Tier** (3 users)
   - Large firms (15+ attorneys)
   - Government agencies
   - **Goal**: Validate white-label, unlimited usage

### **UAT Test Plan (2-week period)**

#### **Week 1: Onboarding & Core Features**

**Day 1-2: Account Setup**

- [ ] User receives invitation email
- [ ] Completes registration
- [ ] Verifies email
- [ ] Activates trial (STARTER: 7 days, PRO: 3 days)
- [ ] Explores dashboard

**Day 3-5: File Upload & Analysis**

- [ ] Uploads BWC video (test tier limits)
- [ ] Uploads PDF documents
- [ ] Reviews transcription accuracy
- [ ] Tests search functionality
- [ ] Generates basic report

**Day 6-7: Advanced Features**

- [ ] Creates multiple cases
- [ ] Uses AI assistant for legal research
- [ ] Exports court-ready report
- [ ] Tests mobile app (if applicable)

#### **Week 2: Edge Cases & Feedback**

**Day 8-10: Tier Limit Testing**

- [ ] STARTER: Attempts to exceed hard cap
- [ ] PRO: Triggers overage billing
- [ ] PREMIUM: Tests API integration
- [ ] ENTERPRISE: Validates unlimited usage

**Day 11-12: Integration & Workflow**

- [ ] End-to-end case workflow
- [ ] Multi-device usage (desktop, tablet, mobile)
- [ ] Export to Word, PDF, Excel
- [ ] Share case with colleague (if multi-user)

**Day 13-14: Feedback & Survey**

- [ ] Complete UAT feedback survey
- [ ] 30-minute exit interview
- [ ] Provide NPS score (Net Promoter Score)
- [ ] Share testimonial (if willing)

### **UAT Feedback Survey**

**Section 1: Usability (1-5 scale)**

- How easy was registration and onboarding?
- How intuitive is the dashboard navigation?
- How clear are the tier limits and upgrade prompts?
- How satisfied are you with the AI assistant quality?

**Section 2: Performance**

- How fast did file uploads complete?
- How accurate were video transcriptions?
- How quickly did reports generate?
- Did you experience any errors or crashes?

**Section 3: Value Proposition**

- Is the pricing fair for your tier?
- Would you recommend Evident to colleagues?
- What features are most valuable to you?
- What features are missing or need improvement?

**Section 4: Tier-Specific Questions**

- **STARTER**: Is the hard cap acceptable or frustrating?
- **PROFESSIONAL**: Did you use overage billing? Was the cost fair?
- **PREMIUM**: Is API access valuable? What integrations do you need?
- **ENTERPRISE**: Do you need white-label? Is unlimited usage sufficient?

**Section 5: Open Feedback**

- What do you love about Evident?
- What would you change?
- Would you pay for this product? At what price?
- Any security concerns?

### **Success Metrics**

- **Onboarding Completion**: > 90% of users complete setup
- **Feature Adoption**: > 70% use core features (upload, analysis, export)
- **Trial Conversion**: > 30% of trial users convert to paid
- **NPS Score**: > +50 (world-class is +70)
- **Critical Bugs**: < 5 bugs per 100 users
- **Satisfaction**: > 4.0/5.0 average rating

---

## 6. 📊 **Test Results Documentation**

### **Report Structure**

#### **Executive Summary**

- Total tests executed: [144 automated + X manual]
- Pass rate: [X%]
- Critical issues: [X]
- Recommendations: [Top 3 priorities]

#### **Automated E2E Testing**

- Total tests: 144
- Passed: [X]
- Failed: [X]
- Skipped: [X]
- Test coverage: [X%] of user journeys
- Screenshot/video evidence: `playwright-report/`

#### **Manual Tier Testing**

- Tiers tested: FREE, STARTER, PRO, PREMIUM, ENTERPRISE
- Scenarios executed: [X]
- Issues found: [X]
- Overage billing accuracy: [X%]

#### **Security Audit**

- High-risk issues: [X] (must fix before production)
- Medium-risk issues: [X]
- Low-risk issues: [X]
- OWASP ZAP report: `security-audit/zap-report.html`

#### **Load Testing**

- Max concurrent users: [X]
- Peak throughput: [X] requests/second
- 95th percentile latency: [X]ms
- Error rate: [X%]
- k6 report: `load-testing/k6-results.html`

#### **User Acceptance Testing**

- Beta users: [X]
- Completion rate: [X%]
- Average satisfaction: [X]/5.0
- NPS score: [X]
- Trial conversion: [X%]
- Key feedback themes: [List top 3]

---

## 7. 🚀 **Pre-Production Checklist**

### **Code Quality**

- [ ] All Playwright tests passing (144/144)
- [ ] No critical security vulnerabilities (OWASP ZAP)
- [ ] Load testing meets benchmarks (< 500ms p95)
- [ ] Code coverage > 80% (backend)
- [ ] Linting/formatting applied (Prettier, Stylelint)

### **Tier System**

- [ ] STARTER hard cap enforced correctly
- [ ] PROFESSIONAL overage billing accurate
- [ ] PREMIUM API access functional
- [ ] ENTERPRISE unlimited usage validated
- [ ] Trial periods working (STARTER: 7 days, PRO: 3 days)

### **Payment Integration**

- [ ] Stripe checkout flow tested
- [ ] Subscription webhooks handling (created, updated, canceled)
- [ ] Overage invoicing automated
- [ ] Refund processing functional
- [ ] Tax calculation (if applicable)

### **Security Hardening**

- [ ] All secrets encrypted (git-crypt)
- [ ] Environment variables configured
- [ ] HTTPS/TLS certificates installed
- [ ] WAF (Web Application Firewall) configured
- [ ] Rate limiting per tier
- [ ] Backup & disaster recovery plan

### **Monitoring & Logging**

- [ ] Application logging (Winston/Python logging)
- [ ] Error tracking (Sentry/Rollbar)
- [ ] Performance monitoring (New Relic/DataDog)
- [ ] Uptime monitoring (Pingdom/StatusCake)
- [ ] Usage analytics (PostHog/Mixpanel)

### **Documentation**

- [ ] API documentation (Swagger/Postman)
- [ ] User guide for each tier
- [ ] Admin manual
- [ ] Troubleshooting guide
- [ ] Security best practices

### **Compliance**

- [ ] GDPR compliance (data export/deletion)
- [ ] Terms of Service finalized
- [ ] Privacy Policy finalized
- [ ] Cookie consent banner
- [ ] Data retention policies documented

---

## 8. 🎯 **Next Steps Priority**

### **Immediate (This Week)**

1. ✅ Run full Playwright test suite
2. ✅ Execute manual tier testing (FREE, STARTER, PRO)
3. ✅ Document tier optimization (hard vs soft caps)
4. ⏳ Fix any critical test failures

### **Short Term (Next 2 Weeks)**

1. ⏳ Complete OWASP ZAP security audit
2. ⏳ Execute load testing with k6
3. ⏳ Recruit 40+ beta users for UAT
4. ⏳ Deploy staging environment

### **Medium Term (Next Month)**

1. ⏳ Complete UAT with beta cohorts
2. ⏳ Analyze feedback and iterate
3. ⏳ Fix all medium/high priority issues
4. ⏳ Prepare production deployment

### **Long Term (Next Quarter)**

1. ⏳ Launch to public (soft launch)
2. ⏳ Monitor metrics (NPS, churn, conversion)
3. ⏳ Scale infrastructure based on load
4. ⏳ Expand API capabilities

---

## 📞 **Support & Resources**

### **Testing Tools**

- Playwright: https://playwright.dev/
- OWASP ZAP: https://www.zaproxy.org/
- k6 Load Testing: https://k6.io/
- Lighthouse (Performance): https://developers.google.com/web/tools/lighthouse

### **Documentation**

- Evident Feature Test Plan: `FEATURE-TEST-PLAN.md`
- Test Coverage Report: `TEST-COVERAGE-REPORT.md`
- Architecture Documentation: `ARCHITECTURE.md`
- API Documentation: `API-REFERENCE.md` (to be created)

### **Contact**

- Development Team: dev@Evident.info
- Security Issues: security@Evident.info
- Beta Program: beta@Evident.info

---

**Status**: Ready to execute comprehensive testing program **Last Updated**:
January 31, 2026 **Next Review**: After initial test execution
