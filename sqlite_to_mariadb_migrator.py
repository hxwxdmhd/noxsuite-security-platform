#!/usr/bin/env python3
"""
Emergency SQLite to MariaDB Migration Tool
==========================================
Extracts data from SQLite databases and migrates to MariaDB-compatible format
"""

import json
import logging
import os
from datetime import datetime

import pymysql

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLiteToMariaDBMigrator:
    """Complete migration from SQLite to MariaDB"""

    def __init__(self):
        self.mariadb_files = [
            "mariadb_dev_simulation.db",
            "archived/sqlite/noxsuite_auth.db",
            "archived/sqlite/noxsuite.db",
            "archived/sqlite/unified_heimnetz.db",
            "database/noxsuite.db",
        ]
        self.migration_report = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "tables_migrated": 0,
            "rows_exported": 0,
            "errors": [],
        }

    def export_mariadb_schema(self, db_path):
        """Export SQLite schema and data"""
        if not os.path.exists(db_path):
            logger.warning(f"Database not found: {db_path}")
            return None

        try:
            conn = pymysql.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get all table names
            cursor.execute(
                "SELECT name FROM mariadb_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            export_data = {"database": db_path, "tables": {}, "schema": {}}

            for table in tables:
                logger.info(f"Exporting table: {table} from {db_path}")

                # Get table schema
                cursor.execute(f"PRAGMA table_info({table})")
                schema = [dict(row) for row in cursor.fetchall()]
                export_data["schema"][table] = schema

                # Get table data
                cursor.execute(f"SELECT * FROM {table}")
                rows = [dict(row) for row in cursor.fetchall()]
                export_data["tables"][table] = rows

                self.migration_report["rows_exported"] += len(rows)
                logger.info(f"Exported {len(rows)} rows from {table}")

            conn.close()
            self.migration_report["files_processed"] += 1
            self.migration_report["tables_migrated"] += len(tables)

            return export_data

        except Exception as e:
            error_msg = f"Export failed for {db_path}: {e}"
            self.migration_report["errors"].append(error_msg)
            logger.error(error_msg)
            return None

    def generate_mariadb_insert_sql(self, export_data):
        """Generate MariaDB-compatible INSERT statements"""
        sql_statements = []

        for table_name, rows in export_data["tables"].items():
            if not rows:
                continue

            # Generate INSERT statements
            for row in rows:
                columns = list(row.keys())
                values = []

                for value in row.values():
                    if value is None:
                        values.append("NULL")
                    elif isinstance(value, str):
                        # Escape quotes for SQL
                        escaped = value.replace("'", "''")
                        values.append(f"'{escaped}'")
                    elif isinstance(value, (dict, list)):
                        # JSON columns
                        json_str = json.dumps(value).replace("'", "''")
                        values.append(f"'{json_str}'")
                    else:
                        values.append(str(value))

                columns_str = ", ".join(columns)
                values_str = ", ".join(values)

                sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"
                sql_statements.append(sql)

        return sql_statements

    def run_migration(self):
        """Execute complete migration"""
        logger.info("🔄 Starting SQLite to MariaDB migration...")

        all_exports = []
        migration_sql = []

        for db_file in self.mariadb_files:
            logger.info(f"Processing: {db_file}")
            export_data = self.export_mariadb_schema(db_file)

            if export_data:
                all_exports.append(export_data)
                sql_statements = self.generate_mariadb_insert_sql(export_data)
                migration_sql.extend(sql_statements)

        # Save migration artifacts
        with open("mariadb_migration_export.json", "w") as f:
            json.dump(all_exports, f, indent=2, default=str)

        with open("mariadb_migration.sql", "w") as f:
            f.write("-- SQLite to MariaDB Migration SQL\n")
            f.write(f"-- Generated: {datetime.now()}\n")
            f.write("-- USE noxsuite_production;\n\n")
            f.write("\n".join(migration_sql))

        # Save migration report
        with open("migration_report.json", "w") as f:
            json.dump(self.migration_report, f, indent=2)

        logger.info("✅ Migration export completed")
        logger.info(
            f"Files processed: {self.migration_report['files_processed']}")
        logger.info(
            f"Tables migrated: {self.migration_report['tables_migrated']}")
        logger.info(f"Rows exported: {self.migration_report['rows_exported']}")

        if self.migration_report["errors"]:
            logger.warning(
                f"Errors encountered: {len(self.migration_report['errors'])}"
            )
            for error in self.migration_report["errors"]:
                logger.error(f"  - {error}")

        return self.migration_report


if __name__ == "__main__":
    migrator = SQLiteToMariaDBMigrator()
    report = migrator.run_migration()

    print("🎯 MIGRATION SUMMARY")
    print(f"✅ Files processed: {report['files_processed']}")
    print(f"✅ Tables migrated: {report['tables_migrated']}")
    print(f"✅ Rows exported: {report['rows_exported']}")
    print(f"❌ Errors: {len(report['errors'])}")
