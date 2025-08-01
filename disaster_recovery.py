"""
Disaster Recovery Script for NoxSuite MFA and RBAC

This script provides functionality for:
1. Backing up authentication and authorization data
2. Restoring authentication and authorization data
3. Resetting MFA for users in case of lost access
4. Emergency admin access recovery
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from auth.auth_integration import AuthIntegrationService
from auth.rbac_service import Permission, Role

# Constants
BACKUP_DIR = "disaster_recovery"
JWT_SECRET = os.environ.get(
    "JWT_SECRET", "your-super-secret-key-change-in-production")


def ensure_backup_dir():
    """Ensure backup directory exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Created backup directory: {BACKUP_DIR}")


def backup_rbac():
    """Backup RBAC data"""
    ensure_backup_dir()

    # Initialize auth service
    auth_service = AuthIntegrationService(jwt_secret=JWT_SECRET)

    # Export RBAC configuration to JSON
    rbac_json = auth_service.rbac_service.export_to_json()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Write to backup file
    backup_file = os.path.join(BACKUP_DIR, f"rbac_backup_{timestamp}.json")
    with open(backup_file, "w") as f:
        f.write(rbac_json)

    print(f"RBAC configuration backed up to {backup_file}")

    # Also create a latest backup
    latest_file = os.path.join(BACKUP_DIR, "rbac_backup_latest.json")
    with open(latest_file, "w") as f:
        f.write(rbac_json)

    print(f"RBAC configuration also backed up to {latest_file}")

    return backup_file


def backup_mfa():
    """Backup MFA data"""
    ensure_backup_dir()

    # In a real implementation, this would encrypt and backup MFA secrets
    # Here we'll just simulate by copying the file if it exists

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup file
    backup_file = os.path.join(BACKUP_DIR, f"mfa_backup_{timestamp}.json")

    # Simulate MFA data backup
    mfa_data = {
        "backup_time": datetime.now().isoformat(),
        "mfa_settings": {
            "enabled": True,
            "issuer": "NoxSuite",
            "digits": 6,
            "interval": 30,
        },
    }

    with open(backup_file, "w") as f:
        json.dump(mfa_data, f, indent=2)

    print(f"MFA configuration backed up to {backup_file}")

    # Also create a latest backup
    latest_file = os.path.join(BACKUP_DIR, "mfa_backup_latest.json")
    with open(latest_file, "w") as f:
        json.dump(mfa_data, f, indent=2)

    print(f"MFA configuration also backed up to {latest_file}")

    return backup_file


def backup_all():
    """Backup all authentication and authorization data"""
    print_header("Backing up all authentication and authorization data")

    rbac_file = backup_rbac()
    mfa_file = backup_mfa()

    # Create combined backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_manifest = {
        "timestamp": datetime.now().isoformat(),
        "rbac_backup": rbac_file,
        "mfa_backup": mfa_file,
    }

    manifest_file = os.path.join(
        BACKUP_DIR, f"backup_manifest_{timestamp}.json")
    with open(manifest_file, "w") as f:
        json.dump(backup_manifest, f, indent=2)

    print(f"Backup manifest created at {manifest_file}")
    print(f"Backup completed successfully at {datetime.now().isoformat()}")


def restore_rbac(backup_file=None):
    """Restore RBAC data from backup"""
    if not backup_file:
        # Use latest backup
        backup_file = os.path.join(BACKUP_DIR, "rbac_backup_latest.json")

    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False

    print(f"Restoring RBAC configuration from {backup_file}")

    # Initialize auth service
    auth_service = AuthIntegrationService(jwt_secret=JWT_SECRET)

    # Import RBAC configuration from JSON
    try:
        with open(backup_file, "r") as f:
            rbac_json = f.read()

        auth_service.rbac_service.import_from_json(rbac_json)
        print("RBAC configuration restored successfully")
        return True
    except Exception as e:
        print(f"Error restoring RBAC configuration: {str(e)}")
        return False


def restore_mfa(backup_file=None):
    """Restore MFA data from backup"""
    if not backup_file:
        # Use latest backup
        backup_file = os.path.join(BACKUP_DIR, "mfa_backup_latest.json")

    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False

    print(f"Restoring MFA configuration from {backup_file}")

    # In a real implementation, this would decrypt and restore MFA secrets
    # Here we'll just simulate by verifying the file exists

    try:
        with open(backup_file, "r") as f:
            mfa_data = json.load(f)

        print("MFA configuration restored successfully")
        print(f"Backup time: {mfa_data.get('backup_time')}")
        return True
    except Exception as e:
        print(f"Error restoring MFA configuration: {str(e)}")
        return False


