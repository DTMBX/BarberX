# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident UX Integration Test
Verify all UX improvements are working correctly
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def test_imports():
    """Test that all UX modules can be imported"""
    print("🔍 Testing imports...")

    try:
        from ux_helpers import (
            format_duration,
            format_file_size,
            format_number,
            register_ux_filters,
            tier_features,
            tier_pricing,
            usage_percentage,
        )

        print("✅ ux_helpers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ux_helpers: {e}")
        return False

    try:
        from flask import Flask

        app = Flask(__name__)
        register_ux_filters(app)
        print("✅ UX filters registered successfully")
    except Exception as e:
        print(f"❌ Failed to register filters: {e}")
        return False

    return True


def test_helper_functions():
    """Test helper function outputs"""
    print("\n🧪 Testing helper functions...")

    from ux_helpers import (
        format_duration,
        format_file_size,
        format_number,
        tier_pricing,
        usage_percentage,
        usage_status,
    )

    tests = [
        (format_number(1500), "1,500", "format_number"),
        (format_file_size(1048576), "1.00 MB", "format_file_size"),
        (format_duration(90), "1m 30s", "format_duration"),
        (tier_pricing("PROFESSIONAL"), 49, "tier_pricing"),
        (usage_percentage(8, 10), 80, "usage_percentage"),
        (usage_status(8, 10), "warning", "usage_status"),
    ]

    all_passed = True
    for result, expected, test_name in tests:
        if result == expected:
            print(f"✅ {test_name}: {result}")
        else:
            print(f"❌ {test_name}: expected {expected}, got {result}")
            all_passed = False

    return all_passed


def test_tier_features():
    """Test tier feature listings"""
    print("\n📊 Testing tier features...")

    from ux_helpers import tier_features

    tiers = ["FREE", "PROFESSIONAL", "PREMIUM", "ENTERPRISE"]

    for tier in tiers:
        features = tier_features(tier)
        if len(features) > 0:
            print(f"✅ {tier}: {len(features)} features")
        else:
            print(f"❌ {tier}: No features found")
            return False

    return True


def test_component_files():
    """Test that component templates exist"""
    print("\n📁 Testing component files...")

    components = [
        "templates/components/usage-meter.html",
        "templates/components/tier-upgrade-card.html",
        "templates/components/onboarding-tour.html",
        "templates/admin/dashboard.html",
        "assets/css/accessibility.css",
    ]

    all_exist = True
    for component in components:
        if os.path.exists(component):
            print(f"✅ {component}")
        else:
            print(f"❌ {component} - NOT FOUND")
            all_exist = False

    return all_exist


def test_app_integration():
    """Test Flask app integration"""
    print("\n🌐 Testing Flask app integration...")

    try:
        from app import app

        # Check if UX helpers are registered
        if "format_number" in app.jinja_env.filters:
            print("✅ Jinja2 filters registered")
        else:
            print("⚠️  Jinja2 filters not found (may need app context)")

        # Check routes exist
        routes = [rule.rule for rule in app.url_map.iter_rules()]

        required_routes = ["/dashboard", "/admin", "/auth/login", "/auth/signup"]
        for route in required_routes:
            if route in routes:
                print(f"✅ Route {route} exists")
            else:
                print(f"❌ Route {route} missing")

        return True
    except Exception as e:
        print(f"❌ App integration error: {e}")
        return False


def test_accessibility_features():
    """Test accessibility CSS exists and has key features"""
    print("\n♿ Testing accessibility features...")

    try:
        with open("assets/css/accessibility.css") as f:
            css_content = f.read()

        required_features = [
            "focus-visible",
            "skip-link",
            "sr-only",
            "prefers-reduced-motion",
            "prefers-contrast",
            "aria-label",
        ]

        all_found = True
        for feature in required_features:
            if feature in css_content:
                print(f"✅ {feature} styles found")
            else:
                print(f"❌ {feature} styles missing")
                all_found = False

        return all_found
    except FileNotFoundError:
        print("❌ accessibility.css not found")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Evident UX Integration Test Suite")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Helper Functions", test_helper_functions),
        ("Tier Features", test_tier_features),
        ("Component Files", test_component_files),
        ("App Integration", test_app_integration),
        ("Accessibility", test_accessibility_features),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! UX improvements are ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
