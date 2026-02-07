# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Flask App Integration Script
Merges enhanced auth system with existing app.py
"""

import os
import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent


def backup_existing():
    """Backup current app.py"""
    app_path = project_root / "app.py"
    backup_path = project_root / "app.py.backup"

    if app_path.exists() and not backup_path.exists():
        import shutil

        shutil.copy(app_path, backup_path)
        print("✅ Backed up app.py to app.py.backup")
        return True
    elif backup_path.exists():
        print("⚠️  Backup already exists: app.py.backup")
        return False
    return False


def integrate_auth_routes():
    """Add auth blueprint registration to app.py"""

    additions = """
# ========================================
# ENHANCED AUTHENTICATION SYSTEM
# ========================================

# Import enhanced models and routes
try:
    from models_auth import UsageTracking, ApiKey
    from auth_routes import auth_bp
    
    # Register authentication blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    print("✅ Enhanced authentication system loaded")
    ENHANCED_AUTH = True
except ImportError as e:
    print(f"⚠️  Enhanced auth not available: {e}")
    ENHANCED_AUTH = False

# Enhanced dashboard with usage tracking
@app.route('/dashboard/enhanced')
@login_required
def dashboard_enhanced():
    '''Enhanced dashboard with usage stats'''
    if ENHANCED_AUTH:
        usage = UsageTracking.get_or_create_current(current_user.id)
        limits = current_user.get_tier_limits()
        return render_template('auth/dashboard.html', 
                             user=current_user,
                             usage=usage,
                             limits=limits)
    else:
        return redirect(url_for('dashboard'))
"""

    print("\n📋 Integration Code:")
    print("=" * 60)
    print(additions)
    print("=" * 60)

    return additions


def show_integration_steps():
    """Display manual integration steps"""

    print("\n" + "=" * 70)
    print("  Evident Flask Integration Guide")
    print("=" * 70 + "\n")

    print("📝 MANUAL INTEGRATION STEPS:\n")

    print("1️⃣  Add imports at the top of app.py (after line 19):")
    print("-" * 60)
    print(
        """
from models_auth import UsageTracking, ApiKey, TierLevel
from auth_routes import auth_bp
"""
    )

    print("\n2️⃣  Register auth blueprint (after line 48):")
    print("-" * 60)
    print(
        """
# Register enhanced authentication blueprint
try:
    app.register_blueprint(auth_bp, url_prefix='/auth')
    print("✅ Enhanced auth routes registered at /auth/*")
except Exception as e:
    print(f"⚠️  Auth blueprint registration failed: {e}")
"""
    )

    print("\n3️⃣  Update dashboard route (replace line 436-440):")
    print("-" * 60)
    print(
        """
@app.route('/dashboard')
@login_required
def dashboard():
    '''User dashboard with usage tracking'''
    try:
        from models_auth import UsageTracking
        usage = UsageTracking.get_or_create_current(current_user.id)
        limits = current_user.get_tier_limits()
        return render_template('auth/dashboard.html',
                             user=current_user,
                             usage=usage,
                             limits=limits)
    except ImportError:
        # Fallback to basic dashboard
        return send_file('templates/dashboard.html')
"""
    )

    print("\n4️⃣  Update login route to use enhanced template (line 396-424):")
    print("-" * 60)
    print(
        """
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''User login - redirect to enhanced auth'''
    return redirect(url_for('auth.login'))
"""
    )

    print("\n5️⃣  Update register route (line 354-393):")
    print("-" * 60)
    print(
        """
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''User registration - redirect to enhanced signup'''
    return redirect(url_for('auth.signup'))
"""
    )

    print("\n6️⃣  Add database path configuration (after line 33):")
    print("-" * 60)
    print(
        """
# Use absolute path for database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{os.path.join(basedir, "instance", "Evident_auth.db")}'
)
"""
    )

    print("\n7️⃣  Initialize database tables (before if __name__ block):")
    print("-" * 60)
    print(
        """
# Initialize database
with app.app_context():
    db.create_all()
    print("✅ Database tables created")
"""
    )

    print("\n" + "=" * 70)
    print("  Quick Integration (Copy/Paste)")
    print("=" * 70 + "\n")

    print("🚀 AUTOMATED INTEGRATION:\n")
    print("Run this in Python console:")
    print("-" * 60)
    print(
        """
# Quick integration script
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Update database path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "Evident_auth.db")}'

# Import and register
from models_auth import UsageTracking, ApiKey
from auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

# Initialize database
with app.app_context():
    db.create_all()
    
print("✅ Integration complete!")
print("🌐 Enhanced auth available at:")
print("   /auth/login")
print("   /auth/signup") 
print("   /auth/logout")
print("   /dashboard (enhanced)")
"""
    )

    print("\n" + "=" * 70)
    print("  Testing")
    print("=" * 70 + "\n")

    print("🧪 TEST THE INTEGRATION:\n")
    print("1. Start Flask app:")
    print("   python app.py")
    print("\n2. Visit routes:")
    print("   http://localhost:5000/auth/signup")
    print("   http://localhost:5000/auth/login")
    print("   http://localhost:5000/dashboard")
    print("\n3. Login with admin account:")
    print("   Email: dTb33@pm.me")
    print("   Password: LoveAll33!")

    print("\n" + "=" * 70 + "\n")


def check_prerequisites():
    """Check if required files exist"""
    print("\n🔍 Checking prerequisites...\n")

    required_files = {
        "models_auth.py": "Enhanced user models",
        "auth_routes.py": "Authentication routes",
        "init_auth.py": "Database initializer",
        "templates/auth/login.html": "Login template",
        "templates/auth/signup.html": "Signup template",
        "templates/auth/dashboard.html": "Dashboard template",
    }

    all_present = True

    for file, description in required_files.items():
        file_path = project_root / file
        if file_path.exists():
            print(f"✅ {file:<35} ({description})")
        else:
            print(f"❌ {file:<35} MISSING!")
            all_present = False

    print()

    if all_present:
        print("✅ All required files present!\n")
        return True
    else:
        print("❌ Some required files are missing. Please create them first.\n")
        return False


def main():
    """Main integration process"""

    print(
        """
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║    Evident Enhanced Authentication Integration        ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    """
    )

    # Check prerequisites
    if not check_prerequisites():
        print("⚠️  Cannot proceed without required files.")
        print("📖 See docs/FLASK-INTEGRATION-GUIDE.md for details")
        return

    # Backup existing app
    print("📦 Creating backup...")
    backup_existing()

    # Show integration steps
    show_integration_steps()

    print("\n💡 RECOMMENDATION:")
    print("   Follow the manual integration steps above")
    print("   This ensures you understand each change")
    print("   and can customize as needed.")

    print("\n📖 Full documentation:")
    print("   docs/FLASK-INTEGRATION-GUIDE.md")

    print("\n✨ After integration:")
    print("   1. Run: python init_auth.py")
    print("   2. Run: python app.py")
    print("   3. Test: http://localhost:5000/auth/signup")

    print("\n💈✂️ Like a fresh NYC fade — clean integration!\n")


if __name__ == "__main__":
    main()
