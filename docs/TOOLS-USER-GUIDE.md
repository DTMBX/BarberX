# Evident Legal Tools - User Guide

Welcome to the Evident Legal Case Management Pro Suite tools! This guide will
help you use all the available tools effectively.

## 🔧 Available Tools

### 1. Docket Search

**URL:** `/tools/docket-search/`

Search and track court dockets, case filings, and party information across all
Evident cases.

**Features:**

- Real-time search across all docket entries
- Advanced filtering by:
  - Court (Atlantic, Mercer, Camden, Essex, Hudson)
  - Case type (Law Division, Special Civil, Family, Criminal)
  - Filing date range
  - Case status
  - Party type
- Results grouped by case
- Direct links to PDF documents

**How to Use:**

1. Enter a docket number (e.g., `ATL-L-003252-25`) or search term
2. Use advanced filters to narrow results
3. Click on case links to view full case details
4. Click on document links to download PDFs

**Search Tips:**

- **Docket Format:** County-Division-Number-Year (e.g., ATL-L-002794-25)
- **Wildcards:** Use \* for partial matches
- **Date Ranges:** Use the date filters to narrow results

--

### 2. Document Analysis

**URL:** `/tools/document-analysis/`

Upload legal documents for processing, classification, and storage.

**Features:**

- Drag-and-drop file upload
- Backend API integration (when available)
- Git inbox workflow (always available)
- Supports: PDF, DOCX, DOC, JPG, PNG
- Max file size: 500MB per file
- Batch upload support (up to 50 files)

**Planned Features (Coming Soon):**

- OCR & text extraction
- Constitutional violation scanning
- Bates numbering
- Document classification

**How to Use:**

#### Option A: Upload via Backend API (requires server running)

1. Drag and drop files onto the upload zone
2. Or click "Choose Files" to browse
3. Files are uploaded automatically to the backend
4. View processing results

#### Option B: Git Inbox Workflow (always available)

1. Save files to `_inbox/` directory
2. Run PowerShell script: `.\tools\upload_pdfs.ps1`
3. Script commits and pushes files
4. GitHub Actions processes automatically

**Supported File Types:**

- Documents: `.pdf`, `.doc`, `.docx`, `.txt`
- Images: `.jpg`, `.jpeg`, `.png`

--

### 3. Deadline Calculator

**URL:** `/tools/deadline-calculator/`

Calculate court deadlines with automatic exclusion of weekends and holidays.

**Features:**

- Real-time date calculations
- Excludes weekends automatically
- Excludes federal holidays
- Supports both forward and backward calculations
- Handles NJ court-specific rules

**How to Use:**

1. **Enter Event Date:** The triggering event (e.g., service date)
2. **Select Direction:** Add days (forward) or subtract days (backward)
3. **Enter Number of Days:** The deadline period
4. **Review Result:** See the calculated deadline with excluded dates

**Examples:**

- **Service response:** 35 days after service
- **Appeal deadline:** 45 days after judgment
- **Discovery response:** 30 days after request

**Important Notes:**

- Weekends are automatically excluded
- Federal holidays are excluded
- Business days only (Monday-Friday)
- For NJ-specific court holidays, consult local court rules

--

## 🚀 Backend API Setup (Optional)

The tools work in two modes:

### 1. Local Data Mode (Default)

- Docket search works immediately with Jekyll site data
- Document upload uses Git inbox workflow
- No backend server required

### 2. Backend API Mode (Enhanced Features)

Requires running the FastAPI backend server.

**Start Backend Server:**

```powershell
cd tillerstead-toolkit/backend
python -m uvicorn app.main:app -reload
```

**Backend URL:** `http://localhost:8000`

**Available Endpoints:**

- `/api/v1/documents/upload` - Document upload
- `/api/v1/batch/upload` - Batch upload with transcription
- `/api/v1/bwc/upload` - Body-worn camera footage
- `/api/v1/documents/ocr` - OCR processing
- `/api/v1/transcription/create` - Audio/video transcription

**Check Backend Health:**

```powershell
curl http://localhost:8000/health
```

--

## 📁 File Upload Workflows

### PDF Batch Upload to Git Inbox

**Step 1: Copy files to inbox**

```powershell
# Copy PDFs with docket number in filename
cp ~/Downloads/ATL-L-003252-25-*.pdf _inbox/

# Or create case-specific subdirectory
mkdir _inbox/atl-l-003252-25
cp ~/Downloads/*.pdf _inbox/atl-l-003252-25/
```

