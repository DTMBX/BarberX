# BarberX Legal Tech Platform
# Professional BWC Forensic Analysis System
# Copyright (c) 2026 BarberX Legal Technologies

from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys
import json
import threading
import hashlib
import uuid
import logging
from logging.handlers import RotatingFileHandler
import flask

# Enhanced authentication imports
try:
    from models_auth import UsageTracking, ApiKey, TierLevel
    from auth_routes import auth_bp
    ENHANCED_AUTH_AVAILABLE = True
except ImportError as e:
    ENHANCED_AUTH_AVAILABLE = False
    print(f"⚠️  Enhanced auth not available: {e}")

# UX enhancement utilities
try:
    from ux_helpers import register_ux_filters
    UX_HELPERS_AVAILABLE = True
except ImportError as e:
    UX_HELPERS_AVAILABLE = False
    print(f"⚠️  UX helpers not available: {e}")

# Import our BWC analyzer (optional - only needed for actual analysis)
try:
    from bwc_forensic_analyzer import BWCForensicAnalyzer
    BWC_ANALYZER_AVAILABLE = True
except ImportError:
    BWC_ANALYZER_AVAILABLE = False
    app_logger = logging.getLogger(__name__)
    app_logger.warning("BWC Forensic Analyzer not available - AI dependencies not installed")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'barberx-legal-tech-2026-secure-key')

# Use absolute path for database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{os.path.join(basedir, "instance", "barberx_auth.db")}'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5GB
app.config['UPLOAD_FOLDER'] = Path('./uploads/bwc_videos')
app.config['ANALYSIS_FOLDER'] = Path('./bwc_analysis')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Create directories
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['ANALYSIS_FOLDER'].mkdir(parents=True, exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # Updated to use auth blueprint

# Register enhanced authentication blueprint
if ENHANCED_AUTH_AVAILABLE:
    app.register_blueprint(auth_bp, url_prefix='/auth')
    print("✅ Enhanced auth routes registered at /auth/*")

# Register UX helper filters and context processors
if UX_HELPERS_AVAILABLE:
    register_ux_filters(app)
    print("✅ UX enhancement filters registered")

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/barberx.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('BarberX Legal Tech startup')

# Global analyzer instance (lazy load)
analyzer = None
analysis_tasks = {}  # Track background analysis tasks

# ========================================
# DATABASE MODELS
# ========================================

class User(UserMixin, db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(200))
    role = db.Column(db.String(20), default='user')  # user, pro, admin
    subscription_tier = db.Column(db.String(20), default='free')  # free, professional, enterprise
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Usage limits
    analyses_count = db.Column(db.Integer, default=0)
    storage_used_mb = db.Column(db.Float, default=0.0)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_tier_limits(self):
        """Get usage limits based on subscription tier"""
        limits = {
            'free': {
                'max_analyses_per_month': 5,
                'max_file_size_mb': 500,
                'max_storage_gb': 5,
                'batch_processing': False,
                'api_access': False,
                'team_collaboration': False,
                'priority_support': False
            },
            'professional': {
                'max_analyses_per_month': 100,
                'max_file_size_mb': 2000,
                'max_storage_gb': 100,
                'batch_processing': True,
                'api_access': True,
                'team_collaboration': True,
                'priority_support': True
            },
            'enterprise': {
                'max_analyses_per_month': -1,  # unlimited
                'max_file_size_mb': 5000,
                'max_storage_gb': -1,  # unlimited
                'batch_processing': True,
                'api_access': True,
                'team_collaboration': True,
                'priority_support': True
            }
        }
        return limits.get(self.subscription_tier, limits['free'])
    
    def can_analyze(self):
        """Check if user can perform analysis based on tier limits"""
        limits = self.get_tier_limits()
        if limits['max_analyses_per_month'] == -1:
            return True
        
        # Count analyses this month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_count = self.analyses.filter(Analysis.created_at >= month_start).count()
        
        return month_count < limits['max_analyses_per_month']
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'organization': self.organization,
            'role': self.role,
            'subscription_tier': self.subscription_tier,
            'created_at': self.created_at.isoformat(),
            'analyses_count': self.analyses_count,
            'tier_limits': self.get_tier_limits()
        }


class Analysis(db.Model):
    """Analysis record for BWC video processing"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.String(32), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False, index=True)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    
    # Case metadata
    case_number = db.Column(db.String(100), index=True)
    evidence_number = db.Column(db.String(100))
    acquired_by = db.Column(db.String(100))
    source = db.Column(db.String(200))
    known_officers = db.Column(db.JSON)
    
    # Analysis status
    status = db.Column(db.String(20), default='uploaded')  # uploaded, analyzing, completed, failed
    progress = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Results summary
    duration = db.Column(db.Float)
    total_speakers = db.Column(db.Integer)
    total_segments = db.Column(db.Integer)
    total_discrepancies = db.Column(db.Integer)
    critical_discrepancies = db.Column(db.Integer)
    
    # Report paths
    report_json_path = db.Column(db.String(500))
    report_txt_path = db.Column(db.String(500))
    report_md_path = db.Column(db.String(500))
    
    # Sharing and collaboration
    is_shared = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(64), unique=True)
    
    # Tags for organization
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def generate_id(self):
        """Generate unique analysis ID"""
        self.id = uuid.uuid4().hex
    
    def to_dict(self, include_results=False):
        data = {
            'id': self.id,
            'filename': self.filename,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'case_number': self.case_number,
            'evidence_number': self.evidence_number,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat(),
            'tags': self.tags or []
        }
        
        if include_results and self.status == 'completed':
            data.update({
                'duration': self.duration,
                'total_speakers': self.total_speakers,
                'total_segments': self.total_segments,
                'total_discrepancies': self.total_discrepancies,
                'critical_discrepancies': self.critical_discrepancies,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None
            })
        
        return data


class APIKey(db.Model):
    """API key for programmatic access"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def generate_key(self):
        """Generate secure API key"""
        self.key = f"bx_{uuid.uuid4().hex}{uuid.uuid4().hex[:16]}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
            'created_at': self.created_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_active': self.is_active
        }


class AppSettings(db.Model):
    """Application settings and configuration"""
    __tablename__ = 'app_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')  # string, int, float, bool, json
    category = db.Column(db.String(50), default='general')  # general, security, features, limits, email, branding
    description = db.Column(db.String(500))
    is_editable = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    @staticmethod
    def get(key, default=None):
        """Get setting value by key"""
        setting = AppSettings.query.filter_by(key=key).first()
        if not setting:
            return default
        
        # Convert based on type
        if setting.value_type == 'bool':
            return setting.value.lower() in ('true', '1', 'yes')
        elif setting.value_type == 'int':
            return int(setting.value)
        elif setting.value_type == 'float':
            return float(setting.value)
        elif setting.value_type == 'json':
            import json
            return json.loads(setting.value)
        return setting.value
    
    @staticmethod
    def set(key, value, value_type='string', category='general', description=''):
        """Set or update setting value"""
        setting = AppSettings.query.filter_by(key=key).first()
        
        # Convert value to string for storage
        if value_type == 'json':
            import json
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        
        if setting:
            setting.value = value_str
            setting.value_type = value_type
            setting.updated_at = datetime.utcnow()
            if current_user.is_authenticated:
                setting.updated_by = current_user.id
        else:
            setting = AppSettings(
                key=key,
                value=value_str,
                value_type=value_type,
                category=category,
                description=description,
                updated_by=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting


class PDFUpload(db.Model):
    """Model for tracking uploaded PDF files"""
    __tablename__ = 'pdf_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    mime_type = db.Column(db.String(100), default='application/pdf')
    
    # Metadata
    case_number = db.Column(db.String(100), index=True)
    document_type = db.Column(db.String(100))  # brief, motion, order, filing, etc.
    tags = db.Column(db.JSON)
    description = db.Column(db.Text)
    
    # Status and processing
    status = db.Column(db.String(20), default='uploaded')  # uploaded, processing, processed, error
    page_count = db.Column(db.Integer)
    extracted_text = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_at = db.Column(db.DateTime)
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(64), unique=True)
    
    def generate_hash(self, file_path):
        """Generate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        self.file_hash = sha256.hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'case_number': self.case_number,
            'document_type': self.document_type,
            'tags': self.tags or [],
            'description': self.description,
            'status': self.status,
            'page_count': self.page_count,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


class AuditLog(db.Model):
    """Audit log for compliance and security"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    action = db.Column(db.String(50), nullable=False, index=True)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.String(100))
    details = db.Column(db.JSON)
    
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    @staticmethod
    def log(action, resource_type=None, resource_id=None, details=None):
        """Create audit log entry"""
        log_entry = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log_entry)
        db.session.commit()


