# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
FREE Tier Data Retention Manager
Automatically deletes FREE tier user data after 7 days
Runs as scheduled job to keep storage costs minimal
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from .models_auth import TierLevel, db


class DataRetentionManager:
    """Manages automatic data deletion for FREE tier users"""

    # FREE tier data retention period
    RETENTION_DAYS = 7

    @staticmethod
    def get_expiration_date(user):
        """
        Calculate when user's data expires

        Args:
            user: User object

        Returns:
            datetime or None: Expiration date (None if no expiration)
        """
        # Only FREE tier has expiration
        if user.tier != TierLevel.FREE:
            return None

        # If they used their one-time upload, data expires 7 days after upload
        if user.one_time_upload_date:
            return user.one_time_upload_date + timedelta(days=DataRetentionManager.RETENTION_DAYS)

        # No upload yet, no data to expire
        return None

    @staticmethod
    def days_until_expiration(user):
        """
        Get days remaining until data deletion

        Returns:
            int or None: Days remaining (None if no expiration)
        """
        expiration = DataRetentionManager.get_expiration_date(user)
        if not expiration:
            return None

        days_remaining = (expiration - datetime.utcnow()).days
        return max(0, days_remaining)  # Don't return negative

    @staticmethod
    def is_data_expired(user):
        """
        Check if user's data should be deleted

        Returns:
            bool: True if data is expired and should be deleted
        """
        expiration = DataRetentionManager.get_expiration_date(user)
        if not expiration:
            return False

        return datetime.utcnow() >= expiration

    @staticmethod
    def cleanup_user_data(user):
        """
        Delete all user files and case data (FREE tier only)

        Args:
            user: User object

        Returns:
            dict: Cleanup summary
        """
        if user.tier != TierLevel.FREE:
            return {"deleted": False, "reason": "Not a FREE tier user"}

        if not DataRetentionManager.is_data_expired(user):
            days_remaining = DataRetentionManager.days_until_expiration(user)
            return {
                "deleted": False,
                "reason": f"Data not expired yet ({days_remaining} days remaining)",
            }

        deleted_items = {"files": 0, "storage_mb": 0, "cases": 0}

        try:
            # Delete uploaded files
            user_upload_dir = Path(f"uploads/user_{user.id}")
            if user_upload_dir.exists():
                # Calculate storage before deletion
                total_size = sum(
                    f.stat().st_size for f in user_upload_dir.glob("**/*") if f.is_file()
                )
                deleted_items["storage_mb"] = round(total_size / (1024 * 1024), 2)
                deleted_items["files"] = len(list(user_upload_dir.glob("**/*")))

                # Delete directory
                shutil.rmtree(user_upload_dir)

            # Delete case data (if you have a Case model, uncomment below)
            # from models import Case
            # cases = Case.query.filter_by(user_id=user.id).all()
            # for case in cases:
            #     db.session.delete(case)
            #     deleted_items['cases'] += 1

            # Reset user storage tracking
            user.storage_used_mb = 0.0

            # Optional: Reset one-time upload to let them try again
            # user.one_time_upload_used = False
            # user.one_time_upload_date = None

            db.session.commit()

            return {
                "deleted": True,
                "items": deleted_items,
                "message": f"Deleted {deleted_items['files']} files ({deleted_items['storage_mb']} MB) and {deleted_items['cases']} cases",
            }

        except Exception as e:
            db.session.rollback()
            return {"deleted": False, "error": str(e)}

    @staticmethod
    def send_expiration_warning(user, days_remaining):
        """
        Send email warning about upcoming data deletion

        Args:
            user: User object
            days_remaining: int, days until deletion

        Returns:
            bool: True if email sent successfully
        """
        # TODO: Implement email sending
        # For now, just log
        print(f"[WARNING] User {user.email} has {days_remaining} days until data deletion")

        # Email content would be:
        email_content = f"""
        Subject: Your Evident Data Expires in {days_remaining} Days
        
        Hi {user.full_name or "there"},
        
        This is a friendly reminder that your FREE tier data will be automatically 
        deleted in {days_remaining} days.
        
        Want to keep your analysis? Upgrade to STARTER for just $29/month:
        - Keep all your data permanently
        - Upload 10 videos & 5 PDFs per month
        - Access AI-powered insights
        - Remove watermarks
        
        [Upgrade Now] → https://Evident.info/pricing
        
        Questions? Reply to this email.
        
        - The Evident Team
        """

        # In production, use SendGrid, AWS SES, etc.
        # send_email(user.email, email_content)

        return True

    @staticmethod
    def run_cleanup_job():
        """
        Scheduled job to cleanup expired FREE tier data
        Run daily via cron, Celery, or cloud scheduler

        Returns:
            dict: Cleanup job summary
        """
        from models_auth import User

        summary = {
            "total_checked": 0,
            "warnings_sent": 0,
            "deletions": 0,
            "errors": 0,
            "storage_freed_mb": 0,
        }

        # Get all FREE tier users
        free_users = User.query.filter_by(tier=TierLevel.FREE).all()
        summary["total_checked"] = len(free_users)

        for user in free_users:
            days_remaining = DataRetentionManager.days_until_expiration(user)

            if days_remaining is None:
                continue  # No upload yet, skip

            # Send warnings at 3 days and 1 day
            if days_remaining in [3, 1]:
                try:
                    DataRetentionManager.send_expiration_warning(user, days_remaining)
                    summary["warnings_sent"] += 1
                except Exception as e:
                    print(f"Error sending warning to {user.email}: {e}")
                    summary["errors"] += 1

            # Delete if expired
            if days_remaining == 0:
                try:
                    result = DataRetentionManager.cleanup_user_data(user)
                    if result.get("deleted"):
                        summary["deletions"] += 1
                        summary["storage_freed_mb"] += result["items"]["storage_mb"]
                except Exception as e:
                    print(f"Error cleaning up user {user.email}: {e}")
                    summary["errors"] += 1

        print(
            f"[CLEANUP JOB] Checked {summary['total_checked']} users, "
            f"sent {summary['warnings_sent']} warnings, "
            f"deleted {summary['deletions']} accounts, "
            f"freed {summary['storage_freed_mb']:.2f} MB"
        )

        return summary


def get_user_data_status(user):
    """
    Get comprehensive data status for user dashboard

    Returns:
        dict: Data retention status
    """
    if user.tier != TierLevel.FREE:
        return {
            "tier": user.tier.name,
            "retention_policy": "permanent",
            "message": "Your data is stored permanently",
        }

    expiration = DataRetentionManager.get_expiration_date(user)
    days_remaining = DataRetentionManager.days_until_expiration(user)

    if not expiration:
        return {
            "tier": "FREE",
            "retention_policy": "7 days after upload",
            "upload_used": False,
            "message": "Upload a file to start your 7-day trial",
        }

    return {
        "tier": "FREE",
        "retention_policy": "7 days",
        "upload_used": True,
        "upload_date": user.one_time_upload_date.strftime("%B %d, %Y"),
        "expiration_date": expiration.strftime("%B %d, %Y"),
        "days_remaining": days_remaining,
        "expires_soon": days_remaining <= 3,
        "message": (
            f"Your data will be deleted in {days_remaining} days. Upgrade to keep it!"
            if days_remaining > 0
            else "Your data has expired and will be deleted soon."
        ),
    }


# Export key components
__all__ = ["DataRetentionManager", "get_user_data_status"]
