"""
Enhanced Database Layer for NoxGuard---NoxPanel System
Implements complete schema with knowledge management, AI conversations, and session handling
"""

import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pymysql

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """
    REASONING CHAIN:
    1. Problem: System component DatabaseConnectionPool needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for DatabaseConnectionPool functionality
    3. Solution: Implement DatabaseConnectionPool with SOLID principles and enterprise patterns
    4. Validation: Test DatabaseConnectionPool with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """SQLite connection pool for improved performance"""
    
    def __init__(self, db_path: str, pool_size: int = 10, timeout: float = 30.0):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool = []
        self._lock = threading.Lock()
        self._create_pool()
    
    def _create_pool(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_pool with enterprise-grade patterns and error handling
    4. Validation: Test _create_pool with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            conn = pymysql.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None,  # autocommit mode
                timeout=self.timeout
            )
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            self._pool.append(conn)
    
    def get_connection(self) -> sqlite3.Connection:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_connection with enterprise-grade patterns and error handling
    4. Validation: Test get_connection with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get connection from pool"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            else:
                # Create new connection if pool is empty
                conn = pymysql.connect(
                    self.db_path,
                    check_same_thread=False,
                    isolation_level=None,
                    timeout=self.timeout
                )
                conn.execute("PRAGMA journal_mode=WAL")
                return conn
    
    def return_connection(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Function return_connection needs clear operational definition
    2. Analysis: Implementation requires specific logic for return_connection operation
    3. Solution: Implement return_connection with enterprise-grade patterns and error handling
    4. Validation: Test return_connection with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Return connection to pool"""
        try:
            # Test connection health
            conn.execute("SELECT 1").fetchone()
            with self._lock:
                if len(self._pool) < self.pool_size:
                    self._pool.append(conn)
                else:
                    conn.close()
        except sqlite3.Error:
            # Connection is unhealthy, close it
            try:
                conn.close()
            except Exception:
                pass
    
    def close_all(self):
    """
    REASONING CHAIN:
    1. Problem: Function close_all needs clear operational definition
    2. Analysis: Implementation requires specific logic for close_all operation
    3. Solution: Implement close_all with enterprise-grade patterns and error handling
    4. Validation: Test close_all with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Close all connections in pool"""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._pool.clear()

