"""
Evidence Processing Engine
===========================
Deterministic, auditable processing of evidence files.

Supported operations:
  - PDF text extraction (native + OCR via pdfplumber + pytesseract)
  - Video metadata extraction (ffprobe) + thumbnail/proxy generation (ffmpeg)
  - Image OCR (PIL + pytesseract)
  - DOCX text extraction (python-docx)
  - Plain-text passthrough
  - Entity extraction (regex: emails, phones)

Design principles:
  - Every output is traceable to a specific original via SHA-256.
  - All derivatives are stored through EvidenceStore (hashed, manifested).
  - Processing tasks are tracked in DocumentProcessingTask with timestamps.
  - No mutation of originals. Ever.
  - Deterministic: same input → same output (no randomness, no LLM calls).
  - Errors are caught, logged, and stored — never swallowed.
"""

import json
import logging
import mimetypes
import os
import re
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class ExtractionResult:
    """Result of a text/metadata extraction operation."""

    success: bool
    evidence_id: int  # DB primary key
    task_type: str  # pdf_text, pdf_ocr, video_metadata, image_ocr, docx_text, plaintext
    full_text: Optional[str] = None
    page_count: Optional[int] = None
    word_count: int = 0
    character_count: int = 0
    metadata: Dict = field(default_factory=dict)
    error_message: Optional[str] = None
    processing_seconds: float = 0.0

    # Entity extraction results
    email_addresses: List[str] = field(default_factory=list)
    phone_numbers: List[str] = field(default_factory=list)


@dataclass
class VideoProcessingResult:
    """Result of video processing (metadata + derivatives)."""

    success: bool
    evidence_id: int
    metadata: Dict = field(default_factory=dict)  # ffprobe output
    thumbnail_path: Optional[str] = None  # path to generated thumbnail
    proxy_path: Optional[str] = None  # path to generated proxy video
    error_message: Optional[str] = None
    processing_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Entity extraction (deterministic regex)
# ---------------------------------------------------------------------------


# RFC 5322 simplified — intentionally conservative
_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
)

# North American phone patterns + international with country code
_PHONE_RE = re.compile(
    r"""
    (?:                                # optional country code
        \+?1[\s.\-]?                   #   +1 or 1
    )?
    (?:                                # area code
        \(?\d{3}\)?[\s.\-]?
    )
    \d{3}[\s.\-]?\d{4}                # subscriber number
    """,
    re.VERBOSE,
)


def extract_entities(text: str) -> Tuple[List[str], List[str]]:
    """
    Extract email addresses and phone numbers from text.

    Returns:
        (emails, phones) — deduplicated, sorted lists.
    """
    if not text:
        return [], []

    emails = sorted(set(_EMAIL_RE.findall(text)))
    phones = sorted(set(_PHONE_RE.findall(text)))
    # Clean phone matches (strip whitespace)
    phones = [p.strip() for p in phones if len(p.strip()) >= 7]
    return emails, phones


# ---------------------------------------------------------------------------
# PDF processing
# ---------------------------------------------------------------------------


