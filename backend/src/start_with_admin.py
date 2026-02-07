# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start Flask with Admin Login Working
This script ensures the database is set up correctly and starts Flask
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Set admin password
os.environ["Evident_ADMIN_PASSWORD"] = "pQWN6CUNH04Gx6Ud73dfybu6jiV_DM4s"

print("\n" + "=" * 70)
print("Evident Quick Start - Admin Login Fixed")
print("=" * 70 + "\n")

from app import app

# Import models and app
from models_auth import TierLevel, User, db

ADMIN_EMAIL = "admin@Evident"

print("[OK] Flask app loaded")
print(f"[OK] Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

# Initialize database
with app.app_context():
    # Create all tables
    db.create_all()
    print("[OK] Database tables created/verified")

    # Check if admin exists
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()

    if not admin:
        print("\n[!] Admin not found, creating...")

        admin = User(
            email=ADMIN_EMAIL,
            full_name="Evident System Administrator",
            tier=TierLevel.ADMIN,
            is_admin=True,
            is_active=True,
            is_verified=True,
        )

        admin.set_password(os.environ["Evident_ADMIN_PASSWORD"])

        db.session.add(admin)
        db.session.commit()

        print("[OK] Admin account created")
    else:
        print(f"[OK] Admin exists: {admin.email}")
        print(f"    Tier: {admin.tier.name}")
        print(f"    Active: {admin.is_active}")

        # Update password to be sure
        admin.set_password(os.environ["Evident_ADMIN_PASSWORD"])
        admin.tier = TierLevel.ADMIN
        admin.is_admin = True
        admin.is_active = True
        admin.is_verified = True
        db.session.commit()
        print("[OK] Admin password updated")

    # Verify password
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()
    if admin.check_password(os.environ["Evident_ADMIN_PASSWORD"]):
        print("[OK] Password verification: SUCCESS")
    else:
        print("[ERROR] Password verification: FAILED")
        sys.exit(1)

print("\n" + "=" * 70)
print("READY TO START")
print("=" * 70)
print("\nAdmin Email: admin@Evident")
print(f"Password: {os.environ['Evident_ADMIN_PASSWORD']}")
print("\nLogin URL: http://localhost:5000/auth/login")
print("\nStarting Flask server...")
print("=" * 70 + "\n")

# Start Flask
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,  # Disable reloader to avoid double startup
    )
