#!/usr/bin/env python3
"""
MariaDB Migration Helper
Automates migration from SQLite to MariaDB for NoxSuite
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MariaDBMigration")

# Configuration
DEFAULT_CONFIG = {
    "mariadb": {
        "host": "localhost",
        "port": 3306,
        "database": "noxsuite_db",
        "user": "noxsuite_user",
        "password": os.environ.get("DB_PASSWORD", ""),  # Will be loaded from env var
        "root_password": os.environ.get("DB_PASSWORD", "")  # Will be loaded from env var
    },
    "container_name": "noxsuite-mariadb",
    "sqlite_db_path": "data/noxsuite.db",
    "docker_image": "mariadb:10.11-jammy",
    "backup_dir": "data/backup",
    "migration_script_dir": "scripts/migration",
}


class MariaDBMigrationHelper:
    """Helper class to migrate from SQLite to MariaDB"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or DEFAULT_CONFIG.copy()
        self.update_config_from_env()
        
        # Create necessary directories
        Path(self.config["backup_dir"]).mkdir(parents=True, exist_ok=True)
        Path(self.config["migration_script_dir"]).mkdir(parents=True, exist_ok=True)
        
        # Verify SQLite database exists
        sqlite_path = Path(self.config["sqlite_db_path"])
        if not sqlite_path.exists():
            logger.warning(f"SQLite database not found at {sqlite_path}")
        else:
            logger.info(f"Found SQLite database at {sqlite_path}")
    
    def update_config_from_env(self):
        """Update configuration from environment variables"""
        self.config["mariadb"]["password"] = os.environ.get(
            "DB_PASSWORD", self.config["mariadb"]["password"]
        )
        self.config["mariadb"]["root_password"] = os.environ.get(
            "MYSQL_ROOT_PASSWORD", self.config["mariadb"]["root_password"]
        )
        
        # Other config options
        self.config["mariadb"]["host"] = os.environ.get(
            "DB_HOST", self.config["mariadb"]["host"]
        )
        self.config["mariadb"]["port"] = int(os.environ.get(
            "DB_PORT", str(self.config["mariadb"]["port"])
        ))
        self.config["mariadb"]["user"] = os.environ.get(
            "DB_USER", self.config["mariadb"]["user"]
        )
        self.config["mariadb"]["database"] = os.environ.get(
            "DB_NAME", self.config["mariadb"]["database"]
        )
    
    def check_docker_installed(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True, 
                capture_output=True, 
                text=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def check_mariadb_container(self) -> bool:
        """Check if MariaDB container exists and is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", 
                 f"name={self.config['container_name']}", "--format", "{{.Status}}"],
                check=True,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                return False
                
            return "Up" in result.stdout
        except subprocess.SubprocessError:
            return False
    
    def backup_sqlite_db(self) -> str:
        """Create backup of SQLite database"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = Path(f"{self.config['backup_dir']}/noxsuite_backup_{timestamp}.db")
        
        sqlite_path = Path(self.config["sqlite_db_path"])
        if not sqlite_path.exists():
            logger.error(f"SQLite database not found at {sqlite_path}")
            return ""
        
        try:
            import shutil
            shutil.copy2(sqlite_path, backup_path)
            logger.info(f"Created backup at {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
    
    def start_mariadb_container(self) -> bool:
        """Start MariaDB Docker container"""
        if not self.check_docker_installed():
            logger.error("Docker not found. Please install Docker first.")
            return False
        
        if self.check_mariadb_container():
            logger.info(f"Container {self.config['container_name']} is already running")
            return True
        
        # Check if container exists but is stopped
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", 
                 f"name={self.config['container_name']}", "--format", "{{.Names}}"],
                check=True, 
                capture_output=True, 
                text=True
            )
            
            if result.stdout.strip():
                # Container exists, start it
                logger.info(f"Starting existing container {self.config['container_name']}...")
                subprocess.run(
                    ["docker", "start", self.config["container_name"]],
                    check=True
                )
                logger.info("MariaDB container started successfully")
                
                # Wait for container to be ready
                time.sleep(10)  # Give MariaDB time to start
                return True
                
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to check container status: {e}")
            return False
        
        # Create and start new container
        logger.info(f"Creating new MariaDB container {self.config['container_name']}...")
        
        try:
            cmd = [
                "docker", "run", "-d",
                "--name", self.config["container_name"],
                "-p", f"{self.config['mariadb']['port']}:3306",
                "-e", f"MYSQL_ROOT_PASSWORD={os.environ.get('MYSQL_ROOT_PASSWORD', '')}", 
                "-e", f"MYSQL_DATABASE={self.config['mariadb']['database']}",
                "-e", f"MYSQL_USER={self.config['mariadb']['user']}",
                "-e", f"MYSQL_PASSWORD={self.config['mariadb']['password']}",
                "-v", "noxsuite_mariadb_data:/var/lib/mysql",
                self.config["docker_image"]
            ]
            
            subprocess.run(cmd, check=True)
            logger.info("MariaDB container started successfully")
            
            # Wait for container to be ready
            time.sleep(20)  # Give MariaDB time to initialize
            return True
            
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to start MariaDB container: {e}")
            return False
    
    def generate_migration_schema(self) -> str:
        """Generate MariaDB schema from SQLite database"""
        migration_script_path = Path(f"{self.config['migration_script_dir']}/sqlite_to_mariadb.sql")
        
        # First, get the SQLite schema
        sqlite_path = Path(self.config["sqlite_db_path"])
        if not sqlite_path.exists():
            logger.error(f"SQLite database not found at {sqlite_path}")
            return ""
        
        try:
            # Get schema from SQLite
            import sqlite3
            conn = sqlite3.connect(self.config["sqlite_db_path"])
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Generate schema
            schema = []
            schema.append("-- Migration script: SQLite to MariaDB")
            schema.append("-- Generated automatically by NoxSuite Migration Helper")
            schema.append(f"-- Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            schema.append("")
            schema.append("SET FOREIGN_KEY_CHECKS=0;")
            schema.append("")
            
            for table in tables:
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                create_table = f"CREATE TABLE IF NOT EXISTS `{table}` ("
                column_defs = []
                
                for col in columns:
                    col_id, name, col_type, not_null, default_val, is_pk = col
                    
                    # Convert SQLite types to MariaDB types
                    if col_type.lower() == "integer primary key":
                        col_type = "INT AUTO_INCREMENT PRIMARY KEY"
                    elif col_type.lower() == "integer":
                        col_type = "INT"
                    elif col_type.lower() == "text":
                        col_type = "TEXT"
                    elif col_type.lower() == "real":
                        col_type = "DOUBLE"
                    elif col_type.lower() == "blob":
                        col_type = "BLOB"
                    
                    col_def = f"`{name}` {col_type}"
                    
                    if not_null:
                        col_def += " NOT NULL"
                        
                    if default_val is not None:
                        if isinstance(default_val, str):
                            col_def += f" DEFAULT '{default_val}'"
                        else:
                            col_def += f" DEFAULT {default_val}"
                            
                    if is_pk and "PRIMARY KEY" not in col_type:
                        col_def += " PRIMARY KEY"
                        
                    column_defs.append(col_def)
                
                create_table += ", ".join(column_defs) + ");"
                schema.append(create_table)
                schema.append("")
                
                # Get all data
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Generate INSERT statements
                if rows:
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, str):
                                # Escape single quotes
                                escaped_val = val.replace("'", "''")
                                values.append(f"'{escaped_val}'")
                            else:
                                values.append(str(val))
                        
                        insert = f"INSERT INTO `{table}` (`{'`, `'.join(column_names)}`) VALUES ({', '.join(values)});"
                        schema.append(insert)
                    
                    schema.append("")
            
            schema.append("SET FOREIGN_KEY_CHECKS=1;")
            
            # Write schema to file
            with open(migration_script_path, "w") as f:
                f.write("\n".join(schema))
            
            logger.info(f"Generated migration schema at {migration_script_path}")
            return str(migration_script_path)
            
        except Exception as e:
            logger.error(f"Failed to generate migration schema: {e}")
            return ""
        finally:
            if 'conn' in locals():
                conn.close()
    
    def execute_migration(self, schema_path: str) -> bool:
        """Execute migration script against MariaDB"""
        if not schema_path:
            logger.error("No schema file provided for migration")
            return False
        
        if not Path(schema_path).exists():
            logger.error(f"Schema file not found at {schema_path}")
            return False
        
        try:
            # Run mysql client inside the container to execute migration script
            cmd = [
                "docker", "exec", "-i", self.config["container_name"],
                "mysql", 
                f"--user=root",
                f"--password={self.config['mariadb']['root_password']}",
                self.config["mariadb"]["database"]
            ]
            
            with open(schema_path, "r") as f:
                schema_content = f.read()
            
            process = subprocess.run(
                cmd,
                input=schema_content,
                text=True,
                capture_output=True
            )
            
            if process.returncode != 0:
                logger.error(f"Migration failed: {process.stderr}")
                return False
            
            logger.info("Migration completed successfully")
            return True
            
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to execute migration: {e}")
            return False
    
    def update_app_config(self) -> bool:
        """Update application configuration to use MariaDB"""
        # Config file locations to check and update
        config_files = [
            ".env",
            ".env.example",
            "config.py",
            "app_config.py",
            "database_config.py"
        ]
        
        found_and_updated = False
        
        # Look for config files in root and common directories
        dirs_to_check = [".", "config", "app", "src"]
        
        for dir_name in dirs_to_check:
            for config_name in config_files:
                config_path = Path(dir_name) / config_name
                if config_path.exists() and config_path.is_file():
                    try:
                        with open(config_path, "r") as f:
                            content = f.read()
                        
                        # Check if it's already configured for MariaDB
                        if "mariadb" in content.lower() or "mysql" in content.lower():
                            logger.info(f"Config file {config_path} already contains MariaDB configuration")
                            found_and_updated = True
                            continue
                        
                        # Update .env style files
                        if config_name.startswith(".env"):
                            new_content = self.update_env_config(content)
                        # Update Python config files
                        else:
                            new_content = self.update_python_config(content)
                        
                        with open(config_path, "w") as f:
                            f.write(new_content)
                        
                        logger.info(f"Updated configuration in {config_path}")
                        found_and_updated = True
                    
                    except Exception as e:
                        logger.error(f"Failed to update config file {config_path}: {e}")
        
        # Create .env file if not found
        if not found_and_updated:
            env_path = Path(".env")
            env_content = self.generate_env_config()
            
            with open(env_path, "w") as f:
                f.write(env_content)
            
            logger.info(f"Created new .env configuration file at {env_path}")
            found_and_updated = True
        
        return found_and_updated
    
    def update_env_config(self, content: str) -> str:
        """Update .env style configuration file"""
        # Add MariaDB configuration
        lines = content.split("\n")
        mariadb_config = [
            "",
            "# MariaDB Configuration",
            f"DB_HOST={self.config['mariadb']['host']}",
            f"DB_PORT={self.config['mariadb']['port']}",
            f"DB_NAME={self.config['mariadb']['database']}",
            f"DB_USER={self.config['mariadb']['user']}",
            f"DB_PASSWORD={self.config['mariadb']['password']}",
            f"MYSQL_ROOT_PASSWORD={os.environ.get('MYSQL_ROOT_PASSWORD', '')}",
            f"DATABASE_URL=mysql+pymysql://{self.config['mariadb']['user']}:{os.environ.get('DB_PASSWORD', '')}@{self.config['mariadb']['host']}:{self.config['mariadb']['port']}/{self.config['mariadb']['database']}",
            "DB_DIALECT=mysql",
            "DB_DRIVER=pymysql"
        ]
        
        # Remove any existing DB configuration
        filtered_lines = []
        skip_patterns = ["DB_", "DATABASE_URL", "MYSQL_", "SQLITE_"]
        
        for line in lines:
            skip = False
            for pattern in skip_patterns:
                if line.startswith(pattern):
                    skip = True
                    break
            
            if not skip:
                filtered_lines.append(line)
        
        # Add our new configuration
        filtered_lines.extend(mariadb_config)
        return "\n".join(filtered_lines)
    
    def update_python_config(self, content: str) -> str:
        """Update Python configuration file"""
        # This is more complex as Python config files vary greatly
        # We'll do a basic replacement for common patterns
        
        # Replace SQLite connection strings
        content = content.replace(
            "sqlite:///",
            f"mysql+pymysql://{self.config['mariadb']['user']}:{os.environ.get('DB_PASSWORD', '')}@{self.config['mariadb']['host']}:{self.config['mariadb']['port']}/{self.config['mariadb']['database']}"
        )
        
        # Replace SQLAlchemy config
        sqlite_config = "SQLALCHEMY_DATABASE_URI = 'sqlite:///"
        mariadb_config = f"SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{self.config['mariadb']['user']}:{os.environ.get('DB_PASSWORD', '')}@{self.config['mariadb']['host']}:{self.config['mariadb']['port']}/{self.config['mariadb']['database']}'"
        
        content = content.replace(sqlite_config, mariadb_config)
        
        return content
    
    def generate_env_config(self) -> str:
        """Generate new .env file content"""
        return f"""# NoxSuite Environment Configuration
# Generated by Migration Helper

# Application settings
SECRET_KEY={os.environ.get('SECRET_KEY', 'generate-a-secure-secret-key-in-production')}
DEBUG=False

# MariaDB Configuration
DB_HOST={self.config['mariadb']['host']}
DB_PORT={self.config['mariadb']['port']}
DB_NAME={self.config['mariadb']['database']}
DB_USER={self.config['mariadb']['user']}
DB_PASSWORD={self.config['mariadb']['password']}
MYSQL_ROOT_PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD", "")
DATABASE_URL=mysql+pymysql: os.environ.get("DB_PASSWORD", ""){self.config['mariadb']['host']}:{self.config['mariadb']['port']}/{self.config['mariadb']['database']}
DB_DIALECT=mysql
DB_DRIVER=pymysql

# API Settings
API_KEY={os.environ.get('API_KEY', '')}
JWT_SECRET_KEY={os.environ.get('JWT_SECRET_KEY', 'generate-a-secure-jwt-key-in-production')}
"""
    
    def migrate(self) -> bool:
        """Execute the full migration process"""
        logger.info("Starting migration from SQLite to MariaDB")
        
        # Step 1: Backup SQLite database
        backup_path = self.backup_sqlite_db()
        if not backup_path:
            logger.error("Failed to backup SQLite database. Aborting migration.")
            return False
        
        # Step 2: Start MariaDB container
        if not self.start_mariadb_container():
            logger.error("Failed to start MariaDB container. Aborting migration.")
            return False
        
        # Step 3: Generate migration schema
        schema_path = self.generate_migration_schema()
        if not schema_path:
            logger.error("Failed to generate migration schema. Aborting migration.")
            return False
        
        # Step 4: Execute migration
        if not self.execute_migration(schema_path):
            logger.error("Failed to execute migration. Aborting migration.")
            return False
        
        # Step 5: Update application configuration
        if not self.update_app_config():
            logger.warning("Failed to update application configuration. Manual configuration required.")
        
        logger.info("Migration completed successfully!")
        logger.info(f"MariaDB connection string: mysql+pymysql://{self.config['mariadb']['user']}:{os.environ.get('DB_PASSWORD', '')}@{self.config['mariadb']['host']}:{self.config['mariadb']['port']}/{self.config['mariadb']['database']}")
        logger.info("Make sure to update your application to use the MariaDB connection string and install any required dependencies (pymysql).")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="SQLite to MariaDB Migration Helper")
    parser.add_argument("--sqlite-path", help="Path to SQLite database", default=None)
    parser.add_argument("--backup-only", action="store_true", help="Only backup SQLite database")
    parser.add_argument("--schema-only", action="store_true", help="Only generate migration schema")
    parser.add_argument("--config-only", action="store_true", help="Only update application configuration")
    
    args = parser.parse_args()
    
    config = DEFAULT_CONFIG.copy()
    if args.sqlite_path:
        config["sqlite_db_path"] = args.sqlite_path
    
    migration_helper = MariaDBMigrationHelper(config)
    
    if args.backup_only:
        migration_helper.backup_sqlite_db()
    elif args.schema_only:
        migration_helper.generate_migration_schema()
    elif args.config_only:
        migration_helper.update_app_config()
    else:
        migration_helper.migrate()


if __name__ == "__main__":
    main()
