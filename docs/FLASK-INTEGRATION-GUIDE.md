# Flask Integration Guide — Authentication Enhancement

## Current State Analysis

### Existing `app.py` Has:

- ✅ Flask app initialized
- ✅ SQLAlchemy database setup
- ✅ Flask-Login configured
- ✅ User model with basic authentication
- ✅ Login/register routes (`/login`, `/register`)
- ✅ Dashboard route (`/dashboard`)
- ✅ Tier system (free, professional, enterprise)
- ✅ Usage limits per tier

### New `auth_routes.py` & `models_auth.py` Provide:

- ✅ Enhanced User model with more fields
- ✅ UsageTracking model for monthly stats
- ✅ ApiKey model for tier-based access
- ✅ Authorization decorators (@admin_required, @tier_required,
  @feature_required)
- ✅ Rate limiting on routes
- ✅ Optimized login/signup/dashboard templates
- ✅ Password strength requirements
- ✅ Tier-based feature gates

--

## Integration Strategy

### Option A: Replace with Enhanced System (Recommended)

**Pros:**

- More robust tier system
- Better usage tracking
- Cleaner decorators
- Optimized UI templates
- Monthly usage reset
- API key management

**Cons:**

- Need to migrate existing database
- Need to update existing routes

### Option B: Keep Current System

**Pros:**

- No migration needed
- Existing code works

**Cons:**

- Less feature-rich
- No monthly usage tracking
- No API key system

### Option C: Hybrid Approach (Quickest)

**Pros:**

- Keep existing database model
- Just swap templates for better UI
- Add decorators incrementally

**Cons:**

- Less unified architecture

--

## Recommended: Option A (Enhanced System)

### Step 1: Backup Current Database

```bash
cp instance/Evident_legal.db instance/Evident_legal.db.backup
```

### Step 2: Update `app.py` Imports

Replace lines 5-8 with:

```python
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from models_auth import db, User, UsageTracking, ApiKey, TierLevel
from auth_routes import auth_bp, init_auth
```

### Step 3: Replace User Model Section

**Remove:** Lines 71-164 (old User model)

**Replace with:** Import from `models_auth.py` (already done in Step 2)

### Step 4: Initialize Enhanced Auth System

After line 46 (`login_manager.login_view = 'login'`), add:

```python
# Initialize enhanced authentication
init_auth(app)

# Register auth blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')
```

### Step 5: Update Existing Routes

#### Update Login Route (line 396)

**Remove old `/login` route**

**Add redirect:**

```python
@app.route('/login')
def login_redirect():
    """Redirect to new auth system"""
    return redirect(url_for('auth.login'))
```

#### Update Register Route (line 354)

**Remove old `/register` route**

**Add redirect:**

```python
@app.route('/register')
def register_redirect():
    """Redirect to new auth system"""
    return redirect(url_for('auth.signup'))
```

#### Update Dashboard Route (line 436)

**Replace with:**

```python
@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with usage stats"""
    usage = UsageTracking.get_or_create_current(current_user.id)
    limits = current_user.get_tier_limits()
    return render_template('auth/dashboard.html',
                         user=current_user,
                         usage=usage,
                         limits=limits)
```

### Step 6: Add User Loader

Make sure this exists after line 48:

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

### Step 7: Update Database Schema

Run migration script:

```python
# migration.py
from app import app, db
from models_auth import User, UsageTracking, ApiKey

with app.app_context():
    # Create all tables (new schema)
    db.create_all()

    print("✅ Database schema updated")
    print("✅ New tables: users, usage_tracking, api_keys")
```

Run:

```bash
python migration.py
```

### Step 8: Create Admin Account

```bash
python init_auth.py
```

This creates:

- Admin account: admin@Evident.info / (set via ADMIN_PASSWORD env var)
- 3 test users (free, pro, premium tiers)

--

## Quick Integration (Just UI Swap)

If you want to keep the current system but use the new templates:

### Update Template Paths Only

#### In `/login` route:

```python
return render_template('auth/login.html')  # instead of 'login.html'
```

#### In `/register` route:

```python
return render_template('auth/signup.html')  # instead of 'register.html'
```

#### In `/dashboard` route:

```python
return render_template('auth/dashboard.html', user=current_user)
```

### Copy Template Variables

Make sure to pass these to templates:

**login.html needs:**

- Flash messages for errors

**signup.html needs:**

- `tiers` list (optional, can be hardcoded in template)

