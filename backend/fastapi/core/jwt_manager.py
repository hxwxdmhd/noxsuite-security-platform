"""
Enhanced JWT Security Manager
Implements advanced JWT security features
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt


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

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        # Add security claims
        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access",
                "jti": secrets.token_urlsafe(8),  # JWT ID for tracking
            }
        )

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token with enhanced security"""
        token_data = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),
        }

        refresh_token = jwt.encode(
            token_data, self.secret_key, algorithm=self.algorithm
        )

        # Store refresh token (in production, use database)
        self.refresh_tokens[token_data["jti"]] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_used": datetime.utcnow(),
        }

        return refresh_token

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
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
            if now - token_data["created_at"] > timedelta(
                days=self.refresh_token_expire_days
            ):
                expired.append(jti)

        for jti in expired:
            del self.refresh_tokens[jti]

        return len(expired)
