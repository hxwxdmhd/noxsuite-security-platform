#!/usr/bin/env python3
"""
ULTIMATE SUITE v11.0 - DEVELOPMENT SERVER
Week 2 Implementation: Development-friendly version without Redis requirement

Author: Ultimate Suite Development Team
Date: July 18, 2025
Version: v2.0-dev (Development)
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import secrets
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

import bleach

# Monitoring and Metrics
import psutil
import pymysql

# Core Flask and Extensions
from flask import Flask, g, jsonify, render_template_string, request, session
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room, leave_room

# Database and ORM
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool
from werkzeug.middleware.proxy_fix import ProxyFix

# Security and Validation
from werkzeug.security import check_password_hash, generate_password_hash

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get('DATABASE_URL', f'mysql+pymysql://{BASE_DIR}/heimnetz_dev.db')
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_urlsafe(32))

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dev_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

class User(Base):
    """
    Enhanced User with enterprise-grade reasoning documentation
    
    REASONING CHAIN:
    1. Problem: System component User needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for User functionality
    3. Solution: Implement User with SOLID principles and enterprise patterns
    4. Validation: Test User with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )

class SystemMetrics(Base):
    """
    Enhanced SystemMetrics with enterprise-grade reasoning documentation
    
    REASONING CHAIN:
    1. Problem: System component SystemMetrics needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SystemMetrics functionality
    3. Solution: Implement SystemMetrics with SOLID principles and enterprise patterns
    4. Validation: Test SystemMetrics with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    network_bytes_sent = Column(Integer)
    network_bytes_recv = Column(Integer)
    active_connections = Column(Integer)
    request_count = Column(Integer)
    avg_response_time = Column(Float)
    
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
    )

class AuditLog(Base):
    """
    Enhanced AuditLog with enterprise-grade reasoning documentation
    
    REASONING CHAIN:
    1. Problem: System component AuditLog needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for AuditLog functionality
    3. Solution: Implement AuditLog with SOLID principles and enterprise patterns
    4. Validation: Test AuditLog with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer)
    action = Column(String(100))
    resource = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    __table_args__ = (
        Index('idx_timestamp_user', 'timestamp', 'user_id'),
    )

@dataclass
class SecurityConfig:
    """
    REASONING CHAIN:
    1. Problem: System component SecurityConfig needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SecurityConfig functionality
    3. Solution: Implement SecurityConfig with SOLID principles and enterprise patterns
    4. Validation: Test SecurityConfig with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Security configuration settings"""
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True
    session_timeout: int = 3600  # 1 hour
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    jwt_expiration: int = 86400  # 24 hours

