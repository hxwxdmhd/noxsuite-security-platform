"""
API Authentication Middleware for NoxSuite
Implements FastAPI dependencies for authentication and authorization
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)

from auth.auth_integration import AuthIntegrationService, AuthStatus, Permission

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# HTTP Bearer scheme for token authentication in headers
security = HTTPBearer()


class AuthMiddleware:
    """Authentication and authorization middleware for FastAPI"""

    def __init__(self, auth_service: AuthIntegrationService):
        """
        Initialize auth middleware

        Args:
            auth_service: Integrated authentication service
        """
        self.auth_service = auth_service

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme)
    ) -> Dict[str, Any]:
        """
        Get current authenticated user from token

        Args:
            token: JWT access token

        Returns:
            User information from token

        Raises:
            HTTPException: If token is invalid or expired
        """
        verify_result = self.auth_service.verify_token(token)

        if verify_result["status"] != AuthStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=verify_result.get(
                    "message", "Invalid or expired token"),
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": verify_result["user_id"],
            "roles": verify_result.get("roles", []),
            "permissions": verify_result.get("permissions", []),
        }

    async def get_optional_user(
        self, token: Optional[str] = Depends(oauth2_scheme)
    ) -> Optional[Dict[str, Any]]:
        """
        Get current user if authenticated, None otherwise

        Args:
            token: JWT access token

        Returns:
            User information or None
        """
        if not token:
            return None

        try:
            return await self.get_current_user(token)
        except HTTPException:
            return None

    async def get_current_user_from_header(
        self, credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> Dict[str, Any]:
        """
        Get current user from Authorization header

        Args:
            credentials: HTTP Authorization credentials

        Returns:
            User information

        Raises:
            HTTPException: If token is invalid or expired
        """
        return await self.get_current_user(credentials.credentials)

    def require_permission(self, permission: Permission):
        """
        Dependency for requiring a specific permission

        Args:
            permission: Required permission

        Returns:
            Dependency function
        """

        async def permission_dependency(
            user: Dict[str, Any] = Depends(self.get_current_user),
        ) -> Dict[str, Any]:
            """
            Check if user has required permission

            Args:
                user: User information

            Returns:
                User information if authorized

            Raises:
                HTTPException: If user lacks required permission
            """
            user_permissions = user.get("permissions", [])
            if permission.value not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not authorized. Required permission: {permission.value}",
                )
            return user

        return permission_dependency

    def require_permissions(
        self, permissions: List[Permission], require_all: bool = True
    ):
        """
        Dependency for requiring multiple permissions

        Args:
            permissions: List of required permissions
            require_all: If True, all permissions are required; if False, any permission is sufficient

        Returns:
            Dependency function
        """

        async def permissions_dependency(
            user: Dict[str, Any] = Depends(self.get_current_user),
        ) -> Dict[str, Any]:
            """
            Check if user has required permissions

            Args:
                user: User information

            Returns:
                User information if authorized

            Raises:
                HTTPException: If user lacks required permissions
            """
            user_permissions = user.get("permissions", [])

            if require_all:
                # All permissions required
                missing = [
                    p.value for p in permissions if p.value not in user_permissions
                ]
                if missing:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized. Missing permissions: {', '.join(missing)}",
                    )
            else:
                # Any permission is sufficient
                if not any(p.value in user_permissions for p in permissions):
                    required = [p.value for p in permissions]
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized. Need any of these permissions: {', '.join(required)}",
                    )

            return user

        return permissions_dependency

    def require_role(self, role: str):
        """
        Dependency for requiring a specific role

        Args:
            role: Required role

        Returns:
            Dependency function
        """

        async def role_dependency(
            user: Dict[str, Any] = Depends(self.get_current_user),
        ) -> Dict[str, Any]:
            """
            Check if user has required role

            Args:
                user: User information

            Returns:
                User information if authorized

            Raises:
                HTTPException: If user lacks required role
            """
            user_roles = user.get("roles", [])
            if role not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not authorized. Required role: {role}",
                )
            return user

        return role_dependency

    def require_roles(self, roles: List[str], require_all: bool = False):
        """
        Dependency for requiring multiple roles

        Args:
            roles: List of required roles
            require_all: If True, all roles are required; if False, any role is sufficient

        Returns:
            Dependency function
        """

        async def roles_dependency(
            user: Dict[str, Any] = Depends(self.get_current_user),
        ) -> Dict[str, Any]:
            """
            Check if user has required roles

            Args:
                user: User information

            Returns:
                User information if authorized

            Raises:
                HTTPException: If user lacks required roles
            """
            user_roles = user.get("roles", [])

            if require_all:
                # All roles required
                missing = [r for r in roles if r not in user_roles]
                if missing:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized. Missing roles: {', '.join(missing)}",
                    )
            else:
                # Any role is sufficient
                if not any(r in user_roles for r in roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized. Need any of these roles: {', '.join(roles)}",
                    )

            return user

        return roles_dependency

    def permission_required(self, permission: Permission):
        """
        Decorator for requiring a specific permission

        Args:
            permission: Required permission

        Returns:
            Decorator function
        """

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract token from kwargs
                token = kwargs.get("token")
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Verify permission
                if not self.auth_service.check_permission(token, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized. Required permission: {permission.value}",
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator

    def role_required(self, role: str):
        """
        Decorator for requiring a specific role

        Args:
            role: Required role

        Returns:
            Decorator function
        """

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract token from kwargs
                token = kwargs.get("token")
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Verify role
                if not self.auth_service.check_role(token, role):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized. Required role: {role}",
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator
