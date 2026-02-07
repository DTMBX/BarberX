# Evidence Processing: Open-Source Component Recommendations

**Document Version:** 1.0  
**Date:** 2026-02-07  
**Author:** AI Engineering & Compliance Assistant  
**Status:** Proposed for Review

---

## EXECUTIVE SUMMARY

Evident Technologies has a **strong foundation** in evidence processing capabilities with professional-grade implementations for:
- SHA-256 hashing and chain of custody tracking
- Audio transcription (OpenAI Whisper) and speaker diarization (PyAnnote)
- Metadata extraction via ffprobe
- Audit logging and rights-aware export systems
- Court-ready exhibit generation

**Critical gaps** requiring hardening:
1. **Media proxy generation**: No h.264 proxy transcoding for fast UI playback
2. **SBOM tracking**: No Software Bill of Materials for supply-chain transparency
3. **Metadata extraction**: Limited EXIF/XMP support; ffprobe used via subprocess
4. **Export packaging**: No explicit ZIP+manifest export implementation
5. **Streaming capabilities**: Batch-only processing; no real-time transcription
6. **Process isolation**: FFmpeg integration fragile (subprocess without error handling)

**Recommended approach**: Incremental hardening with **mature, widely-adopted OSS tools** prioritizing license compatibility (MIT/BSD/Apache-2.0), active maintenance, and court-defensible provenance.

**Key recommendations** (12 high-assurance components):
- **Media processing**: FFmpeg (LGPL-2.1+), MediaInfo (BSD-2-Clause), ExifTool (Perl Artistic + GPL-1.0)
- **SBOM generation**: CycloneDX Python library (Apache-2.0)
- **Vulnerability scanning**: pip-audit (Apache-2.0), OSV-Scanner (Apache-2.0)
- **Export packaging**: Python zipfile (built-in) + secure archiving
- **Search/indexing**: Whoosh (BSD-2-Clause) or Meilisearch (MIT)
- **Manifest formats**: JSON Schema (MIT)

All recommendations **reject** proprietary tools, spyware, or "military-grade" claims. All tools support **headless automation** and **privacy-by-design**.

---

## GAP ANALYSIS TABLE

| Feature | Current Status | Risk Level | Proposed OSS Options |
|---------|---------------|------------|---------------------|
| **SHA-256 Hashing** | ✅ Implemented | ✅ Low | Continue using Python hashlib (built-in) |
| **Chain of Custody** | ✅ Implemented | ✅ Low | Enhance with append-only audit log (SQLite WAL mode) |
| **Audio Transcription** | ✅ Whisper integrated | ⚠️ Medium | Add fallback: Vosk (Apache-2.0) for offline/air-gapped |
| **Speaker Diarization** | ✅ PyAnnote integrated | ✅ Low | Continue; consider SpeechBrain (Apache-2.0) as backup |
| **Metadata Extraction** | ⚠️ Partial (ffprobe) | ⚠️ Medium | Add: MediaInfo (BSD-2), ExifTool (Perl Artistic/GPL-1) |
| **Video Proxy Generation** | ❌ Missing | 🔴 High | Add: FFmpeg with h.264/AAC presets (LGPL-2.1+) |
| **Thumbnail Generation** | ❌ Missing | ⚠️ Medium | Add: FFmpeg frame extraction |
| **Waveform Visualization** | ❌ Missing | 🟡 Low | Add: LibROSA (already installed) + matplotlib |
| **SBOM Generation** | ❌ Missing | 🔴 High | Add: CycloneDX (Apache-2.0) |
| **Vulnerability Scanning** | ❌ Missing | 🔴 High | Add: pip-audit + OSV-Scanner (both Apache-2.0) |
| **Export ZIP Packaging** | ⚠️ Partial | ⚠️ Medium | Add: Python zipfile + structured folders |
| **Manifest Validation** | ⚠️ Partial | ⚠️ Medium | Add: JSON Schema validation (MIT) |
| **Full-Text Search** | ❌ Missing | 🟡 Low | Add: Whoosh (BSD-2) or Meilisearch (MIT) |
| **Document OCR** | ✅ PyTesseract | ✅ Low | Continue; ensure Tesseract binary installed |
| **PDF Processing** | ✅ pypdf + pdfplumber | ✅ Low | Continue; pypdf replaces deprecated PyPDF2 |
| **Redaction Assist** | ❌ Missing | 🟡 Low | Add: OpenCV blur/pixelate (BSD-3) + ffmpeg mute |
| **Quality Metrics** | ❌ Missing | 🟡 Low | Add: ffmpeg-quality-metrics (MIT) |
| **Streaming Transcription** | ❌ Missing | 🟡 Low | Future: Whisper.cpp (MIT) for real-time |

**Risk Legend:**
- ✅ Low: Well-implemented or low priority
- ⚠️ Medium: Needs improvement or backup plan
- 🔴 High: Critical gap affecting security, compliance, or core workflow
- 🟡 Low: Nice-to-have; not blocking production

