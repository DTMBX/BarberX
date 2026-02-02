# Evident - Start Application
# Quick startup script for development

Write-Host "`n=== Evident Legal Tech Platform ===" -ForegroundColor Cyan
Write-Host "Starting application..." -ForegroundColor Green

# Set environment
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

# Check database exists
if (-not (Test-Path "instance\Evident_FRESH.db")) {
    Write-Host "⚠ Database not found, creating..." -ForegroundColor Yellow
    python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ Database created')"
}

# Verify test users exist
Write-Host "`nVerifying test users..." -ForegroundColor Cyan
python -c "
from app import app
from models_auth import db, User, TierLevel

with app.app_context():
    # Check admin
    admin = User.query.filter_by(email='admin@Evident.info').first()
    if admin:
        print('✓ Admin user exists: admin@Evident.info')
        admin.set_password('Admin123!')
        db.session.commit()
        print('  Password reset to: Admin123!')
    
    # Check test user
    test = User.query.filter_by(email='test@Evident.info').first()
    if not test:
        test = User(
            email='test@Evident.info',
            full_name='Test User',
            tier=TierLevel.FREE,
            is_active=True
        )
        test.set_password('Password123!')
        db.session.add(test)
        db.session.commit()
        print('✓ Test user created: test@Evident.info / Password123!')
    else:
        print('✓ Test user exists: test@Evident.info')
        test.set_password('Password123!')
        db.session.commit()
        print('  Password reset to: Password123!')
"

Write-Host "`n=== Login Credentials ===" -ForegroundColor Green
Write-Host "  Admin:     admin@Evident.info / Admin123!" -ForegroundColor Yellow
Write-Host "  Test User: test@Evident.info / Password123!" -ForegroundColor Yellow

Write-Host "`n=== Starting Flask Server ===" -ForegroundColor Cyan
Write-Host "  URL: http://localhost:5000" -ForegroundColor White
Write-Host "  Login: http://localhost:5000/auth/login" -ForegroundColor White
Write-Host "`n  Press Ctrl+C to stop`n" -ForegroundColor Gray

# Start Flask
python app.py
