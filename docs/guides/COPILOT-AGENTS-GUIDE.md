# 🤖 Evident Custom Copilot Agents

## Overview

This repository includes **8 specialized AI agents** built with GitHub Copilot
SDK to accelerate development of the Evident legal tech platform for BWC (Body
Worn Camera) forensic analysis.

## 🚀 Quick Start

### Setup

```bash
npm install
npm run setup:agents
```

### Using Agents in GitHub Copilot Chat

In your IDE with GitHub Copilot, invoke agents with `@agent-name`:

```
@legal-compliance Review this export function for copyright violations
@bwc-forensics Analyze this video processing pipeline
@flask-backend Add authentication to this API endpoint
@frontend-dev Create a responsive case list component
@database-architect Design a schema for evidence chain of custody
@security-devops Review security vulnerabilities in auth flow
@cloud-integration Implement Dropbox file sync for evidence uploads
@documentation Write a quick start guide for attorneys
```

## 📋 Available Agents

### 1. **@legal-compliance** - Legal Compliance Expert

**Expertise:** Copyright law, data rights, OPRA compliance, export validation

**Use Cases:**

- Review export functions for copyright violations
- Validate fair use compliance (200-word limits)
- Ensure proper attribution in reports
- Design rights-aware database schemas
- Prevent Westlaw/Lexis content republishing

**Key Files:** `data_rights.py`, `models_data_rights.py`,
`DATA-RIGHTS-COMPLIANCE.md`

**Example:**

```
@legal-compliance
Check if this PDF export violates Westlaw copyright terms
```

--

### 2. **@bwc-forensics** - BWC Forensic Analysis Specialist

**Expertise:** Video analysis, AI transcription, evidence integrity, chain of
custody

**Use Cases:**

- Implement video metadata extraction
- Integrate Whisper AI for transcription
- Build timeline reconstruction features
- Design evidence integrity verification
  - Prepare forensic reports intended to assist court submissions; final
    admissibility is determined by courts and counsel

**Key Files:** `bwc_forensic_analyzer.py`, `bwc_web_app.py`,
`BWC-ANALYSIS-GUIDE.md`

**Example:**

```
@bwc-forensics
Add SHA-256 hashing for video file integrity verification
```

--

### 3. **@cloud-integration** - Cloud Storage Integration Expert

**Expertise:** Cloud APIs (Dropbox, Google Drive, OneDrive), OAuth 2.0, file
sync, webhooks

**Use Cases:**

- Implement cloud storage provider integrations
- Build OAuth 2.0 authentication flows
- Create two-way file synchronization
- Set up webhook listeners for file changes
- Integrate Dropbox/Drive/OneDrive APIs
- Ensure chain of custody for cloud evidence

**Key Files:** `cloud_storage_integration.py`, `.env.template`, `SECURITY.md`

**Example:**

```
@cloud-integration
Implement Dropbox OAuth flow and evidence file sync with integrity verification
```

---

### 4. **@flask-backend** - Flask Backend Developer

**Expertise:** Flask APIs, authentication, database integration, security

**Use Cases:**

- Build REST API endpoints
- Implement role-based access control
- Design database migrations
- Integrate copyright compliance into exports
- Optimize query performance

**Key Files:** `app.py`, `auth_routes.py`, `models_auth.py`, `ROUTE-MAP.md`

**Example:**

```
@flask-backend
Create an API endpoint for bulk case export with attorney certification
```

--

### 5. **@frontend-dev** - Frontend UI/UX Developer

**Expertise:** React components, responsive design, accessibility, animations

**Use Cases:**

- Build attorney-friendly dashboards
- Create responsive case management UI
- Ensure WCAG AA accessibility
- Optimize hero animations (60fps)
- Design mobile-first layouts

**Key Files:** `index.html`, `assets/css/style.css`, `components/`, `admin.html`

**Example:**

```
@frontend-dev
Create a responsive evidence gallery component with keyboard navigation
```

--

### 6. **@database-architect** - Database Schema Designer

**Expertise:** SQLAlchemy ORM, migrations, data integrity, query optimization

**Use Cases:**

- Design normalized database schemas
- Create migration scripts
- Add indexes for performance
- Enforce data constraints
- Plan SQLite → PostgreSQL migration

**Key Files:** `models_auth.py`, `models_data_rights.py`,
`add_missing_columns.py`

**Example:**

```
@database-architect
Design a schema for multi-file BWC case management with chain of custody
```

--

### 7. **@security-devops** - Security & DevOps Engineer

**Expertise:** Application security, SSL/TLS, secrets management, CI/CD

**Use Cases:**

- Configure HTTPS for production
- Implement secrets management
- Set up GitHub Actions CI/CD
- Scan dependencies for vulnerabilities
- Create backup strategies

**Key Files:** `.github/workflows/`, `SECURITY.md`, `DEPLOYMENT-COMPLETE.md`

**Example:**

```
@security-devops
Configure SSL certificate and rotate SECRET_KEY for production deployment
```

