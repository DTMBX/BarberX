# Evident AI Tools - Dependencies Setup Guide

## ✅ Test Results Summary

**All core dependencies are installed and working!**

### Installed & Working

- ✓ Flask & Flask extensions
- ✓ OpenAI & Whisper AI
- ✓ PyTesseract (Python library)
- ✓ Tesseract OCR binary (v5.4.0)
- ✓ Pillow (image processing)
- ✓ PyPDF (PDF processing)
- ✓ LangChain (AI orchestration)
- ✓ Sentence Transformers (embeddings)
- ✓ ChromaDB (vector database)

### Optional (Not Required)

- ⚠ spaCy - Optional for NER (Named Entity Recognition)
- ⚠ FAISS - Optional for similarity search (ChromaDB works instead)

---

## 🚀 Quick Start

### 1. Verify Installation

```bash
python test_tools.py
```

### 2. Test Flask Routes

```bash
python test_flask_routes.py
```

### 3. Start the Server

```bash
python app.py
```

### 4. Access Tools Hub

Open browser: `http://localhost:5000/tools`

---

## 📦 Installing Optional Dependencies

### SpaCy (Optional - for NER)

**Issue**: SpaCy requires C++ build tools on Windows and fails to compile.

**Workaround**: SpaCy is **not required** for any of the AI tools to function.
The legal analysis, OCR, transcription, and BWC analysis all work without it.

**If you really need it**:

1. Install Visual Studio Build Tools:
   https://visualstudio.microsoft.com/downloads/
2. Install spaCy: `pip install spacy`
3. Download model: `python -m spacy download en_core_web_sm`

### FAISS (Optional - for similarity search)

ChromaDB is already installed and provides vector search functionality. FAISS is
optional.

```bash
pip install faiss-cpu
```

---

## 🔧 Tesseract OCR Binary

**Status**: ✅ Already installed (v5.4.0)

If you need to reinstall or update:

### Windows Installation

```bash
# Option 1: Chocolatey (recommended)
choco install tesseract

# Option 2: Manual download
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

### Verify Installation

```bash
tesseract --version
```

---

## 🧪 Testing Individual Tools

### Test OCR

```python
import pytesseract
from PIL import Image

# Check version
print(pytesseract.get_tesseract_version())

# Test with image
img = Image.open('test.png')
text = pytesseract.image_to_string(img)
print(text)
```

### Test Whisper

```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")
print(result["text"])
```

### Test OpenAI

```python
import openai

# Requires OPENAI_API_KEY environment variable
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

---

## 🔍 Troubleshooting

### Redis Warnings

```
WARNING: Redis unavailable, using in-memory cache
```

**Solution**: Redis is optional. The app works fine without it using in-memory
caching.

To install Redis (optional):

```bash
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Or use WSL: sudo apt install redis-server
```

### Scikit-learn Version Warning

```
InconsistentVersionWarning: Trying to unpickle estimator from version 1.8.0 when using version 1.6.1
```

**Solution**: This is a warning, not an error. The app works fine. To fix:

```bash
pip install --upgrade scikit-learn
```

### Database Initialization

The app automatically creates SQLite database and tables on first run.

---

## 📊 Dependency Matrix

| Tool                      | Required Dependencies                 | Optional Dependencies             |
| ------------------------- | ------------------------------------- | --------------------------------- |
| **OCR**                   | pytesseract, Pillow, Tesseract binary | -                                 |
| **Whisper Transcription** | openai-whisper, torch                 | GPU drivers for faster processing |
| **Legal Analysis**        | openai, langchain                     | spaCy (not needed)                |
| **BWC Analysis**          | whisper, pytesseract, openai          | -                                 |
| **PDF Processing**        | pypdf, pdfplumber, Pillow             | -                                 |
| **Vector Search**         | chromadb OR faiss                     | sentence-transformers             |
| **Chat/AI**               | openai, langchain                     | -                                 |

---

## 🎯 Production Deployment

### Required Environment Variables

```bash
# Required
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host/db  # or sqlite:///Evident.db

# Optional but recommended
OPENAI_API_KEY=sk-...
HUGGINGFACE_TOKEN=hf_...
POSTHOG_API_KEY=phc_...  # Analytics
SENTRY_DSN=https://...   # Error tracking
STRIPE_SECRET_KEY=sk_...  # Payments
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional
REDIS_URL=redis://localhost:6379
```

### Install Production Dependencies

```bash
pip install -r requirements.txt
```

### Production Server

```bash
# Use gunicorn instead of Flask dev server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## ✅ Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Check Python packages
python test_tools.py

# 2. Check Flask routes
python test_flask_routes.py

# 3. Start server
python app.py

# 4. Test in browser
# Visit: http://localhost:5000/tools
# Try: Upload a test image to OCR tool
# Try: Navigate to BWC dashboard
# Try: Access legal analysis tools
```

---

## 🎉 Success Indicators

When everything is working, you should see:

1. **Dependency Test**: All required packages show ✓
2. **Route Test**: All tool routes registered ✓
3. **Server Start**: No errors, listening on port 5000
4. **Tools Hub**: Beautiful landing page with 9 AI tools
5. **OCR Tool**: Can upload and extract text from images
6. **BWC Dashboard**: Can upload videos for analysis
7. **Legal Analysis**: Can scan transcripts for violations

---

## 📞 Support

If you encounter issues:

1. Check `test_tools.py` output for missing dependencies
2. Check `test_flask_routes.py` output for route errors
3. Check Flask console for runtime errors
4. Review `AI-TOOLS-INTERFACE-SUMMARY.md` for architecture details

**Common Issues**:

- Missing Tesseract binary → Install from link above
- OpenAI API errors → Set `OPENAI_API_KEY` environment variable
- Database errors → Delete `Evident.db` and restart (dev only)
- Port 5000 in use → Change port in `app.py` or kill existing process
