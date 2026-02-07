# Evident Tier Architecture & Feature Matrix

## 🎯 Current Tier Structure (From models_auth.py)

### **All Tiers Are Currently WEB-BASED SaaS**

**Critical Finding:** Your current implementation has NO downloadable/desktop
app. Everything runs through the web interface at Evident.info.

--

## 📊 Feature Comparison Matrix

| Feature                   | Free   | Professional | Premium   | Enterprise                 |
| ------------------------- | ------ | ------------ | --------- | -------------------------- |
| **Deployment**            | Web    | Web          | Web       | **Web** (not downloadable) |
| **BWC Videos/Month**      | 2      | 25           | 100       | Unlimited                  |
| **PDF Pages/Month**       | 50     | 1,000        | 10,000    | Unlimited                  |
| **Transcription Minutes** | 30     | 600          | 3,000     | Unlimited                  |
| **Max File Size**         | 100 MB | 1 GB         | 5 GB      | 20 GB                      |
| **Storage**               | 0.5 GB | 25 GB        | 250 GB    | 1 TB                       |
| **Multi-Video Sync**      | ❌     | 3 videos     | 10 videos | Unlimited                  |
| **Export Watermarks**     | ✅ Yes | ❌ No        | ❌ No     | ❌ No                      |
| **API Access**            | ❌     | ❌           | ✅        | ✅                         |
| **Forensic Analysis**     | ❌     | ❌           | ✅        | ✅                         |
| **White Label**           | ❌     | ❌           | ❌        | ✅                         |
| **Priority Support**      | ❌     | ❌           | ❌        | ✅                         |
| **SLA Guarantee**         | ❌     | ❌           | ❌        | ✅                         |

--

## ⚠️ CRITICAL ISSUE: Enterprise at $799/month for Web-Only

### **Problem:**

Your Enterprise tier ($499, or $799 with my recommendation) offers:

- Unlimited usage on YOUR web servers
- White-label branding
- But NOT a downloadable app

**This creates a dangerous scenario:**

- Enterprise customer processes 1,000 videos/month on your infrastructure
- Your costs: ~$500-1,000/month (at scale)
- Your revenue: $799/month
- **Margin squeeze or loss** ⚠️

--

## 💡 RECOMMENDED TIER ARCHITECTURE

### **Option A: Keep All Web-Based (Current Architecture)**

**ALL TIERS:** Web-based SaaS (what you have now)

| Tier             | Price | Deployment | Key Differentiators                                             |
| ---------------- | ----- | ---------- | --------------------------------------------------------------- |
| **Free**         | $0    | Web SaaS   | 2 videos, watermarks, trial tier                                |
| **Professional** | $79   | Web SaaS   | 15 videos, no watermarks, small firms                           |
| **Premium**      | $249  | Web SaaS   | 60 videos, API access, forensics                                |
| **Enterprise**   | $999  | Web SaaS   | **300 videos/month (soft cap)**, white-label, dedicated support |

**Key Changes for Enterprise:**

```python
TierLevel.ENTERPRISE: {
    'bwc_videos_per_month': 300,  # NOT unlimited!
    'soft_cap': True,  # Allow overage with fees
    'overage_fee_per_video': 3.00,  # $3 per video over 300
    'custom_pricing_available': True,
}
```

**Pros:**

- ✅ You control all costs (runs on your servers)
- ✅ Easier to maintain (one codebase)
- ✅ Can update features instantly
- ✅ Usage tracking is accurate
- ✅ Can't bypass payment

**Cons:**

- ❌ Some enterprises want on-premise (security/compliance)
- ❌ Requires your infrastructure to scale
- ❌ Internet dependency

--

### **Option B: Hybrid Model (RECOMMENDED)** ⭐

**Free/Pro/Premium:** Web-based SaaS  
**Enterprise:** Self-hosted with license validation