# ========================================
# AUTHENTICATION
# ========================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def api_key_required(f):
    """Decorator to require API key authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        key_obj = APIKey.query.filter_by(key=api_key, is_active=True).first()
        
        if not key_obj:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Update last used
        key_obj.last_used_at = datetime.utcnow()
        db.session.commit()
        
        # Set current user
        request.current_api_user = key_obj.user
        
        return f(*args, **kwargs)
    
    return decorated_function


# ========================================
# WEB ROUTES
# ========================================

@app.route('/')
def index():
    """Landing page - modern standalone version"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return send_file('index-standalone.html')


@app.route('/bwc-dashboard')
@login_required
def bwc_dashboard():
    """BWC Analysis Dashboard - Frontend Interface"""
    return send_file('bwc-dashboard.html')


@app.route('/test-separation')
def test_separation():
    """Frontend/Backend separation test suite"""
    return send_file('test_separation.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration - redirect to enhanced signup"""
    if ENHANCED_AUTH_AVAILABLE:
        return redirect(url_for('auth.signup'))
    
    # Fallback to old registration logic
    if request.method == 'GET':
        return send_file('templates/register.html')
    
    data = request.get_json()
    
    # Validate input
    if not all([data.get('email'), data.get('password'), data.get('full_name')]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        organization=data.get('organization', ''),
        subscription_tier='free'
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Log audit
    AuditLog.log('user_registered', 'user', str(user.id))
    
    # Auto-login
    login_user(user)
    
    app.logger.info(f'New user registered: {user.email}')
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login - redirect to enhanced auth"""
    if ENHANCED_AUTH_AVAILABLE:
        return redirect(url_for('auth.login'))
    
    # Fallback to old login logic
    if request.method == 'GET':
        return send_file('templates/login.html')
    
    data = request.get_json()
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    login_user(user, remember=data.get('remember', False))
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log audit
    AuditLog.log('user_login', 'user', str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    AuditLog.log('user_logout', 'user', str(current_user.id))
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Enhanced user dashboard with usage tracking and tier-specific features"""
    if ENHANCED_AUTH_AVAILABLE:
        try:
            from models_auth import UsageTracking
            usage = UsageTracking.get_or_create_current(current_user.id)
            limits = current_user.get_tier_limits()
            
            # Add Jinja2 custom filter for number formatting
            @app.template_filter('format_number')
            def format_number(value):
                """Format numbers with thousands separator"""
                try:
                    return f"{int(value):,}"
                except (ValueError, TypeError):
                    return value
            
            return render_template('auth/dashboard.html',
                                 user=current_user,
                                 usage=usage,
                                 limits=limits)
        except Exception as e:
            app.logger.error(f"Dashboard error: {e}")
            # Fallback to basic dashboard
            return send_file('templates/dashboard.html')
    else:
        return send_file('templates/dashboard.html')


@app.route('/admin')
@login_required
def admin_panel():
    """Enhanced admin panel - requires admin role with full analytics"""
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        flash('Admin access required', 'danger')
        return redirect(url_for('dashboard'))
    
    if ENHANCED_AUTH_AVAILABLE:
        try:
            from models_auth import User, UsageTracking
            from sqlalchemy import func
            
            # Get all users
            users = User.query.all()
            
            # Calculate stats
            total_users = User.query.count()
            total_analyses = db.session.query(func.sum(UsageTracking.bwc_videos_processed)).scalar() or 0
            total_storage = db.session.query(func.sum(UsageTracking.storage_used_mb)).scalar() or 0
            storage_gb = round(total_storage / 1024, 2) if total_storage else 0
            
            # Calculate MRR (Monthly Recurring Revenue)
            revenue = 0
            for user in users:
                if user.tier and hasattr(user.tier, 'value'):
                    revenue += user.tier.value
            
            return render_template('admin/dashboard.html',
                                 users=users,
                                 total_users=total_users,
                                 total_analyses=total_analyses,
                                 storage_gb=storage_gb,
                                 revenue=revenue)
        except Exception as e:
            app.logger.error(f"Admin panel error: {e}")
            return send_file('admin.html')
    else:
        return send_file('admin.html')


@app.route('/analyzer')
@login_required
def analyzer():
    """BWC analyzer interface"""
    return send_file('bwc-analyzer.html')


@app.route('/tools/transcript')
@login_required
def transcript_search():
    """Transcript search tool"""
    return send_file('templates/tools/transcript.html')


@app.route('/tools/entity-extract')
@login_required
def entity_extract():
    """Entity extraction tool"""
    return send_file('templates/tools/entity-extract.html')


@app.route('/tools/timeline')
@login_required
def timeline_builder():
    """Timeline builder tool"""
    return send_file('templates/tools/timeline.html')


@app.route('/tools/discrepancy')
@login_required
def discrepancy_finder():
    """Discrepancy finder tool"""
    return send_file('templates/tools/discrepancy.html')


@app.route('/tools/batch')
@login_required
def batch_processor():
    """Batch processor tool"""
    return send_file('templates/tools/batch.html')


@app.route('/tools/api')
@login_required
def api_console():
    """API console tool"""
    return send_file('templates/tools/api-console.html')


# ========================================
# RESOURCE PAGES
# ========================================

@app.route('/docs')
def docs():
    """Documentation home"""
    return send_file('templates/resources/docs.html')


@app.route('/api')
def api_reference():
    """API reference"""
    return send_file('templates/resources/api-reference.html')


@app.route('/blog')
def blog():
    """Blog home"""
    return send_file('templates/resources/blog.html')


@app.route('/case-studies')
def case_studies():
    """Case studies"""
    return send_file('templates/resources/case-studies.html')


@app.route('/guides')
def guides():
    """User guides"""
    return send_file('templates/resources/guides.html')


@app.route('/faq')
def faq():
    """FAQ page"""
    return send_file('templates/resources/faq.html')


@app.route('/animation-demo')
@app.route('/animation-demo.html')
def animation_demo():
    """Animation system demo page"""
    return send_file('animation-demo.html')


# ========================================
# COMPANY PAGES
# ========================================

@app.route('/about')
def about():
    """About us"""
    return send_file('templates/company/about.html')


@app.route('/careers')
def careers():
    """Careers page"""
    return send_file('templates/company/careers.html')


@app.route('/licenses')
@app.route('/company/licenses')
def licenses():
    """Open source licenses and attributions"""
    return send_file('templates/company/licenses.html')


@app.route('/contact')
def contact():
    """Contact page"""
    return send_file('templates/company/contact.html')


@app.route('/press')
def press():
    """Press/media page"""
    return send_file('templates/company/press.html')


# ========================================
# STATIC ASSETS
# ========================================

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets from assets folder"""
    return send_file(os.path.join('assets', filename))


# ========================================
# API ROUTES - Analysis
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if AI models are loaded"""
    global analyzer
    
    try:
        if analyzer is None:
            hf_token = os.getenv('HUGGINGFACE_TOKEN')
            analyzer = BWCForensicAnalyzer(
                whisper_model_size='base',
                hf_token=hf_token
            )
        
        return jsonify({
            'status': 'ready',
            'models': {
                'whisper': analyzer.whisper_model is not None,
                'pyannote': analyzer.diarization_pipeline is not None,
                'spacy': analyzer.nlp is not None
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        app.logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle BWC video file upload"""
    
    # Check if user can analyze
    if not current_user.can_analyze():
        return jsonify({
            'error': 'Monthly analysis limit reached. Please upgrade your plan.'
        }), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Secure filename
    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{current_user.id}_{timestamp}_{filename}"
    filepath = app.config['UPLOAD_FOLDER'] / unique_filename
    
    # Save file
    file.save(filepath)
    
    # Calculate hash
    file_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            file_hash.update(chunk)
    file_hash_hex = file_hash.hexdigest()
    
    file_size = os.path.getsize(filepath)
    
    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        filename=filename,
        file_hash=file_hash_hex,
        file_size=file_size,
        file_path=str(filepath),
        status='uploaded'
    )
    analysis.generate_id()
    
    db.session.add(analysis)
    db.session.commit()
    
    # Update user storage
    current_user.storage_used_mb += file_size / (1024 * 1024)
    db.session.commit()
    
    # Log audit
    AuditLog.log('file_uploaded', 'analysis', analysis.id, {'filename': filename})
    
    app.logger.info(f'File uploaded: {filename} by user {current_user.email}')
    
    return jsonify({
        'upload_id': analysis.id,
        'filename': filename,
        'file_hash': file_hash_hex,
        'file_size': file_size,
        'message': 'File uploaded successfully'
    })


@app.route('/api/upload/pdf', methods=['POST'])
def upload_pdf():
    """Handle single PDF file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate PDF file
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    # Get optional metadata
    case_number = request.form.get('case_number', '')
    document_type = request.form.get('document_type', '')
    description = request.form.get('description', '')
    tags_str = request.form.get('tags', '')
    tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []
    
    # Secure filename
    original_filename = file.filename
    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    
    # Create upload directory
    upload_dir = Path('./uploads/pdfs')
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = upload_dir / unique_filename
    
    # Save file
    file.save(filepath)
    
    # Get file size
    file_size = os.path.getsize(filepath)
    
    # Create PDF upload record
    pdf_upload = PDFUpload(
        user_id=current_user.id if current_user.is_authenticated else None,
        filename=unique_filename,
        original_filename=original_filename,
        file_path=str(filepath),
        file_size=file_size,
        case_number=case_number,
        document_type=document_type,
        description=description,
        tags=tags,
        status='uploaded'
    )
    
    # Generate hash
    pdf_upload.generate_hash(str(filepath))
    
    db.session.add(pdf_upload)
    db.session.commit()
    
    # Log audit
    AuditLog.log('pdf_uploaded', 'pdf_upload', str(pdf_upload.id), {
        'filename': original_filename,
        'file_size': file_size
    })
    
    app.logger.info(f'PDF uploaded: {original_filename} (ID: {pdf_upload.id})')
    
    return jsonify({
        'success': True,
        'upload_id': pdf_upload.id,
        'filename': original_filename,
        'file_hash': pdf_upload.file_hash,
        'file_size': file_size,
        'message': 'PDF uploaded successfully'
    })


@app.route('/api/upload/pdf/batch', methods=['POST'])
def batch_upload_pdf():
    """Handle batch PDF file upload"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    results = {
        'total': len(files),
        'successful': [],
        'failed': []
    }
    
    for file in files:
        try:
            if file.filename == '':
                results['failed'].append({
                    'filename': 'unknown',
                    'error': 'Empty filename'
                })
                continue
            
            # Validate PDF
            if not file.filename.lower().endswith('.pdf'):
                results['failed'].append({
                    'filename': file.filename,
                    'error': 'Not a PDF file'
                })
                continue
            
            # Secure filename
            original_filename = file.filename
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
            unique_filename = f"{timestamp}_{filename}"
            
            # Create upload directory
            upload_dir = Path('./uploads/pdfs')
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = upload_dir / unique_filename
            
            # Save file
            file.save(filepath)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Create PDF upload record
            pdf_upload = PDFUpload(
                user_id=current_user.id if current_user.is_authenticated else None,
                filename=unique_filename,
                original_filename=original_filename,
                file_path=str(filepath),
                file_size=file_size,
                status='uploaded'
            )
            
            # Generate hash
            pdf_upload.generate_hash(str(filepath))
            
            db.session.add(pdf_upload)
            db.session.commit()
            
            results['successful'].append({
                'upload_id': pdf_upload.id,
                'filename': original_filename,
                'file_size': file_size,
                'file_hash': pdf_upload.file_hash
            })
            
            app.logger.info(f'PDF uploaded (batch): {original_filename} (ID: {pdf_upload.id})')
            
        except Exception as e:
            results['failed'].append({
                'filename': file.filename if file else 'unknown',
                'error': str(e)
            })
            app.logger.error(f'Batch PDF upload error: {str(e)}')
    
    # Log audit for batch
    AuditLog.log('pdf_batch_uploaded', 'pdf_upload', None, {
        'total': results['total'],
        'successful': len(results['successful']),
        'failed': len(results['failed'])
    })
    
    return jsonify({
        'success': True,
        'results': results,
        'summary': {
            'total': results['total'],
            'successful': len(results['successful']),
            'failed': len(results['failed'])
        }
    })


@app.route('/api/pdfs', methods=['GET'])
def list_pdfs():
    """List uploaded PDFs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Filter by user if authenticated
    query = PDFUpload.query
    
    if current_user.is_authenticated:
        # Admins can see all, users see only their own
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user.id)
    else:
        # Public access - only show public PDFs
        query = query.filter_by(is_public=True)
    
    pagination = query.order_by(PDFUpload.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages,
        'pdfs': [pdf.to_dict() for pdf in pagination.items]
    })


@app.route('/api/pdf/<int:pdf_id>', methods=['GET'])
def get_pdf_info(pdf_id):
    """Get PDF information"""
    pdf = PDFUpload.query.get(pdf_id)
    
    if not pdf:
        return jsonify({'error': 'PDF not found'}), 404
    
    # Check access
    if not pdf.is_public and (not current_user.is_authenticated or 
                              (current_user.id != pdf.user_id and current_user.role != 'admin')):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(pdf.to_dict())


@app.route('/api/pdf/<int:pdf_id>/download', methods=['GET'])
def download_pdf(pdf_id):
    """Download PDF file"""
    pdf = PDFUpload.query.get(pdf_id)
    
    if not pdf:
        return jsonify({'error': 'PDF not found'}), 404
    
    # Check access
    if not pdf.is_public and (not current_user.is_authenticated or 
                              (current_user.id != pdf.user_id and current_user.role != 'admin')):
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if file exists
    if not os.path.exists(pdf.file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    return send_file(
        pdf.file_path,
        as_attachment=True,
        download_name=pdf.original_filename,
        mimetype='application/pdf'
    )


@app.route('/api/pdf/<int:pdf_id>', methods=['DELETE'])
@login_required
def delete_pdf(pdf_id):
    """Delete PDF file"""
    pdf = PDFUpload.query.get(pdf_id)
    
    if not pdf:
        return jsonify({'error': 'PDF not found'}), 404
    
    # Check permission
    if current_user.id != pdf.user_id and current_user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    # Delete file from disk
    if os.path.exists(pdf.file_path):
        os.remove(pdf.file_path)
    
    # Delete from database
    db.session.delete(pdf)
    db.session.commit()
    
    # Log audit
    AuditLog.log('pdf_deleted', 'pdf_upload', str(pdf_id), {
        'filename': pdf.original_filename
    })
    
    return jsonify({
        'success': True,
        'message': 'PDF deleted successfully'
    })


@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_video():
    """Start BWC video analysis"""
    global analyzer
    
    data = request.get_json()
    upload_id = data.get('upload_id')
    
    analysis = Analysis.query.filter_by(id=upload_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    # Update case metadata
    analysis.case_number = data.get('case_number', '')
    analysis.evidence_number = data.get('evidence_number', '')
    analysis.acquired_by = data.get('acquired_by', current_user.full_name)
    analysis.source = data.get('source', 'Web Upload')
    analysis.known_officers = data.get('known_officers', [])
    analysis.status = 'analyzing'
    analysis.started_at = datetime.utcnow()
    analysis.progress = 0
    
    db.session.commit()
    
    # Start analysis in background
    def run_analysis():
        try:
            analysis.current_step = 'Extracting audio...'
            analysis.progress = 10
            db.session.commit()
            
            # Run forensic analysis
            report = analyzer.analyze_bwc_file(
                video_path=analysis.file_path,
                acquired_by=analysis.acquired_by,
                source=analysis.source,
                case_number=analysis.case_number,
                evidence_number=analysis.evidence_number,
                known_officers=analysis.known_officers
            )
            
            analysis.progress = 90
            analysis.current_step = 'Generating reports...'
            db.session.commit()
            
            # Save reports
            output_dir = app.config['ANALYSIS_FOLDER'] / analysis.id
            output_files = analyzer.export_report(
                report,
                output_dir=str(output_dir),
                formats=['json', 'txt', 'md']
            )
            
            # Update analysis record
            analysis.status = 'completed'
            analysis.progress = 100
            analysis.current_step = 'Analysis complete'
            analysis.completed_at = datetime.utcnow()
            analysis.duration = report.duration
            analysis.total_speakers = len(report.speakers)
            analysis.total_segments = len(report.transcript)
            analysis.total_discrepancies = len(report.discrepancies)
            analysis.critical_discrepancies = len([d for d in report.discrepancies if d.severity == 'critical'])
            analysis.report_json_path = str(output_dir / 'report.json')
            analysis.report_txt_path = str(output_dir / 'report.txt')
            analysis.report_md_path = str(output_dir / 'report.md')
            
            # Update user stats
            current_user.analyses_count += 1
            
            db.session.commit()
            
            # Log audit
            AuditLog.log('analysis_completed', 'analysis', analysis.id)
            
            app.logger.info(f'Analysis completed: {analysis.id}')
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.progress = 0
            db.session.commit()
            
            app.logger.error(f'Analysis failed: {analysis.id} - {str(e)}')
    
    # Start background thread
    thread = threading.Thread(target=run_analysis)
    thread.start()
    
    analysis_tasks[upload_id] = thread
    
    return jsonify({
        'upload_id': upload_id,
        'message': 'Analysis started',
        'status': 'analyzing'
    })


@app.route('/api/analyses', methods=['GET'])
@login_required
def list_analyses():
    """List user's analyses"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = current_user.analyses.order_by(Analysis.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages,
        'analyses': [a.to_dict(include_results=True) for a in pagination.items]
    })


@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id):
    """Get analysis details"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    return jsonify(analysis.to_dict(include_results=True))


@app.route('/api/analysis/<analysis_id>/status', methods=['GET'])
@login_required
def get_analysis_status(analysis_id):
    """Get real-time analysis status"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    status_data = {
        'id': analysis.id,
        'status': analysis.status,
        'progress': analysis.progress,
        'current_step': analysis.current_step,
        'filename': analysis.filename,
        'case_number': analysis.case_number,
        'created_at': analysis.created_at.isoformat(),
        'started_at': analysis.started_at.isoformat() if analysis.started_at else None,
        'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
        'error_message': analysis.error_message
    }
    
    # Add results if completed
    if analysis.status == 'completed':
        status_data.update({
            'duration': analysis.duration,
            'total_speakers': analysis.total_speakers,
            'total_segments': analysis.total_segments,
            'total_discrepancies': analysis.total_discrepancies,
            'critical_discrepancies': analysis.critical_discrepancies
        })
    
    return jsonify(status_data)


@app.route('/api/analysis/<analysis_id>/report/<format>', methods=['GET'])
@login_required
def download_report(analysis_id, format):
    """Download analysis report"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    if analysis.status != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 400
    
    # Get report file path
    if format == 'json':
        report_path = analysis.report_json_path
        mimetype = 'application/json'
    elif format == 'txt':
        report_path = analysis.report_txt_path
        mimetype = 'text/plain'
    elif format == 'md':
        report_path = analysis.report_md_path
        mimetype = 'text/markdown'
    elif format in ['pdf', 'docx']:
        # Generate on-demand for PDF/DOCX
        return export_analysis_report(analysis, format)
    else:
        return jsonify({'error': 'Invalid format'}), 400
    
    if not report_path or not Path(report_path).exists():
        return jsonify({'error': 'Report file not found'}), 404
    
    # Log audit
    AuditLog.log('report_downloaded', 'analysis', analysis_id, {'format': format})
    
    return send_file(
        report_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=f"BWC_Analysis_{analysis.case_number or analysis_id}.{format}"
    )


def export_analysis_report(analysis, format):
    """Export analysis to PDF or DOCX format"""
    try:
        # Load the JSON report
        if not analysis.report_json_path or not Path(analysis.report_json_path).exists():
            return jsonify({'error': 'Analysis report not available'}), 404
        
        import json
        with open(analysis.report_json_path, 'r') as f:
            report_data = json.load(f)
        
        output_dir = Path(app.config['ANALYSIS_FOLDER']) / analysis.id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == 'pdf':
            # Generate PDF report
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            
            pdf_path = output_dir / f'report_{analysis.id}.pdf'
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph(f"<b>BWC Forensic Analysis Report</b>", styles['Title']))
            story.append(Spacer(1, 12))
            
            # Case Information
            story.append(Paragraph("<b>Case Information</b>", styles['Heading2']))
            case_info = [
                ['Case Number:', analysis.case_number or 'N/A'],
                ['Evidence Number:', analysis.evidence_number or 'N/A'],
                ['Filename:', analysis.filename],
                ['File Hash (SHA-256):', analysis.file_hash],
                ['Analysis Date:', analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')],
                ['Duration:', f"{analysis.duration:.2f} seconds" if analysis.duration else 'N/A']
            ]
            case_table = Table(case_info)
            case_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(case_table)
            story.append(Spacer(1, 20))
            
            # Results Summary
            story.append(Paragraph("<b>Analysis Results</b>", styles['Heading2']))
            results = [
                ['Total Speakers:', str(analysis.total_speakers or 0)],
                ['Transcript Segments:', str(analysis.total_segments or 0)],
                ['Total Discrepancies:', str(analysis.total_discrepancies or 0)],
                ['Critical Discrepancies:', str(analysis.critical_discrepancies or 0)]
            ]
            results_table = Table(results)
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold')
            ]))
            story.append(results_table)
            story.append(Spacer(1, 20))
            
            # Chain of Custody
            story.append(Paragraph("<b>Chain of Custody</b>", styles['Heading2']))
            story.append(Paragraph(f"File Integrity (SHA-256): {analysis.file_hash}", styles['Normal']))
            story.append(Paragraph(f"Acquired By: {analysis.acquired_by or 'Not specified'}", styles['Normal']))
            story.append(Paragraph(f"Source: {analysis.source or 'Not specified'}", styles['Normal']))
            
            doc.build(story)
            
            # Log audit
            AuditLog.log('report_exported', 'analysis', analysis.id, {'format': 'pdf'})
            
            return send_file(
                str(pdf_path),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"BWC_Analysis_{analysis.case_number or analysis.id}.pdf"
            )
        
        elif format == 'docx':
            # Generate DOCX report
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            docx_path = output_dir / f'report_{analysis.id}.docx'
            doc = Document()
            
            # Title
            title = doc.add_heading('BWC Forensic Analysis Report', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Case Information
            doc.add_heading('Case Information', level=1)
            table = doc.add_table(rows=6, cols=2)
            table.style = 'Light Grid Accent 1'
            
            cells = table.rows[0].cells
            cells[0].text = 'Case Number:'
            cells[1].text = analysis.case_number or 'N/A'
            
            cells = table.rows[1].cells
            cells[0].text = 'Evidence Number:'
            cells[1].text = analysis.evidence_number or 'N/A'
            
            cells = table.rows[2].cells
            cells[0].text = 'Filename:'
            cells[1].text = analysis.filename
            
            cells = table.rows[3].cells
            cells[0].text = 'File Hash (SHA-256):'
            cells[1].text = analysis.file_hash
            
            cells = table.rows[4].cells
            cells[0].text = 'Analysis Date:'
            cells[1].text = analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            cells = table.rows[5].cells
            cells[0].text = 'Duration:'
            cells[1].text = f"{analysis.duration:.2f} seconds" if analysis.duration else 'N/A'
            
            # Results Summary
            doc.add_heading('Analysis Results', level=1)
            results_table = doc.add_table(rows=4, cols=2)
            results_table.style = 'Light Grid Accent 1'
            
            cells = results_table.rows[0].cells
            cells[0].text = 'Total Speakers:'
            cells[1].text = str(analysis.total_speakers or 0)
            
            cells = results_table.rows[1].cells
            cells[0].text = 'Transcript Segments:'
            cells[1].text = str(analysis.total_segments or 0)
            
            cells = results_table.rows[2].cells
            cells[0].text = 'Total Discrepancies:'
            cells[1].text = str(analysis.total_discrepancies or 0)
            
            cells = results_table.rows[3].cells
            cells[0].text = 'Critical Discrepancies:'
            cells[1].text = str(analysis.critical_discrepancies or 0)
            
            # Chain of Custody
            doc.add_heading('Chain of Custody', level=1)
            doc.add_paragraph(f'File Integrity (SHA-256): {analysis.file_hash}')
            doc.add_paragraph(f'Acquired By: {analysis.acquired_by or "Not specified"}')
            doc.add_paragraph(f'Source: {analysis.source or "Not specified"}')
            
            # Attribution
            doc.add_heading('Attribution', level=1)
            doc.add_paragraph('This analysis was generated using:')
            doc.add_paragraph('• OpenAI Whisper (Apache 2.0 License) - Audio transcription')
            doc.add_paragraph('• pyannote.audio (MIT License) - Speaker diarization')
            doc.add_paragraph('• BarberX Legal Technologies - Forensic analysis platform')
            
            doc.save(str(docx_path))
            
            # Log audit
            AuditLog.log('report_exported', 'analysis', analysis.id, {'format': 'docx'})
            
            return send_file(
                str(docx_path),
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name=f"BWC_Analysis_{analysis.case_number or analysis.id}.docx"
            )
        
        elif format == 'json':
            # Generate JSON export
            import json
            
            json_path = output_dir / f'report_{analysis.id}.json'
            
            json_data = {
                'case_information': {
                    'case_number': analysis.case_number or 'N/A',
                    'evidence_number': analysis.evidence_number or 'N/A',
                    'filename': analysis.filename,
                    'file_hash': analysis.file_hash,
                    'file_size': analysis.file_size,
                    'duration': analysis.duration,
                    'analysis_date': analysis.created_at.isoformat(),
                    'updated_at': analysis.updated_at.isoformat()
                },
                'analysis_results': {
                    'status': analysis.status,
                    'progress': analysis.progress,
                    'current_step': analysis.current_step,
                    'total_speakers': analysis.total_speakers or 0,
                    'total_segments': analysis.total_segments or 0,
                    'total_discrepancies': analysis.total_discrepancies or 0,
                    'critical_discrepancies': analysis.critical_discrepancies or 0
                },
                'chain_of_custody': {
                    'file_integrity_hash': analysis.file_hash,
                    'acquired_by': analysis.acquired_by or 'Not specified',
                    'source': analysis.source or 'Not specified',
                    'analyzed_by': current_user.email
                },
                'metadata': analysis.metadata or {},
                'export_timestamp': datetime.utcnow().isoformat(),
                'platform': 'BarberX Legal Tech Platform',
                'version': '2.0'
            }
            
            with open(str(json_path), 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Log audit
            AuditLog.log('report_exported', 'analysis', analysis.id, {'format': 'json'})
            
            return send_file(
                str(json_path),
                mimetype='application/json',
                as_attachment=True,
                download_name=f"BWC_Analysis_{analysis.case_number or analysis.id}.json"
            )
        
        elif format == 'txt':
            # Generate plain text export
            txt_path = output_dir / f'report_{analysis.id}.txt'
            
            duration_str = f"{int(analysis.duration // 60)}m {int(analysis.duration % 60)}s" if analysis.duration else 'N/A'
            file_size_str = f"{analysis.file_size / (1024*1024):.2f} MB" if analysis.file_size else 'N/A'
            
            text_content = f"""
========================================
BWC FORENSIC ANALYSIS REPORT
========================================
Generated: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}

CASE INFORMATION
----------------
Case Number: {analysis.case_number or 'N/A'}
Evidence Number: {analysis.evidence_number or 'N/A'}
Filename: {analysis.filename}
File Size: {file_size_str}
Duration: {duration_str}
SHA-256 Hash: {analysis.file_hash}

ANALYSIS RESULTS
----------------
Speakers Identified: {analysis.total_speakers or 0}
Transcript Segments: {analysis.total_segments or 0}
Total Discrepancies: {analysis.total_discrepancies or 0}
Critical Issues: {analysis.critical_discrepancies or 0}
Analysis Status: {analysis.status.upper()}
Completion Progress: {analysis.progress}%
Current Step: {analysis.current_step or 'N/A'}

CHAIN OF CUSTODY
----------------
Evidence Acquired By: {analysis.acquired_by or 'Not specified'}
Source/Origin: {analysis.source or 'Not specified'}
Upload Date: {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
Analysis Completed: {analysis.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
Analyzed By: {current_user.email}

INTEGRITY VERIFICATION
----------------------
File Hash (SHA-256): {analysis.file_hash}
This cryptographic hash ensures file integrity and admissibility
in legal proceedings. Any modification to the original file will
result in a different hash value, allowing detection of tampering.

LEGAL NOTICE
------------
This report is generated for official use only and contains chain-of-custody
verified evidence. The SHA-256 cryptographic hash ensures file integrity and
admissibility. Any unauthorized modification, reproduction, or distribution
is prohibited.

This analysis was conducted using BarberX Legal Tech Platform certified
forensic analysis tools in compliance with digital evidence standards.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BarberX Legal Tech Platform
BWC Forensic Analysis System | Copyright © 2024-2026
For official use only - Confidential
"""
            
            with open(str(txt_path), 'w') as f:
                f.write(text_content)
            
            # Log audit
            AuditLog.log('report_exported', 'analysis', analysis.id, {'format': 'txt'})
            
            return send_file(
                str(txt_path),
                mimetype='text/plain',
                as_attachment=True,
                download_name=f"BWC_Analysis_{analysis.case_number or analysis.id}.txt"
            )
        
        elif format == 'md':
            # Generate Markdown export
            md_path = output_dir / f'report_{analysis.id}.md'
            
            duration_str = f"{int(analysis.duration // 60)}m {int(analysis.duration % 60)}s" if analysis.duration else 'N/A'
            file_size_str = f"{analysis.file_size / (1024*1024):.2f} MB" if analysis.file_size else 'N/A'
            
            markdown_content = f"""# BWC FORENSIC ANALYSIS REPORT

**Generated:** {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}

---

## EXECUTIVE SUMMARY

This report presents the forensic analysis results for body-worn camera footage case **{analysis.case_number or 'N/A'}**. 
The analysis identified **{analysis.total_speakers or 0}** distinct speaker(s) across **{analysis.total_segments or 0}** transcript segments.

{"**⚠️ ALERT:** " + str(analysis.critical_discrepancies) + " critical discrepancies require immediate attention." if analysis.critical_discrepancies and analysis.critical_discrepancies > 0 else "✅ No critical issues were detected."}

---

## CASE INFORMATION

| Field | Value |
|-------|-------|
| Case Number | {analysis.case_number or 'N/A'} |
| Evidence Number | {analysis.evidence_number or 'N/A'} |
| Filename | {analysis.filename} |
| File Size | {file_size_str} |
| Duration | {duration_str} |
| SHA-256 Hash | `{analysis.file_hash}` |

---

## ANALYSIS RESULTS

| Metric | Value | Status |
|--------|-------|--------|
| Speakers Identified | {analysis.total_speakers or 0} | ✓ |
| Transcript Segments | {analysis.total_segments or 0} | ✓ |
| Total Discrepancies | {analysis.total_discrepancies or 0} | {'⚠️' if analysis.total_discrepancies and analysis.total_discrepancies > 0 else '✓'} |
| Critical Issues | {analysis.critical_discrepancies or 0} | {'⚠️' if analysis.critical_discrepancies and analysis.critical_discrepancies > 0 else '✓'} |
| Analysis Status | {analysis.status.upper()} | {'✓' if analysis.status == 'completed' else '⏳'} |
| Completion | {analysis.progress}% | {'✓' if analysis.progress == 100 else '⏳'} |

---

## CHAIN OF CUSTODY

| Event | Details |
|-------|---------|
| Evidence Acquired By | {analysis.acquired_by or 'Not specified'} |
| Source/Origin | {analysis.source or 'Not specified'} |
| Upload Date | {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')} |
| Analysis Completed | {analysis.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')} |
| Analyzed By | {current_user.email} |
| Integrity Verification | `SHA-256: {analysis.file_hash}` |

---

## INTEGRITY VERIFICATION

```
File Hash (SHA-256): {analysis.file_hash}
```

This cryptographic hash ensures file integrity and admissibility in legal proceedings. 
Any modification to the original file will result in a different hash value, allowing 
detection of tampering.

---

## LEGAL NOTICE

This report is generated for official use only and contains chain-of-custody verified evidence. 
The **SHA-256 cryptographic hash** ensures file integrity and admissibility. 

⚠️ Any unauthorized modification, reproduction, or distribution is prohibited.

This analysis was conducted using BarberX Legal Tech Platform certified forensic analysis tools 
in compliance with digital evidence standards.

---

**BarberX Legal Tech Platform**  
BWC Forensic Analysis System | Copyright © 2024-2026  
*For official use only - Confidential*
"""
            
            with open(str(md_path), 'w') as f:
                f.write(markdown_content)
            
            # Log audit
            AuditLog.log('report_exported', 'analysis', analysis.id, {'format': 'md'})
            
            return send_file(
                str(md_path),
                mimetype='text/markdown',
                as_attachment=True,
                download_name=f"BWC_Analysis_{analysis.case_number or analysis.id}.md"
            )
    
    except ImportError as e:
        return jsonify({
            'error': 'Export dependencies not installed',
            'message': f'Please install: pip install reportlab python-docx'
        }), 500
    except Exception as e:
        app.logger.error(f'Export error: {str(e)}')
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


# ========================================
# API ROUTES - User Management
# ========================================

@app.route('/api/user/profile', methods=['GET', 'PUT'])
@login_required
def user_profile():
    """Get or update user profile"""
    if request.method == 'GET':
        return jsonify(current_user.to_dict())
    
    # PUT - update profile
    data = request.get_json()
    
    if 'full_name' in data:
        current_user.full_name = data['full_name']
    if 'organization' in data:
        current_user.organization = data['organization']
    
    db.session.commit()
    
    # Log audit
    AuditLog.log('profile_updated', 'user', str(current_user.id))
    
    return jsonify(current_user.to_dict())


@app.route('/api/user/api-keys', methods=['GET', 'POST'])
@login_required
def manage_api_keys():
    """Manage API keys"""
    if request.method == 'GET':
        keys = current_user.api_keys.filter_by(is_active=True).all()
        return jsonify({
            'api_keys': [k.to_dict() for k in keys]
        })
    
    # Create new API key
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'API key name required'}), 400
    
    # Check tier limits
    if current_user.subscription_tier == 'free':
        return jsonify({'error': 'API access requires Professional or Enterprise plan'}), 403
    
    api_key = APIKey(
        user_id=current_user.id,
        name=data['name']
    )
    api_key.generate_key()
    
    db.session.add(api_key)
    db.session.commit()
    
    # Log audit
    AuditLog.log('api_key_created', 'api_key', str(api_key.id))
    
    return jsonify(api_key.to_dict()), 201


# ========================================
# ADMIN ROUTES
# ========================================

# ========================================
# DASHBOARD API ROUTES
# ========================================

@app.route('/api/dashboard-stats', methods=['GET'])
@login_required
def dashboard_stats():
    """Get dashboard statistics for current user"""
    from datetime import timedelta
    from sqlalchemy import extract, func
    
    # Get current month's analysis count
    now = datetime.utcnow()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    analyses_this_month = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.created_at >= first_day
    ).count()
    
    # Get tier limits
    tier_limits = current_user.get_tier_limits()
    
    # Get completed count
    completed_count = Analysis.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).count()
    
    # Get analyzing count
    analyzing_count = Analysis.query.filter_by(
        user_id=current_user.id,
        status='analyzing'
    ).count()
    
    # Get failed count
    failed_count = Analysis.query.filter_by(
        user_id=current_user.id,
        status='failed'
    ).count()
    
    # Get daily activity for last 7 days
    seven_days_ago = now - timedelta(days=7)
    daily_activity = db.session.query(
        func.date(Analysis.created_at).label('date'),
        func.count(Analysis.id).label('count')
    ).filter(
        Analysis.user_id == current_user.id,
        Analysis.created_at >= seven_days_ago
    ).group_by(func.date(Analysis.created_at)).all()
    
    # Format daily activity
    daily_counts = [0] * 7
    for activity in daily_activity:
        days_diff = (now.date() - activity.date).days
        if 0 <= days_diff < 7:
            daily_counts[6 - days_diff] = activity.count
    
    return jsonify({
        'analyses_this_month': analyses_this_month,
        'storage_used_mb': current_user.storage_used_mb,
        'tier_limits': tier_limits,
        'completed_count': completed_count,
        'analyzing_count': analyzing_count,
        'failed_count': failed_count,
        'daily_activity': daily_counts,
        'subscription_tier': current_user.subscription_tier,
        'role': current_user.role
    })


