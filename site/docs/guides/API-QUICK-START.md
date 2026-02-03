# Evident API Quick Start Guide

Get started with the Evident REST API in 5 minutes.

## Base URL

**Production:** `https://Evident.info/api/v1`  
**Local Dev:** `http://localhost:5000/api/v1`

## Authentication Flow

### 1. Register (New User)

```bash
curl -X POST https://Evident.info/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "YourPassword123!",
    "name": "Your Name"
  }'
```

**Response:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "your@email.com",
    "name": "Your Name",
    "tier": "FREE"
  }
}
```

### 2. Login (Existing User)

```bash
curl -X POST https://Evident.info/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "YourPassword123!"
  }'
```

**Save the `token` from the response!**

### 3. Use Token in Requests

Include the token in the `Authorization` header:

```bash
curl -X GET https://Evident.info/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Common Operations

### Upload a PDF

```bash
curl -X POST https://Evident.info/api/v1/upload/pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

### Upload a Video

```bash
curl -X POST https://Evident.info/api/v1/upload/video \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/bodycam.mp4"
```

### Start AI Analysis

```bash
curl -X POST https://Evident.info/api/v1/analysis/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 123,
    "analysis_type": "full"
  }'
```

### Check Analysis Status

```bash
curl -X GET https://Evident.info/api/v1/analysis/ANALYSIS_ID/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Analysis Results

```bash
curl -X GET https://Evident.info/api/v1/analysis/ANALYSIS_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Python Example

```python
import requests

# Login
response = requests.post(
    "https://Evident.info/api/v1/auth/login",
    json={"email": "your@email.com", "password": "YourPassword123!"}
)
token = response.json()["token"]

# Upload PDF
headers = {"Authorization": f"Bearer {token}"}
with open("document.pdf", "rb") as f:
    files = {"file": f}
    upload_response = requests.post(
        "https://Evident.info/api/v1/upload/pdf",
        headers=headers,
        files=files
    )
file_id = upload_response.json()["file_id"]

# Start analysis
analysis_response = requests.post(
    "https://Evident.info/api/v1/analysis/start",
    headers=headers,
    json={"file_id": file_id, "analysis_type": "full"}
)
analysis_id = analysis_response.json()["analysis_id"]

# Check status
status_response = requests.get(
    f"https://Evident.info/api/v1/analysis/{analysis_id}/status",
    headers=headers
)
print(status_response.json())
```

## JavaScript Example

```javascript
// Login
const loginResponse = await fetch("https://Evident.info/api/v1/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "your@email.com",
    password: "YourPassword123!",
  }),
});
const { token } = await loginResponse.json();

// Upload PDF
const formData = new FormData();
formData.append("file", pdfFile);
const uploadResponse = await fetch("https://Evident.info/api/v1/upload/pdf", {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
  body: formData,
});
const { file_id } = await uploadResponse.json();

// Start analysis
const analysisResponse = await fetch(
  "https://Evident.info/api/v1/analysis/start",
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_id, analysis_type: "full" }),
  },
);
const { analysis_id } = await analysisResponse.json();
```

## C# (.NET MAUI) Example

```csharp
using System.Net.Http.Json;

var client = new HttpClient();

// Login
var loginData = new {
    email = "your@email.com",
    password = "YourPassword123!"
};
var loginResponse = await client.PostAsJsonAsync(
    "https://Evident.info/api/v1/auth/login",
    loginData
);
var loginResult = await loginResponse.Content.ReadFromJsonAsync<LoginResponse>();
var token = loginResult.Token;

// Set authorization header for all requests
client.DefaultRequestHeaders.Authorization =
    new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

// Upload PDF
var content = new MultipartFormDataContent();
content.Add(new StreamContent(pdfStream), "file", "document.pdf");
var uploadResponse = await client.PostAsync(
    "https://Evident.info/api/v1/upload/pdf",
    content
);
var uploadResult = await uploadResponse.Content.ReadFromJsonAsync<UploadResponse>();

// Start analysis
var analysisData = new {
    file_id = uploadResult.FileId,
    analysis_type = "full"
};
var analysisResponse = await client.PostAsJsonAsync(
    "https://Evident.info/api/v1/analysis/start",
    analysisData
);
```

## Error Handling

All errors return JSON with `error` field:

```json
{
  "error": "Human-readable error message"
}
```

**Common HTTP Status Codes:**

- `400`: Bad request (invalid data)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient tier/role)
- `404`: Not found
- `413`: File too large
- `500`: Server error

## Token Refresh

Tokens expire after 24 hours. Refresh before expiration:

```bash
curl -X POST https://Evident.info/api/v1/auth/refresh \
  -H "Authorization: Bearer YOUR_CURRENT_TOKEN"
```

Returns a new token with 24-hour expiration.

## Tier Limits

### FREE Tier

- ✅ PDF uploads (10MB max, 10/month)
- ❌ Video uploads
- ❌ AI analysis
- ❌ Report export

### PRO Tier ($49.99/month)

- ✅ PDF uploads (100MB max, unlimited)
- ✅ Video uploads (1GB max, unlimited)
- ✅ AI transcription
- ✅ OCR processing
- ✅ Report export (PDF/JSON)

### PREMIUM Tier ($149.99/month)

- ✅ All PRO features
- ✅ Larger files (PDF 500MB, video 5GB)
- ✅ Advanced AI analysis
- ✅ Priority processing

### ENTERPRISE (Custom pricing)

- ✅ All PREMIUM features
- ✅ Huge files (PDF 5GB, video 20GB)
- ✅ Self-hosted option
- ✅ Custom integrations

## Rate Limiting

**FREE:** 100 req/hour, 1000 req/day  
**PRO:** 500 req/hour, 10,000 req/day  
**PREMIUM+:** Unlimited

Check headers in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643276400
```

## Testing Tools

### Postman Collection

Import this URL:

```
https://Evident.info/api/postman-collection.json
```

### cURL Examples

All examples above use cURL and can be run from terminal.

### API Playground

Interactive testing:

```
https://Evident.info/docs/api-playground
```

## Support

**Documentation:** https://Evident.info/API-REFERENCE.md  
**Issues:** GitHub Issues  
**Email:** api-support@Evident.info

## Next Steps

1. ✅ Get API token (register/login)
2. ✅ Test upload endpoint
3. ✅ Start an analysis
4. ✅ Check analysis status
5. ✅ Get results

**Full Reference:** See `API-REFERENCE.md` for complete documentation.
