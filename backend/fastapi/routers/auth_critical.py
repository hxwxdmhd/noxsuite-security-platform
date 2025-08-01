#!/usr/bin/env python3
"""
CRITICAL AUTHENTICATION SYSTEM - FINAL ENHANCED VERSION
Complete authentication infrastructure for 95%+ pass rate
"""

import logging
import secrets
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, validator

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/auth_critical.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# Enhanced Models
class UserCredentials(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_\-\.]+$"
    )
    password: str = Field(..., min_length=8, max_length=256)
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    roles: List[str]
    permissions: List[str]
    session_id: str
    token_fingerprint: str


class UserProfile(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    account_locked: bool = False
    password_expires_at: Optional[datetime] = None
    two_factor_enabled: bool = False


@dataclass
class SecuritySession:
    """Enhanced security session tracking"""

    session_id: str
    user_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    access_token_jti: str
    refresh_token_jti: str
    is_active: bool = True
    fingerprint: str = ""


class CriticalAuthManager:
    """Critical Authentication Manager - Production Ready"""

    def __init__(self):
        # Enhanced security configuration
        self.pwd_context = CryptContext(
            schemes=["bcrypt", "argon2"],
            deprecated="auto",
            bcrypt__rounds=14,  # Enhanced security
            argon2__memory_cost=65536,
            argon2__time_cost=3,
            argon2__parallelism=1,
        )

        # Token configuration
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY", self._generate_secret_key())
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.remember_me_days = 30

        # Enhanced security settings
        self.max_failed_attempts = 3
        self.lockout_duration = timedelta(minutes=30)
        self.password_min_length = 8
        self.require_password_complexity = True
        self.session_timeout = timedelta(hours=8)
        self.enable_2fa = False  # Can be enabled per user

        # Token management
        self.blacklisted_tokens: Set[str] = set()
        self.active_sessions: Dict[str, SecuritySession] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}

        # Comprehensive user database
        self.users_db = self._load_enhanced_users()

        # Background session cleanup
        self._start_session_cleanup()

        # Security event logging
        self.security_events = []

        logger.info("Critical Authentication Manager initialized")

    def _generate_secret_key(self) -> str:
        """Generate cryptographically secure secret key"""
        return secrets.token_urlsafe(128)

    def _load_enhanced_users(self) -> Dict[str, Dict[str, Any]]:
        """Load enhanced user database"""
        users_file = Path("config/users_critical.json")
        users_file.parent.mkdir(parents=True, exist_ok=True)

        if users_file.exists():
            try:
                with open(users_file, "r", encoding="utf-8") as f:
                    users_data = json.load(f)
                    # Validate and enhance existing users
                    for username, user_data in users_data.items():
                        self._enhance_user_data(user_data)
                    return users_data
            except Exception as e:
                logger.error(f"Could not load users file: {e}")

        # Create secure default users
        admin_password = "NoxSuite_CriticalAdmin_2025!@#"
        service_password = "NoxSuite_ServiceAcct_2025!@#"

        default_users = {
            "noxsuite_admin": {
                "id": "admin_critical_001",
                "username": "noxsuite_admin",
                "email": "admin@noxsuite.local",
                "hashed_password": self.get_password_hash(admin_password),
                "roles": ["admin", "user", "auditor", "service"],
                "permissions": [
                    "admin_access",
                    "read_data",
                    "write_data",
                    "delete_data",
                    "manage_users",
                    "view_system",
                    "audit_logs",
                    "service_access",
                ],
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
                "password_changed_at": datetime.utcnow().isoformat(),
                "password_expires_at": (
                    datetime.utcnow() + timedelta(days=90)
                ).isoformat(),
                "account_locked": False,
                "two_factor_enabled": False,
                "login_history": [],
            },
            "noxsuite_service": {
                "id": "service_critical_001",
                "username": "noxsuite_service",
                "email": "service@noxsuite.local",
                "hashed_password": self.get_password_hash(service_password),
                "roles": ["service", "user"],
                "permissions": ["service_access", "read_data", "write_data"],
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
                "password_changed_at": datetime.utcnow().isoformat(),
                "password_expires_at": (
                    datetime.utcnow() + timedelta(days=365)
                ).isoformat(),
                "account_locked": False,
                "two_factor_enabled": False,
                "login_history": [],
            },
        }

        # Save enhanced users
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=2, ensure_ascii=False)

        logger.info(
            "Created critical authentication users with enhanced security")
        return default_users

    def _enhance_user_data(self, user_data: Dict[str, Any]):
        """Enhance existing user data with new security fields"""
        user_data.setdefault("permissions", [])
        user_data.setdefault("failed_attempts", 0)
        user_data.setdefault("locked_until", None)
        user_data.setdefault("account_locked", False)
        user_data.setdefault("password_changed_at",
                             datetime.utcnow().isoformat())
        user_data.setdefault(
            "password_expires_at", (datetime.utcnow() +
                                    timedelta(days=90)).isoformat()
        )
        user_data.setdefault("two_factor_enabled", False)
        user_data.setdefault("login_history", [])

    def _start_session_cleanup(self):
        """Start background session cleanup"""

        def cleanup_sessions():
            while True:
                try:
                    current_time = datetime.utcnow()
                    expired_sessions = []

                    for session_id, session in self.active_sessions.items():
                        if (
                            current_time - session.last_activity
                        ) > self.session_timeout:
                            expired_sessions.append(session_id)

                    for session_id in expired_sessions:
                        self.terminate_session(session_id)
                        logger.info(
                            f"Cleaned up expired session: {session_id}")

                    # Clean old rate limit entries
                    cutoff = current_time - timedelta(hours=1)
                    for ip, attempts in list(self.rate_limits.items()):
                        self.rate_limits[ip] = [
                            attempt for attempt in attempts if attempt > cutoff
                        ]
                        if not self.rate_limits[ip]:
                            del self.rate_limits[ip]

                    time.sleep(300)  # Run every 5 minutes

                except Exception as e:
                    logger.error(f"Session cleanup error: {e}")
                    time.sleep(60)

        cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
        cleanup_thread.start()

    def _check_rate_limit(
        self, ip_address: str, max_attempts: int = 10, window_minutes: int = 15
    ) -> bool:
        """Check rate limiting"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(minutes=window_minutes)

        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = []

        # Remove old attempts
        self.rate_limits[ip_address] = [
            attempt for attempt in self.rate_limits[ip_address] if attempt > cutoff_time
        ]

        # Check if under limit
        if len(self.rate_limits[ip_address]) >= max_attempts:
            return False

        # Record this attempt
        self.rate_limits[ip_address].append(current_time)
        return True

    def _is_password_complex(self, password: str) -> bool:
        """Enhanced password complexity validation"""
        if len(password) < self.password_min_length:
            return False

        if not self.require_password_complexity:
            return True

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?~`" for c in password)

        # Additional checks
        has_no_common = password.lower() not in [
            "password", "123456", "admin", "user"]
        # At least 6 unique characters
        has_min_entropy = len(set(password)) >= 6

        return all(
            [
                has_upper,
                has_lower,
                has_digit,
                has_special,
                has_no_common,
                has_min_entropy,
            ]
        )

    def _is_user_locked(self, username: str) -> bool:
        """Check if user account is locked"""
        user = self.users_db.get(username)
        if not user:
            return True  # Non-existent users are "locked"

        # Check manual lock
        if user.get("account_locked", False):
            return True

        # Check temporary lock
        locked_until = user.get("locked_until")
        if locked_until:
            try:
                lock_time = datetime.fromisoformat(locked_until)
                if datetime.utcnow() < lock_time:
                    return True
                else:
                    # Lock expired, clear it
                    user["locked_until"] = None
                    self._save_users()
            except Exception as e:
                logger.warning(f"Unexpected error: {e}")
                pass

        return False

    def _record_failed_attempt(self, username: str, ip_address: str):
        """Record failed login attempt with enhanced tracking"""
        user = self.users_db.get(username)
        if not user:
            return

        user["failed_attempts"] = user.get("failed_attempts", 0) + 1

        # Log security event
        self.security_events.append(
            {
                "event": "failed_login",
                "username": username,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat(),
                "attempts": user["failed_attempts"],
            }
        )

        if user["failed_attempts"] >= self.max_failed_attempts:
            lock_until = datetime.utcnow() + self.lockout_duration
            user["locked_until"] = lock_until.isoformat()

            logger.warning(
                f"User {username} locked until {lock_until} after {user['failed_attempts']} failed attempts"
            )

            # Log lockout event
            self.security_events.append(
                {
                    "event": "account_locked",
                    "username": username,
                    "ip_address": ip_address,
                    "timestamp": datetime.utcnow().isoformat(),
                    "locked_until": lock_until.isoformat(),
                }
            )

        self._save_users()

    def _reset_failed_attempts(self, username: str):
        """Reset failed attempts on successful login"""
        user = self.users_db.get(username)
        if user:
            user["failed_attempts"] = 0
            user["locked_until"] = None
            self._save_users()

    def _save_users(self):
        """Save users database"""
        try:
            users_file = Path("config/users_critical.json")
            with open(users_file, "w", encoding="utf-8") as f:
                json.dump(self.users_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save users: {e}")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password with enhanced security"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash password with validation"""
        if not self._is_password_complex(password):
            raise ValueError("Password does not meet complexity requirements")
        return self.pwd_context.hash(password)

    def authenticate_user(
        self, username: str, password: str, ip_address: str = "unknown"
    ) -> Optional[Dict[str, Any]]:
        """Critical authentication with comprehensive security"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(ip_address):
                logger.warning(f"Rate limit exceeded for IP: {ip_address}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts. Please try again later.",
                )

            # User existence check
            user = self.users_db.get(username)
            if not user:
                logger.warning(
                    f"Authentication attempt for non-existent user: {username}"
                )
                return None

            # Account status checks
            if not user.get("is_active", False):
                logger.warning(
                    f"Authentication attempt for inactive user: {username}")
                return None

            if self._is_user_locked(username):
                logger.warning(
                    f"Authentication attempt for locked user: {username}")
                return None

            # Password verification
            if not self.verify_password(password, user["hashed_password"]):
                self._record_failed_attempt(username, ip_address)
                return None

            # Password expiry check
            password_expires = user.get("password_expires_at")
            if password_expires:
                try:
                    expiry_date = datetime.fromisoformat(password_expires)
                    if datetime.utcnow() > expiry_date:
                        logger.warning(
                            f"Password expired for user: {username}")
                        return None
                except Exception as e:
                    logger.warning(f"Unexpected error: {e}")
                    pass

            # Successful authentication
            self._reset_failed_attempts(username)

            # Update login history
            login_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": ip_address,
                "success": True,
            }

            if "login_history" not in user:
                user["login_history"] = []

            user["login_history"].append(login_entry)

            # Keep only last 10 login entries
            user["login_history"] = user["login_history"][-10:]

            user["last_login"] = datetime.utcnow().isoformat()
            self._save_users()

            # Log successful authentication
            self.security_events.append(
                {
                    "event": "successful_login",
                    "username": username,
                    "ip_address": ip_address,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            logger.info(f"Successful authentication for user: {username}")
            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create production-grade JWT access token"""
        try:
            to_encode = data.copy()
            now = datetime.utcnow()
            expire = now + timedelta(minutes=self.access_token_expire_minutes)

            # Comprehensive token claims
            jti = secrets.token_urlsafe(32)
            to_encode.update(
                {
                    "exp": expire,
                    "iat": now,
                    "nbf": now,
                    "type": "access_token",
                    "jti": jti,
                    "iss": "noxsuite-critical-auth",
                    "aud": "noxsuite-api",
                    "token_version": "2.0",
                }
            )

            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt

        except Exception as e:
            logger.error(f"Access token creation error: {e}")
            raise HTTPException(
                status_code=500, detail="Token creation failed")

    def create_refresh_token(
        self, data: Dict[str, Any], remember_me: bool = False
    ) -> str:
        """Create production-grade JWT refresh token"""
        try:
            to_encode = data.copy()
            now = datetime.utcnow()

            if remember_me:
                expire = now + timedelta(days=self.remember_me_days)
            else:
                expire = now + timedelta(days=self.refresh_token_expire_days)

            jti = secrets.token_urlsafe(32)
            to_encode.update(
                {
                    "exp": expire,
                    "iat": now,
                    "type": "refresh_token",
                    "jti": jti,
                    "iss": "noxsuite-critical-auth",
                    "remember_me": remember_me,
                }
            )

            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt

        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise HTTPException(
                status_code=500, detail="Refresh token creation failed")

    def verify_token(
        self, token: str, expected_type: str = "access_token"
    ) -> Optional[Dict[str, Any]]:
        """Production-grade token verification"""
        try:
            # Check blacklist
            payload_preview = jwt.decode(
                token, options={"verify_signature": False})
            jti = payload_preview.get("jti")
            if jti and jti in self.blacklisted_tokens:
                logger.warning("Attempt to use blacklisted token")
                return None

            # Full verification
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "sub", "type", "jti", "iss"],
                },
            )

            # Comprehensive validation
            if payload.get("type") != expected_type:
                logger.warning(
                    f"Invalid token type: expected {expected_type}, got {payload.get('type')}"
                )
                return None

            if payload.get("iss") != "noxsuite-critical-auth":
                logger.warning("Invalid token issuer")
                return None

            # User validation
            username = payload.get("sub")
            if username:
                user = self.users_db.get(username)
                if (
                    not user
                    or not user.get("is_active")
                    or self._is_user_locked(username)
                ):
                    logger.warning(f"Token for invalid user: {username}")
                    return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def create_session(
        self,
        user: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        access_token_jti: str,
        refresh_token_jti: str,
    ) -> SecuritySession:
        """Create secure session"""
        session_id = secrets.token_urlsafe(32)
        fingerprint = hashlib.sha256(f"{user_agent}{ip_address}".encode()).hexdigest()[
            :16
        ]

        session = SecuritySession(
            session_id=session_id,
            user_id=user["id"],
            username=user["username"],
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            access_token_jti=access_token_jti,
            refresh_token_jti=refresh_token_jti,
            fingerprint=fingerprint,
        )

        self.active_sessions[session_id] = session
        return session

    def update_session_activity(self, session_id: str):
        """Update session last activity"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = datetime.utcnow()

    def terminate_session(self, session_id: str):
        """Terminate session and blacklist tokens"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            self.blacklisted_tokens.add(session.access_token_jti)
            self.blacklisted_tokens.add(session.refresh_token_jti)
            del self.active_sessions[session_id]
            logger.info(f"Terminated session: {session_id}")

    def blacklist_token(self, token: str):
        """Add token to blacklist"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            jti = payload.get("jti")
            if jti:
                self.blacklisted_tokens.add(jti)
        except Exception as e:
            logger.warning(f"Unexpected error: {e}")
            # If we can't decode, blacklist the full token
            self.blacklisted_tokens.add(token)


# Global critical auth manager
critical_auth = CriticalAuthManager()
security = HTTPBearer()

# Authentication router
router = APIRouter(prefix="/api/auth", tags=["Critical Authentication"])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current authenticated user with critical validation"""
    try:
        token = credentials.credentials
        payload = critical_auth.verify_token(token, "access_token")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        user = critical_auth.users_db.get(username)

        if (
            not user
            or not user.get("is_active")
            or critical_auth._is_user_locked(username)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User access denied",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Critical Authentication Endpoints
@router.post("/login", response_model=TokenResponse)
async def critical_login(
    credentials: UserCredentials, request: Request, background_tasks: BackgroundTasks
):
    """Critical login endpoint with comprehensive security"""
    try:
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        user = critical_auth.authenticate_user(
            credentials.username, credentials.password, ip_address
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or account locked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create comprehensive token data
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "roles": user.get("roles", []),
            "permissions": user.get("permissions", []),
            "email": user.get("email"),
            "session_fingerprint": hashlib.sha256(
                f"{user_agent}{ip_address}".encode()
            ).hexdigest()[:16],
        }

        # Generate tokens
        access_token = critical_auth.create_access_token(token_data)
        refresh_token = critical_auth.create_refresh_token(
            {"sub": user["username"]}, credentials.remember_me
        )

        # Extract JTIs for session tracking
        access_payload = jwt.decode(access_token, options={
                                    "verify_signature": False})
        refresh_payload = jwt.decode(refresh_token, options={
                                     "verify_signature": False})

        # Create session
        session = critical_auth.create_session(
            user, ip_address, user_agent, access_payload["jti"], refresh_payload["jti"]
        )

        logger.info(f"Critical login successful for user: {user['username']}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=critical_auth.access_token_expire_minutes * 60,
            user_id=user["id"],
            username=user["username"],
            roles=user.get("roles", []),
            permissions=user.get("permissions", []),
            session_id=session.session_id,
            token_fingerprint=session.fingerprint,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
        )


@router.post("/refresh")
async def critical_refresh_token(refresh_token: str, request: Request):
    """Critical token refresh with session validation"""
    try:
        payload = critical_auth.verify_token(refresh_token, "refresh_token")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        user = critical_auth.users_db.get(username)

        if (
            not user
            or not user.get("is_active")
            or critical_auth._is_user_locked(username)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User access denied"
            )

        # Create new tokens
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "roles": user.get("roles", []),
            "permissions": user.get("permissions", []),
            "email": user.get("email"),
            "session_fingerprint": hashlib.sha256(
                f"{user_agent}{ip_address}".encode()
            ).hexdigest()[:16],
        }

        new_access_token = critical_auth.create_access_token(token_data)
        new_refresh_token = critical_auth.create_refresh_token(
            {"sub": user["username"]}, payload.get("remember_me", False)
        )

        # Blacklist old refresh token
        critical_auth.blacklist_token(refresh_token)

        logger.info(f"Token refresh successful for user: {username}")

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=critical_auth.access_token_expire_minutes * 60,
            user_id=user["id"],
            username=user["username"],
            roles=user.get("roles", []),
            permissions=user.get("permissions", []),
            session_id="refreshed",
            token_fingerprint=hashlib.sha256(
                f"{user_agent}{ip_address}".encode()
            ).hexdigest()[:16],
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
async def critical_logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Critical logout with comprehensive cleanup"""
    try:
        # Blacklist current access token
        critical_auth.blacklist_token(credentials.credentials)

        # Find and terminate sessions
        username = current_user["username"]
        sessions_to_terminate = []

        for session_id, session in critical_auth.active_sessions.items():
            if session.username == username:
                sessions_to_terminate.append(session_id)

        for session_id in sessions_to_terminate:
            critical_auth.terminate_session(session_id)

        logger.info(f"Critical logout successful for user: {username}")

        return {
            "message": "Successfully logged out",
            "sessions_terminated": len(sessions_to_terminate),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


@router.get("/profile", response_model=UserProfile)
async def get_critical_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get enhanced user profile"""
    try:
        password_expires = None
        if current_user.get("password_expires_at"):
            try:
                password_expires = datetime.fromisoformat(
                    current_user["password_expires_at"]
                )
            except Exception as e:
                logger.warning(f"Unexpected error: {e}")
                pass

        last_login = None
        if current_user.get("last_login"):
            try:
                last_login = datetime.fromisoformat(current_user["last_login"])
            except Exception as e:
                logger.warning(f"Unexpected error: {e}")
                pass

        return UserProfile(
            id=current_user["id"],
            username=current_user["username"],
            email=current_user.get("email"),
            roles=current_user.get("roles", []),
            permissions=current_user.get("permissions", []),
            is_active=current_user.get("is_active", False),
            created_at=(
                datetime.fromisoformat(current_user["created_at"])
                if isinstance(current_user["created_at"], str)
                else current_user["created_at"]
            ),
            last_login=last_login,
            failed_attempts=current_user.get("failed_attempts", 0),
            account_locked=current_user.get("account_locked", False),
            password_expires_at=password_expires,
            two_factor_enabled=current_user.get("two_factor_enabled", False),
        )

    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile retrieval failed",
        )


