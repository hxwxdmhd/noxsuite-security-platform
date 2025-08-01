from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Ultimate Suite v11.0 - Unified Models Implementation
====================================================

This is the SINGLE, UNIFIED models implementation that consolidates:
- Database models from all server implementations
- User management models
- System metrics models
- Audit logging models
- Plugin registry models

ARCHITECTURAL PRINCIPLE: ONE MODELS FILE FOR ALL DATA
"""

import hashlib
import json
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pymysql

# Logging
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component UserRole needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for UserRole functionality
    3. Solution: Implement UserRole with SOLID principles and enterprise patterns
    4. Validation: Test UserRole with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """User roles enumeration"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

class AuditAction(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component AuditAction needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for AuditAction functionality
    3. Solution: Implement AuditAction with SOLID principles and enterprise patterns
    4. Validation: Test AuditAction with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Audit action types"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"
    SYSTEM = "system"
    PLUGIN = "plugin"

class AuditResult(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component AuditResult needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for AuditResult functionality
    3. Solution: Implement AuditResult with SOLID principles and enterprise patterns
    4. Validation: Test AuditResult with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Audit result types"""
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class User:
    """
    REASONING CHAIN:
    1. Problem: System component User needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for User functionality
    3. Solution: Implement User with SOLID principles and enterprise patterns
    4. Validation: Test User with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """User model"""
    id: int = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = None
    last_login: datetime = None
    login_attempts: int = 0
    locked_until: datetime = None
    two_factor_enabled: bool = False
    two_factor_secret: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
    """
    Enhanced __post_init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __post_init__ with enterprise-grade patterns and error handling
    4. Validation: Test __post_init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def set_password(self, password: str) -> None:
    """
    REASONING CHAIN:
    1. Problem: Data modification needs controlled state management
    2. Analysis: Setter method requires validation and state consistency
    3. Solution: Implement set_password with enterprise-grade patterns and error handling
    4. Validation: Test set_password with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Set password with hashing"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function check_password needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_password operation
    3. Solution: Implement check_password with enterprise-grade patterns and error handling
    4. Validation: Test check_password with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check password against hash"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def is_locked(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function is_locked needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_locked operation
    3. Solution: Implement is_locked with enterprise-grade patterns and error handling
    4. Validation: Test is_locked with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_attempts': self.login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'two_factor_enabled': self.two_factor_enabled,
            'preferences': self.preferences,
            'metadata': self.metadata
        }

# Database dependencies
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from sqlalchemy import (
        JSON,
        Boolean,
        Column,
        DateTime,
        Float,
        ForeignKey,
        Index,
        Integer,
        MetaData,
        String,
        Table,
        Text,
        UniqueConstraint,
        create_engine,
        event,
        text,
    )
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import (
        Session,
        relationship,
        scoped_session,
        sessionmaker,
        validates,
    )
    from sqlalchemy.pool import QueuePool
    
except ImportError as e:
    logger.info(f"Critical database dependency missing: {e}")
    logger.info("Please install required packages:")
    logger.info("pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Database metadata for manual table creation
db_metadata = MetaData()

class SystemStatusEnum(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component SystemStatusEnum needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SystemStatusEnum functionality
    3. Solution: Implement SystemStatusEnum with SOLID principles and enterprise patterns
    4. Validation: Test SystemStatusEnum with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """System status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    WARNING = "warning"

class LogLevelEnum(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component LogLevelEnum needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for LogLevelEnum functionality
    3. Solution: Implement LogLevelEnum with SOLID principles and enterprise patterns
    4. Validation: Test LogLevelEnum with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class PluginStatusEnum(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component PluginStatusEnum needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginStatusEnum functionality
    3. Solution: Implement PluginStatusEnum with SOLID principles and enterprise patterns
    4. Validation: Test PluginStatusEnum with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    ERROR = "error"
    LOADING = "loading"

class UserRoleEnum(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component UserRoleEnum needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for UserRoleEnum functionality
    3. Solution: Implement UserRoleEnum with SOLID principles and enterprise patterns
    4. Validation: Test UserRoleEnum with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """User role enumeration"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

# Association tables for many-to-many relationships
user_role_association = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

plugin_dependency_association = Table(
    'plugin_dependencies',
    Base.metadata,
    Column('plugin_id', UUID(as_uuid=True), ForeignKey('plugin_registry.id'), primary_key=True),
    Column('dependency_id', UUID(as_uuid=True), ForeignKey('plugin_registry.id'), primary_key=True)
)

class User(Base):
    """
    REASONING CHAIN:
    1. Problem: System component User needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for User functionality
    3. Solution: Implement User with SOLID principles and enterprise patterns
    4. Validation: Test User with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    
    # Status and permissions
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Profile information
    profile_data = Column(JSONB, default=dict)
    preferences = Column(JSONB, default=dict)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    verification_token = Column(String(255))
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("Role", secondary=user_role_association, back_populates="users")
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<User {self.username}>"
    
    @validates('email')
    def validate_email(self, key, address):
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_email with enterprise-grade patterns and error handling
    4. Validation: Test validate_email with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Validate email format"""
        if '@' not in address:
            raise ValueError("Invalid email address")
        return address
    
    def set_password(self, password: str):
    """
    REASONING CHAIN:
    1. Problem: Data modification needs controlled state management
    2. Analysis: Setter method requires validation and state consistency
    3. Solution: Implement set_password with enterprise-grade patterns and error handling
    4. Validation: Test set_password with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Set password hash"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function check_password needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_password operation
    3. Solution: Implement check_password with enterprise-grade patterns and error handling
    4. Validation: Test check_password with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check password"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_data': self.profile_data,
            'preferences': self.preferences
        }

class Role(Base):
    """
    REASONING CHAIN:
    1. Problem: System component Role needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for Role functionality
    3. Solution: Implement Role with SOLID principles and enterprise patterns
    4. Validation: Test Role with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Role model for role-based access control"""
    __tablename__ = 'roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(Text)
    
    # Permissions
    permissions = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_role_association, back_populates="roles")
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<Role {self.name}>"
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserSession(Base):
    """
    REASONING CHAIN:
    1. Problem: System component UserSession needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for UserSession functionality
    3. Solution: Implement UserSession with SOLID principles and enterprise patterns
    4. Validation: Test UserSession with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """User session model for session management"""
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    
    # Session metadata
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    device_info = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    
    # Security
    csrf_token = Column(String(255))
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<UserSession {self.session_token[:8]}...>"
    
    def is_expired(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function is_expired needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_expired operation
    3. Solution: Implement is_expired with enterprise-grade patterns and error handling
    4. Validation: Test is_expired with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if session is expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function is_valid needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_valid operation
    3. Solution: Implement is_valid with enterprise-grade patterns and error handling
    4. Validation: Test is_valid with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if session is valid"""
        return self.is_active and not self.is_revoked and not self.is_expired()
    
    def refresh(self, expires_in: int = 3600):
    """
    REASONING CHAIN:
    1. Problem: Function refresh needs clear operational definition
    2. Analysis: Implementation requires specific logic for refresh operation
    3. Solution: Implement refresh with enterprise-grade patterns and error handling
    4. Validation: Test refresh with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Refresh session"""
        self.last_activity = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'session_token': self.session_token,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_info': self.device_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_revoked': self.is_revoked,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid()
        }

class SystemMetrics(Base):
    """
    REASONING CHAIN:
    1. Problem: System component SystemMetrics needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SystemMetrics functionality
    3. Solution: Implement SystemMetrics with SOLID principles and enterprise patterns
    4. Validation: Test SystemMetrics with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """System metrics model for monitoring"""
    __tablename__ = 'system_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metric identification
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram, etc.
    
    # Metric data
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    
    # Metadata
    tags = Column(JSONB, default=dict)
    metadata = Column(JSONB, default=dict)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'metric_name', 'timestamp'),
        Index('idx_metrics_type_timestamp', 'metric_type', 'timestamp'),
        Index('idx_metrics_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<SystemMetrics {self.metric_name}={self.value}>"
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'metric_name': self.metric_name,
            'metric_type': self.metric_type,
            'value': self.value,
            'unit': self.unit,
            'tags': self.tags,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemLog(Base):
    """
    REASONING CHAIN:
    1. Problem: System component SystemLog needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SystemLog functionality
    3. Solution: Implement SystemLog with SOLID principles and enterprise patterns
    4. Validation: Test SystemLog with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """System log model for centralized logging"""
    __tablename__ = 'system_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Log identification
    level = Column(String(20), nullable=False)
    logger_name = Column(String(100), nullable=False)
    
    # Log content
    message = Column(Text, nullable=False)
    formatted_message = Column(Text)
    
    # Context
    module = Column(String(100))
    function = Column(String(100))
    line_number = Column(Integer)
    
    # Request context
    request_id = Column(String(100))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    session_id = Column(UUID(as_uuid=True), ForeignKey('user_sessions.id'))
    
    # Additional data
    extra_data = Column(JSONB, default=dict)
    stack_trace = Column(Text)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_logs_level_timestamp', 'level', 'timestamp'),
        Index('idx_logs_logger_timestamp', 'logger_name', 'timestamp'),
        Index('idx_logs_timestamp', 'timestamp'),
        Index('idx_logs_request_id', 'request_id'),
    )
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<SystemLog {self.level}: {self.message[:50]}...>"
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'level': self.level,
            'logger_name': self.logger_name,
            'message': self.message,
            'formatted_message': self.formatted_message,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'request_id': self.request_id,
            'user_id': str(self.user_id) if self.user_id else None,
            'session_id': str(self.session_id) if self.session_id else None,
            'extra_data': self.extra_data,
            'stack_trace': self.stack_trace,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class PluginRegistry(Base):
    """
    REASONING CHAIN:
    1. Problem: System component PluginRegistry needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginRegistry functionality
    3. Solution: Implement PluginRegistry with SOLID principles and enterprise patterns
    4. Validation: Test PluginRegistry with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin registry model for plugin management"""
    __tablename__ = 'plugin_registry'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Plugin identification
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200))
    description = Column(Text)
    
    # Plugin metadata
    version = Column(String(50))
    author = Column(String(100))
    author_email = Column(String(120))
    homepage = Column(String(200))
    
    # Plugin file information
    file_path = Column(String(500))
    file_hash = Column(String(64))  # SHA-256 hash
    file_size = Column(Integer)
    
    # Plugin status
    status = Column(String(20), default=PluginStatusEnum.INACTIVE.value)
    is_enabled = Column(Boolean, default=False)
    is_core = Column(Boolean, default=False)
    
    # Plugin configuration
    config_schema = Column(JSONB, default=dict)
    config_data = Column(JSONB, default=dict)
    
    # Runtime information
    load_order = Column(Integer, default=0)
    dependencies = Column(JSONB, default=list)
    api_version = Column(String(20))
    
    # Statistics
    install_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    installed_at = Column(DateTime)
    last_loaded = Column(DateTime)
    last_error_at = Column(DateTime)
    
    # Relationships
    plugin_dependencies = relationship(
        "PluginRegistry",
        secondary=plugin_dependency_association,
        primaryjoin=id == plugin_dependency_association.c.plugin_id,
        secondaryjoin=id == plugin_dependency_association.c.dependency_id,
        back_populates="dependent_plugins"
    )
    
    dependent_plugins = relationship(
        "PluginRegistry",
        secondary=plugin_dependency_association,
        primaryjoin=id == plugin_dependency_association.c.dependency_id,
        secondaryjoin=id == plugin_dependency_association.c.plugin_id,
        back_populates="plugin_dependencies"
    )
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<PluginRegistry {self.name}>"
    
    def is_active(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function is_active needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_active operation
    3. Solution: Implement is_active with enterprise-grade patterns and error handling
    4. Validation: Test is_active with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if plugin is active"""
        return self.status == PluginStatusEnum.ACTIVE.value and self.is_enabled
    
    def calculate_file_hash(self) -> str:
    """
    REASONING CHAIN:
    1. Problem: Function calculate_file_hash needs clear operational definition
    2. Analysis: Implementation requires specific logic for calculate_file_hash operation
    3. Solution: Implement calculate_file_hash with enterprise-grade patterns and error handling
    4. Validation: Test calculate_file_hash with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Calculate file hash"""
        if not self.file_path or not os.path.exists(self.file_path):
            return ""
        
        hash_sha256 = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def update_file_info(self):
    """
    REASONING CHAIN:
    1. Problem: Function update_file_info needs clear operational definition
    2. Analysis: Implementation requires specific logic for update_file_info operation
    3. Solution: Implement update_file_info with enterprise-grade patterns and error handling
    4. Validation: Test update_file_info with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Update file information"""
        if self.file_path and os.path.exists(self.file_path):
            stat = os.stat(self.file_path)
            self.file_size = stat.st_size
            self.file_hash = self.calculate_file_hash()
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'author_email': self.author_email,
            'homepage': self.homepage,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'status': self.status,
            'is_enabled': self.is_enabled,
            'is_core': self.is_core,
            'config_schema': self.config_schema,
            'config_data': self.config_data,
            'load_order': self.load_order,
            'dependencies': self.dependencies,
            'api_version': self.api_version,
            'install_count': self.install_count,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'installed_at': self.installed_at.isoformat() if self.installed_at else None,
            'last_loaded': self.last_loaded.isoformat() if self.last_loaded else None,
            'last_error_at': self.last_error_at.isoformat() if self.last_error_at else None,
            'is_active': self.is_active()
        }

class SystemConfiguration(Base):
    """
    REASONING CHAIN:
    1. Problem: System component SystemConfiguration needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SystemConfiguration functionality
    3. Solution: Implement SystemConfiguration with SOLID principles and enterprise patterns
    4. Validation: Test SystemConfiguration with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """System configuration model for application settings"""
    __tablename__ = 'system_configuration'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Configuration identification
    key = Column(String(200), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    
    # Configuration data
    value = Column(JSONB, nullable=False)
    default_value = Column(JSONB)
    
    # Metadata
    description = Column(Text)
    data_type = Column(String(50))  # string, integer, float, boolean, json, etc.
    validation_rules = Column(JSONB, default=dict)
    
    # Security
    is_sensitive = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_config_category', 'category'),
        Index('idx_config_key', 'key'),
    )
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<SystemConfiguration {self.key}>"
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'key': self.key,
            'category': self.category,
            'value': self.value,
            'default_value': self.default_value,
            'description': self.description,
            'data_type': self.data_type,
            'validation_rules': self.validation_rules,
            'is_sensitive': self.is_sensitive,
            'is_readonly': self.is_readonly,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SystemEvent(Base):
    """
    REASONING CHAIN:
    1. Problem: System component SystemEvent needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SystemEvent functionality
    3. Solution: Implement SystemEvent with SOLID principles and enterprise patterns
    4. Validation: Test SystemEvent with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """System event model for event tracking"""
    __tablename__ = 'system_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_type = Column(String(100), nullable=False)
    event_name = Column(String(200), nullable=False)
    
    # Event data
    event_data = Column(JSONB, default=dict)
    
    # Context
    source = Column(String(100))  # plugin, core, api, etc.
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    session_id = Column(UUID(as_uuid=True), ForeignKey('user_sessions.id'))
    
    # Metadata
    severity = Column(String(20), default='info')
    tags = Column(JSONB, default=list)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_events_type_timestamp', 'event_type', 'timestamp'),
        Index('idx_events_name_timestamp', 'event_name', 'timestamp'),
        Index('idx_events_source_timestamp', 'source', 'timestamp'),
        Index('idx_events_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
    """
    Enhanced __repr__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __repr__ with enterprise-grade patterns and error handling
    4. Validation: Test __repr__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return f"<SystemEvent {self.event_type}: {self.event_name}>"
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'event_name': self.event_name,
            'event_data': self.event_data,
            'source': self.source,
            'user_id': str(self.user_id) if self.user_id else None,
            'session_id': str(self.session_id) if self.session_id else None,
            'severity': self.severity,
            'tags': self.tags,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class DatabaseManager:
    """
    REASONING CHAIN:
    1. Problem: Complex system needs centralized management interface
    2. Analysis: Manager class requires coordinated resource handling and lifecycle management
    3. Solution: Implement DatabaseManager with SOLID principles and enterprise patterns
    4. Validation: Test DatabaseManager with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Unified database manager for all database operations"""
    
    def __init__(self, database_url: str):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.Session = None
        
        self._setup_engine()
        self._setup_session_factory()
    
    def _setup_engine(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _setup_engine with enterprise-grade patterns and error handling
    4. Validation: Test _setup_engine with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup database engine"""
        try:
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # Set to True for SQL debugging
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _setup_session_factory(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _setup_session_factory with enterprise-grade patterns and error handling
    4. Validation: Test _setup_session_factory with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup session factory"""
        try:
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            logger.info("Database session factory initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize session factory: {e}")
            raise
    
    def create_tables(self):
    """
    REASONING CHAIN:
    1. Problem: Function create_tables needs clear operational definition
    2. Analysis: Implementation requires specific logic for create_tables operation
    3. Solution: Implement create_tables with enterprise-grade patterns and error handling
    4. Validation: Test create_tables with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create all database tables"""
        try:
            # Create all tables
            Base.metadata.create_all(self.engine)
            logger.info("All database tables created successfully")
            
            # Insert default data
            self._insert_default_data()
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def _insert_default_data(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _insert_default_data with enterprise-grade patterns and error handling
    4. Validation: Test _insert_default_data with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Insert default data into tables"""
        try:
            session = self.Session()
            
            # Create default roles
            roles_data = [
                {'name': 'admin', 'description': 'Administrator role with full permissions'},
                {'name': 'moderator', 'description': 'Moderator role with limited permissions'},
                {'name': 'user', 'description': 'Standard user role'},
                {'name': 'guest', 'description': 'Guest user role with read-only access'}
            ]
            
            for role_data in roles_data:
                existing_role = session.query(Role).filter_by(name=role_data['name']).first()
                if not existing_role:
                    role = Role(**role_data)
                    session.add(role)
            
            # Create default configuration
            config_data = [
                {
                    'key': 'system.version',
                    'category': 'system',
                    'value': '11.0.0',
                    'description': 'System version',
                    'data_type': 'string',
                    'is_readonly': True
                },
                {
                    'key': 'system.debug',
                    'category': 'system',
                    'value': False,
                    'description': 'Enable debug mode',
                    'data_type': 'boolean'
                },
                {
                    'key': 'security.session_timeout',
                    'category': 'security',
                    'value': 3600,
                    'description': 'Session timeout in seconds',
                    'data_type': 'integer'
                },
                {
                    'key': 'security.max_login_attempts',
                    'category': 'security',
                    'value': 5,
                    'description': 'Maximum login attempts before lockout',
                    'data_type': 'integer'
                }
            ]
            
            for config_item in config_data:
                existing_config = session.query(SystemConfiguration).filter_by(key=config_item['key']).first()
                if not existing_config:
                    config = SystemConfiguration(**config_item)
                    session.add(config)
            
            session.commit()
            logger.info("Default data inserted successfully")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to insert default data: {e}")
            raise
        finally:
            session.close()
    
    def get_session(self) -> Session:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_session with enterprise-grade patterns and error handling
    4. Validation: Test get_session with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get database session"""
        return self.Session()
    
    def close_session(self, session: Session):
    """
    REASONING CHAIN:
    1. Problem: Function close_session needs clear operational definition
    2. Analysis: Implementation requires specific logic for close_session operation
    3. Solution: Implement close_session with enterprise-grade patterns and error handling
    4. Validation: Test close_session with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Close database session"""
        session.close()
    
    def cleanup_old_data(self, days_old: int = 30):
    """
    REASONING CHAIN:
    1. Problem: Function cleanup_old_data needs clear operational definition
    2. Analysis: Implementation requires specific logic for cleanup_old_data operation
    3. Solution: Implement cleanup_old_data with enterprise-grade patterns and error handling
    4. Validation: Test cleanup_old_data with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Cleanup old data from database"""
        try:
            session = self.Session()
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Cleanup old metrics
            deleted_metrics = session.query(SystemMetrics).filter(
                SystemMetrics.timestamp < cutoff_date
            ).delete()
            
            # Cleanup old logs
            deleted_logs = session.query(SystemLog).filter(
                SystemLog.timestamp < cutoff_date
            ).delete()
            
            # Cleanup old events
            deleted_events = session.query(SystemEvent).filter(
                SystemEvent.timestamp < cutoff_date
            ).delete()
            
            # Cleanup expired sessions
            deleted_sessions = session.query(UserSession).filter(
                UserSession.expires_at < datetime.utcnow()
            ).delete()
            
            session.commit()
            
            logger.info(f"Cleanup completed: {deleted_metrics} metrics, {deleted_logs} logs, "
                       f"{deleted_events} events, {deleted_sessions} sessions")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cleanup old data: {e}")
            raise
        finally:
            session.close()
    
    def get_system_stats(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_system_stats with enterprise-grade patterns and error handling
    4. Validation: Test get_system_stats with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get system statistics"""
        try:
            session = self.Session()
            
            stats = {
                'users': {
                    'total': session.query(User).count(),
                    'active': session.query(User).filter(User.is_active == True).count(),
                    'verified': session.query(User).filter(User.is_verified == True).count(),
                    'admins': session.query(User).filter(User.is_admin == True).count()
                },
                'sessions': {
                    'total': session.query(UserSession).count(),
                    'active': session.query(UserSession).filter(UserSession.is_active == True).count(),
                    'expired': session.query(UserSession).filter(UserSession.expires_at < datetime.utcnow()).count()
                },
                'plugins': {
                    'total': session.query(PluginRegistry).count(),
                    'enabled': session.query(PluginRegistry).filter(PluginRegistry.is_enabled == True).count(),
                    'active': session.query(PluginRegistry).filter(PluginRegistry.status == PluginStatusEnum.ACTIVE.value).count()
                },
                'logs': {
                    'total': session.query(SystemLog).count(),
                    'errors': session.query(SystemLog).filter(SystemLog.level == 'error').count(),
                    'warnings': session.query(SystemLog).filter(SystemLog.level == 'warning').count()
                },
                'events': {
                    'total': session.query(SystemEvent).count(),
                    'today': session.query(SystemEvent).filter(
                        SystemEvent.timestamp >= datetime.utcnow().date()
                    ).count()
                },
                'metrics': {
                    'total': session.query(SystemMetrics).count(),
                    'today': session.query(SystemMetrics).filter(
                        SystemMetrics.timestamp >= datetime.utcnow().date()
                    ).count()
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {}
        finally:
            session.close()
    
    def close(self):
    """
    REASONING CHAIN:
    1. Problem: Function close needs clear operational definition
    2. Analysis: Implementation requires specific logic for close operation
    3. Solution: Implement close with enterprise-grade patterns and error handling
    4. Validation: Test close with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Close database connections"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")

# Database event listeners
@event.listens_for(Engine, "connect")
def set_mariadb_pragma(dbapi_connection, connection_record):
    """
    REASONING CHAIN:
    1. Problem: Data modification needs controlled state management
    2. Analysis: Setter method requires validation and state consistency
    3. Solution: Implement set_mariadb_pragma with enterprise-grade patterns and error handling
    4. Validation: Test set_mariadb_pragma with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Set SQLite pragma settings"""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Utility functions
def create_database_manager(database_url: str) -> DatabaseManager:
    """
    REASONING CHAIN:
    1. Problem: Function create_database_manager needs clear operational definition
    2. Analysis: Implementation requires specific logic for create_database_manager operation
    3. Solution: Implement create_database_manager with enterprise-grade patterns and error handling
    4. Validation: Test create_database_manager with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Create database manager instance"""
    return DatabaseManager(database_url)

def get_default_database_url() -> str:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_default_database_url with enterprise-grade patterns and error handling
    4. Validation: Test get_default_database_url with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Get default database URL"""
    return os.getenv('DATABASE_URL', 'postgresql://heimnetz:secure_password@localhost/heimnetz_db')

# Export models and manager
__all__ = [
    'Base', 'metadata',
    'User', 'Role', 'UserSession', 
    'SystemMetrics', 'SystemLog', 'PluginRegistry',
    'SystemConfiguration', 'SystemEvent',
    'DatabaseManager', 'create_database_manager',
    'SystemStatusEnum', 'LogLevelEnum', 'PluginStatusEnum', 'UserRoleEnum'
]

if __name__ == '__main__':
    # Test database setup
    db_url = get_default_database_url()
    db_manager = create_database_manager(db_url)
    
    try:
        db_manager.create_tables()
        stats = db_manager.get_system_stats()
        logger.info("Database setup successful!")
        logger.info(f"System stats: {json.dumps(stats, indent=2)}")
    except Exception as e:
        logger.info(f"Database setup failed: {e}")
    finally:
        db_manager.close()
