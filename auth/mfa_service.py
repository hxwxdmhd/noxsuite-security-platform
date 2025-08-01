"""
Multi-Factor Authentication (MFA) Service for NoxSuite
Implements TOTP-based MFA with backup codes and management
"""

import base64
import hmac
import hashlib
import time
import secrets
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

class TOTPService:
    """Time-based One-Time Password (TOTP) Implementation"""
    
    def __init__(self, secret_key: Optional[str] = None, digits: int = 6, period: int = 30, algorithm: str = 'sha1'):
        """
        Initialize TOTP service
        
        Args:
            secret_key: Base32 encoded secret key (generated if None)
            digits: Number of digits in the TOTP code (default: 6)
            period: TOTP refresh period in seconds (default: 30)
            algorithm: Hash algorithm (default: sha1)
        """
        self.secret_key = secret_key or self._generate_secret()
        self.digits = digits
        self.period = period
        self.algorithm = algorithm
    
    def _generate_secret(self, length: int = 32) -> str:
        """Generate a secure random secret key"""
        # Use cryptographically secure random bytes
        random_bytes = secrets.token_bytes(length)
        # Convert to base32 encoding (standard for TOTP)
        return base64.b32encode(random_bytes).decode('utf-8')
    
    def generate_totp(self, timestamp: Optional[int] = None) -> str:
        """
        Generate TOTP code for the current time
        
        Args:
            timestamp: Optional specific timestamp (default: current time)
        
        Returns:
            TOTP code as string
        """
        # Get current timestamp if not provided
        if timestamp is None:
            timestamp = int(time.time())
        
        # Calculate the time counter (floor division by period)
        counter = timestamp // self.period
        
        # Convert counter to bytes (8 bytes, big-endian)
        counter_bytes = counter.to_bytes(8, byteorder='big')
        
        # Decode base32 secret
        key = base64.b32decode(self.secret_key)
        
        # Generate HMAC
        if self.algorithm == 'sha1':
            hash_obj = hmac.new(key, counter_bytes, hashlib.sha1)
        elif self.algorithm == 'sha256':
            hash_obj = hmac.new(key, counter_bytes, hashlib.sha256)
        elif self.algorithm == 'sha512':
            hash_obj = hmac.new(key, counter_bytes, hashlib.sha512)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        # Get the hash digest
        hmac_digest = hash_obj.digest()
        
        # Dynamic truncation
        offset = hmac_digest[-1] & 0x0F
        
        # Take 4 bytes from the digest starting at offset
        truncated_hash = hmac_digest[offset:offset+4]
        
        # Convert to an integer
        code = int.from_bytes(truncated_hash, byteorder='big')
        
        # Apply a mask to get only the last 31 bits
        code = code & 0x7FFFFFFF
        
        # Modulo to get the specified number of digits
        code = code % (10 ** self.digits)
        
        # Format as a zero-padded string
        return str(code).zfill(self.digits)
    
    def verify_totp(self, code: str, timestamp: Optional[int] = None, window: int = 1) -> bool:
        """
        Verify TOTP code
        
        Args:
            code: TOTP code to verify
            timestamp: Optional specific timestamp (default: current time)
            window: Time window in periods to allow (default: 1 period before/after)
        
        Returns:
            True if code is valid, False otherwise
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        # Check codes in the time window
        for i in range(-window, window + 1):
            check_time = timestamp + (i * self.period)
            if self.generate_totp(check_time) == code:
                return True
        
        return False
    
    def get_provisioning_uri(self, account_name: str, issuer: str = "NoxSuite") -> str:
        """
        Generate TOTP provisioning URI for QR codes
        
        Args:
            account_name: User account name/email
            issuer: Service issuer name
        
        Returns:
            otpauth URI for QR code generation
        """
        import urllib.parse
        
        # URL encode parameters
        issuer_encoded = urllib.parse.quote(issuer)
        account_encoded = urllib.parse.quote(account_name)
        
        # Construct the URI
        uri = (f"otpauth://totp/{issuer_encoded}:{account_encoded}?"
               f"secret={self.secret_key}&issuer={issuer_encoded}"
               f"&algorithm={self.algorithm.upper()}&digits={self.digits}"
               f"&period={self.period}")
        
        return uri

class MFAService:
    """MFA Service with TOTP and backup codes"""
    
    def __init__(self, totp_service: Optional[TOTPService] = None):
        """
        Initialize MFA Service
        
        Args:
            totp_service: Optional TOTP service instance
        """
        self.totp_service = totp_service or TOTPService()
    
    def generate_backup_codes(self, count: int = 10, length: int = 8) -> List[str]:
        """
        Generate backup codes for MFA recovery
        
        Args:
            count: Number of backup codes to generate (default: 10)
            length: Length of each backup code (default: 8)
        
        Returns:
            List of backup codes
        """
        backup_codes = []
        for _ in range(count):
            # Generate random code with specified length
            code = ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(length))
            # Add hyphens for better readability (e.g., XXXX-XXXX)
            if length >= 8:
                code = f"{code[:length//2]}-{code[length//2:]}"
            backup_codes.append(code)
        
        return backup_codes
    
    def hash_backup_codes(self, backup_codes: List[str]) -> List[str]:
        """
        Hash backup codes for secure storage
        
        Args:
            backup_codes: List of backup codes
        
        Returns:
            List of hashed backup codes
        """
        return [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes]
    
    def verify_backup_code(self, code: str, hashed_codes: List[str]) -> bool:
        """
        Verify a backup code against a list of hashed codes
        
        Args:
            code: Backup code to verify
            hashed_codes: List of hashed backup codes
        
        Returns:
            True if code is valid, False otherwise
        """
        # Hash the input code
        hashed_input = hashlib.sha256(code.encode()).hexdigest()
        
        # Check if the hashed input matches any of the stored hashed codes
        return hashed_input in hashed_codes
    
    def setup_mfa_for_user(self, user_id: str) -> Dict:
        """
        Set up MFA for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with MFA setup information
        """
        # Create new TOTP service for the user
        totp_service = TOTPService()
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        hashed_backup_codes = self.hash_backup_codes(backup_codes)
        
        # Return setup information
        return {
            "user_id": user_id,
            "totp_secret": totp_service.secret_key,
            "totp_algorithm": totp_service.algorithm,
            "totp_digits": totp_service.digits,
            "totp_period": totp_service.period,
            "backup_codes": backup_codes,
            "hashed_backup_codes": hashed_backup_codes,
            "provisioning_uri": totp_service.get_provisioning_uri(user_id, "NoxSuite"),
            "setup_date": datetime.utcnow().isoformat()
        }
    
    def verify_mfa(self, 
                  totp_code: Optional[str], 
                  backup_code: Optional[str], 
                  totp_secret: str,
                  hashed_backup_codes: List[str],
                  totp_algorithm: str = 'sha1',
                  totp_digits: int = 6,
                  totp_period: int = 30) -> Tuple[bool, str]:
        """
        Verify MFA using either TOTP or backup code
        
        Args:
            totp_code: TOTP code (can be None if using backup code)
            backup_code: Backup code (can be None if using TOTP)
            totp_secret: User's TOTP secret key
            hashed_backup_codes: User's hashed backup codes
            totp_algorithm: TOTP algorithm
            totp_digits: TOTP digits
            totp_period: TOTP period
        
        Returns:
            Tuple of (success, auth_method)
        """
        # Check if TOTP code is provided
        if totp_code:
            # Create TOTP service with user's parameters
            totp_service = TOTPService(
                secret_key=totp_secret,
                algorithm=totp_algorithm,
                digits=totp_digits,
                period=totp_period
            )
            
            # Verify TOTP code
            if totp_service.verify_totp(totp_code):
                return True, "totp"
        
        # Check if backup code is provided
        if backup_code:
            # Verify backup code
            if self.verify_backup_code(backup_code, hashed_backup_codes):
                return True, "backup_code"
        
        # Neither TOTP nor backup code is valid
        return False, "invalid"

# Example usage:
if __name__ == "__main__":
    # Create MFA service
    mfa_service = MFAService()
    
    # Set up MFA for a user
    mfa_setup = mfa_service.setup_mfa_for_user("test_user@example.com")
    
    # Print setup information
    print(f"TOTP Secret: {mfa_setup['totp_secret']}")
    print(f"Provisioning URI: {mfa_setup['provisioning_uri']}")
    print("Backup Codes:")
    for code in mfa_setup['backup_codes']:
        print(f"  {code}")
    
    # Generate current TOTP code
    totp_service = TOTPService(secret_key=mfa_setup['totp_secret'])
    current_code = totp_service.generate_totp()
    print(f"\nCurrent TOTP Code: {current_code}")
    
    # Verify the code
    is_valid = totp_service.verify_totp(current_code)
    print(f"TOTP Code Valid: {is_valid}")
    
    # Verify with MFA service
    success, method = mfa_service.verify_mfa(
        totp_code=current_code,
        backup_code=None,
        totp_secret=mfa_setup['totp_secret'],
        hashed_backup_codes=mfa_setup['hashed_backup_codes']
    )
    print(f"MFA Verification: {success} (method: {method})")
    
    # Verify with backup code
    backup_code = mfa_setup['backup_codes'][0]
    success, method = mfa_service.verify_mfa(
        totp_code=None,
        backup_code=backup_code,
        totp_secret=mfa_setup['totp_secret'],
        hashed_backup_codes=mfa_setup['hashed_backup_codes']
    )
    print(f"Backup Code Verification: {success} (method: {method})")
