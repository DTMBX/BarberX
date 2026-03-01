#!/usr/bin/env bash
# verify-artifacts-safe.sh — Ensure SAFE_MODE compliance.
# Checks that no trace/video/screenshot artifacts exist when SAFE_MODE=1.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/test-results"

echo "🔍 Checking SAFE_MODE artifact compliance..."

if [ "${SAFE_MODE:-0}" != "1" ]; then
  echo "ℹ️  SAFE_MODE is not set to 1. Skipping artifact check."
  echo "   (Set SAFE_MODE=1 to enforce zero-artifact policy)"
  exit 0
fi

FOUND=0

# Check for trace files
if find "$RESULTS_DIR" -name "*.zip" -o -name "trace.zip" 2>/dev/null | head -1 | grep -q .; then
  echo "❌ Found trace archive files in test-results/"
  FOUND=1
fi

# Check for video files
if find "$RESULTS_DIR" -name "*.webm" -o -name "*.mp4" 2>/dev/null | head -1 | grep -q .; then
  echo "❌ Found video files in test-results/"
  FOUND=1
fi

# Check for screenshot files
if find "$RESULTS_DIR" -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" 2>/dev/null | head -1 | grep -q .; then
  echo "❌ Found screenshot files in test-results/"
  FOUND=1
fi

if [ "$FOUND" -eq 1 ]; then
  echo ""
  echo "❌ SAFE_MODE violation: artifacts found in test-results/"
  echo "   Ensure playwright.config.ts respects SAFE_MODE=1"
  exit 1
fi

echo "✅ SAFE_MODE compliant — no artifacts found."