| Tier             | Price         | Deployment      | Architecture                   |
| ---------------- | ------------- | --------------- | ------------------------------ |
| **Free**         | $0            | Web             | Cloud SaaS                     |
| **Professional** | $79           | Web             | Cloud SaaS                     |
| **Premium**      | $249          | Web             | Cloud SaaS                     |
| **Enterprise**   | **$1,999/mo** | **Self-Hosted** | Docker container + license key |

**Enterprise Self-Hosted Architecture:**

```yaml
# Docker deployment they run on their servers
services:
  Evident-app:
    image: Evident/enterprise:latest
    environment:
      - LICENSE_KEY=${ENTERPRISE_LICENSE_KEY}
      - LICENSE_CHECK_URL=https://license.Evident.info/validate
    volumes:
      - /var/Evident/data:/app/data
    ports:
      - "443:443"
```

**License Validation (Prevents Bypass):**

```python
import requests
import hashlib
from datetime import datetime

def validate_license():
    """Call home to verify license is active"""
    license_key = os.getenv('ENTERPRISE_LICENSE_KEY')

    # Call your license server
    response = requests.post(
        'https://license.Evident.info/validate',
        json={
            'license_key': license_key,
            'machine_id': get_machine_fingerprint(),
            'version': APP_VERSION
        }
    )

    if response.status_code != 200:
        raise LicenseError("Invalid or expired license")

    license_data = response.json()

    # Check expiration
    if datetime.fromisoformat(license_data['expires_at']) < datetime.utcnow():
        raise LicenseError("License expired. Please renew.")

    # Check machine limit
    if license_data['active_machines'] > license_data['allowed_machines']:
        raise LicenseError("License installed on too many servers")

    return license_data

# Check license every 24 hours + on startup
@app.before_request
def check_license_status():
    cache_key = 'license_validated'
    if not cache.get(cache_key):
        validate_license()
        cache.set(cache_key, True, timeout=86400)  # 24 hours
```

**How it Prevents Bypass:**

1. **License key required** - Can't run without valid key
2. **Phone home daily** - Checks subscription is active
3. **Machine fingerprinting** - Prevents copying to unlimited servers
4. **Version checking** - Forces updates for security/features
5. **Kill switch** - Can remotely disable if payment fails

**Enterprise Pricing (Self-Hosted):**

```
Base: $1,999/month (1 server, 500 videos/month)
Additional servers: +$500/month each
Volume tier: 1,000 videos/month = $2,999/month
```

**Pros:**

- ✅ Enterprise customers happy (runs in their data center)
- ✅ You don't pay for their AI processing (runs on their GPUs)
- ✅ Higher price justified ($1,999 vs $799)
- ✅ Can't bypass fees (license validation)
- ✅ Meets compliance requirements (DoD, CJIS, HIPAA)

**Cons:**

- ❌ More complex deployment (need Docker images)
- ❌ Support burden (helping them install/configure)
- ❌ License server infrastructure needed

--

### **Option C: Desktop App for All Tiers**

**All tiers:** Electron desktop app that calls your API

```javascript
// Electron app structure
const { app, BrowserWindow } = require("electron");
const axios = require("axios");

// User logs in, app stores auth token
async function analyzeVideo(videoPath) {
  const token = getAuthToken();

  // Upload to your API
  const formData = new FormData();
  formData.append("video", fs.createReadStream(videoPath));

  const response = await axios.post("https://api.Evident.info/analyze", formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "X-Tier": userTier, // Enforced server-side
    },
  });

  return response.data;
}
```

**Key Point:** Processing still happens on YOUR servers (they just upload via
desktop app instead of web browser)

**Pros:**

- ✅ Better UX (native app, offline queueing)
- ✅ Can integrate with local file system
- ✅ You still control costs (processing on your servers)
- ✅ Can add IDE integration (VS Code plugin, etc.)

**Cons:**

- ❌ Need to build/maintain desktop app
- ❌ OS-specific testing (Windows/Mac/Linux)
- ❌ Auto-update complexity
- ❌ Similar to web app, just different UI

--

## 🎯 MY RECOMMENDATION

### **Implement Option B (Hybrid) in Phases:**

