"""
Evident Media Processing Pipeline
Intelligent batch processing for MP4, PDF, JPEG and more formats
"""

import os
import uuid
import hashlib
import json
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, BinaryIO, Tuple
from dataclasses import dataclass, asdict
import logging

# Media processing libraries
import mimetypes
from PIL import Image
import PyPDF2

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """Supported media types"""
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    IMAGE = "image"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class ProcessingStatus(Enum):
    """Processing status states"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProcessingResult:
    """Result of media processing"""
    file_id: str
    filename: str
    media_type: MediaType
    status: ProcessingStatus
    file_size: int
    duration: Optional[float] = None  # For video/audio
    page_count: Optional[int] = None  # For PDF
    image_dimensions: Optional[Tuple[int, int]] = None  # For images
    extracted_text: Optional[str] = None
    metadata: Dict = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        """Convert to dictionary"""
        result = asdict(self)
        result['media_type'] = self.media_type.value
        result['status'] = self.status.value
        return result


class MediaValidator:
    """Validate media files"""

    # Supported extensions
    SUPPORTED_VIDEO = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    SUPPORTED_AUDIO = {'.mp3', '.wav', '.flac', '.aac', '.wma', '.m4a'}
    SUPPORTED_IMAGE = {'.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    SUPPORTED_PDF = {'.pdf'}
    SUPPORTED_DOCUMENT = {'.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt', '.rtf'}

    # File size limits (in MB)
    SIZE_LIMITS = {
        MediaType.VIDEO: 2500,     # 2.5 GB for BWC video evidence
        MediaType.AUDIO: 500,      # 500 MB for audio evidence
        MediaType.PDF: 50,         # 50 MB for PDF
        MediaType.IMAGE: 10,       # 10 MB for image
        MediaType.DOCUMENT: 25,    # 25 MB for document
    }

    @staticmethod
    def get_media_type(filename: str) -> MediaType:
        """Determine media type from filename"""
        ext = Path(filename).suffix.lower()

        if ext in MediaValidator.SUPPORTED_VIDEO:
            return MediaType.VIDEO
        elif ext in MediaValidator.SUPPORTED_AUDIO:
            return MediaType.AUDIO
        elif ext in MediaValidator.SUPPORTED_IMAGE:
            return MediaType.IMAGE
        elif ext in MediaValidator.SUPPORTED_PDF:
            return MediaType.PDF
        elif ext in MediaValidator.SUPPORTED_DOCUMENT:
            return MediaType.DOCUMENT
        else:
            return MediaType.UNKNOWN

    @staticmethod
    def validate_file(
        filename: str,
        file_size: int,
        media_type: Optional[MediaType] = None
    ) -> Tuple[bool, str]:
        """
        Validate a file
        Returns: (is_valid, error_message)
        """
        if media_type is None:
            media_type = MediaValidator.get_media_type(filename)

        # Check if format is supported
        if media_type == MediaType.UNKNOWN:
            return False, f"Unsupported file format: {Path(filename).suffix}"

        # Check file size
        size_limit_mb = MediaValidator.SIZE_LIMITS.get(media_type, 10)
        size_mb = file_size / (1024 * 1024)

        if size_mb > size_limit_mb:
            return False, f"File too large: {size_mb:.1f}MB (limit: {size_limit_mb}MB)"

        return True, ""


class MediaProcessor:
    """Process media files"""

    def __init__(self, upload_dir: str = "uploads", cache_dir: str = ".cache"):
        """Initialize media processor"""
        self.upload_dir = Path(upload_dir)
        self.cache_dir = Path(cache_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def process_file(self, file_path: str) -> ProcessingResult:
        """Process a media file"""
        import time
        start_time = time.time()

        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return ProcessingResult(
                    file_id=str(uuid.uuid4()),
                    filename=file_path.name,
                    media_type=MediaType.UNKNOWN,
                    status=ProcessingStatus.FAILED,
                    file_size=0,
                    error_message=f"File not found: {file_path}",
                    processing_time=time.time() - start_time,
                )

            # Get basic file info
            file_size = file_path.stat().st_size
            media_type = MediaValidator.get_media_type(str(file_path))

            # Validate file
            is_valid, error_msg = MediaValidator.validate_file(
                file_path.name,
                file_size,
                media_type
            )

            if not is_valid:
                return ProcessingResult(
                    file_id=str(uuid.uuid4()),
                    filename=file_path.name,
                    media_type=media_type,
                    status=ProcessingStatus.FAILED,
                    file_size=file_size,
                    error_message=error_msg,
                    processing_time=time.time() - start_time,
                )

            # Process based on media type
            if media_type == MediaType.IMAGE:
                result = self._process_image(file_path)
            elif media_type == MediaType.PDF:
                result = self._process_pdf(file_path)
            elif media_type == MediaType.VIDEO:
                result = self._process_video(file_path)
            elif media_type == MediaType.AUDIO:
                result = self._process_audio(file_path)
            elif media_type == MediaType.DOCUMENT:
                result = self._process_document(file_path)
            else:
                result = ProcessingResult(
                    file_id=str(uuid.uuid4()),
                    filename=file_path.name,
                    media_type=media_type,
                    status=ProcessingStatus.SKIPPED,
                    file_size=file_size,
                )

            result.file_size = file_size
            result.processing_time = time.time() - start_time
            return result

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=Path(file_path).name if file_path else "unknown",
                media_type=MediaType.UNKNOWN,
                status=ProcessingStatus.FAILED,
                file_size=0,
                error_message=str(e),
                processing_time=time.time() - start_time,
            )

    def _process_image(self, file_path: Path) -> ProcessingResult:
        """Process image file"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format

                return ProcessingResult(
                    file_id=str(uuid.uuid4()),
                    filename=file_path.name,
                    media_type=MediaType.IMAGE,
                    status=ProcessingStatus.COMPLETED,
                    file_size=0,  # Will be set by caller
                    image_dimensions=(width, height),
                    metadata={
                        'format': format_name,
                        'mode': img.mode,
                        'size': f"{width}x{height}",
                    }
                )
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.IMAGE,
                status=ProcessingStatus.FAILED,
                file_size=0,
                error_message=str(e),
            )

    def _process_pdf(self, file_path: Path) -> ProcessingResult:
        """Process PDF file"""
        try:
            with open(file_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                page_count = len(reader.pages)

                # Extract text from first page
                first_page_text = ""
                if page_count > 0:
                    first_page = reader.pages[0]
                    first_page_text = first_page.extract_text()[:500]

                return ProcessingResult(
                    file_id=str(uuid.uuid4()),
                    filename=file_path.name,
                    media_type=MediaType.PDF,
                    status=ProcessingStatus.COMPLETED,
                    file_size=0,  # Will be set by caller
                    page_count=page_count,
                    extracted_text=first_page_text,
                    metadata={
                        'pages': page_count,
                        'title': reader.metadata.title if reader.metadata else None,
                        'author': reader.metadata.author if reader.metadata else None,
                    }
                )
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.PDF,
                status=ProcessingStatus.FAILED,
                file_size=0,
                error_message=str(e),
            )

    def _process_video(self, file_path: Path) -> ProcessingResult:
        """Process video file (metadata only for now)"""
        try:
            # Would use ffmpeg/moviepy here in production
            # For now, just create a result with basic metadata
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.VIDEO,
                status=ProcessingStatus.COMPLETED,
                file_size=0,  # Will be set by caller
                metadata={
                    'format': 'video',
                    'extension': file_path.suffix.lower(),
                }
            )
        except Exception as e:
            logger.error(f"Error processing video {file_path}: {e}")
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.VIDEO,
                status=ProcessingStatus.FAILED,
                file_size=0,
                error_message=str(e),
            )

    def _process_audio(self, file_path: Path) -> ProcessingResult:
        """Process audio file (metadata only for now)"""
        try:
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.AUDIO,
                status=ProcessingStatus.COMPLETED,
                file_size=0,  # Will be set by caller
                metadata={
                    'format': 'audio',
                    'extension': file_path.suffix.lower(),
                }
            )
        except Exception as e:
            logger.error(f"Error processing audio {file_path}: {e}")
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.AUDIO,
                status=ProcessingStatus.FAILED,
                file_size=0,
                error_message=str(e),
            )

    def _process_document(self, file_path: Path) -> ProcessingResult:
        """Process document file"""
        try:
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.DOCUMENT,
                status=ProcessingStatus.COMPLETED,
                file_size=0,  # Will be set by caller
                metadata={
                    'format': 'document',
                    'extension': file_path.suffix.lower(),
                }
            )
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return ProcessingResult(
                file_id=str(uuid.uuid4()),
                filename=file_path.name,
                media_type=MediaType.DOCUMENT,
                status=ProcessingStatus.FAILED,
                file_size=0,
                error_message=str(e),
            )


