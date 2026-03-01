"""Transcription provider abstraction."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TranscriptionProvider(ABC):
    """Interface for audio/video transcription."""

    @abstractmethod
    def transcribe(self, file_path: str, mime_type: str) -> dict:
        """Return {"text": str, "segments": list[dict], "language": str}."""
        ...


class StubTranscriptionProvider(TranscriptionProvider):
    """Default stub — marks job as needing provider configuration."""

    def transcribe(self, file_path: str, mime_type: str) -> dict:
        return {
            "text": "",
            "segments": [],
            "language": "unknown",
            "status": "needs_provider_configured",
            "message": (
                "No transcription provider configured. Set TRANSCRIPTION_PROVIDER env var "
                "to enable transcription (e.g., whisper, assembly_ai)."
            ),
        }


def get_transcription_provider() -> TranscriptionProvider:
    """Factory — returns the configured transcription provider."""
    import os
    provider = os.getenv("TRANSCRIPTION_PROVIDER", "stub")
    if provider == "stub":
        return StubTranscriptionProvider()
    # Future: add whisper, assembly_ai, etc.
    logger.warning("Unknown transcription provider '%s', falling back to stub", provider)
    return StubTranscriptionProvider()
