"""
Evident Authentication Models
User management, roles, tokens, and audit logging
"""

from datetime import datetime, timedelta
from enum import Enum
import secrets
from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserRole(Enum):
    """User role hierarchy"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    PRO_USER = "pro_user"
    USER = "user"


class TierLevel(Enum):
    """Subscription tier levels"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class User(UserMixin, db.Model):
    """User account model with authentication and profile"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=True)
    
    # Security
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Roles and tiers
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    tier = db.Column(db.Enum(TierLevel), default=TierLevel.FREE, nullable=False)
    
    # Profile
    avatar_url = db.Column(db.String(512), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    
    # Settings
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    
    # Relationships
    tokens = db.relationship('ApiToken', back_populates='user', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='user', cascade='all, delete-orphan')
    usage_records = db.relationship('UsageRecord', back_populates='user', cascade='all, delete-orphan')

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        """Check if user is admin or moderator"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]

    @property
    def is_pro(self):
        """Check if user has pro tier or higher"""
        return self.tier in [TierLevel.PRO, TierLevel.ENTERPRISE, TierLevel.ADMIN]

    def set_password(self, password):
        """Hash and store password"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def get_tier_limits(self):
        """Get feature limits for current tier"""
        limits = {
            'free': {
                'api_calls_per_month': 1000,
                'storage_gb': 1,
                'concurrent_uploads': 1,
                'batch_processing': False,
                'custom_models': False,
            },
            'pro': {
                'api_calls_per_month': 100000,
                'storage_gb': 100,
                'concurrent_uploads': 5,
                'batch_processing': True,
                'custom_models': False,
            },
            'enterprise': {
                'api_calls_per_month': None,  # Unlimited
                'storage_gb': None,  # Unlimited
                'concurrent_uploads': None,  # Unlimited
                'batch_processing': True,
                'custom_models': True,
            },
            'admin': {
                'api_calls_per_month': None,
                'storage_gb': None,
                'concurrent_uploads': None,
                'batch_processing': True,
                'custom_models': True,
            }
        }
        return limits.get(self.tier.value, limits['free'])

    def update_last_login(self, ip_address=None):
        """Track user login"""
        self.last_login = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
        db.session.commit()

    def log_action(self, action, details=None, ip_address=None):
        """Create audit log entry"""
        log = AuditLog(
            user_id=self.id,
            action=action,
            details=details or {},
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
        return log

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'organization': self.organization,
            'role': self.role.value,
            'tier': self.tier.value,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        if include_sensitive:
            data['email'] = self.email
            data['last_login_ip'] = self.last_login_ip
        return data

    def __repr__(self):
        return f'<User {self.email}>'


class ApiToken(db.Model):
    """API tokens for programmatic access"""
    __tablename__ = 'api_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='tokens')
    
    is_active = db.Column(db.Boolean, default=True)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    @staticmethod
    def generate_token():
        """Generate secure random token"""
        return secrets.token_urlsafe(32)

    def is_valid(self):
        """Check if token is valid and not expired"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

    def record_usage(self):
        """Update last used timestamp"""
        self.last_used_at = datetime.utcnow()
        db.session.commit()


class AuditLog(db.Model):
    """User action audit trail"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='audit_logs')
    
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(100), nullable=True)
    resource_id = db.Column(db.String(100), nullable=True)
    
    details = db.Column(db.JSON, default={})
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    
    status = db.Column(db.String(20), default='success')  # 'success', 'failure', 'warning'
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    @staticmethod
    def log_failed_login(email: str, ip_address: str = None):
        """Log a failed login attempt without requiring a valid user."""
        from flask import request
        log = AuditLog(
            user_id=0,  # System/anonymous event
            action='login_failed',
            resource_type='auth',
            details={'email': email, 'reason': 'invalid_credentials'},
            ip_address=ip_address,
            user_agent=request.headers.get('User-Agent', '')[:512] if request else None,
            status='failure'
        )
        try:
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }


class UsageRecord(db.Model):
    """Track user API usage for billing"""
    __tablename__ = 'usage_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='usage_records')
    
    metric = db.Column(db.String(100), nullable=False)  # e.g., 'api_calls', 'storage_gb'
    quantity = db.Column(db.Float, default=0)
    
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    cost = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('usage_user_metric', 'user_id', 'metric'),
    )


def admin_required(f):
    """Decorator: Require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app, abort
        from flask_login import current_user, login_required
        
        if not current_user or not current_user.is_admin:
            current_app.logger.warning(f"Unauthorized admin access attempt by {current_user}")
            abort(403)
        
        current_user.log_action('admin_action', {'function': f.__name__})
        return f(*args, **kwargs)
    return decorated_function


def moderator_required(f):
    """Decorator: Require moderator role or higher"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import abort
        from flask_login import current_user
        
        if not current_user or not current_user.is_moderator:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def tier_required(tier):
    """Decorator: Require specific tier"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import abort
            from flask_login import current_user
            
            if not current_user:
                abort(401)
            
            tier_hierarchy = {
                TierLevel.FREE: 0,
                TierLevel.PRO: 1,
                TierLevel.ENTERPRISE: 2,
                TierLevel.ADMIN: 3,
            }
            
            if tier_hierarchy.get(current_user.tier, 0) < tier_hierarchy.get(tier, 0):
                abort(402)  # Payment required
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
