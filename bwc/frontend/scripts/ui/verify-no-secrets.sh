#!/usr/bin/env bash
# verify-no-secrets.sh — Scan E2E test files for obvious secrets/tokens.
# Exit 1 if found. Used in CI pre-flight.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔍 Scanning E2E files for secrets..."

PATTERNS=(
  'AKIA[0-9A-Z]{16}'           # AWS access key
  'sk-[a-zA-Z0-9]{24,}'        # OpenAI key
  'ghp_[a-zA-Z0-9]{36}'        # GitHub PAT
  'glpat-[a-zA-Z0-9\-]{20}'    # GitLab PAT
  'password\s*[:=]\s*["\x27][^"\x27]{8,}' # Hardcoded passwords
  'secret\s*[:=]\s*["\x27][^"\x27]{8,}'   # Hardcoded secrets
  'Bearer\s+[a-zA-Z0-9\-._~+/]+=*'       # Bearer tokens
)

FOUND=0

for pat in "${PATTERNS[@]}"; do
  if grep -rEn "$pat" "$PROJECT_ROOT/e2e/" 2>/dev/null; then
    echo "❌ FOUND potential secret matching: $pat"
    FOUND=1
  fi
done

# Also check fixtures for hardcoded URLs with credentials
if grep -rEn 'https?://[^@\s]+:[^@\s]+@' "$PROJECT_ROOT/e2e/" 2>/dev/null; then
  echo "❌ FOUND URL with embedded credentials"
  FOUND=1
fi

if [ "$FOUND" -eq 1 ]; then
  echo ""
  echo "❌ Secret scan FAILED. Remove hardcoded secrets from E2E files."
  exit 1
fi

echo "✅ No secrets detected in E2E files."
