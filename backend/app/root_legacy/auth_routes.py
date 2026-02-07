# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Authentication Routes
Login, logout, signup, and user management with enhanced security
"""

import logging
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError

from .models_auth import (
    EmailVerificationToken,
    PasswordResetToken,
    TierLevel,
    UsageTracking,
    User,
    db,
)

# AI Security & Analytics
try:
    from login_security import check_login_security, login_security
    from user_analytics import check_churn_risk, track_login, track_signup

    AI_SECURITY_ENABLED = True
    print("[OK] AI-powered login security enabled")
except ImportError as e:
    AI_SECURITY_ENABLED = False
    print(f"[WARN] AI security not available: {e}")

    # Fallback functions
    def check_login_security(user_id=None, email=None):
        return {"risk_score": 0, "is_suspicious": False, "recommendation": "allow"}

    def track_login(user, success=True, method="password", risk_score=0):
        pass

    def track_signup(user, tier="FREE"):
        pass

    def check_churn_risk(user):
        return {"risk_level": "unknown", "risk_score": 0, "factors": []}


# ═══════════════════════════════════════════════════════════════════════════
# RATE LIMITING - Brute Force Protection
# ═══════════════════════════════════════════════════════════════════════════

# In-memory rate limiting (consider Redis for production)
login_attempts = defaultdict(list)  # IP -> list of timestamps
failed_logins = defaultdict(int)  # email -> count of failures
lockout_until = defaultdict(float)  # email -> lockout timestamp

# Rate limit settings
MAX_ATTEMPTS_PER_MINUTE = 5
MAX_FAILED_LOGINS = 5
LOCKOUT_DURATION = 300  # 5 minutes


def get_client_ip():
    """Get client IP, handling proxies"""
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def check_rate_limit(ip_address):
    """Check if IP has exceeded rate limit"""
    now = time.time()
    # Remove old attempts (older than 1 minute)
    login_attempts[ip_address] = [t for t in login_attempts[ip_address] if now - t < 60]
    return len(login_attempts[ip_address]) < MAX_ATTEMPTS_PER_MINUTE


def record_attempt(ip_address):
    """Record a login attempt"""
    login_attempts[ip_address].append(time.time())


def check_lockout(email):
    """Check if email is locked out"""
    if email in lockout_until:
        if time.time() < lockout_until[email]:
            remaining = int(lockout_until[email] - time.time())
            return True, remaining
        else:
            # Lockout expired, clear it
            del lockout_until[email]
            failed_logins[email] = 0
    return False, 0


def record_failed_login(email):
    """Record a failed login and potentially lock out"""
    failed_logins[email] += 1
    if failed_logins[email] >= MAX_FAILED_LOGINS:
        lockout_until[email] = time.time() + LOCKOUT_DURATION
        logger.warning(f"Account locked out due to {MAX_FAILED_LOGINS} failed attempts: {email}")
        return True
    return False


def clear_failed_logins(email):
    """Clear failed login count on successful login"""
    if email in failed_logins:
        del failed_logins[email]
    if email in lockout_until:
        del lockout_until[email]


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()

# Initialize logger
logger = logging.getLogger(__name__)


def is_safe_url(target):
    """Check if a redirect URL is safe (same host)"""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def init_auth(app):
    """Initialize authentication system with Flask app"""
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    app.register_blueprint(auth_bp)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        """Handle unauthorized access - return JSON for API routes, redirect for pages"""
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {
                        "error": "Authentication required",
                        "message": "Please log in to access this resource",
                        "login_url": "/auth/login",
                    }
                ),
                401,
            )
        return redirect(url_for("auth.login"))


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
                flash(
                    f"This feature requires {min_tier.name} tier or higher. Please upgrade your account.",
                    "warning",
                )
                return redirect(url_for("pricing"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    """Decorator to require admin access"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


