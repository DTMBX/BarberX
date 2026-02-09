# Evident Authentication & Dashboard System - Complete Documentation

## Overview

This is a professional-grade authentication and dashboard system for the Evident platform, featuring:

- ✅ User registration with email validation
- ✅ Secure login with password hashing (bcrypt)
- ✅ Password reset functionality
- ✅ Profile management
- ✅ Role-based access control (RBAC)
- ✅ Subscription tier system (Free, Pro, Enterprise)
- ✅ Admin dashboard with user management
- ✅ Comprehensive audit logging
- ✅ API token management
- ✅ Usage tracking and limits
- ✅ Two-factor authentication support (foundation)
- ✅ Mobile-responsive design
- ✅ Dark mode support

---

## Architecture

### Database Models

#### User

Core user account model with authentication and profile data.

**Fields:**

- `id` - Primary key
- `email` - Unique email address (indexed)
- `username` - Unique username (indexed)
- `full_name` - Display name
- `organization` - User's organization
- `password_hash` - Hashed password
- `role` - User role (admin, moderator, pro_user, user)
- `tier` - Subscription tier (free, pro, enterprise, admin)
- `is_active` - Account status
- `is_verified` - Email verification status
- `is_deleted` - Soft delete flag
- `avatar_url` - Profile picture URL
- `bio` - User biography
- `two_factor_enabled` - 2FA flag
- `two_factor_secret` - 2FA secret key
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp
- `last_login` - Last login timestamp
- `last_login_ip` - Last login IP address

**Methods:**

- `set_password(password)` - Hash and store password
- `check_password(password)` - Verify password
- `get_tier_limits()` - Get feature limits for tier
- `update_last_login(ip_address)` - Track login
- `log_action(action, details, ip_address)` - Create audit log
- `to_dict(include_sensitive)` - Convert to dict

**Properties:**

- `is_admin` - Check if admin role
- `is_moderator` - Check if moderator or admin
- `is_pro` - Check if pro tier or higher

#### ApiToken

API tokens for programmatic access and rate limiting.

**Fields:**

- `id` - Primary key
- `token` - Unique token (indexed)
- `name` - Token name
- `user_id` - Foreign key to User
- `is_active` - Active status
- `last_used_at` - Last usage timestamp
- `created_at` - Creation timestamp
- `expires_at` - Expiration timestamp

**Methods:**

- `generate_token()` - Generate secure token
- `is_valid()` - Check if valid and not expired
- `record_usage()` - Update last used time

#### AuditLog

Complete audit trail of all user actions.

**Fields:**

- `id` - Primary key
- `user_id` - Foreign key to User
- `action` - Action name
- `resource_type` - Type of resource (optional)
- `resource_id` - ID of resource (optional)
- `details` - JSON details object
- `ip_address` - Client IP
- `user_agent` - User agent string
- `status` - Result status (success, failure, warning)
- `error_message` - Error message if failed
- `created_at` - Timestamp (indexed)

**Methods:**

- `to_dict()` - Convert to dictionary

#### UsageRecord

Track user API usage for billing and limits.

**Fields:**

- `id` - Primary key
- `user_id` - Foreign key to User
- `metric` - Metric name (api_calls, storage_gb, etc)
- `quantity` - Quantity used
- `period_start` - Period start date
- `period_end` - Period end date
- `cost` - Cost in dollars
- `created_at` - Record creation timestamp

---

## API Routes

### Authentication Routes

#### Register

```
GET/POST /auth/register
```

Create new user account.

**GET Response:**
Returns registration form.

**POST Parameters:**

- `email` - User email
- `username` - Unique username (3+ chars)
- `full_name` - Full name
- `organization` - Organization (optional)
- `password` - Password (8+ chars)
- `password_confirm` - Password confirmation

**Success:**
Redirects to login page with success message.

**Errors:**

- Invalid email format
- Email already registered
- Username too short or taken
- Password too short or mismatch
- Invalid organization name

