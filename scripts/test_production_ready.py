# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Production Readiness Test - Verify all systems operational
Run this to confirm Evident.info is ready for court document processing
"""

import os
import sqlite3
import sys
from pathlib import Path

import requests


def test_flask_app():
    """Test if Flask app is running"""
    print("🧪 Testing Flask app...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("   ✅ Flask app is running")
            return True
        else:
            print(f"   ❌ Flask app returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Flask app is NOT running")
        print("   ℹ️  Start it with: python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_database():
    """Test database exists and has required tables"""
    print("\n🧪 Testing database...")
    db_path = Path("./instance/Evident_auth.db")

    if not db_path.exists():
        print("   ❌ Database file not found")
        print("   ℹ️  Run: python init_database.py")
        return False

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    required_tables = {"users", "analyses", "pdf_uploads", "audit_logs", "api_keys"}

    missing = required_tables - tables
    if missing:
        print(f"   ❌ Missing tables: {missing}")
        print("   ℹ️  Run: python init_database.py")
        conn.close()
        return False

    # Check for admin user
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    admin_count = cursor.fetchone()[0]

    if admin_count == 0:
        print("   ❌ No admin user found")
        print("   ℹ️  Run: python create_admin.py")
        conn.close()
        return False

    print(f"   ✅ Database has {len(tables)} tables")
    print("   ✅ Admin user exists")

    conn.close()
    return True


def test_directories():
    """Test required directories exist"""
    print("\n🧪 Testing directories...")

    required_dirs = [
        "./uploads/pdfs",
        "./uploads/bwc_videos",
        "./bwc_analysis",
        "./logs",
        "./instance",
    ]

    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ⚠️  {dir_path} (will be created)")
            path.mkdir(parents=True, exist_ok=True)
            all_exist = False

    return all_exist


def test_netlify_forms():
    """Test Netlify forms are properly configured"""
    print("\n🧪 Testing Netlify forms...")

    forms_to_check = [
        ("_includes/connect.html", "early-access"),
        ("_includes/components/newsletter-signup.html", "newsletter-signup"),
        ("templates/company/contact.html", "contact-form"),
        ("_includes/components/forms/connect.html", "early-access-secondary"),
        ("docs/_includes/connect.html", "docs-early-access"),
    ]

    all_configured = True
    for file_path, form_name in forms_to_check:
        path = Path(file_path)
        if not path.exists():
            print(f"   ❌ {file_path} not found")
            all_configured = False
            continue

        content = path.read_text(encoding="utf-8")

        checks = [
            'data-netlify="true"' in content,
            f'name="{form_name}"' in content,
            "netlify-honeypot" in content,
        ]

        if all(checks):
            print(f"   ✅ {form_name}")
        else:
            print(f"   ❌ {form_name} - missing Netlify attributes")
            all_configured = False

    return all_configured


def test_api_endpoints():
    """Test critical API endpoints"""
    print("\n🧪 Testing API endpoints...")

    endpoints_to_test = [
        ("/", "GET", "Homepage"),
        ("/batch-pdf-upload.html", "GET", "PDF Upload Interface"),
        ("/bwc-analyzer.html", "GET", "BWC Analysis Interface"),
    ]

    all_working = True
    for endpoint, method, name in endpoints_to_test:
        try:
            response = requests.request(method, f"http://localhost:5000{endpoint}", timeout=5)
            if response.status_code in [200, 302]:
                print(f"   ✅ {name}")
            else:
                print(f"   ⚠️  {name} - Status {response.status_code}")
                all_working = False
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {name} - Flask app not running")
            all_working = False
            break
        except Exception as e:
            print(f"   ❌ {name} - {e}")
            all_working = False

    return all_working


def main():
    print("=" * 70)
    print("  Evident.info Production Readiness Test")
    print("  Testing all systems for court document processing")
    print("=" * 70)

    tests = [
        ("Database", test_database),
        ("Directories", test_directories),
        ("Flask App", test_flask_app),
        ("API Endpoints", test_api_endpoints),
        ("Netlify Forms", test_netlify_forms),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test failed with error: {e}")
            results[test_name] = False

    print("\n" + "=" * 70)
    print("  Test Summary")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status:15} {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 70)
    if all_passed:
        print("  🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
        print("=" * 70)
        print("\n  📋 Next Steps:")
        print("     1. Flask app is running on http://localhost:5000")
        print("     2. Upload PDFs via http://localhost:5000/batch-pdf-upload.html")
        print("     3. Login as admin: admin@Evident.info")
        print("     4. Check logs: ./logs/Evident.log")
        print("\n  📄 See TONIGHT-QUICK-START.md for detailed instructions")
        return 0
    else:
        print("  ⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE PRODUCTION")
        print("=" * 70)
        print("\n  🔧 Fix Issues:")
        if not results.get("Database"):
            print("     - Run: python init_database.py")
            print("     - Run: python create_admin.py")
        if not results.get("Flask App"):
            print("     - Run: python app.py")
        print("\n  📄 See PRODUCTION-READY-REPORT.md for troubleshooting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
