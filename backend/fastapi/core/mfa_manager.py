"""
Multi-Factor Authentication Framework
Implements TOTP and backup codes for enhanced security
"""

import base64
import hashlib
import io
import secrets
import time
from typing import Any, Dict, List, Optional, Tuple

import qrcode


class MultiFactorAuthManager:
    def __init__(self):
        self.backup_codes_count = 8
        self.totp_window = 1  # Accept tokens from 1 period before/after
        self.totp_period = 30  # 30 seconds

    def generate_secret_key(self) -> str:
        """Generate TOTP secret key"""
        return base64.b32encode(secrets.token_bytes(20)).decode("utf-8")

    def generate_qr_code(
        self, secret: str, username: str, issuer: str = "NoxSuite"
    ) -> bytes:
        """Generate QR code for TOTP setup"""
        totp_uri = f"otpauth://totp/{issuer}:{username}?secret={secret}&issuer={issuer}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def verify_totp_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token with time window"""
        current_time = int(time.time()) // self.totp_period

        # Check current time and surrounding windows
        for time_window in range(-self.totp_window, self.totp_window + 1):
            if self._generate_totp_token(secret, current_time + time_window) == token:
                return True

        return False

    def _generate_totp_token(self, secret: str, time_counter: int) -> str:
        """Generate TOTP token for given time counter"""
        import hmac

        # Convert secret from base32
        key = base64.b32decode(secret)

        # Convert time counter to bytes
        time_bytes = time_counter.to_bytes(8, byteorder="big")

        # Generate HMAC
        hmac_digest = hmac.new(key, time_bytes, hashlib.sha1).digest()

        # Extract dynamic binary code
        offset = hmac_digest[-1] & 0xF
        code = (
            (hmac_digest[offset] & 0x7F) << 24
            | (hmac_digest[offset + 1] & 0xFF) << 16
            | (hmac_digest[offset + 2] & 0xFF) << 8
            | (hmac_digest[offset + 3] & 0xFF)
        )

        # Generate 6-digit code
        return str(code % 1000000).zfill(6)

    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(self.backup_codes_count):
            # Generate 8-character alphanumeric codes
            code = "".join(
                secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8)
            )
            codes.append(f"{code[:4]}-{code[4:]}")  # Format: XXXX-XXXX

        return codes

    def hash_backup_codes(self, codes: List[str]) -> List[str]:
        """Hash backup codes for secure storage"""
        hashed_codes = []
        for code in codes:
            # Remove hyphen and hash
            clean_code = code.replace("-", "")
            hashed = hashlib.sha256(clean_code.encode()).hexdigest()
            hashed_codes.append(hashed)

        return hashed_codes

    def verify_backup_code(
        self, provided_code: str, stored_hashes: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """Verify backup code and return the hash if valid"""
        clean_code = provided_code.replace("-", "").upper()
        provided_hash = hashlib.sha256(clean_code.encode()).hexdigest()

        if provided_hash in stored_hashes:
            return True, provided_hash

        return False, None

    def setup_mfa_for_user(self, user_id: str) -> Dict[str, Any]:
        """Complete MFA setup for user"""
        secret = self.generate_secret_key()
        backup_codes = self.generate_backup_codes()
        hashed_backup_codes = self.hash_backup_codes(backup_codes)

        return {
            "user_id": user_id,
            "totp_secret": secret,
            "backup_codes": backup_codes,  # Show once to user
            "backup_codes_hashed": hashed_backup_codes,  # Store in database
            "setup_complete": False,
            "created_at": time.time(),
        }

    def validate_mfa_token(
        self, secret: str, token: str, backup_codes: List[str] = None
    ) -> Dict[str, Any]:
        """Validate MFA token (TOTP or backup code)"""
        # Try TOTP first
        if self.verify_totp_token(secret, token):
            return {"valid": True, "method": "totp", "backup_code_used": None}

        # Try backup codes if provided
        if backup_codes:
            is_valid, used_hash = self.verify_backup_code(token, backup_codes)
            if is_valid:
                return {
                    "valid": True,
                    "method": "backup_code",
                    "backup_code_used": used_hash,
                }

        return {"valid": False, "method": None, "backup_code_used": None}
