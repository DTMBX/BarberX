# Evident Security Audit Report

## PHASE 1 — REPOSITORY INVENTORY

**Audit Date**: January 31, 2026  
**Auditor Role**: Senior Security Architect, Application Governance Auditor, Systems Engineer  
**Methodology**: Evidence-based code analysis (no assumptions)

---

## 1. SYSTEM COMPONENTS IDENTIFIED

### 1.1 Frontend Components

- **Flask Web Application** (`app.py` - 6,912 lines)
  - Jinja2 templates in `templates/` (109 files)
  - Static assets in `assets/` (192 items)
  - Client-side JavaScript in `static/js/`
- **.NET MAUI Mobile App** (`src/Evident.Mobile/`)
  - Cross-platform (Windows, Android, iOS)
  - XAML views with MVVM architecture
  - Recently added configuration management (appsettings.json)

- **ASP.NET Core Web API** (`src/Evident.Web/`)
  - API Gateway (optional proxy to Flask)
  - JWT authentication configured
  - Controllers for analysis operations

### 1.2 Backend/API Services

- **Primary Backend**: Flask (`app.py`)
  - 6,912 lines of Python code
  - Multiple API endpoints (upload, analysis, legal, evidence)
  - Session-based authentication via Flask-Login
- **API Modules** (`api/` directory - 17 items):
  - `auth.py` - Authentication API
  - `chatgpt.py` - ChatGPT integration
  - `document_optimizer.py` - Document processing
  - `enhanced_chat.py` - Chat functionality
  - `legal_chatbot.py` - Legal AI assistant
  - `legal_library.py` - Legal research
  - `metering.py` - Usage tracking
  - `municipal.py` - Municipal code access
  - `reasoning_pipeline.py` - AI reasoning
  - `trinity.py` - Trinity service

### 1.3 Authentication & Authorization Modules

**CRITICAL FILES IDENTIFIED**:

1. **`models_auth.py`** (507 lines)
   - `User` model with tier system
   - `TierLevel` enum: FREE, STARTER, PROFESSIONAL, PREMIUM, ENTERPRISE, ADMIN
   - `UsageTracking` model
   - Password hashing via bcrypt
   - Tier limits defined in `get_tier_limits()` method

2. **`auth_routes.py`** (940 lines)
   - Flask Blueprint for auth routes
   - Login/logout/signup handlers
   - Decorators: `@tier_required`, `@admin_required`, `@feature_required`
   - Flask-Login integration

3. **`tier_gating.py`** (498 lines)
   - `@require_tier(minimum_tier)` decorator
   - `@check_usage_limit(limit_field, increment)` decorator
   - `@require_feature(feature_name)` decorator
   - `TierGate` helper class for template access checks

4. **`login_security.py`** (imported but optional)
   - AI-powered login security
   - Risk scoring
   - Fallback functions if not available

5. **`two_factor_auth.py`**
   - Two-factor authentication module

### 1.4 Billing & Membership Logic

**CRITICAL FILES IDENTIFIED**:

1. **`stripe_subscription_service.py`** (26,147 bytes)
   - Stripe integration for subscriptions
   - Webhook handling
   - Subscription status tracking

2. **`stripe_payment_service.py`** (14,885 bytes)
   - Payment processing

3. **`stripe_payments.py`** (10,380 bytes)
   - Additional payment logic

4. **User Model Fields** (in `models_auth.py`):
   ```python
   stripe_customer_id
   stripe_subscription_id
   stripe_subscription_status
   stripe_current_period_end
   trial_end
   is_on_trial
   ```

### 1.5 Storage Systems

**Database**:

- SQLAlchemy ORM with SQLite (development) or PostgreSQL (production)
- `db = SQLAlchemy()` in `models_auth.py`
- Tables: `users`, `usage_tracking`, and others

**File Storage**:

- `UPLOAD_FOLDER` for BWC videos
- `uploads/` directory (gitignored)
- `bwc_videos/` directory (gitignored)
- `bwc_analysis/` directory (gitignored)
- User storage tracking: `storage_used_mb` field in User model

**Secrets Storage**:

- `.env` file (gitignored) - contains API keys
- `secrets.enc` (encrypted file)
- Environment variables

### 1.6 AI/Processing Pipelines

**AI Services Identified**:

