"""OCR provider abstraction."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class OcrProvider(ABC):
    """Interface for PDF/image OCR text extraction."""

    @abstractmethod
    def extract_text(self, file_path: str, mime_type: str) -> dict:
        """Return {"text": str, "pages": list[dict], "page_count": int}."""
        ...


class StubOcrProvider(OcrProvider):
    """Default stub — marks job as needing provider configuration."""

    def extract_text(self, file_path: str, mime_type: str) -> dict:
        return {
            "text": "",
            "pages": [],
            "page_count": 0,
            "status": "needs_provider_configured",
            "message": (
                "No OCR provider configured. Set OCR_PROVIDER env var "
                "to enable OCR (e.g., tesseract, textract)."
            ),
        }


def get_ocr_provider() -> OcrProvider:
    """Factory — returns the configured OCR provider."""
    import os
    provider = os.getenv("OCR_PROVIDER", "stub")
    if provider == "stub":
        return StubOcrProvider()
    # Future: add tesseract, textract, etc.
    logger.warning("Unknown OCR provider '%s', falling back to stub", provider)
    return StubOcrProvider()
