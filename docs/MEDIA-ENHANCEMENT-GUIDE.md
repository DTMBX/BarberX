# Media Enhancement Guide - Non-Destructive Audio/Video/Image Processing

## 🎯 Overview

The Media Enhancement Service provides enhanced audio, video, and image processing with detailed audit trails to support legal review, while **ALWAYS preserving original evidence** in the immutable vault.

**Key Principle: ORIGINALS ARE NEVER MODIFIED**

Every enhancement creates a new derivative file with complete processing documentation, SHA-256 hashes, and quality metrics.

--

## 🔒 Non-Destructive Workflow

### How It Works

1. **Original Evidence**: Ingested into vault with SHA-256 hash
2. **Enhancement Request**: User specifies quality level and enhancements
3. **Processing**: New enhanced file created (original untouched)
4. **Dual Hashing**: Both original and enhanced files hashed
5. **Chain Logging**: Enhancement logged in chain-of-custody
6. **Quality Analysis**: Before/after metrics computed
7. **Court Flag**: Admissibility determined based on quality level

### Vault Safety

```
Original File (vault): WORM storage (read-only, chmod 0o444)
Enhanced File (output): Separate directory, marked as derivative
```

**Original file is physically protected and cannot be overwritten**

--

## 🎬 Audio Enhancement

### Capabilities

- **Noise Reduction**: Remove background noise (traffic, wind, radio static, engine hum, HVAC)
- **Normalization**: Balance volume levels to -20 dBFS target
- **Voice Enhancement**: Boost speech frequencies (85 Hz - 8 kHz)
- **Speaker Isolation**: Extract/enhance specific speaker from multi-person audio

### Noise Profiles

| Profile                       | Best For                            |
| ----------------------------- | ----------------------------------- |
| **Traffic/Road Noise**        | Roadside stops, highway patrol      |
| **Wind Noise**                | Outdoor BWC recordings              |
| **Radio Static/Interference** | Police radio crosstalk              |
| **Background Crowd**          | Multiple speakers, protests, crowds |
| **Vehicle Engine Hum**        | In-car recordings, transports       |
| **HVAC/Air Conditioning**     | Station interrogations              |
| **General**                   | Unknown or mixed noise sources      |

### Quality Levels

| Level          | Noise Reduction | Notes on Admissibility                                                             |
| -------------- | --------------- | ---------------------------------------------------------------------------------- |
| **Minimal**    | 6 dB            | May be admissible; final determination depends on jurisdiction and counsel review. |
| **Moderate**   | 12 dB           | Typically suitable when disclosed and reviewed by counsel.                         |
| **Aggressive** | 20 dB           | ⚠️ Caution (may affect admissibility); attorney review recommended.                |

### API Request

```bash
curl -X POST http://localhost:8000/api/v1/ediscovery/enhancement/audio \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "EV-BWC-001",
    "quality_level": "Moderate",
    "noise_profile": "Traffic/Road Noise",
    "apply_noise_reduction": true,
    "apply_normalization": true,
    "apply_voice_enhancement": true,
    "isolate_speaker": "SPEAKER_01"
  }'
```

### Response

```json
{
  "enhancement_id": "ENH-AUD-EV-BWC-001-20260122143022",
  "original_evidence_id": "EV-BWC-001",
  "enhanced_file": "./enhanced_media/audio_enhanced/ENH-AUD-EV-BWC-001-20260122143022.wav",
  "original_hash": "a3f2b1...",
  "enhanced_hash": "7e9d4c...",
  "processing_duration_seconds": 45.2,
  "court_admissible": true,
  "original_metrics": {
    "signal_to_noise_ratio_db": 8.5,
    "dynamic_range_db": 35.0,
    "clarity_score": 0.55
  },
  "enhanced_metrics": {
    "signal_to_noise_ratio_db": 20.5,
    "dynamic_range_db": 45.0,
    "clarity_score": 0.82
  },
  "enhancement_notes": "Audio enhanced using Moderate settings",
  "warning": "Original evidence preserved in vault. Enhanced version is derivative work."
}
```

