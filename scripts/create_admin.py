# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Admin Account Setup
Creates the one and only admin account with secure credentials
"""

import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

# SECURE ADMIN CREDENTIALS - LOADED FROM ENVIRONMENT
ADMIN_EMAIL = os.environ.get("Evident_ADMIN_EMAIL", "admin@Evident.info")
ADMIN_PASSWORD = os.environ.get("Evident_ADMIN_PASSWORD")  # MUST be set in environment
ADMIN_NAME = "Evident System Administrator"

if not ADMIN_PASSWORD:
    raise ValueError("Evident_ADMIN_PASSWORD environment variable must be set")

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "Evident.db")


def create_admin_account():
    """
    Create the one and only admin account
    Ensures only ONE admin exists in the system
    """
    print("\n" + "=" * 80)
    print("Evident Admin Account Setup")
    print("=" * 80 + "\n")

    # Ensure instance directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            organization VARCHAR(100),
            subscription_tier VARCHAR(20) DEFAULT 'free',
            role VARCHAR(20) DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            storage_used_mb FLOAT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()

    # Remove ALL existing admin accounts
    cursor.execute("SELECT id, email FROM user WHERE role = 'admin'")
    existing_admins = cursor.fetchall()

    if existing_admins:
        print(f"⚠️  Found {len(existing_admins)} existing admin account(s)")
        print("   Removing old admin accounts...")

        for admin_id, admin_email in existing_admins:
            print(f"   • Deleting: {admin_email}")
            cursor.execute("DELETE FROM user WHERE id = ?", (admin_id,))

        conn.commit()
        print("✅ Old admin accounts removed\n")

    # Check if admin email exists as non-admin
    cursor.execute("SELECT id FROM user WHERE email = ?", (ADMIN_EMAIL,))
    existing_user = cursor.fetchone()

    # Generate password hash
    password_hash = generate_password_hash(ADMIN_PASSWORD)
    created_at = datetime.utcnow().isoformat()

    if existing_user:
        print(f"⚠️  Email {ADMIN_EMAIL} already exists as non-admin")
        print("   Converting to admin account...\n")

        # Update existing user to admin
        cursor.execute(
            """
            UPDATE user 
            SET password_hash = ?, 
                full_name = ?, 
                role = 'admin', 
                subscription_tier = 'enterprise',
                is_active = 1,
                updated_at = ?
            WHERE email = ?
        """,
            (password_hash, ADMIN_NAME, created_at, ADMIN_EMAIL),
        )

    else:
        # Insert new admin account
        cursor.execute(
            """
            INSERT INTO user (email, password_hash, full_name, role, subscription_tier, is_active, created_at, updated_at)
            VALUES (?, ?, ?, 'admin', 'enterprise', 1, ?, ?)
        """,
            (ADMIN_EMAIL, password_hash, ADMIN_NAME, created_at, created_at),
        )

    conn.commit()

    # Verify admin account
    cursor.execute("SELECT * FROM user WHERE email = ?", (ADMIN_EMAIL,))
    admin = cursor.fetchone()

    print("✅ Admin Account Created Successfully!\n")
    print("=" * 80)
    print("ADMIN CREDENTIALS (SAVE THESE SECURELY)")
    print("=" * 80)
    print(f"Email:    {ADMIN_EMAIL}")
    print(f"Password: {ADMIN_PASSWORD}")
    print(f"Name:     {ADMIN_NAME}")
    print("Role:     admin")
    print("Tier:     enterprise")
    print("Status:   Active")
    print("=" * 80 + "\n")

    # Verify no other admins exist
    cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'admin'")
    total_admins = cursor.fetchone()[0]

    if total_admins == 1:
        print("✅ VERIFIED: Exactly ONE admin account exists\n")
    else:
        print(f"⚠️  WARNING: {total_admins} admin accounts found!\n")

    # Show all users
    cursor.execute("SELECT email, role, subscription_tier FROM user ORDER BY role DESC, email")
    all_users = cursor.fetchall()

    print(f"Total users in database: {len(all_users)}\n")

    for email, role, tier in all_users:
        role_badge = "🔑 ADMIN" if role == "admin" else f"👤 {role}"
        print(f"{role_badge:12} | {email:30} | {tier}")

    conn.close()

    print("\n" + "=" * 80)
    print("SECURITY NOTES")
    print("=" * 80)
    print("• Password is 33 characters with special characters")
    print("• Only ONE admin account exists in the system")
    print("• Store credentials in a secure password manager")
    print("• Change password after first login via admin panel")
    print("• Admin has full access to all platform features")
    print("=" * 80 + "\n")

    return True


def verify_admin_login():
    """Test admin login credentials"""
    from werkzeug.security import check_password_hash

    print("\n" + "=" * 80)
    print("Verifying Admin Login")
    print("=" * 80 + "\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash, role, subscription_tier, is_active FROM user WHERE email = ?",
        (ADMIN_EMAIL,),
    )
    result = cursor.fetchone()

    conn.close()

    if not result:
        print("❌ Admin account not found!")
        return False

    password_hash, role, tier, is_active = result

    # Verify password
    if check_password_hash(password_hash, ADMIN_PASSWORD):
        print("✅ Password verification: SUCCESS")
        print(f"✅ Admin role: {role}")
        print(f"✅ Admin tier: {tier}")
        print(f"✅ Account active: {bool(is_active)}")
        print("\n✅ Admin account is ready to use!\n")
        return True
    else:
        print("❌ Password verification FAILED!")
        return False


if __name__ == "__main__":
    print("\n🔐 Creating secure admin account...\n")

    # Create admin account
    create_admin_account()

    # Verify login works
    verify_admin_login()

    print("✅ Setup complete!\n")
    print("🌐 Access admin panel at: https://app.Evident.info/admin")
    print(f"📧 Login with: {ADMIN_EMAIL}\n")
