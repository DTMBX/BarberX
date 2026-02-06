# Admin Backend Management - Complete Guide

## Overview

The Evident admin panel now provides complete CRUD (Create, Read, Update,
Delete) operations for managing users, analyses, and monitoring system health
via an online admin portal.

**Access:** `https://app.Evident.info/admin` (requires admin role)

--

## ✅ What's New

### 1. **Enhanced Admin Panel UI** (`templates/admin-enhanced.html`)

- Modern tabbed interface with 5 sections
- Modal-based inline editing
- Real-time search and filtering
- Toast notifications for all actions
- Loading overlays for async operations
- Chart.js visualizations
- Fully responsive design

### 2. **Complete Backend API** (8 new endpoints in `app.py`)

- Full user CRUD operations
- Account status management
- Password reset capabilities
- Analysis management with filtering
- Enhanced platform statistics
- System health monitoring
- Complete audit trail

### 3. **JavaScript Management System** (`assets/js/admin-panel.js`)

- Tab navigation and data loading
- User editing via modals
- Enable/disable user accounts
- Delete users with confirmation
- Analysis filtering and deletion
- Real-time system metrics
- Audit log viewing with filters

--

## 🔐 Security Features

### Role-Based Access Control

```python
@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
```

### Safety Checks

- ✅ Cannot delete your own admin account
- ✅ Cannot disable your own admin account
- ✅ All actions logged to audit trail
- ✅ User-scoped security on all operations
- ✅ Confirmation dialogs for destructive actions

--

## 📊 Admin Panel Sections

### 1. Overview Tab

**Purpose:** High-level platform statistics and charts

**Displays:**

- Total users count
- Active users count
- Total analyses completed
- Overall success rate

**Charts:**

- Subscription distribution (doughnut chart)
- Daily activity (7-day line chart)

**API Endpoint:** `GET /admin/stats`

**Response:**

```json
{
  "total_users": 156,
  "active_users": 142,
  "total_analyses": 2453,
  "success_rate": 94.2,
  "subscription_breakdown": {
    "free": 120,
    "professional": 32,
    "enterprise": 4
  },
  "daily_activity": [45, 52, 48, 61, 58, 44, 39]
}
```

--

### 2. Users Tab

**Purpose:** Manage all platform users with full CRUD operations

#### Features:

- **Search:** Filter users by name, email, or organization
- **Edit:** Inline modal editing of user details
- **Enable/Disable:** Toggle account status
- **Delete:** Remove users with confirmation
- **Password Reset:** Admin can reset any user password

#### User Management Actions

##### ✏️ Edit User

1. Click **Edit** button next to user
2. Modal opens with editable fields:
   - Full Name
   - Organization
   - Subscription Tier (free/professional/enterprise)
   - Role (user/pro/admin)
3. Make changes and click **Save Changes**

**API:** `PUT /admin/users/<id>`

```json
{
  "full_name": "John Doe",
  "organization": "Acme Legal",
  "subscription_tier": "professional",
  "role": "pro"
}
```

##### ⏸ Disable / ▶ Enable User

- Click **Disable** button to deactivate account
- Click **Enable** button to reactivate account
- User loses access immediately when disabled

**API:** `POST /admin/users/<id>/toggle-status`

**Response:**

```json
{
  "message": "User disabled successfully",
  "is_active": false
}
```

##### 🔑 Reset Password

1. Click **Reset Password** button
2. Enter new password in prompt
3. User must use new password on next login

**API:** `POST /admin/users/<id>/reset-password`

```json
{
  "new_password": "SecurePassword123!"
}
```

##### 🗑 Delete User

1. Click **Delete** button
2. Confirm deletion in dialog
3. User and all associated data removed

**API:** `DELETE /admin/users/<id>`

**Safety:** Returns 403 if attempting to delete yourself

--

### 3. Analyses Tab

**Purpose:** View and manage all platform analyses

#### Features:

- **Filter by Status:** All, Completed, Analyzing, Failed
- **View Details:** Click to see full analysis
- **Delete:** Remove analysis with file cleanup

#### Analysis Management

##### 👁 View Analysis

- Click **View** to see full analysis details
- Opens analysis page in same window

##### 🗑 Delete Analysis

1. Click **Delete** button
2. Confirm deletion
3. Analysis record and uploaded files removed

**API:** `DELETE /admin/analyses/<id>`

**List Analyses:** `GET /admin/analyses?status=completed&limit=100`

**Response:**