**SNR Improvement: +12 dB** 🎯

--

## 📹 Video Enhancement

### Capabilities

- **Upscaling**: Increase resolution (720p → 1080p → 4K)
- **Stabilization**: Reduce camera shake/movement
- **Sharpening**: Improve clarity and detail
- **Denoising**: Remove video grain/noise
- **Contrast Enhancement**: Improve visibility in dark footage

### Upscaling Algorithms

| Algorithm     | Quality                  | Court Admissibility                                                                |
| ------------- | ------------------------ | ---------------------------------------------------------------------------------- |
| **Lanczos**   | High-quality traditional | May be admissible; final determination depends on jurisdiction and counsel review. |
| **Bicubic**   | Good traditional         | May be admissible; final determination depends on jurisdiction and counsel review. |
| **AI-ESRGAN** | AI super-resolution      | ⚠️ Disclose AI usage                                                               |

### Common Resolutions

- **1280x720** (720p HD)
- **1920x1080** (1080p Full HD) ⭐ Recommended
- **2560x1440** (1440p 2K)
- **3840x2160** (4K UHD)

### API Request

```bash
curl -X POST http://localhost:8000/api/v1/ediscovery/enhancement/video \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "EV-BWC-001",
    "quality_level": "Moderate",
    "apply_upscaling": true,
    "apply_stabilization": true,
    "apply_sharpening": true,
    "apply_denoising": true,
    "target_resolution": "1920x1080"
  }'
```

### Response

```json
{
  "enhancement_id": "ENH-VID-EV-BWC-001-20260122143045",
  "original_evidence_id": "EV-BWC-001",
  "enhanced_file": "./enhanced_media/video_enhanced/ENH-VID-EV-BWC-001-20260122143045.mp4",
  "original_hash": "b2e5c8...",
  "enhanced_hash": "9f3a1d...",
  "processing_duration_seconds": 320.5,
  "court_admissible": true,
  "original_metrics": {
    "sharpness_score": 0.45,
    "contrast_ratio": 1.2,
    "brightness_average": 95.0,
    "resolution": "1280x720"
  },
  "enhanced_metrics": {
    "sharpness_score": 0.78,
    "contrast_ratio": 1.6,
    "brightness_average": 110.0,
    "resolution": "1920x1080"
  },
  "enhancement_notes": "Video enhanced to 1920x1080"
}
```

**Sharpness Improvement: +73%** 🎯

--

## 🖼️ Image Enhancement

### Capabilities

- **Super-Resolution**: AI/traditional upscaling (2x, 4x, 8x)
- **Clarity Enhancement**: Unsharp masking for improved detail
- **Contrast Adjustment**: Improve visibility
- **Brightness Normalization**: Balance lighting

### Target Scales

| Scale  | Use Case                                     |
| ------ | -------------------------------------------- |
| **2x** | License plates, faces from moderate distance |
| **4x** | Small text, distant objects                  |
| **8x** | Maximum detail (use with caution)            |

### API Request

```bash
curl -X POST http://localhost:8000/api/v1/ediscovery/enhancement/image \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "EV-IMG-001",
    "quality_level": "Moderate",
    "apply_super_resolution": true,
    "apply_clarity": true,
    "apply_contrast": true,
    "target_scale": 2.0
  }'
```

### Response

```json
{
  "enhancement_id": "ENH-IMG-EV-IMG-001-20260122143110",
  "original_evidence_id": "EV-IMG-001",
  "enhanced_file": "./enhanced_media/image_enhanced/ENH-IMG-EV-IMG-001-20260122143110.png",
  "original_hash": "c4f7a9...",
  "enhanced_hash": "2b8e5f...",
  "processing_duration_seconds": 12.3,
  "court_admissible": true,
  "original_metrics": {
    "sharpness_score": 0.52,
    "contrast_ratio": 1.3,
    "brightness_average": 115.0,
    "resolution": "640x480"
  },
  "enhanced_metrics": {
    "sharpness_score": 0.81,
    "contrast_ratio": 1.5,
    "brightness_average": 125.0,
    "resolution": "1280x960"
  },
  "enhancement_notes": "Image enhanced 2.0x"
}
```

