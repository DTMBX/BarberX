# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database Migration: Add API Usage Metering Tables

This migration adds:
- api_usage_logs: Detailed API usage tracking with verification
- user_api_quotas: Per-user quota and rate limit tracking
- encrypted_api_keys: Securely stored API keys

Run: python migrations/add_api_metering_tables.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_migration():
    """Run the migration to add API metering tables"""
    from app import app, db

    with app.app_context():
        # Import the models to register them

        print("=" * 60)
        print("API Usage Metering - Database Migration")
        print("=" * 60)

        # Check if tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        tables_to_create = []

        if "api_usage_logs" not in existing_tables:
            tables_to_create.append("api_usage_logs")
        if "user_api_quotas" not in existing_tables:
            tables_to_create.append("user_api_quotas")
        if "encrypted_api_keys" not in existing_tables:
            tables_to_create.append("encrypted_api_keys")

        if not tables_to_create:
            print("\n✓ All API metering tables already exist!")
            print("  - api_usage_logs")
            print("  - user_api_quotas")
            print("  - encrypted_api_keys")
            return True

        print(f"\nCreating tables: {', '.join(tables_to_create)}")

        # Create tables
        try:
            # Create only the new tables
            from sqlalchemy import text

            if "api_usage_logs" in tables_to_create:
                db.engine.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS api_usage_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        provider VARCHAR(50) NOT NULL,
                        model VARCHAR(100) NOT NULL,
                        prompt_tokens INTEGER DEFAULT 0,
                        completion_tokens INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        estimated_cost_usd DECIMAL(10,6) DEFAULT 0,
                        endpoint VARCHAR(200),
                        request_type VARCHAR(50),
                        request_hash VARCHAR(64),
                        response_hash VARCHAR(64),
                        record_hash VARCHAR(64),
                        success BOOLEAN DEFAULT 1,
                        error_type VARCHAR(50),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """
                    )
                )
                db.engine.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_usage_logs_user ON api_usage_logs(user_id)"
                    )
                )
                db.engine.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_usage_logs_provider ON api_usage_logs(provider)"
                    )
                )
                db.engine.execute(
                    text("CREATE INDEX IF NOT EXISTS idx_usage_logs_model ON api_usage_logs(model)")
                )
                db.engine.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_usage_logs_created ON api_usage_logs(created_at)"
                    )
                )
                print("  ✓ Created api_usage_logs table with indexes")

            if "user_api_quotas" in tables_to_create:
                db.engine.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS user_api_quotas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL UNIQUE,
                        monthly_token_limit INTEGER DEFAULT 100000,
                        monthly_cost_limit_usd DECIMAL(10,2) DEFAULT 10.00,
                        period_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                        tokens_used_this_period INTEGER DEFAULT 0,
                        cost_this_period_usd DECIMAL(10,6) DEFAULT 0,
                        alert_threshold_percent INTEGER DEFAULT 80,
                        alert_sent BOOLEAN DEFAULT 0,
                        requests_per_minute INTEGER DEFAULT 60,
                        last_request_at DATETIME,
                        requests_this_minute INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """
                    )
                )
                print("  ✓ Created user_api_quotas table")

            if "encrypted_api_keys" in tables_to_create:
                db.engine.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS encrypted_api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        provider VARCHAR(50) NOT NULL,
                        key_name VARCHAR(100),
                        encrypted_key TEXT NOT NULL,
                        key_prefix VARCHAR(10),
                        key_hash VARCHAR(64) NOT NULL UNIQUE,
                        is_active BOOLEAN DEFAULT 1,
                        is_valid BOOLEAN DEFAULT 1,
                        last_validated_at DATETIME,
                        validation_error VARCHAR(255),
                        total_requests INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        total_cost_usd DECIMAL(10,2) DEFAULT 0,
                        last_used_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        UNIQUE (user_id, provider, key_hash)
                    )
                """
                    )
                )
                db.engine.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_api_keys_user ON encrypted_api_keys(user_id)"
                    )
                )
                print("  ✓ Created encrypted_api_keys table with indexes")

            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)

            print("\nNew API endpoints available:")
            print("  POST   /api/v1/metering/api-keys         - Store API key (encrypted)")
            print("  GET    /api/v1/metering/api-keys         - List API keys (masked)")
            print("  DELETE /api/v1/metering/api-keys/<id>    - Delete API key")
            print("  POST   /api/v1/metering/api-keys/<id>/validate - Validate key")
            print("  GET    /api/v1/metering/usage            - Get usage summary")
            print("  GET    /api/v1/metering/quota            - Get quota status")
            print("  GET    /api/v1/metering/audit            - Get verifiable audit trail")
            print("  POST   /api/v1/metering/estimate         - Estimate API costs")

            return True

        except Exception as e:
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def verify_tables():
    """Verify tables were created correctly"""
    from app import app, db

    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        print("\nVerifying tables...")
        required = ["api_usage_logs", "user_api_quotas", "encrypted_api_keys"]

        all_present = True
        for table in required:
            if table in tables:
                columns = [c["name"] for c in inspector.get_columns(table)]
                print(f"  ✓ {table} ({len(columns)} columns)")
            else:
                print(f"  ✗ {table} - MISSING")
                all_present = False

        return all_present


if __name__ == "__main__":
    success = run_migration()
    if success:
        verify_tables()
    sys.exit(0 if success else 1)
