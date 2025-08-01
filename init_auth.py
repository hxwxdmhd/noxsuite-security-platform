"""
Initialize user accounts and RBAC settings for NoxSuite
"""

import json
import os
import sys
from argparse import ArgumentParser

from auth.auth_integration import AuthIntegrationService
from auth.rbac_service import Permission, Role


def setup_initial_users(auth_service):
    """
    Set up initial users with roles

    Args:
        auth_service: Authentication service
    """
    print("Setting up initial users and roles...")

    # Make sure admin role exists
    admin_role = auth_service.rbac_service.get_role("admin")
    if not admin_role:
        print("Creating admin role")
        admin_role = Role(
            name="admin",
            description="Administrator with full system access",
            permissions=list(Permission),
        )
        auth_service.rbac_service.add_role(admin_role)

    # Make sure user role exists
    user_role = auth_service.rbac_service.get_role("user")
    if not user_role:
        print("Creating user role")
        user_role = Role(
            name="user",
            description="Regular user with limited permissions",
            permissions=[Permission.USER_VIEW, Permission.API_READ],
        )
        auth_service.rbac_service.add_role(user_role)

    # Make sure moderator role exists
    moderator_role = auth_service.rbac_service.get_role("moderator")
    if not moderator_role:
        print("Creating moderator role")
        moderator_role = Role(
            name="moderator",
            description="Moderator with user management permissions",
            permissions=[
                Permission.USER_VIEW,
                Permission.USER_EDIT,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.SYSTEM_LOGS,
                Permission.SYSTEM_METRICS,
            ],
        )
        auth_service.rbac_service.add_role(moderator_role)

    # Create admin user
    admin_user_id = "user_1234"
    print(f"Assigning admin role to {admin_user_id}")
    auth_service.rbac_service.assign_role_to_user(admin_user_id, "admin")

    # Create regular user
    user_id = "user_5678"
    print(f"Assigning user role to {user_id}")
    auth_service.rbac_service.assign_role_to_user(user_id, "user")

    # Create moderator user
    moderator_id = "user_9012"
    print(f"Assigning moderator role to {moderator_id}")
    auth_service.rbac_service.assign_role_to_user(moderator_id, "moderator")

    # Export RBAC configuration to JSON
    export_rbac_config(auth_service)


def export_rbac_config(auth_service):
    """
    Export RBAC configuration to JSON file

    Args:
        auth_service: Authentication service
    """
    print("Exporting RBAC configuration...")

    rbac_json = auth_service.rbac_service.export_to_json()

    with open("rbac_config.json", "w") as f:
        f.write(rbac_json)

    print("RBAC configuration exported to rbac_config.json")


def import_rbac_config(auth_service, config_file):
    """
    Import RBAC configuration from JSON file

    Args:
        auth_service: Authentication service
        config_file: Path to configuration file
    """
    print(f"Importing RBAC configuration from {config_file}...")

    try:
        with open(config_file, "r") as f:
            rbac_json = f.read()

        auth_service.rbac_service.import_from_json(rbac_json)
        print("RBAC configuration imported successfully")
    except Exception as e:
        print(f"Error importing RBAC configuration: {str(e)}")
        sys.exit(1)


def main():
    """Main function"""
    parser = ArgumentParser(
        description="Initialize NoxSuite users and RBAC settings")
    parser.add_argument(
        "--import-config", type=str, help="Import RBAC configuration from JSON file"
    )
    parser.add_argument(
        "--jwt-secret", type=str, default="your-super-secret-key", help="JWT secret key"
    )
    args = parser.parse_args()

    # Initialize auth service
    print("Initializing authentication service...")
    auth_service = AuthIntegrationService(
        jwt_secret=args.jwt_secret, mfa_enabled=True)

    # Import or create RBAC configuration
    if args.import_config:
        import_rbac_config(auth_service, args.import_config)
    else:
        setup_initial_users(auth_service)

    print("Done!")


if __name__ == "__main__":
    main()