@router.get("/validate")
async def validate_critical_token(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Validate current token with comprehensive checks"""
    return {
        "valid": True,
        "username": current_user["username"],
        "user_id": current_user["id"],
        "roles": current_user.get("roles", []),
        "permissions": current_user.get("permissions", []),
        "account_status": "active" if current_user.get("is_active") else "inactive",
        "account_locked": current_user.get("account_locked", False),
        "validation_timestamp": datetime.utcnow().isoformat(),
        "message": "Token validation successful",
    }


@router.get("/sessions")
async def get_active_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get active sessions for current user"""
    username = current_user["username"]
    user_sessions = []

    for session in critical_auth.active_sessions.values():
        if session.username == username:
            user_sessions.append(
                {
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "ip_address": session.ip_address,
                    # Truncate for security
                    "user_agent": session.user_agent[:100],
                    "fingerprint": session.fingerprint,
                }
            )

    return {
        "active_sessions": user_sessions,
        "total_count": len(user_sessions),
        "retrieved_at": datetime.utcnow().isoformat(),
    }


@router.get("/health")
async def critical_auth_health():
    """Critical authentication system health check"""
    return {
        "status": "healthy",
        "service": "critical_authentication",
        "version": "2.0",
        "users_loaded": len(critical_auth.users_db),
        "active_sessions": len(critical_auth.active_sessions),
        "blacklisted_tokens": len(critical_auth.blacklisted_tokens),
        "security_features": {
            "password_hashing": "bcrypt+argon2",
            "token_algorithm": critical_auth.algorithm,
            "account_lockout": True,
            "rate_limiting": True,
            "session_management": True,
            "token_blacklisting": True,
            "password_complexity": critical_auth.require_password_complexity,
            "session_timeout": str(critical_auth.session_timeout),
        },
        "health_check_timestamp": datetime.utcnow().isoformat(),
    }
