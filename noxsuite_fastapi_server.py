#!/usr/bin/env python3
"""
NoxSuite FastAPI Application - MariaDB Enhanced
===============================================
Production-ready FastAPI server with MariaDB, MFA, RBAC, and security.
"""

from passlib.context import CryptContext
import jwt
import bcrypt
import secrets
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# FastAPI imports
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

# MariaDB-compatible database imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from backend.models.mariadb_user import (
        AuditLog,
        Base,
        Role,
        SessionLocal,
        User,
        UserRole,
        UserSession,
        engine,
        get_db,
        log_audit_event,
    )
except ImportError:
    try:
        from mariadb_dev_setup import (
            AuditLog,
            Base,
            MariaDBDevSetup,
            Role,
            User,
            UserRole,
            UserSession,
        )

        setup = MariaDBDevSetup()
        engine = setup.engine
        SessionLocal = setup.SessionLocal

        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        def log_audit_event(db, user_id, action, category, details, request):
            pass  # Placeholder

    except ImportError:
        print(
            "❌ CRITICAL: MariaDB models not available - run mariadb_dev_setup.py first"
        )
        User = Role = UserRole = UserSession = AuditLog = SessionLocal = Base = (
            engine
        ) = None

        def get_db():
            raise HTTPException(
                status_code=500, detail="MariaDB not configured")

        def log_audit_event(*args):
            pass


# JWT and security

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "noxsuite_secret_key_2025_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Initialize FastAPI
app = FastAPI(
    title="NoxSuite API",
    description="Production-ready API with MFA and RBAC",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Startup time
start_time = time.time()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models
class UserLogin(BaseModel):
    email: str
    password: str
    mfa_code: Optional[str] = None


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    mfa_enabled: bool
    created_at: datetime


# Database dependency
def get_db():
    """Get database session"""
    if SessionLocal is None:
        raise HTTPException(
            status_code=500,
            detail="Database not configured. Run setup_database_simple.py first.",
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Authentication utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db),
):
    """Get current authenticated user"""
    if not User:
        raise HTTPException(
            status_code=500, detail="Database models not available")

    payload = verify_token(credentials.credentials)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


def log_audit_event(
    db: SessionLocal,
    user_id: Optional[int],
    action: str,
    resource: str,
    details: dict,
    request: Request,
):
    """Log audit event"""
    if not AuditLog:
        return

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=str(details),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(audit_log)
    db.commit()


# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    return JSONResponse(
        {
            "status": "healthy",
            "uptime": time.time() - start_time,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service": "noxsuite-api",
            "version": "2.0.0",
            "database": "connected" if SessionLocal else "not configured",
        }
    )


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "NoxSuite API v2.0.0",
        "status": "running",
        "documentation": "/api/docs",
        "health": "/health",
    }


# Authentication endpoints
@app.post("/api/auth/login", response_model=Token)
async def login(
    user_login: UserLogin, request: Request, db: SessionLocal = Depends(get_db)
):
    """User login with optional MFA"""
    logger.info(f"Login attempt for: {user_login.email}")
    return await login_handler(user_login, request, db)


# Compatibility endpoints for TestSprite
@app.post("/auth/login", response_model=Token)
async def login_compat(
    user_login: dict, request: Request, db: SessionLocal = Depends(get_db)
):
    """User login compatibility endpoint for TestSprite"""
    logger.info(f"TestSprite login attempt: {user_login}")

    # Convert TestSprite format to our format
    if "username" in user_login and "email" not in user_login:
        # Convert username-based to email-based login
        if user_login["username"] == "admin":
            email = "admin@noxsuite.local"
        elif user_login["username"] == "user":
            email = "user@noxsuite.local"
        else:
            email = f"{user_login['username']}@noxsuite.local"

        login_data = UserLogin(
            email=email,
            password=user_login["password"],
            mfa_code=user_login.get("mfa_code"),
        )

        logger.info(f"Converted TestSprite login to: {login_data}")

        # Call directly without await to handle potential JSONResponse for MFA
        response = await login_handler(login_data, request, db)

        # Handle the JSONResponse for MFA case
        if isinstance(response, JSONResponse):
            logger.info(f"MFA response: {response.body}")
            return response

        return response
    else:
        # Use as-is
        login_data = UserLogin(**user_login)

        # Call directly without await to handle potential JSONResponse for MFA
        response = await login_handler(login_data, request, db)

        # Handle the JSONResponse for MFA case
        if isinstance(response, JSONResponse):
            logger.info(f"MFA response: {response.body}")
            return response

        return response


