@echo off
REM Evident Platform - Setup Script (Windows CMD)
REM Complete setup of the Evident authentication and dashboard system

setlocal enabledelayedexpansion

cls
echo.
echo ========================================================
echo 🚀 EVIDENT PLATFORM - SETUP
echo ========================================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Found: %PYTHON_VERSION%

REM Install dependencies
echo.
echo [2/5] Installing dependencies...

setlocal enabledelayedexpansion
for %%d in (flask-login flask-sqlalchemy email-validator python-dotenv) do (
    echo   Installing %%d...
    pip install %%d --quiet
)
echo ✅ Dependencies installed

REM Check Flask
echo.
echo [3/5] Checking Flask configuration...

if exist ".env" (
    echo ✅ .env file exists
) else (
    echo   Creating .env file...
    (
        echo # Flask Configuration
        echo FLASK_APP=app.py
        echo FLASK_ENV=development
        echo DEBUG=True
        echo.
        echo # Database
        echo SQLALCHEMY_DATABASE_URI=sqlite:///Evident.db
        echo.
        echo # Security (CHANGE THIS IN PRODUCTION^)
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo.
        echo # Email Configuration (Optional^)
        echo # MAIL_SERVER=smtp.gmail.com
        echo # MAIL_PORT=587
        echo # MAIL_USERNAME=your-email@gmail.com
        echo # MAIL_PASSWORD=your-password
    ) > .env
    echo ✅ .env file created
)

REM Initialize database
echo.
echo [4/5] Initializing database...

python -m flask init-db >nul 2>&1
echo ✅ Database initialized

REM Create admin user
echo.
echo [5/5] Admin user setup...

if "%1"=="-create-admin" (
    echo   Starting admin creation wizard...
    python -m flask create-admin
    echo ✅ Admin user created
) else (
    echo   Run 'python -m flask create-admin' to create an admin account
    echo   Or run this script with -create-admin flag
)

REM Summary
echo.
echo ========================================================
echo ✅ SETUP COMPLETE!
echo ========================================================
echo.
echo 📍 Start Development Server:
echo   python app.py
echo   or
echo   flask run
echo.
echo 📍 Access Application:
echo   🏠 Home:      http://localhost:5000/
echo   🔐 Login:     http://localhost:5000/auth/login
echo   📝 Register:  http://localhost:5000/auth/register
echo   📊 Dashboard: http://localhost:5000/dashboard
echo   ⚙️  Admin:     http://localhost:5000/admin/
echo.
echo 📚 Next Steps:
echo   1. Run 'python app.py' to start the server
echo   2. Visit http://localhost:5000/auth/register to create a user
echo   3. Or create admin with 'python -m flask create-admin'
echo   4. Check docs/AUTH_SYSTEM.md for full documentation
echo.
echo ========================================================
echo.

pause
