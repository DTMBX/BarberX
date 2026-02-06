# Evident Smart Meter Usage Tracking System

## Overview

Comprehensive real-time usage tracking for every user action and resource consumption across the Evident platform.

## Features

### 1. Individual Event Tracking (`smart_meter_events` table)

Tracks every single user action with detailed metadata:

- **AI Requests**: Model used, tokens (input/output), cost, duration
- **File Uploads**: File size, type, processing time
- **Analyses**: Analysis type, duration, cost
- **Workflows**: Workflow execution, resources consumed
- **API Calls**: Endpoint, status, response time
- **Chat Messages**: Model selection, token usage

### 2. Real-Time Quota Management (`usage_quotas` table)

Per-user quota tracking with automatic period resets:

- **AI Tokens**: Track token consumption against monthly limits
- **AI Requests**: Count AI API calls
- **Storage**: Monitor file storage usage in bytes
- **Files**: Count uploaded files
- **Analyses**: Track video/document analyses
- **Workflows**: Monitor workflow executions
- **API Calls**: Rate limiting and quota enforcement
- **Cost Tracking**: Monitor USD spending

### 3. Smart Features

#### Automatic Period Resets

- Monthly billing periods
- Automatic quota reset on new period
- Tracks period start/end dates

#### Rate Limiting

- Per-minute request limiting
- Prevents abuse
- Tier-based limits

#### Alert System

- 80% usage alerts
- 95% usage alerts
- 100% quota exceeded alerts
- Prevents duplicate alerts

#### Cost Attribution

- Real-time cost tracking
- Per-event cost calculation
- Monthly budget monitoring

## Database Schema

### `smart_meter_events`

```sql
id                  INTEGER PRIMARY KEY
user_id             INTEGER NOT NULL (FK -> users.id)
event_type          VARCHAR(50) - 'ai_request', 'file_upload', etc.
event_category      VARCHAR(50) - 'compute', 'storage', 'api', 'feature'
resource_name       VARCHAR(100) - e.g., 'gpt-4', 'claude-3-5'
quantity            FLOAT - Generic quantity metric
tokens_input        INTEGER - AI input tokens
tokens_output       INTEGER - AI output tokens
duration_seconds    FLOAT - Processing time
file_size_bytes     BIGINT - File sizes
cost_usd            NUMERIC(12,6) - Actual cost
cost_credits        INTEGER - Internal credits
endpoint            VARCHAR(200) - API endpoint
ip_address          VARCHAR(45) - IPv4/IPv6
user_agent          VARCHAR(500) - Browser info
session_id          VARCHAR(100) - Session tracking
request_id          VARCHAR(100) - Request tracing
status              VARCHAR(20) - 'success', 'error', 'throttled', 'denied'
error_message       TEXT - Error details
timestamp           DATETIME - Event time
```

### `usage_quotas`

```sql
id                          INTEGER PRIMARY KEY
user_id                     INTEGER NOT NULL UNIQUE (FK -> users.id)
period_start                DATETIME NOT NULL
period_end                  DATETIME NOT NULL
ai_tokens_used              BIGINT DEFAULT 0
ai_tokens_limit             BIGINT DEFAULT 100000
ai_requests_count           INTEGER DEFAULT 0
ai_requests_limit           INTEGER DEFAULT 1000
storage_bytes_used          BIGINT DEFAULT 0
storage_bytes_limit         BIGINT DEFAULT 1073741824 (1GB)
files_uploaded_count        INTEGER DEFAULT 0
files_uploaded_limit        INTEGER DEFAULT 100
analyses_count              INTEGER DEFAULT 0
analyses_limit              INTEGER DEFAULT 50
workflows_executed_count    INTEGER DEFAULT 0
workflows_executed_limit    INTEGER DEFAULT 50
api_calls_count             INTEGER DEFAULT 0
api_calls_limit             INTEGER DEFAULT 10000
total_cost_usd              NUMERIC(12,2) DEFAULT 0
cost_limit_usd              NUMERIC(12,2) DEFAULT 50
requests_this_minute        INTEGER DEFAULT 0
requests_per_minute_limit   INTEGER DEFAULT 60
last_request_timestamp      DATETIME
alert_80_percent_sent       BOOLEAN DEFAULT FALSE
alert_95_percent_sent       BOOLEAN DEFAULT FALSE
alert_100_percent_sent      BOOLEAN DEFAULT FALSE
created_at                  DATETIME
updated_at                  DATETIME
```

## API Endpoints

### GET `/api/usage/stats`

Get comprehensive usage statistics

**Query Parameters:**

- `days` (optional, default: 30) - Number of days to include

**Response:**

```json
{
  "period": {
    "start": "2026-01-01T00:00:00",
    "end": "2026-02-01T00:00:00",
    "days_remaining": 15
  },
  "quotas": {
    "ai_tokens": {
      "used": 45000,
      "limit": 100000,
      "percent": 45.0
    },
    "storage": { ... },
    "files": { ... },
    ...
  },
  "recent_activity": {
    "total_events": 150,
    "by_type": {
      "ai_request": 75,
      "file_upload": 25,
      ...
    },
    "total_cost_usd": 12.50,
    "total_tokens": 75000
  }
}
```

### GET `/api/usage/quota`

Get real-time quota status

**Response:**

```json
{
  "period": { ... },
  "quotas": {
    "ai_tokens": {
      "used": 45000,
      "limit": 100000,
      "percent": 45.0,
      "remaining": 55000
    },
    ...
  },
  "alerts": {
    "alert_80_percent": false,
    "alert_95_percent": false,
    "alert_100_percent": false
  }
}
```