1. **BWC Analysis** (`bwc_forensic_analyzer.py` - 33,937 bytes)
2. **Whisper Transcription** (`whisper_transcription.py` - 13,254 bytes)
3. **OCR Service** (`ocr_service.py` - 14,776 bytes)
4. **Legal AI Agents** (`legal_ai_agents.py` - 31,911 bytes)
5. **Case Law Scanner** (`case_law_violation_scanner.py` - 26,248 bytes)
6. **Evidence Processing** (`evidence_processing.py` - 27,224 bytes)
7. **ChatGPT Integration** (`chatgpt_service.py` - 7,257 bytes)
8. **Legal Trinity Service** (`legal_trinity_service.py` - 33,385 bytes)

**AI Pipeline Orchestration**:

- `src/ai/pipeline/` directory
- `backend_integration.py` (17,878 bytes)
- `unified_evidence_service.py` (17,298 bytes)

### 1.7 Configuration & Environment Handling

**Configuration Files**:

- `.env` - **PRESENT IN REPOSITORY** (1,619 bytes) ⚠️ SECURITY RISK
- `.env-temp` - Present (223 bytes)
- `.env.template` - Safe template (1,428 bytes)
- `config_manager.py` (13,011 bytes)

**Mobile App Configuration**:

- `src/Evident.Mobile/appsettings.json` (embedded resource)
- Environment-based API endpoint selection
- Configuration loaded at runtime

---

## 2. SECURITY, AUTH, AND ACCESS-RELATED FILES

### 2.1 Authentication Files

```
✓ models_auth.py          - User model, tier definitions
✓ auth_routes.py          - Login/signup routes
✓ tier_gating.py          - Tier enforcement decorators
✓ login_security.py       - AI security checks
✓ two_factor_auth.py      - 2FA implementation
✓ api/auth.py             - API authentication
```

### 2.2 Authorization & Access Control Files

```
✓ tier_gating.py          - Tier-based access control
✓ api_middleware.py       - API middleware (14,915 bytes)
✓ usage_meter.py          - Usage tracking (20,182 bytes)
✓ api_usage_metering.py   - API metering (39,191 bytes)
✓ free_tier_*.py          - Free tier restrictions (5 files)
```

### 2.3 Security-Related Files

```
✓ security_audit.py       - Security auditing
✓ ai_security.py          - AI security (11,178 bytes)
✓ data_rights.py          - Data rights management (16,928 bytes)
✓ SECURITY.md             - Security documentation
⚠️ .env                   - **CONTAINS SECRETS** (should not be in repo)
```

### 2.4 Audit & Logging Files

```
✓ AuditLog model          - In models (needs verification)
✓ user_analytics.py       - User analytics (6,480 bytes)
✓ analytics_tracking.py   - Analytics (10,335 bytes)
```

---

## 3. IDENTITY & ROLE REFERENCE POINTS

### 3.1 User Identity Establishment Points

**Primary Authentication**:

```python
# Location: auth_routes.py
@auth_bp.route("/login", methods=["POST"])
def login():
    # Uses Flask-Login
    login_user(user)
    session["user_id"] = user.id  # ⚠️ NEEDS VERIFICATION
```

**Session Management**:

```python
# Flask-Login integration
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**Current User Access**:

```python
# Throughout app.py
from flask_login import current_user, login_required

@app.route("/dashboard")
@login_required
def dashboard():
    # current_user is available here
```

### 3.2 Tier/Role Reference Points

**Tier Enforcement Decorators** (from `tier_gating.py`):

1. **`@require_tier(TierLevel.X)`**
   - Checks: `session["user_id"]` exists
   - Queries: `User.query.get(session["user_id"])`
   - Compares: `user.tier` against `minimum_tier`
   - Returns: 401 if not logged in, 403 if insufficient tier

2. **`@check_usage_limit(limit_field, increment)`**
   - Checks: `session["user_id"]` exists
   - Queries: `User.query.get(session["user_id"])`
   - Gets: `user.get_tier_limits()`
   - Tracks: `UsageTracking.get_or_create_current(user.id)`
   - Increments: Usage counters
   - Returns: 403 if limit exceeded

3. **`@require_feature(feature_name)`**
   - Checks: `session["user_id"]` exists
   - Queries: `User.query.get(session["user_id"])`
   - Checks: Feature availability in tier limits
   - Returns: 403 if feature not available

**Usage in app.py**:

```python
@app.route("/api/upload", methods=["POST"])
@login_required
@require_tier(TierLevel.STARTER)
@check_usage_limit("bwc_videos_per_month", increment=1)
def upload_file():
    # Protected endpoint
