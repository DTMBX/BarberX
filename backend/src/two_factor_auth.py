from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Two-Factor Authentication (2FA) Service
Implements TOTP-based 2FA with QR codes for enhanced security
"""

import base64
import io
from datetime import datetime

import pyotp
import qrcode


class TwoFactorAuthService:
    """
    Professional 2FA service using TOTP (Time-based One-Time Password)

    Features:
    - QR code generation for authenticator apps
    - Backup codes for account recovery
    - Session management
    - Support for Google Authenticator, Authy, Microsoft Authenticator
    """

    def __init__(self, issuer_name: str = "Evident Legal"):
        """
        Initialize 2FA service

        Args:
            issuer_name: Name shown in authenticator app
        """
        self.issuer_name = issuer_name

    def generate_secret(self) -> str:
        """
        Generate random secret key for user

        Returns:
            32-character base32 secret
        """
        return pyotp.random_base32()

    def get_provisioning_uri(self, secret: str, user_email: str) -> str:
        """
        Generate provisioning URI for QR code

        Args:
            secret: User's secret key
            user_email: User's email address

        Returns:
            otpauth:// URI string
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_email, issuer_name=self.issuer_name)

    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """
        Generate QR code image as base64 string

        Args:
            secret: User's secret key
            user_email: User's email address

        Returns:
            Base64-encoded PNG image
        """
        # Get provisioning URI
        uri = self.get_provisioning_uri(secret, user_email)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def verify_token(self, secret: str, token: str, valid_window: int = 1) -> bool:
        """
        Verify 6-digit TOTP token

        Args:
            secret: User's secret key
            token: 6-digit code from authenticator app
            valid_window: Number of time windows to check (1 = ±30s)

        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)

        # Verify token (allows for time drift)
        return totp.verify(token, valid_window=valid_window)

    def get_current_token(self, secret: str) -> str:
        """
        Get current 6-digit token (for testing)

        Args:
            secret: User's secret key

        Returns:
            Current 6-digit TOTP code
        """
        totp = pyotp.TOTP(secret)
        return totp.now()

    def generate_backup_codes(self, count: int = 10) -> list:
        """
        Generate backup codes for account recovery

        Args:
            count: Number of backup codes to generate

        Returns:
            List of 8-character backup codes
        """
        import secrets
        import string

        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Format as XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)

        return codes

    def setup_2fa_for_user(self, user_email: str) -> dict:
        """
        Complete 2FA setup for a user

        Args:
            user_email: User's email address

        Returns:
            {
                'secret': 'ABC123...',
                'qr_code': 'data:image/png;base64,...',
                'backup_codes': ['XXXX-XXXX', ...],
                'manual_entry_key': 'ABC1 2345 ...'
            }
        """
        # Generate secret
        secret = self.generate_secret()

        # Generate QR code
        qr_code = self.generate_qr_code(secret, user_email)

        # Generate backup codes
        backup_codes = self.generate_backup_codes()

        # Format secret for manual entry
        manual_key = " ".join([secret[i : i + 4] for i in range(0, len(secret), 4)])

        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "manual_entry_key": manual_key,
            "setup_date": datetime.now().isoformat(),
            "issuer": self.issuer_name,
        }

    def validate_backup_code(
        self, provided_code: str, valid_codes: list
Optional[) -> tuple[bool, str]]:
        """
        Validate backup code and return remaining code

        Args:
            provided_code: Code entered by user
            valid_codes: List of unused backup codes

        Returns:
            (is_valid, used_code)
        """
        # Normalize input
        normalized = provided_code.strip().upper().replace(" ", "").replace("-", "")

        # Check each valid code
        for code in valid_codes:
            normalized_valid = code.replace("-", "")
            if normalized == normalized_valid:
                return True, code

        return False, None


# Database models for 2FA (add to models_auth.py)
"""
class User2FA(db.Model):
    __tablename__ = 'user_2fa'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    secret = db.Column(db.String(32), nullable=False)  # Encrypted in production
    enabled = db.Column(db.Boolean, default=False)
    backup_codes = db.Column(db.JSON)  # List of unused backup codes (hashed)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='two_factor')


class User2FALog(db.Model):
    __tablename__ = 'user_2fa_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50))  # 'enabled', 'disabled', 'verified', 'failed'
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"""


# Example usage
if __name__ == "__main__":
    # Initialize 2FA service
    tfa = TwoFactorAuthService(issuer_name="Evident Legal Platform")

    print("=" * 80)
    print("TWO-FACTOR AUTHENTICATION SETUP")
    print("=" * 80)

    # Setup 2FA for user
    user_email = "john.doe@example.com"
    setup = tfa.setup_2fa_for_user(user_email)

    print(f"\nUser: {user_email}")
    print(f"Secret Key: {setup['secret']}")
    print(f"Manual Entry: {setup['manual_entry_key']}")
    print("\nQR Code (scan with authenticator app):")
    print("  [Base64 image - display in <img> tag]")
    print("\nBackup Codes (save these securely):")
    for i, code in enumerate(setup["backup_codes"], 1):
        print(f"  {i:2d}. {code}")

    # Simulate verification
    print("\n" + "=" * 80)
    print("VERIFICATION TEST")
    print("=" * 80)

    # Get current token (simulates user entering code from app)
    current_token = tfa.get_current_token(setup["secret"])
    print(f"\nCurrent Token: {current_token}")

    # Verify token
    is_valid = tfa.verify_token(setup["secret"], current_token)
    print(f"Token Valid: {is_valid}")

    # Test backup code
    print("\n" + "=" * 80)
    print("BACKUP CODE TEST")
    print("=" * 80)

    backup_code = setup["backup_codes"][0]
    print(f"\nTesting backup code: {backup_code}")

    is_valid, used_code = tfa.validate_backup_code(backup_code, setup["backup_codes"])
    print(f"Backup Code Valid: {is_valid}")

    if is_valid:
        print(f"Used Code: {used_code}")
        print("Note: Remove this code from valid codes list")

    print("\n" + "=" * 80)
    print("✓ 2FA Service Ready!")
    print("  Install: pip install pyotp qrcode[pil]")
    print("=" * 80)