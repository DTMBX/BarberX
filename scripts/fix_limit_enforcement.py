# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
CRITICAL FIX: Apply Data Limit Enforcement
Adds @check_usage_limit decorators to all upload routes in app.py
"""

import os
import re
from datetime import datetime


def backup_file(filename):
    """Create backup before modifying"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(filename, encoding="utf-8") as f:
            content = f.read()
        with open(backup_name, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created backup: {backup_name}")
        return True
    return False


def add_imports(content):
    """Add tier_gating imports if not present"""

    # Check if already imported
    if "from tier_gating import" in content:
        print("ℹ️  tier_gating already imported")
        return content

    # Find first import statement
    import_pattern = r"(from flask import .*?\n)"
    match = re.search(import_pattern, content)

    if match:
        # Add after Flask imports
        import_statement = "\n# Tier enforcement\nfrom tier_gating import require_tier, check_usage_limit, require_feature\nfrom models_auth import TierLevel\n"
        content = content.replace(match.group(1), match.group(1) + import_statement)
        print("✅ Added tier_gating imports")
    else:
        # Add at top after initial imports
        content = (
            "from tier_gating import require_tier, check_usage_limit, require_feature\nfrom models_auth import TierLevel\n\n"
            + content
        )
        print("✅ Added tier_gating imports at top")

    return content


def apply_video_upload_limits(content):
    """Apply limits to video upload routes"""

    # Find video upload routes (more flexible pattern to match routes with methods)
    patterns = [
        r"@app\.route\(['\"]([^'\"]*upload[^'\"]*video[^'\"]*)['\"].*?\)",
        r"@app\.route\(['\"]([^'\"]*video[^'\"]*upload[^'\"]*)['\"].*?\)",
        r"@app\.route\(['\"]([^'\"]*bwc[^'\"]*upload[^'\"]*)['\"].*?\)",
        r"@app\.route\(['\"]([^'\"]*\/api\/upload)['\"].*?\)",  # Generic API upload
    ]

    modified = False

    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))

        for match in reversed(matches):  # Reverse to maintain positions
            route_path = match.group(1)

            # Check if already has decorator (check 500 chars before)
            start_pos = max(0, match.start() - 500)
            check_snippet = content[start_pos : match.start()]

            if "@check_usage_limit" in check_snippet or "@require_tier" in check_snippet:
                print(f"ℹ️  {route_path} already has usage limits")
                continue

            # Add decorators before @app.route
            decorators = "@require_tier(TierLevel.STARTER)\n@check_usage_limit('bwc_videos_per_month', increment=1)\n"

            # Insert at the position of @app.route
            content = content[: match.start()] + decorators + content[match.start() :]
            print(f"✅ Applied limits to video upload: {route_path}")
            modified = True

    return content, modified


def apply_pdf_upload_limits(content):
    """Apply limits to PDF upload routes"""

    patterns = [
        r"@app\.route\(['\"]([^'\"]*upload[^'\"]*pdf[^'\"]*)['\"].*?\)",
        r"@app\.route\(['\"]([^'\"]*pdf[^'\"]*upload[^'\"]*)['\"].*?\)",
        r"@app\.route\(['\"]([^'\"]*document[^'\"]*upload[^'\"]*)['\"].*?\)",
    ]

    modified = False

    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))

        for match in reversed(matches):
            route_path = match.group(1)

            # Check if already has decorator (check 500 chars before)
            start_pos = max(0, match.start() - 500)
            check_snippet = content[start_pos : match.start()]

            if "@check_usage_limit" in check_snippet or "@require_tier" in check_snippet:
                print(f"ℹ️  {route_path} already has usage limits")
                continue

            # Add decorators
            decorators = "@require_tier(TierLevel.STARTER)\n@check_usage_limit('pdf_documents_per_month', increment=1)\n"

            # Insert at the position of @app.route
            content = content[: match.start()] + decorators + content[match.start() :]
            print(f"✅ Applied limits to PDF upload: {route_path}")
            modified = True

    return content, modified


