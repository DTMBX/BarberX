"""
Evident Flask App Configuration
Complete Flask setup with authentication and database
"""

import os
from dotenv import load_dotenv
from flask import Flask, render_template_string
from flask_login import LoginManager, current_user
from version import __version__ as APP_VERSION

# Load environment variables
load_dotenv()

# Configuration class
class Config:
    """Base configuration"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///Evident.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'dev-key-change-this-in-production'
    )
    
    # Session
    PERMANENT_SESSION_LIFETIME = 2592000  # 30 days
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Media Upload Configuration
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024 * 1024  # 3 GB for large BWC video files
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {
        'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv',  # Video
        'mp3', 'wav', 'flac', 'aac', 'wma', 'm4a',  # Audio
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff',  # Images
        'pdf',  # PDF
        'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'txt', 'rtf'  # Documents
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


# Configuration selection
config_name = os.environ.get('FLASK_ENV', 'development')
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
Config = config_map.get(config_name, DevelopmentConfig)


def create_app():
    """Application factory"""
    
    # Initialize Flask
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['APP_VERSION'] = APP_VERSION
    
    # Initialize database
    from auth.models import db
    db.init_app(app)
    
    # Initialize Alembic migrations via Flask-Migrate
    from flask_migrate import Migrate
    Migrate(app, db, directory='migrations')
    
    # Structured logging (must come before other init so they log properly)
    from services.structured_logging import init_logging
    init_logging(app)

    # Security hardening (headers, rate limits, session)
    from auth.security import init_security
    init_security(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '❌ Please log in to access this page'
    login_manager.login_message_category = 'danger'
    
    @login_manager.user_loader
    def load_user(user_id):
        from auth.models import User
        return User.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import redirect, url_for, flash
        flash('Please log in to continue', 'warning')
        return redirect(url_for('auth.login'))
    
    # Register blueprints
    from auth.routes import auth_bp
    from auth.admin_routes import admin_bp
    from routes.upload_routes import upload_bp
    from routes.legal_routes import legal_bp
    from api.legal_library_routes import legal_library_bp
    from routes.legal_admin import legal_admin_bp
    from routes.chat_routes import chat_bp
    from routes.chat_admin import chat_admin_bp
    from routes.nara_webhook import nara_bp
    from routes.case_routes import case_bp
    from routes.case_event_routes import case_event_bp
    
    # Health-check endpoints (no auth required)
    from routes.health import health_bp
    
    # Phase 7 — external trust & transparency (no auth on portal/transparency)
    from routes.share_routes import share_bp
    from routes.transparency import transparency_bp
    
    # Phase 8 — versioned REST API (Bearer-token auth)
    from routes.api_v1 import api_v1_bp
    
    # Phase 9 — document processing engine
    from routes.processing_routes import processing_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(legal_library_bp)
    app.register_blueprint(legal_admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(chat_admin_bp)
    app.register_blueprint(nara_bp)
    app.register_blueprint(case_event_bp)
    app.register_blueprint(case_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(transparency_bp)
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(processing_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - Page Not Found</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding: 50px; }
                h1 { color: #dc2626; }
                p { color: #666; }
                a { color: #0b73d2; text-decoration: none; }
            </style>
        </head>
        <body>
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/">← Back to home</a>
        </body>
        </html>
        '''), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>500 - Server Error</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding: 50px; }
                h1 { color: #dc2626; }
                p { color: #666; }
                a { color: #0b73d2; text-decoration: none; }
            </style>
        </head>
        <body>
            <h1>500 - Server Error</h1>
            <p>Something went wrong. Please try again later.</p>
            <a href="/">← Back to home</a>
        </body>
        </html>
        '''), 500
    
    # Routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                from flask import redirect, url_for
                return redirect(url_for('admin.dashboard'))
            else:
                from flask import redirect, url_for
                return redirect(url_for('chat'))  # Chat is main feature
        
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome - Evident</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #0b73d2 0%, #e07a5f 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    text-align: center;
                    color: white;
                    max-width: 500px;
                    padding: 2rem;
                }
                h1 { font-size: 3rem; margin-bottom: 0.5rem; }
                p { font-size: 1.25rem; margin-bottom: 2rem; opacity: 0.9; }
                .buttons {
                    display: flex;
                    gap: 1rem;
                    justify-content: center;
                }
                a { 
                    padding: 0.75rem 1.5rem;
                    border-radius: 0.375rem;
                    text-decoration: none;
                    font-weight: 600;
                    transition: all 0.2s ease;
                }
                .btn-login {
                    background: white;
                    color: #0b73d2;
                }
                .btn-login:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
                }
                .btn-register {
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: 2px solid white;
                }
                .btn-register:hover {
                    background: rgba(255,255,255,0.3);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Evident</h1>
                <p>Professional Evidence Management Platform</p>
                <div class="buttons">
                    <a href="/auth/login" class="btn-login">Sign In</a>
                    <a href="/auth/register" class="btn-register">Create Account</a>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    @app.route('/dashboard')
    def dashboard():
        from flask import render_template, redirect, url_for
        from flask_login import login_required, current_user
        
        @login_required
        def _dashboard():
            return render_template('dashboard.html', user=current_user)
        
        return _dashboard()
    
    @app.route('/chat')
    def chat():
        """Render chat interface (main feature of Evident)"""
        from flask import render_template
        from flask_login import login_required
        
        @login_required
        def _chat():
            return render_template('chat/chat_interface.html')
        
        return _chat()
    
    # CLI Commands
    @app.cli.command('init-db')
    def init_db():
        """Initialize database"""
        with app.app_context():
            db.create_all()
            print('✅ Database initialized')
    
    @app.cli.command('create-admin')
    def create_admin():
        """Create admin user"""
        from auth.models import User, UserRole, TierLevel
        import getpass
        
        with app.app_context():
            email = input('Admin email: ')
            username = input('Admin username: ')
            full_name = input('Admin full name: ')
            password = getpass.getpass('Admin password: ')
            
            admin = User.query.filter_by(email=email).first()
            if admin:
                print(f'❌ Admin with email {email} already exists')
                return
            
            admin = User(
                email=email,
                username=username,
                full_name=full_name,
                role=UserRole.ADMIN,
                tier=TierLevel.ADMIN,
                is_verified=True,
                is_active=True,
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            print(f'✅ Admin user created: {email}')
    
    @app.cli.command('list-users')
    def list_users():
        """List all users"""
        from auth.models import User
        
        with app.app_context():
            users = User.query.all()
            print(f'\n{"Email":<30} {"Name":<20} {"Role":<15} {"Tier":<12}')
            print('=' * 77)
            for user in users:
                print(f'{user.email:<30} {user.full_name:<20} {user.role.value:<15} {user.tier.value:<12}')
            print(f'\nTotal users: {len(users)}\n')
    
    @app.cli.command('init-legal-library')
    def init_legal_library():
        """Initialize legal library with founding documents and landmark cases"""
        from auth.legal_library_importer import init_legal_library
        
        with app.app_context():
            init_legal_library()
            print('✅ Legal library initialized with founding documents and landmark cases')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
