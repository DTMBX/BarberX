# Evident BWC — UX System Map

> Canonical reference for frontend architecture, personas, workflows, and
> failure modes. All contributors must follow this document when building or
> modifying UI.

---

## 1. Core User Personas

| Persona             | Goals                                                                        | Key Needs                                                                        |
| ------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Attorney**        | Build case, verify evidence chain, export manifests for court                | Verified evidence, HMAC-signed exports, citation-backed chat, audit replay proof |
| **Paralegal**       | Upload evidence, tag issues, run OCR/transcription pipeline, prepare filings | Batch upload, artifact browsing, issue tracking, export tools                    |
| **Pro Se Litigant** | Self-represent, understand evidence, research applicable law                 | Simple upload flow, plain-language chat, CourtListener search, guided export     |
| **Investigator**    | Analyze body-cam footage, timeline, cross-reference evidence                 | Timeline view, evidence detail, artifact comparison, search/filter               |
| **Admin**           | System configuration, user management, health monitoring                     | Settings page, diagnostics, safe mode controls, storage status                   |

---

## 2. Primary Workflows

### 2.1 Evidence Management Flow

```
Create Case → Upload Evidence → Server-Side SHA-256 Verification
→ Run Pipeline (OCR/Transcription) → Browse Artifacts
→ Track Issues/Violations → Export Manifest (HMAC-signed)
→ Verify Manifest → Audit Replay
```

**Upload detail:**

1. User selects files (drag-drop or file picker)
2. Client computes SHA-256 (WebCrypto, non-blocking)
3. `POST /evidence/init` → presigned URL
4. `PUT` to MinIO via presigned URL
5. `POST /evidence/complete` → server downloads from MinIO, computes SHA-256,
   stores hash
6. If 409 duplicate → show link to existing evidence, non-fatal
7. Background job queued for OCR/transcription

### 2.2 Chat + Legal Research Flow

```
Select Mode: "Evidence QA" | "Legal Research"
├─ Evidence QA: Select case context → ask question → citations from evidence/artifacts
└─ Legal Research: Search CourtListener → browse results → "Use in Chat" → grounded Q&A
```

**Citation rules:**

- Every citation badge must link to a real source: evidence artifact,
  CourtListener opinion, or user-provided resource
- Never claim statutory authority without a verified source
- CourtListener results are case law only; statutes must come from user-uploaded
  sources

### 2.3 Export + Verification Flow

```
Export Manifest (JSON with SHA-256 hashes + HMAC signature)
→ Verify Manifest (recompute SHA-256, validate HMAC)
→ Audit Replay (re-download every file from MinIO, recompute hashes, verify ordering)
```

---

## 3. Failure Modes + UI Handling

| Failure                      | Detection                                         | UI Response                                                                          |
| ---------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Network down**             | Fetch rejects                                     | Toast (error) + inline retry button; React Query retries 1×                          |
| **Backend 500**              | `ApiError.status >= 500`                          | Toast: "Server error — try again"; no data loss                                      |
| **Upload fails mid-stream**  | PUT to presigned URL fails                        | Per-file "Retry" button; file stays in upload queue                                  |
| **SHA-256 mismatch**         | Backend returns hash ≠ client hash after complete | Toast (warning): "Hash mismatch — file may be corrupted"; evidence marked unverified |
| **HMAC invalid**             | Manifest verify returns `hmac_valid: false`       | Red banner: "Manifest tampered — do not rely on this export"                         |
| **409 Duplicate**            | `POST /evidence/complete` returns 409             | Toast (info): "Duplicate file in case"; link to existing evidence row                |
| **Audit replay fail**        | Replay endpoint returns `ok: false`               | Red verification card with `detail` message; never auto-dismiss                      |
| **CourtListener rate limit** | 429 or timeout                                    | Toast (warning): "Legal search temporarily unavailable"; disable search for 30s      |
| **LLM disabled**             | Chat returns error or `LLM_PROVIDER=disabled`     | Chat shows: "AI assistant is not configured. Contact admin."                         |
| **File too large**           | Client checks `MAX_UPLOAD_BYTES` before init      | Form validation: "File exceeds 10 GB limit" before upload starts                     |
| **Invalid MIME type**        | Backend returns 422                               | Toast: "File type not allowed"; list accepted types                                  |

---

## 4. Dependencies + Justification

| Package                                   | Version      | Why                                                               |
| ----------------------------------------- | ------------ | ----------------------------------------------------------------- |
| `next`                                    | 14.2.x       | App framework — app router, server components, image optimization |
| `react` / `react-dom`                     | 18.3.x       | UI library                                                        |
| `@tanstack/react-query`                   | ^5.28        | Server state management — caching, retries, cancellation          |
| `tailwindcss`                             | 3.4.x        | Utility CSS — consistent spacing, colors, responsive              |
| `clsx` + `tailwind-merge`                 | ^2.x         | Class merging without conflicts                                   |
| `lucide-react`                            | ^0.359       | Icon library — consistent, tree-shakeable, MIT licensed           |
| `react-hook-form` + `@hookform/resolvers` | ^7.51 / ^3.3 | Form state — validation, error handling, minimal re-renders       |
| `zod`                                     | ^3.22        | Schema validation — shared with form resolvers                    |

**Not included (and why):**

- No headless UI library — we use custom components with Tailwind for full
  control
- No CSS-in-JS — Tailwind utilities are sufficient and tree-shake better
- No state management library (Redux/Zustand) — React Query + local state covers
  all data flows

---

## 5. Architecture Decisions

### Client Fetch + React Query (not server actions)

All data fetching uses `lib/api.ts` → React Query hooks in `lib/hooks/`.
Reasons:

1. Evidence upload requires client-side presigned URL flow
2. Chat is inherently interactive/streaming
3. We need caching, retry, cancellation, and optimistic updates
4. The backend is a separate service (not co-located)

### Dark Mode Only

The app uses a dark-on-slate palette consistently. Reasons:

1. Attorneys reviewing body-cam footage often work in low-light
2. Simpler to maintain one theme well than two themes poorly
3. Dark backgrounds reduce eye strain for long review sessions

### Forensic Integrity Preservation

The frontend MUST:

- Never modify evidence bytes (upload files as-is via presigned URL)
- Never trust client-side hash alone (server recomputes)
- Show clear visual distinction: Verified (green) / Pending (yellow) / Tampered
  (red)
- Never auto-dismiss forensic warnings (HMAC invalid, replay failed)
