# BWC Forensic Analyzer - Web App Guide

## 🎯 Easy Drag-and-Drop Interface

Your BWC analyzer now has a **user-friendly web interface** - no command line
needed!

--

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Web Server

```powershell
# Activate virtual environment
cd c:\web-dev\github-repos\Evident.info
.\.venv\Scripts\Activate.ps1

# Install Flask (if not already installed)
pip install flask flask-cors

# Start the web app
python bwc_web_app.py
```

You'll see:

```
╔════════════════════════════════════════════════════════════════╗
║   BWC Forensic Analyzer - Web Application                     ║
║   Drag-and-Drop Interface for Body-Worn Camera Analysis       ║
╚════════════════════════════════════════════════════════════════╝

🌐 Web Interface: http://localhost:5000
📊 API Docs: http://localhost:5000/api/health

Ready to accept BWC video uploads!
```

### Step 2: Open Your Browser

Navigate to: **http://localhost:5000**

### Step 3: Upload & Analyze

1. **Drag-and-drop** your BWC video file onto the upload area (or click to
   browse)
2. **Fill in case details:**
   - Case Number (e.g., "ATL-L-002794-25")
   - Evidence Number (e.g., "EX-BWC-001")
   - Acquired By (your name)
   - Source (e.g., "OPRA Request #2025-001")
   - Known Officers (comma-separated)
3. **Click "Start Forensic Analysis"**
4. **Wait for processing** (5-30 minutes depending on video length)
5. **View results:**
   - Full transcript with timestamps
   - Speaker identification (officer vs civilian)
   - Extracted entities (names, dates, locations)
   - Discrepancies vs CAD logs/police reports
   - Legal significance notes
6. **Download reports** in JSON, TXT, or Markdown format

--

## 📊 What You'll See

### Upload Screen

```
🎥 BWC Forensic Analyzer
Analysis documented with immutable audit trails to support legal review

┌─────────────────────────────────────┐
│        Drop BWC Video Here          │
│      or click to browse files       │
│                                     │
│  Supported: MP4, AVI, MOV, MKV     │
│           Max 5GB                   │
└─────────────────────────────────────┘
```

### Case Information Form

```
Case Number *         ATL-L-002794-25
Evidence Number       EX-BWC-001
Acquired By *         Devon Tyler
Source *              OPRA Request #2025-001
Known Officers        Smith, Johnson, Williams

[ 🚀 Start Forensic Analysis ]
```

### Progress Screen

```
Analyzing BWC Footage...          [Processing]

█████████████████░░░░░░░░░░░░░░  65%

Extracting audio from video...

Note: Analysis may take 5-30 minutes depending on
video length and hardware. GPU is 6-10x faster.
```

### Results Screen

```
Analysis Complete ✅              [Completed]

┌─────────┬─────────┬─────────┬──────────────┐
│ 23 min  │ 2       │ 45      │ 3            │
│ Duration│ Speakers│ Segments│ Discrepancies│
└─────────┴─────────┴─────────┴──────────────┘

[ 📄 Download JSON ] [ 📝 Download Text ] [ 📋 Download Markdown ]

⚠️ Discrepancies Detected
┌─────────────────────────────────────────────┐
│ [MAJOR] Statement Discrepancy               │
│ PERSON mentioned in BWC but not in report   │
│ BWC: John Doe identified at scene           │
│ Police Report: Not mentioned                │
│ ⚖️ Potential Brady material - exculpatory   │
│    evidence omitted from official report    │
└─────────────────────────────────────────────┘

📋 Extracted Entities
PERSON: Smith, Johnson, John Doe
GPE: Atlantic County, New Jersey
DATE: January 15, 2025
TIME: 14:30, 15:45

📜 Full Transcript
┌─────────────────────────────────────────────┐
│ 0:00 - 0:04                                 │
│ Officer Smith:                              │
│ Unit 23 responding to 123 Main Street       │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ 0:04 - 0:08                                 │
│ Dispatch:                                   │
│ Copy that, Unit 23                          │
└─────────────────────────────────────────────┘
```

--

## 🎨 Features

### ✅ Drag-and-Drop Upload

- Simply drag BWC video files into the browser
- Supports all major video formats (MP4, AVI, MOV, MKV, WMV, WebM)
- Up to 5GB file size

### ✅ Real-Time Progress

- Live progress bar showing analysis status
- Current step display (audio extraction, transcription, diarization, etc.)
- Estimated time remaining

### ✅ Interactive Results

- **Summary Statistics:** Duration, speakers, segments, discrepancies
- **Discrepancy Cards:** Color-coded by severity (critical=red, major=orange,
  minor=green)
- **Entity Tags:** Visual badges for all extracted names, dates, locations
- **Scrollable Transcript:** Full transcript with timestamps and speaker labels
- **Download Buttons:** Export reports in JSON, TXT, or Markdown

### ✅ Reports Prepared for Legal Review

All reports include:

- SHA-256 verification and chain-of-custody metadata
- Complete file metadata
- Word-level timestamps
- Speaker attribution
- Legal significance annotations
- Exported verification details to assist with authentication (consult counsel
  regarding FRE 901 application)

--

## 📡 API Endpoints

The web app exposes a REST API for programmatic access:

### Health Check

```http
GET /api/health
```

Returns AI model status

### Upload Video

```http
POST /api/upload
Content-Type: multipart/form-data

file: <video_file>
```

Returns `upload_id`

### Start Analysis

