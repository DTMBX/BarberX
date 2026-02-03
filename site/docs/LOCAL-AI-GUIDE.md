# Local AI Tools Guide - Open-Source Evidence Processing

## 🎯 Overview

Process all evidence **locally on your machine** using 100% open-source AI tools. No cloud APIs, no subscriptions, completely free and court-defensible.

**Benefits:**

- ✅ **No costs** - All tools are free and open-source
- ✅ **Privacy** - Data never leaves your system
- ✅ **Court-defensible** - Fully auditable open-source algorithms
- ✅ **Offline** - Works without internet connection
- ✅ **Control** - You own the models and processing pipeline

---

## 📦 Installation

### Step 1: Run Setup Script

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Run setup (installs all open-source AI tools)
python tillerstead-toolkit/backend/scripts/setup_local_ai_tools.py

# Verify installation
python tillerstead-toolkit/backend/scripts/setup_local_ai_tools.py --verify-only
```

### Step 2: Configure Environment

```bash
# Copy example config
cp tillerstead-toolkit/backend/.env.local_ai_example .env

# Edit .env and set:
# - HUGGINGFACE_TOKEN (free from https://huggingface.co/settings/tokens)
# - TESSERACT_CMD (if not in PATH)
```

### Step 3: Test Tools

```bash
# Test Whisper transcription
python -c "import whisper; model = whisper.load_model('small'); print('✅ Whisper ready')"

# Test YOLO object detection
python -c "from ultralytics import YOLO; model = YOLO('yolov8m.pt'); print('✅ YOLO ready')"

# Test spaCy entity extraction
python -c "import spacy; nlp = spacy.load('en_core_web_md'); print('✅ spaCy ready')"
```

---

## 🤖 Available AI Tools

### 1. **Whisper** (Audio Transcription)

**What it does:** Converts spoken words to text with word-level timestamps

**Models:**

- `tiny` - Fastest (1GB RAM) - Good for quick tests
- `base` - Fast (1GB RAM) - Good quality
- **`small`** - **⭐ RECOMMENDED** (2GB RAM) - Best balance
- `medium` - High quality (5GB RAM)
- `large` - Best quality (10GB RAM)

**Example:**

```python
from app.services.local_ai_service import local_ai

result = local_ai.transcribe_audio(
    audio_file="path/to/bwc_audio.wav",
    language="en",
    word_timestamps=True
)

print(result["text"])  # Full transcript
for segment in result["segments"]:
    print(f"{segment['start']:.2f}s - {segment['end']:.2f}s: {segment['text']}")
```

**Use cases:**

- BWC video transcription
- Interview recordings
- Radio communications
- 911 calls

---

### 2. **pyannote.audio** (Speaker Diarization)

**What it does:** Identifies who is speaking when ("SPEAKER_00" = Officer, "SPEAKER_01" = Civilian)

**Setup:**

1. Create free Hugging Face account: https://huggingface.co
2. Accept model license: https://huggingface.co/pyannote/speaker-diarization
3. Get token: https://huggingface.co/settings/tokens
4. Set in .env: `HUGGINGFACE_TOKEN=your_token`

**Example:**

```python
from app.services.local_ai_service import local_ai

segments = local_ai.diarize_audio(
    audio_file="path/to/bwc_audio.wav",
    min_speakers=2,  # Officer + civilian
    max_speakers=5
)

for segment in segments:
    print(f"{segment['speaker']}: {segment['start']:.2f}s - {segment['end']:.2f}s")
```

**Use cases:**

- Separate officer vs civilian speech
- Identify multiple officers at scene
- Track who said what in interviews

---

### 3. **Tesseract OCR** (Document Text Extraction)

**What it does:** Extracts text from images and scanned PDFs

**Installation:**

- **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`

**Example:**

```python
import pytesseract
from PIL import Image

# Set tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Extract text from image
image = Image.open("path/to/document.jpg")
text = pytesseract.image_to_string(image)
print(text)
```

**Use cases:**

- OPRA response PDFs
- Tow invoices
- Police reports
- License plates in photos

---

### 4. **Real-ESRGAN** (AI Super-Resolution)

**What it does:** Upscales images/video 4x with AI (make license plates readable)

**Models:**

- `RealESRGAN_x4plus` - General purpose (photos, BWC)
- `RealESRNet_x4plus` - Real photos (sharper)
- `RealESRGAN_x4plus_anime` - Anime/cartoons

**Example:**

```python
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from PIL import Image
import numpy as np

# Load model
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
upsampler = RealESRGANer(
    scale=4,
    model_path='ai_models/realesrgan/RealESRGAN_x4plus.pth',
    model=model,
    tile=512
)

# Upscale image
image = Image.open("path/to/license_plate.jpg")
image_np = np.array(image)
output, _ = upsampler.enhance(image_np, outscale=4)
upscaled = Image.fromarray(output)
upscaled.save("upscaled.jpg")
```

