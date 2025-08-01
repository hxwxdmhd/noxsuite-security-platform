#!/usr/bin/env python3
"""
RBAC and MFA Extensions for NoxSuite
===================================
Adds RBAC and MFA functionality to the NoxSuite API.
"""

    from fastapi import Body, Depends, HTTPException, Request, status
    from fastapi.responses import JSONResponse
    import secrets
from datetime import datetime, timedelta
import json
import os
import secrets
import sys

        import traceback
    from pydantic import BaseModel, Field
    from typing import List, Optional
import base64
import pyotp

    from noxsuite_fastapi_server import (


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
