# 🚀 Evident Platform - QUICKSTART Guide

## Overview

You now have a complete, production-ready authentication system with:

- ✅ User registration & login
- ✅ Admin dashboard & user management
- ✅ Role-based access control
- ✅ Subscription tier system
- ✅ Audit logging
- ✅ API token management

This guide gets you running in **5 minutes**.

---

## 1️⃣ Initial Setup (1 minute)

### Windows CMD Users

```bash
setup.bat
```

Or with admin creation:

```bash
setup.bat -create-admin
```

### Windows PowerShell Users

```bash
.\setup.ps1
```

### macOS / Linux Users

```bash
chmod +x setup.sh
./setup.sh
```

---

## 2️⃣ Manual Setup (if scripts don't work)

### Step 1: Install Dependencies

```bash
pip install flask-login flask-sqlalchemy email-validator python-dotenv
```

### Step 2: Create .env File

Create `.env` in the root directory:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///Evident.db

# Security (CHANGE IN PRODUCTION)
SECRET_KEY=dev-secret-key-change-in-production
```

### Step 3: Initialize Database

```bash
flask init-db
```

### Step 4: Create Admin User

```bash
flask create-admin
```

You'll be prompted for:

- Email
- Username
- Full Name
- Password

---

## 3️⃣ Start the Server (1 minute)

```bash
python app.py
```

You should see:

```
========================================================
🚀 EVIDENT PLATFORM - Starting...
========================================================

✅ Database: Connected to sqlite:///Evident.db
✅ Config: Development mode with debug enabled

📍 Access the application at:
  🏠 Home:      http://localhost:5000/
  🔐 Login:     http://localhost:5000/auth/login
  📝 Register:  http://localhost:5000/auth/register
  📊 Dashboard: http://localhost:5000/dashboard (login required)
  ⚙️  Admin:     http://localhost:5000/admin/ (admin only)

Press CTRL+C to stop the server
========================================================
```

---

## 🔐 Test the System

### 1. First Time Setup

1. Visit `http://localhost:5000/`
2. Click **"Create Account"** (or go to `/auth/register`)
3. Fill in the registration form:
   - Full Name
   - Email
   - Username
   - Password (8+ characters)
   - Terms acceptance
4. Click **Register**

### 2. Login

1. Go to `http://localhost:5000/auth/login`
2. Use your email and password
3. Check "Remember me" to stay logged in
4. Click **Login**

### 3. View Your Dashboard

- You'll be redirected to `http://localhost:5000/dashboard`
- See your profile info, account tier, limits

### 4. Access Admin Panel (Admin Only)

1. Login as the admin user you created
2. Visit `http://localhost:5000/admin/`
3. Explore admin features:
   - **Dashboard**: Statistics and analytics
   - **Users**: Manage all user accounts
   - **Audit Logs**: View all system activity
   - **API Tokens**: Generate and manage API keys

---

## 📚 Available Commands

```bash
# Start development server
python app.py

# Or use Flask CLI
flask run

# Create admin user (interactive)
flask create-admin

# List all users
flask list-users

# Initialize database (run once)
flask init-db
```

---

## 📍 URL Reference

### Public Pages

| URL                     | Description            |
| ----------------------- | ---------------------- |
| `/`                     | Homepage               |
| `/auth/login`           | User login             |
| `/auth/register`        | User registration      |
| `/auth/forgot-password` | Password reset request |

### Authenticated User Pages

| URL                     | Description        |
| ----------------------- | ------------------ |
| `/dashboard`            | User dashboard     |
| `/auth/profile`         | Profile management |
| `/auth/change-password` | Change password    |

### Admin Pages (Admin Only)

| URL                 | Description     |
| ------------------- | --------------- |
| `/admin/`           | Admin dashboard |
| `/admin/users`      | User management |
| `/admin/users/<id>` | Edit user       |

### API Endpoints

| Endpoint                | Method | Description           |
| ----------------------- | ------ | --------------------- |
| `/auth/api/me`          | GET    | Get current user info |
| `/auth/api/logout`      | POST   | Logout current user   |
| `/admin/api/stats`      | GET    | Get admin statistics  |
| `/admin/api/users/<id>` | GET    | Get user details      |
| `/admin/api/users/<id>` | PUT    | Update user           |
| `/admin/api/users/<id>` | DELETE | Delete user           |
| `/admin/api/audit-logs` | GET    | Get audit logs        |

---

## 🔐 Default User Roles

1. **ADMIN** - Full system access
2. **MODERATOR** - User management & moderation
3. **PREMIUM** - Premium tier features
4. **USER** - Standard user features

---

## 📊 Subscription Tiers

1. **FREE** - Basic features, limited usage
2. **BASIC** - 10k monthly calls
3. **PREMIUM** - 100k monthly calls
4. **ENTERPRISE** - Unlimited, dedicated support

---

## 🐛 Troubleshooting

### "Could not locate a Flask application"

✅ **Fixed** - `app.py` is now present for Flask auto-discovery

### "Database error"

```bash
# Reset the database
rm Evident.db
flask init-db
```

### Port 5000 already in use

```bash
# Use different port
flask run --port 5001
```

### Dependency errors

```bash
# Reinstall all dependencies
pip install -r requirements.txt
```

### .env file not found

The setup script creates it automatically. If manual setup:

```bash
# Copy the .env template
cp .env.example .env
# Edit .env with your settings
```

---

## 📖 Full Documentation

For detailed information, see:

- **[AUTH_SYSTEM.md](docs/AUTH_SYSTEM.md)** - Complete authentication system documentation
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - API endpoints reference
- **[DASHBOARD_AUTH_UPGRADE_SUMMARY.md](docs/DASHBOARD_AUTH_UPGRADE_SUMMARY.md)** - Implementation summary
- **[INTEGRATION_GUIDE.py](auth/INTEGRATION_GUIDE.py)** - Integration instructions

---

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn wsgi:app
```

### Environment Variables for Production

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secure-random-secret-key
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost/evident
```

### Before Deploying

1. Change `SECRET_KEY` to a secure random value
2. Use PostgreSQL instead of SQLite
3. Enable HTTPS
4. Configure email for password resets
5. Set up proper logging
6. Review security settings in `app_config.py`

---

## 📞 Support

If you encounter issues:

1. Check the console output for error messages
2. Review the Full Documentation (links above)
3. Check database integrity with `flask list-users`
4. Review audit logs at `http://localhost:5000/admin/audit-logs`

---

## ✅ Next Steps

1. **Run the setup script** (choose based on your OS)
2. **Start the server** with `python app.py`
3. **Create a test user** at `http://localhost:5000/auth/register`
4. **Login** and explore features
5. **Read the full documentation** for advanced features

---

**🎉 You're all set! Happy coding!**

Last Updated: 2025-01-31  
Platform: Evident v2.0  
Status: ✅ Production Ready
