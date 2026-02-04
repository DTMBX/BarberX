"""
License Validation API Routes
Endpoints for self-hosted instances to validate licenses
"""

import hashlib
import platform
import socket

from flask import Blueprint, jsonify, request

from .models_license import License, LicenseService, LicenseValidation

license_bp = Blueprint("license", __name__, url_prefix="/api/v1/license")


def get_machine_fingerprint(provided_data=None):
    """
    Generate a unique machine fingerprint
    Can use provided data from client or generate server-side
    """
    if provided_data:
        # Client provided their fingerprint
        components = [
            provided_data.get("hostname", ""),
            provided_data.get("mac_address", ""),
            provided_data.get("machine_id", ""),
        ]
    else:
        # Generate server-side (for testing)
        components = [
            platform.node(),
            socket.gethostname(),
            str(socket.gethostbyname(socket.gethostname())),
        ]

    fingerprint_str = "|".join(str(c) for c in components if c)
    return hashlib.sha256(fingerprint_str.encode()).hexdigest()


@license_bp.route("/validate", methods=["POST"])
def validate_license():
    """
    Validate a license key

    Request body:
    {
        "license_key": "BX-XXXX-XXXX-XXXX-XXXX",
        "machine_id": "abc123...",
        "machine_info": {
            "hostname": "server01",
            "os": "Ubuntu 22.04",
            "version": "2.1.0"
        },
        "usage_stats": {
            "videos_processed": 127,
            "active_users": 8,
            "storage_used_gb": 45.3
        }
    }

    Response:
    {
        "valid": true,
        "license": {...},
        "machine_registered": true,
        "grace_period_hours": 72
    }
    """
    data = request.get_json()

    if not data or "license_key" not in data or "machine_id" not in data:
        return (
            jsonify({"valid": False, "error": "Missing required fields: license_key, machine_id"}),
            400,
        )

    license_key = data["license_key"]
    machine_id = data["machine_id"]
    machine_info = data.get("machine_info")
    usage_stats = data.get("usage_stats")

    # Validate license
    result = LicenseService.validate_license(
        license_key=license_key,
        machine_id=machine_id,
        machine_info=machine_info,
        usage_stats=usage_stats,
    )

    # Return appropriate status code
    if result["valid"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 403


@license_bp.route("/info/<license_key>", methods=["GET"])
def get_license_info(license_key):
    """
    Get license information (without validation)
    Requires admin authentication in production
    """
    # TODO: Add admin authentication check

    license = License.query.filter_by(license_key=license_key).first()

    if not license:
        return jsonify({"error": "License not found"}), 404

    return jsonify(license.to_dict()), 200


@license_bp.route("/usage/<license_key>", methods=["GET"])
def get_license_usage(license_key):
    """
    Get usage statistics for a license
    Requires admin authentication in production
    """
    # TODO: Add admin authentication check

    try:
        stats = LicenseService.get_usage_stats(license_key)
        return jsonify(stats), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@license_bp.route("/create", methods=["POST"])
def create_license():
    """
    Create a new license
    Requires admin authentication

    Request body:
    {
        "organization_name": "ACME Law Firm",
        "contact_email": "admin@acme.com",
        "contact_name": "John Smith",
        "tier": "ENTERPRISE",
        "duration_days": 365,
        "max_machines": 2,
        "max_users": 50,
        "monthly_video_quota": 1000,
        "features": {
            "white_label": true,
            "api_access": true
        }
    }
    """
    # TODO: Add admin authentication check
    # from auth_routes import admin_required
    # @admin_required

    data = request.get_json()

    required_fields = ["organization_name", "contact_email"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        license = LicenseService.create_license(
            organization_name=data["organization_name"],
            contact_email=data["contact_email"],
            contact_name=data.get("contact_name"),
            tier=data.get("tier", "ENTERPRISE"),
            duration_days=data.get("duration_days", 365),
            max_machines=data.get("max_machines", 1),
            max_users=data.get("max_users", 10),
            monthly_video_quota=data.get("monthly_video_quota", 500),
            features=data.get("features"),
            notes=data.get("notes"),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "license": license.to_dict(),
                    "message": f"License created successfully: {license.license_key}",
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@license_bp.route("/renew/<license_key>", methods=["POST"])
def renew_license(license_key):
    """
    Renew a license
    Requires admin authentication

    Request body:
    {
        "duration_days": 365
    }
    """
    # TODO: Add admin authentication check

    data = request.get_json() or {}
    duration_days = data.get("duration_days", 365)

    try:
        license = LicenseService.renew_license(license_key, duration_days)

        return (
            jsonify(
                {
                    "success": True,
                    "license": license.to_dict(),
                    "message": f"License renewed until {license.expires_at.isoformat()}",
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@license_bp.route("/suspend/<license_key>", methods=["POST"])
def suspend_license(license_key):
    """
    Suspend a license
    Requires admin authentication

    Request body:
    {
        "reason": "Payment failed"
    }
    """
    # TODO: Add admin authentication check

    data = request.get_json() or {}
    reason = data.get("reason")

    try:
        license = LicenseService.suspend_license(license_key, reason)

        return (
            jsonify(
                {"success": True, "license": license.to_dict(), "message": "License suspended"}
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Health check endpoint (no auth required)
@license_bp.route("/health", methods=["GET"])
def health_check():
    """Health check for license service"""
    return jsonify({"status": "healthy", "service": "license-validation", "version": "1.0.0"}), 200


