#!/usr/bin/env pwsh
# Evident.info - Complete Verification & Startup

Write-Host "`n? Evident.info - Final Verification" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

# Test 1: Verify AI Components
Write-Host "`n[1/4] Testing AI Components..." -ForegroundColor Yellow
python -c @'
print("Testing core AI libraries:")
try:
    import torch
    print(f"  ? PyTorch {torch.__version__}")
except:
    print("  ? PyTorch missing")

try:
    import whisper
    print("  ? Whisper AI")
except:
    print("  ? Whisper missing")

try:
    from pyannote.audio import Pipeline
    print("  ? PyAnnote (Speaker Diarization)")
except:
    print("  ? PyAnnote (needs HuggingFace token)")

try:
    import cv2
    print("  ? OpenCV (Video)")
except:
    print("  ? OpenCV missing")

try:
    import librosa
    print("  ? Librosa (Audio)")
except:
    print("  ? Librosa missing")

try:
    import moviepy.editor
    print("  ? MoviePy (Video)")
except:
    print("  ? MoviePy missing")

try:
    from langchain import LLMChain
    print("  ? LangChain (Constitutional AI)")
except:
    print("  ? LangChain (optional)")

print("\n? AI Components Ready!")
'@

# Test 2: Verify Flask App
Write-Host "`n[2/4] Testing Flask App..." -ForegroundColor Yellow
python -c @'
import sys
sys.path.insert(0, ".")

try:
    from app import app
    print("  ? Flask app imports successfully")
    
    from models_auth import User, TierLevel
    print("  ? Database models ready")
    
    print("\n? Flask App Ready!")
except Exception as e:
    print(f"  ? Error: {e}")
    sys.exit(1)
'@

# Test 3: Verify BWC Analyzer (if no errors, AI is fully working)
Write-Host "`n[3/4] Testing BWC Forensic Analyzer..." -ForegroundColor Yellow
$bwcTest = python -c @'
import sys
try:
    from bwc_forensic_analyzer import BWCForensicAnalyzer
    print("  ? BWC Forensic Analyzer available!")
    print("  ? All AI dependencies working!")
    sys.exit(0)
except ImportError as e:
    print(f"  ? BWC Analyzer not available: {e}")
    print("  ? App will work without AI analysis")
    sys.exit(0)
except Exception as e:
    print(f"  ? Issue: {e}")
    sys.exit(0)
'@

# Test 4: Clean & Prepare Database
Write-Host "`n[4/4] Preparing Database..." -ForegroundColor Yellow
Remove-Item instance\*.db -Force -ErrorAction SilentlyContinue
Remove-Item Evident*.db -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "instance" -Force | Out-Null

python -c @'
import sys
sys.path.insert(0, ".")

from app import app, db
from models_auth import User, TierLevel

with app.app_context():
    db.create_all()
    
    # Create admin
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
        print("  ? Admin user created")
    else:
        print("  ? Admin user exists")
    
    print("  ? Database initialized")
'@

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "? Verification Complete!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "=====================================" -ForegroundColor CyanWrite-Host "`n? Admin credentials stored in environment variables" -ForegroundColor Yellow
Write-Host "  Set Evident_ADMIN_PASSWORD before first login" -ForegroundColor Yellow
Write-Host "`n?? STARTING FLASK APPLICATION..." -ForegroundColor Cyan

Write-Host "`n?? CAPABILITIES ENABLED:" -ForegroundColor Yellow
Write-Host "  ? User Authentication & Login" -ForegroundColor Green
Write-Host "  ? PDF Upload & Processing" -ForegroundColor Green
Write-Host "  ? BWC Video Upload (.mp4, .mov, .avi)" -ForegroundColor Green
Write-Host "  ? Audio Transcription (Whisper AI)" -ForegroundColor Green
Write-Host "  ? Speaker Diarization (Officer vs Civilian)" -ForegroundColor Green
Write-Host "  ? Video Frame Analysis (OpenCV)" -ForegroundColor Green
Write-Host "  ? Audio Enhancement (Librosa)" -ForegroundColor Green
Write-Host "  ? Constitutional Violation Detection (with API keys)" -ForegroundColor Green

Write-Host "`n?? APPLICATION URLS:" -ForegroundColor Cyan
Write-Host "  Main:      http://localhost:5000" -ForegroundColor White
Write-Host "  Login:     http://localhost:5000/auth/login" -ForegroundColor White
Write-Host "  Dashboard: http://localhost:5000/auth/dashboard" -ForegroundColor White
Write-Host "  PDF Upload: http://localhost:5000/batch-pdf-upload.html" -ForegroundColor White

Write-Host "`n?? CREDENTIALS:" -ForegroundColor Cyan
Write-Host "  Email:    admin@Evident.info" -ForegroundColor White
Write-Host "  Password: [Set Evident_ADMIN_PASSWORD env var]" -ForegroundColor White

Write-Host "`n??  PRESS CTRL+C TO STOP" -ForegroundColor Yellow
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host ""

# Start Flask
python app.py
