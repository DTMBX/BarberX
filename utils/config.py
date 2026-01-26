"""
Production-grade configuration management
Removes hardcoded secrets and improves security
"""

import os
import secrets
from typing import Optional


class ConfigurationError(Exception):
    """Raised when required configuration is missing"""
    pass


class Config:
    """Base configuration with secure defaults"""
    
    # Required environment variables
    REQUIRED_ENV_VARS = ['SECRET_KEY', 'DATABASE_URL']
    
    def __init__(self):
        self._validate_required_env()
    
    def _validate_required_env(self):
        """Validates that all required environment variables are set"""
        missing = []
        for var in self.REQUIRED_ENV_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please set them in your .env file or environment."
            )
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')  # REQUIRED - no fallback
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No expiry for CSRF tokens
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # REQUIRED
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024 * 1024  # 20GB
    ALLOWED_EXTENSIONS = {
        'video': {'mp4', 'mov', 'avi', 'mkv', 'webm'},
        'document': {'pdf', 'doc', 'docx', 'txt'},
        'image': {'jpg', 'jpeg', 'png', 'gif', 'webp'},
        'audio': {'mp3', 'wav', 'ogg', 'm4a'}
    }
    
    # API Configuration
    API_VERSION = 'v1'
    API_TITLE = 'BarberX Legal Technologies API'
    API_DESCRIPTION = 'Professional BWC Forensic Analysis Platform'
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200/hour')
    
    # External Services
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # AWS S3 (optional - for production file storage)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
    AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'us-east-1')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # Feature Flags
    ENABLE_2FA = os.getenv('ENABLE_2FA', 'true').lower() == 'true'
    ENABLE_OCR = os.getenv('ENABLE_OCR', 'true').lower() == 'true'
    ENABLE_TRANSCRIPTION = os.getenv('ENABLE_TRANSCRIPTION', 'true').lower() == 'true'
    ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
    
    @classmethod
    def check_optional_features(cls) -> dict:
        """Check which optional features are configured"""
        return {
            'openai': bool(cls.OPENAI_API_KEY),
            'stripe': bool(cls.STRIPE_SECRET_KEY),
            'aws_s3': bool(cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY),
            '2fa': cls.ENABLE_2FA,
            'ocr': cls.ENABLE_OCR,
            'transcription': cls.ENABLE_TRANSCRIPTION,
            'ai_analysis': cls.ENABLE_AI_ANALYSIS
        }


class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Override security for local development
    SESSION_COOKIE_SECURE = False
    
    # Development database default
    if not os.getenv('DATABASE_URL'):
        # Only in development, allow SQLite fallback
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/barberx_dev.db'
        Config.REQUIRED_ENV_VARS = ['SECRET_KEY']  # SECRET_KEY still required
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production requires all security settings
    # No fallbacks allowed
    
    # Production logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Enforce HTTPS
    SESSION_COOKIE_SECURE = True
    
    # Stricter session timeout
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour


class TestingConfig(Config):
    """Testing environment configuration"""
    
    DEBUG = False
    TESTING = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    Config.REQUIRED_ENV_VARS = []  # No env vars required for tests
    
    # Generate test secret key
    SECRET_KEY = secrets.token_hex(32)
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False


def get_config(env: Optional[str] = None) -> Config:
    """
    Get configuration for specified environment
    
    Args:
        env: Environment name ('development', 'production', 'testing')
             Defaults to FLASK_ENV environment variable
    
    Returns:
        Configuration object
    
    Raises:
        ConfigurationError: If required environment variables are missing
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'production')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = configs.get(env.lower(), ProductionConfig)
    
    try:
        return config_class()
    except ConfigurationError as e:
        # In production, fail fast if config is wrong
        if env.lower() == 'production':
            raise
        
        # In development, show helpful error
        print(f"\n{'='*60}")
        print(f"CONFIGURATION ERROR")
        print(f"{'='*60}")
        print(str(e))
        print(f"\nCreate a .env file with:")
        print(f"SECRET_KEY={secrets.token_hex(32)}")
        print(f"DATABASE_URL=sqlite:///instance/barberx_dev.db")
        print(f"{'='*60}\n")
        raise


def create_env_template():
    """Creates a .env.example file with all configuration options"""
    
    template = f"""# BarberX Legal Technologies - Environment Configuration
# Copy this file to .env and fill in your values

# ===== REQUIRED =====
SECRET_KEY={secrets.token_hex(32)}
DATABASE_URL=postgresql://user:password@localhost/barberx

# ===== FLASK =====
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# ===== FILE UPLOADS =====
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=21474836480

# ===== RATE LIMITING =====
RATELIMIT_ENABLED=true
REDIS_URL=redis://localhost:6379/0
RATELIMIT_DEFAULT=200/hour

# ===== EXTERNAL SERVICES =====
# OpenAI (for AI analysis)
OPENAI_API_KEY=sk-...

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=barberx-evidence
AWS_S3_REGION=us-east-1

# ===== FEATURE FLAGS =====
ENABLE_2FA=true
ENABLE_OCR=true
ENABLE_TRANSCRIPTION=true
ENABLE_AI_ANALYSIS=true

# ===== SESSION =====
SESSION_COOKIE_SECURE=true
PERMANENT_SESSION_LIFETIME=3600
"""
    
    with open('.env.example', 'w') as f:
        f.write(template)
    
    print("Created .env.example file")


if __name__ == '__main__':
    # When run directly, create .env.example
    create_env_template()