def extract_pdf_text(file_path: str) -> ExtractionResult:
    """
    Extract text from a PDF file.

    Strategy:
      1. Try native text extraction via pdfplumber.
      2. For pages with no native text, fall back to OCR (pdfplumber → PIL → pytesseract).
      3. Combine all page text into a single document.

    Returns ExtractionResult with full_text populated on success.
    """
    start = time.time()

    try:
        import pdfplumber
    except ImportError:
        return ExtractionResult(
            success=False,
            evidence_id=0,
            task_type="pdf_text",
            error_message="pdfplumber not installed",
            processing_seconds=time.time() - start,
        )

    path = Path(file_path)
    if not path.exists():
        return ExtractionResult(
            success=False,
            evidence_id=0,
            task_type="pdf_text",
            error_message=f"File not found: {file_path}",
            processing_seconds=time.time() - start,
        )

    pages_text = []
    page_count = 0
    ocr_pages = 0

    try:
        with pdfplumber.open(str(path)) as pdf:
            page_count = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                # Try native text first
                native_text = (page.extract_text() or "").strip()

                if native_text:
                    pages_text.append(native_text)
                else:
                    # Fall back to OCR
                    ocr_text = _ocr_pdf_page(page, page_number=i + 1)
                    if ocr_text:
                        pages_text.append(ocr_text)
                        ocr_pages += 1
                    else:
                        pages_text.append("")  # Blank page

        full_text = "\n\n".join(pages_text)
        emails, phones = extract_entities(full_text)
        words = full_text.split()

        task_type = "pdf_ocr" if ocr_pages > 0 else "pdf_text"

        return ExtractionResult(
            success=True,
            evidence_id=0,  # Caller sets this
            task_type=task_type,
            full_text=full_text,
            page_count=page_count,
            word_count=len(words),
            character_count=len(full_text),
            metadata={
                "total_pages": page_count,
                "native_text_pages": page_count - ocr_pages,
                "ocr_pages": ocr_pages,
                "processing_engine": "pdfplumber + pytesseract",
            },
            email_addresses=emails,
            phone_numbers=phones,
            processing_seconds=time.time() - start,
        )

    except Exception as exc:
        logger.error("PDF extraction failed for %s: %s", file_path, exc, exc_info=True)
        return ExtractionResult(
            success=False,
            evidence_id=0,
            task_type="pdf_text",
            error_message=str(exc),
            processing_seconds=time.time() - start,
        )


def _ocr_pdf_page(page, page_number: int = 0) -> str:
    """
    OCR a single pdfplumber page by rendering to image then running pytesseract.

    Returns extracted text or empty string on failure.
    """
    try:
        import pytesseract
        from PIL import Image

        # Render page to image (pdfplumber uses pdfminer + PIL internally)
        img = page.to_image(resolution=300)
        pil_image = img.original  # PIL.Image object

        text = pytesseract.image_to_string(pil_image, lang="eng")
        return text.strip()

    except Exception as exc:
        logger.warning("OCR failed for page %d: %s", page_number, exc)
        return ""


# ---------------------------------------------------------------------------
# Video processing (ffprobe + ffmpeg)
# ---------------------------------------------------------------------------


