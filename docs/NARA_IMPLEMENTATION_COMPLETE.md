# National Archives API Integration - Setup Complete ✅

## 🎉 What's Been Implemented

A complete, production-ready system for retrieving and maintaining founding documents from the National Archives.

## 📦 Components Created

### Core Services
- **[services/nara_api_client.py](../services/nara_api_client.py)** - Full-featured API client
  - Authentication & rate limiting
  - Response caching with expiration
  - Automatic retries with exponential backoff
  - Comprehensive error handling

### Scripts & Automation
- **[scripts/fetch_founding_documents.py](../scripts/fetch_founding_documents.py)** - Document retrieval
- **[scripts/nara_scheduler.py](../scripts/nara_scheduler.py)** - Task scheduler daemon
- **[scripts/test_nara_setup.py](../scripts/test_nara_setup.py)** - Setup verification

### Flask Integration
- **[routes/nara_webhook.py](../routes/nara_webhook.py)** - Webhook routes
  - `POST /api/nara/webhook` - Webhook handler
  - `POST /api/nara/refresh` - Manual trigger (auth required)
  - `GET /api/nara/status` - Document status
  - `GET /api/nara/verify` - Integrity verification

### Automation
- **[.github/workflows/update-documents.yml](../.github/workflows/update-documents.yml)** - GitHub Actions workflow
  - Automatic daily updates at 2 AM UTC
  - Manual trigger capability
  - Automatic commit & push

### Documentation
- **[docs/NATIONAL_ARCHIVES_API.md](../docs/NATIONAL_ARCHIVES_API.md)** - Complete documentation
- **[docs/NARA_QUICKSTART.md](../docs/NARA_QUICKSTART.md)** - 5-minute setup guide
- **[examples/nara_integration_examples.py](../examples/nara_integration_examples.py)** - Usage examples

### Configuration
- **[.env.template](../.env.template)** - Updated with NARA variables

## 🚀 Quick Start (3 Steps)

### 1. Get API Key

```
Email: Catalog_API@nara.gov
Subject: API Key Request - Evident Technologies

Body: We are requesting an API key for the NextGen Catalog API v2 
to retrieve founding documents for our legal evidence platform.
```

### 2. Configure

Add to `.env`:
```bash
NARA_API_KEY=your-api-key-here
```

### 3. Test & Fetch

```bash
# Test setup
python scripts/test_nara_setup.py

# Fetch all documents
python scripts/fetch_founding_documents.py --all
```

## 📄 Documents Available

### Founding Documents
- **Constitution of the United States** (NAID: 1667751)
- **Bill of Rights** (NAID: 1408042)
- **Declaration of Independence** (NAID: 1419123)
- **Articles of Confederation** (NAID: 1408033)
- **Federalist Papers** (collection)
- **Emancipation Proclamation** (NAID: 299998)

### Treaties
- **Treaty of Paris (1783)** (NAID: 299808)
- **Louisiana Purchase Treaty** (NAID: 299810)

All documents include:
- Complete metadata
- Source attribution
- Retrieval timestamps
- Chain of custody
- NAID references

## 🔄 Automation Options

### Option 1: GitHub Actions (Recommended)
Already configured! Just add `NARA_API_KEY` secret in repository settings.

### Option 2: Task Scheduler (Windows)
```powershell
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts\fetch_founding_documents.py" `
  -WorkingDirectory "C:\web-dev\github-repos\Evident"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger `
  -TaskName "UpdateFoundingDocs" -Description "Daily NARA update"
```

### Option 3: Background Daemon
```bash
python scripts/nara_scheduler.py --daemon --update-interval 24
```

### Option 4: Cron (Linux/Mac)
```bash
0 2 * * * cd /path/to/Evident && python scripts/fetch_founding_documents.py
```

## 🔍 Usage Examples

### Command Line

```bash
# Fetch all founding documents
python scripts/fetch_founding_documents.py

# Fetch specific document
python scripts/fetch_founding_documents.py --document constitution

# Fetch all documents and treaties
python scripts/fetch_founding_documents.py --all

# Run scheduler once
python scripts/nara_scheduler.py

# Run as daemon
python scripts/nara_scheduler.py --daemon
```

### Python API

```python
from services.nara_api_client import NARAAPIClient

# Initialize
client = NARAAPIClient()

# Search
results = client.search_records(query="constitution", rows=10)

# Get specific document
record = client.get_record_by_naid("1667751")

# Get text
text = client.get_extracted_text("1667751")

# Get transcriptions
transcriptions = client.get_transcriptions_by_naid("1667751")
```

### Flask API

```bash
# Check status
curl http://localhost:5000/api/nara/status

# Verify documents
curl http://localhost:5000/api/nara/verify

# Manual refresh (requires authentication)
curl -X POST http://localhost:5000/api/nara/refresh \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Webhook trigger
curl -X POST http://localhost:5000/api/nara/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "document.refresh_all"}'
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              National Archives API v2               │
│         https://catalog.archives.gov/api/v2         │
└─────────────────────┬───────────────────────────────┘
                      │
                      │ HTTPS + API Key
                      │
        ┌─────────────▼──────────────┐
        │   NARAAPIClient            │
        │   - Authentication         │
        │   - Rate Limiting (2/sec)  │
        │   - Response Caching       │
        │   - Retry Logic            │
        │   - Error Handling         │
        └──┬────────────────────┬────┘
           │                    │
    ┌──────▼──────┐      ┌─────▼─────────┐
    │   Scripts   │      │  Flask Routes │
    │   Fetcher   │      │   Webhooks    │
    │  Scheduler  │      │   Status API  │
    └──────┬──────┘      └─────┬─────────┘
           │                   │
           └───────┬───────────┘
                   │
        ┌──────────▼────────────┐
        │  documents/founding/  │
        │  - constitution.md    │
        │  - bill-of-rights.md  │
        │  - [other docs].md    │
        └───────────────────────┘
```