#### **Phase 1: Now - Keep All Web-Based**

```
Free: $0 (web)
Professional: $79 (web)
Premium: $249 (web)
Enterprise: $999 (web, 300 video soft cap)
```

**Add to Enterprise limits:**

```python
TierLevel.ENTERPRISE: {
    'bwc_videos_per_month': 300,  # Soft cap
    'overage_allowed': True,
    'overage_fee_per_video': 3.00,
    'white_label': True,
    'priority_support': True,
    'custom_branding': True,
    'dedicated_account_manager': True,
}
```

**If enterprise customer needs more:**

- 300-500 videos: Charge overage fees ($3/video = $600 extra)
- 500+ videos: Upgrade to custom pricing or self-hosted

#### **Phase 2: Q2 2026 - Add Self-Hosted Option**

```
Enterprise Self-Hosted: $1,999/month
- Docker container they run
- License key validation
- Unlimited processing on their hardware
- 1 year contract minimum
- Quarterly business reviews
```

**Build:**

1. Dockerize Flask app
2. License validation service
3. Machine fingerprinting
4. Remote kill switch
5. Enterprise installation docs

#### **Phase 3: Q3 2026 - Desktop App (Optional)**

```
Evident Desktop: Available for Pro+ tiers
- Native Windows/Mac app (Electron)
- Syncs with cloud account
- Offline queueing
- Still calls API for processing
```

--

## 📋 Feature Justification by Tier

### **Free ($0) - Trial/Freemium**

**Goal:** Let users test platform, convert to paid

**Features:**

- 2 videos (enough to see value)
- Watermarked exports (incentive to upgrade)
- Web-only (lowest support burden)
- Basic AI analysis (show capability)

**Value Prop:** "Try before you buy"

--

### **Professional ($79) - Solo Practitioners**

**Goal:** Small law firms, solo defense attorneys

**Features:**

- 15 videos (1-2 cases/month)
- No watermarks (professional deliverables)
- Priority email support
- 500 PDF pages (discovery docs)

**Value Prop:** "Professional tools at accessible price"

**Typical Customer:**

- Public defender with 20 cases/year
- Small firm handling civil rights cases
- Processes 1-2 BWC videos per case

--

### **Premium ($249) - Small Firms**

**Goal:** Firms with multiple attorneys, higher volume

**Features:**

- 60 videos (5 cases/month)
- API access (integrate with case management)
- Forensic analysis (expert witness reports)
- 5,000 PDF pages
- Constitutional AI violations

**Value Prop:** "Complete legal tech stack for serious firms"

**Typical Customer:**

- 2-5 attorney civil rights firm
- Defense firm specializing in police misconduct
- Processes 50-100 videos/year
- Needs API to integrate with Clio/MyCase

--

### **Enterprise ($999-1,999) - Large Organizations**

**Goal:** Public defender offices, large firms, government

**Features:**

- 300 videos/month (web) or unlimited (self-hosted)
- White-label branding
- Dedicated support
- SLA guarantee
- Optional self-hosted deployment

**Value Prop:** "Enterprise-grade platform with compliance and scalability"

**Typical Customer:**

- Public Defender's Office (50+ attorneys)
- ACLU state chapter
- Large civil rights firm (10+ attorneys)
- Government oversight agency
- Processes 200-500 videos/month

**Self-Hosted Option for:**

- Classified/sensitive cases (DoD, FBI)
- CJIS compliance (law enforcement agencies)
- Air-gapped networks
- Countries with data sovereignty laws

--

## 🔒 Preventing Fee Bypass (Self-Hosted)

### **License Enforcement Strategy:**

