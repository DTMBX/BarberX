# Deployment Map

**Document:** Domain → Hosting → Repo mapping  
**Date:** 2026-03-06  
**Status:** Current baseline  
**Scope:** All published and planned surfaces

---

## Evident Technologies LLC

| Surface | Domain | Hosting | Repo | Status |
|---------|--------|---------|------|--------|
| Marketing site | `www.evident.icu` | GitHub Pages | `DTMBX/Evident` | Active — CNAME set |
| BWC Suite frontend | `app.evident.icu` (planned) | Render or Vercel | `DTMBX/Evident` → `bwc/frontend/` | Planned |
| BWC Suite API | `api.evident.icu` (planned) | Render | `DTMBX/Evident` → `bwc/backend/` | Planned |
| Flask legacy API | Render default URL | Render (free) | `DTMBX/Evident` → `app.py` | Active |
| Ops portal | `devon-tyler.com` | GitHub Pages | `DTMBX/Founder-Hub` | Active — CNAME set |

### Evident Satellites

| Surface | Domain | Hosting | Repo | Status |
|---------|--------|---------|------|--------|
| DOJ Document Library | `dtmbx.github.io/epstein-library-evid` (planned) | GitHub Pages | `DTMBX/epstein-library-evid` | Not deployed |
| Civics Hierarchy | `dtmbx.github.io/civics-hierarchy` (planned) | GitHub Pages | `DTMBX/civics-hierarchy` | Not deployed |
| Essential Goods Ledger | `dtmbx.github.io/essential-goods-ledg` (planned) | GitHub Pages | `DTMBX/essential-goods-ledg` | Not deployed |
| Informed Consent Companion | `dtmbx.github.io/informed-consent-com` | GitHub Pages | `DTMBX/informed-consent-com` | Active |

---

## Tillerstead LLC

| Surface | Domain | Hosting | Repo | Status |
|---------|--------|---------|------|--------|
| Marketing site | `tillerstead.com` | Netlify | `DTMBX/Tillerstead` | Active — CNAME set |
| Toolkit API | Railway default URL → `api.tillerstead.com` (planned) | Railway | `DTMBX/tillerstead-toolkit` | Configured |
| Toolkit embed | `tillerstead.com/tools/` (embedded iframe) | Netlify (parent) + Railway (iframe) | Both repos | Planned |

### Tillerstead Satellites

| Surface | Domain | Hosting | Repo | Status |
|---------|--------|---------|------|--------|
| Contractor Command Center | `dtmbx.github.io/contractor-command-center` (planned) | GitHub Pages | `DTMBX/contractor-command-center` | Not deployed |
| Sweat Equity Insurance | NOT DEPLOYED | — | `DTMBX/sweat-equity-insurance` | Private demo |

---

## Personal

| Surface | Domain | Hosting | Repo | Status |
|---------|--------|---------|------|--------|
| Geneva Bible Study | `dtmbx.github.io/geneva-bible-study-t` | GitHub Pages | `DTMBX/geneva-bible-study-t` | Ready (v1.0) |

---

## Domain Reconciliation Notes

| Issue | Details | Resolution |
|-------|---------|-----------|
| Evident dual domain | CNAME says `www.evident.icu`; manifest says `evidenttechnologies.com` | Must choose primary and redirect the other |
| BWC subdomain | No subdomain configured yet for the app frontend | Add `app.evident.icu` when ready |
| Toolkit domain | Railway default URL has no custom domain | Add `api.tillerstead.com` when ready |

---

## CORS Map

| API | Allowed Origins | Must NOT Allow |
|-----|----------------|---------------|
| Evident Flask API | `evident.icu`, `app.evident.icu`, `*.onrender.com` | `tillerstead.com` |
| BWC FastAPI | `evident.icu`, `app.evident.icu` | `tillerstead.com` |
| Tillerstead Toolkit API | `tillerstead.com`, `www.tillerstead.com`, `localhost:3000` | `evident.icu`, `devon-tyler.com` |
