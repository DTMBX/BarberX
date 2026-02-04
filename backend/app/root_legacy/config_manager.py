"""
Optimized Configuration & Database Management
Production-ready configuration and connection pooling

Features:
- Environment-based configuration
- Database connection pooling
- Query optimization
- Index management
- Migration helpers
- Backup utilities
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DatabaseConfig:
    """Database configuration"""

    engine: str  # sqlite, postgresql, mysql
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = "Evident.db"
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class CacheConfig:
    """Cache configuration"""

    backend: str = "memory"  # memory, redis, memcached
    host: Optional[str] = None
    port: Optional[int] = None
    default_ttl: int = 3600
    max_size: int = 1000


@dataclass
class AppConfig:
    """Application configuration"""

    environment: str = "development"  # development, staging, production
    debug: bool = True
    secret_key: str = os.urandom(24).hex()
    upload_folder: str = "uploads"
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = None

    # Database
    database: DatabaseConfig = None

    # Cache
    cache: CacheConfig = None

    # External services
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    openai_api_key: Optional[str] = None
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None

    # Feature flags
    enable_2fa: bool = True
    enable_stripe: bool = True
    enable_ai_analysis: bool = True
    enable_legal_tools: bool = True

    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ["mp4", "avi", "mov", "mp3", "wav", "pdf", "jpg", "png"]

        if self.database is None:
            self.database = DatabaseConfig(engine="sqlite")

        if self.cache is None:
            self.cache = CacheConfig()


class ConfigManager:
    """Centralized configuration management"""

    def __init__(self, config_file: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: Optional[Path]) -> AppConfig:
        """Load configuration from file or environment"""

        # Try to load from file
        if config_file and config_file.exists():
            with open(config_file, "r") as f:
                data = json.load(f)
                return self._dict_to_config(data)

        # Load from environment
        env = os.getenv("FLASK_ENV", "development")

        # Base config
        config = AppConfig(environment=env)

        # Override from environment variables
        config.debug = os.getenv("DEBUG", "true").lower() == "true"
        config.secret_key = os.getenv("SECRET_KEY", config.secret_key)
        config.upload_folder = os.getenv("UPLOAD_FOLDER", "uploads")

        # Database config
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            config.database = self._parse_database_url(db_url)
        else:
            config.database = DatabaseConfig(
                engine=os.getenv("DB_ENGINE", "sqlite"),
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", 0)) if os.getenv("DB_PORT") else None,
                database=os.getenv("DB_NAME", "Evident.db"),
                username=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            )

        # External services
        config.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        config.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        config.openai_api_key = os.getenv("OPENAI_API_KEY")
        config.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        config.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        return config

    def _parse_database_url(self, url: str) -> DatabaseConfig:
        """Parse database URL into config"""
        # Simple parser for postgresql://user:pass@host:port/db
        if url.startswith("sqlite:///"):
            return DatabaseConfig(engine="sqlite", database=url.replace("sqlite:///", ""))

        # Parse full URL
        from urllib.parse import urlparse

        parsed = urlparse(url)

        return DatabaseConfig(
            engine=parsed.scheme.split("+")[0],
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip("/"),
            username=parsed.username,
            password=parsed.password,
        )

    def _dict_to_config(self, data: Dict) -> AppConfig:
        """Convert dictionary to AppConfig"""
        # Simplified conversion
        return AppConfig(**data)

    def get_database_uri(self) -> str:
        """Get SQLAlchemy database URI"""
        db = self.config.database

        if db.engine == "sqlite":
            return f"sqlite:///{db.database}"

        # PostgreSQL/MySQL
        auth = f"{db.username}:{db.password}@" if db.username else ""
        port = f":{db.port}" if db.port else ""

        return f"{db.engine}://{auth}{db.host}{port}/{db.database}"

    def get_sqlalchemy_config(self) -> Dict:
        """Get SQLAlchemy configuration dict"""
        db = self.config.database

        config = {
            "SQLALCHEMY_DATABASE_URI": self.get_database_uri(),
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ECHO": db.echo,
        }

        # Add pool configuration for non-SQLite
        if db.engine != "sqlite":
            config.update(
                {
                    "SQLALCHEMY_ENGINE_OPTIONS": {
                        "pool_size": db.pool_size,
                        "max_overflow": db.max_overflow,
                        "pool_timeout": db.pool_timeout,
                        "pool_recycle": db.pool_recycle,
                        "pool_pre_ping": True,  # Verify connections before using
                    }
                }
            )

        return config


class DatabaseOptimizer:
    """Database query optimization helpers"""

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def create_indexes(self):
        """Create optimized indexes for frequently queried fields"""
        indexes = [
            # User indexes - email already has index from model definition
            "CREATE INDEX IF NOT EXISTS idx_users_tier ON users(tier)",
            "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
            # Analysis indexes
            "CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_user_status ON analyses(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_case_number ON analyses(case_number)",
            # Usage tracking indexes
            "CREATE INDEX IF NOT EXISTS idx_usage_user_id ON usage_tracking(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_usage_year_month ON usage_tracking(year, month)",
            "CREATE INDEX IF NOT EXISTS idx_usage_updated_at ON usage_tracking(updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_usage_user_year_month ON usage_tracking(user_id, year, month)",
            # API keys indexes
            "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active)",
        ]

        for index_sql in indexes:
            try:
                # Use text() for raw SQL in SQLAlchemy 2.0+
                from sqlalchemy import text

                with self.db.engine.connect() as conn:
                    conn.execute(text(index_sql))
                    conn.commit()
                self.logger.info(f"Created index: {index_sql[:50]}...")
            except Exception as e:
                self.logger.warning(f"Index creation failed: {str(e)}")

    def analyze_tables(self):
        """Analyze tables for query optimization (PostgreSQL/MySQL)"""
        try:
            self.db.engine.execute("ANALYZE")
            self.logger.info("Table analysis completed")
        except Exception as e:
            self.logger.debug(f"Table analysis not supported: {str(e)}")

    def vacuum_database(self):
        """Vacuum database (SQLite/PostgreSQL)"""
        try:
            self.db.engine.execute("VACUUM")
            self.logger.info("Database vacuumed")
        except Exception as e:
            self.logger.debug(f"Vacuum not supported: {str(e)}")


class DatabaseBackup:
    """Database backup utilities"""

    def __init__(self, db, backup_dir: Path = Path("backups")):
        self.db = db
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def backup(self) -> Path:
        """Create database backup"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.sql"

        try:
            # SQLite backup
            if "sqlite" in str(self.db.engine.url):
                import shutil

                db_path = str(self.db.engine.url).replace("sqlite:///", "")
                shutil.copy2(db_path, backup_file.with_suffix(".db"))
                self.logger.info(f"Backup created: {backup_file}.db")
                return backup_file.with_suffix(".db")

            # PostgreSQL backup (requires pg_dump)
            elif "postgresql" in str(self.db.engine.url):
                import subprocess

                url = self.db.engine.url
                cmd = [
                    "pg_dump",
                    "-h",
                    url.host,
                    "-p",
                    str(url.port or 5432),
                    "-U",
                    url.username,
                    "-d",
                    url.database,
                    "-f",
                    str(backup_file),
                ]
                subprocess.run(cmd, check=True)
                self.logger.info(f"Backup created: {backup_file}")
                return backup_file

            else:
                self.logger.warning("Backup not supported for this database engine")
                return None

        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            return None

    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove backups older than keep_days"""
        cutoff = datetime.utcnow() - timedelta(days=keep_days)

        for backup_file in self.backup_dir.glob("backup_*"):
            if backup_file.stat().st_mtime < cutoff.timestamp():
                backup_file.unlink()
                self.logger.info(f"Deleted old backup: {backup_file}")


class QueryProfiler:
    """Profile and log slow queries"""

    def __init__(self, db, slow_query_threshold: float = 1.0):
        self.db = db
        self.slow_query_threshold = slow_query_threshold
        self.logger = logging.getLogger("slow_queries")
        self._setup_profiling()

    def _setup_profiling(self):
        """Setup query profiling"""
        from sqlalchemy import event

        @event.listens_for(self.db.engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            context._query_start_time = time.time()

        @event.listens_for(self.db.engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
            total = time.time() - context._query_start_time

            if total > self.slow_query_threshold:
                self.logger.warning(f"Slow query ({total:.2f}s): {statement[:200]}")


# Example usage
if __name__ == "__main__":
    import time

    # Initialize config
    config_mgr = ConfigManager()

    print("Configuration loaded:")
    print(f"Environment: {config_mgr.config.environment}")
    print(f"Database URI: {config_mgr.get_database_uri()}")
    print(f"Upload folder: {config_mgr.config.upload_folder}")
    print(f"Debug mode: {config_mgr.config.debug}")

    # SQLAlchemy config
    print("\nSQLAlchemy configuration:")
    for key, value in config_mgr.get_sqlalchemy_config().items():
        print(f"  {key}: {value}")

    print("\nConfiguration system ready!")