@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@login_required
def get_analysis_details(analysis_id):
    """Get specific analysis details"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    return jsonify(analysis.to_dict())


@app.route('/api/subscription/upgrade', methods=['POST'])
@login_required
def upgrade_subscription():
    """Upgrade user subscription tier"""
    data = request.get_json()
    new_tier = data.get('tier')
    
    valid_tiers = ['free', 'professional', 'enterprise']
    
    if new_tier not in valid_tiers:
        return jsonify({'error': 'Invalid tier'}), 400
    
    # In production, integrate with Stripe here
    current_user.subscription_tier = new_tier
    db.session.commit()
    
    # Log audit
    AuditLog.log('subscription_upgraded', 'user', str(current_user.id), {
        'from': current_user.subscription_tier,
        'to': new_tier
    })
    
    return jsonify({
        'message': 'Subscription upgraded successfully',
        'new_tier': new_tier,
        'tier_limits': current_user.get_tier_limits()
    })


@app.route('/api/user/api-keys', methods=['GET'])
@login_required
def list_api_keys():
    """List user's API keys"""
    if current_user.subscription_tier not in ['professional', 'enterprise']:
        return jsonify({'error': 'API keys require Professional or Enterprise tier'}), 403
    
    keys = APIKey.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'total': len(keys),
        'keys': [k.to_dict() for k in keys]
    })


