"""
Auth Integration Module for NoxSuite
Integrates JWT authentication, MFA, and RBAC into a unified authentication system
"""

import json
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from auth.jwt_utils import JWTManager
from auth.mfa_service import TOTPService
from auth.rbac_service import Permission, RBACService, Role


class AuthStatus(str, Enum):
    """Authentication status enumerations"""

    SUCCESS = "success"
    FAILED = "failed"
    MFA_REQUIRED = "mfa_required"
    MFA_SETUP_REQUIRED = "mfa_setup_required"
    UNAUTHORIZED = "unauthorized"
    EXPIRED = "expired"


class AuthIntegrationService:
    """
    Integrated authentication service that combines JWT, MFA, and RBAC
    """

    def __init__(
        self,
        jwt_secret: str,
        mfa_enabled: bool = True,
        token_expiry: int = 3600,
        refresh_token_expiry: int = 86400 * 7,
    ):
        """
        Initialize the integrated auth service

        Args:
            jwt_secret: Secret for JWT token generation/validation
            mfa_enabled: Whether MFA is enabled system-wide
            token_expiry: Access token expiry in seconds (default: 1 hour)
            refresh_token_expiry: Refresh token expiry in seconds (default: 7 days)
        """
        self.jwt_manager = JWTManager(
            secret=jwt_secret,
            access_token_expiry=token_expiry,
            refresh_token_expiry=refresh_token_expiry,
        )
        self.totp_service = TOTPService()
        self.rbac_service = RBACService()
        self.mfa_enabled = mfa_enabled

        # User sessions storage
        # user_id -> session info
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with username and password

        Args:
            username: User's username
            password: User's password

        Returns:
            Authentication result with status and optional token information
        """
        # In a real implementation, this would validate against the user database
        # For demo purposes, we'll assume validation happens elsewhere
        user_id = f"user_{hash(username) % 10000}"  # Simulated user ID

        # Check if MFA is required for this user
        if self.mfa_enabled and self.totp_service.is_mfa_enabled(user_id):
            return {
                "status": AuthStatus.MFA_REQUIRED,
                "user_id": user_id,
                "message": "MFA verification required",
            }

        # If no MFA or not enabled for user, generate tokens
        return self._generate_auth_tokens(user_id)

    def verify_mfa(self, user_id: str, totp_code: str) -> Dict[str, Any]:
        """
        Verify MFA code and complete authentication

        Args:
            user_id: User ID
            totp_code: TOTP code entered by user

        Returns:
            Authentication result with status and token information if successful
        """
        # Verify the TOTP code
        if not self.totp_service.verify_totp(user_id, totp_code):
            return {"status": AuthStatus.FAILED, "message": "Invalid MFA code"}

        # TOTP verified, generate tokens
        return self._generate_auth_tokens(user_id)

    def _generate_auth_tokens(self, user_id: str) -> Dict[str, Any]:
        """
        Generate JWT tokens for authenticated user

        Args:
            user_id: User ID

        Returns:
            Authentication result with tokens
        """
        # Get user roles and permissions for token claims
        roles = [
            role.name for role in self.rbac_service.get_user_roles(user_id)]
        permissions = [
            p.value for p in self.rbac_service.get_user_permissions(user_id)]

        # Add claims to token
        claims = {"user_id": user_id, "roles": roles,
                  "permissions": permissions}

        # Generate tokens
        access_token = self.jwt_manager.create_access_token(claims)
        refresh_token = self.jwt_manager.create_refresh_token(claims)

        # Store session info
        session_id = f"session_{int(time.time())}_{hash(user_id) % 10000}"
        self.active_sessions[user_id] = {
            "session_id": session_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": int(time.time()),
        }

        return {
            "status": AuthStatus.SUCCESS,
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.jwt_manager.access_token_expiry,
            "roles": roles,
            "permissions": permissions,
        }

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            New access token if refresh token is valid
        """
        # Verify refresh token
        payload = self.jwt_manager.verify_refresh_token(refresh_token)
        if not payload:
            return {"status": AuthStatus.FAILED, "message": "Invalid refresh token"}

        user_id = payload.get("user_id")
        if not user_id:
            return {"status": AuthStatus.FAILED, "message": "Invalid token payload"}

        # Check if refresh token matches stored one
        if (
            user_id not in self.active_sessions
            or self.active_sessions[user_id].get("refresh_token") != refresh_token
        ):
            return {
                "status": AuthStatus.FAILED,
                "message": "Refresh token has been revoked",
            }

        # Get fresh user roles and permissions
        roles = [
            role.name for role in self.rbac_service.get_user_roles(user_id)]
        permissions = [
            p.value for p in self.rbac_service.get_user_permissions(user_id)]

        # Add claims to token
        claims = {"user_id": user_id, "roles": roles,
                  "permissions": permissions}

        # Generate new access token
        access_token = self.jwt_manager.create_access_token(claims)

        # Update session
        self.active_sessions[user_id]["access_token"] = access_token
        self.active_sessions[user_id]["refreshed_at"] = int(time.time())

        return {
            "status": AuthStatus.SUCCESS,
            "user_id": user_id,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.jwt_manager.access_token_expiry,
        }

    def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify an access token

        Args:
            access_token: Access token

        Returns:
            Token verification result
        """
        # Verify token
        payload = self.jwt_manager.verify_access_token(access_token)
        if not payload:
            return {"status": AuthStatus.FAILED, "message": "Invalid access token"}

        user_id = payload.get("user_id")
        if not user_id:
            return {"status": AuthStatus.FAILED, "message": "Invalid token payload"}

        # Check if token has been revoked
        if (
            user_id not in self.active_sessions
            or self.active_sessions[user_id].get("access_token") != access_token
        ):
            return {
                "status": AuthStatus.UNAUTHORIZED,
                "message": "Token has been revoked",
            }

        return {
            "status": AuthStatus.SUCCESS,
            "user_id": user_id,
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", []),
        }

    def logout(self, user_id: str) -> Dict[str, Any]:
        """
        Log out a user by invalidating their session

        Args:
            user_id: User ID

        Returns:
            Logout result
        """
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            return {"status": AuthStatus.SUCCESS, "message": "Logged out successfully"}

        return {"status": AuthStatus.FAILED, "message": "No active session found"}

    def check_permission(self, token: str, required_permission: Permission) -> bool:
        """
        Check if a token has a specific permission

        Args:
            token: Access token
            required_permission: Required permission

        Returns:
            True if token has permission, False otherwise
        """
        # Verify token
        verify_result = self.verify_token(token)
        if verify_result["status"] != AuthStatus.SUCCESS:
            return False

        # Get permissions from token
        token_permissions = verify_result.get("permissions", [])

        # Check if required permission is in token permissions
        return required_permission.value in token_permissions

    def check_role(self, token: str, required_role: str) -> bool:
        """
        Check if a token has a specific role

        Args:
            token: Access token
            required_role: Required role

        Returns:
            True if token has role, False otherwise
        """
        # Verify token
        verify_result = self.verify_token(token)
        if verify_result["status"] != AuthStatus.SUCCESS:
            return False

        # Get roles from token
        token_roles = verify_result.get("roles", [])

        # Check if required role is in token roles
        return required_role in token_roles

    def setup_mfa(self, user_id: str) -> Dict[str, Any]:
        """
        Set up MFA for a user

        Args:
            user_id: User ID

        Returns:
            MFA setup information
        """
        if not self.mfa_enabled:
            return {
                "status": AuthStatus.FAILED,
                "message": "MFA is not enabled for this system",
            }

        # Check if MFA is already set up
        if self.totp_service.is_mfa_enabled(user_id):
            return {
                "status": AuthStatus.FAILED,
                "message": "MFA is already set up for this user",
            }

        # Generate TOTP secret
        secret = self.totp_service.generate_totp_secret()

        # Get provisioning URI for QR code
        uri = self.totp_service.get_provisioning_uri(
            user_id, secret, "NoxSuite")

        # Generate backup codes
        backup_codes = self.totp_service.generate_backup_codes(user_id)

        return {
            "status": AuthStatus.SUCCESS,
            "secret": secret,
            "provisioning_uri": uri,
            "backup_codes": backup_codes,
            "message": "MFA setup initiated. Scan the QR code and verify to complete setup.",
        }

    def complete_mfa_setup(
        self, user_id: str, secret: str, totp_code: str
    ) -> Dict[str, Any]:
        """
        Complete MFA setup by verifying the first TOTP code

        Args:
            user_id: User ID
            secret: TOTP secret
            totp_code: TOTP code entered by user

        Returns:
            MFA setup completion result
        """
        # Verify the TOTP code
        if not self.totp_service.verify_totp_with_secret(secret, totp_code):
            return {"status": AuthStatus.FAILED, "message": "Invalid TOTP code"}

        # Enable MFA for the user
        self.totp_service.enable_mfa(user_id, secret)

        return {
            "status": AuthStatus.SUCCESS,
            "message": "MFA setup completed successfully",
        }

    def disable_mfa(self, user_id: str, verification_code: str) -> Dict[str, Any]:
        """
        Disable MFA for a user

        Args:
            user_id: User ID
            verification_code: TOTP code or backup code for verification

        Returns:
            MFA disabling result
        """
        # Check if MFA is enabled
        if not self.totp_service.is_mfa_enabled(user_id):
            return {
                "status": AuthStatus.FAILED,
                "message": "MFA is not enabled for this user",
            }

        # Verify TOTP code or backup code
        if not (
            self.totp_service.verify_totp(user_id, verification_code)
            or self.totp_service.verify_backup_code(user_id, verification_code)
        ):
            return {"status": AuthStatus.FAILED, "message": "Invalid verification code"}

        # Disable MFA
        self.totp_service.disable_mfa(user_id)

        return {"status": AuthStatus.SUCCESS, "message": "MFA disabled successfully"}


# Example usage
if __name__ == "__main__":
    import os
    # Create integrated auth service
    jwt_secret = os.getenv("JWT_SECRET", "PLEASE_SET_JWT_SECRET_IN_ENVIRONMENT")
    if jwt_secret == "PLEASE_SET_JWT_SECRET_IN_ENVIRONMENT":
        print("WARNING: Using default JWT secret. Set JWT_SECRET environment variable for production!")
    
    auth_service = AuthIntegrationService(
        jwt_secret=jwt_secret, mfa_enabled=True
    )

    # Set up RBAC roles for test users
    auth_service.rbac_service.assign_role_to_user("user_1234", "admin")
    auth_service.rbac_service.assign_role_to_user("user_5678", "user")

    # Simulate authentication flow
    print("Authentication Flow:")

    # 1. Authenticate with username/password
    auth_result = auth_service.authenticate("admin@example.com", "password")
    print(f"Initial auth result: {auth_result['status']}")

    # If MFA is required, simulate MFA verification
    if auth_result["status"] == AuthStatus.MFA_REQUIRED:
        user_id = auth_result["user_id"]
        # In real app, user would enter their TOTP code
        mfa_result = auth_service.verify_mfa(
            user_id, "123456")  # Simulated TOTP code
        print(f"MFA verification result: {mfa_result['status']}")
        if mfa_result["status"] == AuthStatus.SUCCESS:
            auth_result = mfa_result

    # If authentication successful, get token
    if auth_result["status"] == AuthStatus.SUCCESS:
        access_token = auth_result["access_token"]
        refresh_token = auth_result["refresh_token"]

        # Verify the token
        verify_result = auth_service.verify_token(access_token)
        print(f"Token verification: {verify_result['status']}")

        # Check permissions
        has_admin_access = auth_service.check_permission(
            access_token, Permission.ADMIN_ACCESS
        )
        print(f"Has admin access: {has_admin_access}")

        # Refresh token
        refresh_result = auth_service.refresh_token(refresh_token)
        print(f"Token refresh: {refresh_result['status']}")

        # Logout
        logout_result = auth_service.logout(auth_result["user_id"])
        print(f"Logout: {logout_result['status']}")

    # MFA Setup demo
    print("\nMFA Setup Flow:")
    user_id = "user_5678"

    # 1. Set up MFA
    mfa_setup = auth_service.setup_mfa(user_id)
    print(f"MFA Setup initiated: {mfa_setup['status']}")

    if mfa_setup["status"] == AuthStatus.SUCCESS:
        secret = mfa_setup["secret"]
        # In real app, user would scan QR code and enter TOTP
        complete_setup = auth_service.complete_mfa_setup(
            user_id, secret, "123456"
        )  # Simulated TOTP
        print(f"MFA Setup completion: {complete_setup['status']}")

        # Verify MFA is now required for login
        auth_result = auth_service.authenticate("user@example.com", "password")
        print(f"Auth after MFA setup: {auth_result['status']}")

        # Disable MFA
        disable_result = auth_service.disable_mfa(
            user_id, "123456")  # Simulated TOTP
        print(f"MFA Disable: {disable_result['status']}")
