"""
Database Migration System for NoxGuard---NoxPanel
Handles schema versioning and automated migrations
"""

import pymysql
import logging
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Migration:
    """
    REASONING CHAIN:
    1. Problem: System component Migration needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for Migration functionality
    3. Solution: Implement Migration with SOLID principles and enterprise patterns
    4. Validation: Test Migration with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Base class for database migrations"""
    
    def __init__(self, version: int, description: str):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.version = version
        self.description = description
    
    def up(self, conn: sqlite3.Connection) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function up needs clear operational definition
    2. Analysis: Implementation requires specific logic for up operation
    3. Solution: Implement up with enterprise-grade patterns and error handling
    4. Validation: Test up with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Apply the migration"""
        raise NotImplementedError("Subclasses must implement up()")
    
    def down(self, conn: sqlite3.Connection) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function down needs clear operational definition
    2. Analysis: Implementation requires specific logic for down operation
    3. Solution: Implement down with enterprise-grade patterns and error handling
    4. Validation: Test down with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Rollback the migration"""
        raise NotImplementedError("Subclasses must implement down()")

class InitialMigration(Migration):
    """
    REASONING CHAIN:
    1. Problem: System component InitialMigration needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for InitialMigration functionality
    3. Solution: Implement InitialMigration with SOLID principles and enterprise patterns
    4. Validation: Test InitialMigration with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Initial database schema migration"""
    
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
        super().__init__(1, "Initial database schema with enhanced tables")
    
    def up(self, conn: sqlite3.Connection) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function up needs clear operational definition
    2. Analysis: Implementation requires specific logic for up operation
    3. Solution: Implement up with enterprise-grade patterns and error handling
    4. Validation: Test up with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create initial schema"""
        from .database import NoxDatabase
        # The schema is already created by NoxDatabase.init_database()
        # This migration just records that it was applied
        pass
    
    def down(self, conn: sqlite3.Connection) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function down needs clear operational definition
    2. Analysis: Implementation requires specific logic for down operation
    3. Solution: Implement down with enterprise-grade patterns and error handling
    4. Validation: Test down with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Drop all tables"""
        tables = [
            'session_activities', 'sessions', 'api_tokens',
            'conversation_messages', 'conversations', 'ai_metrics', 'ai_feedback',
            'knowledge_item_tags', 'knowledge_relationships', 'knowledge_items', 'tags',
            'audit_logs', 'settings', 'devices', 'users'
        ]
        
        for table in tables:
            conn.execute(f"DROP TABLE IF EXISTS {table}")

