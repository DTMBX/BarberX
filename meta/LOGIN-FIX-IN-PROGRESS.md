# CRITICAL FIX: Admin Login Not Working

## Root Causes Found

### 1. Database Path Mismatch ❌

**Problem**: App configuration says to use `Evident_FRESH.db` but something is
changing it to `Evident_test.db`

**File**: `app.py` Line 224

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Evident_FRESH.db"
```

**But diagnostic shows**: `sqlite:///Evident_test.db`

**Solution**: Force the correct database path

### 2. POST Login Returns 400 ❌

**Problem**: Login form POST request returns HTTP 400 (Bad Request)

- Likely cause: Missing CSRF token
- Or: Form validation failing

## Quick Fix

Run this in PowerShell:

```powershell
# 1. Set admin password
$env:Evident_ADMIN_PASSWORD = "pQWN6CUNH04Gx6Ud73dfybu6jiV_DM4s"

# 2. Create admin in the CORRECT database
cd c:\web-dev\github-repos\Evident.info
python create_admin_fixed.py

# 3. Start Flask app
python app.py
```

Then test login at: **http://localhost:5000/auth/login**

## Diagnostic Results

✅ Password verification: SUCCESS  
✅ Admin user found in database  
✅ Login page accessible (GET /auth/login: 200)  
❌ Login POST returns 400 (CSRF or form validation issue)

## Next Steps

1. **Fix database path** - ensure app uses `Evident_FRESH.db`
2. **Fix CSRF token** - check if login form includes CSRF token
3. **Check form fields** - ensure form has correct field names (email, password)

## Files to Check

1. `app.py` - Database configuration
2. `templates/auth/login.html` - Login form with CSRF token
3. `auth_routes.py` - Login route POST handler

## Admin Credentials

**Email**: admin@Evident.info  
**Password**: pQWN6CUNH04Gx6Ud73dfybu6jiV_DM4s  
**Tier**: ADMIN ($9999/mo)  
**Status**: Active ✅  
**Verified**: True ✅

---

**Created**: January 31, 2026 19:42  
**Status**: IN PROGRESS - Debugging database path and CSRF issues
