"""
Transcription Service
=====================
Extracts audio from video/audio evidence files and generates
timestamped transcriptions using faster-whisper (CTranslate2).

Design principles:
  - Originals are NEVER modified.
  - Audio is extracted to a temporary WAV file, transcribed, then deleted.
  - Transcription output is deterministic for a given model/input pair.
  - Every operation is logged and auditable.
  - Failures are explicit, never silent.
"""

import json
import logging
import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class TranscriptSegment:
    """A single timestamped segment from the transcription."""

    start: float          # Start time in seconds
    end: float            # End time in seconds
    text: str             # Transcribed text for this segment
    confidence: float     # Average log-probability (higher = more confident)
    words: List[Dict[str, Any]] = field(default_factory=list)  # Word-level detail


@dataclass
class TranscriptionResult:
    """Complete transcription result for an evidence file."""

    file_path: str
    model_name: str
    language: str
    language_probability: float
    duration_seconds: float
    segments: List[TranscriptSegment] = field(default_factory=list)
    full_text: str = ""
    word_count: int = 0
    processing_time_seconds: float = 0.0
    error: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a JSON-safe dictionary."""
        return {
            "file_path": self.file_path,
            "model_name": self.model_name,
            "language": self.language,
            "language_probability": round(self.language_probability, 4),
            "duration_seconds": round(self.duration_seconds, 2),
            "full_text": self.full_text,
            "word_count": self.word_count,
            "processing_time_seconds": round(self.processing_time_seconds, 2),
            "timestamp": self.timestamp,
            "error": self.error,
            "segments": [
                {
                    "start": round(s.start, 3),
                    "end": round(s.end, 3),
                    "text": s.text,
                    "confidence": round(s.confidence, 4),
                }
                for s in self.segments
            ],
        }


# ---------------------------------------------------------------------------
# Audio extraction (ffmpeg)
# ---------------------------------------------------------------------------


def _has_audio_stream(file_path: str) -> bool:
    """
    Check whether a file contains at least one audio stream.

    Uses ffprobe to inspect stream types without modifying the file.
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-select_streams", "a",
            "-show_entries", "stream=codec_type",
            "-of", "csv=p=0",
            file_path,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def extract_audio_to_wav(
    source_path: str,
    output_path: str,
    sample_rate: int = 16000,
    channels: int = 1,
) -> bool:
    """
    Extract audio from a video/audio file to 16 kHz mono WAV.

    faster-whisper expects 16 kHz mono input for optimal results.
    The source file is never modified.

    Args:
        source_path: Path to the source video/audio file.
        output_path: Destination WAV path.
        sample_rate: Target sample rate (default 16000 for Whisper).
        channels: Number of audio channels (default 1 = mono).

    Returns:
        True on success, False on failure.
    """
    try:
        cmd = [
            "ffmpeg",
            "-i", source_path,
            "-vn",                          # Discard video
            "-acodec", "pcm_s16le",         # 16-bit PCM
            "-ar", str(sample_rate),         # Resample to 16 kHz
            "-ac", str(channels),            # Mono
            "-y",                            # Overwrite output
            output_path,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5-minute timeout for long files
        )
        if result.returncode != 0:
            logger.error(
                "Audio extraction failed (exit %d): %s",
                result.returncode,
                result.stderr[:500],
            )
            return False

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(
                "Audio extracted: %s (%.1f MB, %d Hz, %d ch)",
                output_path,
                size_mb,
                sample_rate,
                channels,
            )
            return True

        logger.error("Audio extraction produced empty file: %s", output_path)
        return False

    except subprocess.TimeoutExpired:
        logger.error("Audio extraction timed out for: %s", source_path)
        return False
    except Exception as exc:
        logger.error("Audio extraction error: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Transcription engine (faster-whisper)
# ---------------------------------------------------------------------------


# Lazy-loaded singleton to avoid loading the model until first use.
_whisper_model = None
_whisper_model_name = None


def _get_whisper_model(model_size: str = "base"):
    """
    Get or create the faster-whisper model (singleton).

    Model sizes: tiny, base, small, medium, large-v2, large-v3
    Recommended for CPU:
      - 'base'  — fast, ~150 MB, good accuracy for clear speech
      - 'small' — slower, ~500 MB, better accuracy

    On first run, downloads from HuggingFace Hub (~150 MB for base).
    Subsequent runs use the local cache.
    """
    global _whisper_model, _whisper_model_name

    if _whisper_model is not None and _whisper_model_name == model_size:
        return _whisper_model

    try:
        from faster_whisper import WhisperModel

        logger.info("Loading faster-whisper model '%s' (CPU)...", model_size)

        # Try local cache first (avoids network calls after first download)
        try:
            import huggingface_hub
            repo_id = f"Systran/faster-whisper-{model_size}"
            local_path = huggingface_hub.snapshot_download(
                repo_id, local_files_only=True
            )
            logger.info("Using cached model from: %s", local_path)
            _whisper_model = WhisperModel(
                local_path,
                device="cpu",
                compute_type="int8",
                local_files_only=True,
            )
        except Exception:
            # Cache miss — download from HuggingFace Hub
            logger.info("Model not cached, downloading '%s'...", model_size)
            _whisper_model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8",
            )

        _whisper_model_name = model_size
        logger.info("faster-whisper model '%s' loaded successfully.", model_size)
        return _whisper_model

    except Exception as exc:
        logger.error("Failed to load faster-whisper model: %s", exc)
        raise RuntimeError(f"Transcription model load failed: {exc}") from exc


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
) -> TranscriptionResult:
    """
    Transcribe an audio file using faster-whisper.

    Args:
        audio_path: Path to the audio file (WAV recommended).
        model_size: Whisper model size ('base', 'small', etc.).
        language: ISO 639-1 language code, or None for auto-detect.

    Returns:
        TranscriptionResult with timestamped segments and full text.
    """
    import time

    start_time = time.monotonic()

    model = _get_whisper_model(model_size)

    try:
        segments_iter, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,         # Voice-activity detection to skip silence
            vad_parameters=dict(
                min_silence_duration_ms=500,
            ),
            word_timestamps=False,   # Segment-level timestamps are sufficient
        )

        segments: List[TranscriptSegment] = []
        full_text_parts: List[str] = []

        for seg in segments_iter:
            text = seg.text.strip()
            if not text:
                continue
            segments.append(
                TranscriptSegment(
                    start=seg.start,
                    end=seg.end,
                    text=text,
                    confidence=seg.avg_logprob,
                )
            )
            full_text_parts.append(text)

        full_text = " ".join(full_text_parts)
        elapsed = time.monotonic() - start_time

        result = TranscriptionResult(
            file_path=audio_path,
            model_name=model_size,
            language=info.language,
            language_probability=info.language_probability,
            duration_seconds=info.duration,
            segments=segments,
            full_text=full_text,
            word_count=len(full_text.split()) if full_text else 0,
            processing_time_seconds=elapsed,
        )

        logger.info(
            "Transcription complete: %d segments, %d words, %.1fs processing "
            "(%.1fx real-time) — lang=%s (%.0f%%)",
            len(segments),
            result.word_count,
            elapsed,
            info.duration / elapsed if elapsed > 0 else 0,
            info.language,
            info.language_probability * 100,
        )

        return result

    except Exception as exc:
        elapsed = time.monotonic() - start_time
        logger.error("Transcription failed: %s", exc)
        return TranscriptionResult(
            file_path=audio_path,
            model_name=model_size,
            language="unknown",
            language_probability=0.0,
            duration_seconds=0.0,
            processing_time_seconds=elapsed,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# High-level: transcribe an evidence file (video or audio)
# ---------------------------------------------------------------------------


def transcribe_evidence_file(
    file_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
) -> TranscriptionResult:
    """
    End-to-end transcription of a video or audio evidence file.

    1. If the file is video, extract audio to a temp WAV.
    2. Run faster-whisper transcription.
    3. Return structured result.

    The original file is never modified.

    Args:
        file_path: Path to the evidence file (video or audio).
        model_size: Whisper model size.
        language: Language hint (None = auto-detect).

    Returns:
        TranscriptionResult with full text and timestamped segments.
    """
    if not os.path.exists(file_path):
        return TranscriptionResult(
            file_path=file_path,
            model_name=model_size,
            language="unknown",
            language_probability=0.0,
            duration_seconds=0.0,
            error=f"File not found: {file_path}",
        )

    ext = Path(file_path).suffix.lower()
    audio_extensions = {".wav", ".mp3", ".flac", ".aac", ".m4a", ".wma", ".ogg"}
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"}

    if ext in audio_extensions:
        # Direct transcription of audio files
        logger.info("Transcribing audio file directly: %s", file_path)
        return transcribe_audio(file_path, model_size=model_size, language=language)

    if ext in video_extensions:
        # Check for audio stream before attempting extraction
        if not _has_audio_stream(file_path):
            logger.info("Video has no audio stream, skipping transcription: %s", file_path)
            return TranscriptionResult(
                file_path=file_path,
                model_name=model_size,
                language="unknown",
                language_probability=0.0,
                duration_seconds=0.0,
                full_text="",
                word_count=0,
                # Not an error — file simply has no audio
            )

        # Extract audio first, then transcribe
        logger.info("Extracting audio from video: %s", file_path)
        with tempfile.TemporaryDirectory(prefix="evident_audio_") as tmp_dir:
            wav_path = os.path.join(tmp_dir, "audio.wav")
            if not extract_audio_to_wav(file_path, wav_path):
                return TranscriptionResult(
                    file_path=file_path,
                    model_name=model_size,
                    language="unknown",
                    language_probability=0.0,
                    duration_seconds=0.0,
                    error="Audio extraction failed",
                )
            result = transcribe_audio(wav_path, model_size=model_size, language=language)
            # Override file_path to reference the original evidence, not the temp WAV
            result.file_path = file_path
            return result

    return TranscriptionResult(
        file_path=file_path,
        model_name=model_size,
        language="unknown",
        language_probability=0.0,
        duration_seconds=0.0,
        error=f"Unsupported file type for transcription: {ext}",
    )
