#!/usr/bin/env python3
"""
NoxSuite Access Control & RBAC System
Role-based access control with permission validation
"""

import logging
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, HTTPException


class Permission(str, Enum):
    """System permissions"""

    # System permissions
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_ADMIN = "system:admin"

    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # Network management
    NETWORK_READ = "network:read"
    NETWORK_WRITE = "network:write"
    NETWORK_SCAN = "network:scan"

    # Security management
    SECURITY_READ = "security:read"
    SECURITY_WRITE = "security:write"
    SECURITY_AUDIT = "security:audit"

    # Plugin management
    PLUGIN_READ = "plugin:read"
    PLUGIN_WRITE = "plugin:write"
    PLUGIN_INSTALL = "plugin:install"

    # API access
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"


class Role(str, Enum):
    """System roles"""

    ADMIN = "admin"
    USER = "user"
    SERVICE = "service"
    READONLY = "readonly"
    AUDITOR = "auditor"


class AccessControlManager:
    """Role-based access control manager"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.roles_permissions = self._initialize_role_permissions()

    def _initialize_role_permissions(self) -> Dict[str, List[str]]:
        """Initialize default role-permission mappings"""
        return {
            Role.ADMIN: [
                # Full system access
                Permission.SYSTEM_READ,
                Permission.SYSTEM_WRITE,
                Permission.SYSTEM_ADMIN,
                # User management
                Permission.USER_READ,
                Permission.USER_WRITE,
                Permission.USER_DELETE,
                # Network management
                Permission.NETWORK_READ,
                Permission.NETWORK_WRITE,
                Permission.NETWORK_SCAN,
                # Security management
                Permission.SECURITY_READ,
                Permission.SECURITY_WRITE,
                Permission.SECURITY_AUDIT,
                # Plugin management
                Permission.PLUGIN_READ,
                Permission.PLUGIN_WRITE,
                Permission.PLUGIN_INSTALL,
                # API access
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.API_ADMIN,
            ],
            Role.USER: [
                # Limited system access
                Permission.SYSTEM_READ,
                # Basic user operations
                Permission.USER_READ,
                # Network read access
                Permission.NETWORK_READ,
                Permission.NETWORK_SCAN,
                # Security read access
                Permission.SECURITY_READ,
                # Plugin read access
                Permission.PLUGIN_READ,
                # API read/write
                Permission.API_READ,
                Permission.API_WRITE,
            ],
            Role.SERVICE: [
                # Service-specific permissions
                Permission.SYSTEM_READ,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.NETWORK_READ,
                Permission.SECURITY_READ,
            ],
            Role.READONLY: [
                # Read-only access
                Permission.SYSTEM_READ,
                Permission.USER_READ,
                Permission.NETWORK_READ,
                Permission.SECURITY_READ,
                Permission.PLUGIN_READ,
                Permission.API_READ,
            ],
            Role.AUDITOR: [
                # Audit-specific permissions
                Permission.SYSTEM_READ,
                Permission.USER_READ,
                Permission.NETWORK_READ,
                Permission.SECURITY_READ,
                Permission.SECURITY_AUDIT,
                Permission.PLUGIN_READ,
                Permission.API_READ,
            ],
        }

    def get_user_permissions(self, user_roles: List[str]) -> List[str]:
        """Get all permissions for a user based on their roles"""
        permissions = set()

        for role in user_roles:
            if role in self.roles_permissions:
                permissions.update(self.roles_permissions[role])
            else:
                self.logger.warning(f"Unknown role: {role}")

        return list(permissions)

    def check_permission(self, user_roles: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        try:
            user_permissions = self.get_user_permissions(user_roles)
            return required_permission in user_permissions
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return False

    def check_any_permission(
        self, user_roles: List[str], required_permissions: List[str]
    ) -> bool:
        """Check if user has any of the required permissions"""
        try:
            user_permissions = self.get_user_permissions(user_roles)
            return any(perm in user_permissions for perm in required_permissions)
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return False

    def check_all_permissions(
        self, user_roles: List[str], required_permissions: List[str]
    ) -> bool:
        """Check if user has all required permissions"""
        try:
            user_permissions = self.get_user_permissions(user_roles)
            return all(perm in user_permissions for perm in required_permissions)
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return False

    def add_role_permission(self, role: str, permission: str) -> bool:
        """Add permission to a role"""
        try:
            if role not in self.roles_permissions:
                self.roles_permissions[role] = []

            if permission not in self.roles_permissions[role]:
                self.roles_permissions[role].append(permission)
                self.logger.info(
                    f"Added permission {permission} to role {role}")
                return True

            return False
        except Exception as e:
            self.logger.error(f"Error adding role permission: {e}")
            return False

    def remove_role_permission(self, role: str, permission: str) -> bool:
        """Remove permission from a role"""
        try:
            if (
                role in self.roles_permissions
                and permission in self.roles_permissions[role]
            ):
                self.roles_permissions[role].remove(permission)
                self.logger.info(
                    f"Removed permission {permission} from role {role}")
                return True

            return False
        except Exception as e:
            self.logger.error(f"Error removing role permission: {e}")
            return False

    def save_roles_permissions(self, file_path: str) -> bool:
        """Save roles and permissions to file"""
        try:
            with open(file_path, "w") as f:
                json.dump(self.roles_permissions, f, indent=2)
            self.logger.info(f"Roles and permissions saved to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving roles and permissions: {e}")
            return False

    def load_roles_permissions(self, file_path: str) -> bool:
        """Load roles and permissions from file"""
        try:
            if Path(file_path).exists():
                with open(file_path, "r") as f:
                    self.roles_permissions = json.load(f)
                self.logger.info(
                    f"Roles and permissions loaded from {file_path}")
                return True
            else:
                self.logger.warning(f"Roles file not found: {file_path}")
                return False
        except Exception as e:
            self.logger.error(f"Error loading roles and permissions: {e}")
            return False


# Global access control manager
access_control = AccessControlManager()


def require_permission(permission: str):
    """Decorator to require specific permission"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = None
            for arg in args:
                if isinstance(arg, dict) and "roles" in arg:
                    current_user = arg
                    break

            if not current_user:
                # Try to get from kwargs
                current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required")

            user_roles = current_user.get("roles", [])

            if not access_control.check_permission(user_roles, permission):
                raise HTTPException(
                    status_code=403, detail=f"Permission denied: {permission} required"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_any_permission(permissions: List[str]):
    """Decorator to require any of the specified permissions"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = None
            for arg in args:
                if isinstance(arg, dict) and "roles" in arg:
                    current_user = arg
                    break

            if not current_user:
                current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required")

            user_roles = current_user.get("roles", [])

            if not access_control.check_any_permission(user_roles, permissions):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: One of {permissions} required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: str):
    """Decorator to require specific role"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = None
            for arg in args:
                if isinstance(arg, dict) and "roles" in arg:
                    current_user = arg
                    break

            if not current_user:
                current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required")

            user_roles = current_user.get("roles", [])

            if role not in user_roles:
                raise HTTPException(
                    status_code=403, detail=f"Role required: {role}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_permission_dependency(permission: str):
    """Dependency to check permission"""

    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])

        if not access_control.check_permission(user_roles, permission):
            raise HTTPException(
                status_code=403, detail=f"Permission denied: {permission} required"
            )

        return current_user

    return permission_checker


# Save default roles and permissions
def initialize_access_control():
    """Initialize access control with default roles and permissions"""
    try:
        # Create config directory if it doesn't exist
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        # Save default roles and permissions
        roles_file = config_dir / "roles_permissions.json"
        access_control.save_roles_permissions(str(roles_file))

        access_control.logger.info("Access control initialized successfully")
        return True

    except Exception as e:
        access_control.logger.error(
            f"Failed to initialize access control: {e}")
        return False


# Import get_current_user at the end to avoid circular import
try:
    from .auth import get_current_user
except ImportError:
    # Define a placeholder for when auth module is not available
    async def get_current_user():
        raise HTTPException(
            status_code=500, detail="Authentication service unavailable"
        )
