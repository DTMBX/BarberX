# National Archives API Integration

Complete system for retrieving and maintaining founding documents and treaties from
the National Archives using their NextGen Catalog API v2.

## Overview

This integration provides:

- **Automated Document Retrieval**: Fetch Constitution, Bill of Rights, treaties,
  and other founding documents
- **Scheduled Updates**: Automatic periodic refresh of documents
- **Webhook Support**: Trigger updates via HTTP webhooks
- **Cache Management**: Efficient API response caching
- **Integrity Verification**: Automated document validation
- **Chain of Custody**: Complete audit trail for all retrieved documents

## Architecture

```
services/
  └── nara_api_client.py          # Core API client with rate limiting & caching

scripts/
  ├── fetch_founding_documents.py # Document retrieval script
  └── nara_scheduler.py           # Automated task scheduler

routes/
  └── nara_webhook.py             # Flask webhook & API endpoints

documents/founding/
  ├── constitution.md             # Retrieved documents stored here
  ├── bill-of-rights.md
  └── ...
```

## Setup

### 1. Get API Key

Contact the National Archives to obtain an API key:

- **Email**: Catalog_API@nara.gov
- **Subject**: "API Key Request for [Your Organization]"

### 2. Configure Environment

Add to your `.env` file:

```bash
# National Archives API
NARA_API_KEY=your-api-key-here
NARA_API_BASE_URL=https://catalog.archives.gov/api/v2
NARA_USER_UUID=your-user-uuid  # Optional, for write operations
NARA_WEBHOOK_SECRET=random-secret-key  # Optional, for webhook security
```

### 3. Install Dependencies

The integration requires:

```bash
pip install requests python-dotenv
```

Already included in `requirements.txt`.

## Usage

### Command Line

Fetch all founding documents:

```bash
python scripts/fetch_founding_documents.py
```

Fetch specific document:

```bash
python scripts/fetch_founding_documents.py --document constitution
```

Fetch all documents and treaties:

```bash
python scripts/fetch_founding_documents.py --all
```

### Programmatic Usage

```python
from services.nara_api_client import NARAAPIClient

# Initialize client
client = NARAAPIClient()

# Search records
results = client.search_records(query="constitution", rows=10)

# Get specific document
record = client.get_record_by_naid("1667751")

# Get extracted text
text = client.get_extracted_text("1667751")
```

### Automated Scheduling

Run scheduler once:

```bash
python scripts/nara_scheduler.py
```

Run as daemon (continuous):

```bash
python scripts/nara_scheduler.py --daemon
```

Custom intervals:

```bash
python scripts/nara_scheduler.py --daemon \
  --update-interval 48 \
  --verify-interval 24
```

### Flask Integration

Add to your Flask app:

```python
from routes.nara_webhook import register_nara_routes

# Register webhook routes
register_nara_routes(app)
```

Available endpoints:

- `POST /api/nara/webhook` - Webhook handler
- `POST /api/nara/refresh` - Manual refresh trigger (requires auth)
- `GET /api/nara/status` - Document status
- `GET /api/nara/verify` - Integrity verification

## Available Documents

### Founding Documents

- **Constitution** (NAID: 1667751)
- **Bill of Rights** (NAID: 1408042)
- **Declaration of Independence** (NAID: 1419123)
- **Articles of Confederation** (NAID: 1408033)
- **Federalist Papers** (search-based)
- **Emancipation Proclamation** (NAID: 299998)

### Treaties

- **Treaty of Paris (1783)** (NAID: 299808)
- **Louisiana Purchase Treaty** (NAID: 299810)

Add more documents in `scripts/fetch_founding_documents.py` by updating the
`FOUNDING_DOCUMENTS` and `TREATIES` dictionaries.

## Webhook Setup

### Manual Trigger

```bash
curl -X POST http://localhost:5000/api/nara/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "document.refresh_all",
    "timestamp": "2026-02-09T00:00:00Z"
  }'
```

### Scheduled via Cron (Linux/Mac)

```cron
# Update documents daily at 2 AM
0 2 * * * cd /path/to/Evident && python scripts/fetch_founding_documents.py
```

### Scheduled via Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `scripts\fetch_founding_documents.py`
7. Start in: `C:\web-dev\github-repos\Evident`

### GitHub Actions Automation

Create `.github/workflows/update-documents.yml`:

```yaml
name: Update Founding Documents

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests python-dotenv
      
      - name: Fetch documents
        env:
          NARA_API_KEY: ${{ secrets.NARA_API_KEY }}
        run: |
          python scripts/fetch_founding_documents.py --all
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add documents/founding/
          git diff --staged --quiet || git commit -m "Update founding documents [automated]"
          git push
```

## API Client Features

### Rate Limiting

Automatically enforces 2 requests/second to respect API limits:

```python
client = NARAAPIClient()
# Rate limiting is automatic
client.search_records(query="treaty")
client.search_records(query="proclamation")
```

### Response Caching

Cache API responses to reduce API calls:

```python
client = NARAAPIClient(cache_dir="cache/nara")

# First call hits API
results = client.search_records(query="constitution")

# Second call uses cache (within 24 hours)
results = client.search_records(query="constitution")

# Force fresh data
client.clear_cache()
```