```http
POST /api/analyze
Content-Type: application/json

{
  "upload_id": "abc123...",
  "case_number": "ATL-L-002794-25",
  "acquired_by": "Devon Tyler",
  "source": "OPRA Request",
  "known_officers": ["Smith", "Johnson"]
}
```

### Check Status

```http
GET /api/status/<upload_id>
```

Returns analysis progress and results

### Download Report

```http
GET /api/report/<upload_id>/json
GET /api/report/<upload_id>/txt
GET /api/report/<upload_id>/md
```

### Get Transcript

```http
GET /api/transcript/<upload_id>
```

### Get Discrepancies

```http
GET /api/discrepancies/<upload_id>
```

### Get Entities

```http
GET /api/entities/<upload_id>
```

### List All Analyses

```http
GET /api/analyses
```

--

## 🔧 Configuration

### Environment Variables

```powershell
# Set Hugging Face token for speaker diarization
$env:HUGGINGFACE_TOKEN = "hf_your_token_here"

# Optional: Change upload folder
$env:UPLOAD_FOLDER = "C:\evidence\uploads"

# Optional: Change analysis output folder
$env:ANALYSIS_FOLDER = "C:\evidence\analysis"
```

### App Settings

Edit `bwc_web_app.py`:

```python
# Max file size (default 5GB)
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024

# Allowed video formats
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}

# Whisper model size (tiny, base, small, medium, large)
# Larger = more accurate, slower
whisper_model_size='base'  # Change to 'small' or 'medium' for better accuracy
```

--

## 💻 System Requirements

### Minimum (CPU Processing)

- **CPU:** Intel i5 or AMD Ryzen 5
- **RAM:** 8GB
- **Storage:** 50GB free
- **Processing Speed:** ~30 minutes per hour of video

### Recommended (GPU Processing)

- **CPU:** Intel i7/i9 or AMD Ryzen 7/9
- **RAM:** 16GB
- **GPU:** NVIDIA GTX 1660 or better (6GB+ VRAM)
- **Storage:** SSD with 100GB+ free
- **Processing Speed:** ~5 minutes per hour of video

--

## 🎯 Use Cases

### 1. Pro Se Litigant

**You are:** Representing yourself in civil rights case  
**Process:**

1. Open web app in browser
2. Drag OPRA-requested BWC video
3. Fill in case number and details
4. Wait for analysis
5. Download reports for court submission

### 2. Attorney

**You are:** Representing client in excessive force case  
**Process:**

1. Upload multiple BWC files from discovery
2. Batch process all videos
3. Review discrepancies in web interface
4. Export reports for expert review
5. Generate court exhibits

### 3. Investigative Journalist

**You are:** Researching police accountability  
**Process:**

1. Upload public records BWC footage
2. Extract officer names and badge numbers
3. Search transcript for key phrases
4. Export timeline for article

### 4. Civil Rights Advocate

**You are:** Monitoring police conduct patterns  
**Process:**

1. Upload BWC from multiple incidents
2. Compare officer statements across cases
3. Identify pattern of omissions
4. Generate evidence for pattern/practice claims

--

## 🛡️ Security & Privacy

### ✅ 100% Local Processing

- All analysis happens on YOUR computer
- No data sent to cloud services
- No internet connection required (after model download)

### ✅ Data Retention

- Uploaded videos stored in `./uploads/bwc_videos/`
- Analysis reports stored in `./bwc_analysis/`
- **You control the data** - delete anytime

### ✅ Chain of Custody

- SHA-256 hash calculated on upload
- File metadata preserved
- Tampering detection built-in

--

## 🐛 Troubleshooting

### "Cannot connect to analysis server"

**Solution:** Make sure `bwc_web_app.py` is running:

```powershell
python bwc_web_app.py
```

### "AI models are loading"

**Solution:** Wait 30-60 seconds for models to initialize, then refresh page

### "Upload failed: Invalid file type"

**Solution:** Only upload video files (MP4, AVI, MOV, MKV, WMV, WebM)

### "Analysis failed: Out of memory"

**Solution:** Close other programs, or use smaller Whisper model:

```python
# Edit bwc_web_app.py, line 32:
whisper_model_size='tiny'  # Instead of 'base'
```

### Analysis is very slow

**Solution:**

- Normal on CPU (30 min per hour of video)
- Use GPU for 6-10x speedup
- Or process overnight for long videos

--

## 📁 File Structure

```
Evident.info/
├── bwc_web_app.py              # Flask web server
├── bwc-analyzer.html           # Web interface
├── bwc_forensic_analyzer.py    # Analysis engine
├── uploads/
│   └── bwc_videos/             # Uploaded videos
│       └── 20260122_video.mp4
├── bwc_analysis/               # Analysis outputs
│   └── abc123.../
│       ├── report.json         # Machine-readable
│       ├── report.txt          # Human-readable
│       └── report.md           # Documentation
└── assets/
    ├── css/
    │   └── legal-tech-platform.css  # Styling
    └── js/
        └── platform.js         # Interactivity
```

--

## 🚀 Next Steps

1. **Start the web server:**

   ```powershell
   python bwc_web_app.py
   ```

2. **Open browser:** http://localhost:5000

3. **Upload your first BWC video**

4. **Review the results**

5. **Download reports for your case**

--

## 📞 Support

- **Documentation:** See [BWC-ANALYSIS-GUIDE.md](BWC-ANALYSIS-GUIDE.md)
- **GitHub:** https://github.com/Evident/Evident.info
- **License:** MIT (free, open source)

--

**Generated by Evident Legal Tech Platform**  
_Documentation for legal review • 100% Local Processing • Zero Cloud Costs_
