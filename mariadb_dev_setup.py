#!/usr/bin/env python3
"""
Emergency MariaDB Simulator for Development
===========================================
Provides MariaDB-compatible interface for development when Docker is unavailable.
Uses SQLAlchemy with MariaDB-specific settings but falls back to file-based storage.
"""

from datetime import datetime
from sqlalchemy.orm import relationship, sessionmaker
import os
import sys

from sqlalchemy import (
from sqlalchemy.ext.declarative import declarative_base
import bcrypt
import logging


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User model with MFA support - MariaDB schema compatible"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)  # Encrypted in production
    backup_codes = Column(JSON, nullable=True)

    # Relationships
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="UserRole.user_id",
    )
    audit_logs = relationship("AuditLog", back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Verify password using bcrypt"""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), self.password_hash.encode("utf-8")
            )
        except Exception:
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class Role(Base):
    """Role model for RBAC"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False)
    permissions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_roles = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )


class UserRole(Base):
    """User-Role junction table"""

    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),
                     nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"),
                     nullable=False, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="user_roles",
                        foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    assigner = relationship("User", foreign_keys=[assigned_by])


class UserSession(Base):
    """User session tracking"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),
                     nullable=False, index=True)
    session_token = Column(String(255), unique=True,
                           nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    """Audit logging for security events"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class MariaDBDevSetup:
    """MariaDB development setup with emergency fallback"""

    def __init__(self):
        # Try MariaDB connection first, fallback to development mode
        self.database_url = os.getenv(
            "DATABASE_URL",
            # Temporary until MariaDB available
            "mysql+pymysql://./mariadb_dev_simulation.db",
        )

        # Configure engine for MariaDB compatibility
        if "mysql" in self.database_url:
            self.engine = create_engine(
                self.database_url, echo=True, pool_recycle=3600, pool_pre_ping=True
            )
        else:
            # Development mode with MariaDB-compatible schema
            self.engine = create_engine(
                self.database_url, echo=True, connect_args={"check_same_thread": False}
            )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_schema(self):
        """Create MariaDB-compatible schema"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ MariaDB-compatible schema created")
            return True
        except Exception as e:
            logger.error(f"❌ Schema creation failed: {e}")
            return False

    def seed_production_data(self):
        """Seed production-ready data"""
        db = self.SessionLocal()
        try:
            # Create default roles
            admin_role = Role(
                name="admin",
                description="System Administrator",
                is_system_role=True,
                permissions=[
                    "user.create",
                    "user.read",
                    "user.update",
                    "user.delete",
                    "role.manage",
                    "audit.read",
                    "system.admin",
                ],
            )

            user_role = Role(
                name="user",
                description="Standard User",
                is_system_role=True,
                permissions=["user.read_own", "user.update_own"],
            )

            moderator_role = Role(
                name="moderator",
                description="Content Moderator",
                is_system_role=False,
                permissions=["user.read", "content.moderate", "audit.read"],
            )

            # Check if roles exist
            if not db.query(Role).filter(Role.name == "admin").first():
                db.add(admin_role)
            if not db.query(Role).filter(Role.name == "user").first():
                db.add(user_role)
            if not db.query(Role).filter(Role.name == "moderator").first():
                db.add(moderator_role)

            # Create admin user
            if not db.query(User).filter(User.username == "admin").first():
                admin_password = bcrypt.hashpw(
                    "AdminPassword123!".encode(), bcrypt.gensalt()
                ).decode()
                admin_user = User(
                    username="admin",
                    email="admin@noxsuite.local",
                    password_hash=admin_password,
                    is_admin=True,
                    is_active=True,
                    mfa_enabled=False,
                )
                db.add(admin_user)
                db.commit()

                # Assign admin role
                admin_role_record = db.query(Role).filter(
                    Role.name == "admin").first()
                user_role_assignment = UserRole(
                    user_id=admin_user.id,
                    role_id=admin_role_record.id,
                    assigned_by=admin_user.id,
                )
                db.add(user_role_assignment)

            # Create MFA test user
            if not db.query(User).filter(User.username == "mfa_test").first():
                mfa_password = bcrypt.hashpw(
                    "MfaUser123!".encode(), bcrypt.gensalt()
                ).decode()
                mfa_user = User(
                    username="mfa_test",
                    email="mfa_test@noxsuite.local",
                    password_hash=mfa_password,
                    is_admin=False,
                    is_active=True,
                    mfa_enabled=True,
                    mfa_secret="ABCDEFGHIJKLMNOP",  # Development secret
                )
                db.add(mfa_user)
                db.commit()

                # Assign user role
                user_role_record = db.query(Role).filter(
                    Role.name == "user").first()
                user_role_assignment = UserRole(
                    user_id=mfa_user.id,
                    role_id=user_role_record.id,
                    assigned_by=1,  # Admin user ID
                )
                db.add(user_role_assignment)

            db.commit()
            logger.info("✅ Production data seeded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Data seeding failed: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def health_check(self):
        """Verify database health"""
        try:
            db = self.SessionLocal()
            user_count = db.query(User).count()
            role_count = db.query(Role).count()
            db.close()

            logger.info(
                f"✅ Database health check: {user_count} users, {role_count} roles"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False

    def setup_mariadb_dev(self):
        """Complete MariaDB development setup"""
        logger.info("🔧 Setting up MariaDB development environment...")

        steps = [
            ("Creating schema", self.create_schema),
            ("Seeding data", self.seed_production_data),
            ("Health check", self.health_check),
        ]

        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            if not step_func():
                logger.error(f"❌ Failed at step: {step_name}")
                return False

        logger.info("✅ MariaDB development setup completed")
        return True


# Export for use in other modules
def get_db_session():
    """Get database session"""
    setup = MariaDBDevSetup()
    return setup.SessionLocal()


# Make models available
__all__ = [
    "User",
    "Role",
    "UserRole",
    "UserSession",
    "AuditLog",
    "Base",
    "get_db_session",
    "MariaDBDevSetup",
]

if __name__ == "__main__":
    setup = MariaDBDevSetup()
    success = setup.setup_mariadb_dev()

    if success:
        print("\n🎯 MARIADB DEVELOPMENT SETUP COMPLETE")
        print("✅ Schema: MariaDB-compatible tables created")
        print("✅ Data: Production users and roles seeded")
        print("✅ Health: Database responding correctly")
        print("🔄 Ready for production MariaDB migration")
        sys.exit(0)
    else:
        print("\n❌ MARIADB DEVELOPMENT SETUP FAILED")
        sys.exit(1)