--

## 📊 Quality Comparison

### Compare Original vs Enhanced

```bash
curl http://localhost:8000/api/v1/ediscovery/enhancement/compare/ENH-AUD-EV-BWC-001-20260122143022?original_evidence_id=EV-BWC-001
```

### Response

```json
{
  "enhancement_id": "ENH-AUD-EV-BWC-001-20260122143022",
  "original_evidence_id": "EV-BWC-001",
  "enhancement_type": "Audio Noise Reduction",
  "quality_level": "Moderate (Balance Enhancement/Authenticity)",
  "original_metrics": {
    "signal_to_noise_ratio_db": 8.5,
    "dynamic_range_db": 35.0,
    "clarity_score": 0.55
  },
  "enhanced_metrics": {
    "signal_to_noise_ratio_db": 20.5,
    "dynamic_range_db": 45.0,
    "clarity_score": 0.82
  },
  "improvements": {
    "snr_improvement_db": 12.0
  },
  "court_admissible": true,
  "recommendation": "EXCELLENT: Significant audio clarity improvement. Recommended for court exhibits."
}
```

--

## ⚖️ Court Admissibility Guidelines

### May Be Admissible (Minimal/Moderate)

✅ **Minimal Enhancement**

- Subtle noise reduction (6 dB)
- Light sharpening
- Standard upscaling (Lanczos)
- Volume normalization
- **Use for**: Court exhibits, depositions, trial

✅ **Moderate Enhancement**

- Balanced noise reduction (12 dB)
- Moderate sharpening
- Standard stabilization
- **Use for**: Court exhibits with disclosure of enhancement

### Use with Caution (Aggressive)

⚠️ **Aggressive Enhancement**

- Heavy noise reduction (20 dB)
- AI super-resolution
- Maximum sharpening
- **Use for**: Internal investigation only
- **Disclose**: If used in court, expert testimony required

### Best Practice

1. **Always provide original** alongside enhanced version
2. **Disclose enhancement** in exhibit index
3. **Include processing settings** in chain-of-custody report
4. **Compare side-by-side** for jury/judge
5. **Expert testimony** if challenged (Daubert hearing)

--

## 🔬 Processing Pipeline (Production)

### Audio Enhancement Pipeline

```
1. Extract audio from video (if needed)
   → ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 44100 output.wav

2. Apply noise reduction
   → librosa/noisereduce: reduce_noise(y=audio, sr=sample_rate)

3. Apply normalization
   → ffmpeg -af loudnorm=I=-20:TP=-1.5:LRA=11

4. Voice enhancement (boost 1-4 kHz)
   → ffmpeg -af equalizer=f=3000:width_type=h:width=2000:g=6

5. Speaker isolation (if requested)
   → Use diarization results to extract specific speaker segments
```

### Video Enhancement Pipeline

```
1. Upscaling
   → ffmpeg -vf scale=1920:1080:flags=lanczos
   → OR Real-ESRGAN: realesrgan-ncnn-vulkan -i input.mp4 -o output.mp4

2. Stabilization
   → ffmpeg two-pass:
     Pass 1: ffmpeg -vf vidstabdetect=shakiness=5
     Pass 2: ffmpeg -vf vidstabtransform=smoothing=30

3. Sharpening
   → ffmpeg -vf unsharp=5:5:1.0:5:5:0.0

4. Denoising
   → ffmpeg -vf hqdn3d=4:3:6:4.5
```

### Image Enhancement Pipeline

```
1. Super-resolution
   → PIL: img.resize(new_size, Image.LANCZOS)
   → OR Real-ESRGAN: realesrgan-ncnn-vulkan -i input.jpg -o output.png -s 4

2. Clarity (unsharp mask)
   → OpenCV: cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)

3. Contrast
   → PIL: ImageEnhance.Contrast(img).enhance(1.2)
```

