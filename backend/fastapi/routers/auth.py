#!/usr/bin/env python3
"""
NoxSuite FastAPI Authentication Module
Critical authentication infrastructure with JWT token management
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr


# Authentication schemas
class UserCredentials(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    roles: list[str] = []
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class AuthManager:
    """Authentication manager with JWT token handling"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY", self._generate_secret_key())
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

        # Default admin user for bootstrap
        self.users_db = {
            "noxsuite_admin": {
                "id": "admin_001",
                "username": "noxsuite_admin",
                "email": "admin@noxsuite.local",
                "hashed_password": self.get_password_hash("noxsuite_secure_2024"),
                "roles": ["admin", "user"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "last_login": None,
            }
        }

        self.logger = logging.getLogger(__name__)

    def _generate_secret_key(self) -> str:
        """Generate a secure random secret key"""
        return secrets.token_urlsafe(32)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username/password"""
        try:
            user = self.users_db.get(username)
            if not user:
                return None

            if not self.verify_password(password, user["hashed_password"]):
                return None

            if not user["is_active"]:
                return None

            # Update last login
            user["last_login"] = datetime.now(timezone.utc)
            return user

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT access token"""
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )
            to_encode.update({"exp": expire, "type": "access"})

            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt

        except Exception as e:
            self.logger.error(f"Token creation error: {e}")
            raise HTTPException(
                status_code=500, detail="Token creation failed")

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(
                days=self.refresh_token_expire_days
            )
            to_encode.update({"exp": expire, "type": "refresh"})

            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt

        except Exception as e:
            self.logger.error(f"Refresh token creation error: {e}")
            raise HTTPException(
                status_code=500, detail="Refresh token creation failed")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") not in ["access", "refresh"]:
                return None

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(
                timezone.utc
            ):
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


# Global auth manager instance
auth_manager = AuthManager()
security = HTTPBearer()

# Authentication router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get the current authenticated user"""
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if it's an access token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = auth_manager.users_db.get(username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        auth_manager.logger.error(f"User authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserCredentials, request: Request):
    """Authenticate user and return JWT tokens"""
    try:
        # Authenticate user
        user = auth_manager.authenticate_user(
            credentials.username, credentials.password
        )
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create tokens
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "roles": user["roles"],
        }

        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)

        auth_manager.logger.info(
            f"User {user['username']} logged in successfully from {request.client.host}"
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_manager.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        auth_manager.logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = auth_manager.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        user = auth_manager.users_db.get(username)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=401,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "roles": user["roles"],
        }

        new_access_token = auth_manager.create_access_token(token_data)
        new_refresh_token = auth_manager.create_refresh_token(token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=auth_manager.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        auth_manager.logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout current user (token blacklisting would be implemented here)"""
    try:
        auth_manager.logger.info(f"User {current_user['username']} logged out")
        return {"message": "Successfully logged out"}

    except Exception as e:
        auth_manager.logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    try:
        return UserProfile(
            id=current_user["id"],
            username=current_user["username"],
            email=current_user.get("email"),
            roles=current_user["roles"],
            is_active=current_user["is_active"],
            created_at=current_user["created_at"],
            last_login=current_user.get("last_login"),
        )

    except Exception as e:
        auth_manager.logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Profile retrieval failed")


@router.get("/verify")
async def verify_token_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Verify token validity"""
    return {
        "valid": True,
        "username": current_user["username"],
        "roles": current_user["roles"],
    }


# Health check for authentication service
@router.get("/health")
async def auth_health():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }
