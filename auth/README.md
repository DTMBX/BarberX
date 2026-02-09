# Evident Authentication & Dashboard System

> Professional-grade authentication and user management system for Evident platform

## ✨ Features

- **User Authentication** - Secure login, registration, and password reset
- **Admin Dashboard** - Manage users, view statistics, monitor activity
- **User Dashboard** - Profile management, API keys, usage tracking
- **Role-Based Access** - Admin, moderator, pro user, and user roles
- **Subscription Tiers** - Free, Pro, Enterprise, and Admin tiers
- **Audit Logging** - Complete action history with IP tracking
- **API Management** - Generate and manage API tokens
- **Security First** - Bcrypt hashing, session management, CSRF protection

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install flask-login flask-sqlalchemy email-validator python-dotenv
```

### 2. Setup Flask App

```python
from app_config import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Initialize Database

```bash
flask init-db
```

### 4. Create Admin User

```bash
flask create-admin
```

### 5. Run Application

```bash
flask run
```

Access at: http://localhost:5000

## 📁 Project Structure

```
auth/
├── __init__.py              # Package initialization
├── models.py                # Database models (User, ApiToken, etc)
├── routes.py                # Authentication routes
├── admin_routes.py          # Admin panel routes
└── INTEGRATION_GUIDE.py     # Integration instructions

templates/
├── auth/
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── profile.html         # User profile
│   ├── change_password.html # Change password
│   └── forgot_password.html # Password reset request
├── admin/
│   ├── dashboard.html       # Admin overview
│   └── users_list.html      # User management
└── dashboard.html           # User dashboard

docs/
├── AUTH_SYSTEM.md                      # Complete documentation
└── DASHBOARD_AUTH_UPGRADE_SUMMARY.md   # Implementation summary

app_config.py                           # Flask app configuration
```

## 🔐 Routes

### Authentication

- `GET/POST /auth/register` - Register new account
- `GET/POST /auth/login` - Login
- `GET /auth/logout` - Logout
- `GET/POST /auth/profile` - Manage profile
- `GET/POST /auth/change-password` - Change password
- `GET/POST /auth/forgot-password` - Request password reset
- `GET/POST /auth/reset-password/<token>` - Reset password

### User

- `GET /dashboard` - User dashboard

### Admin

- `GET /admin/` - Admin dashboard
- `GET /admin/users` - User management
- `GET/POST /admin/users/<id>` - Edit user
- `POST /admin/users/<id>/toggle-status` - Enable/disable
- `POST /admin/users/<id>/delete` - Delete user

## 🔑 API Endpoints

### Authentication API

```
GET  /auth/api/me              # Get current user
POST /auth/api/logout          # Logout via API
```

### Admin API

```
GET  /admin/api/stats          # Get statistics
GET  /admin/api/users/<id>     # Get user
PUT  /admin/api/users/<id>     # Update user
DELETE /admin/api/users/<id>   # Delete user
GET  /admin/api/audit-logs     # Get audit logs
```

## 👤 User Roles

- **Admin** - Full system access, user management
- **Moderator** - Content moderation capabilities
- **Pro User** - Premium features access
- **User** - Standard user access

## 💰 Subscription Tiers

| Feature          | Free | Pro    | Enterprise | Admin     |
| ---------------- | ---- | ------ | ---------- | --------- |
| API Calls/Month  | 1K   | 100K   | Unlimited  | Unlimited |
| Storage          | 1 GB | 100 GB | Unlimited  | Unlimited |
| Uploads          | 1    | 5      | Unlimited  | Unlimited |
| Batch Processing | ✗    | ✓      | ✓          | ✓         |
| Custom Models    | ✗    | ✗      | ✓          | ✓         |

## 🔐 Security Features

- ✅ Password hashing with bcrypt
- ✅ Email validation
- ✅ Session management
- ✅ CSRF protection
- ✅ Audit logging
- ✅ IP address tracking
- ✅ Account status management
- ✅ Token-based API access
- ✅ Role-based access control

## 📊 Admin Features

### Dashboard

- Real-time user statistics
- Tier distribution breakdown
- Registration trends (7-day)
- Recent activity log
- Verification rate tracking

### User Management

- Search and filter users
- Edit user information
- Change subscription tier
- Assign roles
- Enable/disable accounts
- Force password reset
- View user activity
- Delete users (soft delete)

### Audit Logs

- Complete action history
- Searchable by action type
- Filterable by user
- IP address tracking
- Timestamp indexing

## 🛠️ Configuration

### Environment Variables

```bash
# .env
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///Evident.db
FLASK_ENV=production
DEBUG=False
```

### Database

- SQLite for development
- PostgreSQL for production (recommended)
- SQLAlchemy ORM
- Automatic table creation

## 📚 Documentation

- **Complete Guide**: See `docs/AUTH_SYSTEM.md`
- **Integration**: See `auth/INTEGRATION_GUIDE.py`
- **Implementation Summary**: See `docs/DASHBOARD_AUTH_UPGRADE_SUMMARY.md`

## 🧪 Testing

```bash
# List users
flask list-users

# Create admin user
flask create-admin

# Initialize database
flask init-db
```

## 🚢 Production Deployment

Before deploying:

1. **Database**
   - Use PostgreSQL (not SQLite)
   - Configure connection string
   - Run migrations

2. **Security**
   - Set strong unique SECRET_KEY
   - Enable HTTPS/TLS
   - Configure CORS
   - Enable CSRF protection

3. **Configuration**
   - Set FLASK_ENV=production
   - Disable DEBUG mode
   - Configure logging
   - Setup error tracking

4. **Monitoring**
   - Setup audit log monitoring
   - Configure alerts for failed logins
   - Monitor admin actions
   - Track registration patterns

## 📞 Support

- Check audit logs for debugging
- Review AUTH_SYSTEM.md for comprehensive docs
- Use Flask CLI commands for common tasks
- Monitor application logs

## 📄 License

See LICENSE.md for details.

---

**Status**: ✅ Production Ready  
**Version**: 1.0  
**Last Updated**: February 2026
