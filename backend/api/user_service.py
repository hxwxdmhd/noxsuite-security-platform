"""
Enhanced User Service for API Endpoints with MFA/RBAC Integration
"""

from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from auth.mfa_service import MFAService
from auth.rbac_service import RBACService, Role


class UserService:
    """Enhanced User Service with MFA and RBAC integration"""

    def __init__(self):
        self.data_dir = Path("data/users")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.mfa_service = MFAService()
        self.rbac_service = RBACService()

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID with role and permissions"""
        # Mock implementation - replace with actual database
        users_db = {
            "admin": {
                "user_id": "admin",
                "username": "admin",
                "email": "admin@noxsuite.local",
                "role": "admin",
                "mfa_enabled": True,
                "permissions": [
                    "admin:access", "admin:settings", "system:logs"
                ],
                "created_at": "2025-07-30T00:00:00Z",
                "last_login": "2025-07-31T10:00:00Z"
            },
            "user1": {
                "user_id": "user1",
                "username": "testuser",
                "email": "user@noxsuite.local",
                "role": "user",
                "mfa_enabled": False,
                "permissions": ["user:view", "api:read"],
                "created_at": "2025-07-30T00:00:00Z",
                "last_login": "2025-07-31T09:30:00Z"
            }
        }

        user = users_db.get(user_id)
        if user:
            # Add real-time permission check
            rbac = RBACService()
            user["effective_permissions"] = rbac.get_user_permissions(user_id)

        return user

    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user with role assignment"""
        user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        new_user = {
            "user_id": user_id,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "user"),
            "mfa_enabled": False,
            "permissions": [],
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }

        # Assign default permissions based on role
        rbac = RBACService()
        if user_data.get("role") == "admin":
            rbac.assign_role(user_id, Role.ADMIN)
        else:
            rbac.assign_role(user_id, Role.USER)

        new_user["permissions"] = rbac.get_user_permissions(user_id)

        return {
            "status": "created",
            "user": new_user
        }

    @staticmethod
    def update_user(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            return {"status": "error", "message": "User not found"}

        # Apply updates (mock implementation)
        user.update(updates)
        user["updated_at"] = datetime.utcnow().isoformat()

        return {"status": "updated", "user": user}

    @staticmethod
    def get_user_stats() -> Dict[str, Any]:
        """Get user statistics for dashboard"""
        return {
            "total_users": 2,
            "active_users": 2,
            "mfa_enabled_users": 1,
            "admin_users": 1,
            "regular_users": 1,
            "last_updated": datetime.utcnow().isoformat()
        }