# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Quick Integration Script - Add License Checking to app.py

This script modifies app.py to include license validation for self-hosted deployments.
Run this to integrate the license system into your existing Flask app.
"""

import os
import sys


def integrate_license_system():
    """
    Add license checking to app.py
    """
    print("🔧 Integrating License System into app.py...")
    print()

    app_py_path = "app.py"

    if not os.path.exists(app_py_path):
        print("❌ Error: app.py not found in current directory")
        return False

    # Read current app.py
    with open(app_py_path, encoding="utf-8") as f:
        content = f.read()

    # Check if already integrated
    if "IS_SELF_HOSTED" in content:
        print("⚠️  License system already integrated!")
        print("   No changes needed.")
        return True

    # Find the imports section (after initial docstring/comments)
    insert_position = content.find("from flask import")

    if insert_position == -1:
        insert_position = content.find("import flask")

    if insert_position == -1:
        print("❌ Error: Could not find Flask imports in app.py")
        return False

    # Prepare license integration code
    license_code = """
# ============================================================================
# LICENSE SYSTEM (Self-Hosted Deployments)
# ============================================================================

import os

# Detect deployment mode
IS_SELF_HOSTED = bool(os.getenv('Evident_LICENSE_KEY'))

if IS_SELF_HOSTED:
    print("🔒 Running in SELF-HOSTED mode - License validation enabled")
    from license_client import get_license_client
    
    # Validate license on startup
    license_client = get_license_client()
    if not license_client.is_valid():
        print("❌ LICENSE VALIDATION FAILED - Application cannot start")
        print("   Contact: enterprise@Evident")
        sys.exit(1)
    else:
        license_info = license_client.get_license_info()
        print(f"✅ License validated: {license_info.get('organization')}")
        print(f"   Tier: {license_info.get('tier')}")
        print(f"   Expires: {license_info.get('expires_at')}")
else:
    print("☁️  Running in SAAS mode - Web-based deployment")

"""

    # Insert license code
    content = content[:insert_position] + license_code + content[insert_position:]

    # Add license checking middleware
    # Find where Flask app is created
    app_creation_pos = content.find("app = Flask(__name__)")

    if app_creation_pos == -1:
        print("⚠️  Could not find Flask app creation")
        print("   License startup check added, but you'll need to add middleware manually")
    else:
        # Find end of app configuration
        routes_start = content.find("@app.route", app_creation_pos)

        if routes_start == -1:
            routes_start = content.find("if __name__", app_creation_pos)

        middleware_code = """

# License validation middleware (self-hosted only)
if IS_SELF_HOSTED:
    @app.before_request
    def check_license_middleware():
        \"\"\"Validate license before each request\"\"\"
        # Skip static files and health check
        if request.path.startswith('/static') or request.path == '/health':
            return None
        
        # Skip API endpoints that have their own auth
        if request.path.startswith('/api/v1/license'):
            return None
        
        license_client = get_license_client()
        if not license_client.is_valid():
            return jsonify({
                'error': 'License validation failed',
                'message': 'Please contact enterprise@Evident',
                'contact': 'enterprise@Evident'
            }), 403

"""

        content = content[:routes_start] + middleware_code + content[routes_start:]

    # Register license routes blueprint
    blueprint_registration = """
# Register license management routes
if IS_SELF_HOSTED or os.getenv('ENABLE_LICENSE_API'):
    from license_routes import license_bp
    app.register_blueprint(license_bp)
    print("✅ License API routes registered at /api/v1/license")

"""

    # Find where blueprints are registered or before routes
    blueprint_pos = content.rfind("app.register_blueprint", 0, routes_start)

    if blueprint_pos == -1:
        # No existing blueprints, add before routes
        blueprint_pos = routes_start
    else:
        # Add after last blueprint
        blueprint_pos = content.find("\n\n", blueprint_pos) + 2

    content = content[:blueprint_pos] + blueprint_registration + content[blueprint_pos:]

    # Backup original
    backup_path = "app.py.backup"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📋 Backup created: {backup_path}")

    # Write modified app.py
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ License system integrated successfully!")
    print()
    print("📝 Changes made:")
    print("   1. Added IS_SELF_HOSTED detection")
    print("   2. Added license validation on startup")
    print("   3. Added license checking middleware")
    print("   4. Registered license API routes")
    print()
    print("🧪 Test it:")
    print("   # Web mode (current):")
    print("   python app.py")
    print()
    print("   # Self-hosted mode:")
    print("   export Evident_LICENSE_KEY='BX-XXXX-XXXX-XXXX-XXXX'")
    print("   python app.py")
    print()

    return True


def create_database_migration():
    """Create database migration for license tables"""
    print("📊 Creating database migration for license tables...")

    migration_script = """#!/usr/bin/env python3
