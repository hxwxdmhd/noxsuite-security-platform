"""
Admin API Routes for NoxSuite
Implements administrative functions with role-based access control
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from auth.auth_integration import AuthIntegrationService
from auth.auth_middleware import AuthMiddleware
from auth.rbac_service import Permission, Role

# Initialize router
router = APIRouter(prefix="/admin", tags=["admin"])

# Initialize auth services (to be injected in main app)
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
class RoleCreate(BaseModel):
    """Role creation request"""

    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field("", max_length=200)
    permissions: List[str] = Field(default=[])


class RoleUpdate(BaseModel):
    """Role update request"""

    description: Optional[str] = Field(None, max_length=200)
    permissions: Optional[List[str]] = None


class RoleResponse(BaseModel):
    """Role response model"""

    name: str
    description: str
    permissions: List[str]


class SystemMetricsResponse(BaseModel):
    """System metrics response"""

    active_users: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: int


class SystemSettingsUpdate(BaseModel):
    """System settings update request"""

    mfa_required: Optional[bool] = None
    session_timeout: Optional[int] = None
    password_policy: Optional[Dict[str, Any]] = None


class SystemSettingsResponse(BaseModel):
    """System settings response"""

    mfa_required: bool
    session_timeout: int
    password_policy: Dict[str, Any]


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_ACCESS)
    ),
):
    """
    List all roles in the system

    Args:
        current_user: Current authenticated user with ADMIN_ACCESS permission

    Returns:
        List of roles
    """
    # Get all roles
    roles = []
    for role_name, role in auth_service.rbac_service.roles.items():
        roles.append(
            {
                "name": role.name,
                "description": role.description,
                "permissions": [p.value for p in role.permissions],
            }
        )

    return roles


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_SETTINGS)
    ),
):
    """
    Create a new role

    Args:
        role_data: Role creation data
        current_user: Current authenticated user with ADMIN_SETTINGS permission

    Returns:
        Created role

    Raises:
        HTTPException: If role already exists or permissions invalid
    """
    # Check if role already exists
    if auth_service.rbac_service.get_role(role_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_data.name}' already exists",
        )

    # Validate permissions
    valid_permissions = [p.value for p in Permission]
    invalid_permissions = [
        p for p in role_data.permissions if p not in valid_permissions
    ]
    if invalid_permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permissions: {', '.join(invalid_permissions)}",
        )

    # Create role
    role = Role(
        name=role_data.name,
        description=role_data.description,
        permissions=[Permission(p) for p in role_data.permissions],
    )
    auth_service.rbac_service.add_role(role)

    return {
        "name": role.name,
        "description": role.description,
        "permissions": [p.value for p in role.permissions],
    }


@router.get("/roles/{role_name}", response_model=RoleResponse)
async def get_role(
    role_name: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_ACCESS)
    ),
):
    """
    Get role by name

    Args:
        role_name: Role name
        current_user: Current authenticated user with ADMIN_ACCESS permission

    Returns:
        Role details

    Raises:
        HTTPException: If role not found
    """
    # Get role
    role = auth_service.rbac_service.get_role(role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found",
        )

    return {
        "name": role.name,
        "description": role.description,
        "permissions": [p.value for p in role.permissions],
    }


@router.put("/roles/{role_name}", response_model=RoleResponse)
async def update_role(
    role_data: RoleUpdate,
    role_name: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_SETTINGS)
    ),
):
    """
    Update a role

    Args:
        role_data: Role update data
        role_name: Role name
        current_user: Current authenticated user with ADMIN_SETTINGS permission

    Returns:
        Updated role

    Raises:
        HTTPException: If role not found or permissions invalid
    """
    # Get role
    role = auth_service.rbac_service.get_role(role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found",
        )

    # Protect built-in roles
    if role_name == "admin" and role_data.permissions is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify permissions of the admin role",
        )

    # Update description if provided
    if role_data.description is not None:
        role.description = role_data.description

    # Update permissions if provided
    if role_data.permissions is not None:
        # Validate permissions
        valid_permissions = [p.value for p in Permission]
        invalid_permissions = [
            p for p in role_data.permissions if p not in valid_permissions
        ]
        if invalid_permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid permissions: {', '.join(invalid_permissions)}",
            )

        # Set permissions
        role.permissions = set([Permission(p) for p in role_data.permissions])

    return {
        "name": role.name,
        "description": role.description,
        "permissions": [p.value for p in role.permissions],
    }


@router.delete("/roles/{role_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_name: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_SETTINGS)
    ),
):
    """
    Delete a role

    Args:
        role_name: Role name
        current_user: Current authenticated user with ADMIN_SETTINGS permission

    Raises:
        HTTPException: If role not found or is a protected role
    """
    # Protect built-in roles
    if role_name in ["admin", "user", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot delete built-in role '{role_name}'",
        )

    # Delete role
    if not auth_service.rbac_service.delete_role(role_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found",
        )

    return None


@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.SYSTEM_METRICS)
    ),
):
    """
    Get system metrics

    Args:
        current_user: Current authenticated user with SYSTEM_METRICS permission

    Returns:
        System metrics
    """
    # In a real implementation, this would query system metrics
    # Here we'll just return mock data
    return {
        "active_users": 42,
        "cpu_usage": 25.5,
        "memory_usage": 60.2,
        "disk_usage": 45.7,
        "uptime": 86400 * 3,  # 3 days
    }


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_system_settings(
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_SETTINGS)
    ),
):
    """
    Get system settings

    Args:
        current_user: Current authenticated user with ADMIN_SETTINGS permission

    Returns:
        System settings
    """
    # In a real implementation, this would query system settings
    # Here we'll just return mock data
    return {
        "mfa_required": auth_service.mfa_enabled,
        "session_timeout": auth_service.jwt_manager.access_token_expiry,
        "password_policy": {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special": True,
        },
    }


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_system_settings(
    settings: SystemSettingsUpdate,
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_SETTINGS)
    ),
):
    """
    Update system settings

    Args:
        settings: System settings update
        current_user: Current authenticated user with ADMIN_SETTINGS permission

    Returns:
        Updated system settings
    """
    # In a real implementation, this would update system settings
    # Here we'll just update our in-memory settings

    # Update MFA setting if provided
    if settings.mfa_required is not None:
        auth_service.mfa_enabled = settings.mfa_required

    # Update session timeout if provided
    if settings.session_timeout is not None:
        auth_service.jwt_manager.access_token_expiry = settings.session_timeout

    # Return updated settings
    return {
        "mfa_required": auth_service.mfa_enabled,
        "session_timeout": auth_service.jwt_manager.access_token_expiry,
        "password_policy": {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special": True,
        },
    }


@router.post("/backup", status_code=status.HTTP_202_ACCEPTED)
async def create_system_backup(
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.SYSTEM_BACKUP)
    ),
):
    """
    Create a system backup

    Args:
        current_user: Current authenticated user with SYSTEM_BACKUP permission

    Returns:
        Backup job information
    """
    # In a real implementation, this would initiate a backup job
    # Here we'll just return a mock response
    return {
        "job_id": f"backup_{int(datetime.now().timestamp())}",
        "status": "started",
        "message": "Backup job started successfully",
        "estimated_completion": datetime.now().isoformat(),
    }


@router.post("/restore", status_code=status.HTTP_202_ACCEPTED)
async def restore_system_backup(
    backup_id: str = Body(..., embed=True),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.SYSTEM_RESTORE)
    ),
):
    """
    Restore a system backup

    Args:
        backup_id: Backup ID to restore
        current_user: Current authenticated user with SYSTEM_RESTORE permission

    Returns:
        Restore job information

    Raises:
        HTTPException: If backup not found
    """
    # In a real implementation, this would initiate a restore job
    # Here we'll just return a mock response
    return {
        "job_id": f"restore_{int(datetime.now().timestamp())}",
        "status": "started",
        "backup_id": backup_id,
        "message": "Restore job started successfully",
        "estimated_completion": datetime.now().isoformat(),
    }


@router.get("/logs", status_code=status.HTTP_200_OK)
async def get_system_logs(
    start_date: Optional[str] = Query(
        None, description="ISO format start date"),
    end_date: Optional[str] = Query(None, description="ISO format end date"),
    level: Optional[str] = Query(
        None, description="Log level (info, warning, error)"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.SYSTEM_LOGS)
    ),
):
    """
    Get system logs with filtering

    Args:
        start_date: ISO format start date for log filtering
        end_date: ISO format end date for log filtering
        level: Log level for filtering
        limit: Maximum number of logs to return
        current_user: Current authenticated user with SYSTEM_LOGS permission

    Returns:
        System logs
    """
    # In a real implementation, this would query logs from a database or log files
    # Here we'll just return mock data
    return {
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "source": "auth_service",
                "message": "User authenticated successfully",
                "details": {"user_id": "user_1234", "ip_address": "192.168.1.1"},
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "WARNING",
                "source": "auth_service",
                "message": "Failed login attempt",
                "details": {"username": "unknown", "ip_address": "192.168.1.100"},
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "source": "database",
                "message": "Connection error",
                "details": {"error": "Connection timeout", "duration": 5000},
            },
        ],
        "total": 3,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "level": level,
            "limit": limit,
        },
    }
