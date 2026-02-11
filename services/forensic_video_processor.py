"""
Forensic Video Processor
========================
Extracts metadata, generates thumbnails and low-resolution proxies
from video evidence files using ffmpeg-python.

Design principles:
  - Originals are NEVER modified.
  - All outputs are derivatives stored in the evidence store.
  - Every operation is deterministic and auditable.
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
from typing import Any, Dict, List, Optional, Tuple

import ffmpeg

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class VideoStreamInfo:
    """Metadata for a single video stream."""

    index: int
    codec: str
    width: int
    height: int
    fps: float
    duration_seconds: float
    bit_rate: int
    pix_fmt: str = ""
    profile: str = ""


@dataclass
class AudioStreamInfo:
    """Metadata for a single audio stream."""

    index: int
    codec: str
    sample_rate: int
    channels: int
    channel_layout: str
    bit_rate: int
    duration_seconds: float


@dataclass
class VideoMetadataResult:
    """Complete metadata extraction result for a video file."""

    file_path: str
    format_name: str
    format_long_name: str
    duration_seconds: float
    size_bytes: int
    bit_rate: int
    video_streams: List[VideoStreamInfo] = field(default_factory=list)
    audio_streams: List[AudioStreamInfo] = field(default_factory=list)
    container_metadata: Dict[str, Any] = field(default_factory=dict)
    creation_time: Optional[str] = None
    error: Optional[str] = None

    @property
    def primary_video(self) -> Optional[VideoStreamInfo]:
        return self.video_streams[0] if self.video_streams else None

    @property
    def primary_audio(self) -> Optional[AudioStreamInfo]:
        return self.audio_streams[0] if self.audio_streams else None

    @property
    def resolution(self) -> str:
        v = self.primary_video
        return f"{v.width}x{v.height}" if v else "unknown"

    @property
    def codec_summary(self) -> str:
        parts = []
        v = self.primary_video
        a = self.primary_audio
        if v:
            parts.append(f"video:{v.codec}")
        if a:
            parts.append(f"audio:{a.codec}")
        return ", ".join(parts) if parts else "unknown"

    def to_dict(self) -> Dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Core processor
# ---------------------------------------------------------------------------


class ForensicVideoProcessor:
    """
    Extracts metadata, generates thumbnails and proxies from video files.
    Uses ffmpeg-python (wrapper) and the system ffmpeg binary.
    """

    # Proxy generation settings (low-res review copy)
    PROXY_WIDTH = 640
    PROXY_HEIGHT = 360
    PROXY_BITRATE = "500k"
    PROXY_CODEC = "libx264"
    PROXY_PRESET = "fast"
    PROXY_CRF = 28

    # Thumbnail settings
    THUMB_WIDTH = 320
    THUMB_HEIGHT = 180

    def __init__(self) -> None:
        self._verify_ffmpeg()

    @staticmethod
    def _verify_ffmpeg() -> None:
        """Verify ffmpeg binary is available on PATH."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise RuntimeError("ffmpeg returned non-zero exit code")
            version_line = result.stdout.split("\n")[0]
            logger.info("ffmpeg available: %s", version_line)
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg binary not found on PATH. "
                "Install FFmpeg: https://ffmpeg.org/download.html"
            )

    # -- metadata extraction -------------------------------------------------

    def extract_metadata(self, file_path: str) -> VideoMetadataResult:
        """
        Extract comprehensive metadata from a video file using ffprobe.

        This is non-destructive — no data is written.
        """
        try:
            probe = ffmpeg.probe(file_path)
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
            logger.error("ffprobe failed for %s: %s", file_path, error_msg)
            return VideoMetadataResult(
                file_path=file_path,
                format_name="",
                format_long_name="",
                duration_seconds=0.0,
                size_bytes=0,
                bit_rate=0,
                error=error_msg,
            )

        fmt = probe.get("format", {})
        streams = probe.get("streams", [])

        # Parse video streams
        video_streams = []
        for s in streams:
            if s.get("codec_type") == "video":
                fps_str = s.get("r_frame_rate", "0/1")
                try:
                    num, den = fps_str.split("/")
                    fps = float(num) / float(den) if float(den) else 0.0
                except (ValueError, ZeroDivisionError):
                    fps = 0.0

                video_streams.append(
                    VideoStreamInfo(
                        index=s.get("index", 0),
                        codec=s.get("codec_name", "unknown"),
                        width=s.get("width", 0),
                        height=s.get("height", 0),
                        fps=round(fps, 3),
                        duration_seconds=float(s.get("duration", fmt.get("duration", 0))),
                        bit_rate=int(s.get("bit_rate", 0)),
                        pix_fmt=s.get("pix_fmt", ""),
                        profile=s.get("profile", ""),
                    )
                )

        # Parse audio streams
        audio_streams = []
        for s in streams:
            if s.get("codec_type") == "audio":
                audio_streams.append(
                    AudioStreamInfo(
                        index=s.get("index", 0),
                        codec=s.get("codec_name", "unknown"),
                        sample_rate=int(s.get("sample_rate", 0)),
                        channels=s.get("channels", 0),
                        channel_layout=s.get("channel_layout", "unknown"),
                        bit_rate=int(s.get("bit_rate", 0)),
                        duration_seconds=float(
                            s.get("duration", fmt.get("duration", 0))
                        ),
                    )
                )

        # Container-level metadata tags
        tags = fmt.get("tags", {})
        creation_time = tags.get("creation_time")

        return VideoMetadataResult(
            file_path=file_path,
            format_name=fmt.get("format_name", ""),
            format_long_name=fmt.get("format_long_name", ""),
            duration_seconds=float(fmt.get("duration", 0)),
            size_bytes=int(fmt.get("size", 0)),
            bit_rate=int(fmt.get("bit_rate", 0)),
            video_streams=video_streams,
            audio_streams=audio_streams,
            container_metadata=tags,
            creation_time=creation_time,
        )

    # -- thumbnail generation ------------------------------------------------

    def generate_thumbnail(
        self,
        file_path: str,
        output_path: str,
        timestamp_seconds: float = 1.0,
    ) -> bool:
        """
        Extract a single frame as a JPEG thumbnail.

        Args:
            file_path: Source video path.
            output_path: Destination JPEG path.
            timestamp_seconds: Offset into the video for the frame.

        Returns:
            True on success, False on failure.
        """
        try:
            (
                ffmpeg.input(file_path, ss=timestamp_seconds)
                .filter("scale", self.THUMB_WIDTH, self.THUMB_HEIGHT)
                .output(output_path, vframes=1, format="image2", **{"q:v": 2})
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info("Thumbnail generated: %s", output_path)
                return True
            return False
        except ffmpeg.Error as e:
            stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
            logger.error("Thumbnail generation failed: %s", stderr)
            return False

    def generate_thumbnails(
        self,
        file_path: str,
        output_dir: str,
        base_name: str = "thumb",
    ) -> List[str]:
        """
        Generate first-frame and mid-stream thumbnails.

        Returns list of generated file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []

        # First frame (1 second in to avoid black frames)
        first_path = os.path.join(output_dir, f"{base_name}_first.jpg")
        if self.generate_thumbnail(file_path, first_path, timestamp_seconds=1.0):
            results.append(first_path)

        # Mid-stream frame
        meta = self.extract_metadata(file_path)
        if meta.duration_seconds > 2.0:
            mid_ts = meta.duration_seconds / 2.0
            mid_path = os.path.join(output_dir, f"{base_name}_mid.jpg")
            if self.generate_thumbnail(file_path, mid_path, timestamp_seconds=mid_ts):
                results.append(mid_path)

        return results

    # -- proxy generation ----------------------------------------------------

    def generate_proxy(
        self,
        file_path: str,
        output_path: str,
    ) -> bool:
        """
        Generate a low-resolution review proxy.

        The proxy is a re-encoded copy at reduced resolution and bitrate.
        The original is NEVER modified.

        Returns True on success, False on failure.
        """
        try:
            (
                ffmpeg.input(file_path)
                .filter(
                    "scale",
                    self.PROXY_WIDTH,
                    self.PROXY_HEIGHT,
                    force_original_aspect_ratio="decrease",
                )
                .output(
                    output_path,
                    vcodec=self.PROXY_CODEC,
                    acodec="aac",
                    audio_bitrate="128k",
                    preset=self.PROXY_PRESET,
                    crf=self.PROXY_CRF,
                    movflags="+faststart",
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(
                    "Proxy generated: %s (%d bytes)",
                    output_path,
                    os.path.getsize(output_path),
                )
                return True
            return False
        except ffmpeg.Error as e:
            stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
            logger.error("Proxy generation failed: %s", stderr)
            return False

    # -- combined processing entrypoint --------------------------------------

    def process_video(
        self,
        file_path: str,
        output_dir: str,
        generate_proxy: bool = True,
    ) -> Dict:
        """
        Full processing pipeline for a video file:
          1. Extract metadata (non-destructive).
          2. Generate thumbnails (first frame + mid-stream).
          3. Optionally generate low-res proxy.

        Returns a dict with all results and derivative file paths.
        """
        result = {
            "metadata": None,
            "thumbnails": [],
            "proxy": None,
            "errors": [],
        }

        os.makedirs(output_dir, exist_ok=True)
        base = Path(file_path).stem

        # 1. Metadata
        meta = self.extract_metadata(file_path)
        if meta.error:
            result["errors"].append(f"metadata: {meta.error}")
        result["metadata"] = meta.to_dict()

        # 2. Thumbnails
        thumb_dir = os.path.join(output_dir, "thumbnails")
        thumbs = self.generate_thumbnails(file_path, thumb_dir, base_name=base)
        result["thumbnails"] = thumbs

        # 3. Proxy
        if generate_proxy:
            proxy_path = os.path.join(output_dir, f"{base}_proxy.mp4")
            if self.generate_proxy(file_path, proxy_path):
                result["proxy"] = proxy_path
            else:
                result["errors"].append("proxy generation failed")

        return result
