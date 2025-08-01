#!/usr/bin/env python3
"""
NoxSuite Database Setup Script
=============================

Sets up MariaDB and configures Alembic migrations for NoxSuite.
This is a priority item from the comprehensive audit results.

Author: NoxSuite Development Team
Date: July 31, 2025
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class DatabaseSetupManager:
    """Manages NoxSuite database setup and migration"""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.setup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.setup_log = []
        
    def log_action(self, action: str, status: str = "INFO"):
        """Log setup actions"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {status}: {action}"
        self.setup_log.append(log_entry)
        print(log_entry)
    
    def setup_mariadb_docker(self):
        """Set up MariaDB using Docker"""
        self.log_action("Setting up MariaDB Docker container...")
        
        # Check if Docker is available
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            self.log_action("Docker is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_action("Docker not found! Please install Docker first", "ERROR")
            return False
        
        # Stop existing container if running
        try:
            subprocess.run(['docker', 'stop', 'noxsuite-mariadb'], 
                         capture_output=True, check=False)
            subprocess.run(['docker', 'rm', 'noxsuite-mariadb'], 
                         capture_output=True, check=False)
            self.log_action("Cleaned up existing MariaDB container")
        except:
            pass
        
        # Start new MariaDB container
        docker_cmd = [
            'docker', 'run', '-d',
            '--name', 'noxsuite-mariadb',
            '-e', 'MYSQL_ROOT_PASSWORD=noxsuite_root_2025',
            '-e', 'MYSQL_DATABASE=noxsuite',
            '-e', 'MYSQL_USER=noxsuite_user',
            '-e', 'MYSQL_PASSWORD=noxsuite_secure_pass_2025',
            '-p', '3306:3306',
            '--restart', 'unless-stopped',
            'mariadb:10.6'
        ]
        
        try:
            result = subprocess.run(docker_cmd, check=True, capture_output=True, text=True)
            container_id = result.stdout.strip()
            self.log_action(f"MariaDB container started: {container_id[:12]}")
            
            # Wait for MariaDB to be ready
            self.log_action("Waiting for MariaDB to be ready...")
            self.wait_for_mariadb()
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_action(f"Failed to start MariaDB container: {e}", "ERROR")
            return False
    
    def wait_for_mariadb(self, max_attempts=30):
        """Wait for MariaDB to be ready"""
        for attempt in range(max_attempts):
            try:
                # Test connection using docker exec
                test_cmd = [
                    'docker', 'exec', 'noxsuite-mariadb',
                    'mysql', '-u', 'noxsuite_user', 
                    '-pnoxsuite_secure_pass_2025',
                    '-e', 'SELECT 1;'
                ]
                subprocess.run(test_cmd, check=True, capture_output=True)
                self.log_action("MariaDB is ready!")
                return True
            except subprocess.CalledProcessError:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue
                else:
                    self.log_action("MariaDB failed to become ready", "ERROR")
                    return False
        return False
    
    def create_database_config(self):
        """Create database configuration file"""
        self.log_action("Creating database configuration...")
        
        config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "noxsuite",
                "username": "noxsuite_user",
                "password": "noxsuite_secure_pass_2025",
                "driver": "mariadb+pymysql"
            },
            "connection_string": "mysql+pymysql://noxsuite_user:noxsuite_secure_pass_2025@localhost:3306/noxsuite",
            "alembic_version": "1.12.0",
            "created": self.setup_timestamp
        }
        
        config_dir = self.workspace_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "database_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_action(f"Database config saved: {config_file}")
        return config
    
    def setup_alembic(self):
        """Set up Alembic for database migrations"""
        self.log_action("Setting up Alembic...")
        
        # Check if Alembic is installed
        try:
            subprocess.run(['alembic', '--version'], check=True, capture_output=True)
            self.log_action("Alembic is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_action("Installing Alembic...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'alembic', 'pymysql'], check=True)
                self.log_action("Alembic installed successfully")
            except subprocess.CalledProcessError:
                self.log_action("Failed to install Alembic", "ERROR")
                return False
        
        # Initialize Alembic if not already done
        alembic_ini = self.workspace_root / "alembic.ini"
        if not alembic_ini.exists():
            self.log_action("Initializing Alembic...")
            try:
                subprocess.run(['alembic', 'init', 'migrations'], check=True, cwd=self.workspace_root)
                self.log_action("Alembic initialized successfully")
            except subprocess.CalledProcessError:
                self.log_action("Failed to initialize Alembic", "ERROR")
                return False
        else:
            self.log_action("Alembic already initialized")
        
        # Update alembic.ini with database URL
        self.update_alembic_config()
        return True
    
    def update_alembic_config(self):
        """Update Alembic configuration with MariaDB connection"""
        alembic_ini = self.workspace_root / "alembic.ini"
        
        if alembic_ini.exists():
            with open(alembic_ini, 'r') as f:
                content = f.read()
            
            # Update database URL
            db_url = "mysql+pymysql://noxsuite_user:noxsuite_secure_pass_2025@localhost:3306/noxsuite"
            
            # Replace the sqlalchemy.url line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('sqlalchemy.url'):
                    lines[i] = f"sqlalchemy.url = {db_url}"
                    break
            
            with open(alembic_ini, 'w') as f:
                f.write('\n'.join(lines))
            
            self.log_action("Updated Alembic configuration with MariaDB URL")
    
    def create_database_models(self):
        """Create database models for NoxSuite"""
        self.log_action("Creating database models...")
        
        models_dir = self.workspace_root / "backend" / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = models_dir / "__init__.py"
        with open(init_file, 'w') as f:
            f.write('"""NoxSuite Database Models"""\n')
        
        # Create user.py model
        user_model = models_dir / "user.py"
        user_content = '''"""User model for NoxSuite authentication system"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    """User model with MFA and RBAC support"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # MFA fields
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(32), nullable=True)
    backup_codes = Column(Text, nullable=True)
    
    # User status
    active = Column(Boolean, default=True)
    confirmed = Column(Boolean, default=False)
    
    # RBAC
    role = Column(String(50), default='user')
    permissions = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'mfa_enabled': self.mfa_enabled,
            'active': self.active,
            'confirmed': self.confirmed,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
'''
        
        with open(user_model, 'w') as f:
            f.write(user_content)
        
        # Create roles.py model
        roles_model = models_dir / "roles.py"
        roles_content = '''"""Roles and permissions model for RBAC"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Role(Base):
    """Role model for RBAC system"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=False)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Permission(Base):
    """Permission model"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'resource': self.resource,
            'action': self.action,
            'description': self.description
        }
'''
        
        with open(roles_model, 'w') as f:
            f.write(roles_content)
        
        # Create audit_log.py model
        audit_model = models_dir / "audit_log.py"
        audit_content = '''"""Audit log model for security tracking"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AuditLog(Base):
    """Audit log for tracking user actions"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)  # JSON string
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
'''
        
        with open(audit_model, 'w') as f:
            f.write(audit_content)
        
        self.log_action("Database models created successfully")
        return True
    
    def create_initial_migration(self):
        """Create initial Alembic migration"""
        self.log_action("Creating initial migration...")
        
        try:
            # Create migration
            subprocess.run([
                'alembic', 'revision', '--autogenerate', 
                '-m', 'Initial NoxSuite migration'
            ], check=True, cwd=self.workspace_root)
            
            self.log_action("Initial migration created")
            
            # Run migration
            subprocess.run([
                'alembic', 'upgrade', 'head'
            ], check=True, cwd=self.workspace_root)
            
            self.log_action("Initial migration applied successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_action(f"Migration failed: {e}", "ERROR")
            return False
    
    def create_database_connection(self):
        """Create database connection module"""
        self.log_action("Creating database connection module...")
        
        db_dir = self.workspace_root / "backend" / "database"
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = db_dir / "__init__.py"
        with open(init_file, 'w') as f:
            f.write('"""NoxSuite Database Package"""\n')
        
        # Create connection.py
        connection_file = db_dir / "connection.py"
        connection_content = '''"""Database connection and session management"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'mysql+pymysql://noxsuite_user:noxsuite_secure_pass_2025@localhost:3306/noxsuite'
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv('DATABASE_ECHO', 'False').lower() == 'true'
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)

@contextmanager
def get_db_session():
    """Get database session with automatic cleanup"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db():
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    from backend.models.user import Base as UserBase
    from backend.models.roles import Base as RoleBase  
    from backend.models.audit_log import Base as AuditBase
    
    # Create all tables
    UserBase.metadata.create_all(bind=engine)
    RoleBase.metadata.create_all(bind=engine)
    AuditBase.metadata.create_all(bind=engine)
    
    print("Database tables created successfully")

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            return result.fetchone()[0] == 1
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False
'''
        
        with open(connection_file, 'w') as f:
            f.write(connection_content)
        
        self.log_action("Database connection module created")
        return True
    
    def update_requirements(self):
        """Update requirements with database dependencies"""
        self.log_action("Updating requirements.txt...")
        
        requirements_file = self.workspace_root / "requirements.txt"
        
        # Read existing requirements
        existing_requirements = set()
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                existing_requirements = set(line.strip() for line in f if line.strip())
        
        # Add database requirements
        db_requirements = {
            'SQLAlchemy>=1.4.0',
            'alembic>=1.12.0',
            'PyMySQL>=1.0.0',
            'cryptography>=3.4.0'
        }
        
        # Merge requirements
        all_requirements = existing_requirements.union(db_requirements)
        
        # Write updated requirements
        with open(requirements_file, 'w') as f:
            for req in sorted(all_requirements):
                f.write(f"{req}\n")
        
        self.log_action("Requirements updated with database dependencies")
    
    def generate_setup_report(self):
        """Generate setup completion report"""
        report = {
            'timestamp': self.setup_timestamp,
            'setup_log': self.setup_log,
            'database_config': {
                'host': 'localhost',
                'port': 3306,
                'database': 'noxsuite',
                'username': 'noxsuite_user'
            },
            'components_created': [
                'MariaDB Docker container',
                'Database models (User, Role, Permission, AuditLog)',
                'Alembic migration system',
                'Database connection module',
                'Updated requirements.txt'
            ],
            'next_steps': [
                'Test database connection',
                'Create initial admin user',
                'Update API routes to use database',
                'Run integration tests'
            ]
        }
        
        report_file = self.workspace_root / f"database_setup_report_{self.setup_timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_action(f"Setup report saved: {report_file}")
        return report
    
    def run_setup(self):
        """Run complete database setup"""
        self.log_action("Starting NoxSuite Database Setup", "INFO")
        self.log_action("=" * 50)
        
        try:
            # Step 1: Setup MariaDB
            if not self.setup_mariadb_docker():
                return False
            
            # Step 2: Create configuration
            self.create_database_config()
            
            # Step 3: Setup Alembic
            if not self.setup_alembic():
                return False
            
            # Step 4: Create models
            self.create_database_models()
            
            # Step 5: Create database connection
            self.create_database_connection()
            
            # Step 6: Update requirements
            self.update_requirements()
            
            # Step 7: Generate report
            report = self.generate_setup_report()
            
            self.log_action("=" * 50)
            self.log_action("Database setup completed successfully!", "SUCCESS")
            
            # Print summary
            print("\nSETUP SUMMARY:")
            print(f"- MariaDB container: noxsuite-mariadb")
            print(f"- Database: noxsuite")
            print(f"- User: noxsuite_user")
            print(f"- Models created: 4 (User, Role, Permission, AuditLog)")
            print(f"- Setup report: {report_file}")
            print("\nNEXT STEPS:")
            print("1. Test connection: python -c 'from backend.database.connection import test_connection; print(test_connection())'")
            print("2. Run migrations: alembic upgrade head")
            print("3. Create admin user")
            print("4. Update API routes")
            
            return True
            
        except Exception as e:
            self.log_action(f"Setup failed: {e}", "ERROR")
            return False


def main():
    """Main execution"""
    print("NoxSuite Database Setup")
    print("=" * 40)
    
    setup_manager = DatabaseSetupManager()
    success = setup_manager.run_setup()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
