#!/usr/bin/env python3
"""
NoxSuite MariaDB Setup and Migration
====================================
Enforces MariaDB-only policy and creates production schema with MFA+RBAC.
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pymysql

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MariaDBEnforcer:
    """Enforces MariaDB-only policy and manages schema"""
    
    def __init__(self):
        self.mariadb_url = os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://noxsuite_user:noxsuite_password_2025@localhost:3306/noxsuite_prod"
        )
        self.admin_url = "mysql+pymysql://root:noxsuite_secure_2025@localhost:3306/"
        
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            admin_engine = create_engine(self.admin_url)
            with admin_engine.connect() as conn:
                # Create database
                conn.execute(text("CREATE DATABASE IF NOT EXISTS noxsuite_prod"))
                
                # Create user and grant privileges
                conn.execute(text("""
                    CREATE USER IF NOT EXISTS 'noxsuite_user'@'%' 
                    IDENTIFIED BY 'noxsuite_password_2025'
                """))
                
                conn.execute(text("""
                    GRANT ALL PRIVILEGES ON noxsuite_prod.* 
                    TO 'noxsuite_user'@'%'
                """))
                
                conn.execute(text("FLUSH PRIVILEGES"))
                conn.commit()
                
            logger.info("✅ MariaDB database and user created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create MariaDB database: {e}")
            return False
    
    def create_schema(self):
        """Create production schema with MFA+RBAC"""
        try:
            engine = create_engine(self.mariadb_url)
            
            # Schema creation SQL
            schema_sql = """
            -- Users table with MFA support
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                mfa_enabled BOOLEAN DEFAULT FALSE,
                mfa_secret VARCHAR(255) NULL,
                backup_codes JSON NULL,
                INDEX idx_username (username),
                INDEX idx_email (email),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            
            -- Roles table
            CREATE TABLE IF NOT EXISTS roles (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                is_system_role BOOLEAN DEFAULT FALSE,
                permissions JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            
            -- User roles junction table
            CREATE TABLE IF NOT EXISTS user_roles (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                role_id INT NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                assigned_by INT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL,
                UNIQUE KEY unique_user_role (user_id, role_id),
                INDEX idx_user_id (user_id),
                INDEX idx_role_id (role_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            
            -- User sessions table
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                refresh_token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_session_token (session_token),
                INDEX idx_user_id (user_id),
                INDEX idx_expires_at (expires_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            
            -- Audit log table
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NULL,
                action VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                details JSON NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_action (action),
                INDEX idx_category (category),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            with engine.connect() as conn:
                # Execute schema creation
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                
                conn.commit()
                
            logger.info("✅ MariaDB schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create MariaDB schema: {e}")
            return False
    
    def seed_default_data(self):
        """Seed default roles and admin user"""
        try:
            engine = create_engine(self.mariadb_url)
            
            with engine.connect() as conn:
                # Insert default roles
                roles_sql = """
                INSERT IGNORE INTO roles (name, description, is_system_role, permissions) VALUES
                ('admin', 'System Administrator', TRUE, '["user.create", "user.read", "user.update", "user.delete", "role.manage", "audit.read"]'),
                ('user', 'Standard User', TRUE, '["user.read_own", "user.update_own"]'),
                ('moderator', 'Content Moderator', FALSE, '["user.read", "content.moderate"]');
                """
                
                # Insert admin user (password: AdminPassword123!)
                admin_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdVA2b1Q3Zp4K2u"
                admin_sql = f"""
                INSERT IGNORE INTO users (username, email, password_hash, is_admin, mfa_enabled) VALUES
                ('admin', 'admin@noxsuite.local', '{admin_password}', TRUE, FALSE);
                """
                
                conn.execute(text(roles_sql))
                conn.execute(text(admin_sql))
                
                # Assign admin role to admin user
                assign_role_sql = """
                INSERT IGNORE INTO user_roles (user_id, role_id, assigned_by)
                SELECT u.id, r.id, u.id 
                FROM users u, roles r 
                WHERE u.username = 'admin' AND r.name = 'admin';
                """
                
                conn.execute(text(assign_role_sql))
                conn.commit()
                
            logger.info("✅ Default data seeded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to seed default data: {e}")
            return False
    
    def validate_mariadb_only(self):
        """Validate no SQLite references remain"""
        mariadb_violations = []
        
        # Check for SQLite in Python files
        for root, dirs, files in os.walk('.'):
            if 'archived' in root or '.git' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'sqlite' in content.lower():
                                mariadb_violations.append(file_path)
                    except:
                        pass
        
        if mariadb_violations:
            logger.error(f"❌ SQLite violations found in: {mariadb_violations}")
            return False
        else:
            logger.info("✅ No SQLite violations detected")
            return True
    
    def health_check(self):
        """Perform MariaDB health check"""
        try:
            engine = create_engine(self.mariadb_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as health"))
                if result.fetchone()[0] == 1:
                    logger.info("✅ MariaDB health check passed")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ MariaDB health check failed: {e}")
            return False
    
    def enforce_mariadb_policy(self):
        """Complete MariaDB enforcement workflow"""
        logger.info("🔒 Starting MariaDB-first enforcement...")
        
        steps = [
            ("Creating database", self.create_database_if_not_exists),
            ("Creating schema", self.create_schema),
            ("Seeding data", self.seed_default_data),
            ("Validating no SQLite", self.validate_mariadb_only),
            ("Health check", self.health_check)
        ]
        
        results = {}
        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            results[step_name] = step_func()
            
            if not results[step_name]:
                logger.error(f"❌ Failed at step: {step_name}")
                return False
        
        logger.info("✅ MariaDB-first enforcement completed successfully")
        return True

if __name__ == "__main__":
    enforcer = MariaDBEnforcer()
    success = enforcer.enforce_mariadb_policy()
    
    if success:
        print("\n🎯 MARIADB ENFORCEMENT COMPLETE")
        print("✅ Database: MariaDB production ready")
        print("✅ Schema: MFA+RBAC tables created")
        print("✅ Data: Admin user and roles seeded")
        print("✅ Validation: No SQLite violations")
        print("✅ Health: MariaDB responding correctly")
        sys.exit(0)
    else:
        print("\n❌ MARIADB ENFORCEMENT FAILED")
        sys.exit(1)
