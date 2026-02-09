#!/bin/bash
# Evident Platform - Setup Script (macOS/Linux)
# Complete setup of the Evident authentication and dashboard system

set -e

echo ""
echo "$(tput bold)$(tput setaf 6)======================================================$(tput sgr0)"
echo "$(tput bold)$(tput setaf 2)🚀 EVIDENT PLATFORM - SETUP$(tput sgr0)"
echo "$(tput bold)$(tput setaf 6)======================================================$(tput sgr0)"

# Check Python
echo ""
echo "$(tput setaf 3)[1/5] Checking Python installation...$(tput sgr0)"

if ! command -v python3 &> /dev/null; then
    echo "$(tput setaf 1)❌ Python 3 not found. Please install Python 3.9+$(tput sgr0)"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "$(tput setaf 2)✅ Found: $PYTHON_VERSION$(tput sgr0)"

# Install dependencies
echo ""
echo "$(tput setaf 3)[2/5] Installing dependencies...$(tput sgr0)"

DEPS=(
    "flask-login"
    "flask-sqlalchemy"
    "email-validator"
    "python-dotenv"
)

for dep in "${DEPS[@]}"; do
    echo "$(tput setaf 8)  Installing $dep...$(tput sgr0)"
    pip3 install "$dep" --quiet
done

echo "$(tput setaf 2)✅ Dependencies installed$(tput sgr0)"

# Check Flask
echo ""
echo "$(tput setaf 3)[3/5] Checking Flask configuration...$(tput sgr0)"

if [ -f ".env" ]; then
    echo "$(tput setaf 2)✅ .env file exists$(tput sgr0)"
else
    echo "$(tput setaf 8)  Creating .env file...$(tput sgr0)"
    cat > .env << 'EOF'
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///Evident.db

# Security (CHANGE THIS IN PRODUCTION)
SECRET_KEY=dev-secret-key-change-in-production

# Email Configuration (Optional)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-password
EOF
    echo "$(tput setaf 2)✅ .env file created$(tput sgr0)"
fi

# Initialize database
echo ""
echo "$(tput setaf 3)[4/5] Initializing database...$(tput sgr0)"

python3 -m flask init-db 2>&1 || true
echo "$(tput setaf 2)✅ Database initialized$(tput sgr0)"

# Create admin user
echo ""
echo "$(tput setaf 3)[5/5] Admin user setup...$(tput sgr0)"

if [ "$1" = "-create-admin" ]; then
    echo "$(tput setaf 8)  Starting admin creation wizard...$(tput sgr0)"
    python3 -m flask create-admin
    echo "$(tput setaf 2)✅ Admin user created$(tput sgr0)"
else
    echo "$(tput setaf 8)  Run 'flask create-admin' to create an admin account$(tput sgr0)"
    echo "$(tput setaf 8)  Or run this script with -create-admin flag$(tput sgr0)"
fi

# Summary
echo ""
echo "$(tput bold)$(tput setaf 6)======================================================$(tput sgr0)"
echo "$(tput bold)$(tput setaf 2)✅ SETUP COMPLETE!$(tput sgr0)"
echo "$(tput bold)$(tput setaf 6)======================================================$(tput sgr0)"

echo ""
echo "$(tput bold)$(tput setaf 6)📍 Start Development Server:$(tput sgr0)"
echo "  python3 app.py"
echo "  or"
echo "  flask run"

echo ""
echo "$(tput bold)$(tput setaf 6)📍 Access Application:$(tput sgr0)"
echo "  🏠 Home:      http://localhost:5000/"
echo "  🔐 Login:     http://localhost:5000/auth/login"
echo "  📝 Register:  http://localhost:5000/auth/register"
echo "  📊 Dashboard: http://localhost:5000/dashboard"
echo "  ⚙️  Admin:     http://localhost:5000/admin/"

echo ""
echo "$(tput bold)$(tput setaf 6)📚 Next Steps:$(tput sgr0)"
echo "  1. Run 'python3 app.py' to start the server"
echo "  2. Visit http://localhost:5000/auth/register to create a user"
echo "  3. Or create admin with 'flask create-admin'"
echo "  4. Check docs/AUTH_SYSTEM.md for full documentation"

echo ""
echo "$(tput bold)$(tput setaf 6)======================================================$(tput sgr0)"
echo ""
