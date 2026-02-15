# Public Records Analysis Platform

**Evidence-first analysis of official DOJ Epstein Library releases from justice.gov/epstein**

## Overview

This platform provides audit-grade analysis capabilities for lawfully published public records from the U.S. Department of Justice Epstein Library. It demonstrates a distributed architecture where a browser-based PWA interface connects to local or team-based processing engines for OCR, entity extraction, relationship graphs, and semantic search.

## Current Status: Browser-Only Mode

This release provides the **complete user interface** designed for analyzing official DOJ document releases. The UI shows the data structures, workflows, and visualization patterns that will display real results when connected to a Local Worker Service.

**What's included now:**
- ✅ Full UI for sources, ingestion runs, documents, search, entities, and graphs
- ✅ Connection management for Local Engine and Team Server modes
- ✅ Analysis scripts framework with quality scoring and review queues
- ✅ Provenance tracking and audit log interfaces
- ✅ Export and reporting templates with citation patterns
- ✅ Evidence-backed relationship visualization

**What requires Local Engine (coming soon):**
- ⏳ Actual web crawling of justice.gov/epstein
- ⏳ PDF download and OCR processing
- ⏳ Entity extraction via LLM providers
- ⏳ Vector search and graph computation
- ⏳ Audio transcription (Whisper)

See `DOJ_DATA_SOURCE.md` for complete details on data sources, compliance requirements, and Local Engine setup.

## Key Features

### Evidence-Backed Analysis
- Every entity mention cites source documents with page numbers and snippets
- Relationship edges reference specific text chunks and confidence scores
- No accusatory conclusions—only documented co-occurrence and references

### Chain-of-Custody Provenance
- SHA-256 hashes for all downloaded files
- Timestamped discovery records (`discovered_from` URL tracking)
- Processing version tracking for reproducibility
- Tamper-evident audit logs

### Multi-Mode Architecture
- **Browser-Only**: UI demonstration with DOJ data structures
- **Local Engine**: Full processing on your machine with your API keys
- **Team Server**: Multi-user collaboration with RBAC

### Compliance by Design
- Respects Queue-it traffic management
- Honors age verification gates
- Polite rate limiting (default: 5 req/min)
- Never bypasses access controls
- Compliance reports for every ingestion run

### Analysis Capabilities
- Keyword + semantic search with highlighting
- Entity extraction (people, orgs, locations, dates)
- Relationship graph with evidence filtering
- Custom analysis scripts (pattern scanning, timeline building)
- Review queues for disambiguation and quality control

## Quick Start

1. **Explore the UI** (Browser-Only Mode)
   - Open the app
   - Browse Sources, Documents, Entities, and Graph views
   - See provenance tracking and evidence panels
   - Review audit log and system architecture

2. **Install Local Engine** (for full processing)
   - Download from GitHub Releases (coming soon)
   - Or use Docker: `docker-compose up -d`
   - Connect via pairing code

3. **Configure Sources**
   - Add DOJ Epstein Library: `https://www.justice.gov/epstein`
   - Set crawl rules and rate limits
   - Enable Queue-it detection

4. **Run Ingestion**
   - Crawl → Download → Extract → OCR → Index → Analyze
   - Monitor progress and errors
   - Review provenance for every file

5. **Search & Analyze**
   - Run keyword or semantic searches
   - Browse extracted entities
   - Explore relationship graphs
   - Export evidence bundles with citations

## Architecture

### Browser PWA (This Repository)
- React + TypeScript + Tailwind CSS
- Shadcn UI components
- PWA-ready for offline viewing
- Connects to Local Engine via localhost API

### Local Worker Service (Separate Repository - Coming Soon)
- Python/Node backend with job queues
- OCR (Tesseract), Whisper, vector DB (Qdrant/pgvector)
- Secure API key storage (OS keychain)
- Horizontal scaling for millions of pages

### Data Flow
```
justice.gov/epstein
  → Crawler (polite, respects controls)
    → Downloader (SHA-256, provenance)
      → Text Extraction (native + OCR fallback)
        → Chunking & Indexing (keyword + semantic)
          → Entity Extraction (LLM-based)
            → Relationship Graph (evidence-backed)
              → Browser UI (search, explore, export)
```

## Data Source

**Primary**: https://www.justice.gov/epstein
- Official DOJ document releases
- Court filings, depositions, legal records
- Subject to age verification and Queue-it controls

**Secondary** (optional): https://www.justice.gov/epstein/doj-disclosures
- Additional disclosure subfolder

See `DOJ_DATA_SOURCE.md` for:
- Access control compliance requirements
- Crawling policies and rate limits
- Ethical use guidelines
- Legal disclaimers

## Documentation

- **Product Requirements**: `PRD.md` — Complete feature specification
- **Data Source Guide**: `DOJ_DATA_SOURCE.md` — Official sources and compliance
- **Security Policy**: `SECURITY.md` — API keys, audit logs, and access control
- **Setup Guide**: `LOCAL_ENGINE_SETUP.md` — Installing the processing engine (coming soon)

## Ethical Use & Disclaimers

### This Platform Is Designed For
- Lawful analysis of public records
- Evidence-backed journalism and research
- Audit-grade provenance and chain-of-custody
- Human-verified findings with full citations

### This Platform Must NOT Be Used For
- Generating accusation lists or "suspect databases"
- Automated conclusions of guilt
- Bypassing site protections or access controls
- Doxxing or vigilante targeting
- Processing private materials without authorization

### User Responsibilities
1. Only process content you are authorized to access
2. Verify all findings against original source documents
3. Respect site terms, robots directives, and access controls
4. Use redaction controls for sensitive exports
5. Never publish unverified claims based on probabilistic analysis

**Every analysis output includes warnings** that results are probabilistic and must be verified by reading source passages.

## Technology Stack

- **Frontend**: React 19, TypeScript, Tailwind CSS v4, Shadcn UI
- **Charts**: D3.js, Recharts
- **Icons**: Phosphor Icons
- **State**: React hooks + KV storage (persistent)
- **Build**: Vite 7
- **Backend** (Local Engine): Python/Node, PostgreSQL, Qdrant/pgvector, Neo4j (optional)

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Contributing

This is a demonstration of architecture and UI patterns for evidence-first analysis platforms. Contributions should focus on:

- Improving provenance tracking patterns
- Enhancing evidence citation UX
- Adding safeguards against misuse
- Documentation for ethical use

See GitHub Issues for open items.

## License

MIT License - Copyright GitHub, Inc.

See `LICENSE` file for details.

## Support

- **Issues**: GitHub Issues
- **Documentation**: See `/docs` folder and markdown files in repo root
- **Security**: See `SECURITY.md` for reporting vulnerabilities

---

**Status**: Browser UI complete; Local Engine in development  
**Target Dataset**: https://www.justice.gov/epstein  
**Architecture**: PWA + Local Worker Service (distributed)  
**Principle**: Evidence-backed analysis without accusatory conclusions
