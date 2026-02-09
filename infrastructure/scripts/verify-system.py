#!/usr/bin/env python3
"""
Evident Platform - System Verification Utility
Checks if the authentication system is properly configured and ready to run
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_check(status, message):
    """Print a check result"""
    icon = "✅" if status else "❌"
    print(f"  {icon} {message}")

def print_info(message):
    """Print informational message"""
    print(f"  ℹ️  {message}")

def check_python():
    """Check Python version"""
    print("\n📋 Python Configuration")
    print_check(True, f"Python version: {sys.version.split()[0]}")
    
    if sys.version_info < (3, 9):
        print_check(False, f"Python 3.9+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
        return False
    return True

def check_dependencies():
    """Check required Python packages"""
    print("\n📦 Required Dependencies")
    
    required = {
        'flask': 'Flask',
        'flask_login': 'Flask-Login',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'email_validator': 'Email-Validator',
        'dotenv': 'Python-Dotenv',
    }
    
    all_ok = True
    for module, name in required.items():
        try:
            __import__(module)
            print_check(True, f"{name}: installed")
        except ImportError:
            print_check(False, f"{name}: NOT installed")
            all_ok = False
    
    return all_ok

def check_files():
    """Check required files exist"""
    print("\n📁 Required Files")
    
    root = Path.cwd()
    files_to_check = {
        'app.py': 'Flask entry point',
        'wsgi.py': 'WSGI production entry',
        'app_config.py': 'Flask configuration',
        'auth/__init__.py': 'Auth package',
        'auth/models.py': 'Database models',
        'auth/routes.py': 'Authentication routes',
        'auth/admin_routes.py': 'Admin routes',
        'templates/auth/login.html': 'Login template',
        '.env': 'Environment configuration',
    }
    
    all_ok = True
    for filepath, description in files_to_check.items():
        exists = (root / filepath).exists()
        print_check(exists, f"{filepath}: {description}")
        if not exists:
            all_ok = False
    
    return all_ok

def check_env():
    """Check .env file configuration"""
    print("\n⚙️  Environment Configuration")
    
    env_file = Path.cwd() / '.env'
    
    if not env_file.exists():
        print_check(False, ".env file not found")
        print_info("Run 'setup.bat', './setup.ps1', or './setup.sh' to create it")
        return False
    
    print_check(True, ".env file exists")
    
    required_keys = ['FLASK_APP', 'SECRET_KEY', 'SQLALCHEMY_DATABASE_URI']
    
    with open(env_file) as f:
        env_content = f.read()
    
    all_ok = True
    for key in required_keys:
        has_key = key in env_content and f"\n{key}=" in env_content
        print_check(has_key, f"{key}: configured" if has_key else f"{key}: NOT configured")
        if not has_key:
            all_ok = False
    
    return all_ok

def check_database():
    """Check database configuration"""
    print("\n🗄️  Database Status")
    
    db_file = Path.cwd() / 'Evident.db'
    
    if db_file.exists():
        size_mb = db_file.stat().st_size / (1024 * 1024)
        print_check(True, f"Database exists (Evident.db, {size_mb:.2f} MB)")
        return True
    else:
        print_info("Database not initialized (run 'flask init-db')")
        return False

def check_flask_cli():
    """Check Flask CLI is working"""
    print("\n🔧 Flask CLI Status")
    
    try:
        result = subprocess.run(
            ['flask', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_check(True, f"Flask CLI: {result.stdout.strip()}")
            return True
    except Exception as e:
        print_check(False, f"Flask CLI error: {str(e)}")
        return False

def check_users():
    """Check if admin user exists"""
    print("\n👥 User Accounts")
    
    db_file = Path.cwd() / 'Evident.db'
    
    if not db_file.exists():
        print_info("Database not initialized yet")
        return False
    
    try:
        result = subprocess.run(
            ['flask', 'list-users'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if 'No users found' in result.stdout or len(lines) < 2:
                print_info("No users in database (create with 'flask create-admin')")
                return False
            else:
                print_check(True, f"Users found: {len(lines) - 1} accounts")
                return True
    except Exception as e:
        print_info(f"Could not check users: {str(e)}")
        return False

def print_summary(results):
    """Print summary and recommendations"""
    print_header("Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    pct = (passed / total * 100) if total > 0 else 0
    
    print(f"  Status: {passed}/{total} checks passed ({pct:.0f}%)\n")
    
    if passed == total:
        print("  🎉 Everything looks good! You're ready to run:")
        print("     python app.py")
        print("\n  Then visit: http://localhost:5000/")
        return True
    else:
        print("  ⚠️  Fix the issues above before running the server\n")
        print("  Quick setup:")
        print("    Windows:  setup.bat")
        print("    Linux:    ./setup.sh")
        print("    macOS:    ./setup.sh")
        return False

def main():
    """Run all checks"""
    print_header("Evident Platform - System Verification")
    
    results = {
        'Python': check_python(),
        'Dependencies': check_dependencies(),
        'Files': check_files(),
        'Environment': check_env(),
        'Database': check_database(),
        'Flask CLI': check_flask_cli(),
        'Users': check_users(),
    }
    
    success = print_summary(results)
    
    print("\n" + "="*60 + "\n")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
