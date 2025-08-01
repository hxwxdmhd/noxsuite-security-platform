#!/usr/bin/env python3
"""
RBAC and MFA Extensions for NoxSuite
===================================
Adds RBAC and MFA functionality to the NoxSuite API.
"""

import base64
import json
import os
import secrets
import sys
from datetime import datetime, timedelta

import pyotp

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import FastAPI server
try:
    from typing import List, Optional

    from fastapi import Body, Depends, HTTPException, Request, status
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field

    from noxsuite_fastapi_server import (
        AuditLog,
        Role,
        SessionLocal,
        Token,
        User,
        UserRole,
        UserSession,
        app,
        get_current_user,
        get_db,
    )
except ImportError:
    print(
        "Error: Cannot import FastAPI server. Make sure noxsuite_fastapi_server.py exists."
    )
    sys.exit(1)


# Register all routes with the FastAPI app
def register_rbac_mfa_routes(fastapi_app):
    """Register all RBAC and MFA routes with the FastAPI app"""
    # This is a hack to get around circular imports
    global app
    app = fastapi_app

    # All routes below will be automatically registered with the app
    print("✅ RBAC/MFA routes registered successfully")
    return True


# RBAC Models
class RoleCreate(BaseModel):
    name: str
    description: str
    permissions: List[str]


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    permissions: List[str]


class UserRoleCreate(BaseModel):
    user_id: int
    role_id: int


# MFA Models
class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class MFAVerification(BaseModel):
    session_id: str
    code: str


# TOTP Verification
def verify_totp(secret, code, valid_window=1):
    """
    Verify TOTP code against secret

    Args:
        secret: TOTP secret key
        code: Code to verify
        valid_window: Number of 30-second windows to check before/after current time

    Returns:
        bool: True if code is valid, False otherwise
    """
    if not secret or not code:
        return False

    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)
    except Exception as e:
        print(f"TOTP verification error: {str(e)}")
        return False


class MFAVerify(BaseModel):
    code: str


class MFAEnable(BaseModel):
    code: str
    secret: str


# Add RBAC endpoints
@app.get("/api/roles", response_model=List[RoleResponse])
async def get_roles(
    current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)
):
    """Get all roles (requires admin)"""
    # Check if user has admin role
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    is_admin = any(role.name == "admin" for role in roles)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view roles"
        )

    # Get all roles
    all_roles = db.query(Role).all()
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=json.loads(role.permissions),
        )
        for role in all_roles
    ]


