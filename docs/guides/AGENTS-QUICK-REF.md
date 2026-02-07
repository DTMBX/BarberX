# Evident Custom Agents - Quick Reference Card

## 🚀 Quick Setup

```bash
npm install
npm run setup:agents
python scripts/validate-agents.py
```

## 🤖 The 7 Agents

### @legal-compliance

**Use for:** Copyright violations, export validation, attribution  
**Example:** `@legal-compliance Review this PDF export for Westlaw violations`

### @bwc-forensics

**Use for:** Video analysis, transcription, evidence integrity  
**Example:** `@bwc-forensics Add SHA-256 hashing for chain of custody`

### @flask-backend

**Use for:** APIs, authentication, database integration  
**Example:** `@flask-backend Create bulk export endpoint with rate limiting`

### @frontend-dev

**Use for:** UI components, responsive design, accessibility  
**Example:** `@frontend-dev Build mobile-first case list with pagination`

### @database-architect

**Use for:** Schema design, migrations, query optimization  
**Example:** `@database-architect Design table for speaker diarization`

### @security-devops

**Use for:** SSL, secrets, CI/CD, vulnerability scanning  
**Example:** `@security-devops Configure production SSL and rotate keys`

### @documentation

**Use for:** User guides, API docs, tutorials  
**Example:** `@documentation Write 5-min quick start for attorneys`

--

## 📋 Common Workflows

### New Feature

1. `@database-architect` - Design schema
2. `@flask-backend` - Implement API
3. `@frontend-dev` - Create UI
4. `@legal-compliance` - Review compliance
5. `@security-devops` - Security review
6. `@documentation` - Write guide

### Bug Fix

1. `@bwc-forensics` or `@flask-backend` - Debug issue
2. `@security-devops` - Review security impact
3. `@documentation` - Update docs

### Pre-Production

1. `@legal-compliance` - Audit exports
2. `@security-devops` - Security scan + SSL
3. `@database-architect` - Validate schema
4. `@documentation` - Update deployment guide

### Code Review

1. `@legal-compliance` - Check data handling
2. `@security-devops` - Find vulnerabilities
3. `@frontend-dev` - Verify accessibility

--

## 💡 Pro Tips

- **Chain agents** for complex tasks (e.g., schema → API → UI → docs)
- **Use specific prompts** ("Add rate limiting" vs "improve security")
- **Include context** (paste relevant code for review)
- **Ask follow-ups** (agents maintain context in conversation)
- **Request examples** ("show curl example for this endpoint")

--

## 📖 Documentation

- **Full Guide:** [COPILOT-AGENTS-GUIDE.md](COPILOT-AGENTS-GUIDE.md)
- **Installation Summary:**
  [AGENTS-INSTALLATION-COMPLETE.md](AGENTS-INSTALLATION-COMPLETE.md)
- **Agent Config:** [.github/copilot-agents.yml](.github/copilot-agents.yml)
- **Validation:** `python scripts/validate-agents.py`
- **Demo Workflows:** `python scripts/demo-agent-workflows.py`

--

**Quick Start:** Open GitHub Copilot Chat → Type `@` → Select agent → Ask
question!
