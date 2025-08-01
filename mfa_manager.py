#!/usr/bin/env python3
"""
NoxSuite MFA Manager
===================
Production-ready Multi-Factor Authentication with TOTP support.
Implements RFC 6238 TOTP with QR code generation and backup codes.
"""

import os
import secrets
import qrcode
import base64
import io
from typing import List, Optional, Tuple
import pyotp
import argon2
from datetime import datetime
from sqlalchemy.orm import Session

# Import database models
from mariadb_dev_setup import User, get_db_session


class MFAManager:
    """Multi-Factor Authentication Manager"""
    
    def __init__(self, issuer: str = "NoxSuite Security Platform"):
        self.issuer = issuer
        self.ph = argon2.PasswordHasher()
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, username: str) -> str:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=self.issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 string
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_backup_codes(self, count: int = 8) -> List[str]:
        """Generate backup recovery codes"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes
    
    def hash_backup_codes(self, codes: List[str]) -> List[str]:
        """Hash backup codes using Argon2"""
        return [self.ph.hash(code) for code in codes]
    
    def verify_totp(self, secret: str, token: str, window: int = 1) -> bool:
        """Verify TOTP token with time window tolerance"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception:
            return False
    
    def verify_backup_code(self, hashed_codes: List[str], provided_code: str) -> Tuple[bool, Optional[str]]:
        """Verify backup code and return which one was used"""
        for i, hashed_code in enumerate(hashed_codes):
            try:
                self.ph.verify(hashed_code, provided_code)
                return True, hashed_code
            except argon2.exceptions.VerifyMismatchError:
                continue
        return False, None
    
    def setup_mfa_for_user(self, user_id: int, db: Session) -> dict:
        """Setup MFA for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if user.mfa_enabled:
            raise ValueError("MFA already enabled for this user")
        
        # Generate secret and backup codes
        secret = self.generate_secret()
        backup_codes = self.generate_backup_codes()
        hashed_backup_codes = self.hash_backup_codes(backup_codes)
        
        # Generate QR code
        qr_code = self.generate_qr_code(secret, user.username)
        
        # Store in database (don't enable MFA yet - user must verify first)
        user.mfa_secret = secret
        user.backup_codes = hashed_backup_codes
        db.commit()
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "setup_complete": False
        }
    
    def complete_mfa_setup(self, user_id: int, token: str, db: Session) -> bool:
        """Complete MFA setup by verifying the first token"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_secret:
            return False
        
        # Verify the provided token
        if self.verify_totp(user.mfa_secret, token):
            user.mfa_enabled = True
            db.commit()
            return True
        
        return False
    
    def disable_mfa(self, user_id: int, verification_token: str, db: Session) -> bool:
        """Disable MFA for a user (requires verification)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_enabled:
            return False
        
        # Verify token or backup code
        if self.verify_mfa_token(user_id, verification_token, db):
            user.mfa_enabled = False
            user.mfa_secret = None
            user.backup_codes = None
            db.commit()
            return True
        
        return False
    
    def verify_mfa_token(self, user_id: int, token: str, db: Session, consume_backup: bool = True) -> bool:
        """Verify MFA token (TOTP or backup code)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_enabled:
            return False
        
        # First try TOTP
        if self.verify_totp(user.mfa_secret, token):
            return True
        
        # Then try backup codes
        if user.backup_codes:
            is_valid, used_code = self.verify_backup_code(user.backup_codes, token)
            if is_valid and consume_backup:
                # Remove used backup code
                user.backup_codes = [code for code in user.backup_codes if code != used_code]
                db.commit()
            return is_valid
        
        return False
    
    def regenerate_backup_codes(self, user_id: int, verification_token: str, db: Session) -> Optional[List[str]]:
        """Regenerate backup codes for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_enabled:
            return None
        
        # Verify current access
        if not self.verify_mfa_token(user_id, verification_token, db, consume_backup=False):
            return None
        
        # Generate new backup codes
        backup_codes = self.generate_backup_codes()
        hashed_backup_codes = self.hash_backup_codes(backup_codes)
        
        user.backup_codes = hashed_backup_codes
        db.commit()
        
        return backup_codes
    
    def get_mfa_status(self, user_id: int, db: Session) -> dict:
        """Get MFA status for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        backup_codes_count = len(user.backup_codes) if user.backup_codes else 0
        
        return {
            "mfa_enabled": user.mfa_enabled,
            "has_secret": bool(user.mfa_secret),
            "backup_codes_remaining": backup_codes_count,
            "setup_complete": user.mfa_enabled and user.mfa_secret
        }