\"\"\"
Database migration: Add license management tables
Run this to create license-related tables in your database
\"\"\"

from app import app, db
from models_license import License, LicenseValidation

def migrate():
    with app.app_context():
        # Create license tables
        db.create_all()
        print("✅ License tables created successfully")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'licenses' in tables and 'license_validations' in tables:
            print("   - licenses table ✅")
            print("   - license_validations table ✅")
            print()
            print("🎉 Migration complete!")
        else:
            print("⚠️  Warning: Some tables may not have been created")
            print(f"   Found tables: {tables}")

if __name__ == '__main__':
    migrate()
"""

    with open("migrate_add_licenses.py", "w", encoding="utf-8") as f:
        f.write(migration_script)

    os.chmod("migrate_add_licenses.py", 0o755)

    print("✅ Created: migrate_add_licenses.py")
    print("   Run: python migrate_add_licenses.py")
    print()


def create_test_license_script():
    """Create script to generate test licenses"""
    print("🎟️  Creating test license generation script...")

    test_script = """#!/usr/bin/env python3
\"\"\"
Create Test License
Generate a license key for testing self-hosted deployment
\"\"\"

from app import app, db
from models_license import LicenseService

def create_test_license():
    with app.app_context():
        print("Creating test license...")
        print()
        
        license = LicenseService.create_license(
            organization_name="Test Organization",
            contact_email="test@example.com",
            contact_name="Test User",
            tier="ENTERPRISE",
            duration_days=30,  # 30-day trial
            max_machines=1,
            monthly_video_quota=500,
            features={
                'white_label': True,
                'api_access': True,
                'priority_support': True,
                'forensic_analysis': True,
            }
        )
        
        print("✅ Test license created!")
        print()
        print(f"   License Key: {license.license_key}")
        print(f"   Organization: {license.organization_name}")
        print(f"   Tier: {license.tier}")
        print(f"   Expires: {license.expires_at}")
        print(f"   Max Machines: {license.max_machines}")
        print()
        print("🔧 To use this license:")
        print(f"   export Evident_LICENSE_KEY='{license.license_key}'")
        print("   python app.py")
        print()

if __name__ == '__main__':
    create_test_license()
"""

    with open("create_test_license.py", "w", encoding="utf-8") as f:
        f.write(test_script)

    os.chmod("create_test_license.py", 0o755)

    print("✅ Created: create_test_license.py")
    print("   Run: python create_test_license.py")
    print()


def main():
    """Main integration process"""
    print("=" * 70)
    print(" Evident License System - Quick Integration")
    print("=" * 70)
    print()

    # Step 1: Integrate license checking
    if not integrate_license_system():
        sys.exit(1)

    # Step 2: Create database migration
    create_database_migration()

    # Step 3: Create test license script
    create_test_license_script()

    print("=" * 70)
    print(" Integration Complete! 🎉")
    print("=" * 70)
    print()
    print("📋 Next Steps:")
    print()
    print("1. Run database migration:")
    print("   python migrate_add_licenses.py")
    print()
    print("2. Create a test license:")
    print("   python create_test_license.py")
    print()
    print("3. Test web mode (current behavior):")
    print("   python app.py")
    print()
    print("4. Test self-hosted mode:")
    print("   export Evident_LICENSE_KEY='<key-from-step-2>'")
    print("   python app.py")
    print()
    print("5. Build Docker image:")
    print("   docker build -f Dockerfile.enterprise -t Evident/enterprise .")
    print()
    print("6. Deploy with Docker Compose:")
    print("   docker-compose -f docker-compose.enterprise.yml up -d")
    print()
    print("📚 Read IMPLEMENTATION-COMPLETE.md for full details")
    print()


if __name__ == "__main__":
    main()
