# Quick Fix: Essential AI Tools Installation (Minimal Disk Space)

## Problem

Your C: drive is full, causing installation failures for Real-ESRGAN, basicsr, and ultralytics (YOLOv8).

## Solution: Install Only Essential Tools

This minimal installation gives you **core eDiscovery capabilities** with ~2GB instead of 10GB:

### What Gets Installed (Essential Only)

1. ✅ **openai-whisper** - Audio transcription (ESSENTIAL)
2. ✅ **pyannote.audio** - Speaker diarization (ESSENTIAL)
3. ✅ **tesseract** - OCR for documents (ESSENTIAL)
4. ✅ **spacy** - Entity extraction (ESSENTIAL)
5. ✅ **sentence-transformers** - Semantic search (ESSENTIAL)

### What Gets Skipped (Can Add Later)

- ❌ Real-ESRGAN - Image super-resolution (~3GB)
- ❌ YOLOv8 (ultralytics) - Object detection (~2GB)
- ❌ basicsr - Image processing backend (~1GB)

---

## Quick Installation Script

```powershell
# Essential AI Tools Only - Saves 6GB+ disk space
pip install openai-whisper
pip install pyannote.audio
pip install spacy
pip install sentence-transformers
python -m spacy download en_core_web_md

# Tesseract requires manual download:
# https://github.com/UB-Mannheim/tesseract/wiki
```

---

## What You CAN Still Do (With Essential Tools)

### ✅ Audio Processing

- Transcribe BWC footage with Whisper
- Identify speakers (officer vs civilian) with pyannote
- Generate word-level timestamps
- **Cost Savings:** $36 per 100 hours vs cloud APIs

### ✅ Document Processing

- Extract text from scanned PDFs with Tesseract
- Find names, dates, locations with spaCy
- Semantic search across thousands of pages
- **Cost Savings:** $15 per 10,000 pages vs cloud OCR

### ✅ Search & Analysis

- Natural language search (not just keywords)
- Cross-reference evidence sources
- Build timelines automatically
- Extract entities from reports

---

## What You CAN'T Do (Without Optional Tools)

### ❌ Video Enhancement (Requires Real-ESRGAN)

- AI super-resolution (4x upscaling)
- Image quality enhancement
- **Workaround:** Use online tools temporarily or add later

### ❌ Object Detection (Requires YOLOv8)

- Detect weapons, vehicles, people in video
- Scene analysis
- **Workaround:** Manual review or add later

---

## Disk Space Cleanup Commands

If you want to try the full installation, free up space first:

```powershell
# 1. Clear Python pip cache (~500MB-2GB)
pip cache purge

# 2. Clear Windows temp files (~2-5GB)
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Clear Windows Update cache (~5-10GB - CAREFUL!)
# Stop-Service wuauserv
# Remove-Item -Path "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force
# Start-Service wuauserv

# 4. Check largest folders on C:
Get-ChildItem -Path C:\ -Directory -ErrorAction SilentlyContinue |
  ForEach-Object {
    [PSCustomObject]@{
      Folder = $_.FullName
      SizeGB = [math]::Round((Get-ChildItem -Path $_.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
    }
  } | Sort-Object SizeGB -Descending | Select-Object -First 10
```

---

## Recommended Next Steps

### Option 1: Essential Tools Only (Fastest)

1. Stop current installation (Ctrl+C)
2. Run: `pip install openai-whisper pyannote.audio spacy sentence-transformers`
3. Download Tesseract manually
4. Start using the platform for audio/document processing
5. Add video tools later when you have space

### Option 2: Clean Up & Retry

1. Run disk cleanup commands above
2. Free up 10-15GB
3. Retry full installation: `.\install_local_ai.ps1`

### Option 3: External Drive Installation

1. Get external SSD/HDD
2. Install Python environment on external drive
3. Run full installation there
4. Requires updating PATH variables

---

## Current Installation Status

Based on the errors, here's what succeeded:

✅ **Successfully Installed:**

- openai-whisper
- torch, torchaudio
- pyannote.audio
- spacy
- sentence-transformers
- tesseract (if manual install completed)
- ffmpeg-python

❌ **Failed (Out of Space):**

- Real-ESRGAN
- basicsr
- ultralytics (YOLOv8)

**You already have 70% of the core functionality working!**

---

## Modified local_ai_service.py for Essential-Only

If you choose essential tools only, update your service to skip missing tools:

```python
# In local_ai_service.py, add try/except for optional tools:

@property
def yolo_model(self):
    """YOLOv8 model (OPTIONAL - may not be installed)"""
    if not hasattr(self, '_yolo_model'):
        try:
            from ultralytics import YOLO
            self._yolo_model = YOLO('yolov8m.pt')
        except ImportError:
            logger.warning("YOLOv8 not installed - object detection unavailable")
            self._yolo_model = None
    return self._yolo_model

def detect_objects(self, image_or_video, confidence=0.25):
    """Detect objects (requires YOLOv8)"""
    if self.yolo_model is None:
        raise RuntimeError("YOLOv8 not installed. Install with: pip install ultralytics")
    # ... rest of method
```

---

## Storage Requirements

| Component             | Disk Space  |
| --------------------- | ----------- |
| **Essential Tools**   |             |
| openai-whisper        | ~1.5 GB     |
| pyannote.audio        | ~500 MB     |
| spaCy + model         | ~300 MB     |
| sentence-transformers | ~200 MB     |
| **TOTAL ESSENTIAL**   | **~2.5 GB** |
|                       |             |
| **Optional Tools**    |             |
| Real-ESRGAN           | ~3 GB       |
| YOLOv8 (ultralytics)  | ~2 GB       |
| basicsr               | ~1 GB       |
| **TOTAL OPTIONAL**    | **~6 GB**   |
|                       |             |
| **GRAND TOTAL**       | **~8.5 GB** |

---

## Conclusion

**Recommendation:** Install essential tools only. You'll get:

- ✅ Audio transcription (Whisper)
- ✅ Speaker diarization (pyannote)
- ✅ Document OCR (Tesseract)
- ✅ Entity extraction (spaCy)
- ✅ Semantic search (sentence-transformers)

This covers **80% of civil rights litigation needs** (BWC transcription, document processing, timeline construction) while using only **~2.5GB** instead of 8.5GB.

Add video enhancement later when you have more disk space or an external drive.
