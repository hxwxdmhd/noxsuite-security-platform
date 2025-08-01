# NoxSuite MFA & RBAC Implementation

This repository contains the implementation of Multi-Factor Authentication (MFA) and Role-Based Access Control (RBAC) for the NoxSuite platform.

## Features

### Authentication

- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **Time-Based One-Time Password (TOTP)**: Industry-standard MFA implementation
- **Backup Codes**: Recovery mechanism for MFA-enabled accounts
- **Token Refresh**: Allows extending sessions without re-authentication
- **Session Management**: Tracks active sessions with ability to revoke access

### Authorization

- **Role-Based Access Control (RBAC)**: Comprehensive permission system with roles
- **Fine-grained Permissions**: Control access to specific resources and actions
- **Permission Inheritance**: Users inherit permissions from all assigned roles
- **Role Management**: Create, update, and delete custom roles
- **User-Role Assignment**: Assign and remove roles from users

### API Security

- **Authentication Middleware**: FastAPI dependencies for securing endpoints
- **Permission Requirements**: Decorators and dependencies for permission checks
- **Role Requirements**: Enforce role-based access to endpoints
- **Error Handling**: Standardized error responses for authentication/authorization failures

## Project Structure

```
├── auth/
│   ├── auth_integration.py      # Integrates JWT, MFA, and RBAC
│   ├── auth_middleware.py       # FastAPI auth dependencies
│   ├── jwt_utils.py             # JWT token management
│   ├── mfa_service.py           # TOTP-based MFA implementation
│   └── rbac_service.py          # Role-based access control
├── backend/
│   └── api/
│       ├── admin_routes.py      # Admin API endpoints
│       ├── auth_routes.py       # Authentication endpoints
│       ├── main.py              # FastAPI application setup
│       └── user_routes.py       # User management endpoints
├── frontend/
│   └── src/
│       └── components/
│           └── Login.jsx        # React login component with MFA support
├── Dockerfile.api               # API service Dockerfile
├── docker-compose.yml           # Docker Compose configuration
├── init_auth.py                 # Initialize auth settings
├── prometheus.yml               # Prometheus configuration
├── requirements.txt             # Python dependencies
├── test_auth_rbac.py            # Test script for auth/RBAC
└── test_mfa.py                  # Test script for MFA
```

## Auth Components

### JWT Authentication

JWT authentication provides stateless, token-based authentication for the API:

- **Access Tokens**: Short-lived tokens for API access (default: 1 hour)
- **Refresh Tokens**: Long-lived tokens for obtaining new access tokens (default: 7 days)
- **Token Claims**: Include user ID, roles, and permissions
- **Token Verification**: Validates token integrity and expiration

### Multi-Factor Authentication (MFA)

TOTP-based MFA adds an additional layer of security:

- **TOTP Generation**: Standards-compliant TOTP code generation
- **QR Code Support**: Provision MFA with authenticator apps via QR code
- **Backup Codes**: Single-use recovery codes for account access
- **MFA Flow**: Authentication with username/password + TOTP code

### Role-Based Access Control (RBAC)

RBAC provides fine-grained access control:

- **Permissions**: Atomic access rights for specific resources/actions
- **Roles**: Collections of permissions for common user types
- **Default Roles**: Pre-configured admin, user, and moderator roles
- **Custom Roles**: Create and manage custom roles with specific permissions

## API Endpoints

### Authentication

- `POST /api/auth/login`: Authenticate with username/password
- `POST /api/auth/mfa/verify`: Verify MFA code
- `POST /api/auth/token/refresh`: Refresh access token
- `POST /api/auth/logout`: Invalidate current session
- `GET /api/auth/me`: Get current user information

### MFA Management

- `POST /api/auth/mfa/setup`: Set up MFA for current user
- `POST /api/auth/mfa/setup/complete`: Verify and complete MFA setup
- `POST /api/auth/mfa/disable`: Disable MFA for current user

### User Management

- `GET /api/users`: List users
- `POST /api/users`: Create new user
- `GET /api/users/{user_id}`: Get user details
- `PUT /api/users/{user_id}`: Update user
- `DELETE /api/users/{user_id}`: Delete user
- `POST /api/users/{user_id}/roles`: Assign roles to user
- `DELETE /api/users/{user_id}/roles/{role_name}`: Remove role from user
- `GET /api/users/{user_id}/roles`: Get user roles

### Role Management

- `GET /api/admin/roles`: List roles
- `POST /api/admin/roles`: Create new role
- `GET /api/admin/roles/{role_name}`: Get role details
- `PUT /api/admin/roles/{role_name}`: Update role
- `DELETE /api/admin/roles/{role_name}`: Delete role

### System Administration

- `GET /api/admin/metrics`: Get system metrics
- `GET /api/admin/settings`: Get system settings
- `PUT /api/admin/settings`: Update system settings
- `POST /api/admin/backup`: Create system backup
- `POST /api/admin/restore`: Restore system backup
- `GET /api/admin/logs`: Get system logs

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- Node.js 16+ (for frontend development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/noxsuite.git
   cd noxsuite
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize authentication settings:
   ```bash
   python init_auth.py
   ```

4. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Access the API at [http://localhost:8000](http://localhost:8000) and the frontend at [http://localhost:3000](http://localhost:3000)

### Running Tests

Run the authentication and RBAC tests:
```bash
python test_auth_rbac.py
```

Run the MFA tests:
```bash
python test_mfa.py
```

## Usage Examples

### Authenticating with MFA

1. Call `/api/auth/login` with username/password
2. If MFA is required, the response will indicate `mfa_required` status
3. Generate TOTP code from user's authenticator app
4. Call `/api/auth/mfa/verify` with user ID and TOTP code
5. Store received tokens for subsequent API calls

### Protecting an API Endpoint

```python
@router.get("/protected-resource")
async def get_protected_resource(
    current_user: Dict[str, Any] = Depends(auth_middleware.require_permission(Permission.USER_VIEW))
):
    # Only users with USER_VIEW permission can access this endpoint
    return {"message": "You have access to this resource"}
```

### Setting Up MFA for a User

1. Call `/api/auth/mfa/setup` to get TOTP secret and QR code
2. Display QR code to user for scanning with authenticator app
3. User enters first TOTP code from app
4. Call `/api/auth/mfa/setup/complete` with user ID, secret, and TOTP code
5. Store backup codes securely

## Security Considerations

- Store JWT secret securely and rotate periodically
- Set appropriate token expiry times
- Implement rate limiting for login attempts
- Use HTTPS in production
- Securely store TOTP secrets (encrypted at rest)
- Implement audit logging for security events
- Regular security testing and code reviews

## License

This project is licensed under the MIT License - see the LICENSE file for details.