#### Login

```
GET/POST /auth/login
```

Authenticate user and create session.

**POST Parameters:**

- `email` - User email
- `password` - User password
- `remember` - Remember for 30 days (optional)

**Success:**
Creates session and redirects to dashboard.

**Errors:**

- Email not found
- Account disabled
- Invalid password

#### Logout

```
GET /auth/logout
```

Destroy session and logout user.

**Requires:** Authentication

**Response:**
Redirects to login page.

#### Forgot Password

```
GET/POST /auth/forgot-password
```

Request password reset email.

**POST Parameters:**

- `email` - User email

**Response:**
Confirmation message (doesn't reveal if email exists).

#### Reset Password

```
GET/POST /auth/reset-password/<token>
```

Reset password with token from email.

**POST Parameters:**

- `password` - New password (8+ chars)
- `password_confirm` - Password confirmation

**Success:**
Password updated, redirects to login.

**Errors:**

- Invalid or expired token
- Password too short
- Password mismatch

#### Profile

```
GET/POST /auth/profile
```

View and edit user profile.

**Requires:** Authentication

**POST Parameters:**

- `full_name` - Full name
- `organization` - Organization
- `bio` - User bio

**Response:**
Profile page with current info.

#### Change Password

```
GET/POST /auth/change-password
```

Change password for logged-in user.

**Requires:** Authentication

**POST Parameters:**

- `old_password` - Current password
- `new_password` - New password (8+ chars)
- `new_password_confirm` - Confirmation

**Success:**
Password changed, redirects to profile.

**Errors:**

- Current password incorrect
- New password too short
- Password mismatch

---

### User Routes

#### Dashboard

```
GET /dashboard
```

User dashboard with profile and stats.

**Requires:** Authentication

**Response:**
Dashboard page with:

- Account status
- Member since date
- Tier limits
- Profile information
- API key management

---

### API Routes

#### Get Current User

```
GET /auth/api/me
```

Get authenticated user info.

**Requires:** Authentication

**Response (200):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "organization": "Acme Corp",
    "role": "user",
    "tier": "free",
    "is_active": true,
    "is_verified": true,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-02-01T15:45:00Z",
    "last_login": "2026-02-08T09:20:00Z"
  },
  "tier_limits": {
    "api_calls_per_month": 1000,
    "storage_gb": 1,
    "concurrent_uploads": 1,
    "batch_processing": false,
    "custom_models": false
  }
}
```

#### API Logout

```
POST /auth/api/logout
```

Logout via API.

**Requires:** Authentication

**Response (200):**

```json
{
  "success": true,
  "message": "Logged out"
}
```

---

### Admin Routes

#### Admin Dashboard

```
GET /admin/
```

Admin overview with statistics.

**Requires:** Admin role

**Response:**
Admin dashboard with:

- Total users count
- Active users count
- Verified users count
- Tier breakdown
- Subscription analytics
- Recent activity log

#### Users List

```
GET /admin/users
```

List all users with filtering and pagination.

**Requires:** Admin role

**Query Parameters:**

- `page` - Page number (default: 1)
- `search` - Search by email/name
- `tier` - Filter by tier (free, pro, enterprise)
- `role` - Filter by role (admin, moderator, pro_user, user)
- `status` - Filter by status (active, inactive, unverified)

**Response:**
Users list page with search and filters.

#### Edit User

```
GET/POST /admin/users/<user_id>
```

View and edit specific user.

**Requires:** Admin role

**POST Parameters:**

- `full_name` - User full name
- `organization` - User organization
- `role` - User role
- `tier` - Subscription tier
- `is_active` - Active status (checkbox)
- `is_verified` - Verified status (checkbox)

**Response (GET):**
User edit page with activity log.

**Response (POST):**
Redirects to user page with success message.

**Errors:**

- User not found (404)
- Invalid role or tier
- Cannot edit your own account

#### Toggle User Status

```
POST /admin/users/<user_id>/toggle-status
```

Enable or disable user account.

**Requires:** Admin role

**Response (200):**

```json
{
  "success": true,
  "message": "User enabled",
  "is_active": true
}
```

**Errors:**

- Cannot disable your own account (400)

#### Reset User Password

```
POST /admin/users/<user_id>/reset-password
```

Admin reset user password.

**Requires:** Admin role

**Response (200):**

```json
{
  "success": true,
  "temp_password": "random_secure_password"
}
```

#### Delete User

```
POST /admin/users/<user_id>/delete
```

Soft-delete user account.

**Requires:** Admin role

**Response:**
Redirects with success message.

**Errors:**

- Cannot delete your own account (400)

---

### Admin API Endpoints

#### Get Statistics

```
GET /admin/api/stats
```

Get platform statistics.

**Requires:** Admin role

**Response (200):**

```json
{
  "total_users": 156,
  "active_users": 142,
  "verified_users": 138,
  "tier_breakdown": {
    "free": 120,
    "pro": 32,
    "enterprise": 4,
    "admin": 0
  },
  "timestamp": "2026-02-08T15:30:00Z"
}
```

#### Get User

```
GET /admin/api/users/<user_id>
```

Get specific user details.

**Requires:** Admin role

**Response (200):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "role": "user",
    "tier": "free",
    ...
  }
}
```

