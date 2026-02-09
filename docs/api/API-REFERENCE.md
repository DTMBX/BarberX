# Evident REST API Reference

**Version:** v1  
**Base URL:** `https://Evident.info/api/v1`  
**Authentication:** JWT Bearer Token

## Overview

The Evident REST API provides programmatic access to all platform features for
cross-platform clients (Web, Windows, iOS, Android). All endpoints return JSON
responses and use standard HTTP status codes.

## Authentication

### JWT Token Flow

1. **Register or Login** to receive a JWT token
2. **Include token** in `Authorization` header for all subsequent requests:
   ```
   Authorization: Bearer <your_jwt_token>
   ```
3. **Refresh token** before expiration (24-hour lifetime)

### Endpoints

#### POST /auth/register

Register a new user account.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response (201):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "tier": "FREE",
    "role": "user",
    "created_at": "2026-01-27T04:00:00Z"
  }
}
```

**Errors:**

- `400`: Email and password required / Invalid email format
- `409`: Email already registered

--

#### POST /auth/login

Authenticate existing user.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "tier": "PRO",
    "role": "user",
    "created_at": "2026-01-27T04:00:00Z"
  }
}
```

**Errors:**

- `400`: Email and password required
- `401`: Invalid email or password
- `403`: Account is disabled

--

#### POST /auth/refresh

Refresh JWT token (extends expiration).

**Headers:**

```
Authorization: Bearer <current_token>
```

**Response (200):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

--

#### GET /auth/me

Get current authenticated user info.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "tier": "PRO",
    "role": "user",
    "is_active": true,
    "created_at": "2026-01-27T04:00:00Z",
    "last_login": "2026-01-27T10:30:00Z"
  }
}
```

--

#### POST /auth/logout

Logout (client should discard token).

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "message": "Logged out successfully"
}
```

--

## Upload Endpoints

#### POST /upload/pdf

Upload a PDF document.

**Headers:**

```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request:**

```
file: <PDF file>
```

**Response (201):**

```json
{
  "file_id": 123,
  "filename": "court_document.pdf",
  "original_filename": "Court Document - Case 12345.pdf",
  "size": 1234567,
  "uploaded_at": "2026-01-27T10:45:00Z",
  "path": "/uploads/pdfs/1_20260127_104500_court_document.pdf"
}
```

**Tier Limits:**

- **FREE**: 10MB max, 10 files/month
- **PRO**: 100MB max, unlimited
- **PREMIUM**: 500MB max, unlimited
- **ENTERPRISE**: 5GB max, unlimited

**Errors:**

- `400`: No file provided / No file selected / Only PDF files allowed
- `403`: PDF upload not available on your tier
- `413`: File size exceeds limit

--

#### POST /upload/video

Upload BWC video footage.

**Headers:**

```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request:**

```
file: <Video file (mp4, mov, avi, mkv, webm)>
```

**Response (201):**

```json
{
  "file_id": 456,
  "filename": "bodycam_footage.mp4",
  "original_filename": "BWC_2026_01_27_Officer_Smith.mp4",
  "size": 123456789,
  "uploaded_at": "2026-01-27T10:50:00Z",
  "path": "/uploads/videos/1_20260127_105000_bodycam_footage.mp4",
  "status": "queued_for_transcription"
}
```

**Tier Limits:**

- **FREE**: Not available
- **PRO**: 1GB max per file
- **PREMIUM**: 5GB max per file
- **ENTERPRISE**: 20GB max per file

**Errors:**

- `400`: No file provided / Invalid video format
- `403`: Video upload requires PRO tier or higher
- `413`: Video size exceeds limit

--

#### GET /upload/status/{file_id}

Check upload/processing status.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "file_id": 123,
  "status": "completed",
  "progress": 100,
  "message": "Upload completed successfully"
}
```

**Status Values:**

- `queued`: Upload queued for processing
- `processing`: Currently being processed
- `completed`: Processing complete
- `failed`: Processing failed

--

## Analysis Endpoints

#### POST /analysis/start

Start AI analysis on uploaded evidence.

**Headers:**

```
Authorization: Bearer <token>
```

**Request:**

```json
{
  "file_id": 123,
  "analysis_type": "full"
}
```

**Analysis Types:**

- `transcription`: Audio/video transcription only
- `ocr`: PDF text extraction only
- `full`: Complete analysis (transcription + timeline + entity extraction)

**Response (201):**

```json
{
  "analysis_id": "analysis_20260127105500",
  "file_id": 123,
  "analysis_type": "full",
  "status": "queued",
  "created_at": "2026-01-27T10:55:00Z"
}
```

**Errors:**

- `400`: file_id required
- `403`: AI analysis requires PRO tier or higher

--

#### GET /analysis/{analysis_id}

Get analysis results.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "analysis_id": "analysis_20260127105500",
  "status": "completed",
  "progress": 100,
  "results": {
    "transcription": "Officer Smith approached the vehicle at 14:32...",
    "entities": ["Officer Smith", "John Doe", "Vehicle #AB123"],
    "timeline": [
      {
        "timestamp": "14:32:00",
        "event": "Initial approach",
        "confidence": 0.95
      }
    ]
  },
  "completed_at": "2026-01-27T11:00:00Z"
}
```