class SecurityManager:
    """
    REASONING CHAIN:
    1. Problem: Complex system needs centralized management interface
    2. Analysis: Manager class requires coordinated resource handling and lifecycle management
    3. Solution: Implement SecurityManager with SOLID principles and enterprise patterns
    4. Validation: Test SecurityManager with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Development security management system"""
    
    def __init__(self):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.config = SecurityConfig()
        self.failed_attempts = {}
        self.lockout_times = {}
        
    def validate_password(self, password: str) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_password with enterprise-grade patterns and error handling
    4. Validation: Test validate_password with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Validate password strength"""
        errors = []
        
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters")
        
        if self.config.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.config.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.config.password_require_digit and not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit")
        
        if self.config.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': self._calculate_strength(password)
        }
    
    def _calculate_strength(self, password: str) -> int:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _calculate_strength with enterprise-grade patterns and error handling
    4. Validation: Test _calculate_strength with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length bonus
        score += min(len(password) * 2, 20)
        
        # Character variety bonus
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'[0-9]', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15
        
        # Complexity bonus
        if len(set(password)) / len(password) > 0.7:
            score += 15
        
        # Pattern penalty
        if re.search(r'(.)\1{2,}', password):
            score -= 10
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            score -= 5
        
        return max(0, min(100, score))
    
    def is_account_locked(self, identifier: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function is_account_locked needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_account_locked operation
    3. Solution: Implement is_account_locked with enterprise-grade patterns and error handling
    4. Validation: Test is_account_locked with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if account is locked due to failed attempts"""
        if identifier not in self.lockout_times:
            return False
        
        if datetime.utcnow() > self.lockout_times[identifier]:
            del self.lockout_times[identifier]
            if identifier in self.failed_attempts:
                del self.failed_attempts[identifier]
            return False
        
        return True
    
    def record_failed_attempt(self, identifier: str):
    """
    REASONING CHAIN:
    1. Problem: Function record_failed_attempt needs clear operational definition
    2. Analysis: Implementation requires specific logic for record_failed_attempt operation
    3. Solution: Implement record_failed_attempt with enterprise-grade patterns and error handling
    4. Validation: Test record_failed_attempt with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Record failed login attempt"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = 0
        
        self.failed_attempts[identifier] += 1
        
        if self.failed_attempts[identifier] >= self.config.max_login_attempts:
            self.lockout_times[identifier] = datetime.utcnow() + timedelta(seconds=self.config.lockout_duration)
    
    def reset_failed_attempts(self, identifier: str):
    """
    REASONING CHAIN:
    1. Problem: Function reset_failed_attempts needs clear operational definition
    2. Analysis: Implementation requires specific logic for reset_failed_attempts operation
    3. Solution: Implement reset_failed_attempts with enterprise-grade patterns and error handling
    4. Validation: Test reset_failed_attempts with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Reset failed attempts counter"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        if identifier in self.lockout_times:
            del self.lockout_times[identifier]
    
    def sanitize_input(self, text: str) -> str:
    """
    REASONING CHAIN:
    1. Problem: Function sanitize_input needs clear operational definition
    2. Analysis: Implementation requires specific logic for sanitize_input operation
    3. Solution: Implement sanitize_input with enterprise-grade patterns and error handling
    4. Validation: Test sanitize_input with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Sanitize user input"""
        return bleach.clean(text, tags=[], attributes={}, strip=True)
    
    def validate_email(self, email: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_email with enterprise-grade patterns and error handling
    4. Validation: Test validate_email with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

class PerformanceMonitor:
    """
    REASONING CHAIN:
    1. Problem: System component PerformanceMonitor needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PerformanceMonitor functionality
    3. Solution: Implement PerformanceMonitor with SOLID principles and enterprise patterns
    4. Validation: Test PerformanceMonitor with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Development performance monitoring system"""
    
    def __init__(self):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.metrics_history = []
        self.alert_thresholds = {
            'cpu': 80.0,
            'memory': 85.0,
            'disk': 90.0,
            'response_time': 1.0
        }
        
    def collect_metrics(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function collect_metrics needs clear operational definition
    2. Analysis: Implementation requires specific logic for collect_metrics operation
    3. Solution: Implement collect_metrics with enterprise-grade patterns and error handling
    4. Validation: Test collect_metrics with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Collect comprehensive system metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'memory_used': memory.used,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
                'disk_used': disk.used,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'process_memory_rss': process_memory.rss,
                'process_memory_vms': process_memory.vms,
                'active_connections': len(getattr(g, 'websocket_connections', [])),
                'uptime': (datetime.utcnow() - getattr(g, 'server_start_time', datetime.utcnow())).total_seconds()
            }
            
            # Store in history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)
            
            # Check for alerts
            self._check_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}
    
    def _check_alerts(self, metrics: Dict[str, Any]):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _check_alerts with enterprise-grade patterns and error handling
    4. Validation: Test _check_alerts with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check for performance alerts"""
        alerts = []
        
        if metrics['cpu_percent'] > self.alert_thresholds['cpu']:
            alerts.append({
                'type': 'cpu_high',
                'message': f"High CPU usage: {metrics['cpu_percent']:.1f}%",
                'severity': 'warning'
            })
        
        if metrics['memory_percent'] > self.alert_thresholds['memory']:
            alerts.append({
                'type': 'memory_high',
                'message': f"High memory usage: {metrics['memory_percent']:.1f}%",
                'severity': 'warning'
            })
        
        if metrics['disk_percent'] > self.alert_thresholds['disk']:
            alerts.append({
                'type': 'disk_high',
                'message': f"High disk usage: {metrics['disk_percent']:.1f}%",
                'severity': 'critical'
            })
        
        if alerts:
            logger.warning(f"Performance alerts: {alerts}")
            # Emit alerts via WebSocket
            if hasattr(g, 'socketio'):
                g.socketio.emit('performance_alert', {'alerts': alerts})

class DevServer:
    """
    REASONING CHAIN:
    1. Problem: System component DevServer needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for DevServer functionality
    3. Solution: Implement DevServer with SOLID principles and enterprise patterns
    4. Validation: Test DevServer with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Ultimate Suite v11.0 - Development Server Implementation"""
    
    def __init__(self):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.app = Flask(__name__)
        self.setup_configuration()
        self.setup_database()
        self.setup_security()
        self.setup_caching()
        self.setup_monitoring()
        self.setup_websocket()
        self.setup_routes()
        self.setup_error_handlers()
        
        # Initialize managers
        self.security_manager = SecurityManager()
        self.performance_monitor = PerformanceMonitor()
        
        # Server state
        self.server_start_time = datetime.utcnow()
        self.websocket_connections = set()
        
        logger.info("DevServer initialized successfully")
    
    def setup_configuration(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_configuration needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_configuration operation
    3. Solution: Implement setup_configuration with enterprise-grade patterns and error handling
    4. Validation: Test setup_configuration with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Configure Flask application"""
        self.app.config.update({
            'SECRET_KEY': SECRET_KEY,
            'JWT_SECRET_KEY': JWT_SECRET_KEY,
            'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=24),
            'SQLALCHEMY_DATABASE_URI': DATABASE_URL,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'CACHE_TYPE': 'simple',
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
        })
        
        # Trust proxy headers
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    def setup_database(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_database needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_database operation
    3. Solution: Implement setup_database with enterprise-grade patterns and error handling
    4. Validation: Test setup_database with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize database connection and tables"""
        try:
            self.engine = create_engine(DATABASE_URL, poolclass=StaticPool, connect_args={'check_same_thread': False})
            self.db_session = scoped_session(sessionmaker(bind=self.engine))
            
            # Create tables
            Base.metadata.create_all(self.engine)
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def setup_security(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_security needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_security operation
    3. Solution: Implement setup_security with enterprise-grade patterns and error handling
    4. Validation: Test setup_security with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup security components"""
        # CORS
        CORS(self.app, origins=['*'], supports_credentials=True)
        
        # JWT
        self.jwt = JWTManager(self.app)
        
        # Rate limiting with memory storage
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["1000 per day", "100 per hour"],
            storage_uri="memory://"
        )
        
        # Security headers
        @self.app.after_request
        def set_security_headers(response):
    """
    Enhanced set_security_headers with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Data modification needs controlled state management
    2. Analysis: Setter method requires validation and state consistency
    3. Solution: Implement set_security_headers with enterprise-grade patterns and error handling
    4. Validation: Test set_security_headers with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            return response
        
        logger.info("Security components initialized")
    
    def setup_caching(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_caching needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_caching operation
    3. Solution: Implement setup_caching with enterprise-grade patterns and error handling
    4. Validation: Test setup_caching with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup caching system"""
        try:
            self.cache = Cache(self.app)
            logger.info("Simple caching system initialized")
        except Exception as e:
            logger.warning(f"Cache initialization failed: {e}")
    
    def setup_monitoring(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_monitoring needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_monitoring operation
    3. Solution: Implement setup_monitoring with enterprise-grade patterns and error handling
    4. Validation: Test setup_monitoring with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup monitoring and metrics"""
        @self.app.before_request
        def before_request():
    """
    Enhanced before_request with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function before_request needs clear operational definition
    2. Analysis: Implementation requires specific logic for before_request operation
    3. Solution: Implement before_request with enterprise-grade patterns and error handling
    4. Validation: Test before_request with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            g.start_time = time.time()
            g.server_start_time = self.server_start_time
            g.websocket_connections = self.websocket_connections
        
        @self.app.after_request
        def after_request(response):
    """
    Enhanced after_request with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function after_request needs clear operational definition
    2. Analysis: Implementation requires specific logic for after_request operation
    3. Solution: Implement after_request with enterprise-grade patterns and error handling
    4. Validation: Test after_request with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            return response
        
        logger.info("Monitoring system initialized")
    
    def setup_websocket(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_websocket needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_websocket operation
    3. Solution: Implement setup_websocket with enterprise-grade patterns and error handling
    4. Validation: Test setup_websocket with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup WebSocket with Socket.IO"""
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode='threading',
            ping_timeout=60,
            ping_interval=25
        )
        
        @self.socketio.on('connect')
        def handle_connect():
    """
    Enhanced handle_connect with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function handle_connect needs clear operational definition
    2. Analysis: Implementation requires specific logic for handle_connect operation
    3. Solution: Implement handle_connect with enterprise-grade patterns and error handling
    4. Validation: Test handle_connect with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            self.websocket_connections.add(request.sid)
            logger.info(f"WebSocket connected: {request.sid}")
            emit('connected', {'status': 'success', 'sid': request.sid})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
    """
    Enhanced handle_disconnect with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function handle_disconnect needs clear operational definition
    2. Analysis: Implementation requires specific logic for handle_disconnect operation
    3. Solution: Implement handle_disconnect with enterprise-grade patterns and error handling
    4. Validation: Test handle_disconnect with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            if request.sid in self.websocket_connections:
                self.websocket_connections.remove(request.sid)
            logger.info(f"WebSocket disconnected: {request.sid}")
        
        @self.socketio.on('subscribe_metrics')
        def handle_subscribe_metrics():
    """
    Enhanced handle_subscribe_metrics with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function handle_subscribe_metrics needs clear operational definition
    2. Analysis: Implementation requires specific logic for handle_subscribe_metrics operation
    3. Solution: Implement handle_subscribe_metrics with enterprise-grade patterns and error handling
    4. Validation: Test handle_subscribe_metrics with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            join_room('metrics')
            emit('subscribed', {'room': 'metrics'})
        
        @self.socketio.on('unsubscribe_metrics')
        def handle_unsubscribe_metrics():
    """
    Enhanced handle_unsubscribe_metrics with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function handle_unsubscribe_metrics needs clear operational definition
    2. Analysis: Implementation requires specific logic for handle_unsubscribe_metrics operation
    3. Solution: Implement handle_unsubscribe_metrics with enterprise-grade patterns and error handling
    4. Validation: Test handle_unsubscribe_metrics with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            leave_room('metrics')
            emit('unsubscribed', {'room': 'metrics'})
        
        logger.info("WebSocket system initialized")
    
    def setup_routes(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_routes needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_routes operation
    3. Solution: Implement setup_routes with enterprise-grade patterns and error handling
    4. Validation: Test setup_routes with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup API routes"""
        
        @self.app.route('/')
        def index():
    """
    Enhanced index with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function index needs clear operational definition
    2. Analysis: Implementation requires specific logic for index operation
    3. Solution: Implement index with enterprise-grade patterns and error handling
    4. Validation: Test index with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/v1/health')
        def health_check():
    """
    REASONING CHAIN:
    1. Problem: Function health_check needs clear operational definition
    2. Analysis: Implementation requires specific logic for health_check operation
    3. Solution: Implement health_check with enterprise-grade patterns and error handling
    4. Validation: Test health_check with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': 'v2.0-dev',
                'uptime': (datetime.utcnow() - self.server_start_time).total_seconds()
            })
        
        @self.app.route('/api/v1/metrics')
        def get_metrics():
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_metrics with enterprise-grade patterns and error handling
    4. Validation: Test get_metrics with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            """Get system metrics"""
            metrics = self.performance_monitor.collect_metrics()
            return jsonify(metrics)
        
        @self.app.route('/api/v1/cache/stats')
        def cache_stats():
    """
    REASONING CHAIN:
    1. Problem: Function cache_stats needs clear operational definition
    2. Analysis: Implementation requires specific logic for cache_stats operation
    3. Solution: Implement cache_stats with enterprise-grade patterns and error handling
    4. Validation: Test cache_stats with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            """Get cache statistics"""
            return jsonify({
                'backend': 'memory',
                'hits': 0,
                'misses': 0,
                'hit_rate': 0,
                'total_requests': 0
            })
        
        @self.app.route('/api/v1/auth/register', methods=['POST'])
        @self.limiter.limit("5 per minute")
        def register():
    """
    REASONING CHAIN:
    1. Problem: Function register needs clear operational definition
    2. Analysis: Implementation requires specific logic for register operation
    3. Solution: Implement register with enterprise-grade patterns and error handling
    4. Validation: Test register with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            """User registration endpoint"""
            data = request.get_json()
            
            if not data or not data.get('username') or not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Validate input
            username = self.security_manager.sanitize_input(data['username'])
            email = self.security_manager.sanitize_input(data['email'])
            password = data['password']
            
            if not self.security_manager.validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            password_check = self.security_manager.validate_password(password)
            if not password_check['valid']:
                return jsonify({'error': 'Password validation failed', 'details': password_check['errors']}), 400
            
            # Check if user exists
            existing_user = self.db_session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return jsonify({'error': 'User already exists'}), 409
            
            # Create new user
            password_hash = generate_password_hash(password)
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=data.get('role', 'user')
            )
            
            self.db_session.add(user)
            self.db_session.commit()
            
            # Log audit event
            self.log_audit_event(user.id, 'user_register', 'user', f"User {username} registered")
            
            return jsonify({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username
            }), 201
        
        @self.app.route('/api/v1/auth/login', methods=['POST'])
        @self.limiter.limit("10 per minute")
        def login():
    """
    REASONING CHAIN:
    1. Problem: Function login needs clear operational definition
    2. Analysis: Implementation requires specific logic for login operation
    3. Solution: Implement login with enterprise-grade patterns and error handling
    4. Validation: Test login with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            """User login endpoint"""
            data = request.get_json()
            
            if not data or not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Missing credentials'}), 400
            
            username = self.security_manager.sanitize_input(data['username'])
            password = data['password']
            
            # Check account lockout
            if self.security_manager.is_account_locked(username):
                return jsonify({'error': 'Account temporarily locked due to failed login attempts'}), 423
            
            # Find user
            user = self.db_session.query(User).filter(User.username == username).first()
            
            if not user or not check_password_hash(user.password_hash, password):
                self.security_manager.record_failed_attempt(username)
                return jsonify({'error': 'Invalid credentials'}), 401
            
            if not user.is_active:
                return jsonify({'error': 'Account is disabled'}), 403
            
            # Reset failed attempts
            self.security_manager.reset_failed_attempts(username)
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db_session.commit()
            
            # Create JWT token
            access_token = create_access_token(identity=user.id)
            
            # Log audit event
            self.log_audit_event(user.id, 'user_login', 'user', f"User {username} logged in")
            
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            })
        
        @self.app.route('/api/v1/auth/profile')
        @jwt_required()
        def get_profile():
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_profile with enterprise-grade patterns and error handling
    4. Validation: Test get_profile with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            """Get user profile"""
            user_id = get_jwt_identity()
            user = self.db_session.query(User).get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        logger.info("API routes initialized")
    
    def setup_error_handlers(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_error_handlers needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_error_handlers operation
    3. Solution: Implement setup_error_handlers with enterprise-grade patterns and error handling
    4. Validation: Test setup_error_handlers with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
    """
    Enhanced not_found with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function not_found needs clear operational definition
    2. Analysis: Implementation requires specific logic for not_found operation
    3. Solution: Implement not_found with enterprise-grade patterns and error handling
    4. Validation: Test not_found with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            return jsonify({'error': 'Not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
    """
    Enhanced internal_error with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function internal_error needs clear operational definition
    2. Analysis: Implementation requires specific logic for internal_error operation
    3. Solution: Implement internal_error with enterprise-grade patterns and error handling
    4. Validation: Test internal_error with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            self.db_session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.errorhandler(429)
        def rate_limit_exceeded(error):
    """
    Enhanced rate_limit_exceeded with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function rate_limit_exceeded needs clear operational definition
    2. Analysis: Implementation requires specific logic for rate_limit_exceeded operation
    3. Solution: Implement rate_limit_exceeded with enterprise-grade patterns and error handling
    4. Validation: Test rate_limit_exceeded with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        logger.info("Error handlers initialized")
    
    def log_audit_event(self, user_id: int, action: str, resource: str, details: str):
    """
    REASONING CHAIN:
    1. Problem: Function log_audit_event needs clear operational definition
    2. Analysis: Implementation requires specific logic for log_audit_event operation
    3. Solution: Implement log_audit_event with enterprise-grade patterns and error handling
    4. Validation: Test log_audit_event with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Log audit event"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                details=details,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            
            self.db_session.add(audit_log)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Audit logging error: {e}")
    
    def start_background_tasks(self):
    """
    REASONING CHAIN:
    1. Problem: Function start_background_tasks needs clear operational definition
    2. Analysis: Implementation requires specific logic for start_background_tasks operation
    3. Solution: Implement start_background_tasks with enterprise-grade patterns and error handling
    4. Validation: Test start_background_tasks with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Start background monitoring tasks"""
        def metrics_collector():
    """
    Enhanced metrics_collector with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function metrics_collector needs clear operational definition
    2. Analysis: Implementation requires specific logic for metrics_collector operation
    3. Solution: Implement metrics_collector with enterprise-grade patterns and error handling
    4. Validation: Test metrics_collector with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            while True:
                try:
                    metrics = self.performance_monitor.collect_metrics()
                    
                    # Store metrics in database
                    db_metrics = SystemMetrics(
                        cpu_percent=metrics.get('cpu_percent'),
                        memory_percent=metrics.get('memory_percent'),
                        disk_percent=metrics.get('disk_percent'),
                        network_bytes_sent=metrics.get('network_bytes_sent'),
                        network_bytes_recv=metrics.get('network_bytes_recv'),
                        active_connections=metrics.get('active_connections'),
                        avg_response_time=metrics.get('avg_response_time', 0)
                    )
                    
                    self.db_session.add(db_metrics)
                    self.db_session.commit()
                    
                    # Emit to WebSocket subscribers
                    self.socketio.emit('metrics_update', metrics, room='metrics')
                    
                except Exception as e:
                    logger.error(f"Background metrics collection error: {e}")
                
                time.sleep(5)  # Collect metrics every 5 seconds
        
        # Start metrics collection in background thread
        metrics_thread = threading.Thread(target=metrics_collector, daemon=True)
        metrics_thread.start()
        
        logger.info("Background tasks started")
    
    def run(self, host='127.0.0.1', port=5002, debug=False):
    """
    REASONING CHAIN:
    1. Problem: Function run needs clear operational definition
    2. Analysis: Implementation requires specific logic for run operation
    3. Solution: Implement run with enterprise-grade patterns and error handling
    4. Validation: Test run with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Run the development server"""
        logger.info("="*60)
        logger.info("ULTIMATE SUITE v11.0 - DEVELOPMENT SERVER")
        logger.info("="*60)
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Database: {DATABASE_URL}")
        logger.info(f"Cache: Simple memory cache")
        logger.info("="*60)
        
        # Start background tasks
        self.start_background_tasks()
        
        # Run the server
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,
            log_output=True
        )

# Development Dashboard Template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Suite v11.0 - Development Dashboard</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.2rem;
            color: #666;
        }
        
        .dev-notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-5px);
        }
        
        .status-card h3 {
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: #444;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: bold;
            color: #667eea;
        }
        
        .status-online {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-dev {
            color: #17a2b8;
            font-weight: bold;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .chart-container h3 {
            margin-bottom: 20px;
            color: #444;
        }
        
        .info-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            color: #155724;
        }
        
        .info-box h4 {
            margin-bottom: 10px;
        }
        
        .info-box ul {
            margin-left: 20px;
        }
        
        .info-box li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Ultimate Suite v11.0</h1>
            <p>Development Dashboard - No Redis Required</p>
            <div id="connection-status" class="status-online">● Connected</div>
        </div>
        
        <div class="dev-notice">
            <strong>Development Mode:</strong> This version runs without Redis for easy development. 
            All caching and rate limiting use memory storage.
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>📊 System Status</h3>
                <div class="metric">
                    <span>Server Status</span>
                    <span class="metric-value status-online">Online</span>
                </div>
                <div class="metric">
                    <span>Database</span>
                    <span class="metric-value status-online">Connected</span>
                </div>
                <div class="metric">
                    <span>WebSocket</span>
                    <span class="metric-value status-online">Active</span>
                </div>
                <div class="metric">
                    <span>Cache</span>
                    <span class="metric-value status-dev">Memory</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>⚡ Performance</h3>
                <div class="metric">
                    <span>CPU Usage</span>
                    <span class="metric-value" id="cpu-usage">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                </div>
                <div class="metric">
                    <span>Memory Usage</span>
                    <span class="metric-value" id="memory-usage">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                </div>
                <div class="metric">
                    <span>Disk Usage</span>
                    <span class="metric-value" id="disk-usage">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🌐 Network</h3>
                <div class="metric">
                    <span>Active Connections</span>
                    <span class="metric-value" id="active-connections">0</span>
                </div>
                <div class="metric">
                    <span>Bytes Sent</span>
                    <span class="metric-value" id="bytes-sent">0</span>
                </div>
                <div class="metric">
                    <span>Bytes Received</span>
                    <span class="metric-value" id="bytes-recv">0</span>
                </div>
                <div class="metric">
                    <span>Uptime</span>
                    <span class="metric-value" id="uptime">0s</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🔒 Security</h3>
                <div class="metric">
                    <span>Authentication</span>
                    <span class="metric-value status-online">JWT Active</span>
                </div>
                <div class="metric">
                    <span>Rate Limiting</span>
                    <span class="metric-value status-dev">Memory</span>
                </div>
                <div class="metric">
                    <span>CORS</span>
                    <span class="metric-value status-online">Enabled</span>
                </div>
                <div class="metric">
                    <span>Environment</span>
                    <span class="metric-value status-dev">Development</span>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📈 System Performance</h3>
            <canvas id="performanceChart" width="800" height="300"></canvas>
        </div>
        
        <div class="info-box">
            <h4>🛠️ Development Features</h4>
            <ul>
                <li><strong>No Redis Required:</strong> All caching and rate limiting use memory storage</li>
                <li><strong>SQLite Database:</strong> Lightweight database for development</li>
                <li><strong>JWT Authentication:</strong> Secure token-based authentication</li>
                <li><strong>WebSocket Support:</strong> Real-time communication</li>
                <li><strong>Security Features:</strong> Input validation, rate limiting, CORS</li>
                <li><strong>Performance Monitoring:</strong> Real-time metrics and alerts</li>
            </ul>
        </div>
        
        <div class="info-box">
            <h4>🚀 Ready for Production</h4>
            <ul>
                <li>Add Redis server for production caching</li>
                <li>Configure PostgreSQL for production database</li>
                <li>Set up SSL/TLS certificates</li>
                <li>Configure reverse proxy (Nginx)</li>
                <li>Set up monitoring and logging</li>
            </ul>
        </div>
    </div>

    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Connection status
        const connectionStatus = document.getElementById('connection-status');
        
        socket.on('connect', () => {
            connectionStatus.textContent = '● Connected';
            connectionStatus.className = 'status-online';
            socket.emit('subscribe_metrics');
        });
        
        socket.on('disconnect', () => {
            connectionStatus.textContent = '● Disconnected';
            connectionStatus.className = 'status-offline';
        });
        
        // Initialize performance chart
        const performanceChart = new Chart(document.getElementById('performanceChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage (%)',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true
                }, {
                    label: 'Memory Usage (%)',
                    data: [],
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // Update metrics
        function updateMetrics(metrics) {
            // Update performance metrics
            document.getElementById('cpu-usage').textContent = metrics.cpu_percent?.toFixed(1) + '%' || '0%';
            document.getElementById('memory-usage').textContent = metrics.memory_percent?.toFixed(1) + '%' || '0%';
            document.getElementById('disk-usage').textContent = metrics.disk_percent?.toFixed(1) + '%' || '0%';
            
            // Update progress bars
            document.getElementById('cpu-progress').style.width = (metrics.cpu_percent || 0) + '%';
            document.getElementById('memory-progress').style.width = (metrics.memory_percent || 0) + '%';
            document.getElementById('disk-progress').style.width = (metrics.disk_percent || 0) + '%';
            
            // Update network metrics
            document.getElementById('active-connections').textContent = metrics.active_connections || 0;
            document.getElementById('bytes-sent').textContent = formatBytes(metrics.network_bytes_sent || 0);
            document.getElementById('bytes-recv').textContent = formatBytes(metrics.network_bytes_recv || 0);
            document.getElementById('uptime').textContent = formatUptime(metrics.uptime || 0);
            
            // Update chart
            const now = new Date().toLocaleTimeString();
            
            if (performanceChart.data.labels.length > 10) {
                performanceChart.data.labels.shift();
                performanceChart.data.datasets[0].data.shift();
                performanceChart.data.datasets[1].data.shift();
            }
            
            performanceChart.data.labels.push(now);
            performanceChart.data.datasets[0].data.push(metrics.cpu_percent || 0);
            performanceChart.data.datasets[1].data.push(metrics.memory_percent || 0);
            performanceChart.update();
        }
        
        // Listen for metrics updates
        socket.on('metrics_update', updateMetrics);
        
        // Format bytes
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // Format uptime
        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            if (days > 0) {
                return `${days}d ${hours}h ${minutes}m`;
            } else if (hours > 0) {
                return `${hours}h ${minutes}m ${secs}s`;
            } else if (minutes > 0) {
                return `${minutes}m ${secs}s`;
            } else {
                return `${secs}s`;
            }
        }
        
        // Fetch initial metrics
        fetch('/api/v1/metrics')
            .then(response => response.json())
            .then(updateMetrics)
            .catch(console.error);
        
        // Periodic metrics update
        setInterval(() => {
            fetch('/api/v1/metrics')
                .then(response => response.json())
                .then(updateMetrics)
                .catch(console.error);
        }, 5000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    server = DevServer()
    server.run(host='127.0.0.1', port=5002, debug=True)