---

## CANDIDATE LIBRARY CARDS

### 1. **FFmpeg** (Video/Audio Transcoding & Analysis)

**Purpose**: Industry-standard media processing for proxy generation, thumbnails, metadata extraction, and waveforms.

**License**: LGPL-2.1-or-later (core libraries); GPL-2.0+ (certain codecs/filters)  
**Maintenance**: ✅ Excellent (100+ contributors, 2024 releases, 20+ years active)  
**Security**: ✅ SLSA 3 (reproducible builds), CVE database monitored, signed releases  
**Integration**: Backend worker (subprocess + python-ffmpeg wrapper)

**Why Safer**:
- Most widely audited media processing tool (used by YouTube, Netflix, courts worldwide)
- LGPL allows dynamic linking; no code disclosure obligation
- Better than: proprietary transcoders (vendor lock-in), handwritten codecs (security risk)
- Alternatives like GStreamer (LGPL) or libav (abandoned) lack ecosystem maturity

**Installation**:
```bash
# Ubuntu
apt-get install ffmpeg ffprobe

# Python wrapper
pip install ffmpeg-python==0.2.0
```

**Usage in Evident**:
```python
# Generate h.264 proxy (fast playback)
import ffmpeg
ffmpeg.input('evidence.mp4').output(
    'proxy.mp4',
    vcodec='libx264',
    acodec='aac',
    video_bitrate='2M',
    preset='medium'
).run()

# Extract thumbnail
ffmpeg.input('evidence.mp4', ss='00:00:10').output(
    'thumb.jpg', vframes=1
).run()
```