**Use cases:**

- Enhance license plates
- Read badge numbers
- Improve low-res BWC footage
- Upscale faces for identification

---

### 5. **YOLO** (Object/Scene Detection)

**What it does:** Detects objects in images/video (handcuffs, vehicles, weapons, people)

**Models:**

- `yolov8n` - Nano (fastest)
- `yolov8s` - Small
- **`yolov8m`** - **⭐ RECOMMENDED** (balanced)
- `yolov8l` - Large
- `yolov8x` - Extra large (most accurate)

**Example:**

```python
from app.services.local_ai_service import local_ai

detections = local_ai.detect_objects(
    image_or_video="path/to/bwc_frame.jpg",
    confidence=0.5
)

for detection in detections:
    print(f"{detection['class']}: {detection['confidence']:.2f}")
    print(f"  Location: {detection['bbox']}")
```

**Detected objects:**

- person, car, truck, bus, motorcycle
- handcuffs (requires custom training)
- weapon, knife, gun (use with caution)
- traffic light, stop sign
- backpack, handbag, suitcase

**Use cases:**

- Auto-detect key events in BWC (handcuffs visible, person on ground)
- Vehicle tracking
- Scene analysis

---

### 6. **spaCy** (Entity Extraction)

**What it does:** Extracts names, places, organizations, dates from text

**Models:**

- `en_core_web_sm` - Small (fast)
- **`en_core_web_md`** - **⭐ RECOMMENDED** (balanced)
- `en_core_web_lg` - Large (most accurate)

**Example:**

```python
from app.services.local_ai_service import local_ai

text = "Officer Smith stopped John Doe on Route 9 in Atlantic County on January 22, 2026."

entities = local_ai.extract_entities(text)

for entity in entities:
    print(f"{entity['text']} ({entity['label']})")

# Output:
# Officer Smith (PERSON)
# John Doe (PERSON)
# Route 9 (FAC)
# Atlantic County (GPE)
# January 22, 2026 (DATE)
```

**Entity types:**

- PERSON (names)
- GPE (cities, counties, states)
- ORG (agencies, departments)
- DATE (dates, times)
- FAC (roads, buildings)
- LOC (locations)

**Use cases:**

- Extract names from transcripts
- Build entity relationship maps
- Auto-populate chronologies

---

### 7. **sentence-transformers** (Semantic Search)

**What it does:** Find relevant documents by meaning (not just keywords)

**Models:**

- **`all-MiniLM-L6-v2`** - **⭐ RECOMMENDED** (fast, lightweight)
- `all-mpnet-base-v2` - Higher quality (slower)

**Example:**

```python
from app.services.local_ai_service import local_ai

query = "officer commands to exit vehicle"

documents = [
    "The officer approached the vehicle and knocked on the window.",
    "Get out of the car now!",
    "Please step out of the vehicle, sir.",
    "The suspect was placed under arrest."
]

results = local_ai.semantic_search(query, documents, top_k=3)

for doc_idx, score in results:
    print(f"{score:.2f}: {documents[doc_idx]}")

# Output:
# 0.85: Please step out of the vehicle, sir.
# 0.78: Get out of the car now!
# 0.45: The officer approached the vehicle and knocked on the window.
```

**Use cases:**

- Find relevant BWC segments
- Search across all evidence by meaning
- Build "similar events" finder

---

## 🚀 Integration with eDiscovery Platform

The local AI tools are **automatically integrated** with the eDiscovery platform services:

### BWC Processing

```python
from app.services.bwc_processor_service import bwc_processor

result = await bwc_processor.process_bwc(
    bwc_file="path/to/bwc.mp4",
    evidence_id="EV-BWC-001",
    platform="axon"
)

# Uses local Whisper + pyannote automatically
print(result.transcript)  # Full transcript
print(result.speakers)    # Diarized speakers
```

### Media Enhancement

```python
from app.services.media_enhancement_service import media_enhancer

result = await media_enhancer.enhance_video(
    source_file="path/to/bwc.mp4",
    evidence_id="EV-BWC-001",
    quality_level=EnhancementQuality.MODERATE,
    apply_upscaling=True
)

# Uses local Real-ESRGAN automatically
print(result.enhanced_file)
```

### Document Processing

```python
from app.services.document_processor_service import document_processor

result = await document_processor.process_document(
    document_file="path/to/opra_response.pdf",
    evidence_id="EV-DOC-001",
    document_type=DocumentType.OPRA_RESPONSE
)

# Uses local Tesseract OCR automatically
print(result.ocr_text)
```

---

## 💻 System Requirements

### Minimum (CPU Only)