# FastAPI endpoints for MFA management
def create_mfa_endpoints(app, mfa_manager: MFAManager):
    """Create FastAPI endpoints for MFA management"""
    from fastapi import APIRouter, Depends, HTTPException, status
    from pydantic import BaseModel
    from typing import List
    
    router = APIRouter(prefix="/api/mfa", tags=["MFA"])
    
    class MFASetupResponse(BaseModel):
        qr_code: str
        backup_codes: List[str]
        secret: str
        message: str
    
    class MFAVerifyRequest(BaseModel):
        token: str
    
    class MFAStatusResponse(BaseModel):
        mfa_enabled: bool
        has_secret: bool
        backup_codes_remaining: int
        setup_complete: bool
    
    @router.get("/status", response_model=MFAStatusResponse)
    async def get_mfa_status(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Get MFA status for current user"""
        status = mfa_manager.get_mfa_status(current_user.id, db)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    
    @router.post("/setup", response_model=MFASetupResponse)
    async def setup_mfa(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Setup MFA for current user"""
        try:
            setup_data = mfa_manager.setup_mfa_for_user(current_user.id, db)
            return MFASetupResponse(
                qr_code=setup_data["qr_code"],
                backup_codes=setup_data["backup_codes"],
                secret=setup_data["secret"],
                message="MFA setup initiated. Please verify with your authenticator app."
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post("/setup/complete")
    async def complete_mfa_setup(
        request: MFAVerifyRequest,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Complete MFA setup by verifying token"""
        if mfa_manager.complete_mfa_setup(current_user.id, request.token, db):
            return {"message": "MFA setup completed successfully"}
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    @router.post("/verify")
    async def verify_mfa(
        request: MFAVerifyRequest,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Verify MFA token"""
        if mfa_manager.verify_mfa_token(current_user.id, request.token, db):
            return {"message": "MFA verification successful"}
        raise HTTPException(status_code=400, detail="Invalid MFA token")
    
    @router.post("/disable")
    async def disable_mfa(
        request: MFAVerifyRequest,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Disable MFA for current user"""
        if mfa_manager.disable_mfa(current_user.id, request.token, db):
            return {"message": "MFA disabled successfully"}
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    @router.post("/backup-codes/regenerate")
    async def regenerate_backup_codes(
        request: MFAVerifyRequest,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Regenerate backup codes"""
        codes = mfa_manager.regenerate_backup_codes(current_user.id, request.token, db)
        if codes:
            return {"backup_codes": codes, "message": "Backup codes regenerated"}
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    app.include_router(router)


# Global MFA manager instance
mfa_manager = MFAManager()

if __name__ == "__main__":
    # Test MFA functionality
    print("🔐 Testing NoxSuite MFA Manager...")
    
    # Test secret generation
    secret = mfa_manager.generate_secret()
    print(f"✅ Generated TOTP secret: {secret}")
    
    # Test backup code generation
    backup_codes = mfa_manager.generate_backup_codes()
    print(f"✅ Generated backup codes: {backup_codes}")
    
    # Test TOTP verification (will fail since no real token)
    test_token = "123456"
    is_valid = mfa_manager.verify_totp(secret, test_token)
    print(f"✅ TOTP verification test (expected False): {is_valid}")
    
    print("🎯 MFA Manager ready for integration!")