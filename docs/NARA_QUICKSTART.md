# National Archives API Quick Start

Get founding documents from the National Archives in 5 minutes.

## Step 1: Get API Key

Contact National Archives:

```
Email: Catalog_API@nara.gov
Subject: API Key Request - [Your Organization Name]

Body:
We are requesting an API key for the NextGen Catalog API v2.

Organization: [Your Org]
Purpose: Retrieving founding documents for [your purpose]
Contact: [Your Name] - [Your Email]
```

## Step 2: Configure

Add to `.env`:

```bash
NARA_API_KEY=your-api-key-from-nara
```

## Step 3: Fetch Documents

```bash
python scripts/fetch_founding_documents.py
```

Done! Documents are in `documents/founding/`.

## Step 4: Automate (Optional)

### Option A: Run Daily via Scheduler

**Windows** (Task Scheduler):
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts\fetch_founding_documents.py" -WorkingDirectory "C:\web-dev\github-repos\Evident"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "UpdateFoundingDocs" -Description "Daily National Archives update"
```

**Linux/Mac** (cron):
```bash
# Add to crontab
0 2 * * * cd /path/to/Evident && python scripts/fetch_founding_documents.py
```

### Option B: Run as Background Service

```bash
python scripts/nara_scheduler.py --daemon
```

### Option C: GitHub Actions

Already configured in `.github/workflows/update-documents.yml`.

Add secret in GitHub:
- Go to repository Settings → Secrets → Actions
- Add `NARA_API_KEY` with your API key

## Usage Examples

### Fetch Specific Document

```bash
python scripts/fetch_founding_documents.py --document constitution
```

### Fetch All Documents

```bash
python scripts/fetch_founding_documents.py --all
```

### Check Status

```bash
curl http://localhost:5000/api/nara/status
```

### Manual Refresh via API

```bash
curl -X POST http://localhost:5000/api/nara/refresh \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

## What Gets Downloaded

- Constitution (NAID: 1667751)
- Bill of Rights (NAID: 1408042)
- Declaration of Independence (NAID: 1419123)
- Articles of Confederation (NAID: 1408033)
- Federalist Papers
- Emancipation Proclamation (NAID: 299998)
- Treaty of Paris (1783)
- Louisiana Purchase Treaty

## Programmatic Use

```python
from services.nara_api_client import NARAAPIClient

# Initialize
client = NARAAPIClient()

# Search
results = client.search_records(query="constitution")

# Get specific document
doc = client.get_record_by_naid("1667751")

# Get text
text = client.get_extracted_text("1667751")
```

## Troubleshooting

### "Authentication failed"

Check your API key in `.env`. Make sure it matches the key from National Archives.

### "Rate limit exceeded"

Wait 60 seconds and try again. The client automatically throttles requests.

### Missing transcriptions

Some documents don't have API transcriptions. Visit https://catalog.archives.gov/id/[NAID] directly.

## Full Documentation

See [docs/NATIONAL_ARCHIVES_API.md](NATIONAL_ARCHIVES_API.md) for complete documentation.

## Support

- **National Archives**: Catalog_API@nara.gov
- **GitHub Issues**: https://github.com/DTMBX/EVIDENT/issues