- **CPU:** 4 cores
- **RAM:** 8GB (16GB recommended)
- **Storage:** 20GB free (for models)
- **OS:** Windows 10+, Ubuntu 20.04+, macOS 10.15+

### Recommended (GPU Acceleration)

- **GPU:** NVIDIA GPU with 6GB+ VRAM
- **CUDA:** 11.7+ (for PyTorch)
- **RAM:** 16GB+
- **Storage:** 50GB free

### GPU Acceleration Benefits

- **Whisper:** 5-10x faster
- **pyannote:** 3-5x faster
- **Real-ESRGAN:** 10-20x faster
- **YOLO:** 5-10x faster

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'whisper'"

**Solution:**

```bash
pip install openai-whisper
```

### "CUDA out of memory"

**Solution:** Reduce batch size or use CPU

```bash
# In .env
WHISPER_DEVICE=cpu
YOLO_DEVICE=cpu
```

### "Tesseract not found"

**Solution:** Set tesseract path in .env

```bash
# Windows
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# Linux/Mac (should auto-detect)
which tesseract
```

### "pyannote requires HUGGINGFACE_TOKEN"

**Solution:**

1. Get token: https://huggingface.co/settings/tokens
2. Set in .env: `HUGGINGFACE_TOKEN=your_token`
3. Accept license: https://huggingface.co/pyannote/speaker-diarization

---

## 📊 Processing Speed Estimates

| Task                      | CPU (4-core) | GPU (NVIDIA RTX 3060) |
| ------------------------- | ------------ | --------------------- |
| Whisper (1hr audio)       | 15-20 min    | 2-3 min               |
| pyannote (1hr audio)      | 10-15 min    | 2-4 min               |
| Real-ESRGAN (1080p image) | 5-10 sec     | 0.5-1 sec             |
| YOLO (video frame)        | 0.5-1 sec    | 0.05-0.1 sec          |
| Tesseract OCR (1 page)    | 2-5 sec      | N/A (CPU only)        |
| spaCy (1000 words)        | 1-2 sec      | N/A (CPU only)        |

---

## 🆚 Local vs Cloud Comparison

| Feature     | Local AI            | Cloud APIs                                   |
| ----------- | ------------------- | -------------------------------------------- |
| **Cost**    | Free                | $0.006/min (Whisper), $0.001/page (Textract) |
| **Privacy** | Data stays local    | Data sent to third parties                   |
| **Speed**   | Depends on hardware | Fast (but network latency)                   |
| **Offline** | ✅ Yes              | ❌ No                                        |
| **Court**   | ✅ Fully auditable  | ⚠️ Black box                                 |
| **Scale**   | Limited by hardware | Unlimited                                    |

**Recommendation:** Use local AI for all processing. Only use cloud as fallback if local fails.

---

## 📚 Model Licenses

All models are **open-source** and **free for commercial use**:

- **Whisper:** MIT License
- **pyannote.audio:** MIT License (requires HF account)
- **Tesseract:** Apache 2.0
- **Real-ESRGAN:** BSD 3-Clause
- **YOLO:** AGPL-3.0 (use ultralytics commercial license if needed)
- **spaCy:** MIT License
- **sentence-transformers:** Apache 2.0

---

## 🎓 Training Resources

### Learn More

- Whisper: https://github.com/openai/whisper
- pyannote: https://github.com/pyannote/pyannote-audio
- Tesseract: https://github.com/tesseract-ocr/tesseract
- Real-ESRGAN: https://github.com/xinntao/Real-ESRGAN
- YOLO: https://docs.ultralytics.com
- spaCy: https://spacy.io
- sentence-transformers: https://www.sbert.net

### Custom Training

All models support custom training for your specific use case:

- Train YOLO to detect handcuffs, police vehicles, etc.
- Train spaCy to recognize officer names, badge numbers
- Fine-tune Whisper on police radio communications

---

## ✅ Quick Start Checklist

- [ ] Run `setup_local_ai_tools.py`
- [ ] Copy `.env.local_ai_example` to `.env`
- [ ] Set `HUGGINGFACE_TOKEN` in `.env`
- [ ] Install Tesseract (Windows/Mac)
- [ ] Test Whisper: `python -c "import whisper"`
- [ ] Test YOLO: `python -c "from ultralytics import YOLO"`
- [ ] Test spaCy: `python -c "import spacy"`
- [ ] Process first BWC video
- [ ] Review quality of transcripts
- [ ] Adjust settings in `.env` as needed

---

## 🆘 Support

For issues with local AI tools:

1. Check logs: `./logs/local_ai.log`
2. Verify installation: `python setup_local_ai_tools.py --verify-only`
3. Review troubleshooting section above
4. Check model documentation (links above)

**Remember: Local AI = Free + Private + Court-Defensible**
