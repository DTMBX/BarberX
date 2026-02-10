# Ubuntu System Packages — Evident Technologies

Required system-level dependencies for the Evident forensic stack on
Ubuntu 24.04 LTS (deploy target).

These packages must be installed before `pip install` of the Python
requirements. They are not managed by pip and must be provisioned via
`apt` or equivalent package manager.

---

## Section 0 — Build Essentials

Required for compiling Python C extensions during `pip install`.

```bash
sudo apt update && sudo apt install -y \
  build-essential \
  pkg-config \
  python3.12-dev \
  python3.12-venv
```

| Package            | Purpose                                    |
| ------------------ | ------------------------------------------ |
| `build-essential`  | GCC, make, libc headers for C compilation  |
| `pkg-config`       | Locates system libraries for build scripts |
| `python3.12-dev`   | Python headers for native extension builds |
| `python3.12-venv`  | Virtual environment support                |

---

## Section 1 — Cryptography Libraries

Required by: `cryptography`, `PyNaCl`, `rfc3161ng`

```bash
sudo apt install -y \
  libssl-dev \
  libffi-dev \
  libsodium-dev
```

| Package         | Purpose                                        |
| --------------- | ---------------------------------------------- |
| `libssl-dev`    | OpenSSL headers — TLS, X.509, hashing          |
| `libffi-dev`    | Foreign function interface — cffi/ctypes builds |
| `libsodium-dev` | NaCl/libsodium — Ed25519, sealed boxes          |

---

## Section 2 — Document Processing

Required by: `pytesseract`, `pdf2image`, `pymupdf`, `lxml`, `Pillow`

```bash
sudo apt install -y \
  tesseract-ocr \
  tesseract-ocr-eng \
  poppler-utils \
  libxml2-dev \
  libxslt1-dev \
  libjpeg-dev \
  libpng-dev \
  libtiff-dev \
  libwebp-dev \
  zlib1g-dev
```

| Package              | Purpose                                    |
| -------------------- | ------------------------------------------ |
| `tesseract-ocr`      | OCR engine for scanned document extraction |
| `tesseract-ocr-eng`  | English language data for Tesseract        |
| `poppler-utils`      | PDF rendering tools (`pdftotext`, etc.)    |
| `libxml2-dev`        | XML parser headers for lxml                |
| `libxslt1-dev`       | XSLT headers for lxml                      |
| `libjpeg-dev`        | JPEG codec for Pillow                      |
| `libpng-dev`         | PNG codec for Pillow                       |
| `libtiff-dev`        | TIFF codec for Pillow                      |
| `libwebp-dev`        | WebP codec for Pillow                      |
| `zlib1g-dev`         | Compression for Pillow / PDF libraries     |

---

## Section 3 — Media Processing

Required by: `ffmpeg-python`, `moviepy`, `pydub`, `librosa`, `opencv-python-headless`

```bash
sudo apt install -y \
  ffmpeg \
  mediainfo \
  libexif-dev \
  libgl1 \
  libglib2.0-0 \
  libsndfile1-dev \
  libsm6 \
  libxext6
```

| Package           | Purpose                                         |
| ----------------- | ----------------------------------------------- |
| `ffmpeg`          | Audio/video transcoding and stream manipulation |
| `mediainfo`       | Media container and codec metadata extraction   |
| `libexif-dev`     | EXIF metadata reading for forensic analysis     |
| `libgl1`          | OpenGL runtime for OpenCV headless              |
| `libglib2.0-0`    | GLib runtime for OpenCV                         |
| `libsndfile1-dev` | Audio file reading for librosa/soundfile        |
| `libsm6`          | X11 session management (OpenCV dependency)      |
| `libxext6`        | X11 extension library (OpenCV dependency)       |

For EXIF/metadata forensics, also install ExifTool:

```bash
sudo apt install -y libimage-exiftool-perl
```

---

## Section 4 — Database

Required by: `psycopg`, `SQLAlchemy`, `alembic`

```bash
sudo apt install -y \
  postgresql-client \
  libpq-dev
```

| Package              | Purpose                                 |
| -------------------- | --------------------------------------- |
| `postgresql-client`  | psql CLI for database administration    |
| `libpq-dev`          | PostgreSQL headers for psycopg C build  |

---

## Section 5 — Task Queue Infrastructure

Required by: `celery[redis]`, `redis`

Redis server (install on deploy host or use managed instance):

```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
```

---

## Combined Install (All Sections)

Single command for full provisioning:

```bash
sudo apt update && sudo apt install -y \
  build-essential \
  pkg-config \
  python3.12-dev \
  python3.12-venv \
  libssl-dev \
  libffi-dev \
  libsodium-dev \
  tesseract-ocr \
  tesseract-ocr-eng \
  poppler-utils \
  libxml2-dev \
  libxslt1-dev \
  libjpeg-dev \
  libpng-dev \
  libtiff-dev \
  libwebp-dev \
  zlib1g-dev \
  ffmpeg \
  mediainfo \
  libimage-exiftool-perl \
  libexif-dev \
  libgl1 \
  libglib2.0-0 \
  libsndfile1-dev \
  libsm6 \
  libxext6 \
  postgresql-client \
  libpq-dev \
  redis-server
```

---

## Windows Development Notes

On Windows, many of these system libraries are bundled with the Python
wheel distributions (pre-compiled binaries). The following external tools
must be installed separately:

| Tool            | Windows Path (current)                     |
| --------------- | ------------------------------------------ |
| FFmpeg          | `C:\ffmpeg-lgpl`                           |
| Tesseract OCR   | `C:\Program Files\Tesseract-OCR`           |
| ImageMagick     | System PATH                                |
| Ghostscript     | System PATH                                |
| PostgreSQL      | Managed via Docker or cloud instance       |
| Redis           | Docker: `docker run -p 6379:6379 redis:7`  |

Ensure these paths are on the system `PATH` or configured in `.env`.

---

## Version Verification

After installation, verify key tools:

```bash
python3.12 --version          # Python 3.12.x
ffmpeg -version               # ffmpeg 6.x+
tesseract --version           # tesseract 5.x
exiftool -ver                 # 12.x+
psql --version                # psql 16.x
redis-cli --version           # redis-cli 7.x
```
