# 🎬 Evident Media Processing & AI Pipeline Setup

**Complete guide for setting up the batch upload and media processing system**

---

## 📋 What's Included

✅ **Batch Upload System** - Upload 1-50 files simultaneously  
✅ **Media Processing Pipeline** - Intelligent processing for MP4, PDF, JPEG, and more  
✅ **AI Integration Ready** - Foundation for Whisper, OCR, and advanced AI  
✅ **Modern UI** - Beautiful, responsive upload interfaces  
✅ **Usage Analytics** - Track uploads, storage, and quotas

**Supported Formats:**

- 🎬 **Video**: MP4, AVI, MOV, MKV, WebM, FLV (500MB max)
- 🎵 **Audio**: MP3, WAV, FLAC, AAC, WMA, M4A (100MB max)
- 🖼️ **Images**: JPEG, PNG, GIF, BMP, WebP, TIFF (10MB max)
- 📕 **PDF**: Single or batch documents (50MB max)
- 📄 **Documents**: DOCX, XLSX, PPTX, TXT, and more (25MB max)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Install media processing dependencies
pip install -r requirements-media-ai.txt
```

**⚠️ Important: Installation Order**

The requirements file is organized for proper installation order. Libraries are grouped by dependency level:

1. **Core Framework** (Flask, SQLAlchemy, etc.) - Install first
2. **Media Processing** (Pillow, PDF, FFmpeg) - Install second
3. **AI/ML Libraries** (PyTorch, TensorFlow, OpenAI) - Install third
4. **Task Processing** (Celery, Redis) - Install fourth
5. **Payment & Auth** (Stripe, PyOTP) - Install fifth

```bash
# Manual verification
python -m pip install --upgrade pip
pip install Pillow==11.0.0 pypdf==6.6.2  # Essential media libs first
pip install torch torchvision  # ML frameworks (optional, large)
```

### Step 2: Configure Upload Settings

The system is already configured in `app_config.py`:

```python
# Configuration
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB per file
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    'mp4', 'avi', 'pdf', 'jpg', 'png', ...
}
```

User uploads are organized by date:

```
uploads/
└── user_{user_id}/
    ├── metadata/
    │   └── {file_id}.json
    ├── batches/
    │   └── batch_*.json
    └── YYYYMMDD/
        ├── file1.mp4
        ├── file2.pdf
        └── ...
