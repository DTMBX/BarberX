# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Mobile Experience Validation Script
Checks that all mobile implementation files are in place and properly configured.
"""

from pathlib import Path


def validate_mobile_implementation():
    """Validate that all mobile files are present and configured correctly."""

    print("=" * 60)
    print("Evident Mobile Experience - Implementation Validation")
    print("=" * 60)
    print()

    issues = []
    warnings = []

    # Check required files exist
    print("📁 Checking Required Files...")
    print("-" * 60)

    required_files = {
        "templates/components/navbar.html": "Mobile navigation component",
        "assets/css/mobile.css": "Mobile styles",
        "assets/css/main.css": "Main CSS with mobile import",
        "MOBILE-EXPERIENCE-COMPLETE.md": "Implementation guide",
        "templates/components/navbar-integration-example.html": "Integration example",
    }

    for file_path, description in required_files.items():
        full_path = Path(file_path)
        if full_path.exists():
            file_size = full_path.stat().st_size
            print(f"✅ {file_path}")
            print(f"   {description} ({file_size:,} bytes)")
        else:
            print(f"❌ {file_path}")
            print(f"   Missing: {description}")
            issues.append(f"Missing file: {file_path}")

    print()

    # Check navbar.html content
    print("🔍 Checking Navigation Component...")
    print("-" * 60)

    navbar_path = Path("templates/components/navbar.html")
    if navbar_path.exists():
        content = navbar_path.read_text(encoding="utf-8")

        checks = {
            "nav-toggle": "Mobile hamburger button",
            "nav-menu": "Navigation menu container",
            "toggle.active": "Active state styles",
            "aria-expanded": "ARIA accessibility",
            "@media (max-width: 768px)": "Mobile media query",
            "transform: translateX": "Slide animation",
            "addEventListener": "JavaScript functionality",
        }

        for check, desc in checks.items():
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"⚠️ {desc} - may be missing")
                warnings.append(f"Navbar: {desc} not found")
    else:
        print("❌ navbar.html not found")
        issues.append("navbar.html file missing")

    print()

    # Check mobile.css content
    print("🎨 Checking Mobile Styles...")
    print("-" * 60)

    mobile_css_path = Path("assets/css/mobile.css")
    if mobile_css_path.exists():
        content = mobile_css_path.read_text(encoding="utf-8")

        checks = {
            "--mobile-breakpoint": "CSS variables",
            "@media (max-width: 768px)": "Mobile breakpoint",
            "@media (hover: none)": "Touch device detection",
            "min-height: 48px": "Touch target size",
            "@supports (-webkit-touch-callout": "iOS-specific fixes",
            "env(safe-area-inset-": "Notch support",
            "@media (prefers-reduced-motion": "Accessibility",
        }

        for check, desc in checks.items():
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"⚠️ {desc} - may be missing")
                warnings.append(f"Mobile CSS: {desc} not found")
    else:
        print("❌ mobile.css not found")
        issues.append("mobile.css file missing")

    print()

    # Check main.css imports mobile.css
    print("📦 Checking CSS Import...")
    print("-" * 60)

    main_css_path = Path("assets/css/main.css")
    if main_css_path.exists():
        content = main_css_path.read_text(encoding="utf-8")

        if "mobile.css" in content:
            print("✅ mobile.css imported in main.css")
        else:
            print("❌ mobile.css NOT imported in main.css")
            issues.append("mobile.css not imported in main.css")
            print("   Add this line to main.css:")
            print('   @import url("mobile.css");')
    else:
        print("⚠️ main.css not found")
        warnings.append("main.css file not found")

    print()

    # Check for potential conflicts
    print("⚠️ Checking for Potential Issues...")
    print("-" * 60)

    if navbar_path.exists():
        content = navbar_path.read_text(encoding="utf-8")

        # Check for common issues
        if "translateY(-100%)" in content:
            print("⚠️ Menu uses translateY (should be translateX for slide-in)")
            warnings.append("Menu animation may be incorrect (using translateY)")

        if content.count("addEventListener") < 3:
            print("⚠️ May be missing some event listeners")
            warnings.append("Less than 3 event listeners found")

        if "display: none" in content and "@media" in content:
            print("✅ Proper responsive display handling")

    print()

    # Print summary
    print("=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)

    if not issues and not warnings:
        print("✅ All checks passed! Mobile implementation is complete.")
        print()
        print("Next Steps:")
        print("1. Test in Chrome DevTools responsive mode")
        print("2. Test on real iOS/Android devices")
        print("3. Run Lighthouse mobile audit")
        return True
    else:
        if issues:
            print(f"\n❌ {len(issues)} Critical Issue(s) Found:")
            for issue in issues:
                print(f"   • {issue}")

        if warnings:
            print(f"\n⚠️ {len(warnings)} Warning(s):")
            for warning in warnings:
                print(f"   • {warning}")

        print("\nPlease fix the issues above before deploying to production.")
        return False


if __name__ == "__main__":
    success = validate_mobile_implementation()
    exit(0 if success else 1)