def extract_video_metadata(file_path: str) -> Dict:
    """
    Extract video metadata using ffprobe.

    Returns dict with streams, format, duration, resolution, codec, etc.
    Returns empty dict with 'error' key on failure.
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            return {"error": f"ffprobe exit code {result.returncode}: {result.stderr}"}

        data = json.loads(result.stdout)

        # Extract key fields for structured storage
        video_stream = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )
        audio_stream = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "audio"),
            None,
        )
        fmt = data.get("format", {})

        summary = {
            "duration_seconds": float(fmt.get("duration", 0)),
            "file_size_bytes": int(fmt.get("size", 0)),
            "bitrate_bps": int(fmt.get("bit_rate", 0)),
            "format_name": fmt.get("format_name", ""),
            "format_long_name": fmt.get("format_long_name", ""),
            "stream_count": int(fmt.get("nb_streams", 0)),
        }

        if video_stream:
            summary["video"] = {
                "codec": video_stream.get("codec_name", ""),
                "codec_long": video_stream.get("codec_long_name", ""),
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "fps": _parse_fps(video_stream.get("r_frame_rate", "0/1")),
                "bitrate_bps": int(video_stream.get("bit_rate", 0)),
                "total_frames": int(video_stream.get("nb_frames", 0)),
                "pixel_format": video_stream.get("pix_fmt", ""),
            }

        if audio_stream:
            summary["audio"] = {
                "codec": audio_stream.get("codec_name", ""),
                "sample_rate": int(audio_stream.get("sample_rate", 0)),
                "channels": int(audio_stream.get("channels", 0)),
                "bitrate_bps": int(audio_stream.get("bit_rate", 0)),
            }

        summary["raw_ffprobe"] = data
        return summary

    except subprocess.TimeoutExpired:
        return {"error": "ffprobe timed out after 60 seconds"}
    except Exception as exc:
        return {"error": str(exc)}


def _parse_fps(rate_str: str) -> float:
    """Parse ffprobe frame rate string like '30000/1001' → 29.97."""
    try:
        if "/" in rate_str:
            num, den = rate_str.split("/")
            return round(float(num) / float(den), 2) if float(den) else 0.0
        return float(rate_str)
    except (ValueError, ZeroDivisionError):
        return 0.0


def generate_thumbnail(
    video_path: str, output_path: str, timestamp: float = 10.0
) -> bool:
    """
    Generate a JPEG thumbnail from a video at the given timestamp.

    Args:
        video_path: Path to source video.
        output_path: Path to write the JPEG thumbnail.
        timestamp: Time offset in seconds.

    Returns True on success.
    """
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(timestamp),
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", "2",
            str(output_path),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            logger.error("Thumbnail generation failed: %s", result.stderr)
            return False

        return Path(output_path).exists() and Path(output_path).stat().st_size > 0

    except subprocess.TimeoutExpired:
        logger.error("Thumbnail generation timed out for %s", video_path)
        return False
    except Exception as exc:
        logger.error("Thumbnail generation error: %s", exc)
        return False


def generate_proxy_video(
    video_path: str, output_path: str, target_height: int = 720
) -> bool:
    """
    Generate a lower-resolution proxy video for review.

    Args:
        video_path: Path to source video.
        output_path: Path to write the proxy MP4.
        target_height: Target vertical resolution (default 720p).

    Returns True on success.
    """
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-vf", f"scale=-2:{target_height}",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(output_path),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600  # 10 min for large files
        )
        if result.returncode != 0:
            logger.error("Proxy generation failed: %s", result.stderr)
            return False

        return Path(output_path).exists() and Path(output_path).stat().st_size > 0

    except subprocess.TimeoutExpired:
        logger.error("Proxy generation timed out for %s", video_path)
        return False
    except Exception as exc:
        logger.error("Proxy generation error: %s", exc)
        return False


def process_video_evidence(
    file_path: str,
    evidence_store,
    original_sha256: str,
    generate_proxy: bool = False,
) -> VideoProcessingResult:
    """
    Full video processing pipeline:
      1. Extract metadata via ffprobe.
      2. Generate thumbnail at t=10s.
      3. Optionally generate 720p proxy.
      4. Store derivatives in evidence store.

    Returns VideoProcessingResult.
    """
    start = time.time()

    # 1. Metadata
    metadata = extract_video_metadata(file_path)
    if "error" in metadata and not metadata.get("duration_seconds"):
        return VideoProcessingResult(
            success=False,
            evidence_id=0,
            error_message=metadata["error"],
            processing_seconds=time.time() - start,
        )

    result = VideoProcessingResult(
        success=True,
        evidence_id=0,
        metadata=metadata,
    )

    # 2. Thumbnail
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        thumb_tmp = tmp.name

    try:
        # Pick timestamp: 10s or half of duration if shorter
        duration = metadata.get("duration_seconds", 0)
        ts = min(10.0, duration / 2) if duration > 0 else 0.0

        if generate_thumbnail(file_path, thumb_tmp, timestamp=ts):
            record = evidence_store.store_derivative(
                original_sha256=original_sha256,
                derivative_type="thumbnail",
                source_path=thumb_tmp,
                filename="thumbnail.jpg",
            )
            result.thumbnail_path = evidence_store.get_derivative_path(
                original_sha256, "thumbnail", "thumbnail.jpg"
            )
            result.metadata["thumbnail_sha256"] = record.sha256
    finally:
        if os.path.exists(thumb_tmp):
            os.unlink(thumb_tmp)

    # 3. Proxy (optional, skip for now by default)
    if generate_proxy:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            proxy_tmp = tmp.name

        try:
            if generate_proxy_video(file_path, proxy_tmp):
                record = evidence_store.store_derivative(
                    original_sha256=original_sha256,
                    derivative_type="proxy",
                    source_path=proxy_tmp,
                    filename="proxy_720p.mp4",
                )
                result.proxy_path = evidence_store.get_derivative_path(
                    original_sha256, "proxy", "proxy_720p.mp4"
                )
                result.metadata["proxy_sha256"] = record.sha256
        finally:
            if os.path.exists(proxy_tmp):
                os.unlink(proxy_tmp)

    result.processing_seconds = time.time() - start
    return result


# ---------------------------------------------------------------------------
# Image OCR
# ---------------------------------------------------------------------------


def extract_image_text(file_path: str) -> ExtractionResult:
    """
    OCR an image file (JPEG, PNG, TIFF, BMP) using pytesseract.

    Returns ExtractionResult with full_text populated on success.
    """
    start = time.time()

    try:
        import pytesseract
        from PIL import Image

        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang="eng").strip()

        emails, phones = extract_entities(text)
        words = text.split()

        return ExtractionResult(
            success=bool(text),
            evidence_id=0,
            task_type="image_ocr",
            full_text=text if text else None,
            page_count=1,
            word_count=len(words),
            character_count=len(text),
            metadata={
                "image_size": f"{img.width}x{img.height}",
                "image_mode": img.mode,
                "processing_engine": "pytesseract",
            },
            email_addresses=emails,
            phone_numbers=phones,
            processing_seconds=time.time() - start,
        )

    except Exception as exc:
        logger.error("Image OCR failed for %s: %s", file_path, exc, exc_info=True)
        return ExtractionResult(
            success=False,
            evidence_id=0,
            task_type="image_ocr",
            error_message=str(exc),
            processing_seconds=time.time() - start,
        )


# ---------------------------------------------------------------------------
# DOCX extraction
# ---------------------------------------------------------------------------


def extract_docx_text(file_path: str) -> ExtractionResult:
    """
    Extract text from a DOCX file using python-docx.

    Returns ExtractionResult with full_text populated on success.
    """
    start = time.time()

    try:
        import docx

        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)

        emails, phones = extract_entities(full_text)
        words = full_text.split()

        return ExtractionResult(
            success=bool(full_text),
            evidence_id=0,
            task_type="docx_text",
            full_text=full_text if full_text else None,
            page_count=None,  # DOCX doesn't have reliable page count without rendering
            word_count=len(words),
            character_count=len(full_text),
            metadata={
                "paragraph_count": len(paragraphs),
                "processing_engine": "python-docx",
            },
            email_addresses=emails,
            phone_numbers=phones,
            processing_seconds=time.time() - start,
        )

    except Exception as exc:
        logger.error("DOCX extraction failed for %s: %s", file_path, exc, exc_info=True)
        return ExtractionResult(
            success=False,
            evidence_id=0,
            task_type="docx_text",
            error_message=str(exc),
            processing_seconds=time.time() - start,
        )


# ---------------------------------------------------------------------------
# Plain-text passthrough
# ---------------------------------------------------------------------------


def extract_plaintext(file_path: str) -> ExtractionResult:
    """
    Read a plain-text file and return its content.

    Attempts UTF-8, falls back to latin-1.
    """
    start = time.time()

    try:
        path = Path(file_path)
        if not path.exists():
            return ExtractionResult(
                success=False,
                evidence_id=0,
                task_type="plaintext",
                error_message=f"File not found: {file_path}",
                processing_seconds=time.time() - start,
            )

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")

        emails, phones = extract_entities(text)
        words = text.split()

        return ExtractionResult(
            success=bool(text),
            evidence_id=0,
            task_type="plaintext",
            full_text=text,
            page_count=1,
            word_count=len(words),
            character_count=len(text),
            metadata={"encoding": "utf-8", "processing_engine": "passthrough"},
            email_addresses=emails,
            phone_numbers=phones,
            processing_seconds=time.time() - start,
        )

    except Exception as exc:
        logger.error("Plaintext read failed for %s: %s", file_path, exc, exc_info=True)
        return ExtractionResult(
            success=False,
            evidence_id=0,
            task_type="plaintext",
            error_message=str(exc),
            processing_seconds=time.time() - start,
        )


# ---------------------------------------------------------------------------
# MIME type detection
# ---------------------------------------------------------------------------

# Canonical mapping from MIME type to processing function
MIME_HANDLERS = {
    "application/pdf": "pdf",
    "video/mp4": "video",
    "video/x-msvideo": "video",
    "video/quicktime": "video",
    "video/x-matroska": "video",
    "video/webm": "video",
    "audio/mpeg": "audio",
    "audio/wav": "audio",
    "audio/x-wav": "audio",
    "audio/flac": "audio",
    "audio/aac": "audio",
    "audio/mp4": "audio",
    "image/jpeg": "image",
    "image/png": "image",
    "image/tiff": "image",
    "image/bmp": "image",
    "image/webp": "image",
    "image/gif": "image",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "plaintext",
    "text/csv": "plaintext",
    "text/html": "plaintext",
}


def detect_file_type(file_path: str, original_filename: str = "") -> str:
    """
    Detect file processing type from MIME type and extension.

    Returns one of: 'pdf', 'video', 'audio', 'image', 'docx', 'plaintext', 'unsupported'.
    """
    # Try MIME from filename first
    name = original_filename or file_path
    mime, _ = mimetypes.guess_type(name)

    if mime and mime in MIME_HANDLERS:
        return MIME_HANDLERS[mime]

    # Fallback: extension-based
    ext = Path(name).suffix.lower()
    ext_map = {
        ".pdf": "pdf",
        ".mp4": "video", ".avi": "video", ".mov": "video", ".mkv": "video", ".webm": "video",
        ".mp3": "audio", ".wav": "audio", ".flac": "audio", ".aac": "audio", ".m4a": "audio",
        ".jpg": "image", ".jpeg": "image", ".png": "image", ".tiff": "image",
        ".bmp": "image", ".webp": "image", ".gif": "image",
        ".docx": "docx",
        ".txt": "plaintext", ".csv": "plaintext", ".log": "plaintext",
    }
    return ext_map.get(ext, "unsupported")


# ---------------------------------------------------------------------------
# Unified processing dispatcher
# ---------------------------------------------------------------------------


def process_evidence_file(
    file_path: str,
    original_filename: str = "",
    evidence_store=None,
    original_sha256: str = "",
    generate_video_proxy: bool = False,
) -> ExtractionResult:
    """
    Process a single evidence file: detect type, extract text/metadata, extract entities.

    For video files, use process_video_evidence() directly — this function
    handles text-bearing file types.

    Args:
        file_path: Absolute path to the file on disk.
        original_filename: Original filename (for MIME detection).
        evidence_store: EvidenceStore instance (for derivative storage).
        original_sha256: SHA-256 of the original file (for derivative linking).
        generate_video_proxy: Whether to generate proxy video.

    Returns:
        ExtractionResult on success or failure.
    """
    file_type = detect_file_type(file_path, original_filename)

    if file_type == "pdf":
        return extract_pdf_text(file_path)

    elif file_type == "image":
        return extract_image_text(file_path)

    elif file_type == "docx":
        return extract_docx_text(file_path)

    elif file_type == "plaintext":
        return extract_plaintext(file_path)

    elif file_type == "video":
        # Video returns a different result type — wrap it
        if evidence_store and original_sha256:
            vr = process_video_evidence(
                file_path, evidence_store, original_sha256,
                generate_proxy=generate_video_proxy,
            )
            return ExtractionResult(
                success=vr.success,
                evidence_id=0,
                task_type="video_metadata",
                metadata=vr.metadata,
                error_message=vr.error_message,
                processing_seconds=vr.processing_seconds,
            )
        else:
            # Metadata only (no derivative storage)
            meta = extract_video_metadata(file_path)
            return ExtractionResult(
                success="error" not in meta or bool(meta.get("duration_seconds")),
                evidence_id=0,
                task_type="video_metadata",
                metadata=meta,
                error_message=meta.get("error"),
            )

    elif file_type == "audio":
        # Audio metadata via ffprobe (no text extraction yet)
        meta = extract_video_metadata(file_path)  # ffprobe handles audio too
        return ExtractionResult(
            success="error" not in meta or bool(meta.get("duration_seconds")),
            evidence_id=0,
            task_type="audio_metadata",
            metadata=meta,
            error_message=meta.get("error"),
        )

    else:
        return ExtractionResult(
            success=False,
            evidence_id=0,
            task_type="unsupported",
            error_message=f"Unsupported file type: {file_type} ({original_filename or file_path})",
        )
