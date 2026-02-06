# Admin Panel - Quick Start Guide

**🚀 Your admin backend is now fully functional with online editing!**

--

## 🔑 Admin Credentials

**Email:** `admin@Evident.info`  
**Password:** `BxAdm!n#2026$Secur3*P@ssw0rd%33^` (33 chars with special characters)

**Security Notes:**

- ✅ Only ONE admin account exists
- ✅ Password is 33 characters with special characters
- ✅ Store credentials in secure password manager
- ✅ Change password after first login via admin panel

--

## ⚡ Instant Access

**URL:** `https://app.Evident.info/admin`

**Requirements:**

- Must be logged in
- Account must have `role='admin'`

--

## 🎯 What You Can Do Now

### ✏️ Edit Users

1. Go to **Users** tab
2. Click **Edit** next to any user
3. Change name, organization, tier, or role
4. Click **Save Changes**
5. Changes apply immediately

### 🔄 Change Subscription Tier

1. **Users** tab → **Edit** user
2. Change **Subscription Tier** dropdown:
   - Free: 5 analyses, 500MB
   - Professional: 100 analyses, 2GB
   - Enterprise: Unlimited
3. **Save** → User instantly has new limits

### ⏸ Disable Account

1. Find user in **Users** tab
2. Click **Disable** button
3. User cannot log in anymore
4. Click **Enable** to reactivate

### 🗑 Delete User

1. **Users** tab → Find user
2. Click **Delete** button
3. Confirm deletion
4. User and data removed
5. **Safety:** Cannot delete yourself!

### 🔍 View All Analyses

1. Go to **Analyses** tab
2. Filter by status:
   - Completed
   - Analyzing
   - Failed
3. Click **View** to see details
4. Click **Delete** to remove

### 📊 Monitor System

1. Go to **System** tab
2. See real-time metrics:
   - Database size
   - Upload storage
   - CPU usage
   - Memory usage
3. Click **Refresh** for updates

### 📝 Check Audit Logs

1. Go to **Audit Logs** tab
2. Filter by action type
3. See who did what and when
4. Track all admin actions

### ⚙️ Manage App Settings

1. Go to **Settings** tab
2. Click **Initialize Defaults** (first time)
3. Edit any setting by changing value
4. Toggle feature flags on/off
5. Customize tier limits, branding, security
6. Add custom settings as needed

**Available Settings Categories:**

- **General:** App name, maintenance mode, registrations
- **Security:** Session timeout, password rules, 2FA
- **Features:** API, analytics, webhooks, exports
- **Limits:** Tier quotas (analyses, storage)
- **Email:** SMTP configuration
- **Branding:** Colors, logo, favicon

--

## 🎨 Interface Overview

### 6 Tabs

**1. Overview**

- Platform statistics
- Subscription distribution chart
- Daily activity chart

**2. Users**

- Search users
- Edit/delete users
- Enable/disable accounts
- Reset passwords

**3. Analyses**

- View all analyses
- Filter by status
- Delete analyses

**4. System**

- Real-time metrics
- System health
- Storage usage

**4. Settings** ⭐ NEW

- App configuration
- Feature flags
- Tier limits
- Security settings
- Email & branding

**5. System**

- Real-time metrics
- System health
- Storage usage

**6. Audit Logs**

- Complete history
- Action filtering
- User attribution

--

## 🔐 Security Features

✅ **Role-based access** - Only admins can access  
✅ **Safety checks** - Cannot delete/disable yourself  
✅ **Confirmation dialogs** - Prevents accidents  
✅ **Audit trail** - All actions logged

--

## 📋 Common Tasks

### Task: Upgrade User to Pro

```
Users → Find user → Edit
Change "Subscription Tier" to "professional"
Change "Role" to "pro"
Save Changes
```

### Task: Find Failed Analyses

```
Analyses → Filter "Status" to "failed"
Review list
Delete outdated failures
```

### Task: Check System Health

```
System → View metrics
Check if database is growing
Monitor storage usage
Refresh for updates
```

### Task: Disable Abusive Account

```
Users → Find user
Click "Disable"
Confirm action
User loses access immediately
```

--

## 📁 Files Created

✅ `templates/admin-enhanced.html` - Admin UI  
✅ `assets/js/admin-panel.js` - JavaScript  
✅ `requirements.txt` - Dependencies  
✅ 8 new API endpoints in `app.py`

--

## 📖 Full Documentation

- **ADMIN-BACKEND-GUIDE.md** - Complete feature guide
- **ADMIN-API-REFERENCE.md** - API documentation
- **ADMIN-COMPLETE.md** - Project summary

--

## ✅ Status

**All admin features are LIVE and ready to use!**

Just log in as admin and navigate to `/admin`.

--

**Questions?** Check [ADMIN-BACKEND-GUIDE.md](./ADMIN-BACKEND-GUIDE.md) for detailed instructions.