**Step 2: Run upload script**

```powershell
.\tools\upload_pdfs.ps1 -MaxFilesPerCommit 50
```

**Step 3: Wait for GitHub Actions**

- Workflow: `scripts/docket-intake.js`
- Auto-routes to correct case folder
- Updates YAML docket data
- Creates PR for review

**Filename Best Practices:**

- ✅ `ATL-L-003252-25-motion-to-dismiss.pdf`
- ✅ `2025-12-20-ATL-L-003252-25-order.pdf`
- ⚠️ Without docket number → goes to `cases/unassigned/filings/`

### Video Upload (BWC Footage)

**Motorola BWC Filename Format:**

```
OfficerName_YYYYMMDDHHMI_DeviceID-Segment.mp4
Example: BryanMerritt_202511292256_BWL7137497-0.mp4
```

**Upload via API:**

```powershell
# Using curl
curl -X POST http://localhost:8000/api/v1/bwc/upload \
  -F "files=@BryanMerritt_202511292256_BWL7137497-0.mp4" \
  -F "case_id=1" \
  -F "auto_sync=true" \
  -F "auto_transcribe=true"
```

**Supported Video Types:**

- `.mp4` (recommended)
- `.mov`
- `.avi`
- `.mkv`

**Processing Features:**

- Filename parsing (officer name, timestamp, device ID)
- Multi-POV synchronization
- Automatic transcription
- Thumbnail generation
- Metadata extraction

--

## 🎯 Quick Start Checklist

### For Docket Search:

- [ ] Navigate to `/tools/docket-search/`
- [ ] Enter docket number or search term
- [ ] Apply filters if needed
- [ ] Click search
- [ ] View results grouped by case

### For Document Upload:

- [ ] Navigate to `/tools/document-analysis/`
- [ ] Drag and drop files OR click "Choose Files"
- [ ] Wait for upload confirmation
- [ ] OR: Copy to `_inbox/` and run `upload_pdfs.ps1`

### For Deadline Calculator:

- [ ] Navigate to `/tools/deadline-calculator/`
- [ ] Enter event date
- [ ] Enter number of days
- [ ] Click "Calculate Deadline"
- [ ] Review result with excluded dates

--

## ⚙️ Configuration

### API Configuration

Edit `assets/js/api-config.js`:

```javascript
const API_CONFIG = {
  BACKEND_URL: 'http://localhost:8000', // Change if backend runs elsewhere
  LIMITS: {
    MAX_FILE_SIZE_MB: 500,
    MAX_FILES_PER_BATCH: 50,
  },
};
```

### Jekyll Site Data

Docket data loaded from:

- `/index.json` - Site-wide case data
- `/_data/docket/*.yml` - Individual case dockets
- `/_data/cases-map.yml` - Docket-to-slug mapping

--

## 🐛 Troubleshooting

### "Backend not available" message

**Solution:**

1. Check if backend server is running: `curl http://localhost:8000/health`
2. Start server:
   `cd tillerstead-toolkit/backend && python -m uvicorn app.main:app -reload`
3. Or use Git inbox workflow instead

### No search results found

**Check:**

- Spelling of docket number
- Date range filters (too narrow?)
- Case exists in `_data/cases-map.yml`
- Docket YAML files exist in `_data/docket/`

### File upload fails

**Check:**

- File size under 500MB
- File extension allowed (PDF, DOCX, JPG, PNG)
- Backend server running (if using API mode)
- Git inbox directory exists: `_inbox/`

### Deadline calculator shows wrong date

**Check:**

- Event date is in correct format
- Direction is correct (add vs subtract)
- Number of days is accurate
- Review excluded dates list

--

## 📚 Related Documentation

- **Batch Upload Guide:** `_inbox/README.md`
- **Docket System Docs:** `DOCKET-INTAKE-OPTIMIZATION.md`
- **Backend API Docs:** `tillerstead-toolkit/backend/README.md`
- **Case Management:** `/cases/` directory

--

## 🎓 Support

**Issues or Questions?**

- Check existing documentation in `/docs/`
- Review case files in `/_cases/`
- Examine docket data in `/_data/docket/`
- Submit issues via GitHub

--

**Last Updated:** January 22, 2026 **Version:** 1.0.0 **Evident Legal Case
Management Pro Suite**
