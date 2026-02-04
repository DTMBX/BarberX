#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Login Diagnostic Script
Tests why admin login is failing
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def test_database_path():
    """Check database location"""
    print("\n" + "=" * 70)
    print("TEST 1: Database Path Configuration")
    print("=" * 70)

    from app import app

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "NOT SET")
    print(f"Database URI: {db_uri}")

    # Extract path from URI
    if db_uri.startswith("sqlite:///"):
        db_path = db_uri.replace("sqlite:///", "")
        print(f"Database path: {db_path}")

        if os.path.exists(db_path):
            print(f"✅ Database file exists")
            print(f"   Size: {os.path.getsize(db_path)} bytes")
        else:
            print(f"❌ Database file NOT found at: {db_path}")

            # Check common locations
            common_paths = ["instance/Evident.db", "Evident.db", "Evident_FRESH.db"]

            print("\nChecking common locations:")
            for path in common_paths:
                if os.path.exists(path):
                    print(f"  ✅ Found: {path} ({os.path.getsize(path)} bytes)")
                else:
                    print(f"  ❌ Not found: {path}")

    return db_uri


def test_admin_user():
    """Check if admin user exists in database"""
    print("\n" + "=" * 70)
    print("TEST 2: Admin User in Database")
    print("=" * 70)

    from app import app
    from models_auth import User, db

    with app.app_context():
        try:
            admin = User.query.filter_by(email="admin@Evident.info").first()

            if admin:
                print("✅ Admin user found in database")
                print(f"   Email: {admin.email}")
                print(f"   Role: {admin.role}")
                print(f"   Tier: {admin.subscription_tier}")
                print(f"   Active: {admin.is_active}")
                print(f"   Has password hash: {bool(admin.password_hash)}")
                print(f"   Password hash (first 20 chars): {admin.password_hash[:20]}...")
                return admin
            else:
                print("❌ Admin user NOT found in database")
                print("\nAll users in database:")

                all_users = User.query.all()
                if all_users:
                    for user in all_users:
                        print(f"  - {user.email} (role: {user.role})")
                else:
                    print("  (No users found)")

                return None

        except Exception as e:
            print(f"❌ Error querying database: {e}")
            return None


def test_password_verification():
    """Test password verification"""
    print("\n" + "=" * 70)
    print("TEST 3: Password Verification")
    print("=" * 70)

    password = os.environ.get("Evident_ADMIN_PASSWORD")

    if not password:
        print("❌ Evident_ADMIN_PASSWORD environment variable NOT SET")
        return False

    print(f"✅ Environment variable set: {password[:10]}...")

    from app import app
    from models_auth import User, db

    with app.app_context():
        admin = User.query.filter_by(email="admin@Evident.info").first()

        if not admin:
            print("❌ Cannot test - admin user not found")
            return False

        # Test password
        if admin.check_password(password):
            print("✅ Password verification: SUCCESS")
            print("   Password matches the hash in database")
            return True
        else:
            print("❌ Password verification: FAILED")
            print("   Password does NOT match the hash in database")
            print("\nPossible issues:")
            print("  1. Wrong password in environment variable")
            print("  2. Database has different password hash")
            print("  3. Password hash was corrupted")
            return False


def test_login_route():
    """Test if login route is accessible"""
    print("\n" + "=" * 70)
    print("TEST 4: Login Route Accessibility")
    print("=" * 70)

    from app import app

    with app.test_client() as client:
        # Test GET request
        response = client.get("/auth/login")
        print(f"GET /auth/login: Status {response.status_code}")

        if response.status_code == 200:
            print("✅ Login page accessible")
        elif response.status_code == 404:
            print("❌ Login route NOT FOUND (404)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")

        # Test POST request
        print("\nTesting POST login...")
        password = os.environ.get("Evident_ADMIN_PASSWORD", "test")

        response = client.post(
            "/auth/login",
            data={"email": "admin@Evident.info", "password": password},
            follow_redirects=False,
        )

        print(f"POST /auth/login: Status {response.status_code}")

        if response.status_code == 302:
            print(f"✅ Redirect (login processed)")
            print(f"   Location: {response.location}")
        elif response.status_code == 200:
            print("⚠️  No redirect (check if login failed)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")

        return response.status_code


def main():
    """Run all diagnostic tests"""
    print("\n" + "=" * 70)
    print("LOGIN DIAGNOSTIC - Finding Why Admin Login Fails")
    print("=" * 70)

    results = {}

    # Test 1: Database Path
    try:
        db_uri = test_database_path()
        results["database_path"] = "PASS" if "sqlite" in db_uri else "FAIL"
    except Exception as e:
        print(f"❌ Database path test failed: {e}")
        results["database_path"] = "ERROR"

    # Test 2: Admin User
    try:
        admin = test_admin_user()
        results["admin_user"] = "PASS" if admin else "FAIL"
    except Exception as e:
        print(f"❌ Admin user test failed: {e}")
        results["admin_user"] = "ERROR"

    # Test 3: Password Verification
    try:
        password_ok = test_password_verification()
        results["password"] = "PASS" if password_ok else "FAIL"
    except Exception as e:
        print(f"❌ Password test failed: {e}")
        results["password"] = "ERROR"

    # Test 4: Login Route
    try:
        status = test_login_route()
        results["login_route"] = "PASS" if status in [200, 302] else "FAIL"
    except Exception as e:
        print(f"❌ Login route test failed: {e}")
        results["login_route"] = "ERROR"

    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    for test_name, result in results.items():
        status_symbol = "✅" if result == "PASS" else ("❌" if result == "FAIL" else "⚠️")
        print(f"{status_symbol} {test_name:20} {result}")

    print("=" * 70)

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    if results.get("database_path") == "FAIL":
        print("❌ FIX DATABASE:")
        print("   Database not found at expected location")
        print("   Run: Copy-Item scripts\\instance\\Evident.db instance\\Evident.db -Force")

    if results.get("admin_user") == "FAIL":
        print("❌ FIX ADMIN USER:")
        print("   Admin user not in database")
        print("   Run: python scripts/create_admin.py")

    if results.get("password") == "FAIL":
        print("❌ FIX PASSWORD:")
        print("   Password doesn't match database hash")
        print("   Option 1: Set correct password in environment:")
        print("     $env:Evident_ADMIN_PASSWORD = 'pQWN6CUNH04Gx6Ud73dfybu6jiV_DM4s'")
        print("   Option 2: Recreate admin account:")
        print("     python scripts/create_admin.py")

    if results.get("login_route") == "FAIL":
        print("❌ FIX LOGIN ROUTE:")
        print("   Login route not accessible")
        print("   Check if auth_bp is registered in app.py")

    if all(r == "PASS" for r in results.values()):
        print("✅ ALL TESTS PASSED!")
        print("\nLogin should be working. If still failing:")
        print("  1. Check browser console for errors (F12)")
        print("  2. Clear browser cookies/cache")
        print("  3. Try incognito mode")
        print("  4. Check Flask app logs")

    print("\n")

    # Return exit code
    return 0 if all(r == "PASS" for r in results.values()) else 1


if __name__ == "__main__":
    exit(main())


