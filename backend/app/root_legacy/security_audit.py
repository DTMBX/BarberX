# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Security Audit Script for Evident
Checks all endpoints for proper error handling, input validation, and security
"""

import re
import sys
from pathlib import Path


def check_error_handling(file_path):
    """Check if endpoints have proper error handling"""
    issues = []

    with open(file_path, encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    # Find all route definitions
    routes = []
    for i, line in enumerate(lines):
        if "@app.route" in line or "@login_required" in line:
            routes.append((i + 1, line.strip()))

    # Check for error exposures
    for i, line in enumerate(lines):
        line_num = i + 1

        # Check for raw exceptions being returned
        if "jsonify({" in line and ("error" in line or "str(e)" in line):
            # This is likely error handling - good!
            continue

        # Check for stack trace exposure
        if "traceback" in line.lower() and "import" not in line:
            issues.append(f"Line {line_num}: Potential stack trace exposure")

        # Check for print(e) in production
        if re.search(r'print\([\'"]?.*e[\'"]?\)', line):
            issues.append(f"Line {line_num}: Exception printed (should use logger)")

    return issues


def check_input_validation(file_path):
    """Check for input validation"""
    issues = []

    with open(file_path, encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    for i, line in enumerate(lines):
        line_num = i + 1

        # Check for direct request.form or request.args usage without validation
        if "request.form[" in line or "request.args[" in line:
            # Check if there's a .get() or validation nearby
            context = "\n".join(lines[max(0, i - 2) : min(len(lines), i + 3)])
            if "InputValidator" not in context and ".get(" not in line:
                issues.append(f"Line {line_num}: Direct form/args access without validation")

        # Check for SQL injection risks (raw SQL)
        if "execute(" in line and ("'" in line or '"' in line):
            if 'f"' in line or "f'" in line:
                issues.append(f"Line {line_num}: Potential SQL injection (f-string in SQL)")

    return issues


def check_authentication(file_path):
    """Check for missing authentication on sensitive endpoints"""
    issues = []

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if it's a route decorator
        if line.startswith("@app.route("):
            # Check if it's an API endpoint
            if "/api/" in line:
                # Look ahead for @login_required
                next_few_lines = "".join(lines[i : min(i + 3, len(lines))])

                # Skip health check and public endpoints
                if "/api/health" not in line and "@login_required" not in next_few_lines:
                    issues.append(f"Line {i + 1}: API endpoint without @login_required: {line}")

        i += 1

    return issues


def check_file_upload_security(file_path):
    """Check file upload endpoints for security"""
    issues = []

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Check for file upload handling
    if "request.files" in content:
        # Check for security measures
        if "ALLOWED_EXTENSIONS" not in content and "allowed_file" not in content:
            issues.append("File upload without extension validation")

        if "secure_filename" not in content:
            issues.append("File upload without secure_filename()")

        if "file_size" not in content.lower() and "max_content_length" not in content.lower():
            issues.append("File upload without size validation")

    return issues


def check_password_security(file_path):
    """Check password handling"""
    issues = []

    with open(file_path, encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    for i, line in enumerate(lines):
        line_num = i + 1

        # Check for plaintext password storage
        if "password =" in line and "generate_password_hash" not in line:
            context = "\n".join(lines[max(0, i - 2) : min(len(lines), i + 3)])
            if "password" in line and "=" in line and "hash" not in context.lower():
                issues.append(f"Line {line_num}: Potential plaintext password")

        # Check password strength validation
        if "def register" in line or "def signup" in line:
            context = "\n".join(lines[i : min(len(lines), i + 50)])
            if "password" in context.lower() and "len(" not in context:
                issues.append(f"Line {line_num}: No password strength validation in registration")

    return issues


def check_csrf_protection(file_path):
    """Check CSRF protection"""
    issues = []

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Check if CSRF is enabled
    if "CSRFProtect" not in content and "csrf" not in content.lower():
        issues.append("No CSRF protection detected")

    return issues


def main():
    """Run all security checks"""
    app_file = Path("app.py")

    if not app_file.exists():
        print("❌ app.py not found in current directory")
        print("Please run this script from the Evident.info root directory")
        return 1

    print("🔒 Evident SECURITY AUDIT")
    print("=" * 60)
    print()

    all_issues = {}

    # Run all checks
    checks = {
        "Error Handling": check_error_handling,
        "Input Validation": check_input_validation,
        "Authentication": check_authentication,
        "File Upload Security": check_file_upload_security,
        "Password Security": check_password_security,
        "CSRF Protection": check_csrf_protection,
    }

    for check_name, check_func in checks.items():
        print(f"🔍 Checking {check_name}...")
        issues = check_func(app_file)
        all_issues[check_name] = issues

        if issues:
            print(f"   ⚠️  Found {len(issues)} issue(s)")
        else:
            print("   ✅ Passed")
        print()

    # Summary
    print("=" * 60)
    print("📊 AUDIT SUMMARY")
    print("=" * 60)
    print()

    total_issues = sum(len(issues) for issues in all_issues.values())

    if total_issues == 0:
        print("✅ NO SECURITY ISSUES FOUND!")
        print()
        print("Your application passes all security checks.")
        return 0

    print(f"⚠️  FOUND {total_issues} POTENTIAL ISSUE(S)")
    print()

    for check_name, issues in all_issues.items():
        if issues:
            print(f"\n{check_name}:")
            for issue in issues:
                print(f"  • {issue}")

    print()
    print("=" * 60)
    print("📋 RECOMMENDATIONS")
    print("=" * 60)
    print()
    print("1. Review all flagged items above")
    print("2. Implement missing security measures")
    print("3. Re-run this audit script")
    print("4. Consider penetration testing before launch")
    print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