--

#### GET /analysis/{analysis_id}/status

Get analysis processing status.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "analysis_id": "analysis_20260127105500",
  "status": "processing",
  "progress": 75,
  "estimated_completion": "2026-01-27T11:05:00Z"
}
```

--

#### GET /analysis/{analysis_id}/report

Generate analysis report (PDF or JSON).

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `format`: `json` (default) or `pdf`

**Response (200) - JSON:**

```json
{
  "analysis_id": "analysis_20260127105500",
  "report_type": "full_analysis",
  "generated_at": "2026-01-27T11:10:00Z",
  "findings": [
    {
      "type": "timeline_gap",
      "description": "2-minute gap in footage between 14:35 and 14:37",
      "severity": "medium"
    }
  ],
  "recommendations": ["Review backup camera footage for missing 2 minutes"]
}
```

**Response (200) - PDF:**

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="analysis_report.pdf"

<PDF binary data>
```

**Errors:**

- `403`: Report export requires PRO tier or higher
- `501`: PDF export not yet implemented

--

#### GET /analysis/list

List all analyses for current user.

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)

**Response (200):**

```json
{
  "analyses": [
    {
      "id": "analysis_20260127105500",
      "file_id": 123,
      "status": "completed",
      "created_at": "2026-01-27T10:55:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 20
}
```

--

## User Endpoints

#### GET /user/profile

Get current user profile.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "tier": "PRO",
    "role": "user",
    "is_active": true,
    "created_at": "2026-01-27T04:00:00Z",
    "last_login": "2026-01-27T10:30:00Z"
  }
}
```

--

#### PUT /user/profile

Update user profile.

**Headers:**

```
Authorization: Bearer <token>
```

**Request:**

```json
{
  "name": "John Smith"
}
```

**Response (200):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Smith",
    "tier": "PRO"
  }
}
```

--

#### POST /user/change-password

Change user password.

**Headers:**

```
Authorization: Bearer <token>
```

**Request:**

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Response (200):**

```json
{
  "message": "Password updated successfully"
}
```

**Errors:**

- `400`: Current and new password required
- `401`: Current password is incorrect

--

#### GET /user/subscription

Get subscription information.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "tier": "PRO",
  "plan_details": {
    "name": "PRO",
    "billing_period": "monthly",
    "next_billing_date": "2026-02-27T00:00:00Z",
    "amount": 49.99
  }
}
```

--

#### GET /user/usage

Get usage statistics for current billing period.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "uploads": {
    "count": 5,
    "limit": -1
  },
  "analyses": {
    "count": 3,
    "limit": -1
  },
  "storage_mb": {
    "used": 125,
    "limit": -1
  }
}
```

**Note:** `-1` indicates unlimited.

--

## Billing Endpoints

#### POST /billing/create-checkout-session

Create Stripe checkout session for subscription upgrade.

**Headers:**

```
Authorization: Bearer <token>
```

**Request:**

```json
{
  "price_id": "price_1234567890",
  "tier": "PRO"
}
```

**Response (200):**

```json
{
  "session_id": "cs_test_1234567890",
  "url": "https://checkout.stripe.com/pay/cs_test_1234567890"
}
```

**Client Flow:**

1. Call this endpoint to get checkout URL
2. Redirect user to Stripe checkout page
3. User completes payment
4. Stripe webhook updates user tier
5. User redirected back to success page

--

#### POST /billing/webhook

Stripe webhook handler (internal use).

**Headers:**

```
Stripe-Signature: <stripe_signature>
```

**Events Handled:**

- `checkout.session.completed`: Upgrade user tier after successful payment
- `customer.subscription.updated`: Update subscription details
- `customer.subscription.deleted`: Downgrade to FREE tier

**Note:** This endpoint is called by Stripe servers, not client applications.

--

#### POST /billing/portal