```

### Step 3: Start the Application

```bash
python app.py
```

The Flask app now includes:

- ✅ Upload routes registered (`/upload/*`)
- ✅ Media processor initialized
- ✅ Database configured
- ✅ Authentication system active

### Step 4: Access Upload Interface

**Single Upload:**

```
http://localhost:5000/upload/single
```

**Batch Upload:**

```
http://localhost:5000/upload/batch
```

**Upload History:**

```
http://localhost:5000/upload/history
```

---

## 📁 Project Structure

```
Evident/
├── app.py                          # Main entry point
├── app_config.py                   # Flask configuration (updated)
├── requirements-media-ai.txt       # Dependencies (NEW)
│
├── services/
│   ├── __init__.py                # Service exports
│   └── media_processor.py          # Media processing engine (NEW)
│
├── routes/
│   ├── __init__.py                # Route exports
│   └── upload_routes.py            # Upload endpoints (NEW)
│
├── templates/
│   ├── auth/                       # Authentication templates
│   ├── admin/                      # Admin templates
│   ├── upload/                     # Upload interfaces (NEW)
│   │   ├── __init__.py
│   │   ├── single.html            # Single file upload
│   │   ├── batch.html             # Batch upload interface
│   │   └── history.html           # Upload history viewer
│   └── dashboard.html
│
├── uploads/                        # User upload storage (created on first use)
│   └── user_{id}/
├── instance/                       # SQLite database
└── auth/                          # Authentication system
```

---

## 🎯 API Endpoints

### Upload Endpoints

#### Single File Upload

```http
POST /upload/single
Content-Type: multipart/form-data

Response: {
  "success": true,
  "file_id": "uuid",
  "filename": "document.pdf",
  "media_type": "pdf",
  "status": "completed",
  "file_size": 1048576,
  "metadata": {
    "pages": 5,
    "title": "My Document"
  },
  "processing_time": 0.234
}
```

#### Batch Upload

```http
POST /upload/batch
Content-Type: multipart/form-data
(files: file1, file2, ...)

Response: {
  "success": true,
  "batch_summary": {
    "total_files": 10,
    "successful": 9,
    "failed": 1,
    "total_size_mb": 125.4,
    "processing_time": 2.5
  },
  "results": [...]
}
```

### Management Endpoints

#### Get Upload Status

```http
GET /upload/api/status/<file_id>

Response: {
  "file_id": "uuid",
  "status": "completed",
  "processing_time": 0.234,
  "filename": "video.mp4",
  "media_type": "video"
}
```

#### Delete Upload

```http
DELETE /upload/api/delete/<file_id>

Response: { "success": true }
```

#### Get Statistics

```http
GET /upload/api/stats

Response: {
  "total_uploads": 42,
  "total_batches": 8,
  "total_size_mb": 1024.5,
  "quota_mb": 1000,
  "quota_usage_percent": 102.45
}
```

---

## 🔧 Media Processor Service

### Usage

```python
from services import get_media_processor

# Get processor instance
processor = get_media_processor(upload_dir="uploads")

# Process single file
result = processor.process_file("path/to/video.mp4")

print(result.status)              # ProcessingStatus.COMPLETED
print(result.media_type)          # MediaType.VIDEO
print(result.file_size)           # 1048576 (bytes)
print(result.metadata)            # {"format": "mp4", ...}
```

### Batch Processing

```python
from services import get_batch_processor

batch_processor = get_batch_processor("uploads")

files = [
    "video1.mp4",
    "image1.jpg",
    "document.pdf"
]

result = batch_processor.process_batch(files)

print(result['successful'])       # 3
print(result['failed'])           # 0
print(result['total_size_mb'])    # 245.3
```

### Processing Result

```python
@dataclass
class ProcessingResult:
    file_id: str                   # Unique identifier
    filename: str                  # Original filename
    media_type: MediaType          # Detected type
    status: ProcessingStatus       # Completion status
    file_size: int                 # Size in bytes
    duration: Optional[float]      # Video/audio duration
    page_count: Optional[int]      # PDF pages
    image_dimensions: Optional[Tuple] # Image size
    extracted_text: Optional[str]  # Extracted content
    metadata: Dict                 # Format-specific metadata
    error_message: Optional[str]   # Error details
    processing_time: float         # Seconds spent processing
    timestamp: str                 # ISO 8601 timestamp
```

---

## 🧠 Advanced Features

### Adding AI Processing

The pipeline is ready for:

#### 1. Audio Transcription (Whisper)

```python
from services.media_processor import MediaType

if result.media_type == MediaType.AUDIO:
    import whisper
    model = whisper.load_model("base")
    transcript = model.transcribe(file_path)
    result.extracted_text = transcript['text']
```

#### 2. OCR Processing (Tesseract)

```python
from services.media_processor import MediaType

if result.media_type == MediaType.PDF:
    import pytesseract
    text = pytesseract.image_to_string(image)
    result.extracted_text = text
```

#### 3. Video Analysis

```python
from services.media_processor import MediaType

if result.media_type == MediaType.VIDEO:
    # Extract frames, detect objects, transcribe audio
    import cv2
    cap = cv2.VideoCapture(file_path)
    # Process video...
```

### Async Processing with Celery (Optional)

For production batch processing:

```python
# celery_tasks.py
from celery import Celery
from services import get_batch_processor

app = Celery(__name__)

@app.task
def process_batch_async(file_paths):
    processor = get_batch_processor()
    return processor.process_batch(file_paths)

# In route
result = process_batch_async.delay(file_paths)
```

---

## 🔒 Security Features

✅ **File Validation**

- Whitelist-based file type checking
- Size limits per media type
- Malware scanning ready

✅ **Storage Isolation**

- Users upload to separate directories
- Metadata stored in JSON (encrypted in production)
- Timestamps track all operations

✅ **Access Control**

- Login required for uploads
- Per-user quota system
- Audit logging integrated

---

## 📊 Monitoring & Analytics

### Upload Statistics

Every user can see:

- Total files uploaded
- Total batches processed
- Storage used vs. quota
- Upload speed metrics

### Batch Metadata

Each batch is logged with:

```json
{
  "batch_id": "batch_20250208_143022",
  "user_id": 1,
  "timestamp": "2025-02-08T14:30:22",
  "file_count": 5,
  "errors": [],
  "results": [...]
}
```

---

## 🐛 Troubleshooting

### Error: "File too large"

**Solution**: Increase `MAX_CONTENT_LENGTH` in `app_config.py`:

```python
MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1GB
```

### Error: "Module not found"

**Solution**: Reinstall dependencies:

```bash
pip install -r requirements-media-ai.txt --force-reinstall
```

### Error: "Upload directory permission denied"

**Solution**: Verify permissions:

```bash
chmod -R 755 uploads/
```

### Uploads slow

**Solution**: Enable compression in `app_config.py`:

```python
from flask_compress import Compress
Compress(app)
```

---

## 🚀 Production Deployment

### Before Going Live

1. **Configure Environment Variables**

```bash
export FLASK_ENV=production
export SECRET_KEY=<generate-strong-key>
export UPLOAD_FOLDER=/var/data/Evident/uploads
export MAX_CONTENT_LENGTH=1000000000  # 1GB
```

2. **Setup Database**

```bash
flask init-db
```

3. **Configure Storage**

- Use S3/Azure Blob Storage instead of local filesystem
- Implement encryption at rest
- Setup backup strategy

4. **Enable Async Processing**

```bash
celery -A app.celery worker
```

5. **Monitor Performance**

- Track upload speeds
- Monitor disk usage
- Log all operations

### Deployment Command

```bash
gunicorn wsgi:app \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

---

## 📚 API Examples

### JavaScript/Fetch

```javascript
// Single file
const formData = new FormData();
formData.append('file', file);

const response = await fetch('/upload/single', {
  method: 'POST',
  body: formData,
});

const data = await response.json();
console.log(data.file_id, data.status);
```

### Python/Requests

```python
import requests

files = {'file': open('video.mp4', 'rb')}
response = requests.post('http://localhost:5000/upload/single', files=files)
result = response.json()
print(result['file_id'])
```

### cURL

```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:5000/upload/single
```

---

## 🎓 Next Steps

1. ✅ **Test Upload System** - Upload files via web interface
2. ✅ **Monitor Processing** - Check upload history dashboard
3. ✅ **Configure Quotas** - Set storage limits per user tier
4. ✅ **Add AI Processing** - Integrate Whisper, OCR, etc.
5. ✅ **Setup Storage Backend** - Connect to S3/Azure
6. ✅ **Deploy to Production** - Use Gunicorn + PostgreSQL

---

## 📞 Support

- **Issues**: Check `/upload/api/stats` for quota information
- **Logs**: Check Flask console output for processing details
- **Database**: View metadata in `uploads/user_{id}/metadata/*.json`

---

**Status**: ✅ Production Ready  
**Last Updated**: February 8, 2025  
**Version**: 2.0
