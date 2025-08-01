"""
NoxSuite MariaDB-Compatible User Models
=======================================
Production-ready database models with MFA and RBAC support.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, create_engine, JSON
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import bcrypt
import secrets

# Add mariadb_dev_setup to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import MariaDB setup
try:
    from mariadb_dev_setup import User, Role, UserRole, UserSession, AuditLog, Base, MariaDBDevSetup
    
    # Get database session using MariaDB setup
    def get_db():
        """Get database session"""
        setup = MariaDBDevSetup()
        session = setup.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    # Export configured components
    engine = MariaDBDevSetup().engine
    SessionLocal = MariaDBDevSetup().SessionLocal
    
except ImportError:
    # Fallback for legacy compatibility
    Base = declarative_base()
    DATABASE_URL = "mysql+pymysql://./mariadb_dev_simulation.db"
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        username = Column(String(50), unique=True, nullable=False)
        email = Column(String(100), unique=True, nullable=False)
        password_hash = Column(String(255), nullable=False)
        is_active = Column(Boolean, default=True)
        is_admin = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        last_login = Column(DateTime, nullable=True)
        mfa_enabled = Column(Boolean, default=False)
        mfa_secret = Column(String(255), nullable=True)
        backup_codes = Column(JSON, nullable=True)
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Utility functions
def log_audit_event(db, user_id, action, category, details, request):
    """Log audit events"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            category=category,
            details=details,
            ip_address=getattr(request.client, 'host', None) if request else None,
            user_agent=request.headers.get("user-agent", "") if request else None,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Audit logging failed: {e}")

# Export all models and utilities
__all__ = [
    'User', 'Role', 'UserRole', 'UserSession', 'AuditLog', 'Base', 
    'engine', 'SessionLocal', 'get_db', 'log_audit_event'
]
