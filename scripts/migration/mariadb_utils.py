#!/usr/bin/env python3
"""
MariaDB Database Utility Script
Provides helper functions for MariaDB operations in NoxSuite
"""
import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MariaDBUtils")

try:
    import pymysql
except ImportError:
    logger.error("pymysql package not found. Install with: pip install pymysql")
    sys.exit(1)

class MariaDBUtils:
    """Utility functions for MariaDB database operations"""
    
    def __init__(self, config):
        self.config = config

    def connect(self):
        """Connect to MariaDB"""
        try:
            conn = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
        except pymysql.Error as e:
            logger.error(f"Failed to connect to MariaDB: {e}")
            return None

    def execute_sql_file(self, sql_file):
        """Execute SQL commands from a file"""
        if not Path(sql_file).exists():
            logger.error(f"SQL file not found: {sql_file}")
            return False
            
        try:
            if self.config.get("use_container"):
                # Run using docker exec
                container_name = self.config.get("container_name", "noxsuite-mariadb")
                cmd = [
                    "docker", "exec", "-i", container_name,
                    "mysql",
                    f"-u{self.config['user']}",
                    f"-p{os.environ.get('DB_PASSWORD', '')}",
                    self.config["database"]
                ]
                
                with open(sql_file, 'r') as f:
                    sql_content = f.read()
                
                process = subprocess.run(
                    cmd,
                    input=sql_content,
                    text=True,
                    capture_output=True
                )
                
                if process.returncode != 0:
                    logger.error(f"Error executing SQL: {process.stderr}")
                    return False
                    
                logger.info(f"SQL executed successfully via Docker container")
                return True
            else:
                # Execute using PyMySQL
                conn = self.connect()
                if not conn:
                    return False
                    
                with open(sql_file, 'r') as f:
                    sql_content = f.read()
                
                # Split SQL by semicolons but handle quoted semicolons correctly
                statements = []
                current_statement = ''
                in_quotes = False
                quote_char = None
                
                for char in sql_content:
                    if char in ("'", '"') and (not in_quotes or quote_char == char):
                        in_quotes = not in_quotes
                        if in_quotes:
                            quote_char = char
                        else:
                            quote_char = None
                            
                    current_statement += char
                    
                    if char == ';' and not in_quotes and current_statement.strip():
                        statements.append(current_statement.strip())
                        current_statement = ''
                
                if current_statement.strip():
                    statements.append(current_statement.strip())
                
                # Execute each statement
                cursor = conn.cursor()
                for i, statement in enumerate(statements):
                    try:
                        if statement.strip():
                            cursor.execute(statement)
                            conn.commit()
                    except pymysql.Error as e:
                        logger.error(f"Error executing statement {i+1}: {e}")
                        logger.error(f"Statement: {statement[:100]}...")
                        conn.rollback()
                        return False
                
                conn.close()
                logger.info(f"SQL executed successfully via PyMySQL")
                return True
                
        except Exception as e:
            logger.error(f"Error executing SQL file: {e}")
            return False

    def backup_database(self, output_file):
        """Backup MariaDB database"""
        if self.config.get("use_container"):
            container_name = self.config.get("container_name", "noxsuite-mariadb")
            backup_path = os.path.abspath(output_file)
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            cmd = [
                "docker", "exec", container_name,
                "mysqldump",
                f"-u{self.config['user']}",
                f"-p{os.environ.get('DB_PASSWORD', '')}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                self.config["database"]
            ]
            
            try:
                with open(backup_path, 'w') as f:
                    process = subprocess.run(
                        cmd,
                        stdout=f,
                        text=True,
                        check=True
                    )
                
                logger.info(f"Database backup completed successfully: {backup_path}")
                return True
            except subprocess.SubprocessError as e:
                logger.error(f"Error backing up database: {e}")
                return False
        else:
            logger.error("Backup without container not implemented yet")
            return False

    def restore_database(self, input_file):
        """Restore MariaDB database from backup"""
        if not os.path.exists(input_file):
            logger.error(f"Backup file not found: {input_file}")
            return False
            
        if self.config.get("use_container"):
            container_name = self.config.get("container_name", "noxsuite-mariadb")
            backup_path = os.path.abspath(input_file)
            
            cmd = [
                "docker", "exec", "-i", container_name,
                "mysql",
                f"-u{self.config['user']}",
                f"-p{os.environ.get('DB_PASSWORD', '')}",
                self.config["database"]
            ]
            
            try:
                with open(backup_path, 'r') as f:
                    process = subprocess.run(
                        cmd,
                        stdin=f,
                        text=True,
                        check=True
                    )
                
                logger.info(f"Database restored successfully from {backup_path}")
                return True
            except subprocess.SubprocessError as e:
                logger.error(f"Error restoring database: {e}")
                return False
        else:
            logger.error("Restore without container not implemented yet")
            return False

    def optimize_database(self):
        """Optimize MariaDB database tables"""
        conn = self.connect()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SHOW TABLES")
            tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
            
            # Analyze and optimize each table
            for table in tables:
                logger.info(f"Optimizing table: {table}")
                cursor.execute(f"ANALYZE TABLE `{table}`")
                cursor.execute(f"OPTIMIZE TABLE `{table}`")
            
            conn.close()
            logger.info("Database optimization complete")
            return True
        except pymysql.Error as e:
            logger.error(f"Error optimizing database: {e}")
            if conn:
                conn.close()
            return False

    def check_indexes(self):
        """Check for missing indexes on important columns"""
        conn = self.connect()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # Common columns that should have indexes
            common_columns = ['id', 'user_id', 'created_at', 'updated_at', 'status']
            
            # Get tables
            cursor.execute("SHOW TABLES")
            tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
            
            missing_indexes = []
            for table in tables:
                # Get columns
                cursor.execute(f"DESCRIBE `{table}`")
                columns = [row['Field'] for row in cursor.fetchall()]
                
                # Get existing indexes
                cursor.execute(f"SHOW INDEX FROM `{table}`")
                indexed_columns = [row['Column_name'] for row in cursor.fetchall()]
                
                for col in common_columns:
                    if col in columns and col not in indexed_columns:
                        missing_indexes.append((table, col))
            
            if missing_indexes:
                logger.info(f"Found {len(missing_indexes)} missing indexes:")
                for table, col in missing_indexes:
                    logger.info(f"  - Table `{table}` column `{col}`")
                    logger.info(
                        f"    Add with: ALTER TABLE `{table}` ADD INDEX "
                        f"idx_{table}_{col} (`{col}`);"
                    )
            else:
                logger.info("No missing indexes found on common columns")
            
            conn.close()
            return True
        except pymysql.Error as e:
            logger.error(f"Error checking indexes: {e}")
            if conn:
                conn.close()
            return False

    def create_database_report(self, output_file):
        """Create a comprehensive database report"""
        conn = self.connect()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            report = []
            report.append("# MariaDB Database Report")
            report.append(f"## Database: {self.config['database']}")
            report.append("")
            
            # Database info
            cursor.execute("SELECT VERSION() as version")
            version = cursor.fetchone()['version']
            report.append(f"MariaDB Version: {version}")
            report.append("")
            
            # Table statistics
            cursor.execute("""
                SELECT
                    table_name,
                    engine,
                    table_rows,
                    data_length,
                    index_length,
                    ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY (data_length + index_length) DESC
            """, (self.config['database'],))
            tables = cursor.fetchall()
            
            report.append("## Table Statistics")
            report.append("")
            report.append("| Table | Engine | Rows | Size (MB) |")
            report.append("|-------|--------|------|-----------|")
            for table in tables:
                report.append(
                    f"| {table['table_name']} | {table['engine']} | "
                    f"{table['table_rows']} | {table['size_mb']} |"
                )
            report.append("")
            
            # Non-InnoDB tables
            non_innodb = [t for t in tables if t['engine'] != 'InnoDB']
            if non_innodb:
                report.append("## Non-InnoDB Tables")
                report.append("")
                report.append(
                    "These tables should be converted to InnoDB for better "
                    "performance and reliability:"
                )
                report.append("")
                for table in non_innodb:
                    report.append(f"- {table['table_name']} (current engine: {table['engine']})")
                report.append("")
            
            # Missing primary keys
            cursor.execute("""
                SELECT
                    t.table_name
                FROM information_schema.tables t
                LEFT JOIN information_schema.table_constraints tc
                    ON t.table_name = tc.table_name 
                    AND t.table_schema = tc.table_schema
                    AND tc.constraint_type = 'PRIMARY KEY'
                WHERE t.table_schema = %s
                AND tc.constraint_name IS NULL
                AND t.table_type = 'BASE TABLE'
            """, (self.config['database'],))
            tables_without_pk = cursor.fetchall()
            
            if tables_without_pk:
                report.append("## Tables Without Primary Keys")
                report.append("")
                report.append("These tables have no primary key defined:")
                report.append("")
                for table in tables_without_pk:
                    report.append(f"- {table['table_name']}")
                report.append("")
            
            # Write report to file
            with open(output_file, 'w') as f:
                f.write('\n'.join(report))
            
            logger.info(f"Database report created at {output_file}")
            conn.close()
            return True
        except pymysql.Error as e:
            logger.error(f"Error creating database report: {e}")
            if conn:
                conn.close()
            return False