def apply_case_create_limits(content):
    """Apply limits to case creation routes"""

    patterns = [
        r"@app\.route\(['\"]([^'\"]*case[^'\"]*create[^'\"]*)['\"].*?\)\s*\n\s*def\s+(\w+)",
        r"@app\.route\(['\"]([^'\"]*create[^'\"]*case[^'\"]*)['\"].*?\)\s*\n\s*def\s+(\w+)",
    ]

    modified = False

    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))

        for match in reversed(matches):
            route_path = match.group(1)
            func_name = match.group(2)

            start_pos = max(0, match.start() - 200)
            check_snippet = content[start_pos : match.start()]

            if "@check_usage_limit" in check_snippet:
                print(f"ℹ️  {route_path} already has usage limits")
                continue

            decorators = "@check_usage_limit('case_limit', increment=1)\n"

            route_start = content.rfind("@app.route", start_pos, match.start())
            if route_start != -1:
                content = content[:route_start] + decorators + content[route_start:]
                print(f"✅ Applied limits to case creation: {route_path} ({func_name})")
                modified = True

    return content, modified


def apply_api_limits(content):
    """Apply limits to API routes"""

    # Find routes with /api/ in the path
    pattern = r"@app\.route\(['\"]([^'\"]*\/api\/[^'\"]*)['\"].*?\)\s*\n\s*def\s+(\w+)"
    matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))

    modified = False

    for match in reversed(matches):
        route_path = match.group(1)
        func_name = match.group(2)

        # Skip if already protected
        start_pos = max(0, match.start() - 200)
        check_snippet = content[start_pos : match.start()]

        if "@require_tier" in check_snippet or "@check_usage_limit" in check_snippet:
            continue

        # Require PREMIUM tier for API access (unless it's a public endpoint)
        if any(public in route_path.lower() for public in ["health", "status", "ping"]):
            continue

        decorators = "@require_tier(TierLevel.PREMIUM)  # API access requires PREMIUM+\n"

        route_start = content.rfind("@app.route", start_pos, match.start())
        if route_start != -1:
            content = content[:route_start] + decorators + content[route_start:]
            print(f"✅ Applied API tier requirement: {route_path} ({func_name})")
            modified = True

    return content, modified


def main():
    print("=" * 80)
    print("CRITICAL FIX: APPLYING DATA LIMIT ENFORCEMENT")
    print("=" * 80)
    print()

    app_file = "app.py"

    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found!")
        print("   Run this script from the project root directory.")
        return False

    # Backup
    print("Step 1: Creating backup...")
    backup_file(app_file)
    print()

    # Read file
    print("Step 2: Reading app.py...")
    with open(app_file, encoding="utf-8") as f:
        content = f.read()
    print(f"✅ Read {len(content)} characters")
    print()

    # Add imports
    print("Step 3: Adding tier_gating imports...")
    content = add_imports(content)
    print()

    # Apply limits
    print("Step 4: Applying video upload limits...")
    content, video_modified = apply_video_upload_limits(content)
    print()

    print("Step 5: Applying PDF upload limits...")
    content, pdf_modified = apply_pdf_upload_limits(content)
    print()

    print("Step 6: Applying case creation limits...")
    content, case_modified = apply_case_create_limits(content)
    print()

    print("Step 7: Applying API access limits...")
    content, api_modified = apply_api_limits(content)
    print()

    # Write back
    if any([video_modified, pdf_modified, case_modified, api_modified]):
        print("Step 8: Writing changes to app.py...")
        with open(app_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Changes written successfully")
        print()

        print("=" * 80)
        print("✅ ENFORCEMENT APPLIED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Changes made:")
        if video_modified:
            print("  ✅ Video upload limits enforced")
        if pdf_modified:
            print("  ✅ PDF upload limits enforced")
        if case_modified:
            print("  ✅ Case creation limits enforced")
        if api_modified:
            print("  ✅ API access limits enforced")
        print()
        print("⚠️  NEXT STEPS:")
        print("  1. Review changes in app.py")
        print("  2. Test with FREE account (should hit limits)")
        print("  3. Test with PREMIUM account (should allow overage)")
        print("  4. Monitor usage in database")
        print("  5. Implement overage billing (see DATA-LIMITS-CRITICAL-ANALYSIS.md)")
        print()
        print("📋 Test command:")
        print("  python app.py")
        print("  # Try uploading files as FREE user")
        print()
    else:
        print("=" * 80)
        print("ℹ️  NO CHANGES NEEDED")
        print("=" * 80)
        print()
        print("All routes already have limit enforcement applied.")
        print("Or no upload routes were found in app.py.")
        print()
        print("To verify:")
        print("  grep -n '@check_usage_limit' app.py")
        print()

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
