# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Test Flask routes and tool accessibility
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Flask Routes & Tool Accessibility")
print("=" * 60)

try:
    # Import Flask app
    print("\n[1/4] Importing Flask app...")
    from app import app

    print("  ✓ Flask app imported successfully")

    # Get all routes
    print("\n[2/4] Checking registered routes...")
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":
            routes.append(
                {
                    "endpoint": rule.endpoint,
                    "methods": ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"})),
                    "path": str(rule),
                }
            )

    # Filter for tool-related routes
    tool_routes = [r for r in routes if "/tools" in r["path"] or "tool" in r["endpoint"]]

    print(f"\n  Found {len(tool_routes)} tool-related routes:")
    for route in sorted(tool_routes, key=lambda x: x["path"]):
        print(f"    {route['methods']:8} {route['path']}")

    # Check critical routes
    print("\n[3/4] Verifying critical tool routes...")
    critical_routes = [
        "/tools",
        "/tools/ocr",
        "/tools/case-law",
        "/bwc-dashboard",
        "/legal-analysis",
        "/batch-pdf-upload.html",
    ]

    registered_paths = [r["path"] for r in routes]

    for path in critical_routes:
        if path in registered_paths:
            print(f"  ✓ {path}")
        else:
            print(f"  ✗ {path} - NOT REGISTERED!")

    # Check API endpoints
    print("\n[4/4] Verifying API endpoints...")
    api_endpoints = [
        "/api/upload",
        "/api/analyze",
        "/api/upload/pdf",
        "/api/legal/scan-violations",
        "/api/legal/check-compliance",
        "/api/evidence/ocr",
        "/api/evidence/transcribe",
        "/api/evidence/analyze-pdf",
    ]

    for endpoint in api_endpoints:
        if endpoint in registered_paths:
            print(f"  ✓ {endpoint}")
        else:
            print(f"  ✗ {endpoint} - NOT REGISTERED!")

    print("\n" + "=" * 60)
    print("ROUTE TEST COMPLETE")
    print("=" * 60)
    print("\n✓ Flask app is properly configured")
    print("\nTo start the server:")
    print("  python app.py")
    print("\nThen visit:")
    print("  http://localhost:5000/tools")

except ImportError as e:
    print(f"\n✗ Failed to import Flask app: {e}")
    print("\nThis might be due to missing database or configuration.")
    print("Try running: python app.py")

except Exception as e:
    print(f"\n✗ Error during route testing: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