Create Stripe customer portal session for subscription management.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "url": "https://billing.stripe.com/session/live_1234567890"
}
```

**Client Flow:**

1. Call this endpoint to get portal URL
2. Open portal in browser/webview
3. User can update payment method, cancel subscription, etc.
4. Changes synced via webhooks

**Errors:**

- `400`: No active subscription

--

## Evidence Endpoints

#### GET /evidence/list

List all evidence files for current user.

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)

**Response (200):**

```json
{
  "evidence": [
    {
      "id": 1,
      "type": "video",
      "filename": "bodycam_footage.mp4",
      "size": 123456789,
      "status": "processed",
      "uploaded_at": "2026-01-27T10:50:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20
}
```

--

#### GET /evidence/{evidence_id}

Get evidence details.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "evidence": {
    "id": 1,
    "type": "video",
    "filename": "bodycam_footage.mp4",
    "size": 123456789,
    "status": "processed",
    "uploaded_at": "2026-01-27T10:50:00Z"
  }
}
```

--

#### POST /evidence/{evidence_id}/transcribe

Start transcription for video evidence.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (202):**

```json
{
  "job_id": "trans_1",
  "evidence_id": 1,
  "status": "queued",
  "started_at": "2026-01-27T11:00:00Z"
}
```

**Errors:**

- `403`: Transcription requires PRO tier or higher

--

#### POST /evidence/{evidence_id}/ocr

Start OCR processing for PDF evidence.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (202):**

```json
{
  "job_id": "ocr_1",
  "evidence_id": 1,
  "status": "queued",
  "started_at": "2026-01-27T11:00:00Z"
}
```

**Errors:**

- `403`: OCR requires PRO tier or higher

--

#### DELETE /evidence/{evidence_id}

Delete evidence file.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "message": "Evidence deleted successfully"
}
```

--

## Admin Endpoints

**Note:** All admin endpoints require `role: "admin"`.

#### GET /admin/users

List all users (admin only).

**Headers:**

```
Authorization: Bearer <admin_token>
```

**Query Parameters:**

- `page`: Page number (default: 1)
- `limit`: Results per page (default: 50, max: 100)

**Response (200):**

```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "tier": "PRO",
      "role": "user",
      "is_active": true,
      "created_at": "2026-01-27T04:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 50
}
```

**Errors:**

- `403`: Admin access required

--

#### GET /admin/users/{user_id}

Get user details (admin only).

**Headers:**

```
Authorization: Bearer <admin_token>
```

**Response (200):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "tier": "PRO",
    "role": "user",
    "is_active": true,
    "created_at": "2026-01-27T04:00:00Z"
  }
}
```

**Errors:**

- `403`: Admin access required
- `404`: User not found

--

#### GET /admin/stats

Get system statistics (admin only).

**Headers:**

```
Authorization: Bearer <admin_token>
```

**Response (200):**

```json
{
  "users": {
    "total": 100,
    "active": 85,
    "by_tier": {
      "FREE": 50,
      "PRO": 30,
      "PREMIUM": 15,
      "ENTERPRISE": 5
    }
  },
  "uploads": {
    "total": 500,
    "today": 25
  },
  "analyses": {
    "total": 250,
    "in_progress": 5
  }
}
```

**Errors:**

- `403`: Admin access required

--

## Error Responses

All error responses follow this format:

```json
{
  "error": "Human-readable error message"
}
```

### HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions (tier/role)
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `413 Payload Too Large`: File size exceeds limit
- `500 Internal Server Error`: Server error
- `501 Not Implemented`: Feature not yet available

--

## Rate Limiting

**FREE Tier:**

- 100 requests/hour
- 1000 requests/day

**PRO Tier:**

- 500 requests/hour
- 10,000 requests/day

**PREMIUM/ENTERPRISE:**

- Unlimited requests

Rate limit headers included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643276400
```

--

## Example Client Code

### Python

```python
import requests

# Login
response = requests.post("https://Evident.info/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["token"]

# Upload PDF
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("document.pdf", "rb")}
response = requests.post("https://Evident.info/api/v1/upload/pdf",
                        headers=headers, files=files)
file_id = response.json()["file_id"]

# Start analysis
response = requests.post("https://Evident.info/api/v1/analysis/start",
                        headers=headers, json={"file_id": file_id})
analysis_id = response.json()["analysis_id"]
```

### JavaScript

```javascript
// Login
const response = await fetch('https://Evident.info/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' }),
});
const { token } = await response.json();

// Upload PDF
const formData = new FormData();
formData.append('file', pdfFile);
const uploadResponse = await fetch('https://Evident.info/api/v1/upload/pdf', {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}` },
  body: formData,
});
const { file_id } = await uploadResponse.json();
```

### C# (.NET MAUI)

```csharp
// Login
var client = new HttpClient();
var loginData = new {email = "user@example.com", password = "password123"};
var response = await client.PostAsJsonAsync("https://Evident.info/api/v1/auth/login", loginData);
var result = await response.Content.ReadFromJsonAsync<LoginResponse>();
var token = result.Token;

// Upload PDF
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
var content = new MultipartFormDataContent();
content.Add(new StreamContent(fileStream), "file", "document.pdf");
var uploadResponse = await client.PostAsync("https://Evident.info/api/v1/upload/pdf", content);
```

--

## Changelog

### v1.0.0 (2026-01-27)

- Initial API release
- JWT authentication
- Upload endpoints (PDF, video)
- Analysis endpoints (AI processing)
- User management endpoints
- Stripe billing integration
- Admin endpoints
- Tier-based access control

--

## Support

**Documentation:** https://Evident.info/docs/api  
**Email:** api-support@Evident.info  
**Discord:** https://discord.gg/Evident

**Status Page:** https://status.Evident.info
