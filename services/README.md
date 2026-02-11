# National Archives API Services

Core services for interacting with the National Archives NextGen Catalog API.

## Contents

- `nara_api_client.py` - Main API client with authentication, rate limiting, caching, and error handling

## Quick Usage

```python
from services.nara_api_client import NARAAPIClient

# Initialize client (reads NARA_API_KEY from environment)
client = NARAAPIClient()

# Search catalog
results = client.search_records(query="constitution", rows=10)

# Get specific document by NAID
record = client.get_record_by_naid("1667751")

# Get extracted text
text = client.get_extracted_text("1667751")

# Get transcriptions
transcriptions = client.get_transcriptions_by_naid("1667751")

# Clear cache
client.clear_cache()
```

## Features

- **Authentication**: Automatic API key management
- **Rate Limiting**: Enforces 2 requests/second
- **Caching**: Optional response caching with expiration
- **Retry Logic**: Automatic retries with exponential backoff
- **Error Handling**: Specific exceptions for different error types

## Configuration

Set in environment variables or `.env` file:

```bash
NARA_API_KEY=your-api-key
NARA_API_BASE_URL=https://catalog.archives.gov/api/v2
NARA_USER_UUID=your-uuid  # Optional, for write operations
```

## Documentation

Full documentation: [docs/NATIONAL_ARCHIVES_API.md](../docs/NATIONAL_ARCHIVES_API.md)

Quick start: [docs/NARA_QUICKSTART.md](../docs/NARA_QUICKSTART.md)
