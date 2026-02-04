"""
FREE Tier One-Time Upload Handler
Manages the single file upload allowance for FREE tier users
Tracks usage, validates limits, provides upgrade prompts
"""

import os
from datetime import datetime, timedelta

from flask import flash, jsonify
from pypdf import PdfReader  # Migrated from PyPDF2 (deprecated)

from .models_auth import TierLevel, db


class OneTimeUploadManager:
    """Manages one-time upload for FREE tier users"""

    @staticmethod
    def can_upload(user):
        """
        Check if FREE tier user can use their one-time upload

        Returns:
            tuple: (can_upload: bool, reason: str)
        """
        # Only applies to FREE tier
        if user.tier != TierLevel.FREE:
            return True, "Paid tier - uploads allowed"

        # Check if already used
        if user.one_time_upload_used:
            return (
                False,
                f"You've already used your one-time upload on {user.one_time_upload_date.strftime('%B %d, %Y')}. Upgrade to STARTER ($29/mo) to upload more files.",
            )

        return True, "One-time upload available"

    @staticmethod
    def validate_file(file, file_type):
        """
        Validate file meets FREE tier limits

        Args:
            file: FileStorage object
            file_type: 'video' or 'pdf'

        Returns:
            tuple: (is_valid: bool, error_message: str, details: dict)
        """
        from werkzeug.utils import secure_filename

        # Get file size
        file.seek(0, os.SEEK_END)
        file_size_bytes = file.tell()
        file.seek(0)  # Reset pointer

        file_size_mb = file_size_bytes / (1024 * 1024)

        # FREE tier limits
        MAX_FILE_SIZE_MB = 50
        MAX_VIDEO_DURATION_MIN = 5
        MAX_PDF_PAGES = 10

        # Basic size check
        if file_size_mb > MAX_FILE_SIZE_MB:
            return (
                False,
                f"File size ({file_size_mb:.1f} MB) exceeds FREE tier limit of {MAX_FILE_SIZE_MB} MB. Upgrade to STARTER for 512 MB files.",
                {},
            )

        # File type specific validation
        if file_type == "pdf":
            try:
                # Count pages
                pdf_reader = PdfReader(file)
                page_count = len(pdf_reader.pages)
                file.seek(0)  # Reset pointer

                if page_count > MAX_PDF_PAGES:
                    return (
                        False,
                        f"PDF has {page_count} pages. FREE tier limit is {MAX_PDF_PAGES} pages. Upgrade to STARTER ($29/mo) for 5 documents with up to 100 pages each.",
                        {"page_count": page_count, "max_pages": MAX_PDF_PAGES},
                    )

                return (
                    True,
                    "PDF validated successfully",
                    {"page_count": page_count, "file_size_mb": round(file_size_mb, 2)},
                )

            except Exception as e:
                return False, f"Error reading PDF: {str(e)}", {}

        elif file_type == "video":
            # For video, we'll estimate duration from file size
            # Rough estimate: 10 MB per minute for typical BWC footage
            estimated_duration_min = file_size_mb / 10

            if estimated_duration_min > MAX_VIDEO_DURATION_MIN:
                return (
                    False,
                    f"Video estimated at {estimated_duration_min:.1f} minutes. FREE tier limit is {MAX_VIDEO_DURATION_MIN} minutes. Upgrade to STARTER ($29/mo) for 1 hour of video per month.",
                    {
                        "estimated_duration_min": round(estimated_duration_min, 1),
                        "max_duration_min": MAX_VIDEO_DURATION_MIN,
                    },
                )

            return (
                True,
                "Video validated successfully",
                {
                    "estimated_duration_min": round(estimated_duration_min, 1),
                    "file_size_mb": round(file_size_mb, 2),
                },
            )

        return False, "Unknown file type", {}

    @staticmethod
    def mark_upload_used(user):
        """
        Mark that user has used their one-time upload

        Args:
            user: User object
        """
        user.one_time_upload_used = True
        user.one_time_upload_date = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def get_upload_status(user):
        """
        Get detailed upload status for FREE tier user

        Returns:
            dict: Status information
        """
        if user.tier != TierLevel.FREE:
            return {
                "tier": user.tier.name,
                "upload_type": "recurring",
                "one_time_upload_available": False,
                "message": f"{user.tier.name} tier has recurring upload limits",
            }

        return {
            "tier": "FREE",
            "upload_type": "one-time",
            "one_time_upload_available": not user.one_time_upload_used,
            "one_time_upload_used": user.one_time_upload_used,
            "upload_date": (
                user.one_time_upload_date.isoformat() if user.one_time_upload_date else None
            ),
            "limits": {"max_file_size_mb": 50, "max_pdf_pages": 10, "max_video_duration_min": 5},
            "message": (
                "You have one upload available"
                if not user.one_time_upload_used
                else f'Upload used on {user.one_time_upload_date.strftime("%B %d, %Y")}'
            ),
        }

    @staticmethod
    def get_upgrade_prompt(reason="general"):
        """
        Get appropriate upgrade prompt based on context

        Args:
            reason: 'limit_reached', 'already_used', 'pages_exceeded', 'duration_exceeded', 'general'

        Returns:
            dict: Upgrade prompt with CTA
        """
        prompts = {
            "limit_reached": {
                "title": "Ready for More?",
                "message": "You've used your one-time FREE upload. Upgrade to STARTER to analyze more files.",
                "cta_text": "Upgrade to STARTER - $29/mo",
                "cta_url": "/pricing",
                "features": [
                    "10 videos per month",
                    "5 PDF documents per month",
                    "Up to 512 MB file size",
                    "Basic AI assistant",
                    "10 GB storage",
                ],
            },
            "already_used": {
                "title": "Upload Already Used",
                "message": "FREE tier includes one file upload to test the platform. You've already used yours!",
                "cta_text": "See Paid Plans - Starting at $29/mo",
                "cta_url": "/pricing",
                "features": [
                    "Process multiple files monthly",
                    "No watermarks on exports",
                    "AI-powered analysis",
                    "Court-ready reports",
                ],
            },
            "pages_exceeded": {
                "title": "Document Too Large",
                "message": "FREE tier supports PDFs up to 10 pages. Upgrade to process larger documents.",
                "cta_text": "Upgrade to STARTER - $29/mo",
                "cta_url": "/pricing",
                "features": [
                    "5 PDFs per month",
                    "Up to 100 pages per document",
                    "OCR & AI analysis",
                    "Extract key evidence",
                ],
            },
            "duration_exceeded": {
                "title": "Video Too Long",
                "message": "FREE tier supports videos up to 5 minutes. Upgrade for longer footage.",
                "cta_text": "Upgrade to STARTER - $29/mo",
                "cta_url": "/pricing",
                "features": [
                    "10 videos per month",
                    "1 hour total duration",
                    "AI transcription",
                    "Timeline analysis",
                ],
            },
            "general": {
                "title": "Unlock Full Power",
                "message": "FREE tier gives you a taste. Paid plans unlock professional-grade analysis.",
                "cta_text": "View All Plans",
                "cta_url": "/pricing",
                "features": [
                    "Recurring monthly uploads",
                    "AI-powered insights",
                    "Watermark-free exports",
                    "Priority support",
                ],
            },
        }

        return prompts.get(reason, prompts["general"])


def free_tier_upload_route_decorator(f):
    """
    Decorator for upload routes to enforce FREE tier one-time upload

    Usage:
        @app.route('/upload', methods=['POST'])
        @login_required
        @free_tier_upload_route_decorator
        def upload_file():
            # Your upload logic here
            pass
    """
    from functools import wraps

    from flask_login import current_user

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if FREE tier user can upload
        can_upload, reason = OneTimeUploadManager.can_upload(current_user)

        if not can_upload:
            # Return upgrade prompt
            upgrade_prompt = OneTimeUploadManager.get_upgrade_prompt("already_used")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": reason,
                        "upgrade_required": True,
                        "upgrade_prompt": upgrade_prompt,
                    }
                ),
                403,
            )

        # Proceed with upload
        response = f(*args, **kwargs)

        # If upload was successful, mark as used for FREE tier
        if current_user.tier == TierLevel.FREE and response.status_code == 200:
            OneTimeUploadManager.mark_upload_used(current_user)

        return response

    return decorated_function


# Export key components
__all__ = ["OneTimeUploadManager", "free_tier_upload_route_decorator"]


