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


from app import app

# Import models and app
from models_auth import TierLevel, User, db

# Initialize database
with app.app_context():
    # Create all tables
    db.create_all()
    print("[OK] Database tables created/verified")

    # Check if admin exists
    ADMIN_EMAIL = "admin@Evident.info"
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()

    if not admin:
        print("Admin not found, creating...")
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
        print("Admin account created.")
    else:
        print(f"Admin exists: {admin.email}")
        # Update password to be sure
        admin.set_password(os.environ["Evident_ADMIN_PASSWORD"])
        admin.tier = TierLevel.ADMIN
        admin.is_admin = True
        admin.is_active = True
        admin.is_verified = True
        db.session.commit()
        print("Admin password updated.")

    # Verify password
    admin = User.query.filter_by(email="admin@Evident.info").first()
    if admin.check_password(os.environ["Evident_ADMIN_PASSWORD"]):
        print("Password verification: SUCCESS")
    else:
        print("Password verification: FAILED")
        sys.exit(1)


print("\n" + "=" * 70)
print("READY TO START")
print("=" * 70)
print("Login URL: http://localhost:5000/auth/login")
print("Starting Flask server...")
print("=" * 70 + "\n")

# Start Flask
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,  # Disable reloader to avoid double startup
    )
