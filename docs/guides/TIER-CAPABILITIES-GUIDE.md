# Evident.info - User Tier Capabilities Reference

## ?? Quick Answer: YES, Both Can Process!

### ? **FREE Users CAN:**

- Upload & process PDFs (up to 50 pages/month)
- Upload & analyze BWC videos (up to 2 videos/month)
- Audio transcription (30 minutes/month)
- Max file size: 100 MB

### ? **ENTERPRISE Users CAN:**

- Upload & process PDFs (UNLIMITED)
- Upload & analyze BWC videos (UNLIMITED)
- Audio transcription (UNLIMITED)
- Max file size: 10 GB

--

## ?? Complete Tier Comparison

| Feature                | FREE    | PROFESSIONAL | PREMIUM   | ENTERPRISE        |
| ---------------------- | ------- | ------------ | --------- | ----------------- |
| **BWC Videos/Month**   | 2       | 25           | 100       | **Unlimited**     |
| **Max File Size**      | 100 MB  | 500 MB       | 2 GB      | **10 GB**         |
| **PDF Pages/Month**    | 50      | 1,000        | 10,000    | **Unlimited**     |
| **Transcription Mins** | 30      | 600          | 3,000     | **Unlimited**     |
| **Storage**            | 0.5 GB  | 25 GB        | 250 GB    | **1 TB**          |
| **Export Watermark**   | ? Yes   | ? No         | ? No      | ? No              |
| **Multi-BWC Sync**     | ?       | 3 videos     | 10 videos | **Unlimited**     |
| **API Access**         | ?       | ?            | ?         | ?                 |
| **Priority Support**   | ?       | ?            | ?         | ?                 |
| **Forensic Analysis**  | Basic   | Advanced     | Full      | **Full**          |
| **Constitutional AI**  | Limited | Advanced     | Full      | **Full + Custom** |

--

## ?? How to Test

### **Option 1: Run Test Script**

```powershell
# Creates test users and shows capabilities
.\scripts\TEST-TIER-CAPABILITIES.ps1
```

### **Option 2: Manual Testing**

#### **Start Local Server:**

```powershell
python app.py
```

#### **Test as Free User:**

1. Go to: http://localhost:5000/auth/register
2. Create account with any email
3. Default tier: FREE
4. Try uploading:
   - 1 PDF document (should work)
   - 1 BWC video under 100MB (should work)
   - Try 3rd BWC video (should hit limit)

#### **Test as Enterprise User:**

```powershell
# Create Enterprise user via Python
python -c "
from app import app, db
from models_auth import User, TierLevel

with app.app_context():
    user = User(
        email='test@enterprise.com',
        full_name='Test Enterprise',
        tier=TierLevel.ENTERPRISE,
        is_active=True
    )
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()
"
```

Then login and test unlimited uploads!

--

## ?? What Each Tier Can Process

### **FREE Tier:**

```
? PDFs: YES
   - 50 pages/month limit
   - 100 MB max file size
   - Basic OCR
   - Search enabled
   - Watermarked exports

? BWC Videos: YES
   - 2 videos/month limit
   - 100 MB max file size
   - Audio transcription (30 min total)
   - Basic speaker ID
   - Watermarked reports
```

### **PROFESSIONAL Tier ($49/month):**

```
? PDFs: YES
   - 1,000 pages/month
   - 500 MB max file size
   - Advanced OCR
   - No watermarks
   - Batch processing

? BWC Videos: YES
   - 25 videos/month
   - 500 MB max file size
   - Audio transcription (600 min)
   - Advanced speaker diarization
   - Sync up to 3 videos
   - Professional reports
```

### **PREMIUM Tier ($199/month):**

```
? PDFs: YES
   - 10,000 pages/month
   - 2 GB max file size
   - AI-powered analysis
   - Constitutional violation detection
   - API access

? BWC Videos: YES
   - 100 videos/month
   - 2 GB max file size
   - Full forensic analysis
   - Sync up to 10 videos
   - Constitutional AI analysis
```

### **ENTERPRISE Tier ($499/month):**

```
? PDFs: UNLIMITED
   - No page limits
   - 10 GB max file size
   - Custom AI training
   - Dedicated support
   - White-label options

? BWC Videos: UNLIMITED
   - No video limits
   - 10 GB max file size
   - Unlimited transcription
   - Unlimited video sync
   - Custom forensic models
   - Constitutional AI + Case law matching
```

--

## ?? Live Testing URLs

### **Local:**

- Register: http://localhost:5000/auth/register
- Login: http://localhost:5000/auth/login
- Dashboard: http://localhost:5000/auth/dashboard
- PDF Upload: http://localhost:5000/batch-pdf-upload.html

### **Render (Production):**

- Register: https://Evident-legal-tech.onrender.com/auth/register
- Login: https://Evident-legal-tech.onrender.com/auth/login
- Dashboard: https://Evident-legal-tech.onrender.com/auth/dashboard

--

## ?? Enforcement

Tier limits are enforced at:

1. **Upload Time:**

   ```python
   # In app.py - upload routes
   if not current_user.can_analyze():
       return jsonify({'error': 'Monthly limit reached'}), 403
   ```

2. **File Size Check:**

   ```python
   max_size = current_user.get_tier_limits()['max_file_size_mb']
   if file_size > max_size * 1024 * 1024:
       return jsonify({'error': 'File too large'}), 413
   ```

3. **Usage Tracking:**
   ```python
   # UsageTracking model increments counters
   usage.increment('bwc_videos_used')
   usage.increment('document_pages_used', pages)
   ```

--

## ? Bottom Line

**YES, both FREE and ENTERPRISE users CAN process PDFs and BWC videos!**

The difference is in **quantity** and **features**, not capability:

- **FREE**: Limited processing (2 videos, 50 PDF pages)
- **ENTERPRISE**: Unlimited processing + advanced features

--

## ?? Run the Test Now!

```powershell
# See it in action
.\scripts\TEST-TIER-CAPABILITIES.ps1
```

This will:

1. Create test users for each tier
2. Show exact limits
3. Demonstrate what each can do
4. Provide test credentials