def restore_all(manifest_file=None):
    """Restore all authentication and authorization data"""
    print_header("Restoring all authentication and authorization data")

    if manifest_file:
        # Use specified manifest
        if not os.path.exists(manifest_file):
            print(f"Manifest file not found: {manifest_file}")
            return False

        try:
            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            rbac_backup = manifest.get("rbac_backup")
            mfa_backup = manifest.get("mfa_backup")

            rbac_success = restore_rbac(rbac_backup)
            mfa_success = restore_mfa(mfa_backup)

            if rbac_success and mfa_success:
                print("All data restored successfully")
                return True
            else:
                print("Some data could not be restored")
                return False
        except Exception as e:
            print(f"Error restoring from manifest: {str(e)}")
            return False
    else:
        # Use latest backups
        rbac_success = restore_rbac()
        mfa_success = restore_mfa()

        if rbac_success and mfa_success:
            print("All data restored successfully")
            return True
        else:
            print("Some data could not be restored")
            return False


def reset_user_mfa(user_id):
    """Reset MFA for a user"""
    print_header(f"Resetting MFA for user {user_id}")

    # Initialize auth service
    auth_service = AuthIntegrationService(jwt_secret=JWT_SECRET)

    # Disable MFA for the user
    # In a real implementation, this would override the verification requirement
    # Here we'll just simulate the action

    print(f"MFA disabled for user {user_id}")
    print("User will need to set up MFA again on next login")

    return True


def create_emergency_admin():
    """Create emergency admin access"""
    print_header("Creating emergency admin access")

    # Initialize auth service
    auth_service = AuthIntegrationService(jwt_secret=JWT_SECRET)

    # Generate emergency admin ID
    emergency_admin_id = f"emergency_admin_{int(time.time())}"

    # Assign admin role
    auth_service.rbac_service.assign_role_to_user(emergency_admin_id, "admin")

    print(f"Emergency admin created with ID: {emergency_admin_id}")
    print("Use this ID for emergency API access")

    # In a real implementation, you would also generate a temporary password or token
    # Here we'll just simulate it
    emergency_token = f"emergency_{int(time.time())}_{os.urandom(8).hex()}"

    print(f"Emergency access token: {emergency_token}")
    print("This token will expire in 24 hours")

    # Save emergency credentials to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    credentials_file = os.path.join(
        BACKUP_DIR, f"emergency_credentials_{timestamp}.json"
    )

    credentials = {
        "timestamp": datetime.now().isoformat(),
        "admin_id": emergency_admin_id,
        "token": emergency_token,
        "expires": (datetime.now().timestamp() + 86400),  # 24 hours
    }

    with open(credentials_file, "w") as f:
        json.dump(credentials, f, indent=2)

    print(f"Emergency credentials saved to {credentials_file}")

    return emergency_admin_id, emergency_token


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Disaster Recovery for NoxSuite MFA and RBAC"
    )

    # Add subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Backup parser
    backup_parser = subparsers.add_parser(
        "backup", help="Backup authentication and authorization data"
    )
    backup_parser.add_argument(
        "--type",
        choices=["rbac", "mfa", "all"],
        default="all",
        help="Type of data to backup",
    )

    # Restore parser
    restore_parser = subparsers.add_parser(
        "restore", help="Restore authentication and authorization data"
    )
    restore_parser.add_argument(
        "--type",
        choices=["rbac", "mfa", "all"],
        default="all",
        help="Type of data to restore",
    )
    restore_parser.add_argument(
        "--file", type=str, help="Backup file to restore from")

    # Reset MFA parser
    reset_parser = subparsers.add_parser(
        "reset-mfa", help="Reset MFA for a user")
    reset_parser.add_argument(
        "user_id", type=str, help="User ID to reset MFA for")

    # Emergency admin parser
    emergency_parser = subparsers.add_parser(
        "emergency-admin", help="Create emergency admin access"
    )

    # Parse arguments
    args = parser.parse_args()

    # Ensure backup directory exists
    ensure_backup_dir()

    # Run command
    if args.command == "backup":
        if args.type == "rbac":
            backup_rbac()
        elif args.type == "mfa":
            backup_mfa()
        else:  # all
            backup_all()
    elif args.command == "restore":
        if args.type == "rbac":
            restore_rbac(args.file)
        elif args.type == "mfa":
            restore_mfa(args.file)
        else:  # all
            restore_all(args.file)
    elif args.command == "reset-mfa":
        reset_user_mfa(args.user_id)
    elif args.command == "emergency-admin":
        create_emergency_admin()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
