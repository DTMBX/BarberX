"""
Evident Authentication Routes
Login, logout, registration, password reset
"""

from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import secrets
from email_validator import validate_email, EmailNotValidError

from auth.models import db, User, UserRole, TierLevel, AuditLog
from auth.security import get_limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


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
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('❌ Email not found', 'danger')
            user = None
        elif not user.is_active:
            flash('❌ Account is disabled', 'danger')
            user = None
        elif not user.check_password(password):
            flash('❌ Invalid password', 'danger')
            user = None
        
        if user:
            try:
                login_user(user, remember=remember)
                user.update_last_login(get_client_ip())
                user.log_action('user_login', {'remember_me': remember}, get_client_ip())
                
                flash(f'✅ Welcome back, {user.full_name}!', 'success')
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


from datetime import timedelta  # Add to imports at the top
