"""
BarberX Authentication Routes
Login, logout, signup, and user management
"""

from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models_auth import db, User, UsageTracking, TierLevel
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
login_manager = LoginManager()


def is_safe_url(target):
    """Check if a redirect URL is safe (same host)"""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def init_auth(app):
    """Initialize authentication system with Flask app"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    app.register_blueprint(auth_bp)


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


# ═══════════════════════════════════════════════════════════════════════════
# DECORATORS - Tier & Feature Access Control
# ═══════════════════════════════════════════════════════════════════════════

def tier_required(min_tier):
    """Decorator to require minimum tier level"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.tier.value < min_tier.value:
                flash(f'This feature requires {min_tier.name} tier or higher. Please upgrade your account.', 'warning')
                return redirect(url_for('pricing'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def feature_required(feature_name):
    """Decorator to check if user has access to specific feature"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.can_access_feature(feature_name):
                flash(f'This feature is not available in your current tier. Please upgrade.', 'warning')
                return redirect(url_for('pricing'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_usage_limit(field):
    """Decorator to check usage limits before allowing action"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # Admin has no limits
            if current_user.is_admin or current_user.tier == TierLevel.ADMIN:
                return f(*args, **kwargs)
            
            # Get current usage
            usage = UsageTracking.get_or_create_current(current_user.id)
            
            # Check limit
            if not usage.check_limit(field, current_user):
                flash(f'You have reached your monthly limit for this feature. Please upgrade your tier.', 'warning')
                return redirect(url_for('pricing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            flash(f'Welcome back, {user.full_name or user.email}!', 'success')
            
            # Redirect to next page or dashboard (with open redirect protection)
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('auth.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup'))
        
        # Use strong password validation from utils
        try:
            from utils.security import InputValidator
            is_valid, error_msg = InputValidator.validate_password(password)
            if not is_valid:
                flash(error_msg, 'danger')
                return redirect(url_for('auth.signup'))
        except ImportError:
            # Fallback if utils not available
            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'danger')
                return redirect(url_for('auth.signup'))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Create new user - ALWAYS start with FREE tier
        try:
            new_user = User(
                email=email,
                full_name=full_name,
                tier=TierLevel.FREE,  # Security: Always FREE on signup
                is_active=True,
                is_verified=False  # Email verification required
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Create initial usage tracking
            UsageTracking.get_or_create_current(new_user.id)
            
            flash(f'Account created successfully! Please check your email to verify your account.', 'success')
            
            # Auto-login for development (remove in production after email verification)
            login_user(new_user)
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during signup. Please try again.', 'danger')
            print(f"Signup error: {e}")
    
    return render_template('auth/signup.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ═══════════════════════════════════════════════════════════════════════════
# USER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing usage and limits"""
    from models_auth import UsageTracking
    from app import Analysis
    
    usage = UsageTracking.get_or_create_current(current_user.id)
    limits = current_user.get_tier_limits()
    
    # Get recent analyses
    recent_analyses = Analysis.query.filter_by(user_id=current_user.id)\
        .order_by(Analysis.created_at.desc())\
        .limit(10)\
        .all()
    
    return render_template('auth/dashboard.html', 
                         usage=usage, 
                         limits=limits,
                         recent_analyses=recent_analyses)


@auth_bp.route('/usage/api')
@login_required
def usage_api():
    """API endpoint for current usage stats"""
    usage = UsageTracking.get_or_create_current(current_user.id)
    limits = current_user.get_tier_limits()
    
    return jsonify({
        'tier': current_user.tier_name,
        'tier_price': current_user.tier_price,
        'usage': {
            'bwc_videos': usage.bwc_videos_processed,
            'documents': usage.document_pages_processed,
            'transcription_minutes': usage.transcription_minutes_used,
            'searches': usage.search_queries_made,
            'storage_mb': usage.storage_used_mb,
        },
        'limits': limits,
        'subscription_active': current_user.is_subscription_active,
    })


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/admin/users')
@admin_required
def admin_users():
    """Admin dashboard - user management"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/admin_users.html', users=users)


@auth_bp.route('/admin/user/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def admin_toggle_user_active(user_id):
    """Admin: Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}.', 'success')
    return redirect(url_for('auth.admin_users'))


@auth_bp.route('/admin/user/<int:user_id>/change-tier', methods=['POST'])
@admin_required
def admin_change_user_tier(user_id):
    """Admin: Change user tier"""
    user = User.query.get_or_404(user_id)
    new_tier = request.form.get('tier')
    
    if new_tier in [t.name for t in TierLevel]:
        user.tier = TierLevel[new_tier]
        db.session.commit()
        flash(f'User {user.email} tier changed to {new_tier}.', 'success')
    else:
        flash('Invalid tier selected.', 'danger')
    
    return redirect(url_for('auth.admin_users'))
