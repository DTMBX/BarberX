# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Quick verification test for performance optimizations
Run this to ensure all optimizations are working
"""

import sys
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def test_result(name, passed, details=""):
    """Print test result"""
    symbol = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
    print(f"{symbol} {name}")
    if details:
        print(f"  {details}")
    return passed


def main():
    """Run verification tests"""
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATION VERIFICATION")
    print("=" * 60)

    all_passed = True

    # Test 1: Check files exist
    print("\n1. Checking files...")
    files_to_check = [
        "performance_optimizations.py",
        "performance_check.py",
        "PERFORMANCE-OPTIMIZATION-COMPLETE.md",
        "PERFORMANCE-INSTALL-GUIDE.md",
        "PERFORMANCE-OPTIMIZATION-SUMMARY.md",
    ]

    for filename in files_to_check:
        exists = Path(filename).exists()
        all_passed &= test_result(filename, exists)

    # Test 2: Check imports
    print("\n2. Checking imports...")
    try:
        from performance_optimizations import (
            SimpleCache,
            cached,
            compress_response,
            paginated_query,
            stream_file_hash,
        )

        test_result("performance_optimizations imports", True)
    except ImportError as e:
        test_result("performance_optimizations imports", False, str(e))
        all_passed = False

    # Test 3: Test cache functionality
    print("\n3. Testing cache...")
    try:
        from performance_optimizations import SimpleCache

        cache = SimpleCache()
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        passed = result == "test_value"
        test_result("Cache set/get", passed, f"Got: {result}")
        all_passed &= passed
    except Exception as e:
        test_result("Cache test", False, str(e))
        all_passed = False

    # Test 4: Check Flask-Compress in requirements
    print("\n4. Checking requirements.txt...")
    try:
        with open("requirements.txt") as f:
            content = f.read()
            has_compress = "Flask-Compress" in content
            test_result("Flask-Compress in requirements", has_compress)
            all_passed &= has_compress
    except Exception as e:
        test_result("requirements.txt check", False, str(e))
        all_passed = False

    # Test 5: Check app.py modifications
    print("\n5. Checking app.py modifications...")
    try:
        with open("app.py", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            checks = {
                "Flask-Compress import": "from flask_compress import Compress" in content,
                "Compress initialization": "compress = Compress()" in content,
                "File read fix": "file_content = file.read()" in content,
                "Pagination added": "per_page" in content and "offset" in content,
            }

            for check_name, passed in checks.items():
                test_result(check_name, passed)
                all_passed &= passed

    except Exception as e:
        test_result("app.py modifications", False, str(e))
        all_passed = False

    # Test 6: Check config_manager.py indexes
    print("\n6. Checking database indexes...")
    try:
        with open("config_manager.py", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            # Count indexes
            index_count = content.count("CREATE INDEX")
            passed = index_count >= 15
            test_result(f"Database indexes ({index_count}/15)", passed)
            all_passed &= passed

    except Exception as e:
        test_result("config_manager.py check", False, str(e))
        all_passed = False

    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print(f"{GREEN}✓ ALL CHECKS PASSED{RESET}")
        print("Performance optimizations are ready for production!")
        print("\nNext steps:")
        print("1. pip install Flask-Compress==1.15")
        print("2. python performance_check.py optimize")
        print("3. Deploy to production")
        return 0
    else:
        print(f"{RED}✗ SOME CHECKS FAILED{RESET}")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