```json
{
  "analyses": [
    {
      "id": "uuid",
      "filename": "bodycam_video.mp4",
      "user_id": 123,
      "status": "completed",
      "file_size": 15728640,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

--

### 4. System Tab

**Purpose:** Real-time system health monitoring

#### Metrics Displayed:

- **Database Size:** Current SQLite/PostgreSQL size
- **Upload Storage:** Total storage used by uploaded files
- **CPU Usage:** Current CPU utilization percentage
- **Memory Usage:** RAM usage percentage

#### Detailed System Info:

- Python version
- Flask version
- Memory: Used GB / Total GB (%)
- Disk: Used GB / Total GB (%)

**API:** `GET /admin/system-info`

**Response:**

```json
{
  "python_version": "3.9.13",
  "flask_version": "3.0.0",
  "cpu_percent": 12.3,
  "memory_used_gb": 4.2,
  "memory_total_gb": 16.0,
  "memory_percent": 26.3,
  "disk_used_gb": 250.5,
  "disk_total_gb": 500.0,
  "disk_percent": 50.1,
  "database_size_mb": 45.7,
  "upload_storage_gb": 12.3
}
```

**Dependencies:** Requires `psutil` package

--

### 4. Settings Tab ⭐ NEW

**Purpose:** Comprehensive app configuration and control

#### Features:

- **Initialize Defaults:** Create all standard settings with one click
- **Category Organization:** Settings grouped by function
- **Inline Editing:** Edit values directly in the interface
- **Quick Toggles:** Boolean settings have instant on/off switches
- **Add Custom Settings:** Create your own configuration options
- **Type-Safe:** Settings are typed (string, int, bool, float)

#### Settings Categories:

##### 🌐 General Settings

- `app_name` - Application name displayed throughout platform
- `app_tagline` - Tagline shown on homepage and login
- `maintenance_mode` - Enable to put site in maintenance mode
- `allow_registrations` - Allow new user registrations
- `contact_email` - Contact email for support

##### 🔒 Security Settings

- `session_timeout_minutes` - User session timeout (default: 60)
- `password_min_length` - Minimum password length (default: 8)
- `require_email_verification` - Require email verification for new accounts
- `max_login_attempts` - Max failed login attempts before lockout (default: 5)
- `enable_2fa` - Enable two-factor authentication

##### ✨ Feature Flags

- `enable_api` - Enable API access for Pro/Enterprise users
- `enable_analytics` - Enable analytics dashboard
- `enable_export` - Enable data export functionality
- `enable_webhooks` - Enable webhook notifications

##### 📊 Tier Limits

- `free_tier_analyses` - Max analyses per month for free tier (default: 5)
- `free_tier_storage_mb` - Max storage in MB for free tier (default: 500)
- `pro_tier_analyses` - Max analyses per month for professional tier
  (default: 100)
- `pro_tier_storage_mb` - Max storage in MB for professional tier
  (default: 2048)
- `max_file_size_mb` - Maximum file upload size in MB (default: 500)

##### 📧 Email Configuration

- `smtp_enabled` - Enable SMTP email sending
- `smtp_host` - SMTP server hostname
- `smtp_port` - SMTP server port (default: 587)
- `smtp_username` - SMTP username
- `from_email` - From email address

##### 🎨 Branding & Customization

- `primary_color` - Primary brand color hex (default: #3b82f6)
- `secondary_color` - Secondary brand color hex (default: #8b5cf6)
- `logo_url` - URL to application logo
- `favicon_url` - URL to favicon

#### Settings Management Actions:

##### Initialize Default Settings

1. Click **Initialize Defaults** button
2. Confirm action
3. Creates 29 standard settings
4. Skips any that already exist

**API:** `POST /admin/settings/initialize`

##### Edit Setting

1. Change value directly in input field
2. For boolean settings, click checkbox
3. Blur input (click away) to auto-save
4. See success toast notification

**API:** `PUT /admin/settings/<id>`

```json
{
  "value": "new_value"
}
```

##### Add Custom Setting

1. Scroll to "Add New Setting" card
2. Fill in:
   - Setting Key (e.g., `custom_feature_enabled`)
   - Category (general/security/features/limits/email/branding)
   - Value (the actual value)
   - Type (string/int/bool/float)
   - Description (what it controls)
3. Click **Add Setting**

**API:** `POST /admin/settings`

```json
{
  "key": "custom_feature_enabled",
  "value": "true",
  "value_type": "bool",
  "category": "features",
  "description": "Enable custom feature for enterprise users"
}
```

##### Delete Setting

1. Click **Delete** button (🗑️) next to setting
2. Confirm deletion
3. Setting removed from database

**API:** `DELETE /admin/settings/<id>`

**Note:** Some core settings may be marked as read-only and cannot be deleted.

--

### 5. System Tab

**Purpose:** Real-time system health monitoring

#### Metrics Displayed:

- **Database Size:** Current SQLite/PostgreSQL size
- **Upload Storage:** Total storage used by uploaded files
- **CPU Usage:** Current CPU utilization percentage
- **Memory Usage:** RAM usage percentage

--

### 6. Audit Logs Tab

**Purpose:** Complete audit trail of all admin actions

#### Features:

- **Filter by Action:** View specific action types
- **Action Types:** login, user_edit, user_delete, analysis_delete, etc.
- **Details:** Shows user, resource, IP address, timestamp

**API:** `GET /admin/audit-logs?action=user_edit&limit=200`

**Response:**

```json
{
  "logs": [
    {
      "id": 1,
      "action": "user_edit",
      "user_id": 5,
      "resource_type": "User",
      "resource_id": 123,
      "ip_address": "192.168.1.100",
      "created_at": "2025-01-15T14:22:00Z"
    }
  ]
}
```

--

## 🛠 Technical Implementation

### Frontend (`admin-enhanced.html`)

**Structure:**

```html
<div class="tabs">
  <button class="tab active" data-tab="overview">Overview</button>
  <button class="tab" data-tab="users">Users</button>
  <!-- ... ->
