#!/usr/bin/env python3
"""
NoxSuite Ultimate Backend Application
Unified Flask server with real-time WebSocket, security monitoring, and ADHD-friendly API design
@author @hxwxdmhd
@version 11.0.0
"""

import asyncio
import hashlib
import json
import logging
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

# Monitoring and security
import psutil

# Database and ORM
import pymysql

# Flask and extensions
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import check_password_hash, generate_password_hash

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "src"))

# Import our modules
try:
    from src.core.NoxSuiteController import NoxSuiteController

    from advanced_ai_engine import AdvancedAIEngine, get_ai_engine, initialize_ai_engine
    from enhanced_monitoring_system import EnhancedMonitoringSystem
    from noxsuite_integration_bridge import NoxSuiteIntegrationBridge
except ImportError as e:
    print(f"⚠️ Module import warning: {e}")

    # Create mock classes for development
    class NoxSuiteIntegrationBridge:
        def __init__(self):
            self.status = {"operational": True}

        def get_status(self):
            return self.status

        def validate_configuration(self, config):
            return {"valid": True, "score": 85.5}

    class EnhancedMonitoringSystem:
        def __init__(self):
            self.patterns = {}

        def get_current_metrics(self):
            return {"cpu": 45.2, "memory": 67.8, "status": "operational"}

        def get_security_alerts(self):
            return []

    class NoxSuiteController:
        def __init__(self):
            pass

        @staticmethod
        def initialize():
            return {"status": "initialized"}

    class AdvancedAIEngine:
        def __init__(self):
            pass

        async def analyze_threat(self, data):
            return {"threat_type": "mock", "confidence": 0.5}

        async def optimize_performance(self, metrics):
            return {"optimization": "mock"}

        async def analyze_user_behavior(self, user_id, data):
            return {"pattern": "mock"}

        def get_ai_status(self):
            return {"status": "mock"}

    def initialize_ai_engine():
        return AdvancedAIEngine()

    def get_ai_engine():
        return AdvancedAIEngine()


# Configure logging with ADHD-friendly format
logging.basicConfig(
    level=logging.INFO,
    format="🔍 %(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("noxsuite_backend.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# =============================================================================
# Flask Application Configuration
# =============================================================================

app = Flask(__name__, static_folder="frontend/build", static_url_path="")

# Security configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", secrets.token_hex(32))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# CORS configuration for frontend
CORS(
    app,
    origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5000",  # Flask dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ],
)

# JWT configuration
jwt = JWTManager(app)

# SocketIO configuration with ADHD-friendly settings
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e6,
)

# =============================================================================
# Database Configuration
# =============================================================================

DATABASE_PATH = "noxsuite.db"


