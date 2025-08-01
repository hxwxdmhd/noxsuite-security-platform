# RBAC Schema & Implementation Plan
# NoxSuite Security Enhancement - Phase 3

## Database Schema for RBAC

### Required Tables:

```sql
-- Roles table
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(role_id, permission_id)
);

-- User-Role mapping (already exists but may need updates)
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,
    expires_at DATETIME NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    UNIQUE(user_id, role_id)
);
```

### Default Roles & Permissions:

```sql
-- System roles
INSERT INTO roles (name, description, is_system_role) VALUES 
('admin', 'System administrator with full access', TRUE),
('user', 'Standard user with basic access', TRUE),
('moderator', 'User with moderation capabilities', TRUE),
('service', 'Service account for API access', TRUE);

-- Core permissions
INSERT INTO permissions (name, resource, action, description) VALUES
('user.read', 'user', 'read', 'Read user information'),
('user.write', 'user', 'write', 'Create and update users'),
('user.delete', 'user', 'delete', 'Delete users'),
('role.read', 'role', 'read', 'Read role information'),
('role.write', 'role', 'write', 'Create and update roles'),
('role.assign', 'role', 'assign', 'Assign roles to users'),
('mfa.setup', 'mfa', 'setup', 'Setup MFA for users'),
('mfa.disable', 'mfa', 'disable', 'Disable MFA for users'),
('audit.read', 'audit', 'read', 'Read audit logs'),
('system.admin', 'system', 'admin', 'System administration');
```

## FastAPI RBAC Middleware

### Permission Decorator:

```python
from functools import wraps
from fastapi import HTTPException, status, Depends
from typing import List, Optional

def require_permission(permission: str, resource: Optional[str] = None):
    """
    Decorator to require specific permission for endpoint access
    
    Args:
        permission: Required permission name (e.g., 'user.read')
        resource: Optional resource context for permission check
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has required permission
            if not await check_user_permission(current_user.id, permission, resource):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def check_user_permission(user_id: int, permission: str, resource: Optional[str] = None) -> bool:
    """Check if user has specific permission"""
    # Implementation will query user_roles -> role_permissions -> permissions
    pass

# Role-based decorator
def require_role(role: str):
    """Decorator to require specific role for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not await check_user_role(current_user.id, role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## TestSprite RBAC Test Suite

### Test Cases:

1. **Role Assignment Tests**
   - Assign role to user
   - Remove role from user
   - Test role inheritance
   - Test role expiration

2. **Permission Enforcement Tests**
   - Access endpoint without permission (403)
   - Access endpoint with correct permission (200)
   - Test permission on different resources
   - Test admin override permissions

3. **MFA + RBAC Integration Tests**
   - MFA login with role-restricted endpoint
   - Role change after MFA authentication
   - Session invalidation on role change

### Test Implementation:

```python
# TestSprite RBAC Test Cases
async def test_rbac_permission_enforcement():
    """Test that endpoints properly enforce permissions"""
    
    # Test 1: User without permission gets 403
    user_token = await login_as_user("user@example.com")
    response = await api_request("DELETE", "users/123", token=user_token)
    assert response.status == 403
    
    # Test 2: Admin with permission gets 200
    admin_token = await login_as_user("admin@example.com")
    response = await api_request("DELETE", "users/123", token=admin_token)
    assert response.status == 200

async def test_mfa_rbac_integration():
    """Test MFA + RBAC together"""
    
    # Login with MFA
    session_id = await initiate_mfa_login("mfa_user@example.com")
    mfa_code = generate_totp_code("TESTSECRET")
    token = await verify_mfa(session_id, mfa_code)
    
    # Test role-restricted endpoint
    response = await api_request("GET", "admin/users", token=token)
    assert response.status in [200, 403]  # Depends on user's role
```

## Implementation Sprint Plan

### Week 1: RBAC Core (16 hours)
**Day 1-2: Database Schema (4 hours)**
- Create RBAC migration script
- Update SQLAlchemy models
- Seed default roles and permissions

**Day 3-4: API Middleware (8 hours)**
- Implement permission decorators
- Create role checking functions
- Add RBAC endpoints (assign/revoke roles)

**Day 5: Integration (4 hours)**
- Apply decorators to existing endpoints
- Test basic RBAC functionality
- Fix MFA session ID issue

### Week 2: Testing & Automation (12 hours)
**Day 1-2: TestSprite Extension (6 hours)**
- Create RBAC test cases
- Implement MFA+RBAC integration tests
- Add automated role assignment tests

**Day 3: Security Hardening (4 hours)**
- Add encryption for MFA secrets
- Implement session persistence
- Security audit of RBAC implementation

**Day 4: Documentation (2 hours)**
- Update API documentation
- Create RBAC usage guide
- Security compliance documentation

## Critical Dependencies

### Must Fix Before RBAC:
1. ✅ **Session ID Transmission** - FIXED ABOVE
2. 🔴 **Database Encryption** - Use field-level encryption for secrets
3. 🔴 **Session Storage** - Implement Redis or database-backed sessions

### RBAC Blockers:
1. Database migration script for new tables
2. Permission checking logic implementation
3. Decorator application to endpoints
4. TestSprite integration updates

## Security Considerations

### Encryption Requirements:
- MFA secrets: AES-256 encryption at field level
- Session tokens: Encrypted storage in Redis
- Audit logs: Tamper-proof with digital signatures

### Access Control Matrix:
```
Role      | User Mgmt | Role Mgmt | MFA Admin | Audit Logs | System
----------|-----------|-----------|-----------|------------|--------
admin     | CRUD      | CRUD      | CRUD      | READ       | ADMIN
moderator | READ      | READ      | SETUP     | READ       | NONE
user      | SELF      | NONE      | SELF      | NONE       | NONE
service   | READ      | NONE      | NONE      | READ       | API
```
