# Evident.info - Evidence Processing Platform

## Complete Feature Inventory & User Guide

### ? WORKING FEATURES (Ready to Use)

#### 1. BWC Video Forensic Analysis ??

- **Location**: `bwc_forensic_analyzer.py`
- **Route**: `/upload` (POST)
- **Features**:
  - AI-powered speaker diarization
  - Discrepancy detection
  - Timeline analysis
  - Comprehensive forensic reports
  - Speaker identification
- **Usage**: Upload body-worn camera MP4 videos up to 5GB
- **Output**: JSON, TXT, and Markdown reports

#### 2. PDF Document Processing ??

- **Route**: `/batch-pdf-upload.html`
- **Features**:
  - Batch upload multiple PDFs
  - OCR text extraction
  - Case number tagging
  - Document search
  - Chain of custody tracking
- **Usage**: Upload legal documents, briefs, motions, filings

#### 3. Audio Transcription ???

- **Features**:
  - Multi-speaker transcription
  - Timestamp generation
  - Searchable transcripts
  - Export to multiple formats

#### 4. User Authentication & Tiers ??

- **Routes**:
  - `/auth/login` - User login
  - `/auth/register` - New user registration
  - `/auth/dashboard` - User dashboard
- **Tiers**:
  - **FREE**: 2 BWC videos/month, 50 PDF pages, 30 min transcription
  - **PROFESSIONAL** ($49/mo): 25 videos, 500 pages, priority support
  - **PREMIUM** ($199/mo): 100 videos, 2000 pages, API access
  - **ENTERPRISE** ($499/mo): Unlimited processing, dedicated support

#### 5. Case Management ??

- **Features**:
  - Organize evidence by case number
  - Tag and categorize documents
  - Track chain of custody
  - Share evidence securely

### ?? HOW TO START

#### Quick Start (PowerShell):

```powershell
# Run the complete setup script
.\scripts\START-EVERYTHING.ps1
```

This will:

1. Clean all databases
2. Start Flask on http://localhost:5000
3. Create admin user automatically
4. Open browser to login page

#### Default Admin Credentials:

- **Email**: admin@Evident.info
- **Password**: Evident2026!

### ?? DASHBOARD FEATURES

Your dashboard at `/auth/dashboard` shows:

1. **Usage Statistics**:
   - BWC videos processed this month
   - PDF pages analyzed
   - Audio transcription minutes used
   - Storage space consumed

2. **Quick Access Tools**:
   - BWC Video Upload button
   - PDF Batch Upload button
   - Audio Transcription button
   - Case Management link

3. **Recent Activity**:
   - Table of last 10 evidence items processed
   - Status tracking (uploading, analyzing, completed)
   - Quick links to view reports

4. **Tier Information**:
   - Current subscription level
   - Usage limits
   - Upgrade options

### ?? EVIDENCE PROCESSING WORKFLOW

#### For BWC Videos:

1. Go to Dashboard ? "Upload BWC Video"
2. Select MP4 file (up to 5GB)
3. Enter case details:
   - Case number
   - Evidence number
   - Officer names
   - Source information
4. Click Upload
5. System will:
   - Extract audio
   - Perform speaker diarization
   - Detect discrepancies
   - Generate forensic report
6. Download reports in JSON/TXT/MD format

#### For PDF Documents:

1. Go to Dashboard ? "Upload PDFs"
2. Drag and drop multiple PDFs or click to select
3. Add metadata:
   - Case number
   - Document type (brief, motion, order, etc.)
   - Tags
4. System will:
   - Extract text via OCR
   - Index for search
   - Calculate hash for verification
5. Access documents in Case Management

#### For Audio Files:

1. Go to Dashboard ? "Upload Audio"
2. Select audio file
3. System will:
   - Transcribe speech to text
   - Identify speakers
   - Add timestamps
   - Make searchable
4. Export transcript

### ?? FILE STRUCTURE

```
Evident.info/
??? app.py                          # Main Flask application
??? bwc_forensic_analyzer.py        # BWC analysis engine
??? models_auth.py                  # User & tier models
??? auth_routes.py                  # Authentication routes
??? templates/
?   ??? auth/
?   ?   ??? login.html             # Login page
?   ?   ??? register.html          # Registration
?   ?   ??? dashboard.html         # User dashboard ?
?   ??? batch-pdf-upload.html      # PDF uploader
?   ??? base.html                  # Base template
??? static/
?   ??? css/                       # Stylesheets
?   ??? js/                        # JavaScript
??? instance/
?   ??? Evident.db                 # SQLite database
??? uploads/
?   ??? bwc_videos/                # Uploaded videos
??? bwc_analysis/                  # Analysis results
```

### ?? SECURITY FEATURES

- ? Password hashing (bcrypt)
- ? Session management
- ? CORS protection
- ? File upload validation
- ? SQL injection prevention
- ? XSS protection
- ? Chain of custody tracking
- ? Audit logging

### ?? USAGE LIMITS BY TIER

| Feature            | Free   | Professional | Premium | Enterprise |
| ------------------ | ------ | ------------ | ------- | ---------- |
| BWC Videos/month   | 2      | 25           | 100     | Unlimited  |
| Max File Size      | 100 MB | 2 GB         | 5 GB    | 5 GB       |
| PDF Pages/month    | 50     | 500          | 2000    | Unlimited  |
| Transcription mins | 30     | 200          | 1000    | Unlimited  |
| Storage            | 0.5 GB | 10 GB        | 50 GB   | Unlimited  |
| API Access         | ?      | ?            | ?       | ?          |
| Priority Support   | ?      | ?            | ?       | ?          |
| Batch Processing   | ?      | ?            | ?       | ?          |

### ?? TROUBLESHOOTING

#### Issue: Database errors on startup

**Solution**: Run database reset script

```powershell
Remove-Item instance\*.db -Force
python app.py
```

#### Issue: Login doesn't work

**Solution**: Create fresh admin user

```powershell
.\scripts\START-EVERYTHING.ps1
```

#### Issue: File upload fails

**Solution**: Check file size limits and format

- BWC: MP4, max 5GB
- PDF: PDF format, batch max 100MB total
- Audio: MP3, WAV, max 500MB

### ?? DEPLOYMENT CHECKLIST

Before going live:

- [ ] Set strong database password in `.env`
- [ ] Configure production CORS origins
- [ ] Set `FLASK_ENV=production`
- [ ] Use Gunicorn or uWSGI
- [ ] Set up HTTPS/SSL
- [ ] Configure cloud storage (AWS S3/Azure Blob)
- [ ] Set up automated backups
- [ ] Configure email service
- [ ] Set up monitoring (Sentry, LogRocket)

### ?? SUPPORT

- **GitHub Issues**: https://github.com/DTB396/Evident.info/issues
- **Email**: support@Evident.info
- **Docs**: Check TONIGHT-QUICK-START.md

### ?? NEXT STEPS TO ENHANCE DASHBOARD

1. **Real-time Progress Tracking**: WebSocket for upload/analysis progress
2. **Advanced Search**: Full-text search across all evidence
3. **Timeline View**: Visual timeline of case evidence
4. **Collaboration**: Share cases with team members
5. **Export Options**: Bulk export reports in multiple formats
6. **Mobile App**: React Native mobile evidence collection
7. **API Integration**: REST API for third-party integrations

--

**Everything is ready to use!** Just run `.\scripts\START-EVERYTHING.ps1` and
start processing evidence! ??