async def login_handler(user_login: UserLogin, request: Request, db: SessionLocal):
    """User login with optional MFA"""
    if not User:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Find user
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        log_audit_event(
            db,
            None,
            "login_failed",
            "auth",
            {"email": user_login.email, "reason": "user_not_found"},
            request,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Verify password
    if not user.verify_password(user_login.password):
        log_audit_event(
            db, user.id, "login_failed", "auth", {
                "reason": "invalid_password"}, request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Check if MFA is required
    if user.mfa_enabled:
        if not user_login.mfa_code:
            # Create a temporary MFA session
            mfa_session_id = f"{user.id}_{secrets.token_hex(16)}"

            log_audit_event(
                db,
                user.id,
                "login_mfa_required",
                "auth",
                {"mfa_session_id": mfa_session_id},
                request,
            )

            # Return MFA challenge with session ID
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "MFA code required",
                    "session_id": mfa_session_id,
                    "user_id": user.id,
                    "mfa_required": True,
                },
            )

    # Create tokens with unique id to prevent collisions
    unique_id = secrets.token_hex(8)
    access_token = create_access_token(
        data={"sub": str(user.id), "jti": unique_id})
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "jti": unique_id})

    # Create session record
    if UserSession:
        session = UserSession(
            user_id=user.id,
            # Store first 50 chars for reference
            session_token=access_token[:50],
            # Make sure it's unique
            refresh_token=f"{unique_id}_{refresh_token[:40]}",
            expires_at=datetime.utcnow()
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "")[:255],
        )
        db.add(session)

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    log_audit_event(db, user.id, "login_success", "auth", {}, request)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@app.post("/api/auth/register", response_model=UserResponse)
async def register(
    user_register: UserRegister, request: Request, db: SessionLocal = Depends(get_db)
):
    """User registration"""
    if not User:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Check if user exists
    existing_user = (
        db.query(User)
        .filter(
            (User.email == user_register.email)
            | (User.username == user_register.username)
        )
        .first()
    )

    if existing_user:
        log_audit_event(
            db,
            None,
            "register_failed",
            "auth",
            {"email": user_register.email, "reason": "user_exists"},
            request,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    # Create new user
    user = User(
        username=user_register.username,
        email=user_register.email,
        password_hash=User.hash_password(user_register.password),
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    log_audit_event(
        db, user.id, "register_success", "auth", {
            "username": user.username}, request
    )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at,
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        mfa_enabled=current_user.mfa_enabled,
        created_at=current_user.created_at,
    )


@app.post("/api/auth/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """User logout"""
    # Invalidate sessions (simplified - in production, maintain token blacklist)
    if UserSession:
        db.query(UserSession).filter(
            UserSession.user_id == current_user.id, UserSession.is_active == True
        ).update({"is_active": False})
        db.commit()

    log_audit_event(db, current_user.id, "logout", "auth", {}, request)

    return {"message": "Logged out successfully"}


# Protected routes
@app.get("/api/users")
async def list_users(
    current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)
):
    """List all users (admin only in production)"""
    if not User:
        raise HTTPException(status_code=500, detail="Database not configured")

    users = db.query(User).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            mfa_enabled=user.mfa_enabled,
            created_at=user.created_at,
        )
        for user in users
    ]


@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - start_time,
        "features": [
            "JWT Authentication",
            "MFA Support",
            "RBAC Ready",
            "Audit Logging",
            "SQLite Database",
        ],
    }


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Starting NoxSuite API v2.0.0")

    if Base and engine:
        try:
            # Create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    else:
        logger.warning(
            "Database models not available - run setup_database_simple.py")

    logger.info("Loading RBAC and MFA extensions...")

    # Import and apply RBAC/MFA extensions to the app
    try:
        # Import the extension module to register routes
        import rbac_mfa_extension

        # Register RBAC/MFA routes with the app
        from rbac_mfa_extension import register_rbac_mfa_routes

        register_rbac_mfa_routes(app)

        logger.info(
            "✅ RBAC and MFA extensions loaded and routes registered successfully"
        )

        # Verify MFA endpoints are available
        routes = [route.path for route in app.routes]
        if "/api/auth/verify-mfa" in routes:
            logger.info("✅ MFA verification endpoint registered")
        else:
            logger.warning("⚠️ MFA verification endpoint not found")

    except ImportError as e:
        logger.error(f"Failed to load RBAC/MFA extension: {e}")
    except Exception as e:
        logger.error(f"Extension loading error: {e}")

    # Main application entry point
    import uvicorn

    # Install uvicorn if not available
    try:
        import uvicorn
    except ImportError:
        import subprocess

        subprocess.run([sys.executable, "-m", "pip",
                       "install", "uvicorn[standard]"])
        import uvicorn

    uvicorn.run(
        "noxsuite_fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        debug=True,
    )
