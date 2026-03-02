"""
Evident Authentication Routes
Login, logout, registration, password reset
"""

from datetime import datetime, timedelta
from functools import wraps
import hashlib

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import secrets
from email_validator import validate_email, EmailNotValidError

from auth.models import db, User, UserRole, TierLevel, AuditLog
from auth.security import get_limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Login attempt tracking for brute force protection
LOGIN_ATTEMPTS = {}  # In production, use Redis or database
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


def track_failed_login(identifier: str) -> tuple[bool, int]:
    """Track failed login attempts and return (is_locked, remaining_seconds)."""
    now = datetime.utcnow()
    
    # Clean up expired lockouts
    expired = [k for k, v in LOGIN_ATTEMPTS.items() 
               if v.get('locked_until') and v['locked_until'] < now]
    for k in expired:
        del LOGIN_ATTEMPTS[k]
    
    if identifier not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[identifier] = {'count': 0, 'locked_until': None}
    
    attempt = LOGIN_ATTEMPTS[identifier]
    
    # Check if currently locked
    if attempt.get('locked_until') and attempt['locked_until'] > now:
        remaining = int((attempt['locked_until'] - now).total_seconds())
        return True, remaining
    
    # Increment failed attempts
    attempt['count'] = attempt.get('count', 0) + 1
    attempt['last_attempt'] = now
    
    # Lock if exceeded max attempts
    if attempt['count'] >= MAX_LOGIN_ATTEMPTS:
        attempt['locked_until'] = now + LOCKOUT_DURATION
        remaining = int(LOCKOUT_DURATION.total_seconds())
        return True, remaining
    
    return False, 0


def clear_login_attempts(identifier: str):
    """Clear login attempts on successful login."""
    if identifier in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[identifier]


def _limit(*args):
    """Apply rate limit if limiter is available, otherwise no-op."""
    limiter = get_limiter()
    if limiter:
        return limiter.limit(*args)
    # Return a no-op decorator when limiter is not initialized
    def noop(f):
        return f
    return noop


def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