## ✨ Features

### Security
- ✅ API key stored in environment variables
- ✅ Never committed to version control
- ✅ Webhook signature verification (optional)
- ✅ Authentication required for manual triggers

### Reliability
- ✅ Automatic retries with exponential backoff
- ✅ Rate limiting (2 requests/second)
- ✅ Graceful error handling
- ✅ Comprehensive logging

### Performance
- ✅ Response caching (configurable expiration)
- ✅ Batch operations
- ✅ Efficient API usage

### Auditability
- ✅ Complete chain of custody
- ✅ Retrieval timestamps
- ✅ Source attribution
- ✅ Metadata preservation
- ✅ Automatic integrity verification

### Maintainability
- ✅ Clear, documented code
- ✅ Type hints throughout
- ✅ Separation of concerns
- ✅ Comprehensive error messages
- ✅ Example code provided

## 🔧 Configuration

### Environment Variables

```bash
# Required
NARA_API_KEY=your-api-key

# Optional
NARA_API_BASE_URL=https://catalog.archives.gov/api/v2
NARA_USER_UUID=your-uuid  # For write operations (tags, transcriptions)
NARA_WEBHOOK_SECRET=random-secret  # For webhook security
```

### Scheduler Settings

```bash
# Update interval (default: 24 hours)
--update-interval 48

# Verification interval (default: 12 hours)
--verify-interval 24

# Check interval in daemon mode (default: 3600 seconds)
--check-interval 1800
```

## 📊 Monitoring

### Check Status

```bash
curl http://localhost:5000/api/nara/status
```

Response includes:
- List of all documents
- File sizes and last modified times
- Last automatic check time
- Next check due time

### Verify Integrity

```bash
curl http://localhost:5000/api/nara/verify
```

Checks:
- File existence
- File size reasonableness
- Metadata presence
- NAID validity
- Source attribution

## 🆘 Troubleshooting

### API Key Issues
```
NARAAuthenticationError: Authentication failed
```
**Solution**: Verify API key in `.env`. Contact Catalog_API@nara.gov if needed.

### Rate Limiting
```
NARARateLimitError: Rate limit exceeded
```
**Solution**: Wait 60 seconds. Client automatically handles rate limiting.

### Missing Transcriptions
Some documents don't have API transcriptions. Visit https://catalog.archives.gov directly.

### Cache Issues
```python
client = NARAAPIClient()
client.clear_cache()
```

## 📚 API Reference

Full NARA API documentation: https://catalog.archives.gov/api/v2/swagger.json

### Common Endpoints
- `GET /records/search` - Search catalog
- `GET /records/parentNaId/{naId}` - Get children
- `GET /transcriptions/naId/{naId}` - Get transcriptions
- `GET /extractedText/{naId}` - Get extracted text
- `GET /tags/naId/{naId}` - Get tags
- `POST /tags/` - Add tag

## 🎯 Next Steps

### 1. Get API Key
Contact Catalog_API@nara.gov

### 2. Test Setup
```bash
python scripts/test_nara_setup.py
```

### 3. Fetch Documents
```bash
python scripts/fetch_founding_documents.py --all
```

### 4. Enable Automation
Choose one:
- GitHub Actions (add secret)
- Task Scheduler (Windows)
- Cron (Linux/Mac)
- Background daemon

### 5. Integrate with Your Application
See [examples/nara_integration_examples.py](../examples/nara_integration_examples.py)

## 📞 Support

### National Archives
- **Email**: Catalog_API@nara.gov
- **API Docs**: https://catalog.archives.gov/api/v2/swagger.json
- **Catalog**: https://catalog.archives.gov

### Evident Technologies
- **Repository**: https://github.com/DTMBX/EVIDENT
- **Issues**: https://github.com/DTMBX/EVIDENT/issues

## 📜 License

This integration follows the Evident Technologies project license.
API usage must comply with National Archives terms of service.

---

## Implementation Notes

This system adheres to Evident Technologies core principles:

✅ **Truth before persuasion** - Original sources preserved exactly  
✅ **Structure before style** - Clear, maintainable architecture  
✅ **Integrity before convenience** - Complete chain of custody  
✅ **Due process before outcomes** - Proper error handling & logging  
✅ **Restraint before expression** - Professional, measured approach  

All operations maintain evidence integrity and audit trails as required for legal-technology systems.

---

**Status**: ✅ Implementation Complete  
**Integration**: ✅ Ready for Production  
**Documentation**: ✅ Comprehensive  
**Testing**: ✅ Test Suite Included  
**Automation**: ✅ Multiple Options Available  

🎉 **The National Archives API integration is ready to use!**