</div>

<div id="overview" class="tab-content active">
  <!-- Stats cards and charts ->
</div>

<!-- Edit User Modal ->
<div id="editUserModal" class="modal">
  <div class="modal-content">
    <form id="editUserForm">
      <!-- Form fields ->
    </form>
  </div>
</div>

<!-- Toast Notifications ->
<div id="toast" class="toast"></div>

<!-- Loading Overlay ->
<div id="loadingOverlay" class="loading-overlay"></div>
```

### JavaScript (`admin-panel.js`)

**Key Functions:**

```javascript
// Tab Management
setupTabs(); // Initialize tab navigation
loadTabData(tab); // Load data when tab activated

// Users Tab
loadUsers(); // Fetch all users
editUser(userId); // Open edit modal
toggleUserStatus(userId); // Enable/disable account
deleteUser(userId); // Remove user
filterUsers(); // Search users

// Analyses Tab
loadAnalyses(); // Fetch analyses with filter
deleteAnalysis(analysisId); // Remove analysis
filterAnalyses(); // Apply status filter

// System Tab
loadSystemInfo(); // Fetch system metrics
refreshSystemInfo(); // Manual refresh

// Audit Logs Tab
loadAuditLogs(); // Fetch logs with filter
filterLogs(); // Apply action filter

// Utilities
showLoading(); // Show loading overlay
hideLoading(); // Hide loading overlay
showToast(message, type); // Show toast notification
```

### Backend Routes (`app.py`)

**User Management:**

```python
GET    /admin/users           # List all users
GET    /admin/users/<id>      # Get user details
PUT    /admin/users/<id>      # Update user
DELETE /admin/users/<id>      # Delete user
POST   /admin/users/<id>/toggle-status    # Enable/disable
POST   /admin/users/<id>/reset-password   # Reset password
```

**Analysis Management:**

```python
GET    /admin/analyses        # List analyses (with filters)
DELETE /admin/analyses/<id>   # Delete analysis
```

**Statistics & Monitoring:**

```python
GET    /admin/stats           # Platform statistics
GET    /admin/system-info     # System health metrics
GET    /admin/audit-logs      # Audit trail
```

--

## 📝 Usage Examples

### Example 1: Update User Subscription Tier

1. Navigate to **Users** tab
2. Search for user by email: "john@example.com"
3. Click **Edit** button
4. Change **Subscription Tier** to "Professional"
5. Click **Save Changes**
6. User immediately gets Professional tier limits (100 analyses, 2GB storage)

### Example 2: Disable Abusive Account

1. Navigate to **Users** tab
2. Find problematic user
3. Click **Disable** button
4. Confirm action
5. User can no longer log in
6. Action logged in **Audit Logs** tab

### Example 3: Monitor System Health

1. Navigate to **System** tab
2. View current CPU, memory, disk usage
3. Check if database is growing too large
4. Monitor upload storage consumption
5. Click **Refresh** for updated metrics

### Example 4: Clean Up Failed Analyses

1. Navigate to **Analyses** tab
2. Filter by **Status:** Failed
3. Review list of failed analyses
4. Click **Delete** on outdated failures
5. Frees up storage space

--

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
pip install psutil
```

### 2. Create Admin Account

Run the admin setup script:

```bash
python create_admin.py
```

