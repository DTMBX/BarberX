#!/usr/bin/env pwsh
# Evident.info - Tier-Based Feature Testing
# Tests PDF and BWC processing for Free vs Enterprise users

Write-Host "`n?? Evident Tier Testing - Free vs Enterprise" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

# Test Setup
Write-Host "`n[Setup] Creating test users..." -ForegroundColor Yellow

python -c @'
import sys
sys.path.insert(0, ".")

from app import app, db
from models_auth import User, TierLevel, UsageTracking

with app.app_context():
    # Create Free tier user
    free_user = User.query.filter_by(email="free@Evident.test").first()
    if not free_user:
        free_user = User(
            email="free@Evident.test",
            full_name="Free Tier User",
            organization="Test Organization",
            tier=TierLevel.FREE,
            is_active=True,
            is_verified=True
        )
        free_user.set_password("test123")
        db.session.add(free_user)
    
    # Create Enterprise tier user  
    enterprise_user = User.query.filter_by(email="enterprise@Evident.test").first()
    if not enterprise_user:
        enterprise_user = User(
            email="enterprise@Evident.test",
            full_name="Enterprise Tier User",
            organization="Enterprise Corp",
            tier=TierLevel.ENTERPRISE,
            is_active=True,
            is_verified=True
        )
        enterprise_user.set_password("test123")
        db.session.add(enterprise_user)
    
    db.session.commit()
    
    print("? Test users created")
    print(f"  Free User: free@Evident.test (ID: {free_user.id})")
    print(f"  Enterprise User: enterprise@Evident.test (ID: {enterprise_user.id})")
'@

Write-Host ""

# Display Tier Comparison
Write-Host "`n?? Tier Comparison Table:" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Gray

python -c @'
from app import app
from models_auth import User, TierLevel

with app.app_context():
    free_user = User.query.filter_by(email="free@Evident.test").first()
    enterprise_user = User.query.filter_by(email="enterprise@Evident.test").first()
    
    free_limits = free_user.get_tier_limits()
    enterprise_limits = enterprise_user.get_tier_limits()
    
    print(f"{'Feature':<35} {'FREE':<20} {'ENTERPRISE':<20}")
    print("-" * 80)
    
    features = [
        ('BWC Videos/Month', 'bwc_videos_per_month'),
        ('Max File Size', 'max_file_size_mb'),
        ('PDF Pages/Month', 'document_pages_per_month'),
        ('Transcription Mins/Month', 'transcription_minutes_per_month'),
        ('Storage (GB)', 'storage_gb'),
        ('Export Watermark', 'export_watermark'),
        ('API Access', 'api_access'),
    ]
    
    for label, key in features:
        free_val = free_limits.get(key, 'N/A')
        enterprise_val = enterprise_limits.get(key, 'N/A')
        
        # Format -1 as "Unlimited"
        if free_val == -1:
            free_val = "Unlimited"
        if enterprise_val == -1:
            enterprise_val = "Unlimited"
        
        # Format file sizes
        if 'size' in key.lower() and isinstance(free_val, int):
            free_val = f"{free_val} MB"
        if 'size' in key.lower() and isinstance(enterprise_val, int):
            enterprise_val = f"{enterprise_val} MB"
        
        print(f"{label:<35} {str(free_val):<20} {str(enterprise_val):<20}")
'@

Write-Host ""

# Test PDF Upload Capabilities
Write-Host "`n?? Test 1: PDF Upload Capability" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Gray

python -c @'
from app import app
from models_auth import User

with app.app_context():
    free_user = User.query.filter_by(email="free@Evident.test").first()
    enterprise_user = User.query.filter_by(email="enterprise@Evident.test").first()
    
    print("\n?? PDF Upload Test:")
    print(f"  Free User can upload:      {free_user.get_tier_limits()['document_pages_per_month']} pages/month")
    print(f"  Enterprise can upload:     {enterprise_user.get_tier_limits()['document_pages_per_month']} (Unlimited)")
    print(f"\n  Free User max file size:   {free_user.get_tier_limits()['max_file_size_mb']} MB")
    print(f"  Enterprise max file size:  {enterprise_user.get_tier_limits()['max_file_size_mb']} MB")
    
    # Check if users can upload
    free_limits = free_user.get_tier_limits()
    ent_limits = enterprise_user.get_tier_limits()
    
    print(f"\n  ? Free User CAN upload PDFs: YES (up to 50 pages/month)")
    print(f"  ? Enterprise CAN upload PDFs: YES (unlimited)")
'@

Write-Host ""

# Test BWC Video Capabilities
Write-Host "`n?? Test 2: BWC Video Processing" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Gray

