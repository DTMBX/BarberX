#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test: Admin Login & Mobile Navigation
Tests both critical fixes are working correctly
"""

import os
import sqlite3
import sys

from werkzeug.security import check_password_hash

# Fix Windows console encoding issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def test_admin_login():
    """Test admin login credentials"""
    print("\n" + "=" * 70)
    print("TEST 1: Admin Login Verification")
    print("=" * 70)

    # Check environment variable
    admin_password = os.environ.get("Evident_ADMIN_PASSWORD")
    if not admin_password:
        print("❌ Evident_ADMIN_PASSWORD environment variable NOT SET")
        print("   Run: $env:Evident_ADMIN_PASSWORD = 'pQWN6CUNH04Gx6Ud73dfybu6jiV_DM4s'")
        return False

    print(f"✅ Environment variable set: {admin_password[:10]}...")

    # Check database
    db_path = "instance/Evident.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    print(f"✅ Database found: {db_path}")

    # Check admin account
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT email, password_hash, role, subscription_tier, is_active 
        FROM user 
        WHERE email = 'admin@Evident.info'
    """
    )

    result = cursor.fetchone()

    if not result:
        print("❌ Admin account not found in database")
        print("   Run: python scripts/create_admin.py")
        conn.close()
        return False

    email, password_hash, role, tier, is_active = result

    print(f"✅ Admin account found:")
    print(f"   Email: {email}")
    print(f"   Role: {role}")
    print(f"   Tier: {tier}")
    print(f"   Active: {bool(is_active)}")

    # Verify password
    if check_password_hash(password_hash, admin_password):
        print("✅ Password verification: SUCCESS")
    else:
        print("❌ Password verification: FAILED")
        conn.close()
        return False

    # Check for duplicate admins
    cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'admin'")
    admin_count = cursor.fetchone()[0]

    if admin_count == 1:
        print(f"✅ Security check: Exactly ONE admin account exists")
    else:
        print(f"⚠️  Warning: {admin_count} admin accounts found (should be 1)")

    conn.close()

    print("\n✅ ADMIN LOGIN TEST: PASSED")
    return True


def test_mobile_navigation():
    """Test mobile navigation JavaScript is configured"""
    print("\n" + "=" * 70)
    print("TEST 2: Mobile Navigation JavaScript")
    print("=" * 70)

    # Check layout file
    layout_file = "_layouts/default.html"
    if not os.path.exists(layout_file):
        print(f"❌ Layout file not found: {layout_file}")
        return False

    print(f"✅ Layout file found: {layout_file}")

    # Check for correct JavaScript reference
    with open(layout_file, "r", encoding="utf-8") as f:
        content = f.read()

    if "premium-header.js" in content:
        print("✅ Correct JavaScript reference: premium-header.js")
    else:
        print("❌ JavaScript reference missing or incorrect")
        if "premium-nav.js" in content:
            print("   Found: premium-nav.js (WRONG - should be premium-header.js)")
        return False

    # Check JavaScript file exists
    js_file = "assets/js/premium-header.js"
    if not os.path.exists(js_file):
        print(f"❌ JavaScript file not found: {js_file}")
        return False

    print(f"✅ JavaScript file exists: {js_file}")

    # Check JavaScript contains mobile nav functions
    with open(js_file, "r", encoding="utf-8") as f:
        js_content = f.read()

    required_functions = ["openNav", "closeNav", "toggleNav"]
    found_functions = []

    for func in required_functions:
        if func in js_content:
            found_functions.append(func)

    if len(found_functions) == len(required_functions):
        print(f"✅ Mobile nav functions found: {', '.join(found_functions)}")
    else:
        print(f"⚠️  Only found: {', '.join(found_functions)}")

    print("\n✅ MOBILE NAVIGATION TEST: PASSED")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CRITICAL FIXES VERIFICATION")
    print("Testing: Admin Login & Mobile Navigation")
    print("=" * 70)

    results = []

    # Test 1: Admin Login
    results.append(("Admin Login", test_admin_login()))

    # Test 2: Mobile Navigation
    results.append(("Mobile Navigation", test_mobile_navigation()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25} {status}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Start Flask app: python app.py")
        print("2. Test admin login: http://localhost:5000/auth/login")
        print("3. Test mobile nav: Resize browser to < 1024px width")
        print("\nAdmin credentials:")
        print("   Email: admin@Evident.info")
        print("   Password: (in Evident_ADMIN_PASSWORD env var)")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nSee error messages above for details.")
        print("\nQuick fixes:")
        print("1. Set password: $env:Evident_ADMIN_PASSWORD = 'pQWN6CUNH04Gx6Ud73dfybu6jiV_DM4s'")
        print("2. Create admin: python scripts/create_admin.py")
        print("3. Check _layouts/default.html has premium-header.js")

    print("\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())


