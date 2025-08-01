#!/usr/bin/env python3
"""
SQLite to MariaDB Migration
==========================
Tool to migrate the NoxSuite database from SQLite to MariaDB.

This script:
1. Reads schema and data from SQLite database
2. Creates equivalent schema in MariaDB
3. Migrates all data preserving relationships
4. Validates the migration
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

import pymysql
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    inspect,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("migration.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Add project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database models
try:
    from backend.models.user import AuditLog, Base, Role, User, UserRole, UserSession

    MODELS_IMPORTED = True
except ImportError:
    logger.warning("Could not import models, will use reflection instead")
    MODELS_IMPORTED = False
    Base = declarative_base()


def create_mysql_url(host, port, user, password, database):
    """Create MySQL connection URL"""
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def backup_mariadb_db(mariadb_path, backup_dir="./backups"):
    """Create a backup of the SQLite database"""
    import shutil
    from pathlib import Path

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"noxsuite_backup_{timestamp}.db")

    # Copy the database file
    shutil.copy2(mariadb_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    return backup_path


def inspect_mariadb_db(mariadb_url):
    """Inspect SQLite database structure"""
    engine = create_engine(mariadb_url)
    inspector = inspect(engine)

    db_structure = {}
    for table_name in inspector.get_table_names():
        columns = []
        for column in inspector.get_columns(table_name):
            columns.append(
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "default": str(column["default"]) if column["default"] else None,
                }
            )

        primary_keys = inspector.get_pk_constraint(table_name).get(
            "constrained_columns", []
        )
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            foreign_keys.append(
                {
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                    "constrained_columns": fk["constrained_columns"],
                }
            )

        db_structure[table_name] = {
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "indexes": inspector.get_indexes(table_name),
        }

    return db_structure


def setup_mariadb(mysql_url, mysql_db_name):
    """Setup MariaDB database"""
    # Create database if it doesn't exist
    engine = create_engine(mysql_url.replace(mysql_db_name, ""))
    with engine.connect() as conn:
        conn.execute(
            f"CREATE DATABASE IF NOT EXISTS {mysql_db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )

    # Connect to the database
    engine = create_engine(mysql_url)
    Base.metadata.create_all(engine)
    return engine


def migrate_data(mariadb_engine, mysql_engine, include_tables=None):
    """Migrate data from SQLite to MySQL"""
    mariadb_meta = MetaData()
    mariadb_meta.reflect(bind=mariadb_engine)

    mysql_meta = MetaData()
    mysql_meta.reflect(bind=mysql_engine)

    # Create SQLite and MySQL sessions
    mariadb_session = sessionmaker(bind=mariadb_engine)()
    mysql_session = sessionmaker(bind=mysql_engine)()

    tables = include_tables or mariadb_meta.tables.keys()

    # Process tables in dependency order
    table_order = [
        "roles",  # No dependencies
        "users",  # No dependencies
        "user_roles",  # Depends on roles and users
        "user_sessions",  # Depends on users
        "audit_logs",  # Depends on users
    ]

    # Add any tables not in the predefined order
    for table in tables:
        if table not in table_order:
            table_order.append(table)

    # Migrate each table in order
    for table_name in table_order:
        if table_name not in mariadb_meta.tables:
            logger.info(f"Table {table_name} not in SQLite database, skipping")
            continue

        if table_name not in mysql_meta.tables:
            logger.info(f"Table {table_name} not in MariaDB schema, skipping")
            continue

        # Get table objects
        mariadb_table = mariadb_meta.tables[table_name]
        mysql_table = mysql_meta.tables[table_name]

        # Count rows
        mariadb_count = mariadb_session.query(mariadb_table.c.id).count()
        logger.info(f"Migrating {mariadb_count} rows from {table_name}")

        # Get all rows from SQLite
        rows = mariadb_session.query(mariadb_table).all()

        # Insert rows into MySQL
        insert_count = 0
        for row in rows:
            # Convert row to dict
            row_dict = {
                column.name: getattr(row, column.name)
                for column in mariadb_table.columns
            }

            # Insert into MySQL
            try:
                mysql_session.execute(mysql_table.insert().values(**row_dict))
                insert_count += 1
            except Exception as e:
                logger.error(
                    f"Error inserting row {row_dict} into {table_name}: {e}")

        logger.info(f"Inserted {insert_count} rows into {table_name}")

    # Commit changes
    mysql_session.commit()

    # Close sessions
    mariadb_session.close()
    mysql_session.close()


def validate_migration(mariadb_engine, mysql_engine):
    """Validate that the migration was successful"""
    mariadb_meta = MetaData()
    mariadb_meta.reflect(bind=mariadb_engine)

    mysql_meta = MetaData()
    mysql_meta.reflect(bind=mysql_engine)

    # Create sessions
    mariadb_session = sessionmaker(bind=mariadb_engine)()
    mysql_session = sessionmaker(bind=mysql_engine)()

    validation_results = {}

    # Check each table
    for table_name in mariadb_meta.tables:
        if table_name not in mysql_meta.tables:
            validation_results[table_name] = {
                "status": "error",
                "message": "Table not found in MariaDB",
            }
            continue

        # Get table objects
        mariadb_table = mariadb_meta.tables[table_name]
        mysql_table = mysql_meta.tables[table_name]

        # Count rows
        mariadb_count = mariadb_session.query(mariadb_table.c.id).count()
        mysql_count = mysql_session.query(mysql_table.c.id).count()

        if mariadb_count != mysql_count:
            validation_results[table_name] = {
                "status": "error",
                "message": f"Row count mismatch: SQLite={mariadb_count}, MariaDB={mysql_count}",
            }
            continue

        # Sample a few rows for comparison
        mariadb_rows = mariadb_session.query(mariadb_table).limit(5).all()

        # For each row, check if it exists in MariaDB
        all_rows_match = True
        for mariadb_row in mariadb_rows:
            # Get primary key value
            pk_col = mariadb_table.primary_key.columns.values()[0].name
            pk_val = getattr(mariadb_row, pk_col)

            # Query MariaDB for the same row
            mysql_row = (
                mysql_session.query(mysql_table)
                .filter(getattr(mysql_table.c, pk_col) == pk_val)
                .first()
            )

            if not mysql_row:
                all_rows_match = False
                break

            # Compare columns
            for column in mariadb_table.columns:
                mariadb_val = getattr(mariadb_row, column.name)
                mysql_val = getattr(mysql_row, column.name)

                if mariadb_val != mysql_val:
                    all_rows_match = False
                    break

        validation_results[table_name] = {
            "status": "success" if all_rows_match else "error",
            "message": "Data matches" if all_rows_match else "Data mismatch detected",
        }

    # Close sessions
    mariadb_session.close()
    mysql_session.close()

    return validation_results


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Migrate NoxSuite database from SQLite to MariaDB"
    )
    parser.add_argument(
        "--sqlite-path",
        type=str,
        default="./database/noxsuite.db",
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--mysql-host", type=str, default="localhost", help="MariaDB host"
    )
    parser.add_argument("--mysql-port", type=int,
                        default=3306, help="MariaDB port")
    parser.add_argument("--mysql-user", type=str,
                        default="root", help="MariaDB user")
    parser.add_argument(
        "--mysql-password", type=str, default="noxsuite", help="MariaDB password"
    )
    parser.add_argument(
        "--mysql-db", type=str, default="noxsuite", help="MariaDB database name"
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup of SQLite database"
    )
    parser.add_argument("--validate", action="store_true",
                        help="Validate migration")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without actual migration",
    )

    args = parser.parse_args()

    # Create SQLite URL
    mariadb_url = f"mysql+pymysql://{args.mariadb_path}"

    # Create MySQL URL
    mysql_url = create_mysql_url(
        args.mysql_host,
        args.mysql_port,
        args.mysql_user,
        args.mysql_password,
        args.mysql_db,
    )

    logger.info(f"SQLite URL: {mariadb_url}")
    logger.info(f"MariaDB URL: {mysql_url}")

    # Backup SQLite database if requested
    if args.backup:
        backup_path = backup_mariadb_db(args.mariadb_path)
        logger.info(f"SQLite database backed up to {backup_path}")

    # Inspect SQLite database
    db_structure = inspect_mariadb_db(mariadb_url)
    logger.info(f"Found {len(db_structure)} tables in SQLite database")

    # Dry run
    if args.dry_run:
        logger.info("Dry run mode, skipping actual migration")
        for table_name, table_info in db_structure.items():
            logger.info(f"Table: {table_name}")
            logger.info(f"  Columns: {len(table_info['columns'])}")
            logger.info(f"  Primary keys: {table_info['primary_keys']}")
            logger.info(f"  Foreign keys: {len(table_info['foreign_keys'])}")
            logger.info(f"  Indexes: {len(table_info['indexes'])}")
        return

    # Setup MariaDB
    mariadb_engine = create_engine(mariadb_url)
    mysql_engine = setup_mariadb(mysql_url, args.mysql_db)

    # Migrate data
    migrate_data(mariadb_engine, mysql_engine)

    # Validate migration if requested
    if args.validate:
        logger.info("Validating migration...")
        validation_results = validate_migration(mariadb_engine, mysql_engine)

        # Print validation results
        success_count = sum(
            1 for result in validation_results.values() if result["status"] == "success"
        )
        total_count = len(validation_results)

        logger.info(
            f"Validation results: {success_count}/{total_count} tables successfully migrated"
        )

        for table_name, result in validation_results.items():
            logger.info(
                f"Table {table_name}: {result['status']} - {result['message']}")

    logger.info("Migration completed")


if __name__ == "__main__":
    main()
