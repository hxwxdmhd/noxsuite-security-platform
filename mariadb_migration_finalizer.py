#!/usr/bin/env python3
"""
MariaDB Migration Finalizer
===========================
Completes the final 5% of SQLite to MariaDB migration with comprehensive validation.
"""

import os
import sys
import logging
import sqlite3
import mysql.connector
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MariaDBMigrationFinalizer:
    def __init__(self):
        self.sqlite_db = "noxsuite.db"
        self.mariadb_config = {
            'host': os.environ.get('MARIADB_HOST', 'localhost'),
            'port': int(os.environ.get('MARIADB_PORT', '3306')),
            'user': os.environ.get('MARIADB_USER', 'noxsuite'),
            'password': os.environ.get('MARIADB_PASSWORD', ''),
            'database': os.environ.get('MARIADB_DATABASE', 'noxsuite'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        self.migration_status = {}
        
    def check_sqlite_connection(self) -> bool:
        """Verify SQLite database connectivity"""
        try:
            if not os.path.exists(self.sqlite_db):
                logger.warning(f"SQLite database {self.sqlite_db} not found")
                return False
                
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            logger.info(f"✅ SQLite connection successful - {len(tables)} tables found")
            return True
            
        except Exception as e:
            logger.error(f"❌ SQLite connection failed: {e}")
            return False
    
    def check_mariadb_connection(self) -> bool:
        """Verify MariaDB database connectivity"""
        try:
            conn = mysql.connector.connect(**self.mariadb_config)
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            conn.close()
            
            logger.info(f"✅ MariaDB connection successful - {len(tables)} tables found")
            return True
            
        except Exception as e:
            logger.error(f"❌ MariaDB connection failed: {e}")
            logger.error(f"Config: {self.mariadb_config}")
            return False
    
    def get_sqlite_schema(self) -> Dict[str, str]:
        """Extract complete schema from SQLite"""
        schema = {}
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}';")
                schema[table] = cursor.fetchone()[0]
            
            conn.close()
            logger.info(f"📊 Extracted schema for {len(schema)} tables")
            
        except Exception as e:
            logger.error(f"❌ Failed to extract SQLite schema: {e}")
            
        return schema
    
    def get_mariadb_schema(self) -> Dict[str, str]:
        """Extract complete schema from MariaDB"""
        schema = {}
        try:
            conn = mysql.connector.connect(**self.mariadb_config)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"SHOW CREATE TABLE {table};")
                result = cursor.fetchone()
                if result:
                    schema[table] = result[1]
            
            conn.close()
            logger.info(f"📊 Extracted MariaDB schema for {len(schema)} tables")
            
        except Exception as e:
            logger.error(f"❌ Failed to extract MariaDB schema: {e}")
            
        return schema
    
    def compare_table_counts(self) -> Dict[str, Dict[str, int]]:
        """Compare record counts between SQLite and MariaDB"""
        counts = {}
        
        try:
            # SQLite counts
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
            
            # MariaDB counts
            mariadb_conn = mysql.connector.connect(**self.mariadb_config)
            mariadb_cursor = mariadb_conn.cursor()
            mariadb_cursor.execute("SHOW TABLES;")
            mariadb_tables = [row[0] for row in mariadb_cursor.fetchall()]
            
            # Compare counts for common tables
            common_tables = set(sqlite_tables) & set(mariadb_tables)
            
            for table in common_tables:
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table};")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                mariadb_cursor.execute(f"SELECT COUNT(*) FROM {table};")
                mariadb_count = mariadb_cursor.fetchone()[0]
                
                counts[table] = {
                    'sqlite': sqlite_count,
                    'mariadb': mariadb_count,
                    'match': sqlite_count == mariadb_count
                }
            
            sqlite_conn.close()
            mariadb_conn.close()
            
            logger.info(f"📊 Compared counts for {len(counts)} tables")
            
        except Exception as e:
            logger.error(f"❌ Failed to compare table counts: {e}")
            
        return counts
    
    def validate_data_integrity(self) -> Dict[str, bool]:
        """Validate critical data integrity between databases"""
        validation_results = {}
        
        try:
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            mariadb_conn = mysql.connector.connect(**self.mariadb_config)
            
            # Validate users table
            validation_results['users'] = self._validate_users_table(
                sqlite_conn, mariadb_conn
            )
            
            # Validate roles table
            validation_results['roles'] = self._validate_roles_table(
                sqlite_conn, mariadb_conn
            )
            
            # Validate user_roles table
            validation_results['user_roles'] = self._validate_user_roles_table(
                sqlite_conn, mariadb_conn
            )
            
            sqlite_conn.close()
            mariadb_conn.close()
            
        except Exception as e:
            logger.error(f"❌ Data integrity validation failed: {e}")
            
        return validation_results
    
    def _validate_users_table(self, sqlite_conn, mariadb_conn) -> bool:
        """Validate users table data integrity"""
        try:
            sqlite_cursor = sqlite_conn.cursor()
            mariadb_cursor = mariadb_conn.cursor()
            
            # Check if users exist in both databases
            sqlite_cursor.execute("SELECT id, username, email FROM users ORDER BY id;")
            sqlite_users = sqlite_cursor.fetchall()
            
            mariadb_cursor.execute("SELECT id, username, email FROM users ORDER BY id;")
            mariadb_users = mariadb_cursor.fetchall()
            
            if sqlite_users == mariadb_users:
                logger.info("✅ Users table data integrity validated")
                return True
            else:
                logger.error("❌ Users table data mismatch detected")
                logger.error(f"SQLite users: {len(sqlite_users)}")
                logger.error(f"MariaDB users: {len(mariadb_users)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Users table validation failed: {e}")
            return False
    
    def _validate_roles_table(self, sqlite_conn, mariadb_conn) -> bool:
        """Validate roles table data integrity"""
        try:
            sqlite_cursor = sqlite_conn.cursor()
            mariadb_cursor = mariadb_conn.cursor()
            
            sqlite_cursor.execute("SELECT id, name, permissions FROM roles ORDER BY id;")
            sqlite_roles = sqlite_cursor.fetchall()
            
            mariadb_cursor.execute("SELECT id, name, permissions FROM roles ORDER BY id;")
            mariadb_roles = mariadb_cursor.fetchall()
            
            if sqlite_roles == mariadb_roles:
                logger.info("✅ Roles table data integrity validated")
                return True
            else:
                logger.error("❌ Roles table data mismatch detected")
                return False
                
        except Exception as e:
            logger.error(f"❌ Roles table validation failed: {e}")
            return False
    
    def _validate_user_roles_table(self, sqlite_conn, mariadb_conn) -> bool:
        """Validate user_roles table data integrity"""
        try:
            sqlite_cursor = sqlite_conn.cursor()
            mariadb_cursor = mariadb_conn.cursor()
            
            sqlite_cursor.execute("SELECT user_id, role_id FROM user_roles ORDER BY user_id, role_id;")
            sqlite_user_roles = sqlite_cursor.fetchall()
            
            mariadb_cursor.execute("SELECT user_id, role_id FROM user_roles ORDER BY user_id, role_id;")
            mariadb_user_roles = mariadb_cursor.fetchall()
            
            if sqlite_user_roles == mariadb_user_roles:
                logger.info("✅ User roles table data integrity validated")
                return True
            else:
                logger.error("❌ User roles table data mismatch detected")
                return False
                
        except Exception as e:
            logger.error(f"❌ User roles table validation failed: {e}")
            return False
    
    def update_connection_strings(self) -> bool:
        """Update all application connection strings to use MariaDB"""
        connection_files = [
            "backend/models/user.py",
            "app.py",
            "database_config.py"
        ]
        
        updated_files = []
        
        for file_path in connection_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace SQLite connection with MariaDB
                    if "sqlite://" in content:
                        updated_content = content.replace(
                            "sqlite:///noxsuite.db",
                            f"mysql://{self.mariadb_config['user']}:{self.mariadb_config['password']}@{self.mariadb_config['host']}:{self.mariadb_config['port']}/{self.mariadb_config['database']}"
                        )
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        updated_files.append(file_path)
                        logger.info(f"✅ Updated connection string in {file_path}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to update {file_path}: {e}")
        
        if updated_files:
            logger.info(f"📝 Updated connection strings in {len(updated_files)} files")
            return True
        else:
            logger.warning("⚠️ No files required connection string updates")
            return False
    
    def finalize_migration(self) -> Dict[str, Any]:
        """Complete the final migration steps"""
        logger.info("🚀 Starting MariaDB migration finalization...")
        
        results = {
            'sqlite_connection': False,
            'mariadb_connection': False,
            'schema_comparison': {},
            'data_counts': {},
            'data_integrity': {},
            'connection_updates': False,
            'migration_complete': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Verify connections
        results['sqlite_connection'] = self.check_sqlite_connection()
        results['mariadb_connection'] = self.check_mariadb_connection()
        
        if not results['mariadb_connection']:
            logger.error("❌ Cannot proceed - MariaDB connection failed")
            return results
        
        # Step 2: Compare schemas
        sqlite_schema = self.get_sqlite_schema()
        mariadb_schema = self.get_mariadb_schema()
        results['schema_comparison'] = {
            'sqlite_tables': list(sqlite_schema.keys()),
            'mariadb_tables': list(mariadb_schema.keys()),
            'missing_in_mariadb': list(set(sqlite_schema.keys()) - set(mariadb_schema.keys()))
        }
        
        # Step 3: Compare data counts
        results['data_counts'] = self.compare_table_counts()
        
        # Step 4: Validate data integrity
        results['data_integrity'] = self.validate_data_integrity()
        
        # Step 5: Update connection strings
        results['connection_updates'] = self.update_connection_strings()
        
        # Determine if migration is complete
        integrity_passed = all(results['data_integrity'].values())
        counts_match = all(
            table_data['match'] 
            for table_data in results['data_counts'].values()
        )
        
        results['migration_complete'] = (
            results['mariadb_connection'] and
            integrity_passed and
            counts_match and
            not results['schema_comparison']['missing_in_mariadb']
        )
        
        if results['migration_complete']:
            logger.info("🎉 Migration finalization SUCCESSFUL!")
        else:
            logger.error("❌ Migration finalization FAILED - review results")
        
        return results
    
    def generate_migration_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive migration report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"mariadb_migration_final_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📋 Migration report saved to: {report_file}")
        
        # Generate summary
        if results['migration_complete']:
            summary = "✅ MIGRATION COMPLETE - MariaDB is ready for production!"
        else:
            summary = "❌ MIGRATION INCOMPLETE - Manual intervention required"
        
        logger.info(f"📊 Migration Summary: {summary}")
        return report_file


def main():
    """Main execution function"""
    logger.info("🔄 MariaDB Migration Finalizer - Starting Final Steps")
    
    finalizer = MariaDBMigrationFinalizer()
    results = finalizer.finalize_migration()
    report_file = finalizer.generate_migration_report(results)
    
    if results['migration_complete']:
        logger.info("🎉 SUCCESS: MariaDB migration 100% complete!")
        sys.exit(0)
    else:
        logger.error("❌ FAILURE: Migration incomplete - manual fixes required")
        sys.exit(1)


if __name__ == "__main__":
    main()
