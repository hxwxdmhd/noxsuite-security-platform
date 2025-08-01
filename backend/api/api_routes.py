from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth.auth_service import get_current_user
from auth.rbac_service import RBACService, Permission
from backend.api.user_service import UserService
from backend.api.admin_service import AdminService

api_router = APIRouter(prefix="/api/v1")


# Pydantic models for request/response
class UserCreateRequest(BaseModel):
    username: str
    email: str
    role: str = "user"


class UserUpdateRequest(BaseModel):
    username: str = None
    email: str = None
    role: str = None


def require_permission(permission: Permission):
    """Decorator factory for permission-based access control"""
    def permission_checker(current_user=Depends(get_current_user)):
        rbac = RBACService()
        if not rbac.check_permission(current_user["user_id"], permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return current_user
    return permission_checker


# Health and basic endpoints
@api_router.get("/health")
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "development"
    }


@api_router.get("/status")
async def system_status():
    """Detailed system status"""
    return {
        "services": {
            "auth": "operational",
            "database": "operational",
            "mfa": "operational",
            "rbac": "operational"
        },
        "metrics": {
            "uptime": "99.9%",
            "response_time_ms": 150,
            "active_sessions": 5
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# User management endpoints
@api_router.get("/users/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current user profile information"""
    user_data = UserService.get_user_by_id(current_user["user_id"])
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data


@api_router.put("/users/me")
async def update_current_user(
    updates: UserUpdateRequest,
    current_user=Depends(get_current_user)
):
    """Update current user profile"""
    update_data = updates.dict(exclude_unset=True)
    result = UserService.update_user(current_user["user_id"], update_data)
    return result


@api_router.get("/users")
async def list_users(
    current_user=Depends(require_permission(Permission.USER_VIEW))
):
    """List all users (requires USER_VIEW permission)"""
    return {
        "users": [
            UserService.get_user_by_id("admin"),
            UserService.get_user_by_id("user1")
        ],
        "total": 2
    }


@api_router.post("/users")
async def create_user(
    user_request: UserCreateRequest,
    current_user=Depends(require_permission(Permission.USER_CREATE))
):
    """Create new user (requires USER_CREATE permission)"""
    user_data = user_request.dict()
    result = UserService.create_user(user_data)
    return result


# Admin endpoints
@api_router.get("/admin/dashboard")
async def admin_dashboard(
    current_user=Depends(require_permission(Permission.ADMIN_ACCESS))
):
    """Admin dashboard data (requires ADMIN_ACCESS permission)"""
    AdminService.verify_admin_access(current_user)
    dashboard_data = AdminService.get_dashboard_data()
    user_stats = UserService.get_user_stats()

    return {
        **dashboard_data,
        "user_statistics": user_stats,
        "system_health": {
            "auth_service": "healthy",
            "mfa_service": "healthy",
            "rbac_service": "healthy",
            "api_service": "healthy"
        }
    }


@api_router.get("/admin/users/stats")
async def get_user_statistics(
    current_user=Depends(require_permission(Permission.ADMIN_ACCESS))
):
    """Get detailed user statistics"""
    return UserService.get_user_stats()


# MFA endpoints
@api_router.get("/mfa/status")
async def get_mfa_status(current_user=Depends(get_current_user)):
    """Get current user's MFA status"""
    user = UserService.get_user_by_id(current_user["user_id"])
    return {
        "mfa_enabled": user.get("mfa_enabled", False),
        "backup_codes_count": 0,  # Placeholder
        "last_used": None
    }


# Permissions endpoints
@api_router.get("/permissions/me")
async def get_my_permissions(current_user=Depends(get_current_user)):
    """Get current user's permissions"""
    rbac = RBACService()
    permissions = rbac.get_user_permissions(current_user["user_id"])
    return {
        "user_id": current_user["user_id"],
        "permissions": permissions,
        "role": current_user.get("role", "user")
    }