# Local Development — Evident Discovery Suite

## Prerequisites

- Docker Desktop with `docker compose` v2+
- PowerShell 7+ (`pwsh`)

## Quick Start (Docker)

```powershell
cd bwc/ops/docker
docker compose up --build
```

## Endpoints

| Service | URL | Credentials |
| ------- | --- | ----------- |
| Backend health | `http://localhost:8000/health` | — |
| Frontend | `http://localhost:3000` | — |
| MinIO console | `http://localhost:9001` | minioadmin / minioadmin |
| PostgreSQL | `localhost:5432` | evident / evident |
| Redis | `localhost:6379` | — |

## Environment

- Copy `.env.example` → `.env` (already done by bootstrap)
- All secrets are in `.env` (gitignored). Edit `.env.example` for defaults.

## RAG Context Pack

Rebuild after any file changes:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File bwc\Update-RagContext.ps1
```

Verify integrity:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File bwc\Verify-Integrity.ps1
```

Run tests:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File bwc\tests\Test-RagContext.ps1
```

## Key Files

- `bwc/rag_context/file_index.json` — SHA-256 indexed file manifest (v2 schema)
- `bwc/rag_context/repo_tree.txt` — Directory structure snapshot
- `bwc/rag_context/integrity_statement.json` — Cryptographic integrity proof
- `bwc/rag_context/audit_log.jsonl` — Append-only event log
- `bwc/rag_context/verification_report.txt` — Human-readable verification report
- `bwc/RAG_UPGRADE_PROMPT.md` — Grounded upgrade plan for RAG systems