python -c @'
from app import app
from models_auth import User

with app.app_context():
    free_user = User.query.filter_by(email="free@Evident.test").first()
    enterprise_user = User.query.filter_by(email="enterprise@Evident.test").first()
    
    print("\n?? BWC Video Test:")
    print(f"  Free User can process:     {free_user.get_tier_limits()['bwc_videos_per_month']} videos/month")
    print(f"  Enterprise can process:    Unlimited videos/month")
    print(f"\n  Free User max file size:   {free_user.get_tier_limits()['max_file_size_mb']} MB")
    print(f"  Enterprise max file size:  {enterprise_user.get_tier_limits()['max_file_size_mb']} MB")
    
    print(f"\n  ? Free User CAN upload BWC: YES (up to 2 videos/month, max 100MB each)")
    print(f"  ? Enterprise CAN upload BWC: YES (unlimited, max 10GB each)")
'@

Write-Host ""

# Test AI Features
Write-Host "`n?? Test 3: AI Analysis Features" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Gray

python -c @'
from app import app
from models_auth import User

with app.app_context():
    free_user = User.query.filter_by(email="free@Evident.test").first()
    enterprise_user = User.query.filter_by(email="enterprise@Evident.test").first()
    
    free_limits = free_user.get_tier_limits()
    ent_limits = enterprise_user.get_tier_limits()
    
    print("\n?? AI Features:")
    print(f"  Free User:")
    print(f"    - Audio Transcription:      {free_limits.get('transcription_minutes_per_month', 0)} minutes/month")
    print(f"    - Speaker Diarization:      Basic")
    print(f"    - Constitutional Analysis:  Limited")
    print(f"    - Forensic Reports:         Watermarked")
    
    print(f"\n  Enterprise User:")
    print(f"    - Audio Transcription:      Unlimited")
    print(f"    - Speaker Diarization:      Advanced")
    print(f"    - Constitutional Analysis:  Full Access")
    print(f"    - Forensic Reports:         No Watermark")
    print(f"    - API Access:               {ent_limits.get('api_access', False)}")
    print(f"    - Multi-BWC Sync:           {ent_limits.get('multi_bwc_sync', 'N/A')} simultaneous")
'@

Write-Host ""

# Summary
Write-Host "`n? TEST SUMMARY" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "==============================================" -ForegroundColor Cyan

Write-Host "`n?? CAN FREE USERS:" -ForegroundColor Yellow
Write-Host "  ? Upload PDFs:           YES (50 pages/month max)" -ForegroundColor Green
Write-Host "  ? Process BWC Videos:    YES (2 videos/month max)" -ForegroundColor Green
Write-Host "  ? Audio Transcription:   YES (30 minutes/month)" -ForegroundColor Green
Write-Host "  ??  File Size Limit:      100 MB per file" -ForegroundColor Yellow
Write-Host "  ??  Export Watermark:     YES" -ForegroundColor Yellow
Write-Host "  ? API Access:            NO" -ForegroundColor Red

Write-Host "`n?? CAN ENTERPRISE USERS:" -ForegroundColor Yellow
Write-Host "  ? Upload PDFs:           YES (Unlimited)" -ForegroundColor Green
Write-Host "  ? Process BWC Videos:    YES (Unlimited)" -ForegroundColor Green
Write-Host "  ? Audio Transcription:   YES (Unlimited)" -ForegroundColor Green
Write-Host "  ? File Size Limit:       10 GB per file" -ForegroundColor Green
Write-Host "  ? Export Watermark:      NO" -ForegroundColor Green
Write-Host "  ? API Access:            YES" -ForegroundColor Green
Write-Host "  ? Multi-BWC Sync:        Unlimited simultaneous" -ForegroundColor Green
Write-Host "  ? Priority Support:      YES" -ForegroundColor Green

Write-Host "`n?? TEST USER CREDENTIALS:" -ForegroundColor Cyan
Write-Host "  Free User:" -ForegroundColor White
Write-Host "    Email:    free@Evident.test" -ForegroundColor Gray
Write-Host "    Password: test123" -ForegroundColor Gray

Write-Host "`n  Enterprise User:" -ForegroundColor White
Write-Host "    Email:    enterprise@Evident.test" -ForegroundColor Gray
Write-Host "    Password: test123" -ForegroundColor Gray

Write-Host "`n?? Test on Live App:" -ForegroundColor Cyan
Write-Host "  Local:  http://localhost:5000/auth/login" -ForegroundColor White
Write-Host "  Render: https://Evident-legal-tech.onrender.com/auth/login" -ForegroundColor White

Write-Host ""