class BatchUploadProcessor:
    """Batch process multiple media files"""

    def __init__(self, processor: MediaProcessor):
        """Initialize batch processor"""
        self.processor = processor
        self.results = []

    def process_batch(self, file_paths: List[str]) -> Dict:
        """Process a batch of files"""
        import time
        start_time = time.time()

        self.results = []
        successful = 0
        failed = 0
        skipped = 0

        for file_path in file_paths:
            result = self.processor.process_file(file_path)
            self.results.append(result)

            if result.status == ProcessingStatus.COMPLETED:
                successful += 1
            elif result.status == ProcessingStatus.FAILED:
                failed += 1
            elif result.status == ProcessingStatus.SKIPPED:
                skipped += 1

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_files': len(file_paths),
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'processing_time': time.time() - start_time,
            'results': [r.to_dict() for r in self.results],
        }

    def get_summary(self) -> Dict:
        """Get summary of batch processing"""
        if not self.results:
            return {}

        total_size = sum(r.file_size for r in self.results)
        total_time = sum(r.processing_time for r in self.results)

        media_type_counts = {}
        for result in self.results:
            media_type = result.media_type.value
            media_type_counts[media_type] = media_type_counts.get(media_type, 0) + 1

        return {
            'total_files': len(self.results),
            'total_size_mb': total_size / (1024 * 1024),
            'total_processing_time': total_time,
            'average_time_per_file': total_time / len(self.results) if self.results else 0,
            'media_type_breakdown': media_type_counts,
            'successful': sum(1 for r in self.results if r.status == ProcessingStatus.COMPLETED),
            'failed': sum(1 for r in self.results if r.status == ProcessingStatus.FAILED),
        }


# Global processor instance
_processor = None


def get_media_processor(upload_dir: str = "uploads") -> MediaProcessor:
    """Get or create media processor instance"""
    global _processor
    if _processor is None:
        _processor = MediaProcessor(upload_dir=upload_dir)
    return _processor


def get_batch_processor(upload_dir: str = "uploads") -> BatchUploadProcessor:
    """Get batch processor"""
    processor = get_media_processor(upload_dir)
    return BatchUploadProcessor(processor)
