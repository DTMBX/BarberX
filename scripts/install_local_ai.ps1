# Local AI Quick Start - Install Core Open-Source Tools
# =====================================================
# This script installs the essential open-source AI tools for evidence processing

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  LOCAL AI QUICK START - Essential Open-Source Tools" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "`n[SETUP] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "`n[SETUP] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`n[PIP] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  INSTALLING CORE AI LIBRARIES" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Essential packages
$packages = @(
    # Audio transcription
    "openai-whisper",
    
    # Speaker diarization
    "pyannote.audio",
    
    # Object detection
    "ultralytics",
    
    # OCR
    "pytesseract",
    "pdf2image",
    
    # Entity extraction
    "spacy",
    
    # Semantic search
    "sentence-transformers",
    
    # AI super-resolution
    "realesrgan",
    "basicsr",
    
    # Audio processing
    "librosa",
    "noisereduce",
    "soundfile",
    "pydub",
    
    # Video processing
    "opencv-python",
    "moviepy",
    "imageio",
    "imageio-ffmpeg",
    
    # Document processing
    "PyPDF2",
    "pikepdf",
    "python-docx",
    "openpyxl",
    "pandas",
    
    # Core dependencies
    "torch",
    "torchvision",
    "torchaudio",
    "transformers",
    "numpy",
    "scipy",
    "Pillow"
)

$total = $packages.Count
$current = 0

foreach ($package in $packages) {
    $current++
    Write-Host "`n[$current/$total] Installing $package..." -ForegroundColor Cyan
    python -m pip install $package --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  SUCCESS: $package" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: $package failed (may need manual install)" -ForegroundColor Yellow
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  DOWNLOADING AI MODELS" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Download Whisper model
Write-Host "`n[WHISPER] Downloading 'small' model (recommended)..." -ForegroundColor Cyan
python -c "import whisper; whisper.load_model('small')" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  SUCCESS: Whisper model downloaded" -ForegroundColor Green
}

# Download YOLO model
Write-Host "`n[YOLO] Downloading 'yolov8m' model..." -ForegroundColor Cyan
python -c "from ultralytics import YOLO; YOLO('yolov8m.pt')" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  SUCCESS: YOLO model downloaded" -ForegroundColor Green
}

# Download spaCy model
Write-Host "`n[SPACY] Downloading 'en_core_web_md' model..." -ForegroundColor Cyan
python -m spacy download en_core_web_md --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  SUCCESS: spaCy model downloaded" -ForegroundColor Green
}

# Download sentence-transformers model
Write-Host "`n[SENTENCE-TRANSFORMERS] Downloading 'all-MiniLM-L6-v2' model..." -ForegroundColor Cyan
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  SUCCESS: Sentence transformer model downloaded" -ForegroundColor Green
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  VERIFYING INSTALLATION" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Test imports
Write-Host "`n[TEST] Verifying installations..." -ForegroundColor Cyan

$tests = @(
    @{name="Whisper"; cmd="import whisper"},
    @{name="pyannote.audio"; cmd="import pyannote.audio"},
    @{name="YOLO"; cmd="from ultralytics import YOLO"},
    @{name="Tesseract"; cmd="import pytesseract"},
    @{name="Real-ESRGAN"; cmd="from realesrgan import RealESRGANer"},
    @{name="spaCy"; cmd="import spacy"},
    @{name="sentence-transformers"; cmd="from sentence_transformers import SentenceTransformer"},
    @{name="librosa"; cmd="import librosa"},
    @{name="OpenCV"; cmd="import cv2"},
    @{name="moviepy"; cmd="import moviepy.editor"}
)

$success_count = 0
foreach ($test in $tests) {
    $result = python -c $test.cmd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  SUCCESS: $($test.name)" -ForegroundColor Green
        $success_count++
    } else {
        Write-Host "  FAILED: $($test.name)" -ForegroundColor Red
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION SUMMARY" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`nComponents installed: $success_count/$($tests.Count)" -ForegroundColor White

if ($success_count -eq $tests.Count) {
    Write-Host "`nSUCCESS: All tools are ready!" -ForegroundColor Green
} else {
    Write-Host "`nWARNING: Some components need manual setup" -ForegroundColor Yellow
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`n1. HUGGING FACE TOKEN (for pyannote speaker diarization):" -ForegroundColor Cyan
Write-Host "   - Create free account: https://huggingface.co" -ForegroundColor White
Write-Host "   - Get token: https://huggingface.co/settings/tokens" -ForegroundColor White
Write-Host "   - Accept license: https://huggingface.co/pyannote/speaker-diarization" -ForegroundColor White
Write-Host "   - Set in .env: HUGGINGFACE_TOKEN=your_token" -ForegroundColor White

Write-Host "`n2. TESSERACT OCR (for document text extraction):" -ForegroundColor Cyan
Write-Host "   - Download: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
Write-Host "   - Install to default location" -ForegroundColor White
Write-Host "   - Set in .env: TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe" -ForegroundColor White

Write-Host "`n3. CONFIGURE ENVIRONMENT:" -ForegroundColor Cyan
Write-Host "   - Copy: tillerstead-toolkit\backend\.env.local_ai_example to .env" -ForegroundColor White
Write-Host "   - Edit .env with your tokens/paths" -ForegroundColor White

Write-Host "`n4. TEST THE SERVICES:" -ForegroundColor Cyan
Write-Host "   python -c `"from app.services.local_ai_service import local_ai; print('Ready!')`"" -ForegroundColor White

Write-Host "`n5. READ DOCUMENTATION:" -ForegroundColor Cyan
Write-Host "   docs\LOCAL-AI-GUIDE.md - Complete user guide" -ForegroundColor White

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  NO CLOUD APIs • 100% FREE • COURT-DEFENSIBLE • OFFLINE CAPABLE" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`n"