@auth_bp.route('/register', methods=['GET', 'POST'])
@_limit("5 per minute")
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        organization = request.form.get('organization', '').strip()
        
        # Validation
        errors = []
        
        # Email validation
        try:
            validate_email(email)
        except EmailNotValidError:
            errors.append('Invalid email address')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        # Username validation
        if len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken')
        
        # Password validation
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if password != password_confirm:
            errors.append('Passwords do not match')
        if not full_name:
            errors.append('Full name is required')
        
        if errors:
            for error in errors:
                flash(f'❌ {error}', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user
        try:
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                organization=organization or None,
                role=UserRole.USER,
                tier=TierLevel.FREE,
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Log action
            user.log_action('user_registered', {'username': username}, get_client_ip())
            
            flash(f'✅ Account created! Welcome, {full_name}. Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            flash(f'❌ Registration failed: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@_limit("10 per minute")
def login():
    """User login with improved security"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        totp_code = request.form.get('totp_code', '').strip()
        remember = request.form.get('remember', False)
        
        # Create identifier for rate limiting (hash of email + IP)
        identifier = hashlib.sha256(f"{email}:{get_client_ip()}".encode()).hexdigest()[:16]
        
        # Check for lockout
        is_locked, remaining = track_failed_login.__wrapped__(identifier) if hasattr(track_failed_login, '__wrapped__') else (False, 0)
        
        # Manual lockout check (don't increment on check)
        if identifier in LOGIN_ATTEMPTS:
            attempt = LOGIN_ATTEMPTS[identifier]
            if attempt.get('locked_until') and attempt['locked_until'] > datetime.utcnow():
                remaining = int((attempt['locked_until'] - datetime.utcnow()).total_seconds())
                flash(f'❌ Too many login attempts. Try again in {remaining // 60} minutes.', 'danger')
                return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email).first()
        login_failed = False
        requires_2fa = False
        
        # Unified error handling to prevent information leakage
        if not user:
            login_failed = True
        elif not user.is_active:
            login_failed = True
            # Log attempted login to disabled account (security event)
            current_app.logger.warning(f"Login attempt to disabled account: {email}")
        elif not user.check_password(password):
            login_failed = True
        elif user.two_factor_enabled and user.two_factor_secret:
            # 2FA is required
            if not totp_code:
                requires_2fa = True
            else:
                # Verify TOTP code
                import pyotp
                totp = pyotp.TOTP(user.two_factor_secret)
                if not totp.verify(totp_code, valid_window=1):
                    login_failed = True
        
        if login_failed:
            # Track failed attempt
            is_locked, remaining = track_failed_login(identifier)
            
            # Log failed attempt (don't reveal which field was wrong)
            AuditLog.log_failed_login(email, get_client_ip())
            
            if is_locked:
                flash(f'❌ Too many login attempts. Try again in {remaining // 60} minutes.', 'danger')
            else:
                # Generic error message - DO NOT reveal if email exists or password was wrong
                flash('❌ Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if requires_2fa:
            # Store partial auth state in session
            session['pending_2fa_user'] = user.id
            session['pending_2fa_remember'] = remember
            session['pending_2fa_expires'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            return render_template('auth/login.html', requires_2fa=True, email=email)
        
        if user:
            try:
                # Clear failed login attempts on success
                clear_login_attempts(identifier)
                
                login_user(user, remember=remember)
                user.update_last_login(get_client_ip())
                user.log_action('user_login', {'remember_me': remember, 'method': '2fa' if totp_code else 'password'}, get_client_ip())
                
                flash(f'✅ Welcome back, {user.full_name}!', 'success')
                
                # Handle next parameter for redirect
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            except Exception as e:
                current_app.logger.error(f"Login error: {str(e)}")
                flash('❌ Login failed', 'danger')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    current_user.log_action('user_logout', ip_address=get_client_ip())
    logout_user()
    flash('✅ Logged out successfully', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@_limit("3 per minute")
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
            db.session.commit()
            
            user.log_action('password_reset_requested', ip_address=get_client_ip())
            
            # TODO: Send email with reset link
            # send_password_reset_email(user, reset_token)
            
            flash('✅ If that email is registered, you will receive a password reset link', 'success')
        else:
            # Don't reveal if email exists
            flash('✅ If that email is registered, you will receive a password reset link', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@_limit("5 per minute")
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Find user with valid token
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or (user.password_reset_expires and user.password_reset_expires < datetime.utcnow()):
        flash('❌ Invalid or expired reset link', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if len(password) < 8:
            flash('❌ Password must be at least 8 characters', 'danger')
        elif password != password_confirm:
            flash('❌ Passwords do not match', 'danger')
        else:
            try:
                user.set_password(password)
                user.password_reset_token = None
                user.password_reset_expires = None
                db.session.commit()
                
                user.log_action('password_reset_completed', ip_address=get_client_ip())
                
                flash('✅ Password reset successfully. Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Reset failed: {str(e)}', 'danger')
        
        return redirect(url_for('auth.reset_password', token=token))
    
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.organization = request.form.get('organization', current_user.organization)
        current_user.bio = request.form.get('bio', current_user.bio)
        
        try:
            db.session.commit()
            current_user.log_action('profile_updated', ip_address=get_client_ip())
            flash('✅ Profile updated successfully', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Update failed: {str(e)}', 'danger')
    
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        new_password_confirm = request.form.get('new_password_confirm', '')
        
        if not current_user.check_password(old_password):
            flash('❌ Current password is incorrect', 'danger')
        elif len(new_password) < 8:
            flash('❌ New password must be at least 8 characters', 'danger')
        elif new_password != new_password_confirm:
            flash('❌ New passwords do not match', 'danger')
        else:
            try:
                current_user.set_password(new_password)
                db.session.commit()
                current_user.log_action('password_changed', ip_address=get_client_ip())
                flash('✅ Password changed successfully', 'success')
                return redirect(url_for('auth.profile'))
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Change failed: {str(e)}', 'danger')
        
        return redirect(url_for('auth.change_password'))
    
    return render_template('auth/change_password.html')


# ============================================================================
# Two-Factor Authentication Routes
# ============================================================================

@auth_bp.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Setup two-factor authentication"""
    import pyotp
    import qrcode
    import io
    import base64
    
    if current_user.two_factor_enabled:
        flash('\u2139\ufe0f Two-factor authentication is already enabled', 'info')
        return redirect(url_for('auth.profile'))
    
    if request.method == 'POST':
        verification_code = request.form.get('code', '').strip()
        secret = request.form.get('secret', '')
        
        if not secret:
            flash('\u274c Setup session expired. Please try again.', 'danger')
            return redirect(url_for('auth.setup_2fa'))
        
        # Verify the code
        totp = pyotp.TOTP(secret)
        if not totp.verify(verification_code, valid_window=1):
            flash('\u274c Invalid verification code. Please try again.', 'danger')
            return render_template('auth/setup_2fa.html', secret=secret, show_verify=True)
        
        # Enable 2FA
        try:
            current_user.two_factor_enabled = True
            current_user.two_factor_secret = secret
            db.session.commit()
            
            current_user.log_action('2fa_enabled', ip_address=get_client_ip())
            flash('\u2705 Two-factor authentication enabled successfully', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'\u274c Failed to enable 2FA: {str(e)}', 'danger')
            return redirect(url_for('auth.setup_2fa'))
    
    # Generate new secret
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    # Generate provisioning URI for authenticator apps
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name='Evident'
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white')
    
    # Convert to base64 for display
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template(
        'auth/setup_2fa.html',
        secret=secret,
        qr_code=qr_base64,
        show_verify=False
    )


@auth_bp.route('/2fa/disable', methods=['GET', 'POST'])
@login_required
def disable_2fa():
    """Disable two-factor authentication"""
    if not current_user.two_factor_enabled:
        flash('\u2139\ufe0f Two-factor authentication is not enabled', 'info')
        return redirect(url_for('auth.profile'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        if not current_user.check_password(password):
            flash('\u274c Invalid password', 'danger')
            return redirect(url_for('auth.disable_2fa'))
        
        try:
            current_user.two_factor_enabled = False
            current_user.two_factor_secret = None
            db.session.commit()
            
            current_user.log_action('2fa_disabled', ip_address=get_client_ip())
            flash('\u2705 Two-factor authentication has been disabled', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'\u274c Failed to disable 2FA: {str(e)}', 'danger')
    
    return render_template('auth/disable_2fa.html')


# API Routes

@auth_bp.route('/api/me', methods=['GET'])
@login_required
def api_me():
    """Get current user info"""
    return jsonify({
        'user': current_user.to_dict(include_sensitive=True),
        'tier_limits': current_user.get_tier_limits(),
    })


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API logout"""
    current_user.log_action('api_logout', ip_address=get_client_ip())
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out'}), 200