```

### 3.3 Limit Check Points

**Identified Limit Checks**:

1. **Upload Endpoints**:
   - `/api/upload` - BWC videos (STARTER tier, usage limit)
   - `/api/upload/pdf` - PDF documents (STARTER tier, usage limit)
   - `/api/upload/pdf/batch` - Batch PDFs (STARTER tier, usage limit)
   - `/api/upload/pdf/secure` - Secure PDFs (STARTER tier, usage limit)
   - `/api/upload/video` - Videos (STARTER tier, usage limit)

2. **Analysis Endpoints**:
   - `/api/workspace/analyze` - Evidence analysis (PROFESSIONAL tier)
   - `/api/workspace/execute-workflow` - Workflows (PROFESSIONAL tier)

3. **Usage Tracking**:
   - `UsageTracking` model tracks:
     - `pdf_documents_processed`
     - `bwc_videos_processed`
     - `bwc_video_hours_used`
     - `transcription_minutes_used`
     - `api_calls_made`
     - `cases_created`

---

## 4. CRITICAL FINDINGS - PHASE 1

### 🔴 CRITICAL SECURITY ISSUES

1. **`.env` FILE IN REPOSITORY**
   - **File**: `.env` (1,619 bytes)
   - **Risk**: Contains actual secrets (API keys, database URLs, etc.)
   - **Evidence**: File exists in repository root
   - **Impact**: All secrets exposed if repository is compromised

2. **SESSION-BASED AUTHENTICATION ONLY**
   - **Evidence**: `session["user_id"]` used in `tier_gating.py`
   - **Risk**: Session fixation, session hijacking
   - **No Evidence Found**: JWT validation, token expiry, refresh tokens

3. **TIER ENFORCEMENT RELIES ON SESSION**
   - **Location**: `tier_gating.py` lines 28-33
   - **Code**:
     ```python
     if "user_id" not in session:
         return jsonify({"error": "Authentication required"}), 401
     user = User.query.get(session["user_id"])
     ```
   - **Risk**: If session is compromised, tier can be bypassed

### ⚠️ HIGH-RISK ISSUES

4. **NO EVIDENCE OF RATE LIMITING**
   - **Searched**: No rate limiting decorators found
   - **Impact**: API abuse, DoS attacks possible

5. **USAGE LIMITS CAN BE BYPASSED**
   - **Evidence**: Line 114-116 in `tier_gating.py`:
     ```python
     if not usage_field:
         print(f"⚠️ Unknown limit field: {limit_field}")
         return f(*args, **kwargs)  # ⚠️ ALLOWS ACCESS
     ```
   - **Risk**: Unknown limit fields allow unrestricted access

6. **CLIENT-SIDE TIER CHECKS POSSIBLE**
   - **Evidence**: `TierGate.can_access_feature()` available in templates
   - **Risk**: Client can see tier restrictions, may attempt bypass

### 📋 NEEDS VERIFICATION

7. **STRIPE WEBHOOK VALIDATION**
   - **Files Found**: `stripe_subscription_service.py`, `stripe_payment_service.py`
   - **Status**: Need to verify webhook signature validation

8. **CROSS-USER DATA ACCESS**
   - **Evidence**: Analysis queries like:
     ```python
     analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
     ```
   - **Status**: Appears correct but needs full audit

9. **ADMIN PRIVILEGE ESCALATION**
   - **Evidence**: Multiple admin check patterns:
     ```python
     if not current_user.is_admin:
     if current_user.tier != TierLevel.ADMIN:
     ```
   - **Status**: Need to verify consistency

---

## 5. ATTACK SURFACE SUMMARY

### Entry Points Requiring Authentication

- 50+ routes with `@login_required`
- 10+ routes with `@require_tier()`
- 8+ routes with `@check_usage_limit()`

### Entry Points WITHOUT Tier Checks

- Multiple `/api/` endpoints only have `@login_required`
- Need full enumeration in Phase 2

### Data Flow

```
Client Request
    ↓
Flask Route (@login_required)
    ↓
Session Check (Flask-Login)
    ↓
Tier Check (@require_tier) [OPTIONAL]
    ↓
Usage Limit Check (@check_usage_limit) [OPTIONAL]
    ↓
Business Logic
    ↓
Database Query (user_id filter)
    ↓
Response
```

---

## NEXT STEPS: PHASE 2

Phase 2 will analyze:

1. Authentication implementation details
2. Session management security
3. Token validation (if any)
4. Identity spoofing vectors
5. Server-side vs client-side enforcement

**Status**: PHASE 1 COMPLETE - Proceeding to PHASE 2
