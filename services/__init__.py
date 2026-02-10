"""
Evident Services Package
AI and media processing services

Note: Imports are lazy to avoid loading heavy dependencies (PyPDF2, pymupdf, etc.)
      unless explicitly needed. Import directly from submodules:
      
      from services.hashing_service import compute_sha256_file
      from services.media_processor import MediaProcessor
"""

# Lazy imports via __getattr__ to avoid loading heavy dependencies by default
def __getattr__(name):
    """Lazy-load service modules and their exports."""
    if name in (
        'MediaProcessor',
        'MediaValidator',
        'MediaType',
        'ProcessingStatus',
        'ProcessingResult',
        'BatchUploadProcessor',
        'get_media_processor',
        'get_batch_processor',
    ):
        from .media_processor import (
            BatchUploadProcessor,
            MediaProcessor,
            MediaType,
            MediaValidator,
            ProcessingResult,
            ProcessingStatus,
            get_batch_processor,
            get_media_processor,
        )
        globals().update({
            'MediaProcessor': MediaProcessor,
            'MediaValidator': MediaValidator,
            'MediaType': MediaType,
            'ProcessingStatus': ProcessingStatus,
            'ProcessingResult': ProcessingResult,
            'BatchUploadProcessor': BatchUploadProcessor,
            'get_media_processor': get_media_processor,
            'get_batch_processor': get_batch_processor,
        })
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'get_media_processor',
    'get_batch_processor',
    'MediaProcessor',
    'MediaValidator',
    'MediaType',
    'ProcessingStatus',
    'ProcessingResult',
    'BatchUploadProcessor',
]
