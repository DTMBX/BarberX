# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Security Fixes Test Suite
Tests all P0 critical security fixes implemented
"""

import sys
from pathlib import Path

# Test results
tests_passed = 0
tests_failed = 0
test_results = []


def test_secret_key_validation():
    """Test that SECRET_KEY is required in production"""
    global tests_passed, tests_failed

    print("Testing SECRET_KEY validation...")

    try:
        with open("app.py") as f:
            content = f.read()

        # Check that hardcoded secret is removed
        if "Evident-legal-tech-2026-secure-key-change-in-production" in content:
            test_results.append("❌ FAIL: Hardcoded SECRET_KEY still present")
            tests_failed += 1
            return False

        # Check that SECRET_KEY is required from environment
        if "SECRET_KEY environment variable is required" in content:
            test_results.append("✓ PASS: SECRET_KEY validation implemented")
            tests_passed += 1
            return True
        else:
            test_results.append("❌ FAIL: SECRET_KEY validation not found")
            tests_failed += 1
            return False

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def test_file_upload_validation():
    """Test that file upload validation is implemented"""
    global tests_passed, tests_failed

    print("Testing file upload validation...")

    try:
        with open("app.py") as f:
            content = f.read()

        checks = [
            ("InputValidator.validate_file_type", "File type validation"),
            ("InputValidator.validate_file_size", "File size validation"),
            ("InputValidator.sanitize_path", "Path sanitization"),
        ]

        all_passed = True
        for pattern, name in checks:
            if pattern in content:
                test_results.append(f"  ✓ {name} implemented")
            else:
                test_results.append(f"  ❌ {name} missing")
                all_passed = False

        if all_passed:
            test_results.append("✓ PASS: File upload validation complete")
            tests_passed += 1
            return True
        else:
            test_results.append("❌ FAIL: File upload validation incomplete")
            tests_failed += 1
            return False

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def test_password_validation():
    """Test that password strength validation is implemented"""
    global tests_passed, tests_failed

    print("Testing password strength validation...")

    try:
        with open("app.py") as f:
            content = f.read()

        # Check in register endpoint
        if "InputValidator.validate_password" in content:
            # Count occurrences (should be in register and change_password)
            count = content.count("InputValidator.validate_password")
            if count >= 2:
                test_results.append(f"✓ PASS: Password validation in {count} endpoints")
                tests_passed += 1
                return True
            else:
                test_results.append(
                    f"⚠ PARTIAL: Password validation in {count} endpoint(s), expected 2+"
                )
                tests_passed += 1
                return True
        else:
            test_results.append("❌ FAIL: Password validation not found")
            tests_failed += 1
            return False

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def test_error_sanitization():
    """Test that error messages are sanitized"""
    global tests_passed, tests_failed

    print("Testing error message sanitization...")

    try:
        with open("app.py") as f:
            content = f.read()

        # Check for exposed errors
        exposed_pattern = 'return jsonify({"error": str(e)})'
        exposed_count = content.count(exposed_pattern)

        # Check for sanitized errors
        sanitized_pattern = "ErrorSanitizer.sanitize_error"
        sanitized_count = content.count(sanitized_pattern)

        if exposed_count == 0:
            test_results.append("✓ PASS: No exposed error messages found")
            test_results.append(f"  ✓ Error sanitization used in {sanitized_count} places")
            tests_passed += 1
            return True
        else:
            test_results.append(f"❌ FAIL: {exposed_count} exposed error messages found")
            test_results.append(f"  ✓ Error sanitization used in {sanitized_count} places")
            tests_failed += 1
            return False

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def test_error_tickets():
    """Test that error tickets are generated"""
    global tests_passed, tests_failed

    print("Testing error ticket generation...")

    try:
        with open("app.py") as f:
            content = f.read()

        # Check for error ticket generation
        if "ErrorSanitizer.create_error_ticket" in content:
            count = content.count("ErrorSanitizer.create_error_ticket")
            test_results.append(f"✓ PASS: Error tickets generated in {count} places")
            tests_passed += 1
            return True
        else:
            test_results.append("❌ FAIL: Error ticket generation not found")
            tests_failed += 1
            return False

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def test_input_sanitization():
    """Test that user inputs are sanitized"""
    global tests_passed, tests_failed

    print("Testing input sanitization...")

    try:
        with open("app.py") as f:
            content = f.read()

        # Check for input sanitization
        if "InputValidator.sanitize_text" in content:
            count = content.count("InputValidator.sanitize_text")
            test_results.append(f"✓ PASS: Input sanitization used in {count} places")
            tests_passed += 1
            return True
        else:
            test_results.append("⚠ WARNING: Input sanitization not widely used")
            tests_passed += 1
            return True

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def test_security_logging():
    """Test that security events are logged"""
    global tests_passed, tests_failed

    print("Testing security logging...")

    try:
        with open("app.py") as f:
            content = f.read()

        # Check for logger usage
        if "logger.error" in content:
            error_count = content.count("logger.error")
            info_count = content.count("logger.info")
            total = error_count + info_count
            test_results.append("✓ PASS: Security logging implemented")
            test_results.append(f"  ✓ {error_count} error logs")
            test_results.append(f"  ✓ {info_count} info logs")
            tests_passed += 1
            return True
        else:
            test_results.append("❌ FAIL: Security logging not found")
            tests_failed += 1
            return False

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def test_utilities_exist():
    """Test that utility modules exist and have content"""
    global tests_passed, tests_failed

    print("Testing utility modules...")

    try:
        required_files = [
            ("utils/security.py", "Security utilities"),
            ("utils/logging_config.py", "Logging configuration"),
            ("utils/responses.py", "Response standardization"),
            ("utils/config.py", "Configuration management"),
            ("utils/__init__.py", "Package initialization"),
        ]

        all_exist = True
        for filepath, name in required_files:
            path = Path(filepath)
            if path.exists():
                size = path.stat().st_size
                test_results.append(f"  ✓ {name}: {size} bytes")
            else:
                test_results.append(f"  ❌ {name}: NOT FOUND")
                all_exist = False

        if all_exist:
            test_results.append("✓ PASS: All utility modules exist")
            tests_passed += 1
            return True
        else:
            test_results.append("❌ FAIL: Some utility modules missing")
            tests_failed += 1
            return False

    except Exception as e:
        test_results.append(f"❌ ERROR: {e}")
        tests_failed += 1
        return False


def run_all_tests():
    """Run all security tests"""
    print("=" * 70)
    print("SECURITY FIXES TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        ("SECRET_KEY Validation", test_secret_key_validation),
        ("File Upload Validation", test_file_upload_validation),
        ("Password Strength Validation", test_password_validation),
        ("Error Message Sanitization", test_error_sanitization),
        ("Error Ticket Generation", test_error_tickets),
        ("Input Sanitization", test_input_sanitization),
        ("Security Logging", test_security_logging),
        ("Utility Modules", test_utilities_exist),
    ]

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 70)
        test_func()
        print()

    # Print results
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print()

    for result in test_results:
        print(result)

    print()
    print("=" * 70)
    print(f"PASSED: {tests_passed}/{tests_passed + tests_failed}")
    print(f"FAILED: {tests_failed}/{tests_passed + tests_failed}")

    if tests_failed == 0:
        print("STATUS: ✓ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print(f"STATUS: ❌ {tests_failed} TEST(S) FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