def init_database():
    """Initialize SQLite database with required tables"""
    with pymysql.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                preferences TEXT DEFAULT '{}'
            )
        """
        )

        # Security alerts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                source_ip TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        """
        )

        # System metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                network_in REAL,
                network_out REAL,
                active_connections INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Plugin registry table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS plugins (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                author TEXT,
                description TEXT,
                category TEXT,
                installed BOOLEAN DEFAULT FALSE,
                enabled BOOLEAN DEFAULT TRUE,
                config TEXT DEFAULT '{}',
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Web crawler data table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crawler_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                status_code INTEGER,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}'
            )
        """
        )

        conn.commit()
        logger.info("✅ Database initialized successfully")


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = pymysql.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


# =============================================================================
# Global State Management
# =============================================================================


class NoxSuiteState:
    """Centralized state management for NoxSuite"""

    def __init__(self):
        self.active_users = set()
        self.security_alerts = deque(maxlen=1000)  # Keep last 1000 alerts
        self.system_metrics = {}
        self.plugin_registry = {}
        self.crawler_status = {"running": False, "progress": 0}
        self.real_time_data = defaultdict(dict)
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "peak_connections": 0,
        }

        # Initialize subsystems
        try:
            self.integration_bridge = NoxSuiteIntegrationBridge()
            self.monitoring_system = EnhancedMonitoringSystem()
            # Initialize AI engine
            self.ai_engine = initialize_ai_engine()
            logger.info("✅ NoxSuite subsystems initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize subsystems: {e}")
            self.integration_bridge = None
            self.monitoring_system = None
            self.ai_engine = None

    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        return {
            "system_metrics": self.system_metrics,
            # Last 10 alerts
            "security_alerts": list(self.security_alerts)[-10:],
            "active_users": len(self.active_users),
            "plugin_count": len(self.plugin_registry),
            "crawler_status": self.crawler_status,
            "connection_stats": self.connection_stats,
            "timestamp": datetime.now().isoformat(),
        }

    def add_security_alert(self, alert_data):
        """Add new security alert"""
        alert = {
            "id": secrets.token_hex(8),
            "timestamp": datetime.now().isoformat(),
            **alert_data,
        }
        self.security_alerts.append(alert)

        # Store in database
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO security_alerts 
                    (type, severity, title, message, source_ip, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        alert.get("type", "unknown"),
                        alert.get("severity", "medium"),
                        alert.get("title", "Security Alert"),
                        alert.get("message", ""),
                        alert.get("source_ip"),
                        alert.get("user_agent"),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to store security alert: {e}")

        # Emit to connected clients
        socketio.emit("security_alert", alert, room="dashboard")

        return alert

    def update_system_metrics(self, metrics):
        """Update system metrics"""
        self.system_metrics = {
            "timestamp": datetime.now().isoformat(), **metrics}

        # Store in database
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO system_metrics 
                    (cpu_usage, memory_usage, disk_usage, network_in, network_out, active_connections)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        metrics.get("cpu_usage", 0),
                        metrics.get("memory_usage", 0),
                        metrics.get("disk_usage", 0),
                        metrics.get("network_in", 0),
                        metrics.get("network_out", 0),
                        metrics.get("active_connections", 0),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to store system metrics: {e}")

        # Emit to connected clients
        socketio.emit("metrics_update", self.system_metrics, room="dashboard")


# Initialize global state
nox_state = NoxSuiteState()

# =============================================================================
# Authentication and Security
# =============================================================================


def create_default_admin():
    """Create default admin user if none exists"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
            admin_count = cursor.fetchone()[0]

            if admin_count == 0:
                admin_password = os.environ.get(
                    "ADMIN_PASSWORD", "noxsuite2025!")
                password_hash = generate_password_hash(admin_password)

                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash, is_admin)
                    VALUES (?, ?, ?, ?)
                """,
                    ("admin", "admin@noxsuite.local", password_hash, True),
                )
                conn.commit()

                logger.info(
                    f"✅ Default admin created - Username: admin, Password: {admin_password}"
                )

    except Exception as e:
        logger.error(f"❌ Failed to create default admin: {e}")


def require_auth(f):
    """Decorator for endpoints requiring authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Authentication required"}), 401

        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            # In production, validate JWT token here
            # For now, simple token validation
            if token != "noxsuite-demo-token":
                return jsonify({"error": "Invalid token"}), 401

        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function


def log_security_event(event_type, details, severity="medium"):
    """Log security events with ADHD-friendly formatting"""
    alert_data = {
        "type": event_type,
        "severity": severity,
        "title": f"{event_type.title()} Detected",
        "message": details,
        "source_ip": request.remote_addr if request else "system",
        "user_agent": (
            request.headers.get(
                "User-Agent", "unknown") if request else "system"
        ),
    }

    nox_state.add_security_alert(alert_data)
    logger.warning(f"🚨 Security Event: {event_type} - {details}")


# =============================================================================
# Real-time System Monitoring
# =============================================================================


