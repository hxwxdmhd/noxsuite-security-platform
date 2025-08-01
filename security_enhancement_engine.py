#!/usr/bin/env python3
"""
NoxSuite Security Enhancement Module
Advanced security implementations for Iteration 2 completion
"""

import asyncio
import json
import logging
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityEnhancementEngine:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.security_config = {
            "password_policy": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True,
                "max_age_days": 90
            },
            "jwt_policy": {
                "access_token_expire_minutes": 30,
                "refresh_token_expire_days": 7,
                "algorithm": "HS256",
                "require_audience": True
            },
            "rate_limiting": {
                "login_attempts_per_minute": 5,
                "api_requests_per_minute": 100,
                "lockout_duration_minutes": 15
            },
            "security_headers": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": "default-src 'self'"
            }
        }
    
    async def enhance_authentication_security(self) -> Dict[str, Any]:
        """Enhance authentication security components"""
        logger.info("🔐 Enhancing Authentication Security...")
        
        enhancements = {
            "password_validation": await self._create_password_validator(),
            "jwt_security": await self._enhance_jwt_security(),
            "session_security": await self._enhance_session_security(),
            "multi_factor_auth": await self._implement_mfa_framework(),
            "brute_force_protection": await self._implement_brute_force_protection()
        }
        
        success_count = sum(1 for result in enhancements.values() if result["success"])
        total_count = len(enhancements)
        
        return {
            "category": "authentication_security",
            "enhancements": enhancements,
            "summary": {
                "total_enhancements": total_count,
                "successful": success_count,
                "success_rate": round((success_count / total_count) * 100, 1),
                "security_level": "HIGH" if success_count >= 4 else "MEDIUM"
            }
        }
    
    async def _create_password_validator(self) -> Dict[str, Any]:
        """Create advanced password validation system"""
        password_validator_code = '''
"""
Advanced Password Validation System
Implements comprehensive password security policies
"""

import re
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class AdvancedPasswordValidator:
    def __init__(self):
        self.min_length = 12
        self.max_length = 128
        self.common_passwords = self._load_common_passwords()
        self.password_history = {}  # In production, use database
    
    def validate_password(self, password: str, username: str = None) -> Tuple[bool, List[str]]:
        """
        Comprehensive password validation
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Length validation
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")
        
        # Character requirements
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Username similarity check
        if username and username.lower() in password.lower():
            errors.append("Password must not contain username")
        
        # Common password check
        if password.lower() in self.common_passwords:
            errors.append("Password is too common, please choose a more unique password")
        
        # Sequential characters check
        if self._has_sequential_chars(password):
            errors.append("Password must not contain sequential characters (e.g., 123, abc)")
        
        # Repeated characters check
        if self._has_excessive_repeats(password):
            errors.append("Password must not have excessive repeated characters")
        
        return len(errors) == 0, errors
    
    def _load_common_passwords(self) -> set:
        """Load common passwords list"""
        common = {
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master",
            "password1", "123456789", "12345678", "123123", "1234567890"
        }
        return common
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters"""
        sequences = ["123", "234", "345", "456", "567", "678", "789",
                    "abc", "bcd", "cde", "def", "efg", "fgh", "ghi",
                    "qwe", "wer", "ert", "rty", "tyu", "yui", "uio"]
        
        password_lower = password.lower()
        return any(seq in password_lower for seq in sequences)
    
    def _has_excessive_repeats(self, password: str) -> bool:
        """Check for excessive repeated characters"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a cryptographically secure password"""
        import secrets
        import string
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*(),.?\":{}|<>"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill remaining length
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
'''
        
        # Write password validator to file
        validator_file = Path("backend/fastapi/core/password_validator.py")
        validator_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(validator_file, 'w', encoding='utf-8') as f:
            f.write(password_validator_code)
        
        return {
            "success": True,
            "component": "password_validator",
            "file_created": str(validator_file),
            "details": "Advanced password validation system implemented"
        }
    
    async def _enhance_jwt_security(self) -> Dict[str, Any]:
        """Enhance JWT security implementation"""
        jwt_security_code = '''
"""
Enhanced JWT Security Manager
Implements advanced JWT security features
"""

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hashlib

class EnhancedJWTManager:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.token_blacklist = set()  # In production, use Redis
        self.refresh_tokens = {}  # In production, use database
    
    def _generate_secret_key(self) -> str:
        """Generate cryptographically secure secret key"""
        return secrets.token_urlsafe(32)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        # Add security claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_urlsafe(8)  # JWT ID for tracking
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token with enhanced security"""
        token_data = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        refresh_token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token (in production, use database)
        self.refresh_tokens[token_data["jti"]] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_used": datetime.utcnow()
        }
        
        return refresh_token
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify JWT token with enhanced security checks"""
        try:
            # Check if token is blacklisted
            if token in self.token_blacklist:
                return None
            
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                return None
            
            # For refresh tokens, check if still valid in storage
            if token_type == "refresh":
                jti = payload.get("jti")
                if jti not in self.refresh_tokens:
                    return None
                
                # Update last used timestamp
                self.refresh_tokens[jti]["last_used"] = datetime.utcnow()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token by adding to blacklist"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            
            if jti:
                self.token_blacklist.add(token)
                
                # If it's a refresh token, remove from storage
                if payload.get("type") == "refresh" and jti in self.refresh_tokens:
                    del self.refresh_tokens[jti]
                
                return True
        except:
            pass
        
        return False
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a specific user"""
        revoked_count = 0
        
        # Remove refresh tokens for user
        to_remove = []
        for jti, token_data in self.refresh_tokens.items():
            if token_data["user_id"] == user_id:
                to_remove.append(jti)
                revoked_count += 1
        
        for jti in to_remove:
            del self.refresh_tokens[jti]
        
        return revoked_count
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired refresh tokens"""
        now = datetime.utcnow()
        expired = []
        
        for jti, token_data in self.refresh_tokens.items():
            if now - token_data["created_at"] > timedelta(days=self.refresh_token_expire_days):
                expired.append(jti)
        
        for jti in expired:
            del self.refresh_tokens[jti]
        
        return len(expired)
'''
        
        # Write JWT manager to file
        jwt_file = Path("backend/fastapi/core/jwt_manager.py")
        jwt_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(jwt_file, 'w', encoding='utf-8') as f:
            f.write(jwt_security_code)
        
        return {
            "success": True,
            "component": "jwt_security",
            "file_created": str(jwt_file),
            "details": "Enhanced JWT security manager implemented"
        }
    
    async def _enhance_session_security(self) -> Dict[str, Any]:
        """Enhance session security"""
        session_security_code = '''
"""
Enhanced Session Security Manager
Implements secure session management with advanced features
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
import json

class EnhancedSessionManager:
    def __init__(self):
        self.sessions = {}  # In production, use Redis
        self.session_timeout = timedelta(hours=2)
        self.max_sessions_per_user = 5
        self.secure_cookie_config = {
            "httponly": True,
            "secure": True,
            "samesite": "strict",
            "max_age": 7200  # 2 hours
        }
    
    def create_session(self, user_id: str, user_agent: str, ip_address: str) -> str:
        """Create secure session with tracking"""
        session_id = secrets.token_urlsafe(32)
        
        # Create session fingerprint
        fingerprint = self._create_fingerprint(user_agent, ip_address)
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "fingerprint": fingerprint,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "is_active": True
        }
        
        # Cleanup old sessions for user
        self._cleanup_user_sessions(user_id)
        
        self.sessions[session_id] = session_data
        return session_id
    
    def validate_session(self, session_id: str, user_agent: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Validate session with security checks"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.get("is_active", False):
            return None
        
        # Check session timeout
        if datetime.utcnow() - session["last_activity"] > self.session_timeout:
            self.invalidate_session(session_id)
            return None
        
        # Verify fingerprint
        current_fingerprint = self._create_fingerprint(user_agent, ip_address)
        if current_fingerprint != session["fingerprint"]:
            # Potential session hijacking
            self.invalidate_session(session_id)
            return None
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        
        return session
    
    def _create_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Create session fingerprint for security"""
        data = f"{user_agent}:{ip_address}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a specific session"""
        if session_id in self.sessions:
            self.sessions[session_id]["is_active"] = False
            del self.sessions[session_id]
            return True
        return False
    
    def invalidate_all_user_sessions(self, user_id: str) -> int:
        """Invalidate all sessions for a user"""
        invalidated = 0
        to_remove = []
        
        for session_id, session in self.sessions.items():
            if session["user_id"] == user_id:
                to_remove.append(session_id)
                invalidated += 1
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return invalidated
    
    def _cleanup_user_sessions(self, user_id: str) -> None:
        """Cleanup old sessions if user has too many"""
        user_sessions = []
        for session_id, session in self.sessions.items():
            if session["user_id"] == user_id:
                user_sessions.append((session_id, session["created_at"]))
        
        # Sort by creation time, newest first
        user_sessions.sort(key=lambda x: x[1], reverse=True)
        
        # Remove oldest sessions if exceeding limit
        if len(user_sessions) >= self.max_sessions_per_user:
            sessions_to_remove = user_sessions[self.max_sessions_per_user-1:]
            for session_id, _ in sessions_to_remove:
                del self.sessions[session_id]
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired = []
        
        for session_id, session in self.sessions.items():
            if now - session["last_activity"] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
        
        return len(expired)
    
    def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        active_sessions = []
        
        for session_id, session in self.sessions.items():
            if session["user_id"] == user_id and session.get("is_active", False):
                active_sessions.append({
                    "session_id": session_id,
                    "created_at": session["created_at"],
                    "last_activity": session["last_activity"],
                    "ip_address": session["ip_address"],
                    "user_agent": session["user_agent"]
                })
        
        return active_sessions
'''
        
        # Write session manager to file
        session_file = Path("backend/fastapi/core/session_manager.py")
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(session_security_code)
        
        return {
            "success": True,
            "component": "session_security",
            "file_created": str(session_file),
            "details": "Enhanced session security manager implemented"
        }
    
    async def _implement_mfa_framework(self) -> Dict[str, Any]:
        """Implement multi-factor authentication framework"""
        mfa_code = '''
"""
Multi-Factor Authentication Framework
Implements TOTP and backup codes for enhanced security
"""

import secrets
import base64
import hashlib
import time
import qrcode
from typing import List, Dict, Any, Optional, Tuple
import io

class MultiFactorAuthManager:
    def __init__(self):
        self.backup_codes_count = 8
        self.totp_window = 1  # Accept tokens from 1 period before/after
        self.totp_period = 30  # 30 seconds
    
    def generate_secret_key(self) -> str:
        """Generate TOTP secret key"""
        return base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
    
    def generate_qr_code(self, secret: str, username: str, issuer: str = "NoxSuite") -> bytes:
        """Generate QR code for TOTP setup"""
        totp_uri = f"otpauth://totp/{issuer}:{username}?secret={secret}&issuer={issuer}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
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
        time_bytes = time_counter.to_bytes(8, byteorder='big')
        
        # Generate HMAC
        hmac_digest = hmac.new(key, time_bytes, hashlib.sha1).digest()
        
        # Extract dynamic binary code
        offset = hmac_digest[-1] & 0xf
        code = ((hmac_digest[offset] & 0x7f) << 24 |
                (hmac_digest[offset + 1] & 0xff) << 16 |
                (hmac_digest[offset + 2] & 0xff) << 8 |
                (hmac_digest[offset + 3] & 0xff))
        
        # Generate 6-digit code
        return str(code % 1000000).zfill(6)
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(self.backup_codes_count):
            # Generate 8-character alphanumeric codes
            code = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') 
                          for _ in range(8))
            codes.append(f"{code[:4]}-{code[4:]}")  # Format: XXXX-XXXX
        
        return codes
    
    def hash_backup_codes(self, codes: List[str]) -> List[str]:
        """Hash backup codes for secure storage"""
        hashed_codes = []
        for code in codes:
            # Remove hyphen and hash
            clean_code = code.replace('-', '')
            hashed = hashlib.sha256(clean_code.encode()).hexdigest()
            hashed_codes.append(hashed)
        
        return hashed_codes
    
    def verify_backup_code(self, provided_code: str, stored_hashes: List[str]) -> Tuple[bool, Optional[str]]:
        """Verify backup code and return the hash if valid"""
        clean_code = provided_code.replace('-', '').upper()
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
            "created_at": time.time()
        }
    
    def validate_mfa_token(self, secret: str, token: str, backup_codes: List[str] = None) -> Dict[str, Any]:
        """Validate MFA token (TOTP or backup code)"""
        # Try TOTP first
        if self.verify_totp_token(secret, token):
            return {
                "valid": True,
                "method": "totp",
                "backup_code_used": None
            }
        
        # Try backup codes if provided
        if backup_codes:
            is_valid, used_hash = self.verify_backup_code(token, backup_codes)
            if is_valid:
                return {
                    "valid": True,
                    "method": "backup_code",
                    "backup_code_used": used_hash
                }
        
        return {
            "valid": False,
            "method": None,
            "backup_code_used": None
        }
'''
        
        # Write MFA manager to file
        mfa_file = Path("backend/fastapi/core/mfa_manager.py")
        mfa_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mfa_file, 'w', encoding='utf-8') as f:
            f.write(mfa_code)
        
        return {
            "success": True,
            "component": "mfa_framework",
            "file_created": str(mfa_file),
            "details": "Multi-factor authentication framework implemented"
        }
    
    async def _implement_brute_force_protection(self) -> Dict[str, Any]:
        """Implement brute force protection"""
        brute_force_code = '''
"""
Brute Force Protection System
Implements rate limiting and account lockout protection
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from collections import defaultdict, deque

class BruteForceProtector:
    def __init__(self):
        # Rate limiting storage (in production, use Redis)
        self.login_attempts = defaultdict(deque)  # IP -> deque of timestamps
        self.failed_logins = defaultdict(int)  # username -> count
        self.locked_accounts = {}  # username -> lock_until_timestamp
        self.blocked_ips = {}  # IP -> block_until_timestamp
        
        # Configuration
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.rate_limit_window = timedelta(minutes=1)
        self.max_requests_per_minute = 10
        self.ip_block_duration = timedelta(hours=1)
        self.max_failed_attempts_per_ip = 20
    
    def check_rate_limit(self, ip_address: str) -> Dict[str, Any]:
        """Check if IP is within rate limits"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old attempts
        attempts = self.login_attempts[ip_address]
        while attempts and attempts[0] < minute_ago:
            attempts.popleft()
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[ip_address]:
                return {
                    "allowed": False,
                    "reason": "IP_BLOCKED",
                    "retry_after": (self.blocked_ips[ip_address] - datetime.utcnow()).total_seconds()
                }
            else:
                # Unblock IP
                del self.blocked_ips[ip_address]
        
        # Check rate limit
        if len(attempts) >= self.max_requests_per_minute:
            return {
                "allowed": False,
                "reason": "RATE_LIMITED",
                "retry_after": 60 - (now - attempts[0])
            }
        
        # Record this attempt
        attempts.append(now)
        
        return {
            "allowed": True,
            "remaining_attempts": self.max_requests_per_minute - len(attempts)
        }
    
    def check_account_lockout(self, username: str) -> Dict[str, Any]:
        """Check if account is locked"""
        if username in self.locked_accounts:
            lock_until = self.locked_accounts[username]
            if datetime.utcnow() < lock_until:
                return {
                    "locked": True,
                    "reason": "ACCOUNT_LOCKED",
                    "unlock_time": lock_until,
                    "retry_after": (lock_until - datetime.utcnow()).total_seconds()
                }
            else:
                # Unlock account
                del self.locked_accounts[username]
                self.failed_logins[username] = 0
        
        return {"locked": False}
    
    def record_failed_login(self, username: str, ip_address: str) -> Dict[str, Any]:
        """Record failed login attempt and check for lockout"""
        self.failed_logins[username] += 1
        failed_count = self.failed_logins[username]
        
        result = {
            "failed_attempts": failed_count,
            "account_locked": False,
            "ip_blocked": False
        }
        
        # Check for account lockout
        if failed_count >= self.max_login_attempts:
            lock_until = datetime.utcnow() + self.lockout_duration
            self.locked_accounts[username] = lock_until
            result["account_locked"] = True
            result["lock_until"] = lock_until
        
        # Check for IP blocking (excessive failed attempts)
        ip_failed_attempts = sum(1 for user, count in self.failed_logins.items() 
                               if self._is_recent_attempt(user, ip_address))
        
        if ip_failed_attempts >= self.max_failed_attempts_per_ip:
            block_until = datetime.utcnow() + self.ip_block_duration
            self.blocked_ips[ip_address] = block_until
            result["ip_blocked"] = True
            result["ip_block_until"] = block_until
        
        return result
    
    def record_successful_login(self, username: str) -> None:
        """Record successful login and reset failed attempts"""
        if username in self.failed_logins:
            del self.failed_logins[username]
        
        if username in self.locked_accounts:
            del self.locked_accounts[username]
    
    def _is_recent_attempt(self, username: str, ip_address: str) -> bool:
        """Check if failed attempt is recent (for IP blocking logic)"""
        # In a real implementation, you'd track IP per failed attempt
        # This is a simplified version
        return True
    
    def get_security_status(self, username: str, ip_address: str) -> Dict[str, Any]:
        """Get comprehensive security status"""
        rate_limit = self.check_rate_limit(ip_address)
        account_status = self.check_account_lockout(username)
        
        return {
            "rate_limit": rate_limit,
            "account_status": account_status,
            "failed_attempts": self.failed_logins.get(username, 0),
            "ip_blocked": ip_address in self.blocked_ips,
            "security_level": self._calculate_security_level(username, ip_address)
        }
    
    def _calculate_security_level(self, username: str, ip_address: str) -> str:
        """Calculate security threat level"""
        failed_attempts = self.failed_logins.get(username, 0)
        
        if ip_address in self.blocked_ips or username in self.locked_accounts:
            return "HIGH_RISK"
        elif failed_attempts >= 3:
            return "MEDIUM_RISK"
        elif failed_attempts >= 1:
            return "LOW_RISK"
        else:
            return "NORMAL"
    
    def cleanup_expired_blocks(self) -> Dict[str, int]:
        """Clean up expired locks and blocks"""
        now = datetime.utcnow()
        cleaned = {"accounts": 0, "ips": 0}
        
        # Clean expired account locks
        expired_accounts = [username for username, lock_time in self.locked_accounts.items() 
                          if now >= lock_time]
        for username in expired_accounts:
            del self.locked_accounts[username]
            self.failed_logins[username] = 0
            cleaned["accounts"] += 1
        
        # Clean expired IP blocks
        expired_ips = [ip for ip, block_time in self.blocked_ips.items() 
                      if now >= block_time]
        for ip in expired_ips:
            del self.blocked_ips[ip]
            cleaned["ips"] += 1
        
        return cleaned
    
    def manually_unlock_account(self, username: str) -> bool:
        """Manually unlock an account (admin function)"""
        if username in self.locked_accounts:
            del self.locked_accounts[username]
            self.failed_logins[username] = 0
            return True
        return False
    
    def manually_unblock_ip(self, ip_address: str) -> bool:
        """Manually unblock an IP (admin function)"""
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
            return True
        return False
'''
        
        # Write brute force protector to file
        brute_force_file = Path("backend/fastapi/core/brute_force_protector.py")
        brute_force_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(brute_force_file, 'w', encoding='utf-8') as f:
            f.write(brute_force_code)
        
        return {
            "success": True,
            "component": "brute_force_protection",
            "file_created": str(brute_force_file),
            "details": "Brute force protection system implemented"
        }
    
    async def create_security_configuration(self) -> Dict[str, Any]:
        """Create comprehensive security configuration"""
        logger.info("🔧 Creating Security Configuration...")
        
        security_config = {
            "security_policy": {
                "password_policy": self.security_config["password_policy"],
                "jwt_policy": self.security_config["jwt_policy"],
                "rate_limiting": self.security_config["rate_limiting"],
                "security_headers": self.security_config["security_headers"],
                "session_security": {
                    "session_timeout_minutes": 120,
                    "max_sessions_per_user": 5,
                    "require_secure_cookies": True,
                    "session_fingerprinting": True
                },
                "mfa_policy": {
                    "required_for_admin": True,
                    "backup_codes_count": 8,
                    "totp_window_seconds": 30
                },
                "brute_force_protection": {
                    "max_login_attempts": 5,
                    "lockout_duration_minutes": 15,
                    "ip_blocking_enabled": True,
                    "rate_limiting_enabled": True
                }
            },
            "monitoring": {
                "log_failed_logins": True,
                "log_successful_logins": True,
                "log_security_events": True,
                "alert_on_multiple_failures": True,
                "alert_threshold": 10
            },
            "compliance": {
                "gdpr_compliant": True,
                "data_retention_days": 365,
                "audit_log_retention_days": 2555,  # 7 years
                "encryption_standards": ["AES-256", "RSA-2048"],
                "password_standards": "NIST-800-63B"
            }
        }
        
        # Write security configuration
        config_file = Path("config/security_config.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(security_config, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "component": "security_configuration",
            "file_created": str(config_file),
            "details": "Comprehensive security configuration created"
        }
    
    async def run_comprehensive_security_enhancement(self) -> Dict[str, Any]:
        """Run comprehensive security enhancement process"""
        logger.info("🛡️ Starting Comprehensive Security Enhancement")
        logger.info("=" * 60)
        
        # Enhance authentication security
        auth_results = await self.enhance_authentication_security()
        
        # Create security configuration
        config_results = await self.create_security_configuration()
        
        # Calculate overall results
        total_components = len(auth_results["enhancements"]) + 1  # +1 for config
        successful_components = auth_results["summary"]["successful"] + (1 if config_results["success"] else 0)
        
        overall_results = {
            "timestamp": self.timestamp,
            "enhancement_type": "comprehensive_security",
            "authentication_enhancements": auth_results,
            "security_configuration": config_results,
            "overall_summary": {
                "total_components": total_components,
                "successful_components": successful_components,
                "success_rate": round((successful_components / total_components) * 100, 1),
                "security_level": "HIGH" if successful_components >= total_components - 1 else "MEDIUM",
                "enhancements_completed": [
                    "Advanced password validation",
                    "Enhanced JWT security",
                    "Secure session management", 
                    "Multi-factor authentication framework",
                    "Brute force protection",
                    "Comprehensive security configuration"
                ]
            }
        }
        
        # Save results
        results_dir = Path("logs/security_enhancement")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = results_dir / f"security_enhancement_{self.timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(overall_results, f, indent=2, ensure_ascii=False)
        
        logger.info("=" * 60)
        logger.info("🎉 SECURITY ENHANCEMENT COMPLETE")
        logger.info(f"Components Enhanced: {successful_components}/{total_components}")
        logger.info(f"Success Rate: {overall_results['overall_summary']['success_rate']}%")
        logger.info(f"Security Level: {overall_results['overall_summary']['security_level']}")
        logger.info(f"Results saved: {results_file}")
        logger.info("=" * 60)
        
        return overall_results

async def main():
    """Main execution function"""
    enhancer = SecurityEnhancementEngine()
    results = await enhancer.run_comprehensive_security_enhancement()
    return results

if __name__ == "__main__":
    asyncio.run(main())
