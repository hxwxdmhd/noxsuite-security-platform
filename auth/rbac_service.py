"""
Role-Based Access Control (RBAC) Service for NoxSuite
Implements comprehensive role-based authorization with permissions and policies
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Union, Any
import json

class Permission(str, Enum):
    """Core permissions in the system"""
    # User management permissions
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"
    
    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_USERS = "admin:users"
    
    # System permissions
    SYSTEM_LOGS = "system:logs"
    SYSTEM_METRICS = "system:metrics"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_RESTORE = "system:restore"
    
    # API permissions
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"

class Role:
    """Role definition with permissions"""
    
    def __init__(self, name: str, description: str = "", permissions: Optional[List[Permission]] = None):
        """
        Initialize a role
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permissions for this role
        """
        self.name = name
        self.description = description
        self.permissions: Set[Permission] = set(permissions or [])
    
    def add_permission(self, permission: Permission) -> None:
        """
        Add a permission to the role
        
        Args:
            permission: Permission to add
        """
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        """
        Remove a permission from the role
        
        Args:
            permission: Permission to remove
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def has_permission(self, permission: Permission) -> bool:
        """
        Check if the role has a specific permission
        
        Args:
            permission: Permission to check
        
        Returns:
            True if the role has the permission, False otherwise
        """
        return permission in self.permissions
    
    def to_dict(self) -> Dict:
        """
        Convert role to dictionary
        
        Returns:
            Dictionary representation of the role
        """
        return {
            "name": self.name,
            "description": self.description,
            "permissions": [p for p in self.permissions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Role':
        """
        Create role from dictionary
        
        Args:
            data: Dictionary representation of the role
        
        Returns:
            Role object
        """
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            permissions=[Permission(p) for p in data.get("permissions", [])]
        )

class RBACService:
    """Role-Based Access Control Service"""
    
    def __init__(self):
        """Initialize RBAC service with default roles"""
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, List[str]] = {}  # user_id -> role names
        
        # Initialize default roles
        self._initialize_default_roles()
    
    def _initialize_default_roles(self) -> None:
        """Initialize default roles in the system"""
        # Admin role with all permissions
        admin_role = Role(
            name="admin",
            description="Administrator with full system access",
            permissions=list(Permission)
        )
        
        # User role with basic permissions
        user_role = Role(
            name="user",
            description="Regular user with limited permissions",
            permissions=[
                Permission.USER_VIEW,
                Permission.API_READ
            ]
        )
        
        # Moderator role with intermediate permissions
        moderator_role = Role(
            name="moderator",
            description="Moderator with user management permissions",
            permissions=[
                Permission.USER_VIEW,
                Permission.USER_EDIT,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.SYSTEM_LOGS,
                Permission.SYSTEM_METRICS
            ]
        )
        
        # Add roles to the service
        self.add_role(admin_role)
        self.add_role(user_role)
        self.add_role(moderator_role)
    
    def add_role(self, role: Role) -> None:
        """
        Add a role to the service
        
        Args:
            role: Role to add
        """
        self.roles[role.name] = role
    
    def get_role(self, role_name: str) -> Optional[Role]:
        """
        Get a role by name
        
        Args:
            role_name: Role name
        
        Returns:
            Role object or None if not found
        """
        return self.roles.get(role_name)
    
    def delete_role(self, role_name: str) -> bool:
        """
        Delete a role
        
        Args:
            role_name: Role name
        
        Returns:
            True if deleted, False if not found
        """
        if role_name in self.roles:
            del self.roles[role_name]
            
            # Remove the role from all users
            for user_id, roles in self.user_roles.items():
                if role_name in roles:
                    roles.remove(role_name)
            
            return True
        return False
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """
        Assign a role to a user
        
        Args:
            user_id: User ID
            role_name: Role name
        
        Returns:
            True if assigned, False if role not found
        """
        if role_name not in self.roles:
            return False
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
        
        return True
    
    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """
        Remove a role from a user
        
        Args:
            user_id: User ID
            role_name: Role name
        
        Returns:
            True if removed, False if user or role not found
        """
        if user_id not in self.user_roles:
            return False
        
        if role_name in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role_name)
            return True
        
        return False
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Get all roles assigned to a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of Role objects
        """
        if user_id not in self.user_roles:
            return []
        
        return [self.roles[role_name] for role_name in self.user_roles[user_id] 
                if role_name in self.roles]
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """
        Get all permissions for a user (combined from all roles)
        
        Args:
            user_id: User ID
        
        Returns:
            Set of permissions
        """
        permissions: Set[Permission] = set()
        
        for role in self.get_user_roles(user_id):
            permissions.update(role.permissions)
        
        return permissions
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if a user has a specific permission
        
        Args:
            user_id: User ID
            permission: Permission to check
        
        Returns:
            True if the user has the permission, False otherwise
        """
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions
    
    def has_permissions(self, user_id: str, permissions: List[Permission]) -> bool:
        """
        Check if a user has all specified permissions
        
        Args:
            user_id: User ID
            permissions: List of permissions to check
        
        Returns:
            True if the user has all permissions, False otherwise
        """
        user_permissions = self.get_user_permissions(user_id)
        return all(perm in user_permissions for perm in permissions)
    
    def has_any_permission(self, user_id: str, permissions: List[Permission]) -> bool:
        """
        Check if a user has any of the specified permissions
        
        Args:
            user_id: User ID
            permissions: List of permissions to check
        
        Returns:
            True if the user has any of the permissions, False otherwise
        """
        user_permissions = self.get_user_permissions(user_id)
        return any(perm in user_permissions for perm in permissions)
    
    def export_to_json(self) -> str:
        """
        Export RBAC configuration to JSON
        
        Returns:
            JSON string
        """
        data = {
            "roles": {name: role.to_dict() for name, role in self.roles.items()},
            "user_roles": self.user_roles
        }
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_str: str) -> None:
        """
        Import RBAC configuration from JSON
        
        Args:
            json_str: JSON string
        """
        data = json.loads(json_str)
        
        # Import roles
        self.roles = {}
        for role_data in data.get("roles", {}).values():
            role = Role.from_dict(role_data)
            self.roles[role.name] = role
        
        # Import user roles
        self.user_roles = data.get("user_roles", {})

