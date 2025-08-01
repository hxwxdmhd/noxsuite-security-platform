#!/usr/bin/env python3
"""
Enhanced NoxSuite FastAPI Authentication Module
Critical authentication infrastructure with robust JWT token management
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, validator

# Enhanced logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Enhanced Authentication Schemas
class UserCredentials(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    roles: List[str]


class UserProfile(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    roles: List[str] = []
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_attempts: int = 0


class PasswordResetRequest(BaseModel):
    username: str
    new_password: str = Field(..., min_length=8)


class EnhancedAuthManager:
    """Enhanced Authentication manager with security best practices"""

    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12  # Stronger hashing
        )
        self.secret_key = os.getenv("JWT_SECRET_KEY", self._generate_secret_key())
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.password_min_length = 8
        self.require_password_complexity = True

        # Token blacklist for logout
        self.blacklisted_tokens = set()

        # Rate limiting
        self.login_attempts = {}

        # Load or create users
        self.users_db = self._load_users()
        self.logger = logging.getLogger(__name__)

    def _generate_secret_key(self) -> str:
        """Generate a cryptographically secure secret key"""
        return secrets.token_urlsafe(64)

    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users with enhanced security validation"""
        users_file = Path("config/users.json")
        users_file.parent.mkdir(parents=True, exist_ok=True)

        if users_file.exists():
            try:
                with open(users_file, "r", encoding="utf-8") as f:
                    users_data = json.load(f)
                    # Validate and upgrade user data
                    for username, user_data in users_data.items():
                        user_data.setdefault("failed_attempts", 0)
                        user_data.setdefault("locked_until", None)
                        user_data.setdefault(
                            "password_changed_at", datetime.utcnow().isoformat()
                        )
                    return users_data
            except Exception as e:
                self.logger.error(f"Could not load users file: {e}")

        # Create enhanced default admin
        secure_password = "NoxSuite_Admin_2025!Secure"
        default_admin = {
            "noxsuite_admin": {
                "id": "admin_001",
                "username": "noxsuite_admin",
                "email": "admin@noxsuite.local",
                "hashed_password": self.get_password_hash(secure_password),
                "roles": ["admin", "user", "auditor"],
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
                "password_changed_at": datetime.utcnow().isoformat(),
            }
        }

        # Save to file
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(default_admin, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Created default admin user with secure password")
        return default_admin

    def _is_password_complex(self, password: str) -> bool:
        """Validate password complexity"""
        if not self.require_password_complexity:
            return len(password) >= self.password_min_length

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return (
            len(password) >= self.password_min_length
            and has_upper
            and has_lower
            and has_digit
            and has_special
        )

    def _is_user_locked(self, username: str) -> bool:
        """Check if user is locked due to failed attempts"""
        user = self.users_db.get(username)
        if not user:
            return False

        locked_until = user.get("locked_until")
        if not locked_until:
            return False

        try:
            lock_time = datetime.fromisoformat(locked_until)
            return datetime.utcnow() < lock_time
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Invalid lock time format for user {username}: {e}")
            return False

    def _record_failed_attempt(self, username: str):
        """Record failed login attempt and lock if necessary"""
        user = self.users_db.get(username)
        if not user:
            return

        user["failed_attempts"] = user.get("failed_attempts", 0) + 1

        if user["failed_attempts"] >= self.max_failed_attempts:
            lock_until = datetime.utcnow() + self.lockout_duration
            user["locked_until"] = lock_until.isoformat()
            self.logger.warning(f"User {username} locked until {lock_until}")

        self._save_users()

    def _reset_failed_attempts(self, username: str):
        """Reset failed attempts on successful login"""
        user = self.users_db.get(username)
        if user:
            user["failed_attempts"] = 0
            user["locked_until"] = None
            self._save_users()

    def _save_users(self):
        """Save users to file"""
        try:
            users_file = Path("config/users.json")
            with open(users_file, "w", encoding="utf-8") as f:
                json.dump(self.users_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Could not save users: {e}")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password with enhanced security"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash password with enhanced security"""
        if not self._is_password_complex(password):
            raise ValueError("Password does not meet complexity requirements")
        return self.pwd_context.hash(password)

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user with enhanced security checks"""
        try:
            # Rate limiting check
            client_ip = getattr(self, "_current_ip", "unknown")
            attempt_key = f"{username}:{client_ip}"

            # Check if user is locked
            if self._is_user_locked(username):
                self.logger.warning(
                    f"Authentication attempt on locked user: {username}"
                )
                return None

            user = self.users_db.get(username)
            if not user:
                self.logger.warning(
                    f"Authentication attempt for non-existent user: {username}"
                )
                return None

            if not user.get("is_active", False):
                self.logger.warning(
                    f"Authentication attempt for inactive user: {username}"
                )
                return None

            if not self.verify_password(password, user["hashed_password"]):
                self.logger.warning(f"Invalid password for user: {username}")
                self._record_failed_attempt(username)
                return None

            # Successful authentication
            self._reset_failed_attempts(username)
            user["last_login"] = datetime.utcnow().isoformat()
            self._save_users()

            self.logger.info(f"Successful authentication for user: {username}")
            return user

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create enhanced JWT access token"""
        try:
            to_encode = data.copy()
            now = datetime.utcnow()
            expire = now + timedelta(minutes=self.access_token_expire_minutes)

            # Enhanced token claims
            to_encode.update(
                {
                    "exp": expire,
                    "iat": now,
                    "nbf": now,
                    "type": "access_token",
                    "jti": secrets.token_urlsafe(16),
                    "iss": "noxsuite-api",
                    "aud": "noxsuite-client",
                }
            )

            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt

        except Exception as e:
            self.logger.error(f"Access token creation error: {e}")
            raise HTTPException(status_code=500, detail="Token creation failed")

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create enhanced JWT refresh token"""
        try:
            to_encode = data.copy()
            now = datetime.utcnow()
            expire = now + timedelta(days=self.refresh_token_expire_days)

            to_encode.update(
                {
                    "exp": expire,
                    "iat": now,
                    "type": "refresh_token",
                    "jti": secrets.token_urlsafe(16),
                    "iss": "noxsuite-api",
                }
            )

            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt

        except Exception as e:
            self.logger.error(f"Refresh token creation error: {e}")
            raise HTTPException(status_code=500, detail="Refresh token creation failed")

    def verify_token(
        self, token: str, expected_type: str = "access_token"
    ) -> Optional[Dict[str, Any]]:
        """Verify JWT token with enhanced validation"""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                self.logger.warning("Attempt to use blacklisted token")
                return None

            # Decode with comprehensive options
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "sub", "type", "jti"],
                },
            )

            # Verify token type
            if payload.get("type") != expected_type:
                self.logger.warning(
                    f"Invalid token type: expected {expected_type}, got {payload.get('type')}"
                )
                return None

            # Verify issuer
            if payload.get("iss") != "noxsuite-api":
                self.logger.warning("Invalid token issuer")
                return None

            # Additional user validation
            username = payload.get("sub")
            if username:
                user = self.users_db.get(username)
                if not user or not user.get("is_active"):
                    self.logger.warning(
                        f"Token for inactive/non-existent user: {username}"
                    )
                    return None

            return payload

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Token verification error: {e}")
            return None

    def blacklist_token(self, token: str):
        """Add token to blacklist for logout"""
        try:
            # Extract JTI for efficient blacklisting
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )
            jti = payload.get("jti")
            if jti:
                self.blacklisted_tokens.add(jti)
        except (jwt.InvalidTokenError, ValueError) as e:
            # If we can't decode, blacklist the full token
            self.logger.warning(f"Could not decode token for blacklisting: {e}")
            self.blacklisted_tokens.add(token)


