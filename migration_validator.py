#!/usr/bin/env python3
"""
MariaDB Migration Validator
Validates the SQLite to MariaDB migration for NoxSuite
"""

import argparse
import logging
import os
import sqlite3
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MigrationValidator")

try:
    import pymysql
except ImportError:
    logger.error("pymysql package not found. Install with: pip install pymysql")
    sys.exit(1)


class MigrationValidator:
    """Validates the migration from SQLite to MariaDB"""
    
    def __init__(self, sqlite_path, mariadb_config):
        self.sqlite_path = sqlite_path
        self.mariadb_config = mariadb_config
        self.validation_results = {
            "tables_match": False,
            "record_counts_match": False,
            "schema_differences": [],
            "integrity_issues": [],
            "tables_checked": 0,
            "total_records_sqlite": 0,
            "total_records_mariadb": 0
        }
    
    def connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            return None
    
    def connect_mariadb(self):
        """Connect to MariaDB database"""
        try:
            conn = pymysql.connect(
                host=self.mariadb_config["host"],
                port=self.mariadb_config["port"],
                user=self.mariadb_config["user"],
                password=self.mariadb_config["password"],
                database=self.mariadb_config["database"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
        except pymysql.Error as e:
            logger.error(f"Failed to connect to MariaDB: {e}")
            return None
    
    def get_sqlite_tables(self, conn):
        """Get list of tables in SQLite database"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row["name"] for row in cursor.fetchall()]
        cursor.close()
        return tables
    
    def get_mariadb_tables(self, conn):
        """Get list of tables in MariaDB database"""
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    
    def compare_table_structures(self):
        """Compare table structures between SQLite and MariaDB"""
        sqlite_conn = self.connect_sqlite()
        mariadb_conn = self.connect_mariadb()
        
        if not sqlite_conn or not mariadb_conn:
            return
        
        sqlite_tables = self.get_sqlite_tables(sqlite_conn)
        mariadb_tables = self.get_mariadb_tables(mariadb_conn)
        
        # Compare table lists
        missing_tables = set(sqlite_tables) - set(mariadb_tables)
        extra_tables = set(mariadb_tables) - set(sqlite_tables)
        
        if missing_tables:
            logger.warning(f"Missing tables in MariaDB: {', '.join(missing_tables)}")
            self.validation_results["schema_differences"].append({
                "type": "missing_tables",
                "tables": list(missing_tables)
            })
        
        if extra_tables:
            logger.info(f"Extra tables in MariaDB: {', '.join(extra_tables)}")
            self.validation_results["schema_differences"].append({
                "type": "extra_tables",
                "tables": list(extra_tables)
            })
        
        self.validation_results["tables_match"] = not missing_tables
        
        # Compare column structures for common tables
        common_tables = set(sqlite_tables).intersection(set(mariadb_tables))
        for table in common_tables:
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            sqlite_columns = {row["name"]: row for row in sqlite_cursor.fetchall()}
            
            mariadb_cursor = mariadb_conn.cursor()
            mariadb_cursor.execute(f"DESCRIBE `{table}`")
            mariadb_columns = {row["Field"]: row for row in mariadb_cursor.fetchall()}
            
            missing_columns = set(sqlite_columns.keys()) - set(mariadb_columns.keys())
            extra_columns = set(mariadb_columns.keys()) - set(sqlite_columns.keys())
            
            if missing_columns:
                logger.warning(f"Table '{table}' is missing columns in MariaDB: {', '.join(missing_columns)}")
                self.validation_results["schema_differences"].append({
                    "type": "missing_columns",
                    "table": table,
                    "columns": list(missing_columns)
                })
            
            if extra_columns:
                logger.info(f"Table '{table}' has extra columns in MariaDB: {', '.join(extra_columns)}")
                self.validation_results["schema_differences"].append({
                    "type": "extra_columns",
                    "table": table,
                    "columns": list(extra_columns)
                })
        
        sqlite_conn.close()
        mariadb_conn.close()
    
    def compare_record_counts(self):
        """Compare record counts between SQLite and MariaDB"""
        sqlite_conn = self.connect_sqlite()
        mariadb_conn = self.connect_mariadb()
        
        if not sqlite_conn or not mariadb_conn:
            return
        
        sqlite_tables = self.get_sqlite_tables(sqlite_conn)
        mariadb_tables = self.get_mariadb_tables(mariadb_conn)
        
        common_tables = set(sqlite_tables).intersection(set(mariadb_tables))
        self.validation_results["tables_checked"] = len(common_tables)
        
        count_mismatches = []
        total_sqlite_records = 0
        total_mariadb_records = 0
        
        for table in common_tables:
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()["count"]
            total_sqlite_records += sqlite_count
            
            mariadb_cursor = mariadb_conn.cursor()
            mariadb_cursor.execute(f"SELECT COUNT(*) as count FROM `{table}`")
            mariadb_count = mariadb_cursor.fetchone()["count"]
            total_mariadb_records += mariadb_count
            
            if sqlite_count != mariadb_count:
                logger.warning(f"Record count mismatch for table '{table}': SQLite={sqlite_count}, MariaDB={mariadb_count}")
                count_mismatches.append({
                    "table": table,
                    "sqlite_count": sqlite_count,
                    "mariadb_count": mariadb_count,
                    "difference": abs(sqlite_count - mariadb_count)
                })
        
        self.validation_results["record_counts_match"] = len(count_mismatches) == 0
        self.validation_results["count_mismatches"] = count_mismatches
        self.validation_results["total_records_sqlite"] = total_sqlite_records
        self.validation_results["total_records_mariadb"] = total_mariadb_records
        
        sqlite_conn.close()
        mariadb_conn.close()
    
    def validate_data_sample(self, sample_size=5):
        """Validate a sample of data between SQLite and MariaDB"""
        sqlite_conn = self.connect_sqlite()
        mariadb_conn = self.connect_mariadb()
        
        if not sqlite_conn or not mariadb_conn:
            return
        
        sqlite_tables = self.get_sqlite_tables(sqlite_conn)
        mariadb_tables = self.get_mariadb_tables(mariadb_conn)
        
        common_tables = set(sqlite_tables).intersection(set(mariadb_tables))
        data_mismatches = []
        
        for table in common_tables:
            # Get column names for this table
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            sqlite_columns = [row["name"] for row in sqlite_cursor.fetchall()]
            
            mariadb_cursor = mariadb_conn.cursor()
            mariadb_cursor.execute(f"DESCRIBE `{table}`")
            mariadb_columns = [row["Field"] for row in mariadb_cursor.fetchall()]
            
            # Find common columns to compare
            common_columns = set(sqlite_columns).intersection(set(mariadb_columns))
            if not common_columns:
                continue
            
            # Get primary key column if available, otherwise use first column
            primary_key = None
            for col in sqlite_columns:
                sqlite_cursor.execute(f"PRAGMA table_info({table})")
                for row in sqlite_cursor.fetchall():
                    if row["name"] == col and row["pk"] == 1:
                        primary_key = col
                        break
                if primary_key:
                    break
            
            order_by = primary_key if primary_key else sqlite_columns[0]
            
            # Sample data from SQLite
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT * FROM {table} ORDER BY {order_by} LIMIT {sample_size}")
            sqlite_rows = sqlite_cursor.fetchall()
            
            for row in sqlite_rows:
                if primary_key and row[primary_key]:
                    # Look for this record in MariaDB
                    mariadb_cursor = mariadb_conn.cursor()
                    mariadb_cursor.execute(f"SELECT * FROM `{table}` WHERE `{primary_key}` = %s", (row[primary_key],))
                    mariadb_row = mariadb_cursor.fetchone()
                    
                    if not mariadb_row:
                        data_mismatches.append({
                            "table": table,
                            "type": "missing_record",
                            "primary_key": primary_key,
                            "key_value": row[primary_key]
                        })
                        continue
                    
                    # Compare values in common columns
                    for col in common_columns:
                        sqlite_value = row[col]
                        mariadb_value = mariadb_row[col]
                        
                        # Handle different types between SQLite and MariaDB
                        if isinstance(sqlite_value, (int, float)) and isinstance(mariadb_value, (int, float)):
                            if sqlite_value != mariadb_value:
                                data_mismatches.append({
                                    "table": table,
                                    "type": "value_mismatch",
                                    "primary_key": primary_key,
                                    "key_value": row[primary_key],
                                    "column": col,
                                    "sqlite_value": sqlite_value,
                                    "mariadb_value": mariadb_value
                                })
                        elif (sqlite_value is None and mariadb_value is not None) or (sqlite_value is not None and mariadb_value is None):
                            data_mismatches.append({
                                "table": table,
                                "type": "null_mismatch",
                                "primary_key": primary_key,
                                "key_value": row[primary_key],
                                "column": col,
                                "sqlite_value": sqlite_value,
                                "mariadb_value": mariadb_value
                            })
                        elif isinstance(sqlite_value, str) and isinstance(mariadb_value, str):
                            # Normalize strings for comparison
                            sqlite_str = sqlite_value.strip()
                            mariadb_str = mariadb_value.strip()
                            if sqlite_str != mariadb_str:
                                data_mismatches.append({
                                    "table": table,
                                    "type": "string_mismatch",
                                    "primary_key": primary_key,
                                    "key_value": row[primary_key],
                                    "column": col,
                                    "sqlite_value": sqlite_value,
                                    "mariadb_value": mariadb_value
                                })
        
        self.validation_results["data_sample_mismatches"] = data_mismatches
        
        sqlite_conn.close()
        mariadb_conn.close()
    
    def check_mariadb_configuration(self):
        """Check MariaDB configuration for optimization opportunities"""
        mariadb_conn = self.connect_mariadb()
        if not mariadb_conn:
            return
        
        optimization_suggestions = []
        
        cursor = mariadb_conn.cursor()
        
        # Check table engines
        cursor.execute("""
            SELECT table_name, engine
            FROM information_schema.tables
            WHERE table_schema = %s AND engine != 'InnoDB'
        """, (self.mariadb_config["database"],))
        
        non_innodb_tables = cursor.fetchall()
        if non_innodb_tables:
            table_names = [row["table_name"] for row in non_innodb_tables]
            optimization_suggestions.append({
                "type": "non_innodb_tables",
                "description": "These tables should be converted to InnoDB for better performance and reliability",
                "tables": table_names
            })
        
        # Check for missing indexes on primary key fields
        cursor.execute("""
            SELECT t.table_name, c.column_name
            FROM information_schema.tables t
            JOIN information_schema.columns c ON t.table_name = c.table_name AND t.table_schema = c.table_schema
            LEFT JOIN information_schema.statistics s ON t.table_name = s.table_name AND t.table_schema = s.table_schema AND c.column_name = s.column_name
            WHERE t.table_schema = %s
            AND c.column_name = 'id'
            AND s.index_name IS NULL
        """, (self.mariadb_config["database"],))
        
        tables_without_pk_index = cursor.fetchall()
        if tables_without_pk_index:
            table_names = [row["table_name"] for row in tables_without_pk_index]
            optimization_suggestions.append({
                "type": "missing_pk_indexes",
                "description": "These tables have an 'id' column without an index",
                "tables": table_names
            })
        
        # Check for missing indexes on common foreign key columns
        common_fk_columns = ["user_id", "account_id", "organization_id", "group_id", "parent_id"]
        for fk_column in common_fk_columns:
            cursor.execute("""
                SELECT c.table_name, c.column_name
                FROM information_schema.columns c
                LEFT JOIN information_schema.statistics s ON c.table_name = s.table_name 
                    AND c.table_schema = s.table_schema 
                    AND c.column_name = s.column_name
                WHERE c.table_schema = %s
                AND c.column_name = %s
                AND s.index_name IS NULL
            """, (self.mariadb_config["database"], fk_column))
            
            tables_without_fk_index = cursor.fetchall()
            if tables_without_fk_index:
                table_names = [row["table_name"] for row in tables_without_fk_index]
                optimization_suggestions.append({
                    "type": f"missing_{fk_column}_indexes",
                    "description": f"These tables have '{fk_column}' column without an index",
                    "tables": table_names
                })
        
        # Check character sets and collations
        cursor.execute("""
            SELECT table_name, character_set_name, collation_name
            FROM information_schema.tables
            WHERE table_schema = %s
            AND (character_set_name != 'utf8mb4' OR collation_name != 'utf8mb4_unicode_ci')
            AND character_set_name IS NOT NULL
        """, (self.mariadb_config["database"],))
        
        non_utf8mb4_tables = cursor.fetchall()
        if non_utf8mb4_tables:
            table_names = [row["table_name"] for row in non_utf8mb4_tables]
            optimization_suggestions.append({
                "type": "non_utf8mb4_tables",
                "description": "These tables should use utf8mb4 character set for better Unicode support",
                "tables": table_names
            })
        
        mariadb_conn.close()
        
        self.validation_results["optimization_suggestions"] = optimization_suggestions
    
    def run_validation(self):
        """Run all validation checks"""
        logger.info("Starting migration validation")
        
        # Check connections
        sqlite_conn = self.connect_sqlite()
        if not sqlite_conn:
            return self.validation_results
        sqlite_conn.close()
        
        mariadb_conn = self.connect_mariadb()
        if not mariadb_conn:
            return self.validation_results
        mariadb_conn.close()
        
        # Run validation steps
        logger.info("Comparing table structures...")
        self.compare_table_structures()
        
        logger.info("Comparing record counts...")
        self.compare_record_counts()
        
        logger.info("Validating data samples...")
        self.validate_data_sample()
        
        logger.info("Checking MariaDB configuration...")
        self.check_mariadb_configuration()
        
        return self.validation_results
    
    def print_validation_report(self):
        """Print a validation report"""
        print("\n" + "=" * 60)
        print(" MIGRATION VALIDATION REPORT ")
        print("=" * 60)
        
        # Tables comparison
        print(f"\n## TABLE STRUCTURE")
        if self.validation_results["tables_match"]:
            print("✅ All SQLite tables exist in MariaDB")
        else:
            print("❌ Some SQLite tables are missing in MariaDB")
            for diff in self.validation_results["schema_differences"]:
                if diff["type"] == "missing_tables":
                    print(f"   Missing tables: {', '.join(diff['tables'])}")
        
        # Record counts
        print(f"\n## RECORD COUNTS")
        if self.validation_results["record_counts_match"]:
            print("✅ All tables have matching record counts")
        else:
            print("❌ Record count mismatches found:")
            for mismatch in self.validation_results["count_mismatches"]:
                print(f"   Table '{mismatch['table']}': SQLite={mismatch['sqlite_count']}, MariaDB={mismatch['mariadb_count']}, Difference={mismatch['difference']}")
        
        print(f"\n   Total records in SQLite: {self.validation_results['total_records_sqlite']}")
        print(f"   Total records in MariaDB: {self.validation_results['total_records_mariadb']}")
        
        # Data sample validation
        print(f"\n## DATA SAMPLE VALIDATION")
        data_mismatches = self.validation_results.get("data_sample_mismatches", [])
        if not data_mismatches:
            print("✅ No data mismatches found in samples")
        else:
            print(f"❌ Found {len(data_mismatches)} data mismatches in samples")
            mismatches_by_table = {}
            for mismatch in data_mismatches:
                table = mismatch["table"]
                if table not in mismatches_by_table:
                    mismatches_by_table[table] = {"missing": 0, "value": 0, "null": 0, "string": 0}
                
                mismatches_by_table[table][mismatch["type"].split("_")[0]] += 1
            
            for table, counts in mismatches_by_table.items():
                print(f"   Table '{table}': {counts['missing']} missing records, {counts['value'] + counts['null'] + counts['string']} value mismatches")
        
        # Optimization suggestions
        print(f"\n## OPTIMIZATION SUGGESTIONS")
        optimization_suggestions = self.validation_results.get("optimization_suggestions", [])
        if not optimization_suggestions:
            print("✅ No optimization suggestions")
        else:
            print(f"ℹ️ {len(optimization_suggestions)} optimization suggestions:")
            for suggestion in optimization_suggestions:
                print(f"   - {suggestion['description']}")
                if len(suggestion['tables']) <= 5:
                    print(f"     Affected tables: {', '.join(suggestion['tables'])}")
                else:
                    print(f"     Affected tables: {len(suggestion['tables'])} tables")
        
        # Overall status
        print("\n## OVERALL STATUS")
        if (self.validation_results["tables_match"] and 
            self.validation_results["record_counts_match"] and 
            not data_mismatches):
            print("✅ VALIDATION PASSED - Migration appears successful")
        else:
            print("⚠️ VALIDATION WARNING - Issues found that need attention")
        
        print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Validate SQLite to MariaDB Migration")
    parser.add_argument("--sqlite-path", required=True, help="Path to SQLite database")
    parser.add_argument("--host", default="localhost", help="MariaDB host")
    parser.add_argument("--port", type=int, default=3306, help="MariaDB port")
    parser.add_argument("--user", default="root", help="MariaDB user")
    parser.add_argument("--password", help="MariaDB password")
    parser.add_argument("--database", required=True, help="MariaDB database name")
    
    args = parser.parse_args()
    
    # Use environment variables for passwords if not provided
    if not args.password:
        args.password = os.environ.get("DB_PASSWORD", "")
        if not args.password and args.user == "root":
            args.password = os.environ.get("MYSQL_ROOT_PASSWORD", "")
    
    mariadb_config = {
        "host": args.host,
        "port": args.port,
        "user": args.user,
        "password": args.password,
        "database": args.database
    }
    
    validator = MigrationValidator(args.sqlite_path, mariadb_config)
    validator.run_validation()
    validator.print_validation_report()


if __name__ == "__main__":
    main()