#### Update User

```
PUT /admin/api/users/<user_id>
```

Update user via API.

**Requires:** Admin role

**JSON Parameters:**

```json
{
  "full_name": "Jane Doe",
  "tier": "pro",
  "role": "pro_user",
  "is_active": true
}
```

**Response (200):**

```json
{
  "success": true,
  "user": {...}
}
```

#### Delete User (API)

```
DELETE /admin/api/users/<user_id>
```

Delete user via API.

**Requires:** Admin role

**Response (200):**

```json
{
  "success": true,
  "message": "User deleted"
}
```

#### Get Audit Logs

```
GET /admin/api/audit-logs
```

Get audit logs with filtering.

**Requires:** Admin role

**Query Parameters:**

- `page` - Page number (default: 1)
- `user_id` - Filter by user
- `action` - Filter by action

**Response (200):**

```json
{
  "total": 500,
  "pages": 10,
  "current_page": 1,
  "logs": [
    {
      "id": 1,
      "user_id": 5,
      "action": "user_login",
      "resource_type": null,
      "resource_id": null,
      "details": {"remember_me": false},
      "status": "success",
      "created_at": "2026-02-08T15:30:00Z"
    },
    ...
  ]
}
```

---

## Decorators

### @login_required

Require user to be authenticated.

```python
from flask_login import login_required

@app.route('/protected')
@login_required
def protected():
    return f"Hello, {current_user.full_name}!"
```

### @admin_required

Require admin role.

```python
from auth.models import admin_required

@app.route('/admin-only')
@admin_required
def admin_only():
    return "Admin access granted"
```

### @moderator_required

Require moderator or admin role.

```python
from auth.models import moderator_required

@app.route('/moderate')
@moderator_required
def moderate():
    return "Moderation powers activated"
```

### @tier_required

Require specific subscription tier.

```python
from auth.models import tier_required, TierLevel

@app.route('/premium-feature')
@tier_required(TierLevel.PRO)
def premium_feature():
    return "Premium feature"
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install flask-login flask-sqlalchemy email-validator python-dotenv
```

### 2. Create Flask App

```python
# app.py
import os
from flask import Flask
from flask_login import LoginManager
from auth import db, User, auth_bp, admin_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///Evident.db'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-only')

# Initialize
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Create Admin User

```python
from auth.models import User, UserRole, TierLevel