# Example usage
if __name__ == "__main__":
    # Create RBAC service
    rbac_service = RBACService()
    
    # Print default roles
    print("Default Roles:")
    for role_name, role in rbac_service.roles.items():
        print(f"  {role_name}: {role.description}")
        print(f"    Permissions: {', '.join(sorted(p.value for p in role.permissions))}")
    
    # Create a custom role
    analyst_role = Role(
        name="analyst",
        description="Data analyst with reporting permissions",
        permissions=[
            Permission.USER_VIEW,
            Permission.API_READ,
            Permission.SYSTEM_METRICS
        ]
    )
    rbac_service.add_role(analyst_role)
    
    # Assign roles to users
    rbac_service.assign_role_to_user("user1", "admin")
    rbac_service.assign_role_to_user("user2", "user")
    rbac_service.assign_role_to_user("user3", "moderator")
    rbac_service.assign_role_to_user("user4", "analyst")
    
    # Check permissions
    print("\nPermission Checks:")
    print(f"user1 (admin) has ADMIN_ACCESS: {rbac_service.has_permission('user1', Permission.ADMIN_ACCESS)}")
    print(f"user2 (user) has USER_VIEW: {rbac_service.has_permission('user2', Permission.USER_VIEW)}")
    print(f"user2 (user) has ADMIN_ACCESS: {rbac_service.has_permission('user2', Permission.ADMIN_ACCESS)}")
    print(f"user3 (moderator) has USER_EDIT: {rbac_service.has_permission('user3', Permission.USER_EDIT)}")
    
    # Export to JSON
    json_export = rbac_service.export_to_json()
    print(f"\nJSON Export: {json_export[:100]}...")
    
    # Test import
    new_rbac = RBACService()
    new_rbac.import_from_json(json_export)
    print(f"\nImported roles: {', '.join(new_rbac.roles.keys())}")
    
    # Verify permissions after import
    print(f"user1 (admin) has ADMIN_ACCESS after import: {new_rbac.has_permission('user1', Permission.ADMIN_ACCESS)}")
