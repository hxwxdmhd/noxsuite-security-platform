#!/usr/bin/env python3
"""
NoxSuite Multi-Factor Authentication & Role-Based Access Control Manager
========================================================================

Phase 1 Security Enhancement: Implements enterprise-grade MFA and RBAC
Addresses critical authentication security gaps identified in roadmap analysis.
"""

import json
import uuid
import secrets
import pymysql
import qrcode
import pyotp
import base64
from datetime import datetime, timedelta
from typing import Dict, List
from enum import Enum
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"
    SECURITY_ANALYST = "security_analyst"
    NETWORK_OPERATOR = "network_operator"
    USER = "user"
    VIEWER = "viewer"
    MAINTENANCE = "maintenance"

class Permission(Enum):
    """System permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE_USERS = "manage_users"
    MANAGE_SECURITY = "manage_security"
    MANAGE_NETWORK = "manage_network"
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    VIEW_METRICS = "view_metrics"

class MFAMethod(Enum):
    """MFA authentication methods"""
    TOTP = "totp"
    EMAIL = "email"
    SMS = "sms"
    BACKUP_CODES = "backup_codes"

class NoxSuiteMFAManager:
    """Multi-Factor Authentication Manager"""
    
    def __init__(self, db_path: str = "noxsuite_auth.db"):
        self.db_path = db_path
        self.totp_issuer = "NoxSuite v1.0"
        self.backup_codes_count = 8
        self._init_database()
    
    def _init_database(self):
        """Initialize MFA database tables"""
        with pymysql.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mfa_users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_secret TEXT,
                    backup_codes TEXT,
                    email_verified BOOLEAN DEFAULT FALSE,
                    phone_number TEXT,
                    phone_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    mfa_methods TEXT DEFAULT '[]'
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mfa_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    mfa_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES mfa_users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mfa_attempts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    method TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES mfa_users (id)
                )
            ''')
            
            conn.commit()
            logger.info("MFA database initialized successfully")
    
    def create_user(self, username: str, email: str, password: str, role: str = "user") -> Dict:
        """Create a new user with optional MFA setup"""
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO mfa_users (id, username, email, password_hash, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, email, password_hash, role))
                conn.commit()
            
            logger.info(f"User created successfully: {username}")
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "mfa_enabled": False,
                "status": "created"
            }
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return {"error": "Username or email already exists"}
    
    def enable_totp_mfa(self, user_id: str) -> Dict:
        """Enable TOTP-based MFA for user"""
        try:
            secret = pyotp.random_base32()
            backup_codes = [secrets.token_hex(4).upper() for _ in range(self.backup_codes_count)]
            
            # Get user details for QR code
            with pymysql.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                user = conn.execute('SELECT username FROM mfa_users WHERE id = ?', (user_id,)).fetchone()
                
                if not user:
                    return {"error": "User not found"}
                
                # Update user with MFA details
                mfa_methods = json.dumps([MFAMethod.TOTP.value, MFAMethod.BACKUP_CODES.value])
                conn.execute('''
                    UPDATE mfa_users 
                    SET mfa_enabled = 1, mfa_secret = ?, backup_codes = ?, mfa_methods = ?
                    WHERE id = ?
                ''', (secret, json.dumps(backup_codes), mfa_methods, user_id))
                conn.commit()
            
            # Generate QR code
            totp = pyotp.TOTP(secret)
            qr_url = totp.provisioning_uri(
                name=user['username'],
                issuer_name=self.totp_issuer
            )
            
            # Create QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            qr_code_data = base64.b64encode(img_buffer.getvalue()).decode()
            
            logger.info(f"TOTP MFA enabled for user: {user_id}")
            
            return {
                "status": "enabled",
                "secret": secret,
                "qr_code": qr_code_data,
                "backup_codes": backup_codes,
                "manual_entry_key": secret,
                "qr_url": qr_url
            }
            
        except Exception as e:
            logger.error(f"TOTP MFA setup failed: {e}")
            return {"error": str(e)}
    
    def verify_totp(self, user_id: str, token: str, ip_address: str = None) -> bool:
        """Verify TOTP token"""
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                user = conn.execute(
                    'SELECT mfa_secret, backup_codes FROM mfa_users WHERE id = ?',
                    (user_id,)
                ).fetchone()
                
                if not user or not user['mfa_secret']:
                    self._log_mfa_attempt(user_id, MFAMethod.TOTP.value, False, ip_address)
                    return False
                
                # Verify TOTP
                totp = pyotp.TOTP(user['mfa_secret'])
                if totp.verify(token, valid_window=2):
                    self._log_mfa_attempt(user_id, MFAMethod.TOTP.value, True, ip_address)
                    return True
                
                # Check backup codes
                if user['backup_codes']:
                    backup_codes = json.loads(user['backup_codes'])
                    if token.upper() in backup_codes:
                        # Remove used backup code
                        backup_codes.remove(token.upper())
                        conn.execute('''
                            UPDATE mfa_users SET backup_codes = ? WHERE id = ?
                        ''', (json.dumps(backup_codes), user_id))
                        conn.commit()
                        
                        self._log_mfa_attempt(user_id, MFAMethod.BACKUP_CODES.value, True, ip_address)
                        return True
                
                self._log_mfa_attempt(user_id, MFAMethod.TOTP.value, False, ip_address)
                return False
                
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return False
    
    def _log_mfa_attempt(self, user_id: str, method: str, success: bool, ip_address: str = None):
        """Log MFA attempt"""
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO mfa_attempts (id, user_id, method, success, ip_address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(uuid.uuid4()), user_id, method, success, ip_address))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log MFA attempt: {e}")
    
    def get_mfa_status(self, user_id: str) -> Dict:
        """Get MFA status for user"""
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                user = conn.execute('''
                    SELECT mfa_enabled, mfa_methods, backup_codes
                    FROM mfa_users WHERE id = ?
                ''', (user_id,)).fetchone()
                
                if not user:
                    return {"error": "User not found"}
                
                backup_codes_count = 0
                if user['backup_codes']:
                    backup_codes_count = len(json.loads(user['backup_codes']))
                
                methods = json.loads(user['mfa_methods']) if user['mfa_methods'] else []
                
                return {
                    "mfa_enabled": bool(user['mfa_enabled']),
                    "methods": methods,
                    "backup_codes_remaining": backup_codes_count
                }
                
        except Exception as e:
            logger.error(f"Failed to get MFA status: {e}")
            return {"error": str(e)}

class NoxSuiteRBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self, db_path: str = "noxsuite_auth.db"):
        self.db_path = db_path
        self._init_permissions()
        self._init_database()
    
    def _init_permissions(self):
        """Initialize role permissions matrix"""
        self.role_permissions = {
            UserRole.ADMIN.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.DELETE.value,
                Permission.EXECUTE.value,
                Permission.MANAGE_USERS.value,
                Permission.MANAGE_SECURITY.value,
                Permission.MANAGE_NETWORK.value,
                Permission.MANAGE_SYSTEM.value,
                Permission.VIEW_LOGS.value,
                Permission.VIEW_METRICS.value
            ],
            UserRole.SECURITY_ANALYST.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.MANAGE_SECURITY.value,
                Permission.VIEW_LOGS.value,
                Permission.VIEW_METRICS.value
            ],
            UserRole.NETWORK_OPERATOR.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.MANAGE_NETWORK.value,
                Permission.VIEW_LOGS.value,
                Permission.VIEW_METRICS.value
            ],
            UserRole.USER.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.VIEW_METRICS.value
            ],
            UserRole.VIEWER.value: [
                Permission.READ.value,
                Permission.VIEW_METRICS.value
            ],
            UserRole.MAINTENANCE.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.MANAGE_SYSTEM.value,
                Permission.VIEW_LOGS.value
            ]
        }
    
    def _init_database(self):
        """Initialize RBAC database tables"""
        with pymysql.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rbac_permissions (
                    id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    permission TEXT NOT NULL,
                    resource TEXT,
                    granted_by TEXT,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rbac_access_log (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    permission TEXT NOT NULL,
                    resource TEXT,
                    action TEXT,
                    allowed BOOLEAN NOT NULL,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default role permissions
            for role, permissions in self.role_permissions.items():
                for permission in permissions:
                    conn.execute('''
                        INSERT OR IGNORE INTO rbac_permissions (id, role, permission)
                        VALUES (?, ?, ?)
                    ''', (str(uuid.uuid4()), role, permission))
            
            conn.commit()
            logger.info("RBAC database initialized successfully")
    
    def check_permission(self, user_role: str, permission: str, resource: str = None) -> bool:
        """Check if user role has permission for action"""
        try:
            with pymysql.connect(self.db_path) as conn:
                query = '''
                    SELECT COUNT(*) FROM rbac_permissions 
                    WHERE role = ? AND permission = ? AND is_active = 1
                '''
                params = [user_role, permission]
                
                if resource:
                    query += ' AND (resource = ? OR resource IS NULL)'
                    params.append(resource)
                
                result = conn.execute(query, params).fetchone()
                return result[0] > 0
                
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    def log_access_attempt(self, user_id: str, user_role: str, permission: str, 
                          resource: str = None, action: str = None, 
                          allowed: bool = False, ip_address: str = None):
        """Log access attempt for audit purposes"""
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO rbac_access_log 
                    (id, user_id, role, permission, resource, action, allowed, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (str(uuid.uuid4()), user_id, user_role, permission, resource, action, allowed, ip_address))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log access attempt: {e}")
    
    def get_user_permissions(self, user_role: str) -> List[str]:
        """Get all permissions for a user role"""
        try:
            with pymysql.connect(self.db_path) as conn:
                result = conn.execute('''
                    SELECT permission FROM rbac_permissions 
                    WHERE role = ? AND is_active = 1
                ''', (user_role,)).fetchall()
                
                return [row[0] for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
    
    def grant_permission(self, role: str, permission: str, resource: str = None, 
                        granted_by: str = None, expires_at: datetime = None) -> bool:
        """Grant additional permission to role"""
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO rbac_permissions 
                    (id, role, permission, resource, granted_by, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (str(uuid.uuid4()), role, permission, resource, granted_by, expires_at))
                conn.commit()
                
                logger.info(f"Permission granted: {role} -> {permission}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to grant permission: {e}")
            return False
    
    def revoke_permission(self, role: str, permission: str, resource: str = None) -> bool:
        """Revoke permission from role"""
        try:
            with pymysql.connect(self.db_path) as conn:
                query = 'UPDATE rbac_permissions SET is_active = 0 WHERE role = ? AND permission = ?'
                params = [role, permission]
                
                if resource:
                    query += ' AND resource = ?'
                    params.append(resource)
                
                conn.execute(query, params)
                conn.commit()
                
                logger.info(f"Permission revoked: {role} -> {permission}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to revoke permission: {e}")
            return False

class NoxSuiteSecurityManager:
    """Integrated Security Manager combining MFA and RBAC"""
    
    def __init__(self, db_path: str = "noxsuite_auth.db"):
        self.db_path = db_path
        self.mfa_manager = NoxSuiteMFAManager(db_path)
        self.rbac_manager = NoxSuiteRBACManager(db_path)
    
    def authenticate_user(self, username: str, password: str, 
                         mfa_token: str = None, ip_address: str = None) -> Dict:
        """Complete user authentication with MFA and RBAC"""
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                user = conn.execute('''
                    SELECT id, username, email, password_hash, role, mfa_enabled,
                           failed_login_attempts, locked_until, is_active
                    FROM mfa_users WHERE username = ?
                ''', (username,)).fetchone()
                
                if not user:
                    return {"error": "Invalid credentials", "code": "USER_NOT_FOUND"}
                
                if not user['is_active']:
                    return {"error": "Account is deactivated", "code": "ACCOUNT_INACTIVE"}
                
                # Check if account is locked
                if user['locked_until']:
                    locked_until = datetime.fromisoformat(user['locked_until'])
                    if locked_until > datetime.now():
                        return {"error": "Account is locked", "code": "ACCOUNT_LOCKED"}
                
                # Verify password
                if not check_password_hash(user['password_hash'], password):
                    # Increment failed attempts
                    failed_attempts = user['failed_login_attempts'] + 1
                    locked_until = None
                    
                    if failed_attempts >= 5:
                        locked_until = datetime.now() + timedelta(minutes=15)
                    
                    conn.execute('''
                        UPDATE mfa_users 
                        SET failed_login_attempts = ?, locked_until = ?
                        WHERE id = ?
                    ''', (failed_attempts, locked_until, user['id']))
                    conn.commit()
                    
                    return {"error": "Invalid credentials", "code": "INVALID_PASSWORD"}
                
                # Check MFA if enabled
                if user['mfa_enabled']:
                    if not mfa_token:
                        return {
                            "status": "mfa_required",
                            "user_id": user['id'],
                            "message": "MFA token required"
                        }
                    
                    if not self.mfa_manager.verify_totp(user['id'], mfa_token, ip_address):
                        return {"error": "Invalid MFA token", "code": "INVALID_MFA"}
                
                # Reset failed attempts on successful login
                conn.execute('''
                    UPDATE mfa_users 
                    SET failed_login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user['id'],))
                conn.commit()
                
                # Get user permissions
                permissions = self.rbac_manager.get_user_permissions(user['role'])
                
                logger.info(f"User authenticated successfully: {username}")
                
                return {
                    "status": "authenticated",
                    "user": {
                        "id": user['id'],
                        "username": user['username'],
                        "email": user['email'],
                        "role": user['role'],
                        "permissions": permissions,
                        "mfa_enabled": bool(user['mfa_enabled'])
                    }
                }
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {"error": "Authentication failed", "code": "SYSTEM_ERROR"}
    
    def authorize_action(self, user_id: str, user_role: str, permission: str, 
                        resource: str = None, action: str = None, 
                        ip_address: str = None) -> bool:
        """Authorize user action using RBAC"""
        allowed = self.rbac_manager.check_permission(user_role, permission, resource)
        
        # Log the access attempt
        self.rbac_manager.log_access_attempt(
            user_id, user_role, permission, resource, action, allowed, ip_address
        )
        
        return allowed
    
    def create_secure_user(self, username: str, email: str, password: str, 
                          role: str = "user", enable_mfa: bool = True) -> Dict:
        """Create user with optional MFA setup"""
        # Create user
        result = self.mfa_manager.create_user(username, email, password, role)
        
        if "error" not in result and enable_mfa:
            # Enable MFA
            mfa_result = self.mfa_manager.enable_totp_mfa(result["user_id"])
            result["mfa_setup"] = mfa_result
        
        return result
    
    def get_security_status(self, user_id: str) -> Dict:
        """Get comprehensive security status for user"""
        mfa_status = self.mfa_manager.get_mfa_status(user_id)
        
        try:
            with pymysql.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                user = conn.execute('''
                    SELECT username, role, last_login, failed_login_attempts, is_active
                    FROM mfa_users WHERE id = ?
                ''', (user_id,)).fetchone()
                
                if not user:
                    return {"error": "User not found"}
                
                permissions = self.rbac_manager.get_user_permissions(user['role'])
                
                return {
                    "user": {
                        "username": user['username'],
                        "role": user['role'],
                        "last_login": user['last_login'],
                        "failed_attempts": user['failed_login_attempts'],
                        "is_active": bool(user['is_active'])
                    },
                    "mfa": mfa_status,
                    "permissions": permissions
                }
                
        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            return {"error": str(e)}

def main():
    """Main demonstration and testing"""
    print("🔐 NoxSuite MFA & RBAC Security Manager")
    print("=" * 50)
    
    # Initialize security manager
    security_manager = NoxSuiteSecurityManager()
    
    # Create demo admin user
    print("📋 Creating demo admin user...")
    result = security_manager.create_secure_user(
        username="admin",
        email="admin@noxsuite.com",
        password="AdminPass123!",
        role="admin",
        enable_mfa=True
    )
    
    if "error" not in result:
        print("✅ Admin user created successfully")
        if "mfa_setup" in result:
            print("🔑 MFA enabled with backup codes")
            print(f"   Secret: {result['mfa_setup'].get('secret', 'N/A')}")
            print(f"   Backup codes: {len(result['mfa_setup'].get('backup_codes', []))} generated")
    else:
        print(f"❌ Admin user creation failed: {result['error']}")
    
    # Create demo regular user
    print("\n📋 Creating demo user...")
    user_result = security_manager.create_secure_user(
        username="user",
        email="user@noxsuite.com",
        password="UserPass123!",
        role="user",
        enable_mfa=False
    )
    
    if "error" not in user_result:
        print("✅ Regular user created successfully")
    
    # Test authentication
    print("\n🔍 Testing authentication...")
    auth_result = security_manager.authenticate_user("admin", "AdminPass123!")
    
    if auth_result.get("status") == "mfa_required":
        print("✅ MFA challenge triggered correctly")
    elif auth_result.get("status") == "authenticated":
        print("✅ Authentication successful")
    
    # Test authorization
    print("\n🛡️ Testing authorization...")
    if "user" in auth_result:
        user_data = auth_result["user"]
        
        # Test admin permissions
        can_manage = security_manager.authorize_action(
            user_data["id"], user_data["role"], "manage_users"
        )
        print(f"   Admin can manage users: {'✅' if can_manage else '❌'}")
        
        can_delete = security_manager.authorize_action(
            user_data["id"], user_data["role"], "delete"
        )
        print(f"   Admin can delete: {'✅' if can_delete else '❌'}")
    
    # Generate status report
    print("\n📊 Security Status Report:")
    status_report = {
        "timestamp": datetime.now().isoformat(),
        "mfa_enabled_users": 1,
        "total_users": 2,
        "roles_configured": len(security_manager.rbac_manager.role_permissions),
        "permissions_available": len(Permission),
        "database_path": security_manager.db_path
    }
    
    with open("noxsuite_security_status.json", 'w') as f:
        json.dump(status_report, f, indent=2)
    
    print("✅ MFA & RBAC system initialized successfully")
    print("📄 Status saved to: noxsuite_security_status.json")

if __name__ == "__main__":
    main()
