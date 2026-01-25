#!/usr/bin/env pwsh
# Fix Python indentation in app.py

$appPy = "app.py"

Write-Host "?? Fixing Python indentation in app.py..." -ForegroundColor Cyan

# Read the entire file
$content = Get-Content $appPy -Raw

# Fix User class - Replace lines 127-145 with properly indented version
$content = $content -replace `
    'class User\(UserMixin, db\.Model\):\s*\n"""User model for authentication and authorization"""\s*\n__tablename__ = ''users''\s*\n__table_args__ = \{''extend_existing'': True\}[^#]*?# Relationships', `
    @'
class User(UserMixin, db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(200))
    role = db.Column(db.String(20), default='user')  # user, pro, admin
    subscription_tier = db.Column(db.String(20), default='free')  # free, professional, enterprise
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
'@

# Save the file
$content | Set-Content $appPy -NoNewline -Encoding UTF8

Write-Host "? Fixed! Now run: python app.py" -ForegroundColor Green