def feature_required(feature_name):
    """Decorator to check if user has access to specific feature"""

    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.can_access_feature(feature_name):
                flash(
                    "This feature is not available in your current tier. Please upgrade.", "warning"
                )
                return redirect(url_for("pricing"))
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
                flash(
                    "You have reached your monthly limit for this feature. Please upgrade your tier.",
                    "warning",
                )
                return redirect(url_for("pricing"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═══════════════════════════════════════════════════════════════════════════


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login with enhanced security and rate limiting"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember", False)
        client_ip = get_client_ip()

        # Rate limiting check
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            flash("Too many login attempts. Please wait a moment and try again.", "danger")
            return render_template("auth/login.html")

        record_attempt(client_ip)

        # Check if account is locked out
        is_locked, remaining_seconds = check_lockout(email)
        if is_locked:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            flash(f"Account temporarily locked. Try again in {minutes}m {seconds}s.", "danger")
            return render_template("auth/login.html")

        # Basic validation
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/login.html")

        # AI Security Check BEFORE authentication
        security_check = check_login_security(email=email)
        risk_score = security_check.get("risk_score", 0)
        is_suspicious = security_check.get("is_suspicious", False)
        recommendation = security_check.get("recommendation", "allow")

        # Block highly suspicious attempts
        if recommendation == "block":
            logger.warning(
                f"Blocked suspicious login attempt for {email}: risk_score={risk_score}, IP={client_ip}"
            )
            flash(
                "Suspicious activity detected. Please try again later or contact support.", "danger"
            )
            track_login(None, success=False, method="password", risk_score=risk_score)
            return render_template("auth/login.html")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact support.", "danger")
                track_login(user, success=False, method="password", risk_score=risk_score)
                return render_template("auth/login.html")

            # Challenge suspicious logins (require email verification)
            if recommendation == "challenge" and not session.get(f"verified_{user.id}"):
                session["pending_login_user_id"] = user.id
                session["pending_login_remember"] = remember
                flash(
                    f"Unusual login detected (risk: {risk_score}/100). Please verify your email.",
                    "warning",
                )
                logger.info(f"Login challenge issued for {email}: risk_score={risk_score}")
                return redirect(url_for("auth.verify_login"))

            # Clear failed login count on success
            clear_failed_logins(email)

            login_user(user, remember=remember)
            user.update_last_login()

            # Track successful login with risk score
            track_login(user, success=True, method="password", risk_score=risk_score)

            logger.info(f"Successful login: {email} from IP {client_ip}")

            if is_suspicious:
                flash(f"Welcome back! (Security check: {risk_score}/100 risk)", "info")
            else:
                flash(f"Welcome back, {user.full_name or user.email}!", "success")

            # Redirect to next page or dashboard (with open redirect protection)
            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for("dashboard"))
        else:
            # Record failed login
            is_now_locked = record_failed_login(email)
            track_login(None, success=False, method="password", risk_score=risk_score)
            logger.warning(f"Failed login attempt for {email} from IP {client_ip}")

            if is_now_locked:
                flash(
                    f"Too many failed attempts. Account locked for {LOCKOUT_DURATION // 60} minutes.",
                    "danger",
                )
            else:
                remaining_attempts = MAX_FAILED_LOGINS - failed_logins.get(email, 0)
                if remaining_attempts <= 2:
                    flash(
                        f"Invalid email or password. {remaining_attempts} attempts remaining.",
                        "danger",
                    )
                else:
                    flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
@auth_bp.route("/register", methods=["GET", "POST"])  # Alias for backward compatibility
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    # Get requested tier from URL parameter (for display purposes)
    tier_param = request.args.get("tier", "free").lower()
    requested_tier_name = tier_param.title() if tier_param != "free" else "Free"
    trial_period = "14 days" if tier_param in ["professional", "premium"] else None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()

        # Validation
        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("auth.signup", tier=tier_param))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.signup", tier=tier_param))

        # Use strong password validation from utils
        try:
            from utils.security import InputValidator

            is_valid, error_msg = InputValidator.validate_password(password)
            if not is_valid:
                flash(error_msg, "danger")
                return redirect(url_for("auth.signup", tier=tier_param))
        except ImportError:
            # Fallback if utils not available
            if len(password) < 8:
                flash("Password must be at least 8 characters long.", "danger")
                return redirect(url_for("auth.signup", tier=tier_param))

        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.login"))

        # Create new user - ALWAYS start with FREE tier for security
        # Paid tiers require payment flow through Stripe checkout
        try:
            new_user = User(
                email=email,
                full_name=full_name,
                tier=TierLevel.FREE,  # Security: Always FREE on signup
                is_active=True,
                is_verified=False,  # Email verification required
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            # Create initial usage tracking
            UsageTracking.get_or_create_current(new_user.id)

            # Track signup in analytics
            track_signup(new_user, tier=TierLevel.FREE.name)

            # Send verification email
            try:
                token = EmailVerificationToken.generate(new_user.id)
                _send_verification_email(new_user.email, token)
            except Exception as e:
                logger.error(f"Failed to send verification email: {e}")

            # Auto-login for development (email verification recommended for production)
            login_user(new_user)

            # If user requested a paid tier, redirect to checkout
            if tier_param in ["professional", "premium"]:
                flash(
                    f"Account created! Please verify your email. Complete checkout to activate your {requested_tier_name} plan.",
                    "success",
                )
                # Store intended tier in session for checkout
                session["checkout_tier"] = tier_param
                return redirect(url_for("pricing"))
            else:
                flash(
                    "Account created successfully! Please check your email to verify your account.",
                    "success",
                )
                return redirect(url_for("dashboard"))

        except Exception as e:
            db.session.rollback()
            flash("An error occurred during signup. Please try again.", "danger")
            logger.error(f"Signup error: {e}", exc_info=True)

    return render_template(
        "auth/signup.html",
        requested_tier=requested_tier_name,
        tier_param=tier_param,
        trial_period=trial_period,
    )


@auth_bp.route("/logout")
@login_required
def logout():
    """User logout"""
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))