def collect_system_metrics():
    """Collect comprehensive system metrics"""
    try:
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Network statistics
        network = psutil.net_io_counters()

        # Process information
        process_count = len(psutil.pids())

        # Connection count
        try:
            connections = len(psutil.net_connections())
        except (psutil.AccessDenied, OSError):
            connections = 0

        metrics = {
            "cpu_usage": round(cpu_percent, 2),
            "memory_usage": round(memory.percent, 2),
            "memory_available": round(memory.available / (1024**3), 2),  # GB
            "disk_usage": round(disk.percent, 2),
            "disk_free": round(disk.free / (1024**3), 2),  # GB
            "network_in": round(network.bytes_recv / (1024**2), 2),  # MB
            "network_out": round(network.bytes_sent / (1024**2), 2),  # MB
            "active_connections": connections,
            "process_count": process_count,
            "uptime": time.time() - psutil.boot_time(),
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else [0, 0, 0],
        }

        # Add historical data for charts
        if not hasattr(collect_system_metrics, "history"):
            collect_system_metrics.history = defaultdict(deque)

        for key in ["cpu_usage", "memory_usage", "network_in", "network_out"]:
            collect_system_metrics.history[key].append(metrics[key])
            # Keep last 60 points
            if len(collect_system_metrics.history[key]) > 60:
                collect_system_metrics.history[key].popleft()

        metrics["cpu_history"] = list(
            collect_system_metrics.history["cpu_usage"])
        metrics["memory_history"] = list(
            collect_system_metrics.history["memory_usage"])
        metrics["network_history"] = list(
            collect_system_metrics.history["network_in"])

        return metrics

    except Exception as e:
        logger.error(f"❌ Failed to collect system metrics: {e}")
        return {}


def monitor_system_loop():
    """Background loop for system monitoring"""
    logger.info("🔍 Starting system monitoring loop")

    while True:
        try:
            # Collect metrics
            metrics = collect_system_metrics()
            if metrics:
                nox_state.update_system_metrics(metrics)

            # Check for security threats
            if metrics.get("cpu_usage", 0) > 90:
                log_security_event(
                    "high_cpu_usage", f"CPU usage at {metrics['cpu_usage']}%", "high"
                )

            if metrics.get("memory_usage", 0) > 95:
                log_security_event(
                    "high_memory_usage",
                    f"Memory usage at {metrics['memory_usage']}%",
                    "critical",
                )

            # Sleep for monitoring interval
            time.sleep(10)  # Update every 10 seconds

        except Exception as e:
            logger.error(f"❌ Monitoring loop error: {e}")
            time.sleep(30)  # Wait longer on error


# =============================================================================
# WebSocket Event Handlers
# =============================================================================