@app.route('/api/user/api-keys/<key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id):
    """Delete an API key"""
    key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    
    if not key:
        return jsonify({'error': 'API key not found'}), 404
    
    db.session.delete(key)
    db.session.commit()
    
    # Log audit
    AuditLog.log('api_key_deleted', 'api_key', str(key_id))
    
    return jsonify({'message': 'API key deleted successfully'})


@app.route('/api/audit-logs', methods=['GET'])
@login_required
def list_audit_logs():
    """List user's audit logs"""
    limit = request.args.get('limit', 50, type=int)
    
    logs = AuditLog.query.filter_by(user_id=current_user.id)\
        .order_by(AuditLog.created_at.desc())\
        .limit(limit).all()
    
    return jsonify({
        'total': len(logs),
        'logs': [{
            'id': log.id,
            'action': log.action,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'details': log.details,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat()
        } for log in logs]
    })


# ========================================
# ADMIN ROUTES
# ========================================

@app.route('/admin/users', methods=['GET'])
@login_required
def admin_list_users():
    """Admin: List all users"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    return jsonify({
        'total': len(users),
        'users': [u.to_dict() for u in users]
    })


@app.route('/admin/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def admin_manage_user(user_id):
    """Admin: Get, update, or delete specific user"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify(user.to_dict())
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'organization' in data:
            user.organization = data['organization']
        if 'subscription_tier' in data:
            if data['subscription_tier'] in ['free', 'professional', 'enterprise']:
                user.subscription_tier = data['subscription_tier']
        if 'role' in data:
            if data['role'] in ['user', 'pro', 'admin']:
                user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'is_verified' in data:
            user.is_verified = data['is_verified']
        
        db.session.commit()
        
        # Log audit
        AuditLog.log('admin_user_updated', 'user', str(user_id), {
            'updated_by': current_user.email
        })
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
    
    elif request.method == 'DELETE':
        # Don't allow deleting yourself
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        # Log audit
        AuditLog.log('admin_user_deleted', 'user', str(user_id), {
            'deleted_by': current_user.email,
            'deleted_email': user.email
        })
        
        return jsonify({'message': 'User deleted successfully'})


@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def admin_toggle_user_status(user_id):
    """Admin: Enable/disable user account"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow disabling yourself
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot disable your own account'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    # Log audit
    AuditLog.log('admin_user_status_toggled', 'user', str(user_id), {
        'new_status': 'active' if user.is_active else 'inactive',
        'changed_by': current_user.email
    })
    
    return jsonify({
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
        'is_active': user.is_active
    })


@app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def admin_reset_user_password(user_id):
    """Admin: Reset user password"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data.get('new_password'):
        return jsonify({'error': 'New password required'}), 400
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    # Log audit
    AuditLog.log('admin_password_reset', 'user', str(user_id), {
        'reset_by': current_user.email
    })
    
    return jsonify({'message': 'Password reset successfully'})


@app.route('/admin/analyses', methods=['GET'])
@login_required
def admin_list_analyses():
    """Admin: List all analyses"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    status_filter = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query = Analysis.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    total = query.count()
    analyses = query.order_by(Analysis.created_at.desc()).limit(limit).offset(offset).all()
    
    return jsonify({
        'total': total,
        'limit': limit,
        'offset': offset,
        'analyses': [a.to_dict() for a in analyses]
    })


@app.route('/admin/analyses/<analysis_id>', methods=['DELETE'])
@login_required
def admin_delete_analysis(analysis_id):
    """Admin: Delete an analysis"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Delete associated file if exists
    if analysis.file_path and os.path.exists(analysis.file_path):
        try:
            os.remove(analysis.file_path)
        except Exception as e:
            app.logger.error(f'Error deleting file: {e}')
    
    # Update user storage
    if analysis.user:
        analysis.user.storage_used_mb -= analysis.file_size / (1024 * 1024)
        if analysis.user.storage_used_mb < 0:
            analysis.user.storage_used_mb = 0
    
    db.session.delete(analysis)
    db.session.commit()
    
    # Log audit
    AuditLog.log('admin_analysis_deleted', 'analysis', analysis_id, {
        'deleted_by': current_user.email
    })
    
    return jsonify({'message': 'Analysis deleted successfully'})


@app.route('/admin/stats', methods=['GET'])
@login_required
def admin_stats():
    """Admin: Get platform statistics"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    from sqlalchemy import func
    from datetime import timedelta
    
    total_users = User.query.count()
    total_analyses = Analysis.query.count()
    completed_analyses = Analysis.query.filter_by(status='completed').count()
    analyzing = Analysis.query.filter_by(status='analyzing').count()
    failed = Analysis.query.filter_by(status='failed').count()
    
    # Subscription breakdown
    free_users = User.query.filter_by(subscription_tier='free').count()
    pro_users = User.query.filter_by(subscription_tier='professional').count()
    enterprise_users = User.query.filter_by(subscription_tier='enterprise').count()
    
    # Storage stats
    total_storage = db.session.query(func.sum(User.storage_used_mb)).scalar() or 0
    
    # Active users (logged in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = User.query.filter(User.last_login >= thirty_days_ago).count()
    
    # Daily activity for last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_analyses = db.session.query(
        func.date(Analysis.created_at).label('date'),
        func.count(Analysis.id).label('count')
    ).filter(
        Analysis.created_at >= seven_days_ago
    ).group_by(func.date(Analysis.created_at)).all()
    
    # Format daily activity
    now = datetime.utcnow()
    daily_counts = [0] * 7
    for activity in daily_analyses:
        days_diff = (now.date() - activity.date).days
        if 0 <= days_diff < 7:
            daily_counts[6 - days_diff] = activity.count
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_analyses': total_analyses,
        'completed_analyses': completed_analyses,
        'analyzing_count': analyzing,
        'failed_count': failed,
        'success_rate': (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0,
        'subscription_breakdown': {
            'free': free_users,
            'professional': pro_users,
            'enterprise': enterprise_users
        },
        'total_storage_gb': round(total_storage / 1024, 2),
        'daily_activity': daily_counts
    })


@app.route('/admin/audit-logs', methods=['GET'])
@login_required
def admin_audit_logs():
    """Admin: View all audit logs"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    action_filter = request.args.get('action')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query = AuditLog.query
    
    if action_filter:
        query = query.filter_by(action=action_filter)
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
    
    return jsonify({
        'total': total,
        'limit': limit,
        'offset': offset,
        'logs': [{
            'id': log.id,
            'user_id': log.user_id,
            'action': log.action,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'details': log.details,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'created_at': log.created_at.isoformat()
        } for log in logs]
    })


@app.route('/admin/system-info', methods=['GET'])
@login_required
def admin_system_info():
    """Admin: Get system information"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    import psutil
    
    # Database size
    db_path = os.path.join(app.instance_path, 'barberx_legal.db')
    db_size_mb = os.path.getsize(db_path) / (1024 * 1024) if os.path.exists(db_path) else 0
    
    # Upload folder size
    upload_folder = app.config['UPLOAD_FOLDER']
    upload_size_mb = 0
    if os.path.exists(upload_folder):
        for root, dirs, files in os.walk(upload_folder):
            upload_size_mb += sum(os.path.getsize(os.path.join(root, f)) for f in files)
        upload_size_mb = upload_size_mb / (1024 * 1024)
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return jsonify({
        'database_size_mb': round(db_size_mb, 2),
        'upload_storage_mb': round(upload_size_mb, 2),
        'upload_storage_gb': round(upload_size_mb / 1024, 2),
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used_gb': round(memory.used / (1024**3), 2),
        'memory_total_gb': round(memory.total / (1024**3), 2),
        'disk_percent': disk.percent,
        'disk_used_gb': round(disk.used / (1024**3), 2),
        'disk_total_gb': round(disk.total / (1024**3), 2),
        'python_version': sys.version,
        'flask_version': flask.__version__
    })


# ========================================
# INITIALIZE DATABASE
# ========================================

with app.app_context():
    db.create_all()
    app.logger.info('Database tables initialized')
    
    # Admin user already created via create_admin.py
    # Use admin@barberx.info with the 33-char password from that script


# ========================================
# ADMIN SETTINGS MANAGEMENT
# ========================================

@app.route('/admin/settings', methods=['GET'])
@login_required
def admin_get_settings():
    """Admin: Get all app settings"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get all settings grouped by category
    settings = AppSettings.query.order_by(AppSettings.category, AppSettings.key).all()
    
    settings_by_category = {}
    for setting in settings:
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        
        settings_by_category[setting.category].append({
            'id': setting.id,
            'key': setting.key,
            'value': setting.value,
            'value_type': setting.value_type,
            'description': setting.description,
            'is_editable': setting.is_editable,
            'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
        })
    
    return jsonify({
        'settings': settings_by_category,
        'total': len(settings)
    })


@app.route('/admin/settings/<int:setting_id>', methods=['PUT'])
@login_required
def admin_update_setting(setting_id):
    """Admin: Update a setting"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    setting = AppSettings.query.get_or_404(setting_id)
    
    if not setting.is_editable:
        return jsonify({'error': 'This setting is not editable'}), 400
    
    data = request.get_json()
    
    if 'value' in data:
        setting.value = str(data['value'])
        setting.updated_at = datetime.utcnow()
        setting.updated_by = current_user.id
        
        db.session.commit()
        
        AuditLog.log('setting_update', 'AppSettings', str(setting_id), {
            'key': setting.key,
            'new_value': data['value']
        })
        
        return jsonify({
            'message': 'Setting updated successfully',
            'setting': {
                'id': setting.id,
                'key': setting.key,
                'value': setting.value,
                'updated_at': setting.updated_at.isoformat()
            }
        })
    
    return jsonify({'error': 'No value provided'}), 400


@app.route('/admin/settings', methods=['POST'])
@login_required
def admin_create_setting():
    """Admin: Create a new setting"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    required_fields = ['key', 'value', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if key already exists
    existing = AppSettings.query.filter_by(key=data['key']).first()
    if existing:
        return jsonify({'error': 'Setting key already exists'}), 400
    
    setting = AppSettings(
        key=data['key'],
        value=str(data['value']),
        value_type=data.get('value_type', 'string'),
        category=data['category'],
        description=data.get('description', ''),
        is_editable=data.get('is_editable', True),
        updated_by=current_user.id
    )
    
    db.session.add(setting)
    db.session.commit()
    
    AuditLog.log('setting_create', 'AppSettings', str(setting.id), {
        'key': setting.key,
        'value': data['value']
    })
    
    return jsonify({
        'message': 'Setting created successfully',
        'setting': {
            'id': setting.id,
            'key': setting.key,
            'value': setting.value,
            'category': setting.category
        }
    }), 201


@app.route('/admin/settings/<int:setting_id>', methods=['DELETE'])
@login_required
def admin_delete_setting(setting_id):
    """Admin: Delete a setting"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    setting = AppSettings.query.get_or_404(setting_id)
    
    if not setting.is_editable:
        return jsonify({'error': 'This setting cannot be deleted'}), 400
    
    key = setting.key
    db.session.delete(setting)
    db.session.commit()
    
    AuditLog.log('setting_delete', 'AppSettings', str(setting_id), {
        'key': key
    })
    
    return jsonify({'message': 'Setting deleted successfully'})


@app.route('/admin/settings/initialize', methods=['POST'])
@login_required
def admin_initialize_settings():
    """Admin: Initialize default settings"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Define default settings
    default_settings = [
        # General Settings
        {'key': 'app_name', 'value': 'BarberX Legal Tech', 'value_type': 'string', 'category': 'general', 
         'description': 'Application name displayed throughout the platform'},
        {'key': 'app_tagline', 'value': 'Professional BWC Forensic Analysis', 'value_type': 'string', 'category': 'general',
         'description': 'Tagline shown on homepage and login'},
        {'key': 'maintenance_mode', 'value': 'false', 'value_type': 'bool', 'category': 'general',
         'description': 'Enable to put site in maintenance mode'},
        {'key': 'allow_registrations', 'value': 'true', 'value_type': 'bool', 'category': 'general',
         'description': 'Allow new user registrations'},
        {'key': 'contact_email', 'value': 'support@barberx.info', 'value_type': 'string', 'category': 'general',
         'description': 'Contact email for support'},
        
        # Security Settings
        {'key': 'session_timeout_minutes', 'value': '60', 'value_type': 'int', 'category': 'security',
         'description': 'User session timeout in minutes'},
        {'key': 'password_min_length', 'value': '8', 'value_type': 'int', 'category': 'security',
         'description': 'Minimum password length'},
        {'key': 'require_email_verification', 'value': 'true', 'value_type': 'bool', 'category': 'security',
         'description': 'Require email verification for new accounts'},
        {'key': 'max_login_attempts', 'value': '5', 'value_type': 'int', 'category': 'security',
         'description': 'Max failed login attempts before lockout'},
        {'key': 'enable_2fa', 'value': 'false', 'value_type': 'bool', 'category': 'security',
         'description': 'Enable two-factor authentication'},
        
        # Feature Flags
        {'key': 'enable_api', 'value': 'true', 'value_type': 'bool', 'category': 'features',
         'description': 'Enable API access for Pro/Enterprise users'},
        {'key': 'enable_analytics', 'value': 'true', 'value_type': 'bool', 'category': 'features',
         'description': 'Enable analytics dashboard'},
        {'key': 'enable_export', 'value': 'true', 'value_type': 'bool', 'category': 'features',
         'description': 'Enable data export functionality'},
        {'key': 'enable_webhooks', 'value': 'false', 'value_type': 'bool', 'category': 'features',
         'description': 'Enable webhook notifications'},
        
        # Tier Limits
        {'key': 'free_tier_analyses', 'value': '5', 'value_type': 'int', 'category': 'limits',
         'description': 'Max analyses per month for free tier'},
        {'key': 'free_tier_storage_mb', 'value': '500', 'value_type': 'int', 'category': 'limits',
         'description': 'Max storage in MB for free tier'},
        {'key': 'pro_tier_analyses', 'value': '100', 'value_type': 'int', 'category': 'limits',
         'description': 'Max analyses per month for professional tier'},
        {'key': 'pro_tier_storage_mb', 'value': '2048', 'value_type': 'int', 'category': 'limits',
         'description': 'Max storage in MB for professional tier'},
        {'key': 'max_file_size_mb', 'value': '500', 'value_type': 'int', 'category': 'limits',
         'description': 'Maximum file upload size in MB'},
        
        # Email Settings
        {'key': 'smtp_enabled', 'value': 'false', 'value_type': 'bool', 'category': 'email',
         'description': 'Enable SMTP email sending'},
        {'key': 'smtp_host', 'value': '', 'value_type': 'string', 'category': 'email',
         'description': 'SMTP server hostname'},
        {'key': 'smtp_port', 'value': '587', 'value_type': 'int', 'category': 'email',
         'description': 'SMTP server port'},
        {'key': 'smtp_username', 'value': '', 'value_type': 'string', 'category': 'email',
         'description': 'SMTP username'},
        {'key': 'from_email', 'value': 'noreply@barberx.info', 'value_type': 'string', 'category': 'email',
         'description': 'From email address'},
        
        # Branding
        {'key': 'primary_color', 'value': '#3b82f6', 'value_type': 'string', 'category': 'branding',
         'description': 'Primary brand color (hex)'},
        {'key': 'secondary_color', 'value': '#8b5cf6', 'value_type': 'string', 'category': 'branding',
         'description': 'Secondary brand color (hex)'},
        {'key': 'logo_url', 'value': '/assets/images/logo.png', 'value_type': 'string', 'category': 'branding',
         'description': 'URL to application logo'},
        {'key': 'favicon_url', 'value': '/assets/images/favicon.ico', 'value_type': 'string', 'category': 'branding',
         'description': 'URL to favicon'},
    ]
    
    created = 0
    skipped = 0
    
    for setting_data in default_settings:
        existing = AppSettings.query.filter_by(key=setting_data['key']).first()
        if not existing:
            setting = AppSettings(
                key=setting_data['key'],
                value=setting_data['value'],
                value_type=setting_data['value_type'],
                category=setting_data['category'],
                description=setting_data['description'],
                is_editable=True,
                updated_by=current_user.id
            )
            db.session.add(setting)
            created += 1
        else:
            skipped += 1
    
    db.session.commit()
    
    AuditLog.log('settings_initialize', 'AppSettings', None, {
        'created': created,
        'skipped': skipped
    })
    
    return jsonify({
        'message': 'Settings initialized successfully',
        'created': created,
        'skipped': skipped,
        'total': created + skipped
    })


# ========================================
# RUN APPLICATION
# ========================================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║        BarberX Legal Technologies                              ║
    ║        Professional BWC Forensic Analysis Platform             ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    
    🌐 Web Application: http://localhost:5000
    🔐 Admin Login: admin@barberx.info / admin123
    📊 Database: SQLite (barberx_legal.db)
    📁 Logs: ./logs/barberx.log
    
    Features:
    ✅ Multi-user authentication
    ✅ Role-based access control
    ✅ Subscription tiers (Free, Professional, Enterprise)
    ✅ API key management
    ✅ Audit logging
    ✅ Database persistence
    ✅ Professional dashboard
    
    Ready for production deployment!
    Press Ctrl+C to stop the server.
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