```python
# License validation (in self-hosted version)
class LicenseManager:
    def __init__(self):
        self.license_key = os.getenv('Evident_LICENSE_KEY')
        self.last_check = None
        self.grace_period_hours = 72  # Can run offline for 3 days

    def validate(self):
        """Check license with home server"""
        try:
            response = requests.post(
                'https://license.Evident.info/v1/validate',
                json={
                    'license_key': self.license_key,
                    'machine_id': self.get_machine_id(),
                    'version': VERSION,
                    'usage_stats': self.get_usage_stats()
                },
                timeout=10
            )

            if response.status_code == 200:
                license_data = response.json()
                self.last_check = datetime.utcnow()
                return license_data
            else:
                return self.handle_validation_failure()

        except requests.RequestException:
            # Offline - allow grace period
            if self.within_grace_period():
                return {'status': 'grace_period'}
            else:
                raise LicenseError("Cannot validate license - please check internet")

    def get_machine_id(self):
        """Unique machine fingerprint"""
        import platform
        import socket

        components = [
            platform.node(),  # Hostname
            socket.gethostname(),
            str(uuid.getnode()),  # MAC address
        ]

        return hashlib.sha256(''.join(components).encode()).hexdigest()

    def get_usage_stats(self):
        """Report usage for billing/monitoring"""
        return {
            'videos_processed_this_month': count_videos(),
            'active_users': count_users(),
            'storage_used_gb': get_storage_usage(),
        }

# Enforce on every request
@app.before_request
def enforce_license():
    if not license_manager.is_valid():
        return jsonify({
            'error': 'License invalid or expired',
            'contact': 'enterprise@Evident.info'
        }), 403
```

### **Additional Protections:**

1. **Time bombs:**

```python
if (datetime.utcnow() - last_license_check) > timedelta(days=7):
    # Disable functionality after 7 days offline
    return "License validation required"
```

2. **Feature flags:**

```python
# Disable expensive features if license downgraded
if license_data['tier'] != 'ENTERPRISE':
    disable_feature('unlimited_processing')
    disable_feature('white_label')
```

3. **Usage reporting:**

```python
# Report actual usage for tiered billing
monthly_usage = {
    'videos': 847,  # They processed 847 videos
    'pdf_pages': 125000,
}

# Backend can bill overages or suggest upgrade
if monthly_usage['videos'] > 500:
    send_upgrade_notification()
```

4. **Version control:**

```python
# Force updates for critical security/billing fixes
if current_version < minimum_version:
    return "Update required. Download version 2.5+"
```

--

## 💰 Pricing Rationale for Self-Hosted

**Why $1,999/month for self-hosted vs $999 web?**

1. **Higher support costs:** You're helping them install/maintain
2. **Less control:** Can't instantly push updates
3. **Enterprise value:** They NEED on-premise for compliance
4. **Competitive:** Other legal tech self-hosted = $2k-10k/month
5. **Annual contracts:** Lock in $24k/year revenue

**Usage-based self-hosted pricing:**

```
Base: $1,999/month (up to 500 videos/month)
Standard: $2,999/month (up to 1,500 videos/month)
Enterprise: $4,999/month (up to 5,000 videos/month)
Custom: $10k+/month (unlimited, multiple servers)
```

--

## 🎬 Final Recommendation

### **Current State (Now):**

```
All tiers: Web-based SaaS
Free: $0 | Pro: $79 | Premium: $249 | Enterprise: $999
Enterprise gets 300 video soft cap + overage fees
```

### **6-Month Roadmap:**

```
Q2 2026: Build self-hosted Docker version
Q3 2026: Launch Enterprise Self-Hosted ($1,999/mo)
Q4 2026: Optional desktop app for Pro+ tiers
```

### **DO NOT Make Free Downloadable:**

- ❌ Users would bypass all fees
- ❌ No way to enforce limits
- ❌ No recurring revenue
- ❌ No usage tracking

### **Enterprise Architecture:**

```
Web Version (Current): $999/mo with 300 video cap
Self-Hosted (Future): $1,999/mo with license validation
```

**This gives you:**

- ✅ All current tiers remain profitable web SaaS
- ✅ Enterprise option for compliance-heavy customers
- ✅ License keys prevent bypass
- ✅ Higher pricing justified for self-hosted complexity
- ✅ Annual contracts ($24k-60k/year per enterprise customer)

**Want me to spec out the license validation system or Docker packaging
strategy?**
