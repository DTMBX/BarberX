"""
License Client - For Self-Hosted Deployments
Include this in the self-hosted version to validate licenses
"""

import hashlib
import json
import os
import platform
import socket
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import requests


class LicenseClient:
    """
    Client for validating licenses in self-hosted deployments

    Usage:
        license = LicenseClient()
        if license.is_valid():
            # Continue operation
        else:
            # Show error and exit
    """

    def __init__(self, license_key=None, validation_url=None):
        """
        Initialize license client

        Args:
            license_key: License key (or use Evident_LICENSE_KEY env var)
            validation_url: License validation server URL
        """
        self.license_key = license_key or os.getenv("Evident_LICENSE_KEY")
        self.validation_url = validation_url or os.getenv(
            "Evident_LICENSE_SERVER", "https://license.Evident.info/api/v1/license/validate"
        )

        self.cache_dir = Path.home() / ".Evident" / "license"
        self.cache_file = self.cache_dir / "license_cache.json"
        self.grace_period_hours = 72  # Can run offline for 3 days

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load cached validation
        self._cached_validation = self._load_cache()

    def get_machine_id(self):
        """Generate unique machine fingerprint"""
        try:
            # Gather machine-specific identifiers
            hostname = platform.node()
            mac_address = ":".join(
                [
                    "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
                    for elements in range(0, 2 * 6, 2)
                ][::-1]
            )

            # Combine and hash
            components = [
                hostname,
                mac_address,
                platform.system(),
                platform.machine(),
            ]

            fingerprint_str = "|".join(components)
            return hashlib.sha256(fingerprint_str.encode()).hexdigest()

        except Exception as e:
            # Fallback to basic UUID
            return str(uuid.uuid4())

    def get_machine_info(self):
        """Get machine information for validation"""
        return {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "version": os.getenv("Evident_VERSION", "unknown"),
            "python": platform.python_version(),
        }

    def validate_online(self, usage_stats=None):
        """
        Validate license with online server

        Args:
            usage_stats: Optional usage statistics to report

        Returns:
            dict: Validation response or error
        """
        if not self.license_key:
            return {"valid": False, "error": "No license key configured", "code": "NO_LICENSE"}

        try:
            machine_id = self.get_machine_id()
            machine_info = self.get_machine_info()

            response = requests.post(
                self.validation_url,
                json={
                    "license_key": self.license_key,
                    "machine_id": machine_id,
                    "machine_info": machine_info,
                    "usage_stats": usage_stats or {},
                },
                timeout=10,
                headers={"User-Agent": "Evident-SelfHosted/1.0"},
            )

            result = response.json()

            # Cache successful validation
            if result.get("valid"):
                self._save_cache(result)

            return result

        except requests.RequestException as e:
            # Network error - check cache and grace period
            return self._handle_offline_validation()

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "code": "VALIDATION_ERROR",
            }

    def _handle_offline_validation(self):
        """Handle validation when offline"""
        if not self._cached_validation:
            return {
                "valid": False,
                "error": "Cannot validate license - no internet connection and no cached validation",
                "code": "OFFLINE_NO_CACHE",
            }

        # Check if within grace period
        cached_at = datetime.fromisoformat(self._cached_validation.get("cached_at"))
        hours_since_validation = (datetime.utcnow() - cached_at).total_seconds() / 3600

        if hours_since_validation < self.grace_period_hours:
            # Still within grace period
            return {
                "valid": True,
                "offline": True,
                "grace_period_remaining_hours": self.grace_period_hours - hours_since_validation,
                "license": self._cached_validation.get("license"),
                "message": "Running on cached license validation (offline mode)",
            }
        else:
            # Grace period expired
            return {
                "valid": False,
                "error": f"License validation required - offline for {hours_since_validation:.1f} hours (grace period: {self.grace_period_hours}h)",
                "code": "GRACE_PERIOD_EXPIRED",
            }

    def _save_cache(self, validation_result):
        """Save validation result to cache"""
        cache_data = {
            "validation": validation_result,
            "cached_at": datetime.utcnow().isoformat(),
        }

        try:
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

            self._cached_validation = cache_data
        except Exception as e:
            # Non-critical - continue without caching
            pass

    def _load_cache(self):
        """Load cached validation"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass

        return None

    def is_valid(self, usage_stats=None):
        """
        Check if license is valid

        Args:
            usage_stats: Optional usage statistics to report

        Returns:
            bool: True if license is valid
        """
        result = self.validate_online(usage_stats)

        if result.get("valid"):
            return True

        # Print error message
        error_msg = result.get("error", "Unknown error")
        code = result.get("code", "UNKNOWN")

        print(f"\n{'='*60}")
        print(f"LICENSE VALIDATION FAILED")
        print(f"{'='*60}")
        print(f"Error: {error_msg}")
        print(f"Code: {code}")

        if code == "NO_LICENSE":
            print(f"\nPlease set your license key:")
            print(f"  export Evident_LICENSE_KEY='BX-XXXX-XXXX-XXXX-XXXX'")
        elif code in ["LICENSE_INACTIVE", "LICENSE_EXPIRED"]:
            print(f"\nYour license has expired or been suspended.")
            print(f"Please contact enterprise@Evident.info to renew.")
        elif code == "MACHINE_LIMIT":
            print(f"\nLicense is installed on maximum allowed machines.")
            print(f"Please contact enterprise@Evident.info to add more servers.")
        elif code == "GRACE_PERIOD_EXPIRED":
            print(f"\nPlease connect to internet to validate license.")

        print(f"\nFor support: enterprise@Evident.info")
        print(f"{'='*60}\n")

        return False

    def get_license_info(self):
        """Get license information"""
        result = self.validate_online()

        if result.get("valid"):
            return result.get("license", {})

        return None

    def check_feature(self, feature_name):
        """Check if a feature is enabled in the license"""
        license_info = self.get_license_info()

        if not license_info:
            return False

        features = license_info.get("features", {})
        return features.get(feature_name, False)


# Singleton instance
_license_client = None


def get_license_client():
    """Get global license client instance"""
    global _license_client

    if _license_client is None:
        _license_client = LicenseClient()

    return _license_client


def require_valid_license():
    """
    Decorator to require valid license

    Usage:
        @require_valid_license()
        def protected_function():
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            license_client = get_license_client()

            if not license_client.is_valid():
                raise PermissionError("Valid license required")

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Flask middleware for license checking
def license_check_middleware(app):
    """
    Add license checking middleware to Flask app

    Usage:
        from license_client import license_check_middleware
        license_check_middleware(app)
    """

    @app.before_request
    def check_license():
        """Check license before each request"""
        # Skip health check endpoint
        if request.path == "/health" or request.path.startswith("/static"):
            return None

        license_client = get_license_client()

        if not license_client.is_valid():
            return (
                jsonify(
                    {
                        "error": "License validation failed",
                        "message": "Please contact enterprise@Evident.info",
                        "contact": "enterprise@Evident.info",
                    }
                ),
                403,
            )


if __name__ == "__main__":
    """Test license validation"""
    print("Testing license validation...")
    print()

    # Test with environment variable
    license_client = LicenseClient()

    print(f"License Key: {license_client.license_key}")
    print(f"Machine ID: {license_client.get_machine_id()}")
    print()

    if license_client.is_valid():
        print("✅ License is VALID")

        license_info = license_client.get_license_info()
        if license_info:
            print(f"\nOrganization: {license_info.get('organization')}")
            print(f"Tier: {license_info.get('tier')}")
            print(f"Expires: {license_info.get('expires_at')}")
            print(f"Max Machines: {license_info.get('max_machines')}")
            print(f"Monthly Quota: {license_info.get('monthly_video_quota')}")
    else:
        print("❌ License validation FAILED")


