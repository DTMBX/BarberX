# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Smart Meter Alert System
Monitors usage quotas and sends alerts at thresholds
"""

from datetime import datetime

from flask import current_app

from .models_auth import User, db
from .usage_meter import SmartMeter, UsageQuota


class AlertManager:
    """Manages usage alerts and notifications"""

    @staticmethod
    def check_and_send_alerts(user_id: int):
        """
        Check all quotas and send alerts if thresholds exceeded

        Thresholds:
        - 80% warning
        - 95% critical warning
        - 100% quota exceeded
        """
        quota = UsageQuota.query.filter_by(user_id=user_id).first()
        if not quota:
            return

        user = User.query.get(user_id)
        if not user:
            return

        quota.reset_if_new_period()

        alerts_sent = []

        # Check each quota type
        quota_types = [
            ("ai_tokens", "AI Tokens"),
            ("ai_requests", "AI Requests"),
            ("storage", "Storage"),
            ("files", "Files Uploaded"),
            ("analyses", "Analyses"),
            ("workflows", "Workflows"),
            ("cost", "Monthly Cost"),
        ]

        for quota_type, display_name in quota_types:
            percent = quota.get_usage_percent(quota_type)

            # 100% exceeded alert
            if percent >= 100 and not quota.alert_100_percent_sent:
                AlertManager._send_alert(
                    user=user,
                    alert_type="quota_exceeded",
                    quota_name=display_name,
                    percent=percent,
                    quota_obj=quota,
                )
                quota.alert_100_percent_sent = True
                alerts_sent.append(f"{display_name}: 100% (EXCEEDED)")

            # 95% critical alert
            elif percent >= 95 and not quota.alert_95_percent_sent:
                AlertManager._send_alert(
                    user=user,
                    alert_type="quota_critical",
                    quota_name=display_name,
                    percent=percent,
                    quota_obj=quota,
                )
                quota.alert_95_percent_sent = True
                alerts_sent.append(f"{display_name}: 95% (CRITICAL)")

            # 80% warning alert
            elif percent >= 80 and not quota.alert_80_percent_sent:
                AlertManager._send_alert(
                    user=user,
                    alert_type="quota_warning",
                    quota_name=display_name,
                    percent=percent,
                    quota_obj=quota,
                )
                quota.alert_80_percent_sent = True
                alerts_sent.append(f"{display_name}: 80% (WARNING)")

        if alerts_sent:
            db.session.commit()
            current_app.logger.info(f"Alerts sent for user {user_id}: {', '.join(alerts_sent)}")

        return alerts_sent

    @staticmethod
    def _send_alert(
        user: User, alert_type: str, quota_name: str, percent: float, quota_obj: UsageQuota
    ):
        """
        Send alert notification

        Args:
            user: User object
            alert_type: 'quota_warning', 'quota_critical', or 'quota_exceeded'
            quota_name: Display name of the quota
            percent: Percentage used
            quota_obj: UsageQuota object for details
        """
        # Log to application logs
        severity = {
            "quota_warning": "WARNING",
            "quota_critical": "CRITICAL",
            "quota_exceeded": "ERROR",
        }.get(alert_type, "INFO")

        message = f"User {user.email} - {quota_name} at {percent:.1f}%"
        current_app.logger.log(
            getattr(current_app.logger, severity.lower(), current_app.logger.info),
            f"[QUOTA ALERT] {message}",
        )

        # Track alert event
        SmartMeter.track_event(
            event_type="quota_alert",
            event_category="system",
            user_id=user.id,
            resource_name=quota_name,
            quantity=percent,
            status=alert_type,
        )

        # TODO: Send email notification
        # email_body = AlertManager._build_alert_email(user, alert_type, quota_name, percent, quota_obj)
        # send_email(to=user.email, subject=f"Evident Usage Alert: {quota_name}", body=email_body)

        # TODO: Send in-app notification
        # create_notification(user_id=user.id, type=alert_type, message=message)

        # TODO: Send webhook if configured
        # if user.webhook_url:
        #     send_webhook(url=user.webhook_url, data={'alert': alert_type, 'quota': quota_name, 'percent': percent})

    @staticmethod
    def _build_alert_email(
        user: User, alert_type: str, quota_name: str, percent: float, quota: UsageQuota
    ) -> str:
        """Build email body for alert"""

        severity_emoji = {"quota_warning": "⚠️", "quota_critical": "🔴", "quota_exceeded": "❌"}

        severity_text = {
            "quota_warning": "Warning: High Usage",
            "quota_critical": "Critical: Nearly Exceeded",
            "quota_exceeded": "Alert: Quota Exceeded",
        }

        emoji = severity_emoji.get(alert_type, "📊")
        title = severity_text.get(alert_type, "Usage Alert")

        email_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #0a0a0f; color: #d4af37; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f5f5f5; }}
        .alert-box {{ background: white; border-left: 4px solid #ff6b6b; padding: 15px; margin: 20px 0; }}
        .warning {{ border-color: #ffd43b; }}
        .critical {{ border-color: #ff6b6b; }}
        .stats {{ background: white; padding: 15px; margin: 10px 0; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #d4af37; color: white; text-decoration: none; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{emoji} Evident Usage Alert</h1>
        </div>
        <div class="content">
            <h2>{title}</h2>
            <p>Hello {user.full_name or user.email},</p>
            
            <div class="alert-box {"warning" if percent < 95 else "critical"}">
                <h3>{quota_name}</h3>
                <p style="font-size: 24px; margin: 10px 0;"><strong>{
            percent:.1f}%</strong> of quota used</p>
            </div>
            
            <div class="stats">
                <h4>Your Current Usage:</h4>
                <ul>
                    <li>AI Tokens: {quota.ai_tokens_used:,} / {quota.ai_tokens_limit:,} ({
            quota.get_usage_percent("ai_tokens"):.1f}%)</li>
                    <li>AI Requests: {quota.ai_requests_count} / {quota.ai_requests_limit} ({
            quota.get_usage_percent("ai_requests"):.1f}%)</li>
                    <li>Storage: {quota.storage_bytes_used / 1048576:.1f} MB / {
            quota.storage_bytes_limit / 1048576:.1f} MB ({
            quota.get_usage_percent("storage"):.1f}%)</li>
                    <li>Files: {quota.files_uploaded_count} / {quota.files_uploaded_limit} ({
            quota.get_usage_percent("files"):.1f}%)</li>
                    <li>Cost: ${float(quota.total_cost_usd):.2f} / ${
            float(quota.cost_limit_usd):.2f} ({quota.get_usage_percent("cost"):.1f}%)</li>
                </ul>
            </div>
            
            <div class="stats">
                <h4>Billing Period:</h4>
                <p>Period ends: {quota.period_end.strftime("%B %d, %Y")}</p>
                <p>Days remaining: {(quota.period_end - datetime.utcnow()).days}</p>
            </div>
            
            <p style="margin-top: 30px;">
                {
            "<strong>Action Required:</strong> Your quota has been exceeded. Please upgrade your plan to continue using Evident."
            if percent >= 100
            else "<strong>Recommended:</strong> Consider upgrading your plan to avoid service interruptions."
            if percent >= 95
            else "You're approaching your quota limit. Monitor your usage to avoid interruptions."
        }
            </p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://Evident.info/pricing" class="button">View Upgrade Options</a>
            </p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://Evident.info/workspace">View Your Dashboard</a>
            </p>
        </div>
        <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
            <p>Evident - Legal Intelligence Platform</p>
            <p>This is an automated usage alert. To adjust notification settings, visit your account settings.</p>
        </div>
    </div>
</body>
</html>
"""
        return email_body

    @staticmethod
    def check_all_users_quotas():
        """Background job to check quotas for all active users"""
        users = User.query.filter(User.is_active == True).all()

        total_alerts = 0
        for user in users:
            alerts = AlertManager.check_and_send_alerts(user.id)
            if alerts:
                total_alerts += len(alerts)

        current_app.logger.info(
            f"Quota check complete. {total_alerts} alerts sent across {len(users)} users."
        )
        return total_alerts


def init_alert_scheduler(app):
    """
    Initialize alert scheduler (call this from app.py)

    Usage in app.py:
        from alerts import init_alert_scheduler
        init_alert_scheduler(app)
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()

        # Check quotas every hour
        scheduler.add_job(
            func=lambda: app.app_context().do(AlertManager.check_all_users_quotas),
            trigger="interval",
            hours=1,
            id="quota_check",
            name="Check user quotas and send alerts",
        )

        scheduler.start()
        app.logger.info("Alert scheduler started - checking quotas every hour")

        return scheduler
    except ImportError:
        app.logger.warning(
            "APScheduler not installed. Quota alerts will not be automated. Install with: pip install APScheduler"
        )
        return None