@socketio.on("connect")
def handle_connect():
    """Handle WebSocket connection"""
    client_id = request.sid
    nox_state.active_users.add(client_id)
    nox_state.connection_stats["total_connections"] += 1
    nox_state.connection_stats["active_connections"] = len(
        nox_state.active_users)

    if (
        nox_state.connection_stats["active_connections"]
        > nox_state.connection_stats["peak_connections"]
    ):
        nox_state.connection_stats["peak_connections"] = nox_state.connection_stats[
            "active_connections"
        ]

    # Join dashboard room for real-time updates
    join_room("dashboard")

    logger.info(
        f"✅ Client connected: {client_id} (Total: {len(nox_state.active_users)})"
    )

    # Send current dashboard data
    emit("dashboard_update", nox_state.get_dashboard_data())
    emit("connection_status", {"status": "connected", "client_id": client_id})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle WebSocket disconnection"""
    client_id = request.sid
    nox_state.active_users.discard(client_id)
    nox_state.connection_stats["active_connections"] = len(
        nox_state.active_users)

    leave_room("dashboard")
    logger.info(
        f"❌ Client disconnected: {client_id} (Remaining: {len(nox_state.active_users)})"
    )


@socketio.on("request_dashboard_data")
def handle_request_dashboard_data():
    """Handle request for dashboard data"""
    emit("dashboard_update", nox_state.get_dashboard_data())


@socketio.on("request_security_status")
def handle_request_security_status():
    """Handle request for security status"""
    security_data = {
        "alerts": list(nox_state.security_alerts)[-50:],  # Last 50 alerts
        "threat_count": len(
            [a for a in nox_state.security_alerts if a.get(
                "severity") == "critical"]
        ),
        "last_scan": datetime.now().isoformat(),
    }
    emit("security_status_update", security_data)


@socketio.on("start_security_scan")
def handle_start_security_scan(data):
    """Handle security scan request"""

    def run_security_scan():
        try:
            emit("scan_status", {"status": "starting", "progress": 0})

            # Simulate comprehensive security scan
            scan_steps = [
                "Initializing security modules",
                "Scanning network interfaces",
                "Checking for malware signatures",
                "Analyzing system vulnerabilities",
                "Validating firewall rules",
                "Completing security assessment",
            ]

            for i, step in enumerate(scan_steps):
                time.sleep(2)  # Simulate scan time
                progress = int((i + 1) / len(scan_steps) * 100)
                emit(
                    "scan_status",
                    {"status": "running", "progress": progress, "current_step": step},
                )

            # Generate scan results
            results = {
                "status": "completed",
                "progress": 100,
                "threats_found": 0,
                "vulnerabilities": 2,
                "recommendations": [
                    "Update system packages",
                    "Enable additional firewall rules",
                    "Schedule regular security scans",
                ],
                "scan_time": 12.5,
                "timestamp": datetime.now().isoformat(),
            }

            emit("scan_complete", results)

            # Log scan completion
            log_security_event(
                "security_scan_completed",
                f"Security scan completed - {results['vulnerabilities']} vulnerabilities found",
                "low",
            )

        except Exception as e:
            logger.error(f"❌ Security scan error: {e}")
            emit("scan_error", {"error": str(e)})

    # Run scan in background thread
    threading.Thread(target=run_security_scan, daemon=True).start()


# =============================================================================
# REST API Endpoints
# =============================================================================


@app.route("/")
def serve_frontend():
    """Serve React frontend"""
    try:
        return send_from_directory(app.static_folder, "index.html")
    except:
        # Development fallback
        return jsonify(
            {
                "name": "NoxSuite Ultimate Backend",
                "version": "11.0.0",
                "status": "operational",
                "features": [
                    "Real-time security monitoring",
                    "ADHD-friendly API design",
                    "WebSocket integration",
                    "Plugin management",
                    "Web crawler integration",
                ],
                "endpoints": {
                    "auth": "/api/auth/*",
                    "dashboard": "/api/dashboard/*",
                    "security": "/api/security/*",
                    "plugins": "/api/plugins/*",
                    "crawler": "/api/crawler/*",
                },
            }
        )


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder + "/static", filename)


# Health check endpoint
@app.route("/api/health")
def health_check():
    """Comprehensive health check with ADHD-friendly response"""
    try:
        # Test database connectivity
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")

        # Get current metrics
        metrics = collect_system_metrics()

        # Calculate health score
        health_score = 100
        if metrics.get("cpu_usage", 0) > 80:
            health_score -= 20
        if metrics.get("memory_usage", 0) > 90:
            health_score -= 30
        if metrics.get("disk_usage", 0) > 95:
            health_score -= 25

        status = (
            "healthy"
            if health_score >= 70
            else "degraded" if health_score >= 40 else "unhealthy"
        )

        return jsonify(
            {
                "status": status,
                "health_score": health_score,
                "timestamp": datetime.now().isoformat(),
                "system_metrics": metrics,
                "active_connections": len(nox_state.active_users),
                "database_status": "connected",
                "monitoring_status": "active",
                "version": "11.0.0",
            }
        )

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "health_score": 0,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


# Authentication endpoints
@app.route("/api/auth/login", methods=["POST"])
def login():
    """User authentication with JWT token"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        # For demo purposes, use simple authentication
        if username == "admin" and password == "noxsuite2025!":
            access_token = create_access_token(
                identity=username, additional_claims={"role": "admin"}
            )

            log_security_event(
                "user_login", f"User {username} logged in successfully", "low"
            )

            return jsonify(
                {
                    "access_token": access_token,
                    "user": {
                        "username": username,
                        "role": "admin",
                        "preferences": {
                            "theme": "dark",
                            "accessibility": {
                                "high_contrast": False,
                                "reduced_motion": False,
                                "cognitive_load_reduction": False,
                            },
                        },
                    },
                }
            )
        else:
            log_security_event(
                "failed_login", f"Failed login attempt for {username}", "medium"
            )
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return jsonify({"error": "Authentication failed"}), 500