### GET `/api/usage/events`

Get recent usage events

**Query Parameters:**

- `limit` (optional, default: 100) - Max events to return
- `type` (optional) - Filter by event type
- `days` (optional, default: 7) - Days to look back

**Response:**

```json
{
  "events": [
    {
      "id": 123,
      "event_type": "ai_request",
      "event_category": "compute",
      "resource_name": "gpt-4",
      "tokens_input": 150,
      "tokens_output": 800,
      "cost_usd": 0.0245,
      "status": "success",
      "timestamp": "2026-01-30T14:30:00"
    },
    ...
  ],
  "total": 50
}
```

### GET `/api/usage/summary`

Get usage summary with charts data

**Query Parameters:**

- `days` (optional, default: 30)

**Response:**

```json
{
  "daily": [
    {
      "date": "2026-01-30",
      "events": 25,
      "tokens": 15000,
      "cost_usd": 3.25
    },
    ...
  ],
  "by_type": [
    {
      "type": "ai_request",
      "count": 150,
      "cost_usd": 12.50
    },
    ...
  ],
  "stats": { ... }
}
```

### POST `/api/usage/track`

Manually track a usage event (for client-side tracking)

**Request:**

```json
{
  "event_type": "feature_click",
  "event_category": "navigation",
  "resource_name": "dashboard",
  "quantity": 1.0,
  "duration_seconds": 0.5
}
```

**Response:**

```json
{
  "success": true,
  "event_id": 456
}
```

## Usage in Code

### Decorator Pattern

```python
from usage_meter import track_usage

@track_usage('ai_request', 'compute', quota_type='ai_requests')
def call_ai_model(prompt):
    # Function automatically tracked
    # Quota checked before execution
    # Event logged after execution
    return ai_response
```

### Manual Tracking

```python
from usage_meter import SmartMeter

# Track an event
SmartMeter.track_event(
    event_type='file_upload',
    event_category='storage',
    resource_name='video.mp4',
    file_size_bytes=15728640,  # 15 MB
    duration_seconds=2.5,
    cost_usd=0.0,
)

# Check quota
quota = UsageQuota.query.filter_by(user_id=user_id).first()
has_quota, error = quota.check_quota('files', amount=1)

if not has_quota:
    return jsonify({'error': error}), 429

# Increment quota
quota.increment_quota('files', amount=1)
```

### Initialize User Quota

```python
from usage_meter import SmartMeter

# Automatically sets limits based on user tier
quota = SmartMeter.initialize_user_quota(user_id)
```

## Dashboard UI

The unified workspace includes a real-time smart meter dashboard showing:

### Usage Meters (Progress Bars)

- AI Tokens (used/limit, percentage)
- AI Requests (count, percentage)
- Storage (MB used/limit, percentage)
- Files Uploaded (count, percentage)
- Analyses (count, percentage)
- Monthly Cost ($USD, percentage)

### Billing Period Info

- Current period dates
- Days remaining in period
- Auto-resets each month

### Recent Activity Feed

- Last 24 hours of events
- Event type, resource, tokens, cost
- Time stamp for each event
- Color-coded by status (success/error)

### Visual Indicators

- **Green**: 0-79% usage
- **Yellow**: 80-94% usage
- **Red**: 95-100% usage

## Tier-Based Limits

Limits are automatically configured based on user tier:

### FREE Tier

- 100K AI tokens/month
- 1GB storage
- 100 files/month
- 50 analyses/month
- $50 monthly budget

### PRO Tier

- 500K AI tokens/month
- 50GB storage
- 500 files/month
- 200 analyses/month
- $200 monthly budget

### ENTERPRISE Tier

- Unlimited tokens (-1)
- Unlimited storage (-1)
- Unlimited files (-1)
- Unlimited analyses (-1)
- Custom budget

## Migration

Run the migration to create tables:

```bash
python migrations/create_smart_meter_tables.py
```

Or manually in Python:

```python
from app import app
from models_auth import db
from usage_meter import SmartMeterEvent, UsageQuota

with app.app_context():
    SmartMeterEvent.__table__.create(db.engine, checkfirst=True)
    UsageQuota.__table__.create(db.engine, checkfirst=True)
```

## Integration Checklist

- [x] Database models created (`usage_meter.py`)
- [x] Migration script created
- [x] API endpoints added to `app.py`
- [x] Dashboard UI added to `unified-workspace.html`
- [x] JavaScript functions for real-time updates
- [x] Decorator pattern for automatic tracking
- [x] Tier-based quota initialization
- [x] Rate limiting implementation
- [x] Alert system for usage thresholds
- [x] Cost tracking per event
- [x] Client-side usage tracking

## Benefits

1. **Complete Visibility**: Track every user action
2. **Real-Time Enforcement**: Prevent quota overages instantly
3. **Fair Billing**: Accurate usage-based pricing
4. **User Transparency**: Dashboard shows exact usage
5. **Abuse Prevention**: Rate limiting and alerts
6. **Cost Control**: Track and limit spending
7. **Analytics**: Detailed usage patterns
8. **Compliance**: Audit trail for all activities

## Next Steps

1. Run database migration
2. Test quota initialization for existing users
3. Add usage tracking to existing endpoints
4. Configure tier limits
5. Set up alert email notifications
6. Add usage reports to admin dashboard
7. Implement overage billing integration
