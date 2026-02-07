# 🚀 QUICK START: Court Document Processing Tonight

**Status:** ✅ READY  
**Flask App:** Running on http://localhost:5000  
**Admin Login:** admin@Evident.info  
**Password:** BxAdm!n#2026$Secur3\*P@ssw0rd%33^

--

## 📄 Upload Court Documents (3 Methods)

### Method 1: Web Interface (Easiest)

1. Open browser: http://localhost:5000/batch-pdf-upload.html
2. Drag PDFs into upload zone
3. Add metadata (case number, doc type, etc.)
4. Click "Upload All Files"

### Method 2: API with PowerShell

```powershell
# Upload single PDF
$pdfPath = "C:\path\to\court_document.pdf"

Invoke-RestMethod -Uri "http://localhost:5000/api/upload/pdf" `
  -Method POST `
  -Form @{
    file = Get-Item $pdfPath
    case_number = "2026-CV-12345"
    document_type = "motion"
    description = "Motion to Compel Discovery"
    tags = "discovery,motion,bwc"
  }
```

### Method 3: Python Script

```python
import requests

files = {'file': open('discovery_motion.pdf', 'rb')}
data = {
    'case_number': '2026-CV-12345',
    'document_type': 'motion',
    'description': 'Motion to Compel Discovery of BWC Footage',
    'tags': 'discovery,bwc,compel'
}

response = requests.post('http://localhost:5000/api/upload/pdf',
                        files=files, data=data)
print(response.json())
```

--

## 🎥 Process BWC Video

### Upload & Analyze:

```powershell
# 1. Upload video
$videoPath = "C:\path\to\bwc_footage.mp4"
$uploadResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/upload" `
  -Method POST `
  -Form @{ file = Get-Item $videoPath }

$uploadId = $uploadResponse.upload_id

# 2. Start analysis
Invoke-RestMethod -Uri "http://localhost:5000/api/analyze/$uploadId" `
  -Method POST

# 3. Check status
Invoke-RestMethod -Uri "http://localhost:5000/api/analysis/$uploadId/status"
```

**Analysis includes:**

- Complete audio transcript with timestamps
- Speaker identification (officer vs civilian)
- Discrepancy detection vs police reports
- Chain of custody documentation
- PDF report prepared for legal review

--

## 📊 Check Database

### PowerShell:

```powershell
# View all PDFs uploaded today
sqlite3 instance/Evident_auth.db "
  SELECT id, original_filename, case_number, document_type, created_at
  FROM pdf_uploads
  WHERE date(created_at) = date('now')
"

# View BWC analyses
sqlite3 instance/Evident_auth.db "
  SELECT id, filename, status, created_at
  FROM analyses
  ORDER BY created_at DESC
  LIMIT 10
"
```

--

## 🔐 Admin Access

**Login:** http://localhost:5000/auth/login

- Email: admin@Evident.info
- Password: BxAdm!n#2026$Secur3\*P@ssw0rd%33^

**Admin Panel:** http://localhost:5000/admin

- View all uploads
- Manage users
- Download reports
- Review audit logs

--

## ⚠️ If Flask App Stopped

```powershell
# Restart Flask app
python app.py
```

Wait for this message:

```
🌐 Web Application: http://localhost:5000
Ready for production deployment!
```

--

## 📁 File Locations

**Uploaded PDFs:** `./uploads/pdfs/`  
**Uploaded Videos:** `./uploads/bwc_videos/`  
**Analysis Reports:** `./bwc_analysis/`  
**Database:** `./instance/Evident_auth.db`  
**Logs:** `./logs/Evident.log`

--

## 🆘 Quick Troubleshooting

**PDF Upload Fails?**

```powershell
# Check directory exists
New-Item -ItemType Directory -Force -Path "./uploads/pdfs"
```

**Can't Login?**

```powershell
# Recreate admin account
python create_admin.py
```

**Database Error?**

```powershell
# Reinitialize tables
python init_database.py
```

--

## ✅ Pre-Flight Check

Before processing documents:

- [ ] Flask app running (check http://localhost:5000)
- [ ] Can login as admin
- [ ] `./uploads/pdfs/` directory exists
- [ ] Sufficient disk space (check for video files)
- [ ] Database file exists (`./instance/Evident_auth.db`)

--

## 📋 Document Types Supported

Use these for `document_type` field:

- `brief` - Legal brief
- `motion` - Motion or petition
- `order` - Court order
- `filing` - General court filing
- `discovery` - Discovery request/response
- `transcript` - Deposition or hearing transcript
- `exhibit` - Evidence exhibit
- `report` - Police report, expert report
- `correspondence` - Letters, emails
- `other` - Anything else

--

## 🎯 Tonight's Workflow

1. **Start Flask App:**

   ```powershell
   python app.py
   ```

2. **Open Web Interface:**

   ```
   http://localhost:5000/batch-pdf-upload.html
   ```

3. **Drag All Court PDFs** into upload zone

4. **Add Metadata** for each file:
   - Case number
   - Document type
   - Description (optional)
   - Tags (optional, comma-separated)

5. **Click "Upload All Files"**

6. **Monitor Progress** - Green checkmarks for success

7. **Check Database** to verify:

   ```powershell
   python check_db.py
   ```

8. **Review in Admin Panel:**
   ```
   http://localhost:5000/admin
   ```

--

**That's it! You're ready to process court documents. 📄⚖️**

**Need Help?** Check [PRODUCTION-READY-REPORT.md](PRODUCTION-READY-REPORT.md)
for full documentation.