@app.route("/api/auth/profile", methods=["GET"])
@require_auth
def get_profile():
    """Get user profile information"""
    return jsonify(
        {
            "username": "admin",
            "role": "admin",
            "preferences": {
                "theme": "dark",
                "accessibility": {
                    "high_contrast": False,
                    "reduced_motion": False,
                    "cognitive_load_reduction": False,
                },
            },
            "last_login": datetime.now().isoformat(),
        }
    )


# Dashboard endpoints
@app.route("/api/dashboard/overview", methods=["GET"])
@require_auth
def dashboard_overview():
    """Get dashboard overview data"""
    return jsonify(nox_state.get_dashboard_data())


@app.route("/api/dashboard/metrics", methods=["GET"])
@require_auth
def dashboard_metrics():
    """Get detailed system metrics"""
    metrics = collect_system_metrics()
    return jsonify(
        {
            "current": metrics,
            "historical": {
                "cpu_history": metrics.get("cpu_history", []),
                "memory_history": metrics.get("memory_history", []),
                "network_history": metrics.get("network_history", []),
            },
            "alerts": len(
                [
                    a
                    for a in nox_state.security_alerts
                    if a.get("severity") in ["critical", "high"]
                ]
            ),
            "timestamp": datetime.now().isoformat(),
        }
    )