--

## 📦 Installation

### Required Dependencies

```bash
# Core audio/video processing
pip install librosa noisereduce soundfile pydub
pip install opencv-python pillow moviepy

# OCR/document processing
pip install pytesseract pdf2image

# Excel database
pip install openpyxl pandas
```

### Optional (Production Quality)

```bash
# AI super-resolution (best quality)
pip install realesrgan
# OR
pip install basicsr facexlib gfpgan

# Cloud OCR/transcription
pip install boto3  # AWS Textract/Transcribe
pip install google-cloud-vision  # Google Cloud Vision
pip install azure-cognitiveservices-vision-computervision  # Azure OCR

# Audio diarization
pip install pyannote.audio
```

### System Dependencies

```bash
# ffmpeg (required for video/audio processing)
# Windows: Download from https://ffmpeg.org/download.html
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg

# Tesseract OCR (for document processing)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

--

## 🎯 Real-World Use Cases

### Case 1: BWC Audio Enhancement

**Scenario**: Officer commands inaudible due to traffic noise

**Solution**:

```json
{
  "evidence_id": "EV-BWC-STOP-001",
  "quality_level": "Moderate",
  "noise_profile": "Traffic/Road Noise",
  "apply_noise_reduction": true,
  "apply_voice_enhancement": true
}
```

**Result**: Commands now clearly audible for court playback

--

### Case 2: Video Upscaling

**Scenario**: License plate too small to read (720p BWC)

**Solution**:

```json
{
  "evidence_id": "EV-BWC-STOP-001",
  "quality_level": "Moderate",
  "apply_upscaling": true,
  "target_resolution": "1920x1080"
}
```

**Result**: Plate numbers readable after upscaling

--

### Case 3: Image Super-Resolution

**Scenario**: Badge number unclear in body-worn photo

**Solution**:

```json
{
  "evidence_id": "EV-IMG-BADGE-001",
  "quality_level": "Moderate",
  "apply_super_resolution": true,
  "target_scale": 4.0
}
```

**Result**: Badge number identifiable

--

## 📋 Chain-of-Custody Disclosure

Every enhancement automatically logs in chain-of-custody:

```
Event Type: Enhancement
Evidence ID: EV-BWC-001
Timestamp: 2026-01-22T14:30:22Z
User: Attorney Smith
Notes: Audio enhanced: Moderate, Traffic/Road Noise
Enhancement ID: ENH-AUD-EV-BWC-001-20260122143022
Original Hash: a3f2b1...
Enhanced Hash: 7e9d4c...
Settings: {
  "noise_reduction_db": 12.0,
  "normalization_target_db": -20.0,
  "preserve_frequency_range": [85, 8000],
  "upscaling_algorithm": "lanczos"
}
```

**This disclosure satisfies FRCP 26(a)(1) and Daubert requirements for court exhibits.**

--

## ⚠️ Important Warnings

### DO

✅ **Always preserve originals** in vault
✅ **Disclose enhancements** in exhibit index
✅ **Use Minimal/Moderate** for court exhibits
✅ **Compare side-by-side** before/after
✅ **Include processing settings** in discovery
✅ **Provide expert testimony** if challenged

### DON'T

❌ **Never use Aggressive** for court without disclosure
❌ **Never claim enhanced = original**
❌ **Never hide enhancement** from opposing counsel
❌ **Never rely on AI upscaling** without expert validation
❌ **Never delete original** after enhancement

--

## 🆘 Support

For questions about media enhancement:

1. Check court admissibility flag in API response
2. Review side-by-side comparison report
3. Use Minimal/Moderate quality levels for safety
4. Consult with forensic audio/video expert if challenged
5. Always provide original alongside enhanced version

**Remember: When in doubt, use the original. Enhancement is for clarity, not to create evidence.**
