# Admin API Quick Reference

Complete reference for all admin backend management endpoints.

--

## Authentication

All admin endpoints require:

1. Valid session (logged in)
2. User role = `admin`

Returns `403 Forbidden` if not admin.

--

## User Management

### List All Users

```http
GET /admin/users
```

**Response:**

```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "organization": "Acme Legal",
      "subscription_tier": "professional",
      "role": "pro",
      "is_active": true,
      "analyses_count": 23,
      "storage_used_mb": 456.7,
      "created_at": "2025-01-10T09:00:00Z"
    }
  ]
}
```

--

### Get User Details

```http
GET /admin/users/<id>
```

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "organization": "Acme Legal",
  "subscription_tier": "professional",
  "role": "pro",
  "is_active": true,
  "created_at": "2025-01-10T09:00:00Z"
}
```

--

### Update User

```http
PUT /admin/users/<id>
Content-Type: application/json
```

**Request Body:**

```json
{
  "full_name": "Jane Doe",
  "organization": "Updated Legal LLC",
  "subscription_tier": "enterprise",
  "role": "admin"
}
```

**Editable Fields:**

- `full_name` (string)
- `organization` (string)
- `subscription_tier` (free | professional | enterprise)
- `role` (user | pro | admin)

**Response:**

```json
{
  "message": "User updated successfully",
  "user": {
    /* updated user object */
  }
}
```

--

### Toggle User Status (Enable/Disable)

```http
POST /admin/users/<id>/toggle-status
```

**Response:**

```json
{
  "message": "User disabled successfully",
  "is_active": false
}
```

**Safety:** Returns `403` if trying to disable yourself.

--

### Reset User Password

```http
POST /admin/users/<id>/reset-password
Content-Type: application/json
```

**Request Body:**

```json
{
  "new_password": "SecurePassword123!"
}
```

**Response:**

```json
{
  "message": "Password reset successfully"
}
```

**Note:** User must use new password on next login.

--

### Delete User

```http
DELETE /admin/users/<id>
```

**Response:**

```json
{
  "message": "User deleted successfully"
}
```

**Safety:** Returns `403` if trying to delete yourself.

--

## Analysis Management

### List All Analyses

```http
GET /admin/analyses?status=completed&limit=100
```

**Query Parameters:**

- `status` (optional): Filter by status (completed | analyzing | failed | uploaded)
- `limit` (optional): Max results (default 100)

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

### Delete Analysis

```http
DELETE /admin/analyses/<id>
```

**Response:**

```json
{
  "message": "Analysis deleted successfully"
}
```

**Action:** Deletes analysis record AND uploaded file from disk.

--

## Statistics & Monitoring

### Platform Statistics

```http
GET /admin/stats
```

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
  "daily_activity": [45, 52, 48, 61, 58, 44, 39],
  "storage_used_gb": 23.4
}
```

**Includes:**

- User counts (total, active)
- Analysis stats (total, success rate)
- Subscription distribution
- 7-day activity trend
- Storage usage

--

### System Info

```http
GET /admin/system-info
```

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

**Requires:** `psutil` package

--

### Audit Logs

```http
GET /admin/audit-logs?action=user_edit&limit=200
```

**Query Parameters:**

- `action` (optional): Filter by action type
- `limit` (optional): Max results (default 200)

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

**Action Types:**

- `login`, `logout`
- `user_edit`, `user_delete`, `user_toggle`
- `analysis_delete`
- `password_reset`

--

## Error Responses

### 401 Unauthorized

```json
{
  "error": "Please log in to access this resource"
}
```

### 403 Forbidden

```json
{
  "error": "Admin access required"
}
```

```json
{
  "error": "Cannot delete your own account"
}
```

### 404 Not Found

```json
{
  "error": "User not found"
}
```

```json
{
  "error": "Analysis not found"
}
```

### 400 Bad Request

```json
{
  "error": "Invalid subscription tier"
}
```

--

## Safety Features

### Account Protection

- ✅ Cannot delete your own admin account
- ✅ Cannot disable your own admin account
- ✅ All actions logged to audit trail

### Data Validation

- ✅ Email format validation
- ✅ Subscription tier enum (free/professional/enterprise)
- ✅ Role enum (user/pro/admin)
- ✅ Password strength requirements

### Audit Trail

- ✅ All user edits logged
- ✅ All deletions logged
- ✅ Includes user_id, resource, IP, timestamp

--

## Usage Examples

### Example: Upgrade User to Professional

```javascript
// 1. Get user details
const user = await fetch("/admin/users/123");

// 2. Update subscription tier
const response = await fetch("/admin/users/123", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    subscription_tier: "professional",
    role: "pro",
  }),
});

// 3. User now has Professional limits:
//    - 100 analyses per month
//    - 2GB storage
//    - API access
```

### Example: Disable Abusive Account

```javascript
// Disable user account
const response = await fetch("/admin/users/456/toggle-status", {
  method: "POST",
});

// Result: { "message": "User disabled successfully", "is_active": false }
// User can no longer log in
```

### Example: Clean Up Failed Analyses

```javascript
// 1. Get all failed analyses
const analyses = await fetch("/admin/analyses?status=failed");

// 2. Delete each one
for (const analysis of analyses.analyses) {
  await fetch(`/admin/analyses/${analysis.id}`, { method: "DELETE" });
}

// Frees up storage space
```

--

## Performance Notes

### Pagination

- Use `limit` parameter to control result count
- Default limits: 100 analyses, 200 audit logs
- No limit on users (typically < 1000)

### Caching

- Stats endpoint can be cached (5 min TTL recommended)
- System info refreshes on each request
- User lists should refresh after edits

### Database Indexes

- `user_id` indexed for fast lookups
- `status` indexed for filtering
- `created_at` indexed for sorting

--

## Testing Checklist

- [ ] Can list all users
- [ ] Can edit user details
- [ ] Can toggle user status
- [ ] Can delete users (with safety check)
- [ ] Can list analyses with filters
- [ ] Can delete analyses
- [ ] Stats endpoint returns valid data
- [ ] System info shows metrics
- [ ] Audit logs populate correctly
- [ ] All safety checks enforced

--

**Related Docs:**

- [ADMIN-BACKEND-GUIDE.md](./ADMIN-BACKEND-GUIDE.md) - Full admin panel guide
- [DASHBOARD-QUICK-REF.md](./DASHBOARD-QUICK-REF.md) - User dashboard API
- [WEB-APP-GUIDE.md](./WEB-APP-GUIDE.md) - Platform overview

--

**Last Updated:** January 2025  
**Version:** 2.0.0
