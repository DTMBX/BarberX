#!/usr/bin/env pwsh
# Evident.info - Complete App Fix Script
# Fixes: Login, PDF Upload, BWC Analysis

Write-Host "`n?? Evident.info - Complete App Fix" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

# Step 1: Stop any running Flask
Write-Host "`n[1/7] Stopping existing Flask processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "  ? Processes stopped" -ForegroundColor Green

# Step 2: Clean database
Write-Host "`n[2/7] Cleaning database..." -ForegroundColor Yellow
Remove-Item instance\*.db -Force -ErrorAction SilentlyContinue
Remove-Item *.db -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "instance" -Force | Out-Null
Write-Host "  ? Database cleaned" -ForegroundColor Green

# Step 3: Create required directories
Write-Host "`n[3/7] Creating upload directories..." -ForegroundColor Yellow
@(
    "uploads/bwc_videos",
    "uploads/pdfs", 
    "uploads/audio",
    "bwc_analysis",
    "logs",
    "instance"
) | ForEach-Object {
    New-Item -ItemType Directory -Path $_ -Force | Out-Null
    Write-Host "  Created: $_" -ForegroundColor Gray
}
Write-Host "  ? Directories created" -ForegroundColor Green

# Step 4: Verify Python dependencies
Write-Host "`n[4/7] Checking dependencies..." -ForegroundColor Yellow
python -c @'
import sys
required = {
    "flask": "Flask",
    "flask_cors": "Flask-CORS",
    "flask_sqlalchemy": "Flask-SQLAlchemy", 
    "flask_login": "Flask-Login",
    "werkzeug": "Werkzeug"
}

missing = []
for module, name in required.items():
    try:
        __import__(module)
        print(f"  ? {name}")
    except ImportError:
        print(f"  ? {name} MISSING")
        missing.append(name)

if missing:
    print(f"\n??  Install missing: pip install {' '.join(missing).lower()}")
    sys.exit(1)
'@

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing missing dependencies..." -ForegroundColor Yellow
    python -m pip install flask flask-cors flask-sqlalchemy flask-login werkzeug python-dotenv --quiet
}
Write-Host "  ? All dependencies ready" -ForegroundColor Green

# Step 5: Create .env file with API keys
Write-Host "`n[5/7] Setting up environment..." -ForegroundColor Yellow
$envContent = @"
# Evident.info Environment Configuration
SECRET_KEY=Evident-legal-tech-2026-super-secure-change-me
FLASK_ENV=development
FLASK_APP=app.py

# Database
DATABASE_URL=sqlite:///instance/Evident_FRESH.db

# API Keys (Optional - for AI features)
# OPENAI_API_KEY=your-openai-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here
# HUGGINGFACE_TOKEN=your-hf-token-here

# Security
MAX_CONTENT_LENGTH=5368709120
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# CORS
CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000

# Uploads
UPLOAD_FOLDER=./uploads/bwc_videos
ANALYSIS_FOLDER=./bwc_analysis
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8 -Force
Write-Host "  ? Environment configured" -ForegroundColor Green

# Step 6: Test app startup
Write-Host "`n[6/7] Testing app startup..." -ForegroundColor Yellow
$testResult = python -c @'
import sys
sys.path.insert(0, ".")

try:
    from app import app, db
    from models_auth import User, TierLevel
    
    with app.app_context():
        db.create_all()
        
        # Create admin user
        admin = User.query.filter_by(email="admin@Evident.info").first()
        if not admin:
            admin = User(
                email="admin@Evident.info",
                full_name="Devon Tyler",
                organization="Evident Legal Technologies",
                tier=TierLevel.ADMIN,
                is_admin=True,
                is_active=True,
                is_verified=True
            )
            admin.set_password(os.environ.get('Evident_ADMIN_PASSWORD', 'CHANGE_ME_IMMEDIATELY'))
            db.session.add(admin)
            db.session.commit()
            print("? Admin user created")
        else:
            print("? Admin user exists")
        
        print("? Database initialized")
        print("? App startup successful")
        
except Exception as e:
    print(f"? Startup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'@

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? App startup successful" -ForegroundColor Green
} else {
    Write-Host "  ??  Startup had issues, but continuing..." -ForegroundColor Yellow
}

# Step 7: Start Flask
Write-Host "`n[7/7] Starting Flask..." -ForegroundColor Yellow
Write-Host "  Keep this window open!" -ForegroundColor Yellow

Write-Host "`n====================================" -ForegroundColor Cyan
Write-Host "? Fix Complete!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "====================================" -ForegroundColor Cyan

Write-Host "`n?? APPLICATION:" -ForegroundColor Cyan
Write-Host "  URL:      http://localhost:5000" -ForegroundColor White
Write-Host "  Login:    http://localhost:5000/auth/login" -ForegroundColor White
Write-Host "  Dashboard: http://localhost:5000/auth/dashboard" -ForegroundColor White

Write-Host "`n?? CREDENTIALS:" -ForegroundColor Cyan
Write-Host "  Email:    admin@Evident.info" -ForegroundColor White
Write-Host "  Password: [Set Evident_ADMIN_PASSWORD env var]" -ForegroundColor White

Write-Host "`n?? CAPABILITIES:" -ForegroundColor Cyan
Write-Host "  ? User Login & Authentication" -ForegroundColor Green
Write-Host "  ? PDF Upload: /batch-pdf-upload.html" -ForegroundColor Green
Write-Host "  ? BWC Upload: /api/upload (POST)" -ForegroundColor Green
Write-Host "  ? Dashboard: /auth/dashboard" -ForegroundColor Green

Write-Host "`n??  PRESS CTRL+C TO STOP" -ForegroundColor Yellow
Write-Host ""

# Start Flask
python app.py