def main():
    parser = argparse.ArgumentParser(description="MariaDB Database Utility")
    parser.add_argument("--host", default="localhost", help="MariaDB host")
    parser.add_argument("--port", type=int, default=3306, help="MariaDB port")
    parser.add_argument("--user", default="root", help="MariaDB user")
    parser.add_argument("--password", help="MariaDB password")
    parser.add_argument("--database", required=True, help="MariaDB database name")
    parser.add_argument("--container", default="noxsuite-mariadb", 
                       help="Docker container name")
    parser.add_argument("--use-container", action="store_true", 
                       help="Use Docker container for commands")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Execute SQL file
    execute_parser = subparsers.add_parser("execute", help="Execute SQL file")
    execute_parser.add_argument("sql_file", help="SQL file to execute")
    
    # Backup database
    backup_parser = subparsers.add_parser("backup", help="Backup database")
    backup_parser.add_argument("output_file", help="Output file for backup")
    
    # Restore database
    restore_parser = subparsers.add_parser("restore", help="Restore database from backup")
    restore_parser.add_argument("input_file", help="Input backup file")
    
    # Optimize database
    optimize_parser = subparsers.add_parser("optimize", help="Optimize database tables")
    
    # Check indexes
    check_parser = subparsers.add_parser("check", help="Check database indexes")
    
    # Create report
    report_parser = subparsers.add_parser("report", help="Create database report")
    report_parser.add_argument("output_file", help="Output file for report")
    
    args = parser.parse_args()
    
    # Use environment variables for passwords if not provided
    if not args.password:
        args.password = os.environ.get("DB_PASSWORD", "")
        if not args.password and args.user == "root":
            args.password = os.environ.get("MYSQL_ROOT_PASSWORD", "")
    
    if not args.password:
        args.password = input("Enter MariaDB password: ")
    
    # Create config
    config = {
        "host": args.host,
        "port": args.port,
        "user": args.user,
        "password": args.password,
        "database": args.database,
        "use_container": args.use_container,
        "container_name": args.container
    }
    
    # Create utility object
    db_utils = MariaDBUtils(config)
    
    # Execute command
    if args.command == "execute":
        db_utils.execute_sql_file(args.sql_file)
    elif args.command == "backup":
        db_utils.backup_database(args.output_file)
    elif args.command == "restore":
        db_utils.restore_database(args.input_file)
    elif args.command == "optimize":
        db_utils.optimize_database()
    elif args.command == "check":
        db_utils.check_indexes()
    elif args.command == "report":
        db_utils.create_database_report(args.output_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
