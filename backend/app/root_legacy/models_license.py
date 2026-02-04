"""
Evident License Management System
Handles license generation, validation, and enforcement for self-hosted deployments
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from enum import Enum

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class LicenseType(Enum):
    """License types for different deployment models"""

    SAAS = "saas"  # Web-based, managed by us
    SELF_HOSTED = "self_hosted"  # Customer runs on their servers
    TRIAL = "trial"  # 30-day trial of self-hosted


class LicenseStatus(Enum):
    """License status"""

    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class License(db.Model):
    """
    License keys for self-hosted deployments
    """

    __tablename__ = "licenses"

    id = db.Column(db.Integer, primary_key=True)

    # License identification
    license_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    license_type = db.Column(db.Enum(LicenseType), nullable=False)
    status = db.Column(db.Enum(LicenseStatus), default=LicenseStatus.ACTIVE)

    # Customer info
    organization_name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_name = db.Column(db.String(100))

    # Tier and limits
    tier = db.Column(db.String(50), default="ENTERPRISE")  # ENTERPRISE, CUSTOM
    max_users = db.Column(db.Integer, default=10)
    max_machines = db.Column(db.Integer, default=1)  # How many servers can use this license
    monthly_video_quota = db.Column(db.Integer, default=500)  # -1 = unlimited

    # Validity
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Machine tracking
    registered_machines = db.Column(db.JSON, default=list)  # List of machine fingerprints

    # Feature flags
    features = db.Column(db.JSON, default=dict)  # {"white_label": true, "api_access": true}

    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    validations = db.relationship("LicenseValidation", backref="license", lazy=True)

    @staticmethod
    def generate_license_key():
        """Generate a secure license key"""
        # Format: BX-XXXX-XXXX-XXXX-XXXX (BX = Evident)
        random_bytes = secrets.token_bytes(16)
        key_hash = hashlib.sha256(random_bytes).hexdigest()[:16].upper()

        # Split into 4-character chunks
        parts = [key_hash[i : i + 4] for i in range(0, 16, 4)]
        return f"BX-{'-'.join(parts)}"

    def is_valid(self):
        """Check if license is currently valid"""
        if self.status != LicenseStatus.ACTIVE:
            return False

        if self.expires_at < datetime.utcnow():
            self.status = LicenseStatus.EXPIRED
            db.session.commit()
            return False

        return True

    def can_register_machine(self, machine_id):
        """Check if a new machine can be registered"""
        if not self.is_valid():
            return False

        # Already registered
        if machine_id in self.registered_machines:
            return True

        # Check limit
        if len(self.registered_machines) >= self.max_machines:
            return False

        return True

    def register_machine(self, machine_id, machine_info=None):
        """Register a new machine"""
        if not self.can_register_machine(machine_id):
            raise ValueError("Cannot register machine - limit reached or license invalid")

        if machine_id not in self.registered_machines:
            machines = self.registered_machines or []
            machines.append(
                {
                    "machine_id": machine_id,
                    "registered_at": datetime.utcnow().isoformat(),
                    "info": machine_info or {},
                }
            )
            self.registered_machines = machines
            db.session.commit()

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "license_key": self.license_key,
            "organization": self.organization_name,
            "type": self.license_type.value,
            "status": self.status.value,
            "tier": self.tier,
            "expires_at": self.expires_at.isoformat(),
            "max_users": self.max_users,
            "max_machines": self.max_machines,
            "registered_machines": len(self.registered_machines or []),
            "features": self.features or {},
            "monthly_video_quota": self.monthly_video_quota,
        }


class LicenseValidation(db.Model):
    """
    Track license validation attempts (for monitoring and analytics)
    """

    __tablename__ = "license_validations"

    id = db.Column(db.Integer, primary_key=True)
    license_id = db.Column(db.Integer, db.ForeignKey("licenses.id"), nullable=False)

    # Validation details
    machine_id = db.Column(db.String(64), nullable=False)
    machine_info = db.Column(db.JSON)  # OS, version, hostname, etc.

    # Result
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.String(255))

    # Usage stats reported
    usage_stats = db.Column(db.JSON)  # Videos processed, users active, etc.

    # Timestamps
    validated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Request info
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(255))


class LicenseService:
    """Service for managing licenses"""

    @staticmethod
    def create_license(
        organization_name,
        contact_email,
        tier="ENTERPRISE",
        duration_days=365,
        max_machines=1,
        **kwargs,
    ):
        """
        Create a new license

        Args:
            organization_name: Customer organization
            contact_email: Contact email
            tier: License tier (ENTERPRISE, CUSTOM)
            duration_days: How long license is valid
            max_machines: Number of servers allowed
            **kwargs: Additional options (features, quotas, etc.)

        Returns:
            License object
        """
        license = License(
            license_key=License.generate_license_key(),
            license_type=kwargs.get("license_type", LicenseType.SELF_HOSTED),
            organization_name=organization_name,
            contact_email=contact_email,
            contact_name=kwargs.get("contact_name"),
            tier=tier,
            max_users=kwargs.get("max_users", 10),
            max_machines=max_machines,
            monthly_video_quota=kwargs.get("monthly_video_quota", 500),
            expires_at=datetime.utcnow() + timedelta(days=duration_days),
            features=kwargs.get(
                "features",
                {
                    "white_label": True,
                    "api_access": True,
                    "priority_support": True,
                    "forensic_analysis": True,
                },
            ),
            notes=kwargs.get("notes"),
        )

        db.session.add(license)
        db.session.commit()

        return license

    @staticmethod
    def validate_license(license_key, machine_id, machine_info=None, usage_stats=None):
        """
        Validate a license key

        Args:
            license_key: The license key to validate
            machine_id: Unique machine fingerprint
            machine_info: Machine details (OS, version, etc.)
            usage_stats: Current usage statistics

        Returns:
            dict: Validation result with license info or error
        """
        license = License.query.filter_by(license_key=license_key).first()

        # Log validation attempt
        validation = LicenseValidation(
            license_id=license.id if license else None,
            machine_id=machine_id,
            machine_info=machine_info,
            usage_stats=usage_stats,
        )

        try:
            if not license:
                validation.success = False
                validation.error_message = "Invalid license key"
                db.session.add(validation)
                db.session.commit()
                return {"valid": False, "error": "Invalid license key", "code": "INVALID_KEY"}

            if not license.is_valid():
                validation.success = False
                validation.error_message = f"License {license.status.value}"
                db.session.add(validation)
                db.session.commit()
                return {
                    "valid": False,
                    "error": f"License is {license.status.value}",
                    "code": "LICENSE_INACTIVE",
                    "expires_at": license.expires_at.isoformat(),
                }

            # Check machine registration
            if not license.can_register_machine(machine_id):
                validation.success = False
                validation.error_message = "Machine limit exceeded"
                db.session.add(validation)
                db.session.commit()
                return {
                    "valid": False,
                    "error": f"Maximum machines ({license.max_machines}) already registered",
                    "code": "MACHINE_LIMIT",
                }

            # Register machine if new
            license.register_machine(machine_id, machine_info)

            # Successful validation
            validation.success = True
            db.session.add(validation)
            db.session.commit()

            return {
                "valid": True,
                "license": license.to_dict(),
                "machine_registered": True,
                "grace_period_hours": 72,  # Can run offline for 3 days
            }

        except Exception as e:
            validation.success = False
            validation.error_message = str(e)
            db.session.add(validation)
            db.session.commit()

            return {
                "valid": False,
                "error": "Validation error",
                "code": "VALIDATION_ERROR",
            }

    @staticmethod
    def renew_license(license_key, duration_days=365):
        """Renew an existing license"""
        license = License.query.filter_by(license_key=license_key).first()

        if not license:
            raise ValueError("License not found")

        # Extend from current expiry or now (whichever is later)
        base_date = max(license.expires_at, datetime.utcnow())
        license.expires_at = base_date + timedelta(days=duration_days)
        license.status = LicenseStatus.ACTIVE

        db.session.commit()
        return license

    @staticmethod
    def suspend_license(license_key, reason=None):
        """Suspend a license (e.g., non-payment)"""
        license = License.query.filter_by(license_key=license_key).first()

        if not license:
            raise ValueError("License not found")

        license.status = LicenseStatus.SUSPENDED
        if reason:
            license.notes = f"{license.notes or ''}\n[SUSPENDED] {reason}"

        db.session.commit()
        return license

    @staticmethod
    def get_usage_stats(license_key):
        """Get usage statistics for a license"""
        license = License.query.filter_by(license_key=license_key).first()

        if not license:
            raise ValueError("License not found")

        # Get recent validations
        recent_validations = (
            LicenseValidation.query.filter_by(license_id=license.id)
            .order_by(LicenseValidation.validated_at.desc())
            .limit(100)
            .all()
        )

        # Aggregate usage stats
        total_videos = 0
        active_machines = set()

        for validation in recent_validations:
            if validation.usage_stats:
                total_videos += validation.usage_stats.get("videos_processed", 0)
            active_machines.add(validation.machine_id)

        return {
            "license_key": license_key,
            "organization": license.organization_name,
            "total_validations": len(recent_validations),
            "active_machines": len(active_machines),
            "estimated_videos_processed": total_videos,
            "last_validation": (
                recent_validations[0].validated_at.isoformat() if recent_validations else None
            ),
        }


