#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# Evident Discovery Suite — Smoke Test (Bash)
#
# Prerequisites: curl, jq, sha256sum (or shasum), a running BWC stack.
# Usage:   bash bwc/scripts/smoke.sh
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

API="${BWC_API_BASE:-http://localhost:8000}"
PASS=true

log()  { printf "\033[1;34m▸ %s\033[0m\n" "$*"; }
ok()   { printf "\033[1;32m  ✓ %s\033[0m\n" "$*"; }
fail() { printf "\033[1;31m  ✗ %s\033[0m\n" "$*"; PASS=false; }

# ── Helper: SHA-256 (cross-platform) ────────────────────────────────
sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | awk '{print $1}'
  else
    shasum -a 256 | awk '{print $1}'
  fi
}

# ── 1) Health check ─────────────────────────────────────────────────
log "Health check"
HEALTH=$(curl -sf "${API}/health")
echo "$HEALTH" | jq -e '.status == "healthy"' >/dev/null && ok "GET /health" || fail "GET /health"

# ── 2) Create case ──────────────────────────────────────────────────
log "Create case"
CASE=$(curl -sf -X POST "${API}/cases" \
  -H "Content-Type: application/json" \
  -d '{"title":"Smoke Test Case","created_by":"smoke.sh"}')
CASE_ID=$(echo "$CASE" | jq -r '.id')
[ -n "$CASE_ID" ] && [ "$CASE_ID" != "null" ] && ok "POST /cases → $CASE_ID" || fail "POST /cases"

# ── 3) Init evidence upload ─────────────────────────────────────────
log "Init evidence upload"
TESTFILE_CONTENT="Hello from Evident smoke test $(date -u +%Y%m%d%H%M%S)"
TESTFILE_SIZE=${#TESTFILE_CONTENT}

INIT=$(curl -sf -X POST "${API}/evidence/init" \
  -H "Content-Type: application/json" \
  -d "{\"case_id\":\"${CASE_ID}\",\"filename\":\"smoke-test.txt\",\"content_type\":\"text/plain\",\"size_bytes\":${TESTFILE_SIZE}}")
EVIDENCE_ID=$(echo "$INIT" | jq -r '.evidence_id')
UPLOAD_URL=$(echo "$INIT" | jq -r '.upload_url')
[ -n "$EVIDENCE_ID" ] && [ "$EVIDENCE_ID" != "null" ] && ok "POST /evidence/init → $EVIDENCE_ID" || fail "POST /evidence/init"

# ── 4) Upload file to MinIO via presigned URL ───────────────────────
log "Upload file to MinIO"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
  -H "Content-Type: text/plain" \
  --data-binary "$TESTFILE_CONTENT" \
  "$UPLOAD_URL")
[ "$HTTP_CODE" = "200" ] && ok "PUT presigned URL (HTTP $HTTP_CODE)" || fail "PUT presigned URL (HTTP $HTTP_CODE)"

# ── 5) Complete evidence (triggers SHA-256 + audit) ──────────────────
log "Complete evidence"
COMPLETE=$(curl -sf -X POST "${API}/evidence/complete" \
  -H "Content-Type: application/json" \
  -d "{\"evidence_id\":\"${EVIDENCE_ID}\"}")
SERVER_SHA=$(echo "$COMPLETE" | jq -r '.sha256')
LOCAL_SHA=$(printf '%s' "$TESTFILE_CONTENT" | sha256)
if [ "$SERVER_SHA" = "$LOCAL_SHA" ]; then
  ok "SHA-256 match: $SERVER_SHA"
else
  fail "SHA-256 mismatch: server=$SERVER_SHA local=$LOCAL_SHA"
fi

# ── 6) Export manifest ──────────────────────────────────────────────
log "Export manifest"
MANIFEST=$(curl -sf "${API}/cases/${CASE_ID}/export/manifest")
MANIFEST_SHA=$(echo "$MANIFEST" | jq -r '.manifest_sha256')
MANIFEST_HMAC=$(echo "$MANIFEST" | jq -r '.manifest_hmac')

# Recompute locally: hash the canonical JSON of {case, evidence, audit}
CANONICAL=$(echo "$MANIFEST" | jq -cS '{case: .case, evidence: .evidence, audit: .audit}')
LOCAL_MANIFEST_SHA=$(printf '%s' "$CANONICAL" | sha256)

if [ "$MANIFEST_SHA" = "$LOCAL_MANIFEST_SHA" ]; then
  ok "Manifest SHA-256 match: $MANIFEST_SHA"
else
  fail "Manifest SHA-256 mismatch: server=$MANIFEST_SHA local=$LOCAL_MANIFEST_SHA"
fi

[ -n "$MANIFEST_HMAC" ] && [ "$MANIFEST_HMAC" != "null" ] && ok "Manifest HMAC present: ${MANIFEST_HMAC:0:16}…" || fail "Manifest HMAC missing"

# ── 7) Verify manifest endpoint ─────────────────────────────────────
log "Verify manifest (POST /verify/manifest)"
VERIFY_BODY=$(echo "$MANIFEST" | jq -c '{manifest_sha256: .manifest_sha256, manifest_hmac: .manifest_hmac, case: .case, evidence: .evidence, audit: .audit}')
VERIFY=$(curl -sf -X POST "${API}/verify/manifest" \
  -H "Content-Type: application/json" \
  -d "$VERIFY_BODY")
SHA_VALID=$(echo "$VERIFY" | jq -r '.sha256_valid')
HMAC_VALID=$(echo "$VERIFY" | jq -r '.hmac_valid')
[ "$SHA_VALID" = "true" ] && ok "Manifest SHA-256 verified by server" || fail "Manifest SHA-256 rejected by server"
[ "$HMAC_VALID" = "true" ] && ok "Manifest HMAC verified by server" || fail "Manifest HMAC rejected by server"

# ── 8) Audit replay ─────────────────────────────────────────────────
log "Audit replay (GET /verify/cases/${CASE_ID}/audit-replay)"
REPLAY=$(curl -sf "${API}/verify/cases/${CASE_ID}/audit-replay")
REPLAY_OK=$(echo "$REPLAY" | jq -r '.ok')
REPLAY_EVIDENCE=$(echo "$REPLAY" | jq -r '.evidence_checked')
REPLAY_EVENTS=$(echo "$REPLAY" | jq -r '.events_checked')
if [ "$REPLAY_OK" = "true" ]; then
  ok "Audit replay PASSED ($REPLAY_EVIDENCE evidence, $REPLAY_EVENTS events)"
else
  fail "Audit replay FAILED: $(echo "$REPLAY" | jq -r '.detail')"
fi

# ── Result ──────────────────────────────────────────────────────────
echo ""
if [ "$PASS" = true ]; then
  printf "\033[1;32m══════ PASS ══════\033[0m\n"
  exit 0
else
  printf "\033[1;31m══════ FAIL ══════\033[0m\n"
  exit 1
fi
