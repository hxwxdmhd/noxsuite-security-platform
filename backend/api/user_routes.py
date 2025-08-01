"""
User Management API Routes for NoxSuite
Implements user CRUD operations with role-based access control
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, EmailStr, Field

from auth.auth_integration import AuthIntegrationService, AuthStatus
from auth.auth_middleware import AuthMiddleware
from auth.rbac_service import Permission

# Initialize router
router = APIRouter(prefix="/users", tags=["users"])

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
class UserCreate(BaseModel):
    """User creation request"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = Field(default=[])


class UserUpdate(BaseModel):
    """User update request"""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model"""

    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoleAssignment(BaseModel):
    """Role assignment request"""

    roles: List[str] = Field(..., description="List of role names to assign")


class UserRolesResponse(BaseModel):
    """User roles response"""

    user_id: str
    roles: List[str]
    permissions: List[str]


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.USER_VIEW)
    ),
):
    """
    List users with pagination

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        user: Current authenticated user with USER_VIEW permission

    Returns:
        List of users
    """
    # In a real implementation, this would query the database
    # Here we'll just return a mock response
    return [
        {
            "id": "user_1234",
            "username": "admin",
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "roles": ["admin"],
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": "user_5678",
            "username": "user",
            "email": "user@example.com",
            "first_name": "Regular",
            "last_name": "User",
            "roles": ["user"],
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.USER_CREATE)
    ),
):
    """
    Create a new user

    Args:
        user_data: User creation data
        current_user: Current authenticated user with USER_CREATE permission

    Returns:
        Created user

    Raises:
        HTTPException: If username or email already exists
    """
    # In a real implementation, this would create a user in the database
    # Here we'll just return a mock response

    # Check for role permissions
    if "admin" in user_data.roles and "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users with admin role",
        )

    # Create user
    new_user = {
        "id": f"user_{hash(user_data.username) % 10000}",
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "roles": user_data.roles or ["user"],  # Default to user role
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Assign roles
    for role in new_user["roles"]:
        auth_service.rbac_service.assign_role_to_user(new_user["id"], role)

    return new_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.USER_VIEW)
    ),
):
    """
    Get user by ID

    Args:
        user_id: User ID
        current_user: Current authenticated user with USER_VIEW permission

    Returns:
        User information

    Raises:
        HTTPException: If user not found
    """
    # In a real implementation, this would query the database
    # Here we'll just return a mock response

    # Users can view their own profile, admins can view anyone
    if current_user["user_id"] != user_id and "admin" not in current_user["roles"]:
        if not auth_service.rbac_service.has_permission(
            current_user["user_id"], Permission.ADMIN_USERS
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view other users",
            )

    # Mock user data
    user = {
        "id": user_id,
        "username": "user123" if user_id != "user_1234" else "admin",
        "email": "user@example.com" if user_id != "user_1234" else "admin@example.com",
        "first_name": "Test",
        "last_name": "User",
        "roles": ["user"] if user_id != "user_1234" else ["admin"],
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    user_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.USER_EDIT)
    ),
):
    """
    Update user information

    Args:
        user_data: User update data
        user_id: User ID
        current_user: Current authenticated user with USER_EDIT permission

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or not authorized
    """
    # In a real implementation, this would update the database
    # Here we'll just return a mock response

    # Users can edit their own profile, admins can edit anyone
    if current_user["user_id"] != user_id and "admin" not in current_user["roles"]:
        if not auth_service.rbac_service.has_permission(
            current_user["user_id"], Permission.ADMIN_USERS
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update other users",
            )

    # Mock updated user
    updated_user = {
        "id": user_id,
        "username": "user123" if user_id != "user_1234" else "admin",
        "email": user_data.email or "user@example.com",
        "first_name": user_data.first_name or "Updated",
        "last_name": user_data.last_name or "User",
        "roles": ["user"] if user_id != "user_1234" else ["admin"],
        "is_active": user_data.is_active if user_data.is_active is not None else True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.USER_DELETE)
    ),
):
    """
    Delete a user

    Args:
        user_id: User ID
        current_user: Current authenticated user with USER_DELETE permission

    Raises:
        HTTPException: If user not found or not authorized
    """
    # In a real implementation, this would delete from the database

    # Only admins can delete users
    if "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users",
        )

    # Prevent deleting yourself
    if current_user["user_id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Delete user would happen here

    # Return no content
    return None


@router.post("/{user_id}/roles", response_model=UserRolesResponse)
async def assign_roles(
    role_assignment: RoleAssignment,
    user_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_USERS)
    ),
):
    """
    Assign roles to a user

    Args:
        role_assignment: Roles to assign
        user_id: User ID
        current_user: Current authenticated user with ADMIN_USERS permission

    Returns:
        Updated user roles

    Raises:
        HTTPException: If user not found or role invalid
    """
    # In a real implementation, this would update the database

    # Validate roles
    invalid_roles = []
    for role_name in role_assignment.roles:
        if not auth_service.rbac_service.get_role(role_name):
            invalid_roles.append(role_name)

    if invalid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid roles: {', '.join(invalid_roles)}",
        )

    # Check if admin role assignment and whether current user is admin
    if "admin" in role_assignment.roles and "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can assign admin role",
        )

    # Assign roles
    for role_name in role_assignment.roles:
        auth_service.rbac_service.assign_role_to_user(user_id, role_name)

    # Get updated roles and permissions
    user_roles = [
        role.name for role in auth_service.rbac_service.get_user_roles(user_id)
    ]
    user_permissions = [
        p.value for p in auth_service.rbac_service.get_user_permissions(user_id)
    ]

    return {"user_id": user_id, "roles": user_roles, "permissions": user_permissions}


@router.delete("/{user_id}/roles/{role_name}", response_model=UserRolesResponse)
async def remove_role(
    user_id: str = Path(...),
    role_name: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.ADMIN_USERS)
    ),
):
    """
    Remove a role from a user

    Args:
        user_id: User ID
        role_name: Role to remove
        current_user: Current authenticated user with ADMIN_USERS permission

    Returns:
        Updated user roles

    Raises:
        HTTPException: If user not found, role invalid, or not authorized
    """
    # In a real implementation, this would update the database

    # Validate role
    if not auth_service.rbac_service.get_role(role_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {role_name}"
        )

    # Check if removing admin role and whether current user is admin
    if role_name == "admin" and "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can remove admin role",
        )

    # Prevent removing your own admin role
    if (
        user_id == current_user["user_id"]
        and role_name == "admin"
        and "admin" in current_user["roles"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin role",
        )

    # Remove role
    auth_service.rbac_service.remove_role_from_user(user_id, role_name)

    # Get updated roles and permissions
    user_roles = [
        role.name for role in auth_service.rbac_service.get_user_roles(user_id)
    ]
    user_permissions = [
        p.value for p in auth_service.rbac_service.get_user_permissions(user_id)
    ]

    return {"user_id": user_id, "roles": user_roles, "permissions": user_permissions}


@router.get("/{user_id}/roles", response_model=UserRolesResponse)
async def get_user_roles(
    user_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(
        auth_middleware.require_permission(Permission.USER_VIEW)
    ),
):
    """
    Get roles and permissions for a user

    Args:
        user_id: User ID
        current_user: Current authenticated user with USER_VIEW permission

    Returns:
        User roles and permissions

    Raises:
        HTTPException: If user not found
    """
    # In a real implementation, this would query the database

    # Users can view their own roles, admins can view anyone
    if current_user["user_id"] != user_id and "admin" not in current_user["roles"]:
        if not auth_service.rbac_service.has_permission(
            current_user["user_id"], Permission.ADMIN_USERS
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view other users' roles",
            )

    # Get roles and permissions
    user_roles = [
        role.name for role in auth_service.rbac_service.get_user_roles(user_id)
    ]
    user_permissions = [
        p.value for p in auth_service.rbac_service.get_user_permissions(user_id)
    ]

    return {"user_id": user_id, "roles": user_roles, "permissions": user_permissions}
