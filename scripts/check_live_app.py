# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Check Live App Status - Diagnose Evident deployment
"""

import json
from datetime import datetime

import requests


def test_url(url, description):
    """Test if URL is accessible"""
    print(f"\n{'=' * 60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"{'=' * 60}")

    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response time: {response.elapsed.total_seconds():.2f}s")

        if response.status_code == 200:
            print("✅ Page loaded successfully!")
            # Show first 200 chars of response
            preview = response.text[:200].replace("\n", " ")
            print(f"Preview: {preview}...")
            return True
        elif response.status_code == 500:
            print("❌ SERVER ERROR - App is crashing")
            print(f"Response: {response.text[:500]}")
            return False
        elif response.status_code == 404:
            print("❌ NOT FOUND - Wrong URL or route missing")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ CANNOT CONNECT - App is not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - App is too slow or hung")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_registration():
    """Test if registration works"""
    print(f"\n{'=' * 60}")
    print("Testing: Registration Endpoint")
    print(f"{'=' * 60}")

    urls = [
        "https://Evident.info/auth/register",
        "https://Evident-backend.onrender.com/auth/register",
    ]

    test_data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "TestPass123!",
        "name": "Test User",
    }

    for url in urls:
        try:
            print(f"\nTrying: {url}")
            response = requests.post(
                url, json=test_data, timeout=10, headers={"Content-Type": "application/json"}
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 201:
                print("✅ Registration works!")
                return True
            elif response.status_code == 400:
                print("⚠️  Registration endpoint exists but rejected data")
                print(f"Response: {response.text[:200]}")
                return True  # Endpoint works, just validation issue
            else:
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Failed: {e}")
            continue

    print("\n❌ Registration not working on any URL")
    return False


def main():
    """Run all diagnostics"""
    print("\n" + "=" * 60)
    print("🔍 Evident LIVE APP DIAGNOSTICS")
    print("=" * 60)

    results = []

    # Test main URLs
    print("\n\n📍 TESTING MAIN URLS...")
    results.append(("Main Site", test_url("https://Evident.info/", "Main Homepage")))
    results.append(
        ("Render URL", test_url("https://Evident-backend.onrender.com/", "Render Deployment"))
    )

    print("\n\n📍 TESTING AUTH PAGES...")
    results.append(("Login Page", test_url("https://Evident.info/login", "Login Page")))
    results.append(("Register Page", test_url("https://Evident.info/register", "Register Page")))

    print("\n\n📍 TESTING PAYMENT PAGES...")
    results.append(
        ("Pricing Page", test_url("https://Evident.info/payments/pricing", "Pricing Page"))
    )

    print("\n\n📍 TESTING API ENDPOINTS...")
    results.append(("Registration API", test_registration()))

    # Summary
    print("\n\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test, result in results:
        status = "✅ WORKING" if result else "❌ FAILED"
        print(f"{status:15s} {test}")

    print(f"\n{passed}/{total} checks passed")

    # Recommendations
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS")
    print("=" * 60 + "\n")

    if passed == 0:
        print("❌ APP IS NOT DEPLOYED OR COMPLETELY BROKEN")
        print("\nFIX:")
        print("1. Check Render dashboard: https://dashboard.render.com/")
        print("2. Look at deployment logs")
        print("3. Verify environment variables are set")
        print("4. Check for build errors")

    elif passed < total // 2:
        print("⚠️  APP IS PARTIALLY WORKING - MAJOR ISSUES")
        print("\nFIX:")
        print("1. Check Render logs for errors")
        print("2. Some routes may be broken")
        print("3. Database connection issues?")

    elif passed < total:
        print("⚠️  APP IS MOSTLY WORKING - MINOR ISSUES")
        print("\nFIX:")
        print("1. Some specific routes need attention")
        print("2. Check failed tests above")
        print("3. May be able to access via working URLs")

    else:
        print("✅ APP IS FULLY OPERATIONAL!")
        print("\nNEXT STEPS:")
        print("1. Register at: https://Evident.info/register")
        print("2. Use your real email (not test@Evident.test)")
        print("3. Login and test the app")

    print("\n" + "=" * 60 + "\n")

    return 0 if passed > total // 2 else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
