# Local Worker Service Setup Guide

## Overview

The Local Worker Service is a companion application that runs on your machine to handle heavy processing tasks (OCR, Whisper transcription, vector indexing, graph computation) while keeping your data and API keys secure and under your control.

## Why Local Worker Service?

- **Security First**: API keys (OpenAI, Gemini, Claude) are stored in your OS keychain or encrypted-at-rest, never exposed to browser JavaScript
- **Data Privacy**: All processing happens locally; your documents never leave your machine unless you explicitly export
- **Full Features**: Enables OCR, transcription, semantic search, and graph analysis that would be impossible in a browser
- **Cost Control**: Set spending caps per provider, track token usage, and enable/disable providers as needed

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Browser PWA       │         │  Local Worker        │
│   (Static Files)    │◄────────┤  Service             │
│                     │  HTTP   │  (localhost:8080)    │
│  - UI & Rendering   │  API    │                      │
│  - Document Viewer  │         │  - OCR Engine        │
│  - Search UI        │         │  - Whisper           │
│  - Entity Explorer  │         │  - Vector DB         │
│  - Graph Viewer     │         │  - Graph DB          │
└─────────────────────┘         │  - API Keys (secure) │
                                └──────────────────────┘
```

## Installation Options

### Option 1: Docker Compose (Recommended)

**Prerequisites**: Docker and Docker Compose installed

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/public-records-platform.git
   cd public-records-platform/local-engine
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Verify health:
   ```bash
   curl http://localhost:8080/api/health
   ```

4. View pairing code:
   ```bash
   docker-compose logs engine | grep "Pairing Code"
   ```

### Option 2: Native Installation (Windows/macOS/Linux)

**Coming Soon**: Native installers will be available in GitHub Releases.

For now, you can build from source:

```bash
cd local-engine
npm install
npm run build
npm start
```

## Configuration

### Environment Variables

Create a `.env` file in the `local-engine` directory:

```env
# Server Configuration
PORT=8080
HOST=localhost

# Storage
DATA_DIR=./data
CACHE_DIR=./cache

# Database (embedded SQLite by default)
DATABASE_URL=sqlite:./data/platform.db

# Vector Database (embedded Qdrant by default)
VECTOR_DB_URL=http://localhost:6333

# Feature Flags
ENABLE_OCR=true
ENABLE_TRANSCRIPTION=true
ENABLE_EMBEDDINGS=true

# Processing Limits
MAX_CONCURRENT_JOBS=4
OCR_DPI=250
CHUNK_SIZE=1500
```

### Adding LLM Providers

Once the engine is running, you can add providers via the web UI or API:

**Via API**:
```bash
curl -X POST http://localhost:8080/api/providers \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "openai",
    "name": "My OpenAI Account",
    "credentials": {
      "apiKey": "sk-..."
    },
    "spendingCap": 100,
    "capabilities": ["embeddings", "summarization", "extraction"]
  }'
```

**Supported Providers**:
- **OpenAI**: GPT-4, GPT-3.5, text-embedding-ada-002
- **Google Gemini**: Gemini 1.5 Pro, Gemini 1.5 Flash
- **Anthropic Claude**: Claude 3.5 Sonnet, Claude 3 Opus
- **Local Models**: Ollama, LM Studio (embeddings and inference)

## Connecting the PWA

1. Open the PWA in your browser (hosted or `file://`)
2. Click the connection indicator in the top right
3. Select "Local Engine"
4. Enter the pairing code shown in your engine's terminal/logs
5. Confirm connection

The PWA will now have access to full processing capabilities while your API keys remain secure in the local service.

## Security Model

### API Key Storage

- **macOS/Linux**: Stored in system keychain (Keychain Access / Secret Service)
- **Windows**: Stored in Windows Credential Manager
- **Fallback**: AES-256 encrypted with user passphrase

### Session Tokens

- Browser receives short-lived JWT tokens (24h default)
- Tokens can be revoked instantly from the engine UI
- All API requests require valid token
- Tokens stored in browser localStorage with expiration

### Audit Logging

All LLM API calls are logged with:
- Provider name and model
- Purpose tag (OCR, summarization, extraction, etc.)
- Token counts (prompt + completion)
- Timestamp and user
- **Never** logs raw API keys or credentials

## Troubleshooting

### Engine Not Reachable

```bash
# Check if service is running
docker-compose ps

# View logs
docker-compose logs -f engine

# Restart service
docker-compose restart engine
```

### Pairing Failed

- Ensure the engine is running on `localhost:8080`
- Check firewall rules allow localhost connections
- Verify the pairing code is recent (expires after 5 minutes)
- Try generating a new pairing code

### OCR Not Working

- Verify Tesseract is installed (included in Docker)
- Check OCR feature flag: `ENABLE_OCR=true`
- Review logs for specific error messages
- Ensure sufficient disk space for rendered PDF pages

### High Memory Usage

- Reduce `MAX_CONCURRENT_JOBS` in `.env`
- Lower `OCR_DPI` for less memory-intensive processing
- Disable features you're not using (transcription, embeddings)

## Advanced: Team Server Deployment

For multi-user collaboration, the Local Worker Service can be deployed on a private server:

1. Deploy using docker-compose on a server with HTTPS enabled
2. Configure RBAC roles (Admin, Analyst, Reviewer, ReadOnly)
3. Set up project-based access control
4. Use server-side API keys (never expose to clients)
5. Enable audit logging and retention policies

See [TEAM_DEPLOYMENT.md](./TEAM_DEPLOYMENT.md) for full instructions.

## Support

- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/public-records-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/public-records-platform/discussions)

## License

[Your License Here]