--

### 8. **@documentation** - Technical Documentation Specialist

**Expertise:** Technical writing, API docs, user guides, compliance
documentation

**Use Cases:**

- Write attorney-friendly tutorials
- Document REST API endpoints
- Create quick start guides
- Maintain compliance documentation
- Organize project documentation

**Key Files:** `README-NEW.md`, `ADMIN-QUICK-START.md`,
`COPYRIGHT-QUICK-START.md`

**Example:**

```
@documentation
Write a 5-minute quick start guide for attorneys using the BWC analyzer
```

--

## 🎯 Best Practices

### Multi-Agent Workflows

Chain agents for complex tasks:

```
1. @database-architect Design export_manifests table
2. @flask-backend Create /api/export endpoint using that schema
3. @legal-compliance Review endpoint for copyright compliance
4. @documentation Document the new export API
5. @security-devops Add rate limiting to prevent abuse
```

### Agent Selection Guide

| Task Type         | Recommended Agent     |
| ----------------- | --------------------- |
| Export validation | `@legal-compliance`   |
| Video processing  | `@bwc-forensics`      |
| API endpoints     | `@flask-backend`      |
| UI components     | `@frontend-dev`       |
| Schema changes    | `@database-architect` |
| Cloud integration | `@cloud-integration`  |
| Deployment        | `@security-devops`    |
| User guides       | `@documentation`      |

### Code Review Workflow

```
@legal-compliance Review for copyright violations
@security-devops Review for security vulnerabilities
@frontend-dev Review for accessibility compliance
```

## 📊 Agent Comparison

| Agent              | Model             | Primary Focus     | Audience         |
| ------------------ | ----------------- | ----------------- | ---------------- |
| Legal Compliance   | Claude Sonnet 4.5 | Copyright law     | Attorneys        |
| BWC Forensics      | Claude Sonnet 4.5 | Video analysis    | Forensic experts |
| Cloud Integration  | Claude Sonnet 4.5 | Cloud APIs & sync | Cloud engineers  |
| Flask Backend      | Claude Sonnet 4.5 | API development   | Backend devs     |
| Frontend Dev       | Claude Sonnet 4.5 | UI/UX design      | Frontend devs    |
| Database Architect | Claude Sonnet 4.5 | Schema design     | Database admins  |
| Security DevOps    | Claude Sonnet 4.5 | Infrastructure    | DevOps engineers |
| Documentation      | Claude Sonnet 4.5 | Technical writing | End users        |

## 🔧 Configuration

Agents are configured in `.github/copilot-agents.yml`:

```yaml
agents:
  legal-compliance:
    name: "Evident Legal Compliance Expert"
    model: claude-sonnet-4.5
    tools: [view, edit, create, grep, glob, powershell]
    instructions: |
      Expert in copyright compliance...
```

### Customizing Agents

Edit `.github/copilot-agents.yml` to:

- Add new agents for specific domains
- Modify agent instructions
- Change tool permissions
- Switch AI models (Claude, GPT, etc.)

## 🚨 Critical Use Cases

### Before Production Launch

```bash
@legal-compliance Audit all export endpoints for copyright violations
@security-devops Run security scan and configure SSL
@database-architect Validate database schema and create migration plan
@documentation Update deployment guide with production checklist
```

### New Feature Development

```bash
@database-architect Design schema for new feature
@flask-backend Implement backend API
@frontend-dev Create UI components
@legal-compliance Review for compliance
@documentation Write user guide
@security-devops Security review and deployment
```

### Bug Fixes

```bash
@bwc-forensics Debug video processing failure
@flask-backend Fix API authentication issue
@frontend-dev Resolve responsive layout bug
```

## 📖 Documentation

- **Setup Guide:** This file
- **Legal Framework:** [DATA-RIGHTS-COMPLIANCE.md](../DATA-RIGHTS-COMPLIANCE.md)
- **Backend Guide:** [ADMIN-BACKEND-GUIDE.md](../ADMIN-BACKEND-GUIDE.md)
- **Frontend Guide:** [FRONTEND-COMPLETE.md](../FRONTEND-COMPLETE.md)
- **Deployment:** [LAUNCH-CHECKLIST.md](../LAUNCH-CHECKLIST.md)

## 🏆 Success Metrics

With custom agents, you should achieve:

- ✅ **50% faster development** (specialized context)
- ✅ **Zero copyright violations** (legal-compliance agent)
- ✅ **Consistent code quality** (domain-specific best practices)
- ✅ **Better documentation** (documentation agent)
- ✅ **Fewer security issues** (security-devops agent)

## 🆘 Support

**Agent Issues:**

- Check agent configuration in `.github/copilot-agents.yml`
- Verify GitHub Copilot extension is installed
- Ensure copilot-sdk is in package.json

**Technical Support:**

- support@Evident.info
- support@Evident.info

--

**Created:** January 23, 2026  
**Version:** 1.0  
**Status:** ✅ READY FOR USE