class NoxDatabase:
    """
    REASONING CHAIN:
    1. Problem: System component NoxDatabase needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for NoxDatabase functionality
    3. Solution: Implement NoxDatabase with SOLID principles and enterprise patterns
    4. Validation: Test NoxDatabase with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Enhanced database manager for NoxGuard---NoxPanel system"""
    
    # Database schema version for migrations
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: str = "data/db/noxpanel.db", pool_size: int = 10):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize database with connection pooling"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize connection pool
        self.pool = DatabaseConnectionPool(str(self.db_path), pool_size)
        
        # Initialize database schema
        self.init_database()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_connection with enterprise-grade patterns and error handling
    4. Validation: Test get_connection with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Context manager for database connections"""
        conn = self.pool.get_connection()
        try:
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            self.pool.return_connection(conn)
    
    def init_database(self):
    """
    REASONING CHAIN:
    1. Problem: Function init_database needs clear operational definition
    2. Analysis: Implementation requires specific logic for init_database operation
    3. Solution: Implement init_database with enterprise-grade patterns and error handling
    4. Validation: Test init_database with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize complete database schema"""
        try:
            with self.get_connection() as conn:
                # Create all tables
                self._create_core_tables(conn)
                self._create_knowledge_tables(conn)
                self._create_ai_tables(conn)
                self._create_session_tables(conn)
                self._create_indexes(conn)
                
                # Initialize metadata
                self._init_metadata(conn)
                
                # Create default admin user
                self._create_default_user(conn)
                
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_core_tables(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_core_tables with enterprise-grade patterns and error handling
    4. Validation: Test _create_core_tables with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create core system tables"""
        conn.executescript("""
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                settings TEXT DEFAULT '{}',
                preferences TEXT DEFAULT '{}'
            );
            
            -- Network devices table
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                ip_address TEXT UNIQUE NOT NULL,
                mac_address TEXT,
                device_type TEXT,
                vendor TEXT,
                operating_system TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                online BOOLEAN DEFAULT 0,
                port_scan_data TEXT DEFAULT '{}',
                vulnerability_data TEXT DEFAULT '{}',
                notes TEXT,
                tags TEXT DEFAULT '[]'
            );
            
            -- System settings table
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER,
                FOREIGN KEY (updated_by) REFERENCES users (id)
            );
            
            -- Audit logs table
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT DEFAULT '{}',
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
    
    def _create_knowledge_tables(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_knowledge_tables with enterprise-grade patterns and error handling
    4. Validation: Test _create_knowledge_tables with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create knowledge management tables"""
        conn.executescript("""
            -- Knowledge items table
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                category TEXT DEFAULT 'general',
                source TEXT,
                source_url TEXT,
                author_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                metadata TEXT DEFAULT '{}',
                vector_embedding BLOB,
                search_keywords TEXT,
                FOREIGN KEY (author_id) REFERENCES users (id)
            );
            
            -- Tags table for categorization
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#808080',
                category TEXT DEFAULT 'general',
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users (id)
            );
            
            -- Knowledge item tags relationship
            CREATE TABLE IF NOT EXISTS knowledge_item_tags (
                knowledge_item_id INTEGER,
                tag_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (knowledge_item_id, tag_id),
                FOREIGN KEY (knowledge_item_id) REFERENCES knowledge_items (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            );
            
            -- Knowledge item relationships
            CREATE TABLE IF NOT EXISTS knowledge_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_item_id INTEGER,
                target_item_id INTEGER,
                relationship_type TEXT DEFAULT 'related',
                strength REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_item_id) REFERENCES knowledge_items (id) ON DELETE CASCADE,
                FOREIGN KEY (target_item_id) REFERENCES knowledge_items (id) ON DELETE CASCADE
            );
        """)
    
    def _create_ai_tables(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_ai_tables with enterprise-grade patterns and error handling
    4. Validation: Test _create_ai_tables with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create AI conversation and interaction tables"""
        conn.executescript("""
            -- AI conversations table
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                title TEXT,
                model_name TEXT,
                model_version TEXT,
                context_window INTEGER DEFAULT 4096,
                total_tokens INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            -- AI messages within conversations
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                token_count INTEGER DEFAULT 0,
                response_time REAL,
                model_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            );
            
            -- AI model performance metrics
            CREATE TABLE IF NOT EXISTS ai_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                context TEXT DEFAULT '{}',
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- AI training and feedback data
            CREATE TABLE IF NOT EXISTS ai_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                message_id INTEGER,
                user_id INTEGER,
                feedback_type TEXT CHECK (feedback_type IN ('positive', 'negative', 'neutral')),
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                FOREIGN KEY (message_id) REFERENCES conversation_messages (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
    
    def _create_session_tables(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_session_tables with enterprise-grade patterns and error handling
    4. Validation: Test _create_session_tables with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create session management tables"""
        conn.executescript("""
            -- User sessions table
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                session_data TEXT DEFAULT '{}',
                security_flags TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
            
            -- Session activities log
            CREATE TABLE IF NOT EXISTS session_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                activity_type TEXT NOT NULL,
                activity_data TEXT DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            );
            
            -- API tokens table
            CREATE TABLE IF NOT EXISTS api_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token_hash TEXT UNIQUE NOT NULL,
                name TEXT,
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_used TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                rate_limit INTEGER DEFAULT 1000,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
    
    def _create_indexes(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_indexes with enterprise-grade patterns and error handling
    4. Validation: Test _create_indexes with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create database indexes for performance"""
        conn.executescript("""
            -- User indexes
            CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
            CREATE INDEX IF NOT EXISTS idx_users_active ON users (active);
            CREATE INDEX IF NOT EXISTS idx_users_last_login ON users (last_login);
            
            -- Device indexes
            CREATE INDEX IF NOT EXISTS idx_devices_ip ON devices (ip_address);
            CREATE INDEX IF NOT EXISTS idx_devices_mac ON devices (mac_address);
            CREATE INDEX IF NOT EXISTS idx_devices_online ON devices (online);
            CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices (last_seen);
            CREATE INDEX IF NOT EXISTS idx_devices_type ON devices (device_type);
            
            -- Knowledge indexes
            CREATE INDEX IF NOT EXISTS idx_knowledge_title ON knowledge_items (title);
            CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_items (category);
            CREATE INDEX IF NOT EXISTS idx_knowledge_author ON knowledge_items (author_id);
            CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge_items (created_at);
            CREATE INDEX IF NOT EXISTS idx_knowledge_status ON knowledge_items (status);
            CREATE INDEX IF NOT EXISTS idx_knowledge_keywords ON knowledge_items (search_keywords);
            
            -- Tag indexes
            CREATE INDEX IF NOT EXISTS idx_tags_name ON tags (name);
            CREATE INDEX IF NOT EXISTS idx_tags_category ON tags (category);
            CREATE INDEX IF NOT EXISTS idx_tags_usage ON tags (usage_count);
            
            -- Conversation indexes
            CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations (user_id);
            CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations (session_id);
            CREATE INDEX IF NOT EXISTS idx_conversations_started ON conversations (started_at);
            CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations (status);
            
            -- Message indexes
            CREATE INDEX IF NOT EXISTS idx_messages_conversation ON conversation_messages (conversation_id);
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON conversation_messages (timestamp);
            CREATE INDEX IF NOT EXISTS idx_messages_role ON conversation_messages (role);
            
            -- Session indexes
            CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions (user_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions (active);
            CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions (expires_at);
            CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions (last_activity);
            
            -- Audit log indexes
            CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs (user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs (action);
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs (timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs (resource_type, resource_id);
        """)
    
    def _init_metadata(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _init_metadata with enterprise-grade patterns and error handling
    4. Validation: Test _init_metadata with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize database metadata"""
        conn.execute("""
            INSERT OR REPLACE INTO settings (key, value, category, description)
            VALUES (?, ?, ?, ?)
        """, (
            'db_schema_version',
            str(self.SCHEMA_VERSION),
            'system',
            'Database schema version for migrations'
        ))
        
        conn.execute("""
            INSERT OR REPLACE INTO settings (key, value, category, description)
            VALUES (?, ?, ?, ?)
        """, (
            'db_initialized_at',
            datetime.now(timezone.utc).isoformat(),
            'system',
            'Database initialization timestamp'
        ))
    
    def _create_default_user(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_default_user with enterprise-grade patterns and error handling
    4. Validation: Test _create_default_user with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create default admin user if none exists"""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
        
        if cursor.fetchone()[0] == 0:
            # Simple password hashing (in production, use proper hashing like bcrypt)
            import hashlib
            admin_password = os.getenv("ADMIN_PASS", "admin123!")
            hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role, settings, preferences)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "admin",
                hashed_password,
                "admin@noxguard.local",
                "admin",
                json.dumps({"theme": "dark", "notifications": True}),
                json.dumps({"dashboard_layout": "default", "auto_refresh": 30})
            ))
            
            logger.info("Default admin user created")
    
    def close(self):
    """
    REASONING CHAIN:
    1. Problem: Function close needs clear operational definition
    2. Analysis: Implementation requires specific logic for close operation
    3. Solution: Implement close with enterprise-grade patterns and error handling
    4. Validation: Test close with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Close database connection pool"""
        self.pool.close_all()
    
    def __enter__(self):
    """
    Enhanced __enter__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __enter__ with enterprise-grade patterns and error handling
    4. Validation: Test __enter__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
    """
    Enhanced __exit__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __exit__ with enterprise-grade patterns and error handling
    4. Validation: Test __exit__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.close()

# Export the main class
__all__ = ['NoxDatabase', 'DatabaseConnectionPool']