**dashboard.html needs:**

- `user` object with tier info
- `usage` object with current counts
- `limits` dict with tier limits

--

## Testing After Integration

### 1. Test Auth Routes

```bash
# Start server
python app.py

# Open browser
http://localhost:5000/auth/signup
http://localhost:5000/auth/login
http://localhost:5000/dashboard
```

### 2. Test Signup Flow

1. Go to `/auth/signup`
2. Fill in form with tier selection
3. Submit
4. Verify redirect to `/auth/login`
5. Login with new credentials
6. Verify dashboard shows correctly

### 3. Test Admin Account

1. Login as admin (admin@Evident.info / (set via ADMIN_PASSWORD env var))
2. Verify admin tier shows in dashboard
3. Check unlimited usage limits
4. Test backend tools access

### 4. Test Tier Limits

1. Login as free tier user
2. Process 2 BWC videos
3. Try 3rd video
4. Verify limit warning shows

### 5. Test Usage Tracking

1. Login and process a video
2. Check dashboard shows updated counts
3. Verify progress bars reflect usage

--

## Route Migration Table

| Old Route    | New Route               | Status                 |
| ------------ | ----------------------- | ---------------------- |
| `/login`     | `/auth/login`           | ✅ Redirect or replace |
| `/register`  | `/auth/signup`          | ✅ Redirect or replace |
| `/logout`    | `/auth/logout`          | ✅ Blueprint handles   |
| `/dashboard` | `/dashboard`            | ✅ Enhanced template   |
| -            | `/auth/forgot-password` | ⏳ Future feature      |
| -            | `/auth/reset-password`  | ⏳ Future feature      |

--

## Template Files

### Available Templates:

- ✅ `templates/auth/login.html` — Optimized login with animations
- ✅ `templates/auth/signup.html` — Signup with tier selection
- ✅ `templates/auth/dashboard.html` — Dashboard with usage stats

### Old Templates (Can Remove):

- ⚠️ `templates/login.html` (if exists)
- ⚠️ `templates/register.html` (if exists)
- ⚠️ `templates/dashboard.html` (if exists in root)

--

## Environment Variables

Add to `.env` or set in environment:

```bash
# Flask
SECRET_KEY=your-super-secret-random-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///instance/Evident_auth.db
# For production: postgresql://user:pass@host:5432/Evident

# Mail (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379
```

--

## Production Checklist

Before deploying:

### Security:

- [ ] Change `SECRET_KEY` to secure random value
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags (`SESSION_COOKIE_SECURE=True`)
- [ ] Enable CSRF protection
- [ ] Add security headers (helmet)
- [ ] Rate limit login attempts (already in auth_routes)

### Database:

- [ ] Switch from SQLite to PostgreSQL
- [ ] Set up database backups
- [ ] Add database connection pooling
- [ ] Enable query logging

### Performance:

- [ ] Add Redis for session storage
- [ ] Enable Gzip compression
- [ ] Set up CDN for static files
- [ ] Add caching headers

### Monitoring:

- [ ] Add error tracking (Sentry)
- [ ] Set up logging aggregation
- [ ] Add uptime monitoring
- [ ] Configure alerting

--

## Rollback Plan

If integration causes issues:

### 1. Restore Database:

```bash
cp instance/Evident_legal.db.backup instance/Evident_legal.db
```

### 2. Revert app.py:

```bash
git checkout app.py
```

### 3. Restart Server:

```bash
python app.py
```

--

## Summary

### Files to Modify:

1. ✅ `app.py` — Add imports, register blueprint, update routes
2. ✅ `models_auth.py` — Already created (enhanced models)
3. ✅ `auth_routes.py` — Already created (enhanced routes)
4. ✅ Templates — Already created (optimized UI)

### Files to Create:

5. ⏳ `migration.py` — Database migration script
6. ⏳ `.env` — Environment variables

### Steps:

1. Backup database
2. Update imports in app.py
3. Register auth blueprint
4. Update route handlers
5. Run database migration
6. Create admin account
7. Test all flows
8. Deploy

### Estimated Time:

- Integration: 30 minutes
- Testing: 20 minutes
- Documentation: 10 minutes
- **Total: 1 hour**

--

**Status:** Ready for integration  
**Risk Level:** Low (can rollback easily)  
**Benefit:** Major UI/UX improvement + better tier system

💈✂️ Let's integrate like a clean fade — smooth transitions!