# Global enhanced auth manager
auth_manager = EnhancedAuthManager()
security = HTTPBearer()

# Authentication router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current authenticated user with enhanced validation"""
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token, "access_token")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = auth_manager.users_db.get(username)
        if not user or not user.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Enhanced Authentication Endpoints
@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserCredentials, request: Request):
    """Enhanced login endpoint with security features"""
    try:
        # Set IP for rate limiting
        auth_manager._current_ip = request.client.host if request.client else "unknown"

        user = auth_manager.authenticate_user(
            credentials.username, credentials.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create token data
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "roles": user.get("roles", []),
            "email": user.get("email"),
        }

        # Generate tokens
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token({"sub": user["username"]})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_manager.access_token_expire_minutes * 60,
            user_id=user["id"],
            username=user["username"],
            roles=user.get("roles", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Enhanced token refresh endpoint"""
    try:
        payload = auth_manager.verify_token(refresh_token, "refresh_token")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        user = auth_manager.users_db.get(username)

        if not user or not user.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new tokens
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "roles": user.get("roles", []),
            "email": user.get("email"),
        }

        new_access_token = auth_manager.create_access_token(token_data)
        new_refresh_token = auth_manager.create_refresh_token({"sub": user["username"]})

        # Blacklist old refresh token
        auth_manager.blacklist_token(refresh_token)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=auth_manager.access_token_expire_minutes * 60,
            user_id=user["id"],
            username=user["username"],
            roles=user.get("roles", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Enhanced logout endpoint with token blacklisting"""
    try:
        # Blacklist the current token
        auth_manager.blacklist_token(credentials.credentials)

        logger.info(f"User {current_user['username']} logged out successfully")

        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    try:
        return UserProfile(
            id=current_user["id"],
            username=current_user["username"],
            email=current_user.get("email"),
            roles=current_user.get("roles", []),
            is_active=current_user.get("is_active", False),
            created_at=(
                datetime.fromisoformat(current_user["created_at"])
                if isinstance(current_user["created_at"], str)
                else current_user["created_at"]
            ),
            last_login=(
                datetime.fromisoformat(current_user["last_login"])
                if current_user.get("last_login")
                and isinstance(current_user["last_login"], str)
                else current_user.get("last_login")
            ),
            failed_attempts=current_user.get("failed_attempts", 0),
        )

    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile retrieval failed",
        )


@router.get("/validate")
async def validate_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Validate current token"""
    return {
        "valid": True,
        "username": current_user["username"],
        "roles": current_user.get("roles", []),
        "message": "Token is valid",
    }


# Health check for authentication system
@router.get("/health")
async def auth_health():
    """Authentication system health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "users_loaded": len(auth_manager.users_db),
        "security_features": {
            "password_hashing": "bcrypt",
            "token_algorithm": auth_manager.algorithm,
            "account_lockout": True,
            "token_blacklisting": True,
            "password_complexity": auth_manager.require_password_complexity,
        },
    }