with app.app_context():
    admin = User(
        email='admin@Evident.info',
        username='admin',
        full_name='System Administrator',
        role=UserRole.ADMIN,
        tier=TierLevel.ADMIN,
        is_verified=True,
        is_active=True,
    )
    admin.set_password('secure_password_here')
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin created")
```

### 4. Environment Variables

```bash
# .env
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///Evident.db
FLASK_ENV=production
DEBUG=False
```

### 5. Run Flask

```bash
flask run
```

Access the system:

- Login: http://localhost:5000/auth/login
- Register: http://localhost:5000/auth/register
- Dashboard: http://localhost:5000/dashboard
- Admin: http://localhost:5000/admin/

---

## Security Best Practices

1. **Passwords**
   - Minimum 8 characters
   - Hashed with werkzeug.security
   - Never stored in plaintext

2. **Email**
   - Validated with email-validator
   - Can require verification before access

3. **Sessions**
   - HTTP-only cookies
   - Secure flag in production
   - Configurable timeout

4. **Audit Logging**
   - All actions logged
   - IP address tracking
   - User agent logging
   - Status and error tracking

5. **Access Control**
   - Role-based (admin, moderator, user)
   - Tier-based (free, pro, enterprise)
   - Route-level enforcement

6. **API Tokens**
   - Secure token generation
   - Expiration support
   - Usage tracking
   - Can be revoked

7. **Production**
   - Use PostgreSQL (not SQLite)
   - Enable HTTPS/TLS
   - Set strong SECRET_KEY
   - Use environment variables
   - Configure CORS properly
   - Enable rate limiting
   - Monitor audit logs
   - Regular backups

---

## Tier System

### Free

- 1,000 API calls/month
- 1 GB storage
- 1 concurrent upload
- No batch processing
- No custom models

### Pro

- 100,000 API calls/month
- 100 GB storage
- 5 concurrent uploads
- Batch processing enabled
- No custom models

### Enterprise

- Unlimited API calls
- Unlimited storage
- Unlimited concurrent uploads
- Batch processing enabled
- Custom models enabled

### Admin

- Full system access
- All features unlocked
- Can manage users
- Can view audit logs
- Can change tiers

---

## Troubleshooting

### "Admin access required"

**Cause:** User doesn't have admin role

**Solution:**

```python
with app.app_context():
    user = User.query.filter_by(email='user@example.com').first()
    user.role = UserRole.ADMIN
    db.session.commit()
```

### "Email not found"

**Cause:** User not registered

**Solution:** Register at `/auth/register`

### "Account is disabled"

**Cause:** User marked as inactive

**Solution:** Admin can re-enable at `/admin/users/<id>`

### Database errors

**Cause:** Tables not created

**Solution:**

```python
with app.app_context():
    db.create_all()
```

### CSRF errors

**Cause:** CSRF protection enabled

**Solution:** Include `{{ csrf_token() }}` in forms

### Session lost

**Cause:** SECRET_KEY changed or session expired

**Solution:** Clear cookies and re-login

---

## File Structure

```
Evident/
├── auth/
│   ├── __init__.py           # Package init
│   ├── models.py             # Database models
│   ├── routes.py             # Auth routes
│   ├── admin_routes.py       # Admin routes
│   └── INTEGRATION_GUIDE.py  # Setup guide
│
├── templates/
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── change_password.html
│   │   └── forgot_password.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users_list.html
│   │   └── edit_user.html
│   └── dashboard.html
│
├── static/
│   ├── css/
│   │   ├── design-tokens.css
│   │   ├── components.css
│   │   └── utilities.css
│   └── js/
│       ├── theme.js
│       └── navigation.js
│
└── app.py                     # Main Flask app
```

---

## Support & Documentation

- See `AUTH_INTEGRATION.md` for step-by-step integration
- See `api/API-REFERENCE.md` for complete API documentation
- Check audit logs for debugging: `AuditLog.query.all()`
- Monitor user activity: `User.query.all()`

---

**Created:** February 2026  
**Version:** 1.0  
**Status:** Production Ready  
**License:** See LICENSE.md