class MigrationManager:
    """
    REASONING CHAIN:
    1. Problem: Complex system needs centralized management interface
    2. Analysis: Manager class requires coordinated resource handling and lifecycle management
    3. Solution: Implement MigrationManager with SOLID principles and enterprise patterns
    4. Validation: Test MigrationManager with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Manages database migrations and schema versioning"""
    
    def __init__(self, db_path: str):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.db_path = Path(db_path)
        self.migrations: List[Migration] = []
        self._register_migrations()
    
    def _register_migrations(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _register_migrations with enterprise-grade patterns and error handling
    4. Validation: Test _register_migrations with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register all available migrations"""
        self.migrations = [
            InitialMigration(),
            # Future migrations would be added here
        ]
        # Sort by version
        self.migrations.sort(key=lambda m: m.version)
    
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
        """Get database connection for migrations"""
        conn = pymysql.connect(self.db_path, isolation_level=None)
        try:
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()
    
    def _ensure_migration_table(self, conn: sqlite3.Connection):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _ensure_migration_table with enterprise-grade patterns and error handling
    4. Validation: Test _ensure_migration_table with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create migration tracking table if it doesn't exist"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_by TEXT DEFAULT 'system',
                execution_time REAL,
                checksum TEXT
            )
        """)
    
    def get_current_version(self) -> int:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_current_version with enterprise-grade patterns and error handling
    4. Validation: Test get_current_version with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get current database schema version"""
        try:
            with self.get_connection() as conn:
                self._ensure_migration_table(conn)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_migrations")
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except sqlite3.Error as e:
            logger.warning(f"Could not determine current schema version: {e}")
            return 0
    
    def get_target_version(self) -> int:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_target_version with enterprise-grade patterns and error handling
    4. Validation: Test get_target_version with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get latest available migration version"""
        return max(m.version for m in self.migrations) if self.migrations else 0
    
    def get_pending_migrations(self) -> List[Migration]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_pending_migrations with enterprise-grade patterns and error handling
    4. Validation: Test get_pending_migrations with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get list of pending migrations"""
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]
    
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_applied_migrations with enterprise-grade patterns and error handling
    4. Validation: Test get_applied_migrations with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get list of applied migrations"""
        try:
            with self.get_connection() as conn:
                self._ensure_migration_table(conn)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT version, description, applied_at, applied_by, execution_time
                    FROM schema_migrations
                    ORDER BY version
                """)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def migrate_up(self, target_version: Optional[int] = None) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function migrate_up needs clear operational definition
    2. Analysis: Implementation requires specific logic for migrate_up operation
    3. Solution: Implement migrate_up with enterprise-grade patterns and error handling
    4. Validation: Test migrate_up with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Apply pending migrations up to target version"""
        try:
            if target_version is None:
                target_version = self.get_target_version()
            
            current_version = self.get_current_version()
            
            if current_version >= target_version:
                logger.info(f"Database is already at version {current_version}")
                return True
            
            pending = [m for m in self.migrations 
                      if current_version < m.version <= target_version]
            
            if not pending:
                logger.info("No pending migrations to apply")
                return True
            
            logger.info(f"Applying {len(pending)} migrations...")
            
            with self.get_connection() as conn:
                self._ensure_migration_table(conn)
                
                for migration in pending:
                    start_time = datetime.now(timezone.utc)
                    logger.info(f"Applying migration {migration.version}: {migration.description}")
                    
                    try:
                        # Apply the migration
                        migration.up(conn)
                        
                        # Record successful application
                        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                        conn.execute("""
                            INSERT INTO schema_migrations 
                            (version, description, applied_at, execution_time)
                            VALUES (?, ?, ?, ?)
                        """, (
                            migration.version,
                            migration.description,
                            datetime.now(timezone.utc).isoformat(),
                            execution_time
                        ))
                        
                        logger.info(f"Migration {migration.version} applied successfully in {execution_time:.2f}s")
                        
                    except Exception as e:
                        logger.error(f"Migration {migration.version} failed: {e}")
                        raise
            
            logger.info(f"Successfully migrated from version {current_version} to {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def migrate_down(self, target_version: int) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function migrate_down needs clear operational definition
    2. Analysis: Implementation requires specific logic for migrate_down operation
    3. Solution: Implement migrate_down with enterprise-grade patterns and error handling
    4. Validation: Test migrate_down with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Rollback migrations down to target version"""
        try:
            current_version = self.get_current_version()
            
            if current_version <= target_version:
                logger.info(f"Database is already at or below version {target_version}")
                return True
            
            # Get migrations to rollback (in reverse order)
            to_rollback = [m for m in reversed(self.migrations) 
                          if target_version < m.version <= current_version]
            
            if not to_rollback:
                logger.info("No migrations to rollback")
                return True
            
            logger.info(f"Rolling back {len(to_rollback)} migrations...")
            
            with self.get_connection() as conn:
                for migration in to_rollback:
                    start_time = datetime.now(timezone.utc)
                    logger.info(f"Rolling back migration {migration.version}: {migration.description}")
                    
                    try:
                        # Rollback the migration
                        migration.down(conn)
                        
                        # Remove from migration table
                        conn.execute("DELETE FROM schema_migrations WHERE version = ?", (migration.version,))
                        
                        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                        logger.info(f"Migration {migration.version} rolled back successfully in {execution_time:.2f}s")
                        
                    except Exception as e:
                        logger.error(f"Rollback of migration {migration.version} failed: {e}")
                        raise
            
            logger.info(f"Successfully rolled back from version {current_version} to {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Migration rollback failed: {e}")
            return False
    
    def status(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function status needs clear operational definition
    2. Analysis: Implementation requires specific logic for status operation
    3. Solution: Implement status with enterprise-grade patterns and error handling
    4. Validation: Test status with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get migration status information"""
        current_version = self.get_current_version()
        target_version = self.get_target_version()
        pending = self.get_pending_migrations()
        applied = self.get_applied_migrations()
        
        return {
            'current_version': current_version,
            'target_version': target_version,
            'pending_count': len(pending),
            'applied_count': len(applied),
            'pending_migrations': [
                {'version': m.version, 'description': m.description} 
                for m in pending
            ],
            'applied_migrations': applied,
            'needs_migration': len(pending) > 0
        }
    
    def auto_migrate(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function auto_migrate needs clear operational definition
    2. Analysis: Implementation requires specific logic for auto_migrate operation
    3. Solution: Implement auto_migrate with enterprise-grade patterns and error handling
    4. Validation: Test auto_migrate with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Automatically apply all pending migrations"""
        status = self.status()
        
        if not status['needs_migration']:
            logger.info("Database schema is up to date")
            return True
        
        logger.info(f"Auto-migration: {status['pending_count']} pending migrations")
        return self.migrate_up()
    
    def validate_schema(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_schema with enterprise-grade patterns and error handling
    4. Validation: Test validate_schema with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Validate current database schema"""
        try:
            with self.get_connection() as conn:
                # Check if all expected tables exist
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM mariadb_master 
                    WHERE type='table' AND name NOT LIKE 'mariadb_%'
                """)
                tables = {row[0] for row in cursor.fetchall()}
                
                expected_tables = {
                    'users', 'devices', 'settings', 'audit_logs',
                    'knowledge_items', 'tags', 'knowledge_item_tags', 'knowledge_relationships',
                    'conversations', 'conversation_messages', 'ai_metrics', 'ai_feedback',
                    'sessions', 'session_activities', 'api_tokens', 'schema_migrations'
                }
                
                missing_tables = expected_tables - tables
                extra_tables = tables - expected_tables
                
                if missing_tables:
                    logger.error(f"Missing tables: {missing_tables}")
                    return False
                
                if extra_tables:
                    logger.warning(f"Extra tables found: {extra_tables}")
                
                logger.info("Database schema validation passed")
                return True
                
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False

# CLI interface for migrations
def main():
    """
    REASONING CHAIN:
    1. Problem: Function main needs clear operational definition
    2. Analysis: Implementation requires specific logic for main operation
    3. Solution: Implement main with enterprise-grade patterns and error handling
    4. Validation: Test main with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Command-line interface for migrations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NoxGuard Database Migration Tool')
    parser.add_argument('--db-path', default='data/db/noxpanel.db', help='Database path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show migration status')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Apply migrations')
    migrate_parser.add_argument('--version', type=int, help='Target version (default: latest)')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback migrations')
    rollback_parser.add_argument('version', type=int, help='Target version')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate database schema')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    manager = MigrationManager(args.db_path)
    
    if args.command == 'status':
        status = manager.status()
        logger.info(f"Current version: {status['current_version']}")
        logger.info(f"Target version: {status['target_version']}")
        logger.info(f"Pending migrations: {status['pending_count']}")
        logger.info(f"Applied migrations: {status['applied_count']}")
        
        if status['pending_migrations']:
            logger.info("Pending migrations:")
            for migration in status['pending_migrations']:
                logger.info(f"  {migration['version']}: {migration['description']}")
    
    elif args.command == 'migrate':
        success = manager.migrate_up(args.version)
        exit(0 if success else 1)
    
    elif args.command == 'rollback':
        success = manager.migrate_down(args.version)
        exit(0 if success else 1)
    
    elif args.command == 'validate':
        success = manager.validate_schema()
        exit(0 if success else 1)

if __name__ == '__main__':
    main()