@auth_bp.route("/status")
def auth_status():
    """Check authentication status - useful for debugging"""
    client_ip = get_client_ip()

    status = {
        "authenticated": current_user.is_authenticated,
        "timestamp": datetime.utcnow().isoformat(),
        "rate_limited": not check_rate_limit(client_ip),
    }

    if current_user.is_authenticated:
        status.update(
            {
                "user_id": current_user.id,
                "email": current_user.email,
                "tier": current_user.tier.name
                if hasattr(current_user.tier, "name")
                else str(current_user.tier),
                "is_admin": current_user.is_admin,
                "is_active": current_user.is_active,
            }
        )

    return jsonify(status)


@auth_bp.route("/test-credentials", methods=["POST"])
def test_credentials():
    """Test credentials without logging in - for diagnostics only"""
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"})

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"success": False, "error": "User not found", "email_exists": False})

    password_valid = user.check_password(password)

    return jsonify(
        {
            "success": password_valid,
            "email_exists": True,
            "password_valid": password_valid,
            "user_active": user.is_active,
            "user_verified": user.is_verified,
            "tier": user.tier.name if hasattr(user.tier, "name") else str(user.tier),
        }
    )


@auth_bp.route("/verify-login", methods=["GET", "POST"])
def verify_login():
    """Email verification for suspicious logins (challenge flow)"""
    email = session.get("pending_verification_email")

    if not email:
        flash("Verification session expired. Please login again.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if not user:
        session.pop("pending_verification_email", None)
        flash("User not found. Please login again.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # For now, just verify they have access to the account
        # In production, send a verification email with a token
        verification_code = request.form.get("verification_code", "").strip()

        # Check if verification code matches
        # For now, accept any code and complete login (temporary implementation)
        # TODO: Implement proper email verification with secure tokens

        # Complete the login
        login_user(user)
        session.pop("pending_verification_email", None)

        # Track successful verification
        track_login(user, success=True, login_method="email_verification", risk_score=65)

        flash(
            "Login verified successfully! Your account security is important to us.",
            "success",
        )
        return redirect(url_for("dashboard"))

    # GET request - show verification form
    # Send verification email (if email service is configured)
    try:
        # Generate verification token
        token = EmailVerificationToken.generate(user.id)

        # Send email with verification code
        _send_login_verification_email(user.email, token)

        flash(
            "We've sent a verification code to your email. Please check your inbox.",
            "info",
        )
    except Exception as e:
        logger.warning(f"Could not send verification email: {e}")
        flash(
            "Please enter the verification code we sent to your email, or contact support.",
            "warning",
        )

    return render_template("auth/verify_login.html", email=email)


# ═══════════════════════════════════════════════════════════════════════════
# PASSWORD RESET
# ═══════════════════════════════════════════════════════════════════════════


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Explicitly validate CSRF token
        try:
            validate_csrf(request.form.get("csrf_token"))
        except ValidationError:
            flash("Security validation failed. Please try again.", "danger")
            return render_template("auth/forgot_password.html"), 400

        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        # Always show success message to prevent email enumeration
        flash(
            "If an account exists with that email, you will receive a password reset link.", "info"
        )

        if user:
            # Generate secure token (stored in database)
            token = PasswordResetToken.generate(user.id)

            # Send reset email
            try:
                _send_password_reset_email(user.email, token)
                logger.info(f"Password reset requested for {email}")
            except Exception as e:
                logger.error(f"Failed to send reset email: {e}")

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    # Validate token from database
    user = PasswordResetToken.validate(token)
    if not user:
        flash("This password reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        # Explicitly validate CSRF token
        try:
            validate_csrf(request.form.get("csrf_token"))
        except ValidationError:
            flash("Security validation failed. Please try again.", "danger")
            return render_template("auth/reset_password.html", token=token), 400

        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("auth/reset_password.html", token=token)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/reset_password.html", token=token)

        # Update password
        user.set_password(password)

        # Invalidate token
        reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
        if reset_token:
            reset_token.mark_used()

        db.session.commit()

        flash("Your password has been reset successfully. Please log in.", "success")
        logger.info(f"Password reset completed for {user.email}")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


def _send_password_reset_email(email, token):
    """Send password reset email"""
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Get SMTP settings from environment
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    from_email = os.environ.get("FROM_EMAIL", "noreply@Evident.info")

    # Build reset URL using the current request's host
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Evident - Password Reset Request"
    msg["From"] = from_email
    msg["To"] = email

    text_body = f"""
Evident Password Reset

You requested a password reset for your Evident account.

Click the link below to reset your password (valid for 1 hour):
{reset_url}

If you did not request this reset, please ignore this email.

- Evident Legal Technologies Team
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #B8860B, #DAA520); padding: 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; }}
        .content {{ padding: 30px; background: #f9f9f9; }}
        .button {{ display: inline-block; background: #B8860B; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ Evident</h1>
        </div>
        <div class="content">
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your Evident account.</p>
            <p>Click the button below to reset your password:</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p><small>This link expires in 1 hour.</small></p>
            <p>If you did not request this reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Evident Legal Technologies<br>Democratizing Legal Defense</p>
        </div>
    </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Send email (if SMTP configured)
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"Password reset email sent to {email}")
    else:
        # Log the reset URL for development
        logger.warning(f"SMTP not configured. Reset URL for {email}: {reset_url}")
        print(f"\n🔑 PASSWORD RESET URL (SMTP not configured):\n{reset_url}\n")


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════


@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    """Verify user email address"""
    user = EmailVerificationToken.validate(token)

    if not user:
        flash("This verification link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    # Mark user as verified
    user.is_verified = True

    # Mark token as used
    verify_token = EmailVerificationToken.query.filter_by(token=token, used=False).first()
    if verify_token:
        verify_token.mark_used()

    db.session.commit()

    flash("Your email has been verified! You can now log in.", "success")
    logger.info(f"Email verified for {user.email}")
    return redirect(url_for("auth.login"))


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    """Resend email verification link"""
    email = request.form.get("email", "").strip().lower()

    if not email:
        flash("Please provide your email address.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    # Always show success to prevent email enumeration
    flash("If an account exists with that email, a verification link has been sent.", "info")

    if user and not user.is_verified:
        try:
            token = EmailVerificationToken.generate(user.id)
            _send_verification_email(user.email, token)
            logger.info(f"Verification email resent to {email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")

    return redirect(url_for("auth.login"))


def _send_verification_email(email, token):
    """Send email verification link"""
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Get SMTP settings from environment
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    from_email = os.environ.get("FROM_EMAIL", "noreply@Evident.info")

    # Build verification URL
    verify_url = url_for("auth.verify_email", token=token, _external=True)

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Evident - Verify Your Email"
    msg["From"] = from_email
    msg["To"] = email

    text_body = f"""
Evident Email Verification

Please verify your email address to complete your Evident registration.

Click the link below to verify (valid for 24 hours):
{verify_url}

If you did not create an account, please ignore this email.

- Evident Legal Technologies Team
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #B8860B, #DAA520); padding: 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; }}
        .content {{ padding: 30px; background: #f9f9f9; }}
        .button {{ display: inline-block; background: #B8860B; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ Evident</h1>
        </div>
        <div class="content">
            <h2>Verify Your Email</h2>
            <p>Thank you for registering with Evident!</p>
            <p>Please click the button below to verify your email address:</p>
            <p style="text-align: center;">
                <a href="{verify_url}" class="button">Verify Email</a>
            </p>
            <p><small>This link expires in 24 hours.</small></p>
            <p>If you did not create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Evident Legal Technologies<br>Democratizing Legal Defense</p>
        </div>
    </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Send email (if SMTP configured)
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"Verification email sent to {email}")
    else:
        # Log the verification URL for development
        logger.warning(f"SMTP not configured. Verification URL for {email}: {verify_url}")
        print(f"\n✉️ VERIFICATION URL (SMTP not configured):\n{verify_url}\n")


def _send_login_verification_email(email, token):
    """Send login verification code for suspicious login attempts"""
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Get SMTP settings from environment
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    from_email = os.environ.get("FROM_EMAIL", "noreply@Evident.info")

    # Generate 6-digit verification code from token (last 6 chars)
    verification_code = token[-6:].upper()

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Evident - Verify Your Login"
    msg["From"] = from_email
    msg["To"] = email

    text_body = f"""
Evident Security Alert

We detected an unusual login attempt to your account.

Your verification code is: {verification_code}

If you did not attempt to login, please change your password immediately.

- Evident Security Team
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #DC143C, #FF6347); padding: 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; }}
        .content {{ padding: 30px; background: #f9f9f9; }}
        .code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; text-align: center; 
                 background: #fff; padding: 20px; border: 2px dashed #DC143C; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Evident Security</h1>
        </div>
        <div class="content">
            <h2>Unusual Login Detected</h2>
            <p>We detected an unusual login attempt to your account and need to verify it's you.</p>
            <p>Your verification code is:</p>
            <div class="code">{verification_code}</div>
            <p><strong>If you did not attempt to login:</strong></p>
            <ul>
                <li>Change your password immediately</li>
                <li>Contact our security team</li>
            </ul>
        </div>
        <div class="footer">
            <p>Evident Security Team<br>Protecting Your Legal Data</p>
        </div>
    </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Send email (if SMTP configured)
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"Login verification email sent to {email}")
    else:
        # Log the verification code for development
        logger.warning(f"SMTP not configured. Verification code for {email}: {verification_code}")
        print(f"\n🔐 LOGIN VERIFICATION CODE (SMTP not configured): {verification_code}\n")


# ═══════════════════════════════════════════════════════════════════════════
# USER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard showing usage and limits"""
    from app import Analysis
    from models_auth import UsageTracking

    usage = UsageTracking.get_or_create_current(current_user.id)
    limits = current_user.get_tier_limits()

    # Get recent analyses
    recent_analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "auth/dashboard.html", usage=usage, limits=limits, recent_analyses=recent_analyses
    )


@auth_bp.route("/usage/api")
@login_required
def usage_api():
    """API endpoint for current usage stats"""
    usage = UsageTracking.get_or_create_current(current_user.id)
    limits = current_user.get_tier_limits()

    return jsonify(
        {
            "tier": current_user.tier_name,
            "tier_price": current_user.tier_price,
            "usage": {
                "bwc_videos": usage.bwc_videos_processed,
                "documents": usage.document_pages_processed,
                "transcription_minutes": usage.transcription_minutes_used,
                "searches": usage.search_queries_made,
                "storage_mb": usage.storage_used_mb,
            },
            "limits": limits,
            "subscription_active": current_user.is_subscription_active,
        }
    )


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════════════════


@auth_bp.route("/admin/users")
@admin_required
def admin_users():
    """Admin dashboard - user management"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("auth/admin_users.html", users=users)


@auth_bp.route("/admin/user/<int:user_id>/toggle-active", methods=["POST"])
@admin_required
def admin_toggle_user_active(user_id):
    """Admin: Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()

    status = "activated" if user.is_active else "deactivated"
    flash(f"User {user.email} has been {status}.", "success")
    return redirect(url_for("auth.admin_users"))


@auth_bp.route("/admin/user/<int:user_id>/change-tier", methods=["POST"])
@admin_required
def admin_change_user_tier(user_id):
    """Admin: Change user tier"""
    user = User.query.get_or_404(user_id)
    new_tier = request.form.get("tier")

    if new_tier in [t.name for t in TierLevel]:
        user.tier = TierLevel[new_tier]
        db.session.commit()
        flash(f"User {user.email} tier changed to {new_tier}.", "success")
    else:
        flash("Invalid tier selected.", "danger")

    return redirect(url_for("auth.admin_users"))