### Error Handling

```python
from services.nara_api_client import (
    NARAAPIError,
    NARAAuthenticationError,
    NARARateLimitError
)

try:
    client = NARAAPIClient()
    record = client.get_record_by_naid("1667751")
except NARAAuthenticationError:
    print("Invalid API key")
except NARARateLimitError as e:
    print(f"Rate limited: {e}")
except NARAAPIError as e:
    print(f"API error: {e}")
```

### Retry Logic

Automatic retries with exponential backoff for transient failures:

```python
client = NARAAPIClient(max_retries=3)
# Will retry up to 3 times on 5xx errors
```

## Document Format

Retrieved documents are saved as Markdown with complete metadata:

```markdown
# Constitution of the United States

**Official Source:** National Archives of the United States
**NAID:** 1667751
**Source URL:** https://catalog.archives.gov/id/1667751
**Retrieved:** February 9, 2026

> Note: This document was retrieved from the National Archives Catalog
> using the NextGen Catalog API. Content is preserved as recorded by
> the National Archives.

---

## Document Text

[Full text content here]

---

## Retrieval Metadata

- **Retrieved:** 2026-02-09T12:00:00
- **NAID:** 1667751
- **API Version:** NextGen Catalog API v2
- **Retrieval Method:** Automated via NARA API Client

### Chain of Custody

1. **Source Authority:** National Archives of the United States
2. **Retrieval System:** Evident Technologies Document Management
3. **Verification:** Content retrieved via authenticated API connection
4. **Integrity:** Original formatting and metadata preserved
```

## Monitoring & Verification

### Check Document Status

```bash
curl http://localhost:5000/api/nara/status
```

Response:

```json
{
  "timestamp": "2026-02-09T12:00:00",
  "documents": [
    {
      "filename": "constitution.md",
      "naid": "1667751",
      "size_bytes": 45230,
      "last_modified": "2026-02-09T10:00:00",
      "exists": true
    }
  ],
  "last_automatic_check": "2026-02-09T10:00:00",
  "next_check_due": "2026-02-10T10:00:00"
}
```

### Verify Document Integrity

```bash
curl http://localhost:5000/api/nara/verify
```

Response:

```json
{
  "timestamp": "2026-02-09T12:00:00",
  "total": 8,
  "valid": 8,
  "warnings": [],
  "documents": [
    {
      "filename": "constitution.md",
      "valid": true,
      "checks": {
        "size": {"pass": true, "value": 45230},
        "has_naid": {"pass": true},
        "has_source": {"pass": true},
        "has_timestamp": {"pass": true}
      }
    }
  ]
}
```

## Security Considerations

### API Key Protection

- **Never commit** `.env` files to version control
- Store API keys in environment variables or secure vaults
- Rotate keys periodically
- Use read-only keys when possible

### Webhook Security

Enable signature verification:

```bash
# Generate webhook secret
openssl rand -hex 32

# Add to .env
NARA_WEBHOOK_SECRET=your-generated-secret
```

Webhook requests must include `X-NARA-Signature` header with HMAC-SHA256 signature.

### Rate Limiting

Respect National Archives API limits:

- Maximum 2 requests/second (enforced by client)
- Implement exponential backoff on errors
- Use caching to minimize API calls

## Troubleshooting

### API Key Issues

```
NARAAuthenticationError: Authentication failed
```

**Solution**: Verify your API key is correct. Contact Catalog_API@nara.gov if needed.

### Rate Limiting

```
NARARateLimitError: Rate limit exceeded
```

**Solution**: Client automatically handles rate limiting. If you're using multiple
clients, coordinate requests or increase sleep intervals.

### Missing Documents

Some documents may not have transcriptions available via API. Manual verification at
https://catalog.archives.gov may be required.

### Cache Issues

Clear cache if stale data persists:

```python
client = NARAAPIClient()
client.clear_cache()
```

Or manually delete cache files in `cache/nara/`.

## API Reference

Full API documentation: https://catalog.archives.gov/api/v2/swagger.json

### Common Endpoints

- `GET /records/search` - Search catalog
- `GET /records/parentNaId/{parentNaId}` - Get child records
- `GET /transcriptions/naId/{naId}` - Get transcriptions
- `GET /extractedText/{naId}` - Get extracted text
- `GET /tags/naId/{naId}` - Get tags
- `POST /tags/` - Add tag (requires UUID)

## Support

### National Archives API

- **Email**: Catalog_API@nara.gov
- **Documentation**: https://catalog.archives.gov/api/v2/swagger.json
- **Catalog**: https://catalog.archives.gov

### Evident Technologies

- **GitHub**: https://github.com/DTMBX/EVIDENT
- **Issues**: https://github.com/DTMBX/EVIDENT/issues

## License

This integration is part of the Evident Technologies system and follows the same
license as the main project.

API usage must comply with National Archives terms of service.

---

## Implementation Notes

This system prioritizes:

1. **Evidence Integrity**: Original formatting preserved
2. **Auditability**: Complete chain of custody
3. **Reliability**: Automatic retries and error handling
4. **Efficiency**: Response caching and rate limiting
5. **Maintainability**: Clear documentation and logging

All operations maintain truth, structure, and restraint as prescribed by
Evident Technologies standards.