This creates the **one and only** admin account:

**Email:** `admin@Evident.info`  
**Password:** `BxAdm!n#2026$Secur3*P@ssw0rd%33^` (33 characters)

The script will:

- Remove any existing admin accounts
- Create exactly ONE admin account
- Verify the credentials work
- Display security notes

**Security Features:**

- Ensures only ONE admin exists
- 33-character password with special characters
- Enterprise tier with unlimited access
- All admin actions logged to audit trail

### 3. Alternative: Manual Admin User Setup

```python
from app import db, User, bcrypt

# In Python shell or init script:
admin = User(
    email='admin@Evident.info',
    password_hash=bcrypt.generate_password_hash('SecurePassword123!').decode('utf-8'),
    full_name='Admin User',
    role='admin',
    subscription_tier='enterprise',
    is_active=True
)
db.session.add(admin)
db.session.commit()
```

### 4. Access Admin Panel

1. Log in as admin user
2. Navigate to: `https://app.Evident.info/admin`
3. Start managing users and analyses

--

## 🎨 UI/UX Features

### Modal Editing

- Smooth fade-in animation
- Click outside to close
- Escape key to close
- Form validation before submit

### Toast Notifications

- Success (green): Operations completed successfully
- Error (red): Operations failed
- Auto-dismiss after 4 seconds
- Slide-in animation

### Loading States

- Full-screen overlay during async operations
- Prevents duplicate submissions
- Professional spinner animation

### Responsive Design

- Works on desktop, tablet, mobile
- Sticky table headers for long lists
- Horizontal scroll on small screens
- Touch-friendly action buttons

--

## 🐛 Troubleshooting

### Issue: "Cannot delete user"

**Cause:** Trying to delete yourself  
**Solution:** Only other admins can delete admin accounts

### Issue: "psutil not found"

**Cause:** Missing dependency  
**Solution:** Run `pip install psutil`

### Issue: "Charts not loading"

**Cause:** Chart.js CDN blocked or slow  
**Solution:** Check internet connection, try refreshing page

### Issue: "401 Unauthorized"

**Cause:** Not logged in as admin  
**Solution:** Ensure user has `role='admin'` in database

--

## 📊 Performance

### Pagination

- Users tab: Loads all users (typically < 1000)
- Analyses tab: Limited to 100 most recent by default
- Audit logs: Limited to 200 most recent by default

### Refresh Rates

- Manual refresh via buttons
- No auto-refresh (prevents server load)
- Charts update when tab is reactivated

### Database Queries

- All queries use SQLAlchemy ORM
- Indexed on user_id, status, created_at
- Efficient JOIN operations

--

## 🚀 Future Enhancements

### Planned Features:

- [ ] Bulk user operations (select multiple, bulk delete/disable)
- [ ] Export users to CSV
- [ ] Advanced filtering (date ranges, custom queries)
- [ ] Real-time WebSocket updates
- [ ] Email notifications for critical actions
- [ ] Two-factor authentication requirement for admins
- [ ] IP-based access restrictions
- [ ] Scheduled reports (daily/weekly analytics)

--

## 📖 Related Documentation

- [DASHBOARD-QUICK-REF.md](./DASHBOARD-QUICK-REF.md) - API reference
- [DASHBOARD-OPTIMIZATION.md](./DASHBOARD-OPTIMIZATION.md) - Implementation
  details
- [START-HERE.md](./START-HERE.md) - Quick start guide
- [WEB-APP-GUIDE.md](./WEB-APP-GUIDE.md) - Full platform guide

--

## ✅ Checklist: Is Admin Panel Working?

- [x] Can log in as admin user
- [x] Can access `/admin` route
- [x] Overview tab shows statistics
- [x] Charts render correctly (subscription, activity)
- [x] Users tab displays all users
- [x] Can edit user details via modal
- [x] Can enable/disable user accounts
- [x] Can delete users (with confirmation)
- [x] Analyses tab shows all analyses
- [x] Can filter analyses by status
- [x] Can delete analyses
- [x] System tab shows metrics (CPU, memory, disk)
- [x] psutil installed and working
- [x] Audit logs tab displays actions
- [x] Can filter logs by action type
- [x] Toast notifications work
- [x] Loading overlay shows during operations
- [x] All safety checks enforced (cannot delete self)

--

## 📞 Support

**Issues:** https://github.com/Evident/platform/issues  
**Email:** support@Evident.info  
**Documentation:** https://docs.Evident.info

--

**Last Updated:** January 2025  
**Version:** 2.0.0  
**Author:** Evident Legal Tech Team
