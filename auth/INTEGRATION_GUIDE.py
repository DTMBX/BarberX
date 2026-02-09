"""
Evident Authentication Integration Guide
Step-by-step integration into existing Flask app
"""

INTEGRATION_STEPS = """
# Evident Authentication System - Integration Guide

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
pip install flask-login flask-sqlalchemy email-validator python-dotenv
```

### 2. Add to your app.py

```python
from flask import Flask
from flask_login import LoginManager
from auth.models import db, User
from auth.routes import auth_bp
from auth.admin_routes import admin_bp

# Initialize app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Evident.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Initialize database
db.init_app(app)

# Initialize Flask-Login
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
```

### 3. Create Admin User

```python
from auth.models import User, UserRole, TierLevel

with app.app_context():
    admin = User.query.filter_by(email='admin@Evident.info').first()
    if not admin:
        admin = User(
            email='admin@Evident.info',
            username='admin',
            full_name='System Administrator',
            role=UserRole.ADMIN,
            tier=TierLevel.ADMIN,
            is_verified=True,
            is_active=True,
        )
        admin.set_password('your_secure_password_here')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created')
```

### 4. Restart Flask

The system is now ready!

## Routes Available

### Authentication Routes
- GET/POST `/auth/register` - Register new account
- GET/POST `/auth/login` - Login
- GET `/auth/logout` - Logout
- GET/POST `/auth/forgot-password` - Request password reset
- GET/POST `/auth/reset-password/<token>` - Reset password
- GET/POST `/auth/profile` - User profile
- GET/POST `/auth/change-password` - Change password

### Dashboard Routes
- GET `/dashboard` - User dashboard (requires login)
- POST `/api/me` - Get current user (JSON API)

### Admin Routes
- GET `/admin/` - Admin dashboard (requires admin role)
- GET `/admin/users` - User management
- GET/POST `/admin/users/<id>` - Edit user
- POST `/admin/users/<id>/toggle-status` - Enable/disable user
- POST `/admin/users/<id>/reset-password` - Admin password reset
- POST `/admin/users/<id>/delete` - Delete user

## API Endpoints

### Authentication
```
POST /auth/api/logout
GET  /auth/api/me
```

### Admin
```
GET  /admin/api/stats
GET  /admin/api/users/<id>
PUT  /admin/api/users/<id>
DELETE /admin/api/users/<id>
GET  /admin/api/audit-logs
```

## Models

### User
- id, email, username, full_name, organization
- password_hash, is_active, is_verified, is_deleted
- role (admin, moderator, pro_user, user)
- tier (free, pro, enterprise, admin)
- avatar_url, bio, two_factor_enabled
- created_at, updated_at, last_login, last_login_ip

### ApiToken
- id, token, name, user_id
- is_active, last_used_at, created_at, expires_at

### AuditLog
- id, user_id, action, resource_type, resource_id
- details (JSON), ip_address, user_agent, status, error_message
- created_at

### UsageRecord
- id, user_id, metric, quantity
- period_start, period_end, cost
- created_at

## Decorators Available

### Require Authentication
```python
@login_required
```

### Require Admin Role
```python
from auth.models import admin_required

@admin_required
def admin_function():
    ...
```

### Require Moderator Role
```python
from auth.models import moderator_required

@moderator_required
def moderate_function():
    ...
```

### Require Specific Tier
```python
from auth.models import tier_required, TierLevel

@tier_required(TierLevel.PRO)
def pro_feature():
    ...
```

## Security Features

1. **Password Hashing**: Using werkzeug.security
2. **CSRF Protection**: Enable in Flask
3. **Rate Limiting**: Add flask-limiter for production
4. **Two-Factor Auth**: Foundation in place (two_factor_secret)
5. **Audit Logging**: All actions logged to database
6. **Role-Based Access Control**: Enforced at route level
7. **Session Management**: Flask-Login integrated
8. **Password Requirements**: Minimum 8 characters
9. **Email Validation**: Using email-validator package
10. **API Key Management**: Secure token generation

## Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key-here

# Optional
SQLALCHEMY_DATABASE_URI=sqlite:///Evident.db
FLASK_ENV=production
DEBUG=False
```

## Production Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Set FLASK_ENV=production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set up email for password resets
- [ ] Configure password reset email templates
- [ ] Set up rate limiting on auth endpoints
- [ ] Enable two-factor authentication
- [ ] Configure backup strategy for database
- [ ] Set up monitoring for failed login attempts
- [ ] Configure logging to external service
- [ ] Regular security audits of audit logs
- [ ] Set password expiration policy
- [ ] Configure session timeout
- [ ] Use environment variables for secrets
- [ ] Deploy behind reverse proxy (nginx, etc)

## Troubleshooting

### "Admin access required"
- User account must have role=UserRole.ADMIN

### "Email not found"
- User email must be registered and not marked as is_deleted

### "Account is disabled"
- User.is_active must be True

### "Password is too short"
- Minimum 8 characters required

### Database errors
- Run: `with app.app_context(): db.create_all()`

## File Structure

```
auth/
├── __init__.py
├── models.py          # User, ApiToken, AuditLog, UsageRecord
├── routes.py          # Auth routes (login, register, profile)
└── admin_routes.py    # Admin routes (user management, stats)

templates/
├── auth/
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── change_password.html
├── admin/
│   ├── dashboard.html
│   └── users_list.html
└── dashboard.html     # User dashboard

static/
├── css/
│   ├── design-tokens.css
│   ├── components.css
│   └── utilities.css
└── js/
    ├── theme.js
    └── navigation.js
```

## Upgrading from Old System

If you have an existing authentication system:

1. Backup database: `cp instance/app.db instance/app.db.backup`
2. Migration script: Create one to move user data
3. Test routes: Verify old endpoints still work
4. Update references: Update any hardcoded URLs to new routes
5. Test admin features: Verify admin can manage users
6. Monitor logs: Watch audit logs for errors

## Support

For issues or questions, check:
- SECURITY.md - Security best practices
- API-REFERENCE.md - Full API documentation
- Audit logs - Check AuditLog for error details
"""

if __name__ == '__main__':
    print(INTEGRATION_STEPS)
    print("\n" + "="*80)
    print("Save this integration guide to AUTH_INTEGRATION.md")
    print("="*80)
