# NoxSuite Database Migration Guide
## SQLite to MariaDB Migration

This guide outlines the process for migrating the NoxSuite database from SQLite to MariaDB.

## Prerequisites

Before beginning the migration, ensure you have the following:

- Docker installed and running
- Python 3.8 or higher
- SQLite database file (typically located at `data/noxsuite.db`)
- Administrative access to your system

## Migration Tools

This package includes the following migration tools:

1. **mariadb_migration_helper.py** - The main migration script that handles:
   - Setting up a MariaDB container
   - Converting SQLite schema to MariaDB
   - Migrating data between databases
   - Updating application configuration

2. **migration_validator.py** - Validates the migration:
   - Compares table structures
   - Verifies record counts match
   - Validates data samples
   - Provides optimization suggestions

3. **setup_mariadb.sh** / **setup_mariadb.ps1** - Platform-specific scripts for:
   - Setting up MariaDB in Docker
   - Creating necessary configuration files
   - Installing required Python dependencies

4. **SQL scripts**:
   - `scripts/migration/validate_migration.sql` - SQL queries for validating migration integrity

## Migration Process

### Step 1: Environment Setup

First, set up your MariaDB environment:

#### On Linux/macOS:
```bash
# Make the script executable
chmod +x scripts/migration/setup_mariadb.sh

# Run the setup script
./scripts/migration/setup_mariadb.sh
```

#### On Windows:
```powershell
# Run the PowerShell setup script
.\scripts\migration\setup_mariadb.ps1
```

The setup script will:
- Create a Docker container running MariaDB
- Configure database users and permissions
- Install required Python packages
- Create initial configuration files

### Step 2: Run the Migration Helper

```bash
# Run the migration helper
python mariadb_migration_helper.py
```

Options:
- `--sqlite-path`: Path to the SQLite database (default: `data/noxsuite.db`)
- `--backup-only`: Only backup the SQLite database
- `--schema-only`: Only generate the migration schema
- `--config-only`: Only update application configuration

### Step 3: Validate the Migration

```bash
# Validate the migration
python migration_validator.py --sqlite-path data/noxsuite.db --database noxsuite_db
```

### Step 4: Manual SQL Validation (Optional)

For advanced validation, you can use the provided SQL script:

```bash
# Connect to the MariaDB container
docker exec -it noxsuite-mariadb mysql -u root -p

# Once connected, run:
mysql> source /path/to/scripts/migration/validate_migration.sql
```

## Configuration

The migration creates the following configuration files:

1. `.env` - Contains database connection details
2. `.env.example` - Example configuration file
3. `config/database.py` - Python configuration for SQLAlchemy

## Troubleshooting

### Common Issues

#### Connection Refused
```
ERROR: Failed to connect to MariaDB. Check credentials and try again.
```

**Solution**: Ensure Docker is running and the MariaDB container is active:
```bash
docker ps | grep noxsuite-mariadb
```

#### Migration Schema Errors
```
ERROR: Failed to generate migration schema
```

**Solution**: Check your SQLite database integrity:
```bash
sqlite3 data/noxsuite.db "PRAGMA integrity_check;"
```

#### Data Validation Issues
```
WARNING: Record count mismatches found
```

**Solution**: Use the validation script to identify specific tables with issues and run targeted fixes.

## After Migration

After successfully migrating:

1. Update your application code to use MariaDB connection strings
2. Install PyMySQL if not already installed: `pip install pymysql`
3. Test your application thoroughly with the new database
4. Consider backing up and archiving your SQLite database

## Need Help?

If you encounter issues with the migration:

1. Check the logs generated during migration
2. Review the validation results for specific issues
3. Contact the NoxSuite support team with details of the issue

## License

This migration toolkit is licensed under the same terms as the NoxSuite application.
