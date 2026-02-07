# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database migration: Add ChatGPT integration tables
Run with: python migrate_add_chatgpt.py
"""

from app import app
from models_auth import db


def add_chatgpt_tables():
    """Add tables for ChatGPT integration"""

    with app.app_context():
        # Import the models to ensure they're registered

        print("Creating ChatGPT integration tables...")

        # Create all tables
        db.create_all()

        print("✅ Tables created successfully:")
        print("  - projects")
        print("  - conversations")
        print("  - messages")
        print("  - user_api_keys")

        print("\n✅ Migration complete!")
        print("\nNext steps:")
        print("1. Register the chatgpt blueprint in app.py")
        print("2. Add openai package: pip install openai")
        print("3. Add cryptography package: pip install cryptography")
        print("4. Set API_KEY_ENCRYPTION_KEY environment variable")


if __name__ == "__main__":
    add_chatgpt_tables()
