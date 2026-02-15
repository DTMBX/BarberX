#!/usr/bin/env bash
# scripts/verify.sh — Cross-platform site verification for Evident Technologies
# Usage: bash scripts/verify.sh
# Exit codes: 0 = pass, 1 = fail
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

FAIL=0

step() { echo -e "\n--- $1 ---"; }
pass() { echo -e "${GREEN}PASS${NC}: $1"; }
fail() { echo -e "${RED}FAIL${NC}: $1"; FAIL=1; }

# 1. Check Node.js
step "Node.js version"
if command -v node &>/dev/null; then
  NODE_VER=$(node -v)
  pass "Node $NODE_VER"
else
  fail "Node.js not found"
fi

# 2. Install dependencies
step "npm install"
if npm ci --no-audit --no-fund 2>&1; then
  pass "Dependencies installed"
else
  fail "npm ci failed"
fi

# 3. Lint
step "Lint check"
if npm run lint 2>&1; then
  pass "Lint passed"
else
  fail "Lint failed"
fi

# 4. Build site
step "Eleventy build"
if npm run build 2>&1; then
  pass "Site built"
else
  fail "Build failed"
fi

# 5. Verify output
step "Build output verification"
if [ -f "_site/index.html" ]; then
  PAGE_COUNT=$(find _site -name '*.html' | wc -l)
  pass "_site/index.html present ($PAGE_COUNT pages)"
else
  fail "_site/index.html not found"
fi

# 6. Python tests (optional, skip if no venv)
step "Python tests"
if command -v python3 &>/dev/null || command -v python &>/dev/null; then
  PY=$(command -v python3 || command -v python)
  if $PY -m pytest --version &>/dev/null; then
    if $PY -m pytest tests/ -q --tb=short 2>&1; then
      pass "Python tests passed"
    else
      fail "Python tests failed"
    fi
  else
    echo "SKIP: pytest not installed"
  fi
else
  echo "SKIP: Python not available"
fi

# Summary
step "Summary"
if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}All checks passed.${NC}"
  exit 0
else
  echo -e "${RED}One or more checks failed.${NC}"
  exit 1
fi
