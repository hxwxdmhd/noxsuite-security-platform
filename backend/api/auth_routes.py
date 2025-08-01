"""
API Authentication Routes for NoxSuite
Implements login, logout, token refresh, and MFA endpoints
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from datetime import datetime

from auth.auth_integration import AuthIntegrationService, AuthStatus
from auth.auth_middleware import AuthMiddleware, oauth2_scheme

# Initialize router
router = APIRouter(tags=["authentication"])

# Initialize auth service (to be injected in main app)
auth_service = None
auth_middleware = None

def initialize(auth_svc: AuthIntegrationService):
    """
    Initialize auth services for the router
    
    Args:
        auth_svc: Auth service instance
    """
    global auth_service, auth_middleware
    auth_service = auth_svc
    auth_middleware = AuthMiddleware(auth_service)

# Request/Response models
class LoginRequest(BaseModel):
    """Login request body"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

class MFAVerifyRequest(BaseModel):
    """MFA verification request body"""
    user_id: str = Field(..., description="User ID")
    totp_code: str = Field(..., description="TOTP code")

class MFASetupRequest(BaseModel):
    """MFA setup request body"""
    user_id: str = Field(..., description="User ID")
    secret: str = Field(..., description="TOTP secret")
    totp_code: str = Field(..., description="First TOTP code for verification")

class MFADisableRequest(BaseModel):
    """MFA disable request body"""
    verification_code: str = Field(..., description="TOTP code or backup code")

class RefreshRequest(BaseModel):
    """Token refresh request body"""
    refresh_token: str = Field(..., description="Refresh token")

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    expires_in: int
    roles: list
    permissions: list

class MessageResponse(BaseModel):
    """Generic message response"""
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

class MFASetupResponse(BaseModel):
    """MFA setup response"""
    status: str
    secret: str
    provisioning_uri: str
    backup_codes: list
    message: str

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    """
    Authenticate user with username and password
    
    Args:
        request: Login request with username and password
    
    Returns:
        JWT tokens if authentication successful
    
    Raises:
        HTTPException: If authentication fails
    """
    auth_result = auth_service.authenticate(request.username, request.password)
    
    if auth_result["status"] == AuthStatus.MFA_REQUIRED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": "mfa_required",
                "user_id": auth_result["user_id"],
                "message": "MFA verification required"
            }
        )
    
    if auth_result["status"] != AuthStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return auth_result

@router.post("/mfa/verify", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def verify_mfa(request: MFAVerifyRequest):
    """
    Verify MFA code and complete authentication
    
    Args:
        request: MFA verification request
    
    Returns:
        JWT tokens if verification successful
    
    Raises:
        HTTPException: If verification fails
    """
    auth_result = auth_service.verify_mfa(request.user_id, request.totp_code)
    
    if auth_result["status"] != AuthStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    return auth_result

@router.post("/token/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token
    
    Args:
        request: Refresh token request
    
    Returns:
        New access token
    
    Raises:
        HTTPException: If refresh token is invalid
    """
    refresh_result = auth_service.refresh_token(request.refresh_token)
    
    if refresh_result["status"] != AuthStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=refresh_result.get("message", "Invalid refresh token")
        )
    
    return refresh_result

@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(user: Dict[str, Any] = Depends(auth_middleware.get_current_user)):
    """
    Log out current user
    
    Args:
        user: Current authenticated user
    
    Returns:
        Logout confirmation
    """
    logout_result = auth_service.logout(user["user_id"])
    
    return {
        "status": logout_result["status"],
        "message": logout_result.get("message", "Logged out successfully")
    }

@router.post("/mfa/setup", response_model=MFASetupResponse, status_code=status.HTTP_200_OK)
async def setup_mfa(user: Dict[str, Any] = Depends(auth_middleware.get_current_user)):
    """
    Set up MFA for current user
    
    Args:
        user: Current authenticated user
    
    Returns:
        MFA setup information
    
    Raises:
        HTTPException: If MFA setup fails
    """
    setup_result = auth_service.setup_mfa(user["user_id"])
    
    if setup_result["status"] != AuthStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=setup_result.get("message", "Failed to set up MFA")
        )
    
    return setup_result

@router.post("/mfa/setup/complete", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def complete_mfa_setup(
    request: MFASetupRequest, 
    user: Dict[str, Any] = Depends(auth_middleware.get_current_user)
):
    """
    Complete MFA setup by verifying TOTP code
    
    Args:
        request: MFA setup completion request
        user: Current authenticated user
    
    Returns:
        Setup completion confirmation
    
    Raises:
        HTTPException: If setup completion fails
    """
    # Verify user_id matches authenticated user
    if request.user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot set up MFA for different user"
        )
    
    result = auth_service.complete_mfa_setup(request.user_id, request.secret, request.totp_code)
    
    if result["status"] != AuthStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to complete MFA setup")
        )
    
    return {
        "status": result["status"],
        "message": result.get("message", "MFA setup completed successfully")
    }

@router.post("/mfa/disable", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def disable_mfa(
    request: MFADisableRequest,
    user: Dict[str, Any] = Depends(auth_middleware.get_current_user)
):
    """
    Disable MFA for current user
    
    Args:
        request: MFA disable request
        user: Current authenticated user
    
    Returns:
        Disable confirmation
    
    Raises:
        HTTPException: If MFA disable fails
    """
    result = auth_service.disable_mfa(user["user_id"], request.verification_code)
    
    if result["status"] != AuthStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to disable MFA")
        )
    
    return {
        "status": result["status"],
        "message": result.get("message", "MFA disabled successfully")
    }

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(user: Dict[str, Any] = Depends(auth_middleware.get_current_user)):
    """
    Get current authenticated user information
    
    Args:
        user: Current authenticated user
    
    Returns:
        User information
    """
    return {
        "user_id": user["user_id"],
        "roles": user.get("roles", []),
        "permissions": user.get("permissions", [])
    }