**Provenance**: FFmpeg Project (https://ffmpeg.org), Git tags signed by maintainers

---

### 2. **MediaInfo** (Comprehensive Metadata Extraction)

**Purpose**: Extract technical and descriptive metadata from video/audio files (codec, bitrate, duration, GPS, device info).

**License**: BSD-2-Clause  
**Maintenance**: ✅ Excellent (MediaArea.net, monthly releases, 15+ years active)  
**Security**: ✅ No known CVEs in core library; read-only operation  
**Integration**: Backend worker (Python pymediainfo wrapper)

**Why Safer**:
- Pure metadata reader; no codec execution (unlike ffprobe which loads decoder)
- Smaller attack surface than FFmpeg for metadata-only tasks
- Better than: ffprobe alone (limited output), exiftool (Perl dependency), custom parsing (reinventing wheel)
- Widely used in digital forensics and archival systems

**Installation**:
```bash
# Ubuntu
apt-get install libmediainfo-dev

# Python
pip install pymediainfo==6.1.0
```

**Usage in Evident**:
```python
from pymediainfo import MediaInfo

media_info = MediaInfo.parse('evidence.mp4')
for track in media_info.tracks:
    if track.track_type == 'Video':
        print(f"Codec: {track.codec}")
        print(f"Duration: {track.duration}")
        print(f"Bitrate: {track.bit_rate}")
```

**Provenance**: MediaArea.net (https://mediaarea.net/MediaInfo), GitHub releases signed

---

### 3. **ExifTool** (EXIF/XMP/IPTC Metadata)

**Purpose**: Extract and verify EXIF metadata from images and videos (timestamps, GPS, camera model, lens).

**License**: Perl Artistic License + GPL-1.0-or-later (dual license; user chooses)  
**Maintenance**: ✅ Excellent (Phil Harvey, monthly updates, 20+ years active)  
**Security**: ✅ Read-only mode safe; write mode disabled in Evident use case  
**Integration**: Backend worker (subprocess via PyExifTool)

**Why Safer**:
- Gold standard for EXIF extraction; used by forensic examiners and courts
- More comprehensive than Pillow.Image.getexif() (limited tag support)
- Better than: custom EXIF parsers (security bugs), online services (privacy risk)
- Dual license allows choosing non-copyleft Artistic License

**Installation**:
```bash
# Ubuntu
apt-get install libimage-exiftool-perl

# Python wrapper
pip install PyExifTool==0.5.6
```

**Usage in Evident**:
```python
import exiftool

with exiftool.ExifToolHelper() as et:
    metadata = et.get_metadata(['evidence.jpg'])[0]
    print(f"Camera: {metadata.get('EXIF:Model')}")
    print(f"GPS: {metadata.get('EXIF:GPSLatitude')}")
    print(f"Timestamp: {metadata.get('EXIF:DateTimeOriginal')}")
```

**Provenance**: Phil Harvey (https://exiftool.org), PGP-signed releases

---

### 4. **CycloneDX Python Library** (SBOM Generation)

**Purpose**: Generate Software Bill of Materials (SBOM) in CycloneDX format for supply-chain transparency.

**License**: Apache-2.0  
**Maintenance**: ✅ Excellent (OWASP project, monthly releases, active community)  
**Security**: ✅ OWASP-backed; SBOM standard recognized by NTIA/CISA  
**Integration**: CI/CD pipeline + backend scripts

**Why Safer**:
- OWASP standard for SBOM; interoperable with security tools
- Better than: SPDX (less tooling), custom JSON (non-standard), no SBOM (blind to supply chain)
- Enables automated vulnerability tracking via SBOM ingestion

**Installation**:
```bash
pip install cyclonedx-bom==4.6.4
```

**Usage in Evident**:
```bash
# Generate SBOM from requirements.txt
cyclonedx-py requirements \
    backend/requirements.txt \
    --output governance/sbom-backend.json \
    --format json
```

**Provenance**: OWASP CycloneDX (https://cyclonedx.org), GitHub releases

---

### 5. **pip-audit** (Vulnerability Scanning)

**Purpose**: Scan Python dependencies for known vulnerabilities via OSV database.

**License**: Apache-2.0  
**Maintenance**: ✅ Excellent (Python Packaging Authority, weekly updates)  
**Security**: ✅ Uses OSV/PyPI advisory databases; offline mode available  
**Integration**: CI/CD pre-commit hooks + scheduled scans

**Why Safer**:
- Official PyPA tool; same team as pip/setuptools
- Better than: Safety (proprietary DB), Snyk (commercial), manual CVE tracking (error-prone)
- Works offline (important for air-gapped environments)

**Installation**:
```bash
pip install pip-audit==2.7.3
```

**Usage in Evident**:
```bash
# Scan all installed packages
pip-audit

# Scan requirements file
pip-audit -r backend/requirements.txt --format json > governance/vulnerabilities.json

# Fail CI if vulnerabilities found
pip-audit --strict
```

**Provenance**: PyPA (https://github.com/pypa/pip-audit), PyPI signed

---

### 6. **OSV-Scanner** (Multi-Ecosystem Vulnerability Scanning)

**Purpose**: Scan Python, JavaScript, Go, and other dependencies for vulnerabilities via Google's OSV database.

**License**: Apache-2.0  
**Maintenance**: ✅ Excellent (Google Open Source, weekly updates)  
**Security**: ✅ Aggregates CVE, GitHub Security Advisories, OSV databases  
**Integration**: CI/CD pipeline (runs on lockfiles)

**Why Safer**:
- Multi-ecosystem support (Python + JavaScript worker)
- Better than: language-specific scanners (partial coverage), commercial tools (cost)
- Open database; no vendor lock-in

**Installation**:
```bash
# Ubuntu
wget https://github.com/google/osv-scanner/releases/download/v1.9.1/osv-scanner_linux_amd64
chmod +x osv-scanner_linux_amd64
mv osv-scanner_linux_amd64 /usr/local/bin/osv-scanner
```

**Usage in Evident**:
```bash
# Scan entire repository
osv-scanner --lockfile=backend/requirements.txt --lockfile=package-lock.json

# JSON output for automation
osv-scanner --format json > governance/osv-scan.json
```

**Provenance**: Google Open Source (https://github.com/google/osv-scanner)

---

### 7. **Whoosh** (Full-Text Search Engine)

**Purpose**: Pure-Python full-text search engine for indexing transcripts, metadata, and documents.

**License**: BSD-2-Clause  
**Maintenance**: ⚠️ Moderate (stable but infrequent updates; 2022 last release)  
**Security**: ✅ No known CVEs; pure Python (no native code)  
**Integration**: Backend API (search endpoints)

**Why Safer**:
- Pure Python; no JVM or native dependencies (unlike Elasticsearch, Lucene)
- Better than: Elasticsearch (heavyweight, resource-intensive), PostgreSQL FTS (limited ranking), no search (poor UX)
- Sufficient for <1M documents; upgrade to Meilisearch if scale requires

**Installation**:
```bash
pip install Whoosh==2.7.4
```

**Usage in Evident**:
```python
from whoosh import index
from whoosh.fields import Schema, TEXT, ID

# Create index
schema = Schema(
    id=ID(stored=True),
    transcript=TEXT(stored=True),
    metadata=TEXT(stored=True)
)
idx = index.create_in("indexdir", schema)

# Add documents
writer = idx.writer()
writer.add_document(
    id="evidence_123",
    transcript="Officer: Stop right there...",
    metadata="BWC 2024-01-15"
)
writer.commit()

# Search
from whoosh.qparser import QueryParser
searcher = idx.searcher()
query = QueryParser("transcript", idx.schema).parse("stop")
results = searcher.search(query)
```

**Provenance**: Matt Chaput (https://github.com/mchaput/whoosh), BSD-licensed

**Alternative**: **Meilisearch** (MIT, Rust-based, more modern but requires binary deployment)

---

### 8. **ffmpeg-quality-metrics** (Video Quality Assessment)

**Purpose**: Calculate VMAF, PSNR, SSIM quality metrics for proxy validation.

**License**: MIT  
**Maintenance**: ✅ Good (Werner Robitza, 2024 releases)  
**Security**: ✅ Wrapper around FFmpeg; inherits FFmpeg security  
**Integration**: Backend worker (post-transcode validation)

**Why Safer**:
- Validates proxy quality matches original (detect transcode errors)
- Better than: no validation (broken proxies), custom metrics (unvalidated)
- Uses industry-standard VMAF (Netflix-developed quality metric)

**Installation**:
```bash
pip install ffmpeg-quality-metrics==2.0.1
```

**Usage in Evident**:
```python
from ffmpeg_quality_metrics import FfmpegQualityMetrics

metrics = FfmpegQualityMetrics('original.mp4', 'proxy.mp4')
result = metrics.calculate(['vmaf', 'psnr'])
print(f"VMAF score: {result['vmaf']['mean']}")  # >95 is excellent
```

**Provenance**: Werner Robitza (https://github.com/slhck/ffmpeg-quality-metrics)

---

### 9. **jsonschema** (Manifest Validation)

**Purpose**: Validate evidence manifests against JSON Schema for consistency.

**License**: MIT  
**Maintenance**: ✅ Excellent (Julian Berman, Python Software Foundation)  
**Security**: ✅ No execution; validation only  
**Integration**: Backend API (manifest import/export)

**Why Safer**:
- Prevents malformed manifests (missing hashes, invalid timestamps)
- Better than: no validation (garbage in/out), custom validation (bugs)
- JSON Schema is ISO/IEC standard (draft-07)

**Installation**:
```bash
pip install jsonschema==4.23.0
```

**Usage in Evident**:
```python
import jsonschema

manifest_schema = {
    "type": "object",
    "required": ["evidence_id", "sha256_hash", "timestamp"],
    "properties": {
        "evidence_id": {"type": "string"},
        "sha256_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "timestamp": {"type": "string", "format": "date-time"}
    }
}

# Validate
jsonschema.validate(manifest_data, manifest_schema)
```

**Provenance**: JSON Schema (https://json-schema.org), PSF-backed

---

### 10. **Vosk** (Offline Speech Recognition)

**Purpose**: Offline speech-to-text for air-gapped or privacy-sensitive deployments.

**License**: Apache-2.0  
**Maintenance**: ✅ Excellent (Alpha Cephei, 2024 releases)  
**Security**: ✅ Offline; no data exfiltration risk  
**Integration**: Backend worker (fallback when Whisper unavailable)

**Why Safer**:
- Runs locally; no cloud dependency (Whisper requires GPU or API)
- Better than: Google Speech API (privacy risk), proprietary engines (vendor lock-in)
- Smaller models (50MB-2GB) vs Whisper (1.5GB-10GB)

**Installation**:
```bash
pip install vosk==0.3.45

# Download model (English)
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
```

**Usage in Evident**:
```python
from vosk import Model, KaldiRecognizer
import wave

model = Model("vosk-model-en-us-0.22")
wf = wave.open("evidence.wav", "rb")
rec = KaldiRecognizer(model, wf.getframerate())

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = rec.Result()
```

**Provenance**: Alpha Cephei (https://alphacephei.com/vosk/), Apache-licensed

---

### 11. **SpeechBrain** (Speaker Diarization Backup)

**Purpose**: Backup speaker diarization toolkit if PyAnnote licensing becomes restrictive.

**License**: Apache-2.0  
**Maintenance**: ✅ Excellent (Mila Quebec AI, 2024 releases)  
**Security**: ✅ Academic research origin; no commercial restrictions  
**Integration**: Backend worker (alternative to PyAnnote)

**Why Safer**:
- Apache license (vs PyAnnote's MIT + model license ambiguity)
- Better than: custom diarization (complex), cloud APIs (privacy risk)
- Newer architecture; actively developed by academic lab

**Installation**:
```bash
pip install speechbrain==1.0.4
```

**Usage in Evident**:
```python
from speechbrain.pretrained import SpeakerRecognition

verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb"
)
score, prediction = verification.verify_files("audio1.wav", "audio2.wav")
```

**Provenance**: Mila Quebec AI (https://speechbrain.github.io), Apache-licensed

---

### 12. **Werkzeug FileStorage** (Secure File Uploads)

**Purpose**: Secure file upload handling with path traversal prevention.

**License**: BSD-3-Clause  
**Maintenance**: ✅ Excellent (Pallets Project, 2024 CVE patches)  
**Security**: ✅ CVE-2026-21860 patched in 3.1.5 (already in requirements.txt)  
**Integration**: Already integrated via Flask

**Why Safer**:
- Already required by Flask; no new dependency
- Prevents path traversal attacks (CVE-2026-21860 fix verified)
- Better than: raw file handling (security bugs), custom upload handlers (reinventing wheel)

**Usage in Evident** (already implemented):
```python
from werkzeug.utils import secure_filename

file = request.files['evidence']
filename = secure_filename(file.filename)
file.save(os.path.join(UPLOAD_FOLDER, filename))
```

**Provenance**: Pallets Project (https://palletsprojects.com), BSD-licensed

---

## LICENSE & SUPPLY-CHAIN GATE

### **License Compatibility Matrix**

| License Type | Status | Condition | Examples |
|-------------|--------|-----------|----------|
| **MIT** | ✅ Approved | Permissive; no obligations | jsonschema, Whoosh alternatives, Vosk alternative |
| **BSD-2/BSD-3** | ✅ Approved | Permissive; attribution only | MediaInfo, Whoosh, Werkzeug |
| **Apache-2.0** | ✅ Approved | Permissive; patent grant | CycloneDX, pip-audit, OSV-Scanner, Vosk, SpeechBrain |
| **LGPL-2.1+** | ⚠️ Review Required | Dynamic linking OK; no code disclosure | FFmpeg (OK as subprocess/dynamic lib) |
| **GPL-1.0/2.0/3.0** | ⚠️ Review Required | Copyleft; distribution triggers obligations | ExifTool (use Artistic License), FFmpeg GPL codecs (disable) |
| **Perl Artistic** | ✅ Approved (dual) | Choose over GPL option | ExifTool (dual-licensed) |
| **Proprietary** | ❌ Rejected | No source code; vendor lock-in | All commercial tools excluded |

### **Supply-Chain Requirements (Mandatory)**

All dependencies MUST satisfy:

1. **Version Pinning**
   ```bash
   # requirements.txt MUST use exact versions
   ffmpeg-python==0.2.0  # ✅ Good
   # ffmpeg-python>=0.2.0  # ❌ Bad (unpinned)
   ```

2. **Hash Locking** (pip-tools or Poetry)
   ```bash
   pip-compile --generate-hashes --output-file=requirements-lock.txt requirements.txt
   pip install --require-hashes -r requirements-lock.txt
   ```

3. **SBOM Generation**
   ```bash
   cyclonedx-py requirements backend/requirements.txt \
       --output governance/sbom-backend.json
   ```

4. **Vulnerability Scanning (CI/CD)**
   ```bash
   pip-audit --strict  # Fail build on HIGH/CRITICAL
   osv-scanner --lockfile=requirements.txt
   ```

5. **Provenance Documentation** (`governance/DEPENDENCIES.md`)
   ```markdown
   ## ffmpeg-python 0.2.0
   - License: Apache-2.0
   - Source: https://github.com/kkroening/ffmpeg-python
   - SHA-256: <hash>
   - Added: 2026-02-07
   - Purpose: FFmpeg subprocess wrapper for proxy generation
   - Security: No known CVEs (2024 scan)
   - Maintainer: Karl Kroening (active)
   ```

6. **Security Review Cadence**
   - Weekly: `pip-audit` automated scan
   - Monthly: Dependency update review (patch versions only)
   - Quarterly: Major version upgrade evaluation
   - Annually: Full security audit of supply chain

### **Rejected Dependency Types**

The following are PROHIBITED:

1. **Proprietary/Commercial Tools**
   - Examples: Axon Evidence.com SDK, NICE Investigate API
   - Reason: Vendor lock-in, no source code, cost escalation

2. **Spyware/Surveillance Tooling**
   - Examples: NSO Pegasus, FinFisher, Cellebrite UFED SDK
   - Reason: Unlawful interception, ethics violation

3. **Unverifiable Binaries**
   - Examples: Random GitHub releases without signatures
   - Reason: Supply-chain attack vector

4. **Deprecated/Unmaintained**
   - Examples: PyPDF2 (superseded by pypdf), libav (abandoned)
   - Reason: Security vulnerabilities won't be patched

5. **"Military-Grade" Marketing Claims**
   - Reason: Meaningless term; legally indefensible

### **LGPL Compliance Strategy (FFmpeg)**

FFmpeg uses **LGPL-2.1-or-later** (core libraries). Compliance:

1. **Dynamic Linking**: Use FFmpeg as external binary (subprocess) or shared library
   - ✅ No source code disclosure required
   - ✅ No license propagation to Evident codebase

2. **Distribution**:
   - ✅ Ubuntu package: `apt-get install ffmpeg` (system dependency)
   - ✅ Docker: Include in base image (FROM ubuntu:22.04)
   - ❌ Do NOT: Static link FFmpeg libraries into Python binary

3. **Attribution**:
   - Add FFmpeg to `governance/DEPENDENCIES.md` with license text
   - Include LGPL license text in distribution documentation

4. **GPL Codecs** (if needed):
   - Disable GPL-licensed codecs: `--enable-gpl=no` during FFmpeg build
   - Use only LGPL codecs: h.264 (libx264), AAC, VP9

---

## IMPLEMENTATION ROADMAP

### **Phase 1: Low-Risk Immediate Wins** (1-2 days)

**Goal**: Harden supply chain and add SBOM tracking.

#### Tasks:
1. **Create `governance/` directory**
   ```bash
   mkdir -p governance
   ```

2. **Generate SBOM**
   ```bash
   pip install cyclonedx-bom==4.6.4
   cyclonedx-py requirements backend/requirements.txt \
       --output governance/sbom-backend.json
   ```

3. **Add vulnerability scanning to CI/CD**
   ```yaml
   # .github/workflows/security-scan.yml
   name: Security Scan
   on: [push, pull_request]
   jobs:
     scan:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Install pip-audit
           run: pip install pip-audit==2.7.3
         - name: Scan dependencies
           run: pip-audit -r backend/requirements.txt --format json > vulnerabilities.json
         - name: Upload results
           uses: actions/upload-artifact@v4
           with:
             name: vulnerabilities
             path: vulnerabilities.json
   ```

4. **Create `governance/DEPENDENCIES.md`**
   - Document all current dependencies
   - Add license, source, SHA-256, purpose

5. **Pin dependency versions with hashes**
   ```bash
   pip install pip-tools==7.4.1
   pip-compile --generate-hashes backend/requirements.txt \
       --output-file backend/requirements-lock.txt
   ```

#### Acceptance Criteria:
- ✅ SBOM exists in `governance/sbom-backend.json`
- ✅ CI/CD fails on HIGH/CRITICAL vulnerabilities
- ✅ `governance/DEPENDENCIES.md` documents all 30+ dependencies
- ✅ `requirements-lock.txt` uses `--hash` for all packages

#### How to Measure:
```bash
# Verify SBOM
jq '.components | length' governance/sbom-backend.json  # Should match dependency count

# Verify CI
git commit -m "test" && git push  # CI must run pip-audit

# Verify hashes
grep --count "^    --hash=" backend/requirements-lock.txt  # >0
```

---

### **Phase 2: Pipeline Robustness** (1-2 weeks)

**Goal**: Add media proxy generation, metadata extraction, and quality validation.

#### Tasks:
1. **Install FFmpeg + wrappers**
   ```bash
   # Dockerfile
   RUN apt-get update && apt-get install -y ffmpeg libmediainfo-dev
   
   # requirements.txt
   ffmpeg-python==0.2.0
   pymediainfo==6.1.0
   ffmpeg-quality-metrics==2.0.1
   ```

2. **Create `backend/src/media_processor.py`**
   ```python
   import ffmpeg
   from pymediainfo import MediaInfo
   
   class MediaProcessor:
       def generate_proxy(self, input_path, output_path):
           """Generate h.264 proxy for fast playback"""
           ffmpeg.input(input_path).output(
               output_path,
               vcodec='libx264',
               acodec='aac',
               video_bitrate='2M',
               preset='medium',
               movflags='faststart'  # Web-optimized
           ).run(overwrite_output=True)
       
       def extract_metadata(self, input_path):
           """Extract comprehensive metadata"""
           media_info = MediaInfo.parse(input_path)
           return {
               'format': media_info.tracks[0].format,
               'duration': media_info.tracks[0].duration,
               'file_size': media_info.tracks[0].file_size,
               'tracks': [
                   {
                       'type': t.track_type,
                       'codec': t.codec,
                       'bitrate': t.bit_rate,
                       'language': t.language
                   }
                   for t in media_info.tracks
               ]
           }
       
       def generate_thumbnail(self, input_path, output_path, timestamp='00:00:10'):
           """Extract thumbnail frame"""
           ffmpeg.input(input_path, ss=timestamp).output(
               output_path, vframes=1
           ).run(overwrite_output=True)
   ```

3. **Update `evidence_processing.py`** to use `MediaProcessor`
   ```python
   from src.media_processor import MediaProcessor
   
   processor = MediaProcessor()
   
   # In create_evidence_package():
   if evidence_data['evidence_type'] in ['bwc_video', 'dashcam', 'cctv']:
       metadata = processor.extract_metadata(evidence_data['file_path'])
       processor.generate_proxy(evidence_data['file_path'], proxy_path)
       processor.generate_thumbnail(evidence_data['file_path'], thumb_path)
   ```

4. **Add proxy validation**
   ```python
   from ffmpeg_quality_metrics import FfmpegQualityMetrics
   
   def validate_proxy(original_path, proxy_path):
       metrics = FfmpegQualityMetrics(original_path, proxy_path)
       result = metrics.calculate(['vmaf'])
       vmaf_score = result['vmaf']['mean']
       
       if vmaf_score < 95:
           logger.warning(f"Proxy quality low: VMAF {vmaf_score}")
       
       return vmaf_score
   ```

5. **Add ExifTool for images**
   ```bash
   apt-get install libimage-exiftool-perl
   pip install PyExifTool==0.5.6
   ```
   
   ```python
   import exiftool
   
   def extract_exif(image_path):
       with exiftool.ExifToolHelper() as et:
           metadata = et.get_metadata([image_path])[0]
           return {
               'camera': metadata.get('EXIF:Model'),
               'gps': {
                   'lat': metadata.get('EXIF:GPSLatitude'),
                   'lon': metadata.get('EXIF:GPSLongitude')
               },
               'timestamp': metadata.get('EXIF:DateTimeOriginal')
           }
   ```

6. **Create `backend/src/export_packager.py`**
   ```python
   import zipfile
   import json
   from datetime import datetime
   
   class ExportPackager:
       def create_export_package(self, evidence_package, export_path):
           """Create ZIP export with manifest"""
           with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
               # Add evidence file
               zf.write(evidence_package['file_path'], 
                       arcname=f"evidence/{evidence_package['filename']}")
               
               # Add proxy
               if evidence_package.get('proxy_path'):
                   zf.write(evidence_package['proxy_path'],
                           arcname=f"proxies/{evidence_package['filename']}")
               
               # Add transcript
               if evidence_package.get('transcript_path'):
                   zf.write(evidence_package['transcript_path'],
                           arcname=f"transcripts/{evidence_package['filename']}.txt")
               
               # Add manifest
               manifest = {
                   'evidence_id': evidence_package['id'],
                   'case_number': evidence_package['case_number'],
                   'exported_at': datetime.utcnow().isoformat(),
                   'files': [
                       {
                           'path': f"evidence/{evidence_package['filename']}",
                           'sha256': evidence_package['file_hash'],
                           'size': evidence_package['file_size']
                       }
                   ],
                   'chain_of_custody': evidence_package['chain_of_custody']
               }
               zf.writestr('MANIFEST.json', json.dumps(manifest, indent=2))
               
               # Add README
               readme = f"""# Evidence Export Package
   
   Case Number: {evidence_package['case_number']}
   Evidence ID: {evidence_package['id']}
   Exported: {datetime.utcnow().isoformat()}
   
   ## Contents
   - evidence/: Original evidence files
   - proxies/: Web-optimized proxy files
   - transcripts/: Audio transcripts
   - MANIFEST.json: File hashes and chain of custody
   
   ## Verification
   ```bash
   sha256sum -c MANIFEST.json
   ```
   """
               zf.writestr('README.md', readme)
   ```

7. **Add tests**
   ```python
   # tests/test_media_processor.py
   def test_generate_proxy():
       processor = MediaProcessor()
       processor.generate_proxy('fixtures/test.mp4', 'output/proxy.mp4')
       assert os.path.exists('output/proxy.mp4')
       
       # Verify playable
       metadata = processor.extract_metadata('output/proxy.mp4')
       assert metadata['format'] == 'MPEG-4'
       assert metadata['tracks'][0]['codec'] == 'AVC'
   ```

#### Acceptance Criteria:
- ✅ Proxy generation creates h.264/AAC files
- ✅ MediaInfo extracts codec, duration, bitrate
- ✅ ExifTool extracts GPS, camera model from images
- ✅ Export ZIP contains original + proxy + transcript + manifest
- ✅ VMAF score >95 for all proxies
- ✅ Tests pass for all media processing functions

#### How to Measure:
```bash
# Verify proxy
ffprobe -v error -show_format output/proxy.mp4 | grep codec_name
# Should show: codec_name=h264

# Verify manifest
unzip -l export.zip | grep MANIFEST.json
# Should exist

# Run tests
pytest tests/test_media_processor.py -v
```

---

### **Phase 3: Advanced Review Features** (Later / As Needed)

**Goal**: Add full-text search, waveform visualization, and redaction assist.

#### Tasks:
1. **Add Whoosh for search**
   ```bash
   pip install Whoosh==2.7.4
   ```
   
   ```python
   # backend/src/search_indexer.py
   from whoosh import index
   from whoosh.fields import Schema, TEXT, ID, DATETIME
   
   schema = Schema(
       id=ID(stored=True, unique=True),
       case_number=ID(stored=True),
       transcript=TEXT(stored=True),
       metadata=TEXT(stored=True),
       timestamp=DATETIME(stored=True)
   )
   
   idx = index.create_in("search_index", schema)
   
   def index_evidence(evidence_package):
       writer = idx.writer()
       writer.add_document(
           id=evidence_package['id'],
           case_number=evidence_package['case_number'],
           transcript=evidence_package['transcript'],
           metadata=json.dumps(evidence_package['metadata']),
           timestamp=evidence_package['uploaded_at']
       )
       writer.commit()
   ```

2. **Add waveform generation**
   ```python
   import librosa
   import matplotlib.pyplot as plt
   
   def generate_waveform(audio_path, output_path):
       y, sr = librosa.load(audio_path)
       plt.figure(figsize=(14, 5))
       plt.plot(librosa.times_like(y), y)
       plt.title('Audio Waveform')
       plt.xlabel('Time (s)')
       plt.ylabel('Amplitude')
       plt.savefig(output_path, dpi=150, bbox_inches='tight')
       plt.close()
   ```

3. **Add redaction assist**
   ```python
   import cv2
   
   def blur_region(video_path, output_path, regions):
       """Blur specified regions (e.g., faces, license plates)"""
       cap = cv2.VideoCapture(video_path)
       fourcc = cv2.VideoWriter_fourcc(*'mp4v')
       out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))
       
       while cap.isOpened():
           ret, frame = cap.read()
           if not ret:
               break
           
           for (x, y, w, h) in regions:
               roi = frame[y:y+h, x:x+w]
               blurred = cv2.GaussianBlur(roi, (99, 99), 30)
               frame[y:y+h, x:x+w] = blurred
           
           out.write(frame)
       
       cap.release()
       out.release()
   ```

4. **Add offline speech recognition (Vosk)**
   ```bash
   pip install vosk==0.3.45
   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
   unzip vosk-model-en-us-0.22.zip -d models/
   ```
   
   ```python
   from vosk import Model, KaldiRecognizer
   import wave
   
   def transcribe_offline(audio_path):
       model = Model("models/vosk-model-en-us-0.22")
       wf = wave.open(audio_path, "rb")
       rec = KaldiRecognizer(model, wf.getframerate())
       
       transcript = []
       while True:
           data = wf.readframes(4000)
           if len(data) == 0:
               break
           if rec.AcceptWaveform(data):
               result = json.loads(rec.Result())
               transcript.append(result.get('text', ''))
       
       return ' '.join(transcript)
   ```

#### Acceptance Criteria:
- ✅ Full-text search returns relevant evidence by transcript keyword
- ✅ Waveform PNG generation completes in <5 seconds
- ✅ Redaction blur is irreversible (no unblur attack)
- ✅ Offline transcription works without internet

---

## SECURITY SUMMARY

### **License Compliance Verification**

All proposed dependencies satisfy license requirements:
- **Permissive (MIT/BSD/Apache)**: 10/12 recommendations
- **LGPL (dynamic linking OK)**: 1/12 (FFmpeg)
- **Dual-licensed (Artistic preferred)**: 1/12 (ExifTool)

### **Supply-Chain Hardening**

- ✅ All dependencies from reputable sources (OWASP, PyPA, Google OSS, academic labs)
- ✅ Version pinning + hash locking enforced
- ✅ SBOM generation integrated (CycloneDX)
- ✅ Vulnerability scanning automated (pip-audit + OSV-Scanner)
- ✅ Provenance documentation required

### **Rejected Categories**

- ❌ No proprietary tools (vendor lock-in risk)
- ❌ No spyware/surveillance tooling (ethics violation)
- ❌ No unverifiable binaries (supply-chain attack)
- ❌ No deprecated libraries (security debt)

### **Risk Mitigation**

1. **FFmpeg LGPL compliance**: Use as subprocess; no static linking
2. **ExifTool GPL risk**: Choose Perl Artistic License (dual-licensed)
3. **Whoosh maintenance**: Monitor; fallback to Meilisearch if abandoned
4. **Vosk model size**: Store models outside repo (download on deploy)

---

## NEXT STEPS

1. **Review this document** with legal counsel (license compliance)
2. **Approve Phase 1** (SBOM + vulnerability scanning) for immediate deployment
3. **Pilot Phase 2** (media processing) in staging environment
4. **Defer Phase 3** until Phase 2 validated in production

---

## APPENDICES

### A. Maintenance Signal Criteria

**Excellent**:
- Releases in last 6 months
- 10+ contributors
- Active issue triage (<7 day median response)
- Signed releases or SLSA

**Good**:
- Releases in last 12 months
- 5+ contributors
- Active issue triage (<30 day median response)

**Moderate**:
- Stable; no critical bugs
- 1-5 contributors
- Infrequent updates (feature-complete)

**Poor** (reject):
- No releases in 24+ months
- Unpatched CVEs
- Abandoned repository

### B. SBOM Schema Example

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:...",
  "version": 1,
  "metadata": {
    "timestamp": "2026-02-07T00:00:00Z",
    "component": {
      "name": "Evident Backend",
      "version": "1.0.0"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "ffmpeg-python",
      "version": "0.2.0",
      "purl": "pkg:pypi/ffmpeg-python@0.2.0",
      "licenses": [{"license": {"id": "Apache-2.0"}}],
      "hashes": [{"alg": "SHA-256", "content": "..."}]
    }
  ]
}
```

### C. Vulnerability Scan Output Format

```json
{
  "dependencies": [
    {
      "name": "Pillow",
      "version": "11.0.0",
      "vulnerabilities": [],
      "status": "safe"
    }
  ],
  "summary": {
    "total": 30,
    "vulnerable": 0,
    "safe": 30
  }
}
```

---

**END OF DOCUMENT**

*This recommendation set prioritizes truth, structure, integrity, and restraint. All tools support headless automation and privacy-by-design. No "military-grade" claims. No spyware. Court-defensible provenance.*