@app.post("/api/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Create a new role (requires admin)"""
    # Check if user has admin role
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    is_admin = any(role.name == "admin" for role in roles)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create roles",
        )

    # Check if role already exists
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role.name}' already exists",
        )

    # Create new role
    new_role = Role(
        name=role.name,
        description=role.description,
        permissions=json.dumps(role.permissions),
        created_at=datetime.utcnow(),
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return RoleResponse(
        id=new_role.id,
        name=new_role.name,
        description=new_role.description,
        permissions=json.loads(new_role.permissions),
    )


@app.delete("/api/roles/{role_name}", status_code=204)
async def delete_role(
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Delete a role (requires admin)"""
    # Check if user has admin role
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    is_admin = any(role.name == "admin" for role in roles)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete roles",
        )

    # Get role
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with name '{role_name}' not found",
        )

    # Cannot delete admin or user roles
    if role.name in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete system role '{role.name}'",
        )

    # Delete role
    db.delete(role)
    db.commit()

    return None


# Add MFA endpoints
@app.post("/api/auth/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)
):
    """Setup MFA for user"""
    # Generate secret
    secret = pyotp.random_base32()

    # Generate QR code URL
    totp = pyotp.TOTP(secret)
    qr_code_url = totp.provisioning_uri(
        name=current_user.email, issuer_name="NoxSuite")

    # Generate backup codes
    backup_codes = []
    for _ in range(10):
        code = base64.b32encode(os.urandom(5)).decode("utf-8")
        code = code.replace("=", "").lower()
        backup_codes.append(code)

    # Update user
    current_user.mfa_secret = secret
    current_user.backup_codes = json.dumps(backup_codes)
    db.commit()

    return MFASetupResponse(
        secret=secret, qr_code_url=qr_code_url, backup_codes=backup_codes
    )


@app.post("/api/auth/verify-mfa", response_model=Token)
async def verify_mfa_challenge(
    mfa_verification: MFAVerification,
    request: Request,
    db: SessionLocal = Depends(get_db),
):
    """Verify MFA code and complete login"""
    import secrets

    from noxsuite_fastapi_server import (
        Token,
        create_access_token,
        create_refresh_token,
        log_audit_event,
    )

    # Find user from pending MFA session
    session_id = mfa_verification.session_id

    # In a production system, we would store the session and associated user
    # For this demo, we'll extract the user ID from the session ID
    try:
        # Extract user ID from session (in real implementation, lookup from Redis/DB)
        parts = session_id.split("_")
        if len(parts) < 2:
            raise ValueError("Invalid session format")

        user_id = int(parts[0])
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            log_audit_event(
                db,
                None,
                "mfa_verification_failed",
                "auth",
                {"reason": "user_not_found", "session_id": session_id},
                request,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA session"
            )
    except (ValueError, IndexError):
        log_audit_event(
            db,
            None,
            "mfa_verification_failed",
            "auth",
            {"reason": "invalid_session", "session_id": session_id},
            request,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA session"
        )

    # Verify MFA code
    if not verify_totp(user.mfa_secret, mfa_verification.code):
        log_audit_event(
            db,
            user.id,
            "mfa_verification_failed",
            "auth",
            {"reason": "invalid_code"},
            request,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code"
        )

    # Create tokens with unique id to prevent collisions
    try:
        unique_id = secrets.token_hex(8)
        access_token = create_access_token(
            data={"sub": str(user.id), "jti": unique_id})
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "jti": unique_id}
        )

        # Create session record with unique session token
        if UserSession:
            session_unique_id = secrets.token_hex(16)  # Additional uniqueness
            session_token = (
                f"{session_unique_id}_{user.id}_{int(datetime.utcnow().timestamp())}"
            )

            print(f"[DEBUG] Creating session with token: {session_token}")
            session = UserSession(
                user_id=user.id,
                session_token=session_token,
                refresh_token=f"{unique_id}_{refresh_token[:40]}",
                expires_at=datetime.utcnow() + timedelta(minutes=30),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "")[:255],
            )
            db.add(session)
            print(f"[DEBUG] Session added to db, attempting commit...")

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        print(f"[DEBUG] Database commit successful!")

        log_audit_event(db, user.id, "mfa_verification_success",
                        "auth", {}, request)
    except Exception as e:
        print(f"[ERROR] Exception in MFA verification: {e}")
        print(f"[ERROR] Exception type: {type(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"MFA verification failed: {str(e)}"
        )

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@app.post("/api/auth/mfa/verify")
async def verify_mfa_code(
    verification: MFAVerify,
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Verify MFA code"""
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not set up"
        )

    # Verify code
    if verify_totp(current_user.mfa_secret, verification.code):
        return {"message": "MFA code verified"}

    # Check backup codes
    if current_user.backup_codes:
        backup_codes = json.loads(current_user.backup_codes)
        if verification.code in backup_codes:
            # Remove used backup code
            backup_codes.remove(verification.code)
            current_user.backup_codes = json.dumps(backup_codes)
            db.commit()
            return {"message": "Backup code verified"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
    )


@app.post("/api/auth/mfa/enable")
async def enable_mfa(
    mfa_enable: MFAEnable,
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Enable MFA for user"""
    # Verify code
    if current_user.mfa_secret != mfa_enable.secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA secret does not match"
        )

    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(mfa_enable.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
        )

    # Enable MFA
    current_user.mfa_enabled = True
    db.commit()

    return {"message": "MFA enabled"}


@app.post("/api/auth/mfa/disable")
async def disable_mfa(
    verification: MFAVerify,
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Disable MFA for user"""
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not enabled"
        )

    # Verify code
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(verification.code):
        # Check backup codes
        if current_user.backup_codes:
            backup_codes = json.loads(current_user.backup_codes)
            if verification.code not in backup_codes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
                )
            # Remove used backup code
            backup_codes.remove(verification.code)
            current_user.backup_codes = json.dumps(backup_codes)

    # Disable MFA
    current_user.mfa_enabled = False
    db.commit()

    return {"message": "MFA disabled"}


# Add TestSprite compatibility endpoints
@app.get("/admin/roles")
async def admin_roles_compat(
    current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)
):
    """Admin roles endpoint for TestSprite compatibility"""
    # Check if user has admin role
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    is_admin = any(role.name == "admin" for role in roles)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view roles"
        )

    # Get all roles
    all_roles = db.query(Role).all()
    return [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": json.loads(role.permissions),
        }
        for role in all_roles
    ]


@app.post("/admin/roles", status_code=201)
async def create_role_compat(
    role_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Create role endpoint for TestSprite compatibility"""
    # Check if user has admin role
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    is_admin = any(role.name == "admin" for role in roles)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create roles",
        )

    # Check if role already exists
    existing_role = db.query(Role).filter(
        Role.name == role_data["name"]).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_data['name']}' already exists",
        )

    # Create new role
    new_role = Role(
        name=role_data["name"],
        description=role_data["description"],
        permissions=json.dumps(role_data["permissions"]),
        created_at=datetime.utcnow(),
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return {
        "id": new_role.id,
        "name": new_role.name,
        "description": new_role.description,
        "permissions": json.loads(new_role.permissions),
    }


@app.get("/users")
async def get_users_compat(
    current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)
):
    """Users endpoint for TestSprite compatibility"""
    # Get all users
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "mfa_enabled": user.mfa_enabled,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]


@app.post("/users", status_code=201)
async def create_user_compat(
    user_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Create user endpoint for TestSprite compatibility"""
    # Check if user has admin role
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    is_admin = any(role.name == "admin" for role in roles)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create users",
        )

    # Check if user already exists
    existing_user = (
        db.query(User)
        .filter(
            (User.username == user_data["username"])
            | (User.email == user_data["email"])
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    # Create new user
    new_user = User(
        username=user_data["username"],
        email=user_data["email"],
        password_hash=User.hash_password(user_data["password"]),
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Assign roles
    if "roles" in user_data and user_data["roles"]:
        for role_name in user_data["roles"]:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                user_role = UserRole(
                    user_id=new_user.id, role_id=role.id, created_at=datetime.utcnow()
                )
                db.add(user_role)
        db.commit()

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "mfa_enabled": new_user.mfa_enabled,
        "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
    }