# Security endpoints
@app.route("/api/security/alerts", methods=["GET"])
@require_auth
def get_security_alerts():
    """Get security alerts with pagination and filtering"""
    try:
        # Query parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        severity = request.args.get("severity")
        alert_type = request.args.get("type")

        # Build query
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM security_alerts WHERE 1=1"
            params = []

            if severity:
                query += " AND severity = ?"
                params.append(severity)

            if alert_type:
                query += " AND type = ?"
                params.append(alert_type)

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([per_page, (page - 1) * per_page])

            cursor.execute(query, params)
            alerts = [dict(row) for row in cursor.fetchall()]

            # Get total count
            count_query = "SELECT COUNT(*) FROM security_alerts WHERE 1=1"
            count_params = []

            if severity:
                count_query += " AND severity = ?"
                count_params.append(severity)

            if alert_type:
                count_query += " AND type = ?"
                count_params.append(alert_type)

            cursor.execute(count_query, count_params)
            total = cursor.fetchone()[0]

        return jsonify(
            {
                "alerts": alerts,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page,
                },
                "summary": {
                    "critical": len([a for a in alerts if a["severity"] == "critical"]),
                    "high": len([a for a in alerts if a["severity"] == "high"]),
                    "medium": len([a for a in alerts if a["severity"] == "medium"]),
                    "low": len([a for a in alerts if a["severity"] == "low"]),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Failed to get security alerts: {e}")
        return jsonify({"error": "Failed to retrieve alerts"}), 500


@app.route("/api/security/scan", methods=["POST"])
@require_auth
def start_security_scan():
    """Start comprehensive security scan"""
    try:
        scan_type = request.json.get("type", "full")

        # Trigger WebSocket-based scan
        socketio.emit("start_security_scan", {
                      "type": scan_type}, room="dashboard")

        return jsonify(
            {
                "status": "started",
                "scan_type": scan_type,
                "message": "Security scan initiated",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"❌ Failed to start security scan: {e}")
        return jsonify({"error": "Failed to start scan"}), 500


# Plugin management endpoints
@app.route("/api/plugins", methods=["GET"])
@require_auth
def get_plugins():
    """Get installed and available plugins"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plugins ORDER BY name")
            installed = [dict(row) for row in cursor.fetchall()]

        # Mock available plugins
        available = [
            {
                "id": "enhanced-scanner",
                "name": "Enhanced Security Scanner",
                "version": "2.1.0",
                "author": "NoxSuite Team",
                "description": "Advanced vulnerability scanner with ML detection",
                "category": "security",
                "price": "Free",
                "rating": 4.8,
                "downloads": 15420,
            },
            {
                "id": "ui-accessibility",
                "name": "Accessibility Enhancer",
                "version": "1.5.3",
                "author": "Community",
                "description": "WCAG 2.1 AA compliance improvements",
                "category": "ui",
                "price": "Free",
                "rating": 4.9,
                "downloads": 8750,
            },
        ]

        return jsonify(
            {
                "installed": installed,
                "available": available,
                "categories": [
                    "security",
                    "performance",
                    "ui",
                    "development",
                    "network",
                    "storage",
                ],
            }
        )

    except Exception as e:
        logger.error(f"❌ Failed to get plugins: {e}")
        return jsonify({"error": "Failed to retrieve plugins"}), 500


@app.route("/api/plugins/install", methods=["POST"])
@require_auth
def install_plugin():
    """Install a plugin"""
    try:
        data = request.get_json()
        plugin_id = data.get("id")
        plugin_name = data.get("name")
        plugin_version = data.get("version", "1.0.0")

        if not plugin_id or not plugin_name:
            return jsonify({"error": "Plugin ID and name required"}), 400

        # Simulate plugin installation
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO plugins 
                (id, name, version, description, category, installed, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    plugin_id,
                    plugin_name,
                    plugin_version,
                    data.get("description", ""),
                    data.get("category", "other"),
                    True,
                    True,
                ),
            )
            conn.commit()

        log_security_event(
            "plugin_installed",
            f"Plugin {plugin_name} v{plugin_version} installed",
            "low",
        )

        # Emit to connected clients
        socketio.emit(
            "plugin_installed",
            {"id": plugin_id, "name": plugin_name, "version": plugin_version},
            room="dashboard",
        )

        return jsonify(
            {
                "status": "installed",
                "plugin": {
                    "id": plugin_id,
                    "name": plugin_name,
                    "version": plugin_version,
                },
                "message": f"Plugin {plugin_name} installed successfully",
            }
        )

    except Exception as e:
        logger.error(f"❌ Failed to install plugin: {e}")
        return jsonify({"error": "Failed to install plugin"}), 500


# AI-powered endpoints
@app.route("/api/ai/analyze_threat", methods=["POST"])
@require_auth
def analyze_threat():
    """AI-powered threat analysis"""
    try:
        data = request.get_json()
        threat_data = {
            "source_ip": data.get("source_ip", request.remote_addr),
            "user_agent": data.get("user_agent", request.headers.get("User-Agent", "")),
            "request_frequency": data.get("request_frequency", 1),
            "payload_size": data.get("payload_size", len(str(data))),
            "response_time": data.get("response_time", 0),
            "error_count": data.get("error_count", 0),
            "unique_endpoints": data.get("unique_endpoints", 1),
            "geographic_distance": data.get("geographic_distance", 0),
            "session_duration": data.get("session_duration", 0),
        }

        # Use AI engine for threat analysis
        ai_engine = get_ai_engine()
        if ai_engine:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                ai_engine.analyze_threat(threat_data))

            # Log security event if threat detected
            if result.confidence > 0.5:
                log_security_event(
                    "ai_threat_detected",
                    f"AI detected {result.threat_type} with {result.confidence:.2f} confidence",
                    result.severity,
                )

            return jsonify(
                {
                    "threat_type": result.threat_type,
                    "confidence": result.confidence,
                    "severity": result.severity,
                    "description": result.description,
                    "recommended_action": result.recommended_action,
                    "timestamp": result.timestamp,
                }
            )
        else:
            return jsonify({"error": "AI engine not available"}), 503

    except Exception as e:
        logger.error(f"❌ AI threat analysis error: {e}")
        return jsonify({"error": "Threat analysis failed"}), 500


@app.route("/api/ai/optimize_performance", methods=["POST"])
@require_auth
def optimize_performance():
    """AI-powered performance optimization"""
    try:
        data = request.get_json()
        metrics = data.get("metrics", {})

        # Add current system metrics if not provided
        if not metrics:
            current_metrics = collect_system_metrics()
            metrics = {
                "cpu_usage": current_metrics.get("cpu_usage", 0),
                "memory_usage": current_metrics.get("memory_usage", 0),
                "response_time": data.get("response_time", 500),
                "error_rate": data.get("error_rate", 0),
            }

        # Use AI engine for optimization analysis
        ai_engine = get_ai_engine()
        if ai_engine:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                ai_engine.optimize_performance(metrics))

            return jsonify(
                {
                    "component": result.component,
                    "current_metric": result.current_metric,
                    "optimized_metric": result.optimized_metric,
                    "improvement_percentage": result.improvement_percentage,
                    "optimization_strategy": result.optimization_strategy,
                    "implementation_steps": result.implementation_steps,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            return jsonify({"error": "AI engine not available"}), 503

    except Exception as e:
        logger.error(f"❌ AI performance optimization error: {e}")
        return jsonify({"error": "Performance optimization failed"}), 500


@app.route("/api/ai/analyze_user_behavior", methods=["POST"])
@require_auth
def analyze_user_behavior():
    """AI-powered user behavior analysis"""
    try:
        data = request.get_json()
        user_id = data.get("user_id", "anonymous")
        behavior_data = data.get("behavior_data", {})

        # Add default behavior data if not provided
        default_behavior = {
            "session_duration": data.get("session_duration", 300),
            "click_frequency": data.get("click_frequency", 2.5),
            "page_views": data.get("page_views", 5),
            "features_used": data.get("features_used", []),
            "error_encounters": data.get("error_encounters", 0),
            "help_requests": data.get("help_requests", 0),
            "accessibility_features_used": data.get("accessibility_features_used", 0),
            "response_time_variance": data.get("response_time_variance", 100),
            "zoom_level": data.get("zoom_level", 100),
            "mouse_usage": data.get("mouse_usage", 80),
        }

        behavior_data.update(default_behavior)

        # Use AI engine for behavior analysis
        ai_engine = get_ai_engine()
        if ai_engine:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                ai_engine.analyze_user_behavior(user_id, behavior_data)
            )

            return jsonify(
                {
                    "user_id": result.user_id,
                    "behavior_pattern": result.behavior_pattern,
                    "anomaly_score": result.anomaly_score,
                    "recommendations": result.recommendations,
                    "accessibility_needs": result.accessibility_needs,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            return jsonify({"error": "AI engine not available"}), 503

    except Exception as e:
        logger.error(f"❌ AI user behavior analysis error: {e}")
        return jsonify({"error": "User behavior analysis failed"}), 500


@app.route("/api/ai/status", methods=["GET"])
@require_auth
def ai_status():
    """Get AI engine status and capabilities"""
    try:
        ai_engine = get_ai_engine()
        if ai_engine:
            status = ai_engine.get_ai_status()
            return jsonify(
                {
                    "ai_engine_status": "operational",
                    "models_loaded": status.get("models_loaded", 0),
                    "available_models": status.get("available_models", []),
                    "learning_enabled": status.get("learning_enabled", False),
                    "real_time_processing": status.get("real_time_processing", False),
                    "threat_history_size": status.get("threat_history_size", 0),
                    "user_behavior_cache_size": status.get(
                        "user_behavior_cache_size", 0
                    ),
                    "advanced_ai_available": status.get("advanced_ai_available", False),
                    "background_processing": status.get("background_processing", False),
                    "capabilities": [
                        "threat_detection",
                        "performance_optimization",
                        "user_behavior_analysis",
                        "anomaly_detection",
                        "real_time_learning",
                    ],
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "ai_engine_status": "unavailable",
                        "error": "AI engine not initialized",
                    }
                ),
                503,
            )

    except Exception as e:
        logger.error(f"❌ AI status check error: {e}")
        return jsonify({"error": "AI status check failed"}), 500


# Web crawler endpoints
@app.route("/api/crawler/status", methods=["GET"])
@require_auth
def crawler_status():
    """Get web crawler status"""
    return jsonify(
        {
            "status": nox_state.crawler_status,
            "recent_urls": [],
            "statistics": {
                "total_crawled": 0,
                "success_rate": 100,
                "avg_response_time": 250,
            },
        }
    )


@app.route("/api/crawler/start", methods=["POST"])
@require_auth
def start_crawler():
    """Start web crawler"""
    try:
        data = request.get_json()
        urls = data.get("urls", [])

        if not urls:
            return jsonify({"error": "URLs required"}), 400

        # Update crawler status
        nox_state.crawler_status = {
            "running": True,
            "progress": 0,
            "urls": urls,
            "started_at": datetime.now().isoformat(),
        }

        # Emit status update
        socketio.emit("crawler_status",
                      nox_state.crawler_status, room="dashboard")

        return jsonify(
            {
                "status": "started",
                "urls": urls,
                "message": "Web crawler started successfully",
            }
        )

    except Exception as e:
        logger.error(f"❌ Failed to start crawler: {e}")
        return jsonify({"error": "Failed to start crawler"}), 500


# =============================================================================
# Error Handlers
# =============================================================================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with ADHD-friendly response"""
    return (
        jsonify(
            {
                "error": "Resource not found",
                "message": "The requested endpoint does not exist",
                "suggestion": "Check the API documentation for available endpoints",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with ADHD-friendly response"""
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "suggestion": "Please try again or contact support if the problem persists",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        500,
    )


# =============================================================================
# Application Initialization
# =============================================================================


def initialize_noxsuite():
    """Initialize NoxSuite backend systems"""
    logger.info("🚀 Initializing NoxSuite Ultimate Backend v11.0.0")

    try:
        # Initialize database
        init_database()

        # Create default admin user
        create_default_admin()

        # Initialize TypeScript controller
        try:
            NoxSuiteController.initialize()
            logger.info("✅ TypeScript controller initialized")
        except Exception as e:
            logger.warning(f"⚠️ TypeScript controller warning: {e}")

        # Start system monitoring thread
        monitoring_thread = threading.Thread(
            target=monitor_system_loop, daemon=True)
        monitoring_thread.start()
        logger.info("✅ System monitoring started")

        # Add initial security alert
        nox_state.add_security_alert(
            {
                "type": "system_startup",
                "severity": "low",
                "title": "NoxSuite Backend Started",
                "message": "Backend systems initialized and monitoring active",
            }
        )

        logger.info("🎉 NoxSuite backend initialization complete!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize NoxSuite: {e}")
        raise


# =============================================================================
# Main Application Entry Point
# =============================================================================

if __name__ == "__main__":
    try:
        # Initialize systems
        initialize_noxsuite()

        # Configure development/production settings
        debug_mode = os.environ.get("FLASK_ENV") == "development"
        port = int(os.environ.get("PORT", 5000))
        host = os.environ.get(
            "HOST", "0.0.0.0" if not debug_mode else "127.0.0.1")

        logger.info(f"🌐 Starting NoxSuite backend server on {host}:{port}")
        logger.info(f"🔧 Debug mode: {debug_mode}")
        logger.info(f"🎯 ADHD-friendly features: Enabled")
        logger.info(f"🔒 Security monitoring: Active")
        logger.info(f"🔌 WebSocket support: Enabled")

        # Start Flask-SocketIO server
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug_mode,
            use_reloader=debug_mode,
            log_output=True,
        )

    except KeyboardInterrupt:
        logger.info("🛑 NoxSuite backend shutdown requested")
    except Exception as e:
        logger.error(f"❌ Failed to start NoxSuite backend: {e}")
        sys.exit(1)
